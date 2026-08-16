#!/usr/bin/env python3
"""Run a deterministic CPU-only synthetic cycle-moment projection benchmark."""

from __future__ import annotations

import argparse
import json
import platform
import resource
import time

import torch

from aurora.cycle_moment_projection import (
    jensen_cone_mean_magnitude,
    project_cycle_moments,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phases", type=int, default=80)
    parser.add_argument("--nodes", type=int, default=13_902)
    parser.add_argument("--iterations", type=int, default=24)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--backward", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if min(args.phases, args.nodes, args.iterations, args.threads) <= 0:
        raise SystemExit("all numeric arguments must be positive")
    if args.iterations < 8:
        raise SystemExit("iterations must be at least 8")

    torch.set_num_threads(args.threads)
    dtype = torch.float32
    phase = torch.arange(args.phases, dtype=dtype) * (2.0 * torch.pi / args.phases)
    raw = torch.zeros((args.phases, args.nodes, 3), dtype=dtype)
    raw[:, :, 0] = torch.sin(phase).unsqueeze(1)
    raw[:, :, 1] = 0.3 * torch.cos(phase).unsqueeze(1)
    mean = torch.zeros((args.nodes, 3), dtype=dtype)
    mean[:, 0] = 0.7
    cone_coordinate = torch.full((args.nodes,), -0.2, dtype=dtype)
    normals = torch.zeros((args.nodes, 3), dtype=dtype)
    normals[:, 2] = 1.0

    if args.backward:
        raw.requires_grad_(True)
        mean.requires_grad_(True)
        cone_coordinate.requires_grad_(True)

    target = jensen_cone_mean_magnitude(mean, cone_coordinate, torch)
    started = time.perf_counter()
    result = project_cycle_moments(
        raw,
        mean,
        target,
        normals,
        torch,
        maximum_iterations=args.iterations,
        absolute_tolerance=1e-6,
        relative_tolerance=1e-5,
    )
    forward_seconds = time.perf_counter() - started

    backward_seconds = None
    gradient_finite = None
    gradient_l1 = None
    if args.backward:
        started = time.perf_counter()
        (result["field"].square().mean() + result["scale"].mean()).backward()
        backward_seconds = time.perf_counter() - started
        gradient_finite = bool(torch.isfinite(cone_coordinate.grad).all().item())
        gradient_l1 = float(cone_coordinate.grad.abs().sum().item())

    payload = {
        "schema_version": "aurora.cycle_moment_projection_benchmark.v1",
        "synthetic_only": True,
        "device": "cpu",
        "python_platform": platform.platform(),
        "machine": platform.machine(),
        "torch_version": torch.__version__,
        "dtype": str(dtype),
        "shape": [args.phases, args.nodes, 3],
        "iterations": args.iterations,
        "cpu_threads": torch.get_num_threads(),
        "forward_seconds": forward_seconds,
        "backward_seconds": backward_seconds,
        "process_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "maximum_absolute_moment_error": float(
            result["absolute_moment_error"].max().item()
        ),
        "cone_coordinate_gradient_finite": gradient_finite,
        "cone_coordinate_gradient_l1": gradient_l1,
        "real_field_read": False,
        "gpu_used": False,
    }
    print(json.dumps(payload, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
