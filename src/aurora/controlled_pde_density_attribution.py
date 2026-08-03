"""Post-G1r attribution of boundary-density error in the exact PDE family.

This diagnostic does not define a replacement gate. It compares direct
true-parameter supervision, analytic population cross-entropy, and empirical
NLL, then varies geometry coverage and repeated conditions. All evaluation is
on diagnostic-only synthetic seeds that do not overlap G1 or G1r.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .controlled_pde import (
    ControlledPDEError,
    _build_models,
    _flatten,
    _gaussian_nll,
    _summary,
    _true_boundary_distribution,
    condition_gaussian,
    generate_split,
    poisson_solution,
)
from .controlled_pde_diagnostic import _standardized_mean_error
from .controlled_pde_reentry import _fit_stage, _scheduler


def _imports() -> tuple[Any, Any]:
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - server runtime
        raise ControlledPDEError(
            "Density attribution requires numpy and torch."
        ) from exc
    return np, torch


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_keys(payload: Mapping[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(payload))
    if missing:
        raise ControlledPDEError(f"{label} is missing keys: {missing}")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate the immutable post-result attribution contract."""

    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        {
            "schema_version",
            "experiment_id",
            "status",
            "source_gate",
            "may_relabel_g1_or_g1r",
            "may_define_a_new_gate",
            "g1r_config",
            "g1r_config_sha256",
            "failed_g1r_result",
            "failed_g1r_result_sha256",
            "seeds",
            "split_seed_offsets",
            "grid_points",
            "hidden_dim",
            "reference_cell",
            "validation",
            "analysis",
            "training",
            "reference_objectives",
            "sample_scaling",
            "observation_masks",
            "primary_masks",
            "reporting",
            "interpretation",
        },
        "density-attribution config",
    )
    if payload["schema_version"] != "aurora.controlled_pde_density_attribution.v1":
        raise ControlledPDEError("Unexpected density-attribution schema.")
    if payload["status"] != "post_result_exploratory_density_attribution":
        raise ControlledPDEError("Density attribution must remain post-result.")
    if payload["source_gate"] != "G1r":
        raise ControlledPDEError("Density attribution must remain linked to G1r.")
    if payload["may_relabel_g1_or_g1r"] is not False:
        raise ControlledPDEError("Density attribution cannot relabel G1 or G1r.")
    if payload["may_define_a_new_gate"] is not False:
        raise ControlledPDEError("Density attribution cannot define a new gate.")
    if payload["reporting"].get("success_thresholds") is not None:
        raise ControlledPDEError("Post-result attribution cannot add thresholds.")

    g1r_path = (source.parent / payload["g1r_config"]).resolve()
    result_path = (source.parent / payload["failed_g1r_result"]).resolve()
    if _sha256(g1r_path) != payload["g1r_config_sha256"]:
        raise ControlledPDEError("Pinned G1r config checksum mismatch.")
    if _sha256(result_path) != payload["failed_g1r_result_sha256"]:
        raise ControlledPDEError("Pinned failed-G1r result checksum mismatch.")
    g1r = json.loads(g1r_path.read_text(encoding="utf-8"))
    failed = json.loads(result_path.read_text(encoding="utf-8"))
    if failed.get("gate", {}).get("passed") is not False:
        raise ControlledPDEError("Attribution requires a recorded failed G1r.")
    seeds = [int(value) for value in payload["seeds"]]
    if len(seeds) != 3 or len(set(seeds)) != 3:
        raise ControlledPDEError("Density attribution requires three unique seeds.")
    failed_g1_path = (g1r_path.parent / g1r["failed_g1_config"]).resolve()
    failed_g1 = json.loads(failed_g1_path.read_text(encoding="utf-8"))
    prior_seeds = {
        int(value) for value in [*failed_g1["seeds"], *g1r["seeds"]]
    }
    if set(seeds) & prior_seeds:
        raise ControlledPDEError(
            "Attribution seeds cannot reuse frozen G1 or G1r seeds."
        )
    offsets = payload["split_seed_offsets"]
    if set(offsets) != {"train", "validation", "analysis"}:
        raise ControlledPDEError("Train/validation/analysis offsets must be fixed.")
    if len({int(value) for value in offsets.values()}) != 3:
        raise ControlledPDEError("Split offsets must be distinct.")

    allowed_objectives = {
        "oracle_parameter",
        "analytic_population_nll",
        "empirical_nll",
    }
    objective_ids = set()
    for scenario in payload["reference_objectives"]:
        _require_keys(
            scenario,
            {"id", "train_objective", "validation_objective"},
            "reference objective",
        )
        objective_ids.add(str(scenario["id"]))
        if {
            scenario["train_objective"],
            scenario["validation_objective"],
        } - allowed_objectives:
            raise ControlledPDEError("Unknown density objective.")
    required_ids = {
        "oracle_parameter_regression",
        "analytic_population_nll",
        "empirical_nll_population_selected",
        "empirical_nll_sampled_selected",
    }
    if objective_ids != required_ids:
        raise ControlledPDEError("Reference attribution objectives changed.")

    scaling = payload["sample_scaling"]
    if scaling["scenario_id"] != "empirical_nll_population_selected":
        raise ControlledPDEError("Scaling must use the empirical density objective.")
    cells = scaling["cells"]
    cell_ids = [str(cell["id"]) for cell in cells]
    if len(cell_ids) != len(set(cell_ids)) or len(cells) != 7:
        raise ControlledPDEError("Sample scaling requires seven unique cells.")
    by_id = {str(cell["id"]): cell for cell in cells}
    for required in ("g192_c32", "g768_c8", "g3072_c2"):
        cell = by_id[required]
        budget = int(cell["train_geometries"]) * int(
            cell["conditions_per_geometry"]
        )
        if budget != 6144:
            raise ControlledPDEError("Matched-budget cells must contain 6144 samples.")
    reference = payload["reference_cell"]
    registered_reference = by_id.get(str(reference["id"]))
    if registered_reference is None or any(
        int(registered_reference[key]) != int(reference[key])
        for key in ("train_geometries", "conditions_per_geometry")
    ):
        raise ControlledPDEError("Reference scaling cell mismatch.")
    if set(payload["primary_masks"]) - set(payload["observation_masks"]):
        raise ControlledPDEError("All primary masks must be declared.")
    return payload


