#!/usr/bin/env python3
"""Stage only the two exact D0 members; never parse or summarize their fields."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.run_aneumo_transient_vtp_d0 import _get_member, _url  # noqa: E402
from scripts.audit_aneumo_transient_archives import RangeClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    source = config["source"]
    transport = config["transport"]
    if transport["mode"] != "exact_private_stage":
        raise SystemExit("staging requires exact_private_stage mode")
    if args.output_dir.exists():
        raise SystemExit("private stage must not already exist")
    args.output_dir.mkdir(parents=True)
    client = RangeClient(max_bytes=int(transport["maximum_http_bytes"]), retries=3)
    url = _url(source["repository"], source["huggingface_revision"], source["batch"])
    rows = []
    try:
        for member_name, staged_name, expected in zip(
            source["member_names"],
            source["staged_filenames"],
            source["expected_vtp_sha256"],
        ):
            payload = _get_member(
                client,
                url=url,
                case_id=int(source["case_id"]),
                member_name=member_name,
            )
            observed = hashlib.sha256(payload).hexdigest()
            if observed != expected:
                raise RuntimeError(f"exact member hash mismatch: {member_name}")
            target = args.output_dir / staged_name
            target.write_bytes(payload)
            rows.append({"filename": staged_name, "bytes": len(payload), "sha256": observed})
        if client.requests > int(transport["maximum_requests"]):
            raise RuntimeError("HTTP request ceiling exceeded")
    except Exception:
        for path in args.output_dir.iterdir():
            path.unlink()
        args.output_dir.rmdir()
        raise
    print(json.dumps({
        "state": "exact_private_stage_ready",
        "http_requests": client.requests,
        "http_bytes": client.bytes_read,
        "members": rows,
        "scientific_field_parsed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
