"""D11 official-style strong-baseline adaptation on the frozen D5 split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from torch import nn
from torch.nn import functional as F

from aurora.aneug_processed_v4_d9 import (
    case_metrics,
    field_loss,
    load_cached_split,
    model_parameter_count,
    tangent_projection,
)


class D11StrongBaselineError(RuntimeError):
    """Raised when a D11 evidence or execution boundary is violated."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise D11StrongBaselineError(label)


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
        temporary.replace(target)
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
        temporary.replace(target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_processed_v4_d11_strong_baseline.v1",
        "config_schema",
    )
    _require(config.get("status") == "executable_validation_development", "config_status")
    boundary = config["data_boundary"]
    _require(
        (
            boundary["train_cases"],
            boundary["validation_cases"],
            boundary["outer_cases"],
            boundary["auxiliary_cases"],
        )
        == (406, 51, 51, 70),
        "split",
    )
    _require(boundary["read_outer_or_auxiliary"] is False, "sealed_data")
    identity = config["adaptation_identity"]
    _require(identity["claim"] == "matched_reimplementation_not_reproduction", "identity")
    _require(identity["uses_torch_geometric"] is False, "dependency_boundary")
    _require(identity["uses_pytorch3d"] is False, "dependency_boundary")
    _require(identity["uses_steady_augmentation"] is False, "information_boundary")
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
        )
        == (128, 4, 2, 2, 3, 1, 1),
        "architecture",
    )
    _require(architecture["output_phases"] == 80, "phases")
    optimization = config["optimization"]
    _require(
        (
            optimization["seed"],
            optimization["maximum_epochs"],
            optimization["minimum_epochs"],
            optimization["early_stopping_patience"],
        )
        == (1103, 251, 80, 40),
        "optimization",
    )
    _require(
        optimization["learning_rate"] == 3e-4
        and optimization["weight_decay"] == 1e-4,
        "optimizer",
    )
    _require(
        optimization["scheduler"] == "step_50_gamma_0p75"
        and optimization["checkpoint_selection"]
        == "lowest_validation_field_relative_L2_then_earliest_epoch",
        "selection",
    )
    gate = config["development_gate"]
    _require(gate["field_relative_l2_ceiling"] == 0.35, "threshold")
    authorization = config["authorization"]
    _require(authorization["execute_one_training_job"] is True, "execute")
    for key in (
        "functional_readout_training",
        "multi_seed_confirmation",
        "outer_test",
        "paper_result_or_claim",
        "publish_numeric_result",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")
    _require(authorization["server"] == "introai9", "server")
    _require(authorization["excluded_server"] == "junjinyong", "excluded_server")


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.aneug_processed_v4_d11.private_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "D11_strong_baseline_validation",
        "activation_stage",
    )
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    for key in (
        "cache_manifest_sha256",
        "d10_result_sha256",
        "d10_checkpoint_sha256",
    ):
        _require(activation.get(key) == config["bound_evidence"][key], f"activation_{key}")
    return activation


def baseline_feasible(field_relative_l2: float, threshold: float = 0.35) -> bool:
    _require(
        math.isfinite(field_relative_l2) and field_relative_l2 >= 0.0,
        "field_metric",
    )
    return field_relative_l2 <= threshold


