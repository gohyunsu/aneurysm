import copy
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_confirmation_template_v3 import (
    ConfirmationTemplateV3Error,
    METRICS,
    MODELS,
    TRAINING_SEEDS,
    evaluate_complete_error_rows,
    load_config,
    shared_family_bootstrap,
    type7_quantile,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_confirmation_template_v3.json"


class ResponseFidelityConfirmationTemplateV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)
        self.families = [f"family-{index:03d}" for index in range(100)]

    def rows(
        self,
        *,
        candidate_response: float = 0.8,
        direct_response: float = 1.0,
        power_law_response: float = 1.0,
    ) -> list[dict]:
        rows = []
        for family_id in self.families:
            for case_id in ("case-a", "case-b"):
                for seed in TRAINING_SEEDS:
                    for model in MODELS:
                        for metric in METRICS:
                            if metric == "field_relative_l2":
                                error = 1.0
                            elif model == "candidate":
                                error = candidate_response
                            elif model == "direct":
                                error = direct_response
                            else:
                                error = power_law_response
                            rows.append(
                                {
                                    "family_id": family_id,
                                    "case_id": case_id,
                                    "seed": seed,
                                    "model": model,
                                    "metric": metric,
                                    "error": error,
                                }
                            )
        return rows

    def evaluate(self, rows: list[dict], *, precision: bool = True, compute: bool = True) -> dict:
        return evaluate_complete_error_rows(
            rows,
            self.families,
            prefield_precision_viability_passed=precision,
            prefield_compute_viability_passed=compute,
            bootstrap_replicates=200,
            bootstrap_seed=2027081303,
        )

    def test_v3_is_inactive_and_supersedes_v2_before_evidence(self) -> None:
        checks = validate_config(self.config, repository_root=ROOT)
        self.assertEqual(len(checks), 15)
        self.assertFalse(self.config["supersession"]["v2_executed"])
        self.assertFalse(self.config["supersession"]["v2_confirmation_metadata_read"])
        self.assertFalse(self.config["activation_boundary"]["confirmation_registered"])
        self.assertFalse(self.config["current_state"]["paper_claim_active"])

    def test_type7_quantile_and_shared_bootstrap_are_exact_and_deterministic(self) -> None:
        self.assertEqual(type7_quantile([0.0, 10.0], 0.25), 2.5)
        first = shared_family_bootstrap(
            {"left": [0.0, 1.0, 2.0], "right": [10.0, 11.0, 12.0]},
            replicates=100,
            seed=7,
        )
        second = shared_family_bootstrap(
            {"left": [0.0, 1.0, 2.0], "right": [10.0, 11.0, 12.0]},
            replicates=100,
            seed=7,
        )
        self.assertEqual(first, second)
        self.assertAlmostEqual(
            first["right"]["lower_0_05"] - first["left"]["lower_0_05"],
            10.0,
        )
        self.assertAlmostEqual(
            first["right"]["upper_0_95"] - first["left"]["upper_0_95"],
            10.0,
        )

    def test_complete_strong_candidate_passes_every_comparator(self) -> None:
        result = self.evaluate(self.rows())
        self.assertTrue(result["complete"])
        self.assertTrue(result["passed"])
        self.assertEqual(result["selected_family_count"], 100)
        self.assertEqual(result["case_count"], 200)
        self.assertEqual(result["error_row_count"], 9000)
        for name, contrast in result["contrasts"].items():
            if name.startswith("field_"):
                self.assertAlmostEqual(contrast["one_sided_95_upper"], 0.0)
            else:
                self.assertGreaterEqual(contrast["geometric_mean_ratio"], 1.10)
                self.assertEqual(contrast["positive_seed_count"], 5)
                self.assertEqual(contrast["family_win_count"], 100)

    def test_simple_power_law_can_veto_an_apparent_direct_control_win(self) -> None:
        result = self.evaluate(
            self.rows(
                candidate_response=1.0,
                direct_response=1.2,
                power_law_response=0.9,
            )
        )
        self.assertGreater(
            result["contrasts"]["paired_response_direct_over_candidate"]["population_mean_log_contrast"],
            0.0,
        )
        self.assertLess(
            result["contrasts"]["paired_response_power_law_over_candidate"]["population_mean_log_contrast"],
            0.0,
        )
        self.assertFalse(result["passed"])

    def test_substantially_better_field_error_also_fails_the_matched_mechanism_claim(self) -> None:
        rows = self.rows()
        for row in rows:
            if row["metric"] == "field_relative_l2" and row["model"] == "candidate":
                row["error"] = 0.8
        result = self.evaluate(rows)
        self.assertLess(
            result["contrasts"]["field_candidate_over_direct"]["one_sided_95_upper"],
            0.0,
        )
        self.assertFalse(result["passed"])

    def test_large_mean_from_a_minority_of_families_cannot_pass(self) -> None:
        rows = self.rows(candidate_response=1.01, direct_response=1.0, power_law_response=1.0)
        for row in rows:
            index = int(row["family_id"].split("-")[1])
            if index < 40 and row["model"] == "candidate" and row["metric"] != "field_relative_l2":
                row["error"] = 0.1
        result = self.evaluate(rows)
        paired = result["contrasts"]["paired_response_direct_over_candidate"]
        self.assertGreater(paired["geometric_mean_ratio"], 1.10)
        self.assertEqual(paired["family_win_count"], 40)
        self.assertFalse(result["passed"])

    def test_prefield_viability_is_noncompensatory(self) -> None:
        self.assertFalse(self.evaluate(self.rows(), precision=False)["passed"])
        self.assertFalse(self.evaluate(self.rows(), compute=False)["passed"])

    def test_missing_duplicate_extra_or_analytic_seed_drift_fails_closed(self) -> None:
        base = self.rows()
        malformed = [
            base[:-1],
            base + [copy.deepcopy(base[0])],
        ]
        extra = copy.deepcopy(base)
        extra[0]["family_id"] = "not-in-manifest"
        malformed.append(extra)
        drift = copy.deepcopy(base)
        target = next(
            row
            for row in drift
            if row["model"] == "power_law"
            and row["metric"] == "paired_response_relative_l2"
            and row["seed"] == TRAINING_SEEDS[-1]
        )
        target["error"] = 1.01
        malformed.append(drift)
        for rows in malformed:
            with self.assertRaises(ConfirmationTemplateV3Error):
                self.evaluate(rows)

    def test_contract_mutations_fail_closed(self) -> None:
        mutations = (
            ("supersession", "v2_confirmation_field_read", True),
            ("activation_boundary", "this_file_can_be_executed", True),
            ("prefield_viability", "all_four_response_contrasts_must_pass_precision_gate", False),
            ("deterministic_family_bootstrap", "quantile_method", "nearest"),
            ("primary_comparators_and_pass", "analytic_control_can_be_omitted_or_demoted_after_failure", True),
            ("interpretable_figure", "favorable_only_case_or_comparator_selection_allowed", True),
            ("stopping_and_claim_deletion", "partial_aggregation_allowed", True),
        )
        for section, key, value in mutations:
            changed = copy.deepcopy(self.config)
            changed[section][key] = value
            with self.assertRaises(ConfirmationTemplateV3Error):
                validate_config(changed, repository_root=ROOT)


if __name__ == "__main__":
    unittest.main()
