from __future__ import annotations

import copy
import unittest
from pathlib import Path

from aurora.aneug_release_730_matched_information_analysis import (
    CELL_ORDER,
    MatchedInformationAnalysisError,
    analyze_matched_information,
    extract_cell_rows,
    load_config,
    paired_linear_contrast,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_matched_information_analysis_v1.json"


def rows(offset: float, coverage: float) -> list[dict[str, float]]:
    return [
        {
            "field_relative_l2": 0.50 + offset + index * 1e-5,
            "mean_wss_vector_error": 0.40 + offset,
            "tawss_normalized_absolute_error": 0.30 + offset,
            "osi_mae": 0.020 + offset * 0.01,
            "osi_coverage": coverage,
        }
        for index in range(73)
    ]


def cell(label: str, offset: float, coverage: float = 0.9) -> dict:
    control = label.startswith("control_")
    steady = label.endswith("TS")
    return {
        "schema_version": "aurora.aneug_release_730_matched_information_cell.v1",
        "status": "complete_validation_development",
        "model_role": "selected_control" if control else "selected_proposal",
        "information_mode": "eligible_steady" if steady else "transient_only",
        "validation_case_digest": "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024",
        "private_split_manifest_sha256": "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f",
        "validation_loader_order_sha256": "cceb0e475e2f0dc04ce642e29da12dfc3080eac77dfd796644aa6cad88f05a24",
        "eligible_steady_rows": 13_985 if steady else 0,
        "eligible_steady_case_digest": (
            "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc"
            if steady
            else None
        ),
        "case_ids_included": False,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "paper_result_or_claim": False,
        "per_case_without_identifiers": rows(offset, coverage),
    }


def additive_cells() -> dict[str, dict]:
    return {
        "control_T": cell("control_T", 0.00, 0.80),
        "control_TS": cell("control_TS", -0.05, 0.85),
        "proposal_T": cell("proposal_T", -0.10, 0.90),
        "proposal_TS": cell("proposal_TS", -0.15, 0.95),
    }


class MatchedInformationAnalysisTests(unittest.TestCase):
    def test_config_fixes_complete_factorial_without_a_gate(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(tuple(config["factorial"]["cells"]), CELL_ORDER)
        self.assertEqual(config["factorial"]["eligible_steady_rows"], 13_985)
        self.assertFalse(config["factorial"]["proposal_only_steady_labels"])
        self.assertIsNone(config["decision"]["absolute_performance_threshold"])
        self.assertFalse(config["decision"]["automatic_winner"])
        self.assertFalse(config["boundary"]["locked_test_or_extra_access"])

    def test_additive_effects_have_zero_interaction(self) -> None:
        output = analyze_matched_information(
            additive_cells(), load_config(CONFIG), replicates=200, seed=7
        )
        contrasts = output["paired_contrasts"]
        self.assertAlmostEqual(
            contrasts["proposal_minus_control_T"]["field_relative_l2"][
                "point_delta"
            ],
            -0.10,
        )
        self.assertAlmostEqual(
            contrasts["steady_minus_transient_control"]["field_relative_l2"][
                "point_delta"
            ],
            -0.05,
        )
        self.assertAlmostEqual(
            contrasts["method_by_steady_interaction"]["field_relative_l2"][
                "point_delta"
            ],
            0.0,
            places=12,
        )
        self.assertIsNone(output["automatic_winner"])
        self.assertTrue(output["interaction_is_not_standalone_novelty"])

    def test_interaction_detects_extra_proposal_benefit(self) -> None:
        cells = additive_cells()
        cells["proposal_TS"] = cell("proposal_TS", -0.20, 0.99)
        output = analyze_matched_information(
            cells, load_config(CONFIG), replicates=200, seed=11
        )
        interaction = output["paired_contrasts"]["method_by_steady_interaction"]
        self.assertAlmostEqual(
            interaction["field_relative_l2"]["point_delta"], -0.05
        )
        self.assertEqual(
            interaction["field_relative_l2"][
                "bootstrap_probability_favorable_direction"
            ],
            1.0,
        )
        self.assertGreater(interaction["osi_coverage"]["point_delta"], 0.0)
        self.assertEqual(
            interaction["osi_coverage"][
                "bootstrap_probability_favorable_direction"
            ],
            1.0,
        )

    def test_linear_contrast_is_deterministic(self) -> None:
        config = load_config(CONFIG)
        parsed = {
            label: extract_cell_rows(value, label, config)
            for label, value in additive_cells().items()
        }
        coefficients = config["factorial"]["contrasts"][
            "method_by_steady_interaction"
        ]
        first = paired_linear_contrast(
            parsed, coefficients, "field_relative_l2", replicates=200, seed=13
        )
        second = paired_linear_contrast(
            parsed, coefficients, "field_relative_l2", replicates=200, seed=13
        )
        self.assertEqual(first, second)

    def test_rejects_incomplete_or_unmatched_factorial(self) -> None:
        config = load_config(CONFIG)
        incomplete = additive_cells()
        del incomplete["proposal_TS"]
        with self.assertRaisesRegex(
            MatchedInformationAnalysisError, "complete_factorial"
        ):
            analyze_matched_information(incomplete, config, replicates=200)
        changed = additive_cells()
        changed["proposal_TS"]["eligible_steady_case_digest"] = "0" * 64
        with self.assertRaisesRegex(
            MatchedInformationAnalysisError, "proposal_TS_steady_scope"
        ):
            analyze_matched_information(changed, config, replicates=200)

        changed_order = additive_cells()
        changed_order["proposal_TS"]["validation_loader_order_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            MatchedInformationAnalysisError, "proposal_TS_split"
        ):
            analyze_matched_information(changed_order, config, replicates=200)

    def test_rejects_identifier_test_or_claim_access(self) -> None:
        config = load_config(CONFIG)
        for key, value, label in (
            ("case_ids_included", True, "identifiers"),
            ("locked_test_field_case_count_read", 1, "sealed"),
            ("paper_result_or_claim", True, "claim"),
        ):
            changed = copy.deepcopy(additive_cells())
            changed["control_T"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(
                MatchedInformationAnalysisError, label
            ):
                analyze_matched_information(changed, config, replicates=200)


if __name__ == "__main__":
    unittest.main()
