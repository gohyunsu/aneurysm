import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    build_direct_probabilistic_operator,
    build_independent_mask_density,
    build_joint_density,
    build_lano_completion,
    build_mask_conditional_density,
    build_solution_operator,
    gmm_nll,
    load_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "nonlinear_pde_n1.json"


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


if __name__ == "__main__":
    unittest.main()
