"""Post-result attribution diagnostic for the failed controlled-PDE G1 gate.

This module deliberately does not define a replacement gate.  It retrains the
frozen G1 models and asks two narrower questions:

1. How much of the raw two-sample projective distance is an unavoidable
   finite-sample floor?
2. How much conditional-mean error is attributable to sampling, the learned
   boundary-condition density, and the learned solution operator?

The controlled Poisson family is linear in its two boundary values.  This makes
the density-only counterfactual exact and keeps the diagnostic auditable.
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
    _environment,
    _field_samples,
    _flatten,
    _imports,
    _sample_gaussian,
    _sliced_distance,
    _summary,
    _true_boundary_distribution,
    _write_json,
    condition_gaussian,
    generate_split,
    load_config,
    poisson_solution,
    train_models,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_diagnostic_config(
    path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    """Load and verify the post-result diagnostic and its frozen G1 inputs."""

    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    required = {
        "experiment_id",
        "status",
        "base_experiment_id",
        "base_config",
        "base_config_sha256",
        "failed_result",
        "failed_result_sha256",
        "sample_counts",
        "attribution_geometries",
        "distance_replicates",
        "sliced_projections",
        "operator_sample_chunk",
        "nested_routes",
        "interpretation",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise ControlledPDEError(f"Diagnostic config is missing: {missing}")
    if payload["status"] != "post_result_exploratory_diagnostic":
        raise ControlledPDEError("G1b must remain explicitly post-result exploratory.")

    sample_counts = [int(item) for item in payload["sample_counts"]]
    if not sample_counts or sample_counts != sorted(set(sample_counts)):
        raise ControlledPDEError("sample_counts must be unique and increasing.")
    if sample_counts[0] != 128:
        raise ControlledPDEError("G1b must include the failed G1 sample count K=128.")
    if int(payload["distance_replicates"]) < 2:
        raise ControlledPDEError("At least two distance replicates are required.")
    if set(payload["nested_routes"]) != {"left_then_right", "right_then_left"}:
        raise ControlledPDEError("Both two-boundary nesting routes are required.")

    base_path = (source.parent / str(payload["base_config"])).resolve()
    result_path = (source.parent / str(payload["failed_result"])).resolve()
    if _sha256(base_path) != payload["base_config_sha256"]:
        raise ControlledPDEError("Frozen G1 config checksum does not match G1b.")
    if _sha256(result_path) != payload["failed_result_sha256"]:
        raise ControlledPDEError("Failed G1 public-result checksum does not match G1b.")

    base = load_config(base_path)
    failed = json.loads(result_path.read_text(encoding="utf-8"))
    if base["experiment_id"] != payload["base_experiment_id"]:
        raise ControlledPDEError("G1b base experiment id does not match the frozen config.")
    if failed.get("experiment_id") != payload["base_experiment_id"]:
        raise ControlledPDEError("G1b failed-result experiment id is inconsistent.")
    if failed.get("frozen_gate", {}).get("passed") is not False:
        raise ControlledPDEError("G1b is valid only after a recorded failed frozen gate.")
    if int(payload["attribution_geometries"]) > int(base["test_geometries"]):
        raise ControlledPDEError("Attribution subset exceeds the frozen test split.")
    return payload, base, base_path, result_path


def _generator(device: Any, seed: int) -> Any:
    _, torch = _imports()
    return torch.Generator(device=device).manual_seed(int(seed))


def _nested_gaussian_samples(
    mean: Any,
    covariance: Any,
    samples: int,
    generator: Any,
    *,
    first_index: int,
) -> Any:
    """Sample a bivariate Gaussian as marginal(first) then conditional(second)."""

    _, torch = _imports()
    if first_index not in (0, 1):
        raise ControlledPDEError("first_index must be 0 or 1.")
    second_index = 1 - first_index
    variance_first = covariance[:, first_index, first_index].clamp_min(1e-10)
    first = mean[:, first_index, None] + torch.sqrt(variance_first[:, None]) * torch.randn(
        mean.shape[0],
        samples,
        device=mean.device,
        generator=generator,
    )
    gain = covariance[:, second_index, first_index] / variance_first
    conditional_mean = mean[:, second_index, None] + gain[:, None] * (
        first - mean[:, first_index, None]
    )
    conditional_variance = (
        covariance[:, second_index, second_index]
        - covariance[:, second_index, first_index].square() / variance_first
    ).clamp_min(1e-10)
    second = conditional_mean + torch.sqrt(conditional_variance[:, None]) * torch.randn(
        first.shape,
        device=mean.device,
        generator=generator,
    )
    output = torch.empty(
        mean.shape[0], samples, 2, device=mean.device, dtype=mean.dtype
    )
    output[:, :, first_index] = first
    output[:, :, second_index] = second
    return output


def _nested_moment_residual(
    mean: Any, covariance: Any, *, first_index: int
) -> dict[str, float]:
    """Analytically verify that the nested Gaussian reconstructs the joint."""

    _, torch = _imports()
    second_index = 1 - first_index
    variance_first = covariance[:, first_index, first_index].clamp_min(1e-10)
    gain = covariance[:, second_index, first_index] / variance_first
    conditional_variance = (
        covariance[:, second_index, second_index]
        - covariance[:, second_index, first_index].square() / variance_first
    ).clamp_min(1e-10)
    reconstructed = torch.zeros_like(covariance)
    reconstructed[:, first_index, first_index] = variance_first
    reconstructed[:, second_index, first_index] = gain * variance_first
    reconstructed[:, first_index, second_index] = gain * variance_first
    reconstructed[:, second_index, second_index] = (
        conditional_variance + gain.square() * variance_first
    )
    return {
        "maximum_mean_absolute_residual": 0.0,
        "maximum_covariance_absolute_residual": float(
            torch.max(torch.abs(reconstructed - covariance)).item()
        ),
    }


def _standardized_mean_error(
    prediction: Any,
    oracle: Any,
    *,
    conditions_per_geometry: int,
) -> dict[str, float]:
    """Match the geometry-clustered normalization used by frozen G1."""

    _, torch = _imports()
    if prediction.shape != oracle.shape:
        raise ControlledPDEError("Prediction and oracle mean shapes must match.")
    if prediction.shape[0] % conditions_per_geometry:
        raise ControlledPDEError("Rows do not form complete geometry families.")
    geometries = prediction.shape[0] // conditions_per_geometry
    squared_error = (prediction - oracle).square().reshape(
        geometries, conditions_per_geometry, -1
    )
    squared_oracle = oracle.square().reshape(
        geometries, conditions_per_geometry, -1
    )
    per_geometry = torch.sqrt(torch.mean(squared_error, dim=(1, 2))) / torch.sqrt(
        torch.mean(squared_oracle, dim=(1, 2))
    ).clamp_min(1e-6)
    return {
        "mean": float(per_geometry.mean().item()),
        "maximum": float(per_geometry.max().item()),
    }


def _sampled_exact_mean(
    geometry: Any,
    mean: Any,
    covariance: Any,
    grid: Any,
    *,
    samples: int,
    chunk: int,
    generator: Any,
) -> Any:
    """Estimate the exact Poisson pushforward mean without retaining samples."""

    _, torch = _imports()
    total = torch.zeros(
        geometry.shape[0], grid.numel(), device=geometry.device, dtype=geometry.dtype
    )
    completed = 0
    while completed < samples:
        count = min(chunk, samples - completed)
        boundary = _sample_gaussian(mean, covariance, count, generator)
        field = poisson_solution(
            geometry[:, None, :], boundary, grid.view(1, 1, -1)
        )
        total += field.sum(dim=1)
        completed += count
    return total / float(samples)


def _sampled_operator_mean(
    operator: Any,
    geometry: Any,
    mean: Any,
    covariance: Any,
    *,
    samples: int,
    chunk: int,
    generator: Any,
) -> Any:
    """Estimate a learned-operator pushforward mean in bounded memory."""

    _, torch = _imports()
    total: Any | None = None
    completed = 0
    while completed < samples:
        count = min(chunk, samples - completed)
        boundary = _sample_gaussian(mean, covariance, count, generator)
        field = _field_samples(operator, geometry, boundary)
        if total is None:
            total = torch.zeros(
                geometry.shape[0],
                field.shape[-1],
                device=field.device,
                dtype=field.dtype,
            )
        total += field.sum(dim=1)
        completed += count
    if total is None:  # pragma: no cover - guarded by config
        raise ControlledPDEError("At least one operator sample is required.")
    return total / float(samples)


def _exact_field_samples(geometry: Any, boundary: Any, grid: Any) -> Any:
    return poisson_solution(
        geometry[:, None, :], boundary, grid.view(1, 1, -1)
    )


def _density_parameter_errors(
    learned_mean: Any,
    learned_covariance: Any,
    true_mean: Any,
    true_covariance: Any,
) -> dict[str, float]:
    _, torch = _imports()
    mean_numerator = torch.linalg.vector_norm(learned_mean - true_mean, dim=-1)
    mean_denominator = torch.linalg.vector_norm(true_mean, dim=-1).clamp_min(1e-6)
    covariance_numerator = torch.linalg.matrix_norm(
        learned_covariance - true_covariance, dim=(-2, -1)
    )
    covariance_denominator = torch.linalg.matrix_norm(
        true_covariance, dim=(-2, -1)
    ).clamp_min(1e-6)
    return {
        "relative_mean_l2": float((mean_numerator / mean_denominator).mean().item()),
        "relative_covariance_frobenius": float(
            (covariance_numerator / covariance_denominator).mean().item()
        ),
    }


def _route_index(route: str) -> int:
    if route == "left_then_right":
        return 0
    if route == "right_then_left":
        return 1
    raise ControlledPDEError(f"Unknown nested route: {route}")


def _projective_diagnostic(
    density: Any,
    operator: Any,
    geometry: Any,
    grid: Any,
    diagnostic: Mapping[str, Any],
    seed: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Estimate iid floors and direct-vs-nested distances along both routes."""

    _, torch = _imports()
    true_mean, true_covariance = _true_boundary_distribution(geometry)
    learned_mean, learned_covariance = density(geometry)
    structural: dict[str, Any] = {}
    for route in diagnostic["nested_routes"]:
        first_index = _route_index(route)
        structural[route] = {
            "oracle_density": _nested_moment_residual(
                true_mean, true_covariance, first_index=first_index
            ),
            "learned_density": _nested_moment_residual(
                learned_mean, learned_covariance, first_index=first_index
            ),
        }

    output: dict[str, Any] = {}
    projections = int(diagnostic["sliced_projections"])
    replicates = int(diagnostic["distance_replicates"])
    for sample_count in [int(item) for item in diagnostic["sample_counts"]]:
        count_result: dict[str, Any] = {}
        for route_offset, route in enumerate(diagnostic["nested_routes"]):
            first_index = _route_index(route)
            route_result = {
                "oracle_density_exact_operator": {
                    "iid_floor": [],
                    "direct_vs_nested": [],
                    "signed_excess_over_iid": [],
                    "clamped_excess_over_iid": [],
                },
                "learned_density_learned_operator": {
                    "iid_floor": [],
                    "direct_vs_nested": [],
                    "signed_excess_over_iid": [],
                    "clamped_excess_over_iid": [],
                },
            }
            for replicate in range(replicates):
                base_seed = (
                    int(seed) * 10_000
                    + sample_count * 31
                    + route_offset * 1_003
                    + replicate * 101
                )
                oracle_direct_a = _sample_gaussian(
                    true_mean,
                    true_covariance,
                    sample_count,
                    _generator(geometry.device, base_seed + 1),
                )
                oracle_direct_b = _sample_gaussian(
                    true_mean,
                    true_covariance,
                    sample_count,
                    _generator(geometry.device, base_seed + 2),
                )
                oracle_nested = _nested_gaussian_samples(
                    true_mean,
                    true_covariance,
                    sample_count,
                    _generator(geometry.device, base_seed + 3),
                    first_index=first_index,
                )
                oracle_field_a = _exact_field_samples(
                    geometry, oracle_direct_a, grid
                )
                oracle_field_b = _exact_field_samples(
                    geometry, oracle_direct_b, grid
                )
                oracle_field_nested = _exact_field_samples(
                    geometry, oracle_nested, grid
                )
                projection_seed = base_seed + 7
                iid = _sliced_distance(
                    oracle_field_a,
                    oracle_field_b,
                    seed=projection_seed,
                    projections=projections,
                )
                nested = _sliced_distance(
                    oracle_field_a,
                    oracle_field_nested,
                    seed=projection_seed,
                    projections=projections,
                )
                oracle_metrics = route_result["oracle_density_exact_operator"]
                oracle_metrics["iid_floor"].append(iid)
                oracle_metrics["direct_vs_nested"].append(nested)
                oracle_metrics["signed_excess_over_iid"].append(nested - iid)
                oracle_metrics["clamped_excess_over_iid"].append(max(nested - iid, 0.0))
                del oracle_field_a, oracle_field_b, oracle_field_nested

                learned_direct_a = _sample_gaussian(
                    learned_mean,
                    learned_covariance,
                    sample_count,
                    _generator(geometry.device, base_seed + 11),
                )
                learned_direct_b = _sample_gaussian(
                    learned_mean,
                    learned_covariance,
                    sample_count,
                    _generator(geometry.device, base_seed + 12),
                )
                learned_nested = _nested_gaussian_samples(
                    learned_mean,
                    learned_covariance,
                    sample_count,
                    _generator(geometry.device, base_seed + 13),
                    first_index=first_index,
                )
                learned_field_a = _field_samples(
                    operator, geometry, learned_direct_a
                )
                learned_field_b = _field_samples(
                    operator, geometry, learned_direct_b
                )
                learned_field_nested = _field_samples(
                    operator, geometry, learned_nested
                )
                learned_iid = _sliced_distance(
                    learned_field_a,
                    learned_field_b,
                    seed=projection_seed,
                    projections=projections,
                )
                learned_route = _sliced_distance(
                    learned_field_a,
                    learned_field_nested,
                    seed=projection_seed,
                    projections=projections,
                )
                learned_metrics = route_result["learned_density_learned_operator"]
                learned_metrics["iid_floor"].append(learned_iid)
                learned_metrics["direct_vs_nested"].append(learned_route)
                learned_metrics["signed_excess_over_iid"].append(
                    learned_route - learned_iid
                )
                learned_metrics["clamped_excess_over_iid"].append(
                    max(learned_route - learned_iid, 0.0)
                )
                del learned_field_a, learned_field_b, learned_field_nested
            count_result[route] = route_result
        output[str(sample_count)] = count_result
    return output, structural


