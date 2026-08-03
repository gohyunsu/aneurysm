"""Threshold-free all-context attribution for the failed nonlinear N0 gate."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde import (
    NonlinearPDEError,
    _context,
    _environment,
    _imports,
    _pde_fields,
    _quantiles,
    _relative_l2,
    _sha256,
    _write_json,
    boundary_law,
    context_stratified_case_indices,
    sample_boundary,
    solve_semilinear,
)


def load_config(path: str | Path) -> dict[str, Any]:
    """Validate the non-gating N0a attribution contract and its frozen sources."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "experiment_id",
        "status",
        "source_gate",
        "failed_n0_result",
        "failed_n0_result_sha256",
        "source_n0_config",
        "source_n0_config_sha256",
        "seeds",
        "sampling",
        "analysis",
        "decision_rule",
        "interpretation",
    }
    if set(payload) != required:
        raise NonlinearPDEError("N0a config keys changed after registration.")
    if payload["schema_version"] != "aurora.nonlinear_pde_n0_attribution.v1":
        raise NonlinearPDEError("Unexpected N0a schema version.")
    if (
        payload["status"] != "post_result_exploratory_attribution"
        or payload["source_gate"] != "N0"
    ):
        raise NonlinearPDEError("N0a must remain a post-result N0 attribution.")
    for key, hash_key in (
        ("failed_n0_result", "failed_n0_result_sha256"),
        ("source_n0_config", "source_n0_config_sha256"),
    ):
        source = (config_path.parent / payload[key]).resolve()
        if not source.is_file() or _sha256(source) != payload[hash_key]:
            raise NonlinearPDEError(f"Pinned N0a source does not match: {key}.")
    if payload["seeds"] != [62080311, 62080312, 62080313]:
        raise NonlinearPDEError("N0a must reuse only the failed N0 seeds.")
    if payload["sampling"] != {
        "contexts_per_seed": 24,
        "conditions_per_context": 12,
        "registered_contiguous_cases": 12,
        "context_stratified_cases": 12,
        "all_context_condition_cases": 288,
        "stratified_selector": "even_contexts_rotating_conditions_v1",
    }:
        raise NonlinearPDEError("N0a sampling contract changed.")
    decision = payload["decision_rule"]
    if decision != {
        "has_success_threshold": False,
        "may_relabel_n0": False,
        "may_authorize_n1": False,
        "may_authorize_irregular_3d": False,
        "may_select_n0r_thresholds_or_seeds": False,
        "result_may_motivate_fresh_context_stratified_reentry": True,
    }:
        raise NonlinearPDEError("N0a non-inflation contract changed.")
    return payload


def _pearson(left: Any, right: Any) -> float:
    _, torch = _imports()
    left = left - left.mean()
    right = right - right.mean()
    denominator = torch.linalg.vector_norm(left) * torch.linalg.vector_norm(right)
    if float(denominator.item()) <= 1e-12:
        return 0.0
    return float(torch.dot(left, right).div(denominator).item())


def run_experiment(config: Mapping[str, Any], require_cuda: bool) -> dict[str, Any]:
    """Run N0a without producing a gate decision."""

    _, torch = _imports()
    if require_cuda and not torch.cuda.is_available():
        raise NonlinearPDEError("N0a requires a scheduler-allocated CUDA device.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float32
    sampling = config["sampling"]
    contexts_per_seed = int(sampling["contexts_per_seed"])
    conditions_per_context = int(sampling["conditions_per_context"])
    total_cases = contexts_per_seed * conditions_per_context
    if total_cases != int(sampling["all_context_condition_cases"]):
        raise NonlinearPDEError("N0a full case count is inconsistent.")
    stratified_indices = context_stratified_case_indices(
        contexts_per_seed,
        conditions_per_context,
        int(sampling["context_stratified_cases"]),
    )
    seed_results: list[dict[str, Any]] = []

    for seed in [int(value) for value in config["seeds"]]:
        contexts = _context(seed, contexts_per_seed, device, dtype)
        weights, means, covariances = boundary_law(contexts)
        boundary = sample_boundary(
            weights,
            means,
            covariances,
            conditions_per_context,
            seed + 100_000,
        )
        expanded_context = contexts[:, None, :].expand(
            -1, conditions_per_context, -1
        ).reshape(total_cases, contexts.shape[-1])
        flat_boundary = boundary.reshape(total_cases, boundary.shape[-1])
        solver_args = {
            "grid_points": 33,
            "maximum_iterations": 5000,
            "tolerance": 0.000002,
            "check_interval": 50,
            "relaxation": 0.9,
        }
        semilinear, semilinear_solver = solve_semilinear(
            expanded_context, flat_boundary, **solver_args
        )
        linear, linear_solver = solve_semilinear(
            expanded_context, flat_boundary, linear=True, **solver_args
        )
        departure = _relative_l2(semilinear, linear)
        departure_grid = departure.reshape(
            contexts_per_seed, conditions_per_context
        )
        context_medians = torch.quantile(departure_grid, 0.5, dim=1)
        solution_norm = torch.linalg.vector_norm(
            semilinear.flatten(1), dim=1
        ).reshape(contexts_per_seed, conditions_per_context)
        context_solution_norm = torch.quantile(solution_norm, 0.5, dim=1)
        _, _, nonlinearity = _pde_fields(contexts, 33)
        former_reference = float(
            config["analysis"]["former_n0_reference_value_for_description_only"]
        )
        original_count = int(sampling["registered_contiguous_cases"])
        stratified = departure[
            torch.tensor(stratified_indices, device=device, dtype=torch.long)
        ]
        seed_results.append(
            {
                "seed": seed,
                "semilinear_solver": semilinear_solver,
                "linear_solver": linear_solver,
                "registered_contiguous_case_quantiles": _quantiles(
                    departure[:original_count]
                ),
                "context_stratified_case_quantiles": _quantiles(stratified),
                "all_case_quantiles": _quantiles(departure),
                "context_median_quantiles": _quantiles(context_medians),
                "contexts_at_or_above_former_n0_reference": int(
                    torch.sum(context_medians >= former_reference).item()
                ),
                "contexts_total": contexts_per_seed,
                "pearson_context_nonlinearity_vs_context_median_departure": _pearson(
                    nonlinearity, context_medians
                ),
                "pearson_context_solution_norm_vs_context_median_departure": _pearson(
                    context_solution_norm, context_medians
                ),
            }
        )

    return {
        "schema_version": "aurora.nonlinear_pde_n0_attribution.result.v1",
        "experiment_id": config["experiment_id"],
        "status": "completed_non_gating_attribution",
        "stratified_flat_indices": stratified_indices,
        "seeds": seed_results,
        "decision": {
            "n0_status": "failed_unchanged",
            "has_gate_decision": False,
            "n1_authorized": False,
            "irregular_3d_authorized": False,
            "may_select_n0r_thresholds_or_seeds": False,
            "next_step": (
                "Interpret context sensitivity, then preregister a fresh-seed "
                "context-stratified N0r without changing scientific thresholds."
            ),
        },
        "interpretation": config["interpretation"],
    }


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
        result = run_experiment(config, args.require_cuda)
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
                "has_gate_decision": False,
                "n0_status": "failed_unchanged",
                "n1_authorized": False,
                "irregular_3d_authorized": False,
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
