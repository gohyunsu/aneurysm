#!/usr/bin/env python3
"""Render an auditable BenchAnXplore sample directly from HDF5/XDMF fields."""

from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with h5py.File(args.input, "r") as h5:
        xyz = h5["data0"][()]
        tetra = h5["data1"][()]
        velocity = np.stack([h5[f"data{2 + 2 * t}"][()] for t in range(80)])
        wall_mask = h5["data3"][()]

    speed = np.linalg.norm(velocity, axis=-1)
    means = speed.mean(axis=1)
    p95 = np.quantile(speed, 0.95, axis=1)
    wall_fraction = wall_mask.mean()
    projection = xyz[:, :2]
    extent = [projection[:, 0].min(), projection[:, 0].max(), projection[:, 1].min(), projection[:, 1].max()]
    vmax = np.quantile(speed, 0.995)

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    axes[0].scatter(projection[:, 0], projection[:, 1], c=xyz[:, 2], s=0.5, cmap="viridis")
    axes[0].set(title="Raw mesh points (XY projection)", xlabel="x", ylabel="y", aspect="equal")
    axes[1].scatter(projection[:, 0], projection[:, 1], c=speed[0], s=0.6, cmap="magma", vmin=0, vmax=vmax)
    axes[1].set(title="Velocity magnitude, frame 0", xlabel="x", ylabel="y", aspect="equal")
    axes[2].plot(means, label="mean |V|", lw=2)
    axes[2].plot(p95, label="p95 |V|", lw=2)
    axes[2].set(title="Temporal summary (80 frames)", xlabel="frame", ylabel="stored velocity magnitude")
    axes[2].legend(frameon=False)
    fig.suptitle(f"{args.input.stem}: {len(xyz):,} points · {len(tetra):,} tetrahedra · wall mask {wall_fraction:.1%}")
    fig.tight_layout()
    fig.savefig(args.output / "mesh_velocity_overview.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    dots = ax.scatter(projection[:, 0], projection[:, 1], c=speed[0], s=0.7, cmap="magma", vmin=0, vmax=vmax)
    ax.set(aspect="equal", xlabel="x", ylabel="y")
    title = ax.set_title("Velocity magnitude · frame 0 / 79")
    fig.colorbar(dots, ax=ax, label="stored velocity magnitude")
    def update(frame: int):
        dots.set_array(speed[frame])
        title.set_text(f"Velocity magnitude · frame {frame} / 79")
        return dots, title
    animation = FuncAnimation(fig, update, frames=range(0, 80, 2), interval=100, blit=False)
    animation.save(args.output / "velocity_xy.gif", writer=PillowWriter(fps=8), dpi=110)
    plt.close(fig)

    (args.output / "sample_metrics.txt").write_text(
        f"points={len(xyz)}\ntetrahedra={len(tetra)}\nframes={len(speed)}\nwall_fraction={wall_fraction:.8f}\n"
        f"mean_speed_min={means.min():.8f}\nmean_speed_max={means.max():.8f}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
