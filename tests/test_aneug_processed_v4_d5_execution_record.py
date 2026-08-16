from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "aneug_processed_v4_d5_ghd_component_result_20260816.json"
EXECUTION = ROOT / "results" / "aneug_processed_v4_d5_execution_20260816.json"


class AneuGProcessedV4D5ExecutionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.execution = json.loads(EXECUTION.read_text(encoding="utf-8"))

    def test_exact_one_shot_cpu_execution_is_closed(self) -> None:
        run = self.execution["execution"]
        self.assertEqual(run["job_id"], "116483.ECE-util1")
        self.assertEqual((run["final_state"], run["exit_status"]), ("F", 0))
        self.assertEqual((run["ncpus"], run["memory_requested_gb"], run["ngpus"]), (4, 64, 0))
        self.assertEqual((run["attempts_used"], run["attempt_limit"]), (1, 1))
        self.assertFalse(run["rerun_allowed"])

    def test_public_result_bytes_and_hash_are_exact(self) -> None:
        output = self.execution["output"]
        self.assertEqual(RESULT.stat().st_size, output["public_result_bytes"])
        self.assertEqual(hashlib.sha256(RESULT.read_bytes()).hexdigest(), output["public_result_sha256"])
        self.assertFalse(output["private_case_ids_or_component_members_published"])
        self.assertFalse(output["raw_log_public"])

    def test_gate_pass_freezes_component_disjoint_split(self) -> None:
        self.assertTrue(self.result["gate_pass"])
        self.assertTrue(self.result["private_split_frozen"])
        self.assertEqual(self.result["primary_component_count"], 508)
        self.assertEqual(
            self.result["train_component_count"]
            + self.result["validation_component_count"]
            + self.result["outer_test_component_count"],
            508,
        )
        self.assertEqual(self.result["mixed_primary_auxiliary_component_count"], 0)

    def test_gate_is_field_blind_and_opens_no_model_or_claim(self) -> None:
        decision = self.execution["decision"]
        self.assertFalse(self.result["registered_field_values_read"])
        self.assertFalse(self.result["mesh_connectivity_values_read"])
        self.assertFalse(self.result["scientific_field_metric_computed"])
        self.assertIsNone(self.result["scientific_verdict"])
        for key in (
            "field_audit_or_bounded_development_executed",
            "method_or_architecture_authorized",
            "gpu_training_authorized",
            "validation_or_test_authorized",
            "outer_test_authorized",
            "paper_result_or_claim_authorized",
        ):
            self.assertFalse(decision[key])


if __name__ == "__main__":
    unittest.main()
