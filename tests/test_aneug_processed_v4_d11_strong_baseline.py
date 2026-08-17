import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_processed_v4_d11_strong_baseline import (
    D11StrongBaselineError,
    GHDConditionedGPSUNet,
    baseline_feasible,
    load_config,
    validate_activation,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "aneug_processed_v4_d11_strong_baseline_v1.json"
PBS_PATH = ROOT / "cluster" / "pbs_aneug_processed_v4_d11_strong_baseline_v1.pbs"
SOURCE_PATH = ROOT / "src" / "aurora" / "aneug_processed_v4_d11_strong_baseline.py"


def synthetic_topology() -> dict[str, torch.Tensor]:
    return {
        "edge0": torch.tensor(
            [[0, 1, 1, 2, 2, 3, 3, 0], [1, 0, 2, 1, 3, 2, 0, 3]],
            dtype=torch.int64,
        ),
        "edge1": torch.tensor([[0, 1], [1, 0]], dtype=torch.int64),
        "edge2": torch.tensor([[0], [0]], dtype=torch.int64),
        "idx1": torch.tensor([0, 2], dtype=torch.int64),
        "idx2": torch.tensor([0], dtype=torch.int64),
        "parent1": torch.tensor([0, 0, 1, 1], dtype=torch.int64),
        "parent2": torch.tensor([0, 0], dtype=torch.int64),
    }


class D11StrongBaselineTests(unittest.TestCase):
    def test_config_declares_matched_reimplementation_and_sealed_scope(self) -> None:
        config = load_config(CONFIG_PATH)
        identity = config["adaptation_identity"]
        self.assertEqual(identity["claim"], "matched_reimplementation_not_reproduction")
        self.assertFalse(identity["uses_torch_geometric"])
        self.assertFalse(identity["uses_pytorch3d"])
        self.assertFalse(config["data_boundary"]["read_outer_or_auxiliary"])
        self.assertFalse(config["authorization"]["outer_test"])
        self.assertFalse(config["authorization"]["functional_readout_training"])

    def test_model_has_finite_tangent_full_cycle(self) -> None:
        torch.manual_seed(7)
        model = GHDConditionedGPSUNet(synthetic_topology(), width=16, heads=4)
        coordinates = torch.tensor(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
        )
        case = {
            "coordinates": coordinates,
            "normals": torch.tensor([[0.0, 0.0, 1.0]]).expand(4, -1).clone(),
            "vertex_weights": torch.ones(4),
            "ghd": torch.zeros(432),
        }
        field = model(case)["field"]
        self.assertEqual(tuple(field.shape), (80, 4, 3))
        self.assertTrue(bool(torch.isfinite(field).all().item()))
        self.assertLess(float(field[..., 2].abs().max().item()), 1e-6)
        field.square().mean().backward()
        self.assertTrue(
            all(
                parameter.grad is None or bool(torch.isfinite(parameter.grad).all().item())
                for parameter in model.parameters()
            )
        )

    def test_gate_keeps_absolute_feasibility_requirement(self) -> None:
        self.assertTrue(baseline_feasible(0.35))
        self.assertFalse(baseline_feasible(0.350001))
        with self.assertRaises(D11StrongBaselineError):
            baseline_feasible(float("nan"))

    def test_activation_binds_d10_and_cache(self) -> None:
        config = load_config(CONFIG_PATH)
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d11.private_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D11_strong_baseline_validation",
            "outer_or_auxiliary_access": False,
            **{
                key: config["bound_evidence"][key]
                for key in (
                    "cache_manifest_sha256",
                    "d10_result_sha256",
                    "d10_checkpoint_sha256",
                )
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_activation(path, config, "abc")
            payload["d10_result_sha256"] = "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(D11StrongBaselineError):
                validate_activation(path, config, "abc")

    def test_pbs_and_source_exclude_disallowed_server_and_dependencies(self) -> None:
        script = PBS_PATH.read_text(encoding="utf-8")
        source = SOURCE_PATH.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn('$AURORA_D9_CACHE:/cache:ro', script)
        self.assertIn("d11_result.json", script)
        self.assertNotIn("outer", script.lower())
        self.assertNotIn("import torch_geometric", source)
        self.assertNotIn("from torch_geometric", source)
        self.assertNotIn("import pytorch3d", source)
        self.assertNotIn("from pytorch3d", source)


if __name__ == "__main__":
    unittest.main()
