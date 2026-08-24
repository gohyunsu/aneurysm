"""Five-seed validation confirmation for the release-730 matched design.

The kernel crosses five frozen training seeds with the same 73 ordered
validation geometries.  It reports seed-specific effects and a crossed
seed/case bootstrap, but defines no pass threshold, opens no locked test and
cannot authorize a paper claim.  Model development and one-time test execution
remain separate prospective stages.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_release_730_matched_information_analysis import (
    CELL_ORDER,
    CONFIRMATION_STAGE,
    CONTRASTS,
    DIAGNOSTIC_METRICS,
    METRIC_DIRECTIONS,
    METRICS,
    PRIMARY_CLAIM_ERROR_METRICS,
    SUPPORTING_ERROR_METRICS,
    extract_cell_rows,
    validate_config as validate_matched_config,
)


class MultiseedConfirmationError(RuntimeError):
    """Raised when a seed replicate or confirmation contract is invalid."""


FRESH_TRAINING_SEEDS = (
    20_260_901,
    20_260_902,
    20_260_903,
    20_260_904,
    20_260_905,
)


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise MultiseedConfirmationError(label)


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_multiseed_confirmation.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_multiseed_confirmation_v1",
        "protocol_id",
    )
    _require(config.get("status") == "prepared_result_pending", "status")
    source = config["source"]
    _require(
        source["matched_information_protocol_id"]
        == "aneug_release_730_matched_information_analysis_v1"
        and source["matched_information_config_sha256"]
        == "9632456e59283b951ddeeb6cd40dfe568a5b3e7bb99fdc9a6c8004e624bafe50",
        "source",
    )
    scope = config["scope"]
    _require(
        scope["validation_cases"] == 73
        and scope["validation_case_digest"]
        == "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024"
        and scope["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "validation_scope",
    )
    _require(
        tuple(scope["fresh_training_seeds"]) == FRESH_TRAINING_SEEDS
        and scope["seed_count"] == 5
        and tuple(scope["cells_per_seed"]) == CELL_ORDER
        and scope["locked_test_read"] is False
        and scope["processed_only_extra_read"] is False,
        "seed_scope",
    )
    analysis = config["analysis"]
    _require(
        tuple(analysis["metrics"]) == METRICS
        and tuple(analysis["primary_claim_error_metrics"])
        == PRIMARY_CLAIM_ERROR_METRICS
        and tuple(analysis["supporting_error_metrics"])
        == SUPPORTING_ERROR_METRICS
        and tuple(analysis["diagnostic_metrics"]) == DIAGNOSTIC_METRICS
        and tuple(analysis["contrasts"]) == tuple(CONTRASTS)
        and analysis["point_estimand"]
        == "mean_over_five_training_seeds_and_73_paired_synthetic_geometry_cases"
        and analysis["report_per_seed_deltas"] is True
        and analysis["report_favorable_seed_count"] is True
        and analysis["minimum_favorable_seed_count"] is None
        and analysis["prediction_valid_coverage_is_gate_or_claim_endpoint"] is False,
        "analysis",
    )
    bootstrap = config["bootstrap"]
    _require(
        bootstrap["replicates"] == 10_000
        and bootstrap["seed"] == 20_260_824
        and bootstrap["resampling"]
        == "crossed_training_seed_and_geometry_case_with_replacement"
        and bootstrap["interval"] == "percentile_95pct"
        and bootstrap["population_inference"] is False,
        "bootstrap",
    )
    decision = config["decision"]
    _require(
        decision["absolute_performance_threshold"] is None
        and decision["automatic_winner"] is False
        and decision["automatic_novelty_conclusion"] is False
        and decision["automatic_test_authorization"] is False
        and decision["interpretation"]
        == "five_seed_validation_consistency_before_frozen_one_time_test_batch",
        "decision",
    )
    boundary = config["boundary"]
    _require(
        boundary["execute_now"] is False
        and boundary["requires_selected_control_and_candidate"] is True
        and boundary["requires_twenty_terminal_validation_cells"] is True
        and boundary["requires_fresh_private_activation"] is True
        and boundary["validation_development_only"] is True
        and boundary["locked_test_or_extra_access"] is False
        and boundary["paper_performance_claim"] is False
        and boundary["publish_numeric_result"] is False
        and boundary["server"] == "introai9"
        and boundary["excluded_server"] == "junjinyong"
        and boundary["maintain_public_site"] is False,
        "boundary",
    )


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


def _crossed_bootstrap(
    values_by_seed: Sequence[Sequence[float]],
    *,
    direction: str,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Resample training seeds and paired geometry cases as crossed factors."""

    _require(direction in {"lower", "higher"}, "direction")
    _require(len(values_by_seed) == 5, "seed_count")
    counts = {len(values) for values in values_by_seed}
    _require(len(counts) == 1 and next(iter(counts)) == 73, "case_count")
    _require(
        all(math.isfinite(value) for values in values_by_seed for value in values),
        "finite_values",
    )
    _require(replicates >= 100, "replicates")
    case_count = next(iter(counts))
    point = sum(sum(values) for values in values_by_seed) / (5 * case_count)
    per_seed = [sum(values) / case_count for values in values_by_seed]
    generator = random.Random(seed)
    means: list[float] = []
    for _ in range(replicates):
        sampled_seeds = [generator.randrange(5) for _ in range(5)]
        sampled_cases = [generator.randrange(case_count) for _ in range(case_count)]
        means.append(
            sum(
                values_by_seed[seed_index][case_index]
                for seed_index in sampled_seeds
                for case_index in sampled_cases
            )
            / (5 * case_count)
        )
    means.sort()
    if direction == "lower":
        probability = sum(value < 0.0 for value in means) / replicates
        favorable_seed_count = sum(value < 0.0 for value in per_seed)
    else:
        probability = sum(value > 0.0 for value in means) / replicates
        favorable_seed_count = sum(value > 0.0 for value in per_seed)
    return {
        "direction": direction,
        "estimand": "mean_over_training_seed_and_paired_geometry_case",
        "point_delta": point,
        "ci95_low": _quantile(means, 0.025),
        "ci95_high": _quantile(means, 0.975),
        "bootstrap_probability_favorable_direction": probability,
        "replicates": replicates,
        "bootstrap_seed": seed,
        "training_seed_count": 5,
        "paired_case_count": case_count,
        "per_seed_point_deltas": per_seed,
        "favorable_seed_count": favorable_seed_count,
        "minimum_favorable_seed_count": None,
    }


