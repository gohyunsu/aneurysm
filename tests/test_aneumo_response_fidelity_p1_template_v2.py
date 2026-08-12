import copy
import math
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_p1_template import (
    ResponseFidelityP1TemplateError,
)
from aurora.aneumo_response_fidelity_p1_template_v2 import (
    co_primary_screen_passes,
    load_config,
    power_law_competent,
    same_direction_seed_count,
    select_unique_iso_error_matches,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_p1_template_v2.json"


class ResponseFidelityP1TemplateV2Tests(unittest.TestCase):
    def test_v2_is_valid_inactive_and_preserves_unexecuted_v1(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(len(validate_config(config)), 11)
        self.assertFalse(config["supersession"]["v1_executed"])
        self.assertFalse(config["activation_boundary"]["p1_registered"])
        self.assertEqual(config["activation_boundary"]["real_p0_observed_check_count"], 0)
        self.assertFalse(config["current_state"]["model_prediction_read"])
        self.assertFalse(config["current_state"]["response_metric_read"])

    def test_v2_cannot_relabel_v1_or_activate_itself(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["supersession"]["v1_executed"] = True
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "supersession"):
            validate_config(config)

        config = copy.deepcopy(load_config(CONFIG))
        config["activation_boundary"]["this_file_can_be_executed"] = True
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "activation"):
            validate_config(config)

    def test_contrast_direction_or_competence_margin_cannot_change(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["baselines"]["primary_pair"]["left"] = "deltaphi_style_anchor_residual"
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "contrast direction"):
            validate_config(config)

        config = copy.deepcopy(load_config(CONFIG))
        config["field_only_selection_and_matching"][
            "power_law_field_noninferiority_margin_log_ratio"
        ] = math.log(1.05)
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "competence"):
            validate_config(config)

    def test_unique_matching_uses_three_distinct_checkpoints_per_model(self) -> None:
        values = {
            "minimum": 0.1,
            "q25": 0.1 * 2**0.25,
            "q50": 0.1 * 2**0.5,
            "q75": 0.1 * 2**0.75,
            "maximum": 0.2,
        }
        matches = select_unique_iso_error_matches(values, values)
        self.assertEqual([row.left_checkpoint for row in matches], ["q25", "q50", "q75"])
        self.assertEqual([row.right_checkpoint for row in matches], ["q25", "q50", "q75"])
        self.assertEqual(len({row.left_checkpoint for row in matches}), 3)
        self.assertEqual(len({row.right_checkpoint for row in matches}), 3)
        self.assertTrue(all(row.within_checkpoint_caliper for row in matches))

    def test_unique_matching_is_deterministic_and_fail_closed_on_caliper(self) -> None:
        left = {"a": 0.1, "b": 0.11, "c": 0.12, "d": 0.2}
        right = {"a": 0.1, "b": 0.11, "c": 0.12, "d": 0.2}
        first = select_unique_iso_error_matches(left, right)
        second = select_unique_iso_error_matches(left, right)
        self.assertEqual(first, second)
        self.assertEqual(len({row.left_checkpoint for row in first}), 3)
        self.assertTrue(any(not row.within_checkpoint_caliper for row in first))

    def test_unique_matching_returns_no_rows_without_support_or_three_checkpoints(self) -> None:
        self.assertEqual(
            select_unique_iso_error_matches({"a": 0.05, "b": 0.06}, {"a": 0.2, "b": 0.3}),
            [],
        )
        self.assertEqual(
            select_unique_iso_error_matches(
                {"a": 0.1, "b": 0.2},
                {"a": 0.1, "b": 0.15, "c": 0.2},
            ),
            [],
        )

    def test_crossfit_screen_cannot_claim_exact_p_values_or_holm(self) -> None:
        config = load_config(CONFIG)
        inference = config["inference"]
        self.assertFalse(
            inference["crossfit_family_contrasts_independent_for_exact_null_inference"]
        )
        self.assertFalse(inference["exact_sign_flip_p_value_allowed"])
        self.assertFalse(inference["holm_or_other_p_value_multiplicity_claim_allowed"])
        self.assertEqual(inference["primary_iso_error_quantile"], 0.5)
        self.assertFalse(inference["sensitivity_cells_can_rescue_primary_failure"])

    def test_power_law_competence_is_one_sided_on_model_over_control_ratio(self) -> None:
        self.assertTrue(power_law_competent(math.log(1.019)))
        self.assertTrue(power_law_competent(math.log(1.02)))
        self.assertFalse(power_law_competent(math.log(1.021)))
        self.assertTrue(power_law_competent(math.log(0.9)))

    def test_seed_direction_uses_pooled_sign_and_zero_ties_do_not_count(self) -> None:
        self.assertEqual(same_direction_seed_count(0.2, [0.1, 0.2, -0.1, 0.0, 0.3]), 3)
        self.assertEqual(same_direction_seed_count(-0.2, [-0.1, -0.2, 0.0, -0.3, -0.4]), 4)
        self.assertEqual(same_direction_seed_count(0.0, [0.1, 0.2, 0.3, 0.4, 0.5]), 0)

    def test_co_primary_screen_requires_every_v2_condition(self) -> None:
        passing = dict(
            checkpoint_qualified=True,
            field_ci_lower=-0.005,
            field_ci_upper=0.006,
            left_power_law_upper=math.log(1.01),
            right_power_law_upper=math.log(1.015),
            paired_response_log_ratio=math.log(1.2),
            paired_interval_lower=math.log(1.05),
            paired_interval_upper=math.log(1.3),
            paired_seed_contrasts=[0.1, 0.2, 0.3, 0.0, 0.4],
            tangent_response_log_ratio=math.log(1.25),
            tangent_interval_lower=math.log(1.08),
            tangent_interval_upper=math.log(1.4),
            tangent_seed_contrasts=[0.1, 0.2, 0.3, 0.4, -0.1],
        )
        self.assertTrue(co_primary_screen_passes(**passing))
        for key, value in (
            ("checkpoint_qualified", False),
            ("field_ci_upper", 0.02),
            ("left_power_law_upper", math.log(1.03)),
            ("paired_response_log_ratio", math.log(1.05)),
            ("paired_interval_lower", -0.01),
            ("tangent_interval_upper", math.inf),
            ("tangent_response_log_ratio", -math.log(1.25)),
            ("paired_seed_contrasts", [0.1, -0.2, -0.3, 0.0, -0.4]),
        ):
            changed = dict(passing)
            changed[key] = value
            self.assertFalse(co_primary_screen_passes(**changed), key)


if __name__ == "__main__":
    unittest.main()
