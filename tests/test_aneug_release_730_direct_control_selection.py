from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_release_730_direct_control_selection import (
    CONTROL_ORDER,
    Release730DirectControlSelectionError,
    analyze_direct_controls,
    extract_control_rows,
    file_sha256,
    load_config,
    main,
    validate_activation,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_direct_control_selection_v1.json"


def rows(field: float, tawss: float, osi: float) -> list[dict[str, float]]:
    return [
        {
            "field_relative_l2": field + index * 1e-6,
            "tawss_normalized_absolute_error": tawss,
            "osi_mae": osi,
            "osi_coverage": 1.0,
        }
        for index in range(73)
    ]


def result(label: str, field: float, tawss: float, osi: float) -> dict:
    config = load_config(CONFIG)
    value = {
        "schema_version": {
            "released_graph_unet_adapter": "aurora.aneug_release_730_graphunet.private_result.v1",
            "ghd_gps_unet": "aurora.private.aneug_release_730_ghd_gps_result.v1",
            "transolver": "aurora.private.aneug_release_730_transolver_result.v1",
        }[label],
        "protocol_id": {
            "released_graph_unet_adapter": "aneug_release_730_official_graphunet_baseline_v1",
            "ghd_gps_unet": "aneug_release_730_ghd_gps_baseline_v1",
            "transolver": "aneug_release_730_transolver_baseline_v1",
        }[label],
        "status": (
            "complete_validation_development"
            if label == "released_graph_unet_adapter"
            else "complete"
        ),
        "validation_case_digest": config["split"]["validation_case_digest"],
        "validation_loader_order_sha256": config["split"]
        ["validation_loader_order_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "validation_case_count": 73,
        "case_ids_included": False,
        "processed_only_extra_field_case_count_read": 0,
        "validation": {
            "per_case_without_identifiers": rows(field, tawss, osi)
        },
    }
    if label == "released_graph_unet_adapter":
        value.update(
            {
                "single_seed_validation_development_only": True,
                "test_field_case_count_read": 0,
                "paper_result_or_claim": False,
            }
        )
    else:
        value.update(
            {
                "development_only": True,
                "locked_test_field_case_count_read": 0,
                "paper_performance_claim": False,
                "proposed_method": False,
            }
        )
    return value


def all_results() -> dict[str, dict]:
    return {
        "released_graph_unet_adapter": result(
            "released_graph_unet_adapter", 0.63, 0.20, 0.02
        ),
        "ghd_gps_unet": result("ghd_gps_unet", 0.40, 0.30, 0.03),
        "transolver": result("transolver", 0.45, 0.10, 0.01),
    }


class Release730DirectControlSelectionTests(unittest.TestCase):
    def test_config_is_sealed_threshold_free_and_73_case(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["split"]["validation_cases"], 73)
        self.assertEqual(tuple(config["controls"]["ordered_labels"]), CONTROL_ORDER)
        self.assertIsNone(config["selection"]["absolute_performance_threshold"])
        self.assertFalse(config["selection"]["automatic_paper_winner"])
        self.assertFalse(config["selection"]["zero_crossing_interval_is_equivalence"])
        self.assertFalse(config["boundary"]["execute_now"])

    def test_extractors_accept_all_three_exact_result_contracts(self) -> None:
        config = load_config(CONFIG)
        for label, value in all_results().items():
            self.assertEqual(len(extract_control_rows(label, value, config)), 73)

    def test_field_mean_selects_control_not_functional_tradeoff(self) -> None:
        output = analyze_direct_controls(all_results(), load_config(CONFIG), replicates=200)
        self.assertEqual(output["selected_direct_control"], "ghd_gps_unet")
        self.assertIn("transolver", output["pareto_set"])
        self.assertIsNone(output["automatic_paper_winner"])
        self.assertFalse(output["candidate_selected"])
        self.assertEqual(len(output["all_pairwise_deltas"]), 3)

    def test_registered_order_breaks_only_an_exact_field_tie(self) -> None:
        values = all_results()
        values["ghd_gps_unet"]["validation"]["per_case_without_identifiers"] = rows(
            0.4, 0.3, 0.03
        )
        values["transolver"]["validation"]["per_case_without_identifiers"] = rows(
            0.4, 0.1, 0.01
        )
        output = analyze_direct_controls(values, load_config(CONFIG), replicates=200)
        self.assertEqual(output["selected_direct_control"], "ghd_gps_unet")

    def test_sealed_scope_or_order_violation_is_rejected(self) -> None:
        config = load_config(CONFIG)
        changed = result("transolver", 0.4, 0.2, 0.02)
        changed["locked_test_field_case_count_read"] = 1
        with self.assertRaisesRegex(
            Release730DirectControlSelectionError, "transolver_boundary"
        ):
            extract_control_rows("transolver", changed, config)
        changed = result("ghd_gps_unet", 0.4, 0.2, 0.02)
        changed["validation_loader_order_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            Release730DirectControlSelectionError, "ghd_gps_unet_split"
        ):
            extract_control_rows("ghd_gps_unet", changed, config)

    def test_activation_binds_all_result_and_terminal_hashes(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_direct_control_selection_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "result_sha256": {
                label: str(index + 1) * 64
                for index, label in enumerate(CONTROL_ORDER)
            },
            "terminal_record_sha256": {
                label: str(index + 4) * 64
                for index, label in enumerate(CONTROL_ORDER)
            },
            "validation_case_digest": config["split"]["validation_case_digest"],
            "validation_loader_order_sha256": config["split"]
            ["validation_loader_order_sha256"],
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "read_locked_test_or_extra": False,
            "candidate_selection": False,
            "paper_performance_claim": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            changed = copy.deepcopy(activation)
            changed["candidate_selection"] = True
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(
                Release730DirectControlSelectionError, "activation_boundary"
            ):
                validate_activation(path, config, "abc")

    def test_cli_binds_hashes_and_writes_identifier_free_output(self) -> None:
        config = load_config(CONFIG)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result_paths: dict[str, Path] = {}
            terminal_paths: dict[str, Path] = {}
            for label, value in all_results().items():
                result_path = root / f"{label}.result.json"
                terminal_path = root / f"{label}.terminal.json"
                result_path.write_text(json.dumps(value), encoding="utf-8")
                terminal_path.write_text("{}\n", encoding="utf-8")
                result_paths[label] = result_path
                terminal_paths[label] = terminal_path
            activation = {
                "schema_version": "aurora.private.aneug_release_730_direct_control_selection_activation.v1",
                "protocol_id": config["protocol_id"],
                "public_commit": "abc",
                "quality_conclusion": "success",
                "result_sha256": {
                    label: file_sha256(result_paths[label]) for label in CONTROL_ORDER
                },
                "terminal_record_sha256": {
                    label: file_sha256(terminal_paths[label]) for label in CONTROL_ORDER
                },
                "validation_case_digest": config["split"]["validation_case_digest"],
                "validation_loader_order_sha256": config["split"]
                ["validation_loader_order_sha256"],
                "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
                "read_locked_test_or_extra": False,
                "candidate_selection": False,
                "paper_performance_claim": False,
            }
            activation_path = root / "activation.json"
            activation_path.write_text(json.dumps(activation), encoding="utf-8")
            output_path = root / "selection.json"
            arguments = [
                "--config",
                str(CONFIG),
                "--activation",
                str(activation_path),
                "--expected-commit",
                "abc",
                "--output",
                str(output_path),
            ]
            for label in CONTROL_ORDER:
                option = label.replace("_", "-")
                arguments.extend(
                    [
                        f"--{option}-result",
                        str(result_paths[label]),
                        f"--{option}-terminal",
                        str(terminal_paths[label]),
                    ]
                )
            self.assertEqual(main(arguments), 0)
            output = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(output["selected_direct_control"], "ghd_gps_unet")
            self.assertFalse(output["case_identifiers_included"])
            self.assertFalse(output["locked_test_or_extra_values_read"])


if __name__ == "__main__":
    unittest.main()
