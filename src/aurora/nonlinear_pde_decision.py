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


def load_optimization_config(path: str | Path) -> dict[str, Any]:
    """Load the threshold-free validation-only N1 optimization attribution."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        [
            "schema_version",
            "experiment_id",
            "status",
            "source_n1_config",
            "source_n1_config_sha256",
            "source_attempts",
            "stage",
            "has_success_threshold",
            "may_access_or_generate_test",
            "may_decide_n1",
            "may_authorize_confirmatory_or_irregular_3d",
            "may_establish_method_novelty",
            "development_seed",
            "data_contract",
            "model_contract",
            "factorial_variants",
            "normalization",
            "shared_training",
            "evaluation",
            "selection_rule",
            "interpretation",
        ],
        "N1 optimization attribution",
    )
    if (
        payload["schema_version"]
        != "aurora.nonlinear_pde_n1_optimization_attribution.v1"
        or payload["status"] != "preregistered_before_attribution_metric"
        or payload["stage"] != "validation_only_optimization_attribution"
    ):
        raise NonlinearDecisionError("Unexpected N1 optimization attribution status.")
    source_config = (config_path.parent / payload["source_n1_config"]).resolve()
    if (
        not source_config.is_file()
        or _sha256(source_config) != payload["source_n1_config_sha256"]
    ):
        raise NonlinearDecisionError("Pinned N1 config does not match attribution.")
    for item in payload["source_attempts"]:
        result = (config_path.parent / item["result"]).resolve()
        if not result.is_file() or _sha256(result) != item["sha256"]:
            raise NonlinearDecisionError("Pinned N1 development result changed.")
    for forbidden in (
        "has_success_threshold",
        "may_access_or_generate_test",
        "may_decide_n1",
        "may_authorize_confirmatory_or_irregular_3d",
        "may_establish_method_novelty",
    ):
        if payload[forbidden] is not False:
            raise NonlinearDecisionError("N1 attribution cannot define a gate or claim.")
    if int(payload["development_seed"]) != 73080503:
        raise NonlinearDecisionError("N1 attribution development seed changed.")
    if payload["data_contract"] != {
        "reuse_n1_train_validation_split_seeds": True,
        "operator_train_contexts": 768,
        "operator_validation_contexts": 192,
        "conditions_per_context": 12,
        "grid_points": 33,
        "test_contexts": 0,
    }:
        raise NonlinearDecisionError("N1 attribution data contract changed.")
    variants = {
        (item["id"], item["loss_conditioning"], int(item["maximum_steps"]))
        for item in payload["factorial_variants"]
    }
    expected = {
        ("raw_mse_1400", "raw_field_and_pair_mse", 1400),
        ("raw_mse_2800", "raw_field_and_pair_mse", 2800),
        (
            "scale_normalized_1400",
            "train_only_rms_normalized_field_and_pair_mse",
            1400,
        ),
        (
            "scale_normalized_2800",
            "train_only_rms_normalized_field_and_pair_mse",
            2800,
        ),
    }
    if variants != expected:
        raise NonlinearDecisionError("N1 attribution factorial changed.")
    selection = payload["selection_rule"]
    if (
        selection["select_lowest_validation_objective"] is not True
        or selection["within_one_percent_choose_fewer_steps"] is not True
        or selection["selection_is_architecture_development_not_gate_evidence"]
        is not True
        or selection[
            "selected_variant_requires_new_prospective_n1_version_before_confirmatory_test"
        ]
        is not True
    ):
        raise NonlinearDecisionError("N1 attribution selection rule changed.")
    return payload


def load_n1b_config(path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load the post-N1a prospective checkpoint-freeze overlay."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        [
            "schema_version",
            "experiment_id",
            "status",
            "parent_protocol",
            "selection_evidence",
            "selected_shared_operator_training",
            "direct_probabilistic_training",
            "completion_training",
            "checkpoint_freeze",
            "paired_control_contracts",
            "decision_evaluation",
            "success_rule",
            "claim_boundary",
            "interpretation",
        ],
        "N1b config",
    )
    if (
        payload["schema_version"] != "aurora.nonlinear_pde_n1b.v1"
        or payload["status"]
        != "preregistered_after_n1a_before_confirmatory_checkpoint_or_test"
    ):
        raise NonlinearDecisionError("Unexpected N1b prospective status.")

    parent_contract = payload["parent_protocol"]
    parent_path = (config_path.parent / parent_contract["config"]).resolve()
    if (
        not parent_path.is_file()
        or _sha256(parent_path) != parent_contract["sha256"]
    ):
        raise NonlinearDecisionError("Pinned parent N1 protocol changed.")
    parent = load_config(parent_path)

    selection_contract = payload["selection_evidence"]
    selection_path = (config_path.parent / selection_contract["result"]).resolve()
    if (
        not selection_path.is_file()
        or _sha256(selection_path) != selection_contract["sha256"]
    ):
        raise NonlinearDecisionError("Pinned N1a selection result changed.")
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selected = selection["selection"]
    if (
        selection_contract["selection_was_validation_only"] is not True
        or int(selection_contract["test_contexts_generated"]) != 0
        or selection_contract["test_seed_accessed"] is not False
        or selection_contract["has_gate_decision"] is not False
        or selected["selected_variant"] != "scale_normalized_2800"
        or selected["selected_loss_conditioning"]
        != "train_only_rms_normalized_field_and_pair_mse"
        or int(selected["selected_maximum_steps"]) != 2800
    ):
        raise NonlinearDecisionError("N1b does not preserve the N1a selection.")

    operator = payload["selected_shared_operator_training"]
    if (
        operator["family"]
        != "unit_peak_dirichlet_lifted_low_rank_coordinate_operator"
        or int(operator["rank"]) != 96
        or operator["loss_conditioning"]
        != "train_only_rms_normalized_field_and_pair_mse"
        or int(operator["maximum_steps"]) != 2800
        or operator["normalization_statistics_source"]
        != "operator_training_split_only"
        or operator["validation_and_test_targets_never_define_training_scale"]
        is not True
    ):
        raise NonlinearDecisionError("N1b selected operator contract changed.")

    direct = payload["direct_probabilistic_training"]
    if (
        direct["representation"] != "operator_train_only_centered_pod"
        or int(direct["latent_rank"]) != 96
        or int(direct["representation_seed"]) != 73080601
        or int(direct["randomized_pca_iterations"]) != 4
        or direct["fit_split"] != "operator_training_full_fields_only"
        or direct["pod_and_standardization_source"]
        != "operator_training_split_only"
        or direct["representation_error_reported_separately"] is not True
        or direct[
            "confirmatory_seed_controls_weight_initialization_and_batch_sampling"
        ]
        is not True
    ):
        raise NonlinearDecisionError("N1b direct baseline contract changed.")

    freeze = payload["checkpoint_freeze"]
    confirmatory = [int(seed) for seed in parent["model_seeds"]["confirmatory"]]
    if [int(seed) for seed in freeze["confirmatory_model_seeds"]] != confirmatory:
        raise NonlinearDecisionError("N1b confirmatory seeds changed.")
    required_checkpoints = {
        "aurora_joint_density",
        "independent_mask_heads",
        "lano_adapted_completion",
        "acflow_adapted_completion",
        "aurora_shared_operator_pair_loss",
        "aurora_shared_operator_pair_loss_zero",
        "aurora_shared_operator_random_cross_context_pair",
        "deltaphi_style_residual",
        "generic_probabilistic_operator",
        "nop_adapted",
    }
    if set(freeze["trainable_checkpoints_per_seed"]) != required_checkpoints:
        raise NonlinearDecisionError("N1b checkpoint set changed.")
    if (
        freeze["test_split_generated"] is not False
        or freeze["test_seed_accessed"] is not False
        or freeze["checkpoint_manifest_must_be_committed_before_test_job"]
        is not True
        or freeze["missing_or_nonfinite_model_blocks_test"] is not True
    ):
        raise NonlinearDecisionError("N1b test lock changed.")

    inherited = payload["success_rule"]
    parent_success = parent["success_rule"]
    for key in (
        "full_bc_operator_relative_l2_maximum",
        "aurora_functional_coverage_error_maximum",
        "aurora_route_bayes_action_disagreement_maximum",
        "primary_relative_improvement_over_strongest_validation_selected_non_oracle_minimum",
        "confirmatory_seed_direction_minimum",
        "confirmatory_seeds_total",
        "paired_response_must_improve_with_pair_loss",
        "field_distribution_and_acquisition_regret_must_both_improve",
        "aco_is_ceiling_not_competitor_for_superiority",
        "n1_pass_authorizes_irregular_3d_protocol_registration_only",
        "n1_pass_does_not_establish_cross_domain_or_aaai_acceptance",
    ):
        if inherited[key] != parent_success[key]:
            raise NonlinearDecisionError("N1b success rule changed after N1a.")
    if inherited["inherited_from_parent_without_change"] is not True:
        raise NonlinearDecisionError("N1b must inherit the parent success rule.")
    if payload["claim_boundary"]["irregular_3d_remains_blocked"] is not True:
        raise NonlinearDecisionError("N1b cannot authorize irregular 3D.")
    return parent, payload


def load_n1c_config(
    path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load the post-manifest, pre-test N1c execution overlay."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        [
            "schema_version",
            "experiment_id",
            "status",
            "parents",
            "test_lock",
            "functional_contract",
            "id_distribution_evaluation",
            "paired_response_evaluation",
            "route_evaluation",
            "acquisition_evaluation",
            "registered_shift_evaluation",
            "randomness",
            "inference_and_statistics",
            "success_rule",
            "claim_boundary",
        ],
        "N1c config",
    )
    if (
        payload["schema_version"] != "aurora.nonlinear_pde_n1c.v1"
        or payload["status"]
        != "preregistered_after_checkpoint_manifest_before_outer_test_generation"
    ):
        raise NonlinearDecisionError("Unexpected N1c pre-test status.")

    parents = payload["parents"]
    n1_path = (config_path.parent / parents["n1"]["config"]).resolve()
    n1b_path = (config_path.parent / parents["n1b"]["config"]).resolve()
    manifest_path = (
        config_path.parent / parents["checkpoint_manifest"]["path"]
    ).resolve()
    for source_path, contract, label in (
        (n1_path, parents["n1"], "N1"),
        (n1b_path, parents["n1b"], "N1b"),
        (
            manifest_path,
            parents["checkpoint_manifest"],
            "N1b checkpoint manifest",
        ),
    ):
        if not source_path.is_file() or _sha256(source_path) != contract["sha256"]:
            raise NonlinearDecisionError(f"Pinned {label} source changed.")
    n1, n1b = load_n1b_config(n1b_path)
    if _sha256(n1_path) != parents["n1"]["sha256"]:
        raise NonlinearDecisionError("N1c parent N1 and N1b disagree.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_contract = parents["checkpoint_manifest"]
    if (
        manifest_contract["public_commit"]
        != "c66f651a9cd13c7f58450f21c1d67ba11d78de8e"
        or manifest_contract["checkpoint_source_commit"]
        != "1d0bd9c759f935f818b5705b1b9bc2a00116ea59"
        or manifest_contract["eligible_seed_indices"] != [0, 1, 2, 3, 4]
        or int(manifest_contract["trainable_checkpoints_per_seed"]) != 10
        or manifest_contract[
            "checkpoint_hash_verification_required_before_test_generation"
        ]
        is not True
        or manifest["source"]["git_commit"]
        != manifest_contract["checkpoint_source_commit"]
        or len(manifest["seed_runs"]) != 5
        or any(
            item["checkpoint_seed_eligible"] is not True
            or len(item["checkpoint_sha256"]) != 10
            for item in manifest["seed_runs"]
        )
        or manifest["data_access"]["test_contexts_generated"] != 0
        or manifest["data_access"]["test_seed_accessed"] is not False
        or manifest["decision"]["n1_gate_decided"] is not False
    ):
        raise NonlinearDecisionError("N1c checkpoint manifest is not test-eligible.")

    lock = payload["test_lock"]
    data = n1["data"]
    if (
        int(lock["operator_test_contexts"])
        != int(data["operator_test_contexts"])
        or int(lock["conditions_per_context"])
        != int(data["operator_conditions_per_context"])
        or int(lock["context_seed"])
        != int(data["split_seeds"]["operator_test"])
        or int(lock["boundary_seed"])
        != int(data["split_seeds"]["operator_test"]) + 1000
        or lock["context_support"]
        != data["context_support"]["train_validation_id_test"]
        or float(lock["maximum_latent_mahalanobis_radius"])
        != float(
            data["boundary_latent_support"][
                "train_validation_id_test_max_mahalanobis_radius"
            ]
        )
        or lock["test_split_generated"] is not False
        or lock["test_seed_accessed"] is not False
        or lock["test_generation_must_follow_public_commit_of_this_overlay"]
        is not True
        or lock[
            "model_or_threshold_change_after_test_requires_new_version_and_fresh_test"
        ]
        is not True
    ):
        raise NonlinearDecisionError("N1c outer-test lock changed.")

    acquisition = payload["acquisition_evaluation"]
    if (
        acquisition["context_indices"] != list(range(0, 192, 4))
        or acquisition["selection_rule"]
        != "every_fourth_context_in_generation_order_fixed_before_test"
        or int(acquisition["anchor_condition_index"]) != 0
        or int(acquisition["outer_measurement_samples"]) != 8
        or int(acquisition["inner_posterior_samples"]) != 32
        or acquisition["true_law"]
        != "context_conditioned_two_component_gmm_conditioned_on_global_latent_radius_at_most_2_5"
        or acquisition["aco_role"] != "oracle_ceiling_not_superiority_target"
    ):
        raise NonlinearDecisionError("N1c acquisition selector or oracle changed.")

    route = payload["route_evaluation"]
    if (
        route["models_with_tractable_density_routes"]
        != ["aurora_joint", "independent_mask_heads", "acflow_adapted"]
        or route["initial_mask"] != [0, 2]
        or route["newly_observed_components"] != [5, 7]
        or route["final_mask"] != [0, 2, 5, 7]
        or route["context_indices"] != list(range(0, 192, 4))
        or int(route["anchor_condition_index"]) != 0
        or route["common_random_numbers_across_routes"] is not True
        or route["undefined_routes_are_reported_as_not_applicable_not_zero"]
        is not True
    ):
        raise NonlinearDecisionError("N1c route estimand changed.")

    statistics = payload["inference_and_statistics"]
    success = payload["success_rule"]
    shifts = payload["registered_shift_evaluation"]
    if (
        int(statistics["confirmatory_model_seeds"]) != 5
        or int(statistics["bootstrap_replicates"]) != 2000
        or statistics["bootstrap_unit"] != "test_context_family"
        or statistics["no_test_seed_model_or_policy_selection"] is not True
        or success["all_conditions_required"] is not True
        or float(
            success[
                "primary_relative_improvement_over_strongest_prefrozen_nonoracle_minimum"
            ]
        )
        != 0.05
        or int(success["confirmatory_seed_direction_minimum"]) != 4
        or success["field_distribution_and_acquisition_regret_must_both_improve"]
        is not True
        or success["n1_pass_authorizes_irregular_3d_protocol_registration_only"]
        is not True
        or success["n1_pass_does_not_establish_cross_domain_or_aaai_acceptance"]
        is not True
        or payload["claim_boundary"]["irregular_3d_remains_blocked_until_positive_n1"]
        is not True
        or shifts["execution_stage"]
        != "separate_N1d_secondary_job_after_N1c_without_model_threshold_or_test_seed_change"
        or shifts["shift_metrics_are_secondary_to_n1_primary_decision"] is not True
    ):
        raise NonlinearDecisionError("N1c decision or non-inflation rule changed.")
    return n1, n1b, payload, manifest


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


def _decode_gmm(raw: Any, mixtures: int = 2, dimension: int = 8) -> tuple[Any, Any, Any]:
    _, torch = _imports()
    triangle = dimension * (dimension + 1) // 2
    logits = raw[:, :mixtures]
    offset = mixtures
    means = raw[:, offset : offset + mixtures * dimension].reshape(
        -1, mixtures, dimension
    )
    offset += mixtures * dimension
    covariance = _covariance_from_raw(
        raw[:, offset : offset + mixtures * triangle].reshape(
            -1, mixtures, triangle
        ),
        dimension,
    )
    return torch.softmax(logits, dim=-1), means, covariance


def build_mask_conditional_density(config: Mapping[str, Any], device: Any) -> Any:
    """Build the ACFlow-style arbitrary-mask conditional-density adaptation."""

    _, torch = _imports()
    contract = config["architecture"]["mask_conditional_density"]
    width = int(contract["hidden_width"])
    layers = int(contract["hidden_layers"])
    dimension, mixtures = 8, 2
    triangle = dimension * (dimension + 1) // 2
    output = mixtures + mixtures * dimension + mixtures * triangle

    class MaskConditionalDensity(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = _build_mlp(
                torch, [21, *([width] * layers), output]
            )

        def forward(
            self, context: Any, observed: Any, mask: Any
        ) -> tuple[Any, Any, Any]:
            raw = self.net(torch.cat((context, observed * mask, mask), dim=-1))
            return _decode_gmm(raw)

    return MaskConditionalDensity().to(device)


def build_independent_mask_density(config: Mapping[str, Any], device: Any) -> Any:
    """Build shared features with separately parameterized registered-mask heads."""

    _, torch = _imports()
    contract = config["architecture"]["mask_conditional_density"]
    width = int(contract["hidden_width"])
    layers = int(contract["hidden_layers"])
    dimension, mixtures = 8, 2
    triangle = dimension * (dimension + 1) // 2
    output = mixtures + mixtures * dimension + mixtures * triangle
    mask_names = tuple(config["observation_protocol"]["registered_masks"])

    class IndependentMaskDensity(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = _build_mlp(
                torch, [21, *([width] * layers), width]
            )
            self.heads = torch.nn.ModuleDict(
                {name: torch.nn.Linear(width, output) for name in mask_names}
            )

        def forward(
            self, name: str, context: Any, observed: Any, mask: Any
        ) -> tuple[Any, Any, Any]:
            if name not in self.heads:
                raise NonlinearDecisionError(f"Unregistered independent mask: {name}.")
            feature = self.encoder(
                torch.cat((context, observed * mask, mask), dim=-1)
            )
            return _decode_gmm(self.heads[name](feature))

    return IndependentMaskDensity().to(device)


def build_lano_completion(config: Mapping[str, Any], device: Any) -> Any:
    """Build a boundary-first latent autoregressive completion adaptation."""

    _, torch = _imports()
    width = int(
        config["architecture"]["mask_conditional_density"]["hidden_width"]
    )
    layers = int(
        config["architecture"]["mask_conditional_density"]["hidden_layers"]
    )

    class BoundaryAutoregressiveCompletion(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = _build_mlp(
                torch, [29, *([width] * layers), 2]
            )

        def step(
            self,
            context: Any,
            current: Any,
            mask: Any,
            component: int,
        ) -> tuple[Any, Any]:
            one_hot = torch.zeros(
                context.shape[0], 8, device=context.device, dtype=context.dtype
            )
            one_hot[:, component] = 1.0
            raw = self.net(
                torch.cat((context, current * mask, mask, one_hot), dim=-1)
            )
            return raw[:, 0], torch.nn.functional.softplus(raw[:, 1]) + 1e-3

        def sample(
            self,
            context: Any,
            observed: Any,
            mask: Any,
            samples: int,
            seed: int,
        ) -> Any:
            generator = torch.Generator(device=context.device).manual_seed(seed)
            batch = context.shape[0]
            current = observed[:, None].expand(-1, samples, -1).clone()
            current_mask = mask[:, None].expand(-1, samples, -1).clone()
            expanded_context = context[:, None].expand(-1, samples, -1)
            for component in range(8):
                missing = current_mask[:, :, component] < 0.5
                if not bool(missing.any()):
                    continue
                mean, scale = self.step(
                    expanded_context.reshape(-1, 5),
                    current.reshape(-1, 8),
                    current_mask.reshape(-1, 8),
                    component,
                )
                value = mean + scale * torch.randn(
                    mean.shape,
                    generator=generator,
                    device=mean.device,
                    dtype=mean.dtype,
                )
                flat_current = current.reshape(-1, 8)
                flat_mask = current_mask.reshape(-1, 8)
                flat_missing = missing.reshape(-1)
                flat_current[flat_missing, component] = value[flat_missing]
                flat_mask[flat_missing, component] = 1.0
            return current

    return BoundaryAutoregressiveCompletion().to(device)


def build_direct_probabilistic_operator(
    config: Mapping[str, Any], device: Any, *, set_encoder: bool
) -> Any:
    """Build a generic flat-mask or NOP-style observed-token latent operator."""

    _, torch = _imports()
    contract = config["architecture"]["direct_probabilistic_operator"]
    width = int(contract["hidden_width"])
    rank = int(contract["latent_rank"])
    grid_points = int(config["pde_contract"]["grid_points"])
    coordinate, _ = _coordinate_features(grid_points, device)

    class DirectLatentOperator(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            if set_encoder:
                self.token = _build_mlp(torch, [10, width, width])
                self.context_net = _build_mlp(
                    torch, [5 + width, width, width, 2 * rank]
                )
                component = torch.eye(8, device=device)
                self.register_buffer("component", component)
            else:
                self.context_net = _build_mlp(
                    torch, [21, width, width, width, 2 * rank]
                )
            self.trunk = _build_mlp(
                torch, [coordinate.shape[-1], width, width, rank]
            )
            self.register_buffer("coordinate", coordinate)
            self.set_encoder = set_encoder

        def latent(self, context: Any, observed: Any, mask: Any) -> tuple[Any, Any]:
            if self.set_encoder:
                component = self.component[None].expand(context.shape[0], -1, -1)
                token_input = torch.cat(
                    (
                        observed[:, :, None] * mask[:, :, None],
                        mask[:, :, None],
                        component,
                    ),
                    dim=-1,
                )
                token = self.token(token_input)
                pooled = (token * mask[:, :, None]).sum(dim=1) / (
                    mask.sum(dim=1, keepdim=True) + 1.0
                )
                raw = self.context_net(torch.cat((context, pooled), dim=-1))
            else:
                raw = self.context_net(
                    torch.cat((context, observed * mask, mask), dim=-1)
                )
            mean, raw_scale = raw.chunk(2, dim=-1)
            return mean, torch.nn.functional.softplus(raw_scale) + 1e-3

        def moments(
            self, context: Any, observed: Any, mask: Any
        ) -> tuple[Any, Any]:
            mean, scale = self.latent(context, observed, mask)
            basis = self.trunk(self.coordinate) / math.sqrt(rank)
            field_mean = mean @ basis.transpose(0, 1)
            field_variance = scale.square() @ basis.square().transpose(0, 1)
            return (
                field_mean.reshape(-1, grid_points, grid_points),
                torch.sqrt(field_variance.clamp_min(1e-8)).reshape(
                    -1, grid_points, grid_points
                ),
            )

        def sample(
            self,
            context: Any,
            observed: Any,
            mask: Any,
            samples: int,
            seed: int,
        ) -> Any:
            mean, scale = self.latent(context, observed, mask)
            generator = torch.Generator(device=context.device).manual_seed(seed)
            latent = mean[:, None] + scale[:, None] * torch.randn(
                context.shape[0],
                samples,
                rank,
                generator=generator,
                device=context.device,
                dtype=context.dtype,
            )
            basis = self.trunk(self.coordinate) / math.sqrt(rank)
            field = torch.einsum("bsr,nr->bsn", latent, basis)
            return field.reshape(
                context.shape[0], samples, grid_points, grid_points
            )

    return DirectLatentOperator().to(device)


def fit_train_only_pod(
    field: Any,
    *,
    rank: int,
    seed: int,
    iterations: int,
) -> dict[str, Any]:
    """Fit one centered POD representation using training fields only."""

    _, torch = _imports()
    flat = field.reshape(field.shape[0], -1)
    mean = flat.mean(dim=0)
    centered = flat - mean
    torch.manual_seed(seed)
    _, _, basis = torch.pca_lowrank(
        centered,
        q=rank,
        center=False,
        niter=iterations,
    )
    coefficient = centered @ basis
    coefficient_location = coefficient.mean(dim=0)
    coefficient_scale = coefficient.std(dim=0, unbiased=False).clamp_min(1e-4)
    reconstruction = mean + coefficient @ basis.transpose(0, 1)
    relative = torch.linalg.vector_norm(reconstruction - flat, dim=1) / (
        torch.linalg.vector_norm(flat, dim=1).clamp_min(1e-6)
    )
    return {
        "mean": mean,
        "basis": basis,
        "coefficient_location": coefficient_location,
        "coefficient_scale": coefficient_scale,
        "training_mean_relative_l2": float(relative.mean().item()),
        "training_maximum_relative_l2": float(relative.max().item()),
        "rank": rank,
        "seed": seed,
        "iterations": iterations,
    }


def encode_pod(field: Any, representation: Mapping[str, Any]) -> Any:
    """Encode fields in standardized train-only POD coordinates."""

    flat = field.reshape(field.shape[0], -1)
    coefficient = (
        flat - representation["mean"]
    ) @ representation["basis"]
    return (
        coefficient - representation["coefficient_location"]
    ) / representation["coefficient_scale"]


def pod_representation_error(
    field: Any, representation: Mapping[str, Any]
) -> Any:
    """Return per-case relative reconstruction error for a frozen POD."""

    _, torch = _imports()
    standardized = encode_pod(field, representation)
    coefficient = (
        standardized * representation["coefficient_scale"]
        + representation["coefficient_location"]
    )
    reconstruction = (
        representation["mean"]
        + coefficient @ representation["basis"].transpose(0, 1)
    )
    target = field.reshape(field.shape[0], -1)
    return torch.linalg.vector_norm(reconstruction - target, dim=1) / (
        torch.linalg.vector_norm(target, dim=1).clamp_min(1e-6)
    )


def build_pod_probabilistic_operator(
    config: Mapping[str, Any],
    device: Any,
    *,
    representation: Mapping[str, Any],
    set_encoder: bool,
) -> Any:
    """Build a compute-matched Gaussian operator on a frozen train-only POD."""

    _, torch = _imports()
    contract = config["architecture"]["direct_probabilistic_operator"]
    width = int(contract["hidden_width"])
    rank = int(representation["rank"])
    grid_points = int(config["pde_contract"]["grid_points"])

    class PODGaussianOperator(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            if set_encoder:
                token_width = 64
                self.token = _build_mlp(
                    torch, [10, token_width, token_width]
                )
                self.context_net = _build_mlp(
                    torch,
                    [5 + token_width, width, width, width, 2 * rank],
                )
                self.register_buffer("component", torch.eye(8, device=device))
            else:
                self.context_net = _build_mlp(
                    torch, [21, width, width, width, width, 2 * rank]
                )
            self.register_buffer("pod_mean", representation["mean"].clone())
            self.register_buffer("pod_basis", representation["basis"].clone())
            self.register_buffer(
                "coefficient_location",
                representation["coefficient_location"].clone(),
            )
            self.register_buffer(
                "coefficient_scale",
                representation["coefficient_scale"].clone(),
            )
            self.set_encoder = set_encoder

        def latent(self, context: Any, observed: Any, mask: Any) -> tuple[Any, Any]:
            if self.set_encoder:
                component = self.component[None].expand(context.shape[0], -1, -1)
                token_input = torch.cat(
                    (
                        observed[:, :, None] * mask[:, :, None],
                        mask[:, :, None],
                        component,
                    ),
                    dim=-1,
                )
                token = self.token(token_input)
                pooled = (token * mask[:, :, None]).sum(dim=1) / (
                    mask.sum(dim=1, keepdim=True) + 1.0
                )
                raw = self.context_net(torch.cat((context, pooled), dim=-1))
            else:
                raw = self.context_net(
                    torch.cat((context, observed * mask, mask), dim=-1)
                )
            mean, raw_scale = raw.chunk(2, dim=-1)
            return mean, torch.nn.functional.softplus(raw_scale) + 1e-3

        def nll(
            self,
            context: Any,
            observed: Any,
            mask: Any,
            standardized_coefficient: Any,
        ) -> Any:
            mean, scale = self.latent(context, observed, mask)
            return (
                0.5 * ((standardized_coefficient - mean) / scale).square()
                + torch.log(scale)
                + 0.5 * math.log(2.0 * math.pi)
            ).sum(dim=-1)

        def _decode(self, standardized: Any) -> Any:
            coefficient = (
                standardized * self.coefficient_scale
                + self.coefficient_location
            )
            return self.pod_mean + coefficient @ self.pod_basis.transpose(0, 1)

        def moments(
            self, context: Any, observed: Any, mask: Any
        ) -> tuple[Any, Any]:
            mean, scale = self.latent(context, observed, mask)
            field_mean = self._decode(mean)
            physical_scale = scale * self.coefficient_scale
            field_variance = (
                physical_scale.square()
                @ self.pod_basis.square().transpose(0, 1)
            )
            return (
                field_mean.reshape(-1, grid_points, grid_points),
                torch.sqrt(field_variance.clamp_min(1e-8)).reshape(
                    -1, grid_points, grid_points
                ),
            )

        def sample(
            self,
            context: Any,
            observed: Any,
            mask: Any,
            samples: int,
            seed: int,
        ) -> Any:
            mean, scale = self.latent(context, observed, mask)
            generator = torch.Generator(device=context.device).manual_seed(seed)
            latent = mean[:, None] + scale[:, None] * torch.randn(
                context.shape[0],
                samples,
                rank,
                generator=generator,
                device=context.device,
                dtype=context.dtype,
            )
            field = self._decode(latent)
            return field.reshape(
                context.shape[0], samples, grid_points, grid_points
            )

    return PODGaussianOperator().to(device)


def build_deltaphi_residual_operator(
    config: Mapping[str, Any],
    device: Any,
    *,
    representation: Mapping[str, Any],
) -> Any:
    """Build a parameter-matched DeltaPhi-style retrieved-residual adaptation."""

    _, torch = _imports()
    from aurora.nonlinear_pde import _boundary_field

    rank = int(config["architecture"]["conditional_solution_operator"]["rank"])
    grid_points = int(config["pde_contract"]["grid_points"])
    coordinate_width = int(
        config["architecture"]["conditional_solution_operator"]["coordinate_width"]
    )
    coordinate_layers = int(
        config["architecture"]["conditional_solution_operator"]["coordinate_layers"]
    )
    anchor_rank = 32
    branch_width = 176
    coordinate, envelope = _coordinate_features(grid_points, device)

    class DeltaPhiResidualOperator(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.branch = _build_mlp(
                torch,
                [
                    26 + anchor_rank,
                    branch_width,
                    branch_width,
                    branch_width,
                    rank,
                ],
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
            self.register_buffer("pod_mean", representation["mean"].clone())
            self.register_buffer(
                "anchor_basis", representation["basis"][:, :anchor_rank].clone()
            )
            self.register_buffer(
                "anchor_scale",
                representation["coefficient_scale"][:anchor_rank].clone(),
            )

        def forward(
            self,
            context: Any,
            boundary: Any,
            anchor_context: Any,
            anchor_boundary: Any,
            anchor_field: Any,
        ) -> Any:
            anchor_flat = anchor_field.flatten(1)
            anchor_coefficient = (
                (anchor_flat - self.pod_mean) @ self.anchor_basis
            ) / self.anchor_scale
            branch_input = torch.cat(
                (
                    context,
                    boundary,
                    anchor_context,
                    anchor_boundary,
                    anchor_coefficient,
                ),
                dim=-1,
            )
            coefficient = self.branch(branch_input)
            basis = self.trunk(self.coordinate)
            correction = torch.einsum(
                "br,nr->bn", coefficient, basis
            ) / math.sqrt(rank)
            lifting_delta = (
                _boundary_field(boundary, grid_points)
                - _boundary_field(anchor_boundary, grid_points)
            ).flatten(1)
            prediction = (
                anchor_flat + lifting_delta + correction * self.envelope
            )
            return prediction.reshape(-1, grid_points, grid_points)

    return DeltaPhiResidualOperator().to(device)


def marginal_gmm(
    weights: Any,
    means: Any,
    covariances: Any,
    positions: Sequence[int],
) -> tuple[Any, Any, Any]:
    """Select a component marginal without renormalizing mixture weights."""

    _, torch = _imports()
    index = torch.tensor(positions, device=means.device, dtype=torch.long)
    selected_mean = torch.index_select(means, -1, index)
    selected_covariance = torch.index_select(
        torch.index_select(covariances, -2, index), -1, index
    )
    return weights, selected_mean, selected_covariance


def sample_gmm(
    weights: Any,
    means: Any,
    covariances: Any,
    *,
    samples: int,
    seed: int,
) -> Any:
    """Draw deterministic-seed samples from a batched Gaussian mixture."""

    _, torch = _imports()
    generator = torch.Generator(device=means.device).manual_seed(seed)
    batch, mixtures, dimension = means.shape
    uniforms = torch.rand(
        batch, samples, generator=generator, device=means.device
    )
    cumulative = torch.cumsum(weights, dim=-1)
    component = torch.sum(
        uniforms[:, :, None] > cumulative[:, None, :], dim=-1
    ).clamp_max(mixtures - 1)
    cholesky = torch.linalg.cholesky(
        covariances
        + 1e-6
        * torch.eye(dimension, device=means.device, dtype=means.dtype)
    )
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
    standard = torch.randn(
        batch,
        samples,
        dimension,
        generator=generator,
        device=means.device,
        dtype=means.dtype,
    )
    return selected_mean + torch.einsum(
        "bsij,bsj->bsi", selected_cholesky, standard
    )


def _mask_tensor(
    positions: Sequence[int], batch: int, device: Any, dtype: Any
) -> Any:
    _, torch = _imports()
    mask = torch.zeros(batch, 8, device=device, dtype=dtype)
    if positions:
        mask[:, list(positions)] = 1.0
    return mask


def conditional_joint_nll(
    weights: Any,
    means: Any,
    covariances: Any,
    boundary: Any,
    observed_positions: Sequence[int],
) -> Any:
    """Evaluate missing-component NLL after analytic joint conditioning."""

    from aurora.nonlinear_pde import condition_gaussian_mixture

    observed = list(observed_positions)
    missing = [index for index in range(8) if index not in observed]
    if not missing:
        return boundary.new_zeros(boundary.shape[0])
    if observed:
        conditioned = condition_gaussian_mixture(
            weights,
            means,
            covariances,
            observed,
            boundary[:, observed],
        )
        conditional_weights, conditional_mean, conditional_covariance, remaining = (
            conditioned
        )
        if remaining != missing:
            raise NonlinearDecisionError("Conditional component order changed.")
    else:
        conditional_weights = weights
        conditional_mean = means
        conditional_covariance = covariances
    return gmm_nll(
        conditional_weights,
        conditional_mean,
        conditional_covariance,
        boundary[:, missing],
    )


def mask_density_nll(
    model: Any,
    context: Any,
    boundary: Any,
    observed_positions: Sequence[int],
    *,
    independent_name: str | None = None,
) -> Any:
    """Evaluate a mask-conditional model on exactly the unobserved components."""

    observed = list(observed_positions)
    missing = [index for index in range(8) if index not in observed]
    if not missing:
        return boundary.new_zeros(boundary.shape[0])
    mask = _mask_tensor(
        observed, boundary.shape[0], boundary.device, boundary.dtype
    )
    if independent_name is None:
        weights, means, covariances = model(context, boundary, mask)
    else:
        weights, means, covariances = model(
            independent_name, context, boundary, mask
        )
    weights, means, covariances = marginal_gmm(
        weights, means, covariances, missing
    )
    return gmm_nll(weights, means, covariances, boundary[:, missing])


def autoregressive_completion_nll(
    model: Any,
    context: Any,
    boundary: Any,
    observed_positions: Sequence[int],
) -> Any:
    """Teacher-forced boundary-first completion likelihood."""

    _, torch = _imports()
    observed = set(int(index) for index in observed_positions)
    current = boundary.clone()
    mask = _mask_tensor(
        sorted(observed), boundary.shape[0], boundary.device, boundary.dtype
    )
    losses = []
    for component in range(8):
        if component in observed:
            continue
        mean, scale = model.step(context, current, mask, component)
        target = boundary[:, component]
        losses.append(
            0.5 * ((target - mean) / scale).square()
            + torch.log(scale)
            + 0.5 * math.log(2.0 * math.pi)
        )
        next_mask = mask.clone()
        next_mask[:, component] = 1.0
        mask = next_mask
    if not losses:
        return boundary.new_zeros(boundary.shape[0])
    return torch.stack(losses, dim=-1).sum(dim=-1)


def _random_nonfull_mask(seed: int) -> list[int]:
    """Return a deterministic arbitrary mask while retaining one missing value."""

    np, _ = _imports()
    generator = np.random.default_rng(seed)
    selected = generator.random(8) < 0.5
    if bool(selected.all()):
        selected[int(seed % 8)] = False
    return [int(index) for index in np.flatnonzero(selected)]


def train_completion_development(
    *,
    config: Mapping[str, Any],
    density_train: Mapping[str, Any],
    density_validation: Mapping[str, Any],
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Train joint and strong completion models using validation data only."""

    _, torch = _imports()
    torch.manual_seed(seed)
    device = density_train["context"].device
    joint = build_joint_density(config, device)
    acflow = build_mask_conditional_density(config, device)
    independent = build_independent_mask_density(config, device)
    lano = build_lano_completion(config, device)
    models = {
        "aurora_joint": joint,
        "acflow_adapted": acflow,
        "independent_mask_heads": independent,
        "lano_adapted": lano,
    }
    contract = config["training"]["density"]
    optimizers = {
        name: torch.optim.AdamW(
            model.parameters(),
            lr=float(contract["learning_rate"]),
            weight_decay=float(contract["weight_decay"]),
        )
        for name, model in models.items()
    }
    generators = {
        name: torch.Generator(device=device).manual_seed(
            seed + 1000 + 97 * index
        )
        for index, name in enumerate(models)
    }
    train_context = density_train["context"][:, None].expand(
        -1, density_train["boundary"].shape[1], -1
    ).reshape(-1, 5)
    train_boundary = density_train["boundary"].reshape(-1, 8)
    validation_context = density_validation["context"][:, None].expand(
        -1, density_validation["boundary"].shape[1], -1
    ).reshape(-1, 5)
    validation_boundary = density_validation["boundary"].reshape(-1, 8)
    registered = config["observation_protocol"]["registered_masks"]
    validation_masks = [
        ("missing", registered["missing"]),
        ("sparse_2", registered["sparse_2"]),
        ("partial_4", registered["partial_4"]),
    ]
    best = {name: math.inf for name in models}
    best_epoch = {name: 0 for name in models}
    best_state = {name: _clone_state(model) for name, model in models.items()}
    waits = {name: 0 for name in models}
    traces = {name: [] for name in models}
    active = set(models)
    batch_size = int(contract["batch_size"])
    interval = int(contract["validation_interval"])
    patience = int(contract["early_stopping_patience"])
    maximum_epochs = int(contract["maximum_epochs"])

    for epoch in range(1, maximum_epochs + 1):
        arbitrary_mask = _random_nonfull_mask(seed + epoch)
        registered_name, registered_mask = validation_masks[
            (epoch - 1) % len(validation_masks)
        ]
        training_masks = {
            "aurora_joint": arbitrary_mask,
            "acflow_adapted": arbitrary_mask,
            "independent_mask_heads": registered_mask,
            "lano_adapted": arbitrary_mask,
        }
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
            mask_positions = training_masks[name]
            if name == "aurora_joint":
                weights, means, covariances = joint(context)
                loss = conditional_joint_nll(
                    weights, means, covariances, boundary, mask_positions
                ).mean()
            elif name == "acflow_adapted":
                loss = mask_density_nll(
                    acflow, context, boundary, mask_positions
                ).mean()
            elif name == "independent_mask_heads":
                loss = mask_density_nll(
                    independent,
                    context,
                    boundary,
                    mask_positions,
                    independent_name=registered_name,
                ).mean()
            else:
                loss = autoregressive_completion_nll(
                    lano, context, boundary, mask_positions
                ).mean()
            optimizers[name].zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(models[name].parameters(), 5.0)
            optimizers[name].step()
        if epoch % interval != 0:
            continue
        for model in models.values():
            model.eval()
        with torch.no_grad():
            for name in tuple(active):
                mask_losses = []
                for mask_name, mask_positions in validation_masks:
                    chunks = []
                    for start in range(0, validation_context.shape[0], 4096):
                        end = min(start + 4096, validation_context.shape[0])
                        context = validation_context[start:end]
                        boundary = validation_boundary[start:end]
                        if name == "aurora_joint":
                            weights, means, covariances = joint(context)
                            value = conditional_joint_nll(
                                weights,
                                means,
                                covariances,
                                boundary,
                                mask_positions,
                            )
                        elif name == "acflow_adapted":
                            value = mask_density_nll(
                                acflow, context, boundary, mask_positions
                            )
                        elif name == "independent_mask_heads":
                            value = mask_density_nll(
                                independent,
                                context,
                                boundary,
                                mask_positions,
                                independent_name=mask_name,
                            )
                        else:
                            value = autoregressive_completion_nll(
                                lano, context, boundary, mask_positions
                            )
                        chunks.append(value)
                    mask_losses.append(torch.cat(chunks).mean())
                validation_loss = float(torch.stack(mask_losses).mean().item())
                traces[name].append(
                    {
                        "epoch": epoch,
                        "validation_conditional_nll": validation_loss,
                    }
                )
                if validation_loss < best[name] - 1e-5:
                    best[name] = validation_loss
                    best_epoch[name] = epoch
                    best_state[name] = _clone_state(models[name])
                    waits[name] = 0
                else:
                    waits[name] += 1
                    if waits[name] >= patience:
                        active.remove(name)
        for model in models.values():
            model.train()
        if not active:
            break

    for name, model in models.items():
        model.load_state_dict(best_state[name])
        model.eval()
    history = {
        "stage": "validation_only_completion_development",
        "test_generated_or_accessed": False,
        "seed": seed,
        "models": {
            name: {
                "best_epoch": best_epoch[name],
                "best_validation_conditional_nll": best[name],
                "epochs_executed": traces[name][-1]["epoch"],
                "trace": traces[name],
                "parameters": sum(
                    parameter.numel() for parameter in models[name].parameters()
                ),
            }
            for name in models
        },
        "claim_status": {
            "n1_gate_decided": False,
            "baseline_superiority_established": False,
            "method_novelty_established": False,
            "irregular_3d_authorized": False,
        },
    }
    return models, history


