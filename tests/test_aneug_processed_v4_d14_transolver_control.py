import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_processed_v4_d14_transolver_control import (
    FullCycleTransolver,
    PhysicsSliceAttention,
    load_config,
    validate_activation,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d14_transolver_control_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d14_transolver_control_v1.pbs"
LICENSE = ROOT / "third_party" / "TRANSOLVER_LICENSE.txt"


class D14TransolverControlTests(unittest.TestCase):
    def test_config_is_a_non_executable_comparator_without_threshold(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["architecture"]["blocks"], 8)
        self.assertEqual(config["architecture"]["output_phases"], 80)
        self.assertFalse(config["comparison_identity"]["proposed_method"])
        self.assertIsNone(config["decision_rule"]["absolute_field_threshold"])
        self.assertFalse(config["authorization"]["execute_now"])
        self.assertFalse(config["bound_data"]["read_outer_or_auxiliary"])

    def test_physics_attention_is_node_permutation_equivariant(self) -> None:
        torch.manual_seed(31)
        attention = PhysicsSliceAttention(width=32, heads=4, slices=5).eval()
        features = torch.randn(13, 32)
        permutation = torch.randperm(features.shape[0])
        reference = attention(features)
        permuted = attention(features[permutation])
        self.assertTrue(
            torch.allclose(permuted, reference[permutation], atol=2e-5, rtol=2e-5)
        )

    def test_small_full_cycle_model_is_tangent_and_differentiable(self) -> None:
        torch.manual_seed(37)
        model = FullCycleTransolver(
            width=32,
            heads=4,
            blocks=2,
            slices=4,
            mlp_ratio=2,
            output_phases=4,
        )
        normals = torch.zeros(11, 3)
        normals[:, 2] = 1.0
        weights = torch.rand(11) + 0.1
        weights = weights / weights.sum()
        case = {
            "coordinates": torch.randn(11, 3),
            "normals": normals,
            "vertex_weights": weights,
            "ghd": torch.randn(432),
        }
        field = model(case)["field"]
        self.assertEqual(tuple(field.shape), (4, 11, 3))
        self.assertLess(float(torch.max(torch.abs(field[..., 2])).item()), 1e-7)
        field.square().mean().backward()
        gradients = [
            parameter.grad
            for parameter in model.parameters()
            if parameter.requires_grad and parameter.grad is not None
        ]
        self.assertTrue(gradients)
        self.assertTrue(all(torch.isfinite(gradient).all() for gradient in gradients))

    def test_activation_requires_d12_terminal_record(self) -> None:
        config = load_config(CONFIG)
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d14.private_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D14_Transolver_validation_control",
            "d12_terminal_record_sha256": "123",
            "outer_or_auxiliary_access": False,
            "cache_manifest_sha256": config["bound_data"]["cache_manifest_sha256"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_activation(path, config, "abc")
            payload["d12_terminal_record_sha256"] = ""
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                validate_activation(path, config, "abc")

    def test_pbs_and_license_are_scoped(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("AURORA_D14_ACTIVATION", script)
        self.assertIn("--checkpoint /output/d14_checkpoint.pt", script)
        self.assertNotIn("junjinyong", script)
        license_text = LICENSE.read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2024 THUML", license_text)
        self.assertIn("MIT License", license_text)


if __name__ == "__main__":
    unittest.main()
