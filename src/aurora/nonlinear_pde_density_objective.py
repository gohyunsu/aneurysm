"""Validation-only attribution of nonlinear boundary-density objectives.

The audit keeps the N1 joint-GMM architecture, data budget, optimizer, initial
weights, minibatches, and checkpoint metric fixed.  It changes only the
training objective.  It has no success threshold and cannot relabel N1c.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    build_joint_density,
    conditional_joint_nll,
    gmm_nll,
    load_config as load_n1_config,
)
from aurora.nonlinear_pde_evaluation import (
    radius_truncated_conditional_gmm_nll,
)


VARIANT_IDS = (
    "n1c_random_mask_raw",
    "random_mask_per_component",
    "full_joint_per_component",
    "registered_composite_per_component",
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


def load_density_objective_audit_config(
    path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load the frozen, non-gating density-objective audit contract."""

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
            "may_access_or_generate_n1_test",
            "may_relabel_n1c",
            "may_select_a_method",
            "may_authorize_n1d_or_irregular_3d",
            "may_establish_method_novelty",
            "data",
            "model_seeds",
            "architecture_lock",
            "optimization_lock",
            "objective_variants",
            "checkpoint_selection",
            "audit_evaluation",
            "reporting",
        ),
        "Density-objective audit config",
    )
    if (
        payload["schema_version"]
        != "aurora.nonlinear_pde_n1_density_objective_audit.v1"
        or payload["status"] != "preregistered_development_before_output"
        or payload["stage"] != "threshold_free_validation_only_attribution"
    ):
        raise NonlinearDecisionError("Unexpected density-objective audit status.")
    for key in (
        "has_success_threshold",
        "may_access_or_generate_n1_test",
        "may_relabel_n1c",
        "may_select_a_method",
        "may_authorize_n1d_or_irregular_3d",
        "may_establish_method_novelty",
    ):
        if payload[key] is not False:
            raise NonlinearDecisionError(
                "Density-objective audit cannot gate, select, relabel, or claim."
            )

    parents = payload["parents"]
    n1_path = (config_path.parent / parents["n1_config"]["path"]).resolve()
    attribution_path = (
        config_path.parent / parents["n1c_attribution_result"]["path"]
    ).resolve()
    if (
        not n1_path.is_file()
        or _sha256(n1_path) != parents["n1_config"]["sha256"]
    ):
        raise NonlinearDecisionError("Pinned N1 config changed.")
    if (
        not attribution_path.is_file()
        or _sha256(attribution_path)
        != parents["n1c_attribution_result"]["sha256"]
    ):
        raise NonlinearDecisionError("Pinned N1c-a result changed.")
    if (
        parents["n1c_attribution_result"]["public_commit"]
        != "5eb3b869e93c1557c777259281396bf247688dad"
    ):
        raise NonlinearDecisionError("Density audit must pin the N1c-a release.")
    attribution = json.loads(attribution_path.read_text(encoding="utf-8"))
    if (
        attribution["evidence_status"]
        != "post_result_exploratory_attribution_completed"
        or attribution["decision"]["n1c_status"]
        != "completed_failed_unchanged"
        or attribution["decision"]["n1d_or_irregular_3d_authorized"] is not False
        or attribution["decision"]["fresh_reentry_registered"] is not False
    ):
        raise NonlinearDecisionError("Density audit requires completed failed N1c-a.")
    n1 = load_n1_config(n1_path)

    data = payload["data"]
    if (
        data
        != {
            "train_contexts": 3072,
            "selection_validation_contexts": 384,
            "audit_validation_contexts": 384,
            "conditions_per_context": 8,
            "context_support": [-0.8, 0.8],
            "maximum_latent_mahalanobis_radius": 2.5,
            "split_seeds": {
                "train_context": 73080681,
                "train_boundary": 73081681,
                "selection_context": 73080682,
                "selection_boundary": 73081682,
                "audit_context": 73080683,
                "audit_boundary": 73081683,
            },
            "n1_test_context_seed_accessed": False,
            "n1_test_boundary_seed_accessed": False,
        }
    ):
        raise NonlinearDecisionError("Density-objective data lock changed.")
    seeds = [int(seed) for seed in payload["model_seeds"]]
    if seeds != [73080621, 73080622, 73080623, 73080624, 73080625]:
        raise NonlinearDecisionError("Density-objective development seeds changed.")
    forbidden = {
        *n1["model_seeds"]["development_only"],
        *n1["model_seeds"]["confirmatory"],
    }
    if forbidden & set(seeds):
        raise NonlinearDecisionError("Density-objective seeds overlap N1 seeds.")

    if payload["architecture_lock"] != {
        "family": "context_conditioned_two_component_full_covariance_gmm",
        "hidden_width": 192,
        "hidden_layers": 3,
        "same_initial_state_within_seed": True,
    }:
        raise NonlinearDecisionError("Density architecture lock changed.")
    expected_optimization = {
        "maximum_steps": 1800,
        "batch_size": 4096,
        "learning_rate": 0.001,
        "weight_decay": 0.00001,
        "validation_interval": 20,
        "early_stopping_patience": 15,
        "gradient_clip_norm": 5.0,
        "same_minibatch_indices_within_seed": True,
        "one_likelihood_evaluation_per_step": True,
    }
    if payload["optimization_lock"] != expected_optimization:
        raise NonlinearDecisionError("Density optimization lock changed.")
    variants = payload["objective_variants"]
    if [item["id"] for item in variants] != list(VARIANT_IDS):
        raise NonlinearDecisionError("Density objective variants changed.")
    if not all(item["method_novelty_claimed"] is False for item in variants):
        raise NonlinearDecisionError("Density objective controls are not novelty.")
    if payload["checkpoint_selection"] != {
        "split": "selection_validation_only",
        "metric": "equal_mask_mean_conditional_nll_per_unobserved_component",
        "masks": {
            "missing": [],
            "sparse_2": [0, 2],
            "partial_4": [0, 2, 5, 7],
        },
        "cross_variant_selection": False,
    }:
        raise NonlinearDecisionError("Density checkpoint selection changed.")
    audit = payload["audit_evaluation"]
    if (
        audit["split"] != "disjoint_audit_validation"
        or audit["masks"]
        != {
            "missing": [],
            "sparse_2": [0, 2],
            "partial_4": [0, 2, 5, 7],
        }
        or audit["true_reference"]
        != "exact_radius_truncated_context_conditioned_gmm"
        or audit["report_each_seed"] is not True
        or audit["report_no_test_access"] is not True
    ):
        raise NonlinearDecisionError("Density audit estimands changed.")
    return n1, payload


