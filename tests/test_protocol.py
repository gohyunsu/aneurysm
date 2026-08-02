import copy
import unittest
from pathlib import Path

from aurora.protocol import ProtocolError, canonical_hash, load_protocol, validate_protocol


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aurora_v1.json"


class ProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.protocol = load_protocol(CONFIG)

    def test_reference_protocol_is_valid(self) -> None:
        checks = validate_protocol(self.protocol)
        self.assertGreaterEqual(len(checks), 8)
        self.assertEqual(len(canonical_hash(self.protocol)), 64)

    def test_prospective_endpoint_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["task"]["endpoint"] = "five_year_rupture_risk"
        with self.assertRaisesRegex(ProtocolError, "cross-sectional"):
            validate_protocol(candidate)

    def test_aneux_cannot_be_real_cfd(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        aneux = next(item for item in candidate["datasets"] if item["name"] == "aneux")
        aneux["field_provenance"] = "real_cfd"
        with self.assertRaisesRegex(ProtocolError, "AneuX"):
            validate_protocol(candidate)

    def test_patient_bootstrap_is_required(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["evaluation"]["bootstrap_unit"] = "aneurysm"
        with self.assertRaisesRegex(ProtocolError, "patient"):
            validate_protocol(candidate)

    def test_duplicate_dataset_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.protocol)
        candidate["datasets"].append(copy.deepcopy(candidate["datasets"][0]))
        with self.assertRaisesRegex(ProtocolError, "duplicate"):
            validate_protocol(candidate)


if __name__ == "__main__":
    unittest.main()
