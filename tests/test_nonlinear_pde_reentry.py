import json
import unittest
from pathlib import Path

from aurora.nonlinear_pde import context_stratified_case_indices
from aurora.nonlinear_pde_reentry import (
    EXPECTED_SEEDS,
    EXPECTED_THRESHOLDS,
    load_config,
    resolve_runtime_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "nonlinear_pde_n0r.json"


class NonlinearPDEReentryContractTests(unittest.TestCase):
    def test_n0r_was_frozen_before_n0a_outcome(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(
            config["status"],
            "preregistered_before_n0a_result_and_fresh_gpu_run",
        )
        self.assertFalse(config["n0a_result_may_change_this_contract"])
        self.assertFalse(config["may_relabel_failed_n0"])
        self.assertFalse(config["may_establish_method_novelty"])
        self.assertFalse(config["may_authorize_irregular_3d_headline"])

    def test_n0r_uses_fresh_seeds_and_unchanged_thresholds(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["seeds"], EXPECTED_SEEDS)
        self.assertFalse(
            set(config["seeds"]) & {62080311, 62080312, 62080313}
        )
        self.assertEqual(config["success_thresholds"], EXPECTED_THRESHOLDS)

    def test_n0r_context_coverage_is_exact(self) -> None:
        reference = context_stratified_case_indices(24, 12, 24)
        paired = context_stratified_case_indices(24, 12, 48)
        self.assertEqual(
            [sum(index // 12 == context for index in reference) for context in range(24)],
            [1] * 24,
        )
        self.assertEqual(
            [sum(index // 12 == context for index in paired) for context in range(24)],
            [2] * 24,
        )

    def test_runtime_resolves_only_sampling_and_fresh_seeds(self) -> None:
        config = load_config(CONFIG)
        runtime = resolve_runtime_config(config, CONFIG)
        source = json.loads(
            (ROOT / "configs" / "nonlinear_pde_n0.json").read_text(encoding="utf-8")
        )
        self.assertEqual(runtime["pde"], source["pde"])
        self.assertEqual(runtime["boundary_law"], source["boundary_law"])
        self.assertEqual(runtime["functionals"], source["functionals"])
        self.assertEqual(runtime["success_thresholds"], source["success_thresholds"])
        self.assertEqual(runtime["seeds"], EXPECTED_SEEDS)
        self.assertEqual(
            runtime["sampling"]["case_selector"],
            "context_stratified_case_indices_v1",
        )


if __name__ == "__main__":
    unittest.main()
