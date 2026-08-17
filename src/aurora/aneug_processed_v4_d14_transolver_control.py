"""Matched-information full-cycle Transolver control for processed AneuG v4.

The physics-slice attention follows the official Transolver design, while the
data adapter, GHD conditioner, complete-cycle output and tangent projection are
AURORA-specific.  This is a strong comparator, not a proposed contribution and
not an exact reproduction of an upstream task.
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

from aurora.aneug_processed_v4_d9 import (
    case_metrics,
    field_loss,
    load_cached_split,
    model_parameter_count,
    tangent_projection,
)


class D14TransolverControlError(RuntimeError):
    """Raised when a D14 evidence, data or execution boundary is violated."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise D14TransolverControlError(label)


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
        == "aurora.aneug_processed_v4_d14_transolver_control.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_processed_v4_d14_transolver_control_v1",
        "protocol",
    )
    _require(config.get("status") == "prepared_non_executable", "status")
    source = config["source"]
    _require(
        source["repository"] == "thuml/Transolver"
        and source["commit"] == "75e0f67643806a81cd1d3f6adc88dd8c02416fe7"
        and source["license"] == "MIT",
        "source",
    )
    boundary = config["bound_data"]
    _require(
        (
            boundary["train_cases"],
            boundary["validation_cases"],
            boundary["outer_cases"],
            boundary["auxiliary_cases"],
            boundary["phases"],
            boundary["nodes"],
        )
        == (406, 51, 51, 70, 80, 13_902),
        "data_shape",
    )
    _require(boundary["read_outer_or_auxiliary"] is False, "sealed_data")
    identity = config["comparison_identity"]
    _require(
        identity["label"]
        == "matched_information_full_cycle_Transolver_adaptation_not_reproduction",
        "identity",
    )
    _require(identity["proposed_method"] is False, "comparator_role")
    architecture = config["architecture"]
    _require(
        (
            architecture["width"],
            architecture["attention_heads"],
            architecture["blocks"],
            architecture["slices"],
            architecture["mlp_ratio"],
            architecture["output_phases"],
        )
        == (256, 8, 8, 32, 2, 80),
        "architecture",
    )
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
        optimization["checkpoint_selection"]
        == "lowest_validation_field_relative_L2_then_earliest_epoch"
        and config["decision_rule"]["absolute_field_threshold"] is None,
        "selection",
    )
    authorization = config["authorization"]
    _require(authorization["execute_now"] is False, "non_executable")
    _require(authorization["requires_fresh_private_activation"] is True, "activation")
    for key in (
        "method_combination_search",
        "multi_seed_confirmation",
        "outer_test",
        "paper_claim",
        "publish_numeric_result",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")
    _require(
        authorization["server"] == "introai9"
        and authorization["excluded_server"] == "junjinyong",
        "server_scope",
    )


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
        == "aurora.aneug_processed_v4_d14.private_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "D14_Transolver_validation_control",
        "activation_stage",
    )
    _require(activation.get("d12_terminal_record_sha256"), "d12_terminal_record")
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    _require(
        activation.get("cache_manifest_sha256")
        == config["bound_data"]["cache_manifest_sha256"],
        "activation_cache",
    )
    return activation


class PhysicsSliceAttention(nn.Module):
    """Transolver-style physics attention on an irregular node set."""

    def __init__(
        self, width: int, heads: int = 8, slices: int = 32, dropout: float = 0.0
    ) -> None:
        super().__init__()
        _require(width % heads == 0, "attention_width")
        self.heads = heads
        self.head_width = width // heads
        self.scale = self.head_width**-0.5
        self.temperature = nn.Parameter(torch.full((1, heads, 1, 1), 0.5))
        self.project_assignment = nn.Linear(self.head_width, slices)
        nn.init.orthogonal_(self.project_assignment.weight)
        self.project_key = nn.Linear(width, width)
        self.project_value = nn.Linear(width, width)
        self.to_query = nn.Linear(self.head_width, self.head_width, bias=False)
        self.to_key = nn.Linear(self.head_width, self.head_width, bias=False)
        self.to_value = nn.Linear(self.head_width, self.head_width, bias=False)
        self.output = nn.Sequential(nn.Linear(width, width), nn.Dropout(dropout))
        self.dropout = nn.Dropout(dropout)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        _require(features.ndim == 2, "attention_input")
        nodes, width = features.shape
        key_features = self.project_key(features).reshape(
            nodes, self.heads, self.head_width
        )
        value_features = self.project_value(features).reshape(
            nodes, self.heads, self.head_width
        )
        key_features = key_features.permute(1, 0, 2).contiguous()
        value_features = value_features.permute(1, 0, 2).contiguous()
        temperature = torch.clamp(self.temperature.squeeze(0), min=0.05)
        assignments = torch.softmax(
            self.project_assignment(key_features) / temperature, dim=-1
        )
        normalizer = assignments.sum(dim=1).clamp(min=1e-5)
        tokens = torch.einsum("hnc,hns->hsc", value_features, assignments)
        tokens = tokens / normalizer.unsqueeze(-1)
        query = self.to_query(tokens)
        key = self.to_key(tokens)
        value = self.to_value(tokens)
        attention = torch.softmax(
            torch.matmul(query, key.transpose(-1, -2)) * self.scale, dim=-1
        )
        attention = self.dropout(attention)
        output_tokens = torch.matmul(attention, value)
        output = torch.einsum("hsc,hns->hnc", output_tokens, assignments)
        output = output.permute(1, 0, 2).reshape(nodes, width)
        return self.output(output)


