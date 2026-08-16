from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d7_draft import D7DraftError, load_contract, main, validate_contract


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d7_train_field_admission_draft_v1.json"


class AneuGProcessedV4D7DraftTests(unittest.TestCase):
    def test_draft_is_non_executable_and_preserves_closed_versions(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["status"], "dormant_unselected_non_executable")
        self.assertEqual(contract["bound_prior_evidence"]["closed_d6_attempts"], "1/1")
        self.assertEqual(contract["bound_prior_evidence"]["closed_e0_attempts"], "1/1")
        self.assertFalse(contract["identity"]["d6_retry_repair_resume_or_relabel"])
        self.assertFalse(contract["selection_boundary"]["pbs_submission_authorized"])
        self.assertFalse(contract["selection_boundary"]["field_read_authorized"])
        with self.assertRaisesRegex(D7DraftError, "non_executable_draft"):
            main(["--config", str(CONFIG)])

    def test_only_train_read_is_prospective_and_none_occurs_now(self) -> None:
        read = load_contract(CONFIG)["prospective_read_boundary"]
        self.assertTrue(read["read_d5_train_tensor_values"])
        self.assertTrue(read["read_shared_finest_faces"])
        self.assertFalse(read["read_validation_tensor_values"])
        self.assertFalse(read["read_outer_test_tensor_values"])
        self.assertFalse(read["read_auxiliary_tensor_values"])
        self.assertFalse(read["fit_or_select_model"])
        self.assertFalse(read["read_values_now"])

    def test_e0_wrapper_lessons_are_non_negotiable(self) -> None:
        envelope = load_contract(CONFIG)["required_execution_envelope"]
        self.assertTrue(envelope["attempt_marker_and_internal_log_before_strict_mode"])
        self.assertTrue(envelope["attempt_marker_and_internal_log_before_profile_or_environment_checks"])
        self.assertFalse(envelope["source_etc_profile_inside_wrapper"])
        self.assertTrue(envelope["scheduler_stdout_stderr_is_not_evidence_channel"])
        self.assertEqual(envelope["ngpus"], 0)

    def test_activation_scope_and_resource_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("status", None, "active", "status"),
            ("identity", "d6_retry_repair_resume_or_relabel", True, "identity"),
            ("prospective_read_boundary", "read_validation_tensor_values", True, "read_boundary"),
            ("prospective_read_boundary", "read_values_now", True, "read_boundary"),
            ("required_execution_envelope", "ngpus", 1, "resources"),
            ("required_execution_envelope", "maximum_pbs_attempts", 2, "attempt_budget"),
            ("required_execution_envelope", "source_etc_profile_inside_wrapper", True, "profile"),
            ("selection_boundary", "pbs_submission_authorized", True, "selection"),
            ("selection_boundary", "field_read_authorized", True, "selection"),
            ("conditional_consequence", "complete_pass_is_paper_result", True, "consequence"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            if key is None:
                candidate[section] = value
            else:
                candidate[section][key] = value
            with self.assertRaisesRegex(D7DraftError, reason):
                validate_contract(candidate)


if __name__ == "__main__":
    unittest.main()
