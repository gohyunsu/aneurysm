"""Read-only public-source change monitor for AURORA.

The monitor detects whether an official source has materially changed.  It can
only request a fresh source audit.  It cannot download a dataset, register P0,
select a model, or authorize compute.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Mapping, Sequence


class SourceWatchContractError(RuntimeError):
    """Raised when the watch-only boundary is changed or malformed."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    schema = payload.get("schema_version")
    if schema not in {
        "aurora.source_watch.v1",
        "aurora.source_watch.v2",
        "aurora.source_watch.v3",
        "aurora.source_watch.v4",
    }:
        raise SourceWatchContractError("invalid_schema")
    if payload.get("status") != "watch_only":
        raise SourceWatchContractError("watch_status_changed")

    if schema == "aurora.source_watch.v1":
        _validate_v1(payload)
    elif schema == "aurora.source_watch.v2":
        _validate_v2(payload)
    elif schema == "aurora.source_watch.v3":
        _validate_v3(payload)
    else:
        _validate_v4(payload)

    _validate_common_boundary(payload)
    payload["_config_sha256"] = _sha256(source.read_bytes())
    return payload


def _validate_v1(payload: Mapping[str, Any]) -> None:
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


def _validate_common_boundary(payload: Mapping[str, Any]) -> None:
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
    if payload.get("schema_version") in {
        "aurora.source_watch.v3",
        "aurora.source_watch.v4",
    }:
        if (
            authorization.get("only_automatic_outcome")
            != "manual_review_signal_only"
            or authorization.get("permitted_review_requests")
            != [
                "fresh_source_reaudit_only",
                "direct_prior_baseline_feasibility_reaudit_only",
            ]
        ):
            raise SourceWatchContractError("automatic_outcome_changed")
    elif authorization.get("only_automatic_outcome") != "fresh_source_reaudit_only":
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


