from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


class AneumoBCTransportExecutionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).parents[1]
        self.record_path = (
            root / "results" / "aneumo_bc_transport_p0_execution_20260810.json"
        )
        self.record = json.loads(self.record_path.read_text(encoding="utf-8"))
        self.protocol = json.loads(
            (root / "configs" / "aurora_v1.json").read_text(encoding="utf-8")
        )

    def test_record_is_incomplete_without_scientific_verdict(self) -> None:
        self.assertEqual(
            self.record["status"], "execution_incomplete_no_scientific_verdict"
        )
        self.assertFalse(self.record["scientific_gate_evaluated"])
        self.assertFalse(self.record["artifacts"]["aggregate_result_materialized"])
        self.assertFalse(self.record["artifacts"]["raw_pbs_output_materialized"])
        self.assertIsNone(self.record["source_members_completed"])
        self.assertFalse(self.record["authorization"]["p1_registration"])
        self.assertFalse(self.record["authorization"]["method"])
        self.assertFalse(self.record["authorization"]["gpu_training"])

    def test_execution_is_exact_one_shot_introai9_cpu_only(self) -> None:
        execution = self.record["execution"]
        self.assertEqual(execution["server"], "introai9")
        self.assertEqual(execution["submission_count_for_exact_source"], 1)
        self.assertEqual(execution["requested_ngpus"], 0)
        self.assertFalse(execution["login_node_gpu_command_executed"])
        self.assertFalse(execution["junjinyong_accessed"])
        self.assertEqual(self.record["public_source_commit"], "38e7894fc5ae56ffb3efbe469c4e1f7480f81feb")

    def test_protocol_pins_the_exact_public_record(self) -> None:
        audit = self.protocol["problem_selection"]["aneumo_bc_transport_source_audit"]
        digest = hashlib.sha256(self.record_path.read_bytes()).hexdigest()
        self.assertEqual(digest, audit["p0_execution_record_sha256"])
        self.assertEqual(audit["p0_exit_status"], 1)
        self.assertFalse(audit["p0_scientific_gate_evaluated"])
        self.assertFalse(audit["p1_registration_authorized"])


if __name__ == "__main__":
    unittest.main()
