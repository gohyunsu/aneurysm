from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from aurora.aneug_release_730_train_audit import (
    Release730TrainAuditError,
    index_case_records,
    load_config,
    selected_training_records,
    validate_config,
    validate_split_evidence,
)
from aurora.aneug_release_730_split import _canonical_digest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_train_audit_v1.json"


class GuardedCase(dict):
    def __getitem__(self, key):
        if key == "tensor":
            raise AssertionError("sealed tensor was accessed")
        return super().__getitem__(key)


class Release730TrainAuditTests(unittest.TestCase):
    def test_config_is_train_only_cpu_and_retry_flexible(self):
        config = load_config(CONFIG)
        self.assertEqual(config["split"]["train_cases"], 584)
        self.assertFalse(config["read_scope"]["read_validation_field_values"])
        self.assertFalse(config["read_scope"]["read_test_field_values"])
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertTrue(
            config["execution"]["diagnosed_infrastructure_or_implementation_retry_allowed"]
        )

    def test_gpu_or_sealed_read_mutation_is_rejected(self):
        config = json.loads(CONFIG.read_text())
        for section, key, value in (
            ("execution", "ngpus", 1),
            ("read_scope", "read_validation_field_values", True),
            ("read_scope", "read_test_field_values", True),
        ):
            mutated = copy.deepcopy(config)
            mutated[section][key] = value
            with self.assertRaises(Release730TrainAuditError):
                validate_config(mutated)

    def test_exact_private_partition_and_digests_are_required(self):
        config = load_config(CONFIG)
        train = [f"stable_train_{index}" for index in range(584)]
        validation = [f"stable_validation_{index}" for index in range(73)]
        test = [f"stable_test_{index}" for index in range(73)]
        extras = [f"extra_{index}" for index in range(79)]
        config = copy.deepcopy(config)
        config["split"]["train_case_digest"] = _canonical_digest(train)
        config["split"]["validation_case_digest"] = _canonical_digest(validation)
        config["split"]["test_case_digest"] = _canonical_digest(test)
        release = train + validation + test
        public = {
            "status": "complete",
            "registered_field_values_read": False,
            "test_opened": False,
            "release_case_id_sha256": _canonical_digest(release),
        }
        component = lambda value: {
            "case_ids": [value], "case_count": 1, "component_digest": "unused"
        }
        private = {
            "schema_version": "aurora.aneug_release_730.private_split.v1",
            "registered_field_values_read": False,
            "test_opened": False,
            "source_sha256": config["source"]["processed_v5_sha256"],
            "split_key_sha256": config["split"]["split_key_sha256"],
            "train_components": [component(value) for value in train],
            "validation_components": [component(value) for value in validation],
            "test_components": [component(value) for value in test],
            "processed_extra_case_ids": extras,
            "release_case_ids": release,
        }
        buckets = validate_split_evidence(config, public, private)
        self.assertEqual(tuple(map(len, buckets.values())), (584, 73, 73, 79))
        private["test_opened"] = True
        with self.assertRaisesRegex(Release730TrainAuditError, "private_test_opened"):
            validate_split_evidence(config, public, private)

    def test_digest_grammar_is_shared_with_release_split(self):
        expected = hashlib.sha256(b"stable_a\nstable_b").hexdigest()
        self.assertEqual(_canonical_digest(["stable_b", "stable_a"]), expected)

    def test_sealed_records_are_not_tensor_indexed(self):
        cases = [
            {"case": "train", "tensor": object()},
            GuardedCase(case="validation"),
            GuardedCase(case="test"),
        ]
        ordered, indexed = index_case_records(cases)
        self.assertEqual(ordered, ["train", "validation", "test"])
        selected = selected_training_records(
            indexed, ["train"], ["validation", "test"]
        )
        self.assertEqual(len(selected), 1)
        self.assertIs(selected[0]["tensor"], cases[0]["tensor"])


class Release730TrainAuditOutcomeTests(unittest.TestCase):
    def test_r2_public_result_is_exact_train_only_and_threshold_free(self):
        path = ROOT / "results" / "aneug_release_730_train_audit_r2_20260818.json"
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            "3c525820023a56862c6652441c5d00f43412d3c868840149e5f120b8ed2a9587",
        )
        result = json.loads(path.read_text())
        self.assertEqual(result["status"], "complete_passed")
        self.assertTrue(result["integrity_pass"])
        self.assertEqual(result["integrity_failures"], [])
        self.assertEqual(result["train_case_count"], 584)
        self.assertEqual(result["validation_field_case_count_read"], 0)
        self.assertEqual(result["test_field_case_count_read"], 0)
        self.assertEqual(result["processed_only_extra_field_case_count_read"], 0)
        self.assertFalse(result["test_opened"])
        self.assertFalse(result["model_fitted_or_selected"])
        self.assertTrue(result["descriptive_values_are_not_model_pass_thresholds"])
        boundary = result["descriptive_case_distributions"]["phase_boundary_relative_jump"]
        self.assertGreater(boundary["max"], boundary["q95"])


if __name__ == "__main__":
    unittest.main()
