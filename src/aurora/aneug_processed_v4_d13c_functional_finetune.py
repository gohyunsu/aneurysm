"""Same-backbone complete-cycle functional fine-tuning on processed AneuG v4.

Every variant starts from the exact selected D11 checkpoint.  The experiment
isolates objective and gradient-combination effects without changing the mesh
encoder, information, split or output representation.  It is validation
development, not confirmatory or outer-test evidence.
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

from aurora.aneug_processed_v4_d11_strong_baseline import GHDConditionedGPSUNet
from aurora.aneug_processed_v4_d9 import (
    case_metrics,
    load_cached_split,
    model_parameter_count,
)
from aurora.cycle_functional_alignment import (
    complete_cycle_alignment_terms,
    field_anchored_gradient_combination,
)


VARIANTS = (
    "field_only",
    "statistics_scalarized",
    "osi_scalarized",
    "all_scalarized",
    "all_field_anchored",
)
LOSS_TERMS = ("field", "mean_vector", "tawss", "osi")


class D13CFunctionalFinetuneError(RuntimeError):
    """Raised when a D13C evidence, data or execution boundary is violated."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise D13CFunctionalFinetuneError(label)


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
        == "aurora.aneug_processed_v4_d13c_functional_finetune.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_processed_v4_d13c_functional_finetune_v1",
        "protocol",
    )
    _require(config.get("status") == "prepared_non_executable", "status")
    predecessor = config["predecessors"]
    _require(
        predecessor["d11_checkpoint_sha256"]
        == "e903f244e8cfef04636a846cc2e4a96f49098eea859f0a8a84455fcddcd4a12c"
        and predecessor["d12_terminal_record_required"] is True
        and predecessor["d12_performance_threshold_required"] is False,
        "predecessor",
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
    _require(tuple(config["objective"]["variants"]) == VARIANTS, "variants")
    _require(
        config["objective"]["loss_normalizers"]
        == "mean_D11_initial_train_term_over_all_406_train_cases"
        and config["objective"]["checkpoint_utility_normalizers"]
        == "same_initial_D11_validation_endpoints_recomputed_before_each_variant"
        and config["objective"]["functional_to_field_norm_ratio"] == 1.0
        and config["objective"]["rrt_loss"] is False
        and config["objective"]["hard_posthoc_projection"] is False,
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
        )
        == (1103, 60, 15, 12, 2),
        "optimization",
    )
    _require(
        config["evaluation"]["absolute_performance_threshold"] is None,
        "threshold",
    )
    authorization = config["authorization"]
    _require(authorization["execute_now"] is False, "non_executable")
    _require(authorization["requires_fresh_private_activation"] is True, "activation")
    _require(authorization["one_variant_per_activation"] is True, "variant_scope")
    for key in (
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
    path: str | Path,
    config: Mapping[str, Any],
    expected_commit: str,
    variant: str,
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.aneug_processed_v4_d13c.private_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "D13C_functional_finetune_validation",
        "activation_stage",
    )
    _require(activation.get("authorized_variant") == variant, "activation_variant")
    _require(activation.get("d12_terminal_record_sha256"), "d12_terminal_record")
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    _require(
        activation.get("cache_manifest_sha256")
        == config["bound_data"]["cache_manifest_sha256"],
        "activation_cache",
    )
    _require(
        activation.get("d11_checkpoint_sha256")
        == config["predecessors"]["d11_checkpoint_sha256"],
        "activation_checkpoint",
    )
    return activation


def functional_names(variant: str) -> tuple[str, ...]:
    _require(variant in VARIANTS, "variant")
    if variant == "field_only":
        return ()
    if variant == "statistics_scalarized":
        return ("mean_vector", "tawss")
    if variant == "osi_scalarized":
        return ("osi",)
    return ("mean_vector", "tawss", "osi")


