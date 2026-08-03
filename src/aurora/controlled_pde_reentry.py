"""Prospective exact-domain re-entry after the failed frozen AURORA G1.

G1r does not modify or relabel G1.  It uses fresh simulation-family seeds,
selects boundary-density and operator checkpoints using validation geometries
only, and removes the two estimator confounds diagnosed by G1b:

* conditional moments and density-only coverage are analytic;
* projective discrepancy is evaluated as excess over a matched IID floor.

The controlled Poisson solution is affine in its two boundary values.  That
allows an auditable factorization of density, operator, and sampling errors
before any nonlinear or aneurysm-domain experiment is permitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .controlled_pde import (
    ControlledPDEError,
    _build_models,
    _cluster_summary,
    _distribution_metrics,
    _flatten,
    _gaussian_nll,
    _sample_gaussian,
    _summary,
    _true_boundary_distribution,
    condition_gaussian,
    generate_split,
    poisson_solution,
)
from .controlled_pde_diagnostic import (
    _nested_gaussian_samples,
    _nested_moment_residual,
    _route_index,
    _standardized_mean_error,
)


def _imports() -> tuple[Any, Any]:
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - server runtime
        raise ControlledPDEError("Controlled G1r requires numpy and torch.") from exc
    return np, torch


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_keys(payload: Mapping[str, Any], keys: Sequence[str], label: str) -> None:
    missing = sorted(set(keys) - set(payload))
    if missing:
        raise ControlledPDEError(f"{label} is missing keys: {missing}")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate the immutable prospective G1r contract."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        [
            "schema_version",
            "experiment_id",
            "status",
            "source_gate",
            "may_relabel_failed_source_gate",
            "failed_g1_config",
            "failed_g1_config_sha256",
            "failed_g1_result",
            "failed_g1_result_sha256",
            "g1b_result",
            "g1b_result_sha256",
            "seeds",
            "split_seed_offsets",
            "grid_points",
            "train_geometries",
            "validation_geometries",
            "test_geometries",
            "conditions_per_geometry",
            "hidden_dim",
            "observation_masks",
            "primary_masks",
            "density_training",
            "operator_training",
            "direct_baseline_training",
            "evaluation",
            "success_thresholds",
        ],
        "G1r config",
    )
    if payload["schema_version"] != "aurora.controlled_pde_g1r.v1":
        raise ControlledPDEError("Unexpected G1r schema version.")
    if payload["status"] != "preregistered_before_fresh_test":
        raise ControlledPDEError("G1r must remain prospectively registered.")
    if payload["source_gate"] != "G1":
        raise ControlledPDEError("G1r must remain linked to failed G1.")
    if payload["may_relabel_failed_source_gate"] is not False:
        raise ControlledPDEError("G1r cannot relabel the failed frozen G1.")

    base_path = (config_path.parent / payload["failed_g1_config"]).resolve()
    failed_path = (config_path.parent / payload["failed_g1_result"]).resolve()
    diagnostic_path = (config_path.parent / payload["g1b_result"]).resolve()
    pins = (
        (base_path, payload["failed_g1_config_sha256"], "frozen G1 config"),
        (failed_path, payload["failed_g1_result_sha256"], "failed G1 result"),
        (diagnostic_path, payload["g1b_result_sha256"], "G1b result"),
    )
    for artifact, expected, label in pins:
        if not artifact.is_file() or _sha256(artifact) != expected:
            raise ControlledPDEError(f"Pinned {label} does not match G1r.")

    failed_config = json.loads(base_path.read_text(encoding="utf-8"))
    fresh_seeds = [int(item) for item in payload["seeds"]]
    if len(fresh_seeds) != 5 or len(set(fresh_seeds)) != 5:
        raise ControlledPDEError("G1r requires five unique prospective seeds.")
    if set(fresh_seeds) & {int(item) for item in failed_config["seeds"]}:
        raise ControlledPDEError("G1r seeds must not overlap frozen G1 seeds.")
    offsets = payload["split_seed_offsets"]
    if set(offsets) != {"train", "validation", "test"}:
        raise ControlledPDEError("G1r must freeze train/validation/test seed offsets.")
    if len({int(value) for value in offsets.values()}) != 3:
        raise ControlledPDEError("G1r split seed offsets must be distinct.")
    if int(payload["validation_geometries"]) <= 0:
        raise ControlledPDEError("G1r checkpoint selection requires validation geometry.")
    if set(payload["primary_masks"]) - set(payload["observation_masks"]):
        raise ControlledPDEError("G1r primary masks must be declared.")

    training_keys = (
        "maximum_epochs",
        "learning_rate",
        "weight_decay",
        "validation_interval",
        "early_stopping_patience",
        "minimum_delta",
        "lr_plateau_patience",
        "lr_decay",
        "minimum_learning_rate",
    )
    for label in (
        "density_training",
        "operator_training",
        "direct_baseline_training",
    ):
        _require_keys(payload[label], training_keys, label)
    evaluation_keys = (
        "coverage",
        "bc_samples",
        "gauss_hermite_order",
        "projective_samples",
        "projective_geometries",
        "projective_replicates",
        "sliced_projections",
        "nested_routes",
        "bootstrap_replicates",
    )
    _require_keys(payload["evaluation"], evaluation_keys, "evaluation")
    if payload["evaluation"]["nested_routes"] != [
        "left_then_right",
        "right_then_left",
    ]:
        raise ControlledPDEError("G1r must test both nesting routes.")
    return payload


def _clone_state(module: Any) -> dict[str, Any]:
    return {key: value.detach().clone() for key, value in module.state_dict().items()}


def _paired_loss(operator: Any, split: Mapping[str, Any], first: int, second: int) -> Any:
    _, torch = _imports()
    geometry = split["geometry"]
    boundary = split["boundary"]
    field = split["field"]
    true_delta = field[:, second, :] - field[:, first, :]
    predicted_delta = operator(geometry, boundary[:, second, :]) - operator(
        geometry, boundary[:, first, :]
    )
    return torch.mean((predicted_delta - true_delta).square())


def _direct_loss(
    direct: Any,
    geometry: Any,
    boundary: Any,
    field: Any,
    mask: Any,
) -> Any:
    _, torch = _imports()
    observed = boundary * mask
    mean, scale = direct(geometry, observed, mask)
    return torch.mean(0.5 * ((field - mean) / scale).square() + torch.log(scale))


def _scheduler(optimizer: Any, contract: Mapping[str, Any]) -> Any:
    _, torch = _imports()
    return torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=float(contract["lr_decay"]),
        patience=int(contract["lr_plateau_patience"]),
        min_lr=float(contract["minimum_learning_rate"]),
    )


def _fit_stage(
    *,
    module: Any,
    optimizer: Any,
    scheduler: Any,
    contract: Mapping[str, Any],
    train_step: Any,
    validation_step: Any,
) -> dict[str, Any]:
    """Fit one module and restore the validation-selected checkpoint."""

    best_state = _clone_state(module)
    best_value = math.inf
    best_epoch = 0
    checks_without_improvement = 0
    trace = []
    interval = int(contract["validation_interval"])
    patience = int(contract["early_stopping_patience"])
    minimum_delta = float(contract["minimum_delta"])
    maximum_epochs = int(contract["maximum_epochs"])

    for epoch in range(1, maximum_epochs + 1):
        module.train()
        train_value = train_step(epoch)
        optimizer.zero_grad(set_to_none=True)
        train_value.backward()
        optimizer.step()
        if epoch % interval and epoch != maximum_epochs:
            continue

        module.eval()
        with _imports()[1].inference_mode():
            validation_value = float(validation_step().item())
        scheduler.step(validation_value)
        trace.append(
            {
                "epoch": epoch,
                "train": float(train_value.detach().item()),
                "validation": validation_value,
                "learning_rate": float(optimizer.param_groups[0]["lr"]),
            }
        )
        if validation_value < best_value - minimum_delta:
            best_value = validation_value
            best_epoch = epoch
            best_state = _clone_state(module)
            checks_without_improvement = 0
        else:
            checks_without_improvement += 1
        if checks_without_improvement >= patience:
            break

    module.load_state_dict(best_state)
    module.eval()
    return {
        "best_epoch": best_epoch,
        "best_validation_loss": best_value,
        "epochs_executed": trace[-1]["epoch"],
        "trace": trace,
    }


def train_models(
    train: Mapping[str, Any],
    validation: Mapping[str, Any],
    config: Mapping[str, Any],
    seed: int,
) -> tuple[Any, Any, Any, dict[str, Any]]:
    """Fit density, deterministic operator, and direct baseline without test access."""

    _, torch = _imports()
    torch.manual_seed(seed)
    device = train["geometry"].device
    density, operator, direct = _build_models(
        int(config["grid_points"]), int(config["hidden_dim"]), device
    )
    train_geometry, train_boundary, train_field = _flatten(train)
    val_geometry, val_boundary, val_field = _flatten(validation)

    density_contract = config["density_training"]
    density_optimizer = torch.optim.AdamW(
        density.parameters(),
        lr=float(density_contract["learning_rate"]),
        weight_decay=float(density_contract["weight_decay"]),
    )
    density_scheduler = _scheduler(density_optimizer, density_contract)

    def density_train(_: int) -> Any:
        mean, covariance = density(train_geometry)
        return torch.mean(_gaussian_nll(train_boundary, mean, covariance))

    def density_validation() -> Any:
        mean, covariance = density(val_geometry)
        return torch.mean(_gaussian_nll(val_boundary, mean, covariance))

    density_history = _fit_stage(
        module=density,
        optimizer=density_optimizer,
        scheduler=density_scheduler,
        contract=density_contract,
        train_step=density_train,
        validation_step=density_validation,
    )

    operator_contract = config["operator_training"]
    operator_optimizer = torch.optim.AdamW(
        operator.parameters(),
        lr=float(operator_contract["learning_rate"]),
        weight_decay=float(operator_contract["weight_decay"]),
    )
    operator_scheduler = _scheduler(operator_optimizer, operator_contract)
    pair_weight = float(operator_contract["paired_response_weight"])
    condition_count = int(config["conditions_per_geometry"])

    def operator_train(epoch: int) -> Any:
        prediction = operator(train_geometry, train_boundary)
        field_loss = torch.mean((prediction - train_field).square())
        first = (epoch - 1) % condition_count
        second = epoch % condition_count
        return field_loss + pair_weight * _paired_loss(
            operator, train, first, second
        )

    def operator_validation() -> Any:
        prediction = operator(val_geometry, val_boundary)
        field_loss = torch.mean((prediction - val_field).square())
        return field_loss + pair_weight * _paired_loss(operator, validation, 0, 1)

    operator_history = _fit_stage(
        module=operator,
        optimizer=operator_optimizer,
        scheduler=operator_scheduler,
        contract=operator_contract,
        train_step=operator_train,
        validation_step=operator_validation,
    )

    direct_contract = config["direct_baseline_training"]
    direct_optimizer = torch.optim.AdamW(
        direct.parameters(),
        lr=float(direct_contract["learning_rate"]),
        weight_decay=float(direct_contract["weight_decay"]),
    )
    direct_scheduler = _scheduler(direct_optimizer, direct_contract)
    mask_values = torch.tensor(
        list(config["observation_masks"].values()),
        device=device,
        dtype=train_geometry.dtype,
    )

    def direct_train(epoch: int) -> Any:
        generator = torch.Generator(device=device).manual_seed(seed + epoch)
        chosen = torch.randint(
            0,
            mask_values.shape[0],
            (train_geometry.shape[0],),
            device=device,
            generator=generator,
        )
        mask = mask_values[chosen]
        return _direct_loss(
            direct, train_geometry, train_boundary, train_field, mask
        )

    def direct_validation() -> Any:
        losses = []
        for value in mask_values:
            mask = value.expand(val_geometry.shape[0], -1)
            losses.append(
                _direct_loss(direct, val_geometry, val_boundary, val_field, mask)
            )
        return torch.stack(losses).mean()

    direct_history = _fit_stage(
        module=direct,
        optimizer=direct_optimizer,
        scheduler=direct_scheduler,
        contract=direct_contract,
        train_step=direct_train,
        validation_step=direct_validation,
    )
    return density, operator, direct, {
        "density": density_history,
        "operator": operator_history,
        "direct_mask_gaussian": direct_history,
        "test_access_during_selection": False,
    }


def analytic_field_moments(
    geometry: Any,
    boundary_mean: Any,
    boundary_covariance: Any,
    grid: Any,
) -> tuple[Any, Any]:
    """Push Gaussian boundary moments through the exact affine Poisson map."""

    _, torch = _imports()
    field_mean = poisson_solution(geometry, boundary_mean, grid)
    weights = torch.stack((1.0 - grid, grid), dim=-1)
    field_variance = torch.einsum(
        "xi,bij,xj->bx", weights, boundary_covariance, weights
    ).clamp_min(0.0)
    return field_mean, field_variance


def _analytic_density_metrics(
    geometry: Any,
    boundary: Any,
    target: Any,
    grid: Any,
    learned_mean: Any,
    learned_covariance: Any,
    mask: Sequence[int],
    *,
    coverage: float,
    conditions_per_geometry: int,
    bootstrap_replicates: int,
    seed: int,
) -> dict[str, Any]:
    _, torch = _imports()
    true_mean, true_covariance = _true_boundary_distribution(geometry)
    true_conditional_mean, _ = condition_gaussian(
        true_mean, true_covariance, boundary, mask
    )
    learned_conditional_mean, learned_conditional_covariance = condition_gaussian(
        learned_mean, learned_covariance, boundary, mask
    )
    oracle_field_mean = poisson_solution(geometry, true_conditional_mean, grid)
    field_mean, field_variance = analytic_field_moments(
        geometry,
        learned_conditional_mean,
        learned_conditional_covariance,
        grid,
    )
    mean_error = _standardized_mean_error(
        field_mean,
        oracle_field_mean,
        conditions_per_geometry=conditions_per_geometry,
    )
    normal = torch.distributions.Normal(
        torch.tensor(0.0, device=geometry.device),
        torch.tensor(1.0, device=geometry.device),
    )
    alpha = (1.0 - coverage) / 2.0
    critical = normal.icdf(torch.tensor(1.0 - alpha, device=geometry.device))
    half_width = critical * torch.sqrt(field_variance)
    lower, upper = field_mean - half_width, field_mean + half_width
    geometries = target.shape[0] // conditions_per_geometry
    geometry_coverage = (
        ((target >= lower) & (target <= upper))
        .float()
        .reshape(geometries, conditions_per_geometry, -1)
        .mean(dim=(1, 2))
    )
    coverage_summary = _cluster_summary(
        geometry_coverage,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed,
    )
    return {
        "standardized_mean_error": mean_error,
        "empirical_coverage": coverage_summary["mean"],
        "coverage_error": abs(coverage_summary["mean"] - coverage),
        "coverage_geometry_bootstrap_ci95": [
            coverage_summary["ci95_low"],
            coverage_summary["ci95_high"],
        ],
    }


def gauss_hermite_operator_mean(
    operator: Any,
    geometry: Any,
    boundary_mean: Any,
    boundary_covariance: Any,
    *,
    order: int,
    chunk: int = 262144,
) -> Any:
    """Deterministically integrate a learned operator under a 2-D Gaussian."""

    np, torch = _imports()
    nodes_np, weights_np = np.polynomial.hermite.hermgauss(order)
    first, second = np.meshgrid(nodes_np, nodes_np, indexing="ij")
    points = np.stack((first.reshape(-1), second.reshape(-1)), axis=-1)
    weights = np.outer(weights_np, weights_np).reshape(-1) / math.pi
    points_tensor = torch.as_tensor(
        points, device=geometry.device, dtype=geometry.dtype
    )
    weights_tensor = torch.as_tensor(
        weights, device=geometry.device, dtype=geometry.dtype
    )
    eye = torch.eye(2, device=geometry.device, dtype=geometry.dtype)
    cholesky = torch.linalg.cholesky(
        boundary_covariance + 1e-8 * eye
    )
    samples = boundary_mean[:, None, :] + math.sqrt(2.0) * torch.einsum(
        "bij,qj->bqi", cholesky, points_tensor
    )
    expanded = geometry[:, None, :].expand(-1, samples.shape[1], -1)
    flat_geometry = expanded.reshape(-1, 2)
    flat_boundary = samples.reshape(-1, 2)
    predictions = []
    for start in range(0, flat_boundary.shape[0], chunk):
        stop = min(start + chunk, flat_boundary.shape[0])
        predictions.append(operator(flat_geometry[start:stop], flat_boundary[start:stop]))
    stacked = torch.cat(predictions, dim=0).reshape(
        geometry.shape[0], samples.shape[1], -1
    )
    return torch.sum(stacked * weights_tensor[None, :, None], dim=1)


def _sampled_model_metrics(
    model: Any,
    geometry: Any,
    boundary: Any,
    target: Any,
    grid: Any,
    density_mean: Any,
    density_covariance: Any,
    mask: Sequence[int],
    *,
    samples: int,
    coverage: float,
    conditions_per_geometry: int,
    bootstrap_replicates: int,
    seed: int,
    direct: bool,
) -> dict[str, Any]:
    _, torch = _imports()
    generator = torch.Generator(device=geometry.device).manual_seed(seed)
    oracle_mean, oracle_covariance = _true_boundary_distribution(geometry)
    oracle_conditional_mean, _ = condition_gaussian(
        oracle_mean, oracle_covariance, boundary, mask
    )
    oracle_field_mean = poisson_solution(geometry, oracle_conditional_mean, grid)
    if direct:
        mask_tensor = torch.tensor(
            mask, device=geometry.device, dtype=geometry.dtype
        ).expand(geometry.shape[0], -1)
        mean, scale = model(geometry, boundary * mask_tensor, mask_tensor)
        field_samples = mean[:, None, :] + scale[:, None, :] * torch.randn(
            geometry.shape[0],
            samples,
            target.shape[-1],
            device=geometry.device,
            generator=generator,
        )
    else:
        conditional_mean, conditional_covariance = condition_gaussian(
            density_mean, density_covariance, boundary, mask
        )
        boundary_samples = _sample_gaussian(
            conditional_mean, conditional_covariance, samples, generator
        )
        batch, count, _ = boundary_samples.shape
        expanded = geometry[:, None, :].expand(-1, count, -1)
        field_samples = model(
            expanded.reshape(-1, 2), boundary_samples.reshape(-1, 2)
        ).reshape(batch, count, -1)
    return _distribution_metrics(
        field_samples,
        target,
        oracle_field_mean,
        coverage,
        conditions_per_geometry=conditions_per_geometry,
        bootstrap_replicates=bootstrap_replicates,
        seed=seed + 1,
    )


def _sliced_distance(
    first: Any, second: Any, *, seed: int, projections: int
) -> float:
    _, torch = _imports()
    generator = torch.Generator(device=first.device).manual_seed(seed)
    directions = torch.randn(
        projections, first.shape[-1], device=first.device, generator=generator
    )
    directions = directions / torch.linalg.vector_norm(
        directions, dim=-1, keepdim=True
    ).clamp_min(1e-8)
    first_projection = torch.einsum("bkn,pn->bkp", first, directions)
    second_projection = torch.einsum("bkn,pn->bkp", second, directions)
    first_sorted = torch.sort(first_projection, dim=1).values
    second_sorted = torch.sort(second_projection, dim=1).values
    numerator = torch.mean(torch.abs(first_sorted - second_sorted))
    denominator = torch.std(
        torch.cat((first_projection, second_projection), dim=1)
    ).clamp_min(1e-6)
    return float((numerator / denominator).item())


def _projective_metrics(
    density: Any,
    operator: Any,
    geometry: Any,
    evaluation: Mapping[str, Any],
    seed: int,
) -> tuple[dict[str, Any], float]:
    """Measure direct-vs-nested discrepancy relative to its matched IID floor."""

    _, torch = _imports()
    count = int(evaluation["projective_samples"])
    replicates = int(evaluation["projective_replicates"])
    projections = int(evaluation["sliced_projections"])
    mean, covariance = density(geometry)
    routes: dict[str, Any] = {}
    maximum_residual = 0.0
    for route_offset, route in enumerate(evaluation["nested_routes"]):
        first_index = _route_index(route)
        residual = _nested_moment_residual(
            mean, covariance, first_index=first_index
        )
        maximum_residual = max(
            maximum_residual,
            float(residual["maximum_covariance_absolute_residual"]),
        )
        values = {"iid_floor": [], "direct_vs_nested": [], "signed_excess": []}
        for replicate in range(replicates):
            base_seed = seed * 1000 + route_offset * 100 + replicate * 10
            generator_a = torch.Generator(device=geometry.device).manual_seed(
                base_seed + 1
            )
            generator_b = torch.Generator(device=geometry.device).manual_seed(
                base_seed + 2
            )
            generator_nested = torch.Generator(
                device=geometry.device
            ).manual_seed(base_seed + 3)
            boundary_a = _sample_gaussian(mean, covariance, count, generator_a)
            boundary_b = _sample_gaussian(mean, covariance, count, generator_b)
            boundary_nested = _nested_gaussian_samples(
                mean,
                covariance,
                count,
                generator_nested,
                first_index=first_index,
            )
            batch = geometry.shape[0]
            expanded = geometry[:, None, :].expand(-1, count, -1)

            def fields(boundary_samples: Any) -> Any:
                return operator(
                    expanded.reshape(-1, 2), boundary_samples.reshape(-1, 2)
                ).reshape(batch, count, -1)

            field_a = fields(boundary_a)
            field_b = fields(boundary_b)
            field_nested = fields(boundary_nested)
            projection_seed = base_seed + 7
            iid = _sliced_distance(
                field_a,
                field_b,
                seed=projection_seed,
                projections=projections,
            )
            nested = _sliced_distance(
                field_a,
                field_nested,
                seed=projection_seed,
                projections=projections,
            )
            values["iid_floor"].append(iid)
            values["direct_vs_nested"].append(nested)
            values["signed_excess"].append(nested - iid)
        routes[route] = values
    return routes, maximum_residual


def evaluate_seed(
    density: Any,
    operator: Any,
    direct: Any,
    test: Mapping[str, Any],
    config: Mapping[str, Any],
    seed: int,
) -> dict[str, Any]:
    """Evaluate a test split that was not generated during checkpoint selection."""

    _, torch = _imports()
    density.eval()
    operator.eval()
    direct.eval()
    geometry, boundary, target = _flatten(test)
    conditions = int(config["conditions_per_geometry"])
    evaluation = config["evaluation"]
    coverage = float(evaluation["coverage"])
    bootstrap = int(evaluation["bootstrap_replicates"])
    sample_count = int(evaluation["bc_samples"])

    with torch.inference_mode():
        learned_mean, learned_covariance = density(geometry)
        full_prediction = operator(geometry, boundary)
        full_operator = _standardized_mean_error(
            full_prediction,
            target,
            conditions_per_geometry=conditions,
        )
        masks: dict[str, Any] = {}
        for offset, name in enumerate(config["primary_masks"]):
            mask = config["observation_masks"][name]
            density_metrics = _analytic_density_metrics(
                geometry,
                boundary,
                target,
                test["grid"],
                learned_mean,
                learned_covariance,
                mask,
                coverage=coverage,
                conditions_per_geometry=conditions,
                bootstrap_replicates=bootstrap,
                seed=seed + 100 * offset,
            )
            conditional_mean, conditional_covariance = condition_gaussian(
                learned_mean, learned_covariance, boundary, mask
            )
            quadrature_mean = gauss_hermite_operator_mean(
                operator,
                geometry,
                conditional_mean,
                conditional_covariance,
                order=int(evaluation["gauss_hermite_order"]),
            )
            true_mean, true_covariance = _true_boundary_distribution(geometry)
            true_conditional_mean, _ = condition_gaussian(
                true_mean, true_covariance, boundary, mask
            )
            oracle_field_mean = poisson_solution(
                geometry, true_conditional_mean, test["grid"]
            )
            quadrature_error = _standardized_mean_error(
                quadrature_mean,
                oracle_field_mean,
                conditions_per_geometry=conditions,
            )
            aurora_samples = _sampled_model_metrics(
                operator,
                geometry,
                boundary,
                target,
                test["grid"],
                learned_mean,
                learned_covariance,
                mask,
                samples=sample_count,
                coverage=coverage,
                conditions_per_geometry=conditions,
                bootstrap_replicates=bootstrap,
                seed=seed + 1000 * (offset + 1),
                direct=False,
            )
            direct_samples = _sampled_model_metrics(
                direct,
                geometry,
                boundary,
                target,
                test["grid"],
                learned_mean,
                learned_covariance,
                mask,
                samples=sample_count,
                coverage=coverage,
                conditions_per_geometry=conditions,
                bootstrap_replicates=bootstrap,
                seed=seed + 2000 * (offset + 1),
                direct=True,
            )
            masks[name] = {
                "density_only_analytic": density_metrics,
                "end_to_end_quadrature_mean_error": quadrature_error,
                "aurora_sampled": aurora_samples,
                "direct_mask_gaussian_sampled": direct_samples,
            }

        projective_geometry = test["geometry"][
            : int(evaluation["projective_geometries"])
        ]
        projective, analytic_residual = _projective_metrics(
            density, operator, projective_geometry, evaluation, seed
        )

    gate_metrics = {
        "maximum_density_only_standardized_mean_error": max(
            masks[name]["density_only_analytic"]["standardized_mean_error"]
            for name in config["primary_masks"]
        ),
        "maximum_density_only_coverage_error": max(
            masks[name]["density_only_analytic"]["coverage_error"]
            for name in config["primary_masks"]
        ),
        "maximum_end_to_end_quadrature_mean_error": max(
            masks[name]["end_to_end_quadrature_mean_error"]["mean"]
            for name in config["primary_masks"]
        ),
        "maximum_end_to_end_sampled_coverage_error": max(
            masks[name]["aurora_sampled"]["coverage_error"]
            for name in config["primary_masks"]
        ),
        "maximum_full_bc_operator_error": float(full_operator["mean"]),
        "maximum_analytic_nested_moment_residual": analytic_residual,
    }
    return {
        "seed": seed,
        "split_seeds": {
            name: seed + int(offset)
            for name, offset in config["split_seed_offsets"].items()
        },
        "masks": masks,
        "full_bc_operator": full_operator,
        "projective": projective,
        "gate_metrics": gate_metrics,
    }


def _bootstrap_mean_ci(
    values: Sequence[float], *, replicates: int, seed: int
) -> dict[str, float]:
    np, _ = _imports()
    array = np.asarray(values, dtype=np.float64)
    generator = np.random.default_rng(seed)
    indices = generator.integers(0, len(array), size=(replicates, len(array)))
    means = np.mean(array[indices], axis=1)
    return {
        "mean": float(np.mean(array)),
        "ci95_low": float(np.quantile(means, 0.025)),
        "ci95_high": float(np.quantile(means, 0.975)),
    }


def _aggregate(
    seed_results: Sequence[Mapping[str, Any]], config: Mapping[str, Any]
) -> dict[str, Any]:
    evaluation = config["evaluation"]
    gate_keys = (
        "maximum_density_only_standardized_mean_error",
        "maximum_density_only_coverage_error",
        "maximum_end_to_end_quadrature_mean_error",
        "maximum_end_to_end_sampled_coverage_error",
        "maximum_full_bc_operator_error",
        "maximum_analytic_nested_moment_residual",
    )
    aggregate_metrics = {
        key: _summary(
            [float(result["gate_metrics"][key]) for result in seed_results]
        )
        for key in gate_keys
    }
    projective_routes: dict[str, Any] = {}
    upper_bounds = []
    for route_offset, route in enumerate(evaluation["nested_routes"]):
        seed_means = [
            sum(float(value) for value in result["projective"][route]["signed_excess"])
            / len(result["projective"][route]["signed_excess"])
            for result in seed_results
        ]
        summary = _bootstrap_mean_ci(
            seed_means,
            replicates=int(evaluation["bootstrap_replicates"]),
            seed=int(config["seeds"][0]) + route_offset,
        )
        projective_routes[route] = {
            "seed_mean_signed_excess": seed_means,
            "across_seed_mean_ci95": summary,
            "iid_floor": _summary(
                [
                    float(value)
                    for result in seed_results
                    for value in result["projective"][route]["iid_floor"]
                ]
            ),
            "direct_vs_nested": _summary(
                [
                    float(value)
                    for result in seed_results
                    for value in result["projective"][route]["direct_vs_nested"]
                ]
            ),
        }
        upper_bounds.append(summary["ci95_high"])
    aggregate_metrics["maximum_projective_excess_ci95_upper"] = {
        "mean": max(
            projective_routes[route]["across_seed_mean_ci95"]["mean"]
            for route in evaluation["nested_routes"]
        ),
        "std": 0.0,
        "min": min(upper_bounds),
        "max": max(upper_bounds),
    }
    thresholds = config["success_thresholds"]
    checks = {
        key: aggregate_metrics[key]["max"] <= float(thresholds[key])
        for key in thresholds
    }
    return {
        "gate_metrics": aggregate_metrics,
        "projective_routes": projective_routes,
        "gate": {"passed": all(checks.values()), "checks": checks},
    }


def run_experiment(config: Mapping[str, Any], require_cuda: bool) -> dict[str, Any]:
    """Train on train/validation, then generate and evaluate the frozen fresh test."""

    _, torch = _imports()
    if require_cuda and not torch.cuda.is_available():
        raise ControlledPDEError("CUDA was required but is unavailable.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed_results = []
    histories = []
    offsets = config["split_seed_offsets"]
    for seed in [int(item) for item in config["seeds"]]:
        random.seed(seed)
        torch.manual_seed(seed)
        train = generate_split(
            geometries=int(config["train_geometries"]),
            conditions=int(config["conditions_per_geometry"]),
            grid_points=int(config["grid_points"]),
            seed=seed + int(offsets["train"]),
            device=device,
        )
        validation = generate_split(
            geometries=int(config["validation_geometries"]),
            conditions=int(config["conditions_per_geometry"]),
            grid_points=int(config["grid_points"]),
            seed=seed + int(offsets["validation"]),
            device=device,
        )
        density, operator, direct, history = train_models(
            train, validation, config, seed
        )
        histories.append({"seed": seed, **history})
        del train, validation

        test = generate_split(
            geometries=int(config["test_geometries"]),
            conditions=int(config["conditions_per_geometry"]),
            grid_points=int(config["grid_points"]),
            seed=seed + int(offsets["test"]),
            device=device,
        )
        result = evaluate_seed(density, operator, direct, test, config, seed)
        seed_results.append(result)
        del density, operator, direct, test
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    aggregate = _aggregate(seed_results, config)
    return {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "source_gate": config["source_gate"],
        "failed_g1_relabeled": False,
        "device": str(device),
        "training": histories,
        "seeds": seed_results,
        "aggregate": aggregate,
        "interpretation": config["interpretation"],
    }


def _environment(torch: Any) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(item) for item in sys.argv) + "\n", encoding="utf-8"
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "config.sha256").write_text(
        _sha256(args.config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "run_config.json", config)
    try:
        result = run_experiment(config, args.require_cuda)
        _, torch = _imports()
        result.update(
            {
                "git_commit": args.git_commit,
                "started_at_utc": started,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "environment": _environment(torch),
            }
        )
        _write_json(args.output / "metrics.json", result)
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "gate_passed": result["aggregate"]["gate"]["passed"],
                "failed_g1_relabeled": False,
            },
        )
        return 0
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "error_type": type(exc).__name__,
                "message": str(exc),
                "started_at_utc": started,
                "failed_at_utc": datetime.now(timezone.utc).isoformat(),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
