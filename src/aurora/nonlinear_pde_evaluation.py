"""Evaluation primitives for the preregistered N1c outer test.

The functions in this module are deliberately estimator-level utilities. They
do not select a model, threshold, context, or seed after test access.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    marginal_gmm,
    sample_gmm,
)


def _torch() -> Any:
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server runtime
        raise NonlinearDecisionError("N1c evaluation requires torch.") from exc
    return torch


def mask_tensor(
    positions: Sequence[int],
    batch: int,
    *,
    device: Any,
    dtype: Any,
) -> Any:
    """Return one fixed 8-component observation mask for a batch."""

    torch = _torch()
    mask = torch.zeros(batch, 8, device=device, dtype=dtype)
    if positions:
        mask[:, list(positions)] = 1.0
    return mask


def conditional_posterior_from_joint(
    weights: Any,
    means: Any,
    covariances: Any,
    boundary: Any,
    observed_positions: Sequence[int],
) -> tuple[Any, Any, Any, list[int]]:
    """Condition a joint GMM and return its unobserved component ordering."""

    from aurora.nonlinear_pde import condition_gaussian_mixture

    observed = list(observed_positions)
    if not observed:
        return weights, means, covariances, list(range(means.shape[-1]))
    return condition_gaussian_mixture(
        weights,
        means,
        covariances,
        observed,
        boundary[:, observed],
    )


def direct_mask_posterior(
    weights: Any,
    means: Any,
    covariances: Any,
    observed_positions: Sequence[int],
) -> tuple[Any, Any, Any, list[int]]:
    """Take the missing marginal of a network that already saw the mask."""

    observed = set(int(index) for index in observed_positions)
    remaining = [index for index in range(means.shape[-1]) if index not in observed]
    if not remaining:
        return (
            weights,
            means[..., :0],
            covariances[..., :0, :0],
            remaining,
        )
    selected = marginal_gmm(weights, means, covariances, remaining)
    return *selected, remaining


def sequential_mask_posterior(
    weights: Any,
    means: Any,
    covariances: Any,
    boundary: Any,
    initial_positions: Sequence[int],
    reveal_order: Sequence[int],
) -> tuple[Any, Any, Any, list[int]]:
    """Condition an initial-mask network posterior on revealed components."""

    from aurora.nonlinear_pde import condition_gaussian_mixture

    current_weights, current_means, current_covariances, remaining = (
        direct_mask_posterior(
            weights,
            means,
            covariances,
            initial_positions,
        )
    )
    for component in reveal_order:
        if component not in remaining:
            raise NonlinearDecisionError("Sequential route reveals a non-missing value.")
        local_position = remaining.index(component)
        current_weights, current_means, current_covariances, local_remaining = (
            condition_gaussian_mixture(
                current_weights,
                current_means,
                current_covariances,
                [local_position],
                boundary[:, component : component + 1],
            )
        )
        remaining = [remaining[index] for index in local_remaining]
    return current_weights, current_means, current_covariances, remaining


def complete_boundary_samples(
    posterior: tuple[Any, Any, Any, Sequence[int]],
    observed_boundary: Any,
    observed_positions: Sequence[int],
    *,
    samples: int,
    seed: int,
) -> Any:
    """Sample missing values and place them into an observed full vector."""

    weights, means, covariances, remaining = posterior
    batch = observed_boundary.shape[0]
    full = observed_boundary[:, None].expand(-1, samples, -1).clone()
    if remaining:
        values = sample_gmm(
            weights,
            means,
            covariances,
            samples=samples,
            seed=seed,
        )
        full[:, :, list(remaining)] = values
    if observed_positions:
        full[:, :, list(observed_positions)] = observed_boundary[
            :, None, list(observed_positions)
        ]
    return full


def posterior_mean_completion(
    posterior: tuple[Any, Any, Any, Sequence[int]],
    observed_boundary: Any,
    observed_positions: Sequence[int],
) -> Any:
    """Return the mixture-mean completion under a frozen posterior."""

    weights, means, _, remaining = posterior
    completed = observed_boundary.clone()
    if remaining:
        completed[:, list(remaining)] = (weights[..., None] * means).sum(dim=1)
    if observed_positions:
        completed[:, list(observed_positions)] = observed_boundary[
            :, list(observed_positions)
        ]
    return completed


def radius_truncated_conditional_gmm_nll(
    weights: Any,
    means: Any,
    covariances: Any,
    boundary: Any,
    observed_positions: Sequence[int],
    *,
    maximum_radius: float,
) -> Any:
    """Evaluate the exact conditional NLL under a global Mahalanobis cutoff.

    The untruncated Gaussian conditional is corrected by the remaining-radius
    acceptance probability for every mixture component.  This is an oracle
    diagnostic for the controlled nonlinear boundary law, not a training loss.
    """

    torch = _torch()
    observed = list(int(index) for index in observed_positions)
    posterior_weights, conditional_mean, conditional_covariance, remaining = (
        conditional_posterior_from_joint(
            weights,
            means,
            covariances,
            boundary,
            observed,
        )
    )
    if not remaining:
        return boundary.new_zeros(boundary.shape[0])

    if observed:
        obs_index = torch.tensor(
            observed, device=means.device, dtype=torch.long
        )
        mu_observed = torch.index_select(means, -1, obs_index)
        covariance_observed = torch.index_select(
            torch.index_select(covariances, -2, obs_index),
            -1,
            obs_index,
        )
        obs_eye = torch.eye(
            len(observed), device=means.device, dtype=means.dtype
        )
        obs_cholesky = torch.linalg.cholesky(
            covariance_observed + 1e-6 * obs_eye
        )
        obs_residual = boundary[:, None, observed] - mu_observed
        obs_solved = torch.cholesky_solve(
            obs_residual.unsqueeze(-1), obs_cholesky
        ).squeeze(-1)
        observed_radius_squared = (obs_residual * obs_solved).sum(dim=-1)
    else:
        observed_radius_squared = means.new_zeros(weights.shape)

    target = boundary[:, remaining]
    dimension = len(remaining)
    eye = torch.eye(dimension, device=means.device, dtype=means.dtype)
    cholesky = torch.linalg.cholesky(
        conditional_covariance + 1e-6 * eye
    )
    residual = target[:, None] - conditional_mean
    solved = torch.cholesky_solve(
        residual.unsqueeze(-1), cholesky
    ).squeeze(-1)
    conditional_radius_squared = (residual * solved).sum(dim=-1)
    logdet = 2.0 * torch.log(
        torch.diagonal(cholesky, dim1=-2, dim2=-1)
    ).sum(dim=-1)
    log_normal = -0.5 * (
        conditional_radius_squared
        + logdet
        + dimension * math.log(2.0 * math.pi)
    )

    allowance_squared = (
        float(maximum_radius) ** 2 - observed_radius_squared
    ).clamp_min(0.0)
    acceptance = torch.special.gammainc(
        means.new_tensor(0.5 * dimension),
        0.5 * allowance_squared,
    )
    normalizer = (
        posterior_weights * acceptance
    ).sum(dim=-1).clamp_min(1e-12)
    valid = (
        observed_radius_squared + conditional_radius_squared
        <= float(maximum_radius) ** 2 + 1e-5
    )
    log_component = (
        torch.log(posterior_weights.clamp_min(1e-12)) + log_normal
    ).masked_fill(~valid, -torch.inf)
    log_numerator = torch.logsumexp(log_component, dim=-1)
    if not bool(torch.isfinite(log_numerator).all()):
        raise NonlinearDecisionError(
            "Radius-truncated conditional assigned zero density to a case."
        )
    return -(log_numerator - torch.log(normalizer))


def sample_radius_truncated_conditional_gmm(
    weights: Any,
    means: Any,
    covariances: Any,
    observed_positions: Sequence[int],
    observed_values: Any,
    *,
    samples: int,
    seed: int,
    maximum_radius: float,
) -> Any:
    """Sample the exact GMM conditional under a global latent-radius cutoff.

    For mixture component ``k``, Gaussian conditioning decomposes the full
    Mahalanobis radius into the observed marginal radius plus an independent
    conditional residual radius. The component posterior is therefore adjusted
    by the corresponding chi-square acceptance probability before residual
    rejection sampling.
    """

    torch = _torch()
    observed = list(int(index) for index in observed_positions)
    dimension = means.shape[-1]
    remaining = [index for index in range(dimension) if index not in observed]
    batch, mixtures = weights.shape
    if observed_values.shape != (batch, len(observed)):
        raise NonlinearDecisionError("Observed value shape does not match the mask.")
    if not remaining:
        full = means.new_zeros(batch, samples, dimension)
        full[:, :, observed] = observed_values[:, None]
        return full

    from aurora.nonlinear_pde import condition_gaussian_mixture

    if observed:
        conditional_weights, conditional_mean, conditional_covariance, order = (
            condition_gaussian_mixture(
                weights,
                means,
                covariances,
                observed,
                observed_values,
            )
        )
        if order != remaining:
            raise NonlinearDecisionError("Conditional component order changed.")
        obs_index = torch.tensor(observed, device=means.device, dtype=torch.long)
        mu_observed = torch.index_select(means, -1, obs_index)
        covariance_observed = torch.index_select(
            torch.index_select(covariances, -2, obs_index),
            -1,
            obs_index,
        )
        jitter = 1e-6 * torch.eye(
            len(observed), device=means.device, dtype=means.dtype
        )
        cholesky_observed = torch.linalg.cholesky(
            covariance_observed + jitter
        )
        residual = observed_values[:, None] - mu_observed
        solved = torch.cholesky_solve(
            residual.unsqueeze(-1), cholesky_observed
        ).squeeze(-1)
        observed_radius_squared = (residual * solved).sum(dim=-1)
    else:
        conditional_weights = weights
        conditional_mean = means
        conditional_covariance = covariances
        observed_radius_squared = means.new_zeros(batch, mixtures)

    allowance_squared = (
        float(maximum_radius) ** 2 - observed_radius_squared
    ).clamp_min(0.0)
    degrees = len(remaining)
    acceptance = torch.special.gammainc(
        means.new_tensor(0.5 * degrees),
        0.5 * allowance_squared,
    )
    adjusted = conditional_weights * acceptance
    normalizer = adjusted.sum(dim=-1, keepdim=True)
    if bool((normalizer <= 1e-12).any()):
        raise NonlinearDecisionError(
            "Observed boundary has zero mass under the truncated conditional."
        )
    adjusted = adjusted / normalizer

    generator = torch.Generator(device=means.device).manual_seed(seed)
    uniforms = torch.rand(
        batch,
        samples,
        generator=generator,
        device=means.device,
        dtype=means.dtype,
    )
    component = torch.sum(
        uniforms[:, :, None] > torch.cumsum(adjusted, dim=-1)[:, None],
        dim=-1,
    ).clamp_max(mixtures - 1)
    allowed = torch.sqrt(
        torch.gather(allowance_squared, 1, component).clamp_min(0.0)
    )

    standard = means.new_empty(batch, samples, degrees)
    accepted = torch.zeros(
        batch, samples, device=means.device, dtype=torch.bool
    )
    for _ in range(10000):
        if bool(accepted.all()):
            break
        proposal = torch.randn(
            batch,
            samples,
            degrees,
            generator=generator,
            device=means.device,
            dtype=means.dtype,
        )
        valid = (~accepted) & (
            torch.linalg.vector_norm(proposal, dim=-1) <= allowed
        )
        standard[valid] = proposal[valid]
        accepted |= valid
    if not bool(accepted.all()):
        raise NonlinearDecisionError("Truncated conditional rejection stalled.")

    cholesky = torch.linalg.cholesky(
        conditional_covariance
        + 1e-6
        * torch.eye(degrees, device=means.device, dtype=means.dtype)
    )
    selected_mean = torch.gather(
        conditional_mean[:, None].expand(-1, samples, -1, -1),
        2,
        component[:, :, None, None].expand(-1, -1, 1, degrees),
    ).squeeze(2)
    selected_cholesky = torch.gather(
        cholesky[:, None].expand(-1, samples, -1, -1, -1),
        2,
        component[:, :, None, None, None].expand(
            -1, -1, 1, degrees, degrees
        ),
    ).squeeze(2)
    missing = selected_mean + torch.einsum(
        "bsij,bsj->bsi", selected_cholesky, standard
    )
    full = means.new_zeros(batch, samples, dimension)
    full[:, :, remaining] = missing
    if observed:
        full[:, :, observed] = observed_values[:, None]
    return full


def standardize_functionals(
    values: Any,
    location: Any,
    scale: Any,
) -> Any:
    """Apply training-only functional standardization."""

    return (values - location) / scale


def functional_energy_score(samples: Any, target: Any) -> Any:
    """Return one multivariate energy score per case."""

    torch = _torch()
    if samples.ndim != 3 or target.shape != samples.shape[:1] + samples.shape[2:]:
        raise NonlinearDecisionError("Functional energy score shape mismatch.")
    first = torch.linalg.vector_norm(samples - target[:, None], dim=-1).mean(dim=1)
    half = samples.shape[1] // 2
    if half < 1:
        return first
    second = torch.linalg.vector_norm(
        samples[:, :half] - samples[:, half : 2 * half],
        dim=-1,
    ).mean(dim=1)
    return first - 0.5 * second


def functional_coverage(
    samples: Any,
    target: Any,
    *,
    probability: float,
) -> tuple[Any, Any]:
    """Return per-case/function coverage indicators and interval widths."""

    torch = _torch()
    alpha = 0.5 * (1.0 - probability)
    lower = torch.quantile(samples, alpha, dim=1)
    upper = torch.quantile(samples, 1.0 - alpha, dim=1)
    return ((target >= lower) & (target <= upper)).to(samples.dtype), upper - lower


def bounded_bayes_action(
    samples: Any,
    grid_minimum: Any,
    grid_maximum: Any,
    *,
    grid_points: int,
) -> tuple[Any, Any]:
    """Minimize clipped squared loss on the frozen per-functional grid."""

    torch = _torch()
    if samples.ndim != 3:
        raise NonlinearDecisionError("Bayes action samples must be [B,K,F].")
    fraction = torch.linspace(
        0.0,
        1.0,
        grid_points,
        device=samples.device,
        dtype=samples.dtype,
    )
    grid = (
        grid_minimum[:, None]
        + (grid_maximum - grid_minimum)[:, None] * fraction[None]
    )
    loss = (
        samples[:, :, :, None] - grid[None, None]
    ).square().clamp_max(1.0)
    expected = loss.mean(dim=1)
    index = expected.argmin(dim=-1)
    action = torch.gather(
        grid[None].expand(samples.shape[0], -1, -1),
        2,
        index[:, :, None],
    ).squeeze(-1)
    risk = torch.gather(expected, 2, index[:, :, None]).squeeze(-1)
    return action, risk


def bounded_action_risk(action: Any, samples: Any) -> Any:
    """Evaluate fixed standardized actions under posterior samples."""

    return (samples - action[:, None]).square().clamp_max(1.0).mean(dim=1)


def empirical_one_wasserstein(first: Any, second: Any) -> Any:
    """Per-case/function empirical 1-Wasserstein distance for equal sample counts."""

    torch = _torch()
    if first.shape != second.shape:
        raise NonlinearDecisionError("Wasserstein samples must have equal shape.")
    return torch.abs(
        torch.sort(first, dim=1).values - torch.sort(second, dim=1).values
    ).mean(dim=1)


def context_bootstrap_interval(
    differences: Any,
    *,
    replicates: int,
    seed: int,
) -> dict[str, float]:
    """Bootstrap a seed-averaged paired difference by context family."""

    torch = _torch()
    if differences.ndim != 2:
        raise NonlinearDecisionError("Bootstrap differences must be [seed, context].")
    generator = torch.Generator(device="cpu").manual_seed(seed)
    contexts = differences.shape[1]
    cpu = differences.detach().to(device="cpu", dtype=torch.float64)
    estimates = []
    for _ in range(replicates):
        index = torch.randint(
            contexts, (contexts,), generator=generator, device="cpu"
        )
        estimates.append(cpu[:, index].mean())
    distribution = torch.stack(estimates)
    return {
        "mean": float(cpu.mean().item()),
        "ci95_low": float(torch.quantile(distribution, 0.025).item()),
        "ci95_high": float(torch.quantile(distribution, 0.975).item()),
    }


def aggregate_context(values: Any, contexts: int, conditions: int) -> Any:
    """Average flattened per-case values within their context family."""

    if values.shape[0] != contexts * conditions:
        raise NonlinearDecisionError("Context aggregation shape mismatch.")
    return values.reshape(contexts, conditions, *values.shape[1:]).mean(dim=1)


def checkpoint_state_dict(path: str | Any, expected_sha256: str, device: Any) -> Any:
    """Verify a frozen checkpoint hash before loading it."""

    import hashlib
    from pathlib import Path

    torch = _torch()
    checkpoint = Path(path)
    digest = hashlib.sha256()
    with checkpoint.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != expected_sha256:
        raise NonlinearDecisionError(f"Checkpoint hash mismatch: {checkpoint.name}.")
    return torch.load(checkpoint, map_location=device, weights_only=True)


def representation_from_checkpoint(
    path: str | Any,
    expected_sha256: str,
    device: Any,
) -> Mapping[str, Any]:
    """Load and verify the shared train-only POD representation."""

    state = checkpoint_state_dict(path, expected_sha256, device)
    return {
        key: value.to(device) if hasattr(value, "to") else value
        for key, value in state.items()
    }
