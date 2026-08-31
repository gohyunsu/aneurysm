"""Execute one fixed-budget, validation-only ICCE supervision cell.

The runner intentionally has no test or processed-extra path.  It reuses the
release-730 loader/evaluator and common GHD/GPS backbone, but replaces validation-
selected early stopping with one prespecified final checkpoint.  The six methods
therefore receive the exact exposure counts registered in the ICCE v2 protocol.
"""

from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from aurora.aneug_processed_v4_d13c_functional_finetune import train_wss_rms
from aurora.aneug_processed_v4_d9 import field_loss, model_parameter_count
from aurora.aneug_release_730_ghd_cross_regime_transfer import (
    Release730GHDSharedDecoderSteadyControl,
    Release730GHDSteadyTransferModel,
    shared_decoder_cross_regime_backward_with_decoder_diagnostic,
)
from aurora.aneug_release_730_ghd_gps_baseline import (
    Release730GHDGPSUNet,
    _to_device,
    load_development_data,
)
from aurora.aneug_release_730_icce_revision import (
    METHOD_REGIME_SEPARATED,
    METHOD_SHARED_DECODER,
    METHOD_SHUFFLED_STEADY,
    METHOD_STEADY_THEN_TRANSIENT,
    METHOD_TRANSIENT_MEAN,
    METHOD_TRANSIENT_ONLY,
    TRAINING_SEEDS,
    deterministic_shuffled_target_map,
    expected_exposure_ledger,
    shuffled_target_map_digest,
    summarize_gradient_cosines,
    validate_exposure_result,
    validate_partition_boundary,
    validate_protocol_config,
)
from aurora.aneug_release_730_label_efficiency import balanced_epoch_indices
from aurora.aneug_release_730_matched_steady_stream import (
    ExposureDigest,
    epoch_exposure_indices,
    single_field_relative_squared_error,
)
from aurora.aneug_release_730_matched_training import (
    _build_steady_stream,
    _strict_atomic_json,
    _strict_atomic_torch_save,
    evaluate,
    file_sha256,
)
from aurora.aneug_release_730_single_field_auxiliary import (
    train_cycle_mean_wss_rms,
    transient_mean_auxiliary_case,
)
from aurora.release730_training_continuation import capture_rng_state


