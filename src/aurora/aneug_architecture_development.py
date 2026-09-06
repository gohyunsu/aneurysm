"""Small, shared complete-cycle development trainer, separate from v2 evidence.

The caller supplies an admitted train/validation bundle and a physical-output
model. This module has no split selection, test loader, upstream source import
or scientific acceptance threshold. Snapshots require a different exposure
ledger; they must not be routed through this one-shot cycle trainer silently.
"""

from __future__ import annotations

import math
import random
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import torch
from torch import nn

from aurora.aneug_processed_v4_d9 import field_loss
from aurora.aneug_release_730_ghd_gps_baseline import (
    _strict_atomic_json,
    _strict_atomic_torch_save,
    _to_device,
    extended_case_metrics,
    file_sha256,
)
from aurora.aneug_release_730_response_local_candidate import _valid_support_osi
from aurora.release730_training_continuation import capture_rng_state


@torch.no_grad()
def evaluate_cycles(model: nn.Module, cases: Sequence[Mapping[str, torch.Tensor]],
                    device: torch.device, reference_tawss_floor: float) -> dict[str, Any]:
    if not cases or not math.isfinite(reference_tawss_floor) or reference_tawss_floor <= 0:
        raise ValueError("nonempty admitted validation and positive train-only OSI floor required")
    model.eval()
    rows = []
    for cpu_case in cases:
        case = _to_device(cpu_case, device)
        prediction = model.forward_cycle(case)
        if prediction.shape != case["wss"].shape or not torch.isfinite(prediction).all():
            raise RuntimeError("nonfinite or incompatible complete-cycle validation prediction")
        metrics = extended_case_metrics(prediction, case["wss"], case["vertex_weights"],
                                        case["normals"])
        metrics["osi_mae"], metrics["osi_coverage"] = _valid_support_osi(
            prediction, case["wss"], case["vertex_weights"], reference_tawss_floor
        )
        rows.append(metrics)
    return {"case_count": len(rows), "per_case_without_identifiers": rows,
            "aggregate": {key: sum(row[key] for row in rows) / len(rows) for key in rows[0]}}


def validate_optimization(config: Mapping[str, Any]) -> None:
    for key in ("epochs", "accumulation_cases", "validation_interval", "checkpoint_interval",
                "step_size_epochs"):
        if type(config.get(key)) is not int or config[key] < 1:
            raise ValueError(f"positive integer required: {key}")
    if type(config.get("seed")) is not int or config["seed"] < 0:
        raise ValueError("nonnegative integer seed required")
    for key in ("learning_rate", "gamma", "gradient_clip_norm"):
        if not math.isfinite(config[key]) or config[key] <= 0:
            raise ValueError(f"positive finite value required: {key}")
    if not math.isfinite(config["weight_decay"]) or config["weight_decay"] < 0:
        raise ValueError("nonnegative weight decay required")


