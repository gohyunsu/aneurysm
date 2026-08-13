"""Minimal, fail-closed Aneumo VTP and surface-vector utilities.

The module intentionally implements only the VTK XML contracts needed by the
prospective Aneumo transient target audit.  It has no VTK dependency, accepts
ASCII or appended raw/base64 arrays, and rejects unsupported encodings rather
than silently returning empty fields.
"""

from __future__ import annotations

import base64
import binascii
import dataclasses
import math
import re
import struct
import xml.etree.ElementTree as ET
import zlib
from typing import Iterable

import numpy as np


class TransientVTPError(RuntimeError):
    """Raised when a VTP or surface-vector contract is ambiguous."""


_DTYPES = {
    "Float32": "f4",
    "Float64": "f8",
    "Int8": "i1",
    "UInt8": "u1",
    "Int16": "i2",
    "UInt16": "u2",
    "Int32": "i4",
    "UInt32": "u4",
    "Int64": "i8",
    "UInt64": "u8",
}


@dataclasses.dataclass(frozen=True)
class PolyData:
    points: np.ndarray
    polygons: tuple[np.ndarray, ...]
    point_wss: np.ndarray
    cell_wss: np.ndarray | None


@dataclasses.dataclass(frozen=True)
class CriticalPoint:
    phase: str
    triangle_index: int
    position: np.ndarray
    signed_index: int
    determinant: float
    trace: float
    barycentric: np.ndarray


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _one_child(parent: ET.Element, name: str) -> ET.Element:
    matches = [child for child in parent if _local_name(child.tag) == name]
    if len(matches) != 1:
        raise TransientVTPError(f"expected one {name}, found {len(matches)}")
    return matches[0]


def _dtype(name: str, byte_order: str) -> np.dtype:
    if name not in _DTYPES:
        raise TransientVTPError(f"unsupported VTK scalar type: {name}")
    prefix = "<" if byte_order == "LittleEndian" else ">"
    if byte_order not in {"LittleEndian", "BigEndian"}:
        raise TransientVTPError(f"unsupported byte order: {byte_order}")
    return np.dtype(prefix + _DTYPES[name])


def _decode_compressed(
    payload: bytes,
    *,
    header_dtype: np.dtype,
    compressor: str,
) -> bytes:
    if compressor != "vtkZLibDataCompressor":
        raise TransientVTPError(f"unsupported VTK compressor: {compressor}")
    width = header_dtype.itemsize
    if len(payload) < 3 * width:
        raise TransientVTPError("compressed VTK header is truncated")
    first = np.frombuffer(payload[: 3 * width], dtype=header_dtype)
    blocks, block_size, last_size = (int(value) for value in first)
    if blocks <= 0 or block_size <= 0 or last_size <= 0 or last_size > block_size:
        raise TransientVTPError("invalid compressed VTK block header")
    header_bytes = (3 + blocks) * width
    if len(payload) < header_bytes:
        raise TransientVTPError("compressed VTK size table is truncated")
    sizes = np.frombuffer(payload[3 * width : header_bytes], dtype=header_dtype)
    cursor = header_bytes
    chunks: list[bytes] = []
    for index, raw_size in enumerate(sizes):
        size = int(raw_size)
        if size <= 0 or cursor + size > len(payload):
            raise TransientVTPError("compressed VTK block is truncated")
        try:
            chunk = zlib.decompress(payload[cursor : cursor + size])
        except zlib.error as exc:
            raise TransientVTPError("invalid zlib VTK block") from exc
        expected = last_size if index + 1 == blocks else block_size
        if len(chunk) != expected:
            raise TransientVTPError(
                f"decompressed VTK block length mismatch: {len(chunk)} != {expected}"
            )
        chunks.append(chunk)
        cursor += size
    if cursor != len(payload):
        raise TransientVTPError("compressed VTK array has trailing bytes")
    return b"".join(chunks)


