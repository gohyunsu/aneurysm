"""Release-730 response-manifold plus local-residual development runner.

The runner implements two outcome-blind development stages. ``architecture``
compares a response-only decoder with a response-plus-local decoder under the
same GHD-GPS encoder and field objective. ``functional_finetune`` starts every
objective variant from the exact selected combined field-only checkpoint.
Only the frozen 584 training and 73 validation cases are readable here; the
locked test and 79 processed-only rows are never indexed.
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

from aurora.aneug_processed_v4_d13c_functional_finetune import (
    LOSS_TERMS,
    backward_case,
    train_wss_rms,
)
from aurora.aneug_processed_v4_d9 import field_loss, model_parameter_count
from aurora.aneug_release_730_ghd_gps_baseline import (
    Release730GHDGPSUNet,
    _to_device,
    extended_case_metrics,
    load_development_data,
)
from aurora.cycle_functional_alignment import complete_cycle_alignment_terms
from aurora.cycle_response_residual import SharedEncoderCycleResponseResidual
from aurora.release730_training_continuation import (
    capture_rng_state,
    validate_interrupted_attempt_record,
)


ARCHITECTURE_VARIANTS = ("response_only", "response_plus_residual")
FUNCTIONAL_VARIANTS = ("field_only", "all_scalarized", "all_field_anchored")
MODES = ("architecture", "functional_finetune")


class Release730ResponseLocalError(RuntimeError):
    """Raised when candidate evidence or an execution boundary is invalid."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730ResponseLocalError(reason)


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
        == "aurora.aneug_release_730_response_local_candidate.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_response_local_candidate_v1",
        "protocol_id",
    )
    _require(
        config.get("status")
        == "prepared_non_executable_until_oracle_and_direct_controls_terminal",
        "status",
    )
    source = config["source"]
    _require(
        source["dataset_revision"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36"
        and source["official_code_revision"]
        == "4a090a0f12538deef6fcea88b81afe78ce38152e"
        and source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae"
        and source["steady_norm_bytes"] == 9_632_510_050
        and source["steady_norm_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "source",
    )
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
    model = config["model"]
    _require(
        model["shared_encoder"] == "release730_GHD_conditioned_GINE_GPS_UNet"
        and (model["width"], model["attention_heads"], model["output_phases"])
        == (128, 4, 80)
        and model["rank_grid"] == [16, 32, 64, 128, 256]
        and model["rank_selected_in_config"] is False
        and model["rank_execution_rule"]
        == "lower_median_of_oracle_storage_aware_r1_nomination"
        and model["maximum_learned_response_ranks"] == 1
        and model["local_gate"]
        == "nodewise_phase_shared_sigmoid_from_shared_features"
        and model["basis_buffers_in_checkpoint"] is False
        and not model["hard_tangent_projection"]
        and not model["hard_periodic_closure"]
        and not model["hard_basis_projection"],
        "model",
    )
    cells = config["cells"]
    _require(
        cells["architecture"]
        == ["response_only__field_only", "response_plus_residual__field_only"]
        and cells["functional_finetune"]
        == [
            "response_plus_residual__field_only",
            "response_plus_residual__all_scalarized",
            "response_plus_residual__all_field_anchored",
        ]
        and cells["local_only_source"] == "release730_GHD_GPS_direct_comparator"
        and cells["oracle_rank_nomination_is_learned_performance"] is False
        and cells["selected_rank_fixed_before_candidate_validation"] is True
        and cells["one_cell_per_activation"] is True
        and cells["maximum_candidate_gpu_jobs_before_confirmation"] == 5,
        "cells",
    )
    objective = config["objective"]
    _require(
        objective["reference_tawss_floor_multiplier"] == 1e-4
        and objective["osi_pseudo_huber_delta"] == 0.02
        and objective["finetune_checkpoint_utility"]
        == "common_field_plus_mean_of_mean_vector_tawss_and_osi_for_every_objective_variant"
        and objective["functional_to_field_norm_ratio"] == 1.0
        and objective["rrt_loss"] is False
        and objective["separate_functional_head"] is False,
        "objective",
    )
    architecture = config["architecture_optimization"]
    _require(
        (
            architecture["seed"],
            architecture["maximum_epochs"],
            architecture["minimum_epochs"],
            architecture["early_stopping_patience"],
            architecture["gradient_accumulation_cases"],
            architecture["checkpoint_interval_epochs"],
        )
        == (1103, 251, 80, 40, 2, 10)
        and architecture["learning_rate"] == 3e-4
        and architecture["weight_decay"] == 1e-4
        and architecture["scheduler"] == "step_50_gamma_0p75"
        and architecture["selection"]
        == "lowest_validation_field_relative_l2_then_earliest_epoch",
        "architecture_optimization",
    )
    finetune = config["finetune_optimization"]
    _require(
        (
            finetune["seed"],
            finetune["maximum_epochs"],
            finetune["minimum_epochs"],
            finetune["early_stopping_patience"],
            finetune["gradient_accumulation_cases"],
            finetune["checkpoint_interval_epochs"],
        )
        == (1103, 60, 15, 12, 2, 10)
        and finetune["learning_rate"] == 1e-4
        and finetune["weight_decay"] == 1e-4
        and finetune["scheduler"] == "cosine_to_1e-6"
        and finetune["selection"]
        == "lowest_common_initial_checkpoint_endpoint_normalized_validation_utility_then_earliest_epoch",
        "finetune_optimization",
    )
    evaluation = config["evaluation"]
    _require(
        evaluation["common_report_space"]
        == "raw_released_physical_cartesian_wss"
        and "osi_coverage" in evaluation["secondary_metrics"]
        and "osi_area_coverage" not in evaluation["secondary_metrics"]
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
        and authorization["requires_response_oracle_terminal_and_basis"] is True
        and authorization["requires_GHD_GPS_and_Transolver_terminal_records"] is True
        and authorization["requires_fresh_private_activation"] is True
        and authorization["one_cell_per_activation"] is True
        and authorization[
            "genuine_infrastructure_interruption_exact_state_resume_allowed"
        ]
        is True
        and authorization["continuation_requires_checkpoint_and_terminal_hashes"]
        is True,
        "authorization",
    )
    for key in (
        "multi_seed_confirmation",
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


def validate_activation(
    path: str | Path,
    config: Mapping[str, Any],
    expected_commit: str,
    mode: str,
    architecture_variant: str,
    objective_variant: str,
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_response_local_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "single_seed_validation_development"
        and activation.get("authorized_mode") == mode
        and activation.get("architecture_variant") == architecture_variant
        and activation.get("objective_variant") == objective_variant,
        "activation_cell",
    )
    if mode == "architecture":
        _require(
            architecture_variant in ARCHITECTURE_VARIANTS
            and objective_variant == "field_only",
            "architecture_cell",
        )
    else:
        _require(
            architecture_variant == "response_plus_residual"
            and objective_variant in FUNCTIONAL_VARIANTS,
            "functional_cell",
        )
    rank = activation.get("selected_response_rank")
    _require(rank in config["model"]["rank_grid"], "selected_rank")
    for key in (
        "response_basis_sha256",
        "response_oracle_terminal_record_sha256",
        "ghd_gps_terminal_record_sha256",
        "transolver_terminal_record_sha256",
    ):
        _require(_is_sha256(activation.get(key)), f"activation_{key}")
    initial_hash = activation.get("initial_combined_field_checkpoint_sha256")
    _require(
        (_is_sha256(initial_hash) if mode == "functional_finetune" else initial_hash is None),
        "initial_checkpoint",
    )
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["split"]["train_audit_private_sha256"]
        and activation.get("read_locked_test_or_extra") is False,
        "activation_scope",
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


def _validate_bound_file(path: str | Path, expected_sha256: str, label: str) -> str:
    observed = file_sha256(path)
    _require(observed == expected_sha256, f"{label}_hash")
    return observed


def load_response_basis(
    path: str | Path,
    expected_sha256: str,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_bound_file(path, expected_sha256, "response_basis")
    payload = torch.load(str(path), map_location="cpu", weights_only=True)
    _require(
        isinstance(payload, Mapping)
        and payload.get("schema_version")
        == "aurora.private.aneug_release_730_response_basis.v1"
        and payload.get("protocol_id") == "aneug_release_730_response_oracle_v1"
        and payload.get("train_cases") == 584
        and payload.get("phases") == 80
        and payload.get("nodes") == 13_902
        and payload.get("case_ids_included") is False
        and payload.get("validation_loader_order_sha256")
        == config["split"]["validation_loader_order_sha256"],
        "response_basis_scope",
    )
    return dict(payload)


def configure_trainable_cell(
    model: SharedEncoderCycleResponseResidual, architecture_variant: str
) -> None:
    """Freeze heads that are outside the activated architecture cell."""

    _require(architecture_variant in ARCHITECTURE_VARIANTS, "architecture_variant")
    for parameter in model.parameters():
        parameter.requires_grad_(True)
    for parameter in model.single_field_head.parameters():
        parameter.requires_grad_(False)
    if architecture_variant == "response_only":
        for parameter in model.backbone.output.parameters():
            parameter.requires_grad_(False)
        for parameter in model.residual_gate_head.parameters():
            parameter.requires_grad_(False)


def active_parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


def alignment_terms(
    prediction: torch.Tensor,
    case: Mapping[str, torch.Tensor],
    config: Mapping[str, Any],
    reference_tawss_floor: float,
) -> dict[str, torch.Tensor]:
    phases = prediction.shape[0]
    phase_weights = torch.ones(phases, dtype=prediction.dtype, device=prediction.device)
    return complete_cycle_alignment_terms(
        prediction,
        case["wss"],
        phase_weights,
        case["vertex_weights"],
        {"field": 1.0, "mean_vector": 0.0, "tawss": 0.0, "osi": 0.0},
        reference_tawss_floor=reference_tawss_floor,
        osi_pseudo_huber_delta=float(config["objective"]["osi_pseudo_huber_delta"]),
    )


def _valid_support_osi(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    weights: torch.Tensor,
    reference_tawss_floor: float,
) -> tuple[float, float]:
    reference_tawss = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0)
    prediction_tawss = torch.linalg.vector_norm(prediction, dim=-1).mean(dim=0)
    support = reference_tawss > reference_tawss_floor
    support_weight = torch.sum(weights[support])
    _require(bool((support_weight > 0).item()), "osi_support")
    valid = support & torch.isfinite(prediction_tawss) & (prediction_tawss > 0)
    reference_mean = reference.mean(dim=0)
    prediction_mean = prediction.mean(dim=0)
    reference_osi = 0.5 * (
        1.0
        - torch.linalg.vector_norm(reference_mean, dim=-1)
        / torch.clamp(reference_tawss, min=1e-12)
    )
    prediction_osi = 0.5 * (
        1.0
        - torch.linalg.vector_norm(prediction_mean, dim=-1)
        / torch.clamp(prediction_tawss, min=1e-12)
    )
    error = torch.full_like(reference_osi, 0.5)
    error[valid] = torch.abs(prediction_osi[valid] - reference_osi[valid])
    mae = torch.sum(weights[support] * error[support]) / support_weight
    coverage = torch.sum(weights[valid]) / support_weight
    return float(mae.item()), float(coverage.item())


@torch.no_grad()
def evaluate(
    model: SharedEncoderCycleResponseResidual,
    cases: Sequence[Mapping[str, torch.Tensor]],
    config: Mapping[str, Any],
    architecture_variant: str,
    objective_variant: str,
    reference_tawss_floor: float,
    selection_normalizers: Mapping[str, float] | None,
    device: torch.device,
    *,
    compute_residual_diagnostics: bool = True,
) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    per_case_terms: list[dict[str, float]] = []
    for cpu_case in cases:
        case = _to_device(cpu_case, device)
        output = model(
            case,
            variant=architecture_variant,
            compute_residual_basis_leakage=compute_residual_diagnostics,
        )
        prediction = output["field"]
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
        # Keep the OSI error and its diagnostic coverage on the exact same
        # train-defined reference support.  ``extended_case_metrics`` emits a
        # legacy fixed-threshold ``osi_coverage`` value, so overwrite that
        # canonical key instead of introducing a second, inconsistent name.
        metrics["osi_coverage"] = coverage
        metrics["residual_basis_leakage"] = float(
            output["residual_basis_leakage"].item()
        )
        metrics["residual_gate_mean"] = float(output["residual_gate"].mean().item())
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
        utility = common_validation_utility(aggregate, selection_normalizers)
    return {
        "aggregate": aggregate,
        "aggregate_alignment_terms": aggregate_terms,
        "common_validation_utility": utility,
        "per_case_without_identifiers": per_case,
        "per_case_alignment_terms_without_identifiers": per_case_terms,
        "case_count": len(per_case),
    }


@torch.no_grad()
def compute_train_normalizers(
    model: SharedEncoderCycleResponseResidual,
    cases: Sequence[Mapping[str, torch.Tensor]],
    config: Mapping[str, Any],
    reference_tawss_floor: float,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    sums = {name: 0.0 for name in LOSS_TERMS}
    for cpu_case in cases:
        case = _to_device(cpu_case, device)
        prediction = model(
            case,
            variant="response_plus_residual",
            compute_residual_basis_leakage=False,
        )["field"]
        terms = alignment_terms(prediction, case, config, reference_tawss_floor)
        for name in LOSS_TERMS:
            sums[name] += float(terms[name].item())
    normalizers = {name: value / len(cases) for name, value in sums.items()}
    _require(
        all(math.isfinite(value) and value > 1e-12 for value in normalizers.values()),
        "train_normalizers",
    )
    return normalizers


def _selection_normalizers(initial_validation: Mapping[str, Any]) -> dict[str, float]:
    aggregate = initial_validation["aggregate"]
    result = {
        "field": float(aggregate["field_relative_l2"]),
        "mean_vector": float(aggregate["mean_vector_tawss_normalized_l2"]),
        "tawss": float(aggregate["tawss_normalized_absolute_error"]),
        "osi": float(aggregate["osi_mae"]),
    }
    _require(
        all(math.isfinite(value) and value > 1e-12 for value in result.values()),
        "selection_normalizers",
    )
    return result


def common_validation_utility(
    aggregate_metrics: Mapping[str, float],
    normalizers: Mapping[str, float],
) -> float:
    """Return the shared checkpoint utility for every functional fine-tune.

    Training objectives differ across the three fine-tunes, but checkpoint
    selection must not. All variants therefore use the same field endpoint
    plus the mean of the three functional endpoints, each divided by its value
    at the common initial combined checkpoint.
    """

    metric_keys = {
        "field": "field_relative_l2",
        "mean_vector": "mean_vector_tawss_normalized_l2",
        "tawss": "tawss_normalized_absolute_error",
        "osi": "osi_mae",
    }
    ratios: dict[str, float] = {}
    for name, metric_key in metric_keys.items():
        denominator = float(normalizers.get(name, math.nan))
        numerator = float(aggregate_metrics.get(metric_key, math.nan))
        _require(
            math.isfinite(denominator)
            and denominator > 1e-12
            and math.isfinite(numerator)
            and numerator >= 0.0,
            f"common_validation_utility_{name}",
        )
        ratios[name] = numerator / denominator
    value = ratios["field"] + (
        ratios["mean_vector"] + ratios["tawss"] + ratios["osi"]
    ) / 3.0
    _require(math.isfinite(value), "common_validation_utility")
    return value


def make_candidate_checkpoint(
    *,
    config: Mapping[str, Any],
    mode: str,
    architecture_variant: str,
    objective_variant: str,
    rank: int,
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
    elapsed_seconds_accumulated: float,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    _require(mode in MODES and architecture_variant in ARCHITECTURE_VARIANTS, "checkpoint_cell")
    _require(rank in config["model"]["rank_grid"], "checkpoint_rank")
    _require(epoch > 0 and optimizer_steps > 0 and 0 < best_epoch <= epoch, "checkpoint_progress")
    _require(stale_epochs >= 0 and len(history) == epoch, "checkpoint_history")
    _require(
        math.isfinite(selection_value)
        and math.isfinite(best_selection_value)
        and math.isfinite(reference_tawss_floor)
        and reference_tawss_floor > 0.0
        and math.isfinite(elapsed_seconds_accumulated)
        and elapsed_seconds_accumulated >= 0.0,
        "checkpoint_finite",
    )
    return {
        "schema_version": "aurora.private.aneug_release_730_response_local_checkpoint.v1",
        "protocol_id": config["protocol_id"],
        "mode": mode,
        "architecture_variant": architecture_variant,
        "objective_variant": objective_variant,
        "selected_response_rank": rank,
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
        "elapsed_seconds_accumulated": elapsed_seconds_accumulated,
        "rng_state": capture_rng_state(),
        **dict(provenance),
    }


def restore_candidate_checkpoint(
    path: str | Path,
    *,
    config: Mapping[str, Any],
    expected_provenance: Mapping[str, Any],
    mode: str,
    architecture_variant: str,
    objective_variant: str,
    rank: int,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    maximum_epochs: int,
) -> dict[str, Any]:
    payload = torch.load(str(path), map_location="cpu", weights_only=True)
    _require(isinstance(payload, Mapping), "checkpoint_mapping")
    _require(
        payload.get("schema_version")
        == "aurora.private.aneug_release_730_response_local_checkpoint.v1"
        and payload.get("protocol_id") == config["protocol_id"]
        and payload.get("mode") == mode
        and payload.get("architecture_variant") == architecture_variant
        and payload.get("objective_variant") == objective_variant
        and payload.get("selected_response_rank") == rank,
        "checkpoint_identity",
    )
    for key, value in expected_provenance.items():
        _require(payload.get(key) == value, f"checkpoint_provenance_{key}")
    epoch = int(payload.get("epoch", -1))
    best_epoch = int(payload.get("best_epoch", -1))
    _require(0 < epoch <= maximum_epochs and 0 < best_epoch <= epoch, "checkpoint_progress")
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


def load_initial_combined_checkpoint(
    path: str | Path,
    expected_sha256: str,
    model: SharedEncoderCycleResponseResidual,
    rank: int,
    expected_basis_sha256: str,
) -> dict[str, Any]:
    _validate_bound_file(path, expected_sha256, "initial_checkpoint")
    payload = torch.load(str(path), map_location="cpu", weights_only=True)
    _require(
        isinstance(payload, Mapping)
        and payload.get("schema_version")
        == "aurora.private.aneug_release_730_response_local_best.v1"
        and payload.get("mode") == "architecture"
        and payload.get("architecture_variant") == "response_plus_residual"
        and payload.get("objective_variant") == "field_only"
        and payload.get("selected_response_rank") == rank
        and payload.get("response_basis_sha256") == expected_basis_sha256,
        "initial_checkpoint_scope",
    )
    model.load_state_dict(payload["model_state_dict"], strict=True)
    return dict(payload)


def _build_optimizer_and_scheduler(
    model: nn.Module, optimization: Mapping[str, Any], mode: str
) -> tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.LRScheduler]:
    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    _require(bool(parameters), "trainable_parameters")
    optimizer = torch.optim.AdamW(
        parameters,
        lr=float(optimization["learning_rate"]),
        weight_decay=float(optimization["weight_decay"]),
    )
    if mode == "architecture":
        scheduler: torch.optim.lr_scheduler.LRScheduler = torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=int(optimization["step_size_epochs"]),
            gamma=float(optimization["gamma"]),
        )
    else:
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=int(optimization["maximum_epochs"]),
            eta_min=float(optimization["minimum_learning_rate"]),
        )
    return optimizer, scheduler


def run_development(
    config: Mapping[str, Any],
    paths: Mapping[str, Path],
    activation: Mapping[str, Any],
    mode: str,
    architecture_variant: str,
    objective_variant: str,
    result_path: Path,
    checkpoint_directory: Path,
    provenance: Mapping[str, Any],
    resume_checkpoint: Path | None = None,
    resume_expected_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    optimization = config[
        "architecture_optimization" if mode == "architecture" else "finetune_optimization"
    ]
    rank = int(activation["selected_response_rank"])
    seed = int(optimization["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(4)
    device = torch.device("cuda")
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    train, validation, topology, wss_scale = load_development_data(
        config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
    )
    basis_payload = load_response_basis(
        paths["response_basis"], activation["response_basis_sha256"], config
    )
    backbone = Release730GHDGPSUNet(
        topology,
        width=int(config["model"]["width"]),
        heads=int(config["model"]["attention_heads"]),
    )
    model = SharedEncoderCycleResponseResidual(
        backbone,
        basis_payload,
        rank=rank,
        local_output_scale=wss_scale,
    ).to(device)
    if mode == "functional_finetune":
        load_initial_combined_checkpoint(
            paths["initial_checkpoint"],
            activation["initial_combined_field_checkpoint_sha256"],
            model,
            rank,
            activation["response_basis_sha256"],
        )
    configure_trainable_cell(model, architecture_variant)
    reference_tawss_floor = train_wss_rms(train) * float(
        config["objective"]["reference_tawss_floor_multiplier"]
    )
    initial_validation = None
    train_term_normalizers = None
    selection_endpoint_normalizers = None
    if mode == "functional_finetune":
        train_term_normalizers = compute_train_normalizers(
            model, train, config, reference_tawss_floor, device
        )
        initial_validation = evaluate(
            model,
            validation,
            config,
            architecture_variant,
            objective_variant,
            reference_tawss_floor,
            None,
            device,
        )
        selection_endpoint_normalizers = _selection_normalizers(initial_validation)
    optimizer, scheduler = _build_optimizer_and_scheduler(model, optimization, mode)
    maximum_epochs = int(optimization["maximum_epochs"])
    minimum_epochs = int(optimization["minimum_epochs"])
    patience = int(optimization["early_stopping_patience"])
    accumulation = int(optimization["gradient_accumulation_cases"])
    checkpoint_interval = int(optimization["checkpoint_interval_epochs"])
    ratio = float(config["objective"]["functional_to_field_norm_ratio"])
    checkpoint_directory.mkdir(parents=True, exist_ok=True)
    _require(not any(checkpoint_directory.iterdir()), "checkpoint_directory_not_empty")

    start_epoch = 0
    optimizer_steps = 0
    best_selection = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, Any]] = []
    elapsed_seconds_prior = 0.0
    resumed_from_epoch: int | None = None
    selection_name = (
        "validation_field_relative_l2"
        if mode == "architecture"
        else "common_initial_checkpoint_endpoint_normalized_validation_utility"
    )
    if resume_checkpoint is None:
        smoke_case = _to_device(train[0], device)
        smoke_output = model(
            smoke_case,
            variant=architecture_variant,
            compute_residual_basis_leakage=False,
        )
        if mode == "architecture":
            smoke_loss = field_loss(
                smoke_output["field"], smoke_case["wss"], smoke_case["vertex_weights"]
            )
            smoke_diagnostic: dict[str, Any] = {
                "scalarized_value": float(smoke_loss.detach().item()),
                "projection_applied": False,
                "gradient_conflict_measured": False,
            }
            smoke_loss.backward()
        else:
            _require(train_term_normalizers is not None, "functional_normalizers")
            smoke_terms = alignment_terms(
                smoke_output["field"], smoke_case, config, reference_tawss_floor
            )
            smoke_diagnostic = backward_case(
                model,
                smoke_terms,
                train_term_normalizers,
                objective_variant,
                1,
                ratio,
            )
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
            "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        }
        del smoke_case, smoke_output
    else:
        _require(resume_expected_provenance is not None, "resume_provenance")
        restored = restore_candidate_checkpoint(
            resume_checkpoint,
            config=config,
            expected_provenance=resume_expected_provenance,
            mode=mode,
            architecture_variant=architecture_variant,
            objective_variant=objective_variant,
            rank=rank,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            maximum_epochs=maximum_epochs,
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
        elapsed_seconds_prior = float(restored["elapsed_seconds_accumulated"])
        _require(
            restored["train_term_normalizers"] == train_term_normalizers
            and restored["selection_endpoint_normalizers"]
            == selection_endpoint_normalizers
            and math.isclose(
                float(restored["reference_tawss_floor"]),
                reference_tawss_floor,
                rel_tol=0.0,
                abs_tol=1e-12,
            ),
            "resume_normalizers",
        )

    training_epochs = (
        range(start_epoch, start_epoch)
        if start_epoch >= minimum_epochs and stale >= patience
        else range(start_epoch, maximum_epochs)
    )
    for epoch in training_epochs:
        model.train()
        order = list(range(len(train)))
        random.Random(seed + epoch).shuffle(order)
        optimizer.zero_grad(set_to_none=True)
        epoch_objective = 0.0
        conflicts = 0
        cosine_sum = 0.0
        for step, index in enumerate(order):
            case = _to_device(train[index], device)
            prediction = model(
                case,
                variant=architecture_variant,
                compute_residual_basis_leakage=False,
            )["field"]
            if mode == "architecture":
                objective = field_loss(prediction, case["wss"], case["vertex_weights"])
                _require(bool(torch.isfinite(objective).item()), "training_loss")
                (objective / accumulation).backward()
                diagnostic = {
                    "scalarized_value": float(objective.detach().item()),
                    "projection_applied": False,
                    "gradient_cosine_before": 0.0,
                }
            else:
                _require(train_term_normalizers is not None, "functional_normalizers")
                terms = alignment_terms(prediction, case, config, reference_tawss_floor)
                diagnostic = backward_case(
                    model,
                    terms,
                    train_term_normalizers,
                    objective_variant,
                    accumulation,
                    ratio,
                )
            epoch_objective += float(diagnostic["scalarized_value"])
            conflicts += int(bool(diagnostic["projection_applied"]))
            cosine_sum += float(diagnostic["gradient_cosine_before"])
            if (step + 1) % accumulation == 0:
                torch.nn.utils.clip_grad_norm_(
                    [parameter for parameter in model.parameters() if parameter.requires_grad],
                    float(optimization["gradient_clip_norm"]),
                )
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_steps += 1
        _require(len(order) % accumulation == 0, "incomplete_effective_batch")
        scheduler.step()
        validation_result = evaluate(
            model,
            validation,
            config,
            architecture_variant,
            objective_variant,
            reference_tawss_floor,
            selection_endpoint_normalizers,
            device,
            compute_residual_diagnostics=False,
        )
        validation_field = float(validation_result["aggregate"]["field_relative_l2"])
        selection_value = (
            validation_field
            if mode == "architecture"
            else float(validation_result["common_validation_utility"])
        )
        row: dict[str, Any] = {
            "epoch": epoch + 1,
            "optimizer_steps": optimizer_steps,
            "training_objective": epoch_objective / len(order),
            "selection_value": selection_value,
            "validation_field_relative_l2": validation_field,
            "validation_tawss_error": float(
                validation_result["aggregate"]["tawss_normalized_absolute_error"]
            ),
            "validation_osi_mae": float(validation_result["aggregate"]["osi_mae"]),
            "gradient_conflict_fraction": (
                conflicts / len(order) if objective_variant == "all_field_anchored" else None
            ),
            "mean_gradient_cosine_before": (
                cosine_sum / len(order)
                if objective_variant == "all_field_anchored"
                else None
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
                make_candidate_checkpoint(
                    config=config,
                    mode=mode,
                    architecture_variant=architecture_variant,
                    objective_variant=objective_variant,
                    rank=rank,
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
                    train_term_normalizers=train_term_normalizers,
                    selection_endpoint_normalizers=selection_endpoint_normalizers,
                    reference_tawss_floor=reference_tawss_floor,
                    elapsed_seconds_accumulated=(
                        elapsed_seconds_prior + time.monotonic() - started
                    ),
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
        architecture_variant,
        objective_variant,
        reference_tawss_floor,
        selection_endpoint_normalizers,
        device,
    )
    best_checkpoint = {
        "schema_version": "aurora.private.aneug_release_730_response_local_best.v1",
        "protocol_id": config["protocol_id"],
        "mode": mode,
        "architecture_variant": architecture_variant,
        "objective_variant": objective_variant,
        "selected_response_rank": rank,
        "seed": seed,
        "best_epoch": best_epoch,
        "selection_name": selection_name,
        "best_selection_value": best_selection,
        "model_state_dict": best_state,
        "response_basis_embedded": False,
        "train_term_normalizers": train_term_normalizers,
        "selection_endpoint_normalizers": selection_endpoint_normalizers,
        "reference_tawss_floor": reference_tawss_floor,
        **dict(provenance),
    }
    _strict_atomic_torch_save(checkpoint_directory / "best.pt", best_checkpoint)
    result = {
        "schema_version": "aurora.private.aneug_release_730_response_local_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "mode": mode,
        "architecture_variant": architecture_variant,
        "objective_variant": objective_variant,
        "selected_response_rank": rank,
        "seed": seed,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "optimizer_steps": optimizer_steps,
        "selection_name": selection_name,
        "best_selection_value": best_selection,
        "parameter_count": model_parameter_count(model),
        "active_parameter_count": active_parameter_count(model),
        "elapsed_seconds": elapsed_seconds_prior + time.monotonic() - started,
        "continuation_mode": resume_checkpoint is not None,
        "resumed_from_epoch": resumed_from_epoch,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "train_physical_vector_rms_scale": wss_scale,
        "reference_tawss_floor": reference_tawss_floor,
        "train_term_normalizers": train_term_normalizers,
        "selection_endpoint_normalizers": selection_endpoint_normalizers,
        "smoke": smoke,
        "initial_validation": initial_validation,
        "validation": final_validation,
        "history": history,
        "train_case_count": len(train),
        "validation_case_count": len(validation),
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "hard_tangent_projection": False,
        "hard_periodic_closure": False,
        "case_ids_included": False,
        "development_only": True,
        "paper_performance_claim": False,
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
    parser.add_argument("--mode", choices=MODES)
    parser.add_argument("--architecture-variant", choices=ARCHITECTURE_VARIANTS)
    parser.add_argument("--objective-variant", choices=FUNCTIONAL_VARIANTS)
    parser.add_argument("--response-oracle-terminal-record", type=Path)
    parser.add_argument("--ghd-gps-terminal-record", type=Path)
    parser.add_argument("--transolver-terminal-record", type=Path)
    parser.add_argument("--response-basis", type=Path)
    parser.add_argument("--initial-combined-field-checkpoint", type=Path)
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
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
        args.mode,
        args.architecture_variant,
        args.objective_variant,
        args.response_oracle_terminal_record,
        args.ghd_gps_terminal_record,
        args.transolver_terminal_record,
        args.response_basis,
        args.transient,
        args.steady,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.result,
        args.checkpoint_directory,
    )
    _require(all(value is not None for value in required), "execution_arguments")
    activation = validate_activation(
        args.activation,
        config,
        args.expected_commit,
        args.mode,
        args.architecture_variant,
        args.objective_variant,
    )
    _require(
        (args.initial_combined_field_checkpoint is not None)
        is (args.mode == "functional_finetune"),
        "initial_checkpoint_argument",
    )
    continuation_mode = args.resume_checkpoint is not None
    _require(activation["continuation_mode"] is continuation_mode, "continuation_mode_mismatch")
    if continuation_mode:
        _require(args.prior_attempt_terminal_record is not None, "prior_terminal_required")
        validate_interrupted_attempt_record(
            args.prior_attempt_terminal_record,
            activation["prior_attempt_terminal_record_sha256"],
        )
        _validate_bound_file(
            args.resume_checkpoint, activation["resume_checkpoint_sha256"], "resume_checkpoint"
        )
    else:
        _require(args.prior_attempt_terminal_record is None, "unexpected_prior_terminal")
    for path, key, label in (
        (
            args.response_oracle_terminal_record,
            "response_oracle_terminal_record_sha256",
            "response_oracle_terminal",
        ),
        (args.ghd_gps_terminal_record, "ghd_gps_terminal_record_sha256", "ghd_gps_terminal"),
        (
            args.transolver_terminal_record,
            "transolver_terminal_record_sha256",
            "transolver_terminal",
        ),
    ):
        _validate_bound_file(path, activation[key], label)
    scientific_provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "processed_v5_sha256": config["source"]["processed_v5_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        "validation_case_digest": config["split"]["validation_case_digest"],
        "validation_loader_order_sha256": config["split"]["validation_loader_order_sha256"],
        "response_basis_sha256": activation["response_basis_sha256"],
        "response_oracle_terminal_record_sha256": activation[
            "response_oracle_terminal_record_sha256"
        ],
        "ghd_gps_terminal_record_sha256": activation["ghd_gps_terminal_record_sha256"],
        "transolver_terminal_record_sha256": activation[
            "transolver_terminal_record_sha256"
        ],
        "initial_combined_field_checkpoint_sha256": activation[
            "initial_combined_field_checkpoint_sha256"
        ],
    }
    provenance = {
        **scientific_provenance,
        "activation_sha256": file_sha256(args.activation),
        "continuation_mode": continuation_mode,
        "resume_checkpoint_sha256": activation["resume_checkpoint_sha256"],
        "prior_attempt_terminal_record_sha256": activation[
            "prior_attempt_terminal_record_sha256"
        ],
    }
    paths = {
        "response_basis": args.response_basis,
        "transient": args.transient,
        "steady": args.steady,
        "public_split": args.public_split,
        "private_split": args.private_split,
        "train_audit_public": args.train_audit_public,
        "train_audit_private": args.train_audit_private,
    }
    if args.initial_combined_field_checkpoint is not None:
        paths["initial_checkpoint"] = args.initial_combined_field_checkpoint
    run_development(
        config,
        paths,
        activation,
        args.mode,
        args.architecture_variant,
        args.objective_variant,
        args.result,
        args.checkpoint_directory,
        provenance,
        args.resume_checkpoint,
        scientific_provenance,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
