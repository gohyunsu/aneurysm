"""Prospective missing-condition operator-pullback mechanism gate.

The proposed training control keeps one joint boundary density.  In addition
to full-joint likelihood, it scores the joint pushforward of each candidate
measurement and the registered PDE solution functionals.  The experiment is
validation-only, does not access N1 test data, and cannot authorize 3D work.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    build_joint_density,
    gmm_nll,
    load_config as load_n1_config,
)
from aurora.nonlinear_pde_evaluation import (
    bounded_bayes_action,
    radius_truncated_conditional_gmm_nll,
    sample_radius_truncated_conditional_gmm,
    standardize_functionals,
)


VARIANT_IDS = (
    "full_joint_mle",
    "full_joint_plus_boundary_kernel",
    "full_joint_plus_solution_marginal_kernel",
    "full_joint_plus_candidate_solution_joint_pullback",
)
PROPOSED_VARIANT = "full_joint_plus_candidate_solution_joint_pullback"


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


def load_operator_pullback_config(
    path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load and validate the result-blind M0 development contract."""

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
            "scope_lock",
            "method_hypothesis",
            "theory_contract",
            "data",
            "model_seeds",
            "frozen_operator",
            "architecture_lock",
            "objective_variants",
            "score_lock",
            "optimization_lock",
            "checkpoint_selection",
            "audit_evaluation",
            "mechanism_gate",
            "reporting",
        ),
        "Operator-pullback M0 config",
    )
    if (
        payload["schema_version"]
        != "aurora.nonlinear_pde_n1_missing_operator_pullback_m0.v1"
        or payload["status"] != "preregistered_before_development_output"
        or payload["stage"] != "prospective_validation_only_mechanism_gate"
    ):
        raise NonlinearDecisionError("Unexpected operator-pullback M0 status.")

    scope = payload["scope_lock"]
    if (
        scope["base_mask"] != "missing"
        or scope["observed_components"] != []
        or scope["candidate_components"] != list(range(8))
        or scope["sparse_2_is_fixed_acquisition_control_only"] is not True
        or scope["may_access_or_generate_n1_test"] is not False
        or scope["may_relabel_n1c"] is not False
        or scope["may_authorize_n1d_or_irregular_3d"] is not False
        or scope["may_establish_method_novelty"] is not False
        or scope["pass_only_allows_fresh_reentry_protocol_design"] is not True
    ):
        raise NonlinearDecisionError("M0 scope or authority changed.")

    expected_parent_hashes = {
        "n1_config": "757b742587b2d52860648a42e6c58721716c6675366f5b3b6329d6a695eb0891",
        "n0_solver_config": "cb5d6b0891083bc9460d5557d5c04b708c25dffa09e90e0b951af0dc3dcfcaaf",
        "density_objective_result": "94686547ea927324cd4e376c3500067176843b401511d519e993864ea199b147",
        "decision_task_result": "4492a7759fc08b4c2ac81196e2c345634419215f89030b062356aa801e232ab7",
        "operator_checkpoint_manifest": "4dd22e9f6e8c85662a5352ba123e122fd542a03e4d4131f24ba702629937ad7f",
    }
    parent_paths: dict[str, Path] = {}
    for name, expected_hash in expected_parent_hashes.items():
        contract = payload["parents"][name]
        parent = (config_path.parent / contract["path"]).resolve()
        if (
            not parent.is_file()
            or contract["sha256"] != expected_hash
            or _sha256(parent) != expected_hash
        ):
            raise NonlinearDecisionError(f"Pinned M0 parent changed: {name}.")
        parent_paths[name] = parent

    density_result = json.loads(
        parent_paths["density_objective_result"].read_text(encoding="utf-8")
    )
    task_result = json.loads(
        parent_paths["decision_task_result"].read_text(encoding="utf-8")
    )
    manifest = json.loads(
        parent_paths["operator_checkpoint_manifest"].read_text(encoding="utf-8")
    )
    if (
        density_result["decision"]["method_novelty_established"] is not False
        or density_result["decision"]["fresh_reentry_registered"] is not False
        or density_result["decision"]["n1d_or_irregular_3d_authorized"] is not False
        or density_result["decision"]["n1c_status"]
        != "completed_failed_unchanged"
    ):
        raise NonlinearDecisionError("M0 requires the non-selecting density audit.")
    if (
        task_result["decision"]["method_novelty_established"] is not False
        or task_result["decision"]["fresh_reentry_registered"] is not False
        or task_result["decision"]["n1d_or_irregular_3d_authorized"] is not False
        or task_result["decision"]["n1c_status"]
        != "completed_failed_unchanged"
    ):
        raise NonlinearDecisionError("M0 requires the method-free task audit.")
    if (
        manifest["decision"]["all_five_seed_checkpoints_eligible"] is not True
        or manifest["decision"]["all_checkpoint_hashes_frozen"] is not True
    ):
        raise NonlinearDecisionError("M0 requires the frozen N1b checkpoint set.")

    data = payload["data"]
    if data != {
        "train_contexts": 3072,
        "selection_validation_contexts": 384,
        "audit_validation_contexts": 192,
        "conditions_per_context": 8,
        "acquisition_audit_contexts": 96,
        "context_support": [-0.8, 0.8],
        "maximum_latent_mahalanobis_radius": 2.5,
        "solver_batch_size": 2048,
        "split_seeds": {
            "train_context": 73081081,
            "train_boundary": 73082081,
            "selection_context": 73081082,
            "selection_boundary": 73082082,
            "audit_context": 73081083,
            "audit_boundary": 73082083,
        },
        "n1_test_context_seed_accessed": False,
        "n1_test_boundary_seed_accessed": False,
    }:
        raise NonlinearDecisionError("M0 data lock changed.")
    if payload["model_seeds"] != [73081021, 73081022, 73081023]:
        raise NonlinearDecisionError("M0 development seeds changed.")
    if [item["id"] for item in payload["objective_variants"]] != list(
        VARIANT_IDS
    ):
        raise NonlinearDecisionError("M0 objective variants changed.")
    hypothesis = payload["method_hypothesis"]
    if (
        hypothesis["construction"]
        != "one_joint_boundary_density_plus_candidate_measurement_solution_joint_kernel_scores_through_a_frozen_full_condition_operator"
        or hypothesis["no_acquisition_head"] is not True
        or hypothesis[
            "all_post_measurement_conditionals_come_from_the_same_joint_density"
        ]
        is not True
        or hypothesis["proposed_variant_id"] != PROPOSED_VARIANT
    ):
        raise NonlinearDecisionError("M0 method hypothesis changed.")
    if payload["architecture_lock"] != {
        "density_family": "context_conditioned_two_component_full_covariance_gmm",
        "hidden_width": 192,
        "hidden_layers": 3,
        "same_initial_state_within_seed": True,
    }:
        raise NonlinearDecisionError("M0 density architecture changed.")
    frozen_operator = payload["frozen_operator"]
    if (
        frozen_operator["checkpoint_id"]
        != "aurora_shared_operator_pair_loss_zero"
        or frozen_operator["manifest_seed_indices"] != [0, 1, 2]
        or frozen_operator["full_condition_only"] is not True
        or frozen_operator["parameters_frozen"] is not True
        or frozen_operator[
            "used_for_training_pullback_and_model_policy_only"
        ]
        is not True
        or frozen_operator[
            "true_simulator_used_for_audit_metrics_and_oracle_risk"
        ]
        is not True
        or float(
            frozen_operator[
                "maximum_audit_validation_full_bc_relative_l2"
            ]
        )
        != 0.05
    ):
        raise NonlinearDecisionError("M0 frozen-operator contract changed.")
    for index in frozen_operator["manifest_seed_indices"]:
        seed_run = manifest["seed_runs"][index]
        if (
            int(seed_run["seed_index"]) != index
            or seed_run["checkpoint_seed_eligible"] is not True
            or "aurora_shared_operator_pair_loss_zero"
            not in seed_run["checkpoint_sha256"]
            or float(
                seed_run["validation"][
                    "pair_loss_zero_paired_response_relative_l2"
                ]
            )
            > 0.05
        ):
            raise NonlinearDecisionError(
                "M0 frozen operator is not checkpoint-eligible."
            )
    score = payload["score_lock"]
    if (
        score["kernel"] != "equal_weight_multiscale_rbf"
        or score["kernel_scales"] != [0.5, 1.0, 2.0]
        or score["distance"]
        != "mean_squared_standardized_coordinate_distance"
        or score["candidate_joint_kernel"]
        != "product_of_candidate_component_kernel_and_solution_functional_kernel"
        or score["mixture_estimator"]
        != "component_stratified_unbiased_two_draw_kernel_score"
        or score["draws_per_component_per_set"] != 1
        or float(score["kernel_score_weight"]) != 0.25
        or float(score["maximum_latent_radius_applied_to_standard_draws"])
        != 2.5
    ):
        raise NonlinearDecisionError("M0 score lock changed.")
    optimization = payload["optimization_lock"]
    if optimization != {
        "maximum_steps": 1200,
        "batch_size": 512,
        "learning_rate": 0.001,
        "weight_decay": 0.00001,
        "validation_interval": 20,
        "early_stopping_patience": 15,
        "gradient_clip_norm": 5.0,
        "same_minibatch_indices_within_seed": True,
        "same_kernel_random_numbers_within_seed": True,
    }:
        raise NonlinearDecisionError("M0 optimization lock changed.")
    if payload["checkpoint_selection"] != {
        "split": "selection_validation_only",
        "metric": "full_joint_nll_per_component_plus_0_25_candidate_measurement_solution_joint_kernel_score",
        "same_metric_for_all_variants": True,
        "cross_variant_selection": False,
    }:
        raise NonlinearDecisionError("M0 checkpoint selection changed.")
    audit = payload["audit_evaluation"]
    acquisition = audit["acquisition"]
    if (
        int(audit["true_simulator_pushforward_samples"]) != 64
        or int(audit["model_pushforward_samples"]) != 64
        or audit["candidate_joint_metric"]
        != "nonnegative_biased_multiscale_kernel_MMD_squared_average_over_eight_components"
        or audit["solution_metric"]
        != "nonnegative_biased_multiscale_kernel_MMD_squared"
        or int(audit["bootstrap_replicates"]) != 2000
        or int(acquisition["outer_measurement_samples"]) != 32
        or int(acquisition["inner_posterior_samples"]) != 64
        or int(acquisition["action_grid_points"]) != 129
        or acquisition["same_true_candidate_risk_across_variants"] is not True
        or acquisition[
            "common_random_numbers_across_variants_and_candidates"
        ]
        is not True
        or acquisition["oracle"]
        != "true_boundary_law_and_true_simulator"
    ):
        raise NonlinearDecisionError("M0 audit estimand changed.")
    gate = payload["mechanism_gate"]
    if (
        gate["all_checks_required"] is not True
        or gate["strongest_control_selection"]
        != "lowest_three_seed_mean_separately_for_each_primary_metric"
        or gate["relative_improvement_estimand"] != "three_seed_mean"
        or gate["paired_context_bootstrap"]
        != "average_three_paired_seed_differences_then_resample_context_family"
        or gate["density_and_solution_degradation_estimand"]
        != "three_seed_mean"
        or gate["operator_checkpoint_check"]
        != "every_seed_audit_validation_full_bc_relative_l2"
        or gate["candidate_joint_mmd_relative_improvement_over_strongest_control_minimum"]
        != 0.05
        or gate["candidate_joint_mmd_better_seed_directions_minimum"] != 3
        or gate["acquisition_regret_relative_improvement_over_strongest_control_minimum"]
        != 0.05
        or gate["acquisition_regret_better_seed_directions_minimum"] != 3
        or gate[
            "candidate_joint_mmd_paired_context_bootstrap_ci95_upper_below_zero"
        ]
        is not True
        or gate[
            "acquisition_regret_paired_context_bootstrap_ci95_upper_below_zero"
        ]
        is not True
        or gate["missing_density_excess_relative_degradation_vs_full_joint_maximum"]
        != 0.05
        or gate["solution_marginal_mmd_relative_degradation_vs_full_joint_maximum"]
        != 0.01
        or gate["operator_checkpoint_validation_error_maximum"] != 0.05
        or gate["pass_is_development_mechanism_eligibility_only"] is not True
        or gate["failure_abandons_this_mechanism_without_local_weight_or_kernel_repair"]
        is not True
    ):
        raise NonlinearDecisionError("M0 mechanism gate changed.")
    reporting = payload["reporting"]
    if (
        reporting["raw_history_checkpoints_and_per_context_metrics_private"]
        is not True
        or reporting["public_output_aggregate_only_after_completion"] is not True
        or reporting["retain_n1c_failed"] is not True
        or reporting["retain_method_unselected_until_gate_result"] is not True
        or reporting[
            "new_fresh_reentry_requires_separate_public_version_and_new_five_seeds"
        ]
        is not True
    ):
        raise NonlinearDecisionError("M0 reporting boundary changed.")

    n1 = load_n1_config(parent_paths["n1_config"])
    return n1, payload, manifest


