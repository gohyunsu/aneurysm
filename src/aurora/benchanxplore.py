"""BenchAnXplore temporal-basis audit.

The D0 experiment is deliberately architecture-free.  It asks whether a
truncated, one-shot Fourier representation can preserve the released
80-timestep velocity cycle before GPU time is spent learning an operator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import shlex
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class BenchAnXploreError(RuntimeError):
    """Raised when the released asset violates the preregistered schema."""


@dataclass(frozen=True)
class CaseArrays:
    """One released geometry and its complete velocity cycle."""

    coordinates: Any
    tetrahedra: Any
    velocity: Any
    boundary_mask: Any


def _imports() -> tuple[Any, Any, Any]:
    try:
        import h5py
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - exercised in server container
        raise BenchAnXploreError(
            "D0 requires the experiment extras: numpy, torch, and h5py."
        ) from exc
    return h5py, np, torch


def discover_cases(data_root: str | Path) -> list[Path]:
    """Return a stable case list without depending on patient-derived IDs."""

    root = Path(data_root)
    cases = sorted(root.glob("AllFields_Resultats_MESH_*.h5"))
    if not cases:
        cases = sorted(root.rglob("AllFields_Resultats_MESH_*.h5"))
    return cases


def _numeric_data_keys(keys: Iterable[str]) -> dict[int, str]:
    result: dict[int, str] = {}
    for key in keys:
        if not key.startswith("data"):
            continue
        suffix = key[4:]
        if suffix.isdigit():
            result[int(suffix)] = key
    return result


def load_case(path: str | Path, expected_timesteps: int = 80) -> CaseArrays:
    """Load the compact HDF5 representation and enforce its field contract."""

    h5py, np, _ = _imports()
    source = Path(path)
    with h5py.File(source, "r") as handle:
        key_map = _numeric_data_keys(handle.keys())
        required = set(range(2 + 2 * expected_timesteps))
        missing = sorted(required - set(key_map))
        if missing:
            raise BenchAnXploreError(
                f"{source.name} is missing {len(missing)} expected datasets."
            )
        coordinates = np.asarray(handle[key_map[0]], dtype=np.float32)
        tetrahedra = np.asarray(handle[key_map[1]], dtype=np.int64)
        velocity = np.stack(
            [
                np.asarray(handle[key_map[2 + 2 * step]], dtype=np.float32)
                for step in range(expected_timesteps)
            ],
            axis=0,
        )
        masks = [
            np.asarray(handle[key_map[3 + 2 * step]], dtype=np.float32)
            for step in range(expected_timesteps)
        ]

    if coordinates.ndim != 2 or coordinates.shape[1] != 3:
        raise BenchAnXploreError(f"{source.name}: coordinates must have shape [N, 3].")
    if velocity.shape != (expected_timesteps, coordinates.shape[0], 3):
        raise BenchAnXploreError(
            f"{source.name}: velocity shape {velocity.shape} violates [T, N, 3]."
        )
    if tetrahedra.ndim != 2 or tetrahedra.shape[1] != 4:
        raise BenchAnXploreError(f"{source.name}: tetrahedra must have shape [E, 4].")
    if any(not np.array_equal(masks[0], mask) for mask in masks[1:]):
        raise BenchAnXploreError(f"{source.name}: boundary mask changes over time.")
    return CaseArrays(coordinates, tetrahedra, velocity, masks[0])


def fourier_reconstruct(signal: Any, modes: int) -> Any:
    """Project ``[T, ...]`` onto DC plus ``modes`` positive Fourier modes."""

    _, _, torch = _imports()
    if signal.ndim < 1:
        raise BenchAnXploreError("Signal needs a temporal dimension.")
    maximum = signal.shape[0] // 2
    if modes < 0 or modes > maximum:
        raise BenchAnXploreError(f"modes must be between 0 and {maximum}.")
    coefficients = torch.fft.rfft(signal, dim=0)
    truncated = torch.zeros_like(coefficients)
    truncated[: modes + 1] = coefficients[: modes + 1]
    return torch.fft.irfft(truncated, n=signal.shape[0], dim=0)


def _safe_ratio(numerator: Any, denominator: Any, epsilon: float = 1e-12) -> Any:
    return numerator / denominator.clamp_min(epsilon)


def region_masks(coordinates: Any) -> dict[str, Any]:
    """Use the public benchmark's y-plane anatomical partition."""

    _, _, torch = _imports()
    y = coordinates[:, 1]
    return {
        "full": torch.ones_like(y, dtype=torch.bool),
        "parent": y < 7.0,
        "neck": (y >= 7.0) & (y < 8.5),
        "bulge": y >= 8.5,
    }


