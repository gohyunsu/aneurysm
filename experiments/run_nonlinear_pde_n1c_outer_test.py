"""Run the single preregistered N1c nonlinear-PDE outer test."""

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
from typing import Any, Callable, Mapping, Sequence

from aurora.nonlinear_pde import boundary_law, solution_functionals, solve_semilinear
from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    build_deltaphi_residual_operator,
    build_independent_mask_density,
    build_joint_density,
    build_lano_completion,
    build_mask_conditional_density,
    build_pod_probabilistic_operator,
    build_solution_operator,
    generate_solution_split,
    load_n1c_config,
    nearest_training_indices,
    pod_representation_error,
)
from aurora.nonlinear_pde_evaluation import (
    aggregate_context,
    bounded_action_risk,
    bounded_bayes_action,
    checkpoint_state_dict,
    complete_boundary_samples,
    conditional_posterior_from_joint,
    context_bootstrap_interval,
    direct_mask_posterior,
    empirical_one_wasserstein,
    functional_coverage,
    functional_energy_score,
    mask_tensor,
    posterior_mean_completion,
    representation_from_checkpoint,
    sample_radius_truncated_conditional_gmm,
    sequential_mask_posterior,
    standardize_functionals,
)


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _relative_l2(prediction: Any, target: Any) -> Any:
    import torch

    return torch.linalg.vector_norm((prediction - target).flatten(1), dim=1) / (
        torch.linalg.vector_norm(target.flatten(1), dim=1).clamp_min(1e-6)
    )


def _flatten_split(split: Mapping[str, Any]) -> tuple[Any, Any, Any, Any]:
    contexts, conditions = split["boundary"].shape[:2]
    context = split["context"][:, None].expand(-1, conditions, -1).reshape(-1, 5)
    return (
        context,
        split["boundary"].reshape(-1, 8),
        split["field"].reshape(
            contexts * conditions,
            split["field"].shape[-2],
            split["field"].shape[-1],
        ),
        split["functionals"].reshape(contexts * conditions, -1),
    )


def _solve_functionals(
    context: Any,
    boundary: Any,
    *,
    n0_config: Mapping[str, Any],
    batch_size: int = 512,
) -> tuple[Any, dict[str, Any]]:
    import torch

    pde = n0_config["pde"]
    fields = []
    summaries = []
    for start in range(0, context.shape[0], batch_size):
        end = min(start + batch_size, context.shape[0])
        with torch.no_grad():
            field, summary = solve_semilinear(
                context[start:end],
                boundary[start:end],
                grid_points=int(pde["grid_points"]),
                maximum_iterations=int(pde["maximum_iterations"]),
                tolerance=float(pde["convergence_tolerance"]),
                check_interval=int(pde["residual_check_interval"]),
                relaxation=float(pde["relaxation"]),
            )
        if not summary["converged"]:
            raise NonlinearDecisionError("N1c oracle solve did not converge.")
        fields.append(field)
        summaries.append(summary)
    with torch.no_grad():
        field = torch.cat(fields)
        functionals = solution_functionals(field, context)
    return functionals, {
        "batches": len(summaries),
        "all_converged": True,
        "maximum_normalized_residual": max(
            item["maximum_normalized_residual"] for item in summaries
        ),
        "maximum_iterations": max(int(item["iterations"]) for item in summaries),
    }


def _operator_functionals(
    operator: Any,
    context: Any,
    boundary_samples: Any,
    *,
    chunk_size: int = 8192,
) -> Any:
    import torch

    batch, samples = boundary_samples.shape[:2]
    expanded_context = context[:, None].expand(-1, samples, -1).reshape(-1, 5)
    flat_boundary = boundary_samples.reshape(-1, 8)
    values = []
    for start in range(0, flat_boundary.shape[0], chunk_size):
        end = min(start + chunk_size, flat_boundary.shape[0])
        field = operator(expanded_context[start:end], flat_boundary[start:end])
        values.append(solution_functionals(field, expanded_context[start:end]))
    return torch.cat(values).reshape(batch, samples, -1)


def _direct_functionals(
    model: Any,
    context: Any,
    boundary: Any,
    positions: Sequence[int],
    *,
    samples: int,
    seed: int,
) -> tuple[Any, Any]:
    import torch

    mask = mask_tensor(
        positions,
        context.shape[0],
        device=context.device,
        dtype=context.dtype,
    )
    field = model.sample(context, boundary, mask, samples=samples, seed=seed)
    expanded_context = context[:, None].expand(-1, samples, -1).reshape(-1, 5)
    functionals = solution_functionals(
        field.reshape(-1, field.shape[-2], field.shape[-1]),
        expanded_context,
    ).reshape(context.shape[0], samples, -1)
    return field, functionals


def _load_models(
    n1_config: Mapping[str, Any],
    manifest_seed: Mapping[str, Any],
    checkpoint_directory: Path,
    device: Any,
) -> dict[str, Any]:
    checkpoints = manifest_seed["checkpoint_sha256"]
    representation = representation_from_checkpoint(
        checkpoint_directory / "train_only_pod_representation.pt",
        manifest_seed.get(
            "pod_sha256",
            "42e3bb2fac20315d18f35d8e1c16ffd09dd4e8a98283c9a80b13230271e37326",
        ),
        device,
    )
    models = {
        "aurora_joint": build_joint_density(n1_config, device),
        "independent_mask_heads": build_independent_mask_density(n1_config, device),
        "lano_adapted": build_lano_completion(n1_config, device),
        "acflow_adapted": build_mask_conditional_density(n1_config, device),
        "aurora_shared_operator_pair_loss": build_solution_operator(
            n1_config, device
        ),
        "aurora_shared_operator_pair_loss_zero": build_solution_operator(
            n1_config, device
        ),
        "aurora_shared_operator_random_cross_context_pair": build_solution_operator(
            n1_config, device
        ),
        "generic_probabilistic_operator": build_pod_probabilistic_operator(
            n1_config,
            device,
            representation=representation,
            set_encoder=False,
        ),
        "nop_adapted": build_pod_probabilistic_operator(
            n1_config,
            device,
            representation=representation,
            set_encoder=True,
        ),
        "deltaphi_style_residual": build_deltaphi_residual_operator(
            n1_config,
            device,
            representation=representation,
        ),
    }
    file_names = {
        "aurora_joint": "aurora_joint_density",
        "independent_mask_heads": "independent_mask_heads",
        "lano_adapted": "lano_adapted_completion",
        "acflow_adapted": "acflow_adapted_completion",
        "aurora_shared_operator_pair_loss": "aurora_shared_operator_pair_loss",
        "aurora_shared_operator_pair_loss_zero": (
            "aurora_shared_operator_pair_loss_zero"
        ),
        "aurora_shared_operator_random_cross_context_pair": (
            "aurora_shared_operator_random_cross_context_pair"
        ),
        "generic_probabilistic_operator": "generic_probabilistic_operator",
        "nop_adapted": "nop_adapted",
        "deltaphi_style_residual": "deltaphi_style_residual",
    }
    for model_name, artifact_name in file_names.items():
        state = checkpoint_state_dict(
            checkpoint_directory / f"{artifact_name}.pt",
            checkpoints[artifact_name],
            device,
        )
        models[model_name].load_state_dict(state)
        models[model_name].eval()
    models["representation"] = representation
    return models


