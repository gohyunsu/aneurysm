from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d1 import AcquisitionContractError
from aurora.aneug_processed_v4_d2 import load_contract


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_client_stage_d2.json"
CLOSURE = ROOT / "results" / "aneug_processed_v4_d2_transport_closure_20260814.json"


class AneuGProcessedV4D2Tests(unittest.TestCase):
    def test_closed_transport_record_preserves_partial_and_forbids_retry(self) -> None:
        closure = json.loads(CLOSURE.read_text(encoding="utf-8"))
        self.assertEqual(
            closure["status"],
            "closed_transport_incomplete_sftp_budget_exhausted",
        )
        self.assertEqual(closure["server"]["sftp_sessions_used"], 3)
        self.assertEqual(closure["server"]["transient_partial_gb_rounded_public"], 10.17)
        self.assertFalse(closure["server"]["transient_size_exact"])
        self.assertFalse(closure["server"]["further_sftp_session_allowed"])
        self.assertEqual(closure["schema_gate"]["pbs_attempts_used"], 0)
        self.assertFalse(closure["schema_gate"]["checksum_or_schema_evaluated"])
        self.assertFalse(closure["decision"]["same_contract_repair_or_retry"])
        self.assertFalse(closure["decision"]["scientific_verdict"])
        self.assertNotIn("transient_partial_bytes", closure["server"])
        self.assertNotIn("persistent_error", closure["sftp_session_ledger"][-1])

    def test_route_is_materially_distinct_and_d1_remains_closed(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["d1_boundary"]["attempts_used"], 3)
        self.assertFalse(contract["d1_boundary"]["same_contract_retry_or_repair"])
        self.assertFalse(contract["d1_boundary"]["d2_relabels_d1"])
        self.assertFalse(contract["transport"]["compute_node_external_download"])
        self.assertFalse(contract["transport"]["login_node_external_download"])

    def test_storage_is_bounded_and_sequential(self) -> None:
        contract = load_contract(CONFIG)
        storage = contract["storage"]
        self.assertEqual(storage["workflow_peak_cap_bytes"], 60_000_000_000)
        self.assertEqual(storage["maximum_combined_new_bytes"], 57_122_234_152)
        self.assertTrue(storage["sequential_client_download_required"])
        self.assertTrue(storage["steady_client_copy_deleted_before_transient_download"])
        self.assertFalse(storage["v5_downloaded"])
        self.assertFalse(storage["raw_blood_or_wall_downloaded"])

    def test_schema_is_one_shot_cpu_only_and_claim_free(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["schema_gate"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["schema_gate"]["rerun_after_any_outcome"])
        self.assertEqual(contract["execution"]["ngpus"], 0)
        self.assertEqual(contract["execution"]["excluded_server"], "junjinyong")
        self.assertFalse(contract["authorization"]["scientific_p0_or_confirmatory_test"])
        self.assertFalse(contract["authorization"]["paper_result_or_claim"])

    def test_scope_or_route_expansion_is_rejected(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        for section, key, value, reason in (
            ("storage", "workflow_peak_cap_bytes", 2_000_000_000_000, "workflow_cap"),
            ("transport", "compute_node_external_download", True, "compute_egress"),
            ("schema_gate", "maximum_pbs_attempts", 2, "pbs_attempts"),
            ("execution", "ngpus", 1, "gpu"),
        ):
            candidate = copy.deepcopy(original)
            candidate[section][key] = value
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "contract.json"
                path.write_text(json.dumps(candidate), encoding="utf-8")
                with self.assertRaisesRegex(AcquisitionContractError, reason):
                    load_contract(path)


if __name__ == "__main__":
    unittest.main()
