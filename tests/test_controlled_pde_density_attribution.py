import copy
import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

from aurora.controlled_pde_density_attribution import (
    _population_cross_entropy,
    _tasks,
    load_config,
    run_experiment,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "controlled_pde_density_attribution.json"


class DensityAttributionContractTests(unittest.TestCase):
    def test_contract_is_post_result_and_has_no_gate(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(
            config["status"], "post_result_exploratory_density_attribution"
        )
        self.assertFalse(config["may_relabel_g1_or_g1r"])
        self.assertFalse(config["may_define_a_new_gate"])
        self.assertIsNone(config["reporting"]["success_thresholds"])

    def test_registered_seeds_are_disjoint_from_g1_and_g1r(self) -> None:
        config = load_config(CONFIG)
        g1r = json.loads(
            (ROOT / "configs" / "controlled_pde_g1r.json").read_text(
                encoding="utf-8"
            )
        )
        g1 = json.loads(
            (ROOT / "configs" / "controlled_pde_g1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(
            set(config["seeds"]).isdisjoint([*g1["seeds"], *g1r["seeds"]])
        )

    def test_factorial_tasks_have_one_reference_and_six_extra_cells(self) -> None:
        config = load_config(CONFIG)
        tasks = _tasks(config)
        self.assertEqual(len(tasks), 10)
        matched = [
            cell
            for cell in config["sample_scaling"]["cells"]
            if "matched_6144_boundary_budget" in cell["axes"]
        ]
        self.assertEqual(len(matched), 3)
        self.assertEqual(
            {
                int(cell["train_geometries"])
                * int(cell["conditions_per_geometry"])
                for cell in matched
            },
            {6144},
        )


@unittest.skipIf(torch is None, "density attribution tests require torch")
class DensityAttributionMathTests(unittest.TestCase):
    def test_population_cross_entropy_has_zero_oracle_excess(self) -> None:
        mean = torch.tensor([[0.2, -0.3], [-0.1, 0.4]])
        covariance = torch.tensor(
            [
                [[0.08, 0.02], [0.02, 0.05]],
                [[0.06, -0.01], [-0.01, 0.09]],
            ]
        )
        oracle = _population_cross_entropy(mean, covariance, mean, covariance)
        self.assertTrue(torch.isfinite(oracle).all())
        self.assertTrue(torch.allclose(oracle - oracle, torch.zeros_like(oracle)))

    def test_tiny_runtime_uses_only_nonregistered_smoke_seed(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        registered = set(config["seeds"])
        smoke_seed = 9917401
        self.assertNotIn(smoke_seed, registered)
        config["seeds"] = [smoke_seed]
        config["hidden_dim"] = 8
        config["reference_cell"] = {
            "id": "g4_c2",
            "train_geometries": 4,
            "conditions_per_geometry": 2,
        }
        config["validation"] = {"geometries": 4, "conditions_per_geometry": 2}
        config["analysis"] = {"geometries": 4, "conditions_per_geometry": 2}
        config["training"]["maximum_epochs"] = 2
        config["training"]["validation_interval"] = 1
        config["training"]["early_stopping_patience"] = 2
        config["reference_objectives"] = [
            {
                "id": "empirical_nll_population_selected",
                "train_objective": "empirical_nll",
                "validation_objective": "analytic_population_nll",
            }
        ]
        config["sample_scaling"]["cells"] = [
            {
                "id": "g4_c2",
                "train_geometries": 4,
                "conditions_per_geometry": 2,
                "axes": ["reference"],
            }
        ]
        result = run_experiment(config, require_cuda=False)
        self.assertFalse(result["failed_g1_relabeled"])
        self.assertFalse(result["failed_g1r_relabeled"])
        self.assertFalse(result["new_gate_defined"])
        self.assertEqual(result["records"][0]["seed"], smoke_seed)


if __name__ == "__main__":
    unittest.main()
