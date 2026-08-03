import unittest

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

from aurora.controlled_pde import (
    _distribution_metrics,
    condition_gaussian,
    poisson_solution,
)


@unittest.skipIf(torch is None, "controlled PDE tests require torch")
class ControlledPDETests(unittest.TestCase):
    def test_exact_solution_respects_dirichlet_boundaries(self) -> None:
        geometry = torch.tensor([[0.4, -0.3]])
        boundary = torch.tensor([[1.2, -0.7]])
        grid = torch.tensor([0.0, 0.5, 1.0])
        solution = poisson_solution(geometry, boundary, grid)
        self.assertAlmostEqual(float(solution[0, 0]), 1.2, places=6)
        self.assertAlmostEqual(float(solution[0, -1]), -0.7, places=6)

    def test_partial_gaussian_conditioning_fixes_observed_component(self) -> None:
        mean = torch.tensor([[0.0, 0.0]])
        covariance = torch.tensor([[[1.0, 0.5], [0.5, 1.0]]])
        value = torch.tensor([[2.0, -9.0]])
        conditional_mean, conditional_covariance = condition_gaussian(
            mean, covariance, value, (1, 0)
        )
        self.assertAlmostEqual(float(conditional_mean[0, 0]), 2.0, places=6)
        self.assertAlmostEqual(float(conditional_mean[0, 1]), 1.0, places=6)
        self.assertAlmostEqual(
            float(conditional_covariance[0, 1, 1]), 0.75, places=6
        )

    def test_distribution_metrics_include_geometry_bootstrap_intervals(self) -> None:
        target = torch.tensor([[0.0, 1.0], [0.2, 0.8], [1.0, 0.0], [0.8, 0.2]])
        samples = target[:, None, :] + 0.1 * torch.randn(4, 16, 2)
        metrics = _distribution_metrics(
            samples,
            target,
            target,
            0.9,
            conditions_per_geometry=2,
            bootstrap_replicates=100,
            seed=17,
        )
        self.assertIn("geometry_bootstrap_ci95", metrics)
        self.assertEqual(
            len(metrics["geometry_bootstrap_ci95"]["energy_score"]), 2
        )


if __name__ == "__main__":
    unittest.main()
