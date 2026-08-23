"""Threshold-free paired comparison of the release-730 response oracle.

The oracle uses true validation amplitudes and coefficients.  This module
therefore reports a representation ceiling against the released Graph U-Net
adapter; it cannot select a learned rank, approve the global branch or create a
paper performance claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_release_730_split import _canonical_digest, _ordered_digest
from aurora.aneug_validation_comparison import (
    CORE_METRICS,
    metric_means,
    paired_bootstrap_delta,
    pareto_set,
)


class Release730OracleComparisonError(RuntimeError):
    """Raised when paired result provenance or values are invalid."""


RANK_GRID = (0, 16, 32, 64, 128, 256)
R1_NOMINATION_RULE = "positive_storage_aware_pareto_min_lower_median_max"
VALIDATION_LOADER_ORDER_SHA256 = (
    "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30"
)


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise Release730OracleComparisonError(label)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
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
        == "aurora.aneug_release_730_oracle_comparison.v1",
        "config_schema",
    )
    _require(config.get("status") == "prepared_result_pending", "status")
    split = config["split"]
    _require(
        split["validation_cases"] == 73
        and split["validation_loader_order_sha256"]
        == VALIDATION_LOADER_ORDER_SHA256
        and split["shared_loader_order_provenance_required"] is True
        and split["locked_test_read"] is False
        and split["processed_only_extra_read"] is False,
        "split",
    )
    comparison = config["comparison"]
    _require(
        tuple(comparison["rank_grid"]) == RANK_GRID
        and tuple(comparison["core_metrics"]) == CORE_METRICS
        and comparison["paired_unit"] == "synthetic_geometry_case"
        and comparison["basis_width"] == 80 * 13_902 * 3
        and comparison["basis_dtype_bytes"] == 4,
        "comparison",
    )
    bootstrap = config["bootstrap"]
    _require(
        bootstrap["replicates"] == 10_000
        and bootstrap["seed"] == 20_260_818
        and bootstrap["interval"] == "percentile_95pct"
        and bootstrap["population_inference"] is False,
        "bootstrap",
    )
    decision = config["decision"]
    _require(
        decision["absolute_performance_threshold"] is None
        and decision["automatic_rank_selection"] is False
        and decision["automatic_global_branch_decision"] is False
        and decision["report_all_ranks"] is True
        and decision["report_paired_deltas"] is True,
        "decision",
    )
    _require(
        decision["R1_candidate_nomination_rule"] == R1_NOMINATION_RULE
        and decision["maximum_R1_candidate_ranks"] == 3,
        "nomination_rule",
    )
    boundary = config["boundary"]
    _require(
        boundary["execute_now"] is False
        and boundary["requires_direct_terminal_result"] is True
        and boundary["requires_oracle_terminal_result"] is True
        and boundary["requires_legacy_direct_order_attestation"] is True
        and boundary["requires_fresh_private_activation"] is True
        and boundary["locked_test_or_extra_access"] is False
        and boundary["paper_performance_claim"] is False
        and boundary["publish_numeric_result"] is False
        and boundary["server"] == "introai9"
        and boundary["excluded_server"] == "junjinyong",
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
        == "aurora.private.aneug_release_730_oracle_comparison_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "protocol")
    _require(activation.get("public_commit") == expected_commit, "commit")
    _require(activation.get("quality_conclusion") == "success", "quality")
    for key in ("direct_result_sha256", "oracle_result_sha256"):
        value = activation.get(key)
        _require(isinstance(value, str) and len(value) == 64, key)
    _require(
        activation.get("validation_case_digest")
        == config["split"]["validation_case_digest"],
        "validation_cases",
    )
    _require(
        activation.get("validation_loader_order_sha256")
        == config["split"]["validation_loader_order_sha256"],
        "validation_order",
    )
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"],
        "split_manifest",
    )
    _require(activation.get("read_locked_test_or_extra") is False, "sealed")
    for key in (
        "direct_terminal_record_sha256",
        "oracle_terminal_record_sha256",
        "direct_order_attestation_sha256",
    ):
        value = activation.get(key)
        _require(_is_sha256(value), key)
    _require(activation.get("rank_selection") is False, "rank_selection")
    _require(activation.get("paper_performance_claim") is False, "paper_claim")
    return activation


def validate_direct_order_attestation(
    path: str | Path, config: Mapping[str, Any], activation: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate the order sidecar for the immutable legacy Graph U-Net result."""

    attestation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        attestation.get("schema_version")
        == "aurora.private.aneug_release_730_direct_order_attestation.v1",
        "direct_order_attestation_schema",
    )
    _require(
        attestation.get("direct_result_sha256")
        == activation["direct_result_sha256"]
        and attestation.get("direct_terminal_record_sha256")
        == activation["direct_terminal_record_sha256"],
        "direct_order_attestation_result",
    )
    _require(
        attestation.get("producer_public_commit")
        == "c53b5bc4d0664436de6ae916551448a613e9a4ac"
        and attestation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"],
        "direct_order_attestation_producer",
    )
    _require(
        attestation.get("validation_case_digest")
        == config["split"]["validation_case_digest"]
        and attestation.get("validation_loader_order_sha256")
        == config["split"]["validation_loader_order_sha256"],
        "direct_order_attestation_order",
    )
    _require(
        attestation.get("order_derivation")
        == "flatten_private_validation_components_in_stored_order"
        and attestation.get("case_ids_included") is False
        and attestation.get("scientific_result_changed") is False,
        "direct_order_attestation_scope",
    )
    return attestation


