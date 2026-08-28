"""Validation-only same-field functional fine-tuning of release-730 GHD--GPS.

Each activation starts from the exact same terminal seed-1103 field-only
GHD--GPS checkpoint and executes one objective variant.  Train-only terms
normalize gradients, while every variant selects checkpoints with one common
initial-checkpoint-normalized validation utility.  Locked test and processed-
only extra rows have no runner argument and are never indexed.
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
    backward_case,
    train_wss_rms,
)
from aurora.aneug_release_730_ghd_gps_baseline import (
    Release730GHDGPSUNet,
    _to_device,
    load_development_data,
)
from aurora.aneug_release_730_matched_training import (
    active_parameter_count,
    alignment_terms,
    compute_train_normalizers,
    evaluate,
)
from aurora.aneug_release_730_response_local_candidate import (
    _selection_normalizers,
    common_validation_utility,
)
from aurora.aneug_processed_v4_d9 import model_parameter_count
from aurora.release730_training_continuation import (
    capture_rng_state,
    validate_interrupted_attempt_record,
)


OBJECTIVE_VARIANTS = ("field_only", "all_scalarized", "all_field_anchored")
AUTHORIZED_STAGE = "single_seed_ghd_functional_objective_validation_development"


class Release730GHDFunctionalFinetuneError(RuntimeError):
    """Raised when the objective-selection execution contract is violated."""


class PhysicalGHDGPSCycle(nn.Module):
    """Expose the baseline's normalized decoder in physical WSS coordinates."""

    def __init__(self, backbone: Release730GHDGPSUNet, output_scale: float) -> None:
        super().__init__()
        _require(math.isfinite(output_scale) and output_scale > 0.0, "output_scale")
        self.backbone = backbone
        self.register_buffer("output_scale", torch.tensor(float(output_scale)))

    def forward_cycle(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.backbone(case) * self.output_scale


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730GHDFunctionalFinetuneError(reason)


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
        == "aurora.aneug_release_730_ghd_functional_finetune.v1"
        and config.get("protocol_id")
        == "aneug_release_730_ghd_functional_finetune_v1"
        and config.get("status") == "prepared_validation_development",
        "identity",
    )
    source = config["source"]
    _require(
        source["dataset_revision"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36"
        and source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae"
        and source["steady_norm_bytes"] == 9_632_510_050
        and source["steady_norm_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f"
        and source["ghd_gps_config_sha256"]
        == "0d9ee4615b5af9bf9058920e70252addf5146f06178fb058a2c193be1692bfc9"
        and source["ghd_gps_result_sha256"]
        == "9529b4c69d06e90aec3ccf510fbfe0a55be8c8ee55932beb97ff22ba8c66ebe4"
        and source["ghd_gps_terminal_status_sha256"]
        == "351ac2d3ebadc8755b0d4c054b98e316375b1745ab3a53fd7ffced6a36366c2d"
        and source["ghd_gps_best_checkpoint_sha256"]
        == "6463dcc523170f91ba981833fe1882d40bc98531d13d168aa063349c546ba62b",
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
        == (584, 73, 73, 79)
        and split["train_loader_order_sha256"]
        == "83d40e0579c0999fb380029d11811df835131b62e6bbd3557ad33254f22e6b8f"
        and split["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30"
        and split["read_train_fields"] is True
        and split["read_validation_fields"] is True
        and split["read_locked_test_fields"] is False
        and split["read_processed_only_extra_fields"] is False
        and split["test_opened"] is False,
        "split",
    )
    model = config["model"]
    _require(
        model["family"] == "release730_ghd_gps"
        and (model["width"], model["attention_heads"], model["output_phases"])
        == (128, 4, 80)
        and model["initialization"]
        == "exact_terminal_seed1103_field_only_best_checkpoint"
        and model["separate_functional_head"] is False
        and model["hard_tangent_projection"] is False
        and model["hard_periodic_closure"] is False,
        "model",
    )
    objective = config["objective"]
    _require(
        tuple(objective["variants"]) == OBJECTIVE_VARIANTS
        and objective["same_decoded_field_functionals"]
        == ["mean_vector", "tawss", "valid_reference_support_osi"]
        and objective["checkpoint_selection"]
        == "common_field_plus_mean_of_mean_vector_tawss_and_osi_for_every_objective_variant"
        and objective["reference_tawss_floor_multiplier"] == 0.0001
        and objective["osi_pseudo_huber_delta"] == 0.02
        and objective["functional_to_field_norm_ratio"] == 1.0
        and objective["separate_functional_head"] is False
        and objective["rrt_loss"] is False,
        "objective",
    )
    optimization = config["optimization"]
    _require(
        (
            optimization["seed"],
            optimization["maximum_epochs"],
            optimization["minimum_epochs"],
            optimization["early_stopping_patience"],
            optimization["gradient_accumulation_cases"],
            optimization["checkpoint_interval_epochs"],
        )
        == (1103, 81, 20, 20, 2, 10)
        and optimization["learning_rate"] == 0.0001
        and optimization["weight_decay"] == 0.0001
        and optimization["scheduler"] == "cosine_to_1e-6"
        and optimization["minimum_learning_rate"] == 0.000001,
        "optimization",
    )
    evaluation = config["evaluation"]
    _require(
        evaluation["common_report_space"]
        == "raw_released_physical_cartesian_wss"
        and evaluation["absolute_performance_threshold"] is None
        and evaluation["automatic_winner"] is False
        and evaluation["case_identifiers"] is False,
        "evaluation",
    )
    runtime = config["runtime"]
    _require(
        runtime["allowed_servers"] == ["introai9", "junjinyong"]
        and runtime["queue_by_server"]
        == {"introai9": "coss_a6gpu", "junjinyong": "ssu_a6gpu"}
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2"
        and (runtime["ncpus"], runtime["memory_gb"], runtime["ngpus"])
        == (4, 64, 1),
        "runtime",
    )
    authorization = config["authorization"]
    _require(
        authorization["execute_now"] is False
        and authorization["requires_fresh_private_activation"] is True
        and authorization["one_objective_per_activation"] is True
        and authorization["same_initial_checkpoint_across_variants"] is True
        and authorization[
            "genuine_infrastructure_interruption_exact_state_resume_allowed"
        ]
        is True
        and authorization["continuation_requires_checkpoint_and_terminal_hashes"]
        is True
        and authorization["read_locked_test"] is False
        and authorization["read_processed_only_extra"] is False
        and authorization["paper_performance_claim"] is False
        and authorization["publish_numeric_result"] is False
        and authorization["maintain_public_site"] is False,
        "authorization",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(
    path: str | Path,
    config: Mapping[str, Any],
    expected_commit: str,
    expected_execution_server: str,
    expected_objective_variant: str,
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_ghd_functional_finetune_activation.v1"
        and activation.get("protocol_id") == config["protocol_id"]
        and activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success"
        and activation.get("authorized_stage") == AUTHORIZED_STAGE
        and activation.get("objective_variant") == expected_objective_variant
        and expected_objective_variant in OBJECTIVE_VARIANTS
        and activation.get("training_seed") == config["optimization"]["seed"],
        "activation_identity",
    )
    _require(
        expected_execution_server in config["runtime"]["allowed_servers"]
        and activation.get("server") == expected_execution_server
        and activation.get("queue")
        == config["runtime"]["queue_by_server"][expected_execution_server]
        and activation.get("single_server_per_activation") is True
        and activation.get("duplicate_scientific_cell_across_accounts") is False,
        "activation_server",
    )
    _require(
        activation.get("initial_checkpoint_sha256")
        == config["source"]["ghd_gps_best_checkpoint_sha256"]
        and activation.get("ghd_gps_result_sha256")
        == config["source"]["ghd_gps_result_sha256"]
        and activation.get("ghd_gps_terminal_status_sha256")
        == config["source"]["ghd_gps_terminal_status_sha256"]
        and activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["split"]["train_audit_private_sha256"]
        and activation.get("read_locked_test_or_extra") is False,
        "activation_evidence",
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


def validate_predecessors(
    config: Mapping[str, Any],
    result_path: Path,
    status_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(
        file_sha256(result_path) == config["source"]["ghd_gps_result_sha256"]
        and file_sha256(status_path)
        == config["source"]["ghd_gps_terminal_status_sha256"],
        "predecessor_hash",
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    _require(
        result.get("schema_version")
        == "aurora.private.aneug_release_730_ghd_gps_result.v1"
        and result.get("protocol_id") == "aneug_release_730_ghd_gps_baseline_v1"
        and result.get("status") == "complete"
        and result.get("seed") == 1103
        and result.get("validation_case_count") == 73
        and result.get("validation_case_digest")
        == config["split"]["validation_case_digest"]
        and result.get("validation_loader_order_sha256")
        == config["split"]["validation_loader_order_sha256"]
        and status.get("exit_code") == 0
        and status.get("complete") is True,
        "predecessor_terminal",
    )
    return result, status


def load_initial_checkpoint(
    path: Path,
    expected_sha256: str,
    model: PhysicalGHDGPSCycle,
    predecessor_result: Mapping[str, Any],
) -> dict[str, Any]:
    _require(file_sha256(path) == expected_sha256, "initial_checkpoint_hash")
    payload = safe_torch_load(path, torch)
    _require(
        isinstance(payload, Mapping)
        and payload.get("schema_version")
        == "aurora.private.aneug_release_730_ghd_gps_best.v1"
        and payload.get("protocol_id") == "aneug_release_730_ghd_gps_baseline_v1"
        and payload.get("seed") == 1103
        and payload.get("best_epoch") == predecessor_result.get("best_epoch")
        and math.isclose(
            float(payload.get("validation_field_relative_l2", math.nan)),
            float(
                predecessor_result["validation"]["aggregate"]["field_relative_l2"]
            ),
            rel_tol=0.0,
            abs_tol=1e-12,
        ),
        "initial_checkpoint_identity",
    )
    model.backbone.load_state_dict(payload["model_state_dict"], strict=True)
    return dict(payload)


def make_checkpoint(
    *,
    config: Mapping[str, Any],
    objective_variant: str,
    epoch: int,
    optimizer_steps: int,
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
    train_term_normalizers: Mapping[str, float],
    selection_endpoint_normalizers: Mapping[str, float],
    initial_validation: Mapping[str, Any],
    reference_tawss_floor: float,
    elapsed_seconds_accumulated: float,
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    _require(
        objective_variant in OBJECTIVE_VARIANTS
        and 0 <= best_epoch <= epoch <= config["optimization"]["maximum_epochs"]
        and optimizer_steps > 0
        and len(history) == epoch
        and stale_epochs >= 0,
        "checkpoint_progress",
    )
    return {
        "schema_version": "aurora.private.aneug_release_730_ghd_functional_finetune_checkpoint.v1",
        "protocol_id": config["protocol_id"],
        "objective_variant": objective_variant,
        "training_seed": config["optimization"]["seed"],
        "epoch": epoch,
        "optimizer_steps": optimizer_steps,
        "selection_name": "common_initial_checkpoint_endpoint_normalized_validation_utility",
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
        "train_term_normalizers": dict(train_term_normalizers),
        "selection_endpoint_normalizers": dict(selection_endpoint_normalizers),
        "initial_validation": dict(initial_validation),
        "reference_tawss_floor": reference_tawss_floor,
        "elapsed_seconds_accumulated": elapsed_seconds_accumulated,
        "rng_state": capture_rng_state(),
        **dict(provenance),
    }


def restore_checkpoint(
    path: Path,
    *,
    config: Mapping[str, Any],
    objective_variant: str,
    expected_provenance: Mapping[str, Any],
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
) -> dict[str, Any]:
    payload = safe_torch_load(path, torch)
    _require(
        isinstance(payload, Mapping)
        and payload.get("schema_version")
        == "aurora.private.aneug_release_730_ghd_functional_finetune_checkpoint.v1"
        and payload.get("protocol_id") == config["protocol_id"]
        and payload.get("objective_variant") == objective_variant
        and payload.get("training_seed") == config["optimization"]["seed"],
        "checkpoint_identity",
    )
    for key, value in expected_provenance.items():
        _require(payload.get(key) == value, f"checkpoint_provenance_{key}")
    epoch = int(payload.get("epoch", -1))
    _require(
        0 < epoch <= config["optimization"]["maximum_epochs"]
        and 0 <= int(payload.get("best_epoch", -1)) <= epoch
        and int(payload.get("optimizer_steps", -1)) > 0
        and isinstance(payload.get("history"), list)
        and len(payload["history"]) == epoch,
        "checkpoint_progress",
    )
    model.load_state_dict(payload["model_state_dict"], strict=True)
    optimizer.load_state_dict(payload["optimizer_state_dict"])
    scheduler.load_state_dict(payload["scheduler_state_dict"])
    rng = payload.get("rng_state")
    _require(isinstance(rng, Mapping), "checkpoint_rng")
    random.setstate(rng["python_random_state"])
    torch.set_rng_state(rng["torch_rng_state"])
    cuda_states = rng.get("cuda_rng_state_all", [])
    _require(bool(cuda_states), "checkpoint_cuda_rng")
    torch.cuda.set_rng_state_all(cuda_states)
    return dict(payload)


def run_finetune(
    config: Mapping[str, Any],
    paths: Mapping[str, Path],
    activation: Mapping[str, Any],
    predecessor_result: Mapping[str, Any],
    objective_variant: str,
    result_path: Path,
    checkpoint_directory: Path,
    provenance: Mapping[str, Any],
    resume_checkpoint: Path | None = None,
    resume_expected_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    optimization = config["optimization"]
    seed = int(optimization["seed"])
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
    backbone = Release730GHDGPSUNet(
        topology,
        width=int(config["model"]["width"]),
        heads=int(config["model"]["attention_heads"]),
    )
    model = PhysicalGHDGPSCycle(backbone, cycle_output_scale).to(device)
    initial_checkpoint = load_initial_checkpoint(
        paths["initial_checkpoint"],
        activation["initial_checkpoint_sha256"],
        model,
        predecessor_result,
    )
    reference_tawss_floor = train_wss_rms(train) * float(
        config["objective"]["reference_tawss_floor_multiplier"]
    )
    train_term_normalizers = compute_train_normalizers(
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
    expected_initial_field = float(
        predecessor_result["validation"]["aggregate"]["field_relative_l2"]
    )
    _require(
        math.isclose(
            float(initial_validation["aggregate"]["field_relative_l2"]),
            expected_initial_field,
            rel_tol=0.0,
            abs_tol=1e-8,
        ),
        "initial_validation_reproduction",
    )
    selection_normalizers = _selection_normalizers(initial_validation)
    trainable = tuple(
        parameter for parameter in model.parameters() if parameter.requires_grad
    )
    _require(bool(trainable), "trainable_parameters")
    optimizer = torch.optim.AdamW(
        trainable,
        lr=float(optimization["learning_rate"]),
        weight_decay=float(optimization["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=int(optimization["maximum_epochs"]),
        eta_min=float(optimization["minimum_learning_rate"]),
    )
    maximum_epochs = int(optimization["maximum_epochs"])
    minimum_epochs = int(optimization["minimum_epochs"])
    patience = int(optimization["early_stopping_patience"])
    accumulation = int(optimization["gradient_accumulation_cases"])
    checkpoint_interval = int(optimization["checkpoint_interval_epochs"])
    ratio = float(config["objective"]["functional_to_field_norm_ratio"])
    checkpoint_directory.mkdir(parents=True, exist_ok=True)
    _require(not any(checkpoint_directory.iterdir()), "checkpoint_directory_not_empty")

    initial_selection = common_validation_utility(
        initial_validation["aggregate"], selection_normalizers
    )
    _require(math.isclose(initial_selection, 2.0, abs_tol=1e-12), "initial_utility")
    initial_state = {
        key: value.detach().cpu().clone() for key, value in model.state_dict().items()
    }
    start_epoch = 0
    optimizer_steps = 0
    best_selection = initial_selection
    best_epoch = 0
    best_state: dict[str, torch.Tensor] | None = initial_state
    stale = 0
    history: list[dict[str, Any]] = []
    elapsed_prior = 0.0
    resumed_from_epoch: int | None = None
    if resume_checkpoint is None:
        smoke_case = _to_device(train[0], device)
        smoke_prediction = model.forward_cycle(smoke_case)
        smoke_terms = alignment_terms(
            smoke_prediction, smoke_case, config, reference_tawss_floor
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
                parameter.grad is None
                or bool(torch.isfinite(parameter.grad).all().item())
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
    else:
        _require(resume_expected_provenance is not None, "resume_provenance")
        restored = restore_checkpoint(
            resume_checkpoint,
            config=config,
            objective_variant=objective_variant,
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
            restored["train_term_normalizers"] == train_term_normalizers
            and restored["selection_endpoint_normalizers"]
            == selection_normalizers
            and math.isclose(
                float(restored["reference_tawss_floor"]),
                reference_tawss_floor,
                rel_tol=0.0,
                abs_tol=1e-12,
            ),
            "resume_objective_state",
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
        objective_sum = 0.0
        conflicts = 0
        cosine_sum = 0.0
        for step, index in enumerate(order):
            case = _to_device(train[index], device)
            prediction = model.forward_cycle(case)
            terms = alignment_terms(prediction, case, config, reference_tawss_floor)
            diagnostic = backward_case(
                model,
                terms,
                train_term_normalizers,
                objective_variant,
                accumulation,
                ratio,
            )
            objective_sum += float(diagnostic["scalarized_value"])
            conflicts += int(bool(diagnostic["projection_applied"]))
            cosine_sum += float(diagnostic["gradient_cosine_before"])
            if (step + 1) % accumulation == 0:
                torch.nn.utils.clip_grad_norm_(
                    trainable, float(optimization["gradient_clip_norm"])
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
            objective_variant,
            reference_tawss_floor,
            None,
            device,
        )
        selection_value = common_validation_utility(
            validation_result["aggregate"], selection_normalizers
        )
        row = {
            "epoch": epoch + 1,
            "optimizer_steps": optimizer_steps,
            "training_objective": objective_sum / len(order),
            "selection_value": selection_value,
            "validation_field_relative_l2": float(
                validation_result["aggregate"]["field_relative_l2"]
            ),
            "validation_mean_vector_error": float(
                validation_result["aggregate"][
                    "mean_vector_tawss_normalized_l2"
                ]
            ),
            "validation_tawss_error": float(
                validation_result["aggregate"][
                    "tawss_normalized_absolute_error"
                ]
            ),
            "validation_osi_mae": float(
                validation_result["aggregate"]["osi_mae"]
            ),
            "gradient_conflict_fraction": (
                conflicts / len(order)
                if objective_variant == "all_field_anchored"
                else None
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
                make_checkpoint(
                    config=config,
                    objective_variant=objective_variant,
                    epoch=epoch + 1,
                    optimizer_steps=optimizer_steps,
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
                    selection_endpoint_normalizers=selection_normalizers,
                    initial_validation=initial_validation,
                    reference_tawss_floor=reference_tawss_floor,
                    elapsed_seconds_accumulated=(
                        elapsed_prior + time.monotonic() - started
                    ),
                    provenance=provenance,
                ),
            )
        if epoch + 1 >= minimum_epochs and stale >= patience:
            break

    _require(best_state is not None and best_epoch >= 0, "best_checkpoint")
    model.load_state_dict(best_state, strict=True)
    final_validation = evaluate(
        model,
        validation,
        config,
        objective_variant,
        reference_tawss_floor,
        None,
        device,
    )
    final_validation["common_validation_utility"] = common_validation_utility(
        final_validation["aggregate"], selection_normalizers
    )
    _strict_atomic_torch_save(
        checkpoint_directory / "best.pt",
        {
            "schema_version": "aurora.private.aneug_release_730_ghd_functional_finetune_best.v1",
            "protocol_id": config["protocol_id"],
            "objective_variant": objective_variant,
            "training_seed": seed,
            "best_epoch": best_epoch,
            "selection_name": "common_initial_checkpoint_endpoint_normalized_validation_utility",
            "best_selection_value": best_selection,
            "model_state_dict": best_state,
            "initial_checkpoint_embedded": False,
            "initial_checkpoint_sha256": activation["initial_checkpoint_sha256"],
            "train_term_normalizers": train_term_normalizers,
            "selection_endpoint_normalizers": selection_normalizers,
            "reference_tawss_floor": reference_tawss_floor,
            **dict(provenance),
        },
    )
    result = {
        "schema_version": "aurora.private.aneug_release_730_ghd_functional_finetune_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_validation_development",
        "objective_variant": objective_variant,
        "training_seed": seed,
        "initial_model_family": "release730_ghd_gps",
        "initial_checkpoint_sha256": activation["initial_checkpoint_sha256"],
        "initial_checkpoint_best_epoch": initial_checkpoint["best_epoch"],
        "same_decoded_field_functionals": True,
        "separate_functional_head": False,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "optimizer_steps": optimizer_steps,
        "best_selection_value": best_selection,
        "selection_name": "common_initial_checkpoint_endpoint_normalized_validation_utility",
        "parameter_count": model_parameter_count(model),
        "active_parameter_count": active_parameter_count(model),
        "elapsed_seconds": elapsed_prior + time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "reference_tawss_floor": reference_tawss_floor,
        "train_term_normalizers": train_term_normalizers,
        "selection_endpoint_normalizers": selection_normalizers,
        "initial_validation": initial_validation,
        "validation": final_validation,
        "history": history,
        "continuation_mode": resume_checkpoint is not None,
        "resumed_from_epoch": resumed_from_epoch,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
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
    parser.add_argument(
        "--expected-execution-server", choices=("introai9", "junjinyong")
    )
    parser.add_argument("--objective-variant", choices=OBJECTIVE_VARIANTS)
    parser.add_argument("--initial-checkpoint", type=Path)
    parser.add_argument("--ghd-gps-result", type=Path)
    parser.add_argument("--ghd-gps-terminal-status", type=Path)
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
        args.expected_execution_server,
        args.objective_variant,
        args.initial_checkpoint,
        args.ghd_gps_result,
        args.ghd_gps_terminal_status,
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
        args.expected_execution_server,
        args.objective_variant,
    )
    predecessor_result, _ = validate_predecessors(
        config, args.ghd_gps_result, args.ghd_gps_terminal_status
    )
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
        "execution_server": args.expected_execution_server,
        "execution_queue": config["runtime"]["queue_by_server"][
            args.expected_execution_server
        ],
        "training_config_sha256": file_sha256(args.config),
        "initial_checkpoint_sha256": activation["initial_checkpoint_sha256"],
        "ghd_gps_result_sha256": activation["ghd_gps_result_sha256"],
        "ghd_gps_terminal_status_sha256": activation[
            "ghd_gps_terminal_status_sha256"
        ],
        "processed_v5_sha256": config["source"]["processed_v5_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        "validation_case_digest": config["split"]["validation_case_digest"],
        "validation_loader_order_sha256": config["split"][
            "validation_loader_order_sha256"
        ],
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
    run_finetune(
        config,
        {
            "initial_checkpoint": args.initial_checkpoint,
            "transient": args.transient,
            "steady": args.steady,
            "public_split": args.public_split,
            "private_split": args.private_split,
            "train_audit_public": args.train_audit_public,
            "train_audit_private": args.train_audit_private,
        },
        activation,
        predecessor_result,
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
