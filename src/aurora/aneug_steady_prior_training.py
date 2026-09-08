"""Separate, fixed-budget steady predictor training for the sequence FiLM prior.

Only explicitly eligible steady rows are decoded. No transient field, test
loader, pseudo steady-to-cycle label or validation-based prior selection is
introduced. The fixed terminal prior and its optimizer/RNG recovery states are
recorded independently of subsequent transient training and model selection.
"""
from __future__ import annotations

import math
from pathlib import Path
import random
import time
from typing import Any, Callable, Mapping, Sequence

import torch

from aurora.aneug_release_730_ghd_gps_baseline import (
    _strict_atomic_json, _strict_atomic_torch_save, _to_device, file_sha256,
)
from aurora.aneug_release_730_matched_steady_stream import (
    epoch_exposure_indices, single_field_relative_squared_error,
)
from aurora.aneug_release_730_steady_exposure_schedule import ordered_digest
from aurora.aneug_sequence_film import geometry_only
from aurora.release730_training_continuation import capture_rng_state


def validate_optimization(config):
    integers = ("epochs", "cases_per_epoch", "accumulation_cases", "checkpoint_interval", "step_size_epochs")
    for key in integers:
        if type(config.get(key)) is not int or config[key] < 1:
            raise ValueError(f"positive integer required: {key}")
    if type(config.get("seed")) is not int or config["seed"] < 0:
        raise ValueError("nonnegative integer seed required")
    for key in ("learning_rate", "gamma", "gradient_clip_norm"):
        if not math.isfinite(config[key]) or config[key] <= 0:
            raise ValueError(f"positive finite value required: {key}")
    if not math.isfinite(config["weight_decay"]) or config["weight_decay"] < 0:
        raise ValueError("nonnegative weight decay required")