def normalized_objectives(
    terms: Mapping[str, torch.Tensor],
    normalizers: Mapping[str, float],
    variant: str,
) -> tuple[torch.Tensor, torch.Tensor | None, torch.Tensor]:
    names = functional_names(variant)
    for name in LOSS_TERMS:
        _require(name in terms and float(normalizers[name]) > 0.0, "normalizer")
    field = terms["field"] / float(normalizers["field"])
    if not names:
        return field, None, field
    functional = sum(terms[name] / float(normalizers[name]) for name in names)
    functional = functional / len(names)
    return field, functional, field + functional


def validation_utility(
    aggregate_metrics: Mapping[str, float],
    normalizers: Mapping[str, float],
    variant: str,
) -> float:
    names = functional_names(variant)
    _require(
        all(
            name in normalizers
            and math.isfinite(float(normalizers[name]))
            and float(normalizers[name]) > 0.0
            for name in LOSS_TERMS
        ),
        "selection_normalizer",
    )
    metric_keys = {
        "field": "field_relative_l2",
        "mean_vector": "mean_vector_tawss_normalized_l2",
        "tawss": "tawss_normalized_absolute_error",
        "osi": "osi_mae",
    }
    field = float(aggregate_metrics[metric_keys["field"]]) / float(
        normalizers["field"]
    )
    if not names:
        return field
    functional = sum(
        float(aggregate_metrics[metric_keys[name]]) / float(normalizers[name])
        for name in names
    ) / len(names)
    value = field + functional
    _require(math.isfinite(value), "validation_utility")
    return value


def train_wss_rms(cases: Sequence[Mapping[str, torch.Tensor]]) -> float:
    _require(len(cases) > 0, "train_cases")
    total = 0.0
    for case in cases:
        field = case["wss"].to(torch.float64)
        weights = case["vertex_weights"].to(torch.float64)
        _require(tuple(field.shape[-1:]) == (3,), "train_field_shape")
        _require(weights.shape == (field.shape[1],), "train_weight_shape")
        _require(
            bool(torch.isfinite(field).all().item())
            and bool(torch.isfinite(weights).all().item())
            and bool((weights >= 0).all().item())
            and bool((weights.sum() > 0).item()),
            "train_values",
        )
        weights = weights / weights.sum()
        energy = torch.sum(weights.unsqueeze(0) * torch.sum(field.square(), dim=-1))
        energy = energy / field.shape[0]
        total += float(energy.item())
    value = math.sqrt(total / len(cases))
    _require(math.isfinite(value) and value > 0.0, "train_rms")
    return value


def alignment_terms(
    prediction: torch.Tensor,
    case: Mapping[str, torch.Tensor],
    config: Mapping[str, Any],
    reference_tawss_floor: float,
) -> dict[str, torch.Tensor]:
    phases = int(prediction.shape[0])
    phase_weights = torch.ones(phases, dtype=prediction.dtype, device=prediction.device)
    return complete_cycle_alignment_terms(
        prediction,
        case["wss"],
        phase_weights,
        case["vertex_weights"],
        {"field": 1.0, "mean_vector": 0.0, "tawss": 0.0, "osi": 0.0},
        reference_tawss_floor=reference_tawss_floor,
        osi_pseudo_huber_delta=float(config["objective"]["osi_pseudo_huber_delta"]),
    )


