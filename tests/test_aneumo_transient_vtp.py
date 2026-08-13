from __future__ import annotations

import base64
import struct
import unittest

import numpy as np

from aurora.aneumo_transient_vtp import (
    TransientVTPError,
    bidirectional_signed_recall,
    extract_critical_points,
    normal_component_fraction,
    parse_polydata,
    project_tangent,
    triangulate,
    vertex_normals,
)


def _ascii_vtp() -> bytes:
    return b"""<?xml version='1.0'?>
<VTKFile type='PolyData' byte_order='LittleEndian' header_type='UInt32'>
<PolyData><Piece NumberOfPoints='4' NumberOfPolys='1'>
<PointData><DataArray type='Float64' Name='wallShearStress' NumberOfComponents='3' format='ascii'>
-1.2 -0.9 0  0.8 -0.9 0  0.8 1.1 0  -1.2 1.1 0
</DataArray></PointData>
<CellData><DataArray type='Float64' Name='wallShearStress' NumberOfComponents='3' format='ascii'>1 0 0</DataArray></CellData>
<Points><DataArray type='Float64' NumberOfComponents='3' format='ascii'>
-1 -1 0  1 -1 0  1 1 0  -1 1 0
</DataArray></Points>
<Polys>
<DataArray type='Int32' Name='connectivity' format='ascii'>0 1 2 3</DataArray>
<DataArray type='Int32' Name='offsets' format='ascii'>4</DataArray>
</Polys></Piece></PolyData></VTKFile>"""


def _base64_vtp() -> bytes:
    arrays = [
        np.asarray([[-1.2, -0.9, 0], [0.8, -0.9, 0], [0.8, 1.1, 0], [-1.2, 1.1, 0]], dtype="<f8"),
        np.asarray([0, 1, 2, 3], dtype="<i4"),
        np.asarray([4], dtype="<i4"),
        np.asarray([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]], dtype="<f8"),
    ]
    encoded = []
    for array in arrays:
        raw = array.tobytes()
        encoded.append(base64.b64encode(struct.pack("<I", len(raw)) + raw).decode())
    return f"""<?xml version='1.0'?>
<VTKFile type='PolyData' byte_order='LittleEndian' header_type='UInt32'>
<PolyData><Piece NumberOfPoints='4' NumberOfPolys='1'>
<PointData><DataArray type='Float64' Name='wallShearStress' NumberOfComponents='3' format='binary'>{encoded[3]}</DataArray></PointData>
<Points><DataArray type='Float64' NumberOfComponents='3' format='binary'>{encoded[0]}</DataArray></Points>
<Polys>
<DataArray type='Int32' Name='connectivity' format='binary'>{encoded[1]}</DataArray>
<DataArray type='Int32' Name='offsets' format='binary'>{encoded[2]}</DataArray>
</Polys></Piece></PolyData></VTKFile>""".encode()


class AneumoTransientVTPTests(unittest.TestCase):
    def test_ascii_and_inline_binary_read_identically(self) -> None:
        ascii_data = parse_polydata(_ascii_vtp())
        binary_data = parse_polydata(_base64_vtp())
        np.testing.assert_array_equal(ascii_data.points, binary_data.points)
        np.testing.assert_array_equal(ascii_data.point_wss, binary_data.point_wss)
        np.testing.assert_array_equal(ascii_data.polygons[0], binary_data.polygons[0])

    def test_projection_and_normal_fractions(self) -> None:
        data = parse_polydata(_ascii_vtp())
        normals = vertex_normals(data.points, data.polygons, "polygon_newell")
        projected = project_tangent(data.point_wss + normals, normals)
        np.testing.assert_allclose(projected, data.point_wss, atol=1e-12)
        np.testing.assert_allclose(normal_component_fraction(projected, normals), 0)

    def test_fan_choice_is_explicit_and_critical_point_is_signed(self) -> None:
        data = parse_polydata(_ascii_vtp())
        normals = vertex_normals(data.points, data.polygons, "triangle_area")
        field = project_tangent(data.point_wss, normals)
        first = extract_critical_points(
            data.points, triangulate(data.polygons, "first"), field, phase="4.01"
        )
        last = extract_critical_points(
            data.points, triangulate(data.polygons, "last"), field, phase="4.01"
        )
        self.assertEqual(len(first), 1)
        self.assertEqual(len(last), 1)
        self.assertEqual({point.signed_index for point in first}, {1})
        self.assertEqual(bidirectional_signed_recall(first, last, radius=1e-12), (1.0, 1.0))

    def test_boundary_zero_and_degenerate_field_are_not_counted(self) -> None:
        data = parse_polydata(_ascii_vtp())
        triangles = triangulate(data.polygons, "first")
        zero = np.zeros_like(data.point_wss)
        self.assertEqual(extract_critical_points(data.points, triangles, zero, phase="x"), [])

    def test_missing_vector_wss_fails_closed(self) -> None:
        payload = _ascii_vtp().replace(b"wallShearStress", b"magnitude")
        with self.assertRaisesRegex(TransientVTPError, "point wallShearStress"):
            parse_polydata(payload)


if __name__ == "__main__":
    unittest.main()
