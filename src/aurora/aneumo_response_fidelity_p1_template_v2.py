"""Fail-closed utilities for the superseding inactive Aneumo P1 v2 template.

V2 remains non-executable.  It closes four design ambiguities in v1 without
reading model predictions or response endpoints: checkpoint reuse, power-law
competence, primary/sensitivity multiplicity, contrast direction, and invalid
exact inference from dependent cross-fit contrasts.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_response_fidelity_p1_template import (
    IsoErrorMatch,
    ResponseFidelityP1TemplateError,
    field_equivalent,
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
SEED_DIRECTION_RULE = (
    "seed_specific_mean_over_20_outer_family_log_error_ratios_must_have_same_"
    "nonzero_sign_as_pooled_response_contrast_zero_ties_do_not_count"
)


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ResponseFidelityP1TemplateError(f"invalid v2 config: {exc}") from exc
    if not isinstance(payload, dict):
        raise ResponseFidelityP1TemplateError("v2 config root must be an object")
    validate_config(payload)
    return payload


def _all_false(mapping: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return all(mapping.get(key) is False for key in keys)


def validate_config(config: Mapping[str, Any]) -> list[str]:
    """Validate the immutable inactive v2 design boundary."""

    if (
        config.get("schema_version")
        != "aurora.aneumo_response_fidelity_p1_template.v2"
        or config.get("template_id")
        != "aneumo_field_error_iso_matched_failure_p1_template_v2"
        or config.get("status")
        != "draft_non_authoritative_blocked_on_real_p0_v2_all_11_pass"
    ):
        raise ResponseFidelityP1TemplateError("v2 template identity changed")

    supersession = config.get("supersession", {})
    if (
        supersession.get("supersedes_template")
        != "configs/aneumo_response_fidelity_p1_template_v1.json"
        or supersession.get("supersedes_template_sha256")
        != "07d7b89e4a77331fe3dda7f4fe716ef1efaab3561519e5654f47a2841ad32d06"
        or not _all_false(
            supersession,
            ("v1_executed", "v1_model_prediction_read", "v1_response_metric_read"),
        )
        or supersession.get("reasons")
        != [
            "nearest_checkpoint_rule_did_not_forbid_reuse_across_iso_error_levels",
            "power_law_field_competence_interval_and_direction_were_not_explicit",
            "unqualified_cell_multiplicity_treatment_was_not_explicit",
            "primary_log_ratio_direction_and_seed_tie_handling_were_not_explicit",
            "family_sign_flip_treated_crossfit_contrasts_as_independent_exact_null_units",
        ]
    ):
        raise ResponseFidelityP1TemplateError("v1 supersession history changed")

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
                "core_match_or_inference_change_requires_new_evidence_version",
            )
        )
    ):
        raise ResponseFidelityP1TemplateError("v2 activation boundary changed")

    question = config.get("scientific_question", {})
    if (
        question.get("independent_unit") != "aneumo_generation_base_family"
        or question.get("primary_field_metric") != "node_weighted_velocity_relative_l2"
        or question.get("primary_response_endpoints")
        != ["paired_response_relative_l2", "discrete_tangent_relative_l2"]
        or question.get("clinical_or_biological_interpretation_allowed") is not False
    ):
        raise ResponseFidelityP1TemplateError("v2 scientific estimand changed")

    data = config.get("data_boundary", {})
    if (
        data.get("pool") != "historical_20_train_base_families_only"
        or [
            data.get("outer_crossfit_folds"),
            data.get("families_per_outer_fold"),
            data.get("families_per_rotating_calibration_fold"),
            data.get("families_per_fit_partition"),
        ]
        != [5, 4, 4, 12]
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
        raise ResponseFidelityP1TemplateError("v2 family split boundary changed")

    information = config.get("information_set", {})
    if (
        information.get("inputs")
        != ["same_case_geometry", "same_case_nominal_velocity_field_q0", "target_mass_flow_q"]
        or information.get("target") != "same_case_target_flow_velocity_field"
        or information.get("nominal_mass_flow_kg_per_s") != 0.0025
        or not _all_false(
            information,
            (
                "pressure_allowed",
                "rupture_status_allowed",
                "patient_specific_inflow_claim_allowed",
            ),
        )
    ):
        raise ResponseFidelityP1TemplateError("v2 information set changed")

    baselines = config.get("baselines", {})
    primary = baselines.get("primary_pair", {})
    if (
        baselines.get("deterministic_controls")
        != ["linear_mass_flow_scaling", "train_fitted_power_law_scaling"]
        or baselines.get("learned_same_information_set_models")
        != [
            "pointwise_conditional_mlp",
            "deeponet_anchor_conditioned",
            "deltaphi_style_anchor_residual",
            "meshgraphnet_anchor_conditioned",
        ]
        or primary
        != {
            "left": "meshgraphnet_anchor_conditioned",
            "right": "deltaphi_style_anchor_residual",
            "response_log_error_ratio": "natural_log_left_error_divided_by_right_error",
            "positive_contrast_means": (
                "deltaphi_style_anchor_residual_has_lower_response_error"
            ),
            "negative_contrast_means": (
                "meshgraphnet_anchor_conditioned_has_lower_response_error"
            ),
        }
        or baselines.get("secondary_non_gating_pairs")
        != [
            ["deeponet_anchor_conditioned", "deltaphi_style_anchor_residual"],
            ["pointwise_conditional_mlp", "deltaphi_style_anchor_residual"],
        ]
        or baselines.get("historical_v1e_role")
        != "diagnostic_only_not_primary_pair_due_to_different_information_set"
        or baselines.get("proposal_model_present") is not False
        or baselines.get("model_name_can_satisfy_novelty") is not False
    ):
        raise ResponseFidelityP1TemplateError("v2 baseline or contrast direction changed")

    compute = config.get("compute_matching", {})
    if (
        compute.get("training_seeds")
        != [2027081211, 2027081212, 2027081213, 2027081214, 2027081215]
        or compute.get("target_trainable_parameters") != 2_000_000
        or compute.get("parameter_relative_tolerance") != 0.1
        or compute.get("optimizer_updates_per_run") != 20_000
        or compute.get("node_condition_samples_per_update") != 8192
        or compute.get("checkpoint_fractions") != [index / 20 for index in range(1, 21)]
        or compute.get("same_container_optimizer_batch_sampler_and_precision") is not True
        or compute.get("actual_flops_gpu_seconds_peak_memory_and_inference_latency_reported")
        is not True
        or compute.get("total_p1_gpu_hour_cap") != 160.0
        or compute.get("execution_server") != "introai9"
        or compute.get("pbs_only") is not True
        or not _all_false(
            compute,
            ("gpu_authorized_now", "login_node_gpu_allowed", "junjinyong_allowed"),
        )
    ):
        raise ResponseFidelityP1TemplateError("v2 compute boundary changed")

    matching = config.get("field_only_selection_and_matching", {})
    if (
        matching.get("response_metrics_available_during_selection") is not False
        or matching.get("common_support_scale") != "natural_log_field_relative_l2"
        or matching.get("iso_error_quantiles") != [0.25, 0.5, 0.75]
        or matching.get("checkpoint_assignment_rule") != CHECKPOINT_ASSIGNMENT
        or matching.get("checkpoint_reuse_across_iso_error_levels_allowed") is not False
        or matching.get("maximum_checkpoint_distance_log_ratio") != math.log(1.01)
        or matching.get("unqualified_level_action")
        != (
            "retain_fixed_level_without_replacement_or_caliper_widening_"
            "primary_median_failure_closes_screen"
        )
        or matching.get("outer_field_equivalence_estimand")
        != "per_family_seed_mean_log_left_field_error_divided_by_right_field_error"
        or matching.get("outer_field_equivalence_interval")
        != (
            "fixed_seed_5000_replicate_family_percentile_90_percent_"
            "stability_interval_without_nominal_coverage_claim"
        )
        or matching.get("outer_field_equivalence_margin_log_ratio") != math.log(1.01)
        or matching.get("power_law_competence_estimand")
        != "per_family_seed_mean_log_model_field_error_divided_by_power_law_field_error"
        or matching.get("power_law_competence_interval")
        != (
            "one_sided_family_percentile_95_percent_stability_upper_bound_"
            "without_nominal_coverage_claim"
        )
        or matching.get("power_law_field_noninferiority_margin_log_ratio") != math.log(1.02)
        or matching.get("both_primary_pair_members_must_be_field_competent_against_power_law")
        is not True
    ):
        raise ResponseFidelityP1TemplateError("v2 matching or competence rule changed")

    inference = config.get("inference", {})
    if (
        inference.get("primary_cell_slots")
        != (
            "one_primary_pair_x_median_iso_error_level_x_two_co_primary_"
            "endpoints_always_two"
        )
        or inference.get("primary_iso_error_quantile") != 0.5
        or inference.get("sensitivity_cell_slots")
        != (
            "one_primary_pair_x_low_and_high_iso_error_levels_x_two_"
            "endpoints_always_four"
        )
        or inference.get("sensitivity_cells_can_rescue_primary_failure") is not False
        or inference.get("bootstrap_unit") != "aneumo_generation_base_family"
        or inference.get("bootstrap_replicates") != 5000
        or inference.get("bootstrap_seed") != 2027081221
        or inference.get("bootstrap_interval")
        != "percentile_stability_interval_without_nominal_coverage_claim"
        or inference.get("response_contrast")
        != (
            "per_family_seed_mean_natural_log_left_response_error_"
            "divided_by_right_response_error"
        )
        or inference.get("crossfit_family_contrasts_independent_for_exact_null_inference")
        is not False
        or inference.get("exact_sign_flip_p_value_allowed") is not False
        or inference.get("holm_or_other_p_value_multiplicity_claim_allowed") is not False
        or inference.get("minimum_multiplicative_response_gap") != 0.1
        or inference.get("minimum_same_direction_seed_count") != 4
        or inference.get("training_seed_count") != 5
        or inference.get("seed_direction_rule") != SEED_DIRECTION_RULE
        or inference.get("secondary_pair_level_or_endpoint_can_rescue_primary_failure")
        is not False
        or inference.get("p1_result_can_be_reported_as_confirmatory_inference_or_paper_efficacy")
        is not False
        or inference.get("formal_power_claim_allowed_before_model_contrast_variance_exists")
        is not False
    ):
        raise ResponseFidelityP1TemplateError("v2 inference boundary changed")

    stopping = config.get("stopping_and_repair", {})
    if (
        stopping.get("all_models_folds_seeds_required") is not True
        or stopping.get("partial_success_aggregation_allowed") is not False
        or stopping.get(
            "outcome_conditioned_pair_checkpoint_margin_or_threshold_change_allowed"
        )
        is not False
        or stopping.get(
            "same_version_repair_or_rerun_after_any_outer_response_metric_access_allowed"
        )
        is not False
        or stopping.get("missing_common_support_or_no_qualified_primary_cell_action")
        != "close_exact_direction_no_scientific_mismatch"
        or stopping.get("execution_incomplete_action")
        != "close_exact_p1_no_scientific_verdict"
        or stopping.get("p1_pass_authorizes_only")
        != "separate_bounded_validation_only_method_development_registration"
        or stopping.get("p1_pass_authorizes_paper_claim_outer_test_or_submission") is not False
    ):
        raise ResponseFidelityP1TemplateError("v2 stopping or repair boundary changed")

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
        raise ResponseFidelityP1TemplateError("v2 inactive current state changed")

    return [
        "immutable v1 supersession history",
        "inactive P0-gated authority",
        "family-atomic cyclic cross-fit",
        "direction-explicit primary contrast",
        "fixed compute envelope",
        "duplicate-free response-blind matching",
        "explicit field equivalence and power-law competence",
        "median co-primary and non-rescuing sensitivity roles",
        "cross-fit dependence and no-inference boundary",
        "no-repair stop rules",
        "zero execution and claim state",
    ]


def _finite_positive_logs(values: Mapping[str, float], label: str) -> dict[str, float]:
    if not values:
        raise ResponseFidelityP1TemplateError(f"{label} field-error trace is required")
    if any(not math.isfinite(value) or value <= 0 for value in values.values()):
        raise ResponseFidelityP1TemplateError(
            f"{label} field errors must be finite and positive"
        )
    return {key: math.log(value) for key, value in values.items()}


def _minimum_unique_assignment(
    logs: Mapping[str, float], targets: Sequence[float]
) -> tuple[str, ...] | None:
    if len(logs) < len(targets):
        return None
    keys = tuple(sorted(logs))
    return min(
        itertools.permutations(keys, len(targets)),
        key=lambda assignment: (
            sum(abs(logs[key] - target) for key, target in zip(assignment, targets)),
            assignment,
        ),
    )


def select_unique_iso_error_matches(
    left_field_errors: Mapping[str, float],
    right_field_errors: Mapping[str, float],
    *,
    quantiles: Sequence[float] = (0.25, 0.5, 0.75),
    maximum_log_distance: float = math.log(1.01),
) -> list[IsoErrorMatch]:
    """Jointly assign distinct checkpoints using calibration field error only."""

    if len(set(quantiles)) != len(quantiles) or any(not 0 < value < 1 for value in quantiles):
        raise ResponseFidelityP1TemplateError(
            "v2 iso-error quantiles must be unique and inside (0, 1)"
        )
    if not math.isfinite(maximum_log_distance) or maximum_log_distance <= 0:
        raise ResponseFidelityP1TemplateError(
            "v2 checkpoint caliper must be finite and positive"
        )
    left_logs = _finite_positive_logs(left_field_errors, "left")
    right_logs = _finite_positive_logs(right_field_errors, "right")
    lower = max(min(left_logs.values()), min(right_logs.values()))
    upper = min(max(left_logs.values()), max(right_logs.values()))
    if not lower < upper:
        return []
    targets = tuple(lower + float(quantile) * (upper - lower) for quantile in quantiles)
    left_assignment = _minimum_unique_assignment(left_logs, targets)
    right_assignment = _minimum_unique_assignment(right_logs, targets)
    if left_assignment is None or right_assignment is None:
        return []
    return [
        IsoErrorMatch(
            quantile=float(quantile),
            target_log_field_error=target,
            left_checkpoint=left_key,
            right_checkpoint=right_key,
            left_field_error=float(left_field_errors[left_key]),
            right_field_error=float(right_field_errors[right_key]),
            within_checkpoint_caliper=(
                abs(left_logs[left_key] - target) <= maximum_log_distance
                and abs(right_logs[right_key] - target) <= maximum_log_distance
            ),
        )
        for quantile, target, left_key, right_key in zip(
            quantiles, targets, left_assignment, right_assignment
        )
    ]


def power_law_competent(
    upper_log_error_ratio: float, *, margin: float = math.log(1.02)
) -> bool:
    """One-sided noninferiority: model/power-law upper bound is at most 1.02."""

    return math.isfinite(upper_log_error_ratio) and upper_log_error_ratio <= margin


def same_direction_seed_count(
    pooled_response_contrast: float, seed_specific_contrasts: Sequence[float]
) -> int:
    """Count nonzero seed contrasts whose sign agrees with the pooled contrast."""

    if (
        not math.isfinite(pooled_response_contrast)
        or len(seed_specific_contrasts) != 5
        or any(not math.isfinite(value) for value in seed_specific_contrasts)
    ):
        raise ResponseFidelityP1TemplateError(
            "v2 direction rule requires one pooled and five finite seed contrasts"
        )
    if pooled_response_contrast == 0:
        return 0
    sign = 1 if pooled_response_contrast > 0 else -1
    return sum((value > 0) - (value < 0) == sign for value in seed_specific_contrasts)


def co_primary_screen_passes(
    *,
    checkpoint_qualified: bool,
    field_ci_lower: float,
    field_ci_upper: float,
    left_power_law_upper: float,
    right_power_law_upper: float,
    paired_response_log_ratio: float,
    paired_interval_lower: float,
    paired_interval_upper: float,
    paired_seed_contrasts: Sequence[float],
    tangent_response_log_ratio: float,
    tangent_interval_lower: float,
    tangent_interval_upper: float,
    tangent_seed_contrasts: Sequence[float],
) -> bool:
    """Apply the two co-primary descriptive screening requirements."""

    ratios = (paired_response_log_ratio, tangent_response_log_ratio)
    intervals = (
        (paired_interval_lower, paired_interval_upper),
        (tangent_interval_lower, tangent_interval_upper),
    )
    seed_contrasts = (paired_seed_contrasts, tangent_seed_contrasts)
    intervals_are_finite_and_ordered = all(
        math.isfinite(lower) and math.isfinite(upper) and lower <= upper
        for lower, upper in intervals
    )
    intervals_exclude_zero = all(upper < 0 or lower > 0 for lower, upper in intervals)
    common_nonzero_sign = ratios[0] * ratios[1] > 0
    return (
        checkpoint_qualified
        and field_equivalent(field_ci_lower, field_ci_upper, margin=math.log(1.01))
        and power_law_competent(left_power_law_upper)
        and power_law_competent(right_power_law_upper)
        and all(math.isfinite(value) for value in ratios)
        and intervals_are_finite_and_ordered
        and all(lower <= ratio <= upper for ratio, (lower, upper) in zip(ratios, intervals))
        and intervals_exclude_zero
        and common_nonzero_sign
        and all(abs(value) >= math.log(1.1) for value in ratios)
        and all(
            same_direction_seed_count(ratio, seeds) >= 4
            for ratio, seeds in zip(ratios, seed_contrasts)
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("config", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    print(
        json.dumps(
            {"status": "valid_inactive_template_v2", "checks": validate_config(config)}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
