"""Fail-fast CUDA smoke test for a scheduler allocation."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import torch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable inside the scheduled container")

    device = torch.device("cuda:0")
    left = torch.randn((2048, 2048), device=device)
    right = torch.randn((2048, 2048), device=device)
    product = left @ right
    torch.cuda.synchronize()
    finite = bool(torch.isfinite(product).all().item())
    if not finite:
        raise RuntimeError("CUDA matrix multiplication produced a non-finite value")

    result = {
        "status": "complete",
        "device": torch.cuda.get_device_name(0),
        "device_count": torch.cuda.device_count(),
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "platform": platform.platform(),
        "matmul_shape": [2048, 2048],
        "finite": finite,
    }
    (args.output / "gpu_smoke.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
