"""Geometry-only leakage audit for AneuG steady supervision.

The paper documents 14,000 steady cases, while the exact processed object
contains 14,392 WSS-labelled geometries.  Both cardinalities are preserved.
Before any of those labels can be used, this module verifies its schema and
compares its case names and 432-D GHD geometry rows with every partition of
the frozen 809-case transient object.  It never indexes either WSS tensor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load


class SteadyOverlapAuditError(RuntimeError):
    """Raised when the exact source or geometry-only audit contract fails."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise SteadyOverlapAuditError(label)


def _sha256_file(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(block_size):
            digest.update(block)
    return digest.hexdigest()


def _canonical_digest(values: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(sorted(values)).encode("utf-8")).hexdigest()


def _row_digest(row: Any) -> str:
    values = [float(value) for value in row.tolist()]
    return hashlib.sha256(struct.pack(f"<{len(values)}f", *values)).hexdigest()


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


def validate_config(payload: dict[str, Any]) -> dict[str, Any]:
    _require(
        payload.get("schema_version")
        == "aurora.aneug_release_730_steady_overlap_audit.v1",
        "schema_version",
    )
    _require(
        payload.get("protocol_id") == "aneug_release_730_steady_overlap_audit_v1",
        "protocol_id",
    )
    _require(payload.get("status") == "prepared_cpu_geometry_only", "status")
    source = payload["source"]
    _require(
        source["dataset_revision"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "dataset_revision",
    )
    _require(
        source["official_code_revision"]
        == "4a090a0f12538deef6fcea88b81afe78ce38152e",
        "official_code_revision",
    )
    _require(
        (source["steady_v4_bytes"], source["steady_v4_sha256"])
        == (
            9_632_510_050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
        "steady_identity",
    )
    _require(
        (source["processed_v5_bytes"], source["processed_v5_sha256"])
        == (
            33_233_856_917,
            "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
        ),
        "transient_identity",
    )
    _require(
        source["public_split_sha256"]
        == "4fa3be7c217c3a84b86f477c90112377fb913f6b0b47b829d684b270555bf991"
        and source["private_split_sha256"]
        == "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f",
        "split_identity",
    )
    schema = payload["schema"]
    _require(
        (
            schema["documented_steady_cases"],
            schema["expected_steady_cases"],
            schema["expected_transient_cases"],
            schema["expected_nodes"],
            schema["expected_channels"],
            schema["expected_ghd_width"],
        )
        == (14_000, 14_392, 809, 13_902, 9, 432),
        "expected_schema",
    )
    _require(
        schema["expected_main_split"]
        == {"train": 584, "validation": 73, "test": 73, "processed_only_extra": 79},
        "split_counts",
    )
    overlap = payload["overlap"]
    _require(overlap["descriptor"] == "raw_float32_ghd_coefficients", "descriptor")
    _require(overlap["exact_row_hash"] == "sha256_little_endian_float32", "row_hash")
    _require(
        overlap["near_max_abs_limit"] == 1.0e-6
        and overlap["near_rms_limit"] == 1.0e-7
        and overlap["steady_block_rows"] == 16,
        "near_contract",
    )
    _require(
        all(
            overlap[key] is True
            for key in (
                "exclude_if_case_id_exact_with_any_transient_partition",
                "exclude_if_ghd_exact_or_near_with_any_transient_partition",
                "exclude_validation_test_and_extra_neighbors_from_training",
            )
        ),
        "exclusion_contract",
    )
    interpretation = payload["interpretation"]
    _require(interpretation["steady_supervision_is_novelty"] is False, "novelty_claim")
    _require(interpretation["rhsia_already_uses_steady_augmentation"] is True, "prior_scope")
    _require(
        interpretation["documented_vs_processed_cardinality_discrepancy"] is True,
        "steady_cardinality_discrepancy",
    )
    _require(interpretation["automatic_model_selection"] is False, "automatic_selection")
    _require(interpretation["absolute_performance_threshold"] is None, "threshold")
    scope = payload["read_scope"]
    _require(
        scope["steady_case_names"] is True
        and scope["steady_ghd_geometry"] is True
        and scope["steady_tensor_metadata_only"] is True
        and scope["transient_case_names"] is True
        and scope["transient_ghd_geometry"] is True,
        "geometry_read_scope",
    )
    _require(
        scope["steady_wss_values"] is False
        and scope["transient_wss_values"] is False
        and scope["locked_test_wss_values"] is False
        and scope["processed_only_extra_wss_values"] is False,
        "field_read_scope",
    )
    execution = payload["execution"]
    _require(execution["server"] == "introai9" and execution["ngpus"] == 0, "runtime")
    _require(execution["requires_fresh_private_activation"] is True, "activation_required")
    _require(execution["public_result_contains_case_ids"] is False, "public_ids")
    _require(execution["private_result_is_append_only"] is True, "append_only")
    return payload


def load_config(path: str | Path) -> dict[str, Any]:
    return validate_config(json.loads(Path(path).read_text(encoding="utf-8")))


def validate_activation(path: Path, config: Mapping[str, Any], expected_commit: str) -> dict[str, Any]:
    activation = json.loads(path.read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_steady_overlap_audit_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(activation.get("public_commit") == expected_commit, "activation_commit")
    _require(activation.get("quality_conclusion") == "success", "activation_quality")
    _require(
        activation.get("authorized_stage") == "single_cpu_geometry_only_overlap_audit",
        "activation_stage",
    )
    _require(activation.get("read_any_wss_value") is False, "activation_field_scope")
    _require(activation.get("use_gpu") is False, "activation_gpu")
    _require(activation.get("test_wss_opened") is False, "activation_test")
    _require(
        activation.get("private_split_sha256")
        == config["source"]["private_split_sha256"],
        "activation_split",
    )
    return activation


def _split_partitions(private_split: Mapping[str, Any]) -> dict[str, list[str]]:
    _require(private_split.get("test_opened") is False, "test_already_open")
    _require(private_split.get("registered_field_values_read") is False, "split_field_read")

    def flatten(name: str) -> list[str]:
        components = private_split.get(f"{name}_components")
        _require(isinstance(components, list), f"missing_{name}_components")
        return [str(case_id) for component in components for case_id in component["case_ids"]]

    return {
        "train": flatten("train"),
        "validation": flatten("validation"),
        "test": flatten("test"),
        "processed_only_extra": [
            str(case_id) for case_id in private_split.get("processed_extra_case_ids", [])
        ],
    }


def audit_geometry_overlap(
    steady_case_names: Sequence[str],
    steady_ghd: Any,
    transient_case_names: Sequence[str],
    transient_ghd: Any,
    partitions: Mapping[str, Sequence[str]],
    torch: Any,
    *,
    expected_steady_cases: int,
    expected_transient_cases: int,
    expected_ghd_width: int,
    expected_partition_counts: Mapping[str, int],
    max_abs_limit: float,
    rms_limit: float,
    block_rows: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return identifier-free public and append-only private overlap records."""

    steady_ids = [str(value) for value in steady_case_names]
    transient_ids = [str(value) for value in transient_case_names]
    _require(
        len(steady_ids) == len(set(steady_ids)) == expected_steady_cases,
        "steady_case_identity",
    )
    _require(
        len(transient_ids) == len(set(transient_ids)) == expected_transient_cases,
        "transient_case_identity",
    )
    steady_matrix = steady_ghd.detach().cpu().reshape(expected_steady_cases, -1).contiguous()
    transient_matrix = transient_ghd.detach().cpu().reshape(expected_transient_cases, -1).contiguous()
    _require(
        tuple(steady_matrix.shape) == (expected_steady_cases, expected_ghd_width)
        and tuple(transient_matrix.shape) == (expected_transient_cases, expected_ghd_width),
        "ghd_shape",
    )
    _require(
        str(steady_matrix.dtype) == str(transient_matrix.dtype) == "torch.float32",
        "ghd_dtype",
    )
    _require(
        bool(torch.isfinite(steady_matrix).all().item())
        and bool(torch.isfinite(transient_matrix).all().item()),
        "ghd_nonfinite",
    )

    partition_by_id: dict[str, str] = {}
    for name in ("train", "validation", "test", "processed_only_extra"):
        values = [str(value) for value in partitions[name]]
        expected = int(expected_partition_counts[name])
        _require(len(values) == len(set(values)) == expected, f"{name}_count")
        for value in values:
            _require(value not in partition_by_id, "partition_overlap")
            partition_by_id[value] = name
    _require(set(partition_by_id) == set(transient_ids), "partition_coverage")

    transient_index = {case_id: index for index, case_id in enumerate(transient_ids)}
    name_pairs = [
        (steady_index, transient_index[case_id])
        for steady_index, case_id in enumerate(steady_ids)
        if case_id in transient_index
    ]

    transient_hashes: dict[str, list[int]] = defaultdict(list)
    for index in range(expected_transient_cases):
        transient_hashes[_row_digest(transient_matrix[index])].append(index)
    steady_hashes = [_row_digest(steady_matrix[index]) for index in range(expected_steady_cases)]
    exact_pairs = [
        (steady_index, transient_index_value)
        for steady_index, digest in enumerate(steady_hashes)
        for transient_index_value in transient_hashes.get(digest, [])
    ]
    exact_pair_set = set(exact_pairs)

    steady64 = steady_matrix.to(torch.float64)
    transient64 = transient_matrix.to(torch.float64)
    near_pairs: list[tuple[int, int]] = []
    nearest_rms = torch.full((expected_steady_cases,), float("inf"), dtype=torch.float64)
    for start in range(0, expected_steady_cases, block_rows):
        stop = min(start + block_rows, expected_steady_cases)
        difference = torch.abs(steady64[start:stop, None, :] - transient64[None, :, :])
        rms = torch.sqrt(torch.mean(difference.square(), dim=2))
        nearest_rms[start:stop] = rms.amin(dim=1)
        close = (difference.amax(dim=2) <= max_abs_limit) & (rms <= rms_limit)
        near_pairs.extend(
            (start + int(local_index), int(transient_index_value))
            for local_index, transient_index_value in torch.nonzero(close, as_tuple=False).tolist()
        )

    excluded_steady = {
        steady_index for steady_index, _ in name_pairs + near_pairs
    }
    near_only_pairs = [pair for pair in near_pairs if pair not in exact_pair_set]

    def partition_pair_counts(pairs: Sequence[tuple[int, int]]) -> dict[str, int]:
        counts = {name: 0 for name in partitions}
        for _, transient_index_value in pairs:
            counts[partition_by_id[transient_ids[transient_index_value]]] += 1
        return counts

    quantile_levels = torch.tensor([0.0, 0.05, 0.5, 0.95, 1.0], dtype=torch.float64)
    quantiles = torch.quantile(nearest_rms, quantile_levels).tolist()
    eligible_indices = [
        index for index in range(expected_steady_cases) if index not in excluded_steady
    ]
    eligible_names = [steady_ids[index] for index in eligible_indices]
    public = {
        "schema_version": "aurora.aneug_release_730_steady_overlap_audit.public_result.v1",
        "status": "complete",
        "documented_steady_case_count": 14_000,
        "steady_case_count": expected_steady_cases,
        "transient_case_count": expected_transient_cases,
        "steady_ghd_shape": list(steady_matrix.shape),
        "transient_ghd_shape": list(transient_matrix.shape),
        "case_name_exact_pair_count": len(name_pairs),
        "ghd_exact_pair_count": len(exact_pairs),
        "ghd_near_only_pair_count": len(near_only_pairs),
        "excluded_steady_case_count": len(excluded_steady),
        "eligible_steady_case_count": len(eligible_indices),
        "case_name_pair_counts_by_transient_partition": partition_pair_counts(name_pairs),
        "ghd_exact_pair_counts_by_transient_partition": partition_pair_counts(exact_pairs),
        "ghd_near_only_pair_counts_by_transient_partition": partition_pair_counts(near_only_pairs),
        "nearest_transient_ghd_rms_quantiles": {
            key: float(value)
            for key, value in zip(("min", "q05", "median", "q95", "max"), quantiles)
        },
        "near_max_abs_limit": max_abs_limit,
        "near_rms_limit": rms_limit,
        "steady_case_digest": _canonical_digest(steady_ids),
        "eligible_steady_case_digest": _canonical_digest(eligible_names),
        "case_ids_public": False,
        "steady_tensor_metadata_read": True,
        "steady_wss_values_read": False,
        "transient_wss_values_read": False,
        "locked_test_wss_values_read": False,
        "processed_only_extra_wss_values_read": False,
        "gpu_used": False,
        "model_fitted_or_selected": False,
        "scientific_performance_verdict": None,
    }
    private = {
        "schema_version": "aurora.private.aneug_release_730_steady_overlap_audit.v1",
        "steady_case_names": steady_ids,
        "eligible_steady_indices": eligible_indices,
        "eligible_steady_case_names": eligible_names,
        "case_name_exact_pairs": [
            {"steady_case": steady_ids[left], "transient_case": transient_ids[right]}
            for left, right in name_pairs
        ],
        "ghd_exact_pairs": [
            {"steady_case": steady_ids[left], "transient_case": transient_ids[right]}
            for left, right in exact_pairs
        ],
        "ghd_near_only_pairs": [
            {"steady_case": steady_ids[left], "transient_case": transient_ids[right]}
            for left, right in near_only_pairs
        ],
        "test_wss_opened": False,
        "any_wss_value_read": False,
    }
    serialized_public = json.dumps(public, sort_keys=True)
    _require(
        not any(json.dumps(case_id) in serialized_public for case_id in steady_ids + transient_ids),
        "public_id_leak",
    )
    return public, private


def execute(
    config: Mapping[str, Any],
    activation_path: Path,
    expected_commit: str,
    steady_path: Path,
    transient_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    public_result_path: Path,
    private_result_path: Path,
    torch: Any,
) -> None:
    validate_activation(activation_path, config, expected_commit)
    source = config["source"]
    for path, expected_bytes, expected_hash, label in (
        (steady_path, source["steady_v4_bytes"], source["steady_v4_sha256"], "steady"),
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (public_split_path, public_split_path.stat().st_size, source["public_split_sha256"], "public_split"),
        (private_split_path, private_split_path.stat().st_size, source["private_split_sha256"], "private_split"),
    ):
        _require(path.is_file() and path.stat().st_size == expected_bytes, f"{label}_size")
        _require(_sha256_file(path) == expected_hash, f"{label}_sha256")

    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    _require(public_split.get("status") == "complete", "public_split_status")
    _require(public_split.get("test_opened") is False, "public_test_opened")
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    partitions = _split_partitions(private_split)

    steady = safe_torch_load(steady_path, torch)
    transient = safe_torch_load(transient_path, torch)
    _require(isinstance(steady, Mapping) and isinstance(transient, Mapping), "archive_root")
    _require(
        {"case_name", "ghd_dict", "tensor", "label"}.issubset(steady),
        "steady_schema",
    )
    _require({"registered_data_list", "mesh_data"}.issubset(transient), "transient_schema")
    schema = config["schema"]
    steady_tensor = steady["tensor"]
    _require(
        tuple(int(value) for value in steady_tensor.shape)
        == (schema["expected_steady_cases"], schema["expected_nodes"], schema["expected_channels"]),
        "steady_tensor_shape",
    )
    _require(str(steady_tensor.dtype) == "torch.float32", "steady_tensor_dtype")
    steady_ghd_dict = steady["ghd_dict"]
    _require(isinstance(steady_ghd_dict, Mapping) and "ghd" in steady_ghd_dict, "steady_ghd")
    mesh = transient["mesh_data"]
    _require(isinstance(mesh, Mapping) and {"cases", "ghd"}.issubset(mesh), "transient_mesh")

    public, private = audit_geometry_overlap(
        steady["case_name"],
        steady_ghd_dict["ghd"],
        mesh["cases"],
        mesh["ghd"],
        partitions,
        torch,
        expected_steady_cases=schema["expected_steady_cases"],
        expected_transient_cases=schema["expected_transient_cases"],
        expected_ghd_width=schema["expected_ghd_width"],
        expected_partition_counts=schema["expected_main_split"],
        max_abs_limit=config["overlap"]["near_max_abs_limit"],
        rms_limit=config["overlap"]["near_rms_limit"],
        block_rows=config["overlap"]["steady_block_rows"],
    )
    public.update(
        {
            "public_commit": expected_commit,
            "steady_sha256": source["steady_v4_sha256"],
            "processed_v5_sha256": source["processed_v5_sha256"],
            "public_split_sha256": source["public_split_sha256"],
            "private_split_sha256": source["private_split_sha256"],
        }
    )
    private.update(
        {
            "public_commit": expected_commit,
            "public_result_path": str(public_result_path),
            "source_steady_sha256": source["steady_v4_sha256"],
            "source_processed_v5_sha256": source["processed_v5_sha256"],
        }
    )
    _atomic_json(public_result_path, public)
    private["public_result_sha256"] = _sha256_file(public_result_path)
    _atomic_json(private_result_path, private)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--steady", type=Path, required=True)
    parser.add_argument("--transient", type=Path, required=True)
    parser.add_argument("--public-split", type=Path, required=True)
    parser.add_argument("--private-split", type=Path, required=True)
    parser.add_argument("--public-result", type=Path, required=True)
    parser.add_argument("--private-result", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    import torch

    execute(
        config,
        args.activation,
        args.expected_commit,
        args.steady,
        args.transient,
        args.public_split,
        args.private_split,
        args.public_result,
        args.private_result,
        torch,
    )


if __name__ == "__main__":
    main()
