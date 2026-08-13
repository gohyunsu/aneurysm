from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_transient_vtp_d0.json"
RUNNER = ROOT / "experiments" / "run_aneumo_transient_vtp_d0.py"
PBS = ROOT / "cluster" / "pbs_aneumo_transient_vtp_d0.pbs"


class AneumoTransientVTPD0ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_exact_source_and_previously_read_members_are_pinned(self) -> None:
        source = self.config["source"]
        self.assertEqual(
            source["huggingface_revision"],
            "f801adee816c18d3e18b23e6fcb147fe4c264209",
        )
        self.assertEqual(source["case_id"], 1)
        self.assertEqual(source["phases"], ["4.01", "5.00"])
        self.assertTrue(source["field_members_are_not_newly_selected"])
        self.assertTrue(source["previously_inspected_in_release_audit"])
        self.assertEqual(len(source["expected_vtp_sha256"]), 2)
        for digest in source["expected_vtp_sha256"]:
            self.assertEqual(len(digest), 64)

    def test_license_handling_is_stricter_and_nonredistributing(self) -> None:
        boundary = self.config["license_boundary"]
        self.assertTrue(boundary["declarations_conflict"])
        self.assertFalse(boundary["raw_or_derived_field_redistribution"])
        self.assertFalse(boundary["legal_conclusion_made"])
        self.assertIn("stricter", boundary["handling_rule"])

    def test_bounded_development_cannot_activate_scientific_claims(self) -> None:
        development = self.config["development"]
        self.assertEqual(development["repair_rounds_maximum"], 2)
        self.assertIn("training_a_model", development["forbidden_repairs"])
        self.assertEqual(
            development["success_authorizes"],
            "register_separate_prospective_method_free_stability_p0_on_new_family_disjoint_members",
        )
        self.assertIn("paper_identity", development["does_not_authorize"])
        self.assertIn("gpu_training", development["does_not_authorize"])

    def test_execution_is_introai9_cpu_pbs_only(self) -> None:
        execution = self.config["execution"]
        self.assertEqual(execution["server"], "introai9")
        self.assertEqual(execution["excluded_server"], "junjinyong")
        self.assertEqual(execution["scheduler"], "pbs")
        self.assertEqual(execution["ngpus"], 0)
        self.assertFalse(execution["login_node_gpu_allowed"])
        self.assertEqual(
            execution["runtime_binding"],
            "private_execution_manifest_must_pin_container_path_size_and_sha256_before_submission",
        )
        self.assertNotIn("/home/", CONFIG.read_text(encoding="utf-8"))
        wrapper = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -l select=1:ncpus=4:mem=16gb:ngpus=0", wrapper)
        self.assertIn("singularity exec --cleanenv", wrapper)
        self.assertNotIn("junjinyong", wrapper)

    def test_source_files_have_stable_nonempty_bytes(self) -> None:
        for path in (CONFIG, RUNNER, PBS):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(len(digest), 64)
            self.assertGreater(path.stat().st_size, 100)


if __name__ == "__main__":
    unittest.main()
