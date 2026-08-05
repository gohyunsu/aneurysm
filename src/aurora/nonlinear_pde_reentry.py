"""Fresh context-stratified re-entry for the failed nonlinear N0 gate."""

from __future__ import annotations

import argparse
import copy
import json
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde import (
    NonlinearPDEError,
    _environment,
    _imports,
    _sha256,
    _write_json,
    context_stratified_case_indices,
    load_config as load_n0_config,
    run_experiment as run_n0_experiment,
)


EXPECTED_SEEDS = [62080321, 62080322, 62080323]
EXPECTED_THRESHOLDS = {
    "maximum_solver_normalized_residual": 0.0005,
    "maximum_coarse_reference_relative_l2": 0.04,
    "minimum_median_nonlinear_departure": 0.01,
    "minimum_worst_component_response_median": 0.01,
    "minimum_response_effective_rank": 3.0,
    "minimum_functional_winner_components": 3,
    "maximum_dominant_functional_winner_share": 0.75,
    "maximum_analytic_conditioning_route_residual": 0.00002,
}


def _require_exact_keys(
    payload: Mapping[str, Any], keys: set[str], label: str
) -> None:
    if set(payload) != keys:
        raise NonlinearPDEError(f"{label} keys changed after preregistration.")


def load_config(path: str | Path) -> dict[str, Any]:
    """Validate the N0r preregistration and all pre-outcome source pins."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_exact_keys(
        payload,
        {
            "schema_version",
            "experiment_id",
            "status",
            "source_gate",
            "failed_n0_result",
            "failed_n0_result_sha256",
            "source_n0_config",
            "source_n0_config_sha256",
            "preregistered_n0a_config",
            "preregistered_n0a_config_sha256",
            "n0a_result_may_change_this_contract",
            "may_relabel_failed_n0",
            "may_establish_method_novelty",
            "may_authorize_irregular_3d_headline",
            "seeds",
            "pde_contract",
            "boundary_law_contract",
            "sampling",
            "functionals",
            "conditioning_check",
            "success_thresholds",
            "decision_rule",
            "interpretation",
        },
        "N0r config",
    )
    if payload["schema_version"] != "aurora.nonlinear_pde_n0r.v1":
        raise NonlinearPDEError("Unexpected N0r schema version.")
    if (
        payload["status"] != "preregistered_before_n0a_result_and_fresh_gpu_run"
        or payload["source_gate"] != "N0"
    ):
        raise NonlinearPDEError("N0r must retain its pre-N0a prospective status.")
    for key, hash_key in (
        ("failed_n0_result", "failed_n0_result_sha256"),
        ("source_n0_config", "source_n0_config_sha256"),
        ("preregistered_n0a_config", "preregistered_n0a_config_sha256"),
    ):
        source = (config_path.parent / payload[key]).resolve()
        if not source.is_file() or _sha256(source) != payload[hash_key]:
            raise NonlinearPDEError(f"Pinned N0r source does not match: {key}.")

    if payload["n0a_result_may_change_this_contract"] is not False:
        raise NonlinearPDEError("N0a outcome cannot change the N0r contract.")
    for forbidden_claim in (
        "may_relabel_failed_n0",
        "may_establish_method_novelty",
        "may_authorize_irregular_3d_headline",
    ):
        if payload[forbidden_claim] is not False:
            raise NonlinearPDEError("N0r cannot inflate the failed N0 or method claim.")
    if payload["seeds"] != EXPECTED_SEEDS:
        raise NonlinearPDEError("N0r fresh seeds changed after preregistration.")
    if set(payload["seeds"]) & {62080311, 62080312, 62080313}:
        raise NonlinearPDEError("N0r seeds overlap N0/N0a.")
    if payload["pde_contract"] != {
        "source": "source_n0_config",
        "unchanged_fields": [
            "equation",
            "grid_points",
            "reference_grid_points",
            "context_dim",
            "boundary_components",
            "boundary_modes_per_edge",
            "boundary_basis",
            "dtype",
            "maximum_iterations",
            "reference_maximum_iterations",
            "convergence_tolerance",
            "residual_check_interval",
            "relaxation",
            "nonlinearity_range",
            "diffusivity_range",
        ],
    }:
        raise NonlinearPDEError("N0r PDE/solver inheritance contract changed.")

    sampling = payload["sampling"]
    if sampling != {
        "contexts_per_seed": 24,
        "conditions_per_context": 12,
        "reference_cases_per_seed": 24,
        "reference_selector": "context_stratified_case_indices_v1",
        "reference_coverage": "exactly_one_case_from_each_of_24_contexts",
        "paired_base_cases_per_seed": 48,
        "paired_selector": "context_stratified_case_indices_v1",
        "paired_coverage": "exactly_two_cases_from_each_of_24_contexts",
        "paired_component_perturbation": 0.15,
        "full_case_solver_coverage": "all_24_contexts_times_12_conditions",
    }:
        raise NonlinearPDEError("N0r sampling contract changed.")
    reference_indices = context_stratified_case_indices(24, 12, 24)
    paired_indices = context_stratified_case_indices(24, 12, 48)
    reference_counts = [
        sum(index // 12 == context for index in reference_indices)
        for context in range(24)
    ]
    paired_counts = [
        sum(index // 12 == context for index in paired_indices)
        for context in range(24)
    ]
    if reference_counts != [1] * 24 or paired_counts != [2] * 24:
        raise NonlinearPDEError("N0r selector does not meet context coverage.")
    if payload["success_thresholds"] != EXPECTED_THRESHOLDS:
        raise NonlinearPDEError("N0r scientific thresholds changed.")

    source_n0 = load_n0_config(
        (config_path.parent / payload["source_n0_config"]).resolve()
    )
    if payload["functionals"] != source_n0["functionals"]:
        raise NonlinearPDEError("N0r functionals differ from N0.")
    if payload["conditioning_check"] != source_n0["conditioning_check"]:
        raise NonlinearPDEError("N0r conditioning check differs from N0.")
    if payload["success_thresholds"] != source_n0["success_thresholds"]:
        raise NonlinearPDEError("N0r thresholds differ from N0.")
    if payload["boundary_law_contract"] != {
        "source": "source_n0_config",
        "unchanged": True,
    }:
        raise NonlinearPDEError("N0r boundary-law contract changed.")
    if payload["decision_rule"] != {
        "all_checks_required": True,
        "worst_seed_decides": True,
        "pass_authorizes_n1_model_and_strong_baseline_registration": True,
        "pass_does_not_establish_novelty_or_baseline_superiority": True,
        "failure_keeps_n1_blocked": True,
        "irregular_3d_remains_deferred_until_n1_positive": True,
    }:
        raise NonlinearPDEError("N0r decision rule changed.")
    return payload


def resolve_runtime_config(
    config: Mapping[str, Any], config_path: str | Path
) -> dict[str, Any]:
    """Resolve N0r onto the immutable N0 PDE/solver implementation."""

    source_path = (
        Path(config_path).parent / str(config["source_n0_config"])
    ).resolve()
    resolved = copy.deepcopy(load_n0_config(source_path))
    resolved["schema_version"] = "aurora.nonlinear_pde_n0r.runtime.v1"
    resolved["experiment_id"] = config["experiment_id"]
    resolved["status"] = config["status"]
    resolved["stage"] = "solver_nontriviality_reentry"
    resolved["seeds"] = list(config["seeds"])
    resolved["sampling"] = {
        "contexts_per_seed": 24,
        "conditions_per_context": 12,
        "reference_cases_per_seed": 24,
        "paired_base_cases_per_seed": 48,
        "paired_component_perturbation": 0.15,
        "all_conditions_of_one_context_remain_grouped": True,
        "case_selector": "context_stratified_case_indices_v1",
    }
    resolved["success_thresholds"] = copy.deepcopy(config["success_thresholds"])
    resolved["interpretation"] = config["interpretation"]
    return resolved


def run_experiment(
    config: Mapping[str, Any],
    config_path: str | Path,
    require_cuda: bool,
) -> dict[str, Any]:
    resolved = resolve_runtime_config(config, config_path)
    result = run_n0_experiment(resolved, require_cuda)
    result["schema_version"] = "aurora.nonlinear_pde_n0r.result.v1"
    result["source_gate"] = "failed_N0_with_pre_outcome_N0r_preregistration"
    result["decision"]["failed_n0_status"] = "failed_unchanged"
    result["decision"]["irregular_3d_headline_authorized"] = False
    result["decision"]["method_novelty_established"] = False
    result["decision"]["next_step"] = (
        "Preregister N1 learned nonlinear comparison with strong baselines."
        if result["aggregate"]["gate_passed"]
        else "Keep N1 and irregular 3D blocked; do not tune N0r after outcome."
    )
    result["interpretation"] = config["interpretation"]
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(value) for value in sys.argv) + "\n", encoding="utf-8"
    )
    (args.output / "git_commit.txt").write_text(args.git_commit + "\n", encoding="utf-8")
    (args.output / "config.sha256").write_text(
        _sha256(args.config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "run_config.json", config)
    try:
        result = run_experiment(config, args.config, args.require_cuda)
        _, torch = _imports()
        result.update(
            {
                "git_commit": args.git_commit,
                "started_at_utc": started,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "environment": _environment(torch),
            }
        )
        _write_json(args.output / "metrics.json", result)
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "gate_passed": result["aggregate"]["gate_passed"],
                "failed_n0_status": "failed_unchanged",
                "n1_registration_authorized": result["decision"][
                    "n1_model_and_strong_baseline_registration_authorized"
                ],
                "irregular_3d_headline_authorized": False,
            },
        )
        return 0
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
