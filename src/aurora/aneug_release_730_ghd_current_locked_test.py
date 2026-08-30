"""One access-session locked test for the current five-seed GHD T/T+S pair.

This path is intentionally separate from the historical twenty-checkpoint
response/local T0.  It accepts exactly five fresh transient-only checkpoints
and their five regime-separated eligible-steady counterparts, freezes a
reference-only figure selection before any prediction, and evaluates the ten
checkpoints with one common 73-case loader and metric kernel.  It performs no
training, model selection, threshold selection, or processed-only-extra read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_figure_protocol import build_reference_selection
from aurora.aneug_processed_v4_d9 import _extract_topology
from aurora.aneug_release_730_ghd_gps_baseline import _case_from_record
from aurora.aneug_release_730_matched_information_analysis import (
    DIAGNOSTIC_METRICS,
    METRIC_DIRECTIONS,
    METRICS,
    PRIMARY_CLAIM_ERROR_METRICS,
    SUPPORTING_ERROR_METRICS,
)
from aurora.aneug_release_730_matched_training import (
    build_model,
    evaluate,
    load_config as load_matched_training_config,
)
from aurora.aneug_release_730_multiseed_confirmation import _crossed_bootstrap
from aurora.aneug_release_730_train_audit import (
    _ordered_digest,
    index_case_records,
    selected_training_records,
    validate_split_evidence,
)
from aurora.cycle_functionals import compute_cycle_functionals


class CurrentGHDLockedTestError(RuntimeError):
    """Raised when the frozen current-pair test boundary is violated."""


TRAINING_SEEDS = (20_260_901, 20_260_902, 20_260_903, 20_260_904, 20_260_905)
INFORMATION_MODES = ("transient_only", "eligible_steady")
FIGURE_SEED = 20_260_903
TRAINING_STAGE = "five_seed_matched_information_validation_confirmation"
CHECKPOINT_SCHEMA = "aurora.private.aneug_release_730_matched_training_best.v1"
VALIDATION_SCHEMA = "aurora.aneug_release_730_matched_information_cell.v1"
VALIDATION_PROTOCOL = "aneug_release_730_matched_information_analysis_v1"
TERMINAL_SCHEMA = "aurora.private.aneug_release_730_ghd_fresh_information_terminal.v1"


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise CurrentGHDLockedTestError(reason)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_git_commit(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value)
    )


def _runtime_commit_set_sha256(entries: Sequence[Mapping[str, Any]]) -> str:
    bindings = sorted(
        (
            int(entry["training_seed"]),
            str(entry["information_mode"]),
            str(entry["private_runtime_commit"]),
        )
        for entry in entries
    )
    payload = json.dumps(bindings, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _is_single_scientific_execution(terminal: Mapping[str, Any]) -> bool:
    """Accept scheduler retries only with explicit one-entry provenance.

    A PBS ``run_count`` is an envelope-level counter.  After one completed
    scientific entry, MOM acknowledgement/obituary retries may increase it
    without launching the training script again.  New terminal records bind
    that case with an explicit count of all non-scientific attempts; older
    records remain admissible only through the narrower pre-script field or a
    legacy single run.
    """

    run_count = terminal.get("run_count")
    scheduler_run_count = terminal.get("scheduler_run_count", run_count)
    if (
        not isinstance(run_count, int)
        or isinstance(run_count, bool)
        or not isinstance(scheduler_run_count, int)
        or isinstance(scheduler_run_count, bool)
        or run_count < 1
        or scheduler_run_count != run_count
    ):
        return False
    scientific_entries = terminal.get("scientific_script_entry_count")
    non_scientific_attempts = terminal.get(
        "non_scientific_scheduler_attempt_count"
    )
    if non_scientific_attempts is not None:
        return (
            scientific_entries == 1
            and isinstance(non_scientific_attempts, int)
            and not isinstance(non_scientific_attempts, bool)
            and non_scientific_attempts == run_count - scientific_entries
        )
    pre_script_attempts = terminal.get("pre_script_scheduler_attempt_count")
    if scientific_entries is None and pre_script_attempts is None:
        return run_count == 1
    return (
        scientific_entries == 1
        and isinstance(pre_script_attempts, int)
        and not isinstance(pre_script_attempts, bool)
        and pre_script_attempts == run_count - 1
    )


def _is_scientifically_terminal_execution(terminal: Mapping[str, Any]) -> bool:
    """Accept a clean PBS exit or a hash-bound post-science envelope failure."""

    disposition = terminal.get("scheduler_envelope_disposition", "clean_exit")
    if disposition == "clean_exit":
        return (
            terminal.get("scheduler_state") == "F"
            and terminal.get("scheduler_substate") == 92
            and terminal.get("exit_status") == 0
            and terminal.get("scheduler_acknowledged_clean_exit", True) is True
        )
    if disposition == "science_complete_post_execution_envelope_failure":
        return (
            terminal.get("scheduler_state") == "F"
            and terminal.get("scheduler_substate") == 91
            and terminal.get("exit_status") == -18
            and terminal.get("scheduler_acknowledged_clean_exit") is False
            and terminal.get("run_count", 0) > 1
        )
    return False


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
    return digest.hexdigest()


def _atomic_private_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    try:
        temporary.write_text(
            json.dumps(dict(payload), indent=2, sort_keys=True, allow_nan=False)
            + "\n",
            encoding="utf-8",
        )
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_private_torch(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    try:
        torch.save(dict(payload), temporary)
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_or_validate_access_marker(
    path: str | Path, payload: Mapping[str, Any]
) -> None:
    """Create one access-session marker or validate an exact scheduler retry."""

    target = Path(path)
    expected = dict(payload)
    if target.exists():
        observed = json.loads(target.read_text(encoding="utf-8"))
        _require(observed == expected, "access_session_marker_mismatch")
        _require((target.stat().st_mode & 0o077) == 0, "access_session_marker_mode")
        return
    _atomic_private_json(target, expected)


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_ghd_current_locked_test.v1"
        and config.get("protocol_id")
        == "aneug_release_730_ghd_current_locked_test_v1"
        and config.get("status")
        == "prepared_non_executable_until_complete_five_seed_evidence_and_private_activation",
        "config_identity",
    )
    source = config["source"]
    expected_source = {
        "dataset_revision": "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "processed_v5_bytes": 33_233_856_917,
        "processed_v5_sha256": "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
        "steady_norm_bytes": 9_632_510_050,
        "steady_norm_sha256": "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "checkpoint_producer_public_commit": "c686dff9f7a8e596212c44c279ed7c89d158bbd8",
        "checkpoint_private_runtime_binding": "per_checkpoint_manifest_entry_exact_git_commit",
        "matched_training_config_sha256": "08aa39d3f3f8380e0d28fa1838b56bec5fa774941683b809fb04c8ab321d2ecf",
        "reference_selection_source_sha256": "f0d2a526bdc215520f0a01c4d398a6db64994e84a9d57e3724ed0fc9534a9b9a",
        "cycle_functionals_source_sha256": "5295afa5da2dee4606803fea8f837e126a5f531ca647e873e5b6fadb03578574",
        "public_split_result_sha256": "4fa3be7c217c3a84b86f477c90112377fb913f6b0b47b829d684b270555bf991",
        "public_train_audit_sha256": "3c525820023a56862c6652441c5d00f43412d3c868840149e5f120b8ed2a9587",
    }
    _require(
        all(source.get(key) == value for key, value in expected_source.items()),
        "source",
    )
    split = config["split"]
    _require(
        split["split_key_sha256"]
        == "e75e667def522491a5acb4fe33364c6628db500ae44fd85eba2381cf3b0867a3"
        and split["train_case_digest"]
        == "a23bbda2d74d218e4e77c8e446f54a60ebbed45b906a9acb544988e8bba31aaa"
        and split["validation_case_digest"]
        == "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024"
        and split["private_overlap_result_sha256"]
        == "52219b9a7161f0932a4ed80020a339510474431b67e168741426c2a12e5092ef"
        and split["bound_steady_scale_result_sha256"]
        == "ed589b0322e8ea7cf4c2f33e8f40f04dfc114a5fa32f5c484c4b183e950a7c74"
        and split["steady_mesh_audit_result_sha256"]
        == "f283512edd38abcae5335f6046a67fe9f670cfad67b5eb1b1378cfe11ecce254"
        and (
            split["train_cases"],
            split["validation_cases"],
            split["locked_test_cases"],
            split["processed_only_extra_cases"],
        )
        == (584, 73, 73, 79)
        and split["private_manifest_sha256"]
        == "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f"
        and split["private_train_audit_sha256"]
        == "ce1dd6d2852e290fbe187ac062af155f522cd4b8a82c1580b5430d15ed519385"
        and split["test_case_digest"]
        == "1f87f52fc4b819548aebcc6df77f90830d475d1e92df0ca833980347d792aa56"
        and split["test_loader_order_sha256"] is None
        and split["test_loader_order_source"]
        == "required_from_fresh_private_activation_before_any_field_read"
        and split["all_80_phases_follow_geometry"] is True
        and split["read_train_or_validation_fields"] is False
        and split["read_locked_test_fields_only_after_access_marker"] is True
        and split["read_processed_only_extra_fields"] is False,
        "split",
    )
    frozen = config["frozen_checkpoints"]
    _require(
        frozen["training_seeds"] == list(TRAINING_SEEDS)
        and frozen["information_modes_per_seed"] == list(INFORMATION_MODES)
        and frozen["model_role"] == "selected_control"
        and frozen["model_family"] == "release730_ghd_gps"
        and frozen["objective_variant"] == "field_only"
        and frozen["selected_response_rank"] is None
        and frozen["training_stage"] == TRAINING_STAGE
        and frozen["checkpoint_count"] == 10
        and frozen["all_frozen_before_test"] is True
        and frozen["training_or_checkpoint_selection_in_test"] is False,
        "frozen_checkpoints",
    )
    evaluation = config["evaluation"]
    _require(
        evaluation["metrics"] == list(METRICS)
        and evaluation["primary_claim_error_metrics"]
        == list(PRIMARY_CLAIM_ERROR_METRICS)
        and evaluation["supporting_error_metrics"]
        == list(SUPPORTING_ERROR_METRICS)
        and evaluation["diagnostic_metrics"] == list(DIAGNOSTIC_METRICS)
        and evaluation["contrast"] == "eligible_steady_minus_transient_only"
        and evaluation["bootstrap_replicates"] == 10_000
        and evaluation["bootstrap_seed"] == 20_260_830
        and evaluation["bootstrap_resampling"]
        == "crossed_training_seed_and_geometry_case_with_replacement"
        and evaluation["absolute_performance_threshold"] is None
        and evaluation["automatic_winner"] is False
        and evaluation["automatic_novelty_conclusion"] is False
        and evaluation["population_inference"] is False,
        "evaluation",
    )
    figure = config["figure"]
    _require(
        figure["protocol_id"] == "aneug_release_730_regime_separated_figure_v1"
        and figure["reference_only_selection_before_any_prediction"] is True
        and figure["case_quantiles"] == [0.1, 0.5, 0.9]
        and figure["trace_vertex_quantile"] == 0.9
        and figure["display_training_seed"] == FIGURE_SEED
        and figure["display_control_mode"] == "transient_only"
        and figure["display_proposal_mode"] == "eligible_steady"
        and figure["seed_selected_from_test_outcomes"] is False
        and figure["selected_case_count"] == 3
        and figure["main_case_index"] == 2
        and figure["main_case_role"] == "high_reference_OSI"
        and figure["tawss_limits_source"] == "three_selected_references_only"
        and figure["trace_limits_source"] == "three_selected_references_only"
        and figure["compact_payload_only"] is True
        and figure["case_identifiers_in_payload"] is False,
        "figure",
    )
    runtime = config["runtime"]
    _require(
        runtime["allowed_servers"] == ["introai9", "junjinyong"]
        and runtime["queue_by_server"]
        == {"introai9": "coss_a6gpu", "junjinyong": "ssu_a6gpu"}
        and runtime["Qlist"] == "a6000"
        and (runtime["ncpus"], runtime["memory_gb"], runtime["ngpus"])
        == (4, 64, 1),
        "runtime",
    )
    authorization = config["authorization"]
    _require(
        authorization["execute_now"] is False
        and authorization["requires_fresh_private_activation"] is True
        and authorization["requires_complete_five_seed_validation_result"] is True
        and authorization["requires_exact_ten_checkpoint_manifest"] is True
        and authorization["requires_one_access_session_marker"] is True
        and authorization["locked_test_access_sessions"] == 1
        and authorization["scheduler_envelope_replacement_before_field_access"] is True
        and authorization["exact_frozen_batch_resume_after_infrastructure_failure"] is True
        and authorization["training"] is False
        and authorization["optimizer_or_scheduler_state_change"] is False
        and authorization[
            "post_access_model_loss_seed_threshold_endpoint_or_figure_selection_change"
        ]
        is False
        and authorization["read_processed_only_extra"] is False
        and authorization["case_identifiers_in_result"] is False
        and authorization["automatic_paper_claim"] is False
        and authorization["maintain_public_site"] is False,
        "authorization",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(
    path: str | Path, config: Mapping[str, Any], evaluator_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    server = activation.get("execution_server")
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_ghd_current_locked_test_activation.v1"
        and activation.get("protocol_id") == config["protocol_id"]
        and activation.get("evaluator_public_commit") == evaluator_commit
        and activation.get("evaluator_quality_conclusion") == "success"
        and activation.get("checkpoint_producer_public_commit")
        == config["source"]["checkpoint_producer_public_commit"]
        and activation.get("checkpoint_private_runtime_binding")
        == config["source"]["checkpoint_private_runtime_binding"]
        and activation.get("authorized_stage")
        == "one_access_session_frozen_five_seed_T_vs_separated_TS_locked_test"
        and activation.get("access_session_ordinal") == 1
        and activation.get("created_before_locked_test_read") is True
        and activation.get("prior_access_session_marker_sha256") is None
        and server in config["runtime"]["allowed_servers"]
        and activation.get("queue") == config["runtime"]["queue_by_server"][server],
        "activation_identity",
    )
    for key in (
        "config_sha256",
        "evaluator_source_sha256",
        "checkpoint_manifest_sha256",
        "checkpoint_private_runtime_commit_set_sha256",
        "multiseed_validation_result_sha256",
        "private_split_manifest_sha256",
        "private_train_audit_sha256",
        "test_case_digest",
        "test_loader_order_sha256",
    ):
        _require(_is_sha256(activation.get(key)), f"activation_{key}")
    _require(
        activation["private_split_manifest_sha256"]
        == config["split"]["private_manifest_sha256"]
        and activation["private_train_audit_sha256"]
        == config["split"]["private_train_audit_sha256"]
        and activation["test_case_digest"] == config["split"]["test_case_digest"]
        and activation.get("checkpoint_count") == 10
        and activation.get("training") is False
        and activation.get("read_locked_test") is True
        and activation.get("read_processed_only_extra") is False
        and activation.get("model_or_selection_change_after_access") is False
        and activation.get("exact_same_frozen_batch_retry_only") is True,
        "activation_scope",
    )
    return dict(activation)


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def validate_checkpoint_manifest(
    path: str | Path, expected_sha256: str, config: Mapping[str, Any]
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "checkpoint_manifest_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_ghd_current_frozen_checkpoints.v1"
        and payload.get("status")
        == "complete_ten_checkpoints_frozen_before_locked_test"
        and payload.get("checkpoint_count") == 10
        and payload.get("training_seed_count") == 5
        and payload.get("information_modes") == list(INFORMATION_MODES)
        and payload.get("checkpoint_producer_public_commit")
        == config["source"]["checkpoint_producer_public_commit"]
        and payload.get("checkpoint_private_runtime_binding")
        == config["source"]["checkpoint_private_runtime_binding"]
        and payload.get("all_checkpoints_frozen_before_test") is True
        and payload.get("locked_test_or_extra_used_for_selection") is False
        and payload.get("case_identifiers_included") is False,
        "checkpoint_manifest_scope",
    )
    entries = payload.get("entries")
    _require(isinstance(entries, list) and len(entries) == 10, "checkpoint_entries")
    observed: set[tuple[int, str]] = set()
    paths: set[str] = set()
    transient_protocols: set[str] = set()
    for entry in entries:
        _require(isinstance(entry, Mapping), "checkpoint_entry")
        seed = entry.get("training_seed")
        mode = entry.get("information_mode")
        pair = (seed, mode)
        _require(seed in TRAINING_SEEDS and mode in INFORMATION_MODES, "checkpoint_pair")
        _require(
            entry.get("model_role") == "selected_control"
            and entry.get("model_family") == "release730_ghd_gps"
            and entry.get("objective_variant") == "field_only"
            and entry.get("selected_response_rank") is None
            and entry.get("training_stage") == TRAINING_STAGE
            and entry.get("public_commit")
            == config["source"]["checkpoint_producer_public_commit"]
            and _is_git_commit(entry.get("private_runtime_commit")),
            "checkpoint_cell_identity",
        )
        for key in (
            "checkpoint_sha256",
            "validation_result_sha256",
            "terminal_record_sha256",
            "fresh_information_activation_sha256",
            "fresh_information_protocol_sha256",
            "transient_training_protocol_sha256",
        ):
            _require(_is_sha256(entry.get(key)), f"checkpoint_{key}")
        for key in (
            "checkpoint_relative_path",
            "validation_result_relative_path",
            "terminal_record_relative_path",
        ):
            _require(_safe_relative_path(entry.get(key)), f"checkpoint_{key}")
        checkpoint_path = str(entry["checkpoint_relative_path"])
        _require(pair not in observed and checkpoint_path not in paths, "checkpoint_duplicate")
        observed.add(pair)
        paths.add(checkpoint_path)
        transient_protocols.add(str(entry["transient_training_protocol_sha256"]))
    _require(
        observed == set((seed, mode) for seed in TRAINING_SEEDS for mode in INFORMATION_MODES),
        "checkpoint_grid",
    )
    _require(len(transient_protocols) == 1, "checkpoint_training_protocol")
    _require(
        payload.get("checkpoint_private_runtime_commit_set_sha256")
        == _runtime_commit_set_sha256(entries),
        "checkpoint_private_runtime_set",
    )
    figure = payload.get("figure_display")
    _require(
        isinstance(figure, Mapping)
        and figure.get("training_seed") == FIGURE_SEED
        and figure.get("control_mode") == "transient_only"
        and figure.get("proposal_mode") == "eligible_steady"
        and figure.get("selected_before_locked_test") is True,
        "checkpoint_figure_display",
    )
    return dict(payload)


def validate_multiseed_result(
    path: str | Path,
    expected_sha256: str,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "multiseed_result_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_ghd_fresh_multiseed_analysis.v1"
        and payload.get("status") == "complete_five_seed_validation_confirmation"
        and payload.get("evidence_role") == "validation_consistency_before_locked_test"
        and payload.get("fresh_training_seeds") == list(TRAINING_SEEDS)
        and payload.get("information_modes") == list(INFORMATION_MODES)
        and payload.get("training_seed_count") == 5
        and payload.get("paired_case_count") == 73
        and payload.get("contrast") == "eligible_steady_minus_transient_only"
        and payload.get("minimum_favorable_seed_count") is None
        and payload.get("automatic_winner") is None
        and payload.get("automatic_test_authorization") is None
        and payload.get("automatic_paper_claim") is False
        and payload.get("compute_matched_claim") is False
        and payload.get("population_inference") is False
        and payload.get("locked_test_field_case_count_read") == 0
        and payload.get("processed_only_extra_field_case_count_read") == 0
        and payload.get("case_identifiers_included") is False,
        "multiseed_result_scope",
    )
    _require(
        payload.get("bootstrap_replicates") == 10_000
        and payload.get("bootstrap_seed") == 20_260_829
        and _is_sha256(payload.get("input_manifest_sha256")),
        "multiseed_bootstrap",
    )
    cell_means = payload.get("cell_means_by_seed")
    _require(
        isinstance(cell_means, Mapping)
        and set(cell_means) == {str(seed) for seed in TRAINING_SEEDS},
        "multiseed_cell_means",
    )
    for seed in TRAINING_SEEDS:
        modes = cell_means[str(seed)]
        _require(
            isinstance(modes, Mapping) and set(modes) == set(INFORMATION_MODES),
            "multiseed_cell_means",
        )
        for mode in INFORMATION_MODES:
            metrics = modes[mode]
            _require(
                isinstance(metrics, Mapping)
                and set(METRIC_DIRECTIONS).issubset(metrics)
                and all(math.isfinite(float(value)) for value in metrics.values()),
                "multiseed_cell_means",
            )
    crossed = payload.get("crossed_seed_case_difference")
    _require(
        isinstance(crossed, Mapping)
        and set(METRIC_DIRECTIONS).issubset(crossed),
        "multiseed_crossed",
    )
    for metric, direction in METRIC_DIRECTIONS.items():
        interval = crossed[metric]
        _require(
            isinstance(interval, Mapping)
            and interval.get("direction") == direction
            and interval.get("replicates") == 10_000
            and interval.get("training_seed_count") == 5
            and interval.get("paired_case_count") == 73
            and len(interval.get("per_seed_point_deltas", [])) == 5
            and all(
                math.isfinite(float(interval.get(key, math.nan)))
                for key in ("point_delta", "ci95_low", "ci95_high")
            ),
            "multiseed_crossed",
        )
    protocols = {
        str(entry["transient_training_protocol_sha256"])
        for entry in manifest["entries"]
    }
    _require(
        len(protocols) == 1
        and payload.get("transient_training_protocol_sha256") == next(iter(protocols)),
        "multiseed_training_protocol",
    )
    expected_hashes: dict[str, str] = {}
    for entry in manifest["entries"]:
        prefix = f"{entry['training_seed']}:{entry['information_mode']}"
        expected_hashes[f"{prefix}:result"] = str(entry["validation_result_sha256"])
        expected_hashes[f"{prefix}:terminal"] = str(entry["terminal_record_sha256"])
    _require(payload.get("terminal_result_sha256") == expected_hashes, "multiseed_inputs")
    directions = payload.get("confirmatory_endpoint_direction")
    _require(
        isinstance(directions, Mapping)
        and set(directions) == set(PRIMARY_CLAIM_ERROR_METRICS)
        and all(value in {"favorable", "unfavorable", "inconclusive"} for value in directions.values()),
        "multiseed_directions",
    )
    return dict(payload)


def _resolved_evidence_path(root: Path, relative: str) -> Path:
    resolved_root = root.resolve()
    candidate = (resolved_root / relative).resolve()
    _require(candidate.is_relative_to(resolved_root), "evidence_path_escape")
    return candidate


def _common_positive_value(values: Sequence[float], label: str) -> float:
    _require(bool(values), f"{label}_missing")
    parsed = [float(value) for value in values]
    _require(
        all(math.isfinite(value) and value > 0.0 for value in parsed),
        f"{label}_invalid",
    )
    common = parsed[0]
    _require(all(value == common for value in parsed), f"{label}_mismatch")
    return common


def _validate_checkpoint_payload(
    checkpoint: Mapping[str, Any], entry: Mapping[str, Any], config: Mapping[str, Any]
) -> None:
    mode = entry["information_mode"]
    _require(
        checkpoint.get("schema_version") == CHECKPOINT_SCHEMA
        and checkpoint.get("protocol_id") == "aneug_release_730_matched_training_v1"
        and checkpoint.get("model_role") == "selected_control"
        and checkpoint.get("information_mode") == mode
        and checkpoint.get("model_family") == "release730_ghd_gps"
        and checkpoint.get("objective_variant") == "field_only"
        and checkpoint.get("selected_response_rank") is None
        and checkpoint.get("training_seed") == entry["training_seed"]
        and checkpoint.get("training_stage") == TRAINING_STAGE
        and checkpoint.get("response_basis_embedded") is False
        and checkpoint.get("public_commit")
        == config["source"]["checkpoint_producer_public_commit"]
        and checkpoint.get("private_runtime_commit")
        == entry["private_runtime_commit"]
        and checkpoint.get("training_config_sha256")
        == config["source"]["matched_training_config_sha256"]
        and checkpoint.get("fresh_information_activation_sha256")
        == entry["fresh_information_activation_sha256"]
        and checkpoint.get("fresh_information_protocol_sha256")
        == entry["fresh_information_protocol_sha256"]
        and checkpoint.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and checkpoint.get("private_train_audit_sha256")
        == config["split"]["private_train_audit_sha256"]
        and checkpoint.get("private_overlap_result_sha256")
        == config["split"]["private_overlap_result_sha256"]
        and checkpoint.get("bound_steady_scale_result_sha256")
        == config["split"]["bound_steady_scale_result_sha256"]
        and checkpoint.get("steady_mesh_audit_result_sha256")
        == config["split"]["steady_mesh_audit_result_sha256"]
        and checkpoint.get("initialization") == "fresh_seeded_initialization"
        and checkpoint.get("old_response_local_selection_gate_used") is False,
        "checkpoint_payload_identity",
    )
    state = checkpoint.get("model_state_dict")
    _require(isinstance(state, Mapping), "checkpoint_payload_values")
    scale_tensors = {
        key: state.get(key)
        for key in ("cycle_output_scale", "single_field_output_scale")
    }
    _require(
        all(
            isinstance(value, torch.Tensor)
            and value.numel() == 1
            and math.isfinite(float(value.item()))
            and float(value.item()) > 0.0
            for value in scale_tensors.values()
        ),
        "checkpoint_payload_values",
    )
    cycle_buffer = float(scale_tensors["cycle_output_scale"].item())
    single_buffer = float(scale_tensors["single_field_output_scale"].item())
    explicit_cycle = checkpoint.get("cycle_output_scale")
    explicit_single = checkpoint.get("single_field_output_scale")
    _require(
        isinstance(checkpoint.get("best_epoch"), int)
        and checkpoint["best_epoch"] > 0
        and math.isfinite(float(checkpoint.get("reference_tawss_floor", math.nan)))
        and float(checkpoint["reference_tawss_floor"]) > 0.0
        and (
            explicit_cycle is None
            or (
                math.isfinite(float(explicit_cycle))
                and float(explicit_cycle) > 0.0
                and math.isclose(
                    float(explicit_cycle), cycle_buffer, rel_tol=1e-6, abs_tol=1e-7
                )
            )
        )
        and math.isfinite(float(explicit_single))
        and float(explicit_single) > 0.0
        and math.isclose(
            float(explicit_single), single_buffer, rel_tol=1e-6, abs_tol=1e-7
        ),
        "checkpoint_payload_values",
    )


def preflight_frozen_evidence(
    manifest: Mapping[str, Any], checkpoint_root: Path, config: Mapping[str, Any]
) -> tuple[float, float]:
    """Verify all ten checkpoint/result/terminal triples before test access."""

    _require(checkpoint_root.is_dir(), "checkpoint_root")
    floors: list[float] = []
    cycle_scales: list[float] = []
    for entry in manifest["entries"]:
        checkpoint_path = _resolved_evidence_path(
            checkpoint_root, str(entry["checkpoint_relative_path"])
        )
        validation_path = _resolved_evidence_path(
            checkpoint_root, str(entry["validation_result_relative_path"])
        )
        terminal_path = _resolved_evidence_path(
            checkpoint_root, str(entry["terminal_record_relative_path"])
        )
        for artifact, digest, label in (
            (checkpoint_path, entry["checkpoint_sha256"], "checkpoint"),
            (validation_path, entry["validation_result_sha256"], "validation_result"),
            (terminal_path, entry["terminal_record_sha256"], "terminal_record"),
        ):
            _require(artifact.is_file(), f"{label}_missing")
            _require(file_sha256(artifact) == digest, f"{label}_hash")
        checkpoint = torch.load(
            str(checkpoint_path), map_location="cpu", weights_only=True
        )
        _require(isinstance(checkpoint, Mapping), "checkpoint_mapping")
        _validate_checkpoint_payload(checkpoint, entry, config)
        floors.append(float(checkpoint["reference_tawss_floor"]))
        cycle_scales.append(
            float(checkpoint["model_state_dict"]["cycle_output_scale"].item())
        )
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        _require(
            validation.get("schema_version") == VALIDATION_SCHEMA
            and validation.get("protocol_id") == VALIDATION_PROTOCOL
            and validation.get("status") == "complete_validation_confirmation"
            and validation.get("model_role") == "selected_control"
            and validation.get("information_mode") == entry["information_mode"]
            and validation.get("model_family") == "release730_ghd_gps"
            and validation.get("objective_variant") == "field_only"
            and validation.get("selected_response_rank") is None
            and validation.get("training_seed") == entry["training_seed"]
            and validation.get("training_stage") == TRAINING_STAGE
            and validation.get("public_commit")
            == config["source"]["checkpoint_producer_public_commit"]
            and validation.get("private_runtime_commit")
            == entry["private_runtime_commit"]
            and validation.get("fresh_information_activation_sha256")
            == entry["fresh_information_activation_sha256"]
            and validation.get("fresh_information_protocol_sha256")
            == entry["fresh_information_protocol_sha256"]
            and validation.get("transient_training_protocol_sha256")
            == entry["transient_training_protocol_sha256"]
            and validation.get("locked_test_field_case_count_read") == 0
            and validation.get("processed_only_extra_field_case_count_read") == 0
            and validation.get("case_ids_included") is False
            and validation.get("paper_result_or_claim") is False,
            "validation_result_identity",
        )
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        _require(
            terminal.get("schema_version") == TERMINAL_SCHEMA
            and terminal.get("protocol_id")
            == "aneug_release_730_ghd_fresh_information_v1"
            and terminal.get("information_mode") == entry["information_mode"]
            and terminal.get("training_seed") == entry["training_seed"]
            and terminal.get("public_commit")
            == config["source"]["checkpoint_producer_public_commit"]
            and terminal.get("private_runtime_commit")
            == entry["private_runtime_commit"]
            and _is_scientifically_terminal_execution(terminal)
            and _is_single_scientific_execution(terminal)
            and terminal.get("result_sha256") == entry["validation_result_sha256"]
            and terminal.get("best_checkpoint_sha256") == entry["checkpoint_sha256"]
            and terminal.get("fresh_information_activation_sha256")
            == entry["fresh_information_activation_sha256"]
            and terminal.get("fresh_information_protocol_sha256")
            == entry["fresh_information_protocol_sha256"]
            and terminal.get("locked_test_field_case_count_read") == 0
            and terminal.get("processed_only_extra_field_case_count_read") == 0
            and terminal.get("case_ids_included") is False
            and terminal.get("paper_result_or_claim") is False,
            "terminal_record_identity",
        )
        del checkpoint
    return (
        _common_positive_value(floors, "reference_tawss_floor"),
        _common_positive_value(cycle_scales, "cycle_output_scale"),
    )


def _load_locked_test_data(
    config: Mapping[str, Any],
    transient_path: Path,
    steady_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    train_audit_public_path: Path,
    train_audit_private_path: Path,
    access_marker_path: Path,
    activation_sha256: str,
    test_loader_order_sha256: str,
) -> tuple[list[dict[str, torch.Tensor]], dict[str, torch.Tensor], float]:
    source = config["source"]
    for path, size, digest, label in (
        (
            transient_path,
            source["processed_v5_bytes"],
            source["processed_v5_sha256"],
            "transient",
        ),
        (
            steady_path,
            source["steady_norm_bytes"],
            source["steady_norm_sha256"],
            "steady",
        ),
        (public_split_path, None, source["public_split_result_sha256"], "public_split"),
        (
            private_split_path,
            None,
            config["split"]["private_manifest_sha256"],
            "private_split",
        ),
        (
            train_audit_public_path,
            None,
            source["public_train_audit_sha256"],
            "audit_public",
        ),
        (
            train_audit_private_path,
            None,
            config["split"]["private_train_audit_sha256"],
            "audit_private",
        ),
    ):
        _require(
            path.is_file() and (size is None or path.stat().st_size == size),
            f"{label}_identity",
        )
        _require(file_sha256(path) == digest, f"{label}_sha256")
    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    audit_public = json.loads(train_audit_public_path.read_text(encoding="utf-8"))
    audit = json.loads(train_audit_private_path.read_text(encoding="utf-8"))
    _require(
        audit_public.get("integrity_pass") is True
        and audit_public.get("test_opened") is False,
        "audit_public",
    )
    _require(
        audit.get("validation_test_or_extra_statistics_included") is False,
        "audit_private",
    )
    buckets = validate_split_evidence(config, public_split, private_split)
    _require(
        _ordered_digest(buckets["test"]) == test_loader_order_sha256,
        "test_loader_order",
    )
    _write_or_validate_access_marker(
        access_marker_path,
        {
            "schema_version": "aurora.private.aneug_release_730_ghd_current_locked_test_access_session.v1",
            "protocol_id": config["protocol_id"],
            "activation_sha256": activation_sha256,
            "access_session_ordinal": 1,
            "locked_test_case_count": 73,
            "test_case_digest": config["split"]["test_case_digest"],
            "test_loader_order_sha256": test_loader_order_sha256,
            "processed_only_extra_read_authorized": False,
            "created_before_steady_or_transient_archive_open": True,
            "exact_same_frozen_batch_retry_only": True,
        },
    )
    steady = safe_torch_load(steady_path, torch)
    _require(
        [str(value) for value in steady["label"]]
        == [
            "x",
            "y",
            "z",
            "x_normal",
            "y_normal",
            "z_normal",
            "wss_x",
            "wss_y",
            "wss_z",
        ],
        "steady_labels",
    )
    decoder_mean = steady["tensor_norm"]["mean"].detach().cpu().to(torch.float32).reshape(-1)
    decoder_std = steady["tensor_norm"]["std"].detach().cpu().to(torch.float32).reshape(-1)
    _require(
        decoder_mean.numel() == decoder_std.numel() == 9
        and bool((decoder_std > 0).all().item()),
        "normalizer",
    )
    del steady
    transient = safe_torch_load(transient_path, torch)
    ordered, indexed = index_case_records(transient["registered_data_list"])
    mesh = transient["mesh_data"]
    mesh_cases = [str(value) for value in mesh["cases"]]
    _require(ordered == mesh_cases and len(ordered) == 809, "processed_order")
    ghd = mesh["ghd"].detach().cpu().to(torch.float32)
    _require(tuple(ghd.shape) == (809, 432) and bool(torch.isfinite(ghd).all().item()), "ghd")
    ghd_by_id = {case_id: ghd[index] for index, case_id in enumerate(mesh_cases)}
    ghd_mean = torch.tensor(audit["ghd"]["mean"], dtype=torch.float32)
    ghd_std = torch.tensor(audit["ghd"]["std_population"], dtype=torch.float32).clamp(min=1e-6)
    wss_mean = torch.tensor(audit["wss_physical"]["mean"], dtype=torch.float64)
    wss_std = torch.tensor(audit["wss_physical"]["std_population"], dtype=torch.float64)
    cycle_output_scale = float(
        torch.sqrt(torch.sum(wss_mean.square() + wss_std.square())).item()
    )
    _require(math.isfinite(cycle_output_scale) and cycle_output_scale > 0.0, "cycle_output_scale")
    topology = _extract_topology(mesh)
    faces = topology["faces"]
    sealed = buckets["train"] + buckets["validation"] + buckets["extra"]
    records = selected_training_records(indexed, buckets["test"], sealed)
    cases = [
        _case_from_record(
            record,
            ghd_by_id[case_id],
            ghd_mean,
            ghd_std,
            decoder_mean,
            decoder_std,
            faces,
        )
        for case_id, record in zip(buckets["test"], records)
    ]
    _require(len(cases) == 73, "test_case_count")
    return cases, topology, cycle_output_scale


def _parse_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, float]]:
    _require(len(rows) == 73, "analysis_case_count")
    parsed: list[dict[str, float]] = []
    for row in rows:
        values = {metric: float(row[metric]) for metric in METRICS}
        _require(all(math.isfinite(value) for value in values.values()), "analysis_finite")
        _require(
            all(values[metric] >= 0.0 for metric in METRICS if metric != "osi_coverage")
            and 0.0 <= values["osi_coverage"] <= 1.0,
            "analysis_range",
        )
        parsed.append(values)
    return parsed


def analyze_locked_test(
    rows_by_seed: Mapping[int, Mapping[str, Sequence[Mapping[str, Any]]]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    _require(set(rows_by_seed) == set(TRAINING_SEEDS), "analysis_seed_grid")
    parsed: dict[int, dict[str, list[dict[str, float]]]] = {}
    for training_seed in TRAINING_SEEDS:
        _require(
            set(rows_by_seed[training_seed]) == set(INFORMATION_MODES),
            "analysis_mode_grid",
        )
        parsed[training_seed] = {
            mode: _parse_rows(rows_by_seed[training_seed][mode])
            for mode in INFORMATION_MODES
        }
    means = {
        str(training_seed): {
            mode: {
                metric: sum(row[metric] for row in parsed[training_seed][mode]) / 73
                for metric in METRICS
            }
            for mode in INFORMATION_MODES
        }
        for training_seed in TRAINING_SEEDS
    }
    crossed: dict[str, Any] = {}
    for metric_index, metric in enumerate(METRICS):
        differences = [
            [
                parsed[training_seed]["eligible_steady"][case_index][metric]
                - parsed[training_seed]["transient_only"][case_index][metric]
                for case_index in range(73)
            ]
            for training_seed in TRAINING_SEEDS
        ]
        crossed[metric] = _crossed_bootstrap(
            differences,
            direction=METRIC_DIRECTIONS[metric],
            replicates=int(config["evaluation"]["bootstrap_replicates"]),
            seed=int(config["evaluation"]["bootstrap_seed"]) + metric_index,
        )
    primary_directions: dict[str, str] = {}
    for metric in PRIMARY_CLAIM_ERROR_METRICS:
        interval = crossed[metric]
        if METRIC_DIRECTIONS[metric] == "lower":
            direction = (
                "favorable"
                if interval["ci95_high"] < 0.0
                else "unfavorable"
                if interval["ci95_low"] > 0.0
                else "inconclusive"
            )
        else:
            direction = (
                "favorable"
                if interval["ci95_low"] > 0.0
                else "unfavorable"
                if interval["ci95_high"] < 0.0
                else "inconclusive"
            )
        primary_directions[metric] = direction
    return {
        "contrast": "eligible_steady_minus_transient_only",
        "cell_means_by_seed": means,
        "crossed_seed_case_difference": crossed,
        "confirmatory_endpoint_direction": primary_directions,
        "primary_claim_error_metrics": list(PRIMARY_CLAIM_ERROR_METRICS),
        "supporting_error_metrics": list(SUPPORTING_ERROR_METRICS),
        "diagnostic_metrics": list(DIAGNOSTIC_METRICS),
        "prediction_valid_coverage_is_gate_or_claim_endpoint": False,
        "absolute_performance_threshold": None,
        "automatic_winner": None,
        "automatic_novelty_conclusion": None,
        "population_inference": False,
    }


def summarize_reference_osi_support(
    cases: Sequence[Mapping[str, torch.Tensor]], reference_tawss_floor: float
) -> dict[str, Any]:
    _require(
        len(cases) == 73
        and math.isfinite(reference_tawss_floor)
        and reference_tawss_floor > 0.0,
        "reference_support_scope",
    )
    fractions: list[float] = []
    for case in cases:
        reference = case["wss"].detach().cpu().to(torch.float64)
        weights = case["vertex_weights"].detach().cpu().to(torch.float64)
        _require(
            reference.ndim == 3
            and reference.shape[0] == 80
            and reference.shape[-1] == 3
            and weights.shape == (reference.shape[1],)
            and bool(torch.isfinite(reference).all().item())
            and bool(torch.isfinite(weights).all().item())
            and bool((weights >= 0.0).all().item())
            and bool((weights.sum() > 0.0).item()),
            "reference_support_values",
        )
        tawss = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0)
        support = tawss > reference_tawss_floor
        fractions.append(float((weights[support].sum() / weights.sum()).item()))
    return {
        "definition": "reference_TAWSS_above_common_train_frozen_floor",
        "reference_tawss_floor": reference_tawss_floor,
        "model_independent": True,
        "area_weighted": True,
        "case_count": 73,
        "per_case_area_fraction_without_identifiers": fractions,
        "case_mean_area_fraction": sum(fractions) / 73,
        "distinct_from_model_specific_prediction_valid_coverage": True,
    }


def build_current_reference_selection(
    cases: Sequence[Mapping[str, torch.Tensor]],
    phase_weights: torch.Tensor,
    reference_tawss_floor: float,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    figure = config["figure"]
    selected = build_reference_selection(
        cases,
        phase_weights,
        case_quantiles=figure["case_quantiles"],
        trace_vertex_quantile=float(figure["trace_vertex_quantile"]),
        expected_case_count=73,
        reference_tawss_floor=reference_tawss_floor,
    )
    return {
        "schema_version": "aurora.aneug_release_730_regime_separated_figure.selection.v1",
        "protocol_id": figure["protocol_id"],
        "selection_role": "reference_only_prediction_blind",
        "selected_locked_test_ordinals": selected["selected_outer_ordinals"],
        "selected_reference_osi_burdens": selected[
            "selected_reference_osi_burdens"
        ],
        "selected_reference_trace_vertex_ordinals": selected[
            "selected_reference_trace_vertex_ordinals"
        ],
        "case_quantiles": selected["case_quantiles"],
        "trace_vertex_quantile": selected["trace_vertex_quantile"],
        "reference_tawss_floor": reference_tawss_floor,
        "reference_tawss_floor_source": "common_frozen_checkpoint_train_only_value",
        "reference_case_count": 73,
        "candidate_or_baseline_values_read": False,
        "processed_only_extra_values_read": False,
        "case_identifiers_included": False,
    }


def _figure_case_payload(
    case: Mapping[str, torch.Tensor],
    faces: torch.Tensor,
    transient_prediction: torch.Tensor,
    steady_prediction: torch.Tensor,
    trace_vertex: int,
    phase_weights: torch.Tensor,
    reference_tawss_floor: float,
) -> dict[str, Any]:
    coordinates = case["coordinates"].detach().cpu().to(torch.float32)
    reference = case["wss"].detach().cpu().to(torch.float32)
    cycles = {
        "reference": reference,
        "transient_only": transient_prediction.detach().cpu().to(torch.float32),
        "eligible_steady": steady_prediction.detach().cpu().to(torch.float32),
    }
    nodes = int(coordinates.shape[0])
    _require(
        coordinates.shape == (nodes, 3)
        and faces.ndim == 2
        and faces.shape[1] == 3
        and 0 <= trace_vertex < nodes
        and all(cycle.shape == (80, nodes, 3) for cycle in cycles.values())
        and all(bool(torch.isfinite(cycle).all().item()) for cycle in cycles.values()),
        "figure_case_shape",
    )
    functionals: dict[str, dict[str, torch.Tensor]] = {}
    for mode, cycle in cycles.items():
        values = compute_cycle_functionals(
            cycle,
            phase_weights,
            torch,
            activity_epsilon=reference_tawss_floor,
        )
        functionals[mode] = {
            "tawss": values["tawss"].detach().cpu(),
            "osi": values["osi"].detach().cpu(),
            "osi_valid": values["osi_valid"].detach().cpu(),
        }
    reference_trace = reference[:, trace_vertex, :]
    anchor_phase = int(
        torch.argmax(torch.linalg.vector_norm(reference_trace, dim=-1)).item()
    )
    direction = reference_trace[anchor_phase]
    norm = torch.linalg.vector_norm(direction)
    _require(bool((norm > 0.0).item()), "figure_trace_anchor")
    direction = direction / norm
    for mode, cycle in cycles.items():
        functionals[mode]["signed_trace"] = torch.sum(
            cycle[:, trace_vertex, :] * direction.reshape(1, 3), dim=-1
        )
    display_mask = torch.ones(nodes, dtype=torch.bool)
    reference_support = functionals["reference"]["osi_valid"]
    _require(bool(reference_support.any().item()), "figure_reference_support")
    return {
        "coordinates": coordinates,
        "faces": faces.detach().cpu().to(torch.int64),
        "display_mask": display_mask,
        "trace_vertex_ordinal": trace_vertex,
        "trace_anchor_phase": anchor_phase,
        "reference_osi_support": reference_support,
        "methods": functionals,
    }


def build_current_figure_payload(
    cases: Sequence[Mapping[str, torch.Tensor]],
    faces: torch.Tensor,
    predictions: Mapping[str, Sequence[torch.Tensor]],
    selection: Mapping[str, Any],
    phase_weights: torch.Tensor,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    _require(set(predictions) == set(INFORMATION_MODES), "figure_prediction_modes")
    ordinals = [int(value) for value in selection["selected_locked_test_ordinals"]]
    traces = [
        int(value)
        for value in selection["selected_reference_trace_vertex_ordinals"]
    ]
    _require(len(ordinals) == len(traces) == 3, "figure_selection_count")
    payload_cases = [
        _figure_case_payload(
            cases[ordinal],
            faces,
            predictions["transient_only"][index],
            predictions["eligible_steady"][index],
            traces[index],
            phase_weights,
            float(selection["reference_tawss_floor"]),
        )
        for index, ordinal in enumerate(ordinals)
    ]
    reference_tawss = torch.cat(
        [case["methods"]["reference"]["tawss"] for case in payload_cases]
    )
    reference_traces = torch.cat(
        [case["methods"]["reference"]["signed_trace"] for case in payload_cases]
    )
    tawss_min = float(reference_tawss.min().item())
    tawss_max = float(reference_tawss.max().item())
    trace_min = float(reference_traces.min().item())
    trace_max = float(reference_traces.max().item())
    _require(tawss_max > tawss_min and trace_max > trace_min, "figure_reference_limits")
    padding = 0.05 * (trace_max - trace_min)
    figure = config["figure"]
    return {
        "schema_version": "aurora.aneug_release_730_regime_separated_figure.render_payload.v1",
        "protocol_id": figure["protocol_id"],
        "display_training_seed": FIGURE_SEED,
        "selection_ordinals": ordinals,
        "case_roles": ["low_reference_OSI", "median_reference_OSI", "high_reference_OSI"],
        "main_case_index": figure["main_case_index"],
        "main_case_role": figure["main_case_role"],
        "method_order": ["reference", "transient_only", "eligible_steady"],
        "method_display_labels": {
            "reference": "Reference",
            "transient_only": "T",
            "eligible_steady": "T+S",
        },
        "method_schematic": figure["method_schematic"],
        "camera": {
            "projection": "orthographic",
            "azimuth_degrees": figure["camera_azimuth_degrees"],
            "elevation_degrees": figure["camera_elevation_degrees"],
        },
        "tawss_limits": [tawss_min, tawss_max],
        "osi_limits": list(figure["osi_limits"]),
        "signed_trace_limits": [trace_min - padding, trace_max + padding],
        "reference_tawss_floor": selection["reference_tawss_floor"],
        "limits_camera_and_selection_are_reference_only": True,
        "steady_head_used_at_inference": False,
        "cases": payload_cases,
        "case_identifiers_included": False,
        "paper_claim": False,
    }


def run_locked_test(
    config: Mapping[str, Any],
    matched_config: Mapping[str, Any],
    activation: Mapping[str, Any],
    manifest: Mapping[str, Any],
    paths: Mapping[str, Path],
    result_path: Path,
    selection_path: Path,
    figure_payload_path: Path,
    access_marker_path: Path,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    torch.set_num_threads(4)
    device = torch.device("cuda")
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    reference_tawss_floor, frozen_cycle_scale = preflight_frozen_evidence(
        manifest, paths["checkpoint_root"], config
    )
    cases, topology, cycle_output_scale = _load_locked_test_data(
        config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
        access_marker_path,
        str(provenance["activation_sha256"]),
        str(activation["test_loader_order_sha256"]),
    )
    _require(
        math.isclose(
            cycle_output_scale, frozen_cycle_scale, rel_tol=1e-6, abs_tol=1e-7
        ),
        "cycle_output_scale_mismatch",
    )
    phase_weights = torch.full((80,), 1.0 / 80.0, dtype=torch.float32)
    selection = build_current_reference_selection(
        cases, phase_weights, reference_tawss_floor, config
    )
    _atomic_private_json(selection_path, selection)
    selected_ordinals = [
        int(value) for value in selection["selected_locked_test_ordinals"]
    ]
    reference_support = summarize_reference_osi_support(cases, reference_tawss_floor)
    entries = {
        (int(entry["training_seed"]), str(entry["information_mode"])): entry
        for entry in manifest["entries"]
    }
    rows_by_seed: dict[int, dict[str, list[dict[str, float]]]] = {}
    cells_by_seed: dict[str, dict[str, Any]] = {}
    figure_predictions: dict[str, list[torch.Tensor]] = {}
    for training_seed in TRAINING_SEEDS:
        rows_by_seed[training_seed] = {}
        cells_by_seed[str(training_seed)] = {}
        for mode in INFORMATION_MODES:
            entry = entries[(training_seed, mode)]
            checkpoint_path = _resolved_evidence_path(
                paths["checkpoint_root"], str(entry["checkpoint_relative_path"])
            )
            checkpoint = torch.load(
                str(checkpoint_path), map_location="cpu", weights_only=True
            )
            _require(isinstance(checkpoint, Mapping), "checkpoint_mapping")
            _validate_checkpoint_payload(checkpoint, entry, config)
            _require(
                float(checkpoint["reference_tawss_floor"]) == reference_tawss_floor
                and float(checkpoint["cycle_output_scale"]) == cycle_output_scale,
                "checkpoint_common_values",
            )
            model_activation = {
                "model_role": "selected_control",
                "information_mode": mode,
                "model_family": "release730_ghd_gps",
                "objective_variant": "field_only",
                "selected_response_rank": None,
            }
            model = build_model(
                matched_config,
                model_activation,
                topology,
                cycle_output_scale,
                float(checkpoint["single_field_output_scale"]),
                None,
            ).to(device)
            model.load_state_dict(checkpoint["model_state_dict"], strict=True)
            evaluated = evaluate(
                model,
                cases,
                matched_config,
                "field_only",
                reference_tawss_floor,
                None,
                device,
            )
            rows = [
                {metric: float(row[metric]) for metric in METRICS}
                for row in evaluated["per_case_without_identifiers"]
            ]
            rows_by_seed[training_seed][mode] = rows
            cells_by_seed[str(training_seed)][mode] = {
                "model_role": "selected_control",
                "information_mode": mode,
                "model_family": "release730_ghd_gps",
                "objective_variant": "field_only",
                "selected_response_rank": None,
                "checkpoint_sha256": entry["checkpoint_sha256"],
                "aggregate": {
                    metric: sum(row[metric] for row in rows) / 73
                    for metric in METRICS
                },
                "per_case_without_identifiers": rows,
            }
            if training_seed == FIGURE_SEED:
                predictions: list[torch.Tensor] = []
                model.eval()
                with torch.no_grad():
                    for ordinal in selected_ordinals:
                        case_on_device = {
                            key: value.to(device=device, non_blocking=True)
                            for key, value in cases[ordinal].items()
                        }
                        predictions.append(
                            model.forward_cycle(case_on_device).detach().cpu()
                        )
                figure_predictions[mode] = predictions
            del model, checkpoint
            torch.cuda.empty_cache()
    _require(set(figure_predictions) == set(INFORMATION_MODES), "figure_predictions")
    figure_payload = build_current_figure_payload(
        cases,
        topology["faces"],
        figure_predictions,
        selection,
        phase_weights,
        config,
    )
    _atomic_private_torch(figure_payload_path, figure_payload)
    result = {
        "schema_version": "aurora.private.aneug_release_730_ghd_current_locked_test_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_one_access_session_frozen_ten_checkpoint_batch",
        "evidence_role": "frozen_five_seed_T_vs_regime_separated_TS_confirmatory_test",
        "access_session_ordinal": 1,
        "locked_test_case_count_read": 73,
        "locked_test_phases_per_case": 80,
        "processed_only_extra_field_case_count_read": 0,
        "training_performed": False,
        "optimizer_or_scheduler_state_changed": False,
        "checkpoint_selection_performed": False,
        "case_identifiers_included": False,
        "test_case_digest": config["split"]["test_case_digest"],
        "test_loader_order_sha256": activation["test_loader_order_sha256"],
        "cells_by_seed": cells_by_seed,
        **analyze_locked_test(rows_by_seed, config),
        "figure_selection": selection,
        "figure_display_training_seed": FIGURE_SEED,
        "figure_control_mode": "transient_only",
        "figure_proposal_mode": "eligible_steady",
        "figure_reference_tawss_floor": reference_tawss_floor,
        "osi_reference_support": reference_support,
        "figure_payload_sha256": file_sha256(figure_payload_path),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "automatic_paper_claim": None,
        **dict(provenance),
    }
    _atomic_private_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--expected-evaluator-commit")
    parser.add_argument("--expected-execution-server", choices=("introai9", "junjinyong"))
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--checkpoint-manifest", type=Path)
    parser.add_argument("--checkpoint-root", type=Path)
    parser.add_argument("--multiseed-validation-result", type=Path)
    parser.add_argument("--matched-training-config", type=Path)
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
    parser.add_argument("--access-marker", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--figure-selection", type=Path)
    parser.add_argument("--figure-payload", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    required = (
        args.expected_evaluator_commit,
        args.expected_execution_server,
        args.activation,
        args.checkpoint_manifest,
        args.checkpoint_root,
        args.multiseed_validation_result,
        args.matched_training_config,
        args.transient,
        args.steady,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.access_marker,
        args.result,
        args.figure_selection,
        args.figure_payload,
    )
    _require(all(value is not None for value in required), "execution_arguments")
    _require(
        file_sha256(args.matched_training_config)
        == config["source"]["matched_training_config_sha256"],
        "matched_training_config_hash",
    )
    module_directory = Path(__file__).resolve().parent
    _require(
        file_sha256(module_directory / "aneug_figure_protocol.py")
        == config["source"]["reference_selection_source_sha256"]
        and file_sha256(module_directory / "cycle_functionals.py")
        == config["source"]["cycle_functionals_source_sha256"],
        "source_dependency_hash",
    )
    activation = validate_activation(
        args.activation, config, str(args.expected_evaluator_commit)
    )
    _require(
        activation["config_sha256"] == file_sha256(args.config)
        and activation["evaluator_source_sha256"] == file_sha256(__file__),
        "activation_source_hash",
    )
    _require(
        activation["execution_server"] == args.expected_execution_server,
        "activation_execution_server",
    )
    manifest = validate_checkpoint_manifest(
        args.checkpoint_manifest,
        str(activation["checkpoint_manifest_sha256"]),
        config,
    )
    _require(
        activation["checkpoint_private_runtime_commit_set_sha256"]
        == manifest["checkpoint_private_runtime_commit_set_sha256"],
        "activation_checkpoint_private_runtime_set",
    )
    validate_multiseed_result(
        args.multiseed_validation_result,
        str(activation["multiseed_validation_result_sha256"]),
        manifest,
    )
    matched_config = load_matched_training_config(args.matched_training_config)
    provenance = {
        "evaluator_public_commit": str(args.expected_evaluator_commit),
        "checkpoint_producer_public_commit": config["source"][
            "checkpoint_producer_public_commit"
        ],
        "checkpoint_private_runtime_binding": config["source"][
            "checkpoint_private_runtime_binding"
        ],
        "checkpoint_private_runtime_commit_set_sha256": activation[
            "checkpoint_private_runtime_commit_set_sha256"
        ],
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "checkpoint_manifest_sha256": activation["checkpoint_manifest_sha256"],
        "multiseed_validation_result_sha256": activation[
            "multiseed_validation_result_sha256"
        ],
        "private_split_manifest_sha256": config["split"][
            "private_manifest_sha256"
        ],
        "private_train_audit_sha256": config["split"][
            "private_train_audit_sha256"
        ],
        "execution_server": activation["execution_server"],
        "execution_queue": activation["queue"],
    }
    run_locked_test(
        config,
        matched_config,
        activation,
        manifest,
        {
            "checkpoint_root": args.checkpoint_root,
            "transient": args.transient,
            "steady": args.steady,
            "public_split": args.public_split,
            "private_split": args.private_split,
            "train_audit_public": args.train_audit_public,
            "train_audit_private": args.train_audit_private,
        },
        args.result,
        args.figure_selection,
        args.figure_payload,
        args.access_marker,
        provenance,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