def validate_private_split_manifest(
    path: str | Path, config: Mapping[str, Any], activation: Mapping[str, Any]
) -> dict[str, Any]:
    """Recompute identifier-free validation provenance from the frozen split."""

    manifest_path = Path(path)
    observed_hash = file_sha256(manifest_path)
    _require(
        observed_hash == config["split"]["private_manifest_sha256"]
        and observed_hash == activation["private_split_manifest_sha256"],
        "private_split_manifest_hash",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    components = manifest.get("validation_components")
    _require(isinstance(components, list), "validation_components")
    validation_ids: list[str] = []
    for component in components:
        _require(isinstance(component, Mapping), "validation_component")
        case_ids = component.get("case_ids")
        _require(isinstance(case_ids, list) and case_ids, "validation_component_ids")
        _require(all(isinstance(case_id, str) for case_id in case_ids), "validation_case_id")
        validation_ids.extend(case_ids)
    _require(
        len(validation_ids) == config["split"]["validation_cases"]
        and len(set(validation_ids)) == len(validation_ids),
        "validation_manifest_count",
    )
    case_digest = _canonical_digest(validation_ids)
    order_digest = _ordered_digest(validation_ids)
    _require(
        case_digest == config["split"]["validation_case_digest"],
        "validation_manifest_set",
    )
    _require(
        order_digest == config["split"]["validation_loader_order_sha256"],
        "validation_manifest_order",
    )
    return {
        "private_split_manifest_sha256": observed_hash,
        "validation_case_count": len(validation_ids),
        "validation_case_digest": case_digest,
        "validation_loader_order_sha256": order_digest,
        "case_ids_included": False,
    }


def _validate_rows(rows: Any, expected_case_count: int) -> list[dict[str, float]]:
    _require(isinstance(rows, list) and len(rows) == expected_case_count, "case_count")
    parsed: list[dict[str, float]] = []
    for row in rows:
        _require(isinstance(row, Mapping), "row")
        values: dict[str, float] = {}
        for metric in CORE_METRICS:
            _require(metric in row, f"metric_{metric}")
            value = float(row[metric])
            _require(math.isfinite(value), f"finite_{metric}")
            if metric == "osi_coverage":
                _require(0.0 <= value <= 1.0, "coverage")
            else:
                _require(value >= 0.0, f"nonnegative_{metric}")
            values[metric] = value
        parsed.append(values)
    return parsed


def extract_direct_rows(
    result: Mapping[str, Any], *, expected_case_count: int = 73,
    expected_validation_loader_order_sha256: str = VALIDATION_LOADER_ORDER_SHA256,
    legacy_order_attested: bool = False,
) -> list[dict[str, float]]:
    _require(
        result.get("schema_version")
        == "aurora.aneug_release_730_graphunet.private_result.v1",
        "direct_schema",
    )
    _require(
        result.get("protocol_id")
        == "aneug_release_730_official_graphunet_baseline_v1",
        "direct_protocol",
    )
    _require(result.get("status") == "complete_validation_development", "direct_status")
    _require(
        result.get("single_seed_validation_development_only") is True,
        "direct_role",
    )
    _require(result.get("case_ids_included") is False, "direct_identifiers")
    _require(
        result.get("test_field_case_count_read") == 0
        and result.get("processed_only_extra_field_case_count_read") == 0,
        "direct_sealed",
    )
    _require(result.get("paper_result_or_claim") is False, "direct_claim")
    observed_order = result.get("validation_loader_order_sha256")
    _require(
        observed_order == expected_validation_loader_order_sha256
        or observed_order is None and legacy_order_attested,
        "direct_validation_order",
    )
    validation = result.get("validation")
    _require(isinstance(validation, Mapping), "direct_validation")
    return _validate_rows(
        validation.get("per_case_without_identifiers"), expected_case_count
    )


def extract_oracle_rows(
    result: Mapping[str, Any], rank: int, *, expected_case_count: int = 73,
    expected_validation_loader_order_sha256: str = VALIDATION_LOADER_ORDER_SHA256,
) -> list[dict[str, float]]:
    _require(
        result.get("schema_version")
        == "aurora.private.aneug_release_730_response_oracle_result.v1",
        "oracle_schema",
    )
    _require(
        result.get("protocol_id") == "aneug_release_730_response_oracle_v1",
        "oracle_protocol",
    )
    _require(result.get("status") == "complete", "oracle_status")
    _require(result.get("development_only") is True, "oracle_role")
    _require(result.get("case_ids_included") is False, "oracle_identifiers")
    _require(
        result.get("locked_test_field_case_count_read") == 0
        and result.get("processed_only_extra_field_case_count_read") == 0,
        "oracle_sealed",
    )
    _require(
        result.get("oracle_uses_true_validation_amplitude_and_coefficients") is True
        and result.get("learned_predictor") is False
        and result.get("rank_selected") is False
        and result.get("paper_performance_claim") is False,
        "oracle_interpretation",
    )
    _require(
        result.get("validation_loader_order_sha256")
        == expected_validation_loader_order_sha256,
        "oracle_validation_order",
    )
    _require(rank in RANK_GRID and tuple(result.get("rank_grid", ())) == RANK_GRID, "rank")
    evaluation = result.get("evaluation")
    _require(isinstance(evaluation, Mapping), "oracle_evaluation")
    by_rank = evaluation.get("per_case_without_identifiers_by_rank")
    _require(isinstance(by_rank, Mapping), "oracle_rows")
    return _validate_rows(by_rank.get(str(rank)), expected_case_count)


def _storage_aware_rank_pareto(
    means: Mapping[str, Mapping[str, float]], active_bytes: Mapping[str, int]
) -> list[str]:
    labels = tuple(means)
    _require(labels and set(labels) == set(active_bytes), "storage_labels")
    metrics = ("field_relative_l2", "tawss_normalized_absolute_error", "osi_mae")
    front: list[str] = []
    for label in labels:
        dominated = False
        for other in labels:
            if other == label:
                continue
            no_worse = all(means[other][metric] <= means[label][metric] for metric in metrics)
            no_worse = no_worse and active_bytes[other] <= active_bytes[label]
            strict = any(means[other][metric] < means[label][metric] for metric in metrics)
            strict = strict or active_bytes[other] < active_bytes[label]
            if no_worse and strict:
                dominated = True
                break
        if not dominated:
            front.append(label)
    return sorted(front, key=lambda value: int(value.split("_")[-1]))


def nominate_r1_candidate_ranks(storage_aware_front: Sequence[str]) -> list[int]:
    """Nominate a deterministic storage/performance span, not a final rank."""

    parsed: list[int] = []
    for label in storage_aware_front:
        _require(
            isinstance(label, str) and label.startswith("oracle_rank_"),
            "nomination_label",
        )
        suffix = label.removeprefix("oracle_rank_")
        _require(suffix.isdigit(), "nomination_label")
        rank = int(suffix)
        _require(rank in RANK_GRID, "nomination_rank")
        parsed.append(rank)
    _require(len(parsed) == len(set(parsed)), "nomination_duplicate")
    positive = sorted(rank for rank in parsed if rank > 0)
    if len(positive) <= 3:
        return positive
    indices = (0, (len(positive) - 1) // 2, len(positive) - 1)
    return [positive[index] for index in indices]


def compare_oracle_to_direct(
    direct_result: Mapping[str, Any],
    oracle_result: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    replicates: int | None = None,
    seed: int | None = None,
    legacy_direct_order_attested: bool = False,
) -> dict[str, Any]:
    validate_config(config)
    expected = int(config["split"]["validation_cases"])
    expected_order = config["split"]["validation_loader_order_sha256"]
    direct = extract_direct_rows(
        direct_result,
        expected_case_count=expected,
        expected_validation_loader_order_sha256=expected_order,
        legacy_order_attested=legacy_direct_order_attested,
    )
    oracle = {
        f"oracle_rank_{rank}": extract_oracle_rows(
            oracle_result,
            rank,
            expected_case_count=expected,
            expected_validation_loader_order_sha256=expected_order,
        )
        for rank in RANK_GRID
    }
    all_rows = {"direct_graph_unet": direct, **oracle}
    means = {label: metric_means(rows) for label, rows in all_rows.items()}
    if replicates is None:
        replicates = int(config["bootstrap"]["replicates"])
    if seed is None:
        seed = int(config["bootstrap"]["seed"])
    _require(replicates >= 100, "bootstrap_replicates")
    paired = {
        label: {
            metric: paired_bootstrap_delta(
                rows,
                direct,
                metric,
                replicates=replicates,
                seed=seed + rank_index * 10_007 + metric_index,
            )
            for metric_index, metric in enumerate(CORE_METRICS)
        }
        for rank_index, (label, rows) in enumerate(oracle.items(), start=1)
    }
    width = int(config["comparison"]["basis_width"])
    dtype_bytes = int(config["comparison"]["basis_dtype_bytes"])
    active_bytes = {
        f"oracle_rank_{rank}": (1 + rank) * width * dtype_bytes
        for rank in RANK_GRID
    }
    oracle_means = {label: means[label] for label in oracle}
    storage_front = _storage_aware_rank_pareto(oracle_means, active_bytes)
    nomination = nominate_r1_candidate_ranks(storage_front)
    return {
        "schema_version": "aurora.private.aneug_release_730_oracle_comparison_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "evidence_role": "validation_representation_ceiling_continuous_comparison",
        "method_means": means,
        "paired_oracle_minus_direct": paired,
        "metric_pareto_set": pareto_set(means),
        "active_basis_bytes_by_rank": active_bytes,
        "storage_aware_oracle_rank_pareto_set": storage_front,
        "r1_candidate_rank_nomination": nomination,
        "r1_candidate_nomination_rule": R1_NOMINATION_RULE,
        "r1_nomination_is_final_rank_selection": False,
        "automatic_rank_selection": None,
        "automatic_global_branch_decision": None,
        "absolute_performance_threshold": None,
        "oracle_is_learned_model_performance": False,
        "learned_response_validation_required": True,
        "paired_case_count": expected,
        "paired_unit": config["comparison"]["paired_unit"],
        "case_identifiers_included": False,
        "locked_test_or_extra_values_read": False,
        "population_inference": False,
        "paper_performance_claim": False,
    }


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "result_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--direct-result", type=Path, required=True)
    parser.add_argument("--oracle-result", type=Path, required=True)
    parser.add_argument("--direct-order-attestation", type=Path, required=True)
    parser.add_argument("--private-split-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    activation = validate_activation(args.activation, config, args.expected_commit)
    _require(
        file_sha256(args.direct_result) == activation["direct_result_sha256"],
        "direct_result_hash",
    )
    _require(
        file_sha256(args.oracle_result) == activation["oracle_result_sha256"],
        "oracle_result_hash",
    )
    _require(
        file_sha256(args.direct_order_attestation)
        == activation["direct_order_attestation_sha256"],
        "direct_order_attestation_hash",
    )
    validate_direct_order_attestation(args.direct_order_attestation, config, activation)
    validate_private_split_manifest(args.private_split_manifest, config, activation)
    direct = json.loads(args.direct_result.read_text(encoding="utf-8"))
    oracle = json.loads(args.oracle_result.read_text(encoding="utf-8"))
    output = compare_oracle_to_direct(
        direct, oracle, config, legacy_direct_order_attested=True
    )
    output.update(
        {
            "public_commit": args.expected_commit,
            "config_sha256": file_sha256(args.config),
            "activation_sha256": file_sha256(args.activation),
            "direct_result_sha256": activation["direct_result_sha256"],
            "oracle_result_sha256": activation["oracle_result_sha256"],
            "direct_order_attestation_sha256": activation[
                "direct_order_attestation_sha256"
            ],
            "validation_case_digest": config["split"]["validation_case_digest"],
            "validation_loader_order_sha256": config["split"][
                "validation_loader_order_sha256"
            ],
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "direct_terminal_record_sha256": activation[
                "direct_terminal_record_sha256"
            ],
            "oracle_terminal_record_sha256": activation[
                "oracle_terminal_record_sha256"
            ],
        }
    )
    _strict_atomic_json(args.output, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
