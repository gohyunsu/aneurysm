from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_ghd_current_locked_test import (
    FIGURE_SEED,
    INFORMATION_MODES,
    PRIMARY_ACTIVATION_SCHEMA,
    TRAINING_SEEDS,
    CurrentGHDLockedTestError,
    RECOVERY_ACTIVATION_SCHEMA,
    _validate_checkpoint_common_values,
    _validate_checkpoint_payload,
    _runtime_commit_set_sha256,
    _write_or_validate_access_marker,
    analyze_locked_test,
    build_current_figure_payload,
    build_current_reference_selection,
    file_sha256,
    load_config,
    preflight_frozen_evidence,
    validate_activation,
    validate_checkpoint_manifest,
    validate_config,
    validate_multiseed_result,
)
from aurora.aneug_release_730_matched_information_analysis import METRICS


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_ghd_current_locked_test_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_ghd_current_locked_test_v1.pbs"
HEX = "a" * 64
PROTOCOL_SHA = "b" * 64
TRANSIENT_PROTOCOL_SHA = "c" * 64


def checkpoint_entries() -> list[dict]:
    entries: list[dict] = []
    for seed in TRAINING_SEEDS:
        for mode in INFORMATION_MODES:
            entries.append(
                {
                    "training_seed": seed,
                    "information_mode": mode,
                    "model_role": "selected_control",
                    "model_family": "release730_ghd_gps",
                    "objective_variant": "field_only",
                    "selected_response_rank": None,
                    "training_stage": "five_seed_matched_information_validation_confirmation",
                    "public_commit": "c686dff9f7a8e596212c44c279ed7c89d158bbd8",
                    "private_runtime_commit": f"{seed + len(entries):040x}"[-40:],
                    "checkpoint_relative_path": f"{seed}/{mode}/best.pt",
                    "validation_result_relative_path": f"{seed}/{mode}/result.json",
                    "terminal_record_relative_path": f"{seed}/{mode}/terminal.json",
                    "checkpoint_sha256": HEX,
                    "validation_result_sha256": HEX,
                    "terminal_record_sha256": HEX,
                    "fresh_information_activation_sha256": HEX,
                    "fresh_information_protocol_sha256": PROTOCOL_SHA,
                    "transient_training_protocol_sha256": TRANSIENT_PROTOCOL_SHA,
                }
            )
    return entries


def manifest() -> dict:
    entries = checkpoint_entries()
    return {
        "schema_version": "aurora.private.aneug_release_730_ghd_current_frozen_checkpoints.v1",
        "status": "complete_ten_checkpoints_frozen_before_locked_test",
        "checkpoint_count": 10,
        "training_seed_count": 5,
        "information_modes": list(INFORMATION_MODES),
        "checkpoint_producer_public_commit": "c686dff9f7a8e596212c44c279ed7c89d158bbd8",
        "checkpoint_private_runtime_binding": "per_checkpoint_manifest_entry_exact_git_commit",
        "checkpoint_private_runtime_commit_set_sha256": _runtime_commit_set_sha256(
            entries
        ),
        "all_checkpoints_frozen_before_test": True,
        "locked_test_or_extra_used_for_selection": False,
        "case_identifiers_included": False,
        "entries": entries,
        "figure_display": {
            "training_seed": FIGURE_SEED,
            "control_mode": "transient_only",
            "proposal_mode": "eligible_steady",
            "selected_before_locked_test": True,
        },
    }


