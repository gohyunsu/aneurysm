"""Symmetric T/T+S training and T+M attribution for release-730 models.

One activation executes one cell of the selected-control/proposal by
transient-only/eligible-steady factorial. Eligible-steady cells add exactly
one leakage-audited single-field example per transient training case using the
common deterministic exposure stream. A separate single-seed transient-mean
mode uses a second pass over the same train case to attribute the auxiliary
head/pass without reading steady WSS. Test and processed-only rows have no
runner input and are never indexed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d13c_functional_finetune import (
    LOSS_TERMS,
    backward_case,
    train_wss_rms,
    validation_utility,
)
from aurora.aneug_processed_v4_d9 import field_loss, model_parameter_count
from aurora.aneug_release_730_ghd_gps_baseline import (
    Release730GHDGPSUNet,
    _to_device,
    extended_case_metrics,
    load_development_data,
)
from aurora.aneug_release_730_matched_steady_stream import (
    ExposureDigest,
    MatchedSteadyStream,
    epoch_exposure_indices,
    single_field_relative_squared_error,
)
from aurora.aneug_release_730_response_local_candidate import (
    _selection_normalizers,
    _valid_support_osi,
    alignment_terms,
    load_response_basis,
)
from aurora.aneug_release_730_single_field_auxiliary import (
    SharedEncoderSingleFieldAdapter,
    train_cycle_mean_wss_rms,
    transient_mean_auxiliary_case,
)
from aurora.aneug_release_730_steady_exposure_schedule import (
    load_config as load_exposure_config,
)
from aurora.aneug_release_730_steady_training_scope import (
    load_config as load_scope_config,
    load_scope_files,
)
from aurora.aneug_release_730_transolver_baseline import (
    Release730FullCycleTransolver,
)
from aurora.cycle_response_residual import SharedEncoderCycleResponseResidual
from aurora.release730_training_continuation import (
    capture_rng_state,
    validate_interrupted_attempt_record,
)


MODEL_ROLES = ("selected_control", "selected_proposal")
FACTORIAL_INFORMATION_MODES = ("transient_only", "eligible_steady")
INFORMATION_MODES = (*FACTORIAL_INFORMATION_MODES, "transient_mean")
AUXILIARY_INFORMATION_MODES = ("eligible_steady", "transient_mean")
CONTROL_FAMILIES = ("release730_ghd_gps", "release730_transolver")
PROPOSAL_FAMILY = "release730_response_plus_local_residual"
PROPOSAL_OBJECTIVES = ("field_only", "all_scalarized", "all_field_anchored")
DEVELOPMENT_SEED = 1103
FRESH_CONFIRMATION_SEEDS = (
    20_260_901,
    20_260_902,
    20_260_903,
    20_260_904,
    20_260_905,
)
MATCHED_DEVELOPMENT_STAGE = "single_seed_matched_information_validation_development"
AUXILIARY_DEVELOPMENT_STAGE = "single_seed_auxiliary_compute_attribution_development"
CONFIRMATION_STAGE = "five_seed_matched_information_validation_confirmation"


class Release730MatchedTrainingError(RuntimeError):
    """Raised when a matched-information training boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730MatchedTrainingError(reason)


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