def train_operator_optimization_attribution(
    *,
    n1_config: Mapping[str, Any],
    attribution_config: Mapping[str, Any],
    operator_train: Mapping[str, Any],
    operator_validation: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the registered 2x2 validation-only operator optimization attribution."""

    _, torch = _imports()
    seed = int(attribution_config["development_seed"])
    train_context, train_boundary, train_field = _flatten_solution_split(
        operator_train
    )
    validation_context, validation_boundary, validation_field = (
        _flatten_solution_split(operator_validation)
    )
    field_rms_squared = train_field.square().mean(dim=(-2, -1))
    field_floor = torch.quantile(field_rms_squared, 0.10).clamp_min(1e-8)
    adjacent_delta = (
        operator_train["field"][:, 1:] - operator_train["field"][:, :-1]
    )
    pair_rms_squared = adjacent_delta.square().mean(dim=(-2, -1))
    pair_floor = torch.quantile(pair_rms_squared, 0.10).clamp_min(1e-8)
    shared = attribution_config["shared_training"]
    batch_size = int(shared["batch_size"])
    interval = int(shared["validation_interval"])
    patience = int(shared["early_stopping_patience"])
    pair_weight = float(
        attribution_config["model_contract"]["paired_response_weight"]
    )
    train_conditions = operator_train["boundary"].shape[1]
    family_batch = min(256, operator_train["context"].shape[0])
    operators = {}
    results = {}

    for variant_index, variant in enumerate(
        attribution_config["factorial_variants"]
    ):
        variant_id = variant["id"]
        normalized = (
            variant["loss_conditioning"]
            == "train_only_rms_normalized_field_and_pair_mse"
        )
        torch.manual_seed(seed)
        operator = build_solution_operator(n1_config, train_context.device)
        optimizer = torch.optim.AdamW(
            operator.parameters(),
            lr=float(shared["learning_rate"]),
            weight_decay=float(shared["weight_decay"]),
        )
        generator = torch.Generator(device=train_context.device).manual_seed(
            seed + 10000
        )
        best_value = math.inf
        best_epoch = 0
        best_state = _clone_state(operator)
        wait = 0
        trace = []
        maximum_steps = int(variant["maximum_steps"])
        for step in range(1, maximum_steps + 1):
            index = torch.randint(
                0,
                train_context.shape[0],
                (batch_size,),
                generator=generator,
                device=train_context.device,
            )
            prediction = operator(train_context[index], train_boundary[index])
            field_error = (prediction - train_field[index]).square().mean(
                dim=(-2, -1)
            )
            if normalized:
                denominator = field_rms_squared[index].clamp_min(field_floor)
                field_loss = (field_error / denominator).mean()
            else:
                field_loss = field_error.mean()

            family_index = torch.randint(
                0,
                operator_train["context"].shape[0],
                (family_batch,),
                generator=generator,
                device=train_context.device,
            )
            first = (step - 1) % train_conditions
            second = step % train_conditions
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
            pair_error = (predicted_delta - true_delta).square().mean(
                dim=(-2, -1)
            )
            if normalized:
                denominator = true_delta.square().mean(
                    dim=(-2, -1)
                ).clamp_min(pair_floor)
                pair_loss = (pair_error / denominator).mean()
            else:
                pair_loss = pair_error.mean()
            loss = field_loss + pair_weight * pair_loss
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(operator.parameters(), 5.0)
            optimizer.step()

            if step % interval != 0:
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
                    (
                        validation_relative
                        + pair_weight * validation_pair_relative
                    ).item()
                )
            operator.train()
            trace.append(
                {
                    "step": step,
                    "train_field_loss": float(field_loss.detach().item()),
                    "train_pair_loss": float(pair_loss.detach().item()),
                    "validation_full_bc_relative_l2": float(
                        validation_relative.item()
                    ),
                    "validation_paired_response_relative_l2": float(
                        validation_pair_relative.item()
                    ),
                    "validation_selection_objective": validation_objective,
                }
            )
            if validation_objective < best_value - 1e-5:
                best_value = validation_objective
                best_epoch = step
                best_state = _clone_state(operator)
                wait = 0
            else:
                wait += 1
            if wait >= patience:
                break
        operator.load_state_dict(best_state)
        operator.eval()
        operators[variant_id] = operator
        best_record = min(
            trace, key=lambda item: item["validation_selection_objective"]
        )
        results[variant_id] = {
            "loss_conditioning": variant["loss_conditioning"],
            "maximum_steps": maximum_steps,
            "best_step": best_epoch,
            "steps_executed": trace[-1]["step"],
            "best_validation_objective": best_value,
            "best_record": best_record,
            "last_record": trace[-1],
            "trace": trace,
            "parameters": sum(
                parameter.numel() for parameter in operator.parameters()
            ),
        }

    minimum = min(
        item["best_validation_objective"] for item in results.values()
    )
    within_tolerance = [
        variant
        for variant in attribution_config["factorial_variants"]
        if results[variant["id"]]["best_validation_objective"]
        <= 1.01 * minimum
    ]
    selected_contract = min(
        within_tolerance,
        key=lambda item: (
            int(item["maximum_steps"]),
            results[item["id"]]["best_validation_objective"],
        ),
    )
    history = {
        "stage": "validation_only_optimization_attribution",
        "test_generated_or_accessed": False,
        "development_seed": seed,
        "training_scale": {
            "field_rms_squared_tenth_percentile": float(field_floor.item()),
            "pair_rms_squared_tenth_percentile": float(pair_floor.item()),
            "source": "operator_training_split_only",
        },
        "variants": results,
        "selection": {
            "selected_variant": selected_contract["id"],
            "selected_maximum_steps": int(selected_contract["maximum_steps"]),
            "selected_loss_conditioning": selected_contract[
                "loss_conditioning"
            ],
            "has_gate_decision": False,
            "requires_new_prospective_n1_version": True,
        },
        "claim_status": {
            "n1_gate_decided": False,
            "baseline_superiority_established": False,
            "method_novelty_established": False,
            "confirmatory_test_authorized": False,
            "irregular_3d_authorized": False,
        },
    }
    return operators, history


def _shared_operator_validation(
    operator: Any,
    validation: Mapping[str, Any],
    *,
    pair_weight: float,
) -> dict[str, float]:
    """Evaluate the frozen full-BC and same-context pair selection metrics."""

    _, torch = _imports()
    context, boundary, field = _flatten_solution_split(validation)
    relative = []
    for start in range(0, context.shape[0], 1024):
        end = min(start + 1024, context.shape[0])
        relative.append(
            _relative_l2(
                operator(context[start:end], boundary[start:end]),
                field[start:end],
            )
        )
    full = torch.cat(relative).mean()
    predicted_delta = operator(
        validation["context"], validation["boundary"][:, 1]
    ) - operator(validation["context"], validation["boundary"][:, 0])
    true_delta = validation["field"][:, 1] - validation["field"][:, 0]
    paired = _relative_l2(predicted_delta, true_delta).mean()
    return {
        "validation_full_bc_relative_l2": float(full.item()),
        "validation_paired_response_relative_l2": float(paired.item()),
        "validation_selection_objective": float(
            (full + pair_weight * paired).item()
        ),
    }


def train_shared_operator_controls(
    *,
    n1_config: Mapping[str, Any],
    n1b_config: Mapping[str, Any],
    operator_train: Mapping[str, Any],
    operator_validation: Mapping[str, Any],
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Train pair, no-pair, and random-context controls without test access."""

    _, torch = _imports()
    contract = n1b_config["selected_shared_operator_training"]
    train_context, train_boundary, train_field = _flatten_solution_split(
        operator_train
    )
    field_rms_squared = train_field.square().mean(dim=(-2, -1))
    field_floor = torch.quantile(field_rms_squared, 0.10).clamp_min(1e-8)
    adjacent_delta = (
        operator_train["field"][:, 1:] - operator_train["field"][:, :-1]
    )
    pair_floor = torch.quantile(
        adjacent_delta.square().mean(dim=(-2, -1)), 0.10
    ).clamp_min(1e-8)
    selection_pair_weight = float(contract["paired_response_weight"])
    variants = {
        "aurora_shared_operator_pair_loss": {
            "pair_mode": "same_context",
            "training_pair_weight": selection_pair_weight,
        },
        "aurora_shared_operator_pair_loss_zero": {
            "pair_mode": "none",
            "training_pair_weight": 0.0,
        },
        "aurora_shared_operator_random_cross_context_pair": {
            "pair_mode": "random_cross_context",
            "training_pair_weight": selection_pair_weight,
        },
    }
    models = {}
    histories = {}
    maximum_steps = int(contract["maximum_steps"])
    interval = int(contract["validation_interval"])
    patience = int(contract["early_stopping_patience"])
    batch_size = int(contract["batch_size"])
    conditions = int(operator_train["boundary"].shape[1])
    context_count = int(operator_train["context"].shape[0])
    family_batch = min(256, context_count)

    for variant_index, (name, variant) in enumerate(variants.items()):
        torch.manual_seed(seed)
        model = build_solution_operator(n1_config, train_context.device)
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=float(contract["learning_rate"]),
            weight_decay=float(contract["weight_decay"]),
        )
        generator = torch.Generator(device=train_context.device).manual_seed(
            seed + 20000 + 101 * variant_index
        )
        best = math.inf
        best_step = 0
        best_state = _clone_state(model)
        wait = 0
        trace = []
        for step in range(1, maximum_steps + 1):
            index = torch.randint(
                0,
                train_context.shape[0],
                (batch_size,),
                generator=generator,
                device=train_context.device,
            )
            prediction = model(train_context[index], train_boundary[index])
            field_error = (prediction - train_field[index]).square().mean(
                dim=(-2, -1)
            )
            field_loss = (
                field_error / field_rms_squared[index].clamp_min(field_floor)
            ).mean()

            pair_mode = variant["pair_mode"]
            pair_loss = field_loss.new_zeros(())
            if pair_mode != "none":
                first_family = torch.randint(
                    0,
                    context_count,
                    (family_batch,),
                    generator=generator,
                    device=train_context.device,
                )
                first_condition = (step - 1) % conditions
                second_condition = step % conditions
                if pair_mode == "same_context":
                    second_family = first_family
                else:
                    offset = torch.randint(
                        1,
                        context_count,
                        (family_batch,),
                        generator=generator,
                        device=train_context.device,
                    )
                    second_family = (first_family + offset) % context_count
                first_prediction = model(
                    operator_train["context"][first_family],
                    operator_train["boundary"][
                        first_family, first_condition
                    ],
                )
                second_prediction = model(
                    operator_train["context"][second_family],
                    operator_train["boundary"][
                        second_family, second_condition
                    ],
                )
                true_delta = (
                    operator_train["field"][second_family, second_condition]
                    - operator_train["field"][first_family, first_condition]
                )
                pair_error = (
                    second_prediction - first_prediction - true_delta
                ).square().mean(dim=(-2, -1))
                pair_loss = (
                    pair_error
                    / true_delta.square()
                    .mean(dim=(-2, -1))
                    .clamp_min(pair_floor)
                ).mean()
            loss = field_loss + float(variant["training_pair_weight"]) * pair_loss
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()

            if step % interval != 0:
                continue
            model.eval()
            with torch.no_grad():
                record = {
                    "step": step,
                    "train_field_loss": float(field_loss.detach().item()),
                    "train_pair_loss": float(pair_loss.detach().item()),
                    **_shared_operator_validation(
                        model,
                        operator_validation,
                        pair_weight=selection_pair_weight,
                    ),
                }
            model.train()
            trace.append(record)
            objective = record["validation_selection_objective"]
            if objective < best - 1e-5:
                best = objective
                best_step = step
                best_state = _clone_state(model)
                wait = 0
            else:
                wait += 1
            if wait >= patience:
                break
        model.load_state_dict(best_state)
        model.eval()
        best_record = min(
            trace, key=lambda item: item["validation_selection_objective"]
        )
        models[name] = model
        histories[name] = {
            "pair_mode": variant["pair_mode"],
            "training_pair_weight": variant["training_pair_weight"],
            "best_step": best_step,
            "steps_executed": trace[-1]["step"],
            "best_record": best_record,
            "trace": trace,
            "parameters": sum(
                parameter.numel() for parameter in model.parameters()
            ),
        }
    return models, {
        "stage": "validation_only_shared_operator_checkpoint_freeze",
        "seed": seed,
        "test_generated_or_accessed": False,
        "training_scale": {
            "field_rms_squared_tenth_percentile": float(field_floor.item()),
            "pair_rms_squared_tenth_percentile": float(pair_floor.item()),
            "source": "operator_training_split_only",
        },
        "models": histories,
    }


