from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_official_graphunet_baseline import (
    Release730GraphUNetError,
    extended_case_metrics,
    load_config,
    objective_components,
    validate_activation,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_official_graphunet_baseline_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_official_graphunet_baseline_v1.pbs"
SOURCE = ROOT / "src" / "aurora" / "aneug_release_730_official_graphunet_baseline.py"


class Release730OfficialGraphUNetTests(unittest.TestCase):
    def test_config_is_direct_prior_raw_target_and_test_sealed(self):
        config = load_config(CONFIG)
        self.assertEqual(
            config["comparison_identity"]["label"],
            "released_graphunet_class_release730_protocol_adapter",
        )
        self.assertTrue(
            config["comparison_identity"]["unchanged_released_model_class_and_forward"]
        )
        self.assertFalse(config["comparison_identity"]["exact_end_to_end_reproduction"])
        self.assertEqual(config["split"]["train_cases"], 584)
        self.assertEqual(config["split"]["validation_cases"], 73)
        self.assertEqual(
            config["split"]["validation_loader_order_sha256"],
            "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        )
        self.assertFalse(config["split"]["read_test_fields"])
        self.assertFalse(config["target_and_metric"]["hard_tangent_projection"])
        self.assertIsNone(config["decision_rule"]["absolute_performance_threshold"])

    def test_test_read_tangent_projection_or_arbitrary_threshold_is_rejected(self):
        config = json.loads(CONFIG.read_text())
        mutations = (
            ("split", "read_test_fields", True),
            ("target_and_metric", "hard_tangent_projection", True),
            ("decision_rule", "absolute_performance_threshold", 0.4),
        )
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                mutated = copy.deepcopy(config)
                mutated[section][key] = value
                with self.assertRaises(Release730GraphUNetError):
                    validate_config(mutated)

    def test_objective_components_are_additive_across_microbatches(self):
        torch.manual_seed(3)
        reference = torch.randn(7, 9, 3)
        prediction = reference + 0.2 * torch.randn_like(reference)
        mean = torch.tensor([[[0.2, -0.1, 0.3]]])
        std = torch.tensor([[[2.0, 1.5, 0.8]]])
        whole = objective_components(
            prediction,
            reference,
            mean,
            std,
            physical_epsilon=1e-6,
            log_epsilon=1e-12,
        )
        parts = [torch.zeros(()), torch.zeros(())]
        for start in (0, 3, 6):
            value = objective_components(
                prediction[start : start + 3],
                reference[start : start + 3],
                mean,
                std,
                physical_epsilon=1e-6,
                log_epsilon=1e-12,
            )
            parts[0] += value[0]
            parts[1] += value[1]
        self.assertTrue(torch.allclose(whole[0], parts[0]))
        self.assertTrue(torch.allclose(whole[1], parts[1]))

    def test_extended_metrics_use_reference_only_peak_and_raw_normal_component(self):
        phase = torch.arange(80, dtype=torch.float64).reshape(-1, 1)
        reference = torch.ones((80, 4, 3), dtype=torch.float64)
        reference[..., 0] *= 1.0 + phase
        prediction = reference.clone()
        weights = torch.full((4,), 0.25, dtype=torch.float64)
        normals = torch.tensor([[0.0, 0.0, 1.0]] * 4, dtype=torch.float64)
        exact = extended_case_metrics(prediction, reference, weights, normals)
        for key, value in exact.items():
            if key == "osi_coverage":
                self.assertEqual(value, 1.0)
            else:
                self.assertTrue(math.isclose(value, 0.0, abs_tol=1e-12), key)
        shifted = prediction.clone()
        shifted[-1, :, 0] += 1.0
        changed = extended_case_metrics(shifted, reference, weights, normals)
        self.assertGreater(changed["peak_systolic_wss_relative_l2"], 0.0)

    def test_activation_binds_exact_source_split_and_scope(self):
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_official_graphunet_baseline_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "single_seed_validation_development",
            "read_test_or_extra": False,
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
            "official_commit": config["source"]["commit"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            activation["read_test_or_extra"] = True
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaises(Release730GraphUNetError):
                validate_activation(path, config, "abc")

    def test_pbs_uses_introai9_gpu_and_binds_no_test_path(self):
        script = PBS.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("ngpus=1", script)
        self.assertIn("$AURORA_OFFICIAL_ROOT:/official:ro", script)
        self.assertIn("$AURORA_PYG_TARGET:/pyg:ro", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("test_manifest", script)
        self.assertIn("hard_tangent_projection", source)
        self.assertNotIn("tangent_projection(", source)


if __name__ == "__main__":
    unittest.main()