def _completion_samples(
    model_name: str,
    models: Mapping[str, Any],
    context: Any,
    boundary: Any,
    positions: Sequence[int],
    *,
    samples: int,
    seed: int,
) -> Any:
    if len(positions) == 8:
        return boundary[:, None].expand(-1, samples, -1)
    mask = mask_tensor(
        positions,
        context.shape[0],
        device=context.device,
        dtype=context.dtype,
    )
    if model_name == "aurora_joint":
        posterior = conditional_posterior_from_joint(
            *models[model_name](context),
            boundary,
            positions,
        )
    elif model_name == "independent_mask_heads":
        registered_name = {
            (): "missing",
            (0, 2): "sparse_2",
            (0, 2, 5, 7): "partial_4",
            tuple(range(8)): "full",
        }[tuple(positions)]
        posterior = direct_mask_posterior(
            *models[model_name](registered_name, context, boundary, mask),
            positions,
        )
    elif model_name == "acflow_adapted":
        posterior = direct_mask_posterior(
            *models[model_name](context, boundary, mask),
            positions,
        )
    elif model_name == "lano_adapted":
        return models[model_name].sample(
            context,
            boundary,
            mask,
            samples=samples,
            seed=seed,
        )
    else:
        raise NonlinearDecisionError(f"Unknown completion model: {model_name}.")
    return complete_boundary_samples(
        posterior,
        boundary,
        positions,
        samples=samples,
        seed=seed,
    )


