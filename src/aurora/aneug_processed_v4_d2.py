"""Client-staged AneuG-Flow v4 checksum and schema gate.

D2 does not download data. It audits two exact objects staged through the
registered client/SFTP route, using the same metadata-only schema checks as D1.
D1 remains closed and is never relabelled by this result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aurora.aneug_processed_v4_d1 import AcquisitionContractError, audit_schema


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise AcquisitionContractError(reason)


def load_contract(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.aneug_processed_v4_client_stage_d2.v1",
        "schema_version",
    )
    _require(
        payload.get("protocol_id")
        == "aneug_transient_v4_client_staged_acquisition_d2",
        "protocol_id",
    )
    d1 = payload["d1_boundary"]
    _require(d1["attempts_used"] == 3, "d1_attempts")
    _require(d1["same_contract_retry_or_repair"] is False, "d1_retry")
    _require(d1["d2_relabels_d1"] is False, "d1_relabel")
    probe = payload["pre_registration_route_probe"]
    _require(probe["transient_range_bytes_read_and_discarded"] == 67_108_864, "probe_bytes")
    _require(probe["persistent_output"] is False, "probe_persistence")
    _require(probe["parsed"] is False, "probe_parse")
    source = payload["source"]
    _require(
        source["dataset_revision"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36",
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
    storage = payload["storage"]
    _require(storage["workflow_peak_cap_bytes"] == 60_000_000_000, "workflow_cap")
    _require(storage["client_staging_cap_bytes"] == 30_000_000_000, "client_cap")
    _require(storage["server_peak_bytes"] == 33_377_372_101, "server_peak")
    _require(storage["maximum_combined_new_bytes"] == 57_122_234_152, "combined_peak")
    _require(storage["sequential_client_download_required"] is True, "sequential")
    _require(storage["steady_client_copy_deleted_before_transient_download"] is True, "client_steady")
    _require(storage["steady_server_copy_deleted_after_schema_success"] is True, "server_steady")
    for forbidden in (
        "v5_downloaded",
        "raw_blood_or_wall_downloaded",
        "steady_14000_case_cfd_downloaded",
        "cfd_directory_downloaded",
    ):
        _require(storage[forbidden] is False, forbidden)
    transport = payload["transport"]
    _require(
        transport["route"]
        == "client_https_exact_download_then_windows_openssh_sftp_to_introai9",
        "transport_route",
    )
    _require(transport["compute_node_external_download"] is False, "compute_egress")
    _require(transport["login_node_external_download"] is False, "login_egress")
    _require(transport["maximum_client_sessions_per_object"] == 3, "client_sessions")
    _require(transport["maximum_sftp_sessions_per_object"] == 3, "sftp_sessions")
    gate = payload["schema_gate"]
    _require(gate["maximum_pbs_attempts"] == 1, "pbs_attempts")
    _require(gate["rerun_after_any_outcome"] is False, "schema_rerun")
    execution = payload["execution"]
    _require(execution["schema_server"] == "introai9", "server")
    _require(execution["ngpus"] == 0, "gpu")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")
    auth = payload["authorization"]
    _require(auth["client_download_and_sftp_staging"] is True, "staging_authority")
    for forbidden in (
        "scientific_p0_or_confirmatory_test",
        "method_selection",
        "gpu_training",
        "outer_test",
        "paper_result_or_claim",
    ):
        _require(auth[forbidden] is False, forbidden)
    return payload


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
    result.update(
        {
            "schema_version": "aurora.aneug_processed_v4_client_stage_d2.result.v1",
            "protocol_id": contract["protocol_id"],
            "status": "complete_client_staged_storage_and_schema_gate_passed",
            "d1_relabelled": False,
            "transport_route": contract["transport"]["route"],
        }
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
