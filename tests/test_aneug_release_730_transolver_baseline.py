from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_transolver_baseline import (
    Release730FullCycleTransolver,
    Release730TransolverError,
    load_config,
    validate_activation,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_transolver_baseline_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_transolver_baseline_v1.pbs"
SOURCE = ROOT / "src" / "aurora" / "aneug_release_730_transolver_baseline.py"
LICENSE = ROOT / "third_party" / "TRANSOLVER_LICENSE.txt"


class Release730TransolverBaselineTests(unittest.TestCase):
    def test_config_is_strong_comparator_on_raw_sealed_protocol(self) -> None:
        config = load_config(CONFIG)
        identity = config["comparison_identity"]
        self.assertFalse(identity["exact_upstream_reproduction"])
        self.assertFalse(identity["proposed_method"])
        self.assertEqual(config["split"]["train_cases"], 584)
        self.assertEqual(config["split"]["validation_cases"], 73)
        self.assertFalse(config["split"]["read_locked_test_fields"])
        self.assertFalse(config["split"]["read_processed_only_extra_fields"])
        self.assertFalse(config["target_and_metric"]["hard_tangent_projection"])
        self.assertFalse(config["target_and_metric"]["hard_periodic_closure"])
        self.assertIsNone(config["decision_rule"]["absolute_performance_threshold"])
        self.assertFalse(config["authorization"]["execute_now"])
        self.assertEqual(
            config["runtime"]["container_sha256"],
            "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        )

    def test_sealed_read_projection_closure_threshold_or_execution_is_rejected(self) -> None:
        config = json.loads(CONFIG.read_text())
        mutations = (
            ("split", "read_locked_test_fields", True),
            ("split", "read_processed_only_extra_fields", True),
            ("target_and_metric", "hard_tangent_projection", True),
            ("target_and_metric", "hard_periodic_closure", True),
            ("decision_rule", "absolute_performance_threshold", 0.35),
            ("authorization", "execute_now", True),
        )
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                changed = copy.deepcopy(config)
                changed[section][key] = value
                with self.assertRaises(Release730TransolverError):
                    validate_config(changed)

    def test_small_model_is_permutation_equivariant_raw_and_differentiable(self) -> None:
        torch.manual_seed(43)
        model = Release730FullCycleTransolver(
            width=32,
            heads=4,
            blocks=2,
            slices=4,
            mlp_ratio=2,
            output_phases=4,
        )
        with torch.no_grad():
            bias = model.output.bias.reshape(4, 3)
            bias.zero_()
            bias[:, 2] = 1.0
        weights = torch.rand(11) + 0.1
        weights = weights / weights.sum()
        case = {
            "coordinates": torch.randn(11, 3),
            "normals": torch.tensor([[0.0, 0.0, 1.0]]).expand(11, -1).clone(),
            "vertex_weights": weights,
            "ghd": torch.randn(432),
        }
        field = model(case)
        split_field = model.decode_cycle(model.encode_geometry(case))
        torch.testing.assert_close(split_field, field, rtol=0.0, atol=0.0)
        self.assertEqual(tuple(field.shape), (4, 11, 3))
        self.assertTrue(bool(torch.isfinite(field).all().item()))
        self.assertGreater(float(field[..., 2].abs().mean().item()), 0.5)
        permutation = torch.randperm(11)
        permuted_case = {
            "coordinates": case["coordinates"][permutation],
            "normals": case["normals"][permutation],
            "vertex_weights": case["vertex_weights"][permutation],
            "ghd": case["ghd"],
        }
        with torch.no_grad():
            permuted = model(permuted_case)
        self.assertTrue(
            torch.allclose(permuted, field.detach()[:, permutation], atol=2e-5, rtol=2e-5)
        )
        field.square().mean().backward()
        gradients = [
            parameter.grad
            for parameter in model.parameters()
            if parameter.requires_grad and parameter.grad is not None
        ]
        self.assertTrue(gradients)
        self.assertTrue(all(bool(torch.isfinite(value).all().item()) for value in gradients))

    def test_activation_requires_direct_record_but_allows_flexible_comparator_order(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_transolver_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "single_seed_validation_comparator",
            "direct_baseline_terminal_record_sha256": "direct",
            "ghd_gps_terminal_record_sha256": None,
            "response_oracle_terminal_record_sha256": None,
            "read_locked_test_or_extra": False,
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            changed = copy.deepcopy(activation)
            changed["direct_baseline_terminal_record_sha256"] = ""
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(Release730TransolverError):
                validate_activation(path, config, "abc")
            activation["ghd_gps_terminal_record_sha256"] = "ghd"
            activation["response_oracle_terminal_record_sha256"] = "oracle"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")

    def test_pbs_license_and_source_are_scoped(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("ngpus=1", script)
        self.assertIn("AURORA_TRANSOLVER_ACTIVATION", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("test_manifest", script)
        self.assertNotIn("tangent_projection(", source)
        license_text = LICENSE.read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2024 THUML", license_text)
        self.assertIn("MIT License", license_text)


if __name__ == "__main__":
    unittest.main()
