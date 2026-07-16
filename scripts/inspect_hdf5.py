#!/usr/bin/env python3
"""Record an HDF5 hierarchy, shapes, dtypes, and lightweight statistics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np


def describe(name: str, obj: h5py.Dataset | h5py.Group, records: list[dict]) -> None:
    if not isinstance(obj, h5py.Dataset):
        return
    row = {"path": name, "shape": list(obj.shape), "dtype": str(obj.dtype)}
    if obj.size and np.issubdtype(obj.dtype, np.number):
        sample = (
            obj[()]
            if obj.size <= 100_000
            else obj[tuple(slice(0, min(length, 10)) for length in obj.shape)]
        )
        values = np.asarray(sample, dtype=float)
        row["min"] = float(np.nanmin(values))
        row["max"] = float(np.nanmax(values))
        row["mean"] = float(np.nanmean(values))
    records.append(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records: list[dict] = []
    with h5py.File(args.input, "r") as h5:
        h5.visititems(lambda name, obj: describe(name, obj, records))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"datasets={len(records)} output={args.output}")


if __name__ == "__main__":
    main()
