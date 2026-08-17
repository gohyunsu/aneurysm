import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_processed_v4_d13a_response_oracle import (
    fit_response_basis,
    load_config,
    oracle_reconstruction,
    reference_vertex_weights,
    validate_activation,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d13a_response_oracle_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d13a_response_oracle_v1.pbs"


def synthetic_cases(count: int = 6) -> list[dict[str, torch.Tensor]]:
    generator = torch.Generator().manual_seed(19)
    normals = torch.zeros(5, 3)
    normals[:, 2] = 1.0
    cases = []
    for index in range(count):
        planar = torch.randn(4, 5, 2, generator=generator)
        field = torch.cat((planar, torch.zeros(4, 5, 1)), dim=-1) * (1.0 + index)
        weights = torch.rand(5, generator=generator) + 0.2
        weights = weights / weights.sum()
        cases.append(
            {
                "wss": field,
                "normals": normals.clone(),
                "vertex_weights": weights,
            }
        )
    return cases


class D13AResponseOracleTests(unittest.TestCase):
    def test_config_is_non_executable_oracle_without_threshold(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["representation"]["rank_grid"], [0, 16, 32, 64, 128, 256])
        self.assertEqual(config["representation"]["amplitude"], "oracle_true_validation_rms")
        self.assertIsNone(config["evaluation"]["absolute_performance_threshold"])
        self.assertFalse(config["authorization"]["execute_now"])
        self.assertFalse(config["authorization"]["rank_selection"])
        self.assertFalse(config["bound_data"]["read_outer_or_auxiliary"])

    def test_train_basis_reconstructs_full_rank_synthetic_cycle(self) -> None:
        cases = synthetic_cases()
        weights = reference_vertex_weights(cases)
        self.assertAlmostEqual(float(weights.sum().item()), 1.0, places=6)
        fitted = fit_response_basis(cases, maximum_rank=5, device=torch.device("cpu"))
        prediction, error = oracle_reconstruction(
            cases[0], fitted, rank=5, device=torch.device("cpu")
        )
        self.assertLess(error, 1e-4)
        self.assertTrue(torch.allclose(prediction[..., 2], torch.zeros_like(prediction[..., 2])))
        self.assertLess(float(fitted["orthogonality_error"].item()), 2e-3)

    def test_activation_requires_d12_terminal_record_and_sealed_scope(self) -> None:
        config = load_config(CONFIG)
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d13a.private_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D13A_response_oracle_validation",
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

    def test_pbs_is_introai9_only_and_fail_closed(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("AURORA_D13A_ACTIVATION", script)
        self.assertIn("--basis /output/d13a_basis.pt", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("outer", script.lower())


if __name__ == "__main__":
    unittest.main()
