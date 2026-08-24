"""Exact-state continuation helpers for release-730 development comparators."""

from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from torch import nn


class Release730TrainingContinuationError(RuntimeError):
    """Raised when a comparator checkpoint cannot support an exact resume."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730TrainingContinuationError(reason)


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
    return digest.hexdigest()


def validate_interrupted_attempt_record(
    path: str | Path, expected_sha256: str
) -> dict[str, Any]:
    """Require exact terminal evidence that the earlier attempt did not complete."""

    _require(file_sha256(path) == expected_sha256, "prior_attempt_terminal_hash")
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(isinstance(record, Mapping), "prior_attempt_terminal_mapping")
    _require(
        isinstance(record.get("job_id"), str)
        and bool(record["job_id"])
        and isinstance(record.get("exit_code"), int)
        and record["exit_code"] != 0
        and record.get("complete") is False,
        "prior_attempt_not_interrupted",
    )
    return dict(record)


def capture_rng_state() -> dict[str, Any]:
    """Capture stochastic state even though the registered models use no dropout."""

    return {
        "python_random_state": random.getstate(),
        "torch_rng_state": torch.get_rng_state(),
        "cuda_rng_state_all": torch.cuda.get_rng_state_all()
        if torch.cuda.is_available()
        else [],
    }


def make_training_checkpoint(
    *,
    schema_version: str,
    protocol_id: str,
    epoch: int,
    optimizer_steps: int,
    validation_field_relative_l2: float,
    model_state_dict: Mapping[str, torch.Tensor],
    optimizer_state_dict: Mapping[str, Any],
    scheduler_state_dict: Mapping[str, Any],
    best_state_dict: Mapping[str, torch.Tensor],
    best_field_relative_l2: float,
    best_epoch: int,
    stale_epochs: int,
    history: Sequence[Mapping[str, float | int]],
    smoke: Mapping[str, Any],
    elapsed_seconds_accumulated: float,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Create the complete append-only state needed for an exact continuation."""

    _require(epoch > 0 and optimizer_steps > 0, "checkpoint_progress")
    _require(
        math.isfinite(validation_field_relative_l2)
        and math.isfinite(best_field_relative_l2)
        and math.isfinite(elapsed_seconds_accumulated)
        and elapsed_seconds_accumulated >= 0.0,
        "checkpoint_finite",
    )
    _require(0 < best_epoch <= epoch and stale_epochs >= 0, "checkpoint_selection")
    _require(len(history) == epoch and int(history[-1]["epoch"]) == epoch, "checkpoint_history")
    _require(bool(model_state_dict) and bool(best_state_dict), "checkpoint_model_state")
    return {
        "schema_version": schema_version,
        "protocol_id": protocol_id,
        "epoch": epoch,
        "optimizer_steps": optimizer_steps,
        "validation_field_relative_l2": validation_field_relative_l2,
        "model_state_dict": dict(model_state_dict),
        "optimizer_state_dict": dict(optimizer_state_dict),
        "scheduler_state_dict": dict(scheduler_state_dict),
        "best_state_dict": dict(best_state_dict),
        "best_field_relative_l2": best_field_relative_l2,
        "best_epoch": best_epoch,
        "stale_epochs": stale_epochs,
        "history": [dict(row) for row in history],
        "smoke": dict(smoke),
        "elapsed_seconds_accumulated": elapsed_seconds_accumulated,
        "rng_state": capture_rng_state(),
        **dict(provenance),
    }


def restore_training_checkpoint(
    path: str | Path,
    *,
    schema_version: str,
    protocol_id: str,
    expected_provenance: Mapping[str, Any],
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    maximum_epochs: int,
) -> dict[str, Any]:
    """Validate and restore a complete checkpoint before the next data update."""

    checkpoint = torch.load(str(path), map_location="cpu", weights_only=True)
    _require(isinstance(checkpoint, Mapping), "checkpoint_mapping")
    _require(checkpoint.get("schema_version") == schema_version, "checkpoint_schema")
    _require(checkpoint.get("protocol_id") == protocol_id, "checkpoint_protocol")
    for key, value in expected_provenance.items():
        _require(checkpoint.get(key) == value, f"checkpoint_provenance_{key}")
    epoch = int(checkpoint.get("epoch", -1))
    optimizer_steps = int(checkpoint.get("optimizer_steps", -1))
    best_epoch = int(checkpoint.get("best_epoch", -1))
    stale_epochs = int(checkpoint.get("stale_epochs", -1))
    history = checkpoint.get("history")
    _require(0 < epoch <= maximum_epochs and optimizer_steps > 0, "checkpoint_progress")
    _require(0 < best_epoch <= epoch and stale_epochs >= 0, "checkpoint_selection")
    _require(
        isinstance(history, list)
        and len(history) == epoch
        and int(history[-1]["epoch"]) == epoch,
        "checkpoint_history",
    )
    for key in (
        "validation_field_relative_l2",
        "best_field_relative_l2",
        "elapsed_seconds_accumulated",
    ):
        _require(math.isfinite(float(checkpoint.get(key, math.nan))), f"checkpoint_{key}")
    _require(
        isinstance(checkpoint.get("model_state_dict"), Mapping)
        and isinstance(checkpoint.get("best_state_dict"), Mapping)
        and isinstance(checkpoint.get("optimizer_state_dict"), Mapping)
        and isinstance(checkpoint.get("scheduler_state_dict"), Mapping),
        "checkpoint_states",
    )
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
    rng = checkpoint.get("rng_state")
    _require(isinstance(rng, Mapping), "checkpoint_rng")
    random.setstate(rng["python_random_state"])
    torch.set_rng_state(rng["torch_rng_state"])
    cuda_states = rng.get("cuda_rng_state_all", [])
    if torch.cuda.is_available():
        _require(bool(cuda_states), "checkpoint_cuda_rng")
        torch.cuda.set_rng_state_all(cuda_states)
    else:
        _require(cuda_states == [], "checkpoint_cpu_rng")
    return dict(checkpoint)