def reconstruction_metrics(target: Any, prediction: Any, node_mask: Any) -> dict[str, float]:
    """Compute field, spectral, and cycle-functional preservation metrics."""

    _, _, torch = _imports()
    truth = target[:, node_mask, :]
    estimate = prediction[:, node_mask, :]
    if truth.numel() == 0:
        raise BenchAnXploreError("An anatomical region contains no mesh nodes.")

    error = estimate - truth
    squared_error = torch.sum(error.square())
    squared_truth = torch.sum(truth.square())
    rmse = torch.sqrt(torch.mean(error.square()))
    relative_l2 = torch.sqrt(_safe_ratio(squared_error, squared_truth))
    energy_retained = 1.0 - _safe_ratio(squared_error, squared_truth)

    true_speed = torch.linalg.vector_norm(truth, dim=-1)
    pred_speed = torch.linalg.vector_norm(estimate, dim=-1)
    true_mean = torch.mean(true_speed, dim=0)
    pred_mean = torch.mean(pred_speed, dim=0)
    true_peak = torch.max(true_speed, dim=0).values
    pred_peak = torch.max(pred_speed, dim=0).values
    mean_relative_mae = _safe_ratio(
        torch.sum(torch.abs(pred_mean - true_mean)), torch.sum(torch.abs(true_mean))
    )
    peak_relative_mae = _safe_ratio(
        torch.sum(torch.abs(pred_peak - true_peak)), torch.sum(torch.abs(true_peak))
    )
    return {
        "rmse_mm_s": float(rmse.item()),
        "relative_l2": float(relative_l2.item()),
        "energy_retained": float(energy_retained.item()),
        "cycle_mean_speed_relative_mae": float(mean_relative_mae.item()),
        "cycle_peak_speed_relative_mae": float(peak_relative_mae.item()),
    }


def _summarize(
    values: Sequence[float], *, rng: Any, bootstrap_replicates: int
) -> dict[str, float]:
    _, np, _ = _imports()
    array = np.asarray(values, dtype=np.float64)
    if array.size == 0:
        raise BenchAnXploreError("Cannot summarize an empty metric.")
    boot = np.empty(bootstrap_replicates, dtype=np.float64)
    for index in range(bootstrap_replicates):
        sample = rng.integers(0, array.size, size=array.size)
        boot[index] = float(np.mean(array[sample]))
    return {
        "mean": float(np.mean(array)),
        "std": float(np.std(array, ddof=1)) if array.size > 1 else 0.0,
        "median": float(np.median(array)),
        "ci95_low": float(np.quantile(boot, 0.025)),
        "ci95_high": float(np.quantile(boot, 0.975)),
    }


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "experiment_id",
        "dataset",
        "temporal_modes",
        "primary_mode",
        "bootstrap_replicates",
        "seed",
        "success_thresholds",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise BenchAnXploreError(f"Experiment config is missing: {missing}")
    return payload


