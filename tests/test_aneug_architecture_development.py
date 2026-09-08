import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch
from torch import nn

from aurora.aneug_architecture_development import evaluate_cycles, train_cycles, validate_optimization


class ToyCycle(nn.Module):
    def __init__(self):
        super().__init__()
        self.output = nn.Linear(3, 240)

    def forward_cycle(self, case):
        x = self.output(case["coordinates"])
        return x.reshape(x.shape[0], 80, 3).permute(1, 0, 2)


class ArchitectureDevelopmentTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(28)
        torch.set_num_threads(2)
        self.cases = [dict(coordinates=torch.randn(6, 3), normals=torch.randn(6, 3),
                           vertex_weights=torch.ones(6) / 6, wss=torch.randn(80, 6, 3))
                      for _ in range(3)]
        self.optimization = dict(seed=27, epochs=2, accumulation_cases=2,
                                 validation_interval=1, checkpoint_interval=10,
                                 learning_rate=3e-4, weight_decay=1e-4,
                                 step_size_epochs=50, gamma=0.75, gradient_clip_norm=1.0)

    def test_complete_training_ledger_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "run"
            result = train_cycles(ToyCycle(), self.cases, self.cases[:1],
                                  optimization=self.optimization, reference_tawss_floor=1e-4,
                                  output_directory=root, provenance={"synthetic": True},
                                  device=torch.device("cpu"), log=lambda _: None)
            self.assertEqual(result["training_cycle_exposures"], 6)
            self.assertEqual(result["training_phase_field_exposures"], 480)
            self.assertEqual(result["optimizer_updates"], 4)
            self.assertEqual(result["validation_cycle_forwards"], 2)
            self.assertEqual(len(result["checkpoints"]), 2)
            self.assertTrue((root / "selected.pt").is_file())
            checkpoint = torch.load(root / "checkpoints/epoch_002.pt", weights_only=True)
            self.assertEqual(checkpoint["completed_epoch"], 2)
            self.assertIn("optimizer_state_dict", checkpoint)
            self.assertIn("rng_state", checkpoint)
            self.assertEqual(json.loads((root / "result.json").read_text()), result)
            with self.assertRaises(FileExistsError):
                train_cycles(ToyCycle(), self.cases, self.cases[:1],
                             optimization=self.optimization, reference_tawss_floor=1e-4,
                             output_directory=root, provenance={}, device=torch.device("cpu"))

    def test_disconnected_model_is_not_a_valid_baseline(self):
        model = ToyCycle()
        model.unused = nn.Linear(2, 2)
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(RuntimeError, "disconnected"):
            train_cycles(model, self.cases, self.cases[:1], optimization=self.optimization,
                         reference_tawss_floor=1e-4, output_directory=Path(directory) / "run",
                         provenance={}, device=torch.device("cpu"), log=lambda _: None)

    def test_nonfinite_prediction_rejected_not_assigned_favorable_metric(self):
        model = ToyCycle()
        with torch.no_grad():
            model.output.weight.fill_(float("nan"))
        with self.assertRaisesRegex(RuntimeError, "nonfinite"):
            evaluate_cycles(model, self.cases, torch.device("cpu"), 1e-4)

    def test_validation_does_not_compute_gradients(self):
        model = ToyCycle()
        metrics = evaluate_cycles(model, self.cases[:1], torch.device("cpu"), 1e-4)
        self.assertEqual(metrics["case_count"], 1)
        self.assertTrue(all(p.grad is None for p in model.parameters()))

    def test_invalid_training_options(self):
        for key, value in (("epochs", True), ("seed", -1), ("accumulation_cases", 0),
                           ("weight_decay", -1), ("learning_rate", float("nan"))):
            with self.assertRaises(ValueError):
                validate_optimization(dict(self.optimization, **{key: value}))

    def test_earliest_validation_tie_is_selected(self):
        evaluation = {"aggregate": {"field_relative_l2": 1.0}, "case_count": 1}
        with tempfile.TemporaryDirectory() as directory, patch(
            "aurora.aneug_architecture_development.evaluate_cycles", return_value=evaluation
        ):
            result = train_cycles(ToyCycle(), self.cases[:1], self.cases[:1],
                                  optimization=self.optimization, reference_tawss_floor=1e-4,
                                  output_directory=Path(directory) / "run", provenance={},
                                  device=torch.device("cpu"), log=lambda _: None)
            self.assertEqual(result["selected_epoch"], 1)


if __name__ == "__main__":
    unittest.main()