def _clone_state(module: Any) -> dict[str, Any]:
    return {
        key: value.detach().cpu().clone()
        for key, value in module.state_dict().items()
    }


def _flatten_solution_split(split: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    contexts, conditions = split["boundary"].shape[:2]
    context = (
        split["context"][:, None]
        .expand(-1, conditions, -1)
        .reshape(-1, 5)
    )
    return (
        context,
        split["boundary"].reshape(-1, 8),
        split["functionals"].reshape(contexts * conditions, 4),
    )


def training_standardization(split: Mapping[str, Any]) -> dict[str, Any]:
    """Compute all score and action scales from the training split only."""

    import torch

    _, boundary, functional = _flatten_solution_split(split)
    boundary_location = boundary.mean(dim=0)
    boundary_scale = boundary.std(dim=0, unbiased=False).clamp_min(1e-4)
    functional_location = functional.mean(dim=0)
    functional_scale = functional.std(dim=0, unbiased=False).clamp_min(1e-4)
    standardized_functional = standardize_functionals(
        functional, functional_location, functional_scale
    )
    return {
        "boundary_location": boundary_location,
        "boundary_scale": boundary_scale,
        "functional_location": functional_location,
        "functional_scale": functional_scale,
        "functional_grid_minimum": standardized_functional.min(dim=0).values,
        "functional_grid_maximum": standardized_functional.max(dim=0).values,
    }


def _multiscale_rbf(
    first: Any,
    second: Any,
    scales: Sequence[float],
) -> Any:
    squared = (first - second).square().mean(dim=-1)
    return sum(
        (-0.5 * squared / float(scale) ** 2).exp() for scale in scales
    ) / len(scales)


def _weighted_score(
    weights: Any,
    pair_kernel: Any,
    target_kernel: Any,
) -> Any:
    pair = (
        weights[:, :, None] * weights[:, None, :] * pair_kernel
    ).sum(dim=(1, 2))
    target = (weights * target_kernel).sum(dim=1)
    return pair - 2.0 * target


def boundary_kernel_score(
    weights: Any,
    first: Any,
    second: Any,
    target: Any,
    scales: Sequence[float],
) -> Any:
    pair = _multiscale_rbf(
        first[:, :, None, :], second[:, None, :, :], scales
    )
    target_kernel = _multiscale_rbf(first, target[:, None], scales)
    return _weighted_score(weights, pair, target_kernel)


def solution_kernel_score(
    weights: Any,
    first: Any,
    second: Any,
    target: Any,
    scales: Sequence[float],
) -> Any:
    return boundary_kernel_score(weights, first, second, target, scales)


def candidate_joint_kernel_score(
    weights: Any,
    first_boundary: Any,
    first_functional: Any,
    second_boundary: Any,
    second_functional: Any,
    target_boundary: Any,
    target_functional: Any,
    scales: Sequence[float],
) -> Any:
    """Score all (candidate component, solution functional) joint laws."""

    solution_pair = _multiscale_rbf(
        first_functional[:, :, None, :],
        second_functional[:, None, :, :],
        scales,
    )
    solution_target = _multiscale_rbf(
        first_functional, target_functional[:, None], scales
    )
    component_pair = []
    component_target = []
    for component in range(first_boundary.shape[-1]):
        component_pair.append(
            _multiscale_rbf(
                first_boundary[:, :, None, component : component + 1],
                second_boundary[:, None, :, component : component + 1],
                scales,
            )
        )
        component_target.append(
            _multiscale_rbf(
                first_boundary[:, :, component : component + 1],
                target_boundary[:, None, component : component + 1],
                scales,
            )
        )
    pair = solution_pair * sum(component_pair) / len(component_pair)
    target_kernel = (
        solution_target * sum(component_target) / len(component_target)
    )
    return _weighted_score(weights, pair, target_kernel)


def _truncated_standard(
    *,
    batch: int,
    mixtures: int,
    dimension: int,
    radius: float,
    seed: int,
    device: Any,
    dtype: Any,
) -> Any:
    import torch

    generator = torch.Generator(device=device).manual_seed(seed)
    result = torch.empty(
        batch, mixtures, dimension, device=device, dtype=dtype
    )
    accepted = torch.zeros(batch, mixtures, device=device, dtype=torch.bool)
    for _ in range(10000):
        if bool(accepted.all()):
            break
        proposal = torch.randn(
            batch,
            mixtures,
            dimension,
            generator=generator,
            device=device,
            dtype=dtype,
        )
        valid = (~accepted) & (
            torch.linalg.vector_norm(proposal, dim=-1) <= float(radius)
        )
        result[valid] = proposal[valid]
        accepted |= valid
    if not bool(accepted.all()):
        raise NonlinearDecisionError("M0 truncated score sampling stalled.")
    return result


def stratified_gmm_draws(
    means: Any,
    covariances: Any,
    standard: Any,
) -> Any:
    import torch

    dimension = means.shape[-1]
    cholesky = torch.linalg.cholesky(
        covariances
        + 1e-6
        * torch.eye(dimension, device=means.device, dtype=means.dtype)
    )
    return means + torch.einsum("bcij,bcj->bci", cholesky, standard)


def operator_functionals(
    operator: Any,
    context: Any,
    boundary: Any,
    *,
    chunk_size: int = 4096,
) -> Any:
    """Push boundary samples through a frozen full-condition operator."""

    import torch

    from aurora.nonlinear_pde import solution_functionals

    batch, samples = boundary.shape[:2]
    expanded_context = (
        context[:, None].expand(-1, samples, -1).reshape(-1, 5)
    )
    flat_boundary = boundary.reshape(-1, 8)
    values = []
    for start in range(0, flat_boundary.shape[0], chunk_size):
        end = min(start + chunk_size, flat_boundary.shape[0])
        field = operator(
            expanded_context[start:end], flat_boundary[start:end]
        )
        values.append(
            solution_functionals(field, expanded_context[start:end])
        )
    return torch.cat(values, dim=0).reshape(batch, samples, 4)


def _variant_objective(
    *,
    name: str,
    model: Any,
    operator: Any,
    context: Any,
    boundary: Any,
    target_functional: Any,
    standardization: Mapping[str, Any],
    score_lock: Mapping[str, Any],
    standard_first: Any,
    standard_second: Any,
) -> tuple[Any, dict[str, float]]:
    weights, means, covariances = model(context)
    nll = (gmm_nll(weights, means, covariances, boundary) / 8).mean()
    if name == "full_joint_mle":
        return nll, {"nll": float(nll.detach().item()), "score": 0.0}

    first = stratified_gmm_draws(means, covariances, standard_first)
    second = stratified_gmm_draws(means, covariances, standard_second)
    boundary_location = standardization["boundary_location"]
    boundary_scale = standardization["boundary_scale"]
    first_boundary = (first - boundary_location) / boundary_scale
    second_boundary = (second - boundary_location) / boundary_scale
    target_boundary = (boundary - boundary_location) / boundary_scale
    scales = score_lock["kernel_scales"]

    if name == "full_joint_plus_boundary_kernel":
        score = boundary_kernel_score(
            weights,
            first_boundary,
            second_boundary,
            target_boundary,
            scales,
        ).mean()
    else:
        first_functional = standardize_functionals(
            operator_functionals(operator, context, first),
            standardization["functional_location"],
            standardization["functional_scale"],
        )
        second_functional = standardize_functionals(
            operator_functionals(operator, context, second),
            standardization["functional_location"],
            standardization["functional_scale"],
        )
        target_standard = standardize_functionals(
            target_functional,
            standardization["functional_location"],
            standardization["functional_scale"],
        )
        if name == "full_joint_plus_solution_marginal_kernel":
            score = solution_kernel_score(
                weights,
                first_functional,
                second_functional,
                target_standard,
                scales,
            ).mean()
        elif name == PROPOSED_VARIANT:
            score = candidate_joint_kernel_score(
                weights,
                first_boundary,
                first_functional,
                second_boundary,
                second_functional,
                target_boundary,
                target_standard,
                scales,
            ).mean()
        else:  # pragma: no cover - guarded by the contract
            raise NonlinearDecisionError(f"Unknown M0 variant: {name}.")
    objective = nll + float(score_lock["kernel_score_weight"]) * score
    return objective, {
        "nll": float(nll.detach().item()),
        "score": float(score.detach().item()),
    }


def _selection_objective(
    *,
    model: Any,
    operator: Any,
    context: Any,
    boundary: Any,
    functional: Any,
    standardization: Mapping[str, Any],
    config: Mapping[str, Any],
    seed: int,
) -> tuple[float, dict[str, float]]:
    import torch

    chunks = []
    nll_values = []
    score_values = []
    batch_size = int(config["optimization_lock"]["batch_size"])
    with torch.no_grad():
        for start in range(0, context.shape[0], batch_size):
            end = min(start + batch_size, context.shape[0])
            weights, means, covariances = model(context[start:end])
            standard_first = _truncated_standard(
                batch=end - start,
                mixtures=means.shape[1],
                dimension=means.shape[2],
                radius=float(
                    config["score_lock"][
                        "maximum_latent_radius_applied_to_standard_draws"
                    ]
                ),
                seed=seed + start,
                device=means.device,
                dtype=means.dtype,
            )
            standard_second = _truncated_standard(
                batch=end - start,
                mixtures=means.shape[1],
                dimension=means.shape[2],
                radius=float(
                    config["score_lock"][
                        "maximum_latent_radius_applied_to_standard_draws"
                    ]
                ),
                seed=seed + 10000 + start,
                device=means.device,
                dtype=means.dtype,
            )
            first = stratified_gmm_draws(means, covariances, standard_first)
            second = stratified_gmm_draws(means, covariances, standard_second)
            first_boundary = (
                first - standardization["boundary_location"]
            ) / standardization["boundary_scale"]
            second_boundary = (
                second - standardization["boundary_location"]
            ) / standardization["boundary_scale"]
            target_boundary = (
                boundary[start:end] - standardization["boundary_location"]
            ) / standardization["boundary_scale"]
            first_functional = standardize_functionals(
                operator_functionals(
                    operator, context[start:end], first
                ),
                standardization["functional_location"],
                standardization["functional_scale"],
            )
            second_functional = standardize_functionals(
                operator_functionals(
                    operator, context[start:end], second
                ),
                standardization["functional_location"],
                standardization["functional_scale"],
            )
            target_functional = standardize_functionals(
                functional[start:end],
                standardization["functional_location"],
                standardization["functional_scale"],
            )
            score = candidate_joint_kernel_score(
                weights,
                first_boundary,
                first_functional,
                second_boundary,
                second_functional,
                target_boundary,
                target_functional,
                config["score_lock"]["kernel_scales"],
            )
            nll = gmm_nll(
                weights, means, covariances, boundary[start:end]
            ) / 8
            objective = nll + float(
                config["score_lock"]["kernel_score_weight"]
            ) * score
            chunks.append(objective.detach())
            nll_values.append(nll.detach())
            score_values.append(score.detach())
    return (
        float(torch.cat(chunks).mean().item()),
        {
            "full_joint_nll_per_component": float(
                torch.cat(nll_values).mean().item()
            ),
            "candidate_joint_kernel_score": float(
                torch.cat(score_values).mean().item()
            ),
        },
    )


def train_operator_pullback_variants(
    *,
    n1_config: Mapping[str, Any],
    config: Mapping[str, Any],
    train_split: Mapping[str, Any],
    selection_split: Mapping[str, Any],
    operator: Any,
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Train all four M0 variants under paired initialization and randomness."""

    import torch

    torch.manual_seed(seed)
    device = train_split["context"].device
    operator.eval()
    for parameter in operator.parameters():
        parameter.requires_grad_(False)
    standardization = training_standardization(train_split)
    template = build_joint_density(n1_config, device)
    initial_state = _clone_state(template)
    models = {}
    for name in VARIANT_IDS:
        model = build_joint_density(n1_config, device)
        model.load_state_dict(initial_state)
        models[name] = model

    lock = config["optimization_lock"]
    optimizers = {
        name: torch.optim.AdamW(
            model.parameters(),
            lr=float(lock["learning_rate"]),
            weight_decay=float(lock["weight_decay"]),
        )
        for name, model in models.items()
    }
    generators = {
        name: torch.Generator(device=device).manual_seed(seed + 101)
        for name in models
    }
    train_context, train_boundary, train_functional = _flatten_solution_split(
        train_split
    )
    (
        selection_context,
        selection_boundary,
        selection_functional,
    ) = _flatten_solution_split(selection_split)
    best = {name: math.inf for name in models}
    best_state = {name: _clone_state(model) for name, model in models.items()}
    best_record: dict[str, dict[str, Any]] = {name: {} for name in models}
    wait = {name: 0 for name in models}
    traces = {name: [] for name in models}
    active = set(models)
    batch_size = int(lock["batch_size"])
    maximum_steps = int(lock["maximum_steps"])
    interval = int(lock["validation_interval"])
    patience = int(lock["early_stopping_patience"])
    radius = float(
        config["score_lock"][
            "maximum_latent_radius_applied_to_standard_draws"
        ]
    )

    for step in range(1, maximum_steps + 1):
        common_first = _truncated_standard(
            batch=batch_size,
            mixtures=2,
            dimension=8,
            radius=radius,
            seed=seed + 100000 + step,
            device=device,
            dtype=train_context.dtype,
        )
        common_second = _truncated_standard(
            batch=batch_size,
            mixtures=2,
            dimension=8,
            radius=radius,
            seed=seed + 200000 + step,
            device=device,
            dtype=train_context.dtype,
        )
        for name in tuple(active):
            index = torch.randint(
                0,
                train_context.shape[0],
                (batch_size,),
                generator=generators[name],
                device=device,
            )
            objective, parts = _variant_objective(
                name=name,
                model=models[name],
                operator=operator,
                context=train_context[index],
                boundary=train_boundary[index],
                target_functional=train_functional[index],
                standardization=standardization,
                score_lock=config["score_lock"],
                standard_first=common_first,
                standard_second=common_second,
            )
            optimizers[name].zero_grad(set_to_none=True)
            objective.backward()
            torch.nn.utils.clip_grad_norm_(
                models[name].parameters(),
                float(lock["gradient_clip_norm"]),
            )
            optimizers[name].step()
            traces[name].append(
                {
                    "step": step,
                    "training_objective": float(objective.detach().item()),
                    **parts,
                }
            )

        if step % interval != 0:
            continue
        for name in tuple(active):
            models[name].eval()
            selection, parts = _selection_objective(
                model=models[name],
                operator=operator,
                context=selection_context,
                boundary=selection_boundary,
                functional=selection_functional,
                standardization=standardization,
                config=config,
                seed=seed + 300000,
            )
            traces[name][-1]["selection_objective"] = selection
            traces[name][-1]["selection_parts"] = parts
            if selection < best[name] - 1e-5:
                best[name] = selection
                best_state[name] = _clone_state(models[name])
                best_record[name] = {
                    "step": step,
                    "selection_objective": selection,
                    **parts,
                }
                wait[name] = 0
            else:
                wait[name] += 1
                if wait[name] >= patience:
                    active.remove(name)
            models[name].train()
        if not active:
            break

    for name, model in models.items():
        model.load_state_dict(best_state[name])
        model.eval()
    serializable_standardization = {
        key: value.detach().cpu().tolist()
        for key, value in standardization.items()
    }
    return models, serializable_standardization, {
        "paired_initialization": True,
        "paired_minibatch_indices": True,
        "paired_kernel_random_numbers": True,
        "models": {
            name: {
                "best_record": best_record[name],
                "steps_executed": traces[name][-1]["step"],
                "trace": traces[name],
            }
            for name in models
        },
    }


def _biased_mmd(
    first: Any,
    second: Any,
    kernel: Callable[[Any, Any], Any],
) -> Any:
    """Return a nonnegative empirical MMD-squared estimate per context."""

    pair_first = kernel(first[:, :, None], first[:, None, :])
    pair_second = kernel(second[:, :, None], second[:, None, :])
    cross = kernel(first[:, :, None], second[:, None, :])
    return (
        pair_first.mean(dim=(1, 2))
        + pair_second.mean(dim=(1, 2))
        - 2.0 * cross.mean(dim=(1, 2))
    ).clamp_min(0.0)


def solution_mmd(
    first: Any,
    second: Any,
    scales: Sequence[float],
) -> Any:
    return _biased_mmd(
        first,
        second,
        lambda left, right: _multiscale_rbf(left, right, scales),
    )


def candidate_joint_mmd(
    first_boundary: Any,
    first_functional: Any,
    second_boundary: Any,
    second_functional: Any,
    scales: Sequence[float],
) -> Any:
    values = []
    for component in range(first_boundary.shape[-1]):
        first = (
            first_boundary[:, :, component : component + 1],
            first_functional,
        )
        second = (
            second_boundary[:, :, component : component + 1],
            second_functional,
        )

        def kernel(left: Any, right: Any) -> Any:
            left_boundary, left_functional = left
            right_boundary, right_functional = right
            return _multiscale_rbf(
                left_boundary, right_boundary, scales
            ) * _multiscale_rbf(
                left_functional, right_functional, scales
            )

        pair_first = kernel(
            (first[0][:, :, None], first[1][:, :, None]),
            (first[0][:, None, :], first[1][:, None, :]),
        )
        pair_second = kernel(
            (second[0][:, :, None], second[1][:, :, None]),
            (second[0][:, None, :], second[1][:, None, :]),
        )
        cross = kernel(
            (first[0][:, :, None], first[1][:, :, None]),
            (second[0][:, None, :], second[1][:, None, :]),
        )
        first_term = pair_first.mean(dim=(1, 2))
        second_term = pair_second.mean(dim=(1, 2))
        values.append(
            (
                first_term
                + second_term
                - 2.0 * cross.mean(dim=(1, 2))
            ).clamp_min(0.0)
        )
    return sum(values) / len(values)


def candidate_risk_matrix(
    *,
    weights: Any,
    means: Any,
    covariances: Any,
    context: Any,
    functional_evaluator: Callable[[Any, Any], tuple[Any, Mapping[str, Any]]],
    standardization: Mapping[str, Any],
    config: Mapping[str, Any],
    outer_seed: int,
    inner_seed: int,
) -> tuple[Any, list[Mapping[str, Any]]]:
    """Estimate one-component post-measurement Bayes risk for all candidates."""

    import torch

    acquisition = config["audit_evaluation"]["acquisition"]
    outer = int(acquisition["outer_measurement_samples"])
    inner = int(acquisition["inner_posterior_samples"])
    radius = float(config["data"]["maximum_latent_mahalanobis_radius"])
    empty = context.new_empty(context.shape[0], 0)
    outer_boundary = sample_radius_truncated_conditional_gmm(
        weights,
        means,
        covariances,
        [],
        empty,
        samples=outer,
        seed=outer_seed,
        maximum_radius=radius,
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
    summaries = []
    for candidate in range(8):
        observed = outer_boundary[:, :, candidate].reshape(-1, 1)
        completion = sample_radius_truncated_conditional_gmm(
            expanded_weights,
            expanded_means,
            expanded_covariances,
            [candidate],
            observed,
            samples=inner,
            seed=inner_seed + candidate,
            maximum_radius=radius,
        )
        functional, summary = functional_evaluator(
            expanded_context[:, None]
            .expand(-1, inner, -1)
            .reshape(-1, 5),
            completion.reshape(-1, 8),
        )
        summaries.append(summary)
        standardized = standardize_functionals(
            functional.reshape(expanded_context.shape[0], inner, 4),
            standardization["functional_location"],
            standardization["functional_scale"],
        )
        _, risk = bounded_bayes_action(
            standardized,
            standardization["functional_grid_minimum"],
            standardization["functional_grid_maximum"],
            grid_points=int(acquisition["action_grid_points"]),
        )
        risks.append(
            risk.mean(dim=-1)
            .reshape(context.shape[0], outer)
            .mean(dim=1)
        )
    return torch.stack(risks, dim=1), summaries


def evaluate_operator_pullback_variants(
    *,
    models: Mapping[str, Any],
    audit_split: Mapping[str, Any],
    operator: Any,
    standardization_payload: Mapping[str, Any],
    config: Mapping[str, Any],
    solve_functionals: Callable[[Any, Any], tuple[Any, Mapping[str, Any]]],
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any], list[Mapping[str, Any]]]:
    """Evaluate density, true-simulator pushforwards, and acquisition regret."""

    import torch

    device = audit_split["context"].device
    standardization = {
        key: torch.tensor(value, device=device, dtype=audit_split["context"].dtype)
        for key, value in standardization_payload.items()
    }
    contexts, conditions = audit_split["boundary"].shape[:2]
    flat_context, flat_boundary, _ = _flatten_solution_split(audit_split)
    true_weights = (
        audit_split["true_weights"][:, None]
        .expand(-1, conditions, -1)
        .reshape(-1, 2)
    )
    true_means = (
        audit_split["true_means"][:, None]
        .expand(-1, conditions, -1, -1)
        .reshape(-1, 2, 8)
    )
    true_covariances = (
        audit_split["true_covariances"][:, None]
        .expand(-1, conditions, -1, -1, -1)
        .reshape(-1, 2, 8, 8)
    )
    true_nll = radius_truncated_conditional_gmm_nll(
        true_weights,
        true_means,
        true_covariances,
        flat_boundary,
        [],
        maximum_radius=float(
            config["data"]["maximum_latent_mahalanobis_radius"]
        ),
    ) / 8
    true_context_nll = true_nll.reshape(contexts, conditions).mean(dim=1)

    context = audit_split["context"]
    pushforward_samples = int(
        config["audit_evaluation"]["true_simulator_pushforward_samples"]
    )
    empty = context.new_empty(context.shape[0], 0)
    true_boundary = sample_radius_truncated_conditional_gmm(
        audit_split["true_weights"],
        audit_split["true_means"],
        audit_split["true_covariances"],
        [],
        empty,
        samples=pushforward_samples,
        seed=seed + 400000,
        maximum_radius=float(
            config["data"]["maximum_latent_mahalanobis_radius"]
        ),
    )
    expanded_context = (
        context[:, None]
        .expand(-1, pushforward_samples, -1)
        .reshape(-1, 5)
    )
    true_functional, true_summary = solve_functionals(
        expanded_context, true_boundary.reshape(-1, 8)
    )
    true_functional = standardize_functionals(
        true_functional.reshape(contexts, pushforward_samples, 4),
        standardization["functional_location"],
        standardization["functional_scale"],
    )
    true_boundary_standard = (
        true_boundary - standardization["boundary_location"]
    ) / standardization["boundary_scale"]

    acquisition_contexts = int(config["data"]["acquisition_audit_contexts"])
    acquisition_context = context[:acquisition_contexts]
    true_risk, true_risk_summaries = candidate_risk_matrix(
        weights=audit_split["true_weights"][:acquisition_contexts],
        means=audit_split["true_means"][:acquisition_contexts],
        covariances=audit_split["true_covariances"][:acquisition_contexts],
        context=acquisition_context,
        functional_evaluator=solve_functionals,
        standardization=standardization,
        config=config,
        outer_seed=seed + 500000,
        inner_seed=seed + 510000,
    )
    oracle_local = true_risk.argmin(dim=1)
    oracle_risk = torch.gather(
        true_risk, 1, oracle_local[:, None]
    ).squeeze(1)

    def learned_functionals(
        candidate_context: Any, candidate_boundary: Any
    ) -> tuple[Any, Mapping[str, Any]]:
        boundary_samples = candidate_boundary[:, None]
        values = operator_functionals(
            operator, candidate_context, boundary_samples
        ).squeeze(1)
        return values, {
            "source": "frozen_full_condition_operator",
            "all_converged": True,
        }

    aggregate = {}
    per_context = {}
    solver_summaries: list[Mapping[str, Any]] = [
        true_summary,
        *true_risk_summaries,
    ]
    scales = config["score_lock"]["kernel_scales"]
    for name, model in models.items():
        with torch.no_grad():
            weights, means, covariances = model(flat_context)
            learned_nll = (
                gmm_nll(weights, means, covariances, flat_boundary) / 8
            )
            learned_context_nll = learned_nll.reshape(
                contexts, conditions
            ).mean(dim=1)
            excess = learned_context_nll - true_context_nll

            model_weights, model_means, model_covariances = model(context)
            model_boundary = sample_radius_truncated_conditional_gmm(
                model_weights,
                model_means,
                model_covariances,
                [],
                empty,
                samples=pushforward_samples,
                seed=seed + 600000,
                maximum_radius=float(
                    config["data"]["maximum_latent_mahalanobis_radius"]
                ),
            )
        model_functional_raw, model_summary = solve_functionals(
            expanded_context, model_boundary.reshape(-1, 8)
        )
        solver_summaries.append(model_summary)
        model_functional = standardize_functionals(
            model_functional_raw.reshape(
                contexts, pushforward_samples, 4
            ),
            standardization["functional_location"],
            standardization["functional_scale"],
        )
        model_boundary_standard = (
            model_boundary - standardization["boundary_location"]
        ) / standardization["boundary_scale"]
        solution_distance = solution_mmd(
            model_functional, true_functional, scales
        )
        joint_distance = candidate_joint_mmd(
            model_boundary_standard,
            model_functional,
            true_boundary_standard,
            true_functional,
            scales,
        )

        with torch.no_grad():
            policy_weights, policy_means, policy_covariances = model(
                acquisition_context
            )
        model_risk, model_risk_summaries = candidate_risk_matrix(
            weights=policy_weights,
            means=policy_means,
            covariances=policy_covariances,
            context=acquisition_context,
            functional_evaluator=learned_functionals,
            standardization=standardization,
            config=config,
            outer_seed=seed + 700000,
            inner_seed=seed + 710000,
        )
        solver_summaries.extend(model_risk_summaries)
        selected_local = model_risk.argmin(dim=1)
        selected_true_risk = torch.gather(
            true_risk, 1, selected_local[:, None]
        ).squeeze(1)
        regret = selected_true_risk - oracle_risk
        agreement = (selected_local == oracle_local).to(torch.float32)

        aggregate[name] = {
            "missing_conditional_nll_per_component": float(
                learned_context_nll.mean().item()
            ),
            "missing_excess_over_true_law": float(excess.mean().item()),
            "true_simulator_solution_mmd_squared": float(
                solution_distance.mean().item()
            ),
            "true_simulator_candidate_joint_mmd_squared": float(
                joint_distance.mean().item()
            ),
            "true_oracle_acquisition_regret": float(regret.mean().item()),
            "selected_component_agreement_with_true_oracle": float(
                agreement.mean().item()
            ),
        }
        per_context[name] = {
            "missing_excess_over_true_law": excess.detach().cpu().tolist(),
            "true_simulator_solution_mmd_squared": (
                solution_distance.detach().cpu().tolist()
            ),
            "true_simulator_candidate_joint_mmd_squared": (
                joint_distance.detach().cpu().tolist()
            ),
            "true_oracle_acquisition_regret": regret.detach().cpu().tolist(),
            "selected_component_agreement_with_true_oracle": (
                agreement.detach().cpu().tolist()
            ),
            "selected_component": selected_local.detach().cpu().tolist(),
            "true_oracle_component": oracle_local.detach().cpu().tolist(),
        }
    return aggregate, per_context, solver_summaries
