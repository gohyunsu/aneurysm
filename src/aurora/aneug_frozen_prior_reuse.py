"""Reuse a verified terminal steady predictor without another label exposure.

This component performs no optimization, sampling, dataset read or queue action.
The caller binds the original scientific provenance and eligible training pool.
Its returned original result retains the prior's already incurred cost.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import torch

from aurora.aneug_release_730_ghd_gps_baseline import file_sha256
from aurora.aneug_release_730_matched_steady_stream import epoch_exposure_indices
from aurora.aneug_release_730_steady_exposure_schedule import ordered_digest
from aurora.aneug_steady_prior_training import validate_optimization


def load_completed_steady_prior(model, *, result_path, result_sha256,
                                checkpoint_path, checkpoint_sha256,
                                expected_provenance, optimization,
                                eligible_indices, device):
    """Return the unchanged training result and a zero-new-training receipt."""
    validate_optimization(optimization)
    paths = (Path(result_path), Path(checkpoint_path))
    if any(file_sha256(p) != h for p, h in zip(paths, (result_sha256, checkpoint_sha256))):
        raise ValueError("completed prior artifact hash")
    result = json.loads(paths[0].read_text())
    eligible = tuple(eligible_indices)
    if (not eligible or len(set(eligible)) != len(eligible)
            or any(type(i) is not int or i < 0 for i in eligible)):
        raise ValueError("explicit unique eligible prior rows required")
    if (result.get("schema_version") != "aurora.private.steady_prior_result.v3"
            or result.get("status") != "completed_steady_pretraining"
            or result.get("provenance") != dict(expected_provenance)
            or result.get("optimization") != dict(optimization)
            or result.get("eligible_case_count") != len(eligible)
            or result.get("eligible_order_sha256") != ordered_digest(eligible)
            or result.get("prior_checkpoint_sha256") != checkpoint_sha256
            or result.get("checkpoint_selection") != "fixed_terminal_steady_budget_no_validation_selection"):
        raise ValueError("completed prior scientific identity")
    if (result.get("new_test_field_reads") != 0 or result.get("new_extra_field_reads") != 0
            or result.get("raw_predictions_stored") != 0
            or result.get("transient_phase_field_exposures") != 0):
        raise ValueError("completed prior data scope")
    count, epochs = optimization["cases_per_epoch"], optimization["epochs"]
    updates = math.ceil(count / optimization["accumulation_cases"])
    seen = set()
    if len(result["history"]) != epochs:
        raise ValueError("completed prior history length")
    for epoch, row in enumerate(result["history"], 1):
        seen.update(epoch_exposure_indices(eligible, epoch=epoch - 1,
                    cases_per_epoch=count, seed=optimization["seed"]))
        if ((row["epoch"], row["steady_exposures"], row["optimizer_updates"],
             row["unique_steady_cases_seen"]) != (epoch, epoch * count, epoch * updates, len(seen))
                or not math.isfinite(row["train_relative_squared_error"])):
            raise ValueError("completed prior exposure history")
    if (result["steady_exposures"] != epochs * count or result["optimizer_updates"] != epochs * updates
            or result["unique_steady_cases_seen"] != len(seen)
            or result["parameter_count"] != sum(p.numel() for p in model.parameters())):
        raise ValueError("completed prior exposure or model accounting")
    if (not math.isfinite(result["elapsed_seconds"]) or result["elapsed_seconds"] < 0
            or type(result["peak_cuda_allocated_bytes"]) is not int
            or result["peak_cuda_allocated_bytes"] < 0):
        raise ValueError("completed prior resource accounting")
    checkpoint = torch.load(paths[1], map_location="cpu", weights_only=True)
    if (checkpoint["provenance"] != dict(expected_provenance)
            or checkpoint["completed_epoch"] != epochs
            or checkpoint["eligible_order_sha256"] != ordered_digest(eligible)):
        raise ValueError("fixed terminal prior checkpoint identity")
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.to(device)
    model.requires_grad_(False)
    model.eval()
    receipt = dict(schema_version="aurora.completed_steady_prior_reuse.v3",
        parent_result_sha256=result_sha256, prior_checkpoint_sha256=checkpoint_sha256,
        terminal_prior_loaded=True, new_steady_label_exposures=0, new_optimizer_updates=0,
        frozen_parameters_and_eval_mode=True, original_training_cost_retained=True)
    return result, receipt
