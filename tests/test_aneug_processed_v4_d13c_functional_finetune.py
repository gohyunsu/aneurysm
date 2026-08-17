from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import torch
from torch import nn

from aurora.aneug_processed_v4_d13c_functional_finetune import (
    VARIANTS,
    alignment_terms,
    backward_case,
    evaluate,
    functional_names,
    load_config,
    normalized_objectives,
    train_wss_rms,
    validate_activation,
    validation_utility,
)
from aurora.aneug_processed_v4_d11_strong_baseline import GHDConditionedGPSUNet


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d13c_functional_finetune_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d13c_functional_finetune_v1.pbs"


class D13CFunctionalFinetuneTests(unittest.TestCase):
    def test_config_is_same_backbone_non_executable_and_threshold_free(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(tuple(config["objective"]["variants"]), VARIANTS)
        self.assertEqual(
            config["backbone"]["identity"],
            "exact_D11_selected_checkpoint_and_architecture",
        )
        self.assertIsNone(config["evaluation"]["absolute_performance_threshold"])
        self.assertFalse(config["authorization"]["execute_now"])
        self.assertFalse(config["authorization"]["outer_test"])
        self.assertFalse(config["bound_data"]["read_outer_or_auxiliary"])

    def test_variant_components_and_utilities_are_explicit(self) -> None:
        self.assertEqual(functional_names("field_only"), ())
        self.assertEqual(
            functional_names("statistics_scalarized"), ("mean_vector", "tawss")
        )
        self.assertEqual(functional_names("osi_scalarized"), ("osi",))
        self.assertEqual(
            functional_names("all_field_anchored"),
            ("mean_vector", "tawss", "osi"),
        )
        terms = {
            "field": torch.tensor(2.0),
            "mean_vector": torch.tensor(3.0),
            "tawss": torch.tensor(4.0),
            "osi": torch.tensor(5.0),
        }
        normalizers = {"field": 2.0, "mean_vector": 3.0, "tawss": 4.0, "osi": 5.0}
        field, functional, total = normalized_objectives(
            terms, normalizers, "all_scalarized"
        )
        torch.testing.assert_close(field, torch.tensor(1.0))
        torch.testing.assert_close(functional, torch.tensor(1.0))
        torch.testing.assert_close(total, torch.tensor(2.0))
        metrics = {
            "field_relative_l2": 2.0,
            "mean_vector_tawss_normalized_l2": 3.0,
            "tawss_normalized_absolute_error": 4.0,
            "osi_mae": 5.0,
        }
        self.assertEqual(validation_utility(metrics, normalizers, "field_only"), 1.0)
        self.assertEqual(
            validation_utility(metrics, normalizers, "all_field_anchored"), 2.0
        )

    def test_train_rms_uses_area_phase_vector_energy(self) -> None:
        first = {
            "wss": torch.tensor(
                [[[2.0, 0.0, 0.0]], [[2.0, 0.0, 0.0]]], dtype=torch.float64
            ),
            "vertex_weights": torch.ones(1, dtype=torch.float64),
        }
        second = {
            "wss": torch.tensor(
                [[[0.0, 2.0, 0.0]], [[0.0, 2.0, 0.0]]], dtype=torch.float64
            ),
            "vertex_weights": torch.ones(1, dtype=torch.float64),
        }
        self.assertAlmostEqual(train_wss_rms([first, second]), 2.0, places=12)
        invalid = {"wss": first["wss"], "vertex_weights": torch.zeros(1)}
        with self.assertRaisesRegex(RuntimeError, "train_values"):
            train_wss_rms([invalid])

    def test_scalarized_and_anchored_backward_reach_same_parameters(self) -> None:
        torch.manual_seed(43)
        model = nn.Linear(2, 2, bias=False).to(torch.float64)
        normalizers = {"field": 1.0, "mean_vector": 1.0, "tawss": 1.0, "osi": 1.0}

        def terms() -> dict[str, torch.Tensor]:
            output = model(torch.tensor([0.7, -0.4], dtype=torch.float64))
            return {
                "field": (output[0] - 1.0).square() + 0.1 * output[1].square(),
                "mean_vector": (output[0] + 1.0).square(),
                "tawss": (output[1] - 0.5).square(),
                "osi": (output[0] + output[1]).square(),
            }

        scalar = backward_case(
            model, terms(), normalizers, "all_scalarized", 1, 1.0
        )
        self.assertGreater(float(scalar["scalarized_value"]), 0.0)
        self.assertFalse(bool(scalar["gradient_conflict_measured"]))
        scalar_gradient = model.weight.grad.detach().clone()
        self.assertTrue(bool(torch.isfinite(scalar_gradient).all().item()))

        model.zero_grad(set_to_none=True)
        anchored = backward_case(
            model, terms(), normalizers, "all_field_anchored", 1, 1.0
        )
        self.assertTrue(bool(torch.isfinite(model.weight.grad).all().item()))
        self.assertTrue(bool(anchored["gradient_conflict_measured"]))
        self.assertFalse(torch.equal(model.weight.grad, scalar_gradient))
        self.assertGreaterEqual(float(anchored["gradient_cosine_before"]), -1.000001)
        self.assertLessEqual(float(anchored["gradient_cosine_before"]), 1.000001)

    def test_small_exact_backbone_supports_anchored_full_cycle_backward(self) -> None:
        def ring_edges(nodes: int) -> torch.Tensor:
            source = torch.arange(nodes, dtype=torch.int64)
            target = torch.roll(source, shifts=-1)
            return torch.stack((source, target))

        topology = {
            "edge0": ring_edges(8),
            "edge1": ring_edges(4),
            "edge2": ring_edges(2),
            "idx1": torch.tensor([0, 2, 4, 6], dtype=torch.int64),
            "idx2": torch.tensor([0, 2], dtype=torch.int64),
            "parent1": torch.tensor([0, 0, 1, 1, 2, 2, 3, 3], dtype=torch.int64),
            "parent2": torch.tensor([0, 0, 1, 1], dtype=torch.int64),
        }
        torch.manual_seed(47)
        model = GHDConditionedGPSUNet(topology, width=32, heads=4)
        normals = torch.zeros(8, 3)
        normals[:, 2] = 1.0
        reference = torch.randn(80, 8, 3)
        reference[..., 2] = 0.0
        case = {
            "coordinates": torch.randn(8, 3),
            "normals": normals,
            "vertex_weights": torch.full((8,), 1.0 / 8.0),
            "ghd": torch.randn(432),
            "wss": reference,
        }
        config = load_config(CONFIG)
        initial = evaluate(
            model,
            [case],
            config,
            1e-4,
            None,
            "all_field_anchored",
            torch.device("cpu"),
        )
        self.assertIsNone(initial["variant_validation_utility"])
        self.assertEqual(
            set(initial["aggregate_alignment_terms"]),
            {"field", "mean_vector", "tawss", "osi"},
        )
        prediction = model(case)["field"]
        terms = alignment_terms(prediction, case, config, 1e-4)
        normalizers = {name: 1.0 for name in ("field", "mean_vector", "tawss", "osi")}
        diagnostic = backward_case(
            model,
            terms,
            normalizers,
            "all_field_anchored",
            1,
            1.0,
        )
        gradients = [parameter.grad for parameter in model.parameters()]
        self.assertTrue(all(gradient is not None for gradient in gradients))
        self.assertTrue(all(torch.isfinite(gradient).all() for gradient in gradients))
        self.assertGreater(float(diagnostic["scalarized_value"]), 0.0)

    def test_activation_binds_one_variant_and_d12_terminal_record(self) -> None:
        config = load_config(CONFIG)
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d13c.private_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D13C_functional_finetune_validation",
            "authorized_variant": "field_only",
            "d12_terminal_record_sha256": "123",
            "outer_or_auxiliary_access": False,
            "cache_manifest_sha256": config["bound_data"]["cache_manifest_sha256"],
            "d11_checkpoint_sha256": config["predecessors"]["d11_checkpoint_sha256"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_activation(path, config, "abc", "field_only")
            with self.assertRaisesRegex(RuntimeError, "activation_variant"):
                validate_activation(path, config, "abc", "all_scalarized")
            payload["d12_terminal_record_sha256"] = ""
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "d12_terminal_record"):
                validate_activation(path, config, "abc", "field_only")

    def test_pbs_is_scoped_to_one_variant_and_private_inputs(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("AURORA_D13C_VARIANT", script)
        self.assertIn("AURORA_D11_CHECKPOINT", script)
        self.assertIn("AURORA_D13C_ACTIVATION", script)
        self.assertIn("--variant \"$AURORA_D13C_VARIANT\"", script)
        self.assertIn("all_field_anchored)", script)
        self.assertNotIn("junjinyong", script)


if __name__ == "__main__":
    unittest.main()
