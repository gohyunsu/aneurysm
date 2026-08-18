from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_response_oracle import (
    Release730ResponseOracleError,
    fit_basis_from_matrix,
    load_config,
    validate_activation,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_response_oracle_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_response_oracle_v1.pbs"
SOURCE = ROOT / "src" / "aurora" / "aneug_release_730_response_oracle.py"


class Release730ResponseOracleTests(unittest.TestCase):
    def test_config_is_raw_field_oracle_with_test_sealed(self):
        config = load_config(CONFIG)
        self.assertEqual(config["split"]["train_cases"], 584)
        self.assertEqual(config["split"]["validation_cases"], 73)
        self.assertFalse(config["split"]["read_locked_test_fields"])
        self.assertFalse(config["representation"]["hard_tangent_projection"])
        self.assertFalse(config["representation"]["hard_periodic_closure"])
        self.assertFalse(config["representation"]["learned_coefficient_predictor"])
        self.assertIsNone(config["evaluation"]["absolute_performance_threshold"])
        self.assertFalse(config["authorization"]["execute_now"])

    def test_sealed_read_projection_closure_or_threshold_is_rejected(self):
        config = json.loads(CONFIG.read_text())
        mutations = (
            ("split", "read_locked_test_fields", True),
            ("representation", "hard_tangent_projection", True),
            ("representation", "hard_periodic_closure", True),
            ("evaluation", "absolute_performance_threshold", 0.1),
        )
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                changed = copy.deepcopy(config)
                changed[section][key] = value
                with self.assertRaises(Release730ResponseOracleError):
                    validate_config(changed)

    def test_case_gram_basis_reconstructs_centered_training_rows(self):
        torch.manual_seed(31)
        latent = torch.randn(7, 3, dtype=torch.float64)
        decoder = torch.randn(3, 23, dtype=torch.float64)
        matrix = latent @ decoder
        matrix = matrix / torch.linalg.vector_norm(matrix, dim=1, keepdim=True)
        fitted = fit_basis_from_matrix(matrix.clone(), maximum_rank=3)
        centered = matrix - fitted["mean"]
        coefficients = centered @ fitted["basis"].T
        reconstructed = fitted["mean"] + coefficients @ fitted["basis"]
        self.assertTrue(torch.allclose(reconstructed, matrix, atol=1e-8, rtol=1e-7))
        self.assertLess(float(fitted["orthogonality_error"]), 1e-8)

    def test_activation_requires_terminal_direct_baseline_and_sealed_scope(self):
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_response_oracle_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "single_validation_response_oracle",
            "direct_baseline_terminal_record_sha256": "123",
            "read_locked_test_or_extra": False,
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            activation["direct_baseline_terminal_record_sha256"] = ""
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaises(Release730ResponseOracleError):
                validate_activation(path, config, "abc")

    def test_pbs_is_serialized_introai9_gpu_and_has_no_test_binding(self):
        script = PBS.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("ngpus=1", script)
        self.assertIn("AURORA_RESPONSE_ORACLE_ACTIVATION", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("test_manifest", script)
        self.assertNotIn("tangent_projection(", source)


if __name__ == "__main__":
    unittest.main()
