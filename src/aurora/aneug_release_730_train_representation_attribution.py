"""Train-only attribution of cyclic jumps and registered-normal support."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_release_730_train_audit import (
    _ordered_digest,
    _vertex_areas,
    file_sha256,
    index_case_records,
    selected_training_records,
    validate_split_evidence,
)


class TrainRepresentationAttributionError(RuntimeError):
    """Raised when attribution identity or sealed-read boundaries fail."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise TrainRepresentationAttributionError(reason)


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_train_representation_attribution.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_train_only_periodicity_normal_attribution_v1",
        "protocol_id",
    )
    _require(config.get("status") == "prepared_for_private_activation_after_quality", "status")
    source = config["source"]
    _require(source["processed_v5_bytes"] == 33_233_856_917, "processed_v5_bytes")
    _require(source["processed_v5_sha256"] == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae", "processed_v5_sha256")
    _require(source["steady_norm_bytes"] == 9_632_510_050, "steady_norm_bytes")
    _require(source["steady_norm_sha256"] == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f", "steady_norm_sha256")
    _require(source["train_audit_public_result_sha256"] == "3c525820023a56862c6652441c5d00f43412d3c868840149e5f120b8ed2a9587", "train_audit_public")
    _require(source["train_audit_private_statistics_sha256"] == "ce1dd6d2852e290fbe187ac062af155f522cd4b8a82c1580b5430d15ed519385", "train_audit_private")
    _require(source["train_loader_order_sha256"] == "83d40e0579c0999fb380029d11811df835131b62e6bbd3557ad33254f22e6b8f", "loader_order")
    split = config["split"]
    _require((split["train_cases"], split["validation_cases"], split["test_cases"]) == (584, 73, 73), "split_counts")
    _require(split["test_opened"] is False, "test_opened")
    scope = config["read_scope"]
    _require(scope["allowed_field_partition"] == "train_only" and scope["read_train_field_values"] is True, "train_scope")
    for key in ("read_validation_field_values", "read_test_field_values", "read_processed_only_extra_field_values"):
        _require(scope[key] is False, key)
    _require((scope["expected_timesteps"], scope["expected_nodes"], scope["expected_channels"]) == (80, 13_902, 9), "shape")
    attribution = config["attribution"]
    _require(attribution["cyclic_transition_count"] == 80, "transition_count")
    _require(attribution["boundary_transition"] == "phase_79_to_phase_0", "boundary")
    _require(attribution["boundary_to_interior_ratio_report_levels"] == [2.0, 5.0, 10.0], "ratio_levels")
    _require(attribution["stored_normal_norm_report_levels"] == [0.001, 0.01, 0.1, 0.5], "normal_levels")
    _require(attribution["metrics_are_descriptive_not_gates"] is True, "descriptive")
    _require(attribution["automatic_architecture_selection"] is False, "automatic_selection")
    execution = config["execution"]
    _require(execution["server"] == "introai9" and execution["excluded_server"] == "junjinyong", "server")
    _require((execution["ncpus"], execution["memory_gb"], execution["ngpus"]) == (4, 64, 0), "resources")
    _require(execution["diagnosed_retry_under_fresh_run_id_allowed"] is True, "retry")
    authorization = config["authorization"]
    _require(authorization["read_validation_or_test"] is False, "sealed_authority")
    _require(authorization["fit_or_select_model"] is False and authorization["use_gpu"] is False, "model_gpu_authority")


def _summary(values: Sequence[float]) -> dict[str, float]:
    _require(bool(values) and all(math.isfinite(float(value)) for value in values), "summary_values")
    ordered = sorted(float(value) for value in values)

    def q(fraction: float) -> float:
        position = fraction * (len(ordered) - 1)
        lower, upper = int(math.floor(position)), int(math.ceil(position))
        weight = position - lower
        return ordered[lower] * (1 - weight) + ordered[upper] * weight
    mean = sum(ordered) / len(ordered)
    return {
        "min": ordered[0], "q05": q(0.05), "median": q(0.5),
        "q95": q(0.95), "max": ordered[-1], "mean": mean,
        "std_population": math.sqrt(sum((value - mean) ** 2 for value in ordered) / len(ordered)),
    }


def cyclic_case_metrics(
    wss: Any,
    coordinates: Any,
    stored_normals: Any,
    faces: Any,
    torch: Any,
    *,
    normal_epsilon: float,
    wss_support_fraction: float,
    normal_levels: Sequence[float],
) -> dict[str, Any]:
    """Return per-case periodicity and normal-support diagnostics."""

    _require(wss.ndim == 3 and wss.shape[-1] == 3, "wss_shape")
    _require(
        wss.shape[0] >= 3
        and coordinates.shape == stored_normals.shape == wss.shape[1:]
        and coordinates.shape[-1] == 3,
        "geometry_shape",
    )
    _require(bool(torch.isfinite(wss).all().item()), "wss_nonfinite")
    areas, mesh_normals, twice_area = _vertex_areas(coordinates, faces, torch)
    _require(bool((twice_area > 0).all().item()), "degenerate_face")
    area_sum = areas.sum()
    magnitude = torch.linalg.vector_norm(wss, dim=-1)
    response_energy = torch.sum(areas.reshape(1, -1) * magnitude.square()) / (wss.shape[0] * area_sum)
    response_rms = torch.sqrt(torch.clamp(response_energy, min=torch.finfo(wss.dtype).tiny))
    next_wss = torch.roll(wss, shifts=-1, dims=0)
    transition_absolute = torch.sqrt(
        torch.sum(areas.reshape(1, -1) * torch.sum((next_wss - wss).square(), dim=-1), dim=1) / area_sum
    )
    transition_relative = transition_absolute / response_rms
    boundary = transition_relative[-1]
    interior = transition_relative[:-1]
    interior_median = torch.quantile(interior, 0.5)
    boundary_ratio = boundary / torch.clamp(interior_median, min=torch.finfo(wss.dtype).tiny)
    boundary_percentile = torch.mean(
        (transition_relative <= boundary).to(torch.float64)
    )

    stored_norm = torch.linalg.vector_norm(stored_normals, dim=-1)
    valid_normal = stored_norm > normal_epsilon
    _require(bool(valid_normal.any().item()), "no_valid_stored_normal")
    direction_cosine = torch.abs(
        torch.sum(
            stored_normals[valid_normal] * mesh_normals[valid_normal], dim=-1
        )
    ) / stored_norm[valid_normal]
    support = magnitude >= wss_support_fraction * torch.quantile(
        magnitude.reshape(-1), 0.99
    )
    mesh_ratio = torch.abs(
        torch.sum(wss * mesh_normals.reshape(1, -1, 3), dim=-1)
    ) / torch.clamp(magnitude, min=torch.finfo(wss.dtype).tiny)
    stored_ratio = torch.abs(
        torch.sum(wss * stored_normals.reshape(1, -1, 3), dim=-1)
    ) / torch.clamp(
        magnitude * stored_norm.reshape(1, -1), min=torch.finfo(wss.dtype).tiny
    )
    stored_ratio_values = stored_ratio[support & valid_normal.reshape(1, -1)]
    mesh_ratio_values = mesh_ratio[support]
    _require(stored_ratio_values.numel() > 0 and mesh_ratio_values.numel() > 0, "empty_wss_support")

    result: dict[str, Any] = {
        "response_rms": float(response_rms.item()),
        "boundary_jump_absolute": float(transition_absolute[-1].item()),
        "boundary_jump_relative": float(boundary.item()),
        "interior_jump_relative_median": float(interior_median.item()),
        "interior_jump_relative_q95": float(torch.quantile(interior, 0.95).item()),
        "interior_jump_relative_max": float(interior.max().item()),
        "boundary_to_interior_median_ratio": float(boundary_ratio.item()),
        "boundary_transition_percentile": float(boundary_percentile.item()),
        "maximum_transition_start_phase": int(torch.argmax(transition_relative).item()),
        "stored_normal_norm_min": float(stored_norm.min().item()),
        "stored_normal_norm_q01": float(torch.quantile(stored_norm, 0.01).item()),
        "stored_normal_norm_q05": float(torch.quantile(stored_norm, 0.05).item()),
        "stored_normal_norm_median": float(torch.quantile(stored_norm, 0.5).item()),
        "stored_mesh_normal_abs_cosine_q05": float(torch.quantile(direction_cosine, 0.05).item()),
        "stored_wss_normal_ratio_median": float(torch.quantile(stored_ratio_values, 0.5).item()),
        "stored_wss_normal_ratio_q95": float(torch.quantile(stored_ratio_values, 0.95).item()),
        "mesh_wss_normal_ratio_median": float(torch.quantile(mesh_ratio_values, 0.5).item()),
        "mesh_wss_normal_ratio_q95": float(torch.quantile(mesh_ratio_values, 0.95).item()),
    }
    for level in normal_levels:
        result[f"stored_normal_fraction_below_{level:g}"] = float((stored_norm < level).to(torch.float64).mean().item())
    _require(all(math.isfinite(float(value)) for value in result.values()), "nonfinite_case_metric")
    return result


def aggregate_metrics(
    config: Mapping[str, Any], per_case: Sequence[Mapping[str, Any]], all_case_ids: Sequence[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(len(per_case) == 584, "per_case_count")
    metric_names = [key for key in per_case[0] if key != "case_id"]
    distributions = {
        name: _summary([float(case[name]) for case in per_case])
        for name in metric_names
        if name != "maximum_transition_start_phase"
    }
    levels = config["attribution"]["boundary_to_interior_ratio_report_levels"]
    ratio_values = [float(case["boundary_to_interior_median_ratio"]) for case in per_case]
    boundary_start_count = sum(int(case["maximum_transition_start_phase"] == 79) for case in per_case)
    public = {
        "schema_version": "aurora.aneug_release_730_train_representation_attribution.public_result.v1",
        "status": "complete_descriptive",
        "train_case_count": 584,
        "validation_field_case_count_read": 0,
        "test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "distributions": distributions,
        "boundary_to_interior_ratio_counts": {
            f"at_least_{level:g}": sum(value >= level for value in ratio_values)
            for level in levels
        },
        "boundary_is_largest_transition_case_count": boundary_start_count,
        "metrics_are_descriptive_not_gates": True,
        "automatic_architecture_selection": False,
        "model_fitted_or_selected": False,
        "gpu_used": False,
        "test_opened": False,
        "case_ids_public": False,
        "scientific_performance_verdict": None,
    }
    private = {
        "schema_version": "aurora.aneug_release_730_train_representation_attribution.private_result.v1",
        "train_loader_order_sha256": config["source"]["train_loader_order_sha256"],
        "per_case": list(per_case),
        "validation_test_or_extra_fields_included": False,
    }
    serialized = json.dumps(public, sort_keys=True)
    _require(not any(str(case_id) in serialized for case_id in all_case_ids), "case_id_leak")
    return public, private


def _atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
    os.replace(temporary, target)


def run_attribution(
    config_path: Path,
    transient_path: Path,
    steady_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    train_audit_public_path: Path,
    train_audit_private_path: Path,
    public_result_path: Path,
    private_result_path: Path,
    torch: Any,
) -> dict[str, Any]:
    config = load_config(config_path)
    source = config["source"]
    for path, size, digest, label in (
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (steady_path, source["steady_norm_bytes"], source["steady_norm_sha256"], "steady"),
    ):
        _require(path.is_file() and path.stat().st_size == size, f"{label}_identity")
        _require(file_sha256(path) == digest, f"{label}_sha256")
    for path, digest, label in (
        (public_split_path, source["split_public_result_sha256"], "public_split"),
        (private_split_path, source["split_private_manifest_sha256"], "private_split"),
        (train_audit_public_path, source["train_audit_public_result_sha256"], "audit_public"),
        (train_audit_private_path, source["train_audit_private_statistics_sha256"], "audit_private"),
    ):
        _require(file_sha256(path) == digest, f"{label}_sha256")
    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    audit_public = json.loads(train_audit_public_path.read_text(encoding="utf-8"))
    audit_private = json.loads(train_audit_private_path.read_text(encoding="utf-8"))
    _require(audit_public.get("integrity_pass") is True and audit_public.get("test_opened") is False, "audit_public_status")
    _require(audit_private.get("validation_test_or_extra_statistics_included") is False, "audit_private_scope")
    loader_order = [str(value) for value in audit_private.get("loader_order_case_ids", [])]
    _require(len(loader_order) == 584 and _ordered_digest(loader_order) == source["train_loader_order_sha256"], "loader_order")

    steady = safe_torch_load(steady_path, torch)
    transient = safe_torch_load(transient_path, torch)
    buckets = validate_split_evidence(config, public_split, private_split)
    _require(set(loader_order) == set(buckets["train"]), "loader_train_set")
    labels = [str(value) for value in steady["label"]]
    _require(labels == ["x", "y", "z", "x_normal", "y_normal", "z_normal", "wss_x", "wss_y", "wss_z"], "labels")
    mean = steady["tensor_norm"]["mean"].detach().cpu().to(torch.float64).reshape(1, 1, -1)
    std = steady["tensor_norm"]["std"].detach().cpu().to(torch.float64).reshape(1, 1, -1)
    ordered_ids, case_by_id = index_case_records(transient["registered_data_list"])
    _require(ordered_ids == [str(value) for value in transient["mesh_data"]["cases"]], "mesh_case_order")
    sealed = buckets["validation"] + buckets["test"] + buckets["extra"]
    records = selected_training_records(case_by_id, loader_order, sealed)
    faces = transient["mesh_data"]["faces_list"][0].detach().cpu().to(torch.int64)
    attribution = config["attribution"]
    per_case: list[dict[str, Any]] = []
    for index, (case_id, case) in enumerate(zip(loader_order, records), start=1):
        _require([str(value) for value in case.get("labels", [])] == labels, "case_labels")
        normalized = case["tensor"].detach().cpu().to(torch.float64)
        _require(tuple(normalized.shape) == (80, 13_902, 9), "case_shape")
        physical = normalized * (std + 1e-5) + mean
        metrics = cyclic_case_metrics(
            physical[..., 6:9], physical[0, :, :3], physical[0, :, 3:6], faces, torch,
            normal_epsilon=float(attribution["normal_direction_epsilon"]),
            wss_support_fraction=float(attribution["wss_magnitude_support_fraction_of_case_p99"]),
            normal_levels=attribution["stored_normal_norm_report_levels"],
        )
        per_case.append({"case_id": case_id, **metrics})
        if index % 50 == 0 or index == 584:
            print(json.dumps({"stage": "case_progress", "cases_complete": index}), flush=True)
    public, private = aggregate_metrics(config, per_case, ordered_ids)
    public["config_sha256"] = file_sha256(config_path)
    public["split_public_result_sha256"] = source["split_public_result_sha256"]
    public["split_private_manifest_sha256"] = source["split_private_manifest_sha256"]
    public["train_audit_public_result_sha256"] = source[
        "train_audit_public_result_sha256"
    ]
    public["train_audit_private_statistics_sha256"] = source[
        "train_audit_private_statistics_sha256"
    ]
    private["config_sha256"] = public["config_sha256"]
    _atomic_json(private_result_path, private)
    _atomic_json(public_result_path, public)
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in (
        "config",
        "transient",
        "steady",
        "public_split",
        "private_split",
        "train_audit_public",
        "train_audit_private",
        "public_result",
        "private_result",
    ):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    arguments = parser.parse_args()
    import torch
    result = run_attribution(
        arguments.config, arguments.transient, arguments.steady,
        arguments.public_split, arguments.private_split,
        arguments.train_audit_public, arguments.train_audit_private,
        arguments.public_result, arguments.private_result, torch,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
