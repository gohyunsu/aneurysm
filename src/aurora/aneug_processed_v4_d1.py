"""Storage-bounded acquisition/schema audit for official AneuG-Flow v4.

This module never downloads data.  The PBS wrapper owns exact resumable
transport; this module validates the immutable contract and audits only object
structure, tensor metadata, case-ID linkage, and the small normalization state.
It computes no field value or scientific endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load


class AcquisitionContractError(RuntimeError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise AcquisitionContractError(reason)


def file_sha256(path: Path, chunk_bytes: int = 16 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_bytes), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_contract(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.aneug_processed_v4_acquisition_d1.v1",
        "schema_version",
    )
    _require(
        payload.get("protocol_id")
        == "aneug_transient_v4_storage_bounded_acquisition_d1",
        "protocol_id",
    )
    source = payload["source"]
    _require(
        source["dataset_revision"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "dataset_revision",
    )
    _require(source["license"] == "cc-by-sa-4.0", "license")
    expected = {
        "transient": (
            23744862051,
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        ),
        "steady_norm_source": (
            9632510050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
    }
    for role, identity in expected.items():
        item = source[role]
        _require((item["bytes"], item["sha256"]) == identity, f"{role}_identity")
    storage = payload["storage"]
    _require(storage["selected_aneug_v4_peak_cap_bytes"] == 60_000_000_000, "storage_cap")
    _require(storage["new_processed_peak_bytes"] == sum(v[0] for v in expected.values()), "peak_bytes")
    _require(storage["transient_persistent"] is True, "transient_retention")
    _require(storage["steady_full_object_persistent_after_norm_extraction"] is False, "steady_retention")
    for forbidden in (
        "v5_downloaded", "raw_blood_or_wall_downloaded",
        "steady_14000_case_cfd_downloaded", "cfd_directory_downloaded",
    ):
        _require(storage[forbidden] is False, forbidden)
    transport = payload["transport"]
    _require(transport["maximum_pbs_transport_attempts"] == 3, "attempt_budget")
    _require(transport["resumable_partial_download"] is True, "resume")
    _require(transport["resume_only_while_transport_incomplete"] is True, "resume_scope")
    _require(transport["schema_gate_rerun_after_complete_transport"] is False, "schema_rerun")
    execution = payload["execution"]
    _require(execution["server"] == "introai9", "server")
    _require(execution["ngpus"] == 0, "gpu")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")
    auth = payload["authorization"]
    _require(auth["data_acquisition_and_schema_audit"] is True, "acquisition_authority")
    for forbidden in (
        "scientific_p0_or_confirmatory_test", "method_claim",
        "gpu_training_before_split_freeze", "paper_result",
    ):
        _require(auth[forbidden] is False, forbidden)
    return payload


def verify_object(path: Path, identity: Mapping[str, Any]) -> None:
    _require(path.is_file(), f"missing:{path.name}")
    _require(path.stat().st_size == identity["bytes"], f"size:{path.name}")
    _require(file_sha256(path) == identity["sha256"], f"sha256:{path.name}")


def _tensor_metadata(tensor: Any) -> dict[str, Any]:
    return {
        "shape": [int(v) for v in tensor.shape],
        "dtype": str(tensor.dtype),
        "stride": [int(v) for v in tensor.stride()],
    }


def audit_schema(
    contract: Mapping[str, Any],
    transient_path: Path,
    steady_path: Path,
    geometry_root: Path,
    torch: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    verify_object(transient_path, contract["source"]["transient"])
    verify_object(steady_path, contract["source"]["steady_norm_source"])
    transient = safe_torch_load(transient_path, torch)
    steady = safe_torch_load(steady_path, torch)
    _require(isinstance(transient, Mapping), "transient_root")
    _require(isinstance(steady, Mapping), "steady_root")
    _require({"registered_data_list", "mesh_data"}.issubset(transient), "transient_keys")
    _require({"label", "tensor_norm"}.issubset(steady), "steady_norm_keys")
    cases = transient["registered_data_list"]
    mesh = transient["mesh_data"]
    _require(isinstance(cases, Sequence), "case_sequence")
    _require(isinstance(mesh, Mapping) and "cases" in mesh, "mesh_cases")
    gate = contract["schema_gate"]
    _require(len(cases) >= gate["minimum_cases"], "case_floor")
    case_ids = [str(case.get("case", "")) for case in cases]
    _require(all(case_ids) and len(case_ids) == len(set(case_ids)), "case_ids")
    _require(case_ids == [str(value) for value in mesh["cases"]], "mesh_case_order")
    common_labels: list[str] | None = None
    common_shape: list[int] | None = None
    for case in cases:
        _require(isinstance(case, Mapping), "case_mapping")
        labels = [str(value) for value in case.get("labels", [])]
        tensor = case.get("tensor")
        _require(hasattr(tensor, "shape") and len(tensor.shape) == 3, "case_tensor")
        _require(int(tensor.shape[0]) == gate["expected_timesteps"], "timesteps")
        _require(all(value in labels for value in gate["required_vector_wss_labels"]), "wss_labels")
        _require(all(value in labels for value in gate["required_geometry_labels"]), "geometry_labels")
        if common_labels is None:
            common_labels = labels
            common_shape = [int(v) for v in tensor.shape]
        else:
            _require(labels == common_labels, "common_labels")
            _require([int(v) for v in tensor.shape] == common_shape, "common_shape")
    linked = [case_id for case_id in case_ids if (geometry_root / case_id).is_dir()]
    _require(len(linked) == len(case_ids), "geometry_linkage")
    norm = steady["tensor_norm"]
    _require(isinstance(norm, Mapping) and {"mean", "std"}.issubset(norm), "tensor_norm")
    steady_labels = [str(value) for value in steady["label"]]
    mean = norm["mean"].detach().cpu().reshape(-1)
    std = norm["std"].detach().cpu().reshape(-1)
    _require(len(steady_labels) == int(mean.numel()) == int(std.numel()), "norm_shape")
    _require(all(label in steady_labels for label in gate["required_vector_wss_labels"]), "norm_wss_labels")
    case_manifest = {
        "schema_version": "aurora.aneug_processed_v4.case_manifest.v1",
        "dataset_revision": contract["source"]["dataset_revision"],
        "case_ids": case_ids,
    }
    norm_manifest = {
        "schema_version": "aurora.aneug_processed_v4.norm_manifest.v1",
        "dataset_revision": contract["source"]["dataset_revision"],
        "labels": steady_labels,
        "mean": [float(value) for value in mean.tolist()],
        "std": [float(value) for value in std.tolist()],
        "source_sha256": contract["source"]["steady_norm_source"]["sha256"],
    }
    case_digest = hashlib.sha256(
        json.dumps(case_ids, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    result = {
        "schema_version": "aurora.aneug_processed_v4_acquisition_d1.result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "complete_storage_and_schema_gate_passed",
        "transient_bytes": transient_path.stat().st_size,
        "transient_sha256": contract["source"]["transient"]["sha256"],
        "steady_norm_source_bytes": steady_path.stat().st_size,
        "steady_norm_source_sha256": contract["source"]["steady_norm_source"]["sha256"],
        "case_count": len(cases),
        "case_id_manifest_sha256": case_digest,
        "case_ids_public": False,
        "all_case_ids_linked_to_local_geometry": True,
        "timesteps": common_shape[0],
        "nodes": common_shape[1],
        "channels": common_shape[2],
        "labels": common_labels,
        "first_tensor_metadata": _tensor_metadata(cases[0]["tensor"]),
        "field_values_or_scientific_metrics_read": False,
        "scientific_p0_or_model_executed": False,
        "gpu_executed": False,
        "paper_result_activated": False,
        "next_authorized_action": "freeze_geometry_linkage_near_duplicate_groups_and_development_split",
    }
    return result, norm_manifest, case_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--transient", type=Path, required=True)
    parser.add_argument("--steady", type=Path, required=True)
    parser.add_argument("--geometry-root", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--norm-manifest", type=Path, required=True)
    parser.add_argument("--case-manifest", type=Path, required=True)
    args = parser.parse_args()
    contract = load_contract(args.config)
    import torch

    result, norm, cases = audit_schema(
        contract, args.transient, args.steady, args.geometry_root, torch
    )
    for path, payload in (
        (args.result, result),
        (args.norm_manifest, norm),
        (args.case_manifest, cases),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
