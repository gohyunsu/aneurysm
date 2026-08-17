"""Bounded D10 repair round 1: test the D9 direct optimization horizon."""

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

from aurora.aneug_processed_v4_d9 import (
    MeshCanonicalizedPilot,
    evaluate,
    load_cached_split,
    model_parameter_count,
    training_loss,
)


class D10RepairError(RuntimeError):
    """Raised when a D10 repair boundary is violated."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise D10RepairError(label)


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
    _require(config.get("schema_version") == "aurora.aneug_processed_v4_d10_bounded_repair.v1", "config_schema")
    _require(config.get("status") == "executable_round1_validation_only", "config_status")
    boundary = config["immutable_boundary"]
    _require((boundary["train_cases"], boundary["validation_cases"], boundary["outer_cases"], boundary["auxiliary_cases"]) == (406, 51, 51, 70), "split")
    for key in ("change_backbone", "change_loss", "change_seed", "change_split", "change_metric", "change_threshold", "read_outer_or_auxiliary"):
        _require(boundary[key] is False, f"boundary_{key}")
    budget = config["bounded_repair_budget"]
    _require(budget["maximum_repair_rounds"] == 2 and budget["current_round"] == 1, "round_budget")
    _require(budget["maximum_training_jobs"] == 2 and budget["maximum_total_requested_gpu_hours"] == 8, "compute_budget")
    round1 = config["round1_optimization_horizon"]
    _require(round1["single_failure_hypothesis"] == "D9 direct baseline was under-trained by a 20-epoch cosine horizon", "hypothesis")
    _require((round1["seed"], round1["maximum_epochs"], round1["minimum_epochs"], round1["early_stopping_patience"]) == (1103, 251, 60, 25), "optimization")
    _require(round1["learning_rate"] == 3e-4 and round1["weight_decay"] == 1e-4, "optimizer")
    _require(round1["scheduler"] == "cosine_to_0p1_initial_over_251_epochs", "scheduler")
    _require(round1["direct_feasibility_threshold"] == 0.35, "threshold")
    round2 = config["conditional_round2_projection_alignment"]
    _require(round2["executable_now"] is False and round2["requires_round1_pass"] is True, "round2_closed")
    _require(round2["only_allowed_change"] == "compute moment training field loss through the same exact projection used at validation", "round2_change")
    authorization = config["authorization"]
    _require(authorization["execute_round1_once"] is True, "execute_round1")
    for key in ("execute_round2_now", "multi_seed_confirmation", "outer_test", "paper_result_or_claim", "publish_numeric_result", "maintain_public_site"):
        _require(authorization[key] is False, f"authorization_{key}")
    _require(authorization["excluded_server"] == "junjinyong", "excluded_server")


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(path: str | Path, config: Mapping[str, Any], expected_commit: str) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(activation.get("schema_version") == "aurora.aneug_processed_v4_d10.private_activation.v1", "activation_schema")
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(activation.get("public_commit") == expected_commit and activation.get("quality_conclusion") == "success", "activation_public")
    _require(activation.get("authorized_stage") == "D10_round1_direct_horizon", "activation_stage")
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    for key in ("cache_manifest_sha256", "d9_direct_result_sha256", "d9_aggregate_sha256", "d9a_result_sha256"):
        _require(activation.get(key) == config["bound_evidence"][key], f"activation_{key}")
    return activation


def baseline_feasible(field_relative_l2: float, threshold: float = 0.35) -> bool:
    _require(math.isfinite(field_relative_l2) and field_relative_l2 >= 0.0, "field_metric")
    return field_relative_l2 <= threshold


def run_round1(config: Mapping[str, Any], cache_path: str | Path, result_path: str | Path, checkpoint_path: str | Path) -> dict[str, Any]:
    cache = Path(cache_path)
    _require(file_sha256(cache / "cache_manifest.json") == config["bound_evidence"]["cache_manifest_sha256"], "cache_identity")
    manifest = json.loads((cache / "cache_manifest.json").read_text(encoding="utf-8"))
    _require(manifest.get("r0_pass") is True and manifest.get("train_cases") == 406 and manifest.get("validation_cases") == 51, "cache_boundary")
    _require(manifest.get("outer_cases_read") == 0 and manifest.get("auxiliary_cases_read") == 0, "sealed_cache")

    repair = config["round1_optimization_horizon"]
    seed = int(repair["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device("cuda")
    topology = torch.load(cache / "topology.pt", map_location=device, weights_only=True)
    train_cases = load_cached_split(cache, "train")
    validation_cases = load_cached_split(cache, "validation")
    model = MeshCanonicalizedPilot(topology, variant="direct_cycle").to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(repair["learning_rate"]), weight_decay=float(repair["weight_decay"]))
    maximum_epochs = int(repair["maximum_epochs"])
    minimum_epochs = int(repair["minimum_epochs"])
    patience = int(repair["early_stopping_patience"])
    accumulation = int(repair["gradient_accumulation_cases"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=maximum_epochs, eta_min=0.1 * float(repair["learning_rate"]))
    best_field = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, float | int]] = []
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()

    for epoch in range(maximum_epochs):
        model.train()
        order = list(range(len(train_cases)))
        random.Random(seed + epoch).shuffle(order)
        optimizer.zero_grad(set_to_none=True)
        epoch_loss = 0.0
        for step, index in enumerate(order):
            case = {key: value.to(device=device, non_blocking=True) for key, value in train_cases[index].items()}
            output = model(case, exact_moment_projection=False)
            loss = training_loss(output, case["wss"], case["vertex_weights"], "direct_cycle")
            _require(bool(torch.isfinite(loss).item()), "nonfinite_training_loss")
            (loss / accumulation).backward()
            epoch_loss += float(loss.detach().item())
            if (step + 1) % accumulation == 0 or step + 1 == len(order):
                torch.nn.utils.clip_grad_norm_(model.parameters(), float(repair["gradient_clip_norm"]))
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
        scheduler.step()
        validation = evaluate(model, validation_cases, device)
        validation_field = float(validation["aggregate"]["field_relative_l2"])
        row = {"epoch": epoch + 1, "training_loss": epoch_loss / len(order), "validation_field_relative_l2": validation_field, "learning_rate": float(scheduler.get_last_lr()[0])}
        history.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
        if validation_field < best_field:
            best_field = validation_field
            best_epoch = epoch + 1
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
        if epoch + 1 >= minimum_epochs and stale >= patience:
            break

    _require(best_state is not None and best_epoch > 0, "missing_best_checkpoint")
    model.load_state_dict(best_state)
    final_validation = evaluate(model, validation_cases, device)
    final_field = float(final_validation["aggregate"]["field_relative_l2"])
    passed = baseline_feasible(final_field, float(repair["direct_feasibility_threshold"]))
    checkpoint = {
        "schema_version": "aurora.aneug_processed_v4_d10.private_checkpoint.v1",
        "protocol_id": config["protocol_id"],
        "round": 1,
        "variant": "direct_cycle_horizon",
        "seed": seed,
        "best_epoch": best_epoch,
        "model_state_dict": best_state,
        "optimizer_selection_metric": "validation_field_relative_l2",
    }
    _strict_atomic_torch_save(checkpoint_path, checkpoint)
    result = {
        "schema_version": "aurora.aneug_processed_v4_d10.private_round1_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "round": 1,
        "single_failure_hypothesis": repair["single_failure_hypothesis"],
        "round1_pass": passed,
        "round2_registration_eligible": passed,
        "round2_authorized": False,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
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
    run_round1(config, args.cache, args.result, args.checkpoint)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
