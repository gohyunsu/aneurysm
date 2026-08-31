"""Case-level statistical analysis for the prospective ICCE v2 validation grid.

The module consumes only identifier-free terminal validation results.  Its
inferential unit is one geometry, and every uncertainty interval resamples the
fixed training seeds and paired validation-case positions as crossed factors.
It contains no locked-test or processed-extra input path.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

import numpy as np

from aurora.aneug_release_730_icce_revision import (
    LABEL_COUNTS,
    METHOD_IDS,
    METHOD_REGIME_SEPARATED,
    METHOD_TRANSIENT_ONLY,
    TRAINING_SEEDS,
    expected_exposure_ledger,
    validate_protocol_config,
)


PRIMARY_METRICS = (
    "field_relative_l2",
    "tawss_normalized_absolute_error",
    "osi_mae",
)
DIAGNOSTIC_METRICS = (
    "osi_coverage",
    "mean_wss_vector_error",
    "low_tawss_quartile_field_relative_l2",
    "peak_systolic_wss_relative_l2",
    "mesh_normal_component_relative_l2",
    "mean_vector_tawss_normalized_l2",
)
ALL_METRICS = PRIMARY_METRICS + DIAGNOSTIC_METRICS
ATTRIBUTION_COMPARATORS = (
    METHOD_TRANSIENT_ONLY,
    "T_plus_M",
    "T_plus_S_shared_decoder",
    "S_then_T",
    "T_plus_S_shuffled_labels",
)


class ICCEAnalysisError(RuntimeError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCEAnalysisError(reason)


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    _require(bool(sorted_values) and 0.0 <= probability <= 1.0, "quantile")
    position = probability * (len(sorted_values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(sorted_values[lower])
    fraction = position - lower
    return float(
        sorted_values[lower] * (1.0 - fraction)
        + sorted_values[upper] * fraction
    )


def crossed_seed_case_bootstrap(
    values_by_seed: Sequence[Sequence[float]],
    *,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Estimate a mean and percentile CI by crossed seed/case resampling."""

    seed_count = len(values_by_seed)
    case_counts = {len(values) for values in values_by_seed}
    _require(seed_count >= 3, "seed_count")
    _require(case_counts == {73}, "case_count")
    _require(
        replicates == 10_000
        and all(
            math.isfinite(float(value))
            for values in values_by_seed
            for value in values
        ),
        "bootstrap_values",
    )
    case_count = 73
    point = sum(sum(float(value) for value in values) for values in values_by_seed)
    point /= seed_count * case_count
    per_seed = [sum(float(value) for value in values) / case_count for values in values_by_seed]
    array = np.asarray(values_by_seed, dtype=np.float64)
    generator = np.random.default_rng(seed)
    draws_array = np.empty(replicates, dtype=np.float64)
    chunk_size = 256
    for start in range(0, replicates, chunk_size):
        stop = min(start + chunk_size, replicates)
        count = stop - start
        sampled_seeds = generator.integers(
            0, seed_count, size=(count, seed_count), endpoint=False
        )
        sampled_cases = generator.integers(
            0, case_count, size=(count, case_count), endpoint=False
        )
        crossed = array[
            sampled_seeds[:, :, np.newaxis], sampled_cases[:, np.newaxis, :]
        ]
        draws_array[start:stop] = crossed.mean(axis=(1, 2))
    draws = sorted(float(value) for value in draws_array)
    return {
        "point": point,
        "ci95_low": _quantile(draws, 0.025),
        "ci95_high": _quantile(draws, 0.975),
        "per_seed_points": per_seed,
        "training_seed_count": seed_count,
        "paired_case_count": case_count,
        "replicates": replicates,
        "bootstrap_seed": seed,
        "resampling": "crossed_training_seed_and_paired_geometry_case",
        "population_inference": False,
    }


