from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from aurora.aneumo_transient_stability_p0 import (
    StabilityP0Error,
    aggregate_family,
    aggregate_p0,
    load_config,
    smoothed_tangent_perturbation,
)
from aurora.aneumo_transient_vtp import parse_polydata, project_tangent, vertex_normals
from test_aneumo_transient_vtp import _ascii_vtp


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_transient_structure_stability_p0_v1.json"


class AneumoTransientStabilityP0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(CONFIG)

    def test_selection_is_family_disjoint_from_d0_and_field_blind(self) -> None:
        selection = self.config["selection"]
        self.assertEqual(selection["required_family_count"], 12)
        self.assertEqual(selection["field_members"], 60)
        self.assertNotIn("1", {row["family_id"] for row in selection["selected"]})
        self.assertTrue(selection["selected_before_any_p0_field_read"])
        self.assertFalse(selection["development_case_or_phase_reused"])
        self.assertEqual(
            [(row["family_id"], row["case_id"]) for row in selection["selected"]],
            [
                ("34", 734),
                ("44", 922),
                ("15", 311),
                ("46", 958),
                ("19", 418),
                ("24", 523),
                ("27", 571),
                ("6", 111),
                ("22", 468),
                ("42", 847),
                ("47", 988),
                ("13", 240),
            ],
        )

    def test_license_and_mapping_gates_withdraw_v1_before_field_access(self) -> None:
        self.assertTrue(
            self.config["license_boundary"][
                "authoritative_resolution_required_before_staging_or_execution"
            ]
        )
        self.assertFalse(self.config["execution"]["authorized"])
        self.assertFalse(self.config["authorization"]["new_field_member_staging"])
        self.assertFalse(self.config["authorization"]["p0_execution"])
        self.assertFalse(self.config["authorization"]["current_panel_activation"])
        self.assertFalse(
            self.config["authorization"][
                "successor_panel_registration_before_authoritative_mapping"
            ]
        )
        self.assertTrue(self.config["selection"]["panel_withdrawn_before_field_access"])
        self.assertFalse(self.config["selection"]["inference_unit_verified"])
        mapping = self.config["family_mapping_boundary"]
        self.assertTrue(mapping["owner_acknowledged_connection_csv_error"])
        self.assertEqual(mapping["pinned_csv_case_2158"], "114_deform_10")
        self.assertEqual(mapping["owner_stated_correct_family"], "115_deform")
        self.assertTrue(mapping["current_12_family_panel_may_not_be_activated"])
        self.assertEqual(self.config["execution"]["ngpus"], 0)
        self.assertEqual(self.config["execution"]["excluded_server"], "junjinyong")
        self.assertEqual(
            self.config["perturbation"][
                "sensitivity_amplitudes_relative_to_phase_tangent_rms"
            ],
            [0.005, 0.01, 0.02],
        )

    def test_perturbation_is_deterministic_tangent_and_exact_rms_scaled(self) -> None:
        data = parse_polydata(_ascii_vtp())
        normals = vertex_normals(data.points, data.polygons, "polygon_newell")
        tangent = project_tangent(data.point_wss, normals)
        left = smoothed_tangent_perturbation(
            data, normals, tangent, seed=17, relative_amplitude=0.01, smoothing_steps=3
        )
        right = smoothed_tangent_perturbation(
            data, normals, tangent, seed=17, relative_amplitude=0.01, smoothing_steps=3
        )
        np.testing.assert_array_equal(left, right)
        delta = left - tangent
        np.testing.assert_allclose(np.sum(delta * normals, axis=1), 0, atol=1e-12)
        delta_rms = np.sqrt(np.mean(np.sum(delta * delta, axis=1)))
        field_rms = np.sqrt(np.mean(np.sum(tangent * tangent, axis=1)))
        self.assertAlmostEqual(delta_rms / field_rms, 0.01, places=12)

    def _phase(self, phase: str, passed: bool, informative: bool = True) -> dict:
        return {"phase": phase, "pass": passed, "checks": {"informative": informative}}

    def test_family_and_overall_gates_are_noncompensatory(self) -> None:
        phases = self.config["selection"]["phases"]
        good = aggregate_family(
            family_id="34",
            case_id=734,
            phase_rows=[self._phase(phase, index < 4) for index, phase in enumerate(phases)],
            mesh_static=True,
            config=self.config,
        )
        self.assertTrue(good["pass"])
        bad_mesh = aggregate_family(
            family_id="44",
            case_id=922,
            phase_rows=[self._phase(phase, True) for phase in phases],
            mesh_static=False,
            config=self.config,
        )
        self.assertFalse(bad_mesh["pass"])
        rows = []
        for index, selected in enumerate(self.config["selection"]["selected"]):
            rows.append({"family_id": selected["family_id"], "pass": index < 10})
        self.assertEqual(aggregate_p0(rows, self.config)["state"], "scientific_pass")
        rows[9]["pass"] = False
        self.assertEqual(aggregate_p0(rows, self.config)["state"], "scientific_fail")

    def test_missing_family_or_duplicate_phase_fails_closed(self) -> None:
        phases = self.config["selection"]["phases"]
        with self.assertRaisesRegex(StabilityP0Error, "phase panel"):
            aggregate_family(
                family_id="34",
                case_id=734,
                phase_rows=[self._phase(phase, True) for phase in phases[:-1]],
                mesh_static=True,
                config=self.config,
            )
        with self.assertRaisesRegex(StabilityP0Error, "family panel"):
            aggregate_p0([], self.config)

    def test_machine_contract_has_no_private_path_or_model_authority(self) -> None:
        text = CONFIG.read_text(encoding="utf-8")
        self.assertNotIn("/home/", text)
        self.assertFalse(self.config["authorization"]["method_or_architecture"])
        self.assertFalse(self.config["authorization"]["training"])
        self.assertFalse(self.config["authorization"]["paper_claim"])


if __name__ == "__main__":
    unittest.main()
