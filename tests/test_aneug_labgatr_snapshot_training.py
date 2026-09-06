"""Training-engine fixtures, NOT a substitute for original-core execution."""
from pathlib import Path
import tempfile
import unittest

import torch

from aurora.aneug_labgatr_surface import LaBGATrSurfaceSnapshot
from aurora.aneug_labgatr_snapshot_training import (
    LaBGATrGeometryProvider, LaBGATrSnapshotBackend, train_labgatr_snapshots,
)
from aurora.aneug_release_730_ghd_gps_baseline import file_sha256
from aurora.aneug_rhsia_snapshot_training import reference_energy, snapshot_loss
from test_aneug_labgatr_surface import Core, Data, batch_factory, fixture


def transform(data):
    for key, value in fixture().items():
        if key.startswith("lab_scale"):
            data[key[4:]] = value
    return data


def provider(size=8):
    return LaBGATrGeometryProvider(data_factory=Data, transform=transform, include_ghd=True,
                                   seed=20260901, cache_size=size)


def case(index=0):
    result = fixture()
    result["ghd"] = result["ghd"] * (index + 1) / 432
    t = torch.arange(80).float() * (2 * torch.pi / 80)
    result["wss"] = (1.2 + .4 * t.sin())[:, None, None] * result["normals"][None]
    return result


class DropoutCore(Core):
    def __init__(self):
        super().__init__()
        self.dropout = torch.nn.Dropout(.2)

    def forward(self, data):
        return self.dropout(super().forward(data))


def model():
    return LaBGATrSurfaceSnapshot(DropoutCore(), data_factory=Data, include_ghd=True,
                                  output_scale=2., batch_factory=batch_factory)


def optimization(epochs=2, steady=0):
    return dict(epochs=epochs, phases_per_geometry=5, accumulation_snapshots=4,
        microbatch_graphs=3, validation_interval=1, checkpoint_interval=1,
        step_size_epochs=1, gamma=.8, progress_interval_updates=100,
        seed=17, steady_samples_per_epoch=steady, learning_rate=.001,
        weight_decay=.0001, gradient_clip_norm=1., steady_loss_weight=1.)


class Stream:
    def __init__(self):
        self.seen = []

    def decode(self, index):
        if index not in (7, 9):
            raise AssertionError("inadmissible steady row")
        self.seen.append(index)
        result = case(index)
        del result["wss"]
        result["steady_wss"] = result["normals"] * (2 + index / 10)
        return result


def train(network, root, *, epochs=2, steady=False, continuation=None, backend=None):
    options = dict(train_features=provider(), validation_features=provider(),
        reference_tawss_floor=.02, optimization=optimization(epochs, 3 if steady else 0),
        output_directory=root, provenance=dict(scope="synthetic_fixture_not_original_core_result"),
        device=torch.device("cpu"), log=lambda row: None,
        backend=backend or LaBGATrSnapshotBackend(include_ghd=True, evaluation_phase_batch_size=7))
    if steady:
        options.update(steady_stream=Stream(), eligible_steady=(7, 9), steady_features=provider())
    return train_labgatr_snapshots(network, [case(0), case(1)], [case(2)],
                                   continuation=continuation, **options)


class NativeTrainingTests(unittest.TestCase):
    def test_geometry_only_LRU_is_bounded_and_rejects_changed_geometry(self):
        class Guard(dict):
            def __getitem__(self, key):
                if key in {"wss", "steady_wss", "case_id"}:
                    raise AssertionError("target or identifier read by geometry provider")
                return super().__getitem__(key)
        p = provider(1)
        first = p(0, Guard(case()))
        self.assertIs(p(0, Guard(case())), first)
        self.assertEqual(p.patch_constructions, 1)
        changed = case()
        changed["coordinates"] = changed["coordinates"] + 1
        with self.assertRaisesRegex(ValueError, "different inputs"):
            p(0, changed)
        p(1, case(1))
        p(2, case(2))
        self.assertEqual(len(p.cache), 1)

    def test_mixed_native_training_is_not_one_shot_or_RHSIA(self):
        with tempfile.TemporaryDirectory() as directory:
            result = train(model(), Path(directory) / "run", steady=True)
        self.assertEqual(result["schema_version"], "aurora.private.labgatr_snapshot_result.v3")
        self.assertEqual(result["training_phase_field_exposures"], 20)
        self.assertEqual(result["steady_exposures"], 6)
        self.assertEqual(result["optimizer_updates"], 8)
        self.assertEqual(result["training_model_forward_calls"], 14)
        self.assertEqual(result["training_complete_cycle_forwards"], 0)
        self.assertEqual(result["validation_geometry_graph_encodings"], 160)
        self.assertEqual(result["validation_model_forward_calls"], 24)
        self.assertEqual(result["unique_steady_geometries"], 2)
        self.assertEqual(result["raw_predictions_stored"], 0)
        self.assertFalse(result["independent_confirmatory_evaluation"])

    def test_exact_epoch_boundary_continuation_including_dropout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            torch.manual_seed(21)
            full = model()
            train(full, root / "full")
            torch.manual_seed(21)
            first = model()
            train(first, root / "first", epochs=1)
            checkpoint = root / "first/checkpoints/epoch_001.pt"
            continuation = dict(checkpoint=str(checkpoint), sha256=file_sha256(checkpoint))
            resumed = model()
            result = train(resumed, root / "resumed", continuation=continuation)
            self.assertTrue(result["continuation"]["same_seed_continuation"])
            self.assertEqual(result["steady_exposures"], 0)
            for key, value in full.state_dict().items():
                torch.testing.assert_close(value, resumed.state_dict()[key], rtol=0, atol=0)
            with self.assertRaisesRegex(ValueError, "contract differs"):
                train(model(), root / "changed", continuation=continuation,
                      backend=LaBGATrSnapshotBackend(include_ghd=True, evaluation_phase_batch_size=8))

    def test_all_phase_objective_equals_full_cycle_relative_error(self):
        c = case()
        prediction = c["wss"] * .7
        energy = reference_energy(c["wss"], c["vertex_weights"])
        native = torch.stack([snapshot_loss(prediction[t], c["wss"][t], c["vertex_weights"], energy) for t in range(80)]).mean()
        full = ((prediction - c["wss"]).square().sum(-1) * c["vertex_weights"][None]).sum() / (energy * 80)
        torch.testing.assert_close(native, full)


if __name__ == "__main__":
    unittest.main()
