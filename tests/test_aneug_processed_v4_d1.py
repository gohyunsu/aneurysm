from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d1 import AcquisitionContractError, load_contract


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_acquisition_d1.json"


class AneuGProcessedV4D1Tests(unittest.TestCase):
    def test_contract_is_storage_bounded_and_transient_only_persistent(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["storage"]["selected_aneug_v4_peak_cap_bytes"], 60_000_000_000)
        self.assertEqual(contract["storage"]["new_processed_peak_bytes"], 33_377_372_101)
        self.assertTrue(contract["storage"]["transient_persistent"])
        self.assertFalse(contract["storage"]["steady_full_object_persistent_after_norm_extraction"])
        self.assertFalse(contract["storage"]["v5_downloaded"])
        self.assertFalse(contract["storage"]["raw_blood_or_wall_downloaded"])

    def test_exact_v4_objects_and_attempt_budget_are_frozen(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["source"]["transient"]["bytes"], 23_744_862_051)
        self.assertEqual(
            contract["source"]["transient"]["sha256"],
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        )
        self.assertEqual(contract["transport"]["maximum_pbs_transport_attempts"], 3)
        self.assertTrue(contract["transport"]["resumable_partial_download"])

    def test_no_gpu_or_scientific_claim_is_opened(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["execution"]["server"], "introai9")
        self.assertEqual(contract["execution"]["ngpus"], 0)
        self.assertEqual(contract["execution"]["excluded_server"], "junjinyong")
        self.assertFalse(contract["authorization"]["scientific_p0_or_confirmatory_test"])
        self.assertFalse(contract["authorization"]["gpu_training_before_split_freeze"])
        self.assertFalse(contract["authorization"]["paper_result"])

    def test_expanding_storage_or_payload_scope_is_rejected(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        for section, key, value, reason in (
            ("storage", "selected_aneug_v4_peak_cap_bytes", 2_000_000_000_000, "storage_cap"),
            ("storage", "v5_downloaded", True, "v5_downloaded"),
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
