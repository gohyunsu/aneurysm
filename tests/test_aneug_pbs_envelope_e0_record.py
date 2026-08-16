from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "aneug_pbs_envelope_e0_v1_20260817.json"
EXPECTED_SHA256 = "a1ce52b1ba25955a855a1868e854970d9ca6df71c5ed328f4b789ffebf9a74dc"


class AneuGPBSEnvelopeE0RecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_exact_closure_bytes_are_pinned(self) -> None:
        self.assertEqual(hashlib.sha256(RESULT.read_bytes()).hexdigest(), EXPECTED_SHA256)

    def test_runner_pass_and_scheduler_staging_failure_are_separate(self) -> None:
        self.assertEqual(self.payload["status"], "closed_infrastructure_classified")
        self.assertEqual(self.payload["pbs"]["final_state"], "F")
        self.assertEqual(self.payload["pbs"]["exit_status"], 0)
        self.assertTrue(self.payload["runner_envelope"]["runner_envelope_pass"])
        self.assertEqual(self.payload["runner_envelope"]["wrapper_exit_status"], 0)
        self.assertTrue(
            self.payload["scheduler_output_staging"]["post_job_file_processing_error"]
        )
        self.assertFalse(self.payload["scheduler_output_staging"]["staging_pass"])
        self.assertFalse(self.payload["scheduler_output_staging"]["full_envelope_pass"])
        self.assertFalse(
            self.payload["scheduler_output_staging"]["pbs_stdout_materialized"]
        )
        self.assertFalse(
            self.payload["scheduler_output_staging"]["pbs_stderr_materialized"]
        )

    def test_no_science_was_opened(self) -> None:
        boundary = self.payload["scientific_boundary"]
        for key, value in boundary.items():
            if key == "scientific_verdict":
                self.assertIsNone(value)
            else:
                self.assertFalse(value, key)
        closure = self.payload["closure"]
        self.assertEqual((closure["attempts_used"], closure["attempt_limit"]), (1, 1))
        self.assertTrue(closure["e0_closed"])
        self.assertTrue(closure["d6_remains_closed"])
        self.assertFalse(closure["same_contract_resume_repair_or_rerun_allowed"])
        self.assertFalse(closure["field_read_authorized"])
        self.assertFalse(closure["model_or_gpu_authorized"])
        self.assertFalse(self.payload["excluded_server_accessed"])

    def test_interpretation_does_not_overclaim_exact_d6_cause(self) -> None:
        interpretation = self.payload["interpretation"]
        self.assertTrue(
            interpretation[
                "persistent_wrapper_output_is_available_despite_scheduler_staging_failure"
            ]
        )
        self.assertTrue(
            interpretation[
                "d6_absent_wrapper_record_is_not_explained_by_post_job_staging_alone"
            ]
        )
        self.assertFalse(interpretation["d6_exact_pre_runner_failure_line_identified"])
        self.assertFalse(interpretation["scientific_asset_or_dataset_failure_evidence"])


if __name__ == "__main__":
    unittest.main()
