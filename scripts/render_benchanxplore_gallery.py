#!/usr/bin/env python3
"""Create a multi-case raw-mesh and frame-0 velocity gallery."""
from __future__ import annotations
import argparse
from pathlib import Path
import h5py
import matplotlib.pyplot as plt
import numpy as np

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("root", type=Path); p.add_argument("output", type=Path); p.add_argument("--count", type=int, default=6); a = p.parse_args()
    files = sorted(a.root.glob("*.h5"))[:a.count]
    a.output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    report = ["case,points,tetrahedra,mean_speed_frame0"]
    for ax, f in zip(axes.flat, files):
        with h5py.File(f, "r") as h:
            xyz = h["data0"][()]; tetra = h["data1"].shape[0]; velocity = h["data2"][()]
        speed = np.linalg.norm(velocity, axis=1); step = max(1, len(xyz)//18000)
        d = ax.scatter(xyz[::step,0], xyz[::step,1], c=speed[::step], s=.35, cmap="magma")
        ax.set(title=f.stem.replace("AllFields_Resultats_", ""), aspect="equal"); ax.axis("off")
        report.append(f"{f.stem},{len(xyz)},{tetra},{speed.mean():.8f}")
    for ax in axes.flat[len(files):]: ax.axis("off")
    fig.suptitle("BenchAnXplore: six raw cases · XY projection · velocity magnitude at frame 0")
    fig.tight_layout(); fig.savefig(a.output / "six_case_velocity_gallery.png", dpi=180)
    (a.output / "six_case_velocity_gallery.csv").write_text("\n".join(report)+"\n")
if __name__ == "__main__": main()
