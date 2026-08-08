from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "results" / "flow_mri_protocol_i0b_execution_20260809.json"


class FlowMRII0bExecutionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_record_hash_is_pinned_in_protocol(self) -> None:
        digest = hashlib.sha256(RECORD.read_bytes()).hexdigest()
        protocol = json.loads(
            (ROOT / "configs" / "aurora_v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(digest, protocol["task"]["i0b_execution_record_sha256"])

    def test_execution_stopped_before_any_asset_or_field_access(self) -> None:
        access = self.payload["access_audit"]
        self.assertEqual(
            access["failure_stage"],
            "scientific_dependency_import_before_archive_index_or_field_access",
        )
        numeric_access = [
            value
            for key, value in access.items()
            if key != "failure_stage" and not isinstance(value, bool)
        ]
        self.assertTrue(all(value == 0 for value in numeric_access))
        self.assertFalse(access["GPU_used"])
        self.assertFalse(
            self.payload["raw_private_artifacts"]["velocity_cache_created"]
        )
        self.assertFalse(
            self.payload["raw_private_artifacts"]["scientific_result_created"]
        )

    def test_missing_dependency_is_a_packaging_failure_not_a_gate_verdict(self) -> None:
        environment = self.payload["environment"]
        self.assertEqual(environment["missing_dependency"], "h5py")
        self.assertFalse(environment["known_external_h5py_3_12_1_layer_bound"])
        verdict = self.payload["verdict"]
        self.assertEqual(verdict["gate_status"], "not_evaluated")
        self.assertEqual(verdict["scientific_verdict"], "none")
        self.assertFalse(verdict["task_adequacy_supported"])
        self.assertFalse(verdict["task_adequacy_refuted"])

    def test_record_cannot_authorize_repair_method_or_submission(self) -> None:
        verdict = self.payload["verdict"]
        self.assertFalse(verdict["local_dependency_repair_or_I0b_rerun_allowed"])
        self.assertFalse(verdict["I0c_authorized"])
        self.assertFalse(verdict["neural_or_GPU_training_authorized"])
        self.assertFalse(verdict["outer_test_authorized"])
        self.assertFalse(verdict["submission_authorized"])
        self.assertFalse(verdict["method_selected"])


if __name__ == "__main__":
    unittest.main()