def _validate_v2(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or [watch.get("watch_id") for watch in watches] != [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
    ]:
        raise SourceWatchContractError("v2_watch_set_changed")

    iavs, topbrain = watches
    if iavs.get("kind") != "github":
        raise SourceWatchContractError("iavs_watch_kind_changed")
    _validate_v1(
        {
            "source": iavs.get("source", {}),
            "frozen_snapshot": iavs.get("frozen_snapshot", {}),
        }
    )

    source = topbrain.get("source", {})
    if (
        topbrain.get("kind") != "zenodo_challenge"
        or source.get("zenodo_record_id") != 19707577
        or source.get("zenodo_api_url")
        != "https://zenodo.org/api/records/19707577"
        or source.get("challenge_page_url")
        != "https://topbrain2026.grand-challenge.org/topbrain2026/"
    ):
        raise SourceWatchContractError("topbrain2_official_source_changed")

    snapshot = topbrain.get("frozen_snapshot", {})
    files = snapshot.get("zenodo_files", [])
    if (
        snapshot.get("zenodo_record_id") != 19707577
        or snapshot.get("zenodo_modified")
        != "2026-04-23T11:14:24.475500+00:00"
        or snapshot.get("zenodo_revision") != 4
        or snapshot.get("zenodo_status") != "published"
        or snapshot.get("zenodo_access_right") != "open"
        or snapshot.get("zenodo_license_id") != "cc-by-4.0"
        or files
        != [
            {
                "key": "339-TopBrain_Segmentation_Challenge_for_Whole_Brain_Vessel_Anatomy_2026-04-22T16-37-16.pdf",
                "size": 139840,
                "checksum": "md5:da6c835d0336db81a94b78e7601f47b8",
            }
        ]
        or snapshot.get("payload_or_manifest_files") != []
        or snapshot.get("challenge_under_construction") is not True
        or snapshot.get("challenge_join_registration_available") is not True
        or snapshot.get("challenge_material_navigation_entries") != []
    ):
        raise SourceWatchContractError("topbrain2_frozen_snapshot_changed")


def _validate_v3(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v3_watch_set_changed")

    iavs, topbrain, trellis = watches
    _validate_v2({"watches": [iavs, topbrain]})
    if any(
        watch.get("review_request") != "fresh_source_reaudit_only"
        for watch in (iavs, topbrain)
    ):
        raise SourceWatchContractError("source_review_request_changed")

    source = trellis.get("source", {})
    snapshot = trellis.get("frozen_snapshot", {})
    if (
        trellis.get("kind") != "github_repository_availability"
        or trellis.get("review_request")
        != "direct_prior_baseline_feasibility_reaudit_only"
        or source.get("repository") != "clementhrv/trellis_for_intra"
        or source.get("repository_url")
        != "https://github.com/clementhrv/trellis_for_intra"
        or source.get("repository_api_url")
        != "https://api.github.com/repos/clementhrv/trellis_for_intra"
        or source.get("paper_url") != "https://arxiv.org/abs/2509.03095"
        or source.get("publication_doi") != "10.1016/j.neuri.2026.100259"
    ):
        raise SourceWatchContractError("trellis_official_source_changed")
    if snapshot != {
        "repository_api_http_status": 404,
        "repository_available": False,
        "default_branch": None,
        "main_head_sha": None,
        "root_entries": [],
        "release_count": None,
        "license_spdx_id": None,
        "repository_size_kib": None,
        "payload_or_code_entries": [],
        "availability": "stated_repository_not_publicly_readable",
    }:
        raise SourceWatchContractError("trellis_frozen_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("source_reaudit_is_not_asset_access") is not True
        or detection.get("direct_prior_review_is_not_method_selection") is not True
        or detection.get("score_repair_allowed") is not False
        or detection.get("frozen_snapshot_auto_update_allowed") is not False
    ):
        raise SourceWatchContractError("v3_change_boundary_changed")


def _validate_v4(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v4_watch_set_changed")

    _validate_v3(
        {
            "watches": watches[:3],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    github, huggingface = watches[3:]
    if github.get("kind") != "github" or github.get(
        "review_request"
    ) != "fresh_source_reaudit_only":
        raise SourceWatchContractError("aneumo_github_watch_changed")
    github_source = github.get("source", {})
    if (
        github_source.get("repository") != "Xigui-Li/Aneumo"
        or github_source.get("repository_url")
        != "https://github.com/Xigui-Li/Aneumo"
        or github_source.get("default_branch") != "main"
        or github_source.get("paper_url") != "https://arxiv.org/abs/2505.14717"
    ):
        raise SourceWatchContractError("aneumo_github_source_changed")

    expected_root = [
        {"name": "baselines", "type": "dir", "size": 0},
        {"name": "cfd_opt_deeponet", "type": "dir", "size": 0},
        {"name": "cfd_opt_swin_deeponet", "type": "dir", "size": 0},
        {"name": "Connection.csv", "type": "file", "size": 206795},
        {"name": "Data_preprocessing", "type": "dir", "size": 0},
        {"name": "datasheet_aneumo.md", "type": "file", "size": 17058},
        {"name": "fig", "type": "dir", "size": 0},
        {"name": "inference_deeponet.py", "type": "file", "size": 14333},
        {"name": "inference_swint.py", "type": "file", "size": 16309},
        {"name": "MPs.csv", "type": "file", "size": 2993817},
        {"name": "README.md", "type": "file", "size": 17598},
        {"name": "real_data", "type": "dir", "size": 0},
        {"name": "requirements.txt", "type": "file", "size": 98},
        {"name": "result", "type": "dir", "size": 0},
        {"name": "scripts", "type": "dir", "size": 0},
        {"name": "transient", "type": "dir", "size": 0},
        {"name": "visualization", "type": "dir", "size": 0},
    ]
    expected_root = sorted(expected_root, key=lambda item: item["name"].lower())
    github_snapshot = github.get("frozen_snapshot", {})
    if github_snapshot != {
        "main_head_sha": "701d53dde3489d84dbe9bc8324254629162eb45a",
        "root_entries": expected_root,
        "release_count": 0,
        "license_spdx_id": None,
        "repository_size_kib": 97770,
        "payload_or_code_entries": sorted(
            item["name"] for item in expected_root if item["name"] != "README.md"
        ),
        "availability": "public_code_and_synthetic_payload_without_real_case_mapping",
    }:
        raise SourceWatchContractError("aneumo_github_snapshot_changed")

    if huggingface.get("kind") != "huggingface_dataset" or huggingface.get(
        "review_request"
    ) != "fresh_source_reaudit_only":
        raise SourceWatchContractError("aneumo_huggingface_watch_changed")
    hf_source = huggingface.get("source", {})
    if (
        hf_source.get("dataset_id") != "SAIS-Life-Science/Aneumo"
        or hf_source.get("dataset_url")
        != "https://huggingface.co/datasets/SAIS-Life-Science/Aneumo"
        or hf_source.get("dataset_api_url")
        != "https://huggingface.co/api/datasets/SAIS-Life-Science/Aneumo"
    ):
        raise SourceWatchContractError("aneumo_huggingface_source_changed")
    if huggingface.get("frozen_snapshot") != {
        "sha": "f801adee816c18d3e18b23e6fcb147fe4c264209",
        "last_modified": "2026-03-19T11:17:28.000Z",
        "private": False,
        "gated": False,
        "disabled": False,
        "license_tags": ["license:cc-by-nc-nd-4.0"],
        "sibling_count": 370,
        "siblings_sha256": (
            "8cfc7347c80a52b19d43c83991dbc987cb154463f9669cfb259281d9b7331aa3"
        ),
        "real_case_or_mapping_entries": [],
        "availability": "public_synthetic_payload_without_real_case_mapping",
    }:
        raise SourceWatchContractError("aneumo_huggingface_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("metadata_watch_is_not_payload_access") is not True
        or detection.get("material_release_signal_is_not_e0_pass") is not True
    ):
        raise SourceWatchContractError("v4_change_boundary_changed")


def _url_get(url: str, accept: str) -> bytes:
    headers = {
        "Accept": accept,
        "User-Agent": "AURORA-source-watch/3.0",
    }
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {github_token}"
    request = urllib.request.Request(
        url,
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def _json_get(url: str, *, github: bool = False) -> Any:
    accept = "application/vnd.github+json" if github else "application/json"
    return json.loads(_url_get(url, accept).decode("utf-8"))


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
    metadata = _json_get(base, github=True)
    root = _json_get(f"{base}/contents?ref={branch}", github=True)
    releases = _json_get(f"{base}/releases", github=True)
    commit = _json_get(f"{base}/commits/{branch}", github=True)
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


def fetch_github_repository_availability_snapshot(
    repository_api_url: str,
) -> dict[str, Any]:
    try:
        metadata = _json_get(repository_api_url, github=True)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise SourceWatchContractError(
                f"github_repository_availability_unresolved_http_{error.code}"
            ) from error
        return {
            "repository_api_http_status": 404,
            "repository_available": False,
            "default_branch": None,
            "main_head_sha": None,
            "root_entries": [],
            "release_count": None,
            "license_spdx_id": None,
            "repository_size_kib": None,
            "payload_or_code_entries": [],
            "availability": "stated_repository_not_publicly_readable",
        }

    default_branch = str(metadata.get("default_branch") or "main")
    base = repository_api_url.rstrip("/")
    root = _json_get(f"{base}/contents?ref={default_branch}", github=True)
    releases = _json_get(f"{base}/releases", github=True)
    commit = _json_get(f"{base}/commits/{default_branch}", github=True)
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
        "repository_api_http_status": 200,
        "repository_available": True,
        "default_branch": default_branch,
        "main_head_sha": str(commit.get("sha", "")),
        "root_entries": sorted(entries, key=lambda item: item["name"].lower()),
        "release_count": len(releases),
        "license_spdx_id": license_info.get("spdx_id"),
        "repository_size_kib": int(metadata.get("size", 0)),
        "payload_or_code_entries": _material_entries(entries),
        "availability": "publicly_readable_repository",
    }


def fetch_huggingface_dataset_snapshot(dataset_api_url: str) -> dict[str, Any]:
    metadata = _json_get(dataset_api_url)
    siblings = sorted(
        str(item.get("rfilename"))
        for item in metadata.get("siblings", [])
        if item.get("rfilename")
    )
    sibling_manifest = ("\n".join(siblings) + "\n").encode("utf-8")
    material_tokens = ("aneux", "mapping", "real", "test", "undeform")
    material_entries = sorted(
        name for name in siblings if any(token in name.lower() for token in material_tokens)
    )
    return {
        "sha": str(metadata.get("sha", "")),
        "last_modified": str(metadata.get("lastModified", "")),
        "private": bool(metadata.get("private", False)),
        "gated": metadata.get("gated", False),
        "disabled": bool(metadata.get("disabled", False)),
        "license_tags": sorted(
            str(tag)
            for tag in metadata.get("tags", [])
            if str(tag).startswith("license:")
        ),
        "sibling_count": len(siblings),
        "siblings_sha256": _sha256(sibling_manifest),
        "real_case_or_mapping_entries": material_entries,
        "availability": (
            "public_payload_with_real_case_or_mapping_marker"
            if material_entries
            else "public_synthetic_payload_without_real_case_mapping"
        ),
    }


class _ChallengeAnchorParser(HTMLParser):
    material_labels = {
        "data",
        "dataset",
        "datasets",
        "evaluation",
        "leaderboard",
        "rules",
        "submission",
        "submissions",
        "submit",
    }

    def __init__(self) -> None:
        super().__init__()
        self._href: str | None = None
        self._text: list[str] = []
        self.material_entries: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        self._href = dict(attrs).get("href")
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._href is None:
            return
        label = " ".join(" ".join(self._text).split()).strip().lower()
        if label in self.material_labels:
            self.material_entries.append(f"{label}|{self._href}")
        self._href = None
        self._text = []


def _zenodo_payload_or_manifest_files(files: Sequence[Mapping[str, Any]]) -> list[str]:
    material_suffixes = (
        ".7z",
        ".csv",
        ".dcm",
        ".h5",
        ".json",
        ".mha",
        ".nii",
        ".nii.gz",
        ".npy",
        ".npz",
        ".stl",
        ".tar",
        ".tar.gz",
        ".vtk",
        ".vtp",
        ".yaml",
        ".yml",
        ".zip",
    )
    return sorted(
        str(item.get("key"))
        for item in files
        if str(item.get("key", "")).lower().endswith(material_suffixes)
    )


def fetch_zenodo_challenge_snapshot(
    zenodo_api_url: str, challenge_page_url: str
) -> dict[str, Any]:
    record = _json_get(zenodo_api_url)
    html = _url_get(challenge_page_url, "text/html").decode("utf-8", errors="replace")
    parser = _ChallengeAnchorParser()
    parser.feed(html)
    files = sorted(
        [
            {
                "key": str(item.get("key")),
                "size": int(item.get("size", 0)),
                "checksum": str(item.get("checksum")),
            }
            for item in record.get("files", [])
        ],
        key=lambda item: item["key"].lower(),
    )
    metadata = record.get("metadata", {})
    license_info = metadata.get("license") or {}
    lowered = html.lower()
    return {
        "zenodo_record_id": int(record.get("id", 0)),
        "zenodo_modified": str(record.get("modified", "")),
        "zenodo_revision": int(record.get("revision", 0)),
        "zenodo_status": str(record.get("status", "")),
        "zenodo_access_right": str(metadata.get("access_right", "")),
        "zenodo_license_id": license_info.get("id"),
        "zenodo_files": files,
        "payload_or_manifest_files": _zenodo_payload_or_manifest_files(files),
        "challenge_under_construction": "under construction" in lowered,
        "challenge_join_registration_available": (
            "/participants/registration/create/" in lowered
        ),
        "challenge_material_navigation_entries": sorted(set(parser.material_entries)),
    }


def evaluate_snapshot(
    config: Mapping[str, Any], observed: Mapping[str, Any]
) -> dict[str, Any]:
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
        "next_action": (
            "fresh_source_reaudit_only" if signals else "continue_watch_only"
        ),
        "automatic_download_authorized": False,
        "p0_authorized": False,
        "method_or_architecture_authorized": False,
        "gpu_or_outer_test_authorized": False,
        "observed": dict(observed),
    }


def evaluate_watch(
    watch: Mapping[str, Any], observed: Mapping[str, Any]
) -> dict[str, Any]:
    if watch.get("kind") == "github":
        result = evaluate_snapshot(watch, observed)
        if watch.get("review_request"):
            result["next_action"] = (
                watch["review_request"]
                if result["fresh_source_reaudit_triggered"]
                else "continue_watch_only"
            )
            result["manual_review_triggered"] = result[
                "fresh_source_reaudit_triggered"
            ]
            result["review_request"] = watch["review_request"]
        return result
    if watch.get("kind") == "github_repository_availability":
        frozen = watch["frozen_snapshot"]
        signals: list[str] = []
        if (
            frozen.get("repository_available") is False
            and observed.get("repository_available") is True
        ):
            signals.append("stated_repository_became_publicly_readable")
        if observed.get("payload_or_code_entries"):
            signals.append("repository_code_or_payload_appeared")
        if observed.get("release_count") not in (None, 0):
            signals.append("repository_release_appeared")
        if observed.get("license_spdx_id"):
            signals.append("explicit_repository_license_appeared")
        same_snapshot = all(
            observed.get(key) == frozen.get(key) for key in frozen.keys()
        )
        if not same_snapshot and not signals:
            signals.append("other_frozen_snapshot_field_changed")
        triggered = bool(signals)
        return {
            "watch_id": watch["watch_id"],
            "same_as_frozen_snapshot": same_snapshot,
            "material_change_signals": signals,
            "fresh_source_reaudit_triggered": False,
            "direct_prior_baseline_feasibility_reaudit_triggered": triggered,
            "manual_review_triggered": triggered,
            "review_request": watch["review_request"],
            "next_action": (
                watch["review_request"] if triggered else "continue_watch_only"
            ),
            "automatic_download_authorized": False,
            "p0_authorized": False,
            "method_or_architecture_authorized": False,
            "gpu_or_outer_test_authorized": False,
            "observed": dict(observed),
        }
    if watch.get("kind") == "huggingface_dataset":
        frozen = watch["frozen_snapshot"]
        signals: list[str] = []
        if observed.get("sha") != frozen.get("sha"):
            signals.append("huggingface_revision_changed")
        if observed.get("siblings_sha256") != frozen.get("siblings_sha256"):
            signals.append("huggingface_file_inventory_changed")
        new_material = sorted(
            set(observed.get("real_case_or_mapping_entries", []))
            - set(frozen.get("real_case_or_mapping_entries", []))
        )
        if new_material:
            signals.append("real_case_or_mapping_material_appeared")
        if observed.get("license_tags") != frozen.get("license_tags"):
            signals.append("huggingface_license_changed")
        for key in ("private", "gated", "disabled"):
            if observed.get(key) != frozen.get(key):
                signals.append(f"huggingface_{key}_state_changed")
        same_snapshot = all(
            observed.get(key) == frozen.get(key) for key in frozen.keys()
        )
        if not same_snapshot and not signals:
            signals.append("other_frozen_snapshot_field_changed")
        triggered = bool(signals)
        return {
            "watch_id": watch["watch_id"],
            "same_as_frozen_snapshot": same_snapshot,
            "material_change_signals": signals,
            "fresh_source_reaudit_triggered": triggered,
            "manual_review_triggered": triggered,
            "review_request": watch["review_request"],
            "next_action": (
                watch["review_request"] if triggered else "continue_watch_only"
            ),
            "automatic_download_authorized": False,
            "p0_authorized": False,
            "method_or_architecture_authorized": False,
            "gpu_or_outer_test_authorized": False,
            "observed": dict(observed),
        }
    if watch.get("kind") != "zenodo_challenge":
        raise SourceWatchContractError("unsupported_watch_kind")

    frozen = watch["frozen_snapshot"]
    signals: list[str] = []
    if observed.get("zenodo_modified") != frozen.get("zenodo_modified"):
        signals.append("zenodo_record_modified")
    if observed.get("zenodo_revision") != frozen.get("zenodo_revision"):
        signals.append("zenodo_revision_changed")
    if observed.get("zenodo_files") != frozen.get("zenodo_files"):
        signals.append("zenodo_file_inventory_changed")
    if observed.get("payload_or_manifest_files"):
        signals.append("zenodo_payload_or_manifest_file_appeared")
    if observed.get("zenodo_license_id") != frozen.get("zenodo_license_id"):
        signals.append("zenodo_license_changed")
    if (
        frozen.get("challenge_under_construction") is True
        and observed.get("challenge_under_construction") is False
    ):
        signals.append("challenge_under_construction_removed")
    new_navigation = sorted(
        set(observed.get("challenge_material_navigation_entries", []))
        - set(frozen.get("challenge_material_navigation_entries", []))
    )
    if new_navigation:
        signals.append("challenge_material_navigation_appeared")
    if observed.get("challenge_join_registration_available") != frozen.get(
        "challenge_join_registration_available"
    ):
        signals.append("challenge_registration_state_changed")

    keys = tuple(frozen.keys())
    same_snapshot = all(observed.get(key) == frozen.get(key) for key in keys)
    if not same_snapshot and not signals:
        signals.append("other_frozen_snapshot_field_changed")
    result = {
        "watch_id": watch["watch_id"],
        "same_as_frozen_snapshot": same_snapshot,
        "material_change_signals": signals,
        "fresh_source_reaudit_triggered": bool(signals),
        "next_action": (
            "fresh_source_reaudit_only" if signals else "continue_watch_only"
        ),
        "automatic_download_authorized": False,
        "p0_authorized": False,
        "method_or_architecture_authorized": False,
        "gpu_or_outer_test_authorized": False,
        "observed": dict(observed),
    }
    if watch.get("review_request"):
        result["next_action"] = (
            watch["review_request"] if signals else "continue_watch_only"
        )
        result["manual_review_triggered"] = bool(signals)
        result["review_request"] = watch["review_request"]
    return result


def fetch_watch_snapshot(watch: Mapping[str, Any]) -> dict[str, Any]:
    source = watch["source"]
    if (
        watch.get("kind") == "github"
        or watch.get("schema_version") == "aurora.source_watch.v1"
    ):
        return fetch_github_snapshot(source["repository"], source["default_branch"])
    if watch.get("kind") == "zenodo_challenge":
        return fetch_zenodo_challenge_snapshot(
            source["zenodo_api_url"], source["challenge_page_url"]
        )
    if watch.get("kind") == "github_repository_availability":
        return fetch_github_repository_availability_snapshot(
            source["repository_api_url"]
        )
    if watch.get("kind") == "huggingface_dataset":
        return fetch_huggingface_dataset_snapshot(source["dataset_api_url"])
    raise SourceWatchContractError("unsupported_watch_kind")


def evaluate_config(
    config: Mapping[str, Any], observations: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    if config.get("schema_version") == "aurora.source_watch.v1":
        return evaluate_snapshot(config, observations[config["watch_id"]])
    results = [
        evaluate_watch(watch, observations[watch["watch_id"]])
        for watch in config["watches"]
    ]
    if config.get("schema_version") in {
        "aurora.source_watch.v3",
        "aurora.source_watch.v4",
    }:
        source_triggered = any(
            item["fresh_source_reaudit_triggered"] for item in results
        )
        direct_prior_triggered = any(
            item.get("direct_prior_baseline_feasibility_reaudit_triggered", False)
            for item in results
        )
        manual_triggered = source_triggered or direct_prior_triggered
        requests = sorted(
            {
                item["review_request"]
                for item in results
                if item.get("manual_review_triggered", False)
            }
        )
        return {
            "schema_version": config["schema_version"],
            "same_as_all_frozen_snapshots": all(
                item["same_as_frozen_snapshot"] for item in results
            ),
            "manual_review_triggered": manual_triggered,
            "fresh_source_reaudit_triggered": source_triggered,
            "direct_prior_baseline_feasibility_reaudit_triggered": (
                direct_prior_triggered
            ),
            "manual_review_requests": requests,
            "next_action": (
                "manual_review_signal_only"
                if manual_triggered
                else "continue_watch_only"
            ),
            "automatic_download_authorized": False,
            "p0_authorized": False,
            "method_or_architecture_authorized": False,
            "gpu_or_outer_test_authorized": False,
            "watches": results,
        }

    triggered = any(item["fresh_source_reaudit_triggered"] for item in results)
    return {
        "schema_version": config["schema_version"],
        "same_as_all_frozen_snapshots": all(
            item["same_as_frozen_snapshot"] for item in results
        ),
        "fresh_source_reaudit_triggered": triggered,
        "next_action": (
            "fresh_source_reaudit_only" if triggered else "continue_watch_only"
        ),
        "automatic_download_authorized": False,
        "p0_authorized": False,
        "method_or_architecture_authorized": False,
        "gpu_or_outer_test_authorized": False,
        "watches": results,
    }
