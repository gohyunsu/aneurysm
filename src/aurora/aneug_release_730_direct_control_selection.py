"""Select the release-730 direct control from three terminal validation results.

The analyzer verifies the shared 73-case order and sealed development scope,
reports every method and paired contrast, and identifies the feasible direct
control with the lowest case-mean field error. It does not infer equivalence,
select a candidate, open the locked test or create a paper/novelty conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_validation_comparison import (
    CORE_METRICS,
    metric_means,
    paired_bootstrap_delta,
    pareto_set,
)


class Release730DirectControlSelectionError(RuntimeError):
    """Raised when result provenance, scope or values are incomparable."""


CONTROL_ORDER = (
    "released_graph_unet_adapter",
    "ghd_gps_unet",
    "transolver",
)
RESULT_CONTRACTS = {
    "released_graph_unet_adapter": {
        "schema_version": "aurora.aneug_release_730_graphunet.private_result.v1",
        "protocol_id": "aneug_release_730_official_graphunet_baseline_v1",
        "status": "complete_validation_development",
    },
    "ghd_gps_unet": {
        "schema_version": "aurora.private.aneug_release_730_ghd_gps_result.v1",
        "protocol_id": "aneug_release_730_ghd_gps_baseline_v1",
        "status": "complete",
    },
    "transolver": {
        "schema_version": "aurora.private.aneug_release_730_transolver_result.v1",
        "protocol_id": "aneug_release_730_transolver_baseline_v1",
        "status": "complete",
    },
}
PERFORMANCE_METRICS = (
    "field_relative_l2",
    "tawss_normalized_absolute_error",
    "osi_mae",
)
DIAGNOSTIC_METRICS = ("osi_coverage",)
GRAPH_ORDER_ATTESTATION_SCHEMA = (
    "aurora.private.aneug_release_730_direct_order_attestation.v1"
)
GRAPH_TERMINAL_OUTCOME_SCHEMA = (
    "aurora.private.aneug_release_730_graphunet_terminal_outcome.v1"
)


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise Release730DirectControlSelectionError(label)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_git_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value)
    )


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
    return digest.hexdigest()


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_direct_control_selection.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_direct_control_selection_v1",
        "protocol_id",
    )
    _require(config.get("status") == "prepared_result_pending", "status")
    split = config["split"]
    _require(
        split["validation_cases"] == 73
        and _is_sha256(split["validation_case_digest"])
        and _is_sha256(split["validation_loader_order_sha256"])
        and _is_sha256(split["private_manifest_sha256"])
        and split["locked_test_read"] is False
        and split["processed_only_extra_read"] is False,
        "split",
    )
    controls = config["controls"]
    _require(
        tuple(controls["ordered_labels"]) == CONTROL_ORDER
        and tuple(controls["core_metrics"]) == CORE_METRICS
        and tuple(controls["performance_metrics"]) == PERFORMANCE_METRICS
        and tuple(controls["diagnostic_metrics"]) == DIAGNOSTIC_METRICS
        and controls["paired_unit"] == "synthetic_geometry_case"
        and controls["same_validation_order_required"] is True,
        "controls",
    )
    bootstrap = config["bootstrap"]
    _require(
        bootstrap["replicates"] == 10_000
        and bootstrap["seed"] == 20_260_824
        and bootstrap["interval"] == "percentile_95pct"
        and bootstrap["population_inference"] is False,
        "bootstrap",
    )
    selection = config["selection"]
    _require(
        selection["metric"] == "case_mean_field_relative_l2"
        and selection["rule"]
        == "lowest_case_mean_validation_field_error_then_registered_order_exact_tie"
        and selection["direct_control_selected"] is True
        and selection["automatic_paper_winner"] is False
        and selection["automatic_novelty_conclusion"] is False
        and selection["absolute_performance_threshold"] is None
        and selection["report_all_controls"] is True
        and selection["report_all_pairwise_deltas"] is True
        and selection["report_pareto_set"] is True
        and tuple(selection["pareto_metrics"]) == PERFORMANCE_METRICS
        and selection["model_specific_osi_coverage_is_selection_endpoint"] is False
        and selection["invalid_osi_predictions_are_penalized_in_osi_mae"] is True
        and selection["zero_crossing_interval_is_equivalence"] is False,
        "selection",
    )
    boundary = config["boundary"]
    _require(
        boundary["execute_now"] is False
        and boundary["requires_three_terminal_validation_results"] is True
        and boundary["requires_three_terminal_records"] is True
        and boundary["requires_fresh_private_activation"] is True
        and boundary["validation_development_only"] is True
        and boundary["locked_test_or_extra_access"] is False
        and boundary["paper_performance_claim"] is False
        and boundary["publish_numeric_result"] is False,
        "boundary",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_direct_control_selection_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    for group in ("result_sha256", "terminal_record_sha256"):
        values = activation.get(group)
        _require(
            isinstance(values, Mapping) and set(values) == set(CONTROL_ORDER),
            group,
        )
        _require(all(_is_sha256(values[label]) for label in CONTROL_ORDER), group)
    _require(
        _is_sha256(activation.get("released_graph_unet_order_attestation_sha256"))
        and _is_sha256(
            activation.get("released_graph_unet_terminal_outcome_sha256")
        ),
        "activation_graph_provenance",
    )
    split = config["split"]
    _require(
        activation.get("validation_case_digest") == split["validation_case_digest"]
        and activation.get("validation_loader_order_sha256")
        == split["validation_loader_order_sha256"]
        and activation.get("private_split_manifest_sha256")
        == split["private_manifest_sha256"],
        "activation_split",
    )
    _require(
        activation.get("read_locked_test_or_extra") is False
        and activation.get("candidate_selection") is False
        and activation.get("paper_performance_claim") is False,
        "activation_boundary",
    )
    return activation


def validate_graph_order_attestation(
    attestation: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    direct_result_sha256: str,
    direct_terminal_outcome_sha256: str,
) -> None:
    """Validate the separately preserved order evidence for the historical result."""

    _require(
        attestation.get("schema_version") == GRAPH_ORDER_ATTESTATION_SCHEMA,
        "released_graph_unet_adapter_attestation_schema",
    )
    _require(
        _is_sha256(direct_result_sha256)
        and _is_sha256(direct_terminal_outcome_sha256)
        and attestation.get("direct_result_sha256") == direct_result_sha256
        and attestation.get("direct_terminal_record_sha256")
        == direct_terminal_outcome_sha256,
        "released_graph_unet_adapter_attestation_artifacts",
    )
    split = config["split"]
    _require(
        attestation.get("validation_case_digest")
        == split["validation_case_digest"]
        and attestation.get("validation_loader_order_sha256")
        == split["validation_loader_order_sha256"]
        and attestation.get("private_split_manifest_sha256")
        == split["private_manifest_sha256"]
        and attestation.get("order_derivation")
        == "flatten_private_validation_components_in_stored_order"
        and attestation.get("producer_order_path")
        == "validate_split_evidence_then_selected_training_records_over_buckets_validation",
        "released_graph_unet_adapter_attestation_split",
    )
    _require(
        _is_git_sha(attestation.get("producer_public_commit"))
        and attestation.get("manifest_digest_recomputed_without_identifier_output")
        is True
        and attestation.get("case_ids_included") is False
        and attestation.get("scientific_result_changed") is False
        and attestation.get("locked_test_or_extra_read") is False,
        "released_graph_unet_adapter_attestation_boundary",
    )


def validate_graph_terminal_chain(
    *,
    result_sha256: str,
    terminal_sha256: str,
    terminal: Mapping[str, Any],
    terminal_outcome_sha256: str,
    terminal_outcome: Mapping[str, Any],
    order_attestation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> None:
    """Bind the raw terminal marker, terminal summary, result and order evidence."""

    _require(
        terminal.get("exit_code") == 0 and terminal.get("complete") is True,
        "released_graph_unet_adapter_terminal",
    )
    _require(
        terminal_outcome.get("schema_version") == GRAPH_TERMINAL_OUTCOME_SCHEMA
        and terminal_outcome.get("job_id") == terminal.get("job_id"),
        "released_graph_unet_adapter_terminal_outcome_identity",
    )
    terminal_status = terminal_outcome.get("terminal_status")
    raw_artifacts = terminal_outcome.get("raw_artifacts")
    _require(
        isinstance(terminal_status, Mapping)
        and terminal_status.get("exit_code") == 0
        and terminal_status.get("complete") is True
        and terminal_status.get("result_status")
        == RESULT_CONTRACTS["released_graph_unet_adapter"]["status"],
        "released_graph_unet_adapter_terminal_outcome_status",
    )
    _require(
        isinstance(raw_artifacts, Mapping)
        and raw_artifacts.get("attempt_status_sha256") == terminal_sha256
        and raw_artifacts.get("result_sha256") == result_sha256,
        "released_graph_unet_adapter_terminal_outcome_artifacts",
    )
    validate_graph_order_attestation(
        order_attestation,
        config,
        direct_result_sha256=result_sha256,
        direct_terminal_outcome_sha256=terminal_outcome_sha256,
    )
    _require(
        terminal_outcome.get("public_training_commit")
        == order_attestation.get("producer_public_commit"),
        "released_graph_unet_adapter_producer_commit",
    )


def _parse_rows(rows: Any, expected_count: int) -> list[dict[str, float]]:
    _require(isinstance(rows, list) and len(rows) == expected_count, "case_count")
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
        parsed.append(values)
    return parsed


def extract_control_rows(
    label: str,
    result: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    graph_order_attestation: Mapping[str, Any] | None = None,
    graph_result_sha256: str | None = None,
    graph_terminal_outcome_sha256: str | None = None,
) -> list[dict[str, float]]:
    _require(label in RESULT_CONTRACTS, "control_label")
    contract = RESULT_CONTRACTS[label]
    _require(
        result.get("schema_version") == contract["schema_version"]
        and result.get("protocol_id") == contract["protocol_id"]
        and result.get("status") == contract["status"],
        f"{label}_identity",
    )
    split = config["split"]
    if label == "released_graph_unet_adapter":
        _require(
            graph_order_attestation is not None
            and graph_result_sha256 is not None
            and graph_terminal_outcome_sha256 is not None,
            f"{label}_attestation_required",
        )
        validate_graph_order_attestation(
            graph_order_attestation,
            config,
            direct_result_sha256=graph_result_sha256,
            direct_terminal_outcome_sha256=graph_terminal_outcome_sha256,
        )
        _require(
            result.get("validation_case_count") == split["validation_cases"],
            f"{label}_split",
        )
        optional_result_split = {
            "validation_case_digest": split["validation_case_digest"],
            "validation_loader_order_sha256": split[
                "validation_loader_order_sha256"
            ],
            "private_split_manifest_sha256": split["private_manifest_sha256"],
        }
        for key, expected in optional_result_split.items():
            _require(
                key not in result or result.get(key) == expected,
                f"{label}_split_conflict",
            )
    else:
        _require(
            result.get("validation_case_digest") == split["validation_case_digest"]
            and result.get("validation_loader_order_sha256")
            == split["validation_loader_order_sha256"]
            and result.get("private_split_manifest_sha256")
            == split["private_manifest_sha256"]
            and result.get("validation_case_count") == split["validation_cases"],
            f"{label}_split",
        )
    _require(result.get("case_ids_included") is False, f"{label}_identifiers")
    if label == "released_graph_unet_adapter":
        _require(
            result.get("single_seed_validation_development_only") is True
            and result.get("test_field_case_count_read") == 0
            and result.get("processed_only_extra_field_case_count_read") == 0
            and result.get("paper_result_or_claim") is False,
            f"{label}_boundary",
        )
    else:
        _require(
            result.get("development_only") is True
            and result.get("locked_test_field_case_count_read") == 0
            and result.get("processed_only_extra_field_case_count_read") == 0
            and result.get("paper_performance_claim") is False
            and result.get("proposed_method") is False,
            f"{label}_boundary",
        )
    validation = result.get("validation")
    _require(isinstance(validation, Mapping), f"{label}_validation")
    return _parse_rows(
        validation.get("per_case_without_identifiers"), split["validation_cases"]
    )


def analyze_direct_controls(
    results: Mapping[str, Mapping[str, Any]],
    config: Mapping[str, Any],
    *,
    graph_order_attestation: Mapping[str, Any],
    graph_result_sha256: str,
    graph_terminal_outcome_sha256: str,
    replicates: int | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    validate_config(config)
    _require(tuple(results) == CONTROL_ORDER, "result_order")
    rows = {
        label: extract_control_rows(
            label,
            results[label],
            config,
            graph_order_attestation=graph_order_attestation,
            graph_result_sha256=graph_result_sha256,
            graph_terminal_outcome_sha256=graph_terminal_outcome_sha256,
        )
        for label in CONTROL_ORDER
    }
    means = {label: metric_means(rows[label]) for label in CONTROL_ORDER}
    selected = min(
        CONTROL_ORDER,
        key=lambda label: (
            means[label]["field_relative_l2"],
            CONTROL_ORDER.index(label),
        ),
    )
    if replicates is None:
        replicates = int(config["bootstrap"]["replicates"])
    if seed is None:
        seed = int(config["bootstrap"]["seed"])
    _require(replicates >= 100, "bootstrap_replicates")
    paired: dict[str, dict[str, Any]] = {}
    pair_index = 0
    for left_index, left in enumerate(CONTROL_ORDER):
        for right in CONTROL_ORDER[left_index + 1 :]:
            key = f"{left}_minus_{right}"
            paired[key] = {
                metric: paired_bootstrap_delta(
                    rows[left],
                    rows[right],
                    metric,
                    replicates=replicates,
                    seed=seed + pair_index * 10_007 + metric_index,
                )
                for metric_index, metric in enumerate(CORE_METRICS)
            }
            pair_index += 1
    return {
        "schema_version": "aurora.private.aneug_release_730_direct_control_selection_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "evidence_role": "validation_development_direct_control_selection",
        "control_means": means,
        "all_pairwise_deltas": paired,
        "pareto_set": pareto_set(means, metrics=PERFORMANCE_METRICS),
        "pareto_metrics": list(PERFORMANCE_METRICS),
        "diagnostic_metrics": list(DIAGNOSTIC_METRICS),
        "osi_coverage_role": (
            "model_specific_prediction_validity_diagnostic_not_selection_endpoint"
        ),
        "selected_direct_control": selected,
        "selection_metric": "case_mean_field_relative_l2",
        "selection_rule": config["selection"]["rule"],
        "exact_tie_break_order": list(CONTROL_ORDER),
        "automatic_paper_winner": None,
        "automatic_novelty_conclusion": None,
        "absolute_performance_threshold": None,
        "zero_crossing_interval_is_equivalence": False,
        "paired_case_count": config["split"]["validation_cases"],
        "paired_unit": config["controls"]["paired_unit"],
        "case_identifiers_included": False,
        "locked_test_or_extra_values_read": False,
        "population_inference": False,
        "candidate_selected": False,
        "paper_performance_claim": False,
    }


def _atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, target)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--released-graph-unet-order-attestation", type=Path)
    parser.add_argument("--released-graph-unet-terminal-outcome", type=Path)
    for label in CONTROL_ORDER:
        option = label.replace("_", "-")
        parser.add_argument(f"--{option}-result", type=Path)
        parser.add_argument(f"--{option}-terminal", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    _require(
        args.activation is not None
        and args.expected_commit is not None
        and args.released_graph_unet_order_attestation is not None
        and args.released_graph_unet_terminal_outcome is not None
        and args.output is not None,
        "execution_arguments",
    )
    activation = validate_activation(args.activation, config, args.expected_commit)
    results: dict[str, Mapping[str, Any]] = {}
    for label in CONTROL_ORDER:
        result_path = getattr(args, f"{label}_result")
        terminal_path = getattr(args, f"{label}_terminal")
        _require(result_path is not None and terminal_path is not None, f"{label}_paths")
        _require(
            file_sha256(result_path) == activation["result_sha256"][label]
            and file_sha256(terminal_path)
            == activation["terminal_record_sha256"][label],
            f"{label}_hash",
        )
        results[label] = json.loads(result_path.read_text(encoding="utf-8"))
    graph_label = "released_graph_unet_adapter"
    graph_result_path = getattr(args, f"{graph_label}_result")
    graph_terminal_path = getattr(args, f"{graph_label}_terminal")
    graph_result_sha256 = file_sha256(graph_result_path)
    graph_terminal_sha256 = file_sha256(graph_terminal_path)
    graph_order_attestation_sha256 = file_sha256(
        args.released_graph_unet_order_attestation
    )
    graph_terminal_outcome_sha256 = file_sha256(
        args.released_graph_unet_terminal_outcome
    )
    _require(
        graph_order_attestation_sha256
        == activation["released_graph_unet_order_attestation_sha256"]
        and graph_terminal_outcome_sha256
        == activation["released_graph_unet_terminal_outcome_sha256"],
        "released_graph_unet_adapter_provenance_hash",
    )
    graph_order_attestation = json.loads(
        args.released_graph_unet_order_attestation.read_text(encoding="utf-8")
    )
    graph_terminal_outcome = json.loads(
        args.released_graph_unet_terminal_outcome.read_text(encoding="utf-8")
    )
    graph_terminal = json.loads(graph_terminal_path.read_text(encoding="utf-8"))
    validate_graph_terminal_chain(
        result_sha256=graph_result_sha256,
        terminal_sha256=graph_terminal_sha256,
        terminal=graph_terminal,
        terminal_outcome_sha256=graph_terminal_outcome_sha256,
        terminal_outcome=graph_terminal_outcome,
        order_attestation=graph_order_attestation,
        config=config,
    )
    output = analyze_direct_controls(
        results,
        config,
        graph_order_attestation=graph_order_attestation,
        graph_result_sha256=graph_result_sha256,
        graph_terminal_outcome_sha256=graph_terminal_outcome_sha256,
    )
    output["activation_sha256"] = file_sha256(args.activation)
    output["result_sha256"] = dict(activation["result_sha256"])
    output["terminal_record_sha256"] = dict(activation["terminal_record_sha256"])
    output["released_graph_unet_order_attestation_sha256"] = (
        graph_order_attestation_sha256
    )
    output["released_graph_unet_terminal_outcome_sha256"] = (
        graph_terminal_outcome_sha256
    )
    _atomic_json(args.output, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
