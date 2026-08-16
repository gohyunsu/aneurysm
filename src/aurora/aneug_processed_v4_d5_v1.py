"""Selected one-shot D5 audit for processed AneuG geometry tokens.

D5 reads only the small, case-aligned ``mesh_data.ghd`` matrix from the exact
processed-v4 transient object.  It groups exact and fixed-tolerance numerical
copies before freezing a private synthetic-geometry-component split.  It does
not read registered field tensors, WSS, coordinates, normals, connectivity or
an external geometry payload.  Any PBS outcome consumes the sole D5 attempt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d1 import file_sha256


class D5ContractError(RuntimeError):
    """Raised when the registered D5 scope or evidence boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D5ContractError(reason)


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version") == "aurora.aneug_processed_v4_d5.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_ghd_component_split_d5_v1",
        "protocol_id",
    )
    _require(contract.get("status") == "registered_selected_not_executed", "status")
    _require(
        contract["human_selection"]
        == {
            "explicitly_selected": True,
            "selected_on": "2026-08-16",
            "selection": "D5",
        },
        "human_selection",
    )

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
    transient = source["transient"]
    _require(transient["bytes"] == 23_744_862_051, "transient_bytes")
    _require(
        transient["sha256"]
        == "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        "transient_sha256",
    )
    _require(
        source["d4_public_census_sha256"]
        == "06d111498b62d36a144e47c762bd01b4d059698bbff1f407c96243b83b81de8d",
        "d4_census_identity",
    )
    _require(
        source["d4_ordered_case_id_sha256"]
        == "5e6fa02faa93f88cef258e4ca8defecad04506e3d3de3081ba647e69b1d29930",
        "d4_ordered_case_identity",
    )

    d4 = contract["closed_d4_boundary"]
    _require(d4["status"] == "closed_complete_descriptive_metadata_census", "d4_status")
    _require((d4["attempts_used"], d4["attempt_limit"]) == (1, 1), "d4_attempts")
    _require(d4["registered_cases"] == 578 and d4["ghd_shape"] == [578, 432], "d4_shape")
    _require(d4["scientific_verdict"] is None, "d4_scientific_verdict")
    _require(d4["repair_or_rerun"] is False and d4["d5_relabels_d4"] is False, "d4_immutable")

    builder = contract["official_builder_semantics"]
    for key in (
        "case_directories_selected_from_transient_root",
        "ghd_loaded_from_each_transient_case_checkpoint",
        "mesh_cases_and_ghd_rows_share_builder_order",
    ):
        _require(builder[key] is True, key)
    _require(
        builder["external_geometry_directory_join_required_for_processed_input"] is False,
        "external_geometry_join",
    )
    _require(builder["generator_parent_or_patient_lineage_asserted"] is False, "lineage_claim")

    geometry = contract["geometry_token_contract"]
    _require(geometry["weights_only"] is True and geometry["mmap"] is True, "safe_load")
    _require(geometry["map_location"] == "cpu", "map_location")
    _require(geometry["allowed_value_read"] == "mesh_data.ghd_only", "allowed_value_read")
    _require(geometry["expected_case_count"] == 578, "expected_case_count")
    _require(geometry["expected_ghd_shape"] == [578, 432], "expected_ghd_shape")
    _require(geometry["expected_ghd_dtype"] == "torch.float32", "expected_ghd_dtype")
    _require(geometry["primary_case_regex"] == "^stable_[0-9]+$", "primary_regex")
    _require(geometry["mixed_primary_auxiliary_component_role"] == "sealed_auxiliary", "mixed_role")
    tolerance = geometry["numerical_equivalence"]
    _require(
        tolerance
        == {"max_abs": 0.000001, "rms": 0.0000001, "pairwise_block_rows": 32},
        "numerical_tolerance",
    )
    for key in (
        "require_case_mesh_order_exact",
        "require_all_ghd_values_finite",
        "near_or_exact_duplicate_components_stay_within_one_split",
    ):
        _require(geometry[key] is True, key)
    for key in (
        "read_registered_case_tensor_values",
        "read_wss_values",
        "read_coordinate_or_normal_values",
        "read_mesh_connectivity_values",
        "read_external_geometry_payload",
        "compute_scientific_field_metric",
        "publish_case_ids_or_split_members",
    ):
        _require(geometry[key] is False, key)

    split = contract["split_contract"]
    _require(split["unit"] == "synthetic_geometry_component_not_patient", "split_unit")
    _require(
        (split["train_fraction"], split["validation_fraction"], split["outer_test_fraction"])
        == (0.8, 0.1, 0.1),
        "split_fractions",
    )
    _require(split["minimum_primary_components"] == 400, "primary_floor")
    _require(split["minimum_validation_components"] == 40, "validation_floor")
    _require(split["minimum_outer_test_components"] == 40, "outer_floor")
    for key in (
        "all_timesteps_follow_geometry_component",
        "validation_only_model_selection",
        "outer_test_sealed",
        "private_component_manifest",
        "public_split_digests_only",
    ):
        _require(split[key] is True, key)

    output = contract["output_contract"]
    for key in (
        "atomic_writes",
        "case_ids_and_component_members_private",
        "raw_logs_private",
        "absolute_paths_private",
    ):
        _require(output[key] is True, key)
    _require(output["source_object_mutated_or_deleted"] is False, "source_mutation")

    execution = contract["execution"]
    _require(execution["server"] == "introai9" and execution["scheduler"] == "PBS", "server")
    _require(execution["queue"] == "coss_agpu", "queue")
    _require((execution["ncpus"], execution["memory_gb"], execution["ngpus"]) == (4, 64, 0), "resources")
    _require(execution["walltime"] == "02:00:00", "walltime")
    _require(execution["maximum_pbs_attempts"] == 1, "attempt_budget")
    _require(execution["rerun_after_any_outcome"] is False, "rerun")
    _require(execution["login_node_gpu_allowed"] is False, "login_node_gpu")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")

    consequence = contract["completion_consequence"]
    _require(consequence["gate_pass_permits_private_split_freeze"] is True, "split_freeze")
    _require(
        consequence["gate_pass_permits_registration_of_field_audit_and_bounded_development"] is True,
        "next_registration",
    )
    _require(consequence["failure_closes_d5_without_repair"] is True, "fail_close")
    _require(consequence["scientific_verdict"] is None, "scientific_verdict")
    for key in (
        "permits_unregistered_field_read",
        "permits_immediate_gpu_training",
        "permits_validation_or_outer_test_access",
        "permits_scientific_p0_or_paper_result",
    ):
        _require(consequence[key] is False, key)

    activation = contract["activation_requirements"]
    for key in (
        "explicit_human_selection",
        "fresh_registered_config",
        "quality_passed_public_source",
        "clean_introai9_checkout",
        "private_activation_manifest",
        "source_size_and_sha256_reverified_in_job",
    ):
        _require(activation[key] is True, key)
    _require(activation["draft_file_mutated"] is False, "draft_mutation")

    authorization = contract["authorization"]
    for key in (
        "register_d5",
        "read_processed_ghd_values",
        "freeze_private_split_if_gate_passes",
        "submit_single_cpu_pbs",
        "monitor_single_cpu_pbs",
    ):
        _require(authorization[key] is True, key)
    for key in (
        "read_field_values",
        "scientific_p0",
        "method_or_architecture",
        "gpu_training",
        "validation_or_test",
        "outer_test",
        "paper_result_or_claim",
    ):
        _require(authorization[key] is False, key)


