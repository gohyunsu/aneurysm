#!/usr/bin/env python3
"""Render reproducible point-cloud previews for source mesh assets."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import meshio
import numpy as np
import trimesh


def points_for(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".vtp":
        return np.asarray(meshio.read(path).points)
    mesh = trimesh.load(path, process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    return np.asarray(mesh.vertices)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args()
    paths = sorted([*args.root.rglob("*.vtp"), *args.root.rglob("*.stl")])[: args.limit]
    if not paths:
        raise SystemExit("No VTP/STL assets found")
    args.output.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(15, 8))
    report = []
    for idx, path in enumerate(paths, start=1):
        xyz = points_for(path)
        sample = xyz[:: max(1, len(xyz) // 20_000)]
        ax = fig.add_subplot(2, 3, idx, projection="3d")
        ax.scatter(sample[:, 0], sample[:, 1], sample[:, 2], c=sample[:, 2], s=0.25, cmap="viridis")
        ax.set_title(path.name[:36], fontsize=8)
        ax.set_axis_off()
        ax.set_box_aspect(np.maximum(np.ptp(sample, axis=0), 1e-8))
        report.append(f"{path.relative_to(args.root)},points={len(xyz)}")
    fig.suptitle("Source mesh point-cloud previews (no smoothing or remeshing)")
    fig.tight_layout()
    fig.savefig(args.output / "mesh_samples.png", dpi=180)
    (args.output / "mesh_samples.csv").write_text("path,points\n" + "\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
