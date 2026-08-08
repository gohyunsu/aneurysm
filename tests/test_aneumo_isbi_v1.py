import copy
import json
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v1 import (
    AneumoISBIV1Error,
    build_model,
    evaluate_family_ensemble,
    evaluate_same_case_response_oracle,
    farthest_point_indices,
    knn_indices,
    load_config,
    select_registered_family,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v1.json"
PBS_V1 = ROOT / "cluster" / "pbs_aneumo_isbi_v1.pbs"
PBS_V1_AGGREGATE = ROOT / "cluster" / "pbs_aneumo_isbi_v1_aggregate.pbs"


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

    def test_ensemble_estimand_cannot_be_changed(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["models"]["deep_ensemble"]["missing_predictive_components"] = 8
        with self.assertRaisesRegex(AneumoISBIV1Error, "3x8 ensemble"):
            validate_config(payload)

    def test_response_oracle_cannot_enter_selection(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["controls"]["response_only_oracle"][
            "eligible_for_model_selection_or_gate"
        ] = True
        with self.assertRaisesRegex(AneumoISBIV1Error, "response-only"):
            validate_config(payload)

    def test_selector_is_lexicographic_and_uses_per_seed_metrics(self) -> None:
        config = load_config(CONFIG)
        results = []
        response_by_family = {
            "q_pointnet": 0.30,
            "knn_mgn": 0.20,
            "deltaphi_graph": 0.20,
            "anchor_token_equivariant": 0.25,
        }
        full_by_family = {
            "q_pointnet": 0.10,
            "knn_mgn": 0.12,
            "deltaphi_graph": 0.11,
            "anchor_token_equivariant": 0.08,
        }
        for family_index, family in enumerate(config["models"]["families"]):
            for seed in config["training"]["seeds"]:
                results.append(
                    {
                        "family": family,
                        "seed": seed,
                        "parameter_count": 400_000 + family_index,
                        "metrics": {
                            "response_relative_l2": response_by_family[family],
                            "full_q_relative_l2": full_by_family[family],
                            "missing_field_energy_score_m_s": 0.01,
                        },
                        "condition_zeroing_worsens_full_q_error": True,
                    }
                )
        selection = select_registered_family(config, results)
        self.assertEqual(selection["selected_family"], "deltaphi_graph")
        self.assertFalse(selection["uses_ensemble_metrics"])
        self.assertFalse(selection["uses_response_oracle"])

    def test_selector_rejects_incomplete_factorial(self) -> None:
        config = load_config(CONFIG)
        with self.assertRaisesRegex(AneumoISBIV1Error, "exact 4x3"):
            select_registered_family(config, [])

    def test_pbs_wrapper_preserves_pre_metric_failures(self) -> None:
        script = PBS_V1.read_text(encoding="utf-8")
        self.assertIn('trap aurora_write_pbs_status EXIT', script)
        self.assertIn('tee "$task_output/pbs.log"', script)
        self.assertIn('"learned_metrics_created":%s', script)

        aggregate_script = PBS_V1_AGGREGATE.read_text(encoding="utf-8")
        self.assertIn(
            'trap aurora_write_aggregate_pbs_status EXIT', aggregate_script
        )
        self.assertIn(
            'tee "$AURORA_AGGREGATE_OUTPUT/pbs.log"', aggregate_script
        )
        self.assertIn('"aggregate_created":%s', aggregate_script)
        self.assertIn("AURORA_TASK_GIT_COMMIT", aggregate_script)
        self.assertIn("AURORA_AGGREGATE_GIT_COMMIT", aggregate_script)


class AneumoISBIV1ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import h5py  # noqa: F401
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

    def test_three_seed_ensemble_has_twenty_four_missing_components(self) -> None:
        torch = self.torch
        target = torch.randn(8, 20, 3)
        prepared = {
            11: {
                "base_family": 7,
                "velocity": target.numpy(),
            }
        }
        predictions = {
            seed: {11: target + 0.001 * index}
            for index, seed in enumerate(self.config["training"]["seeds"])
        }
        metrics = evaluate_family_ensemble(self.config, prepared, predictions)
        self.assertEqual(metrics["ensemble_members"], 3)
        self.assertEqual(metrics["missing_predictive_components"], 24)
        self.assertFalse(metrics["eligible_for_selector"])
        self.assertFalse(metrics["supports_uncertainty_separation_claim"])

    def test_same_case_oracle_is_response_only(self) -> None:
        import numpy as np

        torch = self.torch
        registered_flows = np.asarray(
            self.config["task"]["condition_values"], dtype=np.float64
        )
        cache_flows = registered_flows.astype(np.float32)
        anchor = self.config["controls"]["response_only_oracle"][
            "anchor_mass_flow_kg_s"
        ]
        power = self.config["controls"]["response_only_oracle"]["power"]
        base = torch.randn(20, 3)
        target = torch.stack(
            [base * float((flow / anchor) ** power) for flow in registered_flows],
            dim=0,
        )
        prepared = {11: {"base_family": 7, "velocity": target.numpy()}}
        metrics = evaluate_same_case_response_oracle(
            self.config, prepared, cache_flows
        )
        self.assertLess(metrics["validation_response_relative_l2"], 1e-6)
        self.assertFalse(metrics["eligible_for_model_selection_or_gate"])
        self.assertNotIn("full_q_relative_l2", metrics)

    def test_cuda_bookkeeping_uses_current_device_api(self) -> None:
        source = (ROOT / "src" / "aurora" / "aneumo_isbi_v1.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("torch.cuda.set_device(0)", source)
        self.assertIn("torch.cuda.reset_peak_memory_stats()", source)
        self.assertIn("torch.cuda.max_memory_allocated()", source)
        self.assertIn("torch.cuda.synchronize()", source)
        self.assertNotIn("torch.cuda.reset_peak_memory_stats(device)", source)
        self.assertNotIn("torch.cuda.max_memory_allocated(device)", source)
        self.assertNotIn("torch.cuda.synchronize(device)", source)


if __name__ == "__main__":
    unittest.main()