def _clone_state(module: Any) -> dict[str, Any]:
    return {
        key: value.detach().cpu().clone()
        for key, value in module.state_dict().items()
    }


def _flatten(split: Mapping[str, Any]) -> tuple[Any, Any]:
    conditions = split["boundary"].shape[1]
    context = (
        split["context"][:, None]
        .expand(-1, conditions, -1)
        .reshape(-1, 5)
    )
    return context, split["boundary"].reshape(-1, 8)


def _random_nonfull_mask(seed: int) -> list[int]:
    import numpy as np

    generator = np.random.default_rng(seed)
    selected = generator.random(8) < 0.5
    if bool(selected.all()):
        selected[int(seed % 8)] = False
    return [int(index) for index in np.flatnonzero(selected)]


def _registered_selection(
    model: Any,
    context: Any,
    boundary: Any,
    masks: Mapping[str, Sequence[int]],
) -> tuple[float, dict[str, float]]:
    import torch

    values: dict[str, float] = {}
    with torch.no_grad():
        for name, observed in masks.items():
            missing = 8 - len(observed)
            chunks = []
            for start in range(0, context.shape[0], 4096):
                end = min(start + 4096, context.shape[0])
                weights, means, covariances = model(context[start:end])
                chunks.append(
                    conditional_joint_nll(
                        weights,
                        means,
                        covariances,
                        boundary[start:end],
                        observed,
                    )
                    / missing
                )
            values[name] = float(torch.cat(chunks).mean().item())
    return sum(values.values()) / len(values), values


