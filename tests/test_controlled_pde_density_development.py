import copy
import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

from aurora.controlled_pde_density_development import (
    _group_moments,
    _tasks,
    load_config,
    run_experiment,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "controlled_pde_density_development.json"


class DensityDevelopmentContractTests(unittest.TestCase):
    def test_contract_is_development_only_and_cannot_open_a_gate(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["status"], "development_only_estimator_selection")
        self.assertFalse(config["may_relabel_g1_or_g1r"])
        self.assertFalse(config["may_define_or_pass_a_gate"])
        self.assertFalse(config["may_authorize_nonlinear_or_3d_training"])
        self.assertIsNone(config["reporting"]["success_thresholds"])

    def test_development_seeds_are_disjoint_from_prior_exact_runs(self) -> None:
        config = load_config(CONFIG)
        prior = []
        for name in (
            "controlled_pde_g1.json",
            "controlled_pde_g1r.json",
            "controlled_pde_density_attribution.json",
        ):
            payload = json.loads(
                (ROOT / "configs" / name).read_text(encoding="utf-8")
            )
            prior.extend(payload["seeds"])
        self.assertTrue(set(config["seeds"]).isdisjoint(prior))

    def test_two_cells_cross_four_estimators(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(len(_tasks(config)), 8)
        self.assertEqual(config["selection_rule"]["cell_id"], "g768_c8")


@unittest.skipIf(torch is None, "density development tests require torch")
class DensityDevelopmentMathTests(unittest.TestCase):
    def test_pairwise_u_statistic_equals_unbiased_sample_covariance(self) -> None:
        boundary = torch.tensor(
            [
                [
                    [1.0, -1.0],
                    [2.0, 0.0],
                    [4.0, 3.0],
                    [-1.0, 2.0],
                ]
            ]
        )
        _, covariance = _group_moments(boundary, shrinkage=0.0)
        pairs = []
        for left in range(boundary.shape[1]):
            for right in range(left + 1, boundary.shape[1]):
                delta = boundary[:, left] - boundary[:, right]
                pairs.append(0.5 * torch.einsum("bi,bj->bij", delta, delta))
        pairwise = torch.stack(pairs).mean(dim=0)
        self.assertTrue(torch.allclose(covariance - 1e-6 * torch.eye(2), pairwise))

    def test_full_shrinkage_uses_pooled_within_geometry_covariance(self) -> None:
        boundary = torch.tensor(
            [
                [[0.0, 0.0], [2.0, 0.0], [1.0, 1.0]],
                [[0.0, 0.0], [0.0, 4.0], [1.0, 2.0]],
            ]
        )
        _, covariance = _group_moments(boundary, shrinkage=1.0)
        self.assertTrue(torch.allclose(covariance[0], covariance[1]))

    def test_tiny_runtime_cannot_authorize_confirmation(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        smoke_seed = 9917501
        self.assertNotIn(smoke_seed, config["seeds"])
        config["seeds"] = [smoke_seed]
        config["hidden_dim"] = 8
        config["validation"] = {"geometries": 4, "conditions_per_geometry": 2}
        config["analysis"] = {"geometries": 4, "conditions_per_geometry": 2}
        config["training"]["maximum_epochs"] = 2
        config["training"]["validation_interval"] = 1
        config["training"]["early_stopping_patience"] = 2
        config["cells"] = [
            {
                "id": "g4_c2",
                "train_geometries": 4,
                "conditions_per_geometry": 2,
                "role": "smoke",
            }
        ]
        config["estimators"] = [
            {
                "id": "grouped_smoke",
                "train_objective": "grouped_moments",
                "validation_objective": "empirical_nll",
                "covariance_shrinkage": 0.25,
            }
        ]
        config["selection_rule"]["cell_id"] = "g4_c2"
        result = run_experiment(config, require_cuda=False)
        self.assertFalse(result["new_gate_defined_or_passed"])
        self.assertFalse(result["nonlinear_or_3d_training_authorized"])
        self.assertEqual(
            result["aggregate"]["development_selection"]["estimator_id"],
            "grouped_smoke",
        )


if __name__ == "__main__":
    unittest.main()