def nearest_training_indices(
    query_key: Any,
    training_key: Any,
    *,
    exclude_self: bool,
    chunk_size: int = 256,
) -> Any:
    """Find deterministic nearest training anchors in standardized key space."""

    _, torch = _imports()
    outputs = []
    for start in range(0, query_key.shape[0], chunk_size):
        end = min(start + chunk_size, query_key.shape[0])
        distance = torch.cdist(query_key[start:end], training_key)
        if exclude_self:
            row = torch.arange(end - start, device=query_key.device)
            column = torch.arange(start, end, device=query_key.device)
            distance[row, column] = torch.inf
        outputs.append(torch.argmin(distance, dim=1))
    return torch.cat(outputs)


def train_deltaphi_control(
    *,
    n1_config: Mapping[str, Any],
    n1b_config: Mapping[str, Any],
    operator_train: Mapping[str, Any],
    operator_validation: Mapping[str, Any],
    representation: Mapping[str, Any],
    seed: int,
) -> tuple[Any, dict[str, Any]]:
    """Train a retrieval-based residual operator using training anchors only."""

    _, torch = _imports()
    contract = n1b_config["selected_shared_operator_training"]
    train_context, train_boundary, train_field = _flatten_solution_split(
        operator_train
    )
    validation_context, validation_boundary, validation_field = (
        _flatten_solution_split(operator_validation)
    )
    raw_training_key = torch.cat((train_context, train_boundary), dim=-1)
    key_location = raw_training_key.mean(dim=0)
    key_scale = raw_training_key.std(dim=0, unbiased=False).clamp_min(1e-4)
    training_key = (raw_training_key - key_location) / key_scale
    validation_key = (
        torch.cat((validation_context, validation_boundary), dim=-1)
        - key_location
    ) / key_scale
    training_anchor = nearest_training_indices(
        training_key, training_key, exclude_self=True
    )
    validation_anchor = nearest_training_indices(
        validation_key, training_key, exclude_self=False
    )

    field_rms_squared = train_field.square().mean(dim=(-2, -1))
    field_floor = torch.quantile(field_rms_squared, 0.10).clamp_min(1e-8)
    pair_weight = float(contract["paired_response_weight"])
    torch.manual_seed(seed)
    model = build_deltaphi_residual_operator(
        n1_config,
        train_context.device,
        representation=representation,
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(contract["learning_rate"]),
        weight_decay=float(contract["weight_decay"]),
    )
    generator = torch.Generator(device=train_context.device).manual_seed(
        seed + 30000
    )
    best = math.inf
    best_step = 0
    best_state = _clone_state(model)
    wait = 0
    trace = []
    conditions = int(operator_validation["boundary"].shape[1])

    def predict(
        context: Any,
        boundary: Any,
        anchor_index: Any,
    ) -> Any:
        return model(
            context,
            boundary,
            train_context[anchor_index],
            train_boundary[anchor_index],
            train_field[anchor_index],
        )

    for step in range(1, int(contract["maximum_steps"]) + 1):
        index = torch.randint(
            0,
            train_context.shape[0],
            (int(contract["batch_size"]),),
            generator=generator,
            device=train_context.device,
        )
        prediction = predict(
            train_context[index],
            train_boundary[index],
            training_anchor[index],
        )
        error = (prediction - train_field[index]).square().mean(dim=(-2, -1))
        loss = (
            error / field_rms_squared[index].clamp_min(field_floor)
        ).mean()
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        optimizer.step()
        if step % int(contract["validation_interval"]) != 0:
            continue
        model.eval()
        with torch.no_grad():
            relative = []
            for start in range(0, validation_context.shape[0], 1024):
                end = min(start + 1024, validation_context.shape[0])
                relative.append(
                    _relative_l2(
                        predict(
                            validation_context[start:end],
                            validation_boundary[start:end],
                            validation_anchor[start:end],
                        ),
                        validation_field[start:end],
                    )
                )
            full = torch.cat(relative).mean()
            first_flat = torch.arange(
                0,
                validation_context.shape[0],
                conditions,
                device=validation_context.device,
            )
            second_flat = first_flat + 1
            predicted_delta = predict(
                validation_context[second_flat],
                validation_boundary[second_flat],
                validation_anchor[second_flat],
            ) - predict(
                validation_context[first_flat],
                validation_boundary[first_flat],
                validation_anchor[first_flat],
            )
            true_delta = (
                operator_validation["field"][:, 1]
                - operator_validation["field"][:, 0]
            )
            paired = _relative_l2(predicted_delta, true_delta).mean()
            objective = float((full + pair_weight * paired).item())
        model.train()
        record = {
            "step": step,
            "train_normalized_field_mse": float(loss.detach().item()),
            "validation_full_bc_relative_l2": float(full.item()),
            "validation_paired_response_relative_l2": float(paired.item()),
            "validation_selection_objective": objective,
        }
        trace.append(record)
        if objective < best - 1e-5:
            best = objective
            best_step = step
            best_state = _clone_state(model)
            wait = 0
        else:
            wait += 1
        if wait >= int(contract["early_stopping_patience"]):
            break
    model.load_state_dict(best_state)
    model.eval()
    return model, {
        "stage": "validation_only_deltaphi_checkpoint_freeze",
        "seed": seed,
        "test_generated_or_accessed": False,
        "best_step": best_step,
        "steps_executed": trace[-1]["step"],
        "best_record": min(
            trace, key=lambda item: item["validation_selection_objective"]
        ),
        "trace": trace,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "retrieval": {
            "pool": "operator_training_split_only",
            "key_location": key_location.detach().cpu().tolist(),
            "key_scale": key_scale.detach().cpu().tolist(),
            "query_target_leakage": False,
        },
    }


