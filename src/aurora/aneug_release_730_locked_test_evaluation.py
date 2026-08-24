"""One-time locked-test batch for the frozen release-730 C0 checkpoints.

The executable path is fail-closed behind a private T0 activation and an exact
twenty-checkpoint manifest.  It opens the 73 references once, freezes the
reference-only figure selection before loading any model, evaluates every
seed/cell in the same order, and emits identifier-free metrics plus one compact
three-case figure payload.  It performs no training or checkpoint selection.
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
from aurora.aneug_processed_v4_d9 import _extract_topology
from aurora.aneug_release_730_figure_protocol import (
    build_release730_reference_selection,
    load_config as load_figure_config,
)
from aurora.aneug_release_730_figure_renderer import (
    build_release730_render_payload,
)
from aurora.aneug_release_730_ghd_gps_baseline import _case_from_record
from aurora.aneug_release_730_matched_information_analysis import (
    CELL_ORDER,
    CONFIRMATION_STAGE,
    CONTRASTS,
    DIAGNOSTIC_METRICS,
    METRIC_DIRECTIONS,
    METRICS,
    PRIMARY_CLAIM_ERROR_METRICS,
    SUPPORTING_ERROR_METRICS,
)
from aurora.aneug_release_730_matched_training import (
    CONTROL_FAMILIES,
    PROPOSAL_FAMILY,
    PROPOSAL_OBJECTIVES,
    build_model,
    evaluate,
    load_config as load_matched_training_config,
)
from aurora.aneug_release_730_multiseed_confirmation import (
    FRESH_TRAINING_SEEDS,
    _crossed_bootstrap,
    load_config as load_multiseed_config,
)
from aurora.aneug_release_730_response_local_candidate import load_response_basis
from aurora.aneug_release_730_train_audit import (
    _ordered_digest,
    index_case_records,
    selected_training_records,
    validate_split_evidence,
)


class Release730LockedTestError(RuntimeError):
    """Raised when the one-time T0 boundary is violated."""


FIGURE_SEED = 20_260_903
FIGURE_MODE = "eligible_steady"
EXPECTED_CELLS = tuple(CELL_ORDER)


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730LockedTestError(reason)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
    return digest.hexdigest()


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "json_output_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(dict(payload), handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _strict_atomic_torch(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "torch_output_exists")
    try:
        with temporary.open("xb") as handle:
            torch.save(dict(payload), handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_locked_test_evaluation.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_locked_test_evaluation_v1"
        and config.get("status")
        == "prepared_non_executable_until_frozen_C0_and_private_T0_activation",
        "protocol_status",
    )
    source = config["source"]
    expected_source = {
        "dataset_revision": "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "processed_v5_bytes": 33_233_856_917,
        "processed_v5_sha256": "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
        "steady_norm_bytes": 9_632_510_050,
        "steady_norm_sha256": "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "matched_training_config_sha256": "2da43b08b871cd5ed2fc8d7dfa04d3d4267e7a0c1d8cde4892ac11ea32ef13ea",
        "matched_information_config_sha256": "9632456e59283b951ddeeb6cd40dfe568a5b3e7bb99fdc9a6c8004e624bafe50",
        "multiseed_confirmation_config_sha256": "75cd2e6c5d7545dd56274d7dd1b14d8b07380b0711cf10573d5b9fcaa1b57d92",
        "figure_protocol_config_sha256": "6bae547ab03edfc04979aeb2508d08b4f4488d44696f822d6592a5c51f122d91",
        "figure_protocol_source_sha256": "4d9fdd0fdf73cd14b907d84a6b38019f24fa97723fbc132f4482df3e78951399",
        "figure_renderer_source_sha256": "d15b68ae200002cb059f2c3c0ee9d1b21cd4c29c2ab9efd51ea1d7f26a99a013",
        "public_split_result_sha256": "4fa3be7c217c3a84b86f477c90112377fb913f6b0b47b829d684b270555bf991",
        "public_train_audit_sha256": "3c525820023a56862c6652441c5d00f43412d3c868840149e5f120b8ed2a9587",
    }
    _require(all(source.get(key) == value for key, value in expected_source.items()), "source")
    split = config["split"]
    _require(
        (split["train_cases"], split["validation_cases"], split["locked_test_cases"], split["processed_only_extra_cases"])
        == (584, 73, 73, 79)
        and split["private_manifest_sha256"]
        == "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f"
        and split["private_train_audit_sha256"]
        == "ce1dd6d2852e290fbe187ac062af155f522cd4b8a82c1580b5430d15ed519385"
        and split["train_case_digest"]
        == "a23bbda2d74d218e4e77c8e446f54a60ebbed45b906a9acb544988e8bba31aaa"
        and split["validation_case_digest"]
        == "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024"
        and split["test_case_digest"]
        == "1f87f52fc4b819548aebcc6df77f90830d475d1e92df0ca833980347d792aa56"
        and split["test_loader_order_sha256"] is None
        and split["test_loader_order_source"]
        == "required_from_fresh_private_T0_activation"
        and split["all_80_phases_follow_geometry"] is True
        and split["read_train_or_validation_fields"] is False
        and split["read_locked_test_fields_only_after_access_marker"] is True
        and split["read_processed_only_extra_fields"] is False,
        "split",
    )
    frozen = config["frozen_checkpoints"]
    _require(
        tuple(frozen["training_seeds"]) == FRESH_TRAINING_SEEDS
        and tuple(frozen["cells_per_seed"]) == EXPECTED_CELLS
        and frozen["checkpoint_count"] == 20
        and frozen["manifest_required"] is True
        and frozen["checkpoint_sha256_required"] is True
        and frozen["validation_result_sha256_required"] is True
        and frozen["terminal_record_sha256_required"] is True
        and frozen["all_frozen_before_test"] is True
        and frozen["training_or_checkpoint_selection_in_T0"] is False,
        "frozen_checkpoints",
    )
    evaluation = config["evaluation"]
    _require(
        tuple(evaluation["metrics"]) == METRICS
        and tuple(evaluation["primary_claim_error_metrics"])
        == PRIMARY_CLAIM_ERROR_METRICS
        and tuple(evaluation["supporting_error_metrics"])
        == SUPPORTING_ERROR_METRICS
        and tuple(evaluation["diagnostic_metrics"]) == DIAGNOSTIC_METRICS
        and tuple(evaluation["contrasts"]) == tuple(CONTRASTS)
        and evaluation["bootstrap_replicates"] == 10_000
        and evaluation["bootstrap_seed"] == 20_260_824
        and evaluation["prediction_valid_coverage_is_gate_or_claim_endpoint"] is False
        and evaluation["absolute_performance_threshold"] is None
        and evaluation["automatic_winner"] is False
        and evaluation["automatic_novelty_conclusion"] is False
        and evaluation["population_inference"] is False,
        "evaluation",
    )
    figure = config["figure"]
    _require(
        figure["protocol_id"] == "aneug_release_730_confirmatory_figure_v1"
        and figure["reference_only_selection_before_any_prediction"] is True
        and figure["case_quantiles"] == [0.1, 0.5, 0.9]
        and figure["trace_vertex_quantile"] == 0.9
        and figure["display_information_mode"] == FIGURE_MODE
        and figure["display_training_seed"] == FIGURE_SEED
        and figure["seed_selected_from_test_outcomes"] is False
        and figure["selected_case_count"] == 3
        and figure["compact_payload_only"] is True
        and figure["case_identifiers_in_payload"] is False,
        "figure",
    )
    runtime = config["runtime"]
    _require(
        runtime["server"] == "introai9"
        and runtime["excluded_server"] == "junjinyong"
        and (runtime["ncpus"], runtime["memory_gb"], runtime["ngpus"])
        == (4, 64, 1)
        and runtime["maximum_gpu_jobs"] == 1
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        "runtime",
    )
    authorization = config["authorization"]
    _require(
        authorization["execute_now"] is False
        and authorization["requires_fresh_private_T0_activation"] is True
        and authorization["requires_complete_multiseed_confirmation_result"] is True
        and authorization["requires_exact_twenty_checkpoint_manifest"] is True
        and authorization["requires_one_time_access_marker"] is True
        and authorization["locked_test_attempts"] == 1
        and authorization["training"] is False
        and authorization["optimizer_or_scheduler_state_change"] is False
        and authorization["post_test_model_loss_seed_threshold_endpoint_or_figure_selection_change"] is False
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
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_locked_test_activation.v1"
        and activation.get("protocol_id") == config["protocol_id"]
        and activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success"
        and activation.get("authorized_stage")
        == "one_time_locked_test_evaluation_of_frozen_C0"
        and activation.get("locked_test_attempt_ordinal") == 1
        and activation.get("created_before_locked_test_read") is True
        and activation.get("prior_locked_test_access_marker_sha256") is None,
        "activation_identity",
    )
    for key in (
        "checkpoint_manifest_sha256",
        "multiseed_confirmation_result_sha256",
        "selected_model_decision_record_sha256",
        "response_basis_sha256",
    ):
        _require(_is_sha256(activation.get(key)), f"activation_{key}")
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["split"]["private_train_audit_sha256"]
        and activation.get("test_case_digest")
        == config["split"]["test_case_digest"]
        and _is_sha256(activation.get("test_loader_order_sha256"))
        and activation.get("checkpoint_count") == 20
        and activation.get("training") is False
        and activation.get("read_locked_test") is True
        and activation.get("read_processed_only_extra") is False
        and activation.get("post_test_repair_or_rerun") is False,
        "activation_scope",
    )
    return dict(activation)


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def _expected_role_mode(cell: str) -> tuple[str, str]:
    _require(cell in EXPECTED_CELLS, "cell")
    return (
        "selected_control" if cell.startswith("control_") else "selected_proposal",
        "eligible_steady" if cell.endswith("TS") else "transient_only",
    )


def validate_checkpoint_manifest(
    path: str | Path, expected_sha256: str, config: Mapping[str, Any]
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "checkpoint_manifest_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_frozen_C0_checkpoints.v1"
        and payload.get("status") == "complete_frozen_before_locked_test"
        and payload.get("checkpoint_count") == 20
        and payload.get("training_seed_count") == 5
        and payload.get("all_checkpoints_frozen_before_test") is True
        and payload.get("locked_test_or_extra_used_for_selection") is False
        and payload.get("case_identifiers_included") is False,
        "checkpoint_manifest_scope",
    )
    entries = payload.get("entries")
    _require(isinstance(entries, list) and len(entries) == 20, "checkpoint_entries")
    expected_pairs = {(seed, cell) for seed in FRESH_TRAINING_SEEDS for cell in EXPECTED_CELLS}
    observed_pairs: set[tuple[int, str]] = set()
    paths: set[str] = set()
    identities: dict[str, set[tuple[Any, Any, Any]]] = {
        "selected_control": set(),
        "selected_proposal": set(),
    }
    protocol_digests: dict[str, set[str]] = {
        "selected_control": set(),
        "selected_proposal": set(),
    }
    for entry in entries:
        _require(isinstance(entry, Mapping), "checkpoint_entry")
        seed = entry.get("training_seed")
        cell = entry.get("cell")
        _require(isinstance(seed, int) and cell in EXPECTED_CELLS, "checkpoint_pair")
        role, mode = _expected_role_mode(str(cell))
        _require(
            entry.get("model_role") == role
            and entry.get("information_mode") == mode
            and entry.get("training_stage") == CONFIRMATION_STAGE,
            "checkpoint_cell_identity",
        )
        family = entry.get("model_family")
        objective = entry.get("objective_variant")
        rank = entry.get("selected_response_rank")
        if role == "selected_control":
            _require(family in CONTROL_FAMILIES and objective == "field_only" and rank is None, "checkpoint_control")
        else:
            _require(family == PROPOSAL_FAMILY and objective in PROPOSAL_OBJECTIVES and rank in (16, 32, 64, 128, 256), "checkpoint_proposal")
        relative = entry.get("checkpoint_relative_path")
        _require(_safe_relative_path(relative), "checkpoint_relative_path")
        for key in (
            "checkpoint_sha256",
            "validation_result_sha256",
            "terminal_record_sha256",
            "training_activation_sha256",
            "transient_training_protocol_sha256",
        ):
            _require(_is_sha256(entry.get(key)), f"checkpoint_{key}")
        for key in (
            "validation_result_relative_path",
            "terminal_record_relative_path",
        ):
            _require(_safe_relative_path(entry.get(key)), f"checkpoint_{key}")
        pair = (int(seed), str(cell))
        _require(pair not in observed_pairs and relative not in paths, "checkpoint_duplicate")
        observed_pairs.add(pair)
        paths.add(str(relative))
        identities[role].add((family, objective, rank))
        protocol_digests[role].add(str(entry["transient_training_protocol_sha256"]))
    _require(observed_pairs == expected_pairs, "checkpoint_grid")
    _require(all(len(values) == 1 for values in identities.values()), "checkpoint_cross_seed_identity")
    _require(
        all(len(values) == 1 for values in protocol_digests.values()),
        "checkpoint_cross_seed_protocol",
    )
    figure = payload.get("figure_display")
    _require(
        isinstance(figure, Mapping)
        and figure.get("training_seed") == FIGURE_SEED
        and figure.get("information_mode") == FIGURE_MODE
        and figure.get("control_cell") == "control_TS"
        and figure.get("proposal_cell") == "proposal_TS"
        and figure.get("selected_before_locked_test") is True,
        "checkpoint_figure_display",
    )
    return dict(payload)


def validate_multiseed_result(
    path: str | Path, expected_sha256: str, multiseed_config: Mapping[str, Any]
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "multiseed_result_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_multiseed_confirmation_result.v1"
        and payload.get("protocol_id") == multiseed_config["protocol_id"]
        and payload.get("status") == "complete_validation_confirmation"
        and tuple(payload.get("fresh_training_seeds", [])) == FRESH_TRAINING_SEEDS
        and payload.get("training_seed_count") == 5
        and payload.get("paired_case_count") == 73
        and tuple(payload.get("primary_claim_error_metrics", []))
        == PRIMARY_CLAIM_ERROR_METRICS
        and tuple(payload.get("supporting_error_metrics", []))
        == SUPPORTING_ERROR_METRICS
        and tuple(payload.get("diagnostic_metrics", [])) == DIAGNOSTIC_METRICS
        and payload.get("prediction_valid_coverage_is_gate_or_claim_endpoint") is False
        and payload.get("locked_test_or_extra_values_read") is False
        and payload.get("case_identifiers_included") is False
        and payload.get("automatic_test_authorization") is None
        and payload.get("paper_performance_claim") is False,
        "multiseed_result_scope",
    )
    return dict(payload)


def validate_selection_record(path: str | Path, expected_sha256: str) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "selection_record_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version") == "aurora.private.aneug_release_730_selected_models.v1"
        and payload.get("status") == "complete_validation_only_selection"
        and payload.get("locked_test_or_79_extra_used") is False
        and payload.get("absolute_performance_threshold") is None,
        "selection_record_scope",
    )
    return dict(payload)


def validate_frozen_identity_alignment(
    manifest: Mapping[str, Any],
    multiseed_result: Mapping[str, Any],
    selection: Mapping[str, Any],
    response_basis_sha256: str,
) -> None:
    entries = manifest["entries"]
    by_role = {
        role: {
            (
                entry["model_family"],
                entry["objective_variant"],
                entry["selected_response_rank"],
            )
            for entry in entries
            if entry["model_role"] == role
        }
        for role in ("selected_control", "selected_proposal")
    }
    _require(all(len(values) == 1 for values in by_role.values()), "aligned_manifest_identity")
    control = next(iter(by_role["selected_control"]))
    proposal = next(iter(by_role["selected_proposal"]))
    _require(
        control
        == (selection.get("selected_control_family"), "field_only", None)
        and proposal
        == (
            selection.get("selected_proposal_family"),
            selection.get("selected_proposal_objective"),
            selection.get("selected_proposal_rank"),
        )
        and selection.get("selected_response_basis_sha256")
        == response_basis_sha256,
        "aligned_selection_identity",
    )
    expected = multiseed_result.get("selected_model_identity_by_role")
    _require(isinstance(expected, Mapping), "aligned_multiseed_identity")
    for role, identity in (
        ("selected_control", control),
        ("selected_proposal", proposal),
    ):
        observed = expected.get(role)
        _require(
            isinstance(observed, Mapping)
            and (
                observed.get("model_family"),
                observed.get("objective_variant"),
                observed.get("selected_response_rank"),
            )
            == identity,
            "aligned_multiseed_identity",
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
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (steady_path, source["steady_norm_bytes"], source["steady_norm_sha256"], "steady"),
        (public_split_path, None, source["public_split_result_sha256"], "public_split"),
        (private_split_path, None, config["split"]["private_manifest_sha256"], "private_split"),
        (train_audit_public_path, None, source["public_train_audit_sha256"], "audit_public"),
        (train_audit_private_path, None, config["split"]["private_train_audit_sha256"], "audit_private"),
    ):
        _require(path.is_file() and (size is None or path.stat().st_size == size), f"{label}_identity")
        _require(file_sha256(path) == digest, f"{label}_sha256")
    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    audit_public = json.loads(train_audit_public_path.read_text(encoding="utf-8"))
    audit = json.loads(train_audit_private_path.read_text(encoding="utf-8"))
    _require(audit_public.get("integrity_pass") is True and audit_public.get("test_opened") is False, "audit_public")
    _require(audit.get("validation_test_or_extra_statistics_included") is False, "audit_private")
    buckets = validate_split_evidence(config, public_split, private_split)
    _require(
        _ordered_digest(buckets["test"]) == test_loader_order_sha256,
        "test_loader_order",
    )
    _strict_atomic_json(
        access_marker_path,
        {
            "schema_version": "aurora.private.aneug_release_730_locked_test_access_marker.v1",
            "protocol_id": config["protocol_id"],
            "activation_sha256": activation_sha256,
            "locked_test_attempt_ordinal": 1,
            "locked_test_case_count": 73,
            "test_case_digest": config["split"]["test_case_digest"],
            "test_loader_order_sha256": test_loader_order_sha256,
            "processed_only_extra_read_authorized": False,
            "created_before_transient_archive_open": True,
        },
    )
    steady = safe_torch_load(steady_path, torch)
    _require(
        [str(value) for value in steady["label"]]
        == ["x", "y", "z", "x_normal", "y_normal", "z_normal", "wss_x", "wss_y", "wss_z"],
        "steady_labels",
    )
    decoder_mean = steady["tensor_norm"]["mean"].detach().cpu().to(torch.float32).reshape(-1)
    decoder_std = steady["tensor_norm"]["std"].detach().cpu().to(torch.float32).reshape(-1)
    _require(decoder_mean.numel() == decoder_std.numel() == 9 and bool((decoder_std > 0).all().item()), "normalizer")
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
    cycle_output_scale = float(torch.sqrt(torch.sum(wss_mean.square() + wss_std.square())).item())
    _require(math.isfinite(cycle_output_scale) and cycle_output_scale > 0.0, "cycle_output_scale")
    topology = _extract_topology(mesh)
    faces = topology["faces"]
    sealed = buckets["train"] + buckets["validation"] + buckets["extra"]
    records = selected_training_records(indexed, buckets["test"], sealed)
    cases = [
        _case_from_record(record, ghd_by_id[case_id], ghd_mean, ghd_std, decoder_mean, decoder_std, faces)
        for case_id, record in zip(buckets["test"], records)
    ]
    _require(len(cases) == 73, "test_case_count")
    return cases, topology, cycle_output_scale


def _validate_checkpoint_payload(
    payload: Mapping[str, Any], entry: Mapping[str, Any], config: Mapping[str, Any]
) -> None:
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_matched_training_best.v1"
        and payload.get("protocol_id") == "aneug_release_730_matched_training_v1"
        and payload.get("model_role") == entry["model_role"]
        and payload.get("information_mode") == entry["information_mode"]
        and payload.get("model_family") == entry["model_family"]
        and payload.get("objective_variant") == entry["objective_variant"]
        and payload.get("selected_response_rank") == entry["selected_response_rank"]
        and payload.get("training_seed") == entry["training_seed"]
        and payload.get("training_stage") == CONFIRMATION_STAGE
        and payload.get("response_basis_embedded") is False
        and payload.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and payload.get("training_config_sha256")
        == config["source"]["matched_training_config_sha256"]
        and payload.get("multiseed_confirmation_config_sha256")
        == config["source"]["multiseed_confirmation_config_sha256"]
        and payload.get("activation_sha256") == entry["training_activation_sha256"],
        "checkpoint_payload_identity",
    )
    _require(
        isinstance(payload.get("model_state_dict"), Mapping)
        and payload.get("best_epoch", 0) > 0
        and math.isfinite(float(payload.get("reference_tawss_floor", math.nan)))
        and float(payload["reference_tawss_floor"]) > 0.0
        and math.isfinite(float(payload.get("single_field_output_scale", math.nan)))
        and float(payload["single_field_output_scale"]) > 0.0,
        "checkpoint_payload_values",
    )


def _resolved_evidence_path(root: Path, relative: str) -> Path:
    resolved_root = root.resolve()
    candidate = (resolved_root / relative).resolve()
    _require(candidate.is_relative_to(resolved_root), "evidence_path_escape")
    return candidate


def preflight_frozen_evidence(
    manifest: Mapping[str, Any], checkpoint_root: Path, config: Mapping[str, Any]
) -> None:
    """Verify every frozen C0 artifact before the one-time test marker exists."""

    _require(checkpoint_root.is_dir(), "checkpoint_root")
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
        for path, digest, label in (
            (checkpoint_path, entry["checkpoint_sha256"], "checkpoint"),
            (validation_path, entry["validation_result_sha256"], "validation_result"),
            (terminal_path, entry["terminal_record_sha256"], "terminal_record"),
        ):
            _require(path.is_file(), f"{label}_missing")
            _require(file_sha256(path) == digest, f"{label}_hash")
        checkpoint = torch.load(
            str(checkpoint_path), map_location="cpu", weights_only=True
        )
        _require(isinstance(checkpoint, Mapping), "checkpoint_mapping")
        _validate_checkpoint_payload(checkpoint, entry, config)
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        _require(
            validation.get("schema_version")
            == "aurora.aneug_release_730_matched_information_cell.v1"
            and validation.get("status") == "complete_validation_confirmation"
            and validation.get("model_role") == entry["model_role"]
            and validation.get("information_mode") == entry["information_mode"]
            and validation.get("model_family") == entry["model_family"]
            and validation.get("objective_variant") == entry["objective_variant"]
            and validation.get("selected_response_rank")
            == entry["selected_response_rank"]
            and validation.get("training_seed") == entry["training_seed"]
            and validation.get("training_stage") == CONFIRMATION_STAGE
            and validation.get("activation_sha256")
            == entry["training_activation_sha256"]
            and validation.get("locked_test_field_case_count_read") == 0
            and validation.get("processed_only_extra_field_case_count_read") == 0
            and validation.get("case_ids_included") is False,
            "validation_result_identity",
        )
        _require(
            terminal.get("exit_code") == 0 and terminal.get("complete") is True,
            "terminal_record_incomplete",
        )
        del checkpoint
def analyze_locked_test(
    rows_by_seed: Mapping[int, Mapping[str, Sequence[Mapping[str, float]]]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Report the frozen crossed seed/case estimand without selecting a winner."""

    _require(set(rows_by_seed) == set(FRESH_TRAINING_SEEDS), "analysis_seed_grid")
    parsed: dict[int, dict[str, list[dict[str, float]]]] = {}
    for seed in FRESH_TRAINING_SEEDS:
        _require(set(rows_by_seed[seed]) == set(EXPECTED_CELLS), "analysis_cell_grid")
        parsed[seed] = {}
        for cell in EXPECTED_CELLS:
            rows = rows_by_seed[seed][cell]
            _require(len(rows) == 73, "analysis_case_count")
            parsed_rows: list[dict[str, float]] = []
            for row in rows:
                values = {metric: float(row[metric]) for metric in METRICS}
                _require(all(math.isfinite(value) for value in values.values()), "analysis_finite")
                _require(all(values[metric] >= 0.0 for metric in METRICS if metric != "osi_coverage"), "analysis_nonnegative")
                _require(0.0 <= values["osi_coverage"] <= 1.0, "analysis_coverage")
                parsed_rows.append(values)
            parsed[seed][cell] = parsed_rows
    cell_means_by_seed = {
        str(seed): {
            cell: {
                metric: sum(row[metric] for row in parsed[seed][cell]) / 73
                for metric in METRICS
            }
            for cell in EXPECTED_CELLS
        }
        for seed in FRESH_TRAINING_SEEDS
    }
    contrasts: dict[str, dict[str, Any]] = {}
    for contrast_index, (contrast, coefficients) in enumerate(CONTRASTS.items()):
        contrasts[contrast] = {}
        for metric_index, metric in enumerate(METRICS):
            values_by_seed = [
                [
                    sum(
                        coefficient * parsed[seed][cell][case_index][metric]
                        for cell, coefficient in coefficients.items()
                    )
                    for case_index in range(73)
                ]
                for seed in FRESH_TRAINING_SEEDS
            ]
            result = _crossed_bootstrap(
                values_by_seed,
                direction=METRIC_DIRECTIONS[metric],
                replicates=int(config["evaluation"]["bootstrap_replicates"]),
                seed=int(config["evaluation"]["bootstrap_seed"])
                + contrast_index * 10_007
                + metric_index,
            )
            result.update({"metric": metric, "coefficients": dict(coefficients)})
            contrasts[contrast][metric] = result
    return {
        "cell_means_by_seed": cell_means_by_seed,
        "crossed_seed_case_contrasts": contrasts,
        "primary_claim_error_metrics": list(PRIMARY_CLAIM_ERROR_METRICS),
        "supporting_error_metrics": list(SUPPORTING_ERROR_METRICS),
        "diagnostic_metrics": list(DIAGNOSTIC_METRICS),
        "prediction_valid_coverage_is_gate_or_claim_endpoint": False,
        "registered_joint_claim_rule": "upper_95pct_endpoint_below_zero_for_field_TAWSS_and_OSI_proposal_minus_control_within_information_mode",
        "automatic_winner": None,
        "automatic_novelty_conclusion": None,
        "population_inference": False,
    }


