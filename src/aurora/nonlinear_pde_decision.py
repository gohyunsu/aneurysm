"""Prospective N1 contract for route-consistent functional decisions.

The learned experiment is implemented behind this validator.  Keeping contract
validation separate makes it impossible to silently turn numerical N0r
adequacy into a learned-method or irregular-3D claim.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


class NonlinearDecisionError(RuntimeError):
    """Raised when the frozen N1 decision contract is not honored."""


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_keys(payload: Mapping[str, Any], keys: Sequence[str], label: str) -> None:
    missing = sorted(set(keys) - set(payload))
    if missing:
        raise NonlinearDecisionError(f"{label} is missing keys: {missing}")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate the pre-outcome N1 learned-comparison contract."""

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
            "source_result_commit",
            "paper_identity",
            "claims_excluded",
            "pde_contract",
            "data",
            "model_seeds",
            "architecture",
            "training",
            "observation_protocol",
            "mandatory_models",
            "paired_controls",
            "evaluation",
            "success_rule",
            "theory_scope",
            "interpretation",
        ],
        "N1 config",
    )
    if payload["schema_version"] != "aurora.nonlinear_pde_n1.v1":
        raise NonlinearDecisionError("Unexpected N1 schema version.")
    if payload["status"] != "preregistered_before_n1_development_or_test_outcome":
        raise NonlinearDecisionError("N1 must remain prospective before test outcome.")
    if payload["source_gate"] != "N0r":
        raise NonlinearDecisionError("N1 must follow the passed N0r gate.")

    source_result = (config_path.parent / payload["source_result"]).resolve()
    if (
        not source_result.is_file()
        or _sha256(source_result) != payload["source_result_sha256"]
    ):
        raise NonlinearDecisionError("Pinned passed N0r result does not match N1.")
    if payload["source_result_commit"] != (
        "3c9e165483791da040f665b551494872a57615bd"
    ):
        raise NonlinearDecisionError("N1 must pin the exact public N0r result commit.")

    excluded = set(payload["claims_excluded"])
    required_exclusions = {
        "active_feature_acquisition_is_novel",
        "functional_optimization_with_neural_operators_is_novel",
        "generic_regret_bounds_are_novel",
        "analytic_gaussian_mixture_conditioning_is_novel",
        "paired_residual_learning_is_novel",
        "gnn_attention_or_low_rank_decoder_is_novel",
        "nonlinear_n0r_pass_is_learned_method_evidence",
        "aneurysm_or_irregular_3d_claim",
    }
    if excluded != required_exclusions:
        raise NonlinearDecisionError("N1 prior-art claim exclusions changed.")

    pde = payload["pde_contract"]
    if (
        pde["source"] != "nonlinear_pde_n0r.json"
        or int(pde["grid_points"]) != 33
        or int(pde["context_dim"]) != 5
        or int(pde["boundary_components"]) != 8
        or pde["solver_and_boundary_law_unchanged"] is not True
    ):
        raise NonlinearDecisionError("N1 must retain the passed N0r PDE contract.")

    data = payload["data"]
    expected_sizes = {
        "density_train_contexts": 3072,
        "density_validation_contexts": 384,
        "density_conditions_per_context": 8,
        "operator_train_contexts": 768,
        "operator_validation_contexts": 192,
        "operator_test_contexts": 192,
        "operator_conditions_per_context": 12,
        "acquisition_test_contexts": 48,
    }
    for key, expected in expected_sizes.items():
        if int(data[key]) != expected:
            raise NonlinearDecisionError(f"N1 data size changed: {key}.")
    if data["test_access"] != "after_all_model_selection_and_checkpoint_freeze":
        raise NonlinearDecisionError("N1 test access must follow checkpoint freeze.")
    if data["hidden_law_shift"]["allowed_claim"] != "detection_and_abstention_only":
        raise NonlinearDecisionError("Hidden-law shift cannot claim calibrated recovery.")

    seeds = payload["model_seeds"]
    development = [int(seed) for seed in seeds["development_only"]]
    confirmatory = [int(seed) for seed in seeds["confirmatory"]]
    if development != [73080501, 73080502]:
        raise NonlinearDecisionError("N1 development seeds changed.")
    if confirmatory != [73080511, 73080512, 73080513, 73080514, 73080515]:
        raise NonlinearDecisionError("N1 confirmatory seeds changed.")
    if set(development) & set(confirmatory):
        raise NonlinearDecisionError("Development and confirmatory seeds overlap.")
    if (
        seeds["development_may_change_thresholds_or_test_protocol"] is not False
        or seeds["development_may_access_test"] is not False
    ):
        raise NonlinearDecisionError("Development cannot tune the test contract.")

    masks = payload["observation_protocol"]
    if masks["registered_masks"] != {
        "missing": [],
        "sparse_2": [0, 2],
        "partial_4": [0, 2, 5, 7],
        "full": [0, 1, 2, 3, 4, 5, 6, 7],
    }:
        raise NonlinearDecisionError("N1 registered masks changed.")
    if masks["route_test"] != {
        "initial": [0, 2],
        "final": [0, 2, 5, 7],
        "routes": [
            "direct_final",
            "sequential_5_then_7",
            "sequential_7_then_5",
        ],
    }:
        raise NonlinearDecisionError("N1 route test changed.")

    model_ids = {item["id"] for item in payload["mandatory_models"]}
    required_models = {
        "aurora_joint",
        "conditional_mean_imputation",
        "independent_mask_heads",
        "lano_adapted",
        "nop_adapted",
        "generic_probabilistic_operator",
        "acflow_adapted",
        "aco_ceiling",
        "nots_adapted",
    }
    if model_ids != required_models:
        raise NonlinearDecisionError("N1 mandatory strong-baseline set changed.")
    nots = next(
        item for item in payload["mandatory_models"] if item["id"] == "nots_adapted"
    )
    if nots.get("not_a_reproduction") is not True:
        raise NonlinearDecisionError("NOTS adaptation cannot be called a reproduction.")

    success = payload["success_rule"]
    if (
        success["all_conditions_required"] is not True
        or float(success[
            "primary_relative_improvement_over_strongest_validation_selected_non_oracle_minimum"
        ])
        != 0.05
        or int(success["confirmatory_seed_direction_minimum"]) != 4
        or int(success["confirmatory_seeds_total"]) != 5
        or success["field_distribution_and_acquisition_regret_must_both_improve"]
        is not True
        or success["aco_is_ceiling_not_competitor_for_superiority"] is not True
        or success["n1_pass_authorizes_irregular_3d_protocol_registration_only"]
        is not True
        or success["n1_pass_does_not_establish_cross_domain_or_aaai_acceptance"]
        is not True
    ):
        raise NonlinearDecisionError("N1 non-inflation decision rule changed.")
    return payload


