"""Train-only steady versus transient-cycle-mean mismatch metrics."""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

import torch


class RegimeMismatchError(RuntimeError):
    """Raised when a mismatch metric receives an invalid field or scope."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise RegimeMismatchError(reason)


def mismatch_metrics(
    steady_wss: torch.Tensor,
    transient_cycle_wss: torch.Tensor,
    vertex_weights: torch.Tensor,
    *,
    epsilon: float = 1e-12,
) -> dict[str, float]:
    """Compare one steady vector field with one pulsatile cycle.

    The reference for relative normalization is the transient quantity. Spatial
    correlation is the area-weighted Pearson correlation of vector magnitudes.
    """

    _require(
        steady_wss.ndim == 2
        and steady_wss.shape[-1] == 3
        and transient_cycle_wss.ndim == 3
        and transient_cycle_wss.shape[0] == 80
        and transient_cycle_wss.shape[1:] == steady_wss.shape
        and vertex_weights.shape == (steady_wss.shape[0],),
        "shapes",
    )
    _require(
        bool(torch.isfinite(steady_wss).all().item())
        and bool(torch.isfinite(transient_cycle_wss).all().item())
        and bool(torch.isfinite(vertex_weights).all().item())
        and bool((vertex_weights >= 0).all().item())
        and bool((vertex_weights.sum() > 0).item())
        and epsilon > 0.0,
        "finite",
    )
    dtype = torch.float64
    steady = steady_wss.to(dtype)
    cycle = transient_cycle_wss.to(dtype)
    weights = vertex_weights.to(dtype)
    weights = weights / weights.sum()
    cycle_mean = cycle.mean(dim=0)
    transient_tawss = torch.linalg.vector_norm(cycle, dim=-1).mean(dim=0)
    steady_magnitude = torch.linalg.vector_norm(steady, dim=-1)
    mean_magnitude = torch.linalg.vector_norm(cycle_mean, dim=-1)

    difference_energy = torch.sum(
        weights * torch.sum((steady - cycle_mean).square(), dim=-1)
    )
    reference_energy = torch.sum(
        weights * torch.sum(cycle_mean.square(), dim=-1)
    )
    _require(float(reference_energy.item()) > epsilon, "cycle_mean_energy")
    relative_vector_l2 = torch.sqrt(
        difference_energy / torch.clamp(reference_energy, min=epsilon)
    )

    dot = torch.sum(weights * torch.sum(steady * cycle_mean, dim=-1))
    steady_energy = torch.sum(weights * torch.sum(steady.square(), dim=-1))
    denominator = torch.sqrt(
        torch.clamp(steady_energy * reference_energy, min=epsilon)
    )
    cosine = dot / denominator

    steady_mean = torch.sum(weights * steady_magnitude)
    transient_mean = torch.sum(weights * mean_magnitude)
    centered_steady = steady_magnitude - steady_mean
    centered_transient = mean_magnitude - transient_mean
    covariance = torch.sum(weights * centered_steady * centered_transient)
    steady_variance = torch.sum(weights * centered_steady.square())
    transient_variance = torch.sum(weights * centered_transient.square())
    _require(
        float(steady_variance.item()) > epsilon
        and float(transient_variance.item()) > epsilon,
        "magnitude_variance",
    )
    spatial_correlation = covariance / torch.sqrt(
        torch.clamp(steady_variance * transient_variance, min=epsilon)
    )

    tawss_denominator = torch.sum(weights * transient_tawss)
    _require(float(tawss_denominator.item()) > epsilon, "tawss_energy")
    tawss_normalized_absolute_difference = (
        torch.sum(weights * torch.abs(steady_magnitude - transient_tawss))
        / tawss_denominator
    )
    tawss_signed_bias = (
        torch.sum(weights * (steady_magnitude - transient_tawss))
        / tawss_denominator
    )
    result = {
        "steady_vs_cycle_mean_vector_relative_l2": float(relative_vector_l2.item()),
        "steady_vs_cycle_mean_global_cosine": float(cosine.item()),
        "steady_vs_cycle_mean_magnitude_spatial_correlation": float(
            spatial_correlation.item()
        ),
        "steady_magnitude_vs_transient_tawss_normalized_absolute_difference": float(
            tawss_normalized_absolute_difference.item()
        ),
        "steady_magnitude_vs_transient_tawss_signed_bias": float(
            tawss_signed_bias.item()
        ),
    }
    _require(all(math.isfinite(value) for value in result.values()), "result")
    return result


def distribution_summary(values: Sequence[float]) -> dict[str, float | int]:
    """Return deterministic population summaries for one case-level endpoint."""

    tensor = torch.tensor([float(value) for value in values], dtype=torch.float64)
    _require(
        tensor.numel() > 0 and bool(torch.isfinite(tensor).all().item()), "values"
    )
    quantiles = torch.quantile(
        tensor, torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0], dtype=torch.float64)
    )
    return {
        "count": int(tensor.numel()),
        "mean": float(tensor.mean().item()),
        "std_population": float(tensor.std(unbiased=False).item()),
        "minimum": float(quantiles[0].item()),
        "q25": float(quantiles[1].item()),
        "median": float(quantiles[2].item()),
        "q75": float(quantiles[3].item()),
        "maximum": float(quantiles[4].item()),
    }


def summarize_case_metrics(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, float | int]]:
    _require(bool(rows), "rows")
    keys = tuple(rows[0])
    _require(
        all(tuple(row) == keys for row in rows)
        and all(isinstance(row[key], (int, float)) for row in rows for key in keys),
        "row_schema",
    )
    return {
        key: distribution_summary([float(row[key]) for row in rows]) for key in keys
    }
