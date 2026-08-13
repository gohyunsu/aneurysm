from __future__ import annotations

import copy
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_reference_floor_g0 import (
    G0ContractError,
    analyze_hf_tree,
    inspect_tar_members,
    load_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_reference_floor_g0_v1.json"


class AneuGReferenceFloorG0Tests(unittest.TestCase):
    def test_contract_is_prospective_source_only_and_gpu_zero(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["candidate"]["score"], 31.0)
        self.assertFalse(contract["candidate"]["method_selected"])
        self.assertFalse(contract["candidate"]["architecture_selected"])
        self.assertFalse(contract["candidate"]["gpu_training_authorized"])
        self.assertEqual(contract["execution"]["ngpus"], 0)
        self.assertEqual(contract["execution"]["excluded_server"], "junjinyong")
        self.assertFalse(contract["gate"]["same_contract_repair_or_rerun_allowed"])

    def test_candidate_score_cannot_be_rounded_to_admission(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        contract["candidate"]["score"] = 32.0
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(G0ContractError, "candidate_score"):
                load_contract(path)

    def test_payload_or_retry_boundary_is_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        for key, value in (("aneug_mesh_payload_downloaded", True), ("retry_count", 1)):
            contract = copy.deepcopy(original)
            contract["audit"][key] = value
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "config.json"
                path.write_text(json.dumps(contract), encoding="utf-8")
                with self.assertRaisesRegex(G0ContractError, "payload_or_retry"):
                    load_contract(path)

    def test_resource_and_inventory_budgets_are_frozen(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        changes = (
            ("execution", "ncpus", 8, "execution_boundary"),
            ("audit", "maximum_challenge_tar_members", 40_000, "payload_or_retry"),
        )
        for section, key, value, reason in changes:
            contract = copy.deepcopy(original)
            contract[section][key] = value
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "config.json"
                path.write_text(json.dumps(contract), encoding="utf-8")
                with self.assertRaisesRegex(G0ContractError, reason):
                    load_contract(path)

    def test_tree_summary_counts_cases_without_calling_them_patients(self) -> None:
        entries = [
            {"path": "transient_data/stable_0/wall_data.pt"},
            {"path": "transient_data/stable_0/shape.obj"},
            {"path": "transient_data/stable_0/shape_remeshed.obj"},
            {"path": "transient_data/stable_1/wall_data.pt"},
            {"path": "transient_data/stable_1/shape_remeshed.obj"},
            {"path": "transient_data/latent_parent_map.csv"},
        ]
        summary = analyze_hf_tree(entries)
        self.assertEqual(summary["wall_case_count"], 2)
        self.assertEqual(summary["wall_shape_and_remeshed_case_count"], 1)
        self.assertEqual(summary["explicit_lineage_path_count"], 1)
        self.assertTrue(summary["lineage_path_scan_is_not_proof_of_independence"])

    def test_tar_is_inventoried_without_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                payload = b"not-a-field"
                info = tarfile.TarInfo("case1/team1/wss.vtp")
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            summary = inspect_tar_members(path)
        self.assertEqual(summary["file_member_count"], 1)
        self.assertEqual(summary["suffix_counts"], {".vtp": 1})
        self.assertEqual(
            summary["file_inventory"],
            [{"name": "case1/team1/wss.vtp", "size": len(b"not-a-field")}],
        )
        self.assertRegex(summary["file_inventory_sha256"], r"^[0-9a-f]{64}$")
        self.assertFalse(summary["members_extracted"])
        self.assertFalse(summary["field_values_read"])

    def test_tar_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unsafe.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                info = tarfile.TarInfo("../escape.vtp")
                info.size = 1
                archive.addfile(info, io.BytesIO(b"x"))
            with self.assertRaisesRegex(Exception, "unsafe_member"):
                inspect_tar_members(path)

    def test_tar_member_budget_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "too-many.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                for name in ("one.vtp", "two.vtp"):
                    info = tarfile.TarInfo(name)
                    info.size = 1
                    archive.addfile(info, io.BytesIO(b"x"))
            with self.assertRaisesRegex(Exception, "member_budget"):
                inspect_tar_members(path, maximum_members=1)


if __name__ == "__main__":
    unittest.main()