def _decode_array(
    element: ET.Element,
    *,
    appended: bytes,
    header_dtype: np.dtype,
    byte_order: str,
    compressor: str | None,
) -> np.ndarray:
    scalar_dtype = _dtype(element.attrib.get("type", ""), byte_order)
    data_format = element.attrib.get("format", "ascii")
    if data_format == "ascii":
        text = element.text or ""
        array = np.fromstring(text, sep=" ", dtype=scalar_dtype)
    elif data_format == "appended":
        try:
            offset = int(element.attrib["offset"])
        except (KeyError, ValueError) as exc:
            raise TransientVTPError("invalid appended-array offset") from exc
        width = header_dtype.itemsize
        if offset < 0 or offset + width > len(appended):
            raise TransientVTPError("appended-array offset is outside payload")
        if compressor:
            # A compressed array is self-delimiting through its block-size table.
            first = np.frombuffer(appended[offset : offset + 3 * width], dtype=header_dtype)
            if first.size != 3:
                raise TransientVTPError("compressed appended header is truncated")
            blocks = int(first[0])
            table_end = offset + (3 + blocks) * width
            if blocks <= 0 or table_end > len(appended):
                raise TransientVTPError("invalid compressed appended block count")
            sizes = np.frombuffer(
                appended[offset + 3 * width : table_end], dtype=header_dtype
            )
            end = table_end + sum(int(value) for value in sizes)
            if end > len(appended):
                raise TransientVTPError("compressed appended payload is truncated")
            raw = _decode_compressed(
                appended[offset:end], header_dtype=header_dtype, compressor=compressor
            )
        else:
            length = int(np.frombuffer(appended[offset : offset + width], dtype=header_dtype)[0])
            start = offset + width
            end = start + length
            if length < 0 or end > len(appended):
                raise TransientVTPError("appended-array length is outside payload")
            raw = appended[start:end]
        if len(raw) % scalar_dtype.itemsize:
            raise TransientVTPError("VTK array byte count is not dtype-aligned")
        array = np.frombuffer(raw, dtype=scalar_dtype).copy()
    elif data_format == "binary":
        try:
            encoded = base64.b64decode("".join((element.text or "").split()), validate=True)
        except binascii.Error as exc:
            raise TransientVTPError("invalid inline base64 VTK array") from exc
        width = header_dtype.itemsize
        if len(encoded) < width:
            raise TransientVTPError("inline binary VTK header is truncated")
        length = int(np.frombuffer(encoded[:width], dtype=header_dtype)[0])
        raw = encoded[width:]
        if len(raw) != length or len(raw) % scalar_dtype.itemsize:
            raise TransientVTPError("inline binary VTK length mismatch")
        array = np.frombuffer(raw, dtype=scalar_dtype).copy()
    else:
        raise TransientVTPError(f"unsupported DataArray format: {data_format}")

    components = int(element.attrib.get("NumberOfComponents", "1"))
    if components <= 0 or array.size % components:
        raise TransientVTPError("VTK component count does not divide array length")
    return array.reshape(-1, components) if components > 1 else array


