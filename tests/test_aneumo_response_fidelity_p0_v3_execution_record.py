from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "results" / "aneumo_response_fidelity_p0_v3_execution_20260813.json"


class AneumoResponseFidelityP0V3ExecutionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_exact_one_shot_was_cpu_only_and_is_closed(self) -> None:
        execution = self.record["execution"]
        self.assertEqual(execution["server"], "introai9")
        self.assertEqual(execution["job_id"], "116146.ECE-util1")
        self.assertEqual(execution["submission_count_for_exact_contract"], 1)
        self.assertEqual(execution["requested_ngpus"], 0)
        self.assertFalse(execution["login_node_gpu_command_executed"])
        self.assertFalse(execution["junjinyong_accessed"])
        self.assertFalse(self.record["authorization"]["same_contract_resubmission"])

    def test_execution_incomplete_is_not_a_scientific_failure_or_pass(self) -> None:
        self.assertEqual(
            self.record["status"],
            "execution_incomplete_no_scientific_verdict_exact_contract_closed",
        )
        self.assertFalse(self.record["scientific_gate_evaluated"])
        self.assertEqual(self.record["registered_scientific_check_count"], 12)
        self.assertEqual(self.record["evaluated_scientific_check_count"], 0)
        self.assertEqual(self.record["passed_scientific_check_count"], 0)
        self.assertIsNone(self.record["train_field_array_read_extent"])
        self.assertFalse(self.record["authorization"]["fresh_p1_registration"])
        self.assertFalse(self.record["authorization"]["gpu_training"])

    def test_only_minimal_status_materialized(self) -> None:
        artifacts = self.record["artifacts"]
        self.assertTrue(artifacts["private_status_materialized"])
        self.assertEqual(artifacts["private_status_bytes"], 313)
        self.assertEqual(
            artifacts["private_status_sha256"],
            "4f517743c69cbe3a8be0f717118db989644e389675f9ff6136ff063f480db4c6",
        )
        self.assertFalse(artifacts["aggregate_result_materialized"])
        self.assertFalse(artifacts["raw_pbs_output_materialized"])

    def test_record_bytes_are_stable_for_provenance_consumers(self) -> None:
        digest = hashlib.sha256(RECORD.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "bbed8806311d6deaef9d5d6ee797ec119e44ea9c77667b72ba6ed545ac1d82fd",
        )


if __name__ == "__main__":
    unittest.main()
