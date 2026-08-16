from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d4 import (
    D4DraftContractError,
    assert_execution_authorized,
    census_loaded_metadata,
    load_draft_contract,
    validate_draft_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d4_draft.json"


class MetadataOnlyTensor:
    def __init__(self, shape: tuple[int, ...], dtype: str = "torch.float32") -> None:
        self.shape = shape
        self.dtype = dtype

    def __getitem__(self, key: object) -> object:
        raise AssertionError("tensor values must not be indexed")

    def numpy(self) -> object:
        raise AssertionError("tensor values must not be materialized")

    def tolist(self) -> object:
        raise AssertionError("tensor values must not be converted")


class AneuGProcessedV4D4DraftTests(unittest.TestCase):
    def test_draft_is_valid_unselected_and_non_executable(self) -> None:
        contract = load_draft_contract(CONFIG)
        self.assertFalse(contract["human_selection"]["explicitly_selected"])
        self.assertTrue(all(value is False for value in contract["authorization"].values()))
        with self.assertRaisesRegex(D4DraftContractError, "draft_non_executable"):
            assert_execution_authorized(contract)

    def test_d3_failure_is_immutable_and_no_threshold_is_added(self) -> None:
        contract = load_draft_contract(CONFIG)
        self.assertFalse(contract["closed_d3_boundary"]["post_hoc_backfill"])
        self.assertFalse(contract["closed_d3_boundary"]["d4_relabels_d3"])
        self.assertIsNone(contract["census_contract"]["cardinality_pass_threshold"])
        self.assertTrue(
            contract["completion_consequence_if_selected"]["permits_human_rescoring_only"]
        )

    def test_pure_census_uses_metadata_and_keeps_ids_private(self) -> None:
        contract = load_draft_contract(CONFIG)
        transient = {
            "registered_data_list": [
                {
                    "case": "synthetic_case_alpha",
                    "labels": ["x", "y", "z", "wss_x", "wss_y", "wss_z"],
                    "tensor": MetadataOnlyTensor((80, 1024, 6)),
                },
                {
                    "case": "synthetic_case_beta",
                    "labels": ["x", "y", "z", "wss_x", "wss_y", "wss_z"],
                    "tensor": MetadataOnlyTensor((80, 1024, 6)),
                },
            ],
            "mesh_data": {"cases": ["synthetic_case_alpha", "synthetic_case_beta"]},
        }
        steady = {
            "label": ["x", "y", "z", "wss_x", "wss_y", "wss_z"],
            "tensor_norm": {
                "mean": MetadataOnlyTensor((6,)),
                "std": MetadataOnlyTensor((6,)),
            },
        }
        public, private = census_loaded_metadata(contract, transient, steady)
        self.assertEqual(public["registered_case_count"], 2)
        self.assertTrue(public["mesh_case_order_exact"])
        self.assertFalse(public["tensor_values_read"])
        self.assertFalse(public["scientific_verdict"])
        self.assertNotIn("synthetic_case_alpha", json.dumps(public))
        self.assertEqual(
            private["ordered_case_ids"],
            ["synthetic_case_alpha", "synthetic_case_beta"],
        )

    def test_descriptive_census_records_defects_without_scientific_verdict(self) -> None:
        contract = load_draft_contract(CONFIG)
        transient = {
            "registered_data_list": [
                {"case": "duplicate_case", "labels": ["x"], "tensor": MetadataOnlyTensor((79, 8, 1))},
                {"case": "duplicate_case", "labels": ["x"], "tensor": None},
                {"case": "", "labels": [], "tensor": MetadataOnlyTensor((80, 8, 1))},
            ],
            "mesh_data": {"cases": ["duplicate_case"]},
        }
        steady = {
            "label": ["x"],
            "tensor_norm": {
                "mean": MetadataOnlyTensor((1,)),
                "std": MetadataOnlyTensor((1,)),
            },
        }
        public, _ = census_loaded_metadata(contract, transient, steady)
        self.assertEqual(public["duplicate_case_id_count"], 1)
        self.assertEqual(public["blank_case_id_count"], 1)
        self.assertEqual(public["tensor_metadata_missing_count"], 1)
        self.assertFalse(public["mesh_case_order_exact"])
        self.assertIsNone(public["cardinality_pass_threshold"])
        self.assertFalse(public["scientific_field_metric_computed"])

    def test_scope_expansion_and_draft_activation_are_rejected(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("human_selection", "explicitly_selected", True, "human_selection"),
            ("census_contract", "cardinality_pass_threshold", 600, "cardinality_threshold"),
            ("census_contract", "read_tensor_values", True, "read_tensor_values"),
            ("execution_envelope_if_selected_in_fresh_version", "ngpus", 1, "gpu"),
            ("authorization", "read_processed_payload", True, "authorization"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            candidate[section][key] = value
            with self.assertRaisesRegex(D4DraftContractError, reason):
                validate_draft_contract(candidate)


if __name__ == "__main__":
    unittest.main()
