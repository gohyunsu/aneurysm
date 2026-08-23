"""Release-730 adapter for the released AneuG Graph U-Net class."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d12_official_graphunet import (
    balanced_snapshot_pairs,
    build_released_model,
    file_sha256,
)
from aurora.aneug_processed_v4_d9 import case_metrics, model_parameter_count
from aurora.aneug_release_730_train_audit import (
    _ordered_digest,
    _vertex_areas,
    index_case_records,
    selected_training_records,
    validate_split_evidence,
)


class Release730GraphUNetError(RuntimeError):
    """Raised when source, split, objective or sealed-read boundaries fail."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730GraphUNetError(reason)


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_official_graphunet_baseline.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_official_graphunet_baseline_v1",
        "protocol_id",
    )
    _require(
        config.get("status") == "prepared_for_private_activation_after_quality",
        "status",
    )
    source = config["source"]
    _require(
        source["repository"] == "WenHaoDing/AneuG-Flow"
        and source["commit"] == "4a090a0f12538deef6fcea88b81afe78ce38152e",
        "source",
    )
    _require(
        source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae"
        and source["steady_norm_bytes"] == 9_632_510_050
        and source["steady_norm_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "data_source",
    )
    identity = config["comparison_identity"]
    _require(identity["exact_end_to_end_reproduction"] is False, "reproduction")
    _require(identity["unchanged_released_model_class_and_forward"] is True, "model")
    split = config["split"]
    _require(
        (
            split["train_cases"],
            split["validation_cases"],
            split["test_cases"],
            split["processed_only_extra_cases"],
        )
        == (584, 73, 73, 79),
        "split_counts",
    )
    _require(
        split["public_result_sha256"]
        == "4fa3be7c217c3a84b86f477c90112377fb913f6b0b47b829d684b270555bf991"
        and split["private_manifest_sha256"]
        == "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f"
        and split["train_audit_public_sha256"]
        == "3c525820023a56862c6652441c5d00f43412d3c868840149e5f120b8ed2a9587"
        and split["train_audit_private_sha256"]
        == "ce1dd6d2852e290fbe187ac062af155f522cd4b8a82c1580b5430d15ed519385"
        and split["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "split_evidence",
    )
    _require(split["read_train_fields"] and split["read_validation_fields"], "development_read")
    _require(
        not split["read_test_fields"]
        and not split["read_processed_only_extra_fields"]
        and not split["test_opened"],
        "sealed_read",
    )
    target = config["target_and_metric"]
    _require(
        target["common_report_space"] == "raw_released_physical_cartesian_wss",
        "target",
    )
    _require(not target["hard_tangent_projection"] and not target["hard_periodic_closure"], "hard_constraint")
    architecture = config["architecture"]
    _require(
        (
            architecture["in_channels"],
            architecture["hidden_channels"],
            architecture["out_channels"],
            architecture["depth"],
            architecture["pool_ratios"],
        )
        == (6, 512, 3, 3, [0.25, 0.25, 0.25]),
        "architecture",
    )
    optimization = config["optimization"]
    _require(
        (
            optimization["seed"],
            optimization["physical_snapshot_batch_size"],
            optimization["effective_snapshot_batch_size"],
            optimization["gradient_accumulation_steps"],
            optimization["maximum_coverage_epochs"],
            optimization["minimum_coverage_epochs"],
            optimization["validation_interval_coverage_epochs"],
            optimization["early_stopping_validation_checks"],
        )
        == (1103, 8, 56, 7, 30, 15, 5, 3),
        "optimization",
    )
    _require(
        optimization["learning_rate"] == 3e-4
        and optimization["weight_decay"] == 0.01
        and optimization["physical_loss_decoder_epsilon"] == 1e-6
        and optimization["physical_metric_decoder_epsilon"] == 1e-5,
        "objective",
    )
    _require(config["decision_rule"]["absolute_performance_threshold"] is None, "threshold")
    _require(config["decision_rule"]["automatic_winner"] is False, "winner")
    _require(
        config["dependency"]["torch"] == "2.5.1+cu118"
        and config["dependency"]["torch_geometric"] == "2.6.1",
        "dependency",
    )
    runtime = config["runtime"]
    _require(
        runtime["server"] == "introai9"
        and runtime["ngpus"] == 1
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2"
        and config["authorization"]["excluded_server"] == "junjinyong",
        "runtime",
    )
    authorization = config["authorization"]
    _require(authorization["execute_validation_development_after_private_activation"] is True, "execute")
    for key in (
        "multi_seed_confirmation",
        "read_locked_test",
        "read_processed_only_extra",
        "paper_claim",
        "publish_numeric_result",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_official_graphunet_baseline_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(activation.get("authorized_stage") == "single_seed_validation_development", "activation_stage")
    _require(activation.get("read_test_or_extra") is False, "activation_scope")
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"],
        "activation_split",
    )
    _require(
        activation.get("private_train_audit_sha256")
        == config["split"]["train_audit_private_sha256"],
        "activation_audit",
    )
    _require(
        activation.get("official_commit") == config["source"]["commit"],
        "activation_official",
    )
    return activation


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "result_exists")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, target)


