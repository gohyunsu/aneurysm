from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_release_730_steady_overlap_audit import (
    SteadyOverlapAuditError,
    audit_geometry_overlap,
    load_config,
    validate_activation,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_steady_overlap_audit_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_steady_overlap_audit_v1.pbs"


class SteadyOverlapAuditTests(unittest.TestCase):
    def test_contract_is_geometry_only_cpu_and_not_novelty(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["schema"]["expected_steady_cases"], 14_000)
        self.assertFalse(config["read_scope"]["steady_wss_values"])
        self.assertFalse(config["read_scope"]["locked_test_wss_values"])
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertFalse(config["interpretation"]["steady_supervision_is_novelty"])
        self.assertTrue(config["interpretation"]["rhsia_already_uses_steady_augmentation"])

    def test_field_gpu_or_novelty_mutation_is_rejected(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("read_scope", "steady_wss_values", True),
            ("read_scope", "locked_test_wss_values", True),
            ("execution", "ngpus", 1),
            ("interpretation", "steady_supervision_is_novelty", True),
            ("overlap", "near_rms_limit", 1.0),
        )
        for section, key, value in mutations:
            changed = copy.deepcopy(original)
            changed[section][key] = value
            with self.subTest(section=section, key=key):
                with self.assertRaises(SteadyOverlapAuditError):
                    validate_config(changed)

    def test_exact_near_and_identifier_overlap_are_excluded(self) -> None:
        try:
            import torch
        except ImportError as error:
            raise unittest.SkipTest(str(error)) from error
        transient_ids = ["t0", "t1", "t2", "t3"]
        transient = torch.tensor(
            [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0], [0.01, 0.01]], dtype=torch.float32
        )
        steady_ids = ["s0", "t1", "s2", "s3", "s4"]
        steady = torch.tensor(
            [
                [9.0, 9.0],
                [8.0, 8.0],
                [2.0, 2.0],
                [0.01 + 5.0e-8, 0.01 - 5.0e-8],
                [7.0, 7.0],
            ],
            dtype=torch.float32,
        )
        partitions = {
            "train": ["t0"],
            "validation": ["t1"],
            "test": ["t2"],
            "processed_only_extra": ["t3"],
        }
        public, private = audit_geometry_overlap(
            steady_ids,
            steady,
            transient_ids,
            transient,
            partitions,
            torch,
            expected_steady_cases=5,
            expected_transient_cases=4,
            expected_ghd_width=2,
            expected_partition_counts={
                "train": 1,
                "validation": 1,
                "test": 1,
                "processed_only_extra": 1,
            },
            max_abs_limit=1.0e-6,
            rms_limit=1.0e-7,
            block_rows=2,
        )
        self.assertEqual(public["case_name_exact_pair_count"], 1)
        self.assertEqual(public["ghd_exact_pair_count"], 1)
        self.assertEqual(public["ghd_near_only_pair_count"], 1)
        self.assertEqual(public["excluded_steady_case_count"], 3)
        self.assertEqual(public["eligible_steady_case_count"], 2)
        self.assertEqual(private["eligible_steady_indices"], [0, 4])
        self.assertNotIn("t2", json.dumps(public))

    def test_activation_binds_exact_commit_split_and_no_field_read(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_steady_overlap_audit_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "single_cpu_geometry_only_overlap_audit",
            "read_any_wss_value": False,
            "use_gpu": False,
            "test_wss_opened": False,
            "private_split_sha256": config["source"]["private_split_sha256"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            activation["read_any_wss_value"] = True
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaises(SteadyOverlapAuditError):
                validate_activation(path, config, "abc")

    def test_pbs_is_cpu_only_and_has_no_site_or_excluded_server(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("ngpus=0", script)
        self.assertNotIn("--nv", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("site", script.lower())


if __name__ == "__main__":
    unittest.main()
