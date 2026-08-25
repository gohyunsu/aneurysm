from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_locked_test_evaluation import (
    EXPECTED_CELLS,
    FIGURE_MODE,
    FIGURE_SEED,
    FRESH_TRAINING_SEEDS,
    Release730LockedTestError,
    _common_reference_tawss_floor,
    _validate_checkpoint_payload,
    analyze_locked_test,
    file_sha256,
    load_config,
    preflight_frozen_evidence,
    summarize_reference_osi_support,
    validate_activation,
    validate_checkpoint_manifest,
    validate_config,
    validate_frozen_identity_alignment,
)
from aurora.aneug_release_730_matched_information_analysis import METRICS


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_locked_test_evaluation_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_locked_test_evaluation_v1.pbs"
HEX = "a" * 64


def checkpoint_entries() -> list[dict]:
    entries = []
    for seed in FRESH_TRAINING_SEEDS:
        for cell in EXPECTED_CELLS:
            control = cell.startswith("control_")
            entries.append(
                {
                    "training_seed": seed,
                    "cell": cell,
                    "model_role": "selected_control" if control else "selected_proposal",
                    "information_mode": (
                        "eligible_steady" if cell.endswith("TS") else "transient_only"
                    ),
                    "model_family": (
                        "release730_ghd_gps"
                        if control
                        else "release730_response_plus_local_residual"
                    ),
                    "objective_variant": "field_only" if control else "all_scalarized",
                    "selected_response_rank": None if control else 32,
                    "training_stage": "five_seed_matched_information_validation_confirmation",
                    "checkpoint_relative_path": f"{seed}/{cell}/best.pt",
                    "validation_result_relative_path": f"{seed}/{cell}/result.json",
                    "terminal_record_relative_path": f"{seed}/{cell}/attempt.status.json",
                    "checkpoint_sha256": HEX,
                    "validation_result_sha256": HEX,
                    "terminal_record_sha256": HEX,
                    "training_activation_sha256": HEX,
                    "transient_training_protocol_sha256": HEX,
                }
            )
    return entries


def manifest() -> dict:
    return {
        "schema_version": "aurora.private.aneug_release_730_frozen_C0_checkpoints.v1",
        "status": "complete_frozen_before_locked_test",
        "checkpoint_count": 20,
        "training_seed_count": 5,
        "all_checkpoints_frozen_before_test": True,
        "locked_test_or_extra_used_for_selection": False,
        "case_identifiers_included": False,
        "entries": checkpoint_entries(),
        "figure_display": {
            "training_seed": FIGURE_SEED,
            "information_mode": FIGURE_MODE,
            "control_cell": "control_TS",
            "proposal_cell": "proposal_TS",
            "selected_before_locked_test": True,
        },
    }


class LockedTestConfigTests(unittest.TestCase):
    def test_config_fixes_one_batch_and_no_training(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["frozen_checkpoints"]["checkpoint_count"], 20)
        self.assertEqual(config["authorization"]["locked_test_attempts"], 1)
        self.assertFalse(config["authorization"]["execute_now"])
        self.assertFalse(config["authorization"]["training"])
        self.assertFalse(config["authorization"]["read_processed_only_extra"])
        self.assertEqual(config["figure"]["display_training_seed"], FIGURE_SEED)
        self.assertFalse(config["figure"]["seed_selected_from_test_outcomes"])

    def test_scope_mutations_fail_closed(self) -> None:
        config = load_config(CONFIG)
        for section, key, value, reason in (
            ("split", "locked_test_cases", 72, "split"),
            ("frozen_checkpoints", "checkpoint_count", 19, "frozen_checkpoints"),
            ("figure", "seed_selected_from_test_outcomes", True, "figure"),
            ("authorization", "training", True, "authorization"),
            ("authorization", "read_processed_only_extra", True, "authorization"),
        ):
            changed = copy.deepcopy(config)
            changed[section][key] = value
            with self.assertRaisesRegex(Release730LockedTestError, reason):
                validate_config(changed)

    def test_activation_requires_first_and_only_test_attempt(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_locked_test_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "1" * 40,
            "quality_conclusion": "success",
            "authorized_stage": "one_time_locked_test_evaluation_of_frozen_C0",
            "locked_test_attempt_ordinal": 1,
            "created_before_locked_test_read": True,
            "prior_locked_test_access_marker_sha256": None,
            "checkpoint_manifest_sha256": HEX,
            "multiseed_confirmation_result_sha256": HEX,
            "selected_model_decision_record_sha256": HEX,
            "response_basis_sha256": HEX,
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "private_train_audit_sha256": config["split"]["private_train_audit_sha256"],
            "test_case_digest": config["split"]["test_case_digest"],
            "test_loader_order_sha256": "b" * 64,
            "checkpoint_count": 20,
            "training": False,
            "read_locked_test": True,
            "read_processed_only_extra": False,
            "post_test_repair_or_rerun": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "1" * 40)
            activation["locked_test_attempt_ordinal"] = 2
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaisesRegex(Release730LockedTestError, "activation_identity"):
                validate_activation(path, config, "1" * 40)

    def test_pbs_is_one_gpu_one_batch_and_writes_access_marker(self) -> None:
        text = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -l select=1:ncpus=4:mem=64gb:ngpus=1", text)
        self.assertEqual(
            text.count("python -m aurora.aneug_release_730_locked_test_evaluation"),
            1,
        )
        self.assertIn("${PBS_JOBID:?T0 is PBS-only}", text)
        self.assertIn("--access-marker /output/locked_test_access.started.json", text)
        self.assertIn("--checkpoint-root /private/checkpoints", text)
        self.assertNotIn("qsub ", text)


