from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from aurora.aneug_release_730_train_representation_attribution import (
    TrainRepresentationAttributionError,
    aggregate_metrics,
    cyclic_case_metrics,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "configs"
    / "aneug_release_730_train_representation_attribution_v1.json"
)


class TrainRepresentationAttributionContractTests(unittest.TestCase):
    def test_config_is_train_only_cpu_and_not_an_automatic_gate(self):
        config = load_config(CONFIG)
        self.assertEqual(config["split"]["train_cases"], 584)
        self.assertEqual(config["read_scope"]["allowed_field_partition"], "train_only")
        self.assertFalse(config["read_scope"]["read_validation_field_values"])
        self.assertFalse(config["read_scope"]["read_test_field_values"])
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertFalse(config["attribution"]["automatic_architecture_selection"])

    def test_gpu_sealed_read_or_automatic_selection_is_rejected(self):
        config = json.loads(CONFIG.read_text())
        mutations = (
            ("execution", "ngpus", 1),
            ("read_scope", "read_validation_field_values", True),
            ("read_scope", "read_test_field_values", True),
            ("attribution", "automatic_architecture_selection", True),
        )
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                mutated = copy.deepcopy(config)
                mutated[section][key] = value
                with self.assertRaises(TrainRepresentationAttributionError):
                    validate_config(mutated)

    def test_public_aggregate_has_no_case_ids_or_winner(self):
        config = load_config(CONFIG)
        template = {
            "response_rms": 1.0,
            "boundary_jump_absolute": 0.1,
            "boundary_jump_relative": 0.1,
            "interior_jump_relative_median": 0.1,
            "interior_jump_relative_q95": 0.2,
            "interior_jump_relative_max": 0.3,
            "boundary_to_interior_median_ratio": 1.0,
            "boundary_transition_percentile": 0.5,
            "maximum_transition_start_phase": 79,
            "stored_normal_norm_min": 1.0,
            "stored_normal_norm_q01": 1.0,
            "stored_normal_norm_q05": 1.0,
            "stored_normal_norm_median": 1.0,
            "stored_mesh_normal_abs_cosine_q05": 1.0,
            "stored_wss_normal_ratio_median": 0.0,
            "stored_wss_normal_ratio_q95": 0.0,
            "mesh_wss_normal_ratio_median": 0.0,
            "mesh_wss_normal_ratio_q95": 0.0,
            "stored_normal_fraction_below_0.001": 0.0,
            "stored_normal_fraction_below_0.01": 0.0,
            "stored_normal_fraction_below_0.1": 0.0,
            "stored_normal_fraction_below_0.5": 0.0,
        }
        cases = [
            {"case_id": f"private_case_{index}", **template}
            for index in range(584)
        ]
        public, private = aggregate_metrics(
            config, cases, [case["case_id"] for case in cases]
        )
        self.assertFalse(public["case_ids_public"])
        self.assertIsNone(public["scientific_performance_verdict"])
        self.assertFalse(public["automatic_architecture_selection"])
        self.assertNotIn("private_case_0", json.dumps(public, sort_keys=True))
        self.assertEqual(len(private["per_case"]), 584)


class TrainRepresentationAttributionKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import torch
        except ImportError as error:  # pragma: no cover - optional local dependency
            raise unittest.SkipTest(str(error)) from error
        cls.torch = torch

    def _geometry(self):
        torch = self.torch
        coordinates = torch.tensor(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            dtype=torch.float64,
        )
        normals = torch.tensor(
            [[0.0, 0.0, 1.0], [0.0, 0.0, 0.5], [0.0, 0.0, 0.0001]],
            dtype=torch.float64,
        )
        faces = torch.tensor([[0, 1, 2]], dtype=torch.int64)
        return coordinates, normals, faces

    def _metrics(self, wss):
        coordinates, normals, faces = self._geometry()
        return cyclic_case_metrics(
            wss,
            coordinates,
            normals,
            faces,
            self.torch,
            normal_epsilon=1e-6,
            wss_support_fraction=0.01,
            normal_levels=[0.001, 0.01, 0.1, 0.5],
        )

    def test_corrupt_final_phase_is_attributed_to_cycle_boundary(self):
        torch = self.torch
        phase = torch.arange(80, dtype=torch.float64) * (2.0 * torch.pi / 80.0)
        base = torch.stack(
            (torch.cos(phase), torch.sin(phase), torch.zeros_like(phase)), dim=-1
        )
        smooth = base[:, None, :].repeat(1, 3, 1)
        corrupted = smooth.clone()
        corrupted[-1] = torch.tensor([[-5.0, 0.0, 0.0]]).repeat(3, 1)
        smooth_result = self._metrics(smooth)
        corrupt_result = self._metrics(corrupted)
        self.assertLess(smooth_result["boundary_to_interior_median_ratio"], 1.1)
        self.assertGreater(corrupt_result["boundary_to_interior_median_ratio"], 10.0)
        self.assertEqual(corrupt_result["maximum_transition_start_phase"], 79)

    def test_normal_support_and_tangent_ratios_are_finite(self):
        torch = self.torch
        wss = torch.ones((80, 3, 3), dtype=torch.float64)
        wss[..., 2] = 0.0
        result = self._metrics(wss)
        self.assertEqual(result["mesh_wss_normal_ratio_median"], 0.0)
        self.assertGreater(result["stored_normal_fraction_below_0.001"], 0.0)
        self.assertEqual(result["stored_mesh_normal_abs_cosine_q05"], 1.0)


class TrainRepresentationAttributionOutcomeTests(unittest.TestCase):
    def test_r1_public_result_is_exact_train_only_and_nonselecting(self):
        path = (
            ROOT
            / "results"
            / "aneug_release_730_train_representation_attribution_r1_20260818.json"
        )
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            "a44eee330250fb4faee024f21a58f6ff0662cb4a4b3d21c160a17a6176c53b85",
        )
        result = json.loads(path.read_text())
        self.assertEqual(result["status"], "complete_descriptive")
        self.assertEqual(result["train_case_count"], 584)
        self.assertEqual(result["validation_field_case_count_read"], 0)
        self.assertEqual(result["test_field_case_count_read"], 0)
        self.assertEqual(result["processed_only_extra_field_case_count_read"], 0)
        self.assertEqual(
            result["boundary_to_interior_ratio_counts"],
            {"at_least_10": 6, "at_least_2": 6, "at_least_5": 6},
        )
        self.assertEqual(result["boundary_is_largest_transition_case_count"], 5)
        self.assertFalse(result["case_ids_public"])
        self.assertFalse(result["automatic_architecture_selection"])
        self.assertIsNone(result["scientific_performance_verdict"])


if __name__ == "__main__":
    unittest.main()
