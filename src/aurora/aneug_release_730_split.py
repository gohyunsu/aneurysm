"""Outcome-blind split construction for the complete AneuG-Flow release.

The processed v5 object contains 809 entries, whereas the pinned public
transient release contains 730 case directories.  This module intersects the
two identities, reads only the case-aligned 432-D GHD geometry descriptor,
keeps exact and fixed-tolerance geometry copies together, and constructs a
fresh 80/10/10 split from a private keyed ordering.  It never indexes a
registered field tensor.
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
from aurora.aneug_release_730_protocol import load_config
class Release730SplitError(RuntimeError):
    """Raised when source identity or split invariants are not satisfied."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise Release730SplitError(label)


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


def _canonical_digest(case_ids: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(sorted(case_ids)).encode("utf-8")).hexdigest()


def _ordered_digest(case_ids: Sequence[str]) -> str:
    encoded = json.dumps(list(case_ids), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _row_digest(row: Any) -> str:
    values = [float(value) for value in row.tolist()]
    return hashlib.sha256(struct.pack(f"<{len(values)}f", *values)).hexdigest()


def _component_digest(case_ids: Sequence[str], split_key: bytes) -> str:
    encoded = json.dumps(sorted(case_ids), ensure_ascii=False, separators=(",", ":"))
    return hashlib.blake2b(encoded.encode("utf-8"), key=split_key, digest_size=32).hexdigest()


def _choose_to_target(
    components: Sequence[Sequence[int]], target_cases: int
) -> tuple[list[list[int]], list[list[int]], bool]:
    """Choose a deterministic subset whose case count is at or nearest below target."""

    reachable: dict[int, tuple[int, ...]] = {0: ()}
    for index, component in enumerate(components):
        size = len(component)
        for total, chosen in sorted(reachable.items(), reverse=True):
            candidate = total + size
            if candidate <= target_cases and candidate not in reachable:
                reachable[candidate] = chosen + (index,)
    achieved = max(reachable)
    selected_indices = set(reachable[achieved])
    selected = [list(component) for index, component in enumerate(components) if index in selected_indices]
    remainder = [list(component) for index, component in enumerate(components) if index not in selected_indices]
    return selected, remainder, achieved == target_cases


def build_grouped_split(
    case_ids: Sequence[str],
    mesh_case_ids: Sequence[str],
    ghd: Any,
    release_case_ids: Sequence[str],
    split_key: bytes,
    torch: Any,
    *,
    validation_target: int = 73,
    test_target: int = 73,
    max_abs_limit: float = 1.0e-6,
    rms_limit: float = 1.0e-7,
    block_rows: int = 32,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build a geometry-component split without reading any field value."""

    ids = [str(value) for value in case_ids]
    mesh_ids = [str(value) for value in mesh_case_ids]
    release_ids = sorted(str(value) for value in release_case_ids)
    _require(ids == mesh_ids, "mesh_case_order")
    _require(len(ids) == len(set(ids)) == 809, "processed_case_identity")
    _require(len(release_ids) == len(set(release_ids)) == 730, "release_case_identity")
    _require(all(re.fullmatch(r"stable_[0-9]+", value) for value in release_ids), "release_case_format")
    release_set = set(release_ids)
    _require(release_set.issubset(ids), "release_case_missing_from_v5")
    _require(len(set(ids) - release_set) == 79, "processed_extra_count")
    _require(isinstance(split_key, bytes) and len(split_key) == 32, "split_key")
    _require(hasattr(ghd, "shape") and len(ghd.shape) == 2, "ghd_rank")
    _require(tuple(int(value) for value in ghd.shape) == (809, 432), "ghd_shape")
    _require(str(ghd.dtype) == "torch.float32", "ghd_dtype")

    index_by_id = {case_id: index for index, case_id in enumerate(ids)}
    selected_ids = [case_id for case_id in ids if case_id in release_set]
    selected_indices = torch.tensor(
        [index_by_id[case_id] for case_id in selected_ids], dtype=torch.int64
    )
    matrix = ghd.index_select(0, selected_indices).detach().cpu().contiguous()
    _require(bool(torch.isfinite(matrix).all().item()), "ghd_nonfinite")

    exact_hashes = [_row_digest(matrix[index]) for index in range(len(selected_ids))]
    exact_members: dict[str, list[int]] = defaultdict(list)
    for index, digest in enumerate(exact_hashes):
        exact_members[digest].append(index)
    dsu = _DisjointSet(len(selected_ids))
    for members in exact_members.values():
        for member in members[1:]:
            dsu.union(members[0], member)

    matrix64 = matrix.to(torch.float64)
    numerical_edges = 0
    for start in range(0, len(selected_ids), block_rows):
        stop = min(start + block_rows, len(selected_ids))
        difference = torch.abs(matrix64[start:stop, None, :] - matrix64[None, :, :])
        max_abs = difference.amax(dim=2)
        rms = torch.sqrt(torch.mean(difference.square(), dim=2))
        left = torch.arange(start, stop, dtype=torch.int64)[:, None]
        right = torch.arange(len(selected_ids), dtype=torch.int64)[None, :]
        close = (max_abs <= max_abs_limit) & (rms <= rms_limit) & (right > left)
        for local_left, right_index in torch.nonzero(close, as_tuple=False).tolist():
            left_index = start + int(local_left)
            right_index = int(right_index)
            if exact_hashes[left_index] != exact_hashes[right_index]:
                numerical_edges += 1
            dsu.union(left_index, right_index)

    component_map: dict[int, list[int]] = defaultdict(list)
    for index in range(len(selected_ids)):
        component_map[dsu.find(index)].append(index)
    components = list(component_map.values())
    ordered = sorted(
        components,
        key=lambda members: _component_digest(
            [selected_ids[index] for index in members], split_key
        ),
    )
    validation_components, remainder, validation_exact = _choose_to_target(
        ordered, validation_target
    )
    test_components, train_components, test_exact = _choose_to_target(
        remainder, test_target
    )

    def flatten(groups: Sequence[Sequence[int]]) -> list[str]:
        return [selected_ids[index] for members in groups for index in members]

    train_ids = flatten(train_components)
    validation_ids = flatten(validation_components)
    test_ids = flatten(test_components)
    assigned = train_ids + validation_ids + test_ids
    _require(len(assigned) == 730 and set(assigned) == release_set, "split_partition")
    _require(not (set(train_ids) & set(validation_ids)), "train_validation_overlap")
    _require(not (set(train_ids) & set(test_ids)), "train_test_overlap")
    _require(not (set(validation_ids) & set(test_ids)), "validation_test_overlap")

    def private_components(groups: Sequence[Sequence[int]]) -> list[dict[str, Any]]:
        return [
            {
                "component_digest": _component_digest(
                    [selected_ids[index] for index in members], split_key
                ),
                "case_ids": [selected_ids[index] for index in members],
                "case_count": len(members),
            }
            for members in groups
        ]

    split_key_sha256 = hashlib.sha256(split_key).hexdigest()
    private = {
        "schema_version": "aurora.aneug_release_730.private_split.v1",
        "unit": "synthetic_geometry_case_or_geometry_duplicate_component_not_patient",
        "release_case_ids": release_ids,
        "processed_extra_case_ids": sorted(set(ids) - release_set),
        "split_key_hex": split_key.hex(),
        "split_key_sha256": split_key_sha256,
        "train_components": private_components(train_components),
        "validation_components": private_components(validation_components),
        "test_components": private_components(test_components),
        "test_opened": False,
        "registered_field_values_read": False,
    }
    public = {
        "schema_version": "aurora.aneug_release_730.public_split_result.v1",
        "status": "complete",
        "processed_case_count": len(ids),
        "release_case_count": len(release_ids),
        "processed_extra_case_count": len(set(ids) - release_set),
        "release_case_id_sha256": _canonical_digest(release_ids),
        "processed_ordered_case_id_sha256": _ordered_digest(ids),
        "ghd_shape": [int(value) for value in matrix.shape],
        "ghd_dtype": str(matrix.dtype),
        "geometry_component_count": len(components),
        "exact_duplicate_component_count": sum(
            len(members) > 1 for members in exact_members.values()
        ),
        "numerical_equivalence_edge_count": numerical_edges,
        "maximum_component_size": max(len(component) for component in components),
        "train_component_count": len(train_components),
        "validation_component_count": len(validation_components),
        "test_component_count": len(test_components),
        "train_case_count": len(train_ids),
        "validation_case_count": len(validation_ids),
        "test_case_count": len(test_ids),
        "validation_target_exact": validation_exact,
        "test_target_exact": test_exact,
        "train_case_digest": _canonical_digest(train_ids),
        "validation_case_digest": _canonical_digest(validation_ids),
        "test_case_digest": _canonical_digest(test_ids),
        "split_key_sha256": split_key_sha256,
        "case_ids_public": False,
        "field_or_model_result_used_for_split": False,
        "registered_field_values_read": False,
        "test_opened": False,
        "scientific_performance_verdict": None,
    }
    serialized = json.dumps(public, sort_keys=True)
    _require(not any(case_id in serialized for case_id in ids), "case_id_leak")
    return public, private


def _load_tsv(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "\t" in line:
            key, value = line.split("\t", 1)
            rows[key] = value
    return rows


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    _require(not path.exists() and not temporary.exists(), f"output_exists:{path.name}")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _schema_record_matches(schema: Mapping[str, Any]) -> bool:
    """Match the exact field names emitted by the pinned v5 schema audit."""

    return bool(
        schema.get("schema_pass") is True
        and schema.get("registered_case_count") == 809
        and schema.get("mesh_case_count") == 809
        and schema.get("tensor_shape") == [80, 13_902, 9]
        and schema.get("mesh_order_exact") is True
    )


def _load_release_manifest(
    path: Path, config: Mapping[str, Any]
) -> tuple[list[str], str]:
    expected = config["source"]["release_case_manifest"]
    manifest_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    _require(manifest_sha256 == expected["sha256"], "release_manifest_identity")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    _require(
        manifest.get("schema_version") == "aurora.aneug_release_case_manifest.v1"
        and manifest.get("dataset_repository") == "whding123/AneuG-Flow"
        and manifest.get("dataset_revision") == config["source"]["dataset_revision"]
        and manifest.get("source_path") == "transient_data",
        "release_manifest_source",
    )
    release_ids = manifest.get("case_ids")
    _require(
        isinstance(release_ids, list)
        and len(release_ids) == expected["case_count"] == 730
        and len(set(release_ids)) == 730
        and all(re.fullmatch(r"stable_[0-9]+", value) for value in release_ids),
        "release_manifest_cases",
    )
    _require(
        _canonical_digest(release_ids)
        == manifest.get("sorted_case_id_sha256")
        == config["source"]["release_tree_case_id_sha256"],
        "release_manifest_digest",
    )
    return sorted(release_ids), manifest_sha256


def run_split(
    config_path: Path,
    normalization_result_path: Path,
    source_path: Path,
    finalize_record_path: Path,
    schema_record_path: Path,
    release_manifest_path: Path,
    split_key_path: Path,
    public_result_path: Path,
    private_manifest_path: Path,
    torch: Any,
) -> dict[str, Any]:
    config = load_config(config_path)
    normalization = config["normalization_provenance"]
    normalization_result_sha256 = hashlib.sha256(
        normalization_result_path.read_bytes()
    ).hexdigest()
    _require(
        normalization_result_sha256 == normalization["audit_result_sha256"],
        "normalization_result_identity",
    )
    normalization_result = json.loads(
        normalization_result_path.read_text(encoding="utf-8")
    )
    _require(
        normalization_result.get("status") == "complete_strong_overlap_linkage"
        and normalization_result.get("overlap_case_count") == 578
        and normalization_result.get("tensor_exact_equal_overlap_count") == 578
        and normalization_result.get("tensor_mismatch_overlap_count") == 0
        and normalization_result.get("maximum_tensor_mismatch_abs") == 0.0
        and normalization_result.get("ghd_exact_equal_overlap_count") == 578
        and normalization_result.get("shared_hierarchy_equal_item_count")
        == normalization_result.get("shared_hierarchy_item_count")
        == 8
        and normalization_result.get("steady_norm_fingerprint_sha256")
        == normalization["steady_norm_fingerprint_sha256"]
        and normalization_result.get("test_outcome_read") is False,
        "normalization_result",
    )
    source = config["source"]["processed_v5"]
    _require(source_path.is_file(), "source_missing")
    _require(source_path.stat().st_size == source["bytes"], "source_size")
    finalize_record_sha256 = hashlib.sha256(finalize_record_path.read_bytes()).hexdigest()
    _require(
        finalize_record_sha256
        == config["verified_introai9_asset"]["finalize_record_sha256"],
        "finalize_record_identity",
    )
    finalize = _load_tsv(finalize_record_path)
    _require(
        finalize.get("assembled_bytes") == str(source["bytes"])
        and finalize.get("sha256") == source["sha256"]
        and finalize.get("official_match") == "true"
        and finalize.get("exit_code") == "0",
        "finalize_record",
    )
    schema_record_sha256 = hashlib.sha256(schema_record_path.read_bytes()).hexdigest()
    _require(
        schema_record_sha256 == config["verified_introai9_asset"]["schema_record_sha256"],
        "schema_record_identity",
    )
    schema = json.loads(schema_record_path.read_text(encoding="utf-8"))
    _require(_schema_record_matches(schema), "schema_record")
    release_ids, release_manifest_sha256 = _load_release_manifest(
        release_manifest_path, config
    )
    split_key_text = split_key_path.read_text(encoding="utf-8").strip()
    _require(bool(re.fullmatch(r"[0-9a-f]{64}", split_key_text)), "split_key_format")

    transient = safe_torch_load(source_path, torch)
    _require(isinstance(transient, Mapping), "source_mapping")
    _require({"registered_data_list", "mesh_data"}.issubset(transient), "source_keys")
    cases, mesh = transient["registered_data_list"], transient["mesh_data"]
    _require(isinstance(cases, Sequence), "case_sequence")
    _require(isinstance(mesh, Mapping) and {"cases", "ghd"}.issubset(mesh), "mesh_keys")
    case_ids = [str(case["case"]) for case in cases]
    mesh_case_ids = [str(case_id) for case_id in mesh["cases"]]
    public, private = build_grouped_split(
        case_ids,
        mesh_case_ids,
        mesh["ghd"],
        release_ids,
        bytes.fromhex(split_key_text),
        torch,
        validation_target=config["split_design"]["singleton_target_counts"]["validation"],
        test_target=config["split_design"]["singleton_target_counts"]["test"],
        max_abs_limit=config["split_design"]["near_duplicate_max_abs"],
        rms_limit=config["split_design"]["near_duplicate_rms"],
    )
    public["source_finalize_record_sha256"] = finalize_record_sha256
    public["source_schema_record_sha256"] = schema_record_sha256
    public["normalization_result_sha256"] = normalization_result_sha256
    public["release_manifest_sha256"] = release_manifest_sha256
    private["source_path"] = str(source_path)
    private["source_sha256"] = source["sha256"]
    private["release_manifest_sha256"] = release_manifest_sha256
    _atomic_json(private_manifest_path, private)
    _atomic_json(public_result_path, public)
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--normalization-result", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--finalize-record", type=Path, required=True)
    parser.add_argument("--schema-record", type=Path, required=True)
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--split-key", type=Path, required=True)
    parser.add_argument("--public-result", type=Path, required=True)
    parser.add_argument("--private-manifest", type=Path, required=True)
    arguments = parser.parse_args()
    import torch

    result = run_split(
        arguments.config,
        arguments.normalization_result,
        arguments.source,
        arguments.finalize_record,
        arguments.schema_record,
        arguments.release_manifest,
        arguments.split_key,
        arguments.public_result,
        arguments.private_manifest,
        torch,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
