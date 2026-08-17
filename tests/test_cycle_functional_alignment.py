from __future__ import annotations

import json
import unittest
from pathlib import Path

import torch

from aurora.cycle_functional_alignment import (
    CycleFunctionalAlignmentError,
    complete_cycle_alignment_terms,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_cycle_functional_alignment_v1.json"


def fixture() -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    phase = torch.arange(8, dtype=torch.float64) * (2.0 * torch.pi / 8.0)
    field = torch.zeros((8, 3, 3), dtype=torch.float64)
    field[:, 0, 0] = 1.0 + 0.2 * torch.sin(phase)
    field[:, 0, 1] = 0.2 * torch.cos(phase)
    field[:, 1, 0] = 0.45 * torch.cos(phase)
    field[:, 1, 1] = 0.8 + 0.1 * torch.sin(phase)
    field[:, 2, 0] = -0.6 + 0.1 * torch.cos(phase)
    field[:, 2, 1] = 0.25 * torch.sin(phase)
    phase_weights = torch.tensor(
        [0.5, 1.0, 1.5, 1.0, 0.5, 1.0, 1.5, 1.0], dtype=torch.float64
    )
    areas = torch.tensor([0.2, 0.3, 0.5], dtype=torch.float64)
    return field, phase_weights, areas


def all_terms(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    phase_weights: torch.Tensor,
    areas: torch.Tensor,
) -> dict[str, torch.Tensor]:
    return complete_cycle_alignment_terms(
        prediction,
        reference,
        phase_weights,
        areas,
        {"field": 1.0, "mean_vector": 0.3, "tawss": 0.2, "osi": 0.1},
        reference_tawss_floor=0.05,
        osi_pseudo_huber_delta=0.02,
    )


class CycleFunctionalAlignmentTests(unittest.TestCase):
    def test_config_is_non_executable_and_threshold_free(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config["status"], "dataset_free_non_executable_loss_kernel")
        self.assertIsNone(config["decision_rule"]["absolute_performance_threshold"])
        self.assertFalse(config["authorization"]["read_real_field"])
        self.assertFalse(config["authorization"]["select_method"])
        self.assertEqual(config["authorization"]["excluded_server"], "junjinyong")

    def test_exact_cycle_has_zero_terms_and_finite_gradient(self) -> None:
        reference, phase_weights, areas = fixture()
        prediction = reference.clone().requires_grad_(True)
        result = all_terms(prediction, reference, phase_weights, areas)
        for key in ("total", "field", "mean_vector", "tawss", "osi"):
            torch.testing.assert_close(
                result[key], torch.tensor(0.0, dtype=torch.float64), atol=1e-14, rtol=0
            )
        result["total"].backward()
        self.assertTrue(bool(torch.isfinite(prediction.grad).all().item()))

    def test_terms_are_common_rotation_and_scale_invariant(self) -> None:
        reference, phase_weights, areas = fixture()
        prediction = reference.clone()
        prediction[:, 0, 1] += 0.07 * torch.sin(
            torch.arange(8, dtype=torch.float64) * (2.0 * torch.pi / 8.0)
        )
        prediction[:, 1, 0] *= 0.88
        base = all_terms(prediction, reference, phase_weights, areas)

        angle = torch.tensor(0.61, dtype=torch.float64)
        cosine, sine = torch.cos(angle), torch.sin(angle)
        rotation = torch.stack(
            (
                torch.stack((cosine, -sine, torch.tensor(0.0, dtype=torch.float64))),
                torch.stack((sine, cosine, torch.tensor(0.0, dtype=torch.float64))),
                torch.tensor([0.0, 0.0, 1.0], dtype=torch.float64),
            )
        )
        rotated = all_terms(
            2.7 * prediction @ rotation.T,
            2.7 * reference @ rotation.T,
            phase_weights,
            areas,
        )
        for key in ("field", "mean_vector", "tawss", "osi", "total"):
            torch.testing.assert_close(rotated[key], base[key], atol=1e-12, rtol=1e-12)

    def test_reference_only_osi_support_is_explicit(self) -> None:
        reference, phase_weights, areas = fixture()
        reference[:, 2] = 1e-4
        prediction = reference.clone()
        prediction[:, 2, 0] = 100.0
        result = all_terms(prediction, reference, phase_weights, areas)
        torch.testing.assert_close(
            result["osi_reference_node_fraction"],
            torch.tensor(2.0 / 3.0, dtype=torch.float64),
        )
        torch.testing.assert_close(
            result["osi_reference_area_fraction"],
            torch.tensor(0.5, dtype=torch.float64),
        )
        torch.testing.assert_close(
            result["osi"], torch.tensor(0.0, dtype=torch.float64), atol=1e-14, rtol=0
        )
        self.assertGreater(float(result["field"].item()), 0.0)

    def test_nontrivial_cycle_passes_autograd_gradcheck(self) -> None:
        reference, phase_weights, areas = fixture()
        prediction = (reference * 0.93 + 0.04).requires_grad_(True)

        def objective(value: torch.Tensor) -> torch.Tensor:
            return all_terms(value, reference, phase_weights, areas)["total"]

        self.assertTrue(
            torch.autograd.gradcheck(
                objective, (prediction,), eps=1e-6, atol=2e-5, rtol=2e-4
            )
        )

    def test_zero_prediction_is_finite_and_penalized(self) -> None:
        reference, phase_weights, areas = fixture()
        prediction = torch.zeros_like(reference, requires_grad=True)
        result = all_terms(prediction, reference, phase_weights, areas)
        self.assertTrue(bool(torch.isfinite(result["total"]).item()))
        self.assertGreater(float(result["field"].item()), 0.0)
        self.assertGreater(float(result["tawss"].item()), 0.0)
        self.assertGreater(float(result["osi"].item()), 0.0)
        result["total"].backward()
        self.assertTrue(bool(torch.isfinite(prediction.grad).all().item()))

    def test_zero_reference_mean_vector_remains_well_defined(self) -> None:
        reference = torch.tensor(
            [[[1.0, 0.0, 0.0]], [[-1.0, 0.0, 0.0]]], dtype=torch.float64
        )
        prediction = reference.clone()
        prediction[:, 0, 1] = 0.1
        result = all_terms(
            prediction,
            reference,
            torch.ones(2, dtype=torch.float64),
            torch.ones(1, dtype=torch.float64),
        )
        self.assertTrue(bool(torch.isfinite(result["mean_vector"]).item()))
        self.assertGreater(float(result["mean_vector"].item()), 0.0)

    def test_invalid_inputs_and_loss_weights_fail_closed(self) -> None:
        reference, phase_weights, areas = fixture()
        with self.assertRaisesRegex(CycleFunctionalAlignmentError, "loss_weight_keys"):
            complete_cycle_alignment_terms(
                reference,
                reference,
                phase_weights,
                areas,
                {"field": 1.0},
                reference_tawss_floor=0.05,
                osi_pseudo_huber_delta=0.02,
            )
        with self.assertRaisesRegex(CycleFunctionalAlignmentError, "zero_loss"):
            complete_cycle_alignment_terms(
                reference,
                reference,
                phase_weights,
                areas,
                {"field": 0.0, "mean_vector": 0.0, "tawss": 0.0, "osi": 0.0},
                reference_tawss_floor=0.05,
                osi_pseudo_huber_delta=0.02,
            )
        with self.assertRaisesRegex(CycleFunctionalAlignmentError, "loss_weight_osi"):
            complete_cycle_alignment_terms(
                reference,
                reference,
                phase_weights,
                areas,
                {
                    "field": 1.0,
                    "mean_vector": 0.0,
                    "tawss": 0.0,
                    "osi": float("inf"),
                },
                reference_tawss_floor=0.05,
                osi_pseudo_huber_delta=0.02,
            )
        with self.assertRaisesRegex(CycleFunctionalAlignmentError, "field_finite"):
            invalid = reference.clone()
            invalid[0, 0, 0] = float("nan")
            all_terms(invalid, reference, phase_weights, areas)