def parse_polydata(payload: bytes) -> PolyData:
    """Parse the geometry and WSS arrays from one VTK XML PolyData member."""

    marker = payload.find(b"<AppendedData")
    appended = b""
    if marker >= 0:
        tag_end = payload.find(b">", marker)
        closing = payload.rfind(b"</AppendedData>")
        if tag_end < 0 or closing < tag_end:
            raise TransientVTPError("malformed AppendedData element")
        tag = payload[marker : tag_end + 1].decode("ascii", errors="strict")
        encoding_match = re.search(r"\bencoding=['\"]([^'\"]+)['\"]", tag)
        encoding = encoding_match.group(1) if encoding_match else "raw"
        body = payload[tag_end + 1 : closing]
        sentinel = body.find(b"_")
        if sentinel < 0 or body[:sentinel].strip():
            raise TransientVTPError("AppendedData sentinel is absent")
        body = body[sentinel + 1 :]
        if encoding == "raw":
            appended = body
        elif encoding == "base64":
            try:
                appended = base64.b64decode(b"".join(body.split()), validate=True)
            except binascii.Error as exc:
                raise TransientVTPError("invalid appended base64 payload") from exc
        else:
            raise TransientVTPError(f"unsupported AppendedData encoding: {encoding}")
        xml_bytes = payload[:marker] + b"</VTKFile>"
    else:
        xml_bytes = payload

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise TransientVTPError("invalid VTK XML header") from exc
    if _local_name(root.tag) != "VTKFile" or root.attrib.get("type") != "PolyData":
        raise TransientVTPError("VTK file is not PolyData")
    byte_order = root.attrib.get("byte_order", "LittleEndian")
    header_dtype = _dtype(root.attrib.get("header_type", "UInt32"), byte_order)
    compressor = root.attrib.get("compressor")
    poly = _one_child(root, "PolyData")
    piece = _one_child(poly, "Piece")
    try:
        point_count = int(piece.attrib["NumberOfPoints"])
        polygon_count = int(piece.attrib["NumberOfPolys"])
    except (KeyError, ValueError) as exc:
        raise TransientVTPError("invalid PolyData counts") from exc

    points_node = _one_child(piece, "Points")
    point_arrays = [child for child in points_node if _local_name(child.tag) == "DataArray"]
    if len(point_arrays) != 1:
        raise TransientVTPError("Points must contain exactly one DataArray")
    points = _decode_array(
        point_arrays[0], appended=appended, header_dtype=header_dtype,
        byte_order=byte_order, compressor=compressor,
    )
    if points.shape != (point_count, 3) or not np.isfinite(points).all():
        raise TransientVTPError("point coordinate contract failed")

    polys_node = _one_child(piece, "Polys")
    arrays = {
        child.attrib.get("Name", ""): _decode_array(
            child, appended=appended, header_dtype=header_dtype,
            byte_order=byte_order, compressor=compressor,
        )
        for child in polys_node
        if _local_name(child.tag) == "DataArray"
    }
    if set(arrays) != {"connectivity", "offsets"}:
        raise TransientVTPError("Polys require connectivity and offsets arrays")
    connectivity = np.asarray(arrays["connectivity"], dtype=np.int64).reshape(-1)
    offsets = np.asarray(arrays["offsets"], dtype=np.int64).reshape(-1)
    if offsets.size != polygon_count or np.any(np.diff(offsets) <= 0):
        raise TransientVTPError("polygon offsets are invalid")
    if polygon_count and offsets[-1] != connectivity.size:
        raise TransientVTPError("polygon connectivity length does not reconcile")
    starts = np.concatenate(([0], offsets[:-1]))
    polygons = tuple(connectivity[start:end].copy() for start, end in zip(starts, offsets))
    if any(poly.size < 3 for poly in polygons):
        raise TransientVTPError("polygon with fewer than three vertices")
    if connectivity.size and (connectivity.min() < 0 or connectivity.max() >= point_count):
        raise TransientVTPError("polygon index is outside point array")

    def named_wss(section_name: str) -> np.ndarray | None:
        sections = [child for child in piece if _local_name(child.tag) == section_name]
        if len(sections) > 1:
            raise TransientVTPError(f"multiple {section_name} sections")
        if not sections:
            return None
        candidates = [
            child for child in sections[0]
            if _local_name(child.tag) == "DataArray"
            and child.attrib.get("Name") == "wallShearStress"
        ]
        if len(candidates) != 1:
            return None
        value = _decode_array(
            candidates[0], appended=appended, header_dtype=header_dtype,
            byte_order=byte_order, compressor=compressor,
        )
        if value.ndim != 2 or value.shape[1] != 3 or not np.isfinite(value).all():
            raise TransientVTPError(f"invalid {section_name} wallShearStress")
        return np.asarray(value, dtype=np.float64)

    point_wss = named_wss("PointData")
    cell_wss = named_wss("CellData")
    if point_wss is None or point_wss.shape != (point_count, 3):
        raise TransientVTPError("point wallShearStress vector is required")
    if cell_wss is not None and cell_wss.shape != (polygon_count, 3):
        raise TransientVTPError("cell wallShearStress count mismatch")
    return PolyData(
        points=np.asarray(points, dtype=np.float64), polygons=polygons,
        point_wss=point_wss, cell_wss=cell_wss,
    )


def triangulate(polygons: Iterable[np.ndarray], root_mode: str) -> np.ndarray:
    """Triangulate ordered polygons using one of two deterministic fans."""

    triangles: list[tuple[int, int, int]] = []
    for raw in polygons:
        polygon = [int(value) for value in raw]
        if root_mode == "first":
            ordered = polygon
        elif root_mode == "last":
            ordered = [polygon[-1], *polygon[:-1]]
        else:
            raise TransientVTPError(f"unknown triangulation root mode: {root_mode}")
        triangles.extend(
            (ordered[0], ordered[index], ordered[index + 1])
            for index in range(1, len(ordered) - 1)
        )
    result = np.asarray(triangles, dtype=np.int64)
    if result.ndim != 2 or result.shape[1:] != (3,):
        raise TransientVTPError("triangulation produced no valid triangle")
    return result


def vertex_normals(points: np.ndarray, polygons: tuple[np.ndarray, ...], mode: str) -> np.ndarray:
    """Compute fail-closed area-oriented point normals."""

    normals = np.zeros_like(points, dtype=np.float64)
    if mode == "polygon_newell":
        for polygon in polygons:
            vertices = points[polygon]
            nxt = np.roll(vertices, -1, axis=0)
            normal = np.array(
                [
                    np.sum((vertices[:, 1] - nxt[:, 1]) * (vertices[:, 2] + nxt[:, 2])),
                    np.sum((vertices[:, 2] - nxt[:, 2]) * (vertices[:, 0] + nxt[:, 0])),
                    np.sum((vertices[:, 0] - nxt[:, 0]) * (vertices[:, 1] + nxt[:, 1])),
                ]
            )
            normals[polygon] += normal
    elif mode == "triangle_area":
        for triangle in triangulate(polygons, "first"):
            p0, p1, p2 = points[triangle]
            normal = np.cross(p1 - p0, p2 - p0)
            normals[triangle] += normal
    else:
        raise TransientVTPError(f"unknown normal mode: {mode}")
    lengths = np.linalg.norm(normals, axis=1)
    if np.any(~np.isfinite(lengths)) or np.any(lengths <= 0):
        raise TransientVTPError("surface has zero or nonfinite point normal")
    return normals / lengths[:, None]


