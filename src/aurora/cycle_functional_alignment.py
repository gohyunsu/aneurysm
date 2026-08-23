"""Differentiable complete-cycle alignment terms for transient vector WSS.

These are training primitives, not a selected method or executable experiment.
All terms are computed from one reconstructed field, and every coefficient and
the reference-support floor are explicit caller inputs.
"""

from __future__ import annotations

from collections.abc import Mapping
import math

import torch


class CycleFunctionalAlignmentError(RuntimeError):
    """Raised when a complete-cycle objective is ill-defined."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise CycleFunctionalAlignmentError(label)


def _normalized_nonnegative_weights(weights: torch.Tensor, label: str) -> torch.Tensor:
    _require(weights.ndim == 1 and weights.numel() > 0, f"{label}_shape")
    _require(weights.dtype in (torch.float32, torch.float64), f"{label}_dtype")
    _require(bool(torch.isfinite(weights).all().item()), f"{label}_finite")
    _require(bool((weights >= 0).all().item()), f"{label}_negative")
    total = weights.sum()
    _require(bool((total > 0).item()), f"{label}_zero")
    return weights / total


def _relative_squared_error(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    weights: torch.Tensor,
    *,
    numerical_epsilon: float,
) -> torch.Tensor:
    expanded = weights
    while expanded.ndim < prediction.ndim:
        expanded = expanded.unsqueeze(-1)
    numerator = torch.sum(expanded * (prediction - reference).square())
    denominator = torch.sum(expanded * reference.square())
    _require(
        bool((denominator > numerical_epsilon).item()),
        "relative_error_denominator",
    )
    return numerator / denominator


def _cycle_statistics(
    field: torch.Tensor,
    normalized_phase_weights: torch.Tensor,
    *,
    numerical_epsilon: float,
) -> dict[str, torch.Tensor]:
    mean_vector = torch.sum(
        field * normalized_phase_weights.reshape(-1, 1, 1), dim=0
    )
    tawss = torch.sum(
        torch.linalg.vector_norm(field, dim=-1)
        * normalized_phase_weights.reshape(-1, 1),
        dim=0,
    )
    mean_magnitude = torch.linalg.vector_norm(mean_vector, dim=-1)
    ratio = mean_magnitude / torch.clamp(tawss, min=numerical_epsilon)
    osi = 0.5 * (1.0 - torch.clamp(ratio, min=0.0, max=1.0))
    return {
        "mean_vector": mean_vector,
        "tawss": tawss,
        "mean_vector_magnitude": mean_magnitude,
        "osi": osi,
        "jensen_gap": tawss - mean_magnitude,
    }


def complete_cycle_alignment_terms(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    phase_weights: torch.Tensor,
    vertex_areas: torch.Tensor,
    loss_weights: Mapping[str, float],
    *,
    reference_tawss_floor: float,
    osi_pseudo_huber_delta: float,
    numerical_epsilon: float = 1e-12,
) -> dict[str, torch.Tensor]:
    """Return field and nonlinear WSS-functional losses for one decoded cycle.

    ``prediction`` and ``reference`` have shape ``[T,N,3]``. Field,
    mean-vector and TAWSS terms are dimensionless relative squared errors. OSI
    uses an area-weighted pseudo-Huber loss on reference-defined active support.
    The function does not choose weights or apply a performance threshold.
    """

    _require(tuple(prediction.shape) == tuple(reference.shape), "field_shape")
    _require(
        prediction.ndim == 3
        and prediction.shape[0] >= 2
        and prediction.shape[1] >= 1
        and prediction.shape[2] == 3,
        "field_rank",
    )
    _require(
        prediction.dtype in (torch.float32, torch.float64)
        and reference.dtype == prediction.dtype,
        "field_dtype",
    )
    _require(
        bool(torch.isfinite(prediction).all().item())
        and bool(torch.isfinite(reference).all().item()),
        "field_finite",
    )
    _require(phase_weights.shape == (prediction.shape[0],), "phase_weight_shape")
    _require(vertex_areas.shape == (prediction.shape[1],), "vertex_area_shape")
    _require(reference_tawss_floor > 0.0, "reference_tawss_floor")
    _require(osi_pseudo_huber_delta > 0.0, "osi_pseudo_huber_delta")
    _require(numerical_epsilon > 0.0, "numerical_epsilon")
    _require(
        set(loss_weights) == {"field", "mean_vector", "tawss", "osi"},
        "loss_weight_keys",
    )
    for name, value in loss_weights.items():
        _require(
            math.isfinite(float(value)) and float(value) >= 0.0,
            f"loss_weight_{name}",
        )
    _require(any(float(value) > 0.0 for value in loss_weights.values()), "zero_loss")

    phase = _normalized_nonnegative_weights(
        phase_weights.to(dtype=prediction.dtype, device=prediction.device),
        "phase_weight",
    )
    area = _normalized_nonnegative_weights(
        vertex_areas.to(dtype=prediction.dtype, device=prediction.device),
        "vertex_area",
    )
    area_time = phase.reshape(-1, 1) * area.reshape(1, -1)
    reference_stats = _cycle_statistics(
        reference, phase, numerical_epsilon=numerical_epsilon
    )
    prediction_stats = _cycle_statistics(
        prediction, phase, numerical_epsilon=numerical_epsilon
    )

    field_term = _relative_squared_error(
        prediction, reference, area_time, numerical_epsilon=numerical_epsilon
    )
    tawss_term = _relative_squared_error(
        prediction_stats["tawss"],
        reference_stats["tawss"],
        area,
        numerical_epsilon=numerical_epsilon,
    )
    tawss_energy = torch.sum(area * reference_stats["tawss"].square())
    _require(bool((tawss_energy > numerical_epsilon).item()), "tawss_energy")
    mean_vector_term = torch.sum(
        area.unsqueeze(-1)
        * (
            prediction_stats["mean_vector"] - reference_stats["mean_vector"]
        ).square()
    ) / tawss_energy

    osi_support = reference_stats["tawss"] > reference_tawss_floor
    support_area = torch.sum(area * osi_support.to(dtype=area.dtype))
    _require(bool((support_area > numerical_epsilon).item()), "osi_reference_support")
    osi_difference = prediction_stats["osi"] - reference_stats["osi"]
    delta = torch.as_tensor(
        osi_pseudo_huber_delta, dtype=prediction.dtype, device=prediction.device
    )
    osi_robust_error = delta.square() * (
        torch.sqrt(1.0 + (osi_difference / delta).square()) - 1.0
    )
    osi_term = torch.sum(
        area * osi_support.to(dtype=area.dtype) * osi_robust_error
    ) / support_area

    terms = {
        "field": field_term,
        "mean_vector": mean_vector_term,
        "tawss": tawss_term,
        "osi": osi_term,
    }
    total = sum(float(loss_weights[name]) * value for name, value in terms.items())
    return {
        "total": total,
        "field": field_term,
        "mean_vector": mean_vector_term,
        "tawss": tawss_term,
        "osi": osi_term,
        "osi_reference_node_fraction": osi_support.to(prediction.dtype).mean(),
        "osi_reference_area_fraction": support_area,
        "reference_jensen_gap_minimum": reference_stats["jensen_gap"].min(),
        "prediction_jensen_gap_minimum": prediction_stats["jensen_gap"].min(),
    }


def field_anchored_gradient_combination(
    field_gradients: list[torch.Tensor],
    functional_gradients: list[torch.Tensor],
    *,
    functional_to_field_norm_ratio: float,
    numerical_epsilon: float = 1e-12,
) -> dict[str, object]:
    """Combine two gradient families while removing first-order field conflict.

    When the functional gradient has a negative inner product with the field
    gradient, only that conflicting component is removed. The retained
    functional gradient is then norm-matched to the field gradient before the
    explicit ratio is applied. This is an optimization control inspired by
    multi-objective gradient surgery, not a guarantee of finite-step metric
    non-inferiority.
    """

    _require(
        len(field_gradients) == len(functional_gradients)
        and len(field_gradients) > 0,
        "gradient_count",
    )
    _require(
        math.isfinite(functional_to_field_norm_ratio)
        and functional_to_field_norm_ratio >= 0.0,
        "gradient_ratio",
    )
    _require(numerical_epsilon > 0.0, "gradient_epsilon")
    for field, functional in zip(field_gradients, functional_gradients):
        _require(tuple(field.shape) == tuple(functional.shape), "gradient_shape")
        _require(
            field.dtype == functional.dtype
            and field.device == functional.device
            and field.dtype in (torch.float32, torch.float64),
            "gradient_type",
        )
        _require(
            bool(torch.isfinite(field).all().item())
            and bool(torch.isfinite(functional).all().item()),
            "gradient_finite",
        )

    field_norm_squared = sum(torch.sum(value.square()) for value in field_gradients)
    functional_norm_squared = sum(
        torch.sum(value.square()) for value in functional_gradients
    )
    inner_before = sum(
        torch.sum(field * functional)
        for field, functional in zip(field_gradients, functional_gradients)
    )
    _require(
        bool((field_norm_squared > numerical_epsilon).item()), "zero_field_gradient"
    )
    projection_coefficient = torch.clamp(
        inner_before / field_norm_squared, max=0.0
    )
    projected = [
        functional - projection_coefficient * field
        for field, functional in zip(field_gradients, functional_gradients)
    ]
    projected_norm_squared = sum(torch.sum(value.square()) for value in projected)
    field_norm = torch.sqrt(field_norm_squared)
    projected_norm = torch.sqrt(projected_norm_squared)
    if bool((projected_norm_squared > numerical_epsilon).item()):
        scale = (
            functional_to_field_norm_ratio
            * field_norm
            / torch.clamp(projected_norm, min=numerical_epsilon)
        )
    else:
        scale = torch.zeros((), dtype=field_norm.dtype, device=field_norm.device)
    combined = [field + scale * value for field, value in zip(field_gradients, projected)]
    inner_after = sum(
        torch.sum(field * value) for field, value in zip(field_gradients, projected)
    )
    return {
        "combined_gradients": combined,
        "projected_functional_gradients": projected,
        "field_norm": field_norm,
        "functional_norm_before": torch.sqrt(functional_norm_squared),
        "functional_norm_after_projection": projected_norm,
        "inner_product_before": inner_before,
        "inner_product_after_projection": inner_after,
        "projection_applied": inner_before < 0,
        "functional_scale": scale,
    }
