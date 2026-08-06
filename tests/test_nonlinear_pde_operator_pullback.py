import copy
import importlib.util
import math
import unittest
from pathlib import Path

from aurora.nonlinear_pde_decision import generate_boundary_split
from aurora.nonlinear_pde_operator_pullback import (
    PROPOSED_VARIANT,
    VARIANT_IDS,
    candidate_joint_mmd,
    load_operator_pullback_config,
    solution_mmd,
    train_operator_pullback_variants,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "configs"
    / "nonlinear_pde_n1_missing_operator_pullback_m0.json"
)


class OperatorPullbackContractTests(unittest.TestCase):
    def test_live_contract_is_missing_only_and_non_authorizing(self) -> None:
        n1, config, manifest = load_operator_pullback_config(CONFIG)
        self.assertEqual(
            tuple(item["id"] for item in config["objective_variants"]),
            VARIANT_IDS,
        )
        self.assertEqual(
            config["method_hypothesis"]["proposed_variant_id"],
            PROPOSED_VARIANT,
        )
        self.assertEqual(config["scope_lock"]["base_mask"], "missing")
        self.assertFalse(
            config["scope_lock"]["may_access_or_generate_n1_test"]
        )
        self.assertFalse(config["scope_lock"]["may_relabel_n1c"])
        self.assertFalse(
            config["scope_lock"]["may_authorize_n1d_or_irregular_3d"]
        )
        self.assertFalse(
            config["scope_lock"]["may_establish_method_novelty"]
        )
        self.assertTrue(
            config["mechanism_gate"][
                "failure_abandons_this_mechanism_without_local_weight_or_kernel_repair"
            ]
        )
        prior = {
            *n1["model_seeds"]["development_only"],
            *n1["model_seeds"]["confirmatory"],
        }
        self.assertTrue(prior.isdisjoint(config["model_seeds"]))
        self.assertEqual(len(manifest["seed_runs"]), 5)

    def test_cluster_wrapper_keeps_code_and_checkpoints_read_only(self) -> None:
        wrapper = (
            ROOT
            / "cluster"
            / "ssu_a6gpu_nonlinear_pde_n1_missing_operator_pullback_m0.pbs"
        )
        if not wrapper.exists():
            self.skipTest("PBS wrapper is added with the execution contract.")
        text = wrapper.read_text(encoding="utf-8")
        self.assertIn("$AURORA_PROJECT_ROOT:/workspace:ro", text)
        self.assertIn("$AURORA_CHECKPOINT_ROOT:/checkpoints:ro", text)
        self.assertIn("#PBS -J 0-2", text)
        self.assertIn("--require-cuda", text)


@unittest.skipUnless(importlib.util.find_spec("torch"), "torch is not installed")
class OperatorPullbackNumericalTests(unittest.TestCase):
    def setUp(self) -> None:
        import torch

        self.torch = torch
        self.device = torch.device("cpu")

    def test_joint_metric_detects_dependence_hidden_by_solution_marginal(self) -> None:
        torch = self.torch
        coordinate = torch.linspace(-2.0, 2.0, 64)[None, :, None]
        first_boundary = coordinate.expand(-1, -1, 8).clone()
        second_boundary = (-coordinate).expand(-1, -1, 8).clone()
        functional = torch.cat(
            (coordinate, coordinate.square(), coordinate.sin(), coordinate.cos()),
            dim=-1,
        )
        marginal = solution_mmd(
            functional, functional, scales=[0.5, 1.0, 2.0]
        )
        joint = candidate_joint_mmd(
            first_boundary,
            functional,
            second_boundary,
            functional,
            scales=[0.5, 1.0, 2.0],
        )
        self.assertLess(float(marginal.abs().max()), 1e-7)
        self.assertGreater(float(joint.min()), 1e-3)

    def test_tiny_variants_share_initialization_and_train(self) -> None:
        torch = self.torch
        from aurora.nonlinear_pde import solution_functionals

        n1, config, _ = load_operator_pullback_config(CONFIG)
        tiny = copy.deepcopy(config)
        tiny["optimization_lock"].update(
            {
                "maximum_steps": 2,
                "batch_size": 8,
                "validation_interval": 1,
                "early_stopping_patience": 3,
            }
        )

        class DummyOperator(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                axis = torch.linspace(0.0, 1.0, 33)
                xx, yy = torch.meshgrid(axis, axis, indexing="ij")
                self.register_buffer("xx", xx)
                self.register_buffer("yy", yy)

            def forward(self, context, boundary):
                return (
                    boundary[:, 0, None, None] * self.xx
                    + boundary[:, 1, None, None] * self.yy
                    + context[:, 0, None, None] * self.xx * self.yy
                )

        operator = DummyOperator()

        def make_split(contexts, conditions, context_seed, boundary_seed):
            split = generate_boundary_split(
                contexts=contexts,
                conditions=conditions,
                context_seed=context_seed,
                boundary_seed=boundary_seed,
                context_support=[-0.8, 0.8],
                maximum_radius=2.5,
                device=self.device,
            )
            expanded_context = (
                split["context"][:, None]
                .expand(-1, conditions, -1)
                .reshape(-1, 5)
            )
            flat_boundary = split["boundary"].reshape(-1, 8)
            with torch.no_grad():
                field = operator(expanded_context, flat_boundary)
                functional = solution_functionals(field, expanded_context)
            split["functionals"] = functional.reshape(
                contexts, conditions, 4
            )
            return split

        train = make_split(4, 2, 9101, 9201)
        selection = make_split(3, 2, 9102, 9202)
        models, standardization, history = train_operator_pullback_variants(
            n1_config=n1,
            config=tiny,
            train_split=train,
            selection_split=selection,
            operator=operator,
            seed=73081021,
        )
        self.assertEqual(set(models), set(VARIANT_IDS))
        self.assertTrue(history["paired_initialization"])
        self.assertTrue(history["paired_minibatch_indices"])
        self.assertTrue(history["paired_kernel_random_numbers"])
        self.assertEqual(set(standardization), {
            "boundary_location",
            "boundary_scale",
            "functional_location",
            "functional_scale",
            "functional_grid_minimum",
            "functional_grid_maximum",
        })
        for variant in VARIANT_IDS:
            record = history["models"][variant]["best_record"]
            self.assertTrue(math.isfinite(record["selection_objective"]))


if __name__ == "__main__":
    unittest.main()
