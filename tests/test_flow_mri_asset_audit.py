import copy
import unittest
from pathlib import Path

from aurora.flow_mri_asset_audit import (
    FlowMRIAssetAuditError,
    load_config,
    parse_primary_header,
    parse_velocity_descriptor,
    run_audit,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "flow_mri_protocol_i0a_asset_audit.json"


class FlowMRIAssetAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def test_discovery_is_disclosed_and_not_prospective_evidence(self) -> None:
        boundary = self.config["discovery_boundary"]
        self.assertTrue(boundary["inspected_before_registration"])
        self.assertTrue(boundary["not_prospective_evidence"])
        self.assertFalse(boundary["field_values_inspected"])

    def test_field_payload_or_training_access_is_rejected(self) -> None:
        for key in ("processed_velocity_RAW_payloads", "REC_payloads", "training"):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.config)
                candidate["access"][key] = True
                with self.assertRaisesRegex(FlowMRIAssetAuditError, "cannot read"):
                    validate_config(candidate)

    def test_pass_cannot_authorize_a_method(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["pass_authorizes"] = "train_probabilistic_operator"
        with self.assertRaisesRegex(FlowMRIAssetAuditError, "authorize"):
                validate_config(candidate)

    def test_run_requires_an_exact_source_commit_before_network_access(self) -> None:
        with self.assertRaisesRegex(FlowMRIAssetAuditError, "exact 40-character"):
            run_audit(self.config, output=ROOT / "unused", git_commit="deadbeef")

    def test_velocity_descriptor_parser_preserves_axis_order(self) -> None:
        payload = b"""<GTFlow Raw Velocity File Description>
<DimensionSizes TZYX>24 40 144 144</DimensionSizes TZYX>
<VoxelSizeX [mm]>0.694</VoxelSizeX [mm]>
<VoxelSizeY [mm]>0.694</VoxelSizeY [mm]>
<VoxelSizeZ [mm]>0.75</VoxelSizeZ [mm]>
<TimeStep [ms]>0.034</TimeStep [ms]>
"""
        parsed = parse_velocity_descriptor(payload)
        self.assertEqual(parsed["dims_tzyx"], [24, 40, 144, 144])
        self.assertEqual(parsed["spacing_xyz_mm"], [0.694, 0.694, 0.75])
        self.assertEqual(parsed["time_step_descriptor_value"], 0.034)

    def test_primary_header_parser_handles_PAR_and_XML(self) -> None:
        par = b""". Max. number of cardiac phases : 20
. Scan resolution  (x, y) : 148 147
. Phase encoding velocity [cm/sec] : 55.000000 55.000000 55.000000
"""
        xml = b"""<Attribute Name="Max No Phases">20</Attribute>
<Attribute Name="Scan Resolution X">148</Attribute>
<Attribute Name="Scan Resolution Y">147</Attribute>
<Attribute Name="Phase Encoding Velocity">5.0000E+01 5.0000E+01</Attribute>
"""
        self.assertEqual(parse_primary_header(par)["venc_cm_s"], 55.0)
        self.assertEqual(parse_primary_header(xml)["venc_cm_s"], 50.0)
        self.assertEqual(parse_primary_header(xml)["scan_resolution_xy"], [148, 147])


if __name__ == "__main__":
    unittest.main()
