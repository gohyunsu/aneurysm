import copy
import hashlib
import json
import re
import struct
import tempfile
import unittest
from pathlib import Path

from aurora.goal_oriented_s0a_asset import (
    AssetComponentProtocolError,
    _contained,
    load_asset_config,
    read_nifti_header,
    read_stl_bounds,
    validate_asset_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "goal_oriented_segmentation_s0a_asset_component.json"
PBS = ROOT / "cluster" / "pbs_goal_oriented_s0a_asset_component.pbs"
RESULT = ROOT / "results" / "goal_oriented_s0a_asset_component_20260809.json"
RESULT_SHA256 = "c220cb8d92909a5a401b29ad5b75d54f4881d9db4a32ea6f33dd6007e424ad6e"


class GoalOrientedS0AAssetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_asset_config(CONFIG)

    def test_reference_config_is_valid(self) -> None:
        self.assertEqual(len(validate_asset_config(self.config)), 5)

    def test_public_result_preserves_the_failed_asset_gate(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["checks_passed"], 5)
        self.assertEqual(payload["checks_total"], 9)
        self.assertEqual(payload["verdict"]["asset_component"], "failed_5_of_9")
        self.assertEqual(payload["verdict"]["s0a_gate"], "not_evaluated")
        self.assertFalse(payload["verdict"]["solver_preflight_v2_authorized"])
        self.assertFalse(
            payload["verdict"]["method_architecture_gpu_outer_test_or_submission_authorized"]
        )
        self.assertFalse(payload["aggregate"]["nifti_or_stl_header_opened"])

    def test_public_result_hash_and_privacy_boundary_are_exact(self) -> None:
        raw = RESULT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), RESULT_SHA256)
        text = raw.decode("utf-8")
        self.assertNotIn("/home/", text)
        self.assertNotRegex(text, r"147[.]46")
        self.assertIsNone(re.search(r"[\w.+-]+@[\w.-]+", text))
        payload = json.loads(text)
        self.assertFalse(payload["privacy_and_access_boundary"]["source_identifiers_written"])
        self.assertFalse(payload["privacy_and_access_boundary"]["private_paths_written"])

    def test_positional_or_similarity_linkage_cannot_be_enabled(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["linkage_contract"]["row_position_fallback"] = True
        with self.assertRaisesRegex(AssetComponentProtocolError, "no-fallback"):
            validate_asset_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["linkage_contract"]["prefix_or_filename_similarity_fallback"] = True
        with self.assertRaisesRegex(AssetComponentProtocolError, "no-fallback"):
            validate_asset_config(candidate)

    def test_geometry_thresholds_cannot_be_relaxed(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["geometry_contract"]["containment_tolerance_mm"] = 50.0
        with self.assertRaisesRegex(AssetComponentProtocolError, "geometry limits"):
            validate_asset_config(candidate)

    def test_asset_pass_cannot_become_s0a_or_gpu_authorization(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["decision"]["all_nine_pass_is_s0a_pass"] = True
        with self.assertRaisesRegex(AssetComponentProtocolError, "decision"):
            validate_asset_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["authorization"]["gpu_training"] = True
        with self.assertRaisesRegex(AssetComponentProtocolError, "cannot authorize"):
            validate_asset_config(candidate)

    def test_pbs_is_one_shot_cpu_read_only_without_model_or_gpu(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -q coss_agpu", script)
        self.assertIn("select=1:ncpus=4:mem=16gb", script)
        self.assertNotIn("ngpus=", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("singularity exec --nv", script)
        self.assertIn("AURORA_RAW_CMHA_ROOT", script)
        self.assertIn("AURORA_EXTRACTED_CMHA_ROOT", script)
        self.assertIn('export PYTHONPATH="$AURORA_PROJECT_ROOT/src', script)
        self.assertIn("rerun is forbidden", script)
        self.assertIn('"image_voxels_read":false', script)
        self.assertIn('"rupture_label_values_used":false', script)

    def test_minimal_sform_nifti_header_is_read_without_voxels(self) -> None:
        header = bytearray(352)
        struct.pack_into("<i", header, 0, 348)
        struct.pack_into("<8h", header, 40, 3, 32, 40, 48, 1, 1, 1, 1)
        struct.pack_into("<8f", header, 76, 1.0, 0.5, 0.5, 0.625, 0, 0, 0, 0)
        struct.pack_into("<2h", header, 252, 0, 1)
        struct.pack_into("<4f", header, 280, 0.5, 0.0, 0.0, -8.0)
        struct.pack_into("<4f", header, 296, 0.0, 0.5, 0.0, -10.0)
        struct.pack_into("<4f", header, 312, 0.0, 0.0, 0.625, -15.0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.nii"
            path.write_bytes(header)
            result = read_nifti_header(path)
        self.assertEqual(result["spatial"], (32, 40, 48))
        self.assertEqual(result["affine_source"], "sform")
        self.assertAlmostEqual(result["spacing"][2], 0.625)

    def test_binary_stl_bounds_and_lps_ras_containment(self) -> None:
        record = struct.pack(
            "<12fH",
            0.0,
            0.0,
            1.0,
            -2.0,
            -2.0,
            0.0,
            -1.0,
            -2.0,
            0.0,
            -2.0,
            -1.0,
            0.0,
            0,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mesh.stl"
            path.write_bytes(b"x" * 80 + struct.pack("<I", 1) + record)
            stl = read_stl_bounds(path)
        self.assertEqual(stl["triangles"], 1)
        self.assertEqual(stl["encoding"], "binary")
        nifti = {
            "bounds_min": (0.0, 0.0, -1.0),
            "bounds_max": (3.0, 3.0, 1.0),
        }
        self.assertFalse(_contained(stl, nifti, 0.0, "identity"))
        self.assertTrue(_contained(stl, nifti, 0.0, "lps_to_ras_xy_sign_flip"))


if __name__ == "__main__":
    unittest.main()