def checkpoint_payload(entry: dict, config: dict) -> dict:
    return {
        "schema_version": "aurora.private.aneug_release_730_matched_training_best.v1",
        "protocol_id": "aneug_release_730_matched_training_v1",
        "model_role": "selected_control",
        "information_mode": entry["information_mode"],
        "model_family": "release730_ghd_gps",
        "objective_variant": "field_only",
        "selected_response_rank": None,
        "training_seed": entry["training_seed"],
        "training_stage": "five_seed_matched_information_validation_confirmation",
        "best_epoch": 100,
        "model_state_dict": {
            "weight": torch.tensor([1.0]),
            "cycle_output_scale": torch.tensor(2.0),
            "single_field_output_scale": torch.tensor(1.5),
        },
        "response_basis_embedded": False,
        "reference_tawss_floor": 0.001,
        "cycle_output_scale": None,
        "single_field_output_scale": 1.5,
        "public_commit": config["source"]["checkpoint_producer_public_commit"],
        "private_runtime_commit": entry["private_runtime_commit"],
        "training_config_sha256": config["source"]["matched_training_config_sha256"],
        "fresh_information_activation_sha256": entry[
            "fresh_information_activation_sha256"
        ],
        "fresh_information_protocol_sha256": entry[
            "fresh_information_protocol_sha256"
        ],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["private_train_audit_sha256"],
        "private_overlap_result_sha256": config["split"][
            "private_overlap_result_sha256"
        ],
        "bound_steady_scale_result_sha256": config["split"][
            "bound_steady_scale_result_sha256"
        ],
        "steady_mesh_audit_result_sha256": config["split"][
            "steady_mesh_audit_result_sha256"
        ],
        "initialization": "fresh_seeded_initialization",
        "old_response_local_selection_gate_used": False,
    }


def validation_payload(entry: dict) -> dict:
    return {
        "schema_version": "aurora.aneug_release_730_matched_information_cell.v1",
        "protocol_id": "aneug_release_730_matched_information_analysis_v1",
        "status": "complete_validation_confirmation",
        "model_role": "selected_control",
        "information_mode": entry["information_mode"],
        "model_family": "release730_ghd_gps",
        "objective_variant": "field_only",
        "selected_response_rank": None,
        "training_seed": entry["training_seed"],
        "training_stage": "five_seed_matched_information_validation_confirmation",
        "public_commit": "c686dff9f7a8e596212c44c279ed7c89d158bbd8",
        "private_runtime_commit": entry["private_runtime_commit"],
        "fresh_information_activation_sha256": entry[
            "fresh_information_activation_sha256"
        ],
        "fresh_information_protocol_sha256": entry[
            "fresh_information_protocol_sha256"
        ],
        "transient_training_protocol_sha256": entry[
            "transient_training_protocol_sha256"
        ],
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
        "paper_result_or_claim": False,
    }


def terminal_payload(entry: dict, result_sha: str, checkpoint_sha: str) -> dict:
    return {
        "schema_version": "aurora.private.aneug_release_730_ghd_fresh_information_terminal.v1",
        "protocol_id": "aneug_release_730_ghd_fresh_information_v1",
        "information_mode": entry["information_mode"],
        "training_seed": entry["training_seed"],
        "public_commit": "c686dff9f7a8e596212c44c279ed7c89d158bbd8",
        "private_runtime_commit": entry["private_runtime_commit"],
        "scheduler_state": "F",
        "scheduler_substate": 92,
        "exit_status": 0,
        "run_count": 1,
        "result_sha256": result_sha,
        "best_checkpoint_sha256": checkpoint_sha,
        "fresh_information_activation_sha256": entry[
            "fresh_information_activation_sha256"
        ],
        "fresh_information_protocol_sha256": entry[
            "fresh_information_protocol_sha256"
        ],
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
        "paper_result_or_claim": False,
    }


def materialize_evidence(root: Path, payload: dict, config: dict) -> None:
    for entry in payload["entries"]:
        checkpoint = root / entry["checkpoint_relative_path"]
        validation = root / entry["validation_result_relative_path"]
        terminal = root / entry["terminal_record_relative_path"]
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        torch.save(checkpoint_payload(entry, config), checkpoint)
        validation.write_text(
            json.dumps(validation_payload(entry), sort_keys=True), encoding="utf-8"
        )
        checkpoint_sha = file_sha256(checkpoint)
        result_sha = file_sha256(validation)
        terminal.write_text(
            json.dumps(
                terminal_payload(entry, result_sha, checkpoint_sha), sort_keys=True
            ),
            encoding="utf-8",
        )
        entry["checkpoint_sha256"] = checkpoint_sha
        entry["validation_result_sha256"] = result_sha
        entry["terminal_record_sha256"] = file_sha256(terminal)


