#!/usr/bin/env python3
"""Validate or fetch the read-only AURORA public-source watch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from aurora.source_watch import evaluate_snapshot, fetch_github_snapshot, load_config


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--fetch", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        result = {
            "watch_id": config["watch_id"],
            "status": config["status"],
            "config_sha256": config["_config_sha256"],
            "automatic_outcome": config["authorization"]["only_automatic_outcome"],
        }
    else:
        source = config["source"]
        observed = fetch_github_snapshot(source["repository"], source["default_branch"])
        result = evaluate_snapshot(config, observed)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
