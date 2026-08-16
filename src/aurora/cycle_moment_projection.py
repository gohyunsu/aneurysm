"""Synthetic-only prototype for a cycle-moment-consistent WSS readout.

This module has no dataset, filesystem, scheduler or model-training entry
point.  It tests the mathematical mechanism described by the AneuG direct-
prior reappraisal before D6 activation or architecture selection.

For a tangent mean vector ``m``, target mean magnitude ``a >= ||m||`` and a
raw tangent residual cycle ``r_t`` with zero temporal mean, the prototype finds
the non-negative scale closest to one such that

    mean_t ||m + scale * r_t|| = a.

The final cycle therefore has mean vector ``m`` and mean magnitude ``a`` up to
the registered numerical tolerance.  These are self-consistency guarantees,
not guarantees of agreement with CFD.
"""

from __future__ import annotations

from typing import Any


class CycleMomentProjectionError(RuntimeError):
    """Raised when the proposed moment projection is undefined or infeasible."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise CycleMomentProjectionError(reason)


def _finite(value: Any, torch: Any) -> bool:
    return bool(torch.isfinite(value).all().item())


def jensen_cone_mean_magnitude(mean_vector: Any, cone_coordinate: Any, torch: Any) -> Any:
    """Map an unconstrained scalar coordinate into ``a >= ||m||``.

    ``softplus`` makes the cone slack non-negative without clipping the mean
    vector.  This parameterization is a feasibility device, not a physical
    conservation law or a novelty claim.
    """

    _require(mean_vector.ndim >= 1 and int(mean_vector.shape[-1]) == 3, "mean_vector_shape")
    _require(tuple(cone_coordinate.shape) == tuple(mean_vector.shape[:-1]), "cone_coordinate_shape")
    _require(_finite(mean_vector, torch) and _finite(cone_coordinate, torch), "cone_parameter_nonfinite")
    slack = torch.nn.functional.softplus(cone_coordinate)
    mean_norm = torch.linalg.vector_norm(mean_vector, dim=-1)
    return torch.sqrt(mean_norm * mean_norm + slack * slack)


def _mean_cycle_magnitude(mean_vector: Any, residual: Any, scale: Any, torch: Any) -> Any:
    field = mean_vector.unsqueeze(0) + residual * scale.unsqueeze(0).unsqueeze(-1)
    return torch.linalg.vector_norm(field, dim=-1).mean(dim=0)


def project_cycle_moments(
    raw_residual: Any,
    mean_vector: Any,
    mean_magnitude: Any,
    normals: Any,
    torch: Any,
    *,
    maximum_iterations: int = 48,
    absolute_tolerance: float = 1e-7,
    relative_tolerance: float = 1e-6,
    activity_epsilon: float = 1e-10,
) -> dict[str, Any]:
    """Construct a tangent cycle with specified first cycle moments.

    Shapes are ``raw_residual[T,N,3]``, ``mean_vector[N,3]``,
    ``mean_magnitude[N]`` and ``normals[N,3]``.  The raw residual is projected
    to each tangent plane and centred over time.  A vectorized monotone root
    solve chooses the residual scale closest to one.  Choosing the closest
    root preserves unidirectional magnitude pulsatility when the Jensen
    boundary has a non-unique solution.
    """

    _require(raw_residual.ndim == 3 and int(raw_residual.shape[-1]) == 3, "raw_residual_shape")
    _require(mean_vector.ndim == 2 and int(mean_vector.shape[-1]) == 3, "mean_vector_shape")
    _require(normals.ndim == 2 and int(normals.shape[-1]) == 3, "normal_shape")
    _require(mean_magnitude.ndim == 1, "mean_magnitude_shape")
    node_count = int(raw_residual.shape[1])
    _require(
        int(mean_vector.shape[0]) == int(normals.shape[0]) == int(mean_magnitude.shape[0]) == node_count,
        "node_count",
    )
    _require(int(raw_residual.shape[0]) >= 2, "phase_count")
    _require(maximum_iterations >= 8, "maximum_iterations")
    _require(absolute_tolerance > 0 and relative_tolerance > 0, "tolerance")
    _require(activity_epsilon > 0, "activity_epsilon")
    _require(
        _finite(raw_residual, torch)
        and _finite(mean_vector, torch)
        and _finite(mean_magnitude, torch)
        and _finite(normals, torch),
        "input_nonfinite",
    )

    normal_norm = torch.linalg.vector_norm(normals, dim=-1, keepdim=True)
    _require(bool((normal_norm > activity_epsilon).all().item()), "zero_normal")
    unit_normals = normals / normal_norm

    tangent_mean = mean_vector - torch.sum(mean_vector * unit_normals, dim=-1, keepdim=True) * unit_normals
    tangent_residual = raw_residual - torch.sum(
        raw_residual * unit_normals.unsqueeze(0), dim=-1, keepdim=True
    ) * unit_normals.unsqueeze(0)
    tangent_residual = tangent_residual - tangent_residual.mean(dim=0, keepdim=True)

    mean_norm = torch.linalg.vector_norm(tangent_mean, dim=-1)
    tolerance = absolute_tolerance + relative_tolerance * torch.maximum(
        mean_magnitude.abs(), mean_norm
    )
    _require(bool((mean_magnitude >= mean_norm - tolerance).all().item()), "jensen_cone_infeasible")
    target = torch.maximum(mean_magnitude, mean_norm)

    residual_mean_norm = torch.linalg.vector_norm(tangent_residual, dim=-1).mean(dim=0)
    strict_target = target > mean_norm + tolerance
    _require(
        not bool((strict_target & (residual_mean_norm <= activity_epsilon)).any().item()),
        "inactive_residual_for_strict_target",
    )

    one = torch.ones_like(target)
    zero = torch.zeros_like(target)

    # Bracketing is a numerical root locator, not a learned computation.  Keep
    # its repeated field evaluations out of the backward graph, then restore
    # the strict-interior derivative with one implicit correction below.
    with torch.no_grad():
        value_at_one = _mean_cycle_magnitude(tangent_mean, tangent_residual, one, torch)
        close_at_one = torch.abs(value_at_one - target) <= tolerance

        # For strict Jensen-interior targets, convexity and the zero-mean
        # residual make F(s)=E||m+s r|| non-decreasing for s>=0.  The reverse
        # triangle inequality provides a finite upper bracket.
        strict_solve = strict_target & ~close_at_one
        needs_scale_up = strict_solve & (value_at_one < target)
        upper_bound = (target + mean_norm) / torch.clamp(
            residual_mean_norm, min=activity_epsilon
        )
        upper_bound = torch.maximum(
            one,
            upper_bound * (1.0 + relative_tolerance) + absolute_tolerance,
        )
        low = torch.where(needs_scale_up, one, zero)
        high = torch.where(needs_scale_up, upper_bound, one)
        for _ in range(maximum_iterations):
            midpoint = 0.5 * (low + high)
            midpoint_value = _mean_cycle_magnitude(
                tangent_mean, tangent_residual, midpoint, torch
            )
            below = midpoint_value < target
            low = torch.where(strict_solve & below, midpoint, low)
            high = torch.where(strict_solve & ~below, midpoint, high)
        strict_scale = 0.5 * (low + high)

        # At a=||m||, F may have a plateau: a purely collinear pulsatile
        # magnitude residual can preserve both moments for a range of scales.
        # Select the feasible root closest to one rather than collapse to zero.
        boundary_solve = ~strict_target & ~close_at_one
        boundary_low = zero
        boundary_high = one
        for _ in range(maximum_iterations):
            midpoint = 0.5 * (boundary_low + boundary_high)
            midpoint_value = _mean_cycle_magnitude(
                tangent_mean, tangent_residual, midpoint, torch
            )
            acceptable = midpoint_value <= target + tolerance
            boundary_low = torch.where(
                boundary_solve & acceptable, midpoint, boundary_low
            )
            boundary_high = torch.where(
                boundary_solve & ~acceptable, midpoint, boundary_high
            )

        located_scale = torch.where(
            close_at_one,
            one,
            torch.where(strict_target, strict_scale, boundary_low),
        )

    located_field = tangent_mean.unsqueeze(0) + tangent_residual * located_scale.unsqueeze(
        0
    ).unsqueeze(-1)
    located_norm = torch.linalg.vector_norm(located_field, dim=-1)
    located_magnitude = located_norm.mean(dim=0)
    root_derivative = torch.mean(
        torch.sum(located_field * tangent_residual, dim=-1)
        / torch.clamp(located_norm, min=activity_epsilon),
        dim=0,
    )
    _require(
        not bool((strict_target & (root_derivative <= activity_epsilon)).any().item()),
        "ill_conditioned_strict_root",
    )
    safe_derivative = torch.where(
        strict_target,
        root_derivative.detach(),
        torch.ones_like(root_derivative),
    )
    implicit_scale = located_scale - (located_magnitude - target) / safe_derivative
    # The closest-root map can be set-valued at the Jensen boundary and has no
    # unique implicit derivative.  Keep that selected scale detached.
    scale = torch.where(strict_target, implicit_scale, located_scale)
    field = tangent_mean.unsqueeze(0) + tangent_residual * scale.unsqueeze(0).unsqueeze(-1)
    achieved_mean = field.mean(dim=0)
    achieved_mean_magnitude = torch.linalg.vector_norm(field, dim=-1).mean(dim=0)
    achieved_normal_component = torch.abs(
        torch.sum(field * unit_normals.unsqueeze(0), dim=-1)
    )
    moment_error = torch.abs(achieved_mean_magnitude - target)
    _require(_finite(field, torch) and _finite(scale, torch), "output_nonfinite")
    _require(bool((moment_error <= 4.0 * tolerance).all().item()), "root_tolerance")

    return {
        "field": field,
        "scale": scale,
        "tangent_mean_vector": tangent_mean,
        "target_mean_magnitude": target,
        "centred_tangent_residual": tangent_residual,
        "achieved_mean_vector": achieved_mean,
        "achieved_mean_magnitude": achieved_mean_magnitude,
        "maximum_absolute_normal_component": achieved_normal_component.max(),
        "absolute_moment_error": moment_error,
        "strict_root_derivative": root_derivative,
        "strict_jensen_interior": strict_target,
        "raw_scale_preserved": close_at_one,
        "boundary_scale_gradient_detached": ~strict_target,
        "correction_applied": torch.abs(scale - one) > relative_tolerance,
    }
