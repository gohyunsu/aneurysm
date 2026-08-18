import copy
import json
import unittest
from pathlib import Path

from aurora.aneug_release_730_protocol import (
    Release730ProtocolError,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/aneug_release_730_protocol_v1.json"


class AneuGRelease730ProtocolTests(unittest.TestCase):
    def test_selects_release_intersection_not_all_v5_cases(self):
        config = load_config(CONFIG)
        self.assertEqual(config["source"]["processed_v5"]["remote_case_like_count"], 809)
        self.assertEqual(config["cohort"]["expected_case_count"], 730)
        self.assertEqual(config["cohort"]["exclude_processed_only_extra_cases"], 79)
        self.assertFalse(
            config["source"]["release_case_manifest"]["compute_node_network_required"]
        )

    def test_split_is_case_grouped_outcome_blind_and_test_locked(self):
        split = load_config(CONFIG)["split_design"]
        self.assertEqual(split["singleton_target_counts"], {"train": 584, "validation": 73, "test": 73})
        self.assertTrue(split["all_phases_follow_case"])
        self.assertFalse(split["field_or_model_result_used_to_choose_split"])
        self.assertTrue(split["test_locked_until_candidate_and_analysis_freeze"])

    def test_physical_decode_is_bound_to_exact_completed_provenance_audit(self):
        provenance = load_config(CONFIG)["normalization_provenance"]
        self.assertEqual(
            provenance["v4_v5_overlap_identity_audit_status"],
            "complete_strong_overlap_linkage",
        )
        self.assertEqual(provenance["audit_job_id"], "117006.ECE-util1")
        self.assertEqual(
            provenance["audit_result_sha256"],
            "a083a4a71abfca55cac4e638daad00c7acd2bd7a66a3a42b2d5302374fb11fdb",
        )
        self.assertTrue(
            provenance["physical_wss_metrics_authorized_after_supported_linkage"]
        )
        self.assertFalse(provenance["v5_only_creator_manifest_available"])

    def test_no_raw_release_or_premature_gpu_is_authorized(self):
        config = load_config(CONFIG)
        self.assertFalse(config["storage"]["raw_per_case_cfd_downloaded"])
        self.assertFalse(config["storage"]["two_tb_release_downloaded"])
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertFalse(config["authorization"]["download_v5"])
        self.assertTrue(config["authorization"]["use_verified_v5"])
        self.assertFalse(config["authorization"]["gpu_training_before_schema_and_split"])

    def test_cohort_inflation_is_rejected(self):
        payload = json.loads(CONFIG.read_text())
        candidate = copy.deepcopy(payload)
        candidate["cohort"]["expected_case_count"] = 809
        with self.assertRaisesRegex(Release730ProtocolError, "cohort_count"):
            validate_config(candidate)


if __name__ == "__main__":
    unittest.main()