class TransolverBlock(nn.Module):
    """Pre-normalized physics attention and residual feed-forward block."""

    def __init__(
        self,
        width: int,
        heads: int,
        slices: int,
        mlp_ratio: int,
        dropout: float,
    ) -> None:
        super().__init__()
        self.attention_norm = nn.LayerNorm(width)
        self.attention = PhysicsSliceAttention(width, heads, slices, dropout)
        self.feed_forward_norm = nn.LayerNorm(width)
        self.feed_forward = nn.Sequential(
            nn.Linear(width, width * mlp_ratio),
            nn.GELU(),
            nn.Linear(width * mlp_ratio, width),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        features = features + self.attention(self.attention_norm(features))
        return features + self.feed_forward(self.feed_forward_norm(features))


class FullCycleTransolver(nn.Module):
    """Same-information Transolver adaptation with an 80-phase tangent output."""

    variant = "direct_cycle"

    def __init__(
        self,
        *,
        width: int = 256,
        heads: int = 8,
        blocks: int = 8,
        slices: int = 32,
        mlp_ratio: int = 2,
        dropout: float = 0.0,
        output_phases: int = 80,
    ) -> None:
        super().__init__()
        self.output_phases = output_phases
        self.node_input = nn.Sequential(
            nn.Linear(7, 2 * width),
            nn.GELU(),
            nn.Linear(2 * width, width),
        )
        self.ghd_conditioner = nn.Sequential(
            nn.LayerNorm(432),
            nn.Linear(432, 2 * width),
            nn.GELU(),
            nn.Linear(2 * width, width),
        )
        self.blocks = nn.ModuleList(
            [
                TransolverBlock(width, heads, slices, mlp_ratio, dropout)
                for _ in range(blocks)
            ]
        )
        self.output_norm = nn.LayerNorm(width)
        self.output = nn.Linear(width, output_phases * 3)
        self._initialize_weights()

    def _initialize_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.trunc_normal_(module.weight, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                nn.init.zeros_(module.bias)
                nn.init.ones_(module.weight)
        for block in self.blocks:
            nn.init.orthogonal_(block.attention.project_assignment.weight)

    def forward(self, case: Mapping[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        coordinates = case["coordinates"]
        normals = case["normals"]
        weights = case["vertex_weights"]
        relative_area = torch.log(
            torch.clamp(weights / torch.clamp(weights.mean(), min=1e-12), min=1e-8)
        ).unsqueeze(-1)
        features = self.node_input(
            torch.cat((coordinates, normals, relative_area), dim=-1)
        )
        condition = self.ghd_conditioner(case["ghd"].reshape(1, -1)).squeeze(0)
        features = features + condition.unsqueeze(0)
        for block in self.blocks:
            features = block(features)
        raw = self.output(self.output_norm(features))
        raw = raw.reshape(features.shape[0], self.output_phases, 3)
        raw = raw.permute(1, 0, 2).contiguous()
        field = tangent_projection(raw, normals)
        return {"field": field, "raw_field": field}


@torch.no_grad()
def evaluate(
    model: FullCycleTransolver,
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
    provenance: Mapping[str, str],
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    cache = Path(cache_path)
    _require(
        file_sha256(cache / "cache_manifest.json")
        == config["bound_data"]["cache_manifest_sha256"],
        "cache_identity",
    )
    manifest = json.loads((cache / "cache_manifest.json").read_text(encoding="utf-8"))
    _require(
        manifest.get("r0_pass") is True
        and manifest.get("train_cases") == 406
        and manifest.get("validation_cases") == 51
        and manifest.get("outer_cases_read") == 0
        and manifest.get("auxiliary_cases_read") == 0,
        "cache_boundary",
    )
    optimization = config["optimization"]
    architecture = config["architecture"]
    seed = int(optimization["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device("cuda")
    train_cases = load_cached_split(cache, "train")
    validation_cases = load_cached_split(cache, "validation")
    model = FullCycleTransolver(
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
        smoke_output, smoke_case["wss"], smoke_case["vertex_weights"]
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
            prediction = model(case)["field"]
            loss = field_loss(prediction, case["wss"], case["vertex_weights"])
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
    checkpoint = {
        "schema_version": "aurora.aneug_processed_v4_d14.private_checkpoint.v1",
        "protocol_id": config["protocol_id"],
        "variant": "matched_information_full_cycle_Transolver",
        "seed": seed,
        "best_epoch": best_epoch,
        "model_state_dict": best_state,
        "optimizer_selection_metric": "validation_field_relative_l2",
        **dict(provenance),
    }
    _strict_atomic_torch_save(checkpoint_path, checkpoint)
    result = {
        "schema_version": "aurora.aneug_processed_v4_d14.private_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "comparison_identity": config["comparison_identity"]["label"],
        "exact_upstream_reproduction": False,
        "proposed_method": False,
        "absolute_pass_fail_gate": None,
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
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    _require(
        all(
            value is not None
            for value in (
                args.activation,
                args.expected_commit,
                args.cache,
                args.result,
                args.checkpoint,
            )
        ),
        "execution_arguments",
    )
    activation = validate_activation(args.activation, config, args.expected_commit)
    provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "cache_manifest_sha256": config["bound_data"]["cache_manifest_sha256"],
        "d12_terminal_record_sha256": activation["d12_terminal_record_sha256"],
    }
    run_development(
        config, args.cache, args.result, args.checkpoint, provenance
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
