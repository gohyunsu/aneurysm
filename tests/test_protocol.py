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

    def test_aneumo_learning_remains_blocked_by_exact_sanity(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        output = candidate["model"]["irregular_3d_output_contract"]
        output["activation_condition"] = "run_immediately"
        with self.assertRaisesRegex(ProtocolError, "exact sanity"):
            validate_protocol(candidate)

    def test_patient_bootstrap_is_required(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["evaluation"]["clinical_bootstrap_unit"] = "aneurysm"
        with self.assertRaisesRegex(ProtocolError, "patient"):
            validate_protocol(candidate)

    def test_paired_response_cannot_be_disabled(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["loss"]["paired_response"] = 0
        with self.assertRaisesRegex(ProtocolError, "paired-response"):
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


if __name__ == "__main__":
    unittest.main()