class ICCEFixedBudgetError(RuntimeError):
    """Raised when execution departs from the fixed-budget cell contract."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCEFixedBudgetError(reason)


def _state_dict_cpu(model: nn.Module) -> dict[str, torch.Tensor]:
    return {
        name: value.detach().cpu().clone()
        for name, value in model.state_dict().items()
    }


def _parameter_partition(
    model: nn.Module, method_id: str
) -> tuple[tuple[nn.Parameter, ...], tuple[nn.Parameter, ...], tuple[nn.Parameter, ...]]:
    """Return shared encoder, cycle decoder, and auxiliary-head parameters."""

    if method_id == METHOD_SHARED_DECODER:
        backbone = model.backbone
        cycle = tuple(backbone.output.parameters())
        cycle_ids = {id(parameter) for parameter in cycle}
        shared = tuple(
            parameter
            for parameter in backbone.parameters()
            if id(parameter) not in cycle_ids
        )
        auxiliary: tuple[nn.Parameter, ...] = ()
    else:
        shared = tuple(model.shared_encoder_parameters())
        cycle = tuple(model.cycle_decoder_parameters())
        auxiliary = tuple(model.auxiliary_head_parameters())
    _require(bool(shared) and bool(cycle), "model_parameter_partition")
    ids = [
        {id(parameter) for parameter in shared},
        {id(parameter) for parameter in cycle},
        {id(parameter) for parameter in auxiliary},
    ]
    _require(
        ids[0].isdisjoint(ids[1])
        and ids[0].isdisjoint(ids[2])
        and ids[1].isdisjoint(ids[2]),
        "model_parameter_overlap",
    )
    return shared, cycle, auxiliary


def _set_trainable(model: nn.Module, parameters: Sequence[nn.Parameter]) -> None:
    active_ids = {id(parameter) for parameter in parameters}
    _require(bool(active_ids), "trainable_parameters")
    for parameter in model.parameters():
        parameter.requires_grad_(id(parameter) in active_ids)


def _optimizer_scheduler(
    parameters: Sequence[nn.Parameter], optimization: Mapping[str, Any]
) -> tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.LRScheduler]:
    optimizer = torch.optim.AdamW(
        tuple(parameters),
        lr=float(optimization["learning_rate"]),
        weight_decay=float(optimization["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=int(optimization["step_size_epochs"]),
        gamma=float(optimization["gamma"]),
    )
    return optimizer, scheduler


RECOVERY_CHECKPOINT_SCHEMA = (
    "aurora.private.aneug_release_730_icce_fixed_budget_recovery.v2"
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _restore_rng_state(payload: Mapping[str, Any]) -> None:
    _require(isinstance(payload, Mapping), "recovery_rng")
    random.setstate(payload["python_random_state"])
    torch.set_rng_state(payload["torch_rng_state"])
    cuda_states = payload.get("cuda_rng_state_all", [])
    if torch.cuda.is_available():
        _require(bool(cuda_states), "recovery_cuda_rng")
        torch.cuda.set_rng_state_all(cuda_states)
    else:
        _require(cuda_states == [], "recovery_cpu_rng")


def _rebuild_steady_exposure_digests(
    *,
    method_id: str,
    eligible_indices: Sequence[int],
    steady_seed: int,
    exposures_per_epoch: int,
    completed_pretraining_epochs: int,
    completed_transient_epochs: int,
    shuffled_targets: Mapping[int, int] | None,
) -> tuple[ExposureDigest, ExposureDigest]:
    """Rebuild deterministic source/target prefixes without reading a WSS field."""

    source = ExposureDigest()
    target = ExposureDigest()
    if method_id == METHOD_STEADY_THEN_TRANSIENT:
        epochs = completed_pretraining_epochs
    elif method_id in {
        METHOD_REGIME_SEPARATED,
        METHOD_SHARED_DECODER,
        METHOD_SHUFFLED_STEADY,
    }:
        epochs = completed_transient_epochs
    else:
        epochs = 0
    for epoch in range(epochs):
        for steady_index in epoch_exposure_indices(
            eligible_indices,
            epoch=epoch,
            cases_per_epoch=exposures_per_epoch,
            seed=steady_seed,
        ):
            source.update(int(steady_index))
            if shuffled_targets is not None:
                target.update(int(shuffled_targets[int(steady_index)]))
    return source, target


def _make_recovery_checkpoint(
    *,
    revision_config: Mapping[str, Any],
    method_id: str,
    training_seed: int,
    auxiliary_coefficient: float,
    stage: str,
    completed_pretraining_epochs: int,
    completed_transient_epochs: int,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    smoke: Mapping[str, Any],
    pretraining_history: Sequence[Mapping[str, Any]],
    history: Sequence[Mapping[str, Any]],
    shared_decoder_cosines: Sequence[float],
    pretraining_optimizer_updates: int,
    transient_optimizer_updates: int,
    transient_exposures: int,
    auxiliary_exposures: int,
    steady_exposure: ExposureDigest,
    shuffled_target_exposure: ExposureDigest,
    cycle_output_scale: float,
    auxiliary_output_scale: float,
    reference_tawss_floor: float,
    elapsed_seconds_accumulated: float,
    peak_gpu_memory_bytes: int,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    reference_epochs = int(revision_config["reference_epochs"])
    exposures_per_epoch = int(
        revision_config["transient_exposures_per_reference_epoch"]
    )
    _require(
        stage in {"steady_pretraining", "transient_training"}
        and 0 <= completed_pretraining_epochs <= reference_epochs
        and 0 <= completed_transient_epochs <= reference_epochs
        and len(pretraining_history) == completed_pretraining_epochs
        and len(history) == completed_transient_epochs,
        "recovery_progress",
    )
    _require(
        (method_id == METHOD_STEADY_THEN_TRANSIENT)
        == (completed_pretraining_epochs > 0)
        and (
            stage != "transient_training"
            or method_id != METHOD_STEADY_THEN_TRANSIENT
            or completed_pretraining_epochs == reference_epochs
        ),
        "recovery_stage",
    )
    expected_transient = completed_transient_epochs * exposures_per_epoch
    if method_id == METHOD_TRANSIENT_ONLY:
        expected_auxiliary = 0
    elif method_id == METHOD_STEADY_THEN_TRANSIENT:
        expected_auxiliary = completed_pretraining_epochs * exposures_per_epoch
    else:
        expected_auxiliary = completed_transient_epochs * exposures_per_epoch
    _require(
        transient_exposures == expected_transient
        and auxiliary_exposures == expected_auxiliary
        and steady_exposure.count
        == (
            expected_auxiliary
            if method_id
            in {
                METHOD_REGIME_SEPARATED,
                METHOD_SHARED_DECODER,
                METHOD_SHUFFLED_STEADY,
                METHOD_STEADY_THEN_TRANSIENT,
            }
            else 0
        )
        and math.isfinite(elapsed_seconds_accumulated)
        and elapsed_seconds_accumulated >= 0.0
        and peak_gpu_memory_bytes >= 0,
        "recovery_accounting",
    )
    return {
        "schema_version": RECOVERY_CHECKPOINT_SCHEMA,
        "protocol_id": revision_config["protocol_id"],
        "method_id": method_id,
        "training_seed": training_seed,
        "auxiliary_coefficient": auxiliary_coefficient,
        "stage": stage,
        "completed_steady_pretraining_epochs": completed_pretraining_epochs,
        "completed_transient_epochs": completed_transient_epochs,
        "model_state_dict": _state_dict_cpu(model),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict(),
        "smoke": dict(smoke),
        "pretraining_history": [dict(row) for row in pretraining_history],
        "history": [dict(row) for row in history],
        "shared_decoder_cosines": [float(value) for value in shared_decoder_cosines],
        "pretraining_optimizer_updates": pretraining_optimizer_updates,
        "transient_optimizer_updates": transient_optimizer_updates,
        "transient_exposures": transient_exposures,
        "auxiliary_exposures": auxiliary_exposures,
        "steady_exposure_prefix_sha256": (
            steady_exposure.hexdigest() if steady_exposure.count else None
        ),
        "shuffled_target_exposure_prefix_sha256": (
            shuffled_target_exposure.hexdigest()
            if shuffled_target_exposure.count
            else None
        ),
        "cycle_output_scale": cycle_output_scale,
        "auxiliary_output_scale": auxiliary_output_scale,
        "reference_tawss_floor": reference_tawss_floor,
        "elapsed_seconds_accumulated": elapsed_seconds_accumulated,
        "peak_gpu_memory_bytes": peak_gpu_memory_bytes,
        "rng_state": capture_rng_state(),
        **dict(provenance),
    }


def _restore_recovery_checkpoint(
    path: Path,
    *,
    revision_config: Mapping[str, Any],
    method_id: str,
    training_seed: int,
    auxiliary_coefficient: float,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    expected_provenance: Mapping[str, Any],
) -> dict[str, Any]:
    payload = torch.load(str(path), map_location="cpu", weights_only=True)
    _require(isinstance(payload, Mapping), "recovery_mapping")
    _require(
        payload.get("schema_version") == RECOVERY_CHECKPOINT_SCHEMA
        and payload.get("protocol_id") == revision_config["protocol_id"]
        and payload.get("method_id") == method_id
        and payload.get("training_seed") == training_seed
        and math.isclose(
            float(payload.get("auxiliary_coefficient", math.nan)),
            auxiliary_coefficient,
            rel_tol=0.0,
            abs_tol=0.0,
        ),
        "recovery_identity",
    )
    for key, value in expected_provenance.items():
        _require(payload.get(key) == value, f"recovery_provenance_{key}")
    stage = payload.get("stage")
    pretraining_epochs = int(payload.get("completed_steady_pretraining_epochs", -1))
    transient_epochs = int(payload.get("completed_transient_epochs", -1))
    _require(
        stage in {"steady_pretraining", "transient_training"}
        and 0 <= pretraining_epochs <= int(revision_config["reference_epochs"])
        and 0 <= transient_epochs <= int(revision_config["reference_epochs"])
        and isinstance(payload.get("pretraining_history"), list)
        and len(payload["pretraining_history"]) == pretraining_epochs
        and isinstance(payload.get("history"), list)
        and len(payload["history"]) == transient_epochs
        and isinstance(payload.get("model_state_dict"), Mapping)
        and isinstance(payload.get("optimizer_state_dict"), Mapping)
        and isinstance(payload.get("scheduler_state_dict"), Mapping),
        "recovery_payload",
    )
    model.load_state_dict(payload["model_state_dict"], strict=True)
    optimizer.load_state_dict(payload["optimizer_state_dict"])
    scheduler.load_state_dict(payload["scheduler_state_dict"])
    _restore_rng_state(payload["rng_state"])
    return dict(payload)


def _transient_epoch_order(
    *, train_count: int, training_seed: int, epoch: int, exposures: int
) -> tuple[int, ...]:
    if train_count == exposures:
        values = list(range(train_count))
        random.Random(training_seed + epoch).shuffle(values)
        return tuple(values)
    return tuple(
        balanced_epoch_indices(
            train_count,
            training_seed=training_seed,
            epoch=epoch,
            exposures=exposures,
        )
    )


def _build_model(
    *,
    method_id: str,
    topology: Mapping[str, torch.Tensor],
    cycle_output_scale: float,
    auxiliary_output_scale: float,
) -> nn.Module:
    backbone = Release730GHDGPSUNet(topology, width=128, heads=4)
    if method_id == METHOD_SHARED_DECODER:
        return Release730GHDSharedDecoderSteadyControl(
            backbone, cycle_output_scale=cycle_output_scale
        )
    return Release730GHDSteadyTransferModel(
        backbone,
        cycle_output_scale=cycle_output_scale,
        auxiliary_output_scale=auxiliary_output_scale,
    )


def _training_smoke(
    *,
    model: nn.Module,
    method_id: str,
    train_case: Mapping[str, torch.Tensor],
    steady_case: Mapping[str, torch.Tensor] | None,
    auxiliary_coefficient: float,
    shared: Sequence[nn.Parameter],
    cycle: Sequence[nn.Parameter],
    auxiliary: Sequence[nn.Parameter],
) -> dict[str, Any]:
    model.zero_grad(set_to_none=True)
    cycle_loss = field_loss(
        model.forward_cycle(train_case),
        train_case["wss"],
        train_case["vertex_weights"],
    )
    if method_id == METHOD_TRANSIENT_ONLY:
        cycle_loss.backward()
        diagnostic = None
    elif method_id == METHOD_TRANSIENT_MEAN:
        target = transient_mean_auxiliary_case(train_case)
        auxiliary_loss = single_field_relative_squared_error(
            model.forward_single_field(target),
            target["single_field_wss"],
            target["vertex_weights"],
        )
        (cycle_loss + auxiliary_coefficient * auxiliary_loss).backward()
        diagnostic = None
    else:
        _require(steady_case is not None, "steady_smoke_case")
        auxiliary_loss = single_field_relative_squared_error(
            model.forward_single_field(steady_case),
            steady_case["steady_wss"],
            steady_case["vertex_weights"],
        )
        if method_id == METHOD_SHARED_DECODER:
            diagnostic = shared_decoder_cross_regime_backward_with_decoder_diagnostic(
                transient_loss=cycle_loss,
                auxiliary_loss=auxiliary_loss,
                optimization_parameters=tuple(shared) + tuple(cycle),
                diagnostic_decoder_parameters=cycle,
                auxiliary_coefficient=auxiliary_coefficient,
            )
        elif method_id == METHOD_STEADY_THEN_TRANSIENT:
            auxiliary_loss.backward()
            diagnostic = None
        else:
            (cycle_loss + auxiliary_coefficient * auxiliary_loss).backward()
            diagnostic = None
    _require(
        all(
            parameter.grad is None
            or bool(torch.isfinite(parameter.grad).all().item())
            for parameter in model.parameters()
        ),
        "smoke_gradients",
    )
    model.zero_grad(set_to_none=True)
    return {
        "finite_forward_backward": True,
        "decoder_only_gradient_diagnostic": diagnostic,
    }


def run_fixed_budget_cell(
    *,
    matched_config: Mapping[str, Any],
    revision_config: Mapping[str, Any],
    paths: Mapping[str, Path],
    method_id: str,
    training_seed: int,
    auxiliary_coefficient: float,
    steady_output_scale: float,
    result_path: Path,
    checkpoint_path: Path,
    provenance: Mapping[str, Any],
    train_subset_case_ids: Sequence[str] | None = None,
    train_subset_digest: str | None = None,
    prediction_directory: Path | None = None,
    recovery_checkpoint_directory: Path | None = None,
    resume_checkpoint: Path | None = None,
    resume_expected_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run one method/seed cell and write identifier-free final evidence."""

    _require(torch.cuda.is_available(), "cuda_required")
    validate_protocol_config(revision_config)
    _require(training_seed in TRAINING_SEEDS, "training_seed")
    _require(
        math.isfinite(auxiliary_coefficient) and auxiliary_coefficient > 0.0,
        "auxiliary_coefficient",
    )
    _require(
        math.isfinite(steady_output_scale) and steady_output_scale > 0.0,
        "steady_output_scale",
    )
    random.seed(training_seed)
    torch.manual_seed(training_seed)
    torch.cuda.manual_seed_all(training_seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(4)
    device = torch.device("cuda")
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()

    train, validation, topology, cycle_output_scale = load_development_data(
        matched_config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
        train_subset_case_ids,
    )
    _require(len(train) in {58, 146, 292, 584}, "train_count")
    _require(len(validation) == 73, "validation_count")
    _require(
        (train_subset_case_ids is None and train_subset_digest is None)
        or (
            train_subset_case_ids is not None
            and isinstance(train_subset_digest, str)
            and len(train_subset_digest) == 64
        ),
        "train_subset_digest",
    )
    reference_epochs = int(revision_config["reference_epochs"])
    exposures_per_epoch = int(
        revision_config["transient_exposures_per_reference_epoch"]
    )
    ledger = expected_exposure_ledger(
        method_id,
        unique_transient_cases=len(train),
        reference_epochs=reference_epochs,
        transient_exposures_per_epoch=exposures_per_epoch,
    )
    auxiliary_output_scale = (
        train_cycle_mean_wss_rms(train)
        if method_id == METHOD_TRANSIENT_MEAN
        else float(steady_output_scale)
    )
    model = _build_model(
        method_id=method_id,
        topology=topology,
        cycle_output_scale=float(cycle_output_scale),
        auxiliary_output_scale=auxiliary_output_scale,
    ).to(device)
    shared, cycle, auxiliary = _parameter_partition(model, method_id)
    if method_id in {METHOD_TRANSIENT_ONLY, METHOD_STEADY_THEN_TRANSIENT}:
        active = shared + cycle
    elif method_id == METHOD_SHARED_DECODER:
        active = shared + cycle
    else:
        active = shared + cycle + auxiliary
    _set_trainable(model, active)

    needs_steady = method_id not in {METHOD_TRANSIENT_ONLY, METHOD_TRANSIENT_MEAN}
    steady_stream = None
    eligible_indices: tuple[int, ...] = ()
    if needs_steady:
        steady_stream, eligible_indices = _build_steady_stream(
            matched_config,
            paths,
            topology,
            ghd_mean=topology.get("train_subset_ghd_mean"),
            ghd_std=topology.get("train_subset_ghd_std"),
        )
        _require(len(eligible_indices) == 13_985, "eligible_steady_count")
    shuffled_targets = (
        deterministic_shuffled_target_map(
            eligible_indices, training_seed=training_seed
        )
        if method_id == METHOD_SHUFFLED_STEADY
        else None
    )
    reference_tawss_floor = train_wss_rms(train) * float(
        matched_config["objective"]["reference_tawss_floor_multiplier"]
    )
    optimization = matched_config["optimization"]
    accumulation = int(optimization["gradient_accumulation_pairs"])
    _require(exposures_per_epoch % accumulation == 0, "accumulation_divisibility")
    checkpoint_interval = int(optimization["checkpoint_interval_epochs"])
    _require(checkpoint_interval > 0, "checkpoint_interval")
    if recovery_checkpoint_directory is not None:
        recovery_checkpoint_directory.mkdir(parents=True, exist_ok=True)
        _require(
            not any(recovery_checkpoint_directory.iterdir()),
            "recovery_checkpoint_directory_not_empty",
        )
    _require(
        (resume_checkpoint is None and resume_expected_provenance is None)
        or (
            resume_checkpoint is not None
            and resume_checkpoint.is_file()
            and resume_expected_provenance is not None
        ),
        "resume_inputs",
    )
    steady_seed = int(matched_config["eligible_steady"]["schedule_seed"])

    smoke_train = _to_device(train[0], device)
    smoke_steady = (
        _to_device(steady_stream.decode(eligible_indices[0]), device)
        if needs_steady
        else None
    )
    smoke = _training_smoke(
        model=model,
        method_id=method_id,
        train_case=smoke_train,
        steady_case=smoke_steady,
        auxiliary_coefficient=auxiliary_coefficient,
        shared=shared,
        cycle=cycle,
        auxiliary=auxiliary,
    )

    steady_exposure = ExposureDigest()
    shuffled_target_exposure = ExposureDigest()
    pretraining_history: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []
    shared_decoder_cosines: list[float] = []
    pretraining_optimizer_updates = 0
    transient_optimizer_updates = 0
    transient_exposures = 0
    auxiliary_exposures = 0
    completed_pretraining_epochs = 0
    completed_transient_epochs = 0
    elapsed_prior = 0.0
    peak_gpu_memory_prior = 0
    resumed_from_checkpoint_sha256: str | None = None
    resumed_from_stage: str | None = None
    resume_header: Mapping[str, Any] | None = None
    if resume_checkpoint is not None:
        loaded_header = torch.load(
            str(resume_checkpoint), map_location="cpu", weights_only=True
        )
        _require(isinstance(loaded_header, Mapping), "resume_header")
        resume_header = loaded_header
        resumed_from_stage = str(resume_header.get("stage"))
        resumed_from_checkpoint_sha256 = file_sha256(resume_checkpoint)

    if method_id == METHOD_STEADY_THEN_TRANSIENT and resumed_from_stage != "transient_training":
        _set_trainable(model, shared + auxiliary)
        optimizer, scheduler = _optimizer_scheduler(shared + auxiliary, optimization)
        if resume_checkpoint is not None:
            _require(resumed_from_stage == "steady_pretraining", "resume_pretraining_stage")
            restored = _restore_recovery_checkpoint(
                resume_checkpoint,
                revision_config=revision_config,
                method_id=method_id,
                training_seed=training_seed,
                auxiliary_coefficient=auxiliary_coefficient,
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                expected_provenance=resume_expected_provenance or {},
            )
            completed_pretraining_epochs = int(
                restored["completed_steady_pretraining_epochs"]
            )
            _require(restored["completed_transient_epochs"] == 0, "resume_pretraining_progress")
            pretraining_history = [dict(row) for row in restored["pretraining_history"]]
            pretraining_optimizer_updates = int(
                restored["pretraining_optimizer_updates"]
            )
            auxiliary_exposures = int(restored["auxiliary_exposures"])
            smoke = dict(restored["smoke"])
            elapsed_prior = float(restored["elapsed_seconds_accumulated"])
            peak_gpu_memory_prior = int(restored["peak_gpu_memory_bytes"])
            _require(
                math.isclose(
                    float(restored["cycle_output_scale"]),
                    float(cycle_output_scale),
                    rel_tol=0.0,
                    abs_tol=0.0,
                )
                and math.isclose(
                    float(restored["auxiliary_output_scale"]),
                    auxiliary_output_scale,
                    rel_tol=0.0,
                    abs_tol=0.0,
                )
                and math.isclose(
                    float(restored["reference_tawss_floor"]),
                    reference_tawss_floor,
                    rel_tol=0.0,
                    abs_tol=0.0,
                ),
                "resume_scales",
            )
            steady_exposure, shuffled_target_exposure = _rebuild_steady_exposure_digests(
                method_id=method_id,
                eligible_indices=eligible_indices,
                steady_seed=steady_seed,
                exposures_per_epoch=exposures_per_epoch,
                completed_pretraining_epochs=completed_pretraining_epochs,
                completed_transient_epochs=0,
                shuffled_targets=shuffled_targets,
            )
            _require(
                steady_exposure.count == auxiliary_exposures
                and steady_exposure.hexdigest()
                == restored["steady_exposure_prefix_sha256"],
                "resume_pretraining_exposure",
            )
        for epoch in range(completed_pretraining_epochs, reference_epochs):
            model.train()
            order = tuple(
                epoch_exposure_indices(
                    eligible_indices,
                    epoch=epoch,
                    cases_per_epoch=exposures_per_epoch,
                    seed=steady_seed,
                )
            )
            _require(len(order) == exposures_per_epoch, "pretraining_epoch")
            optimizer.zero_grad(set_to_none=True)
            loss_sum = 0.0
            for step, steady_index in enumerate(order):
                case = _to_device(steady_stream.decode(steady_index), device)
                loss = single_field_relative_squared_error(
                    model.forward_single_field(case),
                    case["steady_wss"],
                    case["vertex_weights"],
                )
                (loss / accumulation).backward()
                steady_exposure.update(steady_index)
                loss_sum += float(loss.detach().item())
                if (step + 1) % accumulation == 0:
                    torch.nn.utils.clip_grad_norm_(
                        shared + auxiliary,
                        float(optimization["gradient_clip_norm"]),
                    )
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    pretraining_optimizer_updates += 1
            scheduler.step()
            row = {
                "stage": "steady_pretraining",
                "epoch": epoch + 1,
                "mean_auxiliary_relative_squared_error": loss_sum / len(order),
                "steady_exposures_cumulative": steady_exposure.count,
                "learning_rate": float(scheduler.get_last_lr()[0]),
            }
            pretraining_history.append(row)
            completed_pretraining_epochs = epoch + 1
            print(json.dumps(row, sort_keys=True), flush=True)
            if recovery_checkpoint_directory is not None and (
                completed_pretraining_epochs % checkpoint_interval == 0
                or completed_pretraining_epochs == reference_epochs
            ):
                _strict_atomic_torch_save(
                    recovery_checkpoint_directory
                    / f"steady_pretraining_epoch_{completed_pretraining_epochs:03d}.pt",
                    _make_recovery_checkpoint(
                        revision_config=revision_config,
                        method_id=method_id,
                        training_seed=training_seed,
                        auxiliary_coefficient=auxiliary_coefficient,
                        stage="steady_pretraining",
                        completed_pretraining_epochs=completed_pretraining_epochs,
                        completed_transient_epochs=0,
                        model=model,
                        optimizer=optimizer,
                        scheduler=scheduler,
                        smoke=smoke,
                        pretraining_history=pretraining_history,
                        history=(),
                        shared_decoder_cosines=(),
                        pretraining_optimizer_updates=pretraining_optimizer_updates,
                        transient_optimizer_updates=0,
                        transient_exposures=0,
                        auxiliary_exposures=steady_exposure.count,
                        steady_exposure=steady_exposure,
                        shuffled_target_exposure=shuffled_target_exposure,
                        cycle_output_scale=float(cycle_output_scale),
                        auxiliary_output_scale=auxiliary_output_scale,
                        reference_tawss_floor=reference_tawss_floor,
                        elapsed_seconds_accumulated=elapsed_prior
                        + time.monotonic()
                        - started,
                        peak_gpu_memory_bytes=max(
                            peak_gpu_memory_prior,
                            int(torch.cuda.max_memory_allocated()),
                        ),
                        provenance=provenance,
                    ),
                )
        _require(
            steady_exposure.count == ledger.steady_pretraining_exposures,
            "pretraining_exposure_count",
        )
        _set_trainable(model, shared + cycle)
        auxiliary_exposures = steady_exposure.count

    optimizer, scheduler = _optimizer_scheduler(
        tuple(parameter for parameter in model.parameters() if parameter.requires_grad),
        optimization,
    )
    if resumed_from_stage == "transient_training":
        _require(resume_checkpoint is not None, "resume_transient_checkpoint")
        restored = _restore_recovery_checkpoint(
            resume_checkpoint,
            revision_config=revision_config,
            method_id=method_id,
            training_seed=training_seed,
            auxiliary_coefficient=auxiliary_coefficient,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            expected_provenance=resume_expected_provenance or {},
        )
        completed_pretraining_epochs = int(
            restored["completed_steady_pretraining_epochs"]
        )
        completed_transient_epochs = int(restored["completed_transient_epochs"])
        pretraining_history = [dict(row) for row in restored["pretraining_history"]]
        history = [dict(row) for row in restored["history"]]
        shared_decoder_cosines = [
            float(value) for value in restored["shared_decoder_cosines"]
        ]
        pretraining_optimizer_updates = int(restored["pretraining_optimizer_updates"])
        transient_optimizer_updates = int(restored["transient_optimizer_updates"])
        transient_exposures = int(restored["transient_exposures"])
        auxiliary_exposures = int(restored["auxiliary_exposures"])
        smoke = dict(restored["smoke"])
        elapsed_prior = float(restored["elapsed_seconds_accumulated"])
        peak_gpu_memory_prior = int(restored["peak_gpu_memory_bytes"])
        _require(
            math.isclose(
                float(restored["cycle_output_scale"]),
                float(cycle_output_scale),
                rel_tol=0.0,
                abs_tol=0.0,
            )
            and math.isclose(
                float(restored["auxiliary_output_scale"]),
                auxiliary_output_scale,
                rel_tol=0.0,
                abs_tol=0.0,
            )
            and math.isclose(
                float(restored["reference_tawss_floor"]),
                reference_tawss_floor,
                rel_tol=0.0,
                abs_tol=0.0,
            ),
            "resume_scales",
        )
        steady_exposure, shuffled_target_exposure = _rebuild_steady_exposure_digests(
            method_id=method_id,
            eligible_indices=eligible_indices,
            steady_seed=steady_seed,
            exposures_per_epoch=exposures_per_epoch,
            completed_pretraining_epochs=completed_pretraining_epochs,
            completed_transient_epochs=completed_transient_epochs,
            shuffled_targets=shuffled_targets,
        )
        _require(
            steady_exposure.count
            == (
                auxiliary_exposures
                if method_id != METHOD_TRANSIENT_MEAN
                else 0
            )
            and (
                steady_exposure.hexdigest()
                if steady_exposure.count
                else None
            )
            == restored["steady_exposure_prefix_sha256"]
            and (
                shuffled_target_exposure.hexdigest()
                if shuffled_target_exposure.count
                else None
            )
            == restored["shuffled_target_exposure_prefix_sha256"],
            "resume_transient_exposure",
        )
    elif resume_checkpoint is not None:
        _require(
            method_id == METHOD_STEADY_THEN_TRANSIENT
            and resumed_from_stage == "steady_pretraining"
            and completed_pretraining_epochs == reference_epochs,
            "resume_stage_transition",
        )
    for epoch in range(completed_transient_epochs, reference_epochs):
        model.train()
        transient_order = _transient_epoch_order(
            train_count=len(train),
            training_seed=training_seed,
            epoch=epoch,
            exposures=exposures_per_epoch,
        )
        steady_order = (
            tuple(
                epoch_exposure_indices(
                    eligible_indices,
                    epoch=epoch,
                    cases_per_epoch=exposures_per_epoch,
                    seed=steady_seed,
                )
            )
            if needs_steady and method_id != METHOD_STEADY_THEN_TRANSIENT
            else ()
        )
        _require(
            len(transient_order) == exposures_per_epoch
            and (not steady_order or len(steady_order) == exposures_per_epoch),
            "training_epoch_order",
        )
        optimizer.zero_grad(set_to_none=True)
        cycle_sum = 0.0
        auxiliary_sum = 0.0
        epoch_cosines: list[float] = []
        for step, transient_index in enumerate(transient_order):
            transient_case = _to_device(train[transient_index], device)
            cycle_loss = field_loss(
                model.forward_cycle(transient_case),
                transient_case["wss"],
                transient_case["vertex_weights"],
            )
            cycle_sum += float(cycle_loss.detach().item())
            transient_exposures += 1
            if method_id in {METHOD_TRANSIENT_ONLY, METHOD_STEADY_THEN_TRANSIENT}:
                (cycle_loss / accumulation).backward()
            elif method_id == METHOD_TRANSIENT_MEAN:
                target = transient_mean_auxiliary_case(transient_case)
                auxiliary_loss = single_field_relative_squared_error(
                    model.forward_single_field(target),
                    target["single_field_wss"],
                    target["vertex_weights"],
                )
                (
                    (cycle_loss + auxiliary_coefficient * auxiliary_loss)
                    / accumulation
                ).backward()
                auxiliary_sum += float(auxiliary_loss.detach().item())
                auxiliary_exposures += 1
            else:
                _require(steady_stream is not None, "steady_stream")
                steady_index = int(steady_order[step])
                geometry_case = steady_stream.decode(steady_index)
                target_index = steady_index
                if shuffled_targets is not None:
                    target_index = int(shuffled_targets[steady_index])
                    target_case = steady_stream.decode(target_index)
                    geometry_case = dict(geometry_case)
                    geometry_case["steady_wss"] = target_case["steady_wss"]
                steady_case = _to_device(geometry_case, device)
                auxiliary_loss = single_field_relative_squared_error(
                    model.forward_single_field(steady_case),
                    steady_case["steady_wss"],
                    steady_case["vertex_weights"],
                )
                if method_id == METHOD_SHARED_DECODER:
                    diagnostic = shared_decoder_cross_regime_backward_with_decoder_diagnostic(
                        transient_loss=cycle_loss,
                        auxiliary_loss=auxiliary_loss,
                        optimization_parameters=shared + cycle,
                        diagnostic_decoder_parameters=cycle,
                        auxiliary_coefficient=auxiliary_coefficient,
                        accumulation_steps=accumulation,
                    )
                    cosine = float(diagnostic["decoder_gradient_cosine"])
                    epoch_cosines.append(cosine)
                    shared_decoder_cosines.append(cosine)
                else:
                    (
                        (cycle_loss + auxiliary_coefficient * auxiliary_loss)
                        / accumulation
                    ).backward()
                auxiliary_sum += float(auxiliary_loss.detach().item())
                auxiliary_exposures += 1
                steady_exposure.update(steady_index)
                if shuffled_targets is not None:
                    shuffled_target_exposure.update(target_index)
            if (step + 1) % accumulation == 0:
                torch.nn.utils.clip_grad_norm_(
                    tuple(
                        parameter
                        for parameter in model.parameters()
                        if parameter.requires_grad
                    ),
                    float(optimization["gradient_clip_norm"]),
                )
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                transient_optimizer_updates += 1
        scheduler.step()
        row = {
            "stage": "transient_training",
            "epoch": epoch + 1,
            "mean_cycle_relative_squared_error": cycle_sum / len(transient_order),
            "mean_auxiliary_relative_squared_error": (
                auxiliary_sum / len(transient_order)
                if method_id not in {METHOD_TRANSIENT_ONLY, METHOD_STEADY_THEN_TRANSIENT}
                else None
            ),
            "transient_exposures_cumulative": transient_exposures,
            "auxiliary_exposures_cumulative": auxiliary_exposures,
            "decoder_gradient_cosine": (
                summarize_gradient_cosines(epoch_cosines) if epoch_cosines else None
            ),
            "learning_rate": float(scheduler.get_last_lr()[0]),
        }
        history.append(row)
        completed_transient_epochs = epoch + 1
        print(json.dumps(row, sort_keys=True), flush=True)
        if recovery_checkpoint_directory is not None and (
            completed_transient_epochs % checkpoint_interval == 0
            or completed_transient_epochs == reference_epochs
        ):
            _strict_atomic_torch_save(
                recovery_checkpoint_directory
                / f"transient_training_epoch_{completed_transient_epochs:03d}.pt",
                _make_recovery_checkpoint(
                    revision_config=revision_config,
                    method_id=method_id,
                    training_seed=training_seed,
                    auxiliary_coefficient=auxiliary_coefficient,
                    stage="transient_training",
                    completed_pretraining_epochs=completed_pretraining_epochs,
                    completed_transient_epochs=completed_transient_epochs,
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    smoke=smoke,
                    pretraining_history=pretraining_history,
                    history=history,
                    shared_decoder_cosines=shared_decoder_cosines,
                    pretraining_optimizer_updates=pretraining_optimizer_updates,
                    transient_optimizer_updates=transient_optimizer_updates,
                    transient_exposures=transient_exposures,
                    auxiliary_exposures=auxiliary_exposures,
                    steady_exposure=steady_exposure,
                    shuffled_target_exposure=shuffled_target_exposure,
                    cycle_output_scale=float(cycle_output_scale),
                    auxiliary_output_scale=auxiliary_output_scale,
                    reference_tawss_floor=reference_tawss_floor,
                    elapsed_seconds_accumulated=elapsed_prior
                    + time.monotonic()
                    - started,
                    peak_gpu_memory_bytes=max(
                        peak_gpu_memory_prior,
                        int(torch.cuda.max_memory_allocated()),
                    ),
                    provenance=provenance,
                ),
            )

    _require(transient_exposures == ledger.transient_exposures, "transient_exposures")
    _require(auxiliary_exposures == ledger.auxiliary_exposures, "auxiliary_exposures")
    if needs_steady:
        _require(steady_exposure.count == ledger.auxiliary_exposures, "steady_exposures")
    model.eval()
    final_validation = evaluate(
        model,
        validation,
        matched_config,
        "field_only",
        reference_tawss_floor,
        None,
        device,
    )
    prediction_artifacts: list[dict[str, Any]] = []
    if prediction_directory is not None:
        prediction_directory.mkdir(parents=True, exist_ok=True)
        _require(
            not any(prediction_directory.iterdir()),
            "prediction_directory_not_empty",
        )
        with torch.no_grad():
            for case_index, cpu_case in enumerate(validation):
                prediction = model.forward_cycle(_to_device(cpu_case, device))
                prediction_path = prediction_directory / f"case_{case_index:03d}.pt"
                _strict_atomic_torch_save(
                    prediction_path,
                    {
                        "schema_version": "aurora.private.aneug_release_730_icce_validation_prediction.v2",
                        "protocol_id": revision_config["protocol_id"],
                        "method_id": method_id,
                        "training_seed": training_seed,
                        "validation_order_index": case_index,
                        "physical_vector_wss_float16": prediction.detach()
                        .cpu()
                        .to(torch.float16)
                        .contiguous(),
                        "quantized_for_storage": True,
                        "used_for_reported_metrics": False,
                        "case_identifier_included": False,
                    },
                )
                prediction_artifacts.append(
                    {
                        "validation_order_index": case_index,
                        "filename": prediction_path.name,
                        "bytes": prediction_path.stat().st_size,
                        "sha256": file_sha256(prediction_path),
                        "shape": [80, 13_902, 3],
                        "dtype": "float16",
                    }
                )
    checkpoint_payload = {
        "schema_version": "aurora.private.aneug_release_730_icce_fixed_budget_checkpoint.v2",
        "protocol_id": revision_config["protocol_id"],
        "method_id": method_id,
        "training_seed": training_seed,
        "selected_epoch": reference_epochs,
        "checkpoint_rule": ledger.checkpoint_rule,
        "model_state_dict": _state_dict_cpu(model),
        "cycle_output_scale": float(cycle_output_scale),
        "auxiliary_output_scale": auxiliary_output_scale,
        "reference_tawss_floor": reference_tawss_floor,
        "continuation_mode": resume_checkpoint is not None,
        "resumed_from_checkpoint_sha256": resumed_from_checkpoint_sha256,
        "resumed_from_stage": resumed_from_stage,
        **dict(provenance),
    }
    _strict_atomic_torch_save(checkpoint_path, checkpoint_payload)
    checkpoint_sha256 = file_sha256(checkpoint_path)
    recovery_checkpoint_artifacts = (
        [
            {
                "filename": path.name,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
            for path in sorted(recovery_checkpoint_directory.glob("*.pt"))
        ]
        if recovery_checkpoint_directory is not None
        else []
    )
    result = {
        "schema_version": "aurora.private.aneug_release_730_icce_fixed_budget_result.v2",
        "protocol_id": revision_config["protocol_id"],
        "status": "complete_validation_only",
        **ledger.as_dict(),
        "selected_epoch": reference_epochs,
        "training_seed": training_seed,
        "auxiliary_coefficient": auxiliary_coefficient,
        "transient_encoder_forwards": transient_exposures,
        "auxiliary_encoder_forwards": auxiliary_exposures,
        "optimizer_updates": pretraining_optimizer_updates
        + transient_optimizer_updates,
        "steady_pretraining_optimizer_updates": pretraining_optimizer_updates,
        "transient_training_optimizer_updates": transient_optimizer_updates,
        "total_epochs": reference_epochs
        + (reference_epochs if method_id == METHOD_STEADY_THEN_TRANSIENT else 0),
        "transient_training_epochs": reference_epochs,
        "steady_pretraining_epochs": (
            reference_epochs if method_id == METHOD_STEADY_THEN_TRANSIENT else 0
        ),
        "train_case_count": len(train),
        "validation_case_count": len(validation),
        "train_case_digest": (
            train_subset_digest
            if train_subset_digest is not None
            else matched_config["split"]["train_case_digest"]
        ),
        "validation_case_digest": matched_config["split"]["validation_case_digest"],
        "parameter_count_with_training_head": model_parameter_count(model),
        "cycle_forward_parameter_count": model_parameter_count(model.backbone),
        "checkpoint_sha256": checkpoint_sha256,
        "validation_prediction_artifacts": prediction_artifacts,
        "validation_prediction_count": len(prediction_artifacts),
        "stored_predictions_are_metric_inputs": False,
        "steady_exposure_prefix_sha256": (
            steady_exposure.hexdigest() if needs_steady else None
        ),
        "shuffled_target_map_sha256": (
            shuffled_target_map_digest(shuffled_targets)
            if shuffled_targets is not None
            else None
        ),
        "shuffled_target_exposure_prefix_sha256": (
            shuffled_target_exposure.hexdigest()
            if shuffled_targets is not None
            else None
        ),
        "decoder_gradient_diagnostic": (
            summarize_gradient_cosines(shared_decoder_cosines)
            if shared_decoder_cosines
            else None
        ),
        "smoke": smoke,
        "validation": final_validation,
        "pretraining_history": pretraining_history,
        "history": history,
        "reference_tawss_floor": reference_tawss_floor,
        "elapsed_wall_seconds": elapsed_prior + time.monotonic() - started,
        "peak_gpu_memory_bytes": max(
            peak_gpu_memory_prior, int(torch.cuda.max_memory_allocated())
        ),
        "continuation_mode": resume_checkpoint is not None,
        "resumed_from_checkpoint_sha256": resumed_from_checkpoint_sha256,
        "resumed_from_stage": resumed_from_stage,
        "recovery_checkpoint_artifacts": recovery_checkpoint_artifacts,
        "recovery_checkpoint_count": len(recovery_checkpoint_artifacts),
        "gpu_used": True,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
        "paper_claim": False,
        **dict(provenance),
    }
    validate_partition_boundary(
        train_case_count=len(train),
        validation_case_count=len(validation),
        locked_test_field_case_count_read=0,
        processed_only_extra_field_case_count_read=0,
        train_digest=result["train_case_digest"],
        validation_digest=result["validation_case_digest"],
    )
    validate_exposure_result(result, ledger)
    _strict_atomic_json(result_path, result)
    return result
