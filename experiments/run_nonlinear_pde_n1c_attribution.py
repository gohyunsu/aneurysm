"""Run the threshold-free post-result attribution of the failed N1c test."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shlex
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde import (
    boundary_law,
    condition_gaussian_mixture,
)
from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    generate_solution_split,
    gmm_nll,
    load_n1c_attribution_config,
)
from aurora.nonlinear_pde_evaluation import (
    bounded_action_risk,
    bounded_bayes_action,
    complete_boundary_samples,
    conditional_posterior_from_joint,
    direct_mask_posterior,
    functional_energy_score,
    mask_tensor,
    sample_radius_truncated_conditional_gmm,
    standardize_functionals,
)
from experiments.run_nonlinear_pde_n1c_outer_test import (
    _evaluate_acquisition,
    _load_models,
    _operator_functionals,
    _route_candidate_risks,
    _route_candidate_seed,
    _route_posteriors,
    _sha256,
    _solve_functionals,
)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _model_posterior(
    model_name: str,
    models: Mapping[str, Any],
    context: Any,
    boundary: Any,
    positions: Sequence[int],
) -> tuple[Any, Any, Any, list[int]]:
    mask = mask_tensor(
        positions,
        context.shape[0],
        device=context.device,
        dtype=context.dtype,
    )
    if model_name == "aurora_joint":
        return conditional_posterior_from_joint(
            *models[model_name](context),
            boundary,
            positions,
        )
    if model_name == "independent_mask_heads":
        mask_name = {
            (): "missing",
            (0, 2): "sparse_2",
            (0, 2, 5, 7): "partial_4",
        }[tuple(positions)]
        return direct_mask_posterior(
            *models[model_name](mask_name, context, boundary, mask),
            positions,
        )
    if model_name == "acflow_adapted":
        return direct_mask_posterior(
            *models[model_name](context, boundary, mask),
            positions,
        )
    raise NonlinearDecisionError(f"Unsupported density model: {model_name}.")


def _true_truncated_conditional_nll(
    weights: Any,
    means: Any,
    covariances: Any,
    boundary: Any,
    observed_positions: Sequence[int],
    *,
    maximum_radius: float,
) -> Any:
    """Evaluate the exact conditional density under the global radius cutoff."""

    import torch

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
            "True truncated conditional assigned zero density to a test case."
        )
    return -(log_numerator - torch.log(normalizer))


def _evaluate_density(
    attribution: Mapping[str, Any],
    n1c: Mapping[str, Any],
    models: Mapping[str, Any],
    test: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    contexts, conditions = test["boundary"].shape[:2]
    context = (
        test["context"][:, None]
        .expand(-1, conditions, -1)
        .reshape(-1, 5)
    )
    boundary = test["boundary"].reshape(-1, 8)
    true_weights = (
        test["true_weights"][:, None]
        .expand(-1, conditions, -1)
        .reshape(-1, 2)
    )
    true_means = (
        test["true_means"][:, None]
        .expand(-1, conditions, -1, -1)
        .reshape(-1, 2, 8)
    )
    true_covariances = (
        test["true_covariances"][:, None]
        .expand(-1, conditions, -1, -1, -1)
        .reshape(-1, 2, 8, 8)
    )
    radius = float(n1c["test_lock"]["maximum_latent_mahalanobis_radius"])
    aggregate: dict[str, Any] = {}
    per_context: dict[str, Any] = {}
    contract = attribution["conditional_density_attribution"]
    for mask_name, positions in contract["masks"].items():
        missing = 8 - len(positions)
        true_nll = _true_truncated_conditional_nll(
            true_weights,
            true_means,
            true_covariances,
            boundary,
            positions,
            maximum_radius=radius,
        ) / missing
        true_context = true_nll.reshape(contexts, conditions).mean(dim=1)
        aggregate[mask_name] = {
            "true_radius_truncated_law": {
                "conditional_nll_per_unobserved_component": float(
                    true_context.mean().item()
                ),
                "excess_over_true_law": 0.0,
            }
        }
        per_context[mask_name] = {
            "true_radius_truncated_law": true_context.detach().cpu().tolist()
        }
        for model_name in contract["models"]:
            posterior = _model_posterior(
                model_name, models, context, boundary, positions
            )
            weights, means, covariances, remaining = posterior
            value = boundary[:, remaining]
            nll = gmm_nll(weights, means, covariances, value) / missing
            nll_context = nll.reshape(contexts, conditions).mean(dim=1)
            excess_context = nll_context - true_context
            aggregate[mask_name][model_name] = {
                "conditional_nll_per_unobserved_component": float(
                    nll_context.mean().item()
                ),
                "excess_over_true_law": float(excess_context.mean().item()),
            }
            per_context[mask_name][model_name] = {
                "conditional_nll_per_unobserved_component": (
                    nll_context.detach().cpu().tolist()
                ),
                "excess_over_true_law": (
                    excess_context.detach().cpu().tolist()
                ),
            }
    return aggregate, per_context


def _evaluate_energy_decomposition(
    attribution: Mapping[str, Any],
    n1c: Mapping[str, Any],
    n0: Mapping[str, Any],
    models: Mapping[str, Any],
    test: Mapping[str, Any],
    functional_location: Any,
    functional_scale: Any,
    *,
    seed_index: int,
    true_solver_cache: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    import torch

    contract = attribution["functional_energy_decomposition"]
    index = torch.tensor(
        contract["context_indices"], device=test["context"].device
    )
    anchor = int(contract["anchor_condition_index"])
    context = test["context"][index]
    observed = test["boundary"][index, anchor]
    target = standardize_functionals(
        test["functionals"][index, anchor],
        functional_location,
        functional_scale,
    )
    weights = test["true_weights"][index]
    means = test["true_means"][index]
    covariances = test["true_covariances"][index]
    samples = int(contract["posterior_samples"])
    operator = models["aurora_shared_operator_pair_loss"]
    seed_offset = int(attribution["randomness"]["model_seed_offset"]) * seed_index
    summaries: list[dict[str, Any]] = []
    aggregate: dict[str, Any] = {}
    per_context: dict[str, Any] = {}
    cache: dict[str, Any] = dict(true_solver_cache or {})
    for mask_offset, (mask_name, positions) in enumerate(
        contract["masks"].items()
    ):
        true_seed = (
            int(attribution["randomness"]["energy_true_density_base_seed"])
            + 1000 * mask_offset
        )
        true_boundary = sample_radius_truncated_conditional_gmm(
            weights,
            means,
            covariances,
            positions,
            observed[:, positions],
            samples=samples,
            seed=true_seed,
            maximum_radius=float(
                n1c["test_lock"]["maximum_latent_mahalanobis_radius"]
            ),
        )
        learned = _model_posterior(
            "aurora_joint", models, context, observed, positions
        )
        learned_boundary = complete_boundary_samples(
            learned,
            observed,
            positions,
            samples=samples,
            seed=(
                int(
                    attribution["randomness"][
                        "energy_learned_density_base_seed"
                    ]
                )
                + seed_offset
                + 1000 * mask_offset
            ),
        )

        learned_learned = standardize_functionals(
            _operator_functionals(operator, context, learned_boundary),
            functional_location,
            functional_scale,
        )
        true_learned = standardize_functionals(
            _operator_functionals(operator, context, true_boundary),
            functional_location,
            functional_scale,
        )
        expanded_context = (
            context[:, None].expand(-1, samples, -1).reshape(-1, 5)
        )
        learned_true_raw, learned_summary = _solve_functionals(
            expanded_context,
            learned_boundary.reshape(-1, 8),
            n0_config=n0,
        )
        summaries.append(learned_summary)
        learned_true = standardize_functionals(
            learned_true_raw.reshape(context.shape[0], samples, -1),
            functional_location,
            functional_scale,
        )
        cache_key = mask_name
        if cache_key not in cache:
            true_true_raw, true_summary = _solve_functionals(
                expanded_context,
                true_boundary.reshape(-1, 8),
                n0_config=n0,
            )
            summaries.append(true_summary)
            cache[cache_key] = standardize_functionals(
                true_true_raw.reshape(context.shape[0], samples, -1),
                functional_location,
                functional_scale,
            ).detach().cpu()
        true_true = cache[cache_key].to(context.device)
        cells = {
            "learned_density_learned_operator": learned_learned,
            "true_density_learned_operator": true_learned,
            "learned_density_true_simulator": learned_true,
            "true_density_true_simulator": true_true,
        }
        scores = {
            name: functional_energy_score(values, target)
            for name, values in cells.items()
        }
        aggregate[mask_name] = {
            name: float(value.mean().item()) for name, value in scores.items()
        }
        primary = scores["learned_density_learned_operator"]
        aggregate[mask_name]["density_oracle_substitution_difference"] = float(
            (
                primary - scores["true_density_learned_operator"]
            ).mean().item()
        )
        aggregate[mask_name]["simulator_oracle_substitution_difference"] = float(
            (
                primary - scores["learned_density_true_simulator"]
            ).mean().item()
        )
        per_context[mask_name] = {
            name: value.detach().cpu().tolist()
            for name, value in scores.items()
        }
    return aggregate, per_context, cache, summaries


def _evaluate_corrected_routes(
    attribution: Mapping[str, Any],
    n1c: Mapping[str, Any],
    n0: Mapping[str, Any],
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

    route_contract = n1c["route_evaluation"]
    index = torch.tensor(
        route_contract["context_indices"], device=test["context"].device
    )
    context = test["context"][index]
    boundary = test["boundary"][
        index, int(route_contract["anchor_condition_index"])
    ]
    samples = int(
        attribution["route_regret_attribution"]["posterior_samples"]
    )
    final = route_contract["final_mask"]
    oracle_summary = None
    if true_functional_samples is None:
        true_boundary = sample_radius_truncated_conditional_gmm(
            test["true_weights"][index],
            test["true_means"][index],
            test["true_covariances"][index],
            final,
            boundary[:, final],
            samples=samples,
            seed=int(
                attribution["randomness"]["route_true_functional_seed"]
            ),
            maximum_radius=float(
                n1c["test_lock"]["maximum_latent_mahalanobis_radius"]
            ),
        )
        expanded_context = (
            context[:, None].expand(-1, samples, -1).reshape(-1, 5)
        )
        values, oracle_summary = _solve_functionals(
            expanded_context,
            true_boundary.reshape(-1, 8),
            n0_config=n0,
        )
        true_functional_samples = standardize_functionals(
            values.reshape(context.shape[0], samples, -1),
            functional_location,
            functional_scale,
        )
    oracle_action, _ = bounded_bayes_action(
        true_functional_samples,
        functional_grid_minimum,
        functional_grid_maximum,
        grid_points=int(
            n1c["functional_contract"]["bayes_action_grid_points"]
        ),
    )
    oracle_risk = bounded_action_risk(
        oracle_action, true_functional_samples
    ).mean(dim=-1)
    base_seed = (
        int(n1c["randomness"]["route_base_seed"])
        + int(attribution["randomness"]["model_seed_offset"]) * seed_index
    )
    operator = models["aurora_shared_operator_pair_loss"]
    aggregate: dict[str, Any] = {}
    per_context: dict[str, Any] = {}
    for model_name in attribution["route_regret_attribution"]["models"]:
        posteriors = _route_posteriors(
            model_name, models, context, boundary
        )
        route_context: dict[str, Any] = {}
        route_candidate: dict[str, Any] = {}
        for route_offset, (route_name, posterior) in enumerate(
            posteriors.items()
        ):
            completed = complete_boundary_samples(
                posterior,
                boundary,
                final,
                samples=samples,
                seed=base_seed,
            )
            functionals = standardize_functionals(
                _operator_functionals(operator, context, completed),
                functional_location,
                functional_scale,
            )
            action, _ = bounded_bayes_action(
                functionals,
                functional_grid_minimum,
                functional_grid_maximum,
                grid_points=int(
                    n1c["functional_contract"]["bayes_action_grid_points"]
                ),
            )
            action_risk = bounded_action_risk(
                action, true_functional_samples
            ).mean(dim=-1)
            raw_excess = action_risk - oracle_risk
            excess = raw_excess.clamp_min(0.0)
            route_context[route_name] = {
                "true_oracle_excess_bayes_risk": excess,
                "raw_excess_before_numerical_clipping": raw_excess,
                "action_risk": action_risk,
            }
            route_candidate[route_name] = _route_candidate_risks(
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
                seed=_route_candidate_seed(
                    n1c, base_seed, route_offset
                ),
            )
        excess_stack = torch.stack(
            [
                route_context[name]["true_oracle_excess_bayes_risk"]
                for name in attribution["route_regret_attribution"]["routes"]
            ],
            dim=1,
        )
        direct_candidate = route_candidate["direct_final"]
        model_aggregate = {
            "routes": {
                name: {
                    "mean_true_oracle_excess_bayes_risk": float(
                        route_context[name][
                            "true_oracle_excess_bayes_risk"
                        ].mean().item()
                    ),
                    "mean_true_action_risk": float(
                        route_context[name]["action_risk"].mean().item()
                    ),
                    "minimum_raw_excess_before_numerical_clipping": float(
                        route_context[name][
                            "raw_excess_before_numerical_clipping"
                        ].min().item()
                    ),
                    "candidate_risk_max_abs_difference_from_direct": float(
                        torch.abs(
                            route_candidate[name] - direct_candidate
                        ).max(dim=-1).values.mean().item()
                    ),
                    "selected_component_disagreement_from_direct": float(
                        (
                            route_candidate[name].argmin(dim=-1)
                            != direct_candidate.argmin(dim=-1)
                        ).to(torch.float32).mean().item()
                    ),
                }
                for name in attribution["route_regret_attribution"]["routes"]
            },
            "mean_context_worst_route_true_oracle_excess_bayes_risk": float(
                excess_stack.max(dim=1).values.mean().item()
            ),
            "maximum_route_mean_true_oracle_excess_bayes_risk": float(
                excess_stack.mean(dim=0).max().item()
            ),
            "true_oracle_bayes_risk": float(oracle_risk.mean().item()),
        }
        aggregate[model_name] = model_aggregate
        per_context[model_name] = {
            "routes": {
                name: {
                    key: value.detach().cpu().tolist()
                    for key, value in route_context[name].items()
                }
                for name in attribution["route_regret_attribution"]["routes"]
            },
            "worst_route_true_oracle_excess_bayes_risk": (
                excess_stack.max(dim=1).values.detach().cpu().tolist()
            ),
        }
    return (
        aggregate,
        per_context,
        true_functional_samples,
        oracle_summary,
    )


def _acquisition_budget_key(outer: int, inner: int) -> str:
    return f"outer_{outer}_inner_{inner}"


def _evaluate_acquisition_scaling(
    attribution: Mapping[str, Any],
    n1c: Mapping[str, Any],
    n0: Mapping[str, Any],
    models: Mapping[str, Any],
    test: Mapping[str, Any],
    functional_location: Any,
    functional_scale: Any,
    functional_grid_minimum: Any,
    functional_grid_maximum: Any,
    *,
    seed_index: int,
    true_candidate_risks: Mapping[str, Any] | None,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
]:
    budgets = list(attribution["acquisition_mc_attribution"]["sample_budgets"])
    budgets.sort(
        key=lambda item: (
            item != attribution["acquisition_mc_attribution"][
                "reference_budget"
            ],
            -int(item["outer"]),
            -int(item["inner"]),
        )
    )
    aggregate: dict[str, Any] = {}
    per_context: dict[str, Any] = {}
    summaries: list[dict[str, Any]] = []
    true_risks = true_candidate_risks
    for budget in budgets:
        candidate = deepcopy(n1c)
        candidate["acquisition_evaluation"]["outer_measurement_samples"] = int(
            budget["outer"]
        )
        candidate["acquisition_evaluation"]["inner_posterior_samples"] = int(
            budget["inner"]
        )
        result, context, true_risks, solver = _evaluate_acquisition(
            candidate,
            n0,
            models,
            test,
            functional_location,
            functional_scale,
            functional_grid_minimum,
            functional_grid_maximum,
            seed_index=seed_index,
            true_candidate_risks=true_risks,
        )
        key = _acquisition_budget_key(
            int(budget["outer"]), int(budget["inner"])
        )
        aggregate[key] = result
        per_context[key] = context
        summaries.extend(solver)

    reference = attribution["acquisition_mc_attribution"]["reference_budget"]
    reference_key = _acquisition_budget_key(
        int(reference["outer"]), int(reference["inner"])
    )
    for key, context in per_context.items():
        aggregate[key]["policy_stability_to_reference_budget"] = {}
        for mask_name in n1c["acquisition_evaluation"]["base_masks"]:
            aggregate[key]["policy_stability_to_reference_budget"][
                mask_name
            ] = {}
            for policy in (
                "aurora_expected_functional_risk_reduction",
                "acflow_expected_functional_risk_reduction",
            ):
                selected = context[mask_name][policy]["selected_component"]
                reference_selected = per_context[reference_key][mask_name][
                    policy
                ]["selected_component"]
                agreement = sum(
                    left == right
                    for left, right in zip(selected, reference_selected)
                ) / len(selected)
                aggregate[key]["policy_stability_to_reference_budget"][
                    mask_name
                ][policy] = agreement
    return aggregate, per_context, dict(true_risks or {}), summaries


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attribution-config", type=Path, required=True)
    parser.add_argument("--n0-config", type=Path, required=True)
    parser.add_argument("--checkpoint-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    n1, n1c, attribution, manifest = load_n1c_attribution_config(
        args.attribution_config
    )
    n0 = json.loads(args.n0_config.read_text(encoding="utf-8"))
    import torch

    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("N1c attribution requires CUDA.")
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
    (args.output / "attribution_config.sha256").write_text(
        _sha256(args.attribution_config) + "\n", encoding="utf-8"
    )

    pod_hash = manifest["shared_representation"]["sha256"]
    for seed_run in manifest["seed_runs"]:
        directory = args.checkpoint_root / f"seed_{seed_run['seed_index']}"
        if _sha256(directory / "train_only_pod_representation.pt") != pod_hash:
            raise NonlinearDecisionError("Shared POD checkpoint hash mismatch.")
        for name, expected in seed_run["checkpoint_sha256"].items():
            if _sha256(directory / f"{name}.pt") != expected:
                raise NonlinearDecisionError(
                    f"Frozen checkpoint changed: seed "
                    f"{seed_run['seed_index']} {name}."
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

    seed_metrics = []
    seed_context = []
    true_solver_cache = None
    true_route_functionals = None
    true_acquisition_risks = None
    oracle_summaries: list[dict[str, Any]] = []
    for seed_run in manifest["seed_runs"]:
        seed_index = int(seed_run["seed_index"])
        print(f"N1c-a seed {seed_index}: loading frozen models", flush=True)
        run_contract = dict(seed_run)
        run_contract["pod_sha256"] = pod_hash
        models = _load_models(
            n1,
            run_contract,
            args.checkpoint_root / f"seed_{seed_index}",
            device,
        )
        density, density_context = _evaluate_density(
            attribution, n1c, models, test
        )
        energy, energy_context, true_solver_cache, summaries = (
            _evaluate_energy_decomposition(
                attribution,
                n1c,
                n0,
                models,
                test,
                functional_location,
                functional_scale,
                seed_index=seed_index,
                true_solver_cache=true_solver_cache,
            )
        )
        oracle_summaries.extend(summaries)
        route, route_context, true_route_functionals, route_summary = (
            _evaluate_corrected_routes(
                attribution,
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
        if route_summary is not None:
            oracle_summaries.append(route_summary)
        acquisition, acquisition_context, true_acquisition_risks, summaries = (
            _evaluate_acquisition_scaling(
                attribution,
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
                "conditional_density": density,
                "functional_energy_decomposition": energy,
                "corrected_route_regret": route,
                "acquisition_mc_scaling": acquisition,
            }
        )
        seed_context.append(
            {
                "seed_index": seed_index,
                "conditional_density": density_context,
                "functional_energy_decomposition": energy_context,
                "corrected_route_regret": route_context,
                "acquisition_mc_scaling": acquisition_context,
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
        print(f"N1c-a seed {seed_index}: complete", flush=True)

    raw = {
        "schema_version": "aurora.nonlinear_pde_n1c_attribution.result.v1",
        "experiment_id": attribution["experiment_id"],
        "stage": attribution["stage"],
        "evidence_status": "exploratory_post_result_attribution",
        "git_commit": args.git_commit,
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_runtime": torch.version.cuda,
            "gpu_name": (
                torch.cuda.get_device_name(0)
                if torch.cuda.is_available()
                else None
            ),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "source": {
            "attribution_config_sha256": _sha256(args.attribution_config),
            "n1c_config_sha256": attribution["parents"]["n1c_config"][
                "sha256"
            ],
            "failed_n1c_result_sha256": attribution["parents"][
                "n1c_public_result"
            ]["sha256"],
            "checkpoint_manifest_sha256": n1c["parents"][
                "checkpoint_manifest"
            ]["sha256"],
        },
        "test_reuse": {
            "same_open_n1c_test": True,
            "new_test_seed": False,
            "checkpoint_or_model_selection": False,
            "contexts": int(n1c["test_lock"]["operator_test_contexts"]),
            "conditions_per_context": int(
                n1c["test_lock"]["conditions_per_context"]
            ),
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
                item["maximum_normalized_residual"]
                for item in oracle_summaries
            ),
        },
        "seeds": seed_metrics,
        "interpretation_contract": {
            "has_success_threshold": False,
            "n1c_verdict": "failed_unchanged",
            "n1d_or_irregular_3d_authorized": False,
            "method_novelty_established": False,
            "fresh_test_required_after_any_method_change": True,
        },
    }
    _write_json(args.output / "metrics.json", raw)
    _write_json(
        args.output / "status.json",
        {
            "state": "completed",
            "evidence_status": "exploratory_post_result_attribution",
            "n1c_verdict": "failed_unchanged",
            "n1d_or_irregular_3d_authorized": False,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
