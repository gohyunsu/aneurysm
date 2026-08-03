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
            "activation_condition",
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
    if irregular_3d["activation_condition"] != (
        "new_exact_coherence_sanity_passes_before_any_learned_g2_run"
    ):
        raise ProtocolError(
            "Aneumo learning must remain blocked until a new exact sanity passes."
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
    if diagnostic_ids != {"G1b", "DA1", "D0b"}:
        raise ProtocolError(
            "Schema v2 must retain G1b, DA1, and D0b diagnostics."
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
    if reentry_ids != {"G1r"}:
        raise ProtocolError("Schema v2 must retain the prospectively registered G1r.")
    g1r = reentries[0]
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
    checks.append("prospective G1 re-entry non-inflation contract")

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
