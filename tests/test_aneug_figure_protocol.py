import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:
    torch = None

from aurora.aneug_figure_protocol import (
    AneuGFigureProtocolError,
    build_reference_selection,
    reference_osi_summary,
    select_case_ordinals,
    select_reference_trace_vertex,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]


def cycle(signs, nodes=4):
    base = torch.tensor(signs, dtype=torch.float64).reshape(-1, 1, 1)
    direction = torch.tensor([1.0, 0.0, 0.0], dtype=torch.float64).reshape(1, 1, 3)
    scale = torch.arange(1, nodes + 1, dtype=torch.float64).reshape(1, nodes, 1)
    return base * direction * scale


class AneuGFigureProtocolConfigTests(unittest.TestCase):
    def test_config_is_reference_only_and_non_executable(self):
        config = json.loads(
            (ROOT / "configs/aneug_confirmatory_figure_protocol_v1.json").read_text()
        )
        validate_config(config)
        self.assertFalse(
            config["reference_only_selection"]["candidate_or_baseline_values_used"]
        )
        self.assertFalse(config["boundary"]["execute_now"])


@unittest.skipIf(torch is None, "PyTorch is optional in the local lightweight environment")
class AneuGFigureProtocolTensorTests(unittest.TestCase):

    def test_reference_osi_distinguishes_unidirectional_and_oscillatory_cycles(self):
        phases = torch.full((4,), 0.25, dtype=torch.float64)
        areas = torch.ones(4, dtype=torch.float64)
        steady = reference_osi_summary(cycle([1, 1, 1, 1]), phases, areas)
        oscillatory = reference_osi_summary(cycle([1, -1, 1, -1]), phases, areas)
        self.assertAlmostEqual(steady["area_weighted_mean_reference_osi"], 0.0)
        self.assertAlmostEqual(oscillatory["area_weighted_mean_reference_osi"], 0.5)
        self.assertAlmostEqual(steady["area_weighted_osi_coverage"], 1.0)

    def test_case_quantile_selection_is_stable_and_prediction_blind(self):
        burdens = [float(value) for value in range(51)]
        selected = select_case_ordinals(burdens)
        self.assertEqual(selected, [5, 25, 45])
        reversed_order = list(reversed(burdens))
        self.assertEqual(select_case_ordinals(reversed_order), [45, 25, 5])

    def test_trace_vertex_uses_reference_weighted_quantile_and_tie_break(self):
        summary = {
            "osi": torch.tensor([0.0, 0.1, 0.2, 0.2], dtype=torch.float64),
            "osi_valid": torch.tensor([True, True, True, True]),
        }
        areas = torch.ones(4, dtype=torch.float64)
        self.assertEqual(
            select_reference_trace_vertex(summary, areas, quantile=0.9), 2
        )

    def test_full_selection_contains_no_identifiers_or_predictions(self):
        phases = torch.full((4,), 0.25, dtype=torch.float64)
        cases = []
        for index in range(51):
            negative = min(index, 25)
            signs = [-1.0] * negative + [1.0] * (50 - negative)
            cases.append(
                {
                    "wss": cycle(signs, nodes=4),
                    "vertex_weights": torch.ones(4, dtype=torch.float64),
                }
            )
        phase_weights = torch.full((50,), 1.0 / 50.0, dtype=torch.float64)
        output = build_reference_selection(cases, phase_weights)
        self.assertEqual(len(output["selected_outer_ordinals"]), 3)
        self.assertFalse(output["case_identifiers_included"])
        self.assertFalse(output["candidate_or_baseline_values_read"])

    def test_rejects_duplicate_quantile_ranks(self):
        with self.assertRaisesRegex(AneuGFigureProtocolError, "duplicate_quantile_rank"):
            select_case_ordinals([0.0, 1.0, 2.0], quantile_targets=(0.1, 0.2, 0.3))


if __name__ == "__main__":
    unittest.main()
