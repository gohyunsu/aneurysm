"""Train-only physical audit for the release-aligned AneuG-Flow cohort.

The audit binds the completed 584/73/73 split, decodes only the 584 training
fields with the official steady normalizer and derives the statistics required
by every later baseline.  Validation, locked-test and processed-only tensors
are present only as sealed identifiers and are never indexed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_release_730_split import _canonical_digest


class Release730TrainAuditError(RuntimeError):
    """Raised when source, split or train-only invariants are violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730TrainAuditError(reason)


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
    return digest.hexdigest()


def _ordered_digest(values: Sequence[str]) -> str:
    payload = json.dumps([str(value) for value in values], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version") == "aurora.aneug_release_730_train_audit.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id") == "aneug_release_730_train_only_physical_audit_v1",
        "protocol_id",
    )
    _require(config.get("status") == "prepared_for_private_activation_after_quality", "status")
    source = config["source"]
    _require(source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36", "dataset_revision")
    _require(source["code_revision"] == "4a090a0f12538deef6fcea88b81afe78ce38152e", "code_revision")
    _require(source["processed_v5_bytes"] == 33_233_856_917, "processed_v5_bytes")
    _require(source["processed_v5_sha256"] == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae", "processed_v5_sha256")
    _require(source["steady_norm_bytes"] == 9_632_510_050, "steady_norm_bytes")
    _require(source["steady_norm_sha256"] == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f", "steady_norm_sha256")
    _require(source["split_public_result_sha256"] == "4fa3be7c217c3a84b86f477c90112377fb913f6b0b47b829d684b270555bf991", "public_split_sha256")
    _require(source["split_private_manifest_sha256"] == "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f", "private_split_sha256")

    split = config["split"]
    _require((split["train_cases"], split["validation_cases"], split["test_cases"]) == (584, 73, 73), "split_counts")
    _require(split["all_phases_follow_case"] is True and split["test_opened"] is False, "split_boundary")
    scope = config["read_scope"]
    _require(scope["allowed_field_partition"] == "train_only", "read_scope")
    _require(scope["read_train_field_values"] is True, "train_read")
    for key in ("read_validation_field_values", "read_test_field_values", "read_processed_only_extra_field_values"):
        _require(scope[key] is False, key)
    _require((scope["expected_timesteps"], scope["expected_nodes"], scope["expected_channels"]) == (80, 13_902, 9), "tensor_shape")
    _require(scope["expected_labels"] == ["x", "y", "z", "x_normal", "y_normal", "z_normal", "wss_x", "wss_y", "wss_z"], "labels")
    decoder = config["physical_decoder"]
    _require(decoder["formula"] == "physical=normalized*(std+1e-5)+mean", "decoder_formula")
    _require(decoder["epsilon"] == 0.00001, "decoder_epsilon")
    _require(decoder["model_statistics_source"] == "584_training_cases_only", "model_statistics_source")
    execution = config["execution"]
    _require(execution["server"] == "introai9" and execution["excluded_server"] == "junjinyong", "server_scope")
    _require((execution["ncpus"], execution["memory_gb"], execution["ngpus"]) == (4, 64, 0), "resources")
    _require(execution["diagnosed_infrastructure_or_implementation_retry_allowed"] is True, "retry_policy")
    _require(config["authorization"]["read_validation_or_test"] is False, "sealed_authority")
    _require(config["authorization"]["fit_model"] is False, "model_authority")


def _flatten_components(components: Sequence[Mapping[str, Any]]) -> list[str]:
    result: list[str] = []
    for component in components:
        members = [str(value) for value in component.get("case_ids", [])]
        _require(len(members) == int(component.get("case_count", -1)) > 0, "component_count")
        result.extend(members)
    _require(len(result) == len(set(result)), "duplicate_case_within_partition")
    return result


def index_case_records(cases: Sequence[Mapping[str, Any]]) -> tuple[list[str], dict[str, Mapping[str, Any]]]:
    """Index metadata without touching any case tensor value."""

    ordered: list[str] = []
    indexed: dict[str, Mapping[str, Any]] = {}
    for case in cases:
        case_id = str(case.get("case", ""))
        _require(case_id and case_id not in indexed, "case_identity")
        ordered.append(case_id)
        indexed[case_id] = case
    return ordered, indexed


def selected_training_records(
    case_by_id: Mapping[str, Mapping[str, Any]],
    train_ids: Sequence[str],
    sealed_ids: Sequence[str],
) -> Sequence[Mapping[str, Any]]:
    """Return only training records; sealed records are never indexed for tensors."""

    train = [str(value) for value in train_ids]
    sealed = {str(value) for value in sealed_ids}
    _require(len(train) == len(set(train)) and not set(train) & sealed, "train_sealed_boundary")
    _require(set(train).issubset(case_by_id), "missing_train_case")
    return [case_by_id[case_id] for case_id in train]


def validate_split_evidence(
    config: Mapping[str, Any], public: Mapping[str, Any], private: Mapping[str, Any]
) -> dict[str, list[str]]:
    _require(public.get("status") == "complete", "public_split_status")
    _require(public.get("registered_field_values_read") is False, "split_field_read")
    _require(public.get("test_opened") is False, "public_test_opened")
    _require(private.get("schema_version") == "aurora.aneug_release_730.private_split.v1", "private_split_schema")
    _require(private.get("registered_field_values_read") is False, "private_split_field_read")
    _require(private.get("test_opened") is False, "private_test_opened")
    _require(private.get("source_sha256") == config["source"]["processed_v5_sha256"], "private_source_sha256")
    _require(private.get("split_key_sha256") == config["split"]["split_key_sha256"], "split_key_sha256")
    buckets = {
        "train": _flatten_components(private.get("train_components", [])),
        "validation": _flatten_components(private.get("validation_components", [])),
        "test": _flatten_components(private.get("test_components", [])),
        "extra": [str(value) for value in private.get("processed_extra_case_ids", [])],
    }
    _require(tuple(len(buckets[name]) for name in ("train", "validation", "test", "extra")) == (584, 73, 73, 79), "private_split_counts")
    _require(len(set(buckets["train"] + buckets["validation"] + buckets["test"])) == 730, "release_union")
    _require(not set(buckets["train"]) & set(buckets["validation"]), "train_validation_overlap")
    _require(not set(buckets["train"]) & set(buckets["test"]), "train_test_overlap")
    _require(not set(buckets["validation"]) & set(buckets["test"]), "validation_test_overlap")
    for name in ("train", "validation", "test"):
        _require(_canonical_digest(buckets[name]) == config["split"][f"{name}_case_digest"], f"{name}_digest")
    _require(_canonical_digest(private.get("release_case_ids", [])) == public.get("release_case_id_sha256"), "release_digest")
    return buckets


def _moments(count: int, total: Any, squared: Any, torch: Any) -> dict[str, list[float]]:
    _require(count > 0, "empty_moments")
    mean = total / count
    variance = torch.clamp(squared / count - mean.square(), min=0)
    return {
        "mean": [float(value) for value in mean.tolist()],
        "std_population": [float(value) for value in torch.sqrt(variance).tolist()],
    }


def _scalar_summary(values: Sequence[float]) -> dict[str, float]:
    _require(bool(values) and all(math.isfinite(value) for value in values), "nonfinite_summary")
    ordered = sorted(float(value) for value in values)
    def q(fraction: float) -> float:
        position = fraction * (len(ordered) - 1)
        lower = int(math.floor(position))
        upper = int(math.ceil(position))
        weight = position - lower
        return ordered[lower] * (1.0 - weight) + ordered[upper] * weight
    mean = sum(ordered) / len(ordered)
    variance = sum((value - mean) ** 2 for value in ordered) / len(ordered)
    return {"min": ordered[0], "q05": q(0.05), "median": q(0.5), "q95": q(0.95), "max": ordered[-1], "mean": mean, "std_population": math.sqrt(variance)}


def _vertex_areas(coordinates: Any, faces: Any, torch: Any) -> tuple[Any, Any, Any]:
    triangle = coordinates[faces]
    cross = torch.linalg.cross(triangle[:, 1] - triangle[:, 0], triangle[:, 2] - triangle[:, 0], dim=-1)
    twice_area = torch.linalg.vector_norm(cross, dim=-1)
    areas = torch.zeros(coordinates.shape[0], dtype=coordinates.dtype)
    vertex_normal = torch.zeros_like(coordinates)
    for corner in range(3):
        areas.index_add_(0, faces[:, corner], twice_area / 6.0)
        vertex_normal.index_add_(0, faces[:, corner], cross)
    vertex_normal = vertex_normal / torch.clamp(torch.linalg.vector_norm(vertex_normal, dim=-1, keepdim=True), min=torch.finfo(coordinates.dtype).tiny)
    return areas, vertex_normal, twice_area


def audit_loaded_training_payload(
    config: Mapping[str, Any], steady: Mapping[str, Any], transient: Mapping[str, Any],
    public_split: Mapping[str, Any], private_split: Mapping[str, Any], torch: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Inspect training tensors while keeping validation/test tensors sealed."""

    validate_config(config)
    buckets = validate_split_evidence(config, public_split, private_split)
    labels = [str(value) for value in steady.get("label", [])]
    _require(labels == config["read_scope"]["expected_labels"], "steady_labels")
    norm = steady.get("tensor_norm")
    _require(isinstance(norm, Mapping) and {"mean", "std"}.issubset(norm), "steady_norm")
    mean = norm["mean"].detach().cpu().to(torch.float64).reshape(-1)
    std = norm["std"].detach().cpu().to(torch.float64).reshape(-1)
    _require(mean.numel() == std.numel() == 9, "steady_norm_width")
    _require(bool(torch.isfinite(mean).all().item()) and bool(torch.isfinite(std).all().item()) and bool((std > 0).all().item()), "steady_norm_finite_positive")

    _require(isinstance(transient, Mapping) and {"registered_data_list", "mesh_data"}.issubset(transient), "transient_schema")
    cases = transient["registered_data_list"]
    mesh = transient["mesh_data"]
    _require(len(cases) == 809 and len(mesh["cases"]) == 809, "processed_case_count")
    ordered_ids, case_by_id = index_case_records(cases)
    _require(ordered_ids == [str(value) for value in mesh["cases"]], "mesh_case_order")
    _require(set(buckets["train"] + buckets["validation"] + buckets["test"] + buckets["extra"]) == set(ordered_ids), "split_processed_union")

    faces = mesh["faces_list"][0].detach().cpu().to(torch.int64)
    expected_nodes = config["read_scope"]["expected_nodes"]
    faces_valid = faces.ndim == 2 and faces.shape[1] == 3 and int(faces.min()) >= 0 and int(faces.max()) < expected_nodes
    faces_valid = faces_valid and not bool(((faces[:, 0] == faces[:, 1]) | (faces[:, 1] == faces[:, 2]) | (faces[:, 0] == faces[:, 2])).any().item())
    _require(faces_valid, "shared_faces_invalid")

    train_indices = torch.tensor([ordered_ids.index(case_id) for case_id in buckets["train"]], dtype=torch.int64)
    ghd = mesh["ghd"].detach().cpu()
    _require(tuple(ghd.shape) == (809, 432), "ghd_shape")
    train_ghd = ghd.index_select(0, train_indices).to(torch.float64)
    _require(bool(torch.isfinite(train_ghd).all().item()), "train_ghd_nonfinite")

    coord_count = normal_count = wss_count = 0
    coord_sum = torch.zeros(3, dtype=torch.float64); coord_sq = coord_sum.clone()
    normal_sum = torch.zeros(3, dtype=torch.float64); normal_sq = normal_sum.clone()
    wss_sum = torch.zeros(3, dtype=torch.float64); wss_sq = wss_sum.clone()
    static_max = roundtrip_max = 0.0
    minimum_nondegenerate = 1.0
    normal_norm_min = math.inf; normal_norm_max = -math.inf
    descriptors: dict[str, list[float]] = {name: [] for name in (
        "mesh_normal_abs_cosine_p05", "wss_normal_ratio_median", "wss_normal_ratio_p95",
        "phase_boundary_relative_jump", "surface_area", "response_rms", "area_mean_tawss", "area_mean_osi",
    )}
    epsilon = float(config["physical_decoder"]["epsilon"])
    expected_shape = (config["read_scope"]["expected_timesteps"], expected_nodes, config["read_scope"]["expected_channels"])

    sealed_ids = buckets["validation"] + buckets["test"] + buckets["extra"]
    train_records = selected_training_records(case_by_id, buckets["train"], sealed_ids)
    for case_id, case in zip(buckets["train"], train_records):
        _require([str(value) for value in case.get("labels", [])] == labels, "case_labels")
        normalized = case["tensor"].detach().cpu().to(torch.float64)
        _require(tuple(normalized.shape) == expected_shape, "case_tensor_shape")
        _require(bool(torch.isfinite(normalized).all().item()), "case_tensor_nonfinite")
        physical = normalized * (std.reshape(1, 1, -1) + epsilon) + mean.reshape(1, 1, -1)
        roundtrip = (physical - mean.reshape(1, 1, -1)) / (std.reshape(1, 1, -1) + epsilon)
        static_max = max(static_max, float((normalized[..., :6] - normalized[:1, :, :6]).abs().max().item()))
        roundtrip_max = max(roundtrip_max, float((roundtrip - normalized).abs().max().item()))

        coordinates, normals, wss = physical[0, :, :3], physical[0, :, 3:6], physical[..., 6:9]
        areas, mesh_normals, twice_area = _vertex_areas(coordinates, faces, torch)
        minimum_nondegenerate = min(minimum_nondegenerate, float((twice_area > 0).to(torch.float64).mean().item()))
        area_sum = areas.sum()
        _require(bool(torch.isfinite(area_sum).item()) and float(area_sum) > 0, "surface_area")
        normal_norm = torch.linalg.vector_norm(normals, dim=-1)
        normal_norm_min = min(normal_norm_min, float(normal_norm.min().item())); normal_norm_max = max(normal_norm_max, float(normal_norm.max().item()))
        cosine = torch.abs(torch.sum(normals * mesh_normals, dim=-1)) / torch.clamp(normal_norm, min=torch.finfo(torch.float64).tiny)
        magnitude = torch.linalg.vector_norm(wss, dim=-1)
        ratio = torch.abs(torch.sum(wss * normals.reshape(1, expected_nodes, 3), dim=-1)) / torch.clamp(magnitude * normal_norm.reshape(1, expected_nodes), min=torch.finfo(torch.float64).tiny)
        mask = magnitude >= 0.01 * torch.quantile(magnitude.reshape(-1), 0.99)
        tangent = ratio[mask]
        _require(tangent.numel() > 0, "empty_tangency_support")
        energy = torch.sum(areas.reshape(1, -1) * magnitude.square()) / (80 * area_sum)
        boundary = torch.sum(areas * torch.sum((wss[0] - wss[-1]).square(), dim=-1)) / torch.clamp(torch.sum(areas.reshape(1, -1) * magnitude.square()) / 80, min=torch.finfo(torch.float64).tiny)
        tawss = magnitude.mean(dim=0)
        mean_vector_norm = torch.linalg.vector_norm(wss.mean(dim=0), dim=-1)
        positive = tawss > 0
        _require(bool(positive.any().item()), "empty_tawss_support")
        osi = 0.5 * (1.0 - mean_vector_norm[positive] / tawss[positive])
        _require(bool(torch.isfinite(osi).all().item()), "osi_nonfinite")
        descriptors["mesh_normal_abs_cosine_p05"].append(float(torch.quantile(cosine, 0.05).item()))
        descriptors["wss_normal_ratio_median"].append(float(torch.quantile(tangent, 0.5).item()))
        descriptors["wss_normal_ratio_p95"].append(float(torch.quantile(tangent, 0.95).item()))
        descriptors["phase_boundary_relative_jump"].append(float(torch.sqrt(torch.clamp(boundary, min=0)).item()))
        descriptors["surface_area"].append(float(area_sum.item()))
        descriptors["response_rms"].append(float(torch.sqrt(torch.clamp(energy, min=0)).item()))
        descriptors["area_mean_tawss"].append(float(torch.sum(areas * tawss).div(area_sum).item()))
        descriptors["area_mean_osi"].append(float(torch.sum(areas[positive] * osi).div(areas[positive].sum()).item()))

        coord_count += coordinates.shape[0]; coord_sum += coordinates.sum(0); coord_sq += coordinates.square().sum(0)
        normal_count += normals.shape[0]; normal_sum += normals.sum(0); normal_sq += normals.square().sum(0)
        wss_count += wss.shape[0] * wss.shape[1]; wss_sum += wss.sum((0, 1)); wss_sq += wss.square().sum((0, 1))

    checks = {
        "expected_train_case_count": len(buckets["train"]) == 584,
        "validation_field_reads_zero": True,
        "test_field_reads_zero": True,
        "processed_only_extra_field_reads_zero": True,
        "static_geometry_exact": static_max <= config["integrity_checks"]["maximum_static_normalized_abs_error"],
        "normalization_roundtrip": roundtrip_max <= config["integrity_checks"]["maximum_roundtrip_normalized_abs_error"],
        "shared_faces_valid": faces_valid,
        "all_faces_nondegenerate": minimum_nondegenerate == 1.0,
        "train_ghd_finite": True,
        "cycle_endpoints_finite": all(all(math.isfinite(value) for value in values) for values in descriptors.values()),
    }
    failures = sorted(key for key, passed in checks.items() if not passed)
    public_result = {
        "schema_version": "aurora.aneug_release_730_train_audit.public_result.v1",
        "status": "complete_passed" if not failures else "complete_failed_integrity",
        "integrity_pass": not failures,
        "integrity_failures": failures,
        "train_case_count": 584,
        "validation_field_case_count_read": 0,
        "test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "timesteps": 80,
        "nodes_per_case": 13_902,
        "static_normalized_max_abs": static_max,
        "roundtrip_normalized_max_abs": roundtrip_max,
        "minimum_case_nondegenerate_face_fraction": minimum_nondegenerate,
        "stored_normal_norm_min": normal_norm_min,
        "stored_normal_norm_max": normal_norm_max,
        "descriptive_case_distributions": {name: _scalar_summary(values) for name, values in descriptors.items()},
        "integrity_checks": checks,
        "descriptive_values_are_not_model_pass_thresholds": True,
        "model_fitted_or_selected": False,
        "gpu_used": False,
        "test_opened": False,
        "case_ids_public": False,
        "paper_performance_claim_authorized": False,
    }
    private_statistics = {
        "schema_version": "aurora.aneug_release_730_train_audit.private_statistics.v1",
        "train_case_count": 584,
        "train_case_digest": config["split"]["train_case_digest"],
        "loader_order_case_ids": buckets["train"],
        "loader_order_sha256": _ordered_digest(buckets["train"]),
        "coordinate_physical": _moments(coord_count, coord_sum, coord_sq, torch),
        "normal_physical": _moments(normal_count, normal_sum, normal_sq, torch),
        "wss_physical": _moments(wss_count, wss_sum, wss_sq, torch),
        "ghd": _moments(train_ghd.shape[0], train_ghd.sum(0), train_ghd.square().sum(0), torch),
        "response_rms": _scalar_summary(descriptors["response_rms"]),
        "release_decoder_mean": [float(value) for value in mean.tolist()],
        "release_decoder_std": [float(value) for value in std.tolist()],
        "validation_test_or_extra_statistics_included": False,
    }
    serialized = json.dumps(public_result, sort_keys=True)
    _require(not any(case_id in serialized for case_id in ordered_ids), "public_case_id_leak")
    return public_result, private_statistics


def _atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
    os.replace(temporary, target)


def run_audit(
    config_path: Path, transient_path: Path, steady_path: Path,
    public_split_path: Path, private_split_path: Path,
    public_result_path: Path, private_statistics_path: Path, torch: Any,
) -> dict[str, Any]:
    config = load_config(config_path); source = config["source"]
    for path, size, digest, label in (
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (steady_path, source["steady_norm_bytes"], source["steady_norm_sha256"], "steady"),
    ):
        _require(path.is_file() and path.stat().st_size == size, f"{label}_identity")
        _require(file_sha256(path) == digest, f"{label}_sha256")
    _require(file_sha256(public_split_path) == source["split_public_result_sha256"], "public_split_file")
    _require(file_sha256(private_split_path) == source["split_private_manifest_sha256"], "private_split_file")
    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    steady = safe_torch_load(steady_path, torch); transient = safe_torch_load(transient_path, torch)
    public, private = audit_loaded_training_payload(config, steady, transient, public_split, private_split, torch)
    public["processed_v5_sha256"] = source["processed_v5_sha256"]
    public["steady_norm_sha256"] = source["steady_norm_sha256"]
    public["split_public_result_sha256"] = source["split_public_result_sha256"]
    public["split_private_manifest_sha256"] = source["split_private_manifest_sha256"]
    _atomic_json(private_statistics_path, private); _atomic_json(public_result_path, public)
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--transient", type=Path, required=True)
    parser.add_argument("--steady", type=Path, required=True)
    parser.add_argument("--public-split", type=Path, required=True)
    parser.add_argument("--private-split", type=Path, required=True)
    parser.add_argument("--public-result", type=Path, required=True)
    parser.add_argument("--private-statistics", type=Path, required=True)
    arguments = parser.parse_args()
    import torch
    result = run_audit(arguments.config, arguments.transient, arguments.steady, arguments.public_split, arguments.private_split, arguments.public_result, arguments.private_statistics, torch)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
