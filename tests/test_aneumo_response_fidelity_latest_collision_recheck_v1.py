import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_latest_collision_recheck_v1.json"


class LatestCollisionRecheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_score_is_borderline_and_not_inflated(self) -> None:
        score = self.payload["score"]
        self.assertEqual(sum(score["axis_scores"]), score["total"])
        self.assertEqual(score["total"], 32.5)
        self.assertEqual(score["axis_scores"][2], score["residual_novelty_floor"])
        self.assertFalse(score["score_increased"])
        self.assertFalse(score["historical_34_relabelled"])

    def test_new_collisions_delete_generic_method_claims(self) -> None:
        identifiers = {item["id"] for item in self.payload["new_direct_priors"]}
        self.assertEqual(
            identifiers,
            {
                "arxiv:2606.03038",
                "doi:10.1038/s43588-026-00974-2",
                "doi:10.1007/s10439-026-04269-5",
            },
        )
        self.assertIn(
            "hard_constraint_or_zero_at_anchor_output_transform",
            self.payload["forbidden_novelty_claims"],
        )
        self.assertEqual(
            self.payload["claim_roles"]["RF_C2"],
            "controlled_application_solution_not_general_algorithmic_novelty",
        )

    def test_no_evidence_or_execution_is_activated(self) -> None:
        activation = self.payload["paper_activation"]
        self.assertEqual(activation["real_p0_checks"], "0/12")
        self.assertTrue(all(value is False for key, value in activation.items() if key != "real_p0_checks"))
        execution = self.payload["execution"]
        self.assertTrue(all(value is False for value in execution.values()))


if __name__ == "__main__":
    unittest.main()