def _strict_atomic_checkpoint(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "checkpoint_exists")
    torch.save(dict(payload), temporary)
    os.replace(temporary, target)


def _topology_from_release(transient: Mapping[str, Any]) -> dict[str, torch.Tensor]:
    mesh = transient["mesh_data"]
    edges = mesh["edge_index_list"]
    indices = mesh["idx_list"]
    _require(len(edges) >= 3 and len(indices) >= 2, "hierarchy")
    result = {
        "edge0": edges[0].detach().cpu().to(torch.int64).contiguous(),
        "edge1": edges[1].detach().cpu().to(torch.int64).contiguous(),
        "edge2": edges[2].detach().cpu().to(torch.int64).contiguous(),
        "idx1": indices[0].detach().cpu().to(torch.int64).reshape(-1).contiguous(),
        "idx2": indices[1].detach().cpu().to(torch.int64).reshape(-1).contiguous(),
    }
    _require(int(result["idx1"].min()) >= 0 and int(result["idx1"].max()) < 13_902, "idx1")
    _require(int(result["idx2"].min()) >= 0 and int(result["idx2"].max()) < len(result["idx1"]), "idx2")
    return result


def _in_memory_case(
    record: Mapping[str, Any],
    labels: Sequence[str],
    mean: torch.Tensor,
    std: torch.Tensor,
    faces: torch.Tensor,
) -> dict[str, torch.Tensor]:
    _require([str(value) for value in record.get("labels", [])] == list(labels), "labels")
    normalized = record["tensor"].detach().cpu().to(torch.float32)
    _require(tuple(normalized.shape) == (80, 13_902, 9), "shape")
    _require(bool(torch.isfinite(normalized).all().item()), "finite")
    _require(float((normalized[..., :6] - normalized[:1, :, :6]).abs().max()) == 0.0, "static_geometry")
    physical_coordinates = normalized[0, :, :3].to(torch.float64) * (
        std[:3].to(torch.float64) + 1e-5
    ) + mean[:3].to(torch.float64)
    areas, mesh_normals, twice_area = _vertex_areas(physical_coordinates, faces, torch)
    _require(bool((twice_area > 0).all().item()) and bool((areas > 0).all().item()), "mesh")
    return {
        "input": normalized[0, :, :6].clone().contiguous(),
        "target_normalized": normalized[:, :, 6:9].clone().contiguous(),
        "vertex_weights": (areas / areas.sum()).to(torch.float32).contiguous(),
        "mesh_normals": mesh_normals.to(torch.float32).contiguous(),
    }


