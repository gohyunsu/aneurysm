"""Bounded T+M versus T+S attribution for matched release-730 training.

T+M reuses the T+S single-field head and performs a second geometry pass for
each transient case, but its target is that train case's cycle-mean WSS.  The
comparison therefore controls the auxiliary model path and its principal
forward/backward structure.  It does not match target information, storage
I/O, or all system-level compute and is never labelled a causal steady-label
effect.  The primary T/T+S method factorial remains unchanged.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from aurora.aneug_release_730_matched_information_analysis import (
    METRICS,
    paired_linear_contrast,
)


class AuxiliaryComputeAttributionError(RuntimeError):
    """Raised when a T+M/T+S attribution input violates its contract."""


CELL_ORDER = (
    "control_TM",
    "control_TS",
    "proposal_TM",
    "proposal_TS",
)
CONTRASTS = {
    "steady_minus_transient_mean_control": {
        "control_TM": -1.0,
        "control_TS": 1.0,
    },
    "steady_minus_transient_mean_proposal": {
        "proposal_TM": -1.0,
        "proposal_TS": 1.0,
    },
}


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise AuxiliaryComputeAttributionError(label)


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
        == "aurora.aneug_release_730_auxiliary_compute_attribution.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_auxiliary_compute_attribution_v1",
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
    attribution = config["attribution"]
    _require(tuple(attribution["cells"]) == CELL_ORDER, "cells")
    _require(tuple(attribution["metrics"]) == METRICS, "metrics")
    _require(attribution["contrasts"] == CONTRASTS, "contrasts")
    _require(
        attribution["examples_per_transient_epoch"] == 584
        and attribution["one_auxiliary_forward_backward_per_transient_case"] is True
        and attribution["shared_single_field_head_within_role"] is True
        and attribution["shared_auxiliary_coefficient"] == 1.0
        and attribution["task_specific_train_only_output_scale"] is True
        and attribution["same_transient_protocol_within_role"] is True
        and attribution["same_training_seed_across_four_cells"] is True
        and attribution["single_seed_development_only"] is True,
        "attribution",
    )
    interpretation = config["interpretation"]
    _require(
        interpretation["primary_factorial_replaced"] is False
        and interpretation["fully_compute_matched"] is False
        and interpretation["controls_head_and_model_forward_backward_structure"]
        is True
        and interpretation["controls_storage_io_or_target_information"] is False
        and interpretation["causal_steady_label_effect"] is False
        and interpretation["automatic_winner"] is False
        and interpretation["automatic_novelty_conclusion"] is False
        and interpretation["absolute_performance_threshold"] is None
        and interpretation["standalone_novelty"] is False,
        "interpretation",
    )
    bootstrap = config["bootstrap"]
    _require(
        bootstrap["replicates"] == 10_000
        and bootstrap["seed"] == 20_260_824
        and bootstrap["interval"] == "percentile_95pct"
        and bootstrap["paired_unit"] == "synthetic_geometry_case"
        and bootstrap["population_inference"] is False,
        "bootstrap",
    )
    boundary = config["boundary"]
    _require(
        boundary["execute_now"] is False
        and boundary[
            "requires_two_transient_mean_and_two_steady_terminal_validation_results"
        ]
        is True
        and boundary["required_for_primary_factorial"] is False
        and boundary["required_before_steady_specific_manuscript_interpretation"]
        is True
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
    mode = "transient_mean" if label.endswith("TM") else "eligible_steady"
    return role, mode


def extract_cell_rows(
    cell: Mapping[str, Any], label: str, config: Mapping[str, Any]
) -> list[dict[str, float]]:
    role, mode = _expected_role_and_mode(label)
    is_steady = mode == "eligible_steady"
    _require(
        cell.get("schema_version")
        == (
            "aurora.aneug_release_730_matched_information_cell.v1"
            if is_steady
            else "aurora.aneug_release_730_auxiliary_compute_cell.v1"
        ),
        f"{label}_schema",
    )
    _require(
        cell.get("protocol_id")
        == (
            "aneug_release_730_matched_information_analysis_v1"
            if is_steady
            else config["protocol_id"]
        ),
        f"{label}_protocol",
    )
    _require(cell.get("status") == "complete_validation_development", f"{label}_status")
    _require(cell.get("model_role") == role, f"{label}_role")
    _require(cell.get("information_mode") == mode, f"{label}_mode")
    split = config["split"]
    _require(
        cell.get("validation_case_digest") == split["validation_case_digest"]
        and cell.get("private_split_manifest_sha256")
        == split["private_manifest_sha256"]
        and cell.get("validation_loader_order_sha256")
        == split["validation_loader_order_sha256"],
        f"{label}_split",
    )
    _require(_is_sha256(cell.get("transient_training_protocol_sha256")), f"{label}_training_protocol")
    _require(
        isinstance(cell.get("training_seed"), int)
        and not isinstance(cell.get("training_seed"), bool),
        f"{label}_training_seed",
    )
    for key in (
        "epochs_completed",
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
    epochs = int(cell["epochs_completed"])
    expected_examples = epochs * int(config["attribution"]["examples_per_transient_epoch"])
    _require(
        cell["transient_case_cycles_consumed"] == expected_examples,
        f"{label}_transient_case_cycles",
    )
    seconds = cell.get("training_gpu_seconds")
    scale = cell.get("single_field_output_scale")
    _require(
        isinstance(seconds, (int, float))
        and not isinstance(seconds, bool)
        and math.isfinite(float(seconds))
        and float(seconds) > 0.0,
        f"{label}_training_gpu_seconds",
    )
    _require(
        isinstance(scale, (int, float))
        and not isinstance(scale, bool)
        and math.isfinite(float(scale))
        and float(scale) > 0.0,
        f"{label}_single_field_scale",
    )
    _require(cell.get("single_field_head_active") is True, f"{label}_head")
    _require(
        cell.get("single_field_auxiliary_coefficient") == 1.0
        and cell.get("single_field_auxiliary_examples_consumed") == expected_examples
        and cell.get("additional_auxiliary_forward_backward_work") is True,
        f"{label}_auxiliary_accounting",
    )
    if is_steady:
        _require(
            cell.get("single_field_auxiliary_source") == "eligible_steady_wss"
            and cell.get("single_field_output_scale_source")
            == "eligible_steady_physical_vector_rms_from_bound_descriptive_audit"
            and _is_sha256(cell.get("single_field_scale_source_sha256"))
            and cell.get("steady_head_active") is True
            and cell.get("additional_steady_forward_backward_work") is True
            and cell.get("transient_mean_auxiliary_examples_consumed") == 0
            and cell.get("steady_wss_rows_read_for_auxiliary") == expected_examples
            and cell.get("steady_examples_consumed") == expected_examples
            and cell.get("eligible_steady_rows") == 13_985
            and cell.get("eligible_steady_case_digest")
            == "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc"
            and _is_sha256(cell.get("steady_exposure_prefix_sha256")),
            f"{label}_steady_auxiliary",
        )
    else:
        _require(
            cell.get("single_field_auxiliary_source")
            == "same_train_case_cycle_mean"
            and cell.get("single_field_output_scale_source")
            == "transient_train_cycle_mean_physical_vector_rms_computed_from_frozen_train_fields"
            and _is_sha256(cell.get("single_field_scale_source_sha256"))
            and cell.get("steady_head_active") is False
            and cell.get("additional_steady_forward_backward_work") is False
            and cell.get("transient_mean_auxiliary_examples_consumed")
            == expected_examples
            and cell.get("steady_wss_rows_read_for_auxiliary") == 0
            and cell.get("steady_examples_consumed") == 0
            and cell.get("eligible_steady_rows") == 0
            and cell.get("eligible_steady_case_digest") is None
            and cell.get("steady_exposure_prefix_sha256") is None,
            f"{label}_transient_mean_auxiliary",
        )
    _require(cell.get("case_ids_included") is False, f"{label}_identifiers")
    _require(
        cell.get("locked_test_field_case_count_read") == 0
        and cell.get("processed_only_extra_field_case_count_read") == 0,
        f"{label}_sealed",
    )
    _require(cell.get("paper_result_or_claim") is False, f"{label}_claim")
    rows = cell.get("per_case_without_identifiers")
    _require(
        isinstance(rows, list) and len(rows) == int(split["validation_cases"]),
        f"{label}_case_count",
    )
    parsed: list[dict[str, float]] = []
    for row in rows:
        _require(isinstance(row, Mapping), f"{label}_row")
        values: dict[str, float] = {}
        for metric in METRICS:
            value = float(row.get(metric, math.nan))
            _require(math.isfinite(value), f"{label}_finite_{metric}")
            if metric == "osi_coverage":
                _require(0.0 <= value <= 1.0, f"{label}_coverage")
            else:
                _require(value >= 0.0, f"{label}_nonnegative_{metric}")
            values[metric] = value
        parsed.append(values)
    return parsed


def analyze_auxiliary_compute_attribution(
    cells: Mapping[str, Mapping[str, Any]],
    config: Mapping[str, Any],
    *,
    replicates: int | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Report paired T+S-minus-T+M development contrasts without a gate."""

    validate_config(config)
    _require(set(cells) == set(CELL_ORDER), "complete_attribution")
    rows = {
        label: extract_cell_rows(cells[label], label, config) for label in CELL_ORDER
    }
    for role in ("control", "proposal"):
        transient_mean = cells[f"{role}_TM"]
        steady = cells[f"{role}_TS"]
        for field in (
            "model_family",
            "objective_variant",
            "selected_response_rank",
            "transient_training_protocol_sha256",
        ):
            _require(
                transient_mean.get(field) == steady.get(field),
                f"{role}_{field}_pair",
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
        "schema_version": "aurora.private.aneug_release_730_auxiliary_compute_attribution_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "evidence_role": "validation_development_auxiliary_attribution_sidecar",
        "cell_means": means,
        "paired_contrasts": contrasts,
        "automatic_winner": None,
        "automatic_novelty_conclusion": None,
        "absolute_performance_threshold": None,
        "primary_factorial_replaced": False,
        "fully_compute_matched": False,
        "controls_head_and_model_forward_backward_structure": True,
        "controls_storage_io_or_target_information": False,
        "steady_minus_transient_mean_is_label_only_causal_effect": False,
        "single_seed_development_only": True,
        "paired_case_count": int(config["split"]["validation_cases"]),
        "paired_unit": config["bootstrap"]["paired_unit"],
        "training_accounting": {
            label: {
                key: cells[label][key]
                for key in (
                    "epochs_completed",
                    "transient_case_cycles_consumed",
                    "single_field_auxiliary_examples_consumed",
                    "optimizer_steps",
                    "training_gpu_seconds",
                    "peak_gpu_memory_bytes",
                    "active_parameter_count",
                    "single_field_auxiliary_source",
                    "single_field_output_scale_source",
                    "steady_wss_rows_read_for_auxiliary",
                )
            }
            for label in CELL_ORDER
        },
        "case_identifiers_included": False,
        "locked_test_or_extra_values_read": False,
        "population_inference": False,
        "paper_performance_claim": False,
    }
