"""Fail-closed utilities for the inactive Aneumo response-fidelity P1 template.

This module does not train a model, read a dataset, select an architecture, or
authorize execution.  It validates the pre-P0 design template and implements
only response-blind iso-error matching and small deterministic decision
helpers that can be tested on synthetic numbers.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


class ResponseFidelityP1TemplateError(ValueError):
    """Raised when the inactive P1 design boundary is changed."""


@dataclass(frozen=True)
class IsoErrorMatch:
    """One response-blind checkpoint pair on calibration field error."""

    quantile: float
    target_log_field_error: float
    left_checkpoint: str
    right_checkpoint: str
    left_field_error: float
    right_field_error: float
    within_checkpoint_caliper: bool


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ResponseFidelityP1TemplateError(f"invalid config: {exc}") from exc
    if not isinstance(payload, dict):
        raise ResponseFidelityP1TemplateError("config root must be an object")
    validate_config(payload)
    return payload


def _all_false(mapping: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return all(mapping.get(key) is False for key in keys)


def validate_config(config: Mapping[str, Any]) -> list[str]:
    """Validate that the template remains inactive and outcome-blind."""

    if (
        config.get("schema_version")
        != "aurora.aneumo_response_fidelity_p1_template.v1"
        or config.get("template_id")
        != "aneumo_field_error_iso_matched_failure_p1_template_v1"
        or config.get("status")
        != "draft_non_authoritative_blocked_on_real_p0_v2_all_11_pass"
    ):
        raise ResponseFidelityP1TemplateError("template identity changed")

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
        or activation.get("activation_requires_separate_registered_config") is not True
        or activation.get("activation_requires_exact_cache_path_and_execution_envelope")
        is not True
        or activation.get("activation_requires_public_commit_before_any_model_prediction")
        is not True
        or activation.get("core_match_or_inference_change_requires_new_evidence_version")
        is not True
    ):
        raise ResponseFidelityP1TemplateError("P0 activation boundary changed")

    question = config.get("scientific_question", {})
    if (
        question.get("independent_unit") != "aneumo_generation_base_family"
        or question.get("primary_field_metric")
        != "node_weighted_velocity_relative_l2"
        or question.get("primary_response_endpoints")
        != ["paired_response_relative_l2", "discrete_tangent_relative_l2"]
        or question.get("clinical_or_biological_interpretation_allowed") is not False
    ):
        raise ResponseFidelityP1TemplateError("scientific estimand changed")

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
        or data.get("fold_construction")
        != "seeded_permutation_into_five_equal_blocks_outer_block_k_calibration_block_k_plus_1_mod_5_fit_remaining_three_blocks"
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
        raise ResponseFidelityP1TemplateError("family split or sealed-data boundary changed")

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
        raise ResponseFidelityP1TemplateError("information set changed")

    baselines = config.get("baselines", {})
    expected_learned = [
        "pointwise_conditional_mlp",
        "deeponet_anchor_conditioned",
        "deltaphi_style_anchor_residual",
        "meshgraphnet_anchor_conditioned",
    ]
    expected_pairs = [
        ["meshgraphnet_anchor_conditioned", "deltaphi_style_anchor_residual"],
    ]
    expected_secondary_pairs = [
        ["deeponet_anchor_conditioned", "deltaphi_style_anchor_residual"],
        ["pointwise_conditional_mlp", "deltaphi_style_anchor_residual"],
    ]
    if (
        baselines.get("deterministic_controls")
        != ["linear_mass_flow_scaling", "train_fitted_power_law_scaling"]
        or baselines.get("learned_same_information_set_models") != expected_learned
        or baselines.get("primary_pairs_in_order") != expected_pairs
        or baselines.get("secondary_non_gating_pairs") != expected_secondary_pairs
        or baselines.get("historical_v1e_role")
        != "diagnostic_only_not_primary_pair_due_to_different_information_set"
        or baselines.get("proposal_model_present") is not False
        or baselines.get("model_name_can_satisfy_novelty") is not False
    ):
        raise ResponseFidelityP1TemplateError("baseline or pair family changed")

    compute = config.get("compute_matching", {})
    expected_fractions = [index / 20 for index in range(1, 21)]
    if (
        compute.get("training_seeds")
        != [2027081211, 2027081212, 2027081213, 2027081214, 2027081215]
        or compute.get("target_trainable_parameters") != 2_000_000
        or compute.get("parameter_relative_tolerance") != 0.1
        or compute.get("optimizer_updates_per_run") != 20_000
        or compute.get("node_condition_samples_per_update") != 8192
        or compute.get("checkpoint_fractions") != expected_fractions
        or compute.get("same_container_optimizer_batch_sampler_and_precision") is not True
        or compute.get("actual_flops_gpu_seconds_peak_memory_and_inference_latency_reported")
        is not True
        or compute.get("total_p1_gpu_hour_cap") != 160.0
        or compute.get("gpu_authorized_now") is not False
        or compute.get("execution_server") != "introai9"
        or compute.get("pbs_only") is not True
        or compute.get("login_node_gpu_allowed") is not False
        or compute.get("junjinyong_allowed") is not False
    ):
        raise ResponseFidelityP1TemplateError("compute-matching boundary changed")

    matching = config.get("field_only_selection_and_matching", {})
    if (
        matching.get("response_metrics_available_during_selection") is not False
        or matching.get("checkpoint_selection_metric")
        != "calibration_family_mean_node_weighted_velocity_relative_l2_only"
        or matching.get("common_support_scale") != "natural_log_field_relative_l2"
        or matching.get("iso_error_quantiles") != [0.25, 0.5, 0.75]
        or matching.get("iso_error_levels_derived_from")
        != "pair_seed_calibration_fold_common_field_error_support_only"
        or matching.get("checkpoint_rule")
        != "nearest_predeclared_checkpoint_in_absolute_log_field_error"
        or matching.get("maximum_checkpoint_distance") != "log(1.01)"
        or matching.get("outer_field_equivalence_estimand")
        != "paired_family_seed_mean_log_field_error_ratio"
        or matching.get("outer_field_equivalence_margin_log_ratio") != math.log(1.01)
        or matching.get("outer_field_equivalence_interval_level") != 0.9
        or matching.get("both_pair_members_must_be_field_competent_against_power_law")
        is not True
        or matching.get("power_law_field_noninferiority_margin_relative") != 0.02
        or matching.get("unmatched_pair_level_can_be_replaced_or_widened") is not False
    ):
        raise ResponseFidelityP1TemplateError("response-blind field matching changed")

    inference = config.get("inference", {})
    if (
        inference.get("bootstrap_unit") != "aneumo_generation_base_family"
        or inference.get("bootstrap_replicates") != 5000
        or inference.get("bootstrap_seed") != 2027081221
        or inference.get("response_contrast")
        != "paired_family_seed_mean_log_error_ratio"
        or inference.get("response_confidence_level") != 0.95
        or inference.get("primary_null_test")
        != "exact_two_sided_sign_flip_over_20_outer_family_seed_mean_log_error_ratios"
        or inference.get("familywise_alpha") != 0.05
        or inference.get("multiplicity")
        != "holm_over_1_primary_pair_x_3_iso_error_levels_x_2_primary_endpoints"
        or inference.get("minimum_multiplicative_response_gap") != 0.1
        or inference.get("minimum_same_direction_seed_count") != 4
        or inference.get("training_seed_count") != 5
        or inference.get("secondary_endpoint_can_rescue_primary_failure") is not False
    ):
        raise ResponseFidelityP1TemplateError("inference boundary changed")

    stopping = config.get("stopping_and_repair", {})
    if (
        stopping.get("all_models_folds_seeds_required") is not True
        or stopping.get("partial_success_aggregation_allowed") is not False
        or stopping.get("outcome_conditioned_pair_checkpoint_margin_or_threshold_change_allowed")
        is not False
        or stopping.get("same_version_repair_or_rerun_after_metric_access_allowed") is not False
        or stopping.get("missing_common_support_or_no_qualified_pair_action")
        != "close_exact_direction_no_scientific_mismatch"
        or stopping.get("execution_incomplete_action")
        != "close_exact_p1_no_scientific_verdict"
        or stopping.get("p1_pass_authorizes_only")
        != "separate_bounded_validation_only_method_development_registration"
        or stopping.get("p1_pass_authorizes_paper_claim_outer_test_or_submission") is not False
    ):
        raise ResponseFidelityP1TemplateError("stopping or repair boundary changed")

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
        raise ResponseFidelityP1TemplateError("inactive current state changed")

    return [
        "inactive P0-gated authority",
        "family-atomic nested development split",
        "same-information-set baseline pairs",
        "fixed compute envelope",
        "response-blind iso-error matching",
        "clustered multiplicity-aware inference",
        "no-repair stop rules",
        "zero execution and claim state",
    ]


def select_iso_error_matches(
    left_field_errors: Mapping[str, float],
    right_field_errors: Mapping[str, float],
    *,
    quantiles: Sequence[float] = (0.25, 0.5, 0.75),
    maximum_log_distance: float = math.log(1.01),
) -> list[IsoErrorMatch]:
    """Match checkpoints using calibration field error and no response values."""

    if not left_field_errors or not right_field_errors:
        raise ResponseFidelityP1TemplateError("both field-error traces are required")
    if any(not math.isfinite(value) or value <= 0 for value in left_field_errors.values()):
        raise ResponseFidelityP1TemplateError("left field errors must be finite and positive")
    if any(not math.isfinite(value) or value <= 0 for value in right_field_errors.values()):
        raise ResponseFidelityP1TemplateError("right field errors must be finite and positive")
    if any(not 0 < quantile < 1 for quantile in quantiles):
        raise ResponseFidelityP1TemplateError("iso-error quantiles must be inside (0, 1)")

    left_logs = {key: math.log(value) for key, value in left_field_errors.items()}
    right_logs = {key: math.log(value) for key, value in right_field_errors.items()}
    lower = max(min(left_logs.values()), min(right_logs.values()))
    upper = min(max(left_logs.values()), max(right_logs.values()))
    if not lower < upper:
        return []

    matches: list[IsoErrorMatch] = []
    for quantile in quantiles:
        target = lower + float(quantile) * (upper - lower)
        left_key = min(left_logs, key=lambda key: (abs(left_logs[key] - target), key))
        right_key = min(right_logs, key=lambda key: (abs(right_logs[key] - target), key))
        within = (
            abs(left_logs[left_key] - target) <= maximum_log_distance
            and abs(right_logs[right_key] - target) <= maximum_log_distance
        )
        matches.append(
            IsoErrorMatch(
                quantile=float(quantile),
                target_log_field_error=target,
                left_checkpoint=left_key,
                right_checkpoint=right_key,
                left_field_error=float(left_field_errors[left_key]),
                right_field_error=float(right_field_errors[right_key]),
                within_checkpoint_caliper=within,
            )
        )
    return matches


def field_equivalent(
    ci_lower: float,
    ci_upper: float,
    *,
    margin: float = math.log(1.01),
) -> bool:
    """Return whether the complete equivalence interval lies inside the margin."""

    return (
        math.isfinite(ci_lower)
        and math.isfinite(ci_upper)
        and ci_lower <= ci_upper
        and -margin <= ci_lower
        and ci_upper <= margin
    )


def holm_rejections(p_values: Sequence[float], *, alpha: float = 0.05) -> list[bool]:
    """Holm step-down family-wise error control in original input order."""

    if not p_values:
        return []
    if not 0 < alpha < 1 or any(not math.isfinite(p) or not 0 <= p <= 1 for p in p_values):
        raise ResponseFidelityP1TemplateError("invalid Holm inputs")
    ordered = sorted(enumerate(p_values), key=lambda item: (item[1], item[0]))
    rejected = [False] * len(p_values)
    for rank, (index, p_value) in enumerate(ordered):
        threshold = alpha / (len(p_values) - rank)
        if p_value > threshold:
            break
        rejected[index] = True
    return rejected


def exact_two_sided_sign_flip_pvalue(family_contrasts: Sequence[float]) -> float:
    """Exact paired randomization p-value with family as the exchangeable unit."""

    values = tuple(float(value) for value in family_contrasts)
    if not values or len(values) > 20 or any(not math.isfinite(value) for value in values):
        raise ResponseFidelityP1TemplateError("sign-flip inputs require 1 to 20 finite families")
    observed = abs(sum(values) / len(values))
    extreme = 0
    total = 2 ** len(values)
    tolerance = 1e-15
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        statistic = abs(sum(sign * value for sign, value in zip(signs, values)) / len(values))
        extreme += statistic + tolerance >= observed
    return extreme / total


def response_mismatch_cell_passes(
    *,
    field_ci_lower: float,
    field_ci_upper: float,
    response_log_ratio: float,
    response_ci_lower: float,
    response_ci_upper: float,
    holm_rejected: bool,
    same_direction_seed_count: int,
) -> bool:
    """Apply the frozen field-equivalence and material-response decision cell."""

    response_ci_excludes_zero = response_ci_upper < 0 or response_ci_lower > 0
    material = abs(response_log_ratio) >= math.log(1.1)
    return (
        field_equivalent(field_ci_lower, field_ci_upper)
        and response_ci_lower <= response_log_ratio <= response_ci_upper
        and response_ci_excludes_zero
        and material
        and holm_rejected
        and same_direction_seed_count >= 4
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("config", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    print(json.dumps({"status": "valid_inactive_template", "checks": validate_config(config)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
