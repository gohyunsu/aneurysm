#!/usr/bin/env python3
"""Validate or fetch the read-only AURORA public-source watch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from aurora.source_watch import (
    evaluate_config,
    fetch_watch_snapshot,
    load_config,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--watch-id",
        help="Fetch one v2 watch while retaining the same no-authorization boundary.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--fetch", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        watch_ids = (
            [config["watch_id"]]
            if config["schema_version"] == "aurora.source_watch.v1"
            else [watch["watch_id"] for watch in config["watches"]]
        )
        if args.watch_id and args.watch_id not in watch_ids:
            raise SystemExit(f"unknown watch id: {args.watch_id}")
        result = {
            "watch_ids": [args.watch_id] if args.watch_id else watch_ids,
            "status": config["status"],
            "config_sha256": config["_config_sha256"],
            "automatic_outcome": config["authorization"]["only_automatic_outcome"],
        }
    else:
        watches = (
            [config]
            if config["schema_version"] == "aurora.source_watch.v1"
            else config["watches"]
        )
        if args.watch_id:
            watches = [watch for watch in watches if watch["watch_id"] == args.watch_id]
            if not watches:
                raise SystemExit(f"unknown watch id: {args.watch_id}")
        observations = {
            watch["watch_id"]: fetch_watch_snapshot(watch) for watch in watches
        }
        if config["schema_version"] == "aurora.source_watch.v1":
            result = evaluate_config(config, observations)
        elif args.watch_id:
            watch = watches[0]
            result = evaluate_config(
                {
                    **config,
                    "watches": [watch],
                },
                observations,
            )
        else:
            result = evaluate_config(config, observations)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
