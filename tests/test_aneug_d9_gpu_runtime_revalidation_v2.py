import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_d9_gpu_runtime_revalidation_v2.json"
PBS = ROOT / "cluster" / "pbs_aneug_d9_gpu_runtime_revalidation_v2.pbs"
DRIVER = ROOT / "experiments" / "cuda_driver_probe.py"


class D9GpuRuntimeRevalidationV2Tests(unittest.TestCase):
    def test_v2_has_a_specific_information_gaining_delta(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(contract["predecessor"]["job_id"], "116551.ECE-util1")
        self.assertEqual(contract["predecessor"]["scientific_asset_reads"], 0)
        self.assertEqual(
            contract["diagnostic_delta"]["visibility_variants"],
            ["inherited", "explicit_zero", "unset"],
        )
        self.assertFalse(contract["diagnostic_delta"]["same_error_without_information_gain"])
        self.assertFalse(contract["scope"]["dataset_path_in_wrapper"])

    def test_low_level_probe_uses_driver_api_without_torch(self) -> None:
        script = DRIVER.read_text(encoding="utf-8")
        self.assertIn('ctypes.CDLL("libcuda.so.1")', script)
        self.assertIn("cuInit", script)
        self.assertIn("cuDeviceGetCount", script)
        self.assertNotIn("import torch", script)
        self.assertIn("refusing to overwrite", script)

    def test_wrapper_records_device_nodes_and_all_visibility_variants(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("/dev/nvidia-uvm", script)
        self.assertIn("CUDA_VISIBLE_DEVICES=0", script)
        self.assertIn("-u CUDA_VISIBLE_DEVICES", script)
        self.assertIn("driver_container_${visibility}", script)
        self.assertIn("torch_container_${visibility}", script)
        self.assertIn("pinned_container_cuda_visible_devices_unset", script)
        self.assertNotIn("AURORA_DATA_ROOT", script)
        self.assertNotIn("assembled_registered", script)

    def test_wrapper_is_one_gpu_data_free_and_append_only_per_run_id(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -q coss_agpu", script)
        self.assertIn("select=1:ncpus=2:mem=16gb:ngpus=1", script)
        self.assertIn("choose a new run ID", script)
        self.assertIn("attempt.status.json", script)
        self.assertNotIn("junjinyong", script)


if __name__ == "__main__":
    unittest.main()
