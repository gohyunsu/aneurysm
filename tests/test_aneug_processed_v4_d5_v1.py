from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # public CI and introai9 provide pinned PyTorch
    torch = None

from aurora.aneug_processed_v4_d5_v1 import (
    D5ContractError,
    audit_loaded_geometry_tokens,
    load_contract,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d5_v1.json"
DRAFT = ROOT / "configs" / "aneug_processed_v4_d5_draft.json"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d5_v1.pbs"


def small_fixture() -> tuple[list[str], object]:
    if torch is None:
        raise RuntimeError("PyTorch fixture requested without PyTorch")
    ids = [
        "stable_1",
        "stable_2",
        "stable_3",
        "stable_4",
        "stable_5",
        "stable_6",
        "named_alpha",
        "named_beta",
    ]
    rows = torch.stack(
        [
            torch.zeros(432),
            torch.zeros(432),
            torch.full((432,), 0.1),
            torch.full((432,), 0.1) + 5.0e-8,
            torch.full((432,), 2.0),
            torch.full((432,), 3.0),
            torch.full((432,), 3.0),
            torch.full((432,), 4.0),
        ]
    ).to(torch.float32)
    return ids, rows


class AneuGProcessedV4D5Tests(unittest.TestCase):
    def test_selected_fresh_contract_is_cpu_only_and_one_shot(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["human_selection"]["selection"], "D5")
        self.assertTrue(contract["human_selection"]["explicitly_selected"])
        self.assertEqual(contract["geometry_token_contract"]["allowed_value_read"], "mesh_data.ghd_only")
        self.assertEqual(contract["execution"]["ngpus"], 0)
        self.assertEqual(contract["execution"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["execution"]["rerun_after_any_outcome"])

    def test_dormant_draft_remains_unselected_and_immutable(self) -> None:
        draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        self.assertEqual(draft["status"], "draft_unselected_non_executable")
        self.assertFalse(draft["human_selection"]["explicitly_selected"])
        self.assertTrue(all(value is False for value in draft["authorization"].values()))

    @unittest.skipIf(torch is None, "PyTorch is optional in the local lightweight environment")
    def test_exact_near_and_mixed_components_are_contained_and_private(self) -> None:
        contract = load_contract(CONFIG)
        ids, rows = small_fixture()
        public, private = audit_loaded_geometry_tokens(contract, ids, ids, rows, torch)
        self.assertEqual(public["exact_duplicate_component_count"], 2)
        self.assertEqual(public["numerical_equivalence_edge_count"], 1)
        self.assertEqual(public["primary_component_count"], 3)
        self.assertEqual(public["auxiliary_component_count"], 2)
        self.assertEqual(public["auxiliary_case_count"], 3)
        self.assertEqual(public["mixed_primary_auxiliary_component_count"], 1)
        self.assertFalse(public["gate_pass"])
        serialized_public = json.dumps(public)
        for case_id in ids:
            self.assertNotIn(case_id, serialized_public)
        assignment: dict[str, str] = {}
        for split in ("train", "validation", "outer_test", "auxiliary"):
            for component in private[f"{split}_components"]:
                for case_id in component["case_ids"]:
                    self.assertNotIn(case_id, assignment)
                    assignment[case_id] = split
        self.assertEqual(set(assignment), set(ids))
        self.assertEqual(assignment["stable_6"], "auxiliary")
        self.assertEqual(assignment["named_alpha"], "auxiliary")

    @unittest.skipIf(torch is None, "PyTorch is optional in the local lightweight environment")
    def test_both_maximum_and_rms_tolerances_are_required(self) -> None:
        contract = load_contract(CONFIG)
        ids = ["stable_1", "stable_2", "stable_3"]
        rows = torch.zeros((3, 432), dtype=torch.float32)
        rows[1, 0] = 1.0e-6
        rows[2, :] = 1.0e-6
        public, _ = audit_loaded_geometry_tokens(contract, ids, ids, rows, torch)
        self.assertEqual(public["numerical_equivalence_edge_count"], 1)
        self.assertEqual(public["all_geometry_component_count"], 2)

    @unittest.skipIf(torch is None, "PyTorch is optional in the local lightweight environment")
    def test_full_synthetic_shape_can_freeze_component_split(self) -> None:
        contract = load_contract(CONFIG)
        ids = [f"stable_{index}" for index in range(508)] + [
            f"named_{index}" for index in range(70)
        ]
        rows = torch.arange(578, dtype=torch.float32)[:, None].repeat(1, 432)
        public, private = audit_loaded_geometry_tokens(contract, ids, ids, rows, torch)
        self.assertTrue(public["gate_pass"])
        self.assertTrue(public["private_split_frozen"])
        self.assertEqual(public["primary_component_count"], 508)
        self.assertEqual(public["auxiliary_case_count"], 70)
        self.assertEqual(
            public["train_component_count"]
            + public["validation_component_count"]
            + public["outer_test_component_count"],
            508,
        )
        self.assertGreaterEqual(public["validation_component_count"], 40)
        self.assertGreaterEqual(public["outer_test_component_count"], 40)
        self.assertTrue(private["split_frozen"])

    @unittest.skipIf(torch is None, "PyTorch is optional in the local lightweight environment")
    def test_nonfinite_misaligned_order_and_scope_mutations_fail_closed(self) -> None:
        contract = load_contract(CONFIG)
        ids, rows = small_fixture()
        with self.assertRaisesRegex(D5ContractError, "case_mesh_order"):
            audit_loaded_geometry_tokens(contract, ids, list(reversed(ids)), rows, torch)
        bad_rows = rows.clone()
        bad_rows[0, 0] = float("nan")
        with self.assertRaisesRegex(D5ContractError, "ghd_nonfinite"):
            audit_loaded_geometry_tokens(contract, ids, ids, bad_rows, torch)

        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("geometry_token_contract", "read_wss_values", True, "read_wss_values"),
            ("geometry_token_contract", "read_mesh_connectivity_values", True, "read_mesh_connectivity_values"),
            ("execution", "ngpus", 1, "resources"),
            ("execution", "rerun_after_any_outcome", True, "rerun"),
            ("authorization", "paper_result_or_claim", True, "paper_result_or_claim"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            candidate[section][key] = value
            with self.assertRaisesRegex(D5ContractError, reason):
                validate_contract(candidate)

    def test_pbs_enforces_clean_exact_cpu_only_single_attempt(self) -> None:
        text = PBS.read_text(encoding="utf-8")
        self.assertIn("select=1:ncpus=4:mem=64gb:ngpus=0", text)
        self.assertIn("status --porcelain", text)
        self.assertIn("attempt.started", text)
        self.assertIn("rerun is forbidden", text)
        self.assertIn("--private-grouping-manifest", text)
        self.assertNotIn("nvidia-smi", text)
        self.assertNotIn("registered_data_list'][0]['tensor", text)


if __name__ == "__main__":
    unittest.main()