def _evaluate_id_distribution(
    n1c: Mapping[str, Any],
    models: Mapping[str, Any],
    test: Mapping[str, Any],
    functional_location: Any,
    functional_scale: Any,
    *,
    seed_index: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    import torch

    contexts = int(n1c["test_lock"]["operator_test_contexts"])
    conditions = int(n1c["test_lock"]["conditions_per_context"])
    samples = int(
        n1c["id_distribution_evaluation"]["field_distribution_samples"]
    )
    batch_size = int(n1c["id_distribution_evaluation"]["case_batch_size"])
    context, boundary, target_field, target_functional = _flatten_split(test)
    target_standard = standardize_functionals(
        target_functional, functional_location, functional_scale
    )
    masks = {
        **n1c["id_distribution_evaluation"]["primary_masks"],
        **n1c["id_distribution_evaluation"]["diagnostic_masks"],
    }
    learned = list(n1c["id_distribution_evaluation"]["probabilistic_models"])
    shared_operator = models["aurora_shared_operator_pair_loss"]
    aggregate = {}
    per_context = {}
    seed_base = int(n1c["randomness"]["field_distribution_base_seed"])
    seed_base += 100000 * seed_index
    for mask_name, positions in masks.items():
        aggregate[mask_name] = {}
        per_context[mask_name] = {}
        for model_index, model_name in enumerate(learned):
            energies = []
            coverages = []
            widths = []
            field_errors = []
            for start in range(0, context.shape[0], batch_size):
                end = min(start + batch_size, context.shape[0])
                draw_seed = seed_base + start
                if model_name in {
                    "generic_probabilistic_operator",
                    "nop_adapted",
                }:
                    field_samples, functional_samples = _direct_functionals(
                        models[model_name],
                        context[start:end],
                        boundary[start:end],
                        positions,
                        samples=samples,
                        seed=draw_seed,
                    )
                else:
                    boundary_samples = _completion_samples(
                        model_name,
                        models,
                        context[start:end],
                        boundary[start:end],
                        positions,
                        samples=samples,
                        seed=draw_seed,
                    )
                    flat_context = context[start:end, None].expand(
                        -1, samples, -1
                    ).reshape(-1, 5)
                    flat_boundary = boundary_samples.reshape(-1, 8)
                    field_chunks = []
                    for chunk in range(0, flat_boundary.shape[0], 8192):
                        chunk_end = min(chunk + 8192, flat_boundary.shape[0])
                        field_chunks.append(
                            shared_operator(
                                flat_context[chunk:chunk_end],
                                flat_boundary[chunk:chunk_end],
                            )
                        )
                    field_samples = torch.cat(field_chunks).reshape(
                        end - start, samples, 33, 33
                    )
                    functional_samples = solution_functionals(
                        field_samples.reshape(-1, 33, 33),
                        flat_context,
                    ).reshape(end - start, samples, -1)
                standardized = standardize_functionals(
                    functional_samples,
                    functional_location,
                    functional_scale,
                )
                energies.append(
                    functional_energy_score(
                        standardized,
                        target_standard[start:end],
                    )
                )
                coverage, width = functional_coverage(
                    standardized,
                    target_standard[start:end],
                    probability=float(
                        n1c["functional_contract"]["coverage_probability"]
                    ),
                )
                coverages.append(coverage)
                widths.append(width)
                field_errors.append(
                    _relative_l2(
                        field_samples.mean(dim=1),
                        target_field[start:end],
                    )
                )
            energy = torch.cat(energies)
            coverage = torch.cat(coverages)
            width = torch.cat(widths)
            field_error = torch.cat(field_errors)
            context_energy = aggregate_context(energy, contexts, conditions)
            context_coverage = aggregate_context(coverage, contexts, conditions)
            context_width = aggregate_context(width, contexts, conditions)
            context_field = aggregate_context(field_error, contexts, conditions)
            aggregate[mask_name][model_name] = {
                "functional_energy_score": float(context_energy.mean().item()),
                "functional_coverage": context_coverage.mean(dim=0).tolist(),
                "functional_coverage_error_maximum": float(
                    torch.abs(
                        context_coverage.mean(dim=0)
                        - float(
                            n1c["functional_contract"]["coverage_probability"]
                        )
                    )
                    .max()
                    .item()
                ),
                "matched_coverage_interval_width": context_width.mean(dim=0).tolist(),
                "field_mean_relative_l2": float(context_field.mean().item()),
            }
            per_context[mask_name][model_name] = {
                "functional_energy_score": context_energy.detach().cpu().tolist(),
                "functional_coverage": context_coverage.detach().cpu().tolist(),
                "matched_coverage_interval_width": context_width.detach().cpu().tolist(),
                "field_mean_relative_l2": context_field.detach().cpu().tolist(),
            }

        mean_energies = []
        mean_field_errors = []
        for start in range(0, context.shape[0], batch_size):
            end = min(start + batch_size, context.shape[0])
            weights, means, covariances = models["aurora_joint"](
                context[start:end]
            )
            posterior = conditional_posterior_from_joint(
                weights,
                means,
                covariances,
                boundary[start:end],
                positions,
            )
            completed = posterior_mean_completion(
                posterior,
                boundary[start:end],
                positions,
            )
            prediction = shared_operator(context[start:end], completed)
            prediction_functional = solution_functionals(
                prediction, context[start:end]
            )
            prediction_standard = standardize_functionals(
                prediction_functional,
                functional_location,
                functional_scale,
            )
            mean_energies.append(
                torch.linalg.vector_norm(
                    prediction_standard - target_standard[start:end],
                    dim=-1,
                )
            )
            mean_field_errors.append(
                _relative_l2(prediction, target_field[start:end])
            )
        mean_energy = aggregate_context(
            torch.cat(mean_energies), contexts, conditions
        )
        mean_field = aggregate_context(
            torch.cat(mean_field_errors), contexts, conditions
        )
        aggregate[mask_name]["conditional_mean_imputation"] = {
            "functional_energy_score": float(mean_energy.mean().item()),
            "functional_coverage": None,
            "functional_coverage_error_maximum": None,
            "matched_coverage_interval_width": None,
            "field_mean_relative_l2": float(mean_field.mean().item()),
        }
        per_context[mask_name]["conditional_mean_imputation"] = {
            "functional_energy_score": mean_energy.detach().cpu().tolist(),
            "field_mean_relative_l2": mean_field.detach().cpu().tolist(),
        }
    return aggregate, per_context


def _evaluate_paired_response(
    n1c: Mapping[str, Any],
    models: Mapping[str, Any],
    operator_train: Mapping[str, Any],
    test: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    import torch

    contexts = int(n1c["test_lock"]["operator_test_contexts"])
    conditions = int(n1c["test_lock"]["conditions_per_context"])
    context, boundary, field, _ = _flatten_split(test)
    predictions = {}
    for name in (
        "aurora_shared_operator_pair_loss",
        "aurora_shared_operator_pair_loss_zero",
        "aurora_shared_operator_random_cross_context_pair",
    ):
        chunks = []
        for start in range(0, context.shape[0], 1024):
            end = min(start + 1024, context.shape[0])
            chunks.append(models[name](context[start:end], boundary[start:end]))
        predictions[name] = torch.cat(chunks)

    train_context, train_boundary, train_field, _ = _flatten_split(operator_train)
    raw_key = torch.cat((train_context, train_boundary), dim=-1)
    key_location = raw_key.mean(dim=0)
    key_scale = raw_key.std(dim=0, unbiased=False).clamp_min(1e-4)
    train_key = (raw_key - key_location) / key_scale
    test_key = (torch.cat((context, boundary), dim=-1) - key_location) / key_scale
    anchor = nearest_training_indices(test_key, train_key, exclude_self=False)
    delta_chunks = []
    delta_model = models["deltaphi_style_residual"]
    for start in range(0, context.shape[0], 1024):
        end = min(start + 1024, context.shape[0])
        index = anchor[start:end]
        delta_chunks.append(
            delta_model(
                context[start:end],
                boundary[start:end],
                train_context[index],
                train_boundary[index],
                train_field[index],
            )
        )
    predictions["deltaphi_style_residual"] = torch.cat(delta_chunks)

    first_local = torch.arange(0, conditions, 2, device=context.device)
    second_local = first_local + 1
    context_offset = (
        torch.arange(contexts, device=context.device)[:, None] * conditions
    )
    first = (context_offset + first_local[None]).reshape(-1)
    second = (context_offset + second_local[None]).reshape(-1)
    true_delta = field[second] - field[first]
    aggregate = {}
    per_context = {}
    for name, prediction in predictions.items():
        full = _relative_l2(prediction, field).reshape(
            contexts, conditions
        ).mean(dim=1)
        pair = _relative_l2(
            prediction[second] - prediction[first],
            true_delta,
        ).reshape(contexts, conditions // 2).mean(dim=1)
        aggregate[name] = {
            "full_bc_field_relative_l2": float(full.mean().item()),
            "paired_response_relative_l2": float(pair.mean().item()),
        }
        per_context[name] = {
            "full_bc_field_relative_l2": full.detach().cpu().tolist(),
            "paired_response_relative_l2": pair.detach().cpu().tolist(),
        }
    return aggregate, per_context


def _sequential_joint_posterior(
    joint: tuple[Any, Any, Any],
    boundary: Any,
    initial: Sequence[int],
    reveal_order: Sequence[int],
) -> tuple[Any, Any, Any, list[int]]:
    from aurora.nonlinear_pde import condition_gaussian_mixture

    weights, means, covariances, remaining = conditional_posterior_from_joint(
        *joint,
        boundary,
        initial,
    )
    for component in reveal_order:
        local = remaining.index(component)
        weights, means, covariances, local_remaining = condition_gaussian_mixture(
            weights,
            means,
            covariances,
            [local],
            boundary[:, component : component + 1],
        )
        remaining = [remaining[index] for index in local_remaining]
    return weights, means, covariances, remaining


def _route_posteriors(
    model_name: str,
    models: Mapping[str, Any],
    context: Any,
    boundary: Any,
) -> dict[str, tuple[Any, Any, Any, list[int]]]:
    initial = [0, 2]
    final = [0, 2, 5, 7]
    if model_name == "aurora_joint":
        joint = models[model_name](context)
        return {
            "direct_final": conditional_posterior_from_joint(
                *joint, boundary, final
            ),
            "sequential_5_then_7": _sequential_joint_posterior(
                joint, boundary, initial, [5, 7]
            ),
            "sequential_7_then_5": _sequential_joint_posterior(
                joint, boundary, initial, [7, 5]
            ),
        }
    initial_mask = mask_tensor(
        initial,
        context.shape[0],
        device=context.device,
        dtype=context.dtype,
    )
    final_mask = mask_tensor(
        final,
        context.shape[0],
        device=context.device,
        dtype=context.dtype,
    )
    if model_name == "independent_mask_heads":
        initial_gmm = models[model_name](
            "sparse_2", context, boundary, initial_mask
        )
        final_gmm = models[model_name](
            "partial_4", context, boundary, final_mask
        )
    elif model_name == "acflow_adapted":
        initial_gmm = models[model_name](context, boundary, initial_mask)
        final_gmm = models[model_name](context, boundary, final_mask)
    else:
        raise NonlinearDecisionError(f"Route not defined for {model_name}.")
    return {
        "direct_final": direct_mask_posterior(*final_gmm, final),
        "sequential_5_then_7": sequential_mask_posterior(
            *initial_gmm, boundary, initial, [5, 7]
        ),
        "sequential_7_then_5": sequential_mask_posterior(
            *initial_gmm, boundary, initial, [7, 5]
        ),
    }


def _route_candidate_risks(
    posterior: tuple[Any, Any, Any, list[int]],
    context: Any,
    observed_boundary: Any,
    final_positions: Sequence[int],
    models: Mapping[str, Any],
    functional_location: Any,
    functional_scale: Any,
    functional_grid_minimum: Any,
    functional_grid_maximum: Any,
    n1c: Mapping[str, Any],
    *,
    seed: int,
) -> Any:
    """Estimate next-component risk under one fixed final-mask route posterior."""

    import torch
    from aurora.nonlinear_pde import condition_gaussian_mixture

    weights, means, covariances, remaining = posterior
    candidates = list(remaining)
    outer = int(n1c["acquisition_evaluation"]["outer_measurement_samples"])
    inner = int(n1c["acquisition_evaluation"]["inner_posterior_samples"])
    outer_boundary = complete_boundary_samples(
        posterior,
        observed_boundary,
        final_positions,
        samples=outer,
        seed=seed,
    )
    risks = []
    for candidate in candidates:
        local = remaining.index(candidate)
        expanded_weights = weights[:, None].expand(-1, outer, -1).reshape(-1, 2)
        expanded_means = (
            means[:, None]
            .expand(-1, outer, -1, -1)
            .reshape(-1, 2, len(remaining))
        )
        expanded_covariances = (
            covariances[:, None]
            .expand(-1, outer, -1, -1, -1)
            .reshape(-1, 2, len(remaining), len(remaining))
        )
        candidate_value = outer_boundary[:, :, candidate].reshape(-1, 1)
        conditioned = condition_gaussian_mixture(
            expanded_weights,
            expanded_means,
            expanded_covariances,
            [local],
            candidate_value,
        )
        conditioned_weights, conditioned_means, conditioned_covariances, local_order = (
            conditioned
        )
        global_order = [remaining[index] for index in local_order]
        expanded_observed = (
            observed_boundary[:, None].expand(-1, outer, -1).clone()
        )
        expanded_observed[:, :, candidate] = outer_boundary[:, :, candidate]
        expanded_observed = expanded_observed.reshape(-1, 8)
        completion = complete_boundary_samples(
            (
                conditioned_weights,
                conditioned_means,
                conditioned_covariances,
                global_order,
            ),
            expanded_observed,
            sorted([*final_positions, candidate]),
            samples=inner,
            seed=seed + 1000 + candidate,
        )
        expanded_context = (
            context[:, None].expand(-1, outer, -1).reshape(-1, 5)
        )
        functionals = _operator_functionals(
            models["aurora_shared_operator_pair_loss"],
            expanded_context,
            completion,
        )
        standardized = standardize_functionals(
            functionals, functional_location, functional_scale
        )
        _, risk = bounded_bayes_action(
            standardized,
            functional_grid_minimum,
            functional_grid_maximum,
            grid_points=int(
                n1c["functional_contract"]["bayes_action_grid_points"]
            ),
        )
        risks.append(
            risk.mean(dim=-1).reshape(context.shape[0], outer).mean(dim=1)
        )
    return torch.stack(risks, dim=1)


def _route_candidate_seed(
    n1c: Mapping[str, Any],
    base_seed: int,
    route_offset: int,
) -> int:
    """Return the registered candidate-risk stream for one route.

    The prospective N1c run incorrectly added ``1000 * route_offset`` even
    though its config required common random numbers. Its two affected
    secondary metrics are excluded from that result. This helper prevents the
    same violation in post-result diagnostics and future versions.
    """

    seed = int(base_seed) + 50000
    if not n1c["route_evaluation"]["common_random_numbers_across_routes"]:
        seed += 1000 * int(route_offset)
    return seed


def _evaluate_routes(
    n1c: Mapping[str, Any],
    n0_config: Mapping[str, Any],
    models: Mapping[str, Any],
    test: Mapping[str, Any],
    functional_location: Any,
    functional_scale: Any,
    functional_grid_minimum: Any,
    functional_grid_maximum: Any,
    *,
    seed_index: int,
    true_functional_samples: Any | None,
) -> tuple[dict[str, Any], dict[str, Any], Any, dict[str, Any] | None]:
    import torch

    contract = n1c["route_evaluation"]
    indices = torch.tensor(
        contract["context_indices"], device=test["context"].device
    )
    context = test["context"][indices]
    boundary = test["boundary"][indices, int(contract["anchor_condition_index"])]
    samples = int(contract["posterior_samples"])
    final = contract["final_mask"]
    oracle_summary = None
    if true_functional_samples is None:
        true_boundary = sample_radius_truncated_conditional_gmm(
            test["true_weights"][indices],
            test["true_means"][indices],
            test["true_covariances"][indices],
            final,
            boundary[:, final],
            samples=samples,
            seed=int(n1c["randomness"]["route_base_seed"]) - 1,
            maximum_radius=float(
                n1c["test_lock"]["maximum_latent_mahalanobis_radius"]
            ),
        )
        expanded_context = context[:, None].expand(-1, samples, -1).reshape(-1, 5)
        true_values, oracle_summary = _solve_functionals(
            expanded_context,
            true_boundary.reshape(-1, 8),
            n0_config=n0_config,
        )
        true_functional_samples = standardize_functionals(
            true_values.reshape(context.shape[0], samples, -1),
            functional_location,
            functional_scale,
        )

    aggregate = {}
    per_context = {}
    base_seed = int(n1c["randomness"]["route_base_seed"])
    base_seed += 100000 * seed_index
    operator = models["aurora_shared_operator_pair_loss"]
    for model_name in contract["models_with_tractable_density_routes"]:
        posteriors = _route_posteriors(model_name, models, context, boundary)
        route_functionals = {}
        route_actions = {}
        route_risks = {}
        route_candidate_risk = {}
        for route_offset, (route_name, posterior) in enumerate(posteriors.items()):
            completed = complete_boundary_samples(
                posterior,
                boundary,
                final,
                samples=samples,
                seed=base_seed,
            )
            functionals = _operator_functionals(operator, context, completed)
            standardized = standardize_functionals(
                functionals,
                functional_location,
                functional_scale,
            )
            action, _ = bounded_bayes_action(
                standardized,
                functional_grid_minimum,
                functional_grid_maximum,
                grid_points=int(
                    n1c["functional_contract"]["bayes_action_grid_points"]
                ),
            )
            route_functionals[route_name] = standardized
            route_actions[route_name] = action
            route_risks[route_name] = bounded_action_risk(
                action, true_functional_samples
            )
            route_candidate_risk[route_name] = _route_candidate_risks(
                posterior,
                context,
                boundary,
                final,
                models,
                functional_location,
                functional_scale,
                functional_grid_minimum,
                functional_grid_maximum,
                n1c,
                seed=_route_candidate_seed(n1c, base_seed, route_offset),
            )
        direct = route_functionals["direct_final"]
        direct_action = route_actions["direct_final"]
        model_aggregate = {}
        model_context = {}
        for route_name in ("sequential_5_then_7", "sequential_7_then_5"):
            distance = empirical_one_wasserstein(
                direct, route_functionals[route_name]
            ).mean(dim=-1)
            action_difference = torch.abs(
                direct_action - route_actions[route_name]
            ).max(dim=-1).values
            true_risk_difference = (
                route_risks[route_name] - route_risks["direct_final"]
            ).mean(dim=-1)
            voi_difference = torch.abs(
                route_candidate_risk[route_name]
                - route_candidate_risk["direct_final"]
            ).max(dim=-1).values
            component_disagreement = (
                route_candidate_risk[route_name].argmin(dim=-1)
                != route_candidate_risk["direct_final"].argmin(dim=-1)
            ).to(torch.float32)
            model_aggregate[route_name] = {
                "functional_posterior_wasserstein": float(
                    distance.mean().item()
                ),
                "bayes_action_disagreement": float(
                    action_difference.mean().item()
                ),
                "bayes_action_disagreement_maximum": float(
                    action_difference.max().item()
                ),
                "sequential_minus_direct_true_action_risk": float(
                    true_risk_difference.mean().item()
                ),
                "value_of_information_disagreement": float(
                    voi_difference.mean().item()
                ),
                "selected_next_component_disagreement": float(
                    component_disagreement.mean().item()
                ),
            }
            model_context[route_name] = {
                "functional_posterior_wasserstein": distance.detach()
                .cpu()
                .tolist(),
                "bayes_action_disagreement": action_difference.detach()
                .cpu()
                .tolist(),
                "sequential_minus_direct_true_action_risk": (
                    true_risk_difference.detach().cpu().tolist()
                ),
                "value_of_information_disagreement": voi_difference.detach()
                .cpu()
                .tolist(),
                "selected_next_component_disagreement": (
                    component_disagreement.detach().cpu().tolist()
                ),
            }
        aggregate[model_name] = model_aggregate
        per_context[model_name] = model_context
    return aggregate, per_context, true_functional_samples, oracle_summary


def _candidate_model_risk(
    *,
    model_name: str,
    models: Mapping[str, Any],
    context: Any,
    observed_boundary: Any,
    base_positions: Sequence[int],
    candidate: int,
    outer_boundary: Any,
    functional_location: Any,
    functional_scale: Any,
    functional_grid_minimum: Any,
    functional_grid_maximum: Any,
    n1c: Mapping[str, Any],
    seed: int,
) -> Any:
    import torch

    outer = outer_boundary.shape[1]
    inner = int(n1c["acquisition_evaluation"]["inner_posterior_samples"])
    expanded_context = context[:, None].expand(-1, outer, -1).reshape(-1, 5)
    expanded_observed = observed_boundary[:, None].expand(-1, outer, -1).clone()
    expanded_observed[:, :, candidate] = outer_boundary[:, :, candidate]
    expanded_observed = expanded_observed.reshape(-1, 8)
    positions = sorted([*base_positions, candidate])
    if model_name == "aurora_joint":
        posterior = conditional_posterior_from_joint(
            *models[model_name](expanded_context),
            expanded_observed,
            positions,
        )
    elif model_name == "acflow_adapted":
        mask = mask_tensor(
            positions,
            expanded_context.shape[0],
            device=context.device,
            dtype=context.dtype,
        )
        posterior = direct_mask_posterior(
            *models[model_name](expanded_context, expanded_observed, mask),
            positions,
        )
    else:
        raise NonlinearDecisionError("Expected-risk policy requires a density model.")
    completion = complete_boundary_samples(
        posterior,
        expanded_observed,
        positions,
        samples=inner,
        seed=seed,
    )
    functionals = _operator_functionals(
        models["aurora_shared_operator_pair_loss"],
        expanded_context,
        completion,
    )
    standardized = standardize_functionals(
        functionals, functional_location, functional_scale
    )
    _, risk = bounded_bayes_action(
        standardized,
        functional_grid_minimum,
        functional_grid_maximum,
        grid_points=int(n1c["functional_contract"]["bayes_action_grid_points"]),
    )
    return risk.mean(dim=-1).reshape(context.shape[0], outer).mean(dim=1)


def _candidate_true_risk(
    *,
    true_weights: Any,
    true_means: Any,
    true_covariances: Any,
    context: Any,
    observed_boundary: Any,
    base_positions: Sequence[int],
    candidate: int,
    outer_boundary: Any,
    functional_location: Any,
    functional_scale: Any,
    functional_grid_minimum: Any,
    functional_grid_maximum: Any,
    n1c: Mapping[str, Any],
    n0_config: Mapping[str, Any],
    seed: int,
) -> tuple[Any, dict[str, Any]]:
    outer = outer_boundary.shape[1]
    inner = int(n1c["acquisition_evaluation"]["inner_posterior_samples"])
    expanded_context = context[:, None].expand(-1, outer, -1).reshape(-1, 5)
    expanded_observed = observed_boundary[:, None].expand(-1, outer, -1).clone()
    expanded_observed[:, :, candidate] = outer_boundary[:, :, candidate]
    expanded_observed = expanded_observed.reshape(-1, 8)
    weights = true_weights[:, None].expand(-1, outer, -1).reshape(-1, 2)
    means = true_means[:, None].expand(-1, outer, -1, -1).reshape(-1, 2, 8)
    covariances = (
        true_covariances[:, None]
        .expand(-1, outer, -1, -1, -1)
        .reshape(-1, 2, 8, 8)
    )
    positions = sorted([*base_positions, candidate])
    completion = sample_radius_truncated_conditional_gmm(
        weights,
        means,
        covariances,
        positions,
        expanded_observed[:, positions],
        samples=inner,
        seed=seed,
        maximum_radius=float(
            n1c["test_lock"]["maximum_latent_mahalanobis_radius"]
        ),
    )
    values, summary = _solve_functionals(
        expanded_context[:, None].expand(-1, inner, -1).reshape(-1, 5),
        completion.reshape(-1, 8),
        n0_config=n0_config,
    )
    standardized = standardize_functionals(
        values.reshape(expanded_context.shape[0], inner, -1),
        functional_location,
        functional_scale,
    )
    _, risk = bounded_bayes_action(
        standardized,
        functional_grid_minimum,
        functional_grid_maximum,
        grid_points=int(n1c["functional_contract"]["bayes_action_grid_points"]),
    )
    return (
        risk.mean(dim=-1).reshape(context.shape[0], outer).mean(dim=1),
        summary,
    )


def _evaluate_acquisition(
    n1c: Mapping[str, Any],
    n0_config: Mapping[str, Any],
    models: Mapping[str, Any],
    test: Mapping[str, Any],
    functional_location: Any,
    functional_scale: Any,
    functional_grid_minimum: Any,
    functional_grid_maximum: Any,
    *,
    seed_index: int,
    true_candidate_risks: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    import torch

    contract = n1c["acquisition_evaluation"]
    index = torch.tensor(contract["context_indices"], device=test["context"].device)
    context = test["context"][index]
    observed = test["boundary"][index, int(contract["anchor_condition_index"])]
    weights = test["true_weights"][index]
    means = test["true_means"][index]
    covariances = test["true_covariances"][index]
    outer = int(contract["outer_measurement_samples"])
    base_seed = int(n1c["randomness"]["acquisition_model_base_seed"])
    base_seed += 100000 * seed_index
    oracle_summaries = []
    if true_candidate_risks is None:
        true_candidate_risks = {}
    computed_true = {}
    results = {}
    per_context = {}
    for mask_offset, (mask_name, positions) in enumerate(
        contract["base_masks"].items()
    ):
        candidates = [item for item in range(8) if item not in positions]
        true_outer = sample_radius_truncated_conditional_gmm(
            weights,
            means,
            covariances,
            positions,
            observed[:, positions],
            samples=outer,
            seed=int(n1c["randomness"]["acquisition_oracle_base_seed"])
            + 1000 * mask_offset,
            maximum_radius=float(
                n1c["test_lock"]["maximum_latent_mahalanobis_radius"]
            ),
        )
        if mask_name in true_candidate_risks:
            true_risk_matrix = true_candidate_risks[mask_name].to(context.device)
        else:
            true_risks = []
            for candidate in candidates:
                risk, summary = _candidate_true_risk(
                    true_weights=weights,
                    true_means=means,
                    true_covariances=covariances,
                    context=context,
                    observed_boundary=observed,
                    base_positions=positions,
                    candidate=candidate,
                    outer_boundary=true_outer,
                    functional_location=functional_location,
                    functional_scale=functional_scale,
                    functional_grid_minimum=functional_grid_minimum,
                    functional_grid_maximum=functional_grid_maximum,
                    n1c=n1c,
                    n0_config=n0_config,
                    seed=int(n1c["randomness"]["acquisition_oracle_base_seed"])
                    + 10000
                    + 1000 * mask_offset
                    + candidate,
                )
                true_risks.append(risk)
                oracle_summaries.append(summary)
            true_risk_matrix = torch.stack(true_risks, dim=1)
            computed_true[mask_name] = true_risk_matrix.detach().cpu()

        model_risks = {}
        for model_offset, model_name in enumerate(
            ("aurora_joint", "acflow_adapted")
        ):
            if model_name == "aurora_joint":
                current = conditional_posterior_from_joint(
                    *models[model_name](context), observed, positions
                )
            else:
                mask = mask_tensor(
                    positions,
                    context.shape[0],
                    device=context.device,
                    dtype=context.dtype,
                )
                current = direct_mask_posterior(
                    *models[model_name](context, observed, mask), positions
                )
            model_outer = complete_boundary_samples(
                current,
                observed,
                positions,
                samples=outer,
                seed=base_seed + 1000 * mask_offset + 100 * model_offset,
            )
            risks = []
            for candidate in candidates:
                risks.append(
                    _candidate_model_risk(
                        model_name=model_name,
                        models=models,
                        context=context,
                        observed_boundary=observed,
                        base_positions=positions,
                        candidate=candidate,
                        outer_boundary=model_outer,
                        functional_location=functional_location,
                        functional_scale=functional_scale,
                        functional_grid_minimum=functional_grid_minimum,
                        functional_grid_maximum=functional_grid_maximum,
                        n1c=n1c,
                        seed=base_seed
                        + 10000
                        + 1000 * mask_offset
                        + 100 * model_offset
                        + candidate,
                    )
                )
            model_risks[model_name] = torch.stack(risks, dim=1)

        aurora_current = conditional_posterior_from_joint(
            *models["aurora_joint"](context), observed, positions
        )
        diagnostic_samples = complete_boundary_samples(
            aurora_current,
            observed,
            positions,
            samples=128,
            seed=base_seed + 20000 + mask_offset,
        )
        variance_score = diagnostic_samples[:, :, candidates].var(
            dim=1, unbiased=False
        )
        functional = _operator_functionals(
            models["aurora_shared_operator_pair_loss"],
            context,
            diagnostic_samples,
        )
        functional = standardize_functionals(
            functional, functional_location, functional_scale
        )
        centered_functional = functional - functional.mean(dim=1, keepdim=True)
        centered_boundary = (
            diagnostic_samples[:, :, candidates]
            - diagnostic_samples[:, :, candidates].mean(dim=1, keepdim=True)
        )
        covariance = torch.einsum(
            "bkc,bkf->bcf", centered_boundary, centered_functional
        ) / diagnostic_samples.shape[1]
        dependence_score = torch.abs(covariance).mean(dim=-1)
        generator = torch.Generator(device="cpu").manual_seed(
            int(n1c["randomness"]["random_policy_base_seed"]) + mask_offset
        )
        random_local = torch.randint(
            len(candidates),
            (context.shape[0],),
            generator=generator,
        ).to(context.device)

        selections = {
            "aurora_expected_functional_risk_reduction": model_risks[
                "aurora_joint"
            ].argmin(dim=1),
            "acflow_expected_functional_risk_reduction": model_risks[
                "acflow_adapted"
            ].argmin(dim=1),
            "posterior_boundary_variance": variance_score.argmax(dim=1),
            "nots_style_boundary_functional_dependence": dependence_score.argmax(
                dim=1
            ),
            "uniform_random_component": random_local,
            "aco_true_law_simulator_ceiling": true_risk_matrix.argmin(dim=1),
        }
        oracle_local = selections["aco_true_law_simulator_ceiling"]
        oracle_risk = torch.gather(
            true_risk_matrix, 1, oracle_local[:, None]
        ).squeeze(1)
        mask_results = {}
        mask_context = {}
        candidate_tensor = torch.tensor(candidates, device=context.device)
        for policy, selected_local in selections.items():
            selected_risk = torch.gather(
                true_risk_matrix, 1, selected_local[:, None]
            ).squeeze(1)
            regret = selected_risk - oracle_risk
            agreement = (selected_local == oracle_local).to(torch.float32)
            selected_component = candidate_tensor[selected_local]
            mask_results[policy] = {
                "true_post_acquisition_bayes_risk": float(
                    selected_risk.mean().item()
                ),
                "regret_to_aco_ceiling": float(regret.mean().item()),
                "selected_component_agreement_with_aco": float(
                    agreement.mean().item()
                ),
            }
            mask_context[policy] = {
                "true_post_acquisition_bayes_risk": selected_risk.detach()
                .cpu()
                .tolist(),
                "regret_to_aco_ceiling": regret.detach().cpu().tolist(),
                "selected_component_agreement_with_aco": agreement.detach()
                .cpu()
                .tolist(),
                "selected_component": selected_component.detach().cpu().tolist(),
            }
        results[mask_name] = mask_results
        per_context[mask_name] = mask_context
    merged_true = {
        **{
            key: value.detach().cpu()
            for key, value in true_candidate_risks.items()
        },
        **computed_true,
    }
    return results, per_context, merged_true, oracle_summaries


def _summarize_decision(
    n1c: Mapping[str, Any],
    seed_metrics: Sequence[Mapping[str, Any]],
    seed_context: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    import torch

    primary_masks = list(n1c["id_distribution_evaluation"]["primary_masks"])
    baseline_names = [
        "independent_mask_heads",
        "lano_adapted",
        "acflow_adapted",
        "generic_probabilistic_operator",
        "nop_adapted",
        "conditional_mean_imputation",
    ]
    distribution_comparisons = {}
    distribution_pass = True
    direction_minimum = int(
        n1c["success_rule"]["confirmatory_seed_direction_minimum"]
    )
    bootstrap_seed = int(n1c["randomness"]["bootstrap_base_seed"])
    for mask_offset, mask_name in enumerate(primary_masks):
        aurora = torch.tensor(
            [
                item["id_distribution"][mask_name]["aurora_joint"][
                    "functional_energy_score"
                ]
                for item in seed_metrics
            ]
        )
        baseline = {}
        for name in baseline_names:
            baseline[name] = torch.tensor(
                [
                    item["id_distribution"][mask_name][name][
                        "functional_energy_score"
                    ]
                    for item in seed_metrics
                ]
            )
        strongest_name = min(
            baseline_names,
            key=lambda name: float(baseline[name].mean().item()),
        )
        strongest = baseline[strongest_name]
        relative = (strongest - aurora) / strongest.clamp_min(1e-12)
        directions = int((aurora < strongest).sum().item())
        context_difference = []
        for seed_item in seed_context:
            context_difference.append(
                torch.tensor(
                    seed_item["id_distribution"][mask_name]["aurora_joint"][
                        "functional_energy_score"
                    ]
                )
                - torch.tensor(
                    seed_item["id_distribution"][mask_name][strongest_name][
                        "functional_energy_score"
                    ]
                )
            )
        interval = context_bootstrap_interval(
            torch.stack(context_difference),
            replicates=int(n1c["inference_and_statistics"]["bootstrap_replicates"]),
            seed=bootstrap_seed + mask_offset,
        )
        passed = (
            float(relative.mean().item())
            >= float(
                n1c["success_rule"][
                    "primary_relative_improvement_over_strongest_prefrozen_nonoracle_minimum"
                ]
            )
            and directions >= direction_minimum
            and interval["ci95_high"] < 0.0
        )
        distribution_pass &= passed
        distribution_comparisons[mask_name] = {
            "strongest_nonoracle": strongest_name,
            "aurora_seed_mean": float(aurora.mean().item()),
            "strongest_seed_mean": float(strongest.mean().item()),
            "relative_improvement": float(relative.mean().item()),
            "seed_directions": directions,
            "paired_context_bootstrap": interval,
            "passed": passed,
        }

    acquisition_comparisons = {}
    acquisition_pass = True
    acquisition_baselines = [
        "acflow_expected_functional_risk_reduction",
        "posterior_boundary_variance",
        "nots_style_boundary_functional_dependence",
        "uniform_random_component",
    ]
    for mask_offset, mask_name in enumerate(
        n1c["acquisition_evaluation"]["base_masks"]
    ):
        aurora = torch.tensor(
            [
                item["acquisition"][mask_name][
                    "aurora_expected_functional_risk_reduction"
                ]["regret_to_aco_ceiling"]
                for item in seed_metrics
            ]
        )
        baseline = {
            name: torch.tensor(
                [
                    item["acquisition"][mask_name][name][
                        "regret_to_aco_ceiling"
                    ]
                    for item in seed_metrics
                ]
            )
            for name in acquisition_baselines
        }
        strongest_name = min(
            acquisition_baselines,
            key=lambda name: float(baseline[name].mean().item()),
        )
        strongest = baseline[strongest_name]
        relative = (strongest - aurora) / strongest.clamp_min(1e-12)
        directions = int((aurora < strongest).sum().item())
        context_difference = []
        for seed_item in seed_context:
            context_difference.append(
                torch.tensor(
                    seed_item["acquisition"][mask_name][
                        "aurora_expected_functional_risk_reduction"
                    ]["regret_to_aco_ceiling"]
                )
                - torch.tensor(
                    seed_item["acquisition"][mask_name][strongest_name][
                        "regret_to_aco_ceiling"
                    ]
                )
            )
        interval = context_bootstrap_interval(
            torch.stack(context_difference),
            replicates=int(n1c["inference_and_statistics"]["bootstrap_replicates"]),
            seed=bootstrap_seed + 100 + mask_offset,
        )
        passed = (
            float(relative.mean().item())
            >= float(
                n1c["success_rule"][
                    "primary_relative_improvement_over_strongest_prefrozen_nonoracle_minimum"
                ]
            )
            and directions >= direction_minimum
            and interval["ci95_high"] < 0.0
        )
        acquisition_pass &= passed
        acquisition_comparisons[mask_name] = {
            "strongest_nonoracle": strongest_name,
            "aurora_seed_mean": float(aurora.mean().item()),
            "strongest_seed_mean": float(strongest.mean().item()),
            "relative_improvement": float(relative.mean().item()),
            "seed_directions": directions,
            "paired_context_bootstrap": interval,
            "passed": passed,
        }

    full_operator = max(
        item["paired_response"]["aurora_shared_operator_pair_loss"][
            "full_bc_field_relative_l2"
        ]
        for item in seed_metrics
    )
    coverage = max(
        item["id_distribution"][mask]["aurora_joint"][
            "functional_coverage_error_maximum"
        ]
        for item in seed_metrics
        for mask in primary_masks
    )
    route_action = max(
        item["route"]["aurora_joint"][route][
            "bayes_action_disagreement_maximum"
        ]
        for item in seed_metrics
        for route in ("sequential_5_then_7", "sequential_7_then_5")
    )
    pair_direction = sum(
        item["paired_response"]["aurora_shared_operator_pair_loss"][
            "paired_response_relative_l2"
        ]
        < item["paired_response"]["aurora_shared_operator_pair_loss_zero"][
            "paired_response_relative_l2"
        ]
        for item in seed_metrics
    )
    pair_context_difference = torch.stack(
        [
            torch.tensor(
                item["paired_response"]["aurora_shared_operator_pair_loss"][
                    "paired_response_relative_l2"
                ]
            )
            - torch.tensor(
                item["paired_response"][
                    "aurora_shared_operator_pair_loss_zero"
                ]["paired_response_relative_l2"]
            )
            for item in seed_context
        ]
    )
    pair_interval = context_bootstrap_interval(
        pair_context_difference,
        replicates=int(n1c["inference_and_statistics"]["bootstrap_replicates"]),
        seed=bootstrap_seed + 200,
    )
    checks = {
        "full_bc_operator": full_operator
        <= float(n1c["success_rule"]["full_bc_operator_relative_l2_maximum"]),
        "functional_coverage": coverage
        <= float(
            n1c["success_rule"]["aurora_functional_coverage_error_maximum"]
        ),
        "route_bayes_action": route_action
        <= float(
            n1c["success_rule"][
                "aurora_route_bayes_action_disagreement_maximum"
            ]
        ),
        "paired_response": pair_direction >= direction_minimum
        and pair_interval["ci95_high"] < 0.0,
        "field_distribution": distribution_pass,
        "acquisition_regret": acquisition_pass,
    }
    passed = all(checks.values())
    return {
        "checks": checks,
        "n1_passed": passed,
        "worst_seed_full_bc_operator_relative_l2": full_operator,
        "worst_seed_mask_functional_coverage_error": coverage,
        "maximum_aurora_route_bayes_action_disagreement": route_action,
        "paired_response_pair_loss_better_seed_count": pair_direction,
        "paired_response_pair_minus_zero_bootstrap": pair_interval,
        "distribution_comparisons": distribution_comparisons,
        "acquisition_comparisons": acquisition_comparisons,
        "irregular_3d_protocol_registration_authorized": passed,
        "irregular_3d_execution_authorized": False,
        "aaai_acceptance_established": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n1c-config", type=Path, required=True)
    parser.add_argument("--n0-config", type=Path, required=True)
    parser.add_argument("--checkpoint-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    n1, _, n1c, manifest = load_n1c_config(args.n1c_config)
    n0 = json.loads(args.n0_config.read_text(encoding="utf-8"))
    import torch

    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("N1c outer test requires CUDA.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(value) for value in sys.argv) + "\n",
        encoding="utf-8",
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "n1c_config.sha256").write_text(
        _sha256(args.n1c_config) + "\n", encoding="utf-8"
    )

    # Verify every frozen model and the shared representation before touching
    # the test seed. Loading is repeated later, but no test data exist yet.
    pod_hash = manifest["shared_representation"]["sha256"]
    for seed_run in manifest["seed_runs"]:
        directory = args.checkpoint_root / f"seed_{seed_run['seed_index']}"
        if _sha256(directory / "train_only_pod_representation.pt") != pod_hash:
            raise NonlinearDecisionError("Shared POD checkpoint hash mismatch.")
        for name, expected in seed_run["checkpoint_sha256"].items():
            if _sha256(directory / f"{name}.pt") != expected:
                raise NonlinearDecisionError(
                    f"Checkpoint hash mismatch before test: seed "
                    f"{seed_run['seed_index']} {name}."
                )
    _write_json(
        args.output / "pretest_integrity.json",
        {
            "all_five_seed_checkpoint_hashes_verified": True,
            "test_generated_at_verification_time": False,
            "checkpoint_manifest_sha256": _sha256(
                Path(args.n1c_config).parent
                / n1c["parents"]["checkpoint_manifest"]["path"]
            ),
        },
    )

    data = n1["data"]
    support = data["context_support"]["train_validation_id_test"]
    radius = float(
        data["boundary_latent_support"][
            "train_validation_id_test_max_mahalanobis_radius"
        ]
    )
    operator_train = generate_solution_split(
        contexts=int(data["operator_train_contexts"]),
        conditions=int(data["operator_conditions_per_context"]),
        context_seed=int(data["split_seeds"]["operator_train"]),
        boundary_seed=int(data["split_seeds"]["operator_train"]) + 1000,
        context_support=support,
        maximum_radius=radius,
        solver_config=n0,
        device=device,
    )
    training_functionals = operator_train["functionals"].reshape(-1, 4)
    functional_location = training_functionals.mean(dim=0)
    functional_scale = training_functionals.std(
        dim=0, unbiased=False
    ).clamp_min(
        float(n1c["functional_contract"]["standardization_floor"])
    )
    standardized_training = standardize_functionals(
        training_functionals, functional_location, functional_scale
    )
    functional_grid_minimum = standardized_training.min(dim=0).values
    functional_grid_maximum = standardized_training.max(dim=0).values

    # This is the first test-seed access. It occurs only after all checkpoint
    # hashes and the committed N1c overlay have been validated.
    test = generate_solution_split(
        contexts=int(n1c["test_lock"]["operator_test_contexts"]),
        conditions=int(n1c["test_lock"]["conditions_per_context"]),
        context_seed=int(n1c["test_lock"]["context_seed"]),
        boundary_seed=int(n1c["test_lock"]["boundary_seed"]),
        context_support=n1c["test_lock"]["context_support"],
        maximum_radius=float(
            n1c["test_lock"]["maximum_latent_mahalanobis_radius"]
        ),
        solver_config=n0,
        device=device,
    )
    (
        test["true_weights"],
        test["true_means"],
        test["true_covariances"],
    ) = boundary_law(test["context"])
    _write_json(
        args.output / "test_access.json",
        {
            "test_split_generated": True,
            "test_seed_accessed": True,
            "operator_test_contexts": int(n1c["test_lock"]["operator_test_contexts"]),
            "conditions_per_context": int(
                n1c["test_lock"]["conditions_per_context"]
            ),
            "context_seed": int(n1c["test_lock"]["context_seed"]),
            "boundary_seed": int(n1c["test_lock"]["boundary_seed"]),
            "generated_after_all_checkpoint_hashes_verified": True,
        },
    )

    seed_metrics = []
    seed_context = []
    true_route_functionals = None
    true_acquisition_risks = None
    oracle_summaries = []
    for seed_run in manifest["seed_runs"]:
        seed_index = int(seed_run["seed_index"])
        run_contract = dict(seed_run)
        run_contract["pod_sha256"] = pod_hash
        models = _load_models(
            n1,
            run_contract,
            args.checkpoint_root / f"seed_{seed_index}",
            device,
        )
        representation_error = pod_representation_error(
            test["field"].reshape(-1, 33, 33),
            models["representation"],
        )
        id_aggregate, id_context = _evaluate_id_distribution(
            n1c,
            models,
            test,
            functional_location,
            functional_scale,
            seed_index=seed_index,
        )
        paired_aggregate, paired_context = _evaluate_paired_response(
            n1c, models, operator_train, test
        )
        route_aggregate, route_context, true_route_functionals, route_solver = (
            _evaluate_routes(
                n1c,
                n0,
                models,
                test,
                functional_location,
                functional_scale,
                functional_grid_minimum,
                functional_grid_maximum,
                seed_index=seed_index,
                true_functional_samples=true_route_functionals,
            )
        )
        if route_solver is not None:
            oracle_summaries.append(route_solver)
        acquisition_aggregate, acquisition_context, true_acquisition_risks, summaries = (
            _evaluate_acquisition(
                n1c,
                n0,
                models,
                test,
                functional_location,
                functional_scale,
                functional_grid_minimum,
                functional_grid_maximum,
                seed_index=seed_index,
                true_candidate_risks=true_acquisition_risks,
            )
        )
        oracle_summaries.extend(summaries)
        seed_metrics.append(
            {
                "seed_index": seed_index,
                "model_seed": int(seed_run["model_seed"]),
                "pod_test_mean_relative_l2": float(
                    representation_error.mean().item()
                ),
                "pod_test_maximum_relative_l2": float(
                    representation_error.max().item()
                ),
                "id_distribution": id_aggregate,
                "paired_response": paired_aggregate,
                "route": route_aggregate,
                "acquisition": acquisition_aggregate,
            }
        )
        seed_context.append(
            {
                "seed_index": seed_index,
                "id_distribution": id_context,
                "paired_response": paired_context,
                "route": route_context,
                "acquisition": acquisition_context,
            }
        )
        _write_json(
            args.output / f"seed_{seed_index}_aggregate.json",
            seed_metrics[-1],
        )
        _write_json(
            args.output / f"seed_{seed_index}_per_context.json",
            seed_context[-1],
        )
        del models
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    decision = _summarize_decision(n1c, seed_metrics, seed_context)
    raw = {
        "schema_version": "aurora.nonlinear_pde_n1c.outer_test.v1",
        "experiment_id": n1c["experiment_id"],
        "stage": "single_preregistered_outer_test",
        "git_commit": args.git_commit,
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "test_access": {
            "generated": True,
            "seed_accessed": True,
            "after_checkpoint_and_overlay_public_commits": True,
            "contexts": int(n1c["test_lock"]["operator_test_contexts"]),
            "conditions_per_context": int(
                n1c["test_lock"]["conditions_per_context"]
            ),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_runtime": torch.version.cuda,
            "gpu_name": (
                torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
            ),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "training_only_functional_standardization": {
            "location": functional_location.detach().cpu().tolist(),
            "scale": functional_scale.detach().cpu().tolist(),
            "grid_minimum": functional_grid_minimum.detach().cpu().tolist(),
            "grid_maximum": functional_grid_maximum.detach().cpu().tolist(),
        },
        "test_solver": test["solver"],
        "oracle_solver": {
            "calls": len(oracle_summaries),
            "all_converged": all(
                item["all_converged"] for item in oracle_summaries
            ),
            "maximum_normalized_residual": max(
                item["maximum_normalized_residual"] for item in oracle_summaries
            ),
        },
        "seeds": seed_metrics,
        "decision": decision,
        "claim_boundary": {
            "active_feature_acquisition_novelty": False,
            "generic_route_consistency_novelty": False,
            "method_novelty_established": decision["n1_passed"],
            "irregular_3d_execution_authorized": False,
            "aaai_acceptance_established": False,
        },
    }
    _write_json(args.output / "metrics.json", raw)
    _write_json(
        args.output / "status.json",
        {
            "state": "completed",
            "n1_passed": decision["n1_passed"],
            "irregular_3d_protocol_registration_authorized": decision[
                "irregular_3d_protocol_registration_authorized"
            ],
            "irregular_3d_execution_authorized": False,
            "test_generated_or_accessed": True,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