def _attribution_diagnostic(
    density: Any,
    operator: Any,
    split: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    base: Mapping[str, Any],
    seed: int,
) -> dict[str, Any]:
    """Run the sampling/density/operator factorial conditional-mean analysis."""

    _, torch = _imports()
    geometries = int(diagnostic["attribution_geometries"])
    conditions = int(base["conditions_per_geometry"])
    family = {
        "geometry": split["geometry"][:geometries],
        "boundary": split["boundary"][:geometries],
        "field": split["field"][:geometries],
        "grid": split["grid"],
    }
    geometry, boundary, target = _flatten(family)
    true_mean, true_covariance = _true_boundary_distribution(geometry)
    learned_mean, learned_covariance = density(geometry)
    sample_counts = [int(item) for item in diagnostic["sample_counts"]]
    maximum_samples = max(sample_counts)
    chunk = int(diagnostic["operator_sample_chunk"])
    output: dict[str, Any] = {
        "density_parameters": _density_parameter_errors(
            learned_mean,
            learned_covariance,
            true_mean,
            true_covariance,
        )
    }

    full_prediction = operator(geometry, boundary)
    output["full_bc_deterministic_operator"] = _standardized_mean_error(
        full_prediction,
        target,
        conditions_per_geometry=conditions,
    )
    masks: dict[str, Any] = {}
    for mask_offset, name in enumerate(base["primary_masks"]):
        mask = base["observation_masks"][name]
        true_conditional_mean, true_conditional_covariance = condition_gaussian(
            true_mean, true_covariance, boundary, mask
        )
        learned_conditional_mean, learned_conditional_covariance = condition_gaussian(
            learned_mean, learned_covariance, boundary, mask
        )
        oracle_field_mean = poisson_solution(
            geometry, true_conditional_mean, family["grid"]
        )
        density_only_mean = poisson_solution(
            geometry, learned_conditional_mean, family["grid"]
        )
        mask_result: dict[str, Any] = {
            "density_only_exact_expectation": _standardized_mean_error(
                density_only_mean,
                oracle_field_mean,
                conditions_per_geometry=conditions,
            ),
            "sample_count_curve": {},
        }
        for sample_count in sample_counts:
            base_seed = (
                int(seed) * 100_000 + mask_offset * 10_000 + sample_count * 13
            )
            sampling_only_mean = _sampled_exact_mean(
                geometry,
                true_conditional_mean,
                true_conditional_covariance,
                family["grid"],
                samples=sample_count,
                chunk=chunk,
                generator=_generator(geometry.device, base_seed + 1),
            )
            density_plus_sampling_mean = _sampled_exact_mean(
                geometry,
                learned_conditional_mean,
                learned_conditional_covariance,
                family["grid"],
                samples=sample_count,
                chunk=chunk,
                generator=_generator(geometry.device, base_seed + 2),
            )
            end_to_end_mean = _sampled_operator_mean(
                operator,
                geometry,
                learned_conditional_mean,
                learned_conditional_covariance,
                samples=sample_count,
                chunk=chunk,
                generator=_generator(geometry.device, base_seed + 3),
            )
            curve = {
                "sampling_only_true_density_exact_operator": _standardized_mean_error(
                    sampling_only_mean,
                    oracle_field_mean,
                    conditions_per_geometry=conditions,
                ),
                "learned_density_exact_operator_with_sampling": _standardized_mean_error(
                    density_plus_sampling_mean,
                    oracle_field_mean,
                    conditions_per_geometry=conditions,
                ),
                "end_to_end_learned_density_learned_operator": _standardized_mean_error(
                    end_to_end_mean,
                    oracle_field_mean,
                    conditions_per_geometry=conditions,
                ),
            }
            if sample_count == maximum_samples:
                operator_only_mean = _sampled_operator_mean(
                    operator,
                    geometry,
                    true_conditional_mean,
                    true_conditional_covariance,
                    samples=sample_count,
                    chunk=chunk,
                    generator=_generator(geometry.device, base_seed + 4),
                )
                curve[
                    "operator_only_true_density_learned_operator"
                ] = _standardized_mean_error(
                    operator_only_mean,
                    oracle_field_mean,
                    conditions_per_geometry=conditions,
                )
            mask_result["sample_count_curve"][str(sample_count)] = curve
        masks[name] = mask_result
    output["masks"] = masks
    return output


