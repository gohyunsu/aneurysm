#!/usr/bin/env python3
"""Create a reproducible asset-level inventory without changing raw data."""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter
from pathlib import Path


def suffix_of(path: Path) -> str:
    name = path.name.lower()
    for suffix in (".nii.gz", ".cas.gz", ".tar.gz"):
        if name.endswith(suffix):
            return suffix
    return path.suffix.lower() or "[none]"


def sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help="Stable dataset identifier")
    parser.add_argument("root", type=Path, help="Extracted dataset root")
    parser.add_argument("output", type=Path, help="CSV output path")
    parser.add_argument("--hash", action="store_true", help="Compute SHA-256 for every file")
    args = parser.parse_args()

    root = args.root.resolve()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary = Counter()

    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["dataset", "relative_path", "suffix", "bytes", "sha256"],
        )
        writer.writeheader()
        for path in files:
            suffix = suffix_of(path)
            size = path.stat().st_size
            summary[suffix] += 1
            writer.writerow(
                {
                    "dataset": args.dataset,
                    "relative_path": path.relative_to(root).as_posix(),
                    "suffix": suffix,
                    "bytes": size,
                    "sha256": sha256(path) if args.hash else "",
                }
            )

    print(f"dataset={args.dataset}")
    print(f"root={root}")
    print(f"files={len(files)}")
    for suffix, count in sorted(summary.items()):
        print(f"{suffix}\t{count}")


if __name__ == "__main__":
    main()
