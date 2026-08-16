from __future__ import annotations

import copy
import hashlib
import json
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d6 import D6ContractError, assert_execution_authorized
from aurora.aneug_processed_v4_d6_execution import (
    D6ExecutionError,
    _strict_atomic_json,
    load_execution_contract,
    run_execution,
    validate_execution_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_V1 = ROOT / "configs" / "aneug_processed_v4_d6_execution_v1.json"
CONFIG_V2 = ROOT / "configs" / "aneug_processed_v4_d6_execution_v2.json"
REGISTRATION = ROOT / "configs" / "aneug_processed_v4_d6_train_field_audit_v1.json"
PBS_V1 = ROOT / "cluster" / "pbs_aneug_processed_v4_d6_execution_v1.pbs"
PBS_V2 = ROOT / "cluster" / "pbs_aneug_processed_v4_d6_execution_v2.pbs"


class AneuGProcessedV4D6ExecutionTests(unittest.TestCase):
    def test_fresh_contract_activates_only_d6_train_cpu_attempt(self) -> None:
        contract = load_execution_contract(CONFIG_V2)
        self.assertEqual(contract["human_activation"]["selection"], "D6")
        self.assertEqual(contract["bound_prior_evidence"]["expected_train_cases"], 406)
        self.assertFalse(contract["read_boundary"]["read_validation_tensor_values"])
        self.assertFalse(contract["read_boundary"]["read_outer_test_tensor_values"])
        self.assertEqual(contract["execution"]["ngpus"], 0)
        self.assertEqual(contract["execution"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["execution"]["rerun_or_repair_after_any_outcome"])
        self.assertEqual(
            contract["source_identity"]["steady"]["relative_server_path"],
            "processed_v4_d2/assembled_registered_steady_data_1k_v4.pth.temporary",
        )

    def test_v1_is_withdrawn_before_field_or_submission_and_cannot_execute(self) -> None:
        contract = load_execution_contract(CONFIG_V1)
        self.assertEqual(
            contract["status"], "withdrawn_before_field_read_or_pbs_submission"
        )
        self.assertFalse(contract["withdrawal"]["train_field_values_read"])
        self.assertEqual(contract["withdrawal"]["pbs_attempts_used"], 0)
        self.assertFalse(contract["withdrawal"]["output_record_created"])
        self.assertFalse(contract["withdrawal"]["may_execute"])

    def test_original_registration_remains_immutable_and_non_executable(self) -> None:
        execution = load_execution_contract(CONFIG_V2)
        digest = hashlib.sha256(REGISTRATION.read_bytes()).hexdigest()
        self.assertEqual(digest, execution["immutable_registration"]["sha256"])
        registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(D6ContractError, "not_activated"):
            assert_execution_authorized(registration)

    def test_scope_attempt_and_server_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG_V2.read_text(encoding="utf-8"))
        mutations = (
            ("status", None, "registered_not_activated", "status"),
            ("read_boundary", "read_validation_tensor_values", True, "read_validation"),
            ("execution", "ngpus", 1, "resources"),
            ("execution", "maximum_pbs_attempts", 2, "attempt_budget"),
            ("execution", "rerun_or_repair_after_any_outcome", True, "rerun"),
            ("execution", "excluded_server", "", "excluded_server"),
            ("authorization", "paper_result_or_claim", True, "paper_result"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            if key is None:
                candidate[section] = value
            else:
                candidate[section][key] = value
            with self.assertRaisesRegex(D6ExecutionError, reason):
                validate_execution_contract(candidate)

    def test_strict_atomic_output_refuses_nan_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            with self.assertRaises(ValueError):
                _strict_atomic_json(target, {"value": math.nan})
            self.assertFalse(target.exists())
            self.assertFalse(target.with_name("result.json.tmp").exists())
            _strict_atomic_json(target, {"gate_pass": True})
            self.assertEqual(json.loads(target.read_text()), {"gate_pass": True})
            with self.assertRaisesRegex(D6ExecutionError, "output_exists"):
                _strict_atomic_json(target, {"gate_pass": False})

    def test_pbs_wrapper_is_cpu_only_one_shot_and_shell_valid(self) -> None:
        text = PBS_V2.read_text(encoding="utf-8")
        self.assertIn("ncpus=4:mem=64gb:ngpus=0", text)
        self.assertIn("attempt.started", text)
        self.assertIn("rerun or repair is forbidden", text)
        self.assertIn("AURORA_D5_PRIVATE_MANIFEST", text)
        self.assertIn("processed_v4_d2/assembled_registered_steady_data_1k_v4.pth.temporary", text)
        self.assertIn("aneug_processed_v4_d6_execution_v1", text)
        self.assertNotIn("junjinyong", text)
        subprocess.run(["bash", "-n", str(PBS_V1)], check=True)
        subprocess.run(["bash", "-n", str(PBS_V2)], check=True)

    def test_withdrawn_v1_cannot_be_silently_reactivated(self) -> None:
        original = json.loads(CONFIG_V1.read_text(encoding="utf-8"))
        candidate = copy.deepcopy(original)
        candidate["withdrawal"]["may_execute"] = True
        with self.assertRaisesRegex(D6ExecutionError, "v1_execution"):
            validate_execution_contract(candidate)
        with self.assertRaisesRegex(D6ExecutionError, "only_fresh_d6_v2_may_execute"):
            run_execution(
                CONFIG_V1,
                REGISTRATION,
                Path("missing-transient"),
                Path("missing-steady"),
                Path("missing-manifest"),
                Path("missing-public"),
                Path("missing-private"),
                None,
            )


if __name__ == "__main__":
    unittest.main()
