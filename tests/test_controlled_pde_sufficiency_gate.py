import copy
import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

from aurora.controlled_pde_sufficiency_gate import load_config, run_experiment


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "controlled_pde_g1s.json"


class ControlledPDESufficiencyContractTests(unittest.TestCase):
    def test_only_fresh_seeds_and_training_geometry_change_from_g1r(self) -> None:
        config = load_config(CONFIG)
        g1r = json.loads(
            (ROOT / "configs" / "controlled_pde_g1r.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(config["train_geometries"], 3072)
        self.assertEqual(g1r["train_geometries"], 768)
        for key in (
            "validation_geometries",
            "test_geometries",
            "conditions_per_geometry",
            "hidden_dim",
            "density_training",
            "operator_training",
            "direct_baseline_training",
            "evaluation",
            "success_thresholds",
        ):
            self.assertEqual(config[key], g1r[key])
        self.assertFalse(config["may_relabel_g1_or_g1r"])
        self.assertFalse(config["may_claim_data_quantity_as_method_contribution"])

    def test_seeds_are_disjoint_from_every_prior_density_run(self) -> None:
        config = load_config(CONFIG)
        prior = set()
        for name in (
            "controlled_pde_g1.json",
            "controlled_pde_g1r.json",
            "controlled_pde_density_attribution.json",
            "controlled_pde_density_development.json",
        ):
            payload = json.loads((ROOT / "configs" / name).read_text(encoding="utf-8"))
            prior.update(payload["seeds"])
        self.assertTrue(set(config["seeds"]).isdisjoint(prior))


@unittest.skipIf(torch is None, "controlled PDE tests require torch")
class ControlledPDESufficiencyRuntimeTests(unittest.TestCase):
    def test_tiny_failed_smoke_does_not_authorize_confirmation(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        smoke_seed = 9917601
        self.assertNotIn(smoke_seed, config["seeds"])
        config["seeds"] = [smoke_seed]
        config["train_geometries"] = 8
        config["validation_geometries"] = 4
        config["test_geometries"] = 4
        config["conditions_per_geometry"] = 2
        config["hidden_dim"] = 16
        for name in (
            "density_training",
            "operator_training",
            "direct_baseline_training",
        ):
            config[name]["maximum_epochs"] = 2
            config[name]["validation_interval"] = 1
            config[name]["early_stopping_patience"] = 2
        evaluation = config["evaluation"]
        evaluation["bc_samples"] = 16
        evaluation["gauss_hermite_order"] = 3
        evaluation["projective_samples"] = 8
        evaluation["projective_geometries"] = 4
        evaluation["projective_replicates"] = 2
        evaluation["sliced_projections"] = 4
        evaluation["bootstrap_replicates"] = 20
        result = run_experiment(config, require_cuda=False)
        self.assertFalse(result["failed_g1_relabeled"])
        self.assertFalse(result["failed_g1r_relabeled"])
        self.assertFalse(result["data_quantity_claimed_as_method_contribution"])
        self.assertEqual(
            result["nonlinear_or_3d_confirmatory_training_authorized"],
            result["aggregate"]["gate"]["passed"],
        )


if __name__ == "__main__":
    unittest.main()
