from __future__ import annotations

import copy
import unittest
from pathlib import Path

from aurora.aneug_release_730_matched_information_analysis import (
    CELL_ORDER,
    MatchedInformationAnalysisError,
)
from aurora.aneug_release_730_multiseed_confirmation import (
    FRESH_TRAINING_SEEDS,
    MultiseedConfirmationError,
    analyze_multiseed_confirmation,
    load_config,
)
from aurora.aneug_release_730_matched_information_analysis import (
    load_config as load_matched_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_multiseed_confirmation_v1.json"
MATCHED = ROOT / "configs" / "aneug_release_730_matched_information_analysis_v1.json"


def rows(offset: float, coverage: float) -> list[dict[str, float]]:
    return [
        {
            "field_relative_l2": 0.50 + offset + index * 1e-5,
            "mean_wss_vector_error": 0.40 + offset,
            "tawss_normalized_absolute_error": 0.30 + offset,
            "osi_mae": 0.02 + offset * 0.01,
            "osi_coverage": coverage,
        }
        for index in range(73)
    ]


def cell(label: str, training_seed: int, offset: float, coverage: float) -> dict:
    steady = label.endswith("TS")
    control = label.startswith("control")
    return {
        "schema_version": "aurora.aneug_release_730_matched_information_cell.v1",
        "status": "complete_validation_development",
        "model_role": "selected_control" if control else "selected_proposal",
        "information_mode": "eligible_steady" if steady else "transient_only",
        "validation_case_digest":
        "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024",
        "private_split_manifest_sha256":
        "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f",
        "validation_loader_order_sha256":
        "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "eligible_steady_rows": 13_985 if steady else 0,
        "eligible_steady_case_digest": (
            "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc"
            if steady
            else None
        ),
        "steady_exposure_schedule_protocol_id": (
            "aneug_release_730_steady_exposure_schedule_v1" if steady else None
        ),
        "steady_exposure_schedule_config_sha256": (
            "3509191bd2c3e3294488ab5018109f3beccd402599a17e16dd8696d1deeaceaf"
            if steady
            else None
        ),
        "steady_exposure_algorithm": (
            "sha256_ranked_full_cycle_without_replacement_v1" if steady else None
        ),
        "steady_exposure_seed": 20_260_821 if steady else None,
        "steady_exposure_epochs": 80 if steady else 0,
        "steady_examples_consumed": 46_720 if steady else 0,
        "steady_exposure_prefix_sha256": "a" * 64 if steady else None,
        "transient_training_protocol_sha256": "b" * 64 if control else "c" * 64,
        "training_seed": training_seed,
        "transient_case_cycles_consumed": 46_720,
        "optimizer_steps": 6_680,
        "training_gpu_seconds": 100.0,
        "peak_gpu_memory_bytes": 1_000_000,
        "active_parameter_count": 2_000,
        "steady_head_active": steady,
        "steady_objective_scale_result_sha256": "d" * 64 if steady else None,
        "additional_steady_forward_backward_work": steady,
        "case_ids_included": False,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "paper_result_or_claim": False,
        "per_case_without_identifiers": rows(offset, coverage),
    }


def five_seed_cells() -> dict[int, dict[str, dict]]:
    output: dict[int, dict[str, dict]] = {}
    for seed_index, training_seed in enumerate(FRESH_TRAINING_SEEDS):
        jitter = seed_index * 0.001
        output[training_seed] = {
            "control_T": cell("control_T", training_seed, jitter, 0.80),
            "control_TS": cell("control_TS", training_seed, jitter - 0.03, 0.85),
            "proposal_T": cell("proposal_T", training_seed, jitter - 0.05, 0.90),
            "proposal_TS": cell("proposal_TS", training_seed, jitter - 0.10, 0.96),
        }
    return output


class MultiseedConfirmationTests(unittest.TestCase):
    def test_config_fixes_five_fresh_seeds_without_gate(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(tuple(config["scope"]["fresh_training_seeds"]), FRESH_TRAINING_SEEDS)
        self.assertEqual(config["scope"]["seed_count"], 5)
        self.assertIsNone(config["analysis"]["minimum_favorable_seed_count"])
        self.assertFalse(config["decision"]["automatic_test_authorization"])
        self.assertFalse(config["boundary"]["locked_test_or_extra_access"])

    def test_reports_crossed_bootstrap_and_seed_consistency(self) -> None:
        output = analyze_multiseed_confirmation(
            five_seed_cells(),
            load_matched_config(MATCHED),
            load_config(CONFIG),
            replicates=200,
            seed=7,
        )
        field = output["crossed_seed_case_contrasts"]["proposal_minus_control_T"][
            "field_relative_l2"
        ]
        self.assertAlmostEqual(field["point_delta"], -0.05)
        self.assertEqual(field["favorable_seed_count"], 5)
        self.assertEqual(field["training_seed_count"], 5)
        self.assertEqual(len(field["per_seed_point_deltas"]), 5)
        self.assertEqual(field["bootstrap_probability_favorable_direction"], 1.0)
        coverage = output["crossed_seed_case_contrasts"][
            "proposal_minus_control_T"
        ]["osi_coverage"]
        self.assertEqual(coverage["direction"], "higher")
        self.assertEqual(coverage["favorable_seed_count"], 5)
        self.assertIsNone(output["automatic_test_authorization"])
        self.assertFalse(output["locked_test_or_extra_values_read"])

    def test_is_deterministic(self) -> None:
        inputs = five_seed_cells()
        matched = load_matched_config(MATCHED)
        config = load_config(CONFIG)
        first = analyze_multiseed_confirmation(
            inputs, matched, config, replicates=100, seed=11
        )
        second = analyze_multiseed_confirmation(
            inputs, matched, config, replicates=100, seed=11
        )
        self.assertEqual(first, second)

    def test_rejects_missing_or_relabelled_seed(self) -> None:
        inputs = five_seed_cells()
        del inputs[FRESH_TRAINING_SEEDS[-1]]
        with self.assertRaisesRegex(MultiseedConfirmationError, "fresh_seed_set"):
            analyze_multiseed_confirmation(
                inputs,
                load_matched_config(MATCHED),
                load_config(CONFIG),
                replicates=100,
            )
        inputs = five_seed_cells()
        inputs[FRESH_TRAINING_SEEDS[0]]["proposal_T"]["training_seed"] = 17
        with self.assertRaisesRegex(MultiseedConfirmationError, "identity"):
            analyze_multiseed_confirmation(
                inputs,
                load_matched_config(MATCHED),
                load_config(CONFIG),
                replicates=100,
            )

    def test_rejects_cross_seed_protocol_drift_and_sealed_access(self) -> None:
        inputs = five_seed_cells()
        changed_seed = FRESH_TRAINING_SEEDS[-1]
        for label in ("proposal_T", "proposal_TS"):
            inputs[changed_seed][label]["transient_training_protocol_sha256"] = "e" * 64
        with self.assertRaisesRegex(
            MultiseedConfirmationError, "cross_seed_training_protocol"
        ):
            analyze_multiseed_confirmation(
                inputs,
                load_matched_config(MATCHED),
                load_config(CONFIG),
                replicates=100,
            )

        inputs = five_seed_cells()
        inputs[FRESH_TRAINING_SEEDS[0]]["control_T"][
            "locked_test_field_case_count_read"
        ] = 1
        with self.assertRaisesRegex(MatchedInformationAnalysisError, "sealed"):
            analyze_multiseed_confirmation(
                inputs,
                load_matched_config(MATCHED),
                load_config(CONFIG),
                replicates=100,
            )

    def test_rejects_incomplete_factorial(self) -> None:
        inputs = copy.deepcopy(five_seed_cells())
        del inputs[FRESH_TRAINING_SEEDS[0]][CELL_ORDER[-1]]
        with self.assertRaisesRegex(MultiseedConfirmationError, "cells"):
            analyze_multiseed_confirmation(
                inputs,
                load_matched_config(MATCHED),
                load_config(CONFIG),
                replicates=100,
            )


if __name__ == "__main__":
    unittest.main()
