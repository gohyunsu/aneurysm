from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_release_730_candidate_selection import (
    CELL_IDENTITY,
    CELL_ORDER,
    Release730CandidateSelectionError,
    analyze_candidate_selection,
    file_sha256,
    load_config,
    main,
    validate_activation,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_candidate_selection_v1.json"
HEX = "a" * 64


def candidate_result(cell: str, metrics: dict[str, float]) -> dict:
    mode, architecture, objective = CELL_IDENTITY[cell]
    functional = mode == "functional_finetune"
    initial_metrics = {
        "field_relative_l2": 1.0,
        "mean_vector_tawss_normalized_l2": 1.0,
        "tawss_normalized_absolute_error": 1.0,
        "osi_mae": 1.0,
    }
    return {
        "schema_version": "aurora.private.aneug_release_730_response_local_result.v1",
        "protocol_id": "aneug_release_730_response_local_candidate_v1",
        "status": "complete",
        "mode": mode,
        "architecture_variant": architecture,
        "objective_variant": objective,
        "selected_response_rank": 64,
        "seed": 1103,
        "best_epoch": 80,
        "optimizer_steps": 1000,
        "parameter_count": 100,
        "active_parameter_count": 80,
        "elapsed_seconds": 12.0,
        "validation_case_count": 73,
        "validation_case_digest": "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024",
        "validation_loader_order_sha256": "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "private_split_manifest_sha256": "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f",
        "response_basis_sha256": HEX,
        "public_commit": "1" * 40,
        "config_sha256": "38f256d4e60e2a7c748bb59b7e3de910a1bf1f464d18b7ec99ef0f435aa415b4",
        "initial_combined_field_checkpoint_sha256": "b" * 64 if functional else None,
        "selection_endpoint_normalizers": (
            {"field": 1.0, "mean_vector": 1.0, "tawss": 1.0, "osi": 1.0}
            if functional
            else None
        ),
        "initial_validation": (
            {"aggregate": initial_metrics, "case_count": 73} if functional else None
        ),
        "selection_name": (
            "common_initial_checkpoint_endpoint_normalized_validation_utility"
            if functional
            else "validation_field_relative_l2"
        ),
        "best_selection_value": (
            metrics["field_relative_l2"]
            + (
                metrics["mean_vector_tawss_normalized_l2"]
                + metrics["tawss_normalized_absolute_error"]
                + metrics["osi_mae"]
            )
            / 3.0
            if functional
            else metrics["field_relative_l2"]
        ),
        "validation": {
            "aggregate": metrics,
            "case_count": 73,
            "per_case_without_identifiers": [{} for _ in range(73)],
        },
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
        "development_only": True,
        "paper_performance_claim": False,
    }


def direct_selection(selected: str = "ghd_gps_unet") -> dict:
    return {
        "schema_version": "aurora.private.aneug_release_730_direct_control_selection_result.v1",
        "status": "complete",
        "selection_metric": "case_mean_field_relative_l2",
        "selected_direct_control": selected,
        "locked_test_or_extra_values_read": False,
        "candidate_selected": False,
        "paper_performance_claim": False,
    }


def candidate_results() -> dict[str, dict]:
    values = {
        "architecture_response_only_field": (0.40, 0.42, 0.41, 0.12),
        "architecture_response_plus_residual_field": (0.36, 0.38, 0.37, 0.11),
        "finetune_response_plus_residual_field": (0.35, 0.36, 0.35, 0.10),
        "finetune_response_plus_residual_scalarized": (0.34, 0.31, 0.30, 0.09),
        "finetune_response_plus_residual_anchored": (0.33, 0.28, 0.27, 0.08),
    }
    return {
        cell: candidate_result(
            cell,
            {
                "field_relative_l2": row[0],
                "mean_vector_tawss_normalized_l2": row[1],
                "tawss_normalized_absolute_error": row[2],
                "osi_mae": row[3],
            },
        )
        for cell, row in values.items()
    }


class CandidateSelectionTests(unittest.TestCase):
    def test_config_freezes_common_utility_before_results(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["candidate_cells"]["seed"], 1103)
        self.assertEqual(len(config["candidate_cells"]["ordered"]), 5)
        self.assertIsNone(config["proposal"]["absolute_performance_threshold"])
        changed = copy.deepcopy(config)
        changed["proposal"]["objective_candidates_in_tie_order"].reverse()
        with self.assertRaisesRegex(Release730CandidateSelectionError, "proposal"):
            validate_config(changed)

    def test_common_utility_selects_one_objective_and_retains_all_cells(self) -> None:
        output = analyze_candidate_selection(
            candidate_results(), direct_selection(), load_config(CONFIG)
        )
        self.assertEqual(output["selected_control_family"], "release730_ghd_gps")
        self.assertEqual(output["selected_proposal_objective"], "all_field_anchored")
        self.assertEqual(output["selected_proposal_rank"], 64)
        self.assertEqual(len(output["candidate_metrics_by_cell"]), 5)
        self.assertTrue(output["all_candidate_cells_reported"])
        self.assertIsNone(output["automatic_paper_winner"])

    def test_graph_selection_fails_without_silent_control_fallback(self) -> None:
        with self.assertRaisesRegex(
            Release730CandidateSelectionError,
            "selected_direct_control_not_matched_trainable",
        ):
            analyze_candidate_selection(
                candidate_results(),
                direct_selection("released_graph_unet_adapter"),
                load_config(CONFIG),
            )

    def test_rank_basis_checkpoint_and_normalizer_drift_fail_closed(self) -> None:
        for mutation, reason in (
            (("architecture_response_only_field", "selected_response_rank", 32), "rank_alignment"),
            (("architecture_response_only_field", "response_basis_sha256", "c" * 64), "basis_alignment"),
            (("finetune_response_plus_residual_scalarized", "initial_combined_field_checkpoint_sha256", "c" * 64), "initial_checkpoint_alignment"),
        ):
            results = candidate_results()
            results[mutation[0]][mutation[1]] = mutation[2]
            with self.assertRaisesRegex(Release730CandidateSelectionError, reason):
                analyze_candidate_selection(results, direct_selection(), load_config(CONFIG))
        results = candidate_results()
        results["finetune_response_plus_residual_anchored"][
            "selection_endpoint_normalizers"
        ]["osi"] = 2.0
        with self.assertRaisesRegex(
            Release730CandidateSelectionError, "normalizer_initial_alignment"
        ):
            analyze_candidate_selection(results, direct_selection(), load_config(CONFIG))
        results = candidate_results()
        results["finetune_response_plus_residual_field"]["best_selection_value"] += 0.1
        with self.assertRaisesRegex(
            Release730CandidateSelectionError, "common_checkpoint_selection"
        ):
            analyze_candidate_selection(results, direct_selection(), load_config(CONFIG))

    def test_activation_and_cli_bind_all_terminal_results_once(self) -> None:
        config = load_config(CONFIG)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result_paths: dict[str, Path] = {}
            terminal_paths: dict[str, Path] = {}
            for index, cell in enumerate(CELL_ORDER):
                result_paths[cell] = root / f"{cell}.result.json"
                terminal_paths[cell] = root / f"{cell}.terminal.json"
                result_paths[cell].write_text(
                    json.dumps(candidate_results()[cell]), encoding="utf-8"
                )
                terminal_paths[cell].write_text(
                    json.dumps(
                        {"job_id": f"{index}.ECE-util1", "exit_code": 0, "complete": True}
                    ),
                    encoding="utf-8",
                )
            direct_path = root / "direct.json"
            direct_path.write_text(json.dumps(direct_selection()), encoding="utf-8")
            basis_path = root / "response_basis.pt"
            basis_path.write_bytes(b"opaque basis\n")
            basis_sha256 = file_sha256(basis_path)
            for cell in CELL_ORDER:
                payload = json.loads(result_paths[cell].read_text(encoding="utf-8"))
                payload["response_basis_sha256"] = basis_sha256
                result_paths[cell].write_text(json.dumps(payload), encoding="utf-8")
            activation = {
                "schema_version": "aurora.private.aneug_release_730_candidate_selection_activation.v1",
                "protocol_id": config["protocol_id"],
                "public_commit": "1" * 40,
                "quality_conclusion": "success",
                "candidate_result_sha256": {
                    cell: file_sha256(result_paths[cell]) for cell in CELL_ORDER
                },
                "candidate_terminal_record_sha256": {
                    cell: file_sha256(terminal_paths[cell]) for cell in CELL_ORDER
                },
                "candidate_checkpoint_sha256": {},
                "entries": [],
                "direct_control_selection_result_sha256": file_sha256(direct_path),
                "response_basis_sha256": file_sha256(basis_path),
                "candidate_selection_config_sha256": file_sha256(CONFIG),
                "validation_case_digest": config["split"]["validation_case_digest"],
                "validation_loader_order_sha256": config["split"][
                    "validation_loader_order_sha256"
                ],
                "private_split_manifest_sha256": config["split"][
                    "private_split_manifest_sha256"
                ],
                "read_locked_test_or_extra": False,
                "repair_or_new_variant_authorization": False,
                "paper_performance_claim": False,
            }
            evidence_root = root / "evidence"
            evidence_root.mkdir()
            for cell in CELL_ORDER:
                run_root = evidence_root / cell
                (run_root / "checkpoints").mkdir(parents=True)
                result_target = run_root / "result.json"
                terminal_target = run_root / "attempt.status.json"
                checkpoint_target = run_root / "checkpoints" / "best.pt"
                result_target.write_bytes(result_paths[cell].read_bytes())
                terminal_target.write_bytes(terminal_paths[cell].read_bytes())
                checkpoint_target.write_bytes(f"opaque {cell}\n".encode())
                checkpoint_sha256 = file_sha256(checkpoint_target)
                activation["candidate_checkpoint_sha256"][cell] = checkpoint_sha256
                activation["entries"].append(
                    {
                        "cell": cell,
                        "run_relative_path": cell,
                        "result_sha256": activation["candidate_result_sha256"][cell],
                        "terminal_record_sha256": activation[
                            "candidate_terminal_record_sha256"
                        ][cell],
                        "checkpoint_sha256": checkpoint_sha256,
                    }
                )
            activation_path = root / "activation.json"
            activation_path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(activation_path, config, "1" * 40)
            output = root / "selection.json"
            args = [
                "--config",
                str(CONFIG),
                "--activation",
                str(activation_path),
                "--expected-commit",
                "1" * 40,
                "--direct-control-selection-result",
                str(direct_path),
                "--response-basis",
                str(basis_path),
                "--candidate-evidence-root",
                str(evidence_root),
            ]
            args.extend(["--output", str(output)])
            self.assertEqual(main(args), 0)
            observed = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(observed["selected_proposal_objective"], "all_field_anchored")
            with self.assertRaises(Release730CandidateSelectionError):
                main(args)


if __name__ == "__main__":
    unittest.main()
