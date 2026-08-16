"""Dormant D5 geometry-token grouping utilities for AneuG processed v4.

This module deliberately has no dataset loader, file writer, PBS entry point or
activation path.  It validates an unselected contract and provides a pure
in-memory evaluator for synthetic falsification tests.  A selected D5 must be
registered as a fresh version; this draft may never be mutated into one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


class D5DraftContractError(RuntimeError):
    """Raised when the dormant D5 scope or privacy boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D5DraftContractError(reason)


def load_draft_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_draft_contract(contract)
    return contract


def validate_draft_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version") == "aurora.aneug_processed_v4_d5_draft.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_geometry_token_grouping_d5_draft",
        "protocol_id",
    )
    _require(contract.get("status") == "draft_unselected_non_executable", "draft_status")
    selection = contract["human_selection"]
    _require(selection["explicitly_selected"] is False, "human_selection")
    _require(selection["selected_on"] is None and selection["selection"] is None, "selection")

    source = contract["source"]
    _require(
        source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "dataset_revision",
    )
    _require(
        source["code_revision"] == "4a090a0f12538deef6fcea88b81afe78ce38152e",
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

    d4 = contract["closed_d4_boundary"]
    _require(d4["status"] == "closed_complete_descriptive_metadata_census", "d4_status")
    _require(d4["registered_cases"] == 578 and d4["ghd_shape"] == [578, 432], "d4_shape")
    _require(d4["repair_or_rerun"] is False and d4["d5_relabels_d4"] is False, "d4_immutable")

    builder = contract["official_builder_semantics"]
    for key in (
        "case_directories_selected_from_transient_root",
        "ghd_loaded_from_each_transient_case_checkpoint",
        "mesh_cases_and_ghd_rows_share_builder_order",
    ):
        _require(builder[key] is True, key)
    _require(builder["external_geometry_directory_join_required_for_processed_input"] is False, "external_join")
    _require(builder["generator_parent_or_patient_lineage_asserted"] is False, "lineage_claim")

    geometry = contract["geometry_token_contract"]
    _require(geometry["weights_only"] is True and geometry["mmap"] is True, "safe_load")
    _require(geometry["map_location"] == "cpu", "cpu_load")
    _require(geometry["allowed_value_read"] == "mesh_data.ghd_only", "allowed_value_read")
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
    _require(geometry["expected_case_count"] == 578, "expected_case_count")
    _require(geometry["expected_ghd_columns"] == 432, "expected_ghd_columns")
    _require(geometry["require_case_mesh_order_exact"] is True, "mesh_order")
    _require(geometry["require_all_ghd_values_finite"] is True, "finite")
    _require(geometry["primary_case_regex"] == "^stable_[0-9]+$", "primary_regex")
    tolerance = geometry["numerical_equivalence"]
    _require(tolerance == {"max_abs": 0.000001, "rms": 0.0000001}, "tolerance")

    split = contract["prospective_split_if_selected_and_feasible"]
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
        "private_split_manifest",
        "public_split_digests_only",
    ):
        _require(split[key] is True, key)

    envelope = contract["execution_envelope_if_selected_in_fresh_version"]
    _require(envelope["server"] == "introai9", "server")
    _require(envelope["ncpus"] == 4 and envelope["memory_gb"] == 64, "cpu_memory")
    _require(envelope["ngpus"] == 0, "gpu")
    _require(envelope["maximum_pbs_attempts"] == 1, "attempt_budget")
    _require(envelope["rerun_after_any_outcome"] is False, "rerun")
    _require(envelope["excluded_server"] == "junjinyong", "excluded_server")

    activation = contract["activation_requirements"]
    _require(activation["explicit_human_selection"] is True, "activation_selection")
    _require(activation["fresh_registered_config"] is True, "fresh_config")
    _require(activation["draft_file_mutation_into_executable_contract"] is False, "draft_mutation")
    _require(all(value is False for value in contract["authorization"].values()), "authorization")


def assert_execution_authorized(contract: Mapping[str, Any]) -> None:
    """Fail closed because this source only accepts the dormant draft."""

    validate_draft_contract(contract)
    raise D5DraftContractError("draft_non_executable_requires_fresh_human_selected_version")


class _DisjointSet:
    def __init__(self, count: int) -> None:
        self.parent = list(range(count))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def _float32_bytes(row: Sequence[float]) -> bytes:
    return b"".join(struct.pack("<f", float(value)) for value in row)


def _component_digest(case_ids: Sequence[str], salt: str) -> str:
    payload = json.dumps(sorted(case_ids), ensure_ascii=False, separators=(",", ":"))
    return hashlib.blake2b((salt + "\0" + payload).encode("utf-8"), digest_size=32).hexdigest()


