import copy
import math
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_confirmation_template_v2 import (
    ConfirmationTemplateV2Error,
    confirmation_pass,
    load_config,
    prefield_precision_viability,
    projected_gpu_hours,
    select_family_ids,
    validate_config,
    wilson_lower_bound,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_confirmation_template_v2.json"


class ResponseFidelityConfirmationTemplateV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def passing_summary(self) -> dict:
        return {
            "complete": True,
            "selected_family_count": 100,
            "prefield_precision_viability_passed": True,
            "prefield_compute_viability_passed": True,
            "field_upper_log_candidate_over_direct": 0.01,
            "power_law_upper_log_candidate_over_control": 0.01,
            "paired_response_lower_log_direct_over_candidate": 0.02,
            "tangent_lower_log_direct_over_candidate": 0.03,
            "paired_response_geometric_mean_ratio": 1.12,
            "tangent_geometric_mean_ratio": 1.11,
            "paired_response_positive_seed_count": 4,
            "tangent_positive_seed_count": 5,
            "paired_response_family_win_count": 59,
            "tangent_family_win_count": 60,
        }

    def test_template_is_inactive_and_supersedes_v1_before_evidence(self) -> None:
        checks = validate_config(self.config)
        self.assertEqual(len(checks), 13)
        self.assertFalse(self.config["activation_boundary"]["confirmation_registered"])
        self.assertFalse(self.config["supersession"]["v1_executed"])
        self.assertFalse(self.config["supersession"]["v1_confirmation_metadata_read"])
        self.assertFalse(self.config["supersession"]["v1_confirmation_field_read"])

    def test_source_population_and_hash_selection_are_exact(self) -> None:
        sample = self.config["confirmation_sample"]
        self.assertEqual(sample["reported_total_base_family_count"], 427)
        self.assertEqual(sample["maximum_post_exclusion_base_family_count_before_eligibility_audit"], 395)
        self.assertTrue(math.isclose(sample["maximum_population_sampling_fraction"], 100 / 395))
        eligible = [f"family-{index:03d}" for index in range(427)]
        historical = eligible[:32]
        first = select_family_ids(eligible, historical, count=100, seed=2027081301)
        second = select_family_ids(reversed(eligible), historical, count=100, seed=2027081301)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 100)
        self.assertFalse(set(first) & set(historical))

    def test_prefield_precision_gate_requires_both_endpoints(self) -> None:
        self.assertTrue(prefield_precision_viability(0.20, 0.29))
        self.assertFalse(prefield_precision_viability(0.20, 0.31))
        self.assertFalse(prefield_precision_viability(0.31, 0.20))
        with self.assertRaises(ConfirmationTemplateV2Error):
            prefield_precision_viability(float("nan"), 0.20)

    def test_complete_workload_projection_counts_two_models_and_five_seeds(self) -> None:
        hours = projected_gpu_hours(
            selected_case_flow_count=20000,
            upper_seconds_per_case_flow_model_seed=0.5,
        )
        self.assertAlmostEqual(hours, 20000 * 10 * 0.5 / 3600)
        self.assertLess(hours, 40.0)
        self.assertGreater(
            projected_gpu_hours(
                selected_case_flow_count=20000,
                upper_seconds_per_case_flow_model_seed=1.0,
            ),
            40.0,
        )

    def test_wilson_majority_boundary_is_59_of_100(self) -> None:
        self.assertLessEqual(wilson_lower_bound(58, 100), 0.5)
        self.assertGreater(wilson_lower_bound(59, 100), 0.5)

    def test_confirmation_pass_requires_every_component(self) -> None:
        summary = self.passing_summary()
        self.assertTrue(confirmation_pass(summary))
        failures = {
            "complete": False,
            "prefield_precision_viability_passed": False,
            "prefield_compute_viability_passed": False,
            "field_upper_log_candidate_over_direct": 0.03,
            "power_law_upper_log_candidate_over_control": 0.03,
            "paired_response_lower_log_direct_over_candidate": 0.0,
            "tangent_lower_log_direct_over_candidate": -0.01,
            "paired_response_geometric_mean_ratio": 1.09,
            "tangent_geometric_mean_ratio": 1.09,
            "paired_response_positive_seed_count": 3,
            "tangent_positive_seed_count": 3,
            "paired_response_family_win_count": 58,
            "tangent_family_win_count": 58,
        }
        for key, value in failures.items():
            candidate = copy.deepcopy(summary)
            candidate[key] = value
            self.assertFalse(confirmation_pass(candidate), key)

    def test_mean_effect_cannot_hide_minority_family_benefit(self) -> None:
        summary = self.passing_summary()
        summary["paired_response_geometric_mean_ratio"] = 1.50
        summary["paired_response_lower_log_direct_over_candidate"] = 0.20
        summary["paired_response_family_win_count"] = 40
        self.assertFalse(confirmation_pass(summary))

    def test_exact_estimator_is_case_log_then_seed_mean_then_family_bootstrap(self) -> None:
        estimators = self.config["exact_estimators"]
        self.assertIn("case_log_contrast", estimators["family_seed_contrast"])
        self.assertIn("five_frozen_seeds", estimators["family_contrast"])
        self.assertIn("geometric_mean", estimators["reported_multiplicative_ratio"])
        self.assertEqual(estimators["bootstrap_unit"], "base_family")
        self.assertFalse(estimators["nodes_cases_flows_or_seeds_treated_as_independent_replicates"])

    def test_direct_prior_and_authority_boundaries_fail_closed(self) -> None:
        for section, key, value in (
            ("direct_prior_boundary", "multi_flow_boundary_condition_operator_or_component_stack_claim_allowed", True),
            ("activation_boundary", "prefield_precision_viability_passed", True),
            ("confirmation_sample", "post_result_sample_enlargement_allowed", True),
            ("compute_and_execution", "junjinyong_allowed", True),
            ("compute_and_execution", "gpu_authorized_now", True),
            ("stopping_and_claim_deletion", "partial_aggregation_allowed", True),
        ):
            candidate = copy.deepcopy(self.config)
            candidate[section][key] = value
            with self.assertRaises(ConfirmationTemplateV2Error):
                validate_config(candidate)


if __name__ == "__main__":
    unittest.main()
