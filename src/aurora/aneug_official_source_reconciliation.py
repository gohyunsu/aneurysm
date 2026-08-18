"""Validate the primary-source reconciliation for the AneuG-Flow cohort."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class AneuGSourceReconciliationError(RuntimeError):
    pass


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise AneuGSourceReconciliationError(label)


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    _require(
        record.get("schema_version")
        == "aurora.aneug_official_source_reconciliation.v1",
        "schema_version",
    )
    sources = record["primary_sources"]
    paper = sources["final_neurips_2025_paper"]
    html = sources["neurips_proceedings_html"]
    card = sources["huggingface_dataset_card"]
    _require(
        (paper["transient_cases"], html["transient_cases"], card["transient_cases"])
        == (730, 200, 730),
        "reported_case_counts",
    )
    _require(
        (paper["real_shape_count_abstract"], paper["real_shape_count_table_1"])
        == (109, 116),
        "real_shape_conflict",
    )
    _require(html["conflicts_with_final_paper"] is True, "html_conflict")
    _require(card["processed_v5_explicitly_documented"] is False, "v5_card_claim")
    release = record["release_tree"]
    _require(
        (
            release["stable_case_directory_count"],
            release["complete_seven_asset_directory_count"],
            release["transient_file_count"],
        )
        == (730, 730, 5110),
        "release_tree",
    )
    reconciled = record["reconciliations"]
    _require(
        reconciled["canonical_transient_case_count"]["decision"] == 730,
        "canonical_count",
    )
    _require(
        reconciled["real_parent_cohort_count"]["decision"] is None
        and reconciled["real_parent_cohort_count"][
            "patient_or_parent_lineage_inference_allowed"
        ]
        is False,
        "parent_lineage",
    )
    artifact = reconciled["processed_artifact"]
    _require(
        (
            artifact["processed_v5_entry_count"],
            artifact["release_intersection_count"],
            artifact["processed_only_extra_count"],
        )
        == (809, 730, 79),
        "processed_cohort",
    )
    _require(artifact["all_809_equal_official_release"] is False, "extra_cases")
    normalization = reconciled["normalization"]
    _require(
        normalization["builder_uses_external_steady_tensor_norm"] is True
        and normalization["transient_output_embeds_tensor_norm"] is False
        and normalization["physical_wss_claim_ready"] is False,
        "normalization_provenance",
    )
    baseline = reconciled["official_ml_evaluation"]
    _require(
        baseline["task"] == "steady_wss_only"
        and baseline["best_reported_normalized_wss_relative_l2_percent"] == 4.67
        and baseline["valid_transient_full_cycle_baseline"] is False,
        "baseline_scope",
    )
    decision = record["adjudication"]
    _require(decision["canonical_730_release_composition_supported"] is True, "decision")
    _require(decision["physical_value_lineage_fully_verified"] is False, "lineage_pending")
    _require(decision["scientific_performance_verdict"] is None, "performance_claim")
    return record


def load_record(path: str | Path) -> dict[str, Any]:
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_record(record)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", required=True)
    arguments = parser.parse_args()
    load_record(arguments.record)


if __name__ == "__main__":
    main()
