import unittest
from pathlib import Path

from aurora.aneug_release_730_steady_exposure_schedule import (
    SteadyExposureScheduleError,
    build_schedule_manifest,
    exposure_prefix,
    load_config,
    summarize_prefix,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_steady_exposure_schedule_v1.json"


class SteadyExposureScheduleTest(unittest.TestCase):
    def test_production_config_is_exact_and_non_executable(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["scope"]["eligible_steady_rows"], 13_985)
        self.assertFalse(config["training_boundary"]["gpu_training_authorized"])
        self.assertFalse(config["training_boundary"]["loss_weight_selected_here"])
        self.assertFalse(config["read_boundary"]["steady_wss_values_read"])

    def test_cycle_is_deterministic_exhaustive_and_balanced(self) -> None:
        indices = [1, 3, 5, 7, 9]
        prefix = exposure_prefix(indices, epochs=4, cases_per_epoch=3, seed=17)
        again = exposure_prefix(indices, epochs=4, cases_per_epoch=3, seed=17)
        changed = exposure_prefix(indices, epochs=4, cases_per_epoch=3, seed=18)
        self.assertEqual(prefix, again)
        self.assertNotEqual(prefix, changed)
        summary = summarize_prefix(prefix)
        self.assertEqual(summary["examples"], 12)
        self.assertEqual(summary["unique_rows"], 5)
        self.assertEqual(summary["minimum_visits"], 2)
        self.assertEqual(summary["maximum_visits"], 3)
        self.assertEqual(set(prefix[:5]), set(indices))
        self.assertEqual(set(prefix[5:10]), set(indices))

    def test_dense_synthetic_prefix_has_fixed_regression_digest(self) -> None:
        indices = list(range(13_985))
        prefix = exposure_prefix(indices, epochs=80, cases_per_epoch=584, seed=20_260_821)
        self.assertEqual(
            summarize_prefix(prefix),
            {
                "examples": 46_720,
                "unique_rows": 13_985,
                "minimum_visits": 3,
                "maximum_visits": 4,
                "prefix_sha256": "887b025e2d049636f2a01ae3d57104a68467e85ab4836564c1b0ffad4928a457",
            },
        )

    def test_private_scope_drift_fails_closed(self) -> None:
        config = load_config(CONFIG)
        private = {
            "schema_version": "aurora.private.aneug_release_730_steady_overlap_audit.v1",
            "any_wss_value_read": False,
            "test_wss_opened": False,
            "steady_case_names": ["a"],
            "eligible_steady_indices": [0],
            "eligible_steady_case_names": ["a"],
        }
        with self.assertRaises(SteadyExposureScheduleError):
            build_schedule_manifest(config, private)
        private["any_wss_value_read"] = True
        with self.assertRaises(SteadyExposureScheduleError):
            build_schedule_manifest(config, private)

if __name__ == "__main__":
    unittest.main()
