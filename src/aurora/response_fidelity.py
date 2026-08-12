"""Reference metrics for multi-condition haemodynamic response fidelity.

This module contains evaluation primitives, not a model.  They operate on one
case with aligned conditions and never infer clinical meaning from simulated
velocity fields.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


class ResponseFidelityError(ValueError):
    """Raised when a response-fidelity contract or tensor is invalid."""


def _numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional local dependency
        raise ResponseFidelityError("Response metrics require numpy.") from exc
    return np


def load_p0_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "aurora.aneumo_response_fidelity_p0.v1":
        raise ResponseFidelityError("Unexpected response-fidelity P0 schema.")
    if payload.get("status") != (
        "registered_non_executable_pending_external_service_change_and_exact_private_cache_path"
    ):
        raise ResponseFidelityError("The P0 status must remain fail-closed.")
    source = payload["source"]
    execution = payload["execution"]
    if source.get("allowed_split") != "train":
        raise ResponseFidelityError("P0 may read train fields only.")
    if source.get("pressure_read_allowed") is not False:
        raise ResponseFidelityError("Pressure is outside the registered target.")
    if source.get("validation_or_test_field_read_allowed") is not False:
        raise ResponseFidelityError("Validation/test field reads are forbidden.")
    if source.get("exact_private_cache_path") is not None:
        raise ResponseFidelityError("The current config cannot invent a private path.")
    if source.get("external_service_state_changed_since_incomplete_inventory") is not False:
        raise ResponseFidelityError("No external service change has been observed.")
    if execution.get("server") != "introai9" or execution.get("pbs_only") is not True:
        raise ResponseFidelityError("Scientific execution must remain introai9 PBS-only.")
    if execution.get("gpu") != 0 or execution.get("junjinyong_allowed") is not False:
        raise ResponseFidelityError("P0 is CPU-only and may never use junjinyong.")
    if any(execution.get(key) is not False for key in ("executable", "submitted")):
        raise ResponseFidelityError("The current P0 is not executable or submitted.")
    for key in ("cache_sha256", "staging_config_sha256", "historical_scaling_result_sha256"):
        value = str(source.get(key, ""))
        if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
            raise ResponseFidelityError(f"Invalid pinned SHA-256: {key}.")
    return payload


def validate_case(
    flows: Any,
    coordinates: Any,
    velocity: Any,
    *,
    anchor_flow: float,
) -> tuple[Any, Any, Any, int]:
    """Validate and normalize one aligned multi-flow case."""

    np = _numpy()
    q = np.asarray(flows, dtype=np.float64)
    xyz = np.asarray(coordinates, dtype=np.float64)
    vel = np.asarray(velocity, dtype=np.float64)
    if q.ndim != 1 or q.size < 4 or not np.all(np.diff(q) > 0):
        raise ResponseFidelityError("Flows must be a strictly increasing 1D grid.")
    if xyz.ndim != 2 or xyz.shape[1] != 3:
        raise ResponseFidelityError("Coordinates must have shape [nodes, 3].")
    if vel.shape != (q.size, xyz.shape[0], 3):
        raise ResponseFidelityError("Velocity must have shape [flows, nodes, 3].")
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(xyz)) or not np.all(np.isfinite(vel)):
        raise ResponseFidelityError("Flows, coordinates and velocity must be finite.")
    matches = np.flatnonzero(np.isclose(q, float(anchor_flow), rtol=0.0, atol=1e-12))
    if matches.size != 1:
        raise ResponseFidelityError("The anchor flow must occur exactly once.")
    if float(np.linalg.norm(vel[int(matches[0])])) <= 1e-30:
        raise ResponseFidelityError("The anchor velocity field has zero norm.")
    return q, xyz, vel, int(matches[0])


def coordinate_hash_partition(coordinates: Any) -> Any:
    """Return a platform-independent two-way partition of aligned nodes."""

    np = _numpy()
    xyz = np.asarray(coordinates, dtype="<f8")
    if xyz.ndim != 2 or xyz.shape[1] != 3 or not np.all(np.isfinite(xyz)):
        raise ResponseFidelityError("Finite [nodes, 3] coordinates are required.")
    labels = np.empty(xyz.shape[0], dtype=np.int8)
    for index, row in enumerate(xyz):
        labels[index] = hashlib.sha256(row.tobytes(order="C")).digest()[0] & 1
    if np.unique(labels).size != 2:
        raise ResponseFidelityError("Coordinate hash did not create two non-empty halves.")
    return labels


def discrete_tangent(flows: Any, fields: Any) -> Any:
    """First derivative on a nonuniform flow grid using ``numpy.gradient``."""

    np = _numpy()
    q = np.asarray(flows, dtype=np.float64)
    values = np.asarray(fields, dtype=np.float64)
    if values.shape[0] != q.size or q.size < 3 or not np.all(np.diff(q) > 0):
        raise ResponseFidelityError("Invalid flow grid or field leading dimension.")
    return np.gradient(values, q, axis=0, edge_order=2)


def discrete_curvature(flows: Any, fields: Any) -> Any:
    """Second derivative on the registered nonuniform flow grid."""

    return discrete_tangent(flows, discrete_tangent(flows, fields))


def relative_l2(reference: Any, prediction: Any) -> float:
    np = _numpy()
    truth = np.asarray(reference, dtype=np.float64)
    estimate = np.asarray(prediction, dtype=np.float64)
    if truth.shape != estimate.shape or not np.all(np.isfinite(truth)) or not np.all(np.isfinite(estimate)):
        raise ResponseFidelityError("Relative-L2 inputs must be finite and shape-matched.")
    denominator = float(np.linalg.norm(truth))
    if denominator <= 1e-30:
        raise ResponseFidelityError("Relative-L2 reference has zero norm.")
    return float(np.linalg.norm(estimate - truth) / denominator)


def response_metrics(
    flows: Any,
    reference: Any,
    prediction: Any,
    *,
    anchor_index: int,
) -> dict[str, float]:
    """Compute field, response, tangent, curvature, gain and direction errors."""

    np = _numpy()
    q = np.asarray(flows, dtype=np.float64)
    truth = np.asarray(reference, dtype=np.float64)
    estimate = np.asarray(prediction, dtype=np.float64)
    if truth.shape != estimate.shape or truth.ndim != 3 or truth.shape[0] != q.size:
        raise ResponseFidelityError("Expected matched [flows, nodes, 3] velocity arrays.")
    if not 0 <= int(anchor_index) < q.size:
        raise ResponseFidelityError("Anchor index is out of bounds.")
    truth_response = truth - truth[int(anchor_index)][None, :, :]
    estimated_response = estimate - estimate[int(anchor_index)][None, :, :]
    keep = np.arange(q.size) != int(anchor_index)
    truth_flat = truth_response[keep].reshape(-1)
    estimate_flat = estimated_response[keep].reshape(-1)
    direction_denominator = float(np.linalg.norm(truth_flat) * np.linalg.norm(estimate_flat))
    if direction_denominator <= 1e-30:
        raise ResponseFidelityError("Response-direction metric has a zero-norm field.")
    truth_gain = np.linalg.norm(truth.reshape(q.size, -1), axis=1)
    estimate_gain = np.linalg.norm(estimate.reshape(q.size, -1), axis=1)
    anchor_gain = float(truth_gain[int(anchor_index)])
    return {
        "field_relative_l2": relative_l2(truth[keep], estimate[keep]),
        "paired_response_relative_l2": relative_l2(
            truth_response[keep], estimated_response[keep]
        ),
        "discrete_tangent_relative_l2": relative_l2(
            discrete_tangent(q, truth), discrete_tangent(q, estimate)
        ),
        "discrete_curvature_relative_l2": relative_l2(
            discrete_curvature(q, truth), discrete_curvature(q, estimate)
        ),
        "gain_absolute_error": float(
            np.mean(np.abs(estimate_gain / anchor_gain - truth_gain / anchor_gain))
        ),
        "direction_cosine_error": float(
            1.0 - np.dot(truth_flat, estimate_flat) / direction_denominator
        ),
    }


def leave_one_interior_flow_error(flows: Any, fields: Any) -> float:
    """Median relative error of linear interpolation at interior flow values."""

    np = _numpy()
    q = np.asarray(flows, dtype=np.float64)
    values = np.asarray(fields, dtype=np.float64)
    if values.shape[0] != q.size or q.size < 4:
        raise ResponseFidelityError("Invalid flow-grid interpolation input.")
    errors = []
    for index in range(1, q.size - 1):
        weight = float((q[index] - q[index - 1]) / (q[index + 1] - q[index - 1]))
        estimate = (1.0 - weight) * values[index - 1] + weight * values[index + 1]
        errors.append(relative_l2(values[index], estimate))
    return float(np.median(np.asarray(errors, dtype=np.float64)))
