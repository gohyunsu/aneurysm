"""Pre-evidence validation and synthetic evaluation for confirmation v3.

This module cannot read Aneumo assets or submit work.  It freezes how complete
long-form error rows would later be reduced to family-level evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class ConfirmationTemplateV3Error(ValueError):
    """Raised when the inactive v3 contract or a synthetic fixture drifts."""


EXPECTED_V2_CONFIG_SHA256 = "570bbca4218e1ef22f681c8e308c012b62f92a93807a92dc4953226342f64481"
EXPECTED_V2_VALIDATOR_SHA256 = "7c6dca01253dc7494ba013f72b0c2aee7a7c8ea49fc24e7215fdde97431a0564"
EXPECTED_P1_SHA256 = "fb18827b6153422f2e97c7cf6151c653b0490f09e2942572c064dc1ea66adbc0"
TRAINING_SEEDS = (2027081211, 2027081212, 2027081213, 2027081214, 2027081215)
MODELS = ("candidate", "direct", "power_law")
METRICS = (
    "field_relative_l2",
    "paired_response_relative_l2",
    "discrete_tangent_relative_l2",
)
ROW_FIELDS = ("family_id", "case_id", "seed", "model", "metric", "error")
ERROR_FLOOR = 2.220446049250313e-16
LOG_1_02 = 0.01980262729617973
LOG_1_10 = 0.09531017980432493
ONE_SIDED_95_Z = 1.6448536269514722
UINT64_SPAN = 1 << 64


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConfirmationTemplateV3Error(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def type7_quantile(values: Sequence[float], probability: float) -> float:
    """Hyndman--Fan type-7 quantile with a fully explicit interpolation rule."""

    ordered = sorted(float(value) for value in values)
    _require(ordered and all(math.isfinite(value) for value in ordered), "invalid quantile values")
    p = float(probability)
    _require(math.isfinite(p) and 0.0 <= p <= 1.0, "invalid quantile probability")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * p
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def wilson_lower_bound(successes: int, total: int) -> float:
    """One-sided 95% Wilson lower bound on a family-win proportion."""

    _require(isinstance(successes, int) and isinstance(total, int), "Wilson counts must be integers")
    _require(total > 0 and 0 <= successes <= total, "invalid Wilson counts")
    proportion = successes / total
    z2 = ONE_SIDED_95_Z * ONE_SIDED_95_Z
    numerator = proportion + z2 / (2.0 * total) - ONE_SIDED_95_Z * math.sqrt(
        proportion * (1.0 - proportion) / total + z2 / (4.0 * total * total)
    )
    return numerator / (1.0 + z2 / total)


def _unbiased_sha256_index(*, seed: int, replicate: int, draw: int, size: int) -> int:
    """Map a counter to ``range(size)`` without implementation-dependent PRNG state."""

    _require(size > 0, "bootstrap family count must be positive")
    limit = UINT64_SPAN - (UINT64_SPAN % size)
    attempt = 0
    while True:
        payload = f"{seed}:{replicate}:{draw}:{attempt}".encode("ascii")
        value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
        if value < limit:
            return value % size
        attempt += 1


def shared_family_bootstrap(
    family_contrasts: Mapping[str, Sequence[float]],
    *,
    replicates: int,
    seed: int,
) -> dict[str, dict[str, float]]:
    """Bootstrap all contrasts with the same deterministic family draws."""

    _require(isinstance(replicates, int) and replicates > 0, "replicates must be positive")
    _require(family_contrasts, "at least one contrast is required")
    normalized = {
        str(name): tuple(float(value) for value in values)
        for name, values in family_contrasts.items()
    }
    sizes = {len(values) for values in normalized.values()}
    _require(len(sizes) == 1 and next(iter(sizes)) > 0, "contrast lengths must match")
    size = next(iter(sizes))
    _require(
        all(all(math.isfinite(value) for value in values) for values in normalized.values()),
        "contrasts must be finite",
    )
    distributions = {name: [] for name in normalized}
    for replicate in range(replicates):
        indices = [
            _unbiased_sha256_index(seed=seed, replicate=replicate, draw=draw, size=size)
            for draw in range(size)
        ]
        for name, values in normalized.items():
            distributions[name].append(sum(values[index] for index in indices) / size)
    return {
        name: {
            "lower_0_05": type7_quantile(values, 0.05),
            "upper_0_95": type7_quantile(values, 0.95),
        }
        for name, values in distributions.items()
    }


def _normalise_rows(
    rows: Iterable[Mapping[str, Any]],
    selected_family_ids: Sequence[str],
) -> tuple[dict[tuple[str, str, int, str, str], float], dict[str, tuple[str, ...]], str]:
    selected = tuple(str(family_id) for family_id in selected_family_ids)
    _require(len(selected) == 100 and len(set(selected)) == 100, "exactly 100 unique manifest families required")
    selected_set = set(selected)
    table: dict[tuple[str, str, int, str, str], float] = {}
    cases: dict[str, set[str]] = {family_id: set() for family_id in selected}
    canonical_rows: list[dict[str, Any]] = []
    for raw in rows:
        _require(set(raw) == set(ROW_FIELDS), "error row fields must match the exact schema")
        family_id = str(raw["family_id"])
        case_id = str(raw["case_id"])
        seed = raw["seed"]
        model = str(raw["model"])
        metric = str(raw["metric"])
        value = raw["error"]
        _require(family_id in selected_set, "error row contains an extra family")
        _require(case_id != "", "case ID cannot be empty")
        _require(isinstance(seed, int) and not isinstance(seed, bool) and seed in TRAINING_SEEDS, "unexpected seed")
        _require(model in MODELS, "unexpected model")
        _require(metric in METRICS, "unexpected metric")
        _require(isinstance(value, (int, float)) and not isinstance(value, bool), "error must be numeric")
        error = float(value)
        _require(math.isfinite(error) and error >= 0.0, "error must be finite and nonnegative")
        key = (family_id, case_id, seed, model, metric)
        _require(key not in table, "duplicate error factor cell")
        table[key] = error
        cases[family_id].add(case_id)
        canonical_rows.append(
            {
                "family_id": family_id,
                "case_id": case_id,
                "seed": seed,
                "model": model,
                "metric": metric,
                "error": error,
            }
        )
    frozen_cases: dict[str, tuple[str, ...]] = {}
    for family_id in selected:
        family_cases = tuple(sorted(cases[family_id]))
        _require(family_cases, "every manifest family needs at least one complete case")
        frozen_cases[family_id] = family_cases
        for case_id in family_cases:
            for seed in TRAINING_SEEDS:
                for model in MODELS:
                    for metric in METRICS:
                        _require(
                            (family_id, case_id, seed, model, metric) in table,
                            "missing error factor cell",
                        )
            for metric in METRICS:
                encoded = {
                    struct.pack(">d", table[(family_id, case_id, seed, "power_law", metric)])
                    for seed in TRAINING_SEEDS
                }
                _require(len(encoded) == 1, "power-law errors must be bitwise identical across seed rows")
    canonical_rows.sort(
        key=lambda row: (
            selected.index(row["family_id"]),
            row["case_id"],
            row["seed"],
            MODELS.index(row["model"]),
            METRICS.index(row["metric"]),
        )
    )
    digest = hashlib.sha256(
        json.dumps(
            canonical_rows,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    return table, frozen_cases, digest


def _case_log_ratio(numerator: float, denominator: float) -> float:
    return math.log(max(numerator, ERROR_FLOOR) / max(denominator, ERROR_FLOOR))


def evaluate_complete_error_rows(
    rows: Iterable[Mapping[str, Any]],
    selected_family_ids: Sequence[str],
    *,
    prefield_precision_viability_passed: bool,
    prefield_compute_viability_passed: bool,
    bootstrap_replicates: int = 10000,
    bootstrap_seed: int = 2027081303,
) -> dict[str, Any]:
    """Derive the complete v3 confirmation summary from long-form error rows."""

    _require(isinstance(prefield_precision_viability_passed, bool), "precision gate must be boolean")
    _require(isinstance(prefield_compute_viability_passed, bool), "compute gate must be boolean")
    selected = tuple(str(family_id) for family_id in selected_family_ids)
    table, cases, row_digest = _normalise_rows(rows, selected)
    contrast_specs = {
        "field_candidate_over_direct": ("field_relative_l2", "candidate", "direct"),
        "field_candidate_over_power_law": ("field_relative_l2", "candidate", "power_law"),
        "paired_response_direct_over_candidate": ("paired_response_relative_l2", "direct", "candidate"),
        "paired_response_power_law_over_candidate": ("paired_response_relative_l2", "power_law", "candidate"),
        "tangent_direct_over_candidate": ("discrete_tangent_relative_l2", "direct", "candidate"),
        "tangent_power_law_over_candidate": ("discrete_tangent_relative_l2", "power_law", "candidate"),
    }
    family_seed: dict[str, dict[str, dict[int, float]]] = {
        name: {family_id: {} for family_id in selected} for name in contrast_specs
    }
    for name, (metric, numerator_model, denominator_model) in contrast_specs.items():
        for family_id in selected:
            for seed in TRAINING_SEEDS:
                case_values = [
                    _case_log_ratio(
                        table[(family_id, case_id, seed, numerator_model, metric)],
                        table[(family_id, case_id, seed, denominator_model, metric)],
                    )
                    for case_id in cases[family_id]
                ]
                family_seed[name][family_id][seed] = sum(case_values) / len(case_values)
    family_contrasts = {
        name: [
            sum(family_seed[name][family_id][seed] for seed in TRAINING_SEEDS) / len(TRAINING_SEEDS)
            for family_id in selected
        ]
        for name in contrast_specs
    }
    intervals = shared_family_bootstrap(
        family_contrasts,
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
    )
    response_names = tuple(name for name in contrast_specs if not name.startswith("field_"))
    contrasts: dict[str, dict[str, Any]] = {}
    for name, values in family_contrasts.items():
        population_mean = sum(values) / len(values)
        seed_means = [
            sum(family_seed[name][family_id][seed] for family_id in selected) / len(selected)
            for seed in TRAINING_SEEDS
        ]
        wins = sum(value > 0.0 for value in values)
        contrasts[name] = {
            "population_mean_log_contrast": population_mean,
            "geometric_mean_ratio": math.exp(population_mean),
            "one_sided_95_lower": intervals[name]["lower_0_05"],
            "one_sided_95_upper": intervals[name]["upper_0_95"],
            "positive_seed_count": sum(value > 0.0 for value in seed_means),
            "family_win_count": wins,
            "family_win_wilson_lower": wilson_lower_bound(wins, len(values)),
        }
    field_pass = all(
        contrasts[name]["one_sided_95_lower"] >= -LOG_1_02
        and contrasts[name]["one_sided_95_upper"] <= LOG_1_02
        for name in ("field_candidate_over_direct", "field_candidate_over_power_law")
    )
    response_pass = all(
        contrasts[name]["one_sided_95_lower"] > 0.0
        and contrasts[name]["population_mean_log_contrast"] >= LOG_1_10
        and contrasts[name]["geometric_mean_ratio"] >= 1.10
        and contrasts[name]["positive_seed_count"] >= 4
        and contrasts[name]["family_win_count"] >= 59
        and contrasts[name]["family_win_wilson_lower"] > 0.5
        for name in response_names
    )
    passed = bool(
        prefield_precision_viability_passed
        and prefield_compute_viability_passed
        and field_pass
        and response_pass
    )
    return {
        "schema_version": "aurora.aneumo_response_fidelity_confirmation_summary.v3",
        "complete": True,
        "selected_family_count": len(selected),
        "case_count": sum(len(family_cases) for family_cases in cases.values()),
        "error_row_count": len(table),
        "error_rows_sha256": row_digest,
        "prefield_precision_viability_passed": prefield_precision_viability_passed,
        "prefield_compute_viability_passed": prefield_compute_viability_passed,
        "bootstrap_replicates": bootstrap_replicates,
        "bootstrap_seed": bootstrap_seed,
        "contrasts": contrasts,
        "passed": passed,
    }


def validate_config(config: dict[str, Any], *, repository_root: str | Path) -> list[str]:
    root = Path(repository_root)
    _require(
        config.get("schema_version") == "aurora.aneumo_response_fidelity_confirmation_template.v3",
        "wrong v3 schema",
    )
    _require(
        config.get("status")
        == "draft_non_authoritative_blocked_on_p0_p1_bounded_development_fresh_reentry_and_prefield_viability",
        "v3 must remain inactive",
    )
    supersession = config["supersession"]
    _require(
        supersession["supersedes_template_sha256"] == EXPECTED_V2_CONFIG_SHA256
        and supersession["supersedes_validator_sha256"] == EXPECTED_V2_VALIDATOR_SHA256,
        "v2 provenance drifted",
    )
    _require(
        _sha256(root / supersession["supersedes_template"]) == EXPECTED_V2_CONFIG_SHA256
        and _sha256(root / supersession["supersedes_validator"]) == EXPECTED_V2_VALIDATOR_SHA256,
        "preserved v2 files drifted",
    )
    for key in (
        "v2_executed",
        "v2_confirmation_metadata_read",
        "v2_confirmation_field_read",
        "v2_model_prediction_read",
    ):
        _require(not supersession[key], "v2 can only be superseded before evidence access")

    inherited = config["inherited_v2_contract"]
    _require(inherited["inherit_only_from_exact_v2_hashes"], "inheritance must be hash-pinned")
    _require(
        inherited["reported_total_base_family_count"] == 427
        and inherited["historical_compact_base_family_count"] == 32
        and inherited["required_new_base_family_count"] == 100
        and inherited["historical_families_excluded"],
        "family population drifted",
    )
    _require(inherited["field_blind_selection_seed"] == 2027081301, "selection seed drifted")
    _require(inherited["all_eligible_cases_and_all_eight_flows_required"], "complete cases and flows required")

    activation = config["activation_boundary"]
    _require(not activation["this_file_can_be_executed"] and not activation["this_file_can_be_submitted_to_pbs"], "template cannot execute")
    _require(not activation["confirmation_registered"], "template is not a registration")
    _require(activation["template_frozen_before_eligibility_metadata_read"], "template must precede metadata")
    _require(activation["real_p0_observed_verdict"] is None and activation["p1_observed_verdict"] is None, "future verdict invented")
    _require(activation["p1_required_template_sha256"] == EXPECTED_P1_SHA256, "P1 dependency drifted")
    for key in (
        "bounded_development_candidate_frozen",
        "fresh_seed_or_disjoint_split_reentry_passed",
        "prefield_precision_viability_passed",
        "prefield_compute_viability_passed",
        "manifest_container_checkpoint_evaluator_hashes_frozen_before_field_read",
    ):
        _require(not activation[key], f"future activation gate cannot be pre-passed: {key}")

    viability = config["prefield_viability"]
    _require(
        not viability["precision_uses_confirmation_eligibility_metadata_field_or_prediction"]
        and viability["compute_uses_only_field_blind_confirmation_eligibility_metadata"]
        and not viability["uses_confirmation_field_or_prediction"],
        "prefield viability information boundary drifted",
    )
    _require(viability["development_family_count"] == 20, "development family count drifted")
    _require(tuple(viability["training_seeds"]) == TRAINING_SEEDS, "training seeds drifted")
    _require(viability["maximum_observed_20_family_sample_sd_per_contrast"] == 0.29810546005930777, "dispersion gate drifted")
    _require(len(viability["required_response_contrasts"]) == 4 and viability["all_four_response_contrasts_must_pass_precision_gate"], "all comparator-endpoint dispersions required")
    _require(viability["both_field_comparison_development_intervals_must_be_inside_plus_or_minus_log_1_02"], "development field equivalence required")
    _require(viability["maximum_projected_confirmation_gpu_hours"] == 40.0, "compute cap drifted")
    _require(viability["analytic_power_law_evaluation_included_but_not_counted_as_gpu_inference"], "analytic control must remain included")

    rows = config["complete_error_row_contract"]
    _require(tuple(rows["required_models"]) == MODELS, "required models drifted")
    _require(tuple(rows["required_metrics"]) == METRICS, "required metrics drifted")
    _require(tuple(rows["required_training_seeds"]) == TRAINING_SEEDS, "row seeds drifted")
    _require(tuple(rows["required_fields"]) == ROW_FIELDS, "row schema drifted")
    _require(rows["positive_error_floor"] == ERROR_FLOOR, "error floor drifted")
    for key in (
        "exactly_one_row_per_factor_cell",
        "all_manifest_families_and_no_extra_families_required",
        "same_nonempty_case_set_for_every_model_seed_metric_within_family",
        "power_law_errors_must_be_bitwise_identical_across_replicated_seed_rows",
        "finite_nonnegative_errors_required",
    ):
        _require(rows[key], f"complete-row guardrail disabled: {key}")

    estimators = config["exact_estimators"]
    _require(estimators["positive_seed_definition"].endswith("strictly_above_zero"), "seed direction drifted")
    _require(estimators["family_win_definition"].endswith("strictly_above_zero"), "family win drifted")
    _require(estimators["nodes_flows_cases_seeds_or_deformations_are_not_independent_replicates"], "pseudoreplication forbidden")

    bootstrap = config["deterministic_family_bootstrap"]
    _require(bootstrap["replicates"] == 10000 and bootstrap["seed"] == 2027081303, "bootstrap count or seed drifted")
    _require(bootstrap["resample_size"] == 100 and bootstrap["sampling"] == "with_replacement", "bootstrap sample drifted")
    _require(bootstrap["shared_family_index_draws_across_all_comparators_and_endpoints"], "paired resamples required")
    _require(bootstrap["random_index_algorithm"] == "sha256_counter_uint64_rejection_sampling_without_modulo_bias", "bootstrap RNG drifted")
    _require(bootstrap["quantile_method"] == "hyndman_fan_type_7_linear", "quantile method drifted")
    _require(not bootstrap["exact_p_value_or_nominal_bootstrap_coverage_claim_allowed"], "unsupported inference claim")

    primary = config["primary_comparators_and_pass"]
    _require(primary["field_equivalence_absolute_log_margin"] == LOG_1_02, "field margin drifted")
    _require(primary["minimum_response_geometric_error_ratio"] == 1.1, "response effect floor drifted")
    _require(primary["minimum_positive_seed_count_per_response_comparison_endpoint"] == 4, "seed floor drifted")
    _require(primary["minimum_family_win_count_per_response_comparison_endpoint"] == 59, "family-win floor drifted")
    _require(len(primary["response_comparisons"]) == 2 and len(primary["response_endpoints"]) == 2, "four response contrasts required")
    _require(primary["global_rule"].startswith("intersection_union"), "pass must remain conjunctive")
    _require(not primary["analytic_control_can_be_omitted_or_demoted_after_failure"], "analytic failure cannot be hidden")
    _require(not primary["secondary_endpoint_or_descriptive_model_can_rescue_failure"], "secondary rescue forbidden")
    _require(wilson_lower_bound(58, 100) <= 0.5 < wilson_lower_bound(59, 100), "Wilson boundary drifted")

    figure = config["interpretable_figure"]
    _require(figure["family_ranking_statistic"].startswith("minimum_of_direct_and_power_law"), "figure must expose the weaker comparator")
    _require(figure["display_seed"] == TRAINING_SEEDS[0], "display seed drifted")
    _require(tuple(figure["panels"]) == ("reference", "same_backbone_direct", "analytic_power_law", "candidate"), "figure panels drifted")
    _require(figure["same_coordinates_camera_and_reference_derived_color_range"], "matched visualization required")
    _require(not figure["favorable_only_case_or_comparator_selection_allowed"] and not figure["clinical_interpretation_allowed"], "figure overclaim forbidden")

    stopping = config["stopping_and_claim_deletion"]
    _require(stopping["all_100_families_all_cases_all_flows_all_models_all_metrics_and_all_five_seeds_required"], "complete factorial required")
    _require(not stopping["partial_aggregation_allowed"], "partial aggregation forbidden")
    _require(not stopping["same_version_repair_rerun_or_comparator_endpoint_margin_seed_sample_quantile_change_after_any_confirmation_eligibility_metadata_field_or_prediction_read_allowed"], "post-read repair forbidden")
    _require(not stopping["confirmation_pass_authorizes_submission_automatically"], "confirmation cannot auto-authorize submission")

    state = config["current_state"]
    _require(all(value is False for key, value in state.items() if key != "scientific_result_count"), "all current flags must be false")
    _require(state["scientific_result_count"] == 0, "no scientific result exists")
    return [
        "pre-evidence v2 supersession",
        "exact-v2 inheritance",
        "zero activation authority",
        "four-contrast prefield precision gate",
        "complete long-form error-row schema",
        "bitwise analytic-control replication",
        "case-to-seed-to-family estimator",
        "exact seed-direction definition",
        "shared deterministic family bootstrap",
        "pinned type-7 quantile",
        "learned and analytic field safeguards",
        "learned and analytic response superiority",
        "majority-family safeguards",
        "weaker-comparator figure ranking",
        "no-repair no-claim state",
    ]


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("config")
    args = parser.parse_args()
    config_path = Path(args.config)
    checks = validate_config(load_config(config_path), repository_root=config_path.resolve().parents[1])
    print(json.dumps({"status": "valid_inactive_confirmation_template_v3", "checks": checks}))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
