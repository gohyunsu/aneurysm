from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "results"
    / "nonlinear_pde_n1_missing_operator_pullback_m0_execution_20260808.json"
)


class M0ExecutionRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_record_hash_is_pinned_in_protocol(self) -> None:
        digest = hashlib.sha256(RECORD.read_bytes()).hexdigest()
        protocol = json.loads(
            (ROOT / "configs" / "aurora_v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            digest,
            protocol["venue"]["m0_execution_record_sha256"],
        )

    def test_record_is_provenance_not_a_metric_aggregate(self) -> None:
        self.assertEqual(
            self.payload["evidence_status"],
            "execution_incomplete_no_scientific_verdict",
        )
        self.assertEqual(
            [task["state"] for task in self.payload["tasks"]],
            ["completed", "failed", "completed"],
        )
        gate = self.payload["gate"]
        self.assertEqual(gate["completed_seeds"], 2)
        self.assertEqual(gate["failed_seeds"], 1)
        self.assertFalse(gate["aggregate_created"])
        self.assertFalse(gate["gate_decided"])
        self.assertIsNone(gate["passed"])
        self.assertEqual(gate["scientific_verdict"], "not_available")

    def test_record_cannot_select_or_authorize_a_method(self) -> None:
        decision = self.payload["decision"]
        self.assertFalse(decision["sampler_repair_or_rerun_registered"])
        self.assertFalse(decision["fresh_reentry_registered"])
        self.assertFalse(decision["method_selected"])
        self.assertFalse(decision["method_novelty_established"])
        self.assertFalse(decision["n1d_or_irregular_3d_authorized"])
        self.assertTrue(decision["successful_seed_metrics_may_not_be_cherry_picked"])

    def test_successful_seed_metrics_were_not_inspected_for_gate(self) -> None:
        successful = [
            task for task in self.payload["tasks"] if task["state"] == "completed"
        ]
        self.assertEqual(len(successful), 2)
        self.assertTrue(
            all(task["metrics_inspected_for_gate"] is False for task in successful)
        )


if __name__ == "__main__":
    unittest.main()
