from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from aurora.aneug_release_730_steady_scale_audit import (
    SteadyScaleAuditError,
    eligible_steady_scale,
    load_config,
    validate_activation_payload,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_steady_scale_audit_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_steady_scale_audit_v1.pbs"


class SteadyScaleAuditTests(unittest.TestCase):
    def test_config_is_cpu_descriptive_and_oracle_ordered(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["scope"]["eligible_steady_rows"], 13_985)
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertTrue(
            config["authorization"][
                "execute_after_quality_private_activation_and_response_oracle_terminal"
            ]
        )
        self.assertIsNone(config["audit"]["absolute_materiality_threshold"])
        self.assertFalse(config["audit"]["automatic_loss_weight"])

    def test_scope_model_gpu_or_weight_mutation_fails(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("scope", "eligible_steady_rows", 14_000),
            ("execution", "ngpus", 1),
            ("audit", "automatic_loss_weight", True),
            ("audit", "absolute_materiality_threshold", 1.0),
            ("authorization", "read_transient_wss", True),
        )
        for section, key, value in mutations:
            changed = copy.deepcopy(config)
            changed[section][key] = value
            with self.subTest(section=section, key=key):
                with self.assertRaises(SteadyScaleAuditError):
                    validate_config(changed)

    def test_activation_requires_oracle_and_sealed_scope(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_steady_scale_audit_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "single_eligible_steady_cpu_scale_audit",
            "response_oracle_terminal_record_sha256": "1" * 64,
            "private_overlap_result_sha256": config["source"]["private_overlap_result_sha256"],
            "private_train_audit_sha256": config["source"]["private_train_audit_sha256"],
            "read_transient_validation_test_or_extra": False,
            "use_gpu": False,
        }
        validate_activation_payload(activation, config, "abc")
        for key, value in (
            ("response_oracle_terminal_record_sha256", None),
            ("read_transient_validation_test_or_extra", True),
            ("use_gpu", True),
        ):
            changed = copy.deepcopy(activation)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(SteadyScaleAuditError):
                validate_activation_payload(changed, config, "abc")

    def test_kernel_matches_direct_physical_moments(self) -> None:
        try:
            import torch
        except ImportError as error:
            raise unittest.SkipTest(str(error)) from error
        tensor = torch.zeros((3, 2, 9), dtype=torch.float32)
        tensor[0, :, 6:9] = torch.tensor([[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]])
        tensor[1, :, 6:9] = torch.tensor([[3.0, 4.0, 5.0], [4.0, 5.0, 6.0]])
        tensor[2, :, 6:9] = 100.0
        archive = {
            "tensor": tensor,
            "tensor_norm": {
                "mean": torch.zeros(9),
                "std": torch.ones(9),
            },
        }
        physical = tensor[:2, :, 6:9].to(torch.float64) * 1.00001
        component_mean = physical.mean(dim=(0, 1))
        component_std = physical.reshape(-1, 3).std(dim=0, correction=0)
        vector_rms = torch.sqrt(physical.square().sum(dim=-1).mean())
        train_audit = {
            "schema_version": "aurora.aneug_release_730_train_audit.private_statistics.v1",
            "train_case_count": 584,
            "validation_test_or_extra_statistics_included": False,
            "wss_physical": {
                "mean": [0.0, 0.0, 0.0],
                "std_population": [1.0, 1.0, 1.0],
            },
        }
        result = eligible_steady_scale(
            archive,
            [0, 1],
            train_audit,
            torch,
            expected_nodes=2,
            block_rows=1,
        )
        self.assertTrue(
            torch.allclose(
                torch.tensor(result["physical_component_mean"], dtype=torch.float64),
                component_mean,
            )
        )
        self.assertTrue(
            torch.allclose(
                torch.tensor(
                    result["physical_component_std_population"], dtype=torch.float64
                ),
                component_std,
            )
        )
        self.assertAlmostEqual(result["steady_physical_vector_rms"], float(vector_rms))
        self.assertAlmostEqual(
            result["steady_to_transient_vector_rms_ratio"],
            float(vector_rms / math.sqrt(3.0)),
        )

    def test_kernel_rejects_duplicate_or_out_of_range_indices(self) -> None:
        try:
            import torch
        except ImportError as error:
            raise unittest.SkipTest(str(error)) from error
        archive = {
            "tensor": torch.zeros((2, 1, 9), dtype=torch.float32),
            "tensor_norm": {"mean": torch.zeros(9), "std": torch.ones(9)},
        }
        audit = {
            "schema_version": "aurora.aneug_release_730_train_audit.private_statistics.v1",
            "train_case_count": 584,
            "validation_test_or_extra_statistics_included": False,
            "wss_physical": {"mean": [0.0] * 3, "std_population": [1.0] * 3},
        }
        for indices in ([0, 0], [2]):
            with self.subTest(indices=indices), self.assertRaises(SteadyScaleAuditError):
                eligible_steady_scale(
                    archive, indices, audit, torch, expected_nodes=1, block_rows=1
                )

    def test_pbs_is_cpu_only_and_binds_no_transient_asset(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("ngpus=0", script)
        self.assertNotIn("--nv", script)
        self.assertNotIn("processed_v5", script)
        self.assertNotIn("junjinyong", script)
        self.assertIn("AURORA_PRIVATE_OVERLAP_RESULT", script)
        self.assertIn("AURORA_PRIVATE_TRAIN_AUDIT", script)


if __name__ == "__main__":
    unittest.main()
