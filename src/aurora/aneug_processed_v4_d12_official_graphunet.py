"""D12 direct execution of the released AneuG Graph U-Net model class.

The released model implementation is imported from a pinned, clean upstream
checkout.  This module supplies only the experiment protocol adapter: the D5
split, D9 cache, batching, loss, checkpointing and evaluation.  It is not an
end-to-end reproduction of the released trainer and never reads outer data.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import math
import random
import sys
import time
import types
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_processed_v4_d9 import (
    case_metrics,
    load_cached_split,
    model_parameter_count,
    tangent_projection,
)


class D12OfficialGraphUNetError(RuntimeError):
    """Raised when a D12 evidence, source or data boundary is violated."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise D12OfficialGraphUNetError(label)


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
        == "aurora.aneug_processed_v4_d12_official_graphunet.v1",
        "config_schema",
    )
    _require(config.get("status") == "executable_validation_development", "status")
    source = config["source"]
    _require(
        source["repository"] == "WenHaoDing/AneuG-Flow"
        and source["commit"] == "4a090a0f12538deef6fcea88b81afe78ce38152e",
        "source_identity",
    )
    identity = config["comparison_identity"]
    _require(
        identity["label"]
        == "direct_execution_of_released_GraphUNet_model_class_with_protocol_adapter",
        "comparison_label",
    )
    _require(identity["exact_end_to_end_reproduction"] is False, "reproduction_claim")
    _require(identity["unchanged_released_model_class_and_forward"] is True, "model_source")
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
            optimization["snapshot_batch_size"],
            optimization["maximum_coverage_epochs"],
            optimization["minimum_coverage_epochs"],
            optimization["validation_interval_coverage_epochs"],
            optimization["early_stopping_validation_checks"],
        )
        == (1103, 32, 80, 20, 5, 6),
        "optimization",
    )
    _require(
        optimization["learning_rate"] == 3e-4
        and optimization["weight_decay"] == 0.01,
        "optimizer",
    )
    _require(config["decision_rule"]["absolute_field_threshold"] is None, "threshold")
    dependency = config["dependency"]
    _require(
        dependency["torch"] == "2.5.1+cu118"
        and dependency["torch_geometric"] == "2.6.1",
        "dependency",
    )
    authorization = config["authorization"]
    _require(authorization["execute_validation_development"] is True, "execute")
    for key in (
        "resume_from_interrupted_checkpoint",
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
        == "aurora.aneug_processed_v4_d12.private_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "D12_official_graphunet_validation",
        "activation_stage",
    )
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    _require(
        activation.get("cache_manifest_sha256")
        == config["bound_data"]["cache_manifest_sha256"],
        "activation_cache",
    )
    _require(activation.get("official_commit") == config["source"]["commit"], "activation_source")
    return activation


def balanced_snapshot_pairs(
    case_count: int, phase_count: int, seed: int, coverage_epoch: int
) -> list[tuple[int, int]]:
    _require(case_count > 0 and phase_count > 1 and coverage_epoch >= 0, "pair_shape")
    pairs = [(case_index, phase) for case_index in range(case_count) for phase in range(phase_count)]
    random.Random(seed + 104_729 * coverage_epoch).shuffle(pairs)
    return pairs


def matched_snapshot_loss(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    vertex_weights: torch.Tensor,
) -> torch.Tensor:
    _require(
        prediction.shape == reference.shape
        and prediction.ndim == 3
        and prediction.shape[-1] == 3,
        "loss_field_shape",
    )
    _require(
        vertex_weights.shape == prediction.shape[:2]
        and bool((vertex_weights > 0).all().item()),
        "loss_weight_shape",
    )
    numerator = torch.sum(vertex_weights * torch.sum((prediction - reference) ** 2, dim=-1))
    denominator = torch.sum(vertex_weights * torch.sum(reference**2, dim=-1))
    return numerator / torch.clamp(denominator, min=1e-12)


def _install_unused_pytorch3d_import_stub() -> None:
    if importlib.util.find_spec("pytorch3d") is not None or "pytorch3d" in sys.modules:
        return
    package = types.ModuleType("pytorch3d")
    package.__path__ = []  # type: ignore[attr-defined]
    structures = types.ModuleType("pytorch3d.structures")

    class UnusedMeshesImport:
        pass

    structures.Meshes = UnusedMeshesImport  # type: ignore[attr-defined]
    package.structures = structures  # type: ignore[attr-defined]
    sys.modules["pytorch3d"] = package
    sys.modules["pytorch3d.structures"] = structures


def import_released_model_class(
    official_root: str | Path, config: Mapping[str, Any]
) -> type[torch.nn.Module]:
    root = Path(official_root).resolve()
    source = config["source"]
    paths = {
        "model_sha256": root / "new_version/models/DynamicGraphUNet.py",
        "graphgps_encoders_sha256": root / "new_version/models/GraphGPS_encoders.py",
        "spline_module_sha256": root / "new_version/models/SplineCNNUNet.py",
        "pointnet_module_sha256": root / "new_version/models/pointnet.py",
        "released_trainer_sha256": root / "train_baselines.py",
    }
    for key, path in paths.items():
        _require(path.is_file() and file_sha256(path) == source[key], f"official_{key}")
    _install_unused_pytorch3d_import_stub()
    root_string = str(root)
    if root_string not in sys.path:
        sys.path.insert(0, root_string)
    module = importlib.import_module("new_version.models.DynamicGraphUNet")
    model_class = getattr(module, "PyGGraphUNetwTemporalEmbedding", None)
    _require(isinstance(model_class, type), "official_model_class")
    return model_class


