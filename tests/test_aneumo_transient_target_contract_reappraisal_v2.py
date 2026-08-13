import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_transient_target_contract_reappraisal_v2.json"


class AneumoTransientTargetContractReappraisalV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_whole_release_audit_is_bounded_and_directory_only(self) -> None:
        audit = self.audit["whole_release_directory_audit"]
        self.assertEqual(audit["cases"], 1000)
        self.assertEqual(audit["range_requests"], 2100)
        self.assertLessEqual(audit["bytes_read"], audit["byte_ceiling"])
        self.assertFalse(audit["full_inner_file_payload_downloaded"])
        self.assertFalse(audit["scientific_field_values_interpreted_release_wide"])

    def test_complete_partial_and_preprocessor_counts_reconcile(self) -> None:
        audit = self.audit["whole_release_directory_audit"]
        self.assertEqual(
            audit["complete_directory_structural_cases"]
            + audit["incomplete_cycle_cases"],
            audit["cases"],
        )
        self.assertEqual(
            audit["official_preprocessor_compatible_cases"]
            + audit["noncanonical_wall_naming_cases"],
            audit["complete_directory_structural_cases"],
        )
        self.assertEqual(len(audit["incomplete_cycle_case_ids"]), 34)
        self.assertEqual(len(audit["noncanonical_wall_case_ids"]), 5)
        self.assertEqual(sum(audit["time_contract_counts"].values()), 1000)

    def test_all_families_have_at_least_one_usable_case(self) -> None:
        audit = self.audit["whole_release_directory_audit"]
        self.assertEqual(audit["base_families"], 40)
        self.assertEqual(
            audit["families_with_at_least_one_complete_directory_structural_case"],
            40,
        )
        self.assertEqual(
            audit["families_with_at_least_one_official_preprocessor_compatible_case"],
            40,
        )

    def test_selective_payload_probe_establishes_vector_and_mesh_only_locally(self) -> None:
        probe = self.audit["selective_wall_vector_probe"]
        case = probe["case_1"]
        self.assertFalse(probe["release_wide_generalization_allowed"])
        self.assertEqual(case["point_arrays"]["wallShearStress"], 3)
        self.assertEqual(case["cell_arrays"]["wallShearStress"], 3)
        self.assertTrue(case["phase_mesh_points_byte_identical"])
        self.assertTrue(case["phase_mesh_connectivity_byte_identical"])
        self.assertTrue(case["phase_mesh_offsets_byte_identical"])
        self.assertFalse(case["phase_wss_byte_identical"])

    def test_tangency_is_not_overclaimed(self) -> None:
        interpretation = self.audit["selective_wall_vector_probe"]["interpretation"]
        case = self.audit["selective_wall_vector_probe"]["case_1"]
        self.assertTrue(interpretation["wss_is_mostly_tangent_on_selected_phases"])
        self.assertTrue(
            interpretation["local_high_normal_tail_requires_mesh_quality_and_stability_audit"]
        )
        self.assertFalse(interpretation["wss_units_explicit_in_vtp_or_datasheet"])
        self.assertGreater(
            case["newell_point_normal_absolute_fraction"]["phase_4p01"]["p99"],
            0.3,
        )

    def test_official_preprocessor_is_not_relabelled_as_target_builder(self) -> None:
        pre = self.audit["official_preprocessor_audit"]
        self.assertEqual(pre["documented_cycle_steps"], 100)
        self.assertEqual(pre["discovered_steps_for_complete_cases"], 101)
        self.assertTrue(pre["includes_initial_0p00_after_cycle_eligibility_check"])
        self.assertTrue(pre["noncanonical_wall_can_become_empty_or_zero_wss_without_hard_failure"])
        self.assertTrue(
            pre["provided_pipeline_is_not_a_fail_closed_100_phase_vector_target_builder"]
        )

    def test_rescore_is_inactive_and_opens_no_authority(self) -> None:
        screen = self.audit["candidate_screen"]
        transient = screen["transient_structure_faithful_vector_wss"]
        steady = screen["steady_response_fidelity"]
        self.assertEqual(sum(transient["axis_scores"]), transient["total"])
        self.assertEqual(transient["total"], 30.0)
        self.assertLess(transient["total"], screen["admission_total"])
        self.assertFalse(screen["transient_candidate_admitted"])
        self.assertEqual(steady["total"], 32.5)
        self.assertFalse(self.audit["next_gate"]["registered"])
        self.assertTrue(all(value is False for value in self.audit["authorization"].values()))


if __name__ == "__main__":
    unittest.main()
