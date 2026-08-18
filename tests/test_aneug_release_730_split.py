from __future__ import annotations

import json
import unittest

try:
    import torch
except ImportError:
    torch = None

from aurora.aneug_release_730_split import (
    Release730SplitError,
    _schema_record_matches,
    build_grouped_split,
)


@unittest.skipIf(torch is None, "PyTorch is optional in the local lightweight environment")
class AneuGRelease730SplitTests(unittest.TestCase):
    def fixture(self):
        release = [f"stable_{index}" for index in range(730)]
        extras = [f"named_{index}" for index in range(79)]
        case_ids = release + extras
        rows = torch.arange(809, dtype=torch.float32)[:, None].repeat(1, 432)
        return release, case_ids, rows

    def test_exact_release_intersection_and_584_73_73_partition(self):
        release, case_ids, rows = self.fixture()
        public, private = build_grouped_split(
            case_ids, case_ids, rows, release, bytes(range(32)), torch
        )
        self.assertEqual(public["processed_case_count"], 809)
        self.assertEqual(public["release_case_count"], 730)
        self.assertEqual(public["processed_extra_case_count"], 79)
        self.assertEqual(
            (public["train_case_count"], public["validation_case_count"], public["test_case_count"]),
            (584, 73, 73),
        )
        self.assertTrue(public["validation_target_exact"])
        self.assertTrue(public["test_target_exact"])
        self.assertFalse(public["test_opened"])
        self.assertFalse(public["registered_field_values_read"])
        self.assertNotIn("stable_0", json.dumps(public))
        assigned = {
            case_id
            for split in ("train_components", "validation_components", "test_components")
            for component in private[split]
            for case_id in component["case_ids"]
        }
        self.assertEqual(assigned, set(release))

    def test_duplicate_geometry_never_crosses_splits(self):
        release, case_ids, rows = self.fixture()
        rows[1] = rows[0]
        public, private = build_grouped_split(
            case_ids, case_ids, rows, release, b"x" * 32, torch
        )
        self.assertEqual(public["exact_duplicate_component_count"], 1)
        assignments = {}
        for split in ("train_components", "validation_components", "test_components"):
            for component in private[split]:
                for case_id in component["case_ids"]:
                    assignments[case_id] = split
        self.assertEqual(assignments["stable_0"], assignments["stable_1"])

    def test_missing_release_case_or_wrong_mesh_order_is_rejected(self):
        release, case_ids, rows = self.fixture()
        with self.assertRaisesRegex(Release730SplitError, "mesh_case_order"):
            build_grouped_split(case_ids, list(reversed(case_ids)), rows, release, b"x" * 32, torch)
        with self.assertRaisesRegex(Release730SplitError, "release_case_missing"):
            invalid = release[:-1] + ["stable_999999"]
            build_grouped_split(case_ids, case_ids, rows, invalid, b"x" * 32, torch)

    def test_public_result_contains_no_identifiers_or_fields(self):
        release, case_ids, rows = self.fixture()
        public, _ = build_grouped_split(
            case_ids, case_ids, rows, release, b"z" * 32, torch
        )
        serialized = json.dumps(public, sort_keys=True)
        self.assertFalse(public["registered_field_values_read"])
        self.assertFalse(public["test_opened"])
        self.assertNotIn("stable_", serialized)

    def test_schema_guard_uses_exact_emitted_mesh_order_key(self):
        record = {
            "schema_pass": True,
            "registered_case_count": 809,
            "mesh_case_count": 809,
            "tensor_shape": [80, 13_902, 9],
            "mesh_order_exact": True,
        }
        self.assertTrue(_schema_record_matches(record))
        record["mesh_case_order_exact"] = record.pop("mesh_order_exact")
        self.assertFalse(_schema_record_matches(record))


if __name__ == "__main__":
    unittest.main()
