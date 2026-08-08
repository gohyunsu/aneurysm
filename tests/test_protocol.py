import copy
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

    def test_prospective_endpoint_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["application_endpoint"] = "five_year_rupture_risk"
        with self.assertRaisesRegex(ProtocolError, "cross-sectional"):
            validate_protocol(candidate)

    def test_isbi_target_cannot_be_marked_ready_without_3d_evidence(self) -> None:
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

    def test_m0_failure_cannot_enter_a_local_repair_loop(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["missing_operator_pullback_m0"][
            "failure_abandons_mechanism_without_local_weight_or_kernel_repair"
        ] = False
        with self.assertRaisesRegex(ProtocolError, "terminal after failure"):
            validate_protocol(candidate)

    def test_m0_cannot_open_test_or_reentry(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        n1 = next(
            item for item in candidate["nonlinear_protocols"] if item["id"] == "N1"
        )
        n1["missing_operator_pullback_m0"]["fresh_reentry_registered"] = True
        with self.assertRaisesRegex(ProtocolError, "non-authorizing"):
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