def load_development_data(
    config: Mapping[str, Any],
    transient_path: Path,
    steady_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    train_audit_public_path: Path,
    train_audit_private_path: Path,
) -> tuple[list[dict[str, torch.Tensor]], list[dict[str, torch.Tensor]], dict[str, torch.Tensor], torch.Tensor, torch.Tensor]:
    source = config["source"]
    for path, size, digest, label in (
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (steady_path, source["steady_norm_bytes"], source["steady_norm_sha256"], "steady"),
        (public_split_path, None, config["split"]["public_result_sha256"], "public_split"),
        (private_split_path, None, config["split"]["private_manifest_sha256"], "private_split"),
        (train_audit_public_path, None, config["split"]["train_audit_public_sha256"], "train_audit_public"),
        (train_audit_private_path, None, config["split"]["train_audit_private_sha256"], "train_audit"),
    ):
        _require(path.is_file() and (size is None or path.stat().st_size == size), f"{label}_identity")
        _require(file_sha256(path) == digest, f"{label}_sha256")
    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    audit_public = json.loads(train_audit_public_path.read_text(encoding="utf-8"))
    audit = json.loads(train_audit_private_path.read_text(encoding="utf-8"))
    _require(
        audit_public.get("integrity_pass") is True
        and audit_public.get("test_opened") is False,
        "train_audit_public",
    )
    _require(
        audit.get("validation_test_or_extra_statistics_included") is False,
        "train_audit_private_scope",
    )
    buckets = validate_split_evidence(config, public_split, private_split)
    train_order = [str(value) for value in audit.get("loader_order_case_ids", [])]
    _require(
        len(train_order) == 584
        and _ordered_digest(train_order) == config["split"]["train_loader_order_sha256"]
        and set(train_order) == set(buckets["train"]),
        "train_order",
    )
    _require(
        _ordered_digest(buckets["validation"])
        == config["split"]["validation_loader_order_sha256"],
        "validation_order",
    )
    steady = safe_torch_load(steady_path, torch)
    transient = safe_torch_load(transient_path, torch)
    labels = [str(value) for value in steady["label"]]
    _require(
        labels == ["x", "y", "z", "x_normal", "y_normal", "z_normal", "wss_x", "wss_y", "wss_z"],
        "steady_labels",
    )
    mean = steady["tensor_norm"]["mean"].detach().cpu().to(torch.float32).reshape(-1)
    std = steady["tensor_norm"]["std"].detach().cpu().to(torch.float32).reshape(-1)
    _require(mean.numel() == std.numel() == 9 and bool((std > 0).all().item()), "normalizer")
    ordered, indexed = index_case_records(transient["registered_data_list"])
    _require(ordered == [str(value) for value in transient["mesh_data"]["cases"]], "case_order")
    faces = transient["mesh_data"]["faces_list"][0].detach().cpu().to(torch.int64)
    train_records = selected_training_records(
        indexed, train_order, buckets["validation"] + buckets["test"] + buckets["extra"]
    )
    validation_records = selected_training_records(
        indexed, buckets["validation"], train_order + buckets["test"] + buckets["extra"]
    )
    train: list[dict[str, torch.Tensor]] = []
    validation: list[dict[str, torch.Tensor]] = []
    for index, record in enumerate(train_records, start=1):
        train.append(_in_memory_case(record, labels, mean, std, faces))
        if index % 50 == 0 or index == 584:
            print(json.dumps({"stage": "load_train", "cases": index}), flush=True)
    for index, record in enumerate(validation_records, start=1):
        validation.append(_in_memory_case(record, labels, mean, std, faces))
        if index == 73:
            print(json.dumps({"stage": "load_validation", "cases": index}), flush=True)
    return train, validation, _topology_from_release(transient), mean, std


def _snapshot_batch(
    cases: Sequence[Mapping[str, torch.Tensor]],
    pairs: Sequence[tuple[int, int]],
    device: torch.device,
) -> tuple[Any, torch.Tensor, torch.Tensor, torch.Tensor]:
    from torch_geometric.data import Data

    selected = [cases[case_index] for case_index, _ in pairs]
    node_count = int(selected[0]["input"].shape[0])
    inputs = torch.stack([case["input"] for case in selected]).to(device, non_blocking=True)
    targets = torch.stack(
        [case["target_normalized"][phase] for case, (_, phase) in zip(selected, pairs)]
    ).to(device, non_blocking=True)
    weights = torch.stack([case["vertex_weights"] for case in selected]).to(device, non_blocking=True)
    batch = torch.arange(len(pairs), device=device).repeat_interleave(node_count)
    data = Data(
        x=inputs.reshape(-1, 6),
        pos=inputs[..., :3].reshape(-1, 3),
        batch=batch,
    )
    phases = torch.tensor([phase for _, phase in pairs], dtype=torch.int64, device=device).view(-1, 1)
    return data, phases, targets, weights