class LockedTestManifestTests(unittest.TestCase):
    def test_reference_support_is_model_independent_area_weighted_and_identifier_free(self) -> None:
        reference = torch.zeros(80, 2, 3)
        reference[:, 0, 0] = torch.where(
            torch.arange(80) % 2 == 0,
            torch.tensor(1.0),
            torch.tensor(-1.0),
        )
        reference[:, 1, 0] = 0.01
        cases = [
            {
                "wss": reference.clone(),
                "vertex_weights": torch.tensor([0.75, 0.25]),
            }
            for _ in range(73)
        ]
        result = summarize_reference_osi_support(cases, 0.1)
        self.assertEqual(result["case_count"], 73)
        self.assertTrue(result["model_independent"])
        self.assertTrue(result["area_weighted"])
        self.assertAlmostEqual(result["case_mean_area_fraction"], 0.75)
        self.assertEqual(
            result["per_case_area_fraction_without_identifiers"], [0.75] * 73
        )
        self.assertNotIn("case_ids", result)

    def test_all_frozen_checkpoints_must_share_the_train_only_osi_floor(self) -> None:
        self.assertEqual(_common_reference_tawss_floor([0.001] * 20), 0.001)
        with self.assertRaisesRegex(
            Release730LockedTestError, "reference_tawss_floor_mismatch"
        ):
            _common_reference_tawss_floor([0.001] * 19 + [0.002])

    def test_exact_twenty_checkpoint_grid_is_required(self) -> None:
        config = load_config(CONFIG)
        payload = manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            validated = validate_checkpoint_manifest(path, file_sha256(path), config)
            self.assertEqual(len(validated["entries"]), 20)
            payload["entries"][-1] = copy.deepcopy(payload["entries"][0])
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(Release730LockedTestError, "checkpoint_duplicate"):
                validate_checkpoint_manifest(path, file_sha256(path), config)

    def test_checkpoint_payload_must_match_frozen_cell(self) -> None:
        config = load_config(CONFIG)
        entry = checkpoint_entries()[0]
        payload = {
            "schema_version": "aurora.private.aneug_release_730_matched_training_best.v1",
            "protocol_id": "aneug_release_730_matched_training_v1",
            "model_role": entry["model_role"],
            "information_mode": entry["information_mode"],
            "model_family": entry["model_family"],
            "objective_variant": entry["objective_variant"],
            "selected_response_rank": entry["selected_response_rank"],
            "training_seed": entry["training_seed"],
            "training_stage": entry["training_stage"],
            "response_basis_embedded": False,
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "training_config_sha256": config["source"]["matched_training_config_sha256"],
            "multiseed_confirmation_config_sha256": config["source"]["multiseed_confirmation_config_sha256"],
            "activation_sha256": entry["training_activation_sha256"],
            "model_state_dict": {"weight": 1},
            "best_epoch": 80,
            "reference_tawss_floor": 0.001,
            "single_field_output_scale": 1.0,
        }
        _validate_checkpoint_payload(payload, entry, config)
        payload["training_seed"] = 7
        with self.assertRaisesRegex(Release730LockedTestError, "checkpoint_payload_identity"):
            _validate_checkpoint_payload(payload, entry, config)

    def test_preflight_verifies_checkpoint_result_and_terminal_before_data(self) -> None:
        config = load_config(CONFIG)
        entry = checkpoint_entries()[0]
        checkpoint = {
            "schema_version": "aurora.private.aneug_release_730_matched_training_best.v1",
            "protocol_id": "aneug_release_730_matched_training_v1",
            "model_role": entry["model_role"],
            "information_mode": entry["information_mode"],
            "model_family": entry["model_family"],
            "objective_variant": entry["objective_variant"],
            "selected_response_rank": entry["selected_response_rank"],
            "training_seed": entry["training_seed"],
            "training_stage": entry["training_stage"],
            "response_basis_embedded": False,
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "training_config_sha256": config["source"]["matched_training_config_sha256"],
            "multiseed_confirmation_config_sha256": config["source"]["multiseed_confirmation_config_sha256"],
            "activation_sha256": entry["training_activation_sha256"],
            "model_state_dict": {"weight": torch.tensor([1.0])},
            "best_epoch": 80,
            "reference_tawss_floor": 0.001,
            "single_field_output_scale": 1.0,
        }
        validation = {
            "schema_version": "aurora.aneug_release_730_matched_information_cell.v1",
            "status": "complete_validation_confirmation",
            "model_role": entry["model_role"],
            "information_mode": entry["information_mode"],
            "model_family": entry["model_family"],
            "objective_variant": entry["objective_variant"],
            "selected_response_rank": entry["selected_response_rank"],
            "training_seed": entry["training_seed"],
            "training_stage": entry["training_stage"],
            "activation_sha256": entry["training_activation_sha256"],
            "locked_test_field_case_count_read": 0,
            "processed_only_extra_field_case_count_read": 0,
            "case_ids_included": False,
        }
        terminal = {"job_id": "synthetic", "exit_code": 0, "complete": True}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (
                entry["checkpoint_relative_path"],
                entry["validation_result_relative_path"],
                entry["terminal_record_relative_path"],
            ):
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
            torch.save(checkpoint, root / entry["checkpoint_relative_path"])
            (root / entry["validation_result_relative_path"]).write_text(
                json.dumps(validation), encoding="utf-8"
            )
            (root / entry["terminal_record_relative_path"]).write_text(
                json.dumps(terminal), encoding="utf-8"
            )
            entry["checkpoint_sha256"] = file_sha256(
                root / entry["checkpoint_relative_path"]
            )
            entry["validation_result_sha256"] = file_sha256(
                root / entry["validation_result_relative_path"]
            )
            entry["terminal_record_sha256"] = file_sha256(
                root / entry["terminal_record_relative_path"]
            )
            self.assertEqual(
                preflight_frozen_evidence({"entries": [entry]}, root, config),
                0.001,
            )
            terminal["complete"] = False
            (root / entry["terminal_record_relative_path"]).write_text(
                json.dumps(terminal), encoding="utf-8"
            )
            entry["terminal_record_sha256"] = file_sha256(
                root / entry["terminal_record_relative_path"]
            )
            with self.assertRaisesRegex(
                Release730LockedTestError, "terminal_record_incomplete"
            ):
                preflight_frozen_evidence({"entries": [entry]}, root, config)

    def test_selection_confirmation_and_checkpoint_identities_must_align(self) -> None:
        payload = manifest()
        selection = {
            "selected_control_family": "release730_ghd_gps",
            "selected_proposal_family": "release730_response_plus_local_residual",
            "selected_proposal_objective": "all_scalarized",
            "selected_proposal_rank": 32,
            "selected_response_basis_sha256": HEX,
        }
        multiseed = {
            "selected_model_identity_by_role": {
                "selected_control": {
                    "model_family": "release730_ghd_gps",
                    "objective_variant": "field_only",
                    "selected_response_rank": None,
                },
                "selected_proposal": {
                    "model_family": "release730_response_plus_local_residual",
                    "objective_variant": "all_scalarized",
                    "selected_response_rank": 32,
                },
            }
        }
        validate_frozen_identity_alignment(payload, multiseed, selection, HEX)
        selection["selected_proposal_rank"] = 64
        with self.assertRaisesRegex(
            Release730LockedTestError, "aligned_selection_identity"
        ):
            validate_frozen_identity_alignment(payload, multiseed, selection, HEX)


