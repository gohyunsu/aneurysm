"""Validation utilities for the inactive Aneumo confirmation template v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


class ConfirmationTemplateError(ValueError):
    """Raised when the non-authoritative confirmation template drifts."""


EXPECTED_P1_SHA256 = "fb18827b6153422f2e97c7cf6151c653b0490f09e2942572c064dc1ea66adbc0"
LOG_1_02 = 0.01980262729617973


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConfirmationTemplateError(message)


def select_family_ids(
    eligible_family_ids: Iterable[str],
    historical_family_ids: Iterable[str],
    *,
    count: int,
    seed: int,
) -> list[str]:
    """Outcome-blind deterministic selection used by a future registered manifest."""

    historical = {str(item) for item in historical_family_ids}
    eligible = [str(item) for item in eligible_family_ids]
    _require(len(eligible) == len(set(eligible)), "eligible family IDs must be unique")
    remaining = [item for item in eligible if item not in historical]
    _require(len(remaining) >= count, "fewer eligible nonhistorical families than required")

    def key(item: str) -> tuple[str, str]:
        digest = hashlib.sha256(f"{seed}:{item}".encode("utf-8")).hexdigest()
        return digest, item

    return sorted(remaining, key=key)[:count]


def confirmation_pass(summary: dict[str, Any]) -> bool:
    """Evaluate only the predeclared conjunction; no secondary endpoint can rescue it."""

    required = {
        "complete",
        "selected_family_count",
        "field_upper_log_candidate_over_direct",
        "power_law_upper_log_candidate_over_control",
        "paired_response_lower_log_direct_over_candidate",
        "tangent_lower_log_direct_over_candidate",
        "paired_response_point_ratio",
        "tangent_point_ratio",
        "paired_response_positive_seed_count",
        "tangent_positive_seed_count",
    }
    _require(required <= summary.keys(), "confirmation summary is incomplete")
    numeric = [
        summary["field_upper_log_candidate_over_direct"],
        summary["power_law_upper_log_candidate_over_control"],
        summary["paired_response_lower_log_direct_over_candidate"],
        summary["tangent_lower_log_direct_over_candidate"],
        summary["paired_response_point_ratio"],
        summary["tangent_point_ratio"],
    ]
    _require(all(math.isfinite(float(value)) for value in numeric), "metrics must be finite")
    return bool(
        summary["complete"]
        and summary["selected_family_count"] == 100
        and summary["field_upper_log_candidate_over_direct"] <= LOG_1_02
        and summary["power_law_upper_log_candidate_over_control"] <= LOG_1_02
        and summary["paired_response_lower_log_direct_over_candidate"] > 0.0
        and summary["tangent_lower_log_direct_over_candidate"] > 0.0
        and summary["paired_response_point_ratio"] >= 1.10
        and summary["tangent_point_ratio"] >= 1.10
        and summary["paired_response_positive_seed_count"] >= 4
        and summary["tangent_positive_seed_count"] >= 4
    )


def validate_config(config: dict[str, Any]) -> list[str]:
    _require(
        config.get("schema_version")
        == "aurora.aneumo_response_fidelity_confirmation_template.v1",
        "wrong schema version",
    )
    _require(
        config.get("status")
        == "draft_non_authoritative_blocked_on_p0_p1_bounded_development_and_fresh_reentry",
        "template must remain inactive",
    )

    activation = config["activation_boundary"]
    _require(not activation["this_file_can_be_executed"], "template cannot execute")
    _require(not activation["this_file_can_be_submitted_to_pbs"], "template cannot submit")
    _require(not activation["confirmation_registered"], "template is not registration")
    _require(activation["real_p0_observed_verdict"] is None, "P0 verdict cannot be invented")
    _require(activation["p1_observed_verdict"] is None, "P1 verdict cannot be invented")
    _require(
        activation["p1_required_template_sha256"] == EXPECTED_P1_SHA256,
        "P1 v3 dependency drifted",
    )
    _require(
        not activation["bounded_development_candidate_frozen"]
        and not activation["fresh_seed_or_disjoint_split_reentry_passed"]
        and not activation["confirmation_manifest_frozen_before_any_confirmation_field_read"],
        "future gates cannot be pre-passed",
    )

    sample = config["confirmation_sample"]
    _require(sample["required_new_base_family_count"] == 100, "confirmation requires 100 new families")
    _require(sample["historical_compact_base_family_count"] == 32, "historical count drifted")
    _require(sample["all_historical_train_validation_test_base_families_excluded"], "historical families must be excluded")
    _require(not sample["historical_six_test_families_can_count_toward_confirmation"], "old test cannot count")
    _require(sample["selection_seed"] == 2027081301, "family selection seed drifted")
    _require(sample["case_policy"].startswith("use_all_release_cases"), "all cases are required")
    _require(sample["post_result_sample_enlargement_allowed"] is False, "sample enlargement is forbidden")
    _require("velocity_or_pressure_value" in sample["selection_information_forbidden"], "field-blind selection is required")

    models = config["frozen_models"]
    _require(not models["training_or_tuning_on_confirmation_allowed"], "confirmation cannot train")
    _require(not models["checkpoint_selection_on_confirmation_allowed"], "confirmation cannot select checkpoints")
    _require(models["training_seed_count"] == 5 and models["all_five_seed_checkpoints_required"], "five frozen seeds are required")
    _require(models["same_backbone_parameter_optimizer_sampler_precision_and_update_budget"], "primary pair must remain matched")
    _require(not models["descriptive_controls_can_rescue_primary_failure"], "descriptive controls cannot rescue")

    aggregation = config["family_level_aggregation"]
    _require(aggregation["seed_level"].startswith("mean_over_five"), "seed averaging must precede resampling")
    _require(aggregation["bootstrap_unit"] == "base_family", "family is the bootstrap unit")
    _require(not aggregation["nodes_cases_flows_or_seeds_treated_as_independent_replicates"], "pseudoreplication is forbidden")

    endpoints = config["primary_endpoints"]
    _require(endpoints["field_noninferiority_margin_log_ratio"] == LOG_1_02, "field margin drifted")
    _require(endpoints["candidate_power_law_competence_margin_log_ratio"] == LOG_1_02, "competence margin drifted")
    _require(endpoints["minimum_point_estimate_multiplicative_response_reduction"] == 0.1, "effect floor drifted")
    _require(endpoints["minimum_positive_seed_count_per_response_endpoint"] == 4, "seed direction drifted")
    _require(not endpoints["zero_seed_ties_count_as_positive"], "zero ties cannot count")

    inference = config["confirmatory_inference"]
    _require(inference["family_bootstrap_replicates"] == 10000, "bootstrap count drifted")
    _require(inference["family_bootstrap_seed"] == 2027081302, "bootstrap seed drifted")
    _require(inference["global_rule"].startswith("intersection_union"), "primary claim must be conjunctive")
    _require(not inference["exact_p_value_reported"], "exact p-values are not registered")
    _require(not inference["formal_power_claim_reported"], "formal power is not established")
    _require(not inference["secondary_endpoint_can_rescue_primary_failure"], "secondary rescue is forbidden")
    _require(len(inference["pass_requires"]) == 6, "six primary requirements are required")

    figure = config["interpretable_figure"]
    _require(len(figure["family_roles"]) == 3, "worst, typical and best roles are required")
    _require(figure["family_roles"][0].endswith("candidate_worst_case"), "candidate failure must be shown")
    _require(figure["same_coordinates_camera_and_reference_derived_color_range"], "visual comparison must be matched")
    _require(not figure["favorable_only_case_selection_allowed"], "favorable-only figures are forbidden")
    _require(not figure["clinical_interpretation_allowed"], "clinical overclaim is forbidden")

    execution = config["compute_and_execution"]
    _require(execution["execution_server"] == "introai9" and execution["pbs_only"], "introai9 PBS only")
    _require(not execution["login_node_gpu_allowed"] and not execution["junjinyong_allowed"], "forbidden compute route")
    _require(execution["maximum_confirmation_gpu_hours"] == 40.0, "confirmation cap drifted")
    _require(not execution["gpu_authorized_now"] and not execution["pbs_job_submitted"] and not execution["gpu_job_submitted"], "no current compute authority")

    stopping = config["stopping_and_claim_deletion"]
    _require(stopping["all_100_families_all_eligible_cases_all_flows_and_all_five_seeds_required"], "complete factorial is required")
    _require(not stopping["partial_aggregation_allowed"], "partial aggregation is forbidden")
    _require(not stopping["same_version_repair_rerun_or_threshold_margin_sample_rule_change_after_any_confirmation_field_or_prediction_read_allowed"], "post-read repair is forbidden")
    _require(not stopping["confirmation_pass_authorizes_submission_automatically"], "confirmation alone cannot authorize submission")

    state = config["current_state"]
    _require(all(value is False for key, value in state.items() if key != "scientific_result_count"), "all current state flags must be false")
    _require(state["scientific_result_count"] == 0, "no confirmation result exists")

    return [
        "inactive multi-gate authority",
        "100 new family outcome-blind selection",
        "historical-family exclusion and no substitution",
        "frozen same-backbone five-seed models",
        "family-first non-pseudoreplicated aggregation",
        "conjunctive field and response confirmation",
        "fixed confidence-bound and effect-size rules",
        "failure-revealing interpretable figure",
        "bounded introai9 inference-only compute",
        "no-repair claim-deletion boundary",
        "zero execution and claim state",
    ]


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("config")
    args = parser.parse_args()
    checks = validate_config(load_config(args.config))
    print(json.dumps({"status": "valid_inactive_confirmation_template_v1", "checks": checks}))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
