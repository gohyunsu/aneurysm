import json
import math
import unittest
from pathlib import Path

import torch
from torch import nn

from aurora.cycle_response_residual import (
    CycleResponseResidualDecoder,
    CycleResponseResidualError,
    GHDConditionedCycleResponseResidual,
    validate_config,
    weighted_global_amplitude,
)


ROOT = Path(__file__).resolve().parents[1]


def synthetic_payload(phases: int = 4, nodes: int = 5, rank: int = 3):
    generator = torch.Generator().manual_seed(19)
    dimension = phases * nodes * 3
    matrix = torch.randn(dimension, rank, generator=generator, dtype=torch.float64)
    basis = torch.linalg.qr(matrix, mode="reduced").Q.T.to(torch.float32)
    return {
        "schema_version": "aurora.aneug_processed_v4_d13a.private_basis.v1",
        "phases": phases,
        "nodes": nodes,
        "mean": torch.randn(dimension, generator=generator),
        "basis": basis,
        "reference_weights": torch.full((nodes,), 1.0 / nodes),
        "train_scales": torch.tensor([0.8, 1.0, 1.25]),
    }


def normals(nodes: int):
    value = torch.randn(nodes, 3, generator=torch.Generator().manual_seed(23))
    return value / torch.linalg.vector_norm(value, dim=-1, keepdim=True)


class DummyBackbone(nn.Module):
    def __init__(self, phases: int, nodes: int):
        super().__init__()
        self.field = nn.Parameter(torch.randn(phases, nodes, 3) * 0.01)

    def forward(self, case):
        return {"field": self.field}


class CycleResponseResidualTests(unittest.TestCase):
    def test_config_has_no_threshold_or_execution_authority(self):
        config = json.loads(
            (ROOT / "configs/aneug_cycle_response_residual_prototype_v1.json").read_text()
        )
        validate_config(config)
        self.assertIsNone(config["evidence_boundary"]["absolute_performance_threshold"])
        self.assertFalse(config["runtime_scope"]["execute_now"])

    def test_response_only_is_tangent_and_preserves_positive_amplitude(self):
        payload = synthetic_payload()
        decoder = CycleResponseResidualDecoder(payload, rank=3)
        normal = normals(5)
        output = decoder(
            torch.tensor([0.2, -0.1, 0.05]),
            torch.tensor([0.3]),
            torch.randn(4, 5, 3),
            torch.tensor([9.0]),
            normal,
            response_only=True,
        )
        normal_component = torch.sum(output["field"] * normal.unsqueeze(0), dim=-1)
        self.assertLess(float(normal_component.abs().max()), 2e-5)
        self.assertEqual(float(output["residual_gate"]), 0.0)
        self.assertGreater(float(output["amplitude"]), 0.0)
        self.assertAlmostEqual(
            weighted_global_amplitude(output["global_field"], decoder.reference_weights),
            float(output["amplitude"]),
            places=5,
        )

    def test_residual_gate_and_leakage_are_finite(self):
        payload = synthetic_payload()
        decoder = CycleResponseResidualDecoder(payload, rank=3)
        normal = normals(5)
        raw = torch.randn(4, 5, 3, requires_grad=True)
        output = decoder(
            torch.zeros(3), torch.zeros(1), raw, torch.zeros(1), normal
        )
        self.assertAlmostEqual(float(output["residual_gate"]), 0.5, places=6)
        self.assertTrue(torch.isfinite(output["residual_basis_leakage"]))
        self.assertGreaterEqual(float(output["residual_basis_leakage"]), 0.0)
        loss = output["field"].square().mean() + output["residual_basis_leakage"]
        loss.backward()
        self.assertIsNotNone(raw.grad)
        self.assertTrue(torch.isfinite(raw.grad).all())

    def test_common_rotation_equivariance(self):
        payload = synthetic_payload()
        decoder = CycleResponseResidualDecoder(payload, rank=3)
        normal = normals(5)
        raw = torch.randn(4, 5, 3)
        coefficients = torch.tensor([0.1, -0.2, 0.3])
        angle = 0.37
        rotation = torch.tensor(
            [
                [math.cos(angle), -math.sin(angle), 0.0],
                [math.sin(angle), math.cos(angle), 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=torch.float32,
        )
        original = decoder(
            coefficients, torch.tensor([0.1]), raw, torch.tensor([-0.4]), normal
        )["field"]
        rotated_payload = dict(payload)
        rotated_payload["mean"] = (
            payload["mean"].reshape(4, 5, 3) @ rotation.T
        ).reshape(-1)
        rotated_payload["basis"] = (
            payload["basis"].reshape(3, 4, 5, 3) @ rotation.T
        ).reshape(3, -1)
        rotated_decoder = CycleResponseResidualDecoder(rotated_payload, rank=3)
        rotated = rotated_decoder(
            coefficients,
            torch.tensor([0.1]),
            raw @ rotation.T,
            torch.tensor([-0.4]),
            normal @ rotation.T,
        )["field"]
        torch.testing.assert_close(rotated, original @ rotation.T, atol=2e-5, rtol=2e-5)

    def test_wrapper_routes_gradients_to_response_and_local_branches(self):
        payload = synthetic_payload()
        backbone = DummyBackbone(4, 5)
        model = GHDConditionedCycleResponseResidual(
            backbone, payload, rank=3, width=16
        )
        case = {"ghd": torch.randn(432), "normals": normals(5)}
        output = model(case)
        loss = output["field"].square().mean() + output["residual_basis_leakage"]
        loss.backward()
        self.assertTrue(torch.isfinite(backbone.field.grad).all())
        head_grads = [parameter.grad for parameter in model.response_head.parameters()]
        self.assertTrue(all(gradient is not None for gradient in head_grads))
        self.assertTrue(all(torch.isfinite(gradient).all() for gradient in head_grads))

    def test_rejects_nonorthonormal_basis(self):
        payload = synthetic_payload()
        payload["basis"][1] = payload["basis"][0]
        with self.assertRaisesRegex(CycleResponseResidualError, "orthonormal_basis"):
            CycleResponseResidualDecoder(payload, rank=3)


if __name__ == "__main__":
    unittest.main()
