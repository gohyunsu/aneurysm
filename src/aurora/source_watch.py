"""Read-only public-source change monitor for AURORA.

The monitor detects whether an official source has materially changed.  It can
only request a fresh source audit.  It cannot download a dataset, register P0,
select a model, or authorize compute.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence


class SourceWatchContractError(RuntimeError):
    """Raised when the watch-only boundary is changed or malformed."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "aurora.source_watch.v1":
        raise SourceWatchContractError("invalid_schema")
    if payload.get("status") != "watch_only":
        raise SourceWatchContractError("watch_status_changed")

    official = payload.get("source", {})
    if (
        official.get("repository") != "AbsoluteResonance/IAVS"
        or official.get("default_branch") != "main"
        or official.get("paper_url") != "https://arxiv.org/abs/2512.01319"
    ):
        raise SourceWatchContractError("official_source_changed")

    snapshot = payload.get("frozen_snapshot", {})
    entries = snapshot.get("root_entries", [])
    if (
        snapshot.get("availability") != "unreleased_readme_only"
        or snapshot.get("release_count") != 0
        or snapshot.get("license_spdx_id") is not None
        or snapshot.get("payload_or_code_entries") != []
        or [entry.get("name") for entry in entries] != ["README.md"]
        or len(str(snapshot.get("main_head_sha", ""))) != 40
    ):
        raise SourceWatchContractError("frozen_snapshot_changed")

    authorization = payload.get("authorization", {})
    forbidden = (
        "automatic_download",
        "automatic_terms_acceptance",
        "automatic_p0_registration",
        "method_selection",
        "architecture_selection",
        "gpu_training",
        "outer_test",
    )
    if any(authorization.get(key) is not False for key in forbidden):
        raise SourceWatchContractError("authorization_boundary_changed")
    if authorization.get("only_automatic_outcome") != "fresh_source_reaudit_only":
        raise SourceWatchContractError("automatic_outcome_changed")

    gate = payload.get("future_gate", {})
    if (
        float(gate.get("source_score_required", -1)) != 32.0
        or gate.get("p0_pass_only_opens") != "method_free_task_adequacy_p1"
        or gate.get("p1_pass_required_before_architecture_or_gpu") is not True
    ):
        raise SourceWatchContractError("future_gate_changed")

    execution = payload.get("execution_boundary", {})
    if (
        execution.get("scientific_execution_server") != "introai9"
        or execution.get("scheduler") != "pbs"
        or execution.get("excluded_server") != "junjinyong"
        or execution.get("login_node_gpu_commands_allowed") is not False
        or execution.get("current_aurora_pbs_jobs") != 0
    ):
        raise SourceWatchContractError("execution_boundary_changed")

    payload["_config_sha256"] = _sha256(source.read_bytes())
    return payload


def _json_get(url: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "AURORA-source-watch/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _material_entries(entries: Sequence[Mapping[str, Any]]) -> list[str]:
    non_material = {
        "readme",
        "readme.md",
        "readme.rst",
        "license",
        "license.md",
        "license.txt",
        "citation.cff",
    }
    return sorted(
        str(entry.get("name"))
        for entry in entries
        if str(entry.get("name", "")).lower() not in non_material
    )


def fetch_github_snapshot(repository: str, branch: str) -> dict[str, Any]:
    base = f"https://api.github.com/repos/{repository}"
    metadata = _json_get(base)
    root = _json_get(f"{base}/contents?ref={branch}")
    releases = _json_get(f"{base}/releases")
    commit = _json_get(f"{base}/commits/{branch}")
    if not isinstance(root, list) or not isinstance(releases, list):
        raise SourceWatchContractError("unexpected_github_response")
    license_info = metadata.get("license") or {}
    entries = [
        {
            "name": str(entry.get("name")),
            "type": str(entry.get("type")),
            "size": int(entry.get("size", 0)),
        }
        for entry in root
    ]
    return {
        "main_head_sha": str(commit.get("sha", "")),
        "root_entries": sorted(entries, key=lambda item: item["name"].lower()),
        "release_count": len(releases),
        "license_spdx_id": license_info.get("spdx_id"),
        "repository_size_kib": int(metadata.get("size", 0)),
        "payload_or_code_entries": _material_entries(entries),
    }


def evaluate_snapshot(config: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, Any]:
    frozen = config["frozen_snapshot"]
    signals: list[str] = []
    head_changed = observed.get("main_head_sha") != frozen.get("main_head_sha")
    material_entries = list(observed.get("payload_or_code_entries", []))
    if head_changed and material_entries:
        signals.append("main_head_changed_with_non_readme_payload_or_code")
    if int(observed.get("release_count", 0)) > int(frozen.get("release_count", 0)):
        signals.append("release_count_increased")
    if observed.get("license_spdx_id") and not frozen.get("license_spdx_id"):
        signals.append("explicit_repository_license_appeared")

    same_snapshot = all(
        observed.get(key) == frozen.get(key)
        for key in (
            "main_head_sha",
            "root_entries",
            "release_count",
            "license_spdx_id",
            "repository_size_kib",
            "payload_or_code_entries",
        )
    )
    return {
        "watch_id": config["watch_id"],
        "same_as_frozen_snapshot": same_snapshot,
        "material_change_signals": signals,
        "fresh_source_reaudit_triggered": bool(signals),
        "next_action": "fresh_source_reaudit_only" if signals else "continue_watch_only",
        "automatic_download_authorized": False,
        "p0_authorized": False,
        "method_or_architecture_authorized": False,
        "gpu_or_outer_test_authorized": False,
        "observed": dict(observed),
    }