def train_cycles(
    model: nn.Module,
    train: Sequence[Mapping[str, torch.Tensor]],
    validation: Sequence[Mapping[str, torch.Tensor]],
    *,
    optimization: Mapping[str, Any],
    reference_tawss_floor: float,
    output_directory: Path,
    provenance: Mapping[str, Any],
    device: torch.device,
    log: Callable[[Mapping[str, Any]], None] = print,
    continuation: Mapping[str, Any] | None = None,
    steady_supervision=None,
) -> dict[str, Any]:
    """Fixed development budget, validation-only best checkpoint selection.

    Every epoch visits each supplied training geometry once and supervises its
    full cycle. Checkpoints preserve optimizer, scheduler, RNG and the best
    state as well as the current state for a separately recorded continuation.
    No performance-based early stopping or raw prediction storage is used.
    Optional paired steady supervision adds one independently decoded field
    per cycle before the same optimizer update, with its own relative loss.
    It never treats steady as a phase or mean, or reads it during validation.
    """

    validate_optimization(optimization)
    if steady_supervision is not None:
        from aurora.aneug_paired_steady_supervision import PairedSteadySupervision
        if not isinstance(steady_supervision, PairedSteadySupervision):
            raise ValueError("explicit paired steady supervision required")
        if not callable(getattr(model, "forward_single_field", None)):
            raise ValueError("independent physical steady output required")
        provenance = dict(provenance)
        existing = provenance.get("joint_steady_supervision", steady_supervision.contract)
        if existing != steady_supervision.contract:
            raise ValueError("steady provenance differs from actual sampler")
        provenance["joint_steady_supervision"] = steady_supervision.contract
    elif "joint_steady_supervision" in provenance:
        raise ValueError("steady provenance without actual steady supervision")
    if not train or not validation:
        raise ValueError("nonempty train and validation required")
    if output_directory.exists():
        raise FileExistsError(output_directory)
    output_directory.mkdir(parents=True)
    model.to(device)
    phases = int(train[0]["wss"].shape[0])
    if phases < 2 or any(case["wss"].shape[0] != phases for case in (*train, *validation)):
        raise ValueError("complete cycles must share a phase count")
    optimizer = torch.optim.AdamW(model.parameters(), lr=optimization["learning_rate"],
                                  weight_decay=optimization["weight_decay"])
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, step_size=optimization["step_size_epochs"], gamma=optimization["gamma"]
    )
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
    histories, artifacts = [], []
    best_value, best_epoch, best_state, best_validation = float("inf"), 0, None, None
    exposures, updates, evaluation_forwards = 0, 0, 0
    completed, previous_seconds, previous_peak, resume_receipt = 0, 0.0, 0, None
    if continuation is not None:
        from aurora.aneug_cycle_continuation import restore_completed_curve
        checkpoint, parent, resume_receipt = restore_completed_curve(
            continuation, model=model, optimizer=optimizer, scheduler=scheduler,
            optimization=optimization, provenance=provenance, train_cases=len(train),
            validation_cases=len(validation), phases=phases,
            reference_tawss_floor=reference_tawss_floor, device=device,
            steady_supervision=steady_supervision)
        histories = list(checkpoint["history"])
        completed = checkpoint["completed_epoch"]
        best_value, best_epoch = checkpoint["best_value"], checkpoint["best_epoch"]
        best_state, best_validation = checkpoint["best_state_dict"], checkpoint["best_validation"]
        exposures, updates = parent["training_cycle_exposures"], parent["optimizer_updates"]
        evaluation_forwards = parent["validation_cycle_forwards"]
        previous_seconds = parent["elapsed_training_and_validation_seconds"]
        previous_peak = parent["peak_cuda_allocated_bytes"]
        for row in histories:
            _strict_atomic_json(output_directory / "epochs" / f"epoch_{row['epoch']:03d}.json", row)
        _strict_atomic_json(output_directory / "continuation.json", resume_receipt)
        log({"stage": "architecture_v3_continuation_restored", "completed_epoch": completed,
             "next_epoch": completed + 1, "training_cycle_exposures": exposures,
             "optimizer_updates": updates})
    started = time.monotonic()
    disconnected_checked = False
    seen_steady = set()
    if steady_supervision is not None:
        from aurora.aneug_release_730_matched_steady_stream import single_field_relative_squared_error
        from aurora.aneug_release_730_steady_exposure_schedule import ordered_digest
        for old_epoch in range(1, completed + 1):
            seen_steady.update(steady_supervision.indices(old_epoch, len(train)))
    for epoch in range(completed + 1, optimization["epochs"] + 1):
        model.train()
        order = list(range(len(train)))
        random.Random(optimization["seed"] + epoch).shuffle(order)
        loss_sum = 0.0
        steady_loss_sum = 0.0
        steady_order = steady_supervision.indices(epoch, len(train)) if steady_supervision else None
        epoch_started = time.monotonic()
        for offset in range(0, len(order), optimization["accumulation_cases"]):
            batch = order[offset:offset + optimization["accumulation_cases"]]
            optimizer.zero_grad(set_to_none=True)
            for within_batch, index in enumerate(batch):
                case = _to_device(train[index], device)
                prediction = model.forward_cycle(case)
                if prediction.shape != case["wss"].shape:
                    raise RuntimeError("training cycle shape mismatch")
                loss = field_loss(prediction, case["wss"], case["vertex_weights"])
                if not torch.isfinite(loss):
                    raise RuntimeError("nonfinite training loss")
                (loss / len(batch)).backward()
                loss_sum += float(loss.detach())
                exposures += 1
                if steady_supervision is not None:
                    steady_index = steady_order[offset + within_batch]
                    steady_case = _to_device(steady_supervision.decode(steady_index), device)
                    steady_prediction = model.forward_single_field(steady_case)
                    if steady_prediction.shape != steady_case["steady_wss"].shape or steady_prediction.ndim != 2:
                        raise RuntimeError("steady prediction must be one [node,3] field, not a cycle")
                    steady_loss = single_field_relative_squared_error(
                        steady_prediction, steady_case["steady_wss"], steady_case["vertex_weights"])
                    if not torch.isfinite(steady_loss):
                        raise RuntimeError("nonfinite steady training loss")
                    (steady_loss * steady_supervision.loss_weight / len(batch)).backward()
                    steady_loss_sum += float(steady_loss.detach())
                    seen_steady.add(steady_index)
            if not disconnected_checked:
                missing = [name for name, p in model.named_parameters()
                           if p.requires_grad and p.grad is None]
                if missing:
                    raise RuntimeError(f"disconnected parameters: {missing}")
                disconnected_checked = True
            torch.nn.utils.clip_grad_norm_(model.parameters(), optimization["gradient_clip_norm"],
                                           error_if_nonfinite=True)
            optimizer.step()
            updates += 1
        scheduler.step()
        row = {"epoch": epoch, "train_relative_squared_error": loss_sum / len(train),
               "training_cycle_exposures": exposures, "training_phase_field_exposures": exposures * phases,
               "optimizer_updates": updates, "learning_rate_next_epoch": scheduler.get_last_lr()[0],
               "training_epoch_seconds": time.monotonic() - epoch_started}
        if steady_supervision is not None:
            row.update(steady_exposures=exposures,
                       train_steady_relative_squared_error=steady_loss_sum / len(train),
                       steady_epoch_order_sha256=ordered_digest(steady_order),
                       unique_steady_cases_seen=len(seen_steady))
        if epoch % optimization["validation_interval"] == 0 or epoch == optimization["epochs"]:
            evaluation = evaluate_cycles(model, validation, device, reference_tawss_floor)
            evaluation_forwards += len(validation)
            value = evaluation["aggregate"]["field_relative_l2"]
            row["validation"] = evaluation["aggregate"]
            if value < best_value:
                best_value, best_epoch, best_validation = value, epoch, evaluation
                best_state = {name: value.detach().cpu().clone()
                              for name, value in model.state_dict().items()}
        histories.append(row)
        log({"stage": "architecture_v3_epoch", **row})
        _strict_atomic_json(output_directory / "epochs" / f"epoch_{epoch:03d}.json", row)
        if epoch == 1 or epoch % optimization["checkpoint_interval"] == 0 or epoch == optimization["epochs"]:
            checkpoint = output_directory / "checkpoints" / f"epoch_{epoch:03d}.pt"
            _strict_atomic_torch_save(checkpoint, {
                "schema_version": "aurora.private.architecture_development_checkpoint.v3",
                "completed_epoch": epoch, "optimization": dict(optimization),
                "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                "optimizer_state_dict": optimizer.state_dict(), "scheduler_state_dict": scheduler.state_dict(),
                "rng_state": capture_rng_state(), "best_epoch": best_epoch, "best_value": best_value,
                "best_state_dict": best_state, "best_validation": best_validation,
                "history": histories, "provenance": dict(provenance),
                "reference_tawss_floor": reference_tawss_floor,
            })
            artifacts.append({"file": str(checkpoint.relative_to(output_directory)),
                              "sha256": file_sha256(checkpoint), "bytes": checkpoint.stat().st_size})
    if best_state is None:
        raise RuntimeError("no validation checkpoint selected")
    selected_path = output_directory / "selected.pt"
    _strict_atomic_torch_save(selected_path, {"model_state_dict": best_state, "epoch": best_epoch,
                                             "provenance": dict(provenance)})
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    result = {
        "schema_version": "aurora.private.architecture_development_result.v3",
        "status": "completed_validation_development", "provenance": dict(provenance),
        "optimization": dict(optimization), "train_cases": len(train), "validation_cases": len(validation),
        "phase_count": phases, "training_cycle_exposures": exposures,
        "training_phase_field_exposures": exposures * phases,
        "steady_exposures": exposures if steady_supervision else 0,
        "optimizer_updates": updates, "validation_cycle_forwards": evaluation_forwards,
        "selected_epoch": best_epoch, "checkpoint_selection": "lowest_validation_field_rL2_then_earliest",
        "selected_validation": best_validation, "reference_tawss_floor": reference_tawss_floor,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "elapsed_training_and_validation_seconds": previous_seconds + time.monotonic() - started,
        "peak_cuda_allocated_bytes": max(previous_peak, torch.cuda.max_memory_allocated(device) if device.type == "cuda" else 0),
        "device": str(device), "device_name": torch.cuda.get_device_name(device) if device.type == "cuda" else "CPU",
        "checkpoints": artifacts, "selected_checkpoint_sha256": file_sha256(selected_path),
        "raw_predictions_stored": 0, "test_field_access_performed": False,
        "processed_extra_field_access_performed": False, "independent_confirmatory_evaluation": False,
        "result_is_architectural_novelty_evidence_by_itself": False,
    }
    if steady_supervision is not None:
        result.update(joint_steady_supervision=steady_supervision.contract,
                      unique_steady_cases_seen=len(seen_steady),
                      transient_training_encoder_forwards=exposures,
                      steady_training_encoder_forwards=exposures,
                      total_training_field_exposures=exposures * (phases + 1),
                      inference_requires_steady_CFD=False)
    if resume_receipt is not None:
        result["continuation"] = resume_receipt
        result["segment_training_cycle_exposures"] = (optimization["epochs"] - completed) * len(train)
        result["segment_optimizer_updates"] = (optimization["epochs"] - completed) * math.ceil(len(train) / optimization["accumulation_cases"])
        if steady_supervision is not None:
            result["segment_steady_exposures"] = result["segment_training_cycle_exposures"]
        result["segment_elapsed_training_and_validation_seconds"] = result["elapsed_training_and_validation_seconds"] - previous_seconds
    _strict_atomic_json(output_directory / "result.json", result)
    return result
