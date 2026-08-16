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
from typing import Any, Iterable, Mapping, Sequence


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

    readiness = contract["implementation_readiness"]
    for key in (
        "pure_case_evaluator",
        "streaming_aggregate_gate",
        "private_train_statistics",
        "sealed_split_tensor_sentinel_test",
        "strict_public_json_test",
    ):
        _require(readiness[key] is True, key)
    for key in ("real_payload_read", "file_io_entry_point", "pbs_wrapper"):
        _require(readiness[key] is False, key)

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
        "mean_vector_magnitude": m_norm[positive],
        "rrt_denominator_ratio": rrt_ratio[positive],
        "relative_residual": relative_residual[positive],
        "relative_jensen_violation": relative_jensen,
        "decoder_epsilon_relative_difference": decoder_relative[torch.isfinite(decoder_relative)],
        "coordinate_count": int(coordinates.shape[0]),
        "coordinate_sum": coordinates.sum(dim=0),
        "coordinate_squared_sum": (coordinates * coordinates).sum(dim=0),
        "wss_count": int(wss.shape[0] * wss.shape[1]),
        "wss_sum": wss.sum(dim=(0, 1)),
        "wss_squared_sum": (wss * wss).sum(dim=(0, 1)),
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


def _optional_histogram_quantile(
    histogram: Sequence[int], q: float, low: float, high: float
) -> float | None:
    if sum(int(value) for value in histogram) == 0:
        return None
    return approximate_histogram_quantile(histogram, q, low, high)


def validate_private_split_manifest(
    contract: Mapping[str, Any], manifest: Mapping[str, Any]
) -> dict[str, list[str]]:
    """Validate the exact D5 split structure and return private ID buckets."""

    validate_contract(contract)
    _require(
        manifest.get("schema_version")
        == "aurora.aneug_processed_v4_d5.private_grouping_manifest.v1",
        "private_manifest_schema",
    )
    _require(
        manifest.get("protocol_id") == "aneug_processed_v4_ghd_component_split_d5_v1",
        "private_manifest_protocol",
    )
    _require(manifest.get("split_frozen") is True, "private_manifest_not_frozen")
    _require(manifest.get("source_identity_reverified") is True, "private_manifest_source")
    buckets = {
        "train": flatten_private_components(manifest.get("train_components", [])),
        "validation": flatten_private_components(manifest.get("validation_components", [])),
        "outer_test": flatten_private_components(manifest.get("outer_test_components", [])),
        "auxiliary": flatten_private_components(manifest.get("auxiliary_components", [])),
    }
    expected = contract["closed_d5_boundary"]
    _require(len(buckets["train"]) == expected["train_components"], "private_train_count")
    _require(len(buckets["validation"]) == expected["validation_components"], "private_validation_count")
    _require(len(buckets["outer_test"]) == expected["outer_test_components"], "private_outer_count")
    all_ids: set[str] = set()
    for name, case_ids in buckets.items():
        overlap = all_ids.intersection(case_ids)
        _require(not overlap, f"private_split_overlap:{name}")
        all_ids.update(case_ids)
    _require(
        canonical_case_digest(buckets["train"])
        == contract["source"]["d5_train_split_sha256"],
        "private_train_digest",
    )
    return buckets


def _histogram_update(
    histogram: list[int], values: Any, low: float, high: float, torch: Any
) -> int:
    finite = values.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    finite = finite[torch.isfinite(finite)]
    if int(finite.numel()) == 0:
        return 0
    finite = torch.clamp(finite, min=low, max=high)
    counts = torch.histc(finite, bins=len(histogram), min=low, max=high)
    for index, value in enumerate(counts.to(dtype=torch.int64).tolist()):
        histogram[index] += int(value)
    return int(finite.numel())


def _moments_from_sums(count: int, total: Any, squared: Any, torch: Any) -> dict[str, list[float]]:
    _require(count > 0, "empty_training_statistics")
    mean = total / count
    variance = torch.clamp(squared / count - mean * mean, min=0)
    std = torch.sqrt(variance)
    return {
        "mean": [float(value) for value in mean.tolist()],
        "std_population": [float(value) for value in std.tolist()],
    }


def _scalar_moments(count: int, total: float, squared: float) -> dict[str, float]:
    _require(count > 0, "empty_scalar_statistics")
    mean = total / count
    variance = max(0.0, squared / count - mean * mean)
    return {"mean": mean, "std_population": math.sqrt(variance)}


