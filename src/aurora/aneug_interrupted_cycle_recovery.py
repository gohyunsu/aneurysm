"""Restore an interrupted complete-cycle run without inventing a final result.

Only a completed checkpoint epoch is replayable. A private orchestrator must
first establish that the original job is terminal and a successor is permitted;
this local validator neither queries a scheduler nor authorizes submission.
Unmeasured legacy time/memory and work discarded after the checkpoint stay
unknown. Recovery is not an independent seed or a fresh scientific result.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import random

import torch

from aurora.aneug_release_730_ghd_gps_baseline import file_sha256
from aurora.aneug_cycle_sampling import epoch_examples


def restore_interrupted_curve(recovery, *, model, optimizer, scheduler, optimization,
                              provenance, train_cases, validation_cases, phases,
                              reference_tawss_floor, device):
    paths = {}
    for key in ("checkpoint", "terminal_evidence"):
        paths[key] = Path(recovery[key])
        if file_sha256(paths[key]) != recovery[key + "_sha256"]:
            raise ValueError("interrupted recovery artifact hash: " + key)
    terminal = json.loads(paths["terminal_evidence"].read_text())
    if (terminal.get("schema_version") != "aurora.interrupted_attempt_evidence.v3"
            or terminal.get("state") != "F" or terminal.get("run_count") != 1
            or type(terminal.get("exit_status")) is not int or terminal["exit_status"] == 0
            or terminal.get("scientific_result_present") is not False
            or terminal.get("recovery_authorized") is not True
            or terminal.get("reason") not in ("walltime", "documented_external_interruption")):
        raise ValueError("terminal interrupted attempt and separate recovery authority required")
    cp = torch.load(paths["checkpoint"], map_location="cpu", weights_only=True)
    completed = cp.get("completed_epoch")
    if (cp.get("schema_version") != "aurora.private.architecture_development_checkpoint.v3"
            or cp["optimization"] != dict(optimization) or cp["provenance"] != dict(provenance)
            or type(completed) is not int or not 0 < completed < optimization["epochs"]
            or cp["reference_tawss_floor"] != reference_tawss_floor):
        raise ValueError("interrupted checkpoint science, fixed budget or epoch identity")
    if provenance.get("joint_steady_supervision") is not None:
        raise ValueError("paired joint-steady recovery needs its separate sampler ledger")
    history = cp["history"]
    if len(history) != completed:
        raise ValueError("interrupted checkpoint history length")
    examples = epoch_examples(provenance, train_cases, optimization["seed"])
    steps = math.ceil(examples / optimization["accumulation_cases"])
    validations = []
    for epoch, row in enumerate(history, 1):
        if ((row["epoch"], row["training_cycle_exposures"], row["training_phase_field_exposures"],
             row["optimizer_updates"]) != (epoch, epoch * examples, epoch * examples * phases, epoch * steps)
                or row.get("steady_exposures", 0) != 0
                or not math.isfinite(row["train_relative_squared_error"])):
            raise ValueError("interrupted checkpoint exposure history")
        if ("validation" in row) != (epoch % optimization["validation_interval"] == 0):
            raise ValueError("interrupted checkpoint validation schedule")
        expected_lr = optimization["learning_rate"] * optimization["gamma"] ** (
            epoch // optimization["step_size_epochs"])
        if not math.isclose(row["learning_rate_next_epoch"], expected_lr, rel_tol=1e-12):
            raise ValueError("interrupted checkpoint learning-rate history")
        if "validation" in row:
            if not math.isfinite(row["validation"]["field_relative_l2"]):
                raise ValueError("interrupted checkpoint nonfinite selection metric")
            validations.append(row)
    if validations:
        best = min(validations, key=lambda x: (x["validation"]["field_relative_l2"], x["epoch"]))
        evaluation = cp["best_validation"]
        if (cp["best_epoch"] != best["epoch"] or cp["best_value"] != best["validation"]["field_relative_l2"]
                or evaluation["aggregate"] != best["validation"]
                or evaluation["case_count"] != validation_cases):
            raise ValueError("interrupted checkpoint best-validation identity")
    elif (cp["best_epoch"] != 0 or cp["best_state_dict"] is not None
          or cp["best_validation"] is not None or cp["best_value"] != float("inf")):
        raise ValueError("interrupted checkpoint has an unobserved validation selection")
    if cp["scheduler_state_dict"]["last_epoch"] != completed:
        raise ValueError("interrupted checkpoint scheduler progress")
    cost = cp.get("execution_accounting", {})
    elapsed = cost.get("elapsed_training_and_validation_seconds")
    peak = cost.get("peak_cuda_allocated_bytes")
    if ((elapsed is not None and (not math.isfinite(elapsed) or elapsed < 0))
            or (peak is not None and (type(peak) is not int or peak < 0))):
        raise ValueError("interrupted checkpoint resource accounting")
    rng = cp["rng_state"]
    cuda_states = rng["cuda_rng_state_all"]
    if ((device.type == "cuda" and len(cuda_states) != torch.cuda.device_count())
            or (device.type != "cuda" and cuda_states)):
        raise ValueError("interrupted recovery CUDA RNG device count")
    model.load_state_dict(cp["model_state_dict"], strict=True)
    optimizer.load_state_dict(cp["optimizer_state_dict"])
    scheduler.load_state_dict(cp["scheduler_state_dict"])
    random.setstate(rng["python_random_state"])
    torch.set_rng_state(rng["torch_rng_state"])
    if device.type == "cuda":
        torch.cuda.set_rng_state_all(cuda_states)
    accounting = dict(training_cycle_exposures=completed * examples,
        optimizer_updates=completed * steps, validation_cycle_forwards=len(validations) * validation_cases,
        elapsed_training_and_validation_seconds=elapsed, peak_cuda_allocated_bytes=peak)
    receipt = dict(schema_version="aurora.interrupted_cycle_recovery.v3",
        parent_checkpoint_sha256=recovery["checkpoint_sha256"],
        terminal_evidence_sha256=recovery["terminal_evidence_sha256"],
        parent_completed_epoch=completed, start_epoch=completed + 1,
        original_total_epochs=optimization["epochs"], new_independent_seed=False,
        optimizer_scheduler_rng_restored=True, parent_scientific_result_exists=False,
        discarded_post_checkpoint_work_not_in_effective_exposure_ledger=True,
        total_attempt_cost_including_discarded_work_known=False,
        legacy_checkpoint_cost_unknown=not cost)
    return cp, accounting, receipt
