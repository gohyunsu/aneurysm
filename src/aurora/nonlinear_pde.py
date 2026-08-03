"""Preregistered N0 gate for AURORA's nonlinear multicomponent PDE domain.

N0 is deliberately not a learned-model experiment.  It checks that the
semilinear PDE, its eight-component boundary family, the numerical solver, and
the solution functionals are accurate and non-degenerate before any N1 model
or baseline can see held-out simulations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


class NonlinearPDEError(RuntimeError):
    """Raised when the frozen N0 contract cannot be honored."""


def _imports() -> tuple[Any, Any]:
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - server runtime
        raise NonlinearPDEError("Nonlinear N0 requires numpy and torch.") from exc
    return np, torch


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _require_keys(payload: Mapping[str, Any], keys: Sequence[str], label: str) -> None:
    missing = sorted(set(keys) - set(payload))
    if missing:
        raise NonlinearPDEError(f"{label} is missing keys: {missing}")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate the immutable N0 solver/nontriviality contract."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        [
            "schema_version",
            "experiment_id",
            "status",
            "source_gate",
            "source_result",
            "source_result_sha256",
            "stage",
            "may_establish_method_novelty",
            "may_authorize_irregular_3d_headline",
            "seeds",
            "pde",
            "boundary_law",
            "sampling",
            "functionals",
            "conditioning_check",
            "success_thresholds",
            "decision_rule",
            "interpretation",
        ],
        "N0 config",
    )
    if payload["schema_version"] != "aurora.nonlinear_pde_n0.v1":
        raise NonlinearPDEError("Unexpected nonlinear N0 schema version.")
    if payload["status"] != "preregistered_before_gpu_run":
        raise NonlinearPDEError("N0 must remain preregistered before GPU execution.")
    if payload["source_gate"] != "G1s" or payload["stage"] != "solver_nontriviality":
        raise NonlinearPDEError("N0 must follow G1s and remain a solver gate.")
    if payload["may_establish_method_novelty"] is not False:
        raise NonlinearPDEError("N0 cannot establish method novelty.")
    if payload["may_authorize_irregular_3d_headline"] is not False:
        raise NonlinearPDEError("N0 cannot authorize an irregular-3D headline.")

    source_result = (config_path.parent / payload["source_result"]).resolve()
    if (
        not source_result.is_file()
        or _sha256(source_result) != payload["source_result_sha256"]
    ):
        raise NonlinearPDEError("Pinned G1s result does not match N0.")

    seeds = [int(value) for value in payload["seeds"]]
    if seeds != [62080311, 62080312, 62080313]:
        raise NonlinearPDEError("N0 numerical-audit seeds changed after registration.")

    pde = payload["pde"]
    _require_keys(
        pde,
        [
            "equation",
            "grid_points",
            "reference_grid_points",
            "context_dim",
            "boundary_components",
            "boundary_modes_per_edge",
            "dtype",
            "maximum_iterations",
            "reference_maximum_iterations",
            "convergence_tolerance",
            "residual_check_interval",
            "relaxation",
            "nonlinearity_range",
            "diffusivity_range",
        ],
        "N0 PDE",
    )
    coarse = int(pde["grid_points"])
    reference = int(pde["reference_grid_points"])
    if coarse < 17 or reference != 2 * coarse - 1:
        raise NonlinearPDEError("Reference grid must be the nested 2N-1 grid.")
    if int(pde["context_dim"]) != 5 or int(pde["boundary_components"]) != 8:
        raise NonlinearPDEError("N0 freezes five context and eight BC components.")
    if int(pde["boundary_modes_per_edge"]) != 2:
        raise NonlinearPDEError("N0 requires two sine modes on each of four edges.")
    if pde["dtype"] != "float32":
        raise NonlinearPDEError("N0 GPU contract freezes float32.")
    if pde["nonlinearity_range"] != [8.0, 40.0]:
        raise NonlinearPDEError("N0 nonlinearity range changed after registration.")
    if pde["diffusivity_range"] != [0.7, 1.3]:
        raise NonlinearPDEError("N0 diffusivity range changed after registration.")

    sampling = payload["sampling"]
    if sampling != {
        "contexts_per_seed": 24,
        "conditions_per_context": 12,
        "reference_cases_per_seed": 12,
        "paired_base_cases_per_seed": 48,
        "paired_component_perturbation": 0.15,
        "all_conditions_of_one_context_remain_grouped": True,
    }:
        raise NonlinearPDEError("N0 sampling contract changed after registration.")

    thresholds = payload["success_thresholds"]
    if thresholds != {
        "maximum_solver_normalized_residual": 0.0005,
        "maximum_coarse_reference_relative_l2": 0.04,
        "minimum_median_nonlinear_departure": 0.01,
        "minimum_worst_component_response_median": 0.01,
        "minimum_response_effective_rank": 3.0,
        "minimum_functional_winner_components": 3,
        "maximum_dominant_functional_winner_share": 0.75,
        "maximum_analytic_conditioning_route_residual": 0.00002,
    }:
        raise NonlinearPDEError("N0 success thresholds changed after registration.")

    boundary_law = payload["boundary_law"]
    if (
        int(boundary_law["mixture_components"]) != 2
        or boundary_law["conditioning"] != "analytic_gaussian_mixture"
    ):
        raise NonlinearPDEError("N0 freezes a two-component analytic GMM.")

    if payload["functionals"] != [
        "domain_mean",
        "central_hotspot",
        "smooth_maximum",
        "right_boundary_flux",
    ]:
        raise NonlinearPDEError("N0 functional set changed after registration.")
    conditioning = payload["conditioning_check"]
    if (
        conditioning["initial_observed_components"] != [0, 2]
        or conditioning["additional_components"] != [5, 7]
        or conditioning["routes"] != ["direct_union", "sequential_5_then_7"]
    ):
        raise NonlinearPDEError("N0 conditioning route changed after registration.")

    decision = payload["decision_rule"]
    if decision != {
        "all_checks_required": True,
        "pass_authorizes_n1_model_and_strong_baseline_registration": True,
        "pass_does_not_establish_novelty_or_baseline_superiority": True,
        "failure_requires_pde_or_solver_redesign_before_learning": True,
        "irregular_3d_remains_deferred_until_n1_positive": True,
    }:
        raise NonlinearPDEError("N0 decision rule changed after registration.")
    return payload


def _context(seed: int, count: int, device: Any, dtype: Any) -> Any:
    _, torch = _imports()
    generator = torch.Generator(device="cpu").manual_seed(seed)
    return (2.0 * torch.rand(count, 5, generator=generator) - 1.0).to(
        device=device, dtype=dtype
    )


def boundary_law(context: Any) -> tuple[Any, Any, Any]:
    """Return weights, means, and covariances for a context-dependent 2-GMM."""

    _, torch = _imports()
    batch = context.shape[0]
    device, dtype = context.device, context.dtype
    indices = torch.arange(8, device=device, dtype=dtype)
    phase = context[:, 0:1] * (0.45 + 0.08 * indices)
    spatial = context[:, 1:2] * torch.cos((indices + 1.0) * math.pi / 4.0)
    alternating_sign = torch.where(
        (indices.to(torch.int64) % 2) == 0,
        torch.ones_like(indices),
        -torch.ones_like(indices),
    )
    common = 0.10 * context[:, 2:3] * alternating_sign
    mean0 = 0.16 * torch.sin(phase + indices * 0.55) + 0.09 * spatial + common
    mean1 = -0.13 * torch.cos(phase - indices * 0.40) + 0.07 * spatial - common
    means = torch.stack((mean0, mean1), dim=1)

    logits = 0.85 * context[:, 3] - 0.45 * context[:, 4]
    weights = torch.stack((torch.sigmoid(logits), torch.sigmoid(-logits)), dim=-1)

    distance = torch.abs(indices[:, None] - indices[None, :])
    correlation = 0.42**distance
    correlation = correlation + 0.08 * (
        (indices[:, None] % 2) == (indices[None, :] % 2)
    ).to(dtype)
    diagonal = torch.diagonal(correlation)
    correlation = correlation / torch.sqrt(diagonal[:, None] * diagonal[None, :])
    covariances = []
    for mixture in range(2):
        std = (
            0.16
            + 0.025 * mixture
            + 0.025 * torch.sigmoid(context[:, 2:3] + 0.3 * indices)
        )
        covariance = std[:, :, None] * correlation[None] * std[:, None, :]
        covariance = covariance + 1e-4 * torch.eye(8, device=device, dtype=dtype)
        covariances.append(covariance)
    return weights, means, torch.stack(covariances, dim=1)


def sample_boundary(
    weights: Any, means: Any, covariances: Any, samples: int, seed: int
) -> Any:
    """Sample GMM boundary coefficients without relying on global RNG state."""

    _, torch = _imports()
    generator = torch.Generator(device="cpu").manual_seed(seed)
    batch = weights.shape[0]
    uniforms = torch.rand(batch, samples, generator=generator).to(weights.device)
    component = (uniforms > weights[:, 0:1]).long()
    standard = torch.randn(batch, samples, 8, generator=generator).to(
        device=means.device, dtype=means.dtype
    )
    cholesky = torch.linalg.cholesky(covariances)
    selected_mean = torch.gather(
        means[:, None].expand(-1, samples, -1, -1),
        2,
        component[:, :, None, None].expand(-1, -1, 1, 8),
    ).squeeze(2)
    selected_cholesky = torch.gather(
        cholesky[:, None].expand(-1, samples, -1, -1, -1),
        2,
        component[:, :, None, None, None].expand(-1, -1, 1, 8, 8),
    ).squeeze(2)
    return selected_mean + torch.einsum("bsij,bsj->bsi", selected_cholesky, standard)


def _boundary_field(boundary: Any, grid_points: int) -> Any:
    _, torch = _imports()
    coordinate = torch.linspace(
        0.0, 1.0, grid_points, device=boundary.device, dtype=boundary.dtype
    )
    basis = torch.stack(
        (torch.sin(math.pi * coordinate), torch.sin(2.0 * math.pi * coordinate))
    )
    field = torch.zeros(
        boundary.shape[0],
        grid_points,
        grid_points,
        device=boundary.device,
        dtype=boundary.dtype,
    )
    field[:, 0, :] = torch.einsum("bk,kn->bn", boundary[:, 0:2], basis)
    field[:, -1, :] = torch.einsum("bk,kn->bn", boundary[:, 2:4], basis)
    field[:, :, 0] += torch.einsum("bk,kn->bn", boundary[:, 4:6], basis)
    field[:, :, -1] += torch.einsum("bk,kn->bn", boundary[:, 6:8], basis)
    return field


def _pde_fields(
    context: Any, grid_points: int, linear: bool = False
) -> tuple[Any, Any, Any]:
    _, torch = _imports()
    coordinate = torch.linspace(
        0.0, 1.0, grid_points, device=context.device, dtype=context.dtype
    )
    yy, xx = torch.meshgrid(coordinate, coordinate, indexing="ij")
    center_x = 0.32 + 0.36 * torch.sigmoid(1.2 * context[:, 0])
    center_y = 0.32 + 0.36 * torch.sigmoid(1.2 * context[:, 1])
    width = 0.10 + 0.05 * torch.sigmoid(context[:, 2])
    radius = (
        (xx[None] - center_x[:, None, None]).square()
        + (yy[None] - center_y[:, None, None]).square()
    )
    bump = torch.exp(-radius / (2.0 * width[:, None, None].square()))
    diffusivity = 1.0 + 0.30 * context[:, 2, None, None] * bump
    forcing = (0.8 + 0.4 * torch.sigmoid(context[:, 3]))[:, None, None] * bump
    if linear:
        nonlinearity = torch.zeros_like(context[:, 4])
    else:
        nonlinearity = 24.0 + 16.0 * context[:, 4]
    return diffusivity, forcing, nonlinearity


def solve_semilinear(
    context: Any,
    boundary: Any,
    *,
    grid_points: int,
    maximum_iterations: int,
    tolerance: float,
    check_interval: int,
    relaxation: float,
    linear: bool = False,
) -> tuple[Any, dict[str, Any]]:
    """Solve ``-div(a grad u) + lambda u^3 = f`` by damped Jacobi-Newton."""

    _, torch = _imports()
    if context.shape[0] != boundary.shape[0]:
        raise NonlinearPDEError("Context and boundary batch sizes differ.")
    h = 1.0 / (grid_points - 1)
    inverse_h2 = 1.0 / (h * h)
    diffusivity, forcing, nonlinearity = _pde_fields(context, grid_points, linear)
    solution = _boundary_field(boundary, grid_points)
    converged = False
    update_max = math.inf

    center_diffusivity = diffusivity[:, 1:-1, 1:-1]
    east = 0.5 * (center_diffusivity + diffusivity[:, 1:-1, 2:])
    west = 0.5 * (center_diffusivity + diffusivity[:, 1:-1, :-2])
    north = 0.5 * (center_diffusivity + diffusivity[:, 2:, 1:-1])
    south = 0.5 * (center_diffusivity + diffusivity[:, :-2, 1:-1])
    diagonal = (east + west + north + south) * inverse_h2

    for iteration in range(1, maximum_iterations + 1):
        center = solution[:, 1:-1, 1:-1]
        neighbor_term = (
            east * solution[:, 1:-1, 2:]
            + west * solution[:, 1:-1, :-2]
            + north * solution[:, 2:, 1:-1]
            + south * solution[:, :-2, 1:-1]
        ) * inverse_h2
        residual = (
            diagonal * center
            - neighbor_term
            + nonlinearity[:, None, None] * center.pow(3)
            - forcing[:, 1:-1, 1:-1]
        )
        derivative = diagonal + 3.0 * nonlinearity[:, None, None] * center.square()
        updated = center - relaxation * residual / derivative
        next_solution = solution.clone()
        next_solution[:, 1:-1, 1:-1] = updated
        solution = next_solution
        if iteration % check_interval == 0 or iteration == maximum_iterations:
            update_max = float((relaxation * residual / derivative).abs().amax().item())
            if update_max <= tolerance:
                converged = True
                break

    residual = normalized_residual(context, solution, linear=linear)
    return solution, {
        "iterations": iteration,
        "converged": converged,
        "maximum_update": update_max,
        "maximum_normalized_residual": float(residual.max().item()),
        "mean_normalized_residual": float(residual.mean().item()),
    }


def normalized_residual(context: Any, solution: Any, linear: bool = False) -> Any:
    """Return per-case scale-normalized interior residual."""

    _, torch = _imports()
    grid_points = solution.shape[-1]
    h = 1.0 / (grid_points - 1)
    inverse_h2 = 1.0 / (h * h)
    diffusivity, forcing, nonlinearity = _pde_fields(context, grid_points, linear)
    center = solution[:, 1:-1, 1:-1]
    a_center = diffusivity[:, 1:-1, 1:-1]
    east = 0.5 * (a_center + diffusivity[:, 1:-1, 2:])
    west = 0.5 * (a_center + diffusivity[:, 1:-1, :-2])
    north = 0.5 * (a_center + diffusivity[:, 2:, 1:-1])
    south = 0.5 * (a_center + diffusivity[:, :-2, 1:-1])
    diagonal_term = (east + west + north + south) * inverse_h2 * center
    neighbor_term = (
        east * solution[:, 1:-1, 2:]
        + west * solution[:, 1:-1, :-2]
        + north * solution[:, 2:, 1:-1]
        + south * solution[:, :-2, 1:-1]
    ) * inverse_h2
    nonlinear_term = nonlinearity[:, None, None] * center.pow(3)
    force = forcing[:, 1:-1, 1:-1]
    residual = diagonal_term - neighbor_term + nonlinear_term - force
    numerator = torch.linalg.vector_norm(residual.flatten(1), dim=1)
    denominator = (
        torch.linalg.vector_norm(diagonal_term.flatten(1), dim=1)
        + torch.linalg.vector_norm(neighbor_term.flatten(1), dim=1)
        + torch.linalg.vector_norm(nonlinear_term.flatten(1), dim=1)
        + torch.linalg.vector_norm(force.flatten(1), dim=1)
    ).clamp_min(1e-8)
    return numerator / denominator


def solution_functionals(solution: Any, context: Any) -> Any:
    """Compute four registered scalar solution functionals."""

    _, torch = _imports()
    if solution.shape[0] != context.shape[0]:
        raise NonlinearPDEError("Solution and context batch sizes differ.")
    grid_points = solution.shape[-1]
    coordinate = torch.linspace(
        0.0, 1.0, grid_points, device=solution.device, dtype=solution.dtype
    )
    yy, xx = torch.meshgrid(coordinate, coordinate, indexing="ij")
    hotspot_weight = torch.exp(
        -((xx - 0.60).square() + (yy - 0.60).square()) / (2.0 * 0.12**2)
    )
    hotspot_weight = hotspot_weight / hotspot_weight.sum()
    domain_mean = solution.mean(dim=(-2, -1))
    hotspot = (solution * hotspot_weight).sum(dim=(-2, -1))
    temperature = 0.08
    smooth_maximum = temperature * torch.logsumexp(
        solution.flatten(1) / temperature, dim=1
    ) - temperature * math.log(solution.shape[-1] * solution.shape[-2])
    h = 1.0 / (grid_points - 1)
    diffusivity, _, _ = _pde_fields(context, grid_points)
    right_face_diffusivity = 0.5 * (
        diffusivity[:, 1:-1, -1] + diffusivity[:, 1:-1, -2]
    )
    right_flux = (
        -right_face_diffusivity
        * (solution[:, 1:-1, -1] - solution[:, 1:-1, -2])
        / h
    ).mean(dim=1)
    return torch.stack((domain_mean, hotspot, smooth_maximum, right_flux), dim=-1)


def _mixture_moments(weights: Any, means: Any, covariances: Any) -> tuple[Any, Any]:
    _, torch = _imports()
    mean = torch.sum(weights[..., None] * means, dim=-2)
    centered = means - mean[..., None, :]
    covariance = torch.sum(
        weights[..., None, None]
        * (covariances + centered[..., :, None] * centered[..., None, :]),
        dim=-3,
    )
    return mean, covariance


def condition_gaussian_mixture(
    weights: Any,
    means: Any,
    covariances: Any,
    observed_positions: Sequence[int],
    observed_values: Any,
) -> tuple[Any, Any, Any, list[int]]:
    """Analytically condition a batch of Gaussian mixtures."""

    _, torch = _imports()
    dimension = means.shape[-1]
    observed = list(observed_positions)
    remaining = [index for index in range(dimension) if index not in observed]
    if not observed:
        return weights, means, covariances, remaining
    obs = torch.tensor(observed, device=means.device)
    rem = torch.tensor(remaining, device=means.device)
    mu_o = torch.index_select(means, -1, obs)
    mu_r = torch.index_select(means, -1, rem)
    cov_oo = torch.index_select(torch.index_select(covariances, -2, obs), -1, obs)
    cov_ro = torch.index_select(torch.index_select(covariances, -2, rem), -1, obs)
    cov_rr = torch.index_select(torch.index_select(covariances, -2, rem), -1, rem)
    jitter = 1e-6 * torch.eye(len(observed), device=means.device, dtype=means.dtype)
    cholesky = torch.linalg.cholesky(cov_oo + jitter)
    residual = observed_values[:, None, :] - mu_o
    solved = torch.cholesky_solve(residual.unsqueeze(-1), cholesky).squeeze(-1)
    conditional_mean = mu_r + torch.einsum("bkro,bko->bkr", cov_ro, solved)
    gain = torch.cholesky_solve(cov_ro.transpose(-2, -1), cholesky)
    conditional_covariance = cov_rr - torch.matmul(cov_ro, gain)

    mahalanobis = torch.sum(residual * solved, dim=-1)
    logdet = 2.0 * torch.log(torch.diagonal(cholesky, dim1=-2, dim2=-1)).sum(-1)
    log_likelihood = -0.5 * (
        mahalanobis + logdet + len(observed) * math.log(2.0 * math.pi)
    )
    log_weights = torch.log(weights.clamp_min(1e-12)) + log_likelihood
    conditional_weights = torch.softmax(log_weights, dim=-1)
    return conditional_weights, conditional_mean, conditional_covariance, remaining


def conditioning_route_residual(
    weights: Any, means: Any, covariances: Any, boundary: Any
) -> float:
    """Compare direct and sequential conditioning on the same final mask."""

    _, torch = _imports()
    first, second = [0, 2], [5, 7]
    direct_indices = first + second
    direct_values = boundary[:, direct_indices]
    dw, dm, dc, _ = condition_gaussian_mixture(
        weights, means, covariances, direct_indices, direct_values
    )
    direct_mean, direct_covariance = _mixture_moments(dw, dm, dc)

    sw, sm, sc, remaining = condition_gaussian_mixture(
        weights, means, covariances, first, boundary[:, first]
    )
    positions = [remaining.index(index) for index in second]
    sw, sm, sc, _ = condition_gaussian_mixture(
        sw, sm, sc, positions, boundary[:, second]
    )
    sequential_mean, sequential_covariance = _mixture_moments(sw, sm, sc)
    mean_residual = torch.max(torch.abs(direct_mean - sequential_mean))
    covariance_residual = torch.max(torch.abs(direct_covariance - sequential_covariance))
    return float(torch.maximum(mean_residual, covariance_residual).item())


def _relative_l2(prediction: Any, reference: Any) -> Any:
    _, torch = _imports()
    numerator = torch.linalg.vector_norm((prediction - reference).flatten(1), dim=1)
    denominator = torch.linalg.vector_norm(reference.flatten(1), dim=1).clamp_min(1e-6)
    return numerator / denominator


def context_stratified_case_indices(
    contexts: int,
    conditions_per_context: int,
    cases: int,
) -> list[int]:
    """Select deterministic context-major indices without a contiguous-prefix bias.

    When fewer cases than contexts are requested, the selected contexts are evenly
    spaced and each uses a rotating condition.  When at least one case per context
    is available, every context is represented before an additional condition is
    assigned.  This selector was introduced after the frozen N0 result and therefore
    cannot alter that result; it is intended for N0 attribution and fresh re-entry.
    """

    if contexts <= 0 or conditions_per_context <= 0:
        raise NonlinearPDEError("Context and condition counts must be positive.")
    total = contexts * conditions_per_context
    if cases <= 0 or cases > total:
        raise NonlinearPDEError("Requested cases must be within the case grid.")

    selected: list[int] = []
    if cases < contexts:
        for rank in range(cases):
            context_index = (rank * contexts) // cases
            condition_index = (7 * rank) % conditions_per_context
            selected.append(
                context_index * conditions_per_context + condition_index
            )
        return selected

    quotient, remainder = divmod(cases, contexts)
    for context_index in range(contexts):
        count = quotient + int(context_index < remainder)
        stride = max(1, conditions_per_context // count)
        for slot in range(count):
            condition_index = (
                5 * context_index + slot * stride
            ) % conditions_per_context
            selected.append(
                context_index * conditions_per_context + condition_index
            )
    return selected


def _quantiles(values: Any) -> dict[str, float]:
    _, torch = _imports()
    return {
        "minimum": float(values.min().item()),
        "median": float(torch.quantile(values, 0.5).item()),
        "maximum": float(values.max().item()),
    }


def _environment(torch: Any) -> dict[str, Any]:
    environment = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_runtime": torch.version.cuda,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }
    if torch.cuda.is_available():
        environment["gpu_name"] = torch.cuda.get_device_name(0)
        environment["gpu_capability"] = list(torch.cuda.get_device_capability(0))
    return environment


def run_experiment(config: Mapping[str, Any], require_cuda: bool) -> dict[str, Any]:
    """Execute N0 and return aggregate-only solver/nontriviality evidence."""

    _, torch = _imports()
    if require_cuda and not torch.cuda.is_available():
        raise NonlinearPDEError("N0 requires a scheduler-allocated CUDA device.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float32
    pde = config["pde"]
    sampling = config["sampling"]
    seed_results: list[dict[str, Any]] = []

    for seed in [int(value) for value in config["seeds"]]:
        contexts = _context(
            seed,
            int(sampling["contexts_per_seed"]),
            device,
            dtype,
        )
        weights, means, covariances = boundary_law(contexts)
        boundary = sample_boundary(
            weights,
            means,
            covariances,
            int(sampling["conditions_per_context"]),
            seed + 100_000,
        )
        expanded_context = contexts[:, None, :].expand(
            -1, boundary.shape[1], -1
        ).reshape(-1, contexts.shape[-1])
        flat_boundary = boundary.reshape(-1, boundary.shape[-1])
        solution, solver = solve_semilinear(
            expanded_context,
            flat_boundary,
            grid_points=int(pde["grid_points"]),
            maximum_iterations=int(pde["maximum_iterations"]),
            tolerance=float(pde["convergence_tolerance"]),
            check_interval=int(pde["residual_check_interval"]),
            relaxation=float(pde["relaxation"]),
        )

        reference_count = int(sampling["reference_cases_per_seed"])
        ref_context = expanded_context[:reference_count]
        ref_boundary = flat_boundary[:reference_count]
        reference, reference_solver = solve_semilinear(
            ref_context,
            ref_boundary,
            grid_points=int(pde["reference_grid_points"]),
            maximum_iterations=int(pde["reference_maximum_iterations"]),
            tolerance=float(pde["convergence_tolerance"]),
            check_interval=int(pde["residual_check_interval"]),
            relaxation=float(pde["relaxation"]),
        )
        nested_reference = reference[:, ::2, ::2]
        discretization = _relative_l2(solution[:reference_count], nested_reference)

        linear_solution, linear_solver = solve_semilinear(
            ref_context,
            ref_boundary,
            grid_points=int(pde["grid_points"]),
            maximum_iterations=int(pde["maximum_iterations"]),
            tolerance=float(pde["convergence_tolerance"]),
            check_interval=int(pde["residual_check_interval"]),
            relaxation=float(pde["relaxation"]),
            linear=True,
        )
        nonlinear_departure = _relative_l2(solution[:reference_count], linear_solution)

        pair_count = int(sampling["paired_base_cases_per_seed"])
        pair_context = expanded_context[:pair_count]
        pair_boundary = flat_boundary[:pair_count]
        base_solution = solution[:pair_count]
        component_count = int(pde["boundary_components"])
        delta = float(sampling["paired_component_perturbation"])
        perturbed_boundary = pair_boundary[:, None, :].expand(
            -1, component_count, -1
        ).clone()
        component_index = torch.arange(component_count, device=device)
        perturbed_boundary[:, component_index, component_index] += delta
        perturbed_solution, paired_solver = solve_semilinear(
            pair_context[:, None, :]
            .expand(-1, component_count, -1)
            .reshape(-1, pair_context.shape[-1]),
            perturbed_boundary.reshape(-1, component_count),
            grid_points=int(pde["grid_points"]),
            maximum_iterations=int(pde["maximum_iterations"]),
            tolerance=float(pde["convergence_tolerance"]),
            check_interval=int(pde["residual_check_interval"]),
            relaxation=float(pde["relaxation"]),
        )
        perturbed_solution = perturbed_solution.reshape(
            pair_count, component_count, int(pde["grid_points"]), int(pde["grid_points"])
        )
        delta_field = perturbed_solution - base_solution[:, None]
        response = torch.linalg.vector_norm(delta_field.flatten(2), dim=-1)
        base_scale = torch.linalg.vector_norm(base_solution.flatten(1), dim=-1)
        response = response / (
            base_scale[:, None]
            + torch.linalg.vector_norm(pair_boundary, dim=-1)[:, None]
            + 1e-6
        )
        component_medians = torch.quantile(response, 0.5, dim=0)

        normalized_delta = delta_field / torch.linalg.vector_norm(
            delta_field.flatten(2), dim=-1
        ).clamp_min(1e-8)[:, :, None, None]
        gram = torch.einsum(
            "bcxy,bdxy->cd", normalized_delta, normalized_delta
        ) / pair_count
        eigenvalues = torch.linalg.eigvalsh(gram).clamp_min(0.0)
        effective_rank = float(
            (eigenvalues.sum().square() / eigenvalues.square().sum().clamp_min(1e-12)).item()
        )

        base_functionals = solution_functionals(base_solution, pair_context)
        paired_functionals = solution_functionals(
            perturbed_solution.reshape(
                -1, int(pde["grid_points"]), int(pde["grid_points"])
            ),
            pair_context[:, None, :]
            .expand(-1, component_count, -1)
            .reshape(-1, pair_context.shape[-1]),
        ).reshape(pair_count, component_count, -1)
        functional_response = torch.abs(
            paired_functionals - base_functionals[:, None, :]
        )
        winners = torch.argmax(functional_response, dim=1).flatten()
        counts = torch.bincount(winners, minlength=component_count)
        active_winners = int(torch.sum(counts > 0).item())
        dominant_share = float((counts.max() / counts.sum()).item())

        path_residual = conditioning_route_residual(
            weights,
            means,
            covariances,
            boundary[:, 0, :],
        )
        seed_results.append(
            {
                "seed": seed,
                "solver": solver,
                "reference_solver": reference_solver,
                "linear_solver": linear_solver,
                "paired_solver": paired_solver,
                "discretization_relative_l2": _quantiles(discretization),
                "nonlinear_departure_relative_l2": _quantiles(nonlinear_departure),
                "component_response_medians": [
                    float(value) for value in component_medians.tolist()
                ],
                "worst_component_response_median": float(
                    component_medians.min().item()
                ),
                "response_effective_rank": effective_rank,
                "functional_winner_components": active_winners,
                "dominant_functional_winner_share": dominant_share,
                "analytic_conditioning_route_residual": path_residual,
            }
        )

    thresholds = config["success_thresholds"]
    checks = {
        "maximum_solver_normalized_residual": max(
            item["solver"]["maximum_normalized_residual"] for item in seed_results
        )
        <= float(thresholds["maximum_solver_normalized_residual"]),
        "maximum_coarse_reference_relative_l2": max(
            item["discretization_relative_l2"]["maximum"] for item in seed_results
        )
        <= float(thresholds["maximum_coarse_reference_relative_l2"]),
        "minimum_median_nonlinear_departure": min(
            item["nonlinear_departure_relative_l2"]["median"] for item in seed_results
        )
        >= float(thresholds["minimum_median_nonlinear_departure"]),
        "minimum_worst_component_response_median": min(
            item["worst_component_response_median"] for item in seed_results
        )
        >= float(thresholds["minimum_worst_component_response_median"]),
        "minimum_response_effective_rank": min(
            item["response_effective_rank"] for item in seed_results
        )
        >= float(thresholds["minimum_response_effective_rank"]),
        "minimum_functional_winner_components": min(
            item["functional_winner_components"] for item in seed_results
        )
        >= int(thresholds["minimum_functional_winner_components"]),
        "maximum_dominant_functional_winner_share": max(
            item["dominant_functional_winner_share"] for item in seed_results
        )
        <= float(thresholds["maximum_dominant_functional_winner_share"]),
        "maximum_analytic_conditioning_route_residual": max(
            item["analytic_conditioning_route_residual"] for item in seed_results
        )
        <= float(thresholds["maximum_analytic_conditioning_route_residual"]),
    }
    all_converged = all(
        item[name]["converged"]
        for item in seed_results
        for name in ("solver", "reference_solver", "linear_solver", "paired_solver")
    )
    checks["all_solver_batches_converged"] = all_converged
    passed = all(checks.values())
    return {
        "schema_version": "aurora.nonlinear_pde_n0.result.v1",
        "experiment_id": config["experiment_id"],
        "stage": config["stage"],
        "seeds": seed_results,
        "aggregate": {
            "checks": checks,
            "failed_checks": [name for name, value in checks.items() if not value],
            "gate_passed": passed,
        },
        "decision": {
            "n1_model_and_strong_baseline_registration_authorized": passed,
            "irregular_3d_headline_authorized": False,
            "method_novelty_established": False,
            "next_step": (
                "Preregister N1 learned nonlinear comparison with strong baselines."
                if passed
                else "Redesign or repair the PDE/solver before any N1 learning."
            ),
        },
        "interpretation": (
            "N0 audits numerical accuracy, nonlinear and multicomponent response, "
            "functional diversity, and analytic conditioning. A pass is necessary "
            "for N1 but is not learned performance or method novelty."
        ),
    }


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
        " ".join(shlex.quote(value) for value in sys.argv) + "\n", encoding="utf-8"
    )
    (args.output / "git_commit.txt").write_text(args.git_commit + "\n", encoding="utf-8")
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
                "gate_passed": result["aggregate"]["gate_passed"],
                "n1_registration_authorized": result["decision"][
                    "n1_model_and_strong_baseline_registration_authorized"
                ],
                "irregular_3d_headline_authorized": False,
            },
        )
        return 0
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
