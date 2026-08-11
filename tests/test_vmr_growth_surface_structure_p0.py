from __future__ import annotations

import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from aurora.vmr_growth_surface_structure_p0 import (
    VMRGrowthSurfaceStructureP0Error,
    inspect_metadata,
    inspect_result_archive,
    inspect_vtp_header,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "vmr_growth_surface_structure_p0.json"


def _vtp() -> bytes:
    return b"""<?xml version="1.0"?>
<VTKFile type="PolyData" version="1.0">
  <PolyData><Piece NumberOfPoints="3" NumberOfPolys="1">
    <PointData>
      <DataArray Name="WSS_0" NumberOfComponents="3" type="Float32"/>
      <DataArray Name="WSS_1" NumberOfComponents="3" type="Float32"/>
    </PointData>
    <Points><DataArray NumberOfComponents="3" type="Float32"/></Points>
  </Piece></PolyData>
</VTKFile>
"""


class VMRGrowthSurfaceStructureP0Tests(unittest.TestCase):
    def test_contract_is_fresh_cpu_only_and_noncompensatory(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["candidate"]["score"], 32.5)
        self.assertEqual(sum(config["candidate"]["axis_scores"]), 32.5)
        self.assertEqual(config["candidate"]["axis_scores"][2], 2.5)
        self.assertFalse(config["candidate"]["historical_surface_vector_score_repaired"])
        self.assertFalse(config["candidate"]["historical_surface_vector_p0_rerun"])
        self.assertFalse(config["candidate"]["method_selected"])
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["excluded_server"], "junjinyong")
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertEqual(config["execution"]["maximum_submissions_for_exact_public_source"], 1)
        self.assertFalse(config["access"]["critical_point_or_degree_extraction"])
        self.assertFalse(config["access"]["growth_association_testing"])

    def test_score_source_history_or_gpu_mutation_is_rejected(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["candidate"]["score"] = 33.0
        payload["candidate"]["historical_surface_vector_score_repaired"] = True
        payload["sources"]["metadata"][0]["sha256"] = "0" * 64
        payload["execution"]["ngpus"] = 1
        with self.assertRaises(VMRGrowthSurfaceStructureP0Error):
            validate_config(payload)

    def test_vtp_header_identifies_vector_phases_without_structure_extraction(self) -> None:
        config = load_config(CONFIG)
        result = inspect_vtp_header(_vtp(), config["access"])
        self.assertTrue(result["polydata"])
        self.assertTrue(result["coordinate_three_component"])
        self.assertEqual(result["wss_names"], ["WSS_0", "WSS_1"])
        self.assertEqual(result["phased_wss_names"], ["WSS_0", "WSS_1"])

    def test_synthetic_zip_enforces_three_part_case_and_crc_contract(self) -> None:
        config = load_config(CONFIG)
        case_id = "0199_H_CERE_CA"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / f"{case_id}_3D_RIGID_VTP.zip"
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for suffix in ("_last.vtp", "_dome.vtp", "_parent.vtp"):
                    archive.writestr(f"results/{case_id}{suffix}", _vtp())
            result = inspect_result_archive(path, case_id, config["access"])
        self.assertTrue(result["safe_unique_member_names"])
        self.assertTrue(result["no_symbolic_links"])
        self.assertEqual(result["regular_vtp_member_count"], 3)
        self.assertTrue(result["required_suffix_contract"])
        self.assertTrue(result["case_name_contract"])
        self.assertTrue(result["zip_crc_valid"])
        self.assertTrue(result["all_polydata"])
        self.assertTrue(result["all_three_component_coordinates"])
        self.assertEqual(result["minimum_member_wss_phase_count"], 2)

    def test_synthetic_metadata_uses_patient_pair_not_phase_as_unit(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        projects = []
        results = []
        sizes = []
        for pair_index, (growing_id, stable_id) in enumerate(config["sources"]["matched_pairs"]):
            projects.extend(
                [
                    {
                        "Name": growing_id,
                        "Species": "Human",
                        "Anatomy": "Cerebral",
                        "Disease": "Cerebral Aneurysm",
                        "Results": "1",
                        "Notes": f"Categorized as a growing aneurysm (increased in size by at least 1mm in two or more dimensions between checkups). Paired with stable aneurysm {stable_id}.",
                    },
                    {
                        "Name": stable_id,
                        "Species": "Human",
                        "Anatomy": "Cerebral",
                        "Disease": "Cerebral Aneurysm",
                        "Results": "1",
                        "Notes": f"Categorized as a stable aneurysm (no increase in size by at least 1mm in two or more dimensions between checkups). Paired with growing aneurysm {growing_id}.",
                    },
                ]
            )
            self.assertEqual(pair_index, pair_index)
        for item in config["sources"]["result_archives"]:
            case_id = item["case_id"]
            results.append(
                {
                    "Model Name": case_id,
                    "Full Simulation File Name": f"{case_id}_3D_RIGID_VTP.zip",
                    "Simulation Fidelity": "3D",
                    "Simulation Method": "Rigid Wall",
                    "Results Type": "Time-Resolved",
                    "Results File Type": "Surface (vtp)",
                    "Notes": "Simulation results include wall shear stress. Includes three files.",
                }
            )
            sizes.append(
                {
                    "Name": f"svresults/{case_id}/{case_id}_3D_RIGID_VTP.zip",
                    "Size": str(item["bytes"]),
                }
            )
        aggregate = inspect_metadata(projects, results, sizes, config)
        self.assertEqual(aggregate["unique_project_case_count"], 22)
        self.assertEqual(aggregate["growing_count"], 11)
        self.assertEqual(aggregate["stable_count"], 11)
        self.assertTrue(aggregate["reciprocal_pair_contract"])
        self.assertEqual(aggregate["unique_result_case_count"], 22)
        self.assertTrue(aggregate["size_manifest_exact"])

    def test_pbs_wrapper_forbids_dirty_repeat_gpu_and_other_server(self) -> None:
        script = (ROOT / "cluster" / "pbs_vmr_growth_surface_structure_p0.pbs").read_text()
        self.assertIn("ngpus=0", script)
        self.assertIn("status --porcelain", script)
        self.assertIn("resubmission is forbidden", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("--nv", script)


if __name__ == "__main__":
    unittest.main()