def multiseed_payload(payload: dict) -> dict:
    hashes: dict[str, str] = {}
    for entry in payload["entries"]:
        prefix = f"{entry['training_seed']}:{entry['information_mode']}"
        hashes[f"{prefix}:result"] = entry["validation_result_sha256"]
        hashes[f"{prefix}:terminal"] = entry["terminal_record_sha256"]
    cell_means = {
        str(seed): {
            mode: {
                metric: 0.1 + metric_index * 0.01
                for metric_index, metric in enumerate(METRICS)
            }
            for mode in INFORMATION_MODES
        }
        for seed in TRAINING_SEEDS
    }
    crossed = {
        metric: {
            "direction": "higher" if metric == "osi_coverage" else "lower",
            "point_delta": -0.01,
            "ci95_low": -0.02,
            "ci95_high": -0.001,
            "replicates": 10_000,
            "training_seed_count": 5,
            "paired_case_count": 73,
            "per_seed_point_deltas": [-0.01] * 5,
        }
        for metric in METRICS
    }
    return {
        "schema_version": "aurora.private.aneug_release_730_ghd_fresh_multiseed_analysis.v1",
        "status": "complete_five_seed_validation_confirmation",
        "evidence_role": "validation_consistency_before_locked_test",
        "fresh_training_seeds": list(TRAINING_SEEDS),
        "information_modes": list(INFORMATION_MODES),
        "training_seed_count": 5,
        "paired_case_count": 73,
        "bootstrap_replicates": 10_000,
        "bootstrap_seed": 20_260_829,
        "contrast": "eligible_steady_minus_transient_only",
        "cell_means_by_seed": cell_means,
        "crossed_seed_case_difference": crossed,
        "transient_training_protocol_sha256": TRANSIENT_PROTOCOL_SHA,
        "confirmatory_endpoint_direction": {
            "field_relative_l2": "favorable",
            "tawss_normalized_absolute_error": "favorable",
            "osi_mae": "inconclusive",
        },
        "minimum_favorable_seed_count": None,
        "automatic_winner": None,
        "automatic_test_authorization": None,
        "automatic_paper_claim": False,
        "compute_matched_claim": False,
        "population_inference": False,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_identifiers_included": False,
        "input_manifest_sha256": "e" * 64,
        "terminal_result_sha256": hashes,
    }


