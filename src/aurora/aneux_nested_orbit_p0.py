"""Validate the prospective AneuX nested-orbit P0 scientific contract.

This module deliberately does not access a dataset or a network.  The current
contract freezes the scientific question and falsifier while the exact private
asset path and manifest remain unresolved.  A separate execution envelope must
pin those two values before a CPU-only PBS job can be submitted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


class NestedOrbitP0Error(ValueError):
    """Raised when the prospective P0 boundary is changed."""


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise NestedOrbitP0Error(f"invalid config: {exc}") from exc
    if not isinstance(payload, dict):
        raise NestedOrbitP0Error("config root must be an object")
    validate_config(payload)
    return payload


def _all_false(mapping: Mapping[str, Any], keys: tuple[str, ...]) -> bool:
    return all(mapping.get(key) is False for key in keys)


def validate_config(config: Mapping[str, Any]) -> list[str]:
    """Validate the preregistered, not-yet-executable scientific contract."""

    if config.get("schema_version") != "aurora.aneux_nested_orbit_p0.v1":
        raise NestedOrbitP0Error("schema changed")
    if (
        config.get("experiment_id") != "aneux_nested_orbit_nontriviality_p0"
        or config.get("status")
        != "scientific_contract_preregistered_execution_envelope_pending_exact_private_path"
    ):
        raise NestedOrbitP0Error("registration state changed")

    relation = config.get("relationship_to_closed_p0", {})
    if (
        relation.get("closed_job_id") != "115177.ECE-util1"
        or relation.get("closed_result")
        != "execution_incomplete_zero_of_thirteen_scientific_checks"
        or relation.get("same_contract_rerun") is not False
        or relation.get("downloader_or_reader_repair") is not False
        or relation.get("network_access_allowed") is not False
        or relation.get("material_new_problem")
        != "factorized_resolution_nuisance_and_cut_context_nontriviality_on_an_existing_private_holding"
    ):
        raise NestedOrbitP0Error("closed P0 isolation changed")

    source = config.get("source", {})
    if (
        source.get("dataset") != "AneuX"
        or source.get("version") != "v1.0"
        or source.get("source_reported_lesions") != 750
        or source.get("source_reported_patients") != 605
        or source.get("mesh_resolutions")
        != ["original", "area-001", "area-005"]
        or source.get("cut_types") != ["dome", "ninja", "cut1", "cut2"]
        or source.get("expected_tabular_archive", {}).get("md5")
        != "a00dde7b974de724c6480dbda4585a8c"
        or source.get("expected_model_archive", {}).get("md5")
        != "6248323006f67858b1eb1ec77ce8c0a6"
    ):
        raise NestedOrbitP0Error("source contract changed")

    admission = config.get("admission", {})
    scores = admission.get("axis_scores")
    if (
        scores != [4.0, 4.5, 3.0, 4.0, 4.0, 5.0, 4.5, 4.0]
        or sum(scores or []) != 33.0
        or admission.get("score") != 33.0
        or admission.get("threshold") != 32.0
        or admission.get("critical_axis_pass") is not True
        or admission.get("authorizes_only")
        != "method_free_cpu_p0_registration_pending_exact_private_path"
    ):
        raise NestedOrbitP0Error("admission boundary changed")

    estimand = config.get("estimand", {})
    if (
        estimand.get("target")
        != "cross_sectional_rupture_status_association_not_future_risk"
        or estimand.get("independent_unit") != "patient"
        or estimand.get("resolution_role") != "nuisance_within_fixed_cut"
        or estimand.get("cut_role")
        != "information_set_change_with_permitted_parent_vessel_context_residual"
        or "prospective_rupture_risk" not in estimand.get("prohibited_labels", [])
        or "clinical_utility" not in estimand.get("prohibited_labels", [])
    ):
        raise NestedOrbitP0Error("estimand boundary changed")

    data = config.get("data_boundary", {})
    if (
        data.get("private_holding_only") is not True
        or data.get("public_payload_write") is not False
        or data.get("case_identifier_write") is not False
        or data.get("external_source_labels_or_surfaces_opened") is not False
        or data.get("exact_dataset_root") is not None
        or data.get("exact_manifest_sha256") is not None
        or data.get("execution_envelope_can_be_frozen_only_after_bounded_read_only_inventory")
        is not True
        or data.get("multi_lesion_patient_split_action")
        != "keep_all_lesions_in_one_split"
    ):
        raise NestedOrbitP0Error("private asset boundary changed")

    development = config.get("development_scope", {})
    if (
        development.get("allowed_sources") != ["hug2016", "hug2016snf"]
        or development.get("locked_external_sources") != ["aneurist", "aneurisk"]
        or development.get("external_source_payload_access_in_p0") is not False
        or development.get("bootstrap_unit") != "patient"
        or development.get("bootstrap_replicates") != 2000
    ):
        raise NestedOrbitP0Error("development/outer-source boundary changed")

    criteria = config.get("checks", {}).get("nontriviality_two_of_three_required")
    expected_criteria = [
        (
            "fixed_cut_resolution_decision_flip_fraction",
            "patient_bootstrap_95pct_lower_bound_gt_0_05",
        ),
        (
            "fraction_with_fixed_cut_resolution_logit_range_gt_0_20",
            "patient_bootstrap_95pct_lower_bound_gt_0_10",
        ),
        (
            "orbit_disagreement_to_baseline_error_spearman",
            "patient_bootstrap_95pct_lower_bound_gt_0_20",
        ),
    ]
    observed_criteria = [
        (row.get("endpoint"), row.get("criterion")) for row in criteria or []
    ]
    if observed_criteria != expected_criteria:
        raise NestedOrbitP0Error("nontriviality falsifier changed")

    execution = config.get("execution", {})
    if (
        execution.get("server") != "introai9"
        or execution.get("scheduler") != "pbs"
        or execution.get("resources") != "select=1:ncpus=4:mem=16gb:ngpus=0"
        or execution.get("gpu_requested") is not False
        or execution.get("login_node_gpu_command") is not False
        or execution.get("network_access") is not False
        or execution.get("excluded_server") != "junjinyong"
        or execution.get("job_submitted") is not False
        or execution.get("scheduler_queried") is not False
    ):
        raise NestedOrbitP0Error("execution boundary changed")

    state = config.get("scientific_state", {})
    if state.get("conditional_source_lead") is not True or not _all_false(
        state,
        (
            "primary_problem_selected",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "paper_claim_active",
        ),
    ):
        raise NestedOrbitP0Error("scientific state overclaimed")

    return [
        "closed P0 isolation",
        "factorized estimand",
        "patient/source split boundary",
        "three-part nontriviality falsifier",
        "introai9 CPU-only pending-execution boundary",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    checks = validate_config(load_config(args.config))
    print(json.dumps({"status": "valid", "checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
