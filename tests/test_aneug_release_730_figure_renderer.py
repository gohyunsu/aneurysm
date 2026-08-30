from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_figure_protocol import load_config
from aurora.aneug_release_730_figure_renderer import (
    Release730FigureRendererError,
    build_release730_render_payload,
    render_release730_confirmatory_figure,
    render_release730_regime_separated_figure,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_figure_protocol_v1.json"


def selection() -> dict:
    return {
        "schema_version": "aurora.aneug_release_730_confirmatory_figure.selection.v1",
        "protocol_id": "aneug_release_730_confirmatory_figure_v1",
        "selected_locked_test_ordinals": [7, 36, 65],
        "selected_reference_trace_vertex_ordinals": [2, 2, 2],
        "reference_tawss_floor": 0.01,
        "reference_tawss_floor_source": "common_frozen_checkpoint_train_only_value",
        "candidate_or_baseline_values_read": False,
        "processed_only_extra_values_read": False,
        "case_identifiers_included": False,
    }


def synthetic_case(scale: float) -> dict[str, torch.Tensor]:
    coordinates = torch.tensor(
        [
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.1],
            [1.0, 1.0, 0.2],
            [-1.0, 1.0, -0.1],
        ],
        dtype=torch.float32,
    )
    faces = torch.tensor([[0, 1, 2], [0, 2, 3]], dtype=torch.int64)
    phase = torch.arange(80, dtype=torch.float32).reshape(80, 1, 1)
    node = torch.arange(1, 5, dtype=torch.float32).reshape(1, 4, 1)
    reference = torch.cat(
        (
            scale * node * torch.cos(phase / 11.0),
            0.35 * scale * node * torch.sin(phase / 9.0),
            0.1 * scale * node.expand(80, -1, -1),
        ),
        dim=-1,
    )
    return {
        "coordinates": coordinates,
        "faces": faces,
        "display_mask": torch.ones(4, dtype=torch.bool),
        "reference_wss": reference,
        "selected_control_wss": 0.8 * reference,
        "proposal_wss": 0.95 * reference,
    }


