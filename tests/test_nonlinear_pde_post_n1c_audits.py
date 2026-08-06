import copy
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    generate_boundary_split,
)
from aurora.nonlinear_pde_decision_task_audit import (
    evaluate_true_decision_task,
    load_decision_task_audit_config,
)
from aurora.nonlinear_pde_density_objective import (
    VARIANT_IDS,
    evaluate_density_objective_variants,
    load_density_objective_audit_config,
    train_density_objective_variants,
)
from aurora.nonlinear_pde_evaluation import (
    radius_truncated_conditional_gmm_nll,
)
from scripts.aggregate_n1_post_n1c_audits import (
    aggregate_decision_task,
    aggregate_density,
)


ROOT = Path(__file__).resolve().parents[1]
DENSITY_CONFIG = (
    ROOT / "configs" / "nonlinear_pde_n1_density_objective_audit.json"
)
DECISION_CONFIG = (
    ROOT / "configs" / "nonlinear_pde_n1_decision_task_audit.json"
)


class PostN1cAuditContractTests(unittest.TestCase):
    def _write_candidate(
        self,
        source: Path,
        payload: dict,
        directory: str,
    ) -> Path:
        root = Path(directory)
        configs = root / "configs"
        results = root / "results"
        configs.mkdir()
        results.mkdir()
        for name in ("nonlinear_pde_n1.json", "nonlinear_pde_n0.json"):
            path = ROOT / "configs" / name
            (configs / name).write_bytes(path.read_bytes())
        result = ROOT / "results" / "nonlinear_pde_n1c_attribution_20260806.json"
        (results / result.name).write_bytes(result.read_bytes())
        candidate = configs / source.name
        candidate.write_text(json.dumps(payload), encoding="utf-8")
        return candidate

    def test_density_objective_audit_is_fresh_validation_only(self) -> None:
        n1, audit = load_density_objective_audit_config(DENSITY_CONFIG)
        self.assertEqual(tuple(item["id"] for item in audit["objective_variants"]),
                         VARIANT_IDS)
        self.assertEqual(len(audit["model_seeds"]), 5)
        self.assertFalse(audit["has_success_threshold"])
        self.assertFalse(audit["may_access_or_generate_n1_test"])
        self.assertFalse(audit["may_select_a_method"])
        prior = {
            *n1["model_seeds"]["development_only"],
            *n1["model_seeds"]["confirmatory"],
        }
        self.assertTrue(prior.isdisjoint(audit["model_seeds"]))

    def test_decision_task_audit_is_model_free_and_non_gating(self) -> None:
        _, _, audit = load_decision_task_audit_config(DECISION_CONFIG)
        self.assertFalse(audit["uses_learned_model_or_checkpoint"])
        self.assertFalse(audit["has_success_threshold"])
        self.assertFalse(audit["may_access_or_generate_n1_test"])
        self.assertFalse(audit["may_authorize_n1d_or_irregular_3d"])
        self.assertEqual(len(audit["monte_carlo"]["replicates"]), 2)

    def test_density_audit_rejects_a_post_hoc_threshold(self) -> None:
        payload = json.loads(DENSITY_CONFIG.read_text(encoding="utf-8"))
        payload["has_success_threshold"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = self._write_candidate(
                DENSITY_CONFIG, payload, directory
            )
            with self.assertRaisesRegex(
                NonlinearDecisionError, "cannot gate"
            ):
                load_density_objective_audit_config(candidate)

    def test_decision_audit_rejects_learned_checkpoint_use(self) -> None:
        payload = json.loads(DECISION_CONFIG.read_text(encoding="utf-8"))
        payload["uses_learned_model_or_checkpoint"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = self._write_candidate(
                DECISION_CONFIG, payload, directory
            )
            with self.assertRaisesRegex(
                NonlinearDecisionError, "cannot train"
            ):
                load_decision_task_audit_config(candidate)

    def test_pbs_wrappers_keep_code_read_only(self) -> None:
        density = (
            ROOT
            / "cluster"
            / "ssu_a6gpu_nonlinear_pde_n1_density_objective_audit.pbs"
        ).read_text(encoding="utf-8")
        decision = (
            ROOT
            / "cluster"
            / "ssu_a6gpu_nonlinear_pde_n1_decision_task_audit.pbs"
        ).read_text(encoding="utf-8")
        for wrapper in (density, decision):
            self.assertIn("$AURORA_PROJECT_ROOT:/workspace:ro", wrapper)
            self.assertIn('PYTHONPATH="/workspace/src:/workspace"', wrapper)
            self.assertIn("--require-cuda", wrapper)
        self.assertIn("#PBS -J 0-4", density)
        self.assertNotIn("AURORA_CHECKPOINT_ROOT", decision)
        contract = (
            ROOT / "cluster" / "ssu_a6gpu_contract_tests.pbs"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'experiment_pythonpath="/workspace/src:/workspace"', contract
        )

    def test_density_public_aggregate_requires_every_seed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                NonlinearDecisionError, "all five seed metrics"
            ):
                aggregate_density(
                    config_path=DENSITY_CONFIG,
                    input_root=Path(directory),
                    git_commit="f" * 40,
                )

    def test_task_public_aggregate_rejects_checkpoint_use(self) -> None:
        payload = {
            "schema_version": (
                "aurora.nonlinear_pde_n1_decision_task_audit.result.v1"
            ),
            "git_commit": "f" * 40,
            "test_contexts_generated": 0,
            "test_split_generated": False,
            "test_seed_accessed": False,
            "learned_models_loaded": 0,
            "learned_checkpoints_loaded": 1,
            "decision": {
                "has_success_threshold": False,
                "task_pass_fail_label_assigned": False,
                "method_or_checkpoint_selected": False,
                "n1d_or_irregular_3d_authorized": False,
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                NonlinearDecisionError, "model-free"
            ):
                aggregate_decision_task(
                    config_path=DECISION_CONFIG,
                    metrics_path=path,
                    git_commit="f" * 40,
                )


@unittest.skipUnless(importlib.util.find_spec("torch"), "torch is not installed")
class PostN1cAuditNumericalTests(unittest.TestCase):
    def setUp(self) -> None:
        import torch

        self.torch = torch
        self.device = torch.device("cpu")

    def _boundary_split(
        self,
        contexts: int,
        conditions: int,
        context_seed: int,
        boundary_seed: int,
    ) -> dict:
        return generate_boundary_split(
            contexts=contexts,
            conditions=conditions,
            context_seed=context_seed,
            boundary_seed=boundary_seed,
            context_support=[-0.8, 0.8],
            maximum_radius=2.5,
            device=self.device,
        )

    def test_radius_truncated_true_nll_is_finite_for_all_masks(self) -> None:
        split = self._boundary_split(3, 2, 101, 201)
        boundary = split["boundary"].reshape(-1, 8)
        for observed in ([], [0, 2], [0, 2, 5, 7]):
            conditions = split["boundary"].shape[1]
            weights = split["true_weights"][:, None].expand(
                -1, conditions, -1
            ).reshape(-1, 2)
            means = split["true_means"][:, None].expand(
                -1, conditions, -1, -1
            ).reshape(-1, 2, 8)
            covariance = split["true_covariances"][:, None].expand(
                -1, conditions, -1, -1, -1
            ).reshape(-1, 2, 8, 8)
            value = radius_truncated_conditional_gmm_nll(
                weights,
                means,
                covariance,
                boundary,
                observed,
                maximum_radius=2.5,
            )
            self.assertEqual(tuple(value.shape), (6,))
            self.assertTrue(self.torch.isfinite(value).all())

    def test_density_variants_train_from_paired_initial_state(self) -> None:
        n1, audit = load_density_objective_audit_config(DENSITY_CONFIG)
        tiny = copy.deepcopy(audit)
        tiny["optimization_lock"].update(
            {
                "maximum_steps": 2,
                "batch_size": 8,
                "validation_interval": 1,
                "early_stopping_patience": 3,
            }
        )
        train = self._boundary_split(4, 2, 301, 401)
        selection = self._boundary_split(3, 2, 302, 402)
        held_out = self._boundary_split(3, 2, 303, 403)
        models, history = train_density_objective_variants(
            n1_config=n1,
            audit_config=tiny,
            train_split=train,
            selection_split=selection,
            seed=73080621,
        )
        self.assertEqual(set(models), set(VARIANT_IDS))
        self.assertTrue(history["paired_initialization"])
        self.assertTrue(history["paired_minibatch_indices"])
        aggregate, per_context = evaluate_density_objective_variants(
            models=models,
            audit_split=held_out,
            audit_config=tiny,
        )
        self.assertEqual(set(aggregate), {"missing", "sparse_2", "partial_4"})
        for mask in aggregate.values():
            for model in VARIANT_IDS:
                self.assertTrue(math.isfinite(mask[model]["excess_over_true_law"]))
        self.assertEqual(set(per_context), set(aggregate))

    def test_true_decision_task_smoke_has_registered_estimands(self) -> None:
        _, _, audit = load_decision_task_audit_config(DECISION_CONFIG)
        tiny = copy.deepcopy(audit)
        tiny["monte_carlo"]["base_posterior_samples"] = 8
        for replicate in tiny["monte_carlo"]["replicates"]:
            replicate["outer_measurement_samples"] = 2
            replicate["inner_posterior_samples"] = 3
        tiny["functional_contract"]["action_grid_points"] = 9
        calibration_boundary = self._boundary_split(4, 2, 501, 601)
        context = calibration_boundary["context"][:, None].expand(-1, 2, -1)
        boundary = calibration_boundary["boundary"]
        calibration_boundary["functionals"] = self.torch.stack(
            (
                boundary.mean(dim=-1),
                boundary.square().mean(dim=-1),
                context[..., 0] + boundary[..., 0],
                context[..., 1] - boundary[..., 1],
            ),
            dim=-1,
        )
        calibration_boundary["solver"] = {
            "batches": 1,
            "all_converged": True,
            "maximum_normalized_residual": 0.0,
            "maximum_iterations": 1,
        }
        audit_split = self._boundary_split(2, 1, 502, 602)

        def solve_functionals(context, boundary):
            functional = self.torch.stack(
                (
                    boundary.mean(dim=-1),
                    boundary.square().mean(dim=-1),
                    context[:, 0] + boundary[:, 0],
                    context[:, 1] - boundary[:, 1],
                ),
                dim=-1,
            )
            return functional, {
                "batches": 1,
                "all_converged": True,
                "maximum_normalized_residual": 0.0,
                "maximum_iterations": 1,
            }

        aggregate, raw, solver = evaluate_true_decision_task(
            calibration_split=calibration_boundary,
            audit_split=audit_split,
            audit_config=tiny,
            solve_functionals=solve_functionals,
        )
        self.assertEqual(set(aggregate["masks"]), {"missing", "sparse_2"})
        self.assertFalse(
            aggregate["interpretation_boundary"][
                "uses_learned_model_or_checkpoint"
            ]
        )
        for mask in aggregate["masks"].values():
            self.assertIn("replicate_stability", mask)
            self.assertEqual(len(mask["replicates"]), 2)
        self.assertEqual(set(raw), {"missing", "sparse_2"})
        self.assertGreater(len(solver), 1)


if __name__ == "__main__":
    unittest.main()
