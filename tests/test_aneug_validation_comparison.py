import copy
import json
import unittest
from pathlib import Path

from aurora.aneug_validation_comparison import (
    AneuGValidationComparisonError,
    compare_to_reference,
    paired_bootstrap_delta,
    pareto_set,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]


def rows(field, tawss, osi, coverage=1.0):
    return [
        {
            "field_relative_l2": value,
            "tawss_normalized_absolute_error": tawss[index],
            "osi_mae": osi[index],
            "osi_coverage": coverage,
        }
        for index, value in enumerate(field)
    ]


def result(case_rows):
    return {
        "status": "complete",
        "development_only": True,
        "case_ids_included": False,
        "outer_or_auxiliary_values_read": False,
        "validation": {"per_case_without_identifiers": case_rows},
    }


class AneuGValidationComparisonTests(unittest.TestCase):
    def test_config_has_no_absolute_or_automatic_gate(self):
        config = json.loads(
            (ROOT / "configs/aneug_validation_comparison_v1.json").read_text()
        )
        validate_config(config)
        self.assertIsNone(config["decision"]["absolute_performance_threshold"])
        self.assertFalse(config["decision"]["automatic_winner"])

    def test_paired_delta_is_deterministic_and_direction_aware(self):
        reference = rows([0.4, 0.5, 0.6], [0.3] * 3, [0.02] * 3)
        candidate = rows([0.3, 0.4, 0.5], [0.2] * 3, [0.01] * 3)
        first = paired_bootstrap_delta(
            candidate, reference, "field_relative_l2", replicates=500, seed=7
        )
        second = paired_bootstrap_delta(
            candidate, reference, "field_relative_l2", replicates=500, seed=7
        )
        self.assertEqual(first, second)
        self.assertAlmostEqual(first["point_delta"], -0.1)
        self.assertEqual(first["bootstrap_probability_candidate_better"], 1.0)

    def test_higher_coverage_uses_the_correct_favorable_direction(self):
        reference = rows([0.4, 0.5], [0.3] * 2, [0.02] * 2, coverage=0.8)
        candidate = rows([0.4, 0.5], [0.3] * 2, [0.02] * 2, coverage=1.0)
        output = paired_bootstrap_delta(
            candidate, reference, "osi_coverage", replicates=200, seed=3
        )
        self.assertEqual(output["direction"], "higher")
        self.assertEqual(output["bootstrap_probability_candidate_better"], 1.0)

    def test_pareto_set_retains_tradeoffs_and_removes_dominated_method(self):
        means = {
            "field_specialist": {
                "field_relative_l2": 0.2,
                "tawss_normalized_absolute_error": 0.3,
                "osi_mae": 0.02,
                "osi_coverage": 1.0,
            },
            "functional_specialist": {
                "field_relative_l2": 0.3,
                "tawss_normalized_absolute_error": 0.2,
                "osi_mae": 0.01,
                "osi_coverage": 1.0,
            },
            "dominated": {
                "field_relative_l2": 0.4,
                "tawss_normalized_absolute_error": 0.4,
                "osi_mae": 0.03,
                "osi_coverage": 0.9,
            },
        }
        self.assertEqual(
            pareto_set(means), ["field_specialist", "functional_specialist"]
        )

    def test_comparison_reports_no_winner_and_no_threshold(self):
        reference_rows = rows([0.4] * 51, [0.3] * 51, [0.02] * 51)
        candidate_rows = rows([0.35] * 51, [0.25] * 51, [0.015] * 51)
        output = compare_to_reference(
            {"reference": result(reference_rows), "candidate": result(candidate_rows)},
            "reference",
            replicates=200,
            seed=11,
        )
        self.assertIsNone(output["automatic_winner"])
        self.assertIsNone(output["absolute_performance_threshold"])
        self.assertEqual(output["pareto_set"], ["candidate"])
        self.assertFalse(output["population_inference"])

    def test_rejects_unsealed_or_mismatched_result(self):
        case_rows = rows([0.4] * 51, [0.3] * 51, [0.02] * 51)
        invalid = result(case_rows)
        invalid["outer_or_auxiliary_values_read"] = True
        with self.assertRaisesRegex(AneuGValidationComparisonError, "sealed_boundary"):
            compare_to_reference(
                {"reference": result(case_rows), "invalid": invalid},
                "reference",
                replicates=200,
            )
        short = result(copy.deepcopy(case_rows[:-1]))
        with self.assertRaisesRegex(AneuGValidationComparisonError, "case_count"):
            compare_to_reference(
                {"reference": result(case_rows), "short": short},
                "reference",
                replicates=200,
            )


if __name__ == "__main__":
    unittest.main()