def canonical_digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            dict(payload),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "result_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _strict_atomic_torch_save(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "checkpoint_exists")
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
        == "aurora.aneug_release_730_matched_training.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id") == "aneug_release_730_matched_training_v1",
        "protocol_id",
    )
    _require(
        config.get("status")
        == "prepared_non_executable_until_model_selection_and_all_development_predecessors_terminal",
        "status",
    )
    source = config["source"]
    expected_source = {
        "dataset_revision": "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "processed_v5_bytes": 33_233_856_917,
        "processed_v5_sha256": "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
        "steady_bytes": 9_632_510_050,
        "steady_sha256": "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "steady_norm_bytes": 9_632_510_050,
        "steady_norm_sha256": "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "steady_scope_config_sha256": "782285c95a7eed7ead983b298426606bdb6d9258d076908c9c65a0ad3d8aa5cf",
        "steady_exposure_config_sha256": "3509191bd2c3e3294488ab5018109f3beccd402599a17e16dd8696d1deeaceaf",
        "public_overlap_result_sha256": "b3a118bae156a1dbc6c838b923a594f9b0f452a40f34b8bccb6bc396d28ba397",
        "private_overlap_result_sha256": "52219b9a7161f0932a4ed80020a339510474431b67e168741426c2a12e5092ef",
        "response_local_config_sha256": "38f256d4e60e2a7c748bb59b7e3de910a1bf1f464d18b7ec99ef0f435aa415b4",
        "ghd_gps_config_sha256": "0d9ee4615b5af9bf9058920e70252addf5146f06178fb058a2c193be1692bfc9",
        "transolver_config_sha256": "0cb20c0c3041e63043d92a4a4062e7b8f9b63deb2e7390dbbaeaf1c9bad86fcb",
        "multiseed_confirmation_config_sha256": "75cd2e6c5d7545dd56274d7dd1b14d8b07380b0711cf10573d5b9fcaa1b57d92",
    }
    _require(all(source.get(key) == value for key, value in expected_source.items()), "source")
    split = config["split"]
    _require(
        (
            split["train_cases"],
            split["validation_cases"],
            split["locked_test_cases"],
            split["processed_only_extra_cases"],
        )
        == (584, 73, 73, 79),
        "split_counts",
    )
    _require(
        split["train_loader_order_sha256"]
        == "83d40e0579c0999fb380029d11811df835131b62e6bbd3557ad33254f22e6b8f"
        and split["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "loader_order",
    )
    _require(split["read_train_fields"] and split["read_validation_fields"], "development_read")
    _require(
        not split["read_locked_test_fields"]
        and not split["read_processed_only_extra_fields"]
        and not split["test_opened"],
        "sealed_read",
    )
    factorial = config["factorial"]
    _require(
        factorial["model_roles"] == list(MODEL_ROLES)
        and factorial["information_modes"] == list(FACTORIAL_INFORMATION_MODES)
        and factorial["cells"]
        == ["control_T", "control_TS", "proposal_T", "proposal_TS"]
        and factorial["one_cell_per_activation"] is True
        and factorial["same_training_seed_across_cells"] is True
        and factorial["same_transient_protocol_within_role"] is True
        and factorial["same_steady_scope_and_schedule_across_roles"] is True
        and factorial["proposal_only_steady_access"] is False
        and factorial["steady_supervision_is_novelty"] is False,
        "factorial",
    )
    attribution = config["auxiliary_attribution"]
    _require(
        attribution["information_mode"] == "transient_mean"
        and attribution["cells"] == ["control_TM", "proposal_TM"]
        and attribution["single_seed_development_only"] is True
        and attribution["examples_per_transient_epoch"] == 584
        and attribution["one_second_geometry_pass_per_transient_case"] is True
        and attribution["target"] == "same_train_case_80_phase_mean_vector_wss"
        and attribution["shared_single_field_head_with_t_plus_s"] is True
        and attribution["head_output_scale"]
        == "transient_train_cycle_mean_physical_vector_rms"
        and attribution["steady_wss_rows_read"] == 0
        and attribution["locked_test_or_extra_rows_read"] == 0
        and attribution["comparison_cells"] == ["control_TS", "proposal_TS"]
        and attribution["causal_steady_label_effect"] is False
        and attribution["standalone_novelty"] is False,
        "auxiliary_attribution",
    )
    confirmation = config["confirmation"]
    _require(
        confirmation["protocol_id"]
        == "aneug_release_730_multiseed_confirmation_v1"
        and confirmation["activation_stage"] == CONFIRMATION_STAGE
        and tuple(confirmation["fresh_training_seeds"])
        == FRESH_CONFIRMATION_SEEDS
        and confirmation["cells_per_seed"]
        == ["control_T", "control_TS", "proposal_T", "proposal_TS"]
        and confirmation["cell_count"] == 20
        and confirmation["selected_models_frozen_before_confirmation"] is True
        and confirmation["single_seed_matched_information_result_required"]
        is True
        and confirmation["same_seed_shared_across_four_cells"] is True
        and confirmation[
            "seed_excluded_from_transient_protocol_digest_and_recorded_separately"
        ]
        is True
        and confirmation["transient_mean_sidecar_in_confirmation"] is False
        and confirmation["locked_test_or_extra_rows_read"] == 0,
        "confirmation",
    )
    steady = config["eligible_steady"]
    _require(
        (
            steady["processed_rows"],
            steady["eligible_rows"],
            steady["excluded_overlap_rows"],
            steady["examples_per_transient_epoch"],
        )
        == (14_392, 13_985, 407, 584)
        and steady["eligible_case_digest"]
        == "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc"
        and steady["ordered_case_digest"]
        == "403ae3afedcbf755a1ff97e096090930b016fb8ebcfdaf5b2e7540bc6828feb7"
        and steady["ordered_index_digest"]
        == "292946acf8857942a68df1626ca58cf46f5260b0d64b277439b42a92d5bd4629"
        and steady["schedule_algorithm"]
        == "sha256_ranked_full_cycle_without_replacement_v1"
        and steady["schedule_seed"] == 20_260_821
        and steady["one_single_field_example_per_transient_cycle_case"] is True
        and steady["separate_single_field_head"] is True
        and steady["replicate_across_80_phases"] is False
        and steady["steady_time_or_waveform_token"] is False,
        "steady_scope",
    )
    selected = config["selected_model_space"]
    _require(
        selected["control_families"] == list(CONTROL_FAMILIES)
        and selected["proposal_family"] == PROPOSAL_FAMILY
        and selected["proposal_rank_grid"] == [16, 32, 64, 128, 256]
        and selected["proposal_objective_variants"] == list(PROPOSAL_OBJECTIVES)
        and selected["selection_record_required"] is True
        and selected["selection_record_cannot_use_locked_test_or_79_extras"] is True,
        "model_space",
    )
    objective = config["objective"]
    _require(
        objective["steady_pair_coefficient"] == 1.0
        and objective["transient_mean_pair_coefficient"] == 1.0
        and objective["steady_head_output_scale"]
        == "eligible_steady_physical_vector_rms_from_bound_descriptive_audit"
        and objective["transient_mean_head_output_scale"]
        == "transient_train_cycle_mean_physical_vector_rms_computed_from_frozen_train_fields"
        and objective["steady_scale_is_loss_weight"] is False
        and objective["reference_tawss_floor_multiplier"] == 1e-4
        and objective["osi_pseudo_huber_delta"] == 0.02
        and objective["functional_to_field_norm_ratio"] == 1.0
        and objective["separate_functional_head"] is False
        and objective["rrt_loss"] is False,
        "objective",
    )
    optimization = config["optimization"]
    _require(
        (
            optimization["development_seed"],
            optimization["maximum_epochs"],
            optimization["minimum_epochs"],
            optimization["early_stopping_patience"],
            optimization["gradient_accumulation_pairs"],
            optimization["validation_interval_epochs"],
            optimization["checkpoint_interval_epochs"],
        )
        == (DEVELOPMENT_SEED, 251, 80, 40, 2, 1, 10)
        and optimization["learning_rate"] == 3e-4
        and optimization["weight_decay"] == 1e-4
        and optimization["scheduler"] == "step_50_gamma_0p75",
        "optimization",
    )
    evaluation = config["evaluation"]
    _require(
        evaluation["common_report_space"] == "raw_released_physical_cartesian_wss"
        and evaluation["metrics"]
        == [
            "field_relative_l2",
            "mean_wss_vector_error",
            "tawss_normalized_absolute_error",
            "osi_mae",
            "osi_coverage",
        ]
        and evaluation["case_level_paired_analysis"] is True
        and evaluation["absolute_performance_threshold"] is None
        and evaluation["automatic_winner"] is False
        and evaluation["case_identifiers"] is False,
        "evaluation",
    )
    runtime = config["runtime"]
    _require(
        runtime["server"] == "introai9"
        and runtime["ngpus"] == 1
        and runtime["memory_gb"] == 64
        and runtime["walltime"] == "72:00:00"
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        "runtime",
    )
    authorization = config["authorization"]
    _require(
        authorization["execute_now"] is False
        and authorization[
            "requires_all_direct_and_candidate_development_terminal_records"
        ]
        is True
        and authorization["requires_selected_model_decision_record"] is True
        and authorization["requires_steady_scale_audit_terminal_result"] is True
        and authorization["requires_fresh_private_activation"] is True
        and authorization[
            "genuine_infrastructure_interruption_exact_state_resume_allowed"
        ]
        is True
        and authorization["continuation_requires_checkpoint_and_terminal_hashes"]
        is True,
        "authorization",
    )
    _require(
        authorization["multi_seed_confirmation"] is True,
        "authorization_confirmation",
    )
    for key in (
        "read_locked_test",
        "read_processed_only_extra",
        "paper_performance_claim",
        "publish_numeric_result",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")
    _require(
        authorization["server"] == "introai9"
        and authorization["excluded_server"] == "junjinyong",
        "server_scope",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def activation_training_stage(
    config: Mapping[str, Any], information_mode: str, training_seed: int
) -> str:
    """Return the sole stage authorized for one mode/seed combination."""

    _require(
        isinstance(training_seed, int) and not isinstance(training_seed, bool),
        "training_seed_type",
    )
    if training_seed == int(config["optimization"]["development_seed"]):
        return (
            AUXILIARY_DEVELOPMENT_STAGE
            if information_mode == "transient_mean"
            else MATCHED_DEVELOPMENT_STAGE
        )
    _require(
        information_mode in FACTORIAL_INFORMATION_MODES
        and training_seed in tuple(config["confirmation"]["fresh_training_seeds"]),
        "confirmation_seed_mode",
    )
    return CONFIRMATION_STAGE


def validate_activation(
    path: str | Path,
    config: Mapping[str, Any],
    expected_commit: str,
    model_role: str,
    information_mode: str,
    expected_training_seed: int,
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_matched_training_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    expected_stage = activation_training_stage(
        config, information_mode, expected_training_seed
    )
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success"
        and activation.get("authorized_stage") == expected_stage
        and activation.get("training_seed") == expected_training_seed,
        "activation_public",
    )
    _require(
        model_role in MODEL_ROLES
        and information_mode in INFORMATION_MODES
        and activation.get("model_role") == model_role
        and activation.get("information_mode") == information_mode,
        "activation_cell",
    )
    family = activation.get("model_family")
    objective = activation.get("objective_variant")
    rank = activation.get("selected_response_rank")
    if model_role == "selected_control":
        _require(
            family in CONTROL_FAMILIES
            and objective == "field_only"
            and rank is None,
            "control_cell",
        )
    else:
        _require(
            family == PROPOSAL_FAMILY
            and objective in PROPOSAL_OBJECTIVES
            and rank in config["selected_model_space"]["proposal_rank_grid"],
            "proposal_cell",
        )
    for key in (
        "development_evidence_bundle_sha256",
        "selected_model_decision_record_sha256",
        "steady_scale_result_sha256",
    ):
        _require(_is_sha256(activation.get(key)), f"activation_{key}")
    basis_hash = activation.get("response_basis_sha256")
    _require(
        (_is_sha256(basis_hash) if model_role == "selected_proposal" else basis_hash is None),
        "activation_basis",
    )
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["split"]["train_audit_private_sha256"]
        and activation.get("private_overlap_result_sha256")
        == config["source"]["private_overlap_result_sha256"]
        and activation.get("read_locked_test_or_extra") is False,
        "activation_scope",
    )
    confirmation = expected_stage == CONFIRMATION_STAGE
    _require(
        (
            activation.get("multiseed_confirmation_config_sha256")
            == config["source"]["multiseed_confirmation_config_sha256"]
            and _is_sha256(
                activation.get("single_seed_matched_information_result_sha256")
            )
        )
        if confirmation
        else (
            activation.get("multiseed_confirmation_config_sha256") is None
            and activation.get("single_seed_matched_information_result_sha256")
            is None
        ),
        "activation_confirmation_lineage",
    )
    continuation = activation.get("continuation_mode")
    _require(isinstance(continuation, bool), "continuation_mode")
    if continuation:
        _require(
            _is_sha256(activation.get("resume_checkpoint_sha256"))
            and _is_sha256(activation.get("prior_attempt_terminal_record_sha256")),
            "continuation_evidence",
        )
    else:
        _require(
            activation.get("resume_checkpoint_sha256") is None
            and activation.get("prior_attempt_terminal_record_sha256") is None,
            "continuation_evidence",
        )
    return activation


def validate_development_bundle(
    path: str | Path, expected_sha256: str
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "development_bundle_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_development_evidence_bundle.v1"
        and payload.get("status") == "complete_all_required_validation_development"
        and payload.get("locked_test_or_extra_read") is False,
        "development_bundle_scope",
    )
    required = payload.get("terminal_or_result_sha256")
    _require(
        isinstance(required, Mapping)
        and set(required)
        == {
            "response_oracle",
            "ghd_gps",
            "transolver",
            "response_only",
            "response_plus_residual_field",
            "selected_functional_variant",
        }
        and all(_is_sha256(value) for value in required.values()),
        "development_bundle_entries",
    )
    return dict(payload)


def validate_selection_record(
    path: str | Path,
    expected_sha256: str,
    activation: Mapping[str, Any],
    bundle_sha256: str,
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "selection_record_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_selected_models.v1"
        and payload.get("status") == "complete_validation_only_selection"
        and payload.get("development_evidence_bundle_sha256") == bundle_sha256
        and payload.get("locked_test_or_79_extra_used") is False
        and payload.get("absolute_performance_threshold") is None,
        "selection_record_scope",
    )
    _require(payload.get("selected_control_family") in CONTROL_FAMILIES, "selected_control")
    if activation["model_role"] == "selected_control":
        _require(
            payload["selected_control_family"] == activation["model_family"],
            "control_activation_selection",
        )
    _require(
        payload.get("selected_proposal_family") == PROPOSAL_FAMILY
        and payload.get("selected_proposal_objective") in PROPOSAL_OBJECTIVES
        and payload.get("selected_proposal_rank") in (16, 32, 64, 128, 256),
        "selected_proposal",
    )
    if activation["model_role"] == "selected_proposal":
        _require(
            payload["selected_proposal_objective"] == activation["objective_variant"]
            and payload["selected_proposal_rank"]
            == activation["selected_response_rank"]
            and payload.get("selected_response_basis_sha256")
            == activation["response_basis_sha256"],
            "proposal_activation_selection",
        )
    return dict(payload)


def validate_steady_scale_result(
    path: str | Path, expected_sha256: str, config: Mapping[str, Any]
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "steady_scale_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    scale = payload.get("steady_physical_vector_rms")
    transient_scale = payload.get("transient_train_physical_vector_rms")
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_steady_scale_audit_result.v1"
        and payload.get("status") == "complete_eligible_steady_descriptive"
        and payload.get("eligible_steady_rows")
        == config["eligible_steady"]["eligible_rows"]
        and isinstance(scale, (int, float))
        and math.isfinite(float(scale))
        and float(scale) > 0.0
        and isinstance(transient_scale, (int, float))
        and math.isfinite(float(transient_scale))
        and float(transient_scale) > 0.0
        and payload.get("automatic_loss_weight") is None
        and payload.get("steady_wss_rows_read")
        == config["eligible_steady"]["eligible_rows"]
        and payload.get("model_fit_or_prediction") is False
        and payload.get("validation_test_or_extra_wss_rows_read") == 0
        and payload.get("gpu_used") is False
        and payload.get("case_ids_included") is False
        and payload.get("paper_performance_claim") is False,
        "steady_scale_scope",
    )
    return dict(payload)


def validate_single_seed_matched_information_result(
    path: str | Path, expected_sha256: str, config: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate the completed four-cell development result before fresh seeds."""

    _require(file_sha256(path) == expected_sha256, "single_seed_matched_hash")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_matched_information_analysis_result.v1"
        and payload.get("protocol_id")
        == "aneug_release_730_matched_information_analysis_v1"
        and payload.get("status") == "complete"
        and payload.get("evidence_role")
        == "validation_development_matched_information_factorial"
        and payload.get("paired_case_count") == config["split"]["validation_cases"]
        and payload.get("case_identifiers_included") is False
        and payload.get("locked_test_or_extra_values_read") is False
        and payload.get("paper_performance_claim") is False,
        "single_seed_matched_result",
    )
    return dict(payload)


class MatchedCycleSingleFieldModel(nn.Module):
    """Expose a physical cycle and one auxiliary field from a shared encoder."""

    def __init__(
        self,
        inner: nn.Module,
        *,
        model_role: str,
        model_family: str,
        cycle_output_scale: float,
        single_field_output_scale: float,
    ) -> None:
        super().__init__()
        _require(model_role in MODEL_ROLES, "model_role")
        _require(
            math.isfinite(cycle_output_scale) and cycle_output_scale > 0.0,
            "cycle_output_scale",
        )
        _require(
            math.isfinite(single_field_output_scale)
            and single_field_output_scale > 0.0,
            "single_field_output_scale",
        )
        self.inner = inner
        self.model_role = model_role
        self.model_family = model_family
        self.register_buffer(
            "cycle_output_scale", torch.tensor(float(cycle_output_scale))
        )
        self.register_buffer(
            "single_field_output_scale",
            torch.tensor(float(single_field_output_scale)),
        )

    @property
    def single_field_head(self) -> nn.Module:
        return self.inner.single_field_head

    def forward_cycle(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        if self.model_role == "selected_proposal":
            output = self.inner(
                case,
                variant="response_plus_residual",
                compute_residual_basis_leakage=False,
            )
            return output["field"]
        return self.inner(case, mode="cycle") * self.cycle_output_scale

    def forward_single_field(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        if self.model_role == "selected_proposal":
            normalized = self.inner.forward_single_field(case)
        else:
            normalized = self.inner(case, mode="single_field")
        return normalized * self.single_field_output_scale


def build_model(
    config: Mapping[str, Any],
    activation: Mapping[str, Any],
    topology: Mapping[str, torch.Tensor],
    cycle_output_scale: float,
    single_field_output_scale: float,
    basis_payload: Mapping[str, Any] | None,
) -> MatchedCycleSingleFieldModel:
    role = activation["model_role"]
    family = activation["model_family"]
    if role == "selected_control":
        if family == "release730_ghd_gps":
            backbone: nn.Module = Release730GHDGPSUNet(topology, width=128, heads=4)
        elif family == "release730_transolver":
            backbone = Release730FullCycleTransolver(
                width=256,
                heads=8,
                blocks=8,
                slices=32,
                mlp_ratio=2,
                dropout=0.0,
                output_phases=80,
            )
        else:
            raise Release730MatchedTrainingError("control_family")
        inner: nn.Module = SharedEncoderSingleFieldAdapter(backbone)
    else:
        _require(family == PROPOSAL_FAMILY and basis_payload is not None, "proposal_family")
        backbone = Release730GHDGPSUNet(topology, width=128, heads=4)
        inner = SharedEncoderCycleResponseResidual(
            backbone,
            basis_payload,
            rank=int(activation["selected_response_rank"]),
            local_output_scale=cycle_output_scale,
        )
    return MatchedCycleSingleFieldModel(
        inner,
        model_role=role,
        model_family=family,
        cycle_output_scale=cycle_output_scale,
        single_field_output_scale=single_field_output_scale,
    )


def configure_information_mode(
    model: MatchedCycleSingleFieldModel, information_mode: str
) -> None:
    _require(information_mode in INFORMATION_MODES, "information_mode")
    for parameter in model.parameters():
        parameter.requires_grad_(True)
    if information_mode == "transient_only":
        for parameter in model.single_field_head.parameters():
            parameter.requires_grad_(False)


def active_parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


@torch.no_grad()
def evaluate(
    model: MatchedCycleSingleFieldModel,
    cases: Sequence[Mapping[str, torch.Tensor]],
    config: Mapping[str, Any],
    objective_variant: str,
    reference_tawss_floor: float,
    selection_normalizers: Mapping[str, float] | None,
    device: torch.device,
) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    per_case_terms: list[dict[str, float]] = []
    for cpu_case in cases:
        case = _to_device(cpu_case, device)
        prediction = model.forward_cycle(case)
        metrics = extended_case_metrics(
            prediction,
            case["wss"],
            case["vertex_weights"],
            case["normals"],
        )
        terms = alignment_terms(prediction, case, config, reference_tawss_floor)
        metrics["mean_vector_tawss_normalized_l2"] = float(
            torch.sqrt(torch.clamp(terms["mean_vector"], min=0.0)).item()
        )
        osi, coverage = _valid_support_osi(
            prediction,
            case["wss"],
            case["vertex_weights"],
            reference_tawss_floor,
        )
        metrics["osi_mae"] = osi
        metrics["osi_coverage"] = coverage
        per_case.append(metrics)
        per_case_terms.append({name: float(terms[name].item()) for name in LOSS_TERMS})
    keys = tuple(per_case[0])
    aggregate = {
        key: sum(row[key] for row in per_case) / len(per_case) for key in keys
    }
    aggregate_terms = {
        name: sum(row[name] for row in per_case_terms) / len(per_case_terms)
        for name in LOSS_TERMS
    }
    utility = None
    if selection_normalizers is not None:
        utility = validation_utility(aggregate, selection_normalizers, objective_variant)
    return {
        "aggregate": aggregate,
        "aggregate_alignment_terms": aggregate_terms,
        "variant_validation_utility": utility,
        "per_case_without_identifiers": per_case,
        "per_case_alignment_terms_without_identifiers": per_case_terms,
        "case_count": len(per_case),
    }


@torch.no_grad()
def compute_train_normalizers(
    model: MatchedCycleSingleFieldModel,
    cases: Sequence[Mapping[str, torch.Tensor]],
    config: Mapping[str, Any],
    reference_tawss_floor: float,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    sums = {name: 0.0 for name in LOSS_TERMS}
    for cpu_case in cases:
        case = _to_device(cpu_case, device)
        terms = alignment_terms(
            model.forward_cycle(case), case, config, reference_tawss_floor
        )
        for name in LOSS_TERMS:
            sums[name] += float(terms[name].item())
    result = {name: value / len(cases) for name, value in sums.items()}
    _require(
        all(math.isfinite(value) and value > 1e-12 for value in result.values()),
        "train_normalizers",
    )
    return result


def transient_protocol_digest(
    config: Mapping[str, Any], activation: Mapping[str, Any]
) -> str:
    """Return the information-mode-independent protocol identifier."""

    optimization = {
        key: value
        for key, value in config["optimization"].items()
        if key != "development_seed"
    }
    payload = {
        "protocol_id": config["protocol_id"],
        "model_role": activation["model_role"],
        "model_family": activation["model_family"],
        "objective_variant": activation["objective_variant"],
        "selected_response_rank": activation["selected_response_rank"],
        "split": config["split"],
        "objective": config["objective"],
        "optimization_without_training_seed": optimization,
        "training_seed_recorded_separately": True,
    }
    return canonical_digest(payload)


def _build_steady_stream(
    config: Mapping[str, Any],
    paths: Mapping[str, Path],
    topology: Mapping[str, torch.Tensor],
) -> tuple[MatchedSteadyStream, tuple[int, ...]]:
    scope_config = load_scope_config(paths["steady_scope_config"])
    exposure_config = load_exposure_config(paths["steady_exposure_config"])
    _require(
        exposure_config["scope"]["eligible_steady_rows"]
        == config["eligible_steady"]["eligible_rows"]
        and exposure_config["scope"]["ordered_case_digest"]
        == config["eligible_steady"]["ordered_case_digest"]
        and exposure_config["scope"]["ordered_index_digest"]
        == config["eligible_steady"]["ordered_index_digest"],
        "exposure_config_scope",
    )
    archive = safe_torch_load(paths["steady"], torch)
    indices = load_scope_files(
        scope_config,
        paths["public_overlap"],
        paths["private_overlap"],
        archive,
    )
    audit = json.loads(paths["train_audit_private"].read_text(encoding="utf-8"))
    _require(
        audit.get("schema_version")
        == "aurora.aneug_release_730_train_audit.private_statistics.v1"
        and audit.get("validation_test_or_extra_statistics_included") is False,
        "train_audit_scope",
    )
    ghd_mean = torch.tensor(audit["ghd"]["mean"], dtype=torch.float32)
    ghd_std = torch.tensor(
        audit["ghd"]["std_population"], dtype=torch.float32
    ).clamp(min=1e-6)
    _require("faces" in topology, "topology_faces")
    stream = MatchedSteadyStream(
        archive,
        indices,
        ghd_mean=ghd_mean,
        ghd_std=ghd_std,
        faces=topology["faces"],
        expected_rows=config["eligible_steady"]["processed_rows"],
        expected_nodes=13_902,
        expected_eligible_rows=config["eligible_steady"]["eligible_rows"],
        expected_ordered_index_digest=config["eligible_steady"][
            "ordered_index_digest"
        ],
        expected_ordered_case_digest=config["eligible_steady"][
            "ordered_case_digest"
        ],
    )
    return stream, tuple(indices)


def rebuild_exposure_digest(
    eligible_indices: Sequence[int],
    *,
    epochs: int,
    cases_per_epoch: int,
    seed: int,
) -> ExposureDigest:
    digest = ExposureDigest()
    for epoch in range(epochs):
        for index in epoch_exposure_indices(
            eligible_indices,
            epoch=epoch,
            cases_per_epoch=cases_per_epoch,
            seed=seed,
        ):
            digest.update(index)
    _require(digest.count == epochs * cases_per_epoch, "exposure_rebuild")
    return digest


def make_checkpoint(
    *,
    config: Mapping[str, Any],
    activation: Mapping[str, Any],
    epoch: int,
    optimizer_steps: int,
    selection_name: str,
    selection_value: float,
    best_selection_value: float,
    best_epoch: int,
    stale_epochs: int,
    model_state_dict: Mapping[str, torch.Tensor],
    optimizer_state_dict: Mapping[str, Any],
    scheduler_state_dict: Mapping[str, Any],
    best_state_dict: Mapping[str, torch.Tensor],
    history: Sequence[Mapping[str, Any]],
    smoke: Mapping[str, Any],
    train_term_normalizers: Mapping[str, float] | None,
    selection_endpoint_normalizers: Mapping[str, float] | None,
    reference_tawss_floor: float,
    steady_exposure_count: int,
    steady_exposure_prefix_sha256: str | None,
    elapsed_seconds_accumulated: float,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    _require(epoch > 0 and optimizer_steps > 0 and 0 < best_epoch <= epoch, "checkpoint_progress")
    _require(stale_epochs >= 0 and len(history) == epoch, "checkpoint_history")
    _require(
        all(
            math.isfinite(value)
            for value in (
                selection_value,
                best_selection_value,
                reference_tawss_floor,
                elapsed_seconds_accumulated,
            )
        )
        and reference_tawss_floor > 0.0
        and elapsed_seconds_accumulated >= 0.0,
        "checkpoint_finite",
    )
    if activation["information_mode"] == "eligible_steady":
        _require(
            steady_exposure_count
            == epoch * config["eligible_steady"]["examples_per_transient_epoch"]
            and _is_sha256(steady_exposure_prefix_sha256),
            "checkpoint_steady_exposure",
        )
    else:
        _require(
            steady_exposure_count == 0
            and steady_exposure_prefix_sha256 is None,
            "checkpoint_transient_exposure",
        )
    information_mode = activation["information_mode"]
    training_seed = int(activation["training_seed"])
    training_stage = activation_training_stage(
        config, information_mode, training_seed
    )
    auxiliary_examples = (
        epoch * config["auxiliary_attribution"]["examples_per_transient_epoch"]
        if information_mode in AUXILIARY_INFORMATION_MODES
        else 0
    )
    auxiliary_source = {
        "transient_only": None,
        "transient_mean": "same_train_case_cycle_mean",
        "eligible_steady": "eligible_steady_wss",
    }[information_mode]
    return {
        "schema_version": "aurora.private.aneug_release_730_matched_training_checkpoint.v1",
        "protocol_id": config["protocol_id"],
        "model_role": activation["model_role"],
        "information_mode": activation["information_mode"],
        "model_family": activation["model_family"],
        "objective_variant": activation["objective_variant"],
        "selected_response_rank": activation["selected_response_rank"],
        "training_seed": training_seed,
        "training_stage": training_stage,
        "epoch": epoch,
        "optimizer_steps": optimizer_steps,
        "selection_name": selection_name,
        "selection_value": selection_value,
        "best_selection_value": best_selection_value,
        "best_epoch": best_epoch,
        "stale_epochs": stale_epochs,
        "model_state_dict": dict(model_state_dict),
        "optimizer_state_dict": dict(optimizer_state_dict),
        "scheduler_state_dict": dict(scheduler_state_dict),
        "best_state_dict": dict(best_state_dict),
        "history": [dict(row) for row in history],
        "smoke": dict(smoke),
        "train_term_normalizers": (
            None if train_term_normalizers is None else dict(train_term_normalizers)
        ),
        "selection_endpoint_normalizers": (
            None
            if selection_endpoint_normalizers is None
            else dict(selection_endpoint_normalizers)
        ),
        "reference_tawss_floor": reference_tawss_floor,
        "steady_exposure_count": steady_exposure_count,
        "steady_exposure_prefix_sha256": steady_exposure_prefix_sha256,
        "single_field_auxiliary_examples_consumed": auxiliary_examples,
        "single_field_auxiliary_source": auxiliary_source,
        "elapsed_seconds_accumulated": elapsed_seconds_accumulated,
        "rng_state": capture_rng_state(),
        **dict(provenance),
    }


def restore_checkpoint(
    path: str | Path,
    *,
    config: Mapping[str, Any],
    activation: Mapping[str, Any],
    expected_provenance: Mapping[str, Any],
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
) -> dict[str, Any]:
    payload = torch.load(str(path), map_location="cpu", weights_only=True)
    _require(isinstance(payload, Mapping), "checkpoint_mapping")
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_matched_training_checkpoint.v1"
        and payload.get("protocol_id") == config["protocol_id"]
        and payload.get("model_role") == activation["model_role"]
        and payload.get("information_mode") == activation["information_mode"]
        and payload.get("model_family") == activation["model_family"]
        and payload.get("objective_variant") == activation["objective_variant"]
        and payload.get("selected_response_rank")
        == activation["selected_response_rank"]
        and payload.get("training_seed") == activation.get("training_seed")
        and payload.get("training_stage")
        == activation_training_stage(
            config,
            activation["information_mode"],
            int(activation["training_seed"]),
        ),
        "checkpoint_identity",
    )
    for key, value in expected_provenance.items():
        _require(payload.get(key) == value, f"checkpoint_provenance_{key}")
    epoch = int(payload.get("epoch", -1))
    best_epoch = int(payload.get("best_epoch", -1))
    _require(
        0 < epoch <= config["optimization"]["maximum_epochs"]
        and 0 < best_epoch <= epoch
        and int(payload.get("optimizer_steps", -1)) > 0,
        "checkpoint_progress",
    )
    _require(
        isinstance(payload.get("history"), list)
        and len(payload["history"]) == epoch
        and int(payload["history"][-1]["epoch"]) == epoch,
        "checkpoint_history",
    )
    for key in (
        "selection_value",
        "best_selection_value",
        "reference_tawss_floor",
        "elapsed_seconds_accumulated",
    ):
        _require(math.isfinite(float(payload.get(key, math.nan))), f"checkpoint_{key}")
    if activation["information_mode"] == "eligible_steady":
        _require(
            payload.get("steady_exposure_count")
            == epoch * config["eligible_steady"]["examples_per_transient_epoch"]
            and _is_sha256(payload.get("steady_exposure_prefix_sha256")),
            "checkpoint_steady_exposure",
        )
    else:
        _require(
            payload.get("steady_exposure_count") == 0
            and payload.get("steady_exposure_prefix_sha256") is None,
            "checkpoint_transient_exposure",
        )
    expected_auxiliary_examples = (
        epoch * config["auxiliary_attribution"]["examples_per_transient_epoch"]
        if activation["information_mode"] in AUXILIARY_INFORMATION_MODES
        else 0
    )
    expected_auxiliary_source = {
        "transient_only": None,
        "transient_mean": "same_train_case_cycle_mean",
        "eligible_steady": "eligible_steady_wss",
    }[activation["information_mode"]]
    _require(
        payload.get("single_field_auxiliary_examples_consumed")
        == expected_auxiliary_examples
        and payload.get("single_field_auxiliary_source")
        == expected_auxiliary_source,
        "checkpoint_auxiliary_accounting",
    )
    model.load_state_dict(payload["model_state_dict"], strict=True)
    optimizer.load_state_dict(payload["optimizer_state_dict"])
    scheduler.load_state_dict(payload["scheduler_state_dict"])
    rng = payload.get("rng_state")
    _require(isinstance(rng, Mapping), "checkpoint_rng")
    random.setstate(rng["python_random_state"])
    torch.set_rng_state(rng["torch_rng_state"])
    cuda_states = rng.get("cuda_rng_state_all", [])
    if torch.cuda.is_available():
        _require(bool(cuda_states), "checkpoint_cuda_rng")
        torch.cuda.set_rng_state_all(cuda_states)
    else:
        _require(cuda_states == [], "checkpoint_cpu_rng")
    return dict(payload)


def run_training(
    config: Mapping[str, Any],
    paths: Mapping[str, Path],
    activation: Mapping[str, Any],
    steady_scale_result: Mapping[str, Any],
    result_path: Path,
    checkpoint_directory: Path,
    provenance: Mapping[str, Any],
    resume_checkpoint: Path | None = None,
    resume_expected_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    optimization = config["optimization"]
    role = activation["model_role"]
    information_mode = activation["information_mode"]
    objective_variant = activation["objective_variant"]
    seed = int(activation["training_seed"])
    training_stage = activation_training_stage(config, information_mode, seed)
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(4)
    device = torch.device("cuda")
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    train, validation, topology, cycle_output_scale = load_development_data(
        config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
    )
    basis_payload = None
    if role == "selected_proposal":
        basis_payload = load_response_basis(
            paths["response_basis"], activation["response_basis_sha256"], config
        )
    single_field_output_scale = (
        train_cycle_mean_wss_rms(train)
        if information_mode == "transient_mean"
        else float(steady_scale_result["steady_physical_vector_rms"])
    )
    model = build_model(
        config,
        activation,
        topology,
        cycle_output_scale,
        single_field_output_scale,
        basis_payload,
    ).to(device)
    configure_information_mode(model, information_mode)
    reference_tawss_floor = train_wss_rms(train) * float(
        config["objective"]["reference_tawss_floor_multiplier"]
    )
    train_normalizers = None
    selection_normalizers = None
    initial_validation = None
    aligned_proposal = role == "selected_proposal" and objective_variant != "field_only"
    if aligned_proposal:
        train_normalizers = compute_train_normalizers(
            model, train, config, reference_tawss_floor, device
        )
        initial_validation = evaluate(
            model,
            validation,
            config,
            objective_variant,
            reference_tawss_floor,
            None,
            device,
        )
        selection_normalizers = _selection_normalizers(initial_validation)

    steady_stream = None
    eligible_indices: tuple[int, ...] = ()
    if information_mode == "eligible_steady":
        steady_stream, eligible_indices = _build_steady_stream(config, paths, topology)
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    _require(bool(trainable), "trainable_parameters")
    optimizer = torch.optim.AdamW(
        trainable,
        lr=float(optimization["learning_rate"]),
        weight_decay=float(optimization["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=int(optimization["step_size_epochs"]),
        gamma=float(optimization["gamma"]),
    )
    maximum_epochs = int(optimization["maximum_epochs"])
    minimum_epochs = int(optimization["minimum_epochs"])
    patience = int(optimization["early_stopping_patience"])
    accumulation = int(optimization["gradient_accumulation_pairs"])
    checkpoint_interval = int(optimization["checkpoint_interval_epochs"])
    steady_cases_per_epoch = int(
        config["eligible_steady"]["examples_per_transient_epoch"]
    )
    steady_seed = int(config["eligible_steady"]["schedule_seed"])
    checkpoint_directory.mkdir(parents=True, exist_ok=True)
    _require(not any(checkpoint_directory.iterdir()), "checkpoint_directory_not_empty")

    start_epoch = 0
    optimizer_steps = 0
    best_selection = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, Any]] = []
    elapsed_prior = 0.0
    resumed_from_epoch: int | None = None
    selection_name = (
        "initial_endpoint_normalized_validation_utility"
        if aligned_proposal
        else "validation_field_relative_l2"
    )
    exposure = ExposureDigest()
    if resume_checkpoint is None:
        smoke_case = _to_device(train[0], device)
        smoke_prediction = model.forward_cycle(smoke_case)
        optimizer.zero_grad(set_to_none=True)
        if aligned_proposal:
            _require(train_normalizers is not None, "train_normalizers")
            smoke_terms = alignment_terms(
                smoke_prediction, smoke_case, config, reference_tawss_floor
            )
            smoke_diagnostic = backward_case(
                model,
                smoke_terms,
                train_normalizers,
                objective_variant,
                1,
                float(config["objective"]["functional_to_field_norm_ratio"]),
            )
        else:
            smoke_loss = field_loss(
                smoke_prediction, smoke_case["wss"], smoke_case["vertex_weights"]
            )
            smoke_loss.backward()
            smoke_diagnostic = {
                "scalarized_value": float(smoke_loss.detach().item()),
                "projection_applied": False,
                "gradient_conflict_measured": False,
            }
        if information_mode in AUXILIARY_INFORMATION_MODES:
            smoke_auxiliary = transient_mean_auxiliary_case(smoke_case)
            smoke_single = model.forward_single_field(smoke_auxiliary)
            smoke_auxiliary_loss = single_field_relative_squared_error(
                smoke_single,
                smoke_auxiliary["single_field_wss"],
                smoke_auxiliary["vertex_weights"],
            )
            smoke_auxiliary_loss.backward()
            smoke_diagnostic["single_field_head_finite_backward"] = True
        _require(
            all(
                parameter.grad is None or bool(torch.isfinite(parameter.grad).all().item())
                for parameter in model.parameters()
            ),
            "smoke_gradient",
        )
        optimizer.zero_grad(set_to_none=True)
        smoke = {
            "finite_forward_backward": True,
            "diagnostic": smoke_diagnostic,
            "single_field_smoke_target": (
                "train_transient_cycle_mean"
                if information_mode in AUXILIARY_INFORMATION_MODES
                else None
            ),
            "used_steady_wss": False,
            "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        }
    else:
        _require(resume_expected_provenance is not None, "resume_provenance")
        restored = restore_checkpoint(
            resume_checkpoint,
            config=config,
            activation=activation,
            expected_provenance=resume_expected_provenance,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
        )
        start_epoch = int(restored["epoch"])
        resumed_from_epoch = start_epoch
        optimizer_steps = int(restored["optimizer_steps"])
        best_selection = float(restored["best_selection_value"])
        best_epoch = int(restored["best_epoch"])
        best_state = dict(restored["best_state_dict"])
        stale = int(restored["stale_epochs"])
        history = [dict(row) for row in restored["history"]]
        smoke = dict(restored["smoke"])
        elapsed_prior = float(restored["elapsed_seconds_accumulated"])
        _require(
            restored["train_term_normalizers"] == train_normalizers
            and restored["selection_endpoint_normalizers"] == selection_normalizers
            and math.isclose(
                float(restored["reference_tawss_floor"]),
                reference_tawss_floor,
                rel_tol=0.0,
                abs_tol=1e-12,
            ),
            "resume_objective_state",
        )
        if information_mode == "eligible_steady":
            exposure = rebuild_exposure_digest(
                eligible_indices,
                epochs=start_epoch,
                cases_per_epoch=steady_cases_per_epoch,
                seed=steady_seed,
            )
            _require(
                exposure.count == restored["steady_exposure_count"]
                and exposure.hexdigest()
                == restored["steady_exposure_prefix_sha256"],
                "resume_exposure",
            )

    training_epochs = (
        range(start_epoch, start_epoch)
        if start_epoch >= minimum_epochs and stale >= patience
        else range(start_epoch, maximum_epochs)
    )
    for epoch in training_epochs:
        model.train()
        transient_order = list(range(len(train)))
        random.Random(seed + epoch).shuffle(transient_order)
        steady_order: list[int] = []
        if information_mode == "eligible_steady":
            steady_order = list(
                epoch_exposure_indices(
                    eligible_indices,
                    epoch=epoch,
                    cases_per_epoch=steady_cases_per_epoch,
                    seed=steady_seed,
                )
            )
            _require(len(steady_order) == len(transient_order) == 584, "paired_epoch")
        optimizer.zero_grad(set_to_none=True)
        cycle_sum = 0.0
        auxiliary_sum = 0.0
        conflicts = 0
        cosine_sum = 0.0
        for step, transient_index in enumerate(transient_order):
            case = _to_device(train[transient_index], device)
            prediction = model.forward_cycle(case)
            if aligned_proposal:
                _require(train_normalizers is not None, "train_normalizers")
                terms = alignment_terms(
                    prediction, case, config, reference_tawss_floor
                )
                diagnostic = backward_case(
                    model,
                    terms,
                    train_normalizers,
                    objective_variant,
                    accumulation,
                    float(config["objective"]["functional_to_field_norm_ratio"]),
                )
            else:
                cycle_loss = field_loss(
                    prediction, case["wss"], case["vertex_weights"]
                )
                _require(bool(torch.isfinite(cycle_loss).item()), "cycle_loss")
                (cycle_loss / accumulation).backward()
                diagnostic = {
                    "scalarized_value": float(cycle_loss.detach().item()),
                    "projection_applied": False,
                    "gradient_cosine_before": 0.0,
                }
            cycle_sum += float(diagnostic["scalarized_value"])
            conflicts += int(bool(diagnostic["projection_applied"]))
            cosine_sum += float(diagnostic["gradient_cosine_before"])
            if information_mode == "eligible_steady":
                _require(steady_stream is not None, "steady_stream")
                steady_index = steady_order[step]
                steady_case = _to_device(steady_stream.decode(steady_index), device)
                steady_prediction = model.forward_single_field(steady_case)
                auxiliary_loss = single_field_relative_squared_error(
                    steady_prediction,
                    steady_case["steady_wss"],
                    steady_case["vertex_weights"],
                )
                (
                    float(config["objective"]["steady_pair_coefficient"])
                    * auxiliary_loss
                    / accumulation
                ).backward()
                auxiliary_sum += float(auxiliary_loss.detach().item())
                exposure.update(steady_index)
            elif information_mode == "transient_mean":
                auxiliary_case = transient_mean_auxiliary_case(case)
                auxiliary_prediction = model.forward_single_field(auxiliary_case)
                auxiliary_loss = single_field_relative_squared_error(
                    auxiliary_prediction,
                    auxiliary_case["single_field_wss"],
                    auxiliary_case["vertex_weights"],
                )
                (
                    float(config["objective"]["transient_mean_pair_coefficient"])
                    * auxiliary_loss
                    / accumulation
                ).backward()
                auxiliary_sum += float(auxiliary_loss.detach().item())
            if (step + 1) % accumulation == 0:
                torch.nn.utils.clip_grad_norm_(
                    trainable, float(optimization["gradient_clip_norm"])
                )
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_steps += 1
        _require(len(transient_order) % accumulation == 0, "incomplete_pair_batch")
        scheduler.step()
        validation_result = evaluate(
            model,
            validation,
            config,
            objective_variant,
            reference_tawss_floor,
            selection_normalizers,
            device,
        )
        validation_field = float(validation_result["aggregate"]["field_relative_l2"])
        selection_value = (
            float(validation_result["variant_validation_utility"])
            if aligned_proposal
            else validation_field
        )
        row: dict[str, Any] = {
            "epoch": epoch + 1,
            "optimizer_steps": optimizer_steps,
            "mean_cycle_objective": cycle_sum / len(transient_order),
            "mean_single_field_auxiliary_relative_squared_error": (
                auxiliary_sum / len(transient_order)
                if information_mode in AUXILIARY_INFORMATION_MODES
                else None
            ),
            "selection_value": selection_value,
            "validation_field_relative_l2": validation_field,
            "validation_tawss_error": float(
                validation_result["aggregate"]["tawss_normalized_absolute_error"]
            ),
            "validation_osi_mae": float(validation_result["aggregate"]["osi_mae"]),
            "gradient_conflict_fraction": (
                conflicts / len(transient_order)
                if objective_variant == "all_field_anchored"
                else None
            ),
            "mean_gradient_cosine_before": (
                cosine_sum / len(transient_order)
                if objective_variant == "all_field_anchored"
                else None
            ),
            "steady_examples_consumed_cumulative": exposure.count,
            "transient_mean_examples_consumed_cumulative": (
                (epoch + 1) * len(transient_order)
                if information_mode == "transient_mean"
                else 0
            ),
            "steady_exposure_prefix_sha256": (
                exposure.hexdigest() if steady_order else None
            ),
            "learning_rate": float(scheduler.get_last_lr()[0]),
        }
        history.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
        current_state: dict[str, torch.Tensor] | None = None
        if selection_value < best_selection:
            current_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
            best_selection = selection_value
            best_epoch = epoch + 1
            best_state = current_state
            stale = 0
        else:
            stale += 1
        if (epoch + 1) % checkpoint_interval == 0:
            if current_state is None:
                current_state = {
                    key: value.detach().cpu().clone()
                    for key, value in model.state_dict().items()
                }
            _require(best_state is not None, "best_state")
            _strict_atomic_torch_save(
                checkpoint_directory / f"epoch_{epoch + 1:03d}.pt",
                make_checkpoint(
                    config=config,
                    activation=activation,
                    epoch=epoch + 1,
                    optimizer_steps=optimizer_steps,
                    selection_name=selection_name,
                    selection_value=selection_value,
                    best_selection_value=best_selection,
                    best_epoch=best_epoch,
                    stale_epochs=stale,
                    model_state_dict=current_state,
                    optimizer_state_dict=optimizer.state_dict(),
                    scheduler_state_dict=scheduler.state_dict(),
                    best_state_dict=best_state,
                    history=history,
                    smoke=smoke,
                    train_term_normalizers=train_normalizers,
                    selection_endpoint_normalizers=selection_normalizers,
                    reference_tawss_floor=reference_tawss_floor,
                    steady_exposure_count=exposure.count,
                    steady_exposure_prefix_sha256=(
                        exposure.hexdigest() if steady_order else None
                    ),
                    elapsed_seconds_accumulated=elapsed_prior
                    + time.monotonic()
                    - started,
                    provenance=provenance,
                ),
            )
        if epoch + 1 >= minimum_epochs and stale >= patience:
            break

    _require(best_state is not None and best_epoch > 0, "best_checkpoint")
    model.load_state_dict(best_state, strict=True)
    final_validation = evaluate(
        model,
        validation,
        config,
        objective_variant,
        reference_tawss_floor,
        selection_normalizers,
        device,
    )
    _strict_atomic_torch_save(
        checkpoint_directory / "best.pt",
        {
            "schema_version": "aurora.private.aneug_release_730_matched_training_best.v1",
            "protocol_id": config["protocol_id"],
            "model_role": role,
            "information_mode": information_mode,
            "model_family": activation["model_family"],
            "objective_variant": objective_variant,
            "selected_response_rank": activation["selected_response_rank"],
            "training_seed": seed,
            "training_stage": training_stage,
            "best_epoch": best_epoch,
            "selection_name": selection_name,
            "best_selection_value": best_selection,
            "model_state_dict": best_state,
            "response_basis_embedded": False,
            "train_term_normalizers": train_normalizers,
            "selection_endpoint_normalizers": selection_normalizers,
            "reference_tawss_floor": reference_tawss_floor,
            "single_field_output_scale": single_field_output_scale,
            "single_field_output_scale_source": (
                "transient_train_cycle_mean_physical_vector_rms_computed_from_frozen_train_fields"
                if information_mode == "transient_mean"
                else (
                    "eligible_steady_physical_vector_rms_from_bound_descriptive_audit"
                    if information_mode == "eligible_steady"
                    else None
                )
            ),
            **dict(provenance),
        },
    )
    epochs_completed = len(history)
    is_steady = information_mode == "eligible_steady"
    is_transient_mean = information_mode == "transient_mean"
    uses_auxiliary = information_mode in AUXILIARY_INFORMATION_MODES
    result = {
        "schema_version": (
            "aurora.aneug_release_730_auxiliary_compute_cell.v1"
            if is_transient_mean
            else "aurora.aneug_release_730_matched_information_cell.v1"
        ),
        "protocol_id": (
            "aneug_release_730_auxiliary_compute_attribution_v1"
            if is_transient_mean
            else "aneug_release_730_matched_information_analysis_v1"
        ),
        "training_protocol_id": config["protocol_id"],
        "status": (
            "complete_validation_confirmation"
            if training_stage == CONFIRMATION_STAGE
            else "complete_validation_development"
        ),
        "model_role": role,
        "information_mode": information_mode,
        "model_family": activation["model_family"],
        "objective_variant": objective_variant,
        "selected_response_rank": activation["selected_response_rank"],
        "validation_case_digest": config["split"]["validation_case_digest"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "validation_loader_order_sha256": config["split"][
            "validation_loader_order_sha256"
        ],
        "eligible_steady_rows": config["eligible_steady"]["eligible_rows"]
        if is_steady
        else 0,
        "eligible_steady_case_digest": config["eligible_steady"][
            "eligible_case_digest"
        ]
        if is_steady
        else None,
        "steady_exposure_schedule_protocol_id": "aneug_release_730_steady_exposure_schedule_v1"
        if is_steady
        else None,
        "steady_exposure_schedule_config_sha256": config["source"][
            "steady_exposure_config_sha256"
        ]
        if is_steady
        else None,
        "steady_exposure_algorithm": config["eligible_steady"]["schedule_algorithm"]
        if is_steady
        else None,
        "steady_exposure_seed": config["eligible_steady"]["schedule_seed"]
        if is_steady
        else None,
        "steady_exposure_epochs": epochs_completed if is_steady else 0,
        "steady_examples_consumed": exposure.count if is_steady else 0,
        "steady_exposure_prefix_sha256": exposure.hexdigest() if is_steady else None,
        "transient_training_protocol_sha256": transient_protocol_digest(
            config, activation
        ),
        "training_seed": seed,
        "training_stage": training_stage,
        "transient_case_cycles_consumed": epochs_completed * len(train),
        "optimizer_steps": optimizer_steps,
        "training_gpu_seconds": elapsed_prior + time.monotonic() - started,
        "peak_gpu_memory_bytes": int(torch.cuda.max_memory_allocated()),
        "parameter_count": model_parameter_count(model),
        "active_parameter_count": active_parameter_count(model),
        "single_field_head_active": uses_auxiliary,
        "steady_head_active": is_steady,
        "steady_objective_scale_result_sha256": activation[
            "steady_scale_result_sha256"
        ]
        if is_steady
        else None,
        "single_field_output_scale": single_field_output_scale
        if uses_auxiliary
        else None,
        "single_field_output_scale_source": (
            "eligible_steady_physical_vector_rms_from_bound_descriptive_audit"
            if is_steady
            else (
                "transient_train_cycle_mean_physical_vector_rms_computed_from_frozen_train_fields"
                if is_transient_mean
                else None
            )
        ),
        "single_field_scale_source_sha256": (
            activation["steady_scale_result_sha256"]
            if is_steady
            else (
                config["split"]["train_audit_private_sha256"]
                if is_transient_mean
                else None
            )
        ),
        "single_field_auxiliary_source": (
            "eligible_steady_wss"
            if is_steady
            else ("same_train_case_cycle_mean" if is_transient_mean else None)
        ),
        "single_field_auxiliary_coefficient": (
            float(config["objective"]["steady_pair_coefficient"])
            if is_steady
            else (
                float(config["objective"]["transient_mean_pair_coefficient"])
                if is_transient_mean
                else None
            )
        ),
        "single_field_auxiliary_examples_consumed": (
            epochs_completed * len(train) if uses_auxiliary else 0
        ),
        "transient_mean_auxiliary_examples_consumed": (
            epochs_completed * len(train) if is_transient_mean else 0
        ),
        "steady_wss_rows_read_for_auxiliary": exposure.count if is_steady else 0,
        "additional_auxiliary_forward_backward_work": uses_auxiliary,
        "additional_steady_forward_backward_work": is_steady,
        "best_epoch": best_epoch,
        "epochs_completed": epochs_completed,
        "best_selection_value": best_selection,
        "selection_name": selection_name,
        "reference_tawss_floor": reference_tawss_floor,
        "train_term_normalizers": train_normalizers,
        "selection_endpoint_normalizers": selection_normalizers,
        "initial_validation": initial_validation,
        "validation": final_validation,
        "per_case_without_identifiers": final_validation[
            "per_case_without_identifiers"
        ],
        "history": history,
        "continuation_mode": resume_checkpoint is not None,
        "resumed_from_epoch": resumed_from_epoch,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
        "paper_result_or_claim": False,
        **dict(provenance),
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--model-role", choices=MODEL_ROLES)
    parser.add_argument("--information-mode", choices=INFORMATION_MODES)
    parser.add_argument("--training-seed", type=int)
    parser.add_argument("--development-evidence-bundle", type=Path)
    parser.add_argument("--selection-record", type=Path)
    parser.add_argument("--steady-scale-result", type=Path)
    parser.add_argument("--single-seed-matched-information-result", type=Path)
    parser.add_argument("--response-basis", type=Path)
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
    parser.add_argument("--public-overlap", type=Path)
    parser.add_argument("--private-overlap", type=Path)
    parser.add_argument("--steady-scope-config", type=Path)
    parser.add_argument("--steady-exposure-config", type=Path)
    parser.add_argument("--response-local-config", type=Path)
    parser.add_argument("--ghd-gps-config", type=Path)
    parser.add_argument("--transolver-config", type=Path)
    parser.add_argument("--multiseed-confirmation-config", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--checkpoint-directory", type=Path)
    parser.add_argument("--resume-checkpoint", type=Path)
    parser.add_argument("--prior-attempt-terminal-record", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    required = (
        args.activation,
        args.expected_commit,
        args.model_role,
        args.information_mode,
        args.training_seed,
        args.development_evidence_bundle,
        args.selection_record,
        args.steady_scale_result,
        args.transient,
        args.steady,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.public_overlap,
        args.private_overlap,
        args.steady_scope_config,
        args.steady_exposure_config,
        args.response_local_config,
        args.ghd_gps_config,
        args.transolver_config,
        args.multiseed_confirmation_config,
        args.result,
        args.checkpoint_directory,
    )
    _require(all(value is not None for value in required), "execution_arguments")
    activation = validate_activation(
        args.activation,
        config,
        args.expected_commit,
        args.model_role,
        args.information_mode,
        args.training_seed,
    )
    confirmation = activation["authorized_stage"] == CONFIRMATION_STAGE
    _require(
        (args.single_seed_matched_information_result is not None) is confirmation,
        "single_seed_matched_result_argument",
    )
    if confirmation:
        validate_single_seed_matched_information_result(
            args.single_seed_matched_information_result,
            activation["single_seed_matched_information_result_sha256"],
            config,
        )
    _require(
        (args.response_basis is not None)
        is (args.model_role == "selected_proposal"),
        "response_basis_argument",
    )
    bundle = validate_development_bundle(
        args.development_evidence_bundle,
        activation["development_evidence_bundle_sha256"],
    )
    validate_selection_record(
        args.selection_record,
        activation["selected_model_decision_record_sha256"],
        activation,
        activation["development_evidence_bundle_sha256"],
    )
    steady_scale = validate_steady_scale_result(
        args.steady_scale_result,
        activation["steady_scale_result_sha256"],
        config,
    )
    for path, expected, label in (
        (args.steady_scope_config, config["source"]["steady_scope_config_sha256"], "scope_config"),
        (
            args.steady_exposure_config,
            config["source"]["steady_exposure_config_sha256"],
            "exposure_config",
        ),
        (args.public_overlap, config["source"]["public_overlap_result_sha256"], "public_overlap"),
        (args.private_overlap, config["source"]["private_overlap_result_sha256"], "private_overlap"),
        (
            args.response_local_config,
            config["source"]["response_local_config_sha256"],
            "response_local_config",
        ),
        (args.ghd_gps_config, config["source"]["ghd_gps_config_sha256"], "ghd_gps_config"),
        (
            args.transolver_config,
            config["source"]["transolver_config_sha256"],
            "transolver_config",
        ),
        (
            args.multiseed_confirmation_config,
            config["source"]["multiseed_confirmation_config_sha256"],
            "multiseed_confirmation_config",
        ),
    ):
        _require(file_sha256(path) == expected, f"{label}_hash")
    continuation = args.resume_checkpoint is not None
    _require(activation["continuation_mode"] is continuation, "continuation_mode_mismatch")
    if continuation:
        _require(args.prior_attempt_terminal_record is not None, "prior_terminal_required")
        validate_interrupted_attempt_record(
            args.prior_attempt_terminal_record,
            activation["prior_attempt_terminal_record_sha256"],
        )
        _require(
            file_sha256(args.resume_checkpoint)
            == activation["resume_checkpoint_sha256"],
            "resume_checkpoint_hash",
        )
    else:
        _require(args.prior_attempt_terminal_record is None, "unexpected_prior_terminal")
    scientific_provenance = {
        "public_commit": args.expected_commit,
        "training_seed": int(activation["training_seed"]),
        "training_stage": activation["authorized_stage"],
        "training_config_sha256": file_sha256(args.config),
        "development_evidence_bundle_sha256": activation[
            "development_evidence_bundle_sha256"
        ],
        "selected_model_decision_record_sha256": activation[
            "selected_model_decision_record_sha256"
        ],
        "processed_v5_sha256": config["source"]["processed_v5_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        "private_overlap_result_sha256": config["source"][
            "private_overlap_result_sha256"
        ],
        "response_basis_sha256": activation["response_basis_sha256"],
        "bound_steady_scale_result_sha256": activation[
            "steady_scale_result_sha256"
        ],
        "multiseed_confirmation_config_sha256": config["source"][
            "multiseed_confirmation_config_sha256"
        ],
        "single_seed_matched_information_result_sha256": activation[
            "single_seed_matched_information_result_sha256"
        ],
        "evidence_entries": bundle["terminal_or_result_sha256"],
    }
    provenance = {
        **scientific_provenance,
        "activation_sha256": file_sha256(args.activation),
        "continuation_mode": continuation,
        "resume_checkpoint_sha256": activation["resume_checkpoint_sha256"],
        "prior_attempt_terminal_record_sha256": activation[
            "prior_attempt_terminal_record_sha256"
        ],
    }
    paths = {
        "transient": args.transient,
        "steady": args.steady,
        "public_split": args.public_split,
        "private_split": args.private_split,
        "train_audit_public": args.train_audit_public,
        "train_audit_private": args.train_audit_private,
        "public_overlap": args.public_overlap,
        "private_overlap": args.private_overlap,
        "steady_scope_config": args.steady_scope_config,
        "steady_exposure_config": args.steady_exposure_config,
    }
    if args.response_basis is not None:
        paths["response_basis"] = args.response_basis
    run_training(
        config,
        paths,
        activation,
        steady_scale,
        args.result,
        args.checkpoint_directory,
        provenance,
        args.resume_checkpoint,
        scientific_provenance,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
