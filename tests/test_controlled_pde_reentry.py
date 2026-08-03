import copy
import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

try:
    import numpy
except ImportError:  # pragma: no cover - lightweight local environment
    numpy = None

from aurora.controlled_pde import poisson_solution
from aurora.controlled_pde_reentry import (
    _bootstrap_mean_ci,
    analytic_field_moments,
    gauss_hermite_operator_mean,
    load_config,
    run_experiment,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "controlled_pde_g1r.json"


class ControlledPDEReentryContractTests(unittest.TestCase):
    def test_config_is_fresh_and_cannot_relabel_g1(self) -> None:
        config = load_config(CONFIG)
        frozen = json.loads(
            (ROOT / "configs" / "controlled_pde_g1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(config["may_relabel_failed_source_gate"])
        self.assertEqual(config["status"], "preregistered_before_fresh_test")
        self.assertFalse(set(config["seeds"]) & set(frozen["seeds"]))
        self.assertEqual(
            set(config["split_seed_offsets"]),
            {"train", "validation", "test"},
        )

    @unittest.skipIf(numpy is None, "bootstrap test requires numpy")
    def test_bootstrap_mean_interval_is_deterministic(self) -> None:
        first = _bootstrap_mean_ci([0.0, 1.0, 2.0], replicates=100, seed=7)
        second = _bootstrap_mean_ci([0.0, 1.0, 2.0], replicates=100, seed=7)
        self.assertEqual(first, second)
        self.assertAlmostEqual(first["mean"], 1.0)


@unittest.skipIf(torch is None, "controlled PDE tests require torch")
class ControlledPDEReentryMathTests(unittest.TestCase):
    def test_analytic_field_moments_match_monte_carlo(self) -> None:
        geometry = torch.tensor([[0.2, -0.1]])
        mean = torch.tensor([[0.3, -0.2]])
        covariance = torch.tensor([[[0.04, 0.01], [0.01, 0.09]]])
        grid = torch.linspace(0.0, 1.0, 9)
        analytic_mean, analytic_variance = analytic_field_moments(
            geometry, mean, covariance, grid
        )
        generator = torch.Generator().manual_seed(13)
        standard = torch.randn(200000, 2, generator=generator)
        boundary = mean + standard @ torch.linalg.cholesky(covariance[0]).T
        field = poisson_solution(
            geometry.expand(boundary.shape[0], -1), boundary, grid
        )
        self.assertTrue(
            torch.allclose(analytic_mean[0], field.mean(0), atol=2e-3)
        )
        self.assertTrue(
            torch.allclose(analytic_variance[0], field.var(0), atol=2e-3)
        )

    def test_gauss_hermite_mean_is_exact_for_affine_solution(self) -> None:
        grid = torch.linspace(0.0, 1.0, 11)

        class ExactOperator(torch.nn.Module):
            def forward(self, geometry, boundary):
                return poisson_solution(geometry, boundary, grid)

        geometry = torch.tensor([[0.2, -0.1], [-0.4, 0.3]])
        mean = torch.tensor([[0.3, -0.2], [0.1, 0.4]])
        covariance = torch.tensor(
            [
                [[0.04, 0.01], [0.01, 0.09]],
                [[0.03, -0.005], [-0.005, 0.02]],
            ]
        )
        estimate = gauss_hermite_operator_mean(
            ExactOperator(),
            geometry,
            mean,
            covariance,
            order=5,
        )
        expected = poisson_solution(geometry, mean, grid)
        self.assertTrue(torch.allclose(estimate, expected, atol=1e-6))

    def test_tiny_runtime_uses_only_nonregistered_smoke_seed(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        registered = set(config["seeds"])
        smoke_seed = 9917301
        self.assertNotIn(smoke_seed, registered)
        config["seeds"] = [smoke_seed]
        config["train_geometries"] = 8
        config["validation_geometries"] = 4
        config["test_geometries"] = 4
        config["conditions_per_geometry"] = 2
        config["hidden_dim"] = 16
        for name in (
            "density_training",
            "operator_training",
            "direct_baseline_training",
        ):
            config[name]["maximum_epochs"] = 2
            config[name]["validation_interval"] = 1
            config[name]["early_stopping_patience"] = 2
        evaluation = config["evaluation"]
        evaluation["bc_samples"] = 16
        evaluation["gauss_hermite_order"] = 3
        evaluation["projective_samples"] = 8
        evaluation["projective_geometries"] = 4
        evaluation["projective_replicates"] = 2
        evaluation["sliced_projections"] = 4
        evaluation["bootstrap_replicates"] = 20
        result = run_experiment(config, require_cuda=False)
        self.assertFalse(result["failed_g1_relabeled"])
        self.assertEqual(result["seeds"][0]["seed"], smoke_seed)
        self.assertTrue(
            registered.isdisjoint(
                result["seeds"][0]["split_seeds"].values()
            )
        )


if __name__ == "__main__":
    unittest.main()
