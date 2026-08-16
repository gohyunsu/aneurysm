"""Prospective, non-executable D6 train-field admission utilities.

D6 is materially different from the closed transport-era cycle-functional P0.
It is conditional on the D5 geometry-component split and may inspect only the
406 private training cases.  The registered file remains non-executable until
a separate human activation is recorded in a fresh selected contract.

The pure functions in this module make the future audit testable without
opening any dataset field.  They decode the release with the exact official
``std + 1e-5`` rule and evaluate the surface-vector and cycle-moment
quantities that a later moment-constrained periodic decoder would require.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


class D6ContractError(RuntimeError):
    """Raised when the prospective D6 scope or evidence boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D6ContractError(reason)


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version")
        == "aurora.aneug_processed_v4_d6_train_field_audit.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_train_only_field_admission_d6_v1",
        "protocol_id",
    )
    _require(contract.get("status") == "registered_not_activated", "status")
    authority = contract["authority"]
    _require(authority["d5_pass_permits_registration"] is True, "d5_registration")
    _require(authority["field_execution_requires_separate_human_activation"] is True, "activation_rule")
    _require(authority["human_activation_recorded"] is False, "activation_state")

    source = contract["source"]
    _require(
        source["dataset_revision"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "dataset_revision",
    )
    _require(
        source["code_revision"]
        == "4a090a0f12538deef6fcea88b81afe78ce38152e",
        "code_revision",
    )
    _require(source["transient"]["bytes"] == 23_744_862_051, "transient_bytes")
    _require(
        source["transient"]["sha256"]
        == "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        "transient_sha256",
    )
    _require(source["steady"]["bytes"] == 9_632_510_050, "steady_bytes")
    _require(
        source["steady"]["sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "steady_sha256",
    )
    _require(
        source["d5_public_result_sha256"]
        == "3545831b50c1fa5b6ada5e2d29c06c25f04c6e02a34845a7a4d147b56b3f3eee",
        "d5_public_result",
    )
    _require(
        source["d5_private_manifest_sha256"]
        == "0f95cf303fa63b58c049e722864389c1432460686e335d20402b677c368181d6",
        "d5_private_manifest",
    )
    _require(
        source["d5_train_split_sha256"]
        == "df583f3553ce4efcf0588da5bdc029921025648c1981eba3a85fe3841d2bf26e",
        "d5_train_split",
    )

    d5 = contract["closed_d5_boundary"]
    _require((d5["attempts_used"], d5["attempt_limit"]) == (1, 1), "d5_attempts")
    _require(d5["gate_pass"] is True and d5["rerun_or_repair"] is False, "d5_closed_pass")
    _require(
        (d5["train_components"], d5["validation_components"], d5["outer_test_components"])
        == (406, 51, 51),
        "d5_split_counts",
    )
    _require(d5["scientific_verdict"] is None, "d5_scientific_verdict")

    scope = contract["read_scope"]
    _require(scope["private_split"] == "d5_train_components_only", "train_scope")
    _require(
        (
            scope["expected_train_cases"],
            scope["expected_timesteps"],
            scope["expected_nodes"],
            scope["expected_channels"],
        )
        == (406, 80, 13_902, 9),
        "expected_shape",
    )
    _require(
        scope["expected_labels"]
        == [
            "x",
            "y",
            "z",
            "x_normal",
            "y_normal",
            "z_normal",
            "wss_x",
            "wss_y",
            "wss_z",
        ],
        "expected_labels",
    )
    for key in (
        "read_validation_tensor_values",
        "read_outer_test_tensor_values",
        "read_auxiliary_tensor_values",
        "fit_model",
        "select_architecture",
        "use_gpu",
    ):
        _require(scope[key] is False, key)

    decoder = contract["physical_decoder"]
    _require(decoder["formula"] == "physical=normalized*(std+1e-5)+mean", "decoder_formula")
    _require(decoder["epsilon"] == 0.00001, "decoder_epsilon")
    _require(decoder["legacy_cycle_helper_epsilon_for_sensitivity_only"] == 0.000001, "legacy_epsilon")
    _require(decoder["steady_norm_is_release_decoding_metadata"] is True, "decoder_metadata")
    _require(decoder["future_model_normalization_must_be_recomputed_from_d5_train_only"] is True, "train_norm")

    checks = contract["gate"]["checks"]
    _require(contract["gate"]["all_checks_required"] is True, "all_checks")
    _require(checks["maximum_static_normalized_abs_error"] == 0.000001, "static_tolerance")
    _require(checks["maximum_roundtrip_normalized_abs_error"] == 0.00001, "roundtrip_tolerance")
    _require((checks["normal_norm_minimum"], checks["normal_norm_maximum"]) == (0.5, 1.5), "normal_bounds")
    _require(checks["minimum_nondegenerate_face_fraction_per_case"] == 0.999, "face_fraction")
    _require(checks["minimum_global_p05_absolute_mesh_stored_normal_cosine"] == 0.9, "normal_cosine")
    _require(checks["tangency_mask_minimum_fraction_of_case_p99_wss_magnitude"] == 0.01, "tangency_mask")
    _require(checks["maximum_global_median_normal_component_ratio"] == 0.05, "tangency_median")
    _require(checks["maximum_global_p95_normal_component_ratio"] == 0.25, "tangency_p95")
    _require(checks["minimum_cases_with_nonzero_temporal_residual_fraction"] == 1.0, "dynamic_cases")
    _require(checks["minimum_nodes_with_positive_tawss_fraction"] == 0.99, "positive_tawss")
    _require(checks["maximum_relative_Jensen_violation"] == 0.000001, "jensen")
    _require(contract["gate"]["histogram_bins"] == 10_000, "histogram_bins")

    execution = contract["execution_if_activated"]
    _require(execution["server"] == "introai9" and execution["scheduler"] == "PBS", "server")
    _require(execution["queue"] == "coss_agpu", "queue")
    _require((execution["ncpus"], execution["memory_gb"], execution["ngpus"]) == (4, 64, 0), "resources")
    _require(execution["maximum_pbs_attempts"] == 1, "attempt_budget")
    _require(execution["rerun_after_any_outcome"] is False, "rerun")
    _require(execution["login_node_gpu_allowed"] is False, "login_node_gpu")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")

    authorization = contract["authorization"]
    _require(authorization["register_d6"] is True, "register_d6")
    for key in (
        "execute_d6_now",
        "read_train_field_values_now",
        "read_validation_or_outer_field_values",
        "gpu_training",
        "paper_result_or_claim",
    ):
        _require(authorization[key] is False, key)


def assert_execution_authorized(contract: Mapping[str, Any]) -> None:
    """Fail closed: this registration cannot execute or be mutated in place."""

    validate_contract(contract)
    raise D6ContractError("d6_not_activated_requires_fresh_human_selected_contract")


def canonical_case_digest(case_ids: Sequence[str]) -> str:
    """Match the D5 private split digest without revealing identifiers."""

    payload = json.dumps(sorted(str(item) for item in case_ids), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def flatten_private_components(components: Sequence[Mapping[str, Any]]) -> list[str]:
    case_ids: list[str] = []
    for component in components:
        members = component.get("case_ids")
        _require(isinstance(members, Sequence) and not isinstance(members, (str, bytes)), "component_case_ids")
        _require(int(component.get("case_count", -1)) == len(members), "component_case_count")
        case_ids.extend(str(item) for item in members)
    _require(all(case_ids) and len(case_ids) == len(set(case_ids)), "component_case_id_integrity")
    return case_ids


def decode_release_channels(normalized: Any, mean: Any, std: Any, torch: Any, *, epsilon: float = 1e-5) -> Any:
    """Invert the exact transient normalization in official ``loaders.py``."""

    _require(normalized.shape[-1] == mean.numel() == std.numel(), "decoder_width")
    _require(bool(torch.isfinite(mean).all().item()), "decoder_mean_nonfinite")
    _require(bool(torch.isfinite(std).all().item()), "decoder_std_nonfinite")
    return normalized * (std.reshape(*([1] * (normalized.ndim - 1)), -1) + epsilon) + mean.reshape(
        *([1] * (normalized.ndim - 1)), -1
    )


def cycle_moments(wss: Any, torch: Any) -> dict[str, Any]:
    """Compute unclipped physical cycle moments for one ``[T,N,3]`` field."""

    _require(wss.ndim == 3 and int(wss.shape[-1]) == 3, "wss_shape")
    _require(bool(torch.isfinite(wss).all().item()), "wss_nonfinite")
    mean_vector = wss.mean(dim=0)
    magnitude = torch.linalg.vector_norm(wss, dim=-1)
    mean_magnitude = magnitude.mean(dim=0)
    mean_vector_magnitude = torch.linalg.vector_norm(mean_vector, dim=-1)
    positive = mean_magnitude > 0
    osi = torch.full_like(mean_magnitude, float("nan"))
    osi[positive] = 0.5 * (
        1.0 - mean_vector_magnitude[positive] / mean_magnitude[positive]
    )
    residual = wss - mean_vector.unsqueeze(0)
    residual_rms = torch.sqrt(torch.mean(torch.sum(residual * residual, dim=-1), dim=0))
    return {
        "mean_vector": mean_vector,
        "mean_magnitude": mean_magnitude,
        "mean_vector_magnitude": mean_vector_magnitude,
        "osi_unclipped": osi,
        "residual": residual,
        "residual_rms": residual_rms,
        "positive_tawss": positive,
    }


def area_weighted_vertex_normals(coordinates: Any, faces: Any, torch: Any) -> tuple[Any, Any]:
    """Return oriented area-weighted vertex normals and twice-face areas."""

    _require(coordinates.ndim == 2 and int(coordinates.shape[1]) == 3, "coordinate_shape")
    _require(faces.ndim == 2 and int(faces.shape[1]) == 3, "face_shape")
    _require(int(faces.min().item()) >= 0 and int(faces.max().item()) < int(coordinates.shape[0]), "face_range")
    triangle = coordinates[faces.to(dtype=torch.int64)]
    cross = torch.linalg.cross(triangle[:, 1] - triangle[:, 0], triangle[:, 2] - triangle[:, 0], dim=-1)
    twice_area = torch.linalg.vector_norm(cross, dim=-1)
    vertex = torch.zeros_like(coordinates)
    for corner in range(3):
        vertex.index_add_(0, faces[:, corner].to(dtype=torch.int64), cross)
    norms = torch.linalg.vector_norm(vertex, dim=-1, keepdim=True)
    unit = vertex / torch.clamp(norms, min=torch.finfo(vertex.dtype).tiny)
    return unit, twice_area


def inspect_case_tensor(
    tensor: Any,
    labels: Sequence[str],
    mean: Any,
    std: Any,
    faces: Any,
    torch: Any,
    *,
    decoder_epsilon: float = 1e-5,
    legacy_epsilon: float = 1e-6,
    tangency_mask_fraction: float = 0.01,
) -> dict[str, Any]:
    """Compute one case's method-free diagnostics without fitting anything."""

    required = [
        "x",
        "y",
        "z",
        "x_normal",
        "y_normal",
        "z_normal",
        "wss_x",
        "wss_y",
        "wss_z",
    ]
    _require(list(labels) == required, "case_labels")
    _require(tensor.ndim == 3 and int(tensor.shape[2]) == 9, "case_tensor_shape")
    normalized = tensor.detach().to(device="cpu", dtype=torch.float64)
    _require(bool(torch.isfinite(normalized).all().item()), "case_tensor_nonfinite")
    mean64 = mean.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    std64 = std.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    physical = decode_release_channels(normalized, mean64, std64, torch, epsilon=decoder_epsilon)
    roundtrip = (physical - mean64.reshape(1, 1, -1)) / (
        std64.reshape(1, 1, -1) + decoder_epsilon
    )
    static_error = float((normalized[..., :6] - normalized[:1, :, :6]).abs().max().item())
    roundtrip_error = float((roundtrip - normalized).abs().max().item())

    coordinates = physical[0, :, :3]
    normals = physical[..., 3:6]
    wss = physical[..., 6:9]
    normal_norm = torch.linalg.vector_norm(normals, dim=-1)
    moments = cycle_moments(wss, torch)
    magnitude = torch.linalg.vector_norm(wss, dim=-1)
    p99 = torch.quantile(magnitude.reshape(-1), 0.99)
    tangent_mask = (magnitude >= tangency_mask_fraction * p99) & (normal_norm > 0)
    ratio = torch.abs(torch.sum(wss * normals, dim=-1)) / torch.clamp(
        magnitude * normal_norm, min=torch.finfo(torch.float64).tiny
    )
    tangent_ratio = ratio[tangent_mask]

    mesh_normals, twice_area = area_weighted_vertex_normals(coordinates, faces, torch)
    stored = normals[0]
    stored_norm = torch.linalg.vector_norm(stored, dim=-1)
    mesh_norm = torch.linalg.vector_norm(mesh_normals, dim=-1)
    mesh_mask = (stored_norm > 0) & (mesh_norm > 0)
    normal_cosine = torch.abs(torch.sum(stored * mesh_normals, dim=-1)) / torch.clamp(
        stored_norm * mesh_norm, min=torch.finfo(torch.float64).tiny
    )
    normal_cosine = normal_cosine[mesh_mask]

    a = moments["mean_magnitude"]
    m_norm = moments["mean_vector_magnitude"]
    positive = moments["positive_tawss"]
    relative_jensen = torch.zeros_like(a)
    relative_jensen[positive] = torch.clamp(m_norm[positive] - a[positive], min=0) / a[positive]
    relative_residual = torch.zeros_like(a)
    relative_residual[positive] = moments["residual_rms"][positive] / a[positive]
    rrt_ratio = torch.ones_like(a)
    rrt_ratio[positive] = m_norm[positive] / a[positive]

    legacy = normalized[..., 6:9] * (std64[6:9].reshape(1, 1, 3) + legacy_epsilon) + mean64[6:9].reshape(1, 1, 3)
    decoder_difference = torch.linalg.vector_norm(wss - legacy, dim=-1)
    decoder_relative = decoder_difference / torch.clamp(
        magnitude, min=torch.finfo(torch.float64).tiny
    )

    return {
        "static_max_abs": static_error,
        "roundtrip_max_abs": roundtrip_error,
        "normal_norm_min": float(normal_norm.min().item()),
        "normal_norm_max": float(normal_norm.max().item()),
        "face_nondegenerate_fraction": float((twice_area > 0).to(torch.float64).mean().item()),
        "normal_cosine": normal_cosine,
        "tangent_ratio": tangent_ratio,
        "temporal_residual_nonzero": bool((moments["residual_rms"] > 0).any().item()),
        "positive_tawss_count": int(positive.sum().item()),
        "node_count": int(a.numel()),
        "tawss": a,
        "osi": moments["osi_unclipped"][positive],
        "rrt_denominator_ratio": rrt_ratio[positive],
        "relative_residual": relative_residual[positive],
        "relative_jensen_violation": relative_jensen,
        "decoder_epsilon_relative_difference": decoder_relative[torch.isfinite(decoder_relative)],
    }


def approximate_histogram_quantile(histogram: Sequence[int], q: float, low: float, high: float) -> float:
    """Deterministic midpoint quantile for prospectively fixed equal-width bins."""

    _require(0.0 <= q <= 1.0 and high > low, "histogram_quantile_arguments")
    total = sum(int(value) for value in histogram)
    _require(total > 0, "empty_histogram")
    target = max(1, math.ceil(q * total))
    cumulative = 0
    for index, value in enumerate(histogram):
        cumulative += int(value)
        if cumulative >= target:
            return low + (index + 0.5) * (high - low) / len(histogram)
    return high
