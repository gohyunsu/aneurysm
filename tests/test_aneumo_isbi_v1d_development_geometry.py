import base64
import copy
import json
import struct
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v1d_development_geometry import (
    AneumoV1dDevelopmentGeometryError,
    _development_cases,
    exact_surface_subset,
    load_config,
    parse_vtu_points,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v1d_development_geometry_cache.json"
STAGING = ROOT / "configs" / "aneumo_g2_pilot_v1.json"


def _binary(values: bytes) -> str:
    return base64.b64encode(struct.pack("<Q", len(values)) + values).decode("ascii")


class AneumoV1dDevelopmentGeometryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def _numpy(self):
        try:
            import numpy as np
        except ImportError as exc:
            raise unittest.SkipTest("numpy is unavailable") from exc
        return np

    def _vtu(self, include_pressure: bool = True) -> bytes:
        np = self._numpy()
        points = np.asarray(
            [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype="<f4"
        )
        velocity = np.zeros((4, 3), dtype="<f4")
        pressure = np.zeros(4, dtype="<f4")
        pressure_element = (
            f"<DataArray type='Float32' Name='p' format='binary'>"
            f"{_binary(pressure.tobytes())}</DataArray>"
            if include_pressure
            else ""
        )
        return f"""<?xml version='1.0'?>
<VTKFile type='UnstructuredGrid' header_type='UInt64'>
<UnstructuredGrid><Piece NumberOfPoints='4' NumberOfCells='1'>
<PointData><DataArray type='Float32' Name='U' NumberOfComponents='3' format='binary'>{_binary(velocity.tobytes())}</DataArray>{pressure_element}</PointData>
<Points><DataArray type='Float32' Name='Points' NumberOfComponents='3' format='binary'>{_binary(points.tobytes())}</DataArray></Points>
</Piece></UnstructuredGrid></VTKFile>""".encode()

    def test_reference_contract_is_development_only(self) -> None:
        self.assertEqual(self.config["access"]["splits"], ["train", "validation"])
        self.assertFalse(self.config["access"]["test_payload_read"])
        staging = json.loads(STAGING.read_text(encoding="utf-8"))
        cases = _development_cases(staging)
        self.assertEqual(sum(split == "train" for _, _, split in cases), 40)
        self.assertEqual(sum(split == "validation" for _, _, split in cases), 12)

    def test_pass_cannot_authorize_training_or_test(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["pass_authorizes"] = "train_boundary_operator"
        with self.assertRaisesRegex(AneumoV1dDevelopmentGeometryError, "authorize"):
            validate_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["access"]["test_payload_read"] = True
        with self.assertRaisesRegex(AneumoV1dDevelopmentGeometryError, "access"):
            validate_config(candidate)

    def test_payload_budget_and_exact_correspondence_cannot_drift(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["audit"]["total_payload_members"] = 519
        with self.assertRaisesRegex(AneumoV1dDevelopmentGeometryError, "audit"):
            validate_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["audit"][
            "require_every_boundary_point_in_reference_volume_points"
        ] = False
        with self.assertRaisesRegex(AneumoV1dDevelopmentGeometryError, "audit"):
            validate_config(candidate)

    def test_vtu_decodes_points_but_not_field_arrays(self) -> None:
        geometry = parse_vtu_points(self._vtu())
        self.assertEqual(geometry["points"].shape, (4, 3))
        self.assertEqual(geometry["decoded_arrays"], ["Points"])
        self.assertEqual(geometry["available_but_not_decoded"], ["U", "p"])

    def test_vtu_requires_field_contract_without_decoding_it(self) -> None:
        with self.assertRaisesRegex(AneumoV1dDevelopmentGeometryError, "field contract"):
            parse_vtu_points(self._vtu(include_pressure=False))

    def test_exact_surface_subset(self) -> None:
        np = self._numpy()
        volume = np.asarray(
            [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64
        )
        self.assertTrue(exact_surface_subset(volume[:3], volume))
        shifted = volume[:3].copy()
        shifted[0, 0] += 1e-12
        self.assertFalse(exact_surface_subset(shifted, volume))


if __name__ == "__main__":
    unittest.main()
