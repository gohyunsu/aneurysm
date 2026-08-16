from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # PyTorch is pinned in public Quality
    torch = None

from aurora.cycle_functionals import CycleFunctionalError, compute_cycle_functionals


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "cycle_functional_metric_kernel_v1.json"


@unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
class CycleFunctionalTests(unittest.TestCase):
    def test_config_keeps_metrics_method_free_and_non_executable(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config["status"], "synthetic_only_non_executable_metric_kernel")
        self.assertTrue(config["semantics"]["phase_weights_required"])
        self.assertEqual(config["semantics"]["rrt_role"], "redundant_secondary_only")
        self.assertFalse(config["authorization"]["read_real_field"])
        self.assertFalse(config["authorization"]["select_architecture"])
        self.assertEqual(config["excluded_server"], "junjinyong")

    def test_constant_and_reversing_cycles_have_expected_functionals(self) -> None:
        weights = torch.ones(2, dtype=torch.float64)
        constant = torch.tensor(
            [[[2.0, 0.0, 0.0]], [[2.0, 0.0, 0.0]]],
            dtype=torch.float64,
        )
        constant_result = compute_cycle_functionals(constant, weights, torch)
        torch.testing.assert_close(
            constant_result["tawss"], torch.tensor([2.0], dtype=torch.float64)
        )
        torch.testing.assert_close(
            constant_result["osi"], torch.tensor([0.0], dtype=torch.float64)
        )
        torch.testing.assert_close(
            constant_result["rrt"], torch.tensor([0.5], dtype=torch.float64)
        )

        reversing = torch.tensor(
            [[[1.0, 0.0, 0.0]], [[-1.0, 0.0, 0.0]]],
            dtype=torch.float64,
        )
        reversing_result = compute_cycle_functionals(reversing, weights, torch)
        torch.testing.assert_close(
            reversing_result["osi"], torch.tensor([0.5], dtype=torch.float64)
        )
        self.assertFalse(bool(reversing_result["rrt_valid"].item()))
        self.assertTrue(bool(torch.isnan(reversing_result["rrt"]).item()))

    def test_explicit_nonuniform_phase_quadrature(self) -> None:
        field = torch.tensor(
            [[[1.0, 0.0, 0.0]], [[3.0, 0.0, 0.0]]],
            dtype=torch.float64,
        )
        weights = torch.tensor([1.0, 3.0], dtype=torch.float64)
        result = compute_cycle_functionals(field, weights, torch)
        torch.testing.assert_close(
            result["normalized_phase_weights"],
            torch.tensor([0.25, 0.75], dtype=torch.float64),
        )
        torch.testing.assert_close(
            result["mean_vector"],
            torch.tensor([[2.5, 0.0, 0.0]], dtype=torch.float64),
        )
        torch.testing.assert_close(
            result["tawss"], torch.tensor([2.5], dtype=torch.float64)
        )

    def test_rotation_scale_and_phase_replication_properties(self) -> None:
        phase = torch.arange(8, dtype=torch.float64) * (2.0 * torch.pi / 8.0)
        field = torch.zeros((8, 2, 3), dtype=torch.float64)
        field[:, 0, 0] = 0.8 + 0.2 * torch.sin(phase)
        field[:, 0, 1] = 0.3 * torch.cos(phase)
        field[:, 1, 0] = 0.4 * torch.cos(phase)
        field[:, 1, 1] = -0.6 + 0.1 * torch.sin(phase)
        weights = torch.ones(8, dtype=torch.float64)
        base = compute_cycle_functionals(field, weights, torch)

        angle = torch.tensor(0.71, dtype=torch.float64)
        cosine, sine = torch.cos(angle), torch.sin(angle)
        rotation = torch.stack(
            (
                torch.stack((cosine, -sine, torch.tensor(0.0, dtype=field.dtype))),
                torch.stack((sine, cosine, torch.tensor(0.0, dtype=field.dtype))),
                torch.tensor([0.0, 0.0, 1.0], dtype=field.dtype),
            )
        )
        rotated = compute_cycle_functionals(field @ rotation.T, weights, torch)
        torch.testing.assert_close(rotated["mean_vector"], base["mean_vector"] @ rotation.T)
        torch.testing.assert_close(rotated["tawss"], base["tawss"])
        torch.testing.assert_close(rotated["osi"], base["osi"])

        scaled = compute_cycle_functionals(2.5 * field, weights, torch)
        torch.testing.assert_close(scaled["tawss"], 2.5 * base["tawss"])
        torch.testing.assert_close(scaled["osi"], base["osi"])
        torch.testing.assert_close(scaled["rrt"], base["rrt"] / 2.5)

        repeated = compute_cycle_functionals(
            torch.repeat_interleave(field, repeats=2, dim=0),
            torch.ones(16, dtype=torch.float64),
            torch,
        )
        for key in ("mean_vector", "tawss", "osi", "rrt"):
            torch.testing.assert_close(repeated[key], base[key])

    def test_rrt_is_redundant_and_invalid_nodes_are_explicit(self) -> None:
        field = torch.tensor(
            [
                [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                [[0.0, 1.0, 0.0], [0.0, 0.0, 0.0]],
            ],
            dtype=torch.float64,
        )
        result = compute_cycle_functionals(
            field, torch.ones(2, dtype=torch.float64), torch
        )
        self.assertTrue(bool(result["rrt_valid"][0].item()))
        self.assertFalse(bool(result["rrt_valid"][1].item()))
        self.assertFalse(bool(result["osi_valid"][1].item()))
        torch.testing.assert_close(
            result["rrt"][0], result["rrt_from_definition"][0]
        )
        torch.testing.assert_close(
            result["rrt_redundancy_absolute_error"][0],
            torch.tensor(0.0, dtype=torch.float64),
            atol=1e-14,
            rtol=0.0,
        )
        self.assertTrue(bool(torch.isnan(result["osi"][1]).item()))
        self.assertTrue(bool(torch.isnan(result["rrt"][1]).item()))

    def test_invalid_cycles_and_weights_fail_closed(self) -> None:
        field = torch.ones((3, 2, 3), dtype=torch.float64)
        cases = (
            (torch.ones((3, 2), dtype=torch.float64), "phase_weight_shape"),
            (torch.tensor([1.0, -1.0, 1.0]), "negative_phase_weight"),
            (torch.tensor([1.0, 0.0, 0.0]), "insufficient_positive"),
        )
        for weights, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(CycleFunctionalError, reason):
                    compute_cycle_functionals(field, weights, torch)

        with self.assertRaisesRegex(CycleFunctionalError, "wss_dtype"):
            compute_cycle_functionals(
                torch.ones((3, 2, 3), dtype=torch.int64),
                torch.ones(3),
                torch,
            )

        nonfinite = field.clone()
        nonfinite[0, 0, 0] = float("nan")
        with self.assertRaisesRegex(CycleFunctionalError, "input_nonfinite"):
            compute_cycle_functionals(nonfinite, torch.ones(3), torch)


if __name__ == "__main__":
    unittest.main()
