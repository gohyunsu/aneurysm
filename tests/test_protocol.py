import copy
import hashlib
import unittest
from pathlib import Path

from aurora.protocol import ProtocolError, canonical_hash, load_protocol, validate_protocol


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aurora_v1.json"


class ProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.protocol = load_protocol(CONFIG)

    def test_reference_protocol_is_valid(self) -> None:
        checks = validate_protocol(self.protocol)
        self.assertGreaterEqual(len(checks), 8)
        self.assertEqual(len(canonical_hash(self.protocol)), 64)

    def test_compute_is_introai9_only_and_currently_idle(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["project"]["execution_server"] = "junjinyong"
        with self.assertRaisesRegex(ProtocolError, "introai9-only"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["project"]["current_gpu_job_count"] = 1
        with self.assertRaisesRegex(ProtocolError, "no active GPU job"):
            validate_protocol(candidate)

    def test_dsa_prefix_candidate_is_rejected_before_payload_or_training(self) -> None:
        audit = self.protocol["problem_selection"]["dsa_prefix_risk_source_audit"]
        self.assertEqual(audit["score"], 31.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertFalse(audit["dataset_payload_accessed"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertAlmostEqual(audit["full_minus_minimum_projection_dsc"], 0.002)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["dsa_prefix_risk_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "DSA prefix-risk candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        dias = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "dias_dsa_sequence_2024"
        )
        dias["payload_accessed"] = True
        with self.assertRaisesRegex(ProtocolError, "DIAS must remain"):
            validate_protocol(candidate)

    def test_source_delta_audit_rejects_all_candidates_before_p0(self) -> None:
        audit = self.protocol["problem_selection"]["source_delta_audit"]
        self.assertEqual(audit["best_score"], 31.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertTrue(audit["introai9_connection_verified"])
        self.assertEqual(audit["introai9_pbs_jobs_observed"], 0)
        self.assertFalse(audit["introai9_login_node_gpu_command_executed"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["source_delta_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "source-delta audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["source_delta_audit"]["candidates"][0][
            "payload_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "source-delta audit"):
            validate_protocol(candidate)

    def test_closed_problem_selection_cannot_select_method_or_gpu(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["method_selected"] = True
        with self.assertRaisesRegex(ProtocolError, "PINN direct-prior boundary"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["coarsening_at_random_assumed"] = True
        with self.assertRaisesRegex(ProtocolError, "PINN direct-prior boundary"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "PINN direct-prior boundary"):
            validate_protocol(candidate)

    def test_pinn_rupture_direct_prior_is_rejected_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "pinn_rupture_direct_prior_audit"
        ]
        self.assertEqual(audit["score"], 23.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(len(audit["axis_scores"]), 8)
        self.assertAlmostEqual(sum(audit["axis_scores"]), audit["score"])
        self.assertEqual(audit["aneux_source_patients"], 605)
        self.assertEqual(audit["direct_prior_rupture_status_cases"], 735)
        self.assertFalse(audit["patient_specific_boundary_conditions_available"])
        self.assertFalse(audit["paired_cfd_or_in_vivo_flow_validation_available"])
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["pinn_rupture_direct_prior_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "PINN rupture-status"):
            validate_protocol(candidate)

    def test_hemodynamic_endpoint_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "hemodynamic_endpoint_source_audit"
        ]
        self.assertEqual(audit["best_score"], 31.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertEqual(audit["aneurisk_cfd_source_cases"], 76)
        self.assertFalse(audit["aneurisk_cfd_archive_downloaded"])
        self.assertFalse(audit["aneurisk_cfd_patient_specific_measured_inflow"])
        self.assertFalse(
            audit["aneurisk_cfd_record_paper_outlet_condition_consistent"]
        )
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["hemodynamic_endpoint_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "hemodynamic-endpoint audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["hemodynamic_endpoint_source_audit"][
            "candidates"
        ][0]["payload_accessed"] = True
        with self.assertRaisesRegex(ProtocolError, "hemodynamic-endpoint audit"):
            validate_protocol(candidate)

    def test_topology_procedure_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "topology_procedure_source_audit"
        ]
        self.assertEqual(audit["best_score"], 28.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertEqual(audit["tornadic_cfd_wss_cases"], 3)
        self.assertEqual(audit["tornadic_mri_figure_cases"], 2)
        self.assertEqual(audit["tornadic_same_case_cfd_mri_pairs_reported"], 0)
        self.assertFalse(audit["tornadic_wss_archives_downloaded"])
        self.assertFalse(audit["tornadic_velocity_archive_downloaded"])
        self.assertFalse(audit["maximus_model_archive_downloaded"])
        self.assertFalse(audit["maximus_source_images_public_in_record"])
        self.assertEqual(audit["optimal_view_paper_patients"], 18)
        self.assertEqual(audit["rheology_slip_aneurysm_geometries"], 1)
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topology_procedure_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "topology-procedure audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topology_procedure_source_audit"][
            "maximus_model_archive_downloaded"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "topology-procedure audit"):
            validate_protocol(candidate)

    def test_context_treatment_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "context_treatment_source_audit"
        ]
        self.assertEqual(audit["best_score"], 31.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertEqual(audit["aneusi_paper_patients"], 99)
        self.assertEqual(audit["aneusi_paper_cases"], 102)
        self.assertEqual(audit["aneusi_repository_named_cases"], 103)
        self.assertFalse(audit["aneusi_paper_repository_case_count_reconciled"])
        self.assertFalse(audit["aneusi_spreadsheet_accessed"])
        self.assertFalse(audit["aneusi_vtk_payload_accessed"])
        self.assertEqual(audit["flow_mri_source_patient_anatomies"], 2)
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["observed_introai9_pbs_job_count"], 0)
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["context_treatment_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "context-treatment audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["context_treatment_source_audit"][
            "aneusi_vtk_payload_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "context-treatment audit"):
            validate_protocol(candidate)

    def test_provenance_evaluation_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "provenance_evaluation_source_audit"
        ]
        self.assertEqual(audit["best_score"], 30.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertEqual(audit["aneux_aneurisk_lesions"], 101)
        self.assertFalse(audit["aneux_case_level_cross_release_lineage_manifest_found"])
        self.assertEqual(audit["aneurisk_cfd_selected_geometries"], 76)
        self.assertFalse(audit["aneurisk_cfd_archive_accessed"])
        self.assertEqual(audit["public_aneurisk_mirror_named_model_folders"], 24)
        self.assertEqual(audit["public_aneurisk_mirror_label_files"], 15)
        self.assertTrue(audit["pointnet_external_set_used_in_reported_curve_selection"])
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["observed_introai9_pbs_job_count"], 0)
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["provenance_evaluation_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "provenance-evaluation audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["provenance_evaluation_source_audit"][
            "aneurisk_cfd_archive_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "provenance-evaluation audit"):
            validate_protocol(candidate)

    def test_treatment_surveillance_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "treatment_surveillance_source_audit"
        ]
        self.assertEqual(audit["best_score"], 30.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertEqual(audit["flow_diverter_subjects"], 126)
        self.assertEqual(audit["flow_diverter_procedures"], 141)
        self.assertFalse(audit["exact_biological_occlusion_time_observed"])
        self.assertFalse(audit["device_assignment_randomized"])
        self.assertEqual(audit["paired_mra_patients"], 22)
        self.assertEqual(audit["paired_mra_record_access_right"], "restricted")
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["observed_introai9_pbs_job_count"], 0)
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["treatment_surveillance_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "treatment-surveillance audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["treatment_surveillance_source_audit"][
            "device_assignment_randomized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "treatment-surveillance audit"):
            validate_protocol(candidate)

    def test_acquisition_flow_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"]["acquisition_flow_source_audit"]
        self.assertEqual(audit["best_score"], 27.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertEqual(audit["cmrx_train_fully_sampled_cases"], 138)
        self.assertEqual(audit["cmrx_cerebrovascular_validation_cases"], 10)
        self.assertEqual(audit["cmrx_cerebrovascular_test_cases"], 20)
        self.assertEqual(
            audit["cmrx_independent_research_embargo_ends"], "2026-12"
        )
        self.assertTrue(audit["cmrx_embargo_after_isbi_submission_deadline"])
        self.assertFalse(
            audit["cmrx_same_case_repeat_multi_venc_acquisitions_reported"]
        )
        self.assertEqual(audit["dual_venc_aneurysm_scans"], 8)
        self.assertEqual(audit["dual_venc_aneurysm_effective_anatomies"], 1)
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["observed_introai9_pbs_job_count"], 0)
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["acquisition_flow_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "acquisition-flow audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["acquisition_flow_source_audit"][
            "dual_venc_aneurysm_effective_anatomies"
        ] = 4
        with self.assertRaisesRegex(ProtocolError, "acquisition-flow audit"):
            validate_protocol(candidate)

    def test_vascular_semantics_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"]["vascular_semantics_source_audit"]
        self.assertEqual(audit["best_score"], 29.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["vascular_semantics_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "vascular-semantics audit"):
            validate_protocol(candidate)

    def test_aneux_orbit_p0_is_closed_without_payload_p1_or_training(self) -> None:
        audit = self.protocol["problem_selection"][
            "aneux_preprocessing_orbit_candidate"
        ]
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(audit["p0_scheduler_exit_status"], 2)
        self.assertEqual(audit["p0_error_code"], "transport_attempts_exhausted")
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["completed_tabular_archive_retained"])
        self.assertFalse(audit["model_central_directory_accessed"])
        self.assertFalse(audit["p1_authorized"])
        self.assertFalse(audit["transport_or_reader_repair_allowed"])

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["aneux_preprocessing_orbit_candidate"]
        audit["model_member_payload_accessed"] = True
        with self.assertRaisesRegex(ProtocolError, "preprocessing-orbit candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["aneux_preprocessing_orbit_candidate"]
        audit["full_model_archive_download_allowed"] = True
        with self.assertRaisesRegex(ProtocolError, "preprocessing-orbit candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["aneux_preprocessing_orbit_candidate"]
        audit["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "preprocessing-orbit candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["aneux_preprocessing_orbit_candidate"]
        audit["direct_prior_threats"].remove(
            "diffusionnet_discretization_agnostic_surface_learning"
        )
        with self.assertRaisesRegex(ProtocolError, "preprocessing-orbit candidate"):
            validate_protocol(candidate)

    def test_cycle_functional_p0_incomplete_is_closed(self) -> None:
        audit = self.protocol["problem_selection"][
            "aneug_cycle_functional_source_audit"
        ]
        self.assertEqual(audit["score"], 33.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertFalse(audit["processed_payload_accessed"])
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["same_contract_rerun_allowed"])
        self.assertEqual(audit["p0_scheduler_exit_status"], 28)
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneug_cycle_functional_source_audit"][
            "processed_payload_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "cycle-functional candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneug_cycle_functional_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "cycle-functional candidate"):
            validate_protocol(candidate)

    def test_inverse_counterfactual_source_rejection_cannot_register_or_train(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"][
            "inverse_healthy_vessel_counterfactual_source_audit"
        ]
        audit["aneumo_existing_64_case_cache_is_healthy_pathological_paired"] = True
        with self.assertRaisesRegex(ProtocolError, "inverse-counterfactual"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"][
            "inverse_healthy_vessel_counterfactual_source_audit"
        ]
        audit["executable_p0_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "inverse-counterfactual"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"][
            "inverse_healthy_vessel_counterfactual_source_audit"
        ]
        audit["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "inverse-counterfactual"):
            validate_protocol(candidate)

    def test_closed_goal_oriented_candidate_cannot_be_reopened(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["architecture_selected"] = True
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["cmha_stage_v2_evaluates_s0a"] = True
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["precompiled_su2_omp_release_is_s0a_eligible"] = True
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["s0a_pass_authorizes"] = "train_model"
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["s0a_asset_component_pass_authorizes"] = "train_model"
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["solver_runtime_preflight_status"] = "passed"
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["s0a_asset_component_gate"] = "9_of_9_passed"
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["s0a_failure_action"] = "register_solver_v2"
        with self.assertRaisesRegex(ProtocolError, "goal-oriented candidate"):
            validate_protocol(candidate)

    def test_cmha_cannot_be_restored_as_the_active_primary(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        cmha = next(item for item in candidate["datasets"] if item["name"] == "cmha")
        cmha["role"] = "active_primary"
        with self.assertRaisesRegex(ProtocolError, "closed 5/9"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        cmha = next(item for item in candidate["datasets"] if item["name"] == "cmha")
        cmha["status"] = "asset_gate_passed"
        with self.assertRaisesRegex(ProtocolError, "closed 5/9"):
            validate_protocol(candidate)

    def test_direct_prior_narrowing_cannot_be_removed_or_authorize_training(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["direct_prior_narrowing"]["method_or_gpu_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "direct-prior red team"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["goal_oriented_segmentation_cold_audit"]
        audit["direct_prior_narrowing"]["broad_claims_rejected"].pop()
        with self.assertRaisesRegex(ProtocolError, "direct-prior red team"):
            validate_protocol(candidate)

    def test_source_only_substitution_screen_cannot_open_data_or_training(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        screen = candidate["problem_selection"][
            "source_only_dataset_substitution_screen"
        ]
        screen["payload_accessed"] = True
        with self.assertRaisesRegex(ProtocolError, "source-only dataset"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        screen = candidate["problem_selection"][
            "source_only_dataset_substitution_screen"
        ]
        screen["candidate_ids"].remove("topcow_2024")
        with self.assertRaisesRegex(ProtocolError, "source-only dataset"):
            validate_protocol(candidate)

    def test_topaneu_source_audit_cannot_select_a_problem_or_accept_terms(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["topaneu_attachment_source_audit"]
        audit["topaneu_user_terms_accepted_verified"] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu attachment audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["topaneu_attachment_source_audit"]
        audit["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu attachment audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["topaneu_attachment_source_audit"]
        audit["score"] = audit["automatic_selection_threshold"]
        with self.assertRaisesRegex(ProtocolError, "TopAneu attachment audit"):
            validate_protocol(candidate)

    def test_topaneu_dataset_cannot_be_relabelled_as_staged_training_data(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        topaneu = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "topaneu_2026_terms_gated"
        )
        topaneu["payload_accessed"] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu must remain"):
            validate_protocol(candidate)

    def test_open_cta_metadata_discovery_cannot_authorize_headline_training(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        open_cta = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "open_multicenter_cta_2026_zenodo_15697196"
        )
        open_cta["headline_or_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "Open CTA must remain"):
            validate_protocol(candidate)

    def test_open_cta_metadata_discovery_hash_is_pinned(self) -> None:
        audit = self.protocol["problem_selection"]["topaneu_attachment_source_audit"]
        result = ROOT / audit["open_cta_discovery_result"]
        self.assertEqual(
            hashlib.sha256(result.read_bytes()).hexdigest(),
            audit["open_cta_discovery_result_sha256"],
        )

    def test_open_cta_physical_p0_cannot_be_relabelled_or_repaired(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["open_cta_physical_grid_candidate"]
        audit["p0_scientific_gate_evaluated"] = True
        with self.assertRaisesRegex(ProtocolError, "physical-grid P0"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["open_cta_physical_grid_candidate"]
        audit["parser_repair_allowed"] = True
        with self.assertRaisesRegex(ProtocolError, "physical-grid P0"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["open_cta_physical_grid_candidate"]
        audit["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "physical-grid P0"):
            validate_protocol(candidate)

    def test_open_cta_physical_p0_execution_record_hash_is_pinned(self) -> None:
        audit = self.protocol["problem_selection"]["open_cta_physical_grid_candidate"]
        result = ROOT / audit["p0_execution_record"]
        self.assertEqual(
            hashlib.sha256(result.read_bytes()).hexdigest(),
            audit["p0_execution_record_sha256"],
        )

    def test_open_cta_physical_p0_cannot_inflate_score_or_assume_patient_unit(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["open_cta_physical_grid_candidate"]
        audit["score"] = 40.0
        with self.assertRaisesRegex(ProtocolError, "physical-grid P0"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        open_cta = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "open_multicenter_cta_2026_zenodo_15697196"
        )
        open_cta["split_unit"] = "patient"
        with self.assertRaisesRegex(ProtocolError, "Open CTA must remain"):
            validate_protocol(candidate)

    def test_open_cta_physical_p0_direct_priors_are_frozen(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["open_cta_physical_grid_candidate"]
        audit["direct_prior_threats"].remove("consispace_voxel_spacing_resampling")
        with self.assertRaisesRegex(ProtocolError, "physical-grid P0"):
            validate_protocol(candidate)

    def test_attachment_direct_prior_threats_cannot_be_removed(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["non_novel_components"].remove(
            "patient_specific_centerline_graph_or_gnn"
        )
        with self.assertRaisesRegex(ProtocolError, "Direct prior-art boundaries"):
            validate_protocol(candidate)

    def test_rsna_semantics_audit_cannot_be_relabelled_as_lesion_masks(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["rsna_supervision_semantics_red_team"]
        audit["provided_segmentation_semantics"] = "aneurysm_masks"
        with self.assertRaisesRegex(ProtocolError, "supervision-semantics"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        audit = candidate["problem_selection"]["rsna_supervision_semantics_red_team"]
        audit["mixed_granularity_lesion_annotation_selection_cohort_supported"] = True
        with self.assertRaisesRegex(ProtocolError, "supervision-semantics"):
            validate_protocol(candidate)

    def test_rsna_candidate_cannot_claim_staging_or_redistribution(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        rsna = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "rsna_ica_2025_controlled_access"
        )
        rsna["status"] = "staged"
        with self.assertRaisesRegex(ProtocolError, "controlled-access"):
            validate_protocol(candidate)

    def test_prospective_endpoint_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["application_endpoint"] = "five_year_rupture_risk"
        with self.assertRaisesRegex(ProtocolError, "unselected"):
            validate_protocol(candidate)

    def test_historical_partial_bc_task_cannot_remain_primary(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["primary_problem"] = candidate["task"][
            "historical_primary_problem"
        ]
        with self.assertRaisesRegex(ProtocolError, "unselected"):
            validate_protocol(candidate)

    def test_i0a_pass_cannot_select_a_method_or_call_cfd_mri_truth(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["active_candidate_status"] = "method_selected"
        with self.assertRaisesRegex(ProtocolError, "source-shortlist/P0 only"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["cfd_field_is_clinical_mri_ground_truth"] = True
        with self.assertRaisesRegex(ProtocolError, "exact I0a result"):
            validate_protocol(candidate)

    def test_i0a_pass_must_retain_exact_result_and_limited_authorization(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["i0a_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "exact I0a result"):
            validate_protocol(candidate)

    def test_i0a_pass_cannot_imply_field_staging(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        flow_2021 = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "flow_mri_multiresolution_phantom_2021"
        )
        flow_2021["status"] = "field_staged"
        with self.assertRaisesRegex(ProtocolError, "field/REC access"):
            validate_protocol(candidate)

    def test_i0b_execution_record_cannot_select_method_or_read_REC(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["i0b_pass_authorizes"] = "select_method"
        with self.assertRaisesRegex(ProtocolError, "execution record"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        expanded = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "flow_mri_intervention_phantoms_2025"
        )
        expanded["status"] = "REC_read"
        with self.assertRaisesRegex(ProtocolError, "field/REC access"):
            validate_protocol(candidate)

    def test_i0b_execution_incomplete_cannot_be_repaired_or_open_i0c(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["i0b_execution_reentry_allowed"] = True
        with self.assertRaisesRegex(ProtocolError, "execution record"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["i0c_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "execution record"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["i0b_execution_gate"] = "failed"
        with self.assertRaisesRegex(ProtocolError, "execution record"):
            validate_protocol(candidate)

    def test_expanded_scans_cannot_become_independent_patient_units(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        expanded = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "flow_mri_intervention_phantoms_2025"
        )
        expanded["split_unit"] = "patient"
        with self.assertRaisesRegex(ProtocolError, "physical-unit"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["i0a_pass_authorizes"] = "method_selection"
        with self.assertRaisesRegex(ProtocolError, "exact I0a result"):
            validate_protocol(candidate)

    def test_isbi_target_cannot_be_marked_ready_while_primary_is_unselected(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["submission_ready"] = True
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)

    def test_m0_cannot_authorize_isbi_submission(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["m0_alone_may_authorize_submission"] = True
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)

    def test_v0_cannot_authorize_outer_test(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v0_pass_authorizes"] = "outer_test"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)

    def test_v0_pass_must_retain_public_result(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v0_result"] = "results/missing.json"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)

    def test_aneux_cannot_be_real_cfd(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        aneux = next(item for item in candidate["datasets"] if item["name"] == "aneux")
        aneux["field_provenance"] = "real_cfd"
        with self.assertRaisesRegex(ProtocolError, "AneuX"):
            validate_protocol(candidate)

    def test_aneumo_must_split_by_base_family(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        aneumo = next(item for item in candidate["datasets"] if item["name"] == "aneumo")
        aneumo["split_unit"] = "generator_seed_geometry"
        with self.assertRaisesRegex(ProtocolError, "base family"):
            validate_protocol(candidate)

    def test_aneumo_pressure_cannot_return_after_scaling_audit(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        output = candidate["model"]["irregular_3d_output_contract"]
        output["aneumo_current_candidate_channels"].append("pressure")
        with self.assertRaisesRegex(ProtocolError, "velocity-only"):
            validate_protocol(candidate)

    def test_aneumo_learning_remains_linked_to_g1s_and_v0(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        output = candidate["model"]["irregular_3d_output_contract"]
        output["protocol_registration_condition"] = "run_immediately"
        with self.assertRaisesRegex(ProtocolError, "G1s and the ISBI V0 pass"):
            validate_protocol(candidate)

    def test_irregular_3d_headline_requires_positive_m0_and_v2(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        output = candidate["model"]["irregular_3d_output_contract"]
        output["headline_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "positive M0"):
            validate_protocol(candidate)

    def test_v1_cannot_read_test_fields(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1_test_access"] = True
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)

    def test_failed_v1_cannot_enter_a_local_repair_or_open_v1a(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1_failure_action"] = "tune_hidden_dim_and_retry"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["model"]["irregular_3d_output_contract"][
            "v1a_status"
        ] = "completed_passed_open_v2"
        with self.assertRaisesRegex(ProtocolError, "independent V2 evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1a_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1b_pass_authorizes"] = "train_boundary_gnn"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1b_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1c_pass_authorizes"] = "train_boundary_operator"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["model"]["irregular_3d_output_contract"]["v1c_status"] = (
            "completed_passed_model_training_authorized"
        )
        with self.assertRaisesRegex(ProtocolError, "independent V2 evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1c_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1d_pass_authorizes"] = "train_known_condition_baseline"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["model"]["irregular_3d_output_contract"]["v1d_status"] = (
            "completed_test_geometry_opened"
        )
        with self.assertRaisesRegex(ProtocolError, "independent V2 evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1d_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1e_pass_authorizes"] = "run_scalar_missing_test"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1e_result_sha256"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["v1e_failure_action"] = "repair_and_retry"
        with self.assertRaisesRegex(ProtocolError, "3D evidence"):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["model"]["irregular_3d_output_contract"]["v1e_status"] = (
            "completed_passed_submission_ready"
        )
        with self.assertRaisesRegex(ProtocolError, "independent V2 evidence"):
            validate_protocol(candidate)

    def test_n0_cannot_establish_novelty(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0"
        )
        n0["may_establish_method_novelty"] = True
        with self.assertRaisesRegex(ProtocolError, "numerical adequacy"):
            validate_protocol(candidate)

    def test_failed_n0_cannot_authorize_n1(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0"
        )
        n0["n1_registration_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "cannot authorize N1"):
            validate_protocol(candidate)

    def test_failed_n0_requires_failed_checks(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0"
        )
        n0["failed_checks"] = []
        with self.assertRaisesRegex(ProtocolError, "failed checks"):
            validate_protocol(candidate)

    def test_n0a_cannot_authorize_or_tune_reentry(self) -> None:
        for key in ("may_authorize_n1", "may_select_n0r_thresholds_or_seeds"):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.protocol)
                n0a = next(
                    item
                    for item in candidate["nonlinear_protocols"]
                    if item["id"] == "N0a"
                )
                n0a[key] = True
                with self.assertRaisesRegex(ProtocolError, "attribution only"):
                    validate_protocol(candidate)

    def test_n0a_cannot_claim_uniform_nonlinearity(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0a = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0a"
        )
        n0a["uniformly_strong_nonlinearity_across_every_context"] = True
        with self.assertRaisesRegex(ProtocolError, "cannot be inflated"):
            validate_protocol(candidate)

    def test_n0r_cannot_change_after_n0a_outcome(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0r = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0r"
        )
        n0r["n0a_outcome_may_change_contract"] = True
        with self.assertRaisesRegex(ProtocolError, "independent"):
            validate_protocol(candidate)

    def test_n0r_requires_every_context(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0r = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0r"
        )
        n0r["reference_context_coverage"] = "12_of_24"
        with self.assertRaisesRegex(ProtocolError, "every context"):
            validate_protocol(candidate)

    def test_n0r_cannot_restore_failed_n0_or_3d_claim(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0r = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0r"
        )
        n0r["may_relabel_failed_n0"] = True
        with self.assertRaisesRegex(ProtocolError, "numerical adequacy"):
            validate_protocol(candidate)

    def test_passed_n0r_requires_exact_public_result(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n0r = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N0r"
        )
        n0r["failed_checks"] = ["nonlinear_departure"]
        with self.assertRaisesRegex(ProtocolError, "no failures"):
            validate_protocol(candidate)

    def test_passed_n0r_authorizes_registration_not_unregistered_training(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["status"] = "training"
        with self.assertRaisesRegex(ProtocolError, "unregistered training"):
            validate_protocol(candidate)

    def test_n1_cannot_drop_active_feature_baseline(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["mandatory_baselines"].remove("acquisition_conditioned_oracle")
        with self.assertRaisesRegex(ProtocolError, "AFA baselines"):
            validate_protocol(candidate)

    def test_n1_cannot_access_test_before_checkpoint_freeze(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["test_access_before_checkpoint_freeze"] = True
        with self.assertRaisesRegex(ProtocolError, "pre-freeze test access"):
            validate_protocol(candidate)

    def test_insufficient_n1_development_cannot_open_confirmatory_test(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["core_development"]["confirmatory_test_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "cannot decide"):
            validate_protocol(candidate)

    def test_n1_optimization_attribution_cannot_define_gate(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["optimization_attribution"]["has_success_threshold"] = True
        with self.assertRaisesRegex(ProtocolError, "non-gating"):
            validate_protocol(candidate)

    def test_n1c_attribution_cannot_rescue_the_failed_identity(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["post_result_attribution"]["result_summary"][
            "current_paper_identity_supported"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "density bottleneck"):
            validate_protocol(candidate)

    def test_post_n1c_audits_cannot_select_a_method(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["next_development_audits"]["density_objective"][
            "may_select_a_method"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "non-selecting"):
            validate_protocol(candidate)

    def test_decision_task_audit_cannot_load_a_checkpoint(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["next_development_audits"]["decision_task"][
            "uses_learned_model_or_checkpoint"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "non-selecting"):
            validate_protocol(candidate)

    def test_m0_incomplete_execution_cannot_enter_a_local_repair_loop(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["missing_operator_pullback_m0"][
            "failure_abandons_mechanism_without_local_weight_or_kernel_repair"
        ] = False
        with self.assertRaisesRegex(ProtocolError, "closed without local repair"):
            validate_protocol(candidate)

    def test_m0_cannot_open_test_or_reentry(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["missing_operator_pullback_m0"]["fresh_reentry_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "non-authorizing"):
            validate_protocol(candidate)

    def test_m0_incomplete_execution_cannot_be_given_a_gate_verdict(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["missing_operator_pullback_m0"]["gate_decided"] = True
        with self.assertRaisesRegex(ProtocolError, "incomplete no-verdict"):
            validate_protocol(candidate)

    def test_patient_bootstrap_is_required(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["evaluation"]["clinical_bootstrap_unit"] = "aneurysm"
        with self.assertRaisesRegex(ProtocolError, "patient"):
            validate_protocol(candidate)

    def test_paired_response_cannot_return_to_headline_objective(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["loss"]["paired_response"] = 0.5
        with self.assertRaisesRegex(ProtocolError, "paired-response"):
            validate_protocol(candidate)

    def test_v1_response_oracle_cannot_enter_selection_or_gate(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["model"]["irregular_3d_output_contract"][
            "v1_response_oracle_role"
        ] = "learned_reconstruction_selector"
        with self.assertRaisesRegex(ProtocolError, "independent V2 evidence"):
            validate_protocol(candidate)

    def test_paired_response_ablation_remains_explicit(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["loss"]["paired_response_ablation_weight"] = 0
        with self.assertRaisesRegex(ProtocolError, "named ablation"):
            validate_protocol(candidate)

    def test_duplicate_dataset_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["datasets"].append(copy.deepcopy(candidate["datasets"][0]))
        with self.assertRaisesRegex(ProtocolError, "duplicate"):
            validate_protocol(candidate)

    def test_fixed_fourier_cannot_return_without_a_new_contract(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["model"]["temporal_representation"]["fixed_fourier"] = "selected"
        with self.assertRaisesRegex(ProtocolError, "fixed Fourier"):
            validate_protocol(candidate)

    def test_dct_cannot_return_after_d0b(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["model"]["temporal_representation"]["candidate_bases"].append(
            "dct_ii"
        )
        with self.assertRaisesRegex(ProtocolError, "train-only POD"):
            validate_protocol(candidate)

    def test_same_benchmark_cannot_be_confirmatory_g3(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        g3 = next(item for item in candidate["gates"] if item["id"] == "G3")
        g3["same_benchmark_learned_comparison"] = "confirmatory"
        with self.assertRaisesRegex(ProtocolError, "exploratory"):
            validate_protocol(candidate)

    def test_post_result_diagnostic_cannot_reopen_g1(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["post_result_diagnostics"][0][
            "may_reopen_or_relabel_source_gate"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "cannot reopen"):
            validate_protocol(candidate)

    def test_density_attribution_cannot_define_a_gate(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        da1 = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "DA1"
        )
        da1["may_define_new_gate"] = True
        with self.assertRaisesRegex(ProtocolError, "define a new gate"):
            validate_protocol(candidate)

    def test_density_attribution_cannot_add_a_threshold(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        da1 = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "DA1"
        )
        da1["success_thresholds"] = {
            "maximum_density_only_standardized_mean_error": 0.05
        }
        with self.assertRaisesRegex(ProtocolError, "no threshold"):
            validate_protocol(candidate)

    def test_completed_density_attribution_cannot_authorize_3d(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        da1 = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "DA1"
        )
        da1["nonlinear_or_3d_confirmatory_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "cannot authorize"):
            validate_protocol(candidate)

    def test_density_development_cannot_pass_a_gate(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        da2 = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "DA2"
        )
        da2["may_define_or_pass_new_gate"] = True
        with self.assertRaisesRegex(ProtocolError, "cannot pass a gate"):
            validate_protocol(candidate)

    def test_density_development_requires_a_fresh_exact_gate(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        da2 = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "DA2"
        )
        da2["fresh_exact_gate_required_after_selection"] = False
        with self.assertRaisesRegex(ProtocolError, "fresh exact gate"):
            validate_protocol(candidate)

    def test_density_development_selects_at_original_data_budget(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        da2 = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "DA2"
        )
        da2["estimator_selection_cell"] = "3072x8"
        with self.assertRaisesRegex(ProtocolError, "original G1r budget"):
            validate_protocol(candidate)

    def test_density_development_cannot_promote_negligible_shrinkage(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        da2 = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "DA2"
        )
        da2["promote_grouped_estimator_to_method"] = True
        with self.assertRaisesRegex(ProtocolError, "did not support"):
            validate_protocol(candidate)

    def test_post_result_d0b_cannot_relabel_d0(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        d0b = next(
            item
            for item in candidate["post_result_diagnostics"]
            if item["id"] == "D0b"
        )
        d0b["may_reopen_or_relabel_source_gate"] = True
        with self.assertRaisesRegex(ProtocolError, "cannot relabel"):
            validate_protocol(candidate)

    def test_prospective_g1r_cannot_relabel_failed_g1(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["prospective_reentry_protocols"][0][
            "may_relabel_failed_source_gate"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "cannot relabel"):
            validate_protocol(candidate)

    def test_prospective_g1r_cannot_select_on_fresh_test(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["prospective_reentry_protocols"][0][
            "test_access_during_selection"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "validation-only"):
            validate_protocol(candidate)

    def test_prospective_g1r_thresholds_are_frozen(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["prospective_reentry_protocols"][0]["success_thresholds"][
            "maximum_density_only_standardized_mean_error"
        ] = 0.1
        with self.assertRaisesRegex(ProtocolError, "thresholds changed"):
            validate_protocol(candidate)

    def test_failed_g1r_cannot_authorize_complex_confirmation(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["prospective_reentry_protocols"][0][
            "nonlinear_or_3d_confirmatory_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "cannot authorize"):
            validate_protocol(candidate)

    def test_completed_g1r_must_retain_public_result(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        del candidate["prospective_reentry_protocols"][0]["result"]
        with self.assertRaisesRegex(ProtocolError, "missing"):
            validate_protocol(candidate)

    def test_g1s_must_retain_empirical_nll(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        g1s = next(
            item
            for item in candidate["prospective_reentry_protocols"]
            if item["id"] == "G1s"
        )
        g1s["density_estimator"] = "grouped_shrinkage_050"
        with self.assertRaisesRegex(ProtocolError, "empirical NLL"):
            validate_protocol(candidate)

    def test_g1s_must_retain_data_adequacy_budget(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        g1s = next(
            item
            for item in candidate["prospective_reentry_protocols"]
            if item["id"] == "G1s"
        )
        g1s["train_geometries"] = 768
        with self.assertRaisesRegex(ProtocolError, "3072x8"):
            validate_protocol(candidate)

    def test_g1s_thresholds_cannot_change(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        g1s = next(
            item
            for item in candidate["prospective_reentry_protocols"]
            if item["id"] == "G1s"
        )
        g1s["success_thresholds"][
            "maximum_density_only_standardized_mean_error"
        ] = 0.051
        with self.assertRaisesRegex(ProtocolError, "original G1r thresholds"):
            validate_protocol(candidate)

    def test_passed_g1s_must_authorize_next_domain(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        g1s = next(
            item
            for item in candidate["prospective_reentry_protocols"]
            if item["id"] == "G1s"
        )
        g1s["nonlinear_or_3d_confirmatory_training_authorized"] = False
        with self.assertRaisesRegex(ProtocolError, "completed G1s pass"):
            validate_protocol(candidate)

    def test_g1s_cannot_change_fresh_test_size(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        g1s = next(
            item
            for item in candidate["prospective_reentry_protocols"]
            if item["id"] == "G1s"
        )
        g1s["test_geometries"] = 512
        with self.assertRaisesRegex(ProtocolError, "unchanged 192/192"):
            validate_protocol(candidate)

    def test_g1s_cannot_promote_data_quantity_to_contribution(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        g1s = next(
            item
            for item in candidate["prospective_reentry_protocols"]
            if item["id"] == "G1s"
        )
        g1s["may_claim_data_quantity_as_method_contribution"] = True
        with self.assertRaisesRegex(ProtocolError, "method contribution"):
            validate_protocol(candidate)

    def test_n1b_manifest_state_cannot_open_test(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["prospective_reentry"]["test_generated_or_accessed"] = True
        with self.assertRaisesRegex(ProtocolError, "manifest must remain exact"):
            validate_protocol(candidate)

    def test_n1b_manifest_hash_is_pinned(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["prospective_reentry"]["checkpoint_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ProtocolError, "manifest must remain exact"):
            validate_protocol(candidate)

    def test_failed_n1c_cannot_be_relabelled_or_open_3d(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["outer_test_execution"]["n1_passed"] = True
        with self.assertRaisesRegex(ProtocolError, "Failed N1c must retain"):
            validate_protocol(candidate)


if __name__ == "__main__":
    unittest.main()
