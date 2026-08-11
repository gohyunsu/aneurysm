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

    def test_compute_is_introai9_only_with_no_gpu_authority(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["project"]["execution_server"] = "junjinyong"
        with self.assertRaisesRegex(ProtocolError, "introai9-only"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["project"]["current_gpu_job_count"] = 1
        with self.assertRaisesRegex(ProtocolError, "no tracked AURORA GPU job"):
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

    def test_top_level_problem_selection_cannot_select_method_or_gpu(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["method_selected"] = True
        with self.assertRaisesRegex(
            ProtocolError, "target-time/instability batch"
        ):
            validate_protocol(candidate)

    def test_future_source_admission_is_noncompensatory_and_prospective(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["open_model_transport_source_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertTrue(gate["prospective_only"])
        self.assertFalse(gate["historical_scores_relabelled"])
        self.assertEqual(gate["total_threshold"], 32.0)
        self.assertEqual(gate["critical_axis_minima"]["residual_novelty"], 2.5)
        self.assertEqual(audit["best_score"], 32.0)
        self.assertEqual(audit["best_residual_novelty_score"], 0.5)
        self.assertEqual(audit["conditional_source_lead_count"], 0)
        self.assertTrue(all(not item["critical_axis_pass"] for item in audit["candidates"]))
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["future_source_admission_v2"][
            "critical_axis_minima"
        ]["residual_novelty"] = 0.5
        with self.assertRaisesRegex(ProtocolError, "source admission v2"):
            validate_protocol(candidate)

    def test_target_time_and_instability_batch_is_rejected_before_compute(
        self,
    ) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["target_time_and_instability_prediction_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(audit["best_score"], 27.0)
        self.assertEqual(audit["best_residual_novelty_score"], 3.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [27.0, 26.5, 26.0, 25.5, 25.5, 25.5],
        )
        self.assertEqual(
            (
                audit["seven_hospital_patients_total"],
                audit["seven_hospital_aneurysms_total"],
                audit["seven_hospital_centres_total"],
            ),
            (852, 1111, 7),
        )
        self.assertEqual(
            (
                audit["seven_hospital_internal_patients"],
                audit["seven_hospital_internal_aneurysms"],
                audit["seven_hospital_external_patients"],
                audit["seven_hospital_external_aneurysms"],
                audit["seven_hospital_external_centres"],
            ),
            (646, 840, 206, 271, 6),
        )
        self.assertEqual(
            (
                audit["seven_hospital_source_auc_external_radiomics"],
                audit["seven_hospital_source_auc_external_conventional"],
                audit["seven_hospital_source_auc_external_combined"],
            ),
            (0.85, 0.61, 0.78),
        )
        self.assertEqual(
            (
                audit["vwi_transformer_patients"],
                audit["vwi_transformer_aneurysms"],
                audit["vwi_transformer_training_patients"],
                audit["vwi_transformer_validation_patients"],
            ),
            (293, 312, 205, 88),
        )
        self.assertEqual(
            (
                audit["vwi_transformer_source_validation_auc_fusion"],
                audit["vwi_transformer_source_validation_auc_densenet169"],
                audit[
                    "vwi_transformer_source_validation_auc_radiomics_habitat"
                ],
            ),
            (0.844, 0.816, 0.721),
        )
        self.assertFalse(
            audit["vwi_transformer_label_is_single_pure_future_event_estimand"]
        )
        self.assertEqual(audit["aneurysm_at_risk_estimated_enrollment"], 3800)
        self.assertEqual(audit["aneurysm_at_risk_centres"], 3)
        self.assertFalse(audit["aneurysm_at_risk_results_available"])
        self.assertTrue(
            all(
                sum(row["axis_scores"]) == row["total"]
                and not row["critical_axis_pass"]
                for row in audit["candidates"]
            )
        )
        self.assertFalse(
            audit[
                "joined_public_timestamped_multicentre_patient_lesion_image_mask_component_outcome_asset_identified"
            ]
        )
        self.assertFalse(audit["surface_vector_reactivated"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "target_time_and_instability_prediction_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(
            ProtocolError, "Target-time and instability prediction"
        ):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "target_time_and_instability_prediction_reappraisal"
        ][
            "joined_public_timestamped_multicentre_patient_lesion_image_mask_component_outcome_asset_identified"
        ] = True
        with self.assertRaisesRegex(
            ProtocolError, "Target-time and instability prediction"
        ):
            validate_protocol(candidate)

    def test_decision_time_and_clinical_precision_batch_is_rejected_before_compute(
        self,
    ) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["decision_time_and_clinical_precision_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(audit["best_score"], 30.0)
        self.assertEqual(audit["best_residual_novelty_score"], 3.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [30.0, 26.0, 25.5, 25.0, 24.5, 23.0],
        )
        self.assertEqual(
            (
                audit["ped_nomogram_patients"],
                audit["ped_nomogram_aneurysms"],
                audit["ped_nomogram_centres"],
                audit["ped_nomogram_multi_aneurysm_patients_one_ped"],
            ),
            (362, 426, 4, 61),
        )
        self.assertEqual(
            (
                audit["ped_nomogram_development_aneurysms"],
                audit["ped_nomogram_validation_aneurysms"],
                audit["ped_nomogram_median_followup_days"],
            ),
            (298, 128, 199),
        )
        self.assertTrue(audit["ped_nomogram_whole_cohort_random_split"])
        self.assertFalse(
            audit["ped_nomogram_patient_grouped_split_explicitly_stated"]
        )
        self.assertFalse(audit["ped_nomogram_centre_held_out_validation"])
        self.assertFalse(audit["ped_nomogram_pure_preoperative_information_set"])
        self.assertEqual(
            (
                audit["ped_nomogram_complete_occlusion_numerator"],
                audit["ped_nomogram_complete_occlusion_denominator"],
                audit["ped_nomogram_complete_occlusion_percent"],
            ),
            (340, 426, 79.8),
        )
        self.assertEqual(
            (
                audit["commercial_precision_patients"],
                audit["commercial_precision_aneurysms"],
                audit["commercial_precision_paired_cta_dsa_patients"],
            ),
            (148, 163, 86),
        )
        self.assertFalse(
            audit["commercial_precision_all_method_dsa_limits_within_threshold"]
        )
        self.assertTrue(audit["commercial_precision_cross_sectional_not_longitudinal"])
        self.assertEqual(
            (
                audit["autonomous_morphometry_patients"],
                audit["autonomous_morphometry_aneurysms"],
                audit["autonomous_morphometry_centres"],
            ),
            (2980, 2585, 5),
        )
        self.assertEqual(
            (
                audit["openneuro_longitudinal_patients"],
                audit["openneuro_same_session_control_patients"],
                audit["bayesian_direct_prior_public_patients_retained"],
                audit["bayesian_direct_prior_public_aneurysms_retained"],
                audit["bayesian_direct_prior_public_growth_positives"],
            ),
            (24, 4, 16, 19, 6),
        )
        self.assertTrue(
            all(
                sum(row["axis_scores"]) == row["total"]
                and not row["critical_axis_pass"]
                for row in audit["candidates"]
            )
        )
        self.assertFalse(
            audit[
                "joined_public_timestamped_patient_centre_image_cfd_device_outcome_asset_identified"
            ]
        )
        self.assertFalse(audit["surface_vector_reactivated"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "decision_time_and_clinical_precision_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "Decision-time and clinical precision"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "decision_time_and_clinical_precision_reappraisal"
        ][
            "joined_public_timestamped_patient_centre_image_cfd_device_outcome_asset_identified"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Decision-time and clinical precision"):
            validate_protocol(candidate)

    def test_device_planning_and_mechanistic_occlusion_batch_is_rejected_before_compute(
        self,
    ) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["device_planning_and_mechanistic_occlusion_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(audit["best_score"], 26.5)
        self.assertEqual(audit["best_residual_novelty_score"], 3.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [26.5, 25.0, 24.5, 24.5, 24.0, 23.5],
        )
        self.assertEqual(
            (
                audit["neuraneunet_reported_aneurysms"],
                audit["neuraneunet_non_ped_aneurysms"],
                audit["neuraneunet_ped_treated_aneurysms"],
            ),
            (600, 390, 210),
        )
        self.assertEqual(
            (
                audit["neuraneunet_ped_train_cases"],
                audit["neuraneunet_ped_validation_cases"],
                audit["neuraneunet_ped_test_cases"],
            ),
            (147, 21, 42),
        )
        self.assertFalse(
            audit["neuraneunet_patient_disjoint_split_explicitly_stated"]
        )
        self.assertEqual(
            (
                audit["neuraneunet_reader_cohort_cases"],
                audit["neuraneunet_reader_count"],
                audit["neuraneunet_reference_consensus_senior_readers"],
            ),
            (21, 6, 3),
        )
        self.assertEqual(
            (
                audit["neuraneunet_source_top1_agreement_numerator"],
                audit["neuraneunet_source_top1_agreement_denominator"],
                audit["neuraneunet_source_top1_agreement_percent"],
            ),
            (20, 21, 95.2),
        )
        self.assertFalse(
            audit["neuraneunet_long_term_occlusion_or_safety_endpoint_evaluated"]
        )
        self.assertFalse(audit["neuraneunet_data_public"])
        self.assertFalse(
            audit["neuraneunet_public_code_release_stated_in_inspected_paper"]
        )
        self.assertEqual(
            (
                audit["device_thrombosis_preprint"],
                audit["device_thrombosis_representative_geometries"],
                len(audit["device_thrombosis_treatment_strategies"]),
            ),
            ("arXiv:2605.03536v1", 3, 3),
        )
        self.assertFalse(audit["device_thrombosis_clinical_followup_validation"])
        self.assertFalse(
            audit["device_thrombosis_versioned_output_release_stated_in_inspected_v1"]
        )
        self.assertEqual(
            (
                audit["paired_treatment_4d_flow_datasets"],
                audit["paired_treatment_black_blood_datasets"],
                audit["paired_treatment_models"],
                audit["paired_treatment_source_patient_anatomies"],
                audit["paired_treatment_devices"],
            ),
            (33, 38, 5, 2, 15),
        )
        self.assertFalse(
            audit["volume_vortex_evidence_equates_surface_wss_critical_topology"]
        )
        self.assertFalse(
            audit[
                "joined_public_preop_device_flow_thrombus_delayed_outcome_asset_identified"
            ]
        )
        self.assertTrue(
            all(
                sum(row["axis_scores"]) == row["total"]
                and not row["critical_axis_pass"]
                for row in audit["candidates"]
            )
        )
        self.assertTrue(
            audit[
                "outcome_grounded_device_planning_retained_as_future_evaluation_template_only"
            ]
        )
        self.assertTrue(
            audit["surface_vector_volume_vortex_motivation_retained_without_e0"]
        )
        self.assertFalse(audit["surface_vector_reactivated"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "device_planning_and_mechanistic_occlusion_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(
            ProtocolError, "Device planning and mechanistic occlusion"
        ):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "device_planning_and_mechanistic_occlusion_reappraisal"
        ][
            "joined_public_preop_device_flow_thrombus_delayed_outcome_asset_identified"
        ] = True
        with self.assertRaisesRegex(
            ProtocolError, "Device planning and mechanistic occlusion"
        ):
            validate_protocol(candidate)

    def test_longitudinal_intervention_reliability_batch_rejects_additive_32(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem[
            "longitudinal_intervention_and_patient_reliability_reappraisal"
        ]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(audit["best_additive_score"], 32.0)
        self.assertEqual(audit["best_residual_novelty_score"], 1.5)
        self.assertEqual(
            audit["all_candidate_scores"],
            [32.0, 31.0, 29.5, 29.5, 26.5, 23.0],
        )
        self.assertEqual(audit["bayesian_growth_internal_patients"], 39)
        self.assertEqual(audit["bayesian_growth_internal_aneurysms"], 42)
        self.assertEqual(audit["bayesian_growth_public_patients_included"], 16)
        self.assertEqual(audit["bayesian_growth_public_aneurysms_included"], 19)
        self.assertTrue(
            audit[
                "bayesian_growth_public_pair_selection_uses_growth_event_representation"
            ]
        )
        self.assertFalse(audit["bayesian_growth_reported_results_reproduced_by_aurora"])
        self.assertEqual(audit["open_longitudinal_patients"], 63)
        self.assertEqual(audit["open_longitudinal_aneurysms"], 85)
        self.assertEqual(audit["rsna_second_place_training_series"], 4348)
        self.assertEqual(audit["rsna_second_place_split_unit"], "series")
        self.assertEqual(audit["flow_diverter_subjects"], 126)
        self.assertEqual(audit["flow_diverter_procedures"], 141)
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                and not candidate["critical_axis_pass"]
                for candidate in audit["candidates"]
            )
        )
        self.assertTrue(
            audit[
                "patient_level_all_lesion_reliability_retained_as_evaluation_template_only"
            ]
        )
        self.assertFalse(audit["surface_vector_reactivated"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "longitudinal_intervention_and_patient_reliability_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "Longitudinal/intervention"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "longitudinal_intervention_and_patient_reliability_reappraisal"
        ]["bayesian_growth_public_patients_included"] = 24
        with self.assertRaisesRegex(ProtocolError, "Longitudinal/intervention"):
            validate_protocol(candidate)

    def test_diagnostic_action_human_ai_batch_is_rejected_before_compute(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["diagnostic_action_and_human_ai_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(audit["best_score"], 29.5)
        self.assertEqual(audit["best_residual_novelty_score"], 0.5)
        self.assertEqual(
            audit["all_candidate_scores"],
            [29.5, 27.0, 26.0, 26.0, 25.0, 24.5],
        )
        self.assertEqual(audit["automation_bias_tof_mra_examinations"], 20)
        self.assertEqual(audit["automation_bias_radiologists"], 9)
        self.assertEqual(
            (
                audit["automation_bias_false_positive_vascular_loops"],
                audit["automation_bias_false_positive_infundibula"],
                audit["automation_bias_false_positive_perforators"],
            ),
            (5, 3, 2),
        )
        self.assertEqual(audit["iavs_reported_mra_volumes"], 641)
        self.assertEqual(audit["iavs_reported_annotations"], 587)
        self.assertEqual(audit["iavs_repository_blob_paths"], ["README.md"])
        self.assertIsNone(audit["iavs_repository_license"])
        self.assertEqual(
            audit["contrast_retention_cross_sectional_aneurysms"], 271
        )
        self.assertEqual(audit["contrast_retention_longitudinal_aneurysms"], 41)
        self.assertEqual(audit["marta_treated_patients"], 2647)
        self.assertTrue(
            all(
                sum(row["axis_scores"]) == row["total"]
                and not row["critical_axis_pass"]
                for row in audit["candidates"]
            )
        )
        self.assertFalse(audit["full_source_watch_refresh_completed"])
        self.assertFalse(audit["aneumo_metadata_request_completed"])
        self.assertTrue(audit["mimic_taxonomy_retained_as_future_evaluation_only"])
        self.assertFalse(audit["surface_vector_reactivated"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "diagnostic_action_and_human_ai_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "Diagnostic-action/human-AI"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "diagnostic_action_and_human_ai_reappraisal"
        ]["iavs_repository_blob_paths"] = ["README.md", "train.py"]
        with self.assertRaisesRegex(ProtocolError, "Diagnostic-action/human-AI"):
            validate_protocol(candidate)

    def test_adam_longitudinal_semantics_batch_is_rejected_before_compute(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["adam_longitudinal_and_treated_exclusion_source_correction"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [28.5, 28.0, 28.0, 27.0, 27.0, 24.5],
        )
        self.assertEqual(
            (
                audit["adam_training_cases"],
                audit["adam_training_positive_cases"],
                audit["adam_training_negative_cases"],
                audit["adam_training_paired_subjects"],
            ),
            (113, 93, 20, 35),
        )
        self.assertEqual(
            audit["adam_label_1_semantics"], "untreated_unruptured_aneurysm"
        )
        self.assertTrue(audit["adam_label_2_ignored_in_official_evaluation"])
        self.assertFalse(
            audit["adam_label_2_identifies_posttreatment_remnant_or_outcome"]
        )
        self.assertFalse(audit["adam_public_exact_pair_manifest_visible"])
        self.assertFalse(audit["adam_public_growth_adjudication_visible"])
        self.assertFalse(audit["adam_terms_accepted_by_aurora"])
        self.assertFalse(audit["adam_payload_accessed_this_schema"])
        self.assertTrue(
            all(
                sum(row["axis_scores"]) == row["total"]
                and not row["critical_axis_pass"]
                for row in audit["candidates"]
            )
        )
        self.assertTrue(
            audit["surface_vector_analysis_task_stability_sequence_retained"]
        )
        self.assertFalse(audit["surface_vector_material_e0_identified"])
        self.assertFalse(audit["surface_vector_reactivated"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "adam_longitudinal_and_treated_exclusion_source_correction"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(
            ProtocolError, "ADAM longitudinal/treated-exclusion"
        ):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "adam_longitudinal_and_treated_exclusion_source_correction"
        ]["adam_label_2_identifies_posttreatment_remnant_or_outcome"] = True
        with self.assertRaisesRegex(
            ProtocolError, "ADAM longitudinal/treated-exclusion"
        ):
            validate_protocol(candidate)

    def test_vmr_growth_paired_p0_closes_execution_incomplete_without_repair(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["vmr_growth_paired_surface_structure_source_audit"]
        task = self.protocol["task"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(audit["best_score"], 32.5)
        self.assertEqual(audit["primary_paper_patient_count"], 22)
        self.assertEqual(audit["primary_paper_matched_pair_count"], 11)
        self.assertEqual(audit["vmr_result_archive_count"], 22)
        self.assertEqual(audit["vmr_result_archive_total_bytes"], 1998793994)
        self.assertTrue(audit["p0_registered"])
        self.assertTrue(audit["p0_submitted"])
        self.assertTrue(audit["p0_cpu_only"])
        self.assertEqual(audit["p0_gpu_count"], 0)
        self.assertEqual(audit["p0_job_id"], "115848.ECE-util1")
        self.assertEqual(audit["p0_final_job_state"], "E")
        self.assertEqual(audit["p0_exit_status"], 2)
        self.assertEqual(audit["p0_scientific_checks_evaluated"], 0)
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["p0_archive_or_vtp_access_extent_known"])
        self.assertFalse(audit["p0_archive_or_vtp_persisted"])
        execution_path = ROOT / audit["p0_execution_record"]
        self.assertEqual(
            hashlib.sha256(execution_path.read_bytes()).hexdigest(),
            audit["p0_execution_record_sha256"],
        )
        self.assertFalse(audit["p1_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertTrue(audit["scientific_server_queried_this_schema"])
        self.assertFalse(audit["junjinyong_accessed"])
        self.assertEqual(task["active_candidate_problem"], "none")
        self.assertIsNone(task["candidate_primary_estimand"])
        self.assertIsNone(task["candidate_secondary_estimand"])
        self.assertEqual(
            sum(item["critical_axis_pass"] for item in audit["candidates"]),
            1,
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "vmr_growth_paired_surface_structure_source_audit"
        ]["p0_submitted"] = False
        with self.assertRaisesRegex(ProtocolError, "VMR audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        vmr = next(
            item
            for item in candidate["datasets"]
            if item["name"] == "vmr_growth_matched_cerebral_aneurysm"
        )
        vmr["matched_pairs"] = 22
        with self.assertRaisesRegex(ProtocolError, "VMR matched-pair"):
            validate_protocol(candidate)

    def test_neck_isolation_batch_is_rejected_without_payload_or_compute(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["neck_isolation_and_open_model_source_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(gate["current_batch_admitted_count"], 0)
        self.assertEqual(audit["best_score"], 31.5)
        self.assertEqual(audit["best_residual_novelty_score"], 0.5)
        self.assertEqual(audit["aneusi_visible_base_ids"], 99)
        self.assertEqual(audit["aneusi_model_files"], 103)
        self.assertEqual(audit["aneusi_derived_vtk_per_clip_factor"], 102)
        self.assertEqual(audit["aneusi_clip_factors"], [20, 25, 30, 35, 40, 45, 50])
        self.assertTrue(audit["aneusi_requires_input_neck_polygon"])
        self.assertFalse(audit["aneusi_vtk_or_ods_payload_body_accessed"])
        self.assertEqual(audit["neckspline_stated_code_url_http_status"], 401)
        self.assertFalse(audit["neckspline_code_or_annotation_payload_accessed"])
        self.assertEqual(audit["open_model_archive_bytes"], 1167744043)
        self.assertFalse(audit["open_model_archive_accessed"])
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                and not candidate["critical_axis_pass"]
                for candidate in audit["candidates"]
            )
        )
        self.assertFalse(audit["surface_vector_reactivated"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "neck_isolation_and_open_model_source_reappraisal"
        ]["aneusi_visible_base_ids"] = 103
        with self.assertRaisesRegex(ProtocolError, "Neck/isolation sources"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "neck_isolation_and_open_model_source_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "Neck/isolation sources"):
            validate_protocol(candidate)

    def test_latent_shape_open_cta_batch_is_rejected_without_payload_or_compute(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["latent_shape_open_cta_transport_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(audit["best_score"], 29.5)
        self.assertEqual(
            audit["all_candidate_scores"],
            [29.5, 29.0, 28.5, 28.0, 28.0, 23.0],
        )
        self.assertEqual(audit["paper_patient_derived_surfaces"], 958)
        self.assertEqual(audit["paper_ruptured_status_surfaces"], 338)
        self.assertEqual(audit["paper_lodo_auc"], 0.66)
        self.assertEqual(
            audit["repository_head"],
            "43e8219e947cfa318ab83a01df01c6602e7d5756",
        )
        self.assertFalse(audit["processed_obj_dataset_tracked"])
        self.assertFalse(audit["rupture_labels_csv_tracked"])
        self.assertTrue(
            audit[
                "released_training_scripts_use_default_seed42_file_level_80_20_split"
            ]
        )
        self.assertTrue(audit["unknown_status_label_condition_is_always_truthy"])
        self.assertFalse(audit["paper_results_invalidated_by_static_code_audit"])
        self.assertEqual(audit["vae_3k_cache_rows"], 885)
        self.assertEqual(audit["vae_3k_cache_ruptured_status"], 261)
        self.assertEqual(audit["open_cta_cases"], 172)
        self.assertEqual(audit["open_cta_lesions"], 122)
        self.assertEqual(audit["open_cta_ruptured_lesion_rows"], 9)
        self.assertFalse(audit["open_cta_stl_payload_accessed_this_schema"])
        self.assertFalse(audit["open_cta_dicom_pixel_accessed_this_schema"])
        self.assertFalse(
            audit["expert_morphology_category_treated_as_latent_support_ground_truth"]
        )
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                and not candidate["critical_axis_pass"]
                for candidate in audit["candidates"]
            )
        )
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "latent_shape_open_cta_transport_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "latent-shape/open-CTA"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "latent_shape_open_cta_transport_reappraisal"
        ]["paper_results_invalidated_by_static_code_audit"] = True
        with self.assertRaisesRegex(ProtocolError, "latent-shape/open-CTA"):
            validate_protocol(candidate)

    def test_topaneu_version_orbit_is_rejected_without_terms_or_p0(self) -> None:
        audit = self.protocol["problem_selection"][
            "topaneu_annotation_version_orbit_reappraisal"
        ]
        self.assertEqual(audit["best_additive_score"], 32.0)
        self.assertEqual(audit["most_relevant_candidate_score"], 31.5)
        self.assertEqual(audit["best_residual_novelty_score"], 2.0)
        self.assertEqual(audit["conditional_source_lead_count"], 0)
        self.assertEqual(audit["current_manifest_case_paths"], 417)
        self.assertEqual(audit["batch1_manifest_case_paths"], 98)
        self.assertEqual(
            audit["version_manifest_comparison"][
                "minimum_same_path_unchanged_image_and_changed_location_json"
            ],
            39,
        )
        self.assertFalse(audit["user_terms_acceptance_verified"])
        self.assertFalse(audit["individual_annotation_content_accessed"])
        self.assertFalse(audit["medical_image_or_mask_payload_accessed"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "topaneu_annotation_version_orbit_reappraisal"
        ]["p0_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu version orbit"):
            validate_protocol(candidate)

    def test_reference_provenance_and_rsna_batch_is_rejected_without_access(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem[
            "reference_provenance_and_rsna_release_contract_reappraisal"
        ]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(audit["best_score"], 31.0)
        self.assertEqual(audit["best_residual_novelty_score"], 2.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [31.0, 31.0, 29.5, 28.5, 28.0, 25.5],
        )
        self.assertTrue(audit["controlled_access_declared"])
        self.assertTrue(audit["data_resource_publication_forthcoming"])
        self.assertTrue(audit["wiki_page_is_coming_soon_only"])
        self.assertFalse(audit["machine_auditable_release_contract_present"])
        self.assertFalse(audit["clean_reference_subset_public"])
        self.assertFalse(audit["user_terms_acceptance_verified"])
        self.assertFalse(audit["mira_access_requested"])
        self.assertFalse(audit["registry_s3_medical_or_case_level_payload_accessed"])
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                and not candidate["critical_axis_pass"]
                for candidate in audit["candidates"]
            )
        )
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "reference_provenance_and_rsna_release_contract_reappraisal"
        ]["mira_access_requested"] = True
        with self.assertRaisesRegex(ProtocolError, "reference-provenance"):
            validate_protocol(candidate)

    def test_synva_release_and_synthetic_utility_batch_is_rejected(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["synva_release_and_synthetic_utility_source_audit"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(audit["best_score"], 27.5)
        self.assertEqual(
            audit["all_candidate_scores"],
            [27.5, 26.5, 26.0, 26.0, 23.5, 23.5],
        )
        self.assertEqual(audit["paper_claimed_synthetic_samples"], 50000)
        self.assertEqual(audit["paper_reported_real_test_samples"], 100)
        self.assertEqual(audit["paper_reported_downstream_regimes"], 11)
        self.assertFalse(audit["paper_results_reproduced_by_aurora"])
        self.assertFalse(audit["dedicated_synva_code_url_present_in_paper"])
        self.assertFalse(audit["dedicated_synva_dataset_url_present_in_paper"])
        self.assertFalse(audit["public_synva_github_repository_found"])
        self.assertFalse(audit["versioned_release_manifest_present"])
        self.assertFalse(audit["explicit_release_license_present"])
        self.assertFalse(audit["executable_real_split_manifest_present"])
        self.assertFalse(audit["patient_grouped_real_split_explicitly_reported"])
        self.assertTrue(audit["paper_reports_dataset_stratified_real_split"])
        self.assertFalse(audit["procedural_samples_are_patients"])
        self.assertFalse(audit["hemodynamic_construct_validity_reported"])
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                and not candidate["critical_axis_pass"]
                for candidate in audit["candidates"]
            )
        )
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "synva_release_and_synthetic_utility_source_audit"
        ]["versioned_release_manifest_present"] = True
        with self.assertRaisesRegex(ProtocolError, "SynVA v1 source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "synva_release_and_synthetic_utility_source_audit"
        ]["method_selected"] = True
        with self.assertRaisesRegex(ProtocolError, "SynVA v1 source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "reference_provenance_and_rsna_release_contract_reappraisal"
        ]["method_selected"] = True
        with self.assertRaisesRegex(ProtocolError, "reference-provenance"):
            validate_protocol(candidate)

    def test_aaa_cross_scale_sources_do_not_create_a_model_or_patient_join(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["aaa_cross_scale_source_reappraisal"]
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(audit["best_score"], 30.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [30.0, 28.5, 26.5, 26.5, 23.0, 22.0],
        )
        self.assertEqual(audit["regional_wall_stress_geo_id"], "GSE205071")
        self.assertEqual(audit["regional_wall_stress_independent_patients"], 12)
        self.assertFalse(
            audit["regional_wall_stress_public_image_mesh_field_coordinate_contract"]
        )
        self.assertEqual(audit["source_cta_measurement_cases"], 258)
        self.assertEqual(audit["selected_virtual_geometries"], 182)
        self.assertEqual(audit["reported_cfd_simulations"], 364)
        self.assertFalse(
            audit["selected_virtual_geometries_treated_as_observed_patients"]
        )
        self.assertFalse(audit["public_real_cta_image_cohort_present"])
        self.assertFalse(
            audit["public_real_patient_paired_cfd_outer_reference_present"]
        )
        self.assertFalse(
            audit["zip_xlsx_example_case_cfd_expression_or_image_payload_accessed"]
        )
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                and not candidate["critical_axis_pass"]
                for candidate in audit["candidates"]
            )
        )
        self.assertFalse(audit["recurring_source_watch_added"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aaa_cross_scale_source_reappraisal"][
            "best_score"
        ] = 32.0
        with self.assertRaisesRegex(ProtocolError, "AAA cross-scale"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aaa_cross_scale_source_reappraisal"][
            "architecture_selected"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "AAA cross-scale"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["open_model_transport_source_reappraisal"][
            "p0_registered"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "open-model transport batch"):
            validate_protocol(candidate)

    def test_mris_bench_target_contract_is_rejected_before_payload_or_model(self) -> None:
        problem = self.protocol["problem_selection"]
        gate = problem["future_source_admission_v2"]
        audit = problem["mris_bench_target_contract_audit"]
        self.assertEqual(gate["current_batch_best_score"], 27.0)
        self.assertEqual(gate["current_batch_best_residual_novelty"], 3.0)
        self.assertEqual(audit["best_score"], 24.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [24.0, 23.5, 23.0, 22.5, 22.0, 21.0],
        )
        self.assertEqual(audit["public_rows_reported"], 30110)
        self.assertFalse(audit["machine_schema_mask_field_present"])
        self.assertIsNone(audit["state_split"])
        self.assertFalse(audit["patient_grouping_public"])
        self.assertFalse(audit["row_count_treated_as_independent_patient_count"])
        self.assertFalse(audit["arrow_or_image_payload_accessed"])
        self.assertFalse(audit["visible_viewer_examples_are_registered_quality_prevalence"])
        self.assertTrue(
            all(not item["critical_axis_pass"] for item in audit["candidates"])
        )
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["mris_bench_target_contract_audit"][
            "arrow_or_image_payload_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "MRIS-Bench"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["mris_bench_target_contract_audit"][
            "machine_schema_mask_field_present"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "MRIS-Bench"):
            validate_protocol(candidate)

    def test_cross_vascular_transient_wss_batch_is_rejected(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["cross_vascular_transient_wss_source_correction"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 30.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [30.0, 29.0, 28.5, 25.5, 23.0, 21.5],
        )
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                for candidate in audit["candidates"]
            )
        )
        self.assertEqual(audit["aaa_wss_training_patients"], 100)
        self.assertEqual(audit["aaa_wss_external_patients"], 29)
        self.assertEqual(audit["aaa_wss_external_scans"], 118)
        self.assertEqual(audit["aaa_wss_total_cfd_simulations"], 1090)
        self.assertTrue(audit["aaa_wss_reports_transient_vector_wss"])
        self.assertTrue(audit["aaa_wss_reports_high_frequency_directional_oversmoothing"])
        self.assertFalse(
            audit["aaa_wss_evaluates_signed_degree_critical_points_or_worldlines"]
        )
        self.assertEqual(audit["aaa_wss_repository_commit_count"], 1)
        self.assertEqual(audit["aaa_wss_repository_readme_bytes"], 183)
        self.assertFalse(
            audit["aaa_wss_repository_contains_implementation_checkpoint_or_cfd_fields"]
        )
        self.assertEqual(audit["aaa100_patient_geometries"], 100)
        self.assertFalse(audit["aaa100_transient_cfd_fields_public"])
        self.assertEqual(audit["sano_independent_patient_cases"], 12)
        self.assertTrue(audit["sano_flow_is_steady_state"])
        self.assertFalse(audit["sano_payload_accessed"])
        self.assertTrue(audit["surface_vector_question_retained_as_inactive_hypothesis"])
        self.assertFalse(audit["architecture_selected_from_direct_prior"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])
        self.assertEqual(
            problem["most_recent_source_rejected_candidate"],
            "target_time_disjoint_future_event_benchmark_rejected_at_27_no_timestamped_multicentre_public_asset",
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "cross_vascular_transient_wss_source_correction"
        ]["best_score"] = 32.0
        with self.assertRaisesRegex(ProtocolError, "cross-vascular transient-WSS"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "cross_vascular_transient_wss_source_correction"
        ]["architecture_selected"] = True
        with self.assertRaisesRegex(ProtocolError, "cross-vascular transient-WSS"):
            validate_protocol(candidate)

    def test_posttreatment_reference_linked_imaging_batch_is_rejected(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["posttreatment_reference_linked_imaging_source_delta"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 28.5)
        self.assertEqual(
            audit["all_candidate_scores"],
            [28.5, 27.5, 26.5, 26.5, 26.0, 24.5],
        )
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["total"]
                for candidate in audit["candidates"]
            )
        )
        self.assertEqual(audit["petra_prospective_patients"], 100)
        self.assertEqual(audit["petra_stent_assisted_coiling_units"], 72)
        self.assertEqual(audit["petra_flow_diverter_units"], 28)
        self.assertTrue(audit["petra_dsa_reference_at_both_timepoints"])
        self.assertFalse(audit["petra_raw_data_publicly_versioned"])
        self.assertFalse(audit["petra_raw_images_accessed"])
        self.assertEqual(audit["helsinki_treated_patients_with_dwi"], 119)
        self.assertEqual(
            audit["helsinki_patients_with_six_month_angiographic_followup"], 113
        )
        self.assertFalse(audit["helsinki_researcher_initiated_data_sharing_possible"])
        self.assertTrue(audit["helsinki_findata_official_decision_required"])
        self.assertEqual(audit["clipped_table_patients"], 58)
        self.assertFalse(audit["clipped_table_contains_raw_cta_tof_or_petra_images"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])
        self.assertEqual(
            problem["most_recent_source_rejected_candidate"],
            "target_time_disjoint_future_event_benchmark_rejected_at_27_no_timestamped_multicentre_public_asset",
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "posttreatment_reference_linked_imaging_source_delta"
        ]["best_score"] = 32.0
        with self.assertRaisesRegex(
            ProtocolError, "post-treatment reference-linked imaging source delta"
        ):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "posttreatment_reference_linked_imaging_source_delta"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(
            ProtocolError, "post-treatment reference-linked imaging source delta"
        ):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["coarsening_at_random_assumed"] = True
        with self.assertRaisesRegex(
            ProtocolError, "target-time/instability batch"
        ):
            validate_protocol(candidate)
        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(
            ProtocolError, "target-time/instability batch"
        ):
            validate_protocol(candidate)

    def test_aneug_target_construction_audit_rejects_compute_and_score_repair(self) -> None:
        audit = self.protocol["problem_selection"][
            "aneug_target_construction_source_audit"
        ]
        self.assertEqual(audit["best_score"], 31.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertFalse(audit["field_or_mesh_payload_accessed"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["introai9_pbs_jobs_observed"], 0)
        self.assertFalse(audit["login_node_gpu_command_executed"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "aneug_target_construction_source_audit"
        ]["best_score"] = 32.0
        with self.assertRaisesRegex(ProtocolError, "AneuG target-construction"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "aneug_target_construction_source_audit"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "AneuG target-construction"):
            validate_protocol(candidate)

    def test_aneug_surface_vector_structure_p0_closes_execution_incomplete(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["aneug_surface_vector_structure_source_audit"]
        self.assertEqual(problem["conditional_source_lead_count"], 0)
        self.assertIsNone(problem["shortlisted_candidate"])
        self.assertEqual(audit["score"], 32.0)
        self.assertEqual(sum(audit["axis_scores"]), 32.0)
        self.assertEqual(audit["registered_probe_cases"], 3)
        self.assertEqual(audit["registered_total_bytes"], 276642685)
        self.assertTrue(audit["executable_p0_registered"])
        self.assertTrue(audit["p0_job_submitted"])
        self.assertEqual(audit["p0_job_id"], "115645.ECE-util1")
        self.assertEqual(audit["p0_final_job_state"], "E")
        self.assertEqual(audit["p0_exit_status"], 2)
        self.assertEqual(audit["p0_registered_high_level_checks_evaluated"], 0)
        self.assertFalse(audit["p0_aggregate_scientific_result_materialized"])
        self.assertFalse(audit["p0_raw_scheduler_output_materialized"])
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["p1_registration_authorized"])
        execution_path = ROOT / audit["p0_execution_record"]
        self.assertEqual(
            hashlib.sha256(execution_path.read_bytes()).hexdigest(),
            audit["p0_execution_record_sha256"],
        )
        self.assertFalse(audit["field_or_mesh_payload_accessed"])
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["pbs_ngpus"], 0)
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "aneug_surface_vector_structure_source_audit"
        ]["score"] = 32.5
        with self.assertRaisesRegex(ProtocolError, "surface-vector structure"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "aneug_surface_vector_structure_source_audit"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "surface-vector structure"):
            validate_protocol(candidate)

    def test_surface_vector_is_retained_only_as_an_inactive_hypothesis(self) -> None:
        problem = self.protocol["problem_selection"]
        assessment = problem["surface_vector_conditional_assessment"]
        task = self.protocol["task"]
        self.assertEqual(problem["conditional_source_lead_count"], 0)
        self.assertEqual(task["active_candidate_problem"], "none")
        self.assertIsNone(task["candidate_primary_estimand"])
        self.assertIsNone(task["candidate_secondary_estimand"])
        self.assertEqual(assessment["historical_source_score"], 32.0)
        self.assertTrue(assessment["historical_p0_closed"])
        self.assertFalse(assessment["historical_p0_job_running"])
        self.assertFalse(assessment["architecture_selected"])
        self.assertFalse(assessment["executable_p0_registered"])
        self.assertFalse(assessment["gpu_training_authorized"])
        self.assertTrue(
            assessment["new_evidence_version_requires_material_source_or_asset_change"]
        )
        self.assertFalse(
            assessment["new_wrapper_downloader_retry_or_model_name_is_new_evidence"]
        )
        self.assertEqual(assessment["execution_server"], "introai9")
        self.assertFalse(assessment["junjinyong_accessed_for_this_assessment"])
        self.assertEqual(
            assessment["primary_method_free_endpoints_before_e1"],
            [
                "boundary_margin_signed_total_degree_validity",
                "certificate_efficiency_and_abstention",
            ],
        )
        self.assertFalse(
            assessment["critical_point_or_worldline_primary_before_e1_allowed"]
        )
        self.assertFalse(
            assessment["structural_training_loss_before_e2_failure_allowed"]
        )
        self.assertEqual(len(assessment["isbi_result_contract_all_required"]), 5)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["surface_vector_conditional_assessment"][
            "architecture_selected"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "inactive conditional hypothesis"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["surface_vector_conditional_assessment"][
            "new_wrapper_downloader_retry_or_model_name_is_new_evidence"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "material source change"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["surface_vector_conditional_assessment"][
            "critical_point_or_worldline_primary_before_e1_allowed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "inactive conditional hypothesis"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["surface_vector_conditional_assessment"][
            "historical_p0_job_running"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "inactive conditional hypothesis"):
            validate_protocol(candidate)

    def test_virtual_removal_pair_corrects_source_but_opens_no_model(self) -> None:
        audit = self.protocol["problem_selection"][
            "expert_virtual_removal_pair_source_delta"
        ]
        self.assertEqual(audit["score"], 28.5)
        self.assertEqual(sum(audit["axis_scores"]), 28.5)
        self.assertEqual(audit["figshare_file_count"], 30)
        self.assertEqual(
            audit["figshare_canonical_name_size_md5_manifest_sha256"],
            "875cc1f92f586ab4c9fba8b28180b57fa2c2e58657c6a98c2fb98e128e04a2fb",
        )
        self.assertEqual(audit["independent_paired_case_units"], 10)
        self.assertTrue(audit["target_is_investigator_virtual_removal"])
        self.assertFalse(
            audit["target_is_observed_same_patient_preaneurysm_anatomy"]
        )
        self.assertTrue(audit["license_statements_conflict"])
        self.assertFalse(audit["payload_accessed"])
        self.assertFalse(audit["surface_vector_e0_satisfied"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["server_queried"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "expert_virtual_removal_pair_source_delta"
        ]["target_is_observed_same_patient_preaneurysm_anatomy"] = True
        with self.assertRaisesRegex(ProtocolError, "virtual-removal pair"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "expert_virtual_removal_pair_source_delta"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "virtual-removal pair"):
            validate_protocol(candidate)

    def test_inverse_flow_delta_rejects_all_candidates_and_opens_no_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "measurement_functional_inverse_flow_source_delta"
        ]
        self.assertEqual(audit["best_score"], 30.0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["score"]
                for candidate in audit["candidates"]
            )
        )
        self.assertLess(
            max(candidate["score"] for candidate in audit["candidates"]),
            audit["automatic_selection_threshold"],
        )
        self.assertEqual(audit["new_direct_prior_arxiv"], "2607.20224")
        self.assertEqual(audit["new_direct_prior_reported_geometries"], 3)
        self.assertEqual(audit["benchanxplore_cases"], 105)
        self.assertEqual(audit["benchanxplore_timeframes"], 80)
        self.assertTrue(audit["benchanxplore_common_idealized_parent_vessel"])
        self.assertFalse(
            audit["benchanxplore_compact_pressure_or_wss_contract_verified"]
        )
        self.assertTrue(
            audit["benchanxplore_all_cases_previously_used_for_representation_selection"]
        )
        self.assertEqual(audit["flowmri_cerebrovascular_volunteers"], 10)
        self.assertEqual(audit["flowmri_cerebrovascular_reference_test_volunteers"], 1)
        self.assertFalse(audit["new_payload_accessed"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["server_queried"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "measurement_functional_inverse_flow_source_delta"
        ]["best_score"] = 32.0
        with self.assertRaisesRegex(ProtocolError, "inverse-flow batch"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "measurement_functional_inverse_flow_source_delta"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "inverse-flow batch"):
            validate_protocol(candidate)

    def test_structure_faithful_wss_reappraisal_rejects_without_compute(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["structure_faithful_wss_source_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 31.0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["score"]
                for candidate in audit["candidates"]
            )
        )
        self.assertLess(
            max(candidate["score"] for candidate in audit["candidates"]),
            audit["automatic_selection_threshold"],
        )
        self.assertEqual(audit["aneurisk_geometries"], 76)
        self.assertTrue(audit["aneurisk_public_readme_accessed"])
        self.assertFalse(audit["aneurisk_archive_or_vtp_payload_accessed"])
        self.assertFalse(audit["aneug_material_source_change_observed"])
        self.assertTrue(
            audit["critical_points_and_worldlines_start_as_evaluation_not_loss"]
        )
        self.assertTrue(
            audit["hodge_is_required_strong_baseline_not_selected_proposal"]
        )
        self.assertFalse(audit["edge_one_form_guarantees_critical_point_fidelity"])
        self.assertEqual(audit["cfd_challenge_independent_anatomy_count"], 5)
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["server_queried"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertEqual(
            problem["most_recent_source_rejected_candidate"],
            "target_time_disjoint_future_event_benchmark_rejected_at_27_no_timestamped_multicentre_public_asset",
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "structure_faithful_wss_source_reappraisal"
        ]["best_score"] = 32.0
        with self.assertRaisesRegex(ProtocolError, "structure-faithful WSS"):
            validate_protocol(candidate)

    def test_conformal_degree_candidate_closes_after_incomplete_cpu_p0(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["conformal_degree_certificate_source_audit"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 32.5)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["conditional_source_lead_count"], 0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertFalse(audit["new_estimand_is_historical_endpoint_fidelity_score_repair"])
        self.assertTrue(audit["historical_surface_vector_source_scores_preserved"])
        self.assertFalse(audit["historical_surface_vector_p0_rerun_or_repair"])
        self.assertFalse(
            audit["certificate_guarantees_exact_critical_point_count_location_or_type"]
        )
        self.assertTrue(
            audit["certificate_guarantees_nonzero_degree_implies_at_least_one_zero"]
        )
        self.assertEqual(audit["independent_unit"], "patient")
        self.assertEqual(audit["reported_patient_specific_geometries"], 76)
        self.assertFalse(audit["archive_or_vtp_payload_accessed"])
        self.assertTrue(audit["p0_registered"])
        self.assertTrue(audit["p0_job_submitted"])
        self.assertEqual(audit["p0_job_id"], "115684.ECE-util1")
        self.assertEqual(audit["p0_final_job_state"], "E")
        self.assertEqual(audit["p0_exit_status"], 2)
        self.assertEqual(audit["p0_walltime"], "00:40:06")
        self.assertEqual(audit["p0_cput"], "00:00:01")
        self.assertEqual(audit["p0_scientific_checks_evaluated"], 0)
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["p0_aggregate_scientific_result_created"])
        self.assertFalse(audit["p0_raw_scheduler_log_materialized"])
        execution_path = ROOT / audit["p0_execution_record"]
        self.assertEqual(
            hashlib.sha256(execution_path.read_bytes()).hexdigest(),
            audit["p0_execution_record_sha256"],
        )
        self.assertEqual(audit["p0_scientific_check_count"], 10)
        self.assertFalse(audit["p0_critical_point_or_conformal_computation"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertTrue(audit["server_queried_for_this_audit"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["conformal_degree_certificate_source_audit"][
            "best_score"
        ] = 33.0
        with self.assertRaisesRegex(ProtocolError, "conformal-degree audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["conformal_degree_certificate_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "conformal-degree audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "structure_faithful_wss_source_reappraisal"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "structure-faithful WSS"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "structure_faithful_wss_source_reappraisal"
        ]["critical_points_and_worldlines_start_as_evaluation_not_loss"] = False
        with self.assertRaisesRegex(ProtocolError, "structure-faithful WSS"):
            validate_protocol(candidate)

    def test_cross_view_projection_batch_rejects_proxy_and_no_compute(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["cross_view_projection_source_delta"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 31.0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertLess(
            max(candidate["score"] for candidate in audit["candidates"]),
            audit["automatic_selection_threshold"],
        )
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["score"]
                for candidate in audit["candidates"]
            )
        )
        self.assertEqual(audit["midl_source_cases"], 113)
        self.assertFalse(audit["midl_source_uses_real_clinical_biplane_dsa"])
        self.assertFalse(audit["midl_source_inference_uses_both_views"])
        self.assertTrue(
            audit["adam_registration_and_confidentiality_agreement_required"]
        )
        self.assertFalse(audit["adam_payload_accessed"])
        self.assertEqual(audit["sdan_clinical_dsa_images"], 62187)
        self.assertFalse(audit["sdan_public_distribution_permitted"])
        self.assertTrue(audit["sdan_reasonable_request_only"])
        self.assertEqual(audit["path_length_correction_independent_cases"], 3)
        self.assertFalse(audit["p0_or_p1_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["server_queried"])
        self.assertFalse(audit["pbs_or_gpu_job_created"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["cross_view_projection_source_delta"][
            "best_score"
        ] = 32.0
        with self.assertRaisesRegex(ProtocolError, "cross-view projection"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["cross_view_projection_source_delta"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "cross-view projection"):
            validate_protocol(candidate)

    def test_functional_4dflow_segmentation_batch_is_direct_prior_limited(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["functional_4dflow_segmentation_source_delta"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 25.5)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertLess(
            max(candidate["score"] for candidate in audit["candidates"]),
            audit["automatic_selection_threshold"],
        )
        self.assertTrue(
            all(
                sum(candidate["axis_scores"]) == candidate["score"]
                for candidate in audit["candidates"]
            )
        )
        self.assertEqual(audit["tof_mra_pretraining_scans"], 355)
        self.assertEqual(audit["clinical_7t_4dflow_scans"], 11)
        self.assertFalse(audit["tof_pretraining_scans_are_downstream_4dflow_units"])
        self.assertEqual(audit["segmentation_target"], "circle_of_willis_not_aneurysm_sac")
        self.assertTrue(audit["time_resolved_wss_uses_time_averaged_static_mask"])
        self.assertFalse(audit["clinical_imaging_publicly_shareable"])
        self.assertFalse(audit["trained_weights_currently_released"])
        self.assertTrue(audit["weights_promised_upon_publication"])
        self.assertFalse(audit["clinical_image_or_mask_payload_accessed"])
        self.assertFalse(audit["model_weight_or_checkpoint_accessed"])
        self.assertFalse(audit["p0_or_p1_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["server_queried"])
        self.assertFalse(audit["pbs_or_gpu_job_created"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertEqual(
            problem["most_recent_source_rejected_candidate"],
            "target_time_disjoint_future_event_benchmark_rejected_at_27_no_timestamped_multicentre_public_asset",
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["functional_4dflow_segmentation_source_delta"][
            "best_score"
        ] = 32.0
        with self.assertRaisesRegex(ProtocolError, "functional 4D-flow segmentation"):
            validate_protocol(candidate)

    def test_aneux_transient_material_source_is_rejected_without_access(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["aneux_transient_cfd_material_source_audit"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 28.0)
        self.assertLess(
            max(audit["all_candidate_scores"]),
            audit["automatic_selection_threshold"],
        )
        self.assertEqual(audit["dataset_gated"], "manual")
        self.assertFalse(audit["user_terms_or_contact_sharing_accepted"])
        self.assertEqual(audit["topology_qualified_case_folders"], 323)
        self.assertEqual(audit["unique_visible_case_ids"], 322)
        self.assertEqual(audit["cross_topology_overlap_ids"], ["SNF365"])
        self.assertFalse(audit["visible_id_is_verified_patient_or_base_family"])
        self.assertFalse(audit["tensor_mesh_or_raw_readme_payload_accessed"])
        self.assertTrue(audit["material_source_change_signal"])
        self.assertFalse(audit["e0_pass"])
        self.assertFalse(audit["historical_aneug_p0_repair_or_rerun_authorized"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])
        self.assertEqual(
            problem["most_recent_source_rejected_candidate"],
            "target_time_disjoint_future_event_benchmark_rejected_at_27_no_timestamped_multicentre_public_asset",
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneux_transient_cfd_material_source_audit"][
            "best_score"
        ] = 32.0
        with self.assertRaisesRegex(ProtocolError, "AneuX-derived transient-CFD"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneux_transient_cfd_material_source_audit"][
            "user_terms_or_contact_sharing_accepted"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "AneuX-derived transient-CFD"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["functional_4dflow_segmentation_source_delta"][
            "trained_weights_currently_released"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "functional 4D-flow segmentation"):
            validate_protocol(candidate)

    def test_source_watch_v4_is_metadata_only_and_fail_closed(self) -> None:
        watch = self.protocol["problem_selection"]["public_source_watch_v4"]
        self.assertEqual(watch["config"], "configs/source_watch_v4.json")
        self.assertEqual(watch["watch_count"], 5)
        self.assertEqual(watch["aneumo_github_release_count"], 0)
        self.assertIsNone(watch["aneumo_github_license_spdx_id"])
        self.assertEqual(watch["aneumo_huggingface_sibling_count"], 370)
        self.assertEqual(watch["aneumo_real_case_or_mapping_entries"], [])
        self.assertTrue(
            watch["maintainer_future_real_undeformed_release_statement_not_material_e0"]
        )
        self.assertTrue(watch["same_as_all_frozen_snapshots"])
        self.assertFalse(watch["manual_review_triggered"])
        self.assertFalse(watch["automatic_download_authorized"])
        self.assertFalse(watch["p0_or_p1_authorized"])
        self.assertFalse(watch["method_or_architecture_authorized"])
        self.assertFalse(watch["gpu_or_outer_test_authorized"])
        self.assertFalse(watch["server_queried"])
        self.assertFalse(watch["junjinyong_accessed_for_this_watch"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["public_source_watch_v4"][
            "automatic_download_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Source watch v4"):
            validate_protocol(candidate)

    def test_source_watch_v5_expands_material_signals_without_authority(self) -> None:
        watch = self.protocol["problem_selection"]["public_source_watch_v5"]
        self.assertEqual(watch["config"], "configs/source_watch_v5.json")
        self.assertEqual(watch["extends_historical_config"], "configs/source_watch_v4.json")
        self.assertEqual(watch["watch_count"], 9)
        self.assertEqual(
            watch["aneug_huggingface_sha"],
            "9dd418083899deddd93a67f9a6fca7a14304fa36",
        )
        self.assertEqual(watch["aneurisk_zenodo_revision"], 4)
        self.assertEqual(watch["aneurisk_archive_bytes"], 1430889142)
        self.assertEqual(watch["largeia_access_right"], "restricted")
        self.assertEqual(watch["largeia_public_file_count"], 0)
        self.assertFalse(watch["topaneu_challenge_under_construction"])
        self.assertTrue(watch["topaneu_join_registration_available"])
        self.assertTrue(watch["same_as_all_frozen_snapshots"])
        self.assertFalse(watch["manual_review_triggered"])
        self.assertFalse(watch["automatic_download_authorized"])
        self.assertFalse(watch["automatic_terms_acceptance_authorized"])
        self.assertFalse(watch["historical_execution_repair_or_rerun_authorized"])
        self.assertFalse(watch["p0_or_p1_authorized"])
        self.assertFalse(watch["method_or_architecture_authorized"])
        self.assertFalse(watch["gpu_or_outer_test_authorized"])
        self.assertFalse(watch["server_queried"])
        self.assertFalse(watch["junjinyong_accessed_for_this_watch"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["public_source_watch_v5"][
            "automatic_terms_acceptance_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Source watch v5"):
            validate_protocol(candidate)

    def test_source_watch_v6_adds_gated_manifest_without_authority(self) -> None:
        watch = self.protocol["problem_selection"]["public_source_watch_v6"]
        self.assertEqual(watch["config"], "configs/source_watch_v6.json")
        self.assertEqual(watch["extends_historical_config"], "configs/source_watch_v5.json")
        self.assertEqual(watch["watch_count"], 10)
        self.assertEqual(watch["aneux_transient_gated"], "manual")
        self.assertEqual(watch["aneux_transient_sibling_count"], 1940)
        self.assertEqual(watch["aneux_transient_bifurcation_case_folders"], 180)
        self.assertEqual(watch["aneux_transient_sidewall_case_folders"], 143)
        self.assertEqual(watch["aneux_transient_unique_visible_case_ids"], 322)
        self.assertEqual(watch["aneux_transient_cross_topology_overlap_ids"], ["SNF365"])
        self.assertTrue(watch["same_as_all_frozen_snapshots"])
        self.assertFalse(watch["manual_review_triggered"])
        self.assertFalse(watch["automatic_download_authorized"])
        self.assertFalse(watch["automatic_terms_acceptance_authorized"])
        self.assertFalse(watch["historical_execution_repair_or_rerun_authorized"])
        self.assertFalse(watch["p0_or_p1_authorized"])
        self.assertFalse(watch["method_or_architecture_authorized"])
        self.assertFalse(watch["gpu_or_outer_test_authorized"])
        self.assertFalse(watch["server_queried"])
        self.assertFalse(watch["junjinyong_accessed_for_this_watch"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["public_source_watch_v6"][
            "automatic_terms_acceptance_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Source watch v6"):
            validate_protocol(candidate)

    def test_team_downstream_utility_batch_rejects_architecture_first_reentry(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["team_downstream_utility_reappraisal"]
        self.assertEqual(self.protocol["schema_version"], "10.3")
        self.assertEqual(audit["best_score"], 27.0)
        self.assertEqual(
            audit["all_candidate_scores"],
            [27.0, 25.5, 24.0, 24.0, 23.5, 21.5],
        )
        self.assertLess(
            max(audit["all_candidate_scores"]),
            audit["automatic_selection_threshold"],
        )
        self.assertFalse(audit["new_team_discussion_detected"])
        self.assertTrue(audit["team_question_retained_as_evaluation_template_only"])
        self.assertEqual(audit["cmha_patients"], 99)
        self.assertFalse(audit["cmha_official_case_map_verified"])
        self.assertFalse(audit["cmha_contains_matched_surrogate_predictions"])
        self.assertFalse(
            audit["cmha_negative_exploratory_signal_relabelled_as_confirmatory_failure"]
        )
        self.assertEqual(audit["pointflownet_idealized_mca_geometries"], 984)
        self.assertEqual(audit["pointflownet_repository_release_count"], 0)
        self.assertIsNone(audit["pointflownet_repository_license_spdx_id"])
        self.assertFalse(audit["pointflownet_tracked_train_val_test_manifests_present"])
        self.assertFalse(audit["pointflownet_cfd_payload_present"])
        self.assertFalse(
            audit["pointflownet_public_repository_is_complete_executable_matched_baseline"]
        )
        self.assertEqual(audit["dryad_fsi_effective_anatomies"], 1)
        self.assertFalse(audit["dryad_fsi_payload_accessed"])
        self.assertFalse(audit["dryad_grid_or_time_samples_counted_as_independent_units"])
        self.assertFalse(audit["p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["scientific_server_queried"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["team_downstream_utility_reappraisal"][
            "architecture_selected"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "team downstream-utility reappraisal"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["team_downstream_utility_reappraisal"][
            "cmha_negative_exploratory_signal_relabelled_as_confirmatory_failure"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "team downstream-utility reappraisal"):
            validate_protocol(candidate)

    def test_source_watch_v7_adds_pointflownet_baseline_watch_only(self) -> None:
        watch = self.protocol["problem_selection"]["public_source_watch_v7"]
        self.assertEqual(watch["config"], "configs/source_watch_v7.json")
        self.assertEqual(watch["extends_historical_config"], "configs/source_watch_v6.json")
        self.assertEqual(watch["watch_count"], 11)
        self.assertEqual(watch["pointflownet_release_count"], 0)
        self.assertIsNone(watch["pointflownet_license_spdx_id"])
        self.assertFalse(watch["pointflownet_split_manifests_present"])
        self.assertFalse(watch["pointflownet_cfd_payload_present"])
        self.assertTrue(watch["same_as_all_frozen_snapshots"])
        self.assertFalse(watch["manual_review_triggered"])
        self.assertFalse(watch["fresh_source_reaudit_triggered"])
        self.assertFalse(watch["direct_prior_baseline_feasibility_reaudit_triggered"])
        self.assertFalse(watch["automatic_download_authorized"])
        self.assertFalse(watch["method_or_architecture_authorized"])
        self.assertFalse(watch["gpu_or_outer_test_authorized"])
        self.assertFalse(watch["server_queried"])
        self.assertFalse(watch["junjinyong_accessed_for_this_watch"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["public_source_watch_v7"][
            "method_or_architecture_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Source watch v7"):
            validate_protocol(candidate)

    def test_source_watch_v8_adds_aaa_wss_baseline_watch_only(self) -> None:
        watch = self.protocol["problem_selection"]["public_source_watch_v8"]
        self.assertEqual(watch["config"], "configs/source_watch_v8.json")
        self.assertEqual(watch["extends_historical_config"], "configs/source_watch_v7.json")
        self.assertEqual(watch["watch_count"], 12)
        self.assertEqual(
            watch["aaa_wss_repository"], "PatRyg99/AAA-WSS-neural-surrogate"
        )
        self.assertEqual(watch["aaa_wss_release_count"], 0)
        self.assertIsNone(watch["aaa_wss_license_spdx_id"])
        self.assertEqual(watch["aaa_wss_readme_bytes"], 183)
        self.assertEqual(watch["aaa_wss_payload_or_code_entries"], [])
        self.assertTrue(watch["same_as_all_frozen_snapshots"])
        self.assertFalse(watch["manual_review_triggered"])
        self.assertFalse(watch["automatic_download_authorized"])
        self.assertFalse(watch["method_or_architecture_authorized"])
        self.assertFalse(watch["gpu_or_outer_test_authorized"])
        self.assertFalse(watch["server_queried"])
        self.assertFalse(watch["junjinyong_accessed_for_this_watch"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["public_source_watch_v8"][
            "method_or_architecture_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Source watch v8"):
            validate_protocol(candidate)

    def test_source_watch_v9_adds_mris_target_contract_watch_only(self) -> None:
        watch = self.protocol["problem_selection"]["public_source_watch_v9"]
        self.assertEqual(watch["config"], "configs/source_watch_v9.json")
        self.assertEqual(watch["extends_historical_config"], "configs/source_watch_v8.json")
        self.assertEqual(watch["watch_count"], 13)
        self.assertEqual(watch["mris_bench_dataset_id"], "lixiangcog/MRIS-Bench")
        self.assertEqual(watch["mris_bench_arrow_shard_count"], 8)
        self.assertTrue(watch["mris_bench_under_review_release_statement_present"])
        self.assertTrue(watch["same_as_all_frozen_snapshots"])
        self.assertFalse(watch["manual_review_triggered"])
        self.assertFalse(watch["automatic_download_authorized"])
        self.assertFalse(watch["method_or_architecture_authorized"])
        self.assertFalse(watch["gpu_or_outer_test_authorized"])
        self.assertFalse(watch["server_queried"])
        self.assertFalse(watch["junjinyong_accessed_for_this_watch"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["public_source_watch_v9"][
            "automatic_download_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Source watch v9"):
            validate_protocol(candidate)

    def test_trellis_surface_feature_update_is_direct_prior_only(self) -> None:
        assessment = self.protocol["problem_selection"][
            "surface_vector_conditional_assessment"
        ]
        prior = assessment["foundation_surface_feature_direct_prior"]
        self.assertEqual(prior["arxiv"], "2509.03095")
        self.assertEqual(prior["anxplore_cases_reported"], 101)
        self.assertTrue(prior["common_uniform_parent_vessel"])
        self.assertEqual(prior["feature_dimension"], 1024)
        self.assertEqual(prior["stated_code_url_http_status_on_2026_08_11"], 404)
        self.assertEqual(prior["source_watch_config"], "configs/source_watch_v4.json")
        self.assertTrue(prior["source_watch_current_snapshot_matches"])
        self.assertEqual(prior["source_watch_next_action"], "continue_watch_only")
        self.assertEqual(
            prior["source_watch_change_opens_only"],
            "direct_prior_baseline_feasibility_reaudit_only",
        )
        self.assertFalse(
            prior["surface_wss_critical_point_or_worldline_endpoint_reported"]
        )
        self.assertFalse(prior["medical_payload_or_checkpoint_accessed"])
        self.assertFalse(prior["server_queried"])
        self.assertFalse(prior["gpu_training_authorized"])
        self.assertFalse(prior["junjinyong_accessed_for_this_audit"])
        self.assertFalse(assessment["architecture_selected"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["surface_vector_conditional_assessment"][
            "foundation_surface_feature_direct_prior"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(ProtocolError, "TRELLIS"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["surface_vector_conditional_assessment"][
            "foundation_surface_feature_direct_prior"
        ]["surface_wss_critical_point_or_worldline_endpoint_reported"] = True
        with self.assertRaisesRegex(ProtocolError, "TRELLIS"):
            validate_protocol(candidate)

    def test_aneumo_bc_transport_p0_closes_execution_incomplete(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["aneumo_bc_transport_source_audit"]
        self.assertEqual(audit["score"], 33.5)
        self.assertAlmostEqual(sum(audit["axis_scores"]), 33.5)
        self.assertEqual(audit["conditional_source_lead_count"], 0)
        self.assertEqual(problem["conditional_source_lead_count"], 0)
        self.assertTrue(audit["p0_registered"])
        self.assertEqual(audit["p0_train_base_families"], [1])
        self.assertEqual(audit["p0_cases"], [1, 2])
        self.assertEqual(audit["p0_required_members"], 16)
        self.assertTrue(audit["p0_job_submitted"])
        self.assertEqual(audit["p0_job_id"], "115518.ECE-util1")
        self.assertEqual(
            audit["p0_execution_status"],
            "execution_incomplete_no_scientific_verdict",
        )
        self.assertFalse(audit["p0_aggregate_result_materialized"])
        self.assertFalse(audit["p0_raw_pbs_output_materialized"])
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["p1_registration_authorized"])
        self.assertFalse(audit["p0_persistent_field_cache"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneumo_bc_transport_source_audit"][
            "p0_train_base_families"
        ] = [13]
        with self.assertRaisesRegex(ProtocolError, "BC-transport P0"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneumo_bc_transport_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "BC-transport P0"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneumo_bc_transport_source_audit"][
            "p1_registration_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "BC-transport P0"):
            validate_protocol(candidate)

    def test_aneumo_lineage_candidate_closes_after_one_cpu_metadata_p0(self) -> None:
        audit = self.protocol["problem_selection"][
            "aneumo_lineage_split_source_audit"
        ]
        self.assertEqual(audit["best_score"], 35.0)
        self.assertEqual(audit["active_source_shortlist_count"], 0)
        self.assertEqual(audit["official_exact_case_overlap"], 0)
        self.assertEqual(audit["official_base_family_overlap"], 20)
        self.assertEqual(audit["official_validation_family_overlap_fraction"], 1.0)
        self.assertFalse(audit["license_sources_agree"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertTrue(audit["pbs_job_created"])
        self.assertEqual(audit["p0_job_id"], "115386.ECE-util1")
        self.assertEqual(audit["p0_exit_status"], -29)
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["p0_same_contract_repair_or_resubmission_allowed"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneumo_lineage_split_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "Aneumo generation-lineage audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["aneumo_lineage_split_source_audit"][
            "official_base_family_overlap"
        ] = 0
        with self.assertRaisesRegex(ProtocolError, "Aneumo generation-lineage audit"):
            validate_protocol(candidate)

    def test_failure_mechanism_biology_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "failure_mechanism_biology_source_audit"
        ]
        self.assertEqual(audit["best_score"], 30.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["anatomy_fp_open_training_ctas"], 1186)
        self.assertFalse(audit["anatomy_fp_casewise_cause_labels_public"])
        self.assertTrue(audit["topaneu_verified_account_required"])
        self.assertFalse(audit["topaneu_payload_accessed"])
        self.assertEqual(audit["spatial_atlas_aneurysm_donors"], 6)
        self.assertFalse(
            audit["paired_preoperative_imaging_tissue_coordinate_manifest_found"]
        )
        self.assertTrue(audit["ican_public_table_is_simulated"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["failure_mechanism_biology_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "failure-mechanism/biology audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["failure_mechanism_biology_source_audit"][
            "candidates"
        ][0]["payload_accessed"] = True
        with self.assertRaisesRegex(ProtocolError, "failure-mechanism/biology audit"):
            validate_protocol(candidate)

    def test_reconstruction_annotation_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "reconstruction_annotation_reliability_source_audit"
        ]
        self.assertEqual(audit["best_score"], 31.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["di_noto_total_subjects"], 284)
        self.assertEqual(audit["vp_unet_precise_label_test_subjects"], 38)
        self.assertFalse(
            audit[
                "same_subject_prospective_real_weak_and_independent_precise_annotation_manifest_public"
            ]
        )
        self.assertEqual(audit["reconstruction_variability_models"], 600)
        self.assertEqual(audit["ultrasparse_dsa_patients"], 202)
        self.assertEqual(audit["biplane_unidentifiable_neck_aneurysms"], 23)
        self.assertEqual(audit["phantomx_effective_anatomies"], 1)
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "reconstruction_annotation_reliability_source_audit"
        ]["gpu_training_authorized"] = True
        with self.assertRaisesRegex(
            ProtocolError, "reconstruction/annotation reliability audit"
        ):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"][
            "reconstruction_annotation_reliability_source_audit"
        ]["candidates"][0]["score"] = 32.0
        with self.assertRaisesRegex(
            ProtocolError, "reconstruction/annotation reliability audit"
        ):
            validate_protocol(candidate)

    def test_method_asset_viability_rejects_direct_priors_and_unreleased_assets(self) -> None:
        audit = self.protocol["problem_selection"][
            "method_asset_viability_source_audit"
        ]
        self.assertEqual(audit["best_score"], 30.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertTrue(audit["introai9_connection_verified"])
        self.assertEqual(audit["introai9_remote_user"], "introai9")
        self.assertEqual(audit["introai9_observed_host"], "ECE-util2")
        self.assertEqual(audit["introai9_pbs_jobs_observed"], 0)
        self.assertFalse(audit["aneug_flow_material_new_version_found"])
        self.assertFalse(audit["iavs_payload_or_code_present"])
        self.assertFalse(audit["rsna_per_reader_label_manifest_public"])
        self.assertFalse(audit["cq500_ia_cited_repository_publicly_resolvable"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not candidate["payload_accessed"] for candidate in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["method_asset_viability_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "method--asset viability audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["method_asset_viability_source_audit"][
            "iavs_main_head"
        ] = "changed"
        with self.assertRaisesRegex(ProtocolError, "method--asset viability audit"):
            validate_protocol(candidate)

    def test_registry_gap_audit_keeps_public_test_and_payload_sealed(self) -> None:
        audit = self.protocol["problem_selection"]["registry_gap_source_audit"]
        self.assertEqual(audit["best_score"], 26.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["official_registry_records_returned"], 49)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 5)
        self.assertEqual(audit["transiar_retained_patients"], 423)
        self.assertEqual(audit["transiar_retained_aneurysms"], 449)
        self.assertEqual(audit["gn_net_reported_patients"], 423)
        self.assertFalse(audit["exact_cross_record_case_lineage_manifest_public"])
        self.assertFalse(audit["public_test_payload_accessed"])
        self.assertEqual(audit["vwe_unruptured_aneurysms"], 41)
        self.assertFalse(audit["vwe_observed_future_instability_endpoint_present"])
        self.assertFalse(audit["transcriptomic_casewise_imaging_bridge_public"])
        self.assertFalse(audit["autopsy_casewise_table_or_imaging_public"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not candidate["payload_accessed"] for candidate in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["registry_gap_source_audit"][
            "public_test_payload_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "registry-gap source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["registry_gap_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "registry-gap source audit"):
            validate_protocol(candidate)

    def test_broad_registry_audit_rejects_restricted_and_pseudoreplicated_leads(self) -> None:
        audit = self.protocol["problem_selection"]["broad_registry_source_audit"]
        self.assertEqual(audit["best_score"], 30.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["largeia_internal_cta_studies"], 1338)
        self.assertEqual(audit["largeia_internal_institutions"], 6)
        self.assertEqual(audit["largeia_external_cta_studies"], 138)
        self.assertEqual(audit["largeia_external_institutions"], 2)
        self.assertEqual(audit["largeia_access_state"], "restricted_request_required")
        self.assertFalse(audit["largeia_user_access_request_or_terms_completed"])
        self.assertFalse(audit["largeia_payload_accessed"])
        self.assertEqual(audit["cfd_challenge_independent_aneurysm_anatomies"], 5)
        self.assertEqual(audit["cfd_challenge_submitted_datasets"], 28)
        self.assertEqual(audit["cfd_challenge_teams"], 26)
        self.assertEqual(audit["rupture_destined_patients"], 20)
        self.assertFalse(
            audit["rupture_destined_casewise_image_mesh_or_measurement_table_public"]
        )
        self.assertEqual(audit["synthetic_dsa_embargo_end"], "2026-10-31")
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["introai9_pbs_jobs_observed"], 0)
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["login_node_gpu_command_executed"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not candidate["payload_accessed"] for candidate in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["broad_registry_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "broad-registry source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["broad_registry_source_audit"][
            "largeia_user_access_request_or_terms_completed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "broad-registry source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["broad_registry_source_audit"][
            "cfd_challenge_independent_aneurysm_anatomies"
        ] = 28
        with self.assertRaisesRegex(ProtocolError, "broad-registry source audit"):
            validate_protocol(candidate)

    def test_rsna_aws_registry_correction_remains_controlled_and_precompute(self) -> None:
        audit = self.protocol["problem_selection"][
            "rsna_aws_registry_correction_audit"
        ]
        self.assertEqual(audit["score"], 31.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertAlmostEqual(sum(audit["axis_scores"]), audit["score"])
        self.assertTrue(audit["controlled_access"])
        self.assertFalse(audit["user_terms_accepted_verified"])
        self.assertFalse(audit["access_request_submitted"])
        self.assertFalse(audit["s3_listing_or_payload_accessed"])
        self.assertEqual(audit["reported_institutions"], 18)
        self.assertEqual(audit["official_wiki_status"], "coming_soon")
        self.assertFalse(audit["release_modality_contract_publicly_reconciled"])
        self.assertFalse(audit["public_per_reader_or_adjudication_manifest_verified"])
        self.assertEqual(
            audit["first_place_repository_commit"],
            "e1dcdf0058e1e0d0044d8053e92243b4b4794555",
        )
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["introai9_pbs_jobs_observed"], 0)
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["rsna_aws_registry_correction_audit"][
            "user_terms_accepted_verified"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "RSNA AWS registry correction"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["rsna_aws_registry_correction_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "RSNA AWS registry correction"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["rsna_aws_registry_correction_audit"][
            "provided_voxel_segmentation_semantics"
        ] = "aneurysm_extent"
        with self.assertRaisesRegex(ProtocolError, "RSNA AWS registry correction"):
            validate_protocol(candidate)

    def test_topbrain2_proposal_only_batch_cannot_open_compute(self) -> None:
        audit = self.protocol["problem_selection"]["topbrain2_source_audit"]
        self.assertEqual(audit["best_score"], 29.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["design_pdf_bytes"], 139840)
        self.assertEqual(audit["design_pdf_pages"], 35)
        self.assertTrue(audit["zenodo_license_identifier_present"])
        self.assertEqual(audit["zenodo_design_object_license_id"], "cc-by-4.0")
        self.assertEqual(
            audit["zenodo_license_scope"],
            "design_record_only_not_unreleased_medical_dataset",
        )
        self.assertEqual(audit["challenge_page_status"], "under_construction")
        self.assertTrue(audit["challenge_join_registration_available"])
        self.assertEqual(
            audit["grand_challenge_submission_status"],
            "join_registration_available_but_no_executable_task_submission_contract",
        )
        self.assertEqual(audit["source_watch_config"], "configs/source_watch_v4.json")
        self.assertTrue(audit["source_watch_current_snapshot_matches"])
        self.assertFalse(audit["versioned_topbrain2_dataset_release_verified"])
        self.assertFalse(
            audit["versioned_topbrain2_executable_evaluation_contract_verified"]
        )
        self.assertTrue(
            audit[
                "planned_task1_aneurysm_is_robustness_condition_not_lesion_target"
            ]
        )
        self.assertFalse(
            audit[
                "casewise_aneurysm_mask_parent_vessel_attachment_acquisition_reader_or_cross_challenge_identity_manifest_verified"
            ]
        )
        self.assertFalse(
            audit["patient_image_mask_clinical_split_or_test_payload_accessed"]
        )
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["pbs_job_created"])
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["introai9_pbs_jobs_observed"], 0)
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not candidate["payload_accessed"] for candidate in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topbrain2_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopBrain 2.0 source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topbrain2_source_audit"]["candidates"][0][
            "score"
        ] = 32.0
        with self.assertRaisesRegex(ProtocolError, "TopBrain 2.0 source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topbrain2_source_audit"][
            "versioned_topbrain2_dataset_release_verified"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopBrain 2.0 source audit"):
            validate_protocol(candidate)

    def test_four_d_cta_aaa_mechanics_batch_cannot_open_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "four_d_cta_aaa_mechanics_source_audit"
        ]
        self.assertEqual(audit["best_score"], 31.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["zenodo_record"], "10.5281/zenodo.19182978")
        self.assertEqual(audit["zenodo_license_id"], "cc-by-4.0")
        self.assertEqual(audit["archive_bytes"], 1857980948)
        self.assertEqual(
            audit["archive_md5"], "11b74684e382d1410a2d64f81967e613"
        )
        self.assertFalse(audit["archive_or_member_payload_accessed"])
        self.assertEqual(audit["reported_patients"], 20)
        self.assertEqual(audit["reported_centres"], 3)
        self.assertFalse(
            audit[
                "future_growth_rupture_treatment_wall_strength_or_histology_endpoint_available"
            ]
        )
        self.assertTrue(
            audit[
                "released_mechanics_are_derived_workflow_outputs_not_independent_clinical_ground_truth"
            ]
        )
        self.assertEqual(
            audit["synthetic_displacement_ground_truth_effective_patient_units"],
            1,
        )
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["pbs_job_created"])
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(
            audit["introai9_current_status_attempt"],
            "connection_reset_before_remote_command_no_scheduler_observation",
        )
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not candidate["payload_accessed"] for candidate in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["four_d_cta_aaa_mechanics_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "4D-CTA AAA mechanics source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["four_d_cta_aaa_mechanics_source_audit"][
            "candidates"
        ][0]["score"] = 32.0
        with self.assertRaisesRegex(ProtocolError, "4D-CTA AAA mechanics source audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["four_d_cta_aaa_mechanics_source_audit"][
            "reported_patients"
        ] = 200
        with self.assertRaisesRegex(ProtocolError, "4D-CTA AAA mechanics source audit"):
            validate_protocol(candidate)

    def test_topaneu_material_release_preserves_historical_33_record(self) -> None:
        audit = self.protocol["problem_selection"][
            "topaneu_release_evaluation_source_audit"
        ]
        self.assertEqual(audit["best_score"], 33.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["conditional_source_lead_count"], 1)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(
            audit["official_repository_commit"],
            "018c243445f99199f484018c4c80575c84c72293",
        )
        self.assertEqual(audit["official_release_scans"], 417)
        self.assertEqual(audit["official_unique_patients"], 409)
        self.assertEqual(audit["official_location_classes"], 52)
        self.assertEqual(audit["location_json_paths"], 417)
        self.assertEqual(audit["batch1_cases_revised_in_current_release"], 52)
        self.assertFalse(audit["user_terms_acceptance_verified"])
        self.assertFalse(audit["medical_payload_accessed"])
        self.assertFalse(audit["executable_p0_registered"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["architecture_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertFalse(audit["outer_test_authorized"])
        self.assertEqual(audit["conditional_source_lead_count"], 1)
        self.assertEqual(
            self.protocol["problem_selection"]["conditional_source_lead_count"], 0
        )
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topaneu_release_evaluation_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu material release"):
            validate_protocol(candidate)

    def test_openneuro_containment_p0_closes_execution_incomplete(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["openneuro_containment_morphometry_source_audit"]
        self.assertEqual(problem["conditional_source_lead_count"], 0)
        self.assertIsNone(problem["shortlisted_candidate"])
        self.assertEqual(audit["score"], 32.5)
        self.assertAlmostEqual(sum(audit["axis_scores"]), 32.5)
        self.assertEqual(audit["public_weak_subjects"], 246)
        self.assertEqual(audit["public_precise_subjects"], 38)
        self.assertEqual(audit["code_weak_entries"], 262)
        self.assertEqual(audit["code_only_weak_subjects"], ["sub-115", "sub-143", "sub-181", "sub-272"])
        self.assertTrue(audit["p0_job_submitted"])
        self.assertEqual(audit["p0_job_id"], "115622.ECE-util1")
        self.assertEqual(audit["p0_final_job_state"], "F")
        self.assertEqual(audit["p0_exit_status"], 1)
        self.assertEqual(audit["p0_registered_high_level_checks_evaluated"], 0)
        self.assertFalse(audit["p0_aggregate_result_materialized"])
        self.assertFalse(audit["p0_raw_pbs_output_materialized"])
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["p1_registration_authorized"])
        self.assertFalse(audit["patient_nifti_image_or_mask_payload_accessed"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["openneuro_containment_morphometry_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "OpenNeuro containment P0"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["openneuro_containment_morphometry_source_audit"][
            "session_date_is_registered_join_key"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "OpenNeuro containment P0"):
            validate_protocol(candidate)

    def test_topaneu_code_semantics_red_team_rejects_historical_lead_without_relabel(self) -> None:
        problem = self.protocol["problem_selection"]
        audit = problem["topaneu_code_semantics_red_team"]
        self.assertEqual(audit["best_score"], 31.5)
        self.assertLess(audit["best_score"], audit["automatic_selection_threshold"])
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(audit["conditional_source_lead_count"], 0)
        self.assertEqual(audit["historical_schema_6_3_score"], 33.0)
        self.assertFalse(audit["historical_score_relabelled"])
        self.assertEqual(audit["fresh_same_formulation_score"], 31.0)
        self.assertEqual(audit["official_location_leaf_count"], 52)
        self.assertEqual(audit["official_right_lateralized_leaves"], 24)
        self.assertEqual(audit["official_left_lateralized_leaves"], 24)
        self.assertEqual(audit["official_non_lateralized_leaves"], 4)
        self.assertTrue(audit["task1_preserves_repeated_class_ids_as_counts"])
        self.assertTrue(audit["task2_active_path_evaluates_per_class_binary_volume"])
        self.assertFalse(audit["task2_instance_level_code_active"])
        self.assertFalse(audit["official_test_interface_includes_vessel_mask"])
        for key in (
            "user_terms_acceptance_verified",
            "patient_image_or_mask_payload_accessed",
            "patient_location_json_content_accessed",
            "switchdrive_medical_member_accessed",
            "medical_payload_accessed",
            "executable_p0_registered",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
        ):
            self.assertFalse(audit[key])

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topaneu_code_semantics_red_team"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu code-semantics"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topaneu_code_semantics_red_team"][
            "historical_score_relabelled"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu code-semantics"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topaneu_code_semantics_red_team"][
            "candidates"
        ][0]["score"] = 32.0
        with self.assertRaisesRegex(ProtocolError, "TopAneu code-semantics"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topaneu_code_semantics_red_team"][
            "patient_image_or_mask_payload_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu code-semantics"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topaneu_release_evaluation_source_audit"][
            "medical_payload_accessed"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu material release"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["topaneu_release_evaluation_source_audit"][
            "user_terms_acceptance_verified"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "TopAneu material release"):
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

    def test_fsi_wall_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"]["fsi_wall_source_audit"]
        self.assertEqual(audit["best_score"], 31.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["anxplore_geometries"], 101)
        self.assertEqual(audit["anxplore_public_full_dataset_fluid_meshes"], 101)
        self.assertEqual(
            audit["anxplore_paired_rigid_fsi_simulations_reported_by_paper"],
            101,
        )
        self.assertFalse(
            audit["anxplore_paired_rigid_fsi_solution_fields_publicly_released"]
        )
        self.assertEqual(audit["anxplore_flow_diverter_paired_effective_cases"], 1)
        self.assertEqual(audit["inverse_mechanics_effective_units"], 1)
        self.assertEqual(audit["microct_wall_thickness_human_aneurysms"], 5)
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["observed_introai9_pbs_job_count"], 0)
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["fsi_wall_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "FSI-wall audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["fsi_wall_source_audit"][
            "anxplore_paired_rigid_fsi_solution_fields_publicly_released"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "FSI-wall audit"):
            validate_protocol(candidate)

    def test_longitudinal_perfusion_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "longitudinal_perfusion_source_audit"
        ]
        self.assertEqual(audit["best_score"], 31.0)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["ctp_patients"], 62)
        self.assertEqual(audit["ctp_original_exams"], 291)
        self.assertEqual(audit["ctp_parametric_maps"], 873)
        self.assertEqual(audit["ctp_dci_events"], 9)
        self.assertEqual(audit["ctp_vasospasm_patients"], 42)
        self.assertTrue(audit["ctp_observation_process_clinically_informative"])
        self.assertTrue(audit["ctp_guided_rescue_treatment_reported"])
        self.assertFalse(audit["unobserved_untreated_trajectory_identified"])
        self.assertEqual(audit["figshare_3dra_cta_effective_aneurysms"], 10)
        self.assertFalse(
            audit["figshare_3dra_cta_source_images_meshes_or_fields_released"]
        )
        self.assertEqual(audit["vwe_unruptured_aneurysms"], 41)
        self.assertFalse(
            audit["vwe_mri_volumes_surfaces_or_spatial_maps_released"]
        )
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertEqual(audit["observed_introai9_pbs_job_count"], 0)
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["longitudinal_perfusion_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "longitudinal-perfusion audit"):
            validate_protocol(candidate)

    def test_longitudinal_mra_growth_batch_rejects_all_before_compute(self) -> None:
        audit = self.protocol["problem_selection"][
            "longitudinal_mra_growth_source_audit"
        ]
        self.assertEqual(audit["best_score"], 31.5)
        self.assertEqual(audit["automatic_selection_threshold"], 32.0)
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(len(audit["candidates"]), 6)
        self.assertEqual(audit["openneuro_dataset_id"], "ds005096")
        self.assertEqual(audit["patients"], 63)
        self.assertEqual(audit["aneurysms"], 85)
        self.assertEqual(audit["longitudinal_patients"], 24)
        self.assertEqual(audit["raw_angio_paths"], 126)
        self.assertEqual(audit["same_session_multi_acquisition_patients"], 4)
        self.assertEqual(
            audit["bayesian_direct_prior_public_growth_positives"], 6
        )
        self.assertFalse(
            audit[
                "any_openneuro_annotation_spreadsheet_participant_table_acquisition_sidecar_nifti_segmentation_slicer_scene_or_stl_payload_accessed"
            ]
        )
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertFalse(
            audit["introai9_connection_or_job_query_performed_for_this_audit"]
        )
        self.assertFalse(audit["pbs_job_created"])
        self.assertFalse(audit["junjinyong_accessed_for_this_audit"])
        self.assertTrue(
            all(not item["payload_accessed"] for item in audit["candidates"])
        )

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["longitudinal_mra_growth_source_audit"][
            "gpu_training_authorized"
        ] = True
        with self.assertRaisesRegex(ProtocolError, "longitudinal-MRA-growth audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["longitudinal_mra_growth_source_audit"][
            "same_session_multi_acquisition_patients"
        ] = 40
        with self.assertRaisesRegex(ProtocolError, "longitudinal-MRA-growth audit"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["problem_selection"]["longitudinal_perfusion_source_audit"][
            "ctp_dci_events"
        ] = 90
        with self.assertRaisesRegex(ProtocolError, "longitudinal-perfusion audit"):
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

    def test_cycle_transport_v2a_is_one_round_cpu_only_reentry(self) -> None:
        audit = self.protocol["problem_selection"]["aneug_cycle_transport_reentry_v2a"]
        self.assertEqual(audit["active_shortlist_count"], 0)
        self.assertEqual(audit["maximum_transport_repair_rounds"], 1)
        self.assertEqual(audit["maximum_total_payload_bytes"], 4194304)
        self.assertFalse(audit["historical_v1_failure_relabelled"])
        self.assertFalse(audit["scientific_p0_evaluated"])
        self.assertFalse(audit["transport_gate_evaluated"])
        self.assertIsNone(audit["transport_gate_passed"])
        self.assertTrue(audit["pbs_job_submitted"])
        self.assertEqual(audit["p0_scheduler_job_id"], "115467.ECE-util1")
        self.assertEqual(audit["p0_scheduler_exit_status"], 1)
        self.assertFalse(audit["second_transport_repair_round_allowed"])
        self.assertFalse(audit["p0_v2b_authorized"])
        self.assertFalse(audit["method_selected"])
        self.assertFalse(audit["gpu_training_authorized"])
        self.assertEqual(audit["execution_server"], "introai9")
        self.assertFalse(audit["junjinyong_accessed_for_this_reentry"])
        execution_path = ROOT / audit["p0_execution_record"]
        self.assertEqual(
            hashlib.sha256(execution_path.read_bytes()).hexdigest(),
            audit["p0_execution_record_sha256"],
        )

        for field, value in (
            ("maximum_transport_repair_rounds", 2),
            ("maximum_total_payload_bytes", 8388608),
            ("gpu_training_authorized", True),
            ("historical_v1_failure_relabelled", True),
        ):
            candidate = copy.deepcopy(self.protocol)
            candidate["problem_selection"]["aneug_cycle_transport_reentry_v2a"][field] = value
            with self.assertRaisesRegex(ProtocolError, "P0-v2a re-entry"):
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
        with self.assertRaisesRegex(ProtocolError, "active candidate"):
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

    def test_isbi_author_compliance_contract_is_frozen(self) -> None:
        venue = self.protocol["venue"]
        self.assertEqual(venue["maximum_first_author_submissions"], 2)
        self.assertTrue(venue["substantially_similar_prior_publication_prohibited"])
        self.assertTrue(venue["substantially_similar_concurrent_submission_prohibited"])
        self.assertTrue(venue["preprint_posting_allowed"])
        self.assertTrue(venue["ethics_statement_required_irrespective_of_approval_need"])
        self.assertTrue(venue["conflict_of_interest_disclosure_required"])
        self.assertEqual(venue["submission_link_status"], "coming_soon")

        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["ethics_statement_required_irrespective_of_approval_need"] = False
        with self.assertRaisesRegex(ProtocolError, "authorship, originality"):
            validate_protocol(candidate)

        candidate = copy.deepcopy(self.protocol)
        candidate["venue"]["substantially_similar_concurrent_submission_prohibited"] = False
        with self.assertRaisesRegex(ProtocolError, "authorship, originality"):
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
