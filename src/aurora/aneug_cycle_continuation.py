"""Exact-state extension of a completed development curve, not a new seed."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Mapping

import torch

from aurora.aneug_release_730_ghd_gps_baseline import file_sha256
from aurora.aneug_cycle_sampling import KEY as SAMPLING_KEY, epoch_examples


CONTINUATION_INVARIANTS = (
    "upstream", "reader_config_sha256", "private_split_sha256",
    "private_train_audit_sha256", "train_loader_order_sha256",
    "validation_loader_order_sha256", "processed_v5_sha256",
    "decoder_normalizer_archive_sha256", "cycle_output_scale",
    "historical_test_already_opened", "torch", "cuda",
)


def restore_completed_curve(continuation: Mapping, *, model, optimizer, scheduler,
                            optimization, provenance, train_cases, validation_cases,
                            phases, reference_tawss_floor, device, steady_supervision=None):
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
    steady_contract = steady_supervision.contract if steady_supervision else None
    if (parent["provenance"].get("joint_steady_supervision") != steady_contract
            or provenance.get("joint_steady_supervision") != steady_contract
            or parent.get("joint_steady_supervision") != steady_contract):
        raise ValueError("continuation steady supervision changed")
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
    if ((SAMPLING_KEY in parent["provenance"]) != (SAMPLING_KEY in provenance)
            or parent["provenance"].get(SAMPLING_KEY) != provenance.get(SAMPLING_KEY)):
        raise ValueError("continuation cycle sampling changed")
    examples = epoch_examples(provenance, train_cases, optimization["seed"])
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
    updates_per_epoch = math.ceil(examples / optimization["accumulation_cases"])
    steady_seen = set()
    for epoch, row in enumerate(history, 1):
        expected = (epoch, epoch * examples, epoch * examples * phases,
                    epoch * updates_per_epoch)
        if tuple(row[k] for k in ("epoch", "training_cycle_exposures",
                                  "training_phase_field_exposures", "optimizer_updates")) != expected:
            raise ValueError("continuation exposure ledger")
        if steady_supervision is not None:
            from aurora.aneug_release_730_steady_exposure_schedule import ordered_digest
            indices = steady_supervision.indices(epoch, examples)
            steady_seen.update(indices)
            if (row.get("steady_exposures") != epoch * examples
                    or row.get("steady_epoch_order_sha256") != ordered_digest(indices)
                    or row.get("unique_steady_cases_seen") != len(steady_seen)
                    or not math.isfinite(row["train_steady_relative_squared_error"])):
                raise ValueError("continuation steady exposure ledger")
        elif row.get("steady_exposures", 0) != 0:
            raise ValueError("continuation unexpected steady exposure")
    for key in ("training_cycle_exposures", "training_phase_field_exposures", "optimizer_updates"):
        if parent[key] != history[-1][key]:
            raise ValueError("continuation parent exposure ledger")
    if parent.get("steady_exposures") != (completed * examples if steady_supervision else 0):
        raise ValueError("continuation parent steady exposure ledger")
    if steady_supervision is not None and (
            parent.get("unique_steady_cases_seen") != len(steady_seen)
            or parent.get("steady_training_encoder_forwards") != completed * examples
            or parent.get("total_training_field_exposures") != completed * examples * (phases + 1)):
        raise ValueError("continuation parent steady computation ledger")
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