class LockedTestAnalysisTests(unittest.TestCase):
    def test_lower_proposal_error_has_negative_registered_delta(self) -> None:
        config = load_config(CONFIG)
        config["evaluation"]["bootstrap_replicates"] = 100
        rows = {}
        for seed in FRESH_TRAINING_SEEDS:
            rows[seed] = {}
            for cell in EXPECTED_CELLS:
                proposal = cell.startswith("proposal_")
                steady = cell.endswith("TS")
                base = 0.8 if proposal else 1.0
                if steady:
                    base -= 0.05
                rows[seed][cell] = [
                    {
                        metric: (0.9 if metric == "osi_coverage" else base)
                        for metric in METRICS
                    }
                    for _ in range(73)
                ]
        result = analyze_locked_test(rows, config)
        for contrast in ("proposal_minus_control_T", "proposal_minus_control_TS"):
            for metric in ("field_relative_l2", "tawss_normalized_absolute_error", "osi_mae"):
                self.assertAlmostEqual(
                    result["crossed_seed_case_contrasts"][contrast][metric]["point_delta"],
                    -0.2,
                )
        self.assertIsNone(result["automatic_winner"])
        self.assertFalse(result["prediction_valid_coverage_is_gate_or_claim_endpoint"])


if __name__ == "__main__":
    unittest.main()
