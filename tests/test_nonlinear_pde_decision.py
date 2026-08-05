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
    load_optimization_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "nonlinear_pde_n1.json"
OPTIMIZATION_CONFIG = (
    ROOT / "configs" / "nonlinear_pde_n1_optimization_attribution.json"
)
N1B_CONFIG = ROOT / "configs" / "nonlinear_pde_n1b.json"
N1C_CONFIG = ROOT / "configs" / "nonlinear_pde_n1c.json"


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
    def test_energy_score_is_zero_for_identical_deterministic_samples(self) -> None:
        import torch

        from aurora.nonlinear_pde_evaluation import functional_energy_score

        target = torch.tensor([[1.0, -2.0, 0.5, 0.0]])
        samples = target[:, None].expand(-1, 8, -1).clone()
        self.assertTrue(
            torch.allclose(functional_energy_score(samples, target), torch.zeros(1))
        )


if __name__ == "__main__":
    unittest.main()
