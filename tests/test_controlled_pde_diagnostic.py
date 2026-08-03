import json
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

from aurora.controlled_pde_diagnostic import (
    _nested_gaussian_samples,
    _nested_moment_residual,
    _standardized_mean_error,
    load_diagnostic_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "controlled_pde_g1b_diagnostic.json"


class ControlledPDEDiagnosticContractTests(unittest.TestCase):
    def test_reference_diagnostic_pins_a_failed_frozen_gate(self) -> None:
        diagnostic, base, _, _ = load_diagnostic_config(CONFIG)
        self.assertEqual(diagnostic["status"], "post_result_exploratory_diagnostic")
        self.assertEqual(base["experiment_id"], diagnostic["base_experiment_id"])
        self.assertEqual(diagnostic["sample_counts"][0], base["bc_samples_eval"])

    def test_diagnostic_rejects_status_inflation(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["status"] = "confirmatory"
        with patch.object(Path, "read_text", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(Exception, "post-result exploratory"):
                load_diagnostic_config(CONFIG)


@unittest.skipIf(torch is None, "controlled PDE tests require torch")
class ControlledPDEDiagnosticTensorTests(unittest.TestCase):
    def test_nested_sampler_recovers_joint_moments_in_both_orders(self) -> None:
        mean = torch.tensor([[0.3, -0.2]])
        covariance = torch.tensor([[[0.8, 0.3], [0.3, 0.5]]])
        for first_index in (0, 1):
            generator = torch.Generator().manual_seed(100 + first_index)
            samples = _nested_gaussian_samples(
                mean,
                covariance,
                100_000,
                generator,
                first_index=first_index,
            )[0]
            empirical_mean = samples.mean(dim=0)
            centered = samples - empirical_mean
            empirical_covariance = centered.T @ centered / (samples.shape[0] - 1)
            self.assertTrue(torch.allclose(empirical_mean, mean[0], atol=0.012))
            self.assertTrue(
                torch.allclose(empirical_covariance, covariance[0], atol=0.018)
            )
            residual = _nested_moment_residual(
                mean, covariance, first_index=first_index
            )
            self.assertLess(
                residual["maximum_covariance_absolute_residual"], 1e-6
            )

    def test_standardized_mean_error_is_zero_for_exact_prediction(self) -> None:
        oracle = torch.randn(12, 16)
        error = _standardized_mean_error(
            oracle, oracle, conditions_per_geometry=3
        )
        self.assertEqual(error["mean"], 0.0)
        self.assertEqual(error["maximum"], 0.0)


if __name__ == "__main__":
    unittest.main()
