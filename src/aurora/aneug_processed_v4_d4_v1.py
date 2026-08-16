"""Selected, one-shot AneuG processed-v4 D4 metadata census.

D4 is not a repair of the closed D3 case-floor gate. It describes the exact
processed snapshot without a cohort-size threshold, reads no tensor or mesh
connectivity values, and emits case identifiers only to a private manifest.
Any PBS outcome closes this version and permits human rescoring only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d1 import file_sha256


class D4ContractError(RuntimeError):
    """Raised when the selected D4 contract or census boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D4ContractError(reason)


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(contract.get("schema_version") == "aurora.aneug_processed_v4_d4.v1", "schema_version")
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_threshold_free_metadata_census_d4_v1",
        "protocol_id",
    )
    _require(contract.get("status") == "registered_selected_not_executed", "status")
    selection = contract["human_selection"]
    _require(selection == {
        "explicitly_selected": True,
        "selected_on": "2026-08-16",
        "selection": "D4",
    }, "human_selection")
    source = contract["source"]
    _require(source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36", "dataset_revision")
    _require(source["code_revision"] == "4a090a0f12538deef6fcea88b81afe78ce38152e", "code_revision")
    identities = {
        "transient": (23_744_862_051, "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9"),
        "steady_norm_source": (9_632_510_050, "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f"),
    }
    for role, identity in identities.items():
        item = source[role]
        _require((item["bytes"], item["sha256"]) == identity, f"{role}_identity")
    d3 = contract["closed_d3_boundary"]
    _require(d3["status"] == "closed_transport_passed_schema_failed_case_floor", "d3_status")
    _require(d3["minimum_cases"] == 700 and d3["exact_count_recorded"] is False, "d3_history")
    for key in ("post_hoc_backfill", "repair_or_rerun", "d4_is_d3_retry_or_repair", "d4_relabels_d3"):
        _require(d3[key] is False, key)
    census = contract["census_contract"]
    _require(census["cardinality_pass_threshold"] is None, "cardinality_threshold")
    for key in (
        "weights_only", "mmap", "record_exact_registered_count",
        "record_private_ordered_case_ids", "record_public_ordered_case_id_sha256",
        "record_blank_and_duplicate_id_counts", "record_root_and_case_key_histograms",
        "record_label_timestep_shape_dtype_histograms", "record_mesh_case_order_agreement",
        "record_mesh_hierarchy_shape_dtype_metadata",
        "record_mesh_geometry_tensor_shape_dtype_metadata", "record_geometry_linkage_counts",
        "record_normalization_metadata_only",
    ):
        _require(census[key] is True, key)
    _require(census["map_location"] == "cpu", "map_location")
    for key in (
        "arbitrary_pickle_globals_allowed", "read_tensor_values",
        "read_mesh_connectivity_values", "compute_scientific_field_metric", "publish_case_ids",
    ):
        _require(census[key] is False, key)
    output = contract["output_contract"]
    _require(output["atomic_writes"] is True, "atomic_writes")
    _require(output["source_objects_mutated_or_deleted"] is False, "source_mutation")
    _require(output["raw_logs_private"] is True and output["case_ids_private"] is True, "privacy")
    execution = contract["execution"]
    _require(execution["server"] == "introai9" and execution["scheduler"] == "PBS", "server")
    _require(execution["queue"] == "coss_agpu", "queue")
    _require((execution["ncpus"], execution["memory_gb"], execution["ngpus"]) == (4, 64, 0), "resources")
    _require(execution["walltime"] == "02:00:00", "walltime")
    _require(execution["maximum_pbs_attempts"] == 1, "attempt_budget")
    _require(execution["rerun_after_any_outcome"] is False, "rerun")
    _require(execution["login_node_gpu_allowed"] is False, "login_gpu")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")
    consequence = contract["completion_consequence"]
    _require(consequence["permits_human_rescoring_only"] is True, "human_rescore")
    for key, value in consequence.items():
        if key != "permits_human_rescoring_only":
            _require(value is False, key)
    activation = contract["activation_requirements"]
    _require(all(activation[key] is True for key in (
        "quality_passed_public_source", "clean_introai9_checkout",
        "private_activation_manifest", "source_size_and_sha256_reverified_in_job",
    )), "activation")
    _require(activation["draft_file_mutated"] is False, "draft_mutation")
    authorization = contract["authorization"]
    for key in ("register_d4", "read_processed_metadata", "submit_single_cpu_pbs", "monitor_single_cpu_pbs"):
        _require(authorization[key] is True, key)
    for key in (
        "scientific_p0", "method_or_architecture", "gpu_training",
        "validation_or_test", "outer_test", "paper_result_or_claim",
    ):
        _require(authorization[key] is False, key)


def _tensor_metadata(value: Any) -> dict[str, Any] | None:
    shape = getattr(value, "shape", None)
    dtype = getattr(value, "dtype", None)
    if shape is None or dtype is None:
        return None
    return {"shape": [int(item) for item in shape], "dtype": str(dtype)}


def _histogram(values: Sequence[Any]) -> dict[str, int]:
    encoded = [json.dumps(value, separators=(",", ":"), sort_keys=True) for value in values]
    return dict(sorted(Counter(encoded).items()))


def _sequence_tensor_metadata(value: Any) -> dict[str, Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return {"present": value is not None, "is_sequence": False, "sequence_length": None, "items": []}
    items = [_tensor_metadata(item) for item in value]
    return {
        "present": True,
        "is_sequence": True,
        "sequence_length": len(value),
        "items": items,
        "items_without_tensor_metadata": sum(item is None for item in items),
    }


def _safe_case_component(value: str) -> bool:
    return bool(value) and value not in {".", ".."} and Path(value).name == value


def census_loaded_metadata(
    contract: Mapping[str, Any],
    transient: Mapping[str, Any],
    steady: Mapping[str, Any],
    geometry_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_contract(contract)
    _require(isinstance(transient, Mapping), "transient_mapping")
    _require({"registered_data_list", "mesh_data"}.issubset(transient), "transient_keys")
    _require(isinstance(steady, Mapping), "steady_mapping")
    _require({"label", "tensor_norm"}.issubset(steady), "steady_keys")
    cases = transient["registered_data_list"]
    mesh = transient["mesh_data"]
    _require(isinstance(cases, Sequence) and not isinstance(cases, (str, bytes)), "case_sequence")
    _require(isinstance(mesh, Mapping) and "cases" in mesh, "mesh_cases")

    case_ids: list[str] = []
    labels: list[list[str]] = []
    tensor_metadata: list[dict[str, Any] | None] = []
    case_keys: list[list[str]] = []
    for case in cases:
        _require(isinstance(case, Mapping), "case_mapping")
        case_ids.append(str(case.get("case", "")))
        labels.append([str(item) for item in case.get("labels", [])])
        tensor_metadata.append(_tensor_metadata(case.get("tensor")))
        case_keys.append(sorted(str(key) for key in case))

    canonical_ids = json.dumps(case_ids, ensure_ascii=False, separators=(",", ":"))
    case_digest = hashlib.sha256(canonical_ids.encode("utf-8")).hexdigest()
    counts = Counter(case_ids)
    blank_count = sum(not item for item in case_ids)
    duplicate_id_count = sum(count - 1 for key, count in counts.items() if key and count > 1)
    shapes = [item["shape"] if item else None for item in tensor_metadata]
    dtypes = [item["dtype"] if item else None for item in tensor_metadata]
    timesteps = [item["shape"][0] if item and item["shape"] else None for item in tensor_metadata]
    mesh_cases = [str(item) for item in mesh["cases"]]
    case_set = {item for item in case_ids if item}
    mesh_set = {item for item in mesh_cases if item}
    unsafe_count = sum(not _safe_case_component(item) for item in case_ids)
    linked_count: int | None = None
    if geometry_root is not None:
        linked_count = sum((geometry_root / item).is_dir() for item in case_ids if _safe_case_component(item))

    norm = steady["tensor_norm"]
    _require(isinstance(norm, Mapping), "tensor_norm")
    private_manifest = {
        "schema_version": "aurora.aneug_processed_v4_d4.private_case_manifest.v1",
        "protocol_id": contract["protocol_id"],
        "ordered_case_ids": case_ids,
        "ordered_case_id_sha256": case_digest,
        "case_ids_public": False,
    }
    public_result = {
        "schema_version": "aurora.aneug_processed_v4_d4.public_census_result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "descriptive_metadata_census_complete",
        "registered_case_count": len(case_ids),
        "ordered_case_id_sha256": case_digest,
        "blank_case_id_count": blank_count,
        "duplicate_case_id_count": duplicate_id_count,
        "unsafe_case_component_count": unsafe_count,
        "transient_root_keys": sorted(str(key) for key in transient),
        "steady_root_keys": sorted(str(key) for key in steady),
        "mesh_root_keys": sorted(str(key) for key in mesh),
        "case_key_histogram": _histogram(case_keys),
        "tensor_metadata_missing_count": sum(item is None for item in tensor_metadata),
        "label_histogram": _histogram(labels),
        "timestep_histogram": _histogram(timesteps),
        "tensor_shape_histogram": _histogram(shapes),
        "tensor_dtype_histogram": _histogram(dtypes),
        "mesh_case_count": len(mesh_cases),
        "mesh_case_order_exact": case_ids == mesh_cases,
        "registered_only_case_count": len(case_set - mesh_set),
        "mesh_only_case_count": len(mesh_set - case_set),
        "mesh_hierarchy_metadata": {
            key: _sequence_tensor_metadata(mesh.get(key))
            for key in ("idx_list", "edge_index_list", "faces_list")
        },
        "mesh_geometry_tensor_metadata": {
            key: _tensor_metadata(mesh.get(key)) for key in ("ghd", "shape_scale")
        },
        "geometry_linkage_evaluated": geometry_root is not None,
        "geometry_linked_count": linked_count,
        "steady_labels": [str(item) for item in steady["label"]],
        "normalization_metadata": {key: _tensor_metadata(norm.get(key)) for key in ("mean", "std")},
        "source_identity_reverified": True,
        "cardinality_pass_threshold": None,
        "case_ids_public": False,
        "tensor_values_read": False,
        "mesh_connectivity_values_read": False,
        "scientific_field_metric_computed": False,
        "scientific_verdict": None,
        "census_outcome": "observed_without_pass_fail_threshold",
        "permits_human_rescoring_only": True,
    }
    serialized_public = json.dumps(public_result, ensure_ascii=False, sort_keys=True)
    for case_id in case_ids:
        if case_id:
            _require(json.dumps(case_id, ensure_ascii=False) not in serialized_public, "case_id_leaked_public")
    return public_result, private_manifest


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    _require(not temporary.exists(), f"temporary_output_exists:{path.name}")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def run_census(
    contract: Mapping[str, Any],
    transient_path: Path,
    steady_path: Path,
    geometry_root: Path,
    public_result_path: Path,
    private_manifest_path: Path,
    torch: Any,
) -> dict[str, Any]:
    for role, path in (("transient", transient_path), ("steady_norm_source", steady_path)):
        identity = contract["source"][role]
        _require(path.is_file(), f"missing:{role}")
        _require(path.stat().st_size == identity["bytes"], f"size:{role}")
        _require(file_sha256(path) == identity["sha256"], f"sha256:{role}")
    _require(geometry_root.is_dir(), "geometry_root")
    transient = safe_torch_load(transient_path, torch)
    steady = safe_torch_load(steady_path, torch)
    public, private = census_loaded_metadata(contract, transient, steady, geometry_root)
    _atomic_json(private_manifest_path, private)
    _atomic_json(public_result_path, public)
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--transient", type=Path, required=True)
    parser.add_argument("--steady", type=Path, required=True)
    parser.add_argument("--geometry-root", type=Path, required=True)
    parser.add_argument("--public-result", type=Path, required=True)
    parser.add_argument("--private-case-manifest", type=Path, required=True)
    args = parser.parse_args()
    contract = load_contract(args.config)
    import torch
    run_census(
        contract, args.transient, args.steady, args.geometry_root,
        args.public_result, args.private_case_manifest, torch,
    )
    print("D4 descriptive metadata census complete; scientific verdict is null")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
