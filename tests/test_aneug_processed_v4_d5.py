from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d5 import (
    D5DraftContractError,
    assert_execution_authorized,
    audit_loaded_geometry_tokens,
    load_draft_contract,
    validate_draft_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d5_draft.json"


class AneuGProcessedV4D5DraftTests(unittest.TestCase):
    def test_draft_is_unselected_and_refuses_execution(self) -> None:
        contract = load_draft_contract(CONFIG)
        self.assertFalse(contract["human_selection"]["explicitly_selected"])
        self.assertTrue(all(value is False for value in contract["authorization"].values()))
        with self.assertRaisesRegex(D5DraftContractError, "draft_non_executable"):
            assert_execution_authorized(contract)

    def test_external_geometry_join_is_not_reintroduced_as_a_gate(self) -> None:
        contract = load_draft_contract(CONFIG)
        builder = contract["official_builder_semantics"]
        scope = contract["geometry_token_contract"]
        self.assertTrue(builder["ghd_loaded_from_each_transient_case_checkpoint"])
        self.assertFalse(builder["external_geometry_directory_join_required_for_processed_input"])
        self.assertEqual(scope["allowed_value_read"], "mesh_data.ghd_only")
        self.assertFalse(scope["read_registered_case_tensor_values"])
        self.assertFalse(scope["read_wss_values"])

    def test_pure_geometry_grouping_keeps_duplicates_together_and_ids_private(self) -> None:
        contract = load_draft_contract(CONFIG)
        case_ids = [
            "stable_10",
            "stable_11",
            "stable_12",
            "stable_13",
            "named_shape_1",
        ]
        rows = [
            [0.0, 1.0, 2.0],
            [0.0, 1.0, 2.0],
            [1.0, 2.0, 3.0],
            [2.0, 3.0, 4.0],
            [3.0, 4.0, 5.0],
        ]
        public, private = audit_loaded_geometry_tokens(contract, case_ids, case_ids, rows)
        self.assertEqual(public["exact_duplicate_component_count"], 1)
        self.assertEqual(public["primary_component_count"], 3)
        self.assertEqual(public["auxiliary_case_count"], 1)
        self.assertFalse(public["external_geometry_directory_join_used"])
        self.assertFalse(public["registered_field_values_read"])
        self.assertIsNone(public["scientific_verdict"])
        self.assertFalse(public["split_feasible_under_draft_contract"])
        public_text = json.dumps(public, sort_keys=True)
        self.assertTrue(all(case_id not in public_text for case_id in case_ids))
        assigned = (
            private["train_case_ids"]
            + private["validation_case_ids"]
            + private["outer_test_case_ids"]
        )
        self.assertEqual(set(assigned), set(case_ids[:4]))
        locations = {
            split: set(private[f"{split}_case_ids"])
            for split in ("train", "validation", "outer_test")
        }
        duplicate_locations = [
            split for split, members in locations.items() if {"stable_10", "stable_11"} <= members
        ]
        self.assertEqual(len(duplicate_locations), 1)

    def test_order_nonfinite_and_scope_expansion_fail_closed(self) -> None:
        contract = load_draft_contract(CONFIG)
        with self.assertRaisesRegex(D5DraftContractError, "case_mesh_order"):
            audit_loaded_geometry_tokens(
                contract,
                ["stable_1", "stable_2"],
                ["stable_2", "stable_1"],
                [[0.0], [1.0]],
            )
        public, _ = audit_loaded_geometry_tokens(
            contract,
            ["stable_1"],
            ["stable_1"],
            [[math.nan]],
        )
        self.assertEqual(public["finite_row_count"], 0)
        self.assertFalse(public["split_feasible_under_draft_contract"])

        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("human_selection", "explicitly_selected", True, "human_selection"),
            ("geometry_token_contract", "read_wss_values", True, "read_wss_values"),
            (
                "geometry_token_contract",
                "allowed_value_read",
                "registered_data_list.tensor",
                "allowed_value_read",
            ),
            ("execution_envelope_if_selected_in_fresh_version", "ngpus", 1, "gpu"),
            ("authorization", "read_processed_ghd_values", True, "authorization"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            candidate[section][key] = value
            with self.assertRaisesRegex(D5DraftContractError, reason):
                validate_draft_contract(candidate)


if __name__ == "__main__":
    unittest.main()