def _validate_result(
    result: Mapping[str, Any],
    *,
    method_id: str,
    training_seed: int,
    unique_transient_cases: int,
) -> list[dict[str, float]]:
    ledger = expected_exposure_ledger(
        method_id, unique_transient_cases=unique_transient_cases
    )
    label_percent = next(
        percent for percent, count in LABEL_COUNTS.items() if count == unique_transient_cases
    )
    _require(
        result.get("schema_version")
        == "aurora.private.aneug_release_730_icce_fixed_budget_result.v2"
        and result.get("status") == "complete_validation_only"
        and result.get("method_id") == method_id
        and result.get("training_seed") == training_seed
        and result.get("label_percent") == label_percent
        and result.get("selected_epoch") == 251
        and result.get("train_case_count") == unique_transient_cases
        and result.get("validation_case_count") == 73
        and result.get("transient_exposures") == ledger.transient_exposures
        and result.get("auxiliary_exposures") == ledger.auxiliary_exposures
        and result.get("locked_test_field_case_count_read") == 0
        and result.get("processed_only_extra_field_case_count_read") == 0
        and result.get("case_ids_included") is False,
        "result_contract",
    )
    validation = result.get("validation")
    _require(
        isinstance(validation, Mapping)
        and validation.get("case_count") == 73
        and isinstance(validation.get("per_case_without_identifiers"), list)
        and len(validation["per_case_without_identifiers"]) == 73,
        "validation_rows",
    )
    rows: list[dict[str, float]] = []
    for row in validation["per_case_without_identifiers"]:
        _require(
            isinstance(row, Mapping)
            and all(metric in row for metric in ALL_METRICS)
            and all(math.isfinite(float(row[metric])) for metric in ALL_METRICS),
            "metric_row",
        )
        rows.append({metric: float(row[metric]) for metric in ALL_METRICS})
    aggregate = validation.get("aggregate")
    _require(isinstance(aggregate, Mapping), "aggregate")
    for metric in ALL_METRICS:
        recomputed = sum(row[metric] for row in rows) / 73
        _require(
            math.isclose(
                recomputed,
                float(aggregate[metric]),
                rel_tol=1e-12,
                abs_tol=1e-12,
            ),
            f"aggregate_{metric}",
        )
    return rows


