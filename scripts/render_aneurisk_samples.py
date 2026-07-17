#!/usr/bin/env python3
"""Aggregate Aneurisk case manifests and publisher preview images."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("root",type=Path); p.add_argument("output",type=Path); a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    manifests=sorted(a.root.glob("models/*_models/*/manifest.csv")); rows=[]
    for f in manifests:
        d=pd.read_csv(f); d["source_manifest"]=str(f.relative_to(a.root)); rows.append(d)
    df=pd.concat(rows,ignore_index=True); df.to_csv(a.output/"case_manifest.csv",index=False)
    fig,axes=plt.subplots(1,2,figsize=(12,5)); df["ruptureStatus"].fillna("missing").value_counts().plot.bar(color="#ef8354",ax=axes[0]); axes[0].set(title="Rupture status",xlabel="status",ylabel="cases")
    df["aneurysmLocation"].fillna("missing").value_counts().plot.bar(color="#447a67",ax=axes[1]); axes[1].set(title="Aneurysm location",xlabel="location",ylabel="cases")
    fig.tight_layout(); fig.savefig(a.output/"clinical_eda.png",dpi=180); plt.close(fig)
    previews=[f.parent/"image.png" for f in manifests if (f.parent/"image.png").exists()][:6]
    fig,axes=plt.subplots(2,3,figsize=(12,8))
    for ax,path in zip(axes.flat,previews):
        ax.imshow(Image.open(path)); ax.set(title=path.parent.name); ax.axis("off")
    for ax in axes.flat[len(previews):]: ax.axis("off")
    fig.suptitle("AneuriskData publisher-provided case previews")
    fig.tight_layout(); fig.savefig(a.output/"six_case_preview_gallery.png",dpi=180); plt.close(fig)
if __name__=="__main__": main()
