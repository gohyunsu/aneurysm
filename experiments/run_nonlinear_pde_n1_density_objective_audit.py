"""Run one seed of the threshold-free nonlinear density-objective audit."""

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
)
from aurora.nonlinear_pde_density_objective import (
    evaluate_density_objective_variants,
    load_density_objective_audit_config,
    train_density_objective_variants,
)


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--seed-index", type=int, choices=range(5), required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    n1_config, audit_config = load_density_objective_audit_config(
        args.audit_config
    )
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server runtime
        raise NonlinearDecisionError("Density-objective audit requires torch.") from exc
    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("Density-objective audit requires CUDA.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = int(audit_config["model_seeds"][args.seed_index])
    data = audit_config["data"]
    split_seeds = data["split_seeds"]
    support = data["context_support"]
    radius = float(data["maximum_latent_mahalanobis_radius"])

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
        train = generate_boundary_split(
            contexts=int(data["train_contexts"]),
            conditions=int(data["conditions_per_context"]),
            context_seed=int(split_seeds["train_context"]),
            boundary_seed=int(split_seeds["train_boundary"]),
            context_support=support,
            maximum_radius=radius,
            device=device,
        )
        selection = generate_boundary_split(
            contexts=int(data["selection_validation_contexts"]),
            conditions=int(data["conditions_per_context"]),
            context_seed=int(split_seeds["selection_context"]),
            boundary_seed=int(split_seeds["selection_boundary"]),
            context_support=support,
            maximum_radius=radius,
            device=device,
        )
        audit = generate_boundary_split(
            contexts=int(data["audit_validation_contexts"]),
            conditions=int(data["conditions_per_context"]),
            context_seed=int(split_seeds["audit_context"]),
            boundary_seed=int(split_seeds["audit_boundary"]),
            context_support=support,
            maximum_radius=radius,
            device=device,
        )
        models, history = train_density_objective_variants(
            n1_config=n1_config,
            audit_config=audit_config,
            train_split=train,
            selection_split=selection,
            seed=seed,
        )
        aggregate, per_context = evaluate_density_objective_variants(
            models=models,
            audit_split=audit,
            audit_config=audit_config,
        )
        checkpoints = {}
        for name, model in models.items():
            path = args.output / f"{name}.pt"
            torch.save(model.state_dict(), path)
            checkpoints[name] = {
                "file": path.name,
                "sha256": _sha256(path),
                "parameters": sum(
                    parameter.numel() for parameter in model.parameters()
                ),
            }
        payload = {
            "schema_version": (
                "aurora.nonlinear_pde_n1_density_objective_audit.seed.v1"
            ),
            "experiment_id": audit_config["experiment_id"],
            "stage": audit_config["stage"],
            "git_commit": args.git_commit,
            "seed_index": args.seed_index,
            "model_seed": seed,
            "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "test_contexts_generated": 0,
            "test_split_generated": False,
            "test_seed_accessed": False,
            "data": {
                "train_contexts": int(data["train_contexts"]),
                "selection_validation_contexts": int(
                    data["selection_validation_contexts"]
                ),
                "audit_validation_contexts": int(
                    data["audit_validation_contexts"]
                ),
                "conditions_per_context": int(data["conditions_per_context"]),
                "splits_disjoint_by_seed": True,
            },
            "training": history,
            "audit_validation": aggregate,
            "artifacts": {"checkpoints": checkpoints},
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
                "cross_variant_method_selected": False,
                "n1c_verdict_unchanged": True,
                "n1d_or_irregular_3d_authorized": False,
                "method_novelty_established": False,
                "next_step": (
                    "Aggregate all five paired development seeds without "
                    "selecting a winner or accessing the N1 test."
                ),
            },
        }
        _write_json(args.output / "metrics.json", payload)
        _write_json(
            args.output / "per_context_metrics.json",
            {
                "schema_version": (
                    "aurora.nonlinear_pde_n1_density_objective_audit."
                    "per_context.v1"
                ),
                "model_seed": seed,
                "audit_validation": per_context,
            },
        )
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "stage": audit_config["stage"],
                "seed_index": args.seed_index,
                "model_seed": seed,
                "test_generated_or_accessed": False,
                "gate_decided": False,
            },
        )
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "stage": audit_config["stage"],
                "seed_index": args.seed_index,
                "model_seed": seed,
                "test_generated_or_accessed": False,
                "gate_decided": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
