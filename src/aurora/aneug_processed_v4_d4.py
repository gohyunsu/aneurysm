"""Non-executable draft utilities for an AneuG processed-v4 D4 census.

The draft deliberately has no file-loading or PBS execution entry point. It
validates the unselected contract and provides a pure metadata census used by
synthetic tests. A future human-selected D4 must be a fresh registered version;
mutating this draft into an executable contract is prohibited.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


class D4DraftContractError(RuntimeError):
    """Raised when the dormant D4 design or metadata boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D4DraftContractError(reason)


def load_draft_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_draft_contract(contract)
    return contract


def validate_draft_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version") == "aurora.aneug_processed_v4_d4_draft.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id") == "aneug_processed_v4_metadata_census_d4_draft",
        "protocol_id",
    )
    _require(contract.get("status") == "draft_unselected_non_executable", "draft_status")
    selection = contract["human_selection"]
    _require(selection["explicitly_selected"] is False, "human_selection")
    _require(selection["selected_on"] is None and selection["selection"] is None, "selection_fields")
    source = contract["source"]
    _require(
        source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "dataset_revision",
    )
    identities = {
        "transient": (
            23_744_862_051,
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        ),
        "steady_norm_source": (
            9_632_510_050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
    }
    for role, identity in identities.items():
        item = source[role]
        _require((item["bytes"], item["sha256"]) == identity, f"{role}_identity")
    d3 = contract["closed_d3_boundary"]
    _require(d3["status"] == "closed_transport_passed_schema_failed_case_floor", "d3_status")
    _require(d3["minimum_cases"] == 700, "d3_floor_history")
    for key in ("exact_count_recorded", "post_hoc_backfill", "repair_or_rerun", "d4_relabels_d3"):
        _require(d3[key] is False, key)
    census = contract["census_contract"]
    _require(census["cardinality_pass_threshold"] is None, "cardinality_threshold")
    for key in (
        "weights_only",
        "mmap",
        "record_exact_registered_count",
        "record_private_ordered_case_ids",
        "record_public_ordered_case_id_sha256",
        "record_blank_and_duplicate_id_counts",
        "record_label_timestep_shape_dtype_histograms",
        "record_mesh_case_order_agreement",
        "record_geometry_linkage_counts",
        "record_normalization_metadata_only",
    ):
        _require(census[key] is True, key)
    for key in ("read_tensor_values", "compute_scientific_field_metric", "publish_case_ids"):
        _require(census[key] is False, key)
    envelope = contract["execution_envelope_if_selected_in_fresh_version"]
    _require(envelope["server"] == "introai9", "server")
    _require(envelope["ncpus"] == 4 and envelope["memory_gb"] == 64, "cpu_memory")
    _require(envelope["ngpus"] == 0, "gpu")
    _require(envelope["maximum_pbs_attempts"] == 1, "attempt_budget")
    _require(envelope["rerun_after_any_outcome"] is False, "rerun")
    _require(envelope["excluded_server"] == "junjinyong", "excluded_server")
    consequence = contract["completion_consequence_if_selected"]
    _require(consequence["permits_human_rescoring_only"] is True, "human_rescore")
    for key, value in consequence.items():
        if key != "permits_human_rescoring_only":
            _require(value is False, key)
    activation = contract["activation_requirements"]
    _require(activation["explicit_human_selection"] is True, "activation_selection")
    _require(activation["fresh_registered_config"] is True, "fresh_config")
    _require(activation["draft_file_mutation_into_executable_contract"] is False, "draft_mutation")
    _require(all(value is False for value in contract["authorization"].values()), "authorization")


def assert_execution_authorized(contract: Mapping[str, Any]) -> None:
    """Fail closed: this source version accepts only the dormant draft."""

    validate_draft_contract(contract)
    raise D4DraftContractError("draft_non_executable_requires_fresh_human_selected_version")


def _tensor_metadata(value: Any) -> dict[str, Any] | None:
    shape = getattr(value, "shape", None)
    dtype = getattr(value, "dtype", None)
    if shape is None or dtype is None:
        return None
    return {"shape": [int(item) for item in shape], "dtype": str(dtype)}


def _histogram(values: Sequence[Any]) -> dict[str, int]:
    encoded = [json.dumps(value, separators=(",", ":"), sort_keys=True) for value in values]
    return dict(sorted(Counter(encoded).items()))


def _safe_case_component(value: str) -> bool:
    return bool(value) and value not in {".", ".."} and Path(value).name == value


def census_loaded_metadata(
    contract: Mapping[str, Any],
    transient: Mapping[str, Any],
    steady: Mapping[str, Any],
    geometry_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Describe object metadata without indexing or materializing tensor values."""

    validate_draft_contract(contract)
    _require({"registered_data_list", "mesh_data"}.issubset(transient), "transient_keys")
    _require({"label", "tensor_norm"}.issubset(steady), "steady_keys")
    cases = transient["registered_data_list"]
    mesh = transient["mesh_data"]
    _require(isinstance(cases, Sequence) and not isinstance(cases, (str, bytes)), "case_sequence")
    _require(isinstance(mesh, Mapping) and "cases" in mesh, "mesh_cases")

    case_ids: list[str] = []
    labels: list[list[str]] = []
    tensor_metadata: list[dict[str, Any] | None] = []
    for case in cases:
        _require(isinstance(case, Mapping), "case_mapping")
        case_ids.append(str(case.get("case", "")))
        labels.append([str(item) for item in case.get("labels", [])])
        tensor_metadata.append(_tensor_metadata(case.get("tensor")))

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

    geometry_linked_count: int | None = None
    unsafe_case_component_count = sum(not _safe_case_component(item) for item in case_ids)
    if geometry_root is not None:
        geometry_linked_count = sum(
            (geometry_root / item).is_dir() for item in case_ids if _safe_case_component(item)
        )

    norm = steady["tensor_norm"]
    _require(isinstance(norm, Mapping), "tensor_norm")
    norm_metadata = {key: _tensor_metadata(norm.get(key)) for key in ("mean", "std")}
    private_manifest = {
        "schema_version": "aurora.aneug_processed_v4_d4.private_case_manifest.v1",
        "ordered_case_ids": case_ids,
        "ordered_case_id_sha256": case_digest,
        "case_ids_public": False,
    }
    public_result = {
        "schema_version": "aurora.aneug_processed_v4_d4.public_census_result.v1",
        "status": "descriptive_metadata_census",
        "registered_case_count": len(case_ids),
        "ordered_case_id_sha256": case_digest,
        "blank_case_id_count": blank_count,
        "duplicate_case_id_count": duplicate_id_count,
        "unsafe_case_component_count": unsafe_case_component_count,
        "tensor_metadata_missing_count": sum(item is None for item in tensor_metadata),
        "label_histogram": _histogram(labels),
        "timestep_histogram": _histogram(timesteps),
        "tensor_shape_histogram": _histogram(shapes),
        "tensor_dtype_histogram": _histogram(dtypes),
        "mesh_case_count": len(mesh_cases),
        "mesh_case_order_exact": case_ids == mesh_cases,
        "registered_only_case_count": len(case_set - mesh_set),
        "mesh_only_case_count": len(mesh_set - case_set),
        "geometry_linkage_evaluated": geometry_root is not None,
        "geometry_linked_count": geometry_linked_count,
        "steady_labels": [str(item) for item in steady["label"]],
        "normalization_metadata": norm_metadata,
        "cardinality_pass_threshold": None,
        "case_ids_public": False,
        "tensor_values_read": False,
        "scientific_field_metric_computed": False,
        "scientific_verdict": False,
        "permits_human_rescoring_only": True,
    }
    serialized_public = json.dumps(public_result, ensure_ascii=False, sort_keys=True)
    for case_id in case_ids:
        if case_id:
            _require(
                json.dumps(case_id, ensure_ascii=False) not in serialized_public,
                "case_id_leaked_public",
            )
    return public_result, private_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true", required=True)
    args = parser.parse_args()
    load_draft_contract(args.config)
    print("AneuG processed-v4 D4 draft valid · unselected · non-executable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
