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


def triangle_lumped_vertex_areas(
    vertices: Any,
    faces: Any,
    torch: Any,
    *,
    area_epsilon: float = 1e-15,
) -> dict[str, Any]:
    """Compute one-third triangle-area weights without repairing the mesh."""

    _require(vertices.ndim == 2 and int(vertices.shape[1]) == 3, "vertex_shape")
    _require(vertices.dtype in (torch.float32, torch.float64), "vertex_dtype")
    _require(faces.ndim == 2 and int(faces.shape[1]) == 3, "face_shape")
    _require(faces.dtype in (torch.int32, torch.int64), "face_dtype")
    _require(int(faces.shape[0]) >= 1, "face_count")
    _require(area_epsilon > 0, "area_epsilon")
    _require(_finite(vertices, torch) and _finite(faces, torch), "mesh_nonfinite")
    integer_faces = faces.to(dtype=torch.int64, device=vertices.device)
    _require(
        int(integer_faces.min().item()) >= 0
        and int(integer_faces.max().item()) < int(vertices.shape[0]),
        "face_range",
    )

    repeated = (
        (integer_faces[:, 0] == integer_faces[:, 1])
        | (integer_faces[:, 1] == integer_faces[:, 2])
        | (integer_faces[:, 0] == integer_faces[:, 2])
    )
    triangles = vertices[integer_faces]
    cross = torch.linalg.cross(
        triangles[:, 1] - triangles[:, 0],
        triangles[:, 2] - triangles[:, 0],
        dim=-1,
    )
    face_areas = 0.5 * torch.linalg.vector_norm(cross, dim=-1)
    nondegenerate = (~repeated) & (face_areas > area_epsilon)
    retained_face_areas = torch.where(
        nondegenerate,
        face_areas,
        torch.zeros_like(face_areas),
    )
    vertex_areas = torch.zeros(
        int(vertices.shape[0]),
        dtype=vertices.dtype,
        device=vertices.device,
    )
    for corner in range(3):
        vertex_areas.index_add_(
            0,
            integer_faces[:, corner],
            retained_face_areas / 3.0,
        )
    total_area = vertex_areas.sum()
    _require(bool((total_area > area_epsilon).item()), "zero_retained_mesh_area")
    return {
        "vertex_areas": vertex_areas,
        "normalized_vertex_areas": vertex_areas / total_area,
        "face_areas": face_areas,
        "nondegenerate_face_mask": nondegenerate,
        "nondegenerate_face_fraction": nondegenerate.to(vertices.dtype).mean(),
        "positive_vertex_area_mask": vertex_areas > area_epsilon,
        "total_retained_area": total_area,
    }


def _weighted_relative_l2(
    reference: Any,
    prediction: Any,
    weights: Any,
    torch: Any,
    *,
    numerical_epsilon: float,
) -> Any:
    squared_error = (prediction - reference).square()
    squared_reference = reference.square()
    while weights.ndim < squared_error.ndim:
        weights = weights.unsqueeze(-1)
    numerator = torch.sum(weights * squared_error)
    denominator = torch.sum(weights * squared_reference)
    _require(bool((denominator > numerical_epsilon).item()), "relative_l2_denominator")
    return torch.sqrt(numerator / denominator)


def _masked_weighted_mean(
    values: Any,
    weights: Any,
    mask: Any,
    torch: Any,
    *,
    reason: str,
    numerical_epsilon: float,
) -> tuple[Any, Any]:
    support = weights * mask.to(dtype=weights.dtype)
    support_weight = support.sum()
    _require(bool((support_weight > numerical_epsilon).item()), reason)
    return torch.sum(support * values) / support_weight, support_weight


