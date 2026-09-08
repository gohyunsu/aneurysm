import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch
from torch import nn

from aurora.aneug_architecture_development import train_cycles
from aurora.aneug_cycle_continuation import CONTINUATION_INVARIANTS
from aurora.aneug_paired_steady_supervision import PairedSteadySupervision
from aurora.aneug_release_730_ghd_gps_baseline import file_sha256
from aurora.aneug_surface_transfer import VARIANTS, build_paired_surface_transfer_model
from test_aneug_surface_transfer import topology, geometry
from test_aneug_release_730_matched_steady_stream import synthetic_archive, synthetic_stream


class Stream:
    def __init__(self):
        self.reads = []

    def decode(self, index):
        if index not in (2, 4, 9, 10):
            raise AssertionError("ineligible row")
        self.reads.append(index)
        case = geometry()
        case["steady_wss"] = torch.ones(4, 3) * (index + 1) / 10
        return case


class StochasticMixed(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(3, 8), nn.Dropout(.3), nn.SiLU())
        self.cycle = nn.Linear(8, 240)
        self.steady = nn.Linear(8, 3)

    def forward_cycle(self, case):
        return self.cycle(self.encoder(case["coordinates"])).reshape(-1, 80, 3).permute(1, 0, 2)

    def forward_single_field(self, case):
        return self.steady(self.encoder(case["coordinates"]))


class PairedSteadyTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(3)
        self.cases = [dict(geometry(), wss=torch.randn(80, 4, 3)) for _ in range(3)]
        self.opt = dict(seed=17, epochs=2, accumulation_cases=2, validation_interval=1,
                        checkpoint_interval=1, learning_rate=3e-4, weight_decay=1e-4,
                        step_size_epochs=1, gamma=.75, gradient_clip_norm=1.)
        self.provenance = {key: "synthetic" for key in CONTINUATION_INVARIANTS}
        self.provenance.update(torch=str(torch.__version__), cuda=None,
                               historical_test_already_opened=True, cycle_output_scale=1.)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def supervision(self, seed=91, weight=.7, eligible=(2, 4, 9, 10)):
        return PairedSteadySupervision(Stream(), eligible, seed=seed, loss_weight=weight)

    def run_curve(self, name, epochs, *, supervision=None, continuation=None, model=None):
        return train_cycles(model if model is not None else StochasticMixed(), self.cases, self.cases[:1],
            optimization=dict(self.opt, epochs=epochs), reference_tawss_floor=1e-4,
            output_directory=self.root / name, provenance=self.provenance,
            device=torch.device("cpu"), log=lambda _: None, continuation=continuation,
            steady_supervision=supervision if supervision is not None else self.supervision())

    def parent(self):
        torch.manual_seed(314)
        self.run_curve("parent", 2)
        root = self.root / "parent"
        return dict(checkpoint=str(root / "checkpoints/epoch_002.pt"),
                    checkpoint_sha256=file_sha256(root / "checkpoints/epoch_002.pt"),
                    parent_result=str(root / "result.json"),
                    parent_result_sha256=file_sha256(root / "result.json"))

    def test_schedule_is_prefix_consistent_and_admits_no_unscheduled_reads(self):
        mixed = self.supervision()
        short = sum((mixed.indices(e, 3) for e in range(1, 5)), [])
        long = sum((mixed.indices(e, 6) for e in range(1, 3)), [])
        self.assertEqual(short, long)
        self.assertEqual(mixed.stream.reads, [])
        for start in range(0, 12, 4):
            self.assertEqual(set(short[start:start + 4]), {2, 4, 9, 10})
        with self.assertRaisesRegex(ValueError, "not admitted"):
            mixed.decode(8)
        self.assertEqual(mixed.stream.reads, [])

    def test_actual_audited_stream_label_key_and_lazy_row_access_are_used(self):
        archive, tensor, ghd, faces = synthetic_archive()
        stream = synthetic_stream(archive, faces)
        mixed = PairedSteadySupervision(stream, (0, 2, 4), seed=7, loss_weight=1.)
        self.assertEqual(tensor.indices, [])
        self.run_curve("real_stream", 2, supervision=mixed)
        expected = mixed.indices(1, 3) + mixed.indices(2, 3)
        self.assertEqual(tensor.indices, expected)
        self.assertEqual(ghd.indices, expected)
        self.assertTrue(set(tensor.indices).isdisjoint({1, 3}))

    def test_invalid_weight_pool_and_seed_do_not_become_hidden_T_only(self):
        for weight in (0, -1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                self.supervision(weight=weight)
        for eligible in ((), (2, 2), (-1,), (True,)):
            with self.assertRaises(ValueError):
                self.supervision(eligible=eligible)
        with self.assertRaises(ValueError):
            self.supervision(seed=-1)

    def test_mixed_ledger_counts_fields_not_fake_cycles_and_no_validation_steady_read(self):
        mixed = self.supervision()
        result = self.run_curve("mixed", 2, supervision=mixed)
        self.assertEqual(result["training_cycle_exposures"], 6)
        self.assertEqual(result["training_phase_field_exposures"], 480)
        self.assertEqual(result["steady_exposures"], 6)
        self.assertEqual(result["total_training_field_exposures"], 486)
        self.assertEqual(result["optimizer_updates"], 4)  # includes partial final batches
        self.assertEqual(result["validation_cycle_forwards"], 2)
        self.assertEqual(mixed.stream.reads, mixed.indices(1, 3) + mixed.indices(2, 3))
        self.assertEqual(result["unique_steady_cases_seen"], 4)
        self.assertFalse(result["inference_requires_steady_CFD"])
        self.assertNotIn("joint_steady_supervision", self.provenance)  # caller was not mutated
        self.assertEqual(result["raw_predictions_stored"], 0)
        row = json.loads((self.root / "mixed/epochs/epoch_002.json").read_text())
        self.assertEqual(row["steady_exposures"], 6)
        self.assertEqual(row["unique_steady_cases_seen"], 4)

    def test_dropout_mixed_resume_preserves_weights_optimizer_rng_and_sampling(self):
        torch.manual_seed(314)
        whole = self.run_curve("whole", 4)
        continuation = self.parent()
        resumed_stream = self.supervision()
        torch.manual_seed(777)
        resumed = self.run_curve("resumed", 4, continuation=continuation, supervision=resumed_stream)
        full = torch.load(self.root / "whole/checkpoints/epoch_004.pt", weights_only=True)
        part = torch.load(self.root / "resumed/checkpoints/epoch_004.pt", weights_only=True)
        for key, tensor in full["model_state_dict"].items():
            self.assertTrue(torch.equal(tensor, part["model_state_dict"][key]), key)
        for key, state in full["optimizer_state_dict"]["state"].items():
            for name, value in state.items():
                self.assertTrue(torch.equal(value, part["optimizer_state_dict"]["state"][key][name]))
        self.assertEqual(full["scheduler_state_dict"], part["scheduler_state_dict"])
        self.assertTrue(torch.equal(full["rng_state"]["torch_rng_state"], part["rng_state"]["torch_rng_state"]))
        for key in ("selected_epoch", "selected_validation", "steady_exposures", "optimizer_updates",
                    "training_phase_field_exposures", "unique_steady_cases_seen"):
            self.assertEqual(whole[key], resumed[key], key)
        self.assertEqual(resumed_stream.stream.reads,
                         resumed_stream.indices(3, 3) + resumed_stream.indices(4, 3))
        self.assertEqual(resumed["segment_steady_exposures"], 6)
        for epoch in (1, 2):
            self.assertEqual(file_sha256(self.root / f"parent/epochs/epoch_{epoch:03d}.json"),
                             file_sha256(self.root / f"resumed/epochs/epoch_{epoch:03d}.json"))

    def test_changed_steady_condition_rejected_before_parent_checkpoint_load(self):
        continuation = self.parent()
        for name, supervision in (("seed", self.supervision(seed=8)),
                                  ("weight", self.supervision(weight=.9)),
                                  ("rows", self.supervision(eligible=(2, 4, 9)))):
            with patch("aurora.aneug_cycle_continuation.torch.load") as loader:
                with self.assertRaisesRegex(ValueError, "steady supervision changed"):
                    self.run_curve(name, 4, continuation=continuation, supervision=supervision)
                loader.assert_not_called()
            self.assertEqual(supervision.stream.reads, [])

    def test_corrupted_steady_ledger_rejected_before_any_new_label_read(self):
        continuation = self.parent()
        checkpoint = torch.load(continuation["checkpoint"], weights_only=True)
        checkpoint["history"][0]["steady_exposures"] = 240  # field cannot count as 80 phases
        torch.save(checkpoint, continuation["checkpoint"])
        continuation["checkpoint_sha256"] = file_sha256(Path(continuation["checkpoint"]))
        parent = json.loads(Path(continuation["parent_result"]).read_text())
        parent["checkpoints"][-1]["sha256"] = continuation["checkpoint_sha256"]
        Path(continuation["parent_result"]).write_text(json.dumps(parent))
        continuation["parent_result_sha256"] = file_sha256(Path(continuation["parent_result"]))
        mixed = self.supervision()
        with self.assertRaisesRegex(ValueError, "steady exposure ledger"):
            self.run_curve("bad", 4, continuation=continuation, supervision=mixed)
        self.assertEqual(mixed.stream.reads, [])

    def test_T_and_TS_all_common_initial_parameters_paired_and_no_dead_steady_heads(self):
        options = dict(width=16, heads=4, bank_width=4, operators=3, adapter_width=8, output_scale=2.)
        for variant in VARIANTS:
            torch.manual_seed(31)
            plain = build_paired_surface_transfer_model(topology(), torch.arange(80, dtype=torch.float64) / 80,
                variant=variant, auxiliary_steady=False, **options)
            torch.manual_seed(31)
            mixed = build_paired_surface_transfer_model(topology(), torch.arange(80, dtype=torch.float64) / 80,
                variant=variant, auxiliary_steady=True, **options)
            self.assertFalse(hasattr(plain, "steady_head"))
            for key, value in plain.state_dict().items():
                self.assertTrue(torch.equal(value, mixed.state_dict()[key]), key)
            torch.testing.assert_close(plain.forward_cycle(geometry()), mixed.forward_cycle(geometry()), rtol=0, atol=0)
            train_cycles(plain, self.cases, self.cases[:1], optimization=dict(self.opt, epochs=1),
                reference_tawss_floor=1e-4, output_directory=self.root / (variant + "_T"),
                provenance=self.provenance, device=torch.device("cpu"), log=lambda _: None)
            self.assertTrue(all(p.grad is not None for p in plain.parameters()))
            self.run_curve(variant, 1, model=mixed)
            self.assertTrue(all(p.grad is not None for p in mixed.parameters()))

    def test_nonfinite_or_cycle_shaped_steady_target_cannot_train(self):
        mixed = self.supervision()
        original = mixed.stream.decode
        def corrupt(index):
            return dict(original(index), steady_wss=torch.full((4, 3), float("nan")))
        mixed.stream.decode = corrupt
        with self.assertRaises((RuntimeError, ValueError)):
            self.run_curve("nonfinite", 1, supervision=mixed)
        model = StochasticMixed()
        model.forward_single_field = model.forward_cycle
        with self.assertRaisesRegex(RuntimeError, "one .*field"):
            self.run_curve("fake_cycle", 1, model=model)


if __name__ == "__main__":
    unittest.main()
