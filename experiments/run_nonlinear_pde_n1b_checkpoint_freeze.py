"""Freeze one N1b confirmatory-seed model set using train/validation only."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
    fit_train_only_pod,
    generate_boundary_split,
    generate_solution_split,
    load_n1b_config,
    train_completion_development,
    train_deltaphi_control,
    train_direct_probabilistic_controls,
    train_shared_operator_controls,
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


def _best_values(history: Mapping[str, Any]) -> list[float]:
    values = []
    for model in history["models"].values():
        if "best_record" in model:
            values.extend(
                float(value)
                for key, value in model["best_record"].items()
                if key.startswith("validation_")
            )
        for key, value in model.items():
            if key.startswith("best_validation_"):
                values.append(float(value))
    return values


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n1b-config", type=Path, required=True)
    parser.add_argument("--n0-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--seed-index", type=int, choices=range(5), required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)

    n1_config, n1b_config = load_n1b_config(args.n1b_config)
    n0_config = load_n0_config(args.n0_config)
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server runtime
        raise NonlinearDecisionError("N1b checkpoint freeze requires torch.") from exc
    if args.require_cuda and not torch.cuda.is_available():
        raise NonlinearDecisionError("N1b checkpoint freeze requires CUDA.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seeds = n1b_config["checkpoint_freeze"]["confirmatory_model_seeds"]
    seed = int(seeds[args.seed_index])
    data = n1_config["data"]
    split_seed = data["split_seeds"]
    support = data["context_support"]["train_validation_id_test"]
    maximum_radius = float(
        data["boundary_latent_support"][
            "train_validation_id_test_max_mahalanobis_radius"
        ]
    )

    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(value) for value in sys.argv) + "\n",
        encoding="utf-8",
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "n1b_config.sha256").write_text(
        _sha256(args.n1b_config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "n1_run_config.json", n1_config)
    _write_json(args.output / "n1b_run_config.json", n1b_config)

    try:
        density_train = generate_boundary_split(
            contexts=int(data["density_train_contexts"]),
            conditions=int(data["density_conditions_per_context"]),
            context_seed=int(split_seed["density_train"]),
            boundary_seed=int(split_seed["density_train"]) + 1000,
            context_support=support,
            maximum_radius=maximum_radius,
            device=device,
        )
        density_validation = generate_boundary_split(
            contexts=int(data["density_validation_contexts"]),
            conditions=int(data["density_conditions_per_context"]),
            context_seed=int(split_seed["density_validation"]),
            boundary_seed=int(split_seed["density_validation"]) + 1000,
            context_support=support,
            maximum_radius=maximum_radius,
            device=device,
        )
        operator_train = generate_solution_split(
            contexts=int(data["operator_train_contexts"]),
            conditions=int(data["operator_conditions_per_context"]),
            context_seed=int(split_seed["operator_train"]),
            boundary_seed=int(split_seed["operator_train"]) + 1000,
            context_support=support,
            maximum_radius=maximum_radius,
            solver_config=n0_config,
            device=device,
        )
        operator_validation = generate_solution_split(
            contexts=int(data["operator_validation_contexts"]),
            conditions=int(data["operator_conditions_per_context"]),
            context_seed=int(split_seed["operator_validation"]),
            boundary_seed=int(split_seed["operator_validation"]) + 1000,
            context_support=support,
            maximum_radius=maximum_radius,
            solver_config=n0_config,
            device=device,
        )

        completion_models, completion_history = train_completion_development(
            config=n1_config,
            density_train=density_train,
            density_validation=density_validation,
            seed=seed,
        )
        shared_models, shared_history = train_shared_operator_controls(
            n1_config=n1_config,
            n1b_config=n1b_config,
            operator_train=operator_train,
            operator_validation=operator_validation,
            seed=seed,
        )
        direct_contract = n1b_config["direct_probabilistic_training"]
        flat_training_field = operator_train["field"].reshape(
            -1,
            operator_train["field"].shape[-2],
            operator_train["field"].shape[-1],
        )
        representation = fit_train_only_pod(
            flat_training_field,
            rank=int(direct_contract["latent_rank"]),
            seed=int(direct_contract["representation_seed"]),
            iterations=int(direct_contract["randomized_pca_iterations"]),
        )
        direct_models, direct_history = train_direct_probabilistic_controls(
            n1_config=n1_config,
            n1b_config=n1b_config,
            operator_train=operator_train,
            operator_validation=operator_validation,
            representation=representation,
            seed=seed,
        )
        deltaphi, deltaphi_history = train_deltaphi_control(
            n1_config=n1_config,
            n1b_config=n1b_config,
            operator_train=operator_train,
            operator_validation=operator_validation,
            representation=representation,
            seed=seed,
        )

        checkpoint_models = {
            "aurora_joint_density": completion_models["aurora_joint"],
            "independent_mask_heads": completion_models["independent_mask_heads"],
            "lano_adapted_completion": completion_models["lano_adapted"],
            "acflow_adapted_completion": completion_models["acflow_adapted"],
            **shared_models,
            "deltaphi_style_residual": deltaphi,
            **direct_models,
        }
        expected = set(
            n1b_config["checkpoint_freeze"]["trainable_checkpoints_per_seed"]
        )
        if set(checkpoint_models) != expected:
            raise NonlinearDecisionError("N1b checkpoint set is incomplete.")
        checkpoint_files = {}
        for name, model in checkpoint_models.items():
            path = args.output / f"{name}.pt"
            torch.save(model.state_dict(), path)
            checkpoint_files[name] = {
                "file": path.name,
                "sha256": _sha256(path),
                "parameters": sum(
                    parameter.numel() for parameter in model.parameters()
                ),
            }
        representation_path = args.output / "train_only_pod_representation.pt"
        torch.save(
            {
                key: value
                for key, value in representation.items()
                if key
                in {
                    "mean",
                    "basis",
                    "coefficient_location",
                    "coefficient_scale",
                    "rank",
                    "seed",
                    "iterations",
                }
            },
            representation_path,
        )
        reference_parameters = checkpoint_files[
            "aurora_shared_operator_pair_loss"
        ]["parameters"]
        parameter_tolerance = float(
            n1_config["training"]["parameter_match_tolerance_fraction"]
        )
        matched_models = {}
        for name in (
            "deltaphi_style_residual",
            "generic_probabilistic_operator",
            "nop_adapted",
        ):
            fraction = abs(
                checkpoint_files[name]["parameters"] - reference_parameters
            ) / reference_parameters
            matched_models[name] = {
                "relative_parameter_difference": fraction,
                "within_tolerance": fraction <= parameter_tolerance,
            }

        all_values = [
            *_best_values(completion_history),
            *_best_values(shared_history),
            *_best_values(direct_history),
            float(
                deltaphi_history["best_record"][
                    "validation_selection_objective"
                ]
            ),
        ]
        selected_shared = shared_history["models"][
            "aurora_shared_operator_pair_loss"
        ]["best_record"]
        checkpoint_eligible = (
            all(math.isfinite(value) for value in all_values)
            and all(
                item["within_tolerance"] for item in matched_models.values()
            )
            and selected_shared["validation_full_bc_relative_l2"]
            <= float(
                n1b_config["success_rule"][
                    "full_bc_operator_relative_l2_maximum"
                ]
            )
        )
        payload = {
            "schema_version": "aurora.nonlinear_pde_n1b.checkpoint_seed.v1",
            "experiment_id": n1b_config["experiment_id"],
            "stage": "confirmatory_seed_training_validation_only_checkpoint_freeze",
            "git_commit": args.git_commit,
            "seed_index": args.seed_index,
            "model_seed": seed,
            "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "test_contexts_generated": 0,
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
            "training": {
                "completion": completion_history,
                "shared_operators": shared_history,
                "direct_probabilistic": direct_history,
                "deltaphi": deltaphi_history,
            },
            "artifacts": {
                "checkpoints": checkpoint_files,
                "train_only_pod_representation": {
                    "file": representation_path.name,
                    "sha256": _sha256(representation_path),
                },
            },
            "compute_matching": {
                "reference_parameters": reference_parameters,
                "tolerance_fraction": parameter_tolerance,
                "models": matched_models,
            },
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
                "checkpoint_seed_eligible": checkpoint_eligible,
                "all_checkpoint_hashes_present": len(checkpoint_files)
                == len(expected),
                "n1_gate_decided": False,
                "n1_passed": False,
                "confirmatory_test_authorized": False,
                "irregular_3d_authorized": False,
                "next_step": (
                    "Complete all five validation-only seed jobs and commit one "
                    "aggregate checkpoint manifest before test generation."
                ),
            },
        }
        _write_json(args.output / "metrics.json", payload)
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "stage": payload["stage"],
                "seed_index": args.seed_index,
                "model_seed": seed,
                "checkpoint_seed_eligible": checkpoint_eligible,
                "test_generated_or_accessed": False,
                "n1_gate_decided": False,
            },
        )
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "stage": "confirmatory_seed_training_validation_only_checkpoint_freeze",
                "seed_index": args.seed_index,
                "model_seed": seed,
                "test_generated_or_accessed": False,
                "n1_gate_decided": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
