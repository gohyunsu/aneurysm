from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "aneug_processed_v4_d6_execution_v2_20260817.json"
EXPECTED_SHA256 = "f3c73f4c2d553af276f392ef6baa2d894cb3a791a3bd73323a4a1a25af396caa"


class AneuGProcessedV4D6ExecutionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_exact_record_bytes_are_pinned(self) -> None:
        self.assertEqual(hashlib.sha256(RESULT.read_bytes()).hexdigest(), EXPECTED_SHA256)

    def test_attempt_is_closed_execution_incomplete_without_scientific_verdict(self) -> None:
        self.assertEqual(self.payload["status"], "closed_execution_incomplete")
        self.assertEqual(self.payload["pbs_final_state"], "F")
        self.assertEqual(self.payload["pbs_exit_status"], 1)
        self.assertEqual(self.payload["closure"]["attempts_used"], 1)
        self.assertEqual(self.payload["closure"]["attempt_limit"], 1)
        self.assertTrue(self.payload["closure"]["d6_v2_closed"])
        self.assertFalse(
            self.payload["closure"]["same_contract_resume_repair_or_rerun_allowed"]
        )
        self.assertFalse(self.payload["field_audit"]["scientific_gate_evaluated"])
        self.assertIsNone(self.payload["field_audit"]["scientific_verdict"])
        self.assertIsNone(self.payload["field_audit"]["gate_pass"])

    def test_no_runner_field_or_downstream_authority_materialized(self) -> None:
        wrapper = self.payload["wrapper_evidence"]
        self.assertFalse(wrapper["private_record_directory_materialized"])
        self.assertFalse(wrapper["runner_started"])
        self.assertEqual(
            [
                self.payload["field_audit"][key]
                for key in (
                    "train_cases_evaluated",
                    "validation_cases_evaluated",
                    "outer_test_cases_evaluated",
                    "auxiliary_cases_evaluated",
                )
            ],
            [0, 0, 0, 0],
        )
        for key in (
            "baseline_development_authorized",
            "model_or_architecture_authorized",
            "gpu_training_authorized",
            "validation_or_outer_test_authorized",
            "paper_result_or_claim_authorized",
        ):
            self.assertFalse(self.payload["closure"][key])
        self.assertFalse(self.payload["excluded_server_accessed"])

    def test_resources_are_cpu_only_and_trace_is_preserved(self) -> None:
        self.assertEqual(
            (
                self.payload["resources"]["ncpus"],
                self.payload["resources"]["memory_gb"],
                self.payload["resources"]["ngpus"],
            ),
            (4, 64, 0),
        )
        self.assertTrue(self.payload["scheduler_trace"]["post_job_file_processing_error"])
        self.assertFalse(self.payload["scheduler_trace"]["pbs_stdout_materialized"])
        self.assertFalse(self.payload["scheduler_trace"]["pbs_stderr_materialized"])


if __name__ == "__main__":
    unittest.main()
