"""Validation utilities for the inactive Aneumo confirmation template v2."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


class ConfirmationTemplateV2Error(ValueError):
    """Raised when the non-authoritative v2 confirmation design drifts."""


EXPECTED_V1_CONFIG_SHA256 = "aa2cf90f9b1d34ecf74f94ef8eb88559671458e126ab5004d1ae24024bc910ec"
EXPECTED_V1_VALIDATOR_SHA256 = "a03c9b754fc857298a6b8a136d7651edfcaa17092f9551b1a40cdd03a0958aac"
EXPECTED_P1_SHA256 = "fb18827b6153422f2e97c7cf6151c653b0490f09e2942572c064dc1ea66adbc0"
LOG_1_02 = 0.01980262729617973
MAX_OBSERVED_DEVELOPMENT_SD = 0.29810546005930777
ONE_SIDED_95_Z = 1.6448536269514722


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConfirmationTemplateV2Error(message)


def select_family_ids(
    eligible_family_ids: Iterable[str],
    historical_family_ids: Iterable[str],
    *,
    count: int,
    seed: int,
) -> list[str]:
    """Return the outcome-blind hash order for a future public manifest."""

    historical = {str(item) for item in historical_family_ids}
    eligible = [str(item) for item in eligible_family_ids]
    _require(len(eligible) == len(set(eligible)), "eligible family IDs must be unique")
    remaining = [item for item in eligible if item not in historical]
    _require(len(remaining) >= count, "fewer eligible nonhistorical families than required")

    def key(item: str) -> tuple[str, str]:
        digest = hashlib.sha256(f"{seed}:{item}".encode("utf-8")).hexdigest()
        return digest, item

    return sorted(remaining, key=key)[:count]


def wilson_lower_bound(successes: int, total: int, *, z: float = ONE_SIDED_95_Z) -> float:
    """One-sided Wilson lower bound used as a family-prevalence safeguard."""

    _require(isinstance(successes, int) and isinstance(total, int), "counts must be integers")
    _require(total > 0 and 0 <= successes <= total, "invalid Wilson counts")
    proportion = successes / total
    z2 = z * z
    numerator = proportion + z2 / (2.0 * total) - z * math.sqrt(
        proportion * (1.0 - proportion) / total + z2 / (4.0 * total * total)
    )
    return numerator / (1.0 + z2 / total)


def prefield_precision_viability(
    paired_response_family_sd: float,
    tangent_family_sd: float,
) -> bool:
    """Planning-only adequacy gate; it is not confirmatory inference."""

    values = (float(paired_response_family_sd), float(tangent_family_sd))
    _require(all(math.isfinite(value) and value >= 0.0 for value in values), "invalid SD")
    return all(value <= MAX_OBSERVED_DEVELOPMENT_SD for value in values)


def projected_gpu_hours(
    *,
    selected_case_flow_count: int,
    upper_seconds_per_case_flow_model_seed: float,
) -> float:
    """Project the complete two-model, five-seed inference workload."""

    _require(
        isinstance(selected_case_flow_count, int) and selected_case_flow_count > 0,
        "selected case-flow count must be positive",
    )
    seconds = float(upper_seconds_per_case_flow_model_seed)
    _require(math.isfinite(seconds) and seconds > 0.0, "inference seconds must be positive")
    return selected_case_flow_count * 2 * 5 * seconds / 3600.0


def confirmation_pass(summary: dict[str, Any]) -> bool:
    """Evaluate the predeclared non-compensatory v2 conjunction."""

    required = {
        "complete",
        "selected_family_count",
        "prefield_precision_viability_passed",
        "prefield_compute_viability_passed",
        "field_upper_log_candidate_over_direct",
        "power_law_upper_log_candidate_over_control",
        "paired_response_lower_log_direct_over_candidate",
        "tangent_lower_log_direct_over_candidate",
        "paired_response_geometric_mean_ratio",
        "tangent_geometric_mean_ratio",
        "paired_response_positive_seed_count",
        "tangent_positive_seed_count",
        "paired_response_family_win_count",
        "tangent_family_win_count",
    }
    _require(required <= summary.keys(), "confirmation summary is incomplete")
    numeric = [
        summary["field_upper_log_candidate_over_direct"],
        summary["power_law_upper_log_candidate_over_control"],
        summary["paired_response_lower_log_direct_over_candidate"],
        summary["tangent_lower_log_direct_over_candidate"],
        summary["paired_response_geometric_mean_ratio"],
        summary["tangent_geometric_mean_ratio"],
    ]
    _require(all(math.isfinite(float(value)) for value in numeric), "metrics must be finite")
    selected = summary["selected_family_count"]
    _require(isinstance(selected, int), "selected family count must be an integer")
    paired_wilson = wilson_lower_bound(summary["paired_response_family_win_count"], selected)
    tangent_wilson = wilson_lower_bound(summary["tangent_family_win_count"], selected)
    return bool(
        summary["complete"]
        and selected == 100
        and summary["prefield_precision_viability_passed"]
        and summary["prefield_compute_viability_passed"]
        and summary["field_upper_log_candidate_over_direct"] <= LOG_1_02
        and summary["power_law_upper_log_candidate_over_control"] <= LOG_1_02
        and summary["paired_response_lower_log_direct_over_candidate"] > 0.0
        and summary["tangent_lower_log_direct_over_candidate"] > 0.0
        and summary["paired_response_geometric_mean_ratio"] >= 1.10
        and summary["tangent_geometric_mean_ratio"] >= 1.10
        and summary["paired_response_positive_seed_count"] >= 4
        and summary["tangent_positive_seed_count"] >= 4
        and paired_wilson > 0.50
        and tangent_wilson > 0.50
    )


def validate_config(config: dict[str, Any]) -> list[str]:
    _require(
        config.get("schema_version")
        == "aurora.aneumo_response_fidelity_confirmation_template.v2",
        "wrong schema version",
    )
    _require(
        config.get("status")
        == "draft_non_authoritative_blocked_on_p0_p1_bounded_development_fresh_reentry_and_prefield_viability",
        "template must remain inactive",
    )

    supersession = config["supersession"]
    _require(
        supersession["supersedes_template_sha256"] == EXPECTED_V1_CONFIG_SHA256
        and supersession["supersedes_validator_sha256"] == EXPECTED_V1_VALIDATOR_SHA256,
        "v1 provenance drifted",
    )
    _require(
        not supersession["v1_executed"]
        and not supersession["v1_confirmation_metadata_read"]
        and not supersession["v1_confirmation_field_read"]
        and not supersession["v1_model_prediction_read"],
        "v1 can only be superseded before evidence access",
    )

    activation = config["activation_boundary"]
    _require(not activation["this_file_can_be_executed"], "template cannot execute")
    _require(not activation["this_file_can_be_submitted_to_pbs"], "template cannot submit")
    _require(not activation["confirmation_registered"], "template is not registration")
    _require(activation["real_p0_observed_verdict"] is None, "P0 verdict cannot be invented")
    _require(activation["p1_observed_verdict"] is None, "P1 verdict cannot be invented")
    _require(activation["p1_required_template_sha256"] == EXPECTED_P1_SHA256, "P1 dependency drifted")
    for key in (
        "bounded_development_candidate_frozen",
        "fresh_seed_or_disjoint_split_reentry_passed",
        "prefield_precision_viability_passed",
        "prefield_compute_viability_passed",
        "confirmation_manifest_frozen_before_any_confirmation_field_read",
    ):
        _require(not activation[key], f"future gate cannot be pre-passed: {key}")

    prior = config["direct_prior_boundary"]
    _require(
        prior["aneumo_reported_base_geometry_count"] == 427
        and prior["aneumo_reported_deformed_shape_count"] == 10660
        and prior["aneumo_reported_flow_count"] == 8,
        "Aneumo source counts drifted",
    )
    _require(
        prior["aneumo_already_studies_training_and_validation_flow_condition_diversity"]
        and prior["hemo_mpo_already_maps_geometry_and_boundary_conditions_to_full_fields"]
        and prior["sc_fno_already_owns_generic_solution_sensitivity_mismatch"]
        and not prior["multi_flow_boundary_condition_operator_or_component_stack_claim_allowed"],
        "direct-prior subtraction is incomplete",
    )

    sample = config["confirmation_sample"]
    _require(sample["reported_total_base_family_count"] == 427, "reported population drifted")
    _require(sample["historical_compact_base_family_count"] == 32, "historical count drifted")
    _require(sample["maximum_post_exclusion_base_family_count_before_eligibility_audit"] == 395, "post-exclusion maximum drifted")
    _require(sample["required_new_base_family_count"] == 100, "confirmation requires 100 new families")
    _require(math.isclose(sample["maximum_population_sampling_fraction"], 100.0 / 395.0), "sampling fraction drifted")
    _require(sample["all_historical_train_validation_test_base_families_excluded"], "historical families must be excluded")
    _require(not sample["historical_six_test_families_can_count_toward_confirmation"], "old test cannot count")
    _require(sample["selection_seed"] == 2027081301, "family selection seed drifted")
    _require(sample["case_policy"].startswith("use_all_release_cases"), "all cases are required")
    _require(not sample["post_result_sample_enlargement_allowed"], "sample enlargement is forbidden")
    _require("velocity_or_pressure_value" in sample["selection_information_forbidden"], "selection must be field-blind")

    viability = config["prefield_viability"]
    _require(not viability["uses_confirmation_field_or_prediction"], "viability must be prefield")
    _require(viability["minimum_complete_development_family_count"] == 20, "development count drifted")
    _require(viability["planning_confirmation_family_count"] == 100, "planning n drifted")
    _require(viability["planning_one_sided_alpha"] == 0.05 and viability["planning_target_power"] == 0.8, "planning targets drifted")
    _require(viability["maximum_observed_20_family_sample_sd_per_response_endpoint"] == MAX_OBSERVED_DEVELOPMENT_SD, "SD gate drifted")
    _require(viability["both_response_endpoints_must_pass_precision_gate"], "both endpoints need precision")
    _require(viability["precision_gate_is_planning_adequacy_not_paper_power_or_normality_claim"], "planning cannot become a paper claim")
    _require(viability["maximum_projected_confirmation_gpu_hours"] == 40.0, "compute cap drifted")

    models = config["frozen_models"]
    _require(not models["training_or_tuning_on_confirmation_allowed"], "confirmation cannot train")
    _require(not models["checkpoint_selection_on_confirmation_allowed"], "confirmation cannot select checkpoints")
    _require(models["training_seed_count"] == 5 and models["all_five_seed_checkpoints_required"], "five frozen seeds required")
    _require(models["same_backbone_parameter_optimizer_sampler_precision_and_update_budget"], "pair must remain matched")
    _require(not models["descriptive_controls_can_rescue_primary_failure"], "descriptive controls cannot rescue")

    estimators = config["exact_estimators"]
    _require(estimators["positive_error_floor"] == 2.220446049250313e-16, "error floor drifted")
    _require(estimators["family_seed_contrast"].startswith("arithmetic_mean_case_log_contrast"), "case aggregation drifted")
    _require(estimators["family_contrast"].startswith("arithmetic_mean_family_seed_contrast"), "seed aggregation drifted")
    _require(estimators["reported_multiplicative_ratio"].startswith("exp_population_log_contrast"), "geometric ratio drifted")
    _require(estimators["bootstrap_unit"] == "base_family", "family is bootstrap unit")
    _require(not estimators["nodes_cases_flows_or_seeds_treated_as_independent_replicates"], "pseudoreplication forbidden")

    endpoints = config["primary_endpoints"]
    _require(endpoints["field_noninferiority_margin_log_ratio"] == LOG_1_02, "field margin drifted")
    _require(endpoints["candidate_power_law_competence_margin_log_ratio"] == LOG_1_02, "competence margin drifted")
    _require(endpoints["minimum_point_estimate_multiplicative_response_reduction"] == 0.1, "effect floor drifted")
    _require(endpoints["minimum_positive_seed_count_per_response_endpoint"] == 4, "seed direction drifted")
    _require(not endpoints["zero_seed_ties_count_as_positive"], "zero ties cannot count")
    _require(endpoints["family_win_prevalence_lower_bound_must_exceed"] == 0.5, "family prevalence null drifted")
    _require(endpoints["minimum_family_win_count_when_n_is_100"] == 59, "family win count drifted")
    _require(wilson_lower_bound(58, 100) <= 0.5 < wilson_lower_bound(59, 100), "Wilson boundary drifted")

    inference = config["confirmatory_inference"]
    _require(inference["family_bootstrap_replicates"] == 10000, "bootstrap count drifted")
    _require(inference["family_bootstrap_seed"] == 2027081302, "bootstrap seed drifted")
    _require(inference["global_rule"].startswith("intersection_union"), "primary claim must be conjunctive")
    _require(not inference["exact_p_value_reported"] and not inference["formal_power_claim_reported"], "unsupported inference")
    _require(not inference["secondary_endpoint_can_rescue_primary_failure"], "secondary rescue forbidden")
    _require(len(inference["pass_requires"]) == 8, "eight primary requirements required")

    figure = config["interpretable_figure"]
    _require(figure["family_ranking_statistic"].startswith("half_paired_response_plus_half_tangent"), "figure rank drifted")
    _require(len(figure["family_roles"]) == 3, "worst, typical and best required")
    _require(figure["family_roles"][0].endswith("candidate_worst_case"), "candidate failure must be shown")
    _require(figure["same_coordinates_camera_and_reference_derived_color_range"], "visual comparison must be matched")
    _require(not figure["favorable_only_case_selection_allowed"] and not figure["clinical_interpretation_allowed"], "figure overclaim forbidden")

    execution = config["compute_and_execution"]
    _require(execution["execution_server"] == "introai9" and execution["pbs_only"], "introai9 PBS only")
    _require(not execution["login_node_gpu_allowed"] and not execution["junjinyong_allowed"], "forbidden compute route")
    _require(execution["maximum_confirmation_gpu_hours"] == 40.0, "confirmation cap drifted")
    _require(not execution["gpu_authorized_now"] and not execution["pbs_job_submitted"] and not execution["gpu_job_submitted"], "no current compute authority")

    stopping = config["stopping_and_claim_deletion"]
    _require(stopping["all_100_families_all_eligible_cases_all_flows_and_all_five_seeds_required"], "complete factorial required")
    _require(not stopping["partial_aggregation_allowed"], "partial aggregation forbidden")
    _require(not stopping["same_version_repair_rerun_or_threshold_margin_sample_rule_change_after_any_confirmation_field_or_prediction_read_allowed"], "post-read repair forbidden")
    _require(not stopping["confirmation_pass_authorizes_submission_automatically"], "confirmation alone cannot authorize submission")

    state = config["current_state"]
    _require(all(value is False for key, value in state.items() if key != "scientific_result_count"), "all current flags must be false")
    _require(state["scientific_result_count"] == 0, "no confirmation result exists")

    return [
        "pre-evidence v1 supersession",
        "direct-prior-complete residual claim boundary",
        "427-to-395 source population accounting",
        "100 new family field-blind selection",
        "prefield precision adequacy gate",
        "prefield complete-workload compute gate",
        "same-backbone five-seed frozen comparison",
        "case-log to family geometric estimator",
        "family-only bootstrap without pseudoreplication",
        "conjunctive field and response requirements",
        "majority-family Wilson safeguard",
        "failure-revealing deterministic figure",
        "zero authority execution and claim state",
    ]


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("config")
    args = parser.parse_args()
    checks = validate_config(load_config(args.config))
    print(json.dumps({"status": "valid_inactive_confirmation_template_v2", "checks": checks}))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