def objective_components(
    prediction_normalized: torch.Tensor,
    reference_normalized: torch.Tensor,
    mean_wss: torch.Tensor,
    std_wss: torch.Tensor,
    *,
    physical_epsilon: float,
    log_epsilon: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    _require(prediction_normalized.shape == reference_normalized.shape, "objective_shape")
    squared = torch.sum((prediction_normalized - reference_normalized).square())
    prediction = prediction_normalized * (std_wss + physical_epsilon) + mean_wss
    reference = reference_normalized * (std_wss + physical_epsilon) + mean_wss
    prediction_log = torch.log(torch.clamp(torch.linalg.vector_norm(prediction, dim=-1), min=log_epsilon))
    reference_log = torch.log(torch.clamp(torch.linalg.vector_norm(reference, dim=-1), min=log_epsilon))
    log_squared = torch.sum((prediction_log - reference_log).square())
    return squared, log_squared


def extended_case_metrics(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    weights: torch.Tensor,
    mesh_normals: torch.Tensor,
) -> dict[str, float]:
    """Common physical-field and complete-cycle functional endpoints."""

    _require(
        prediction.shape == reference.shape
        and prediction.ndim == 3
        and prediction.shape[-1] == 3
        and weights.shape == prediction.shape[1:2]
        and mesh_normals.shape == prediction.shape[1:],
        "metric_shape",
    )
    result = case_metrics(prediction, reference, weights)
    tiny = torch.finfo(reference.dtype).tiny
    reference_mean = reference.mean(dim=0)
    prediction_mean = prediction.mean(dim=0)
    result["mean_wss_vector_error"] = float(
        torch.sqrt(
            torch.sum(weights * torch.sum((prediction_mean - reference_mean).square(), dim=-1))
            / torch.clamp(
                torch.sum(weights * torch.sum(reference_mean.square(), dim=-1)), min=tiny
            )
        )
    )
    reference_tawss = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0)
    low_support = reference_tawss <= torch.quantile(reference_tawss, 0.25)
    low_weights = weights[low_support]
    low_numerator = torch.sum(
        low_weights.reshape(1, -1)
        * torch.sum((prediction[:, low_support] - reference[:, low_support]).square(), dim=-1)
    )
    low_denominator = torch.sum(
        low_weights.reshape(1, -1)
        * torch.sum(reference[:, low_support].square(), dim=-1)
    )
    result["low_tawss_quartile_field_relative_l2"] = float(
        torch.sqrt(low_numerator / torch.clamp(low_denominator, min=tiny))
    )
    phase_burden = torch.sum(
        weights.reshape(1, -1) * torch.linalg.vector_norm(reference, dim=-1), dim=1
    )
    peak_phase = int(torch.argmax(phase_burden))
    peak_numerator = torch.sum(
        weights * torch.sum((prediction[peak_phase] - reference[peak_phase]).square(), dim=-1)
    )
    peak_denominator = torch.sum(
        weights * torch.sum(reference[peak_phase].square(), dim=-1)
    )
    result["peak_systolic_wss_relative_l2"] = float(
        torch.sqrt(peak_numerator / torch.clamp(peak_denominator, min=tiny))
    )
    prediction_normal = torch.sum(prediction * mesh_normals.reshape(1, -1, 3), dim=-1)
    reference_normal = torch.sum(reference * mesh_normals.reshape(1, -1, 3), dim=-1)
    normal_numerator = torch.sum(
        weights.reshape(1, -1) * (prediction_normal - reference_normal).square()
    )
    normal_denominator = torch.sum(
        weights.reshape(1, -1) * reference_normal.square()
    )
    result["mesh_normal_component_relative_l2"] = float(
        torch.sqrt(normal_numerator / torch.clamp(normal_denominator, min=tiny))
    )
    _require(all(math.isfinite(value) for value in result.values()), "metric_finite")
    return result