def analyze_multiseed_confirmation(
    cells_by_seed: Mapping[int, Mapping[str, Mapping[str, Any]]],
    matched_config: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    replicates: int | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Validate twenty cells and report threshold-free five-seed contrasts."""

    validate_config(config)
    validate_matched_config(matched_config)
    _require(
        matched_config["protocol_id"]
        == config["source"]["matched_information_protocol_id"],
        "matched_protocol",
    )
    expected_seeds = tuple(int(value) for value in config["scope"]["fresh_training_seeds"])
    _require(
        all(isinstance(value, int) and not isinstance(value, bool) for value in cells_by_seed),
        "seed_key_type",
    )
    _require(set(cells_by_seed) == set(expected_seeds), "fresh_seed_set")
    rows_by_seed: dict[int, dict[str, list[dict[str, float]]]] = {}
    protocol_digests: dict[str, set[str]] = {
        "selected_control": set(),
        "selected_proposal": set(),
    }
    selected_identities: dict[str, set[tuple[Any, Any, Any]]] = {
        "selected_control": set(),
        "selected_proposal": set(),
    }
    for training_seed in expected_seeds:
        cells = cells_by_seed[training_seed]
        _require(set(cells) == set(CELL_ORDER), f"seed_{training_seed}_cells")
        _require(
            all(cells[label].get("training_seed") == training_seed for label in CELL_ORDER),
            f"seed_{training_seed}_identity",
        )
        _require(
            cells["control_T"]["transient_training_protocol_sha256"]
            == cells["control_TS"]["transient_training_protocol_sha256"],
            f"seed_{training_seed}_control_protocol_pair",
        )
        _require(
            cells["proposal_T"]["transient_training_protocol_sha256"]
            == cells["proposal_TS"]["transient_training_protocol_sha256"],
            f"seed_{training_seed}_proposal_protocol_pair",
        )
        protocol_digests["selected_control"].add(
            cells["control_T"]["transient_training_protocol_sha256"]
        )
        protocol_digests["selected_proposal"].add(
            cells["proposal_T"]["transient_training_protocol_sha256"]
        )
        for role, prefix in (
            ("selected_control", "control"),
            ("selected_proposal", "proposal"),
        ):
            transient = cells[f"{prefix}_T"]
            steady = cells[f"{prefix}_TS"]
            identity = (
                transient.get("model_family"),
                transient.get("objective_variant"),
                transient.get("selected_response_rank"),
            )
            _require(
                identity
                == (
                    steady.get("model_family"),
                    steady.get("objective_variant"),
                    steady.get("selected_response_rank"),
                ),
                f"seed_{training_seed}_{role}_identity_pair",
            )
            selected_identities[role].add(identity)
        rows_by_seed[training_seed] = {
            label: extract_cell_rows(
                cells[label],
                label,
                matched_config,
                expected_training_stage=CONFIRMATION_STAGE,
            )
            for label in CELL_ORDER
        }
    _require(
        all(len(values) == 1 for values in protocol_digests.values()),
        "cross_seed_training_protocol",
    )
    _require(
        all(len(values) == 1 for values in selected_identities.values()),
        "cross_seed_selected_model_identity",
    )
    if replicates is None:
        replicates = int(config["bootstrap"]["replicates"])
    if seed is None:
        seed = int(config["bootstrap"]["seed"])
    _require(replicates >= 100, "bootstrap_replicates")

    cell_means_by_seed = {
        str(training_seed): {
            label: {
                metric: sum(row[metric] for row in rows_by_seed[training_seed][label])
                / len(rows_by_seed[training_seed][label])
                for metric in METRICS
            }
            for label in CELL_ORDER
        }
        for training_seed in expected_seeds
    }
    aggregate: dict[str, dict[str, Any]] = {}
    for contrast_index, (contrast, coefficients) in enumerate(CONTRASTS.items()):
        aggregate[contrast] = {}
        for metric_index, metric in enumerate(METRICS):
            values_by_seed = [
                [
                    sum(
                        coefficient
                        * rows_by_seed[training_seed][label][case_index][metric]
                        for label, coefficient in coefficients.items()
                    )
                    for case_index in range(73)
                ]
                for training_seed in expected_seeds
            ]
            result = _crossed_bootstrap(
                values_by_seed,
                direction=METRIC_DIRECTIONS[metric],
                replicates=replicates,
                seed=seed + contrast_index * 10_007 + metric_index,
            )
            result.update({"metric": metric, "coefficients": dict(coefficients)})
            aggregate[contrast][metric] = result

    return {
        "schema_version": "aurora.private.aneug_release_730_multiseed_confirmation_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_validation_confirmation",
        "evidence_role": "five_seed_validation_consistency_before_locked_test",
        "fresh_training_seeds": list(expected_seeds),
        "cell_means_by_seed": cell_means_by_seed,
        "crossed_seed_case_contrasts": aggregate,
        "primary_claim_error_metrics": list(PRIMARY_CLAIM_ERROR_METRICS),
        "supporting_error_metrics": list(SUPPORTING_ERROR_METRICS),
        "diagnostic_metrics": list(DIAGNOSTIC_METRICS),
        "prediction_valid_coverage_is_gate_or_claim_endpoint": False,
        "transient_training_protocol_sha256_by_role": {
            role: next(iter(values)) for role, values in protocol_digests.items()
        },
        "selected_model_identity_by_role": {
            role: {
                "model_family": next(iter(values))[0],
                "objective_variant": next(iter(values))[1],
                "selected_response_rank": next(iter(values))[2],
            }
            for role, values in selected_identities.items()
        },
        "automatic_winner": None,
        "automatic_novelty_conclusion": None,
        "automatic_test_authorization": None,
        "absolute_performance_threshold": None,
        "minimum_favorable_seed_count": None,
        "training_seed_count": 5,
        "paired_case_count": 73,
        "case_identifiers_included": False,
        "locked_test_or_extra_values_read": False,
        "population_inference": False,
        "paper_performance_claim": False,
    }
