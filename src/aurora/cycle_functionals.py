"""Method-free transient WSS functionals with explicit validity masks.

This module contains no dataset loader, model, filesystem or scheduler entry
point.  It makes the future evaluation definitions for TAWSS, OSI and RRT
explicit without treating those established quantities as novelty.
"""

from __future__ import annotations

from typing import Any


class CycleFunctionalError(RuntimeError):
    """Raised when a cycle-functional evaluation is not well defined."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise CycleFunctionalError(reason)


def _finite(value: Any, torch: Any) -> bool:
    return bool(torch.isfinite(value).all().item())


def compute_cycle_functionals(
    wss: Any,
    phase_weights: Any,
    torch: Any,
    *,
    activity_epsilon: float = 1e-12,
) -> dict[str, Any]:
    """Compute quadrature-weighted nodewise TAWSS, OSI and RRT.

    ``wss`` has shape ``[T,N,3]`` and ``phase_weights`` has shape ``[T]``.
    Weights are mandatory so uniform sampling is never inferred silently.
    OSI is undefined where TAWSS is inactive, and RRT is undefined where the
    mean-vector magnitude is inactive.  Undefined values are returned as NaN
    together with explicit masks; callers must report coverage rather than
    silently replacing singular values with a large finite constant.
    """

    _require(wss.ndim == 3 and int(wss.shape[-1]) == 3, "wss_shape")
    _require(wss.dtype in (torch.float32, torch.float64), "wss_dtype")
    _require(int(wss.shape[0]) >= 2 and int(wss.shape[1]) >= 1, "cycle_shape")
    _require(
        phase_weights.ndim == 1
        and int(phase_weights.shape[0]) == int(wss.shape[0]),
        "phase_weight_shape",
    )
    _require(activity_epsilon > 0, "activity_epsilon")
    _require(_finite(wss, torch) and _finite(phase_weights, torch), "input_nonfinite")
    _require(bool((phase_weights >= 0).all().item()), "negative_phase_weight")
    _require(
        int((phase_weights > 0).sum().item()) >= 2,
        "insufficient_positive_phase_weights",
    )

    weights = phase_weights.to(dtype=wss.dtype, device=wss.device)
    weight_sum = weights.sum()
    _require(bool((weight_sum > 0).item()), "zero_phase_weight_sum")
    normalized_weights = weights / weight_sum

    mean_vector = torch.sum(
        wss * normalized_weights.reshape(-1, 1, 1),
        dim=0,
    )
    instantaneous_magnitude = torch.linalg.vector_norm(wss, dim=-1)
    tawss = torch.sum(
        instantaneous_magnitude * normalized_weights.reshape(-1, 1),
        dim=0,
    )
    mean_vector_magnitude = torch.linalg.vector_norm(mean_vector, dim=-1)
    jensen_gap = tawss - mean_vector_magnitude

    osi_valid = tawss > activity_epsilon
    safe_tawss = torch.clamp(tawss, min=activity_epsilon)
    mean_to_tawss_ratio = torch.clamp(
        mean_vector_magnitude / safe_tawss,
        min=0.0,
        max=1.0,
    )
    nan = torch.full_like(tawss, float("nan"))
    osi = torch.where(
        osi_valid,
        0.5 * (1.0 - mean_to_tawss_ratio),
        nan,
    )

    rrt_valid = mean_vector_magnitude > activity_epsilon
    safe_mean_magnitude = torch.clamp(
        mean_vector_magnitude,
        min=activity_epsilon,
    )
    rrt = torch.where(rrt_valid, 1.0 / safe_mean_magnitude, nan)
    rrt_denominator = (1.0 - 2.0 * osi) * tawss
    rrt_from_definition = torch.where(
        rrt_valid & osi_valid,
        1.0 / torch.clamp(rrt_denominator, min=activity_epsilon),
        nan,
    )
    rrt_redundancy_absolute_error = torch.where(
        rrt_valid & osi_valid,
        torch.abs(rrt - rrt_from_definition),
        nan,
    )

    _require(
        _finite(mean_vector, torch)
        and _finite(tawss, torch)
        and _finite(mean_vector_magnitude, torch),
        "finite_moment_failure",
    )

    return {
        "normalized_phase_weights": normalized_weights,
        "mean_vector": mean_vector,
        "mean_vector_magnitude": mean_vector_magnitude,
        "tawss": tawss,
        "jensen_gap": jensen_gap,
        "osi": osi,
        "osi_valid": osi_valid,
        "rrt": rrt,
        "rrt_valid": rrt_valid,
        "rrt_from_definition": rrt_from_definition,
        "rrt_redundancy_absolute_error": rrt_redundancy_absolute_error,
    }
