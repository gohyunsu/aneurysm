import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_d9_gpu_runtime_revalidation_v3.json"
PBS = ROOT / "cluster" / "pbs_aneug_d9_gpu_runtime_revalidation_v3.pbs"


class D9GpuRuntimeRevalidationV3Tests(unittest.TestCase):
    def test_v3_changes_only_the_introai9_gpu_queue_route(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(contract["predecessor"]["job_id"], "116553.ECE-util1")
        self.assertEqual(contract["predecessor"]["all_low_level_cu_init_codes"], 999)
        self.assertFalse(contract["predecessor"]["nvidia_uvm_device_present"])
        self.assertEqual(
            contract["diagnostic_delta"]["only_material_execution_change"],
            "queue_coss_agpu_to_coss_a6gpu",
        )
        self.assertEqual(contract["execution"]["server"], "introai9")
        self.assertEqual(contract["execution"]["queue"], "coss_a6gpu")

    def test_v3_reuses_the_exact_v2_diagnostic_and_container(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertTrue(contract["diagnostic_delta"]["same_driver_probe"])
        self.assertTrue(contract["diagnostic_delta"]["same_torch_smoke"])
        self.assertEqual(
            contract["runtime"]["container_sha256"],
            "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        )
        self.assertFalse(contract["scope"]["dataset_path_in_wrapper"])

    def test_wrapper_selects_a6gpu_and_executes_the_exact_v2_probe(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -q coss_a6gpu", script)
        self.assertIn("select=1:ncpus=2:mem=16gb:ngpus=1", script)
        self.assertIn("pbs_aneug_d9_gpu_runtime_revalidation_v2.pbs", script)
        self.assertNotIn("AURORA_DATA_ROOT", script)
        self.assertNotIn("junjinyong", script)


if __name__ == "__main__":
    unittest.main()