def diagnose_seed(
    density: Any,
    operator: Any,
    split: Mapping[str, Any],
    diagnostic: Mapping[str, Any],
    base: Mapping[str, Any],
    seed: int,
) -> dict[str, Any]:
    """Evaluate one exact retraining seed."""

    density.eval()
    operator.eval()
    geometries = int(diagnostic["attribution_geometries"])
    with _imports()[1].inference_mode():
        projective, structural = _projective_diagnostic(
            density,
            operator,
            split["geometry"][:geometries],
            split["grid"],
            diagnostic,
            seed,
        )
        attribution = _attribution_diagnostic(
            density, operator, split, diagnostic, base, seed
        )
    return {
        "seed": seed,
        "projective_distance": projective,
        "analytic_nested_moment_residual": structural,
        "conditional_mean_attribution": attribution,
    }


def _aggregate_results(
    seed_results: Sequence[Mapping[str, Any]],
    diagnostic: Mapping[str, Any],
    base: Mapping[str, Any],
) -> dict[str, Any]:
    """Create compact cross-seed summaries for decision making."""

    maximum_samples = str(max(int(item) for item in diagnostic["sample_counts"]))
    attribution: dict[str, Any] = {}
    for mask in base["primary_masks"]:
        component_paths = {
            "sampling_only": (
                "sample_count_curve",
                maximum_samples,
                "sampling_only_true_density_exact_operator",
            ),
            "density_only": ("density_only_exact_expectation",),
            "operator_only": (
                "sample_count_curve",
                maximum_samples,
                "operator_only_true_density_learned_operator",
            ),
            "end_to_end": (
                "sample_count_curve",
                maximum_samples,
                "end_to_end_learned_density_learned_operator",
            ),
        }
        attribution[mask] = {}
        for component, path in component_paths.items():
            values = []
            for result in seed_results:
                node: Any = result["conditional_mean_attribution"]["masks"][mask]
                for key in path:
                    node = node[key]
                values.append(float(node["mean"]))
            attribution[mask][component] = _summary(values)

    sampling_curve: dict[str, Any] = {}
    for mask in base["primary_masks"]:
        sampling_curve[mask] = {}
        for sample_count in diagnostic["sample_counts"]:
            key = str(int(sample_count))
            sampling_curve[mask][key] = {}
            for component in (
                "sampling_only_true_density_exact_operator",
                "end_to_end_learned_density_learned_operator",
            ):
                values = [
                    float(
                        result["conditional_mean_attribution"]["masks"][mask][
                            "sample_count_curve"
                        ][key][component]["mean"]
                    )
                    for result in seed_results
                ]
                sampling_curve[mask][key][component] = _summary(values)

    projective: dict[str, Any] = {}
    for sample_count in diagnostic["sample_counts"]:
        key = str(int(sample_count))
        projective[key] = {}
        for route in diagnostic["nested_routes"]:
            projective[key][route] = {}
            for model in (
                "oracle_density_exact_operator",
                "learned_density_learned_operator",
            ):
                projective[key][route][model] = {}
                for metric in (
                    "iid_floor",
                    "direct_vs_nested",
                    "signed_excess_over_iid",
                    "clamped_excess_over_iid",
                ):
                    values = [
                        float(value)
                        for result in seed_results
                        for value in result["projective_distance"][key][route][model][
                            metric
                        ]
                    ]
                    projective[key][route][model][metric] = _summary(values)

    structural_maximum = 0.0
    for result in seed_results:
        for route in diagnostic["nested_routes"]:
            for density_name in ("oracle_density", "learned_density"):
                structural_maximum = max(
                    structural_maximum,
                    float(
                        result["analytic_nested_moment_residual"][route][density_name][
                            "maximum_covariance_absolute_residual"
                        ]
                    ),
                )
    return {
        "maximum_sample_count": int(maximum_samples),
        "conditional_mean_attribution": attribution,
        "sampling_curve": sampling_curve,
        "projective_distance": projective,
        "maximum_analytic_nested_moment_residual": structural_maximum,
    }


