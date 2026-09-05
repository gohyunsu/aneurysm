"""Exact-state extension of a completed development curve, not a new seed."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Mapping

import torch

from aurora.aneug_release_730_ghd_gps_baseline import file_sha256


CONTINUATION_INVARIANTS = (
    "upstream", "reader_config_sha256", "private_split_sha256",
    "private_train_audit_sha256", "train_loader_order_sha256",
    "validation_loader_order_sha256", "processed_v5_sha256",
    "decoder_normalizer_archive_sha256", "cycle_output_scale",
    "historical_test_already_opened", "torch", "cuda",
)


def restore_completed_curve(continuation: Mapping, *, model, optimizer, scheduler,
                            optimization, provenance, train_cases, validation_cases,
                            phases, reference_tawss_floor, device):
    """Restore a hash-bound parent, allowing only a larger total epoch budget.

    The caller separately pins architecture and runtime compatibility. This
    helper checks data/model provenance, state shapes, optimization, selection,
    exposure ledgers and stochastic state before the first new model update.
    A completed-curve extension is deliberately distinct from interrupted-run
    recovery, which can have incomplete epoch/validation evidence.
    """
    paths = {}
    for key in ("checkpoint", "parent_result"):
        paths[key] = Path(continuation[key])
        if file_sha256(paths[key]) != continuation[key + "_sha256"]:
            raise ValueError(f"continuation {key} hash")
    parent = json.loads(paths["parent_result"].read_text())
    if (parent.get("schema_version") != "aurora.private.architecture_development_result.v3"
            or parent.get("status") != "completed_validation_development"):
        raise ValueError("continuation completed parent required")
    for key in ("test_field_access_performed", "processed_extra_field_access_performed",
                "independent_confirmatory_evaluation", "result_is_architectural_novelty_evidence_by_itself"):
        if parent.get(key) is not False:
            raise ValueError("continuation evidence boundary")
    if parent.get("raw_predictions_stored") != 0:
        raise ValueError("continuation raw prediction scope")
    old_opt = parent["optimization"]
    completed = old_opt["epochs"]
    if type(completed) is not int or not 0 < completed < optimization["epochs"]:
        raise ValueError("continuation must extend total epoch budget")
    if {k: v for k, v in old_opt.items() if k != "epochs"} != {
            k: v for k, v in optimization.items() if k != "epochs"}:
        raise ValueError("continuation optimization changed beyond total epochs")
    for key in CONTINUATION_INVARIANTS:
        if key not in provenance or parent["provenance"].get(key) != provenance[key]:
            raise ValueError(f"continuation provenance invariant: {key}")
    if (parent["train_cases"], parent["validation_cases"], parent["phase_count"]) != (
            train_cases, validation_cases, phases):
        raise ValueError("continuation admitted dimensions")
    if (parent["reference_tawss_floor"] != reference_tawss_floor
            or parent["parameter_count"] != sum(p.numel() for p in model.parameters())):
        raise ValueError("continuation model/metric scale")
    if not any(a["sha256"] == continuation["checkpoint_sha256"]
               and a["file"] == f"checkpoints/epoch_{completed:03d}.pt"
               for a in parent["checkpoints"]):
        raise ValueError("continuation checkpoint is not parent terminal state")
    checkpoint = torch.load(paths["checkpoint"], map_location="cpu", weights_only=True)
    if (checkpoint.get("schema_version") != "aurora.private.architecture_development_checkpoint.v3"
            or checkpoint["completed_epoch"] != completed
            or checkpoint["optimization"] != old_opt
            or checkpoint["provenance"] != parent["provenance"]
            or checkpoint["reference_tawss_floor"] != reference_tawss_floor):
        raise ValueError("continuation checkpoint identity")
    history = checkpoint["history"]
    if len(history) != completed:
        raise ValueError("continuation history length")
    updates_per_epoch = math.ceil(train_cases / optimization["accumulation_cases"])
    for epoch, row in enumerate(history, 1):
        expected = (epoch, epoch * train_cases, epoch * train_cases * phases,
                    epoch * updates_per_epoch)
        if tuple(row[k] for k in ("epoch", "training_cycle_exposures",
                                  "training_phase_field_exposures", "optimizer_updates")) != expected:
            raise ValueError("continuation exposure ledger")
    for key in ("training_cycle_exposures", "training_phase_field_exposures", "optimizer_updates"):
        if parent[key] != history[-1][key]:
            raise ValueError("continuation parent exposure ledger")
    if parent["validation_cycle_forwards"] != validation_cases * sum("validation" in row for row in history):
        raise ValueError("continuation evaluation ledger")
    eligible = [row for row in history if "validation" in row]
    if not eligible or any(not math.isfinite(row["validation"]["field_relative_l2"]) for row in eligible):
        raise ValueError("continuation validation history")
    best = min(eligible, key=lambda row: (row["validation"]["field_relative_l2"], row["epoch"]))
    if (parent["checkpoint_selection"] != "lowest_validation_field_rL2_then_earliest"
            or parent["selected_epoch"] != best["epoch"]
            or checkpoint["best_epoch"] != best["epoch"]
            or checkpoint["best_value"] != best["validation"]["field_relative_l2"]
            or checkpoint["best_validation"] != parent["selected_validation"]):
        raise ValueError("continuation checkpoint selection")
    if checkpoint["scheduler_state_dict"]["last_epoch"] != completed:
        raise ValueError("continuation scheduler progress")
    elapsed = parent["elapsed_training_and_validation_seconds"]
    if not math.isfinite(elapsed) or elapsed < 0:
        raise ValueError("continuation elapsed accounting")
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
    rng = checkpoint["rng_state"]
    random.setstate(rng["python_random_state"])
    torch.set_rng_state(rng["torch_rng_state"])
    cuda_states = rng["cuda_rng_state_all"]
    if device.type == "cuda":
        if len(cuda_states) != torch.cuda.device_count():
            raise ValueError("continuation CUDA RNG device count")
        torch.cuda.set_rng_state_all(cuda_states)
    elif cuda_states:
        raise ValueError("continuation cannot silently move CUDA RNG to CPU")
    receipt = {
        "parent_result_sha256": continuation["parent_result_sha256"],
        "parent_checkpoint_sha256": continuation["checkpoint_sha256"],
        "parent_completed_epoch": completed, "start_epoch": completed + 1,
        "parent_provenance": parent["provenance"],
        "parent_checkpoint_inventory": parent["checkpoints"],
        "new_independent_seed": False, "optimizer_scheduler_rng_restored": True,
        "parent_elapsed_training_and_validation_seconds": elapsed,
    }
    return checkpoint, parent, receipt
