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


ALLOWED_PRIMARY_PROBLEMS = {"unselected"}
ALLOWED_ENDPOINTS = {"unselected"}
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
    "physical_base_geometry",
    "cta_case",
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
    "flow_mri_multiresolution_phantom_2021",
    "flow_mri_dual_venc_phantoms_2025",
    "flow_mri_intervention_phantoms_2025",
    "rsna_ica_2025_controlled_access",
    "open_multicenter_cta_2026_zenodo_15697196",
    "topaneu_2026_terms_gated",
    "dias_dsa_sequence_2024",
    "aneurisk_cfd_curvature_2026",
    "tornadic_wss_topology_2026_figshare",
    "maximus_tof_model_2025",
    "rheology_slip_aneurysm_case01_2026",
    "openneuro_ds003949",
    "vmr_growth_matched_cerebral_aneurysm",
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
            "problem_selection",
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

    if protocol["schema_version"] != "11.8":
        raise ProtocolError("The current research-state schema must be version 11.8.")

    project = protocol["project"]
    _require_keys(
        project,
        [
            "name",
            "status",
            "clinical_use",
            "execution_server",
            "allowed_pbs_queues",
            "excluded_execution_servers",
            "current_gpu_job_count",
            "current_scheduler_observation",
            "first_future_gpu_action",
        ],
        "project",
    )
    if project["name"] != "AURORA":
        raise ProtocolError("Project name must remain AURORA for schema v1.")
    if project["clinical_use"] is not False:
        raise ProtocolError("AURORA v1 must be marked research-only.")
    if (
        project["status"]
        != "one_conditional_response_fidelity_source_lead_with_non_executable_method_free_p0_no_method_gpu_outer_test_or_claim"
        or project["execution_server"] != "introai9"
        or project["allowed_pbs_queues"] != ["coss_agpu", "coss_a6gpu"]
        or project["excluded_execution_servers"] != ["junjinyong"]
        or project["current_gpu_job_count"] != 0
        or project["current_scheduler_observation"]
        != "introai9_p0_115848_e_exit2_walltime_00_04_44_gpu0_scientific_checks_0_of_10_no_login_node_gpu_command"
        or project["first_future_gpu_action"]
        != "none_until_a_fresh_problem_passes_source_admission_and_a_later_gate_explicitly_authorizes_gpu"
    ):
        raise ProtocolError(
            "AURORA compute must remain introai9-only with junjinyong excluded, "
            "no tracked AURORA GPU job, the last CPU-only P0 observation, "
            "and no future GPU action before a fresh scientific gate."
        )
    checks.append("research-only project boundary")

    problem_selection = protocol["problem_selection"]
    _require_keys(
        problem_selection,
        [
            "status",
            "shortlisted_candidate",
            "conditional_source_lead_count",
            "candidate_dataset",
            "candidate_estimand",
            "asset_access_status",
            "user_accepted_data_terms_verified",
            "task_unit_audited",
            "annotation_selection_mechanism_audited",
            "coarsening_at_random_assumed",
            "method_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "next_allowed_action",
            "audit_document",
            "future_source_admission_v2",
            "dataset_asset_state_ledger",
            "acquired_asset_application_direction",
            "aneux_reliability_direct_prior_reappraisal",
            "aneumo_response_fidelity_source_audit",
            "open_clinical_outcome_and_target_time_reappraisal",
            "mechanistic_treatment_and_growth_asset_reappraisal",
            "introai9_dataset_inventory_audit",
            "endovascular_collision_anticipation_and_release_reappraisal",
            "molecular_biomarker_and_treatment_specific_outcome_reappraisal",
            "structured_vessel_and_embargoed_4dflow_reappraisal",
            "pose_workflow_and_spatiotemporal_operator_reappraisal",
            "surface_vector_and_task_faithful_dsa_delta",
            "adam_patch_fold_and_segmentation_prior_delta",
            "aneurysmal_sah_segmentation_outcome_reappraisal",
            "rsna_release_layer_and_webgan_utility_delta",
            "rupture_state_future_risk_and_unit_semantics_delta",
            "longitudinal_biology_and_cross_scale_mechanism_reappraisal",
            "four_d_cta_wall_phenotype_release_reappraisal",
            "culprit_lesion_and_mimic_differential_reappraisal",
            "topbrain2025_and_rsna_multitask_source_correction",
            "target_time_and_instability_prediction_reappraisal",
            "decision_time_and_clinical_precision_reappraisal",
            "device_planning_and_mechanistic_occlusion_reappraisal",
            "adam_longitudinal_and_treated_exclusion_source_correction",
            "diagnostic_action_and_human_ai_reappraisal",
            "longitudinal_intervention_and_patient_reliability_reappraisal",
            "neck_isolation_and_open_model_source_reappraisal",
            "vmr_growth_paired_surface_structure_source_audit",
            "latent_shape_open_cta_transport_reappraisal",
            "synva_release_and_synthetic_utility_source_audit",
            "reference_provenance_and_rsna_release_contract_reappraisal",
            "topaneu_registered_design_and_realized_release_reappraisal",
            "topaneu_annotation_version_orbit_reappraisal",
            "aaa_cross_scale_source_reappraisal",
            "mris_bench_target_contract_audit",
            "open_model_transport_source_reappraisal",
            "cross_vascular_transient_wss_source_correction",
            "posttreatment_reference_linked_imaging_source_delta",
            "aneumo_bc_transport_source_audit",
            "source_only_dataset_substitution_screen",
            "topaneu_attachment_source_audit",
            "topaneu_release_evaluation_source_audit",
            "topaneu_code_semantics_red_team",
            "open_cta_physical_grid_candidate",
            "inverse_healthy_vessel_counterfactual_source_audit",
            "rsna_supervision_semantics_red_team",
            "goal_oriented_segmentation_cold_audit",
            "aneux_preprocessing_orbit_candidate",
            "aneug_cycle_functional_source_audit",
            "aneug_cycle_transport_reentry_v2a",
            "dsa_prefix_risk_source_audit",
            "source_delta_audit",
            "vascular_semantics_source_audit",
            "pinn_rupture_direct_prior_audit",
            "hemodynamic_endpoint_source_audit",
            "topology_procedure_source_audit",
            "context_treatment_source_audit",
            "provenance_evaluation_source_audit",
            "treatment_surveillance_source_audit",
            "acquisition_flow_source_audit",
            "fsi_wall_source_audit",
            "longitudinal_perfusion_source_audit",
            "longitudinal_mra_growth_source_audit",
            "aneumo_lineage_split_source_audit",
            "failure_mechanism_biology_source_audit",
            "reconstruction_annotation_reliability_source_audit",
            "method_asset_viability_source_audit",
            "registry_gap_source_audit",
            "broad_registry_source_audit",
            "rsna_aws_registry_correction_audit",
            "topbrain2_source_audit",
            "four_d_cta_aaa_mechanics_source_audit",
            "openneuro_containment_morphometry_source_audit",
            "aneug_target_construction_source_audit",
            "aneug_surface_vector_structure_source_audit",
            "surface_vector_conditional_assessment",
            "surface_vector_finite_closure",
            "expert_virtual_removal_pair_source_delta",
            "measurement_functional_inverse_flow_source_delta",
            "structure_faithful_wss_source_reappraisal",
            "conformal_degree_certificate_source_audit",
            "cross_view_projection_source_delta",
            "functional_4dflow_segmentation_source_delta",
            "aneux_transient_cfd_material_source_audit",
            "team_downstream_utility_reappraisal",
            "public_source_watch_v4",
            "public_source_watch_v5",
            "public_source_watch_v6",
            "public_source_watch_v7",
            "public_source_watch_v8",
            "public_source_watch_v9",
            "public_source_watch_v10",
            "public_source_watch_v11",
            "public_source_watch_v12",
            "public_source_watch_v13",
            "public_source_watch_v14",
            "public_source_watch_v15",
            "public_source_watch_v16",
            "public_source_watch_v17",
            "public_source_watch_v18",
            "public_source_watch_v19",
            "public_source_watch_v20",
            "public_source_watch_v21",
            "most_recent_closed_candidate",
            "most_recent_source_rejected_candidate",
            "most_recent_conditional_source_lead",
            "rejected_candidates",
            "non_novel_components",
        ],
        "problem_selection",
    )
    if (
        problem_selection["status"]
        != "one_conditional_source_lead_and_registered_non_executable_method_free_p0_no_primary_method_gpu_outer_test_or_claim"
        or problem_selection["shortlisted_candidate"]
        != "field_error_matched_multi_flow_response_fidelity"
        or problem_selection["conditional_source_lead_count"] != 1
        or problem_selection["candidate_dataset"] != "aneumo_verified_compact_cache"
        or problem_selection["candidate_estimand"]
        != "reference_velocity_multi_flow_response_fidelity_not_clinical_outcome"
        or problem_selection["asset_access_status"]
        != "verified_historical_aneumo_compact_cache_contract_but_current_introai9_exact_private_path_unresolved_active_assignment_zero"
        or problem_selection["user_accepted_data_terms_verified"] is not False
        or problem_selection["task_unit_audited"] is not True
        or problem_selection["annotation_selection_mechanism_audited"] is not False
        or problem_selection["coarsening_at_random_assumed"] is not False
        or problem_selection["method_selected"] is not False
        or problem_selection["gpu_training_authorized"] is not False
        or problem_selection["outer_test_authorized"] is not False
        or problem_selection["submission_identity_active"] is not False
        or problem_selection["next_allowed_action"]
        != "after_external_service_change_run_one_bounded_exact_aneumo_cache_path_checksum_preflight_then_cpu_only_method_free_p0_no_model_gpu_or_test"
        or problem_selection["audit_document"]
        != "docs/response-faithful-hemodynamic-surrogate-source-audit-2026-08-12.md"
        or problem_selection["most_recent_closed_candidate"]
        != "growth_paired_transient_wss_structure_stability_execution_incomplete_no_scientific_verdict"
        or problem_selection["most_recent_source_rejected_candidate"]
        != "aneux_factorized_nested_preprocessing_orbit_reliability_rejected_pre_execution_at_32_residual_novelty_2_below_2_5_floor"
        or problem_selection["most_recent_conditional_source_lead"]
        != "field_error_matched_multi_flow_response_fidelity_method_free_p0_only"
    ):
        raise ProtocolError(
            "The sole response-fidelity source lead may authorize only its registered "
            "non-executable method-free P0, never a primary method, GPU, test, or claim."
        )
    admission_v2 = problem_selection["future_source_admission_v2"]
    _require_keys(
        admission_v2,
        [
            "status",
            "effective_schema",
            "prospective_only",
            "historical_scores_relabelled",
            "historical_job_outcomes_relabelled",
            "axis_order",
            "total_threshold",
            "critical_axis_minima",
            "requires_noncompositional_residual_gap",
            "requires_prospective_failure_mechanism_and_falsifier",
            "component_stacking_or_model_naming_can_satisfy_novelty",
            "pass_authorizes_only",
            "pass_authorizes_method_architecture_or_gpu",
            "current_batch_best_score",
            "current_batch_best_residual_novelty",
            "current_batch_admitted_count",
        ],
        "future source admission v2",
    )
    expected_admission_axes = [
        "clinical_importance",
        "target_identifiability",
        "residual_novelty",
        "asset_readiness",
        "effective_independent_unit",
        "strong_baseline_feasibility",
        "interpretable_evidence",
        "isbi_schedule_fit",
    ]
    expected_critical_minima = {
        "target_identifiability": 3.5,
        "residual_novelty": 2.5,
        "asset_readiness": 3.0,
        "effective_independent_unit": 3.0,
        "strong_baseline_feasibility": 3.0,
    }
    if (
        admission_v2["status"]
        != "prospective_noncompensatory_gate_active_for_fresh_candidates_only"
        or admission_v2["effective_schema"] != "8.8"
        or admission_v2["prospective_only"] is not True
        or admission_v2["historical_scores_relabelled"] is not False
        or admission_v2["historical_job_outcomes_relabelled"] is not False
        or admission_v2["axis_order"] != expected_admission_axes
        or admission_v2["total_threshold"] != 32.0
        or admission_v2["critical_axis_minima"] != expected_critical_minima
        or admission_v2["requires_noncompositional_residual_gap"] is not True
        or admission_v2["requires_prospective_failure_mechanism_and_falsifier"]
        is not True
        or admission_v2["component_stacking_or_model_naming_can_satisfy_novelty"]
        is not False
        or admission_v2["pass_authorizes_only"]
        != "prospectively_registered_method_free_p0"
        or admission_v2["pass_authorizes_method_architecture_or_gpu"] is not False
        or admission_v2["current_batch_best_score"] != 34.0
        or admission_v2["current_batch_best_residual_novelty"] != 2.5
        or admission_v2["current_batch_admitted_count"] != 1
    ):
        raise ProtocolError(
            "Future source admission v2 must remain prospective and non-compensatory: "
            "a total score cannot override novelty, identifiability, asset, unit, or "
            "baseline floors, and a pass opens only a method-free P0."
        )
    checks.append("prospective non-compensatory source-admission boundary")

    open_outcome = problem_selection[
        "open_clinical_outcome_and_target_time_reappraisal"
    ]
    _require_keys(
        open_outcome,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "asah_risk_doi", "asah_risk_zenodo_record_id",
            "asah_risk_zenodo_revision", "asah_risk_zenodo_license",
            "asah_risk_file_name", "asah_risk_file_bytes",
            "asah_risk_file_md5", "asah_risk_source_patients",
            "asah_risk_source_variables",
            "asah_risk_missing_six_month_mrs_patients",
            "asah_risk_fixed_six_month_outcome_identified",
            "asah_risk_medical_image_payload_present",
            "asah_risk_xlsx_payload_downloaded_or_opened", "candidates",
            "recurring_source_watch_added", "source_watch_config",
            "p0_registered", "p1_registered", "method_selected",
            "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "submission_identity_active", "execution_server",
            "login_node_gpu_command_executed", "junjinyong_accessed",
        ],
        "open clinical outcome and target-time reappraisal",
    )
    expected_open_candidates = {
        "endpoint_provenance_aware_asah_six_month_prognosis": 29.5,
        "asis_management_to_one_year_mrs": 28.0,
        "admission_only_external_calibration_of_asah_risk": 27.0,
        "risk_score_refinement_for_future_instability": 27.0,
        "circle_of_willis_imaging_marker_transport": 26.0,
        "center_robust_rupture_phenotype_dependency": 25.5,
    }
    if (
        open_outcome["status"]
        != "fresh_batch_rejected_best_29_5_open_actual_clinical_table_but_not_imaging_and_fixed_time_target_unidentified"
        or open_outcome["audit_document"]
        != "docs/open-clinical-outcome-and-target-time-reappraisal-2026-08-12.md"
        or open_outcome["automatic_selection_threshold"] != 32.0
        or open_outcome["best_candidate_id"]
        != "endpoint_provenance_aware_asah_six_month_prognosis"
        or open_outcome["best_score"] != 29.5
        or open_outcome["best_residual_novelty_score"] != 2.0
        or open_outcome["all_candidate_scores"]
        != [29.5, 28.0, 27.0, 27.0, 26.0, 25.5]
        or open_outcome["conditional_source_lead_count"] != 0
        or open_outcome["asah_risk_zenodo_record_id"] != 17339029
        or open_outcome["asah_risk_zenodo_revision"] != 6
        or open_outcome["asah_risk_file_bytes"] != 39686
        or open_outcome["asah_risk_source_patients"] != 230
        or open_outcome["asah_risk_missing_six_month_mrs_patients"] != 70
        or {
            item["id"]: item["total"] for item in open_outcome["candidates"]
        } != expected_open_candidates
        or any(item["critical_axis_pass"] for item in open_outcome["candidates"])
        or open_outcome["asah_risk_fixed_six_month_outcome_identified"] is not False
        or open_outcome["asah_risk_medical_image_payload_present"] is not False
        or open_outcome["asah_risk_xlsx_payload_downloaded_or_opened"] is not False
        or open_outcome["recurring_source_watch_added"] is not True
        or open_outcome["source_watch_config"] != "configs/source_watch_v21.json"
        or open_outcome["execution_server"] != "introai9"
        or any(
            open_outcome[key] is not False
            for key in (
                "primary_problem_selected", "paper_identity_active",
                "p0_registered", "p1_registered", "method_selected",
                "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
    ):
        raise ProtocolError(
            "The open aSAH clinical table is a versioned non-imaging source asset, "
            "not a fixed-time outcome truth, active dataset, method or compute authority."
        )
    checks.append("open clinical table target-time and non-imaging boundary")

    mechanistic = problem_selection[
        "mechanistic_treatment_and_growth_asset_reappraisal"
    ]
    _require_keys(
        mechanistic,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "coil_mechanics_doi", "coil_mechanics_synthetic_sacs",
            "coil_mechanics_reaction_force_source_r2",
            "coil_mechanics_elastic_energy_source_r2",
            "coil_mechanics_public_patient_geometry_device_outcome_join",
            "qa_occlusion_doi", "qa_occlusion_source_patients",
            "qa_occlusion_target_months", "qa_occlusion_source_auc_uncorrected",
            "qa_occlusion_source_auc_corrected",
            "qa_occlusion_public_patient_rows_images_split",
            "longitudinal_growth_doi", "longitudinal_growth_aneurysms",
            "longitudinal_growth_matched_pairs",
            "longitudinal_growth_timepoints_per_aneurysm",
            "longitudinal_growth_public_image_mesh_cfd_manifest",
            "amplified_wall_motion_doi", "amplified_wall_motion_growing_cases",
            "amplified_wall_motion_stable_cases",
            "amplified_wall_motion_public_field_motion_growth_asset",
            "automated_initiation_doi", "automated_initiation_cases",
            "automated_initiation_initial_failures_manually_resolved",
            "automated_initiation_public_casewise_failure_contract",
            "particle_transport_doi", "particle_transport_idealized_anatomies",
            "particle_transport_configurations",
            "particle_transport_clinical_outcome_asset",
            "same_patient_geometry_device_immediate_response_fixed_time_outcome_join_public",
            "candidates", "subscription_full_text_accessed",
            "supplement_payload_accessed",
            "patient_image_or_geometry_payload_accessed",
            "clinical_row_or_device_payload_accessed",
            "surface_vector_question_retained_as_inactive_hypothesis",
            "historical_surface_vector_source_score_or_job_relabelled",
            "historical_surface_vector_p0_repaired_or_rerun", "p0_registered",
            "p1_registered", "method_selected", "architecture_selected",
            "scientific_server_queried", "gpu_training_authorized",
            "outer_test_authorized", "submission_identity_active",
            "execution_server", "login_node_gpu_command_executed",
            "junjinyong_accessed", "source_watch_added", "next_allowed_action",
        ],
        "mechanistic treatment and growth asset reappraisal",
    )
    expected_mechanistic_candidates = [
        ("injection_invariant_qa_to_six_month_occlusion", 27.5),
        ("longitudinal_hemodynamics_to_future_growth", 25.5),
        ("patient_family_disjoint_coil_mechanics_transport", 24.0),
        ("amplified_wall_motion_cfd_growth_mechanism", 23.5),
        ("coil_mechanics_to_actual_followup_occlusion", 23.0),
        ("particle_regime_guided_therapeutic_delivery", 22.5),
    ]
    if (
        mechanistic["status"]
        != "fresh_problem_level_batch_rejected_best_27_5_no_same_patient_mechanics_response_outcome_join"
        or mechanistic["audit_document"]
        != "docs/mechanistic-treatment-and-growth-asset-reappraisal-2026-08-12.md"
        or mechanistic["automatic_selection_threshold"] != 32.0
        or mechanistic["best_candidate_id"]
        != "injection_invariant_qa_to_six_month_occlusion"
        or mechanistic["best_score"] != 27.5
        or mechanistic["best_residual_novelty_score"] != 3.0
        or mechanistic["all_candidate_scores"]
        != [27.5, 25.5, 24.0, 23.5, 23.0, 22.5]
        or mechanistic["conditional_source_lead_count"] != 0
        or mechanistic["primary_problem_selected"] is not False
        or mechanistic["paper_identity_active"] is not False
        or mechanistic["coil_mechanics_doi"] != "10.1063/5.0312971"
        or mechanistic["coil_mechanics_synthetic_sacs"] != 500
        or mechanistic["coil_mechanics_reaction_force_source_r2"] != 0.74
        or mechanistic["coil_mechanics_elastic_energy_source_r2"] != 0.68
        or mechanistic["coil_mechanics_public_patient_geometry_device_outcome_join"]
        is not False
        or mechanistic["qa_occlusion_doi"] != "10.1136/jnis-2025-023416"
        or mechanistic["qa_occlusion_source_patients"] != 458
        or mechanistic["qa_occlusion_target_months"] != 6
        or mechanistic["qa_occlusion_source_auc_uncorrected"] != 0.60
        or mechanistic["qa_occlusion_source_auc_corrected"] != 0.79
        or mechanistic["qa_occlusion_public_patient_rows_images_split"] is not False
        or mechanistic["longitudinal_growth_aneurysms"] != 34
        or mechanistic["longitudinal_growth_matched_pairs"] != 17
        or mechanistic["longitudinal_growth_timepoints_per_aneurysm"] != 3
        or mechanistic["longitudinal_growth_public_image_mesh_cfd_manifest"]
        is not False
        or mechanistic["amplified_wall_motion_growing_cases"] != 6
        or mechanistic["amplified_wall_motion_stable_cases"] != 6
        or mechanistic["amplified_wall_motion_public_field_motion_growth_asset"]
        is not False
        or mechanistic["automated_initiation_cases"] != 42
        or mechanistic["automated_initiation_initial_failures_manually_resolved"]
        != 5
        or mechanistic["automated_initiation_public_casewise_failure_contract"]
        is not False
        or mechanistic["particle_transport_idealized_anatomies"] != 1
        or mechanistic["particle_transport_configurations"] != 28
        or mechanistic["particle_transport_clinical_outcome_asset"] is not False
        or mechanistic[
            "same_patient_geometry_device_immediate_response_fixed_time_outcome_join_public"
        ]
        is not False
        or [
            (item.get("id"), item.get("total"))
            for item in mechanistic["candidates"]
        ]
        != expected_mechanistic_candidates
        or any(
            item.get("critical_axis_pass") is not False
            or item.get("decision") in (None, "")
            for item in mechanistic["candidates"]
        )
        or any(
            mechanistic[key] is not False
            for key in [
                "subscription_full_text_accessed",
                "supplement_payload_accessed",
                "patient_image_or_geometry_payload_accessed",
                "clinical_row_or_device_payload_accessed",
                "historical_surface_vector_source_score_or_job_relabelled",
                "historical_surface_vector_p0_repaired_or_rerun",
                "p0_registered", "p1_registered", "method_selected",
                "architecture_selected",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "login_node_gpu_command_executed",
                "junjinyong_accessed", "source_watch_added",
            ]
        )
        or mechanistic["surface_vector_question_retained_as_inactive_hypothesis"]
        is not True
        or mechanistic["scientific_server_queried"] is not True
        or mechanistic["execution_server"] != "introai9"
        or mechanistic["next_allowed_action"]
        != "fresh_unrelated_problem_level_source_or_versioned_same_patient_mechanics_response_outcome_asset_reaudit_only_no_payload_p0_model_or_compute"
    ):
        raise ProtocolError(
            "The mechanistic-treatment/growth batch must remain rejected: source-reported "
            "mechanics, QA, growth, wall-motion and transport results cannot be joined or "
            "relabelled as AURORA evidence, and no payload, P0, method or compute may open."
    )
    checks.append("mechanistic treatment and growth asset non-admission boundary")

    server_inventory = problem_selection["introai9_dataset_inventory_audit"]
    _require_keys(
        server_inventory,
        [
            "status", "requested_by_user", "read_only_audit",
            "login_endpoints_attempted", "tcp_port_22_reachable_endpoints",
            "public_key_authentication_confirmed_endpoints",
            "authenticated_account", "remote_shell_listing_obtained",
            "sftp_listing_obtained", "remote_command_output_lines",
            "known_project_root_from_prior_successful_audit",
            "prior_bounded_inventory_confirmed_aneurysm_asset_traces",
            "prior_intra_repository_skeleton_observed",
            "prior_intra_mesh_payload_verified",
            "prior_deep_candidate_manifest_search_completed",
            "current_dataset_presence_or_absence_determined",
            "current_direction_verified_train_cases",
            "current_direction_verified_validation_cases",
            "current_direction_verified_test_cases",
            "same_patient_geometry_device_immediate_response_outcome_dataset_verified",
            "pbs_job_submitted", "scheduler_queried",
            "login_node_gpu_command_executed", "gpu_used",
            "files_transferred", "junjinyong_accessed", "verdict",
            "next_allowed_action",
        ],
        "introai9 dataset inventory audit",
    )
    if (
        server_inventory["status"] != "execution_incomplete_no_asset_verdict"
        or server_inventory["requested_by_user"] is not True
        or server_inventory["read_only_audit"] is not True
        or server_inventory["login_endpoints_attempted"] != 2
        or server_inventory["tcp_port_22_reachable_endpoints"] != 2
        or server_inventory["public_key_authentication_confirmed_endpoints"] != 1
        or server_inventory["authenticated_account"] != "introai9"
        or server_inventory["remote_command_output_lines"] != 0
        or server_inventory["known_project_root_from_prior_successful_audit"]
        != "/home/introai9/AAAI"
        or server_inventory["prior_bounded_inventory_confirmed_aneurysm_asset_traces"]
        is not True
        or server_inventory["prior_intra_repository_skeleton_observed"] is not True
        or server_inventory["verdict"]
        != "inventory_incomplete_no_dataset_can_be_claimed_secured_or_absent"
        or server_inventory["next_allowed_action"]
        != "administrator_or_service_recovery_then_new_bounded_read_only_exact_path_inventory_no_recursive_repair_loop"
        or any(
            server_inventory[key] is not False
            for key in [
                "remote_shell_listing_obtained", "sftp_listing_obtained",
                "prior_intra_mesh_payload_verified",
                "prior_deep_candidate_manifest_search_completed",
                "current_dataset_presence_or_absence_determined",
                "same_patient_geometry_device_immediate_response_outcome_dataset_verified",
                "pbs_job_submitted", "scheduler_queried",
                "login_node_gpu_command_executed", "gpu_used",
                "files_transferred", "junjinyong_accessed",
            ]
        )
        or any(
            server_inventory[key] != 0
            for key in [
                "current_direction_verified_train_cases",
                "current_direction_verified_validation_cases",
                "current_direction_verified_test_cases",
            ]
        )
    ):
        raise ProtocolError(
            "The introai9 inventory must remain execution-incomplete and no-verdict: "
            "port reachability or public-key authentication cannot be relabelled as a "
            "dataset listing, and no PBS, GPU, transfer, or junjinyong action may open."
        )
    checks.append("introai9 incomplete dataset-inventory no-verdict boundary")

    asset_ledger = problem_selection["dataset_asset_state_ledger"]
    _require_keys(
        asset_ledger,
        [
            "status", "audit_document", "historical_named_holding_records",
            "historical_holdings_absent_claim",
            "current_introai9_exact_path_inventory_complete",
            "current_introai9_presence_or_absence_verdict",
            "public_git_raw_patient_mesh_or_field_payload_count",
            "active_dataset_count", "active_train_cases",
            "active_validation_cases", "active_test_cases",
            "active_p0_count", "active_p1_count", "active_model_count",
            "active_gpu_job_count", "active_outer_test_count",
            "registered_scientific_p0_pending_execution_envelope_count",
            "blanket_dataset_rejection_claim_allowed", "reason_taxonomy",
            "holdings", "next_allowed_action",
        ],
        "dataset asset state ledger",
    )
    expected_holding_status = {
        "aneumo": "performance_gate_failed",
        "benchanxplore": "discovery_used_not_fresh_confirmation",
        "cmha": "asset_linkage_gate_failed",
        "aneux": "execution_incomplete_no_verdict",
        "aneug_flow": "execution_incomplete_no_verdict",
        "aneurisk": "execution_incomplete_no_verdict",
    }
    expected_reason_taxonomy = [
        "performance_gate_failed",
        "asset_linkage_gate_failed",
        "execution_incomplete_no_verdict",
        "task_mismatch",
        "controlled_or_terms_pending",
        "discovery_used_not_fresh_confirmation",
        "active_assignment_zero",
    ]
    if (
        asset_ledger["status"]
        != "historical_holdings_current_inventory_scientific_admission_and_active_assignment_are_separate"
        or asset_ledger["audit_document"]
        != "docs/data-asset-state-ledger-2026-08-12.md"
        or asset_ledger["historical_named_holding_records"] != 6
        or asset_ledger["historical_holdings_absent_claim"] is not False
        or asset_ledger["current_introai9_exact_path_inventory_complete"] is not False
        or asset_ledger["current_introai9_presence_or_absence_verdict"] is not False
        or asset_ledger["public_git_raw_patient_mesh_or_field_payload_count"] != 0
        or asset_ledger["reason_taxonomy"] != expected_reason_taxonomy
        or {item["id"]: item["scientific_status"] for item in asset_ledger["holdings"]}
        != expected_holding_status
        or any(item["active_role"] is not None for item in asset_ledger["holdings"])
        or asset_ledger["blanket_dataset_rejection_claim_allowed"] is not False
        or asset_ledger[
            "registered_scientific_p0_pending_execution_envelope_count"
        ] != 1
        or any(
            asset_ledger[key] != 0
            for key in (
                "active_dataset_count", "active_train_cases",
                "active_validation_cases", "active_test_cases",
                "active_p0_count", "active_p1_count", "active_model_count",
                "active_gpu_job_count", "active_outer_test_count",
            )
        )
        or asset_ledger["next_allowed_action"]
        != "after_external_service_change_run_bounded_read_only_exact_path_checksum_inventory_then_continue_fresh_problem_asset_admission_without_repairing_closed_jobs"
    ):
        raise ProtocolError(
            "Historical audited holdings, current introai9 inventory, scientific "
            "admission and active split assignment must remain separate; active zero "
            "cannot be relabelled as historical dataset absence or blanket rejection."
        )
    checks.append("historical holdings and active-assignment state separation")

    acquired_direction = problem_selection["acquired_asset_application_direction"]
    _require_keys(
        acquired_direction,
        [
            "status", "current_authority", "superseded_by", "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "candidate_dataset", "candidate_target", "candidate_failure_mechanism",
            "resolution_role", "cut_role",
            "flat_final_logit_consistency_allowed_as_proposal",
            "source_reported_lesions", "source_reported_patients",
            "source_reported_status_observed", "mesh_resolutions",
            "cut_configurations", "morphometric_features",
            "morphometric_feature_resolution", "official_code_head",
            "official_feature_code_publicly_available", "p0_v1_config",
            "p0_v1_config_sha256", "p0_v1_status",
            "p0_v1_post_result_repair", "p0_config",
            "p0_config_sha256", "p0_scientific_contract_registered",
            "p0_execution_envelope_frozen", "p0_exact_private_path_frozen",
            "p0_exact_manifest_sha256_frozen", "p0_executable", "p0_submitted",
            "p0_cpu_only", "p0_gpu_count", "p0_network_access_allowed",
            "p0_previous_downloader_or_reader_repaired", "p0_previous_job_rerun",
            "p0_previous_job_id", "p0_previous_scientific_checks_evaluated",
            "p0_nontriviality_required_count", "p0_nontriviality_total_count",
            "p0_decision_flip_primary", "p0_baseline_adequacy_required",
            "p0_external_sources_opened", "candidate_architecture_status",
            "candidate_architecture", "non_novel_components",
            "required_strong_baselines", "primary_evidence_roles", "candidates",
            "method_selected", "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "submission_identity_active", "paper_claim_active", "execution_server",
            "login_node_gpu_command_executed", "junjinyong_accessed",
            "next_allowed_action",
        ],
        "acquired-asset application direction",
    )
    expected_acquired_candidates = [
        ("aneux_factorized_nested_preprocessing_orbit_reliability", 33.0, True),
        ("benchanxplore_sac_local_transient_velocity_operator", 32.5, False),
        ("aneumo_multibc_steady_surrogate_reentry", 32.5, False),
        ("aneurisk_context_visualization_only", 29.5, False),
        ("aneug_aneurisk_structure_faithful_wss", 28.0, False),
        ("cmha_hemodynamic_incremental_value", 27.0, False),
    ]
    if (
        acquired_direction["status"]
        != "historical_schema_11_6_conditional_lead_superseded_pre_execution_by_direct_prior_reappraisal"
        or acquired_direction["current_authority"] is not False
        or acquired_direction["superseded_by"]
        != "aneux_reliability_direct_prior_reappraisal"
        or acquired_direction["audit_document"]
        != "docs/acquired-asset-application-direction-2026-08-12.md"
        or acquired_direction["automatic_selection_threshold"] != 32.0
        or acquired_direction["best_candidate_id"]
        != "aneux_factorized_nested_preprocessing_orbit_reliability"
        or acquired_direction["best_score"] != 33.0
        or acquired_direction["best_residual_novelty_score"] != 3.0
        or acquired_direction["all_candidate_scores"]
        != [33.0, 32.5, 32.5, 29.5, 28.0, 27.0]
        or acquired_direction["conditional_source_lead_count"] != 1
        or acquired_direction["candidate_dataset"] != "aneux_v1_0"
        or acquired_direction["candidate_target"]
        != "cross_sectional_rupture_status_association_not_future_risk"
        or acquired_direction["resolution_role"] != "nuisance_within_fixed_cut"
        or acquired_direction["cut_role"]
        != "information_set_change_with_permitted_parent_vessel_context_residual"
        or acquired_direction["flat_final_logit_consistency_allowed_as_proposal"]
        is not False
        or acquired_direction["source_reported_lesions"] != 750
        or acquired_direction["source_reported_patients"] != 605
        or acquired_direction["source_reported_status_observed"] != 735
        or acquired_direction["mesh_resolutions"] != 3
        or acquired_direction["cut_configurations"] != 4
        or acquired_direction["morphometric_features"] != 170
        or acquired_direction["morphometric_feature_resolution"] != "area-005_only"
        or acquired_direction["official_code_head"]
        != "a6b355e8f271e9a88399a2e432ed924d99b85d64"
        or acquired_direction["official_feature_code_publicly_available"] is not False
        or acquired_direction["p0_v1_config"] != "configs/aneux_nested_orbit_p0.json"
        or acquired_direction["p0_v1_config_sha256"]
        != "b82e3606ea76697dbdc44973a287538a436fe330c25edcd8bf9f113d147149c1"
        or acquired_direction["p0_v1_status"]
        != "superseded_pre_execution_zero_rows_zero_job_because_170_morphometrics_are_area_005_only"
        or acquired_direction["p0_v1_post_result_repair"] is not False
        or acquired_direction["p0_config"] != "configs/aneux_nested_orbit_p0_v2.json"
        or acquired_direction["p0_config_sha256"]
        != "86de76c4c7e4d493f12d2eb300e78647a74daf88e469102411f959982a07d0da"
        or acquired_direction["p0_scientific_contract_registered"] is not True
        or acquired_direction["p0_cpu_only"] is not True
        or acquired_direction["p0_gpu_count"] != 0
        or acquired_direction["p0_previous_job_id"] != "115177.ECE-util1"
        or acquired_direction["p0_previous_scientific_checks_evaluated"] != 0
        or acquired_direction["p0_nontriviality_required_count"] != 2
        or acquired_direction["p0_nontriviality_total_count"] != 2
        or acquired_direction["p0_decision_flip_primary"] is not False
        or acquired_direction["p0_baseline_adequacy_required"] is not True
        or acquired_direction["candidate_architecture_status"]
        != "development_hypothesis_only_unselected"
        or [
            (row.get("id"), row.get("total"), row.get("critical_axis_pass"))
            for row in acquired_direction["candidates"]
        ]
        != expected_acquired_candidates
        or acquired_direction["execution_server"] != "introai9"
        or acquired_direction["next_allowed_action"]
        != "after_external_service_change_run_one_bounded_exact_path_manifest_and_reader_preflight_then_freeze_p0_v2_execution_envelope_or_close_no_broad_search_no_old_job_repair"
        or any(
            acquired_direction[key] is not False
            for key in (
                "primary_problem_selected", "paper_identity_active",
                "p0_execution_envelope_frozen", "p0_exact_private_path_frozen",
                "p0_exact_manifest_sha256_frozen", "p0_executable", "p0_submitted",
                "p0_network_access_allowed",
                "p0_previous_downloader_or_reader_repaired", "p0_previous_job_rerun",
                "p0_external_sources_opened", "method_selected",
                "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "paper_claim_active",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
    ):
        raise ProtocolError(
            "The acquired-asset direction may retain exactly one factorized AneuX "
            "nested-orbit conditional lead and a non-executable CPU P0 scientific "
            "contract; flat cut invariance, old-job repair, method, GPU, outer test "
            "and paper claims remain forbidden."
        )
    p0_path = Path(__file__).resolve().parents[2] / acquired_direction["p0_config"]
    if (
        not p0_path.is_file()
        or hashlib.sha256(p0_path.read_bytes()).hexdigest()
        != acquired_direction["p0_config_sha256"]
    ):
        raise ProtocolError("The AneuX nested-orbit P0 contract hash changed.")
    checks.append("historical acquired-asset AneuX nested-orbit boundary")

    aneux_reappraisal = problem_selection[
        "aneux_reliability_direct_prior_reappraisal"
    ]
    _require_keys(
        aneux_reappraisal,
        [
            "status", "audit_document", "supersedes_current_authority_of",
            "historical_schema_11_6_score_preserved",
            "historical_score_relabelled", "automatic_selection_threshold",
            "residual_novelty_floor", "best_candidate_id", "best_score",
            "best_residual_novelty_score", "all_candidate_scores",
            "conditional_source_lead_count", "direct_prior_dois",
            "diffusionnet_arxiv", "aneux_cut_robustness_already_studied",
            "aneux_dome_cut1_surface_classification_already_studied",
            "generic_same_unit_perturbation_reliability_already_studied",
            "generic_preprocessing_multiverse_already_studied",
            "implementation_source_qualified_patient_grouping_matches_contract",
            "implementation_source_qualified_lesion_identity_matches_contract",
            "implementation_single_connected_open_surface_gate_present",
            "p0_v1_config", "p0_v1_config_sha256", "p0_v2_config",
            "p0_v2_config_sha256", "p0_v1_or_v2_modified",
            "p0_v2_repaired", "p0_v2_executed", "p0_v3_created",
            "primary_problem_selected", "p0_active", "p1_registered",
            "method_selected", "architecture_selected",
            "scientific_server_queried", "gpu_training_authorized",
            "outer_test_authorized", "paper_claim_active",
            "submission_identity_active", "execution_server",
            "login_node_gpu_command_executed", "junjinyong_accessed",
            "candidates", "next_allowed_action",
        ],
        "AneuX reliability direct-prior reappraisal",
    )
    expected_aneux_reappraisal_candidates = [
        ("aneux_factorized_nested_preprocessing_orbit_reliability", 32.0, False),
        ("reliability_selected_robust_surface_signature", 31.5, False),
        ("aneux_preprocessing_multiverse_aggregation", 31.0, False),
        ("orbit_disagreement_abstention", 30.5, False),
        ("adaptive_cut_or_view_selection", 29.5, False),
        ("flat_consistency_across_all_cuts", 27.0, False),
    ]
    expected_aneux_direct_prior_dois = [
        "10.3389/fneur.2022.809391",
        "10.3389/fphys.2024.1293380",
        "10.1038/s41598-022-14178-x",
        "10.1038/s41598-023-45477-6",
        "10.1162/imag_a_00523",
    ]
    if (
        aneux_reappraisal["status"]
        != "fresh_direct_prior_batch_rejected_best_32_residual_novelty_2_below_2_5_floor_and_frozen_p0_v2_not_executed"
        or aneux_reappraisal["audit_document"]
        != "docs/aneux-reliability-direct-prior-reappraisal-2026-08-12.md"
        or aneux_reappraisal["supersedes_current_authority_of"]
        != "acquired_asset_application_direction"
        or aneux_reappraisal["historical_schema_11_6_score_preserved"] != 33.0
        or aneux_reappraisal["historical_score_relabelled"] is not False
        or aneux_reappraisal["automatic_selection_threshold"] != 32.0
        or aneux_reappraisal["residual_novelty_floor"] != 2.5
        or aneux_reappraisal["best_candidate_id"]
        != "aneux_factorized_nested_preprocessing_orbit_reliability"
        or aneux_reappraisal["best_score"] != 32.0
        or aneux_reappraisal["best_residual_novelty_score"] != 2.0
        or aneux_reappraisal["all_candidate_scores"]
        != [32.0, 31.5, 31.0, 30.5, 29.5, 27.0]
        or aneux_reappraisal["conditional_source_lead_count"] != 0
        or aneux_reappraisal["direct_prior_dois"]
        != expected_aneux_direct_prior_dois
        or aneux_reappraisal["diffusionnet_arxiv"] != "2012.00888"
        or aneux_reappraisal["p0_v1_config"]
        != "configs/aneux_nested_orbit_p0.json"
        or aneux_reappraisal["p0_v1_config_sha256"]
        != "b82e3606ea76697dbdc44973a287538a436fe330c25edcd8bf9f113d147149c1"
        or aneux_reappraisal["p0_v2_config"]
        != "configs/aneux_nested_orbit_p0_v2.json"
        or aneux_reappraisal["p0_v2_config_sha256"]
        != "86de76c4c7e4d493f12d2eb300e78647a74daf88e469102411f959982a07d0da"
        or aneux_reappraisal["execution_server"] != "introai9"
        or aneux_reappraisal["next_allowed_action"]
        != "fresh_problem_level_audit_over_existing_documented_assets_no_aneux_p0_v2_repair_or_compute"
        or [
            (row.get("id"), row.get("total"), row.get("critical_axis_pass"))
            for row in aneux_reappraisal["candidates"]
        ] != expected_aneux_reappraisal_candidates
        or any(
            aneux_reappraisal[key] is not True
            for key in (
                "aneux_cut_robustness_already_studied",
                "aneux_dome_cut1_surface_classification_already_studied",
                "generic_same_unit_perturbation_reliability_already_studied",
                "generic_preprocessing_multiverse_already_studied",
            )
        )
        or any(
            aneux_reappraisal[key] is not False
            for key in (
                "implementation_source_qualified_patient_grouping_matches_contract",
                "implementation_source_qualified_lesion_identity_matches_contract",
                "implementation_single_connected_open_surface_gate_present",
                "p0_v1_or_v2_modified", "p0_v2_repaired", "p0_v2_executed",
                "p0_v3_created", "primary_problem_selected", "p0_active",
                "p1_registered", "method_selected", "architecture_selected",
                "scientific_server_queried", "gpu_training_authorized",
                "outer_test_authorized", "paper_claim_active",
                "submission_identity_active", "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
    ):
        raise ProtocolError(
            "The AneuX reliability direction must remain source-rejected before "
            "execution: direct prior closes the novelty floor and the frozen v1/v2 "
            "contracts cannot be repaired, executed, or promoted."
        )
    for config_key, hash_key in (
        ("p0_v1_config", "p0_v1_config_sha256"),
        ("p0_v2_config", "p0_v2_config_sha256"),
    ):
        frozen_path = Path(__file__).resolve().parents[2] / aneux_reappraisal[config_key]
        if (
            not frozen_path.is_file()
            or hashlib.sha256(frozen_path.read_bytes()).hexdigest()
            != aneux_reappraisal[hash_key]
        ):
            raise ProtocolError("A frozen AneuX P0 contract changed after rejection.")
    checks.append("AneuX reliability direct-prior rejection and frozen-contract boundary")

    response_fidelity = problem_selection["aneumo_response_fidelity_source_audit"]
    _require_keys(
        response_fidelity,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "residual_novelty_floor", "best_candidate_id", "best_score",
            "best_residual_novelty_score", "all_candidate_scores",
            "conditional_source_lead_count", "candidate_dataset",
            "candidate_estimand", "application_identity",
            "candidate_failure_mechanism", "candidate_failure_observed",
            "dataset_cache_sha256", "staging_config", "staging_config_sha256",
            "historical_scaling_result", "historical_scaling_result_sha256",
            "historical_scaling_result_recomputed", "historical_scaling_exponent",
            "historical_velocity_response_residual",
            "historical_velocity_response_ci95", "compact_base_families",
            "compact_cases", "conditions_per_case", "nodes_per_case",
            "train_validation_test_base_families",
            "current_confirmation_family_count",
            "required_locked_confirmation_family_count",
            "validation_or_test_fields_read_for_this_audit",
            "v1e_absolute_train_relative_l2",
            "v1e_absolute_validation_relative_l2", "v1e_response_relative_l2",
            "v1e_repaired_or_rerun", "direct_prior_identifiers",
            "non_novel_components", "primary_response_endpoints",
            "secondary_response_endpoints", "p0_v1_config",
            "p0_v1_config_sha256", "p0_v1_superseded_pre_execution",
            "p0_v1_supersession_reason", "p0_config", "p0_config_sha256",
            "p0_reference_evaluator", "p0_reference_evaluator_sha256",
            "p0_pbs_wrapper", "p0_pbs_wrapper_sha256",
            "p0_reference_evaluator_synthetic_validation_passed",
            "p0_current_config_refuses_before_cache_access",
            "p0_coordinate_half_metric_flow_stratified_by_family",
            "p0_coordinate_half_magnitude_gate_registered",
            "p0_observed_cache_bytes_hashed",
            "p0_host_container_cache_path_identity_preserved",
            "p0_pre_execution_red_team_finalized",
            "p0_future_metric_or_threshold_change_requires_new_evidence_version",
            "p0_registered_bootstrap_replicates",
            "p0_registered_scientific_check_count",
            "p0_pbs_wrapper_submittable_now",
            "p0_scientific_contract_registered", "p0_status", "p0_method_free",
            "p0_train_only", "p0_exact_private_cache_path_frozen",
            "p0_execution_envelope_frozen", "p0_executable", "p0_submitted",
            "p0_scientific_checks_evaluated", "p1_registered",
            "p1_requires_field_error_matched_response_mismatch",
            "p1_design_v1_template", "p1_design_v1_template_sha256",
            "p1_design_v1_validator", "p1_design_v1_validator_sha256",
            "p1_design_v1_superseded_pre_execution",
            "p1_design_template", "p1_design_template_sha256",
            "p1_design_validator", "p1_design_validator_sha256",
            "p1_design_template_status",
            "p1_design_template_non_authoritative",
            "p1_design_family_crossfit_uses_historical_20_train_families_only",
            "p1_design_response_blind_iso_error_matching",
            "p1_design_duplicate_free_checkpoint_assignment",
            "p1_design_predeclared_primary_pair_level_endpoint_cells",
            "p1_design_predeclared_nonrescuing_sensitivity_cells",
            "p1_design_field_equivalence_margin_log_ratio",
            "p1_design_power_law_competence_margin_log_ratio",
            "p1_design_median_co_primary_and_nonrescuing_sensitivity_roles",
            "p1_design_contrast_direction_and_seed_ties_explicit",
            "p1_design_crossfit_exact_null_inference_allowed",
            "p1_design_confirmatory_or_paper_efficacy_claim_allowed",
            "p1_design_formal_power_claim_allowed",
            "p1_design_minimum_multiplicative_response_gap",
            "p1_design_minimum_same_direction_seeds",
            "p1_design_training_seed_count", "p1_design_total_gpu_hour_cap",
            "p1_design_real_p0_required_check_count",
            "p1_design_real_p0_observed_check_count",
            "p1_design_validator_synthetic_tests_passed",
            "candidate_architecture_status", "candidate_architecture",
            "primary_problem_selected", "method_selected",
            "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "paper_claim_active", "submission_identity_active",
            "clinical_risk_or_patient_specific_physiology_claim_allowed",
            "execution_server", "pbs_only", "login_node_gpu_command_executed",
            "junjinyong_accessed", "candidates", "next_allowed_action",
        ],
        "Aneumo response-fidelity source audit",
    )
    expected_response_candidates = [
        ("field_error_matched_multi_flow_response_fidelity", 34.0, True),
        ("generic_anchor_state_residual_operator", 31.5, False),
        ("derivative_informed_aneurysm_operator", 31.0, False),
        ("multi_flow_condition_diversity_benchmark", 29.0, False),
        ("geometry_only_full_field_reentry", 28.0, False),
        ("multi_flow_rupture_response_phenotype", 22.0, False),
    ]
    expected_response_priors = [
        "arxiv:2505.14717",
        "pmid:32008209",
        "neurips_2025_deltaphi",
        "doi:10.1016/j.jcp.2023.112555",
        "arxiv:2512.14086",
        "doi:10.1038/s41746-026-02404-z",
        "doi:10.1016/j.cmpb.2026.109308",
        "pmid:30203115",
    ]
    if (
        response_fidelity["status"]
        != "conditional_source_lead_with_registered_non_executable_method_free_p0_no_primary_method_or_claim"
        or response_fidelity["audit_document"]
        != "docs/response-faithful-hemodynamic-surrogate-source-audit-2026-08-12.md"
        or response_fidelity["automatic_selection_threshold"] != 32.0
        or response_fidelity["residual_novelty_floor"] != 2.5
        or response_fidelity["best_candidate_id"]
        != "field_error_matched_multi_flow_response_fidelity"
        or response_fidelity["best_score"] != 34.0
        or response_fidelity["best_residual_novelty_score"] != 2.5
        or response_fidelity["all_candidate_scores"]
        != [34.0, 31.5, 31.0, 29.0, 28.0, 22.0]
        or response_fidelity["conditional_source_lead_count"] != 1
        or response_fidelity["candidate_dataset"] != "aneumo_verified_compact_cache"
        or response_fidelity["candidate_estimand"]
        != "reference_velocity_multi_flow_response_fidelity_not_clinical_outcome"
        or response_fidelity["dataset_cache_sha256"]
        != "9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9"
        or response_fidelity["staging_config"] != "configs/aneumo_g2_pilot_v1.json"
        or response_fidelity["staging_config_sha256"]
        != "f2b027c5f14107531ac1ae33eafab76513bcbdf49ad908c9a35641ae80181b7d"
        or response_fidelity["historical_scaling_result"]
        != "results/aneumo_scaling_audit_20260803.json"
        or response_fidelity["historical_scaling_result_sha256"]
        != "d1b8bfba9b904264d4e495d98b833a6f639b6438869e854a7c07ab88269562ca"
        or response_fidelity["historical_scaling_exponent"] != 1.075
        or response_fidelity["historical_velocity_response_residual"]
        != 0.21116332234297996
        or response_fidelity["historical_velocity_response_ci95"]
        != [0.20013078657046568, 0.22433041263796377]
        or [
            response_fidelity["compact_base_families"],
            response_fidelity["compact_cases"],
            response_fidelity["conditions_per_case"],
            response_fidelity["nodes_per_case"],
        ] != [32, 64, 8, 4096]
        or response_fidelity["train_validation_test_base_families"] != [20, 6, 6]
        or response_fidelity["current_confirmation_family_count"] != 6
        or response_fidelity["required_locked_confirmation_family_count"] != 50
        or [
            response_fidelity["v1e_absolute_train_relative_l2"],
            response_fidelity["v1e_absolute_validation_relative_l2"],
            response_fidelity["v1e_response_relative_l2"],
        ] != [0.77221, 0.87796, 0.94918]
        or response_fidelity["direct_prior_identifiers"] != expected_response_priors
        or response_fidelity["primary_response_endpoints"]
        != ["paired_response_relative_l2", "discrete_tangent_relative_l2"]
        or response_fidelity["p0_v1_config"]
        != "configs/aneumo_response_fidelity_p0.json"
        or response_fidelity["p0_v1_config_sha256"]
        != "07c0c89799e04fbee88a1218383aa7b7fd8fc3a5ab8d7bcb15d286195571135f"
        or response_fidelity["p0_v1_supersession_reason"]
        != "spearman_only_coordinate_half_gate_can_pass_arbitrary_response_magnitude_scaling"
        or response_fidelity["p0_config"]
        != "configs/aneumo_response_fidelity_p0_v2.json"
        or response_fidelity["p0_config_sha256"]
        != "b82b3bfd3d83713f375378f471ec506e7b8437fd470e98366534d4cb1d021381"
        or response_fidelity["p0_reference_evaluator"]
        != "src/aurora/aneumo_response_fidelity_p0.py"
        or response_fidelity["p0_reference_evaluator_sha256"]
        != "3f9667329b2f7f61850eddbd5b118c8cab0520cccb86a3382ecfebf6cc292790"
        or response_fidelity["p0_pbs_wrapper"]
        != "cluster/pbs_aneumo_response_fidelity_p0.pbs"
        or response_fidelity["p0_pbs_wrapper_sha256"]
        != "d895fa85926cdbd70f7d9b152cc8ace9e91eced1a943d2889c5c398511d6b6ee"
        or response_fidelity["p0_registered_bootstrap_replicates"] != 5000
        or response_fidelity["p0_registered_scientific_check_count"] != 11
        or response_fidelity["p0_status"]
        != "registered_non_executable_pending_external_service_change_and_exact_private_cache_path"
        or response_fidelity["p1_design_v1_template"]
        != "configs/aneumo_response_fidelity_p1_template_v1.json"
        or response_fidelity["p1_design_v1_template_sha256"]
        != "07d7b89e4a77331fe3dda7f4fe716ef1efaab3561519e5654f47a2841ad32d06"
        or response_fidelity["p1_design_v1_validator"]
        != "src/aurora/aneumo_response_fidelity_p1_template.py"
        or response_fidelity["p1_design_v1_validator_sha256"]
        != "b14e4c8dcf9a236c5bfeb30b559b5799409d701e42a119f9ba5967394394d9fa"
        or response_fidelity["p1_design_template"]
        != "configs/aneumo_response_fidelity_p1_template_v2.json"
        or response_fidelity["p1_design_template_sha256"]
        != "67cbb858b0ffaaca9f6ee289872a4f2bd1d499deca95697b149bea86e5386918"
        or response_fidelity["p1_design_validator"]
        != "src/aurora/aneumo_response_fidelity_p1_template_v2.py"
        or response_fidelity["p1_design_validator_sha256"]
        != "d77cc99e9646ef64da4abfac441d0947101e634fb087d2e3a9b52ce1d3317530"
        or response_fidelity["p1_design_template_status"]
        != "draft_non_authoritative_blocked_on_real_p0_v2_all_11_pass"
        or response_fidelity["p1_design_predeclared_primary_pair_level_endpoint_cells"]
        != 2
        or response_fidelity["p1_design_predeclared_nonrescuing_sensitivity_cells"]
        != 4
        or response_fidelity["p1_design_field_equivalence_margin_log_ratio"]
        != 0.009950330853168092
        or response_fidelity["p1_design_power_law_competence_margin_log_ratio"]
        != 0.01980262729617973
        or response_fidelity["p1_design_minimum_multiplicative_response_gap"] != 0.1
        or response_fidelity["p1_design_minimum_same_direction_seeds"] != 4
        or response_fidelity["p1_design_training_seed_count"] != 5
        or response_fidelity["p1_design_total_gpu_hour_cap"] != 160.0
        or response_fidelity["p1_design_real_p0_required_check_count"] != 11
        or response_fidelity["p1_design_real_p0_observed_check_count"] != 0
        or response_fidelity["candidate_architecture_status"]
        != "mechanism_linked_hypothesis_only_unselected"
        or response_fidelity["execution_server"] != "introai9"
        or response_fidelity["pbs_only"] is not True
        or response_fidelity["p0_scientific_checks_evaluated"] != 0
        or [
            (row.get("id"), row.get("total"), row.get("critical_axis_pass"))
            for row in response_fidelity["candidates"]
        ] != expected_response_candidates
        or any(
            response_fidelity[key] is not True
            for key in (
                "p0_scientific_contract_registered", "p0_method_free",
                "p0_train_only",
                "p0_v1_superseded_pre_execution",
                "p0_reference_evaluator_synthetic_validation_passed",
                "p0_current_config_refuses_before_cache_access",
                "p0_coordinate_half_metric_flow_stratified_by_family",
                "p0_coordinate_half_magnitude_gate_registered",
                "p0_observed_cache_bytes_hashed",
                "p0_host_container_cache_path_identity_preserved",
                "p0_pre_execution_red_team_finalized",
                "p0_future_metric_or_threshold_change_requires_new_evidence_version",
                "p1_requires_field_error_matched_response_mismatch",
                "p1_design_v1_superseded_pre_execution",
                "p1_design_template_non_authoritative",
                "p1_design_family_crossfit_uses_historical_20_train_families_only",
                "p1_design_response_blind_iso_error_matching",
                "p1_design_duplicate_free_checkpoint_assignment",
                "p1_design_median_co_primary_and_nonrescuing_sensitivity_roles",
                "p1_design_contrast_direction_and_seed_ties_explicit",
                "p1_design_validator_synthetic_tests_passed",
            )
        )
        or any(
            response_fidelity[key] is not False
            for key in (
                "candidate_failure_observed", "historical_scaling_result_recomputed",
                "validation_or_test_fields_read_for_this_audit",
                "v1e_repaired_or_rerun", "p0_exact_private_cache_path_frozen",
                "p0_execution_envelope_frozen", "p0_executable", "p0_submitted",
                "p0_pbs_wrapper_submittable_now",
                "p1_registered", "primary_problem_selected", "method_selected",
                "p1_design_crossfit_exact_null_inference_allowed",
                "p1_design_confirmatory_or_paper_efficacy_claim_allowed",
                "p1_design_formal_power_claim_allowed",
                "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "paper_claim_active", "submission_identity_active",
                "clinical_risk_or_patient_specific_physiology_claim_allowed",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or response_fidelity["next_allowed_action"]
        != "after_external_service_change_run_one_bounded_exact_cache_path_checksum_preflight_then_cpu_only_method_free_p0_no_model_gpu_validation_test_or_claim"
    ):
        raise ProtocolError(
            "The Aneumo response-fidelity direction must remain a conditional source "
            "lead with a method-free, train-only, non-executable P0; direct-prior "
            "components, architecture, GPU, validation/test, and paper claims stay closed."
        )
    for path_key, hash_key in (
        ("p0_v1_config", "p0_v1_config_sha256"),
        ("p0_config", "p0_config_sha256"),
    ):
        response_p0_path = Path(__file__).resolve().parents[2] / response_fidelity[path_key]
        if (
            not response_p0_path.is_file()
            or hashlib.sha256(response_p0_path.read_bytes()).hexdigest()
            != response_fidelity[hash_key]
        ):
            raise ProtocolError("The registered Aneumo response-fidelity P0 contract changed.")
    for path_key, hash_key in (
        ("p0_reference_evaluator", "p0_reference_evaluator_sha256"),
        ("p0_pbs_wrapper", "p0_pbs_wrapper_sha256"),
        ("p1_design_v1_template", "p1_design_v1_template_sha256"),
        ("p1_design_v1_validator", "p1_design_v1_validator_sha256"),
        ("p1_design_template", "p1_design_template_sha256"),
        ("p1_design_validator", "p1_design_validator_sha256"),
    ):
        implementation_path = (
            Path(__file__).resolve().parents[2] / response_fidelity[path_key]
        )
        if (
            not implementation_path.is_file()
            or hashlib.sha256(implementation_path.read_bytes()).hexdigest()
            != response_fidelity[hash_key]
        ):
            raise ProtocolError(
                "The registered Aneumo response-fidelity P0 implementation changed."
            )
    checks.append("Aneumo response-fidelity conditional lead and fail-closed P0 boundary")

    collision = problem_selection[
        "endovascular_collision_anticipation_and_release_reappraisal"
    ]
    _require_keys(
        collision,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_ids", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "cathaction_paper_arxiv", "cathaction_paper_reported_videos",
            "cathaction_paper_reported_action_collision_frames_approx",
            "cathaction_paper_reported_segmentation_masks_approx",
            "cathaction_source_domains", "challenge_reports_human_domain",
            "source_already_benchmarks_action_anticipation",
            "source_already_benchmarks_collision_detection",
            "source_already_benchmarks_segmentation",
            "source_already_benchmarks_phantom_to_animal_adaptation",
            "huggingface_exact_sha", "huggingface_last_modified",
            "huggingface_used_storage_bytes", "huggingface_public",
            "huggingface_gated", "huggingface_license_tag",
            "dataset_card_requests_download_form_and_license_agreement",
            "archive_count", "human_segmentation_archive_present",
            "human_collision_archive_present",
            "chronological_collision_onset_contract_declared",
            "warning_horizon_contract_declared",
            "complete_negative_sequence_contract_declared",
            "procedure_specimen_anatomy_identifiers_declared",
            "immutable_action_mask_collision_cross_archive_join_declared",
            "challenge_collision_warning_output_interface_declared",
            "candidates", "download_form_completed", "license_terms_accepted",
            "archive_payload_accessed", "image_or_label_payload_accessed",
            "source_watch_added",
            "surface_vector_question_retained_as_inactive_hypothesis",
            "historical_surface_vector_source_score_or_job_relabelled",
            "historical_surface_vector_p0_repaired_or_rerun", "p0_registered",
            "p1_registered", "method_selected", "architecture_selected",
            "scientific_server_queried", "gpu_training_authorized",
            "outer_test_authorized", "submission_identity_active",
            "execution_server", "login_node_gpu_command_executed",
            "junjinyong_accessed", "next_allowed_action",
        ],
        "endovascular collision anticipation and release reappraisal",
    )
    expected_collision_candidates = [
        ("pre_contact_collision_onset_anticipation", 26.5),
        ("phantom_to_animal_collision_calibration", 26.5),
        ("human_tool_segmentation_domain_generalization", 26.0),
        ("action_conditioned_collision_early_warning", 24.5),
        ("segmentation_conditioned_collision_detection", 24.0),
        ("aneurysm_specific_navigation_safety_transfer", 20.0),
    ]
    if (
        collision["status"]
        != "fresh_problem_level_batch_rejected_best_26_5_target_asset_unit_and_direct_prior_floors"
        or collision["audit_document"]
        != "docs/endovascular-collision-anticipation-and-release-contract-reappraisal-2026-08-12.md"
        or collision["automatic_selection_threshold"] != 32.0
        or collision["best_candidate_ids"]
        != [
            "pre_contact_collision_onset_anticipation",
            "phantom_to_animal_collision_calibration",
        ]
        or collision["best_score"] != 26.5
        or collision["best_residual_novelty_score"] != 3.0
        or collision["all_candidate_scores"]
        != [26.5, 26.5, 26.0, 24.5, 24.0, 20.0]
        or collision["conditional_source_lead_count"] != 0
        or collision["cathaction_paper_arxiv"] != "2408.13126"
        or collision["cathaction_paper_reported_videos"] != 569
        or collision["cathaction_paper_reported_action_collision_frames_approx"]
        != 500000
        or collision["cathaction_paper_reported_segmentation_masks_approx"]
        != 25000
        or collision["cathaction_source_domains"] != ["phantom", "live_animal"]
        or collision["huggingface_exact_sha"]
        != "8b04056f0f4fa4b04d8454728f000730af0d5560"
        or collision["huggingface_last_modified"] != "2026-05-18T11:16:32Z"
        or collision["huggingface_used_storage_bytes"] != 56678352136
        or collision["huggingface_license_tag"] != "cc-by-nc-sa-4.0"
        or collision["archive_count"] != 4
        or [(row["id"], row["total"]) for row in collision["candidates"]]
        != expected_collision_candidates
        or any(row["critical_axis_pass"] for row in collision["candidates"])
        or any(
            collision[key] is not True
            for key in (
                "challenge_reports_human_domain",
                "source_already_benchmarks_action_anticipation",
                "source_already_benchmarks_collision_detection",
                "source_already_benchmarks_segmentation",
                "source_already_benchmarks_phantom_to_animal_adaptation",
                "huggingface_public",
                "dataset_card_requests_download_form_and_license_agreement",
                "human_segmentation_archive_present", "source_watch_added",
                "surface_vector_question_retained_as_inactive_hypothesis",
            )
        )
        or any(
            collision[key] is not False
            for key in (
                "primary_problem_selected", "paper_identity_active",
                "huggingface_gated", "human_collision_archive_present",
                "chronological_collision_onset_contract_declared",
                "warning_horizon_contract_declared",
                "complete_negative_sequence_contract_declared",
                "procedure_specimen_anatomy_identifiers_declared",
                "immutable_action_mask_collision_cross_archive_join_declared",
                "challenge_collision_warning_output_interface_declared",
                "download_form_completed", "license_terms_accepted",
                "archive_payload_accessed", "image_or_label_payload_accessed",
                "historical_surface_vector_source_score_or_job_relabelled",
                "historical_surface_vector_p0_repaired_or_rerun",
                "p0_registered", "p1_registered", "method_selected",
                "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or collision["execution_server"] != "introai9"
        or collision["next_allowed_action"]
        != "fresh_unrelated_problem_level_source_or_versioned_collision_onset_and_independent_unit_contract_reaudit_only_no_terms_payload_p0_model_or_compute"
    ):
        raise ProtocolError(
            "The endovascular collision-anticipation batch must remain rejected: "
            "current-frame detection and human segmentation do not identify a "
            "pre-contact warning target or authorize payload, model, or compute."
        )
    checks.append("endovascular collision-anticipation non-admission boundary")

    molecular = problem_selection[
        "molecular_biomarker_and_treatment_specific_outcome_reappraisal"
    ]
    _require_keys(
        molecular,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "pxd024615_source_doi", "pxd024615_accession",
            "pxd024615_cohort_i_samples", "pxd024615_cohort_i_ruptured",
            "pxd024615_cohort_i_unruptured", "pxd024615_cohort_i_controls",
            "pxd024615_cohort_ii_samples", "pxd024615_cohort_ii_ruptured",
            "pxd024615_cohort_ii_unruptured", "pxd024615_cohort_ii_controls",
            "pxd024615_ev1_name", "pxd024615_ev1_bytes", "pxd024615_ev1_md5",
            "pxd024615_ev2_name", "pxd024615_ev2_bytes", "pxd024615_ev2_md5",
            "pxd024615_source_3dra_reviewed",
            "pxd024615_public_3dra_image_release_identified",
            "pxd024615_future_event_timeline_released",
            "pxd024615_source_results_reproduced_by_aurora",
            "pxd013442_accession", "pxd013442_listed_files",
            "pxd013442_discovery_tissue_samples",
            "pxd013442_discovery_serum_samples",
            "pxd013442_samples_per_group_pool",
            "pxd013442_effective_discovery_biological_pools",
            "gse231922_accession", "gse231922_samples", "gse231922_smoking_ia",
            "gse231922_nonsmoking_ia", "gse231922_controls",
            "gse231922_future_rupture_endpoint_released", "treatment_source_doi",
            "treatment_source_patients", "treatment_source_coiling",
            "treatment_source_clipping", "treatment_source_ruptured_fraction",
            "treatment_source_external_validation",
            "treatment_source_public_patient_rows_identified",
            "treatment_source_is_counterfactual_effect_model", "candidates",
            "omics_spreadsheet_payload_downloaded",
            "mass_spectrometry_payload_downloaded", "sequencing_payload_downloaded",
            "patient_image_payload_downloaded", "clinical_row_table_downloaded",
            "surface_vector_question_retained_as_inactive_hypothesis",
            "historical_surface_vector_source_score_or_job_relabelled",
            "historical_surface_vector_p0_repaired_or_rerun", "p0_registered",
            "p1_registered", "method_selected", "architecture_selected",
            "scientific_server_queried", "gpu_training_authorized",
            "outer_test_authorized", "submission_identity_active",
            "execution_server", "login_node_gpu_command_executed",
            "junjinyong_accessed", "next_allowed_action",
        ],
        "molecular biomarker and treatment-specific outcome reappraisal",
    )
    expected_molecular_candidates = [
        ("cross_cohort_serum_proteomic_rupture_state_calibration", 31.0),
        ("morphology_conditioned_proteomic_incremental_value", 28.0),
        ("smoking_conditioned_plasma_mirna_mechanism", 27.0),
        ("treatment_specific_inhospital_outcome_recalibration", 27.0),
        ("pooled_tissue_serum_proteomic_reanalysis", 26.0),
        ("pre_event_imaging_proteomic_progression_prediction", 23.0),
    ]
    if (
        molecular["status"]
        != "fresh_problem_level_batch_rejected_best_31_direct_task_prior_and_missing_joint_temporal_asset"
        or molecular["audit_document"]
        != "docs/molecular-biomarker-and-treatment-specific-outcome-reappraisal-2026-08-12.md"
        or molecular["automatic_selection_threshold"] != 32.0
        or molecular["best_candidate_id"]
        != "cross_cohort_serum_proteomic_rupture_state_calibration"
        or molecular["best_score"] != 31.0
        or molecular["best_residual_novelty_score"] != 2.5
        or molecular["all_candidate_scores"]
        != [31.0, 28.0, 27.0, 27.0, 26.0, 23.0]
        or molecular["conditional_source_lead_count"] != 0
        or molecular["pxd024615_source_doi"] != "10.15252/emmm.202114713"
        or molecular["pxd024615_accession"] != "PXD024615"
        or [
            molecular["pxd024615_cohort_i_samples"],
            molecular["pxd024615_cohort_i_ruptured"],
            molecular["pxd024615_cohort_i_unruptured"],
            molecular["pxd024615_cohort_i_controls"],
            molecular["pxd024615_cohort_ii_samples"],
            molecular["pxd024615_cohort_ii_ruptured"],
            molecular["pxd024615_cohort_ii_unruptured"],
            molecular["pxd024615_cohort_ii_controls"],
        ] != [212, 55, 57, 100, 32, 6, 6, 20]
        or [
            molecular["pxd024615_ev1_name"],
            molecular["pxd024615_ev1_bytes"],
            molecular["pxd024615_ev1_md5"],
            molecular["pxd024615_ev2_name"],
            molecular["pxd024615_ev2_bytes"],
            molecular["pxd024615_ev2_md5"],
        ] != [
            "EMMM-14-e14713-s024.xlsx", 13784,
            "b22ecc3da824b8a72a767ff39cb649be",
            "EMMM-14-e14713-s022.xlsx", 13642,
            "5f9b9b933f8546659378a11264089735",
        ]
        or [
            molecular["pxd013442_accession"],
            molecular["pxd013442_listed_files"],
            molecular["pxd013442_discovery_tissue_samples"],
            molecular["pxd013442_discovery_serum_samples"],
            molecular["pxd013442_samples_per_group_pool"],
            molecular["pxd013442_effective_discovery_biological_pools"],
        ] != ["PXD013442", 42, 20, 20, 5, 4]
        or [
            molecular["gse231922_accession"], molecular["gse231922_samples"],
            molecular["gse231922_smoking_ia"],
            molecular["gse231922_nonsmoking_ia"],
            molecular["gse231922_controls"],
        ] != ["GSE231922", 30, 10, 10, 10]
        or [
            molecular["treatment_source_doi"],
            molecular["treatment_source_patients"],
            molecular["treatment_source_coiling"],
            molecular["treatment_source_clipping"],
            molecular["treatment_source_ruptured_fraction"],
        ] != ["10.1016/j.jocn.2026.112073", 436, 224, 212, 0.869]
        or [(row["id"], row["total"]) for row in molecular["candidates"]]
        != expected_molecular_candidates
        or any(row["critical_axis_pass"] for row in molecular["candidates"])
        or any(
            molecular[key] is not False
            for key in (
                "primary_problem_selected", "paper_identity_active",
                "pxd024615_public_3dra_image_release_identified",
                "pxd024615_future_event_timeline_released",
                "pxd024615_source_results_reproduced_by_aurora",
                "gse231922_future_rupture_endpoint_released",
                "treatment_source_external_validation",
                "treatment_source_public_patient_rows_identified",
                "treatment_source_is_counterfactual_effect_model",
                "omics_spreadsheet_payload_downloaded",
                "mass_spectrometry_payload_downloaded",
                "sequencing_payload_downloaded", "patient_image_payload_downloaded",
                "clinical_row_table_downloaded",
                "historical_surface_vector_source_score_or_job_relabelled",
                "historical_surface_vector_p0_repaired_or_rerun", "p0_registered",
                "p1_registered", "method_selected", "architecture_selected",
                "scientific_server_queried", "gpu_training_authorized",
                "outer_test_authorized", "submission_identity_active",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or molecular["pxd024615_source_3dra_reviewed"] is not True
        or molecular["surface_vector_question_retained_as_inactive_hypothesis"]
        is not True
        or molecular["execution_server"] != "introai9"
        or molecular["next_allowed_action"]
        != "fresh_unrelated_problem_level_source_or_whitelisted_joint_temporal_asset_audit_only_no_payload_p0_model_or_compute"
    ):
        raise ProtocolError(
            "The molecular-biomarker/treatment-outcome batch must remain rejected: "
            "public omics data do not create a new future-event imaging task, and "
            "the single-centre prognostic cohort cannot authorize a model or compute."
        )
    checks.append("molecular-biomarker and treatment-outcome non-admission boundary")

    structured = problem_selection[
        "structured_vessel_and_embargoed_4dflow_reappraisal"
    ]
    _require_keys(
        structured,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "venet_source_doi", "venet_dataset_repository",
            "venet_dataset_exact_head", "venet_code_exact_head",
            "venet_paper_reported_dataset_masks", "venet_exact_public_git_masks",
            "venet_public_source_mra_redistributed", "venet_full_dataset_contact_only",
            "venet_independent_test_reported",
            "venet_topology_discontinuity_acknowledged_by_source",
            "venet_topology_aware_loss_is_source_stated_future_work",
            "rsna_multitask_arxiv", "rsna_multitask_repository_exact_head",
            "rsna_multitask_series", "rsna_split_unit",
            "rsna_patient_grouped_split_explicit",
            "rsna_independent_dense_reference_test",
            "rsna_source_results_reproduced_by_aurora",
            "cmrx4dflow_repository_exact_head",
            "cmrx4dflow_reported_total_cases_lower_bound",
            "cmrx4dflow_reported_centers_lower_bound",
            "cmrx4dflow_regular_training_cases",
            "cmrx4dflow_regular_validation_cases",
            "cmrx4dflow_regular_test_cases", "cmrx4dflow_terms_accepted_by_aurora",
            "cmrx4dflow_payload_accessed", "cmrx4dflow_embargo_date",
            "isbi_2027_submission_deadline",
            "cmrx4dflow_embargo_after_submission_deadline",
            "cmrx4dflow_aneurysm_patient_rows_identified",
            "device_phantom_zenodo_record", "device_phantom_base_anatomies",
            "device_phantom_models", "device_phantom_acquisitions",
            "device_phantom_venc_per_model", "device_phantom_cardiac_phases",
            "device_phantom_human_patients", "candidates",
            "surface_vector_question_retained_as_inactive_hypothesis",
            "historical_surface_vector_source_score_or_job_relabelled",
            "historical_surface_vector_p0_repaired_or_rerun", "source_watch_added",
            "p0_registered", "p1_registered", "method_selected",
            "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "submission_identity_active", "execution_server",
            "login_node_gpu_command_executed", "junjinyong_accessed",
            "next_allowed_action",
        ],
        "structured vessel and embargoed 4D-flow reappraisal",
    )
    expected_structured_candidates = [
        ("device_phantom_venc_stable_hemodynamic_response", 27.5),
        ("topology_faithful_cerebral_vessel_segmentation_for_downstream_simulation", 27.0),
        ("reference_aware_multitask_aneurysm_segmentation", 27.0),
        ("patient_grouped_multimodal_rsna_multitask_revalidation", 26.5),
        ("venet_label_uncertainty_and_topology_audit", 26.0),
        ("aneurysm_specific_4dflow_reconstruction_under_shift", 21.0),
    ]
    if (
        structured["status"]
        != "fresh_problem_level_batch_rejected_best_27_5_unit_novelty_asset_and_schedule_floors"
        or structured["audit_document"]
        != "docs/structured-vessel-and-embargoed-4dflow-reappraisal-2026-08-12.md"
        or structured["automatic_selection_threshold"] != 32.0
        or structured["best_candidate_id"]
        != "device_phantom_venc_stable_hemodynamic_response"
        or structured["best_score"] != 27.5
        or structured["best_residual_novelty_score"] != 1.5
        or structured["all_candidate_scores"]
        != [27.5, 27.0, 27.0, 26.5, 26.0, 21.0]
        or structured["conditional_source_lead_count"] != 0
        or structured["venet_source_doi"] != "10.1038/s41598-026-54176-x"
        or structured["venet_dataset_exact_head"]
        != "c233ab9074f2e531028d8485794dd873e0b23b29"
        or structured["venet_code_exact_head"]
        != "7c9cf0f2f3bde20ad76082ae306cd9b0c4dcb86f"
        or structured["venet_paper_reported_dataset_masks"] != 200
        or structured["venet_exact_public_git_masks"] != 20
        or structured["rsna_multitask_arxiv"] != "2606.26706"
        or structured["rsna_multitask_repository_exact_head"]
        != "e59e2368a722eabedc6b2228b1c6e1e7325cacd5"
        or structured["rsna_multitask_series"] != 4348
        or structured["rsna_split_unit"] != "series_level_random_five_fold"
        or structured["cmrx4dflow_repository_exact_head"]
        != "f6f835f34b86464256e3ce4362e7831325f32590"
        or [
            structured["cmrx4dflow_regular_training_cases"],
            structured["cmrx4dflow_regular_validation_cases"],
            structured["cmrx4dflow_regular_test_cases"],
        ] != [138, 32, 43]
        or structured["cmrx4dflow_embargo_date"] != "2026-12-01"
        or structured["isbi_2027_submission_deadline"] != "2026-10-26"
        or [
            structured["device_phantom_zenodo_record"],
            structured["device_phantom_base_anatomies"],
            structured["device_phantom_models"],
            structured["device_phantom_acquisitions"],
            structured["device_phantom_venc_per_model"],
            structured["device_phantom_cardiac_phases"],
            structured["device_phantom_human_patients"],
        ] != [14981710, 1, 4, 8, 2, 20, 0]
        or [(row["id"], row["total"]) for row in structured["candidates"]]
        != expected_structured_candidates
        or any(row["critical_axis_pass"] for row in structured["candidates"])
        or any(
            structured[key] is not False
            for key in (
                "primary_problem_selected", "paper_identity_active",
                "venet_public_source_mra_redistributed",
                "venet_independent_test_reported",
                "rsna_patient_grouped_split_explicit",
                "rsna_independent_dense_reference_test",
                "rsna_source_results_reproduced_by_aurora",
                "cmrx4dflow_terms_accepted_by_aurora", "cmrx4dflow_payload_accessed",
                "cmrx4dflow_aneurysm_patient_rows_identified",
                "historical_surface_vector_source_score_or_job_relabelled",
                "historical_surface_vector_p0_repaired_or_rerun", "p0_registered",
                "p1_registered", "method_selected", "architecture_selected",
                "scientific_server_queried", "gpu_training_authorized",
                "outer_test_authorized", "submission_identity_active",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or any(
            structured[key] is not True
            for key in (
                "venet_full_dataset_contact_only",
                "venet_topology_discontinuity_acknowledged_by_source",
                "venet_topology_aware_loss_is_source_stated_future_work",
                "cmrx4dflow_embargo_after_submission_deadline",
                "surface_vector_question_retained_as_inactive_hypothesis",
                "source_watch_added",
            )
        )
        or structured["execution_server"] != "introai9"
    ):
        raise ProtocolError(
            "The structured-vessel/4D-flow batch must remain rejected: the "
            "public VeNet subset, RSNA reference semantics, challenge embargo "
            "and one-anatomy phantom cannot authorize a task, model or compute."
        )
    checks.append("structured-vessel and embargoed 4D-flow non-admission boundary")

    pose_operator = problem_selection[
        "pose_workflow_and_spatiotemporal_operator_reappraisal"
    ]
    _require_keys(
        pose_operator,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "deepanepose_official_repository", "deepanepose_exact_head",
            "deepanepose_selected_sessions", "deepanepose_unique_subject_ids",
            "deepanepose_positive_annotation_json", "deepanepose_annotated_lesions",
            "deepanepose_fold_train_counts", "deepanepose_fold_validation_counts",
            "deepanepose_fold_test_counts", "deepanepose_test_union_subjects",
            "deepanepose_each_selected_subject_tested_once",
            "deepanepose_repository_license_file_present",
            "deepanepose_tracked_checkpoint_present",
            "source_reported_combined_patients", "source_reported_combined_aneurysms",
            "source_results_reproduced_by_aurora", "graph_physics_exact_head",
            "graph_physics_arxiv", "wss_transolver_exact_head",
            "wss_transolver_source_fields", "wss_transolver_wss_is_derived_magnitude",
            "wss_transolver_tracked_dataset_checkpoint_or_completed_fold_outputs",
            "expigeo_exact_head", "expigeo_patient_or_family_grouped_split_public",
            "hyctor_exact_head", "hyctor_learned_components_validated",
            "surface_vector_scientific_hypothesis_retained",
            "surface_vector_reactivated", "architecture_candidate_is_control_family_only",
            "candidates", "required_reentry_observables", "p0_registered",
            "p1_registered", "method_selected", "architecture_selected",
            "scientific_server_queried", "gpu_training_authorized",
            "outer_test_authorized", "submission_identity_active",
            "historical_job_repaired_or_rerun", "login_node_gpu_command_executed",
            "junjinyong_accessed", "next_allowed_action",
        ],
        "pose workflow and spatiotemporal operator reappraisal",
    )
    expected_pose_operator_candidates = [
        ("patient_wise_weak_pose_benchmark_repair", 29.0),
        ("axis_symmetry_aware_selective_pose_sets", 28.5),
        ("weak_pose_external_transport_to_ds005096", 27.0),
        ("derived_wss_reference_uncertainty", 26.0),
        ("family_disjoint_expigeo_explainability", 25.5),
        ("structure_faithful_transient_wss_operator", 21.5),
    ]
    if (
        pose_operator["status"]
        != "fresh_problem_level_batch_rejected_best_29_pose_task_direct_prior_and_transient_vector_asset_floors"
        or pose_operator["audit_document"]
        != "docs/pose-workflow-and-spatiotemporal-operator-source-reappraisal-2026-08-12.md"
        or pose_operator["automatic_selection_threshold"] != 32.0
        or pose_operator["best_candidate_id"]
        != "patient_wise_weak_pose_benchmark_repair"
        or pose_operator["best_score"] != 29.0
        or pose_operator["best_residual_novelty_score"] != 1.0
        or pose_operator["all_candidate_scores"]
        != [29.0, 28.5, 27.0, 26.0, 25.5, 21.5]
        or pose_operator["conditional_source_lead_count"] != 0
        or pose_operator["deepanepose_exact_head"]
        != "40042fa4290fe2e36a30dfb100b514cbe2fbaea2"
        or pose_operator["deepanepose_selected_sessions"] != 270
        or pose_operator["deepanepose_unique_subject_ids"] != 270
        or pose_operator["deepanepose_positive_annotation_json"] != 140
        or pose_operator["deepanepose_annotated_lesions"] != 164
        or pose_operator["deepanepose_fold_train_counts"]
        != [216, 216, 217, 216, 215]
        or pose_operator["deepanepose_fold_validation_counts"] != [0, 0, 0, 0, 0]
        or pose_operator["deepanepose_fold_test_counts"] != [54, 54, 53, 54, 55]
        or pose_operator["deepanepose_test_union_subjects"] != 270
        or pose_operator["deepanepose_each_selected_subject_tested_once"] is not True
        or pose_operator["deepanepose_repository_license_file_present"] is not False
        or pose_operator["deepanepose_tracked_checkpoint_present"] is not False
        or pose_operator["graph_physics_exact_head"]
        != "e4ac523d749b126f504665fb6270fcb91ac3cbd2"
        or pose_operator["wss_transolver_exact_head"]
        != "3087fc9b8370ad39db85db9a61315bb34bf43cbb"
        or pose_operator["wss_transolver_source_fields"] != ["p", "U"]
        or pose_operator["wss_transolver_wss_is_derived_magnitude"] is not True
        or pose_operator["expigeo_exact_head"]
        != "b28736842ec521641ea9389e4a9a58bccc5616f3"
        or pose_operator["hyctor_exact_head"]
        != "31f69e6c0953b4d1d0f52856cd4d16efb9248556"
        or pose_operator["surface_vector_scientific_hypothesis_retained"] is not True
        or pose_operator["architecture_candidate_is_control_family_only"] is not True
        or [
            (candidate.get("id"), candidate.get("total"))
            for candidate in pose_operator["candidates"]
        ]
        != expected_pose_operator_candidates
        or any(candidate.get("critical_axis_pass") is not False for candidate in pose_operator["candidates"])
        or any(
            pose_operator[key] is not False
            for key in (
                "primary_problem_selected", "paper_identity_active",
                "source_results_reproduced_by_aurora",
                "wss_transolver_tracked_dataset_checkpoint_or_completed_fold_outputs",
                "expigeo_patient_or_family_grouped_split_public",
                "hyctor_learned_components_validated", "surface_vector_reactivated",
                "p0_registered", "p1_registered", "method_selected",
                "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or pose_operator["next_allowed_action"]
        != "fresh_problem_level_source_or_whitelisted_material_task_asset_audit_only_no_payload_architecture_or_compute"
    ):
        raise ProtocolError(
            "The pose/operator source batch must remain rejected: public folds and "
            "direct-prior code do not create pose novelty or a transient-vector task asset."
        )
    checks.append("pose workflow and spatiotemporal operator rejection boundary")

    dsa_delta = problem_selection["surface_vector_and_task_faithful_dsa_delta"]
    _require_keys(
        dsa_delta,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_ids", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "current_schema_or_primary_batch_changed",
            "surface_vector_hypothesis_retained", "surface_vector_reactivated",
            "surface_vector_current_architecture",
            "structure_extractor_role_before_stability",
            "first_topological_endpoint", "historical_aneug_job_id",
            "historical_aneug_job_state", "historical_job_repaired_or_rerun",
            "fresh_version_without_whitelisted_material_signal_allowed",
            "save_net_doi", "save_net_internal_sequences_reported",
            "save_net_internal_patients_reported",
            "save_net_external_sequences_reported",
            "save_net_external_hospitals_reported", "save_net_reader_count",
            "save_net_reader_sequence_pairs",
            "save_net_source_reports_six_generated_frames_and_one_seventh_dose",
            "save_net_formal_diagnostic_consistency_prospectively_defined",
            "save_net_downstream_ia_segmentation_or_cvs_detection_evaluated",
            "save_net_data_public_versioned", "save_net_data_access",
            "dsa_transunet_doi", "dsa_transunet_patients_reported",
            "dsa_transunet_images_reported",
            "dsa_transunet_evaluates_morphology_and_qdsa_biomarker_agreement",
            "dsa_transunet_public_patient_image_mask_qdsa_split_asset_identified",
            "synthetic_dsa_arxiv", "synthetic_dsa_training_frames_reported",
            "synthetic_dsa_reader_images_reported", "synthetic_dsa_zenodo_record",
            "synthetic_dsa_zenodo_revision", "synthetic_dsa_zenodo_access",
            "synthetic_dsa_original_patient_images_present",
            "synthetic_dsa_public_downstream_labels_present",
            "dias_public_patient_count", "dias_public_sequence_count",
            "dias_release_is_expert_pruned_arterial_phase",
            "dias_framewise_arrival_exposure_aneurysm_qdsa_or_action_target_present",
            "source_results_reproduced_by_aurora", "candidates",
            "p0_registered", "p1_registered", "method_selected",
            "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "submission_identity_active", "login_node_gpu_command_executed",
            "junjinyong_accessed", "next_allowed_action",
        ],
        "surface-vector and task-faithful DSA delta",
    )
    expected_dsa_candidates = [
        ("task_faithful_sparse_dsa_biomarker_preservation", 26.5),
        ("adaptive_acquisition_stopping_with_downstream_risk", 26.5),
        ("posttreatment_coil_robust_qdsa_segmentation", 26.0),
        ("downstream_segmentation_transport_on_generated_dsa", 25.5),
        ("rare_pathology_ood_sparse_synthesis", 24.5),
        ("reader_calibrated_hallucination_detection", 23.5),
    ]
    if (
        dsa_delta["status"]
        != "delta_rejected_surface_vector_no_material_e0_and_task_faithful_dsa_direct_prior_composition_no_state_change"
        or dsa_delta["audit_document"]
        != "docs/surface-vector-and-task-faithful-dsa-adjudication-2026-08-12.md"
        or dsa_delta["automatic_selection_threshold"] != 32.0
        or dsa_delta["best_score"] != 26.5
        or dsa_delta["best_residual_novelty_score"] != 1.5
        or dsa_delta["all_candidate_scores"]
        != [26.5, 26.5, 26.0, 25.5, 24.5, 23.5]
        or dsa_delta["conditional_source_lead_count"] != 0
        or dsa_delta["surface_vector_current_architecture"] is not None
        or dsa_delta["structure_extractor_role_before_stability"]
        != "evaluation_only_not_training_loss"
        or dsa_delta["first_topological_endpoint"]
        != "boundary_margin_signed_total_degree_with_abstention_before_exact_points_or_worldlines"
        or dsa_delta["historical_aneug_job_id"] != "115645.ECE-util1"
        or dsa_delta["save_net_doi"] != "10.3389/fmed.2026.1793962"
        or (
            dsa_delta["save_net_internal_sequences_reported"],
            dsa_delta["save_net_internal_patients_reported"],
            dsa_delta["save_net_external_sequences_reported"],
            dsa_delta["save_net_external_hospitals_reported"],
            dsa_delta["save_net_reader_count"],
            dsa_delta["save_net_reader_sequence_pairs"],
        ) != (17335, 15286, 3255, 2, 5, 200)
        or dsa_delta["dsa_transunet_doi"] != "10.1016/j.ejrad.2026.112882"
        or (
            dsa_delta["dsa_transunet_patients_reported"],
            dsa_delta["dsa_transunet_images_reported"],
        ) != (1539, 2777)
        or dsa_delta["synthetic_dsa_arxiv"] != "2602.11703"
        or dsa_delta["synthetic_dsa_training_frames_reported"] != 99349
        or dsa_delta["synthetic_dsa_reader_images_reported"] != 400
        or dsa_delta["synthetic_dsa_zenodo_record"] != 21104782
        or dsa_delta["synthetic_dsa_zenodo_revision"] != 4
        or dsa_delta["synthetic_dsa_zenodo_access"]
        != "embargoed_until_2026_10_31"
        or (dsa_delta["dias_public_patient_count"], dsa_delta["dias_public_sequence_count"])
        != (60, 120)
        or [
            (candidate.get("id"), candidate.get("total"))
            for candidate in dsa_delta["candidates"]
        ] != expected_dsa_candidates
        or any(candidate.get("critical_axis_pass") is not False for candidate in dsa_delta["candidates"])
        or any(
            dsa_delta[key] is not False
            for key in (
                "current_schema_or_primary_batch_changed", "surface_vector_reactivated",
                "historical_job_repaired_or_rerun",
                "fresh_version_without_whitelisted_material_signal_allowed",
                "save_net_formal_diagnostic_consistency_prospectively_defined",
                "save_net_downstream_ia_segmentation_or_cvs_detection_evaluated",
                "save_net_data_public_versioned",
                "dsa_transunet_public_patient_image_mask_qdsa_split_asset_identified",
                "synthetic_dsa_original_patient_images_present",
                "synthetic_dsa_public_downstream_labels_present",
                "dias_framewise_arrival_exposure_aneurysm_qdsa_or_action_target_present",
                "source_results_reproduced_by_aurora", "p0_registered",
                "p1_registered", "method_selected", "architecture_selected",
                "scientific_server_queried", "gpu_training_authorized",
                "outer_test_authorized", "submission_identity_active",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or dsa_delta["surface_vector_hypothesis_retained"] is not True
        or dsa_delta["save_net_source_reports_six_generated_frames_and_one_seventh_dose"] is not True
        or dsa_delta["dsa_transunet_evaluates_morphology_and_qdsa_biomarker_agreement"] is not True
        or dsa_delta["dias_release_is_expert_pruned_arterial_phase"] is not True
    ):
        raise ProtocolError(
            "The surface-vector/DSA delta must remain fail-closed: a fresh label, "
            "direct-prior composition or embargo change cannot create E0, a model or compute."
        )
    checks.append("surface-vector and task-faithful DSA fail-closed delta boundary")

    adam_fold = problem_selection["adam_patch_fold_and_segmentation_prior_delta"]
    _require_keys(
        adam_fold,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_ids", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "current_schema_or_primary_batch_changed", "adam_fold_repository",
            "adam_fold_exact_head", "adam_fold_manifest_blob",
            "adam_fold_release_tag", "adam_fold_release_id",
            "adam_fold_release_assets", "adam_fold_release_total_bytes",
            "adam_fold_release_manifest_sha256",
            "adam_fold_repository_license_present",
            "adam_fold_upstream_redistribution_or_reuse_permission_public",
            "adam_fold_payload_accessed", "adam_fold_dataset_declared",
            "adam_fold_exact_scan_ids", "adam_fold_unique_base_ids",
            "adam_fold_suffix_counts", "adam_fold_train_counts",
            "adam_fold_validation_counts", "adam_fold_test_counts",
            "adam_fold_exact_train_test_overlap",
            "adam_fold_base_id_train_test_overlap",
            "adam_fold_test_union_exact_ids",
            "adam_fold_each_exact_id_tested_once",
            "adam_fold_negative_control_ids_present",
            "adam_fold_patient_overlap_interpretation",
            "official_adam_training_cases", "official_adam_positive_cases",
            "official_adam_negative_cases",
            "official_adam_baseline_followup_pairs",
            "official_adam_additional_unique_positive_subjects",
            "dino_3dra_repository", "dino_3dra_exact_head",
            "dino_3dra_sample_image_present",
            "dino_3dra_weight_is_git_lfs_pointer",
            "dino_3dra_training_code_fold_manifest_or_completed_outputs_present",
            "dino_3dra_arxiv_identifier_is_placeholder",
            "geop2vnet_repository", "geop2vnet_exact_head",
            "geop2vnet_repository_reported_cta_cases",
            "geop2vnet_repository_reported_lesions",
            "geop2vnet_clinical_data_or_checkpoint_present",
            "geop2vnet_patient_grouped_fold_semantics_public",
            "modality_agnostic_repository_head",
            "anatomy_weak_supervision_repository_head",
            "pre_post_stent_zenodo_record",
            "pre_post_stent_independent_patients",
            "pre_post_stent_dicom_bytes", "pre_post_stent_geometry_bytes",
            "pre_post_stent_cfd_field_output_released",
            "cow_gwas_zenodo_record", "cow_gwas_file_count",
            "cow_gwas_total_bytes",
            "cow_gwas_is_casewise_imaging_aneurysm_asset",
            "source_results_reproduced_by_aurora", "candidates",
            "p0_registered", "p1_registered", "method_selected",
            "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "submission_identity_active", "login_node_gpu_command_executed",
            "junjinyong_accessed", "next_allowed_action",
        ],
        "ADAM patch-fold and segmentation-prior delta",
    )
    expected_adam_fold_candidates = [
        ("dino_feature_3dra_segmentation_extension", 26.5),
        ("geometry_splatting_cta_segmentation_extension", 26.5),
        ("modality_agnostic_anatomy_aware_weak_supervision", 26.0),
        ("pre_post_stent_hemodynamic_remodeling_learning", 25.5),
        ("patient_grouped_adam_patch_benchmark_repair", 23.0),
        ("paired_adam_change_consistency_segmentation", 23.0),
    ]
    if (
        adam_fold["status"]
        != "fresh_public_release_and_direct_prior_batch_rejected_best_26_5_patient_grouping_novelty_asset_and_unit_floors_no_state_change"
        or adam_fold["audit_document"]
        != "docs/adam-patch-fold-release-and-segmentation-prior-reappraisal-2026-08-12.md"
        or adam_fold["automatic_selection_threshold"] != 32.0
        or adam_fold["best_candidate_ids"]
        != [
            "dino_feature_3dra_segmentation_extension",
            "geometry_splatting_cta_segmentation_extension",
        ]
        or adam_fold["best_score"] != 26.5
        or adam_fold["best_residual_novelty_score"] != 1.0
        or adam_fold["all_candidate_scores"]
        != [26.5, 26.5, 26.0, 25.5, 23.0, 23.0]
        or adam_fold["conditional_source_lead_count"] != 0
        or adam_fold["adam_fold_repository"]
        != "josedaviddr/Aneurysm_segmentation_DataSet_folds"
        or adam_fold["adam_fold_exact_head"]
        != "d36df7d19a96aa5b9fca0cc9050e021ac7319fee"
        or adam_fold["adam_fold_manifest_blob"]
        != "2476524d617068206467e7b93306266e95b8779d"
        or (adam_fold["adam_fold_release_tag"], adam_fold["adam_fold_release_id"])
        != ("v1.0", 349278633)
        or (
            adam_fold["adam_fold_release_assets"],
            adam_fold["adam_fold_release_total_bytes"],
        ) != (35, 61506611200)
        or adam_fold["adam_fold_release_manifest_sha256"]
        != "7d5ebe80859b4d781a13a3c1b65d3b18fb2dfa2bd13486bb64c36b980b133f9c"
        or (adam_fold["adam_fold_exact_scan_ids"], adam_fold["adam_fold_unique_base_ids"])
        != (93, 58)
        or adam_fold["adam_fold_suffix_counts"]
        != {"B": 35, "F": 35, "none": 23}
        or adam_fold["adam_fold_train_counts"] != [74, 74, 74, 75, 75]
        or adam_fold["adam_fold_validation_counts"] != [0, 0, 0, 0, 0]
        or adam_fold["adam_fold_test_counts"] != [19, 19, 19, 18, 18]
        or adam_fold["adam_fold_exact_train_test_overlap"] != [0, 0, 0, 0, 0]
        or adam_fold["adam_fold_base_id_train_test_overlap"] != [2, 3, 5, 6, 2]
        or adam_fold["adam_fold_test_union_exact_ids"] != 93
        or adam_fold["adam_fold_patient_overlap_interpretation"]
        != "inference_under_official_adam_b_f_same_subject_semantics_not_raw_payload_duplication_claim"
        or (
            adam_fold["official_adam_training_cases"],
            adam_fold["official_adam_positive_cases"],
            adam_fold["official_adam_negative_cases"],
            adam_fold["official_adam_baseline_followup_pairs"],
            adam_fold["official_adam_additional_unique_positive_subjects"],
        ) != (113, 93, 20, 35, 23)
        or adam_fold["dino_3dra_exact_head"]
        != "5d9982ee794b531a8f04e73e849af0040976381f"
        or adam_fold["geop2vnet_exact_head"]
        != "25c59bc172d0fedac37c1b6cfc8fe4af0823bf65"
        or (
            adam_fold["geop2vnet_repository_reported_cta_cases"],
            adam_fold["geop2vnet_repository_reported_lesions"],
        ) != (205, 266)
        or adam_fold["modality_agnostic_repository_head"]
        != "8ae1eec763d87887dac728d591c2c2b6df36be4f"
        or adam_fold["anatomy_weak_supervision_repository_head"]
        != "98072ee239ef6b61b8cd2a6ab01371b3f56c446d"
        or (
            adam_fold["pre_post_stent_zenodo_record"],
            adam_fold["pre_post_stent_independent_patients"],
            adam_fold["pre_post_stent_dicom_bytes"],
            adam_fold["pre_post_stent_geometry_bytes"],
        ) != (18944596, 1, 194755060, 3205118)
        or (
            adam_fold["cow_gwas_zenodo_record"],
            adam_fold["cow_gwas_file_count"],
            adam_fold["cow_gwas_total_bytes"],
        ) != (15084068, 46, 9016438620)
        or [
            (candidate.get("id"), candidate.get("total"))
            for candidate in adam_fold["candidates"]
        ] != expected_adam_fold_candidates
        or any(
            candidate.get("critical_axis_pass") is not False
            for candidate in adam_fold["candidates"]
        )
        or any(
            adam_fold[key] is not False
            for key in (
                "current_schema_or_primary_batch_changed",
                "adam_fold_repository_license_present",
                "adam_fold_upstream_redistribution_or_reuse_permission_public",
                "adam_fold_payload_accessed",
                "adam_fold_negative_control_ids_present",
                "dino_3dra_training_code_fold_manifest_or_completed_outputs_present",
                "geop2vnet_clinical_data_or_checkpoint_present",
                "geop2vnet_patient_grouped_fold_semantics_public",
                "pre_post_stent_cfd_field_output_released",
                "cow_gwas_is_casewise_imaging_aneurysm_asset",
                "source_results_reproduced_by_aurora", "p0_registered",
                "p1_registered", "method_selected", "architecture_selected",
                "scientific_server_queried", "gpu_training_authorized",
                "outer_test_authorized", "submission_identity_active",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or any(
            adam_fold[key] is not True
            for key in (
                "adam_fold_each_exact_id_tested_once",
                "dino_3dra_sample_image_present",
                "dino_3dra_weight_is_git_lfs_pointer",
                "dino_3dra_arxiv_identifier_is_placeholder",
            )
        )
        or adam_fold["next_allowed_action"]
        != "fresh_problem_or_material_patient_grouped_lawful_asset_audit_only_no_payload_architecture_or_compute"
    ):
        raise ProtocolError(
            "The ADAM patch-fold delta must remain rejected: release size and "
            "scan-wise folds cannot compensate for license, subject grouping, "
            "independent-unit or direct-prior failures."
        )
    checks.append("ADAM patch-fold and segmentation-prior rejection boundary")

    sah = problem_selection["aneurysmal_sah_segmentation_outcome_reappraisal"]
    _require_keys(
        sah,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "primary_problem_selected", "paper_identity_active",
            "zenodo_record_id", "zenodo_record_revision", "zenodo_license",
            "zenodo_archive_name", "zenodo_archive_bytes", "zenodo_archive_md5",
            "zenodo_archive_opened",
            "zenodo_metadata_declares_preprocessed_ncct_and_expert_mask_pairs",
            "zenodo_top_level_manifest_public", "zenodo_patient_count_public",
            "versioned_image_mask_outcome_join_public",
            "versioned_patient_centre_split_manifest_public",
            "official_pipeline_repository_head",
            "official_pipeline_tracked_patient_data",
            "official_pipeline_tracked_checkpoint",
            "multiclass_baseline_repository_head", "source_results_reproduced_by_aurora",
            "direct_prior_threats", "candidates", "required_reentry_observables",
            "surface_vector_reactivated", "p0_registered", "p1_registered",
            "method_selected", "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "submission_identity_active", "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed", "junjinyong_accessed",
            "next_allowed_action",
        ],
        "aneurysmal SAH segmentation-outcome reappraisal",
    )
    expected_sah_candidates = [
        ("cross_aetiology_small_volume_asah_transport", 29.0),
        ("segmentation_error_aware_six_month_gos_volume_equivalence", 28.5),
        ("multicompartment_burden_beyond_modified_fisher", 28.0),
        ("segmentation_conditioned_three_month_mortality", 28.0),
        ("selective_outcome_preserving_segmentation", 27.0),
        ("longitudinal_resolution_dci_trajectory_modelling", 22.5),
    ]
    if (
        sah["status"]
        != "fresh_problem_level_batch_rejected_best_29_fails_residual_novelty_and_joined_outcome_asset_floors"
        or sah["audit_document"]
        != "docs/sah-segmentation-outcome-asset-reappraisal-2026-08-12.md"
        or sah["automatic_selection_threshold"] != 32.0
        or sah["best_candidate_id"] != "cross_aetiology_small_volume_asah_transport"
        or sah["best_score"] != 29.0
        or sah["best_residual_novelty_score"] != 1.0
        or sah["all_candidate_scores"] != [29.0, 28.5, 28.0, 28.0, 27.0, 22.5]
        or sah["conditional_source_lead_count"] != 0
        or sah["primary_problem_selected"] is not False
        or sah["paper_identity_active"] is not False
        or sah["zenodo_record_id"] != 8228847
        or sah["zenodo_record_revision"] != 2
        or sah["zenodo_license"] != "cc-by-4.0"
        or sah["zenodo_archive_name"] != "subarachnoid_hemorrhage_rhuh.rar"
        or sah["zenodo_archive_bytes"] != 648502298
        or sah["zenodo_archive_md5"] != "a67bf358ebb326f156071864c318ab42"
        or sah["zenodo_archive_opened"] is not False
        or sah["zenodo_metadata_declares_preprocessed_ncct_and_expert_mask_pairs"]
        is not True
        or any(
            sah[key] is not False
            for key in (
                "zenodo_top_level_manifest_public", "zenodo_patient_count_public",
                "versioned_image_mask_outcome_join_public",
                "versioned_patient_centre_split_manifest_public",
                "official_pipeline_tracked_patient_data",
                "official_pipeline_tracked_checkpoint",
                "source_results_reproduced_by_aurora",
            )
        )
        or sah["official_pipeline_repository_head"]
        != "3fbd7a9282287a719aff5f603e9539b7a886b373"
        or sah["multiclass_baseline_repository_head"]
        != "269f4724fde89515eac8dbdac648925dc24bf492"
        or [(row["id"], row["total"]) for row in sah["candidates"]]
        != expected_sah_candidates
        or any(row["critical_axis_pass"] is not False for row in sah["candidates"])
        or any(
            sah[key] is not False
            for key in (
                "surface_vector_reactivated", "p0_registered", "p1_registered",
                "method_selected", "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or sah["next_allowed_action"]
        != "fresh_problem_level_source_or_versioned_joined_outcome_asset_audit_only_no_rar_checkpoint_payload_architecture_or_compute"
    ):
        raise ProtocolError(
            "The aSAH mask release must remain a rejected metadata-only source: "
            "no patient-level outcome join, residual novelty, payload, model or compute."
        )
    checks.append("aSAH segmentation-outcome joined-asset and novelty rejection boundary")

    release_utility = problem_selection[
        "rsna_release_layer_and_webgan_utility_delta"
    ]
    _require_keys(
        release_utility,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "current_schema_or_primary_batch_changed", "rsna_launch_release_date",
            "rsna_launch_imaging_studies_reported",
            "rsna_launch_annotated_aneurysms_reported",
            "rsna_launch_institutions_reported",
            "rsna_launch_radiologists_reported", "rsna_launch_modalities",
            "rsna_registry_scans_reported",
            "rsna_registry_radiologists_reported",
            "rsna_registry_institutions_reported",
            "rsna_registry_ai_segmented_studies_reported",
            "rsna_second_place_training_series_reported",
            "rsna_three_counts_same_release_layer_proven",
            "rsna_arithmetic_train_hidden_test_split_inferred",
            "rsna_machine_readable_identity_map_public",
            "rsna_terms_accepted_or_mira_requested",
            "rsna_controlled_payload_accessed", "webgan_article_doi",
            "webgan_original_cases_reported", "webgan_institutions_reported",
            "webgan_synthetic_rows_reported", "webgan_target",
            "webgan_original_data_access", "webgan_repository",
            "webgan_repository_head", "webgan_repository_release_count",
            "webgan_github_recognized_license",
            "webgan_tracked_license_file_present", "webgan_readme_claims_mit",
            "webgan_synthetic_csv_bytes",
            "webgan_repository_shallow_cloned_for_static_code_audit",
            "webgan_synthetic_csv_body_inspected",
            "webgan_original_patient_table_present",
            "webgan_generator_trained_on_complete_original_table_in_inspected_notebook",
            "webgan_synthetic_model_evaluated_on_complete_original_table_in_inspected_notebook",
            "webgan_real_test_donors_unseen_by_generator",
            "webgan_patient_or_institution_disjoint_outer_test_executable",
            "webgan_source_reported_results_reproduced_by_aurora",
            "webgan_source_paper_invalidated_by_aurora", "candidates",
            "source_watch_added", "surface_vector_reactivated", "p0_registered",
            "p1_registered", "method_selected", "architecture_selected",
            "scientific_server_queried", "gpu_training_authorized",
            "outer_test_authorized", "submission_identity_active",
            "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed", "junjinyong_accessed",
            "next_allowed_action",
        ],
        "RSNA release-layer and WEB-GAN utility delta",
    )
    expected_release_utility_candidates = [
        ("rsna_release_layer_aware_multimodal_transport", 29.0),
        ("rsna_modality_site_selective_risk", 28.5),
        ("donor_disjoint_web_synthetic_utility", 26.0),
        ("leave_one_institution_out_web_outcome_transport", 25.5),
        ("leakage_aware_synthetic_utility_identified_set", 24.5),
        ("released_synthetic_only_web_reproducibility", 23.0),
    ]
    if (
        release_utility["status"]
        != "delta_rejected_rsna_release_layers_unresolved_webgan_donor_overlap_original_unavailable_no_state_change"
        or release_utility["audit_document"]
        != "docs/rsna-release-layer-and-webgan-utility-delta-2026-08-12.md"
        or release_utility["automatic_selection_threshold"] != 32.0
        or release_utility["best_candidate_id"]
        != "rsna_release_layer_aware_multimodal_transport"
        or release_utility["best_score"] != 29.0
        or release_utility["best_residual_novelty_score"] != 1.5
        or release_utility["all_candidate_scores"]
        != [29.0, 28.5, 26.0, 25.5, 24.5, 23.0]
        or release_utility["conditional_source_lead_count"] != 0
        or release_utility["rsna_launch_release_date"] != "2025-07-29"
        or (
            release_utility["rsna_launch_imaging_studies_reported"],
            release_utility["rsna_launch_annotated_aneurysms_reported"],
            release_utility["rsna_launch_institutions_reported"],
            release_utility["rsna_launch_radiologists_reported"],
        )
        != ("over_6500", "over_3500", 18, "over_60")
        or release_utility["rsna_launch_modalities"]
        != ["CTA", "MRA", "T1_post_contrast", "T2_weighted_MRI"]
        or (
            release_utility["rsna_registry_scans_reported"],
            release_utility["rsna_registry_radiologists_reported"],
            release_utility["rsna_registry_institutions_reported"],
            release_utility["rsna_registry_ai_segmented_studies_reported"],
            release_utility["rsna_second_place_training_series_reported"],
        )
        != ("over_4000_CT_brain_scans", "over_40", 18, "about_200", 4348)
        or release_utility["webgan_article_doi"]
        != "10.1177/2997979X251369456"
        or (
            release_utility["webgan_original_cases_reported"],
            release_utility["webgan_institutions_reported"],
            release_utility["webgan_synthetic_rows_reported"],
        )
        != (78, 3, 1000)
        or release_utility["webgan_target"] != "six_month_occlusion_grade"
        or release_utility["webgan_original_data_access"]
        != "corresponding_author_request_only"
        or release_utility["webgan_repository"]
        != "shrinitbabel/WEB-GAN-occlusion-prediction"
        or release_utility["webgan_repository_head"]
        != "42ce2a8c795b32e03163be3a9a324eba9a0a76e5"
        or release_utility["webgan_repository_release_count"] != 0
        or release_utility["webgan_github_recognized_license"] is not None
        or release_utility["webgan_synthetic_csv_bytes"] != 109364
        or [
            (row["id"], float(row["total"]))
            for row in release_utility["candidates"]
        ]
        != expected_release_utility_candidates
        or any(row["critical_axis_pass"] is not False for row in release_utility["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in release_utility["candidates"]
        )
        or any(
            release_utility[key] is not False
            for key in (
                "current_schema_or_primary_batch_changed",
                "rsna_three_counts_same_release_layer_proven",
                "rsna_arithmetic_train_hidden_test_split_inferred",
                "rsna_machine_readable_identity_map_public",
                "rsna_terms_accepted_or_mira_requested",
                "rsna_controlled_payload_accessed",
                "webgan_tracked_license_file_present",
                "webgan_synthetic_csv_body_inspected",
                "webgan_original_patient_table_present",
                "webgan_real_test_donors_unseen_by_generator",
                "webgan_patient_or_institution_disjoint_outer_test_executable",
                "webgan_source_reported_results_reproduced_by_aurora",
                "webgan_source_paper_invalidated_by_aurora",
                "source_watch_added", "surface_vector_reactivated",
                "p0_registered", "p1_registered", "method_selected",
                "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or any(
            release_utility[key] is not True
            for key in (
                "webgan_readme_claims_mit",
                "webgan_repository_shallow_cloned_for_static_code_audit",
                "webgan_generator_trained_on_complete_original_table_in_inspected_notebook",
                "webgan_synthetic_model_evaluated_on_complete_original_table_in_inspected_notebook",
            )
        )
        or release_utility["next_allowed_action"]
        != "fresh_problem_level_source_or_versioned_patient_centre_disjoint_real_outer_test_asset_audit_only_no_data_request_architecture_or_compute"
    ):
        raise ProtocolError(
            "The RSNA release-layer and WEB-GAN utility delta must remain a "
            "rejected static-source audit: no count conflation, donor-disjoint "
            "claim, original patient asset, model, server, compute or paper identity."
        )
    checks.append("RSNA release-layer and WEB-GAN donor-utility rejection boundary")

    rupture_delta = problem_selection[
        "rupture_state_future_risk_and_unit_semantics_delta"
    ]
    _require_keys(
        rupture_delta,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "current_schema_or_primary_batch_changed", "qims_article_doi",
            "qims_reported_patients", "qims_reported_aneurysms",
            "qims_reported_centres", "qims_centre_1_patients",
            "qims_centre_1_aneurysms", "qims_centre_1_split_rows",
            "qims_external_set_1_patients", "qims_external_set_1_aneurysms",
            "qims_external_set_2_patients", "qims_external_set_2_aneurysms",
            "qims_reported_auc_train_internal_external",
            "qims_target_is_cross_sectional_rupture_status",
            "qims_admission_blood_glucose_is_post_event_for_ruptured_presentations",
            "qims_patient_grouped_centre_1_split_explicit",
            "qims_public_versioned_patient_image_feature_split_asset_identified",
            "qims_source_results_reproduced_by_aurora", "plos_article_doi",
            "plos_reported_aneurysm_patients", "plos_reported_controls",
            "plos_reported_ruptured_unruptured", "plos_figshare_article_id",
            "plos_figshare_license", "plos_figshare_file_name",
            "plos_figshare_file_bytes", "plos_figshare_file_md5",
            "plos_figshare_object_is_aggregate_table_not_patient_rows_or_cta",
            "plos_figshare_xls_body_opened",
            "patient_image_or_feature_payload_accessed", "candidates",
            "source_watch_added", "surface_vector_reactivated", "p0_registered",
            "p1_registered", "method_selected", "architecture_selected",
            "scientific_server_queried", "gpu_training_authorized",
            "outer_test_authorized", "submission_identity_active",
            "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed", "junjinyong_accessed",
            "next_allowed_action",
        ],
        "rupture-state and future-risk unit-semantics delta",
    )
    expected_rupture_delta_candidates = [
        ("external_centre_rupture_status_calibration_decomposition", 27.5),
        ("mca_circle_of_willis_occurrence_transport", 27.0),
        ("measurement_time_aware_incremental_radiomics_value", 25.5),
        ("pre_event_only_individualized_future_rupture_prediction", 25.0),
        ("patient_grouped_multi_aneurysm_external_validation", 24.0),
        ("rupture_status_synthetic_data_external_utility", 23.5),
    ]
    if (
        rupture_delta["status"]
        != "delta_rejected_cross_sectional_rupture_status_is_not_future_risk_no_public_joined_asset_no_state_change"
        or rupture_delta["audit_document"]
        != "docs/rupture-state-future-risk-and-unit-semantics-delta-2026-08-12.md"
        or rupture_delta["automatic_selection_threshold"] != 32.0
        or rupture_delta["best_candidate_id"]
        != "external_centre_rupture_status_calibration_decomposition"
        or rupture_delta["best_score"] != 27.5
        or rupture_delta["best_residual_novelty_score"] != 2.5
        or rupture_delta["all_candidate_scores"]
        != [27.5, 27.0, 25.5, 25.0, 24.0, 23.5]
        or rupture_delta["conditional_source_lead_count"] != 0
        or rupture_delta["qims_article_doi"] != "10.21037/qims-2025-1-2593"
        or (
            rupture_delta["qims_reported_patients"],
            rupture_delta["qims_reported_aneurysms"],
            rupture_delta["qims_reported_centres"],
        ) != (756, 877, 3)
        or (
            rupture_delta["qims_centre_1_patients"],
            rupture_delta["qims_centre_1_aneurysms"],
            rupture_delta["qims_centre_1_split_rows"],
        ) != (404, 450, [314, 136])
        or (
            rupture_delta["qims_external_set_1_patients"],
            rupture_delta["qims_external_set_1_aneurysms"],
            rupture_delta["qims_external_set_2_patients"],
            rupture_delta["qims_external_set_2_aneurysms"],
        ) != (125, 148, 227, 279)
        or rupture_delta["qims_reported_auc_train_internal_external"]
        != [0.887, 0.910, 0.773, 0.735]
        or rupture_delta["plos_article_doi"] != "10.1371/journal.pone.0319500"
        or (
            rupture_delta["plos_reported_aneurysm_patients"],
            rupture_delta["plos_reported_controls"],
            rupture_delta["plos_reported_ruptured_unruptured"],
        ) != (269, 269, [193, 76])
        or rupture_delta["plos_figshare_article_id"] != 28661913
        or rupture_delta["plos_figshare_license"] != "cc-by-4.0"
        or rupture_delta["plos_figshare_file_name"] != "Table 1.xls"
        or rupture_delta["plos_figshare_file_bytes"] != 5632
        or rupture_delta["plos_figshare_file_md5"]
        != "6e188acb4759df4b14ca4cb7d5eb3477"
        or [
            (row["id"], float(row["total"]))
            for row in rupture_delta["candidates"]
        ] != expected_rupture_delta_candidates
        or any(row["critical_axis_pass"] is not False for row in rupture_delta["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in rupture_delta["candidates"]
        )
        or any(
            rupture_delta[key] is not False
            for key in (
                "current_schema_or_primary_batch_changed",
                "qims_patient_grouped_centre_1_split_explicit",
                "qims_public_versioned_patient_image_feature_split_asset_identified",
                "qims_source_results_reproduced_by_aurora",
                "plos_figshare_xls_body_opened",
                "patient_image_or_feature_payload_accessed", "source_watch_added",
                "surface_vector_reactivated", "p0_registered", "p1_registered",
                "method_selected", "architecture_selected", "scientific_server_queried",
                "gpu_training_authorized", "outer_test_authorized",
                "submission_identity_active", "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed", "junjinyong_accessed",
            )
        )
        or any(
            rupture_delta[key] is not True
            for key in (
                "qims_target_is_cross_sectional_rupture_status",
                "qims_admission_blood_glucose_is_post_event_for_ruptured_presentations",
                "plos_figshare_object_is_aggregate_table_not_patient_rows_or_cta",
            )
        )
        or rupture_delta["next_allowed_action"]
        != "fresh_problem_level_source_or_timestamped_patient_grouped_future_event_asset_audit_only_no_data_request_architecture_or_compute"
    ):
        raise ProtocolError(
            "The rupture-state/future-risk delta must remain a rejected source "
            "audit: status is not a future event, patient grouping is unresolved, "
            "the public PLOS object is aggregate, and no model or compute may open."
        )
    checks.append("rupture-state versus future-risk and patient-unit rejection boundary")

    biology_delta = problem_selection[
        "longitudinal_biology_and_cross_scale_mechanism_reappraisal"
    ]
    _require_keys(
        biology_delta,
        [
            "status", "audit_document", "automatic_selection_threshold",
            "best_candidate_id", "best_score", "best_residual_novelty_score",
            "all_candidate_scores", "conditional_source_lead_count",
            "current_schema_or_primary_batch_changed", "long_term_awe_doi",
            "long_term_awe_reported_patients", "long_term_awe_reported_aneurysms",
            "long_term_awe_reported_centres", "long_term_awe_median_followup_years",
            "long_term_awe_events_with_without_enhancement",
            "long_term_awe_denominators_with_without_enhancement",
            "long_term_awe_reported_adjusted_hr",
            "long_term_awe_endpoint_is_growth_morphology_or_rupture_composite",
            "long_term_awe_public_versioned_patient_image_event_split_asset_identified",
            "academic_radiology_doi",
            "academic_radiology_cross_sectional_patients_aneurysms",
            "academic_radiology_longitudinal_patients_aneurysms",
            "academic_radiology_uses_separate_cross_sectional_longitudinal_and_ukb_datasets",
            "same_patient_nhr_siri_awe_growth_asah_mediation_identified",
            "jmri_inflammation_pmid", "jmri_reported_patients_aneurysms",
            "jmri_longitudinal_subcohort_patients_aneurysms",
            "jmri_median_followup_months", "rat_mra_doi",
            "rat_induced_analysis_animals", "rat_control_animals",
            "rat_induced_w12_animals", "rat_early_deaths", "rat_sah_deaths",
            "rat_mra_reported_sensitivity_specificity",
            "rat_tof_mra_isotropic_resolution_mm",
            "rat_largest_false_negative_aneurysm_mm", "rat_data_access",
            "rat_public_versioned_mr_sem_animal_time_manifest_identified",
            "tissue_ingrowth_doi", "tissue_ingrowth_direct_prior_already_audited",
            "human_or_animal_transient_wss_critical_point_worldline_outcome_join_identified",
            "source_results_reproduced_by_aurora", "patient_or_animal_payload_accessed",
            "candidates", "source_watch_added", "surface_vector_reactivated",
            "p0_registered", "p1_registered", "method_selected",
            "architecture_selected", "scientific_server_queried",
            "gpu_training_authorized", "outer_test_authorized",
            "submission_identity_active", "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed", "junjinyong_accessed",
            "next_allowed_action",
        ],
        "longitudinal biology and cross-scale mechanism reappraisal",
    )
    expected_biology_candidates = [
        ("baseline_awe_incremental_survival_value_beyond_clinical_morphology", 28.5),
        ("component_specific_long_term_instability_with_intervention_censoring", 26.5),
        ("resolution_calibrated_preclinical_mra_sem_detectability", 25.0),
        ("angiography_to_histological_healing_bridge", 23.0),
        ("same_patient_inflammation_awe_growth_asah_mediation", 22.5),
        ("animal_to_human_longitudinal_instability_transport", 20.0),
    ]
    if (
        biology_delta["status"]
        != "delta_rejected_real_future_followup_exists_but_direct_association_prior_and_no_public_joined_biological_mechanical_asset_no_state_change"
        or biology_delta["audit_document"]
        != "docs/longitudinal-biology-and-cross-scale-mechanism-reappraisal-2026-08-12.md"
        or biology_delta["automatic_selection_threshold"] != 32.0
        or biology_delta["best_candidate_id"]
        != "baseline_awe_incremental_survival_value_beyond_clinical_morphology"
        or biology_delta["best_score"] != 28.5
        or biology_delta["best_residual_novelty_score"] != 2.5
        or biology_delta["all_candidate_scores"]
        != [28.5, 26.5, 25.0, 23.0, 22.5, 20.0]
        or biology_delta["conditional_source_lead_count"] != 0
        or biology_delta["long_term_awe_doi"] != "10.1002/ana.78106"
        or (
            biology_delta["long_term_awe_reported_patients"],
            biology_delta["long_term_awe_reported_aneurysms"],
            biology_delta["long_term_awe_reported_centres"],
        ) != (198, 224, 2)
        or biology_delta["long_term_awe_median_followup_years"] != 6.8
        or biology_delta["long_term_awe_events_with_without_enhancement"] != [15, 13]
        or biology_delta["long_term_awe_denominators_with_without_enhancement"]
        != [72, 152]
        or biology_delta["long_term_awe_reported_adjusted_hr"] != 5.06
        or biology_delta["academic_radiology_doi"] != "10.1016/j.acra.2026.04.002"
        or biology_delta["academic_radiology_cross_sectional_patients_aneurysms"]
        != [308, 416]
        or biology_delta["academic_radiology_longitudinal_patients_aneurysms"]
        != [80, 85]
        or biology_delta["jmri_inflammation_pmid"] != 41913331
        or biology_delta["jmri_reported_patients_aneurysms"] != [311, 418]
        or biology_delta["jmri_longitudinal_subcohort_patients_aneurysms"]
        != [67, 84]
        or biology_delta["jmri_median_followup_months"] != 7.0
        or biology_delta["rat_mra_doi"] != "10.1038/s41598-026-37369-2"
        or (
            biology_delta["rat_induced_analysis_animals"],
            biology_delta["rat_control_animals"],
            biology_delta["rat_induced_w12_animals"],
            biology_delta["rat_early_deaths"],
            biology_delta["rat_sah_deaths"],
        ) != (13, 6, 8, 5, 3)
        or biology_delta["rat_mra_reported_sensitivity_specificity"] != [0.40, 0.60]
        or biology_delta["rat_tof_mra_isotropic_resolution_mm"] != 0.146
        or biology_delta["rat_largest_false_negative_aneurysm_mm"] != 0.10
        or biology_delta["rat_data_access"]
        != "corresponding_author_reasonable_request"
        or biology_delta["tissue_ingrowth_doi"] != "10.1038/s41598-026-43798-w"
        or [
            (row["id"], float(row["total"]))
            for row in biology_delta["candidates"]
        ] != expected_biology_candidates
        or any(row["critical_axis_pass"] is not False for row in biology_delta["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in biology_delta["candidates"]
        )
        or any(
            biology_delta[key] is not False
            for key in (
                "current_schema_or_primary_batch_changed",
                "long_term_awe_public_versioned_patient_image_event_split_asset_identified",
                "same_patient_nhr_siri_awe_growth_asah_mediation_identified",
                "rat_public_versioned_mr_sem_animal_time_manifest_identified",
                "human_or_animal_transient_wss_critical_point_worldline_outcome_join_identified",
                "source_results_reproduced_by_aurora", "patient_or_animal_payload_accessed",
                "source_watch_added", "surface_vector_reactivated", "p0_registered",
                "p1_registered", "method_selected", "architecture_selected",
                "scientific_server_queried", "gpu_training_authorized",
                "outer_test_authorized", "submission_identity_active",
                "historical_job_repaired_or_rerun", "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or any(
            biology_delta[key] is not True
            for key in (
                "long_term_awe_endpoint_is_growth_morphology_or_rupture_composite",
                "academic_radiology_uses_separate_cross_sectional_longitudinal_and_ukb_datasets",
                "tissue_ingrowth_direct_prior_already_audited",
            )
        )
        or biology_delta["next_allowed_action"]
        != "fresh_problem_level_source_or_versioned_patient_image_biomarker_time_event_asset_audit_only_no_request_payload_architecture_or_compute"
    ):
        raise ProtocolError(
            "The longitudinal-biology delta must preserve real future follow-up "
            "without inferring cross-cohort mediation or opening a joined asset, "
            "surface-vector method, server, compute or paper identity."
        )
    checks.append("longitudinal biology and cross-scale mechanism rejection boundary")

    wall_release = problem_selection[
        "four_d_cta_wall_phenotype_release_reappraisal"
    ]
    _require_keys(
        wall_release,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "source_paper_doi",
            "source_paper_pmid",
            "source_reported_aneurysms",
            "source_reported_hospitals",
            "source_trajectory_sampling_hz",
            "source_trajectory_duration_seconds",
            "source_reported_average_accuracy_percent",
            "source_results_reproduced_by_aurora",
            "source_directly_predicts_intraoperative_wall_phenotype_from_4dcta_trajectory",
            "zenodo_record_id",
            "zenodo_record_revision",
            "zenodo_record_modified",
            "zenodo_record_license",
            "zenodo_archive_name",
            "zenodo_archive_bytes",
            "zenodo_archive_md5",
            "zenodo_archive_downloaded",
            "github_repository",
            "github_repository_head",
            "github_repository_release_count",
            "github_recognized_license",
            "visible_top_level_case_directories",
            "visible_case_directory_count_equated_to_independent_patient_count",
            "suffix_identifier_semantics_machine_auditable",
            "recursive_git_tree_truncated",
            "source_4dcta_dicom_public",
            "intraoperative_rgb_or_video_public",
            "image_to_wall_registration_reference_public",
            "surface_geometry_and_adjacency_contract_public",
            "complete_patient_centre_fold_manifest_public",
            "dense_independent_whole_wall_reference_public",
            "future_growth_or_progression_target_joined",
            "recent_dynamic_direct_priors",
            "direct_prior_threats",
            "candidates",
            "required_reentry_observables",
            "surface_vector_reactivated",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "historical_score_or_job_relabelled",
            "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "4D-CTA wall-phenotype release reappraisal",
    )
    wall_candidate_ids = [
        "verification_aware_wall_phenotype_partial_identification",
        "centre_held_out_spatiotemporal_surface_mapping",
        "patient_clustered_conformal_wall_phenotype_mapping",
        "temporal_resolution_stable_wall_phenotype_inference",
        "joint_motion_hemodynamics_wall_map",
        "motion_to_future_growth_bridge",
    ]
    wall_axes = [
        [5.0, 2.0, 2.5, 3.5, 2.5, 4.5, 5.0, 4.0],
        [5.0, 3.5, 1.5, 3.0, 2.5, 4.5, 5.0, 3.5],
        [4.5, 3.0, 1.0, 3.0, 2.5, 5.0, 5.0, 4.0],
        [4.5, 2.5, 2.0, 2.5, 2.5, 4.5, 5.0, 4.0],
        [5.0, 3.0, 1.5, 1.5, 2.5, 5.0, 5.0, 3.0],
        [5.0, 1.5, 2.5, 1.0, 1.0, 5.0, 5.0, 3.5],
    ]
    wall_scores = [29.0, 28.5, 28.0, 27.5, 26.5, 24.5]
    wall_candidates = wall_release["candidates"]
    if (
        wall_release["status"]
        != "fresh_material_source_batch_rejected_best_29_fails_target_identifiability_and_independent_unit_floors_no_active_lead"
        or wall_release["audit_document"]
        != "docs/four-d-cta-wall-phenotype-release-and-target-reappraisal-2026-08-12.md"
        or wall_release["automatic_selection_threshold"] != 32.0
        or wall_release["best_candidate_id"] != wall_candidate_ids[0]
        or wall_release["best_score"] != 29.0
        or wall_release["best_residual_novelty_score"] != 2.5
        or wall_release["all_candidate_scores"] != wall_scores
        or wall_release["conditional_source_lead_count"] != 0
        or wall_release["primary_problem_selected"] is not False
        or wall_release["paper_identity_active"] is not False
        or wall_release["source_paper_doi"] != "10.7717/peerj.19393"
        or wall_release["source_paper_pmid"] != 40356666
        or wall_release["source_reported_aneurysms"] != 52
        or wall_release["source_reported_hospitals"] != 4
        or wall_release["source_trajectory_sampling_hz"] != 100
        or wall_release["source_trajectory_duration_seconds"] != 1
        or wall_release["source_reported_average_accuracy_percent"] != 92
        or wall_release["source_results_reproduced_by_aurora"] is not False
        or wall_release[
            "source_directly_predicts_intraoperative_wall_phenotype_from_4dcta_trajectory"
        ]
        is not True
        or wall_release["zenodo_record_id"] != 13788524
        or wall_release["zenodo_record_revision"] != 4
        or wall_release["zenodo_record_modified"]
        != "2024-09-23T04:40:53.613542+00:00"
        or wall_release["zenodo_record_license"] != "cc-by-4.0"
        or wall_release["zenodo_archive_name"]
        != "Kumrai-T/DA_4DCTA-v1.0.1.zip"
        or wall_release["zenodo_archive_bytes"] != 1934055674
        or wall_release["zenodo_archive_md5"]
        != "fd9f856b485983cd430ab94d01a24596"
        or wall_release["zenodo_archive_downloaded"] is not False
        or wall_release["github_repository"] != "Kumrai-T/DA_4DCTA"
        or wall_release["github_repository_head"]
        != "8df7d45e9f65e3cbfd4ae3fc430c65a98905bdfc"
        or wall_release["github_repository_release_count"] != 1
        or wall_release["github_recognized_license"] is not None
        or wall_release["visible_top_level_case_directories"] != 52
        or wall_release[
            "visible_case_directory_count_equated_to_independent_patient_count"
        ]
        is not False
        or wall_release["suffix_identifier_semantics_machine_auditable"]
        is not False
        or wall_release["recursive_git_tree_truncated"] is not True
        or any(
            wall_release[key] is not False
            for key in (
                "source_4dcta_dicom_public",
                "intraoperative_rgb_or_video_public",
                "image_to_wall_registration_reference_public",
                "surface_geometry_and_adjacency_contract_public",
                "complete_patient_centre_fold_manifest_public",
                "dense_independent_whole_wall_reference_public",
                "future_growth_or_progression_target_joined",
            )
        )
        or not isinstance(wall_candidates, list)
        or len(wall_candidates) != 6
        or [item.get("id") for item in wall_candidates] != wall_candidate_ids
        or [item.get("axis_scores") for item in wall_candidates] != wall_axes
        or [item.get("total") for item in wall_candidates] != wall_scores
        or any(item.get("critical_axis_pass") is not False for item in wall_candidates)
        or any(
            wall_release[key] is not False
            for key in (
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_score_or_job_relabelled",
                "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or wall_release["next_allowed_action"]
        != "fresh_problem_level_source_or_complete_4dcta_intraoperative_joined_asset_audit_only_no_payload_architecture_or_compute"
    ):
        raise ProtocolError(
            "The 4D-CTA wall-phenotype release must remain a rejected source "
            "lead: derived trajectories do not identify registration, selection, "
            "dense wall truth or independent patient units and authorize no compute."
        )
    checks.append("4D-CTA wall-phenotype release and target rejection boundary")

    culprit_mimic = problem_selection[
        "culprit_lesion_and_mimic_differential_reappraisal"
    ]
    _require_keys(
        culprit_mimic,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "cta_culprit_doi",
            "cta_culprit_development_patients",
            "cta_culprit_development_aneurysms",
            "cta_culprit_development_hospitals",
            "cta_culprit_external_patients",
            "cta_culprit_external_aneurysms",
            "cta_culprit_external_hospitals",
            "cta_culprit_total_patients",
            "cta_culprit_total_aneurysms",
            "cta_culprit_total_hospitals",
            "cta_culprit_reference_uses_ct_hematoma_or_neurosurgical_findings",
            "cta_culprit_source_external_auc_gaussian_process",
            "cta_culprit_source_external_auc_logistic_regression",
            "cta_culprit_source_external_auc_quadratic_discriminant",
            "cta_culprit_source_results_reproduced_by_aurora",
            "cta_culprit_public_versioned_joined_image_lesion_reference_asset_identified",
            "vwi_symptomatic_doi",
            "vwi_symptomatic_institutions",
            "vwi_symptomatic_patients",
            "vwi_symptomatic_aneurysms",
            "vwi_symptomatic_aneurysms_positive",
            "vwi_symptomatic_aneurysms_negative",
            "vwi_symptomatic_source_cutoff",
            "vwi_symptomatic_source_specificity",
            "vwi_symptomatic_source_negative_predictive_value",
            "vwi_symptomatic_source_results_reproduced_by_aurora",
            "vwi_symptomatic_status_equated_to_acute_rupture_culprit",
            "vwi_symptomatic_public_versioned_patient_image_release_identified",
            "smaller_counterpart_doi",
            "smaller_counterpart_single_centre",
            "smaller_counterpart_patients",
            "smaller_counterpart_largest_ruptured_patients",
            "smaller_counterpart_smaller_ruptured_patients",
            "smaller_counterpart_data_request_only",
            "smaller_counterpart_cross_sectional_label_is_future_rupture_estimand",
            "infundibulum_doi",
            "infundibulum_single_centre",
            "infundibulum_total_outpouchings",
            "infundibulum_unequivocal_count",
            "infundibulum_conundrum_count",
            "infundibulum_unequivocal_followed",
            "infundibulum_conundrum_followed",
            "infundibulum_followup_lesion_years",
            "infundibulum_dsa_rereview_count",
            "infundibulum_source_reports_morphological_change_or_complication",
            "infundibulum_source_results_reproduced_by_aurora",
            "infundibulum_public_versioned_image_dsa_reader_action_asset_identified",
            "ican_public_table_is_simulated_not_patient_evidence",
            "topaneu_target_is_vessel_location_and_segmentation_not_culprit_or_mimic_reference",
            "joined_public_ncct_cta_all_lesions_culprit_reference_patient_split_asset_identified",
            "direct_prior_threats",
            "candidates",
            "patient_set_unit_retained_as_evaluation_principle_only",
            "culprit_reference_provenance_retained_as_evaluation_principle_only",
            "symptomatic_status_and_rupture_culprit_separated",
            "surface_vector_reactivated",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "historical_score_or_job_relabelled",
            "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "culprit-lesion and mimic-differential reappraisal",
    )
    expected_culprit_mimic_candidates = [
        (
            "hemorrhage_conditioned_patient_set_evidence_alignment",
            [5.0, 5.0, 2.5, 0.5, 3.5, 5.0, 5.0, 4.0],
            30.5,
        ),
        (
            "patient_set_conformal_culprit_shortlist",
            [5.0, 5.0, 1.5, 0.5, 3.5, 5.0, 5.0, 4.0],
            29.5,
        ),
        (
            "smaller_counterpart_prospective_triage",
            [5.0, 3.0, 1.5, 1.0, 3.5, 5.0, 5.0, 4.0],
            28.0,
        ),
        (
            "infundibulum_aware_dsa_escalation",
            [4.5, 4.5, 2.0, 0.5, 1.0, 5.0, 5.0, 3.5],
            26.0,
        ),
        (
            "vwi_morphology_discordance_localization",
            [5.0, 4.5, 0.5, 0.5, 1.0, 5.0, 5.0, 4.0],
            25.5,
        ),
        (
            "longitudinal_conundrum_surveillance_deferral",
            [4.5, 2.5, 1.5, 0.5, 2.0, 5.0, 4.5, 3.5],
            24.0,
        ),
    ]
    observed_culprit_mimic_candidates = [
        (row["id"], row["axis_scores"], float(row["total"]))
        for row in culprit_mimic["candidates"]
    ]
    culprit_mimic_false_keys = [
        "primary_problem_selected",
        "paper_identity_active",
        "cta_culprit_source_results_reproduced_by_aurora",
        "cta_culprit_public_versioned_joined_image_lesion_reference_asset_identified",
        "vwi_symptomatic_source_results_reproduced_by_aurora",
        "vwi_symptomatic_status_equated_to_acute_rupture_culprit",
        "vwi_symptomatic_public_versioned_patient_image_release_identified",
        "smaller_counterpart_cross_sectional_label_is_future_rupture_estimand",
        "infundibulum_source_reports_morphological_change_or_complication",
        "infundibulum_source_results_reproduced_by_aurora",
        "infundibulum_public_versioned_image_dsa_reader_action_asset_identified",
        "joined_public_ncct_cta_all_lesions_culprit_reference_patient_split_asset_identified",
        "surface_vector_reactivated",
        "p0_registered",
        "p1_registered",
        "method_selected",
        "architecture_selected",
        "scientific_server_queried",
        "gpu_training_authorized",
        "outer_test_authorized",
        "submission_identity_active",
        "historical_score_or_job_relabelled",
        "historical_job_repaired_or_rerun",
        "login_node_gpu_command_executed",
        "junjinyong_accessed",
    ]
    if (
        culprit_mimic["status"]
        != "fresh_batch_rejected_best_30_5_fails_asset_floor_no_active_lead"
        or culprit_mimic["audit_document"]
        != "docs/culprit-lesion-and-mimic-differential-source-reappraisal-2026-08-12.md"
        or culprit_mimic["automatic_selection_threshold"] != 32.0
        or culprit_mimic["best_candidate_id"]
        != "hemorrhage_conditioned_patient_set_evidence_alignment"
        or culprit_mimic["best_score"] != 30.5
        or culprit_mimic["best_residual_novelty_score"] != 2.5
        or culprit_mimic["all_candidate_scores"]
        != [30.5, 29.5, 28.0, 26.0, 25.5, 24.0]
        or culprit_mimic["conditional_source_lead_count"] != 0
        or (
            culprit_mimic["cta_culprit_development_patients"],
            culprit_mimic["cta_culprit_development_aneurysms"],
            culprit_mimic["cta_culprit_development_hospitals"],
            culprit_mimic["cta_culprit_external_patients"],
            culprit_mimic["cta_culprit_external_aneurysms"],
            culprit_mimic["cta_culprit_external_hospitals"],
            culprit_mimic["cta_culprit_total_patients"],
            culprit_mimic["cta_culprit_total_aneurysms"],
            culprit_mimic["cta_culprit_total_hospitals"],
        )
        != (207, 460, 4, 65, 147, 4, 272, 607, 8)
        or (
            culprit_mimic["cta_culprit_source_external_auc_gaussian_process"],
            culprit_mimic["cta_culprit_source_external_auc_logistic_regression"],
            culprit_mimic["cta_culprit_source_external_auc_quadratic_discriminant"],
        )
        != (0.898, 0.892, 0.897)
        or culprit_mimic[
            "cta_culprit_reference_uses_ct_hematoma_or_neurosurgical_findings"
        ]
        is not True
        or (
            culprit_mimic["vwi_symptomatic_institutions"],
            culprit_mimic["vwi_symptomatic_patients"],
            culprit_mimic["vwi_symptomatic_aneurysms"],
            culprit_mimic["vwi_symptomatic_aneurysms_positive"],
            culprit_mimic["vwi_symptomatic_aneurysms_negative"],
        )
        != (3, 30, 82, 30, 52)
        or (
            culprit_mimic["vwi_symptomatic_source_cutoff"],
            culprit_mimic["vwi_symptomatic_source_specificity"],
            culprit_mimic["vwi_symptomatic_source_negative_predictive_value"],
        )
        != (1.02, 0.88, 0.79)
        or (
            culprit_mimic["smaller_counterpart_patients"],
            culprit_mimic["smaller_counterpart_largest_ruptured_patients"],
            culprit_mimic["smaller_counterpart_smaller_ruptured_patients"],
        )
        != (285, 261, 24)
        or culprit_mimic["smaller_counterpart_single_centre"] is not True
        or culprit_mimic["smaller_counterpart_data_request_only"] is not True
        or (
            culprit_mimic["infundibulum_total_outpouchings"],
            culprit_mimic["infundibulum_unequivocal_count"],
            culprit_mimic["infundibulum_conundrum_count"],
            culprit_mimic["infundibulum_unequivocal_followed"],
            culprit_mimic["infundibulum_conundrum_followed"],
            culprit_mimic["infundibulum_followup_lesion_years"],
            culprit_mimic["infundibulum_dsa_rereview_count"],
        )
        != (665, 321, 344, 146, 208, 1040, 10)
        or culprit_mimic["infundibulum_single_centre"] is not True
        or culprit_mimic["ican_public_table_is_simulated_not_patient_evidence"]
        is not True
        or culprit_mimic[
            "topaneu_target_is_vessel_location_and_segmentation_not_culprit_or_mimic_reference"
        ]
        is not True
        or observed_culprit_mimic_candidates
        != expected_culprit_mimic_candidates
        or any(
            sum(row["axis_scores"]) != row["total"]
            or row["critical_axis_pass"] is not False
            for row in culprit_mimic["candidates"]
        )
        or any(culprit_mimic[key] is not False for key in culprit_mimic_false_keys)
        or culprit_mimic["patient_set_unit_retained_as_evaluation_principle_only"]
        is not True
        or culprit_mimic[
            "culprit_reference_provenance_retained_as_evaluation_principle_only"
        ]
        is not True
        or culprit_mimic["symptomatic_status_and_rupture_culprit_separated"]
        is not True
        or culprit_mimic["next_allowed_action"]
        != "fresh_problem_or_material_joined_asset_audit_only_no_data_request_payload_architecture_or_compute"
    ):
        raise ProtocolError(
            "Culprit-lesion and mimic-differential candidates must remain rejected "
            "without a public joined patient-set or DSA reference asset; no request, "
            "payload, P0, method, server, GPU, outer test or claim may open."
        )
    checks.append("culprit-lesion and mimic-differential no-compute boundary")

    topbrain_rsna = problem_selection[
        "topbrain2025_and_rsna_multitask_source_correction"
    ]
    _require_keys(
        topbrain_rsna,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "topbrain2025_data_zenodo_record_id",
            "topbrain2025_data_zenodo_revision",
            "topbrain2025_data_modified",
            "topbrain2025_data_archive_name",
            "topbrain2025_data_archive_bytes",
            "topbrain2025_data_archive_md5",
            "topbrain2025_api_license_id",
            "topbrain2025_custom_download_terms_present",
            "topbrain2025_terms_accepted",
            "topbrain2025_payload_accessed",
            "topbrain2025_public_volumes",
            "topbrain2025_public_same_patient_cta_mra_pairs",
            "topbrain2025_public_independent_patients",
            "topbrain2025_cta_label_count",
            "topbrain2025_mra_label_count",
            "topbrain2025_overlapping_cta_mra_label_count",
            "topbrain2025_challenge_total_volumes",
            "topbrain2025_challenge_total_patients",
            "topbrain2025_hidden_test_volumes",
            "topbrain2025_hidden_test_patients",
            "topbrain2025_source_anatomy_classes",
            "topbrain2025_public_labels_are_whole_brain_vessel_anatomy_not_aneurysm_masks",
            "topbrain2025_independent_dense_repeated_reference_established",
            "topbrain2025_podium_zenodo_record_id",
            "topbrain2025_podium_zenodo_revision",
            "topbrain2025_podium_file_count",
            "topbrain2025_podium_docker_archive_count",
            "topbrain2025_podium_license_id",
            "topbrain2025_podium_payload_accessed",
            "topbrain2025_source_topology_and_small_branch_endpoints_present",
            "topbrain2025_source_results_reproduced_by_aurora",
            "topcow_unique_patients",
            "topcow_train_patients",
            "topcow_validation_patients",
            "topcow_test_patients",
            "topcow_same_patient_paired_cta_mra",
            "topcow_large_aneurysms_excluded_from_cow_roi",
            "topcow_external_largeia_aneurysm_patients",
            "bravecowcow_arxiv_id",
            "bravecowcow_repository",
            "bravecowcow_repository_head",
            "bravecowcow_repository_license",
            "bravecowcow_repository_release_count",
            "bravecowcow_modalities",
            "bravecowcow_aneurysm_location_classes",
            "bravecowcow_vessel_classes",
            "bravecowcow_pseudomask_training_series",
            "bravecowcow_source_public_auc",
            "bravecowcow_source_private_auc",
            "bravecowcow_source_results_reproduced_by_aurora",
            "bravecowcow_controlled_rsna_payload_accessed",
            "bravecowcow_independent_expert_dense_aneurysm_mask_benchmark_established",
            "joined_public_same_patient_cta_mra_aneurysm_mask_or_outcome_target_identified",
            "direct_prior_threats",
            "candidates",
            "patient_pair_counting_retained_as_evaluation_principle_only",
            "reference_provenance_retained_as_evaluation_principle_only",
            "vessel_anatomy_and_aneurysm_target_separation_retained_as_evaluation_principle_only",
            "surface_vector_reactivated",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "historical_score_or_job_relabelled",
            "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "TopBrain 2025 and RSNA multitask source correction",
    )
    expected_topbrain_rsna_candidates = [
        (
            "paired_cta_mra_graph_agreement_certificate",
            [4.0, 5.0, 2.0, 2.5, 3.0, 5.0, 5.0, 4.0],
            30.5,
        ),
        (
            "small_branch_failure_aware_selective_segmentation",
            [4.0, 4.5, 1.0, 2.5, 3.0, 5.0, 5.0, 4.0],
            29.0,
        ),
        (
            "paired_modality_aneurysm_location_robustness",
            [5.0, 3.5, 1.5, 1.5, 2.0, 5.0, 5.0, 3.5],
            27.0,
        ),
        (
            "reference_provenance_aware_rsna_dense_pseudolabel_audit",
            [5.0, 3.0, 2.5, 0.5, 1.0, 5.0, 5.0, 3.0],
            25.0,
        ),
        (
            "segmentation_uncertainty_to_hemodynamic_pressure_certificate",
            [5.0, 4.0, 1.5, 0.5, 1.0, 5.0, 5.0, 3.0],
            25.0,
        ),
        (
            "anatomy_conditioned_multimodal_aneurysm_segmentation",
            [5.0, 4.5, 0.5, 0.5, 1.0, 5.0, 5.0, 3.0],
            24.5,
        ),
    ]
    observed_topbrain_rsna_candidates = [
        (row["id"], row["axis_scores"], float(row["total"]))
        for row in topbrain_rsna["candidates"]
    ]
    expected_topbrain_rsna_priors = [
        "topbrain2025_same_patient_cta_mra_whole_brain_vessel_anatomy_segmentation",
        "topbrain2025_topology_contamination_small_branch_and_detection_endpoints",
        "topcow_paired_cta_mra_cow_topology_and_external_aneurysm_location_evaluation",
        "bravecowcow_multimodal_roi_multitask_aneurysm_classification_and_pseudomask_segmentation",
        "paired_data_cross_modality_cerebrovascular_segmentation",
        "multimodal_pre_post_treatment_consistency_learning",
        "generic_selective_segmentation_conformal_and_graph_consistency",
    ]
    if (
        topbrain_rsna["status"]
        != "fresh_material_source_correction_rejected_best_30_5_fails_total_novelty_and_asset_floors_no_active_lead"
        or topbrain_rsna["audit_document"]
        != "docs/topbrain-2025-release-and-rsna-multitask-source-correction-2026-08-12.md"
        or topbrain_rsna["automatic_selection_threshold"] != 32.0
        or topbrain_rsna["best_candidate_id"]
        != "paired_cta_mra_graph_agreement_certificate"
        or topbrain_rsna["best_score"] != 30.5
        or topbrain_rsna["best_residual_novelty_score"] != 2.5
        or topbrain_rsna["all_candidate_scores"]
        != [30.5, 29.0, 27.0, 25.0, 25.0, 24.5]
        or topbrain_rsna["conditional_source_lead_count"] != 0
        or (
            topbrain_rsna["topbrain2025_data_zenodo_record_id"],
            topbrain_rsna["topbrain2025_data_zenodo_revision"],
            topbrain_rsna["topbrain2025_data_modified"],
            topbrain_rsna["topbrain2025_data_archive_name"],
            topbrain_rsna["topbrain2025_data_archive_bytes"],
            topbrain_rsna["topbrain2025_data_archive_md5"],
            topbrain_rsna["topbrain2025_api_license_id"],
        )
        != (
            16878417,
            14,
            "2026-06-02T16:56:20.313691+00:00",
            "TopBrain_Data_Release_Batches1n2_081425.zip",
            1958849592,
            "b703ea31cd1f0e7115a5d3e6e61f59b3",
            None,
        )
        or (
            topbrain_rsna["topbrain2025_public_volumes"],
            topbrain_rsna["topbrain2025_public_same_patient_cta_mra_pairs"],
            topbrain_rsna["topbrain2025_public_independent_patients"],
            topbrain_rsna["topbrain2025_cta_label_count"],
            topbrain_rsna["topbrain2025_mra_label_count"],
            topbrain_rsna["topbrain2025_overlapping_cta_mra_label_count"],
        )
        != (50, 25, 25, 40, 42, 34)
        or (
            topbrain_rsna["topbrain2025_challenge_total_volumes"],
            topbrain_rsna["topbrain2025_challenge_total_patients"],
            topbrain_rsna["topbrain2025_hidden_test_volumes"],
            topbrain_rsna["topbrain2025_hidden_test_patients"],
            topbrain_rsna["topbrain2025_source_anatomy_classes"],
        )
        != (90, 45, 40, 20, 48)
        or (
            topbrain_rsna["topbrain2025_podium_zenodo_record_id"],
            topbrain_rsna["topbrain2025_podium_zenodo_revision"],
            topbrain_rsna["topbrain2025_podium_file_count"],
            topbrain_rsna["topbrain2025_podium_docker_archive_count"],
            topbrain_rsna["topbrain2025_podium_license_id"],
        )
        != (20158639, 18, 7, 5, "cc-by-4.0")
        or (
            topbrain_rsna["topcow_unique_patients"],
            topbrain_rsna["topcow_train_patients"],
            topbrain_rsna["topcow_validation_patients"],
            topbrain_rsna["topcow_test_patients"],
            topbrain_rsna["topcow_external_largeia_aneurysm_patients"],
        )
        != (200, 125, 5, 70, 12)
        or topbrain_rsna["bravecowcow_arxiv_id"] != "2606.26706"
        or topbrain_rsna["bravecowcow_repository"]
        != "PengchengShi1220/RSNA2025_Intracranial-Aneurysm-Detection"
        or topbrain_rsna["bravecowcow_repository_head"]
        != "e59e2368a722eabedc6b2228b1c6e1e7325cacd5"
        or topbrain_rsna["bravecowcow_repository_license"] != "Apache-2.0"
        or topbrain_rsna["bravecowcow_repository_release_count"] != 0
        or topbrain_rsna["bravecowcow_modalities"]
        != ["CTA", "MRA", "T2", "T1-post"]
        or (
            topbrain_rsna["bravecowcow_aneurysm_location_classes"],
            topbrain_rsna["bravecowcow_vessel_classes"],
            topbrain_rsna["bravecowcow_pseudomask_training_series"],
        )
        != (13, 13, 4348)
        or (
            topbrain_rsna["bravecowcow_source_public_auc"],
            topbrain_rsna["bravecowcow_source_private_auc"],
        )
        != (0.90035, 0.86727)
        or topbrain_rsna["direct_prior_threats"]
        != expected_topbrain_rsna_priors
        or observed_topbrain_rsna_candidates
        != expected_topbrain_rsna_candidates
        or any(row["critical_axis_pass"] for row in topbrain_rsna["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in topbrain_rsna["candidates"]
        )
        or any(
            topbrain_rsna[key] is not True
            for key in (
                "topbrain2025_custom_download_terms_present",
                "topbrain2025_public_labels_are_whole_brain_vessel_anatomy_not_aneurysm_masks",
                "topbrain2025_source_topology_and_small_branch_endpoints_present",
                "topcow_same_patient_paired_cta_mra",
                "topcow_large_aneurysms_excluded_from_cow_roi",
                "patient_pair_counting_retained_as_evaluation_principle_only",
                "reference_provenance_retained_as_evaluation_principle_only",
                "vessel_anatomy_and_aneurysm_target_separation_retained_as_evaluation_principle_only",
            )
        )
        or any(
            topbrain_rsna[key] is not False
            for key in (
                "primary_problem_selected",
                "paper_identity_active",
                "topbrain2025_terms_accepted",
                "topbrain2025_payload_accessed",
                "topbrain2025_independent_dense_repeated_reference_established",
                "topbrain2025_podium_payload_accessed",
                "topbrain2025_source_results_reproduced_by_aurora",
                "bravecowcow_source_results_reproduced_by_aurora",
                "bravecowcow_controlled_rsna_payload_accessed",
                "bravecowcow_independent_expert_dense_aneurysm_mask_benchmark_established",
                "joined_public_same_patient_cta_mra_aneurysm_mask_or_outcome_target_identified",
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_score_or_job_relabelled",
                "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or topbrain_rsna["next_allowed_action"]
        != "fresh_problem_level_source_or_material_aneurysm_target_audit_only_no_terms_payload_architecture_or_compute"
    ):
        raise ProtocolError(
            "TopBrain 2025 and BraveCoWCoW must remain a material source correction, "
            "not a patient-count inflation, aneurysm target, independent dense reference, "
            "selected method, P0 or compute authority."
        )
    checks.append("TopBrain 2025 and RSNA multitask rejected-source boundary")

    target_time = problem_selection[
        "target_time_and_instability_prediction_reappraisal"
    ]
    expected_target_time_candidates = [
        (
            "target_time_disjoint_future_event_benchmark",
            [5.0, 5.0, 3.0, 0.5, 1.0, 5.0, 5.0, 2.5],
            27.0,
        ),
        (
            "segmentation_acquisition_uncertainty_propagation_to_instability",
            [5.0, 4.5, 2.5, 0.5, 1.0, 5.0, 5.0, 3.0],
            26.5,
        ),
        (
            "cross_modality_site_conditional_pre_event_radiomics_transport",
            [5.0, 4.5, 1.5, 0.5, 1.0, 5.0, 5.0, 3.5],
            26.0,
        ),
        (
            "growth_rupture_multistate_competing_risk_prediction",
            [5.0, 5.0, 2.5, 0.5, 1.0, 5.0, 4.5, 2.0],
            25.5,
        ),
        (
            "external_centre_hemodynamic_incremental_value_over_radiomics",
            [5.0, 4.5, 2.0, 0.5, 1.0, 5.0, 5.0, 2.5],
            25.5,
        ),
        (
            "patient_grouped_centre_heldout_calibrated_selective_referral",
            [5.0, 5.0, 1.0, 0.5, 1.0, 5.0, 5.0, 3.0],
            25.5,
        ),
    ]
    observed_target_time_candidates = [
        (row["id"], row["axis_scores"], float(row["total"]))
        for row in target_time["candidates"]
    ]
    if (
        target_time["status"]
        != "fresh_batch_rejected_best_27_fails_total_asset_and_independent_unit_floors_no_active_lead"
        or target_time["audit_document"]
        != "docs/target-time-and-instability-prediction-reappraisal-2026-08-12.md"
        or target_time["automatic_selection_threshold"] != 32.0
        or target_time["best_candidate_id"]
        != "target_time_disjoint_future_event_benchmark"
        or target_time["best_score"] != 27.0
        or target_time["best_residual_novelty_score"] != 3.0
        or target_time["all_candidate_scores"]
        != [27.0, 26.5, 26.0, 25.5, 25.5, 25.5]
        or target_time["conditional_source_lead_count"] != 0
        or target_time["primary_problem_selected"] is not False
        or target_time["paper_identity_active"] is not False
        or target_time["seven_hospital_doi"]
        != "10.1016/j.jocn.2026.111974"
        or target_time["seven_hospital_pmid"] != 41843961
        or (
            target_time["seven_hospital_patients_total"],
            target_time["seven_hospital_aneurysms_total"],
            target_time["seven_hospital_centres_total"],
        )
        != (852, 1111, 7)
        or (
            target_time["seven_hospital_internal_patients"],
            target_time["seven_hospital_internal_aneurysms"],
            target_time["seven_hospital_external_patients"],
            target_time["seven_hospital_external_aneurysms"],
            target_time["seven_hospital_external_centres"],
        )
        != (646, 840, 206, 271, 6)
        or target_time["seven_hospital_modalities"] != ["CTA", "MRA", "DSA"]
        or (
            target_time["seven_hospital_source_auc_external_radiomics"],
            target_time["seven_hospital_source_auc_external_conventional"],
            target_time["seven_hospital_source_auc_external_combined"],
        )
        != (0.85, 0.61, 0.78)
        or target_time["vwi_transformer_doi"]
        != "10.3389/fnins.2026.1818110"
        or (
            target_time["vwi_transformer_patients"],
            target_time["vwi_transformer_aneurysms"],
            target_time["vwi_transformer_stable_patients"],
            target_time["vwi_transformer_stable_aneurysms"],
            target_time["vwi_transformer_unstable_patients"],
            target_time["vwi_transformer_unstable_aneurysms"],
        )
        != (293, 312, 188, 197, 105, 115)
        or (
            target_time["vwi_transformer_training_patients"],
            target_time["vwi_transformer_training_aneurysms"],
            target_time["vwi_transformer_validation_patients"],
            target_time["vwi_transformer_validation_aneurysms"],
        )
        != (205, 218, 88, 94)
        or target_time["vwi_transformer_patient_random_split_ratio"] != "7:3"
        or (
            target_time["vwi_transformer_source_validation_auc_fusion"],
            target_time["vwi_transformer_source_validation_auc_densenet169"],
            target_time[
                "vwi_transformer_source_validation_auc_radiomics_habitat"
            ],
        )
        != (0.844, 0.816, 0.721)
        or target_time["vwi_transformer_unstable_label_components"]
        != [
            "recent_ipsilateral_symptoms_before_admission",
            "growth_or_daughter_sac_on_previous_examination",
            "rupture_within_three_months_after_index_examination",
            "progression_across_two_examinations_within_six_months",
        ]
        or target_time["aneurysm_at_risk_nct"] != "NCT07111975"
        or target_time["aneurysm_at_risk_status"] != "ACTIVE_NOT_RECRUITING"
        or target_time["aneurysm_at_risk_design"]
        != "retrospective_observational_cohort"
        or (
            target_time["aneurysm_at_risk_estimated_enrollment"],
            target_time["aneurysm_at_risk_centres"],
            target_time["aneurysm_at_risk_primary_completion_estimated"],
            target_time["aneurysm_at_risk_completion_estimated"],
        )
        != (3800, 3, "2028-06", "2028-12")
        or observed_target_time_candidates != expected_target_time_candidates
        or any(row["critical_axis_pass"] for row in target_time["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in target_time["candidates"]
        )
        or any(
            target_time[key] is not False
            for key in (
                "seven_hospital_source_results_reproduced_by_aurora",
                "seven_hospital_public_versioned_patient_image_mask_release_identified",
                "seven_hospital_public_code_repository_identified",
                "seven_hospital_patient_grouping_and_centrewise_external_manifest_established_by_inspected_public_metadata",
                "vwi_transformer_independent_external_validation",
                "vwi_transformer_optimism_corrected_bootstrap",
                "vwi_transformer_source_results_reproduced_by_aurora",
                "vwi_transformer_label_is_single_pure_future_event_estimand",
                "vwi_transformer_raw_data_public_versioned_release",
                "aneurysm_at_risk_results_available",
                "aneurysm_at_risk_ipd_available_before_main_publication",
                "joined_public_timestamped_multicentre_patient_lesion_image_mask_component_outcome_asset_identified",
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_score_or_job_relabelled",
                "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or any(
            target_time[key] is not True
            for key in (
                "seven_hospital_each_patient_has_imaging_followup",
                "seven_hospital_features_use_pre_growth_or_pre_rupture_images",
                "vwi_transformer_single_centre",
                "vwi_transformer_raw_data_author_available",
                "target_time_declaration_retained_as_evaluation_principle_only",
                "component_endpoint_separation_retained_as_evaluation_principle_only",
                "external_centre_incremental_value_retained_as_evaluation_principle_only",
            )
        )
        or target_time["next_allowed_action"]
        != "fresh_problem_level_source_or_material_timestamped_asset_audit_only_no_architecture_or_compute"
    ):
        raise ProtocolError(
            "Target-time and instability prediction must remain a rejected, "
            "metadata-only batch with no timestamped multicentre public asset, "
            "P0, model, server or claim."
        )
    checks.append("target-time and instability-prediction rejected-source boundary")

    decision_time = problem_selection[
        "decision_time_and_clinical_precision_reappraisal"
    ]
    expected_decision_time_candidates = [
        (
            "acquisition_conditioned_longitudinal_morphology_precision_certificate",
            [5.0, 4.5, 2.0, 4.0, 1.5, 5.0, 5.0, 3.0],
            30.0,
        ),
        (
            "decision_time_stratified_ped_occlusion_prediction",
            [5.0, 4.5, 3.0, 0.5, 1.0, 5.0, 5.0, 2.0],
            26.0,
        ),
        (
            "preoperative_cfd_incremental_value_over_geometry",
            [5.0, 5.0, 1.0, 0.5, 1.0, 5.0, 5.0, 3.0],
            25.5,
        ),
        (
            "patient_grouped_centre_heldout_nomogram_revalidation",
            [5.0, 5.0, 0.5, 0.5, 1.0, 5.0, 4.0, 4.0],
            25.0,
        ),
        (
            "deployment_mediator_aware_dynamic_occlusion_update",
            [5.0, 4.0, 2.5, 0.5, 1.0, 4.5, 5.0, 2.0],
            24.5,
        ),
        (
            "outcome_grounded_autonomous_morphometry_and_neck_planning",
            [5.0, 3.5, 1.0, 0.5, 1.0, 5.0, 5.0, 2.0],
            23.0,
        ),
    ]
    observed_decision_time_candidates = [
        (row["id"], row["axis_scores"], float(row["total"]))
        for row in decision_time["candidates"]
    ]
    if (
        decision_time["status"]
        != "fresh_batch_rejected_best_30_fails_total_novelty_asset_and_independent_unit_floors_no_active_lead"
        or decision_time["audit_document"]
        != "docs/decision-time-and-clinical-precision-reappraisal-2026-08-12.md"
        or decision_time["automatic_selection_threshold"] != 32.0
        or decision_time["best_candidate_id"]
        != "acquisition_conditioned_longitudinal_morphology_precision_certificate"
        or decision_time["best_score"] != 30.0
        or decision_time["best_residual_novelty_score"] != 3.0
        or decision_time["all_candidate_scores"]
        != [30.0, 26.0, 25.5, 25.0, 24.5, 23.0]
        or decision_time["conditional_source_lead_count"] != 0
        or decision_time["primary_problem_selected"] is not False
        or decision_time["paper_identity_active"] is not False
        or decision_time["ped_nomogram_doi"] != "10.3389/fneur.2026.1756374"
        or decision_time["ped_nomogram_pmid"] != 41738005
        or decision_time["ped_nomogram_pmcid"] != "PMC12926474"
        or (
            decision_time["ped_nomogram_patients"],
            decision_time["ped_nomogram_aneurysms"],
            decision_time["ped_nomogram_centres"],
            decision_time["ped_nomogram_multi_aneurysm_patients_one_ped"],
        )
        != (362, 426, 4, 61)
        or (
            decision_time["ped_nomogram_development_aneurysms"],
            decision_time["ped_nomogram_validation_aneurysms"],
            decision_time["ped_nomogram_median_followup_days"],
        )
        != (298, 128, 199)
        or (
            decision_time["ped_nomogram_complete_occlusion_numerator"],
            decision_time["ped_nomogram_complete_occlusion_denominator"],
            decision_time["ped_nomogram_complete_occlusion_percent"],
        )
        != (340, 426, 79.8)
        or (
            decision_time["ped_nomogram_source_auc_development"],
            decision_time["ped_nomogram_source_auc_validation"],
        )
        != (0.785, 0.809)
        or decision_time["ped_nomogram_final_predictors"]
        != [
            "smoking",
            "flow_complexity",
            "device_migration",
            "poor_wall_apposition",
            "aneurysm_angle",
            "low_wss_area_ratio",
        ]
        or decision_time["commercial_precision_doi"]
        != "10.1186/s12880-026-02209-2"
        or decision_time["commercial_precision_pmid"] != 41654787
        or decision_time["commercial_precision_pmcid"] != "PMC12977671"
        or (
            decision_time["commercial_precision_patients"],
            decision_time["commercial_precision_aneurysms"],
            decision_time["commercial_precision_paired_cta_dsa_patients"],
            decision_time["commercial_precision_ai_platforms"],
        )
        != (148, 163, 86, 2)
        or decision_time["commercial_precision_clinical_agreement_threshold_mm"]
        != 1.0
        or decision_time["autonomous_morphometry_doi"]
        != "10.1148/ryai.251093"
        or decision_time["autonomous_morphometry_pmid"] != 42159477
        or (
            decision_time["autonomous_morphometry_patients"],
            decision_time["autonomous_morphometry_aneurysms"],
            decision_time["autonomous_morphometry_centres"],
        )
        != (2980, 2585, 5)
        or (
            decision_time["openneuro_longitudinal_patients"],
            decision_time["openneuro_same_session_control_patients"],
            decision_time["bayesian_direct_prior_public_patients_retained"],
            decision_time["bayesian_direct_prior_public_aneurysms_retained"],
            decision_time["bayesian_direct_prior_public_growth_positives"],
        )
        != (24, 4, 16, 19, 6)
        or observed_decision_time_candidates
        != expected_decision_time_candidates
        or any(row["critical_axis_pass"] for row in decision_time["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in decision_time["candidates"]
        )
        or any(
            decision_time[key] is not False
            for key in (
                "ped_nomogram_patient_grouped_split_explicitly_stated",
                "ped_nomogram_centre_held_out_validation",
                "ped_nomogram_source_results_reproduced_by_aurora",
                "ped_nomogram_pure_preoperative_information_set",
                "ped_nomogram_raw_data_public_versioned_release",
                "ped_nomogram_public_code_release_stated_in_inspected_article",
                "commercial_precision_all_method_dsa_limits_within_threshold",
                "commercial_precision_data_public_versioned_release",
                "autonomous_morphometry_public_web_platform_is_patient_training_release",
                "joined_public_timestamped_patient_centre_image_cfd_device_outcome_asset_identified",
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_score_or_job_relabelled",
                "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or any(
            decision_time[key] is not True
            for key in (
                "ped_nomogram_whole_cohort_random_split",
                "ped_nomogram_source_calls_random_holdout_external_validation",
                "ped_nomogram_preoperative_cfd_uses_normal_subject_waveform",
                "ped_nomogram_data_author_available_without_versioned_contract",
                "commercial_precision_cross_sectional_not_longitudinal",
                "commercial_precision_single_centre",
                "commercial_precision_data_reasonable_request_only",
                "information_set_declaration_retained_as_evaluation_principle_only",
                "hemodynamic_incremental_value_retained_as_evaluation_principle_only",
                "clinical_precision_before_longitudinal_claim_retained_as_evaluation_principle_only",
            )
        )
        or decision_time["next_allowed_action"]
        != "fresh_problem_level_source_or_material_asset_audit_only_no_architecture_or_compute"
    ):
        raise ProtocolError(
            "Decision-time and clinical precision must remain a rejected, "
            "paper-text-only batch with no joined timestamped patient asset, "
            "P0, model, server or claim."
        )
    checks.append("decision-time and clinical-precision rejected-source boundary")

    device_planning = problem_selection[
        "device_planning_and_mechanistic_occlusion_reappraisal"
    ]
    expected_device_planning_candidates = [
        (
            "paired_in_vitro_multidevice_response_ranking",
            [5.0, 4.0, 1.0, 3.0, 1.0, 4.5, 5.0, 3.0],
            26.5,
        ),
        (
            "selective_certificate_for_expert_consensus_ped_planning",
            [5.0, 4.0, 1.5, 0.5, 1.0, 5.0, 5.0, 3.0],
            25.0,
        ),
        (
            "mechanistic_clot_to_virtual_dsa_surrogate",
            [5.0, 5.0, 0.5, 1.0, 1.0, 4.0, 5.0, 3.0],
            24.5,
        ),
        (
            "expert_imitation_versus_outcome_optimality_audit",
            [5.0, 3.5, 2.5, 0.5, 1.0, 4.0, 5.0, 3.0],
            24.5,
        ),
        (
            "surface_flow_structure_as_clot_organization_predictor",
            [5.0, 2.5, 2.5, 1.0, 1.0, 4.0, 5.0, 3.0],
            24.0,
        ),
        (
            "outcome_grounded_counterfactual_ped_planner",
            [5.0, 4.0, 3.0, 0.5, 1.0, 3.0, 5.0, 2.0],
            23.5,
        ),
    ]
    observed_device_planning_candidates = [
        (row["id"], row["axis_scores"], float(row["total"]))
        for row in device_planning["candidates"]
    ]
    if (
        device_planning["status"]
        != "fresh_batch_rejected_best_26_5_fails_total_novelty_asset_and_independent_unit_floors_no_active_lead"
        or device_planning["audit_document"]
        != "docs/device-planning-and-mechanistic-occlusion-reappraisal-2026-08-12.md"
        or device_planning["automatic_selection_threshold"] != 32.0
        or device_planning["best_candidate_id"]
        != "paired_in_vitro_multidevice_response_ranking"
        or device_planning["best_score"] != 26.5
        or device_planning["best_residual_novelty_score"] != 3.0
        or device_planning["all_candidate_scores"]
        != [26.5, 25.0, 24.5, 24.5, 24.0, 23.5]
        or device_planning["conditional_source_lead_count"] != 0
        or device_planning["primary_problem_selected"] is not False
        or device_planning["paper_identity_active"] is not False
        or device_planning["neuraneunet_doi"] != "10.1002/cns.71047"
        or device_planning["neuraneunet_pmid"] != 42484549
        or device_planning["neuraneunet_pmcid"] != "PMC13390615"
        or (
            device_planning["neuraneunet_reported_aneurysms"],
            device_planning["neuraneunet_non_ped_aneurysms"],
            device_planning["neuraneunet_ped_treated_aneurysms"],
        )
        != (600, 390, 210)
        or (
            device_planning["neuraneunet_ped_train_cases"],
            device_planning["neuraneunet_ped_validation_cases"],
            device_planning["neuraneunet_ped_test_cases"],
        )
        != (147, 21, 42)
        or (
            device_planning["neuraneunet_reader_cohort_cases"],
            device_planning["neuraneunet_reader_count"],
            device_planning["neuraneunet_reference_consensus_senior_readers"],
        )
        != (21, 6, 3)
        or (
            device_planning["neuraneunet_source_top1_agreement_numerator"],
            device_planning["neuraneunet_source_top1_agreement_denominator"],
            device_planning["neuraneunet_source_top1_agreement_percent"],
        )
        != (20, 21, 95.2)
        or device_planning["device_thrombosis_preprint"]
        != "arXiv:2605.03536v1"
        or device_planning["device_thrombosis_representative_geometries"] != 3
        or device_planning["device_thrombosis_treatment_strategies"]
        != ["coiling", "flow_diversion", "stent_assisted_coiling"]
        or (
            device_planning["paired_treatment_4d_flow_datasets"],
            device_planning["paired_treatment_black_blood_datasets"],
            device_planning["paired_treatment_models"],
            device_planning["paired_treatment_source_patient_anatomies"],
            device_planning["paired_treatment_devices"],
        )
        != (33, 38, 5, 2, 15)
        or observed_device_planning_candidates
        != expected_device_planning_candidates
        or any(row["critical_axis_pass"] for row in device_planning["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in device_planning["candidates"]
        )
        or any(
            device_planning[key] is not False
            for key in (
                "neuraneunet_patient_disjoint_split_explicitly_stated",
                "neuraneunet_long_term_occlusion_or_safety_endpoint_evaluated",
                "neuraneunet_data_public",
                "neuraneunet_public_code_release_stated_in_inspected_paper",
                "neuraneunet_results_reproduced_by_aurora",
                "device_thrombosis_clinical_followup_validation",
                "device_thrombosis_versioned_output_release_stated_in_inspected_v1",
                "device_thrombosis_results_reproduced_by_aurora",
                "paired_treatment_archives_accessed_this_schema",
                "volume_vortex_evidence_equates_surface_wss_critical_topology",
                "joined_public_preop_device_flow_thrombus_delayed_outcome_asset_identified",
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_score_or_job_relabelled",
                "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or any(
            device_planning[key] is not True
            for key in (
                "neuraneunet_data_request_requires_ethics_and_dua",
                "device_thrombosis_models_acute_fibrin_and_virtual_dsa",
                "device_thrombosis_uses_flow_diverter_2016_challenge_geometries",
                "outcome_grounded_device_planning_retained_as_future_evaluation_template_only",
                "surface_vector_volume_vortex_motivation_retained_without_e0",
            )
        )
        or device_planning["next_allowed_action"]
        != "fresh_problem_level_source_or_material_asset_audit_only_no_architecture_or_compute"
    ):
        raise ProtocolError(
            "Device planning and mechanistic occlusion must remain a rejected, "
            "paper-text-only batch with no joined patient outcome asset, P0, model, "
            "server or claim."
        )
    checks.append("device-planning and mechanistic-occlusion rejected-source boundary")

    adam_longitudinal = problem_selection[
        "adam_longitudinal_and_treated_exclusion_source_correction"
    ]
    expected_adam_candidates = [
        (
            "patient_level_longitudinal_all_lesion_correspondence_on_adam",
            [5.0, 3.0, 2.0, 2.0, 3.5, 5.0, 5.0, 3.0],
            28.5,
        ),
        (
            "ignored_treated_region_false_output_budget",
            [5.0, 2.5, 2.0, 2.0, 3.0, 5.0, 5.0, 3.5],
            28.0,
        ),
        (
            "paired_timepoint_change_preserving_aneurysm_segmentation",
            [5.0, 3.0, 1.5, 2.0, 3.5, 5.0, 5.0, 3.0],
            28.0,
        ),
        (
            "paired_mask_growth_interval_calibration",
            [5.0, 2.5, 1.0, 2.0, 3.5, 5.0, 5.0, 3.0],
            27.0,
        ),
        (
            "baseline_followup_registration_failure_certificate",
            [4.0, 3.5, 1.5, 2.0, 3.5, 5.0, 4.5, 3.0],
            27.0,
        ),
        (
            "pre_post_treatment_semantics_reaudit_of_msdanet",
            [4.0, 2.0, 0.5, 2.0, 3.0, 5.0, 4.0, 4.0],
            24.5,
        ),
    ]
    observed_adam_candidates = [
        (row["id"], row["axis_scores"], float(row["total"]))
        for row in adam_longitudinal["candidates"]
    ]
    if (
        adam_longitudinal["status"]
        != "fresh_batch_rejected_best_28_5_fails_total_identifiability_novelty_and_asset_floors_no_active_lead"
        or adam_longitudinal["audit_document"]
        != "docs/adam-longitudinal-and-treated-exclusion-source-correction-2026-08-12.md"
        or adam_longitudinal["automatic_selection_threshold"] != 32.0
        or adam_longitudinal["best_candidate_id"]
        != "patient_level_longitudinal_all_lesion_correspondence_on_adam"
        or adam_longitudinal["best_score"] != 28.5
        or adam_longitudinal["best_residual_novelty_score"] != 2.0
        or adam_longitudinal["all_candidate_scores"]
        != [28.5, 28.0, 28.0, 27.0, 27.0, 24.5]
        or adam_longitudinal["conditional_source_lead_count"] != 0
        or adam_longitudinal["primary_problem_selected"] is not False
        or adam_longitudinal["paper_identity_active"] is not False
        or (
            adam_longitudinal["adam_training_cases"],
            adam_longitudinal["adam_training_positive_cases"],
            adam_longitudinal["adam_training_negative_cases"],
            adam_longitudinal["adam_training_paired_subjects"],
            adam_longitudinal["adam_training_unique_positive_subjects"],
        )
        != (113, 93, 20, 35, 23)
        or (
            adam_longitudinal["adam_test_cases_reported"],
            adam_longitudinal["adam_test_positive_cases_reported"],
            adam_longitudinal["adam_test_negative_cases_reported"],
            adam_longitudinal["adam_test_paired_subjects_reported"],
            adam_longitudinal["adam_test_unique_positive_subjects_reported"],
        )
        != (141, 115, 26, 43, 29)
        or adam_longitudinal["adam_label_1_semantics"]
        != "untreated_unruptured_aneurysm"
        or adam_longitudinal["adam_label_2_semantics"]
        != "treated_aneurysm_or_treatment_artifact_rough_mask"
        or adam_longitudinal["msdanet_reports_adam_baseline_or_distinct_volumes"]
        != 78
        or adam_longitudinal["msdanet_reports_adam_followup_as_posttreatment_volumes"]
        != 35
        or adam_longitudinal["growth_measurement_patients"] != 72
        or adam_longitudinal["growth_measurement_aneurysms"] != 84
        or adam_longitudinal["growth_measurement_3d_change_icc"] != 0.76
        or observed_adam_candidates != expected_adam_candidates
        or any(row["critical_axis_pass"] for row in adam_longitudinal["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in adam_longitudinal["candidates"]
        )
        or adam_longitudinal[
            "surface_vector_analysis_task_stability_sequence_retained"
        ]
        is not True
        or adam_longitudinal[
            "surface_vector_architecture_sketch_retained_as_unselected_control_set"
        ]
        is not True
        or any(
            adam_longitudinal[key] is not False
            for key in (
                "adam_test_publicly_released",
                "adam_public_exact_pair_manifest_visible",
                "adam_public_growth_adjudication_visible",
                "adam_public_lesion_correspondence_visible",
                "adam_label_2_identifies_posttreatment_remnant_or_outcome",
                "adam_terms_accepted_by_aurora",
                "adam_organizer_approval_obtained_by_aurora",
                "adam_payload_accessed_this_schema",
                "msdanet_results_reproduced_by_aurora",
                "msdanet_followup_posttreatment_equivalence_publicly_established",
                "surface_vector_material_e0_identified",
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_score_or_job_relabelled",
                "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or any(
            adam_longitudinal[key] is not True
            for key in (
                "adam_label_2_dilated_one_pixel_in_plane",
                "adam_label_2_ignored_in_official_evaluation",
                "adam_live_legacy_pages_redirect_to_grand_challenge",
                "adam_registration_and_signed_agreement_required",
                "adam_nonchallenge_reuse_requires_organizer_approval",
                "msdanet_excludes_label_2_from_evaluation",
                "msdanet_wording_treated_as_bounded_source_uncertainty",
            )
        )
        or adam_longitudinal["next_allowed_action"]
        != "fresh_problem_level_source_or_material_asset_audit_only_no_architecture_or_compute"
    ):
        raise ProtocolError(
            "ADAM longitudinal/treated-exclusion sources must remain a rejected, "
            "terms-unaccepted metadata-only batch with no P0, model, server or claim."
        )
    checks.append("ADAM longitudinal and treated-exclusion rejected-source boundary")

    diagnostic_action = problem_selection[
        "diagnostic_action_and_human_ai_reappraisal"
    ]
    _require_keys(
        diagnostic_action,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "automation_bias_paper_doi",
            "automation_bias_tof_mra_examinations",
            "automation_bias_radiologists",
            "automation_bias_false_positive_cases",
            "automation_bias_false_positive_vascular_loops",
            "automation_bias_false_positive_infundibula",
            "automation_bias_false_positive_perforators",
            "automation_bias_results_reproduced_by_aurora",
            "seven_t_mimic_patients",
            "seven_t_mimic_infundibula_clarified",
            "open_tof_model_private_cohort_patients",
            "open_tof_model_private_cohort_scans",
            "open_tof_model_adam_cases",
            "open_tof_model_weights_public",
            "open_tof_model_differential_diagnosis_patient_rows_public",
            "iavs_reported_mra_volumes",
            "iavs_reported_annotations",
            "iavs_repository_head",
            "iavs_repository_blob_paths",
            "iavs_repository_license",
            "iavs_dataset_code_or_cfd_payload_public",
            "contrast_retention_cross_sectional_aneurysms",
            "contrast_retention_longitudinal_aneurysms",
            "contrast_retention_versioned_public_patient_bundle_identified",
            "marta_treated_patients",
            "marta_endovascular_patients",
            "marta_neurosurgical_patients",
            "marta_public_patient_image_join_identified",
            "topaneu_repository_head_unchanged",
            "full_source_watch_refresh_completed",
            "full_source_watch_observation_failure",
            "aneumo_metadata_request_completed",
            "aneumo_metadata_observation_failure",
            "candidates",
            "mimic_taxonomy_retained_as_future_evaluation_only",
            "patient_recommendation_or_acquisition_action_retained_as_future_evaluation_only",
            "surface_vector_reactivated",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "historical_score_or_job_relabelled",
            "historical_job_repaired_or_rerun",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "diagnostic action and human-AI reappraisal",
    )
    expected_diagnostic_action_candidates = [
        (
            "cfd_applicability_certified_segmentation_on_iavs",
            [5.0, 5.0, 0.5, 1.0, 5.0, 5.0, 5.0, 3.0],
            29.5,
            False,
            "reject_task_directly_occupied_and_official_release_is_readme_only",
        ),
        (
            "contrast_retention_instability_functional_surrogate",
            [5.0, 4.5, 1.0, 1.0, 3.0, 5.0, 5.0, 2.5],
            27.0,
            False,
            "reject_functional_directly_occupied_and_matched_public_patient_bundle_absent",
        ),
        (
            "mimic_aware_selective_diagnosis_with_acquisition_escalation",
            [5.0, 4.0, 2.0, 1.0, 1.5, 5.0, 5.0, 2.5],
            26.0,
            False,
            "reject_paired_mimic_and_reference_asset_absent",
        ),
        (
            "real_biplane_dsa_crossview_lesion_set_localization",
            [5.0, 4.0, 0.5, 1.0, 3.0, 5.0, 5.0, 2.5],
            26.0,
            False,
            "reject_direct_prior_and_no_public_acquired_pair_contract",
        ),
        (
            "imaging_augmented_treatment_specific_marta_risk",
            [5.0, 2.0, 0.5, 1.0, 5.0, 5.0, 4.5, 2.0],
            25.0,
            False,
            "reject_counterfactual_and_joined_image_asset_absent",
        ),
        (
            "automation_bias_aware_evidence_display_policy",
            [5.0, 3.5, 1.5, 1.0, 1.5, 5.0, 5.0, 2.0],
            24.5,
            False,
            "reject_direct_human_ai_prior_and_no_development_reader_asset",
        ),
    ]
    observed_diagnostic_action_candidates = [
        (
            row["id"],
            row["axis_scores"],
            row["total"],
            row["critical_axis_pass"],
            row["decision"],
        )
        for row in diagnostic_action["candidates"]
    ]
    if (
        diagnostic_action["status"]
        != "fresh_batch_rejected_best_29_5_fails_total_novelty_and_asset_floors_no_active_lead"
        or diagnostic_action["audit_document"]
        != "docs/diagnostic-action-and-human-ai-source-reappraisal-2026-08-12.md"
        or diagnostic_action["automatic_selection_threshold"] != 32.0
        or diagnostic_action["best_candidate_id"]
        != "cfd_applicability_certified_segmentation_on_iavs"
        or diagnostic_action["best_score"] != 29.5
        or diagnostic_action["best_residual_novelty_score"] != 0.5
        or diagnostic_action["all_candidate_scores"]
        != [29.5, 27.0, 26.0, 26.0, 25.0, 24.5]
        or diagnostic_action["conditional_source_lead_count"] != 0
        or diagnostic_action["primary_problem_selected"] is not False
        or diagnostic_action["paper_identity_active"] is not False
        or diagnostic_action["automation_bias_tof_mra_examinations"] != 20
        or diagnostic_action["automation_bias_radiologists"] != 9
        or diagnostic_action["automation_bias_false_positive_cases"] != 10
        or (
            diagnostic_action["automation_bias_false_positive_vascular_loops"],
            diagnostic_action["automation_bias_false_positive_infundibula"],
            diagnostic_action["automation_bias_false_positive_perforators"],
        )
        != (5, 3, 2)
        or diagnostic_action["automation_bias_results_reproduced_by_aurora"]
        is not False
        or diagnostic_action["seven_t_mimic_patients"] != 6
        or diagnostic_action["seven_t_mimic_infundibula_clarified"] != 5
        or (
            diagnostic_action["open_tof_model_private_cohort_patients"],
            diagnostic_action["open_tof_model_private_cohort_scans"],
            diagnostic_action["open_tof_model_adam_cases"],
        )
        != (364, 385, 113)
        or diagnostic_action["open_tof_model_weights_public"] is not True
        or diagnostic_action[
            "open_tof_model_differential_diagnosis_patient_rows_public"
        ]
        is not False
        or (
            diagnostic_action["iavs_reported_mra_volumes"],
            diagnostic_action["iavs_reported_annotations"],
        )
        != (641, 587)
        or diagnostic_action["iavs_repository_head"]
        != "2e40088d9eaa671c592929a154b7b2cf99f9320a"
        or diagnostic_action["iavs_repository_blob_paths"] != ["README.md"]
        or diagnostic_action["iavs_repository_license"] is not None
        or diagnostic_action["iavs_dataset_code_or_cfd_payload_public"] is not False
        or diagnostic_action["contrast_retention_cross_sectional_aneurysms"] != 271
        or diagnostic_action["contrast_retention_longitudinal_aneurysms"] != 41
        or diagnostic_action[
            "contrast_retention_versioned_public_patient_bundle_identified"
        ]
        is not False
        or (
            diagnostic_action["marta_treated_patients"],
            diagnostic_action["marta_endovascular_patients"],
            diagnostic_action["marta_neurosurgical_patients"],
        )
        != (2647, 1907, 740)
        or diagnostic_action["marta_public_patient_image_join_identified"] is not False
        or diagnostic_action["topaneu_repository_head_unchanged"]
        != "018c243445f99199f484018c4c80575c84c72293"
        or diagnostic_action["full_source_watch_refresh_completed"] is not False
        or diagnostic_action["full_source_watch_observation_failure"]
        != "github_unauthenticated_api_http_403_rate_limit_no_source_verdict"
        or diagnostic_action["aneumo_metadata_request_completed"] is not False
        or diagnostic_action["aneumo_metadata_observation_failure"]
        != "prolonged_response_terminated_no_source_verdict"
        or observed_diagnostic_action_candidates
        != expected_diagnostic_action_candidates
        or diagnostic_action["mimic_taxonomy_retained_as_future_evaluation_only"]
        is not True
        or diagnostic_action[
            "patient_recommendation_or_acquisition_action_retained_as_future_evaluation_only"
        ]
        is not True
        or any(
            diagnostic_action[key] is not False
            for key in [
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_score_or_job_relabelled",
                "historical_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            ]
        )
        or diagnostic_action["next_allowed_action"]
        != "fresh_problem_level_source_or_material_asset_audit_only_no_architecture_or_compute"
    ):
        raise ProtocolError(
            "Diagnostic-action/human-AI sources must remain a rejected, "
            "public-metadata-only batch with no model, compute or claim."
        )
    checks.append("diagnostic action and human-AI rejected-source boundary")

    longitudinal_reliability = problem_selection[
        "longitudinal_intervention_and_patient_reliability_reappraisal"
    ]
    _require_keys(
        longitudinal_reliability,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_additive_candidate_id",
            "best_additive_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "bayesian_growth_preprint",
            "bayesian_growth_preprint_date",
            "bayesian_growth_code_release_stated",
            "bayesian_growth_internal_patients",
            "bayesian_growth_internal_aneurysms",
            "bayesian_growth_public_followup_patients_screened",
            "bayesian_growth_public_patients_included",
            "bayesian_growth_public_aneurysms_included",
            "bayesian_growth_public_pair_selection_uses_growth_event_representation",
            "bayesian_growth_reported_results_reproduced_by_aurora",
            "open_longitudinal_dataset_doi",
            "open_longitudinal_openneuro_doi",
            "open_longitudinal_patients",
            "open_longitudinal_aneurysms",
            "open_longitudinal_followup_patients",
            "open_longitudinal_multiple_aneurysm_patients",
            "open_longitudinal_payload_accessed_this_schema",
            "rsna_registry_controlled_access",
            "rsna_registry_nonredistributable",
            "rsna_registry_institutions",
            "rsna_official_wiki_coming_soon_only",
            "rsna_terms_acceptance_verified",
            "rsna_mira_access_requested",
            "rsna_payload_accessed_this_schema",
            "rsna_second_place_preprint",
            "rsna_second_place_training_series",
            "rsna_second_place_split_unit",
            "rsna_second_place_best_two_folds_selected",
            "rsna_second_place_repository_head",
            "flow_diverter_dataset_doi",
            "flow_diverter_dataset_license",
            "flow_diverter_subjects",
            "flow_diverter_procedures",
            "flow_diverter_contains_paired_pre_post_3d_images",
            "flow_diverter_payload_accessed_this_schema",
            "petra_prospective_patients",
            "petra_raw_images_public",
            "direct_prior_threats",
            "candidates",
            "patient_level_all_lesion_reliability_retained_as_evaluation_template_only",
            "surface_vector_reactivated",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "historical_vmr_or_surface_vector_score_or_job_relabelled",
            "historical_vmr_or_surface_vector_job_repaired_or_rerun",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "longitudinal/intervention/patient-reliability reappraisal",
    )
    expected_longitudinal_reliability_candidates = [
        (
            "patient_level_all_lesion_miss_risk_control_on_rsna",
            32.0,
            [5.0, 4.0, 1.5, 2.5, 4.5, 5.0, 5.0, 4.5],
        ),
        (
            "selection_audited_adjacent_vessel_longitudinal_growth_benchmark",
            31.0,
            [5.0, 3.0, 1.5, 4.5, 2.5, 5.0, 5.0, 4.5],
        ),
        (
            "flow_diverter_occlusion_prediction_from_open_procedural_table",
            29.5,
            [4.5, 3.5, 0.5, 4.5, 2.5, 5.0, 4.0, 5.0],
        ),
        (
            "multimodality_second_reader_selective_referral_on_rsna",
            29.5,
            [5.0, 3.5, 0.5, 2.5, 4.5, 5.0, 4.5, 4.0],
        ),
        (
            "local_posterior_growth_maps_with_adjacent_vessel_control",
            26.5,
            [4.5, 2.5, 1.0, 3.5, 2.5, 4.5, 5.0, 3.0],
        ),
        (
            "noninvasive_posttreatment_image_to_dsa_concordance",
            23.0,
            [5.0, 4.0, 0.5, 1.0, 2.0, 4.5, 4.5, 1.5],
        ),
    ]
    observed_longitudinal_reliability_candidates = [
        (row["id"], float(row["total"]), row["axis_scores"])
        for row in longitudinal_reliability["candidates"]
    ]
    if (
        longitudinal_reliability["status"]
        != "fresh_batch_rejected_additive_best_32_fails_residual_novelty_and_asset_floors_no_active_lead"
        or longitudinal_reliability["audit_document"]
        != "docs/longitudinal-intervention-and-patient-reliability-reappraisal-2026-08-12.md"
        or longitudinal_reliability["automatic_selection_threshold"] != 32.0
        or longitudinal_reliability["best_additive_candidate_id"]
        != "patient_level_all_lesion_miss_risk_control_on_rsna"
        or longitudinal_reliability["best_additive_score"] != 32.0
        or longitudinal_reliability["best_residual_novelty_score"] != 1.5
        or longitudinal_reliability["all_candidate_scores"]
        != [32.0, 31.0, 29.5, 29.5, 26.5, 23.0]
        or longitudinal_reliability["conditional_source_lead_count"] != 0
        or longitudinal_reliability["primary_problem_selected"] is not False
        or longitudinal_reliability["paper_identity_active"] is not False
        or longitudinal_reliability["bayesian_growth_preprint"]
        != "arXiv:2604.06649v1"
        or longitudinal_reliability["bayesian_growth_code_release_stated"] is not False
        or longitudinal_reliability["bayesian_growth_internal_patients"] != 39
        or longitudinal_reliability["bayesian_growth_internal_aneurysms"] != 42
        or longitudinal_reliability["bayesian_growth_public_followup_patients_screened"]
        != 24
        or longitudinal_reliability["bayesian_growth_public_patients_included"] != 16
        or longitudinal_reliability["bayesian_growth_public_aneurysms_included"] != 19
        or longitudinal_reliability[
            "bayesian_growth_public_pair_selection_uses_growth_event_representation"
        ]
        is not True
        or longitudinal_reliability["bayesian_growth_reported_results_reproduced_by_aurora"]
        is not False
        or longitudinal_reliability["open_longitudinal_patients"] != 63
        or longitudinal_reliability["open_longitudinal_aneurysms"] != 85
        or longitudinal_reliability["open_longitudinal_followup_patients"] != 24
        or longitudinal_reliability["open_longitudinal_multiple_aneurysm_patients"]
        != 16
        or longitudinal_reliability["rsna_registry_controlled_access"] is not True
        or longitudinal_reliability["rsna_registry_nonredistributable"] is not True
        or longitudinal_reliability["rsna_registry_institutions"] != 18
        or longitudinal_reliability["rsna_official_wiki_coming_soon_only"] is not True
        or longitudinal_reliability["rsna_second_place_training_series"] != 4348
        or longitudinal_reliability["rsna_second_place_split_unit"] != "series"
        or longitudinal_reliability["rsna_second_place_repository_head"]
        != "e59e2368a722eabedc6b2228b1c6e1e7325cacd5"
        or longitudinal_reliability["flow_diverter_dataset_doi"]
        != "10.17632/nzzx92ky6r.2"
        or longitudinal_reliability["flow_diverter_dataset_license"] != "CC-BY-4.0"
        or longitudinal_reliability["flow_diverter_subjects"] != 126
        or longitudinal_reliability["flow_diverter_procedures"] != 141
        or longitudinal_reliability["petra_prospective_patients"] != 100
        or observed_longitudinal_reliability_candidates
        != expected_longitudinal_reliability_candidates
        or any(row["critical_axis_pass"] for row in longitudinal_reliability["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in longitudinal_reliability["candidates"]
        )
        or longitudinal_reliability[
            "patient_level_all_lesion_reliability_retained_as_evaluation_template_only"
        ]
        is not True
        or any(
            longitudinal_reliability[key] is not False
            for key in (
                "open_longitudinal_payload_accessed_this_schema",
                "rsna_terms_acceptance_verified",
                "rsna_mira_access_requested",
                "rsna_payload_accessed_this_schema",
                "flow_diverter_contains_paired_pre_post_3d_images",
                "flow_diverter_payload_accessed_this_schema",
                "petra_raw_images_public",
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_vmr_or_surface_vector_score_or_job_relabelled",
                "historical_vmr_or_surface_vector_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or longitudinal_reliability["next_allowed_action"]
        != "fresh_problem_level_source_or_material_asset_audit_only_no_architecture_or_compute"
    ):
        raise ProtocolError(
            "Longitudinal/intervention/patient-reliability sources must remain a "
            "public-source-only rejected batch: the additive 32 row fails critical "
            "novelty and asset floors and cannot open P0, method, server or GPU."
        )
    checks.append("longitudinal intervention and patient-reliability rejected-source boundary")

    neck_audit = problem_selection[
        "neck_isolation_and_open_model_source_reappraisal"
    ]
    _require_keys(
        neck_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "aneusi_paper_doi",
            "aneusi_repository",
            "aneusi_repository_head",
            "aneusi_code_license",
            "aneusi_bundled_data_license",
            "aneusi_release_count",
            "aneusi_tree_truncated",
            "aneusi_blob_count",
            "aneusi_total_blob_bytes",
            "aneusi_source_files",
            "aneusi_model_files",
            "aneusi_centerline_files",
            "aneusi_neck_files",
            "aneusi_visible_base_ids",
            "aneusi_analysis_files",
            "aneusi_clip_factors",
            "aneusi_derived_vtk_per_clip_factor",
            "aneusi_requires_input_neck_polygon",
            "aneusi_cross_dataset_generalization_established",
            "aneusi_vtk_or_ods_payload_body_accessed",
            "neckspline_paper_doi",
            "neckspline_directly_predicts_continuous_neck_curve",
            "neckspline_expert_loop_training_asset_identified",
            "neckspline_stated_code_url_http_status",
            "neckspline_code_or_annotation_payload_accessed",
            "open_model_record_id",
            "open_model_record_revision",
            "open_model_version",
            "open_model_license",
            "open_model_archive_name",
            "open_model_archive_bytes",
            "open_model_archive_md5",
            "open_model_reported_positive_training_scans",
            "open_model_training_sources_include_lausanne_and_adam",
            "open_model_archive_accessed",
            "workflow_variability_paper_doi",
            "workflow_variability_transient_simulations",
            "workflow_variability_patient_specific_anatomies",
            "tar_repository",
            "tar_repository_head",
            "tar_repository_license",
            "tar_blob_count",
            "tar_total_blob_bytes",
            "direct_prior_threats",
            "candidates",
            "surface_vector_reactivated",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "historical_vmr_or_surface_vector_score_or_job_relabelled",
            "historical_vmr_or_surface_vector_job_repaired_or_rerun",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "neck-isolation/open-model source reappraisal",
    )
    expected_neck_candidates = [
        (
            "clipfactor_orbit_morphometry_stability_audit",
            31.5,
            [3.5, 4.5, 0.5, 5.0, 3.0, 5.0, 5.0, 5.0],
        ),
        (
            "neck_conditioned_roi_isolation_transfer",
            30.0,
            [4.0, 3.5, 0.5, 4.5, 3.0, 5.0, 5.0, 4.5],
        ),
        (
            "automatic_surface_neck_loop_transfer",
            29.0,
            [4.5, 3.0, 1.0, 4.0, 3.0, 4.5, 5.0, 4.0],
        ),
        (
            "differential_diagnosis_set_calibration_of_open_model",
            28.0,
            [4.5, 2.5, 0.5, 4.0, 2.0, 5.0, 5.0, 4.5],
        ),
        (
            "neck_uncertainty_to_hemodynamic_functional_certificate",
            24.0,
            [4.5, 2.0, 1.5, 2.0, 3.0, 3.5, 5.0, 2.5],
        ),
        (
            "workflow_orbit_structure_faithful_wss_surrogate",
            22.5,
            [4.5, 3.0, 1.0, 1.5, 1.0, 4.0, 5.0, 2.5],
        ),
    ]
    observed_neck_candidates = [
        (row["id"], float(row["total"]), row["axis_scores"])
        for row in neck_audit["candidates"]
    ]
    if (
        neck_audit["status"]
        != "fresh_batch_rejected_best_31_5_fails_total_and_residual_novelty_floor_no_active_lead"
        or neck_audit["audit_document"]
        != "docs/neck-isolation-and-open-model-source-reappraisal-2026-08-11.md"
        or neck_audit["automatic_selection_threshold"] != 32.0
        or neck_audit["best_candidate_id"]
        != "clipfactor_orbit_morphometry_stability_audit"
        or neck_audit["best_score"] != 31.5
        or neck_audit["best_residual_novelty_score"] != 0.5
        or neck_audit["all_candidate_scores"]
        != [31.5, 30.0, 29.0, 28.0, 24.0, 22.5]
        or neck_audit["conditional_source_lead_count"] != 0
        or neck_audit["primary_problem_selected"] is not False
        or neck_audit["paper_identity_active"] is not False
        or neck_audit["aneusi_repository_head"]
        != "5b4c454ede46c4cd56d3831cb24748c7e1521eca"
        or neck_audit["aneusi_code_license"] != "MIT"
        or neck_audit["aneusi_bundled_data_license"] != "CC-BY-NC-3.0"
        or neck_audit["aneusi_release_count"] != 0
        or neck_audit["aneusi_tree_truncated"] is not False
        or neck_audit["aneusi_blob_count"] != 1041
        or neck_audit["aneusi_total_blob_bytes"] != 977740269
        or neck_audit["aneusi_model_files"] != 103
        or neck_audit["aneusi_centerline_files"] != 103
        or neck_audit["aneusi_neck_files"] != 103
        or neck_audit["aneusi_visible_base_ids"] != 99
        or neck_audit["aneusi_analysis_files"] != 716
        or neck_audit["aneusi_clip_factors"] != [20, 25, 30, 35, 40, 45, 50]
        or neck_audit["aneusi_derived_vtk_per_clip_factor"] != 102
        or neck_audit["aneusi_requires_input_neck_polygon"] is not True
        or neck_audit["aneusi_cross_dataset_generalization_established"] is not False
        or neck_audit["neckspline_stated_code_url_http_status"] != 401
        or neck_audit["open_model_record_id"] != 17894703
        or neck_audit["open_model_record_revision"] != 4
        or neck_audit["open_model_archive_bytes"] != 1167744043
        or neck_audit["open_model_archive_md5"]
        != "3b38956f084d1570c00c47b232d6269d"
        or neck_audit["open_model_reported_positive_training_scans"] != 1094
        or neck_audit["workflow_variability_transient_simulations"] != 1024
        or neck_audit["workflow_variability_patient_specific_anatomies"] != 4
        or neck_audit["tar_repository_head"]
        != "5e852dd919feb98406067a8034dd744ddb78877f"
        or neck_audit["tar_repository_license"] is not None
        or neck_audit["tar_blob_count"] != 153
        or neck_audit["tar_total_blob_bytes"] != 4495522
        or observed_neck_candidates != expected_neck_candidates
        or any(row["critical_axis_pass"] for row in neck_audit["candidates"])
        or any(abs(sum(row["axis_scores"]) - row["total"]) > 1e-9 for row in neck_audit["candidates"])
        or any(
            neck_audit[key] is not False
            for key in (
                "aneusi_vtk_or_ods_payload_body_accessed",
                "neckspline_expert_loop_training_asset_identified",
                "neckspline_code_or_annotation_payload_accessed",
                "open_model_archive_accessed",
                "surface_vector_reactivated",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_vmr_or_surface_vector_score_or_job_relabelled",
                "historical_vmr_or_surface_vector_job_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or neck_audit["next_allowed_action"]
        != "fresh_problem_level_source_or_asset_audit_only_no_architecture_or_compute"
    ):
        raise ProtocolError(
            "Neck/isolation sources must remain a metadata-only rejected batch: "
            "AneuSI views are not patients, NeckSpline and workflow variability "
            "are direct priors, and no P0, method, server or GPU is authorized."
        )
    checks.append("neck isolation and open-model rejected-source boundary")

    vmr_growth = problem_selection["vmr_growth_paired_surface_structure_source_audit"]
    _require_keys(
        vmr_growth,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "primary_paper_doi",
            "primary_paper_patient_count",
            "primary_paper_matched_pair_count",
            "primary_paper_growing_count",
            "primary_paper_stable_count",
            "primary_paper_directly_tests_wss_osi_low_shear_and_mesh_convergence",
            "primary_paper_results_reproduced_by_aurora",
            "later_prospective_growth_prior_doi",
            "later_prospective_growth_prior_enrolled_patients",
            "later_prior_directly_reports_size_dependent_wss_growth_mechanisms",
            "vmr_project_metadata_bytes",
            "vmr_project_metadata_sha256",
            "vmr_result_metadata_bytes",
            "vmr_result_metadata_sha256",
            "vmr_size_metadata_bytes",
            "vmr_size_metadata_sha256",
            "vmr_cohort_case_rows",
            "vmr_time_resolved_surface_result_rows",
            "vmr_result_archive_count",
            "vmr_result_archive_total_bytes",
            "vmr_medical_image_or_project_zip_accessed",
            "vmr_result_archive_or_vtp_accessed_before_p0",
            "critical_structure_or_growth_association_computed",
            "direct_prior_threats",
            "candidates",
            "p0_config",
            "p0_protocol_id",
            "p0_registered",
            "p0_submitted",
            "p0_execution_server",
            "p0_cpu_only",
            "p0_gpu_count",
            "p0_public_source_commit",
            "p0_job_id",
            "p0_final_job_state",
            "p0_exit_status",
            "p0_walltime",
            "p0_cput",
            "p0_memory_kb",
            "p0_scientific_checks_total",
            "p0_scientific_checks_evaluated",
            "p0_scientific_gate_evaluated",
            "p0_aggregate_scientific_result_created",
            "p0_archive_or_vtp_access_extent_known",
            "p0_archive_or_vtp_persisted",
            "p0_raw_pbs_log_accessed",
            "p0_error_class",
            "p0_low_level_cause",
            "p0_bounded_status_bytes",
            "p0_bounded_status_sha256",
            "p0_bounded_result_bytes",
            "p0_bounded_result_sha256",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_pass_authorizes",
            "p0_failure_or_incomplete_action",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "historical_surface_vector_score_or_job_relabelled",
            "historical_surface_vector_p0_repaired_or_rerun",
            "scientific_server_queried_this_schema",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "problem_selection.vmr_growth_paired_surface_structure_source_audit",
    )
    expected_vmr_candidates = {
        "growth_paired_transient_wss_structure_stability": 32.5,
        "critical_flow_growth_biomarker": 30.5,
        "low_shear_threshold_continuum": 30.5,
        "mesh_fidelity_growth_signal": 30.0,
        "growth_paired_structure_faithful_surrogate_retention": 26.0,
        "image_to_growth_hemodynamics": 23.0,
    }
    vmr_candidates = _unique_ids(vmr_growth["candidates"], "id", "VMR candidates")
    vmr_scores = {
        row["id"]: float(row["total"]) for row in vmr_growth["candidates"]
    }
    admitted_vmr = [
        row for row in vmr_growth["candidates"] if row["critical_axis_pass"] is True
    ]
    if (
        vmr_growth["status"]
        != "historical_source_score_32_5_p0_execution_incomplete_0_of_10_exact_version_closed_without_repair"
        or vmr_growth["audit_document"]
        != "docs/vmr-growth-paired-surface-structure-source-audit-2026-08-11.md"
        or vmr_growth["best_candidate_id"]
        != "growth_paired_transient_wss_structure_stability"
        or vmr_growth["best_score"] != 32.5
        or vmr_growth["best_residual_novelty_score"] != 2.5
        or vmr_growth["all_candidate_scores"]
        != [32.5, 30.5, 30.5, 30.0, 26.0, 23.0]
        or vmr_growth["conditional_source_lead_count"] != 0
        or vmr_growth["primary_problem_selected"] is not False
        or vmr_growth["paper_identity_active"] is not False
        or vmr_growth["primary_paper_doi"] != "10.3389/fphys.2023.1300754"
        or vmr_growth["primary_paper_patient_count"] != 22
        or vmr_growth["primary_paper_matched_pair_count"] != 11
        or vmr_growth["primary_paper_growing_count"] != 11
        or vmr_growth["primary_paper_stable_count"] != 11
        or vmr_growth["primary_paper_directly_tests_wss_osi_low_shear_and_mesh_convergence"]
        is not True
        or vmr_growth["primary_paper_results_reproduced_by_aurora"] is not False
        or vmr_growth["later_prospective_growth_prior_doi"]
        != "10.1177/0271678X251325972"
        or vmr_growth["later_prospective_growth_prior_enrolled_patients"] != 481
        or vmr_growth["later_prior_directly_reports_size_dependent_wss_growth_mechanisms"]
        is not True
        or vmr_growth["vmr_project_metadata_bytes"] != 152492
        or vmr_growth["vmr_project_metadata_sha256"]
        != "d8d43c633df5fa7d7b21edf6a2b6158686fed4c6dbf0253cfffe77dcb18e19e0"
        or vmr_growth["vmr_result_metadata_bytes"] != 77713
        or vmr_growth["vmr_result_metadata_sha256"]
        != "9bf79ff7d79241c1e0b564ad4efbe7ae9da5a1405a9d3a36f3a5b5c6f39f6a14"
        or vmr_growth["vmr_size_metadata_bytes"] != 39122
        or vmr_growth["vmr_size_metadata_sha256"]
        != "0522f4b076eb82c1f85db6eb687ac97ef995506145953161cc135ec7a488ab94"
        or vmr_growth["vmr_cohort_case_rows"] != 22
        or vmr_growth["vmr_time_resolved_surface_result_rows"] != 22
        or vmr_growth["vmr_result_archive_count"] != 22
        or vmr_growth["vmr_result_archive_total_bytes"] != 1998793994
        or vmr_candidates != set(expected_vmr_candidates)
        or vmr_scores != expected_vmr_candidates
        or len(admitted_vmr) != 1
        or admitted_vmr[0]["id"]
        != "growth_paired_transient_wss_structure_stability"
        or admitted_vmr[0]["axis_scores"]
        != [4.5, 4.0, 2.5, 4.5, 3.0, 5.0, 5.0, 4.0]
        or vmr_growth["p0_config"] != "configs/vmr_growth_surface_structure_p0.json"
        or vmr_growth["p0_protocol_id"]
        != "vmr_growth_surface_structure_asset_semantics_p0_v1"
        or vmr_growth["p0_registered"] is not True
        or vmr_growth["p0_submitted"] is not True
        or vmr_growth["p0_execution_server"] != "introai9"
        or vmr_growth["p0_cpu_only"] is not True
        or vmr_growth["p0_gpu_count"] != 0
        or vmr_growth["p0_public_source_commit"]
        != "92060937529f915649fcbbc06fc2856ce45d61ea"
        or vmr_growth["p0_job_id"] != "115848.ECE-util1"
        or vmr_growth["p0_final_job_state"] != "E"
        or vmr_growth["p0_exit_status"] != 2
        or vmr_growth["p0_walltime"] != "00:04:44"
        or vmr_growth["p0_cput"] != "00:00:01"
        or vmr_growth["p0_memory_kb"] != 57084
        or vmr_growth["p0_scientific_checks_total"] != 10
        or vmr_growth["p0_scientific_checks_evaluated"] != 0
        or vmr_growth["p0_scientific_gate_evaluated"] is not False
        or vmr_growth["p0_aggregate_scientific_result_created"] is not False
        or vmr_growth["p0_archive_or_vtp_access_extent_known"] is not False
        or vmr_growth["p0_archive_or_vtp_persisted"] is not False
        or vmr_growth["p0_raw_pbs_log_accessed"] is not False
        or vmr_growth["p0_error_class"] != "VMRGrowthSurfaceStructureP0Error"
        or vmr_growth["p0_low_level_cause"] is not None
        or vmr_growth["p0_bounded_status_bytes"] != 325
        or vmr_growth["p0_bounded_status_sha256"]
        != "d4c67a168be0fc90fa21073048b8b00096dcb33ccff48e2ce471221921b4523f"
        or vmr_growth["p0_bounded_result_bytes"] != 980
        or vmr_growth["p0_bounded_result_sha256"]
        != "6ec0067b9c349810aa625066e47ffa626442920e2c09e79ab96b04054a35f51f"
        or vmr_growth["p0_execution_record"]
        != "results/vmr_growth_surface_structure_p0_execution_20260811.json"
        or vmr_growth["p0_execution_record_sha256"]
        != "c3c7c5f4984436b43cde94ed8f76f3abe006ba15d027f22ae43b1bf5b97e18a1"
        or vmr_growth["p0_pass_authorizes"]
        != "register_separate_method_free_cpu_only_p1_mesh_phase_tolerance_and_perturbation_stability_audit_only"
        or vmr_growth["p0_failure_or_incomplete_action"]
        != "close_exact_candidate_version_without_same_contract_repair_or_rerun"
        or vmr_growth["p1_registered"] is not False
        or any(
            vmr_growth[key] is not False
            for key in (
                "vmr_medical_image_or_project_zip_accessed",
                "vmr_result_archive_or_vtp_accessed_before_p0",
                "critical_structure_or_growth_association_computed",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "historical_surface_vector_score_or_job_relabelled",
                "historical_surface_vector_p0_repaired_or_rerun",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or vmr_growth["scientific_server_queried_this_schema"] is not True
        or vmr_growth["next_allowed_action"]
        != "fresh_problem_level_source_or_asset_audit_only_no_same_contract_repair_or_rerun"
    ):
        raise ProtocolError(
            "The VMR audit must preserve the 32.5 source history and exact "
            "115848 execution-incomplete CPU P0 record with 0/10 checks, unknown "
            "access extent, no persisted payload and no repair or P1 authority."
        )
    checks.append("VMR growth-paired closed execution-incomplete P0 boundary")

    latent_transport = problem_selection[
        "latent_shape_open_cta_transport_reappraisal"
    ]
    _require_keys(
        latent_transport,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_doi",
            "paper_patient_derived_surfaces",
            "paper_ruptured_status_surfaces",
            "paper_source_dataset_count",
            "paper_lodo_accuracy",
            "paper_lodo_auc",
            "paper_lodo_ae_mse",
            "paper_lodo_vae_mse",
            "paper_results_reproduced_by_aurora",
            "repository",
            "repository_head",
            "repository_license",
            "processed_obj_dataset_tracked",
            "rupture_labels_csv_tracked",
            "released_model_weights_present",
            "released_aggregate_latent_caches_present",
            "loo_loader_present",
            "released_training_scripts_use_default_seed42_file_level_80_20_split",
            "released_complete_lodo_driver_and_fold_manifest_present",
            "unknown_status_label_condition_is_always_truthy",
            "paper_results_invalidated_by_static_code_audit",
            "vae_3k_cache_sha256",
            "vae_3k_cache_rows",
            "vae_3k_cache_unique_ids",
            "vae_3k_cache_nonblank_hospital",
            "vae_3k_cache_nonblank_status",
            "vae_3k_cache_ruptured_status",
            "cache_to_paper_patient_mapping_present",
            "open_cta_record_id",
            "open_cta_record_revision",
            "open_cta_license",
            "open_cta_archive_bytes",
            "open_cta_archive_md5",
            "open_cta_cases",
            "open_cta_positive_cases",
            "open_cta_lesions",
            "open_cta_miliary_lesions",
            "open_cta_ruptured_lesion_rows",
            "open_cta_stl_payload_accessed_this_schema",
            "open_cta_dicom_pixel_accessed_this_schema",
            "open_cta_stl_ostium_topology_compatibility_identified",
            "expert_morphology_category_treated_as_latent_support_ground_truth",
            "direct_prior_threats",
            "candidates",
            "surface_vector_retained_only_as_inactive_falsifiable_question",
            "open_cta_physical_grid_or_surface_vector_job_repaired_or_rerun",
            "historical_scores_or_job_outcomes_relabelled",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "latent-shape/open-CTA transport reappraisal",
    )
    expected_latent_transport_candidates = [
        (
            "released_code_paper_contract_reproducibility_audit",
            29.5,
            [3.5, 4.0, 0.5, 4.0, 4.0, 5.0, 4.5, 4.0],
        ),
        (
            "source_disjoint_latent_transport_reliability",
            29.0,
            [4.0, 4.0, 0.5, 3.5, 4.0, 5.0, 4.5, 3.5],
        ),
        (
            "miliary_shape_support_abstention",
            28.5,
            [4.5, 3.0, 1.5, 3.0, 3.5, 5.0, 5.0, 3.0],
        ),
        (
            "support_certified_saccular_model_transport_to_open_cta",
            28.0,
            [4.0, 3.0, 1.5, 3.0, 3.5, 5.0, 5.0, 3.0],
        ),
        (
            "nonsaccular_topology_aware_registration_extension",
            28.0,
            [4.0, 2.5, 2.0, 3.0, 3.5, 5.0, 5.0, 3.0],
        ),
        (
            "open_cta_rupture_selective_prediction",
            23.0,
            [4.5, 1.5, 1.0, 3.0, 1.0, 5.0, 4.5, 2.5],
        ),
    ]
    observed_latent_transport_candidates = [
        (candidate["id"], candidate["total"], candidate["axis_scores"])
        for candidate in latent_transport["candidates"]
    ]
    latent_transport_sums_match = all(
        abs(sum(candidate["axis_scores"]) - candidate["total"]) < 1e-9
        for candidate in latent_transport["candidates"]
    )
    latent_transport_false_boundaries = [
        "paper_results_reproduced_by_aurora",
        "processed_obj_dataset_tracked",
        "rupture_labels_csv_tracked",
        "released_complete_lodo_driver_and_fold_manifest_present",
        "paper_results_invalidated_by_static_code_audit",
        "cache_to_paper_patient_mapping_present",
        "open_cta_stl_payload_accessed_this_schema",
        "open_cta_dicom_pixel_accessed_this_schema",
        "open_cta_stl_ostium_topology_compatibility_identified",
        "expert_morphology_category_treated_as_latent_support_ground_truth",
        "open_cta_physical_grid_or_surface_vector_job_repaired_or_rerun",
        "historical_scores_or_job_outcomes_relabelled",
        "p0_registered",
        "p1_registered",
        "method_selected",
        "architecture_selected",
        "scientific_server_queried",
        "gpu_training_authorized",
        "outer_test_authorized",
        "submission_identity_active",
        "login_node_gpu_command_executed",
        "junjinyong_accessed",
    ]
    if (
        latent_transport["status"]
        != "fresh_batch_rejected_best_29_5_fails_total_residual_novelty_and_identifiability_floors"
        or latent_transport["audit_document"]
        != "docs/latent-shape-open-cta-transport-reappraisal-2026-08-11.md"
        or latent_transport["automatic_selection_threshold"] != 32.0
        or latent_transport["best_candidate_id"]
        != "released_code_paper_contract_reproducibility_audit"
        or latent_transport["best_score"] != 29.5
        or latent_transport["best_residual_novelty_score"] != 2.0
        or latent_transport["all_candidate_scores"]
        != [29.5, 29.0, 28.5, 28.0, 28.0, 23.0]
        or latent_transport["conditional_source_lead_count"] != 0
        or latent_transport["primary_problem_selected"] is not False
        or latent_transport["paper_doi"] != "10.1016/j.cmpb.2026.109445"
        or latent_transport["paper_patient_derived_surfaces"] != 958
        or latent_transport["paper_ruptured_status_surfaces"] != 338
        or latent_transport["paper_source_dataset_count"] != 5
        or latent_transport["paper_lodo_accuracy"] != 0.68
        or latent_transport["paper_lodo_auc"] != 0.66
        or latent_transport["paper_lodo_ae_mse"] != 0.16
        or latent_transport["paper_lodo_vae_mse"] != 0.14
        or latent_transport["repository"]
        != "PepeEulzer/aneurysm-latent-space"
        or latent_transport["repository_head"]
        != "43e8219e947cfa318ab83a01df01c6602e7d5756"
        or latent_transport["repository_license"] != "MIT"
        or latent_transport["released_model_weights_present"] is not True
        or latent_transport["released_aggregate_latent_caches_present"] is not True
        or latent_transport["loo_loader_present"] is not True
        or latent_transport[
            "released_training_scripts_use_default_seed42_file_level_80_20_split"
        ]
        is not True
        or latent_transport["unknown_status_label_condition_is_always_truthy"]
        is not True
        or latent_transport["vae_3k_cache_sha256"]
        != "4ceafa78bee07a50f94b844840ba7c94b64ca3414258ec06ca431f82fded3173"
        or latent_transport["vae_3k_cache_rows"] != 885
        or latent_transport["vae_3k_cache_unique_ids"] != 885
        or latent_transport["vae_3k_cache_nonblank_hospital"] != 749
        or latent_transport["vae_3k_cache_nonblank_status"] != 734
        or latent_transport["vae_3k_cache_ruptured_status"] != 261
        or latent_transport["open_cta_record_id"] != 15697196
        or latent_transport["open_cta_record_revision"] != 4
        or latent_transport["open_cta_license"] != "cc-by-4.0"
        or latent_transport["open_cta_archive_bytes"] != 25578845008
        or latent_transport["open_cta_archive_md5"]
        != "264ff9ee868c022d108b7c7aa7396d32"
        or latent_transport["open_cta_cases"] != 172
        or latent_transport["open_cta_positive_cases"] != 82
        or latent_transport["open_cta_lesions"] != 122
        or latent_transport["open_cta_miliary_lesions"] != 30
        or latent_transport["open_cta_ruptured_lesion_rows"] != 9
        or observed_latent_transport_candidates
        != expected_latent_transport_candidates
        or not latent_transport_sums_match
        or any(
            candidate["critical_axis_pass"]
            for candidate in latent_transport["candidates"]
        )
        or any(latent_transport[key] for key in latent_transport_false_boundaries)
        or latent_transport[
            "surface_vector_retained_only_as_inactive_falsifiable_question"
        ]
        is not True
        or latent_transport["execution_server"] != "introai9"
        or latent_transport["next_allowed_action"]
        != "continue_fresh_problem_level_source_audit_or_wait_for_patient_mapped_latent_release_and_distinct_failure_target"
    ):
        raise ProtocolError(
            "The latent-shape/open-CTA reappraisal must preserve the source "
            "paper's own LODO failure, the exact code/cache mismatch boundary, "
            "all six critical-floor rejections, closed historical P0s and zero "
            "payload or compute authority."
        )
    checks.append("latent-shape/open-CTA transport rejection boundary")

    synva_audit = problem_selection["synva_release_and_synthetic_utility_source_audit"]
    _require_keys(
        synva_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "arxiv_id",
            "arxiv_version",
            "arxiv_submitted_on",
            "paper_pdf_bytes",
            "paper_pdf_sha256",
            "paper_claimed_synthetic_samples",
            "paper_reported_synthetic_train_samples",
            "paper_reported_synthetic_validation_samples",
            "paper_reported_real_processed_samples",
            "paper_reported_real_test_samples",
            "paper_reported_downstream_regimes",
            "paper_reported_synthetic_only_real_test_miou",
            "paper_reported_ten_percent_real_only_miou",
            "paper_reported_synthetic_pretrain_ten_percent_real_miou",
            "paper_results_reproduced_by_aurora",
            "dedicated_synva_code_url_present_in_paper",
            "dedicated_synva_dataset_url_present_in_paper",
            "public_synva_github_repository_found",
            "versioned_release_manifest_present",
            "explicit_release_license_present",
            "immutable_release_checksums_present",
            "executable_real_split_manifest_present",
            "patient_grouped_real_split_explicitly_reported",
            "paper_reports_dataset_stratified_real_split",
            "procedural_samples_are_patients",
            "procedural_samples_reported_independently_sampled",
            "hemodynamic_construct_validity_reported",
            "clinical_or_rupture_construct_validity_reported",
            "direct_prior_threats",
            "candidates",
            "surface_vector_retained_only_as_inactive_falsifiable_question",
            "closed_surface_vector_or_aneurisk_job_repaired_or_rerun",
            "historical_scores_or_job_outcomes_relabelled",
            "recurring_source_watch_added",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "SynVA release and synthetic-utility source audit",
    )
    expected_synva_candidates = [
        (
            "ostium_segmentation_with_synva_pretraining",
            27.5,
            [4.0, 5.0, 0.5, 1.0, 4.0, 5.0, 5.0, 3.0],
        ),
        (
            "procedural_intervention_effect_audit",
            26.5,
            [3.5, 4.0, 1.0, 1.0, 4.0, 5.0, 5.0, 3.0],
        ),
        (
            "source_disjoint_synthetic_pretraining_utility",
            26.0,
            [4.0, 3.5, 1.5, 1.0, 4.0, 5.0, 4.5, 2.5],
        ),
        (
            "morphology_support_calibrated_synthetic_curriculum",
            26.0,
            [4.0, 3.0, 1.5, 1.0, 4.0, 5.0, 5.0, 2.5],
        ),
        (
            "synthetic_to_real_hemodynamic_pretraining",
            23.5,
            [4.5, 1.5, 1.0, 0.5, 4.0, 5.0, 5.0, 2.0],
        ),
        (
            "patient_privacy_or_membership_audit",
            23.5,
            [2.5, 5.0, 0.5, 1.0, 4.0, 5.0, 2.5, 3.0],
        ),
    ]
    observed_synva_candidates = [
        (candidate["id"], candidate["total"], candidate["axis_scores"])
        for candidate in synva_audit["candidates"]
    ]
    synva_score_sums_match = all(
        abs(sum(candidate["axis_scores"]) - candidate["total"]) < 1e-9
        for candidate in synva_audit["candidates"]
    )
    synva_false_boundaries = [
        "paper_results_reproduced_by_aurora",
        "dedicated_synva_code_url_present_in_paper",
        "dedicated_synva_dataset_url_present_in_paper",
        "public_synva_github_repository_found",
        "versioned_release_manifest_present",
        "explicit_release_license_present",
        "immutable_release_checksums_present",
        "executable_real_split_manifest_present",
        "patient_grouped_real_split_explicitly_reported",
        "procedural_samples_are_patients",
        "hemodynamic_construct_validity_reported",
        "clinical_or_rupture_construct_validity_reported",
        "closed_surface_vector_or_aneurisk_job_repaired_or_rerun",
        "historical_scores_or_job_outcomes_relabelled",
        "recurring_source_watch_added",
        "p0_registered",
        "p1_registered",
        "method_selected",
        "architecture_selected",
        "scientific_server_queried",
        "gpu_training_authorized",
        "outer_test_authorized",
        "submission_identity_active",
        "login_node_gpu_command_executed",
        "junjinyong_accessed",
    ]
    if (
        synva_audit["status"]
        != "fresh_batch_rejected_best_27_5_fails_total_residual_novelty_and_asset_floors_synva_release_contract_absent"
        or synva_audit["audit_document"]
        != "docs/synva-release-and-synthetic-utility-source-audit-2026-08-11.md"
        or synva_audit["automatic_selection_threshold"] != 32.0
        or synva_audit["best_candidate_id"]
        != "ostium_segmentation_with_synva_pretraining"
        or synva_audit["best_score"] != 27.5
        or synva_audit["best_residual_novelty_score"] != 1.5
        or synva_audit["all_candidate_scores"]
        != [27.5, 26.5, 26.0, 26.0, 23.5, 23.5]
        or synva_audit["conditional_source_lead_count"] != 0
        or synva_audit["primary_problem_selected"] is not False
        or synva_audit["arxiv_id"] != "2605.17620"
        or synva_audit["arxiv_version"] != "v1"
        or synva_audit["arxiv_submitted_on"] != "2026-05-13"
        or synva_audit["paper_pdf_bytes"] != 25831786
        or synva_audit["paper_pdf_sha256"]
        != "f483f6b91bf8ab94d55dd456e22ea108468780131c9df9dcbcaff46d9f2d92fe"
        or synva_audit["paper_claimed_synthetic_samples"] != 50000
        or synva_audit["paper_reported_synthetic_train_samples"] != 40000
        or synva_audit["paper_reported_synthetic_validation_samples"] != 10000
        or synva_audit["paper_reported_real_processed_samples"] != 769
        or synva_audit["paper_reported_real_test_samples"] != 100
        or synva_audit["paper_reported_downstream_regimes"] != 11
        or synva_audit["paper_reported_synthetic_only_real_test_miou"] != 36.78
        or synva_audit["paper_reported_ten_percent_real_only_miou"] != 50.41
        or synva_audit["paper_reported_synthetic_pretrain_ten_percent_real_miou"]
        != 63.88
        or any(synva_audit[key] for key in synva_false_boundaries)
        or synva_audit["paper_reports_dataset_stratified_real_split"] is not True
        or synva_audit["procedural_samples_reported_independently_sampled"]
        is not True
        or observed_synva_candidates != expected_synva_candidates
        or not synva_score_sums_match
        or any(candidate["critical_axis_pass"] for candidate in synva_audit["candidates"])
        or synva_audit[
            "surface_vector_retained_only_as_inactive_falsifiable_question"
        ]
        is not True
        or synva_audit["execution_server"] != "introai9"
        or synva_audit["next_allowed_action"]
        != "wait_for_versioned_synva_code_dataset_license_checksum_and_split_contract_or_fresh_unrelated_problem_level_source_audit"
    ):
        raise ProtocolError(
            "The SynVA v1 source audit must preserve the claimed-but-unreleased "
            "50k asset boundary, the source paper's own synthetic-to-real utility "
            "experiment, all six prospective rejections, and zero compute authority."
        )
    checks.append("SynVA release and synthetic-utility rejection boundary")

    reference_audit = problem_selection[
        "reference_provenance_and_rsna_release_contract_reappraisal"
    ]
    _require_keys(
        reference_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_ids",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "registry_repository",
            "registry_file_path",
            "registry_file_commit_sha",
            "registry_blob_sha",
            "registry_file_bytes",
            "registry_file_sha256",
            "registry_scans_reported",
            "registry_radiologists_reported",
            "registry_institutions_reported",
            "registry_ai_segmented_studies_reported",
            "controlled_access_declared",
            "data_resource_publication_forthcoming",
            "noncommercial_no_redistribution_terms_declared",
            "wiki_repository_head",
            "wiki_page_bytes",
            "wiki_page_sha256",
            "wiki_page_is_coming_soon_only",
            "machine_auditable_release_contract_present",
            "public_patient_manifest_present",
            "public_split_contract_present",
            "public_annotation_lineage_and_adjudication_contract_present",
            "clean_reference_subset_public",
            "about_200_ai_segmentations_treated_as_independent_lesion_masks",
            "user_terms_acceptance_verified",
            "mira_access_requested",
            "registry_s3_medical_or_case_level_payload_accessed",
            "direct_prior_threats",
            "candidates",
            "surface_vector_retained_only_as_inactive_falsifiable_question",
            "surface_vector_closed_job_repaired_or_rerun",
            "historical_scores_or_job_outcomes_relabelled",
            "recurring_source_watch_added",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "reference-provenance and RSNA release-contract reappraisal",
    )
    expected_reference_scores = [31.0, 31.0, 29.5, 28.5, 28.0, 25.5]
    expected_reference_candidates = [
        (
            "topaneu_revision_robust_lesion_set_ranking_interval",
            31.0,
            [4.0, 4.0, 1.0, 4.0, 4.0, 5.0, 5.0, 4.0],
        ),
        (
            "versioned_morphometry_partial_identification",
            31.0,
            [4.5, 3.5, 2.0, 3.5, 4.0, 5.0, 5.0, 3.5],
        ),
        (
            "rsna_clean_calibration_subgroup_risk_bound",
            29.5,
            [5.0, 3.0, 1.5, 2.0, 5.0, 5.0, 4.5, 3.5],
        ),
        (
            "reference_provenance_conditioned_segmentation",
            28.5,
            [4.5, 3.0, 1.0, 3.0, 4.0, 5.0, 4.5, 3.5],
        ),
        (
            "active_review_allocation_by_morphometric_utility",
            28.0,
            [4.5, 3.0, 0.5, 3.0, 4.0, 5.0, 4.5, 3.5],
        ),
        (
            "subgroup_biased_ruler_audit_for_aneurysm_masks",
            25.5,
            [4.5, 2.0, 0.5, 2.0, 4.0, 5.0, 4.0, 3.5],
        ),
    ]
    observed_reference_candidates = [
        (candidate.get("id"), candidate.get("total"), candidate.get("axis_scores"))
        for candidate in reference_audit["candidates"]
    ]
    if (
        reference_audit["status"]
        != "fresh_batch_rejected_best_31_fails_total_and_residual_novelty_floors_rsna_release_contract_incomplete"
        or reference_audit["audit_document"]
        != "docs/reference-provenance-and-rsna-release-contract-reappraisal-2026-08-11.md"
        or reference_audit["automatic_selection_threshold"] != 32.0
        or reference_audit["best_candidate_ids"]
        != [
            "topaneu_revision_robust_lesion_set_ranking_interval",
            "versioned_morphometry_partial_identification",
        ]
        or reference_audit["best_score"] != 31.0
        or reference_audit["best_residual_novelty_score"] != 2.0
        or reference_audit["all_candidate_scores"] != expected_reference_scores
        or observed_reference_candidates != expected_reference_candidates
        or any(
            candidate["critical_axis_pass"] is not False
            or sum(candidate["axis_scores"]) != candidate["total"]
            for candidate in reference_audit["candidates"]
        )
        or reference_audit["conditional_source_lead_count"] != 0
        or reference_audit["primary_problem_selected"] is not False
        or reference_audit["registry_repository"] != "awslabs/open-data-registry"
        or reference_audit["registry_file_path"]
        != "datasets/rsna-intracranial-aneurysm-detection-dataset.yaml"
        or reference_audit["registry_file_commit_sha"]
        != "523ffd3914ba99e6c4b17441f1633cc3eec74c69"
        or reference_audit["registry_blob_sha"]
        != "97b8c1f16b2809d2e82ec0c39d3b156b174c8c83"
        or reference_audit["registry_file_bytes"] != 2626
        or reference_audit["registry_file_sha256"]
        != "864f0716a8f6618e90f4c257c417f599fd6bb454abe73fc06eee8e771d3d8a10"
        or reference_audit["registry_scans_reported"] != "over_4000"
        or reference_audit["registry_radiologists_reported"] != "over_40"
        or reference_audit["registry_institutions_reported"] != 18
        or reference_audit["registry_ai_segmented_studies_reported"]
        != "about_200"
        or reference_audit["controlled_access_declared"] is not True
        or reference_audit["data_resource_publication_forthcoming"] is not True
        or reference_audit["noncommercial_no_redistribution_terms_declared"]
        is not True
        or reference_audit["wiki_repository_head"]
        != "11dcd6571b312543b63f059617e5f34c265b984b"
        or reference_audit["wiki_page_bytes"] != 11
        or reference_audit["wiki_page_sha256"]
        != "4f7d64017689437e6d93f5724f3f797054f3935d98a13148025b616b8db8fb2c"
        or reference_audit["wiki_page_is_coming_soon_only"] is not True
        or reference_audit[
            "surface_vector_retained_only_as_inactive_falsifiable_question"
        ]
        is not True
        or reference_audit["recurring_source_watch_added"] is not True
        or any(
            reference_audit[key] is not False
            for key in (
                "machine_auditable_release_contract_present",
                "public_patient_manifest_present",
                "public_split_contract_present",
                "public_annotation_lineage_and_adjudication_contract_present",
                "clean_reference_subset_public",
                "about_200_ai_segmentations_treated_as_independent_lesion_masks",
                "user_terms_acceptance_verified",
                "mira_access_requested",
                "registry_s3_medical_or_case_level_payload_accessed",
                "surface_vector_closed_job_repaired_or_rerun",
                "historical_scores_or_job_outcomes_relabelled",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or reference_audit["execution_server"] != "introai9"
        or reference_audit["next_allowed_action"]
        != "wait_for_material_rsna_release_contract_change_or_fresh_unrelated_problem_level_source_audit_no_terms_payload_p0_or_model"
    ):
        raise ProtocolError(
            "The reference-provenance and RSNA release-contract batch must remain "
            "source-only, below the non-compensatory gate and without terms, "
            "payload, P0, model, server query or compute."
        )
    checks.append("reference-provenance and RSNA release-contract rejection boundary")

    topaneu_release = problem_selection[
        "topaneu_registered_design_and_realized_release_reappraisal"
    ]
    _require_keys(
        topaneu_release,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "paper_identity_active",
            "miccai_registry_doi",
            "zenodo_record_id",
            "zenodo_revision",
            "zenodo_design_pdf_pages",
            "zenodo_design_pdf_bytes",
            "zenodo_design_pdf_md5",
            "zenodo_record_license",
            "zenodo_license_applies_to_medical_release",
            "medical_data_license",
            "registered_task1_train_volumes",
            "registered_private_test_volumes",
            "registered_public_source_train_volumes",
            "registered_train_gold_vessel_masks",
            "registered_test_gold_vessel_masks",
            "registered_minimum_positive_per_location_per_split",
            "registered_minimum_nonaneurysm_control_fraction",
            "registered_annotation_verifier_count_per_label_or_mask",
            "registered_multi_annotator_merge_performed",
            "realized_training_scans",
            "realized_unique_patients",
            "realized_unique_patient_source_counts",
            "realized_held_out_test_center",
            "realized_location_classes",
            "realized_aneurysm_types",
            "realized_vessel_masks_described_as_organizer_topbrain_predictions",
            "realized_casewise_gold_silver_indicator_publicly_exposed",
            "realized_complete_patient_grouped_split_manifest_publicly_exposed",
            "realized_test_case_manifest_publicly_exposed",
            "realized_minimum_location_support_verified_from_public_contract",
            "realized_control_fraction_verified_from_public_contract",
            "official_repository",
            "official_repository_head",
            "official_task1_true_negative_is_standard_patient_class_tn",
            "official_task2_active_path_is_instance_connected_component_evaluation",
            "direct_prior_threats",
            "candidates",
            "historical_topaneu_scores_relabelled",
            "surface_vector_reactivated",
            "surface_vector_closed_job_repaired_or_rerun",
            "user_terms_acceptance_verified",
            "challenge_joined",
            "medical_image_mask_json_or_annotation_payload_accessed",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "existing_source_watch_v20_reused_without_duplicate_watch",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "TopAneu registered-design and realized-release reappraisal",
    )
    expected_topaneu_release_candidates = [
        (
            "topaneu_official_metric_instance_collapse_aware_evaluation",
            [4.0, 5.0, 0.5, 5.0, 4.5, 5.0, 3.5, 4.0],
            31.5,
        ),
        (
            "topaneu_registered_to_realized_benchmark_contract_fidelity",
            [4.0, 4.5, 0.5, 5.0, 4.0, 5.0, 3.5, 4.0],
            30.5,
        ),
        (
            "topaneu_external_centre_modality_generalization",
            [5.0, 3.0, 0.5, 2.0, 4.0, 5.0, 5.0, 3.0],
            27.5,
        ),
        (
            "topaneu_gold_silver_provenance_conditioned_generalization",
            [4.5, 2.0, 1.0, 2.0, 4.0, 5.0, 5.0, 3.0],
            26.5,
        ),
        (
            "topaneu_bifurcation_uncertainty_aware_fine_location",
            [5.0, 1.5, 2.0, 2.0, 3.5, 4.5, 5.0, 3.0],
            26.5,
        ),
        (
            "topaneu_longitudinal_patient_set_consistency_v2",
            [4.5, 1.0, 1.5, 2.0, 0.5, 4.0, 5.0, 2.0],
            20.5,
        ),
    ]
    observed_topaneu_release_candidates = [
        (row["id"], row["axis_scores"], float(row["total"]))
        for row in topaneu_release["candidates"]
    ]
    if (
        topaneu_release["status"]
        != "fresh_batch_rejected_best_31_5_fails_total_and_residual_novelty_floors_no_active_lead"
        or topaneu_release["audit_document"]
        != "docs/topaneu-registered-design-and-realized-release-reappraisal-2026-08-12.md"
        or topaneu_release["automatic_selection_threshold"] != 32.0
        or topaneu_release["best_candidate_id"]
        != "topaneu_official_metric_instance_collapse_aware_evaluation"
        or topaneu_release["best_score"] != 31.5
        or topaneu_release["best_residual_novelty_score"] != 0.5
        or topaneu_release["all_candidate_scores"]
        != [31.5, 30.5, 27.5, 26.5, 26.5, 20.5]
        or topaneu_release["conditional_source_lead_count"] != 0
        or topaneu_release["miccai_registry_doi"]
        != "10.5281/zenodo.19848807"
        or (
            topaneu_release["zenodo_record_id"],
            topaneu_release["zenodo_revision"],
            topaneu_release["zenodo_design_pdf_pages"],
            topaneu_release["zenodo_design_pdf_bytes"],
            topaneu_release["zenodo_design_pdf_md5"],
        )
        != (
            19848807,
            4,
            37,
            150978,
            "773b04597d4ff2c798837fb5d40b4bf9",
        )
        or topaneu_release["zenodo_record_license"] != "cc-by-4.0"
        or topaneu_release["medical_data_license"]
        != "custom_data_usage_agreement"
        or (
            topaneu_release["registered_task1_train_volumes"],
            topaneu_release["registered_private_test_volumes"],
            topaneu_release["registered_public_source_train_volumes"],
            topaneu_release["registered_train_gold_vessel_masks"],
            topaneu_release["registered_test_gold_vessel_masks"],
        )
        != (500, 350, 200, 50, 20)
        or (
            topaneu_release["realized_training_scans"],
            topaneu_release["realized_unique_patients"],
            topaneu_release["realized_location_classes"],
            topaneu_release["realized_aneurysm_types"],
        )
        != (417, 409, 52, 3)
        or topaneu_release["realized_unique_patient_source_counts"]
        != {
            "chuv": 200,
            "hug": 87,
            "mie_chuo": 54,
            "public": 68,
            "insted": 32,
            "openneuro": 36,
        }
        or topaneu_release["realized_held_out_test_center"] != "umcu"
        or topaneu_release["official_repository"] != "Bangulli/TopAneu-26"
        or topaneu_release["official_repository_head"]
        != "018c243445f99199f484018c4c80575c84c72293"
        or observed_topaneu_release_candidates
        != expected_topaneu_release_candidates
        or any(row["critical_axis_pass"] for row in topaneu_release["candidates"])
        or any(
            abs(sum(row["axis_scores"]) - row["total"]) > 1e-9
            for row in topaneu_release["candidates"]
        )
        or any(
            topaneu_release[key] is not True
            for key in (
                "realized_vessel_masks_described_as_organizer_topbrain_predictions",
                "existing_source_watch_v20_reused_without_duplicate_watch",
            )
        )
        or any(
            topaneu_release[key] is not False
            for key in (
                "zenodo_license_applies_to_medical_release",
                "registered_multi_annotator_merge_performed",
                "realized_casewise_gold_silver_indicator_publicly_exposed",
                "realized_complete_patient_grouped_split_manifest_publicly_exposed",
                "realized_test_case_manifest_publicly_exposed",
                "realized_minimum_location_support_verified_from_public_contract",
                "realized_control_fraction_verified_from_public_contract",
                "official_task1_true_negative_is_standard_patient_class_tn",
                "official_task2_active_path_is_instance_connected_component_evaluation",
                "historical_topaneu_scores_relabelled",
                "surface_vector_reactivated",
                "surface_vector_closed_job_repaired_or_rerun",
                "user_terms_acceptance_verified",
                "challenge_joined",
                "medical_image_mask_json_or_annotation_payload_accessed",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or topaneu_release["execution_server"] != "introai9"
        or topaneu_release["next_allowed_action"]
        != "fresh_problem_level_source_audit_or_material_topaneu_casewise_reference_contract_change_only_no_terms_payload_p0_model_or_compute"
    ):
        raise ProtocolError(
            "TopAneu registered design and realized release must remain separated, "
            "source-only and rejected without terms, payload, P0, model or compute."
        )
    checks.append("TopAneu registered-design and realized-release rejection boundary")

    topaneu_orbit = problem_selection[
        "topaneu_annotation_version_orbit_reappraisal"
    ]
    _require_keys(
        topaneu_orbit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_additive_candidate_id",
            "best_additive_score",
            "most_relevant_candidate_id",
            "most_relevant_candidate_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "official_repository",
            "current_commit",
            "current_root_tree",
            "current_release_tree",
            "batch1_anchor_commit",
            "batch1_root_tree",
            "batch1_release_tree",
            "current_manifest_case_paths",
            "batch1_manifest_case_paths",
            "current_unique_patients_reported",
            "training_centers",
            "held_out_test_center",
            "location_leaf_count",
            "aneurysm_type_count",
            "version_manifest_comparison",
            "dense_mask_change_interpretation",
            "terms_state",
            "user_terms_acceptance_verified",
            "individual_annotation_content_accessed",
            "medical_image_or_mask_payload_accessed",
            "direct_prior_threats",
            "candidates",
            "historical_topaneu_scores_relabelled",
            "surface_vector_history_reopened",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
            "next_allowed_action",
        ],
        "TopAneu annotation-version orbit reappraisal",
    )
    expected_topaneu_scores = [32.0, 31.5, 31.5, 30.5, 28.5, 24.5]
    expected_topaneu_candidates = [
        (
            "topaneu_official_evaluator_patient_instance_unit_correction",
            32.0,
            [4.0, 5.0, 0.5, 5.0, 4.5, 5.0, 4.0, 4.0],
        ),
        (
            "topaneu_revision_conditioned_hierarchical_lesion_set_robustness",
            31.5,
            [4.0, 4.0, 2.0, 4.0, 4.0, 4.5, 5.0, 4.0],
        ),
        (
            "topaneu_type_location_factorized_instance_set_prediction",
            31.5,
            [4.5, 4.5, 1.0, 4.0, 4.5, 5.0, 4.5, 3.5],
        ),
        (
            "topaneu_train_only_silver_vessel_privileged_distillation",
            30.5,
            [4.0, 4.0, 1.0, 4.0, 4.5, 5.0, 4.5, 3.5],
        ),
        (
            "topaneu_center_modality_invariant_learning",
            28.5,
            [4.5, 2.5, 1.0, 4.0, 3.5, 5.0, 4.5, 3.5],
        ),
        (
            "topaneu_longitudinal_growth_consistency",
            24.5,
            [5.0, 1.5, 1.5, 4.0, 0.5, 4.5, 5.0, 2.5],
        ),
    ]
    observed_topaneu_candidates = [
        (candidate.get("id"), candidate.get("total"), candidate.get("axis_scores"))
        for candidate in topaneu_orbit["candidates"]
    ]
    version_comparison = topaneu_orbit["version_manifest_comparison"]
    if (
        topaneu_orbit["status"]
        != "fresh_batch_rejected_additive_best_32_and_revision_orbit_31_5_fail_residual_novelty_floor"
        or topaneu_orbit["audit_document"]
        != "docs/surface-vector-and-topaneu-version-orbit-adjudication-2026-08-11.md"
        or topaneu_orbit["automatic_selection_threshold"] != 32.0
        or topaneu_orbit["best_additive_candidate_id"]
        != "topaneu_official_evaluator_patient_instance_unit_correction"
        or topaneu_orbit["best_additive_score"] != 32.0
        or topaneu_orbit["most_relevant_candidate_id"]
        != "topaneu_revision_conditioned_hierarchical_lesion_set_robustness"
        or topaneu_orbit["most_relevant_candidate_score"] != 31.5
        or topaneu_orbit["best_residual_novelty_score"] != 2.0
        or topaneu_orbit["all_candidate_scores"] != expected_topaneu_scores
        or topaneu_orbit["conditional_source_lead_count"] != 0
        or topaneu_orbit["primary_problem_selected"] is not False
        or topaneu_orbit["official_repository"] != "Bangulli/TopAneu-26"
        or topaneu_orbit["current_commit"]
        != "018c243445f99199f484018c4c80575c84c72293"
        or topaneu_orbit["current_root_tree"]
        != "e7af931d6d9e1e236bac5b96903ab6a2a65daa06"
        or topaneu_orbit["current_release_tree"]
        != "0bab2856144db5f0ba11e4151a59d44517481e95"
        or topaneu_orbit["batch1_anchor_commit"]
        != "15afd4b95e770f69cd3ff1dba9f625c65446a6e5"
        or topaneu_orbit["batch1_root_tree"]
        != "8ca0e92bed6e75713557e2f8e10111ebfd9f489f"
        or topaneu_orbit["batch1_release_tree"]
        != "3bf4db45c1c1100fbcb6fd763bf0fb554f15c831"
        or topaneu_orbit["current_manifest_case_paths"] != 417
        or topaneu_orbit["batch1_manifest_case_paths"] != 98
        or topaneu_orbit["current_unique_patients_reported"] != 409
        or topaneu_orbit["training_centers"] != 4
        or topaneu_orbit["held_out_test_center"] != "center_3_umcu"
        or topaneu_orbit["location_leaf_count"] != 52
        or topaneu_orbit["aneurysm_type_count"] != 3
        or version_comparison
        != {
            "common_paths": 87,
            "old_only_paths": 11,
            "new_only_paths": 330,
            "unchanged_image_checksum_blobs": 73,
            "changed_image_checksum_blobs": 14,
            "unchanged_location_json_blobs": 34,
            "changed_location_json_blobs": 53,
            "changed_location_mask_checksum_blobs": 87,
            "changed_type_mask_checksum_blobs": 87,
            "unchanged_vessel_mask_checksum_blobs": 79,
            "changed_vessel_mask_checksum_blobs": 8,
            "minimum_same_path_unchanged_image_and_changed_location_json": 39,
            "comparison_scope": "git_path_and_blob_metadata_only_no_individual_annotation_content",
        }
        or topaneu_orbit["dense_mask_change_interpretation"]
        != "not_verified_expert_contour_revision_format_taxonomy_or_regeneration_may_be_mixed"
        or topaneu_orbit["terms_state"]
        != "downloading_constitutes_agreement_user_acceptance_not_verified"
        or observed_topaneu_candidates != expected_topaneu_candidates
        or any(
            sum(axis_scores) != score
            for _, score, axis_scores in expected_topaneu_candidates
        )
        or any(candidate["critical_axis_pass"] is not False for candidate in topaneu_orbit["candidates"])
        or topaneu_orbit["historical_topaneu_scores_relabelled"] is not False
        or topaneu_orbit["surface_vector_history_reopened"] is not False
        or any(
            topaneu_orbit[key] is not False
            for key in (
                "user_terms_acceptance_verified",
                "individual_annotation_content_accessed",
                "medical_image_or_mask_payload_accessed",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or topaneu_orbit["execution_server"] != "introai9"
        or topaneu_orbit["next_allowed_action"]
        != "fresh_problem_level_source_and_direct_prior_audit_only_no_terms_payload_topaneu_p0_or_model_from_rejected_version"
    ):
        raise ProtocolError(
            "The TopAneu version orbit must remain source-only and rejected: "
            "the additive 32 score and 31.5 revision formulation both fail the "
            "residual-novelty floor and authorize no terms, payload, P0 or compute."
        )
    checks.append("TopAneu annotation-version source-only rejection boundary")

    cross_scale = problem_selection["aaa_cross_scale_source_reappraisal"]
    _require_keys(
        cross_scale,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "transcriptomic_zenodo_record_id",
            "transcriptomic_zenodo_revision",
            "transcriptomic_license",
            "transcriptomic_archive_bytes",
            "transcriptomic_archive_md5",
            "transcriptomic_upstream_geo_count",
            "regional_wall_stress_geo_id",
            "regional_wall_stress_independent_patients",
            "regional_wall_stress_public_image_mesh_field_coordinate_contract",
            "synthetic_cfd_zenodo_record_id",
            "synthetic_cfd_zenodo_revision",
            "synthetic_cfd_license",
            "synthetic_cfd_archive_bytes",
            "synthetic_cfd_archive_md5",
            "synthetic_cfd_repository",
            "synthetic_cfd_release",
            "synthetic_cfd_release_head",
            "source_cta_measurement_cases",
            "selected_virtual_geometries",
            "reported_cfd_simulations",
            "selected_virtual_geometries_treated_as_observed_patients",
            "public_real_cta_image_cohort_present",
            "public_real_patient_paired_cfd_outer_reference_present",
            "zip_xlsx_example_case_cfd_expression_or_image_payload_accessed",
            "direct_prior_threats",
            "candidates",
            "recurring_source_watch_added",
            "recurring_watch_not_added_reason",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
        ],
        "AAA cross-scale source reappraisal",
    )
    expected_cross_scale_scores = [30.0, 28.5, 26.5, 26.5, 23.0, 22.0]
    expected_cross_scale_ids = [
        "synthetic_aaa_transient_wss_neural_operator",
        "selection_aware_virtual_population_validity_and_uncertainty",
        "synthetic_to_real_aaa_hemodynamic_transport_with_abstention",
        "paired_regional_wall_stress_transcriptomic_program_prediction",
        "mechanobiology_conditioned_surface_operator",
        "local_wss_to_cell_state_spatial_alignment",
    ]
    if (
        cross_scale["status"]
        != "fresh_batch_rejected_best_30_fails_residual_novelty_and_task_linkage_floors"
        or cross_scale["audit_document"]
        != "docs/aaa-cross-scale-source-reappraisal-2026-08-11.md"
        or cross_scale["automatic_selection_threshold"] != 32.0
        or cross_scale["best_candidate_id"]
        != "synthetic_aaa_transient_wss_neural_operator"
        or cross_scale["best_score"] != 30.0
        or cross_scale["best_residual_novelty_score"] != 0.5
        or cross_scale["all_candidate_scores"] != expected_cross_scale_scores
        or cross_scale["conditional_source_lead_count"] != 0
        or cross_scale["primary_problem_selected"] is not False
        or cross_scale["transcriptomic_zenodo_record_id"] != 21868617
        or cross_scale["transcriptomic_zenodo_revision"] != 4
        or cross_scale["transcriptomic_license"] != "cc-by-4.0"
        or cross_scale["transcriptomic_archive_bytes"] != 293641
        or cross_scale["transcriptomic_archive_md5"]
        != "264d9ada285aa65a09239266147a1ad5"
        or cross_scale["transcriptomic_upstream_geo_count"] != 6
        or cross_scale["regional_wall_stress_geo_id"] != "GSE205071"
        or cross_scale["regional_wall_stress_independent_patients"] != 12
        or cross_scale[
            "regional_wall_stress_public_image_mesh_field_coordinate_contract"
        ]
        is not False
        or cross_scale["synthetic_cfd_zenodo_record_id"] != 21435232
        or cross_scale["synthetic_cfd_zenodo_revision"] != 4
        or cross_scale["synthetic_cfd_license"] != "mit"
        or cross_scale["synthetic_cfd_archive_bytes"] != 37064038
        or cross_scale["synthetic_cfd_archive_md5"]
        != "93cec210d801786fe3728dbffe990067"
        or cross_scale["synthetic_cfd_repository"]
        != "Harish-Research-Lab/Synthetic-AAA-CFD-framework"
        or cross_scale["synthetic_cfd_release"] != "v1.0.0"
        or cross_scale["synthetic_cfd_release_head"]
        != "98363a0104701dcc4bea11c2ee808eed1febafbe"
        or cross_scale["source_cta_measurement_cases"] != 258
        or cross_scale["selected_virtual_geometries"] != 182
        or cross_scale["reported_cfd_simulations"] != 364
        or cross_scale["selected_virtual_geometries_treated_as_observed_patients"]
        is not False
        or cross_scale["public_real_cta_image_cohort_present"] is not False
        or cross_scale["public_real_patient_paired_cfd_outer_reference_present"]
        is not False
        or cross_scale[
            "zip_xlsx_example_case_cfd_expression_or_image_payload_accessed"
        ]
        is not False
        or [item["id"] for item in cross_scale["candidates"]]
        != expected_cross_scale_ids
        or [item["total"] for item in cross_scale["candidates"]]
        != expected_cross_scale_scores
        or any(
            sum(item["axis_scores"]) != item["total"]
            or item["critical_axis_pass"] is not False
            for item in cross_scale["candidates"]
        )
        or cross_scale["recurring_source_watch_added"] is not False
        or cross_scale["recurring_watch_not_added_reason"]
        != "public_version_change_alone_cannot_supply_missing_patient_linkage_or_real_paired_outer_reference"
        or any(
            cross_scale[key] is not False
            for key in (
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or cross_scale["execution_server"] != "introai9"
    ):
        raise ProtocolError(
            "The AAA cross-scale source reappraisal must preserve exact public "
            "metadata, independent-unit and no-payload facts, all six rejected "
            "scores, no recurring-watch inflation and no P0/model/compute authority."
        )
    checks.append("AAA cross-scale source reappraisal boundary")

    mris = problem_selection["mris_bench_target_contract_audit"]
    _require_keys(
        mris,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "canonical_dataset_id",
            "legacy_alias_id",
            "huggingface_revision",
            "huggingface_last_modified",
            "public_rows_reported",
            "sibling_count",
            "arrow_shard_count",
            "arrow_shard_bytes",
            "used_storage_bytes",
            "machine_schema_fields",
            "machine_schema_mask_field_present",
            "state_split",
            "source_dataset_lineage_public",
            "patient_grouping_public",
            "annotation_protocol_public",
            "upstream_medical_image_license_public",
            "under_review_release_statement_present",
            "visible_viewer_examples_are_registered_quality_prevalence",
            "row_count_treated_as_independent_patient_count",
            "arrow_or_image_payload_accessed",
            "direct_prior_threats",
            "candidates",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
        ],
        "MRIS-Bench target-contract audit",
    )
    expected_mris_candidate_ids = [
        "modality_semantic_contradiction_detection_with_selective_abstention",
        "evidence_grounded_aneurysm_referring_segmentation",
        "dataset_contract_and_provenance_benchmark",
        "patient_grouped_cross_slice_statement_consistency",
        "label_noise_robust_mris_training",
        "two_dimensional_descriptions_to_three_dimensional_lesion_consistency",
    ]
    if (
        mris["status"]
        != "fresh_batch_rejected_best_24_fails_identifiability_novelty_asset_and_independent_unit_floors"
        or mris["audit_document"]
        != "docs/mris-bench-target-contract-audit-2026-08-11.md"
        or mris["automatic_selection_threshold"] != 32.0
        or mris["best_candidate_id"] != expected_mris_candidate_ids[0]
        or mris["best_score"] != 24.0
        or mris["best_residual_novelty_score"] != 1.5
        or mris["all_candidate_scores"]
        != [24.0, 23.5, 23.0, 22.5, 22.0, 21.0]
        or mris["conditional_source_lead_count"] != 0
        or mris["primary_problem_selected"] is not False
        or mris["canonical_dataset_id"] != "lixiangcog/MRIS-Bench"
        or mris["legacy_alias_id"] != "lixiang007666/MRIS-Bench"
        or mris["huggingface_revision"]
        != "6f2d6d9ad10eba68700ce95c7523ec78934f7a3d"
        or mris["huggingface_last_modified"] != "2026-05-15T03:22:31.000Z"
        or mris["public_rows_reported"] != 30110
        or mris["sibling_count"] != 12
        or mris["arrow_shard_count"] != 8
        or mris["arrow_shard_bytes"] != 3728270168
        or mris["used_storage_bytes"] != 7449574455
        or mris["machine_schema_fields"]
        != ["id", "problem", "solution", "image", "height", "width"]
        or mris["machine_schema_mask_field_present"] is not False
        or mris["state_split"] is not None
        or any(
            mris[key] is not False
            for key in (
                "source_dataset_lineage_public",
                "patient_grouping_public",
                "annotation_protocol_public",
                "upstream_medical_image_license_public",
                "visible_viewer_examples_are_registered_quality_prevalence",
                "row_count_treated_as_independent_patient_count",
                "arrow_or_image_payload_accessed",
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or mris["under_review_release_statement_present"] is not True
        or mris["execution_server"] != "introai9"
        or [item.get("id") for item in mris["candidates"]]
        != expected_mris_candidate_ids
        or [item.get("total") for item in mris["candidates"]]
        != mris["all_candidate_scores"]
        or any(
            sum(item.get("axis_scores", [])) != item.get("total")
            or item.get("critical_axis_pass") is not False
            for item in mris["candidates"]
        )
    ):
        raise ProtocolError(
            "MRIS-Bench must remain a metadata-only rejected target contract: rows "
            "are not patient units, box/point strings are not masks, visible examples "
            "are not a measured error rate, and no method or compute is authorized."
        )
    checks.append("MRIS-Bench target-contract rejection boundary")

    open_model = problem_selection["open_model_transport_source_reappraisal"]
    _require_keys(
        open_model,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "best_residual_novelty_score",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "maximus_zenodo_record_id",
            "maximus_zenodo_revision",
            "maximus_license",
            "maximus_file_name",
            "maximus_file_bytes",
            "maximus_file_md5",
            "rsna_first_place_repository",
            "rsna_first_place_head",
            "rsna_first_place_release_count",
            "rsna_first_place_license_spdx_id",
            "tar_repository",
            "tar_repository_head",
            "tar_release_count",
            "tar_license_spdx_id",
            "iavs_repository_head",
            "topaneu_repository_head",
            "openneuro_ds005096_head",
            "openneuro_patients",
            "openneuro_aneurysms",
            "openneuro_longitudinal_subjects",
            "openneuro_same_session_multi_acquisition_patients",
            "patient_or_model_payload_accessed",
            "direct_prior_threats",
            "candidates",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
        ],
        "open-model transport source reappraisal",
    )
    expected_open_model_scores = [32.0, 31.5, 29.0, 28.5, 27.5, 27.0]
    expected_open_model_ids = {
        "fixed_open_model_external_tof_mra_transport_and_morphometry",
        "patient_level_selective_morphometry_under_domain_shift",
        "dual_public_model_disagreement_triage",
        "topology_conditioned_parent_vessel_failure_audit",
        "public_model_pseudolabel_self_training",
        "longitudinal_prediction_consistency",
    }
    expected_open_model_priors = {
        "multicentre_tof_mra_detection_segmentation_and_morphometry",
        "rsna_multimodal_tri_axial_roi_and_multitask_3d_nnunet",
        "topology_aware_semi_supervised_aneurysm_vessel_segmentation",
        "selective_and_conformal_segmentation_under_domain_shift",
        "external_segmentation_and_morphometry_validation",
    }
    open_model_candidates = open_model["candidates"]
    if (
        open_model["status"]
        != "fresh_batch_rejected_best_additive_score_meets_32_but_residual_novelty_floor_fails"
        or open_model["audit_document"]
        != "docs/open-model-transport-and-admission-reappraisal-2026-08-11.md"
        or open_model["automatic_selection_threshold"] != 32.0
        or open_model["best_candidate_id"]
        != "fixed_open_model_external_tof_mra_transport_and_morphometry"
        or open_model["best_score"] != 32.0
        or open_model["best_residual_novelty_score"] != 0.5
        or open_model["all_candidate_scores"] != expected_open_model_scores
        or open_model["conditional_source_lead_count"] != 0
        or open_model["primary_problem_selected"] is not False
        or open_model["maximus_zenodo_record_id"] != 13386859
        or open_model["maximus_zenodo_revision"] != 10
        or open_model["maximus_license"] != "cc-by-nc-4.0"
        or open_model["maximus_file_name"] != "Dataset610_AP+DD+ADAM.zip"
        or open_model["maximus_file_bytes"] != 1143245289
        or open_model["maximus_file_md5"] != "dc7478e2595739306ec7ef85d05699be"
        or open_model["rsna_first_place_repository"]
        != "uchiyama33/rsna2025_1st_place"
        or open_model["rsna_first_place_head"]
        != "e1dcdf0058e1e0d0044d8053e92243b4b4794555"
        or open_model["rsna_first_place_release_count"] != 0
        or open_model["rsna_first_place_license_spdx_id"] is not None
        or open_model["tar_repository"] != "AbsoluteResonance/TAR"
        or open_model["tar_repository_head"]
        != "5e852dd919feb98406067a8034dd744ddb78877f"
        or open_model["tar_release_count"] != 0
        or open_model["tar_license_spdx_id"] is not None
        or open_model["iavs_repository_head"]
        != "2e40088d9eaa671c592929a154b7b2cf99f9320a"
        or open_model["topaneu_repository_head"]
        != "018c243445f99199f484018c4c80575c84c72293"
        or open_model["openneuro_ds005096_head"]
        != "0760bf865612600c4eee85f6f437aefaeb534204"
        or open_model["openneuro_patients"] != 63
        or open_model["openneuro_aneurysms"] != 85
        or open_model["openneuro_longitudinal_subjects"] != 24
        or open_model["openneuro_same_session_multi_acquisition_patients"] != 4
        or open_model["patient_or_model_payload_accessed"] is not False
        or set(open_model["direct_prior_threats"]) != expected_open_model_priors
        or len(open_model_candidates) != 6
        or _unique_ids(open_model_candidates, "id", "open-model candidates")
        != expected_open_model_ids
        or [candidate["total"] for candidate in open_model_candidates]
        != expected_open_model_scores
        or any(
            sum(candidate["axis_scores"]) != candidate["total"]
            for candidate in open_model_candidates
        )
        or any(candidate["critical_axis_pass"] is not False for candidate in open_model_candidates)
        or open_model_candidates[0]["axis_scores"][2]
        >= admission_v2["critical_axis_minima"]["residual_novelty"]
        or any(
            open_model[key] is not False
            for key in [
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            ]
        )
        or open_model["execution_server"] != "introai9"
    ):
        raise ProtocolError(
            "The open-model transport batch must preserve the exact public-model "
            "metadata, frozen candidate scores, novelty-floor rejection, no payload, "
            "no active lead and no-compute state."
        )
    checks.append("open-model transport rejection and no-compute boundary")

    cross_vascular = problem_selection[
        "cross_vascular_transient_wss_source_correction"
    ]
    _require_keys(
        cross_vascular,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "axis_scores",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "aaa_wss_arxiv_id",
            "aaa_wss_training_patients",
            "aaa_wss_external_patients",
            "aaa_wss_external_scans",
            "aaa_wss_total_cfd_simulations",
            "aaa_wss_extracted_cycle_phases",
            "aaa_wss_reports_transient_vector_wss",
            "aaa_wss_reports_tawss_and_osi",
            "aaa_wss_reports_bc_remodelling_topology_and_mesh_generalization",
            "aaa_wss_reports_high_frequency_directional_oversmoothing",
            "aaa_wss_evaluates_signed_degree_critical_points_or_worldlines",
            "aaa_wss_repository",
            "aaa_wss_repository_head",
            "aaa_wss_repository_commit_count",
            "aaa_wss_repository_readme_bytes",
            "aaa_wss_repository_release_count",
            "aaa_wss_repository_size_kib",
            "aaa_wss_repository_license_spdx_id",
            "aaa_wss_repository_contains_implementation_checkpoint_or_cfd_fields",
            "aaa100_zenodo_record_id",
            "aaa100_zenodo_revision",
            "aaa100_license",
            "aaa100_patient_geometries",
            "aaa100_public_file_count",
            "aaa100_transient_cfd_fields_public",
            "aaa100_payload_accessed",
            "sano_dataverse_doi",
            "sano_dataset_version",
            "sano_license",
            "sano_public_file_count",
            "sano_independent_patient_cases",
            "sano_flow_is_steady_state",
            "sano_original_study_owns_geometry_fidelity_to_low_wss_relation",
            "sano_payload_accessed",
            "surface_vector_question_retained_as_inactive_hypothesis",
            "architecture_selected_from_direct_prior",
            "direct_prior_threats",
            "candidates",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
        ],
        "cross-vascular transient-WSS source correction",
    )
    expected_cross_scores = [30.0, 29.0, 28.5, 25.5, 23.0, 21.5]
    expected_cross_ids = {
        "sano_anatomical_fidelity_low_wss_reproduction",
        "sano_steady_wss_structural_stability_audit",
        "new_cfd_generation_on_open_aaa100_geometry",
        "aaa_transient_wss_structure_failure_audit",
        "aaa_longitudinal_structure_consistency",
        "cross_vascular_structure_transfer",
    }
    expected_cross_priors = {
        "lab_gatr_e3_equivariant_transient_aaa_wss_surrogate",
        "boundary_condition_remodelling_topology_and_mesh_generalization",
        "transient_wss_tawss_and_osi_external_evaluation",
        "sano_geometry_fidelity_to_low_wss_analysis",
        "hodge_dec_and_equivariant_surface_operator_components",
        "robust_critical_point_and_vector_field_trajectory_tracking",
    }
    cross_candidates = cross_vascular["candidates"]
    if (
        cross_vascular["status"]
        != "fresh_source_batch_rejected_below_admission_strong_direct_prior_but_no_executable_matched_baseline_or_transient_field_asset"
        or cross_vascular["audit_document"]
        != "docs/cross-vascular-transient-wss-source-correction-2026-08-11.md"
        or cross_vascular["automatic_selection_threshold"] != 32.0
        or cross_vascular["best_candidate_id"]
        != "sano_anatomical_fidelity_low_wss_reproduction"
        or cross_vascular["best_score"] != 30.0
        or cross_vascular["axis_scores"]
        != [4.0, 5.0, 0.5, 5.0, 1.0, 5.0, 5.0, 4.5]
        or sum(cross_vascular["axis_scores"]) != cross_vascular["best_score"]
        or cross_vascular["all_candidate_scores"] != expected_cross_scores
        or max(cross_vascular["all_candidate_scores"])
        >= cross_vascular["automatic_selection_threshold"]
        or cross_vascular["conditional_source_lead_count"] != 0
        or cross_vascular["primary_problem_selected"] is not False
        or cross_vascular["aaa_wss_arxiv_id"] != "2507.22817"
        or cross_vascular["aaa_wss_training_patients"] != 100
        or cross_vascular["aaa_wss_external_patients"] != 29
        or cross_vascular["aaa_wss_external_scans"] != 118
        or cross_vascular["aaa_wss_total_cfd_simulations"] != 1090
        or cross_vascular["aaa_wss_extracted_cycle_phases"] != 21
        or cross_vascular["aaa_wss_reports_transient_vector_wss"] is not True
        or cross_vascular["aaa_wss_reports_tawss_and_osi"] is not True
        or cross_vascular[
            "aaa_wss_reports_bc_remodelling_topology_and_mesh_generalization"
        ]
        is not True
        or cross_vascular[
            "aaa_wss_reports_high_frequency_directional_oversmoothing"
        ]
        is not True
        or cross_vascular[
            "aaa_wss_evaluates_signed_degree_critical_points_or_worldlines"
        ]
        is not False
        or cross_vascular["aaa_wss_repository"]
        != "PatRyg99/AAA-WSS-neural-surrogate"
        or cross_vascular["aaa_wss_repository_head"]
        != "2f78bf1879e5e555c3369d91822be3f567f9fbd1"
        or cross_vascular["aaa_wss_repository_commit_count"] != 1
        or cross_vascular["aaa_wss_repository_readme_bytes"] != 183
        or cross_vascular["aaa_wss_repository_release_count"] != 0
        or cross_vascular["aaa_wss_repository_size_kib"] != 0
        or cross_vascular["aaa_wss_repository_license_spdx_id"] is not None
        or cross_vascular[
            "aaa_wss_repository_contains_implementation_checkpoint_or_cfd_fields"
        ]
        is not False
        or cross_vascular["aaa100_zenodo_record_id"] != 10932957
        or cross_vascular["aaa100_zenodo_revision"] != 10
        or cross_vascular["aaa100_license"] != "cc-by-nc-4.0"
        or cross_vascular["aaa100_patient_geometries"] != 100
        or cross_vascular["aaa100_public_file_count"] != 3
        or cross_vascular["aaa100_transient_cfd_fields_public"] is not False
        or cross_vascular["aaa100_payload_accessed"] is not False
        or cross_vascular["sano_dataverse_doi"] != "10.71580/SANO/GVPFQ5"
        or cross_vascular["sano_dataset_version"] != "1.0"
        or cross_vascular["sano_license"] != "CC0-1.0"
        or cross_vascular["sano_public_file_count"] != 141
        or cross_vascular["sano_independent_patient_cases"] != 12
        or cross_vascular["sano_flow_is_steady_state"] is not True
        or cross_vascular[
            "sano_original_study_owns_geometry_fidelity_to_low_wss_relation"
        ]
        is not True
        or cross_vascular["sano_payload_accessed"] is not False
        or cross_vascular[
            "surface_vector_question_retained_as_inactive_hypothesis"
        ]
        is not True
        or cross_vascular["architecture_selected_from_direct_prior"] is not False
        or set(cross_vascular["direct_prior_threats"])
        != expected_cross_priors
        or len(cross_candidates) != 6
        or _unique_ids(cross_candidates, "id", "cross-vascular candidates")
        != expected_cross_ids
        or [candidate["total"] for candidate in cross_candidates]
        != expected_cross_scores
        or any(
            sum(candidate["axis_scores"]) != candidate["total"]
            for candidate in cross_candidates
        )
        or any(
            cross_vascular[key] is not False
            for key in [
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            ]
        )
        or cross_vascular["execution_server"] != "introai9"
    ):
        raise ProtocolError(
            "The cross-vascular transient-WSS correction must preserve the "
            "patient/unit, public-code, geometry-only and steady-flow boundaries, "
            "frozen sub-32 scores, inactive surface question and no-compute state."
        )
    checks.append("cross-vascular transient-WSS correction and no-compute boundary")
    posttreatment = problem_selection[
        "posttreatment_reference_linked_imaging_source_delta"
    ]
    _require_keys(
        posttreatment,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "axis_scores",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "petra_prospective_doi",
            "petra_prospective_patients",
            "petra_prospective_aneurysms",
            "petra_timepoints",
            "petra_stent_assisted_coiling_units",
            "petra_flow_diverter_units",
            "petra_dsa_reference_at_both_timepoints",
            "petra_raw_data_publicly_versioned",
            "petra_raw_images_accessed",
            "petra_article_already_proposes_noninvasive_dsa_alternative",
            "helsinki_technique_dwi_occlusion_doi",
            "helsinki_treated_patients_with_dwi",
            "helsinki_patients_with_six_month_angiographic_followup",
            "helsinki_parent_quality_cohort_doi",
            "helsinki_parent_quality_cohort_patients",
            "helsinki_researcher_initiated_data_sharing_possible",
            "helsinki_findata_official_decision_required",
            "helsinki_image_or_patient_table_accessed",
            "clipped_table_doi",
            "clipped_table_patients",
            "clipped_table_aneurysms",
            "clipped_table_branches",
            "clipped_table_public_xlsx_display_size",
            "clipped_table_public_pdf_display_size",
            "clipped_table_contains_raw_cta_tof_or_petra_images",
            "clipped_table_payload_accessed",
            "direct_prior_threats",
            "candidates",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
        ],
        "post-treatment reference-linked imaging source delta",
    )
    expected_posttreatment_priors = {
        "prospective_petra_tof_dsa_comparison_and_noninvasive_followup_proposal",
        "prior_petra_ute_and_silent_mra_posttreatment_followup",
        "prospective_silent_mra_endovascular_followup",
        "selectivenet_integrated_reject_option",
        "learning_to_defer_to_an_expert",
        "conformal_risk_control_for_bounded_selective_error",
        "prospective_technique_specific_dwi_and_occlusion_tradeoff",
    }
    expected_posttreatment_scores = [28.5, 27.5, 26.5, 26.5, 26.0, 24.5]
    expected_posttreatment_ids = {
        "petra_first_selective_dsa_referral_with_patient_level_missed_residual_budget",
        "device_conditioned_residual_filling_estimation",
        "longitudinal_occlusion_change_concordance",
        "dwi_lesion_size_outcome_stratification",
        "postclip_branch_visibility_reliability",
        "treatment_technique_benefit_harm_decision_model",
    }
    candidates = posttreatment["candidates"]
    if (
        posttreatment["status"]
        != "fresh_source_batch_rejected_below_admission_no_public_image_level_development_asset"
        or posttreatment["audit_document"]
        != "docs/posttreatment-reference-linked-imaging-source-delta-2026-08-11.md"
        or posttreatment["automatic_selection_threshold"] != 32.0
        or posttreatment["best_candidate_id"]
        != "petra_first_selective_dsa_referral_with_patient_level_missed_residual_budget"
        or posttreatment["best_score"] != 28.5
        or posttreatment["axis_scores"] != [5.0, 4.5, 1.5, 1.0, 4.5, 5.0, 5.0, 2.0]
        or sum(posttreatment["axis_scores"]) != posttreatment["best_score"]
        or posttreatment["all_candidate_scores"] != expected_posttreatment_scores
        or max(posttreatment["all_candidate_scores"])
        >= posttreatment["automatic_selection_threshold"]
        or posttreatment["conditional_source_lead_count"] != 0
        or posttreatment["primary_problem_selected"] is not False
        or posttreatment["petra_prospective_doi"] != "10.3389/fneur.2026.1786151"
        or posttreatment["petra_prospective_patients"] != 100
        or posttreatment["petra_prospective_aneurysms"] != 100
        or posttreatment["petra_timepoints"]
        != ["postoperative_day_1", "six_months"]
        or posttreatment["petra_stent_assisted_coiling_units"] != 72
        or posttreatment["petra_flow_diverter_units"] != 28
        or posttreatment["petra_dsa_reference_at_both_timepoints"] is not True
        or posttreatment["petra_raw_data_publicly_versioned"] is not False
        or posttreatment["petra_raw_images_accessed"] is not False
        or posttreatment["petra_article_already_proposes_noninvasive_dsa_alternative"]
        is not True
        or posttreatment["helsinki_technique_dwi_occlusion_doi"]
        != "10.1007/s00701-026-06934-z"
        or posttreatment["helsinki_treated_patients_with_dwi"] != 119
        or posttreatment["helsinki_patients_with_six_month_angiographic_followup"]
        != 113
        or posttreatment["helsinki_parent_quality_cohort_doi"]
        != "10.3171/2025.7.JNS25775"
        or posttreatment["helsinki_parent_quality_cohort_patients"] != 169
        or posttreatment["helsinki_researcher_initiated_data_sharing_possible"]
        is not False
        or posttreatment["helsinki_findata_official_decision_required"] is not True
        or posttreatment["helsinki_image_or_patient_table_accessed"] is not False
        or posttreatment["clipped_table_doi"] != "10.1016/j.dib.2021.106874"
        or posttreatment["clipped_table_patients"] != 58
        or posttreatment["clipped_table_aneurysms"] != 72
        or posttreatment["clipped_table_branches"] != 141
        or posttreatment["clipped_table_public_xlsx_display_size"] != "18.5_KB"
        or posttreatment["clipped_table_public_pdf_display_size"] != "37.3_KB"
        or posttreatment["clipped_table_contains_raw_cta_tof_or_petra_images"]
        is not False
        or posttreatment["clipped_table_payload_accessed"] is not False
        or set(posttreatment["direct_prior_threats"])
        != expected_posttreatment_priors
        or len(candidates) != 6
        or _unique_ids(candidates, "id", "post-treatment candidates")
        != expected_posttreatment_ids
        or [candidate["total"] for candidate in candidates]
        != expected_posttreatment_scores
        or any(sum(candidate["axis_scores"]) != candidate["total"] for candidate in candidates)
        or any(
            posttreatment[key] is not False
            for key in [
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            ]
        )
        or posttreatment["execution_server"] != "introai9"
    ):
        raise ProtocolError(
            "The post-treatment reference-linked imaging source delta must preserve "
            "the prospective PETRA/DSA and Helsinki unit boundaries, tabular-only "
            "clipped source, direct-prior threats, frozen sub-32 scores and no-compute state."
        )
    checks.append("post-treatment reference-linked imaging rejection and no-compute boundary")

    bc_transport = problem_selection["aneumo_bc_transport_source_audit"]
    _require_keys(
        bc_transport,
        [
            "status",
            "audit_document",
            "config",
            "candidate_id",
            "score",
            "axis_scores",
            "automatic_selection_threshold",
            "conditional_source_lead_count",
            "active_method_count",
            "primary_problem_selected",
            "hf_repo_commit",
            "upstream_code_commit",
            "historical_v1e_failed_preserved",
            "direct_prior_threats",
            "p0_protocol_id",
            "p0_registered",
            "p0_train_base_families",
            "p0_cases",
            "p0_conditions",
            "p0_required_members",
            "p0_persistent_field_cache",
            "p0_pressure_validation_test_model_checkpoint_gpu_or_outer_test_access",
            "p0_submission_limit",
            "p0_job_submitted",
            "p0_job_id",
            "p0_public_source_commit",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_execution_status",
            "p0_exit_status",
            "p0_resources_used_walltime",
            "p0_resources_used_cput",
            "p0_resources_used_memory_kb",
            "p0_private_status_bytes",
            "p0_private_status_sha256",
            "p0_aggregate_result_materialized",
            "p0_raw_pbs_output_materialized",
            "p0_scientific_gate_evaluated",
            "p1_registration_authorized",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_pbs_jobs_observed_before_registration",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "p0_pass_authorizes",
            "p0_failure_action",
        ],
        "Aneumo BC-transport source audit",
    )
    if (
        bc_transport["status"]
        != "p0_execution_incomplete_no_scientific_verdict_closed_without_repair_or_rerun"
        or bc_transport["candidate_id"]
        != "similarity_quotiented_anchor_conditioned_bc_transport"
        or bc_transport["score"] != 33.5
        or sum(bc_transport["axis_scores"]) != 33.5
        or bc_transport["automatic_selection_threshold"] != 32.0
        or bc_transport["conditional_source_lead_count"] != 0
        or bc_transport["active_method_count"] != 0
        or bc_transport["primary_problem_selected"] is not False
        or bc_transport["historical_v1e_failed_preserved"] is not True
        or bc_transport["p0_protocol_id"]
        != "aneumo_anchor_conditioned_bc_transport_p0_v1"
        or bc_transport["p0_registered"] is not True
        or bc_transport["p0_train_base_families"] != [1]
        or bc_transport["p0_cases"] != [1, 2]
        or bc_transport["p0_conditions"] != 8
        or bc_transport["p0_required_members"] != 16
        or bc_transport["p0_persistent_field_cache"] is not False
        or bc_transport[
            "p0_pressure_validation_test_model_checkpoint_gpu_or_outer_test_access"
        ]
        is not False
        or bc_transport["p0_submission_limit"] != 1
        or bc_transport["p0_job_submitted"] is not True
        or bc_transport["p0_job_id"] != "115518.ECE-util1"
        or bc_transport["p0_public_source_commit"]
        != "38e7894fc5ae56ffb3efbe469c4e1f7480f81feb"
        or bc_transport["p0_execution_record"]
        != "results/aneumo_bc_transport_p0_execution_20260810.json"
        or bc_transport["p0_execution_record_sha256"]
        != "3f8c6aa5621584176da0f3245e843309dd06ba024c5275f5c0a13b82b884c28b"
        or bc_transport["p0_execution_status"]
        != "execution_incomplete_no_scientific_verdict"
        or bc_transport["p0_exit_status"] != 1
        or bc_transport["p0_resources_used_walltime"] != "00:08:21"
        or bc_transport["p0_resources_used_cput"] != "00:00:00"
        or bc_transport["p0_resources_used_memory_kb"] != 39160
        or bc_transport["p0_private_status_bytes"] != 275
        or bc_transport["p0_private_status_sha256"]
        != "5f0c26118e86cc68ed6c494c782e301537b11589565e77996a672c442c266207"
        or bc_transport["p0_aggregate_result_materialized"] is not False
        or bc_transport["p0_raw_pbs_output_materialized"] is not False
        or bc_transport["p0_scientific_gate_evaluated"] is not False
        or bc_transport["p1_registration_authorized"] is not False
        or any(
            bc_transport[key] is not False
            for key in (
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or bc_transport["execution_server"] != "introai9"
        or bc_transport["introai9_connection_verified"] is not True
        or bc_transport["introai9_pbs_jobs_observed_before_registration"] != 0
        or bc_transport["p0_pass_authorizes"]
        != "register_separate_train_only_method_free_p1_task_adequacy_audit_only"
        or bc_transport["p0_failure_action"]
        != "close_exact_p0_without_same_contract_repair_or_rerun"
    ):
        raise ProtocolError(
            "Aneumo BC-transport P0 must remain train-only, method-free, CPU-only, "
            "one-shot on introai9 with junjinyong excluded."
        )
    checks.append("Aneumo BC-transport conditional source/P0 boundary")
    containment = problem_selection["openneuro_containment_morphometry_source_audit"]
    _require_keys(
        containment,
        [
            "status",
            "audit_document",
            "config",
            "candidate_id",
            "score",
            "axis_scores",
            "automatic_selection_threshold",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "historical_one_sided_outer_annotation_candidate_score",
            "historical_candidate_rejected_preserved",
            "new_version_estimates_real_coarsening_mechanism",
            "new_version_observed_statement",
            "same_subject_real_weak_and_independent_precise_pairs_available",
            "dataset_commit",
            "dataset_license",
            "dataset_tree_paths",
            "dataset_public_subjects",
            "dataset_manual_mask_subject_sessions",
            "dataset_manual_mask_nifti_paths",
            "code_commit",
            "code_license",
            "code_precise_entries",
            "code_precise_subjects",
            "code_weak_entries",
            "code_weak_subjects",
            "public_precise_subjects",
            "public_weak_subjects",
            "code_only_weak_subjects",
            "code_session_pairs_matching_public_tree",
            "subject_id_is_registered_join_key",
            "session_date_is_registered_join_key",
            "direct_prior_threats",
            "candidates",
            "patient_nifti_image_or_mask_payload_accessed",
            "participants_or_clinical_table_accessed",
            "pretrained_model_or_checkpoint_accessed",
            "p0_protocol_id",
            "p0_registered",
            "p0_submission_limit",
            "p0_job_submitted",
            "p0_job_id",
            "p0_public_source_commit",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_execution_status",
            "p0_final_job_state",
            "p0_exit_status",
            "p0_resources_used_walltime",
            "p0_resources_used_cput",
            "p0_resources_used_memory_kb",
            "p0_private_status_bytes",
            "p0_private_status_sha256",
            "p0_aggregate_result_materialized",
            "p0_raw_pbs_output_materialized",
            "p0_registered_small_source_objects_retained",
            "p0_registered_high_level_checks_evaluated",
            "p0_registered_high_level_checks_total",
            "p0_failure_stage",
            "p0_low_level_cause",
            "p0_scientific_gate_evaluated",
            "p1_registration_authorized",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_last_verified_pbs_jobs_observed",
            "introai9_running_or_queued_aurora_jobs_after_final",
            "pbs_ncpus",
            "pbs_memory_gb",
            "pbs_ngpus",
            "pbs_walltime",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "p0_pass_authorizes",
            "p0_failure_action",
        ],
        "OpenNeuro containment-morphometry source audit",
    )
    expected_containment_scores = {
        "containment_identified_morphometry_envelopes": 32.5,
        "openneuro_longitudinal_surface_growth_detection_direct_prior_and_unit_limited": 31.5,
        "acquisition_quality_indexed_external_lesion_set_risk": 31.0,
        "cross_center_weak_to_strong_segmentation": 30.5,
        "royal_reference_morphometry_certificate_direct_prior_occupied": 30.0,
        "conformal_lesion_fnr_control": 30.0,
    }
    observed_containment_scores = {
        candidate["id"]: candidate["score"] for candidate in containment["candidates"]
    }
    if (
        containment["status"]
        != "p0_execution_incomplete_no_scientific_verdict_closed_without_repair_or_rerun"
        or containment["audit_document"]
        != "docs/openneuro-containment-morphometry-source-audit-2026-08-10.md"
        or containment["config"]
        != "configs/openneuro_containment_morphometry_p0.json"
        or containment["candidate_id"]
        != "containment_identified_morphometry_envelopes"
        or containment["score"] != 32.5
        or sum(containment["axis_scores"]) != 32.5
        or containment["automatic_selection_threshold"] != 32.0
        or containment["conditional_source_lead_count"] != 0
        or containment["primary_problem_selected"] is not False
        or containment["historical_one_sided_outer_annotation_candidate_score"]
        != 31.5
        or containment["historical_candidate_rejected_preserved"] is not True
        or containment["new_version_estimates_real_coarsening_mechanism"] is not False
        or containment["new_version_observed_statement"]
        != "true_lesion_mask_is_subset_of_observed_outer_sphere"
        or containment["same_subject_real_weak_and_independent_precise_pairs_available"]
        is not False
        or containment["dataset_commit"]
        != "896b8846d899acee68c0246cc987ca96e77267d4"
        or containment["dataset_license"] != "CC0"
        or containment["dataset_tree_paths"] != 5737
        or containment["dataset_public_subjects"] != 284
        or containment["dataset_manual_mask_subject_sessions"] != 296
        or containment["dataset_manual_mask_nifti_paths"] != 494
        or containment["code_commit"]
        != "5ecdf6e5b9a811e4ec7472c210dada42e60cc3dc"
        or containment["code_license"] != "Apache-2.0"
        or containment["code_precise_entries"] != 38
        or containment["code_precise_subjects"] != 38
        or containment["code_weak_entries"] != 262
        or containment["code_weak_subjects"] != 250
        or containment["public_precise_subjects"] != 38
        or containment["public_weak_subjects"] != 246
        or containment["code_only_weak_subjects"]
        != ["sub-115", "sub-143", "sub-181", "sub-272"]
        or containment["code_session_pairs_matching_public_tree"] != 11
        or containment["subject_id_is_registered_join_key"] is not True
        or containment["session_date_is_registered_join_key"] is not False
        or observed_containment_scores != expected_containment_scores
        or any(
            sum(candidate["axis_scores"]) != candidate["score"]
            for candidate in containment["candidates"]
        )
        or any(
            containment[key] is not False
            for key in (
                "patient_nifti_image_or_mask_payload_accessed",
                "participants_or_clinical_table_accessed",
                "pretrained_model_or_checkpoint_accessed",
                "p0_scientific_gate_evaluated",
                "p1_registration_authorized",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or containment["p0_protocol_id"]
        != "openneuro_containment_morphometry_metadata_p0_v1"
        or containment["p0_registered"] is not True
        or containment["p0_submission_limit"] != 1
        or containment["p0_job_submitted"] is not True
        or containment["p0_job_id"] != "115622.ECE-util1"
        or containment["p0_public_source_commit"]
        != "bb227edc86bf3b68e92b97f120a7918b0753c831"
        or containment["p0_execution_record"]
        != "results/openneuro_containment_morphometry_p0_execution_20260810.json"
        or containment["p0_execution_record_sha256"]
        != "4e59f8225ef423d5adf3d9e625b26dc5e15e255b3d2501b7989e005b8432ff9e"
        or containment["p0_execution_status"]
        != "execution_incomplete_no_scientific_verdict"
        or containment["p0_final_job_state"] != "F"
        or containment["p0_exit_status"] != 1
        or containment["p0_resources_used_walltime"] != "00:02:24"
        or containment["p0_resources_used_cput"] != "00:00:00"
        or containment["p0_resources_used_memory_kb"] != 15328
        or containment["p0_private_status_bytes"] != 310
        or containment["p0_private_status_sha256"]
        != "d5022b2c3ac689e1d36083175c04be87ba71a09f3d4ec2275b8729e089c66444"
        or containment["p0_aggregate_result_materialized"] is not False
        or containment["p0_raw_pbs_output_materialized"] is not False
        or containment["p0_registered_small_source_objects_retained"] != 0
        or containment["p0_registered_high_level_checks_evaluated"] != 0
        or containment["p0_registered_high_level_checks_total"] != 10
        or containment["p0_failure_stage"]
        != "before_all_registered_small_source_objects_were_available"
        or containment["p0_low_level_cause"]
        != "unresolved_without_raw_log_or_result_json"
        or containment["execution_server"] != "introai9"
        or containment["introai9_connection_verified"] is not True
        or containment["introai9_last_verified_pbs_jobs_observed"] != 0
        or containment["introai9_running_or_queued_aurora_jobs_after_final"] != 0
        or containment["pbs_ncpus"] != 2
        or containment["pbs_memory_gb"] != 4
        or containment["pbs_ngpus"] != 0
        or containment["pbs_walltime"] != "00:20:00"
        or containment["p0_pass_authorizes"]
        != "register_separate_method_free_p1_task_adequacy_audit_only"
        or containment["p0_failure_action"]
        != "close_exact_candidate_version_without_same_contract_repair_or_rerun"
    ):
        raise ProtocolError(
            "OpenNeuro containment P0 must preserve the 32.5/40 source history and its "
            "CPU-only execution-incomplete closure without payload, repair, or re-entry."
        )
    checks.append("OpenNeuro containment metadata/P0 boundary")
    target_audit = problem_selection["aneug_target_construction_source_audit"]
    _require_keys(
        target_audit,
        [
            "status",
            "audit_document",
            "dataset_repo",
            "dataset_commit",
            "code_repo",
            "code_commit",
            "paper_release",
            "reported_steady_cases",
            "reported_transient_cases",
            "reported_registered_wss_relative_l2_percent",
            "registered_surface_interpolator",
            "registered_coordinates_and_wss_interpolated_together",
            "registered_common_connectivity_retained",
            "registered_normals_recomputed_after_coordinate_transfer",
            "explicit_wss_tangent_projection_after_transfer",
            "explicit_area_or_functional_conservation_after_transfer",
            "processed_steady_normalization_before_random_split",
            "best_checkpoint_selected_on_test_loader_each_epoch",
            "transient_split_uses_ordered_prefix_matching",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "candidates",
            "direct_prior_threats",
            "field_or_mesh_payload_accessed",
            "large_model_or_checkpoint_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_pbs_jobs_observed",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_allowed_action",
        ],
        "AneuG target-construction source audit",
    )
    expected_target_scores = {
        "surface_vector_tangency_and_functional_commutation": 31.5,
        "area_integral_and_hotspot_conservative_target_transport": 31.0,
        "coordinate_connectivity_orientation_and_area_validity": 30.5,
        "remap_then_integrate_vs_integrate_then_remap_transient_functionals": 30.5,
        "split_blind_normalization_provenance": 30.0,
        "test_blind_checkpoint_and_prefix_split_reaudit": 29.5,
    }
    observed_target_scores = {
        candidate["id"]: candidate["score"]
        for candidate in target_audit["candidates"]
    }
    if (
        target_audit["status"]
        != "completed_source_only_all_rejected_below_admission_threshold"
        or target_audit["audit_document"]
        != "docs/aneug-target-construction-source-audit-2026-08-10.md"
        or target_audit["dataset_commit"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or target_audit["code_commit"]
        != "4a090a0f12538deef6fcea88b81afe78ce38152e"
        or target_audit["reported_steady_cases"] != 14000
        or target_audit["reported_transient_cases"] != 730
        or target_audit["reported_registered_wss_relative_l2_percent"] != 4.67
        or target_audit["registered_surface_interpolator"]
        != "torch_geometric_knn_interpolate_k3"
        or target_audit["registered_coordinates_and_wss_interpolated_together"]
        is not True
        or target_audit["registered_common_connectivity_retained"] is not True
        or target_audit["registered_normals_recomputed_after_coordinate_transfer"]
        is not True
        or target_audit["explicit_wss_tangent_projection_after_transfer"] is not False
        or target_audit["explicit_area_or_functional_conservation_after_transfer"]
        is not False
        or target_audit["processed_steady_normalization_before_random_split"]
        is not True
        or target_audit["best_checkpoint_selected_on_test_loader_each_epoch"]
        is not True
        or target_audit["transient_split_uses_ordered_prefix_matching"] is not True
        or target_audit["automatic_selection_threshold"] != 32.0
        or target_audit["best_candidate_id"]
        != "surface_vector_tangency_and_functional_commutation"
        or target_audit["best_score"] != 31.5
        or observed_target_scores != expected_target_scores
        or any(
            sum(candidate["axis_scores"]) != candidate["score"]
            for candidate in target_audit["candidates"]
        )
        or set(target_audit["direct_prior_threats"])
        != {
            "conservative_supermesh_interpolation_between_unstructured_meshes",
            "optimal_transport_neural_operator_for_varying_geometries",
            "conservation_law_neural_operator",
            "generic_surface_vector_tangent_projection_or_parallel_transport",
            "generic_train_only_normalization_and_test_blind_checkpoint_selection",
        }
        or any(
            target_audit[key] is not False
            for key in (
                "field_or_mesh_payload_accessed",
                "large_model_or_checkpoint_accessed",
                "executable_p0_registered",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "pbs_job_created",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or target_audit["execution_server"] != "introai9"
        or target_audit["introai9_connection_verified"] is not True
        or target_audit["introai9_pbs_jobs_observed"] != 0
        or target_audit["decision"]
        != "reject_all_without_score_repair_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or target_audit["next_allowed_action"]
        != "fresh_problem_level_primary_source_and_asset_audit_not_aneug_target_construction_repair_or_training"
    ):
        raise ProtocolError(
            "The AneuG target-construction audit must preserve all six frozen "
            "sub-threshold scores, public-source-only access, and no compute or method."
        )
    checks.append("AneuG target-construction source rejection boundary")
    vector_structure = problem_selection["aneug_surface_vector_structure_source_audit"]
    _require_keys(
        vector_structure,
        [
            "status",
            "audit_document",
            "candidate_id",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "axis_scores",
            "conditional_source_lead_count",
            "active_shortlist_count",
            "primary_problem_selected",
            "dataset_repo",
            "dataset_commit",
            "code_commit",
            "reported_transient_cases",
            "registered_probe_cases",
            "registered_wall_bytes",
            "registered_mesh_bytes",
            "registered_total_bytes",
            "field_or_mesh_payload_accessed",
            "blood_or_processed_payload_accessed",
            "large_model_or_checkpoint_accessed",
            "p0_config",
            "p0_protocol_id",
            "executable_p0_registered",
            "p0_job_submitted",
            "p0_job_id",
            "p0_public_source_commit",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_execution_status",
            "p0_final_job_state",
            "p0_exit_status",
            "p0_resources_used_walltime",
            "p0_resources_used_cput",
            "p0_resources_used_cpupercent",
            "p0_resources_used_memory_kb",
            "p0_resources_used_vmemory_kb",
            "p0_private_status_bytes",
            "p0_private_status_sha256",
            "p0_private_result_bytes",
            "p0_private_result_sha256",
            "p0_aggregate_scientific_result_materialized",
            "p0_raw_scheduler_output_materialized",
            "p0_persistent_probe_cache_files",
            "p0_registered_high_level_checks_evaluated",
            "p0_registered_high_level_checks_total",
            "p0_scientific_gate_evaluated",
            "p1_registration_authorized",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "direct_prior_threats",
            "execution_server",
            "introai9_connection_verified",
            "introai9_pbs_jobs_observed_before_registration",
            "pbs_job_created",
            "pbs_ncpus",
            "pbs_memory_gb",
            "pbs_ngpus",
            "pbs_walltime",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "p0_pass_authorizes",
            "p0_failure_action",
            "decision",
        ],
        "AneuG surface-vector structure source audit",
    )
    if (
        vector_structure["status"]
        != "p0_execution_incomplete_no_scientific_verdict_closed_without_repair_or_rerun"
        or vector_structure["audit_document"]
        != "docs/aneug-surface-vector-structure-source-audit-2026-08-10.md"
        or vector_structure["candidate_id"]
        != "time_varying_surface_wss_index_structure_prediction"
        or vector_structure["score"] != 32.0
        or vector_structure["maximum_score"] != 40.0
        or vector_structure["automatic_selection_threshold"] != 32.0
        or vector_structure["axis_scores"]
        != [4.5, 4.0, 2.5, 3.5, 4.5, 5.0, 5.0, 3.0]
        or sum(vector_structure["axis_scores"]) != vector_structure["score"]
        or vector_structure["conditional_source_lead_count"] != 0
        or vector_structure["active_shortlist_count"] != 0
        or vector_structure["primary_problem_selected"] is not False
        or vector_structure["dataset_repo"] != "whding123/AneuG-Flow"
        or vector_structure["dataset_commit"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or vector_structure["code_commit"]
        != "4a090a0f12538deef6fcea88b81afe78ce38152e"
        or vector_structure["reported_transient_cases"] != 730
        or vector_structure["registered_probe_cases"] != 3
        or vector_structure["registered_wall_bytes"] != 256179406
        or vector_structure["registered_mesh_bytes"] != 20463279
        or vector_structure["registered_total_bytes"] != 276642685
        or vector_structure["p0_config"]
        != "configs/aneug_surface_vector_structure_p0.json"
        or vector_structure["p0_protocol_id"]
        != "aneug_surface_vector_structure_raw_probe_p0_v1"
        or vector_structure["executable_p0_registered"] is not True
        or vector_structure["p0_job_submitted"] is not True
        or vector_structure["p0_job_id"] != "115645.ECE-util1"
        or vector_structure["p0_public_source_commit"]
        != "8a06de209892c09fe4adf86a3125a612a5030d9f"
        or vector_structure["p0_execution_record"]
        != "results/aneug_surface_vector_structure_p0_execution_20260810.json"
        or vector_structure["p0_execution_record_sha256"]
        != "4384651030883669bd8594606b125ee9597d32df4a9fd7cdb9010f37a96ec691"
        or vector_structure["p0_execution_status"]
        != "execution_incomplete_no_scientific_verdict"
        or vector_structure["p0_final_job_state"] != "E"
        or vector_structure["p0_exit_status"] != 2
        or vector_structure["p0_resources_used_walltime"] != "00:27:02"
        or vector_structure["p0_resources_used_cput"] != "00:00:06"
        or vector_structure["p0_resources_used_cpupercent"] != 8
        or vector_structure["p0_resources_used_memory_kb"] != 625780
        or vector_structure["p0_resources_used_vmemory_kb"] != 5076920
        or vector_structure["p0_private_status_bytes"] != 301
        or vector_structure["p0_private_status_sha256"]
        != "4881bcae77e39748fdf015ba886db4bea6c0485404a7271bed8b93ed7aaf15e2"
        or vector_structure["p0_private_result_bytes"] != 588
        or vector_structure["p0_private_result_sha256"]
        != "e52117efddf8102e80b7249fcfa2d23d926b074570d373f5e32c72f485ca296e"
        or vector_structure["p0_aggregate_scientific_result_materialized"] is not False
        or vector_structure["p0_raw_scheduler_output_materialized"] is not False
        or vector_structure["p0_persistent_probe_cache_files"] != 0
        or vector_structure["p0_registered_high_level_checks_evaluated"] != 0
        or vector_structure["p0_registered_high_level_checks_total"] != 10
        or vector_structure["p0_scientific_gate_evaluated"] is not False
        or vector_structure["p1_registration_authorized"] is not False
        or set(vector_structure["direct_prior_threats"])
        != {
            "hodge_spectral_duality_topology_preserving_neural_operator",
            "se3_equivariant_transient_surface_wss_estimation",
            "classical_time_varying_vector_field_critical_point_tracking",
            "critical_point_trajectory_preserving_vector_field_compression",
            "aneurysm_wss_critical_point_and_area_of_influence_analysis",
            "conservative_surface_remapping_and_tangent_projection",
        }
        or any(
            vector_structure[key] is not False
            for key in (
                "field_or_mesh_payload_accessed",
                "blood_or_processed_payload_accessed",
                "large_model_or_checkpoint_accessed",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or vector_structure["pbs_job_created"] is not True
        or vector_structure["execution_server"] != "introai9"
        or vector_structure["introai9_connection_verified"] is not True
        or vector_structure["introai9_pbs_jobs_observed_before_registration"] != 0
        or vector_structure["pbs_ncpus"] != 4
        or vector_structure["pbs_memory_gb"] != 16
        or vector_structure["pbs_ngpus"] != 0
        or vector_structure["pbs_walltime"] != "01:00:00"
        or vector_structure["p0_pass_authorizes"]
        != "register_separate_method_free_32_case_p1_structure_stability_audit_only"
        or vector_structure["p0_failure_action"]
        != "close_exact_candidate_version_without_same_contract_repair_or_rerun"
        or vector_structure["decision"]
        != "preserve_exact_32_source_history_but_close_execution_incomplete_without_repair_rerun_p1_method_architecture_gpu_outer_test_or_submission_claim"
    ):
        raise ProtocolError(
            "The AneuG surface-vector structure history must stay exactly at 32/40 "
            "and closed after one incomplete introai9 CPU P0 without P1 or model authority."
        )
    checks.append("AneuG surface-vector structure conditional P0 boundary")
    conditional_surface = problem_selection["surface_vector_conditional_assessment"]
    _require_keys(
        conditional_surface,
        [
            "status",
            "assessment_document",
            "analysis_reappraisal_status",
            "historical_candidate_id",
            "historical_source_score",
            "historical_p0_closed",
            "historical_p0_job_running",
            "historical_p0_scientific_checks_evaluated",
            "hypothesis",
            "evaluation_problem_is_independently_novel",
            "current_architecture",
            "current_architecture_is_gnn",
            "architecture_selected",
            "candidate_components_are_novel_individually",
            "candidate_components",
            "direct_prior_components",
            "latest_external_analysis_review_date",
            "latest_external_analysis_changed_scientific_state",
            "agents_running_status_correction_needed_at_review",
            "foundation_surface_feature_direct_prior",
            "new_evidence_version_requires_material_source_or_asset_change",
            "new_wrapper_downloader_retry_or_model_name_is_new_evidence",
            "same_contract_repair_or_rerun_allowed",
            "executable_p0_registered",
            "method_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "evidence_ladder",
            "independent_evaluation_unit",
            "primary_method_free_endpoints_before_e1",
            "secondary_endpoints_after_e1_stability_only",
            "critical_point_or_worldline_primary_before_e1_allowed",
            "structural_training_loss_before_e2_failure_allowed",
            "field_guard",
            "isbi_result_contract_all_required",
            "isbi_application_identity_status",
            "current_authorization",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_assessment",
        ],
        "surface-vector conditional assessment",
    )
    if (
        conditional_surface["status"]
        != "closed_until_whitelisted_material_release_inactive_conditional_hypothesis"
        or conditional_surface["assessment_document"]
        != "docs/surface-vector-finite-closure-and-reentry-contract-2026-08-12.md"
        or conditional_surface["analysis_reappraisal_status"]
        != "accept_problem_question_reject_architecture_selection_and_finitely_close_current_asset_family"
        or conditional_surface["historical_candidate_id"]
        != "time_varying_surface_wss_index_structure_prediction"
        or conditional_surface["historical_source_score"] != 32.0
        or conditional_surface["historical_p0_closed"] is not True
        or conditional_surface["historical_p0_job_running"] is not False
        or conditional_surface["historical_p0_scientific_checks_evaluated"] != 0
        or conditional_surface["hypothesis"]
        != "field_error_matched_transient_wss_surrogates_may_disagree_on_robust_signed_critical_points_and_cardiac_cycle_worldlines"
        or conditional_surface["evaluation_problem_is_independently_novel"] is not False
        or conditional_surface["current_architecture"] is not None
        or conditional_surface["current_architecture_is_gnn"] is not False
        or conditional_surface["candidate_components_are_novel_individually"] is not False
        or set(conditional_surface["direct_prior_components"])
        != {
            "physics_constrained_autoregressive_transient_aneurysm_mesh_gnn",
            "hodge_and_dec_operator_learning",
            "se3_equivariant_surface_wss_prediction",
            "critical_point_extraction_and_robust_tracking",
            "trajectory_preserving_vector_field_compression",
            "aneurysm_specific_cardiac_cycle_wss_critical_point_tracking",
            "nonmedical_3d_foundation_surface_feature_augmentation_for_aneurysm_flow_gnn",
        }
        or conditional_surface["latest_external_analysis_review_date"] != "2026-08-12"
        or conditional_surface["latest_external_analysis_changed_scientific_state"] is not False
        or conditional_surface["agents_running_status_correction_needed_at_review"] is not False
        or conditional_surface["new_evidence_version_requires_material_source_or_asset_change"] is not True
        or conditional_surface["new_wrapper_downloader_retry_or_model_name_is_new_evidence"] is not False
        or conditional_surface["same_contract_repair_or_rerun_allowed"] is not False
        or conditional_surface["independent_evaluation_unit"]
        != "generator_geometry_family_or_patient_not_vertices_triangles_phases_or_critical_points"
        or conditional_surface["field_guard"]
        != "area_weighted_field_error_noninferiority_and_calibration_language_only_for_probabilistic_outputs"
        or conditional_surface["primary_method_free_endpoints_before_e1"]
        != [
            "boundary_margin_signed_total_degree_validity",
            "certificate_efficiency_and_abstention",
        ]
        or conditional_surface["critical_point_or_worldline_primary_before_e1_allowed"]
        is not False
        or conditional_surface["structural_training_loss_before_e2_failure_allowed"]
        is not False
        or conditional_surface["isbi_result_contract_all_required"]
        != [
            "fresh_patient_or_base_family_confirmation",
            "area_weighted_field_error_noninferiority",
            "stable_structure_superiority_over_compute_and_field_error_matched_controls",
            "patient_or_base_family_bootstrap_uncertainty",
            "matched_case_interpretation_in_same_coordinates_and_color_scale",
        ]
        or conditional_surface["isbi_application_identity_status"]
        != "inactive_until_reproducible_field_error_matched_structural_failure_and_minimal_intervention_are_confirmed"
        or conditional_surface["execution_server"] != "introai9"
        or any(
            conditional_surface[key] is not False
            for key in (
                "architecture_selected",
                "executable_p0_registered",
                "method_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_assessment",
            )
        )
        or conditional_surface["evidence_ladder"]
        != [
            "e0_material_source_reentry",
            "e1_method_free_structure_stability",
            "e2_field_error_matched_failure_mechanism_and_baseline_feasibility",
            "e3_bounded_family_disjoint_validation_development",
            "e4_fresh_confirmatory_noninferior_field_and_superior_structure_evidence",
            "e5_external_physical_interpretation_without_clinical_overclaim",
        ]
        or set(conditional_surface["secondary_endpoints_after_e1_stability_only"])
        != {
            "signed_critical_point_precision_recall_with_geodesic_tolerance",
            "total_index_discrepancy_per_frame",
            "trajectory_assignment_distance",
            "temporally_tolerant_birth_death_event_f1",
        }
    ):
        raise ProtocolError(
            "The surface-vector idea must remain an inactive conditional hypothesis, "
            "closed for the current asset family; its exact P0 is immutable and re-entry "
            "requires a material source change through a whitelisted material release."
        )
    checks.append("finite surface-vector closure and material re-entry boundary")
    surface_closure = problem_selection["surface_vector_finite_closure"]
    _require_keys(
        surface_closure,
        [
            "status", "audit_document", "scientific_hypothesis_retained",
            "active_paper_identity", "current_asset_family_closed",
            "historical_aneug_job_id", "historical_aneug_job_state",
            "historical_aneug_exit_status", "historical_aneug_gpu_count",
            "historical_aneug_scientific_checks_evaluated_total",
            "historical_aneug_scientific_verdict", "historical_aneug_source_score",
            "historical_job_repaired_or_rerun", "aneug_dataset_head",
            "aneurisk_record_revision", "aneux_transient_head",
            "aaa_wss_repository_head", "trellis_repository_publicly_readable",
            "synthetic_aaa_release_tag", "synthetic_aaa_release_tag_commit",
            "synthetic_aaa_main_head", "synthetic_aaa_post_release_changed_paths",
            "synthetic_aaa_post_release_change_is_doi_and_citation_metadata_only",
            "synthetic_aaa_generated_population_committed",
            "synthetic_aaa_transient_field_cohort_committed",
            "fresh_material_e0_identified",
            "same_objects_new_wrapper_timeout_parser_cache_or_seed_is_fresh_evidence",
            "architecture_selected", "current_architecture",
            "current_architecture_is_gnn", "p0_registered", "p1_registered",
            "method_selected", "gpu_training_authorized", "outer_test_authorized",
            "paper_claim_authorized", "reentry_watch_config",
            "whitelisted_material_reentry_signals", "evidence_ladder",
            "scientific_server_queried", "pbs_or_gpu_job_created",
            "execution_server_if_future_gate_authorized",
            "login_node_gpu_command_executed", "junjinyong_accessed", "next_action",
        ],
        "surface-vector finite closure",
    )
    if (
        surface_closure["status"] != "closed_until_whitelisted_material_release"
        or surface_closure["audit_document"]
        != "docs/surface-vector-finite-closure-and-reentry-contract-2026-08-12.md"
        or surface_closure["scientific_hypothesis_retained"] is not True
        or surface_closure["active_paper_identity"] is not False
        or surface_closure["current_asset_family_closed"] is not True
        or surface_closure["historical_aneug_job_id"] != "115645.ECE-util1"
        or surface_closure["historical_aneug_job_state"] != "E"
        or surface_closure["historical_aneug_exit_status"] != 2
        or surface_closure["historical_aneug_gpu_count"] != 0
        or surface_closure["historical_aneug_scientific_checks_evaluated_total"]
        != [0, 10]
        or surface_closure["historical_aneug_scientific_verdict"] != "not_available"
        or surface_closure["historical_aneug_source_score"] != 32.0
        or surface_closure["historical_job_repaired_or_rerun"] is not False
        or surface_closure["aneug_dataset_head"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or surface_closure["aneurisk_record_revision"] != 4
        or surface_closure["aneux_transient_head"]
        != "38c574bc54a1ead9a4830da09ae5087e42b9d6c2"
        or surface_closure["aaa_wss_repository_head"]
        != "2f78bf1879e5e555c3369d91822be3f567f9fbd1"
        or surface_closure["trellis_repository_publicly_readable"] is not False
        or surface_closure["synthetic_aaa_release_tag"] != "v1.0.0"
        or surface_closure["synthetic_aaa_release_tag_commit"]
        != "98363a0104701dcc4bea11c2ee808eed1febafbe"
        or surface_closure["synthetic_aaa_main_head"]
        != "7872b816f1803195bcb54524caeb715970bfdcc7"
        or surface_closure["synthetic_aaa_post_release_changed_paths"]
        != ["CITATION.cff", "README.md"]
        or surface_closure[
            "synthetic_aaa_post_release_change_is_doi_and_citation_metadata_only"
        ]
        is not True
        or surface_closure["synthetic_aaa_generated_population_committed"] is not False
        or surface_closure["synthetic_aaa_transient_field_cohort_committed"] is not False
        or surface_closure["fresh_material_e0_identified"] is not False
        or surface_closure[
            "same_objects_new_wrapper_timeout_parser_cache_or_seed_is_fresh_evidence"
        ]
        is not False
        or surface_closure["current_architecture"] is not None
        or surface_closure["current_architecture_is_gnn"] is not False
        or surface_closure["reentry_watch_config"] != "configs/source_watch_v16.json"
        or surface_closure["whitelisted_material_reentry_signals"]
        != [
            "official_phase_resolved_surface_vector_schema_units_time_correspondence_and_family_manifest",
            "licensed_independent_phase_resolved_wss_cohort_with_prospective_split_capacity",
            "executable_direct_prior_code_checkpoint_fold_and_compatible_field_release",
            "physical_or_clinical_paired_reference_with_shared_coordinates_and_independent_anatomies",
        ]
        or surface_closure["evidence_ladder"]
        != [
            "e0_source_admission",
            "e1_method_free_degree_stability_and_abstention",
            "e2_field_error_matched_baseline_failure",
            "e3_bounded_family_disjoint_validation_development",
            "e4_fresh_field_noninferiority_and_structure_superiority_confirmation",
            "e5_matched_coordinate_interpretation_without_clinical_overclaim",
        ]
        or any(
            surface_closure[key] is not False
            for key in (
                "architecture_selected", "p0_registered", "p1_registered",
                "method_selected", "gpu_training_authorized", "outer_test_authorized",
                "paper_claim_authorized", "scientific_server_queried",
                "pbs_or_gpu_job_created", "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or surface_closure["execution_server_if_future_gate_authorized"] != "introai9"
        or surface_closure["next_action"]
        != "source_watch_only_for_whitelisted_material_signal_or_genuinely_fresh_problem_class_no_local_repair_or_compute"
    ):
        raise ProtocolError(
            "Surface-vector finite closure must preserve the exact no-verdict history, "
            "reject metadata-only re-entry, and authorize no local repair, model or compute."
        )
    checks.append("surface-vector closed-until-material-release invariant")
    foundation_prior = conditional_surface["foundation_surface_feature_direct_prior"]
    _require_keys(
        foundation_prior,
        [
            "status",
            "audit_document",
            "arxiv",
            "publication_doi",
            "anxplore_cases_reported",
            "common_uniform_parent_vessel",
            "pretraining_nonmedical_3d_assets",
            "feature_dimension",
            "rendered_views_per_object",
            "voxel_grid_edge",
            "active_surface_voxels_approximate",
            "gnn_core_modified_beyond_feature_addition",
            "runs_with_features",
            "runs_without_features",
            "small_model_rollout_rmse_without_features",
            "small_model_rollout_rmse_with_features",
            "large_model_rollout_rmse_without_features",
            "large_model_rollout_rmse_with_features",
            "paper_summary_error_reduction_percent_approximate",
            "surface_wss_critical_point_or_worldline_endpoint_reported",
            "independent_sealed_gnn_split_stated_in_inspected_source",
            "stated_code_url",
            "stated_code_url_http_status_on_2026_08_11",
            "github_exact_repository_search_count_on_2026_08_11",
            "source_watch_config",
            "source_watch_current_snapshot_matches",
            "source_watch_next_action",
            "source_watch_change_opens_only",
            "medical_payload_or_checkpoint_accessed",
            "server_queried",
            "pbs_job_created",
            "gpu_training_authorized",
            "junjinyong_accessed_for_this_audit",
            "decision",
        ],
        "TRELLIS surface-feature direct prior",
    )
    if (
        foundation_prior["status"]
        != "paper_verified_stated_code_url_currently_404_no_candidate_or_authorization_change"
        or foundation_prior["audit_document"]
        != "docs/trellis-surface-feature-direct-prior-delta-2026-08-11.md"
        or foundation_prior["arxiv"] != "2509.03095"
        or foundation_prior["publication_doi"]
        != "10.1016/j.neuri.2026.100259"
        or foundation_prior["anxplore_cases_reported"] != 101
        or foundation_prior["common_uniform_parent_vessel"] is not True
        or foundation_prior["pretraining_nonmedical_3d_assets"] != 500000
        or foundation_prior["feature_dimension"] != 1024
        or foundation_prior["rendered_views_per_object"] != 200
        or foundation_prior["voxel_grid_edge"] != 64
        or foundation_prior["active_surface_voxels_approximate"] != 5000
        or foundation_prior["gnn_core_modified_beyond_feature_addition"] is not False
        or foundation_prior["runs_with_features"] != 5
        or foundation_prior["runs_without_features"] != 5
        or foundation_prior["small_model_rollout_rmse_without_features"] != 7.57
        or foundation_prior["small_model_rollout_rmse_with_features"] != 6.09
        or foundation_prior["large_model_rollout_rmse_without_features"] != 4.03
        or foundation_prior["large_model_rollout_rmse_with_features"] != 3.55
        or foundation_prior["paper_summary_error_reduction_percent_approximate"] != 15
        or foundation_prior["surface_wss_critical_point_or_worldline_endpoint_reported"] is not False
        or foundation_prior["independent_sealed_gnn_split_stated_in_inspected_source"] is not False
        or foundation_prior["stated_code_url"]
        != "https://github.com/clementhrv/trellis_for_intra"
        or foundation_prior["stated_code_url_http_status_on_2026_08_11"] != 404
        or foundation_prior["github_exact_repository_search_count_on_2026_08_11"] != 0
        or foundation_prior["source_watch_config"]
        != "configs/source_watch_v4.json"
        or foundation_prior["source_watch_current_snapshot_matches"] is not True
        or foundation_prior["source_watch_next_action"] != "continue_watch_only"
        or foundation_prior["source_watch_change_opens_only"]
        != "direct_prior_baseline_feasibility_reaudit_only"
        or any(
            foundation_prior[key] is not False
            for key in (
                "medical_payload_or_checkpoint_accessed",
                "server_queried",
                "pbs_job_created",
                "gpu_training_authorized",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or foundation_prior["decision"]
        != "treat_foundation_surface_features_as_direct_control_without_reopening_surface_vector_source_score_p0_method_architecture_gpu_or_claim"
    ):
        raise ProtocolError(
            "The TRELLIS update must remain a direct-prior correction with a "
            "currently unavailable stated code URL and no candidate or compute authority."
        )
    checks.append("TRELLIS surface-feature direct-prior and no-authority boundary")
    removal_delta = problem_selection["expert_virtual_removal_pair_source_delta"]
    _require_keys(
        removal_delta,
        [
            "status",
            "audit_document",
            "candidate_id",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "axis_scores",
            "active_shortlist_count",
            "figshare_article_id",
            "figshare_doi",
            "figshare_version",
            "figshare_file_count",
            "figshare_total_bytes",
            "figshare_canonical_name_size_md5_manifest_sha256",
            "pathological_case_surfaces",
            "virtual_removal_case_surfaces",
            "matched_control_surfaces",
            "independent_paired_case_units",
            "top_level_license",
            "description_license",
            "license_statements_conflict",
            "payload_accessed",
            "official_paper_doi",
            "target_is_investigator_virtual_removal",
            "target_is_observed_same_patient_preaneurysm_anatomy",
            "second_observer_sensitivity_reported_in_paper",
            "second_observer_pair_exposed_in_public_manifest",
            "surface_vector_e0_satisfied",
            "phase_resolved_wss_field_available",
            "direct_prior_threats",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "server_queried",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_allowed_action",
        ],
        "expert virtual-removal pair source delta",
    )
    if (
        removal_delta["status"]
        != "completed_source_only_rejected_below_admission_threshold"
        or removal_delta["audit_document"]
        != "docs/expert-virtual-removal-pair-source-delta-2026-08-11.md"
        or removal_delta["candidate_id"]
        != "expert_virtual_removal_pair_counterfactual_emulation"
        or removal_delta["score"] != 28.5
        or removal_delta["maximum_score"] != 40.0
        or removal_delta["automatic_selection_threshold"] != 32.0
        or removal_delta["axis_scores"]
        != [4.5, 3.0, 1.5, 3.5, 1.5, 5.0, 5.0, 4.5]
        or sum(removal_delta["axis_scores"]) != removal_delta["score"]
        or removal_delta["active_shortlist_count"] != 0
        or removal_delta["figshare_article_id"] != 1159108
        or removal_delta["figshare_doi"] != "10.6084/m9.figshare.1159108.v3"
        or removal_delta["figshare_version"] != 3
        or removal_delta["figshare_file_count"] != 30
        or removal_delta["figshare_total_bytes"] != 163634666
        or removal_delta["figshare_canonical_name_size_md5_manifest_sha256"]
        != "875cc1f92f586ab4c9fba8b28180b57fa2c2e58657c6a98c2fb98e128e04a2fb"
        or removal_delta["pathological_case_surfaces"] != 10
        or removal_delta["virtual_removal_case_surfaces"] != 10
        or removal_delta["matched_control_surfaces"] != 10
        or removal_delta["independent_paired_case_units"] != 10
        or removal_delta["top_level_license"] != "CC_BY_4_0"
        or removal_delta["description_license"]
        != "CC_BY_NC_3_0_plus_bona_fide_researcher_restriction"
        or removal_delta["license_statements_conflict"] is not True
        or removal_delta["official_paper_doi"] != "10.1007/s10237-016-0804-3"
        or removal_delta["target_is_investigator_virtual_removal"] is not True
        or removal_delta["target_is_observed_same_patient_preaneurysm_anatomy"]
        is not False
        or removal_delta["second_observer_sensitivity_reported_in_paper"] is not True
        or removal_delta["second_observer_pair_exposed_in_public_manifest"] is not False
        or removal_delta["surface_vector_e0_satisfied"] is not False
        or removal_delta["phase_resolved_wss_field_available"] is not False
        or set(removal_delta["direct_prior_threats"])
        != {
            "original_virtual_removal_and_wss_initiation_analysis",
            "synva_healthy_vessel_generation_and_localized_aneurysm_editing",
            "aneug_morphology_conditioned_aneurysm_surface_generation",
            "intra_point_cloud_vessel_and_aneurysm_completion",
            "aneusi_automatic_aneurysm_and_neck_surface_isolation",
            "generic_counterfactual_reconstruction_and_anomaly_localization",
        }
        or any(
            removal_delta[key] is not False
            for key in (
                "payload_accessed",
                "executable_p0_registered",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "server_queried",
                "pbs_job_created",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or removal_delta["decision"]
        != "correct_historical_pair_absence_premise_but_reject_new_version_without_payload_p0_method_architecture_gpu_outer_test_or_claim"
        or removal_delta["next_allowed_action"]
        != "fresh_problem_level_source_audit_or_explicit_license_clarification_for_a_new_asset_audit_only_not_training"
    ):
        raise ProtocolError(
            "The expert virtual-removal pair must remain a source-only 28.5/40 "
            "rejection: it is not an observed healthy counterfactual or a "
            "surface-vector E0 asset and authorizes no payload, method, or compute."
        )
    checks.append("expert virtual-removal pair source-only rejection boundary")
    inverse_delta = problem_selection[
        "measurement_functional_inverse_flow_source_delta"
    ]
    _require_keys(
        inverse_delta,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "new_direct_prior_arxiv",
            "new_direct_prior_title",
            "new_direct_prior_submission_date",
            "new_direct_prior_velocity_observation_is_noisy_and_underresolved",
            "new_direct_prior_unknown_boundary_conditions",
            "new_direct_prior_exact_no_slip",
            "new_direct_prior_laplace_posterior",
            "new_direct_prior_wss_uncertainty_propagation",
            "new_direct_prior_reported_geometries",
            "new_direct_prior_code_or_data_link_exposed_on_arxiv_record",
            "benchanxplore_cases",
            "benchanxplore_timeframes",
            "benchanxplore_common_idealized_parent_vessel",
            "benchanxplore_compact_contract",
            "benchanxplore_compact_pressure_or_wss_contract_verified",
            "benchanxplore_all_cases_previously_used_for_representation_selection",
            "flowmri_dataset_doi",
            "flowmri_dataset_license",
            "flowmri_cerebrovascular_volunteers",
            "flowmri_cerebrovascular_training_volunteers",
            "flowmri_cerebrovascular_reference_test_volunteers",
            "cmrx_independent_research_embargo_end",
            "isbi_submission_deadline",
            "minnesota_in_vitro_effective_anatomies",
            "candidates",
            "new_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "server_queried",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "surface_vector_hypothesis_status",
            "decision",
        ],
        "measurement-functional inverse-flow source delta",
    )
    expected_inverse_candidates = [
        (
            "benchanxplore_transient_measurement_to_functional_posterior",
            30.0,
            [5.0, 3.0, 1.5, 4.5, 2.5, 5.0, 5.0, 3.5],
        ),
        (
            "in_vitro_cross_physics_functional_calibration_single_anatomy",
            29.0,
            [4.5, 4.5, 1.5, 4.0, 0.5, 5.0, 5.0, 4.0],
        ),
        (
            "device_state_posterior_wss_reconstruction_single_anatomy",
            28.0,
            [5.0, 3.0, 1.5, 5.0, 0.5, 5.0, 5.0, 3.0],
        ),
        (
            "amortized_exact_boundary_bayesian_fer_across_geometries",
            26.5,
            [5.0, 5.0, 1.0, 1.5, 1.5, 5.0, 4.5, 3.0],
        ),
        (
            "flowmri_cerebrovascular_kspace_to_wss_pressure_posterior",
            26.0,
            [5.0, 1.5, 1.5, 4.0, 1.0, 5.0, 5.0, 3.0],
        ),
        (
            "cmrx_functional_risk_reconstruction_embargoed",
            25.0,
            [5.0, 2.0, 1.0, 1.0, 5.0, 5.0, 5.0, 1.0],
        ),
    ]
    observed_inverse_candidates = [
        (candidate.get("id"), candidate.get("score"), candidate.get("axis_scores"))
        for candidate in inverse_delta["candidates"]
    ]
    if (
        inverse_delta["status"]
        != "completed_source_only_all_candidates_rejected_below_admission_threshold"
        or inverse_delta["audit_document"]
        != "docs/measurement-functional-inverse-flow-source-delta-2026-08-11.md"
        or inverse_delta["automatic_selection_threshold"] != 32.0
        or inverse_delta["best_candidate_id"]
        != "benchanxplore_transient_measurement_to_functional_posterior"
        or inverse_delta["best_score"] != 30.0
        or inverse_delta["active_shortlist_count"] != 0
        or inverse_delta["primary_problem_selected"] is not False
        or inverse_delta["new_direct_prior_arxiv"] != "2607.20224"
        or inverse_delta["new_direct_prior_submission_date"] != "2026-07-22"
        or inverse_delta["new_direct_prior_reported_geometries"] != 3
        or inverse_delta[
            "new_direct_prior_code_or_data_link_exposed_on_arxiv_record"
        ]
        is not False
        or any(
            inverse_delta[key] is not True
            for key in (
                "new_direct_prior_velocity_observation_is_noisy_and_underresolved",
                "new_direct_prior_unknown_boundary_conditions",
                "new_direct_prior_exact_no_slip",
                "new_direct_prior_laplace_posterior",
                "new_direct_prior_wss_uncertainty_propagation",
                "benchanxplore_common_idealized_parent_vessel",
                "benchanxplore_all_cases_previously_used_for_representation_selection",
            )
        )
        or inverse_delta["benchanxplore_cases"] != 105
        or inverse_delta["benchanxplore_timeframes"] != 80
        or inverse_delta["benchanxplore_compact_contract"]
        != ["coordinates", "tetrahedra", "velocity", "boundary_mask"]
        or inverse_delta["benchanxplore_compact_pressure_or_wss_contract_verified"]
        is not False
        or inverse_delta["flowmri_dataset_doi"]
        != "10.3929/ethz-b-000705347"
        or inverse_delta["flowmri_dataset_license"] != "CC_BY_SA_4_0"
        or inverse_delta["flowmri_cerebrovascular_volunteers"] != 10
        or inverse_delta["flowmri_cerebrovascular_training_volunteers"] != 9
        or inverse_delta["flowmri_cerebrovascular_reference_test_volunteers"]
        != 1
        or inverse_delta["cmrx_independent_research_embargo_end"] != "2026-12"
        or inverse_delta["isbi_submission_deadline"]
        != "2026-10-26T23:59:00-04:00"
        or inverse_delta["minnesota_in_vitro_effective_anatomies"] != 1
        or observed_inverse_candidates != expected_inverse_candidates
        or any(sum(axis_scores) != score for _, score, axis_scores in expected_inverse_candidates)
        or max(score for _, score, _ in expected_inverse_candidates)
        >= inverse_delta["automatic_selection_threshold"]
        or any(
            inverse_delta[key] is not False
            for key in (
                "new_payload_accessed",
                "executable_p0_registered",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "server_queried",
                "pbs_job_created",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or inverse_delta["surface_vector_hypothesis_status"]
        != "inactive_not_rejected_not_activated"
        or inverse_delta["decision"]
        != "reject_all_six_without_new_payload_p0_method_architecture_server_compute_outer_test_or_claim"
    ):
        raise ProtocolError(
            "The measurement-functional inverse-flow batch must preserve the "
            "30.0/40 source-only rejection, the new FER direct-prior boundary, "
            "the already-used BenchAnXplore limit, and zero method or compute."
        )
    checks.append("measurement-functional inverse-flow source-only rejection")
    structure_reappraisal = problem_selection[
        "structure_faithful_wss_source_reappraisal"
    ]
    _require_keys(
        structure_reappraisal,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "surface_vector_hypothesis_status",
            "historical_aneug_source_score",
            "historical_aneug_p0_job_id",
            "historical_aneug_p0_scientific_checks_evaluated",
            "historical_aneug_p0_closed_without_repair_or_rerun",
            "aneug_code_head",
            "aneug_dataset_head",
            "aneug_material_source_change_observed",
            "aneurisk_record",
            "aneurisk_record_version",
            "aneurisk_license",
            "aneurisk_geometries",
            "aneurisk_archive_bytes",
            "aneurisk_archive_md5",
            "aneurisk_readme_bytes",
            "aneurisk_public_readme_accessed",
            "aneurisk_archive_or_vtp_payload_accessed",
            "aneurisk_manifest_enumerates_vtp_arrays",
            "aneurisk_manifest_enumerates_phase_count_and_alignment",
            "aneurisk_manifest_exposes_critical_point_annotations_or_tolerances",
            "companion_paper_cycle_averaged_fixed_points_and_separatrices",
            "companion_paper_cardio_cycle_critical_point_worldlines",
            "companion_temporal_evolution_cases_shown",
            "aneurysm_specific_tracking_prior_lesions",
            "aneurysm_specific_tracking_prior_patients",
            "cfd_challenge_cases",
            "cfd_challenge_submissions",
            "cfd_challenge_teams",
            "cfd_challenge_independent_anatomy_count",
            "critical_points_and_worldlines_start_as_evaluation_not_loss",
            "hodge_is_required_strong_baseline_not_selected_proposal",
            "edge_one_form_guarantees_critical_point_fidelity",
            "poincare_hopf_boundary_contract_required",
            "candidates",
            "direct_prior_threats",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "server_queried",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_allowed_action",
        ],
        "structure-faithful WSS source reappraisal",
    )
    expected_structure_candidates = [
        (
            "aneurisk_cycle_averaged_fixed_point_faithful_surrogation",
            31.0,
            [4.5, 3.5, 1.5, 4.0, 3.5, 5.0, 5.0, 4.0],
        ),
        (
            "aneurisk_cycle_averaged_separatrix_network_surrogation",
            30.0,
            [4.5, 3.0, 1.5, 4.0, 3.5, 5.0, 5.0, 3.5],
        ),
        (
            "aneurisk_phase_resolved_critical_point_worldlines",
            29.0,
            [4.5, 2.0, 2.0, 3.5, 3.5, 5.0, 5.0, 3.5],
        ),
        (
            "aneurisk_structure_selective_surrogate_abstention",
            28.5,
            [4.5, 2.5, 1.5, 4.0, 3.5, 5.0, 4.5, 3.0],
        ),
        (
            "cfd_challenge_multi_pipeline_wss_topology_robustness",
            27.5,
            [4.5, 4.0, 1.0, 4.5, 0.5, 5.0, 4.5, 3.5],
        ),
        (
            "rhsia_structure_fidelity_benchmark_extension",
            27.0,
            [4.5, 2.0, 1.0, 1.5, 4.5, 5.0, 5.0, 3.5],
        ),
    ]
    observed_structure_candidates = [
        (candidate.get("id"), candidate.get("score"), candidate.get("axis_scores"))
        for candidate in structure_reappraisal["candidates"]
    ]
    expected_structure_priors = {
        "hodge_spectral_duality_discrete_form_topology_preserving_operator",
        "se3_equivariant_transient_surface_wss_mesh_prediction",
        "rhsia_graph_transformer_ghd_transient_wss_surrogation",
        "robust_critical_point_tracking",
        "critical_point_trajectory_preserving_vector_field_compression",
        "aneurysm_specific_cardiac_cycle_wss_critical_point_tracking",
    }
    if (
        structure_reappraisal["status"]
        != "completed_source_only_all_candidates_rejected_below_admission_threshold"
        or structure_reappraisal["audit_document"]
        != "docs/structure-faithful-wss-source-reappraisal-2026-08-11.md"
        or structure_reappraisal["automatic_selection_threshold"] != 32.0
        or structure_reappraisal["best_candidate_id"]
        != "aneurisk_cycle_averaged_fixed_point_faithful_surrogation"
        or structure_reappraisal["best_score"] != 31.0
        or structure_reappraisal["active_shortlist_count"] != 0
        or structure_reappraisal["primary_problem_selected"] is not False
        or structure_reappraisal["surface_vector_hypothesis_status"]
        != "inactive_conditional_not_active_paper_identity"
        or structure_reappraisal["historical_aneug_source_score"] != 32.0
        or structure_reappraisal["historical_aneug_p0_job_id"]
        != "115645.ECE-util1"
        or structure_reappraisal["historical_aneug_p0_scientific_checks_evaluated"]
        != 0
        or structure_reappraisal[
            "historical_aneug_p0_closed_without_repair_or_rerun"
        ]
        is not True
        or structure_reappraisal["aneug_code_head"]
        != "4a090a0f12538deef6fcea88b81afe78ce38152e"
        or structure_reappraisal["aneug_dataset_head"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or structure_reappraisal["aneug_material_source_change_observed"] is not False
        or structure_reappraisal["aneurisk_record"] != "10.5281/zenodo.19455127"
        or structure_reappraisal["aneurisk_record_version"] != "v1"
        or structure_reappraisal["aneurisk_license"] != "CC_BY_4_0"
        or structure_reappraisal["aneurisk_geometries"] != 76
        or structure_reappraisal["aneurisk_archive_bytes"] != 1430889142
        or structure_reappraisal["aneurisk_archive_md5"]
        != "8c66e7bb359d04bd1a5d6db6da3f3926"
        or structure_reappraisal["aneurisk_readme_bytes"] != 1436
        or structure_reappraisal["aneurisk_public_readme_accessed"] is not True
        or structure_reappraisal["aneurisk_archive_or_vtp_payload_accessed"]
        is not False
        or structure_reappraisal["aneurisk_manifest_enumerates_vtp_arrays"]
        is not False
        or structure_reappraisal[
            "aneurisk_manifest_enumerates_phase_count_and_alignment"
        ]
        is not False
        or structure_reappraisal[
            "aneurisk_manifest_exposes_critical_point_annotations_or_tolerances"
        ]
        is not False
        or structure_reappraisal[
            "companion_paper_cycle_averaged_fixed_points_and_separatrices"
        ]
        is not True
        or structure_reappraisal[
            "companion_paper_cardio_cycle_critical_point_worldlines"
        ]
        is not False
        or structure_reappraisal["companion_temporal_evolution_cases_shown"] != 1
        or structure_reappraisal["aneurysm_specific_tracking_prior_lesions"] != 359
        or structure_reappraisal["aneurysm_specific_tracking_prior_patients"] != 268
        or structure_reappraisal["cfd_challenge_cases"] != 5
        or structure_reappraisal["cfd_challenge_submissions"] != 28
        or structure_reappraisal["cfd_challenge_teams"] != 26
        or structure_reappraisal["cfd_challenge_independent_anatomy_count"] != 5
        or structure_reappraisal[
            "critical_points_and_worldlines_start_as_evaluation_not_loss"
        ]
        is not True
        or structure_reappraisal[
            "hodge_is_required_strong_baseline_not_selected_proposal"
        ]
        is not True
        or structure_reappraisal["edge_one_form_guarantees_critical_point_fidelity"]
        is not False
        or structure_reappraisal["poincare_hopf_boundary_contract_required"]
        is not True
        or observed_structure_candidates != expected_structure_candidates
        or any(
            sum(candidate["axis_scores"]) != candidate["score"]
            for candidate in structure_reappraisal["candidates"]
        )
        or set(structure_reappraisal["direct_prior_threats"])
        != expected_structure_priors
        or any(
            structure_reappraisal[key] is not False
            for key in (
                "executable_p0_registered",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "server_queried",
                "pbs_job_created",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or structure_reappraisal["decision"]
        != "reject_all_six_without_score_repair_archive_vtp_p0_method_architecture_server_compute_outer_test_or_claim"
        or structure_reappraisal["next_allowed_action"]
        != "fresh_problem_level_source_audit_or_material_official_phase_resolved_surface_wss_manifest_change_only_not_same_contract_repair"
    ):
        raise ProtocolError(
            "The structure-faithful WSS reappraisal must preserve all six "
            "sub-threshold scores, keep Hodge as a control, avoid treating "
            "critical structures as a loss before stability, and open no compute."
        )
    checks.append("structure-faithful WSS source rejection and no-compute boundary")
    degree_audit = problem_selection["conformal_degree_certificate_source_audit"]
    _require_keys(
        degree_audit,
        [
            "status",
            "audit_document",
            "config",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "conditional_source_lead_count",
            "active_shortlist_count",
            "primary_problem_selected",
            "new_estimand_is_historical_endpoint_fidelity_score_repair",
            "historical_surface_vector_source_scores_preserved",
            "historical_surface_vector_p0_job_id",
            "historical_surface_vector_p0_rerun_or_repair",
            "certificate_target",
            "certificate_guarantees_exact_critical_point_count_location_or_type",
            "certificate_guarantees_nonzero_degree_implies_at_least_one_zero",
            "coverage_scope",
            "independent_unit",
            "zenodo_record",
            "zenodo_record_revision",
            "zenodo_created",
            "zenodo_modified",
            "zenodo_status",
            "zenodo_access_right",
            "zenodo_license",
            "reported_patient_specific_geometries",
            "archive_bytes",
            "archive_md5",
            "readme_bytes",
            "readme_md5",
            "public_readme_accessed",
            "archive_or_vtp_payload_accessed",
            "companion_cycle_averaged_wss_fixed_points",
            "companion_phase_resolved_worldlines",
            "companion_inflow_uses_inlet_diameter_and_patient_age",
            "manifest_enumerates_vtp_arrays_units_or_case_mapping",
            "candidates",
            "direct_prior_threats",
            "p0_registered",
            "p0_protocol_id",
            "p0_archive_download_bytes",
            "p0_archive_job_local_only",
            "p0_scientific_check_count",
            "p0_critical_point_or_conformal_computation",
            "p0_submission_limit",
            "p0_job_submitted",
            "p0_job_id",
            "p0_submission_count",
            "p0_final_job_state",
            "p0_exit_status",
            "p0_walltime",
            "p0_cput",
            "p0_memory_kb",
            "p0_vmemory_kb",
            "p0_result_status",
            "p0_reported_error_class",
            "p0_scientific_gate_evaluated",
            "p0_scientific_checks_evaluated",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_private_status_bytes",
            "p0_private_status_sha256",
            "p0_private_result_bytes",
            "p0_private_result_sha256",
            "p0_aggregate_scientific_result_created",
            "p0_raw_scheduler_log_materialized",
            "p0_complete_archive_verified",
            "p0_vtp_header_access_reported",
            "p0_transient_partial_download_bytes",
            "p0_low_level_cause",
            "p1_registration_authorized",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "result_row_created",
            "paper_contribution_created",
            "submission_identity_active",
            "execution_server",
            "server_queried_for_this_audit",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "p0_pass_authorizes",
            "p0_failure_or_incomplete_action",
            "decision",
            "next_allowed_action",
        ],
        "conformal degree certificate source audit",
    )
    expected_degree_candidates = [
        (
            "patient_level_conformal_degree_certificate_for_surface_wss_surrogates",
            32.5,
            [4.5, 4.0, 3.0, 4.0, 3.5, 5.0, 5.0, 3.5],
            "conditional_source_lead_p0_only",
        ),
        (
            "conformal_critical_region_localization",
            31.0,
            [4.5, 3.5, 2.0, 4.0, 3.5, 5.0, 5.0, 3.5],
            "reject",
        ),
        (
            "conformal_separatrix_network_certificate",
            29.5,
            [4.5, 2.5, 2.0, 4.0, 3.5, 5.0, 5.0, 3.0],
            "reject",
        ),
        (
            "margin_trained_topology_preserving_surrogate",
            29.5,
            [4.5, 3.0, 1.0, 4.0, 3.5, 5.0, 5.0, 3.5],
            "reject",
        ),
        (
            "generic_structure_selective_abstention",
            29.0,
            [4.5, 3.0, 1.0, 4.0, 3.5, 5.0, 4.5, 3.5],
            "reject",
        ),
        (
            "phase_resolved_worldline_event_certificate",
            28.5,
            [4.5, 1.5, 2.5, 3.5, 3.5, 5.0, 5.0, 3.0],
            "reject",
        ),
    ]
    observed_degree_candidates = [
        (
            candidate.get("id"),
            candidate.get("score"),
            candidate.get("axis_scores"),
            candidate.get("decision"),
        )
        for candidate in degree_audit["candidates"]
    ]
    expected_degree_priors = {
        "uai_2025_guaranteed_prediction_sets_for_functional_surrogate_models",
        "functional_conformalized_distance_fields_with_uniform_downstream_certificate",
        "simultaneous_conformal_neural_operator_field_coverage",
        "uncertain_2d_vector_field_topology",
        "multilevel_critical_point_robustness",
        "hodge_spectral_duality",
        "se3_equivariant_transient_surface_wss_prediction",
        "rhsia_transient_wss_surrogation",
        "aneurisk_cycle_averaged_fixed_point_analysis",
    }
    if (
        degree_audit["status"]
        != "p0_execution_incomplete_no_scientific_verdict_closed_without_repair_or_rerun"
        or degree_audit["audit_document"]
        != "docs/conformal-degree-certificate-source-audit-2026-08-11.md"
        or degree_audit["config"] != "configs/aneurisk_conformal_degree_p0.json"
        or degree_audit["automatic_selection_threshold"] != 32.0
        or degree_audit["best_candidate_id"]
        != "patient_level_conformal_degree_certificate_for_surface_wss_surrogates"
        or degree_audit["best_score"] != 32.5
        or degree_audit["conditional_source_lead_count"] != 0
        or degree_audit["active_shortlist_count"] != 0
        or degree_audit["primary_problem_selected"] is not False
        or degree_audit["new_estimand_is_historical_endpoint_fidelity_score_repair"]
        is not False
        or degree_audit["historical_surface_vector_source_scores_preserved"] is not True
        or degree_audit["historical_surface_vector_p0_job_id"] != "115645.ECE-util1"
        or degree_audit["historical_surface_vector_p0_rerun_or_repair"] is not False
        or degree_audit["certificate_guarantees_exact_critical_point_count_location_or_type"]
        is not False
        or degree_audit["certificate_guarantees_nonzero_degree_implies_at_least_one_zero"]
        is not True
        or degree_audit["coverage_scope"]
        != "marginal_over_exchangeable_patient_units_not_conditional_or_per_critical_point"
        or degree_audit["independent_unit"] != "patient"
        or degree_audit["zenodo_record"] != 19455127
        or degree_audit["zenodo_record_revision"] != 4
        or degree_audit["zenodo_modified"] != "2026-04-07T14:32:30.723519+00:00"
        or degree_audit["zenodo_status"] != "published"
        or degree_audit["zenodo_access_right"] != "open"
        or degree_audit["zenodo_license"] != "CC_BY_4_0"
        or degree_audit["reported_patient_specific_geometries"] != 76
        or degree_audit["archive_bytes"] != 1430889142
        or degree_audit["archive_md5"] != "8c66e7bb359d04bd1a5d6db6da3f3926"
        or degree_audit["readme_bytes"] != 1436
        or degree_audit["readme_md5"] != "f552f4d1440848f0cdb8700371579115"
        or degree_audit["public_readme_accessed"] is not True
        or degree_audit["archive_or_vtp_payload_accessed"] is not False
        or degree_audit["companion_cycle_averaged_wss_fixed_points"] is not True
        or degree_audit["companion_phase_resolved_worldlines"] is not False
        or degree_audit["companion_inflow_uses_inlet_diameter_and_patient_age"]
        is not True
        or degree_audit["manifest_enumerates_vtp_arrays_units_or_case_mapping"]
        is not False
        or observed_degree_candidates != expected_degree_candidates
        or any(
            sum(candidate["axis_scores"]) != candidate["score"]
            for candidate in degree_audit["candidates"]
        )
        or set(degree_audit["direct_prior_threats"]) != expected_degree_priors
        or degree_audit["p0_registered"] is not True
        or degree_audit["p0_protocol_id"]
        != "aneurisk_conformal_degree_archive_semantics_p0_v1"
        or degree_audit["p0_archive_download_bytes"] != 1430889142
        or degree_audit["p0_archive_job_local_only"] is not True
        or degree_audit["p0_scientific_check_count"] != 10
        or degree_audit["p0_critical_point_or_conformal_computation"] is not False
        or degree_audit["p0_submission_limit"] != 1
        or degree_audit["p0_job_submitted"] is not True
        or degree_audit["p0_job_id"] != "115684.ECE-util1"
        or degree_audit["p0_submission_count"] != 1
        or degree_audit["p0_final_job_state"] != "E"
        or degree_audit["p0_exit_status"] != 2
        or degree_audit["p0_walltime"] != "00:40:06"
        or degree_audit["p0_cput"] != "00:00:01"
        or degree_audit["p0_memory_kb"] != 56812
        or degree_audit["p0_vmemory_kb"] != 1484532
        or degree_audit["p0_result_status"]
        != "execution_incomplete_no_scientific_verdict"
        or degree_audit["p0_reported_error_class"]
        != "AneuriskConformalDegreeP0Error"
        or degree_audit["p0_scientific_gate_evaluated"] is not False
        or degree_audit["p0_scientific_checks_evaluated"] != 0
        or degree_audit["p0_private_status_bytes"] != 323
        or degree_audit["p0_private_status_sha256"]
        != "c03716ad792dc21aec3fb21f1208f3d7c6d21ad38d35eff692788e1ba0955823"
        or degree_audit["p0_private_result_bytes"] != 971
        or degree_audit["p0_private_result_sha256"]
        != "7e9f04e2d68c1ed987fad4f1c5a2a230e8117e49f419b2717faaf534618ed8e4"
        or degree_audit["p0_execution_record"]
        != "results/aneurisk_conformal_degree_p0_execution_20260811.json"
        or degree_audit["p0_execution_record_sha256"]
        != "82480a830f8518f7ecfde71b4b7b19259426fa033f18230754e932a775fdf1ef"
        or degree_audit["p0_aggregate_scientific_result_created"] is not False
        or degree_audit["p0_raw_scheduler_log_materialized"] is not False
        or degree_audit["p0_complete_archive_verified"] is not False
        or degree_audit["p0_vtp_header_access_reported"] is not False
        or degree_audit["p0_transient_partial_download_bytes"] is not None
        or degree_audit["p0_low_level_cause"]
        != "unresolved_without_raw_scheduler_log_or_stage_specific_private_record"
        or degree_audit["p1_registration_authorized"] is not False
        or any(
            degree_audit[key] is not False
            for key in (
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "result_row_created",
                "paper_contribution_created",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or degree_audit["server_queried_for_this_audit"] is not True
        or degree_audit["pbs_job_created"] is not True
        or degree_audit["execution_server"] != "introai9"
        or degree_audit["p0_pass_authorizes"]
        != "register_separate_method_free_cpu_only_p1_intrinsic_field_boundary_and_degree_stability_audit_only"
        or degree_audit["p0_failure_or_incomplete_action"]
        != "close_exact_candidate_version_without_same_contract_repair_or_rerun"
        or degree_audit["decision"]
        != "preserve_exact_32_5_source_history_but_close_candidate_after_execution_incomplete_without_scientific_verdict_repair_rerun_p1_method_architecture_gpu_outer_test_or_claim"
        or degree_audit["next_allowed_action"]
        != "fresh_problem_level_primary_source_and_asset_audit_not_same_contract_repair_or_rerun"
    ):
        raise ProtocolError(
            "The conformal-degree audit must preserve the fresh 32.5/40 "
            "certificate estimand, patient-level marginal guarantee limits, "
            "exact closed CPU P0 outcome, and zero active lead/method/GPU/claim boundary."
        )
    checks.append("conformal degree closed execution-incomplete P0 boundary")
    cross_view = problem_selection["cross_view_projection_source_delta"]
    _require_keys(
        cross_view,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "conditional_source_lead_count",
            "active_shortlist_count",
            "primary_problem_selected",
            "midl_cross_view_source",
            "midl_source_uses_real_clinical_biplane_dsa",
            "midl_source_projection_origin",
            "midl_source_cases",
            "midl_source_split_ratio",
            "midl_source_inference_uses_both_views",
            "midl_source_rt_detr_ap_map50",
            "midl_source_joint_prompt_ap_map50",
            "adam_registration_and_confidentiality_agreement_required",
            "adam_payload_accessed",
            "adam_reported_scans",
            "adam_positive_scans",
            "adam_negative_scans",
            "adam_repeated_subject_scans_require_group_split",
            "sdan_clinical_dsa_images",
            "sdan_clinical_dsa_patients",
            "sdan_clinical_dsa_centers",
            "sdan_public_distribution_permitted",
            "sdan_reasonable_request_only",
            "path_length_correction_independent_cases",
            "path_length_correction_tdc_rmse_before",
            "path_length_correction_tdc_rmse_after",
            "candidates",
            "direct_prior_threats",
            "patient_payload_accessed",
            "user_access_agreement_accepted",
            "p0_or_p1_registered",
            "method_selected",
            "architecture_selected",
            "server_queried",
            "pbs_or_gpu_job_created",
            "gpu_training_authorized",
            "outer_test_authorized",
            "result_row_created",
            "paper_contribution_created",
            "submission_identity_active",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_material_change",
        ],
        "cross-view projection source delta",
    )
    expected_cross_view_candidates = [
        (
            "adam_projection_consistent_3d_lesion_set",
            31.0,
            [4.5, 4.0, 1.0, 3.0, 4.0, 5.0, 5.0, 4.5],
            "reject",
        ),
        (
            "adam_selective_biplanar_3d_point_localization",
            30.0,
            [4.5, 4.0, 0.5, 3.0, 4.0, 5.0, 5.0, 4.0],
            "reject",
        ),
        (
            "adam_cross_view_consistency_failure_audit",
            29.5,
            [4.5, 4.0, 1.0, 3.0, 4.0, 5.0, 5.0, 3.0],
            "reject",
        ),
        (
            "multicenter_single_frame_dsa_shift_abstention",
            26.5,
            [5.0, 4.0, 0.5, 0.5, 5.0, 5.0, 5.0, 1.5],
            "reject",
        ),
        (
            "cross_view_quantitative_dsa_functional_calibration",
            22.5,
            [5.0, 4.0, 0.5, 0.5, 0.5, 5.0, 5.0, 2.0],
            "reject",
        ),
        (
            "clinical_biplane_dsa_projection_set_localization",
            21.5,
            [5.0, 2.0, 1.5, 0.5, 0.5, 5.0, 5.0, 2.0],
            "reject",
        ),
    ]
    observed_cross_view_candidates = [
        (
            candidate.get("id"),
            candidate.get("score"),
            candidate.get("axis_scores"),
            candidate.get("decision"),
        )
        for candidate in cross_view["candidates"]
    ]
    expected_cross_view_priors = {
        "midl_2026_adam_mip_cross_view_z_prompting_and_consistency",
        "ribassist3d_selective_biplanar_localization_and_false_output_budget",
        "medical_image_analysis_2026_multioutput_conformal_2d_3d_landmark_regions",
        "eccv_2024_task_driven_conformal_uncertainty_for_inverse_problems",
        "provl_net_projective_geometry_aware_biplanar_3d_localization",
        "aneurysm_biplane_silhouette_curve_morphing_reconstruction",
        "clinical_dsa_path_length_and_kvp_cross_view_correction",
    }
    if (
        cross_view["status"] != "completed_source_only_all_candidates_rejected"
        or cross_view["audit_document"]
        != "docs/cross-view-projection-source-delta-2026-08-11.md"
        or cross_view["automatic_selection_threshold"] != 32.0
        or cross_view["best_candidate_id"]
        != "adam_projection_consistent_3d_lesion_set"
        or cross_view["best_score"] != 31.0
        or cross_view["conditional_source_lead_count"] != 0
        or cross_view["active_shortlist_count"] != 0
        or cross_view["primary_problem_selected"] is not False
        or cross_view["midl_cross_view_source"]
        != "openreview_f943ad69f9a9542edf4f959c51bb2a2b2ba7f2d2"
        or cross_view["midl_source_uses_real_clinical_biplane_dsa"] is not False
        or cross_view["midl_source_projection_origin"]
        != "deterministic_ap_and_lateral_mip_from_adam_3d_mra"
        or cross_view["midl_source_cases"] != 113
        or cross_view["midl_source_split_ratio"]
        != "8_1_1_case_split_subject_grouping_not_reported"
        or cross_view["midl_source_inference_uses_both_views"] is not False
        or cross_view["midl_source_rt_detr_ap_map50"] != 0.270
        or cross_view["midl_source_joint_prompt_ap_map50"] != 0.643
        or cross_view["adam_registration_and_confidentiality_agreement_required"]
        is not True
        or cross_view["adam_payload_accessed"] is not False
        or cross_view["adam_reported_scans"] != 113
        or cross_view["adam_positive_scans"] != 93
        or cross_view["adam_negative_scans"] != 20
        or cross_view["adam_repeated_subject_scans_require_group_split"] is not True
        or cross_view["sdan_clinical_dsa_images"] != 62187
        or cross_view["sdan_clinical_dsa_patients"] != 1114
        or cross_view["sdan_clinical_dsa_centers"] != 3
        or cross_view["sdan_public_distribution_permitted"] is not False
        or cross_view["sdan_reasonable_request_only"] is not True
        or cross_view["path_length_correction_independent_cases"] != 3
        or cross_view["path_length_correction_tdc_rmse_before"] != 0.23
        or cross_view["path_length_correction_tdc_rmse_after"] != 0.14
        or observed_cross_view_candidates != expected_cross_view_candidates
        or any(
            sum(candidate["axis_scores"]) != candidate["score"]
            for candidate in cross_view["candidates"]
        )
        or set(cross_view["direct_prior_threats"]) != expected_cross_view_priors
        or any(
            cross_view[key] is not False
            for key in (
                "patient_payload_accessed",
                "user_access_agreement_accepted",
                "p0_or_p1_registered",
                "method_selected",
                "architecture_selected",
                "server_queried",
                "pbs_or_gpu_job_created",
                "gpu_training_authorized",
                "outer_test_authorized",
                "result_row_created",
                "paper_contribution_created",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or cross_view["decision"]
        != "reject_all_without_score_repair_source_combination_novelty_or_compute"
        or cross_view["next_material_change"]
        != "paired_calibrated_clinical_ap_lateral_dsa_with_patient_split_keys_acquisition_geometry_timing_and_3d_reference_or_identified_set_target"
    ):
        raise ProtocolError(
            "The cross-view projection source delta must preserve the synthetic-MIP "
            "versus clinical-DSA distinction, reject all scores below 32, and open "
            "no access agreement, payload, method, server query, or GPU work."
        )
    checks.append("cross-view projection source rejection and no-compute boundary")
    functional_seg = problem_selection["functional_4dflow_segmentation_source_delta"]
    _require_keys(
        functional_seg,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "conditional_source_lead_count",
            "active_shortlist_count",
            "primary_problem_selected",
            "direct_source_title",
            "direct_source_doi",
            "direct_source_posted",
            "tof_mra_pretraining_scans",
            "clinical_7t_4dflow_scans",
            "tof_pretraining_scans_are_downstream_4dflow_units",
            "segmentation_target",
            "time_resolved_wss_uses_time_averaged_static_mask",
            "baseline_masks_manually_cleaned_for_functional_analysis",
            "nnunet_mean_wss_pa_mean",
            "nnunet_mean_wss_pa_sd",
            "nnunet_mean_wss_icc",
            "nnunet_max_wss_pa_mean",
            "nnunet_max_wss_pa_sd",
            "nnunet_max_wss_icc",
            "nnunet_wss_bias_percent_upper_bound",
            "unet_wss_bias_percent_approximate",
            "densenet_unet_wss_bias_percent_approximate",
            "clinical_imaging_publicly_shareable",
            "trained_weights_currently_released",
            "weights_promised_upon_publication",
            "public_phantom_effective_anatomy_count",
            "public_phantom_is_fresh_asset",
            "candidates",
            "direct_prior_threats",
            "clinical_image_or_mask_payload_accessed",
            "model_weight_or_checkpoint_accessed",
            "p0_or_p1_registered",
            "method_selected",
            "architecture_selected",
            "server_queried",
            "pbs_or_gpu_job_created",
            "gpu_training_authorized",
            "outer_test_authorized",
            "result_row_created",
            "paper_contribution_created",
            "submission_identity_active",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_material_change",
        ],
        "functional 4D-flow segmentation source delta",
    )
    expected_functional_candidates = [
        (
            "public_phantom_to_clinical_wss_segmentation_transfer",
            25.5,
            [5.0, 3.0, 1.5, 3.0, 0.5, 5.0, 5.0, 2.5],
            "reject",
        ),
        (
            "aneurysm_sac_aware_4dflow_functional_segmentation",
            24.5,
            [5.0, 3.5, 2.0, 0.5, 1.0, 5.0, 5.0, 2.5],
            "reject",
        ),
        (
            "patient_level_selective_wss_error_certificate",
            23.5,
            [5.0, 4.0, 1.0, 0.5, 1.0, 5.0, 5.0, 2.0],
            "reject",
        ),
        (
            "segmentation_induced_hemodynamic_ranking_reversal",
            23.5,
            [5.0, 4.0, 1.0, 0.5, 1.0, 5.0, 5.0, 2.0],
            "reject",
        ),
        (
            "resolution_shift_functional_segmentation",
            23.5,
            [4.5, 4.5, 0.5, 0.5, 1.0, 5.0, 5.0, 2.5],
            "reject",
        ),
        (
            "tof_pretrained_4dflow_anatomy_transfer",
            23.0,
            [4.5, 5.0, 0.0, 0.5, 1.0, 5.0, 5.0, 2.0],
            "reject",
        ),
    ]
    observed_functional_candidates = [
        (
            candidate.get("id"),
            candidate.get("score"),
            candidate.get("axis_scores"),
            candidate.get("decision"),
        )
        for candidate in functional_seg["candidates"]
    ]
    expected_functional_priors = {
        "medrxiv_2026_intracranial_4dflow_segmentation_and_wss_quantification",
        "vast_unsupervised_intracranial_4dflow_segmentation_and_physics_reconstruction",
        "compass_conformal_downstream_segmentation_metric_intervals",
        "generic_task_based_or_goal_oriented_segmentation",
        "segmentation_to_cfd_uncertainty_propagation",
        "tof_to_4dflow_transfer_and_resolution_adaptation",
    }
    if (
        functional_seg["status"] != "completed_source_only_all_candidates_rejected"
        or functional_seg["audit_document"]
        != "docs/functional-4dflow-segmentation-source-delta-2026-08-11.md"
        or functional_seg["automatic_selection_threshold"] != 32.0
        or functional_seg["best_candidate_id"]
        != "public_phantom_to_clinical_wss_segmentation_transfer"
        or functional_seg["best_score"] != 25.5
        or functional_seg["conditional_source_lead_count"] != 0
        or functional_seg["active_shortlist_count"] != 0
        or functional_seg["primary_problem_selected"] is not False
        or functional_seg["direct_source_title"]
        != "Automated Segmentation of Intracranial Arteries on 4D Flow MRI for Hemodynamic Quantification"
        or functional_seg["direct_source_doi"] != "10.64898/2026.03.09.26347567"
        or functional_seg["direct_source_posted"] != "2026-03-10"
        or functional_seg["tof_mra_pretraining_scans"] != 355
        or functional_seg["clinical_7t_4dflow_scans"] != 11
        or functional_seg["tof_pretraining_scans_are_downstream_4dflow_units"] is not False
        or functional_seg["segmentation_target"]
        != "circle_of_willis_not_aneurysm_sac"
        or functional_seg["time_resolved_wss_uses_time_averaged_static_mask"] is not True
        or functional_seg["baseline_masks_manually_cleaned_for_functional_analysis"] is not True
        or functional_seg["nnunet_mean_wss_pa_mean"] != 1.57
        or functional_seg["nnunet_mean_wss_pa_sd"] != 0.63
        or functional_seg["nnunet_mean_wss_icc"] != 0.96
        or functional_seg["nnunet_max_wss_pa_mean"] != 2.16
        or functional_seg["nnunet_max_wss_pa_sd"] != 1.05
        or functional_seg["nnunet_max_wss_icc"] != 0.97
        or functional_seg["nnunet_wss_bias_percent_upper_bound"] != 1.7
        or functional_seg["unet_wss_bias_percent_approximate"] != -5.0
        or functional_seg["densenet_unet_wss_bias_percent_approximate"] != 7.0
        or functional_seg["clinical_imaging_publicly_shareable"] is not False
        or functional_seg["trained_weights_currently_released"] is not False
        or functional_seg["weights_promised_upon_publication"] is not True
        or functional_seg["public_phantom_effective_anatomy_count"] != 1
        or functional_seg["public_phantom_is_fresh_asset"] is not False
        or observed_functional_candidates != expected_functional_candidates
        or any(
            sum(candidate["axis_scores"]) != candidate["score"]
            for candidate in functional_seg["candidates"]
        )
        or set(functional_seg["direct_prior_threats"]) != expected_functional_priors
        or any(
            functional_seg[key] is not False
            for key in (
                "clinical_image_or_mask_payload_accessed",
                "model_weight_or_checkpoint_accessed",
                "p0_or_p1_registered",
                "method_selected",
                "architecture_selected",
                "server_queried",
                "pbs_or_gpu_job_created",
                "gpu_training_authorized",
                "outer_test_authorized",
                "result_row_created",
                "paper_contribution_created",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_audit",
            )
        )
        or functional_seg["decision"]
        != "reject_all_without_score_repair_future_weight_promise_or_architecture_combination_novelty"
        or functional_seg["next_material_change"]
        != "usable_patient_level_aneurysm_4dflow_mask_velocity_wss_asset_with_split_keys_and_independently_novel_estimand"
    ):
        raise ProtocolError(
            "The functional 4D-flow segmentation audit must preserve the direct "
            "segmentation-to-WSS prior, distinguish 355 TOF pretraining scans from "
            "11 unavailable 4D-flow units, reject all scores below 32, and open no compute."
        )
    checks.append("functional 4D-flow segmentation direct-prior rejection")

    aneux_transient = problem_selection["aneux_transient_cfd_material_source_audit"]
    _require_keys(
        aneux_transient,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "axis_scores",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "dataset_id",
            "legacy_alias_id",
            "dataset_revision",
            "dataset_gated",
            "user_terms_or_contact_sharing_accepted",
            "license_tag",
            "sibling_count",
            "topology_qualified_case_folders",
            "bifurcation_case_folders",
            "sidewall_case_folders",
            "unique_visible_case_ids",
            "cross_topology_overlap_ids",
            "visible_id_is_verified_patient_or_base_family",
            "tensor_mesh_or_raw_readme_payload_accessed",
            "public_card_exposes_tensor_units_phases_bc_solver_split",
            "material_source_change_signal",
            "e0_pass",
            "historical_aneug_p0_repair_or_rerun_authorized",
            "direct_prior_threats",
            "source_watch_config",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
        ],
        "AneuX-derived transient-CFD material source audit",
    )
    expected_aneux_transient_priors = {
        "aneug_flow_transient_cfd_and_wss_baselines",
        "rhsia_graph_transformer_ghd_temporal_wss_and_steady_augmentation",
        "physics_constrained_aneurysm_mesh_gnn_and_inflow_ood",
        "multiphysics_transformer_gnn_thrombosis_surrogation",
        "hodge_hsd_and_se3_equivariant_surface_field_operators",
        "critical_point_tracking_and_trajectory_preservation",
    }
    if (
        aneux_transient["status"]
        != "fresh_source_batch_rejected_below_admission_metadata_only"
        or aneux_transient["audit_document"]
        != "docs/aneux-transient-cfd-material-source-audit-2026-08-11.md"
        or aneux_transient["automatic_selection_threshold"] != 32.0
        or aneux_transient["best_candidate_id"]
        != "topology_stratified_sidewall_bifurcation_transient_wss_generalization"
        or aneux_transient["best_score"] != 28.0
        or aneux_transient["axis_scores"]
        != [4.5, 3.0, 1.5, 2.5, 4.0, 5.0, 5.0, 2.5]
        or sum(aneux_transient["axis_scores"]) != aneux_transient["best_score"]
        or aneux_transient["all_candidate_scores"]
        != [28.0, 27.5, 27.5, 27.0, 26.0, 26.0]
        or max(aneux_transient["all_candidate_scores"])
        >= aneux_transient["automatic_selection_threshold"]
        or aneux_transient["conditional_source_lead_count"] != 0
        or aneux_transient["primary_problem_selected"] is not False
        or aneux_transient["dataset_id"] != "yiyings/transient-dataset"
        or aneux_transient["legacy_alias_id"] != "yiyings/sidewall-transient-cfd"
        or aneux_transient["dataset_revision"]
        != "38c574bc54a1ead9a4830da09ae5087e42b9d6c2"
        or aneux_transient["dataset_gated"] != "manual"
        or aneux_transient["user_terms_or_contact_sharing_accepted"] is not False
        or aneux_transient["license_tag"] != "cc-by-nc-4.0"
        or aneux_transient["sibling_count"] != 1940
        or aneux_transient["topology_qualified_case_folders"] != 323
        or aneux_transient["bifurcation_case_folders"] != 180
        or aneux_transient["sidewall_case_folders"] != 143
        or aneux_transient["unique_visible_case_ids"] != 322
        or aneux_transient["cross_topology_overlap_ids"] != ["SNF365"]
        or aneux_transient["visible_id_is_verified_patient_or_base_family"] is not False
        or aneux_transient["tensor_mesh_or_raw_readme_payload_accessed"] is not False
        or aneux_transient["public_card_exposes_tensor_units_phases_bc_solver_split"] is not False
        or aneux_transient["material_source_change_signal"] is not True
        or aneux_transient["e0_pass"] is not False
        or aneux_transient["historical_aneug_p0_repair_or_rerun_authorized"] is not False
        or set(aneux_transient["direct_prior_threats"])
        != expected_aneux_transient_priors
        or aneux_transient["source_watch_config"] != "configs/source_watch_v6.json"
        or any(
            aneux_transient[key] is not False
            for key in (
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or aneux_transient["execution_server"] != "introai9"
    ):
        raise ProtocolError(
            "The AneuX-derived transient-CFD audit must count visible IDs conservatively, "
            "reject all scores below 32, accept no gate, and open no P0, method, or compute."
        )
    checks.append("AneuX-derived transient-CFD material rejection and no-compute boundary")

    downstream = problem_selection["team_downstream_utility_reappraisal"]
    _require_keys(
        downstream,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "axis_scores",
            "all_candidate_scores",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "tmp_kakaotalk_sha256",
            "tmp_tistory_sha256",
            "latest_team_discussion_date",
            "new_team_discussion_detected",
            "team_question_retained_as_evaluation_template_only",
            "cmha_exploratory_result",
            "cmha_patients",
            "cmha_lesions",
            "cmha_clinical_morphology_auprc",
            "cmha_plus_hemodynamics_auprc",
            "cmha_delta_auprc",
            "cmha_patient_bootstrap_ci95",
            "cmha_official_case_map_verified",
            "cmha_contains_matched_surrogate_predictions",
            "cmha_negative_exploratory_signal_relabelled_as_confirmatory_failure",
            "historical_patient_condition_incremental_utility_score",
            "historical_patient_condition_incremental_utility_repaired",
            "pointflownet_publication_doi",
            "pointflownet_idealized_mca_geometries",
            "pointflownet_peak_systolic_only",
            "pointflownet_repository",
            "pointflownet_repository_head",
            "pointflownet_repository_release_count",
            "pointflownet_repository_license_spdx_id",
            "pointflownet_readme_bytes",
            "pointflownet_norm_stats_bytes",
            "pointflownet_checkpoint_bytes",
            "pointflownet_tracked_train_val_test_manifests_present",
            "pointflownet_cfd_payload_present",
            "pointflownet_code_executed",
            "pointflownet_public_repository_is_complete_executable_matched_baseline",
            "hemo_mpo_publication_doi",
            "hemo_mpo_public_code_contract_available",
            "hemo_mpo_data_publicly_available",
            "hemo_mpo_aneumo_patient_semantics_reconciled",
            "dryad_fsi_doi",
            "dryad_fsi_license",
            "dryad_fsi_effective_anatomies",
            "dryad_fsi_rigid_cases",
            "dryad_fsi_deformable_cases",
            "dryad_fsi_grid_resolutions",
            "dryad_fsi_time_samples_per_case",
            "dryad_fsi_payload_accessed",
            "dryad_grid_or_time_samples_counted_as_independent_units",
            "rupture_overlap_arxiv_id",
            "rupture_overlap_total_cases",
            "rupture_overlap_classifier_or_prediction_rule_reported",
            "direct_prior_threats",
            "source_watch_config",
            "p0_registered",
            "p1_registered",
            "method_selected",
            "architecture_selected",
            "scientific_server_queried",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "login_node_gpu_command_executed",
            "junjinyong_accessed",
        ],
        "team downstream-utility reappraisal",
    )
    expected_downstream_priors = {
        "pointflownet_peak_systolic_distance_to_wall_point_surrogation",
        "hemo_mpo_se3_mesh_physics_deeponet_operator",
        "aneux_pointnext_per_geometry_pinn_clinical_fusion",
        "aneug_rhsia_and_physics_constrained_transient_mesh_surrogates",
        "task_based_downstream_functional_evaluation",
        "generic_attention_multigrid_masked_rollout_and_temporal_operator_components",
    }
    if (
        downstream["status"]
        != "fresh_problem_batch_rejected_below_admission_no_joint_estimand_or_executable_new_baseline"
        or downstream["audit_document"]
        != "docs/team-downstream-utility-reappraisal-2026-08-11.md"
        or downstream["automatic_selection_threshold"] != 32.0
        or downstream["best_candidate_id"]
        != "geometry_only_peak_systolic_point_surrogation"
        or downstream["best_score"] != 27.0
        or downstream["axis_scores"]
        != [3.5, 4.0, 0.5, 2.0, 4.0, 5.0, 4.5, 3.5]
        or sum(downstream["axis_scores"]) != downstream["best_score"]
        or downstream["all_candidate_scores"]
        != [27.0, 25.5, 24.0, 24.0, 23.5, 21.5]
        or max(downstream["all_candidate_scores"])
        >= downstream["automatic_selection_threshold"]
        or downstream["conditional_source_lead_count"] != 0
        or downstream["primary_problem_selected"] is not False
        or downstream["tmp_kakaotalk_sha256"]
        != "ad99ccdcc66fcb57a049e6f2dfaa7ee11dd305779dd49a6e545b9b6b6cab175d"
        or downstream["tmp_tistory_sha256"]
        != "6d50cb4ae8db683cf2b4f1aa48c402a8765a64d0f19b5c67687912ab660c2b38"
        or downstream["latest_team_discussion_date"] != "2026-08-02"
        or downstream["new_team_discussion_detected"] is not False
        or downstream["team_question_retained_as_evaluation_template_only"]
        is not True
        or downstream["cmha_exploratory_result"]
        != "results/cmha_g1_exploratory_20260803.json"
        or downstream["cmha_patients"] != 99
        or downstream["cmha_lesions"] != 105
        or downstream["cmha_official_case_map_verified"] is not False
        or downstream["cmha_contains_matched_surrogate_predictions"] is not False
        or downstream[
            "cmha_negative_exploratory_signal_relabelled_as_confirmatory_failure"
        ]
        is not False
        or downstream["historical_patient_condition_incremental_utility_score"]
        != 23.5
        or downstream["historical_patient_condition_incremental_utility_repaired"]
        is not False
        or downstream["pointflownet_publication_doi"]
        != "10.1016/j.cmpb.2026.109308"
        or downstream["pointflownet_idealized_mca_geometries"] != 984
        or downstream["pointflownet_peak_systolic_only"] is not True
        or downstream["pointflownet_repository"]
        != "yiyingsheng07/PointFlowNet"
        or downstream["pointflownet_repository_head"]
        != "5cb4f2545d25b6e8b855806cb3a345b8b1d72594"
        or downstream["pointflownet_repository_release_count"] != 0
        or downstream["pointflownet_repository_license_spdx_id"] is not None
        or downstream["pointflownet_readme_bytes"] != 35
        or downstream["pointflownet_norm_stats_bytes"] != 538
        or downstream["pointflownet_checkpoint_bytes"] != 14120802
        or downstream["pointflownet_tracked_train_val_test_manifests_present"]
        is not False
        or downstream["pointflownet_cfd_payload_present"] is not False
        or downstream["pointflownet_code_executed"] is not False
        or downstream[
            "pointflownet_public_repository_is_complete_executable_matched_baseline"
        ]
        is not False
        or downstream["hemo_mpo_publication_doi"]
        != "10.1016/j.aej.2026.05.044"
        or downstream["hemo_mpo_public_code_contract_available"] is not False
        or downstream["hemo_mpo_data_publicly_available"] is not False
        or downstream["hemo_mpo_aneumo_patient_semantics_reconciled"] is not False
        or downstream["dryad_fsi_doi"] != "10.5061/dryad.pc866t22m"
        or downstream["dryad_fsi_license"] != "CC0"
        or downstream["dryad_fsi_effective_anatomies"] != 1
        or downstream["dryad_fsi_rigid_cases"] != 1
        or downstream["dryad_fsi_deformable_cases"] != 2
        or downstream["dryad_fsi_grid_resolutions"] != 2
        or downstream["dryad_fsi_time_samples_per_case"] != 55
        or downstream["dryad_fsi_payload_accessed"] is not False
        or downstream["dryad_grid_or_time_samples_counted_as_independent_units"]
        is not False
        or downstream["rupture_overlap_arxiv_id"] != "2606.00072"
        or downstream["rupture_overlap_total_cases"] != 8
        or downstream["rupture_overlap_classifier_or_prediction_rule_reported"]
        is not False
        or set(downstream["direct_prior_threats"])
        != expected_downstream_priors
        or downstream["source_watch_config"] != "configs/source_watch_v7.json"
        or any(
            downstream[key] is not False
            for key in (
                "p0_registered",
                "p1_registered",
                "method_selected",
                "architecture_selected",
                "scientific_server_queried",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
                "login_node_gpu_command_executed",
                "junjinyong_accessed",
            )
        )
        or downstream["execution_server"] != "introai9"
    ):
        raise ProtocolError(
            "The team downstream-utility reappraisal must preserve exploratory CMHA, "
            "direct-prior and one-anatomy boundaries, reject all scores below 32, "
            "and open no P0, method, architecture or compute."
        )
    checks.append("team downstream-utility rejection and no-compute boundary")

    source_watch_v4 = problem_selection["public_source_watch_v4"]
    _require_keys(
        source_watch_v4,
        [
            "status",
            "config",
            "watch_count",
            "watch_ids",
            "aneumo_github_head",
            "aneumo_github_release_count",
            "aneumo_github_license_spdx_id",
            "aneumo_github_repository_size_kib",
            "aneumo_huggingface_sha",
            "aneumo_huggingface_last_modified",
            "aneumo_huggingface_license_tags",
            "aneumo_huggingface_sibling_count",
            "aneumo_huggingface_siblings_sha256",
            "aneumo_real_case_or_mapping_entries",
            "maintainer_future_real_undeformed_release_statement_not_material_e0",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "automatic_download_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v4",
    )
    if (
        source_watch_v4["status"] != "watch_only_all_five_frozen_snapshots_match"
        or source_watch_v4["config"] != "configs/source_watch_v4.json"
        or source_watch_v4["watch_count"] != 5
        or source_watch_v4["watch_ids"]
        != [
            "iavs_public_release_v1",
            "topbrain2_material_release_v1",
            "trellis_stated_code_availability_v1",
            "aneumo_github_material_release_v1",
            "aneumo_huggingface_material_release_v1",
        ]
        or source_watch_v4["aneumo_github_head"]
        != "701d53dde3489d84dbe9bc8324254629162eb45a"
        or source_watch_v4["aneumo_github_release_count"] != 0
        or source_watch_v4["aneumo_github_license_spdx_id"] is not None
        or source_watch_v4["aneumo_github_repository_size_kib"] != 97770
        or source_watch_v4["aneumo_huggingface_sha"]
        != "f801adee816c18d3e18b23e6fcb147fe4c264209"
        or source_watch_v4["aneumo_huggingface_last_modified"]
        != "2026-03-19T11:17:28.000Z"
        or source_watch_v4["aneumo_huggingface_license_tags"]
        != ["license:cc-by-nc-nd-4.0"]
        or source_watch_v4["aneumo_huggingface_sibling_count"] != 370
        or source_watch_v4["aneumo_huggingface_siblings_sha256"]
        != "8cfc7347c80a52b19d43c83991dbc987cb154463f9669cfb259281d9b7331aa3"
        or source_watch_v4["aneumo_real_case_or_mapping_entries"] != []
        or source_watch_v4["maintainer_future_real_undeformed_release_statement_not_material_e0"] is not True
        or source_watch_v4["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v4[key] is not False
            for key in (
                "manual_review_triggered",
                "automatic_download_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v4["decision"] != "continue_fail_closed_metadata_watch_only"
    ):
        raise ProtocolError(
            "Source watch v4 must preserve all five exact public snapshots and "
            "create only a manual source re-audit signal, never payload or compute authority."
        )
    checks.append("five-source fail-closed metadata watch boundary")
    source_watch_v5 = problem_selection["public_source_watch_v5"]
    _require_keys(
        source_watch_v5,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "watch_ids",
            "aneug_huggingface_sha",
            "aneug_huggingface_last_modified",
            "aneug_huggingface_used_storage_bytes",
            "aneurisk_zenodo_revision",
            "aneurisk_archive_bytes",
            "aneurisk_archive_md5",
            "largeia_zenodo_revision",
            "largeia_access_right",
            "largeia_public_file_count",
            "topaneu_zenodo_revision",
            "topaneu_challenge_under_construction",
            "topaneu_join_registration_available",
            "topaneu_material_navigation_entries",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v5",
    )
    if (
        source_watch_v5["status"]
        != "watch_only_all_nine_frozen_snapshots_match"
        or source_watch_v5["config"] != "configs/source_watch_v5.json"
        or source_watch_v5["extends_historical_config"]
        != "configs/source_watch_v4.json"
        or source_watch_v5["config_sha256"]
        != "24c4d9b6d25bfe5fd77cddb9bf9fd593ce492ea70930051f070ee44c1b5438cb"
        or source_watch_v5["watch_count"] != 9
        or source_watch_v5["watch_ids"]
        != [
            "iavs_public_release_v1",
            "topbrain2_material_release_v1",
            "trellis_stated_code_availability_v1",
            "aneumo_github_material_release_v1",
            "aneumo_huggingface_material_release_v1",
            "aneug_huggingface_material_revision_v1",
            "aneurisk_zenodo_material_revision_v1",
            "largeia_zenodo_access_revision_v1",
            "topaneu_material_release_v1",
        ]
        or source_watch_v5["aneug_huggingface_sha"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or source_watch_v5["aneug_huggingface_last_modified"]
        != "2026-01-13T17:09:10.000Z"
        or source_watch_v5["aneug_huggingface_used_storage_bytes"]
        != 2632691749582
        or source_watch_v5["aneurisk_zenodo_revision"] != 4
        or source_watch_v5["aneurisk_archive_bytes"] != 1430889142
        or source_watch_v5["aneurisk_archive_md5"]
        != "8c66e7bb359d04bd1a5d6db6da3f3926"
        or source_watch_v5["largeia_zenodo_revision"] != 10
        or source_watch_v5["largeia_access_right"] != "restricted"
        or source_watch_v5["largeia_public_file_count"] != 0
        or source_watch_v5["topaneu_zenodo_revision"] != 4
        or source_watch_v5["topaneu_challenge_under_construction"] is not False
        or source_watch_v5["topaneu_join_registration_available"] is not True
        or source_watch_v5["topaneu_material_navigation_entries"]
        != [
            "data|https://topaneu-26.grand-challenge.org/data/",
            "evaluation|https://topaneu-26.grand-challenge.org/evaluation/",
        ]
        or source_watch_v5["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v5[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v5["decision"]
        != "continue_fail_closed_nine_source_metadata_watch_only_without_new_scientific_evidence"
    ):
        raise ProtocolError(
            "Source watch v5 must preserve all nine exact public snapshots, "
            "the terms and no-repair boundaries, and zero payload or compute authority."
        )
    checks.append("nine-source fail-closed metadata watch boundary")
    source_watch_v6 = problem_selection["public_source_watch_v6"]
    _require_keys(
        source_watch_v6,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "watch_ids",
            "aneux_transient_dataset_id",
            "aneux_transient_legacy_alias_id",
            "aneux_transient_sha",
            "aneux_transient_gated",
            "aneux_transient_license_tags",
            "aneux_transient_sibling_count",
            "aneux_transient_bifurcation_case_folders",
            "aneux_transient_sidewall_case_folders",
            "aneux_transient_unique_visible_case_ids",
            "aneux_transient_cross_topology_overlap_ids",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v6",
    )
    if (
        source_watch_v6["status"] != "watch_only_all_ten_frozen_snapshots_match"
        or source_watch_v6["config"] != "configs/source_watch_v6.json"
        or source_watch_v6["extends_historical_config"]
        != "configs/source_watch_v5.json"
        or source_watch_v6["config_sha256"]
        != "72487198df76491cf95547581438695fc04e09275a1f477e5017781ded1da5fe"
        or source_watch_v6["watch_count"] != 10
        or source_watch_v6["watch_ids"][-1]
        != "aneux_transient_cfd_material_revision_v1"
        or source_watch_v6["aneux_transient_dataset_id"]
        != "yiyings/transient-dataset"
        or source_watch_v6["aneux_transient_legacy_alias_id"]
        != "yiyings/sidewall-transient-cfd"
        or source_watch_v6["aneux_transient_sha"]
        != "38c574bc54a1ead9a4830da09ae5087e42b9d6c2"
        or source_watch_v6["aneux_transient_gated"] != "manual"
        or source_watch_v6["aneux_transient_license_tags"]
        != ["license:cc-by-nc-4.0"]
        or source_watch_v6["aneux_transient_sibling_count"] != 1940
        or source_watch_v6["aneux_transient_bifurcation_case_folders"] != 180
        or source_watch_v6["aneux_transient_sidewall_case_folders"] != 143
        or source_watch_v6["aneux_transient_unique_visible_case_ids"] != 322
        or source_watch_v6["aneux_transient_cross_topology_overlap_ids"]
        != ["SNF365"]
        or source_watch_v6["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v6[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v6["decision"]
        != "continue_fail_closed_ten_source_metadata_watch_only_without_new_scientific_evidence"
    ):
        raise ProtocolError(
            "Source watch v6 must preserve all ten exact metadata snapshots and "
            "create no gated access, historical repair, payload, or compute authority."
        )
    checks.append("ten-source fail-closed metadata watch boundary")
    source_watch_v7 = problem_selection["public_source_watch_v7"]
    _require_keys(
        source_watch_v7,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "watch_ids",
            "pointflownet_repository",
            "pointflownet_head",
            "pointflownet_release_count",
            "pointflownet_license_spdx_id",
            "pointflownet_readme_bytes",
            "pointflownet_norm_stats_bytes",
            "pointflownet_checkpoint_bytes",
            "pointflownet_split_manifests_present",
            "pointflownet_cfd_payload_present",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v7",
    )
    if (
        source_watch_v7["status"]
        != "watch_only_all_eleven_frozen_snapshots_match"
        or source_watch_v7["config"] != "configs/source_watch_v7.json"
        or source_watch_v7["extends_historical_config"]
        != "configs/source_watch_v6.json"
        or source_watch_v7["config_sha256"]
        != "351608168228d0877a6467ec9190d8bca31addaef9ad5592145768f6e2933015"
        or source_watch_v7["watch_count"] != 11
        or source_watch_v7["watch_ids"][-1]
        != "pointflownet_baseline_release_v1"
        or source_watch_v7["pointflownet_repository"]
        != "yiyingsheng07/PointFlowNet"
        or source_watch_v7["pointflownet_head"]
        != "5cb4f2545d25b6e8b855806cb3a345b8b1d72594"
        or source_watch_v7["pointflownet_release_count"] != 0
        or source_watch_v7["pointflownet_license_spdx_id"] is not None
        or source_watch_v7["pointflownet_readme_bytes"] != 35
        or source_watch_v7["pointflownet_norm_stats_bytes"] != 538
        or source_watch_v7["pointflownet_checkpoint_bytes"] != 14120802
        or source_watch_v7["pointflownet_split_manifests_present"] is not False
        or source_watch_v7["pointflownet_cfd_payload_present"] is not False
        or source_watch_v7["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v7[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v7["decision"]
        != "continue_fail_closed_eleven_source_watch_only_pointflownet_change_requests_baseline_reaudit"
    ):
        raise ProtocolError(
            "Source watch v7 must preserve all eleven exact snapshots and allow a "
            "PointFlowNet change to request baseline review only, never data, method or compute."
        )
    checks.append("eleven-source fail-closed baseline watch boundary")
    source_watch_v8 = problem_selection["public_source_watch_v8"]
    _require_keys(
        source_watch_v8,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "watch_ids",
            "aaa_wss_repository",
            "aaa_wss_head",
            "aaa_wss_release_count",
            "aaa_wss_license_spdx_id",
            "aaa_wss_readme_bytes",
            "aaa_wss_repository_size_kib",
            "aaa_wss_payload_or_code_entries",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v8",
    )
    if (
        source_watch_v8["status"]
        != "watch_only_all_twelve_frozen_snapshots_match"
        or source_watch_v8["config"] != "configs/source_watch_v8.json"
        or source_watch_v8["extends_historical_config"]
        != "configs/source_watch_v7.json"
        or source_watch_v8["config_sha256"]
        != "1f54a94637d064618227f9ed43c38e01901fde006cf452696903509ba58f9c7b"
        or source_watch_v8["watch_count"] != 12
        or source_watch_v8["watch_ids"][-1]
        != "aaa_wss_neural_surrogate_baseline_release_v1"
        or source_watch_v8["aaa_wss_repository"]
        != "PatRyg99/AAA-WSS-neural-surrogate"
        or source_watch_v8["aaa_wss_head"]
        != "2f78bf1879e5e555c3369d91822be3f567f9fbd1"
        or source_watch_v8["aaa_wss_release_count"] != 0
        or source_watch_v8["aaa_wss_license_spdx_id"] is not None
        or source_watch_v8["aaa_wss_readme_bytes"] != 183
        or source_watch_v8["aaa_wss_repository_size_kib"] != 0
        or source_watch_v8["aaa_wss_payload_or_code_entries"] != []
        or source_watch_v8["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v8[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v8["decision"]
        != "continue_fail_closed_twelve_source_watch_only_aaa_wss_change_requests_baseline_reaudit"
    ):
        raise ProtocolError(
            "Source watch v8 must preserve all twelve exact snapshots and allow "
            "an AAA-WSS repository change to request baseline review only, never "
            "task-asset access, architecture selection or compute."
        )
    checks.append("twelve-source fail-closed baseline watch boundary")
    source_watch_v9 = problem_selection["public_source_watch_v9"]
    _require_keys(
        source_watch_v9,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "watch_ids",
            "mris_bench_dataset_id",
            "mris_bench_legacy_alias_id",
            "mris_bench_sha",
            "mris_bench_last_modified",
            "mris_bench_license_tags",
            "mris_bench_sibling_count",
            "mris_bench_arrow_shard_count",
            "mris_bench_under_review_release_statement_present",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v9",
    )
    if (
        source_watch_v9["status"]
        != "watch_only_all_thirteen_frozen_snapshots_match"
        or source_watch_v9["config"] != "configs/source_watch_v9.json"
        or source_watch_v9["extends_historical_config"]
        != "configs/source_watch_v8.json"
        or source_watch_v9["config_sha256"]
        != "92e7cb9d87ad6ead118d4e41e230bd3bbd6b83d79b7ae78df34626a006a43c35"
        or source_watch_v9["watch_count"] != 13
        or source_watch_v9["watch_ids"][-1]
        != "mris_bench_postreview_target_contract_v1"
        or source_watch_v9["mris_bench_dataset_id"]
        != "lixiangcog/MRIS-Bench"
        or source_watch_v9["mris_bench_legacy_alias_id"]
        != "lixiang007666/MRIS-Bench"
        or source_watch_v9["mris_bench_sha"]
        != "6f2d6d9ad10eba68700ce95c7523ec78934f7a3d"
        or source_watch_v9["mris_bench_last_modified"]
        != "2026-05-15T03:22:31.000Z"
        or source_watch_v9["mris_bench_license_tags"] != ["license:mit"]
        or source_watch_v9["mris_bench_sibling_count"] != 12
        or source_watch_v9["mris_bench_arrow_shard_count"] != 8
        or source_watch_v9[
            "mris_bench_under_review_release_statement_present"
        ]
        is not True
        or source_watch_v9["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v9[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v9["decision"]
        != "continue_fail_closed_thirteen_source_watch_only_mris_change_requests_fresh_source_reaudit"
    ):
        raise ProtocolError(
            "Source watch v9 must preserve thirteen exact metadata snapshots and "
            "allow an MRIS-Bench change to request a fresh source audit only, never "
            "payload access, score repair, method selection or compute."
        )
    checks.append("thirteen-source fail-closed target-contract watch boundary")
    source_watch_v10 = problem_selection["public_source_watch_v10"]
    _require_keys(
        source_watch_v10,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "added_watch_id",
            "topaneu_main_head",
            "topaneu_current_release_tree",
            "topaneu_batch1_anchor_commit",
            "topaneu_current_manifest_count_per_family",
            "topaneu_batch1_manifest_count_per_family",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v10",
    )
    if (
        source_watch_v10["status"]
        != "watch_only_all_fourteen_frozen_snapshots_match"
        or source_watch_v10["config"] != "configs/source_watch_v10.json"
        or source_watch_v10["extends_historical_config"]
        != "configs/source_watch_v9.json"
        or source_watch_v10["config_sha256"]
        != "cc9f2004e5ec27bbb8a85b8b97da643475128e38a4122137361304e2a67c9eae"
        or source_watch_v10["watch_count"] != 14
        or source_watch_v10["added_watch_id"]
        != "topaneu_github_release_contract_v2"
        or source_watch_v10["topaneu_main_head"]
        != "018c243445f99199f484018c4c80575c84c72293"
        or source_watch_v10["topaneu_current_release_tree"]
        != "0bab2856144db5f0ba11e4151a59d44517481e95"
        or source_watch_v10["topaneu_batch1_anchor_commit"]
        != "15afd4b95e770f69cd3ff1dba9f625c65446a6e5"
        or source_watch_v10["topaneu_current_manifest_count_per_family"] != 417
        or source_watch_v10["topaneu_batch1_manifest_count_per_family"] != 98
        or source_watch_v10["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v10[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v10["decision"]
        != "continue_fail_closed_fourteen_source_watch_only_topaneu_git_change_requests_fresh_source_reaudit"
    ):
        raise ProtocolError(
            "Source watch v10 must preserve fourteen exact public snapshots; a "
            "TopAneu Git change may request source re-audit only, never terms, "
            "payload, score repair, P0, model or compute."
        )
    checks.append("fourteen-source fail-closed TopAneu version watch boundary")
    source_watch_v11 = problem_selection["public_source_watch_v11"]
    _require_keys(
        source_watch_v11,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "added_watch_id",
            "rsna_registry_file_commit_sha",
            "rsna_registry_blob_sha",
            "rsna_wiki_page_sha256",
            "rsna_controlled_access_declared",
            "rsna_data_resource_publication_forthcoming",
            "rsna_wiki_page_is_coming_soon_only",
            "rsna_machine_auditable_release_contract_present",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v11",
    )
    if (
        source_watch_v11["status"]
        != "watch_only_all_fifteen_frozen_snapshots_match"
        or source_watch_v11["config"] != "configs/source_watch_v11.json"
        or source_watch_v11["extends_historical_config"]
        != "configs/source_watch_v10.json"
        or source_watch_v11["config_sha256"]
        != "7bb95ea965615e3499d09039c28ad8ab6cdf3afbea53871d0c4c7268cab8025c"
        or source_watch_v11["watch_count"] != 15
        or source_watch_v11["added_watch_id"] != "rsna_ica_release_contract_v1"
        or source_watch_v11["rsna_registry_file_commit_sha"]
        != "523ffd3914ba99e6c4b17441f1633cc3eec74c69"
        or source_watch_v11["rsna_registry_blob_sha"]
        != "97b8c1f16b2809d2e82ec0c39d3b156b174c8c83"
        or source_watch_v11["rsna_wiki_page_sha256"]
        != "4f7d64017689437e6d93f5724f3f797054f3935d98a13148025b616b8db8fb2c"
        or source_watch_v11["rsna_controlled_access_declared"] is not True
        or source_watch_v11["rsna_data_resource_publication_forthcoming"]
        is not True
        or source_watch_v11["rsna_wiki_page_is_coming_soon_only"] is not True
        or source_watch_v11[
            "rsna_machine_auditable_release_contract_present"
        ]
        is not False
        or source_watch_v11["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v11[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v11["decision"]
        != "continue_fail_closed_fifteen_source_watch_only_rsna_release_contract_change_requests_fresh_source_reaudit"
    ):
        raise ProtocolError(
            "Source watch v11 must preserve fifteen exact public snapshots; an "
            "RSNA registry or wiki change may request source re-audit only, never "
            "terms, payload, score repair, P0, model or compute."
        )
    checks.append("fifteen-source fail-closed RSNA release-contract watch boundary")
    source_watch_v12 = problem_selection["public_source_watch_v12"]
    _require_keys(
        source_watch_v12,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "added_watch_ids",
            "topbrain2025_data_zenodo_revision",
            "topbrain2025_data_archive_bytes",
            "topbrain2025_data_archive_md5",
            "topbrain2025_podium_zenodo_revision",
            "bravecowcow_repository_head",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v12",
    )
    if (
        source_watch_v12["status"]
        != "watch_only_all_eighteen_frozen_snapshots_match"
        or source_watch_v12["config"] != "configs/source_watch_v12.json"
        or source_watch_v12["extends_historical_config"]
        != "configs/source_watch_v11.json"
        or source_watch_v12["config_sha256"]
        != "6c5ae0c328550bdc2cd0af66006250eee25766db73c0df81714e546b57e7fa7b"
        or source_watch_v12["watch_count"] != 18
        or source_watch_v12["added_watch_ids"]
        != [
            "topbrain2025_data_release_v1",
            "topbrain2025_podium_dockers_v1",
            "bravecowcow_rsna_multitask_baseline_v1",
        ]
        or source_watch_v12["topbrain2025_data_zenodo_revision"] != 14
        or source_watch_v12["topbrain2025_data_archive_bytes"] != 1958849592
        or source_watch_v12["topbrain2025_data_archive_md5"]
        != "b703ea31cd1f0e7115a5d3e6e61f59b3"
        or source_watch_v12["topbrain2025_podium_zenodo_revision"] != 18
        or source_watch_v12["bravecowcow_repository_head"]
        != "e59e2368a722eabedc6b2228b1c6e1e7325cacd5"
        or source_watch_v12["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v12[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v12["decision"]
        != "continue_fail_closed_eighteen_source_watch_only_changes_request_registered_review_without_terms_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v12 must preserve eighteen exact public snapshots; a "
            "TopBrain or BraveCoWCoW change may request only its registered review, "
            "never terms, payload, score repair, P0, model or compute."
        )
    checks.append("eighteen-source fail-closed TopBrain and RSNA baseline watch boundary")
    source_watch_v13 = problem_selection["public_source_watch_v13"]
    _require_keys(
        source_watch_v13,
        [
            "status",
            "config",
            "extends_historical_config",
            "config_sha256",
            "watch_count",
            "added_watch_ids",
            "da4dcta_zenodo_revision",
            "da4dcta_archive_bytes",
            "da4dcta_archive_md5",
            "da4dcta_repository_head",
            "da4dcta_visible_case_directories",
            "same_as_all_frozen_snapshots",
            "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized",
            "p0_or_p1_authorized",
            "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized",
            "server_queried",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v13",
    )
    if (
        source_watch_v13["status"]
        != "watch_only_all_twenty_frozen_snapshots_match"
        or source_watch_v13["config"] != "configs/source_watch_v13.json"
        or source_watch_v13["extends_historical_config"]
        != "configs/source_watch_v12.json"
        or source_watch_v13["config_sha256"]
        != "9c7d8350ffb0bfe992c20c2736537296d027bedc48d9e017bcee38337fb6d10b"
        or source_watch_v13["watch_count"] != 20
        or source_watch_v13["added_watch_ids"]
        != [
            "da4dcta_zenodo_material_release_v1",
            "da4dcta_github_release_and_baseline_v1",
        ]
        or source_watch_v13["da4dcta_zenodo_revision"] != 4
        or source_watch_v13["da4dcta_archive_bytes"] != 1934055674
        or source_watch_v13["da4dcta_archive_md5"]
        != "fd9f856b485983cd430ab94d01a24596"
        or source_watch_v13["da4dcta_repository_head"]
        != "8df7d45e9f65e3cbfd4ae3fc430c65a98905bdfc"
        or source_watch_v13["da4dcta_visible_case_directories"] != 52
        or source_watch_v13["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v13[key] is not False
            for key in (
                "manual_review_triggered",
                "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized",
                "p0_or_p1_authorized",
                "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized",
                "server_queried",
                "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v13["decision"]
        != "continue_fail_closed_twenty_source_watch_only_da4dcta_change_requests_fresh_source_reaudit_without_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v13 must preserve twenty exact public snapshots; a "
            "DA_4DCTA change may request fresh source re-audit only, never payload, "
            "score repair, P0, model or compute."
        )
    checks.append("twenty-source fail-closed DA_4DCTA watch boundary")
    source_watch_v14 = problem_selection["public_source_watch_v14"]
    _require_keys(
        source_watch_v14,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "asah_zenodo_revision",
            "asah_archive_bytes", "asah_archive_md5",
            "asah_pipeline_repository_head", "asah_multiclass_repository_head",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized", "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
            "p0_or_p1_authorized", "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized", "server_queried",
            "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v14",
    )
    if (
        source_watch_v14["status"]
        != "watch_only_all_twenty_three_frozen_snapshots_match"
        or source_watch_v14["config"] != "configs/source_watch_v14.json"
        or source_watch_v14["extends_historical_config"]
        != "configs/source_watch_v13.json"
        or source_watch_v14["config_sha256"]
        != "299c06ff709aa268a9f0b6b9bac22a30cb13d91f518df93971db3a9513c331ed"
        or source_watch_v14["watch_count"] != 23
        or source_watch_v14["added_watch_ids"]
        != [
            "asah_segmentation_zenodo_asset_v1",
            "asah_segmentation_mortality_code_v1",
            "asah_multiclass_baseline_release_v1",
        ]
        or source_watch_v14["asah_zenodo_revision"] != 2
        or source_watch_v14["asah_archive_bytes"] != 648502298
        or source_watch_v14["asah_archive_md5"]
        != "a67bf358ebb326f156071864c318ab42"
        or source_watch_v14["asah_pipeline_repository_head"]
        != "3fbd7a9282287a719aff5f603e9539b7a886b373"
        or source_watch_v14["asah_multiclass_repository_head"]
        != "269f4724fde89515eac8dbdac648925dc24bf492"
        or source_watch_v14["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v14[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized", "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
                "p0_or_p1_authorized", "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized", "server_queried",
                "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v14["decision"]
        != "continue_fail_closed_twenty_three_source_watch_only_asah_changes_request_registered_review_without_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v14 must preserve twenty-three exact public snapshots; "
            "aSAH changes may request only their registered review, never payload, "
            "score repair, P0, model or compute."
        )
    checks.append("twenty-three-source fail-closed aSAH asset and baseline watch boundary")
    source_watch_v15 = problem_selection["public_source_watch_v15"]
    _require_keys(
        source_watch_v15,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "synthetic_aaa_release_tag_commit",
            "synthetic_aaa_main_head", "synthetic_aaa_post_release_changed_paths",
            "synthetic_aaa_post_release_change_is_metadata_only",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized", "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
            "p0_or_p1_authorized", "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized", "server_queried",
            "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v15",
    )
    if (
        source_watch_v15["status"]
        != "watch_only_all_twenty_four_frozen_snapshots_match"
        or source_watch_v15["config"] != "configs/source_watch_v15.json"
        or source_watch_v15["extends_historical_config"]
        != "configs/source_watch_v14.json"
        or source_watch_v15["config_sha256"]
        != "a585e8b00fe10e168356edf9084fba5d861b75efa9fc609ac2a07cb7c0bf46af"
        or source_watch_v15["watch_count"] != 24
        or source_watch_v15["added_watch_ids"]
        != ["synthetic_aaa_cfd_material_release_v1"]
        or source_watch_v15["synthetic_aaa_release_tag_commit"]
        != "98363a0104701dcc4bea11c2ee808eed1febafbe"
        or source_watch_v15["synthetic_aaa_main_head"]
        != "7872b816f1803195bcb54524caeb715970bfdcc7"
        or source_watch_v15["synthetic_aaa_post_release_changed_paths"]
        != ["CITATION.cff", "README.md"]
        or source_watch_v15["synthetic_aaa_post_release_change_is_metadata_only"]
        is not True
        or source_watch_v15["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v15[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized", "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
                "p0_or_p1_authorized", "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized", "server_queried",
                "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v15["decision"]
        != "continue_fail_closed_twenty_four_source_watch_synthetic_aaa_change_requests_fresh_source_reaudit_only_without_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v15 must preserve twenty-four exact public snapshots; "
            "a Synthetic-AAA change may request source re-audit only, never E0, "
            "historical repair, method or compute."
        )
    checks.append("twenty-four-source fail-closed Synthetic-AAA material watch boundary")
    source_watch_v16 = problem_selection["public_source_watch_v16"]
    _require_keys(
        source_watch_v16,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "graph_physics_main_head",
            "wss_transolver_main_head", "expigeo_main_head",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized", "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
            "p0_or_p1_authorized", "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized", "server_queried",
            "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v16",
    )
    if (
        source_watch_v16["status"]
        != "watch_only_all_twenty_seven_frozen_snapshots_match"
        or source_watch_v16["config"] != "configs/source_watch_v16.json"
        or source_watch_v16["extends_historical_config"]
        != "configs/source_watch_v15.json"
        or source_watch_v16["config_sha256"]
        != "fb1b0cb80d764873f5364a4a56d3cd4c64dbd7c620e01bbb64d495da9de0b875"
        or source_watch_v16["watch_count"] != 27
        or source_watch_v16["added_watch_ids"]
        != [
            "graph_physics_spatiotemporal_direct_prior_v1",
            "aneurysm_wss_transolver_direct_prior_v1",
            "expigeo_geometry_gnn_direct_prior_v1",
        ]
        or source_watch_v16["graph_physics_main_head"]
        != "e4ac523d749b126f504665fb6270fcb91ac3cbd2"
        or source_watch_v16["wss_transolver_main_head"]
        != "3087fc9b8370ad39db85db9a61315bb34bf43cbb"
        or source_watch_v16["expigeo_main_head"]
        != "b28736842ec521641ea9389e4a9a58bccc5616f3"
        or source_watch_v16["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v16[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized", "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
                "p0_or_p1_authorized", "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized", "server_queried",
                "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v16["decision"]
        != "continue_fail_closed_twenty_seven_source_watch_new_code_is_direct_prior_only_without_task_asset_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v16 must preserve twenty-seven exact public states; "
            "new code can request direct-prior review only, never a task, method or compute."
        )
    checks.append("twenty-seven-source fail-closed direct-prior code watch boundary")
    source_watch_v17 = problem_selection["public_source_watch_v17"]
    _require_keys(
        source_watch_v17,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "synthetic_dsa_zenodo_record",
            "synthetic_dsa_zenodo_revision", "synthetic_dsa_zenodo_access",
            "synthetic_dsa_embargo_date",
            "synthetic_dsa_original_patient_images_present",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized", "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
            "p0_or_p1_authorized", "method_or_architecture_authorized",
            "gpu_or_outer_test_authorized", "server_queried",
            "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            "decision",
        ],
        "public source watch v17",
    )
    if (
        source_watch_v17["status"]
        != "watch_only_all_twenty_eight_frozen_snapshots_match"
        or source_watch_v17["config"] != "configs/source_watch_v17.json"
        or source_watch_v17["extends_historical_config"]
        != "configs/source_watch_v16.json"
        or source_watch_v17["config_sha256"]
        != "ebd1bdf0e6708e93c77b59870cf8cedbf051c16d41467673c516cc26ac5b3653"
        or source_watch_v17["watch_count"] != 28
        or source_watch_v17["added_watch_ids"]
        != ["synthetic_cerebral_dsa_reader_study_embargo_v1"]
        or source_watch_v17["synthetic_dsa_zenodo_record"] != 21104782
        or source_watch_v17["synthetic_dsa_zenodo_revision"] != 4
        or source_watch_v17["synthetic_dsa_zenodo_access"] != "embargoed"
        or source_watch_v17["synthetic_dsa_embargo_date"] != "2026-10-31"
        or source_watch_v17["synthetic_dsa_original_patient_images_present"] is not False
        or source_watch_v17["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v17[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized", "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized", "score_repair_authorized",
                "p0_or_p1_authorized", "method_or_architecture_authorized",
                "gpu_or_outer_test_authorized", "server_queried",
                "login_node_gpu_command_executed", "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v17["decision"]
        != "continue_fail_closed_twenty_eight_source_watch_synthetic_dsa_embargo_change_requests_source_reaudit_only_without_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v17 must preserve twenty-eight exact public states; "
            "an embargo change may request source review only, never task, method or compute."
        )
    checks.append("twenty-eight-source fail-closed synthetic DSA embargo watch boundary")
    source_watch_v18 = problem_selection["public_source_watch_v18"]
    _require_keys(
        source_watch_v18,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "adam_fold_repository_head",
            "adam_fold_release_asset_manifest_sha256",
            "dino_3dra_repository_head", "geop2vnet_repository_head",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized", "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized", "p0_or_p1_authorized",
            "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
            "server_queried", "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch", "decision",
        ],
        "public source watch v18",
    )
    if (
        source_watch_v18["status"]
        != "watch_only_all_thirty_one_frozen_snapshots_match"
        or source_watch_v18["config"] != "configs/source_watch_v18.json"
        or source_watch_v18["extends_historical_config"]
        != "configs/source_watch_v17.json"
        or source_watch_v18["config_sha256"]
        != "ab69bca79ba70d8b6543dbcc1e11d9091eaef201f0da61a6f29fa26320d7cf00"
        or source_watch_v18["watch_count"] != 31
        or source_watch_v18["added_watch_ids"]
        != [
            "adam_patch_fold_release_contract_v1",
            "dino_3dra_foundation_segmentation_direct_prior_v1",
            "geop2vnet_geometry_voxel_segmentation_direct_prior_v1",
        ]
        or source_watch_v18["adam_fold_repository_head"]
        != "d36df7d19a96aa5b9fca0cc9050e021ac7319fee"
        or source_watch_v18["adam_fold_release_asset_manifest_sha256"]
        != "7d5ebe80859b4d781a13a3c1b65d3b18fb2dfa2bd13486bb64c36b980b133f9c"
        or source_watch_v18["dino_3dra_repository_head"]
        != "5d9982ee794b531a8f04e73e849af0040976381f"
        or source_watch_v18["geop2vnet_repository_head"]
        != "25c59bc172d0fedac37c1b6cfc8fe4af0823bf65"
        or source_watch_v18["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v18[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized", "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized", "p0_or_p1_authorized",
                "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
                "server_queried", "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v18["decision"]
        != "continue_fail_closed_thirty_one_source_watch_patch_release_and_segmentation_code_request_review_only_without_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v18 must preserve thirty-one exact public states; "
            "release or code changes may request review only, never payload, method or compute."
        )
    checks.append("thirty-one-source fail-closed ADAM-fold and segmentation-prior watch boundary")
    source_watch_v19 = problem_selection["public_source_watch_v19"]
    _require_keys(
        source_watch_v19,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "cmrx4dflow_repository_head",
            "cmrx4dflow_release_count", "cmrx4dflow_license_spdx_id",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized", "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized", "p0_or_p1_authorized",
            "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
            "server_queried", "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch", "decision",
        ],
        "public source watch v19",
    )
    if (
        source_watch_v19["status"]
        != "watch_only_all_thirty_two_frozen_snapshots_match"
        or source_watch_v19["config"] != "configs/source_watch_v19.json"
        or source_watch_v19["extends_historical_config"]
        != "configs/source_watch_v18.json"
        or source_watch_v19["config_sha256"]
        != "911fa8b327b8f828de9ca349c577c9375d32e5fc3ddbe33ae8d06b0f04d1c228"
        or source_watch_v19["watch_count"] != 32
        or source_watch_v19["added_watch_ids"]
        != ["cmrx4dflow2026_embargoed_challenge_code_v1"]
        or source_watch_v19["cmrx4dflow_repository_head"]
        != "f6f835f34b86464256e3ce4362e7831325f32590"
        or source_watch_v19["cmrx4dflow_release_count"] != 0
        or source_watch_v19["cmrx4dflow_license_spdx_id"] is not None
        or source_watch_v19["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v19[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized", "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized", "p0_or_p1_authorized",
                "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
                "server_queried", "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v19["decision"]
        != "continue_fail_closed_thirty_two_source_watch_challenge_code_or_embargo_change_requests_review_only_without_terms_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v19 must preserve thirty-two exact public states; "
            "challenge-code changes request review only, never data, terms, method or compute."
        )
    checks.append("thirty-two-source fail-closed embargoed 4D-flow code watch boundary")
    source_watch_v20 = problem_selection["public_source_watch_v20"]
    _require_keys(
        source_watch_v20,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "cathaction_exact_sha",
            "cathaction_used_storage_bytes", "cathaction_archive_count",
            "cathaction_human_segmentation_archive_present",
            "cathaction_human_collision_archive_present",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized",
            "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized", "p0_or_p1_authorized",
            "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
            "server_queried", "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch", "decision",
        ],
        "source watch v20",
    )
    if (
        source_watch_v20["status"]
        != "watch_only_all_thirty_three_frozen_snapshots_match"
        or source_watch_v20["config"] != "configs/source_watch_v20.json"
        or source_watch_v20["extends_historical_config"]
        != "configs/source_watch_v19.json"
        or source_watch_v20["config_sha256"]
        != "57d2a8671e09a2f49d3e3b265ee87353b86245ecdf2d0199f482c11d50580198"
        or source_watch_v20["watch_count"] != 33
        or source_watch_v20["added_watch_ids"]
        != ["cathaction_intervention_release_contract_v1"]
        or source_watch_v20["cathaction_exact_sha"]
        != "8b04056f0f4fa4b04d8454728f000730af0d5560"
        or source_watch_v20["cathaction_used_storage_bytes"] != 56678352136
        or source_watch_v20["cathaction_archive_count"] != 4
        or source_watch_v20["cathaction_human_segmentation_archive_present"]
        is not True
        or source_watch_v20["cathaction_human_collision_archive_present"]
        is not False
        or source_watch_v20["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v20[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized",
                "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized", "p0_or_p1_authorized",
                "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
                "server_queried", "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v20["decision"]
        != "continue_fail_closed_thirty_three_source_watch_cathaction_change_requests_review_only_without_terms_payload_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v20 must preserve thirty-three exact public states; "
            "a CathAction change requests review only, never terms, payload, model or compute."
        )
    checks.append("thirty-three-source fail-closed intervention release watch boundary")
    source_watch_v21 = problem_selection["public_source_watch_v21"]
    _require_keys(
        source_watch_v21,
        [
            "status", "config", "extends_historical_config", "config_sha256",
            "watch_count", "added_watch_ids", "asah_risk_zenodo_record_id",
            "asah_risk_zenodo_revision", "asah_risk_file_bytes",
            "asah_risk_file_checksum", "asah_risk_medical_imaging_present",
            "asah_risk_fixed_six_month_outcome_identified",
            "same_as_all_frozen_snapshots", "manual_review_triggered",
            "fresh_source_reaudit_triggered",
            "direct_prior_baseline_feasibility_reaudit_triggered",
            "automatic_download_authorized", "automatic_terms_acceptance_authorized",
            "historical_execution_repair_or_rerun_authorized",
            "score_repair_authorized", "p0_or_p1_authorized",
            "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
            "server_queried", "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_watch", "decision",
        ],
        "source watch v21",
    )
    if (
        source_watch_v21["status"]
        != "watch_only_all_thirty_four_frozen_snapshots_match"
        or source_watch_v21["config"] != "configs/source_watch_v21.json"
        or source_watch_v21["extends_historical_config"]
        != "configs/source_watch_v20.json"
        or source_watch_v21["config_sha256"]
        != "ab34cf2b69e44877270250e1421eec057411a3a0a108c567bc8a22bf9a483dbb"
        or source_watch_v21["watch_count"] != 34
        or source_watch_v21["added_watch_ids"]
        != ["asah_risk_open_clinical_table_v1"]
        or source_watch_v21["asah_risk_zenodo_record_id"] != 17339029
        or source_watch_v21["asah_risk_zenodo_revision"] != 6
        or source_watch_v21["asah_risk_file_bytes"] != 39686
        or source_watch_v21["asah_risk_medical_imaging_present"] is not False
        or source_watch_v21["asah_risk_fixed_six_month_outcome_identified"] is not False
        or source_watch_v21["same_as_all_frozen_snapshots"] is not True
        or any(
            source_watch_v21[key] is not False
            for key in (
                "manual_review_triggered", "fresh_source_reaudit_triggered",
                "direct_prior_baseline_feasibility_reaudit_triggered",
                "automatic_download_authorized", "automatic_terms_acceptance_authorized",
                "historical_execution_repair_or_rerun_authorized",
                "score_repair_authorized", "p0_or_p1_authorized",
                "method_or_architecture_authorized", "gpu_or_outer_test_authorized",
                "server_queried", "login_node_gpu_command_executed",
                "junjinyong_accessed_for_this_watch",
            )
        )
        or source_watch_v21["decision"]
        != "continue_fail_closed_thirty_four_source_watch_open_clinical_table_change_requests_reaudit_only_without_download_p0_method_or_compute"
    ):
        raise ProtocolError(
            "Source watch v21 must preserve thirty-four exact public states; the open "
            "clinical-table watch may request review only, never download, P0 or compute."
        )
    checks.append("thirty-four-source fail-closed open clinical table watch boundary")
    if set(problem_selection["rejected_candidates"]) != {
        "endpoint_provenance_aware_asah_six_month_prognosis_mixed_time_and_no_imaging",
        "asis_management_to_one_year_mrs_direct_prior_and_synthetic_public_rows",
        "admission_only_external_calibration_of_asah_risk_no_external_cohort",
        "risk_score_refinement_for_future_instability_direct_prior_and_private_asset",
        "circle_of_willis_imaging_marker_transport_direct_prior_and_private_images",
        "center_robust_rupture_phenotype_dependency_case_only_and_private_rows",
        "topaneu_official_metric_instance_collapse_aware_evaluation_total_and_novelty_floors",
        "topaneu_registered_to_realized_benchmark_contract_fidelity_novelty_floor",
        "topaneu_external_centre_modality_generalization_direct_challenge_objective_and_private_test",
        "topaneu_gold_silver_provenance_conditioned_generalization_missing_casewise_manifest",
        "topaneu_bifurcation_uncertainty_aware_fine_location_missing_adjudicated_reference",
        "topaneu_longitudinal_patient_set_consistency_v2_no_chronology_growth_or_outcome_reference",
        "pre_contact_collision_onset_anticipation_missing_onset_horizon_and_independent_sequence_unit",
        "phantom_to_animal_collision_calibration_direct_prior_and_specimen_grouping_absent",
        "human_tool_segmentation_domain_generalization_direct_challenge_prior_and_unit_contract_absent",
        "action_conditioned_collision_early_warning_missing_cross_archive_identity_join",
        "segmentation_conditioned_collision_detection_missing_paired_mask_contact_reference",
        "aneurysm_specific_navigation_safety_transfer_missing_aneurysm_procedure_target",
        "cross_cohort_serum_proteomic_rupture_state_calibration_direct_prior_and_not_future_risk",
        "morphology_conditioned_proteomic_incremental_value_no_public_image_serum_join",
        "smoking_conditioned_plasma_mirna_mechanism_small_cross_sectional_direct_prior",
        "treatment_specific_inhospital_outcome_recalibration_no_public_rows_and_direct_prior",
        "pooled_tissue_serum_proteomic_reanalysis_four_biological_pools",
        "pre_event_imaging_proteomic_progression_prediction_missing_joint_temporal_asset",
        "device_phantom_venc_stable_hemodynamic_response_one_anatomy_unit_floor",
        "topology_faithful_cerebral_vessel_segmentation_direct_prior_and_twenty_mask_asset_floor",
        "reference_aware_multitask_aneurysm_segmentation_no_independent_dense_reference",
        "patient_grouped_multimodal_rsna_multitask_revalidation_not_method_novelty",
        "venet_label_uncertainty_and_topology_audit_evaluation_only",
        "aneurysm_specific_4dflow_reconstruction_embargo_after_deadline_and_unknown_units",
        "dino_feature_3dra_segmentation_extension_direct_code_prior_and_missing_training_fold_result_contract",
        "geometry_splatting_cta_segmentation_extension_direct_prior_and_unresolved_clinical_units",
        "modality_agnostic_anatomy_aware_weak_supervision_public_component_combination",
        "pre_post_stent_hemodynamic_remodeling_learning_single_patient_no_field_confirmation",
        "patient_grouped_adam_patch_benchmark_repair_provenance_not_paper_identity",
        "paired_adam_change_consistency_segmentation_no_growth_target_and_base_id_overlap",
        "clipfactor_orbit_morphometry_stability_audit_total_and_novelty_floor",
        "neck_conditioned_roi_isolation_transfer_direct_prior_and_engineering_only",
        "automatic_surface_neck_loop_transfer_neckspline_direct_prior_and_missing_expert_loop_contract",
        "differential_diagnosis_set_calibration_direct_prior_and_private_reference_errors",
        "neck_uncertainty_to_hemodynamic_functional_certificate_missing_joint_asset",
        "workflow_orbit_structure_faithful_wss_surrogate_direct_prior_and_four_anatomy_limit",
        "critical_flow_growth_biomarker_direct_prior_and_eleven_pair_limit",
        "low_shear_threshold_continuum_directly_tested_by_primary_paper",
        "mesh_fidelity_growth_signal_directly_tested_by_primary_paper",
        "growth_paired_structure_faithful_surrogate_retention_no_compatible_executable_surrogate",
        "image_to_growth_hemodynamics_no_open_image_contract_or_confirmatory_units",
        "released_code_paper_contract_reproducibility_audit_non_novel",
        "source_disjoint_latent_transport_reliability_directly_reported_by_source_paper",
        "miliary_shape_support_abstention_support_target_not_identified",
        "support_certified_saccular_model_transport_calibration_direct_prior",
        "nonsaccular_topology_aware_registration_target_not_identified",
        "open_cta_rupture_selective_prediction_nine_positive_units",
        "ostium_segmentation_with_synva_pretraining_direct_prior_and_missing_release_contract",
        "procedural_intervention_effect_audit_direct_prior_and_missing_action_asset",
        "source_disjoint_synthetic_pretraining_utility_evaluation_only_and_missing_manifest",
        "morphology_support_calibrated_synthetic_curriculum_missing_support_truth",
        "synthetic_to_real_hemodynamic_pretraining_construct_invalid",
        "patient_privacy_membership_audit_no_patient_members",
        "topaneu_revision_robust_lesion_set_ranking_interval_total_and_novelty_floors",
        "versioned_morphometry_partial_identification_total_and_novelty_floors",
        "rsna_clean_calibration_subgroup_risk_bound_no_clean_subset_or_public_asset",
        "reference_provenance_conditioned_segmentation_biased_ruler_direct_prior",
        "active_review_allocation_by_morphometric_utility_active_cleaning_direct_prior",
        "subgroup_biased_ruler_audit_no_adjudicated_reference",
        "topaneu_official_evaluator_patient_instance_unit_correction_novelty_floor",
        "topaneu_revision_conditioned_hierarchical_lesion_set_robustness_total_and_novelty_floors",
        "topaneu_type_location_factorized_instance_set_prediction_direct_prior_occupied",
        "topaneu_train_only_silver_vessel_privileged_distillation_direct_prior_occupied",
        "topaneu_center_modality_invariant_learning_confounding",
        "topaneu_longitudinal_growth_consistency_n7_no_chronology_or_reference",
        "synthetic_aaa_transient_wss_neural_operator_directly_occupied_no_real_paired_outer_reference",
        "selection_aware_virtual_population_validity_source_method_no_observed_target",
        "synthetic_to_real_aaa_hemodynamic_transport_no_matched_real_reference",
        "paired_regional_wall_stress_transcriptomic_program_direct_source_question_n12",
        "mechanobiology_conditioned_surface_operator_no_joint_patient_observation",
        "local_wss_to_cell_state_spatial_alignment_no_registered_local_field",
        "modality_semantic_contradiction_detection_no_adjudicated_reference_or_patient_grouping",
        "evidence_grounded_aneurysm_referring_segmentation_no_mask_target",
        "dataset_contract_and_provenance_benchmark_missing_lineage_and_adjudication",
        "patient_grouped_cross_slice_statement_consistency_no_patient_session_manifest",
        "label_noise_robust_mris_training_target_not_identified",
        "two_dimensional_descriptions_to_three_dimensional_lesion_consistency_no_volume_contract",
        "fixed_open_model_external_tof_mra_transport_and_morphometry_novelty_floor",
        "patient_level_selective_morphometry_total_and_novelty_floor",
        "dual_public_model_disagreement_not_reference_linked",
        "topology_conditioned_parent_vessel_failure_asset_and_novelty_floor",
        "public_model_pseudolabel_self_training_no_ground_truth_or_novelty",
        "longitudinal_prediction_consistency_change_not_identified",
        "sano_anatomical_fidelity_low_wss_reproduction_directly_occupied_and_n12",
        "sano_steady_wss_structural_stability_nonaneurysm_n12",
        "new_cfd_generation_on_aaa100_geometry_not_independent_confirmation",
        "aaa_transient_wss_structure_failure_fields_and_baseline_nonpublic",
        "aaa_longitudinal_structure_consistency_external_fields_nonpublic",
        "cross_vascular_structure_transfer_incompatible_contracts",
        "geometry_only_peak_systolic_point_surrogation_direct_prior_occupied",
        "rigid_fsi_model_form_robust_functional_concordance_effective_anatomy_one",
        "real_cfd_to_surrogate_downstream_status_retention_joint_observation_absent",
        "attention_multigrid_masked_rollout_gnn_architecture_only",
        "hemodynamic_overlap_aware_selective_status_abstention_eight_case_qualitative_source",
        "topology_stratified_sidewall_bifurcation_transient_wss_generalization",
        "generic_3d_aneurysm_segmentation_or_detection_with_uncertainty",
        "public_cohort_longitudinal_growth_detection",
        "geometry_boundary_condition_shape_response_operator",
        "cross_protocol_4d_flow_posterior_prediction",
        "annotation_selection_aware_mixed_granularity_anatomy_structured_lesion_set_inference",
        "goal_oriented_hemodynamic_segmentation",
        "inverse_healthy_vessel_counterfactual_editing",
        "dsa_prefix_to_final_vessel_support_risk_control",
        "openneuro_longitudinal_surface_growth_detection_direct_prior_and_unit_limited",
        "rsna_anatomy_indexed_point_set_detection_terms_gated_and_direct_prior_dense",
        "victoria_neck_curve_distribution_effective_geometry_n5",
        "intra_topology_false_positive_detection_payload_absent_and_direct_prior",
        "iaia_joint_aneurysm_stenosis_proposal_only",
        "flow_diverter_dsa_outcome_imaging_endpoint_not_linked",
        "topbrain_paired_modality_vascular_anatomy_without_aneurysm_endpoint",
        "ixi_healthy_vessel_atlas_as_aneurysm_anomaly_support",
        "vesselverse_protocol_conditioned_vessel_distribution_not_human_aneurysm_raters",
        "neckspline_multiloop_or_artifact_extension_direct_prior_occupied",
        "paired_cta_dose_reconstruction_phantom_orbit_effective_anatomy_one",
        "adam_longitudinal_or_post_treatment_remnant_endpoint_not_released",
        "physically_validated_incremental_hemodynamic_information_beyond_geometry_and_clinical_variables",
        "curvature_only_surrogate_of_local_hemodynamic_fields",
        "cross_source_curvature_residualized_hemodynamic_added_value",
        "within_patient_multiple_aneurysm_culprit_ranking",
        "paired_pre_post_treatment_remnant_change_prediction",
        "wall_enhancement_hemodynamic_discordance_localization",
        "cross_modality_tornadic_topology_preservation",
        "noise_resolution_stable_wss_topological_skeleton",
        "set_valued_c_arm_working_view_distribution",
        "differential_diagnosis_aware_open_set_tof_detection",
        "rheology_slip_model_form_hemodynamic_uncertainty",
        "ordered_parent_vessel_context_sufficiency_for_rupture_status",
        "paired_black_blood_to_4d_flow_treatment_response",
        "device_conditioned_counterfactual_treatment_selection",
        "morphology_decision_preserving_tof_segmentation",
        "external_latent_shape_calibration",
        "cross_release_lineage_blocked_cfd_to_rupture_transfer_validity",
        "source_conditional_selective_rupture_prediction",
        "test_blind_pointnet_external_reevaluation",
        "hug_curator_lineage_invariant_morphometry",
        "patient_set_multiple_aneurysm_rupture_consistency",
        "observed_interval_censored_post_fd_occlusion_forecasting",
        "causal_pipeline_versus_surpass_device_selection",
        "early_complication_delayed_occlusion_utility_prediction",
        "recurrent_procedure_patient_history_sequence_modeling",
        "fast_standard_tof_mra_remnant_decision_equivalence",
        "nested_acceleration_coherent_4d_flow_reconstruction",
        "cross_site_cross_anatomy_4d_flow_reconstruction",
        "explicit_multi_venc_divergence_free_uncertainty",
        "functional_risk_controlled_wss_vorticity_reconstruction",
        "treated_aneurysm_dual_venc_device_response_transfer",
        "rigid_to_compliant_hemodynamic_discrepancy_operator",
        "dynamic_geometry_inverse_wall_property_inference",
        "compliance_conditioned_flow_diverter_response",
        "lumen_to_wall_thickness_hotspot_prediction",
        "selective_rigid_cfd_to_fsi_referral",
        "multi_granularity_conformal_hemodynamic_surrogate",
        "informative_scan_aware_continuous_time_ctp_field_forecasting",
        "pre_dci_event_time_perfusion_early_warning",
        "personalized_ctp_reacquisition_policy",
        "treatment_conditioned_perfusion_counterfactual",
        "cross_modality_3dra_cta_hemodynamic_invariance",
        "global_local_vwe_hemodynamic_discordance",
        "acquisition_orbit_calibrated_longitudinal_mra_growth_detection",
        "single_anchor_weakly_supervised_local_growth_localization",
        "interval_censored_mra_growth_trajectory_forecasting",
        "mixed_modality_clinical_growth_measurement_harmonization",
        "awe_conditioned_long_term_instability_prediction",
        "same_day_post_flow_diverter_multimodal_disagreement_modeling",
        "geometry_flow_compositional_ood_generalization",
        "hierarchical_deformation_vs_family_uncertainty_calibration",
        "shape_derivative_informed_deformation_response",
        "synthetic_to_real_selection_on_ten_original_cases",
        "family_disjoint_transient_wss_forecasting",
        "cause_specific_false_positive_risk_control",
        "topaneu_post_release_attachment_consistency",
        "directional_topology_small_lesion_bifurcation_error_control",
        "synthetic_avatar_structural_fidelity_for_rupture_status",
        "angiography_to_preclinical_tissue_ingrowth_translation",
        "imaging_to_spatial_wall_cell_state_alignment",
        "one_sided_outer_annotation_morphometry_sets",
        "sparse_view_dsa_neck_risk_reconstruction",
        "segmentation_software_threshold_orbit_calibrated_morphometry",
        "dose_reconstruction_phantom_aneurysm_consistency",
        "biplane_shape_posterior_for_neck_and_lobulation",
        "reconstruction_induced_hemodynamic_risk_propagation",
        "royal_reference_morphometry_certificate_direct_prior_occupied",
        "partial_observation_solution_functional_operator_direct_prior_occupied",
        "iavs_topology_to_cfd_reliability_unreleased_and_direct_prior_occupied",
        "rsna_reader_source_reliability_without_per_reader_manifest",
        "cq500_provenance_aware_multimodal_adaptation_without_versioned_annotation_source",
        "public_test_only_rupture_status_reuse_direct_prior_and_lineage_unresolved",
        "scalar_vwe_hemodynamic_association_without_instability_endpoint_or_fields",
        "open_cfd_pipeline_numerical_certificate_without_independent_reference",
        "cross_cohort_rupture_transcriptomic_core_without_imaging_bridge",
        "autopsy_circle_of_willis_variant_geometry_prior_without_casewise_asset",
        "multicenter_study_level_lesion_set_risk_control",
        "solver_population_calibrated_hemodynamic_functionals",
        "rupture_destined_longitudinal_sig_forecasting",
        "asah_day21_hydrocephalus_dynamic_imaging",
        "vwi_habitat_instability_reanalysis",
        "synthetic_dsa_reader_realism",
        "rsna_registry_backed_study_level_lesion_set_miss_risk_control",
        "topbrain2_joint_lesion_parent_vessel_consistency",
        "topbrain2_disease_conditioned_selective_vessel_segmentation",
        "topbrain2_aneurysm_conditioned_vessel_integrity_failure_localization",
        "topbrain2_unified_modality_source_invariant_artery_vein_anatomy",
        "topbrain2_class_contamination_aware_multiclass_vessel_calibration",
        "topbrain2_compositional_aneurysm_stenosis_ordinal_diagnosis",
        "four_d_cta_phase_subset_rsii_hotspot_preservation",
        "four_d_cta_image_to_rsii_surface_operator",
        "four_d_cta_mechanics_consistent_cardiac_cycle_registration",
        "four_d_cta_synthetic_gt_calibrated_selective_strain_mapping",
        "four_d_cta_centre_pipeline_invariant_structural_integrity_mapping",
        "four_d_cta_progression_or_rupture_prediction_from_released_mechanics",
        "topaneu_factorized_leaf_risk_with_train_only_silver_anatomy_v2_direct_prior_occupied",
        "acquisition_quality_indexed_external_lesion_set_risk",
        "cross_center_weak_to_strong_segmentation",
        "conformal_lesion_fnr_control",
        "surface_vector_tangency_and_functional_commutation",
        "area_integral_and_hotspot_conservative_target_transport",
        "coordinate_connectivity_orientation_and_area_validity",
        "remap_then_integrate_vs_integrate_then_remap_transient_functionals",
        "split_blind_normalization_provenance",
        "test_blind_checkpoint_and_prefix_split_reaudit",
        "expert_virtual_removal_pair_counterfactual_emulation",
        "benchanxplore_transient_measurement_to_functional_posterior",
        "in_vitro_cross_physics_functional_calibration_single_anatomy",
        "device_state_posterior_wss_reconstruction_single_anatomy",
        "amortized_exact_boundary_bayesian_fer_across_geometries",
        "flowmri_cerebrovascular_kspace_to_wss_pressure_posterior",
        "cmrx_functional_risk_reconstruction_embargoed",
        "aneurisk_cycle_averaged_fixed_point_faithful_surrogation",
        "aneurisk_cycle_averaged_separatrix_network_surrogation",
        "aneurisk_phase_resolved_critical_point_worldlines",
        "aneurisk_structure_selective_surrogate_abstention",
        "cfd_challenge_multi_pipeline_wss_topology_robustness",
        "rhsia_structure_fidelity_benchmark_extension",
        "adam_projection_consistent_3d_lesion_set",
        "adam_selective_biplanar_3d_point_localization",
        "adam_cross_view_consistency_failure_audit",
        "multicenter_single_frame_dsa_shift_abstention",
        "cross_view_quantitative_dsa_functional_calibration",
        "clinical_biplane_dsa_projection_set_localization",
        "public_phantom_to_clinical_wss_segmentation_transfer",
        "aneurysm_sac_aware_4dflow_functional_segmentation",
        "patient_level_selective_wss_error_certificate",
        "segmentation_induced_hemodynamic_ranking_reversal",
        "resolution_shift_functional_segmentation",
        "tof_pretrained_4dflow_anatomy_transfer",
    }:
        raise ProtocolError("Rejected problem candidates must remain explicit.")
    if set(problem_selection["non_novel_components"]) != {
        "generic_synthetic_to_real_pretraining_or_finetuning",
        "generic_synthetic_data_utility_fidelity_privacy_or_scaling_benchmark",
        "generic_patient_or_institution_leakage_audit",
        "generic_synthetic_shape_artifact_or_counterfactual_effect_audit",
        "vessel_graph_or_gnn",
        "generic_set_prediction_or_point_process",
        "mixed_or_weak_supervision",
        "anatomy_prompt_or_foundation_model",
        "conformal_prediction_or_fdr_control",
        "automatic_segmentation_to_cfd_pipeline",
        "joint_image_mesh_and_cfd_field_prediction",
        "cfd_applicability_score",
        "inverse_navier_stokes_shape_gradient_boundary_segmentation",
        "task_based_quantitative_segmentation_evaluation",
        "adjoint_or_shape_derivative_general_method",
        "soft_vessel_distance_or_vesselness_prior",
        "patient_specific_centerline_graph_or_gnn",
        "parent_artery_classification",
        "generic_hierarchical_or_universal_taxonomy_loss",
        "generic_joint_aneurysm_vessel_multitask_segmentation",
        "generic_implicit_continuous_segmentation",
        "semantic_resampling_or_voxel_spacing_consistency",
        "resolution_invariant_autoencoder",
        "random_finite_set_probabilistic_detection",
        "lesion_detr_variable_cardinality_set_prediction",
        "topology_or_shape_guided_aneurysm_segmentation",
        "supervised_aneurysm_surface_segmentation",
        "forward_healthy_vessel_generation_and_localized_aneurysm_editing",
        "morphology_conditioned_aneurysm_mesh_generation",
        "generic_healthy_counterfactual_anomaly_localization",
        "generic_point_cloud_reconstruction_anomaly_detection",
        "generic_transient_wss_surrogate",
        "graph_transformer_or_graphgps_backbone",
        "ghd_geometry_tokens",
        "steady_flow_pretraining_or_augmentation",
        "pod_fourier_dct_or_sequence_temporal_decoder",
        "generic_cycle_functional_loss_or_direct_functional_head",
        "scalar_or_population_neural_operator_functional_debiasing",
        "generic_e3_equivariant_graph_network",
        "bayesian_parent_vessel_internal_control_growth_detection",
        "persistent_topology_or_bifurcation_false_positive_filter",
        "foundation_3d_surface_feature_transfer",
        "annotator_distribution_calibration",
        "treatment_outcome_ml_from_morphology_api_or_cfd",
        "generic_cross_modal_vessel_anatomy_segmentation",
        "healthy_atlas_cross_dataset_anomaly_detection",
        "staple_or_generic_annotator_aggregation",
        "centerline_guided_periodic_neck_spline",
        "generic_phantom_ai_quality_monitoring",
        "pointnext_geometry_pinn_hemodynamics_clinical_fusion",
        "pinn_residual_convergence_as_physiological_validation",
        "early_or_late_multimodal_rupture_status_fusion",
        "curvature_to_hemodynamic_field_proxy",
        "cross_source_cfd_rupture_status_fusion",
        "multiple_aneurysm_culprit_set_ranking_from_morphology_or_wall_enhancement",
        "generic_pre_post_treatment_remnant_segmentation",
        "wall_enhancement_wss_spatial_correlation",
        "tornadic_wss_topology_taxonomy_or_detector",
        "generic_noise_or_resolution_robust_wss_topological_skeleton",
        "differentiable_projection_adversarial_or_diffusion_working_view_prediction",
        "differential_diagnosis_aware_nnunet_or_open_set_calibration",
        "rheology_or_wall_slip_condition_tokens_and_parameter_sweeps",
        "parent_vessel_context_or_nested_crop_consistency",
        "aneurysm_size_ratio_or_parent_vessel_morphology",
        "semantic_vessel_graph_or_point_cloud_rupture_classification",
        "generic_latent_shape_reconstruction_synthesis_or_calibration",
        "paired_black_blood_to_4d_flow_regression",
        "morphology_aware_segmentation_metric_or_bias_analysis",
        "generic_patient_source_or_lineage_disjoint_split",
        "generic_near_duplicate_shape_hash_or_embedding",
        "generic_source_aware_calibration_abstention_or_domain_adaptation",
        "regularized_or_deep_four_d_medical_image_registration",
        "generic_equivariant_cycle_or_semigroup_registration",
        "generic_registration_uncertainty_or_selective_prediction",
        "generic_image_or_mesh_to_fe_strain_stress_surface_surrogate",
        "generic_functional_surrogate_prediction_set_or_neural_operator_uq",
        "generic_phase_masking_active_acquisition_or_task_fidelity_loss",
        "flow_diverter_outcome_ml_from_morphology_virtual_stenting_or_cfd",
        "time_to_occlusion_statistical_modeling",
        "propensity_score_device_comparison",
        "generic_interval_censored_survival_or_competing_risk_model",
        "generic_multitask_benefit_harm_or_decision_curve_analysis",
        "generic_patient_history_transformer",
        "compressed_sensing_mri_reconstruction_or_paired_consistency",
        "generic_fluid_structure_neural_operator",
        "generic_multifidelity_rigid_to_fsi_residual_learning",
        "multi_granularity_conformal_field_calibration_or_selective_simulation_referral",
        "generic_irregular_longitudinal_medical_image_forecasting",
        "informative_observation_intensity_modeling_or_inverse_intensity_weighting",
        "generic_temporal_transformer_or_latent_diffusion",
        "observational_ctp_dci_classification",
        "generic_cross_modality_consistency",
        "tabular_vwe_hemodynamic_association_model",
        "anatomy_compartment_false_positive_filter",
        "directional_sect_topological_bifurcation_filter",
        "imaging_to_spatial_transcriptomic_alignment_without_paired_coordinates",
        "preclinical_unetplusplus_tissue_ingrowth_segmentation",
        "generic_synthetic_tabular_privacy_utility_generation",
        "mask_to_box_or_scale_consistency_weak_medical_segmentation",
        "vesselness_prior_multitask_weak_aneurysm_segmentation",
        "sparse_backprojection_pose_adaptation_and_vascular_graph_reconstruction",
        "software_threshold_or_inter_user_morphometry_variability_audit",
        "biplane_silhouette_curve_morphing_reconstruction",
        "phantom_dose_reconstruction_ai_consistency",
        "generic_outer_containment_as_dense_pseudo_mask",
        "generic_morphological_conformal_segmentation_set",
        "generic_downstream_segmentation_metric_conformal_interval",
        "generic_three_d_lesion_fnr_conformal_threshold",
        "generic_knn_barycentric_or_conservative_surface_field_remapping",
        "generic_surface_vector_tangent_projection_or_parallel_transport",
        "generic_train_only_normalization_and_test_blind_checkpoint_selection",
        "cross_view_prompting_or_consistency_loss",
        "biplanar_detection_correspondence_triangulation_and_abstention",
        "generic_multioutput_conformal_2d_or_3d_localization_region",
        "task_driven_conformal_uncertainty_for_imaging_inverse_problems",
        "projective_geometry_aware_biplanar_feature_fusion",
        "intracranial_4dflow_segmentation_to_wss_bias_evaluation",
        "tof_to_4dflow_transfer_learning",
        "generic_resolution_shift_functional_segmentation",
        "generic_downstream_wss_metric_conformal_interval",
        "joint_4dflow_segmentation_and_physics_consistency",
    }:
        raise ProtocolError("Direct prior-art boundaries must remain explicit.")

    inverse_audit = problem_selection[
        "inverse_healthy_vessel_counterfactual_source_audit"
    ]
    _require_keys(
        inverse_audit,
        [
            "status",
            "audit_document",
            "candidate_hypothesis",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "aneumo_current_release_geometries",
            "aneumo_current_base_families",
            "aneumo_current_mapping_unit",
            "aneumo_released_healthy_counterpart_manifest_available",
            "aneumo_released_ostium_or_edit_parameter_manifest_available",
            "aneumo_existing_64_case_cache_is_healthy_pathological_paired",
            "intra_whole_vessel_models_source_reported",
            "intra_local_segments_source_reported",
            "intra_expert_annotated_local_aneurysm_segments_source_reported",
            "intra_payload_accessed",
            "intra_explicit_repository_license_verified",
            "real_healthy_counterfactual_ground_truth_available",
            "direct_prior_threats",
            "method_selected",
            "architecture_selected",
            "executable_p0_registered",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "decision",
        ],
        "problem_selection.inverse_healthy_vessel_counterfactual_source_audit",
    )
    if (
        inverse_audit["status"]
        != "completed_source_only_rejected_below_admission_threshold"
        or inverse_audit["audit_document"]
        != "docs/inverse-aneurysm-editing-audit-2026-08-09.md"
        or inverse_audit["score"] != 27.0
        or inverse_audit["maximum_score"] != 40.0
        or inverse_audit["automatic_selection_threshold"] != 32.0
        or inverse_audit["active_shortlist_count"] != 0
        or inverse_audit["aneumo_current_release_geometries"] != 10660
        or inverse_audit["aneumo_current_base_families"] != 427
        or inverse_audit["aneumo_current_mapping_unit"]
        != "base_family_deformation_not_observed_healthy_pathological_pair"
        or inverse_audit["aneumo_released_healthy_counterpart_manifest_available"]
        is not False
        or inverse_audit["aneumo_released_ostium_or_edit_parameter_manifest_available"]
        is not False
        or inverse_audit["aneumo_existing_64_case_cache_is_healthy_pathological_paired"]
        is not False
        or inverse_audit["intra_whole_vessel_models_source_reported"] != 103
        or inverse_audit["intra_local_segments_source_reported"] != 1909
        or inverse_audit[
            "intra_expert_annotated_local_aneurysm_segments_source_reported"
        ]
        != 116
        or inverse_audit["intra_payload_accessed"] is not False
        or inverse_audit["intra_explicit_repository_license_verified"] is not False
        or inverse_audit["real_healthy_counterfactual_ground_truth_available"]
        is not False
        or set(inverse_audit["direct_prior_threats"])
        != {
            "supervised_aneurysm_surface_segmentation",
            "healthy_vessel_generation_and_localized_aneurysm_editing",
            "morphology_conditioned_aneurysm_mesh_generation",
            "synthetic_vasculature_augmentation_for_aneurysm_detection",
            "medical_healthy_counterfactual_anomaly_localization",
            "point_cloud_normal_reconstruction_and_anomaly_localization",
        }
        or inverse_audit["method_selected"] is not False
        or inverse_audit["architecture_selected"] is not False
        or inverse_audit["executable_p0_registered"] is not False
        or inverse_audit["gpu_training_authorized"] is not False
        or inverse_audit["outer_test_authorized"] is not False
        or inverse_audit["submission_identity_active"] is not False
        or inverse_audit["decision"]
        != "reject_without_pseudo_healthy_repair_method_or_gpu"
    ):
        raise ProtocolError(
            "The inverse-counterfactual source audit must remain rejected without "
            "paired-target assumptions, executable P0, method, or GPU authorization."
        )
    substitution_screen = problem_selection["source_only_dataset_substitution_screen"]
    _require_keys(
        substitution_screen,
        [
            "status",
            "payload_accessed",
            "method_or_gpu_authorized",
            "decision",
            "candidate_ids",
        ],
        "problem_selection.source_only_dataset_substitution_screen",
    )
    if (
        substitution_screen["status"]
        != "completed_primary_source_metadata_only"
        or substitution_screen["payload_accessed"] is not False
        or substitution_screen["method_or_gpu_authorized"] is not False
        or substitution_screen["decision"]
        != "screened_alternatives_did_not_replace_rsna_and_do_not_rescue_the_rejected_rsna_candidate"
        or set(substitution_screen["candidate_ids"])
        != {"cada_2020", "adam_2020", "intra_2020", "topcow_2024"}
    ):
        raise ProtocolError(
            "The source-only dataset substitution screen must preserve its no-payload, "
            "no-method decision and all four audited alternatives."
        )
    topaneu_audit = problem_selection["topaneu_attachment_source_audit"]
    _require_keys(
        topaneu_audit,
        [
            "status",
            "audit_document",
            "candidate_hypothesis",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "topaneu_official_challenge",
            "topaneu_live_training_scans",
            "topaneu_live_unique_patients",
            "topaneu_live_location_classes",
            "topaneu_vessel_mask_provenance",
            "topaneu_user_terms_accepted_verified",
            "topaneu_payload_accessed",
            "ambiguity_reference_distribution_verified",
            "open_cta_discovery_result",
            "open_cta_discovery_result_sha256",
            "open_cta_discovery_scope",
            "open_cta_archive_entries",
            "open_cta_cases",
            "open_cta_lesions",
            "open_cta_multi_lesion_cases",
            "direct_prior_threats",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "decision",
            "next_gate",
        ],
        "problem_selection.topaneu_attachment_source_audit",
    )
    if (
        topaneu_audit["status"]
        != "completed_source_only_conditional_lead_not_admitted"
        or topaneu_audit["audit_document"]
        != "docs/topaneu-attachment-audit-2026-08-09.md"
        or topaneu_audit["candidate_hypothesis"]
        != "patient_specific_vascular_attachment_consistent_lesion_segmentation_and_location_projection"
        or topaneu_audit["score"] != 29.0
        or topaneu_audit["maximum_score"] != 40.0
        or topaneu_audit["automatic_selection_threshold"] != 32.0
        or topaneu_audit["score"] >= topaneu_audit["automatic_selection_threshold"]
        or topaneu_audit["active_shortlist_count"] != 0
        or topaneu_audit["topaneu_official_challenge"] != "miccai_2026"
        or topaneu_audit["topaneu_live_training_scans"] != 417
        or topaneu_audit["topaneu_live_unique_patients"] != 409
        or topaneu_audit["topaneu_live_location_classes"] != 52
        or topaneu_audit["topaneu_vessel_mask_provenance"]
        != "organizer_model_prediction_silver_not_ground_truth"
        or topaneu_audit["topaneu_user_terms_accepted_verified"] is not False
        or topaneu_audit["topaneu_payload_accessed"] is not False
        or topaneu_audit["ambiguity_reference_distribution_verified"] is not False
        or topaneu_audit["open_cta_discovery_result"]
        != "results/open_multicenter_cta_metadata_discovery_20260809.json"
        or topaneu_audit["open_cta_discovery_result_sha256"]
        != "8ed7fa00f10bc81e3db5cfed1b26fa8f5c910ab7edc78b1384f3c8e6bcabb3ed"
        or topaneu_audit["open_cta_discovery_scope"]
        != "zip64_central_directory_and_metadata_csv_member_only_no_dicom_header_pixel_or_stl_payload"
        or topaneu_audit["open_cta_archive_entries"] != 149452
        or topaneu_audit["open_cta_cases"] != 172
        or topaneu_audit["open_cta_lesions"] != 122
        or topaneu_audit["open_cta_multi_lesion_cases"] != 24
        or set(topaneu_audit["direct_prior_threats"])
        != {
            "soft_vessel_distance_or_vesselness_prior",
            "patient_specific_centerline_graph_or_gnn",
            "parent_artery_classification",
            "generic_hierarchical_or_universal_taxonomy_loss",
            "generic_joint_aneurysm_vessel_multitask_segmentation",
        }
        or topaneu_audit["method_selected"] is not False
        or topaneu_audit["architecture_selected"] is not False
        or topaneu_audit["gpu_training_authorized"] is not False
        or topaneu_audit["outer_test_authorized"] is not False
        or topaneu_audit["submission_identity_active"] is not False
        or topaneu_audit["decision"]
        != "retain_as_conditional_lead_below_admission_threshold_with_no_active_problem"
        or topaneu_audit["next_gate"]
        != "explicit_user_terms_acceptance_then_prospectively_register_cpu_read_only_p0_asset_and_supervision_semantics_audit_or_continue_other_fresh_problem_audits"
    ):
        raise ProtocolError(
            "The TopAneu attachment audit must remain a below-threshold source-only "
            "conditional lead with no accepted terms, payload, method, GPU, or outer test."
        )
    release_audit = problem_selection["topaneu_release_evaluation_source_audit"]
    _require_keys(
        release_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "conditional_source_lead_count",
            "active_shortlist_count",
            "primary_problem_selected",
            "official_repository_commit",
            "official_release_scans",
            "official_unique_patients",
            "official_centers",
            "reserved_test_center",
            "official_location_classes",
            "official_type_classes",
            "official_share_bytes",
            "image_sha_manifest_paths",
            "location_mask_sha_manifest_paths",
            "type_mask_sha_manifest_paths",
            "vessel_mask_sha_manifest_paths",
            "location_json_paths",
            "terms_sha256",
            "readme_sha256",
            "changelog_sha256",
            "task1_evaluator_sha256",
            "task2_evaluator_sha256",
            "batch1_cases_revised_in_current_release",
            "vessel_mask_provenance",
            "task2_evaluation_unit",
            "official_metrics",
            "official_ranking",
            "runtime_seconds_per_case",
            "runtime_ram_gb",
            "runtime_gpu",
            "terms_state",
            "user_terms_acceptance_verified",
            "medical_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "direct_prior_threats",
            "candidates",
            "p0_registration_condition",
            "p0_pass_authorizes",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.topaneu_release_evaluation_source_audit",
    )
    release_candidates = release_audit["candidates"]
    release_ids = _unique_ids(release_candidates, "id", "TopAneu release candidates")
    expected_release_ids = {
        "topaneu_factorized_leaf_risk_with_train_only_silver_anatomy",
        "topaneu_bilateral_reflection_equivariant_leaf_taxonomy",
        "topaneu_type_location_compositional_auxiliary_segmentation",
        "topaneu_official_mean_rank_aligned_optimization",
        "topaneu_batch_revision_aware_annotation_robustness",
        "topaneu_center4_longitudinal_growth",
    }
    release_scores = {item["id"]: item["score"] for item in release_candidates}
    if (
        release_audit["status"]
        != "completed_source_only_one_conditional_lead_above_admission_pending_user_terms"
        or release_audit["audit_document"]
        != "docs/topaneu-release-evaluation-audit-2026-08-10.md"
        or release_audit["automatic_selection_threshold"] != 32.0
        or release_audit["best_candidate_id"]
        != "topaneu_factorized_leaf_risk_with_train_only_silver_anatomy"
        or release_audit["best_score"] != 33.0
        or release_audit["conditional_source_lead_count"] != 1
        or release_audit["active_shortlist_count"] != 0
        or release_audit["primary_problem_selected"] is not False
        or release_audit["official_repository_commit"]
        != "018c243445f99199f484018c4c80575c84c72293"
        or release_audit["official_release_scans"] != 417
        or release_audit["official_unique_patients"] != 409
        or release_audit["official_centers"] != 4
        or release_audit["reserved_test_center"] != "center_3_umcu"
        or release_audit["official_location_classes"] != 52
        or release_audit["official_type_classes"] != 3
        or release_audit["official_share_bytes"] != 21025241495
        or any(
            release_audit[key] != 417
            for key in (
                "image_sha_manifest_paths",
                "location_mask_sha_manifest_paths",
                "type_mask_sha_manifest_paths",
                "vessel_mask_sha_manifest_paths",
                "location_json_paths",
            )
        )
        or release_audit["terms_sha256"]
        != "aa7d73eefe57adae20fafd23ddafc068341468aec53db33948060a203ba3432e"
        or release_audit["readme_sha256"]
        != "ea7c5cd4898b5abeef9c251ec05e962d769b51e83d35b0678c41aaa5f9273577"
        or release_audit["changelog_sha256"]
        != "5a992240cb6f4089c138d8dd62830204326693d859f159794e681e44f8e7f0b1"
        or release_audit["task1_evaluator_sha256"]
        != "58cda5d310ec2e4588428b73fbadee5bfdd30a40a79ecec8c9a10f2ceefc462e"
        or release_audit["task2_evaluator_sha256"]
        != "5e24667a47f2141344c07666c7d0492bd8e92122a276512f801f1154ba00e09e"
        or release_audit["batch1_cases_revised_in_current_release"] != 52
        or release_audit["vessel_mask_provenance"]
        != "organizer_model_prediction_silver_training_only_not_ground_truth"
        or release_audit["task2_evaluation_unit"]
        != "per_class_binary_volume_not_aneurysm_instance"
        or set(release_audit["official_metrics"])
        != {"precision", "recall", "mcc", "dice", "volumetric_similarity", "normalized_hd95"}
        or release_audit["official_ranking"] != "mean_rank_across_task_metrics"
        or release_audit["runtime_seconds_per_case"] != 420
        or release_audit["runtime_ram_gb"] != 32
        or release_audit["runtime_gpu"] != "nvidia_t4_16gb"
        or release_audit["terms_state"]
        != "downloading_constitutes_agreement_user_acceptance_not_verified"
        or release_audit["user_terms_acceptance_verified"] is not False
        or release_audit["medical_payload_accessed"] is not False
        or release_audit["executable_p0_registered"] is not False
        or release_audit["method_selected"] is not False
        or release_audit["architecture_selected"] is not False
        or release_audit["gpu_training_authorized"] is not False
        or release_audit["outer_test_authorized"] is not False
        or release_audit["submission_identity_active"] is not False
        or release_ids != expected_release_ids
        or release_scores
        != {
            "topaneu_factorized_leaf_risk_with_train_only_silver_anatomy": 33.0,
            "topaneu_bilateral_reflection_equivariant_leaf_taxonomy": 31.5,
            "topaneu_type_location_compositional_auxiliary_segmentation": 31.0,
            "topaneu_official_mean_rank_aligned_optimization": 30.5,
            "topaneu_batch_revision_aware_annotation_robustness": 28.5,
            "topaneu_center4_longitudinal_growth": 20.0,
        }
        or any(sum(item["axis_scores"]) != item["score"] for item in release_candidates)
        or any(item["payload_accessed"] is not False for item in release_candidates)
        or release_audit["p0_registration_condition"]
        != "explicit_user_confirmation_of_topaneu_data_use_terms"
        or release_audit["p0_pass_authorizes"]
        != "register_one_method_free_p1_task_adequacy_audit_only"
        or release_audit["decision"]
        != "retain_one_conditional_source_lead_without_active_shortlist_payload_p0_method_architecture_gpu_outer_test_or_claim"
        or release_audit["next_allowed_action"]
        != "after_explicit_user_terms_acceptance_register_a_fresh_cpu_read_only_p0_release_asset_and_semantics_audit_or_continue_other_fresh_source_audits"
    ):
        raise ProtocolError(
            "The TopAneu material release may retain exactly one 33/40 terms-pending "
            "source lead, but must not open payload, P0, method, GPU, outer test, or claim."
        )
    checks.append("TopAneu material-release conditional source-lead boundary")
    code_red_team = problem_selection["topaneu_code_semantics_red_team"]
    _require_keys(
        code_red_team,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_score",
            "active_shortlist_count",
            "conditional_source_lead_count",
            "primary_problem_selected",
            "historical_schema_6_3_candidate_id",
            "historical_schema_6_3_score",
            "historical_score_relabelled",
            "fresh_same_formulation_score",
            "official_repository_commit",
            "public_checkout_bytes_class",
            "location_mapping_sha256",
            "type_mapping_sha256",
            "vessel_mapping_sha256",
            "task1_evaluator_sha256",
            "task2_evaluator_sha256",
            "task2_readme_sha256",
            "task1_template_main_sha256",
            "task2_template_main_sha256",
            "official_location_leaf_count",
            "official_right_lateralized_leaves",
            "official_left_lateralized_leaves",
            "official_non_lateralized_leaves",
            "official_taxonomy_already_encodes",
            "official_test_interface_inputs",
            "official_test_interface_includes_vessel_mask",
            "task1_preserves_repeated_class_ids_as_counts",
            "task2_active_path_evaluates_per_class_binary_volume",
            "task2_instance_level_code_active",
            "task2_documented_same_class_multiple_aneurysms",
            "user_terms_acceptance_verified",
            "patient_image_or_mask_payload_accessed",
            "patient_location_json_content_accessed",
            "switchdrive_medical_member_accessed",
            "direct_prior_threats",
            "candidates",
            "medical_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.topaneu_code_semantics_red_team",
    )
    red_team_candidates = code_red_team["candidates"]
    red_team_ids = _unique_ids(
        red_team_candidates, "id", "TopAneu code-semantics red-team candidates"
    )
    red_team_scores = {item["id"]: item["score"] for item in red_team_candidates}
    if (
        code_red_team["status"]
        != "completed_public_code_and_primary_prior_red_team_all_rejected"
        or code_red_team["audit_document"]
        != "docs/topaneu-code-semantics-red-team-2026-08-10.md"
        or code_red_team["automatic_selection_threshold"] != 32.0
        or code_red_team["best_score"] != 31.5
        or code_red_team["active_shortlist_count"] != 0
        or code_red_team["conditional_source_lead_count"] != 0
        or code_red_team["primary_problem_selected"] is not False
        or code_red_team["historical_schema_6_3_candidate_id"]
        != "topaneu_factorized_leaf_risk_with_train_only_silver_anatomy"
        or code_red_team["historical_schema_6_3_score"] != 33.0
        or code_red_team["historical_score_relabelled"] is not False
        or code_red_team["fresh_same_formulation_score"] != 31.0
        or code_red_team["official_repository_commit"]
        != "018c243445f99199f484018c4c80575c84c72293"
        or code_red_team["public_checkout_bytes_class"]
        != "44mb_source_evaluation_simulations_mapping_metadata_and_sha_manifests"
        or code_red_team["location_mapping_sha256"]
        != "815c021012f499bff80b517bab1c7a351f4967ce628c0a8055d98e2ac8bc69fa"
        or code_red_team["type_mapping_sha256"]
        != "2c75d432539028ac4c58f726c89bd216089015575388e51701a30f8b2f4833c6"
        or code_red_team["vessel_mapping_sha256"]
        != "0ecca1d2a962a08c7c0fcdd41ed94af11e0e121be8b31677902396ea52dafe7f"
        or code_red_team["task1_evaluator_sha256"]
        != "58cda5d310ec2e4588428b73fbadee5bfdd30a40a79ecec8c9a10f2ceefc462e"
        or code_red_team["task2_evaluator_sha256"]
        != "5e24667a47f2141344c07666c7d0492bd8e92122a276512f801f1154ba00e09e"
        or code_red_team["task2_readme_sha256"]
        != "10ee0d290be010cc70c69b175621bd9db6ec2a0dbbabceb6ff3b55ba80bd2fa9"
        or code_red_team["task1_template_main_sha256"]
        != "5f87a02222cc2d0cb9903f012a7b77252407707e5fb3ebdadca8fa8cbee7f6d1"
        or code_red_team["task2_template_main_sha256"]
        != "7b431588eebff8e154dab9ca286c5fa07a775b29e48b134ad6ec11d2afdb26dd"
        or code_red_team["official_location_leaf_count"] != 52
        or code_red_team["official_right_lateralized_leaves"] != 24
        or code_red_team["official_left_lateralized_leaves"] != 24
        or code_red_team["official_non_lateralized_leaves"] != 4
        or set(code_red_team["official_taxonomy_already_encodes"])
        != {
            "territory_numeric_prefix",
            "laterality",
            "trunk_junction_terminus_or_distal_branch_role",
        }
        or set(code_red_team["official_test_interface_inputs"])
        != {"head_ct_angiography", "head_mr_angiography"}
        or code_red_team["official_test_interface_includes_vessel_mask"] is not False
        or code_red_team["task1_preserves_repeated_class_ids_as_counts"] is not True
        or code_red_team["task2_active_path_evaluates_per_class_binary_volume"]
        is not True
        or code_red_team["task2_instance_level_code_active"] is not False
        or code_red_team["task2_documented_same_class_multiple_aneurysms"]
        != "very_unlikely"
        or code_red_team["user_terms_acceptance_verified"] is not False
        or code_red_team["patient_image_or_mask_payload_accessed"] is not False
        or code_red_team["patient_location_json_content_accessed"] is not False
        or code_red_team["switchdrive_medical_member_accessed"] is not False
        or set(code_red_team["direct_prior_threats"])
        != {
            "midl_2026_scaling_supervision_for_free_training_only_automatic_anatomy_supervision",
            "midl_2022_segmentation_consistent_probabilistic_lesion_counting",
            "ml4h_2021_image_classification_with_consistent_supporting_evidence",
            "miccai_2024_hierarchical_adaptive_taxonomy_segmentation",
            "miccai_2024_vessel_aware_aneurysm_detection_with_distance_maps",
            "deepsetnet_set_cardinality_prediction",
            "generic_joint_lesion_classification_and_segmentation",
            "aran_patient_specific_centerline_gat_and_artery_aware_fusion",
            "generic_lupi_distillation_and_conformal_segmentation",
        }
        or red_team_ids
        != {
            "topaneu_official_metric_instance_collapse_aware_training",
            "topaneu_explicit_hierarchical_52_leaf_taxonomy",
            "topaneu_image_only_source_generalization_with_train_only_silver_anatomy",
            "topaneu_type_location_compositional_auxiliary_segmentation_v2",
            "topaneu_multiset_mask_cardinality_coherence",
            "topaneu_center4_longitudinal_growth_v2",
        }
        or red_team_scores
        != {
            "topaneu_official_metric_instance_collapse_aware_training": 31.5,
            "topaneu_explicit_hierarchical_52_leaf_taxonomy": 31.0,
            "topaneu_image_only_source_generalization_with_train_only_silver_anatomy": 31.0,
            "topaneu_type_location_compositional_auxiliary_segmentation_v2": 30.5,
            "topaneu_multiset_mask_cardinality_coherence": 28.5,
            "topaneu_center4_longitudinal_growth_v2": 20.0,
        }
        or any(sum(item["axis_scores"]) != item["score"] for item in red_team_candidates)
        or any(
            code_red_team[key] is not False
            for key in (
                "medical_payload_accessed",
                "executable_p0_registered",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
            )
        )
        or code_red_team["decision"]
        != "reject_all_fresh_candidates_without_repairing_historical_33_score_or_opening_terms_payload_p0_method_architecture_gpu_outer_test_or_claim"
        or code_red_team["next_allowed_action"]
        != "fresh_problem_level_primary_source_and_direct_prior_audit_only_no_topaneu_p0_from_rejected_formulation"
    ):
        raise ProtocolError(
            "The TopAneu code-semantics red team must preserve the historical 33/40 "
            "record while rejecting every fresh candidate below 32/40 and keeping "
            "terms, medical payload, P0, method, GPU, and outer test closed."
        )
    checks.append("TopAneu code-semantics all-rejected boundary")
    physical_candidate = problem_selection["open_cta_physical_grid_candidate"]
    _require_keys(
        physical_candidate,
        [
            "status",
            "audit_document",
            "config",
            "candidate_hypothesis",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "primary_problem_selected",
            "independent_unit_before_p0",
            "source_cases",
            "source_controls",
            "source_positive_cases",
            "source_lesions",
            "source_multi_lesion_cases",
            "source_miliary_lesions",
            "source_slice_thickness_range_mm",
            "dicom_headers_accessed",
            "dicom_header_access_scope",
            "dicom_pixel_values_decoded",
            "stl_payload_accessed",
            "p0_source_commit",
            "p0_config_sha256",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_process_exit_code",
            "p0_scientific_gate_evaluated",
            "p0_failure_stage",
            "same_contract_rerun_allowed",
            "parser_repair_allowed",
            "direct_prior_threats",
            "residual_gap",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "p0_pass_authorizes",
            "p0_failure_action",
        ],
        "problem_selection.open_cta_physical_grid_candidate",
    )
    if (
        physical_candidate["status"]
        != "closed_after_registered_p0_execution_incomplete_no_scientific_verdict"
        or physical_candidate["audit_document"]
        != "docs/open-cta-physical-grid-audit-2026-08-09.md"
        or physical_candidate["config"] != "configs/open_cta_physical_p0.json"
        or physical_candidate["candidate_hypothesis"]
        != "physical_coordinate_lesion_instance_predictions_should_commute_with_deterministic_resampling_in_cardinality_surface_and_morphometry"
        or physical_candidate["score"] != 32.0
        or physical_candidate["maximum_score"] != 40.0
        or physical_candidate["automatic_selection_threshold"] != 32.0
        or physical_candidate["active_shortlist_count"] != 0
        or physical_candidate["primary_problem_selected"] is not False
        or physical_candidate["independent_unit_before_p0"]
        != "cta_case_patient_key_not_yet_audited"
        or physical_candidate["source_cases"] != 172
        or physical_candidate["source_controls"] != 90
        or physical_candidate["source_positive_cases"] != 82
        or physical_candidate["source_lesions"] != 122
        or physical_candidate["source_multi_lesion_cases"] != 24
        or physical_candidate["source_miliary_lesions"] != 30
        or physical_candidate["source_slice_thickness_range_mm"] != [0.5, 2.0]
        or physical_candidate["dicom_headers_accessed"] is not True
        or physical_candidate["dicom_header_access_scope"]
        != "partial_threaded_selected_compressed_prefixes_exact_count_unknown_after_early_exception"
        or physical_candidate["dicom_pixel_values_decoded"] is not False
        or physical_candidate["stl_payload_accessed"] is not False
        or physical_candidate["p0_source_commit"]
        != "b437875f884346d7f0fada68f089981664ae2a3c"
        or physical_candidate["p0_config_sha256"]
        != "278b95c1e77c0918eb894fd5431cb8d1d8859d693184026827987ef659c3a551"
        or physical_candidate["p0_execution_record"]
        != "results/open_cta_physical_p0_execution_20260809.json"
        or physical_candidate["p0_execution_record_sha256"]
        != "538725c9901039169cc6e747a112630f327411c5594d021edf9b76fd913f950b"
        or physical_candidate["p0_process_exit_code"] != 1
        or physical_candidate["p0_scientific_gate_evaluated"] is not False
        or physical_candidate["p0_failure_stage"]
        != "undefined_length_procedure_code_sequence_before_pixel_data_outside_frozen_minimal_parser"
        or physical_candidate["same_contract_rerun_allowed"] is not False
        or physical_candidate["parser_repair_allowed"] is not False
        or set(physical_candidate["direct_prior_threats"])
        != {
            "consispace_voxel_spacing_resampling",
            "implicit_continuous_medical_segmentation",
            "resolution_invariant_autoencoding",
            "random_finite_set_probabilistic_detection",
            "lesion_detr_variable_cardinality_set_prediction",
            "topology_or_shape_guided_aneurysm_segmentation",
        }
        or physical_candidate["residual_gap"]
        != "one_physical_coordinate_lesion_instance_representation_whose_cardinality_surface_and_morphometry_commute_with_grid_changes"
        or physical_candidate["method_selected"] is not False
        or physical_candidate["architecture_selected"] is not False
        or physical_candidate["gpu_training_authorized"] is not False
        or physical_candidate["outer_test_authorized"] is not False
        or physical_candidate["submission_identity_active"] is not False
        or physical_candidate["p0_pass_authorizes"]
        != "register_method_free_p1_native_grid_rasterization_and_instance_stability_audit_only"
        or physical_candidate["p0_failure_action"]
        != "close_physical_grid_candidate_without_threshold_repair_method_gpu_or_outer_test"
    ):
        raise ProtocolError(
            "The open-CTA physical-grid P0 must remain execution-incomplete, "
            "scientifically unevaluated, closed, and forbidden from parser repair or rerun."
        )
    semantics_audit = problem_selection["rsna_supervision_semantics_red_team"]
    _require_keys(
        semantics_audit,
        [
            "status",
            "audit_document",
            "payload_accessed",
            "anonymous_s3_listing_http_status",
            "official_wiki_status",
            "first_place_repository_commit",
            "second_place_preprint",
            "training_series_reported_by_second_place",
            "provided_vessel_mask_cases_reported_by_second_place",
            "provided_segmentation_semantics",
            "aneurysm_supervision_semantics",
            "second_place_aneurysm_masks",
            "mixed_granularity_lesion_annotation_selection_cohort_supported",
            "method_or_gpu_authorized",
            "decision",
        ],
        "problem_selection.rsna_supervision_semantics_red_team",
    )
    if (
        semantics_audit["status"] != "completed_public_primary_sources_no_payload"
        or semantics_audit["audit_document"]
        != "docs/rsna-supervision-semantics-audit-2026-08-09.md"
        or semantics_audit["payload_accessed"] is not False
        or semantics_audit["anonymous_s3_listing_http_status"] != 403
        or semantics_audit["official_wiki_status"] != "coming_soon"
        or semantics_audit["first_place_repository_commit"]
        != "e1dcdf0058e1e0d0044d8053e92243b4b4794555"
        or semantics_audit["second_place_preprint"] != "arxiv_2606.26706v1"
        or semantics_audit["training_series_reported_by_second_place"] != 4348
        or semantics_audit["provided_vessel_mask_cases_reported_by_second_place"]
        != 178
        or semantics_audit["provided_segmentation_semantics"]
        != "thirteen_class_circle_of_willis_vessel_anatomy_not_aneurysm_extent"
        or semantics_audit["aneurysm_supervision_semantics"]
        != "center_points_for_all_annotated_series_with_presence_and_territory_labels_no_official_voxel_aneurysm_masks"
        or semantics_audit["second_place_aneurysm_masks"]
        != "author_derived_from_points_pseudo_labels_and_manual_correction_not_official_mixed_granularity_annotations"
        or semantics_audit[
            "mixed_granularity_lesion_annotation_selection_cohort_supported"
        ]
        is not False
        or semantics_audit["method_or_gpu_authorized"] is not False
        or semantics_audit["decision"]
        != "reject_annotation_selection_aware_mixed_granularity_lesion_set_candidate"
    ):
        raise ProtocolError(
            "The RSNA supervision-semantics audit must preserve the vessel-mask/"
            "aneurysm-point distinction, no-payload boundary, and candidate rejection."
        )
    goal_audit = problem_selection["goal_oriented_segmentation_cold_audit"]
    _require_keys(
        goal_audit,
        [
            "status",
            "audit_document",
            "direct_prior_narrowing",
            "s0a_config",
            "solver_runtime_preflight_config",
            "solver_runtime_preflight_status",
            "solver_runtime_preflight_execution_record",
            "solver_runtime_preflight_execution_record_sha256",
            "precompiled_su2_omp_release_is_s0a_eligible",
            "solver_runtime_preflight_evaluates_s0a",
            "solver_runtime_preflight_pass_authorizes",
            "cmha_stage_v1_status",
            "cmha_stage_v1_execution_record",
            "cmha_stage_v1_execution_record_sha256",
            "cmha_stage_v2_config",
            "cmha_stage_v2_config_sha256",
            "cmha_stage_v2_status",
            "cmha_stage_v2_execution_record",
            "cmha_stage_v2_execution_record_sha256",
            "cmha_stage_v2_evaluates_s0a",
            "cmha_source_asset_discovery_status",
            "cmha_source_asset_discovery_record",
            "cmha_source_asset_discovery_record_sha256",
            "s0a_asset_component_config",
            "s0a_asset_component_config_sha256",
            "s0a_asset_component_status",
            "s0a_asset_component_source_commit",
            "s0a_asset_component_result",
            "s0a_asset_component_result_sha256",
            "s0a_asset_component_gate",
            "s0a_asset_component_pass_authorizes",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "direct_gap",
            "required_next_gate",
            "s0a_pass_authorizes",
            "s0a_failure_action",
        ],
        "problem_selection.goal_oriented_segmentation_cold_audit",
    )
    direct_prior_narrowing = goal_audit["direct_prior_narrowing"]
    _require_keys(
        direct_prior_narrowing,
        [
            "status",
            "inverse_navier_stokes_joint_segmentation",
            "task_based_quantitative_segmentation",
            "broad_claims_rejected",
            "remaining_gap",
            "method_or_gpu_authorized",
        ],
        "problem_selection.goal_oriented_segmentation_cold_audit.direct_prior_narrowing",
    )
    if (
        direct_prior_narrowing["status"] != "completed_primary_source_red_team"
        or direct_prior_narrowing["inverse_navier_stokes_joint_segmentation"]
        != "doi:10.1017/jfm.2022.503"
        or direct_prior_narrowing["task_based_quantitative_segmentation"]
        != "pmid:38360049"
        or set(direct_prior_narrowing["broad_claims_rejected"])
        != {
            "pde_shape_gradient_connected_to_segmentation",
            "downstream_quantity_evaluation_instead_of_overlap_only",
        }
        or direct_prior_narrowing["remaining_gap"]
        != "cta_multi_functional_signed_adjoint_pullback_with_remainder_control_and_held_out_functional_superiority"
        or direct_prior_narrowing["method_or_gpu_authorized"] is not False
    ):
        raise ProtocolError(
            "The direct-prior red team must reject broad PDE-segmentation and "
            "task-based-evaluation novelty without opening a method or GPU path."
        )
    if (
        goal_audit["status"]
        != "closed_after_completed_asset_component_failed_5_of_9"
        or goal_audit["audit_document"]
        != "docs/goal-oriented-segmentation-audit-2026-08-09.md"
        or goal_audit["s0a_config"]
        != "configs/goal_oriented_segmentation_s0a.json"
        or goal_audit["solver_runtime_preflight_config"]
        != "configs/goal_oriented_segmentation_s0a_solver_preflight.json"
        or goal_audit["solver_runtime_preflight_status"]
        != "execution_incomplete_exit_1_before_runtime_build_or_probe_no_s0a_verdict"
        or goal_audit["solver_runtime_preflight_execution_record"]
        != "results/goal_oriented_s0a_solver_preflight_v1_execution_20260809.json"
        or goal_audit["solver_runtime_preflight_execution_record_sha256"]
        != "704fedb9f3667242c1ce00e8622c2cf41708ff00ff1e8483cd1890cd9e82e0fa"
        or goal_audit["precompiled_su2_omp_release_is_s0a_eligible"] is not False
        or goal_audit["solver_runtime_preflight_evaluates_s0a"] is not False
        or goal_audit["solver_runtime_preflight_pass_authorizes"]
        != "pin_runtime_overlay_and_execute_the_single_preregistered_s0a_gate_only"
        or goal_audit["cmha_stage_v1_status"]
        != "execution_incomplete_exit_28_before_any_verified_archive_no_s0a_verdict"
        or goal_audit["cmha_stage_v1_execution_record"]
        != "results/goal_oriented_s0a_cmha_stage_v1_execution_20260809.json"
        or goal_audit["cmha_stage_v1_execution_record_sha256"]
        != "98a80fda1e832c4898f30c6e3ceaedcce2e28c07971338af50c0802a6e89d6fa"
        or goal_audit["cmha_stage_v2_config"]
        != "configs/goal_oriented_segmentation_s0a_cmha_stage_v2.json"
        or goal_audit["cmha_stage_v2_config_sha256"]
        != "da2c224fc55542f9a76c62dc54dd24db83a93c7213b42173af229bc0f097fcc6"
        or goal_audit["cmha_stage_v2_status"]
        != "execution_incomplete_exit_28_before_first_verified_chunk_no_s0a_verdict"
        or goal_audit["cmha_stage_v2_execution_record"]
        != "results/goal_oriented_s0a_cmha_stage_v2_execution_20260809.json"
        or goal_audit["cmha_stage_v2_execution_record_sha256"]
        != "c284b5cf20b6e8e9ce509c2047337395c294939ad7830f1daf0af2992082223f"
        or goal_audit["cmha_stage_v2_evaluates_s0a"] is not False
        or goal_audit["cmha_source_asset_discovery_status"]
        != "three_of_three_official_archive_size_and_md5_match_not_s0a"
        or goal_audit["cmha_source_asset_discovery_record"]
        != "results/goal_oriented_s0a_cmha_source_asset_discovery_20260809.json"
        or goal_audit["cmha_source_asset_discovery_record_sha256"]
        != "0bdc8e5c901318ab3c46ec3f877a8f9d2c5a999279f717d3cdb5ced13fdf19b5"
        or goal_audit["s0a_asset_component_config"]
        != "configs/goal_oriented_segmentation_s0a_asset_component.json"
        or goal_audit["s0a_asset_component_config_sha256"]
        != "f951d68b42e2590fe57d0739f2b16a72893347c1feadc9ddab631f40ffa633e7"
        or goal_audit["s0a_asset_component_status"]
        != "completed_failed_5_of_9_exact_lesion_linkage_precondition_failed"
        or goal_audit["s0a_asset_component_source_commit"]
        != "ef547a4ccb71fa45b4a43e67c0939e2701ebfc11"
        or goal_audit["s0a_asset_component_result"]
        != "results/goal_oriented_s0a_asset_component_20260809.json"
        or goal_audit["s0a_asset_component_result_sha256"]
        != "c220cb8d92909a5a401b29ad5b75d54f4881d9db4a32ea6f33dd6007e424ad6e"
        or goal_audit["s0a_asset_component_gate"]
        != "5_of_9_failed_asset_component_s0a_not_evaluated"
        or goal_audit["s0a_asset_component_pass_authorizes"]
        != "register_one_distinct_prospective_no_runtime_network_solver_preflight_v2_only"
        or goal_audit["score"] != 27.0
        or goal_audit["maximum_score"] != 40.0
        or goal_audit["automatic_selection_threshold"] != 32.0
        or goal_audit["method_selected"] is not False
        or goal_audit["architecture_selected"] is not False
        or goal_audit["gpu_training_authorized"] is not False
        or goal_audit["outer_test_authorized"] is not False
        or goal_audit["submission_identity_active"] is not False
        or goal_audit["direct_gap"]
        != "cta_multi_functional_signed_adjoint_pullback_with_remainder_control_and_held_out_functional_superiority"
        or goal_audit["required_next_gate"]
        != "none_candidate_closed_at_asset_component"
        or goal_audit["s0a_pass_authorizes"]
        != "register_method_free_s0b_functional_non_equivalence_and_linearization_audit_only"
        or goal_audit["s0a_failure_action"]
        != "executed_close_candidate_without_solver_v2_model_gpu_or_outer_test"
    ):
        raise ProtocolError(
            "The goal-oriented candidate must remain closed after its 5/9 asset failure, "
            "without solver v2, method, GPU, or outer-test authority."
        )
    orbit_audit = problem_selection["aneux_preprocessing_orbit_candidate"]
    _require_keys(
        orbit_audit,
        [
            "status",
            "audit_document",
            "config",
            "config_sha256",
            "candidate_hypothesis",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "primary_problem_selected",
            "tabular_archive_bytes",
            "tabular_archive_md5",
            "model_archive_bytes",
            "model_archive_md5",
            "source_lesions",
            "source_patients",
            "patient_id_observed_rows",
            "mesh_resolutions",
            "cut_configurations",
            "morphometric_features",
            "tabular_payload_accessed",
            "completed_tabular_archive_retained",
            "partial_tabular_file_retained",
            "transient_transport_bytes_received",
            "model_central_directory_accessed",
            "model_member_payload_accessed",
            "task_unit_audited",
            "direct_prior_threats",
            "transport_attempts_inside_one_exact_job",
            "transport_attempt_scope",
            "same_source_job_resubmission_allowed",
            "full_model_archive_download_allowed",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "p0_pass_authorizes",
            "p0_failure_action",
            "p0_source_commit",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_scheduler_job_id",
            "p0_scheduler_exit_status",
            "p0_scheduler_walltime",
            "p0_scheduler_cput",
            "p0_scheduler_peak_memory",
            "p0_run_count",
            "p0_result_created",
            "p0_result_sha256",
            "p0_status_sha256",
            "p0_raw_log_materialized",
            "p0_error_code",
            "p0_scientific_gate_evaluated",
            "p0_checks_passed",
            "p0_checks_total",
            "p1_authorized",
            "transport_or_reader_repair_allowed",
            "next_allowed_action",
        ],
        "problem_selection.aneux_preprocessing_orbit_candidate",
    )
    expected_orbit_priors = {
        "diffusionnet_discretization_agnostic_surface_learning",
        "match_segmentation_and_reconstruction_geometry_uncertainty",
        "aneux_original_morphometry_and_cut_robustness",
        "aneux_pointnet_status_classification",
        "aneurysm_latent_shape_space_across_three_resolutions",
        "generic_consistency_regularization",
        "generic_rotation_or_e3_equivariant_mesh_learning",
    }
    if (
        orbit_audit["status"]
        != "closed_after_registered_p0_execution_incomplete_no_scientific_verdict"
        or orbit_audit["audit_document"]
        != "docs/aneux-preprocessing-orbit-audit-2026-08-09.md"
        or orbit_audit["config"] != "configs/aneux_preprocessing_orbit_p0.json"
        or orbit_audit["config_sha256"]
        != "26393855aec6dbd8af53477e54e8079587af2458fbaf91b5d0fc959c77adc978"
        or orbit_audit["score"] != 34.0
        or orbit_audit["maximum_score"] != 40.0
        or orbit_audit["automatic_selection_threshold"] != 32.0
        or orbit_audit["active_shortlist_count"] != 0
        or orbit_audit["primary_problem_selected"] is not False
        or orbit_audit["tabular_archive_bytes"] != 12992074
        or orbit_audit["tabular_archive_md5"]
        != "a00dde7b974de724c6480dbda4585a8c"
        or orbit_audit["model_archive_bytes"] != 6277720483
        or orbit_audit["model_archive_md5"]
        != "6248323006f67858b1eb1ec77ce8c0a6"
        or orbit_audit["source_lesions"] != 750
        or orbit_audit["source_patients"] != 605
        or orbit_audit["patient_id_observed_rows"] != 637
        or orbit_audit["mesh_resolutions"] != 3
        or orbit_audit["cut_configurations"] != 4
        or orbit_audit["morphometric_features"] != 170
        or orbit_audit["tabular_payload_accessed"] is not False
        or orbit_audit["completed_tabular_archive_retained"] is not False
        or orbit_audit["partial_tabular_file_retained"] is not False
        or orbit_audit["transient_transport_bytes_received"] is not None
        or orbit_audit["model_central_directory_accessed"] is not False
        or orbit_audit["model_member_payload_accessed"] is not False
        or orbit_audit["task_unit_audited"] is not False
        or set(orbit_audit["direct_prior_threats"]) != expected_orbit_priors
        or orbit_audit["transport_attempts_inside_one_exact_job"] != 3
        or orbit_audit["transport_attempt_scope"]
        != "maximum_three_per_http_operation_within_single_exact_job"
        or orbit_audit["same_source_job_resubmission_allowed"] is not False
        or orbit_audit["full_model_archive_download_allowed"] is not False
        or orbit_audit["method_selected"] is not False
        or orbit_audit["architecture_selected"] is not False
        or orbit_audit["gpu_training_authorized"] is not False
        or orbit_audit["outer_test_authorized"] is not False
        or orbit_audit["submission_identity_active"] is not False
        or orbit_audit["p0_pass_authorizes"]
        != "register_one_method_free_p1_casewise_preprocessing_orbit_task_adequacy_audit_only"
        or orbit_audit["p0_failure_action"]
        != "close_this_candidate_version_without_model_architecture_gpu_outer_test_or_scientific_claim"
        or orbit_audit["p0_source_commit"]
        != "42cc3c7127f382b440f2ac22f662c45692f37863"
        or orbit_audit["p0_execution_record"]
        != "results/aneux_preprocessing_orbit_p0_execution_20260809.json"
        or orbit_audit["p0_execution_record_sha256"]
        != "ba547b9855229d59fd2ca79293e870828d878ad0b818ca4bb904eb29defde05a"
        or orbit_audit["p0_scheduler_job_id"] != "115177.ECE-util1"
        or orbit_audit["p0_scheduler_exit_status"] != 2
        or orbit_audit["p0_scheduler_walltime"] != "00:37:00"
        or orbit_audit["p0_scheduler_cput"] != "00:00:00"
        or orbit_audit["p0_scheduler_peak_memory"] != "26596kb"
        or orbit_audit["p0_run_count"] != 1
        or orbit_audit["p0_result_created"] is not True
        or orbit_audit["p0_result_sha256"]
        != "f57ef0747806679d4de233d26330420de3bb3d29516a433d1125931ffaa333a0"
        or orbit_audit["p0_status_sha256"]
        != "b278d9f759f06976d4f1616a2e6fcd406c5b109ba3e7e4d4c4955c6f82a5d184"
        or orbit_audit["p0_raw_log_materialized"] is not False
        or orbit_audit["p0_error_code"] != "transport_attempts_exhausted"
        or orbit_audit["p0_scientific_gate_evaluated"] is not False
        or orbit_audit["p0_checks_passed"] is not None
        or orbit_audit["p0_checks_total"] != 13
        or orbit_audit["p1_authorized"] is not False
        or orbit_audit["transport_or_reader_repair_allowed"] is not False
        or orbit_audit["next_allowed_action"]
        != "fresh_problem_level_primary_source_and_asset_audit_only"
    ):
        raise ProtocolError(
            "The AneuX preprocessing-orbit candidate must remain closed after its "
            "one-shot P0, without P1, repair, method, GPU, or outer test."
        )
    checks.append("AneuX preprocessing-orbit closed P0 boundary")

    cycle_audit = problem_selection["aneug_cycle_functional_source_audit"]
    _require_keys(
        cycle_audit,
        [
            "status",
            "audit_document",
            "config",
            "candidate_hypothesis",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "primary_problem_selected",
            "dataset_repository_commit",
            "official_code_commit",
            "steady_processed_bytes",
            "steady_processed_sha256",
            "transient_processed_bytes",
            "transient_processed_sha256",
            "dataset_page_transient_cases",
            "rhsia_paper_transient_cases",
            "case_count_discrepancy_resolved",
            "processed_payload_accessed",
            "physical_wss_recovery_audited",
            "task_unit_audited",
            "direct_prior_threats",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "p0_pass_authorizes",
            "p0_failure_action",
            "p0_source_commit",
            "p0_config_sha256",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_scheduler_job_id",
            "p0_scheduler_exit_status",
            "p0_scheduler_walltime",
            "p0_result_created",
            "p0_raw_log_materialized",
            "p0_scientific_gate_evaluated",
            "same_contract_rerun_allowed",
            "dependency_or_reader_repair_allowed",
        ],
        "problem_selection.aneug_cycle_functional_source_audit",
    )
    if (
        cycle_audit["status"]
        != "closed_after_registered_p0_execution_incomplete_no_scientific_verdict"
        or cycle_audit["audit_document"]
        != "docs/cycle-functional-wss-audit-2026-08-09.md"
        or cycle_audit["config"] != "configs/aneug_cycle_functional_p0.json"
        or cycle_audit["score"] != 33.0
        or cycle_audit["maximum_score"] != 40.0
        or cycle_audit["automatic_selection_threshold"] != 32.0
        or cycle_audit["active_shortlist_count"] != 0
        or cycle_audit["primary_problem_selected"] is not False
        or cycle_audit["dataset_repository_commit"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or cycle_audit["official_code_commit"]
        != "4a090a0f12538deef6fcea88b81afe78ce38152e"
        or cycle_audit["steady_processed_bytes"] != 9632510050
        or cycle_audit["steady_processed_sha256"]
        != "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f"
        or cycle_audit["transient_processed_bytes"] != 23744862051
        or cycle_audit["transient_processed_sha256"]
        != "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9"
        or cycle_audit["dataset_page_transient_cases"] != 730
        or cycle_audit["rhsia_paper_transient_cases"] != 808
        or cycle_audit["case_count_discrepancy_resolved"] is not False
        or cycle_audit["processed_payload_accessed"] is not False
        or cycle_audit["physical_wss_recovery_audited"] is not False
        or cycle_audit["task_unit_audited"] is not False
        or cycle_audit["p0_source_commit"]
        != "754ed746fb60aef707f639189ad59e84a0fca556"
        or cycle_audit["p0_config_sha256"]
        != "37e73d6b6e7f2ff73065aeb7e9a33834e729bb1a312955238c9b355eefbb8996"
        or cycle_audit["p0_execution_record"]
        != "results/aneug_cycle_functional_p0_execution_20260809.json"
        or cycle_audit["p0_execution_record_sha256"]
        != "cf2eab0a118688698183004928d7fc1786f694c1435fe7f4316502817e6290ae"
        or cycle_audit["p0_scheduler_job_id"] != "115168.ECE-util1"
        or cycle_audit["p0_scheduler_exit_status"] != 28
        or cycle_audit["p0_scheduler_walltime"] != "00:05:16"
        or cycle_audit["p0_result_created"] is not False
        or cycle_audit["p0_raw_log_materialized"] is not False
        or cycle_audit["p0_scientific_gate_evaluated"] is not False
        or cycle_audit["same_contract_rerun_allowed"] is not False
        or cycle_audit["dependency_or_reader_repair_allowed"] is not False
        or set(cycle_audit["direct_prior_threats"])
        != {
            "rhsia_transient_wss_graph_transformer_with_ghd_and_steady_augmentation",
            "generic_cycle_functional_loss_or_direct_functional_head",
            "pod_fourier_dct_or_sequence_temporal_decoder",
            "goal_oriented_neural_operator_correction",
            "scalar_or_population_neural_operator_functional_debiasing",
            "generic_e3_equivariant_graph_network",
        }
        or cycle_audit["method_selected"] is not False
        or cycle_audit["architecture_selected"] is not False
        or cycle_audit["gpu_training_authorized"] is not False
        or cycle_audit["outer_test_authorized"] is not False
        or cycle_audit["submission_identity_active"] is not False
        or cycle_audit["p0_pass_authorizes"]
        != "register_method_free_p1_cycle_functional_task_adequacy_perturbation_audit_only"
        or cycle_audit["p0_failure_action"]
        != "executed_close_cycle_functional_candidate_without_dependency_or_reader_repair_same_contract_rerun_p1_method_gpu_or_outer_test"
    ):
        raise ProtocolError(
            "The cycle-functional candidate must remain closed after its exact P0 "
            "execution-incomplete outcome, with no payload, P1, model, or GPU authority."
        )
    checks.append("historical cycle-functional P0 failure preserved")

    cycle_reentry = problem_selection["aneug_cycle_transport_reentry_v2a"]
    _require_keys(
        cycle_reentry,
        [
            "status",
            "audit_document",
            "config",
            "historical_v1_status",
            "historical_v1_same_contract_rerun_allowed",
            "historical_v1_failure_relabelled",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "primary_problem_selected",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "single_failure_hypothesis",
            "only_changed_layer",
            "repair_round_index",
            "maximum_transport_repair_rounds",
            "dataset_repository_commit",
            "dataset_license",
            "official_code_commit",
            "head_operations",
            "range_operations",
            "range_bytes_per_operation",
            "maximum_total_payload_bytes",
            "retry_count",
            "local_discovery_range_bytes_read",
            "full_object_downloaded",
            "torch_or_pickle_reader_accessed",
            "case_identifier_accessed",
            "scientific_p0_evaluated",
            "pass_authorizes",
            "failure_action",
            "execution_server",
            "scheduler",
            "resources",
            "pbs_job_submitted",
            "p0_source_commit",
            "p0_config_sha256",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "p0_scheduler_job_id",
            "p0_scheduler_last_observed_state",
            "p0_scheduler_exit_status",
            "p0_scheduler_walltime",
            "p0_scheduler_cput",
            "p0_scheduler_memory",
            "p0_result_created",
            "p0_raw_log_materialized",
            "p0_status_artifact_sha256",
            "transport_gate_evaluated",
            "transport_gate_passed",
            "transport_operations_completed",
            "low_level_failure_cause",
            "repair_rounds_used",
            "second_transport_repair_round_allowed",
            "p0_v2b_authorized",
            "scheduler_observation",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_reentry",
        ],
        "problem_selection.aneug_cycle_transport_reentry_v2a",
    )
    if (
        cycle_reentry["status"]
        != "closed_after_introai9_execution_incomplete_no_transport_or_scientific_verdict"
        or cycle_reentry["audit_document"]
        != "docs/aneug-cycle-transport-reentry-2026-08-10.md"
        or cycle_reentry["config"] != "configs/aneug_cycle_transport_p0_v2a.json"
        or cycle_reentry["historical_v1_status"]
        != "closed_after_registered_p0_execution_incomplete_no_scientific_verdict"
        or cycle_reentry["historical_v1_same_contract_rerun_allowed"] is not False
        or cycle_reentry["historical_v1_failure_relabelled"] is not False
        or cycle_reentry["score"] != 33.0
        or cycle_reentry["maximum_score"] != 40.0
        or cycle_reentry["automatic_selection_threshold"] != 32.0
        or cycle_reentry["active_shortlist_count"] != 0
        or cycle_reentry["primary_problem_selected"] is not False
        or cycle_reentry["method_selected"] is not False
        or cycle_reentry["architecture_selected"] is not False
        or cycle_reentry["gpu_training_authorized"] is not False
        or cycle_reentry["outer_test_authorized"] is not False
        or cycle_reentry["submission_identity_active"] is not False
        or cycle_reentry["single_failure_hypothesis"]
        != "unbounded_whole_object_transport_obscured_source_reachability_before_the_v1_reader_gate"
        or cycle_reentry["only_changed_layer"]
        != "transport_preflight_before_any_full_object_or_reader_access"
        or cycle_reentry["repair_round_index"] != 1
        or cycle_reentry["maximum_transport_repair_rounds"] != 1
        or cycle_reentry["dataset_repository_commit"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or cycle_reentry["dataset_license"] != "cc-by-sa-4.0"
        or cycle_reentry["official_code_commit"]
        != "4a090a0f12538deef6fcea88b81afe78ce38152e"
        or cycle_reentry["head_operations"] != 2
        or cycle_reentry["range_operations"] != 4
        or cycle_reentry["range_bytes_per_operation"] != 1048576
        or cycle_reentry["maximum_total_payload_bytes"] != 4194304
        or cycle_reentry["retry_count"] != 0
        or cycle_reentry["local_discovery_range_bytes_read"] != 4194304
        or cycle_reentry["full_object_downloaded"] is not False
        or cycle_reentry["torch_or_pickle_reader_accessed"] is not False
        or cycle_reentry["case_identifier_accessed"] is not False
        or cycle_reentry["scientific_p0_evaluated"] is not False
        or cycle_reentry["pass_authorizes"]
        != "register_one_separate_aneug_cycle_full_payload_reader_p0_v2b_with_fixed_total_transfer_budget_only"
        or cycle_reentry["failure_action"]
        != "close_v2a_without_second_transport_repair_round_v2b_p1_method_architecture_gpu_or_outer_test"
        or cycle_reentry["execution_server"] != "introai9"
        or cycle_reentry["scheduler"] != "pbs"
        or cycle_reentry["resources"] != "select=1:ncpus=2:mem=4gb:ngpus=0"
        or cycle_reentry["pbs_job_submitted"] is not True
        or cycle_reentry["p0_source_commit"]
        != "690035ae5385328780fbaace9f956ce142a78f33"
        or cycle_reentry["p0_config_sha256"]
        != "814e14f2114d13cae5581184c1696ba50aafff2aa43b364bde5cf338e131e503"
        or cycle_reentry["p0_execution_record"]
        != "results/aneug_cycle_transport_p0_v2a_execution_20260810.json"
        or cycle_reentry["p0_execution_record_sha256"]
        != "85f7c2e7b159d4353972f3ae6f16f3f9a8997eacc61563e8740e8dac26406e63"
        or cycle_reentry["p0_scheduler_job_id"] != "115467.ECE-util1"
        or cycle_reentry["p0_scheduler_last_observed_state"] != "E"
        or cycle_reentry["p0_scheduler_exit_status"] != 1
        or cycle_reentry["p0_scheduler_walltime"] != "00:00:08"
        or cycle_reentry["p0_scheduler_cput"] != "00:00:00"
        or cycle_reentry["p0_scheduler_memory"] != "16824kb"
        or cycle_reentry["p0_result_created"] is not False
        or cycle_reentry["p0_raw_log_materialized"] is not False
        or cycle_reentry["p0_status_artifact_sha256"]
        != "5a3322f2f44ef6300865ac841ead92a240853fa0d7df3209c55bc1c4d935f1ef"
        or cycle_reentry["transport_gate_evaluated"] is not False
        or cycle_reentry["transport_gate_passed"] is not None
        or cycle_reentry["transport_operations_completed"] is not None
        or cycle_reentry["low_level_failure_cause"] != "unresolved"
        or cycle_reentry["repair_rounds_used"] != 1
        or cycle_reentry["second_transport_repair_round_allowed"] is not False
        or cycle_reentry["p0_v2b_authorized"] is not False
        or cycle_reentry["scheduler_observation"]
        != "job_observed_exiting_then_no_longer_returned_by_qstat"
        or cycle_reentry["login_node_gpu_command_executed"] is not False
        or cycle_reentry["junjinyong_accessed_for_this_reentry"] is not False
    ):
        raise ProtocolError(
            "The AneuG-Flow P0-v2a re-entry must remain closed after its single "
            "introai9 CPU/PBS execution-incomplete outcome, with no v1 relabel, "
            "second repair, transport verdict, method, model, GPU, or outer test."
        )
    checks.append("bounded AneuG-Flow P0-v2a transport re-entry")

    dsa_audit = problem_selection["dsa_prefix_risk_source_audit"]
    _require_keys(
        dsa_audit,
        [
            "status",
            "audit_document",
            "candidate_hypothesis",
            "score",
            "maximum_score",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "primary_problem_selected",
            "official_dataset_record",
            "dataset_license",
            "archive_bytes",
            "archive_md5",
            "source_patients",
            "source_sequences",
            "fully_annotated_sequences",
            "released_sequence_length_frames_min",
            "released_sequence_length_frames_max",
            "paper_frame_count_discrepancy",
            "full_sequence_dsc",
            "minimum_projection_dsc",
            "full_minus_minimum_projection_dsc",
            "full_sequence_cldice",
            "minimum_projection_cldice",
            "raw_full_phase_sequence_released",
            "frame_level_arrival_ground_truth_released",
            "prospective_stop_action_or_dose_endpoint_released",
            "dataset_payload_accessed",
            "introai9_staged_asset_found_in_bounded_inventory",
            "direct_prior_threats",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.dsa_prefix_risk_source_audit",
    )
    expected_dsa_priors = {
        "dias_vssnet_full_sequence_segmentation",
        "dsca_spatiotemporal_cerebral_artery_segmentation",
        "temsam_mip_global_prompt_and_complementary_frame_selection",
        "incomplete_angiogram_time_density_curve_recovery",
        "generic_risk_controlled_early_exit",
        "conditional_conformal_segmentation_risk_control",
        "dynamic_dsa_vessel_probability_reconstruction",
    }
    if (
        dsa_audit["status"]
        != "completed_source_rejected_below_admission_threshold"
        or dsa_audit["audit_document"]
        != "docs/dsa-prefix-risk-audit-2026-08-09.md"
        or dsa_audit["score"] != 31.0
        or dsa_audit["maximum_score"] != 40.0
        or dsa_audit["automatic_selection_threshold"] != 32.0
        or dsa_audit["active_shortlist_count"] != 0
        or dsa_audit["primary_problem_selected"] is not False
        or dsa_audit["official_dataset_record"] != "zenodo_11637181_version_3"
        or dsa_audit["dataset_license"] != "cc_by_4_0"
        or dsa_audit["archive_bytes"] != 292444663
        or dsa_audit["archive_md5"] != "780f32df6fb2a5de5d476f385cf2e83b"
        or dsa_audit["source_patients"] != 60
        or dsa_audit["source_sequences"] != 120
        or dsa_audit["fully_annotated_sequences"] != 60
        or dsa_audit["released_sequence_length_frames_min"] != 4
        or dsa_audit["released_sequence_length_frames_max"] != 14
        or dsa_audit["full_sequence_dsc"] != 0.7822
        or dsa_audit["minimum_projection_dsc"] != 0.7802
        or dsa_audit["full_minus_minimum_projection_dsc"] != 0.002
        or dsa_audit["full_sequence_cldice"] != 0.7119
        or dsa_audit["minimum_projection_cldice"] != 0.704
        or dsa_audit["raw_full_phase_sequence_released"] is not False
        or dsa_audit["frame_level_arrival_ground_truth_released"] is not False
        or dsa_audit["prospective_stop_action_or_dose_endpoint_released"] is not False
        or dsa_audit["dataset_payload_accessed"] is not False
        or dsa_audit["introai9_staged_asset_found_in_bounded_inventory"] is not False
        or set(dsa_audit["direct_prior_threats"]) != expected_dsa_priors
        or dsa_audit["executable_p0_registered"] is not False
        or dsa_audit["method_selected"] is not False
        or dsa_audit["architecture_selected"] is not False
        or dsa_audit["gpu_training_authorized"] is not False
        or dsa_audit["outer_test_authorized"] is not False
        or dsa_audit["submission_identity_active"] is not False
        or dsa_audit["decision"] != "reject_without_score_repair_p0_model_or_gpu"
        or dsa_audit["next_allowed_action"]
        != "fresh_problem_level_primary_source_and_task_unit_audit_only"
    ):
        raise ProtocolError(
            "The DSA prefix-risk candidate must remain source-rejected at 31/40, "
            "without payload, P0, method, architecture, GPU, or outer-test authority."
        )
    checks.append("DSA prefix-risk source rejection and no-training boundary")

    source_delta = problem_selection["source_delta_audit"]
    _require_keys(
        source_delta,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "new_candidate_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "introai9_connection_verified",
            "introai9_pbs_jobs_observed",
            "introai9_login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "intra_staged_payload_found",
            "intra_staged_material_scope",
            "rsna_access_state",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.source_delta_audit",
    )
    expected_source_delta_scores = {
        "openneuro_longitudinal_surface_growth_detection_direct_prior_and_unit_limited": 31.5,
        "rsna_anatomy_indexed_point_set_detection_terms_gated_and_direct_prior_dense": 30.5,
        "victoria_neck_curve_distribution_effective_geometry_n5": 30.5,
        "intra_topology_false_positive_detection_payload_absent_and_direct_prior": 28.5,
        "iaia_joint_aneurysm_stenosis_proposal_only": 26.0,
        "flow_diverter_dsa_outcome_imaging_endpoint_not_linked": 25.5,
    }
    observed_source_delta_scores = {
        candidate["id"]: candidate["score"]
        for candidate in source_delta["candidates"]
    }
    if (
        source_delta["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or source_delta["audit_document"]
        != "docs/source-delta-audit-2026-08-09.md"
        or source_delta["automatic_selection_threshold"] != 32.0
        or source_delta["best_candidate_id"]
        != "openneuro_longitudinal_surface_growth_detection_direct_prior_and_unit_limited"
        or source_delta["best_score"] != 31.5
        or source_delta["best_score"] >= source_delta["automatic_selection_threshold"]
        or source_delta["active_shortlist_count"] != 0
        or source_delta["primary_problem_selected"] is not False
        or source_delta["new_candidate_payload_accessed"] is not False
        or source_delta["executable_p0_registered"] is not False
        or source_delta["method_selected"] is not False
        or source_delta["architecture_selected"] is not False
        or source_delta["gpu_training_authorized"] is not False
        or source_delta["outer_test_authorized"] is not False
        or source_delta["submission_identity_active"] is not False
        or source_delta["introai9_connection_verified"] is not True
        or source_delta["introai9_pbs_jobs_observed"] != 0
        or source_delta["introai9_login_node_gpu_command_executed"] is not False
        or source_delta["junjinyong_accessed_for_this_audit"] is not False
        or source_delta["intra_staged_payload_found"] is not False
        or source_delta["intra_staged_material_scope"]
        != "repository_skeleton_readme_splits_and_preview_images_only"
        or source_delta["rsna_access_state"]
        != "official_registry_controlled_access_terms_not_user_accepted_no_payload"
        or observed_source_delta_scores != expected_source_delta_scores
        or any(candidate["payload_accessed"] for candidate in source_delta["candidates"])
        or source_delta["decision"]
        != "reject_all_without_score_repair_p0_method_architecture_or_gpu"
        or source_delta["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The source-delta audit must preserve all six source-only rejections, "
            "introai9-only idle execution, and no P0, method, architecture, or GPU authority."
        )
    checks.append("source-delta rejection and introai9 idle boundary")

    vascular_audit = problem_selection["vascular_semantics_source_audit"]
    _require_keys(
        vascular_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "new_candidate_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "vesselverse_repository_commit",
            "vesselverse_request_or_payload_accessed",
            "phantom_data_url_http_status",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.vascular_semantics_source_audit",
    )
    expected_vascular_scores = {
        "topbrain_paired_modality_vascular_anatomy_without_aneurysm_endpoint": 29.5,
        "ixi_healthy_vessel_atlas_as_aneurysm_anomaly_support": 28.5,
        "vesselverse_protocol_conditioned_vessel_distribution_not_human_aneurysm_raters": 27.5,
        "neckspline_multiloop_or_artifact_extension_direct_prior_occupied": 26.5,
        "paired_cta_dose_reconstruction_phantom_orbit_effective_anatomy_one": 26.0,
        "adam_longitudinal_or_post_treatment_remnant_endpoint_not_released": 25.0,
    }
    observed_vascular_scores = {
        candidate["id"]: candidate["score"]
        for candidate in vascular_audit["candidates"]
    }
    axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in vascular_audit["candidates"]
    )
    if (
        vascular_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or vascular_audit["audit_document"]
        != "docs/vascular-semantics-source-audit-2026-08-10.md"
        or vascular_audit["automatic_selection_threshold"] != 32.0
        or vascular_audit["best_candidate_id"]
        != "topbrain_paired_modality_vascular_anatomy_without_aneurysm_endpoint"
        or vascular_audit["best_score"] != 29.5
        or vascular_audit["best_score"] >= vascular_audit["automatic_selection_threshold"]
        or vascular_audit["active_shortlist_count"] != 0
        or vascular_audit["primary_problem_selected"] is not False
        or vascular_audit["new_candidate_payload_accessed"] is not False
        or vascular_audit["executable_p0_registered"] is not False
        or vascular_audit["method_selected"] is not False
        or vascular_audit["architecture_selected"] is not False
        or vascular_audit["gpu_training_authorized"] is not False
        or vascular_audit["outer_test_authorized"] is not False
        or vascular_audit["submission_identity_active"] is not False
        or vascular_audit["execution_server"] != "introai9"
        or vascular_audit["pbs_job_created"] is not False
        or vascular_audit["login_node_gpu_command_executed"] is not False
        or vascular_audit["junjinyong_accessed_for_this_audit"] is not False
        or vascular_audit["vesselverse_repository_commit"]
        != "ef94d3fd3ce9102cf396a83b1554c98f9f1b5e99"
        or vascular_audit["vesselverse_request_or_payload_accessed"] is not False
        or vascular_audit["phantom_data_url_http_status"] != 404
        or observed_vascular_scores != expected_vascular_scores
        or not axis_sums_match
        or any(candidate["payload_accessed"] for candidate in vascular_audit["candidates"])
        or vascular_audit["decision"]
        != "reject_all_without_score_repair_payload_p0_method_architecture_or_gpu"
        or vascular_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The vascular-semantics audit must preserve all six frozen source-only "
            "rejections, introai9-only execution, and no payload, P0, model, or GPU."
        )
    checks.append("vascular-semantics source rejection and introai9-only boundary")

    pinn_audit = problem_selection["pinn_rupture_direct_prior_audit"]
    _require_keys(
        pinn_audit,
        [
            "status",
            "audit_document",
            "candidate_id",
            "score",
            "maximum_score",
            "axis_scores",
            "automatic_selection_threshold",
            "direct_prior",
            "direct_prior_release_date",
            "direct_prior_rupture_status_cases",
            "direct_prior_ruptured_cases",
            "direct_prior_unruptured_cases",
            "direct_prior_best_late_fusion_auroc",
            "direct_prior_best_late_fusion_auprc",
            "direct_prior_geometry_clinical_auroc",
            "direct_prior_primary_split_description",
            "direct_prior_separate_feature_analysis_patient_aware",
            "direct_prior_fusion_weight_selected_on_same_oof_cohort",
            "aneux_source_lesions",
            "aneux_source_vessel_trees",
            "aneux_source_patients",
            "patient_specific_boundary_conditions_available",
            "paired_cfd_or_in_vivo_flow_validation_available",
            "prospective_rupture_endpoint_available",
            "code_or_split_manifest_linked_in_manuscript",
            "active_shortlist_count",
            "primary_problem_selected",
            "new_candidate_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.pinn_rupture_direct_prior_audit",
    )
    pinn_axis_scores = pinn_audit["axis_scores"]
    if (
        pinn_audit["status"]
        != "completed_source_only_rejected_below_admission_threshold"
        or pinn_audit["audit_document"]
        != "docs/pinn-rupture-direct-prior-audit-2026-08-10.md"
        or pinn_audit["candidate_id"]
        != "physically_validated_incremental_hemodynamic_information_beyond_geometry_and_clinical_variables"
        or pinn_audit["score"] != 23.5
        or pinn_audit["maximum_score"] != 40.0
        or pinn_audit["automatic_selection_threshold"] != 32.0
        or pinn_audit["score"] >= pinn_audit["automatic_selection_threshold"]
        or len(pinn_axis_scores) != 8
        or any(score < 0.0 or score > 5.0 for score in pinn_axis_scores)
        or abs(sum(pinn_axis_scores) - pinn_audit["score"]) >= 1e-12
        or pinn_audit["direct_prior"] != "arxiv_2607_10530"
        or pinn_audit["direct_prior_release_date"] != "2026-07-12"
        or pinn_audit["direct_prior_rupture_status_cases"] != 735
        or pinn_audit["direct_prior_ruptured_cases"] != 261
        or pinn_audit["direct_prior_unruptured_cases"] != 474
        or pinn_audit["direct_prior_best_late_fusion_auroc"] != 0.827
        or pinn_audit["direct_prior_best_late_fusion_auprc"] != 0.732
        or pinn_audit["direct_prior_geometry_clinical_auroc"] != 0.809
        or pinn_audit["direct_prior_primary_split_description"]
        != "stratified_five_fold_fixed_seed_primary_models_patient_grouping_not_explicit_in_manuscript"
        or pinn_audit["direct_prior_separate_feature_analysis_patient_aware"] is not True
        or pinn_audit["direct_prior_fusion_weight_selected_on_same_oof_cohort"] is not True
        or pinn_audit["aneux_source_lesions"] != 750
        or pinn_audit["aneux_source_vessel_trees"] != 668
        or pinn_audit["aneux_source_patients"] != 605
        or pinn_audit["patient_specific_boundary_conditions_available"] is not False
        or pinn_audit["paired_cfd_or_in_vivo_flow_validation_available"] is not False
        or pinn_audit["prospective_rupture_endpoint_available"] is not False
        or pinn_audit["code_or_split_manifest_linked_in_manuscript"] is not False
        or pinn_audit["active_shortlist_count"] != 0
        or pinn_audit["primary_problem_selected"] is not False
        or pinn_audit["new_candidate_payload_accessed"] is not False
        or pinn_audit["executable_p0_registered"] is not False
        or pinn_audit["method_selected"] is not False
        or pinn_audit["architecture_selected"] is not False
        or pinn_audit["gpu_training_authorized"] is not False
        or pinn_audit["outer_test_authorized"] is not False
        or pinn_audit["submission_identity_active"] is not False
        or pinn_audit["execution_server"] != "introai9"
        or pinn_audit["pbs_job_created"] is not False
        or pinn_audit["login_node_gpu_command_executed"] is not False
        or pinn_audit["junjinyong_accessed_for_this_audit"] is not False
        or pinn_audit["decision"]
        != "reject_original_pipeline_as_directly_occupied_and_residual_candidate_as_unidentifiable_without_joint_asset"
        or pinn_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The PINN rupture-status direct-prior audit must preserve the frozen "
            "23.5/40 rejection, unresolved patient grouping, no physical validation, "
            "and introai9-only no-compute boundary."
        )
    checks.append("PINN rupture-status direct-prior rejection boundary")

    hemodynamic_audit = problem_selection["hemodynamic_endpoint_source_audit"]
    _require_keys(
        hemodynamic_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "new_candidate_payload_accessed",
            "aneurisk_cfd_archive_downloaded",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "aneurisk_cfd_record",
            "aneurisk_cfd_archive_bytes_reported",
            "aneurisk_cfd_archive_md5",
            "aneurisk_cfd_source_cases",
            "aneurisk_cfd_source_license",
            "aneurisk_cfd_patient_specific_measured_inflow",
            "aneurisk_cfd_population_age_group_waveforms",
            "aneurisk_cfd_record_paper_outlet_condition_consistent",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.hemodynamic_endpoint_source_audit",
    )
    expected_hemodynamic_scores = {
        "curvature_only_surrogate_of_local_hemodynamic_fields": 31.0,
        "cross_source_curvature_residualized_hemodynamic_added_value": 30.0,
        "within_patient_multiple_aneurysm_culprit_ranking": 23.0,
        "paired_pre_post_treatment_remnant_change_prediction": 25.0,
        "wall_enhancement_hemodynamic_discordance_localization": 26.0,
    }
    observed_hemodynamic_scores = {
        candidate["id"]: candidate["score"]
        for candidate in hemodynamic_audit["candidates"]
    }
    hemodynamic_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in hemodynamic_audit["candidates"]
    )
    if (
        hemodynamic_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or hemodynamic_audit["audit_document"]
        != "docs/hemodynamic-endpoint-source-audit-2026-08-10.md"
        or hemodynamic_audit["automatic_selection_threshold"] != 32.0
        or hemodynamic_audit["best_candidate_id"]
        != "curvature_only_surrogate_of_local_hemodynamic_fields"
        or hemodynamic_audit["best_score"] != 31.0
        or hemodynamic_audit["best_score"]
        >= hemodynamic_audit["automatic_selection_threshold"]
        or hemodynamic_audit["active_shortlist_count"] != 0
        or hemodynamic_audit["primary_problem_selected"] is not False
        or hemodynamic_audit["new_candidate_payload_accessed"] is not False
        or hemodynamic_audit["aneurisk_cfd_archive_downloaded"] is not False
        or hemodynamic_audit["executable_p0_registered"] is not False
        or hemodynamic_audit["method_selected"] is not False
        or hemodynamic_audit["architecture_selected"] is not False
        or hemodynamic_audit["gpu_training_authorized"] is not False
        or hemodynamic_audit["outer_test_authorized"] is not False
        or hemodynamic_audit["submission_identity_active"] is not False
        or hemodynamic_audit["execution_server"] != "introai9"
        or hemodynamic_audit["pbs_job_created"] is not False
        or hemodynamic_audit["login_node_gpu_command_executed"] is not False
        or hemodynamic_audit["junjinyong_accessed_for_this_audit"] is not False
        or hemodynamic_audit["aneurisk_cfd_record"] != "zenodo_19455127"
        or hemodynamic_audit["aneurisk_cfd_archive_bytes_reported"] != 1400000000
        or hemodynamic_audit["aneurisk_cfd_archive_md5"]
        != "8c66e7bb359d04bd1a5d6db6da3f3926"
        or hemodynamic_audit["aneurisk_cfd_source_cases"] != 76
        or hemodynamic_audit["aneurisk_cfd_source_license"] != "cc_by_4_0"
        or hemodynamic_audit["aneurisk_cfd_patient_specific_measured_inflow"]
        is not False
        or hemodynamic_audit["aneurisk_cfd_population_age_group_waveforms"] != 2
        or hemodynamic_audit["aneurisk_cfd_record_paper_outlet_condition_consistent"]
        is not False
        or observed_hemodynamic_scores != expected_hemodynamic_scores
        or not hemodynamic_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in hemodynamic_audit["candidates"]
        )
        or hemodynamic_audit["decision"]
        != "reject_all_without_score_repair_payload_p0_method_architecture_or_gpu"
        or hemodynamic_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The hemodynamic-endpoint audit must preserve all five frozen "
            "source-only rejections, the 31/40 maximum, no archive/P0/model/GPU, "
            "and introai9-only execution."
        )
    checks.append("hemodynamic-endpoint rejection and introai9-only boundary")

    topology_audit = problem_selection["topology_procedure_source_audit"]
    _require_keys(
        topology_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_ids",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "large_archive_or_model_weight_payload_accessed",
            "patient_image_or_controlled_challenge_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "tornadic_figshare_record",
            "tornadic_figshare_license",
            "tornadic_cfd_wss_cases",
            "tornadic_mri_figure_cases",
            "tornadic_same_case_cfd_mri_pairs_reported",
            "tornadic_readme_bytes",
            "tornadic_readme_accessed",
            "tornadic_wss_archives_bytes",
            "tornadic_wss_archives_downloaded",
            "tornadic_velocity_archive_bytes",
            "tornadic_velocity_archive_downloaded",
            "tornadic_matlab_archive_bytes",
            "tornadic_matlab_archive_downloaded",
            "maximus_record",
            "maximus_model_archive_bytes",
            "maximus_model_archive_md5",
            "maximus_model_archive_downloaded",
            "maximus_source_images_public_in_record",
            "maximus_paper_images",
            "maximus_paper_patients",
            "maximus_paper_adam_subjects",
            "optimal_view_paper_patients",
            "optimal_view_public_volume_and_view_label_asset_found",
            "rheology_slip_tag_commit",
            "rheology_slip_aneurysm_geometries",
            "rheology_slip_repository_tree_and_readme_accessed",
            "rheology_slip_generated_fields_or_zenodo_zip_accessed",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.topology_procedure_source_audit",
    )
    expected_topology_scores = {
        "cross_modality_tornadic_topology_preservation": 24.0,
        "noise_resolution_stable_wss_topological_skeleton": 28.5,
        "set_valued_c_arm_working_view_distribution": 24.0,
        "differential_diagnosis_aware_open_set_tof_detection": 28.5,
        "rheology_slip_model_form_hemodynamic_uncertainty": 28.5,
    }
    observed_topology_scores = {
        candidate["id"]: candidate["score"]
        for candidate in topology_audit["candidates"]
    }
    topology_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in topology_audit["candidates"]
    )
    if (
        topology_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or topology_audit["audit_document"]
        != "docs/topology-procedure-source-audit-2026-08-10.md"
        or topology_audit["automatic_selection_threshold"] != 32.0
        or topology_audit["best_candidate_ids"]
        != [
            "noise_resolution_stable_wss_topological_skeleton",
            "differential_diagnosis_aware_open_set_tof_detection",
            "rheology_slip_model_form_hemodynamic_uncertainty",
        ]
        or topology_audit["best_score"] != 28.5
        or topology_audit["best_score"]
        >= topology_audit["automatic_selection_threshold"]
        or topology_audit["active_shortlist_count"] != 0
        or topology_audit["primary_problem_selected"] is not False
        or topology_audit["large_archive_or_model_weight_payload_accessed"]
        is not False
        or topology_audit["patient_image_or_controlled_challenge_payload_accessed"]
        is not False
        or topology_audit["executable_p0_registered"] is not False
        or topology_audit["method_selected"] is not False
        or topology_audit["architecture_selected"] is not False
        or topology_audit["gpu_training_authorized"] is not False
        or topology_audit["outer_test_authorized"] is not False
        or topology_audit["submission_identity_active"] is not False
        or topology_audit["execution_server"] != "introai9"
        or topology_audit["pbs_job_created"] is not False
        or topology_audit["login_node_gpu_command_executed"] is not False
        or topology_audit["junjinyong_accessed_for_this_audit"] is not False
        or topology_audit["tornadic_figshare_record"]
        != "10.6084/m9.figshare.32270130.v2"
        or topology_audit["tornadic_figshare_license"] != "cc_by_4_0"
        or topology_audit["tornadic_cfd_wss_cases"] != 3
        or topology_audit["tornadic_mri_figure_cases"] != 2
        or topology_audit["tornadic_same_case_cfd_mri_pairs_reported"] != 0
        or topology_audit["tornadic_readme_bytes"] != 2063
        or topology_audit["tornadic_readme_accessed"] is not True
        or topology_audit["tornadic_wss_archives_bytes"] != 3189493388
        or topology_audit["tornadic_wss_archives_downloaded"] is not False
        or topology_audit["tornadic_velocity_archive_bytes"] != 309081947
        or topology_audit["tornadic_velocity_archive_downloaded"] is not False
        or topology_audit["tornadic_matlab_archive_bytes"] != 10059
        or topology_audit["tornadic_matlab_archive_downloaded"] is not False
        or topology_audit["maximus_record"] != "zenodo_17894703"
        or topology_audit["maximus_model_archive_bytes"] != 1167744043
        or topology_audit["maximus_model_archive_md5"]
        != "3b38956f084d1570c00c47b232d6269d"
        or topology_audit["maximus_model_archive_downloaded"] is not False
        or topology_audit["maximus_source_images_public_in_record"] is not False
        or topology_audit["maximus_paper_images"] != 385
        or topology_audit["maximus_paper_patients"] != 345
        or topology_audit["maximus_paper_adam_subjects"] != 113
        or topology_audit["optimal_view_paper_patients"] != 18
        or topology_audit["optimal_view_public_volume_and_view_label_asset_found"]
        is not False
        or topology_audit["rheology_slip_tag_commit"]
        != "acda3721a511a527ebe374728874f8e69cfa7fbb"
        or topology_audit["rheology_slip_aneurysm_geometries"] != 1
        or topology_audit["rheology_slip_repository_tree_and_readme_accessed"]
        is not True
        or topology_audit["rheology_slip_generated_fields_or_zenodo_zip_accessed"]
        is not False
        or observed_topology_scores != expected_topology_scores
        or not topology_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in topology_audit["candidates"]
        )
        or topology_audit["decision"]
        != "reject_all_without_score_repair_large_payload_p0_method_architecture_or_gpu"
        or topology_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The topology-procedure audit must preserve all five frozen "
            "source-only rejections, the 28.5/40 maximum, no large payload/P0/"
            "model/GPU, and introai9-only execution."
        )
    checks.append("topology-procedure rejection and introai9-only boundary")

    context_audit = problem_selection["context_treatment_source_audit"]
    _require_keys(
        context_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "spreadsheet_vtk_mri_or_model_weight_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "observed_introai9_pbs_job_count",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "aneusi_doi",
            "aneusi_repository_commit",
            "aneusi_repository_tree",
            "aneusi_code_license",
            "aneusi_data_license",
            "aneusi_paper_patients",
            "aneusi_paper_cases",
            "aneusi_clip_factors",
            "aneusi_isolated_models",
            "aneusi_reported_cuts",
            "aneusi_repository_named_cases",
            "aneusi_model_vtk_entries",
            "aneusi_centerline_vtk_entries",
            "aneusi_automated_neck_vtk_entries",
            "aneusi_paper_repository_case_count_reconciled",
            "aneusi_spreadsheet_accessed",
            "aneusi_vtk_payload_accessed",
            "flow_mri_4d_record",
            "flow_mri_4d_datasets",
            "flow_mri_black_blood_record",
            "flow_mri_black_blood_datasets",
            "flow_mri_unique_models",
            "flow_mri_source_patient_anatomies",
            "flow_mri_device_conditions",
            "flow_mri_archives_downloaded",
            "diva_seg_labeled_train",
            "diva_seg_test",
            "diva_seg_unlabeled",
            "diva_seg_external_labeled",
            "diva_seg_public_image_mask_payload_found",
            "latent_shape_surfaces_reported",
            "latent_shape_public_code_and_weights",
            "latent_shape_source_mesh_payload_accessed",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.context_treatment_source_audit",
    )
    expected_context_scores = {
        "ordered_parent_vessel_context_sufficiency_for_rupture_status": 31.5,
        "paired_black_blood_to_4d_flow_treatment_response": 27.5,
        "device_conditioned_counterfactual_treatment_selection": 26.0,
        "morphology_decision_preserving_tof_segmentation": 27.0,
        "external_latent_shape_calibration": 30.0,
    }
    observed_context_scores = {
        candidate["id"]: candidate["score"]
        for candidate in context_audit["candidates"]
    }
    context_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in context_audit["candidates"]
    )
    if (
        context_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or context_audit["audit_document"]
        != "docs/context-treatment-source-audit-2026-08-10.md"
        or context_audit["automatic_selection_threshold"] != 32.0
        or context_audit["best_candidate_id"]
        != "ordered_parent_vessel_context_sufficiency_for_rupture_status"
        or context_audit["best_score"] != 31.5
        or context_audit["best_score"]
        >= context_audit["automatic_selection_threshold"]
        or context_audit["active_shortlist_count"] != 0
        or context_audit["primary_problem_selected"] is not False
        or context_audit["spreadsheet_vtk_mri_or_model_weight_payload_accessed"]
        is not False
        or context_audit["executable_p0_registered"] is not False
        or context_audit["method_selected"] is not False
        or context_audit["architecture_selected"] is not False
        or context_audit["gpu_training_authorized"] is not False
        or context_audit["outer_test_authorized"] is not False
        or context_audit["submission_identity_active"] is not False
        or context_audit["execution_server"] != "introai9"
        or context_audit["observed_introai9_pbs_job_count"] != 0
        or context_audit["pbs_job_created"] is not False
        or context_audit["login_node_gpu_command_executed"] is not False
        or context_audit["junjinyong_accessed_for_this_audit"] is not False
        or context_audit["aneusi_doi"] != "10.1016/j.cmpb.2026.109525"
        or context_audit["aneusi_repository_commit"]
        != "5b4c454ede46c4cd56d3831cb24748c7e1521eca"
        or context_audit["aneusi_repository_tree"]
        != "21ee76c85c1ddb00961879d737b5c994dbc3b711"
        or context_audit["aneusi_code_license"] != "mit"
        or context_audit["aneusi_data_license"] != "cc_by_nc_3_0"
        or context_audit["aneusi_paper_patients"] != 99
        or context_audit["aneusi_paper_cases"] != 102
        or context_audit["aneusi_clip_factors"] != 7
        or context_audit["aneusi_isolated_models"] != 714
        or context_audit["aneusi_reported_cuts"] != 2592
        or context_audit["aneusi_repository_named_cases"] != 103
        or context_audit["aneusi_model_vtk_entries"] != 103
        or context_audit["aneusi_centerline_vtk_entries"] != 103
        or context_audit["aneusi_automated_neck_vtk_entries"] != 103
        or context_audit["aneusi_paper_repository_case_count_reconciled"]
        is not False
        or context_audit["aneusi_spreadsheet_accessed"] is not False
        or context_audit["aneusi_vtk_payload_accessed"] is not False
        or context_audit["flow_mri_4d_record"]
        != "10.5281/zenodo.17183575"
        or context_audit["flow_mri_4d_datasets"] != 33
        or context_audit["flow_mri_black_blood_record"]
        != "10.5281/zenodo.17191239"
        or context_audit["flow_mri_black_blood_datasets"] != 38
        or context_audit["flow_mri_unique_models"] != 5
        or context_audit["flow_mri_source_patient_anatomies"] != 2
        or context_audit["flow_mri_device_conditions"] != 15
        or context_audit["flow_mri_archives_downloaded"] is not False
        or context_audit["diva_seg_labeled_train"] != 57
        or context_audit["diva_seg_test"] != 14
        or context_audit["diva_seg_unlabeled"] != 518
        or context_audit["diva_seg_external_labeled"] != 82
        or context_audit["diva_seg_public_image_mask_payload_found"] is not False
        or context_audit["latent_shape_surfaces_reported"] != 958
        or context_audit["latent_shape_public_code_and_weights"] is not True
        or context_audit["latent_shape_source_mesh_payload_accessed"] is not False
        or observed_context_scores != expected_context_scores
        or not context_axis_sums_match
        or any(candidate["payload_accessed"] for candidate in context_audit["candidates"])
        or context_audit["decision"]
        != "reject_all_without_score_repair_spreadsheet_vtk_mri_payload_p0_method_architecture_or_gpu"
        or context_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The context-treatment audit must preserve all five frozen "
            "source-only rejections, the 31.5/40 maximum, no spreadsheet/VTK/"
            "MRI/P0/model/GPU, and introai9-only execution."
        )
    checks.append("context-treatment rejection and introai9-only boundary")

    provenance_audit = problem_selection["provenance_evaluation_source_audit"]
    _require_keys(
        provenance_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "any_archive_mesh_image_spreadsheet_or_model_weight_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "observed_introai9_pbs_job_count",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "aneux_total_lesions",
            "aneux_total_patients",
            "aneux_aneurisk_lesions",
            "aneux_aneurisk_patients",
            "aneux_case_level_cross_release_lineage_manifest_found",
            "aneux_archive_accessed",
            "aneurisk_cfd_record",
            "aneurisk_cfd_selected_geometries",
            "aneurisk_cfd_source_cases_reported",
            "aneurisk_cfd_archive_bytes",
            "aneurisk_cfd_archive_accessed",
            "public_aneurisk_mirror_named_model_folders",
            "public_aneurisk_mirror_named_dicom_folders",
            "public_aneurisk_mirror_label_files",
            "public_aneurisk_mirror_contains_c0074a_and_c0074b",
            "public_aneurisk_mirror_member_payload_accessed",
            "pointnet_internal_auc",
            "pointnet_external_auc",
            "pointnet_external_set_used_in_reported_curve_selection",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.provenance_evaluation_source_audit",
    )
    expected_provenance_scores = {
        "cross_release_lineage_blocked_cfd_to_rupture_transfer_validity": 30.0,
        "source_conditional_selective_rupture_prediction": 29.5,
        "test_blind_pointnet_external_reevaluation": 28.5,
        "hug_curator_lineage_invariant_morphometry": 23.5,
        "patient_set_multiple_aneurysm_rupture_consistency": 25.5,
    }
    observed_provenance_scores = {
        candidate["id"]: candidate["score"]
        for candidate in provenance_audit["candidates"]
    }
    provenance_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in provenance_audit["candidates"]
    )
    if (
        provenance_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or provenance_audit["audit_document"]
        != "docs/provenance-evaluation-source-audit-2026-08-10.md"
        or provenance_audit["automatic_selection_threshold"] != 32.0
        or provenance_audit["best_candidate_id"]
        != "cross_release_lineage_blocked_cfd_to_rupture_transfer_validity"
        or provenance_audit["best_score"] != 30.0
        or provenance_audit["best_score"]
        >= provenance_audit["automatic_selection_threshold"]
        or provenance_audit["active_shortlist_count"] != 0
        or provenance_audit["primary_problem_selected"] is not False
        or provenance_audit[
            "any_archive_mesh_image_spreadsheet_or_model_weight_payload_accessed"
        ]
        is not False
        or provenance_audit["executable_p0_registered"] is not False
        or provenance_audit["method_selected"] is not False
        or provenance_audit["architecture_selected"] is not False
        or provenance_audit["gpu_training_authorized"] is not False
        or provenance_audit["outer_test_authorized"] is not False
        or provenance_audit["submission_identity_active"] is not False
        or provenance_audit["execution_server"] != "introai9"
        or provenance_audit["observed_introai9_pbs_job_count"] != 0
        or provenance_audit["pbs_job_created"] is not False
        or provenance_audit["login_node_gpu_command_executed"] is not False
        or provenance_audit["junjinyong_accessed_for_this_audit"] is not False
        or provenance_audit["aneux_total_lesions"] != 750
        or provenance_audit["aneux_total_patients"] != 605
        or provenance_audit["aneux_aneurisk_lesions"] != 101
        or provenance_audit["aneux_aneurisk_patients"] != 97
        or provenance_audit["aneux_case_level_cross_release_lineage_manifest_found"]
        is not False
        or provenance_audit["aneux_archive_accessed"] is not False
        or provenance_audit["aneurisk_cfd_record"] != "10.5281/zenodo.19455127"
        or provenance_audit["aneurisk_cfd_selected_geometries"] != 76
        or provenance_audit["aneurisk_cfd_source_cases_reported"] != 100
        or provenance_audit["aneurisk_cfd_archive_bytes"] != 1430889142
        or provenance_audit["aneurisk_cfd_archive_accessed"] is not False
        or provenance_audit["public_aneurisk_mirror_named_model_folders"] != 24
        or provenance_audit["public_aneurisk_mirror_named_dicom_folders"] != 24
        or provenance_audit["public_aneurisk_mirror_label_files"] != 15
        or provenance_audit[
            "public_aneurisk_mirror_contains_c0074a_and_c0074b"
        ]
        is not True
        or provenance_audit["public_aneurisk_mirror_member_payload_accessed"]
        is not False
        or provenance_audit["pointnet_internal_auc"] != 0.85
        or provenance_audit["pointnet_external_auc"] != 0.71
        or provenance_audit["pointnet_external_set_used_in_reported_curve_selection"]
        is not True
        or observed_provenance_scores != expected_provenance_scores
        or not provenance_axis_sums_match
        or any(candidate["payload_accessed"] for candidate in provenance_audit["candidates"])
        or provenance_audit["decision"]
        != "reject_all_without_score_repair_archive_mesh_image_spreadsheet_payload_p0_method_architecture_or_gpu"
        or provenance_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_with_exact_public_lineage_or_independent_patient_endpoint_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The provenance-evaluation audit must preserve all five frozen "
            "source-only rejections, the 30.0/40 maximum, no archive/mesh/"
            "image/P0/model/GPU, and introai9-only execution."
        )
    checks.append("provenance-evaluation rejection and introai9-only boundary")

    treatment_audit = problem_selection["treatment_surveillance_source_audit"]
    _require_keys(
        treatment_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "any_spreadsheet_r_document_presentation_dsa_mra_or_patient_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "observed_introai9_pbs_job_count",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "flow_diverter_dataset_doi",
            "flow_diverter_subjects",
            "flow_diverter_procedures",
            "pipeline_procedures",
            "surpass_procedures",
            "followup_observation_count_maximum_per_procedure",
            "exact_biological_occlusion_time_observed",
            "device_assignment_randomized",
            "paired_mra_zenodo_doi",
            "paired_mra_patients",
            "paired_mra_record_access_right",
            "paired_mra_public_file_list_exposed",
            "paired_mra_reference_standard",
            "paired_mra_reported_intermodality_kappa",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.treatment_surveillance_source_audit",
    )
    expected_treatment_scores = {
        "observed_interval_censored_post_fd_occlusion_forecasting": 30.0,
        "causal_pipeline_versus_surpass_device_selection": 26.0,
        "early_complication_delayed_occlusion_utility_prediction": 29.0,
        "recurrent_procedure_patient_history_sequence_modeling": 26.0,
        "fast_standard_tof_mra_remnant_decision_equivalence": 23.0,
    }
    observed_treatment_scores = {
        candidate["id"]: candidate["score"]
        for candidate in treatment_audit["candidates"]
    }
    treatment_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in treatment_audit["candidates"]
    )
    if (
        treatment_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or treatment_audit["audit_document"]
        != "docs/treatment-surveillance-source-audit-2026-08-10.md"
        or treatment_audit["automatic_selection_threshold"] != 32.0
        or treatment_audit["best_candidate_id"]
        != "observed_interval_censored_post_fd_occlusion_forecasting"
        or treatment_audit["best_score"] != 30.0
        or treatment_audit["best_score"]
        >= treatment_audit["automatic_selection_threshold"]
        or treatment_audit["active_shortlist_count"] != 0
        or treatment_audit["primary_problem_selected"] is not False
        or treatment_audit[
            "any_spreadsheet_r_document_presentation_dsa_mra_or_patient_payload_accessed"
        ]
        is not False
        or treatment_audit["executable_p0_registered"] is not False
        or treatment_audit["method_selected"] is not False
        or treatment_audit["architecture_selected"] is not False
        or treatment_audit["gpu_training_authorized"] is not False
        or treatment_audit["outer_test_authorized"] is not False
        or treatment_audit["submission_identity_active"] is not False
        or treatment_audit["execution_server"] != "introai9"
        or treatment_audit["observed_introai9_pbs_job_count"] != 0
        or treatment_audit["pbs_job_created"] is not False
        or treatment_audit["login_node_gpu_command_executed"] is not False
        or treatment_audit["junjinyong_accessed_for_this_audit"] is not False
        or treatment_audit["flow_diverter_dataset_doi"]
        != "10.17632/nzzx92ky6r.2"
        or treatment_audit["flow_diverter_subjects"] != 126
        or treatment_audit["flow_diverter_procedures"] != 141
        or treatment_audit["pipeline_procedures"] != 96
        or treatment_audit["surpass_procedures"] != 45
        or treatment_audit["followup_observation_count_maximum_per_procedure"]
        != 2
        or treatment_audit["exact_biological_occlusion_time_observed"] is not False
        or treatment_audit["device_assignment_randomized"] is not False
        or treatment_audit["paired_mra_zenodo_doi"]
        != "10.5281/zenodo.6654502"
        or treatment_audit["paired_mra_patients"] != 22
        or treatment_audit["paired_mra_record_access_right"] != "restricted"
        or treatment_audit["paired_mra_public_file_list_exposed"] is not False
        or treatment_audit["paired_mra_reference_standard"]
        != "parallel_imaging_tof_mra_not_dsa"
        or treatment_audit["paired_mra_reported_intermodality_kappa"] != 0.98
        or observed_treatment_scores != expected_treatment_scores
        or not treatment_axis_sums_match
        or any(candidate["payload_accessed"] for candidate in treatment_audit["candidates"])
        or treatment_audit["decision"]
        != "reject_all_without_score_repair_spreadsheet_r_document_presentation_dsa_mra_payload_p0_method_architecture_or_gpu"
        or treatment_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_with_public_independent_endpoint_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The treatment-surveillance audit must preserve all five frozen "
            "source-only rejections, the 30.0/40 maximum, no spreadsheet/DSA/"
            "MRA/P0/model/GPU, and introai9-only execution."
        )
    checks.append("treatment-surveillance rejection and introai9-only boundary")

    acquisition_audit = problem_selection["acquisition_flow_source_audit"]
    _require_keys(
        acquisition_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "any_synapse_application_challenge_form_kspace_mat_aneurysm_zip_or_patient_payload_accessed",
            "cmrx_terms_accepted_verified",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "observed_introai9_pbs_job_count",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "cmrx_total_cases_minimum",
            "cmrx_train_fully_sampled_cases",
            "cmrx_regular_validation_cases",
            "cmrx_regular_test_cases",
            "cmrx_cerebrovascular_validation_cases",
            "cmrx_cerebrovascular_test_cases",
            "cmrx_acceleration_factors",
            "cmrx_independent_research_embargo_ends",
            "cmrx_embargo_after_isbi_submission_deadline",
            "cmrx_same_case_repeat_multi_venc_acquisitions_reported",
            "dual_venc_aneurysm_doi",
            "dual_venc_aneurysm_scans",
            "dual_venc_aneurysm_printed_models",
            "dual_venc_aneurysm_effective_anatomies",
            "dual_venc_aneurysm_archive_accessed",
            "cmrx_fully_sampled_reference_is_independent_wss_ground_truth",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.acquisition_flow_source_audit",
    )
    expected_acquisition_scores = {
        "nested_acceleration_coherent_4d_flow_reconstruction": 27.5,
        "cross_site_cross_anatomy_4d_flow_reconstruction": 26.5,
        "explicit_multi_venc_divergence_free_uncertainty": 24.0,
        "functional_risk_controlled_wss_vorticity_reconstruction": 26.0,
        "treated_aneurysm_dual_venc_device_response_transfer": 27.0,
    }
    observed_acquisition_scores = {
        candidate["id"]: candidate["score"]
        for candidate in acquisition_audit["candidates"]
    }
    acquisition_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in acquisition_audit["candidates"]
    )
    if (
        acquisition_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or acquisition_audit["audit_document"]
        != "docs/acquisition-flow-source-audit-2026-08-10.md"
        or acquisition_audit["automatic_selection_threshold"] != 32.0
        or acquisition_audit["best_candidate_id"]
        != "nested_acceleration_coherent_4d_flow_reconstruction"
        or acquisition_audit["best_score"] != 27.5
        or acquisition_audit["best_score"]
        >= acquisition_audit["automatic_selection_threshold"]
        or acquisition_audit["active_shortlist_count"] != 0
        or acquisition_audit["primary_problem_selected"] is not False
        or acquisition_audit[
            "any_synapse_application_challenge_form_kspace_mat_aneurysm_zip_or_patient_payload_accessed"
        ]
        is not False
        or acquisition_audit["cmrx_terms_accepted_verified"] is not False
        or acquisition_audit["executable_p0_registered"] is not False
        or acquisition_audit["method_selected"] is not False
        or acquisition_audit["architecture_selected"] is not False
        or acquisition_audit["gpu_training_authorized"] is not False
        or acquisition_audit["outer_test_authorized"] is not False
        or acquisition_audit["submission_identity_active"] is not False
        or acquisition_audit["execution_server"] != "introai9"
        or acquisition_audit["observed_introai9_pbs_job_count"] != 0
        or acquisition_audit["pbs_job_created"] is not False
        or acquisition_audit["login_node_gpu_command_executed"] is not False
        or acquisition_audit["junjinyong_accessed_for_this_audit"] is not False
        or acquisition_audit["cmrx_total_cases_minimum"] != 400
        or acquisition_audit["cmrx_train_fully_sampled_cases"] != 138
        or acquisition_audit["cmrx_regular_validation_cases"] != 32
        or acquisition_audit["cmrx_regular_test_cases"] != 43
        or acquisition_audit["cmrx_cerebrovascular_validation_cases"] != 10
        or acquisition_audit["cmrx_cerebrovascular_test_cases"] != 20
        or acquisition_audit["cmrx_acceleration_factors"]
        != [10, 20, 30, 40, 50]
        or acquisition_audit["cmrx_independent_research_embargo_ends"]
        != "2026-12"
        or acquisition_audit["cmrx_embargo_after_isbi_submission_deadline"]
        is not True
        or acquisition_audit["cmrx_same_case_repeat_multi_venc_acquisitions_reported"]
        is not False
        or acquisition_audit["dual_venc_aneurysm_doi"]
        != "10.5281/zenodo.14981710"
        or acquisition_audit["dual_venc_aneurysm_scans"] != 8
        or acquisition_audit["dual_venc_aneurysm_printed_models"] != 4
        or acquisition_audit["dual_venc_aneurysm_effective_anatomies"] != 1
        or acquisition_audit["dual_venc_aneurysm_archive_accessed"] is not False
        or acquisition_audit[
            "cmrx_fully_sampled_reference_is_independent_wss_ground_truth"
        ]
        is not False
        or observed_acquisition_scores != expected_acquisition_scores
        or not acquisition_axis_sums_match
        or any(candidate["payload_accessed"] for candidate in acquisition_audit["candidates"])
        or acquisition_audit["decision"]
        != "reject_all_without_score_repair_synapse_application_challenge_form_kspace_mat_aneurysm_zip_payload_p0_method_architecture_or_gpu"
        or acquisition_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_with_isbi_compatible_public_assets_and_independent_functional_reference_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The acquisition-flow audit must preserve all five frozen "
            "source-only rejections, the 27.5/40 maximum, no Synapse/k-space/"
            "aneurysm archive/P0/model/GPU, and introai9-only execution."
        )
    checks.append("acquisition-flow rejection and introai9-only boundary")

    fsi_wall_audit = problem_selection["fsi_wall_source_audit"]
    _require_keys(
        fsi_wall_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "any_anxplore_vtk_rigid_fsi_field_wall_motion_microct_fem_or_new_benchanxplore_member_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "observed_introai9_pbs_job_count",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "anxplore_public_repository",
            "anxplore_geometries",
            "anxplore_public_full_dataset_fluid_meshes",
            "anxplore_paired_rigid_fsi_simulations_reported_by_paper",
            "anxplore_paired_rigid_fsi_solution_fields_publicly_released",
            "anxplore_public_repository_role",
            "anxplore_shared_parent_geometry",
            "anxplore_shared_inflow_and_material_assumptions",
            "anxplore_flow_diverter_paired_effective_cases",
            "inverse_mechanics_species",
            "inverse_mechanics_effective_units",
            "microct_wall_thickness_human_aneurysms",
            "benchanxplore_cases",
            "benchanxplore_used_for_prior_architecture_discovery",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.fsi_wall_source_audit",
    )
    expected_fsi_wall_scores = {
        "rigid_to_compliant_hemodynamic_discrepancy_operator": 30.5,
        "dynamic_geometry_inverse_wall_property_inference": 29.5,
        "compliance_conditioned_flow_diverter_response": 26.5,
        "lumen_to_wall_thickness_hotspot_prediction": 24.5,
        "selective_rigid_cfd_to_fsi_referral": 29.0,
        "multi_granularity_conformal_hemodynamic_surrogate": 31.0,
    }
    observed_fsi_wall_scores = {
        candidate["id"]: candidate["score"]
        for candidate in fsi_wall_audit["candidates"]
    }
    fsi_wall_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in fsi_wall_audit["candidates"]
    )
    if (
        fsi_wall_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or fsi_wall_audit["audit_document"]
        != "docs/fsi-wall-source-audit-2026-08-10.md"
        or fsi_wall_audit["automatic_selection_threshold"] != 32.0
        or fsi_wall_audit["best_candidate_id"]
        != "multi_granularity_conformal_hemodynamic_surrogate"
        or fsi_wall_audit["best_score"] != 31.0
        or fsi_wall_audit["best_score"]
        >= fsi_wall_audit["automatic_selection_threshold"]
        or fsi_wall_audit["active_shortlist_count"] != 0
        or fsi_wall_audit["primary_problem_selected"] is not False
        or fsi_wall_audit[
            "any_anxplore_vtk_rigid_fsi_field_wall_motion_microct_fem_or_new_benchanxplore_member_payload_accessed"
        ]
        is not False
        or fsi_wall_audit["executable_p0_registered"] is not False
        or fsi_wall_audit["method_selected"] is not False
        or fsi_wall_audit["architecture_selected"] is not False
        or fsi_wall_audit["gpu_training_authorized"] is not False
        or fsi_wall_audit["outer_test_authorized"] is not False
        or fsi_wall_audit["submission_identity_active"] is not False
        or fsi_wall_audit["execution_server"] != "introai9"
        or fsi_wall_audit["observed_introai9_pbs_job_count"] != 0
        or fsi_wall_audit["pbs_job_created"] is not False
        or fsi_wall_audit["login_node_gpu_command_executed"] is not False
        or fsi_wall_audit["junjinyong_accessed_for_this_audit"] is not False
        or fsi_wall_audit["anxplore_public_repository"]
        != "https://github.com/aurelegoetz/AnXplore"
        or fsi_wall_audit["anxplore_geometries"] != 101
        or fsi_wall_audit["anxplore_public_full_dataset_fluid_meshes"] != 101
        or fsi_wall_audit["anxplore_paired_rigid_fsi_simulations_reported_by_paper"]
        != 101
        or fsi_wall_audit["anxplore_paired_rigid_fsi_solution_fields_publicly_released"]
        is not False
        or fsi_wall_audit["anxplore_public_repository_role"]
        != "tetrahedral_fluid_and_selected_solid_meshes_not_paired_rigid_fsi_solution_fields"
        or fsi_wall_audit["anxplore_shared_parent_geometry"]
        != "idealized_toroidal_parent_artery"
        or fsi_wall_audit["anxplore_shared_inflow_and_material_assumptions"]
        is not True
        or fsi_wall_audit["anxplore_flow_diverter_paired_effective_cases"] != 1
        or fsi_wall_audit["inverse_mechanics_species"] != "animal_model"
        or fsi_wall_audit["inverse_mechanics_effective_units"] != 1
        or fsi_wall_audit["microct_wall_thickness_human_aneurysms"] != 5
        or fsi_wall_audit["benchanxplore_cases"] != 105
        or fsi_wall_audit["benchanxplore_used_for_prior_architecture_discovery"]
        is not True
        or observed_fsi_wall_scores != expected_fsi_wall_scores
        or not fsi_wall_axis_sums_match
        or any(candidate["payload_accessed"] for candidate in fsi_wall_audit["candidates"])
        or fsi_wall_audit["decision"]
        != "reject_all_without_score_repair_anxplore_vtk_rigid_fsi_field_wall_motion_microct_fem_or_new_benchanxplore_payload_p0_method_architecture_or_gpu"
        or fsi_wall_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_with_public_paired_rigid_fsi_or_measured_wall_motion_targets_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The FSI-wall audit must preserve all six frozen source-only "
            "rejections, the 31.0/40 maximum, no mesh/field/wall payload/P0/"
            "model/GPU, and introai9-only execution."
        )
    checks.append("FSI-wall rejection and introai9-only boundary")

    longitudinal_audit = problem_selection["longitudinal_perfusion_source_audit"]
    _require_keys(
        longitudinal_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "official_record_embedded_readme_and_file_manifests_accessed",
            "any_standalone_ctp_json_spreadsheet_nifti_zip_sah_ct_archive_3dra_cta_csv_vwe_csv_image_mesh_or_field_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "observed_introai9_pbs_job_count",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "ctp_dryad_doi",
            "ctp_license",
            "ctp_version",
            "ctp_patients",
            "ctp_original_exams",
            "ctp_parametric_maps",
            "ctp_parameters",
            "ctp_dci_events",
            "ctp_vasospasm_patients",
            "ctp_mean_original_exams_per_patient",
            "ctp_mean_inter_exam_days",
            "ctp_inter_exam_day_range",
            "ctp_paper_interpolated_exams",
            "ctp_single_center_single_scanner",
            "ctp_source_slice_thickness_mm",
            "ctp_mni_grid_shape",
            "ctp_mni_voxel_mm",
            "ctp_observation_process_clinically_informative",
            "ctp_guided_rescue_treatment_reported",
            "unobserved_untreated_trajectory_identified",
            "scan_policy_utility_released",
            "figshare_3dra_cta_doi",
            "figshare_3dra_cta_effective_aneurysms",
            "figshare_3dra_cta_released_files",
            "figshare_3dra_cta_released_csv_bytes",
            "figshare_3dra_cta_source_images_meshes_or_fields_released",
            "vwe_dryad_doi",
            "vwe_unruptured_aneurysms",
            "vwe_released_files",
            "vwe_released_csv_bytes",
            "vwe_mri_volumes_surfaces_or_spatial_maps_released",
            "sah_segmentation_zenodo_doi",
            "sah_segmentation_record_license_present",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.longitudinal_perfusion_source_audit",
    )
    expected_longitudinal_scores = {
        "informative_scan_aware_continuous_time_ctp_field_forecasting": 31.0,
        "pre_dci_event_time_perfusion_early_warning": 29.0,
        "personalized_ctp_reacquisition_policy": 28.0,
        "treatment_conditioned_perfusion_counterfactual": 27.0,
        "cross_modality_3dra_cta_hemodynamic_invariance": 29.5,
        "global_local_vwe_hemodynamic_discordance": 29.0,
    }
    observed_longitudinal_scores = {
        candidate["id"]: candidate["score"]
        for candidate in longitudinal_audit["candidates"]
    }
    longitudinal_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in longitudinal_audit["candidates"]
    )
    if (
        longitudinal_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or longitudinal_audit["audit_document"]
        != "docs/longitudinal-perfusion-source-audit-2026-08-10.md"
        or longitudinal_audit["automatic_selection_threshold"] != 32.0
        or longitudinal_audit["best_candidate_id"]
        != "informative_scan_aware_continuous_time_ctp_field_forecasting"
        or longitudinal_audit["best_score"] != 31.0
        or longitudinal_audit["best_score"]
        >= longitudinal_audit["automatic_selection_threshold"]
        or longitudinal_audit["active_shortlist_count"] != 0
        or longitudinal_audit["primary_problem_selected"] is not False
        or longitudinal_audit[
            "official_record_embedded_readme_and_file_manifests_accessed"
        ]
        is not True
        or longitudinal_audit[
            "any_standalone_ctp_json_spreadsheet_nifti_zip_sah_ct_archive_3dra_cta_csv_vwe_csv_image_mesh_or_field_payload_accessed"
        ]
        is not False
        or longitudinal_audit["executable_p0_registered"] is not False
        or longitudinal_audit["method_selected"] is not False
        or longitudinal_audit["architecture_selected"] is not False
        or longitudinal_audit["gpu_training_authorized"] is not False
        or longitudinal_audit["outer_test_authorized"] is not False
        or longitudinal_audit["submission_identity_active"] is not False
        or longitudinal_audit["execution_server"] != "introai9"
        or longitudinal_audit["observed_introai9_pbs_job_count"] != 0
        or longitudinal_audit["pbs_job_created"] is not False
        or longitudinal_audit["login_node_gpu_command_executed"] is not False
        or longitudinal_audit["junjinyong_accessed_for_this_audit"] is not False
        or longitudinal_audit["ctp_dryad_doi"]
        != "10.5061/dryad.0zpc86784"
        or longitudinal_audit["ctp_license"] != "CC0-1.0"
        or longitudinal_audit["ctp_version"] != 7
        or longitudinal_audit["ctp_patients"] != 62
        or longitudinal_audit["ctp_original_exams"] != 291
        or longitudinal_audit["ctp_parametric_maps"] != 873
        or longitudinal_audit["ctp_parameters"] != ["TMax", "CBF", "MTT"]
        or longitudinal_audit["ctp_dci_events"] != 9
        or longitudinal_audit["ctp_vasospasm_patients"] != 42
        or longitudinal_audit["ctp_mean_original_exams_per_patient"] != 4.69
        or longitudinal_audit["ctp_mean_inter_exam_days"] != 2.8
        or longitudinal_audit["ctp_inter_exam_day_range"] != [0.6, 13.1]
        or longitudinal_audit["ctp_paper_interpolated_exams"] != 302
        or longitudinal_audit["ctp_single_center_single_scanner"] is not True
        or longitudinal_audit["ctp_source_slice_thickness_mm"] != 5.0
        or longitudinal_audit["ctp_mni_grid_shape"] != [181, 217, 181]
        or longitudinal_audit["ctp_mni_voxel_mm"] != [1.0, 1.0, 1.0]
        or longitudinal_audit["ctp_observation_process_clinically_informative"]
        is not True
        or longitudinal_audit["ctp_guided_rescue_treatment_reported"] is not True
        or longitudinal_audit["unobserved_untreated_trajectory_identified"]
        is not False
        or longitudinal_audit["scan_policy_utility_released"] is not False
        or longitudinal_audit["figshare_3dra_cta_doi"]
        != "10.6084/m9.figshare.1354056.v3"
        or longitudinal_audit["figshare_3dra_cta_effective_aneurysms"] != 10
        or longitudinal_audit["figshare_3dra_cta_released_files"] != 1
        or longitudinal_audit["figshare_3dra_cta_released_csv_bytes"] != 2516
        or longitudinal_audit[
            "figshare_3dra_cta_source_images_meshes_or_fields_released"
        ]
        is not False
        or longitudinal_audit["vwe_dryad_doi"]
        != "10.5061/dryad.p2ngf1vrg"
        or longitudinal_audit["vwe_unruptured_aneurysms"] != 41
        or longitudinal_audit["vwe_released_files"] != 1
        or longitudinal_audit["vwe_released_csv_bytes"] != 3572
        or longitudinal_audit["vwe_mri_volumes_surfaces_or_spatial_maps_released"]
        is not False
        or longitudinal_audit["sah_segmentation_zenodo_doi"]
        != "10.5281/zenodo.8228847"
        or longitudinal_audit["sah_segmentation_record_license_present"]
        is not False
        or observed_longitudinal_scores != expected_longitudinal_scores
        or not longitudinal_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in longitudinal_audit["candidates"]
        )
        or longitudinal_audit["decision"]
        != "reject_all_without_score_repair_or_standalone_ctp_spreadsheet_nifti_zip_sah_ct_3dra_cta_vwe_payload_p0_method_architecture_pbs_or_gpu"
        or longitudinal_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_with_independent_patient_units_prospective_prediction_time_and_policy_independent_labels_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The longitudinal-perfusion audit must preserve all six frozen "
            "source-only rejections, the 31.0/40 maximum, 62 patients and nine "
            "DCI events, no standalone payload/P0/model/PBS/GPU, and "
            "introai9-only execution."
        )
    checks.append("longitudinal-perfusion rejection and introai9-only boundary")

    mra_growth_audit = problem_selection["longitudinal_mra_growth_source_audit"]
    _require_keys(
        mra_growth_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "official_article_openneuro_git_tree_tags_commits_and_dataset_description_accessed",
            "any_openneuro_annotation_spreadsheet_participant_table_acquisition_sidecar_nifti_segmentation_slicer_scene_or_stl_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_or_job_query_performed_for_this_audit",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "openneuro_dataset_id",
            "paper_linked_version",
            "paper_linked_commit",
            "current_audited_version",
            "current_audited_commit",
            "license",
            "patients",
            "aneurysms",
            "longitudinal_patients",
            "raw_angio_paths",
            "same_session_multi_acquisition_patients",
            "same_session_multi_acquisition_subject_sessions",
            "expert_derivative_sessions_per_subject_maximum",
            "bayesian_direct_prior_public_patients_retained",
            "bayesian_direct_prior_public_aneurysms_retained",
            "bayesian_direct_prior_public_growth_positives",
            "bayesian_direct_prior_public_auc",
            "bayesian_direct_prior_public_loocv_auc",
            "bayesian_direct_prior_public_loocv_kappa",
            "large_clinical_growth_patients",
            "large_clinical_growth_aneurysms",
            "large_clinical_growth_imaging_observations",
            "large_clinical_growth_standardized_threshold",
            "large_clinical_growth_public_learning_asset",
            "awe_long_term_patients",
            "awe_long_term_aneurysms",
            "awe_long_term_instability_events",
            "awe_public_patient_imaging_asset",
            "miniflow_patients",
            "miniflow_aneurysms",
            "miniflow_public_patient_imaging_asset",
            "pcom_virtual_angiography_aneurysms",
            "pcom_longitudinal_stable",
            "pcom_longitudinal_unstable",
            "pcom_public_casewise_mesh_field_or_virtual_angiography_asset",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.longitudinal_mra_growth_source_audit",
    )
    expected_mra_growth_scores = {
        "acquisition_orbit_calibrated_longitudinal_mra_growth_detection": 31.5,
        "single_anchor_weakly_supervised_local_growth_localization": 29.0,
        "interval_censored_mra_growth_trajectory_forecasting": 30.0,
        "mixed_modality_clinical_growth_measurement_harmonization": 26.5,
        "awe_conditioned_long_term_instability_prediction": 26.5,
        "same_day_post_flow_diverter_multimodal_disagreement_modeling": 26.0,
    }
    observed_mra_growth_scores = {
        candidate["id"]: candidate["score"]
        for candidate in mra_growth_audit["candidates"]
    }
    mra_growth_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in mra_growth_audit["candidates"]
    )
    if (
        mra_growth_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or mra_growth_audit["audit_document"]
        != "docs/longitudinal-mra-growth-source-audit-2026-08-10.md"
        or mra_growth_audit["automatic_selection_threshold"] != 32.0
        or mra_growth_audit["best_candidate_id"]
        != "acquisition_orbit_calibrated_longitudinal_mra_growth_detection"
        or mra_growth_audit["best_score"] != 31.5
        or mra_growth_audit["best_score"]
        >= mra_growth_audit["automatic_selection_threshold"]
        or mra_growth_audit["active_shortlist_count"] != 0
        or mra_growth_audit["primary_problem_selected"] is not False
        or mra_growth_audit[
            "official_article_openneuro_git_tree_tags_commits_and_dataset_description_accessed"
        ]
        is not True
        or mra_growth_audit[
            "any_openneuro_annotation_spreadsheet_participant_table_acquisition_sidecar_nifti_segmentation_slicer_scene_or_stl_payload_accessed"
        ]
        is not False
        or mra_growth_audit["executable_p0_registered"] is not False
        or mra_growth_audit["method_selected"] is not False
        or mra_growth_audit["architecture_selected"] is not False
        or mra_growth_audit["gpu_training_authorized"] is not False
        or mra_growth_audit["outer_test_authorized"] is not False
        or mra_growth_audit["submission_identity_active"] is not False
        or mra_growth_audit["execution_server"] != "introai9"
        or mra_growth_audit["introai9_connection_or_job_query_performed_for_this_audit"]
        is not False
        or mra_growth_audit["pbs_job_created"] is not False
        or mra_growth_audit["login_node_gpu_command_executed"] is not False
        or mra_growth_audit["junjinyong_accessed_for_this_audit"] is not False
        or mra_growth_audit["openneuro_dataset_id"] != "ds005096"
        or mra_growth_audit["paper_linked_version"] != "1.0.0"
        or mra_growth_audit["paper_linked_commit"]
        != "645f8579ca0dbbf62edf0275bf35f104f66a2f41"
        or mra_growth_audit["current_audited_version"] != "1.0.3"
        or mra_growth_audit["current_audited_commit"]
        != "0760bf865612600c4eee85f6f437aefaeb534204"
        or mra_growth_audit["license"] != "CC0"
        or mra_growth_audit["patients"] != 63
        or mra_growth_audit["aneurysms"] != 85
        or mra_growth_audit["longitudinal_patients"] != 24
        or mra_growth_audit["raw_angio_paths"] != 126
        or mra_growth_audit["same_session_multi_acquisition_patients"] != 4
        or mra_growth_audit["same_session_multi_acquisition_subject_sessions"]
        != [
            "sub-006/ses-20141026",
            "sub-013/ses-20171118",
            "sub-015/ses-20121216",
            "sub-028/ses-20080621",
        ]
        or mra_growth_audit["expert_derivative_sessions_per_subject_maximum"] != 1
        or mra_growth_audit["bayesian_direct_prior_public_patients_retained"] != 16
        or mra_growth_audit["bayesian_direct_prior_public_aneurysms_retained"] != 19
        or mra_growth_audit["bayesian_direct_prior_public_growth_positives"] != 6
        or mra_growth_audit["large_clinical_growth_public_learning_asset"]
        is not False
        or mra_growth_audit["awe_public_patient_imaging_asset"] is not False
        or mra_growth_audit["miniflow_public_patient_imaging_asset"] is not False
        or mra_growth_audit[
            "pcom_public_casewise_mesh_field_or_virtual_angiography_asset"
        ]
        is not False
        or observed_mra_growth_scores != expected_mra_growth_scores
        or not mra_growth_axis_sums_match
        or any(candidate["payload_accessed"] for candidate in mra_growth_audit["candidates"])
        or mra_growth_audit["decision"]
        != "reject_all_without_score_repair_or_openneuro_annotation_spreadsheet_participant_table_sidecar_nifti_segmentation_slicer_scene_stl_p0_method_architecture_pbs_or_gpu"
        or mra_growth_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_with_a_materially_larger_independent_same_session_control_cohort_or_an_external_longitudinal_image_cohort_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The longitudinal-MRA-growth audit must preserve all six frozen "
            "source-only rejections, the 31.5/40 maximum, four same-session "
            "controls, no payload/P0/model/PBS/GPU, and introai9-only execution."
        )
    checks.append("longitudinal-MRA-growth rejection and introai9-only boundary")

    lineage_audit = problem_selection["aneumo_lineage_split_source_audit"]
    _require_keys(
        lineage_audit,
        [
            "status",
            "audit_document",
            "p0_config",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_source_shortlist_count",
            "primary_problem_selected",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "pbs_job_created",
            "gpu_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "github_source_commit",
            "huggingface_source_commit",
            "mapping_rows",
            "base_families",
            "official_train_cases",
            "official_train_families",
            "official_validation_cases",
            "official_validation_families",
            "official_exact_case_overlap",
            "official_base_family_overlap",
            "official_validation_family_overlap_fraction",
            "github_license_text",
            "huggingface_license_text",
            "license_sources_agree",
            "any_archive_central_directory_or_member_payload_accessed",
            "lfs_object_resolved",
            "p0_source_commit",
            "p0_config_sha256",
            "p0_job_id",
            "p0_final_job_state",
            "p0_exit_status",
            "p0_walltime",
            "p0_cpu_time",
            "p0_completed_small_source_files",
            "p0_partial_small_source_files",
            "p0_result_json_created",
            "p0_raw_scheduler_log_materialized",
            "p0_scientific_gate_evaluated",
            "p0_registered_high_level_checks_evaluated",
            "p0_failure_stage",
            "p0_low_level_cause",
            "p0_same_contract_repair_or_resubmission_allowed",
            "p0_execution_record",
            "p0_execution_record_sha256",
            "candidates",
            "direct_prior_threats",
            "p0_pass_authorizes",
            "decision",
        ],
        "problem_selection.aneumo_lineage_split_source_audit",
    )
    expected_lineage_scores = {
        "generation_family_disjoint_hemodynamic_operator_model_selection": 35.0,
        "geometry_flow_compositional_ood_generalization": 31.5,
        "hierarchical_deformation_vs_family_uncertainty_calibration": 31.0,
        "shape_derivative_informed_deformation_response": 29.0,
        "synthetic_to_real_selection_on_ten_original_cases": 27.0,
        "family_disjoint_transient_wss_forecasting": 29.5,
    }
    observed_lineage_scores = {
        candidate["id"]: candidate["score"]
        for candidate in lineage_audit["candidates"]
    }
    lineage_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in lineage_audit["candidates"]
    )
    if (
        lineage_audit["status"]
        != "closed_after_exact_p0_execution_incomplete_no_scientific_verdict"
        or lineage_audit["audit_document"]
        != "docs/aneumo-lineage-split-source-audit-2026-08-10.md"
        or lineage_audit["p0_config"] != "configs/aneumo_lineage_p0.json"
        or lineage_audit["automatic_selection_threshold"] != 32.0
        or lineage_audit["best_candidate_id"]
        != "generation_family_disjoint_hemodynamic_operator_model_selection"
        or lineage_audit["best_score"] != 35.0
        or lineage_audit["best_score"] < lineage_audit["automatic_selection_threshold"]
        or lineage_audit["active_source_shortlist_count"] != 0
        or lineage_audit["primary_problem_selected"] is not False
        or lineage_audit["method_selected"] is not False
        or lineage_audit["architecture_selected"] is not False
        or lineage_audit["gpu_training_authorized"] is not False
        or lineage_audit["outer_test_authorized"] is not False
        or lineage_audit["submission_identity_active"] is not False
        or lineage_audit["execution_server"] != "introai9"
        or lineage_audit["pbs_job_created"] is not True
        or lineage_audit["gpu_job_created"] is not False
        or lineage_audit["login_node_gpu_command_executed"] is not False
        or lineage_audit["junjinyong_accessed_for_this_audit"] is not False
        or lineage_audit["github_source_commit"]
        != "701d53dde3489d84dbe9bc8324254629162eb45a"
        or lineage_audit["huggingface_source_commit"]
        != "f801adee816c18d3e18b23e6fcb147fe4c264209"
        or lineage_audit["mapping_rows"] != 10660
        or lineage_audit["base_families"] != 427
        or lineage_audit["official_train_cases"] != 160
        or lineage_audit["official_train_families"] != 20
        or lineage_audit["official_validation_cases"] != 40
        or lineage_audit["official_validation_families"] != 20
        or lineage_audit["official_exact_case_overlap"] != 0
        or lineage_audit["official_base_family_overlap"] != 20
        or lineage_audit["official_validation_family_overlap_fraction"] != 1.0
        or lineage_audit["github_license_text"] != "CC_BY_4_0"
        or lineage_audit["huggingface_license_text"] != "CC_BY_NC_ND_4_0"
        or lineage_audit["license_sources_agree"] is not False
        or lineage_audit["any_archive_central_directory_or_member_payload_accessed"]
        is not False
        or lineage_audit["lfs_object_resolved"] is not False
        or lineage_audit["p0_source_commit"]
        != "d3eb3d344d284aaae42db1490f2946d54c94029e"
        or lineage_audit["p0_config_sha256"]
        != "7f14e29a7208f9d2f62552fc485ab6e5e5dbee6f28c4b5ceba2398d7b32f3f77"
        or lineage_audit["p0_job_id"] != "115386.ECE-util1"
        or lineage_audit["p0_final_job_state"] != "F"
        or lineage_audit["p0_exit_status"] != -29
        or lineage_audit["p0_walltime"] != "00:20:36"
        or lineage_audit["p0_cpu_time"] != "00:00:00"
        or lineage_audit["p0_completed_small_source_files"] != 0
        or lineage_audit["p0_partial_small_source_files"] != 0
        or lineage_audit["p0_result_json_created"] is not False
        or lineage_audit["p0_raw_scheduler_log_materialized"] is not False
        or lineage_audit["p0_scientific_gate_evaluated"] is not False
        or lineage_audit["p0_registered_high_level_checks_evaluated"] != 0
        or lineage_audit["p0_failure_stage"]
        != "before_first_preregistered_small_source_completed"
        or lineage_audit["p0_low_level_cause"]
        != "unresolved_without_raw_log_or_result_json"
        or lineage_audit["p0_same_contract_repair_or_resubmission_allowed"]
        is not False
        or lineage_audit["p0_execution_record"]
        != "results/aneumo_lineage_p0_execution_20260810.json"
        or lineage_audit["p0_execution_record_sha256"]
        != "c10c65766f0f0564cbddb911f10c32a03eb41f4aa7e8adbff99094cb5ad7b30d"
        or observed_lineage_scores != expected_lineage_scores
        or not lineage_axis_sums_match
        or lineage_audit["p0_pass_authorizes"]
        != "seek_publisher_license_clarification_then_register_one_method_free_p1_only_if_a_single_pinned_license_is_unambiguous"
        or lineage_audit["decision"]
        != "close_this_exact_candidate_version_after_execution_incomplete_without_transport_repair_rerun_p1_method_architecture_gpu_outer_test_or_scientific_claim"
    ):
        raise ProtocolError(
            "The Aneumo generation-lineage audit must preserve the frozen 35/40 "
            "source admission history, exact train/validation family overlap, "
            "license conflict, introai9 CPU P0 execution-incomplete record, no "
            "rerun, and no model/GPU/outer-test boundary."
        )
    checks.append("closed Aneumo generation-lineage metadata-P0 boundary")

    failure_biology_audit = problem_selection[
        "failure_mechanism_biology_source_audit"
    ]
    _require_keys(
        failure_biology_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "any_image_mask_histology_spatial_transcriptomic_patient_table_or_controlled_payload_accessed",
            "user_accepted_rsna_or_topaneu_terms_verified",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "anatomy_fp_open_training_ctas",
            "anatomy_fp_open_training_aneurysms",
            "anatomy_fp_private_test_ctas",
            "anatomy_fp_public_rsna_test_ctas",
            "anatomy_fp_casewise_cause_labels_public",
            "rsna_registry_scans_minimum",
            "rsna_registry_institutions",
            "rsna_access",
            "topaneu_current_total_scans_approximate",
            "topaneu_current_location_classes_minimum",
            "topaneu_open_use_with_attribution_stated",
            "topaneu_verified_account_required",
            "topaneu_payload_accessed",
            "sect_scanner_manufacturers",
            "sect_exact_curated_manifest_publicly_identified",
            "spatial_atlas_total_aneurysms",
            "spatial_atlas_total_control_vessels",
            "spatial_atlas_aneurysm_donors",
            "spatial_atlas_control_donors",
            "paired_preoperative_imaging_tissue_coordinate_manifest_found",
            "preclinical_ingrowth_histology_images",
            "preclinical_ingrowth_dataset_public",
            "paired_angiography_histology_manifest_public",
            "ican_public_table_is_simulated",
            "ican_public_medical_images",
            "cleo_real_multicenter_records",
            "cleo_formal_differential_privacy_guarantee",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.failure_mechanism_biology_source_audit",
    )
    expected_failure_biology_scores = {
        "cause_specific_false_positive_risk_control": 30.5,
        "topaneu_post_release_attachment_consistency": 29.0,
        "directional_topology_small_lesion_bifurcation_error_control": 28.0,
        "synthetic_avatar_structural_fidelity_for_rupture_status": 25.5,
        "angiography_to_preclinical_tissue_ingrowth_translation": 24.5,
        "imaging_to_spatial_wall_cell_state_alignment": 21.0,
    }
    observed_failure_biology_scores = {
        candidate["id"]: candidate["score"]
        for candidate in failure_biology_audit["candidates"]
    }
    failure_biology_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in failure_biology_audit["candidates"]
    )
    if (
        failure_biology_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or failure_biology_audit["audit_document"]
        != "docs/failure-mechanism-biology-source-audit-2026-08-10.md"
        or failure_biology_audit["automatic_selection_threshold"] != 32.0
        or failure_biology_audit["best_candidate_id"]
        != "cause_specific_false_positive_risk_control"
        or failure_biology_audit["best_score"] != 30.5
        or failure_biology_audit["best_score"]
        >= failure_biology_audit["automatic_selection_threshold"]
        or failure_biology_audit["active_shortlist_count"] != 0
        or failure_biology_audit["primary_problem_selected"] is not False
        or failure_biology_audit[
            "any_image_mask_histology_spatial_transcriptomic_patient_table_or_controlled_payload_accessed"
        ]
        is not False
        or failure_biology_audit["user_accepted_rsna_or_topaneu_terms_verified"]
        is not False
        or failure_biology_audit["executable_p0_registered"] is not False
        or failure_biology_audit["method_selected"] is not False
        or failure_biology_audit["architecture_selected"] is not False
        or failure_biology_audit["gpu_training_authorized"] is not False
        or failure_biology_audit["outer_test_authorized"] is not False
        or failure_biology_audit["submission_identity_active"] is not False
        or failure_biology_audit["execution_server"] != "introai9"
        or failure_biology_audit["pbs_job_created"] is not False
        or failure_biology_audit["login_node_gpu_command_executed"] is not False
        or failure_biology_audit["junjinyong_accessed_for_this_audit"] is not False
        or failure_biology_audit["anatomy_fp_open_training_ctas"] != 1186
        or failure_biology_audit["anatomy_fp_open_training_aneurysms"] != 1373
        or failure_biology_audit["anatomy_fp_private_test_ctas"] != 143
        or failure_biology_audit["anatomy_fp_public_rsna_test_ctas"] != 843
        or failure_biology_audit["anatomy_fp_casewise_cause_labels_public"]
        is not False
        or failure_biology_audit["rsna_registry_scans_minimum"] != 4000
        or failure_biology_audit["rsna_registry_institutions"] != 18
        or failure_biology_audit["rsna_access"]
        != "controlled_noncommercial_no_redistribution"
        or failure_biology_audit["topaneu_current_total_scans_approximate"] != 850
        or failure_biology_audit["topaneu_current_location_classes_minimum"] != 50
        or failure_biology_audit["topaneu_open_use_with_attribution_stated"]
        is not True
        or failure_biology_audit["topaneu_verified_account_required"] is not True
        or failure_biology_audit["topaneu_payload_accessed"] is not False
        or failure_biology_audit["sect_scanner_manufacturers"] != 4
        or failure_biology_audit["sect_exact_curated_manifest_publicly_identified"]
        is not False
        or failure_biology_audit["spatial_atlas_total_aneurysms"] != 14
        or failure_biology_audit["spatial_atlas_total_control_vessels"] != 11
        or failure_biology_audit["spatial_atlas_aneurysm_donors"] != 6
        or failure_biology_audit["spatial_atlas_control_donors"] != 3
        or failure_biology_audit[
            "paired_preoperative_imaging_tissue_coordinate_manifest_found"
        ]
        is not False
        or failure_biology_audit["preclinical_ingrowth_histology_images"] != 64
        or failure_biology_audit["preclinical_ingrowth_dataset_public"] is not False
        or failure_biology_audit["paired_angiography_histology_manifest_public"]
        is not False
        or failure_biology_audit["ican_public_table_is_simulated"] is not True
        or failure_biology_audit["ican_public_medical_images"] is not False
        or failure_biology_audit["cleo_real_multicenter_records"] != 1035
        or failure_biology_audit["cleo_formal_differential_privacy_guarantee"]
        is not False
        or observed_failure_biology_scores != expected_failure_biology_scores
        or not failure_biology_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in failure_biology_audit["candidates"]
        )
        or failure_biology_audit["decision"]
        != "reject_all_without_score_repair_image_mask_histology_spatial_transcriptomic_patient_table_controlled_payload_p0_method_architecture_pbs_or_gpu"
        or failure_biology_audit["next_allowed_action"]
        != "monitor_genuinely_new_or_revised_primary_sources_with_public_casewise_error_or_paired_imaging_biology_endpoints_and_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The failure-mechanism/biology audit must retain all six frozen "
            "source-only rejections, the 30.5/40 maximum, no payload/P0/model/"
            "PBS/GPU, and the introai9-only execution boundary."
        )
    checks.append("failure-mechanism/biology rejection and introai9-only boundary")

    reconstruction_audit = problem_selection[
        "reconstruction_annotation_reliability_source_audit"
    ]
    _require_keys(
        reconstruction_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_id",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "any_patient_dicom_nifti_mask_mesh_projection_cfd_or_phantom_payload_accessed",
            "article_supplementary_document_read",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "di_noto_dataset_id",
            "di_noto_total_subjects",
            "di_noto_patients",
            "di_noto_controls",
            "di_noto_aneurysms",
            "di_noto_reported_weak_label_speedup",
            "vp_unet_coarse_label_subjects",
            "vp_unet_precise_label_test_subjects",
            "vp_unet_external_adam_subjects",
            "same_subject_prospective_real_weak_and_independent_precise_annotation_manifest_public",
            "weakmed_tasks",
            "weakmed_datasets",
            "weakmed_modalities",
            "reconstruction_variability_patient_dsas",
            "reconstruction_variability_models",
            "reconstruction_variability_software_platforms",
            "reconstruction_variability_thresholds",
            "reconstruction_variability_users",
            "reconstruction_variability_max_user_percent_difference",
            "reconstruction_variability_patient_mesh_table_public",
            "ultrasparse_dsa_patients",
            "ultrasparse_dsa_projection_counts",
            "ultrasparse_dsa_aneurysms_identified_at_eight_views",
            "ultrasparse_dsa_raw_patient_projection_data_public",
            "biplane_isuia_aneurysms",
            "biplane_unidentifiable_neck_aneurysms",
            "biplane_volumetric_validation_models",
            "phantomx_axial_images",
            "phantomx_series",
            "phantomx_dose_levels",
            "phantomx_reconstruction_methods",
            "phantomx_aneurysms",
            "phantomx_effective_anatomies",
            "autocar_clinical_imaging_parameter_cases_minimum",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.reconstruction_annotation_reliability_source_audit",
    )
    expected_reconstruction_scores = {
        "one_sided_outer_annotation_morphometry_sets": 31.5,
        "sparse_view_dsa_neck_risk_reconstruction": 29.5,
        "segmentation_software_threshold_orbit_calibrated_morphometry": 29.0,
        "dose_reconstruction_phantom_aneurysm_consistency": 26.5,
        "biplane_shape_posterior_for_neck_and_lobulation": 25.5,
        "reconstruction_induced_hemodynamic_risk_propagation": 25.5,
    }
    observed_reconstruction_scores = {
        candidate["id"]: candidate["score"]
        for candidate in reconstruction_audit["candidates"]
    }
    reconstruction_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in reconstruction_audit["candidates"]
    )
    if (
        reconstruction_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or reconstruction_audit["audit_document"]
        != "docs/reconstruction-annotation-reliability-source-audit-2026-08-10.md"
        or reconstruction_audit["automatic_selection_threshold"] != 32.0
        or reconstruction_audit["best_candidate_id"]
        != "one_sided_outer_annotation_morphometry_sets"
        or reconstruction_audit["best_score"] != 31.5
        or reconstruction_audit["best_score"]
        >= reconstruction_audit["automatic_selection_threshold"]
        or reconstruction_audit["active_shortlist_count"] != 0
        or reconstruction_audit["primary_problem_selected"] is not False
        or reconstruction_audit[
            "any_patient_dicom_nifti_mask_mesh_projection_cfd_or_phantom_payload_accessed"
        ]
        is not False
        or reconstruction_audit["article_supplementary_document_read"] is not True
        or reconstruction_audit["executable_p0_registered"] is not False
        or reconstruction_audit["method_selected"] is not False
        or reconstruction_audit["architecture_selected"] is not False
        or reconstruction_audit["gpu_training_authorized"] is not False
        or reconstruction_audit["outer_test_authorized"] is not False
        or reconstruction_audit["submission_identity_active"] is not False
        or reconstruction_audit["execution_server"] != "introai9"
        or reconstruction_audit["pbs_job_created"] is not False
        or reconstruction_audit["login_node_gpu_command_executed"] is not False
        or reconstruction_audit["junjinyong_accessed_for_this_audit"] is not False
        or reconstruction_audit["di_noto_dataset_id"] != "openneuro_ds003949"
        or reconstruction_audit["di_noto_total_subjects"] != 284
        or reconstruction_audit["di_noto_patients"] != 157
        or reconstruction_audit["di_noto_controls"] != 127
        or reconstruction_audit["di_noto_aneurysms"] != 198
        or reconstruction_audit["di_noto_reported_weak_label_speedup"] != 4.0
        or reconstruction_audit["vp_unet_coarse_label_subjects"] != 246
        or reconstruction_audit["vp_unet_precise_label_test_subjects"] != 38
        or reconstruction_audit["vp_unet_external_adam_subjects"] != 113
        or reconstruction_audit[
            "same_subject_prospective_real_weak_and_independent_precise_annotation_manifest_public"
        ]
        is not False
        or reconstruction_audit["weakmed_tasks"] != 9
        or reconstruction_audit["weakmed_datasets"] != 9
        or reconstruction_audit["weakmed_modalities"] != 6
        or reconstruction_audit["reconstruction_variability_patient_dsas"] != 100
        or reconstruction_audit["reconstruction_variability_models"] != 600
        or reconstruction_audit["reconstruction_variability_software_platforms"]
        != 2
        or reconstruction_audit["reconstruction_variability_thresholds"] != 3
        or reconstruction_audit["reconstruction_variability_users"] != 3
        or reconstruction_audit[
            "reconstruction_variability_max_user_percent_difference"
        ]
        != 22.7
        or reconstruction_audit["reconstruction_variability_patient_mesh_table_public"]
        is not False
        or reconstruction_audit["ultrasparse_dsa_patients"] != 202
        or reconstruction_audit["ultrasparse_dsa_projection_counts"]
        != [4, 6, 8, 10, 12]
        or reconstruction_audit[
            "ultrasparse_dsa_aneurysms_identified_at_eight_views"
        ]
        != 82
        or reconstruction_audit["ultrasparse_dsa_raw_patient_projection_data_public"]
        is not False
        or reconstruction_audit["biplane_isuia_aneurysms"] != 150
        or reconstruction_audit["biplane_unidentifiable_neck_aneurysms"] != 23
        or reconstruction_audit["biplane_volumetric_validation_models"] != 10
        or reconstruction_audit["phantomx_axial_images"] != 39000
        or reconstruction_audit["phantomx_series"] != 120
        or reconstruction_audit["phantomx_dose_levels"] != 30
        or reconstruction_audit["phantomx_reconstruction_methods"] != 4
        or reconstruction_audit["phantomx_aneurysms"] != 3
        or reconstruction_audit["phantomx_effective_anatomies"] != 1
        or reconstruction_audit["autocar_clinical_imaging_parameter_cases_minimum"]
        != 1000
        or observed_reconstruction_scores != expected_reconstruction_scores
        or not reconstruction_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in reconstruction_audit["candidates"]
        )
        or reconstruction_audit["decision"]
        != "reject_all_without_score_repair_patient_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or reconstruction_audit["next_allowed_action"]
        != "monitor_for_same_subject_paired_annotation_or_reconstruction_orbits_with_independent_reference_then_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The reconstruction/annotation reliability audit must retain all six "
            "frozen source-only rejections, the 31.5/40 maximum, no patient "
            "payload/P0/model/PBS/GPU, and the introai9-only boundary."
        )
    checks.append("reconstruction/annotation rejection and introai9-only boundary")

    method_asset_audit = problem_selection["method_asset_viability_source_audit"]
    _require_keys(
        method_asset_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_ids",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "any_patient_image_mask_mesh_cfd_or_controlled_challenge_payload_accessed",
            "public_article_and_repository_metadata_read",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_remote_user",
            "introai9_observed_host",
            "introai9_pbs_jobs_observed",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "royal_openneuro_main_head",
            "royal_patients",
            "royal_aneurysms",
            "royal_longitudinal_patients",
            "royal_mask_and_stl_are_independent_references",
            "aneug_flow_dataset_main_head",
            "aneug_flow_code_master_head",
            "aneug_flow_material_new_version_found",
            "iavs_main_head",
            "iavs_release_count",
            "iavs_repository_license_present",
            "iavs_payload_or_code_present",
            "rsna_controlled_terms_user_accepted_verified",
            "rsna_per_reader_label_manifest_public",
            "cq500_ia_cited_repository_publicly_resolvable",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.method_asset_viability_source_audit",
    )
    expected_method_asset_scores = {
        "royal_reference_morphometry_certificate_direct_prior_occupied": 30.0,
        "partial_observation_solution_functional_operator_direct_prior_occupied": 30.0,
        "iavs_topology_to_cfd_reliability_unreleased_and_direct_prior_occupied": 29.0,
        "rsna_reader_source_reliability_without_per_reader_manifest": 26.0,
        "cq500_provenance_aware_multimodal_adaptation_without_versioned_annotation_source": 23.0,
    }
    observed_method_asset_scores = {
        candidate["id"]: candidate["score"]
        for candidate in method_asset_audit["candidates"]
    }
    method_asset_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in method_asset_audit["candidates"]
    )
    expected_method_asset_priors = {
        "compass_downstream_segmentation_metric_conformal_intervals_and_shift_weighting",
        "robust_conformal_3d_volume_estimation_under_covariate_shift",
        "neckspline_topology_preserving_neck_morphometry_and_perturbation_uncertainty",
        "spatial_anatomical_and_morphological_conformal_segmentation_sets",
        "neural_operator_processes_for_probabilistic_partial_observation_operator_learning",
        "learned_boundary_function_extensions_for_neural_operators",
        "amortized_conditioning_by_neural_operators",
        "iavs_two_stage_topology_aware_segmentation_and_cfd_applicability",
        "amap_anatomy_guided_pretraining_and_domain_adaptive_prompting",
    }
    if (
        method_asset_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or method_asset_audit["audit_document"]
        != "docs/method-asset-viability-source-audit-2026-08-10.md"
        or method_asset_audit["automatic_selection_threshold"] != 32.0
        or method_asset_audit["best_candidate_ids"]
        != [
            "royal_reference_morphometry_certificate_direct_prior_occupied",
            "partial_observation_solution_functional_operator_direct_prior_occupied",
        ]
        or method_asset_audit["best_score"] != 30.0
        or method_asset_audit["best_score"]
        >= method_asset_audit["automatic_selection_threshold"]
        or method_asset_audit["active_shortlist_count"] != 0
        or method_asset_audit["primary_problem_selected"] is not False
        or method_asset_audit[
            "any_patient_image_mask_mesh_cfd_or_controlled_challenge_payload_accessed"
        ]
        is not False
        or method_asset_audit["public_article_and_repository_metadata_read"]
        is not True
        or method_asset_audit["executable_p0_registered"] is not False
        or method_asset_audit["method_selected"] is not False
        or method_asset_audit["architecture_selected"] is not False
        or method_asset_audit["gpu_training_authorized"] is not False
        or method_asset_audit["outer_test_authorized"] is not False
        or method_asset_audit["submission_identity_active"] is not False
        or method_asset_audit["execution_server"] != "introai9"
        or method_asset_audit["introai9_connection_verified"] is not True
        or method_asset_audit["introai9_remote_user"] != "introai9"
        or method_asset_audit["introai9_observed_host"] != "ECE-util2"
        or method_asset_audit["introai9_pbs_jobs_observed"] != 0
        or method_asset_audit["pbs_job_created"] is not False
        or method_asset_audit["login_node_gpu_command_executed"] is not False
        or method_asset_audit["junjinyong_accessed_for_this_audit"] is not False
        or method_asset_audit["royal_openneuro_main_head"]
        != "0760bf865612600c4eee85f6f437aefaeb534204"
        or method_asset_audit["royal_patients"] != 63
        or method_asset_audit["royal_aneurysms"] != 85
        or method_asset_audit["royal_longitudinal_patients"] != 24
        or method_asset_audit["royal_mask_and_stl_are_independent_references"]
        is not False
        or method_asset_audit["aneug_flow_dataset_main_head"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or method_asset_audit["aneug_flow_code_master_head"]
        != "4a090a0f12538deef6fcea88b81afe78ce38152e"
        or method_asset_audit["aneug_flow_material_new_version_found"] is not False
        or method_asset_audit["iavs_main_head"]
        != "2e40088d9eaa671c592929a154b7b2cf99f9320a"
        or method_asset_audit["iavs_release_count"] != 0
        or method_asset_audit["iavs_repository_license_present"] is not False
        or method_asset_audit["iavs_payload_or_code_present"] is not False
        or method_asset_audit["rsna_controlled_terms_user_accepted_verified"]
        is not False
        or method_asset_audit["rsna_per_reader_label_manifest_public"] is not False
        or method_asset_audit["cq500_ia_cited_repository_publicly_resolvable"]
        is not False
        or set(method_asset_audit["direct_prior_threats"])
        != expected_method_asset_priors
        or observed_method_asset_scores != expected_method_asset_scores
        or not method_asset_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in method_asset_audit["candidates"]
        )
        or method_asset_audit["decision"]
        != "reject_all_without_score_repair_patient_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or method_asset_audit["next_allowed_action"]
        != "monitor_material_source_releases_or_a_genuinely_new_identifiable_problem_then_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The method--asset viability audit must retain all five frozen "
            "source-only rejections, the 30/40 maximum, exact public source "
            "heads, no payload/P0/model/PBS/GPU, and introai9-only execution."
        )
    checks.append("method--asset viability rejection and source-version boundary")

    registry_gap_audit = problem_selection["registry_gap_source_audit"]
    _require_keys(
        registry_gap_audit,
        [
            "status",
            "audit_document",
            "official_registry_query",
            "official_registry_records_returned",
            "automatic_selection_threshold",
            "best_candidate_ids",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "official_metadata_and_primary_sources_read",
            "any_csv_pkl_zip_image_wall_map_cfd_case_rna_or_patient_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_remote_user",
            "introai9_pbs_jobs_observed",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "iavs_watch_same_as_frozen_snapshot",
            "iavs_watch_material_change_signals",
            "transiar_test_record",
            "transiar_test_archive_bytes",
            "transiar_test_archive_md5",
            "unlinked_test_record",
            "unlinked_test_blob_bytes",
            "unlinked_test_blob_md5",
            "transiar_retained_patients",
            "transiar_retained_aneurysms",
            "transiar_balanced_test_aneurysms",
            "transiar_imbalanced_test_aneurysms",
            "gn_net_reported_patients",
            "exact_cross_record_case_lineage_manifest_public",
            "public_test_payload_accessed",
            "vwe_record",
            "vwe_unruptured_aneurysms",
            "vwe_csv_bytes",
            "vwe_csv_md5",
            "vwe_observed_future_instability_endpoint_present",
            "vwe_image_wall_map_or_cfd_field_public",
            "transcriptomic_record",
            "transcriptomic_discovery_labeled_aneurysms",
            "transcriptomic_discovery_ruptured",
            "transcriptomic_discovery_unruptured",
            "transcriptomic_raw_geo_included",
            "transcriptomic_casewise_imaging_bridge_public",
            "autopsy_record",
            "autopsy_adults",
            "autopsy_aneurysm_cases",
            "autopsy_casewise_table_or_imaging_public",
            "vortex_cfd_record",
            "vortex_cfd_independent_patient_or_experimental_reference_included",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.registry_gap_source_audit",
    )
    expected_registry_gap_scores = {
        "public_test_only_rupture_status_reuse_direct_prior_and_lineage_unresolved": 26.5,
        "scalar_vwe_hemodynamic_association_without_instability_endpoint_or_fields": 26.0,
        "open_cfd_pipeline_numerical_certificate_without_independent_reference": 26.0,
        "cross_cohort_rupture_transcriptomic_core_without_imaging_bridge": 25.5,
        "autopsy_circle_of_willis_variant_geometry_prior_without_casewise_asset": 23.5,
    }
    observed_registry_gap_scores = {
        candidate["id"]: candidate["score"]
        for candidate in registry_gap_audit["candidates"]
    }
    registry_gap_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in registry_gap_audit["candidates"]
    )
    expected_registry_gap_priors = {
        "transiar_multiscale_3d_branch_transformer_and_anatomical_features",
        "gn_net_geometric_and_neighborhood_aware_rupture_status_model",
        "vwe_hemodynamic_risk_metric_correlation_analysis",
        "three_dimensional_vwe_mapping_and_enhancement_area_workflows",
        "multi_cohort_geo_immune_signature_and_rupture_status_models",
        "anatomy_aware_detection_centerline_graphs_and_fine_vessel_taxonomies",
        "standard_openfoam_pulsatile_cfd_and_biomarker_extraction",
    }
    if (
        registry_gap_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or registry_gap_audit["audit_document"]
        != "docs/registry-gap-source-audit-2026-08-10.md"
        or registry_gap_audit["official_registry_query"]
        != "zenodo_metadata_title_exact_phrase_intracranial_aneurysm_sorted_most_recent"
        or registry_gap_audit["official_registry_records_returned"] != 49
        or registry_gap_audit["automatic_selection_threshold"] != 32.0
        or registry_gap_audit["best_candidate_ids"]
        != ["public_test_only_rupture_status_reuse_direct_prior_and_lineage_unresolved"]
        or registry_gap_audit["best_score"] != 26.5
        or registry_gap_audit["best_score"]
        >= registry_gap_audit["automatic_selection_threshold"]
        or registry_gap_audit["active_shortlist_count"] != 0
        or registry_gap_audit["primary_problem_selected"] is not False
        or registry_gap_audit["official_metadata_and_primary_sources_read"] is not True
        or registry_gap_audit[
            "any_csv_pkl_zip_image_wall_map_cfd_case_rna_or_patient_payload_accessed"
        ]
        is not False
        or registry_gap_audit["executable_p0_registered"] is not False
        or registry_gap_audit["method_selected"] is not False
        or registry_gap_audit["architecture_selected"] is not False
        or registry_gap_audit["gpu_training_authorized"] is not False
        or registry_gap_audit["outer_test_authorized"] is not False
        or registry_gap_audit["submission_identity_active"] is not False
        or registry_gap_audit["execution_server"] != "introai9"
        or registry_gap_audit["introai9_connection_verified"] is not True
        or registry_gap_audit["introai9_remote_user"] != "introai9"
        or registry_gap_audit["introai9_pbs_jobs_observed"] != 0
        or registry_gap_audit["pbs_job_created"] is not False
        or registry_gap_audit["login_node_gpu_command_executed"] is not False
        or registry_gap_audit["junjinyong_accessed_for_this_audit"] is not False
        or registry_gap_audit["iavs_watch_same_as_frozen_snapshot"] is not True
        or registry_gap_audit["iavs_watch_material_change_signals"] != []
        or registry_gap_audit["transiar_test_record"]
        != "10.5281/zenodo.7536330"
        or registry_gap_audit["transiar_test_archive_bytes"] != 578924037
        or registry_gap_audit["transiar_test_archive_md5"]
        != "f0770b8f59306f6db33f5411575020c9"
        or registry_gap_audit["unlinked_test_record"]
        != "10.5281/zenodo.7757069"
        or registry_gap_audit["unlinked_test_blob_bytes"] != 2321552713
        or registry_gap_audit["unlinked_test_blob_md5"]
        != "b579b4368ec7d14c621529554e394c6e"
        or registry_gap_audit["transiar_retained_patients"] != 423
        or registry_gap_audit["transiar_retained_aneurysms"] != 449
        or registry_gap_audit["transiar_balanced_test_aneurysms"] != 82
        or registry_gap_audit["transiar_imbalanced_test_aneurysms"] != 249
        or registry_gap_audit["gn_net_reported_patients"] != 423
        or registry_gap_audit["exact_cross_record_case_lineage_manifest_public"]
        is not False
        or registry_gap_audit["public_test_payload_accessed"] is not False
        or registry_gap_audit["vwe_record"] != "10.5061/dryad.p2ngf1vrg"
        or registry_gap_audit["vwe_unruptured_aneurysms"] != 41
        or registry_gap_audit["vwe_csv_bytes"] != 3572
        or registry_gap_audit["vwe_csv_md5"]
        != "4ba44d3becf0a0f327aa9aa7aede01d2"
        or registry_gap_audit["vwe_observed_future_instability_endpoint_present"]
        is not False
        or registry_gap_audit["vwe_image_wall_map_or_cfd_field_public"] is not False
        or registry_gap_audit["transcriptomic_record"]
        != "10.5281/zenodo.21249929"
        or registry_gap_audit["transcriptomic_discovery_labeled_aneurysms"] != 43
        or registry_gap_audit["transcriptomic_discovery_ruptured"] != 22
        or registry_gap_audit["transcriptomic_discovery_unruptured"] != 21
        or registry_gap_audit["transcriptomic_raw_geo_included"] is not False
        or registry_gap_audit["transcriptomic_casewise_imaging_bridge_public"]
        is not False
        or registry_gap_audit["autopsy_record"] != "10.5281/zenodo.15692542"
        or registry_gap_audit["autopsy_adults"] != 221
        or registry_gap_audit["autopsy_aneurysm_cases"] != 29
        or registry_gap_audit["autopsy_casewise_table_or_imaging_public"]
        is not False
        or registry_gap_audit["vortex_cfd_record"]
        != "10.5281/zenodo.20732293"
        or registry_gap_audit[
            "vortex_cfd_independent_patient_or_experimental_reference_included"
        ]
        is not False
        or set(registry_gap_audit["direct_prior_threats"])
        != expected_registry_gap_priors
        or observed_registry_gap_scores != expected_registry_gap_scores
        or not registry_gap_axis_sums_match
        or any(candidate["payload_accessed"] for candidate in registry_gap_audit["candidates"])
        or registry_gap_audit["decision"]
        != "reject_all_without_score_repair_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or registry_gap_audit["next_allowed_action"]
        != "monitor_material_source_changes_or_a_genuinely_new_observable_imaging_endpoint_with_auditable_development_units_and_sealed_outer_test_then_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The registry-gap source audit must retain all five source-only "
            "rejections, the 26.5/40 maximum, exact public metadata, no "
            "payload/P0/model/PBS/GPU, and introai9-only execution."
        )
    checks.append("registry-gap rejection and public-test sealing boundary")

    broad_registry_audit = problem_selection["broad_registry_source_audit"]
    _require_keys(
        broad_registry_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "search_boundaries",
            "best_candidate_ids",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "official_metadata_file_manifests_and_primary_sources_read",
            "any_patient_image_mesh_spreadsheet_document_or_model_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_remote_user",
            "introai9_observed_host",
            "introai9_pbs_jobs_observed",
            "introai9_name_level_source_scan_result_artifact_created",
            "introai9_candidate_asset_presence_conclusion",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "largeia_record",
            "largeia_access_state",
            "largeia_internal_cta_studies",
            "largeia_internal_aneurysms",
            "largeia_internal_institutions",
            "largeia_external_cta_studies",
            "largeia_external_aneurysms",
            "largeia_external_institutions",
            "largeia_voxelwise_masks_age_sex_rupture_status_reported",
            "largeia_user_access_request_or_terms_completed",
            "largeia_payload_accessed",
            "largeia_public_reader_adjudication_and_sealed_outer_test_manifest",
            "cfd_challenge_figshare_record",
            "cfd_challenge_independent_aneurysm_anatomies",
            "cfd_challenge_submitted_datasets",
            "cfd_challenge_teams",
            "cfd_challenge_dicom_wss_segmentation_or_velocity_payload_accessed",
            "cfd_challenge_primary_paper_already_quantifies_whole_pipeline_variability",
            "cfd_challenge_sac_average_wss_iqr_maximum_percent",
            "cfd_challenge_normalized_sac_average_wss_iqr_below_percent",
            "rupture_destined_figshare_records",
            "rupture_destined_supplement_duplicate_md5",
            "rupture_destined_patients",
            "rupture_destined_aneurysms",
            "longitudinal_unruptured_patients",
            "longitudinal_unruptured_aneurysms",
            "rupture_destined_delta_sig_ratio_auc",
            "rupture_destined_size_ratio_auc",
            "rupture_destined_casewise_image_mesh_or_measurement_table_public",
            "asah_hydrocephalus_figshare_record",
            "asah_hydrocephalus_development_patients",
            "asah_hydrocephalus_external_patients",
            "asah_hydrocephalus_development_auc",
            "asah_hydrocephalus_external_auc",
            "asah_hydrocephalus_patient_level_image_or_time_series_public",
            "vwi_habitat_figshare_record",
            "vwi_habitat_patients",
            "vwi_habitat_aneurysms",
            "vwi_habitat_stable_aneurysms",
            "vwi_habitat_unstable_aneurysms",
            "vwi_habitat_validation_auc",
            "vwi_habitat_raw_vwi_segmentation_or_case_manifest_public",
            "synthetic_dsa_record",
            "synthetic_dsa_embargo_end",
            "synthetic_dsa_images_reported",
            "synthetic_dsa_generation_runs",
            "synthetic_dsa_views_per_run",
            "synthetic_dsa_original_patient_dsa_released",
            "synthetic_dsa_payload_accessed",
            "low_quality_cta_restoration_direct_prior_record",
            "direct_prior_threats",
            "candidates",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.broad_registry_source_audit",
    )
    expected_broad_registry_scores = {
        "multicenter_study_level_lesion_set_risk_control": 30.5,
        "solver_population_calibrated_hemodynamic_functionals": 29.5,
        "rupture_destined_longitudinal_sig_forecasting": 26.0,
        "asah_day21_hydrocephalus_dynamic_imaging": 26.0,
        "vwi_habitat_instability_reanalysis": 24.5,
        "synthetic_dsa_reader_realism": 18.0,
    }
    observed_broad_registry_scores = {
        candidate["id"]: candidate["score"]
        for candidate in broad_registry_audit["candidates"]
    }
    broad_registry_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in broad_registry_audit["candidates"]
    )
    expected_broad_registry_priors = {
        "glia_net_global_localization_and_fine_3d_segmentation",
        "anatomy_aware_centerline_graph_and_global_local_aneurysm_detection",
        "conformal_risk_control_and_sequential_conformal_object_detection",
        "conformal_prediction_sets_for_instance_segmentation",
        "cfd_challenge_whole_pipeline_wss_variability_analysis",
        "match_segmentation_to_hemodynamic_variability",
        "generic_probabilistic_multifidelity_neural_operator_uncertainty",
        "primary_sig_geometry_hemodynamic_rupture_destined_analysis",
        "primary_vwi_habitat_transformer_instability_prediction",
        "primary_dynamic_asah_hydrocephalus_prediction",
        "physics_grounded_synthetic_supervision_for_ct_restoration",
    }
    expected_search_boundaries = {
        "zenodo_broad_query_total_records": 1226,
        "zenodo_recent_records_screened": 100,
        "datacite_intracranial_aneurysm_dataset_total_records": 196,
        "figshare_records_screened": 100,
        "dryad_records_screened_approximately": 20,
        "prior_exact_title_zenodo_records": 49,
    }
    if (
        broad_registry_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or broad_registry_audit["audit_document"]
        != "docs/broad-registry-source-audit-2026-08-10.md"
        or broad_registry_audit["automatic_selection_threshold"] != 32.0
        or broad_registry_audit["search_boundaries"] != expected_search_boundaries
        or broad_registry_audit["best_candidate_ids"]
        != ["multicenter_study_level_lesion_set_risk_control"]
        or broad_registry_audit["best_score"] != 30.5
        or broad_registry_audit["best_score"]
        >= broad_registry_audit["automatic_selection_threshold"]
        or broad_registry_audit["active_shortlist_count"] != 0
        or broad_registry_audit["primary_problem_selected"] is not False
        or broad_registry_audit[
            "official_metadata_file_manifests_and_primary_sources_read"
        ]
        is not True
        or broad_registry_audit[
            "any_patient_image_mesh_spreadsheet_document_or_model_payload_accessed"
        ]
        is not False
        or broad_registry_audit["executable_p0_registered"] is not False
        or broad_registry_audit["method_selected"] is not False
        or broad_registry_audit["architecture_selected"] is not False
        or broad_registry_audit["gpu_training_authorized"] is not False
        or broad_registry_audit["outer_test_authorized"] is not False
        or broad_registry_audit["submission_identity_active"] is not False
        or broad_registry_audit["execution_server"] != "introai9"
        or broad_registry_audit["introai9_connection_verified"] is not True
        or broad_registry_audit["introai9_remote_user"] != "introai9"
        or broad_registry_audit["introai9_observed_host"] != "ECE-util2"
        or broad_registry_audit["introai9_pbs_jobs_observed"] != 0
        or broad_registry_audit[
            "introai9_name_level_source_scan_result_artifact_created"
        ]
        is not False
        or broad_registry_audit["introai9_candidate_asset_presence_conclusion"]
        != "not_established_not_absent"
        or broad_registry_audit["pbs_job_created"] is not False
        or broad_registry_audit["login_node_gpu_command_executed"] is not False
        or broad_registry_audit["junjinyong_accessed_for_this_audit"] is not False
        or broad_registry_audit["largeia_record"] != "10.5281/zenodo.6801398"
        or broad_registry_audit["largeia_access_state"]
        != "restricted_request_required"
        or broad_registry_audit["largeia_internal_cta_studies"] != 1338
        or broad_registry_audit["largeia_internal_aneurysms"] != 1489
        or broad_registry_audit["largeia_internal_institutions"] != 6
        or broad_registry_audit["largeia_external_cta_studies"] != 138
        or broad_registry_audit["largeia_external_aneurysms"] != 101
        or broad_registry_audit["largeia_external_institutions"] != 2
        or broad_registry_audit[
            "largeia_voxelwise_masks_age_sex_rupture_status_reported"
        ]
        is not True
        or broad_registry_audit[
            "largeia_user_access_request_or_terms_completed"
        ]
        is not False
        or broad_registry_audit["largeia_payload_accessed"] is not False
        or broad_registry_audit[
            "largeia_public_reader_adjudication_and_sealed_outer_test_manifest"
        ]
        is not False
        or broad_registry_audit["cfd_challenge_figshare_record"] != "6383516"
        or broad_registry_audit[
            "cfd_challenge_independent_aneurysm_anatomies"
        ]
        != 5
        or broad_registry_audit["cfd_challenge_submitted_datasets"] != 28
        or broad_registry_audit["cfd_challenge_teams"] != 26
        or broad_registry_audit[
            "cfd_challenge_dicom_wss_segmentation_or_velocity_payload_accessed"
        ]
        is not False
        or broad_registry_audit[
            "cfd_challenge_primary_paper_already_quantifies_whole_pipeline_variability"
        ]
        is not True
        or broad_registry_audit[
            "cfd_challenge_sac_average_wss_iqr_maximum_percent"
        ]
        != 56
        or broad_registry_audit[
            "cfd_challenge_normalized_sac_average_wss_iqr_below_percent"
        ]
        != 30
        or broad_registry_audit["rupture_destined_figshare_records"]
        != ["23905128", "23905134", "23905143"]
        or broad_registry_audit["rupture_destined_supplement_duplicate_md5"]
        != "6d1bdb0ab06b75f38ab02ae5faa34912"
        or broad_registry_audit["rupture_destined_patients"] != 20
        or broad_registry_audit["rupture_destined_aneurysms"] != 20
        or broad_registry_audit["longitudinal_unruptured_patients"] != 41
        or broad_registry_audit["longitudinal_unruptured_aneurysms"] != 45
        or broad_registry_audit["rupture_destined_delta_sig_ratio_auc"] != 0.72
        or broad_registry_audit["rupture_destined_size_ratio_auc"] != 0.56
        or broad_registry_audit[
            "rupture_destined_casewise_image_mesh_or_measurement_table_public"
        ]
        is not False
        or broad_registry_audit["asah_hydrocephalus_figshare_record"] != "33077267"
        or broad_registry_audit["asah_hydrocephalus_development_patients"] != 228
        or broad_registry_audit["asah_hydrocephalus_external_patients"] != 102
        or broad_registry_audit["asah_hydrocephalus_development_auc"] != 0.894
        or broad_registry_audit["asah_hydrocephalus_external_auc"] != 0.867
        or broad_registry_audit[
            "asah_hydrocephalus_patient_level_image_or_time_series_public"
        ]
        is not False
        or broad_registry_audit["vwi_habitat_figshare_record"] != "32695140"
        or broad_registry_audit["vwi_habitat_patients"] != 293
        or broad_registry_audit["vwi_habitat_aneurysms"] != 312
        or broad_registry_audit["vwi_habitat_stable_aneurysms"] != 197
        or broad_registry_audit["vwi_habitat_unstable_aneurysms"] != 115
        or broad_registry_audit["vwi_habitat_validation_auc"] != 0.844
        or broad_registry_audit[
            "vwi_habitat_raw_vwi_segmentation_or_case_manifest_public"
        ]
        is not False
        or broad_registry_audit["synthetic_dsa_record"]
        != "10.5281/zenodo.21104782"
        or broad_registry_audit["synthetic_dsa_embargo_end"] != "2026-10-31"
        or broad_registry_audit["synthetic_dsa_images_reported"] != 400
        or broad_registry_audit["synthetic_dsa_generation_runs"] != 10
        or broad_registry_audit["synthetic_dsa_views_per_run"] != 4
        or broad_registry_audit[
            "synthetic_dsa_original_patient_dsa_released"
        ]
        is not False
        or broad_registry_audit["synthetic_dsa_payload_accessed"] is not False
        or broad_registry_audit["low_quality_cta_restoration_direct_prior_record"]
        != "10.5281/zenodo.20754346"
        or set(broad_registry_audit["direct_prior_threats"])
        != expected_broad_registry_priors
        or observed_broad_registry_scores != expected_broad_registry_scores
        or not broad_registry_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in broad_registry_audit["candidates"]
        )
        or not set(expected_broad_registry_scores).issubset(
            set(problem_selection["rejected_candidates"])
        )
        or broad_registry_audit["decision"]
        != "reject_all_without_score_repair_access_request_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or broad_registry_audit["next_allowed_action"]
        != "monitor_material_source_changes_or_a_genuinely_new_observable_imaging_endpoint_with_auditable_development_units_and_sealed_outer_test_then_register_only_a_fresh_candidate_scoring_at_least_32"
    ):
        raise ProtocolError(
            "The broad-registry source audit must retain all six frozen "
            "rejections, the restricted LargeIA boundary, five independent "
            "CFD anatomies, no payload/P0/model/PBS/GPU, introai9-only "
            "execution, and complete junjinyong exclusion."
        )
    checks.append("broad-registry rejection and restricted-access boundary")

    rsna_registry_audit = problem_selection["rsna_aws_registry_correction_audit"]
    _require_keys(
        rsna_registry_audit,
        [
            "status",
            "audit_document",
            "candidate_id",
            "score",
            "axis_scores",
            "automatic_selection_threshold",
            "active_shortlist_count",
            "primary_problem_selected",
            "registry_entry",
            "registry_yaml_file_commit",
            "registry_yaml_blob_sha",
            "registry_yaml_bytes",
            "dataset_doi",
            "controlled_access",
            "noncommercial_no_redistribution_terms_reported",
            "user_terms_accepted_verified",
            "access_request_submitted",
            "mira_account_created",
            "s3_listing_or_payload_accessed",
            "reported_brain_scans_more_than",
            "reported_volunteer_radiologists_more_than",
            "reported_institutions",
            "reported_ai_segmented_studies_approximately",
            "official_wiki_status",
            "registry_description_modality",
            "public_competition_implementation_modalities",
            "release_modality_contract_publicly_reconciled",
            "data_resource_publication_status",
            "registry_data_at_work_url_points_to_unrelated_pulmonary_embolism_paper",
            "first_place_repository_commit",
            "second_place_preprint",
            "official_aneurysm_supervision_semantics",
            "provided_voxel_segmentation_semantics",
            "public_per_reader_or_adjudication_manifest_verified",
            "public_center_modality_and_sealed_outer_test_manifest_verified",
            "direct_prior_threats",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_pbs_jobs_observed",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.rsna_aws_registry_correction_audit",
    )
    expected_rsna_registry_priors = {
        "rsna_2025_first_place_global_local_anatomy_aware_detection",
        "rsna_2025_second_place_multitask_vessel_and_aneurysm_system",
        "vessel_aware_multiscale_deformable_3d_attention",
        "sequential_conformal_risk_control_for_object_detection",
        "conformal_prediction_sets_for_instance_segmentation",
        "generic_point_supervised_3d_lesion_detection_and_set_prediction",
    }
    rsna_registry_axis_scores = rsna_registry_audit["axis_scores"]
    if (
        rsna_registry_audit["status"]
        != "completed_source_only_rejected_below_admission_threshold"
        or rsna_registry_audit["audit_document"]
        != "docs/rsna-aws-registry-audit-2026-08-10.md"
        or rsna_registry_audit["candidate_id"]
        != "rsna_registry_backed_study_level_lesion_set_miss_risk_control"
        or rsna_registry_audit["score"] != 31.5
        or len(rsna_registry_axis_scores) != 8
        or any(score < 0.0 or score > 5.0 for score in rsna_registry_axis_scores)
        or abs(sum(rsna_registry_axis_scores) - rsna_registry_audit["score"]) >= 1e-12
        or rsna_registry_audit["automatic_selection_threshold"] != 32.0
        or rsna_registry_audit["score"]
        >= rsna_registry_audit["automatic_selection_threshold"]
        or rsna_registry_audit["active_shortlist_count"] != 0
        or rsna_registry_audit["primary_problem_selected"] is not False
        or rsna_registry_audit["registry_entry"]
        != "https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/"
        or rsna_registry_audit["registry_yaml_file_commit"]
        != "523ffd3914ba99e6c4b17441f1633cc3eec74c69"
        or rsna_registry_audit["registry_yaml_blob_sha"]
        != "97b8c1f16b2809d2e82ec0c39d3b156b174c8c83"
        or rsna_registry_audit["registry_yaml_bytes"] != 2626
        or rsna_registry_audit["dataset_doi"] != "10.1148/dataset.ica.2025"
        or rsna_registry_audit["controlled_access"] is not True
        or rsna_registry_audit[
            "noncommercial_no_redistribution_terms_reported"
        ]
        is not True
        or rsna_registry_audit["user_terms_accepted_verified"] is not False
        or rsna_registry_audit["access_request_submitted"] is not False
        or rsna_registry_audit["mira_account_created"] is not False
        or rsna_registry_audit["s3_listing_or_payload_accessed"] is not False
        or rsna_registry_audit["reported_brain_scans_more_than"] != 4000
        or rsna_registry_audit["reported_volunteer_radiologists_more_than"] != 40
        or rsna_registry_audit["reported_institutions"] != 18
        or rsna_registry_audit["reported_ai_segmented_studies_approximately"] != 200
        or rsna_registry_audit["official_wiki_status"] != "coming_soon"
        or rsna_registry_audit["registry_description_modality"]
        != "ct_brain_scans"
        or rsna_registry_audit["public_competition_implementation_modalities"]
        != ["cta", "mra", "t1_post", "t2"]
        or rsna_registry_audit[
            "release_modality_contract_publicly_reconciled"
        ]
        is not False
        or rsna_registry_audit["data_resource_publication_status"] != "forthcoming"
        or rsna_registry_audit[
            "registry_data_at_work_url_points_to_unrelated_pulmonary_embolism_paper"
        ]
        is not True
        or rsna_registry_audit["first_place_repository_commit"]
        != "e1dcdf0058e1e0d0044d8053e92243b4b4794555"
        or rsna_registry_audit["second_place_preprint"] != "arxiv_2606.26706v1"
        or rsna_registry_audit["official_aneurysm_supervision_semantics"]
        != "center_points_study_presence_and_vascular_territory"
        or rsna_registry_audit["provided_voxel_segmentation_semantics"]
        != "thirteen_class_circle_of_willis_vessel_anatomy_not_aneurysm_extent"
        or rsna_registry_audit[
            "public_per_reader_or_adjudication_manifest_verified"
        ]
        is not False
        or rsna_registry_audit[
            "public_center_modality_and_sealed_outer_test_manifest_verified"
        ]
        is not False
        or set(rsna_registry_audit["direct_prior_threats"])
        != expected_rsna_registry_priors
        or rsna_registry_audit["executable_p0_registered"] is not False
        or rsna_registry_audit["method_selected"] is not False
        or rsna_registry_audit["architecture_selected"] is not False
        or rsna_registry_audit["gpu_training_authorized"] is not False
        or rsna_registry_audit["outer_test_authorized"] is not False
        or rsna_registry_audit["submission_identity_active"] is not False
        or rsna_registry_audit["execution_server"] != "introai9"
        or rsna_registry_audit["introai9_connection_verified"] is not True
        or rsna_registry_audit["introai9_pbs_jobs_observed"] != 0
        or rsna_registry_audit["pbs_job_created"] is not False
        or rsna_registry_audit["login_node_gpu_command_executed"] is not False
        or rsna_registry_audit["junjinyong_accessed_for_this_audit"] is not False
        or rsna_registry_audit["decision"]
        != "reject_without_score_repair_terms_acceptance_access_request_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or rsna_registry_audit["next_allowed_action"]
        != "after_user_personal_terms_acceptance_and_official_manifest_release_register_a_fresh_source_task_audit_not_automatic_p0_or_training"
        or rsna_registry_audit["candidate_id"]
        not in set(problem_selection["rejected_candidates"])
    ):
        raise ProtocolError(
            "The RSNA AWS registry correction must remain a 31.5/40 source "
            "rejection with controlled access, unresolved release semantics, "
            "no terms/request/payload/P0/model/GPU, introai9-only execution, "
            "and complete junjinyong exclusion."
        )
    checks.append("RSNA AWS controlled-access registry correction boundary")

    topbrain2_audit = problem_selection["topbrain2_source_audit"]
    _require_keys(
        topbrain2_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_ids",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "zenodo_record",
            "zenodo_publication_date",
            "design_pdf_bytes",
            "design_pdf_pages",
            "design_pdf_md5",
            "design_pdf_sha256",
            "zenodo_license_identifier_present",
            "zenodo_design_object_license_id",
            "zenodo_license_scope",
            "challenge_page_status",
            "challenge_join_registration_available",
            "grand_challenge_submission_status",
            "planned_training_release_date",
            "planned_test_window",
            "versioned_topbrain2_dataset_release_verified",
            "versioned_topbrain2_executable_evaluation_contract_verified",
            "topbrain2025_evaluation_repository_head",
            "topbrain2025_evaluation_repository_scope",
            "planned_task1_train_volumes",
            "planned_task1_test_volumes",
            "planned_task1_labels_at_least",
            "planned_task1_modalities",
            "planned_task1_topaneu_train_volumes",
            "planned_task1_topaneu_test_volumes",
            "planned_task1_aneurysm_is_robustness_condition_not_lesion_target",
            "planned_task1_metrics",
            "planned_task2_train_volumes",
            "planned_task2_test_volumes",
            "planned_task2_endpoint",
            "planned_task2_single_expert_per_case_without_merge",
            "casewise_aneurysm_mask_parent_vessel_attachment_acquisition_reader_or_cross_challenge_identity_manifest_verified",
            "patient_image_mask_clinical_split_or_test_payload_accessed",
            "source_watch_config",
            "source_watch_current_snapshot_matches",
            "direct_prior_threats",
            "candidates",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_verified",
            "introai9_pbs_jobs_observed",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.topbrain2_source_audit",
    )
    expected_topbrain2_scores = {
        "topbrain2_joint_lesion_parent_vessel_consistency": 29.0,
        "topbrain2_disease_conditioned_selective_vessel_segmentation": 28.5,
        "topbrain2_aneurysm_conditioned_vessel_integrity_failure_localization": 28.0,
        "topbrain2_unified_modality_source_invariant_artery_vein_anatomy": 27.5,
        "topbrain2_class_contamination_aware_multiclass_vessel_calibration": 27.0,
        "topbrain2_compositional_aneurysm_stenosis_ordinal_diagnosis": 23.5,
    }
    observed_topbrain2_scores = {
        candidate["id"]: candidate["score"]
        for candidate in topbrain2_audit["candidates"]
    }
    topbrain2_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in topbrain2_audit["candidates"]
    )
    expected_topbrain2_priors = {
        "topbrain1_multimodal_multiclass_whole_brain_vessel_segmentation",
        "topaneu_multimodal_aneurysm_detection_classification_and_segmentation",
        "rsna_multitask_aneurysm_and_vessel_classification_and_segmentation",
        "multiclass_betti_matching_topology_loss",
        "cbdice_radius_boundary_topology_loss",
        "centerline_cross_entropy_connectivity_loss",
        "generic_pathology_aware_domain_generalization_and_selective_segmentation",
    }
    if (
        topbrain2_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or topbrain2_audit["audit_document"]
        != "docs/topbrain2-source-audit-2026-08-10.md"
        or topbrain2_audit["automatic_selection_threshold"] != 32.0
        or topbrain2_audit["best_candidate_ids"]
        != ["topbrain2_joint_lesion_parent_vessel_consistency"]
        or topbrain2_audit["best_score"] != 29.0
        or topbrain2_audit["best_score"]
        >= topbrain2_audit["automatic_selection_threshold"]
        or topbrain2_audit["active_shortlist_count"] != 0
        or topbrain2_audit["primary_problem_selected"] is not False
        or topbrain2_audit["zenodo_record"] != "10.5281/zenodo.19707577"
        or topbrain2_audit["zenodo_publication_date"] != "2026-04-23"
        or topbrain2_audit["design_pdf_bytes"] != 139840
        or topbrain2_audit["design_pdf_pages"] != 35
        or topbrain2_audit["design_pdf_md5"]
        != "da6c835d0336db81a94b78e7601f47b8"
        or topbrain2_audit["design_pdf_sha256"]
        != "15a2269bc00b6720f10d6efd41d8996010703451aef32de14f599cd3357ff4f7"
        or topbrain2_audit["zenodo_license_identifier_present"] is not True
        or topbrain2_audit["zenodo_design_object_license_id"] != "cc-by-4.0"
        or topbrain2_audit["zenodo_license_scope"]
        != "design_record_only_not_unreleased_medical_dataset"
        or topbrain2_audit["challenge_page_status"] != "under_construction"
        or topbrain2_audit["challenge_join_registration_available"] is not True
        or topbrain2_audit["grand_challenge_submission_status"]
        != "join_registration_available_but_no_executable_task_submission_contract"
        or topbrain2_audit["versioned_topbrain2_dataset_release_verified"]
        is not False
        or topbrain2_audit[
            "versioned_topbrain2_executable_evaluation_contract_verified"
        ]
        is not False
        or topbrain2_audit["topbrain2025_evaluation_repository_head"]
        != "ba4252ab0dbe9d59a9ae45058ae040b016aae0ad"
        or topbrain2_audit["planned_task1_train_volumes"] != 215
        or topbrain2_audit["planned_task1_test_volumes"] != 123
        or topbrain2_audit["planned_task1_labels_at_least"] != 55
        or topbrain2_audit["planned_task1_topaneu_train_volumes"] != 50
        or topbrain2_audit["planned_task1_topaneu_test_volumes"] != 20
        or topbrain2_audit[
            "planned_task1_aneurysm_is_robustness_condition_not_lesion_target"
        ]
        is not True
        or topbrain2_audit["planned_task2_train_volumes"] != 315
        or topbrain2_audit["planned_task2_test_volumes"] != 183
        or topbrain2_audit["planned_task2_endpoint"]
        != "per_vessel_stenosis_and_occlusion_ordinal_grading"
        or topbrain2_audit[
            "planned_task2_single_expert_per_case_without_merge"
        ]
        is not True
        or topbrain2_audit[
            "casewise_aneurysm_mask_parent_vessel_attachment_acquisition_reader_or_cross_challenge_identity_manifest_verified"
        ]
        is not False
        or topbrain2_audit[
            "patient_image_mask_clinical_split_or_test_payload_accessed"
        ]
        is not False
        or topbrain2_audit["source_watch_config"] != "configs/source_watch_v4.json"
        or topbrain2_audit["source_watch_current_snapshot_matches"] is not True
        or set(topbrain2_audit["direct_prior_threats"])
        != expected_topbrain2_priors
        or observed_topbrain2_scores != expected_topbrain2_scores
        or not topbrain2_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in topbrain2_audit["candidates"]
        )
        or not set(expected_topbrain2_scores).issubset(
            set(problem_selection["rejected_candidates"])
        )
        or topbrain2_audit["executable_p0_registered"] is not False
        or topbrain2_audit["method_selected"] is not False
        or topbrain2_audit["architecture_selected"] is not False
        or topbrain2_audit["gpu_training_authorized"] is not False
        or topbrain2_audit["outer_test_authorized"] is not False
        or topbrain2_audit["submission_identity_active"] is not False
        or topbrain2_audit["execution_server"] != "introai9"
        or topbrain2_audit["introai9_connection_verified"] is not True
        or topbrain2_audit["introai9_pbs_jobs_observed"] != 0
        or topbrain2_audit["pbs_job_created"] is not False
        or topbrain2_audit["login_node_gpu_command_executed"] is not False
        or topbrain2_audit["junjinyong_accessed_for_this_audit"] is not False
        or topbrain2_audit["decision"]
        != "reject_all_without_score_repair_medical_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or topbrain2_audit["next_allowed_action"]
        != "monitor_for_a_versioned_licensed_release_and_casewise_target_lineage_then_run_only_a_fresh_source_audit_not_automatic_download_p0_or_training"
    ):
        raise ProtocolError(
            "The TopBrain 2.0 source audit must retain the six frozen "
            "rejections, proposal-only release boundary, no medical payload/"
            "P0/model/PBS/GPU, introai9-only execution, and complete "
            "junjinyong exclusion."
        )
    checks.append("TopBrain 2.0 proposal-only source rejection boundary")

    mechanics_audit = problem_selection["four_d_cta_aaa_mechanics_source_audit"]
    _require_keys(
        mechanics_audit,
        [
            "status",
            "audit_document",
            "automatic_selection_threshold",
            "best_candidate_ids",
            "best_score",
            "active_shortlist_count",
            "primary_problem_selected",
            "zenodo_record",
            "zenodo_concept_record",
            "zenodo_publication_date",
            "zenodo_revision",
            "zenodo_access_right",
            "zenodo_license_id",
            "archive_name",
            "archive_bytes",
            "archive_md5",
            "archive_or_member_payload_accessed",
            "reported_patients",
            "reported_centres",
            "reported_minimum_cardiac_phases_per_patient",
            "reported_maximum_cardiac_phases_per_patient",
            "reported_surface_and_fe_outputs",
            "p01_to_p10_segmentation_assistance",
            "p11_to_p20_segmentation_assistance",
            "future_growth_rupture_treatment_wall_strength_or_histology_endpoint_available",
            "released_mechanics_are_derived_workflow_outputs_not_independent_clinical_ground_truth",
            "synthetic_displacement_ground_truth_effective_patient_units",
            "direct_prior_threats",
            "candidates",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "execution_server",
            "introai9_connection_previously_verified",
            "introai9_current_status_attempt",
            "introai9_last_verified_pbs_jobs_observed",
            "pbs_job_created",
            "login_node_gpu_command_executed",
            "junjinyong_accessed_for_this_audit",
            "decision",
            "next_allowed_action",
        ],
        "problem_selection.four_d_cta_aaa_mechanics_source_audit",
    )
    expected_mechanics_scores = {
        "four_d_cta_phase_subset_rsii_hotspot_preservation": 31.5,
        "four_d_cta_image_to_rsii_surface_operator": 30.5,
        "four_d_cta_mechanics_consistent_cardiac_cycle_registration": 30.0,
        "four_d_cta_synthetic_gt_calibrated_selective_strain_mapping": 29.0,
        "four_d_cta_centre_pipeline_invariant_structural_integrity_mapping": 28.5,
        "four_d_cta_progression_or_rupture_prediction_from_released_mechanics": 25.5,
    }
    observed_mechanics_scores = {
        candidate["id"]: candidate["score"]
        for candidate in mechanics_audit["candidates"]
    }
    mechanics_axis_sums_match = all(
        len(candidate["axis_scores"]) == 8
        and all(0.0 <= score <= 5.0 for score in candidate["axis_scores"])
        and abs(sum(candidate["axis_scores"]) - candidate["score"]) < 1e-12
        for candidate in mechanics_audit["candidates"]
    )
    expected_mechanics_priors = {
        "regularized_four_d_cta_registration_displacement_and_strain",
        "fe_tension_plus_registered_strain_sii_and_rsii",
        "equivariant_cycle_and_semigroup_consistent_deformable_registration",
        "uncertainty_aware_deformable_registration",
        "aneurysm_wall_stress_and_hemodynamic_neural_surrogates",
        "functional_surrogate_prediction_sets",
        "function_valued_neural_operator_uncertainty",
    }
    expected_mechanics_outputs = {
        "wall_surface",
        "ilt_surface",
        "aaa_fe_model",
        "wall_fe_mesh",
        "ilt_fe_mesh",
        "strain_map",
        "tension_map",
        "sii_map",
        "rsii_map",
    }
    if (
        mechanics_audit["status"]
        != "completed_source_only_all_candidates_below_admission_threshold"
        or mechanics_audit["audit_document"]
        != "docs/four-d-cta-aaa-mechanics-source-audit-2026-08-10.md"
        or mechanics_audit["automatic_selection_threshold"] != 32.0
        or mechanics_audit["best_candidate_ids"]
        != ["four_d_cta_phase_subset_rsii_hotspot_preservation"]
        or mechanics_audit["best_score"] != 31.5
        or mechanics_audit["best_score"]
        >= mechanics_audit["automatic_selection_threshold"]
        or mechanics_audit["active_shortlist_count"] != 0
        or mechanics_audit["primary_problem_selected"] is not False
        or mechanics_audit["zenodo_record"] != "10.5281/zenodo.19182978"
        or mechanics_audit["zenodo_concept_record"] != "10.5281/zenodo.19182977"
        or mechanics_audit["zenodo_publication_date"] != "2026-03-23"
        or mechanics_audit["zenodo_revision"] != 3
        or mechanics_audit["zenodo_access_right"] != "open"
        or mechanics_audit["zenodo_license_id"] != "cc-by-4.0"
        or mechanics_audit["archive_name"] != "Dataset_root.zip"
        or mechanics_audit["archive_bytes"] != 1857980948
        or mechanics_audit["archive_md5"]
        != "11b74684e382d1410a2d64f81967e613"
        or mechanics_audit["archive_or_member_payload_accessed"] is not False
        or mechanics_audit["reported_patients"] != 20
        or mechanics_audit["reported_centres"] != 3
        or mechanics_audit["reported_minimum_cardiac_phases_per_patient"] != 2
        or mechanics_audit["reported_maximum_cardiac_phases_per_patient"] != 10
        or set(mechanics_audit["reported_surface_and_fe_outputs"])
        != expected_mechanics_outputs
        or mechanics_audit["p01_to_p10_segmentation_assistance"] != "praevaorta"
        or mechanics_audit["p11_to_p20_segmentation_assistance"]
        != "nninteractive"
        or mechanics_audit[
            "future_growth_rupture_treatment_wall_strength_or_histology_endpoint_available"
        ]
        is not False
        or mechanics_audit[
            "released_mechanics_are_derived_workflow_outputs_not_independent_clinical_ground_truth"
        ]
        is not True
        or mechanics_audit[
            "synthetic_displacement_ground_truth_effective_patient_units"
        ]
        != 1
        or set(mechanics_audit["direct_prior_threats"])
        != expected_mechanics_priors
        or observed_mechanics_scores != expected_mechanics_scores
        or not mechanics_axis_sums_match
        or any(
            candidate["payload_accessed"]
            for candidate in mechanics_audit["candidates"]
        )
        or not set(expected_mechanics_scores).issubset(
            set(problem_selection["rejected_candidates"])
        )
        or mechanics_audit["executable_p0_registered"] is not False
        or mechanics_audit["method_selected"] is not False
        or mechanics_audit["architecture_selected"] is not False
        or mechanics_audit["gpu_training_authorized"] is not False
        or mechanics_audit["outer_test_authorized"] is not False
        or mechanics_audit["submission_identity_active"] is not False
        or mechanics_audit["execution_server"] != "introai9"
        or mechanics_audit["introai9_connection_previously_verified"] is not True
        or mechanics_audit["introai9_current_status_attempt"]
        != "connection_reset_before_remote_command_no_scheduler_observation"
        or mechanics_audit["introai9_last_verified_pbs_jobs_observed"] != 0
        or mechanics_audit["pbs_job_created"] is not False
        or mechanics_audit["login_node_gpu_command_executed"] is not False
        or mechanics_audit["junjinyong_accessed_for_this_audit"] is not False
        or mechanics_audit["decision"]
        != "reject_all_without_score_repair_archive_payload_p0_method_architecture_pbs_gpu_outer_test_or_submission_claim"
        or mechanics_audit["next_allowed_action"]
        != "seek_an_independent_clinical_or_physical_target_with_sufficient_patient_units_then_run_only_a_fresh_source_audit_not_automatic_download_p0_or_training"
    ):
        raise ProtocolError(
            "The 4D-CTA AAA mechanics source audit must retain the six frozen "
            "sub-threshold rejections, twenty-patient and derived-target "
            "boundaries, no archive/P0/model/PBS/GPU, introai9-only execution, "
            "and complete junjinyong exclusion."
        )
    checks.append("4D-CTA AAA mechanics source rejection boundary")

    venue = protocol["venue"]
    _require_keys(
        venue,
        [
            "target",
            "submission_deadline",
            "review",
            "technical_page_limit",
            "maximum_first_author_submissions",
            "substantially_similar_prior_publication_prohibited",
            "substantially_similar_concurrent_submission_prohibited",
            "preprint_posting_allowed",
            "ethics_statement_required_irrespective_of_approval_need",
            "conflict_of_interest_disclosure_required",
            "submission_link_status",
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
    if (
        venue["maximum_first_author_submissions"] != 2
        or venue["substantially_similar_prior_publication_prohibited"] is not True
        or venue["substantially_similar_concurrent_submission_prohibited"] is not True
        or venue["preprint_posting_allowed"] is not True
        or venue["ethics_statement_required_irrespective_of_approval_need"] is not True
        or venue["conflict_of_interest_disclosure_required"] is not True
        or venue["submission_link_status"] != "coming_soon"
    ):
        raise ProtocolError(
            "ISBI authorship, originality, preprint, ethics, COI, and submission-link rules changed."
        )
    if set(venue["fifth_page_allowed_content"]) != {
        "references",
        "compliance_with_ethical_standards",
        "acknowledgments_and_conflict_of_interest",
    }:
        raise ProtocolError("ISBI fifth-page content must remain non-technical.")
    if (
        venue["submission_ready"] is not False
        or venue["required_headline_domain"]
        != "no_active_primary_vmr_p0_closed_no_verdict_surface_vector_inactive_no_method_architecture_gpu_or_submission_identity"
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
            "ISBI submission must remain blocked while the primary problem is "
            "unselected; historical 3D evidence remains insufficient."
        )
    checks.append("ISBI 2027 four-page and no-active-primary boundary")

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
            "i0a_source_commit",
            "i0a_result",
            "i0a_result_sha256",
            "i0a_raw_result_sha256",
            "i0a_raw_status_sha256",
            "i0a_gate",
            "i0a_pass_authorizes",
            "i0b_config",
            "i0b_config_sha256",
            "i0b_status",
            "i0b_discovery_scope",
            "i0b_allowed_field_access",
            "i0b_pass_authorizes",
            "i0b_local_repair_rerun_or_threshold_change_allowed",
            "i0b_execution_source_commit",
            "i0b_execution_record",
            "i0b_execution_record_sha256",
            "i0b_execution_gate",
            "i0b_execution_asset_and_field_access",
            "i0b_execution_reentry_allowed",
            "i0c_authorized",
            "generic_super_resolution_or_denoising_is_novel",
            "cfd_field_is_clinical_mri_ground_truth",
            "forbidden_claims",
        ],
        "task",
    )
    if task["primary_problem"] not in ALLOWED_PRIMARY_PROBLEMS:
        raise ProtocolError(
            "The primary task must remain unselected while the AneuX candidate "
            "is only a source shortlist."
        )
    if task["application_endpoint"] not in ALLOWED_ENDPOINTS:
        raise ProtocolError(
            "The application endpoint must remain unselected; prospective risk or "
            "rupture-status relabeling requires a separate protocol."
        )
    forbidden = set(task["forbidden_claims"])
    if "prospective_rupture_risk" not in forbidden or "clinical_utility" not in forbidden:
        raise ProtocolError("Task must forbid prospective-risk and clinical-utility claims.")
    if "causal_intervention_effect" not in forbidden:
        raise ProtocolError("Paired simulator responses must not be called causal effects.")
    if (
        task["primary_metric"] != "unselected"
        or task["historical_primary_problem"]
        != "operator_learning_under_partial_boundary_observation"
        or task["historical_application_endpoint"] != "cross_sectional_rupture_status"
        or task["historical_primary_metric"] != "functional_energy_score"
        or task["historical_primary_status"]
        != "unsupported_after_n1c_and_inactive_after_m0_execution_incomplete"
        or task["active_candidate_problem"] != "unselected"
        or task["active_candidate_status"]
        != "aneux_reliability_source_rejected_pre_execution_no_active_candidate"
        or task["candidate_primary_estimand"] != "unselected"
        or task["candidate_secondary_estimand"] != "unselected"
        or task["i0a_config"] != "configs/flow_mri_protocol_i0a_asset_audit.json"
        or task["i0a_config_sha256"]
        != "ceb6413047b117ecbc7b52d83919b73117491e8de6c099c7b158f592788f40ff"
        or task["i0a_source_commit"]
        != "f7b4e024d69d43cf042f4163342b4d993386f441"
        or task["i0a_result"]
        != "results/flow_mri_protocol_i0a_asset_audit_20260808.json"
        or task["i0a_result_sha256"]
        != "2243172a720b25ebebd6052b9c0989880d95cba5b8d984f8980f70cf5f26d9c6"
        or task["i0a_raw_result_sha256"]
        != "c666644bf72fa10bb550747fbeace923ca0caabbf8142f4f6c7ff5417af00faa"
        or task["i0a_raw_status_sha256"]
        != "254c5966474e3304449b94976e0f03392f1b154b716812c40736d722213b74ec"
        or task["i0a_gate"] != "14_of_14_passed_asset_integrity_only"
        or task["i0a_pass_authorizes"]
        != "register_selective_private_staging_and_method_free_I0b_task_adequacy_only"
        or task["i0b_config"]
        != "configs/flow_mri_protocol_i0b_task_adequacy.json"
        or task["i0b_config_sha256"]
        != "e19a1194f1b9ec41861c5084b26c9add5be47924a19aee4d23ffc826399dce06"
        or task["i0b_status"]
        != "execution_incomplete_missing_h5py_before_archive_or_field_access_no_scientific_verdict_closed_without_rerun"
        or task["i0b_discovery_scope"]
        != "2021_README_and_MATLAB_reader_plus_Zenodo_17183575_record_three_central_directories_and_33_primary_PAR_headers_not_prospective_evidence"
        or task["i0b_allowed_field_access"]
        != "2021_processed_velocity_27_RAW_members_only"
        or task["i0b_pass_authorizes"]
        != "register_method_free_I0c_PAR_REC_decoder_noise_and_cross_VENC_measurement_audit_only"
        or task["i0b_local_repair_rerun_or_threshold_change_allowed"] is not False
        or task["i0b_execution_source_commit"]
        != "0ebdb344a6cd4009a928746cda5389b95f12bf8d"
        or task["i0b_execution_record"]
        != "results/flow_mri_protocol_i0b_execution_20260809.json"
        or task["i0b_execution_record_sha256"]
        != "1b75bb953352966b9c7e2edbb838973d5222c883fe821e4b77ee2302c2ba2130"
        or task["i0b_execution_gate"] != "not_evaluated"
        or task["i0b_execution_asset_and_field_access"] != "zero"
        or task["i0b_execution_reentry_allowed"] is not False
        or task["i0c_authorized"] is not False
        or task["generic_super_resolution_or_denoising_is_novel"] is not False
        or task["cfd_field_is_clinical_mri_ground_truth"] is not False
    ):
        raise ProtocolError(
            "The AneuX nested-orbit direction is source-rejected and no active "
            "candidate, estimand, primary problem, or endpoint may remain; historical "
            "4D-flow must retain the exact I0a result and I0b execution record."
        )
    checks.append("no-active-task and historical 4D-flow guardrails")

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
    aneug_flow = next(item for item in datasets if item["name"] == "aneug_flow")
    vmr_growth_dataset = next(
        item
        for item in datasets
        if item["name"] == "vmr_growth_matched_cerebral_aneurysm"
    )
    flow_2021 = next(
        item for item in datasets if item["name"] == "flow_mri_multiresolution_phantom_2021"
    )
    flow_2025 = next(
        item for item in datasets if item["name"] == "flow_mri_dual_venc_phantoms_2025"
    )
    flow_intervention = next(
        item
        for item in datasets
        if item["name"] == "flow_mri_intervention_phantoms_2025"
    )
    rsna_ica = next(
        item for item in datasets if item["name"] == "rsna_ica_2025_controlled_access"
    )
    openneuro_lausanne = next(
        item for item in datasets if item["name"] == "openneuro_ds003949"
    )
    open_cta = next(
        item
        for item in datasets
        if item["name"] == "open_multicenter_cta_2026_zenodo_15697196"
    )
    topaneu = next(
        item for item in datasets if item["name"] == "topaneu_2026_terms_gated"
    )
    dias = next(item for item in datasets if item["name"] == "dias_dsa_sequence_2024")
    if (
        openneuro_lausanne.get("role")
        != "closed_source_lead_history_after_metadata_p0_execution_incomplete_not_training_or_outer_test"
        or openneuro_lausanne.get("status")
        != "metadata_p0_execution_incomplete_no_scientific_verdict_closed_without_rerun_no_patient_payload"
        or openneuro_lausanne.get("dataset_commit")
        != "896b8846d899acee68c0246cc987ca96e77267d4"
        or openneuro_lausanne.get("license") != "CC0"
        or openneuro_lausanne.get("public_subjects") != 284
        or openneuro_lausanne.get("public_weak_subjects_expected") != 246
        or openneuro_lausanne.get("public_precise_subjects_expected") != 38
        or openneuro_lausanne.get("patient_nifti_image_or_mask_payload_accessed")
        is not False
        or openneuro_lausanne.get("method_or_gpu_authorized") is not False
        or
        cmha["field_provenance"] != "real_cfd"
        or cmha.get("role") != "closed_goal_oriented_s0a_asset_history_not_an_active_primary"
        or cmha.get("status")
        != "asset_component_failed_5_of_9_exact_lesion_level_image_surface_table_linkage_unsupported"
    ):
        raise ProtocolError(
            "CMHA must remain a real-CFD provenance asset but a closed 5/9 "
            "goal-oriented history, not an active primary dataset."
        )
    if (
        aneux.get("field_provenance") != "none"
        or aneux.get("split_unit") != "patient"
        or aneux.get("role")
        != "closed_preprocessing_orbit_p0_history_no_active_primary_role"
        or aneux.get("status")
        != "p0_execution_incomplete_initial_tabular_transport_exhausted_scientific_gate_unevaluated_no_rerun"
        or aneux.get("license")
        != "cc_by_nc_4_0_with_attribution_requirement"
        or aneux.get("source_lesions") != 750
        or aneux.get("source_patients") != 605
        or aneux.get("patient_id_observed_rows") != 637
        or aneux.get("mesh_resolutions") != 3
        or aneux.get("cut_configurations") != 4
        or aneux.get("tabular_payload_accessed") is not False
        or aneux.get("completed_tabular_archive_retained") is not False
        or aneux.get("model_central_directory_accessed") is not False
        or aneux.get("model_member_payload_accessed") is not False
    ):
        raise ProtocolError(
            "AneuX must remain a patient-grouped, non-CFD, closed P0 history "
            "after its execution-incomplete one-shot source contract."
        )
    if (
        dias.get("field_provenance") != "none"
        or dias.get("split_unit") != "patient"
        or dias.get("role")
        != "source_rejected_prefix_risk_candidate_possible_future_external_segmentation_baseline_only"
        or dias.get("status")
        != "source_metadata_audited_payload_not_accessed_candidate_rejected_31_of_40"
        or dias.get("doi") != "10.5281/zenodo.11637181"
        or dias.get("license") != "cc_by_4_0"
        or dias.get("source_patients") != 60
        or dias.get("source_sequences") != 120
        or dias.get("fully_annotated_sequences") != 60
        or dias.get("released_min_frames") != 4
        or dias.get("released_max_frames") != 14
        or dias.get("payload_accessed") is not False
        or dias.get("introai9_staged_asset_found_in_bounded_inventory") is not False
        or dias.get("method_or_gpu_authorized") is not False
    ):
        raise ProtocolError(
            "DIAS must remain a patient-grouped source-only asset whose prefix-risk "
            "candidate was rejected before payload, method, or GPU access."
        )
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
    if (
        aneug_flow.get("role")
        != "closed_raw_surface_vector_p0_execution_incomplete_with_closed_cycle_functional_history_preserved"
        or aneug_flow.get("field_provenance") != "synthetic_cfd"
        or aneug_flow.get("split_unit") != "generator_seed_geometry"
        or aneug_flow.get("status")
        != "raw_structure_p0_execution_incomplete_no_verdict_no_rerun_old_processed_cycle_p0_closed_no_rerun"
        or aneug_flow.get("dataset_repository_commit")
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or aneug_flow.get("p0_config")
        != "configs/aneug_surface_vector_structure_p0.json"
        or aneug_flow.get("p0_execution_record")
        != "results/aneug_surface_vector_structure_p0_execution_20260810.json"
        or aneug_flow.get("historical_cycle_p0_execution_record")
        != "results/aneug_cycle_functional_p0_execution_20260809.json"
        or aneug_flow.get("method_or_gpu_authorized") is not False
    ):
        raise ProtocolError(
            "AneuG-Flow must remain synthetic with both raw-structure and processed "
            "P0 versions closed without a verdict, rerun, method, or GPU authority."
        )
    if (
        vmr_growth_dataset.get("role")
        != "closed_vmr_growth_paired_structure_stability_source_history_after_p0_execution_incomplete"
        or vmr_growth_dataset.get("field_provenance") != "real_cfd"
        or vmr_growth_dataset.get("split_unit") != "patient"
        or vmr_growth_dataset.get("status")
        != "p0_execution_incomplete_0_of_10_no_scientific_verdict_no_repair_or_rerun"
        or vmr_growth_dataset.get("primary_paper_doi")
        != "10.3389/fphys.2023.1300754"
        or vmr_growth_dataset.get("patients") != 22
        or vmr_growth_dataset.get("matched_pairs") != 11
        or vmr_growth_dataset.get("result_archives") != 22
        or vmr_growth_dataset.get("result_archive_bytes") != 1998793994
        or vmr_growth_dataset.get("p0_config")
        != "configs/vmr_growth_surface_structure_p0.json"
        or vmr_growth_dataset.get("p0_execution_record")
        != "results/vmr_growth_surface_structure_p0_execution_20260811.json"
        or vmr_growth_dataset.get("p0_job_id") != "115848.ECE-util1"
        or vmr_growth_dataset.get("p0_archive_or_vtp_access_extent_known")
        is not False
        or vmr_growth_dataset.get("p0_archive_or_vtp_persisted") is not False
        or vmr_growth_dataset.get(
            "medical_image_project_zip_result_archive_or_vtp_accessed"
        )
        is not False
        or vmr_growth_dataset.get("method_or_gpu_authorized") is not False
    ):
        raise ProtocolError(
            "The VMR matched-pair source must remain a 22-patient/11-pair closed "
            "history after the exact no-verdict P0, with no persisted payload."
        )
    if (
        flow_2021.get("status")
        != "i0b_execution_incomplete_before_asset_access_no_field_read"
        or flow_2025.get("status")
        != "i0b_execution_incomplete_overlap_unresolved_no_REC_read"
        or flow_intervention.get("status")
        != "i0b_execution_incomplete_metadata_discovery_only_no_REC_read"
        or flow_intervention.get("split_unit") != "physical_base_geometry"
        or flow_intervention.get("source_patient_anatomies") != 2
        or flow_intervention.get("base_geometry_models") != 5
        or flow_intervention.get("primary_acquisitions") != 33
        or flow_intervention.get("physical_model_device_states") != 22
        or flow_intervention.get("multi_venc_physical_states") != 8
        or flow_intervention.get("pump_off_noise_acquisitions") != 2
        or flow_intervention.get("unique_device_conditions") != 15
    ):
        raise ProtocolError(
            "I0b execution record must preserve zero field/REC access and physical-unit boundaries."
        )
    if (
        rsna_ica.get("field_provenance") != "none"
        or rsna_ica.get("split_unit") != "patient"
        or rsna_ica.get("status")
        != "controlled_access_not_staged_supervision_semantics_audited_from_public_sources_no_active_method_or_gpu"
        or rsna_ica.get("license_boundary")
        != "controlled_noncommercial_access_terms_require_user_acceptance_no_redistribution"
    ):
        raise ProtocolError(
            "RSNA-ICA must remain controlled-access, patient-split, unstaged, "
            "method/GPU-disabled, and rejected for the mixed-granularity shortlist."
        )
    if (
        open_cta.get("field_provenance") != "none"
        or open_cta.get("split_unit") != "cta_case"
        or open_cta.get("role")
        != "closed_physical_grid_p0_execution_history_no_active_primary_role"
        or open_cta.get("status")
        != "p0_execution_incomplete_after_partial_dicom_header_prefix_access_no_pixel_or_stl_no_rerun"
        or open_cta.get("series") != 172
        or open_cta.get("controls") != 90
        or open_cta.get("positive_cases") != 82
        or open_cta.get("aneurysm_stl") != 122
        or open_cta.get("multi_lesion_cases") != 24
        or open_cta.get("metadata_discovery_result")
        != "results/open_multicenter_cta_metadata_discovery_20260809.json"
        or open_cta.get("p0_config") != "configs/open_cta_physical_p0.json"
        or open_cta.get("p0_status")
        != "execution_incomplete_no_scientific_verdict_candidate_closed"
        or open_cta.get("p0_execution_record")
        != "results/open_cta_physical_p0_execution_20260809.json"
        or open_cta.get("p0_execution_record_sha256")
        != "538725c9901039169cc6e747a112630f327411c5594d021edf9b76fd913f950b"
        or open_cta.get("headline_or_training_authorized") is not False
    ):
        raise ProtocolError(
            "Open CTA must remain a case-unit P0 execution-incomplete history, "
            "not an active candidate, training, or TopAneu supervision evidence."
        )
    if (
        topaneu.get("field_provenance") != "none"
        or topaneu.get("split_unit") != "patient"
        or topaneu.get("role")
        != "conditional_p0_candidate_only_after_explicit_user_terms_acceptance_not_training"
        or topaneu.get("status")
        != "official_source_audited_terms_not_user_accepted_payload_not_accessed_conditional_lead_29_of_40"
        or topaneu.get("live_training_scans") != 417
        or topaneu.get("live_unique_patients") != 409
        or topaneu.get("location_classes") != 52
        or topaneu.get("vessel_mask_provenance")
        != "organizer_model_prediction_silver"
        or topaneu.get("user_terms_accepted_verified") is not False
        or topaneu.get("payload_accessed") is not False
        or topaneu.get("method_or_gpu_authorized") is not False
    ):
        raise ProtocolError(
            "TopAneu must remain terms-gated, unstaged, silver-vessel-aware, and "
            "method/GPU-disabled while the lead is below admission."
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
            "current_headline_architecture",
            *numeric_model_keys,
            "observation_modes",
            "temporal_representation",
            "irregular_3d_output_contract",
        ],
        "model",
    )
    if (
        model["current_headline_architecture"]
        != "unselected_no_active_problem_surface_vector_components_are_inactive_controls_only"
    ):
        raise ProtocolError(
            "No surface-vector, GNN, Hodge, equivariant, or temporal architecture "
            "may be selected after the VMR exact version closed without a verdict."
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
