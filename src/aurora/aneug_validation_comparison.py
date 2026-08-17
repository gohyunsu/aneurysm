"""Paired validation comparison for AneuG transient-WSS surrogates.

The module reports continuous component-level deltas, bootstrap intervals and
Pareto membership. It deliberately contains no absolute performance threshold
and never chooses a paper winner automatically.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Mapping, Sequence


class AneuGValidationComparisonError(RuntimeError):
    """Raised when result comparability or metric inputs are invalid."""


METRIC_DIRECTIONS = {
    "field_relative_l2": "lower",
    "mean_vector_tawss_normalized_l2": "lower",
    "tawss_normalized_absolute_error": "lower",
    "osi_mae": "lower",
    "osi_coverage": "higher",
}
CORE_METRICS = (
    "field_relative_l2",
    "tawss_normalized_absolute_error",
    "osi_mae",
    "osi_coverage",
)


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise AneuGValidationComparisonError(label)


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version") == "aurora.aneug_validation_comparison.v1",
        "config_schema",
    )
    _require(config.get("status") == "prepared_result_pending", "status")
    comparison = config["comparison"]
    _require(tuple(comparison["core_metrics"]) == CORE_METRICS, "metrics")
    _require(
        comparison["paired_unit"] == "synthetic_geometry_component"
        and comparison["validation_case_count"] == 51
        and comparison["same_cache_order_required"] is True,
        "paired_unit",
    )
    bootstrap = config["bootstrap"]
    _require(
        bootstrap["replicates"] == 10_000
        and bootstrap["seed"] == 20_260_818
        and bootstrap["interval"] == "percentile_95pct",
        "bootstrap",
    )
    decision = config["decision"]
    _require(
        decision["absolute_performance_threshold"] is None
        and decision["automatic_winner"] is False
        and decision["report_pareto_set"] is True
        and decision["report_all_pairwise_deltas"] is True,
        "decision",
    )
    boundary = config["boundary"]
    _require(
        boundary["validation_development_only"] is True
        and boundary["outer_or_auxiliary_access"] is False
        and boundary["paper_claim"] is False,
        "boundary",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def extract_validation_rows(
    result: Mapping[str, Any], *, expected_case_count: int = 51
) -> list[dict[str, float]]:
    _require(result.get("status") == "complete", "result_status")
    _require(result.get("development_only") is True, "development_role")
    _require(result.get("case_ids_included") is False, "identifier_boundary")
    _require(
        result.get("outer_or_auxiliary_values_read") is False,
        "sealed_boundary",
    )
    validation = result.get("validation")
    _require(isinstance(validation, Mapping), "validation")
    rows = validation.get("per_case_without_identifiers")
    _require(isinstance(rows, list) and len(rows) == expected_case_count, "case_count")
    parsed: list[dict[str, float]] = []
    for row in rows:
        _require(isinstance(row, Mapping), "case_row")
        values: dict[str, float] = {}
        for metric in CORE_METRICS:
            _require(metric in row, f"metric_{metric}")
            value = float(row[metric])
            _require(math.isfinite(value), f"finite_{metric}")
            if metric == "osi_coverage":
                _require(0.0 <= value <= 1.0, "coverage_bounds")
            else:
                _require(value >= 0.0, f"nonnegative_{metric}")
            values[metric] = value
        for metric in set(METRIC_DIRECTIONS) - set(CORE_METRICS):
            if metric in row:
                value = float(row[metric])
                _require(math.isfinite(value) and value >= 0.0, f"optional_{metric}")
                values[metric] = value
        parsed.append(values)
    return parsed


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    _require(len(sorted_values) > 0 and 0.0 <= probability <= 1.0, "quantile")
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


def paired_bootstrap_delta(
    candidate: Sequence[Mapping[str, float]],
    reference: Sequence[Mapping[str, float]],
    metric: str,
    *,
    replicates: int = 10_000,
    seed: int = 20_260_818,
) -> dict[str, Any]:
    _require(metric in METRIC_DIRECTIONS, "metric")
    _require(len(candidate) == len(reference) and len(candidate) >= 2, "paired_count")
    _require(replicates >= 100, "replicates")
    differences = [
        float(candidate[index][metric]) - float(reference[index][metric])
        for index in range(len(candidate))
    ]
    _require(all(math.isfinite(value) for value in differences), "finite_delta")
    point = sum(differences) / len(differences)
    generator = random.Random(seed)
    means: list[float] = []
    for _ in range(replicates):
        means.append(
            sum(differences[generator.randrange(len(differences))] for _ in differences)
            / len(differences)
        )
    means.sort()
    direction = METRIC_DIRECTIONS[metric]
    if direction == "lower":
        probability_better = sum(value < 0.0 for value in means) / replicates
    else:
        probability_better = sum(value > 0.0 for value in means) / replicates
    return {
        "metric": metric,
        "direction": direction,
        "estimand": "mean_candidate_minus_reference",
        "point_delta": point,
        "ci95_low": _quantile(means, 0.025),
        "ci95_high": _quantile(means, 0.975),
        "bootstrap_probability_candidate_better": probability_better,
        "replicates": replicates,
        "seed": seed,
        "paired_case_count": len(differences),
    }


def metric_means(rows: Sequence[Mapping[str, float]]) -> dict[str, float]:
    available = tuple(
        metric for metric in METRIC_DIRECTIONS if all(metric in row for row in rows)
    )
    _require(len(rows) > 0 and all(metric in rows[0] for metric in CORE_METRICS), "rows")
    return {
        metric: sum(float(row[metric]) for row in rows) / len(rows)
        for metric in available
    }


def pareto_set(
    method_means: Mapping[str, Mapping[str, float]],
    *,
    metrics: Sequence[str] = CORE_METRICS,
) -> list[str]:
    _require(len(method_means) >= 2, "method_count")
    _require(all(metric in METRIC_DIRECTIONS for metric in metrics), "pareto_metric")

    def no_worse(left: float, right: float, direction: str) -> bool:
        return left <= right if direction == "lower" else left >= right

    def strictly_better(left: float, right: float, direction: str) -> bool:
        return left < right if direction == "lower" else left > right

    front: list[str] = []
    for label, values in method_means.items():
        _require(all(metric in values for metric in metrics), "pareto_values")
        dominated = False
        for other_label, other in method_means.items():
            if other_label == label:
                continue
            if all(
                no_worse(other[metric], values[metric], METRIC_DIRECTIONS[metric])
                for metric in metrics
            ) and any(
                strictly_better(other[metric], values[metric], METRIC_DIRECTIONS[metric])
                for metric in metrics
            ):
                dominated = True
                break
        if not dominated:
            front.append(label)
    return sorted(front)


def compare_to_reference(
    methods: Mapping[str, Mapping[str, Any]],
    reference_label: str,
    *,
    replicates: int = 10_000,
    seed: int = 20_260_818,
) -> dict[str, Any]:
    _require(reference_label in methods and len(methods) >= 2, "reference")
    rows = {label: extract_validation_rows(result) for label, result in methods.items()}
    means = {label: metric_means(value) for label, value in rows.items()}
    comparisons: dict[str, dict[str, Any]] = {}
    for method_index, (label, value) in enumerate(rows.items()):
        if label == reference_label:
            continue
        comparisons[label] = {
            metric: paired_bootstrap_delta(
                value,
                rows[reference_label],
                metric,
                replicates=replicates,
                seed=seed + 10_007 * method_index + metric_index,
            )
            for metric_index, metric in enumerate(CORE_METRICS)
        }
    return {
        "schema_version": "aurora.aneug_validation_comparison.result.v1",
        "evidence_role": "validation_development_continuous_comparison",
        "automatic_winner": None,
        "absolute_performance_threshold": None,
        "reference_label": reference_label,
        "method_means": means,
        "paired_deltas": comparisons,
        "pareto_set": pareto_set(means),
        "paired_unit": "synthetic_geometry_component",
        "population_inference": False,
        "case_identifiers_included": False,
        "outer_or_auxiliary_values_read": False,
        "paper_claim": False,
    }

