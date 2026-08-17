"""Fresh, human-selected one-shot D7 train-field admission execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d6 import (
    audit_loaded_training_payload,
    load_contract as load_registered_kernel,
)


class D7ExecutionError(RuntimeError):
    """Raised when the selected D7 contract cannot be honored exactly."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D7ExecutionError(reason)


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def validate_execution_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version") == "aurora.aneug_processed_v4_d7_execution.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_train_only_field_admission_d7_execution_v1",
        "protocol_id",
    )
    _require(contract.get("status") == "human_activated_executable", "status")

    activation = contract["human_activation"]
    _require(activation["explicitly_selected"] is True, "human_selection")
    _require(activation["selection"] == "D7", "human_selection_name")
    _require(activation["selected_on"] == "2026-08-17", "selection_date")
    for key in (
        "activates_only_this_fresh_execution_version",
        "does_not_mutate_dormant_draft",
        "does_not_repair_resume_rerun_reopen_or_relabel_d6",
    ):
        _require(activation[key] is True, f"activation_{key}")

    draft = contract["immutable_dormant_draft"]
    _require(
        draft["relative_path"]
        == "configs/aneug_processed_v4_d7_train_field_admission_draft_v1.json",
        "draft_path",
    )
    _require(
        draft["sha256"]
        == "1ebd3d4e218d432fa0c0fa6379bd5086af22c33d621f46f4df5ac9490bf0d0ed",
        "draft_sha256",
    )
    _require(draft["status"] == "dormant_unselected_non_executable", "draft_status")
    _require(draft["remains_non_executable"] is True, "draft_boundary")

    kernel = contract["immutable_scientific_kernel"]
    _require(
        kernel["registration_path"]
        == "configs/aneug_processed_v4_d6_train_field_audit_v1.json",
        "kernel_registration_path",
    )
    _require(
        kernel["registration_sha256"]
        == "2965ab58aec4ca7ee890f8f7f1928d4be69fd39f471f75099907809f43e13a66",
        "kernel_registration_sha256",
    )
    _require(
        kernel["evaluator_path"] == "src/aurora/aneug_processed_v4_d6.py",
        "kernel_evaluator_path",
    )
    _require(
        kernel["evaluator_sha256"]
        == "d38805c3c6c9dcec7081db108ff66be4afda93dbbc578938cc186a972facf907",
        "kernel_evaluator_sha256",
    )
    _require(kernel["threshold_or_metric_change"] is False, "kernel_change")
    _require(kernel["method_free"] is True, "kernel_method")

    prior = contract["bound_prior_evidence"]
    _require(
        prior["closed_d5_private_manifest_sha256"]
        == "0f95cf303fa63b58c049e722864389c1432460686e335d20402b677c368181d6",
        "d5_private_manifest_sha256",
    )
    _require(
        prior["d5_train_split_sha256"]
        == "df583f3553ce4efcf0588da5bdc029921025648c1981eba3a85fe3841d2bf26e",
        "d5_train_split_sha256",
    )
    _require(
        (
            prior["expected_train_cases"],
            prior["expected_validation_cases"],
            prior["expected_outer_test_cases"],
        )
        == (406, 51, 51),
        "split_counts",
    )
    _require(prior["closed_d6_status"] == "closed_execution_incomplete", "d6_status")
    _require(prior["closed_d6_attempts"] == "1/1", "d6_attempts")
    _require(prior["closed_e0_status"] == "closed_infrastructure_classified", "e0_status")
    _require(prior["closed_e0_attempts"] == "1/1", "e0_attempts")
    _require(prior["e0_runner_envelope_pass"] is True, "e0_runner")
    _require(prior["e0_scheduler_output_staging_pass"] is False, "e0_staging")

    expected = {
        "transient": (
            "processed_v4_d3/assembled_registered_data_1k_v4.pth",
            23_744_862_051,
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        ),
        "steady": (
            "processed_v4_d2/assembled_registered_steady_data_1k_v4.pth.temporary",
            9_632_510_050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
    }
    for name, (relative_path, size, sha256) in expected.items():
        item = contract["source_identity"][name]
        _require(item["relative_server_path"] == relative_path, f"{name}_path")
        _require(item["bytes"] == size, f"{name}_bytes")
        _require(item["sha256"] == sha256, f"{name}_sha256")

    boundary = contract["read_boundary"]
    _require(boundary["allowed_tensor_values"] == "d5_train_cases_only", "train_scope")
    _require(boundary["read_train_tensor_values"] is True, "train_read")
    _require(boundary["read_shared_finest_faces"] is True, "faces_read")
    for key in (
        "read_validation_tensor_values",
        "read_outer_test_tensor_values",
        "read_auxiliary_tensor_values",
        "publish_case_ids",
        "publish_train_normalization_values",
    ):
        _require(boundary[key] is False, f"read_boundary_{key}")

    execution = contract["execution"]
    _require(execution["server"] == "introai9", "server")
    _require(
        execution["scheduler"] == "PBS" and execution["queue"] == "coss_agpu",
        "scheduler",
    )
    _require(
        (execution["ncpus"], execution["memory_gb"], execution["ngpus"])
        == (4, 64, 0),
        "resources",
    )
    _require(execution["walltime"] == "03:00:00", "walltime")
    _require(
        (execution["attempts_used_before_submission"], execution["maximum_pbs_attempts"])
        == (0, 1),
        "attempt_budget",
    )
    for key in (
        "one_interrupted_attempt_may_resume",
        "rerun_or_repair_after_any_outcome",
        "source_etc_profile_inside_wrapper",
        "scheduler_stdout_stderr_is_evidence",
        "login_node_gpu_allowed",
    ):
        _require(execution[key] is False, f"execution_{key}")
    for key in (
        "precreate_private_record_directory",
        "attempt_marker_and_internal_log_before_strict_mode",
        "exact_quality_passed_clean_commit_required",
        "private_activation_manifest_required",
    ):
        _require(execution[key] is True, f"execution_{key}")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")

    consequence = contract["consequence"]
    _require(consequence["any_attempt_outcome_closes_d7"] is True, "closure")
    _require(
        consequence["pass_permits_only_fresh_bounded_train_validation_baseline_registration"]
        is True,
        "pass_scope",
    )
    for key in (
        "pass_permits_outer_test_access",
        "pass_permits_immediate_gpu_training",
        "pass_is_paper_result",
        "failure_or_incomplete_permits_same_contract_repair",
    ):
        _require(consequence[key] is False, f"consequence_{key}")

    authorization = contract["authorization"]
    for key in (
        "execute_d7_now",
        "submit_one_cpu_pbs",
        "monitor_that_attempt",
        "read_d5_train_field_values",
    ):
        _require(authorization[key] is True, f"authorization_{key}")
    for key in (
        "read_validation_or_outer_field_values",
        "fit_or_select_model",
        "gpu_training",
        "paper_result_or_claim",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")


def load_execution_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_execution_contract(contract)
    return contract


def verify_exact_file(path: str | Path, identity: Mapping[str, Any], label: str) -> None:
    source = Path(path)
    _require(source.is_file(), f"missing_{label}")
    _require(source.stat().st_size == int(identity["bytes"]), f"{label}_size")
    _require(file_sha256(source) == identity["sha256"], f"{label}_sha256")


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists(), f"output_exists:{target.name}")
    _require(not temporary.exists(), f"temporary_output_exists:{target.name}")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _assert_finite_json(value: Any) -> None:
    if isinstance(value, float):
        _require(math.isfinite(value), "nonfinite_output")
    elif isinstance(value, Mapping):
        for nested in value.values():
            _assert_finite_json(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _assert_finite_json(nested)


def run_execution(
    execution_contract_path: str | Path,
    dormant_draft_path: str | Path,
    registration_path: str | Path,
    evaluator_path: str | Path,
    transient_path: str | Path,
    steady_path: str | Path,
    private_manifest_path: str | Path,
    public_result_path: str | Path,
    private_statistics_path: str | Path,
    torch: Any,
) -> dict[str, Any]:
    execution = load_execution_contract(execution_contract_path)
    _require(
        file_sha256(dormant_draft_path)
        == execution["immutable_dormant_draft"]["sha256"],
        "dormant_draft_file_sha256",
    )
    kernel = execution["immutable_scientific_kernel"]
    _require(
        file_sha256(registration_path) == kernel["registration_sha256"],
        "registration_file_sha256",
    )
    _require(
        file_sha256(evaluator_path) == kernel["evaluator_sha256"],
        "evaluator_file_sha256",
    )
    registration = load_registered_kernel(registration_path)
    verify_exact_file(transient_path, execution["source_identity"]["transient"], "transient")
    verify_exact_file(steady_path, execution["source_identity"]["steady"], "steady")

    manifest_path = Path(private_manifest_path)
    _require(manifest_path.is_file(), "missing_d5_private_manifest")
    _require(
        file_sha256(manifest_path)
        == execution["bound_prior_evidence"]["closed_d5_private_manifest_sha256"],
        "d5_private_manifest_file_sha256",
    )
    private_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    steady = safe_torch_load(steady_path, torch)
    transient = safe_torch_load(transient_path, torch)
    public, private = audit_loaded_training_payload(
        registration,
        steady,
        transient,
        private_manifest,
        torch,
        source_identity_reverified=True,
    )
    public.update(
        {
            "kernel_schema_version": public["schema_version"],
            "kernel_protocol_id": public["protocol_id"],
            "schema_version": "aurora.aneug_processed_v4_d7.public_result.v1",
            "protocol_id": execution["protocol_id"],
            "execution_schema_version": execution["schema_version"],
            "human_activation": "D7",
            "pbs_attempt_limit": 1,
            "d7_closes_after_this_outcome": True,
        }
    )
    private.update(
        {
            "kernel_schema_version": private["schema_version"],
            "kernel_protocol_id": private["protocol_id"],
            "schema_version": "aurora.aneug_processed_v4_d7.private_train_statistics.v1",
            "protocol_id": execution["protocol_id"],
            "execution_schema_version": execution["schema_version"],
            "human_activation": "D7",
        }
    )
    _assert_finite_json(public)
    _assert_finite_json(private)
    _strict_atomic_json(private_statistics_path, private)
    _strict_atomic_json(public_result_path, public)
    return public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution-config", type=Path, required=True)
    parser.add_argument("--dormant-draft", type=Path)
    parser.add_argument("--registration", type=Path)
    parser.add_argument("--evaluator", type=Path)
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--private-d5-manifest", type=Path)
    parser.add_argument("--public-result", type=Path)
    parser.add_argument("--private-statistics", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    load_execution_contract(args.execution_config)
    if args.validate_only:
        return 0
    required = (
        args.dormant_draft,
        args.registration,
        args.evaluator,
        args.transient,
        args.steady,
        args.private_d5_manifest,
        args.public_result,
        args.private_statistics,
    )
    _require(all(item is not None for item in required), "missing_execution_argument")
    import torch

    torch.set_num_threads(4)
    result = run_execution(
        args.execution_config,
        args.dormant_draft,
        args.registration,
        args.evaluator,
        args.transient,
        args.steady,
        args.private_d5_manifest,
        args.public_result,
        args.private_statistics,
        torch,
    )
    print(
        "D7 train-only admission complete; "
        f"gate_pass={str(result['gate_pass']).lower()}; "
        "validation/outer reads=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
