import copy
import json
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v1 import (
    AneumoISBIV1Error,
    build_model,
    farthest_point_indices,
    knn_indices,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v1.json"


class AneumoISBIV1ContractTests(unittest.TestCase):
    def test_reference_contract_is_valid(self) -> None:
        payload = load_config(CONFIG)
        self.assertFalse(payload["authorization"]["outer_test"])

    def test_test_field_access_is_rejected(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["access"]["read_field_splits"].append("test")
        with self.assertRaisesRegex(AneumoISBIV1Error, "test fields"):
            validate_config(payload)

    def test_candidate_cannot_be_declared_novel(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["models"]["candidate_is_method_novelty"] = True
        with self.assertRaisesRegex(AneumoISBIV1Error, "not method novelty"):
            validate_config(payload)

    def test_m0_dependency_cannot_be_removed(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["authorization"]["measurement_solution_objective_requires_positive_m0"] = False
        with self.assertRaisesRegex(AneumoISBIV1Error, "blocked before M0"):
            validate_config(payload)


class AneumoISBIV1ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import numpy  # noqa: F401
            import torch
        except ImportError as exc:
            raise unittest.SkipTest("numpy/torch are unavailable") from exc
        cls.torch = torch
        cls.config = load_config(CONFIG)

    def test_knn_has_no_self_edges(self) -> None:
        torch = self.torch
        coordinates = torch.randn(24, 3)
        neighbors = knn_indices(coordinates, 4, chunk=7)
        self.assertEqual(tuple(neighbors.shape), (24, 4))
        rows = torch.arange(24)[:, None]
        self.assertFalse(bool((neighbors == rows).any().item()))

    def test_farthest_anchors_are_unique(self) -> None:
        torch = self.torch
        coordinates = torch.randn(2, 32, 3)
        anchors = farthest_point_indices(coordinates, 8)
        self.assertEqual(tuple(anchors.shape), (2, 8))
        for row in anchors:
            self.assertEqual(len(set(row.tolist())), 8)

    def test_registered_models_have_vector_output(self) -> None:
        torch = self.torch
        config = copy.deepcopy(self.config)
        config["models"]["hidden_dim"] = 32
        config["models"]["message_passing_layers"] = 2
        config["models"]["token_blocks"] = 1
        config["models"]["attention_heads"] = 4
        config["models"]["parameter_match_residual_blocks"] = {
            family: 1 for family in config["models"]["families"]
        }
        config["representation"]["anchor_count"] = 4
        coordinates = torch.randn(2, 24, 3)
        neighbors = torch.stack([knn_indices(item, 4) for item in coordinates])
        condition = torch.tensor([[-0.5], [0.75]])
        for family in config["models"]["families"]:
            with self.subTest(family=family):
                model = build_model(config, family).eval()
                output = model(coordinates, condition, neighbors)
                self.assertEqual(tuple(output.shape), (2, 24, 3))
                self.assertTrue(bool(torch.isfinite(output).all().item()))

    def test_anchor_token_model_is_rotation_equivariant(self) -> None:
        torch = self.torch
        config = copy.deepcopy(self.config)
        config["models"]["hidden_dim"] = 32
        config["models"]["message_passing_layers"] = 2
        config["models"]["token_blocks"] = 1
        config["models"]["attention_heads"] = 4
        config["models"]["parameter_match_residual_blocks"][
            "anchor_token_equivariant"
        ] = 0
        config["representation"]["anchor_count"] = 4
        torch.manual_seed(17)
        coordinates = torch.randn(1, 28, 3)
        matrix, _ = torch.linalg.qr(torch.randn(3, 3))
        if torch.linalg.det(matrix) < 0:
            matrix[:, 0] *= -1
        rotated = coordinates @ matrix
        neighbors = knn_indices(coordinates[0], 5)[None]
        rotated_neighbors = knn_indices(rotated[0], 5)[None]
        condition = torch.tensor([[0.25]])
        model = build_model(config, "anchor_token_equivariant").eval()
        with torch.no_grad():
            expected = model(coordinates, condition, neighbors) @ matrix
            actual = model(rotated, condition, rotated_neighbors)
        error = torch.max(torch.abs(actual - expected)).item()
        self.assertLess(error, 2e-4)

    def test_registered_parameter_budgets_are_matched(self) -> None:
        counts = []
        for family in self.config["models"]["families"]:
            model = build_model(self.config, family)
            counts.append(sum(parameter.numel() for parameter in model.parameters()))
        relative_range = (max(counts) - min(counts)) / max(counts)
        self.assertLessEqual(
            relative_range,
            float(self.config["models"]["parameter_match_relative_tolerance"]),
            msg=f"parameter counts are not matched: {counts}",
        )


if __name__ == "__main__":
    unittest.main()