class CurrentLockedTestContractTests(unittest.TestCase):
    def test_config_is_current_ten_checkpoint_pair_and_flexible_server_bound(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["frozen_checkpoints"]["checkpoint_count"], 10)
        self.assertEqual(
            config["frozen_checkpoints"]["information_modes_per_seed"],
            ["transient_only", "eligible_steady"],
        )
        self.assertEqual(
            config["runtime"]["allowed_servers"], ["introai9", "junjinyong"]
        )
        self.assertTrue(
            config["authorization"][
                "exact_frozen_batch_resume_after_infrastructure_failure"
            ]
        )
        self.assertFalse(config["authorization"]["execute_now"])
        self.assertFalse(config["authorization"]["read_processed_only_extra"])

    def test_scope_mutations_fail_closed(self) -> None:
        config = load_config(CONFIG)
        for section, key, value, reason in (
            ("split", "locked_test_cases", 72, "split"),
            ("frozen_checkpoints", "checkpoint_count", 20, "frozen_checkpoints"),
            ("evaluation", "automatic_winner", True, "evaluation"),
            ("figure", "seed_selected_from_test_outcomes", True, "figure"),
            ("authorization", "training", True, "authorization"),
        ):
            changed = copy.deepcopy(config)
            changed[section][key] = value
            with self.assertRaisesRegex(CurrentGHDLockedTestError, reason):
                validate_config(changed)

    def test_activation_binds_evaluator_producer_runtime_server_and_one_session(self) -> None:
        config = load_config(CONFIG)
        evaluator = "1" * 40
        activation = {
            "schema_version": PRIMARY_ACTIVATION_SCHEMA,
            "protocol_id": config["protocol_id"],
            "evaluator_public_commit": evaluator,
            "evaluator_quality_conclusion": "success",
            "checkpoint_producer_public_commit": config["source"][
                "checkpoint_producer_public_commit"
            ],
            "checkpoint_private_runtime_binding": config["source"][
                "checkpoint_private_runtime_binding"
            ],
            "authorized_stage": (
                "one_access_session_frozen_five_seed_T_vs_separated_TS_locked_test"
            ),
            "access_session_ordinal": 1,
            "created_before_locked_test_read": True,
            "prior_access_session_marker_sha256": None,
            "execution_server": "junjinyong",
            "queue": "ssu_a6gpu",
            "config_sha256": "e" * 64,
            "evaluator_source_sha256": "f" * 64,
            "checkpoint_manifest_sha256": HEX,
            "checkpoint_private_runtime_commit_set_sha256": HEX,
            "multiseed_validation_result_sha256": HEX,
            "private_split_manifest_sha256": config["split"][
                "private_manifest_sha256"
            ],
            "private_train_audit_sha256": config["split"][
                "private_train_audit_sha256"
            ],
            "test_case_digest": config["split"]["test_case_digest"],
            "test_loader_order_sha256": "d" * 64,
            "checkpoint_count": 10,
            "training": False,
            "read_locked_test": True,
            "read_processed_only_extra": False,
            "model_or_selection_change_after_access": False,
            "exact_same_frozen_batch_retry_only": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, evaluator)
            activation["queue"] = "coss_a6gpu"
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaisesRegex(CurrentGHDLockedTestError, "activation_identity"):
                validate_activation(path, config, evaluator)

    def test_recovery_activation_preserves_the_existing_access_session(self) -> None:
        config = load_config(CONFIG)
        evaluator = "1" * 40
        activation = {
            "schema_version": RECOVERY_ACTIVATION_SCHEMA,
            "protocol_id": config["protocol_id"],
            "status": "activated_for_exact_same_access_session_checkpoint_schema_recovery",
            "evaluator_public_commit": evaluator,
            "evaluator_quality_conclusion": "success",
            "checkpoint_producer_public_commit": config["source"][
                "checkpoint_producer_public_commit"
            ],
            "checkpoint_private_runtime_binding": config["source"][
                "checkpoint_private_runtime_binding"
            ],
            "authorized_stage": (
                "one_access_session_exact_frozen_batch_checkpoint_schema_recovery"
            ),
            "access_session_ordinal": 1,
            "created_before_locked_test_read": False,
            "root_access_activation_sha256": "1" * 64,
            "prior_access_session_marker_sha256": "2" * 64,
            "prior_failed_job_id": "120604.ECE-util1",
            "prior_failure_reason": (
                "checkpoint_cycle_scale_top_level_key_missing_before_model_evaluation"
            ),
            "prior_access_session_started": True,
            "prior_locked_test_cases_read": 73,
            "prior_reference_selection_created": True,
            "prior_reference_selection_sha256": "3" * 64,
            "prior_checkpoint_evaluations_completed": 0,
            "prior_model_predictions_created": False,
            "prior_result_created": False,
            "prior_figure_payload_created": False,
            "checkpoint_batch_changed_after_access": False,
            "split_or_loader_order_changed_after_access": False,
            "metric_or_bootstrap_change_after_access": False,
            "execution_server": "introai9",
            "queue": "coss_a6gpu",
            "config_sha256": "4" * 64,
            "evaluator_source_sha256": "5" * 64,
            "checkpoint_manifest_sha256": HEX,
            "checkpoint_private_runtime_commit_set_sha256": HEX,
            "multiseed_validation_result_sha256": HEX,
            "private_split_manifest_sha256": config["split"][
                "private_manifest_sha256"
            ],
            "private_train_audit_sha256": config["split"][
                "private_train_audit_sha256"
            ],
            "test_case_digest": config["split"]["test_case_digest"],
            "test_loader_order_sha256": "6" * 64,
            "checkpoint_count": 10,
            "training": False,
            "read_locked_test": True,
            "read_processed_only_extra": False,
            "model_or_selection_change_after_access": False,
            "exact_same_frozen_batch_retry_only": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, evaluator)
            activation["checkpoint_batch_changed_after_access"] = True
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaisesRegex(
                CurrentGHDLockedTestError, "activation_recovery_scope"
            ):
                validate_activation(path, config, evaluator)

    def test_access_marker_is_idempotent_only_for_exact_same_session(self) -> None:
        payload = {
            "schema_version": "test",
            "activation_sha256": HEX,
            "access_session_ordinal": 1,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "marker.json"
            _write_or_validate_access_marker(path, payload)
            _write_or_validate_access_marker(path, payload)
            changed = dict(payload, activation_sha256="b" * 64)
            with self.assertRaisesRegex(
                CurrentGHDLockedTestError, "access_session_marker_mismatch"
            ):
                _write_or_validate_access_marker(path, changed)

    def test_pbs_is_one_gpu_one_batch_and_has_stable_access_session(self) -> None:
        text = PBS.read_text(encoding="utf-8")
        source = (
            ROOT
            / "src"
            / "aurora"
            / "aneug_release_730_ghd_current_locked_test.py"
        ).read_text(encoding="utf-8")
        self.assertIn("${PBS_JOBID:?current locked test is PBS-only}", text)
        self.assertIn("#PBS -l select=1:ncpus=4:mem=64gb:ngpus=1:Qlist=a6000", text)
        self.assertEqual(
            text.count("python -m aurora.aneug_release_730_ghd_current_locked_test"),
            1,
        )
        self.assertIn("AURORA_ACCESS_SESSION_ROOT", text)
        self.assertIn(
            '--expected-execution-server "$AURORA_EXECUTION_SERVER"', text
        )
        self.assertIn(
            'activation["execution_server"] == args.expected_execution_server',
            source,
        )
        self.assertIn(
            "--access-marker /private/access/locked_test_access_session.json", text
        )
        self.assertIn("AURORA_PRIOR_LOCKED_RUN_ROOT", text)
        self.assertIn("--prior-figure-selection /private/prior/figure_selection.json", text)
        self.assertIn('--prior-failed-job-id "$AURORA_PRIOR_FAILED_JOB_ID"', text)
        self.assertNotIn("response-basis", text)
        self.assertNotIn("processed_only", text)
        self.assertNotIn("qsub ", text)


class CurrentLockedTestEvidenceTests(unittest.TestCase):
    def test_manifest_requires_exact_five_by_two_grid(self) -> None:
        config = load_config(CONFIG)
        payload = manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            validated = validate_checkpoint_manifest(path, file_sha256(path), config)
            self.assertEqual(len(validated["entries"]), 10)
            payload["entries"][-1] = copy.deepcopy(payload["entries"][0])
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(CurrentGHDLockedTestError, "checkpoint_duplicate"):
                validate_checkpoint_manifest(path, file_sha256(path), config)

    def test_manifest_binds_each_checkpoint_private_runtime_commit(self) -> None:
        config = load_config(CONFIG)
        payload = manifest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            payload["entries"][0]["private_runtime_commit"] = "f" * 40
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(
                CurrentGHDLockedTestError, "checkpoint_private_runtime_set"
            ):
                validate_checkpoint_manifest(path, file_sha256(path), config)

            payload["checkpoint_private_runtime_commit_set_sha256"] = (
                _runtime_commit_set_sha256(payload["entries"])
            )
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            validated = validate_checkpoint_manifest(
                path, file_sha256(path), config
            )
            self.assertEqual(
                validated["entries"][0]["private_runtime_commit"], "f" * 40
            )

    def test_checkpoint_payload_is_current_ghd_control_not_legacy_proposal(self) -> None:
        config = load_config(CONFIG)
        entry = checkpoint_entries()[0]
        checkpoint = checkpoint_payload(entry, config)
        _validate_checkpoint_payload(checkpoint, entry, config)
        checkpoint["model_family"] = "release730_response_plus_local_residual"
        with self.assertRaisesRegex(CurrentGHDLockedTestError, "checkpoint_payload_identity"):
            _validate_checkpoint_payload(checkpoint, entry, config)
        checkpoint = checkpoint_payload(entry, config)
        checkpoint["private_runtime_commit"] = "f" * 40
        with self.assertRaisesRegex(CurrentGHDLockedTestError, "checkpoint_payload_identity"):
            _validate_checkpoint_payload(checkpoint, entry, config)
        checkpoint = checkpoint_payload(entry, config)
        checkpoint["model_state_dict"]["cycle_output_scale"] = torch.tensor(3.0)
        checkpoint["cycle_output_scale"] = 2.0
        with self.assertRaisesRegex(CurrentGHDLockedTestError, "checkpoint_payload_values"):
            _validate_checkpoint_payload(checkpoint, entry, config)

    def test_checkpoint_common_values_use_the_registered_state_buffer(self) -> None:
        config = load_config(CONFIG)
        checkpoint = checkpoint_payload(checkpoint_entries()[0], config)
        self.assertIsNone(checkpoint["cycle_output_scale"])
        _validate_checkpoint_payload(checkpoint, checkpoint_entries()[0], config)
        _validate_checkpoint_common_values(checkpoint, 0.001, 2.0)
        checkpoint["model_state_dict"]["cycle_output_scale"] = torch.tensor(3.0)
        with self.assertRaisesRegex(
            CurrentGHDLockedTestError, "checkpoint_common_values"
        ):
            _validate_checkpoint_common_values(checkpoint, 0.001, 2.0)

    def test_preflight_verifies_all_ten_triples_before_data(self) -> None:
        config = load_config(CONFIG)
        payload = manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_evidence(root, payload, config)
            floor, scale = preflight_frozen_evidence(payload, root, config)
            self.assertEqual(floor, 0.001)
            self.assertEqual(scale, 2.0)
            payload["entries"][0]["checkpoint_sha256"] = HEX
            with self.assertRaisesRegex(CurrentGHDLockedTestError, "checkpoint_hash"):
                preflight_frozen_evidence(payload, root, config)

    def test_preflight_separates_scheduler_retries_from_scientific_entries(self) -> None:
        config = load_config(CONFIG)
        payload = manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_evidence(root, payload, config)
            entry = payload["entries"][0]
            terminal_path = root / entry["terminal_record_relative_path"]
            terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
            terminal.update(
                {
                    "run_count": 6,
                    "scheduler_run_count": 6,
                    "scientific_script_entry_count": 1,
                    "pre_script_scheduler_attempt_count": 5,
                }
            )
            terminal_path.write_text(
                json.dumps(terminal, sort_keys=True), encoding="utf-8"
            )
            entry["terminal_record_sha256"] = file_sha256(terminal_path)
            floor, scale = preflight_frozen_evidence(payload, root, config)
            self.assertEqual((floor, scale), (0.001, 2.0))

            terminal["scientific_script_entry_count"] = 2
            terminal_path.write_text(
                json.dumps(terminal, sort_keys=True), encoding="utf-8"
            )
            entry["terminal_record_sha256"] = file_sha256(terminal_path)
            with self.assertRaisesRegex(
                CurrentGHDLockedTestError, "terminal_record_identity"
            ):
                preflight_frozen_evidence(payload, root, config)

    def test_preflight_accepts_only_accounted_post_science_envelope_failure(self) -> None:
        config = load_config(CONFIG)
        payload = manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_evidence(root, payload, config)
            entry = payload["entries"][0]
            terminal_path = root / entry["terminal_record_relative_path"]
            terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
            terminal.update(
                {
                    "scheduler_state": "F",
                    "scheduler_substate": 91,
                    "exit_status": -18,
                    "run_count": 21,
                    "scheduler_run_count": 21,
                    "scientific_script_entry_count": 1,
                    "pre_script_scheduler_attempt_count": None,
                    "non_scientific_scheduler_attempt_count": 20,
                    "scheduler_acknowledged_clean_exit": False,
                    "scheduler_envelope_disposition": (
                        "science_complete_post_execution_envelope_failure"
                    ),
                }
            )
            terminal_path.write_text(
                json.dumps(terminal, sort_keys=True), encoding="utf-8"
            )
            entry["terminal_record_sha256"] = file_sha256(terminal_path)
            floor, scale = preflight_frozen_evidence(payload, root, config)
            self.assertEqual((floor, scale), (0.001, 2.0))

            terminal["non_scientific_scheduler_attempt_count"] = 19
            terminal_path.write_text(
                json.dumps(terminal, sort_keys=True), encoding="utf-8"
            )
            entry["terminal_record_sha256"] = file_sha256(terminal_path)
            with self.assertRaisesRegex(
                CurrentGHDLockedTestError, "terminal_record_identity"
            ):
                preflight_frozen_evidence(payload, root, config)

    def test_multiseed_result_must_bind_exact_manifest_result_and_terminal_hashes(self) -> None:
        config = load_config(CONFIG)
        payload = manifest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialize_evidence(root, payload, config)
            result = multiseed_payload(payload)
            path = root / "multiseed.json"
            path.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
            validate_multiseed_result(path, file_sha256(path), payload)

            with_diagnostics = copy.deepcopy(result)
            for modes in with_diagnostics["cell_means_by_seed"].values():
                for metrics in modes.values():
                    metrics["peak_systolic_wss_relative_l2"] = 0.25
            with_diagnostics["crossed_seed_case_difference"][
                "peak_systolic_wss_relative_l2"
            ] = {
                "direction": "lower",
                "point_delta": -0.01,
                "ci95_low": -0.02,
                "ci95_high": -0.001,
                "replicates": 10_000,
                "training_seed_count": 5,
                "paired_case_count": 73,
                "per_seed_point_deltas": [-0.01] * 5,
            }
            path.write_text(
                json.dumps(with_diagnostics, sort_keys=True), encoding="utf-8"
            )
            validate_multiseed_result(path, file_sha256(path), payload)

            missing_required = copy.deepcopy(result)
            missing_required["cell_means_by_seed"][str(TRAINING_SEEDS[0])][
                INFORMATION_MODES[0]
            ].pop("field_relative_l2")
            path.write_text(
                json.dumps(missing_required, sort_keys=True), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                CurrentGHDLockedTestError, "multiseed_cell_means"
            ):
                validate_multiseed_result(path, file_sha256(path), payload)

            path.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
            result["terminal_result_sha256"].pop(next(iter(result["terminal_result_sha256"])))
            path.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(CurrentGHDLockedTestError, "multiseed_inputs"):
                validate_multiseed_result(path, file_sha256(path), payload)


class CurrentLockedTestAnalysisAndFigureTests(unittest.TestCase):
    def test_crossed_analysis_reports_only_prespecified_steady_minus_transient(self) -> None:
        config = load_config(CONFIG)
        rows: dict[int, dict[str, list[dict[str, float]]]] = {}
        for seed_index, seed in enumerate(TRAINING_SEEDS):
            rows[seed] = {}
            for mode in INFORMATION_MODES:
                offset = 0.0 if mode == "transient_only" else -0.01
                rows[seed][mode] = [
                    {
                        "field_relative_l2": 0.30 + offset + seed_index * 0.001,
                        "mean_wss_vector_error": 0.20 + offset,
                        "tawss_normalized_absolute_error": 0.18 + offset,
                        "osi_mae": 0.01 + offset / 10.0,
                        "osi_coverage": 0.90 - offset,
                    }
                    for _ in range(73)
                ]
        result = analyze_locked_test(rows, config)
        self.assertEqual(result["contrast"], "eligible_steady_minus_transient_only")
        self.assertLess(
            result["crossed_seed_case_difference"]["field_relative_l2"][
                "ci95_high"
            ],
            0.0,
        )
        self.assertEqual(
            result["confirmatory_endpoint_direction"]["field_relative_l2"],
            "favorable",
        )
        self.assertIsNone(result["automatic_winner"])

    def test_figure_selection_limits_and_labels_are_current_and_reference_only(self) -> None:
        config = load_config(CONFIG)
        cases = []
        for index in range(73):
            amplitude = 1.0 + index / 100.0
            wss = torch.zeros(80, 3, 3)
            wss[:, :, 0] = amplitude
            cases.append(
                {
                    "wss": wss,
                    "vertex_weights": torch.tensor([0.2, 0.3, 0.5]),
                    "coordinates": torch.tensor(
                        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
                    ),
                }
            )
        phase_weights = torch.full((80,), 1.0 / 80.0)
        selection = build_current_reference_selection(
            cases, phase_weights, 0.001, config
        )
        ordinals = selection["selected_locked_test_ordinals"]
        predictions = {
            mode: [cases[ordinal]["wss"].clone() for ordinal in ordinals]
            for mode in INFORMATION_MODES
        }
        payload = build_current_figure_payload(
            cases,
            torch.tensor([[0, 1, 2]], dtype=torch.int64),
            predictions,
            selection,
            phase_weights,
            config,
        )
        self.assertEqual(
            payload["method_order"],
            ["reference", "transient_only", "eligible_steady"],
        )
        self.assertEqual(payload["method_display_labels"]["eligible_steady"], "T+S")
        self.assertEqual(
            payload["method_schematic"],
            "geometry_encoder_to_cycle_decoder_with_train_only_disposable_steady_head",
        )
        self.assertTrue(payload["limits_camera_and_selection_are_reference_only"])
        self.assertFalse(payload["steady_head_used_at_inference"])
        self.assertFalse(payload["case_identifiers_included"])


if __name__ == "__main__":
    unittest.main()
