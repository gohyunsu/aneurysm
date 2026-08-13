from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.run_aneumo_transient_vtp_d0 import D0Error, run
from test_aneumo_transient_vtp import _ascii_vtp


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_transient_vtp_d0_v2.json"
RUNNER = ROOT / "experiments" / "run_aneumo_transient_vtp_d0.py"
STAGER = ROOT / "scripts" / "stage_aneumo_transient_vtp_d0.py"
PBS = ROOT / "cluster" / "pbs_aneumo_transient_vtp_d0_v2.pbs"
OUTCOME = ROOT / "results" / "aneumo_transient_vtp_d0_v1_execution_20260813.json"


class AneumoTransientVTPD0V2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_v1_failure_is_exact_and_final_repair_is_transport_only(self) -> None:
        outcome = json.loads(OUTCOME.read_text(encoding="utf-8"))
        self.assertEqual(outcome["job"]["id"], "116160.ECE-util1")
        self.assertEqual(outcome["outcome"], "execution_incomplete")
        self.assertFalse(outcome["vtp_payload_obtained"])
        self.assertFalse(outcome["reader_or_structure_extractor_evaluated"])
        development = self.config["development"]
        self.assertEqual(development["repair_round"], 2)
        self.assertEqual(development["repair_rounds_maximum"], 2)
        self.assertEqual(development["repair_scope"], "zip_range_member_extraction_transport_only")
        self.assertFalse(development["further_repair_or_resubmission_allowed"])
        self.assertFalse(development["case_phase_array_threshold_or_scientific_code_changed"])

    def test_source_members_and_hashes_are_unchanged(self) -> None:
        source = self.config["source"]
        self.assertEqual(source["case_id"], 1)
        self.assertEqual(source["phases"], ["4.01", "5.00"])
        self.assertTrue(source["field_members_are_not_newly_selected"])
        self.assertEqual(
            source["expected_vtp_sha256"],
            [
                "39e0f8028bdb80ce2e32920addeb3dcced611c20d8e3ff713a5bce82b846fc3a",
                "007c9b72708e468f5d1d8bdde8dbe30bc30a6921938c62fa435375f5a5a8eff9",
            ],
        )

    def test_stage_is_exact_ephemeral_and_pbs_is_network_free_cpu_only(self) -> None:
        transport = self.config["transport"]
        boundary = self.config["license_boundary"]
        execution = self.config["execution"]
        self.assertEqual(transport["mode"], "exact_private_stage")
        self.assertFalse(transport["network_during_pbs"])
        self.assertFalse(transport["raw_member_persistence_after_attempt"])
        self.assertTrue(boundary["private_raw_stage_is_ephemeral"])
        self.assertTrue(boundary["raw_stage_deleted_after_attempt"])
        self.assertEqual(execution["server"], "introai9")
        self.assertEqual(execution["excluded_server"], "junjinyong")
        self.assertEqual(execution["ngpus"], 0)
        wrapper = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -l select=1:ncpus=4:mem=16gb:ngpus=0", wrapper)
        self.assertIn("--member-root", wrapper)
        self.assertIn("cleanup_stage", wrapper)
        self.assertNotIn("rm -rf", wrapper)
        self.assertNotIn("curl", wrapper)
        self.assertNotIn("wget", wrapper)
        self.assertNotIn("junjinyong", wrapper)

    def test_staged_runner_performs_zero_http_requests(self) -> None:
        payload_a = _ascii_vtp()
        payload_b = payload_a.replace(b"-1.2 -0.9 0", b"-1.1 -0.9 0", 1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / "stage"
            stage.mkdir()
            names = ["phase-a.vtp", "phase-b.vtp"]
            (stage / names[0]).write_bytes(payload_a)
            (stage / names[1]).write_bytes(payload_b)
            config = json.loads(CONFIG.read_text(encoding="utf-8"))
            config["source"]["staged_filenames"] = names
            config["source"]["expected_vtp_sha256"] = [
                hashlib.sha256(payload_a).hexdigest(),
                hashlib.sha256(payload_b).hexdigest(),
            ]
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = run(config_path, stage)
            self.assertEqual(result["transport"]["mode"], "exact_private_stage")
            self.assertEqual(result["transport"]["http_requests_during_pbs"], 0)
            self.assertEqual(result["transport"]["http_bytes_during_pbs"], 0)
            self.assertFalse(result["scientific_stability_gate_evaluated"])

    def test_missing_stage_fails_closed_and_public_config_has_no_private_path(self) -> None:
        with self.assertRaisesRegex(D0Error, "stage is absent"):
            run(CONFIG, Path("/definitely/absent/aurora-stage"))
        self.assertNotIn("/home/", CONFIG.read_text(encoding="utf-8"))
        for path in (CONFIG, RUNNER, STAGER, PBS, OUTCOME):
            self.assertGreater(path.stat().st_size, 100)


if __name__ == "__main__":
    unittest.main()
