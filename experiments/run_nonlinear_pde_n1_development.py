"""Run validation-only N1 core development without creating a test split."""

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

from aurora.nonlinear_pde import load_config as load_n0_config
from aurora.nonlinear_pde_decision import (
    NonlinearDecisionError,
    generate_boundary_split,
    generate_solution_split,
    load_config,
    train_core_development,
)


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--n0-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--development-index", type=int, choices=(0, 1), required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    n0_config = load_n0_config(args.n0_config)
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server runtime
        raise NonlinearDecisionError("N1 development requires torch.") from exc
    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("N1 development requires a CUDA allocation.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed = int(config["model_seeds"]["development_only"][args.development_index])
    data = config["data"]
    split_seed = data["split_seeds"]
    context_support = data["context_support"]["train_validation_id_test"]
    maximum_radius = float(
        data["boundary_latent_support"][
            "train_validation_id_test_max_mahalanobis_radius"
        ]
    )

    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(value) for value in sys.argv) + "\n", encoding="utf-8"
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "config.sha256").write_text(
        _sha256(args.config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "run_config.json", config)

    try:
        density_train = generate_boundary_split(
            contexts=int(data["density_train_contexts"]),
            conditions=int(data["density_conditions_per_context"]),
            context_seed=int(split_seed["density_train"]),
            boundary_seed=int(split_seed["density_train"]) + 1000,
            context_support=context_support,
            maximum_radius=maximum_radius,
            device=device,
        )
        density_validation = generate_boundary_split(
            contexts=int(data["density_validation_contexts"]),
            conditions=int(data["density_conditions_per_context"]),
            context_seed=int(split_seed["density_validation"]),
            boundary_seed=int(split_seed["density_validation"]) + 1000,
            context_support=context_support,
            maximum_radius=maximum_radius,
            device=device,
        )
        operator_train = generate_solution_split(
            contexts=int(data["operator_train_contexts"]),
            conditions=int(data["operator_conditions_per_context"]),
            context_seed=int(split_seed["operator_train"]),
            boundary_seed=int(split_seed["operator_train"]) + 1000,
            context_support=context_support,
            maximum_radius=maximum_radius,
            solver_config=n0_config,
            device=device,
        )
        operator_validation = generate_solution_split(
            contexts=int(data["operator_validation_contexts"]),
            conditions=int(data["operator_conditions_per_context"]),
            context_seed=int(split_seed["operator_validation"]),
            boundary_seed=int(split_seed["operator_validation"]) + 1000,
            context_support=context_support,
            maximum_radius=maximum_radius,
            solver_config=n0_config,
            device=device,
        )
        density, operator, training = train_core_development(
            config=config,
            density_train=density_train,
            density_validation=density_validation,
            operator_train=operator_train,
            operator_validation=operator_validation,
            seed=seed,
        )
        torch.save(density.state_dict(), args.output / "joint_density.pt")
        torch.save(operator.state_dict(), args.output / "solution_operator.pt")
        payload = {
            "schema_version": "aurora.nonlinear_pde_n1.development.v1",
            "experiment_id": config["experiment_id"],
            "stage": "validation_only_core_development",
            "git_commit": args.git_commit,
            "development_index": args.development_index,
            "development_seed": seed,
            "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "test_split_generated": False,
            "test_seed_accessed": False,
            "data": {
                "density_train_contexts": int(data["density_train_contexts"]),
                "density_validation_contexts": int(
                    data["density_validation_contexts"]
                ),
                "operator_train_contexts": int(data["operator_train_contexts"]),
                "operator_validation_contexts": int(
                    data["operator_validation_contexts"]
                ),
                "operator_train_solver": operator_train["solver"],
                "operator_validation_solver": operator_validation["solver"],
            },
            "training": training,
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
                "n1_gate_decided": False,
                "baseline_superiority_established": False,
                "method_novelty_established": False,
                "irregular_3d_authorized": False,
                "next_step": (
                    "Complete every preregistered baseline and validation-only "
                    "checkpoint path before any confirmatory test generation."
                ),
            },
        }
        _write_json(args.output / "metrics.json", payload)
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "stage": "validation_only_core_development",
                "test_generated_or_accessed": False,
                "n1_gate_decided": False,
            },
        )
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "stage": "validation_only_core_development",
                "test_generated_or_accessed": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
