from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_label_efficiency import (
    Release730LabelEfficiencyError,
    balanced_epoch_indices,
    canonical_digest,
    loader_order_for_membership,
    nested_subset_memberships,
    subset_training_statistics,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_label_efficiency_v1.json"


def config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


class Release730LabelEfficiencyTests(unittest.TestCase):
    def test_config_fixes_nested_budgets_equal_compute_and_sealed_scope(self):
        value = config()
        validate_config(value)
        self.assertEqual(
            [(row["percent"], row["unique_transient_cases"]) for row in value["label_budgets"]],
            [(10, 58), (25, 146), (50, 292), (100, 584)],
        )
        self.assertEqual(
            value["training_exposure"]["transient_examples_per_reference_epoch"],
            584,
        )
        self.assertFalse(value["evaluation"]["read_locked_test"])
        self.assertFalse(value["evaluation"]["read_processed_only_extras"])

    def test_config_rejects_label_aware_selection_or_test_access(self):
        mutations = (
            ("subset_selection", "uses_geometry_or_field_values", True),
            ("training_exposure", "transient_examples_per_reference_epoch", 58),
            ("evaluation", "read_locked_test", True),
            ("evaluation", "absolute_performance_threshold", 0.25),
        )
        for section, key, replacement in mutations:
            with self.subTest(section=section, key=key):
                value = copy.deepcopy(config())
                value[section][key] = replacement
                with self.assertRaises(Release730LabelEfficiencyError):
                    validate_config(value)

    def test_memberships_are_deterministic_nested_and_input_order_independent(self):
        ids = [f"case-{index:04d}" for index in range(584)]
        forward = nested_subset_memberships(ids, config())
        reverse = nested_subset_memberships(list(reversed(ids)), config())
        self.assertEqual(forward, reverse)
        self.assertEqual([len(forward[p]) for p in (10, 25, 50, 100)], [58, 146, 292, 584])
        self.assertLessEqual(set(forward[10]), set(forward[25]))
        self.assertLessEqual(set(forward[25]), set(forward[50]))
        self.assertLessEqual(set(forward[50]), set(forward[100]))
        self.assertEqual(
            canonical_digest(forward[10]),
            "3509e5fbe9b22ea91d71da75e87c74fa819886b28a91ebe3a846471fd6071182",
        )

    def test_loader_order_is_frozen_full_order_filtered_by_membership(self):
        full = [f"case-{index:04d}" for index in range(584)]
        membership = (full[17], full[2], full[90])
        self.assertEqual(
            loader_order_for_membership(full, membership),
            (full[2], full[17], full[90]),
        )

    def test_balanced_epoch_is_deterministic_and_compute_matched(self):
        for cases in (58, 146, 292, 584):
            first = balanced_epoch_indices(
                cases, training_seed=20_260_901, epoch=7
            )
            second = balanced_epoch_indices(
                cases, training_seed=20_260_901, epoch=7
            )
            self.assertEqual(first, second)
            self.assertEqual(len(first), 584)
            counts = [first.count(index) for index in range(cases)]
            self.assertLessEqual(max(counts) - min(counts), 1)
        full = balanced_epoch_indices(584, training_seed=20_260_901, epoch=0)
        self.assertEqual(set(full), set(range(584)))

    def test_statistics_use_only_selected_records(self):
        records = [
            {"tensor": torch.zeros(2, 3, 9)},
            {"tensor": torch.ones(2, 3, 9)},
        ]
        ghd = torch.stack((torch.zeros(432), torch.full((432,), 2.0)))
        mean = torch.zeros(9)
        std = torch.ones(9)
        result = subset_training_statistics(
            records, ghd, mean, std, decoder_epsilon=0.0
        )
        self.assertEqual(result["unique_train_cases"], 2)
        torch.testing.assert_close(result["ghd_mean"], torch.ones(432))
        torch.testing.assert_close(result["ghd_std_population"], torch.ones(432))
        torch.testing.assert_close(
            result["wss_physical_mean"], torch.full((3,), 0.5, dtype=torch.float64)
        )
        torch.testing.assert_close(
            result["wss_physical_std_population"],
            torch.full((3,), 0.5, dtype=torch.float64),
        )
        self.assertAlmostEqual(result["cycle_output_scale"], (1.5) ** 0.5)
        self.assertFalse(result["validation_test_or_extra_statistics_included"])


if __name__ == "__main__":
    unittest.main()
