"""One-shot D8 audit of mesh-derived normals for train-only AneuG WSS."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d6 import (
    approximate_histogram_quantile,
    area_weighted_vertex_normals,
    decode_release_channels,
    validate_private_split_manifest,
    load_contract as load_d6_registration,
)


class D8AuditError(RuntimeError):
    """Raised when the D8 geometry-normal contract cannot be honored."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D8AuditError(reason)


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version")
        == "aurora.aneug_processed_v4_d8_geometry_normal_audit.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_mesh_normal_identifiability_d8_v1",
        "protocol_id",
    )
    _require(contract.get("status") == "human_activated_executable", "status")
    activation = contract["human_activation"]
    _require(activation["explicitly_selected"] is True, "human_selection")
    _require(activation["selection"] == "D8", "human_selection_name")
    _require(activation["selected_on"] == "2026-08-17", "selection_date")
    for key in (
        "fresh_scientifically_distinct_version",
        "does_not_change_or_reinterpret_d7_thresholds",
        "does_not_repair_resume_rerun_reopen_or_relabel_d7",
    ):
        _require(activation[key] is True, f"activation_{key}")

    question = contract["question"]
    _require(question["stored_normal_magnitude_is_descriptive_only"] is True, "descriptive_only")
    _require(question["deterministic_geometry_repair_is_novelty"] is False, "novelty")
    _require(question["model_architecture_or_paper_claim"] is False, "paper_claim")

    bound = contract["bound_inputs"]
    _require(
        bound["d5_private_manifest_sha256"]
        == "0f95cf303fa63b58c049e722864389c1432460686e335d20402b677c368181d6",
        "d5_manifest_sha256",
    )
    _require(
        bound["d5_train_split_sha256"]
        == "df583f3553ce4efcf0588da5bdc029921025648c1981eba3a85fe3841d2bf26e",
        "d5_train_sha256",
    )
    _require(
        (
            bound["expected_train_cases"],
            bound["expected_validation_cases"],
            bound["expected_outer_test_cases"],
            bound["expected_timesteps"],
            bound["expected_nodes"],
            bound["expected_channels"],
        )
        == (406, 51, 51, 80, 13_902, 9),
        "expected_shape",
    )
    _require(bound["physical_decoder_formula"] == "physical=normalized*(std+1e-5)+mean", "decoder")
    _require(bound["physical_decoder_epsilon"] == 0.00001, "decoder_epsilon")

    expected = {
        "transient": (
            "processed_v4_d3/assembled_registered_data_1k_v4.pth",
            23_744_862_051,
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        ),
        "steady": (
            "processed_v4_d2/assembled_registered_steady_data_1k_v4.pth.temporary",
            9_632_510_050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
    }
    for name, (relative_path, size, sha256) in expected.items():
        item = contract["source_identity"][name]
        _require(item["relative_server_path"] == relative_path, f"{name}_path")
        _require(item["bytes"] == size, f"{name}_bytes")
        _require(item["sha256"] == sha256, f"{name}_sha256")

    read = contract["read_boundary"]
    _require(read["allowed_tensor_values"] == "d5_train_cases_only", "train_scope")
    _require(read["read_train_tensor_values"] is True, "train_read")
    _require(read["read_shared_finest_faces"] is True, "faces_read")
    for key in (
        "read_validation_tensor_values",
        "read_outer_test_tensor_values",
        "read_auxiliary_tensor_values",
        "publish_case_ids_or_split_members",
        "fit_or_select_model",
    ):
        _require(read[key] is False, f"read_boundary_{key}")

    census = contract["descriptive_stored_normal_census"]
    _require(census["lower_magnitude_cutoffs"] == [0.001, 0.01, 0.1, 0.5], "census_cutoffs")
    _require(census["upper_magnitude_cutoff"] == 1.5, "census_upper")
    _require(census["thresholds_select_or_change_gate"] is False, "census_gate")
    _require(census["report_counts_and_fractions_only"] is True, "census_output")

    gate = contract["prospective_gate"]
    _require(gate["all_checks_required"] is True, "all_checks")
    _require(gate["maximum_static_coordinate_normalized_abs_error"] == 0.000001, "static")
    _require(gate["minimum_nondegenerate_face_fraction_per_case"] == 0.999, "faces")
    _require(gate["minimum_mesh_unit_normal_valid_fraction_per_case"] == 0.999, "coverage")
    _require(gate["maximum_mesh_unit_normal_abs_error"] == 1e-12, "unit_error")
    _require(gate["direction_support_minimum_stored_normal_magnitude"] == 0.5, "direction_support")
    _require(gate["minimum_global_p05_absolute_mesh_stored_direction_cosine"] == 0.9, "direction")
    _require(gate["tangency_mask_minimum_fraction_of_case_p99_wss_magnitude"] == 0.01, "mask")
    _require(
        (gate["maximum_global_mesh_normal_component_ratio_median"], gate["maximum_global_mesh_normal_component_ratio_p95"])
        == (0.05, 0.25),
        "tangency",
    )
    _require(gate["minimum_case_fraction_passing_same_tangency_limits"] == 0.95, "case_fraction")
    _require(gate["histogram_bins"] == 10_000, "histogram_bins")
    _require(gate["scientific_verdict_before_execution"] is None, "premature_verdict")

    execution = contract["execution"]
    _require(execution["server"] == "introai9" and execution["excluded_server"] == "junjinyong", "server")
    _require(execution["scheduler"] == "PBS" and execution["queue"] == "coss_agpu", "scheduler")
    _require((execution["ncpus"], execution["memory_gb"], execution["ngpus"]) == (4, 64, 0), "resources")
    _require(execution["walltime"] == "03:00:00", "walltime")
    _require((execution["attempts_used_before_submission"], execution["maximum_pbs_attempts"]) == (0, 1), "attempt_budget")
    for key in (
        "one_interrupted_attempt_may_resume",
        "rerun_or_repair_after_any_outcome",
        "source_etc_profile_inside_wrapper",
        "scheduler_stdout_stderr_is_evidence",
        "login_node_gpu_allowed",
    ):
        _require(execution[key] is False, f"execution_{key}")
    for key in (
        "precreate_private_record_directory",
        "attempt_marker_and_internal_log_before_strict_mode",
        "exact_quality_passed_clean_commit_required",
        "private_activation_manifest_required",
    ):
        _require(execution[key] is True, f"execution_{key}")

    output = contract["output_contract"]
    _require(output["all_numeric_results_private"] is True, "result_privacy")
    _require(output["case_ids_absent_from_outputs"] is True, "id_privacy")
    _require(output["atomic_json"] is True and output["refuse_existing_output"] is True, "atomic_output")

    consequence = contract["consequence"]
    _require(consequence["any_attempt_outcome_closes_d8"] is True, "closure")
    _require(consequence["pass_permits_only_fresh_mesh_canonicalized_train_validation_development_registration"] is True, "pass_scope")
    for key in (
        "pass_permits_outer_test_access",
        "pass_permits_immediate_gpu_training",
        "pass_is_paper_result",
        "failure_or_incomplete_permits_same_contract_repair",
    ):
        _require(consequence[key] is False, f"consequence_{key}")

    authorization = contract["authorization"]
    for key in ("execute_d8_now", "submit_one_cpu_pbs", "monitor_that_attempt", "read_d5_train_field_values"):
        _require(authorization[key] is True, f"authorization_{key}")
    for key in (
        "read_validation_or_outer_field_values",
        "fit_or_select_model",
        "gpu_training",
        "paper_result_or_claim",
        "publish_numeric_result",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def _histogram_update(histogram: list[int], values: Any, torch: Any) -> int:
    finite = values.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    finite = finite[torch.isfinite(finite)]
    if int(finite.numel()) == 0:
        return 0
    counts = torch.histc(torch.clamp(finite, 0.0, 1.0), bins=len(histogram), min=0.0, max=1.0)
    for index, value in enumerate(counts.to(dtype=torch.int64).tolist()):
        histogram[index] += int(value)
    return int(finite.numel())


def inspect_case(
    tensor: Any,
    labels: Sequence[str],
    mean: Any,
    std: Any,
    faces: Any,
    contract: Mapping[str, Any],
    torch: Any,
) -> dict[str, Any]:
    _require(list(labels) == contract["bound_inputs"]["expected_labels"], "labels")
    _require(tensor.ndim == 3 and int(tensor.shape[-1]) == 9, "tensor_shape")
    normalized = tensor.detach().to(device="cpu", dtype=torch.float64)
    _require(bool(torch.isfinite(normalized).all().item()), "tensor_nonfinite")
    physical = decode_release_channels(
        normalized,
        mean,
        std,
        torch,
        epsilon=float(contract["bound_inputs"]["physical_decoder_epsilon"]),
    )
    static_coordinate_error = float((normalized[..., :3] - normalized[:1, :, :3]).abs().max().item())
    coordinates = physical[0, :, :3]
    stored = physical[0, :, 3:6]
    wss = physical[..., 6:9]
    mesh_unit, twice_area = area_weighted_vertex_normals(coordinates, faces, torch)
    mesh_norm = torch.linalg.vector_norm(mesh_unit, dim=-1)
    mesh_valid = mesh_norm > 0
    unit_error = (
        float(torch.abs(mesh_norm[mesh_valid] - 1.0).max().item())
        if bool(mesh_valid.any().item())
        else math.inf
    )
    stored_norm = torch.linalg.vector_norm(stored, dim=-1)
    direction_floor = float(
        contract["prospective_gate"]["direction_support_minimum_stored_normal_magnitude"]
    )
    direction_mask = mesh_valid & (stored_norm >= direction_floor)
    direction_cosine = torch.empty(0, dtype=torch.float64)
    if bool(direction_mask.any().item()):
        direction_cosine = torch.abs(
            torch.sum(stored[direction_mask] * mesh_unit[direction_mask], dim=-1)
        ) / torch.clamp(stored_norm[direction_mask] * mesh_norm[direction_mask], min=torch.finfo(torch.float64).tiny)

    magnitude = torch.linalg.vector_norm(wss, dim=-1)
    p99 = torch.quantile(magnitude.reshape(-1), 0.99)
    mask_fraction = float(
        contract["prospective_gate"]["tangency_mask_minimum_fraction_of_case_p99_wss_magnitude"]
    )
    tangent_mask = (magnitude >= mask_fraction * p99) & mesh_valid.unsqueeze(0)
    ratio = torch.abs(torch.sum(wss * mesh_unit.unsqueeze(0), dim=-1)) / torch.clamp(
        magnitude * mesh_norm.unsqueeze(0), min=torch.finfo(torch.float64).tiny
    )
    tangent_ratio = ratio[tangent_mask]
    case_median = float(torch.quantile(tangent_ratio, 0.5).item()) if int(tangent_ratio.numel()) else math.inf
    case_p95 = float(torch.quantile(tangent_ratio, 0.95).item()) if int(tangent_ratio.numel()) else math.inf
    cutoffs = contract["descriptive_stored_normal_census"]["lower_magnitude_cutoffs"]
    lower_counts = {str(value): int((stored_norm < float(value)).sum().item()) for value in cutoffs}
    upper_cutoff = float(contract["descriptive_stored_normal_census"]["upper_magnitude_cutoff"])
    return {
        "static_coordinate_max_abs": static_coordinate_error,
        "face_nondegenerate_fraction": float((twice_area > 0).to(torch.float64).mean().item()),
        "mesh_valid_fraction": float(mesh_valid.to(torch.float64).mean().item()),
        "mesh_unit_abs_error": unit_error,
        "direction_cosine": direction_cosine,
        "mesh_tangent_ratio": tangent_ratio,
        "case_mesh_tangent_median": case_median,
        "case_mesh_tangent_p95": case_p95,
        "stored_node_count": int(stored_norm.numel()),
        "stored_lower_counts": lower_counts,
        "stored_upper_count": int((stored_norm > upper_cutoff).sum().item()),
    }


def aggregate_diagnostics(
    diagnostics: Iterable[Mapping[str, Any]],
    contract: Mapping[str, Any],
    torch: Any,
    *,
    source_identity_reverified: bool,
    private_manifest_reverified: bool,
    train_scope_enforced: bool,
    shared_faces_valid: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    gate = contract["prospective_gate"]
    bins = int(gate["histogram_bins"])
    tangent_hist = [0] * bins
    direction_hist = [0] * bins
    tangent_count = 0
    direction_count = 0
    case_count = 0
    case_tangent_pass_count = 0
    static_max = 0.0
    face_fraction_min = 1.0
    mesh_coverage_min = 1.0
    unit_error_max = 0.0
    stored_node_count = 0
    lower_counts = {str(value): 0 for value in contract["descriptive_stored_normal_census"]["lower_magnitude_cutoffs"]}
    upper_count = 0

    for item in diagnostics:
        case_count += 1
        static_max = max(static_max, float(item["static_coordinate_max_abs"]))
        face_fraction_min = min(face_fraction_min, float(item["face_nondegenerate_fraction"]))
        mesh_coverage_min = min(mesh_coverage_min, float(item["mesh_valid_fraction"]))
        unit_error_max = max(unit_error_max, float(item["mesh_unit_abs_error"]))
        tangent_count += _histogram_update(tangent_hist, item["mesh_tangent_ratio"], torch)
        direction_count += _histogram_update(direction_hist, item["direction_cosine"], torch)
        case_tangent_pass_count += int(
            float(item["case_mesh_tangent_median"])
            <= float(gate["maximum_global_mesh_normal_component_ratio_median"])
            and float(item["case_mesh_tangent_p95"])
            <= float(gate["maximum_global_mesh_normal_component_ratio_p95"])
        )
        stored_node_count += int(item["stored_node_count"])
        for key, value in item["stored_lower_counts"].items():
            lower_counts[key] += int(value)
        upper_count += int(item["stored_upper_count"])

    global_median = (
        approximate_histogram_quantile(tangent_hist, 0.5, 0.0, 1.0)
        if tangent_count
        else math.inf
    )
    global_p95 = (
        approximate_histogram_quantile(tangent_hist, 0.95, 0.0, 1.0)
        if tangent_count
        else math.inf
    )
    direction_p05 = (
        approximate_histogram_quantile(direction_hist, 0.05, 0.0, 1.0)
        if direction_count
        else -math.inf
    )
    case_pass_fraction = case_tangent_pass_count / case_count if case_count else 0.0
    checks = {
        "source_sizes_and_sha256_exact": bool(source_identity_reverified),
        "d5_private_manifest_and_train_digest_exact": bool(private_manifest_reverified),
        "only_d5_train_tensor_values_read": bool(train_scope_enforced),
        "shared_faces_valid_nonrepeated_triangles": bool(shared_faces_valid),
        "expected_train_case_count": case_count == int(contract["bound_inputs"]["expected_train_cases"]),
        "static_coordinates": static_max <= float(gate["maximum_static_coordinate_normalized_abs_error"]),
        "nondegenerate_face_fraction": face_fraction_min >= float(gate["minimum_nondegenerate_face_fraction_per_case"]),
        "mesh_unit_normal_coverage": mesh_coverage_min >= float(gate["minimum_mesh_unit_normal_valid_fraction_per_case"]),
        "mesh_unit_normal_norm": unit_error_max <= float(gate["maximum_mesh_unit_normal_abs_error"]),
        "mesh_stored_direction_agreement": direction_p05 >= float(gate["minimum_global_p05_absolute_mesh_stored_direction_cosine"]),
        "mesh_normal_wss_tangency_global": global_median <= float(gate["maximum_global_mesh_normal_component_ratio_median"])
        and global_p95 <= float(gate["maximum_global_mesh_normal_component_ratio_p95"]),
        "mesh_normal_wss_tangency_case_coverage": case_pass_fraction >= float(gate["minimum_case_fraction_passing_same_tangency_limits"]),
    }
    reasons = sorted(key for key, value in checks.items() if not value)
    passed = not reasons
    result = {
        "schema_version": "aurora.aneug_processed_v4_d8_geometry_normal_audit.result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "completed_passed" if passed else "completed_failed",
        "scientific_verdict": "pass" if passed else "fail",
        "gate_pass": passed,
        "gate_reasons": reasons,
        "check_results": checks,
        "train_case_count": case_count,
        "validation_case_field_count_read": 0,
        "outer_test_case_field_count_read": 0,
        "auxiliary_case_field_count_read": 0,
        "minimum_case_mesh_unit_normal_valid_fraction": mesh_coverage_min,
        "maximum_mesh_unit_normal_abs_error": unit_error_max,
        "minimum_case_nondegenerate_face_fraction": face_fraction_min,
        "maximum_static_coordinate_normalized_abs_error": static_max,
        "global_mesh_stored_direction_abs_cosine_p05_histogram": direction_p05 if math.isfinite(direction_p05) else None,
        "global_mesh_normal_component_ratio_median_histogram": global_median if math.isfinite(global_median) else None,
        "global_mesh_normal_component_ratio_p95_histogram": global_p95 if math.isfinite(global_p95) else None,
        "case_fraction_passing_same_tangency_limits": case_pass_fraction,
        "stored_normal_census_selects_gate": False,
        "case_ids_included": False,
        "model_fitted_or_selected": False,
        "gpu_used": False,
        "paper_result_or_claim_authorized": False,
        "numeric_result_publication_authorized": False,
        "d8_closes_after_this_outcome": True,
    }
    statistics = {
        "schema_version": "aurora.aneug_processed_v4_d8_geometry_normal_audit.private_statistics.v1",
        "protocol_id": contract["protocol_id"],
        "train_split_sha256": contract["bound_inputs"]["d5_train_split_sha256"],
        "train_case_count": case_count,
        "stored_normal_node_count": stored_node_count,
        "stored_normal_magnitude_below_counts": lower_counts,
        "stored_normal_magnitude_below_fractions": {
            key: value / stored_node_count if stored_node_count else None
            for key, value in lower_counts.items()
        },
        "stored_normal_magnitude_above_1p5_count": upper_count,
        "stored_normal_magnitude_above_1p5_fraction": upper_count / stored_node_count if stored_node_count else None,
        "stored_normal_census_is_descriptive_only": True,
        "case_ids_included": False,
        "validation_outer_or_auxiliary_statistics_included": False,
    }
    return result, statistics


def selected_diagnostics(
    case_by_id: Mapping[str, Mapping[str, Any]],
    train_ids: Sequence[str],
    sealed_ids: Sequence[str],
    labels: Sequence[str],
    mean: Any,
    std: Any,
    faces: Any,
    contract: Mapping[str, Any],
    torch: Any,
) -> Iterable[Mapping[str, Any]]:
    train = [str(item) for item in train_ids]
    sealed = {str(item) for item in sealed_ids}
    _require(len(train) == len(set(train)) and not set(train).intersection(sealed), "split_overlap")
    _require(set(train).issubset(case_by_id), "missing_train_case")
    expected = [
        int(contract["bound_inputs"]["expected_timesteps"]),
        int(contract["bound_inputs"]["expected_nodes"]),
        int(contract["bound_inputs"]["expected_channels"]),
    ]
    for case_id in train:
        case = case_by_id[case_id]
        _require([str(item) for item in case.get("labels", [])] == list(labels), "case_labels")
        tensor = case.get("tensor")
        _require(hasattr(tensor, "shape") and list(tensor.shape) == expected, "case_tensor_shape")
        yield inspect_case(tensor, labels, mean, std, faces, contract, torch)


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists(), f"output_exists:{target.name}")
    _require(not temporary.exists(), f"temporary_output_exists:{target.name}")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def verify_exact_file(path: str | Path, identity: Mapping[str, Any], label: str) -> None:
    source = Path(path)
    _require(source.is_file(), f"missing_{label}")
    _require(source.stat().st_size == int(identity["bytes"]), f"{label}_size")
    _require(file_sha256(source) == identity["sha256"], f"{label}_sha256")


def run(
    contract_path: str | Path,
    d6_registration_path: str | Path,
    transient_path: str | Path,
    steady_path: str | Path,
    private_manifest_path: str | Path,
    result_path: str | Path,
    statistics_path: str | Path,
    torch: Any,
) -> dict[str, Any]:
    contract = load_contract(contract_path)
    verify_exact_file(transient_path, contract["source_identity"]["transient"], "transient")
    verify_exact_file(steady_path, contract["source_identity"]["steady"], "steady")
    manifest_path = Path(private_manifest_path)
    _require(manifest_path.is_file(), "missing_d5_private_manifest")
    _require(file_sha256(manifest_path) == contract["bound_inputs"]["d5_private_manifest_sha256"], "d5_manifest_file_sha256")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    d6_registration = load_d6_registration(d6_registration_path)
    buckets = validate_private_split_manifest(d6_registration, manifest)

    steady = safe_torch_load(steady_path, torch)
    transient = safe_torch_load(transient_path, torch)
    _require(isinstance(steady, Mapping) and {"label", "tensor_norm"}.issubset(steady), "steady_schema")
    labels = [str(item) for item in steady["label"]]
    _require(labels == contract["bound_inputs"]["expected_labels"], "steady_labels")
    norm = steady["tensor_norm"]
    mean = norm["mean"].detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    std = norm["std"].detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    _require(bool(torch.isfinite(mean).all().item()) and bool(torch.isfinite(std).all().item()) and bool((std > 0).all().item()), "normalization_metadata")

    _require(isinstance(transient, Mapping) and {"registered_data_list", "mesh_data"}.issubset(transient), "transient_schema")
    faces = transient["mesh_data"]["faces_list"][0].detach().to(device="cpu")
    expected_nodes = int(contract["bound_inputs"]["expected_nodes"])
    shared_faces_valid = (
        faces.ndim == 2
        and int(faces.shape[1]) == 3
        and int(faces.min().item()) >= 0
        and int(faces.max().item()) < expected_nodes
        and not bool((faces[:, 0] == faces[:, 1]).any().item())
        and not bool((faces[:, 1] == faces[:, 2]).any().item())
        and not bool((faces[:, 0] == faces[:, 2]).any().item())
    )
    _require(shared_faces_valid, "shared_faces")
    cases = transient["registered_data_list"]
    case_by_id: dict[str, Mapping[str, Any]] = {}
    for case in cases:
        _require(isinstance(case, Mapping), "case_mapping")
        case_id = str(case.get("case", ""))
        _require(case_id and case_id not in case_by_id, "case_id_integrity")
        case_by_id[case_id] = case
    train_ids = buckets["train"]
    sealed_ids = buckets["validation"] + buckets["outer_test"] + buckets["auxiliary"]
    stream = selected_diagnostics(
        case_by_id,
        train_ids,
        sealed_ids,
        labels,
        mean,
        std,
        faces,
        contract,
        torch,
    )
    result, statistics = aggregate_diagnostics(
        stream,
        contract,
        torch,
        source_identity_reverified=True,
        private_manifest_reverified=True,
        train_scope_enforced=True,
        shared_faces_valid=shared_faces_valid,
    )
    _strict_atomic_json(statistics_path, statistics)
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--d6-registration", type=Path)
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--private-d5-manifest", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--private-statistics", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    load_contract(args.config)
    if args.validate_only:
        return 0
    required = (
        args.d6_registration,
        args.transient,
        args.steady,
        args.private_d5_manifest,
        args.result,
        args.private_statistics,
    )
    _require(all(value is not None for value in required), "missing_execution_argument")
    import torch

    torch.set_num_threads(4)
    result = run(
        args.config,
        args.d6_registration,
        args.transient,
        args.steady,
        args.private_d5_manifest,
        args.result,
        args.private_statistics,
        torch,
    )
    print(
        "D8 geometry-normal audit complete; "
        f"gate_pass={str(result['gate_pass']).lower()}; validation/outer reads=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
