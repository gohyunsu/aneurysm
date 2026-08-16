"""Validator for the dormant, non-executable AneuG D7 draft."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class D7DraftError(RuntimeError):
    """Raised when the draft is broadened or made executable."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D7DraftError(reason)


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version")
        == "aurora.aneug_processed_v4_d7_train_field_admission_draft.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_train_only_field_admission_d7_draft_v1",
        "protocol_id",
    )
    _require(contract.get("status") == "dormant_unselected_non_executable", "status")
    identity = contract["identity"]
    for key in ("d6_retry_repair_resume_or_relabel", "scientific_model_or_architecture", "paper_result_or_claim"):
        _require(identity[key] is False, f"identity_{key}")

    prior = contract["bound_prior_evidence"]
    _require(prior["expected_train_cases"] == 406, "train_count")
    _require((prior["expected_validation_cases"], prior["expected_outer_test_cases"]) == (51, 51), "sealed_counts")
    _require(prior["closed_d6_status"] == "closed_execution_incomplete", "d6_status")
    _require(prior["closed_d6_attempts"] == "1/1", "d6_attempts")
    _require(prior["closed_e0_status"] == "closed_infrastructure_classified", "e0_status")
    _require(prior["closed_e0_attempts"] == "1/1", "e0_attempts")
    _require(prior["e0_runner_envelope_pass"] is True, "e0_runner")
    _require(prior["e0_scheduler_output_staging_pass"] is False, "e0_staging")

    kernel = contract["immutable_scientific_kernel"]
    _require(
        kernel["registration_sha256"]
        == "2965ab58aec4ca7ee890f8f7f1928d4be69fd39f471f75099907809f43e13a66",
        "registration_identity",
    )
    _require(
        kernel["evaluator_sha256"]
        == "d38805c3c6c9dcec7081db108ff66be4afda93dbbc578938cc186a972facf907",
        "evaluator_identity",
    )
    _require(kernel["threshold_or_metric_change_allowed_after_selection"] is False, "threshold_change")
    _require(kernel["training_only_threshold_source"] is True and kernel["method_free"] is True, "method_free")

    read = contract["prospective_read_boundary"]
    _require(read["read_d5_train_tensor_values"] is True, "prospective_train_read")
    _require(read["read_shared_finest_faces"] is True, "prospective_faces_read")
    for key in (
        "read_validation_tensor_values",
        "read_outer_test_tensor_values",
        "read_auxiliary_tensor_values",
        "publish_case_ids_or_split_members",
        "fit_or_select_model",
        "read_values_now",
    ):
        _require(read[key] is False, f"read_boundary_{key}")

    gate = contract["prospective_gate"]
    _require(gate["scientific_verdict_before_execution"] is None, "premature_verdict")
    _require(all(value is True for key, value in gate.items() if key != "scientific_verdict_before_execution"), "gate")

    envelope = contract["required_execution_envelope"]
    _require(envelope["server"] == "introai9" and envelope["excluded_server"] == "junjinyong", "server")
    _require((envelope["ncpus"], envelope["memory_gb"], envelope["ngpus"]) == (4, 64, 0), "resources")
    _require(envelope["maximum_pbs_attempts"] == 1, "attempt_budget")
    _require(envelope["rerun_or_repair_after_any_outcome"] is False, "rerun")
    for key in (
        "precreate_fresh_private_record_directory",
        "attempt_marker_and_internal_log_before_strict_mode",
        "attempt_marker_and_internal_log_before_profile_or_environment_checks",
        "absolute_approved_python",
        "exact_quality_passed_clean_checkout",
        "atomic_internal_status_and_result",
        "scheduler_stdout_stderr_is_not_evidence_channel",
        "post_job_staging_error_cannot_erase_complete_internal_result",
    ):
        _require(envelope[key] is True, f"envelope_{key}")
    _require(envelope["source_etc_profile_inside_wrapper"] is False, "profile")
    _require(envelope["login_node_gpu_allowed"] is False, "login_gpu")

    selection = contract["selection_boundary"]
    for key in (
        "human_selected",
        "private_activation_registered",
        "executable_config_exists",
        "pbs_wrapper_exists_for_d7",
        "execution_runner_exists_for_d7",
        "pbs_submission_authorized",
        "field_read_authorized",
        "same_file_may_be_mutated_into_executable_contract",
    ):
        _require(selection[key] is False, f"selection_{key}")
    _require(selection["selected_contract_must_be_a_fresh_version"] is True, "fresh_selection")

    consequence = contract["conditional_consequence"]
    _require(consequence["complete_pass_permits_only_fresh_bounded_train_validation_baseline_registration"] is True, "pass_scope")
    for key in (
        "complete_pass_permits_immediate_model_training",
        "complete_pass_permits_outer_test",
        "complete_pass_is_paper_result",
    ):
        _require(consequence[key] is False, f"consequence_{key}")
    _require(consequence["scientific_failure_closes_selected_d7_without_repair"] is True, "scientific_failure")
    _require(consequence["execution_incomplete_closes_selected_d7_without_repair"] is True, "execution_incomplete")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    load_contract(args.config)
    if not args.validate_only:
        raise D7DraftError("non_executable_draft")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
