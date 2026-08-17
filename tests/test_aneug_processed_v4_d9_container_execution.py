import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d9_container_execution_v2.json"
R0 = ROOT / "cluster" / "pbs_aneug_processed_v4_d9_r0_container_v2.pbs"
R1 = ROOT / "cluster" / "pbs_aneug_processed_v4_d9_r1_container_v2.pbs"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class D9ContainerExecutionTests(unittest.TestCase):
    def test_overlay_pins_unchanged_scientific_code_and_config(self) -> None:
        overlay = json.loads(CONFIG.read_text(encoding="utf-8"))
        science = overlay["unchanged_scientific_contract"]
        self.assertEqual(sha256(ROOT / science["config"]), science["config_sha256"])
        self.assertEqual(sha256(ROOT / science["implementation"]), science["implementation_sha256"])
        self.assertFalse(science["split_architecture_loss_seed_thresholds_changed"])
        self.assertFalse(science["outer_or_auxiliary_access"])
        self.assertEqual(overlay["predecessors"]["passing_gpu_runtime_job"], "116555.ECE-util1")

    def test_runtime_is_exact_a6000_container_route(self) -> None:
        overlay = json.loads(CONFIG.read_text(encoding="utf-8"))
        runtime = overlay["runtime_delta"]
        self.assertEqual((runtime["server"], runtime["queue"], runtime["Qlist"]), ("introai9", "coss_a6gpu", "a6000"))
        self.assertEqual(
            runtime["container_sha256"],
            "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        )
        self.assertFalse(runtime["host_torch_used_for_science"])

    def test_r0_uses_read_only_data_and_passing_runtime_evidence(self) -> None:
        script = R0.read_text(encoding="utf-8")
        self.assertIn("select=1:ncpus=4:mem=64gb:ngpus=1:Qlist=a6000", script)
        self.assertIn("/usr/bin/singularity exec --nv --cleanenv", script)
        self.assertIn('$AURORA_DATA_ROOT:/data:ro', script)
        self.assertIn('p["probe_pass"] is True', script)
        self.assertIn('p["selected_runtime"] == "pinned_container_inherited"', script)
        self.assertIn("--mode prepare", script)
        self.assertIn("choose a new run ID", script)
        self.assertNotIn("AURORA_PYTHON", script)

    def test_r1_is_cache_only_and_cannot_run_without_r0_manifest(self) -> None:
        script = R1.read_text(encoding="utf-8")
        self.assertIn("select=1:ncpus=4:mem=64gb:ngpus=1:Qlist=a6000", script)
        self.assertIn('[ -f "$AURORA_D9_CACHE/cache_manifest.json" ]', script)
        self.assertIn('$AURORA_D9_CACHE:/cache:ro', script)
        self.assertIn("direct_cycle|moment_pod", script)
        self.assertNotIn("AURORA_DATA_ROOT", script)
        self.assertNotIn("assembled_registered", script)
        self.assertNotIn("AURORA_PYTHON", script)

    def test_retry_is_append_only_development_not_confirmation(self) -> None:
        overlay = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertTrue(overlay["provenance"]["new_run_id_and_result_directory_each_execution"])
        self.assertTrue(overlay["provenance"]["existing_attempts_never_overwritten_hidden_or_relabelled"])
        self.assertFalse(overlay["authorization"]["multi_seed_confirmation"])
        self.assertFalse(overlay["authorization"]["outer_test"])
        self.assertFalse(overlay["authorization"]["paper_result_or_claim"])


if __name__ == "__main__":
    unittest.main()