def aggregate_case_diagnostics(
    contract: Mapping[str, Any],
    diagnostics: Iterable[Mapping[str, Any]],
    torch: Any,
    *,
    source_identity_reverified: bool,
    private_manifest_reverified: bool,
    train_scope_enforced: bool,
    normalization_metadata_valid: bool,
    shared_faces_valid: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Stream per-case diagnostics into deidentified public and private outputs."""

    validate_contract(contract)
    checks = contract["gate"]["checks"]
    bins = int(contract["gate"]["histogram_bins"])
    tangent_hist = [0] * bins
    normal_cosine_hist = [0] * bins
    osi_hist = [0] * bins
    rrt_ratio_hist = [0] * bins
    residual_hist = [0] * bins
    decoder_difference_hist = [0] * bins

    case_count = 0
    dynamic_case_count = 0
    static_max = 0.0
    roundtrip_max = 0.0
    normal_norm_min = math.inf
    normal_norm_max = -math.inf
    face_fraction_min = 1.0
    positive_tawss_count = 0
    node_count = 0
    endpoint_finite = True
    tawss_min = math.inf
    tawss_max = -math.inf
    osi_min = math.inf
    osi_max = -math.inf
    jensen_max = 0.0
    tangent_value_count = 0
    normal_cosine_value_count = 0
    rrt_near_zero_count = 0
    rrt_ratio_count = 0

    coordinate_count = 0
    coordinate_sum = torch.zeros(3, dtype=torch.float64)
    coordinate_squared = torch.zeros(3, dtype=torch.float64)
    wss_count = 0
    wss_sum = torch.zeros(3, dtype=torch.float64)
    wss_squared = torch.zeros(3, dtype=torch.float64)
    endpoint_stats = {
        key: {"count": 0, "sum": 0.0, "squared": 0.0}
        for key in ("tawss", "osi", "mean_vector_magnitude", "relative_residual")
    }

    for item in diagnostics:
        case_count += 1
        static_max = max(static_max, float(item["static_max_abs"]))
        roundtrip_max = max(roundtrip_max, float(item["roundtrip_max_abs"]))
        normal_norm_min = min(normal_norm_min, float(item["normal_norm_min"]))
        normal_norm_max = max(normal_norm_max, float(item["normal_norm_max"]))
        face_fraction_min = min(face_fraction_min, float(item["face_nondegenerate_fraction"]))
        dynamic_case_count += int(bool(item["temporal_residual_nonzero"]))

        tangent_value_count += _histogram_update(
            tangent_hist, item["tangent_ratio"], 0.0, 1.0, torch
        )
        normal_cosine_value_count += _histogram_update(
            normal_cosine_hist, item["normal_cosine"], 0.0, 1.0, torch
        )
        _histogram_update(osi_hist, item["osi"], 0.0, 0.5, torch)
        _histogram_update(
            rrt_ratio_hist, item["rrt_denominator_ratio"], 0.0, 1.0, torch
        )
        _histogram_update(residual_hist, item["relative_residual"], 0.0, 4.0, torch)
        _histogram_update(
            decoder_difference_hist,
            item["decoder_epsilon_relative_difference"],
            0.0,
            0.01,
            torch,
        )

        tawss = item["tawss"].detach().to(device="cpu", dtype=torch.float64)
        osi = item["osi"].detach().to(device="cpu", dtype=torch.float64)
        mean_vector_magnitude = item["mean_vector_magnitude"].detach().to(
            device="cpu", dtype=torch.float64
        )
        relative_residual = item["relative_residual"].detach().to(
            device="cpu", dtype=torch.float64
        )
        endpoint_finite = endpoint_finite and all(
            bool(torch.isfinite(values).all().item())
            for values in (tawss, osi, mean_vector_magnitude, relative_residual)
        )
        endpoint_finite = endpoint_finite and bool(
            ((osi >= -1e-12) & (osi <= 0.5 + 1e-12)).all().item()
        )
        if int(tawss.numel()):
            tawss_min = min(tawss_min, float(tawss.min().item()))
            tawss_max = max(tawss_max, float(tawss.max().item()))
        if int(osi.numel()):
            osi_min = min(osi_min, float(osi.min().item()))
            osi_max = max(osi_max, float(osi.max().item()))
        positive_tawss_count += int(item["positive_tawss_count"])
        node_count += int(item["node_count"])
        jensen_max = max(
            jensen_max,
            float(item["relative_jensen_violation"].max().item()),
        )
        rrt_ratio = item["rrt_denominator_ratio"]
        rrt_near_zero_count += int((rrt_ratio < 0.001).sum().item())
        rrt_ratio_count += int(rrt_ratio.numel())

        coordinate_count += int(item["coordinate_count"])
        coordinate_sum += item["coordinate_sum"].to(dtype=torch.float64)
        coordinate_squared += item["coordinate_squared_sum"].to(dtype=torch.float64)
        wss_count += int(item["wss_count"])
        wss_sum += item["wss_sum"].to(dtype=torch.float64)
        wss_squared += item["wss_squared_sum"].to(dtype=torch.float64)
        for name, values in (
            ("tawss", tawss),
            ("osi", osi),
            ("mean_vector_magnitude", mean_vector_magnitude),
            ("relative_residual", relative_residual),
        ):
            stats = endpoint_stats[name]
            stats["count"] += int(values.numel())
            stats["sum"] += float(values.sum().item())
            stats["squared"] += float((values * values).sum().item())

    expected_cases = int(contract["read_scope"]["expected_train_cases"])
    tangent_median = (
        approximate_histogram_quantile(tangent_hist, 0.5, 0.0, 1.0)
        if tangent_value_count
        else math.inf
    )
    tangent_p95 = (
        approximate_histogram_quantile(tangent_hist, 0.95, 0.0, 1.0)
        if tangent_value_count
        else math.inf
    )
    normal_cosine_p05 = (
        approximate_histogram_quantile(normal_cosine_hist, 0.05, 0.0, 1.0)
        if normal_cosine_value_count
        else -math.inf
    )
    positive_tawss_fraction = positive_tawss_count / node_count if node_count else 0.0
    dynamic_case_fraction = dynamic_case_count / case_count if case_count else 0.0
    endpoints_nonconstant = (
        endpoint_finite
        and math.isfinite(tawss_min)
        and math.isfinite(osi_min)
        and tawss_max > tawss_min
        and osi_max > osi_min
    )

    check_results = {
        "source_sizes_and_sha256_exact": bool(source_identity_reverified),
        "d5_private_manifest_and_train_digest_exact": bool(private_manifest_reverified),
        "only_d5_train_tensor_values_read": bool(train_scope_enforced),
        "normalization_mean_std_finite_and_positive_required_scales": bool(
            normalization_metadata_valid
        ),
        "static_geometry_and_normals": static_max
        <= float(checks["maximum_static_normalized_abs_error"]),
        "normalization_roundtrip": roundtrip_max
        <= float(checks["maximum_roundtrip_normalized_abs_error"]),
        "normal_norm_bounds": normal_norm_min >= float(checks["normal_norm_minimum"])
        and normal_norm_max <= float(checks["normal_norm_maximum"]),
        "shared_faces_valid_nonrepeated_triangles": bool(shared_faces_valid),
        "nondegenerate_face_fraction": face_fraction_min
        >= float(checks["minimum_nondegenerate_face_fraction_per_case"]),
        "mesh_stored_normal_agreement": normal_cosine_p05
        >= float(checks["minimum_global_p05_absolute_mesh_stored_normal_cosine"]),
        "wss_tangency": tangent_median
        <= float(checks["maximum_global_median_normal_component_ratio"])
        and tangent_p95 <= float(checks["maximum_global_p95_normal_component_ratio"]),
        "all_cases_temporally_nonzero": dynamic_case_fraction
        >= float(checks["minimum_cases_with_nonzero_temporal_residual_fraction"]),
        "positive_tawss_support": positive_tawss_fraction
        >= float(checks["minimum_nodes_with_positive_tawss_fraction"]),
        "jensen_moment_cone": jensen_max
        <= float(checks["maximum_relative_Jensen_violation"]),
        "cycle_endpoints_finite_and_nonconstant": endpoints_nonconstant,
        "expected_train_case_count": case_count == expected_cases,
    }
    gate_reasons = sorted(key for key, passed in check_results.items() if not passed)
    gate_pass = not gate_reasons
    osi_q05 = _optional_histogram_quantile(osi_hist, 0.05, 0.0, 0.5)
    osi_q50 = _optional_histogram_quantile(osi_hist, 0.5, 0.0, 0.5)
    osi_q95 = _optional_histogram_quantile(osi_hist, 0.95, 0.0, 0.5)
    residual_q50 = _optional_histogram_quantile(residual_hist, 0.5, 0.0, 4.0)
    decoder_difference_q95 = _optional_histogram_quantile(
        decoder_difference_hist, 0.95, 0.0, 0.01
    )
    public_result = {
        "schema_version": "aurora.aneug_processed_v4_d6.public_result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "completed_passed" if gate_pass else "completed_failed",
        "scientific_gate_evaluated": True,
        "scientific_verdict": "pass" if gate_pass else "fail",
        "gate_pass": gate_pass,
        "gate_reasons": gate_reasons,
        "train_case_count": case_count,
        "validation_case_field_count_read": 0,
        "outer_test_case_field_count_read": 0,
        "auxiliary_case_field_count_read": 0,
        "timesteps": int(contract["read_scope"]["expected_timesteps"]),
        "nodes_per_case": int(contract["read_scope"]["expected_nodes"]),
        "static_max_abs": static_max,
        "roundtrip_max_abs": roundtrip_max,
        "normal_norm_min": normal_norm_min if math.isfinite(normal_norm_min) else None,
        "normal_norm_max": normal_norm_max if math.isfinite(normal_norm_max) else None,
        "minimum_case_nondegenerate_face_fraction": face_fraction_min,
        "global_mesh_stored_normal_abs_cosine_p05_histogram": (
            normal_cosine_p05 if math.isfinite(normal_cosine_p05) else None
        ),
        "global_normal_component_ratio_median_histogram": (
            tangent_median if math.isfinite(tangent_median) else None
        ),
        "global_normal_component_ratio_p95_histogram": (
            tangent_p95 if math.isfinite(tangent_p95) else None
        ),
        "dynamic_case_fraction": dynamic_case_fraction,
        "positive_tawss_node_fraction": positive_tawss_fraction,
        "maximum_relative_jensen_violation": jensen_max,
        "rrt_denominator_ratio_below_0p001_fraction": (
            rrt_near_zero_count / rrt_ratio_count if rrt_ratio_count else None
        ),
        "osi_q05_histogram": osi_q05,
        "osi_q50_histogram": osi_q50,
        "osi_q95_histogram": osi_q95,
        "relative_residual_q50_histogram": residual_q50,
        "decoder_epsilon_relative_difference_q95_histogram": decoder_difference_q95,
        "histogram_bins": bins,
        "check_results": check_results,
        "private_case_ids_published": False,
        "private_normalization_values_published": False,
        "model_fitted_or_selected": False,
        "gpu_used": False,
        "paper_result_or_claim_authorized": False,
    }
    private_statistics = {
        "schema_version": "aurora.aneug_processed_v4_d6.private_train_statistics.v1",
        "protocol_id": contract["protocol_id"],
        "train_split_sha256": contract["source"]["d5_train_split_sha256"],
        "train_case_count": case_count,
        "coordinate_physical": _moments_from_sums(
            coordinate_count, coordinate_sum, coordinate_squared, torch
        ),
        "wss_physical": _moments_from_sums(wss_count, wss_sum, wss_squared, torch),
        "cycle_endpoints": {
            name: (
                _scalar_moments(
                    int(values["count"]),
                    float(values["sum"]),
                    float(values["squared"]),
                )
                if int(values["count"]) > 0
                else None
            )
            for name, values in endpoint_stats.items()
        },
        "model_normalization_source": "d5_train_physical_values_only",
        "validation_outer_or_auxiliary_statistics_included": False,
        "case_ids_included": False,
    }
    return public_result, private_statistics


def stream_selected_case_diagnostics(
    case_by_id: Mapping[str, Mapping[str, Any]],
    train_ids: Sequence[str],
    sealed_ids: Sequence[str],
    labels: Sequence[str],
    mean: Any,
    std: Any,
    faces: Any,
    torch: Any,
    *,
    expected_shape: Sequence[int],
    decoder_epsilon: float,
    legacy_epsilon: float,
    tangency_mask_fraction: float,
) -> Iterable[Mapping[str, Any]]:
    """Yield diagnostics while making sealed-case tensor access impossible by construction."""

    train = [str(item) for item in train_ids]
    sealed = {str(item) for item in sealed_ids}
    _require(len(train) == len(set(train)) and all(train), "stream_train_id_integrity")
    _require(not set(train).intersection(sealed), "stream_train_sealed_overlap")
    _require(set(train).issubset(case_by_id), "stream_missing_train_case")
    for case_id in train:
        case = case_by_id[case_id]
        _require([str(item) for item in case.get("labels", [])] == list(labels), "case_labels")
        tensor = case.get("tensor")
        _require(hasattr(tensor, "shape") and list(tensor.shape) == list(expected_shape), "case_tensor_shape")
        yield inspect_case_tensor(
            tensor,
            labels,
            mean,
            std,
            faces,
            torch,
            decoder_epsilon=decoder_epsilon,
            legacy_epsilon=legacy_epsilon,
            tangency_mask_fraction=tangency_mask_fraction,
        )


def audit_loaded_training_payload(
    contract: Mapping[str, Any],
    steady: Mapping[str, Any],
    transient: Mapping[str, Any],
    private_manifest: Mapping[str, Any],
    torch: Any,
    *,
    source_identity_reverified: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Audit loaded objects while indexing tensor values for D5-train IDs only."""

    validate_contract(contract)
    buckets = validate_private_split_manifest(contract, private_manifest)
    _require(isinstance(steady, Mapping), "steady_mapping")
    _require({"label", "tensor_norm"}.issubset(steady), "steady_keys")
    labels = [str(item) for item in steady["label"]]
    _require(labels == contract["read_scope"]["expected_labels"], "steady_labels")
    norm = steady["tensor_norm"]
    _require(isinstance(norm, Mapping) and {"mean", "std"}.issubset(norm), "tensor_norm")
    mean = norm["mean"].detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    std = norm["std"].detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    normalization_valid = (
        int(mean.numel()) == int(std.numel()) == len(labels)
        and bool(torch.isfinite(mean).all().item())
        and bool(torch.isfinite(std).all().item())
        and bool((std > 0).all().item())
    )
    _require(normalization_valid, "normalization_metadata")

    _require(isinstance(transient, Mapping), "transient_mapping")
    _require({"registered_data_list", "mesh_data"}.issubset(transient), "transient_keys")
    cases = transient["registered_data_list"]
    mesh = transient["mesh_data"]
    _require(isinstance(cases, Sequence) and not isinstance(cases, (str, bytes)), "case_sequence")
    _require(isinstance(mesh, Mapping) and "faces_list" in mesh, "mesh_faces")
    faces_list = mesh["faces_list"]
    _require(isinstance(faces_list, Sequence) and faces_list, "faces_list")
    faces = faces_list[0].detach().to(device="cpu")
    expected_nodes = int(contract["read_scope"]["expected_nodes"])
    shared_faces_valid = (
        faces.ndim == 2
        and int(faces.shape[1]) == 3
        and not bool((faces[:, 0] == faces[:, 1]).any().item())
        and not bool((faces[:, 1] == faces[:, 2]).any().item())
        and not bool((faces[:, 0] == faces[:, 2]).any().item())
        and int(faces.min().item()) >= 0
        and int(faces.max().item()) < expected_nodes
    )
    _require(shared_faces_valid, "shared_faces_invalid")

    case_by_id: dict[str, Mapping[str, Any]] = {}
    for case in cases:
        _require(isinstance(case, Mapping), "case_mapping")
        case_id = str(case.get("case", ""))
        _require(case_id and case_id not in case_by_id, "case_id_integrity")
        case_by_id[case_id] = case
    train_ids = buckets["train"]
    _require(set(train_ids).issubset(case_by_id), "missing_train_case")
    sealed_ids = set(buckets["validation"] + buckets["outer_test"] + buckets["auxiliary"])
    _require(not set(train_ids).intersection(sealed_ids), "train_sealed_overlap")

    expected_timesteps = int(contract["read_scope"]["expected_timesteps"])
    expected_channels = int(contract["read_scope"]["expected_channels"])

    stream = stream_selected_case_diagnostics(
        case_by_id,
        train_ids,
        sorted(sealed_ids),
        labels,
        mean,
        std,
        faces,
        torch,
        expected_shape=[expected_timesteps, expected_nodes, expected_channels],
        decoder_epsilon=float(contract["physical_decoder"]["epsilon"]),
        legacy_epsilon=float(
            contract["physical_decoder"]["legacy_cycle_helper_epsilon_for_sensitivity_only"]
        ),
        tangency_mask_fraction=float(
            contract["gate"]["checks"][
                "tangency_mask_minimum_fraction_of_case_p99_wss_magnitude"
            ]
        ),
    )

    public_result, private_statistics = aggregate_case_diagnostics(
        contract,
        stream,
        torch,
        source_identity_reverified=source_identity_reverified,
        private_manifest_reverified=True,
        train_scope_enforced=True,
        normalization_metadata_valid=normalization_valid,
        shared_faces_valid=shared_faces_valid,
    )
    serialized_public = json.dumps(public_result, ensure_ascii=False, sort_keys=True)
    for case_id in case_by_id:
        _require(json.dumps(case_id, ensure_ascii=False) not in serialized_public, "case_id_leaked_public")
    for private_key in ("coordinate_physical", "wss_physical", "train_split_sha256"):
        _require(private_key not in public_result, "normalization_value_leaked_public")
    return public_result, private_statistics
