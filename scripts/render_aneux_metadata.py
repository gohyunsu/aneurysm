#!/usr/bin/env python3
"""Create EDA figures from the AneuX clinical master table without modifying it."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("clinical_csv", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.clinical_csv)
    status = df["status"].fillna("missing")
    source_status = pd.crosstab(df["source"], status).reindex(columns=["unruptured", "ruptured", "missing"], fill_value=0)
    locations = df["location"].fillna("missing").value_counts().head(12).sort_values()

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.15, 1]})
    source_status.plot.bar(stacked=True, color=["#ef8354", "#447a67", "#b7b7ae"], ax=axes[0])
    axes[0].set(title="Rupture status by source", xlabel="source", ylabel="cases")
    axes[0].legend(title="status", frameon=False)
    locations.plot.barh(color="#ef8354", ax=axes[1])
    axes[1].set(title="Top anatomical locations", xlabel="cases", ylabel="location")
    fig.suptitle(f"AneuX clinical.csv · {len(df)} cases")
    fig.tight_layout()
    fig.savefig(args.output / "clinical_eda.png", dpi=180)
    plt.close(fig)

    pd.DataFrame({"status": status.value_counts().index, "count": status.value_counts().values}).to_csv(args.output / "status_counts.csv", index=False)
    source_status.to_csv(args.output / "status_by_source.csv")
    locations.rename_axis("location").reset_index(name="count").to_csv(args.output / "top_locations.csv", index=False)


if __name__ == "__main__":
    main()