def _split_digest(case_ids: Sequence[str]) -> str:
    payload = json.dumps(sorted(case_ids), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def audit_loaded_geometry_tokens(
    contract: Mapping[str, Any],
    case_ids: Sequence[str],
    mesh_case_ids: Sequence[str],
    ghd_rows: Sequence[Sequence[float]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Audit already loaded geometry tokens; never load files or field values."""

    validate_draft_contract(contract)
    ids = [str(item) for item in case_ids]
    mesh_ids = [str(item) for item in mesh_case_ids]
    rows = [tuple(float(value) for value in row) for row in ghd_rows]
    _require(len(ids) == len(mesh_ids) == len(rows), "row_count_alignment")
    _require(len(set(ids)) == len(ids) and all(ids), "case_id_integrity")
    _require(ids == mesh_ids, "case_mesh_order")
    column_counts = sorted({len(row) for row in rows})
    _require(len(column_counts) == 1, "ghd_rectangular")

    finite_rows = [all(math.isfinite(value) for value in row) for row in rows]
    exact_hashes = [hashlib.sha256(_float32_bytes(row)).hexdigest() for row in rows]
    dsu = _DisjointSet(len(rows))
    exact_members: dict[str, list[int]] = defaultdict(list)
    for index, digest in enumerate(exact_hashes):
        exact_members[digest].append(index)
    for members in exact_members.values():
        for member in members[1:]:
            dsu.union(members[0], member)

    tolerance = contract["geometry_token_contract"]["numerical_equivalence"]
    max_abs_limit = float(tolerance["max_abs"])
    rms_limit = float(tolerance["rms"])
    numerical_edges = 0
    for left in range(len(rows)):
        for right in range(left + 1, len(rows)):
            if exact_hashes[left] == exact_hashes[right]:
                continue
            differences = [abs(a - b) for a, b in zip(rows[left], rows[right])]
            if not differences:
                continue
            max_abs = max(differences)
            rms = math.sqrt(sum(value * value for value in differences) / len(differences))
            if max_abs <= max_abs_limit and rms <= rms_limit:
                dsu.union(left, right)
                numerical_edges += 1

    components: dict[int, list[int]] = defaultdict(list)
    for index in range(len(rows)):
        components[dsu.find(index)].append(index)

    primary_pattern = re.compile(contract["geometry_token_contract"]["primary_case_regex"])
    primary_components: list[list[int]] = []
    auxiliary_indices: list[int] = []
    mixed_components = 0
    for members in components.values():
        primary = [index for index in members if primary_pattern.fullmatch(ids[index])]
        auxiliary = [index for index in members if index not in primary]
        if primary and not auxiliary:
            primary_components.append(members)
        else:
            auxiliary_indices.extend(members)
            mixed_components += int(bool(primary and auxiliary))

    split_contract = contract["prospective_split_if_selected_and_feasible"]
    salt = split_contract["fixed_salt"]
    ordered_components = sorted(
        primary_components,
        key=lambda members: _component_digest([ids[index] for index in members], salt),
    )
    component_count = len(ordered_components)
    train_count = round(split_contract["train_fraction"] * component_count)
    validation_count = round(split_contract["validation_fraction"] * component_count)
    train_components = ordered_components[:train_count]
    validation_components = ordered_components[train_count : train_count + validation_count]
    outer_components = ordered_components[train_count + validation_count :]

    def flatten(groups: Sequence[Sequence[int]]) -> list[str]:
        return [ids[index] for group in groups for index in group]

    train_ids = flatten(train_components)
    validation_ids = flatten(validation_components)
    outer_ids = flatten(outer_components)
    auxiliary_ids = [ids[index] for index in auxiliary_indices]

    expected_count = contract["geometry_token_contract"]["expected_case_count"]
    expected_columns = contract["geometry_token_contract"]["expected_ghd_columns"]
    feasible = (
        len(ids) == expected_count
        and column_counts == [expected_columns]
        and all(finite_rows)
        and component_count >= split_contract["minimum_primary_components"]
        and len(validation_components) >= split_contract["minimum_validation_components"]
        and len(outer_components) >= split_contract["minimum_outer_test_components"]
    )

    private_manifest = {
        "schema_version": "aurora.aneug_processed_v4_d5.private_split_draft.v1",
        "draft_only": True,
        "train_case_ids": train_ids,
        "validation_case_ids": validation_ids,
        "outer_test_case_ids": outer_ids,
        "auxiliary_case_ids": auxiliary_ids,
        "case_ids_public": False,
    }
    public_result = {
        "schema_version": "aurora.aneug_processed_v4_d5.public_geometry_token_draft.v1",
        "draft_only": True,
        "case_count": len(ids),
        "ghd_column_counts": column_counts,
        "finite_row_count": sum(finite_rows),
        "exact_duplicate_component_count": sum(len(members) > 1 for members in exact_members.values()),
        "numerical_equivalence_edge_count": numerical_edges,
        "geometry_component_count": len(components),
        "primary_component_count": component_count,
        "auxiliary_case_count": len(auxiliary_ids),
        "mixed_primary_auxiliary_component_count": mixed_components,
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
        "split_feasible_under_draft_contract": feasible,
        "external_geometry_directory_join_used": False,
        "registered_field_values_read": False,
        "scientific_verdict": None,
        "case_ids_public": False,
    }
    serialized = json.dumps(public_result, ensure_ascii=False, sort_keys=True)
    for case_id in ids:
        _require(json.dumps(case_id, ensure_ascii=False) not in serialized, "case_id_leaked_public")
    return public_result, private_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true", required=True)
    args = parser.parse_args()
    load_draft_contract(args.config)
    print("AneuG processed-v4 D5 draft valid · unselected · non-executable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