def _parameter_objective(
    predicted_mean: Any,
    predicted_covariance: Any,
    true_mean: Any,
    true_covariance: Any,
) -> Any:
    """Balanced supervision for mean, log standard deviation, and correlation."""

    _, torch = _imports()
    predicted_std = torch.sqrt(
        torch.diagonal(predicted_covariance, dim1=-2, dim2=-1).clamp_min(1e-12)
    )
    true_std = torch.sqrt(
        torch.diagonal(true_covariance, dim1=-2, dim2=-1).clamp_min(1e-12)
    )
    predicted_correlation = predicted_covariance[:, 0, 1] / (
        predicted_std[:, 0] * predicted_std[:, 1]
    ).clamp_min(1e-12)
    true_correlation = true_covariance[:, 0, 1] / (
        true_std[:, 0] * true_std[:, 1]
    ).clamp_min(1e-12)
    return (
        torch.mean((predicted_mean - true_mean).square())
        + torch.mean((torch.log(predicted_std) - torch.log(true_std)).square())
        + torch.mean((predicted_correlation - true_correlation).square())
    )


def _population_cross_entropy(
    predicted_mean: Any,
    predicted_covariance: Any,
    true_mean: Any,
    true_covariance: Any,
) -> Any:
    """Expected Gaussian NLL under the exact geometry-conditional law."""

    _, torch = _imports()
    eye = torch.eye(
        2, device=predicted_mean.device, dtype=predicted_mean.dtype
    ).expand(predicted_mean.shape[0], -1, -1)
    effective = predicted_covariance + 1e-5 * eye
    cholesky = torch.linalg.cholesky(effective)
    solved_covariance = torch.cholesky_solve(true_covariance, cholesky)
    trace = torch.diagonal(solved_covariance, dim1=-2, dim2=-1).sum(-1)
    difference = (true_mean - predicted_mean).unsqueeze(-1)
    solved_difference = torch.cholesky_solve(difference, cholesky)
    quadratic = torch.matmul(
        difference.transpose(-2, -1), solved_difference
    ).flatten()
    logdet = 2.0 * torch.log(
        torch.diagonal(cholesky, dim1=-2, dim2=-1)
    ).sum(-1)
    return 0.5 * (trace + quadratic + logdet + 2.0 * math.log(2.0 * math.pi))