def run_diagnostic(
    diagnostic: Mapping[str, Any],
    base: Mapping[str, Any],
    require_cuda: bool,
) -> dict[str, Any]:
    """Retrain the frozen G1 setup and run post-result attribution."""

    _, torch = _imports()
    if require_cuda and not torch.cuda.is_available():
        raise ControlledPDEError("CUDA was required but is unavailable.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seed_results = []
    for seed in [int(item) for item in base["seeds"]]:
        random.seed(seed)
        torch.manual_seed(seed)
        train = generate_split(
            geometries=int(base["train_geometries"]),
            conditions=int(base["conditions_per_geometry"]),
            grid_points=int(base["grid_points"]),
            seed=seed,
            device=device,
        )
        test = generate_split(
            geometries=int(base["test_geometries"]),
            conditions=int(base["conditions_per_geometry"]),
            grid_points=int(base["grid_points"]),
            seed=seed + 10_000,
            device=device,
        )
        density, operator, direct, train_metrics = train_models(train, base, seed)
        del direct
        result = diagnose_seed(
            density, operator, test, diagnostic, base, seed
        )
        result["train"] = train_metrics
        seed_results.append(result)
        del density, operator, train, test
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return {
        "experiment_id": diagnostic["experiment_id"],
        "status": diagnostic["status"],
        "base_experiment_id": diagnostic["base_experiment_id"],
        "device": str(device),
        "seeds": seed_results,
        "aggregate_findings": _aggregate_results(seed_results, diagnostic, base),
        "frozen_gate_reopened": False,
        "interpretation": diagnostic["interpretation"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)
    diagnostic, base, base_path, result_path = load_diagnostic_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(item) for item in sys.argv) + "\n", encoding="utf-8"
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "diagnostic_config.sha256").write_text(
        _sha256(args.config) + "\n", encoding="utf-8"
    )
    (args.output / "base_config.sha256").write_text(
        _sha256(base_path) + "\n", encoding="utf-8"
    )
    (args.output / "failed_result.sha256").write_text(
        _sha256(result_path) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "run_config.json", diagnostic)
    try:
        result = run_diagnostic(diagnostic, base, args.require_cuda)
        _, torch = _imports()
        result.update(
            {
                "git_commit": args.git_commit,
                "started_at_utc": started,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "environment": _environment(torch),
                "runtime": {
                    "python": sys.version.split()[0],
                    "platform": platform.platform(),
                },
            }
        )
        _write_json(args.output / "metrics.json", result)
        _write_json(
            args.output / "status.json",
            {
                "state": "diagnostic_completed",
                "frozen_gate_reopened": False,
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
