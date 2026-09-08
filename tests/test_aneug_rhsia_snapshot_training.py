import copy
import json
from pathlib import Path
import tempfile
import unittest

import torch
from torch import nn

from aurora.aneug_architecture_development import evaluate_cycles
from aurora.aneug_processed_v4_d9 import field_loss
from aurora.aneug_release_730_ghd_gps_baseline import file_sha256
from aurora.aneug_rhsia_snapshot_training import (
    collate_graphs, evaluate_snapshots, reference_energy, snapshot_epoch, snapshot_loss, train_snapshots,
)


class ToySnapshot(nn.Module):
    def __init__(self, phases=4):
        super().__init__()
        self.phases = phases
        self.space = nn.Linear(3, 3)
        self.time = nn.Linear(1, 3)
        self.dropout = nn.Dropout(.2)
        self.seen_phases = []

    def forward_snapshot(self, features, phase_indices, waveform, *, period, output_scale):
        self.seen_phases.extend(phase_indices.tolist())
        temporal = self.time(phase_indices.clamp_min(0).float().reshape(-1, 1))
        temporal = torch.where(phase_indices[:, None] >= 0, temporal, torch.zeros_like(temporal))
        return output_scale * (self.dropout(self.space(features["coordinates"])) + temporal[features["batch"]])

    def forward_cycle(self, features, waveform, *, period, output_scale):
        return torch.stack([self.forward_snapshot(features, torch.tensor([p]), waveform,
            period=period, output_scale=output_scale) for p in range(self.phases)])


class ToySteady:
    def __init__(self, case):
        self.case = {k: v for k, v in case.items() if k != "wss"}
        self.case["steady_wss"] = torch.ones_like(case["wss"][0]) * 7
        self.read = []

    def decode(self, index):
        if index not in (2, 5, 9):
            raise AssertionError("ineligible steady data read")
        self.read.append(index)
        return self.case


def geometry(index, case):
    n = len(case["coordinates"])
    return {"coordinates": case["coordinates"], "batch": torch.zeros(n, dtype=torch.long),
            "edge_index": torch.stack((torch.arange(n - 1), torch.arange(1, n)))}


class SnapshotScheduleTests(unittest.TestCase):
    def test_native_epoch_is_full_geometry_times_phase_and_pairs_transient_order(self):
        plain = snapshot_epoch(584, 80, 80, (), steady_samples=0, seed=3, epoch=1)
        mixed = snapshot_epoch(584, 80, 80, tuple(range(13985)), steady_samples=13985, seed=3, epoch=1)
        self.assertEqual(len(plain), 46720)
        self.assertEqual(len(mixed), 60705)
        self.assertEqual(plain, [s for s in mixed if s.regime == "T"])
        self.assertEqual({(s.index, s.phase) for s in plain}, {(i, p) for i in range(584) for p in range(80)})
        self.assertEqual({s.index for s in mixed if s.regime == "S"}, set(range(13985)))
        self.assertTrue(all(s.phase == -1 for s in mixed if s.regime == "S"))

    def test_phase_subsampling_is_balanced_not_permanently_fixed(self):
        seen = {i: [] for i in range(3)}
        for epoch in range(1, 81):
            for sample in snapshot_epoch(3, 80, 1, (), steady_samples=0, seed=29, epoch=epoch):
                seen[sample.index].append(sample.phase)
        for values in seen.values():
            self.assertEqual(sorted(values), list(range(80)))
        self.assertNotEqual(seen[0], seen[1])

    def test_all_phase_average_matches_full_cycle_objective_and_gradient(self):
        torch.manual_seed(11)
        reference = torch.randn(80, 7, 3) * torch.linspace(.1, 4, 80)[:, None, None]
        weights = torch.rand(7) + .1
        prediction = torch.randn_like(reference).requires_grad_()
        whole = field_loss(prediction, reference, weights)
        partial = torch.stack([snapshot_loss(prediction[p], reference[p], weights,
            reference_energy(reference, weights)) for p in range(80)]).mean()
        torch.testing.assert_close(whole, partial)
        torch.testing.assert_close(torch.autograd.grad(whole, prediction, retain_graph=True)[0],
                                   torch.autograd.grad(partial, prediction)[0])
        wrong = torch.stack([field_loss(prediction[p:p+1], reference[p:p+1], weights) for p in range(80)]).mean()
        self.assertGreater(float((wrong - whole).abs()), .1)


class SnapshotTrainingTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(9)
        self.cases = [dict(coordinates=torch.randn(6, 3), normals=torch.randn(6, 3),
            vertex_weights=torch.ones(6) / 6, wss=torch.randn(4, 6, 3)) for _ in range(3)]
        self.config = dict(seed=17, epochs=2, phases_per_geometry=4, steady_samples_per_epoch=3,
            accumulation_snapshots=4, microbatch_graphs=1, validation_interval=1, checkpoint_interval=1,
            progress_interval_updates=1, learning_rate=3e-4, weight_decay=1e-4,
            step_size_epochs=2, gamma=.75, gradient_clip_norm=1., steady_loss_weight=1.)

    def run_model(self, root, model=None, config=None, **kwargs):
        torch.manual_seed(20)
        model = ToySnapshot() if model is None else model
        config = self.config if config is None else config
        stream = ToySteady(self.cases[0]) if config["steady_samples_per_epoch"] else None
        result = train_snapshots(model, self.cases, self.cases[:1], train_features=geometry,
            validation_features=geometry, waveform=torch.ones(32), period=.8, output_scale=2.,
            optimization=config, reference_tawss_floor=1e-4, output_directory=root,
            provenance={"synthetic": True, "admitted_order": "fixed"}, device=torch.device("cpu"),
            steady_stream=stream, eligible_steady=(2, 5, 9) if stream else (),
            steady_features=geometry if stream else None, log=lambda _: None, **kwargs)
        return model, result, stream

    def test_mixed_training_checkpoint_counts_and_masked_steady_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            model, result, stream = self.run_model(root)
            self.assertEqual(result["training_phase_field_exposures"], 24)
            self.assertEqual(result["steady_exposures"], 6)
            self.assertEqual(result["optimizer_updates"], 8)  # final partial accumulation batch
            self.assertEqual(result["phase_histogram"], [6] * 4)
            self.assertEqual(result["training_complete_cycle_forwards"], 0)
            self.assertEqual(result["training_cycle_equivalent_phase_exposures"], 6)
            self.assertEqual(result["training_geometry_graph_encodings"], 30)
            self.assertEqual(result["validation_conditioned_graph_forwards"], 8)
            self.assertEqual(model.seen_phases.count(-1), 6)
            self.assertEqual(len(stream.read), 6)
            self.assertEqual(result["unique_steady_geometries"], 3)
            self.assertEqual(json.loads((root / "result.json").read_text()), result)
            state = torch.load(root / "checkpoints/epoch_002.pt", weights_only=True)
            self.assertIn("optimizer_state_dict", state)
            self.assertIn("rng_state", state)
            with self.assertRaises(FileExistsError):
                self.run_model(root)

    def test_transient_only_subsample_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            _, result, stream = self.run_model(Path(directory) / "run", config=dict(
                self.config, phases_per_geometry=1, steady_samples_per_epoch=0))
            self.assertIsNone(stream)
            self.assertEqual(result["training_phase_field_exposures"], 6)
            self.assertEqual(result["training_cycle_equivalent_phase_exposures"], 1.5)
            self.assertEqual(result["steady_exposures"], 0)
            self.assertEqual(result["sampling_identity"], "balanced_phase_subsampling_adaptation")

    def test_real_graph_batch10_is_distinct_from_accumulation(self):
        with tempfile.TemporaryDirectory() as directory:
            _, result, _ = self.run_model(Path(directory) / "run", config=dict(
                self.config, accumulation_snapshots=10, microbatch_graphs=10))
            self.assertEqual(result["batch_identity"], "graph_batch10")
            self.assertEqual(result["training_model_forward_calls"], 4)
            self.assertEqual(result["training_geometry_graph_encodings"], 30)

    def test_batched_mesh_edges_cannot_cross_geometries(self):
        features, sizes = collate_graphs([geometry(0, c) for c in self.cases], torch.device("cpu"))
        self.assertEqual(sizes, [6, 6, 6])
        a, b = features["edge_index"]
        self.assertTrue(bool((features["batch"][a] == features["batch"][b]).all()))
        self.assertEqual(features["batch"].tolist(), [0] * 6 + [1] * 6 + [2] * 6)
        bad = geometry(0, self.cases[0])
        bad["edge_index"][0, 0] = 6
        with self.assertRaisesRegex(ValueError, "single graph"):
            collate_graphs([bad], torch.device("cpu"))

    def assert_nested_equal(self, first, second):
        if isinstance(first, torch.Tensor):
            torch.testing.assert_close(first, second, atol=0, rtol=0)
        elif isinstance(first, dict):
            self.assertEqual(first.keys(), second.keys())
            for key in first:
                self.assert_nested_equal(first[key], second[key])
        elif isinstance(first, (tuple, list)):
            self.assertEqual(len(first), len(second))
            for a, b in zip(first, second):
                self.assert_nested_equal(a, b)
        else:
            self.assertEqual(first, second)

    def test_dropout_exact_epoch_resume_and_immutable_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, whole, _ = self.run_model(root / "whole", config=dict(self.config, epochs=4))
            _, first, _ = self.run_model(root / "first")
            checkpoint = root / "first/checkpoints/epoch_002.pt"
            digest = file_sha256(checkpoint)
            _, resumed, _ = self.run_model(root / "resumed", config=dict(self.config, epochs=4),
                continuation={"checkpoint": checkpoint, "sha256": digest})
            a = torch.load(root / "whole/checkpoints/epoch_004.pt", weights_only=True)
            b = torch.load(root / "resumed/checkpoints/epoch_004.pt", weights_only=True)
            for key in ("model_state_dict", "optimizer_state_dict", "scheduler_state_dict", "rng_state",
                        "ledger", "best_state_dict", "best_validation", "best_epoch", "best_value"):
                self.assert_nested_equal(a[key], b[key])
            self.assertEqual(whole["selected_validation"], resumed["selected_validation"])
            self.assertEqual(resumed["continuation"]["parent_ledger"]["phase_histogram"], first["phase_histogram"])
            self.assertEqual(file_sha256(checkpoint), digest)

    def test_resume_rejects_changed_schedule_hash_or_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_model(root / "first")
            checkpoint = root / "first/checkpoints/epoch_002.pt"
            continuation = {"checkpoint": checkpoint, "sha256": file_sha256(checkpoint)}
            with self.assertRaisesRegex(ValueError, "contract differs"):
                self.run_model(root / "changed", config=dict(self.config, epochs=4, phases_per_geometry=1), continuation=continuation)
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.run_model(root / "bad_hash", config=dict(self.config, epochs=4), continuation=dict(continuation, sha256="0" * 64))
            self.assertFalse((root / "changed").exists())

    def test_same_complete_cycle_metrics_as_existing_evaluator(self):
        model = ToySnapshot().eval()
        snapshot = evaluate_snapshots(model, self.cases, geometry, torch.ones(32), period=.8,
            output_scale=2., reference_tawss_floor=1e-4, device=torch.device("cpu"))
        class View(nn.Module):
            def forward_cycle(self, case):
                return model.forward_cycle(geometry(0, case), torch.ones(32), period=.8, output_scale=2.)
        expected = evaluate_cycles(View(), self.cases, torch.device("cpu"), 1e-4)
        self.assertEqual(snapshot, expected)

    def test_unconnected_and_nonfinite_models_cannot_produce_results(self):
        with tempfile.TemporaryDirectory() as directory:
            model = ToySnapshot()
            model.dead = nn.Linear(1, 1)
            with self.assertRaisesRegex(RuntimeError, "disconnected"):
                self.run_model(Path(directory) / "dead", model=model)
            model = ToySnapshot()
            with torch.no_grad():
                model.space.weight.fill_(float("nan"))
            with self.assertRaisesRegex(ValueError, "invalid physical"):
                self.run_model(Path(directory) / "nan", model=model)

    def test_actual_pyg_mixed_snapshot_training_not_mocked_graph(self):
        try:
            import torch_geometric  # noqa: F401
        except ImportError:
            self.skipTest("actual PyG dependency required; run in pinned comparator layer")
        from aurora.aneug_rhsia_graph_transformer import RHSIAGraphTransformer
        model = RHSIAGraphTransformer(hidden=16, heads=4, layers=1, phases=4,
            pe_width=8, pe_layers=1, pe_feedforward=16, dropout=.1)
        features = dict(node_features=torch.randn(6, 10), ghd_descriptors=torch.randn(6, 8, 7),
            cot_descriptors=torch.randn(6, 16, 5), batch=torch.zeros(6, dtype=torch.long),
            edge_index=torch.tensor([[0, 1, 1, 2, 2, 3, 3, 4, 4, 5], [1, 0, 2, 1, 3, 2, 4, 3, 5, 4]]))
        stream = ToySteady(self.cases[0])
        with tempfile.TemporaryDirectory() as directory:
            result = train_snapshots(model, self.cases[:1], self.cases[:1],
                train_features=lambda *_: features, validation_features=lambda *_: features,
                steady_features=lambda *_: features, steady_stream=stream, eligible_steady=(2, 5, 9),
                waveform=torch.linspace(0, 6.2, 32).sin() + 2, period=.8, output_scale=2.,
                optimization=dict(self.config, epochs=1, microbatch_graphs=2), reference_tawss_floor=1e-4,
                output_directory=Path(directory) / "run", provenance={"synthetic_actual_pyg": True},
                device=torch.device("cpu"), log=lambda _: None)
            self.assertEqual(result["training_phase_field_exposures"], 4)
            self.assertEqual(result["steady_exposures"], 3)
            self.assertEqual(result["selected_validation"]["case_count"], 1)


if __name__ == "__main__":
    unittest.main()
