import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

from aurora.nonlinear_pde import load_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "nonlinear_pde_n0.json"


class NonlinearPDEContractTests(unittest.TestCase):
    def test_n0_is_solver_gate_not_claim(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["source_gate"], "G1s")
        self.assertEqual(config["stage"], "solver_nontriviality")
        self.assertFalse(config["may_establish_method_novelty"])
        self.assertFalse(config["may_authorize_irregular_3d_headline"])
        self.assertEqual(config["pde"]["boundary_components"], 8)
        self.assertEqual(config["pde"]["reference_grid_points"], 65)
        self.assertEqual(config["pde"]["grid_points"], 33)

    def test_g1s_pin_is_exact(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            config["source_result_sha256"],
            "7e9797abaaf4ff6b7f2c5ab38fa75d768b24af0d6f0d00f74276ec488d6ba7a9",
        )


@unittest.skipIf(torch is None, "nonlinear PDE tests require torch")
class NonlinearPDERuntimeTests(unittest.TestCase):
    def test_boundary_law_is_spd_and_route_consistent(self) -> None:
        from aurora.nonlinear_pde import (
            boundary_law,
            conditioning_route_residual,
            sample_boundary,
        )

        context = torch.tensor(
            [[-0.5, 0.25, 0.1, -0.2, 0.4], [0.4, -0.1, 0.6, 0.3, -0.7]]
        )
        weights, means, covariances = boundary_law(context)
        self.assertEqual(tuple(weights.shape), (2, 2))
        self.assertEqual(tuple(means.shape), (2, 2, 8))
        self.assertTrue(torch.all(torch.linalg.eigvalsh(covariances) > 0))
        boundary = sample_boundary(weights, means, covariances, 2, 77)
        residual = conditioning_route_residual(
            weights, means, covariances, boundary[:, 0]
        )
        self.assertLess(residual, 2e-5)

    def test_registered_parameter_envelopes_and_physical_flux(self) -> None:
        from aurora.nonlinear_pde import _pde_fields, solution_functionals

        context = torch.tensor(
            [
                [0.0, 0.0, -1.0, 0.0, -1.0],
                [0.0, 0.0, 1.0, 0.0, 1.0],
            ]
        )
        diffusivity, _, nonlinearity = _pde_fields(context, 17)
        self.assertGreaterEqual(float(diffusivity.min()), 0.7 - 1e-6)
        self.assertLessEqual(float(diffusivity.max()), 1.3 + 1e-6)
        self.assertTrue(torch.allclose(nonlinearity, torch.tensor([8.0, 40.0])))

        coordinate = torch.linspace(0.0, 1.0, 17)
        solution = coordinate[None, None, :].expand(2, 17, -1).clone()
        functionals = solution_functionals(solution, context)
        expected = -0.5 * (
            diffusivity[:, 1:-1, -1] + diffusivity[:, 1:-1, -2]
        ).mean(dim=1)
        self.assertTrue(torch.allclose(functionals[:, 3], expected, atol=1e-6))

    def test_small_solver_converges_and_preserves_boundary(self) -> None:
        from aurora.nonlinear_pde import solve_semilinear

        context = torch.zeros(2, 5)
        boundary = torch.tensor(
            [
                [0.1, 0.0, -0.1, 0.0, 0.05, 0.0, -0.05, 0.0],
                [-0.1, 0.05, 0.1, -0.05, 0.0, 0.05, 0.0, -0.05],
            ]
        )
        solution, diagnostics = solve_semilinear(
            context,
            boundary,
            grid_points=17,
            maximum_iterations=3000,
            tolerance=1e-5,
            check_interval=25,
            relaxation=0.9,
        )
        self.assertTrue(diagnostics["converged"])
        self.assertTrue(torch.allclose(solution[:, 0, 0], torch.zeros(2)))
        self.assertTrue(torch.isfinite(solution).all())


if __name__ == "__main__":
    unittest.main()
