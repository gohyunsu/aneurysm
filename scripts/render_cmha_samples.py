#!/usr/bin/env python3
"""Render auditable CMHA clinical EDA and source CTA/mesh previews."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import trimesh


def vertices(path: Path) -> np.ndarray:
    mesh = trimesh.load(path, process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    return np.asarray(mesh.vertices)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--case", default="AHMU1218001")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    clinical = args.root / "statistical results" / "clinical_all.csv"
    df = pd.read_csv(clinical, skiprows=[1])
    label = np.where(df["Has aneurysm"].eq(0), "control", np.where(df["Rupture"].eq(1), "ruptured", "unruptured"))
    counts = pd.Series(label).value_counts().reindex(["control", "unruptured", "ruptured"], fill_value=0)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    counts.plot.bar(color=["#89938d", "#ef8354", "#447a67"], ax=axes[0])
    axes[0].set(title="CMHA clinical cohort labels", xlabel="group", ylabel="cases")
    df["location"].fillna("control/missing").value_counts().head(10).sort_values().plot.barh(color="#ef8354", ax=axes[1])
    axes[1].set(title="Top recorded locations", xlabel="cases", ylabel="location")
    fig.suptitle(f"CMHA clinical_all.csv · {len(df)} rows (unit row excluded)")
    fig.tight_layout()
    fig.savefig(args.output / "clinical_eda.png", dpi=180)
    plt.close(fig)

    case_dir = args.root / "patients" / args.case
    volume = next(case_dir.glob("*.nii.gz"))
    image = nib.load(volume).get_fdata()
    mid = tuple(n // 2 for n in image.shape[:3])
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, view, title in zip(axes[:3], [image[mid[0], :, :], image[:, mid[1], :], image[:, :, mid[2]]], ["sagittal", "coronal", "axial"]):
        ax.imshow(np.rot90(view), cmap="gray")
        ax.set(title=title); ax.axis("off")
    aneurysm = vertices(next(case_dir.glob("3D_aneurysm_*.stl")))
    vessel = vertices(next(case_dir.glob("3D_aneurysm_artery_*.stl")))
    a = aneurysm[::max(1, len(aneurysm)//10000)]
    v = vessel[::max(1, len(vessel)//30000)]
    ax = fig.add_subplot(1, 4, 4, projection="3d")
    ax.scatter(v[:,0], v[:,1], v[:,2], s=.15, c="#89938d")
    ax.scatter(a[:,0], a[:,1], a[:,2], s=.3, c="#ef8354")
    ax.set(title="source STL\nartery + aneurysm"); ax.set_axis_off()
    fig.suptitle(f"CMHA source preview · {args.case}")
    fig.tight_layout()
    fig.savefig(args.output / "case_AHMU1218001_preview.png", dpi=180)
    plt.close(fig)
    pd.DataFrame({"group": counts.index, "count": counts.values}).to_csv(args.output / "clinical_group_counts.csv", index=False)


if __name__ == "__main__":
    main()