def _imports() -> tuple[Any, Any]:
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server environment
        raise NonlinearDecisionError("N1 implementation requires numpy and torch.") from exc
    return np, torch


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def sample_contexts(
    count: int,
    seed: int,
    *,
    lower: float,
    upper: float,
    device: Any,
    dtype: Any,
) -> Any:
    """Sample a geometry/context family from the registered ID hypercube."""

    _, torch = _imports()
    generator = torch.Generator(device="cpu").manual_seed(seed)
    context = lower + (upper - lower) * torch.rand(
        count, 5, generator=generator
    )
    return context.to(device=device, dtype=dtype)


def sample_truncated_boundary(
    weights: Any,
    means: Any,
    covariances: Any,
    *,
    samples: int,
    seed: int,
    minimum_radius: float,
    maximum_radius: float,
) -> Any:
    """Sample the registered GMM within a latent Mahalanobis-radius contract."""

    _, torch = _imports()
    if not 0.0 <= minimum_radius < maximum_radius:
        raise NonlinearDecisionError("Invalid boundary latent-radius interval.")
    generator = torch.Generator(device="cpu").manual_seed(seed)
    batch, mixtures, dimension = means.shape
    if mixtures != 2 or dimension != 8:
        raise NonlinearDecisionError("N1 expects a two-component 8D boundary GMM.")

    uniforms = torch.rand(batch, samples, generator=generator).to(weights.device)
    component = (uniforms > weights[:, 0:1]).long()
    standard = torch.empty(batch, samples, dimension)
    accepted = torch.zeros(batch, samples, dtype=torch.bool)
    attempts = 0
    while not bool(accepted.all()):
        attempts += 1
        if attempts > 10000:
            raise NonlinearDecisionError("Boundary latent rejection sampling stalled.")
        proposal = torch.randn(batch, samples, dimension, generator=generator)
        radius = torch.linalg.vector_norm(proposal, dim=-1)
        valid = (
            (~accepted)
            & (radius >= minimum_radius)
            & (radius <= maximum_radius)
        )
        standard[valid] = proposal[valid]
        accepted |= valid
    standard = standard.to(device=means.device, dtype=means.dtype)

    cholesky = torch.linalg.cholesky(covariances)
    selected_mean = torch.gather(
        means[:, None].expand(-1, samples, -1, -1),
        2,
        component[:, :, None, None].expand(-1, -1, 1, dimension),
    ).squeeze(2)
    selected_cholesky = torch.gather(
        cholesky[:, None].expand(-1, samples, -1, -1, -1),
        2,
        component[:, :, None, None, None].expand(
            -1, -1, 1, dimension, dimension
        ),
    ).squeeze(2)
    return selected_mean + torch.einsum(
        "bsij,bsj->bsi", selected_cholesky, standard
    )


