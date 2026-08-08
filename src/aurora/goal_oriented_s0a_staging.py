"""Validate the bounded CMHA chunked-staging v2 contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


class StagingProtocolError(ValueError):
    """Raised when staging provenance or the one-change repair boundary drifts."""


EXPECTED_FILES = {
    49199083: ("controls", "controls.rar", 4821489080, "8d18b970978a303ed89618066919a1b1"),
    49199500: (
        "statistics",
        "statistical results.rar",
        34376,
        "12b92693c79587fb6dbab4638bfad8bc",
    ),
    49201807: ("patients", "patients.rar", 10735821611, "e783d656ba51c6813aae9fca68565c17"),
}
EXPECTED_SINGLE_CHANGE = (
    "replace_each_monolithic_GET_with_exact_64_MiB_HTTP_range_chunks_and_atomic_assembly_while_adding_failure_status"
)


def load_staging_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate_staging_config(config: Mapping[str, Any]) -> tuple[str, ...]:
    checks: list[str] = []

    attribution = config.get("v1_attribution", {})
    if (
        attribution.get("public_source_commit")
        != "b6b6175e79a59e441c5a7fc88d4e5e23b1c3ff8c"
        or attribution.get("exit_status") != 28
        or attribution.get("verified_archive_bytes") != 0
        or attribution.get("retained_payload_bytes") != 0
        or attribution.get("raw_scheduler_stdout_available") is not False
        or attribution.get("exact_transport_cause") != "unresolved"
        or attribution.get("scientific_gate_evaluated") is not False
    ):
        raise StagingProtocolError("v1 incomplete execution must remain unresolved and non-scientific")
    checks.append("v1_failure_preserved")

    if config.get("single_change_from_v1") != EXPECTED_SINGLE_CHANGE:
        raise StagingProtocolError("v2 must retain the single transport-only change")
    transport = config.get("transport", {})
    if (
        transport.get("chunk_bytes") != 64 * 1024 * 1024
        or transport.get("expected_http_status") != 206
        or transport.get("pbs_attempts_for_this_public_source") != 1
        or transport.get("failure_status_trap") is not True
    ):
        raise StagingProtocolError("64 MiB range and one-attempt contract must remain fixed")
    checks.append("bounded_transport_change")

    release = config.get("official_release", {})
    observed = {
        item.get("id"): (
            item.get("label"),
            item.get("name"),
            item.get("bytes"),
            item.get("md5"),
        )
        for item in release.get("files", [])
    }
    if observed != EXPECTED_FILES or release.get("total_bytes") != 15557345067:
        raise StagingProtocolError("official CMHA release pins cannot change")
    checks.append("official_release_unchanged")

    boundaries = config.get("unchanged_boundaries", {})
    required_false = (
        "identifier_mapping",
        "unit_or_frame_audit",
        "solver_probe",
        "scientific_gate_evaluated",
        "medical_payload_publication",
        "model_access",
        "gpu_access",
        "outer_test_access",
        "submission_identity",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        raise StagingProtocolError("staging cannot evaluate S0a or open data/model claims")
    if boundaries.get("official_file_ids_sizes_md5") is not True:
        raise StagingProtocolError("official asset pins must remain unchanged")
    checks.append("staging_only_boundary")

    decision = config.get("decision", {})
    if decision.get("v1_relabelled") is not False or decision.get("s0a_relabelled") is not False:
        raise StagingProtocolError("v2 cannot relabel v1 or S0a")
    if "do_not_resubmit" not in str(decision.get("failure_action", "")):
        raise StagingProtocolError("v2 failure must not enter a same-source retry loop")
    checks.append("decision_boundary")

    return tuple(checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args(argv)
    config = load_staging_config(args.config)
    checks = validate_staging_config(config)
    print(json.dumps({"protocol_id": config["protocol_id"], "valid": True, "checks": list(checks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
