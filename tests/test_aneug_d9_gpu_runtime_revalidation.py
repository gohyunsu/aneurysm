import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_d9_gpu_runtime_revalidation_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_d9_gpu_runtime_revalidation_v1.pbs"


class D9GpuRuntimeRevalidationTests(unittest.TestCase):
    def test_contract_is_data_free_and_reuses_the_d9_study_family(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(contract["schema_version"], "aurora.aneug_d9_gpu_runtime_revalidation.v1")
        self.assertEqual(contract["predecessor"]["job_id"], "116549.ECE-util1")
        self.assertTrue(contract["scope"]["engineering_only"])
        self.assertFalse(contract["scope"]["dataset_paths_or_values_read"])
        self.assertFalse(contract["scope"]["model_or_metric_execution"])
        self.assertEqual(
            contract["decision"]["pass_authorizes"],
            "new_id_D9_R0_rerun_in_exact_pinned_container",
        )

    def test_pinned_container_identity_and_runtime_are_exact(self) -> None:
        contract = json.loads(CONFIG.read_text(encoding="utf-8"))
        container = contract["runtime_candidates"]["pinned_container"]
        self.assertEqual(container["bytes"], 3_204_870_144)
        self.assertEqual(
            container["sha256"],
            "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        )
        self.assertEqual(container["torch"], "2.5.1+cu118")
        self.assertEqual(container["cuda_runtime"], "11.8")

    def test_wrapper_compares_host_and_container_in_one_gpu_allocation(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -q coss_agpu", script)
        self.assertIn("select=1:ncpus=2:mem=16gb:ngpus=1", script)
        self.assertIn("/usr/bin/nvidia-smi", script)
        self.assertIn("$AURORA_HOST_PYTHON", script)
        self.assertIn("/usr/bin/singularity exec --nv --cleanenv", script)
        self.assertIn("experiments/gpu_smoke.py", script)
        self.assertIn("container_runtime_exit", script)
        self.assertNotIn("AURORA_DATA_ROOT", script)
        self.assertNotIn("assembled_registered", script)

    def test_wrapper_uses_append_only_run_identity_not_a_global_no_rerun_rule(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("choose a new run ID", script)
        self.assertNotIn("rerun or repair is forbidden", script)
        self.assertIn("attempt.started", script)
        self.assertIn("attempt.status.json", script)


if __name__ == "__main__":
    unittest.main()
