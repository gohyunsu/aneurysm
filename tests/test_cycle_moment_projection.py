from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # PyTorch is pinned in public Quality
    torch = None

from aurora.cycle_moment_projection import (
    CycleMomentProjectionError,
    jensen_cone_mean_magnitude,
    project_cycle_moments,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "cycle_moment_projection_prototype_v1.json"


@unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
class CycleMomentProjectionTests(unittest.TestCase):
    @staticmethod
    def _fixture(dtype: object = None) -> tuple[object, object, object, object]:
        dtype = dtype or torch.float64
        phase = torch.arange(16, dtype=dtype) * (2.0 * torch.pi / 16.0)
        raw = torch.zeros((16, 3, 3), dtype=dtype)
        raw[:, 0, 0] = torch.sin(phase)
        raw[:, 0, 1] = 0.3 * torch.cos(phase)
        raw[:, 1, 0] = 0.4 * torch.cos(phase)
        raw[:, 1, 1] = torch.sin(phase)
        raw[:, 2, 0] = 0.2 * torch.sin(2.0 * phase)
        raw[:, 2, 1] = 0.1 * torch.cos(phase)
        mean = torch.tensor([[0.7, 0.1, 0.0], [0.2, -0.3, 0.0], [0.0, 0.0, 0.0]], dtype=dtype)
        target = torch.tensor([1.0, 0.8, 0.4], dtype=dtype)
        normals = torch.tensor([[0.0, 0.0, 1.0]] * 3, dtype=dtype)
        return raw, mean, target, normals

    def test_config_is_synthetic_only_and_non_executable(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config["status"], "synthetic_only_non_executable_prototype")
        self.assertFalse(config["authorization"]["read_real_field"])
        self.assertFalse(config["authorization"]["select_architecture"])
        self.assertFalse(config["authorization"]["submit_pbs_or_use_gpu"])
        self.assertEqual(config["excluded_server"], "junjinyong")

    def test_projection_matches_both_cycle_moments_and_tangency(self) -> None:
        raw, mean, target, normals = self._fixture()
        result = project_cycle_moments(raw, mean, target, normals, torch)
        torch.testing.assert_close(result["achieved_mean_vector"], mean, atol=1e-10, rtol=1e-10)
        torch.testing.assert_close(
            result["achieved_mean_magnitude"], target, atol=2e-7, rtol=2e-7
        )
        self.assertLess(float(result["maximum_absolute_normal_component"].item()), 1e-12)
        self.assertTrue(bool(result["strict_jensen_interior"].all().item()))

    def test_jensen_infeasibility_and_inactive_residual_fail_closed(self) -> None:
        raw, mean, target, normals = self._fixture()
        bad_target = target.clone()
        bad_target[0] = 0.1
        with self.assertRaisesRegex(CycleMomentProjectionError, "jensen_cone"):
            project_cycle_moments(raw, mean, bad_target, normals, torch)
        with self.assertRaisesRegex(CycleMomentProjectionError, "inactive_residual"):
            project_cycle_moments(
                torch.zeros_like(raw), mean, target, normals, torch
            )

    def test_rotation_equivariance_is_exact_up_to_solver_tolerance(self) -> None:
        raw, mean, target, normals = self._fixture()
        angle = torch.tensor(0.63, dtype=raw.dtype)
        cosine = torch.cos(angle)
        sine = torch.sin(angle)
        rotation = torch.stack(
            (
                torch.stack((cosine, -sine, torch.tensor(0.0, dtype=raw.dtype))),
                torch.stack((sine, cosine, torch.tensor(0.0, dtype=raw.dtype))),
                torch.tensor([0.0, 0.0, 1.0], dtype=raw.dtype),
            )
        )
        original = project_cycle_moments(raw, mean, target, normals, torch)
        rotated = project_cycle_moments(
            raw @ rotation.T, mean @ rotation.T, target, normals @ rotation.T, torch
        )
        torch.testing.assert_close(
            rotated["field"], original["field"] @ rotation.T, atol=2e-7, rtol=2e-7
        )

    def test_boundary_root_preserves_unidirectional_pulsatility(self) -> None:
        residual = torch.zeros((8, 1, 3), dtype=torch.float64)
        residual[:, 0, 0] = torch.tensor(
            [-0.2, -0.1, 0.0, 0.1, 0.2, 0.1, 0.0, -0.1], dtype=torch.float64
        )
        mean = torch.tensor([[1.0, 0.0, 0.0]], dtype=torch.float64)
        target = torch.tensor([1.0], dtype=torch.float64)
        normals = torch.tensor([[0.0, 0.0, 1.0]], dtype=torch.float64)
        result = project_cycle_moments(residual, mean, target, normals, torch)
        torch.testing.assert_close(result["scale"], torch.ones_like(target))
        torch.testing.assert_close(result["field"], mean.unsqueeze(0) + residual)

    def test_cone_parameterization_and_gradients_are_finite(self) -> None:
        raw, mean, _, normals = self._fixture()
        raw.requires_grad_(True)
        mean.requires_grad_(True)
        cone_coordinate = torch.tensor([-0.2, 0.1, -0.4], dtype=raw.dtype, requires_grad=True)
        target = jensen_cone_mean_magnitude(mean, cone_coordinate, torch)
        self.assertTrue(bool((target >= torch.linalg.vector_norm(mean, dim=-1)).all().item()))
        result = project_cycle_moments(raw, mean, target, normals, torch)
        loss = result["field"].square().mean() + result["scale"].mean()
        loss.backward()
        for value in (raw.grad, mean.grad, cone_coordinate.grad):
            self.assertIsNotNone(value)
            self.assertTrue(bool(torch.isfinite(value).all().item()))
        self.assertGreater(float(cone_coordinate.grad.abs().sum().item()), 0.0)
        self.assertTrue(bool((result["strict_root_derivative"] > 0).all().item()))

    def test_backward_graph_does_not_grow_with_bisection_iterations(self) -> None:
        raw, mean, target, normals = self._fixture()

        def graph_nodes(iterations: int) -> int:
            local_raw = raw.clone().requires_grad_(True)
            local_mean = mean.clone().requires_grad_(True)
            result = project_cycle_moments(
                local_raw,
                local_mean,
                target,
                normals,
                torch,
                maximum_iterations=iterations,
            )
            pending = [result["field"].grad_fn]
            seen: set[object] = set()
            while pending:
                node = pending.pop()
                if node is None or node in seen:
                    continue
                seen.add(node)
                pending.extend(parent for parent, _ in node.next_functions)
            return len(seen)

        self.assertEqual(graph_nodes(8), graph_nodes(64))


if __name__ == "__main__":
    unittest.main()
