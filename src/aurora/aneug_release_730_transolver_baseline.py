"""Release-730 raw-field Transolver strong comparator."""

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

from aurora.aneug_processed_v4_d14_transolver_control import FullCycleTransolver
from aurora.aneug_processed_v4_d9 import field_loss, model_parameter_count
from aurora.aneug_release_730_ghd_gps_baseline import load_development_data
from aurora.aneug_release_730_official_graphunet_baseline import extended_case_metrics
from aurora.release730_training_continuation import (
    make_training_checkpoint,
    restore_training_checkpoint,
    validate_interrupted_attempt_record,
)


class Release730TransolverError(RuntimeError):
    """Raised when a release-730 Transolver boundary fails."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730TransolverError(reason)


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


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_transolver_baseline.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id") == "aneug_release_730_transolver_baseline_v1",
        "protocol_id",
    )
    _require(
        config.get("status")
        == "prepared_non_executable_until_response_oracle_and_ghd_gps_terminal",
        "status",
    )
    source = config["source"]
    _require(
        source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36"
        and source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae"
        and source["steady_norm_bytes"] == 9_632_510_050
        and source["steady_norm_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "dataset_source",
    )
    _require(
        source["repository"] == "thuml/Transolver"
        and source["commit"] == "75e0f67643806a81cd1d3f6adc88dd8c02416fe7"
        and source["irregular_mesh_model_sha256"]
        == "1d0c1b932411ac408d8d00ca047d7f875c3176e7b001db802d30c065a7416d74"
        and source["license"] == "MIT"
        and source["license_sha256"]
        == "2c919cd03fa823bf7eefc00a957ff8324c865cd22aa5285e563dc4b558084f25",
        "transolver_source",
    )
    identity = config["comparison_identity"]
    _require(
        identity["label"]
        == "release730_matched_information_full_cycle_transolver_adaptation"
        and identity["exact_upstream_reproduction"] is False
        and identity["proposed_method"] is False,
        "comparison_identity",
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
        split["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "validation_order",
    )
    _require(split["read_train_fields"] and split["read_validation_fields"], "development_read")
    _require(
        not split["read_locked_test_fields"]
        and not split["read_processed_only_extra_fields"]
        and not split["test_opened"],
        "sealed_read",
    )
    target = config["target_and_metric"]
    _require(
        target["common_report_space"] == "raw_released_physical_cartesian_wss"
        and target["training_scale"] == "train_audit_global_physical_vector_rms",
        "target",
    )
    _require(
        not target["hard_tangent_projection"] and not target["hard_periodic_closure"],
        "hard_constraint",
    )
    architecture = config["architecture"]
    _require(
        (
            architecture["width"],
            architecture["attention_heads"],
            architecture["blocks"],
            architecture["slices"],
            architecture["mlp_ratio"],
            architecture["dropout"],
            architecture["output_phases"],
        )
        == (256, 8, 8, 32, 2, 0.0, 80),
        "architecture",
    )
    _require(
        architecture["output_coordinates"] == "raw_cartesian_no_hard_projection",
        "output_coordinates",
    )
    optimization = config["optimization"]
    _require(
        (
            optimization["seed"],
            optimization["maximum_epochs"],
            optimization["minimum_epochs"],
            optimization["early_stopping_patience"],
            optimization["gradient_accumulation_cases"],
            optimization["validation_interval_epochs"],
            optimization["checkpoint_interval_epochs"],
        )
        == (1103, 251, 80, 40, 2, 1, 10),
        "optimization",
    )
    _require(
        optimization["learning_rate"] == 3e-4
        and optimization["weight_decay"] == 1e-4
        and optimization["scheduler"] == "step_50_gamma_0p75"
        and optimization["checkpoint_selection"]
        == "lowest_validation_primary_field_metric_then_earliest_epoch",
        "optimizer_selection",
    )
    _require(config["decision_rule"]["absolute_performance_threshold"] is None, "threshold")
    _require(config["decision_rule"]["automatic_winner"] is False, "winner")
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
    _require(not authorization["execute_now"], "execute_now")
    for key in (
        "requires_direct_baseline_terminal_record",
        "requires_fresh_private_activation",
        "record_other_prior_terminal_context_if_available",
    ):
        _require(authorization[key] is True, f"authorization_{key}")
    _require(authorization["requires_ghd_gps_terminal_record"], "ghd_predecessor")
    _require(
        authorization["requires_response_oracle_terminal_record"],
        "oracle_predecessor",
    )
    _require(
        authorization["genuine_infrastructure_interruption_exact_state_resume_allowed"]
        and authorization[
            "continuation_requires_fresh_private_activation_and_checkpoint_sha256"
        ],
        "continuation",
    )
    for key in (
        "completed_scientific_run_resume_allowed",
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


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_transolver_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "single_seed_validation_comparator",
        "activation_stage",
    )
    for key in (
        "direct_baseline_terminal_record_sha256",
        "ghd_gps_terminal_record_sha256",
        "response_oracle_terminal_record_sha256",
    ):
        _require(_is_sha256(activation.get(key)), key)
    _require(activation.get("read_locked_test_or_extra") is False, "activation_scope")
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["split"]["train_audit_private_sha256"],
        "activation_evidence",
    )
    continuation = activation.get("continuation_mode")
    _require(isinstance(continuation, bool), "continuation_mode")
    if continuation:
        _require(
            _is_sha256(activation.get("resume_checkpoint_sha256"))
            and _is_sha256(
                activation.get("prior_attempt_terminal_record_sha256")
            ),
            "continuation_evidence",
        )
    else:
        _require(
            activation.get("resume_checkpoint_sha256") is None
            and activation.get("prior_attempt_terminal_record_sha256") is None,
            "continuation_evidence",
        )
    return activation


def validate_predecessor_terminal_record(
    path: str | Path,
    activation: Mapping[str, Any],
    activation_key: str,
) -> str:
    """Bind execution to exact preserved predecessor terminal bytes."""

    _require(
        activation_key
        in {
            "response_oracle_terminal_record_sha256",
            "ghd_gps_terminal_record_sha256",
        },
        "terminal_record_key",
    )
    observed = file_sha256(path)
    _require(observed == activation[activation_key], f"{activation_key}_mismatch")
    return observed


class Release730FullCycleTransolver(FullCycleTransolver):
    """Transolver adaptation that preserves the released Cartesian target."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.encoded_width = int(self.output.in_features)

    def encode_geometry(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        """Return the shared per-node representation before the cycle head."""

        coordinates = case["coordinates"]
        normals = case["normals"]
        weights = case["vertex_weights"]
        relative_area = torch.log(
            torch.clamp(
                weights / torch.clamp(weights.mean(), min=1e-12), min=1e-8
            )
        ).unsqueeze(-1)
        features = self.node_input(
            torch.cat((coordinates, normals, relative_area), dim=-1)
        )
        condition = self.ghd_conditioner(case["ghd"].reshape(1, -1)).squeeze(0)
        features = features + condition.unsqueeze(0)
        for block in self.blocks:
            features = block(features)
        return features

    def decode_cycle(self, features: torch.Tensor) -> torch.Tensor:
        """Decode a normalized complete-cycle field from shared features."""

        _require(
            features.ndim == 2 and features.shape[1] == self.encoded_width,
            "encoded_features",
        )
        raw = self.output(self.output_norm(features))
        raw = raw.reshape(features.shape[0], self.output_phases, 3)
        return raw.permute(1, 0, 2).contiguous()

    def forward(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.decode_cycle(self.encode_geometry(case))


def _to_device(
    case: Mapping[str, torch.Tensor], device: torch.device
) -> dict[str, torch.Tensor]:
    return {
        key: value.to(device=device, non_blocking=True) for key, value in case.items()
    }


@torch.no_grad()
def evaluate(
    model: Release730FullCycleTransolver,
    cases: Sequence[Mapping[str, torch.Tensor]],
    device: torch.device,
    wss_scale: float,
) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    for cpu_case in cases:
        case = _to_device(cpu_case, device)
        prediction = model(case) * wss_scale
        per_case.append(
            extended_case_metrics(
                prediction,
                case["wss"],
                case["vertex_weights"],
                case["normals"],
            )
        )
    keys = tuple(per_case[0])
    return {
        "aggregate": {
            key: sum(row[key] for row in per_case) / len(per_case) for key in keys
        },
        "per_case_without_identifiers": per_case,
        "case_count": len(per_case),
    }


def run_development(
    config: Mapping[str, Any],
    paths: Mapping[str, Path],
    result_path: Path,
    checkpoint_directory: Path,
    provenance: Mapping[str, Any],
    resume_checkpoint: Path | None = None,
    resume_expected_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    optimization = config["optimization"]
    architecture = config["architecture"]
    seed = int(optimization["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(4)
    device = torch.device("cuda")
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    train, validation, _topology, wss_scale = load_development_data(
        config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
    )
    model = Release730FullCycleTransolver(
        width=int(architecture["width"]),
        heads=int(architecture["attention_heads"]),
        blocks=int(architecture["blocks"]),
        slices=int(architecture["slices"]),
        mlp_ratio=int(architecture["mlp_ratio"]),
        dropout=float(architecture["dropout"]),
        output_phases=int(architecture["output_phases"]),
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(optimization["learning_rate"]),
        weight_decay=float(optimization["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=int(optimization["step_size_epochs"]),
        gamma=float(optimization["gamma"]),
    )
    maximum_epochs = int(optimization["maximum_epochs"])
    minimum_epochs = int(optimization["minimum_epochs"])
    patience = int(optimization["early_stopping_patience"])
    accumulation = int(optimization["gradient_accumulation_cases"])
    checkpoint_interval = int(optimization["checkpoint_interval_epochs"])
    checkpoint_directory.mkdir(parents=True, exist_ok=True)
    _require(not any(checkpoint_directory.iterdir()), "checkpoint_directory_not_empty")
    _require(len(train) % accumulation == 0, "incomplete_effective_batch")
    start_epoch = 0
    best_field = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, float | int]] = []
    optimizer_steps = 0
    elapsed_seconds_prior = 0.0
    resumed_from_epoch: int | None = None
    if resume_checkpoint is None:
        smoke_case = _to_device(train[0], device)
        smoke_output = model(smoke_case)
        smoke_loss = field_loss(
            smoke_output,
            smoke_case["wss"] / wss_scale,
            smoke_case["vertex_weights"],
        )
        smoke_loss.backward()
        _require(bool(torch.isfinite(smoke_loss).item()), "smoke")
        optimizer.zero_grad(set_to_none=True)
        smoke = {
            "finite_forward_backward": True,
            "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        }
        del smoke_case, smoke_output, smoke_loss
    else:
        _require(resume_expected_provenance is not None, "resume_provenance")
        restored = restore_training_checkpoint(
            resume_checkpoint,
            schema_version="aurora.private.aneug_release_730_transolver_checkpoint.v2",
            protocol_id=config["protocol_id"],
            expected_provenance=resume_expected_provenance,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            maximum_epochs=maximum_epochs,
        )
        start_epoch = int(restored["epoch"])
        resumed_from_epoch = start_epoch
        optimizer_steps = int(restored["optimizer_steps"])
        best_field = float(restored["best_field_relative_l2"])
        best_epoch = int(restored["best_epoch"])
        best_state = dict(restored["best_state_dict"])
        stale = int(restored["stale_epochs"])
        history = [dict(row) for row in restored["history"]]
        smoke = dict(restored["smoke"])
        elapsed_seconds_prior = float(restored["elapsed_seconds_accumulated"])

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
        epoch_loss = 0.0
        for step, index in enumerate(order):
            case = _to_device(train[index], device)
            prediction = model(case)
            loss = field_loss(
                prediction,
                case["wss"] / wss_scale,
                case["vertex_weights"],
            )
            _require(bool(torch.isfinite(loss).item()), "training_loss")
            (loss / accumulation).backward()
            epoch_loss += float(loss.detach().item())
            if (step + 1) % accumulation == 0:
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), float(optimization["gradient_clip_norm"])
                )
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                optimizer_steps += 1
        scheduler.step()
        validation_result = evaluate(model, validation, device, wss_scale)
        validation_field = float(
            validation_result["aggregate"]["field_relative_l2"]
        )
        _require(math.isfinite(validation_field), "validation_field")
        row: dict[str, float | int] = {
            "epoch": epoch + 1,
            "optimizer_steps": optimizer_steps,
            "training_loss": epoch_loss / len(order),
            "validation_field_relative_l2": validation_field,
            "learning_rate": float(scheduler.get_last_lr()[0]),
        }
        history.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
        state = {
            key: value.detach().cpu().clone() for key, value in model.state_dict().items()
        }
        if validation_field < best_field:
            best_field = validation_field
            best_epoch = epoch + 1
            best_state = state
            stale = 0
        else:
            stale += 1
        if (epoch + 1) % checkpoint_interval == 0:
            _strict_atomic_torch_save(
                checkpoint_directory / f"epoch_{epoch + 1:03d}.pt",
                make_training_checkpoint(
                    schema_version="aurora.private.aneug_release_730_transolver_checkpoint.v2",
                    protocol_id=config["protocol_id"],
                    epoch=epoch + 1,
                    optimizer_steps=optimizer_steps,
                    validation_field_relative_l2=validation_field,
                    model_state_dict=state,
                    optimizer_state_dict=optimizer.state_dict(),
                    scheduler_state_dict=scheduler.state_dict(),
                    best_state_dict=best_state,
                    best_field_relative_l2=best_field,
                    best_epoch=best_epoch,
                    stale_epochs=stale,
                    history=history,
                    smoke=smoke,
                    elapsed_seconds_accumulated=elapsed_seconds_prior
                    + time.monotonic()
                    - started,
                    provenance=provenance,
                ),
            )
        if epoch + 1 >= minimum_epochs and stale >= patience:
            break

    _require(best_state is not None and best_epoch > 0, "best_checkpoint")
    model.load_state_dict(best_state)
    final_validation = evaluate(model, validation, device, wss_scale)
    _strict_atomic_torch_save(
        checkpoint_directory / "best.pt",
        {
            "schema_version": "aurora.private.aneug_release_730_transolver_best.v1",
            "protocol_id": config["protocol_id"],
            "seed": seed,
            "best_epoch": best_epoch,
            "validation_field_relative_l2": float(
                final_validation["aggregate"]["field_relative_l2"]
            ),
            "model_state_dict": best_state,
            **provenance,
        },
    )
    result = {
        "schema_version": "aurora.private.aneug_release_730_transolver_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "comparison_identity": config["comparison_identity"]["label"],
        "exact_upstream_reproduction": False,
        "proposed_method": False,
        "seed": seed,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "optimizer_steps": optimizer_steps,
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": elapsed_seconds_prior + time.monotonic() - started,
        "continuation_mode": resume_checkpoint is not None,
        "resumed_from_epoch": resumed_from_epoch,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "train_physical_vector_rms_scale": wss_scale,
        "smoke": smoke,
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
        **provenance,
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--response-oracle-terminal-record", type=Path)
    parser.add_argument("--ghd-gps-terminal-record", type=Path)
    parser.add_argument("--expected-commit")
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
        args.response_oracle_terminal_record,
        args.ghd_gps_terminal_record,
        args.expected_commit,
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
    activation = validate_activation(args.activation, config, args.expected_commit)
    continuation_mode = args.resume_checkpoint is not None
    _require(
        activation["continuation_mode"] is continuation_mode,
        "continuation_mode_mismatch",
    )
    if continuation_mode:
        _require(
            args.prior_attempt_terminal_record is not None,
            "prior_attempt_terminal_required",
        )
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
        _require(
            args.prior_attempt_terminal_record is None,
            "unexpected_prior_attempt_terminal",
        )
    validate_predecessor_terminal_record(
        args.response_oracle_terminal_record,
        activation,
        "response_oracle_terminal_record_sha256",
    )
    validate_predecessor_terminal_record(
        args.ghd_gps_terminal_record,
        activation,
        "ghd_gps_terminal_record_sha256",
    )
    scientific_provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "processed_v5_sha256": config["source"]["processed_v5_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        "validation_case_digest": config["split"]["validation_case_digest"],
        "validation_loader_order_sha256": config["split"]
        ["validation_loader_order_sha256"],
        "direct_baseline_terminal_record_sha256": activation[
            "direct_baseline_terminal_record_sha256"
        ],
        "ghd_gps_terminal_record_sha256": activation[
            "ghd_gps_terminal_record_sha256"
        ],
        "response_oracle_terminal_record_sha256": activation[
            "response_oracle_terminal_record_sha256"
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
    run_development(
        config,
        {
            "transient": args.transient,
            "steady": args.steady,
            "public_split": args.public_split,
            "private_split": args.private_split,
            "train_audit_public": args.train_audit_public,
            "train_audit_private": args.train_audit_private,
        },
        args.result,
        args.checkpoint_directory,
        provenance,
        args.resume_checkpoint,
        scientific_provenance,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
