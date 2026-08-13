import importlib.util
import io
import struct
import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_aneumo_transient_archives.py"
SPEC = importlib.util.spec_from_file_location("aneumo_archive_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def make_zip(members: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return stream.getvalue()


def entries_from_zip(payload: bytes):
    return AUDIT.parse_central_directory(
        AUDIT.RangeBlock(data=payload, start=0, end=len(payload) - 1, total=len(payload))
    )


class AneumoTransientArchiveAuditTests(unittest.TestCase):
    def test_complete_cycle_with_canonical_wall_is_preprocessor_usable(self) -> None:
        members = {}
        for time_name in ["0.00"] + [f"{4 + i / 100:.2f}" for i in range(1, 101)]:
            for kind, extension in (
                ("inlet", "vtp"),
                ("internal", "vtu"),
                ("outlet", "vtp"),
                ("wall", "vtp"),
            ):
                members[f"1/{time_name}/{time_name}_{kind}.{extension}"] = b"x"
        summary = AUDIT.summarize_case(1, entries_from_zip(make_zip(members)))
        self.assertEqual(summary["time_count"], 101)
        self.assertEqual(
            summary["time_contract"],
            "initial_plus_complete_4p01_to_5p00_cycle",
        )
        self.assertTrue(summary["official_preprocessor_wall_contract"])
        self.assertTrue(summary["directory_level_structural_target_contract"])

    def test_noncanonical_wall_is_visible_and_not_silently_accepted(self) -> None:
        members = {}
        for time_name in ["0.00"] + [f"{4 + i / 100:.2f}" for i in range(1, 101)]:
            members[f"4/{time_name}/{time_name}_inlet.vtp"] = b"x"
            members[f"4/{time_name}/{time_name}_internal.vtu"] = b"x"
            members[f"4/{time_name}/{time_name}_outlet.vtp"] = b"x"
            members[
                f"4/{time_name}/{time_name}_fluid-wall-3931-__granite__35.vtp"
            ] = b"x"
        summary = AUDIT.summarize_case(4, entries_from_zip(make_zip(members)))
        self.assertFalse(summary["canonical_wall_filename_every_time"])
        self.assertFalse(summary["official_preprocessor_wall_contract"])
        self.assertTrue(summary["directory_level_structural_target_contract"])
        self.assertTrue(summary["noncanonical_wall_examples"])

    def test_partial_zero_based_case_is_not_a_complete_cycle(self) -> None:
        members = {}
        for index in range(30):
            time_name = f"{index / 100:.2f}"
            for kind, extension in (
                ("inlet", "vtp"),
                ("internal", "vtu"),
                ("outlet", "vtp"),
                ("wall", "vtp"),
            ):
                members[f"7/{time_name}/{time_name}_{kind}.{extension}"] = b"x"
        summary = AUDIT.summarize_case(7, entries_from_zip(make_zip(members)))
        self.assertEqual(summary["time_count"], 30)
        self.assertEqual(
            summary["time_contract"],
            "zero_based_contiguous_partial_or_alternate_sequence",
        )
        self.assertFalse(summary["official_cycle_directories_complete"])
        self.assertFalse(summary["directory_level_structural_target_contract"])

    def test_local_header_name_and_data_offset_are_checked(self) -> None:
        payload = make_zip({"7.zip": b"nested"})
        entry = entries_from_zip(payload)[0]
        block = AUDIT.RangeBlock(
            data=payload[:128], start=0, end=127, total=len(payload)
        )
        offset = AUDIT.parse_local_data_offset(block, entry.name)
        name_length, extra_length = struct.unpack_from("<HH", payload, 26)
        self.assertEqual(offset, 30 + name_length + extra_length)
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.parse_local_data_offset(block, "8.zip")

    def test_network_is_opt_in_and_byte_ceiling_is_finite(self) -> None:
        self.assertEqual(AUDIT.REVISION, "f801adee816c18d3e18b23e6fcb147fe4c264209")
        self.assertLessEqual(AUDIT.DEFAULT_MAX_BYTES, 100_000_000)
        self.assertEqual(AUDIT.DEFAULT_TAIL_BYTES, 65_536)


if __name__ == "__main__":
    unittest.main()
