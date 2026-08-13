"""Fail-closed activation layer for the immutable Aneumo P0 v3 evaluator.

The public P0 v3 config deliberately contains no private path and cannot
authorize execution by itself.  After a *verified* introai9 operational change,
a separately registered private manifest may bind that immutable evaluator to
one exact cache, container, runtime wheel and public source commit.  Until that
private manifest exists, this module refuses before reading cache bytes or HDF5
arrays.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_response_fidelity_p0 import (
    AneumoResponseFidelityP0Error,
    _load_train_hdf5,
    _sha256,
    load_dependencies,
    verify_cache_hash,
)
from .aneumo_response_fidelity_p0_v3 import (
    evaluate_records,
    load_config,
)


PROTOCOL_ID = "aneumo_response_fidelity_method_free_p0_v3"
ACTIVATION_SCHEMA = "aurora.aneumo_response_fidelity_p0_v3.activation.v2"
BASE_CONFIG = "configs/aneumo_response_fidelity_p0_v3.json"
BASE_CONFIG_SHA256 = (
    "1c7cc85dbd5d4ae5059663cfe3f638a7b4276b0f9fec537f4eec19757adfcc81"
)
BASE_EVALUATOR = "src/aurora/aneumo_response_fidelity_p0_v3.py"
BASE_EVALUATOR_SHA256 = (
    "51a7db669ea1e17917954291819586b827b975bb7d42b0d7f1c87e59b6971d25"
)
ACTIVATION_RUNNER = "src/aurora/aneumo_response_fidelity_p0_v3_activation.py"
REGISTERED_CACHE_SHA256 = (
    "9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9"
)
REGISTERED_CACHE_BYTES = 31_832_716
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
UTC_PATTERN = re.compile(r"^20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$")


class AneumoP0V3ActivationError(AneumoResponseFidelityP0Error):
    """Raised before scientific data access when activation is not exact."""


def _require_exact_keys(
    payload: Mapping[str, Any], expected: set[str], *, label: str
) -> None:
    observed = set(payload)
    if observed != expected:
        raise AneumoP0V3ActivationError(
            f"{label} keys differ: missing={sorted(expected - observed)}, "
            f"extra={sorted(observed - expected)}"
        )


def _require_absolute_private_path(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        raise AneumoP0V3ActivationError(f"{label} must be an absolute private path.")
    if value in {"/", "/home", "/tmp"}:
        raise AneumoP0V3ActivationError(f"{label} is too broad.")
    if not value.startswith("/home/introai9/"):
        raise AneumoP0V3ActivationError(f"{label} must remain inside introai9 scope.")
    return value


def _observed_git_commit(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AneumoP0V3ActivationError("Cannot resolve the public source commit.") from exc


def validate_activation_manifest(
    manifest: Mapping[str, Any],
    *,
    repository_root: Path,
    expected_public_source_commit: str,
    expected_host_cache_path: str,
    expected_container_path: str,
    expected_runtime_wheel_path: str,
    expected_output_root: str,
    observed_container_sha256: str,
    observed_runtime_wheel_sha256: str,
) -> None:
    """Validate private authority without opening the cache or HDF5 payload."""

    _require_exact_keys(
        manifest,
        {
            "schema_version",
            "protocol_id",
            "status",
            "registration",
            "source",
            "execution",
            "authorization",
        },
        label="activation manifest",
    )
    if (
        manifest["schema_version"] != ACTIVATION_SCHEMA
        or manifest["protocol_id"] != PROTOCOL_ID
        or manifest["status"]
        != "registered_after_verified_introai9_operational_change_before_p0_v3_field_read"
    ):
        raise AneumoP0V3ActivationError("Activation identity or status is not exact.")

    registration = manifest["registration"]
    _require_exact_keys(
        registration,
        {
            "registered_at_utc",
            "external_operational_change_evidence_id",
            "external_operational_change_verified",
            "container_readability_verified",
            "cache_readability_verified_without_hdf5_array_read",
            "registered_before_any_p0_v3_field_array_read",
            "prior_p0_v3_scientific_attempt_count",
        },
        label="registration",
    )
    evidence_id = registration["external_operational_change_evidence_id"]
    if (
        not isinstance(evidence_id, str)
        or len(evidence_id.strip()) < 8
        or evidence_id.lower() in {"unknown", "unverified", "pending"}
        or not UTC_PATTERN.fullmatch(str(registration["registered_at_utc"]))
        or registration["prior_p0_v3_scientific_attempt_count"] != 0
        or any(
            registration[key] is not True
            for key in (
                "external_operational_change_verified",
                "container_readability_verified",
                "cache_readability_verified_without_hdf5_array_read",
                "registered_before_any_p0_v3_field_array_read",
            )
        )
    ):
        raise AneumoP0V3ActivationError(
            "Activation requires prospective operational-change and readability evidence."
        )

    source = manifest["source"]
    _require_exact_keys(
        source,
        {
            "public_source_commit",
            "p0_config",
            "p0_config_sha256",
            "p0_evaluator",
            "p0_evaluator_sha256",
            "activation_runner",
            "activation_runner_sha256",
            "exact_private_cache_path",
            "cache_bytes",
            "cache_sha256",
            "container_path",
            "container_sha256",
            "runtime_wheel_path",
            "runtime_wheel_sha256",
            "runtime_wheel_package",
            "runtime_wheel_version",
        },
        label="source",
    )
    host_cache_path = _require_absolute_private_path(
        source["exact_private_cache_path"], label="exact_private_cache_path"
    )
    container_path = _require_absolute_private_path(
        source["container_path"], label="container_path"
    )
    runtime_wheel_path = _require_absolute_private_path(
        source["runtime_wheel_path"], label="runtime_wheel_path"
    )
    runner_path = repository_root / ACTIVATION_RUNNER
    if (
        source["public_source_commit"] != expected_public_source_commit
        or not COMMIT_PATTERN.fullmatch(expected_public_source_commit)
        or source["p0_config"] != BASE_CONFIG
        or source["p0_config_sha256"] != BASE_CONFIG_SHA256
        or source["p0_evaluator"] != BASE_EVALUATOR
        or source["p0_evaluator_sha256"] != BASE_EVALUATOR_SHA256
        or source["activation_runner"] != ACTIVATION_RUNNER
        or not runner_path.is_file()
        or _sha256(runner_path) != source["activation_runner_sha256"]
        or not FULL_SHA_PATTERN.fullmatch(source["activation_runner_sha256"])
        or host_cache_path != expected_host_cache_path
        or not host_cache_path.endswith(".h5")
        or source["cache_bytes"] != REGISTERED_CACHE_BYTES
        or source["cache_sha256"] != REGISTERED_CACHE_SHA256
        or container_path != expected_container_path
        or source["container_sha256"] != observed_container_sha256
        or not FULL_SHA_PATTERN.fullmatch(observed_container_sha256)
        or runtime_wheel_path != expected_runtime_wheel_path
        or not runtime_wheel_path.endswith(".whl")
        or source["runtime_wheel_sha256"] != observed_runtime_wheel_sha256
        or not FULL_SHA_PATTERN.fullmatch(observed_runtime_wheel_sha256)
        or source["runtime_wheel_package"] != "h5py"
        or source["runtime_wheel_version"] != "3.12.1"
    ):
        raise AneumoP0V3ActivationError(
            "Activation source, cache, container or runtime-wheel pin drifted."
        )
    for relative, expected_hash in (
        (BASE_CONFIG, BASE_CONFIG_SHA256),
        (BASE_EVALUATOR, BASE_EVALUATOR_SHA256),
    ):
        path = repository_root / relative
        if not path.is_file() or _sha256(path) != expected_hash:
            raise AneumoP0V3ActivationError("Immutable P0 v3 bytes drifted.")

    execution = manifest["execution"]
    _require_exact_keys(
        execution,
        {
            "server",
            "pbs_only",
            "queue",
            "cpu",
            "memory_gb",
            "gpu",
            "walltime",
            "network",
            "one_shot",
            "submitted",
            "allowed_split",
            "output_root",
            "login_node_gpu_command_allowed",
            "junjinyong_allowed",
        },
        label="execution",
    )
    output_root = _require_absolute_private_path(
        execution["output_root"], label="output_root"
    )
    if (
        execution["server"] != "introai9"
        or execution["pbs_only"] is not True
        or execution["queue"] != "coss_agpu"
        or execution["cpu"] != 4
        or execution["memory_gb"] != 16
        or execution["gpu"] != 0
        or execution["walltime"] != "01:00:00"
        or execution["network"] is not False
        or execution["one_shot"] is not True
        or execution["submitted"] is not False
        or execution["allowed_split"] != "train"
        or output_root != expected_output_root
        or execution["login_node_gpu_command_allowed"] is not False
        or execution["junjinyong_allowed"] is not False
    ):
        raise AneumoP0V3ActivationError("Activation execution envelope drifted.")

    authorization = manifest["authorization"]
    _require_exact_keys(
        authorization,
        {
            "p0_v3_train_only_field_read",
            "pressure_read",
            "validation_or_test_field_read",
            "method",
            "architecture",
            "gpu",
            "outer_test",
            "paper_claim",
        },
        label="authorization",
    )
    if authorization["p0_v3_train_only_field_read"] is not True or any(
        authorization[key] is not False
        for key in (
            "pressure_read",
            "validation_or_test_field_read",
            "method",
            "architecture",
            "gpu",
            "outer_test",
            "paper_claim",
        )
    ):
        raise AneumoP0V3ActivationError("Activation scientific authority is too broad.")


def load_activation_manifest(
    path: Path,
    *,
    repository_root: Path,
    expected_public_source_commit: str,
    expected_host_cache_path: str,
    expected_container_path: str,
    expected_runtime_wheel_path: str,
    expected_output_root: str,
    observed_container_sha256: str,
    observed_runtime_wheel_sha256: str,
    expected_activation_manifest_sha256: str,
) -> dict[str, Any]:
    if not path.is_file():
        raise AneumoP0V3ActivationError(
            "No registered private P0 v3 activation manifest; cache access is forbidden."
        )
    try:
        manifest_bytes = path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AneumoP0V3ActivationError("Activation manifest is unreadable.") from exc
    if (
        not FULL_SHA_PATTERN.fullmatch(expected_activation_manifest_sha256)
        or hashlib.sha256(manifest_bytes).hexdigest()
        != expected_activation_manifest_sha256
    ):
        raise AneumoP0V3ActivationError("Activation manifest bytes differ from submission pin.")
    validate_activation_manifest(
        manifest,
        repository_root=repository_root,
        expected_public_source_commit=expected_public_source_commit,
        expected_host_cache_path=expected_host_cache_path,
        expected_container_path=expected_container_path,
        expected_runtime_wheel_path=expected_runtime_wheel_path,
        expected_output_root=expected_output_root,
        observed_container_sha256=observed_container_sha256,
        observed_runtime_wheel_sha256=observed_runtime_wheel_sha256,
    )
    return manifest


def run_activated_p0(
    *,
    config_path: Path,
    activation_manifest_path: Path,
    root: Path,
    cache: Path,
    expected_host_cache_path: str,
    expected_container_path: str,
    expected_runtime_wheel_path: str,
    expected_output_root: str,
    public_source_commit: str,
    observed_container_sha256: str,
    observed_runtime_wheel_sha256: str,
    expected_activation_manifest_sha256: str,
    pbs_job_id: str,
) -> dict[str, Any]:
    """Run the immutable evaluator only after every private activation check."""

    if not pbs_job_id or os.environ.get("PBS_JOBID") != pbs_job_id:
        raise AneumoP0V3ActivationError("P0 v3 must execute inside the declared PBS job.")
    if _observed_git_commit(root) != public_source_commit:
        raise AneumoP0V3ActivationError("Public source commit differs from activation.")
    config = load_config(config_path)
    manifest = load_activation_manifest(
        activation_manifest_path,
        repository_root=root,
        expected_public_source_commit=public_source_commit,
        expected_host_cache_path=expected_host_cache_path,
        expected_container_path=expected_container_path,
        expected_runtime_wheel_path=expected_runtime_wheel_path,
        expected_output_root=expected_output_root,
        observed_container_sha256=observed_container_sha256,
        observed_runtime_wheel_sha256=observed_runtime_wheel_sha256,
        expected_activation_manifest_sha256=expected_activation_manifest_sha256,
    )
    if cache.stat().st_size != REGISTERED_CACHE_BYTES:
        raise AneumoP0V3ActivationError("Observed compact-cache byte count drifted.")
    observed_cache_sha256 = verify_cache_hash(
        cache,
        reported_sha256=manifest["source"]["cache_sha256"],
        registered_sha256=config["source"]["cache_sha256"],
    )
    dependencies = load_dependencies(config, root=root)
    flows, records = _load_train_hdf5(config, cache)
    result = evaluate_records(
        config,
        repository_root=root,
        flows=flows,
        records=records,
        expected_train_mapping=dependencies["train_mapping"],
        reported_cache_sha256=observed_cache_sha256,
        dependency_hashes_exact=dependencies["hashes_exact"],
        historical_velocity_response_exact=dependencies[
            "historical_velocity_response_exact"
        ],
    )
    result["config_sha256"] = _sha256(config_path)
    result["activation"] = {
        "manifest_sha256": _sha256(activation_manifest_path),
        "public_source_commit": public_source_commit,
        "pbs_job_id": pbs_job_id,
        "external_operational_change_evidence_id": manifest["registration"][
            "external_operational_change_evidence_id"
        ],
        "private_paths_published": False,
    }
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--activation-manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--expected-host-cache-path", required=True)
    parser.add_argument("--expected-container-path", required=True)
    parser.add_argument("--expected-runtime-wheel-path", required=True)
    parser.add_argument("--expected-output-root", required=True)
    parser.add_argument("--public-source-commit", required=True)
    parser.add_argument("--observed-container-sha256", required=True)
    parser.add_argument("--observed-runtime-wheel-sha256", required=True)
    parser.add_argument("--expected-activation-manifest-sha256", required=True)
    parser.add_argument("--pbs-job-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_activated_p0(
        config_path=args.config,
        activation_manifest_path=args.activation_manifest,
        root=args.root,
        cache=args.cache,
        expected_host_cache_path=args.expected_host_cache_path,
        expected_container_path=args.expected_container_path,
        expected_runtime_wheel_path=args.expected_runtime_wheel_path,
        expected_output_root=args.expected_output_root,
        public_source_commit=args.public_source_commit,
        observed_container_sha256=args.observed_container_sha256,
        observed_runtime_wheel_sha256=args.observed_runtime_wheel_sha256,
        expected_activation_manifest_sha256=(
            args.expected_activation_manifest_sha256
        ),
        pbs_job_id=args.pbs_job_id,
    )
    temporary = args.output.with_name(f".{args.output.name}.partial")
    if args.output.exists() or temporary.exists():
        raise AneumoP0V3ActivationError("P0 v3 refuses to overwrite an aggregate.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