def _method_summary(
    rows_by_seed: Mapping[int, Sequence[Mapping[str, float]]],
    *,
    seeds: Sequence[int],
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for metric_index, metric in enumerate(ALL_METRICS):
        values = [[float(row[metric]) for row in rows_by_seed[seed]] for seed in seeds]
        estimate = crossed_seed_case_bootstrap(
            values,
            replicates=bootstrap_replicates,
            seed=bootstrap_seed + metric_index,
        )
        output[metric] = estimate
    return output


def analyze_main_attribution(
    results_by_method_seed: Mapping[str, Mapping[int, Mapping[str, Any]]],
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    """Analyze the six-method, five-seed validation-only attribution matrix."""

    validate_protocol_config(protocol)
    _require(set(results_by_method_seed) == set(METHOD_IDS), "method_set")
    seeds = tuple(int(value) for value in protocol["training_seeds"])
    rows: dict[str, dict[int, list[dict[str, float]]]] = {}
    validation_digests: set[str] = set()
    for method_id in METHOD_IDS:
        _require(set(results_by_method_seed[method_id]) == set(seeds), "seed_set")
        rows[method_id] = {}
        for training_seed in seeds:
            result = results_by_method_seed[method_id][training_seed]
            rows[method_id][training_seed] = _validate_result(
                result,
                method_id=method_id,
                training_seed=training_seed,
                unique_transient_cases=584,
            )
            digest = result.get("validation_case_digest")
            _require(isinstance(digest, str) and len(digest) == 64, "validation_digest")
            validation_digests.add(digest)
    _require(len(validation_digests) == 1, "paired_validation_order")
    replicates = int(protocol["bootstrap"]["replicates"])
    bootstrap_seed = int(protocol["bootstrap"]["seed"])
    method_summaries = {
        method_id: _method_summary(
            rows[method_id],
            seeds=seeds,
            bootstrap_replicates=replicates,
            bootstrap_seed=bootstrap_seed + method_index * 1_003,
        )
        for method_index, method_id in enumerate(METHOD_IDS)
    }
    contrasts: dict[str, Any] = {}
    for comparator_index, comparator in enumerate(ATTRIBUTION_COMPARATORS):
        contrast_name = f"{METHOD_REGIME_SEPARATED}_minus_{comparator}"
        contrasts[contrast_name] = {}
        for metric_index, metric in enumerate(PRIMARY_METRICS):
            deltas = [
                [
                    rows[METHOD_REGIME_SEPARATED][training_seed][case_index][metric]
                    - rows[comparator][training_seed][case_index][metric]
                    for case_index in range(73)
                ]
                for training_seed in seeds
            ]
            estimate = crossed_seed_case_bootstrap(
                deltas,
                replicates=replicates,
                seed=bootstrap_seed + 10_000 + comparator_index * 101 + metric_index,
            )
            estimate.update(
                {
                    "candidate": METHOD_REGIME_SEPARATED,
                    "comparator": comparator,
                    "metric": metric,
                    "lower_is_better": True,
                }
            )
            contrasts[contrast_name][metric] = estimate
    gradient = {
        str(seed): results_by_method_seed["T_plus_S_shared_decoder"][seed].get(
            "decoder_gradient_diagnostic"
        )
        for seed in seeds
    }
    _require(
        all(
            isinstance(value, Mapping)
            and int(value.get("count", 0)) == 146_584
            and math.isfinite(float(value.get("mean", math.nan)))
            and math.isfinite(float(value.get("median", math.nan)))
            and 0.0 <= float(value.get("fraction_below_zero", math.nan)) <= 1.0
            for value in gradient.values()
        ),
        "gradient_diagnostics",
    )
    return {
        "schema_version": "aurora.aneug_release_730_icce_attribution_analysis.v1",
        "protocol_id": protocol["protocol_id"],
        "status": "complete_validation_only",
        "method_summaries": method_summaries,
        "proposed_minus_comparator": contrasts,
        "shared_decoder_gradient_diagnostic_by_seed": gradient,
        "training_seeds": list(seeds),
        "paired_case_count": 73,
        "validation_case_digest": next(iter(validation_digests)),
        "locked_test_or_extra_read": False,
        "case_is_statistical_unit": True,
        "automatic_winner": None,
        "paper_claim": False,
    }


def analyze_label_efficiency(
    results_by_percent_method_seed: Mapping[
        int, Mapping[str, Mapping[int, Mapping[str, Any]]]
    ],
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    """Analyze five common seeds at each nested transient-label budget."""

    validate_protocol_config(protocol)
    percents = tuple(int(value) for value in protocol["label_efficiency"]["percents"])
    counts = {
        int(percent): int(count)
        for percent, count in protocol["label_efficiency"]["unique_case_counts"].items()
    }
    seeds = tuple(int(value) for value in protocol["training_seeds"])
    _require(set(results_by_percent_method_seed) == set(percents), "label_percents")
    replicates = int(protocol["bootstrap"]["replicates"])
    bootstrap_seed = int(protocol["bootstrap"]["seed"])
    curves: dict[str, Any] = {}
    for percent_index, percent in enumerate(percents):
        cells = results_by_percent_method_seed[percent]
        _require(set(cells) == {METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED}, "label_methods")
        rows: dict[str, dict[int, list[dict[str, float]]]] = {}
        for method_id in (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED):
            _require(set(cells[method_id]) == set(seeds), "label_seed_set")
            rows[method_id] = {
                seed: _validate_result(
                    cells[method_id][seed],
                    method_id=method_id,
                    training_seed=seed,
                    unique_transient_cases=counts[percent],
                )
                for seed in seeds
            }
        point: dict[str, Any] = {
            "percent": percent,
            "unique_transient_cases": counts[percent],
            "methods": {},
            "proposed_minus_T": {},
        }
        for method_index, method_id in enumerate(
            (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED)
        ):
            point["methods"][method_id] = {}
            for metric_index, metric in enumerate(PRIMARY_METRICS):
                values = [
                    [row[metric] for row in rows[method_id][seed]] for seed in seeds
                ]
                point["methods"][method_id][metric] = crossed_seed_case_bootstrap(
                    values,
                    replicates=replicates,
                    seed=bootstrap_seed
                    + 20_000
                    + percent_index * 1_003
                    + method_index * 101
                    + metric_index,
                )
        for metric_index, metric in enumerate(PRIMARY_METRICS):
            deltas = [
                [
                    rows[METHOD_REGIME_SEPARATED][seed][case_index][metric]
                    - rows[METHOD_TRANSIENT_ONLY][seed][case_index][metric]
                    for case_index in range(73)
                ]
                for seed in seeds
            ]
            point["proposed_minus_T"][metric] = crossed_seed_case_bootstrap(
                deltas,
                replicates=replicates,
                seed=bootstrap_seed + 30_000 + percent_index * 101 + metric_index,
            )
        curves[str(percent)] = point
    return {
        "schema_version": "aurora.aneug_release_730_icce_label_efficiency_analysis.v1",
        "protocol_id": protocol["protocol_id"],
        "status": "complete_validation_only",
        "common_training_seeds": list(seeds),
        "curves": curves,
        "locked_test_or_extra_read": False,
        "equivalence_claim": False,
        "paper_claim": False,
    }


def analyze_lambda_sensitivity(
    results_by_lambda_seed: Mapping[float, Mapping[int, Mapping[str, Any]]],
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    """Describe prespecified validation-only lambda sensitivity without selection."""

    validate_protocol_config(protocol)
    lambdas = tuple(float(value) for value in protocol["lambda_sensitivity"]["values"])
    seeds = tuple(int(value) for value in protocol["lambda_sensitivity"]["seeds"])
    _require(set(results_by_lambda_seed) == set(lambdas), "lambda_values")
    replicates = int(protocol["bootstrap"]["replicates"])
    bootstrap_seed = int(protocol["bootstrap"]["seed"])
    rows: dict[float, dict[int, list[dict[str, float]]]] = {}
    for value in lambdas:
        _require(set(results_by_lambda_seed[value]) == set(seeds), "lambda_seed_set")
        rows[value] = {
            seed: _validate_result(
                results_by_lambda_seed[value][seed],
                method_id=METHOD_REGIME_SEPARATED,
                training_seed=seed,
                unique_transient_cases=584,
            )
            for seed in seeds
        }
    output: dict[str, Any] = {}
    for lambda_index, value in enumerate(lambdas):
        output[str(value)] = {"metrics": {}, "minus_lambda_1": {}}
        for metric_index, metric in enumerate(PRIMARY_METRICS):
            values = [[row[metric] for row in rows[value][seed]] for seed in seeds]
            output[str(value)]["metrics"][metric] = crossed_seed_case_bootstrap(
                values,
                replicates=replicates,
                seed=bootstrap_seed + 40_000 + lambda_index * 101 + metric_index,
            )
            deltas = [
                [
                    rows[value][seed][case_index][metric]
                    - rows[1.0][seed][case_index][metric]
                    for case_index in range(73)
                ]
                for seed in seeds
            ]
            output[str(value)]["minus_lambda_1"][metric] = crossed_seed_case_bootstrap(
                deltas,
                replicates=replicates,
                seed=bootstrap_seed + 50_000 + lambda_index * 101 + metric_index,
            )
    return {
        "schema_version": "aurora.aneug_release_730_icce_lambda_sensitivity_analysis.v1",
        "protocol_id": protocol["protocol_id"],
        "status": "complete_validation_only",
        "main_lambda": 1.0,
        "main_lambda_selected_from_sensitivity": False,
        "training_seeds": list(seeds),
        "lambda_results": output,
        "locked_test_or_extra_read": False,
        "paper_claim": False,
    }
