from __future__ import annotations

import copy
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from aurora.aneurisk_conformal_degree_p0 import (
    AneuriskConformalDegreeP0Error,
    inspect_archive,
    inspect_vtp_header,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneurisk_conformal_degree_p0.json"


def _vtp() -> bytes:
    return b"""<?xml version="1.0"?>
<VTKFile type="PolyData" version="1.0">
  <PolyData><Piece NumberOfPoints="3" NumberOfPolys="1">
    <PointData>
      <DataArray Name="WSS_cycle_average_Pa" NumberOfComponents="3" type="Float32"/>
    </PointData>
    <FieldData>
      <DataArray Name="Age_years" type="Float32"/>
      <DataArray Name="inflow_waveform_group" type="Int32"/>
      <DataArray Name="coordinate_unit_meter" type="String"/>
    </FieldData>
    <Points><DataArray NumberOfComponents="3" type="Float32"/></Points>
  </Piece></PolyData>
</VTKFile>
"""


class AneuriskConformalDegreeP0Tests(unittest.TestCase):
    def test_reference_contract_is_fresh_cpu_only_and_one_shot(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["candidate"]["score"], 32.5)
        self.assertEqual(sum(config["candidate"]["axis_scores"]), 32.5)
        self.assertFalse(config["candidate"]["historical_surface_vector_score_repaired"])
        self.assertFalse(config["candidate"]["historical_surface_vector_p0_rerun"])
        self.assertFalse(config["candidate"]["method_selected"])
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["excluded_server"], "junjinyong")
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertEqual(config["execution"]["maximum_submissions_for_exact_public_source"], 1)
        self.assertFalse(config["access"]["critical_point_extraction"])
        self.assertFalse(config["access"]["conformal_calibration"])

    def test_score_source_history_or_gpu_mutation_is_rejected(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["candidate"]["score"] = 33.0
        payload["candidate"]["historical_surface_vector_score_repaired"] = True
        payload["sources"]["archive"]["md5"] = "0" * 32
        payload["execution"]["ngpus"] = 1
        with self.assertRaises(AneuriskConformalDegreeP0Error):
            validate_config(payload)

    def test_vtp_header_identifies_cycle_average_vector_and_input_contract(self) -> None:
        config = load_config(CONFIG)
        result = inspect_vtp_header(_vtp(), config["access"])
        self.assertTrue(result["polydata"])
        self.assertTrue(result["coordinate_three_component"])
        self.assertEqual(result["wss_signatures"], ["point:WSS_cycle_average_Pa"])
        self.assertEqual(result["cycle_wss_signatures"], ["point:WSS_cycle_average_Pa"])
        self.assertTrue(result["has_coordinate_unit_semantics"])
        self.assertTrue(result["has_wss_unit_semantics"])
        self.assertTrue(result["has_age_or_inflow_semantics"])

    def test_synthetic_archive_aggregates_by_patient_case(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["access"]["exact_unique_case_ids"] = 2
        config["access"]["minimum_vtp_members"] = 2
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                for case_id in ("C0001", "C0002"):
                    payload = _vtp()
                    info = tarfile.TarInfo(f"Aneurisk/{case_id}/surface.vtp")
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))
            result = inspect_archive(path, config)
        self.assertTrue(result["safe_unique_regular_contract"])
        self.assertEqual(result["vtp_member_count"], 2)
        self.assertEqual(result["unique_case_id_count"], 2)
        self.assertTrue(result["every_vtp_is_polydata"])
        self.assertEqual(result["common_cycle_wss_signatures"], ["point:WSS_cycle_average_Pa"])
        self.assertTrue(result["every_case_has_explicit_units_and_input_contract"])

    def test_pbs_wrapper_forbids_dirty_repeat_gpu_and_other_server(self) -> None:
        script = (ROOT / "cluster" / "pbs_aneurisk_conformal_degree_p0.pbs").read_text()
        self.assertIn("ngpus=0", script)
        self.assertIn("status --porcelain", script)
        self.assertIn("resubmission is forbidden", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("--nv", script)


if __name__ == "__main__":
    unittest.main()