def build_released_model(
    official_root: str | Path,
    config: Mapping[str, Any],
    topology: Mapping[str, torch.Tensor],
) -> torch.nn.Module:
    model_class = import_released_model_class(official_root, config)
    architecture = config["architecture"]
    return model_class(
        in_channels=int(architecture["in_channels"]),
        hidden_channels=int(architecture["hidden_channels"]),
        out_channels=int(architecture["out_channels"]),
        depth=int(architecture["depth"]),
        pool_ratios=list(architecture["pool_ratios"]),
        sum_res=bool(architecture["sum_res"]),
        act=str(architecture["activation"]),
        dim_te=int(architecture["time_embedding_dim"]),
        dim_wfe=int(architecture["waveform_embedding_dim"]),
        idx_list=[topology["idx1"], topology["idx2"]],
        edge_index_list=[topology["edge0"], topology["edge1"], topology["edge2"]],
    )


def _snapshot_batch(
    cases: Sequence[Mapping[str, torch.Tensor]],
    pairs: Sequence[tuple[int, int]],
    device: torch.device,
) -> tuple[Any, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    from torch_geometric.data import Data

    selected = [cases[case_index] for case_index, _ in pairs]
    node_count = int(selected[0]["coordinates"].shape[0])
    coordinates = torch.stack([case["coordinates"] for case in selected]).to(
        device=device, non_blocking=True
    )
    normals = torch.stack([case["normals"] for case in selected]).to(
        device=device, non_blocking=True
    )
    weights = torch.stack([case["vertex_weights"] for case in selected]).to(
        device=device, non_blocking=True
    )
    target = torch.stack(
        [case["wss"][phase] for case, (_, phase) in zip(selected, pairs)]
    ).to(device=device, non_blocking=True)
    batch = torch.arange(len(pairs), device=device).repeat_interleave(node_count)
    data = Data(
        x=torch.cat((coordinates, normals), dim=-1).reshape(-1, 6),
        pos=coordinates.reshape(-1, 3),
        batch=batch,
    )
    phases = torch.tensor([phase for _, phase in pairs], device=device, dtype=torch.int64).view(-1, 1)
    return data, phases, target, normals, weights


def _predict_snapshots(
    model: torch.nn.Module,
    cases: Sequence[Mapping[str, torch.Tensor]],
    pairs: Sequence[tuple[int, int]],
    device: torch.device,
    waveform: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    data, phases, target, normals, weights = _snapshot_batch(cases, pairs, device)
    raw = model(data, phases, waveform).reshape(len(pairs), target.shape[1], 3)
    prediction = tangent_projection(raw, normals)
    return prediction, target, weights


@torch.no_grad()
def evaluate_full_cycles(
    model: torch.nn.Module,
    cases: Sequence[Mapping[str, torch.Tensor]],
    device: torch.device,
    waveform: torch.Tensor,
    batch_size: int,
) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    for case_index, case in enumerate(cases):
        chunks: list[torch.Tensor] = []
        pairs = [(case_index, phase) for phase in range(80)]
        for start in range(0, 80, batch_size):
            prediction, _, _ = _predict_snapshots(
                model, cases, pairs[start : start + batch_size], device, waveform
            )
            chunks.append(prediction.cpu())
        field = torch.cat(chunks, dim=0)
        per_case.append(case_metrics(field, case["wss"], case["vertex_weights"]))
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
    official_root: str | Path,
    result_path: str | Path,
    checkpoint_directory: str | Path,
) -> dict[str, Any]:
    import torch_geometric

    _require(torch.__version__ == config["dependency"]["torch"], "torch_version")
    _require(torch_geometric.__version__ == config["dependency"]["torch_geometric"], "pyg_version")
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
        and manifest.get("validation_cases") == 51,
        "cache_boundary",
    )
    _require(
        manifest.get("outer_cases_read") == 0
        and manifest.get("auxiliary_cases_read") == 0,
        "sealed_cache",
    )
    checkpoint_root = Path(checkpoint_directory)
    _require(not checkpoint_root.exists(), "checkpoint_directory_exists")
    checkpoint_root.mkdir(parents=True)

    optimization = config["optimization"]
    seed = int(optimization["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(4)
    device = torch.device("cuda")
    topology = torch.load(cache / "topology.pt", map_location="cpu", weights_only=True)
    train_cases = load_cached_split(cache, "train")
    validation_cases = load_cached_split(cache, "validation")
    model = build_released_model(official_root, config, topology).to(device)
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
    batch_size = int(optimization["snapshot_batch_size"])
    maximum_epochs = int(optimization["maximum_coverage_epochs"])
    minimum_epochs = int(optimization["minimum_coverage_epochs"])
    validation_interval = int(optimization["validation_interval_coverage_epochs"])
    patience_checks = int(optimization["early_stopping_validation_checks"])
    best_field = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale_checks = 0
    total_steps = 0
    history: list[dict[str, float | int]] = []
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()

    # Exercise the exact registered training batch before the first optimizer
    # step so memory or sparse-kernel infeasibility is an execution result,
    # never a partially trained scientific comparison.
    smoke_pairs = [(0, phase) for phase in range(batch_size)]
    smoke_started = time.monotonic()
    model.train()
    prediction, target, weights = _predict_snapshots(
        model, train_cases, smoke_pairs, device, waveform
    )
    smoke_loss = matched_snapshot_loss(prediction, target, weights)
    smoke_loss.backward()
    _require(bool(torch.isfinite(smoke_loss).item()), "nonfinite_smoke")
    optimizer.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    smoke = {
        "snapshot_batch_size": len(smoke_pairs),
        "finite_forward_backward": True,
        "seconds": time.monotonic() - smoke_started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
    }
    del prediction, target, weights, smoke_loss

    for coverage_epoch in range(maximum_epochs):
        model.train()
        pairs = balanced_snapshot_pairs(len(train_cases), 80, seed, coverage_epoch)
        epoch_loss = 0.0
        epoch_batches = 0
        for start in range(0, len(pairs), batch_size):
            batch_pairs = pairs[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            prediction, target, weights = _predict_snapshots(
                model, train_cases, batch_pairs, device, waveform
            )
            loss = matched_snapshot_loss(prediction, target, weights)
            _require(bool(torch.isfinite(loss).item()), "nonfinite_training_loss")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                model.parameters(), float(optimization["gradient_clip_norm"])
            )
            optimizer.step()
            epoch_loss += float(loss.detach().item())
            epoch_batches += 1
            total_steps += 1
        scheduler.step()
        if (coverage_epoch + 1) % validation_interval != 0:
            print(
                json.dumps(
                    {
                        "coverage_epoch": coverage_epoch + 1,
                        "optimizer_steps": total_steps,
                        "training_loss": epoch_loss / epoch_batches,
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            continue
        validation = evaluate_full_cycles(
            model, validation_cases, device, waveform, batch_size
        )
        validation_field = float(validation["aggregate"]["field_relative_l2"])
        row = {
            "coverage_epoch": coverage_epoch + 1,
            "optimizer_steps": total_steps,
            "training_loss": epoch_loss / epoch_batches,
            "validation_field_relative_l2": validation_field,
            "learning_rate": float(scheduler.get_last_lr()[0]),
        }
        history.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
        state = {
            key: value.detach().cpu().clone() for key, value in model.state_dict().items()
        }
        _strict_atomic_torch_save(
            checkpoint_root / f"coverage_{coverage_epoch + 1:03d}.pt",
            {
                "schema_version": "aurora.aneug_processed_v4_d12.private_checkpoint.v1",
                "protocol_id": config["protocol_id"],
                "official_model_class": config["source"]["model_class"],
                "seed": seed,
                "coverage_epoch": coverage_epoch + 1,
                "optimizer_steps": total_steps,
                "validation_field_relative_l2": validation_field,
                "model_state_dict": state,
            },
        )
        if validation_field < best_field:
            best_field = validation_field
            best_epoch = coverage_epoch + 1
            best_state = state
            stale_checks = 0
        else:
            stale_checks += 1
        if coverage_epoch + 1 >= minimum_epochs and stale_checks >= patience_checks:
            break

    _require(best_state is not None and best_epoch > 0, "missing_best_checkpoint")
    model.load_state_dict(best_state)
    final_validation = evaluate_full_cycles(
        model, validation_cases, device, waveform, batch_size
    )
    _strict_atomic_torch_save(
        checkpoint_root / "best.pt",
        {
            "schema_version": "aurora.aneug_processed_v4_d12.private_checkpoint.v1",
            "protocol_id": config["protocol_id"],
            "official_model_class": config["source"]["model_class"],
            "seed": seed,
            "coverage_epoch": best_epoch,
            "model_state_dict": best_state,
            "optimizer_selection_metric": "validation_field_relative_l2",
        },
    )
    result = {
        "schema_version": "aurora.aneug_processed_v4_d12.private_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "comparison_identity": config["comparison_identity"]["label"],
        "exact_end_to_end_reproduction": False,
        "absolute_pass_fail_gate": None,
        "best_coverage_epoch": best_epoch,
        "coverage_epochs_completed": coverage_epoch + 1,
        "optimizer_steps": total_steps,
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "smoke": smoke,
        "validation": final_validation,
        "validation_check_history": history,
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
    parser.add_argument("--official-root", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--checkpoint-directory", type=Path, required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    validate_activation(args.activation, config, args.expected_commit)
    _require(torch.cuda.is_available(), "cuda_required")
    run_development(
        config,
        args.cache,
        args.official_root,
        args.result,
        args.checkpoint_directory,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