def project_tangent(vectors: np.ndarray, normals: np.ndarray) -> np.ndarray:
    if vectors.shape != normals.shape:
        raise TransientVTPError("vector and normal shapes differ")
    return vectors - np.sum(vectors * normals, axis=1, keepdims=True) * normals


def normal_component_fraction(vectors: np.ndarray, normals: np.ndarray) -> np.ndarray:
    magnitude = np.linalg.norm(vectors, axis=1)
    normal = np.abs(np.sum(vectors * normals, axis=1))
    return normal / np.maximum(magnitude, np.finfo(np.float64).tiny)


def extract_critical_points(
    points: np.ndarray,
    triangles: np.ndarray,
    vectors: np.ndarray,
    *,
    phase: str,
    interior_margin: float = 1e-4,
    determinant_relative_floor: float = 1e-10,
) -> list[CriticalPoint]:
    """Extract nondegenerate zeros of a piecewise-linear tangent vector field."""

    if not 0 <= interior_margin < 1 / 3:
        raise TransientVTPError("invalid barycentric interior margin")
    critical: list[CriticalPoint] = []
    for triangle_index, triangle in enumerate(triangles):
        xyz = points[triangle]
        e1_raw = xyz[1] - xyz[0]
        e1_length = float(np.linalg.norm(e1_raw))
        face_normal_raw = np.cross(e1_raw, xyz[2] - xyz[0])
        face_area2 = float(np.linalg.norm(face_normal_raw))
        if e1_length <= 0 or face_area2 <= 0:
            raise TransientVTPError("degenerate triangle")
        e1 = e1_raw / e1_length
        face_normal = face_normal_raw / face_area2
        e2 = np.cross(face_normal, e1)
        local_xy = np.stack(((xyz - xyz[0]) @ e1, (xyz - xyz[0]) @ e2), axis=1)
        local_v = np.stack((vectors[triangle] @ e1, vectors[triangle] @ e2), axis=1)
        field_difference = np.column_stack((local_v[1] - local_v[0], local_v[2] - local_v[0]))
        determinant = float(np.linalg.det(field_difference))
        scale = float(np.linalg.norm(field_difference, ord="fro") ** 2)
        if scale <= 0 or abs(determinant) <= determinant_relative_floor * scale:
            continue
        try:
            ab = np.linalg.solve(field_difference, -local_v[0])
        except np.linalg.LinAlgError:
            continue
        barycentric = np.array([1.0 - ab.sum(), ab[0], ab[1]])
        if np.any(barycentric <= interior_margin) or np.any(barycentric >= 1 - interior_margin):
            continue
        coordinate_difference = np.column_stack((local_xy[1], local_xy[2]))
        try:
            jacobian = field_difference @ np.linalg.inv(coordinate_difference)
        except np.linalg.LinAlgError as exc:
            raise TransientVTPError("degenerate local coordinate map") from exc
        jacobian_det = float(np.linalg.det(jacobian))
        if not math.isfinite(jacobian_det) or jacobian_det == 0:
            continue
        critical.append(
            CriticalPoint(
                phase=phase,
                triangle_index=triangle_index,
                position=barycentric @ xyz,
                signed_index=1 if jacobian_det > 0 else -1,
                determinant=jacobian_det,
                trace=float(np.trace(jacobian)),
                barycentric=barycentric,
            )
        )
    return critical


def bidirectional_signed_recall(
    left: list[CriticalPoint],
    right: list[CriticalPoint],
    *,
    radius: float,
) -> tuple[float, float]:
    """Return sign-aware nearest-neighbour recalls in both directions."""

    if radius <= 0:
        raise TransientVTPError("matching radius must be positive")

    def recall(source: list[CriticalPoint], target: list[CriticalPoint]) -> float:
        if not source:
            return 1.0 if not target else 0.0
        matched = 0
        for point in source:
            distances = [
                np.linalg.norm(point.position - candidate.position)
                for candidate in target
                if point.signed_index == candidate.signed_index
            ]
            matched += bool(distances and min(distances) <= radius)
        return matched / len(source)

    return recall(left, right), recall(right, left)