def train_direct_probabilistic_controls(
    *,
    n1_config: Mapping[str, Any],
    n1b_config: Mapping[str, Any],
    operator_train: Mapping[str, Any],
    operator_validation: Mapping[str, Any],
    representation: Mapping[str, Any],
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Train generic and NOP-style POD Gaussian baselines on validation only."""

    _, torch = _imports()
    contract = n1b_config["direct_probabilistic_training"]
    train_context, train_boundary, train_field = _flatten_solution_split(
        operator_train
    )
    validation_context, validation_boundary, validation_field = (
        _flatten_solution_split(operator_validation)
    )
    train_coefficient = encode_pod(train_field, representation)
    validation_coefficient = encode_pod(validation_field, representation)
    # The POD draw is intentionally shared across seeds. Reset the RNG here so
    # each registered confirmatory seed, rather than the POD seed, controls
    # direct-baseline weight initialization as well as minibatch sampling.
    torch.manual_seed(seed)
    models = {
        "generic_probabilistic_operator": build_pod_probabilistic_operator(
            n1_config,
            train_context.device,
            representation=representation,
            set_encoder=False,
        ),
        "nop_adapted": build_pod_probabilistic_operator(
            n1_config,
            train_context.device,
            representation=representation,
            set_encoder=True,
        ),
    }
    optimizers = {
        name: torch.optim.AdamW(
            model.parameters(),
            lr=float(contract["learning_rate"]),
            weight_decay=float(contract["weight_decay"]),
        )
        for name, model in models.items()
    }
    generators = {
        name: torch.Generator(device=train_context.device).manual_seed(
            seed + 40000 + 137 * index
        )
        for index, name in enumerate(models)
    }
    registered = n1_config["observation_protocol"]["registered_masks"]
    masks = [(name, registered[name]) for name in contract["masks"]]
    best = {name: math.inf for name in models}
    best_step = {name: 0 for name in models}
    best_state = {name: _clone_state(model) for name, model in models.items()}
    waits = {name: 0 for name in models}
    traces = {name: [] for name in models}
    active = set(models)

    for step in range(1, int(contract["maximum_steps"]) + 1):
        _, positions = masks[(step - 1) % len(masks)]
        for name in tuple(active):
            index = torch.randint(
                0,
                train_context.shape[0],
                (int(contract["batch_size"]),),
                generator=generators[name],
                device=train_context.device,
            )
            mask = _mask_tensor(
                positions,
                index.shape[0],
                train_context.device,
                train_context.dtype,
            )
            loss = models[name].nll(
                train_context[index],
                train_boundary[index],
                mask,
                train_coefficient[index],
            ).mean()
            optimizers[name].zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(models[name].parameters(), 5.0)
            optimizers[name].step()
        if step % int(contract["validation_interval"]) != 0:
            continue
        for model in models.values():
            model.eval()
        with torch.no_grad():
            for name in tuple(active):
                values = []
                mask_values = {}
                for mask_name, positions in masks:
                    chunks = []
                    for start in range(0, validation_context.shape[0], 2048):
                        end = min(start + 2048, validation_context.shape[0])
                        mask = _mask_tensor(
                            positions,
                            end - start,
                            validation_context.device,
                            validation_context.dtype,
                        )
                        chunks.append(
                            models[name].nll(
                                validation_context[start:end],
                                validation_boundary[start:end],
                                mask,
                                validation_coefficient[start:end],
                            )
                        )
                    value = torch.cat(chunks).mean()
                    mask_values[mask_name] = float(value.item())
                    values.append(value)
                validation_nll = float(torch.stack(values).mean().item())
                traces[name].append(
                    {
                        "step": step,
                        "validation_mean_mask_latent_nll": validation_nll,
                        "validation_mask_latent_nll": mask_values,
                    }
                )
                if validation_nll < best[name] - 1e-5:
                    best[name] = validation_nll
                    best_step[name] = step
                    best_state[name] = _clone_state(models[name])
                    waits[name] = 0
                else:
                    waits[name] += 1
                    if waits[name] >= int(contract["early_stopping_patience"]):
                        active.remove(name)
        for model in models.values():
            model.train()
        if not active:
            break

    for name, model in models.items():
        model.load_state_dict(best_state[name])
        model.eval()
    representation_error = pod_representation_error(
        validation_field, representation
    )
    return models, {
        "stage": "validation_only_direct_probabilistic_checkpoint_freeze",
        "seed": seed,
        "model_initialization_seed": seed,
        "test_generated_or_accessed": False,
        "representation": {
            "rank": int(representation["rank"]),
            "seed": int(representation["seed"]),
            "iterations": int(representation["iterations"]),
            "train_mean_relative_l2": representation[
                "training_mean_relative_l2"
            ],
            "train_maximum_relative_l2": representation[
                "training_maximum_relative_l2"
            ],
            "validation_mean_relative_l2": float(
                representation_error.mean().item()
            ),
            "validation_maximum_relative_l2": float(
                representation_error.max().item()
            ),
        },
        "models": {
            name: {
                "best_step": best_step[name],
                "steps_executed": traces[name][-1]["step"],
                "best_validation_mean_mask_latent_nll": best[name],
                "trace": traces[name],
                "parameters": sum(
                    parameter.numel() for parameter in models[name].parameters()
                ),
            }
            for name in models
        },
    }


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
    # The polynomial is exactly zero on every boundary and peaks at 1/16.
    # Unit-peak scaling preserves the represented function class while avoiding
    # a 16x attenuation of the interior correction and its gradient.
    envelope = 16.0 * xx * (1.0 - xx) * yy * (1.0 - yy)
    return (
        torch.stack(features, dim=-1).reshape(-1, len(features)),
        envelope.reshape(-1),
    )


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