class _DisjointSet:
    def __init__(self, count: int) -> None:
        self.parent = list(range(count))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def _case_digest(case_ids: Sequence[str]) -> str:
    payload = json.dumps(list(case_ids), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _split_digest(case_ids: Sequence[str]) -> str:
    payload = json.dumps(sorted(case_ids), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _component_digest(case_ids: Sequence[str], salt: str) -> str:
    payload = json.dumps(sorted(case_ids), ensure_ascii=False, separators=(",", ":"))
    encoded = (salt + "\0" + payload).encode("utf-8")
    return hashlib.blake2b(encoded, digest_size=32).hexdigest()


def _float32_row_sha256(row: Any) -> str:
    values = [float(value) for value in row.tolist()]
    packed = struct.pack(f"<{len(values)}f", *values)
    return hashlib.sha256(packed).hexdigest()


def _format_components(
    components: Sequence[Sequence[int]], case_ids: Sequence[str], salt: str
) -> list[dict[str, Any]]:
    return [
        {
            "component_digest": _component_digest([case_ids[index] for index in members], salt),
            "case_ids": [case_ids[index] for index in members],
            "case_count": len(members),
        }
        for members in components
    ]


def audit_loaded_geometry_tokens(
    contract: Mapping[str, Any],
    case_ids: Sequence[str],
    mesh_case_ids: Sequence[str],
    ghd: Any,
    torch: Any,
    *,
    source_identity_reverified: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Group an already loaded GHD matrix without touching any field tensor."""

    validate_contract(contract)
    ids = [str(item) for item in case_ids]
    mesh_ids = [str(item) for item in mesh_case_ids]
    _require(len(ids) == len(mesh_ids), "case_mesh_count")
    _require(len(set(ids)) == len(ids) and all(ids), "case_id_integrity")
    _require(ids == mesh_ids, "case_mesh_order")
    _require(hasattr(ghd, "shape") and hasattr(ghd, "dtype"), "ghd_tensor")
    _require(len(ghd.shape) == 2, "ghd_rank")
    _require(int(ghd.shape[0]) == len(ids), "ghd_case_alignment")
    _require(str(ghd.dtype) == contract["geometry_token_contract"]["expected_ghd_dtype"], "ghd_dtype")

    matrix = ghd.detach().to(device="cpu").contiguous()
    _require(bool(torch.isfinite(matrix).all().item()), "ghd_nonfinite")
    exact_hashes = [_float32_row_sha256(matrix[index]) for index in range(len(ids))]
    exact_members: dict[str, list[int]] = defaultdict(list)
    for index, digest in enumerate(exact_hashes):
        exact_members[digest].append(index)

    dsu = _DisjointSet(len(ids))
    for members in exact_members.values():
        for member in members[1:]:
            dsu.union(members[0], member)

    tolerance = contract["geometry_token_contract"]["numerical_equivalence"]
    max_abs_limit = float(tolerance["max_abs"])
    rms_limit = float(tolerance["rms"])
    block_rows = int(tolerance["pairwise_block_rows"])
    matrix64 = matrix.to(dtype=torch.float64)
    numerical_edges = 0
    for start in range(0, len(ids), block_rows):
        stop = min(start + block_rows, len(ids))
        difference = torch.abs(matrix64[start:stop, None, :] - matrix64[None, :, :])
        max_abs = difference.amax(dim=2)
        rms = torch.sqrt(torch.mean(difference * difference, dim=2))
        global_left = torch.arange(start, stop, dtype=torch.int64)[:, None]
        right = torch.arange(len(ids), dtype=torch.int64)[None, :]
        close = (max_abs <= max_abs_limit) & (rms <= rms_limit) & (right > global_left)
        for local_left, right_index in torch.nonzero(close, as_tuple=False).tolist():
            left_index = start + int(local_left)
            right_index = int(right_index)
            if exact_hashes[left_index] == exact_hashes[right_index]:
                continue
            dsu.union(left_index, right_index)
            numerical_edges += 1

    component_map: dict[int, list[int]] = defaultdict(list)
    for index in range(len(ids)):
        component_map[dsu.find(index)].append(index)
    all_components = sorted(component_map.values(), key=lambda members: members[0])

    primary_pattern = re.compile(contract["geometry_token_contract"]["primary_case_regex"])
    primary_components: list[list[int]] = []
    auxiliary_components: list[list[int]] = []
    mixed_component_count = 0
    for members in all_components:
        primary_flags = [bool(primary_pattern.fullmatch(ids[index])) for index in members]
        if all(primary_flags):
            primary_components.append(members)
        else:
            auxiliary_components.append(members)
            mixed_component_count += int(any(primary_flags))

    split_contract = contract["split_contract"]
    salt = split_contract["fixed_salt"]
    ordered_primary = sorted(
        primary_components,
        key=lambda members: _component_digest([ids[index] for index in members], salt),
    )
    component_count = len(ordered_primary)
    train_count = round(split_contract["train_fraction"] * component_count)
    validation_count = round(split_contract["validation_fraction"] * component_count)
    train_components = ordered_primary[:train_count]
    validation_components = ordered_primary[train_count : train_count + validation_count]
    outer_components = ordered_primary[train_count + validation_count :]

    def flatten(groups: Sequence[Sequence[int]]) -> list[str]:
        return [ids[index] for members in groups for index in members]

    train_ids = flatten(train_components)
    validation_ids = flatten(validation_components)
    outer_ids = flatten(outer_components)
    auxiliary_ids = flatten(auxiliary_components)
    assigned_ids = train_ids + validation_ids + outer_ids + auxiliary_ids
    _require(len(assigned_ids) == len(ids) and set(assigned_ids) == set(ids), "assignment_partition")
    _require(not (set(train_ids) & set(validation_ids)), "train_validation_overlap")
    _require(not (set(train_ids) & set(outer_ids)), "train_outer_overlap")
    _require(not (set(validation_ids) & set(outer_ids)), "validation_outer_overlap")

    observed_shape = [int(value) for value in matrix.shape]
    gate_reasons: list[str] = []
    if len(ids) != contract["geometry_token_contract"]["expected_case_count"]:
        gate_reasons.append("case_count")
    if observed_shape != contract["geometry_token_contract"]["expected_ghd_shape"]:
        gate_reasons.append("ghd_shape")
    if component_count < split_contract["minimum_primary_components"]:
        gate_reasons.append("primary_component_floor")
    if len(validation_components) < split_contract["minimum_validation_components"]:
        gate_reasons.append("validation_component_floor")
    if len(outer_components) < split_contract["minimum_outer_test_components"]:
        gate_reasons.append("outer_test_component_floor")
    if source_identity_reverified and _case_digest(ids) != contract["source"]["d4_ordered_case_id_sha256"]:
        gate_reasons.append("d4_ordered_case_identity")
    gate_pass = not gate_reasons

    private_manifest = {
        "schema_version": "aurora.aneug_processed_v4_d5.private_grouping_manifest.v1",
        "protocol_id": contract["protocol_id"],
        "source_identity_reverified": source_identity_reverified,
        "ordered_case_id_sha256": _case_digest(ids),
        "split_frozen": gate_pass,
        "gate_reasons": gate_reasons,
        "train_components": _format_components(train_components, ids, salt),
        "validation_components": _format_components(validation_components, ids, salt),
        "outer_test_components": _format_components(outer_components, ids, salt),
        "auxiliary_components": _format_components(auxiliary_components, ids, salt),
        "all_case_ids_private": True,
        "unit_is_patient_or_site": False,
    }
    public_result = {
        "schema_version": "aurora.aneug_processed_v4_d5.public_ghd_component_result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "complete_gate_pass" if gate_pass else "complete_gate_fail",
        "source_identity_reverified": source_identity_reverified,
        "case_count": len(ids),
        "ghd_shape": observed_shape,
        "ghd_dtype": str(matrix.dtype),
        "finite_row_count": len(ids),
        "exact_duplicate_component_count": sum(len(members) > 1 for members in exact_members.values()),
        "numerical_equivalence_edge_count": numerical_edges,
        "all_geometry_component_count": len(all_components),
        "maximum_geometry_component_size": max((len(members) for members in all_components), default=0),
        "primary_component_count": component_count,
        "auxiliary_component_count": len(auxiliary_components),
        "auxiliary_case_count": len(auxiliary_ids),
        "mixed_primary_auxiliary_component_count": mixed_component_count,
        "train_component_count": len(train_components),
        "validation_component_count": len(validation_components),
        "outer_test_component_count": len(outer_components),
        "train_case_count": len(train_ids),
        "validation_case_count": len(validation_ids),
        "outer_test_case_count": len(outer_ids),
        "train_case_digest": _split_digest(train_ids),
        "validation_case_digest": _split_digest(validation_ids),
        "outer_test_case_digest": _split_digest(outer_ids),
        "auxiliary_case_digest": _split_digest(auxiliary_ids),
        "gate_pass": gate_pass,
        "gate_reasons": gate_reasons,
        "private_split_frozen": gate_pass,
        "unit": "synthetic_geometry_component_not_patient",
        "all_timesteps_follow_geometry_component": True,
        "case_ids_public": False,
        "external_geometry_payload_read": False,
        "registered_field_values_read": False,
        "mesh_connectivity_values_read": False,
        "scientific_field_metric_computed": False,
        "scientific_verdict": None,
    }
    serialized_public = json.dumps(public_result, ensure_ascii=False, sort_keys=True)
    for case_id in ids:
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


def run_audit(
    contract: Mapping[str, Any],
    transient_path: Path,
    public_result_path: Path,
    private_manifest_path: Path,
    torch: Any,
) -> dict[str, Any]:
    identity = contract["source"]["transient"]
    _require(transient_path.is_file(), "missing_transient")
    _require(transient_path.stat().st_size == identity["bytes"], "transient_size")
    _require(file_sha256(transient_path) == identity["sha256"], "transient_sha256")
    transient = safe_torch_load(transient_path, torch)
    _require(isinstance(transient, Mapping), "transient_mapping")
    _require({"registered_data_list", "mesh_data"}.issubset(transient), "transient_root_keys")
    cases = transient["registered_data_list"]
    mesh = transient["mesh_data"]
    _require(isinstance(cases, Sequence) and not isinstance(cases, (str, bytes)), "case_sequence")
    _require(isinstance(mesh, Mapping) and {"cases", "ghd"}.issubset(mesh), "mesh_keys")
    case_ids: list[str] = []
    for case in cases:
        _require(isinstance(case, Mapping) and "case" in case, "case_metadata")
        case_ids.append(str(case["case"]))
    mesh_case_ids = [str(item) for item in mesh["cases"]]
    _require(len(case_ids) == contract["geometry_token_contract"]["expected_case_count"], "registered_case_count")
    _require(
        [int(value) for value in mesh["ghd"].shape]
        == contract["geometry_token_contract"]["expected_ghd_shape"],
        "registered_ghd_shape",
    )
    _require(_case_digest(case_ids) == contract["source"]["d4_ordered_case_id_sha256"], "d4_ordered_case_identity")
    public, private = audit_loaded_geometry_tokens(
        contract,
        case_ids,
        mesh_case_ids,
        mesh["ghd"],
        torch,
        source_identity_reverified=True,
    )
    _atomic_json(private_manifest_path, private)
    _atomic_json(public_result_path, public)
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--transient", type=Path, required=True)
    parser.add_argument("--public-result", type=Path, required=True)
    parser.add_argument("--private-grouping-manifest", type=Path, required=True)
    args = parser.parse_args()
    contract = load_contract(args.config)
    import torch

    result = run_audit(
        contract,
        args.transient,
        args.public_result,
        args.private_grouping_manifest,
        torch,
    )
    print(
        "D5 GHD component audit complete; "
        f"gate_pass={str(result['gate_pass']).lower()}; scientific verdict is null"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
