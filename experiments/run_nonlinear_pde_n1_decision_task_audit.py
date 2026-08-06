"""Run the true-law/true-simulator nonlinear decision-task adequacy audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    generate_boundary_split,
    generate_solution_split,
)
from aurora.nonlinear_pde_decision_task_audit import (
    evaluate_true_decision_task,
    load_decision_task_audit_config,
)
from experiments.run_nonlinear_pde_n1c_outer_test import _solve_functionals


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _aggregate_solver_calls(
    summaries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not summaries:
        raise NonlinearDecisionError("Decision-task audit recorded no solver calls.")
    if not all(item.get("all_converged") for item in summaries):
        raise NonlinearDecisionError("Decision-task oracle solver did not converge.")
    return {
        "oracle_call_groups": len(summaries),
        "solver_batches": sum(int(item["batches"]) for item in summaries),
        "all_converged": True,
        "maximum_normalized_residual": max(
            float(item["maximum_normalized_residual"]) for item in summaries
        ),
        "maximum_iterations": max(
            int(item["maximum_iterations"]) for item in summaries
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    _, n0_config, audit_config = load_decision_task_audit_config(
        args.audit_config
    )
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server runtime
        raise NonlinearDecisionError("Decision-task audit requires torch.") from exc
    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("Decision-task audit requires CUDA.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data = audit_config["data"]
    split_seeds = data["split_seeds"]
    support = data["context_support"]
    radius = float(data["maximum_latent_mahalanobis_radius"])
    solver_batch_size = int(data["solver_batch_size"])

    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(value) for value in sys.argv) + "\n",
        encoding="utf-8",
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "audit_config.sha256").write_text(
        _sha256(args.audit_config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "audit_run_config.json", audit_config)

    try:
        calibration = generate_solution_split(
            contexts=int(data["calibration_contexts"]),
            conditions=int(data["calibration_conditions_per_context"]),
            context_seed=int(split_seeds["calibration_context"]),
            boundary_seed=int(split_seeds["calibration_boundary"]),
            context_support=support,
            maximum_radius=radius,
            solver_config=n0_config,
            device=device,
            solver_batch_size=solver_batch_size,
        )
        audit = generate_boundary_split(
            contexts=int(data["audit_contexts"]),
            conditions=int(data["audit_conditions_per_context"]),
            context_seed=int(split_seeds["audit_context"]),
            boundary_seed=int(split_seeds["audit_boundary"]),
            context_support=support,
            maximum_radius=radius,
            device=device,
        )

        def solve_functionals(
            context: Any,
            boundary: Any,
        ) -> tuple[Any, Mapping[str, Any]]:
            return _solve_functionals(
                context,
                boundary,
                n0_config=n0_config,
                batch_size=solver_batch_size,
            )

        aggregate, per_context, solver_calls = evaluate_true_decision_task(
            calibration_split=calibration,
            audit_split=audit,
            audit_config=audit_config,
            solve_functionals=solve_functionals,
        )
        solver = _aggregate_solver_calls(solver_calls)
        payload = {
            "schema_version": (
                "aurora.nonlinear_pde_n1_decision_task_audit.result.v1"
            ),
            "experiment_id": audit_config["experiment_id"],
            "stage": audit_config["stage"],
            "git_commit": args.git_commit,
            "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "test_contexts_generated": 0,
            "test_split_generated": False,
            "test_seed_accessed": False,
            "learned_models_loaded": 0,
            "learned_checkpoints_loaded": 0,
            "data": {
                "calibration_contexts": int(data["calibration_contexts"]),
                "calibration_conditions_per_context": int(
                    data["calibration_conditions_per_context"]
                ),
                "audit_contexts": int(data["audit_contexts"]),
                "audit_conditions_per_context": int(
                    data["audit_conditions_per_context"]
                ),
                "calibration_and_audit_splits_disjoint_by_seed": True,
            },
            "task_adequacy": aggregate,
            "solver": solver,
            "environment": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "torch": torch.__version__,
                "cuda_runtime": torch.version.cuda,
                "cuda_available": torch.cuda.is_available(),
                "gpu_name": (
                    torch.cuda.get_device_name(0)
                    if torch.cuda.is_available()
                    else None
                ),
                "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            },
            "decision": {
                "has_success_threshold": False,
                "task_pass_fail_label_assigned": False,
                "method_or_checkpoint_selected": False,
                "n1c_verdict_unchanged": True,
                "n1d_or_irregular_3d_authorized": False,
                "method_novelty_established": False,
                "next_step": (
                    "Interpret the frozen task-adequacy estimands jointly with "
                    "the separately preregistered density-objective controls."
                ),
            },
        }
        _write_json(args.output / "metrics.json", payload)
        _write_json(
            args.output / "per_context_metrics.json",
            {
                "schema_version": (
                    "aurora.nonlinear_pde_n1_decision_task_audit."
                    "per_context.v1"
                ),
                "audit_context_seed": int(split_seeds["audit_context"]),
                "task_adequacy": per_context,
            },
        )
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "stage": audit_config["stage"],
                "test_generated_or_accessed": False,
                "learned_model_or_checkpoint_used": False,
                "gate_decided": False,
            },
        )
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "stage": audit_config["stage"],
                "test_generated_or_accessed": False,
                "learned_model_or_checkpoint_used": False,
                "gate_decided": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
