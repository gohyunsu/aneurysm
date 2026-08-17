import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d10_bounded_repair import (
    D10RepairError,
    baseline_feasible,
    load_config,
    validate_activation,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "aneug_processed_v4_d10_bounded_repair_v1.json"
PBS_PATH = ROOT / "cluster" / "pbs_aneug_processed_v4_d10_round1_v1.pbs"


class D10BoundedRepairTests(unittest.TestCase):
    def test_round_budget_and_single_horizon_change_are_fixed(self) -> None:
        config = load_config(CONFIG_PATH)
        self.assertEqual(config["bounded_repair_budget"]["maximum_repair_rounds"], 2)
        self.assertEqual(config["bounded_repair_budget"]["maximum_training_jobs"], 2)
        self.assertEqual(config["round1_optimization_horizon"]["maximum_epochs"], 251)
        self.assertEqual(config["round1_optimization_horizon"]["seed"], 1103)
        self.assertFalse(config["immutable_boundary"]["change_backbone"])
        self.assertFalse(config["immutable_boundary"]["change_loss"])

    def test_round2_is_conditional_and_not_executable(self) -> None:
        config = load_config(CONFIG_PATH)
        round2 = config["conditional_round2_projection_alignment"]
        self.assertFalse(round2["executable_now"])
        self.assertTrue(round2["requires_round1_pass"])
        self.assertFalse(config["authorization"]["execute_round2_now"])
        self.assertFalse(config["authorization"]["outer_test"])

    def test_baseline_gate_keeps_original_threshold(self) -> None:
        self.assertTrue(baseline_feasible(0.35))
        self.assertFalse(baseline_feasible(0.3500001))
        with self.assertRaises(D10RepairError):
            baseline_feasible(float("nan"))

    def test_activation_binds_failed_d9_and_d9a(self) -> None:
        config = load_config(CONFIG_PATH)
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d10.private_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D10_round1_direct_horizon",
            "outer_or_auxiliary_access": False,
            **{key: config["bound_evidence"][key] for key in ("cache_manifest_sha256", "d9_direct_result_sha256", "d9_aggregate_sha256", "d9a_result_sha256")},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_activation(path, config, "abc")
            payload["d9a_result_sha256"] = "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(D10RepairError):
                validate_activation(path, config, "abc")

    def test_pbs_locks_a6000_read_only_cache_and_new_outputs(self) -> None:
        script = PBS_PATH.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn('$AURORA_D9_CACHE:/cache:ro', script)
        self.assertIn("aneug_processed_v4_d10_bounded_repair", script)
        self.assertIn("round1_result.json", script)
        self.assertIn("round1_direct_best.pt", script)
        self.assertNotIn("outer", script.lower())


if __name__ == "__main__":
    unittest.main()
