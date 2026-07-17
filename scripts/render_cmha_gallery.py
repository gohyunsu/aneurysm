#!/usr/bin/env python3
"""Render three source CMHA cases: CTA axial slice and aneurysm STL preview."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import trimesh

def pts(path: Path) -> np.ndarray:
    m = trimesh.load(path, process=False)
    if isinstance(m, trimesh.Scene): m = trimesh.util.concatenate(tuple(m.geometry.values()))
    return np.asarray(m.vertices)

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("root",type=Path); p.add_argument("output",type=Path); p.add_argument("--count",type=int,default=3); a=p.parse_args()
    cases=sorted(x for x in (a.root/"patients").iterdir() if x.is_dir())[:a.count]; a.output.mkdir(parents=True,exist_ok=True)
    fig=plt.figure(figsize=(15,10)); report=["case,cta_shape,aneurysm_vertices"]
    for row,case in enumerate(cases):
        vol=nib.load(next(case.glob("*.nii.gz"))).get_fdata(); axial=vol[:,:,vol.shape[2]//2]
        ax=fig.add_subplot(len(cases),2,2*row+1); ax.imshow(np.rot90(axial),cmap="gray"); ax.set(title=f"{case.name} · CTA axial midpoint"); ax.axis("off")
        xyz=pts(next(case.glob("3D_aneurysm_*.stl"))); sample=xyz[::max(1,len(xyz)//16000)]
        ax=fig.add_subplot(len(cases),2,2*row+2,projection="3d"); ax.scatter(sample[:,0],sample[:,1],sample[:,2],c=sample[:,2],s=.3,cmap="magma"); ax.set(title=f"{case.name} · aneurysm STL"); ax.set_axis_off()
        report.append(f"{case.name},{'x'.join(map(str,vol.shape))},{len(xyz)}")
    fig.suptitle("CMHA source gallery: CTA NIfTI and corresponding aneurysm STL")
    fig.tight_layout(); fig.savefig(a.output/"three_case_cta_mesh_gallery.png",dpi=180)
    (a.output/"three_case_cta_mesh_gallery.csv").write_text("\n".join(report)+"\n")
if __name__=="__main__": main()