class GINEStyleBlock(nn.Module):
    """Dependency-free local edge-conditioned residual message passing."""

    def __init__(self, width: int) -> None:
        super().__init__()
        self.edge_encoder = nn.Sequential(
            nn.Linear(5, width),
            nn.SiLU(),
            nn.Linear(width, width),
        )
        self.update = nn.Sequential(
            nn.Linear(width, 2 * width),
            nn.SiLU(),
            nn.Linear(2 * width, width),
        )
        self.feed_forward = nn.Sequential(
            nn.Linear(width, 2 * width),
            nn.SiLU(),
            nn.Linear(2 * width, width),
        )
        self.local_norm = nn.LayerNorm(width)
        self.ff_norm = nn.LayerNorm(width)
        self.epsilon = nn.Parameter(torch.zeros(()))

    def forward(
        self,
        features: torch.Tensor,
        positions: torch.Tensor,
        normals: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        source, target = edge_index
        displacement = positions[source] - positions[target]
        distance = torch.linalg.vector_norm(displacement, dim=-1, keepdim=True)
        normal_alignment = torch.sum(normals[source] * normals[target], dim=-1, keepdim=True)
        edge_features = torch.cat((displacement, distance, normal_alignment), dim=-1)
        message = F.silu(features[source] + self.edge_encoder(edge_features))
        aggregate = torch.zeros_like(features).index_add_(0, target, message)
        degree = torch.bincount(target, minlength=features.shape[0]).to(features.dtype)
        aggregate = aggregate / degree.clamp(min=1).unsqueeze(-1)
        local = self.update((1.0 + self.epsilon) * features + aggregate)
        features = self.local_norm(features + local)
        return self.ff_norm(features + self.feed_forward(features))


class CoarseGPSBlock(nn.Module):
    """Local GINE-style update plus exact global attention on the coarse mesh."""

    def __init__(self, width: int, heads: int) -> None:
        super().__init__()
        self.local = GINEStyleBlock(width)
        self.attention_input_norm = nn.LayerNorm(width)
        self.attention = nn.MultiheadAttention(
            width,
            heads,
            dropout=0.0,
            batch_first=True,
        )
        self.attention_output_norm = nn.LayerNorm(width)
        self.feed_forward = nn.Sequential(
            nn.Linear(width, 2 * width),
            nn.SiLU(),
            nn.Linear(2 * width, width),
        )
        self.ff_norm = nn.LayerNorm(width)

    def forward(
        self,
        features: torch.Tensor,
        positions: torch.Tensor,
        normals: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        features = self.local(features, positions, normals, edge_index)
        normalized = self.attention_input_norm(features).unsqueeze(0)
        attended, _ = self.attention(
            normalized,
            normalized,
            normalized,
            need_weights=False,
        )
        features = self.attention_output_norm(features + attended.squeeze(0))
        return self.ff_norm(features + self.feed_forward(features))


class GHDConditionedGPSUNet(nn.Module):
    """Pure-Torch matched adaptation of the released GINE/GraphGPS hierarchy."""

    variant = "direct_cycle"

    def __init__(
        self,
        topology: Mapping[str, torch.Tensor],
        *,
        width: int = 128,
        heads: int = 4,
    ) -> None:
        super().__init__()
        _require(width % heads == 0, "attention_width")
        for name in ("edge0", "edge1", "edge2", "idx1", "idx2", "parent1", "parent2"):
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

    def forward(
        self, case: Mapping[str, torch.Tensor], *, exact_moment_projection: bool = False
    ) -> dict[str, torch.Tensor]:
        _require(exact_moment_projection is False, "projection_not_supported")
        positions0 = case["coordinates"]
        normals0 = case["normals"]
        weights = case["vertex_weights"]
        relative_area = torch.log(
            torch.clamp(weights / torch.clamp(weights.mean(), min=1e-12), min=1e-8)
        ).unsqueeze(-1)
        condition = self.ghd_encoder(case["ghd"].reshape(1, -1)).squeeze(0)
        features0 = self.node_input(torch.cat((positions0, normals0, relative_area), dim=-1))
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
        raw = self.output(features0).reshape(features0.shape[0], 80, 3)
        raw = raw.permute(1, 0, 2).contiguous()
        field = tangent_projection(raw, normals0)
        return {"field": field, "raw_field": field}


@torch.no_grad()
def evaluate(
    model: GHDConditionedGPSUNet,
    cases: Sequence[Mapping[str, torch.Tensor]],
    device: torch.device,
) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    for cpu_case in cases:
        case = {
            key: value.to(device=device, non_blocking=True)
            for key, value in cpu_case.items()
        }
        prediction = model(case)["field"]
        per_case.append(case_metrics(prediction, case["wss"], case["vertex_weights"]))
    keys = tuple(per_case[0])
    return {
        "aggregate": {
            key: sum(item[key] for item in per_case) / len(per_case) for key in keys
        },
        "per_case_without_identifiers": per_case,
        "case_count": len(per_case),
    }


def run_development(
    config: Mapping[str, Any],
    cache_path: str | Path,
    result_path: str | Path,
    checkpoint_path: str | Path,
) -> dict[str, Any]:
    cache = Path(cache_path)
    _require(
        file_sha256(cache / "cache_manifest.json")
        == config["bound_evidence"]["cache_manifest_sha256"],
        "cache_identity",
    )
    manifest = json.loads((cache / "cache_manifest.json").read_text(encoding="utf-8"))
    _require(
        manifest.get("r0_pass") is True
        and manifest.get("train_cases") == 406
        and manifest.get("validation_cases") == 51,
        "cache_boundary",
    )
    _require(
        manifest.get("outer_cases_read") == 0
        and manifest.get("auxiliary_cases_read") == 0,
        "sealed_cache",
    )

    optimization = config["optimization"]
    architecture = config["architecture"]
    seed = int(optimization["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device("cuda")
    topology = torch.load(cache / "topology.pt", map_location=device, weights_only=True)
    train_cases = load_cached_split(cache, "train")
    validation_cases = load_cached_split(cache, "validation")
    model = GHDConditionedGPSUNet(
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
    maximum_epochs = int(optimization["maximum_epochs"])
    minimum_epochs = int(optimization["minimum_epochs"])
    patience = int(optimization["early_stopping_patience"])
    accumulation = int(optimization["gradient_accumulation_cases"])
    best_field = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, float | int]] = []
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()

    smoke_case = {
        key: value.to(device=device, non_blocking=True)
        for key, value in train_cases[0].items()
    }
    smoke_started = time.monotonic()
    smoke_output = model(smoke_case)["field"]
    smoke_loss = field_loss(
        smoke_output,
        smoke_case["wss"],
        smoke_case["vertex_weights"],
    )
    smoke_loss.backward()
    _require(bool(torch.isfinite(smoke_loss).item()), "nonfinite_smoke")
    optimizer.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    smoke = {
        "finite_forward_backward": True,
        "seconds": time.monotonic() - smoke_started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
    }
    del smoke_case, smoke_output, smoke_loss

    for epoch in range(maximum_epochs):
        model.train()
        order = list(range(len(train_cases)))
        random.Random(seed + epoch).shuffle(order)
        optimizer.zero_grad(set_to_none=True)
        epoch_loss = 0.0
        for step, index in enumerate(order):
            case = {
                key: value.to(device=device, non_blocking=True)
                for key, value in train_cases[index].items()
            }
            output = model(case)["field"]
            loss = field_loss(output, case["wss"], case["vertex_weights"])
            _require(bool(torch.isfinite(loss).item()), "nonfinite_training_loss")
            (loss / accumulation).backward()
            epoch_loss += float(loss.detach().item())
            if (step + 1) % accumulation == 0 or step + 1 == len(order):
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), float(optimization["gradient_clip_norm"])
                )
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
        scheduler.step()
        validation = evaluate(model, validation_cases, device)
        validation_field = float(validation["aggregate"]["field_relative_l2"])
        row = {
            "epoch": epoch + 1,
            "training_loss": epoch_loss / len(order),
            "validation_field_relative_l2": validation_field,
            "learning_rate": float(scheduler.get_last_lr()[0]),
        }
        history.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
        if validation_field < best_field:
            best_field = validation_field
            best_epoch = epoch + 1
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
            stale = 0
        else:
            stale += 1
        if epoch + 1 >= minimum_epochs and stale >= patience:
            break

    _require(best_state is not None and best_epoch > 0, "missing_best_checkpoint")
    model.load_state_dict(best_state)
    final_validation = evaluate(model, validation_cases, device)
    final_field = float(final_validation["aggregate"]["field_relative_l2"])
    passed = baseline_feasible(
        final_field,
        float(config["development_gate"]["field_relative_l2_ceiling"]),
    )
    checkpoint = {
        "schema_version": "aurora.aneug_processed_v4_d11.private_checkpoint.v1",
        "protocol_id": config["protocol_id"],
        "variant": "ghd_conditioned_gine_gps_unet",
        "seed": seed,
        "best_epoch": best_epoch,
        "model_state_dict": best_state,
        "optimizer_selection_metric": "validation_field_relative_l2",
    }
    _strict_atomic_torch_save(checkpoint_path, checkpoint)
    result = {
        "schema_version": "aurora.aneug_processed_v4_d11.private_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "adaptation_identity": "matched_reimplementation_not_reproduction",
        "baseline_feasible": passed,
        "functional_readout_development_eligible": passed,
        "functional_readout_authorized": False,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "smoke": smoke,
        "validation": final_validation,
        "history": history,
        "train_case_count": len(train_cases),
        "validation_case_count": len(validation_cases),
        "outer_or_auxiliary_values_read": False,
        "case_ids_included": False,
        "development_only": True,
        "paper_result_or_claim": False,
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    validate_activation(args.activation, config, args.expected_commit)
    _require(torch.cuda.is_available(), "cuda_required")
    torch.set_num_threads(4)
    run_development(config, args.cache, args.result, args.checkpoint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