def _gate(result: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    primary = str(config["primary_mode"])
    metrics = result["modes"][primary]
    thresholds = config["success_thresholds"]
    checks = {
        "full_relative_l2": (
            metrics["full"]["relative_l2"]["mean"]
            <= thresholds["full_relative_l2_max"]
        ),
        "full_energy_retained": (
            metrics["full"]["energy_retained"]["mean"]
            >= thresholds["full_energy_retained_min"]
        ),
        "full_cycle_mean_speed": (
            metrics["full"]["cycle_mean_speed_relative_mae"]["mean"]
            <= thresholds["full_cycle_mean_speed_relative_mae_max"]
        ),
        "full_cycle_peak_speed": (
            metrics["full"]["cycle_peak_speed_relative_mae"]["mean"]
            <= thresholds["full_cycle_peak_speed_relative_mae_max"]
        ),
        "bulge_relative_l2": (
            metrics["bulge"]["relative_l2"]["mean"]
            <= thresholds["bulge_relative_l2_max"]
        ),
    }
    return {"passed": all(checks.values()), "checks": checks}


def run_audit(
    *,
    data_root: str | Path,
    config: Mapping[str, Any],
    require_cuda: bool,
    git_commit: str,
) -> dict[str, Any]:
    """Run the preregistered D0 audit and return aggregate-only evidence."""

    h5py, np, torch = _imports()
    seed = int(config["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if require_cuda and not torch.cuda.is_available():
        raise BenchAnXploreError("CUDA was required but is unavailable.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cases = discover_cases(data_root)
    expected_cases = int(config["dataset"]["expected_cases"])
    if len(cases) != expected_cases:
        raise BenchAnXploreError(f"Expected {expected_cases} cases, found {len(cases)}.")

    modes = [int(value) for value in config["temporal_modes"]]
    regions = tuple(config["regions"].keys())
    metric_names = (
        "rmse_mm_s",
        "relative_l2",
        "energy_retained",
        "cycle_mean_speed_relative_mae",
        "cycle_peak_speed_relative_mae",
    )
    collected = {
        str(mode): {
            region: {metric: [] for metric in metric_names} for region in regions
        }
        for mode in modes
    }
    nodes: list[int] = []
    tetrahedra: list[int] = []
    boundary_fraction: list[float] = []
    endpoint_jump: list[float] = []

    with torch.inference_mode():
        for path in cases:
            case = load_case(path, expected_timesteps=int(config["dataset"]["timesteps"]))
            coordinates = torch.from_numpy(case.coordinates).to(device)
            velocity = torch.from_numpy(case.velocity).to(device)
            masks = region_masks(coordinates)
            nodes.append(int(case.coordinates.shape[0]))
            tetrahedra.append(int(case.tetrahedra.shape[0]))
            boundary_fraction.append(float(np.mean(case.boundary_mask)))
            endpoint_jump.append(
                float(
                    torch.sqrt(
                        _safe_ratio(
                            torch.sum((velocity[0] - velocity[-1]).square()),
                            torch.sum(velocity.square()) / velocity.shape[0],
                        )
                    ).item()
                )
            )
            for mode in modes:
                prediction = fourier_reconstruct(velocity, mode)
                for region in regions:
                    case_metrics = reconstruction_metrics(
                        velocity, prediction, masks[region]
                    )
                    for metric, value in case_metrics.items():
                        collected[str(mode)][region][metric].append(value)

    rng = np.random.default_rng(seed)
    replicates = int(config["bootstrap_replicates"])
    summarized = {
        mode: {
            region: {
                metric: _summarize(values, rng=rng, bootstrap_replicates=replicates)
                for metric, values in metrics.items()
            }
            for region, metrics in region_values.items()
        }
        for mode, region_values in collected.items()
    }
    result: dict[str, Any] = {
        "schema_version": "1.0",
        "experiment_id": config["experiment_id"],
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "interpretation_scope": (
            "Temporal representation audit only; not learned operator performance."
        ),
        "config_sha256": _canonical_hash(config),
        "git_commit": git_commit,
        "dataset": {
            "name": config["dataset"]["name"],
            "archive_sha256": config["dataset"]["archive_sha256"],
            "cases": len(cases),
            "timesteps": int(config["dataset"]["timesteps"]),
            "node_count": {
                "min": min(nodes),
                "median": float(np.median(nodes)),
                "max": max(nodes),
            },
            "tetrahedra_count": {
                "min": min(tetrahedra),
                "median": float(np.median(tetrahedra)),
                "max": max(tetrahedra),
            },
            "boundary_mask_fraction": _summarize(
                boundary_fraction, rng=rng, bootstrap_replicates=replicates
            ),
            "cycle_endpoint_jump_relative": _summarize(
                endpoint_jump, rng=rng, bootstrap_replicates=replicates
            ),
        },
        "runtime": {
            "device": str(device),
            "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "h5py": h5py.__version__,
            "python": platform.python_version(),
        },
        "modes": summarized,
    }
    result["gate"] = _gate(result, config)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", default=os.environ.get("AURORA_GIT_COMMIT", "unknown"))
    parser.add_argument("--require-cuda", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config = load_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output / "git_commit.txt").write_text(
        f"{args.git_commit}\n", encoding="utf-8"
    )
    (args.output / "dataset_manifest.sha256").write_text(
        f"{config['dataset']['archive_sha256']}  BenchAnXplore-release-archive\n",
        encoding="utf-8",
    )
    command = " ".join(shlex.quote(value) for value in sys.argv)
    (args.output / "command.txt").write_text(f"{command}\n", encoding="utf-8")
    try:
        result = run_audit(
            data_root=args.data_root,
            config=config,
            require_cuda=args.require_cuda,
            git_commit=args.git_commit,
        )
    except Exception as exc:
        failure = {
            "schema_version": "1.0",
            "experiment_id": config.get("experiment_id", "unknown"),
            "status": "failed",
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        (args.output / "status.json").write_text(
            json.dumps(failure, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        raise

    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (args.output / "metrics.json").write_text(serialized, encoding="utf-8")
    (args.output / "status.json").write_text(
        json.dumps(
            {
                "experiment_id": result["experiment_id"],
                "status": result["status"],
                "gate_passed": result["gate"]["passed"],
                "completed_at": result["completed_at"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output / "environment.json").write_text(
        json.dumps(result["runtime"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