def run_locked_test(
    config: Mapping[str, Any],
    matched_config: Mapping[str, Any],
    figure_config: Mapping[str, Any],
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
    preflight_frozen_evidence(manifest, paths["checkpoint_root"], config)
    basis_payload = load_response_basis(
        paths["response_basis"], activation["response_basis_sha256"], matched_config
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
        provenance["activation_sha256"],
        str(activation["test_loader_order_sha256"]),
    )
    phase_weights = torch.full((80,), 1.0 / 80.0, dtype=torch.float32)
    selection = build_release730_reference_selection(cases, phase_weights, figure_config)
    _strict_atomic_json(selection_path, selection)
    selected_ordinals = [int(value) for value in selection["selected_locked_test_ordinals"]]
    entries = {
        (int(entry["training_seed"]), str(entry["cell"])): entry
        for entry in manifest["entries"]
    }
    rows_by_seed: dict[int, dict[str, list[dict[str, float]]]] = {}
    cell_outputs: dict[str, dict[str, Any]] = {}
    figure_predictions: dict[str, list[torch.Tensor]] = {}
    for seed in FRESH_TRAINING_SEEDS:
        rows_by_seed[seed] = {}
        cell_outputs[str(seed)] = {}
        for cell in EXPECTED_CELLS:
            entry = entries[(seed, cell)]
            checkpoint_path = _resolved_evidence_path(
                paths["checkpoint_root"], str(entry["checkpoint_relative_path"])
            )
            _require(checkpoint_path.is_file(), "checkpoint_missing")
            _require(file_sha256(checkpoint_path) == entry["checkpoint_sha256"], "checkpoint_hash")
            checkpoint = torch.load(str(checkpoint_path), map_location="cpu", weights_only=True)
            _require(isinstance(checkpoint, Mapping), "checkpoint_mapping")
            _validate_checkpoint_payload(checkpoint, entry, config)
            model_activation = {
                "model_role": entry["model_role"],
                "model_family": entry["model_family"],
                "objective_variant": entry["objective_variant"],
                "selected_response_rank": entry["selected_response_rank"],
            }
            model = build_model(
                matched_config,
                model_activation,
                topology,
                cycle_output_scale,
                float(checkpoint["single_field_output_scale"]),
                basis_payload if entry["model_role"] == "selected_proposal" else None,
            ).to(device)
            model.load_state_dict(checkpoint["model_state_dict"], strict=True)
            evaluated = evaluate(
                model,
                cases,
                matched_config,
                str(entry["objective_variant"]),
                float(checkpoint["reference_tawss_floor"]),
                None,
                device,
            )
            rows = [
                {metric: float(row[metric]) for metric in METRICS}
                for row in evaluated["per_case_without_identifiers"]
            ]
            rows_by_seed[seed][cell] = rows
            cell_outputs[str(seed)][cell] = {
                "model_role": entry["model_role"],
                "information_mode": entry["information_mode"],
                "model_family": entry["model_family"],
                "objective_variant": entry["objective_variant"],
                "selected_response_rank": entry["selected_response_rank"],
                "checkpoint_sha256": entry["checkpoint_sha256"],
                "aggregate": {
                    metric: sum(row[metric] for row in rows) / 73 for metric in METRICS
                },
                "per_case_without_identifiers": rows,
            }
            if seed == FIGURE_SEED and cell in ("control_TS", "proposal_TS"):
                predictions: list[torch.Tensor] = []
                model.eval()
                with torch.no_grad():
                    for ordinal in selected_ordinals:
                        case_on_device = {
                            key: value.to(device=device, non_blocking=True)
                            for key, value in cases[ordinal].items()
                        }
                        predictions.append(model.forward_cycle(case_on_device).detach().cpu())
                figure_predictions[cell] = predictions
            del model, checkpoint
            torch.cuda.empty_cache()
    _require(set(figure_predictions) == {"control_TS", "proposal_TS"}, "figure_predictions")
    figure_cases = []
    faces = topology["faces"].detach().cpu().to(torch.int64)
    for index, ordinal in enumerate(selected_ordinals):
        reference = cases[ordinal]
        figure_cases.append(
            {
                "coordinates": reference["coordinates"],
                "faces": faces,
                "display_mask": torch.ones(reference["coordinates"].shape[0], dtype=torch.bool),
                "reference_wss": reference["wss"],
                "selected_control_wss": figure_predictions["control_TS"][index],
                "proposal_wss": figure_predictions["proposal_TS"][index],
            }
        )
    render_payload = build_release730_render_payload(
        figure_cases, selection, phase_weights, figure_config
    )
    _strict_atomic_torch(figure_payload_path, render_payload)
    analysis = analyze_locked_test(rows_by_seed, config)
    result = {
        "schema_version": "aurora.private.aneug_release_730_locked_test_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_one_time_locked_test_batch",
        "evidence_role": "frozen_five_seed_four_cell_confirmatory_test",
        "locked_test_attempt_ordinal": 1,
        "locked_test_case_count_read": 73,
        "locked_test_phases_per_case": 80,
        "processed_only_extra_field_case_count_read": 0,
        "training_performed": False,
        "optimizer_or_scheduler_state_changed": False,
        "checkpoint_selection_performed": False,
        "case_identifiers_included": False,
        "test_case_digest": config["split"]["test_case_digest"],
        "test_loader_order_sha256": activation["test_loader_order_sha256"],
        "cells_by_seed": cell_outputs,
        **analysis,
        "figure_selection": selection,
        "figure_display_training_seed": FIGURE_SEED,
        "figure_display_information_mode": FIGURE_MODE,
        "figure_payload_sha256": file_sha256(figure_payload_path),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "automatic_paper_claim": None,
        **dict(provenance),
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--expected-commit")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--checkpoint-manifest", type=Path)
    parser.add_argument("--checkpoint-root", type=Path)
    parser.add_argument("--multiseed-confirmation-result", type=Path)
    parser.add_argument("--selected-model-record", type=Path)
    parser.add_argument("--matched-training-config", type=Path)
    parser.add_argument("--matched-information-config", type=Path)
    parser.add_argument("--multiseed-config", type=Path)
    parser.add_argument("--figure-config", type=Path)
    parser.add_argument("--response-basis", type=Path)
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
        args.expected_commit,
        args.activation,
        args.checkpoint_manifest,
        args.checkpoint_root,
        args.multiseed_confirmation_result,
        args.selected_model_record,
        args.matched_training_config,
        args.matched_information_config,
        args.multiseed_config,
        args.figure_config,
        args.response_basis,
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
    for path, expected, label in (
        (args.matched_training_config, config["source"]["matched_training_config_sha256"], "matched_training_config"),
        (args.matched_information_config, config["source"]["matched_information_config_sha256"], "matched_information_config"),
        (args.multiseed_config, config["source"]["multiseed_confirmation_config_sha256"], "multiseed_config"),
        (args.figure_config, config["source"]["figure_protocol_config_sha256"], "figure_config"),
    ):
        _require(file_sha256(path) == expected, f"{label}_hash")
    module_directory = Path(__file__).resolve().parent
    _require(
        file_sha256(module_directory / "aneug_release_730_figure_protocol.py")
        == config["source"]["figure_protocol_source_sha256"],
        "figure_protocol_source_hash",
    )
    _require(
        file_sha256(module_directory / "aneug_release_730_figure_renderer.py")
        == config["source"]["figure_renderer_source_sha256"],
        "figure_renderer_source_hash",
    )
    matched_config = load_matched_training_config(args.matched_training_config)
    multiseed_config = load_multiseed_config(args.multiseed_config)
    figure_config = load_figure_config(args.figure_config)
    activation = validate_activation(args.activation, config, str(args.expected_commit))
    manifest = validate_checkpoint_manifest(
        args.checkpoint_manifest, activation["checkpoint_manifest_sha256"], config
    )
    multiseed_result = validate_multiseed_result(
        args.multiseed_confirmation_result,
        activation["multiseed_confirmation_result_sha256"],
        multiseed_config,
    )
    selection_record = validate_selection_record(
        args.selected_model_record,
        activation["selected_model_decision_record_sha256"],
    )
    _require(file_sha256(args.response_basis) == activation["response_basis_sha256"], "response_basis_hash")
    validate_frozen_identity_alignment(
        manifest,
        multiseed_result,
        selection_record,
        activation["response_basis_sha256"],
    )
    provenance = {
        "public_commit": str(args.expected_commit),
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "checkpoint_manifest_sha256": activation["checkpoint_manifest_sha256"],
        "multiseed_confirmation_result_sha256": activation["multiseed_confirmation_result_sha256"],
        "selected_model_decision_record_sha256": activation["selected_model_decision_record_sha256"],
        "response_basis_sha256": activation["response_basis_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["private_train_audit_sha256"],
        "figure_protocol_config_sha256": config["source"]["figure_protocol_config_sha256"],
    }
    run_locked_test(
        config,
        matched_config,
        figure_config,
        activation,
        manifest,
        {
            "checkpoint_root": args.checkpoint_root,
            "response_basis": args.response_basis,
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