@torch.no_grad()
def compute_train_normalizers(
    model: GHDConditionedGPSUNet,
    cases: Sequence[Mapping[str, torch.Tensor]],
    config: Mapping[str, Any],
    reference_tawss_floor: float,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    sums = {name: 0.0 for name in LOSS_TERMS}
    for cpu_case in cases:
        case = {key: value.to(device=device, non_blocking=True) for key, value in cpu_case.items()}
        terms = alignment_terms(model(case)["field"], case, config, reference_tawss_floor)
        for name in sums:
            sums[name] += float(terms[name].item())
    normalizers = {name: value / len(cases) for name, value in sums.items()}
    _require(
        all(math.isfinite(value) and value > 1e-12 for value in normalizers.values()),
        "train_normalizers",
    )
    return normalizers


@torch.no_grad()
def evaluate(
    model: GHDConditionedGPSUNet,
    cases: Sequence[Mapping[str, torch.Tensor]],
    config: Mapping[str, Any],
    reference_tawss_floor: float,
    selection_normalizers: Mapping[str, float] | None,
    variant: str,
    device: torch.device,
) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    per_case_terms: list[dict[str, float]] = []
    for cpu_case in cases:
        case = {key: value.to(device=device, non_blocking=True) for key, value in cpu_case.items()}
        prediction = model(case)["field"]
        metrics = case_metrics(prediction, case["wss"], case["vertex_weights"])
        terms = alignment_terms(prediction, case, config, reference_tawss_floor)
        metrics["mean_vector_tawss_normalized_l2"] = float(
            torch.sqrt(torch.clamp(terms["mean_vector"], min=0.0)).item()
        )
        per_case.append(metrics)
        per_case_terms.append(
            {name: float(terms[name].item()) for name in LOSS_TERMS}
        )
    metric_keys = tuple(per_case[0])
    aggregate_terms = {
        name: sum(item[name] for item in per_case_terms) / len(per_case_terms)
        for name in LOSS_TERMS
    }
    aggregate = {
        key: sum(item[key] for item in per_case) / len(per_case)
        for key in metric_keys
    }
    utility = None
    if selection_normalizers is not None:
        utility = validation_utility(aggregate, selection_normalizers, variant)
    return {
        "aggregate": aggregate,
        "aggregate_alignment_terms": aggregate_terms,
        "variant_validation_utility": utility,
        "per_case_without_identifiers": per_case,
        "per_case_alignment_terms_without_identifiers": per_case_terms,
        "case_count": len(per_case),
    }


def _add_gradients(
    parameters: Sequence[torch.nn.Parameter],
    gradients: Sequence[torch.Tensor],
    divisor: int,
) -> None:
    _require(len(parameters) == len(gradients) and divisor > 0, "gradient_add")
    for parameter, gradient in zip(parameters, gradients):
        value = gradient.detach() / divisor
        if parameter.grad is None:
            parameter.grad = value.clone()
        else:
            parameter.grad.add_(value)


def backward_case(
    model: torch.nn.Module,
    terms: Mapping[str, torch.Tensor],
    normalizers: Mapping[str, float],
    variant: str,
    accumulation: int,
    functional_to_field_norm_ratio: float,
) -> dict[str, float | bool]:
    field, functional, scalarized = normalized_objectives(terms, normalizers, variant)
    if variant != "all_field_anchored":
        (scalarized / accumulation).backward()
        return {
            "scalarized_value": float(scalarized.detach().item()),
            "projection_applied": False,
            "gradient_cosine_before": 0.0,
            "gradient_conflict_measured": False,
        }

    _require(functional is not None, "anchored_functional")
    parameters = tuple(parameter for parameter in model.parameters() if parameter.requires_grad)
    field_gradients = torch.autograd.grad(
        field,
        parameters,
        retain_graph=True,
        allow_unused=True,
    )
    functional_gradients = torch.autograd.grad(
        functional,
        parameters,
        allow_unused=True,
    )
    active_parameters: list[torch.nn.Parameter] = []
    active_field_gradients: list[torch.Tensor] = []
    active_functional_gradients: list[torch.Tensor] = []
    for parameter, field_gradient, functional_gradient in zip(
        parameters, field_gradients, functional_gradients
    ):
        _require(
            (field_gradient is None) == (functional_gradient is None),
            "anchored_gradient_dependency",
        )
        if field_gradient is None:
            continue
        active_parameters.append(parameter)
        active_field_gradients.append(field_gradient)
        active_functional_gradients.append(functional_gradient)
    _require(len(active_parameters) > 0, "anchored_active_parameters")
    combined = field_anchored_gradient_combination(
        active_field_gradients,
        active_functional_gradients,
        functional_to_field_norm_ratio=functional_to_field_norm_ratio,
    )
    _add_gradients(
        active_parameters,
        combined["combined_gradients"],
        accumulation,
    )
    denominator = torch.clamp(
        combined["field_norm"] * combined["functional_norm_before"], min=1e-12
    )
    cosine = combined["inner_product_before"] / denominator
    return {
        "scalarized_value": float(scalarized.detach().item()),
        "projection_applied": bool(combined["projection_applied"].item()),
        "gradient_cosine_before": float(cosine.detach().item()),
        "gradient_conflict_measured": True,
    }


def load_d11_model(
    checkpoint_path: str | Path,
    topology: Mapping[str, torch.Tensor],
    config: Mapping[str, Any],
    device: torch.device,
) -> GHDConditionedGPSUNet:
    _require(
        file_sha256(checkpoint_path)
        == config["predecessors"]["d11_checkpoint_sha256"],
        "d11_checkpoint_identity",
    )
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    _require(
        payload.get("schema_version")
        == "aurora.aneug_processed_v4_d11.private_checkpoint.v1"
        and payload.get("variant") == "ghd_conditioned_gine_gps_unet"
        and payload.get("best_epoch") == 121,
        "d11_checkpoint_schema",
    )
    model = GHDConditionedGPSUNet(
        topology,
        width=int(config["backbone"]["width"]),
        heads=int(config["backbone"]["attention_heads"]),
    ).to(device)
    model.load_state_dict(payload["model_state_dict"], strict=True)
    return model


def run_development(
    config: Mapping[str, Any],
    cache_path: str | Path,
    d11_checkpoint_path: str | Path,
    variant: str,
    result_path: str | Path,
    checkpoint_path: str | Path,
    provenance: Mapping[str, str],
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    _require(variant in VARIANTS, "variant")
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
    seed = int(optimization["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device("cuda")
    topology = torch.load(cache / "topology.pt", map_location=device, weights_only=True)
    train_cases = load_cached_split(cache, "train")
    validation_cases = load_cached_split(cache, "validation")
    train_rms = train_wss_rms(train_cases)
    reference_tawss_floor = (
        train_rms * float(config["objective"]["reference_tawss_floor_multiplier"])
    )
    model = load_d11_model(d11_checkpoint_path, topology, config, device)
    normalizers = compute_train_normalizers(
        model, train_cases, config, reference_tawss_floor, device
    )
    initial_validation = evaluate(
        model,
        validation_cases,
        config,
        reference_tawss_floor,
        None,
        variant,
        device,
    )
    selection_normalizers = {
        "field": float(initial_validation["aggregate"]["field_relative_l2"]),
        "mean_vector": float(
            initial_validation["aggregate"]["mean_vector_tawss_normalized_l2"]
        ),
        "tawss": float(
            initial_validation["aggregate"]["tawss_normalized_absolute_error"]
        ),
        "osi": float(initial_validation["aggregate"]["osi_mae"]),
    }
    _require(
        all(
            math.isfinite(value) and value > 1e-12
            for value in selection_normalizers.values()
        ),
        "selection_normalizers",
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
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
    ratio = float(config["objective"]["functional_to_field_norm_ratio"])
    best_utility = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, Any]] = []
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()

    smoke_case = {
        key: value.to(device=device, non_blocking=True)
        for key, value in train_cases[0].items()
    }
    smoke_prediction = model(smoke_case)["field"]
    smoke_terms = alignment_terms(
        smoke_prediction, smoke_case, config, reference_tawss_floor
    )
    optimizer.zero_grad(set_to_none=True)
    smoke_diagnostic = backward_case(
        model, smoke_terms, normalizers, variant, 1, ratio
    )
    _require(
        all(
            parameter.grad is None or bool(torch.isfinite(parameter.grad).all().item())
            for parameter in model.parameters()
        ),
        "smoke_gradient",
    )
    optimizer.zero_grad(set_to_none=True)
    smoke = {
        "finite_forward_backward": True,
        "variant": variant,
        "diagnostic": smoke_diagnostic,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
    }
    del smoke_case, smoke_prediction, smoke_terms

    for epoch in range(maximum_epochs):
        model.train()
        order = list(range(len(train_cases)))
        random.Random(seed + epoch).shuffle(order)
        optimizer.zero_grad(set_to_none=True)
        epoch_objective = 0.0
        conflicts = 0
        cosine_sum = 0.0
        for step, index in enumerate(order):
            case = {
                key: value.to(device=device, non_blocking=True)
                for key, value in train_cases[index].items()
            }
            prediction = model(case)["field"]
            terms = alignment_terms(prediction, case, config, reference_tawss_floor)
            diagnostic = backward_case(
                model, terms, normalizers, variant, accumulation, ratio
            )
            epoch_objective += float(diagnostic["scalarized_value"])
            conflicts += int(bool(diagnostic["projection_applied"]))
            cosine_sum += float(diagnostic["gradient_cosine_before"])
            if (step + 1) % accumulation == 0:
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), float(optimization["gradient_clip_norm"])
                )
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
        _require(len(order) % accumulation == 0, "incomplete_accumulation")
        scheduler.step()
        validation = evaluate(
            model,
            validation_cases,
            config,
            reference_tawss_floor,
            selection_normalizers,
            variant,
            device,
        )
        utility = float(validation["variant_validation_utility"])
        row = {
            "epoch": epoch + 1,
            "training_normalized_objective": epoch_objective / len(order),
            "validation_utility": utility,
            "validation_field_relative_l2": float(
                validation["aggregate"]["field_relative_l2"]
            ),
            "validation_tawss_error": float(
                validation["aggregate"]["tawss_normalized_absolute_error"]
            ),
            "validation_osi_mae": float(validation["aggregate"]["osi_mae"]),
            "gradient_conflict_fraction": (
                conflicts / len(order) if variant == "all_field_anchored" else None
            ),
            "mean_gradient_cosine_before": (
                cosine_sum / len(order) if variant == "all_field_anchored" else None
            ),
            "learning_rate": float(scheduler.get_last_lr()[0]),
        }
        history.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
        if utility < best_utility:
            best_utility = utility
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
    final_validation = evaluate(
        model,
        validation_cases,
        config,
        reference_tawss_floor,
        selection_normalizers,
        variant,
        device,
    )
    checkpoint = {
        "schema_version": "aurora.aneug_processed_v4_d13c.private_checkpoint.v1",
        "protocol_id": config["protocol_id"],
        "variant": variant,
        "seed": seed,
        "best_epoch": best_epoch,
        "model_state_dict": best_state,
        "optimizer_selection_metric": "variant_validation_utility",
        "train_term_normalizers": normalizers,
        "selection_endpoint_normalizers": selection_normalizers,
        "reference_tawss_floor": reference_tawss_floor,
        **dict(provenance),
    }
    _strict_atomic_torch_save(checkpoint_path, checkpoint)
    result = {
        "schema_version": "aurora.aneug_processed_v4_d13c.private_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "variant": variant,
        "same_backbone_initialization": True,
        "absolute_pass_fail_gate": None,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "train_wss_rms": train_rms,
        "reference_tawss_floor": reference_tawss_floor,
        "train_term_normalizers": normalizers,
        "selection_endpoint_normalizers": selection_normalizers,
        "smoke": smoke,
        "initial_validation": initial_validation,
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
    parser.add_argument("--d11-checkpoint", type=Path)
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    torch.set_num_threads(4)
    _require(
        all(
            value is not None
            for value in (
                args.activation,
                args.expected_commit,
                args.cache,
                args.d11_checkpoint,
                args.variant,
                args.result,
                args.checkpoint,
            )
        ),
        "execution_arguments",
    )
    activation = validate_activation(
        args.activation, config, args.expected_commit, args.variant
    )
    provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "cache_manifest_sha256": config["bound_data"]["cache_manifest_sha256"],
        "d11_checkpoint_sha256": config["predecessors"]["d11_checkpoint_sha256"],
        "d12_terminal_record_sha256": activation["d12_terminal_record_sha256"],
    }
    run_development(
        config,
        args.cache,
        args.d11_checkpoint,
        args.variant,
        args.result,
        args.checkpoint,
        provenance,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