def train_steady_prior(model, stream, eligible_indices: Sequence[int], *,
                       optimization: Mapping[str, Any], output_directory: Path,
                       provenance: Mapping[str, Any], device: torch.device,
                       continuation: Mapping[str, Any] | None = None,
                       log: Callable = print):
    """Train a physical single-field model; terminal state, no early stopping.

    The caller seeds before model construction and binds admitted source/row
    manifests. Case microbatches use explicit gradient accumulation, not a
    claimed source batch-ten recipe. A fresh output may resume a hash-bound
    epoch checkpoint, preserving sample order, optimizer, scheduler and RNG.
    """
    validate_optimization(optimization)
    eligible = tuple(eligible_indices)
    if (not eligible or len(set(eligible)) != len(eligible)
            or any(type(i) is not int or i < 0 for i in eligible)):
        raise ValueError("unique explicitly eligible integer steady rows required")
    if output_directory.exists():
        raise FileExistsError(output_directory)
    if not all(p.requires_grad for p in model.parameters()):
        raise ValueError("separate steady model must be trainable before it is frozen for FiLM")
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=optimization["learning_rate"],
                                  weight_decay=optimization["weight_decay"])
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
        step_size=optimization["step_size_epochs"], gamma=optimization["gamma"])
    digest = ordered_digest(eligible)
    history, artifacts, seen = [], [], set()
    completed, previous_seconds, previous_peak, receipt = 0, 0.0, 0, None
    if continuation is not None:
        path = Path(continuation["checkpoint"])
        if file_sha256(path) != continuation["sha256"]:
            raise ValueError("steady prior continuation checkpoint hash")
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        if (checkpoint.get("schema_version") != "aurora.private.steady_prior_checkpoint.v3"
                or checkpoint["provenance"] != dict(provenance)
                or checkpoint["eligible_order_sha256"] != digest
                or checkpoint["eligible_case_count"] != len(eligible)
                or {k: v for k, v in checkpoint["optimization"].items() if k != "epochs"}
                   != {k: v for k, v in optimization.items() if k != "epochs"}):
            raise ValueError("steady prior continuation scientific identity")
        completed, history = checkpoint["completed_epoch"], checkpoint["history"]
        if type(completed) is not int or not 0 < completed < optimization["epochs"] or len(history) != completed:
            raise ValueError("steady prior continuation epoch range")
        count = optimization["cases_per_epoch"]
        steps = math.ceil(count / optimization["accumulation_cases"])
        for epoch, row in enumerate(history, 1):
            if ((row["epoch"], row["steady_exposures"], row["optimizer_updates"])
                    != (epoch, epoch * count, epoch * steps)
                    or not math.isfinite(row["train_relative_squared_error"])):
                raise ValueError("steady prior continuation ledger")
        seen = set(checkpoint["seen_steady_indices"])
        if not seen.issubset(eligible) or checkpoint["scheduler_state_dict"]["last_epoch"] != completed:
            raise ValueError("steady prior continuation sampling/scheduler")
        previous_seconds, previous_peak = checkpoint["elapsed_seconds"], checkpoint["peak_cuda_allocated_bytes"]
        if not math.isfinite(previous_seconds) or previous_seconds < 0:
            raise ValueError("steady prior continuation timing")
        model.load_state_dict(checkpoint["model_state_dict"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        rng = checkpoint["rng_state"]
        random.setstate(rng["python_random_state"])
        torch.set_rng_state(rng["torch_rng_state"])
        cuda_states = rng["cuda_rng_state_all"]
        if device.type == "cuda":
            if len(cuda_states) != torch.cuda.device_count():
                raise ValueError("steady prior continuation CUDA RNG count")
            torch.cuda.set_rng_state_all(cuda_states)
        elif cuda_states:
            raise ValueError("steady prior continuation cannot silently discard CUDA RNG")
        receipt = dict(checkpoint_sha256=continuation["sha256"], completed_epoch=completed,
                       optimizer_scheduler_rng_restored=True, new_independent_seed=False)
    output_directory.mkdir(parents=True)
    for row in history:
        _strict_atomic_json(output_directory / "epochs" / f"epoch_{row['epoch']:03d}.json", row)
    if receipt:
        _strict_atomic_json(output_directory / "continuation.json", receipt)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
    started = time.monotonic()
    exposures = completed * optimization["cases_per_epoch"]
    updates = completed * math.ceil(optimization["cases_per_epoch"] / optimization["accumulation_cases"])
    gradient_checked = False
    for epoch in range(completed + 1, optimization["epochs"] + 1):
        model.train()
        order = list(epoch_exposure_indices(eligible, epoch=epoch - 1,
            cases_per_epoch=optimization["cases_per_epoch"], seed=optimization["seed"]))
        loss_sum, epoch_started = 0.0, time.monotonic()
        for offset in range(0, len(order), optimization["accumulation_cases"]):
            batch = order[offset:offset + optimization["accumulation_cases"]]
            optimizer.zero_grad(set_to_none=True)
            for index in batch:
                case = _to_device(stream.decode(index), device)
                prediction = model(geometry_only(case))
                loss = single_field_relative_squared_error(prediction, case["steady_wss"], case["vertex_weights"])
                if not torch.isfinite(loss):
                    raise RuntimeError("nonfinite steady prior loss")
                (loss / len(batch)).backward()
                loss_sum += float(loss.detach())
                exposures += 1
                seen.add(index)
            if not gradient_checked:
                missing = [name for name, p in model.named_parameters() if p.grad is None]
                if missing:
                    raise RuntimeError(f"disconnected steady prior parameters: {missing}")
                gradient_checked = True
            torch.nn.utils.clip_grad_norm_(model.parameters(), optimization["gradient_clip_norm"],
                                           error_if_nonfinite=True)
            optimizer.step()
            updates += 1
        scheduler.step()
        row = dict(epoch=epoch, steady_exposures=exposures, optimizer_updates=updates,
            train_relative_squared_error=loss_sum / len(order), unique_steady_cases_seen=len(seen),
            learning_rate_next_epoch=scheduler.get_last_lr()[0],
            training_epoch_seconds=time.monotonic() - epoch_started)
        history.append(row)
        _strict_atomic_json(output_directory / "epochs" / f"epoch_{epoch:03d}.json", row)
        log(dict(stage="sequence_steady_prior_epoch", **row))
        if epoch == 1 or epoch % optimization["checkpoint_interval"] == 0 or epoch == optimization["epochs"]:
            if device.type == "cuda":
                torch.cuda.synchronize(device)
            checkpoint_path = output_directory / "checkpoints" / f"epoch_{epoch:03d}.pt"
            _strict_atomic_torch_save(checkpoint_path, dict(
                schema_version="aurora.private.steady_prior_checkpoint.v3", completed_epoch=epoch,
                optimization=dict(optimization), provenance=dict(provenance),
                eligible_order_sha256=digest, eligible_case_count=len(eligible),
                model_state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
                optimizer_state_dict=optimizer.state_dict(), scheduler_state_dict=scheduler.state_dict(),
                rng_state=capture_rng_state(), history=history, seen_steady_indices=sorted(seen),
                elapsed_seconds=previous_seconds + time.monotonic() - started,
                peak_cuda_allocated_bytes=max(previous_peak, torch.cuda.max_memory_allocated(device) if device.type == "cuda" else 0)))
            artifacts.append(dict(file=str(checkpoint_path.relative_to(output_directory)),
                                  sha256=file_sha256(checkpoint_path), bytes=checkpoint_path.stat().st_size))
    final_path = output_directory / "prior.pt"
    _strict_atomic_torch_save(final_path, dict(model_state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
        provenance=dict(provenance), completed_epoch=optimization["epochs"], eligible_order_sha256=digest))
    result = dict(schema_version="aurora.private.steady_prior_result.v3", status="completed_steady_pretraining",
        provenance=dict(provenance), optimization=dict(optimization), eligible_case_count=len(eligible),
        eligible_order_sha256=digest, unique_steady_cases_seen=len(seen), steady_exposures=exposures,
        transient_phase_field_exposures=0, optimizer_updates=updates, history=history,
        checkpoint_selection="fixed_terminal_steady_budget_no_validation_selection",
        prior_checkpoint_sha256=file_sha256(final_path), checkpoints=artifacts,
        parameter_count=sum(p.numel() for p in model.parameters()),
        elapsed_seconds=previous_seconds + time.monotonic() - started,
        peak_cuda_allocated_bytes=max(previous_peak, torch.cuda.max_memory_allocated(device) if device.type == "cuda" else 0),
        device=str(device), device_name=torch.cuda.get_device_name(device) if device.type == "cuda" else "CPU",
        new_test_field_reads=0, new_extra_field_reads=0, raw_predictions_stored=0)
    if receipt:
        result["continuation"] = receipt
        result["segment_steady_exposures"] = (optimization["epochs"] - completed) * optimization["cases_per_epoch"]
    _strict_atomic_json(output_directory / "result.json", result)
    return result
