import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_public_transient_release_reappraisal_v1.json"


class AneumoPublicTransientReleaseReappraisalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_exact_public_snapshots_and_manifest_counts_are_frozen(self) -> None:
        src = self.audit["official_sources"]
        manifest = self.audit["release_manifest"]
        self.assertEqual(
            src["github_commit"],
            "701d53dde3489d84dbe9bc8324254629162eb45a",
        )
        self.assertEqual(
            src["huggingface_revision"],
            "f801adee816c18d3e18b23e6fcb147fe4c264209",
        )
        self.assertEqual(src["huggingface_used_storage_bytes"], 3284946024600)
        self.assertEqual(manifest["total_siblings"], 370)
        self.assertEqual(manifest["numeric_steady_zip_count"], 267)
        self.assertEqual(manifest["transient_batch_zip_count"], 100)
        self.assertEqual(manifest["other_file_count"], 3)
        self.assertEqual(
            manifest["numeric_steady_zip_count"]
            + manifest["transient_batch_zip_count"]
            + manifest["other_file_count"],
            manifest["total_siblings"],
        )

    def test_bounded_probe_does_not_become_field_evidence(self) -> None:
        probe = self.audit["bounded_archive_metadata_probe"]
        self.assertFalse(probe["full_archive_downloaded"])
        self.assertFalse(probe["field_values_interpreted"])
        self.assertEqual(probe["outer_case_archives"], 10)
        self.assertEqual(probe["inner_time_directories"], 101)
        self.assertEqual(probe["cycle_time_directory_count"], 100)
        self.assertEqual(probe["inner_member_count"], 404)
        self.assertEqual(probe["files_per_time_directory"], 4)

    def test_case_count_is_not_mislabeled_as_independent_unit(self) -> None:
        units = self.audit["lineage_units"]
        self.assertEqual(units["released_transient_cases"], 1000)
        self.assertEqual(units["released_transient_base_families"], 40)
        self.assertFalse(units["case_phase_vertex_or_critical_point_as_independent_unit_allowed"])

    def test_official_code_is_not_relabelled_as_family_disjoint_vector_baseline(self) -> None:
        code = self.audit["official_code_audit"]
        self.assertTrue(code["cross_dataset_converts_wss_vector_to_magnitude"])
        self.assertFalse(code["geometry_split_is_base_family_disjoint"])
        self.assertEqual(code["geometry_split_train_test_base_family_overlap"], 10)
        self.assertFalse(code["critical_point_or_worldline_metric_present"])
        self.assertEqual(code["python_parse_error_count"], 1)
        self.assertEqual(len(code["declared_but_missing_model_modules"]), 2)

    def test_license_conflict_fails_closed(self) -> None:
        license_audit = self.audit["license_audit"]
        self.assertEqual(license_audit["huggingface_declared_license"], "cc-by-nc-nd-4.0")
        self.assertEqual(license_audit["github_datasheet_declared_license"], "cc-by-4.0")
        self.assertFalse(license_audit["exact_release_license_consistent"])
        self.assertTrue(
            license_audit[
                "license_resolution_required_before_scientific_activation_or_redistribution"
            ]
        )
        self.assertFalse(license_audit["legal_conclusion_made"])

    def test_candidate_screen_retains_one_lead_without_transient_activation(self) -> None:
        screen = self.audit["candidate_screen"]
        rows = screen["candidates"]
        for row in rows:
            self.assertEqual(sum(row["axis_scores"]), row["total"])
        self.assertEqual(rows[0]["total"], 32.5)
        self.assertEqual(rows[1]["total"], 28.0)
        self.assertEqual(screen["conditional_source_lead_count"], 1)
        self.assertEqual(screen["transient_candidate_admitted_count"], 0)

    def test_source_delta_is_neither_p0_nor_server_recovery(self) -> None:
        gate = self.audit["future_transient_reentry_gate"]
        auth = self.audit["authorization"]
        self.assertTrue(gate["source_change_satisfies_historical_material_e0_change_only"])
        self.assertTrue(gate["source_change_is_not_task_p0_pass"])
        self.assertTrue(gate["source_change_is_not_introai9_operational_change"])
        self.assertFalse(gate["p0_registered"])
        self.assertTrue(all(value is False for value in auth.values()))


if __name__ == "__main__":
    unittest.main()
