from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d1 import AcquisitionContractError
from aurora.aneug_processed_v4_d3 import (
    expected_chunk_name,
    expected_chunk_size,
    load_chunk_manifest,
    load_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_chunk_stage_d3.json"


class AneuGProcessedV4D3Tests(unittest.TestCase):
    def test_d3_is_human_selected_and_d2_stays_closed(self) -> None:
        contract = load_contract(CONFIG)
        self.assertTrue(contract["human_selection"]["explicitly_selected"])
        self.assertFalse(contract["human_selection"]["d3_is_d2_retry_or_repair"])
        self.assertEqual(contract["d2_boundary"]["sftp_sessions_used"], 3)
        self.assertFalse(contract["d2_boundary"]["further_d2_sftp_session_allowed"])
        self.assertFalse(contract["transport"]["d2_monolithic_partial_resumed"])

    def test_chunk_partition_is_exact_and_bounded(self) -> None:
        contract = load_contract(CONFIG)
        sizes = [expected_chunk_size(contract, index) for index in range(23)]
        self.assertEqual(sizes[:22], [1_073_741_824] * 22)
        self.assertEqual(sizes[-1], 122_541_923)
        self.assertEqual(sum(sizes), 23_744_862_051)
        self.assertEqual(
            expected_chunk_name(contract, 0),
            "transient-v4.part-000-of-023.bin",
        )
        self.assertEqual(
            expected_chunk_name(contract, 22),
            "transient-v4.part-022-of-023.bin",
        )
        self.assertLess(contract["storage"]["client_peak_bytes"], 30_000_000_000)
        self.assertLess(
            contract["storage"]["server_reassembly_peak_after_d2_partial_retirement_bytes"],
            60_000_000_000,
        )

    def test_finalizer_and_schema_are_cpu_only_one_shot(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["transport_finalizer"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["transport_finalizer"]["rerun_after_any_outcome"])
        self.assertEqual(contract["transport_finalizer"]["ngpus"], 0)
        self.assertEqual(contract["schema_gate"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["schema_gate"]["rerun_after_any_outcome"])
        self.assertEqual(contract["execution"]["excluded_server"], "junjinyong")
        self.assertFalse(contract["authorization"]["scientific_p0_or_confirmatory_test"])
        self.assertFalse(contract["authorization"]["paper_result_or_claim"])

    def test_private_manifest_contract(self) -> None:
        contract = load_contract(CONFIG)
        rows = []
        offset = 0
        for index in range(23):
            size = expected_chunk_size(contract, index)
            rows.append(
                {
                    "index": index,
                    "name": expected_chunk_name(contract, index),
                    "offset": offset,
                    "bytes": size,
                    "sha256": hashlib.sha256(f"chunk-{index}".encode()).hexdigest(),
                }
            )
            offset += size
        manifest = {
            "schema_version": "aurora.aneug_processed_v4_chunk_manifest_d3.v1",
            "protocol_id": contract["protocol_id"],
            "source_bytes": contract["source"]["transient"]["bytes"],
            "source_sha256": contract["source"]["transient"]["sha256"],
            "chunks": rows,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            loaded = load_chunk_manifest(path, contract)
            self.assertEqual(len(loaded["chunks"]), 23)
            broken = copy.deepcopy(manifest)
            broken["chunks"][5]["offset"] += 1
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaisesRegex(AcquisitionContractError, "manifest_offset"):
                load_chunk_manifest(path, contract)

    def test_scope_or_order_expansion_is_rejected(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        for section, key, value, reason in (
            ("human_selection", "d3_is_d2_retry_or_repair", True, "d2_retry"),
            ("chunk_contract", "chunk_bytes", 2_147_483_648, "chunk_bytes"),
            ("storage", "workflow_peak_cap_bytes", 2_000_000_000_000, "workflow_cap"),
            ("transport_finalizer", "maximum_pbs_attempts", 2, "finalizer_attempts"),
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
