"""Development-only density-estimator comparison after the negative G1r gate.

The experiment compares record-wise Gaussian NLL with geometry-grouped moment
targets at equal architecture and optimizer budget.  It may select one
estimator for a future, independently frozen exact-data gate, but it cannot
itself pass a gate or authorize nonlinear/3D experiments.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
    generate_split,
)
from .controlled_pde_density_attribution import (
    _evaluate_density,
    _imports,
)
from .controlled_pde_reentry import _fit_stage, _scheduler


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_keys(payload: Mapping[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(payload))
    if missing:
        raise ControlledPDEError(f"{label} is missing keys: {missing}")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate the development-only estimator contract."""

    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        {
            "schema_version",
            "experiment_id",
            "status",
            "source_diagnostic",
            "source_config",
            "source_config_sha256",
            "source_result",
            "source_result_sha256",
            "may_relabel_g1_or_g1r",
            "may_define_or_pass_a_gate",
            "may_authorize_nonlinear_or_3d_training",
            "seeds",
            "split_seed_offsets",
            "grid_points",
            "hidden_dim",
            "validation",
            "analysis",
            "training",
            "cells",
            "estimators",
            "grouped_objective",
            "observation_masks",
            "primary_masks",
            "selection_rule",
            "reporting",
            "interpretation",
        },
        "density-development config",
    )
    if payload["schema_version"] != "aurora.controlled_pde_density_development.v1":
        raise ControlledPDEError("Unexpected density-development schema.")
    if payload["status"] != "development_only_estimator_selection":
        raise ControlledPDEError("DA2 must remain development-only.")
    if payload["source_diagnostic"] != "DA1":
        raise ControlledPDEError("DA2 must remain linked to DA1.")
    for key in (
        "may_relabel_g1_or_g1r",
        "may_define_or_pass_a_gate",
        "may_authorize_nonlinear_or_3d_training",
    ):
        if payload[key] is not False:
            raise ControlledPDEError(f"DA2 safety flag {key} must remain false.")
    if payload["reporting"].get("success_thresholds") is not None:
        raise ControlledPDEError("Development-only DA2 cannot define thresholds.")

    source_config = (source.parent / payload["source_config"]).resolve()
    source_result = (source.parent / payload["source_result"]).resolve()
    if _sha256(source_config) != payload["source_config_sha256"]:
        raise ControlledPDEError("Pinned DA1 config checksum mismatch.")
    if _sha256(source_result) != payload["source_result_sha256"]:
        raise ControlledPDEError("Pinned DA1 result checksum mismatch.")
    da1 = json.loads(source_config.read_text(encoding="utf-8"))
    prior_config = json.loads(
        (source.parent / da1["g1r_config"]).resolve().read_text(encoding="utf-8")
    )
    failed_g1 = json.loads(
        (source.parent / prior_config["failed_g1_config"])
        .resolve()
        .read_text(encoding="utf-8")
    )
    prior_seeds = {
        int(value)
        for value in [
            *failed_g1["seeds"],
            *prior_config["seeds"],
            *da1["seeds"],
        ]
    }
    seeds = [int(value) for value in payload["seeds"]]
    if len(seeds) != 3 or len(set(seeds)) != 3:
        raise ControlledPDEError("DA2 requires three unique development seeds.")
    if set(seeds) & prior_seeds:
        raise ControlledPDEError("DA2 cannot reuse G1, G1r, or DA1 seeds.")

    offsets = payload["split_seed_offsets"]
    if set(offsets) != {"train", "validation", "analysis"}:
        raise ControlledPDEError("DA2 split offsets changed.")
    if len({int(value) for value in offsets.values()}) != 3:
        raise ControlledPDEError("DA2 split offsets must be distinct.")

    cells = payload["cells"]
    cell_ids = {str(cell["id"]) for cell in cells}
    if cell_ids != {"g768_c8", "g3072_c8"}:
        raise ControlledPDEError("DA2 data cells changed.")
    estimator_ids = {str(item["id"]) for item in payload["estimators"]}
    if estimator_ids != {
        "empirical_nll",
        "grouped_unbiased",
        "grouped_shrinkage_025",
        "grouped_shrinkage_050",
    }:
        raise ControlledPDEError("DA2 estimator comparison changed.")
    allowed_objectives = {"empirical_nll", "grouped_moments"}
    for estimator in payload["estimators"]:
        if estimator["train_objective"] not in allowed_objectives:
            raise ControlledPDEError("Unknown DA2 training objective.")
        if estimator["validation_objective"] != "empirical_nll":
            raise ControlledPDEError(
                "All DA2 checkpoints must use sampled validation NLL."
            )
        shrinkage = estimator["covariance_shrinkage"]
        if estimator["train_objective"] == "empirical_nll":
            if shrinkage is not None:
                raise ControlledPDEError("Empirical NLL cannot use target shrinkage.")
        elif not 0.0 <= float(shrinkage) <= 1.0:
            raise ControlledPDEError("Grouped covariance shrinkage must be in [0,1].")
    if payload["selection_rule"]["cell_id"] != "g768_c8":
        raise ControlledPDEError(
            "DA2 estimator selection must use the original G1r data budget."
        )
    if set(payload["primary_masks"]) - set(payload["observation_masks"]):
        raise ControlledPDEError("Every DA2 primary mask must be declared.")
    return payload


