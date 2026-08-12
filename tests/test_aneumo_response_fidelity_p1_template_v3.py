import copy
import math
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_p1_template import (
    ResponseFidelityP1TemplateError,
)
from aurora.aneumo_response_fidelity_p1_template_v3 import (
    directed_co_primary_screen_passes,
    load_config,
    positive_seed_count,
    select_unique_iso_error_matches,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_p1_template_v3.json"


class ResponseFidelityP1TemplateV3Tests(unittest.TestCase):
    def test_v3_is_inactive_and_preserves_unexecuted_v2(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(len(validate_config(config)), 12)
        self.assertFalse(config["supersession"]["v2_executed"])
        self.assertFalse(config["activation_boundary"]["p1_registered"])
        self.assertEqual(config["activation_boundary"]["real_p0_observed_check_count"], 0)
        self.assertFalse(config["current_state"]["model_prediction_read"])
        self.assertFalse(config["current_state"]["response_metric_read"])

    def test_new_direct_priors_are_controls_not_novelty(self) -> None:
        config = load_config(CONFIG)
        sources = config["source_reappraisal"]
        self.assertFalse(sources["architecture_component_can_be_claimed_as_novelty"])
        self.assertFalse(sources["hemo_mpo"]["public_code_repository_identified"])
        self.assertEqual(sources["ab_gatr"]["exact_experiment_release_status"], "coming_soon")
        self.assertEqual(sources["lab_gatr"]["repository_license_spdx"], "MIT")

    def test_primary_pair_controls_backbone_and_fixes_beneficial_direction(self) -> None:
        config = load_config(CONFIG)
        primary = config["baseline_contract"]["primary_pair"]
        self.assertTrue(primary["all_non_output_parameterization_settings_identical"])
        self.assertEqual(primary["shared_backbone"], "lab_gatr_anchor_conditioned")
        self.assertIn("residual_has_lower", primary["required_positive_direction"])
        self.assertFalse(config["inference"]["negative_direction_can_pass"])

        changed = copy.deepcopy(config)
        changed["baseline_contract"]["primary_pair"]["shared_backbone"] = "meshgraphnet"
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "primary pair"):
            validate_config(changed)

    def test_checkpoint_matching_remains_duplicate_free(self) -> None:
        values = {
            "minimum": 0.1,
            "q25": 0.1 * 2**0.25,
            "q50": 0.1 * 2**0.5,
            "q75": 0.1 * 2**0.75,
            "maximum": 0.2,
        }
        rows = select_unique_iso_error_matches(values, values)
        self.assertEqual(len({row.left_checkpoint for row in rows}), 3)
        self.assertEqual(len({row.right_checkpoint for row in rows}), 3)

    def test_positive_seed_count_excludes_zero_and_negative(self) -> None:
        self.assertEqual(positive_seed_count([0.1, 0.2, 0.0, -0.1, 0.3]), 3)
        with self.assertRaises(ResponseFidelityP1TemplateError):
            positive_seed_count([0.1, 0.2])

    def test_directed_screen_accepts_only_prespecified_residual_benefit(self) -> None:
        passing = dict(
            checkpoint_qualified=True,
            field_ci_lower=-0.005,
            field_ci_upper=0.006,
            direct_power_law_upper=math.log(1.01),
            residual_power_law_upper=math.log(1.015),
            paired_response_log_ratio=math.log(1.2),
            paired_interval_lower=math.log(1.05),
            paired_interval_upper=math.log(1.3),
            paired_seed_contrasts=[0.1, 0.2, 0.3, 0.0, 0.4],
            tangent_response_log_ratio=math.log(1.25),
            tangent_interval_lower=math.log(1.08),
            tangent_interval_upper=math.log(1.4),
            tangent_seed_contrasts=[0.1, 0.2, 0.3, 0.4, -0.1],
        )
        self.assertTrue(directed_co_primary_screen_passes(**passing))

        reverse = dict(passing)
        reverse["paired_response_log_ratio"] = -math.log(1.2)
        reverse["paired_interval_lower"] = -math.log(1.3)
        reverse["paired_interval_upper"] = -math.log(1.05)
        reverse["paired_seed_contrasts"] = [-0.1, -0.2, -0.3, 0.0, -0.4]
        self.assertFalse(directed_co_primary_screen_passes(**reverse))

    def test_every_directed_gate_is_non_rescuing(self) -> None:
        passing = dict(
            checkpoint_qualified=True,
            field_ci_lower=-0.005,
            field_ci_upper=0.006,
            direct_power_law_upper=math.log(1.01),
            residual_power_law_upper=math.log(1.015),
            paired_response_log_ratio=math.log(1.2),
            paired_interval_lower=math.log(1.05),
            paired_interval_upper=math.log(1.3),
            paired_seed_contrasts=[0.1, 0.2, 0.3, 0.0, 0.4],
            tangent_response_log_ratio=math.log(1.25),
            tangent_interval_lower=math.log(1.08),
            tangent_interval_upper=math.log(1.4),
            tangent_seed_contrasts=[0.1, 0.2, 0.3, 0.4, -0.1],
        )
        for key, value in (
            ("checkpoint_qualified", False),
            ("field_ci_upper", 0.02),
            ("direct_power_law_upper", math.log(1.03)),
            ("paired_response_log_ratio", math.log(1.05)),
            ("paired_interval_lower", 0.0),
            ("tangent_interval_upper", math.inf),
            ("paired_seed_contrasts", [0.1, -0.2, -0.3, 0.0, -0.4]),
        ):
            changed = dict(passing)
            changed[key] = value
            self.assertFalse(directed_co_primary_screen_passes(**changed), key)

    def test_bounded_development_cannot_be_opened_or_expanded(self) -> None:
        config = load_config(CONFIG)
        self.assertFalse(config["bounded_development_after_p1_pass"]["authorized_now"])
        self.assertEqual(config["bounded_development_after_p1_pass"]["maximum_repair_rounds"], 2)
        self.assertEqual(config["bounded_development_after_p1_pass"]["maximum_additional_gpu_hours"], 80.0)

        changed = copy.deepcopy(config)
        changed["bounded_development_after_p1_pass"]["maximum_repair_rounds"] = 3
        with self.assertRaisesRegex(ResponseFidelityP1TemplateError, "bounded development"):
            validate_config(changed)


if __name__ == "__main__":
    unittest.main()
