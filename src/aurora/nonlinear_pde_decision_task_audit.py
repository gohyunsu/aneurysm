"""Method-independent adequacy audit for the nonlinear acquisition task."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from aurora.nonlinear_pde import load_config as load_n0_config
from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    load_config as load_n1_config,
)
from aurora.nonlinear_pde_evaluation import (
    bounded_bayes_action,
    sample_radius_truncated_conditional_gmm,
    standardize_functionals,
)


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_keys(
    payload: Mapping[str, Any],
    keys: Sequence[str],
    label: str,
) -> None:
    missing = sorted(set(keys) - set(payload))
    if missing:
        raise NonlinearDecisionError(f"{label} is missing keys: {missing}")


def load_decision_task_audit_config(
    path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load the frozen true-law/true-simulator task-audit contract."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        (
            "schema_version",
            "experiment_id",
            "status",
            "stage",
            "parents",
            "has_success_threshold",
            "uses_learned_model_or_checkpoint",
            "may_access_or_generate_n1_test",
            "may_relabel_n1c",
            "may_select_a_method",
            "may_authorize_n1d_or_irregular_3d",
            "may_establish_method_novelty",
            "data",
            "functional_contract",
            "base_masks",
            "monte_carlo",
            "estimands",
            "reporting",
        ),
        "Decision-task audit config",
    )
    if (
        payload["schema_version"]
        != "aurora.nonlinear_pde_n1_decision_task_audit.v1"
        or payload["status"] != "preregistered_development_before_output"
        or payload["stage"] != "threshold_free_method_independent_task_audit"
    ):
        raise NonlinearDecisionError("Unexpected decision-task audit status.")
    for key in (
        "has_success_threshold",
        "uses_learned_model_or_checkpoint",
        "may_access_or_generate_n1_test",
        "may_relabel_n1c",
        "may_select_a_method",
        "may_authorize_n1d_or_irregular_3d",
        "may_establish_method_novelty",
    ):
        if payload[key] is not False:
            raise NonlinearDecisionError(
                "Decision-task audit cannot train, gate, select, relabel, or claim."
            )

    parents = payload["parents"]
    n1_path = (config_path.parent / parents["n1_config"]["path"]).resolve()
    n0_path = (config_path.parent / parents["n0_solver_config"]["path"]).resolve()
    attribution_path = (
        config_path.parent / parents["n1c_attribution_result"]["path"]
    ).resolve()
    for candidate, contract, label in (
        (n1_path, parents["n1_config"], "N1 config"),
        (n0_path, parents["n0_solver_config"], "N0 solver config"),
        (
            attribution_path,
            parents["n1c_attribution_result"],
            "N1c-a result",
        ),
    ):
        if not candidate.is_file() or _sha256(candidate) != contract["sha256"]:
            raise NonlinearDecisionError(f"Pinned {label} changed.")
    if (
        parents["n1c_attribution_result"]["public_commit"]
        != "5eb3b869e93c1557c777259281396bf247688dad"
    ):
        raise NonlinearDecisionError("Task audit must pin the N1c-a release.")
    attribution = json.loads(attribution_path.read_text(encoding="utf-8"))
    if (
        attribution["evidence_status"]
        != "post_result_exploratory_attribution_completed"
        or attribution["decision"]["n1c_status"]
        != "completed_failed_unchanged"
        or attribution["decision"]["n1d_or_irregular_3d_authorized"] is not False
        or attribution["decision"]["fresh_reentry_registered"] is not False
    ):
        raise NonlinearDecisionError("Task audit requires completed failed N1c-a.")
    n1 = load_n1_config(n1_path)
    n0 = load_n0_config(n0_path)

    if payload["data"] != {
        "calibration_contexts": 384,
        "calibration_conditions_per_context": 8,
        "audit_contexts": 96,
        "audit_conditions_per_context": 1,
        "context_support": [-0.8, 0.8],
        "maximum_latent_mahalanobis_radius": 2.5,
        "solver_batch_size": 2048,
        "split_seeds": {
            "calibration_context": 73080684,
            "calibration_boundary": 73081684,
            "audit_context": 73080685,
            "audit_boundary": 73081685,
        },
        "n1_test_context_seed_accessed": False,
        "n1_test_boundary_seed_accessed": False,
    }:
        raise NonlinearDecisionError("Decision-task data lock changed.")
    if payload["functional_contract"] != {
        "functionals": [
            "domain_mean",
            "central_hotspot",
            "smooth_maximum",
            "right_boundary_flux",
        ],
        "standardization": "true_simulator_calibration_split_only",
        "action_grid_range": "calibration_standardized_minimum_to_maximum",
        "action_grid_points": 129,
        "bounded_loss": "clip_squared_standardized_error_to_unit_interval",
        "average_equal_weight_over_four_functionals": True,
    }:
        raise NonlinearDecisionError("Decision-task functional contract changed.")
    if payload["base_masks"] != {"missing": [], "sparse_2": [0, 2]}:
        raise NonlinearDecisionError("Decision-task masks changed.")
    monte_carlo = payload["monte_carlo"]
    if (
        int(monte_carlo["base_posterior_samples"]) != 2048
        or int(monte_carlo["base_seed"]) != 73080921
        or monte_carlo["replicates"]
        != [
            {
                "id": "replicate_a",
                "outer_measurement_samples": 32,
                "inner_posterior_samples": 64,
                "outer_seed": 73080901,
                "inner_seed": 73080911,
            },
            {
                "id": "replicate_b",
                "outer_measurement_samples": 32,
                "inner_posterior_samples": 64,
                "outer_seed": 73080902,
                "inner_seed": 73080912,
            },
        ]
        or monte_carlo["same_outer_full_boundary_draws_across_candidates"]
        is not True
        or monte_carlo["same_inner_random_stream_across_candidates"] is not True
        or monte_carlo["replicates_independent"] is not True
    ):
        raise NonlinearDecisionError("Decision-task Monte Carlo contract changed.")
    if not all(payload["estimands"].values()):
        raise NonlinearDecisionError("Decision-task estimands cannot be dropped.")
    if (
        payload["reporting"]["no_task_threshold_or_pass_fail_label"] is not True
        or payload["reporting"]["retain_n1c_failed"] is not True
    ):
        raise NonlinearDecisionError("Decision-task reporting boundary changed.")
    return n1, n0, payload


def _quantiles(values: Any) -> dict[str, float]:
    import torch
    probability = values.new_tensor([0.1, 0.25, 0.5, 0.75, 0.9])
    quantile = torch.quantile(values, probability)
    return {
        "q10": float(quantile[0].item()),
        "q25": float(quantile[1].item()),
        "median": float(quantile[2].item()),
        "q75": float(quantile[3].item()),
        "q90": float(quantile[4].item()),
    }


def _normalized_entropy(index: Any, categories: int) -> tuple[float, list[int]]:
    import torch
    counts = torch.bincount(index, minlength=categories)
    probability = counts.to(torch.float64)
    probability = probability / probability.sum().clamp_min(1.0)
    positive = probability > 0
    entropy = -(probability[positive] * torch.log(probability[positive])).sum()
    normalizer = math.log(categories) if categories > 1 else 1.0
    return float((entropy / normalizer).item()), counts.cpu().tolist()


def _correlation(first: Any, second: Any) -> float:
    import torch

    centered_first = first - first.mean()
    centered_second = second - second.mean()
    denominator = (
        torch.linalg.vector_norm(centered_first)
        * torch.linalg.vector_norm(centered_second)
    )
    if float(denominator.item()) <= 1e-12:
        return 1.0 if bool((first == second).all()) else 0.0
    return float(
        ((centered_first * centered_second).sum() / denominator).item()
    )
def _calibration_statistics(calibration_split: Mapping[str, Any]) -> dict[str, Any]:
    functional = calibration_split["functionals"].reshape(-1, 4)
    location = functional.mean(dim=0)
    scale = functional.std(dim=0, unbiased=False).clamp_min(1e-4)
    standardized = standardize_functionals(functional, location, scale)
    return {
        "location": location,
        "scale": scale,
        "grid_minimum": standardized.min(dim=0).values,
        "grid_maximum": standardized.max(dim=0).values,
        "raw_minimum": functional.min(dim=0).values,
        "raw_maximum": functional.max(dim=0).values,
    }


def _base_posterior(
    *,
    context: Any,
    observed: Any,
    weights: Any,
    means: Any,
    covariances: Any,
    positions: Sequence[int],
    calibration: Mapping[str, Any],
    audit_config: Mapping[str, Any],
    solve_functionals: Callable[[Any, Any], tuple[Any, Mapping[str, Any]]],
    mask_offset: int,
) -> tuple[Any, Any, dict[str, Any], Mapping[str, Any]]:
    samples = int(audit_config["monte_carlo"]["base_posterior_samples"])
    boundary = sample_radius_truncated_conditional_gmm(
        weights,
        means,
        covariances,
        positions,
        observed[:, positions],
        samples=samples,
        seed=int(audit_config["monte_carlo"]["base_seed"]) + 1000 * mask_offset,
        maximum_radius=float(
            audit_config["data"]["maximum_latent_mahalanobis_radius"]
        ),
    )
    expanded_context = (
        context[:, None].expand(-1, samples, -1).reshape(-1, 5)
    )
    functional, solver = solve_functionals(
        expanded_context,
        boundary.reshape(-1, 8),
    )
    standardized = standardize_functionals(
        functional.reshape(context.shape[0], samples, 4),
        calibration["location"],
        calibration["scale"],
    )
    action, risk = bounded_bayes_action(
        standardized,
        calibration["grid_minimum"],
        calibration["grid_maximum"],
        grid_points=int(
            audit_config["functional_contract"]["action_grid_points"]
        ),
    )
    summary = {
        "risk": risk.mean(dim=-1),
        "action": action,
        "action_unique_counts": [
            int(action[:, index].unique().numel()) for index in range(4)
        ],
        "action_standard_deviation": action.std(
            dim=0, unbiased=False
        ).detach().cpu().tolist(),
    }
    return action, risk.mean(dim=-1), summary, solver


def _replicate_candidate_risks(
    *,
    context: Any,
    observed: Any,
    weights: Any,
    means: Any,
    covariances: Any,
    positions: Sequence[int],
    base_action: Any,
    calibration: Mapping[str, Any],
    audit_config: Mapping[str, Any],
    replicate: Mapping[str, Any],
    solve_functionals: Callable[[Any, Any], tuple[Any, Mapping[str, Any]]],
    mask_offset: int,
) -> tuple[dict[str, Any], dict[str, Any], list[Mapping[str, Any]]]:
    import torch

    candidates = [index for index in range(8) if index not in positions]
    outer = int(replicate["outer_measurement_samples"])
    inner = int(replicate["inner_posterior_samples"])
    outer_boundary = sample_radius_truncated_conditional_gmm(
        weights,
        means,
        covariances,
        positions,
        observed[:, positions],
        samples=outer,
        seed=int(replicate["outer_seed"]) + 1000 * mask_offset,
        maximum_radius=float(
            audit_config["data"]["maximum_latent_mahalanobis_radius"]
        ),
    )
    expanded_context = (
        context[:, None].expand(-1, outer, -1).reshape(-1, 5)
    )
    expanded_weights = (
        weights[:, None].expand(-1, outer, -1).reshape(-1, 2)
    )
    expanded_means = (
        means[:, None].expand(-1, outer, -1, -1).reshape(-1, 2, 8)
    )
    expanded_covariances = (
        covariances[:, None]
        .expand(-1, outer, -1, -1, -1)
        .reshape(-1, 2, 8, 8)
    )
    risks = []
    action_change = []
    solver_summaries: list[Mapping[str, Any]] = []
    for candidate in candidates:
        revealed = observed[:, None].expand(-1, outer, -1).clone()
        revealed[:, :, candidate] = outer_boundary[:, :, candidate]
        revealed = revealed.reshape(-1, 8)
        new_positions = sorted([*positions, candidate])
        completion = sample_radius_truncated_conditional_gmm(
            expanded_weights,
            expanded_means,
            expanded_covariances,
            new_positions,
            revealed[:, new_positions],
            samples=inner,
            seed=int(replicate["inner_seed"]) + 1000 * mask_offset,
            maximum_radius=float(
                audit_config["data"]["maximum_latent_mahalanobis_radius"]
            ),
        )
        functional, solver = solve_functionals(
            expanded_context[:, None]
            .expand(-1, inner, -1)
            .reshape(-1, 5),
            completion.reshape(-1, 8),
        )
        solver_summaries.append(solver)
        standardized = standardize_functionals(
            functional.reshape(expanded_context.shape[0], inner, 4),
            calibration["location"],
            calibration["scale"],
        )
        action, risk = bounded_bayes_action(
            standardized,
            calibration["grid_minimum"],
            calibration["grid_maximum"],
            grid_points=int(
                audit_config["functional_contract"]["action_grid_points"]
            ),
        )
        risks.append(
            risk.mean(dim=-1)
            .reshape(context.shape[0], outer)
            .mean(dim=1)
        )
        changed = (
            action.reshape(context.shape[0], outer, 4)
            != base_action[:, None]
        ).to(torch.float32)
        action_change.append(changed.mean(dim=(1, 2)))
    risk_matrix = torch.stack(risks, dim=1)
    change_matrix = torch.stack(action_change, dim=1)
    order = torch.argsort(risk_matrix, dim=1)
    winner_local = order[:, 0]
    second_local = order[:, 1]
    candidate_tensor = torch.tensor(
        candidates, device=context.device, dtype=torch.long
    )
    winner_component = candidate_tensor[winner_local]
    best = torch.gather(risk_matrix, 1, winner_local[:, None]).squeeze(1)
    second = torch.gather(risk_matrix, 1, second_local[:, None]).squeeze(1)
    margin = second - best
    winner_change = torch.gather(
        change_matrix, 1, winner_local[:, None]
    ).squeeze(1)
    entropy, counts = _normalized_entropy(winner_local, len(candidates))
    aggregate = {
        "winner_component_counts": {
            str(component): int(count)
            for component, count in zip(candidates, counts)
        },
        "winner_components_observed": int(sum(count > 0 for count in counts)),
        "normalized_selected_component_entropy": entropy,
        "best_post_acquisition_risk_mean": float(best.mean().item()),
        "first_second_margin_mean": float(margin.mean().item()),
        "first_second_margin_quantiles": _quantiles(margin),
        "candidate_risk_dispersion_mean": float(
            risk_matrix.std(dim=1, unbiased=False).mean().item()
        ),
        "winner_action_change_rate_mean": float(winner_change.mean().item()),
    }
    per_context = {
        "candidate_components": candidates,
        "candidate_risk": risk_matrix.detach().cpu().tolist(),
        "winner_component": winner_component.detach().cpu().tolist(),
        "best_post_acquisition_risk": best.detach().cpu().tolist(),
        "first_second_margin": margin.detach().cpu().tolist(),
        "winner_action_change_rate": winner_change.detach().cpu().tolist(),
    }
    tensors = {
        "risk_matrix": risk_matrix,
        "winner_local": winner_local,
        "winner_component": winner_component,
        "best_risk": best,
        "margin": margin,
        "winner_action_change": winner_change,
    }
    return {**aggregate, "_tensors": tensors}, per_context, solver_summaries


def evaluate_true_decision_task(
    *,
    calibration_split: Mapping[str, Any],
    audit_split: Mapping[str, Any],
    audit_config: Mapping[str, Any],
    solve_functionals: Callable[[Any, Any], tuple[Any, Mapping[str, Any]]],
) -> tuple[dict[str, Any], dict[str, Any], list[Mapping[str, Any]]]:
    """Audit acquisition identifiability using only the true law and simulator."""

    import torch

    calibration = _calibration_statistics(calibration_split)
    context = audit_split["context"]
    observed = audit_split["boundary"][:, 0]
    weights = audit_split["true_weights"]
    means = audit_split["true_means"]
    covariances = audit_split["true_covariances"]
    aggregate: dict[str, Any] = {
        "calibration": {
            "contexts": int(calibration_split["context"].shape[0]),
            "conditions_per_context": int(
                calibration_split["boundary"].shape[1]
            ),
            "functional_location": calibration["location"].cpu().tolist(),
            "functional_scale": calibration["scale"].cpu().tolist(),
            "functional_raw_minimum": calibration["raw_minimum"].cpu().tolist(),
            "functional_raw_maximum": calibration["raw_maximum"].cpu().tolist(),
        },
        "masks": {},
    }
    per_context: dict[str, Any] = {}
    solver_summaries: list[Mapping[str, Any]] = [calibration_split["solver"]]
    for mask_offset, (mask_name, positions) in enumerate(
        audit_config["base_masks"].items()
    ):
        base_action, base_risk, base_summary, base_solver = _base_posterior(
            context=context,
            observed=observed,
            weights=weights,
            means=means,
            covariances=covariances,
            positions=positions,
            calibration=calibration,
            audit_config=audit_config,
            solve_functionals=solve_functionals,
            mask_offset=mask_offset,
        )
        solver_summaries.append(base_solver)
        mask_aggregate: dict[str, Any] = {
            "base_no_acquisition_risk_mean": float(base_risk.mean().item()),
            "base_bayes_action_unique_counts": base_summary[
                "action_unique_counts"
            ],
            "base_bayes_action_standard_deviation": base_summary[
                "action_standard_deviation"
            ],
            "replicates": {},
        }
        mask_context: dict[str, Any] = {
            "base_no_acquisition_risk": base_risk.detach().cpu().tolist(),
            "replicates": {},
        }
        replicate_tensors = {}
        for replicate in audit_config["monte_carlo"]["replicates"]:
            result, raw, summaries = _replicate_candidate_risks(
                context=context,
                observed=observed,
                weights=weights,
                means=means,
                covariances=covariances,
                positions=positions,
                base_action=base_action,
                calibration=calibration,
                audit_config=audit_config,
                replicate=replicate,
                solve_functionals=solve_functionals,
                mask_offset=mask_offset,
            )
            solver_summaries.extend(summaries)
            tensors = result.pop("_tensors")
            value_of_information = base_risk - tensors["best_risk"]
            relative_margin = tensors["margin"] / base_risk.clamp_min(1e-8)
            result.update(
                {
                    "no_acquisition_minus_best_post_acquisition_risk_mean": float(
                        value_of_information.mean().item()
                    ),
                    "value_of_information_positive_fraction": float(
                        (value_of_information > 0).to(torch.float32).mean().item()
                    ),
                    "value_of_information_quantiles": _quantiles(
                        value_of_information
                    ),
                    "relative_first_second_margin_mean": float(
                        relative_margin.mean().item()
                    ),
                    "relative_first_second_margin_quantiles": _quantiles(
                        relative_margin
                    ),
                }
            )
            raw["no_acquisition_minus_best_post_acquisition_risk"] = (
                value_of_information.detach().cpu().tolist()
            )
            raw["relative_first_second_margin"] = (
                relative_margin.detach().cpu().tolist()
            )
            replicate_id = str(replicate["id"])
            mask_aggregate["replicates"][replicate_id] = result
            mask_context["replicates"][replicate_id] = raw
            replicate_tensors[replicate_id] = tensors

        first_id, second_id = [
            str(item["id"]) for item in audit_config["monte_carlo"]["replicates"]
        ]
        first = replicate_tensors[first_id]
        second = replicate_tensors[second_id]
        first_top2 = torch.sort(
            torch.argsort(first["risk_matrix"], dim=1)[:, :2], dim=1
        ).values
        second_top2 = torch.sort(
            torch.argsort(second["risk_matrix"], dim=1)[:, :2], dim=1
        ).values
        mask_aggregate["replicate_stability"] = {
            "winner_agreement": float(
                (first["winner_local"] == second["winner_local"])
                .to(torch.float32)
                .mean()
                .item()
            ),
            "top2_set_agreement": float(
                (first_top2 == second_top2)
                .all(dim=1)
                .to(torch.float32)
                .mean()
                .item()
            ),
            "candidate_risk_correlation": _correlation(
                first["risk_matrix"].flatten(),
                second["risk_matrix"].flatten(),
            ),
            "candidate_risk_mean_absolute_difference": float(
                torch.abs(first["risk_matrix"] - second["risk_matrix"])
                .mean()
                .item()
            ),
            "winner_margin_mean_absolute_difference": float(
                torch.abs(first["margin"] - second["margin"]).mean().item()
            ),
        }
        aggregate["masks"][mask_name] = mask_aggregate
        per_context[mask_name] = mask_context
    aggregate["interpretation_boundary"] = {
        "has_success_threshold": False,
        "uses_learned_model_or_checkpoint": False,
        "n1c_verdict_unchanged": True,
        "method_or_gate_selected": False,
        "irregular_3d_authorized": False,
    }
    return aggregate, per_context, solver_summaries
