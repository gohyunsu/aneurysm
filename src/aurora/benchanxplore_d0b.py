"""Equal-budget nonperiodic/train-only temporal audit after failed D0.

D0b compares two 17/25-dimensional temporal subspaces:

* a fixed nonperiodic DCT-II basis; and
* temporal POD fit only on the training geometries of each outer fold.

It is a post-result diagnostic and cannot relabel the frozen Fourier D0.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .benchanxplore import (
    BenchAnXploreError,
    _canonical_hash,
    _imports,
    _summarize,
    _torch_import,
    discover_cases,
    load_case,
    reconstruction_metrics,
    region_masks,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_d0b_config(
    path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    """Load D0b and verify that it is pinned to the failed frozen D0."""

    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    required = {
        "experiment_id",
        "status",
        "base_experiment_id",
        "failed_result",
        "failed_result_sha256",
        "dataset",
        "candidate_bases",
        "coefficient_budgets",
        "equal_budget_reference",
        "geometry_folds",
        "pod_covariance_weighting",
        "pod_centering",
        "regions",
        "bootstrap_replicates",
        "seed",
        "success_thresholds",
        "interpretation",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise BenchAnXploreError(f"D0b config is missing: {missing}")
    if payload["status"] != "post_result_exploratory_representation_diagnostic":
        raise BenchAnXploreError("D0b must remain explicitly post-result exploratory.")
    if payload["candidate_bases"] != ["dct_ii", "train_only_pod"]:
        raise BenchAnXploreError("D0b candidates are frozen to DCT-II and train-only POD.")
    if payload["coefficient_budgets"] != [17, 25]:
        raise BenchAnXploreError("D0b coefficient budgets are frozen at 17 and 25.")
    if payload["equal_budget_reference"] != {
        "17": "fixed_fourier_k8",
        "25": "fixed_fourier_k12",
    }:
        raise BenchAnXploreError("D0b equal-budget Fourier mapping is inconsistent.")
    if payload["pod_covariance_weighting"] != (
        "equal_geometry_after_scalar_signal_normalization"
    ):
        raise BenchAnXploreError("D0b POD geometry weighting cannot change post-result.")
    if payload["pod_centering"] != "none_rank_budget_includes_mean_component":
        raise BenchAnXploreError(
            "D0b POD must keep the mean inside the equal rank budget."
        )

    result_path = (source.parent / str(payload["failed_result"])).resolve()
    if _sha256(result_path) != payload["failed_result_sha256"]:
        raise BenchAnXploreError("D0b failed-result checksum does not match.")
    failed = json.loads(result_path.read_text(encoding="utf-8"))
    if failed.get("experiment_id") != payload["base_experiment_id"]:
        raise BenchAnXploreError("D0b base experiment does not match the failed result.")
    if failed.get("frozen_gate", {}).get("passed") is not False:
        raise BenchAnXploreError("D0b requires a recorded failed frozen D0.")
    return payload, failed, result_path


def dct_ii_basis(
    timesteps: int,
    rank: int,
    *,
    device: Any = None,
    dtype: Any = None,
) -> Any:
    """Return the first ``rank`` orthonormal DCT-II temporal vectors."""

    torch = _torch_import()
    if rank < 1 or rank > timesteps:
        raise BenchAnXploreError("DCT rank must lie in [1, timesteps].")
    if dtype is None:
        dtype = torch.float32
    time = torch.arange(timesteps, device=device, dtype=dtype)[:, None]
    frequency = torch.arange(rank, device=device, dtype=dtype)[None, :]
    basis = torch.cos(torch.pi * (time + 0.5) * frequency / float(timesteps))
    basis[:, 0] *= (1.0 / timesteps) ** 0.5
    if rank > 1:
        basis[:, 1:] *= (2.0 / timesteps) ** 0.5
    return basis


def temporal_covariance(signal: Any) -> Any:
    """Return a per-geometry temporal second moment with scalar-count normalization."""

    torch = _torch_import()
    if signal.ndim < 2:
        raise BenchAnXploreError("Temporal covariance needs [T, ...] data.")
    flattened = signal.reshape(signal.shape[0], -1)
    if flattened.shape[1] == 0:
        raise BenchAnXploreError("Temporal covariance received an empty field.")
    return torch.matmul(flattened, flattened.T) / float(flattened.shape[1])


def geometry_fold_assignment(cases: int, folds: int, seed: int) -> list[int]:
    """Create deterministic balanced geometry-disjoint fold assignments."""

    if folds < 2 or folds > cases:
        raise BenchAnXploreError("geometry_folds must lie in [2, cases].")
    indices = list(range(cases))
    generator = random.Random(seed)
    generator.shuffle(indices)
    assignment = [-1] * cases
    for position, case_index in enumerate(indices):
        assignment[case_index] = position % folds
    return assignment


def train_only_pod_basis(
    case_covariances: Any,
    train_indices: Sequence[int],
    rank: int,
    *,
    device: Any,
) -> Any:
    """Fit POD from explicitly supplied training geometries only."""

    torch = _torch_import()
    if not train_indices:
        raise BenchAnXploreError("POD requires at least one training geometry.")
    if rank < 1 or rank > case_covariances.shape[-1]:
        raise BenchAnXploreError("POD rank is outside the temporal dimension.")
    selected = case_covariances[list(train_indices)].to(device)
    covariance = selected.mean(dim=0)
    _, eigenvectors = torch.linalg.eigh(covariance)
    return torch.flip(eigenvectors[:, -rank:], dims=(1,))


def project_temporal(signal: Any, basis: Any) -> Any:
    """Orthogonally project a ``[T, ...]`` field onto a temporal basis."""

    if signal.shape[0] != basis.shape[0]:
        raise BenchAnXploreError("Signal and temporal basis lengths differ.")
    flattened = signal.reshape(signal.shape[0], -1)
    prediction = basis @ (basis.T @ flattened)
    return prediction.reshape_as(signal)


def _candidate_screen(
    metrics: Mapping[str, Any], thresholds: Mapping[str, float]
) -> dict[str, Any]:
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
    return {"meets_frozen_d0_thresholds": all(checks.values()), "checks": checks}


def run_d0b(
    *,
    data_root: str | Path,
    config: Mapping[str, Any],
    failed_result: Mapping[str, Any],
    require_cuda: bool,
    git_commit: str,
) -> dict[str, Any]:
    """Run the two-pass geometry-disjoint DCT/POD representation diagnostic."""

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
    timesteps = int(config["dataset"]["timesteps"])
    if len(cases) != expected_cases:
        raise BenchAnXploreError(f"Expected {expected_cases} cases, found {len(cases)}.")

    folds = int(config["geometry_folds"])
    assignment = geometry_fold_assignment(len(cases), folds, seed)
    fold_counts = [assignment.count(fold) for fold in range(folds)]
    budgets = [int(item) for item in config["coefficient_budgets"]]

    covariance_list = []
    with torch.inference_mode():
        for case_index, path in enumerate(cases, start=1):
            case = load_case(path, expected_timesteps=timesteps)
            velocity = torch.from_numpy(case.velocity).to(device)
            covariance_list.append(temporal_covariance(velocity).cpu())
            print(
                f"[D0b covariance] completed case {case_index}/{len(cases)}",
                flush=True,
            )
    case_covariances = torch.stack(covariance_list, dim=0)

    dct_bases = {
        budget: dct_ii_basis(
            timesteps,
            budget,
            device=device,
            dtype=torch.float32,
        )
        for budget in budgets
    }
    pod_bases: dict[int, dict[int, Any]] = {}
    for fold in range(folds):
        train_indices = [
            index for index, value in enumerate(assignment) if value != fold
        ]
        pod_bases[fold] = {
            budget: train_only_pod_basis(
                case_covariances,
                train_indices,
                budget,
                device=device,
            )
            for budget in budgets
        }

    metric_names = (
        "rmse_mm_s",
        "relative_l2",
        "energy_retained",
        "cycle_mean_speed_relative_mae",
        "cycle_peak_speed_relative_mae",
    )
    regions = tuple(config["regions"].keys())
    candidates = tuple(config["candidate_bases"])
    collected = {
        candidate: {
            str(budget): {
                region: {metric: [] for metric in metric_names}
                for region in regions
            }
            for budget in budgets
        }
        for candidate in candidates
    }

    with torch.inference_mode():
        for case_index, path in enumerate(cases):
            case = load_case(path, expected_timesteps=timesteps)
            coordinates = torch.from_numpy(case.coordinates).to(device)
            velocity = torch.from_numpy(case.velocity).to(device)
            masks = region_masks(coordinates)
            fold = assignment[case_index]
            basis_sets = {
                "dct_ii": dct_bases,
                "train_only_pod": pod_bases[fold],
            }
            for candidate in candidates:
                for budget in budgets:
                    prediction = project_temporal(
                        velocity, basis_sets[candidate][budget]
                    )
                    for region in regions:
                        metrics = reconstruction_metrics(
                            velocity, prediction, masks[region]
                        )
                        for metric, value in metrics.items():
                            collected[candidate][str(budget)][region][metric].append(
                                value
                            )
            print(
                f"[D0b evaluation] completed case {case_index + 1}/{len(cases)}",
                flush=True,
            )

    rng = np.random.default_rng(seed)
    replicates = int(config["bootstrap_replicates"])
    summarized = {
        candidate: {
            budget: {
                region: {
                    metric: _summarize(
                        values,
                        rng=rng,
                        bootstrap_replicates=replicates,
                    )
                    for metric, values in region_metrics.items()
                }
                for region, region_metrics in budget_metrics.items()
            }
            for budget, budget_metrics in candidate_metrics.items()
        }
        for candidate, candidate_metrics in collected.items()
    }
    screens = {
        candidate: {
            budget: _candidate_screen(
                metrics, config["success_thresholds"]
            )
            for budget, metrics in candidate_metrics.items()
        }
        for candidate, candidate_metrics in summarized.items()
    }
    eligible = [
        f"{candidate}_{budget}"
        for candidate, candidate_screens in screens.items()
        for budget, screen in candidate_screens.items()
        if screen["meets_frozen_d0_thresholds"]
    ]
    return {
        "schema_version": "1.0",
        "experiment_id": config["experiment_id"],
        "status": "completed",
        "protocol_status": config["status"],
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "config_sha256": _canonical_hash(config),
        "dataset": {
            "name": config["dataset"]["name"],
            "archive_sha256": config["dataset"]["archive_sha256"],
            "cases": len(cases),
            "timesteps": timesteps,
        },
        "geometry_split": {
            "folds": folds,
            "fold_case_counts": fold_counts,
            "pod_fit_scope": "training_geometries_only",
            "pod_centering": config["pod_centering"],
            "case_identifiers_published": False,
        },
        "failed_d0_reference": {
            "result_id": failed_result["result_id"],
            "frozen_gate_passed": False,
            "fourier_k8_full_relative_l2": failed_result["primary_metrics"][
                "full_relative_l2"
            ]["mean"],
            "fourier_k8_bulge_relative_l2": failed_result["primary_metrics"][
                "bulge_relative_l2"
            ]["mean"],
            "fourier_k12_bulge_relative_l2": failed_result[
                "secondary_mode_summary"
            ]["fourier_12"]["bulge_relative_l2"],
        },
        "representations": summarized,
        "candidate_screen": screens,
        "eligible_for_learned_compute_matched_test": eligible,
        "frozen_d0_relabeled": False,
        "runtime": {
            "device": str(device),
            "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "h5py": h5py.__version__,
            "python": platform.python_version(),
        },
        "interpretation": config["interpretation"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--git-commit",
        default=os.environ.get("AURORA_GIT_COMMIT", "unknown"),
    )
    parser.add_argument("--require-cuda", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    config, failed_result, result_path = load_d0b_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output / "git_commit.txt").write_text(
        f"{args.git_commit}\n", encoding="utf-8"
    )
    (args.output / "failed_result.sha256").write_text(
        _sha256(result_path) + "\n", encoding="utf-8"
    )
    (args.output / "dataset_manifest.sha256").write_text(
        f"{config['dataset']['archive_sha256']}  BenchAnXplore-release-archive\n",
        encoding="utf-8",
    )
    command = " ".join(shlex.quote(value) for value in sys.argv)
    (args.output / "command.txt").write_text(command + "\n", encoding="utf-8")
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "status.json").write_text(
        json.dumps(
            {
                "experiment_id": config["experiment_id"],
                "status": "running",
                "started_at": started,
                "frozen_d0_relabeled": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        result = run_d0b(
            data_root=args.data_root,
            config=config,
            failed_result=failed_result,
            require_cuda=args.require_cuda,
            git_commit=args.git_commit,
        )
    except Exception as exc:
        failure = {
            "schema_version": "1.0",
            "experiment_id": config["experiment_id"],
            "status": "failed",
            "started_at": started,
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "frozen_d0_relabeled": False,
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
                "eligible_candidates": result[
                    "eligible_for_learned_compute_matched_test"
                ],
                "frozen_d0_relabeled": False,
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