def _group_moments(boundary: Any, shrinkage: float) -> tuple[Any, Any]:
    """Return sample means and shrunk unbiased within-geometry covariances.

    The unbiased covariance equals the average pairwise-difference
    U-statistic: E[0.5 (B_i-B_j)(B_i-B_j)^T].
    """

    _, torch = _imports()
    conditions = int(boundary.shape[1])
    if conditions < 2:
        raise ControlledPDEError("Grouped covariance needs at least two conditions.")
    sample_mean = boundary.mean(dim=1)
    centered = boundary - sample_mean[:, None, :]
    covariance = torch.einsum("gci,gcj->gij", centered, centered) / (
        conditions - 1
    )
    pooled = covariance.mean(dim=0, keepdim=True).expand_as(covariance)
    target = (1.0 - float(shrinkage)) * covariance + float(shrinkage) * pooled
    eye = torch.eye(2, device=boundary.device, dtype=boundary.dtype)
    return sample_mean, target + 1e-6 * eye


def _grouped_moment_loss(
    density: Any,
    split: Mapping[str, Any],
    shrinkage: float,
    covariance_weight: float,
) -> Any:
    """Fit mean and covariance to separate geometry-level sufficient moments."""

    _, torch = _imports()
    geometry = split["geometry"]
    boundary = split["boundary"]
    predicted_mean, predicted_covariance = density(geometry)
    target_mean, target_covariance = _group_moments(boundary, shrinkage)

    pooled_variance = boundary.reshape(-1, 2).var(dim=0, unbiased=True).clamp_min(
        1e-6
    )
    mean_loss = torch.mean(
        (predicted_mean - target_mean).square() / pooled_variance
    )
    predicted_std = torch.sqrt(
        torch.diagonal(predicted_covariance, dim1=-2, dim2=-1).clamp_min(1e-8)
    )
    target_std = torch.sqrt(
        torch.diagonal(target_covariance, dim1=-2, dim2=-1).clamp_min(1e-8)
    )
    predicted_correlation = predicted_covariance[:, 0, 1] / (
        predicted_std[:, 0] * predicted_std[:, 1]
    ).clamp_min(1e-8)
    target_correlation = target_covariance[:, 0, 1] / (
        target_std[:, 0] * target_std[:, 1]
    ).clamp_min(1e-8)
    covariance_loss = torch.mean(
        (torch.log(predicted_std) - torch.log(target_std)).square()
    ) + torch.mean((predicted_correlation - target_correlation).square())
    return mean_loss + float(covariance_weight) * covariance_loss


def _objective(
    density: Any,
    split: Mapping[str, Any],
    estimator: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    validation: bool,
) -> Any:
    objective = (
        estimator["validation_objective"]
        if validation
        else estimator["train_objective"]
    )
    if objective == "empirical_nll":
        geometry, boundary, _ = _flatten(split)
        mean, covariance = density(geometry)
        return _gaussian_nll(boundary, mean, covariance).mean()
    if objective == "grouped_moments":
        return _grouped_moment_loss(
            density,
            split,
            float(estimator["covariance_shrinkage"]),
            float(config["grouped_objective"]["covariance_loss_weight"]),
        )
    raise ControlledPDEError(f"Unknown DA2 objective: {objective}")


