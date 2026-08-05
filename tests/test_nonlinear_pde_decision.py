import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    build_deltaphi_residual_operator,
    build_direct_probabilistic_operator,
    build_independent_mask_density,
    build_joint_density,
    build_lano_completion,
    build_mask_conditional_density,
    build_pod_probabilistic_operator,
    build_solution_operator,
    gmm_nll,
    load_config,
    load_n1b_config,
    load_n1c_config,
    load_n1c_attribution_config,
    load_optimization_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "nonlinear_pde_n1.json"
OPTIMIZATION_CONFIG = (
    ROOT / "configs" / "nonlinear_pde_n1_optimization_attribution.json"
)
N1B_CONFIG = ROOT / "configs" / "nonlinear_pde_n1b.json"
N1C_CONFIG = ROOT / "configs" / "nonlinear_pde_n1c.json"
N1C_ATTRIBUTION_CONFIG = (
    ROOT / "configs" / "nonlinear_pde_n1c_attribution.json"
)


class NonlinearDecisionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def _write_candidate(self, payload: dict, directory: str) -> Path:
        config_dir = Path(directory) / "configs"
        result_dir = Path(directory) / "results"
        config_dir.mkdir()
        result_dir.mkdir()
        source = ROOT / "results" / "nonlinear_pde_n0r_20260805.json"
        (result_dir / source.name).write_bytes(source.read_bytes())
        candidate = config_dir / CONFIG.name
        candidate.write_text(json.dumps(payload), encoding="utf-8")
        return candidate

    def test_reference_contract_is_valid(self) -> None:
        self.assertEqual(len(self.config["model_seeds"]["confirmatory"]), 5)
        self.assertEqual(len(self.config["mandatory_models"]), 9)

    def test_optimization_attribution_is_non_gating(self) -> None:
        attribution = load_optimization_config(OPTIMIZATION_CONFIG)
        self.assertFalse(attribution["has_success_threshold"])
        self.assertFalse(attribution["may_access_or_generate_test"])
        self.assertEqual(len(attribution["factorial_variants"]), 4)

    def test_n1b_freezes_selection_and_keeps_test_locked(self) -> None:
        parent, n1b = load_n1b_config(N1B_CONFIG)
        self.assertEqual(
            n1b["selected_shared_operator_training"]["maximum_steps"], 2800
        )
        self.assertEqual(
            n1b["checkpoint_freeze"]["confirmatory_model_seeds"],
            parent["model_seeds"]["confirmatory"],
        )
        self.assertFalse(n1b["checkpoint_freeze"]["test_split_generated"])
        self.assertFalse(n1b["checkpoint_freeze"]["test_seed_accessed"])

    def test_n1c_pins_manifest_and_deterministic_test_selector(self) -> None:
        parent, _, n1c, manifest = load_n1c_config(N1C_CONFIG)
        self.assertEqual(
            n1c["acquisition_evaluation"]["context_indices"],
            list(range(0, parent["data"]["operator_test_contexts"], 4)),
        )
        self.assertEqual(len(manifest["seed_runs"]), 5)
        self.assertFalse(n1c["test_lock"]["test_split_generated"])
        self.assertFalse(n1c["test_lock"]["test_seed_accessed"])

    def test_n1c_manifest_hash_cannot_change(self) -> None:
        payload = json.loads(N1C_CONFIG.read_text(encoding="utf-8"))
        payload["parents"]["checkpoint_manifest"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory) / "configs"
            result_dir = Path(directory) / "results"
            config_dir.mkdir()
            result_dir.mkdir()
            for source in (CONFIG, N1B_CONFIG):
                (config_dir / source.name).write_bytes(source.read_bytes())
            manifest = (
                ROOT
                / "results"
                / "nonlinear_pde_n1b_checkpoint_manifest_20260805.json"
            )
            (result_dir / manifest.name).write_bytes(manifest.read_bytes())
            candidate = config_dir / N1C_CONFIG.name
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                NonlinearDecisionError, "checkpoint manifest"
            ):
                load_n1c_config(candidate)

    def test_n1c_attribution_is_threshold_free_and_keeps_failure(self) -> None:
        _, n1c, attribution, manifest = load_n1c_attribution_config(
            N1C_ATTRIBUTION_CONFIG
        )
        self.assertFalse(attribution["has_success_threshold"])
        self.assertFalse(attribution["may_relabel_n1c"])
        self.assertFalse(
            attribution["may_authorize_n1d_or_irregular_3d"]
        )
        self.assertEqual(len(manifest["seed_runs"]), 5)
        self.assertEqual(
            attribution["test_semantics"]["same_test_context_seed"],
            n1c["test_lock"]["context_seed"],
        )

    def test_route_candidate_seed_honors_common_random_numbers(self) -> None:
        from experiments.run_nonlinear_pde_n1c_outer_test import (
            _route_candidate_seed,
        )

        _, _, n1c, _ = load_n1c_config(N1C_CONFIG)
        seeds = [
            _route_candidate_seed(n1c, 1234, route_offset)
            for route_offset in range(3)
        ]
        self.assertEqual(seeds, [51234, 51234, 51234])

    def test_test_access_cannot_move_before_checkpoint_freeze(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["data"]["test_access"] = "during_model_selection"
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_candidate(candidate, directory)
            with self.assertRaisesRegex(NonlinearDecisionError, "checkpoint freeze"):
                load_config(path)

    def test_nots_adaptation_cannot_be_called_reproduction(self) -> None:
        candidate = copy.deepcopy(self.config)
        nots = next(
            item
            for item in candidate["mandatory_models"]
            if item["id"] == "nots_adapted"
        )
        nots["not_a_reproduction"] = False
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_candidate(candidate, directory)
            with self.assertRaisesRegex(NonlinearDecisionError, "reproduction"):
                load_config(path)

    def test_n1_cannot_authorize_3d_execution(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["success_rule"][
            "n1_pass_authorizes_irregular_3d_protocol_registration_only"
        ] = False
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_candidate(candidate, directory)
            with self.assertRaisesRegex(NonlinearDecisionError, "decision rule"):
                load_config(path)

    @unittest.skipUnless(importlib.util.find_spec("torch"), "torch is not installed")
    def test_joint_density_and_lifted_operator_shapes(self) -> None:
        import torch

        device = torch.device("cpu")
        density = build_joint_density(self.config, device)
        operator = build_solution_operator(self.config, device)
        context = torch.zeros(3, 5)
        boundary = torch.zeros(3, 8)
        weights, means, covariances = density(context)
        self.assertEqual(tuple(weights.shape), (3, 2))
        self.assertEqual(tuple(means.shape), (3, 2, 8))
        self.assertEqual(tuple(covariances.shape), (3, 2, 8, 8))
        self.assertTrue(torch.isfinite(gmm_nll(
            weights, means, covariances, boundary
        )).all())
        field = operator(context, boundary)
        self.assertEqual(tuple(field.shape), (3, 33, 33))
        self.assertTrue(torch.allclose(field[:, 0], torch.zeros_like(field[:, 0])))
        self.assertTrue(torch.allclose(field[:, -1], torch.zeros_like(field[:, -1])))

        mask = torch.zeros(3, 8)
        mask[:, [0, 2]] = 1.0
        conditional = build_mask_conditional_density(self.config, device)
        independent = build_independent_mask_density(self.config, device)
        for result in (
            conditional(context, boundary, mask),
            independent("sparse_2", context, boundary, mask),
        ):
            self.assertEqual(tuple(result[0].shape), (3, 2))
            self.assertEqual(tuple(result[1].shape), (3, 2, 8))
            self.assertEqual(tuple(result[2].shape), (3, 2, 8, 8))

        autoregressive = build_lano_completion(self.config, device)
        completion = autoregressive.sample(
            context, boundary, mask, samples=4, seed=7
        )
        self.assertEqual(tuple(completion.shape), (3, 4, 8))

        for set_encoder in (False, True):
            direct = build_direct_probabilistic_operator(
                self.config, device, set_encoder=set_encoder
            )
            mean, scale = direct.moments(context, boundary, mask)
            self.assertEqual(tuple(mean.shape), (3, 33, 33))
            self.assertEqual(tuple(scale.shape), (3, 33, 33))
            self.assertTrue((scale > 0).all())

        representation = {
            "mean": torch.zeros(33 * 33),
            "basis": torch.eye(33 * 33)[:, :96],
            "coefficient_location": torch.zeros(96),
            "coefficient_scale": torch.ones(96),
            "rank": 96,
            "seed": 73080601,
            "iterations": 4,
        }
        reference_parameters = sum(
            parameter.numel() for parameter in operator.parameters()
        )
        matched = []
        for set_encoder in (False, True):
            direct = build_pod_probabilistic_operator(
                self.config,
                device,
                representation=representation,
                set_encoder=set_encoder,
            )
            mean, scale = direct.moments(context, boundary, mask)
            self.assertEqual(tuple(mean.shape), (3, 33, 33))
            self.assertTrue((scale > 0).all())
            matched.append(
                sum(parameter.numel() for parameter in direct.parameters())
            )
        deltaphi = build_deltaphi_residual_operator(
            self.config,
            device,
            representation=representation,
        )
        residual = deltaphi(
            context,
            boundary,
            context,
            boundary,
            torch.zeros(3, 33, 33),
        )
        self.assertEqual(tuple(residual.shape), (3, 33, 33))
        matched.append(
            sum(parameter.numel() for parameter in deltaphi.parameters())
        )
        for parameters in matched:
            self.assertLessEqual(
                abs(parameters - reference_parameters) / reference_parameters,
                0.1,
            )

    @unittest.skipUnless(importlib.util.find_spec("torch"), "torch is not installed")
    def test_radius_truncated_conditional_sampler_preserves_mask_and_support(
        self,
    ) -> None:
        import torch

        from aurora.nonlinear_pde_evaluation import (
            sample_radius_truncated_conditional_gmm,
        )

        weights = torch.tensor([[0.4, 0.6]])
        means = torch.zeros(1, 2, 8)
        covariances = torch.eye(8)[None, None].expand(1, 2, -1, -1).clone()
        observed = torch.tensor([[0.2, -0.1]])
        samples = sample_radius_truncated_conditional_gmm(
            weights,
            means,
            covariances,
            [0, 2],
            observed,
            samples=256,
            seed=17,
            maximum_radius=2.5,
        )
        self.assertTrue(
            torch.allclose(samples[:, :, [0, 2]], observed[:, None])
        )
        self.assertLessEqual(
            float(torch.linalg.vector_norm(samples, dim=-1).max().item()),
            2.5 + 1e-5,
        )

    @unittest.skipUnless(importlib.util.find_spec("torch"), "torch is not installed")
    def test_true_truncated_conditional_nll_is_finite(self) -> None:
        import torch

        from aurora.nonlinear_pde import boundary_law
        from aurora.nonlinear_pde_evaluation import (
            sample_radius_truncated_conditional_gmm,
        )
        from experiments.run_nonlinear_pde_n1c_attribution import (
            _true_truncated_conditional_nll,
        )

        context = torch.zeros(3, 5)
        weights, means, covariances = boundary_law(context)
        boundary = sample_radius_truncated_conditional_gmm(
            weights,
            means,
            covariances,
            [],
            torch.empty(3, 0),
            samples=1,
            seed=919,
            maximum_radius=2.5,
        )[:, 0]
        for mask in ([], [0, 2], [0, 2, 5, 7]):
            nll = _true_truncated_conditional_nll(
                weights,
                means,
                covariances,
                boundary,
                mask,
                maximum_radius=2.5,
            )
            self.assertEqual(tuple(nll.shape), (3,))
            self.assertTrue(torch.isfinite(nll).all())

    @unittest.skipUnless(importlib.util.find_spec("torch"), "torch is not installed")
    def test_energy_score_is_zero_for_identical_deterministic_samples(self) -> None:
        import torch

        from aurora.nonlinear_pde_evaluation import functional_energy_score

        target = torch.tensor([[1.0, -2.0, 0.5, 0.0]])
        samples = target[:, None].expand(-1, 8, -1).clone()
        self.assertTrue(
            torch.allclose(functional_energy_score(samples, target), torch.zeros(1))
        )

    @unittest.skipUnless(importlib.util.find_spec("torch"), "torch is not installed")
    def test_n1c_route_and_acquisition_tensor_smoke(self) -> None:
        import torch

        from aurora.nonlinear_pde import boundary_law
        from aurora.nonlinear_pde_decision import generate_solution_split
        from experiments.run_nonlinear_pde_n1c_outer_test import (
            _evaluate_acquisition,
            _evaluate_routes,
        )

        n1, _, n1c, _ = load_n1c_config(N1C_CONFIG)
        smoke = copy.deepcopy(n1c)
        smoke["route_evaluation"]["context_indices"] = [0]
        smoke["route_evaluation"]["posterior_samples"] = 4
        smoke["acquisition_evaluation"]["context_indices"] = [0]
        smoke["acquisition_evaluation"]["outer_measurement_samples"] = 2
        smoke["acquisition_evaluation"]["inner_posterior_samples"] = 2
        smoke["functional_contract"]["bayes_action_grid_points"] = 9
        n0 = json.loads(
            (ROOT / "configs" / "nonlinear_pde_n0.json").read_text(
                encoding="utf-8"
            )
        )
        device = torch.device("cpu")
        test = generate_solution_split(
            contexts=1,
            conditions=1,
            context_seed=9917801,
            boundary_seed=9917802,
            context_support=[-0.2, 0.2],
            maximum_radius=2.5,
            solver_config=n0,
            device=device,
        )
        (
            test["true_weights"],
            test["true_means"],
            test["true_covariances"],
        ) = boundary_law(test["context"])
        models = {
            "aurora_joint": build_joint_density(n1, device).eval(),
            "independent_mask_heads": build_independent_mask_density(
                n1, device
            ).eval(),
            "acflow_adapted": build_mask_conditional_density(n1, device).eval(),
            "aurora_shared_operator_pair_loss": build_solution_operator(
                n1, device
            ).eval(),
        }
        location = torch.zeros(4)
        scale = torch.ones(4)
        grid_minimum = -2.0 * torch.ones(4)
        grid_maximum = 2.0 * torch.ones(4)
        route, _, true_samples, summary = _evaluate_routes(
            smoke,
            n0,
            models,
            test,
            location,
            scale,
            grid_minimum,
            grid_maximum,
            seed_index=0,
            true_functional_samples=None,
        )
        self.assertEqual(set(route), {
            "aurora_joint",
            "independent_mask_heads",
            "acflow_adapted",
        })
        self.assertEqual(tuple(true_samples.shape), (1, 4, 4))
        self.assertTrue(summary["all_converged"])
        acquisition, _, true_risks, summaries = _evaluate_acquisition(
            smoke,
            n0,
            models,
            test,
            location,
            scale,
            grid_minimum,
            grid_maximum,
            seed_index=0,
            true_candidate_risks=None,
        )
        self.assertEqual(set(acquisition), {"missing", "sparse_2"})
        self.assertEqual(set(true_risks), {"missing", "sparse_2"})
        self.assertTrue(all(item["all_converged"] for item in summaries))


if __name__ == "__main__":
    unittest.main()
