"""Chunk-staged AneuG-Flow processed-v4 D3 transport and schema gate.

D3 never downloads data. It validates a private manifest for 23 fixed-size
chunks, verifies every staged chunk before retiring the closed D2 partial,
reassembles the exact transient object, and exposes the unchanged metadata-only
schema audit. No field metric or scientific endpoint is computed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Mapping

from aurora.aneug_processed_v4_d1 import AcquisitionContractError, audit_schema, file_sha256


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise AcquisitionContractError(reason)


def load_contract(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version") == "aurora.aneug_processed_v4_chunk_stage_d3.v1",
        "schema_version",
    )
    _require(
        payload.get("protocol_id") == "aneug_transient_v4_chunk_staged_acquisition_d3",
        "protocol_id",
    )
    selection = payload["human_selection"]
    _require(selection["explicitly_selected"] is True, "human_selection")
    _require(selection["d3_is_d2_retry_or_repair"] is False, "d2_retry")
    d2 = payload["d2_boundary"]
    _require(d2["status"] == "closed_transport_incomplete_sftp_budget_exhausted", "d2_status")
    _require(d2["sftp_sessions_used"] == 3, "d2_sessions")
    _require(d2["further_d2_sftp_session_allowed"] is False, "d2_fourth_session")
    _require(d2["d2_relabelled"] is False, "d2_relabel")
    source = payload["source"]
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
    client = payload["client_precondition"]
    _require(client["transient_exact_bytes"] == identities["transient"][0], "client_size")
    _require(client["transient_exact_sha256"] == identities["transient"][1], "client_sha")
    _require(client["full_object_redownload_allowed"] is False, "redownload")
    chunk = payload["chunk_contract"]
    _require(chunk["chunk_bytes"] == 1_073_741_824, "chunk_bytes")
    _require(chunk["chunk_count"] == 23, "chunk_count")
    _require(chunk["full_chunk_count"] == 22, "full_chunk_count")
    _require(chunk["final_chunk_bytes"] == 122_541_923, "final_chunk_bytes")
    _require(
        chunk["full_chunk_count"] * chunk["chunk_bytes"] + chunk["final_chunk_bytes"]
        == identities["transient"][0],
        "chunk_sum",
    )
    _require(chunk["one_local_chunk_at_a_time"] is True, "sequential_chunk")
    _require(chunk["maximum_sftp_sessions_per_chunk"] == 2, "chunk_session_budget")
    _require(chunk["completed_chunk_reupload_forbidden"] is True, "chunk_reupload")
    transport = payload["transport"]
    _require(transport["compute_node_external_download"] is False, "compute_egress")
    _require(transport["login_node_external_download"] is False, "login_egress")
    _require(transport["d2_monolithic_partial_resumed"] is False, "d2_resume")
    storage = payload["storage"]
    _require(storage["workflow_peak_cap_bytes"] == 60_000_000_000, "workflow_cap")
    _require(storage["client_staging_cap_bytes"] == 30_000_000_000, "client_cap")
    _require(storage["client_peak_bytes"] == 24_818_603_875, "client_peak")
    _require(
        storage["server_peak_before_d2_partial_retirement_bytes"] == 43_550_459_845,
        "server_pre_retirement_peak",
    )
    _require(
        storage["server_reassembly_peak_after_d2_partial_retirement_bytes"]
        == 57_122_234_152,
        "server_reassembly_peak",
    )
    _require(storage["d2_partial_retired_only_after_all_chunks_verified"] is True, "retire_order")
    _require(storage["chunks_deleted_only_after_full_size_and_sha256_match"] is True, "chunk_delete")
    for forbidden in (
        "v5_downloaded",
        "raw_blood_or_wall_downloaded",
        "steady_14000_case_cfd_downloaded",
        "cfd_directory_downloaded",
    ):
        _require(storage[forbidden] is False, forbidden)
    finalizer = payload["transport_finalizer"]
    _require(finalizer["server"] == "introai9", "finalizer_server")
    _require(finalizer["maximum_pbs_attempts"] == 1, "finalizer_attempts")
    _require(finalizer["rerun_after_any_outcome"] is False, "finalizer_rerun")
    _require(finalizer["ngpus"] == 0, "finalizer_gpu")
    gate = payload["schema_gate"]
    _require(gate["maximum_pbs_attempts"] == 1, "schema_attempts")
    _require(gate["rerun_after_any_outcome"] is False, "schema_rerun")
    execution = payload["execution"]
    _require(execution["schema_server"] == "introai9", "server")
    _require(execution["ngpus"] == 0, "gpu")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")
    auth = payload["authorization"]
    for allowed in (
        "chunk_creation_and_sftp_staging",
        "transport_finalization",
        "checksum_and_schema_audit",
    ):
        _require(auth[allowed] is True, allowed)
    for forbidden in (
        "scientific_p0_or_confirmatory_test",
        "method_selection",
        "gpu_training",
        "outer_test",
        "paper_result_or_claim",
    ):
        _require(auth[forbidden] is False, forbidden)
    return payload


def expected_chunk_size(contract: Mapping[str, Any], index: int) -> int:
    chunk = contract["chunk_contract"]
    _require(0 <= index < chunk["chunk_count"], "chunk_index")
    if index < chunk["full_chunk_count"]:
        return int(chunk["chunk_bytes"])
    return int(chunk["final_chunk_bytes"])


def expected_chunk_name(contract: Mapping[str, Any], index: int) -> str:
    return str(contract["chunk_contract"]["name_template"]).format(index=index)


def load_chunk_manifest(path: Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    _require(
        manifest.get("schema_version") == "aurora.aneug_processed_v4_chunk_manifest_d3.v1",
        "manifest_schema",
    )
    _require(manifest.get("protocol_id") == contract["protocol_id"], "manifest_protocol")
    _require(
        manifest.get("source_bytes") == contract["source"]["transient"]["bytes"],
        "manifest_bytes",
    )
    _require(
        manifest.get("source_sha256") == contract["source"]["transient"]["sha256"],
        "manifest_sha",
    )
    rows = manifest.get("chunks")
    _require(isinstance(rows, list) and len(rows) == 23, "manifest_chunk_count")
    offset = 0
    seen_hashes: set[str] = set()
    for index, row in enumerate(rows):
        _require(row.get("index") == index, "manifest_index")
        _require(row.get("name") == expected_chunk_name(contract, index), "manifest_name")
        _require(row.get("offset") == offset, "manifest_offset")
        size = expected_chunk_size(contract, index)
        _require(row.get("bytes") == size, "manifest_chunk_size")
        digest = row.get("sha256")
        _require(
            isinstance(digest, str)
            and len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            "manifest_chunk_sha",
        )
        _require(digest not in seen_hashes, "manifest_duplicate_sha")
        seen_hashes.add(digest)
        offset += size
    _require(offset == contract["source"]["transient"]["bytes"], "manifest_total")
    return manifest


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def finalize_chunks(
    contract: Mapping[str, Any],
    manifest: Mapping[str, Any],
    chunk_root: Path,
    closed_d2_partial: Path,
    target: Path,
    result_path: Path,
) -> dict[str, Any]:
    """Verify chunks, retire the closed D2 partial, and publish one exact object."""

    _require(not target.exists(), "target_already_exists")
    rows = manifest["chunks"]
    paths: list[Path] = []
    for row in rows:
        path = chunk_root / row["name"]
        _require(path.is_file(), f"missing_chunk:{row['index']}")
        _require(path.stat().st_size == row["bytes"], f"chunk_size:{row['index']}")
        _require(file_sha256(path) == row["sha256"], f"chunk_sha:{row['index']}")
        paths.append(path)

    # The D2 partial is retired only after every immutable D3 chunk passed.
    if closed_d2_partial.exists():
        closed_d2_partial.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".d3-assembling")
    _require(not temporary.exists(), "assembly_partial_exists")
    required = int(contract["source"]["transient"]["bytes"])
    _require(shutil.disk_usage(target.parent).free >= required, "reassembly_free_space")
    with temporary.open("xb") as output:
        for path in paths:
            with path.open("rb") as source:
                shutil.copyfileobj(source, output, length=16 * 1024 * 1024)
        output.flush()
        os.fsync(output.fileno())
    _require(temporary.stat().st_size == required, "assembled_size")
    digest = file_sha256(temporary)
    _require(digest == contract["source"]["transient"]["sha256"], "assembled_sha")
    os.replace(temporary, target)
    for path in paths:
        path.unlink()
    result = {
        "schema_version": "aurora.aneug_processed_v4_chunk_stage_d3.transport_result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "complete_exact_transient_reassembled",
        "chunk_count_verified": len(paths),
        "transient_bytes": target.stat().st_size,
        "transient_sha256": digest,
        "d2_partial_retired_after_all_chunks_verified": True,
        "chunks_deleted_after_full_identity_match": True,
        "scientific_field_read": False,
        "scientific_verdict": False,
        "gpu_executed": False,
        "next_authorized_action": "single_cpu_checksum_schema_gate",
    }
    _atomic_json(result_path, result)
    return result


def run_schema(
    contract: Mapping[str, Any],
    transient: Path,
    steady: Path,
    geometry_root: Path,
    result_path: Path,
    norm_manifest_path: Path,
    case_manifest_path: Path,
) -> None:
    import torch

    result, norm, cases = audit_schema(contract, transient, steady, geometry_root, torch)
    result.update(
        {
            "schema_version": "aurora.aneug_processed_v4_chunk_stage_d3.schema_result.v1",
            "protocol_id": contract["protocol_id"],
            "status": "complete_chunk_staged_storage_and_schema_gate_passed",
            "d2_relabelled": False,
            "scientific_verdict": False,
        }
    )
    _atomic_json(result_path, result)
    _atomic_json(norm_manifest_path, norm)
    _atomic_json(case_manifest_path, cases)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)
    finalizer = subparsers.add_parser("finalize")
    finalizer.add_argument("--manifest", type=Path, required=True)
    finalizer.add_argument("--chunk-root", type=Path, required=True)
    finalizer.add_argument("--closed-d2-partial", type=Path, required=True)
    finalizer.add_argument("--target", type=Path, required=True)
    finalizer.add_argument("--result", type=Path, required=True)
    schema = subparsers.add_parser("schema")
    schema.add_argument("--transport-result", type=Path, required=True)
    schema.add_argument("--transient", type=Path, required=True)
    schema.add_argument("--steady", type=Path, required=True)
    schema.add_argument("--geometry-root", type=Path, required=True)
    schema.add_argument("--result", type=Path, required=True)
    schema.add_argument("--norm-manifest", type=Path, required=True)
    schema.add_argument("--case-manifest", type=Path, required=True)
    args = parser.parse_args()
    contract = load_contract(args.config)
    if args.command == "finalize":
        manifest = load_chunk_manifest(args.manifest, contract)
        finalize_chunks(
            contract,
            manifest,
            args.chunk_root,
            args.closed_d2_partial,
            args.target,
            args.result,
        )
    else:
        transport = json.loads(args.transport_result.read_text(encoding="utf-8"))
        _require(
            transport.get("status") == "complete_exact_transient_reassembled",
            "transport_pass",
        )
        _require(
            transport.get("transient_sha256")
            == contract["source"]["transient"]["sha256"],
            "transport_sha",
        )
        run_schema(
            contract,
            args.transient,
            args.steady,
            args.geometry_root,
            args.result,
            args.norm_manifest,
            args.case_manifest,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