def paired_cycle_errors(
    reference: Any,
    prediction: Any,
    phase_weights: Any,
    vertex_areas: Any,
    torch: Any,
    *,
    reference_direction_floor: float,
    reference_tawss_floor: float,
    reference_mean_vector_floor: float,
    numerical_epsilon: float = 1e-12,
) -> dict[str, Any]:
    """Return one case's paired, mesh-area-weighted sufficient metrics.

    All three physical floors are mandatory caller inputs.  This function does
    not estimate thresholds, aggregate cases, select models or infer an
    independent unit.  Invalid predictions are penalized on reference-defined
    support and their coverage is returned explicitly.
    """

    _require(tuple(reference.shape) == tuple(prediction.shape), "paired_shape")
    _require(reference.ndim == 3 and int(reference.shape[-1]) == 3, "paired_field_shape")
    _require(
        reference.dtype in (torch.float32, torch.float64)
        and prediction.dtype == reference.dtype,
        "paired_dtype",
    )
    _require(_finite(reference, torch) and _finite(prediction, torch), "paired_nonfinite")
    _require(
        vertex_areas.ndim == 1
        and int(vertex_areas.shape[0]) == int(reference.shape[1]),
        "vertex_area_shape",
    )
    _require(_finite(vertex_areas, torch), "vertex_area_nonfinite")
    _require(bool((vertex_areas >= 0).all().item()), "negative_vertex_area")
    _require(bool((vertex_areas.sum() > numerical_epsilon).item()), "zero_vertex_area")
    for value, reason in (
        (reference_direction_floor, "direction_floor"),
        (reference_tawss_floor, "tawss_floor"),
        (reference_mean_vector_floor, "mean_vector_floor"),
        (numerical_epsilon, "numerical_epsilon"),
    ):
        _require(value > 0, reason)

    reference_functionals = compute_cycle_functionals(
        reference,
        phase_weights,
        torch,
        activity_epsilon=numerical_epsilon,
    )
    prediction_functionals = compute_cycle_functionals(
        prediction,
        phase_weights,
        torch,
        activity_epsilon=numerical_epsilon,
    )
    node_weights = vertex_areas.to(dtype=reference.dtype, device=reference.device)
    node_weights = node_weights / node_weights.sum()
    time_weights = reference_functionals["normalized_phase_weights"]
    area_time_weights = time_weights.reshape(-1, 1) * node_weights.reshape(1, -1)

    field_relative_l2 = _weighted_relative_l2(
        reference,
        prediction,
        area_time_weights,
        torch,
        numerical_epsilon=numerical_epsilon,
    )
    mean_vector_relative_l2 = _weighted_relative_l2(
        reference_functionals["mean_vector"],
        prediction_functionals["mean_vector"],
        node_weights,
        torch,
        numerical_epsilon=numerical_epsilon,
    )
    tawss_relative_l2 = _weighted_relative_l2(
        reference_functionals["tawss"],
        prediction_functionals["tawss"],
        node_weights,
        torch,
        numerical_epsilon=numerical_epsilon,
    )

    reference_magnitude = torch.linalg.vector_norm(reference, dim=-1)
    prediction_magnitude = torch.linalg.vector_norm(prediction, dim=-1)
    direction_support = reference_magnitude >= reference_direction_floor
    prediction_direction_valid = prediction_magnitude > numerical_epsilon
    cosine = torch.sum(reference * prediction, dim=-1) / (
        torch.clamp(reference_magnitude, min=numerical_epsilon)
        * torch.clamp(prediction_magnitude, min=numerical_epsilon)
    )
    cosine = torch.clamp(cosine, min=-1.0, max=1.0)
    direction_penalty = torch.where(
        prediction_direction_valid,
        1.0 - cosine,
        torch.ones_like(cosine),
    )
    direction_cosine_error, direction_support_weight = _masked_weighted_mean(
        direction_penalty,
        area_time_weights,
        direction_support,
        torch,
        reason="empty_direction_support",
        numerical_epsilon=numerical_epsilon,
    )
    direction_prediction_coverage, _ = _masked_weighted_mean(
        prediction_direction_valid.to(reference.dtype),
        area_time_weights,
        direction_support,
        torch,
        reason="empty_direction_support",
        numerical_epsilon=numerical_epsilon,
    )

    osi_support = reference_functionals["tawss"] >= reference_tawss_floor
    prediction_osi_valid = prediction_functionals["osi_valid"]
    osi_absolute_error = torch.where(
        prediction_osi_valid,
        torch.abs(prediction_functionals["osi"] - reference_functionals["osi"]),
        torch.full_like(node_weights, 0.5),
    )
    osi_mae, osi_support_weight = _masked_weighted_mean(
        osi_absolute_error,
        node_weights,
        osi_support,
        torch,
        reason="empty_osi_support",
        numerical_epsilon=numerical_epsilon,
    )
    osi_prediction_coverage, _ = _masked_weighted_mean(
        prediction_osi_valid.to(reference.dtype),
        node_weights,
        osi_support,
        torch,
        reason="empty_osi_support",
        numerical_epsilon=numerical_epsilon,
    )

    reference_mean_magnitude = reference_functionals["mean_vector_magnitude"]
    prediction_mean_magnitude = prediction_functionals["mean_vector_magnitude"]
    rrt_support = reference_mean_magnitude >= reference_mean_vector_floor
    prediction_rrt_above_floor = prediction_mean_magnitude >= reference_mean_vector_floor
    log_rrt_error = torch.abs(
        torch.log(torch.clamp(prediction_mean_magnitude, min=numerical_epsilon))
        - torch.log(torch.clamp(reference_mean_magnitude, min=numerical_epsilon))
    )
    log_rrt_mae, rrt_support_weight = _masked_weighted_mean(
        log_rrt_error,
        node_weights,
        rrt_support,
        torch,
        reason="empty_rrt_support",
        numerical_epsilon=numerical_epsilon,
    )
    rrt_prediction_coverage, _ = _masked_weighted_mean(
        prediction_rrt_above_floor.to(reference.dtype),
        node_weights,
        rrt_support,
        torch,
        reason="empty_rrt_support",
        numerical_epsilon=numerical_epsilon,
    )

    return {
        "field_relative_l2": field_relative_l2,
        "mean_vector_relative_l2": mean_vector_relative_l2,
        "tawss_relative_l2": tawss_relative_l2,
        "direction_cosine_error_with_invalid_penalty": direction_cosine_error,
        "direction_reference_support_fraction": direction_support_weight,
        "direction_prediction_valid_fraction": direction_prediction_coverage,
        "osi_mae_with_invalid_penalty": osi_mae,
        "osi_reference_support_fraction": osi_support_weight,
        "osi_prediction_valid_fraction": osi_prediction_coverage,
        "log_rrt_mae": log_rrt_mae,
        "rrt_reference_support_fraction": rrt_support_weight,
        "rrt_prediction_above_floor_fraction": rrt_prediction_coverage,
    }
