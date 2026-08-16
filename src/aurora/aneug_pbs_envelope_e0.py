"""Data-free, one-shot PBS execution-envelope audit for introai9.

E0 deliberately knows no scientific asset path.  It checks only the scheduler
envelope, an exact clean checkout, the selected Python/Torch runtime and a
strict atomic result write.  It cannot reopen the closed D6 v2 attempt or
authorize any field read, model, GPU, validation, outer test or paper claim.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


class E0ContractError(RuntimeError):
    """Raised when E0's infrastructure-only boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise E0ContractError(reason)


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version") == "aurora.aneug_pbs_envelope_e0.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id") == "aneug_data_free_pbs_envelope_e0_v1",
        "protocol_id",
    )
    _require(
        contract.get("status") == "registered_infrastructure_only_not_executed",
        "status",
    )
    closed = contract["closed_d6_boundary"]
    _require(closed["status"] == "closed_execution_incomplete", "d6_status")
    _require((closed["attempts_used"], closed["attempt_limit"]) == (1, 1), "d6_attempts")
    _require(closed["scientific_verdict"] is None, "d6_scientific_verdict")
    _require(closed["same_contract_resume_repair_or_rerun_allowed"] is False, "d6_rerun")
    _require(closed["e0_reopens_or_relabels_d6"] is False, "d6_reopen")

    execution = contract["execution"]
    _require(execution["server"] == "introai9", "server")
    _require(execution["scheduler"] == "PBS", "scheduler")
    _require(execution["queue"] == "coss_agpu", "queue")
    _require(
        (execution["ncpus"], execution["memory_gb"], execution["ngpus"])
        == (1, 2, 0),
        "resources",
    )
    _require(execution["walltime"] == "00:05:00", "walltime")
    _require(execution["maximum_pbs_attempts"] == 1, "attempt_budget")
    for key in (
        "one_interrupted_attempt_may_resume",
        "rerun_or_repair_after_any_outcome",
        "login_node_gpu_allowed",
    ):
        _require(execution[key] is False, key)
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")

    checks = contract["checks"]
    for key, value in checks.items():
        if key != "python_minimum":
            _require(value is True, f"check_{key}")
    _require(checks["python_minimum"] == "3.9", "python_minimum")

    forbidden = contract["forbidden_scope"]
    _require(forbidden and all(value is True for value in forbidden.values()), "forbidden_scope")
    output = contract["output_contract"]
    _require(output["record_directory_name"] == "aneug_pbs_envelope_e0_v1", "record_name")
    _require(output["atomic_json"] is True, "atomic_json")
    _require(output["refuse_existing_output"] is True, "refuse_existing_output")
    consequence = contract["consequence"]
    _require(consequence and all(value is True for value in consequence.values()), "consequence")


def _strict_atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists():
        raise E0ContractError("output_exists")
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise E0ContractError("temporary_output_exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with temporary.open("x", encoding="utf-8") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def _git(project_root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["/usr/bin/git", "-C", str(project_root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def run(
    config_path: str | Path,
    project_root: str | Path,
    expected_commit: str,
    output_path: str | Path,
) -> dict[str, Any]:
    contract = load_contract(config_path)
    root = Path(project_root).resolve()
    output = Path(output_path)
    _require(root.is_dir(), "project_root")
    _require(len(expected_commit) == 40, "expected_commit")
    actual_commit = _git(root, "rev-parse", "HEAD")
    _require(actual_commit == expected_commit, "commit_mismatch")
    _require(_git(root, "status", "--porcelain") == "", "checkout_dirty")
    job_id = os.environ.get("PBS_JOBID", "")
    work_directory = os.environ.get("PBS_O_WORKDIR", "")
    _require(bool(job_id), "pbs_job_id")
    _require(bool(work_directory), "pbs_work_directory")

    import torch

    _require(sys.version_info >= (3, 9), "python_version")
    payload: dict[str, Any] = {
        "schema_version": "aurora.aneug_pbs_envelope_e0.result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "complete_infrastructure_pass",
        "envelope_pass": True,
        "checks": {
            "pbs_job_id_present": True,
            "pbs_work_directory_present": True,
            "exact_commit": True,
            "clean_checkout": True,
            "approved_python_executable": True,
            "python_minimum_met": True,
            "torch_import": True,
            "atomic_json_write": True,
        },
        "runtime": {
            "python": ".".join(str(value) for value in sys.version_info[:3]),
            "torch": str(torch.__version__),
            "scheduler_gpu_request": 0,
        },
        "scientific_boundary": {
            "payload_or_tensor_read": False,
            "scientific_metric_or_gate_evaluated": False,
            "scientific_verdict": None,
            "model_or_method_executed": False,
            "training_or_inference_executed": False,
            "validation_or_outer_test_accessed": False,
            "gpu_used": False,
            "paper_result_or_claim_authorized": False,
        },
        "consequence": {
            "e0_closed": True,
            "d6_reopened": False,
            "field_read_authorized": False,
            "model_or_gpu_authorized": False,
            "validation_or_outer_test_authorized": False,
            "only_fresh_scientific_contract_design_permitted": True,
        },
        "excluded_server_accessed": False,
    }
    _strict_atomic_json(output, payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--project-root")
    parser.add_argument("--expected-commit")
    parser.add_argument("--output")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if args.validate_only:
        load_contract(args.config)
        return 0
    for name in ("project_root", "expected_commit", "output"):
        if not getattr(args, name):
            parser.error(f"--{name.replace('_', '-')} is required unless --validate-only")
    run(args.config, args.project_root, args.expected_commit, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