def _predict_normalized(
    model: torch.nn.Module,
    cases: Sequence[Mapping[str, torch.Tensor]],
    pairs: Sequence[tuple[int, int]],
    device: torch.device,
    waveform: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    data, phases, target, weights = _snapshot_batch(cases, pairs, device)
    prediction = model(data, phases, waveform).reshape(len(pairs), target.shape[1], 3)
    return prediction, target, weights


@torch.no_grad()
def evaluate_full_cycles(
    model: torch.nn.Module,
    cases: Sequence[Mapping[str, torch.Tensor]],
    device: torch.device,
    waveform: torch.Tensor,
    mean_wss: torch.Tensor,
    std_wss: torch.Tensor,
    metric_epsilon: float,
    batch_size: int,
) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    mean_cpu = mean_wss.detach().cpu()
    std_cpu = std_wss.detach().cpu()
    for case_index, case in enumerate(cases):
        chunks: list[torch.Tensor] = []
        pairs = [(case_index, phase) for phase in range(80)]
        for start in range(0, 80, batch_size):
            prediction, _, _ = _predict_normalized(
                model, cases, pairs[start : start + batch_size], device, waveform
            )
            chunks.append(prediction.cpu())
        prediction_normalized = torch.cat(chunks, dim=0)
        reference_normalized = case["target_normalized"]
        prediction_physical = prediction_normalized * (std_cpu + metric_epsilon) + mean_cpu
        reference_physical = reference_normalized * (std_cpu + metric_epsilon) + mean_cpu
        per_case.append(
            extended_case_metrics(
                prediction_physical,
                reference_physical,
                case["vertex_weights"],
                case["mesh_normals"],
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
    transient_path: Path,
    steady_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    train_audit_public_path: Path,
    train_audit_private_path: Path,
    official_root: Path,
    result_path: Path,
    checkpoint_directory: Path,
) -> dict[str, Any]:
    import torch_geometric

    _require(torch.__version__ == config["dependency"]["torch"], "torch_version")
    _require(torch_geometric.__version__ == config["dependency"]["torch_geometric"], "pyg_version")
    _require(not checkpoint_directory.exists(), "checkpoint_directory_exists")
    checkpoint_directory.mkdir(parents=True)
    train, validation, topology, mean, std = load_development_data(
        config,
        transient_path,
        steady_path,
        public_split_path,
        private_split_path,
        train_audit_public_path,
        train_audit_private_path,
    )
    optimization = config["optimization"]
    seed = int(optimization["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(4)
    device = torch.device("cuda")
    topology_gpu = {key: value.to(device) for key, value in topology.items()}
    model = build_released_model(official_root, config, topology_gpu).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(optimization["learning_rate"]),
        weight_decay=float(optimization["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=int(optimization["step_size_coverage_epochs"]),
        gamma=float(optimization["gamma"]),
    )
    waveform = torch.zeros((1, 80, 1), dtype=torch.float32, device=device)
    mean_wss = mean[6:9].to(device).reshape(1, 1, 3)
    std_wss = std[6:9].to(device).reshape(1, 1, 3)
    physical_batch = int(optimization["physical_snapshot_batch_size"])
    effective_batch = int(optimization["effective_snapshot_batch_size"])
    accumulation = int(optimization["gradient_accumulation_steps"])
    _require(effective_batch == physical_batch * accumulation, "effective_batch")
    maximum_epochs = int(optimization["maximum_coverage_epochs"])
    minimum_epochs = int(optimization["minimum_coverage_epochs"])
    validation_interval = int(optimization["validation_interval_coverage_epochs"])
    patience = int(optimization["early_stopping_validation_checks"])
    best_field = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    steps = 0
    history: list[dict[str, float | int]] = []
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()

    for coverage_epoch in range(maximum_epochs):
        pairs = balanced_snapshot_pairs(len(train), 80, seed, coverage_epoch)
        model.train()
        epoch_loss = 0.0
        epoch_batches = 0
        for start in range(0, len(pairs), effective_batch):
            effective_pairs = pairs[start : start + effective_batch]
            optimizer.zero_grad(set_to_none=True)
            mse_denominator = len(effective_pairs) * 13_902 * 3
            log_denominator = len(effective_pairs) * 13_902
            effective_loss = 0.0
            for micro_start in range(0, len(effective_pairs), physical_batch):
                micro_pairs = effective_pairs[micro_start : micro_start + physical_batch]
                prediction, reference, _ = _predict_normalized(
                    model, train, micro_pairs, device, waveform
                )
                mse_sum, log_sum = objective_components(
                    prediction,
                    reference,
                    mean_wss,
                    std_wss,
                    physical_epsilon=float(optimization["physical_loss_decoder_epsilon"]),
                    log_epsilon=float(optimization["log_magnitude_epsilon"]),
                )
                loss = (
                    float(optimization["normalized_frame_mse_weight"])
                    * mse_sum
                    / mse_denominator
                    + float(optimization["physical_log_magnitude_weight"])
                    * log_sum
                    / log_denominator
                )
                _require(bool(torch.isfinite(loss).item()), "training_loss")
                loss.backward()
                effective_loss += float(loss.detach())
            torch.nn.utils.clip_grad_norm_(
                model.parameters(), float(optimization["gradient_clip_norm"])
            )
            optimizer.step()
            epoch_loss += effective_loss
            epoch_batches += 1
            steps += 1
        scheduler.step()
        progress: dict[str, float | int] = {
            "coverage_epoch": coverage_epoch + 1,
            "optimizer_steps": steps,
            "training_loss": epoch_loss / epoch_batches,
        }
        if (coverage_epoch + 1) % validation_interval != 0:
            print(json.dumps(progress, sort_keys=True), flush=True)
            continue
        validation_result = evaluate_full_cycles(
            model,
            validation,
            device,
            waveform,
            mean_wss,
            std_wss,
            float(optimization["physical_metric_decoder_epsilon"]),
            physical_batch,
        )
        validation_field = float(validation_result["aggregate"]["field_relative_l2"])
        progress["validation_field_relative_l2"] = validation_field
        progress["learning_rate"] = float(scheduler.get_last_lr()[0])
        history.append(progress)
        print(json.dumps(progress, sort_keys=True), flush=True)
        state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        _strict_atomic_checkpoint(
            checkpoint_directory / f"coverage_{coverage_epoch + 1:03d}.pt",
            {
                "schema_version": "aurora.aneug_release_730_graphunet.private_checkpoint.v1",
                "protocol_id": config["protocol_id"],
                "seed": seed,
                "coverage_epoch": coverage_epoch + 1,
                "optimizer_steps": steps,
                "validation_field_relative_l2": validation_field,
                "model_state_dict": state,
                "optimizer_state_dict": optimizer.state_dict(),
                "scheduler_state_dict": scheduler.state_dict(),
            },
        )
        if validation_field < best_field:
            best_field = validation_field
            best_epoch = coverage_epoch + 1
            best_state = state
            stale = 0
        else:
            stale += 1
        if coverage_epoch + 1 >= minimum_epochs and stale >= patience:
            break

    _require(best_state is not None and best_epoch > 0, "best_checkpoint")
    model.load_state_dict(best_state)
    final_validation = evaluate_full_cycles(
        model,
        validation,
        device,
        waveform,
        mean_wss,
        std_wss,
        float(optimization["physical_metric_decoder_epsilon"]),
        physical_batch,
    )
    _strict_atomic_checkpoint(
        checkpoint_directory / "best.pt",
        {
            "schema_version": "aurora.aneug_release_730_graphunet.private_best.v1",
            "protocol_id": config["protocol_id"],
            "seed": seed,
            "coverage_epoch": best_epoch,
            "model_state_dict": best_state,
            "optimizer_selection_metric": config["target_and_metric"]["primary_metric"],
        },
    )
    result = {
        "schema_version": "aurora.aneug_release_730_graphunet.private_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_validation_development",
        "comparison_identity": config["comparison_identity"]["label"],
        "exact_end_to_end_reproduction": False,
        "absolute_pass_fail_gate": None,
        "best_coverage_epoch": best_epoch,
        "coverage_epochs_completed": coverage_epoch + 1,
        "optimizer_steps": steps,
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "validation": final_validation,
        "validation_check_history": history,
        "train_case_count": len(train),
        "validation_case_count": len(validation),
        "validation_case_digest": config["split"]["validation_case_digest"],
        "validation_loader_order_sha256": config["split"]
        ["validation_loader_order_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
        "single_seed_validation_development_only": True,
        "paper_result_or_claim": False,
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "config",
        "activation",
        "transient",
        "steady",
        "public_split",
        "private_split",
        "train_audit_public",
        "train_audit_private",
        "official_root",
        "result",
        "checkpoint_directory",
    ):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    validate_activation(args.activation, config, args.expected_commit)
    _require(torch.cuda.is_available(), "cuda_required")
    run_development(
        config,
        args.transient,
        args.steady,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.official_root,
        args.result,
        args.checkpoint_directory,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
