from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d7_execution import (
    D7ExecutionError,
    _strict_atomic_json,
    load_execution_contract,
    validate_execution_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d7_execution_v1.json"
DRAFT = ROOT / "configs" / "aneug_processed_v4_d7_train_field_admission_draft_v1.json"
REGISTRATION = ROOT / "configs" / "aneug_processed_v4_d6_train_field_audit_v1.json"
EVALUATOR = ROOT / "src" / "aurora" / "aneug_processed_v4_d6.py"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d7_execution_v1.pbs"


class AneuGProcessedV4D7ExecutionTests(unittest.TestCase):
    def test_fresh_d7_activation_preserves_draft_d6_and_e0(self) -> None:
        contract = load_execution_contract(CONFIG)
        self.assertEqual(contract["human_activation"]["selection"], "D7")
        self.assertTrue(
            contract["human_activation"][
                "does_not_repair_resume_rerun_reopen_or_relabel_d6"
            ]
        )
        self.assertEqual(contract["bound_prior_evidence"]["closed_d6_attempts"], "1/1")
        self.assertEqual(contract["bound_prior_evidence"]["closed_e0_attempts"], "1/1")
        self.assertTrue(contract["immutable_dormant_draft"]["remains_non_executable"])

    def test_exact_dormant_draft_and_scientific_kernel_are_bound(self) -> None:
        contract = load_execution_contract(CONFIG)
        self.assertEqual(
            hashlib.sha256(DRAFT.read_bytes()).hexdigest(),
            contract["immutable_dormant_draft"]["sha256"],
        )
        self.assertEqual(
            hashlib.sha256(REGISTRATION.read_bytes()).hexdigest(),
            contract["immutable_scientific_kernel"]["registration_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(EVALUATOR.read_bytes()).hexdigest(),
            contract["immutable_scientific_kernel"]["evaluator_sha256"],
        )
        self.assertFalse(
            contract["immutable_scientific_kernel"]["threshold_or_metric_change"]
        )

    def test_scope_attempt_resource_and_claim_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("status", None, "draft", "status"),
            ("human_activation", "selection", "D6", "human_selection_name"),
            ("read_boundary", "read_validation_tensor_values", True, "read_boundary"),
            ("execution", "ngpus", 1, "resources"),
            ("execution", "maximum_pbs_attempts", 2, "attempt_budget"),
            ("execution", "source_etc_profile_inside_wrapper", True, "execution"),
            ("consequence", "pass_is_paper_result", True, "consequence"),
            ("authorization", "gpu_training", True, "authorization"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            if key is None:
                candidate[section] = value
            else:
                candidate[section][key] = value
            with self.assertRaisesRegex(D7ExecutionError, reason):
                validate_execution_contract(candidate)

    def test_atomic_output_is_strict_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            _strict_atomic_json(target, {"gate_pass": True})
            self.assertEqual(json.loads(target.read_text()), {"gate_pass": True})
            with self.assertRaisesRegex(D7ExecutionError, "output_exists"):
                _strict_atomic_json(target, {"gate_pass": False})

    def test_pbs_wrapper_records_before_strict_mode_and_never_sources_profile(self) -> None:
        text = PBS.read_text(encoding="utf-8")
        marker = text.index("attempt.started")
        internal_log = text.index('exec >>"$record_root/attempt.log"')
        strict = text.index("set -euo pipefail")
        self.assertLess(marker, strict)
        self.assertLess(internal_log, strict)
        self.assertNotIn("source /etc/profile", text)
        self.assertIn("ncpus=4:mem=64gb:ngpus=0", text)
        self.assertIn("PBS_O_WORKDIR", text)
        self.assertIn("rerun or repair is forbidden", text)
        self.assertIn("AURORA_D5_PRIVATE_MANIFEST", text)
        self.assertNotIn("#PBS -o", text)
        self.assertNotIn("#PBS -e", text)
        subprocess.run(["bash", "-n", str(PBS)], check=True)


if __name__ == "__main__":
    unittest.main()
