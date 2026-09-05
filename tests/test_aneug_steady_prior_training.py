import copy
import json
from pathlib import Path
import tempfile
import unittest

import torch
from torch import nn

from aurora.aneug_release_730_ghd_gps_baseline import file_sha256
from aurora.aneug_steady_prior_training import train_steady_prior, validate_optimization


class TinySteady(nn.Module):
    """Checkpoint/trainer interface only; not a benchmark model."""
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(3, 8), nn.Tanh(), nn.Dropout(.2), nn.Linear(8, 3))

    def forward(self, case):
        assert "steady_wss" not in case and "wss" not in case
        return self.layers(case["coordinates"])


class SteadyPriorTrainingTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)
        torch.manual_seed(4)
        self.cases = {i: dict(coordinates=torch.randn(5, 3), normals=torch.randn(5, 3),
                             vertex_weights=torch.ones(5) / 5, steady_wss=torch.randn(5, 3))
                      for i in [1, 4, 9]}
        self.reads = []
        self.opt = dict(seed=14, epochs=4, cases_per_epoch=5, accumulation_cases=2,
            checkpoint_interval=2, learning_rate=.002, weight_decay=.001,
            step_size_epochs=2, gamma=.75, gradient_clip_norm=1)

    def decode(self, index):
        self.reads.append(index)
        return self.cases[index]

    def run_model(self, model, root, opt=None, continuation=None):
        return train_steady_prior(model, self, [1, 4, 9], optimization=opt or self.opt,
            output_directory=root, provenance={"synthetic": True}, device=torch.device("cpu"),
            log=lambda _: None, continuation=continuation)

    def test_exact_budget_private_artifacts_and_nonoverwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            result = self.run_model(TinySteady(), root)
            self.assertEqual(result["steady_exposures"], 20)
            self.assertEqual(result["optimizer_updates"], 12)
            self.assertEqual(result["unique_steady_cases_seen"], 3)
            self.assertEqual(result["transient_phase_field_exposures"], 0)
            self.assertEqual(result["prior_checkpoint_sha256"], file_sha256(root / "prior.pt"))
            self.assertEqual(result, json.loads((root / "result.json").read_text()))
            self.assertEqual(len(self.reads), 20)
            with self.assertRaises(FileExistsError):
                self.run_model(TinySteady(), root)

    def test_epoch_resume_is_dropout_optimizer_and_sample_order_exact(self):
        initial = TinySteady()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            torch.manual_seed(70)
            full = self.run_model(copy.deepcopy(initial), root / "full")
            full_order = list(self.reads)
            self.reads.clear()
            torch.manual_seed(70)
            self.run_model(copy.deepcopy(initial), root / "first", dict(self.opt, epochs=2))
            path = root / "first/checkpoints/epoch_002.pt"
            digest = file_sha256(path)
            resumed = self.run_model(TinySteady(), root / "resume", continuation={"checkpoint": path, "sha256": digest})
            self.assertEqual(self.reads, full_order)
            self.assertEqual(file_sha256(path), digest)
            a = torch.load(root / "full/checkpoints/epoch_004.pt", weights_only=True)
            b = torch.load(root / "resume/checkpoints/epoch_004.pt", weights_only=True)
            for key in a["model_state_dict"]:
                torch.testing.assert_close(a["model_state_dict"][key], b["model_state_dict"][key], rtol=0, atol=0)
            for key, state in a["optimizer_state_dict"]["state"].items():
                for name, tensor in state.items():
                    torch.testing.assert_close(tensor, b["optimizer_state_dict"]["state"][key][name], rtol=0, atol=0)
            torch.testing.assert_close(a["rng_state"]["torch_rng_state"], b["rng_state"]["torch_rng_state"])
            self.assertEqual(full["steady_exposures"], resumed["steady_exposures"])
            self.assertEqual(resumed["segment_steady_exposures"], 10)
            self.assertFalse(resumed["continuation"]["new_independent_seed"])

    def test_invalid_options_hash_and_provenance_rejected_before_new_reads(self):
        for key, value in (("epochs", 0), ("cases_per_epoch", True), ("seed", -1), ("learning_rate", float("nan"))):
            with self.assertRaises(ValueError):
                validate_optimization(dict(self.opt, **{key: value}))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.run_model(TinySteady(), root / "first", dict(self.opt, epochs=2))
            path = root / "first/checkpoints/epoch_002.pt"
            reads = len(self.reads)
            with self.assertRaisesRegex(ValueError, "hash"):
                self.run_model(TinySteady(), root / "bad", continuation={"checkpoint": path, "sha256": "0" * 64})
            with self.assertRaisesRegex(ValueError, "scientific identity"):
                self.run_model(TinySteady(), root / "badopt", dict(self.opt, seed=15),
                    continuation={"checkpoint": path, "sha256": file_sha256(path)})
            self.assertEqual(len(self.reads), reads)

    def test_dead_parameters_are_not_successful_pretraining(self):
        model = TinySteady()
        model.unused = nn.Linear(2, 2)
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(RuntimeError, "disconnected"):
            self.run_model(model, Path(directory) / "run")


if __name__ == "__main__":
    unittest.main()
