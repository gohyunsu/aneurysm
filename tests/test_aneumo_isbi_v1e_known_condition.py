import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v1e_known_condition import (
    AneumoV1eKnownConditionError,
    CONTROL,
    PRIMARY,
    SEEDS,
    VARIANTS,
    aggregate_tasks,
    apply_rotation,
    build_model,
    load_config,
    normalize_case,
    parameter_count,
    source_features,
    uniform_rotation,
    validate_config,
    CaseData,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v1e_known_condition_baseline.json"


class AneumoV1eKnownConditionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def _numpy(self):
        try:
            import numpy as np
        except ImportError as exc:
            raise unittest.SkipTest("numpy is unavailable") from exc
        return np

    def _torch(self):
        try:
            import torch
        except ImportError as exc:
            raise unittest.SkipTest("torch is unavailable") from exc
        return torch

    def _prepared_case(self):
        np = self._numpy()
        rng = np.random.default_rng(7)
        coordinates = rng.normal(size=(4096, 3)).astype(np.float32)
        velocity = rng.normal(size=(8, 4096, 3)).astype(np.float32)
        patches = {}
        for index, patch in enumerate(("inlet", "outlet", "wall")):
            points = rng.normal(size=(96 + index, 3)).astype(np.float32)
            normal = np.zeros(3, dtype=np.float32)
            if patch != "wall":
                normal[index] = 1.0
            patches[patch] = {
                "points": points,
                "normal": normal,
                "area": 1.0 + index,
            }
        return normalize_case(
            CaseData(
                case=1,
                split="train",
                coordinates=coordinates,
                velocity=velocity,
                patches=patches,
            )
        )

    def test_reference_contract_is_known_condition_only(self) -> None:
        self.assertEqual(self.config["task"]["condition"], "fully_observed_scalar_mass_flow")
        self.assertFalse(self.config["task"]["missing_or_partial_condition_evaluated"])
        self.assertFalse(self.config["access"]["test_geometry_or_field_read"])
        self.assertEqual(self.config["training"]["seeds"], SEEDS)
        self.assertEqual(self.config["training"]["variants"], VARIANTS)

    def test_pass_cannot_authorize_test_or_novelty(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["pass_authorizes"] = "run_v2_test"
        with self.assertRaisesRegex(AneumoV1eKnownConditionError, "authorize"):
            validate_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["access"]["test_geometry_or_field_read"] = True
        with self.assertRaisesRegex(AneumoV1eKnownConditionError, "access"):
            validate_config(candidate)

    def test_training_and_gate_thresholds_cannot_drift(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["training"]["steps"] = 12000
        with self.assertRaisesRegex(AneumoV1eKnownConditionError, "training"):
            validate_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["thresholds"][
            "maximum_worst_seed_validation_full_q_relative_l2"
        ] = 0.5
        with self.assertRaisesRegex(AneumoV1eKnownConditionError, "authorize"):
            validate_config(candidate)

    def test_token_budget_is_exact_and_boundary_is_the_only_difference(self) -> None:
        primary = source_features(self._prepared_case(), PRIMARY, 0.25)
        control = source_features(self._prepared_case(), CONTROL, 0.25)
        self.assertEqual(primary.shape, (320, 12))
        self.assertEqual(control.shape, (320, 12))
        self.assertEqual(int((primary[:, 4:7] != 0).any(axis=1).sum()), 192)
        self.assertEqual(int((control[:, 4:7] != 0).any(axis=1).sum()), 0)

    def test_rotation_is_proper_and_preserves_vector_norms(self) -> None:
        np = self._numpy()
        rng = np.random.default_rng(11)
        rotation = uniform_rotation(rng)
        source = source_features(self._prepared_case(), PRIMARY, -0.5)
        query = np.concatenate([source[:17, :3], np.zeros((17, 1), dtype=np.float32)], axis=1)
        target = rng.normal(size=(17, 3)).astype(np.float32)
        _, _, rotated = apply_rotation(source, query, target, rotation)
        self.assertAlmostEqual(float(np.linalg.det(rotation)), 1.0, places=5)
        self.assertTrue(
            np.allclose(
                np.linalg.norm(target, axis=1), np.linalg.norm(rotated, axis=1)
            )
        )

    def test_shared_model_parameterization_and_forward_shape(self) -> None:
        torch = self._torch()
        first = build_model(self.config)
        second = build_model(self.config)
        self.assertEqual(parameter_count(first), parameter_count(second))
        with torch.no_grad():
            output = first(torch.zeros(2, 320, 12), torch.zeros(2, 19, 4))
        self.assertEqual(tuple(output.shape), (2, 19, 3))
        first(torch.zeros(1, 320, 12), torch.zeros(1, 7, 4)).sum().backward()
        self.assertTrue(
            all(
                parameter.grad is not None and torch.isfinite(parameter.grad).all()
                for parameter in first.parameters()
            )
        )

    def test_aggregate_requires_absolute_and_relative_gate(self) -> None:
        config = copy.deepcopy(self.config)
        config["_config_sha256"] = hashlib.sha256(CONFIG.read_bytes()).hexdigest()
        commit = "v1e-test-commit"
        access = {
            "splits_read": ["train", "validation"],
            "pressure_channel_read": False,
            "missing_or_partial_condition_evaluated": False,
            "test_geometry_or_field_read": False,
            "test_metric_computed": False,
            "clinical_endpoint_evaluated": False,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for variant_index, variant in enumerate(VARIANTS):
                for seed_index, seed in enumerate(SEEDS):
                    task = root / f"{variant}_seed_{seed}"
                    task.mkdir()
                    primary = variant == PRIMARY
                    metrics = {
                        "schema_version": "aurora.aneumo_isbi_v1e_known_condition.task.v1",
                        "experiment_id": config["experiment_id"],
                        "variant": variant,
                        "seed": seed,
                        "git_commit": commit,
                        "config_sha256": config["_config_sha256"],
                        "selected_step": 400,
                        "parameter_count": 1000,
                        "source_token_count": 320,
                        "selection_score": 0.25,
                        "velocity_scale_m_s": 0.2,
                        "dependencies": {
                            "compact_cache_sha256": config["source"]["compact_cache_sha256"],
                            "geometry_cache_sha256": config["source"][
                                "v1d_private_geometry_cache_sha256"
                            ],
                            "v1d_result_sha256": config["source"]["v1d_result_sha256"],
                        },
                        "train": {
                            "full_q_relative_l2": 0.12 if primary else 0.20,
                            "paired_response_relative_l2": 0.30 if primary else 0.42,
                            "prediction_target_norm_ratio": 0.95,
                            "vector_cosine": 0.94,
                        },
                        "validation": {
                            "full_q_relative_l2": 0.20 if primary else 0.30,
                            "paired_response_relative_l2": 0.30 if primary else 0.40,
                            "prediction_target_norm_ratio": 0.95,
                            "vector_cosine": 0.94,
                        },
                        "access": access,
                        "checkpoint": {
                            "eligible": True,
                            "selected_on": "validation_only",
                            "sha256": "a" * 64,
                        },
                        "device": {
                            "type": "cuda:0",
                            "cuda_available": True,
                            "name": "test-gpu",
                            "torch": "test",
                        },
                    }
                    (task / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
                    (task / "pbs_status.json").write_text(
                        json.dumps(
                            {
                                "array_index": variant_index * len(SEEDS) + seed_index,
                                "exit_status": 0,
                                "metrics_created": True,
                                "seed": seed,
                                "state": "complete",
                                "variant": variant,
                            }
                        ),
                        encoding="utf-8",
                    )
            result = aggregate_tasks(
                config, tasks_root=root, output=root / "aggregate", git_commit=commit
            )
            bad_path = root / f"{PRIMARY}_seed_{SEEDS[0]}" / "metrics.json"
            bad = json.loads(bad_path.read_text(encoding="utf-8"))
            bad["validation"]["full_q_relative_l2"] = float("nan")
            bad_path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(AneumoV1eKnownConditionError, "provenance"):
                aggregate_tasks(
                    config, tasks_root=root, output=root / "bad", git_commit=commit
                )
        self.assertTrue(result["gate"]["all_checks_passed"])
        self.assertEqual(result["gate"]["passed_checks"], 9)


if __name__ == "__main__":
    unittest.main()