def generate_boundary_split(
    *,
    contexts: int,
    conditions: int,
    context_seed: int,
    boundary_seed: int,
    context_support: Sequence[float],
    maximum_radius: float,
    device: Any,
) -> dict[str, Any]:
    """Generate a density-only family without invoking the PDE solver."""

    _, torch = _imports()
    from aurora.nonlinear_pde import boundary_law

    context = sample_contexts(
        contexts,
        context_seed,
        lower=float(context_support[0]),
        upper=float(context_support[1]),
        device=device,
        dtype=torch.float32,
    )
    weights, means, covariances = boundary_law(context)
    boundary = sample_truncated_boundary(
        weights,
        means,
        covariances,
        samples=conditions,
        seed=boundary_seed,
        minimum_radius=0.0,
        maximum_radius=maximum_radius,
    )
    return {
        "context": context,
        "boundary": boundary,
        "true_weights": weights,
        "true_means": means,
        "true_covariances": covariances,
    }


def generate_solution_split(
    *,
    contexts: int,
    conditions: int,
    context_seed: int,
    boundary_seed: int,
    context_support: Sequence[float],
    maximum_radius: float,
    solver_config: Mapping[str, Any],
    device: Any,
    solver_batch_size: int = 512,
) -> dict[str, Any]:
    """Generate a geometry-family split and solve every registered full BC."""

    _, torch = _imports()
    from aurora.nonlinear_pde import (
        boundary_law,
        solution_functionals,
        solve_semilinear,
    )

    context = sample_contexts(
        contexts,
        context_seed,
        lower=float(context_support[0]),
        upper=float(context_support[1]),
        device=device,
        dtype=torch.float32,
    )
    weights, means, covariances = boundary_law(context)
    boundary = sample_truncated_boundary(
        weights,
        means,
        covariances,
        samples=conditions,
        seed=boundary_seed,
        minimum_radius=0.0,
        maximum_radius=maximum_radius,
    )
    expanded_context = context[:, None].expand(-1, conditions, -1).reshape(-1, 5)
    flat_boundary = boundary.reshape(-1, 8)
    fields = []
    solver_summaries = []
    pde = solver_config["pde"]
    for start in range(0, flat_boundary.shape[0], solver_batch_size):
        end = min(start + solver_batch_size, flat_boundary.shape[0])
        field, summary = solve_semilinear(
            expanded_context[start:end],
            flat_boundary[start:end],
            grid_points=int(pde["grid_points"]),
            maximum_iterations=int(pde["maximum_iterations"]),
            tolerance=float(pde["convergence_tolerance"]),
            check_interval=int(pde["residual_check_interval"]),
            relaxation=float(pde["relaxation"]),
        )
        if not summary["converged"]:
            raise NonlinearDecisionError("N1 solution split contains a failed solve.")
        fields.append(field)
        solver_summaries.append(summary)
    flat_field = torch.cat(fields, dim=0)
    functionals = solution_functionals(flat_field, expanded_context)
    return {
        "context": context,
        "boundary": boundary,
        "field": flat_field.reshape(
            contexts,
            conditions,
            int(pde["grid_points"]),
            int(pde["grid_points"]),
        ),
        "functionals": functionals.reshape(contexts, conditions, -1),
        "solver": {
            "batches": len(solver_summaries),
            "all_converged": all(item["converged"] for item in solver_summaries),
            "maximum_normalized_residual": max(
                item["maximum_normalized_residual"] for item in solver_summaries
            ),
            "maximum_iterations": max(
                int(item["iterations"]) for item in solver_summaries
            ),
        },
    }