class Release730FigureRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)
        self.phases = torch.full((80,), 1.0 / 80.0, dtype=torch.float32)
        self.cases = [synthetic_case(value) for value in (1.0, 2.0, 3.0)]

    def test_layout_matches_reserved_paper_footprint(self) -> None:
        layout = self.config["render_layout"]
        self.assertEqual(layout["paper_height_fraction"], 0.235)
        self.assertEqual(layout["audit_case_columns"], [
            "low_reference_OSI",
            "median_reference_OSI",
            "high_reference_OSI",
        ])
        self.assertEqual(layout["main_case_column"], "high_reference_OSI")
        self.assertEqual(layout["main_case_index"], 2)
        self.assertEqual(layout["main_figure_left_panel"], "method_schematic")
        self.assertEqual(
            layout["method_columns_within_case"],
            ["reference", "selected_control", "proposal"],
        )
        self.assertFalse(layout["error_or_candidate_dependent_limits"])

    def test_payload_limits_and_trace_direction_are_reference_only(self) -> None:
        first = build_release730_render_payload(
            self.cases, selection(), self.phases, self.config
        )
        changed = copy.deepcopy(self.cases)
        for case in changed:
            case["selected_control_wss"] *= 1000.0
            case["proposal_wss"] *= -500.0
        second = build_release730_render_payload(
            changed, selection(), self.phases, self.config
        )
        self.assertEqual(first["selection_ordinals"], second["selection_ordinals"])
        self.assertEqual(first["camera"], second["camera"])
        self.assertEqual(first["tawss_limits"], second["tawss_limits"])
        self.assertEqual(first["osi_limits"], [0.0, 0.5])
        self.assertEqual(
            first["signed_trace_limits"], second["signed_trace_limits"]
        )
        self.assertFalse(
            first["candidate_or_control_used_for_selection_limits_or_camera"]
        )
        self.assertTrue(first["osi_support_is_reference_defined"])
        self.assertEqual(first["reference_tawss_floor"], 0.01)
        self.assertEqual(len(first["cases"]), 3)
        self.assertEqual(first["main_case_index"], 2)
        self.assertEqual(first["main_case_label"], "high_reference_OSI")
        self.assertEqual(
            tuple(first["cases"][0]["methods"]["reference"]["signed_trace"].shape),
            (80,),
        )

    def test_osi_display_support_is_reference_defined_and_floor_aware(self) -> None:
        changed = copy.deepcopy(self.cases)
        changed[0]["reference_wss"][:, 0, :] *= 1e-6
        changed[0]["selected_control_wss"][:, 0, :] *= 1e-6
        changed[0]["proposal_wss"][:, 0, :] *= 1e-6
        payload = build_release730_render_payload(
            changed, selection(), self.phases, self.config
        )
        self.assertFalse(payload["cases"][0]["reference_osi_support"][0].item())
        self.assertTrue(payload["cases"][0]["reference_osi_support"][1:].all().item())

    def test_identifier_or_prediction_selected_payload_is_rejected(self) -> None:
        changed = selection()
        changed["case_identifiers_included"] = True
        with self.assertRaisesRegex(
            Release730FigureRendererError, "prediction_blind_selection"
        ):
            build_release730_render_payload(
                self.cases, changed, self.phases, self.config
            )
        changed = selection()
        del changed["reference_tawss_floor"]
        with self.assertRaisesRegex(
            Release730FigureRendererError, "reference_tawss_floor"
        ):
            build_release730_render_payload(
                self.cases, changed, self.phases, self.config
            )

    @unittest.skipIf(
        importlib.util.find_spec("matplotlib") is None,
        "Matplotlib is an optional rendering dependency",
    )
    def test_optional_renderer_writes_both_declared_formats(self) -> None:
        payload = build_release730_render_payload(
            self.cases, selection(), self.phases, self.config
        )
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "figure.pdf"
            png = Path(directory) / "figure.png"
            result = render_release730_confirmatory_figure(payload, pdf, png)
            self.assertTrue(pdf.is_file() and png.is_file())
            self.assertGreater(result["pdf_bytes"], 0)
            self.assertGreater(result["png_bytes"], 0)
            self.assertEqual(result["audit_case_count"], 3)
            self.assertEqual(result["main_case_index"], 2)
            self.assertEqual(result["main_case_label"], "high_reference_OSI")
            self.assertFalse(result["case_identifiers_included"])

    def _regime_payload(self) -> dict:
        historical = build_release730_render_payload(
            self.cases, selection(), self.phases, self.config
        )
        cases = []
        for case in historical["cases"]:
            cases.append(
                {
                    "coordinates": case["coordinates"],
                    "faces": case["faces"],
                    "display_mask": case["display_mask"],
                    "trace_vertex_ordinal": case["trace_vertex_ordinal"],
                    "trace_anchor_phase": case["trace_anchor_phase"],
                    "reference_osi_support": case["reference_osi_support"],
                    "methods": {
                        "reference": case["methods"]["reference"],
                        "transient_only": case["methods"]["selected_control"],
                        "eligible_steady": case["methods"]["proposal"],
                    },
                }
            )
        return {
            "schema_version": "aurora.aneug_release_730_regime_separated_figure.render_payload.v1",
            "protocol_id": "aneug_release_730_regime_separated_figure_v1",
            "display_training_seed": 20_260_903,
            "selection_ordinals": [7, 36, 65],
            "case_roles": [
                "low_reference_OSI",
                "median_reference_OSI",
                "high_reference_OSI",
            ],
            "main_case_index": 2,
            "main_case_role": "high_reference_OSI",
            "method_order": ["reference", "transient_only", "eligible_steady"],
            "method_display_labels": {
                "reference": "Reference",
                "transient_only": "T",
                "eligible_steady": "T+S",
            },
            "method_schematic": "geometry_encoder_to_cycle_decoder_with_train_only_disposable_steady_head",
            "camera": historical["camera"],
            "tawss_limits": historical["tawss_limits"],
            "osi_limits": historical["osi_limits"],
            "signed_trace_limits": historical["signed_trace_limits"],
            "reference_tawss_floor": historical["reference_tawss_floor"],
            "limits_camera_and_selection_are_reference_only": True,
            "steady_head_used_at_inference": False,
            "cases": cases,
            "case_identifiers_included": False,
            "paper_claim": False,
        }

    def test_regime_payload_rejects_identifier_or_inference_head_drift(self) -> None:
        payload = self._regime_payload()
        payload["case_identifiers_included"] = True
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                Release730FigureRendererError, "regime_payload_scope"
            ):
                render_release730_regime_separated_figure(
                    payload,
                    Path(directory) / "figure.pdf",
                    Path(directory) / "figure.png",
                )
        payload = self._regime_payload()
        payload["steady_head_used_at_inference"] = True
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                Release730FigureRendererError, "regime_payload_scope"
            ):
                render_release730_regime_separated_figure(
                    payload,
                    Path(directory) / "figure.pdf",
                    Path(directory) / "figure.png",
                )

    @unittest.skipIf(
        importlib.util.find_spec("matplotlib") is None,
        "Matplotlib is an optional rendering dependency",
    )
    def test_regime_renderer_writes_current_contract(self) -> None:
        payload = self._regime_payload()
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "regime.pdf"
            png = Path(directory) / "regime.png"
            result = render_release730_regime_separated_figure(payload, pdf, png)
            self.assertTrue(pdf.is_file() and png.is_file())
            self.assertEqual(
                result["schema_version"],
                "aurora.aneug_release_730_regime_separated_figure.render_result.v1",
            )
            self.assertEqual(result["display_training_seed"], 20_260_903)
            self.assertEqual(result["selection_ordinals"], [7, 36, 65])
            self.assertEqual(result["control_mode"], "transient_only")
            self.assertEqual(result["proposal_mode"], "eligible_steady")
            self.assertFalse(result["steady_head_used_at_inference"])
            self.assertTrue(result["limits_camera_and_selection_are_reference_only"])


if __name__ == "__main__":
    unittest.main()
