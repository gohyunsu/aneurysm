import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_d9_gpu_runtime_revalidation_v4.json"
PBS = ROOT / "cluster" / "pbs_aneug_d9_gpu_runtime_revalidation_v4.pbs"


class D9GpuRuntimeRevalidationV4Tests(unittest.TestCase):
    def test_v4_explains_why_queue_only_r3_did_not_isolate_a6000(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(contract["predecessor"]["job_id"], "116554.ECE-util1")
        self.assertEqual(contract["predecessor"]["allocated_node_qlist"], "tgpu")
        self.assertEqual(
            contract["predecessor"]["finding"],
            "queue_name_without_Qlist_did_not_isolate_A6000_nodes",
        )
        self.assertEqual(contract["scheduler_evidence"]["a6000_node_resource"], "resources_available.Qlist=a6000")

    def test_v4_adds_only_the_a6000_resource_selector(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            contract["diagnostic_delta"]["only_material_execution_change"],
            "add_select_resource_Qlist_a6000",
        )
        self.assertTrue(
            contract["diagnostic_delta"]["same_driver_probe_torch_smoke_visibility_variants_and_container"]
        )
        self.assertEqual(contract["execution"]["queue"], "coss_a6gpu")
        self.assertEqual(contract["execution"]["Qlist"], "a6000")
        self.assertFalse(contract["scope"]["dataset_path_in_wrapper"])

    def test_wrapper_forces_a6000_and_reuses_exact_probe(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -q coss_a6gpu", script)
        self.assertIn("select=1:ncpus=2:mem=16gb:ngpus=1:Qlist=a6000", script)
        self.assertIn("pbs_aneug_d9_gpu_runtime_revalidation_v2.pbs", script)
        self.assertNotIn("AURORA_DATA_ROOT", script)
        self.assertNotIn("junjinyong", script)


if __name__ == "__main__":
    unittest.main()
