from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_release_730_objective_scale_audit import (
    ObjectiveScaleAuditError,
    load_config,
    upstream_channel_scale,
    validate_activation,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_objective_scale_audit_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_objective_scale_audit_v1.pbs"


class ObjectiveScaleAuditTests(unittest.TestCase):
    def test_config_is_train_only_cpu_descriptive(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["split"]["train_cases"], 584)
        self.assertFalse(config["split"]["read_validation_fields"])
        self.assertFalse(config["split"]["read_locked_test_fields"])
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertIsNone(config["audit"]["absolute_materiality_threshold"])
        self.assertFalse(config["audit"]["automatic_sensitivity_authorization"])

    def test_sealed_gpu_model_or_threshold_mutation_is_rejected(self) -> None:
        config = json.loads(CONFIG.read_text())
        mutations = (
            ("split", "read_validation_fields", True),
            ("execution", "ngpus", 1),
            ("audit", "model_fit_or_prediction", True),
            ("audit", "absolute_materiality_threshold", 1.1),
            ("audit", "upstream_renormalization_epsilon", 0.0),
        )
        for section, key, value in mutations:
            changed = copy.deepcopy(config)
            changed[section][key] = value
            with self.subTest(section=section, key=key):
                with self.assertRaises(ObjectiveScaleAuditError):
                    validate_config(changed)

    def test_kernel_matches_upstream_phasewise_population_formula(self) -> None:
        try:
            import torch
        except ImportError as error:
            raise unittest.SkipTest(str(error)) from error
        first = torch.zeros((2, 2, 9), dtype=torch.float32)
        second = torch.zeros_like(first)
        first[:, :, 6:9] = torch.tensor(
            [[[0.0, 0.0, 0.0], [2.0, 4.0, 6.0]], [[1.0, 2.0, 3.0], [3.0, 6.0, 9.0]]]
        )
        second[:, :, 6:9] = first[:, :, 6:9] + torch.tensor([2.0, 4.0, 6.0])
        result = upstream_channel_scale(
            [{"tensor": first}, {"tensor": second}],
            torch,
            expected_phases=2,
            expected_nodes=2,
        )
        std = torch.tensor(result["upstream_phase_averaged_channel_std"])
        self.assertTrue(torch.allclose(std / std[0], torch.tensor([1.0, 2.0, 3.0])))
        epsilon = result["upstream_renormalization_epsilon"]
        expected_ratio = float(((std[2] + epsilon) / (std[0] + epsilon)).square())
        self.assertAlmostEqual(
            result["maximum_to_minimum_squared_channel_weight_ratio"],
            expected_ratio,
        )

    def test_activation_requires_exact_sealed_evidence(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_objective_scale_audit_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "single_train_only_cpu_audit",
            "read_validation_test_or_extra": False,
            "use_gpu": False,
            "private_split_sha256": config["source"]["private_split_sha256"],
            "private_train_audit_sha256": config["source"]["private_train_audit_sha256"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            activation["read_validation_test_or_extra"] = True
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaises(ObjectiveScaleAuditError):
                validate_activation(path, config, "abc")

    def test_pbs_uses_no_gpu_and_binds_no_test_or_extra(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("ngpus=0", script)
        self.assertNotIn("--nv", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("test_manifest", script)
        self.assertNotIn("extra_manifest", script)


if __name__ == "__main__":
    unittest.main()
