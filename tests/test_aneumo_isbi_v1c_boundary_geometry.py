import base64
import copy
import struct
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v1c_boundary_geometry import (
    AneumoV1cBoundaryGeometryError,
    load_config,
    parse_vtp_geometry,
    polygon_geometry,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v1c_boundary_geometry_staging_audit.json"


def _binary(values: bytes) -> str:
    return base64.b64encode(struct.pack("<Q", len(values)) + values).decode("ascii")


class AneumoV1cBoundaryGeometryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def _numpy(self):
        try:
            import numpy as np
        except ImportError as exc:
            raise unittest.SkipTest("numpy is unavailable") from exc
        return np

    def _triangle_vtp(self, patch: str = "inlet") -> bytes:
        np = self._numpy()
        points = np.asarray([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype="<f4")
        connectivity = np.asarray([0, 1, 2], dtype="<i8")
        offsets = np.asarray([3], dtype="<i8")
        return f"""<?xml version='1.0'?>
<!-- patch='{patch}' -->
<VTKFile type='PolyData' header_type='UInt64'>
<PolyData><Piece NumberOfPoints='3' NumberOfPolys='1'>
<Points><DataArray type='Float32' Name='Points' NumberOfComponents='3' format='binary'>{_binary(points.tobytes())}</DataArray></Points>
<Polys><DataArray type='Int64' Name='connectivity' format='binary'>{_binary(connectivity.tobytes())}</DataArray><DataArray type='Int64' Name='offsets' format='binary'>{_binary(offsets.tobytes())}</DataArray></Polys>
</Piece></PolyData></VTKFile>""".encode()

    def test_reference_contract_is_valid_and_train_only(self) -> None:
        self.assertEqual(self.config["access"]["splits"], ["train"])
        self.assertFalse(self.config["access"]["compact_cache_field_values_read"])

    def test_pass_cannot_authorize_model_or_test(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["pass_authorizes"] = "train_boundary_operator"
        with self.assertRaisesRegex(AneumoV1cBoundaryGeometryError, "authorize"):
            validate_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["access"]["test_payload_read"] = True
        with self.assertRaisesRegex(AneumoV1cBoundaryGeometryError, "access"):
            validate_config(candidate)

    def test_geometry_and_private_cache_contract_cannot_drift(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["audit"]["derive_outward_inlet_outlet_normals_from_geometry_only"] = False
        with self.assertRaisesRegex(AneumoV1cBoundaryGeometryError, "geometry"):
            validate_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["private_cache"]["contents"] = "boundary_and_velocity"
        with self.assertRaisesRegex(AneumoV1cBoundaryGeometryError, "private-cache"):
            validate_config(candidate)

    def test_inline_geometry_decode_and_polygon_area(self) -> None:
        geometry = parse_vtp_geometry(self._triangle_vtp(), "inlet")
        summary = polygon_geometry(geometry)
        self.assertAlmostEqual(summary["area_m2"], 0.5)
        self.assertEqual(summary["valid_polygon_fraction"], 1.0)
        self.assertEqual(
            geometry["decoded_arrays"], ["Points", "connectivity", "offsets"]
        )

    def test_patch_identity_is_required(self) -> None:
        with self.assertRaisesRegex(AneumoV1cBoundaryGeometryError, "identity"):
            parse_vtp_geometry(self._triangle_vtp("wall"), "inlet")

    def test_uint64_binary_header_is_required(self) -> None:
        payload = self._triangle_vtp().replace(b"header_type='UInt64'", b"header_type='UInt32'")
        with self.assertRaisesRegex(AneumoV1cBoundaryGeometryError, "uncompressed"):
            parse_vtp_geometry(payload, "inlet")


if __name__ == "__main__":
    unittest.main()