def _fit_density(
    train: Mapping[str, Any],
    validation: Mapping[str, Any],
    config: Mapping[str, Any],
    estimator: Mapping[str, Any],
    seed: int,
) -> tuple[Any, dict[str, Any]]:
    _, torch = _imports()
    torch.manual_seed(int(seed))
    density, _, _ = _build_models(
        int(config["grid_points"]),
        int(config["hidden_dim"]),
        train["geometry"].device,
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
            density, train, estimator, config, validation=False
        ),
        validation_step=lambda: _objective(
            density, validation, estimator, config, validation=True
        ),
    )
    return density, {
        "best_epoch": history["best_epoch"],
        "best_validation_loss": history["best_validation_loss"],
        "epochs_executed": history["epochs_executed"],
    }


def _tasks(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"cell": dict(cell), "estimator": dict(estimator)}
        for cell in config["cells"]
        for estimator in config["estimators"]
    ]


def _aggregate(
    records: Sequence[Mapping[str, Any]], config: Mapping[str, Any]
) -> dict[str, Any]:
    metric_keys = (
        "mean_normalized_rmse",
        "covariance_normalized_frobenius",
        "correlation_mae",
        "analytic_population_excess_nll",
        "maximum_density_only_standardized_mean_error",
    )
    by_cell: dict[str, Any] = {}
    for cell in config["cells"]:
        cell_id = str(cell["id"])
        by_estimator: dict[str, Any] = {}
        for estimator in config["estimators"]:
            estimator_id = str(estimator["id"])
            selected = [
                record
                for record in records
                if record["cell"]["id"] == cell_id
                and record["estimator"]["id"] == estimator_id
            ]
            by_estimator[estimator_id] = {
                key: _summary(
                    [
                        float(record["analysis_metrics"][key])
                        for record in selected
                    ]
                )
                for key in metric_keys
            }
        by_cell[cell_id] = by_estimator

    rule = config["selection_rule"]
    cell_metrics = by_cell[str(rule["cell_id"])]
    primary = str(rule["primary_metric"])
    tie_breaker = str(rule["tie_breaker"])
    ordered = sorted(
        cell_metrics,
        key=lambda estimator_id: (
            float(cell_metrics[estimator_id][primary]["mean"]),
            float(cell_metrics[estimator_id][tie_breaker]["mean"]),
            estimator_id,
        ),
    )
    return {
        "by_cell": by_cell,
        "development_selection": {
            "estimator_id": ordered[0],
            "rule": dict(rule),
            "descriptive_only": True,
            "fresh_gate_required": True,
        },
        "gate_passed": False,
        "g1_or_g1r_relabeled": False,
        "nonlinear_or_3d_training_authorized": False,
    }


def run_experiment(config: Mapping[str, Any], require_cuda: bool) -> dict[str, Any]:
    """Run estimator comparisons on development-only synthetic seeds."""

    _, torch = _imports()
    if require_cuda and not torch.cuda.is_available():
        raise ControlledPDEError("CUDA was required but is unavailable.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    offsets = config["split_seed_offsets"]
    records: list[dict[str, Any]] = []
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
        for task in _tasks(config):
            cell = task["cell"]
            estimator = task["estimator"]
            train = generate_split(
                geometries=int(cell["train_geometries"]),
                conditions=int(cell["conditions_per_geometry"]),
                grid_points=int(config["grid_points"]),
                seed=seed + int(offsets["train"]),
                device=device,
            )
            density, history = _fit_density(
                train, validation, config, estimator, seed
            )
            records.append(
                {
                    "seed": seed,
                    "cell": cell,
                    "estimator": estimator,
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
        "source_diagnostic": config["source_diagnostic"],
        "device": str(device),
        "failed_g1_relabeled": False,
        "failed_g1r_relabeled": False,
        "new_gate_defined_or_passed": False,
        "nonlinear_or_3d_training_authorized": False,
        "records": records,
        "aggregate": _aggregate(records, config),
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
                "experiment_id": config["experiment_id"],
                "git_commit": args.git_commit,
                "started_at_utc": started,
                "completed_at_utc": result["completed_at_utc"],
            },
        )
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "experiment_id": config["experiment_id"],
                "git_commit": args.git_commit,
                "started_at_utc": started,
                "failed_at_utc": datetime.now(timezone.utc).isoformat(),
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
