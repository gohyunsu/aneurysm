"""Validate the machine-readable AURORA research contract.

This module intentionally uses only Python's standard library so the protocol
can be checked before a GPU environment or medical dataset is available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class ProtocolError(ValueError):
    """Raised when a research protocol violates a project invariant."""


ALLOWED_PRIMARY_PROBLEMS = {
    "protocol_indexed_posterior_prediction_under_intracranial_4d_flow_acquisition_shift"
}
ALLOWED_ENDPOINTS = {"held_out_same_flow_acquisition_prediction"}
ALLOWED_PROVENANCE = {
    "analytical_pde",
    "in_vitro_measurement",
    "real_cfd",
    "synthetic_cfd",
    "surrogate",
    "none",
}
ALLOWED_SPLIT_UNITS = {
    "patient",
    "geometry",
    "generator_seed_geometry",
    "simulation_family",
    "aneux_base_family",
    "physical_phantom",
}
REQUIRED_GATES = {"G0", "G1", "G2", "G3", "G4"}
REQUIRED_DATASETS = {
    "controlled_pde",
    "nonlinear_pde",
    "aneumo",
    "aneug_flow",
    "benchanxplore",
    "cmha",
    "aneux",
}


def load_protocol(path: str | Path) -> dict[str, Any]:
    """Load a protocol JSON file and validate its top-level representation."""

    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProtocolError(f"Protocol does not exist: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Invalid JSON in {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProtocolError("Protocol root must be a JSON object.")
    return payload


def _require_keys(
    mapping: Mapping[str, Any], keys: Sequence[str], context: str
) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ProtocolError(f"{context} is missing: {', '.join(missing)}")


def _unique_ids(items: Sequence[Mapping[str, Any]], key: str, context: str) -> set[str]:
    values = [str(item.get(key, "")) for item in items]
    if "" in values:
        raise ProtocolError(f"{context} contains an empty {key}.")
    if len(values) != len(set(values)):
        raise ProtocolError(f"{context} contains duplicate {key} values.")
    return set(values)


def validate_protocol(protocol: Mapping[str, Any]) -> list[str]:
    """Return human-readable checks or raise :class:`ProtocolError`.

    The validator focuses on invariants that prevent target inflation,
    provenance loss, and split leakage. It does not judge whether a future
    experiment passed a scientific gate.
    """

    _require_keys(
        protocol,
        [
            "schema_version",
            "project",
            "venue",
            "task",
            "datasets",
            "model",
            "loss",
            "gates",
            "post_result_diagnostics",
            "prospective_reentry_protocols",
            "nonlinear_protocols",
            "evaluation",
            "phases",
        ],
        "protocol",
    )
    checks: list[str] = []

    project = protocol["project"]
    _require_keys(project, ["name", "status", "clinical_use"], "project")
    if project["name"] != "AURORA":
        raise ProtocolError("Project name must remain AURORA for schema v1.")
    if project["clinical_use"] is not False:
        raise ProtocolError("AURORA v1 must be marked research-only.")
    checks.append("research-only project boundary")

    venue = protocol["venue"]
    _require_keys(
        venue,
        [
            "target",
            "submission_deadline",
            "review",
            "technical_page_limit",
            "fifth_page_allowed_content",
            "submission_ready",
            "required_headline_domain",
            "development_cache_is_confirmatory",
            "m0_alone_may_authorize_submission",
            "v0_task_audit_config",
            "v0_status",
            "v0_result",
            "v0_pass_authorizes",
            "v1_backbone_config",
            "v1_status",
            "v1_result",
            "v1_result_sha256",
            "v1_gate",
            "v1_failure_action",
            "v1a_attribution_config",
            "v1a_status",
            "v1a_result",
            "v1a_result_sha256",
            "v1a_primary_observation",
            "v1a_next_action",
            "v1b_boundary_asset_config",
            "v1b_config_sha256",
            "v1b_status",
            "v1b_result",
            "v1b_result_sha256",
            "v1b_gate",
            "v1b_discovery_scope",
            "v1b_pass_authorizes",
            "v1c_boundary_geometry_config",
            "v1c_config_sha256",
            "v1c_status",
            "v1c_result",
            "v1c_result_sha256",
            "v1c_gate",
            "v1c_pass_authorizes",
            "v1d_development_geometry_config",
            "v1d_config_sha256",
            "v1d_status",
            "v1d_result",
            "v1d_result_sha256",
            "v1d_gate",
            "v1d_pass_authorizes",
            "v1e_known_condition_config",
            "v1e_config_sha256",
            "v1e_status",
            "v1e_result",
            "v1e_result_sha256",
            "v1e_gate",
            "v1e_failure_action",
            "v1e_pass_authorizes",
            "v1_test_access",
            "plan",
        ],
        "venue",
    )
    if venue["target"] != "IEEE_ISBI_2027_four_page_regular":
        raise ProtocolError("The locked target is the ISBI 2027 four-page paper.")
    if venue["submission_deadline"] != "2026-10-26T23:59:00-04:00":
        raise ProtocolError("The ISBI 2027 official EDT deadline changed.")
    if venue["review"] != "single_blind" or venue["technical_page_limit"] != 4:
        raise ProtocolError("ISBI review mode and four-page technical limit are fixed.")
    if set(venue["fifth_page_allowed_content"]) != {
        "references",
        "compliance_with_ethical_standards",
        "acknowledgments_and_conflict_of_interest",
    }:
        raise ProtocolError("ISBI fifth-page content must remain non-technical.")
    if (
        venue["submission_ready"] is not False
        or venue["required_headline_domain"] != "irregular_3d_aneurysm_velocity"
        or venue["development_cache_is_confirmatory"] is not False
        or venue["m0_alone_may_authorize_submission"] is not False
        or venue["v0_task_audit_config"] != "configs/aneumo_isbi_v0.json"
        or venue["v0_status"] != "completed_passed_development_only"
        or venue["v0_result"] != "results/aneumo_isbi_v0_20260808.json"
        or venue["v0_pass_authorizes"]
        != "v1_64_case_implementation_smoke_only"
        or venue["v1_backbone_config"] != "configs/aneumo_isbi_v1.json"
        or venue["v1_status"]
        != "completed_failed_development_only"
        or venue["v1_result"] != "results/aneumo_isbi_v1_20260808.json"
        or venue["v1_result_sha256"]
        != "f67970c4d8028bf869ae793a776ed86d32b9cc477a9ba414e54bf9c8fab6a9b1"
        or venue["v1_gate"] != "5_of_7_passed"
        or venue["v1_failure_action"]
        != "stop_the_current_3d_backbone_branch_without_local_hyperparameter_repair"
        or venue["v1a_attribution_config"]
        != "configs/aneumo_isbi_v1_attribution.json"
        or venue["v1a_status"]
        != "completed_threshold_free_diagnostic_no_reentry"
        or venue["v1a_result"]
        != "results/aneumo_isbi_v1_attribution_20260808.json"
        or venue["v1a_result_sha256"]
        != "1a7b3e768e97b560da54d52cfe343c019d392e5af2fb3bbf518705f3728076a2"
        or venue["v1a_primary_observation"]
        != "high_training_error_and_prediction_collapse_across_all_four_families_not_only_geometry_disjoint_generalization"
        or venue["v1a_next_action"]
        != "audit_a_new_task_or_data_identity_before_any_new_method_without_reopening_v1_or_v2"
        or venue["v1b_boundary_asset_config"]
        != "configs/aneumo_isbi_v1b_boundary_asset_audit.json"
        or venue["v1b_config_sha256"]
        != "78918c629c9a738ae7aced3b4e36a99cc10aba7279c9d70044e46182c52e6b26"
        or venue["v1b_status"]
        != "completed_passed_asset_identifiability_only"
        or venue["v1b_result"]
        != "results/aneumo_isbi_v1b_boundary_asset_audit_20260808.json"
        or venue["v1b_result_sha256"]
        != "8cc4871f8d8b234c7c3f3cb3763e5cc959b5653e26349497eb55d2e17b54d901"
        or venue["v1b_gate"] != "8_of_8_passed"
        or venue["v1b_discovery_scope"]
        != "archive_1_central_directory_and_case_1_reference_flow_vtp_headers_not_prospective_evidence"
        or venue["v1b_pass_authorizes"]
        != "register_a_new_boundary_aware_cache_staging_audit_only"
        or venue["v1c_boundary_geometry_config"]
        != "configs/aneumo_isbi_v1c_boundary_geometry_staging_audit.json"
        or venue["v1c_config_sha256"]
        != "cccef81c9b948d24ea67c1164f3dec394e9d7695fb336219e6e7eb57bb7925be"
        or venue["v1c_status"]
        != "completed_passed_geometry_staging_adequacy_only"
        or venue["v1c_result"]
        != "results/aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json"
        or venue["v1c_result_sha256"]
        != "a023e9fbcbcbc1fc719c8a902a582dee031cf3e08d360d28a741f5530aa2bbd1"
        or venue["v1c_gate"] != "8_of_8_passed"
        or venue["v1c_pass_authorizes"]
        != "register_full_boundary_aware_geometry_cache_staging_protocol_only"
        or venue["v1d_development_geometry_config"]
        != "configs/aneumo_isbi_v1d_development_geometry_cache.json"
        or venue["v1d_config_sha256"]
        != "5b843de7dd7ed1250bdfa93b41e7817645e330b31d3020c994e208ff8295fd9b"
        or venue["v1d_status"]
        != "completed_passed_development_geometry_adequacy_only"
        or venue["v1d_result"]
        != "results/aneumo_isbi_v1d_development_geometry_cache_20260808.json"
        or venue["v1d_result_sha256"]
        != "051a722cb96ca1adb4f7eb4997d9f4dc96f5c84c04fb295e4aa489be7ff1b0db"
        or venue["v1d_gate"] != "9_of_9_passed"
        or venue["v1d_pass_authorizes"]
        != "register_boundary_aware_known_condition_baseline_protocol_only"
        or venue["v1e_known_condition_config"]
        != "configs/aneumo_isbi_v1e_known_condition_baseline.json"
        or venue["v1e_config_sha256"]
        != "e21414f467b3f6dc0ac6d8a0086ed04cf2873f66f890239c033c77d464e4ae19"
        or venue["v1e_status"]
        != "completed_failed_development_known_condition_qualification"
        or venue["v1e_result"]
        != "results/aneumo_isbi_v1e_known_condition_baseline_20260808.json"
        or venue["v1e_result_sha256"]
        != "63fdb3a6fbddb15bb8d6cb82fde7b6880e3b3c7badef46b7a4cc2da4d31f2c0e"
        or venue["v1e_gate"] != "6_of_9_passed"
        or venue["v1e_failure_action"]
        != "stop_the_current_aneumo_3d_learning_line_without_local_architecture_loss_step_seed_or_threshold_repair"
        or venue["v1e_pass_authorizes"]
        != "register_boundary_aware_scalar_missing_inflow_development_protocol_only"
        or venue["v1_test_access"] is not False
        or venue["plan"] != "docs/isbi-2027-plan.md"
    ):
        raise ProtocolError(
            "ISBI submission must remain blocked before independent 3D evidence."
        )
    checks.append("ISBI 2027 four-page and 3D evidence boundary")

    task = protocol["task"]
    _require_keys(
        task,
        [
            "primary_problem",
            "application_endpoint",
            "primary_metric",
            "historical_primary_problem",
            "historical_application_endpoint",
            "historical_primary_metric",
            "historical_primary_status",
            "active_candidate_problem",
            "active_candidate_status",
            "candidate_primary_estimand",
            "candidate_secondary_estimand",
            "i0a_config",
            "i0a_config_sha256",
            "i0a_pass_authorizes",
            "generic_super_resolution_or_denoising_is_novel",
            "cfd_field_is_clinical_mri_ground_truth",
            "forbidden_claims",
        ],
        "task",
    )
    if task["primary_problem"] not in ALLOWED_PRIMARY_PROBLEMS:
        raise ProtocolError(
            "The active primary task must remain protocol-indexed 4D-flow "
            "posterior prediction for schema v2."
        )
    if task["application_endpoint"] not in ALLOWED_ENDPOINTS:
        raise ProtocolError(
            "Only held-out same-flow acquisition prediction is active; prospective "
            "risk or rupture-status relabeling requires a separate protocol."
        )
    forbidden = set(task["forbidden_claims"])
    if "prospective_rupture_risk" not in forbidden or "clinical_utility" not in forbidden:
        raise ProtocolError("Task must forbid prospective-risk and clinical-utility claims.")
    if "causal_intervention_effect" not in forbidden:
        raise ProtocolError("Paired simulator responses must not be called causal effects.")
    if (
        task["primary_metric"] != "held_out_measurement_energy_score"
        or task["historical_primary_problem"]
        != "operator_learning_under_partial_boundary_observation"
        or task["historical_application_endpoint"] != "cross_sectional_rupture_status"
        or task["historical_primary_metric"] != "functional_energy_score"
        or task["historical_primary_status"]
        != "unsupported_after_n1c_and_inactive_after_m0_execution_incomplete"
        or task["active_candidate_problem"]
        != "protocol_indexed_posterior_prediction_under_intracranial_4d_flow_acquisition_shift"
        or task["active_candidate_status"]
        != "i0a_post_discovery_asset_audit_registered_no_method_selected"
        or task["candidate_primary_estimand"]
        != "held_out_same_flow_acquisition_predictive_distribution_in_measurement_space"
        or task["candidate_secondary_estimand"]
        != "aneurysm_localized_velocity_functional_calibration"
        or task["i0a_config"] != "configs/flow_mri_protocol_i0a_asset_audit.json"
        or task["i0a_config_sha256"]
        != "ceb6413047b117ecbc7b52d83919b73117491e8de6c099c7b158f592788f40ff"
        or task["i0a_pass_authorizes"]
        != "register_selective_private_staging_and_method_free_I0b_task_adequacy_only"
        or task["generic_super_resolution_or_denoising_is_novel"] is not False
        or task["cfd_field_is_clinical_mri_ground_truth"] is not False
    ):
        raise ProtocolError(
            "The 4D-flow candidate must remain asset-only, measurement-space, "
            "and method-unselected before I0b."
        )
    checks.append("historical task boundary and 4D-flow candidate guardrails")

    datasets = protocol["datasets"]
    if not isinstance(datasets, list) or not datasets:
        raise ProtocolError("datasets must be a non-empty list.")
    dataset_names = _unique_ids(datasets, "name", "datasets")
    missing_datasets = REQUIRED_DATASETS - dataset_names
    if missing_datasets:
        raise ProtocolError(
            f"Required dataset roles are absent: {', '.join(sorted(missing_datasets))}"
        )
    for dataset in datasets:
        _require_keys(
            dataset, ["name", "role", "field_provenance", "split_unit"],
            f"dataset {dataset.get('name', '?')}",
        )
        if dataset["field_provenance"] not in ALLOWED_PROVENANCE:
            raise ProtocolError(
                f"Unsupported provenance for {dataset['name']}: "
                f"{dataset['field_provenance']}"
            )
        if dataset["split_unit"] not in ALLOWED_SPLIT_UNITS:
            raise ProtocolError(
                f"Unsupported split unit for {dataset['name']}: {dataset['split_unit']}"
            )
    cmha = next(item for item in datasets if item["name"] == "cmha")
    aneux = next(item for item in datasets if item["name"] == "aneux")
    aneumo = next(item for item in datasets if item["name"] == "aneumo")
    if cmha["field_provenance"] != "real_cfd":
        raise ProtocolError("CMHA is the declared real-CFD bridge in protocol v1.")
    if aneux["field_provenance"] != "none":
        raise ProtocolError("AneuX must not be declared as real-CFD data.")
    if aneumo["split_unit"] != "aneux_base_family":
        raise ProtocolError(
            "Aneumo split must keep both deformations of an AneuX base family "
            "in one fold."
        )
    if aneumo.get("pressure_head_status") != (
        "excluded_after_train_only_scaling_audit"
    ):
        raise ProtocolError(
            "Aneumo pressure must remain excluded after the scaling audit."
        )
    checks.append("dataset provenance and split units")

    model = protocol["model"]
    numeric_model_keys = [
        "surface_queries", "volume_queries", "knn", "latent_tokens", "hidden_dim",
        "attention_layers", "attention_heads", "bc_basis_dim",
        "bc_mixture_components", "bc_covariance_rank", "bc_samples_train",
        "bc_samples_eval", "ensemble_members", "physics_collocation_points",
    ]
    _require_keys(
        model,
        [
            *numeric_model_keys,
            "observation_modes",
            "temporal_representation",
            "irregular_3d_output_contract",
        ],
        "model",
    )
    for key in numeric_model_keys:
        if not isinstance(model[key], int) or model[key] <= 0:
            raise ProtocolError(f"model.{key} must be a positive integer.")
    if model["hidden_dim"] % model["attention_heads"] != 0:
        raise ProtocolError("hidden_dim must be divisible by attention_heads.")
    if model["bc_samples_eval"] < model["bc_samples_train"]:
        raise ProtocolError("Evaluation must use at least as many BC samples as training.")
    if set(model["observation_modes"]) != {"full", "partial", "missing"}:
        raise ProtocolError("Model must support full, partial, and missing BC modes.")
    temporal = model["temporal_representation"]
    _require_keys(
        temporal,
        [
            "status",
            "fixed_fourier",
            "candidate_bases",
            "rejected_bases",
            "coefficient_budgets",
            "selection_metric",
            "leakage_rule",
        ],
        "model.temporal_representation",
    )
    if temporal["fixed_fourier"] != "rejected_by_frozen_d0":
        raise ProtocolError("Frozen D0 requires fixed Fourier to remain rejected.")
    if temporal["candidate_bases"] != ["train_only_pod"]:
        raise ProtocolError("Only train-only POD remains representation-eligible.")
    if temporal["rejected_bases"] != ["dct_ii"]:
        raise ProtocolError("DCT-II must remain rejected after D0b.")
    if temporal["coefficient_budgets"] != [17, 25]:
        raise ProtocolError("D0b must compare the frozen equal budgets 17 and 25.")
    if temporal["leakage_rule"] != "pod_fit_on_training_geometries_only":
        raise ProtocolError("Temporal POD must be fit on training geometries only.")
    irregular_3d = model["irregular_3d_output_contract"]
    _require_keys(
        irregular_3d,
        [
            "aneumo_current_candidate_channels",
            "excluded_headline_channels",
            "mandatory_baselines",
            "protocol_registration_condition",
            "headline_activation_condition",
            "v1_config",
            "v1_status",
            "v1_result",
            "v1_gate",
            "v1_failure_action",
            "v1a_attribution_config",
            "v1a_status",
            "v1a_result",
            "v1a_result_sha256",
            "v1a_primary_observation",
            "post_v1a_action",
            "v1b_boundary_asset_config",
            "v1b_status",
            "v1b_result",
            "v1b_result_sha256",
            "v1b_gate",
            "v1b_pass_authorizes",
            "v1c_boundary_geometry_config",
            "v1c_config_sha256",
            "v1c_status",
            "v1c_result",
            "v1c_result_sha256",
            "v1c_gate",
            "v1c_pass_authorizes",
            "v1d_development_geometry_config",
            "v1d_config_sha256",
            "v1d_status",
            "v1d_result",
            "v1d_result_sha256",
            "v1d_gate",
            "v1d_pass_authorizes",
            "v1e_known_condition_config",
            "v1e_config_sha256",
            "v1e_status",
            "v1e_result",
            "v1e_result_sha256",
            "v1e_gate",
            "v1e_failure_action",
            "v1e_pass_authorizes",
            "v1_ensemble_estimand",
            "v1_aggregate_integrity",
            "v1_response_oracle_role",
            "v1_test_access",
            "headline_authorized",
        ],
        "model.irregular_3d_output_contract",
    )
    if irregular_3d["aneumo_current_candidate_channels"] != ["velocity"]:
        raise ProtocolError(
            "The Aneumo candidate must remain velocity-only after the scaling audit."
        )
    if "pressure" not in irregular_3d["excluded_headline_channels"]:
        raise ProtocolError("Aneumo pressure must not return as a headline output.")
    if set(irregular_3d["mandatory_baselines"]) != {
        "same_case_anchor_train_tuned_global_power_response_control",
        "q_pointnet",
        "knn_mgn",
        "deltaphi_graph",
        "three_seed_deep_ensemble",
    }:
        raise ProtocolError("The registered V1 physical and learned baselines are mandatory.")
    if irregular_3d["protocol_registration_condition"] != (
        "g1s_completed_and_isbi_v0_passed"
    ):
        raise ProtocolError(
            "Aneumo V1 registration must remain linked to G1s and the ISBI V0 pass."
        )
    if (
        irregular_3d["headline_activation_condition"]
        != "positive_m0_then_expanded_or_independent_v2_outer_test_passed"
        or irregular_3d["v1_config"] != "configs/aneumo_isbi_v1.json"
        or irregular_3d["v1_status"]
        != "completed_failed_development_only"
        or irregular_3d["v1_result"] != "results/aneumo_isbi_v1_20260808.json"
        or irregular_3d["v1_gate"] != "5_of_7_passed"
        or irregular_3d["v1_failure_action"]
        != "stop_the_current_3d_backbone_branch_without_local_hyperparameter_repair"
        or irregular_3d["v1a_attribution_config"]
        != "configs/aneumo_isbi_v1_attribution.json"
        or irregular_3d["v1a_status"]
        != "completed_threshold_free_diagnostic_no_reentry"
        or irregular_3d["v1a_result"]
        != "results/aneumo_isbi_v1_attribution_20260808.json"
        or irregular_3d["v1a_result_sha256"]
        != "1a7b3e768e97b560da54d52cfe343c019d392e5af2fb3bbf518705f3728076a2"
        or irregular_3d["v1a_primary_observation"]
        != "high_training_error_and_low_prediction_magnitude_or_alignment_across_all_four_families"
        or irregular_3d["post_v1a_action"]
        != "audit_a_new_task_or_data_identity_before_any_new_method_without_v1_repair_or_v2_access"
        or irregular_3d["v1b_boundary_asset_config"]
        != "configs/aneumo_isbi_v1b_boundary_asset_audit.json"
        or irregular_3d["v1b_status"]
        != "completed_passed_asset_identifiability_only"
        or irregular_3d["v1b_result"]
        != "results/aneumo_isbi_v1b_boundary_asset_audit_20260808.json"
        or irregular_3d["v1b_result_sha256"]
        != "8cc4871f8d8b234c7c3f3cb3763e5cc959b5653e26349497eb55d2e17b54d901"
        or irregular_3d["v1b_gate"] != "8_of_8_passed"
        or irregular_3d["v1b_pass_authorizes"]
        != "register_a_new_boundary_aware_cache_staging_audit_only"
        or irregular_3d["v1c_boundary_geometry_config"]
        != "configs/aneumo_isbi_v1c_boundary_geometry_staging_audit.json"
        or irregular_3d["v1c_config_sha256"]
        != "cccef81c9b948d24ea67c1164f3dec394e9d7695fb336219e6e7eb57bb7925be"
        or irregular_3d["v1c_status"]
        != "completed_passed_geometry_staging_adequacy_only"
        or irregular_3d["v1c_result"]
        != "results/aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json"
        or irregular_3d["v1c_result_sha256"]
        != "a023e9fbcbcbc1fc719c8a902a582dee031cf3e08d360d28a741f5530aa2bbd1"
        or irregular_3d["v1c_gate"] != "8_of_8_passed"
        or irregular_3d["v1c_pass_authorizes"]
        != "register_full_boundary_aware_geometry_cache_staging_protocol_only"
        or irregular_3d["v1d_development_geometry_config"]
        != "configs/aneumo_isbi_v1d_development_geometry_cache.json"
        or irregular_3d["v1d_config_sha256"]
        != "5b843de7dd7ed1250bdfa93b41e7817645e330b31d3020c994e208ff8295fd9b"
        or irregular_3d["v1d_status"]
        != "completed_passed_development_geometry_adequacy_only"
        or irregular_3d["v1d_result"]
        != "results/aneumo_isbi_v1d_development_geometry_cache_20260808.json"
        or irregular_3d["v1d_result_sha256"]
        != "051a722cb96ca1adb4f7eb4997d9f4dc96f5c84c04fb295e4aa489be7ff1b0db"
        or irregular_3d["v1d_gate"] != "9_of_9_passed"
        or irregular_3d["v1d_pass_authorizes"]
        != "register_boundary_aware_known_condition_baseline_protocol_only"
        or irregular_3d["v1e_known_condition_config"]
        != "configs/aneumo_isbi_v1e_known_condition_baseline.json"
        or irregular_3d["v1e_config_sha256"]
        != "e21414f467b3f6dc0ac6d8a0086ed04cf2873f66f890239c033c77d464e4ae19"
        or irregular_3d["v1e_status"]
        != "completed_failed_development_known_condition_qualification"
        or irregular_3d["v1e_result"]
        != "results/aneumo_isbi_v1e_known_condition_baseline_20260808.json"
        or irregular_3d["v1e_result_sha256"]
        != "63fdb3a6fbddb15bb8d6cb82fde7b6880e3b3c7badef46b7a4cc2da4d31f2c0e"
        or irregular_3d["v1e_gate"] != "6_of_9_passed"
        or irregular_3d["v1e_failure_action"]
        != "stop_the_current_aneumo_3d_learning_line_without_local_architecture_loss_step_seed_or_threshold_repair"
        or irregular_3d["v1e_pass_authorizes"]
        != "register_boundary_aware_scalar_missing_inflow_development_protocol_only"
        or irregular_3d["v1_ensemble_estimand"]
        != "matching_q_three_seed_mean_and_seed_by_eight_q_twenty_four_component_missing_mixture"
        or irregular_3d["v1_aggregate_integrity"]
        != "exact_four_by_three_manifest_plus_validation_checkpoint_replay_absolute_tolerance_1e-5"
        or irregular_3d["v1_response_oracle_role"]
        != "true_validation_anchor_response_only_report_never_selector_or_gate"
        or irregular_3d["v1_test_access"] is not False
        or irregular_3d["headline_authorized"] is not False
    ):
        raise ProtocolError(
            "Irregular-3D headline requires positive M0 and independent V2 evidence."
        )
    checks.append("model dimensional contract")

    loss = protocol["loss"]
    loss_keys = [
        "full_field",
        "paired_response",
        "paired_response_ablation_weight",
        "boundary_nll",
        "physics",
        "functional",
    ]
    _require_keys(loss, loss_keys, "loss")
    if any(not isinstance(loss[key], (int, float)) or loss[key] < 0 for key in loss_keys):
        raise ProtocolError("All loss weights must be non-negative numbers.")
    if loss["full_field"] <= 0:
        raise ProtocolError("The full-field objective cannot be disabled.")
    if loss["paired_response"] != 0:
        raise ProtocolError(
            "paired-response must remain disabled in the headline objective after N1c."
        )
    if loss["paired_response_ablation_weight"] <= 0:
        raise ProtocolError(
            "A positive paired-response weight must remain available for the named ablation."
        )
    checks.append("full-field objective and paired-response ablation boundary")

    gates = protocol["gates"]
    gate_ids = _unique_ids(gates, "id", "gates")
    if gate_ids != REQUIRED_GATES:
        raise ProtocolError(
            "Gate set must be exactly G0–G4; change schema version to alter it."
        )
    g1 = next(item for item in gates if item["id"] == "G1")
    if "maximum_projective_consistency_error" not in g1:
        raise ProtocolError("G1 must preregister a projective-consistency threshold.")
    g4 = next(item for item in gates if item["id"] == "G4")
    required_domains = {"controlled_pde", "nonlinear_pde", "irregular_3d"}
    if int(g4.get("minimum_domains", 0)) < 3:
        raise ProtocolError("G4 must require evidence in at least three domains.")
    if set(g4.get("required_domains", [])) != required_domains:
        raise ProtocolError("G4 must retain controlled, nonlinear, and irregular-3D tests.")
    g3 = next(item for item in gates if item["id"] == "G3")
    if g3.get("same_benchmark_learned_comparison") != (
        "exploratory_after_architecture_discovery"
    ):
        raise ProtocolError("Same-benchmark learned temporal comparison is exploratory.")
    if g3.get("confirmatory_requires_fresh_transient_cases") is not True:
        raise ProtocolError("Confirmatory G3 requires fresh transient cases.")
    checks.append("coherence and cross-domain blocking gates")

    diagnostics = protocol["post_result_diagnostics"]
    diagnostic_ids = _unique_ids(diagnostics, "id", "post_result_diagnostics")
    if diagnostic_ids != {"G1b", "DA1", "DA2", "D0b"}:
        raise ProtocolError(
            "Schema v2 must retain G1b, DA1, DA2, and D0b diagnostics."
        )
    g1b = next(item for item in diagnostics if item["id"] == "G1b")
    _require_keys(
        g1b,
        [
            "status",
            "source_gate",
            "may_reopen_or_relabel_source_gate",
            "questions",
            "sample_counts",
        ],
        "G1b diagnostic",
    )
    if g1b["source_gate"] != "G1":
        raise ProtocolError("G1b must remain attributed to the failed G1 gate.")
    if g1b["may_reopen_or_relabel_source_gate"] is not False:
        raise ProtocolError("A post-result diagnostic cannot reopen or relabel G1.")
    if g1b["sample_counts"] != [128, 512, 2048]:
        raise ProtocolError("G1b sample counts are frozen at 128, 512, and 2048.")
    da1 = next(item for item in diagnostics if item["id"] == "DA1")
    _require_keys(
        da1,
        [
            "status",
            "source_gate",
            "may_reopen_or_relabel_source_gate",
            "may_define_new_gate",
            "config",
            "diagnostic_seeds",
            "success_thresholds",
            "questions",
            "matched_boundary_record_cells",
        ],
        "DA1 density attribution",
    )
    if da1["status"] not in {
        "preregistered_post_result_unrun",
        "completed_post_result_exploratory",
    }:
        raise ProtocolError("DA1 must retain a registered or exploratory status.")
    if da1["source_gate"] != "G1r":
        raise ProtocolError("DA1 must remain attributed to failed G1r.")
    if (
        da1["may_reopen_or_relabel_source_gate"] is not False
        or da1["may_define_new_gate"] is not False
    ):
        raise ProtocolError("DA1 cannot relabel a failure or define a new gate.")
    if da1["config"] != "configs/controlled_pde_density_attribution.json":
        raise ProtocolError("DA1 must point to its executable frozen config.")
    if da1["diagnostic_seeds"] != 3 or da1["success_thresholds"] is not None:
        raise ProtocolError("DA1 requires three diagnostic seeds and no threshold.")
    if da1["matched_boundary_record_cells"] != [
        "192x32",
        "768x8",
        "3072x2",
    ]:
        raise ProtocolError("DA1 matched-budget cells changed.")
    if da1["status"] == "completed_post_result_exploratory":
        _require_keys(
            da1,
            [
                "result",
                "source_commit",
                "maximum_population_objective_density_error",
                "maximum_empirical_population_selected_density_error",
                "maximum_empirical_sampled_selected_density_error",
                "attribution",
                "nonlinear_or_3d_confirmatory_training_authorized",
            ],
            "completed DA1",
        )
        if da1["result"] != (
            "results/controlled_pde_density_attribution_20260803.json"
        ):
            raise ProtocolError("Completed DA1 must retain its public aggregate.")
        if len(da1["source_commit"]) != 40:
            raise ProtocolError("Completed DA1 must retain its exact source commit.")
        if da1["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
            raise ProtocolError(
                "Exploratory DA1 cannot authorize nonlinear or 3D confirmation."
            )
    da2 = next(item for item in diagnostics if item["id"] == "DA2")
    _require_keys(
        da2,
        [
            "status",
            "source_diagnostic",
            "may_reopen_or_relabel_source_gate",
            "may_define_or_pass_new_gate",
            "may_authorize_nonlinear_or_3d_confirmatory_training",
            "config",
            "development_seeds",
            "success_thresholds",
            "estimators",
            "data_cells",
            "checkpoint_objective",
            "estimator_selection_cell",
            "higher_data_cell_role",
            "fresh_exact_gate_required_after_selection",
        ],
        "DA2 density estimator development",
    )
    if da2["status"] not in {
        "registered_development_only_unrun",
        "completed_development_only",
    }:
        raise ProtocolError("DA2 must remain development-only.")
    if da2["source_diagnostic"] != "DA1":
        raise ProtocolError("DA2 must remain linked to DA1.")
    if (
        da2["may_reopen_or_relabel_source_gate"] is not False
        or da2["may_define_or_pass_new_gate"] is not False
        or da2["may_authorize_nonlinear_or_3d_confirmatory_training"] is not False
    ):
        raise ProtocolError(
            "Development-only DA2 cannot pass a gate or authorize confirmation."
        )
    if da2["config"] != "configs/controlled_pde_density_development.json":
        raise ProtocolError("DA2 must point to its executable development config.")
    if da2["development_seeds"] != 3 or da2["success_thresholds"] is not None:
        raise ProtocolError("DA2 requires three development seeds and no threshold.")
    if da2["estimators"] != [
        "empirical_nll",
        "grouped_unbiased",
        "grouped_shrinkage_025",
        "grouped_shrinkage_050",
    ]:
        raise ProtocolError("DA2 estimator comparison changed.")
    if da2["data_cells"] != ["768x8", "3072x8"]:
        raise ProtocolError("DA2 data cells changed.")
    if da2["checkpoint_objective"] != "sampled_validation_nll":
        raise ProtocolError("DA2 must use sampled validation NLL checkpoints.")
    if da2["estimator_selection_cell"] != "768x8_original_g1r_budget":
        raise ProtocolError("DA2 must select estimators at the original G1r budget.")
    if da2["higher_data_cell_role"] != "data_sufficiency_control_only":
        raise ProtocolError("The DA2 high-data cell cannot select the estimator.")
    if da2["fresh_exact_gate_required_after_selection"] is not True:
        raise ProtocolError("DA2 selection must be followed by a fresh exact gate.")
    if da2["status"] == "completed_development_only":
        _require_keys(
            da2,
            [
                "result",
                "source_commit",
                "formal_selected_estimator",
                "material_estimator_improvement_found",
                "selected_mean_relative_improvement",
                "high_data_empirical_nll_maximum_density_error",
                "promote_grouped_estimator_to_method",
                "next_exact_sanity_candidate",
            ],
            "completed DA2",
        )
        if da2["result"] != (
            "results/controlled_pde_density_development_20260803.json"
        ):
            raise ProtocolError("Completed DA2 must retain its public aggregate.")
        if len(da2["source_commit"]) != 40:
            raise ProtocolError("Completed DA2 must retain its exact source commit.")
        if da2["formal_selected_estimator"] != "grouped_shrinkage_050":
            raise ProtocolError("DA2 must retain the fixed-rule formal selection.")
        if (
            da2["material_estimator_improvement_found"] is not False
            or da2["promote_grouped_estimator_to_method"] is not False
        ):
            raise ProtocolError(
                "DA2 did not support promoting grouped shrinkage as a method."
            )
        if da2["next_exact_sanity_candidate"] != (
            "empirical_nll_with_3072x8_data_budget"
        ):
            raise ProtocolError("DA2 supports a data-adequacy sanity next.")
    d0b = next(item for item in diagnostics if item["id"] == "D0b")
    _require_keys(
        d0b,
        [
            "status",
            "source_gate",
            "may_reopen_or_relabel_source_gate",
            "questions",
            "candidate_bases",
            "coefficient_budgets",
        ],
        "D0b diagnostic",
    )
    if d0b["source_gate"] != "G3":
        raise ProtocolError("D0b must remain attributed to the transient G3 branch.")
    if d0b["may_reopen_or_relabel_source_gate"] is not False:
        raise ProtocolError("A post-result diagnostic cannot relabel the failed D0.")
    if d0b["candidate_bases"] != ["dct_ii", "train_only_pod"]:
        raise ProtocolError("D0b candidates are frozen to DCT-II and train-only POD.")
    if d0b["coefficient_budgets"] != [17, 25]:
        raise ProtocolError("D0b coefficient budgets are frozen at 17 and 25.")
    checks.append("post-result diagnostic non-inflation contract")

    reentries = protocol["prospective_reentry_protocols"]
    reentry_ids = _unique_ids(reentries, "id", "prospective_reentry_protocols")
    if reentry_ids != {"G1r", "G1s"}:
        raise ProtocolError(
            "Schema v2 must retain failed G1r and the data-adequacy G1s."
        )
    g1r = next(item for item in reentries if item["id"] == "G1r")
    _require_keys(
        g1r,
        [
            "status",
            "source_gate",
            "may_relabel_failed_source_gate",
            "config",
            "fresh_test_seeds",
            "test_access_during_selection",
            "density_checkpoint_selection",
            "conditional_moment_evaluation",
            "end_to_end_mean_evaluation",
            "projective_metric",
            "success_thresholds",
        ],
        "G1r prospective re-entry",
    )
    allowed_reentry_status = {
        "preregistered_before_fresh_test",
        "completed_passed",
        "completed_failed",
    }
    if g1r["status"] not in allowed_reentry_status:
        raise ProtocolError("G1r must retain a registered or completed status.")
    if g1r["source_gate"] != "G1" or g1r["may_relabel_failed_source_gate"] is not False:
        raise ProtocolError("G1r cannot relabel the failed frozen G1.")
    if g1r["config"] != "configs/controlled_pde_g1r.json":
        raise ProtocolError("G1r must point to its executable frozen config.")
    if g1r["fresh_test_seeds"] != 5 or g1r["test_access_during_selection"] is not False:
        raise ProtocolError("G1r requires five fresh seeds and validation-only selection.")
    if g1r["density_checkpoint_selection"] != (
        "validation_nll_on_disjoint_geometries"
    ):
        raise ProtocolError("G1r density selection must use disjoint validation geometry.")
    if g1r["conditional_moment_evaluation"] != (
        "analytic_exact_poisson_pushforward"
    ):
        raise ProtocolError("G1r must retain analytic density-only moment evaluation.")
    if g1r["end_to_end_mean_evaluation"] != "gauss_hermite_quadrature":
        raise ProtocolError("G1r must retain deterministic end-to-end quadrature.")
    if g1r["projective_metric"] != (
        "signed_excess_over_matched_iid_floor_ci95_upper"
    ):
        raise ProtocolError("G1r projective metric must remain IID-floor calibrated.")
    expected_reentry_thresholds = {
        "maximum_density_only_standardized_mean_error": 0.05,
        "maximum_density_only_coverage_error": 0.03,
        "maximum_end_to_end_quadrature_mean_error": 0.05,
        "maximum_end_to_end_sampled_coverage_error": 0.03,
        "maximum_full_bc_operator_error": 0.03,
        "maximum_projective_excess_ci95_upper": 0.01,
        "maximum_analytic_nested_moment_residual": 0.000001,
    }
    if g1r["success_thresholds"] != expected_reentry_thresholds:
        raise ProtocolError("G1r thresholds changed after prospective registration.")
    if g1r["status"].startswith("completed_"):
        _require_keys(
            g1r,
            [
                "result",
                "source_commit",
                "failed_checks",
                "nonlinear_or_3d_confirmatory_training_authorized",
            ],
            "completed G1r",
        )
        if g1r["result"] != "results/controlled_pde_g1r_20260803.json":
            raise ProtocolError("Completed G1r must point to its public aggregate.")
        if len(g1r["source_commit"]) != 40:
            raise ProtocolError("Completed G1r must retain its exact source commit.")
        if g1r["status"] == "completed_failed":
            if not g1r["failed_checks"]:
                raise ProtocolError("Failed G1r must retain its failed checks.")
            if g1r["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
                raise ProtocolError(
                    "Failed G1r cannot authorize nonlinear or 3D confirmation."
                )
        elif g1r["failed_checks"]:
            raise ProtocolError("Passed G1r cannot retain failed checks.")
    g1s = next(item for item in reentries if item["id"] == "G1s")
    _require_keys(
        g1s,
        [
            "status",
            "source_gate",
            "source_diagnostic",
            "may_relabel_g1_or_g1r",
            "may_claim_data_quantity_as_method_contribution",
            "config",
            "fresh_test_seeds",
            "test_access_during_selection",
            "density_estimator",
            "train_geometries",
            "validation_geometries",
            "conditions_per_geometry",
            "test_geometries",
            "changes_from_g1r",
            "pass_interpretation",
            "success_thresholds",
            "nonlinear_or_3d_confirmatory_training_authorized",
        ],
        "G1s prospective data-adequacy re-entry",
    )
    if g1s["status"] not in allowed_reentry_status:
        raise ProtocolError("G1s must retain a registered or completed status.")
    if (
        g1s["source_gate"] != "G1r"
        or g1s["source_diagnostic"] != "DA2"
        or g1s["may_relabel_g1_or_g1r"] is not False
    ):
        raise ProtocolError("G1s cannot relabel failed G1/G1r and must follow DA2.")
    if g1s["may_claim_data_quantity_as_method_contribution"] is not False:
        raise ProtocolError("G1s cannot promote data quantity to a method contribution.")
    if g1s["config"] != "configs/controlled_pde_g1s.json":
        raise ProtocolError("G1s must point to its executable frozen config.")
    if g1s["fresh_test_seeds"] != 5 or g1s["test_access_during_selection"] is not False:
        raise ProtocolError("G1s requires five fresh seeds and validation-only selection.")
    if g1s["density_estimator"] != "empirical_nll":
        raise ProtocolError("G1s must retain empirical NLL; DA2 found no new method.")
    if (
        g1s["train_geometries"] != 3072
        or g1s["validation_geometries"] != 192
        or g1s["conditions_per_geometry"] != 8
        or g1s["test_geometries"] != 192
    ):
        raise ProtocolError(
            "G1s freezes the 3072x8 train and unchanged 192/192 validation/test budget."
        )
    if g1s["changes_from_g1r"] != [
        "five_entirely_fresh_simulation_family_seeds",
        "training_geometries_increased_from_768_to_3072",
    ]:
        raise ProtocolError("G1s may change only fresh seeds and training-data adequacy.")
    if g1s["pass_interpretation"] != (
        "data_adequacy_sanity_not_method_novelty_or_baseline_superiority"
    ):
        raise ProtocolError("G1s cannot inflate a data-adequacy pass into novelty.")
    if g1s["success_thresholds"] != expected_reentry_thresholds:
        raise ProtocolError("G1s must retain the original G1r thresholds.")
    if g1s["status"] == "preregistered_before_fresh_test":
        if g1s["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
            raise ProtocolError("Unrun G1s cannot authorize nonlinear or 3D training.")
        for forbidden_key in ("result", "source_commit", "failed_checks"):
            if forbidden_key in g1s:
                raise ProtocolError("Unrun G1s cannot contain post-result fields.")
    else:
        _require_keys(
            g1s,
            ["result", "source_commit", "failed_checks"],
            "completed G1s",
        )
        if g1s["result"] != "results/controlled_pde_g1s_20260803.json":
            raise ProtocolError("Completed G1s must point to its public aggregate.")
        if len(g1s["source_commit"]) != 40:
            raise ProtocolError("Completed G1s must retain its exact source commit.")
        if g1s["status"] == "completed_failed":
            if not g1s["failed_checks"]:
                raise ProtocolError("Failed G1s must retain its failed checks.")
            if g1s["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
                raise ProtocolError("Failed G1s cannot authorize complex confirmation.")
        else:
            if g1s["failed_checks"]:
                raise ProtocolError("Passed G1s cannot retain failed checks.")
            if g1s["nonlinear_or_3d_confirmatory_training_authorized"] is not True:
                raise ProtocolError("A completed G1s pass must authorize the next domain.")
    checks.append("prospective G1 re-entry non-inflation and data-adequacy contract")

    nonlinear = protocol["nonlinear_protocols"]
    nonlinear_ids = _unique_ids(nonlinear, "id", "nonlinear_protocols")
    if nonlinear_ids != {"N0", "N0a", "N0r", "N1"}:
        raise ProtocolError(
            "Nonlinear ladder must contain N0, non-gating N0a, fresh N0r, and N1."
        )
    n0 = next(item for item in nonlinear if item["id"] == "N0")
    _require_keys(
        n0,
        [
            "status",
            "source_gate",
            "config",
            "context_dim",
            "boundary_components",
            "conditioning",
            "functionals",
            "checks",
            "may_establish_method_novelty",
            "may_authorize_irregular_3d_headline",
            "pass_authorizes",
        ],
        "N0 nonlinear protocol",
    )
    if (
        n0["status"] not in {"preregistered_before_gpu_run", "completed_failed"}
        or n0["source_gate"] != "G1s"
        or n0["config"] != "configs/nonlinear_pde_n0.json"
    ):
        raise ProtocolError("N0 must retain its executable and prospective status after G1s.")
    if n0["context_dim"] != 5 or n0["boundary_components"] != 8:
        raise ProtocolError("N0 freezes five context and eight boundary components.")
    if n0["conditioning"] != "analytic_for_arbitrary_component_masks":
        raise ProtocolError("N0 must retain analytic component-mask conditioning.")
    if (
        n0["may_establish_method_novelty"] is not False
        or n0["may_authorize_irregular_3d_headline"] is not False
    ):
        raise ProtocolError("N0 is numerical adequacy, not novelty or a 3D gate.")
    if n0["pass_authorizes"] != "N1_learned_model_and_strong_baseline_registration":
        raise ProtocolError("N0 may authorize only N1 registration.")
    if n0["status"] == "completed_failed":
        _require_keys(
            n0,
            [
                "result",
                "source_commit",
                "failed_checks",
                "n1_registration_authorized",
                "post_result_sampling_audit",
                "next_step",
            ],
            "completed failed N0",
        )
        if n0["result"] != "results/nonlinear_pde_n0_20260803.json":
            raise ProtocolError("Failed N0 must point to its public aggregate.")
        if len(n0["source_commit"]) != 40 or not n0["failed_checks"]:
            raise ProtocolError("Failed N0 must retain exact source and failed checks.")
        if n0["n1_registration_authorized"] is not False:
            raise ProtocolError("Failed N0 cannot authorize N1.")
    else:
        for forbidden_key in (
            "result",
            "source_commit",
            "failed_checks",
            "n1_registration_authorized",
            "post_result_sampling_audit",
            "next_step",
        ):
            if forbidden_key in n0:
                raise ProtocolError("Unrun N0 cannot contain post-result fields.")
    n0a = next(item for item in nonlinear if item["id"] == "N0a")
    _require_keys(
        n0a,
        [
            "status",
            "source_gate",
            "config",
            "source_failed_result",
            "uses_only_failed_n0_seeds",
            "all_context_condition_cases_per_seed",
            "has_success_threshold",
            "may_relabel_n0",
            "may_authorize_n1",
            "may_authorize_irregular_3d",
            "may_select_n0r_thresholds_or_seeds",
            "next_step",
        ],
        "N0a nonlinear attribution",
    )
    if (
        n0a["status"]
        not in {
            "preregistered_post_result_attribution",
            "completed_non_gating_attribution",
        }
        or n0a["source_gate"] != "N0"
        or n0a["config"] != "configs/nonlinear_pde_n0_attribution.json"
        or n0a["source_failed_result"] != "results/nonlinear_pde_n0_20260803.json"
    ):
        raise ProtocolError("N0a must remain pinned to the failed N0 result.")
    if (
        n0a["uses_only_failed_n0_seeds"] is not True
        or n0a["all_context_condition_cases_per_seed"] != 288
    ):
        raise ProtocolError("N0a must audit the complete failed-seed context grid.")
    for forbidden_authority in (
        "has_success_threshold",
        "may_relabel_n0",
        "may_authorize_n1",
        "may_authorize_irregular_3d",
        "may_select_n0r_thresholds_or_seeds",
    ):
        if n0a[forbidden_authority] is not False:
            raise ProtocolError("N0a is attribution only and cannot open or tune a gate.")
    if n0a["status"] == "completed_non_gating_attribution":
        _require_keys(
            n0a,
            [
                "result",
                "source_commit",
                "source_metrics_sha256",
                "supports_contiguous_context_sampling_hypothesis",
                "uniformly_strong_nonlinearity_across_every_context",
            ],
            "completed N0a attribution",
        )
        if (
            n0a["result"]
            != "results/nonlinear_pde_n0_attribution_20260803.json"
            or len(n0a["source_commit"]) != 40
            or len(n0a["source_metrics_sha256"]) != 64
        ):
            raise ProtocolError("Completed N0a must retain exact public provenance.")
        if (
            n0a["supports_contiguous_context_sampling_hypothesis"] is not True
            or n0a["uniformly_strong_nonlinearity_across_every_context"] is not False
        ):
            raise ProtocolError("Completed N0a interpretation cannot be inflated.")
    else:
        for forbidden_key in (
            "result",
            "source_commit",
            "source_metrics_sha256",
            "supports_contiguous_context_sampling_hypothesis",
            "uniformly_strong_nonlinearity_across_every_context",
        ):
            if forbidden_key in n0a:
                raise ProtocolError("Unrun N0a cannot contain post-result fields.")

    n0r = next(item for item in nonlinear if item["id"] == "N0r")
    _require_keys(
        n0r,
        [
            "status",
            "source_gate",
            "config",
            "contract_source_commit",
            "contract_frozen_before_n0a_outcome",
            "n0a_outcome_may_change_contract",
            "fresh_seeds",
            "reference_context_coverage",
            "paired_context_coverage",
            "pde_boundary_law_functionals_solver_unchanged",
            "scientific_thresholds_and_worst_seed_rule_unchanged",
            "may_relabel_failed_n0",
            "may_establish_method_novelty",
            "may_authorize_irregular_3d_headline",
            "pass_authorizes",
        ],
        "N0r nonlinear re-entry",
    )
    if (
        n0r["status"]
        not in {"preregistered_before_fresh_gpu_run", "completed_passed"}
        or n0r["source_gate"] != "N0"
        or n0r["config"] != "configs/nonlinear_pde_n0r.json"
        or n0r["contract_source_commit"]
        != "1a680537957e4d87849abb84eab6380c76e656c9"
    ):
        raise ProtocolError("N0r must retain its exact pre-N0a preregistration.")
    if (
        n0r["contract_frozen_before_n0a_outcome"] is not True
        or n0r["n0a_outcome_may_change_contract"] is not False
        or n0r["fresh_seeds"] != 3
    ):
        raise ProtocolError("N0r must be fresh and independent of the N0a outcome.")
    if (
        n0r["reference_context_coverage"] != "24_of_24_exactly_once_per_seed"
        or n0r["paired_context_coverage"] != "24_of_24_exactly_twice_per_seed"
    ):
        raise ProtocolError("N0r must cover every context explicitly.")
    if (
        n0r["pde_boundary_law_functionals_solver_unchanged"] is not True
        or n0r["scientific_thresholds_and_worst_seed_rule_unchanged"] is not True
    ):
        raise ProtocolError("N0r may change only the biased selector and fresh seeds.")
    for forbidden_claim in (
        "may_relabel_failed_n0",
        "may_establish_method_novelty",
        "may_authorize_irregular_3d_headline",
    ):
        if n0r[forbidden_claim] is not False:
            raise ProtocolError("N0r is numerical adequacy, not a method or 3D claim.")
    if n0r["pass_authorizes"] != "N1_learned_model_and_strong_baseline_registration":
        raise ProtocolError("N0r may authorize only N1 registration.")
    if n0r["status"] == "completed_passed":
        _require_keys(
            n0r,
            [
                "result",
                "source_commit",
                "source_metrics_sha256",
                "failed_checks",
                "n1_registration_authorized",
            ],
            "completed N0r",
        )
        if n0r["result"] != "results/nonlinear_pde_n0r_20260805.json":
            raise ProtocolError("Completed N0r must point to its public aggregate.")
        if (
            len(n0r["source_commit"]) != 40
            or len(n0r["source_metrics_sha256"]) != 64
            or n0r["failed_checks"]
        ):
            raise ProtocolError("Passed N0r must retain exact source and no failures.")
        if n0r["n1_registration_authorized"] is not True:
            raise ProtocolError("A passed N0r must authorize N1 registration.")
    else:
        for forbidden_key in (
            "result",
            "source_commit",
            "source_metrics_sha256",
            "failed_checks",
            "n1_registration_authorized",
        ):
            if forbidden_key in n0r:
                raise ProtocolError("Unrun N0r cannot contain post-result fields.")

    n1 = next(item for item in nonlinear if item["id"] == "N1")
    expected_n1_status = (
        "completed_failed"
        if n0r["status"] == "completed_passed"
        else "blocked_pending_N0r"
    )
    if n1["status"] != expected_n1_status or n1["source_gate"] != "N0r":
        raise ProtocolError(
            "N1 status must follow N0r without authorizing unregistered training."
        )
    required_n1_baselines = {
        "conditional_mean_imputation",
        "independent_mask_heads",
        "LANO_style_partial_observation",
        "NOP_style_latent_conditioning",
        "compute_matched_generic_probabilistic_operator",
        "ACFlow_style_generative_active_feature_acquisition",
        "acquisition_conditioned_oracle",
        "NOTS_style_posterior_sample_functional_acquisition",
    }
    if set(n1["mandatory_baselines"]) != required_n1_baselines:
        raise ProtocolError("N1 must retain strong partial-observation and AFA baselines.")
    if n1["five_seed_confirmation_required"] is not True:
        raise ProtocolError("N1 requires five-seed confirmation.")
    if n0r["status"] == "completed_passed":
        _require_keys(
            n1,
            [
                "config",
                "source_result",
                "test_access_before_checkpoint_freeze",
                "irregular_3d_registration_authorized",
                "core_development",
                "optimization_attribution",
                "prospective_reentry",
                "outer_test_execution",
                "post_result_attribution",
                "next_development_audits",
                "missing_operator_pullback_m0",
            ],
            "completed N1",
        )
        if (
            n1["config"] != "configs/nonlinear_pde_n1.json"
            or n1["source_result"] != "results/nonlinear_pde_n0r_20260805.json"
            or n1["test_access_before_checkpoint_freeze"] is not False
            or n1["irregular_3d_registration_authorized"] is not False
        ):
            raise ProtocolError(
                "Failed N1 must retain pre-freeze test access order and cannot "
                "authorize irregular 3D."
            )
        development = n1["core_development"]
        _require_keys(
            development,
            [
                "status",
                "results",
                "source_commits",
                "test_generated_or_accessed",
                "n1_gate_decided",
                "confirmatory_test_authorized",
                "next_step",
            ],
            "N1 core development",
        )
        if (
            development["status"]
            != "validation_only_two_attempts_completed_insufficient"
            or development["results"]
            != [
                "results/nonlinear_pde_n1_core_development_20260805.json",
                "results/nonlinear_pde_n1_core_development_unit_peak_20260805.json",
            ]
            or len(development["source_commits"]) != 2
            or any(len(value) != 40 for value in development["source_commits"])
            or development["test_generated_or_accessed"] is not False
            or development["n1_gate_decided"] is not False
            or development["confirmatory_test_authorized"] is not False
        ):
            raise ProtocolError(
                "Insufficient N1 development cannot decide the gate or open test."
            )
        attribution = n1["optimization_attribution"]
        if attribution != {
            "status": "completed_validation_only_selected_scale_normalized_2800",
            "config": "configs/nonlinear_pde_n1_optimization_attribution.json",
            "result": "results/nonlinear_pde_n1_optimization_attribution_20260805.json",
            "source_commit": "eebcd918f194159e1c12c78269fd2829896d3c59",
            "source_metrics_sha256": "3af4e7d98928c928bbfb62e4bd70bfa96c3fa93941e13a3403bdea3d9b570337",
            "selected_variant": "scale_normalized_2800",
            "validation_full_bc_relative_l2": 0.011623237282037735,
            "validation_paired_response_relative_l2": 0.012195270508527756,
            "has_success_threshold": False,
            "may_access_test_or_decide_n1": False,
        }:
            raise ProtocolError(
                "N1 optimization attribution must remain non-gating and test-free."
            )
        prospective = n1["prospective_reentry"]
        if prospective != {
            "id": "N1b",
            "status": "five_seed_validation_only_checkpoint_freeze_complete_before_test",
            "config": "configs/nonlinear_pde_n1b.json",
            "checkpoint_manifest": "results/nonlinear_pde_n1b_checkpoint_manifest_20260805.json",
            "checkpoint_manifest_sha256": "4dd22e9f6e8c85662a5352ba123e122fd542a03e4d4131f24ba702629937ad7f",
            "source_commit": "1d0bd9c759f935f818b5705b1b9bc2a00116ea59",
            "selected_loss_conditioning": "train_only_rms_normalized_field_and_pair_mse",
            "selected_maximum_steps": 2800,
            "direct_baseline_pod_rank": 96,
            "direct_baseline_pod_seed": 73080601,
            "direct_baseline_pod_iterations": 4,
            "confirmatory_seed_controls_weight_initialization_and_batch_sampling": True,
            "confirmatory_checkpoint_seeds": 5,
            "checkpoint_seed_jobs_exit_zero": 5,
            "checkpoint_seed_jobs_eligible": 5,
            "trainable_checkpoints_frozen": 50,
            "validation_aurora_full_bc_relative_l2_mean": 0.01346952822059393,
            "validation_aurora_paired_response_relative_l2_mean": 0.01366054341197014,
            "validation_aurora_objective_better_than_deltaphi_seeds": 0,
            "checkpoint_manifest_required_before_test": True,
            "outer_test_execution_overlay_required_before_test": True,
            "test_generated_or_accessed": False,
            "n1_gate_decided": False,
            "irregular_3d_registration_authorized": False,
        }:
            raise ProtocolError(
                "N1b manifest must remain exact, test-free, and non-gating."
            )
        outer_test = n1["outer_test_execution"]
        if outer_test != {
            "id": "N1c",
            "status": "completed_failed",
            "config": "configs/nonlinear_pde_n1c.json",
            "config_sha256": "6e14a9ed1682771fe3936e753d16d30317145752fb17f5e091f3db0b8e63ba8e",
            "checkpoint_manifest_commit": "c66f651a9cd13c7f58450f21c1d67ba11d78de8e",
            "checkpoint_manifest_sha256": "4dd22e9f6e8c85662a5352ba123e122fd542a03e4d4131f24ba702629937ad7f",
            "source_commit": "62605a0a2060613dd739217474a90ddc6869c10c",
            "result": "results/nonlinear_pde_n1c_20260805.json",
            "source_metrics_sha256": "a3759dcf7d47aa3f636e8cab695ee96d285d60c7236e4899bb2af0737ebc0368",
            "route_and_acquisition_context_selector": (
                "indices_0_to_188_step_4_condition_0"
            ),
            "true_conditional_respects_latent_radius_truncation": True,
            "route_common_random_numbers_registered": True,
            "route_common_random_numbers_valid_for_primary_action_metric": True,
            "route_candidate_voi_common_random_numbers_implemented": False,
            "invalid_secondary_metrics": [
                "route_value_of_information_disagreement",
                "route_selected_next_component_disagreement",
            ],
            "acquisition_outer_inner_samples": [8, 32],
            "context_family_bootstrap_replicates": 2000,
            "registered_shifts_deferred_to_fixed_N1d_secondary_job": True,
            "test_generated_or_accessed": True,
            "n1_gate_decided": True,
            "n1_passed": False,
            "passed_checks": [
                "full_bc_operator",
                "functional_coverage",
                "route_bayes_action",
            ],
            "failed_checks": [
                "paired_response",
                "field_distribution",
                "acquisition_regret",
            ],
            "n1d_shift_executed": False,
            "post_result_attribution_is_non_gating": True,
            "irregular_3d_registration_authorized": False,
        }:
            raise ProtocolError(
                "Failed N1c must retain its exact result and keep N1d/3D closed."
            )
        post_result = n1["post_result_attribution"]
        _require_keys(
            post_result,
            [
                "id",
                "status",
                "config",
                "source_commit",
                "result",
                "parent_n1c_status",
                "has_success_threshold",
                "may_relabel_n1c",
                "may_select_model_or_checkpoint",
                "may_authorize_n1d_or_irregular_3d",
                "result_summary",
                "next_development",
            ],
            "N1c-a post-result attribution",
        )
        if (
            post_result["id"] != "N1c-a"
            or post_result["status"] != "completed_non_gating_attribution"
            or post_result["config"]
            != "configs/nonlinear_pde_n1c_attribution.json"
            or post_result["source_commit"]
            != "b97899cee774d0ab0bc3da2b3cfa4af2d609c615"
            or post_result["result"]
            != "results/nonlinear_pde_n1c_attribution_20260806.json"
            or post_result["parent_n1c_status"]
            != "completed_failed_unchanged"
            or post_result["has_success_threshold"] is not False
            or post_result["may_relabel_n1c"] is not False
            or post_result["may_select_model_or_checkpoint"] is not False
            or post_result["may_authorize_n1d_or_irregular_3d"] is not False
            or post_result["result_summary"]
            != {
                "aurora_joint_better_than_independent_conditional_nll_seeds": {
                    "missing": 0,
                    "sparse_2": 0,
                    "partial_4": 0,
                },
                "functional_energy_density_to_simulator_substitution_ratio": {
                    "missing": 13.001171873559112,
                    "sparse_2": 5.807517272798561,
                },
                "missing_64x128_acquisition_regret_better_than_acflow_seeds": 1,
                "sparse_2_acquisition_is_non_discriminative": True,
                "worst_route_risk_better_than_independent_seeds": 3,
                "primary_bottleneck": "joint_boundary_density_and_training_objective",
                "current_paper_identity_supported": False,
            }
            or post_result["next_development"]
            != {
                "density_objective_control": (
                    "validation_only_full_joint_nll_vs_registered_mask_"
                    "conditional_composite_likelihood"
                ),
                "decision_task_adequacy": "true_law_and_true_simulator_only",
                "has_success_threshold": False,
                "fresh_reentry_registered": False,
                "irregular_3d_authorized": False,
            }
        ):
            raise ProtocolError(
                "N1c-a must preserve the density bottleneck, failed N1c, "
                "and non-gating development boundary."
            )
        audits = n1["next_development_audits"]
        if audits != {
            "status": "two_threshold_free_audits_completed_non_gating",
            "parent_public_commit": "5eb3b869e93c1557c777259281396bf247688dad",
            "execution_source_commit": (
                "337c75e6fcb933eaab86c900fc132d4a13b740a5"
            ),
            "density_objective": {
                "config": (
                    "configs/nonlinear_pde_n1_density_objective_audit.json"
                ),
                "config_sha256": (
                    "b4af684939d2659a88f885ed487b4b85657fbe5da319da81a351f908c1200ec5"
                ),
                "status": "completed_threshold_free_development_audit",
                "result": (
                    "results/nonlinear_pde_n1_density_objective_audit_"
                    "20260806.json"
                ),
                "result_sha256": (
                    "94686547ea927324cd4e376c3500067176843b401511d519e993864ea199b147"
                ),
                "model_seeds": 5,
                "fresh_from_n1_development_and_confirmatory_seeds": True,
                "variants": [
                    "n1c_random_mask_raw",
                    "random_mask_per_component",
                    "full_joint_per_component",
                    "registered_composite_per_component",
                ],
                "selection_split": "selection_validation_only",
                "audit_split": "disjoint_audit_validation",
                "has_success_threshold": False,
                "may_access_or_generate_n1_test": False,
                "may_select_a_method": False,
                "may_establish_method_novelty": False,
                "full_joint_excess_reduction_percent": {
                    "missing": 27.236424996624383,
                    "sparse_2": 23.79853039822494,
                    "partial_4": 20.27965080407532,
                },
                "full_joint_better_than_n1c_raw_seeds": {
                    "missing": 5,
                    "sparse_2": 5,
                    "partial_4": 5,
                },
                "interpretation": (
                    "full_joint_likelihood_is_strongest_engineering_"
                    "control_not_method_novelty"
                ),
            },
            "decision_task": {
                "config": (
                    "configs/nonlinear_pde_n1_decision_task_audit.json"
                ),
                "config_sha256": (
                    "00cef2ab32885ed4091e4aa85e59d94cbc4acf1a8630accf241046c1e4a62a60"
                ),
                "status": "completed_threshold_free_model_free_audit",
                "result": (
                    "results/nonlinear_pde_n1_decision_task_audit_"
                    "20260806.json"
                ),
                "result_sha256": (
                    "4492a7759fc08b4c2ac81196e2c345634419215f89030b062356aa801e232ab7"
                ),
                "uses_learned_model_or_checkpoint": False,
                "base_masks": ["missing", "sparse_2"],
                "independent_monte_carlo_replicates": 2,
                "has_success_threshold": False,
                "may_access_or_generate_n1_test": False,
                "may_select_a_method": False,
                "may_establish_method_novelty": False,
                "missing": {
                    "value_of_information_replicates": [
                        0.1558709591627121,
                        0.15558111667633057,
                    ],
                    "winner_agreement": 0.9270833730697632,
                    "interpretation": (
                        "nonzero_stable_context_dependent_"
                        "acquisition_endpoint"
                    ),
                },
                "sparse_2": {
                    "value_of_information_replicates": [
                        0.18517088890075684,
                        0.1855398416519165,
                    ],
                    "winner_agreement": 1.0,
                    "fixed_winner_component": 6,
                    "fixed_winner_contexts": 96,
                    "interpretation": (
                        "valuable_measurement_but_nonadaptive_"
                        "fixed_winner_task"
                    ),
                },
            },
            "joint_interpretation": {
                "n1c_status": "completed_failed_unchanged",
                "method_novelty_established": False,
                "missing_only_future_decision_endpoint_candidate": True,
                "sparse_2_adaptive_policy_headline_eligible": False,
                "fresh_reentry_registered": False,
                "n1d_or_irregular_3d_authorized": False,
                "positive_feasibility_evidence_can_only_motivate_a_separate_fresh_protocol": True,
            },
        }:
            raise ProtocolError(
                "Post-N1c audits must remain completed, test-free, "
                "non-selecting, non-gating, and unable to authorize N1d "
                "or irregular 3D."
            )
        m0 = n1["missing_operator_pullback_m0"]
        if m0 != {
            "config": (
                "configs/nonlinear_pde_n1_missing_operator_pullback_m0.json"
            ),
            "status": "execution_incomplete_no_scientific_verdict",
            "stage": (
                "closed_validation_only_mechanism_execution_without_gate_verdict"
            ),
            "source_commit": "89bdc8560a7e5db1d4b5402cd76dbbb01d991aad",
            "source_config_sha256": (
                "78aa6752ed647ffbcb1b90f262873a05156ddda49c6aa21557cc6f7908345f91"
            ),
            "execution_record": (
                "results/nonlinear_pde_n1_missing_operator_pullback_"
                "m0_execution_20260808.json"
            ),
            "execution_record_sha256": (
                "5376cd4629cc30f1fa16ab1e1762a576866a4d35620cc5e34a9986d5a2bfc593"
            ),
            "pbs_array_job": "115078",
            "required_complete_seeds": 3,
            "completed_seeds": 2,
            "failed_seeds": 1,
            "aggregate_created": False,
            "gate_decided": False,
            "scientific_verdict": "not_available",
            "successful_seed_metrics_inspected_for_gate": False,
            "sampler_repair_or_rerun_registered": False,
            "base_mask": "missing",
            "sparse_2_role": "fixed_acquisition_control_only",
            "model_seeds": [73081021, 73081022, 73081023],
            "data": {
                "train_contexts": 3072,
                "conditions_per_context": 8,
                "selection_validation_contexts": 384,
                "audit_validation_contexts": 192,
                "acquisition_audit_contexts": 96,
            },
            "proposed_mechanism": (
                "full_joint_likelihood_plus_candidate_measurement_solution_"
                "joint_pushforward_kernel_score"
            ),
            "controls": [
                "full_joint_mle",
                "full_joint_plus_boundary_kernel",
                "full_joint_plus_solution_marginal_kernel",
            ],
            "frozen_operator": "N1b_pair_loss_zero_seed_matched_read_only",
            "primary_metrics": [
                "true_simulator_candidate_joint_mmd_squared",
                "true_oracle_acquisition_regret",
            ],
            "all_checks_required": True,
            "relative_improvement_minimum": 0.05,
            "seed_direction_minimum": 3,
            "paired_context_ci95_upper_below_zero": True,
            "missing_density_excess_relative_degradation_maximum": 0.05,
            "solution_marginal_mmd_relative_degradation_maximum": 0.01,
            "frozen_operator_audit_l2_maximum_every_seed": 0.05,
            "may_access_or_generate_n1_test": False,
            "may_relabel_n1c": False,
            "may_establish_method_novelty": False,
            "fresh_reentry_registered": False,
            "may_authorize_n1d_or_irregular_3d": False,
            "failure_abandons_mechanism_without_local_weight_or_kernel_repair": True,
            "incomplete_execution_closes_mechanism_without_local_sampler_repair_or_rerun": True,
            "pass_only_allows_separate_fresh_reentry_protocol_design": True,
        }:
            raise ProtocolError(
                "M0 must preserve its incomplete no-verdict execution record, "
                "remain missing-only, test-free, non-authorizing, and closed "
                "without local repair or rerun."
            )
    checks.append("nonlinear N0-to-N1 non-inflation and strong-baseline contract")

    evaluation = protocol["evaluation"]
    _require_keys(
        evaluation,
        [
            "operator_outer_split",
            "condition_shift_split",
            "observation_masks",
            "clinical_outer_folds",
            "clinical_inner_folds",
            "bootstrap_unit",
            "clinical_bootstrap_unit",
            "bootstrap_replicates",
            "headline_seeds",
        ],
        "evaluation",
    )
    if evaluation["operator_outer_split"] != "geometry_disjoint":
        raise ProtocolError("Operator evaluation must remain geometry-disjoint.")
    if evaluation["bootstrap_unit"] != "geometry":
        raise ProtocolError("Operator uncertainty must be bootstrapped by geometry.")
    if evaluation["clinical_bootstrap_unit"] != "patient":
        raise ProtocolError("Secondary clinical uncertainty must be bootstrapped by patient.")
    if {"full", "missing"} - set(evaluation["observation_masks"]):
        raise ProtocolError("Evaluation must include full and missing observation masks.")
    if evaluation["clinical_outer_folds"] < 3 or evaluation["clinical_inner_folds"] < 3:
        raise ProtocolError("Nested clinical validation requires at least 3 folds per level.")
    if evaluation["bootstrap_replicates"] < 1000:
        raise ProtocolError("At least 1,000 patient bootstrap replicates are required.")
    checks.append("geometry-disjoint operator and nested patient-level evaluation")

    phases = protocol["phases"]
    _unique_ids(phases, "id", "phases")
    for phase in phases:
        _require_keys(phase, ["id", "name", "requires", "outputs"], "phase")
        unknown = set(phase["requires"]) - gate_ids
        if unknown:
            raise ProtocolError(
                f"Phase {phase['id']} references unknown gates: {sorted(unknown)}"
            )
    checks.append("phase dependency graph")
    return checks


def canonical_hash(protocol: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 for split/run manifests."""

    encoded = json.dumps(
        protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "summary"):
        child = subparsers.add_parser(command)
        child.add_argument("protocol", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    protocol = load_protocol(args.protocol)
    checks = validate_protocol(protocol)
    digest = canonical_hash(protocol)
    if args.command == "validate":
        print(f"AURORA protocol valid · {len(checks)} invariant groups")
        for check in checks:
            print(f"  ✓ {check}")
        print(f"  sha256 {digest}")
    else:
        print(
            json.dumps(
                {
                    "project": protocol["project"]["name"],
                    "primary_problem": protocol["task"]["primary_problem"],
                    "application_endpoint": protocol["task"]["application_endpoint"],
                    "datasets": [item["name"] for item in protocol["datasets"]],
                    "gates": [item["id"] for item in protocol["gates"]],
                    "protocol_sha256": digest,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
