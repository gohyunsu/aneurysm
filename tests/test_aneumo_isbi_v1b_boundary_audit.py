import copy
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v1b_boundary_audit import (
    AneumoV1bBoundaryAuditError,
    load_config,
    parse_vtp_contract,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v1b_boundary_asset_audit.json"


class AneumoV1bBoundaryAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def test_reference_contract_is_valid_and_post_discovery(self) -> None:
        self.assertTrue(self.config["discovery_boundary"]["inspected_before_registration"])
        self.assertTrue(self.config["discovery_boundary"]["not_prospective_evidence"])

    def test_audit_cannot_read_validation_or_test_payload(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["access"]["test_payload_read"] = True
        with self.assertRaisesRegex(AneumoV1bBoundaryAuditError, "access"):
            validate_config(candidate)

    def test_pass_cannot_authorize_model_training(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["pass_authorizes"] = "train_boundary_gnn"
        with self.assertRaisesRegex(AneumoV1bBoundaryAuditError, "authorize"):
            validate_config(candidate)

    def test_vtp_contract_requires_patch_connectivity_and_fields(self) -> None:
        payload = b"""<?xml version='1.0'?>
<!-- patch='inlet' -->
<VTKFile type='PolyData'><Piece NumberOfPoints='4' NumberOfPolys='2'>
<DataArray Name='Points'/><DataArray Name='TimeValue'/><DataArray Name='U'/>
<DataArray Name='p'/><DataArray Name='connectivity'/><DataArray Name='offsets'/>
</Piece></VTKFile>"""
        parsed = parse_vtp_contract(payload, "inlet")
        self.assertEqual(parsed["points"], 4)
        with self.assertRaisesRegex(AneumoV1bBoundaryAuditError, "identity"):
            parse_vtp_contract(payload, "wall")


if __name__ == "__main__":
    unittest.main()
