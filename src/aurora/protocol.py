"""Validate the machine-readable AURORA research contract.

This module intentionally uses only Python's standard library so the protocol
can be checked before a GPU environment or medical dataset is available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class ProtocolError(ValueError):
    """Raised when a research protocol violates a project invariant."""


ALLOWED_PRIMARY_PROBLEMS = {"operator_learning_under_partial_boundary_observation"}
ALLOWED_ENDPOINTS = {"cross_sectional_rupture_status"}
ALLOWED_PROVENANCE = {
    "analytical_pde",
    "real_cfd",
    "synthetic_cfd",
    "surrogate",
    "none",
}
ALLOWED_SPLIT_UNITS = {
    "patient",
    "geometry",
    "generator_seed_geometry",
    "simulation_family",
    "aneux_base_family",
}
REQUIRED_GATES = {"G0", "G1", "G2", "G3", "G4"}
REQUIRED_DATASETS = {
    "controlled_pde",
    "nonlinear_pde",
    "aneumo",
    "aneug_flow",
    "benchanxplore",
    "cmha",
    "aneux",
}


def load_protocol(path: str | Path) -> dict[str, Any]:
    """Load a protocol JSON file and validate its top-level representation."""

    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProtocolError(f"Protocol does not exist: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Invalid JSON in {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProtocolError("Protocol root must be a JSON object.")
    return payload


def _require_keys(
    mapping: Mapping[str, Any], keys: Sequence[str], context: str
) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ProtocolError(f"{context} is missing: {', '.join(missing)}")


def _unique_ids(items: Sequence[Mapping[str, Any]], key: str, context: str) -> set[str]:
    values = [str(item.get(key, "")) for item in items]
    if "" in values:
        raise ProtocolError(f"{context} contains an empty {key}.")
    if len(values) != len(set(values)):
        raise ProtocolError(f"{context} contains duplicate {key} values.")
    return set(values)


def validate_protocol(protocol: Mapping[str, Any]) -> list[str]:
    """Return human-readable checks or raise :class:`ProtocolError`.

    The validator focuses on invariants that prevent target inflation,
    provenance loss, and split leakage. It does not judge whether a future
    experiment passed a scientific gate.
    """

    _require_keys(
        protocol,
        [
            "schema_version",
            "project",
            "task",
            "datasets",
            "model",
            "loss",
            "gates",
            "post_result_diagnostics",
            "prospective_reentry_protocols",
            "nonlinear_protocols",
            "evaluation",
            "phases",
        ],
        "protocol",
    )
    checks: list[str] = []

    project = protocol["project"]
    _require_keys(project, ["name", "status", "clinical_use"], "project")
    if project["name"] != "AURORA":
        raise ProtocolError("Project name must remain AURORA for schema v1.")
    if project["clinical_use"] is not False:
        raise ProtocolError("AURORA v1 must be marked research-only.")
    checks.append("research-only project boundary")

    task = protocol["task"]
    _require_keys(
        task,
        [
            "primary_problem",
            "application_endpoint",
            "primary_metric",
            "forbidden_claims",
        ],
        "task",
    )
    if task["primary_problem"] not in ALLOWED_PRIMARY_PROBLEMS:
        raise ProtocolError(
            "The primary task must remain partial-boundary-observation operator "
            "learning for schema v2."
        )
    if task["application_endpoint"] not in ALLOWED_ENDPOINTS:
        raise ProtocolError(
            "Only cross-sectional rupture status is supported; prospective risk "
            "requires a longitudinal protocol."
        )
    forbidden = set(task["forbidden_claims"])
    if "prospective_rupture_risk" not in forbidden or "clinical_utility" not in forbidden:
        raise ProtocolError("Task must forbid prospective-risk and clinical-utility claims.")
    if "causal_intervention_effect" not in forbidden:
        raise ProtocolError("Paired simulator responses must not be called causal effects.")
    checks.append("primary method task and application-claim guardrails")

    datasets = protocol["datasets"]
    if not isinstance(datasets, list) or not datasets:
        raise ProtocolError("datasets must be a non-empty list.")
    dataset_names = _unique_ids(datasets, "name", "datasets")
    missing_datasets = REQUIRED_DATASETS - dataset_names
    if missing_datasets:
        raise ProtocolError(
            f"Required dataset roles are absent: {', '.join(sorted(missing_datasets))}"
        )
    for dataset in datasets:
        _require_keys(
            dataset, ["name", "role", "field_provenance", "split_unit"],
            f"dataset {dataset.get('name', '?')}",
        )
        if dataset["field_provenance"] not in ALLOWED_PROVENANCE:
            raise ProtocolError(
                f"Unsupported provenance for {dataset['name']}: "
                f"{dataset['field_provenance']}"
            )
        if dataset["split_unit"] not in ALLOWED_SPLIT_UNITS:
            raise ProtocolError(
                f"Unsupported split unit for {dataset['name']}: {dataset['split_unit']}"
            )
    cmha = next(item for item in datasets if item["name"] == "cmha")
    aneux = next(item for item in datasets if item["name"] == "aneux")
    aneumo = next(item for item in datasets if item["name"] == "aneumo")
    if cmha["field_provenance"] != "real_cfd":
        raise ProtocolError("CMHA is the declared real-CFD bridge in protocol v1.")
    if aneux["field_provenance"] != "none":
        raise ProtocolError("AneuX must not be declared as real-CFD data.")
    if aneumo["split_unit"] != "aneux_base_family":
        raise ProtocolError(
            "Aneumo split must keep both deformations of an AneuX base family "
            "in one fold."
        )
    if aneumo.get("pressure_head_status") != (
        "excluded_after_train_only_scaling_audit"
    ):
        raise ProtocolError(
            "Aneumo pressure must remain excluded after the scaling audit."
        )
    checks.append("dataset provenance and split units")

    model = protocol["model"]
    numeric_model_keys = [
        "surface_queries", "volume_queries", "knn", "latent_tokens", "hidden_dim",
        "attention_layers", "attention_heads", "bc_basis_dim",
        "bc_mixture_components", "bc_covariance_rank", "bc_samples_train",
        "bc_samples_eval", "ensemble_members", "physics_collocation_points",
    ]
    _require_keys(
        model,
        [
            *numeric_model_keys,
            "observation_modes",
            "temporal_representation",
            "irregular_3d_output_contract",
        ],
        "model",
    )
    for key in numeric_model_keys:
        if not isinstance(model[key], int) or model[key] <= 0:
            raise ProtocolError(f"model.{key} must be a positive integer.")
    if model["hidden_dim"] % model["attention_heads"] != 0:
        raise ProtocolError("hidden_dim must be divisible by attention_heads.")
    if model["bc_samples_eval"] < model["bc_samples_train"]:
        raise ProtocolError("Evaluation must use at least as many BC samples as training.")
    if set(model["observation_modes"]) != {"full", "partial", "missing"}:
        raise ProtocolError("Model must support full, partial, and missing BC modes.")
    temporal = model["temporal_representation"]
    _require_keys(
        temporal,
        [
            "status",
            "fixed_fourier",
            "candidate_bases",
            "rejected_bases",
            "coefficient_budgets",
            "selection_metric",
            "leakage_rule",
        ],
        "model.temporal_representation",
    )
    if temporal["fixed_fourier"] != "rejected_by_frozen_d0":
        raise ProtocolError("Frozen D0 requires fixed Fourier to remain rejected.")
    if temporal["candidate_bases"] != ["train_only_pod"]:
        raise ProtocolError("Only train-only POD remains representation-eligible.")
    if temporal["rejected_bases"] != ["dct_ii"]:
        raise ProtocolError("DCT-II must remain rejected after D0b.")
    if temporal["coefficient_budgets"] != [17, 25]:
        raise ProtocolError("D0b must compare the frozen equal budgets 17 and 25.")
    if temporal["leakage_rule"] != "pod_fit_on_training_geometries_only":
        raise ProtocolError("Temporal POD must be fit on training geometries only.")
    irregular_3d = model["irregular_3d_output_contract"]
    _require_keys(
        irregular_3d,
        [
            "aneumo_current_candidate_channels",
            "excluded_headline_channels",
            "mandatory_baseline",
            "protocol_registration_condition",
            "headline_activation_condition",
            "headline_authorized",
        ],
        "model.irregular_3d_output_contract",
    )
    if irregular_3d["aneumo_current_candidate_channels"] != ["velocity"]:
        raise ProtocolError(
            "The Aneumo candidate must remain velocity-only after the scaling audit."
        )
    if "pressure" not in irregular_3d["excluded_headline_channels"]:
        raise ProtocolError("Aneumo pressure must not return as a headline output.")
    if irregular_3d["mandatory_baseline"] != (
        "same_case_anchor_train_tuned_global_power"
    ):
        raise ProtocolError("The strong Aneumo physical-scaling baseline is mandatory.")
    if irregular_3d["protocol_registration_condition"] != "g1s_completed_passed":
        raise ProtocolError(
            "Aneumo protocol registration must remain linked to the G1s pass."
        )
    if (
        irregular_3d["headline_activation_condition"]
        != "n1_nonlinear_strong_baseline_gate_passed"
        or irregular_3d["headline_authorized"] is not False
    ):
        raise ProtocolError(
            "Irregular-3D headline must remain deferred until a positive N1 gate."
        )
    checks.append("model dimensional contract")

    loss = protocol["loss"]
    loss_keys = [
        "full_field",
        "paired_response",
        "boundary_nll",
        "physics",
        "functional",
    ]
    _require_keys(loss, loss_keys, "loss")
    if any(not isinstance(loss[key], (int, float)) or loss[key] < 0 for key in loss_keys):
        raise ProtocolError("All loss weights must be non-negative numbers.")
    if loss["full_field"] <= 0 or loss["paired_response"] <= 0:
        raise ProtocolError("Full-field and paired-response objectives cannot be disabled.")
    checks.append("full-field and paired-response objectives")

    gates = protocol["gates"]
    gate_ids = _unique_ids(gates, "id", "gates")
    if gate_ids != REQUIRED_GATES:
        raise ProtocolError(
            "Gate set must be exactly G0–G4; change schema version to alter it."
        )
    g1 = next(item for item in gates if item["id"] == "G1")
    if "maximum_projective_consistency_error" not in g1:
        raise ProtocolError("G1 must preregister a projective-consistency threshold.")
    g4 = next(item for item in gates if item["id"] == "G4")
    required_domains = {"controlled_pde", "nonlinear_pde", "irregular_3d"}
    if int(g4.get("minimum_domains", 0)) < 3:
        raise ProtocolError("G4 must require evidence in at least three domains.")
    if set(g4.get("required_domains", [])) != required_domains:
        raise ProtocolError("G4 must retain controlled, nonlinear, and irregular-3D tests.")
    g3 = next(item for item in gates if item["id"] == "G3")
    if g3.get("same_benchmark_learned_comparison") != (
        "exploratory_after_architecture_discovery"
    ):
        raise ProtocolError("Same-benchmark learned temporal comparison is exploratory.")
    if g3.get("confirmatory_requires_fresh_transient_cases") is not True:
        raise ProtocolError("Confirmatory G3 requires fresh transient cases.")
    checks.append("coherence and cross-domain blocking gates")

    diagnostics = protocol["post_result_diagnostics"]
    diagnostic_ids = _unique_ids(diagnostics, "id", "post_result_diagnostics")
    if diagnostic_ids != {"G1b", "DA1", "DA2", "D0b"}:
        raise ProtocolError(
            "Schema v2 must retain G1b, DA1, DA2, and D0b diagnostics."
        )
    g1b = next(item for item in diagnostics if item["id"] == "G1b")
    _require_keys(
        g1b,
        [
            "status",
            "source_gate",
            "may_reopen_or_relabel_source_gate",
            "questions",
            "sample_counts",
        ],
        "G1b diagnostic",
    )
    if g1b["source_gate"] != "G1":
        raise ProtocolError("G1b must remain attributed to the failed G1 gate.")
    if g1b["may_reopen_or_relabel_source_gate"] is not False:
        raise ProtocolError("A post-result diagnostic cannot reopen or relabel G1.")
    if g1b["sample_counts"] != [128, 512, 2048]:
        raise ProtocolError("G1b sample counts are frozen at 128, 512, and 2048.")
    da1 = next(item for item in diagnostics if item["id"] == "DA1")
    _require_keys(
        da1,
        [
            "status",
            "source_gate",
            "may_reopen_or_relabel_source_gate",
            "may_define_new_gate",
            "config",
            "diagnostic_seeds",
            "success_thresholds",
            "questions",
            "matched_boundary_record_cells",
        ],
        "DA1 density attribution",
    )
    if da1["status"] not in {
        "preregistered_post_result_unrun",
        "completed_post_result_exploratory",
    }:
        raise ProtocolError("DA1 must retain a registered or exploratory status.")
    if da1["source_gate"] != "G1r":
        raise ProtocolError("DA1 must remain attributed to failed G1r.")
    if (
        da1["may_reopen_or_relabel_source_gate"] is not False
        or da1["may_define_new_gate"] is not False
    ):
        raise ProtocolError("DA1 cannot relabel a failure or define a new gate.")
    if da1["config"] != "configs/controlled_pde_density_attribution.json":
        raise ProtocolError("DA1 must point to its executable frozen config.")
    if da1["diagnostic_seeds"] != 3 or da1["success_thresholds"] is not None:
        raise ProtocolError("DA1 requires three diagnostic seeds and no threshold.")
    if da1["matched_boundary_record_cells"] != [
        "192x32",
        "768x8",
        "3072x2",
    ]:
        raise ProtocolError("DA1 matched-budget cells changed.")
    if da1["status"] == "completed_post_result_exploratory":
        _require_keys(
            da1,
            [
                "result",
                "source_commit",
                "maximum_population_objective_density_error",
                "maximum_empirical_population_selected_density_error",
                "maximum_empirical_sampled_selected_density_error",
                "attribution",
                "nonlinear_or_3d_confirmatory_training_authorized",
            ],
            "completed DA1",
        )
        if da1["result"] != (
            "results/controlled_pde_density_attribution_20260803.json"
        ):
            raise ProtocolError("Completed DA1 must retain its public aggregate.")
        if len(da1["source_commit"]) != 40:
            raise ProtocolError("Completed DA1 must retain its exact source commit.")
        if da1["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
            raise ProtocolError(
                "Exploratory DA1 cannot authorize nonlinear or 3D confirmation."
            )
    da2 = next(item for item in diagnostics if item["id"] == "DA2")
    _require_keys(
        da2,
        [
            "status",
            "source_diagnostic",
            "may_reopen_or_relabel_source_gate",
            "may_define_or_pass_new_gate",
            "may_authorize_nonlinear_or_3d_confirmatory_training",
            "config",
            "development_seeds",
            "success_thresholds",
            "estimators",
            "data_cells",
            "checkpoint_objective",
            "estimator_selection_cell",
            "higher_data_cell_role",
            "fresh_exact_gate_required_after_selection",
        ],
        "DA2 density estimator development",
    )
    if da2["status"] not in {
        "registered_development_only_unrun",
        "completed_development_only",
    }:
        raise ProtocolError("DA2 must remain development-only.")
    if da2["source_diagnostic"] != "DA1":
        raise ProtocolError("DA2 must remain linked to DA1.")
    if (
        da2["may_reopen_or_relabel_source_gate"] is not False
        or da2["may_define_or_pass_new_gate"] is not False
        or da2["may_authorize_nonlinear_or_3d_confirmatory_training"] is not False
    ):
        raise ProtocolError(
            "Development-only DA2 cannot pass a gate or authorize confirmation."
        )
    if da2["config"] != "configs/controlled_pde_density_development.json":
        raise ProtocolError("DA2 must point to its executable development config.")
    if da2["development_seeds"] != 3 or da2["success_thresholds"] is not None:
        raise ProtocolError("DA2 requires three development seeds and no threshold.")
    if da2["estimators"] != [
        "empirical_nll",
        "grouped_unbiased",
        "grouped_shrinkage_025",
        "grouped_shrinkage_050",
    ]:
        raise ProtocolError("DA2 estimator comparison changed.")
    if da2["data_cells"] != ["768x8", "3072x8"]:
        raise ProtocolError("DA2 data cells changed.")
    if da2["checkpoint_objective"] != "sampled_validation_nll":
        raise ProtocolError("DA2 must use sampled validation NLL checkpoints.")
    if da2["estimator_selection_cell"] != "768x8_original_g1r_budget":
        raise ProtocolError("DA2 must select estimators at the original G1r budget.")
    if da2["higher_data_cell_role"] != "data_sufficiency_control_only":
        raise ProtocolError("The DA2 high-data cell cannot select the estimator.")
    if da2["fresh_exact_gate_required_after_selection"] is not True:
        raise ProtocolError("DA2 selection must be followed by a fresh exact gate.")
    if da2["status"] == "completed_development_only":
        _require_keys(
            da2,
            [
                "result",
                "source_commit",
                "formal_selected_estimator",
                "material_estimator_improvement_found",
                "selected_mean_relative_improvement",
                "high_data_empirical_nll_maximum_density_error",
                "promote_grouped_estimator_to_method",
                "next_exact_sanity_candidate",
            ],
            "completed DA2",
        )
        if da2["result"] != (
            "results/controlled_pde_density_development_20260803.json"
        ):
            raise ProtocolError("Completed DA2 must retain its public aggregate.")
        if len(da2["source_commit"]) != 40:
            raise ProtocolError("Completed DA2 must retain its exact source commit.")
        if da2["formal_selected_estimator"] != "grouped_shrinkage_050":
            raise ProtocolError("DA2 must retain the fixed-rule formal selection.")
        if (
            da2["material_estimator_improvement_found"] is not False
            or da2["promote_grouped_estimator_to_method"] is not False
        ):
            raise ProtocolError(
                "DA2 did not support promoting grouped shrinkage as a method."
            )
        if da2["next_exact_sanity_candidate"] != (
            "empirical_nll_with_3072x8_data_budget"
        ):
            raise ProtocolError("DA2 supports a data-adequacy sanity next.")
    d0b = next(item for item in diagnostics if item["id"] == "D0b")
    _require_keys(
        d0b,
        [
            "status",
            "source_gate",
            "may_reopen_or_relabel_source_gate",
            "questions",
            "candidate_bases",
            "coefficient_budgets",
        ],
        "D0b diagnostic",
    )
    if d0b["source_gate"] != "G3":
        raise ProtocolError("D0b must remain attributed to the transient G3 branch.")
    if d0b["may_reopen_or_relabel_source_gate"] is not False:
        raise ProtocolError("A post-result diagnostic cannot relabel the failed D0.")
    if d0b["candidate_bases"] != ["dct_ii", "train_only_pod"]:
        raise ProtocolError("D0b candidates are frozen to DCT-II and train-only POD.")
    if d0b["coefficient_budgets"] != [17, 25]:
        raise ProtocolError("D0b coefficient budgets are frozen at 17 and 25.")
    checks.append("post-result diagnostic non-inflation contract")

    reentries = protocol["prospective_reentry_protocols"]
    reentry_ids = _unique_ids(reentries, "id", "prospective_reentry_protocols")
    if reentry_ids != {"G1r", "G1s"}:
        raise ProtocolError(
            "Schema v2 must retain failed G1r and the data-adequacy G1s."
        )
    g1r = next(item for item in reentries if item["id"] == "G1r")
    _require_keys(
        g1r,
        [
            "status",
            "source_gate",
            "may_relabel_failed_source_gate",
            "config",
            "fresh_test_seeds",
            "test_access_during_selection",
            "density_checkpoint_selection",
            "conditional_moment_evaluation",
            "end_to_end_mean_evaluation",
            "projective_metric",
            "success_thresholds",
        ],
        "G1r prospective re-entry",
    )
    allowed_reentry_status = {
        "preregistered_before_fresh_test",
        "completed_passed",
        "completed_failed",
    }
    if g1r["status"] not in allowed_reentry_status:
        raise ProtocolError("G1r must retain a registered or completed status.")
    if g1r["source_gate"] != "G1" or g1r["may_relabel_failed_source_gate"] is not False:
        raise ProtocolError("G1r cannot relabel the failed frozen G1.")
    if g1r["config"] != "configs/controlled_pde_g1r.json":
        raise ProtocolError("G1r must point to its executable frozen config.")
    if g1r["fresh_test_seeds"] != 5 or g1r["test_access_during_selection"] is not False:
        raise ProtocolError("G1r requires five fresh seeds and validation-only selection.")
    if g1r["density_checkpoint_selection"] != (
        "validation_nll_on_disjoint_geometries"
    ):
        raise ProtocolError("G1r density selection must use disjoint validation geometry.")
    if g1r["conditional_moment_evaluation"] != (
        "analytic_exact_poisson_pushforward"
    ):
        raise ProtocolError("G1r must retain analytic density-only moment evaluation.")
    if g1r["end_to_end_mean_evaluation"] != "gauss_hermite_quadrature":
        raise ProtocolError("G1r must retain deterministic end-to-end quadrature.")
    if g1r["projective_metric"] != (
        "signed_excess_over_matched_iid_floor_ci95_upper"
    ):
        raise ProtocolError("G1r projective metric must remain IID-floor calibrated.")
    expected_reentry_thresholds = {
        "maximum_density_only_standardized_mean_error": 0.05,
        "maximum_density_only_coverage_error": 0.03,
        "maximum_end_to_end_quadrature_mean_error": 0.05,
        "maximum_end_to_end_sampled_coverage_error": 0.03,
        "maximum_full_bc_operator_error": 0.03,
        "maximum_projective_excess_ci95_upper": 0.01,
        "maximum_analytic_nested_moment_residual": 0.000001,
    }
    if g1r["success_thresholds"] != expected_reentry_thresholds:
        raise ProtocolError("G1r thresholds changed after prospective registration.")
    if g1r["status"].startswith("completed_"):
        _require_keys(
            g1r,
            [
                "result",
                "source_commit",
                "failed_checks",
                "nonlinear_or_3d_confirmatory_training_authorized",
            ],
            "completed G1r",
        )
        if g1r["result"] != "results/controlled_pde_g1r_20260803.json":
            raise ProtocolError("Completed G1r must point to its public aggregate.")
        if len(g1r["source_commit"]) != 40:
            raise ProtocolError("Completed G1r must retain its exact source commit.")
        if g1r["status"] == "completed_failed":
            if not g1r["failed_checks"]:
                raise ProtocolError("Failed G1r must retain its failed checks.")
            if g1r["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
                raise ProtocolError(
                    "Failed G1r cannot authorize nonlinear or 3D confirmation."
                )
        elif g1r["failed_checks"]:
            raise ProtocolError("Passed G1r cannot retain failed checks.")
    g1s = next(item for item in reentries if item["id"] == "G1s")
    _require_keys(
        g1s,
        [
            "status",
            "source_gate",
            "source_diagnostic",
            "may_relabel_g1_or_g1r",
            "may_claim_data_quantity_as_method_contribution",
            "config",
            "fresh_test_seeds",
            "test_access_during_selection",
            "density_estimator",
            "train_geometries",
            "validation_geometries",
            "conditions_per_geometry",
            "test_geometries",
            "changes_from_g1r",
            "pass_interpretation",
            "success_thresholds",
            "nonlinear_or_3d_confirmatory_training_authorized",
        ],
        "G1s prospective data-adequacy re-entry",
    )
    if g1s["status"] not in allowed_reentry_status:
        raise ProtocolError("G1s must retain a registered or completed status.")
    if (
        g1s["source_gate"] != "G1r"
        or g1s["source_diagnostic"] != "DA2"
        or g1s["may_relabel_g1_or_g1r"] is not False
    ):
        raise ProtocolError("G1s cannot relabel failed G1/G1r and must follow DA2.")
    if g1s["may_claim_data_quantity_as_method_contribution"] is not False:
        raise ProtocolError("G1s cannot promote data quantity to a method contribution.")
    if g1s["config"] != "configs/controlled_pde_g1s.json":
        raise ProtocolError("G1s must point to its executable frozen config.")
    if g1s["fresh_test_seeds"] != 5 or g1s["test_access_during_selection"] is not False:
        raise ProtocolError("G1s requires five fresh seeds and validation-only selection.")
    if g1s["density_estimator"] != "empirical_nll":
        raise ProtocolError("G1s must retain empirical NLL; DA2 found no new method.")
    if (
        g1s["train_geometries"] != 3072
        or g1s["validation_geometries"] != 192
        or g1s["conditions_per_geometry"] != 8
        or g1s["test_geometries"] != 192
    ):
        raise ProtocolError(
            "G1s freezes the 3072x8 train and unchanged 192/192 validation/test budget."
        )
    if g1s["changes_from_g1r"] != [
        "five_entirely_fresh_simulation_family_seeds",
        "training_geometries_increased_from_768_to_3072",
    ]:
        raise ProtocolError("G1s may change only fresh seeds and training-data adequacy.")
    if g1s["pass_interpretation"] != (
        "data_adequacy_sanity_not_method_novelty_or_baseline_superiority"
    ):
        raise ProtocolError("G1s cannot inflate a data-adequacy pass into novelty.")
    if g1s["success_thresholds"] != expected_reentry_thresholds:
        raise ProtocolError("G1s must retain the original G1r thresholds.")
    if g1s["status"] == "preregistered_before_fresh_test":
        if g1s["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
            raise ProtocolError("Unrun G1s cannot authorize nonlinear or 3D training.")
        for forbidden_key in ("result", "source_commit", "failed_checks"):
            if forbidden_key in g1s:
                raise ProtocolError("Unrun G1s cannot contain post-result fields.")
    else:
        _require_keys(
            g1s,
            ["result", "source_commit", "failed_checks"],
            "completed G1s",
        )
        if g1s["result"] != "results/controlled_pde_g1s_20260803.json":
            raise ProtocolError("Completed G1s must point to its public aggregate.")
        if len(g1s["source_commit"]) != 40:
            raise ProtocolError("Completed G1s must retain its exact source commit.")
        if g1s["status"] == "completed_failed":
            if not g1s["failed_checks"]:
                raise ProtocolError("Failed G1s must retain its failed checks.")
            if g1s["nonlinear_or_3d_confirmatory_training_authorized"] is not False:
                raise ProtocolError("Failed G1s cannot authorize complex confirmation.")
        else:
            if g1s["failed_checks"]:
                raise ProtocolError("Passed G1s cannot retain failed checks.")
            if g1s["nonlinear_or_3d_confirmatory_training_authorized"] is not True:
                raise ProtocolError("A completed G1s pass must authorize the next domain.")
    checks.append("prospective G1 re-entry non-inflation and data-adequacy contract")

    nonlinear = protocol["nonlinear_protocols"]
    nonlinear_ids = _unique_ids(nonlinear, "id", "nonlinear_protocols")
    if nonlinear_ids != {"N0", "N0a", "N0r", "N1"}:
        raise ProtocolError(
            "Nonlinear ladder must contain N0, non-gating N0a, fresh N0r, and N1."
        )
    n0 = next(item for item in nonlinear if item["id"] == "N0")
    _require_keys(
        n0,
        [
            "status",
            "source_gate",
            "config",
            "context_dim",
            "boundary_components",
            "conditioning",
            "functionals",
            "checks",
            "may_establish_method_novelty",
            "may_authorize_irregular_3d_headline",
            "pass_authorizes",
        ],
        "N0 nonlinear protocol",
    )
    if (
        n0["status"] not in {"preregistered_before_gpu_run", "completed_failed"}
        or n0["source_gate"] != "G1s"
        or n0["config"] != "configs/nonlinear_pde_n0.json"
    ):
        raise ProtocolError("N0 must retain its executable and prospective status after G1s.")
    if n0["context_dim"] != 5 or n0["boundary_components"] != 8:
        raise ProtocolError("N0 freezes five context and eight boundary components.")
    if n0["conditioning"] != "analytic_for_arbitrary_component_masks":
        raise ProtocolError("N0 must retain analytic component-mask conditioning.")
    if (
        n0["may_establish_method_novelty"] is not False
        or n0["may_authorize_irregular_3d_headline"] is not False
    ):
        raise ProtocolError("N0 is numerical adequacy, not novelty or a 3D gate.")
    if n0["pass_authorizes"] != "N1_learned_model_and_strong_baseline_registration":
        raise ProtocolError("N0 may authorize only N1 registration.")
    if n0["status"] == "completed_failed":
        _require_keys(
            n0,
            [
                "result",
                "source_commit",
                "failed_checks",
                "n1_registration_authorized",
                "post_result_sampling_audit",
                "next_step",
            ],
            "completed failed N0",
        )
        if n0["result"] != "results/nonlinear_pde_n0_20260803.json":
            raise ProtocolError("Failed N0 must point to its public aggregate.")
        if len(n0["source_commit"]) != 40 or not n0["failed_checks"]:
            raise ProtocolError("Failed N0 must retain exact source and failed checks.")
        if n0["n1_registration_authorized"] is not False:
            raise ProtocolError("Failed N0 cannot authorize N1.")
    else:
        for forbidden_key in (
            "result",
            "source_commit",
            "failed_checks",
            "n1_registration_authorized",
            "post_result_sampling_audit",
            "next_step",
        ):
            if forbidden_key in n0:
                raise ProtocolError("Unrun N0 cannot contain post-result fields.")
    n0a = next(item for item in nonlinear if item["id"] == "N0a")
    _require_keys(
        n0a,
        [
            "status",
            "source_gate",
            "config",
            "source_failed_result",
            "uses_only_failed_n0_seeds",
            "all_context_condition_cases_per_seed",
            "has_success_threshold",
            "may_relabel_n0",
            "may_authorize_n1",
            "may_authorize_irregular_3d",
            "may_select_n0r_thresholds_or_seeds",
            "next_step",
        ],
        "N0a nonlinear attribution",
    )
    if (
        n0a["status"]
        not in {
            "preregistered_post_result_attribution",
            "completed_non_gating_attribution",
        }
        or n0a["source_gate"] != "N0"
        or n0a["config"] != "configs/nonlinear_pde_n0_attribution.json"
        or n0a["source_failed_result"] != "results/nonlinear_pde_n0_20260803.json"
    ):
        raise ProtocolError("N0a must remain pinned to the failed N0 result.")
    if (
        n0a["uses_only_failed_n0_seeds"] is not True
        or n0a["all_context_condition_cases_per_seed"] != 288
    ):
        raise ProtocolError("N0a must audit the complete failed-seed context grid.")
    for forbidden_authority in (
        "has_success_threshold",
        "may_relabel_n0",
        "may_authorize_n1",
        "may_authorize_irregular_3d",
        "may_select_n0r_thresholds_or_seeds",
    ):
        if n0a[forbidden_authority] is not False:
            raise ProtocolError("N0a is attribution only and cannot open or tune a gate.")
    if n0a["status"] == "completed_non_gating_attribution":
        _require_keys(
            n0a,
            [
                "result",
                "source_commit",
                "source_metrics_sha256",
                "supports_contiguous_context_sampling_hypothesis",
                "uniformly_strong_nonlinearity_across_every_context",
            ],
            "completed N0a attribution",
        )
        if (
            n0a["result"]
            != "results/nonlinear_pde_n0_attribution_20260803.json"
            or len(n0a["source_commit"]) != 40
            or len(n0a["source_metrics_sha256"]) != 64
        ):
            raise ProtocolError("Completed N0a must retain exact public provenance.")
        if (
            n0a["supports_contiguous_context_sampling_hypothesis"] is not True
            or n0a["uniformly_strong_nonlinearity_across_every_context"] is not False
        ):
            raise ProtocolError("Completed N0a interpretation cannot be inflated.")
    else:
        for forbidden_key in (
            "result",
            "source_commit",
            "source_metrics_sha256",
            "supports_contiguous_context_sampling_hypothesis",
            "uniformly_strong_nonlinearity_across_every_context",
        ):
            if forbidden_key in n0a:
                raise ProtocolError("Unrun N0a cannot contain post-result fields.")

    n0r = next(item for item in nonlinear if item["id"] == "N0r")
    _require_keys(
        n0r,
        [
            "status",
            "source_gate",
            "config",
            "contract_source_commit",
            "contract_frozen_before_n0a_outcome",
            "n0a_outcome_may_change_contract",
            "fresh_seeds",
            "reference_context_coverage",
            "paired_context_coverage",
            "pde_boundary_law_functionals_solver_unchanged",
            "scientific_thresholds_and_worst_seed_rule_unchanged",
            "may_relabel_failed_n0",
            "may_establish_method_novelty",
            "may_authorize_irregular_3d_headline",
            "pass_authorizes",
        ],
        "N0r nonlinear re-entry",
    )
    if (
        n0r["status"] != "preregistered_before_fresh_gpu_run"
        or n0r["source_gate"] != "N0"
        or n0r["config"] != "configs/nonlinear_pde_n0r.json"
        or n0r["contract_source_commit"]
        != "1a680537957e4d87849abb84eab6380c76e656c9"
    ):
        raise ProtocolError("N0r must retain its exact pre-N0a preregistration.")
    if (
        n0r["contract_frozen_before_n0a_outcome"] is not True
        or n0r["n0a_outcome_may_change_contract"] is not False
        or n0r["fresh_seeds"] != 3
    ):
        raise ProtocolError("N0r must be fresh and independent of the N0a outcome.")
    if (
        n0r["reference_context_coverage"] != "24_of_24_exactly_once_per_seed"
        or n0r["paired_context_coverage"] != "24_of_24_exactly_twice_per_seed"
    ):
        raise ProtocolError("N0r must cover every context explicitly.")
    if (
        n0r["pde_boundary_law_functionals_solver_unchanged"] is not True
        or n0r["scientific_thresholds_and_worst_seed_rule_unchanged"] is not True
    ):
        raise ProtocolError("N0r may change only the biased selector and fresh seeds.")
    for forbidden_claim in (
        "may_relabel_failed_n0",
        "may_establish_method_novelty",
        "may_authorize_irregular_3d_headline",
    ):
        if n0r[forbidden_claim] is not False:
            raise ProtocolError("N0r is numerical adequacy, not a method or 3D claim.")
    if n0r["pass_authorizes"] != "N1_learned_model_and_strong_baseline_registration":
        raise ProtocolError("N0r may authorize only N1 registration.")

    n1 = next(item for item in nonlinear if item["id"] == "N1")
    if n1["status"] != "blocked_pending_N0r" or n1["source_gate"] != "N0r":
        raise ProtocolError("N1 must remain blocked until N0r passes.")
    required_n1_baselines = {
        "conditional_mean_imputation",
        "independent_mask_heads",
        "LANO_style_partial_observation",
        "NOP_style_latent_conditioning",
        "compute_matched_generic_probabilistic_operator",
        "ACFlow_style_generative_active_feature_acquisition",
        "acquisition_conditioned_oracle",
    }
    if set(n1["mandatory_baselines"]) != required_n1_baselines:
        raise ProtocolError("N1 must retain strong partial-observation and AFA baselines.")
    if n1["five_seed_confirmation_required"] is not True:
        raise ProtocolError("N1 requires five-seed confirmation.")
    checks.append("nonlinear N0-to-N1 non-inflation and strong-baseline contract")

    evaluation = protocol["evaluation"]
    _require_keys(
        evaluation,
        [
            "operator_outer_split",
            "condition_shift_split",
            "observation_masks",
            "clinical_outer_folds",
            "clinical_inner_folds",
            "bootstrap_unit",
            "clinical_bootstrap_unit",
            "bootstrap_replicates",
            "headline_seeds",
        ],
        "evaluation",
    )
    if evaluation["operator_outer_split"] != "geometry_disjoint":
        raise ProtocolError("Operator evaluation must remain geometry-disjoint.")
    if evaluation["bootstrap_unit"] != "geometry":
        raise ProtocolError("Operator uncertainty must be bootstrapped by geometry.")
    if evaluation["clinical_bootstrap_unit"] != "patient":
        raise ProtocolError("Secondary clinical uncertainty must be bootstrapped by patient.")
    if {"full", "missing"} - set(evaluation["observation_masks"]):
        raise ProtocolError("Evaluation must include full and missing observation masks.")
    if evaluation["clinical_outer_folds"] < 3 or evaluation["clinical_inner_folds"] < 3:
        raise ProtocolError("Nested clinical validation requires at least 3 folds per level.")
    if evaluation["bootstrap_replicates"] < 1000:
        raise ProtocolError("At least 1,000 patient bootstrap replicates are required.")
    checks.append("geometry-disjoint operator and nested patient-level evaluation")

    phases = protocol["phases"]
    _unique_ids(phases, "id", "phases")
    for phase in phases:
        _require_keys(phase, ["id", "name", "requires", "outputs"], "phase")
        unknown = set(phase["requires"]) - gate_ids
        if unknown:
            raise ProtocolError(
                f"Phase {phase['id']} references unknown gates: {sorted(unknown)}"
            )
    checks.append("phase dependency graph")
    return checks


def canonical_hash(protocol: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 for split/run manifests."""

    encoded = json.dumps(
        protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "summary"):
        child = subparsers.add_parser(command)
        child.add_argument("protocol", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    protocol = load_protocol(args.protocol)
    checks = validate_protocol(protocol)
    digest = canonical_hash(protocol)
    if args.command == "validate":
        print(f"AURORA protocol valid · {len(checks)} invariant groups")
        for check in checks:
            print(f"  ✓ {check}")
        print(f"  sha256 {digest}")
    else:
        print(
            json.dumps(
                {
                    "project": protocol["project"]["name"],
                    "primary_problem": protocol["task"]["primary_problem"],
                    "application_endpoint": protocol["task"]["application_endpoint"],
                    "datasets": [item["name"] for item in protocol["datasets"]],
                    "gates": [item["id"] for item in protocol["gates"]],
                    "protocol_sha256": digest,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
