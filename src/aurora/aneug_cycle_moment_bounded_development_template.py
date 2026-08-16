"""Validator for the non-executable D7-conditional GPU development template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class BoundedDevelopmentTemplateError(RuntimeError):
    """Raised when the template is broadened or activated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise BoundedDevelopmentTemplateError(reason)


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version")
        == "aurora.aneug_cycle_moment_bounded_development_template.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_cycle_moment_validation_only_bounded_development_template_v1",
        "protocol_id",
    )
    _require(
        contract.get("status")
        == "conditional_on_future_d7_pass_unselected_non_executable",
        "status",
    )
    activation = contract["activation_preconditions"]
    _require(activation["d7_selected_executed_and_complete_pass"] is False, "d7_not_passed")
    _require(activation["d7_same_contract_retry_or_repair"] is False, "d7_retry")
    _require(activation["fresh_development_contract_required_after_d7_pass"] is True, "fresh_contract")
    _require(activation["private_activation_before_first_gpu_allocation"] is True, "private_activation")
    _require(activation["current_gpu_or_model_authority"] is False, "current_authority")

    scheduler = contract["scheduler_observation_not_guarantee"]
    _require(scheduler["server"] == "introai9", "server")
    _require((scheduler["coss_agpu_user_max_running_jobs"], scheduler["coss_agpu_user_max_running_gpus"]) == (1, 2), "agpu_limits")
    _require((scheduler["coss_a6gpu_user_max_running_jobs"], scheduler["coss_a6gpu_user_max_running_gpus"]) == (1, 1), "a6gpu_limits")
    _require(scheduler["queue_default_walltime_hours"] == 72, "queue_walltime")
    for key in (
        "gpu_model_identity_exposed_by_audited_scheduler_fields",
        "node_availability_is_stable_or_reserved",
        "gpu_model_name_may_be_inferred_from_node_name",
    ):
        _require(scheduler[key] is False, f"scheduler_{key}")

    data = contract["immutable_data_boundary"]
    _require(data["unit"] == "d5_synthetic_geometry_component_not_patient", "unit")
    _require((data["train_components"], data["validation_components"], data["outer_components"], data["auxiliary_cases"]) == (406, 51, 51, 70), "split")
    for key in (
        "all_phases_follow_component",
        "validation_only_selection",
        "outer_values_sealed_until_one_shot_confirmation",
        "auxiliary_values_never_used_for_model_selection_or_confirmation",
    ):
        _require(data[key] is True, f"data_{key}")
    _require(data["split_or_unit_change_allowed"] is False, "split_change")

    budget = contract["resource_budget"]
    _require((budget["gpu_per_job"], budget["maximum_concurrent_jobs"]) == (1, 1), "job_resources")
    _require(budget["maximum_total_gpu_hours"] == 360, "total_budget")
    _require(budget["round_caps_gpu_hours"] == {"R0_engineering": 12, "R1_primary_development": 220, "R2_single_repair": 108, "C0_outer_evaluation": 20}, "round_budgets")
    _require(sum(budget["round_caps_gpu_hours"].values()) == 360, "budget_sum")
    _require(budget["maximum_accepted_gpu_jobs"] == 32, "job_cap")
    _require(budget["maximum_training_jobs"] == 29, "training_job_cap")
    _require(budget["maximum_accepted_attempts_per_variant_seed"] == 1, "variant_attempt_cap")
    _require(budget["same_variant_seed_resubmission_after_accepted_job"] is False, "variant_resubmission")
    _require(budget["maximum_repair_rounds"] == 1, "repair_cap")
    _require(budget["pbs_walltime_per_job_hours"] == 24, "job_walltime")
    for key in (
        "round_caps_are_nonfungible",
        "unused_budget_may_not_create_new_variants",
        "stop_before_submission_if_projected_total_exceeds_cap",
        "failed_or_preempted_accepted_jobs_consume_budget",
    ):
        _require(budget[key] is True, f"budget_{key}")

    runtime = contract["runtime_lock"]
    for key in (
        "first_allocation_is_runtime_smoke_only",
        "record_gpu_name_driver_cuda_torch_memory_and_container_hash",
        "no_gpu_model_assumed_before_smoke",
        "one_epoch_scaling_probe_before_training_schedule",
        "scaling_probe_is_not_performance_evidence",
        "exact_environment_frozen_after_smoke",
        "persistent_internal_log_before_strict_mode_or_environment_checks",
        "scheduler_stdout_stderr_is_not_evidence_channel",
    ):
        _require(runtime[key] is True, f"runtime_{key}")
    _require(runtime["login_node_gpu_allowed"] is False, "login_gpu")
    _require(runtime["excluded_server"] == "junjinyong", "excluded_server")

    rounds = contract["rounds"]
    _require(rounds["R0"]["maximum_gpu_jobs"] == 2 and rounds["R0"]["seed"] == 17, "R0")
    _require(rounds["R0"]["may_read_validation"] is False and rounds["R0"]["may_read_outer"] is False, "R0_read")
    _require(rounds["R1"]["maximum_training_jobs"] == 19, "R1_jobs")
    _require(rounds["R1"]["primary_pair_seeds"] == [1103, 2207, 3301, 4409, 5501], "R1_seeds")
    _require(rounds["R1"]["control_seeds"] == [1103, 2207, 3301], "control_seeds")
    _require(rounds["R1"]["may_read_outer"] is False, "R1_outer")
    _require(rounds["R2"]["maximum_training_jobs"] == 10, "R2_jobs")
    _require(rounds["R2"]["fresh_primary_pair_seeds"] == [6607, 7703, 8807, 9901, 11113], "R2_seeds")
    _require(rounds["R2"]["second_repair_round_allowed"] is False, "R2_only")
    _require(rounds["C0"]["maximum_gpu_jobs"] == 1 and rounds["C0"]["outer_attempt_limit"] == 1, "C0_attempt")
    _require(rounds["C0"]["training_allowed"] is False and rounds["C0"]["outer_rerun_repair_or_relabel"] is False, "C0_no_repair")

    repair = contract["repair_hypothesis_menu"]
    _require(set(repair["allowed"]) == {"optimization_underfit", "moment_cone_infeasibility", "memory_induced_batch_mismatch"}, "repair_menu")
    for key in (
        "architecture_family_change",
        "new_loss_or_endpoint",
        "new_data_or_split",
        "new_threshold_or_seed_after_observation",
        "multiple_simultaneous_changes",
    ):
        _require(repair[key] is False, f"repair_{key}")

    selection = contract["selection_and_confirmation"]
    _require(selection["field_noninferiority_upper_ratio"] == 1.02, "field_margin")
    _require(selection["tawss_point_ratio_maximum"] == 0.95, "tawss_floor")
    _require(selection["osi_metric"] == "area_weighted_mae_on_reference_valid_support", "osi_metric")
    _require(selection["osi_point_ratio_maximum"] == 0.95, "osi_floor")
    _require((selection["component_bootstrap_replicates"], selection["component_bootstrap_seed"]) == (10000, 271828), "bootstrap")
    _require((selection["minimum_positive_primary_pair_seeds"], selection["primary_pair_seed_count"]) == (4, 5), "seed_rule")
    for key in (
        "field_bootstrap_upper_must_not_exceed_margin",
        "tawss_and_osi_bootstrap_upper_must_be_below_one",
        "all_field_tawss_osi_and_seed_conditions_form_one_conjunction",
        "rrt_is_redundant_secondary",
        "invalid_predictions_penalized_and_coverage_reported",
        "same_rule_used_for_R1_R2_and_C0",
        "outer_failure_is_final",
    ):
        _require(selection[key] is True, f"selection_{key}")

    authorization = contract["current_authorization"]
    _require(authorization and all(value is False for value in authorization.values()), "current_authorization")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    load_contract(args.config)
    if not args.validate_only:
        raise BoundedDevelopmentTemplateError("non_executable_template")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
