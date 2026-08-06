"""Run one prospective validation-only seed of the M0 mechanism gate."""

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

from aurora.nonlinear_pde import (
    boundary_law,
    solution_functionals,
    solve_semilinear,
)
from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    build_solution_operator,
    generate_solution_split,
)
from aurora.nonlinear_pde_evaluation import checkpoint_state_dict
from aurora.nonlinear_pde_operator_pullback import (
    evaluate_operator_pullback_variants,
    load_operator_pullback_config,
    train_operator_pullback_variants,
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


def _attach_true_law(split: dict[str, Any]) -> None:
    weights, means, covariances = boundary_law(split["context"])
    split["true_weights"] = weights
    split["true_means"] = means
    split["true_covariances"] = covariances


def _solve_functionals(
    context: Any,
    boundary: Any,
    *,
    n0_config: Mapping[str, Any],
    batch_size: int,
) -> tuple[Any, dict[str, Any]]:
    import torch

    pde = n0_config["pde"]
    values = []
    summaries = []
    for start in range(0, context.shape[0], batch_size):
        end = min(start + batch_size, context.shape[0])
        with torch.no_grad():
            field, summary = solve_semilinear(
                context[start:end],
                boundary[start:end],
                grid_points=int(pde["grid_points"]),
                maximum_iterations=int(pde["maximum_iterations"]),
                tolerance=float(pde["convergence_tolerance"]),
                check_interval=int(pde["residual_check_interval"]),
                relaxation=float(pde["relaxation"]),
            )
            functional = solution_functionals(field, context[start:end])
        if not summary["converged"]:
            raise NonlinearDecisionError("M0 audit simulator solve failed.")
        values.append(functional)
        summaries.append(summary)
    return torch.cat(values, dim=0), {
        "batches": len(summaries),
        "all_converged": True,
        "maximum_normalized_residual": max(
            item["maximum_normalized_residual"] for item in summaries
        ),
        "maximum_iterations": max(
            int(item["iterations"]) for item in summaries
        ),
    }


def _operator_validation_error(
    operator: Any,
    split: Mapping[str, Any],
    *,
    chunk_size: int = 4096,
) -> float:
    import torch

    contexts, conditions = split["boundary"].shape[:2]
    context = (
        split["context"][:, None]
        .expand(-1, conditions, -1)
        .reshape(-1, 5)
    )
    boundary = split["boundary"].reshape(-1, 8)
    target = split["field"].reshape(
        contexts * conditions,
        split["field"].shape[-2],
        split["field"].shape[-1],
    )
    values = []
    with torch.no_grad():
        for start in range(0, boundary.shape[0], chunk_size):
            end = min(start + chunk_size, boundary.shape[0])
            prediction = operator(context[start:end], boundary[start:end])
            relative = torch.linalg.vector_norm(
                (prediction - target[start:end]).flatten(1), dim=1
            ) / torch.linalg.vector_norm(
                target[start:end].flatten(1), dim=1
            ).clamp_min(1e-6)
            values.append(relative)
    return float(torch.cat(values).mean().item())


def _generate_split(
    *,
    contexts: int,
    data: Mapping[str, Any],
    context_seed: int,
    boundary_seed: int,
    n0_config: Mapping[str, Any],
    device: Any,
) -> dict[str, Any]:
    split = generate_solution_split(
        contexts=contexts,
        conditions=int(data["conditions_per_context"]),
        context_seed=context_seed,
        boundary_seed=boundary_seed,
        context_support=data["context_support"],
        maximum_radius=float(data["maximum_latent_mahalanobis_radius"]),
        solver_config=n0_config,
        device=device,
        solver_batch_size=int(data["solver_batch_size"]),
    )
    _attach_true_law(split)
    return split


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mechanism-config", type=Path, required=True)
    parser.add_argument("--checkpoint-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--seed-index", type=int, choices=range(3), required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    n1_config, config, manifest = load_operator_pullback_config(
        args.mechanism_config
    )
    n0_path = (
        args.mechanism_config.parent
        / config["parents"]["n0_solver_config"]["path"]
    ).resolve()
    n0_config = json.loads(n0_path.read_text(encoding="utf-8"))
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server runtime
        raise NonlinearDecisionError("M0 mechanism gate requires torch.") from exc
    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("M0 mechanism gate requires CUDA.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = int(config["model_seeds"][args.seed_index])
    data = config["data"]
    split_seed = data["split_seeds"]

    manifest_index = int(
        config["frozen_operator"]["manifest_seed_indices"][args.seed_index]
    )
    manifest_seed = manifest["seed_runs"][manifest_index]
    checkpoint_name = "aurora_shared_operator_pair_loss_zero"
    checkpoint_path = (
        args.checkpoint_root
        / f"seed_{manifest_index}"
        / f"{checkpoint_name}.pt"
    )
    expected_checkpoint_sha = manifest_seed["checkpoint_sha256"][
        checkpoint_name
    ]

    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(value) for value in sys.argv) + "\n",
        encoding="utf-8",
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "mechanism_config.sha256").write_text(
        _sha256(args.mechanism_config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "mechanism_run_config.json", config)

    try:
        operator = build_solution_operator(n1_config, device)
        operator.load_state_dict(
            checkpoint_state_dict(
                checkpoint_path, expected_checkpoint_sha, device
            )
        )
        operator.eval()
        for parameter in operator.parameters():
            parameter.requires_grad_(False)

        train = _generate_split(
            contexts=int(data["train_contexts"]),
            data=data,
            context_seed=int(split_seed["train_context"]),
            boundary_seed=int(split_seed["train_boundary"]),
            n0_config=n0_config,
            device=device,
        )
        selection = _generate_split(
            contexts=int(data["selection_validation_contexts"]),
            data=data,
            context_seed=int(split_seed["selection_context"]),
            boundary_seed=int(split_seed["selection_boundary"]),
            n0_config=n0_config,
            device=device,
        )
        audit = _generate_split(
            contexts=int(data["audit_validation_contexts"]),
            data=data,
            context_seed=int(split_seed["audit_context"]),
            boundary_seed=int(split_seed["audit_boundary"]),
            n0_config=n0_config,
            device=device,
        )
        operator_error = _operator_validation_error(operator, audit)
        for split in (train, selection):
            split.pop("field")

        models, standardization, history = train_operator_pullback_variants(
            n1_config=n1_config,
            config=config,
            train_split=train,
            selection_split=selection,
            operator=operator,
            seed=seed,
        )
        audit.pop("field")

        def solve_functionals_callback(
            context: Any, boundary: Any
        ) -> tuple[Any, Mapping[str, Any]]:
            return _solve_functionals(
                context,
                boundary,
                n0_config=n0_config,
                batch_size=int(data["solver_batch_size"]),
            )

        aggregate, per_context, solver_summaries = (
            evaluate_operator_pullback_variants(
                models=models,
                audit_split=audit,
                operator=operator,
                standardization_payload=standardization,
                config=config,
                solve_functionals=solve_functionals_callback,
                seed=seed,
            )
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
                "aurora.nonlinear_pde_n1_missing_operator_pullback_m0.seed.v1"
            ),
            "experiment_id": config["experiment_id"],
            "stage": config["stage"],
            "git_commit": args.git_commit,
            "seed_index": args.seed_index,
            "model_seed": seed,
            "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "test_contexts_generated": 0,
            "test_split_generated": False,
            "test_seed_accessed": False,
            "frozen_operator": {
                "manifest_seed_index": manifest_index,
                "checkpoint_id": checkpoint_name,
                "checkpoint_sha256": expected_checkpoint_sha,
                "audit_validation_full_bc_relative_l2": operator_error,
                "parameters_frozen": True,
            },
            "data": {
                "train_contexts": int(data["train_contexts"]),
                "selection_validation_contexts": int(
                    data["selection_validation_contexts"]
                ),
                "audit_validation_contexts": int(
                    data["audit_validation_contexts"]
                ),
                "conditions_per_context": int(data["conditions_per_context"]),
                "acquisition_audit_contexts": int(
                    data["acquisition_audit_contexts"]
                ),
                "splits_disjoint_by_seed": True,
            },
            "training": history,
            "audit_validation": aggregate,
            "solver": {
                "all_converged": all(
                    item.get("all_converged", False)
                    for item in solver_summaries
                ),
                "summaries": solver_summaries,
            },
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
                "mechanism_gate_decided_per_seed": False,
                "n1c_verdict_unchanged": True,
                "fresh_reentry_registered": False,
                "n1d_or_irregular_3d_authorized": False,
                "method_novelty_established": False,
                "local_weight_or_kernel_repair_authorized": False,
                "next_step": (
                    "Aggregate all three preregistered development seeds once."
                ),
            },
        }
        _write_json(args.output / "metrics.json", payload)
        _write_json(
            args.output / "per_context_metrics.json",
            {
                "schema_version": (
                    "aurora.nonlinear_pde_n1_missing_operator_pullback_m0."
                    "per_context.v1"
                ),
                "model_seed": seed,
                "audit_validation": per_context,
            },
        )
        _write_json(
            args.output / "training_standardization.json",
            standardization,
        )
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "stage": config["stage"],
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
                "stage": config["stage"],
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