def _build_mlp(torch: Any, dimensions: Sequence[int]) -> Any:
    layers = []
    for index, (first, second) in enumerate(zip(dimensions[:-1], dimensions[1:])):
        layers.append(torch.nn.Linear(first, second))
        if index + 2 < len(dimensions):
            layers.append(torch.nn.SiLU())
    return torch.nn.Sequential(*layers)


def _covariance_from_raw(raw: Any, dimension: int) -> Any:
    """Convert packed lower-triangle values into a stable full covariance."""

    _, torch = _imports()
    batch_shape = raw.shape[:-1]
    lower = torch.zeros(
        *batch_shape,
        dimension,
        dimension,
        device=raw.device,
        dtype=raw.dtype,
    )
    row, column = torch.tril_indices(dimension, dimension, device=raw.device)
    lower[..., row, column] = raw
    diagonal = torch.arange(dimension, device=raw.device)
    lower[..., diagonal, diagonal] = (
        torch.nn.functional.softplus(lower[..., diagonal, diagonal]) + 1e-3
    )
    return lower @ lower.transpose(-2, -1)


def build_joint_density(config: Mapping[str, Any], device: Any) -> Any:
    """Build the context-conditioned two-component full-covariance GMM."""

    _, torch = _imports()
    contract = config["architecture"]["boundary_density"]
    width = int(contract["hidden_width"])
    layers = int(contract["hidden_layers"])
    dimension, mixtures = 8, 2
    triangle = dimension * (dimension + 1) // 2
    output = mixtures + mixtures * dimension + mixtures * triangle

    class JointBoundaryDensity(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = _build_mlp(
                torch, [5, *([width] * layers), output]
            )

        def forward(self, context: Any) -> tuple[Any, Any, Any]:
            raw = self.net(context)
            logits = raw[:, :mixtures]
            offset = mixtures
            means = raw[:, offset : offset + mixtures * dimension].reshape(
                -1, mixtures, dimension
            )
            offset += mixtures * dimension
            covariance = _covariance_from_raw(
                raw[:, offset:].reshape(-1, mixtures, triangle), dimension
            )
            return torch.softmax(logits, dim=-1), means, covariance

    return JointBoundaryDensity().to(device)


def _coordinate_features(grid_points: int, device: Any) -> tuple[Any, Any]:
    _, torch = _imports()
    coordinate = torch.linspace(0.0, 1.0, grid_points, device=device)
    yy, xx = torch.meshgrid(coordinate, coordinate, indexing="ij")
    features = [xx, yy]
    for frequency in (1.0, 2.0, 3.0, 4.0):
        features.extend(
            (
                torch.sin(math.pi * frequency * xx),
                torch.cos(math.pi * frequency * xx),
                torch.sin(math.pi * frequency * yy),
                torch.cos(math.pi * frequency * yy),
            )
        )
    envelope = xx * (1.0 - xx) * yy * (1.0 - yy)
    return torch.stack(features, dim=-1).reshape(-1, len(features)), envelope


def build_solution_operator(config: Mapping[str, Any], device: Any) -> Any:
    """Build the exact-Dirichlet-lifted low-rank coordinate operator."""

    _, torch = _imports()
    from aurora.nonlinear_pde import _boundary_field

    contract = config["architecture"]["conditional_solution_operator"]
    width = int(contract["branch_width"])
    branch_layers = int(contract["branch_layers"])
    coordinate_width = int(contract["coordinate_width"])
    coordinate_layers = int(contract["coordinate_layers"])
    rank = int(contract["rank"])
    grid_points = int(config["pde_contract"]["grid_points"])
    coordinate, envelope = _coordinate_features(grid_points, device)

    class LiftedCoordinateOperator(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.branch = _build_mlp(
                torch, [13, *([width] * branch_layers), rank]
            )
            self.trunk = _build_mlp(
                torch,
                [
                    coordinate.shape[-1],
                    *([coordinate_width] * coordinate_layers),
                    rank,
                ],
            )
            self.register_buffer("coordinate", coordinate)
            self.register_buffer("envelope", envelope)

        def forward(self, context: Any, boundary: Any) -> Any:
            coefficient = self.branch(torch.cat((context, boundary), dim=-1))
            basis = self.trunk(self.coordinate)
            correction = torch.einsum(
                "br,nr->bn", coefficient, basis
            ) / math.sqrt(rank)
            correction = correction * self.envelope
            lifting = _boundary_field(boundary, grid_points).flatten(1)
            return (lifting + correction).reshape(
                boundary.shape[0], grid_points, grid_points
            )

    return LiftedCoordinateOperator().to(device)


def gmm_nll(
    weights: Any,
    means: Any,
    covariances: Any,
    value: Any,
) -> Any:
    """Negative log likelihood for a batched full-covariance mixture."""

    _, torch = _imports()
    dimension = value.shape[-1]
    eye = torch.eye(dimension, device=value.device, dtype=value.dtype)
    cholesky = torch.linalg.cholesky(covariances + 1e-5 * eye)
    residual = value[:, None, :] - means
    solved = torch.cholesky_solve(residual.unsqueeze(-1), cholesky).squeeze(-1)
    mahalanobis = torch.sum(residual * solved, dim=-1)
    logdet = 2.0 * torch.log(
        torch.diagonal(cholesky, dim1=-2, dim2=-1)
    ).sum(-1)
    log_density = -0.5 * (
        mahalanobis + logdet + dimension * math.log(2.0 * math.pi)
    )
    return -torch.logsumexp(
        torch.log(weights.clamp_min(1e-12)) + log_density, dim=-1
    )


def _clone_state(module: Any) -> dict[str, Any]:
    return {
        key: value.detach().cpu().clone()
        for key, value in module.state_dict().items()
    }


def _flatten_solution_split(split: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    contexts, conditions = split["boundary"].shape[:2]
    context = split["context"][:, None].expand(-1, conditions, -1).reshape(-1, 5)
    boundary = split["boundary"].reshape(-1, 8)
    field = split["field"].reshape(
        contexts * conditions, split["field"].shape[-2], split["field"].shape[-1]
    )
    return context, boundary, field


def _relative_l2(prediction: Any, target: Any) -> Any:
    _, torch = _imports()
    numerator = torch.linalg.vector_norm((prediction - target).flatten(1), dim=1)
    denominator = torch.linalg.vector_norm(target.flatten(1), dim=1).clamp_min(1e-6)
    return numerator / denominator


def train_core_development(
    *,
    config: Mapping[str, Any],
    density_train: Mapping[str, Any],
    density_validation: Mapping[str, Any],
    operator_train: Mapping[str, Any],
    operator_validation: Mapping[str, Any],
    seed: int,
) -> tuple[Any, Any, dict[str, Any]]:
    """Train only the coherent N1 core without generating or reading test data."""

    _, torch = _imports()
    torch.manual_seed(seed)
    device = density_train["context"].device
    density = build_joint_density(config, device)
    operator = build_solution_operator(config, device)

    density_context = density_train["context"][:, None].expand(
        -1, density_train["boundary"].shape[1], -1
    ).reshape(-1, 5)
    density_boundary = density_train["boundary"].reshape(-1, 8)
    validation_density_context = density_validation["context"][:, None].expand(
        -1, density_validation["boundary"].shape[1], -1
    ).reshape(-1, 5)
    validation_density_boundary = density_validation["boundary"].reshape(-1, 8)

    density_contract = config["training"]["density"]
    density_optimizer = torch.optim.AdamW(
        density.parameters(),
        lr=float(density_contract["learning_rate"]),
        weight_decay=float(density_contract["weight_decay"]),
    )
    density_generator = torch.Generator(device=device).manual_seed(seed + 101)
    density_batch = int(density_contract["batch_size"])
    density_best = math.inf
    density_state = _clone_state(density)
    density_best_epoch = 0
    density_wait = 0
    density_trace = []
    for epoch in range(1, int(density_contract["maximum_epochs"]) + 1):
        index = torch.randint(
            0,
            density_context.shape[0],
            (density_batch,),
            generator=density_generator,
            device=device,
        )
        weights, means, covariances = density(density_context[index])
        loss = gmm_nll(
            weights, means, covariances, density_boundary[index]
        ).mean()
        density_optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(density.parameters(), 5.0)
        density_optimizer.step()
        if epoch % int(density_contract["validation_interval"]) != 0:
            continue
        density.eval()
        with torch.no_grad():
            validation_values = []
            for start in range(0, validation_density_context.shape[0], 4096):
                end = min(start + 4096, validation_density_context.shape[0])
                weights, means, covariances = density(
                    validation_density_context[start:end]
                )
                validation_values.append(
                    gmm_nll(
                        weights,
                        means,
                        covariances,
                        validation_density_boundary[start:end],
                    )
                )
            validation_loss = float(torch.cat(validation_values).mean().item())
        density.train()
        density_trace.append(
            {
                "epoch": epoch,
                "train_nll": float(loss.detach().item()),
                "validation_nll": validation_loss,
            }
        )
        if validation_loss < density_best - 1e-5:
            density_best = validation_loss
            density_state = _clone_state(density)
            density_best_epoch = epoch
            density_wait = 0
        else:
            density_wait += 1
        if density_wait >= int(density_contract["early_stopping_patience"]):
            break
    density.load_state_dict(density_state)
    density.eval()

    train_context, train_boundary, train_field = _flatten_solution_split(operator_train)
    validation_context, validation_boundary, validation_field = (
        _flatten_solution_split(operator_validation)
    )
    operator_contract = config["training"]["operator"]
    operator_optimizer = torch.optim.AdamW(
        operator.parameters(),
        lr=float(operator_contract["learning_rate"]),
        weight_decay=float(operator_contract["weight_decay"]),
    )
    operator_generator = torch.Generator(device=device).manual_seed(seed + 202)
    operator_batch = int(operator_contract["batch_size"])
    pair_weight = float(operator_contract["paired_response_weight"])
    operator_best = math.inf
    operator_state = _clone_state(operator)
    operator_best_epoch = 0
    operator_wait = 0
    operator_trace = []
    train_conditions = operator_train["boundary"].shape[1]
    family_batch = min(256, operator_train["context"].shape[0])
    for epoch in range(1, int(operator_contract["maximum_epochs"]) + 1):
        index = torch.randint(
            0,
            train_context.shape[0],
            (operator_batch,),
            generator=operator_generator,
            device=device,
        )
        prediction = operator(train_context[index], train_boundary[index])
        field_loss = torch.mean((prediction - train_field[index]).square())

        family_index = torch.randint(
            0,
            operator_train["context"].shape[0],
            (family_batch,),
            generator=operator_generator,
            device=device,
        )
        first = (epoch - 1) % train_conditions
        second = epoch % train_conditions
        pair_context = operator_train["context"][family_index]
        first_boundary = operator_train["boundary"][family_index, first]
        second_boundary = operator_train["boundary"][family_index, second]
        predicted_delta = operator(pair_context, second_boundary) - operator(
            pair_context, first_boundary
        )
        true_delta = (
            operator_train["field"][family_index, second]
            - operator_train["field"][family_index, first]
        )
        pair_loss = torch.mean((predicted_delta - true_delta).square())
        loss = field_loss + pair_weight * pair_loss
        operator_optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(operator.parameters(), 5.0)
        operator_optimizer.step()
        if epoch % int(operator_contract["validation_interval"]) != 0:
            continue
        operator.eval()
        with torch.no_grad():
            relative = []
            for start in range(0, validation_context.shape[0], 1024):
                end = min(start + 1024, validation_context.shape[0])
                relative.append(
                    _relative_l2(
                        operator(
                            validation_context[start:end],
                            validation_boundary[start:end],
                        ),
                        validation_field[start:end],
                    )
                )
            validation_relative = torch.cat(relative).mean()
            validation_pair_prediction = operator(
                operator_validation["context"],
                operator_validation["boundary"][:, 1],
            ) - operator(
                operator_validation["context"],
                operator_validation["boundary"][:, 0],
            )
            validation_pair_target = (
                operator_validation["field"][:, 1]
                - operator_validation["field"][:, 0]
            )
            validation_pair_relative = _relative_l2(
                validation_pair_prediction, validation_pair_target
            ).mean()
            validation_objective = float(
                (validation_relative + pair_weight * validation_pair_relative).item()
            )
        operator.train()
        operator_trace.append(
            {
                "epoch": epoch,
                "train_field_mse": float(field_loss.detach().item()),
                "train_pair_mse": float(pair_loss.detach().item()),
                "validation_full_bc_relative_l2": float(
                    validation_relative.item()
                ),
                "validation_paired_response_relative_l2": float(
                    validation_pair_relative.item()
                ),
                "validation_selection_objective": validation_objective,
            }
        )
        if validation_objective < operator_best - 1e-5:
            operator_best = validation_objective
            operator_state = _clone_state(operator)
            operator_best_epoch = epoch
            operator_wait = 0
        else:
            operator_wait += 1
        if operator_wait >= int(operator_contract["early_stopping_patience"]):
            break
    operator.load_state_dict(operator_state)
    operator.eval()
    return density, operator, {
        "stage": "validation_only_core_development",
        "test_generated_or_accessed": False,
        "seed": seed,
        "density": {
            "best_epoch": density_best_epoch,
            "best_validation_nll": density_best,
            "epochs_executed": density_trace[-1]["epoch"],
            "trace": density_trace,
        },
        "operator": {
            "best_epoch": operator_best_epoch,
            "best_validation_objective": operator_best,
            "epochs_executed": operator_trace[-1]["epoch"],
            "trace": operator_trace,
        },
        "parameter_counts": {
            "joint_boundary_density": sum(
                parameter.numel() for parameter in density.parameters()
            ),
            "lifted_solution_operator": sum(
                parameter.numel() for parameter in operator.parameters()
            ),
        },
        "claim_status": {
            "n1_gate_decided": False,
            "baseline_superiority_established": False,
            "method_novelty_established": False,
            "irregular_3d_authorized": False,
        },
    }
