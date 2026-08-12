import copy
import math
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_p1_template import (
    ResponseFidelityP1TemplateError,
    exact_two_sided_sign_flip_pvalue,
    field_equivalent,
    holm_rejections,
    load_config,
    response_mismatch_cell_passes,
    select_iso_error_matches,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_p1_template_v1.json"


class ResponseFidelityP1TemplateTests(unittest.TestCase):
    def test_template_is_valid_but_inactive(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(len(validate_config(config)), 8)
        self.assertFalse(config["activation_boundary"]["p1_registered"])
        self.assertIsNone(config["activation_boundary"]["real_p0_observed_verdict"])
        self.assertEqual(config["activation_boundary"]["real_p0_observed_check_count"], 0)
        self.assertFalse(config["compute_matching"]["gpu_authorized_now"])
        self.assertFalse(config["current_state"]["model_prediction_read"])
        self.assertFalse(config["current_state"]["response_metric_read"])

    def test_template_cannot_activate_itself_or_claim_a_p0_pass(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["activation_boundary"]["this_file_can_be_executed"] = True
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "activation"):
            validate_config(config)

        config = copy.deepcopy(load_config(CONFIG))
        config["activation_boundary"]["real_p0_observed_verdict"] = "pass_all_11_checks"
        config["activation_boundary"]["real_p0_observed_check_count"] = 11
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "activation"):
            validate_config(config)

    def test_validation_test_or_junjinyong_access_cannot_be_enabled(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["data_boundary"]["historical_validation_families_read"] = True
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "sealed-data"):
            validate_config(config)

        config = copy.deepcopy(load_config(CONFIG))
        config["compute_matching"]["junjinyong_allowed"] = True
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "compute-matching"):
            validate_config(config)

    def test_matching_margin_or_pair_cannot_be_silently_changed(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["field_only_selection_and_matching"][
            "outer_field_equivalence_margin_log_ratio"
        ] = math.log(1.05)
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "field matching"):
            validate_config(config)

        config = copy.deepcopy(load_config(CONFIG))
        config["baselines"]["primary_pairs_in_order"].reverse()
        config["baselines"]["primary_pairs_in_order"].append(
            ["deeponet_anchor_conditioned", "deltaphi_style_anchor_residual"]
        )
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "pair family"):
            validate_config(config)

    def test_iso_error_matching_uses_only_common_field_support(self) -> None:
        left = {f"c{i}": 0.20 - i * 0.005 for i in range(20)}
        right = {f"c{i}": 0.205 - i * 0.005 for i in range(20)}
        matches = select_iso_error_matches(
            left,
            right,
            maximum_log_distance=math.log(1.03),
        )
        self.assertEqual([row.quantile for row in matches], [0.25, 0.5, 0.75])
        self.assertTrue(all(row.within_checkpoint_caliper for row in matches))
        self.assertTrue(all(row.left_checkpoint in left for row in matches))
        self.assertTrue(all(row.right_checkpoint in right for row in matches))

    def test_iso_error_matching_returns_no_rows_without_overlap(self) -> None:
        self.assertEqual(
            select_iso_error_matches({"a": 0.05, "b": 0.06}, {"a": 0.2, "b": 0.3}),
            [],
        )

    def test_field_equivalence_requires_complete_interval_inside_margin(self) -> None:
        self.assertTrue(field_equivalent(-0.009, 0.008))
        self.assertFalse(field_equivalent(-0.011, 0.008))
        self.assertFalse(field_equivalent(-0.005, 0.012))

    def test_holm_step_down_stops_after_first_non_rejection(self) -> None:
        rejected = holm_rejections([0.001, 0.02, 0.03, 0.9], alpha=0.05)
        self.assertEqual(rejected, [True, False, False, False])
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "Holm"):
            holm_rejections([0.01, -0.1])

    def test_exact_sign_flip_uses_family_as_the_unit(self) -> None:
        self.assertEqual(exact_two_sided_sign_flip_pvalue([1.0, 1.0, 1.0]), 0.25)
        self.assertEqual(exact_two_sided_sign_flip_pvalue([0.0, 0.0]), 1.0)
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "sign-flip"):
            exact_two_sided_sign_flip_pvalue([])

    def test_response_cell_needs_equivalence_materiality_multiplicity_and_four_seeds(self) -> None:
        passing = dict(
            field_ci_lower=-0.005,
            field_ci_upper=0.007,
            response_log_ratio=math.log(1.2),
            response_ci_lower=math.log(1.05),
            response_ci_upper=math.log(1.3),
            holm_rejected=True,
            same_direction_seed_count=4,
        )
        self.assertTrue(response_mismatch_cell_passes(**passing))
        for key, value in (
            ("field_ci_upper", 0.02),
            ("response_log_ratio", math.log(1.05)),
            ("response_ci_lower", -0.01),
            ("holm_rejected", False),
            ("same_direction_seed_count", 3),
        ):
            changed = dict(passing)
            changed[key] = value
            self.assertFalse(response_mismatch_cell_passes(**changed), key)


if __name__ == "__main__":
    unittest.main()
