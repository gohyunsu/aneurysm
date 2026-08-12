import copy
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_confirmation_template_v1 import (
    ConfirmationTemplateError,
    confirmation_pass,
    load_config,
    select_family_ids,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_confirmation_template_v1.json"


class ResponseFidelityConfirmationTemplateV1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def test_template_is_inactive_and_blocked_on_every_upstream_gate(self) -> None:
        checks = validate_config(self.config)
        self.assertEqual(len(checks), 11)
        activation = self.config["activation_boundary"]
        self.assertFalse(activation["this_file_can_be_executed"])
        self.assertFalse(activation["confirmation_registered"])
        self.assertIsNone(activation["real_p0_observed_verdict"])
        self.assertIsNone(activation["p1_observed_verdict"])

    def test_selector_is_outcome_blind_unique_and_excludes_all_historical_families(self) -> None:
        eligible = [f"family-{index:03d}" for index in range(160)]
        historical = eligible[:32]
        selected_a = select_family_ids(eligible, historical, count=100, seed=2027081301)
        selected_b = select_family_ids(reversed(eligible), historical, count=100, seed=2027081301)
        self.assertEqual(selected_a, selected_b)
        self.assertEqual(len(selected_a), 100)
        self.assertFalse(set(selected_a) & set(historical))
        self.assertEqual(len(set(selected_a)), 100)

    def test_fewer_than_100_new_families_fails_without_substitution(self) -> None:
        with self.assertRaisesRegex(ConfirmationTemplateError, "fewer eligible"):
            select_family_ids(range(120), range(32), count=100, seed=2027081301)

    def test_confirmation_pass_requires_the_complete_intersection_union_conjunction(self) -> None:
        summary = {
            "complete": True,
            "selected_family_count": 100,
            "field_upper_log_candidate_over_direct": 0.01,
            "power_law_upper_log_candidate_over_control": 0.01,
            "paired_response_lower_log_direct_over_candidate": 0.02,
            "tangent_lower_log_direct_over_candidate": 0.03,
            "paired_response_point_ratio": 1.12,
            "tangent_point_ratio": 1.11,
            "paired_response_positive_seed_count": 4,
            "tangent_positive_seed_count": 5,
        }
        self.assertTrue(confirmation_pass(summary))
        for key in (
            "complete",
            "field_upper_log_candidate_over_direct",
            "power_law_upper_log_candidate_over_control",
            "paired_response_lower_log_direct_over_candidate",
            "tangent_lower_log_direct_over_candidate",
            "paired_response_point_ratio",
            "tangent_point_ratio",
            "paired_response_positive_seed_count",
            "tangent_positive_seed_count",
        ):
            candidate = copy.deepcopy(summary)
            candidate[key] = {
                "complete": False,
                "field_upper_log_candidate_over_direct": 0.03,
                "power_law_upper_log_candidate_over_control": 0.03,
                "paired_response_lower_log_direct_over_candidate": 0.0,
                "tangent_lower_log_direct_over_candidate": -0.01,
                "paired_response_point_ratio": 1.09,
                "tangent_point_ratio": 1.09,
                "paired_response_positive_seed_count": 3,
                "tangent_positive_seed_count": 3,
            }[key]
            self.assertFalse(confirmation_pass(candidate), key)

    def test_negative_or_mixed_response_direction_cannot_be_relabelled(self) -> None:
        summary = {
            "complete": True,
            "selected_family_count": 100,
            "field_upper_log_candidate_over_direct": 0.0,
            "power_law_upper_log_candidate_over_control": 0.0,
            "paired_response_lower_log_direct_over_candidate": 0.02,
            "tangent_lower_log_direct_over_candidate": -0.02,
            "paired_response_point_ratio": 1.15,
            "tangent_point_ratio": 0.90,
            "paired_response_positive_seed_count": 5,
            "tangent_positive_seed_count": 1,
        }
        self.assertFalse(confirmation_pass(summary))
        self.assertIn("without_narrative_reversal", self.config["stopping_and_claim_deletion"]["negative_or_mixed_direction_action"])

    def test_family_mean_and_seed_mean_precede_family_bootstrap(self) -> None:
        aggregation = self.config["family_level_aggregation"]
        self.assertEqual(aggregation["bootstrap_unit"], "base_family")
        self.assertIn("mean_over_five", aggregation["seed_level"])
        self.assertFalse(aggregation["nodes_cases_flows_or_seeds_treated_as_independent_replicates"])

    def test_figure_must_show_candidate_failure_typical_and_benefit_cases(self) -> None:
        figure = self.config["interpretable_figure"]
        self.assertEqual(len(figure["family_roles"]), 3)
        self.assertIn("candidate_worst_case", figure["family_roles"][0])
        self.assertFalse(figure["favorable_only_case_selection_allowed"])
        self.assertTrue(figure["same_coordinates_camera_and_reference_derived_color_range"])

    def test_compute_and_claim_authority_cannot_be_opened(self) -> None:
        for mutation in (
            ("compute_and_execution", "junjinyong_allowed", True),
            ("compute_and_execution", "gpu_authorized_now", True),
            ("activation_boundary", "confirmation_registered", True),
            ("confirmation_sample", "post_result_sample_enlargement_allowed", True),
            ("stopping_and_claim_deletion", "partial_aggregation_allowed", True),
        ):
            candidate = copy.deepcopy(self.config)
            candidate[mutation[0]][mutation[1]] = mutation[2]
            with self.assertRaises(ConfirmationTemplateError):
                validate_config(candidate)


if __name__ == "__main__":
    unittest.main()
