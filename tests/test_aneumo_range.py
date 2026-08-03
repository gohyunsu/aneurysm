from __future__ import annotations

import binascii
import io
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from aurora.aneumo_range import (
    AneumoRangeError,
    ZipMember,
    _request,
    archive_for_case,
    decode_member_payload,
    load_config,
    parse_central_directory,
    stage,
)

try:
    import h5py
    import numpy as np
except ImportError:  # pragma: no cover - lightweight local environment
    h5py = None
    np = None


class AneumoRangeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Path(__file__).parents[1] / "configs" / "aneumo_g2_pilot_v1.json"

    def test_reference_config_is_base_family_disjoint(self) -> None:
        config = load_config(self.config)
        split = config["split"]
        train = set(split["train_base_families"])
        validation = set(split["validation_base_families"])
        test = set(split["test_base_families"])
        self.assertFalse(train & validation)
        self.assertFalse(train & test)
        self.assertFalse(validation & test)

    def test_geometry_split_cannot_replace_base_family_split(self) -> None:
        payload = json.loads(self.config.read_text())
        payload["split"]["unit"] = "synthetic_geometry"
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "config.json"
            candidate.write_text(json.dumps(payload))
            with self.assertRaisesRegex(AneumoRangeError, "base family"):
                load_config(candidate)

    def test_archive_mapping(self) -> None:
        self.assertEqual(archive_for_case(1), "1.zip")
        self.assertEqual(archive_for_case(40), "1.zip")
        self.assertEqual(archive_for_case(41), "41.zip")
        self.assertEqual(archive_for_case(788), "761.zip")


class AneumoZipTests(unittest.TestCase):
    def _archive(self) -> bytes:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("1/npy/m=0.001/array_internal_1.npy", b"audited payload")
        return stream.getvalue()

    def test_central_directory_and_member_crc(self) -> None:
        archive = self._archive()
        eocd = archive.rfind(b"PK\x05\x06")
        values = struct.unpack_from("<4s4H2LH", archive, eocd)
        central_size, central_offset = int(values[5]), int(values[6])
        members = parse_central_directory(
            archive[central_offset : central_offset + central_size]
        )
        member = members["1/npy/m=0.001/array_internal_1.npy"]
        local_end = member.local_offset + 30 + len(member.name) + member.compressed_size
        decoded = decode_member_payload(archive[member.local_offset:local_end], member)
        self.assertEqual(decoded, b"audited payload")
        self.assertEqual(
            member.crc32, binascii.crc32(b"audited payload") & 0xFFFFFFFF
        )

    def test_crc_corruption_is_rejected(self) -> None:
        raw = b"content"
        compressed = __import__("zlib").compress(raw)[2:-4]
        name = "member.npy"
        header = struct.pack(
            "<4s5H3L2H",
            b"PK\x03\x04",
            20,
            0,
            8,
            0,
            0,
            0,
            len(compressed),
            len(raw),
            len(name),
            0,
        )
        member = ZipMember(name, 8, 123, len(compressed), len(raw), 0)
        with self.assertRaisesRegex(AneumoRangeError, "CRC32"):
            decode_member_payload(header + name.encode() + compressed, member)

    def test_ignored_range_is_rejected_before_reading_body(self) -> None:
        class Response:
            status = 200
            headers = {"content-length": "6878451054"}
            body_read = False

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                self.body_read = True
                return b"full archive"

        response = Response()
        with mock.patch("urllib.request.urlopen", return_value=response):
            with self.assertRaisesRegex(AneumoRangeError, "full-archive"):
                _request("https://example.invalid/1.zip", start=10, end=19)
        self.assertFalse(response.body_read)


@unittest.skipIf(np is None or h5py is None, "staging test requires numpy and h5py")
class AneumoStageTests(unittest.TestCase):
    def test_two_condition_stage_writes_field_axis(self) -> None:
        config = load_config(
            Path(__file__).parents[1] / "configs" / "aneumo_g2_pilot_v1.json"
        )
        config["asset_selection"].update(
            {
                "base_families": [1],
                "cases_by_base_family": {"1": [1, 2]},
                "cases": 2,
                "conditions_per_case": 2,
                "nodes_per_case": 4,
            }
        )
        config["dataset"]["mass_flows_kg_s"] = [0.001, 0.004]
        config["split"].update(
            {
                "train_base_families": [1],
                "validation_base_families": [],
                "test_base_families": [],
            }
        )
        config["_config_sha256"] = "synthetic-test"
        members = {}
        payloads = {}
        for case in (1, 2):
            coordinates = np.arange(18, dtype=np.float64).reshape(6, 3) + case
            for condition_index, mass_flow in enumerate((0.001, 0.004)):
                array = np.column_stack(
                    [
                        coordinates,
                        np.full((6, 4), case + condition_index, dtype=np.float64),
                    ]
                )
                stream = io.BytesIO()
                np.save(stream, array)
                raw = stream.getvalue()
                name = f"{case}/npy/m={mass_flow:g}/array_internal_{case}.npy"
                member = ZipMember(
                    name=name,
                    compression=0,
                    crc32=binascii.crc32(raw) & 0xFFFFFFFF,
                    compressed_size=len(raw),
                    uncompressed_size=len(raw),
                    local_offset=0,
                )
                members[name] = member
                payloads[name] = raw

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "staged.h5"
            with (
                mock.patch(
                    "aurora.aneumo_range.load_archive_index",
                    return_value=(members, {"entries": len(members)}),
                ),
                mock.patch(
                    "aurora.aneumo_range.fetch_member",
                    side_effect=lambda _, member: payloads[member.name],
                ),
            ):
                summary = stage(config, output)
            self.assertEqual(summary["members_crc_verified"], 4)
            with h5py.File(output, "r") as handle:
                self.assertEqual(
                    handle["geometries"]["1"]["pressure_velocity"].shape,
                    (2, 4, 4),
                )


if __name__ == "__main__":
    unittest.main()