def _objective(
    density: Any,
    split: Mapping[str, Any],
    objective: str,
) -> Any:
    if objective == "empirical_nll":
        geometry, boundary, _ = _flatten(split)
        mean, covariance = density(geometry)
        return _gaussian_nll(boundary, mean, covariance).mean()
    geometry = split["geometry"]
    predicted_mean, predicted_covariance = density(geometry)
    true_mean, true_covariance = _true_boundary_distribution(geometry)
    if objective == "analytic_population_nll":
        return _population_cross_entropy(
            predicted_mean,
            predicted_covariance,
            true_mean,
            true_covariance,
        ).mean()
    if objective == "oracle_parameter":
        return _parameter_objective(
            predicted_mean,
            predicted_covariance,
            true_mean,
            true_covariance,
        )
    raise ControlledPDEError(f"Unknown density objective: {objective}")


def _fit_density(
    train: Mapping[str, Any],
    validation: Mapping[str, Any],
    config: Mapping[str, Any],
    scenario: Mapping[str, Any],
    seed: int,
) -> tuple[Any, dict[str, Any]]:
    _, torch = _imports()
    torch.manual_seed(int(seed))
    device = train["geometry"].device
    density, _, _ = _build_models(
        int(config["grid_points"]), int(config["hidden_dim"]), device
    )
    contract = config["training"]
    optimizer = torch.optim.AdamW(
        density.parameters(),
        lr=float(contract["learning_rate"]),
        weight_decay=float(contract["weight_decay"]),
    )
    scheduler = _scheduler(optimizer, contract)
    history = _fit_stage(
        module=density,
        optimizer=optimizer,
        scheduler=scheduler,
        contract=contract,
        train_step=lambda _: _objective(
            density, train, str(scenario["train_objective"])
        ),
        validation_step=lambda: _objective(
            density, validation, str(scenario["validation_objective"])
        ),
    )
    return density, {
        "best_epoch": history["best_epoch"],
        "best_validation_loss": history["best_validation_loss"],
        "epochs_executed": history["epochs_executed"],
    }


def _parameter_metrics(
    predicted_mean: Any,
    predicted_covariance: Any,
    true_mean: Any,
    true_covariance: Any,
) -> dict[str, float]:
    _, torch = _imports()
    mean_rmse = torch.sqrt(torch.mean((predicted_mean - true_mean).square()))
    mean_scale = torch.sqrt(torch.mean(true_mean.square())).clamp_min(1e-12)
    covariance_error = torch.linalg.matrix_norm(
        predicted_covariance - true_covariance, dim=(-2, -1)
    )
    covariance_scale = torch.linalg.matrix_norm(
        true_covariance, dim=(-2, -1)
    ).clamp_min(1e-12)
    predicted_std = torch.sqrt(
        torch.diagonal(predicted_covariance, dim1=-2, dim2=-1).clamp_min(1e-12)
    )
    true_std = torch.sqrt(
        torch.diagonal(true_covariance, dim1=-2, dim2=-1).clamp_min(1e-12)
    )
    predicted_correlation = predicted_covariance[:, 0, 1] / (
        predicted_std[:, 0] * predicted_std[:, 1]
    ).clamp_min(1e-12)
    true_correlation = true_covariance[:, 0, 1] / (
        true_std[:, 0] * true_std[:, 1]
    ).clamp_min(1e-12)
    return {
        "mean_normalized_rmse": float((mean_rmse / mean_scale).item()),
        "covariance_normalized_frobenius": float(
            torch.mean(covariance_error / covariance_scale).item()
        ),
        "correlation_mae": float(
            torch.mean(torch.abs(predicted_correlation - true_correlation)).item()
        ),
    }


