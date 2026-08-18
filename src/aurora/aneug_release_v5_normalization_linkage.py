"""Audit processed-v5 normalization lineage through the complete v4 overlap.

This is a data-provenance audit, not a model evaluation. It compares every
overlapping normalized case tensor across official processed v4 and v5 and
binds the separately distributed steady normalization record used by the
official builder. No field statistic or case identifier is emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import file_sha256, safe_torch_load


class AneuGV5NormalizationLinkageError(RuntimeError):
    pass


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise AneuGV5NormalizationLinkageError(label)


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_v5_normalization_linkage.v1",
        "schema_version",
    )
    _require(config.get("status") == "authorized_cpu_audit_pending", "status")
    _require(
        config["source_code"]["commit"]
        == "4a090a0f12538deef6fcea88b81afe78ce38152e",
        "official_code_commit",
    )
    identities = config["inputs"]
    expected_identities = {
        "steady_v4": (
            9_632_510_050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
        "transient_v4": (
            23_744_862_051,
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        ),
        "transient_v5": (
            33_233_856_917,
            "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
        ),
    }
    for role, identity in expected_identities.items():
        _require(
            (identities[role]["bytes"], identities[role]["sha256"]) == identity,
            f"{role}_identity",
        )
    expected = config["expected"]
    _require(
        (
            expected["v4_case_count"],
            expected["v5_case_count"],
            expected["v4_v5_overlap_count"],
            expected["v4_only_count"],
            expected["v5_only_count"],
        )
        == (578, 809, 578, 0, 231),
        "expected_cohort",
    )
    _require(expected["case_tensor_shape"] == [80, 13_902, 9], "tensor_shape")
    _require(expected["compare_every_overlap_case"] is True, "complete_overlap")
    reader = config["reader"]
    _require(
        reader == {
            "weights_only": True,
            "mmap": True,
            "full_file_sha256": True,
            "arbitrary_pickle_globals": False,
        },
        "reader",
    )
    execution = config["execution"]
    _require(
        execution["server"] == "introai9"
        and execution["ngpus"] == 0
        and execution["excluded_server"] == "junjinyong",
        "execution_scope",
    )
    return config


def _case_map(payload: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], Mapping[str, Any]]:
    _require({"registered_data_list", "mesh_data"}.issubset(payload), "transient_root")
    rows = payload["registered_data_list"]
    _require(isinstance(rows, Sequence), "registered_sequence")
    mapped: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        _require(isinstance(row, Mapping), "registered_row")
        case_id = str(row.get("case", ""))
        _require(case_id and case_id not in mapped, "case_identity")
        mapped[case_id] = row
    mesh = payload["mesh_data"]
    _require(isinstance(mesh, Mapping), "mesh_mapping")
    _require([str(value) for value in mesh["cases"]] == list(mapped), "mesh_case_order")
    return mapped, mesh


def _normalization_fingerprint(mean: Any, std: Any) -> str:
    values = [float(value) for value in mean.reshape(-1).tolist()]
    values.extend(float(value) for value in std.reshape(-1).tolist())
    return hashlib.sha256(struct.pack(f"<{len(values)}f", *values)).hexdigest()


def compare_loaded(
    steady: Mapping[str, Any],
    v4: Mapping[str, Any],
    v5: Mapping[str, Any],
    config: Mapping[str, Any],
    torch: Any,
) -> dict[str, Any]:
    labels = list(config["expected"]["labels"])
    _require(isinstance(steady, Mapping), "steady_root")
    _require({"label", "tensor_norm"}.issubset(steady), "steady_schema")
    _require([str(value) for value in steady["label"]] == labels, "steady_labels")
    norm = steady["tensor_norm"]
    _require(isinstance(norm, Mapping) and {"mean", "std"}.issubset(norm), "norm_schema")
    mean = norm["mean"].detach().cpu().to(torch.float32)
    std = norm["std"].detach().cpu().to(torch.float32)
    _require(tuple(mean.shape) == (1, 1, 9) and tuple(std.shape) == (1, 1, 9), "norm_shape")
    _require(
        bool(torch.isfinite(mean).all().item())
        and bool(torch.isfinite(std).all().item())
        and bool((std > 0).all().item()),
        "norm_values",
    )

    v4_cases, v4_mesh = _case_map(v4)
    v5_cases, v5_mesh = _case_map(v5)
    v4_ids, v5_ids = set(v4_cases), set(v5_cases)
    overlap = sorted(v4_ids & v5_ids)
    _require(
        (len(v4_ids), len(v5_ids), len(overlap), len(v4_ids - v5_ids), len(v5_ids - v4_ids))
        == (578, 809, 578, 0, 231),
        "observed_cohort",
    )
    expected_shape = tuple(config["expected"]["case_tensor_shape"])
    tensor_equal_count = 0
    label_equal_count = 0
    tensor_mismatch_count = 0
    maximum_mismatch_abs = 0.0
    for case_id in overlap:
        left, right = v4_cases[case_id], v5_cases[case_id]
        if [str(value) for value in left["labels"]] == labels == [
            str(value) for value in right["labels"]
        ]:
            label_equal_count += 1
        left_tensor, right_tensor = left["tensor"], right["tensor"]
        _require(
            tuple(left_tensor.shape) == expected_shape
            and tuple(right_tensor.shape) == expected_shape,
            "case_tensor_shape",
        )
        _require(left_tensor.dtype == right_tensor.dtype == torch.float32, "case_tensor_dtype")
        if torch.equal(left_tensor, right_tensor):
            tensor_equal_count += 1
        else:
            tensor_mismatch_count += 1
            mismatch = float(torch.max(torch.abs(left_tensor - right_tensor)).item())
            maximum_mismatch_abs = max(maximum_mismatch_abs, mismatch)

    v4_index = {str(value): index for index, value in enumerate(v4_mesh["cases"])}
    v5_index = {str(value): index for index, value in enumerate(v5_mesh["cases"])}
    v4_ghd, v5_ghd = v4_mesh["ghd"], v5_mesh["ghd"]
    _require(tuple(v4_ghd.shape) == (578, 432), "v4_ghd_shape")
    _require(tuple(v5_ghd.shape) == (809, 432), "v5_ghd_shape")
    ghd_equal_count = sum(
        torch.equal(v4_ghd[v4_index[case_id]], v5_ghd[v5_index[case_id]])
        for case_id in overlap
    )
    hierarchy_items = 0
    hierarchy_equal_items = 0
    for key in ("idx_list", "edge_index_list", "faces_list"):
        left_items, right_items = v4_mesh[key], v5_mesh[key]
        _require(len(left_items) == len(right_items), f"{key}_length")
        for left, right in zip(left_items, right_items):
            hierarchy_items += 1
            hierarchy_equal_items += int(torch.equal(left, right))

    strong = (
        label_equal_count == 578
        and tensor_equal_count == 578
        and tensor_mismatch_count == 0
        and ghd_equal_count == 578
        and hierarchy_equal_items == hierarchy_items
    )
    return {
        "schema_version": "aurora.aneug_release_v5_normalization_linkage_result.v1",
        "status": "complete_strong_overlap_linkage" if strong else "complete_linkage_not_supported",
        "v4_case_count": len(v4_ids),
        "v5_case_count": len(v5_ids),
        "overlap_case_count": len(overlap),
        "v4_only_case_count": len(v4_ids - v5_ids),
        "v5_only_case_count": len(v5_ids - v4_ids),
        "label_equal_overlap_count": label_equal_count,
        "tensor_exact_equal_overlap_count": tensor_equal_count,
        "tensor_mismatch_overlap_count": tensor_mismatch_count,
        "maximum_tensor_mismatch_abs": maximum_mismatch_abs,
        "ghd_exact_equal_overlap_count": ghd_equal_count,
        "shared_hierarchy_equal_item_count": hierarchy_equal_items,
        "shared_hierarchy_item_count": hierarchy_items,
        "steady_norm_shape": [list(mean.shape), list(std.shape)],
        "steady_norm_fingerprint_sha256": _normalization_fingerprint(mean, std),
        "overlap_identity_supports_common_preprocessing_lineage": strong,
        "v5_embeds_normalization_metadata": False,
        "v5_only_creator_manifest_available": False,
        "physical_decode_interpretation": (
            "supported_by_official_single_normalizer_builder_and_complete_v4_overlap_identity"
            if strong
            else "not_supported"
        ),
        "case_identifiers_public": False,
        "field_distribution_statistic_computed": False,
        "model_or_performance_metric_computed": False,
        "test_outcome_read": False,
        "scientific_performance_verdict": None,
    }


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    _require(not path.exists() and not temporary.exists(), "output_exists")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def run(
    config_path: Path,
    data_root: Path,
    result_path: Path,
    torch: Any,
) -> dict[str, Any]:
    config = load_config(config_path)
    loaded: dict[str, Any] = {}
    verified_hashes: dict[str, str] = {}
    for role, identity in config["inputs"].items():
        path = data_root / identity["relative_path"]
        _require(path.is_file() and path.stat().st_size == identity["bytes"], f"{role}_file")
        digest = file_sha256(path)
        _require(digest == identity["sha256"], f"{role}_sha256")
        verified_hashes[role] = digest
        loaded[role] = safe_torch_load(path, torch)
    result = compare_loaded(
        loaded["steady_v4"], loaded["transient_v4"], loaded["transient_v5"], config, torch
    )
    result["input_sha256"] = verified_hashes
    _atomic_json(result_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    arguments = parser.parse_args()
    load_config(arguments.config)
    if arguments.validate_only:
        return 0
    _require(arguments.data_root is not None and arguments.result is not None, "arguments")
    import torch

    torch.set_num_threads(4)
    result = run(arguments.config, arguments.data_root, arguments.result, torch)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
