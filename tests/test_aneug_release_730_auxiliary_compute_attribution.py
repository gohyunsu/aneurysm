from __future__ import annotations

import copy
import unittest
from pathlib import Path

from aurora.aneug_release_730_auxiliary_compute_attribution import (
    CELL_ORDER,
    AuxiliaryComputeAttributionError,
    analyze_auxiliary_compute_attribution,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_auxiliary_compute_attribution_v1.json"


def rows(offset: float, coverage: float) -> list[dict[str, float]]:
    return [
        {
            "field_relative_l2": 0.50 + offset + index * 1e-5,
            "mean_wss_vector_error": 0.40 + offset,
            "tawss_normalized_absolute_error": 0.30 + offset,
            "osi_mae": 0.020 + offset * 0.01,
            "osi_coverage": coverage,
        }
        for index in range(73)
    ]


def cell(label: str, offset: float, coverage: float = 0.9) -> dict:
    control = label.startswith("control_")
    steady = label.endswith("TS")
    epochs = 80
    examples = epochs * 584
    return {
        "schema_version": (
            "aurora.aneug_release_730_matched_information_cell.v1"
            if steady
            else "aurora.aneug_release_730_auxiliary_compute_cell.v1"
        ),
        "protocol_id": (
            "aneug_release_730_matched_information_analysis_v1"
            if steady
            else "aneug_release_730_auxiliary_compute_attribution_v1"
        ),
        "status": "complete_validation_development",
        "model_role": "selected_control" if control else "selected_proposal",
        "information_mode": "eligible_steady" if steady else "transient_mean",
        "model_family": "control_family" if control else "proposal_family",
        "objective_variant": "field_only" if control else "all_field_anchored",
        "selected_response_rank": None if control else 64,
        "validation_case_digest": "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024",
        "private_split_manifest_sha256": "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f",
        "validation_loader_order_sha256": "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "transient_training_protocol_sha256": ("a" if control else "b") * 64,
        "training_seed": 1103,
        "epochs_completed": epochs,
        "transient_case_cycles_consumed": examples,
        "optimizer_steps": examples // 2,
        "training_gpu_seconds": 3600.0,
        "peak_gpu_memory_bytes": 12_000_000_000,
        "active_parameter_count": 7_000_000 if control else 8_000_000,
        "single_field_head_active": True,
        "steady_head_active": steady,
        "single_field_output_scale": 2.5 if steady else 1.75,
        "single_field_output_scale_source": (
            "eligible_steady_physical_vector_rms_from_bound_descriptive_audit"
            if steady
            else "transient_train_physical_vector_rms_from_train_audit"
        ),
        "single_field_scale_source_sha256": ("c" if steady else "d") * 64,
        "single_field_auxiliary_source": (
            "eligible_steady_wss" if steady else "same_train_case_cycle_mean"
        ),
        "single_field_auxiliary_coefficient": 1.0,
        "single_field_auxiliary_examples_consumed": examples,
        "transient_mean_auxiliary_examples_consumed": 0 if steady else examples,
        "steady_wss_rows_read_for_auxiliary": examples if steady else 0,
        "additional_auxiliary_forward_backward_work": True,
        "additional_steady_forward_backward_work": steady,
        "eligible_steady_rows": 13_985 if steady else 0,
        "eligible_steady_case_digest": (
            "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc"
            if steady
            else None
        ),
        "steady_examples_consumed": examples if steady else 0,
        "steady_exposure_prefix_sha256": "e" * 64 if steady else None,
        "case_ids_included": False,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "paper_result_or_claim": False,
        "per_case_without_identifiers": rows(offset, coverage),
    }


def cells() -> dict[str, dict]:
    return {
        "control_TM": cell("control_TM", 0.00, 0.80),
        "control_TS": cell("control_TS", -0.03, 0.85),
        "proposal_TM": cell("proposal_TM", -0.10, 0.90),
        "proposal_TS": cell("proposal_TS", -0.15, 0.95),
    }


class AuxiliaryComputeAttributionTests(unittest.TestCase):
    def test_config_keeps_sidecar_noncausal_and_nonblocking(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(tuple(config["attribution"]["cells"]), CELL_ORDER)
        self.assertFalse(config["interpretation"]["fully_compute_matched"])
        self.assertFalse(config["interpretation"]["causal_steady_label_effect"])
        self.assertFalse(config["boundary"]["required_for_primary_factorial"])

    def test_config_rejects_causal_relabeling(self) -> None:
        config = load_config(CONFIG)
        changed = copy.deepcopy(config)
        changed["interpretation"]["causal_steady_label_effect"] = True
        with self.assertRaisesRegex(AuxiliaryComputeAttributionError, "interpretation"):
            validate_config(changed)

    def test_reports_paired_role_specific_contrasts(self) -> None:
        result = analyze_auxiliary_compute_attribution(
            cells(), load_config(CONFIG), replicates=200, seed=7
        )
        self.assertAlmostEqual(
            result["paired_contrasts"]["steady_minus_transient_mean_control"]
            ["field_relative_l2"]["point_delta"],
            -0.03,
        )
        self.assertAlmostEqual(
            result["paired_contrasts"]["steady_minus_transient_mean_proposal"]
            ["field_relative_l2"]["point_delta"],
            -0.05,
        )
        self.assertFalse(result["fully_compute_matched"])
        self.assertFalse(result["steady_minus_transient_mean_is_label_only_causal_effect"])
        self.assertIsNone(result["automatic_winner"])

    def test_rejects_head_or_steady_read_mismatch(self) -> None:
        config = load_config(CONFIG)
        changed = cells()
        changed["control_TM"]["steady_wss_rows_read_for_auxiliary"] = 1
        with self.assertRaisesRegex(
            AuxiliaryComputeAttributionError, "control_TM_transient_mean_auxiliary"
        ):
            analyze_auxiliary_compute_attribution(changed, config, replicates=200)
        changed = cells()
        changed["proposal_TS"]["single_field_head_active"] = False
        with self.assertRaisesRegex(AuxiliaryComputeAttributionError, "proposal_TS_head"):
            analyze_auxiliary_compute_attribution(changed, config, replicates=200)

    def test_rejects_model_or_protocol_drift_within_role(self) -> None:
        config = load_config(CONFIG)
        changed = cells()
        changed["proposal_TS"]["model_family"] = "different"
        with self.assertRaisesRegex(
            AuxiliaryComputeAttributionError, "proposal_model_family_pair"
        ):
            analyze_auxiliary_compute_attribution(changed, config, replicates=200)
        changed = cells()
        changed["control_TS"]["transient_training_protocol_sha256"] = "f" * 64
        with self.assertRaisesRegex(
            AuxiliaryComputeAttributionError,
            "control_transient_training_protocol_sha256_pair",
        ):
            analyze_auxiliary_compute_attribution(changed, config, replicates=200)

    def test_rejects_test_or_identifier_access(self) -> None:
        config = load_config(CONFIG)
        changed = cells()
        changed["control_TM"]["locked_test_field_case_count_read"] = 1
        with self.assertRaisesRegex(AuxiliaryComputeAttributionError, "control_TM_sealed"):
            analyze_auxiliary_compute_attribution(changed, config, replicates=200)
        changed = cells()
        changed["control_TS"]["case_ids_included"] = True
        with self.assertRaisesRegex(
            AuxiliaryComputeAttributionError, "control_TS_identifiers"
        ):
            analyze_auxiliary_compute_attribution(changed, config, replicates=200)


if __name__ == "__main__":
    unittest.main()
