import json
import unittest
from pathlib import Path

from aurora.nonlinear_pde import context_stratified_case_indices
from aurora.nonlinear_pde_attribution import load_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "nonlinear_pde_n0_attribution.json"


class NonlinearPDEAttributionContractTests(unittest.TestCase):
    def test_attribution_has_no_gate_or_authority(self) -> None:
        config = load_config(CONFIG)
        decision = config["decision_rule"]
        self.assertFalse(decision["has_success_threshold"])
        self.assertFalse(decision["may_relabel_n0"])
        self.assertFalse(decision["may_authorize_n1"])
        self.assertFalse(decision["may_authorize_irregular_3d"])
        self.assertFalse(decision["may_select_n0r_thresholds_or_seeds"])

    def test_failed_n0_result_pin_is_exact(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            config["failed_n0_result_sha256"],
            "ca442819026757a56ec1e62febd9cbcae9a4df435ed88cf4b9f78b76fc1dfff8",
        )

    def test_stratified_reference_spans_twelve_contexts(self) -> None:
        indices = context_stratified_case_indices(24, 12, 12)
        contexts = [index // 12 for index in indices]
        conditions = [index % 12 for index in indices]
        self.assertEqual(len(set(contexts)), 12)
        self.assertGreaterEqual(len(set(conditions)), 8)
        self.assertNotEqual(indices, list(range(12)))

    def test_stratified_pairs_cover_every_context(self) -> None:
        indices = context_stratified_case_indices(24, 12, 48)
        counts = [sum(index // 12 == context for index in indices) for context in range(24)]
        self.assertEqual(counts, [2] * 24)


if __name__ == "__main__":
    unittest.main()
