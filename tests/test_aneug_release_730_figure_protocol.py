from __future__ import annotations

import copy
import unittest
from pathlib import Path

try:
    import torch
except ImportError:
    torch = None

from aurora.aneug_figure_protocol import (
    AneuGFigureProtocolError,
    reference_osi_summary,
    select_case_ordinals,
)
from aurora.aneug_release_730_figure_protocol import (
    build_release730_reference_selection,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_figure_protocol_v1.json"


def cycle(signs: list[float], nodes: int = 4) -> torch.Tensor:
    base = torch.tensor(signs, dtype=torch.float64).reshape(-1, 1, 1)
    direction = torch.tensor([1.0, 0.0, 0.0], dtype=torch.float64).reshape(1, 1, 3)
    scale = torch.arange(1, nodes + 1, dtype=torch.float64).reshape(1, nodes, 1)
    return base * direction * scale


class Release730FigureProtocolConfigTests(unittest.TestCase):
    def test_config_is_release730_sealed_and_non_executable(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["split"]["locked_test_cases"], 73)
        self.assertFalse(config["boundary"]["execute_now"])
        self.assertFalse(config["boundary"]["locked_test_access_before_T0"])
        self.assertFalse(
            config["reference_only_selection"]["candidate_or_baseline_values_used"]
        )

    def test_scope_mutations_fail_closed(self) -> None:
        config = load_config(CONFIG)
        for section, key, value, reason in (
            ("split", "locked_test_cases", 51, "split"),
            ("boundary", "execute_now", True, "boundary"),
            (
                "reference_only_selection",
                "candidate_or_baseline_values_used",
                True,
                "selection",
            ),
            (
                "reference_only_selection",
                "reference_tawss_floor_source",
                "locked_test_derived",
                "selection",
            ),
        ):
            changed = copy.deepcopy(config)
            changed[section][key] = value
            with self.assertRaisesRegex(AneuGFigureProtocolError, reason):
                validate_config(changed)

    def test_main_figure_layout_is_prospectively_fixed(self) -> None:
        config = load_config(CONFIG)
        layout = config["render_layout"]
        self.assertEqual(
            layout["audit_case_columns"],
            ["low_reference_OSI", "median_reference_OSI", "high_reference_OSI"],
        )
        self.assertEqual(layout["main_case_index"], 2)
        self.assertEqual(layout["main_case_column"], "high_reference_OSI")
        self.assertEqual(layout["main_figure_left_panel"], "method_schematic")
        self.assertEqual(
            layout["main_figure_right_panel"],
            "high_reference_OSI_surfaces_and_trace",
        )
        for key, value in (
            ("main_case_index", 1),
            ("main_case_column", "median_reference_OSI"),
            ("main_figure_left_panel", "three_case_grid"),
            ("main_figure_right_panel", "all_reference_OSI_surfaces"),
        ):
            changed = copy.deepcopy(config)
            changed["render_layout"][key] = value
            with self.assertRaisesRegex(AneuGFigureProtocolError, "render_layout"):
                validate_config(changed)


@unittest.skipIf(torch is None, "PyTorch is optional")
class Release730FigureProtocolTensorTests(unittest.TestCase):
    def test_release730_quantile_ordinals_are_fixed_for_73_cases(self) -> None:
        self.assertEqual(
            select_case_ordinals([float(value) for value in range(73)]),
            [7, 36, 65],
        )

    def test_selection_uses_all_73_references_and_no_predictions(self) -> None:
        config = load_config(CONFIG)
        cases = []
        for index in range(73):
            negative = min(index, 40)
            signs = [-1.0] * negative + [1.0] * (80 - negative)
            cases.append(
                {
                    "wss": cycle(signs),
                    "vertex_weights": torch.ones(4, dtype=torch.float64),
                }
            )
        output = build_release730_reference_selection(
            cases,
            torch.full((80,), 1.0 / 80.0, dtype=torch.float64),
            config,
            0.1,
        )
        self.assertEqual(output["locked_test_case_count"], 73)
        self.assertEqual(output["reference_phase_count"], 80)
        self.assertEqual(len(output["selected_locked_test_ordinals"]), 3)
        self.assertFalse(output["case_identifiers_included"])
        self.assertFalse(output["candidate_or_baseline_values_read"])
        self.assertFalse(output["processed_only_extra_values_read"])
        with self.assertRaisesRegex(AneuGFigureProtocolError, "phase_count"):
            build_release730_reference_selection(
                cases,
                torch.full((79,), 1.0 / 79.0, dtype=torch.float64),
                config,
                0.1,
            )
        changed = list(cases)
        changed[0] = {
            "wss": cycle([1.0] * 79),
            "vertex_weights": torch.ones(4, dtype=torch.float64),
        }
        with self.assertRaisesRegex(
            AneuGFigureProtocolError, "reference_cycle_shape"
        ):
            build_release730_reference_selection(
                changed,
                torch.full((80,), 1.0 / 80.0, dtype=torch.float64),
                config,
                0.1,
            )

    def test_train_frozen_floor_excludes_low_activity_osi_from_burden(self) -> None:
        signs = torch.tensor(
            [-1.0] * 40 + [1.0] * 40,
            dtype=torch.float64,
        ).reshape(80, 1, 1)
        low_activity = 1e-6 * signs * torch.tensor(
            [1.0, 0.0, 0.0], dtype=torch.float64
        ).reshape(1, 1, 3)
        active = torch.tensor(
            [1.0, 0.0, 0.0], dtype=torch.float64
        ).reshape(1, 1, 3).expand(80, -1, -1)
        summary = reference_osi_summary(
            torch.cat((low_activity, active), dim=1),
            torch.full((80,), 1.0 / 80.0, dtype=torch.float64),
            torch.ones(2, dtype=torch.float64),
            reference_tawss_floor=1e-4,
        )
        self.assertEqual(summary["osi_valid"].tolist(), [False, True])
        self.assertAlmostEqual(summary["area_weighted_mean_reference_osi"], 0.0)

    def test_historical_51_case_scope_is_rejected(self) -> None:
        config = load_config(CONFIG)
        cases = [
            {
                "wss": cycle([1.0] * 80),
                "vertex_weights": torch.ones(4, dtype=torch.float64),
            }
            for _ in range(51)
        ]
        with self.assertRaisesRegex(AneuGFigureProtocolError, "outer_case_count"):
            build_release730_reference_selection(
                cases,
                torch.full((80,), 1.0 / 80.0, dtype=torch.float64),
                config,
                0.1,
            )


if __name__ == "__main__":
    unittest.main()