def _evaluate_density(
    density: Any,
    analysis: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    _, torch = _imports()
    density.eval()
    unique_geometry = analysis["geometry"]
    with torch.inference_mode():
        predicted_mean, predicted_covariance = density(unique_geometry)
        true_mean, true_covariance = _true_boundary_distribution(unique_geometry)
        parameter_metrics = _parameter_metrics(
            predicted_mean, predicted_covariance, true_mean, true_covariance
        )
        predicted_cross_entropy = _population_cross_entropy(
            predicted_mean,
            predicted_covariance,
            true_mean,
            true_covariance,
        )
        oracle_cross_entropy = _population_cross_entropy(
            true_mean,
            true_covariance,
            true_mean,
            true_covariance,
        )
        excess_nll = float(
            torch.mean(predicted_cross_entropy - oracle_cross_entropy).item()
        )

        geometry, boundary, _ = _flatten(analysis)
        learned_mean, learned_covariance = density(geometry)
        exact_mean, exact_covariance = _true_boundary_distribution(geometry)
        mask_results: dict[str, Any] = {}
        for name in config["primary_masks"]:
            mask = config["observation_masks"][name]
            learned_conditional_mean, _ = condition_gaussian(
                learned_mean, learned_covariance, boundary, mask
            )
            exact_conditional_mean, _ = condition_gaussian(
                exact_mean, exact_covariance, boundary, mask
            )
            predicted_field = poisson_solution(
                geometry, learned_conditional_mean, analysis["grid"]
            )
            exact_field = poisson_solution(
                geometry, exact_conditional_mean, analysis["grid"]
            )
            mask_results[name] = _standardized_mean_error(
                predicted_field,
                exact_field,
                conditions_per_geometry=int(
                    config["analysis"]["conditions_per_geometry"]
                ),
            )
    worst = max(float(result["mean"]) for result in mask_results.values())
    return {
        **parameter_metrics,
        "analytic_population_excess_nll": excess_nll,
        "conditional_mean_error_by_mask": mask_results,
        "maximum_density_only_standardized_mean_error": worst,
    }


def _tasks(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    reference = config["reference_cell"]
    tasks = [
        {
            "task_type": "reference_objective",
            "cell": dict(reference),
            "scenario": dict(scenario),
        }
        for scenario in config["reference_objectives"]
    ]
    scaling = config["sample_scaling"]
    for cell in scaling["cells"]:
        if str(cell["id"]) == str(reference["id"]):
            continue
        tasks.append(
            {
                "task_type": "sample_scaling",
                "cell": dict(cell),
                "scenario": {
                    "id": scaling["scenario_id"],
                    "train_objective": scaling["train_objective"],
                    "validation_objective": scaling["validation_objective"],
                },
            }
        )
    return tasks


def _aggregate_records(
    records: Sequence[Mapping[str, Any]], config: Mapping[str, Any]
) -> dict[str, Any]:
    metric_keys = (
        "mean_normalized_rmse",
        "covariance_normalized_frobenius",
        "correlation_mae",
        "analytic_population_excess_nll",
        "maximum_density_only_standardized_mean_error",
    )

    def metrics_for(selected: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        return {
            key: _summary(
                [float(record["analysis_metrics"][key]) for record in selected]
            )
            for key in metric_keys
        }

    reference: dict[str, Any] = {}
    reference_id = str(config["reference_cell"]["id"])
    for scenario in config["reference_objectives"]:
        selected = [
            record
            for record in records
            if str(record["cell"]["id"]) == reference_id
            and str(record["scenario"]["id"]) == str(scenario["id"])
        ]
        reference[str(scenario["id"])] = metrics_for(selected)

    scaling: dict[str, Any] = {}
    scaling_scenario = str(config["sample_scaling"]["scenario_id"])
    for cell in config["sample_scaling"]["cells"]:
        selected = [
            record
            for record in records
            if str(record["cell"]["id"]) == str(cell["id"])
            and str(record["scenario"]["id"]) == scaling_scenario
        ]
        scaling[str(cell["id"])] = {
            "train_geometries": int(cell["train_geometries"]),
            "conditions_per_geometry": int(cell["conditions_per_geometry"]),
            "boundary_samples": int(cell["train_geometries"])
            * int(cell["conditions_per_geometry"]),
            "axes": list(cell["axes"]),
            "metrics": metrics_for(selected),
        }
    return {
        "reference_objectives": reference,
        "sample_scaling": scaling,
        "new_gate_defined": False,
        "g1_or_g1r_relabeled": False,
    }


def run_experiment(config: Mapping[str, Any], require_cuda: bool) -> dict[str, Any]:
    """Run paired attribution tasks on diagnostic-only synthetic splits."""

    _, torch = _imports()
    if require_cuda and not torch.cuda.is_available():
        raise ControlledPDEError("CUDA was required but is unavailable.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    offsets = config["split_seed_offsets"]
    records: list[dict[str, Any]] = []
    tasks = _tasks(config)
    for seed in [int(value) for value in config["seeds"]]:
        random.seed(seed)
        torch.manual_seed(seed)
        validation = generate_split(
            geometries=int(config["validation"]["geometries"]),
            conditions=int(config["validation"]["conditions_per_geometry"]),
            grid_points=int(config["grid_points"]),
            seed=seed + int(offsets["validation"]),
            device=device,
        )
        analysis = generate_split(
            geometries=int(config["analysis"]["geometries"]),
            conditions=int(config["analysis"]["conditions_per_geometry"]),
            grid_points=int(config["grid_points"]),
            seed=seed + int(offsets["analysis"]),
            device=device,
        )
        for task in tasks:
            cell = task["cell"]
            scenario = task["scenario"]
            train = generate_split(
                geometries=int(cell["train_geometries"]),
                conditions=int(cell["conditions_per_geometry"]),
                grid_points=int(config["grid_points"]),
                seed=seed + int(offsets["train"]),
                device=device,
            )
            density, history = _fit_density(
                train, validation, config, scenario, seed
            )
            records.append(
                {
                    "seed": seed,
                    "task_type": task["task_type"],
                    "cell": cell,
                    "scenario": scenario,
                    "training": history,
                    "analysis_metrics": _evaluate_density(
                        density, analysis, config
                    ),
                }
            )
            del train, density
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        del validation, analysis
    return {
        "experiment_id": config["experiment_id"],
        "status": config["status"],
        "source_gate": config["source_gate"],
        "device": str(device),
        "failed_g1_relabeled": False,
        "failed_g1r_relabeled": False,
        "new_gate_defined": False,
        "records": records,
        "aggregate": _aggregate_records(records, config),
        "interpretation": config["interpretation"],
    }


def _environment(torch: Any) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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
        " ".join(shlex.quote(item) for item in sys.argv) + "\n",
        encoding="utf-8",
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
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
                "failed_g1_relabeled": False,
                "failed_g1r_relabeled": False,
                "new_gate_defined": False,
            },
        )
        return 0
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "error_type": type(exc).__name__,
                "message": str(exc),
                "started_at_utc": started,
                "failed_at_utc": datetime.now(timezone.utc).isoformat(),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
