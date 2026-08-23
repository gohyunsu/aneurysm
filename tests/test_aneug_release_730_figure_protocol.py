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
        ):
            changed = copy.deepcopy(config)
            changed[section][key] = value
            with self.assertRaisesRegex(AneuGFigureProtocolError, reason):
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
            )

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
            )


if __name__ == "__main__":
    unittest.main()
