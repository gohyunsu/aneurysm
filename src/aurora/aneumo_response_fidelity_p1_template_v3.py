"""Fail-closed utilities for the inactive Aneumo P1 v3 design.

V3 was created before any P1 execution or prediction read.  It incorporates
new direct priors, controls the primary backbone, fixes the beneficial
direction prospectively, and bounds any later validation-only development.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_response_fidelity_p1_template import ResponseFidelityP1TemplateError
from .aneumo_response_fidelity_p1_template_v2 import (
    power_law_competent,
    select_unique_iso_error_matches,
)


FOLD_CONSTRUCTION = (
    "seeded_permutation_into_five_equal_blocks_outer_block_k_"
    "calibration_block_k_plus_1_mod_5_fit_remaining_three_blocks"
)
CHECKPOINT_ASSIGNMENT = (
    "for_each_model_jointly_assign_three_distinct_predeclared_checkpoints_to_"
    "three_ordered_targets_minimizing_total_absolute_log_distance_with_"
    "lexicographic_checkpoint_id_tie_break"
)


def _all_false(mapping: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return all(mapping.get(key) is False for key in keys)


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ResponseFidelityP1TemplateError(f"invalid v3 config: {exc}") from exc
    if not isinstance(payload, dict):
        raise ResponseFidelityP1TemplateError("v3 config root must be an object")
    validate_config(payload)
    return payload


def validate_config(config: Mapping[str, Any]) -> list[str]:
    """Validate the complete inactive v3 evidence boundary."""

    if (
        config.get("schema_version")
        != "aurora.aneumo_response_fidelity_p1_template.v3"
        or config.get("template_id")
        != "aneumo_backbone_controlled_response_failure_p1_template_v3"
        or config.get("status")
        != "draft_non_authoritative_blocked_on_real_p0_v2_all_11_pass"
    ):
        raise ResponseFidelityP1TemplateError("v3 template identity changed")

    supersession = config.get("supersession", {})
    if (
        supersession.get("supersedes_template")
        != "configs/aneumo_response_fidelity_p1_template_v2.json"
        or supersession.get("supersedes_template_sha256")
        != "67cbb858b0ffaaca9f6ee289872a4f2bd1d499deca95697b149bea86e5386918"
        or supersession.get("supersedes_validator")
        != "src/aurora/aneumo_response_fidelity_p1_template_v2.py"
        or supersession.get("supersedes_validator_sha256")
        != "d77cc99e9646ef64da4abfac441d0947101e634fb087d2e3a9b52ce1d3317530"
        or not _all_false(
            supersession,
            ("v2_executed", "v2_model_prediction_read", "v2_response_metric_read"),
        )
        or supersession.get("reasons")
        != [
            "new_aneumo_direct_priors_make_meshgraphnet_an_inadequate_primary_architecture_control",
            "meshgraphnet_versus_deltaphi_confounded_backbone_with_output_parameterization",
            "an_undirected_difference_could_post_hoc_reverse_the_mechanistic_story",
            "bounded_post_gate_development_repair_was_not_prospectively_limited",
        ]
    ):
        raise ResponseFidelityP1TemplateError("v2 supersession boundary changed")

    activation = config.get("activation_boundary", {})
    if (
        activation.get("real_p0_config")
        != "configs/aneumo_response_fidelity_p0_v2.json"
        or activation.get("real_p0_config_sha256")
        != "b82b3bfd3d83713f375378f471ec506e7b8437fd470e98366534d4cb1d021381"
        or activation.get("real_p0_required_verdict") != "pass_all_11_checks"
        or activation.get("real_p0_observed_verdict") is not None
        or activation.get("real_p0_required_check_count") != 11
        or activation.get("real_p0_observed_check_count") != 0
        or not _all_false(
            activation,
            ("this_file_can_be_executed", "this_file_can_be_submitted_to_pbs", "p1_registered"),
        )
        or any(
            activation.get(key) is not True
            for key in (
                "activation_requires_separate_registered_config",
                "activation_requires_exact_cache_path_and_execution_envelope",
                "activation_requires_public_commit_before_any_model_prediction",
                "core_match_pair_direction_or_inference_change_requires_new_evidence_version",
            )
        )
    ):
        raise ResponseFidelityP1TemplateError("v3 activation boundary changed")

    sources = config.get("source_reappraisal", {})
    hemo = sources.get("hemo_mpo", {})
    abgatr = sources.get("ab_gatr", {})
    labgatr = sources.get("lab_gatr", {})
    if (
        sources.get("scfno", {}).get("identifier")
        != "iclr_2025_sensitivity_constrained_fno"
        or hemo.get("identifier") != "doi:10.1016/j.aej.2026.05.044"
        or hemo.get("uses_aneumo") is not True
        or hemo.get("public_code_repository_identified") is not False
        or hemo.get("exact_family_split_and_reproduction_bundle_identified") is not False
        or abgatr.get("identifier") != "arxiv:2605.18816"
        or abgatr.get("uses_aneumo_single_flow_kg_per_s") != 0.001
        or abgatr.get("official_repository_commit")
        != "49acb32083d3389e57dde0f7f82703366c4cba27"
        or abgatr.get("repository_license_spdx") is not None
        or abgatr.get("exact_experiment_release_status") != "coming_soon"
        or labgatr.get("official_repository_commit")
        != "43379fddb7583d5a8527fc3e104b7c11f8f0afb9"
        or labgatr.get("repository_license_spdx") != "MIT"
        or labgatr.get("ab_gatr_source_reports_slightly_lower_aneumo_field_error_than_ab_gatr")
        is not True
        or sources.get("architecture_component_can_be_claimed_as_novelty") is not False
    ):
        raise ResponseFidelityP1TemplateError("v3 direct-prior boundary changed")

    question = config.get("scientific_question", {})
    if (
        question.get("independent_unit") != "aneumo_generation_base_family"
        or question.get("primary_field_metric") != "node_weighted_velocity_relative_l2"
        or question.get("primary_response_endpoints")
        != ["paired_response_relative_l2", "discrete_tangent_relative_l2"]
        or question.get("clinical_or_biological_interpretation_allowed") is not False
    ):
        raise ResponseFidelityP1TemplateError("v3 scientific estimand changed")

    data = config.get("data_boundary", {})
    if (
        data.get("pool") != "historical_20_train_base_families_only"
        or [
            data.get("outer_crossfit_folds"),
            data.get("families_per_outer_fold"),
            data.get("families_per_rotating_calibration_fold"),
            data.get("families_per_fit_partition"),
        ] != [5, 4, 4, 12]
        or data.get("fold_seed") != 2027081201
        or data.get("fold_construction") != FOLD_CONSTRUCTION
        or data.get("all_cases_flows_nodes_for_a_family_are_atomic") is not True
        or data.get("outer_response_metrics_never_select_checkpoint_or_match_level")
        is not True
        or not _all_false(
            data,
            (
                "historical_validation_families_read",
                "historical_test_families_read",
                "confirmation_families_read",
            ),
        )
    ):
        raise ResponseFidelityP1TemplateError("v3 family split boundary changed")

    information = config.get("information_set", {})
    if (
        information.get("inputs")
        != ["same_case_geometry", "same_case_nominal_velocity_field_q0", "target_mass_flow_q"]
        or information.get("target") != "same_case_target_flow_velocity_field"
        or information.get("nominal_mass_flow_kg_per_s") != 0.0025
        or not _all_false(
            information,
            ("pressure_allowed", "rupture_status_allowed", "patient_specific_inflow_claim_allowed"),
        )
    ):
        raise ResponseFidelityP1TemplateError("v3 information set changed")

    baselines = config.get("baseline_contract", {})
    primary = baselines.get("primary_pair", {})
    if (
        baselines.get("deterministic_controls")
        != ["linear_mass_flow_scaling", "train_fitted_power_law_scaling"]
        or baselines.get("descriptive_non_gating_architecture_controls")
        != [
            "pointwise_conditional_mlp",
            "deeponet_anchor_conditioned",
            "meshgraphnet_anchor_conditioned",
        ]
        or primary
        != {
            "shared_backbone": "lab_gatr_anchor_conditioned",
            "left": "lab_gatr_direct_target_field",
            "right": "lab_gatr_deltaphi_identity_residual",
            "left_output_map": "predict_target_velocity_directly",
            "right_output_map": "nominal_velocity_plus_log_flow_ratio_times_predicted_residual",
            "all_non_output_parameterization_settings_identical": True,
            "response_log_error_ratio": "natural_log_left_error_divided_by_right_error",
            "required_positive_direction": "lab_gatr_deltaphi_identity_residual_has_lower_response_error",
            "negative_or_mixed_direction_action": "close_exact_direction_without_reversing_narrative",
        }
        or baselines.get("source_only_unavailable_controls")
        != [
            "hemo_mpo_no_identified_code_or_exact_split_bundle",
            "ab_gatr_no_declared_repository_license_and_experiments_coming_soon",
        ]
        or baselines.get("proposal_model_present") is not False
        or baselines.get("model_name_or_component_stack_can_satisfy_novelty") is not False
    ):
        raise ResponseFidelityP1TemplateError("v3 controlled primary pair changed")

    compute = config.get("compute_matching", {})
    if (
        compute.get("training_seeds")
        != [2027081211, 2027081212, 2027081213, 2027081214, 2027081215]
        or compute.get("target_trainable_parameters") != 2_000_000
        or compute.get("parameter_relative_tolerance") != 0.1
        or compute.get("optimizer_updates_per_run") != 20_000
        or compute.get("node_condition_samples_per_update") != 8192
        or compute.get("checkpoint_fractions") != [index / 20 for index in range(1, 21)]
        or compute.get("same_container_optimizer_batch_sampler_precision_and_backbone")
        is not True
        or compute.get("actual_flops_gpu_seconds_peak_memory_and_inference_latency_reported")
        is not True
        or compute.get("total_p1_gpu_hour_cap") != 160.0
        or compute.get("execution_server") != "introai9"
        or compute.get("pbs_only") is not True
        or not _all_false(
            compute, ("gpu_authorized_now", "login_node_gpu_allowed", "junjinyong_allowed")
        )
    ):
        raise ResponseFidelityP1TemplateError("v3 compute boundary changed")

    matching = config.get("field_only_selection_and_matching", {})
    if (
        matching.get("response_metrics_available_during_selection") is not False
        or matching.get("iso_error_quantiles") != [0.25, 0.5, 0.75]
        or matching.get("checkpoint_assignment_rule") != CHECKPOINT_ASSIGNMENT
        or matching.get("checkpoint_reuse_across_iso_error_levels_allowed") is not False
        or matching.get("maximum_checkpoint_distance_log_ratio") != math.log(1.01)
        or matching.get("outer_field_equivalence_margin_log_ratio") != math.log(1.01)
        or matching.get("power_law_field_noninferiority_margin_log_ratio") != math.log(1.02)
        or matching.get("both_primary_pair_members_must_be_field_competent_against_power_law")
        is not True
    ):
        raise ResponseFidelityP1TemplateError("v3 matching boundary changed")

    inference = config.get("inference", {})
    if (
        inference.get("primary_iso_error_quantile") != 0.5
        or inference.get("sensitivity_iso_error_quantiles") != [0.25, 0.75]
        or inference.get("sensitivity_cells_can_rescue_primary_failure") is not False
        or inference.get("bootstrap_unit") != "aneumo_generation_base_family"
        or inference.get("bootstrap_replicates") != 5000
        or inference.get("bootstrap_seed") != 2027081221
        or inference.get("crossfit_family_contrasts_independent_for_exact_null_inference")
        is not False
        or inference.get("exact_sign_flip_p_value_allowed") is not False
        or inference.get("multiplicity_adjusted_p_value_claim_allowed") is not False
        or inference.get("minimum_multiplicative_response_gap") != 0.1
        or inference.get("minimum_positive_seed_count") != 4
        or inference.get("training_seed_count") != 5
        or inference.get("zero_seed_ties_count_as_positive") is not False
        or inference.get("negative_direction_can_pass") is not False
        or inference.get("descriptive_architecture_control_can_rescue_primary_failure")
        is not False
        or inference.get("p1_result_can_be_reported_as_confirmatory_inference_or_paper_efficacy")
        is not False
        or inference.get("formal_power_claim_allowed_before_independent_confirmation")
        is not False
    ):
        raise ResponseFidelityP1TemplateError("v3 directed inference boundary changed")

    development = config.get("bounded_development_after_p1_pass", {})
    if (
        development.get("authorized_now") is not False
        or development.get("requires_separate_public_registration") is not True
        or development.get("validation_only") is not True
        or development.get("historical_test_and_confirmation_families_remain_sealed")
        is not True
        or development.get("maximum_repair_rounds") != 2
        or development.get("maximum_additional_gpu_hours") != 80.0
        or development.get("one_attribution_supported_failure_hypothesis_per_round")
        is not True
        or development.get("all_variants_and_selection_rule_logged") is not True
        or development.get("fresh_seed_or_disjoint_split_prospective_reentry_required")
        is not True
        or development.get("prior_failure_relabelling_allowed") is not False
    ):
        raise ResponseFidelityP1TemplateError("v3 bounded development boundary changed")

    stopping = config.get("stopping_and_repair", {})
    if (
        stopping.get("all_primary_models_folds_seeds_required") is not True
        or stopping.get("partial_success_aggregation_allowed") is not False
        or stopping.get(
            "outcome_conditioned_pair_checkpoint_margin_threshold_or_direction_change_allowed"
        ) is not False
        or stopping.get("same_version_repair_or_rerun_after_any_outer_response_metric_access_allowed")
        is not False
        or stopping.get("negative_or_mixed_primary_direction_action")
        != "close_exact_direction_no_post_hoc_reversal"
        or stopping.get("p1_pass_authorizes_only")
        != "separate_bounded_validation_only_method_development_registration"
        or stopping.get("p1_pass_authorizes_paper_claim_outer_test_or_submission") is not False
    ):
        raise ResponseFidelityP1TemplateError("v3 stop boundary changed")

    current = config.get("current_state", {})
    if current.get("scientific_result_count") != 0 or not _all_false(
        current,
        (
            "config_registered",
            "model_code_authorized",
            "validation_or_test_access_authorized",
            "pbs_job_submitted",
            "gpu_job_submitted",
            "model_prediction_read",
            "response_metric_read",
            "paper_claim_active",
        ),
    ):
        raise ResponseFidelityP1TemplateError("v3 inactive current state changed")

    return [
        "immutable no-output v2 supersession",
        "inactive P0-gated authority",
        "direct-prior-complete architecture boundary",
        "family-atomic cyclic cross-fit",
        "same-backbone primary contrast",
        "fixed compute envelope",
        "duplicate-free response-blind matching",
        "directed residual-benefit criterion",
        "cross-fit no-inference boundary",
        "bounded validation-only development",
        "no-repair stop rules",
        "zero execution and claim state",
    ]


def positive_seed_count(seed_specific_contrasts: Sequence[float]) -> int:
    """Count strictly positive direct-over-residual log-error contrasts."""

    if len(seed_specific_contrasts) != 5 or any(
        not math.isfinite(value) for value in seed_specific_contrasts
    ):
        raise ResponseFidelityP1TemplateError(
            "v3 direction rule requires five finite seed contrasts"
        )
    return sum(value > 0 for value in seed_specific_contrasts)


def directed_co_primary_screen_passes(
    *,
    checkpoint_qualified: bool,
    field_ci_lower: float,
    field_ci_upper: float,
    direct_power_law_upper: float,
    residual_power_law_upper: float,
    paired_response_log_ratio: float,
    paired_interval_lower: float,
    paired_interval_upper: float,
    paired_seed_contrasts: Sequence[float],
    tangent_response_log_ratio: float,
    tangent_interval_lower: float,
    tangent_interval_upper: float,
    tangent_seed_contrasts: Sequence[float],
) -> bool:
    """Require prespecified residual benefit on both co-primary endpoints."""

    ratios = (paired_response_log_ratio, tangent_response_log_ratio)
    intervals = (
        (paired_interval_lower, paired_interval_upper),
        (tangent_interval_lower, tangent_interval_upper),
    )
    seeds = (paired_seed_contrasts, tangent_seed_contrasts)
    finite_ordered = all(
        math.isfinite(lower) and math.isfinite(upper) and lower <= upper
        for lower, upper in intervals
    )
    return (
        checkpoint_qualified
        and math.isfinite(field_ci_lower)
        and math.isfinite(field_ci_upper)
        and -math.log(1.01) <= field_ci_lower <= field_ci_upper <= math.log(1.01)
        and power_law_competent(direct_power_law_upper)
        and power_law_competent(residual_power_law_upper)
        and all(math.isfinite(value) and value >= math.log(1.1) for value in ratios)
        and finite_ordered
        and all(lower <= ratio <= upper for ratio, (lower, upper) in zip(ratios, intervals))
        and all(lower > 0 for lower, _ in intervals)
        and all(positive_seed_count(values) >= 4 for values in seeds)
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("config", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    print(json.dumps({"status": "valid_inactive_template_v3", "checks": validate_config(config)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
