"""Paired 2x2 analysis for matched transient/steady AneuG supervision.

The four cells cross model role (selected control versus proposal) with
information mode (transient-only versus the identical audited steady set).
The module reports case-paired method and registered augmentation-protocol
contrasts.  Because T+S adds forward/backward work, the within-model T-to-T+S
contrast is not labelled a causal effect of steady labels alone. A separate
bounded T+M sidecar controls the auxiliary model path but not target
information, storage I/O or all system compute; it does not replace or gate
this primary factorial. The module deliberately selects no model, defines no
pass threshold and reads no locked-test value.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Mapping, Sequence


class MatchedInformationAnalysisError(RuntimeError):
    """Raised when a factorial cell or analysis contract is inconsistent."""


CELL_ORDER = (
    "control_T",
    "control_TS",
    "proposal_T",
    "proposal_TS",
)
METRIC_DIRECTIONS = {
    "field_relative_l2": "lower",
    "mean_wss_vector_error": "lower",
    "tawss_normalized_absolute_error": "lower",
    "osi_mae": "lower",
    "osi_coverage": "higher",
}
METRICS = tuple(METRIC_DIRECTIONS)
PRIMARY_CLAIM_ERROR_METRICS = (
    "field_relative_l2",
    "tawss_normalized_absolute_error",
    "osi_mae",
)
SUPPORTING_ERROR_METRICS = ("mean_wss_vector_error",)
DIAGNOSTIC_METRICS = ("osi_coverage",)
MATCHED_DEVELOPMENT_STAGE = "single_seed_matched_information_validation_development"
CONFIRMATION_STAGE = "five_seed_matched_information_validation_confirmation"
CONTRASTS = {
    "proposal_minus_control_T": {
        "control_T": -1.0,
        "proposal_T": 1.0,
    },
    "proposal_minus_control_TS": {
        "control_TS": -1.0,
        "proposal_TS": 1.0,
    },
    "steady_minus_transient_control": {
        "control_T": -1.0,
        "control_TS": 1.0,
    },
    "steady_minus_transient_proposal": {
        "proposal_T": -1.0,
        "proposal_TS": 1.0,
    },
    "method_by_steady_interaction": {
        "control_T": 1.0,
        "control_TS": -1.0,
        "proposal_T": -1.0,
        "proposal_TS": 1.0,
    },
}


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise MatchedInformationAnalysisError(label)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_matched_information_analysis.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_matched_information_analysis_v1",
        "protocol_id",
    )
    _require(config.get("status") == "prepared_result_pending", "status")
    split = config["split"]
    _require(
        split["validation_cases"] == 73
        and split["validation_case_digest"]
        == "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024"
        and split["private_manifest_sha256"]
        == "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f"
        and split["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30"
        and split["shared_loader_order_required"] is True,
        "split",
    )
    factorial = config["factorial"]
    _require(tuple(factorial["cells"]) == CELL_ORDER, "cells")
    _require(
        tuple(factorial["metrics"]) == METRICS
        and tuple(factorial["primary_claim_error_metrics"])
        == PRIMARY_CLAIM_ERROR_METRICS
        and tuple(factorial["supporting_error_metrics"])
        == SUPPORTING_ERROR_METRICS
        and tuple(factorial["diagnostic_metrics"]) == DIAGNOSTIC_METRICS
        and (
            set(PRIMARY_CLAIM_ERROR_METRICS)
            | set(SUPPORTING_ERROR_METRICS)
            | set(DIAGNOSTIC_METRICS)
        )
        == set(METRICS)
        and factorial["invalid_osi_predictions_are_penalized_in_osi_mae"] is True,
        "metrics",
    )
    _require(
        factorial["eligible_steady_rows"] == 13_985
        and factorial["eligible_steady_case_digest"]
        == "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc"
        and factorial["same_steady_indices_for_control_and_proposal"] is True,
        "steady_scope",
    )
    _require(
        factorial["proposal_only_steady_labels"] is False
        and factorial["steady_supervision_is_novelty"] is False,
        "information_fairness",
    )
    exposure = factorial["steady_exposure_schedule"]
    _require(
        exposure["protocol_id"]
        == "aneug_release_730_steady_exposure_schedule_v1"
        and exposure["config_sha256"]
        == "3509191bd2c3e3294488ab5018109f3beccd402599a17e16dd8696d1deeaceaf"
        and exposure["algorithm"]
        == "sha256_ranked_full_cycle_without_replacement_v1"
        and exposure["seed"] == 20_260_821
        and exposure["examples_per_epoch"] == 584
        and exposure["minimum_epochs"] == 80
        and exposure["maximum_epochs"] == 251
        and exposure["terminal_prefix_digest_required"] is True,
        "steady_exposure_schedule",
    )
    _require(factorial["contrasts"] == CONTRASTS, "contrasts")
    accounting = config["training_accounting"]
    _require(
        accounting["required_cell_fields"]
        == [
            "transient_training_protocol_sha256",
            "training_stage",
            "training_seed",
            "transient_case_cycles_consumed",
            "optimizer_steps",
            "training_gpu_seconds",
            "peak_gpu_memory_bytes",
            "active_parameter_count",
            "steady_head_active",
            "steady_objective_scale_result_sha256",
            "additional_steady_forward_backward_work",
        ]
        and accounting["same_transient_training_protocol_within_model_role"]
        is True
        and accounting["same_training_seed_across_four_cells"] is True
        and accounting[
            "terminal_examples_steps_time_memory_and_parameters_reported"
        ]
        is True
        and accounting["compute_matched_transient_replay_control_present"]
        is False
        and accounting["bounded_auxiliary_attribution_sidecar_registered"]
        is True
        and accounting["auxiliary_attribution_protocol_id"]
        == "aneug_release_730_auxiliary_compute_attribution_v1"
        and accounting["auxiliary_attribution_is_primary_factorial_gate"]
        is False
        and accounting["steady_contrast_estimand"]
        == "registered_T_plus_S_augmentation_protocol_including_its_additional_compute_not_a_label_only_causal_effect"
        and accounting["primary_method_comparisons_are_within_information_mode"]
        is True,
        "training_accounting",
    )
    bootstrap = config["bootstrap"]
    _require(
        bootstrap["replicates"] == 10_000
        and bootstrap["seed"] == 20_260_821
        and bootstrap["interval"] == "percentile_95pct"
        and bootstrap["paired_unit"] == "synthetic_geometry_case"
        and bootstrap["population_inference"] is False,
        "bootstrap",
    )
    decision = config["decision"]
    _require(
        decision["absolute_performance_threshold"] is None
        and decision["automatic_winner"] is False
        and decision["automatic_novelty_conclusion"] is False
        and decision["report_all_cells"] is True
        and decision["report_all_contrasts"] is True
        and decision["prediction_valid_coverage_is_gate_or_claim_endpoint"] is False
        and decision["interpretation"]
        == "report_within_information_method_effects_and_registered_augmentation_protocol_contrasts_without_a_label_only_causal_or_novelty_claim",
        "decision",
    )
    boundary = config["boundary"]
    _require(
        boundary["execute_now"] is False
        and boundary["requires_four_terminal_validation_results"] is True
        and boundary["requires_fresh_private_activation"] is True
        and boundary["validation_development_only"] is True
        and boundary["locked_test_or_extra_access"] is False
        and boundary["paper_performance_claim"] is False
        and boundary["publish_numeric_result"] is False
        and boundary["server"] == "introai9"
        and boundary["excluded_server"] == "junjinyong",
        "boundary",
    )


def _expected_role_and_mode(label: str) -> tuple[str, str]:
    _require(label in CELL_ORDER, "cell_label")
    role = "selected_control" if label.startswith("control_") else "selected_proposal"
    mode = "eligible_steady" if label.endswith("TS") else "transient_only"
    return role, mode


def extract_cell_rows(
    cell: Mapping[str, Any],
    label: str,
    config: Mapping[str, Any],
    *,
    expected_training_stage: str = MATCHED_DEVELOPMENT_STAGE,
) -> list[dict[str, float]]:
    """Validate one normalized terminal-validation cell and return metric rows."""

    role, mode = _expected_role_and_mode(label)
    _require(
        cell.get("schema_version")
        == "aurora.aneug_release_730_matched_information_cell.v1",
        f"{label}_schema",
    )
    expected_status = (
        "complete_validation_confirmation"
        if expected_training_stage == CONFIRMATION_STAGE
        else "complete_validation_development"
    )
    _require(cell.get("status") == expected_status, f"{label}_status")
    _require(cell.get("model_role") == role, f"{label}_role")
    _require(cell.get("information_mode") == mode, f"{label}_mode")
    _require(
        cell.get("validation_case_digest")
        == config["split"]["validation_case_digest"]
        and cell.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and cell.get("validation_loader_order_sha256")
        == config["split"]["validation_loader_order_sha256"],
        f"{label}_split",
    )
    if mode == "eligible_steady":
        exposure = config["factorial"]["steady_exposure_schedule"]
        _require(
            cell.get("eligible_steady_rows")
            == config["factorial"]["eligible_steady_rows"]
            and cell.get("eligible_steady_case_digest")
            == config["factorial"]["eligible_steady_case_digest"],
            f"{label}_steady_scope",
        )
        _require(
            cell.get("steady_exposure_schedule_protocol_id")
            == exposure["protocol_id"]
            and cell.get("steady_exposure_schedule_config_sha256")
            == exposure["config_sha256"]
            and cell.get("steady_exposure_algorithm") == exposure["algorithm"]
            and cell.get("steady_exposure_seed") == exposure["seed"],
            f"{label}_steady_exposure_contract",
        )
        epochs = cell.get("steady_exposure_epochs")
        examples = cell.get("steady_examples_consumed")
        prefix_digest = cell.get("steady_exposure_prefix_sha256")
        _require(
            isinstance(epochs, int)
            and exposure["minimum_epochs"] <= epochs <= exposure["maximum_epochs"]
            and examples == epochs * exposure["examples_per_epoch"]
            and isinstance(prefix_digest, str)
            and len(prefix_digest) == 64
            and all(character in "0123456789abcdef" for character in prefix_digest),
            f"{label}_steady_exposure_terminal",
        )
    else:
        _require(
            cell.get("eligible_steady_rows") == 0
            and cell.get("eligible_steady_case_digest") is None,
            f"{label}_transient_scope",
        )
        _require(
            cell.get("steady_exposure_schedule_protocol_id") is None
            and cell.get("steady_exposure_schedule_config_sha256") is None
            and cell.get("steady_exposure_algorithm") is None
            and cell.get("steady_exposure_seed") is None
            and cell.get("steady_exposure_epochs") == 0
            and cell.get("steady_examples_consumed") == 0
            and cell.get("steady_exposure_prefix_sha256") is None,
            f"{label}_transient_exposure",
        )
    _require(
        _is_sha256(cell.get("transient_training_protocol_sha256")),
        f"{label}_training_protocol",
    )
    _require(
        cell.get("training_stage") == expected_training_stage,
        f"{label}_training_stage",
    )
    _require(
        isinstance(cell.get("training_seed"), int)
        and not isinstance(cell.get("training_seed"), bool),
        f"{label}_training_seed",
    )
    for key in (
        "transient_case_cycles_consumed",
        "optimizer_steps",
        "peak_gpu_memory_bytes",
        "active_parameter_count",
    ):
        _require(
            isinstance(cell.get(key), int)
            and not isinstance(cell.get(key), bool)
            and cell[key] > 0,
            f"{label}_{key}",
        )
    _require(
        cell["transient_case_cycles_consumed"] % 584 == 0,
        f"{label}_transient_case_cycles",
    )
    training_gpu_seconds = cell.get("training_gpu_seconds")
    _require(
        isinstance(training_gpu_seconds, (int, float))
        and not isinstance(training_gpu_seconds, bool)
        and math.isfinite(float(training_gpu_seconds))
        and float(training_gpu_seconds) > 0.0,
        f"{label}_training_gpu_seconds",
    )
    _require(
        cell.get("steady_head_active") is (mode == "eligible_steady"),
        f"{label}_steady_head",
    )
    _require(
        cell.get("additional_steady_forward_backward_work")
        is (mode == "eligible_steady"),
        f"{label}_steady_compute",
    )
    if mode == "eligible_steady":
        _require(
            _is_sha256(cell.get("steady_objective_scale_result_sha256")),
            f"{label}_steady_scale",
        )
    else:
        _require(
            cell.get("steady_objective_scale_result_sha256") is None,
            f"{label}_transient_scale",
        )
    _require(cell.get("case_ids_included") is False, f"{label}_identifiers")
    _require(
        cell.get("locked_test_field_case_count_read") == 0
        and cell.get("processed_only_extra_field_case_count_read") == 0,
        f"{label}_sealed",
    )
    _require(cell.get("paper_result_or_claim") is False, f"{label}_claim")
    rows = cell.get("per_case_without_identifiers")
    expected = int(config["split"]["validation_cases"])
    _require(isinstance(rows, list) and len(rows) == expected, f"{label}_case_count")
    parsed: list[dict[str, float]] = []
    for row in rows:
        _require(isinstance(row, Mapping), f"{label}_row")
        values: dict[str, float] = {}
        for metric in METRICS:
            _require(metric in row, f"{label}_{metric}")
            value = float(row[metric])
            _require(math.isfinite(value), f"{label}_finite_{metric}")
            if metric == "osi_coverage":
                _require(0.0 <= value <= 1.0, f"{label}_coverage")
            else:
                _require(value >= 0.0, f"{label}_nonnegative_{metric}")
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


def paired_linear_contrast(
    rows_by_cell: Mapping[str, Sequence[Mapping[str, float]]],
    coefficients: Mapping[str, float],
    metric: str,
    *,
    replicates: int = 10_000,
    seed: int = 20_260_821,
) -> dict[str, Any]:
    """Bootstrap a case-paired linear factorial contrast."""

    _require(metric in METRIC_DIRECTIONS, "metric")
    _require(set(coefficients).issubset(rows_by_cell), "coefficient_cells")
    counts = {len(rows_by_cell[label]) for label in coefficients}
    _require(len(counts) == 1 and next(iter(counts)) >= 2, "paired_count")
    _require(replicates >= 100, "replicates")
    count = next(iter(counts))
    values = [
        sum(
            float(coefficient) * float(rows_by_cell[label][index][metric])
            for label, coefficient in coefficients.items()
        )
        for index in range(count)
    ]
    _require(all(math.isfinite(value) for value in values), "finite_contrast")
    point = sum(values) / count
    generator = random.Random(seed)
    means = [
        sum(values[generator.randrange(count)] for _ in range(count)) / count
        for _ in range(replicates)
    ]
    means.sort()
    direction = METRIC_DIRECTIONS[metric]
    if direction == "lower":
        favorable = sum(value < 0.0 for value in means) / replicates
    else:
        favorable = sum(value > 0.0 for value in means) / replicates
    return {
        "metric": metric,
        "direction": direction,
        "estimand": "paired_mean_linear_contrast",
        "coefficients": dict(coefficients),
        "point_delta": point,
        "ci95_low": _quantile(means, 0.025),
        "ci95_high": _quantile(means, 0.975),
        "bootstrap_probability_favorable_direction": favorable,
        "replicates": replicates,
        "seed": seed,
        "paired_case_count": count,
    }


def analyze_matched_information(
    cells: Mapping[str, Mapping[str, Any]],
    config: Mapping[str, Any],
    *,
    replicates: int | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Report all four cell means and five prespecified paired contrasts."""

    validate_config(config)
    _require(set(cells) == set(CELL_ORDER), "complete_factorial")
    rows = {
        label: extract_cell_rows(cells[label], label, config) for label in CELL_ORDER
    }
    _require(
        cells["control_T"]["transient_training_protocol_sha256"]
        == cells["control_TS"]["transient_training_protocol_sha256"],
        "control_training_protocol_pair",
    )
    _require(
        cells["proposal_T"]["transient_training_protocol_sha256"]
        == cells["proposal_TS"]["transient_training_protocol_sha256"],
        "proposal_training_protocol_pair",
    )
    _require(
        len({int(cells[label]["training_seed"]) for label in CELL_ORDER}) == 1,
        "shared_training_seed",
    )
    if replicates is None:
        replicates = int(config["bootstrap"]["replicates"])
    if seed is None:
        seed = int(config["bootstrap"]["seed"])
    _require(replicates >= 100, "bootstrap_replicates")
    means = {
        label: {
            metric: sum(row[metric] for row in cell_rows) / len(cell_rows)
            for metric in METRICS
        }
        for label, cell_rows in rows.items()
    }
    contrasts = {
        contrast: {
            metric: paired_linear_contrast(
                rows,
                coefficients,
                metric,
                replicates=replicates,
                seed=seed + contrast_index * 10_007 + metric_index,
            )
            for metric_index, metric in enumerate(METRICS)
        }
        for contrast_index, (contrast, coefficients) in enumerate(CONTRASTS.items())
    }
    return {
        "schema_version": "aurora.private.aneug_release_730_matched_information_analysis_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "evidence_role": "validation_development_matched_information_factorial",
        "cell_means": means,
        "paired_contrasts": contrasts,
        "primary_claim_error_metrics": list(PRIMARY_CLAIM_ERROR_METRICS),
        "supporting_error_metrics": list(SUPPORTING_ERROR_METRICS),
        "diagnostic_metrics": list(DIAGNOSTIC_METRICS),
        "prediction_valid_coverage_is_gate_or_claim_endpoint": False,
        "automatic_winner": None,
        "automatic_novelty_conclusion": None,
        "absolute_performance_threshold": None,
        "interaction_is_not_standalone_novelty": True,
        "paired_case_count": int(config["split"]["validation_cases"]),
        "paired_unit": config["bootstrap"]["paired_unit"],
        "same_eligible_steady_indices_for_control_and_proposal": True,
        "same_steady_exposure_schedule_rule_for_control_and_proposal": True,
        "training_accounting": {
            label: {
                key: cells[label][key]
                for key in config["training_accounting"]["required_cell_fields"]
            }
            for label in CELL_ORDER
        },
        "primary_method_comparisons_are_within_information_mode": True,
        "steady_contrasts_are_registered_augmentation_protocol_effects": True,
        "steady_contrasts_are_label_only_causal_effects": False,
        "compute_matched_transient_replay_control_present": False,
        "bounded_auxiliary_attribution_sidecar_registered": True,
        "auxiliary_attribution_protocol_id": (
            "aneug_release_730_auxiliary_compute_attribution_v1"
        ),
        "auxiliary_attribution_is_primary_factorial_gate": False,
        "steady_exposure": {
            label: {
                "epochs": cells[label]["steady_exposure_epochs"],
                "examples": cells[label]["steady_examples_consumed"],
                "prefix_sha256": cells[label]["steady_exposure_prefix_sha256"],
            }
            for label in ("control_TS", "proposal_TS")
        },
        "case_identifiers_included": False,
        "locked_test_or_extra_values_read": False,
        "population_inference": False,
        "paper_performance_claim": False,
    }
