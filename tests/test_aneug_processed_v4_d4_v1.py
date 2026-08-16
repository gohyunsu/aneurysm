from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d4_v1 import (
    D4ContractError,
    census_loaded_metadata,
    load_contract,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d4_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d4_v1.pbs"


class MetadataOnlyTensor:
    def __init__(self, shape: tuple[int, ...], dtype: str = "torch.float32") -> None:
        self.shape = shape
        self.dtype = dtype

    def __getitem__(self, key: object) -> object:
        raise AssertionError("tensor values must not be indexed")

    def __iter__(self) -> object:
        raise AssertionError("tensor values must not be iterated")

    def numpy(self) -> object:
        raise AssertionError("tensor values must not be materialized")

    def tolist(self) -> object:
        raise AssertionError("tensor values must not be converted")


def fixtures() -> tuple[dict[str, object], dict[str, object]]:
    transient = {
        "registered_data_list": [
            {"case": "synthetic_alpha", "labels": ["wss_x", "wss_y", "wss_z"], "tensor": MetadataOnlyTensor((80, 128, 3))},
            {"case": "synthetic_beta", "labels": ["wss_x", "wss_y", "wss_z"], "tensor": MetadataOnlyTensor((80, 128, 3))},
        ],
        "mesh_data": {
            "cases": ["synthetic_alpha", "synthetic_beta"],
            "idx_list": [MetadataOnlyTensor((64,), "torch.int64")],
            "edge_index_list": [MetadataOnlyTensor((2, 512), "torch.int64")],
            "faces_list": [MetadataOnlyTensor((256, 3), "torch.int64")],
            "ghd": MetadataOnlyTensor((2, 10, 3)),
            "shape_scale": MetadataOnlyTensor((2, 1)),
        },
    }
    steady = {
        "label": ["wss_x", "wss_y", "wss_z"],
        "tensor_norm": {"mean": MetadataOnlyTensor((3,)), "std": MetadataOnlyTensor((3,))},
    }
    return transient, steady


class AneuGProcessedV4D4Tests(unittest.TestCase):
    def test_selected_fresh_contract_is_cpu_only_and_one_shot(self) -> None:
        contract = load_contract(CONFIG)
        self.assertTrue(contract["human_selection"]["explicitly_selected"])
        self.assertEqual(contract["human_selection"]["selection"], "D4")
        self.assertEqual(contract["execution"]["ngpus"], 0)
        self.assertEqual(contract["execution"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["execution"]["rerun_after_any_outcome"])

    def test_d3_is_immutable_and_d4_has_no_threshold(self) -> None:
        contract = load_contract(CONFIG)
        self.assertFalse(contract["closed_d3_boundary"]["post_hoc_backfill"])
        self.assertFalse(contract["closed_d3_boundary"]["d4_is_d3_retry_or_repair"])
        self.assertIsNone(contract["census_contract"]["cardinality_pass_threshold"])
        self.assertTrue(contract["completion_consequence"]["permits_human_rescoring_only"])

    def test_census_reads_only_metadata_and_keeps_ids_private(self) -> None:
        contract = load_contract(CONFIG)
        transient, steady = fixtures()
        public, private = census_loaded_metadata(contract, transient, steady)
        self.assertEqual(public["registered_case_count"], 2)
        self.assertFalse(public["geometry_linkage_evaluated"])
        self.assertIsNone(public["geometry_linked_count"])
        self.assertTrue(public["mesh_case_order_exact"])
        self.assertFalse(public["tensor_values_read"])
        self.assertFalse(public["mesh_connectivity_values_read"])
        self.assertIsNone(public["scientific_verdict"])
        serialized = json.dumps(public)
        self.assertNotIn("synthetic_alpha", serialized)
        self.assertEqual(private["ordered_case_ids"], ["synthetic_alpha", "synthetic_beta"])

    def test_defects_are_descriptive_not_pass_fail(self) -> None:
        contract = load_contract(CONFIG)
        transient, steady = fixtures()
        transient["registered_data_list"] = [
            {"case": "dup", "labels": ["x"], "tensor": MetadataOnlyTensor((79, 8, 1))},
            {"case": "dup", "labels": ["x"], "tensor": None},
            {"case": "", "labels": [], "tensor": MetadataOnlyTensor((80, 8, 1))},
        ]
        transient["mesh_data"]["cases"] = ["dup"]
        public, _ = census_loaded_metadata(contract, transient, steady)
        self.assertEqual(public["duplicate_case_id_count"], 1)
        self.assertEqual(public["blank_case_id_count"], 1)
        self.assertEqual(public["tensor_metadata_missing_count"], 1)
        self.assertIsNone(public["cardinality_pass_threshold"])
        self.assertIsNone(public["scientific_verdict"])

    def test_scope_gpu_rerun_and_claim_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("census_contract", "cardinality_pass_threshold", 600, "cardinality_threshold"),
            ("census_contract", "read_tensor_values", True, "read_tensor_values"),
            ("census_contract", "read_mesh_connectivity_values", True, "read_mesh_connectivity_values"),
            ("execution", "ngpus", 1, "resources"),
            ("execution", "rerun_after_any_outcome", True, "rerun"),
            ("authorization", "paper_result_or_claim", True, "paper_result_or_claim"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            candidate[section][key] = value
            with self.assertRaisesRegex(D4ContractError, reason):
                validate_contract(candidate)

    def test_pbs_enforces_clean_exact_cpu_only_single_attempt(self) -> None:
        text = PBS.read_text(encoding="utf-8")
        self.assertIn("select=1:ncpus=4:mem=64gb:ngpus=0", text)
        self.assertIn("status --porcelain", text)
        self.assertIn("attempt.started", text)
        self.assertIn("rerun is forbidden", text)
        self.assertNotIn("rm -f \"$steady\"", text)
        self.assertNotIn("nvidia-smi", text)


if __name__ == "__main__":
    unittest.main()
