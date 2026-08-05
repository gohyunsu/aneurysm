"""Run threshold-free N1 operator optimization attribution on validation only."""

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
    generate_solution_split,
    load_config,
    load_optimization_config,
    train_operator_optimization_attribution,
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
    parser.add_argument("--attribution-config", type=Path, required=True)
    parser.add_argument("--n0-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    attribution = load_optimization_config(args.attribution_config)
    n0_config = load_n0_config(args.n0_config)
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server runtime
        raise NonlinearDecisionError("N1 attribution requires torch.") from exc
    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("N1 attribution requires a CUDA allocation.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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
    (args.output / "attribution_config.sha256").write_text(
        _sha256(args.attribution_config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "run_config.json", config)
    _write_json(args.output / "attribution_run_config.json", attribution)

    try:
        operator_train = generate_solution_split(
            contexts=int(attribution["data_contract"]["operator_train_contexts"]),
            conditions=int(attribution["data_contract"]["conditions_per_context"]),
            context_seed=int(split_seed["operator_train"]),
            boundary_seed=int(split_seed["operator_train"]) + 1000,
            context_support=context_support,
            maximum_radius=maximum_radius,
            solver_config=n0_config,
            device=device,
        )
        operator_validation = generate_solution_split(
            contexts=int(
                attribution["data_contract"]["operator_validation_contexts"]
            ),
            conditions=int(attribution["data_contract"]["conditions_per_context"]),
            context_seed=int(split_seed["operator_validation"]),
            boundary_seed=int(split_seed["operator_validation"]) + 1000,
            context_support=context_support,
            maximum_radius=maximum_radius,
            solver_config=n0_config,
            device=device,
        )
        operators, training = train_operator_optimization_attribution(
            n1_config=config,
            attribution_config=attribution,
            operator_train=operator_train,
            operator_validation=operator_validation,
        )
        for name, operator in operators.items():
            torch.save(operator.state_dict(), args.output / f"{name}.pt")
        payload = {
            "schema_version": (
                "aurora.nonlinear_pde_n1.optimization_attribution.result.v1"
            ),
            "experiment_id": attribution["experiment_id"],
            "stage": attribution["stage"],
            "git_commit": args.git_commit,
            "development_seed": attribution["development_seed"],
            "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "test_contexts_generated": 0,
            "test_split_generated": False,
            "test_seed_accessed": False,
            "data": {
                "operator_train_contexts": int(
                    attribution["data_contract"]["operator_train_contexts"]
                ),
                "operator_validation_contexts": int(
                    attribution["data_contract"]["operator_validation_contexts"]
                ),
                "train_solver": operator_train["solver"],
                "validation_solver": operator_validation["solver"],
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
                "has_gate_decision": False,
                "n1_passed": False,
                "confirmatory_test_authorized": False,
                "irregular_3d_authorized": False,
                "next_step": (
                    "Freeze the selected validation variant in a new prospective "
                    "N1 version before any confirmatory test generation."
                ),
            },
        }
        _write_json(args.output / "metrics.json", payload)
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "stage": attribution["stage"],
                "test_generated_or_accessed": False,
                "has_gate_decision": False,
            },
        )
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "stage": attribution["stage"],
                "test_generated_or_accessed": False,
                "has_gate_decision": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
