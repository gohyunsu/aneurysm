"""Prospective physical-coordinate asset audit for the open CTA/STL release.

The audit reads the already-discovered ZIP64 index and metadata member, three
deterministically selected DICOM headers per case, and every aneurysm STL. It
does not decode DICOM PixelData or retain raw medical payloads. A pass only
permits a separate learned-method-free rasterization/task-adequacy audit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import struct
import subprocess
import sys
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .aneumo_range import ZipMember, _request, fetch_member, load_archive_index


class OpenCTAP0Error(RuntimeError):
    """Raised when the frozen open-CTA P0 contract cannot be evaluated."""


class IncompleteDicomHeader(OpenCTAP0Error):
    """Raised when another compressed prefix is required to reach PixelData."""


@dataclass(frozen=True)
class DicomHeader:
    transfer_syntax_uid: str
    modality: str
    patient_id: str
    study_uid: str
    series_uid: str
    frame_uid: str
    sop_uid: str
    rows: int
    columns: int
    pixel_spacing: tuple[float, float]
    slice_thickness: float
    spacing_between_slices: float | None
    image_position: tuple[float, float, float]
    image_orientation: tuple[float, float, float, float, float, float]
    pixel_data_found: bool


@dataclass(frozen=True)
class HeaderFetch:
    header: DicomHeader
    compressed_bytes_fetched: int
    member_fully_fetched: bool


@dataclass(frozen=True)
class VolumeFrame:
    origin: tuple[float, float, float]
    x_direction: tuple[float, float, float]
    y_direction: tuple[float, float, float]
    normal: tuple[float, float, float]
    x_max_mm: float
    y_max_mm: float
    z_min_mm: float
    z_max_mm: float


@dataclass(frozen=True)
class StlSummary:
    triangles: int
    vertices: int
    nondegenerate_fraction: float
    finite: bool
    absolute_signed_volume_mm3: float
    inside_frame_fraction: float


LONG_VR = {
    b"OB",
    b"OD",
    b"OF",
    b"OL",
    b"OV",
    b"OW",
    b"SQ",
    b"UC",
    b"UR",
    b"UT",
    b"UN",
}
TEXT_TAGS = {
    (0x0008, 0x0018): "sop_uid",
    (0x0008, 0x0060): "modality",
    (0x0010, 0x0020): "patient_id",
    (0x0018, 0x0050): "slice_thickness",
    (0x0018, 0x0088): "spacing_between_slices",
    (0x0020, 0x000D): "study_uid",
    (0x0020, 0x000E): "series_uid",
    (0x0020, 0x0032): "image_position",
    (0x0020, 0x0037): "image_orientation",
    (0x0020, 0x0052): "frame_uid",
    (0x0028, 0x0030): "pixel_spacing",
}
INT_TAGS = {
    (0x0028, 0x0010): "rows",
    (0x0028, 0x0011): "columns",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OpenCTAP0Error(message)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version") == "aurora.open_cta_physical_p0.v1",
        "Unexpected open-CTA P0 schema.",
    )
    _require(
        payload.get("status") == "preregistered_before_any_dicom_header_or_stl_payload",
        "The open-CTA P0 must remain prospectively registered.",
    )
    source = payload["source"]
    _require(
        {
            key: source.get(key)
            for key in (
                "record_id",
                "doi",
                "data_paper_doi",
                "license",
                "record_revision",
                "archive_name",
                "archive_url",
                "archive_bytes",
                "archive_md5",
                "archive_entries",
                "central_directory_bytes",
                "dicom_members",
                "stl_members",
                "metadata_member",
                "metadata_bytes",
                "metadata_sha256",
            )
        }
        == {
            "record_id": 15697196,
            "doi": "10.5281/zenodo.15697196",
            "data_paper_doi": "10.3390/data11040074",
            "license": "cc-by-4.0",
            "record_revision": 4,
            "archive_name": "Dataset.zip",
            "archive_url": (
                "https://zenodo.org/api/records/15697196/files/"
                "Dataset.zip/content"
            ),
            "archive_bytes": 25578845008,
            "archive_md5": "264ff9ee868c022d108b7c7aa7396d32",
            "archive_entries": 149452,
            "central_directory_bytes": 11207225,
            "dicom_members": 149329,
            "stl_members": 122,
            "metadata_member": "Metadata.csv",
            "metadata_bytes": 16458,
            "metadata_sha256": (
                "407cd3c35307b491d714c5a7c05a0a9e26ef92faa54d43259a704516bf2bc7f4"
            ),
        },
        "P0 source identity or archive contract changed.",
    )
    candidate = payload["candidate"]
    _require(
        candidate.get("candidate_estimand")
        == (
            "physical_space_grid_commutation_of_lesion_instance_support_"
            "cardinality_and_morphometry_under_deterministic_resampling"
        ),
        "P0 candidate estimand changed.",
    )
    _require(
        candidate.get("independent_unit") == "cta_case",
        "P0 independent unit changed.",
    )
    _require(
        candidate.get("direct_prior_threats")
        == [
            "consispace_voxel_spacing_resampling",
            "implicit_continuous_medical_segmentation",
            "resolution_invariant_autoencoding",
            "random_finite_set_probabilistic_detection",
            "lesion_detr_variable_cardinality_set_prediction",
            "topology_or_shape_guided_aneurysm_segmentation",
        ],
        "P0 direct-prior boundary changed.",
    )
    _require(candidate.get("method_selected") is False, "P0 cannot select a method.")
    _require(
        candidate.get("architecture_selected") is False,
        "P0 cannot select an architecture.",
    )
    execution = payload["execution"]
    _require(
        execution.get("source_commit_rule")
        == "exact_clean_public_git_head_at_execution",
        "P0 source-commit rule changed.",
    )
    _require(
        execution.get("network_access") == "http_byte_range_only",
        "P0 network boundary changed.",
    )
    _require(
        execution.get("write_scope") == "aggregate_result_only",
        "P0 write scope changed.",
    )
    _require(execution.get("gpu_requested") is False, "P0 must remain CPU-only.")
    _require(
        execution.get("raw_medical_payload_retained") is False,
        "P0 must not retain raw medical payloads.",
    )
    selection = payload["selection"]
    _require(
        {
            key: selection.get(key)
            for key in (
                "expected_cases",
                "expected_positive_cases",
                "expected_control_cases",
                "expected_lesions",
                "expected_multi_lesion_cases",
                "expected_miliary_lesions",
                "expected_selected_dicom_members",
                "dicom_compressed_chunk_bytes",
                "dicom_max_compressed_prefix_bytes_per_member",
                "expected_selected_stl_members",
                "workers",
            )
        }
        == {
            "expected_cases": 172,
            "expected_positive_cases": 82,
            "expected_control_cases": 90,
            "expected_lesions": 122,
            "expected_multi_lesion_cases": 24,
            "expected_miliary_lesions": 30,
            "expected_selected_dicom_members": 516,
            "dicom_compressed_chunk_bytes": 32768,
            "dicom_max_compressed_prefix_bytes_per_member": 262144,
            "expected_selected_stl_members": 122,
            "workers": 4,
        },
        "P0 sample or byte-range selection changed.",
    )
    _require(
        selection.get("dicom_member_rule")
        == "numeric_first_upper_median_last_unique",
        "DICOM selection changed.",
    )
    _require(
        selection.get("stl_member_rule") == "all_annotations",
        "STL selection changed.",
    )
    _require(
        int(selection.get("dicom_header_members_per_case", 0)) == 3,
        "P0 fixes three DICOM headers per case.",
    )
    gate = payload["gate"]
    _require(gate.get("all_checks_required") is True, "P0 is an all-check gate.")
    _require(
        gate.get("checks")
        == {
            "archive_and_metadata_contract_exact": True,
            "case_lesion_and_member_mapping_exact": True,
            "selected_dicom_headers_parse_without_pixel_value_decode": True,
            "dicom_study_and_patient_keys_are_one_to_one_across_172_cases": True,
            "three_sample_headers_are_series_geometry_consistent_per_case": True,
            "declared_image_count_matches_archive_for_all_nonmissing_metadata_cases": True,
            "metadata_and_header_slice_thickness_agree_for_at_least_120_cases": True,
            "observed_header_slice_thickness_ratio_at_least": 2.0,
            "all_stl_are_crc_verified_finite_and_at_least_99_percent_nondegenerate": True,
            "at_least_95_percent_stl_have_plausible_metadata_volume_ratio_0_5_to_2": True,
            (
                "at_least_95_percent_stl_have_99_percent_vertices_inside_"
                "dicom_frame_with_tolerance_mm"
            ): 3.0,
            "no_model_gpu_outer_test_or_pixel_value_decode": True,
        },
        "P0 gate checks or thresholds changed.",
    )
    _require(
        gate.get("pass_authorizes")
        == "register_method_free_p1_native_grid_rasterization_and_instance_stability_audit_only",
        "P0 pass authorization changed.",
    )
    _require(
        gate.get("failure_action")
        == "close_physical_grid_candidate_without_threshold_repair_method_gpu_or_outer_test",
        "P0 failure action changed.",
    )
    return payload


def _clean_text(value: bytes) -> str:
    return value.rstrip(b"\0 ").decode("ascii", errors="strict")


def _decimal_tuple(value: bytes, count: int) -> tuple[float, ...]:
    parts = _clean_text(value).split("\\")
    if len(parts) != count:
        raise OpenCTAP0Error(f"Expected {count} DICOM decimal values, found {len(parts)}.")
    result = tuple(float(item) for item in parts)
    _require(all(math.isfinite(item) for item in result), "Non-finite DICOM decimal value.")
    return result


def _element_header(
    payload: bytes, position: int, *, explicit_vr: bool
) -> tuple[tuple[int, int], bytes | None, int, int]:
    if position + 8 > len(payload):
        raise IncompleteDicomHeader("DICOM element header is incomplete.")
    group, element = struct.unpack_from("<HH", payload, position)
    if explicit_vr:
        vr = payload[position + 4 : position + 6]
        if vr in LONG_VR:
            if position + 12 > len(payload):
                raise IncompleteDicomHeader("Long-VR DICOM header is incomplete.")
            length = int(struct.unpack_from("<L", payload, position + 8)[0])
            value_start = position + 12
        else:
            length = int(struct.unpack_from("<H", payload, position + 6)[0])
            value_start = position + 8
    else:
        vr = None
        length = int(struct.unpack_from("<L", payload, position + 4)[0])
        value_start = position + 8
    return (group, element), vr, length, value_start


def parse_dicom_header(payload: bytes) -> DicomHeader:
    """Parse required DICOM geometry tags and stop before PixelData values."""

    if len(payload) < 132:
        raise IncompleteDicomHeader("DICOM preamble is incomplete.")
    _require(payload[128:132] == b"DICM", "DICOM magic is missing.")
    position = 132
    transfer_syntax = ""
    while True:
        tag, _, length, value_start = _element_header(payload, position, explicit_vr=True)
        if tag[0] != 0x0002:
            break
        if length == 0xFFFFFFFF:
            raise OpenCTAP0Error("Undefined-length file-meta element is unsupported.")
        value_end = value_start + length
        if value_end > len(payload):
            raise IncompleteDicomHeader("DICOM file-meta value is incomplete.")
        if tag == (0x0002, 0x0010):
            transfer_syntax = _clean_text(payload[value_start:value_end])
        position = value_end
    _require(bool(transfer_syntax), "TransferSyntaxUID is missing.")
    _require(
        transfer_syntax != "1.2.840.10008.1.2.2",
        "Explicit-VR big-endian DICOM is outside this frozen parser contract.",
    )
    explicit_vr = transfer_syntax != "1.2.840.10008.1.2"
    values: dict[str, Any] = {}
    pixel_data_found = False
    while position < len(payload):
        tag, vr, length, value_start = _element_header(
            payload, position, explicit_vr=explicit_vr
        )
        if tag == (0x7FE0, 0x0010):
            pixel_data_found = True
            break
        if length == 0xFFFFFFFF:
            raise OpenCTAP0Error(
                f"Undefined-length element {tag} occurred before PixelData."
            )
        value_end = value_start + length
        if value_end > len(payload):
            raise IncompleteDicomHeader("DICOM dataset value is incomplete.")
        value = payload[value_start:value_end]
        if tag in TEXT_TAGS:
            key = TEXT_TAGS[tag]
            if key == "pixel_spacing":
                values[key] = _decimal_tuple(value, 2)
            elif key == "image_position":
                values[key] = _decimal_tuple(value, 3)
            elif key == "image_orientation":
                values[key] = _decimal_tuple(value, 6)
            elif key in {"slice_thickness", "spacing_between_slices"}:
                text = _clean_text(value)
                values[key] = float(text) if text else None
            else:
                values[key] = _clean_text(value)
        elif tag in INT_TAGS:
            key = INT_TAGS[tag]
            if length == 2:
                values[key] = int(struct.unpack_from("<H", value, 0)[0])
            elif length == 4:
                values[key] = int(struct.unpack_from("<L", value, 0)[0])
            else:
                raise OpenCTAP0Error(f"Unexpected integer width for {tag}: {length}.")
        position = value_end
    if not pixel_data_found:
        raise IncompleteDicomHeader("PixelData tag has not been reached.")
    required = {
        "modality",
        "patient_id",
        "study_uid",
        "series_uid",
        "frame_uid",
        "sop_uid",
        "rows",
        "columns",
        "pixel_spacing",
        "slice_thickness",
        "image_position",
        "image_orientation",
    }
    missing = sorted(required - values.keys())
    _require(not missing, f"Required DICOM tags are missing: {', '.join(missing)}")
    _require(values["modality"] == "CT", "Selected series is not CT.")
    _require(int(values["rows"]) > 0 and int(values["columns"]) > 0, "Invalid DICOM matrix.")
    return DicomHeader(
        transfer_syntax_uid=transfer_syntax,
        modality=str(values["modality"]),
        patient_id=str(values["patient_id"]),
        study_uid=str(values["study_uid"]),
        series_uid=str(values["series_uid"]),
        frame_uid=str(values["frame_uid"]),
        sop_uid=str(values["sop_uid"]),
        rows=int(values["rows"]),
        columns=int(values["columns"]),
        pixel_spacing=tuple(values["pixel_spacing"]),
        slice_thickness=float(values["slice_thickness"]),
        spacing_between_slices=(
            None
            if values.get("spacing_between_slices") is None
            else float(values["spacing_between_slices"])
        ),
        image_position=tuple(values["image_position"]),
        image_orientation=tuple(values["image_orientation"]),
        pixel_data_found=pixel_data_found,
    )


def _member_data_start(url: str, member: ZipMember) -> tuple[int, int]:
    prefix, _ = _request(url, start=member.local_offset, end=member.local_offset + 4095)
    _require(prefix[:4] == b"PK\x03\x04", f"Invalid local ZIP header: {member.name}")
    local = struct.unpack_from("<4s5H3L2H", prefix, 0)
    name_length, extra_length = int(local[9]), int(local[10])
    name = prefix[30 : 30 + name_length].decode("utf-8")
    _require(name == member.name, f"Local ZIP name mismatch: {member.name}")
    return member.local_offset + 30 + name_length + extra_length, len(prefix)


def fetch_dicom_header(
    url: str,
    member: ZipMember,
    *,
    chunk_bytes: int,
    maximum_compressed_prefix: int,
) -> HeaderFetch:
    """Range-read a deflated prefix until the DICOM PixelData tag is reached."""

    data_start, local_bytes = _member_data_start(url, member)
    _require(member.compression in {0, 8}, f"Unsupported ZIP compression: {member.name}")
    decompressor = zlib.decompressobj(-15) if member.compression == 8 else None
    decoded = bytearray()
    consumed = 0
    while consumed < member.compressed_size and consumed < maximum_compressed_prefix:
        take = min(
            chunk_bytes,
            member.compressed_size - consumed,
            maximum_compressed_prefix - consumed,
        )
        chunk, _ = _request(
            url,
            start=data_start + consumed,
            end=data_start + consumed + take - 1,
        )
        consumed += len(chunk)
        decoded.extend(decompressor.decompress(chunk) if decompressor else chunk)
        try:
            header = parse_dicom_header(bytes(decoded))
        except IncompleteDicomHeader:
            continue
        return HeaderFetch(
            header=header,
            compressed_bytes_fetched=local_bytes + consumed,
            member_fully_fetched=consumed == member.compressed_size,
        )
    raise OpenCTAP0Error(
        f"DICOM header exceeded frozen compressed-prefix budget: {member.name}"
    )


def _norm(vector: Sequence[float]) -> float:
    return math.sqrt(sum(float(value) ** 2 for value in vector))


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(float(a) * float(b) for a, b in zip(left, right))


def _sub(left: Sequence[float], right: Sequence[float]) -> tuple[float, float, float]:
    return tuple(float(a) - float(b) for a, b in zip(left, right))  # type: ignore[return-value]


def _cross(left: Sequence[float], right: Sequence[float]) -> tuple[float, float, float]:
    return (
        float(left[1]) * float(right[2]) - float(left[2]) * float(right[1]),
        float(left[2]) * float(right[0]) - float(left[0]) * float(right[2]),
        float(left[0]) * float(right[1]) - float(left[1]) * float(right[0]),
    )


def _unit(vector: Sequence[float]) -> tuple[float, float, float]:
    length = _norm(vector)
    _require(length > 0, "Zero-length DICOM orientation vector.")
    return tuple(float(value) / length for value in vector)  # type: ignore[return-value]


def _close(left: Sequence[float], right: Sequence[float], tolerance: float = 1e-5) -> bool:
    return len(left) == len(right) and all(
        abs(float(a) - float(b)) <= tolerance for a, b in zip(left, right)
    )


def headers_are_consistent(headers: Sequence[DicomHeader]) -> bool:
    first = headers[0]
    return all(
        header.study_uid == first.study_uid
        and header.patient_id == first.patient_id
        and header.series_uid == first.series_uid
        and header.frame_uid == first.frame_uid
        and header.rows == first.rows
        and header.columns == first.columns
        and _close(header.pixel_spacing, first.pixel_spacing)
        and _close(header.image_orientation, first.image_orientation)
        and abs(header.slice_thickness - first.slice_thickness) <= 1e-3
        and header.sop_uid != first.sop_uid
        for header in headers[1:]
    )


def volume_frame(headers: Sequence[DicomHeader]) -> VolumeFrame:
    first = headers[0]
    x_direction = _unit(first.image_orientation[:3])
    y_direction = _unit(first.image_orientation[3:])
    _require(
        abs(_dot(x_direction, y_direction)) <= 1e-3,
        "DICOM axes are not orthogonal.",
    )
    normal = _unit(_cross(x_direction, y_direction))
    origin = first.image_position
    positions = [_dot(_sub(header.image_position, origin), normal) for header in headers]
    _require(max(positions) - min(positions) > 0, "Selected slices do not span a volume.")
    return VolumeFrame(
        origin=origin,
        x_direction=x_direction,
        y_direction=y_direction,
        normal=normal,
        x_max_mm=(first.columns - 1) * first.pixel_spacing[1],
        y_max_mm=(first.rows - 1) * first.pixel_spacing[0],
        z_min_mm=min(positions) - first.slice_thickness / 2,
        z_max_mm=max(positions) + first.slice_thickness / 2,
    )


def _inside_frame(point: Sequence[float], frame: VolumeFrame, tolerance_mm: float) -> bool:
    relative = _sub(point, frame.origin)
    x_value = _dot(relative, frame.x_direction)
    y_value = _dot(relative, frame.y_direction)
    z_value = _dot(relative, frame.normal)
    return (
        -tolerance_mm <= x_value <= frame.x_max_mm + tolerance_mm
        and -tolerance_mm <= y_value <= frame.y_max_mm + tolerance_mm
        and frame.z_min_mm - tolerance_mm <= z_value <= frame.z_max_mm + tolerance_mm
    )


def _binary_stl_vertices(payload: bytes) -> tuple[int, Iterable[tuple[float, float, float]]]:
    _require(len(payload) >= 84, "STL payload is truncated.")
    triangles = int(struct.unpack_from("<L", payload, 80)[0])
    _require(len(payload) == 84 + 50 * triangles, "Binary STL byte contract is invalid.")

    def iterator() -> Iterable[tuple[float, float, float]]:
        for index in range(triangles):
            offset = 84 + 50 * index + 12
            for vertex in range(3):
                yield tuple(struct.unpack_from("<3f", payload, offset + 12 * vertex))

    return triangles, iterator()


def parse_stl(payload: bytes, frame: VolumeFrame, tolerance_mm: float) -> StlSummary:
    """Parse a binary STL and compute privacy-safe geometry aggregates."""

    triangles, vertices = _binary_stl_vertices(payload)
    _require(triangles > 0, "STL contains no triangles.")
    iterator = iter(vertices)
    finite = True
    nondegenerate = 0
    inside = 0
    signed_volume = 0.0
    vertex_count = 0
    for _ in range(triangles):
        first = next(iterator)
        second = next(iterator)
        third = next(iterator)
        triangle = (first, second, third)
        for point in triangle:
            vertex_count += 1
            point_finite = all(math.isfinite(value) for value in point)
            finite = finite and point_finite
            if point_finite and _inside_frame(point, frame, tolerance_mm):
                inside += 1
        edge_a = _sub(second, first)
        edge_b = _sub(third, first)
        cross = _cross(edge_a, edge_b)
        area_twice = _norm(cross)
        if area_twice > 1e-10:
            nondegenerate += 1
        signed_volume += _dot(first, _cross(second, third)) / 6.0
    return StlSummary(
        triangles=triangles,
        vertices=vertex_count,
        nondegenerate_fraction=nondegenerate / triangles,
        finite=finite,
        absolute_signed_volume_mm3=abs(signed_volume),
        inside_frame_fraction=inside / vertex_count,
    )


def _case_dicom_members(members: Mapping[str, ZipMember]) -> dict[str, list[ZipMember]]:
    grouped: dict[str, list[tuple[int, ZipMember]]] = {}
    for name, member in members.items():
        if not name.startswith("Studies/") or not name.endswith(".dcm"):
            continue
        parts = name.split("/")
        _require(len(parts) == 3, f"Unexpected DICOM member path: {name}")
        try:
            numeric = int(parts[2][:-4])
        except ValueError as exc:
            raise OpenCTAP0Error(f"Non-numeric DICOM member stem: {name}") from exc
        grouped.setdefault(parts[1], []).append((numeric, member))
    return {
        case: [member for _, member in sorted(items)]
        for case, items in grouped.items()
    }


def select_headers(items: Sequence[ZipMember]) -> list[ZipMember]:
    positions = sorted({0, len(items) // 2, len(items) - 1})
    return [items[position] for position in positions]


def _case_rows(metadata: bytes) -> tuple[list[dict[str, str]], dict[str, list[dict[str, str]]]]:
    rows = list(
        csv.DictReader(io.StringIO(metadata.decode("cp1251")), delimiter=";")
    )
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["ID"], []).append(row)
    return rows, grouped


def _decimal(text: str) -> float | None:
    normalized = text.strip().replace(",", ".")
    if normalized.lower() in {"", "na", "n/a"}:
        return None
    value = float(normalized)
    _require(math.isfinite(value), "Non-finite metadata decimal.")
    return value


def _integer(text: str) -> int | None:
    normalized = text.strip().lower()
    if normalized in {"", "na", "n/a"}:
        return None
    return int(normalized)


def _lesion_member_name(row: Mapping[str, str]) -> str | None:
    token = row["IA(0/№_?)"]
    if token == "0":
        return None
    sequence, total = (int(item) for item in token.split("_"))
    suffix = "" if total == 1 else f"_{sequence}"
    return f"Annotations/an_{row['ID']}{suffix}.stl"


def _git_state(root: Path) -> tuple[str, bool]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return head, not bool(status)


def _quantiles(values: Sequence[float]) -> dict[str, float]:
    ordered = sorted(float(value) for value in values)
    _require(bool(ordered), "Cannot summarize an empty value list.")

    def at(fraction: float) -> float:
        return ordered[round((len(ordered) - 1) * fraction)]

    return {
        "minimum": ordered[0],
        "median": statistics.median(ordered),
        "p95": at(0.95),
        "maximum": ordered[-1],
    }


def run(config: Mapping[str, Any], *, repo_root: Path) -> dict[str, Any]:
    source = config["source"]
    selection = config["selection"]
    gate_spec = config["gate"]["checks"]
    url = str(source["archive_url"])
    members, archive = load_archive_index(url)
    metadata_member = members.get(str(source["metadata_member"]))
    _require(metadata_member is not None, "Metadata.csv is absent from the archive.")
    metadata = fetch_member(url, metadata_member)
    rows, rows_by_case = _case_rows(metadata)
    dicom_by_case = _case_dicom_members(members)
    stl_members = {
        name: member
        for name, member in members.items()
        if name.startswith("Annotations/") and name.endswith(".stl")
    }
    expected_stl_names = {
        name for row in rows if (name := _lesion_member_name(row)) is not None
    }

    archive_contract = (
        int(archive["content_length"]) == int(source["archive_bytes"])
        and int(archive["entries"]) == int(source["archive_entries"])
        and int(archive["central_directory_size"])
        == int(source["central_directory_bytes"])
        and len(dicom_by_case) == int(selection["expected_cases"])
        and sum(len(items) for items in dicom_by_case.values())
        == int(source["dicom_members"])
        and len(stl_members) == int(source["stl_members"])
        and len(metadata) == int(source["metadata_bytes"])
        and _sha256_bytes(metadata) == source["metadata_sha256"]
    )
    controls = sum(
        all(row["IA(0/№_?)"] == "0" for row in group)
        for group in rows_by_case.values()
    )
    positive_cases = len(rows_by_case) - controls
    multi_cases = sum(len(group) > 1 for group in rows_by_case.values())
    miliary = sum(row["Size"] == "miliary" for row in rows)
    mapping_exact = (
        len(rows_by_case) == int(selection["expected_cases"])
        and positive_cases == int(selection["expected_positive_cases"])
        and controls == int(selection["expected_control_cases"])
        and len(expected_stl_names) == int(selection["expected_lesions"])
        and multi_cases == int(selection["expected_multi_lesion_cases"])
        and miliary == int(selection["expected_miliary_lesions"])
        and expected_stl_names == set(stl_members)
        and set(rows_by_case) == set(dicom_by_case)
    )

    selected: list[tuple[str, ZipMember]] = []
    for case in sorted(dicom_by_case):
        chosen = select_headers(dicom_by_case[case])
        _require(len(chosen) == 3, f"Case {case} does not yield three unique headers.")
        selected.extend((case, member) for member in chosen)
    _require(
        len(selected) == int(selection["expected_selected_dicom_members"]),
        "Selected DICOM count changed from the frozen contract.",
    )

    def fetch(item: tuple[str, ZipMember]) -> tuple[str, HeaderFetch]:
        case, member = item
        return (
            case,
            fetch_dicom_header(
                url,
                member,
                chunk_bytes=int(selection["dicom_compressed_chunk_bytes"]),
                maximum_compressed_prefix=int(
                    selection["dicom_max_compressed_prefix_bytes_per_member"]
                ),
            ),
        )

    header_groups: dict[str, list[HeaderFetch]] = {case: [] for case in dicom_by_case}
    with ThreadPoolExecutor(max_workers=int(selection["workers"])) as executor:
        for case, fetched in executor.map(fetch, selected):
            header_groups[case].append(fetched)
    for group in header_groups.values():
        group.sort(
            key=lambda item: _dot(
                item.header.image_position,
                _unit(
                    _cross(
                        item.header.image_orientation[:3],
                        item.header.image_orientation[3:],
                    )
                ),
            )
        )

    header_parse_ok = (
        sum(len(group) for group in header_groups.values()) == len(selected)
        and all(item.header.pixel_data_found for group in header_groups.values() for item in group)
    )
    consistent_cases = {
        case: headers_are_consistent([item.header for item in group])
        for case, group in header_groups.items()
    }
    frames = {
        case: volume_frame([item.header for item in group])
        for case, group in header_groups.items()
        if consistent_cases[case]
    }
    series_consistent = len(frames) == int(selection["expected_cases"])
    first_headers = [group[0].header for group in header_groups.values()]
    unit_keys_one_to_one = (
        len({header.patient_id for header in first_headers})
        == int(selection["expected_cases"])
        and len({header.study_uid for header in first_headers})
        == int(selection["expected_cases"])
    )

    count_comparable = 0
    count_matches = 0
    thickness_comparable = 0
    thickness_matches = 0
    header_thickness: list[float] = []
    for case, group in rows_by_case.items():
        first_row = group[0]
        declared_count = _integer(first_row["Images count"])
        if declared_count is not None:
            count_comparable += 1
            count_matches += declared_count == len(dicom_by_case[case])
        declared_thickness = _decimal(first_row["Slice Thickness, mm"])
        observed_thickness = header_groups[case][0].header.slice_thickness
        header_thickness.append(observed_thickness)
        if declared_thickness is not None:
            thickness_comparable += 1
            thickness_matches += abs(declared_thickness - observed_thickness) <= 0.01
    image_count_match = count_comparable > 0 and count_matches == count_comparable
    thickness_match = thickness_matches >= 120
    thickness_ratio = max(header_thickness) / min(header_thickness)

    tolerance_mm = float(
        gate_spec[
            "at_least_95_percent_stl_have_99_percent_vertices_inside_dicom_frame_with_tolerance_mm"
        ]
    )
    stl_summaries: list[StlSummary] = []
    volume_ratios: list[float] = []
    for row in rows:
        name = _lesion_member_name(row)
        if name is None:
            continue
        _require(row["ID"] in frames, "STL case lacks a valid DICOM volume frame.")
        raw = fetch_member(url, stl_members[name])
        summary = parse_stl(raw, frames[row["ID"]], tolerance_mm)
        stl_summaries.append(summary)
        reference_volume = _decimal(row["Vobject, mm3"])
        _require(
            reference_volume is not None and reference_volume > 0,
            "Metadata volume is absent.",
        )
        volume_ratios.append(summary.absolute_signed_volume_mm3 / reference_volume)

    stl_geometry_ok = (
        len(stl_summaries) == int(selection["expected_selected_stl_members"])
        and all(summary.finite for summary in stl_summaries)
        and all(summary.nondegenerate_fraction >= 0.99 for summary in stl_summaries)
    )
    plausible_volume_count = sum(0.5 <= ratio <= 2.0 for ratio in volume_ratios)
    plausible_volume_fraction = plausible_volume_count / len(volume_ratios)
    aligned_count = sum(
        summary.inside_frame_fraction >= 0.99 for summary in stl_summaries
    )
    aligned_fraction = aligned_count / len(stl_summaries)
    no_forbidden_access = True

    checks = {
        "archive_and_metadata_contract_exact": archive_contract,
        "case_lesion_and_member_mapping_exact": mapping_exact,
        "selected_dicom_headers_parse_without_pixel_value_decode": header_parse_ok,
        "dicom_study_and_patient_keys_are_one_to_one_across_172_cases": (
            unit_keys_one_to_one
        ),
        "three_sample_headers_are_series_geometry_consistent_per_case": series_consistent,
        "declared_image_count_matches_archive_for_all_nonmissing_metadata_cases": image_count_match,
        "metadata_and_header_slice_thickness_agree_for_at_least_120_cases": thickness_match,
        "observed_header_slice_thickness_ratio_at_least_2_0": thickness_ratio >= float(
            gate_spec["observed_header_slice_thickness_ratio_at_least"]
        ),
        "all_stl_are_crc_verified_finite_and_at_least_99_percent_nondegenerate": stl_geometry_ok,
        "at_least_95_percent_stl_have_plausible_metadata_volume_ratio_0_5_to_2": (
            plausible_volume_fraction >= 0.95
        ),
        "at_least_95_percent_stl_have_99_percent_vertices_inside_dicom_frame_with_3_mm_tolerance": (
            aligned_fraction >= 0.95
        ),
        "no_model_gpu_outer_test_or_pixel_value_decode": no_forbidden_access,
    }
    all_passed = all(checks.values())
    source_commit, clean = _git_state(repo_root)
    _require(clean, "The public worktree must be clean at P0 execution.")
    return {
        "schema_version": "aurora.open_cta_physical_p0.public_result.v1",
        "experiment_id": config["experiment_id"],
        "as_of": config["as_of"],
        "status": "completed_passed_p0" if all_passed else "completed_failed_p0",
        "source_commit": source_commit,
        "source": {
            "record_id": source["record_id"],
            "doi": source["doi"],
            "license": source["license"],
            "declared_archive_md5": source["archive_md5"],
            "archive_bytes": archive["content_length"],
            "archive_entries": archive["entries"],
            "central_directory_bytes": archive["central_directory_size"],
            "metadata_sha256": _sha256_bytes(metadata),
        },
        "execution": {
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "process_exit_code": 0,
            "gpu_requested": False,
            "model_or_checkpoint_accessed": False,
            "dicom_pixel_values_decoded_or_inspected": False,
            "raw_payload_retained": False,
            "individual_identifier_published": False,
        },
        "audit_scope": {
            "cases": len(dicom_by_case),
            "dicom_members_in_archive": sum(len(items) for items in dicom_by_case.values()),
            "selected_dicom_headers": len(selected),
            "selected_dicom_compressed_prefix_bytes_fetched": sum(
                item.compressed_bytes_fetched
                for group in header_groups.values()
                for item in group
            ),
            "selected_dicom_members_fully_fetched": sum(
                item.member_fully_fetched
                for group in header_groups.values()
                for item in group
            ),
            "stl_members_crc_verified": len(stl_summaries),
            "stl_uncompressed_bytes_parsed": sum(
                stl_members[name].uncompressed_size for name in expected_stl_names
            ),
        },
        "task_units": {
            "positive_cases": positive_cases,
            "control_cases": controls,
            "lesions": len(expected_stl_names),
            "multi_lesion_cases": multi_cases,
            "miliary_lesions": miliary,
            "minimum_slices_per_case": min(len(items) for items in dicom_by_case.values()),
            "maximum_slices_per_case": max(len(items) for items in dicom_by_case.values()),
        },
        "geometry_aggregates": {
            "header_slice_thickness_mm": _quantiles(header_thickness),
            "header_slice_thickness_ratio": thickness_ratio,
            "metadata_image_count_comparable_cases": count_comparable,
            "metadata_image_count_matching_cases": count_matches,
            "metadata_thickness_comparable_cases": thickness_comparable,
            "metadata_thickness_matching_cases": thickness_matches,
            "stl_nondegenerate_fraction": _quantiles(
                [summary.nondegenerate_fraction for summary in stl_summaries]
            ),
            "stl_to_metadata_volume_ratio": _quantiles(volume_ratios),
            "plausible_volume_ratio_fraction": plausible_volume_fraction,
            "stl_vertices_inside_dicom_frame_fraction": _quantiles(
                [summary.inside_frame_fraction for summary in stl_summaries]
            ),
            "aligned_stl_fraction": aligned_fraction,
        },
        "gate": {
            "checks": checks,
            "passed_checks": sum(checks.values()),
            "total_checks": len(checks),
            "all_checks_passed": all_passed,
            "decision": (
                config["gate"]["pass_authorizes"]
                if all_passed
                else config["gate"]["failure_action"]
            ),
            "does_not_authorize": config["gate"]["does_not_authorize"],
        },
        "interpretation": (
            "P0 establishes only asset and physical-frame adequacy for a separate "
            "method-free grid/rasterization audit. It is not performance, novelty, "
            "repeat-acquisition evidence, or training authorization."
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        print("Open CTA physical-coordinate P0 contract valid")
        return 0
    if args.output is None:
        parser.error("--output is required unless --validate-only is used")
    result = run(config, repo_root=args.repo_root.resolve())
    result["config"] = {
        "path": args.config.as_posix(),
        "sha256": _sha256_bytes(args.config.read_bytes()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
