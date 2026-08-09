from __future__ import annotations

import json
import struct
import tempfile
import unittest
from pathlib import Path

from aurora.open_cta_physical_p0 import (
    DicomHeader,
    OpenCTAP0Error,
    VolumeFrame,
    headers_are_consistent,
    load_config,
    parse_dicom_header,
    parse_stl,
    select_headers,
)
from aurora.aneumo_range import ZipMember


def _explicit_element(group: int, element: int, vr: bytes, value: bytes) -> bytes:
    if len(value) % 2:
        value += b"\0" if vr == b"UI" else b" "
    if vr in {b"OB", b"OW", b"SQ", b"UN", b"UT"}:
        return struct.pack("<HH2sHL", group, element, vr, 0, len(value)) + value
    return struct.pack("<HH2sH", group, element, vr, len(value)) + value


def _dicom(position: float = 0.0, sop: str = "1.2.3.1") -> bytes:
    meta = _explicit_element(0x0002, 0x0010, b"UI", b"1.2.840.10008.1.2.1")
    body = b"".join(
        [
            _explicit_element(0x0008, 0x0018, b"UI", sop.encode()),
            _explicit_element(0x0008, 0x0060, b"CS", b"CT"),
            _explicit_element(0x0010, 0x0020, b"LO", b"case-1"),
            _explicit_element(0x0018, 0x0050, b"DS", b"0.5"),
            _explicit_element(0x0018, 0x0088, b"DS", b"0.5"),
            _explicit_element(0x0020, 0x000D, b"UI", b"1.2.3"),
            _explicit_element(0x0020, 0x000E, b"UI", b"1.2.3.4"),
            _explicit_element(
                0x0020,
                0x0032,
                b"DS",
                f"0\\0\\{position:g}".encode(),
            ),
            _explicit_element(0x0020, 0x0037, b"DS", b"1\\0\\0\\0\\1\\0"),
            _explicit_element(0x0020, 0x0052, b"UI", b"1.2.3.5"),
            _explicit_element(0x0028, 0x0010, b"US", struct.pack("<H", 8)),
            _explicit_element(0x0028, 0x0011, b"US", struct.pack("<H", 8)),
            _explicit_element(0x0028, 0x0030, b"DS", b"0.5\\0.5"),
            _explicit_element(0x7FE0, 0x0010, b"OW", b"\x01\x02"),
        ]
    )
    return b"\0" * 128 + b"DICM" + meta + body


class OpenCTAP0Tests(unittest.TestCase):
    def test_registered_config_is_valid(self) -> None:
        config = load_config("configs/open_cta_physical_p0.json")
        self.assertFalse(config["candidate"]["method_selected"])
        self.assertFalse(config["execution"]["gpu_requested"])
        self.assertEqual(config["selection"]["expected_selected_dicom_members"], 516)

    def test_config_cannot_authorize_gpu(self) -> None:
        payload = json.loads(Path("configs/open_cta_physical_p0.json").read_text())
        payload["execution"]["gpu_requested"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(payload))
            with self.assertRaises(OpenCTAP0Error):
                load_config(path)

    def test_config_cannot_change_source_or_gate_after_registration(self) -> None:
        baseline = json.loads(Path("configs/open_cta_physical_p0.json").read_text())
        variants = []
        changed_source = json.loads(json.dumps(baseline))
        changed_source["source"]["archive_bytes"] += 1
        variants.append(changed_source)
        changed_gate = json.loads(json.dumps(baseline))
        changed_gate["gate"]["checks"][
            "observed_header_slice_thickness_ratio_at_least"
        ] = 1.5
        variants.append(changed_gate)
        changed_selection = json.loads(json.dumps(baseline))
        changed_selection["selection"]["workers"] = 8
        variants.append(changed_selection)
        for payload in variants:
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "config.json"
                    path.write_text(json.dumps(payload))
                    with self.assertRaises(OpenCTAP0Error):
                        load_config(path)

    def test_parse_dicom_stops_at_pixel_data(self) -> None:
        header = parse_dicom_header(_dicom())
        self.assertEqual(header.modality, "CT")
        self.assertEqual(header.rows, 8)
        self.assertEqual(header.pixel_spacing, (0.5, 0.5))
        self.assertTrue(header.pixel_data_found)

    def test_header_consistency_requires_distinct_sop_and_shared_geometry(self) -> None:
        headers = [
            parse_dicom_header(_dicom(0, "1.2.3.1")),
            parse_dicom_header(_dicom(2, "1.2.3.2")),
            parse_dicom_header(_dicom(4, "1.2.3.3")),
        ]
        self.assertTrue(headers_are_consistent(headers))
        self.assertFalse(headers_are_consistent([headers[0], headers[0]]))

    def test_selects_numeric_first_middle_last(self) -> None:
        members = [
            ZipMember(str(index), 8, 0, 10, 10, index) for index in range(8)
        ]
        self.assertEqual([item.name for item in select_headers(members)], ["0", "4", "7"])

    def test_binary_stl_geometry_and_frame(self) -> None:
        vertices = [
            ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
            ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)),
            ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
            ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0)),
        ]
        payload = bytearray(b"test".ljust(80, b"\0") + struct.pack("<L", len(vertices)))
        for triangle in vertices:
            payload.extend(struct.pack("<3f", 0.0, 0.0, 0.0))
            for point in triangle:
                payload.extend(struct.pack("<3f", *point))
            payload.extend(struct.pack("<H", 0))
        frame = VolumeFrame(
            origin=(-1.0, -1.0, -1.0),
            x_direction=(1.0, 0.0, 0.0),
            y_direction=(0.0, 1.0, 0.0),
            normal=(0.0, 0.0, 1.0),
            x_max_mm=4.0,
            y_max_mm=4.0,
            z_min_mm=0.0,
            z_max_mm=4.0,
        )
        summary = parse_stl(bytes(payload), frame, tolerance_mm=0.0)
        self.assertTrue(summary.finite)
        self.assertEqual(summary.triangles, 4)
        self.assertEqual(summary.inside_frame_fraction, 1.0)
        self.assertAlmostEqual(summary.absolute_signed_volume_mm3, 1 / 6)


if __name__ == "__main__":
    unittest.main()