def train_density_objective_variants(
    *,
    n1_config: Mapping[str, Any],
    audit_config: Mapping[str, Any],
    train_split: Mapping[str, Any],
    selection_split: Mapping[str, Any],
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Train all objective variants under paired initialization and batches."""

    import torch

    torch.manual_seed(seed)
    device = train_split["context"].device
    template = build_joint_density(n1_config, device)
    initial_state = _clone_state(template)
    models = {}
    for variant in VARIANT_IDS:
        model = build_joint_density(n1_config, device)
        model.load_state_dict(initial_state)
        models[variant] = model

    lock = audit_config["optimization_lock"]
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
    train_context, train_boundary = _flatten(train_split)
    selection_context, selection_boundary = _flatten(selection_split)
    masks = audit_config["checkpoint_selection"]["masks"]
    mask_items = list(masks.items())
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

    for step in range(1, maximum_steps + 1):
        arbitrary = _random_nonfull_mask(seed + step)
        _, registered = mask_items[(step - 1) % len(mask_items)]
        for name in tuple(active):
            index = torch.randint(
                0,
                train_context.shape[0],
                (batch_size,),
                generator=generators[name],
                device=device,
            )
            context = train_context[index]
            boundary = train_boundary[index]
            weights, means, covariances = models[name](context)
            if name == "n1c_random_mask_raw":
                loss = conditional_joint_nll(
                    weights, means, covariances, boundary, arbitrary
                ).mean()
            elif name == "random_mask_per_component":
                loss = (
                    conditional_joint_nll(
                        weights, means, covariances, boundary, arbitrary
                    )
                    / (8 - len(arbitrary))
                ).mean()
            elif name == "full_joint_per_component":
                loss = (
                    gmm_nll(weights, means, covariances, boundary) / 8
                ).mean()
            else:
                loss = (
                    conditional_joint_nll(
                        weights, means, covariances, boundary, registered
                    )
                    / (8 - len(registered))
                ).mean()
            optimizers[name].zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                models[name].parameters(), float(lock["gradient_clip_norm"])
            )
            optimizers[name].step()
            traces[name].append(
                {"step": step, "training_objective": float(loss.detach().item())}
            )

        if step % interval != 0:
            continue
        for name in tuple(active):
            models[name].eval()
            selection, per_mask = _registered_selection(
                models[name],
                selection_context,
                selection_boundary,
                masks,
            )
            traces[name][-1]["selection_objective"] = selection
            traces[name][-1]["selection_per_mask"] = per_mask
            if selection < best[name] - 1e-5:
                best[name] = selection
                best_state[name] = _clone_state(models[name])
                best_record[name] = {
                    "step": step,
                    "selection_objective": selection,
                    "selection_per_mask": per_mask,
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
    return models, {
        "paired_initialization": True,
        "paired_minibatch_indices": True,
        "models": {
            name: {
                "best_record": best_record[name],
                "steps_executed": traces[name][-1]["step"],
                "likelihood_evaluations": traces[name][-1]["step"],
                "trace": traces[name],
            }
            for name in models
        },
    }


def evaluate_density_objective_variants(
    *,
    models: Mapping[str, Any],
    audit_split: Mapping[str, Any],
    audit_config: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Evaluate fixed checkpoints on a disjoint development-audit split."""

    import torch

    contexts, conditions = audit_split["boundary"].shape[:2]
    context, boundary = _flatten(audit_split)
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
    radius = float(audit_config["data"]["maximum_latent_mahalanobis_radius"])
    aggregate: dict[str, Any] = {}
    per_context: dict[str, Any] = {}
    for mask_name, observed in audit_config["audit_evaluation"]["masks"].items():
        missing = 8 - len(observed)
        true_nll = radius_truncated_conditional_gmm_nll(
            true_weights,
            true_means,
            true_covariances,
            boundary,
            observed,
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
        for name, model in models.items():
            chunks = []
            with torch.no_grad():
                for start in range(0, context.shape[0], 4096):
                    end = min(start + 4096, context.shape[0])
                    weights, means, covariances = model(context[start:end])
                    chunks.append(
                        conditional_joint_nll(
                            weights,
                            means,
                            covariances,
                            boundary[start:end],
                            observed,
                        )
                        / missing
                    )
            nll = torch.cat(chunks)
            context_nll = nll.reshape(contexts, conditions).mean(dim=1)
            excess = context_nll - true_context
            aggregate[mask_name][name] = {
                "conditional_nll_per_unobserved_component": float(
                    context_nll.mean().item()
                ),
                "excess_over_true_law": float(excess.mean().item()),
            }
            per_context[mask_name][name] = {
                "conditional_nll_per_unobserved_component": (
                    context_nll.detach().cpu().tolist()
                ),
                "excess_over_true_law": excess.detach().cpu().tolist(),
            }
    return aggregate, per_context
