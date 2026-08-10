from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # pragma: no cover - optional local dependency
    torch = None

from aurora.aneug_surface_vector_structure_p0 import (
    AneuGSurfaceVectorP0Error,
    analyse_case,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_surface_vector_structure_p0.json"


class SurfaceVectorP0ContractTests(unittest.TestCase):
    def test_reference_contract_is_exactly_admitted_cpu_only_and_one_shot(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["candidate"]["score"], 32.0)
        self.assertEqual(sum(config["candidate"]["axis_scores"]), 32.0)
        self.assertFalse(config["candidate"]["method_selected"])
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["excluded_server"], "junjinyong")
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertEqual(config["execution"]["maximum_submissions_for_exact_public_source"], 1)
        self.assertEqual(len(config["sources"]["cases"]), 3)
        self.assertFalse(config["access"]["blood_data_access"])
        self.assertFalse(config["access"]["processed_archive_access"])

    def test_score_source_access_or_gpu_mutation_is_rejected(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["candidate"]["score"] = 32.5
        payload["sources"]["dataset_commit"] = "f" * 40
        payload["access"]["blood_data_access"] = True
        payload["execution"]["ngpus"] = 1
        with self.assertRaises(AneuGSurfaceVectorP0Error):
            validate_config(payload)

    def test_pbs_wrapper_forbids_dirty_repeat_gpu_and_other_server(self) -> None:
        script = (ROOT / "cluster" / "pbs_aneug_surface_vector_structure_p0.pbs").read_text()
        self.assertIn("ngpus=0", script)
        self.assertIn("status --porcelain", script)
        self.assertIn("resubmission is forbidden", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("--nv", script)


@unittest.skipIf(torch is None, "PyTorch is optional for local contract tests")
class SurfaceVectorP0GeometryTests(unittest.TestCase):
    def test_synthetic_tangent_field_has_an_interior_indexed_critical_point(self) -> None:
        config = load_config(CONFIG)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mesh = root / "shape_remeshed.obj"
            mesh.write_text(
                "v -1 -1 0\n"
                "v 1 -1 0\n"
                "v 0 1 0\n"
                "f 1 2 3\n",
                encoding="utf-8",
            )
            phases = 80
            xyz = torch.tensor(
                [[[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]]],
                dtype=torch.float32,
            ).repeat(phases, 1, 1)
            scale = 1.0 + 0.1 * torch.sin(torch.linspace(0, 2 * math.pi, phases))
            wss = xyz * scale[:, None, None]
            wall = root / "wall_data.pt"
            torch.save(
                {
                    "x_coordinate": xyz[..., 0:1],
                    "y_coordinate": xyz[..., 1:2],
                    "z_coordinate": xyz[..., 2:3],
                    "x_wall_shear": wss[..., 0:1],
                    "y_wall_shear": wss[..., 1:2],
                    "z_wall_shear": wss[..., 2:3],
                    "wall_shear": torch.linalg.vector_norm(wss, dim=-1, keepdim=True),
                },
                wall,
            )
            result = analyse_case(wall, mesh, config)
        self.assertTrue(result["finite"])
        self.assertTrue(result["mesh_valid"])
        self.assertEqual(result["mesh_coordinate_match_fraction"], 1.0)
        self.assertEqual(result["median_normal_component_ratio"], 0.0)
        self.assertEqual(result["p95_normal_component_ratio"], 0.0)
        self.assertGreater(result["relative_temporal_variation"], 0.0)
        self.assertEqual(result["critical_nonempty_frame_fraction"], 1.0)
        self.assertGreaterEqual(result["critical_count_min"], 1)

    def test_normal_component_is_detected(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mesh = root / "shape_remeshed.obj"
            mesh.write_text(
                "v -1 -1 0\nv 1 -1 0\nv 0 1 0\nf 1 2 3\n",
                encoding="utf-8",
            )
            xyz = torch.tensor(
                [[[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]]],
                dtype=torch.float32,
            ).repeat(80, 1, 1)
            wss = torch.zeros_like(xyz)
            wss[..., 2] = 1.0
            wall = root / "wall_data.pt"
            torch.save(
                {
                    "x_coordinate": xyz[..., 0:1],
                    "y_coordinate": xyz[..., 1:2],
                    "z_coordinate": xyz[..., 2:3],
                    "x_wall_shear": wss[..., 0:1],
                    "y_wall_shear": wss[..., 1:2],
                    "z_wall_shear": wss[..., 2:3],
                },
                wall,
            )
            result = analyse_case(wall, mesh, config)
        self.assertEqual(result["median_normal_component_ratio"], 1.0)
        self.assertEqual(result["p95_normal_component_ratio"], 1.0)


if __name__ == "__main__":
    unittest.main()
