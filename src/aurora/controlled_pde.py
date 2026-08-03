"""Exact partial-boundary benchmark for AURORA's G1 coherence gate.

The benchmark solves a one-dimensional Poisson family with correlated random
Dirichlet boundary values.  Its conditional solution distribution is available
in closed form, so coverage and observation-mask coherence can be tested
without treating a numerical solver as ground truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


class ControlledPDEError(RuntimeError):
    """Raised when the preregistered controlled experiment cannot be honored."""


def _imports() -> tuple[Any, Any]:
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - server runtime
        raise ControlledPDEError("Controlled G1 requires numpy and torch.") from exc
    return np, torch


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "experiment_id",
        "seeds",
        "grid_points",
        "train_geometries",
        "validation_geometries",
        "test_geometries",
        "conditions_per_geometry",
        "train_epochs",
        "learning_rate",
        "hidden_dim",
        "bc_samples_eval",
        "coverage",
        "observation_masks",
        "primary_masks",
        "success_thresholds",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ControlledPDEError(f"Config is missing: {missing}")
    if set(payload["primary_masks"]) - set(payload["observation_masks"]):
        raise ControlledPDEError("primary_masks must be declared observation masks.")
    return payload


def _true_boundary_distribution(geometry: Any) -> tuple[Any, Any]:
    """Return geometry-conditioned mean/covariance for two Dirichlet values."""

    _, torch = _imports()
    g0, g1 = geometry[:, 0], geometry[:, 1]
    mean = torch.stack(
        (0.30 * g0 + 0.20 * torch.sin(g1), -0.20 * g0 + 0.25 * torch.cos(g1)),
        dim=-1,
    )
    std0 = 0.24 + 0.05 * torch.sigmoid(g0)
    std1 = 0.20 + 0.05 * torch.sigmoid(g1)
    correlation = 0.35 + 0.10 * torch.tanh(0.5 * (g0 - g1))
    covariance = torch.zeros(
        geometry.shape[0], 2, 2, device=geometry.device, dtype=geometry.dtype
    )
    covariance[:, 0, 0] = std0.square()
    covariance[:, 1, 1] = std1.square()
    covariance[:, 0, 1] = correlation * std0 * std1
    covariance[:, 1, 0] = covariance[:, 0, 1]
    return mean, covariance


def poisson_solution(geometry: Any, boundary: Any, grid: Any) -> Any:
    """Evaluate the exact solution of ``-u''=g0+g1 sin(pi x)``."""

    _, torch = _imports()
    g0 = geometry[..., 0:1]
    g1 = geometry[..., 1:2]
    left = boundary[..., 0:1]
    right = boundary[..., 1:2]
    return (
        left * (1.0 - grid)
        + right * grid
        + 0.5 * g0 * grid * (1.0 - grid)
        + g1 * torch.sin(math.pi * grid) / (math.pi**2)
    )


def generate_split(
    *, geometries: int, conditions: int, grid_points: int, seed: int, device: Any
) -> dict[str, Any]:
    """Generate geometry families and paired boundary-condition simulations."""

    _, torch = _imports()
    generator = torch.Generator(device="cpu").manual_seed(seed)
    geometry = 2.0 * torch.rand(geometries, 2, generator=generator) - 1.0
    mean, covariance = _true_boundary_distribution(geometry)
    standard = torch.randn(geometries, conditions, 2, generator=generator)
    cholesky = torch.linalg.cholesky(covariance)
    boundary = mean[:, None, :] + torch.einsum(
        "gij,gcj->gci", cholesky, standard
    )
    grid = torch.linspace(0.0, 1.0, grid_points)
    field = poisson_solution(
        geometry[:, None, :], boundary, grid.view(1, 1, -1)
    )
    return {
        "geometry": geometry.to(device),
        "boundary": boundary.to(device),
        "field": field.to(device),
        "grid": grid.to(device),
    }


def _build_models(grid_points: int, hidden_dim: int, device: Any) -> tuple[Any, Any, Any]:
    _, torch = _imports()

    class BoundaryDensity(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = torch.nn.Sequential(
                torch.nn.Linear(2, hidden_dim),
                torch.nn.SiLU(),
                torch.nn.Linear(hidden_dim, hidden_dim),
                torch.nn.SiLU(),
                torch.nn.Linear(hidden_dim, 5),
            )

        def forward(self, geometry: Any) -> tuple[Any, Any]:
            raw = self.net(geometry)
            mean = raw[:, :2]
            std = torch.nn.functional.softplus(raw[:, 2:4]) + 1e-3
            correlation = 0.95 * torch.tanh(raw[:, 4])
            covariance = torch.zeros(
                geometry.shape[0], 2, 2, device=geometry.device
            )
            covariance[:, 0, 0] = std[:, 0].square()
            covariance[:, 1, 1] = std[:, 1].square()
            covariance[:, 0, 1] = correlation * std[:, 0] * std[:, 1]
            covariance[:, 1, 0] = covariance[:, 0, 1]
            return mean, covariance

    class SolutionOperator(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = torch.nn.Sequential(
                torch.nn.Linear(4, hidden_dim),
                torch.nn.SiLU(),
                torch.nn.Linear(hidden_dim, hidden_dim),
                torch.nn.SiLU(),
                torch.nn.Linear(hidden_dim, grid_points),
            )

        def forward(self, geometry: Any, boundary: Any) -> Any:
            return self.net(torch.cat((geometry, boundary), dim=-1))

    class DirectMaskOperator(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = torch.nn.Sequential(
                torch.nn.Linear(6, hidden_dim),
                torch.nn.SiLU(),
                torch.nn.Linear(hidden_dim, hidden_dim),
                torch.nn.SiLU(),
                torch.nn.Linear(hidden_dim, 2 * grid_points),
            )

        def forward(self, geometry: Any, observed: Any, mask: Any) -> tuple[Any, Any]:
            raw = self.net(torch.cat((geometry, observed, mask), dim=-1))
            mean, raw_scale = raw.chunk(2, dim=-1)
            scale = torch.nn.functional.softplus(raw_scale) + 2e-3
            return mean, scale

    return (
        BoundaryDensity().to(device),
        SolutionOperator().to(device),
        DirectMaskOperator().to(device),
    )


def _gaussian_nll(value: Any, mean: Any, covariance: Any) -> Any:
    _, torch = _imports()
    cholesky = torch.linalg.cholesky(
        covariance + 1e-5 * torch.eye(2, device=value.device)
    )
    residual = (value - mean).unsqueeze(-1)
    solved = torch.cholesky_solve(residual, cholesky)
    mahalanobis = torch.matmul(residual.transpose(-2, -1), solved).flatten()
    logdet = 2.0 * torch.log(torch.diagonal(cholesky, dim1=-2, dim2=-1)).sum(-1)
    return 0.5 * (mahalanobis + logdet + 2.0 * math.log(2.0 * math.pi))


def _flatten(split: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    geometry = split["geometry"]
    boundary = split["boundary"]
    field = split["field"]
    conditions = boundary.shape[1]
    expanded = geometry[:, None, :].expand(-1, conditions, -1)
    return (
        expanded.reshape(-1, 2),
        boundary.reshape(-1, 2),
        field.reshape(-1, field.shape[-1]),
    )


def train_models(
    split: Mapping[str, Any], config: Mapping[str, Any], seed: int
) -> tuple[Any, Any, Any, dict[str, float]]:
    """Fit the coherent construction and a direct masked Gaussian baseline."""

    _, torch = _imports()
    torch.manual_seed(seed)
    device = split["geometry"].device
    density, operator, direct = _build_models(
        int(config["grid_points"]), int(config["hidden_dim"]), device
    )
    coherent_optimizer = torch.optim.Adam(
        [*density.parameters(), *operator.parameters()],
        lr=float(config["learning_rate"]),
    )
    direct_optimizer = torch.optim.Adam(
        direct.parameters(), lr=float(config["learning_rate"])
    )
    geometry, boundary, field = _flatten(split)
    family_geometry = split["geometry"]
    family_boundary = split["boundary"]
    family_field = split["field"]
    mask_values = torch.tensor(
        list(config["observation_masks"].values()),
        device=device,
        dtype=geometry.dtype,
    )
    epochs = int(config["train_epochs"])

    for _ in range(epochs):
        density.train()
        operator.train()
        mean, covariance = density(geometry)
        prediction = operator(geometry, boundary)
        field_loss = torch.mean((prediction - field).square())
        boundary_loss = torch.mean(_gaussian_nll(boundary, mean, covariance))

        order = torch.randperm(family_boundary.shape[1], device=device)
        first = family_boundary[:, order[0], :]
        second = family_boundary[:, order[1], :]
        true_delta = family_field[:, order[1], :] - family_field[:, order[0], :]
        predicted_delta = operator(family_geometry, second) - operator(
            family_geometry, first
        )
        pair_loss = torch.mean((predicted_delta - true_delta).square())
        coherent_loss = field_loss + 0.5 * pair_loss + 0.1 * boundary_loss
        coherent_optimizer.zero_grad(set_to_none=True)
        coherent_loss.backward()
        coherent_optimizer.step()

        direct.train()
        chosen = torch.randint(
            0, mask_values.shape[0], (geometry.shape[0],), device=device
        )
        mask = mask_values[chosen]
        observed = boundary * mask
        direct_mean, direct_scale = direct(geometry, observed, mask)
        direct_loss = torch.mean(
            0.5 * ((field - direct_mean) / direct_scale).square()
            + torch.log(direct_scale)
        )
        direct_optimizer.zero_grad(set_to_none=True)
        direct_loss.backward()
        direct_optimizer.step()

    return density, operator, direct, {
        "coherent_train_loss": float(coherent_loss.detach().item()),
        "direct_train_loss": float(direct_loss.detach().item()),
    }


def condition_gaussian(
    mean: Any, covariance: Any, value: Any, mask: Sequence[int]
) -> tuple[Any, Any]:
    """Analytically condition batched two-dimensional Gaussians."""

    _, torch = _imports()
    mask_tuple = tuple(int(item) for item in mask)
    if mask_tuple == (0, 0):
        return mean, covariance
    if mask_tuple == (1, 1):
        tiny = 1e-8 * torch.eye(2, device=mean.device).expand(mean.shape[0], -1, -1)
        return value, tiny

    observed = 0 if mask_tuple == (1, 0) else 1
    missing = 1 - observed
    result_mean = mean.clone()
    result_covariance = torch.zeros_like(covariance)
    variance_observed = covariance[:, observed, observed].clamp_min(1e-8)
    gain = covariance[:, missing, observed] / variance_observed
    result_mean[:, observed] = value[:, observed]
    result_mean[:, missing] = mean[:, missing] + gain * (
        value[:, observed] - mean[:, observed]
    )
    result_covariance[:, missing, missing] = (
        covariance[:, missing, missing]
        - covariance[:, missing, observed].square() / variance_observed
    ).clamp_min(1e-8)
    result_covariance[:, observed, observed] = 1e-8
    return result_mean, result_covariance


def _sample_gaussian(mean: Any, covariance: Any, samples: int, generator: Any) -> Any:
    _, torch = _imports()
    eye = torch.eye(2, device=mean.device)
    cholesky = torch.linalg.cholesky(covariance + 1e-7 * eye)
    standard = torch.randn(
        mean.shape[0], samples, 2, device=mean.device, generator=generator
    )
    return mean[:, None, :] + torch.einsum("bij,bkj->bki", cholesky, standard)


def _field_samples(operator: Any, geometry: Any, boundary_samples: Any) -> Any:
    batch, samples, _ = boundary_samples.shape
    expanded = geometry[:, None, :].expand(-1, samples, -1)
    prediction = operator(
        expanded.reshape(-1, 2), boundary_samples.reshape(-1, 2)
    )
    return prediction.reshape(batch, samples, -1)


def _oracle_field_mean(
    geometry: Any, boundary_value: Any, mask: Sequence[int], grid: Any
) -> Any:
    mean, covariance = _true_boundary_distribution(geometry)
    conditional_mean, _ = condition_gaussian(mean, covariance, boundary_value, mask)
    return poisson_solution(geometry, conditional_mean, grid)


def _cluster_summary(
    values: Any, *, bootstrap_replicates: int, seed: int
) -> dict[str, float]:
    np, _ = _imports()
    array = values.detach().cpu().numpy().astype(np.float64, copy=False)
    generator = np.random.default_rng(seed)
    indices = generator.integers(
        0, array.size, size=(bootstrap_replicates, array.size)
    )
    bootstrap = np.mean(array[indices], axis=1)
    return {
        "mean": float(np.mean(array)),
        "ci95_low": float(np.quantile(bootstrap, 0.025)),
        "ci95_high": float(np.quantile(bootstrap, 0.975)),
    }


def _distribution_metrics(
    samples: Any,
    target: Any,
    oracle_mean: Any,
    coverage: float,
    *,
    conditions_per_geometry: int,
    bootstrap_replicates: int,
    seed: int,
) -> dict[str, Any]:
    _, torch = _imports()
    if target.shape[0] % conditions_per_geometry:
        raise ControlledPDEError("Evaluation rows do not form complete geometry families.")
    geometries = target.shape[0] // conditions_per_geometry
    predicted_mean = samples.mean(dim=1)
    squared_mean_error = (predicted_mean - oracle_mean).square().reshape(
        geometries, conditions_per_geometry, -1
    )
    squared_oracle = oracle_mean.square().reshape(
        geometries, conditions_per_geometry, -1
    )
    geometry_mean_error = torch.sqrt(
        torch.mean(squared_mean_error, dim=(1, 2))
    ) / torch.sqrt(torch.mean(squared_oracle, dim=(1, 2))).clamp_min(1e-6)
    alpha = (1.0 - coverage) / 2.0
    lower = torch.quantile(samples, alpha, dim=1)
    upper = torch.quantile(samples, 1.0 - alpha, dim=1)
    geometry_coverage = (
        ((target >= lower) & (target <= upper))
        .float()
        .reshape(geometries, conditions_per_geometry, -1)
        .mean(dim=(1, 2))
    )
    distance_to_target = torch.linalg.vector_norm(
        samples - target[:, None, :], dim=-1
    ).mean(dim=1)
    paired = torch.roll(samples, shifts=1, dims=1)
    sample_spread = torch.linalg.vector_norm(samples - paired, dim=-1).mean(dim=1)
    geometry_energy = (distance_to_target - 0.5 * sample_spread).reshape(
        geometries, conditions_per_geometry
    ).mean(dim=1)
    geometry_width = (upper - lower).reshape(
        geometries, conditions_per_geometry, -1
    ).mean(dim=(1, 2))
    summaries = {
        "standardized_mean_error": _cluster_summary(
            geometry_mean_error,
            bootstrap_replicates=bootstrap_replicates,
            seed=seed,
        ),
        "empirical_coverage": _cluster_summary(
            geometry_coverage,
            bootstrap_replicates=bootstrap_replicates,
            seed=seed + 1,
        ),
        "energy_score": _cluster_summary(
            geometry_energy,
            bootstrap_replicates=bootstrap_replicates,
            seed=seed + 2,
        ),
        "mean_interval_width": _cluster_summary(
            geometry_width,
            bootstrap_replicates=bootstrap_replicates,
            seed=seed + 3,
        ),
    }
    empirical_coverage = summaries["empirical_coverage"]["mean"]
    return {
        "standardized_mean_error": summaries["standardized_mean_error"]["mean"],
        "empirical_coverage": empirical_coverage,
        "coverage_error": float(abs(empirical_coverage - coverage)),
        "energy_score": summaries["energy_score"]["mean"],
        "mean_interval_width": summaries["mean_interval_width"]["mean"],
        "geometry_bootstrap_ci95": {
            name: [summary["ci95_low"], summary["ci95_high"]]
            for name, summary in summaries.items()
        },
    }


def _sliced_distance(first: Any, second: Any, seed: int, projections: int = 16) -> float:
    """Normalized sliced Wasserstein-1 distance for function samples."""

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


def evaluate_seed(
    density: Any,
    operator: Any,
    direct: Any,
    split: Mapping[str, Any],
    config: Mapping[str, Any],
    seed: int,
) -> dict[str, Any]:
    _, torch = _imports()
    density.eval()
    operator.eval()
    direct.eval()
    geometry, boundary, target = _flatten(split)
    samples = int(config["bc_samples_eval"])
    coverage = float(config["coverage"])
    conditions = int(config["conditions_per_geometry"])
    bootstrap_replicates = int(config["bootstrap_replicates"])
    generator = torch.Generator(device=geometry.device).manual_seed(seed + 91)
    masks_result: dict[str, Any] = {}

    with torch.inference_mode():
        predicted_mean, predicted_covariance = density(geometry)
        for name in config["primary_masks"]:
            mask = config["observation_masks"][name]
            conditional_mean, conditional_covariance = condition_gaussian(
                predicted_mean, predicted_covariance, boundary, mask
            )
            boundary_samples = _sample_gaussian(
                conditional_mean, conditional_covariance, samples, generator
            )
            coherent_samples = _field_samples(operator, geometry, boundary_samples)
            oracle_mean = _oracle_field_mean(
                geometry, boundary, mask, split["grid"]
            )
            mask_tensor = torch.tensor(
                mask, device=geometry.device, dtype=geometry.dtype
            ).expand(geometry.shape[0], -1)
            direct_mean, direct_scale = direct(
                geometry, boundary * mask_tensor, mask_tensor
            )
            direct_samples = direct_mean[:, None, :] + direct_scale[:, None, :] * torch.randn(
                geometry.shape[0],
                samples,
                target.shape[-1],
                device=geometry.device,
                generator=generator,
            )
            masks_result[name] = {
                "aurora": _distribution_metrics(
                    coherent_samples,
                    target,
                    oracle_mean,
                    coverage,
                    conditions_per_geometry=conditions,
                    bootstrap_replicates=bootstrap_replicates,
                    seed=seed + 1000 * (len(masks_result) + 1),
                ),
                "direct_mask_gaussian": _distribution_metrics(
                    direct_samples,
                    target,
                    oracle_mean,
                    coverage,
                    conditions_per_geometry=conditions,
                    bootstrap_replicates=bootstrap_replicates,
                    seed=seed + 2000 * (len(masks_result) + 1),
                ),
            }

        coherence_geometry = split["geometry"][:64]
        density_mean, density_covariance = density(coherence_geometry)
        dummy = density_mean
        direct_boundary = _sample_gaussian(
            density_mean, density_covariance, samples, generator
        )
        direct_field = _field_samples(operator, coherence_geometry, direct_boundary)

        nested_seed_boundary = _sample_gaussian(
            density_mean, density_covariance, samples, generator
        )
        left = nested_seed_boundary[:, :, 0]
        nested_boundary = torch.empty_like(direct_boundary)
        nested_boundary[:, :, 0] = left
        variance_left = density_covariance[:, 0, 0].clamp_min(1e-8)
        gain = density_covariance[:, 1, 0] / variance_left
        right_mean = density_mean[:, 1, None] + gain[:, None] * (
            left - density_mean[:, 0, None]
        )
        right_variance = (
            density_covariance[:, 1, 1]
            - density_covariance[:, 1, 0].square() / variance_left
        ).clamp_min(1e-8)
        nested_boundary[:, :, 1] = right_mean + torch.sqrt(
            right_variance[:, None]
        ) * torch.randn(
            left.shape, device=left.device, generator=generator
        )
        nested_field = _field_samples(operator, coherence_geometry, nested_boundary)
        coherent_distance = _sliced_distance(
            direct_field, nested_field, seed=seed + 101
        )

        missing_mask = torch.zeros_like(coherence_geometry)
        baseline_mean, baseline_scale = direct(
            coherence_geometry, torch.zeros_like(coherence_geometry), missing_mask
        )
        baseline_direct = baseline_mean[:, None, :] + baseline_scale[:, None, :] * torch.randn(
            baseline_mean.shape[0],
            samples,
            baseline_mean.shape[1],
            device=baseline_mean.device,
            generator=generator,
        )
        partial_geometry = coherence_geometry[:, None, :].expand(-1, samples, -1)
        partial_observed = torch.zeros_like(nested_boundary)
        partial_observed[:, :, 0] = left
        partial_mask = torch.zeros_like(nested_boundary)
        partial_mask[:, :, 0] = 1.0
        partial_mean, partial_scale = direct(
            partial_geometry.reshape(-1, 2),
            partial_observed.reshape(-1, 2),
            partial_mask.reshape(-1, 2),
        )
        baseline_nested = partial_mean + partial_scale * torch.randn(
            partial_mean.shape, device=partial_mean.device, generator=generator
        )
        baseline_nested = baseline_nested.reshape(
            coherence_geometry.shape[0], samples, -1
        )
        baseline_distance = _sliced_distance(
            baseline_direct, baseline_nested, seed=seed + 103
        )

    primary = [masks_result[name]["aurora"] for name in config["primary_masks"]]
    aggregate = {
        "maximum_standardized_mean_error": max(
            item["standardized_mean_error"] for item in primary
        ),
        "maximum_coverage_error": max(item["coverage_error"] for item in primary),
        "maximum_projective_consistency_error": coherent_distance,
    }
    thresholds = config["success_thresholds"]
    checks = {
        key: aggregate[key] <= float(thresholds[key]) for key in aggregate
    }
    return {
        "seed": seed,
        "masks": masks_result,
        "coherence": {
            "aurora": coherent_distance,
            "direct_mask_gaussian": baseline_distance,
        },
        "gate_metrics": aggregate,
        "gate": {"passed": all(checks.values()), "checks": checks},
    }


def _summary(values: Sequence[float]) -> dict[str, float]:
    np, _ = _imports()
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(array)),
        "std": float(np.std(array, ddof=1)) if len(array) > 1 else 0.0,
        "min": float(np.min(array)),
        "max": float(np.max(array)),
    }


def run_experiment(config: Mapping[str, Any], require_cuda: bool) -> dict[str, Any]:
    _, torch = _imports()
    if require_cuda and not torch.cuda.is_available():
        raise ControlledPDEError("CUDA was required but is unavailable.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed_results = []
    for seed in [int(item) for item in config["seeds"]]:
        random.seed(seed)
        torch.manual_seed(seed)
        train = generate_split(
            geometries=int(config["train_geometries"]),
            conditions=int(config["conditions_per_geometry"]),
            grid_points=int(config["grid_points"]),
            seed=seed,
            device=device,
        )
        test = generate_split(
            geometries=int(config["test_geometries"]),
            conditions=int(config["conditions_per_geometry"]),
            grid_points=int(config["grid_points"]),
            seed=seed + 10_000,
            device=device,
        )
        density, operator, direct, train_metrics = train_models(train, config, seed)
        result = evaluate_seed(density, operator, direct, test, config, seed)
        result["train"] = train_metrics
        seed_results.append(result)

    gate_keys = (
        "maximum_standardized_mean_error",
        "maximum_coverage_error",
        "maximum_projective_consistency_error",
    )
    aggregate = {
        key: _summary([item["gate_metrics"][key] for item in seed_results])
        for key in gate_keys
    }
    thresholds = config["success_thresholds"]
    aggregate_checks = {
        key: aggregate[key]["max"] <= float(thresholds[key]) for key in gate_keys
    }
    return {
        "experiment_id": config["experiment_id"],
        "device": str(device),
        "seeds": seed_results,
        "aggregate_gate_metrics": aggregate,
        "gate": {"passed": all(aggregate_checks.values()), "checks": aggregate_checks},
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
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    command = " ".join(shlex.quote(item) for item in sys.argv)
    config_bytes = args.config.read_bytes()
    (output / "command.txt").write_text(command + "\n", encoding="utf-8")
    (output / "git_commit.txt").write_text(args.git_commit + "\n", encoding="utf-8")
    (output / "config.sha256").write_text(
        hashlib.sha256(config_bytes).hexdigest() + "\n", encoding="utf-8"
    )
    _write_json(output / "run_config.json", config)
    started = datetime.now(timezone.utc).isoformat()
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
        _write_json(output / "metrics.json", result)
        _write_json(
            output / "status.json",
            {"state": "completed", "gate_passed": result["gate"]["passed"]},
        )
        return 0
    except Exception as exc:
        _write_json(
            output / "status.json",
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
