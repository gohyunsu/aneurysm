"""Prospective N1 contract for route-consistent functional decisions.

The learned experiment is implemented behind this validator.  Keeping contract
validation separate makes it impossible to silently turn numerical N0r
adequacy into a learned-method or irregular-3D claim.
"""

from __future__ import annotations

import hashlib
import json
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
