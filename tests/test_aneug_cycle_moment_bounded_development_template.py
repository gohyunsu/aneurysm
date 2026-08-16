from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from aurora.aneug_cycle_moment_bounded_development_template import (
    BoundedDevelopmentTemplateError,
    load_contract,
    main,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_cycle_moment_bounded_development_template_v1.json"


class AneuGCycleMomentBoundedDevelopmentTemplateTests(unittest.TestCase):
    def test_template_is_conditional_and_non_executable(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(
            contract["status"],
            "conditional_on_future_d7_pass_unselected_non_executable",
        )
        self.assertFalse(
            contract["activation_preconditions"]["d7_selected_executed_and_complete_pass"]
        )
        self.assertTrue(
            contract["activation_preconditions"][
                "fresh_development_contract_required_after_d7_pass"
            ]
        )
        self.assertTrue(all(not value for value in contract["current_authorization"].values()))
        with self.assertRaisesRegex(BoundedDevelopmentTemplateError, "non_executable_template"):
            main(["--config", str(CONFIG)])

    def test_compute_round_and_seed_caps_are_exact(self) -> None:
        contract = load_contract(CONFIG)
        budget = contract["resource_budget"]
        self.assertEqual(sum(budget["round_caps_gpu_hours"].values()), 360)
        self.assertEqual(budget["maximum_repair_rounds"], 1)
        self.assertEqual(budget["maximum_accepted_attempts_per_variant_seed"], 1)
        self.assertFalse(budget["same_variant_seed_resubmission_after_accepted_job"])
        self.assertTrue(budget["round_caps_are_nonfungible"])
        self.assertEqual(
            contract["rounds"]["R1"]["primary_pair_seeds"],
            [1103, 2207, 3301, 4409, 5501],
        )
        self.assertEqual(
            contract["rounds"]["R2"]["fresh_primary_pair_seeds"],
            [6607, 7703, 8807, 9901, 11113],
        )
        self.assertFalse(contract["rounds"]["R2"]["second_repair_round_allowed"])

    def test_outer_and_scientific_conjunction_are_fail_closed(self) -> None:
        contract = load_contract(CONFIG)
        c0 = contract["rounds"]["C0"]
        self.assertEqual(c0["outer_attempt_limit"], 1)
        self.assertFalse(c0["training_allowed"])
        self.assertFalse(c0["outer_rerun_repair_or_relabel"])
        selection = contract["selection_and_confirmation"]
        self.assertEqual(selection["field_noninferiority_upper_ratio"], 1.02)
        self.assertEqual(selection["tawss_point_ratio_maximum"], 0.95)
        self.assertEqual(selection["osi_point_ratio_maximum"], 0.95)
        self.assertEqual(
            (selection["minimum_positive_primary_pair_seeds"], selection["primary_pair_seed_count"]),
            (4, 5),
        )
        self.assertTrue(
            selection["all_field_tawss_osi_and_seed_conditions_form_one_conjunction"]
        )

    def test_activation_budget_repair_and_outer_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("status", None, "active", "status"),
            ("activation_preconditions", "current_gpu_or_model_authority", True, "current_authority"),
            ("immutable_data_boundary", "outer_values_sealed_until_one_shot_confirmation", False, "data"),
            ("resource_budget", "maximum_total_gpu_hours", 720, "total_budget"),
            ("resource_budget", "maximum_repair_rounds", 2, "repair_cap"),
            ("resource_budget", "same_variant_seed_resubmission_after_accepted_job", True, "variant_resubmission"),
            ("runtime_lock", "no_gpu_model_assumed_before_smoke", False, "runtime"),
            ("rounds.R2", "second_repair_round_allowed", True, "R2_only"),
            ("rounds.C0", "outer_attempt_limit", 2, "C0_attempt"),
            ("selection_and_confirmation", "field_noninferiority_upper_ratio", 1.05, "field_margin"),
            ("current_authorization", "submit_gpu_smoke_or_training", True, "current_authorization"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            if section == "status":
                candidate[section] = value
            elif "." in section:
                first, second = section.split(".", 1)
                candidate[first][second][key] = value
            else:
                candidate[section][key] = value
            with self.assertRaisesRegex(BoundedDevelopmentTemplateError, reason):
                validate_contract(candidate)


if __name__ == "__main__":
    unittest.main()
