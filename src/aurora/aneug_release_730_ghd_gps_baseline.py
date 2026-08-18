"""Release-730 GHD-conditioned GINE-GPS U-Net strong comparator."""

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
from torch.nn import functional as F

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d11_strong_baseline import (
    CoarseGPSBlock,
    GINEStyleBlock,
)
from aurora.aneug_processed_v4_d9 import (
    _extract_topology,
    field_loss,
    model_parameter_count,
)
from aurora.aneug_release_730_official_graphunet_baseline import (
    extended_case_metrics,
)
from aurora.aneug_release_730_train_audit import (
    _ordered_digest,
    _vertex_areas,
    index_case_records,
    selected_training_records,
    validate_split_evidence,
)


class Release730GHDGPSError(RuntimeError):
    """Raised when a strong-comparator evidence or execution boundary fails."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730GHDGPSError(reason)


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
        torch.save(dict(payload), temporary)
        with temporary.open("rb") as handle:
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
        == "aurora.aneug_release_730_ghd_gps_baseline.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id") == "aneug_release_730_ghd_gps_baseline_v1",
        "protocol_id",
    )
    _require(
        config.get("status")
        == "prepared_non_executable_until_direct_baseline_terminal",
        "status",
    )
    source = config["source"]
    _require(
        source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36"
        and source["official_code_revision"]
        == "4a090a0f12538deef6fcea88b81afe78ce38152e"
        and source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae"
        and source["steady_norm_bytes"] == 9_632_510_050
        and source["steady_norm_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "source",
    )
    identity = config["comparison_identity"]
    _require(
        identity["label"]
        == "release730_ghd_conditioned_gine_gps_unet_matched_reimplementation"
        and identity["exact_rhsia_reproduction"] is False
        and identity["proposed_method"] is False,
        "identity",
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
    _require(split["read_train_fields"] and split["read_validation_fields"], "development_read")
    _require(
        not split["read_locked_test_fields"]
        and not split["read_processed_only_extra_fields"]
        and not split["test_opened"],
        "sealed_read",
    )
    target = config["target_and_metric"]
    _require(
        target["common_report_space"] == "raw_released_physical_cartesian_wss",
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
            architecture["fine_encoder_blocks"],
            architecture["middle_encoder_blocks"],
            architecture["coarse_gps_blocks"],
            architecture["middle_decoder_blocks"],
            architecture["fine_decoder_blocks"],
            architecture["output_phases"],
        )
        == (128, 4, 2, 2, 3, 1, 1, 80),
        "architecture",
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
        and optimization["scheduler"] == "step_50_gamma_0p75",
        "optimizer",
    )
    _require(config["decision_rule"]["absolute_performance_threshold"] is None, "threshold")
    _require(config["decision_rule"]["automatic_winner"] is False, "winner")
    runtime = config["runtime"]
    _require(
        runtime["server"] == "introai9"
        and runtime["ngpus"] == 1
        and runtime["memory_gb"] == 64
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0a61ae05b88681f2",
        "runtime",
    )
    authorization = config["authorization"]
    _require(not authorization["execute_now"], "execute_now")
    _require(authorization["requires_direct_baseline_terminal_record"], "predecessor")
    _require(authorization["requires_fresh_private_activation"], "activation")
    for key in (
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
        == "aurora.private.aneug_release_730_ghd_gps_activation.v1",
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
    _require(bool(activation.get("direct_baseline_terminal_record_sha256")), "baseline_terminal")
    _require(activation.get("read_locked_test_or_extra") is False, "activation_scope")
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["split"]["train_audit_private_sha256"],
        "activation_evidence",
    )
    return activation


class Release730GHDGPSUNet(nn.Module):
    """Pure-Torch GHD-conditioned full-cycle mesh U-Net comparator."""

    def __init__(
        self,
        topology: Mapping[str, torch.Tensor],
        *,
        width: int = 128,
        heads: int = 4,
    ) -> None:
        super().__init__()
        _require(width % heads == 0, "attention_width")
        for name in (
            "edge0",
            "edge1",
            "edge2",
            "idx1",
            "idx2",
            "parent1",
            "parent2",
        ):
            self.register_buffer(name, topology[name].to(dtype=torch.int64))
        self.node_input = nn.Sequential(
            nn.Linear(7, width),
            nn.SiLU(),
            nn.Linear(width, width),
        )
        self.ghd_encoder = nn.Sequential(
            nn.LayerNorm(432),
            nn.Linear(432, 2 * width),
            nn.SiLU(),
            nn.Linear(2 * width, width),
        )
        self.film = nn.ModuleList([nn.Linear(width, 2 * width) for _ in range(5)])
        self.fine_encoder = nn.ModuleList([GINEStyleBlock(width) for _ in range(2)])
        self.middle_encoder = nn.ModuleList([GINEStyleBlock(width) for _ in range(2)])
        self.coarse = nn.ModuleList([CoarseGPSBlock(width, heads) for _ in range(3)])
        self.middle_decoder = nn.ModuleList([GINEStyleBlock(width)])
        self.fine_decoder = nn.ModuleList([GINEStyleBlock(width)])
        self.coarse_to_middle = nn.Linear(width, width)
        self.middle_to_fine = nn.Linear(width, width)
        self.middle_skip_norm = nn.LayerNorm(width)
        self.fine_skip_norm = nn.LayerNorm(width)
        self.output = nn.Sequential(
            nn.Linear(width, width),
            nn.SiLU(),
            nn.Linear(width, 80 * 3),
        )

    @staticmethod
    def _apply_blocks(
        blocks: nn.ModuleList,
        features: torch.Tensor,
        positions: torch.Tensor,
        normals: torch.Tensor,
        edges: torch.Tensor,
    ) -> torch.Tensor:
        for block in blocks:
            features = block(features, positions, normals, edges)
        return features

    def _condition(
        self, features: torch.Tensor, condition: torch.Tensor, level: int
    ) -> torch.Tensor:
        scale, shift = self.film[level](condition).chunk(2, dim=-1)
        return features * (1.0 + 0.25 * torch.tanh(scale)) + shift

    def forward(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        positions0 = case["coordinates"]
        normals0 = case["normals"]
        weights = case["vertex_weights"]
        relative_area = torch.log(
            torch.clamp(
                weights / torch.clamp(weights.mean(), min=1e-12), min=1e-8
            )
        ).unsqueeze(-1)
        condition = self.ghd_encoder(case["ghd"].reshape(1, -1)).squeeze(0)
        features0 = self.node_input(
            torch.cat((positions0, normals0, relative_area), dim=-1)
        )
        features0 = self._condition(features0, condition, 0)
        features0 = self._apply_blocks(
            self.fine_encoder, features0, positions0, normals0, self.edge0
        )
        fine_skip = features0

        positions1 = positions0[self.idx1]
        normals1 = normals0[self.idx1]
        features1 = self._condition(features0[self.idx1], condition, 1)
        features1 = self._apply_blocks(
            self.middle_encoder, features1, positions1, normals1, self.edge1
        )
        middle_skip = features1

        positions2 = positions1[self.idx2]
        normals2 = normals1[self.idx2]
        features2 = self._condition(features1[self.idx2], condition, 2)
        features2 = self._apply_blocks(
            self.coarse, features2, positions2, normals2, self.edge2
        )

        features1 = self.middle_skip_norm(
            middle_skip + self.coarse_to_middle(features2[self.parent2])
        )
        features1 = self._condition(features1, condition, 3)
        features1 = self._apply_blocks(
            self.middle_decoder, features1, positions1, normals1, self.edge1
        )

        features0 = self.fine_skip_norm(
            fine_skip + self.middle_to_fine(features1[self.parent1])
        )
        features0 = self._condition(features0, condition, 4)
        features0 = self._apply_blocks(
            self.fine_decoder, features0, positions0, normals0, self.edge0
        )
        output = self.output(features0).reshape(features0.shape[0], 80, 3)
        return output.permute(1, 0, 2).contiguous()


def _case_from_record(
    record: Mapping[str, Any],
    ghd: torch.Tensor,
    ghd_mean: torch.Tensor,
    ghd_std: torch.Tensor,
    decoder_mean: torch.Tensor,
    decoder_std: torch.Tensor,
    faces: torch.Tensor,
) -> dict[str, torch.Tensor]:
    expected_labels = [
        "x",
        "y",
        "z",
        "x_normal",
        "y_normal",
        "z_normal",
        "wss_x",
        "wss_y",
        "wss_z",
    ]
    _require([str(value) for value in record.get("labels", [])] == expected_labels, "labels")
    normalized = record["tensor"].detach().cpu().to(torch.float32)
    _require(tuple(normalized.shape) == (80, 13_902, 9), "case_shape")
    _require(bool(torch.isfinite(normalized).all().item()), "case_finite")
    physical = normalized * (decoder_std.reshape(1, 1, 9) + 1e-5)
    physical = physical + decoder_mean.reshape(1, 1, 9)
    coordinates = physical[0, :, :3].to(torch.float64)
    center = coordinates.mean(dim=0, keepdim=True)
    centered = coordinates - center
    coordinate_scale = torch.sqrt(torch.mean(torch.sum(centered.square(), dim=-1)))
    _require(
        bool(torch.isfinite(coordinate_scale).item())
        and float(coordinate_scale.item()) > 0.0,
        "coordinate_scale",
    )
    weights, normals, twice_area = _vertex_areas(coordinates, faces, torch)
    _require(bool((weights > 0).all().item()) and bool((twice_area > 0).all().item()), "mesh")
    return {
        "coordinates": (centered / coordinate_scale).to(torch.float32).contiguous(),
        "normals": normals.to(torch.float32).contiguous(),
        "vertex_weights": (weights / weights.sum()).to(torch.float32).contiguous(),
        "ghd": ((ghd.to(torch.float32) - ghd_mean) / ghd_std).contiguous(),
        "wss": physical[:, :, 6:9].to(torch.float32).contiguous(),
    }


def load_development_data(
    config: Mapping[str, Any],
    transient_path: Path,
    steady_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    train_audit_public_path: Path,
    train_audit_private_path: Path,
) -> tuple[
    list[dict[str, torch.Tensor]],
    list[dict[str, torch.Tensor]],
    dict[str, torch.Tensor],
    float,
]:
    source = config["source"]
    checks = (
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (steady_path, source["steady_norm_bytes"], source["steady_norm_sha256"], "steady"),
        (public_split_path, None, config["split"]["public_result_sha256"], "public_split"),
        (private_split_path, None, config["split"]["private_manifest_sha256"], "private_split"),
        (train_audit_public_path, None, config["split"]["train_audit_public_sha256"], "audit_public"),
        (train_audit_private_path, None, config["split"]["train_audit_private_sha256"], "audit_private"),
    )
    for path, size, digest, label in checks:
        _require(path.is_file() and (size is None or path.stat().st_size == size), f"{label}_identity")
        _require(file_sha256(path) == digest, f"{label}_sha256")
    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    audit_public = json.loads(train_audit_public_path.read_text(encoding="utf-8"))
    audit = json.loads(train_audit_private_path.read_text(encoding="utf-8"))
    _require(audit_public.get("integrity_pass") is True and audit_public.get("test_opened") is False, "audit_public")
    _require(audit.get("validation_test_or_extra_statistics_included") is False, "audit_scope")
    buckets = validate_split_evidence(config, public_split, private_split)
    train_order = [str(value) for value in audit.get("loader_order_case_ids", [])]
    _require(
        len(train_order) == 584
        and _ordered_digest(train_order) == config["split"]["train_loader_order_sha256"]
        and set(train_order) == set(buckets["train"]),
        "train_order",
    )
    steady = safe_torch_load(steady_path, torch)
    transient = safe_torch_load(transient_path, torch)
    labels = [str(value) for value in steady["label"]]
    _require(
        labels
        == [
            "x",
            "y",
            "z",
            "x_normal",
            "y_normal",
            "z_normal",
            "wss_x",
            "wss_y",
            "wss_z",
        ],
        "steady_labels",
    )
    decoder_mean = steady["tensor_norm"]["mean"].detach().cpu().to(torch.float32).reshape(-1)
    decoder_std = steady["tensor_norm"]["std"].detach().cpu().to(torch.float32).reshape(-1)
    _require(
        decoder_mean.numel() == decoder_std.numel() == 9
        and bool((decoder_std > 0).all().item()),
        "normalizer",
    )
    ordered, indexed = index_case_records(transient["registered_data_list"])
    mesh = transient["mesh_data"]
    mesh_cases = [str(value) for value in mesh["cases"]]
    _require(ordered == mesh_cases, "case_order")
    ghd = mesh["ghd"].detach().cpu().to(torch.float32)
    _require(tuple(ghd.shape) == (809, 432) and bool(torch.isfinite(ghd).all().item()), "ghd")
    ghd_by_id = {case_id: ghd[index] for index, case_id in enumerate(mesh_cases)}
    ghd_mean = torch.tensor(audit["ghd"]["mean"], dtype=torch.float32)
    ghd_std = torch.tensor(audit["ghd"]["std_population"], dtype=torch.float32).clamp(min=1e-6)
    _require(ghd_mean.shape == ghd_std.shape == (432,), "ghd_statistics")
    wss_mean = torch.tensor(audit["wss_physical"]["mean"], dtype=torch.float64)
    wss_std = torch.tensor(audit["wss_physical"]["std_population"], dtype=torch.float64)
    wss_scale = float(torch.sqrt(torch.sum(wss_mean.square() + wss_std.square())).item())
    _require(math.isfinite(wss_scale) and wss_scale > 0.0, "wss_scale")
    topology = _extract_topology(mesh)
    faces = topology.pop("faces")
    train_records = selected_training_records(
        indexed, train_order, buckets["validation"] + buckets["test"] + buckets["extra"]
    )
    validation_records = selected_training_records(
        indexed, buckets["validation"], train_order + buckets["test"] + buckets["extra"]
    )
    train: list[dict[str, torch.Tensor]] = []
    validation: list[dict[str, torch.Tensor]] = []
    for index, (case_id, record) in enumerate(zip(train_order, train_records), start=1):
        train.append(
            _case_from_record(
                record,
                ghd_by_id[case_id],
                ghd_mean,
                ghd_std,
                decoder_mean,
                decoder_std,
                faces,
            )
        )
        if index % 50 == 0 or index == 584:
            print(json.dumps({"stage": "load_train", "cases": index}), flush=True)
    for index, (case_id, record) in enumerate(
        zip(buckets["validation"], validation_records), start=1
    ):
        validation.append(
            _case_from_record(
                record,
                ghd_by_id[case_id],
                ghd_mean,
                ghd_std,
                decoder_mean,
                decoder_std,
                faces,
            )
        )
        if index == 73:
            print(json.dumps({"stage": "load_validation", "cases": index}), flush=True)
    return train, validation, topology, wss_scale


def _to_device(
    case: Mapping[str, torch.Tensor], device: torch.device
) -> dict[str, torch.Tensor]:
    return {
        key: value.to(device=device, non_blocking=True) for key, value in case.items()
    }


@torch.no_grad()
def evaluate(
    model: Release730GHDGPSUNet,
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
    provenance: Mapping[str, str],
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
    train, validation, topology, wss_scale = load_development_data(
        config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
    )
    model = Release730GHDGPSUNet(
        topology,
        width=int(architecture["width"]),
        heads=int(architecture["attention_heads"]),
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

    maximum_epochs = int(optimization["maximum_epochs"])
    minimum_epochs = int(optimization["minimum_epochs"])
    patience = int(optimization["early_stopping_patience"])
    accumulation = int(optimization["gradient_accumulation_cases"])
    checkpoint_interval = int(optimization["checkpoint_interval_epochs"])
    checkpoint_directory.mkdir(parents=True, exist_ok=True)
    _require(not any(checkpoint_directory.iterdir()), "checkpoint_directory_not_empty")
    best_field = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, float | int]] = []
    optimizer_steps = 0
    for epoch in range(maximum_epochs):
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
        _require(len(order) % accumulation == 0, "incomplete_effective_batch")
        scheduler.step()
        validation_result = evaluate(model, validation, device, wss_scale)
        validation_field = float(
            validation_result["aggregate"]["field_relative_l2"]
        )
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
                {
                    "schema_version": "aurora.private.aneug_release_730_ghd_gps_checkpoint.v1",
                    "protocol_id": config["protocol_id"],
                    "epoch": epoch + 1,
                    "optimizer_steps": optimizer_steps,
                    "validation_field_relative_l2": validation_field,
                    "model_state_dict": state,
                    "optimizer_state_dict": optimizer.state_dict(),
                    "scheduler_state_dict": scheduler.state_dict(),
                    **provenance,
                },
            )
        if epoch + 1 >= minimum_epochs and stale >= patience:
            break

    _require(best_state is not None and best_epoch > 0, "best_checkpoint")
    model.load_state_dict(best_state)
    final_validation = evaluate(model, validation, device, wss_scale)
    _strict_atomic_torch_save(
        checkpoint_directory / "best.pt",
        {
            "schema_version": "aurora.private.aneug_release_730_ghd_gps_best.v1",
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
        "schema_version": "aurora.private.aneug_release_730_ghd_gps_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "comparison_identity": "matched_reimplementation_not_rhsia_reproduction",
        "proposed_method": False,
        "seed": seed,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "optimizer_steps": optimizer_steps,
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": time.monotonic() - started,
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
    parser.add_argument("--expected-commit")
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--checkpoint-directory", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    required = (
        args.activation,
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
    provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "processed_v5_sha256": config["source"]["processed_v5_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        "direct_baseline_terminal_record_sha256": activation[
            "direct_baseline_terminal_record_sha256"
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
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
