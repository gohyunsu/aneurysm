"""Validate the immutable SU2 reverse-AD preflight contract for S0a."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


class SolverPreflightProtocolError(ValueError):
    """Raised when the solver preflight contract is weakened or inconsistent."""


EXPECTED_SU2_COMMIT = "12eb826f049ef7f67df974dfcb44cf36ee07c0f8"
EXPECTED_TESTDATA_COMMIT = "790c80ec5b543487b5f8ecf8bb0f0e4d2cc67f3f"
EXPECTED_AMD64_MANIFEST = (
    "sha256:8dc6f035de165a1e7c2e62c33e274ede60947d8a204b9dd2ae806fa12ccb9a72"
)
REQUIRED_FLAGS = {
    "-Denable-autodiff=true",
    "-Denable-normal=true",
    "-Dwith-omp=true",
}
REQUIRED_BINARIES = {"SU2_CFD", "SU2_CFD_AD", "SU2_DEF", "SU2_DOT"}
REQUIRED_CHECKS = {
    "exact_source_and_testdata_commits",
    "exact_oci_linux_amd64_manifest",
    "license_hash",
    "normal_and_reverse_ad_binaries",
    "immutable_runtime_sif_and_sha256",
    "incompressible_steady_direct_exit_0",
    "fresh_direct_solution_written",
    "discrete_adjoint_exit_0",
    "surface_sensitivity_is_finite_and_nonzero",
    "no_medical_asset_model_gpu_or_outer_test_access",
}


def load_solver_preflight_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate_solver_preflight_config(config: Mapping[str, Any]) -> tuple[str, ...]:
    checks: list[str] = []

    if config.get("scientific_gate_evaluated") is not False:
        raise SolverPreflightProtocolError("preflight cannot evaluate or relabel S0a")
    checks.append("preflight_boundary")

    upstream = config.get("upstream", {})
    if upstream.get("su2", {}).get("commit") != EXPECTED_SU2_COMMIT:
        raise SolverPreflightProtocolError("SU2 source commit must remain exact")
    if upstream.get("testdata", {}).get("commit") != EXPECTED_TESTDATA_COMMIT:
        raise SolverPreflightProtocolError("TestCases commit must remain exact")
    if (
        upstream.get("official_build_image", {}).get("linux_amd64_manifest_digest")
        != EXPECTED_AMD64_MANIFEST
    ):
        raise SolverPreflightProtocolError("linux/amd64 OCI manifest must remain exact")
    checks.append("immutable_upstream")

    build = config.get("build", {})
    if not REQUIRED_FLAGS.issubset(set(build.get("flags", []))):
        raise SolverPreflightProtocolError("both normal and reverse-AD OMP builds are required")
    if set(build.get("required_binaries", [])) != REQUIRED_BINARIES:
        raise SolverPreflightProtocolError("four solver binaries are required")
    if build.get("runtime_format") != "immutable_sif":
        raise SolverPreflightProtocolError("runtime must be an immutable SIF")
    checks.append("build_contract")

    discovery = config.get("discovery_before_registration", {}).get(
        "official_precompiled_omp_release", {}
    )
    if discovery.get("eligible_for_s0a") is not False or "AD_support" not in str(
        discovery.get("discrete_adjoint_probe", "")
    ):
        raise SolverPreflightProtocolError("direct-only precompiled release failure must be preserved")
    checks.append("negative_control_preserved")

    probe = config.get("probe", {})
    if probe.get("equations") != "INC_NAVIER_STOKES":
        raise SolverPreflightProtocolError("probe must remain incompressible Navier-Stokes")
    if probe.get("direct", {}).get("uses_supplied_solution") is not False:
        raise SolverPreflightProtocolError("probe must produce a fresh direct solution")
    if probe.get("discrete_adjoint", {}).get("uses_fresh_direct_solution") is not True:
        raise SolverPreflightProtocolError("adjoint must consume the fresh direct solution")
    if set(probe.get("required_checks", [])) != REQUIRED_CHECKS:
        raise SolverPreflightProtocolError("all ten runtime checks are required")
    checks.append("probe_contract")

    execution = config.get("execution", {})
    if execution.get("resource") != "cpu_only_no_ngpus":
        raise SolverPreflightProtocolError("preflight must remain CPU-only")
    if execution.get("exact_clean_public_checkout_required") is not True:
        raise SolverPreflightProtocolError("exact clean public checkout is required")
    checks.append("execution_boundary")

    decision = config.get("decision", {})
    if decision.get("same_source_version_rerun_after_failure") is not False:
        raise SolverPreflightProtocolError("same-version preflight rerun is forbidden")
    if decision.get("s0a_relabelled_by_preflight") is not False:
        raise SolverPreflightProtocolError("preflight cannot relabel S0a")
    checks.append("decision_boundary")

    authorization = config.get("authorization", {})
    forbidden = (
        "medical_asset_access",
        "model_selected",
        "architecture_selected",
        "gpu_training",
        "outer_test",
        "submission_identity",
        "clinical_claim",
    )
    if any(authorization.get(key) is not False for key in forbidden):
        raise SolverPreflightProtocolError("preflight cannot authorize data, method, GPU, or claims")
    checks.append("authorization_boundary")

    return tuple(checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args(argv)
    config = load_solver_preflight_config(args.config)
    checks = validate_solver_preflight_config(config)
    print(
        json.dumps(
            {
                "protocol_id": config["protocol_id"],
                "valid": True,
                "checks": list(checks),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
