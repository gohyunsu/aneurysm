from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "results" / "aneug_reference_floor_g0_execution_20260814.json"


class AneuGReferenceFloorG0ExecutionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_exact_one_shot_was_cpu_only_and_is_closed(self) -> None:
        execution = self.record["execution"]
        self.assertEqual(execution["server"], "introai9")
        self.assertEqual(execution["job_id"], "116204.ECE-util1")
        self.assertEqual(execution["submission_count_for_exact_contract"], 1)
        self.assertEqual(execution["requested_ngpus"], 0)
        self.assertFalse(execution["login_node_gpu_command_executed"])
        self.assertFalse(execution["junjinyong_accessed"])
        self.assertFalse(self.record["authorization"]["same_contract_resubmission"])

    def test_incomplete_source_request_is_not_a_dataset_or_science_verdict(self) -> None:
        self.assertEqual(
            self.record["status"],
            "execution_incomplete_no_source_feasibility_or_scientific_verdict_exact_contract_closed",
        )
        self.assertEqual(self.record["reported_reason"], "public_source_request_failed")
        self.assertFalse(self.record["source_feasibility_gate_evaluated"])
        self.assertFalse(self.record["scientific_gate_evaluated"])
        self.assertEqual(self.record["registered_scientific_check_count"], 0)
        self.assertEqual(self.record["evaluated_scientific_check_count"], 0)
        self.assertFalse(self.record["authorization"]["scientific_p0_or_p1"])
        self.assertFalse(self.record["authorization"]["gpu_training"])

    def test_minimal_artifact_boundary_is_exact(self) -> None:
        artifacts = self.record["artifacts"]
        self.assertTrue(artifacts["private_result_materialized"])
        self.assertEqual(artifacts["private_result_bytes"], 408)
        self.assertEqual(
            artifacts["private_result_sha256"],
            "524df994071abad681d5369ea741b8dc0a680ae895aa568a62308fcfacfb4338",
        )
        self.assertTrue(artifacts["raw_pbs_log_materialized"])
        self.assertEqual(artifacts["raw_pbs_log_bytes"], 0)
        self.assertFalse(artifacts["aggregate_source_inventory_materialized"])

    def test_record_bytes_are_stable_for_provenance_consumers(self) -> None:
        digest = hashlib.sha256(RECORD.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "49fed859e64f4464816678af16c8ac737efdcf57bd01d63bed705a16a369f623",
        )


if __name__ == "__main__":
    unittest.main()
