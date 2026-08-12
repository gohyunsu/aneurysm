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
        "aurora.source_watch.v5",
        "aurora.source_watch.v6",
        "aurora.source_watch.v7",
        "aurora.source_watch.v8",
        "aurora.source_watch.v9",
        "aurora.source_watch.v10",
        "aurora.source_watch.v11",
        "aurora.source_watch.v12",
        "aurora.source_watch.v13",
        "aurora.source_watch.v14",
        "aurora.source_watch.v15",
        "aurora.source_watch.v16",
        "aurora.source_watch.v17",
        "aurora.source_watch.v18",
        "aurora.source_watch.v19",
        "aurora.source_watch.v20",
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
    elif schema == "aurora.source_watch.v4":
        _validate_v4(payload)
    elif schema == "aurora.source_watch.v5":
        if payload.get("extends") != "source_watch_v4.json":
            raise SourceWatchContractError("v5_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v4":
            raise SourceWatchContractError("v5_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v5_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v5(payload)
    elif schema == "aurora.source_watch.v6":
        if payload.get("extends") != "source_watch_v5.json":
            raise SourceWatchContractError("v6_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v5":
            raise SourceWatchContractError("v6_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v6_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v6(payload)
    elif schema == "aurora.source_watch.v7":
        if payload.get("extends") != "source_watch_v6.json":
            raise SourceWatchContractError("v7_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v6":
            raise SourceWatchContractError("v7_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v7_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v7(payload)
    elif schema == "aurora.source_watch.v8":
        if payload.get("extends") != "source_watch_v7.json":
            raise SourceWatchContractError("v8_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v7":
            raise SourceWatchContractError("v8_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v8_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v8(payload)
    elif schema == "aurora.source_watch.v9":
        if payload.get("extends") != "source_watch_v8.json":
            raise SourceWatchContractError("v9_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v8":
            raise SourceWatchContractError("v9_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v9_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v9(payload)
    elif schema == "aurora.source_watch.v10":
        if payload.get("extends") != "source_watch_v9.json":
            raise SourceWatchContractError("v10_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v9":
            raise SourceWatchContractError("v10_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v10_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v10(payload)
    elif schema == "aurora.source_watch.v11":
        if payload.get("extends") != "source_watch_v10.json":
            raise SourceWatchContractError("v11_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v10":
            raise SourceWatchContractError("v11_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v11_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v11(payload)
    elif schema == "aurora.source_watch.v12":
        if payload.get("extends") != "source_watch_v11.json":
            raise SourceWatchContractError("v12_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v11":
            raise SourceWatchContractError("v12_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v12_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v12(payload)
    elif schema == "aurora.source_watch.v13":
        if payload.get("extends") != "source_watch_v12.json":
            raise SourceWatchContractError("v13_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v12":
            raise SourceWatchContractError("v13_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v13_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v13(payload)
    elif schema == "aurora.source_watch.v14":
        if payload.get("extends") != "source_watch_v13.json":
            raise SourceWatchContractError("v14_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v13":
            raise SourceWatchContractError("v14_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v14_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v14(payload)
    elif schema == "aurora.source_watch.v15":
        if payload.get("extends") != "source_watch_v14.json":
            raise SourceWatchContractError("v15_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v14":
            raise SourceWatchContractError("v15_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v15_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v15(payload)
    elif schema == "aurora.source_watch.v16":
        if payload.get("extends") != "source_watch_v15.json":
            raise SourceWatchContractError("v16_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v15":
            raise SourceWatchContractError("v16_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v16_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v16(payload)
    elif schema == "aurora.source_watch.v17":
        if payload.get("extends") != "source_watch_v16.json":
            raise SourceWatchContractError("v17_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v16":
            raise SourceWatchContractError("v17_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v17_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v17(payload)
    elif schema == "aurora.source_watch.v18":
        if payload.get("extends") != "source_watch_v17.json":
            raise SourceWatchContractError("v18_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v17":
            raise SourceWatchContractError("v18_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v18_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v18(payload)
    elif schema == "aurora.source_watch.v19":
        if payload.get("extends") != "source_watch_v18.json":
            raise SourceWatchContractError("v19_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v18":
            raise SourceWatchContractError("v19_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v19_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v19(payload)
    else:
        if payload.get("extends") != "source_watch_v19.json":
            raise SourceWatchContractError("v20_base_contract_changed")
        base = load_config(source.parent / payload["extends"])
        if base.get("schema_version") != "aurora.source_watch.v19":
            raise SourceWatchContractError("v20_base_schema_changed")
        added = payload.get("added_watches")
        if not isinstance(added, list):
            raise SourceWatchContractError("v20_added_watches_missing")
        payload["watches"] = list(base["watches"]) + added
        _validate_v20(payload)

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
        "aurora.source_watch.v5",
        "aurora.source_watch.v6",
        "aurora.source_watch.v7",
        "aurora.source_watch.v8",
        "aurora.source_watch.v9",
        "aurora.source_watch.v10",
        "aurora.source_watch.v11",
        "aurora.source_watch.v12",
        "aurora.source_watch.v13",
        "aurora.source_watch.v14",
        "aurora.source_watch.v15",
        "aurora.source_watch.v16",
        "aurora.source_watch.v17",
        "aurora.source_watch.v18",
        "aurora.source_watch.v19",
        "aurora.source_watch.v20",
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


def _validate_v5(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v5_watch_set_changed")

    _validate_v4(
        {
            "watches": watches[:5],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    aneug, aneurisk, largeia, topaneu = watches[5:]

    if aneug.get("kind") != "huggingface_revision" or aneug.get(
        "review_request"
    ) != "fresh_source_reaudit_only":
        raise SourceWatchContractError("aneug_huggingface_watch_changed")
    if aneug.get("source") != {
        "dataset_id": "whding123/AneuG-Flow",
        "dataset_url": "https://huggingface.co/datasets/whding123/AneuG-Flow",
        "dataset_api_url": "https://huggingface.co/api/datasets/whding123/AneuG-Flow",
    }:
        raise SourceWatchContractError("aneug_huggingface_source_changed")
    if aneug.get("frozen_snapshot") != {
        "sha": "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "last_modified": "2026-01-13T17:09:10.000Z",
        "private": False,
        "gated": False,
        "disabled": False,
        "license_tags": ["license:cc-by-sa-4.0"],
        "used_storage_bytes": 2632691749582,
        "availability": "public_synthetic_transient_wss_payload_exact_revision",
    }:
        raise SourceWatchContractError("aneug_huggingface_snapshot_changed")

    expected_zenodo = {
        "aneurisk_zenodo_material_revision_v1": {
            "source": {
                "zenodo_record_id": 19455127,
                "zenodo_api_url": "https://zenodo.org/api/records/19455127",
                "record_url": "https://zenodo.org/records/19455127",
            },
            "snapshot": {
                "zenodo_record_id": 19455127,
                "zenodo_modified": "2026-04-07T14:32:30.723519+00:00",
                "zenodo_revision": 4,
                "zenodo_status": "published",
                "zenodo_access_right": "open",
                "zenodo_license_id": "cc-by-4.0",
                "zenodo_files": [
                    {
                        "key": "AneuriskCFDResults_Zenodo.tar.gz",
                        "size": 1430889142,
                        "checksum": "md5:8c66e7bb359d04bd1a5d6db6da3f3926",
                    },
                    {
                        "key": "README.md",
                        "size": 1436,
                        "checksum": "md5:f552f4d1440848f0cdb8700371579115",
                    },
                ],
                "payload_or_manifest_files": ["AneuriskCFDResults_Zenodo.tar.gz"],
                "availability": "public_cycle_averaged_wss_vtp_archive_exact_revision",
            },
        },
        "largeia_zenodo_access_revision_v1": {
            "source": {
                "zenodo_record_id": 6801398,
                "zenodo_api_url": "https://zenodo.org/api/records/6801398",
                "record_url": "https://zenodo.org/records/6801398",
            },
            "snapshot": {
                "zenodo_record_id": 6801398,
                "zenodo_modified": "2025-07-10T02:07:42.142484+00:00",
                "zenodo_revision": 10,
                "zenodo_status": "published",
                "zenodo_access_right": "restricted",
                "zenodo_license_id": None,
                "zenodo_files": [],
                "payload_or_manifest_files": [],
                "availability": "restricted_metadata_only_no_public_files",
            },
        },
    }
    for watch in (aneurisk, largeia):
        expected = expected_zenodo[watch["watch_id"]]
        if watch.get("kind") != "zenodo_record" or watch.get(
            "review_request"
        ) != "fresh_source_reaudit_only":
            raise SourceWatchContractError("zenodo_record_watch_changed")
        if watch.get("source") != expected["source"]:
            raise SourceWatchContractError("zenodo_record_source_changed")
        if watch.get("frozen_snapshot") != expected["snapshot"]:
            raise SourceWatchContractError("zenodo_record_snapshot_changed")

    if topaneu.get("kind") != "zenodo_challenge" or topaneu.get(
        "review_request"
    ) != "fresh_source_reaudit_only":
        raise SourceWatchContractError("topaneu_watch_changed")
    if topaneu.get("source") != {
        "zenodo_record_id": 19848807,
        "zenodo_api_url": "https://zenodo.org/api/records/19848807",
        "record_url": "https://zenodo.org/records/19848807",
        "challenge_page_url": "https://topaneu-26.grand-challenge.org/",
    }:
        raise SourceWatchContractError("topaneu_source_changed")
    if topaneu.get("frozen_snapshot") != {
        "zenodo_record_id": 19848807,
        "zenodo_modified": "2026-04-28T09:48:58.486163+00:00",
        "zenodo_revision": 4,
        "zenodo_status": "published",
        "zenodo_access_right": "open",
        "zenodo_license_id": "cc-by-4.0",
        "zenodo_files": [
            {
                "key": "335-TopAneu_2026_Multimodal_Vessel-Specific_Intracranial_Aneurysm_Classification_and_2026-04-22T16-37-15.pdf",
                "size": 150978,
                "checksum": "md5:773b04597d4ff2c798837fb5d40b4bf9",
            }
        ],
        "payload_or_manifest_files": [],
        "challenge_under_construction": False,
        "challenge_join_registration_available": True,
        "challenge_material_navigation_entries": [
            "data|https://topaneu-26.grand-challenge.org/data/",
            "evaluation|https://topaneu-26.grand-challenge.org/evaluation/",
        ],
    }:
        raise SourceWatchContractError("topaneu_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("historical_execution_repair_trigger_allowed") is not False
        or detection.get("terms_acceptance_automatic_allowed") is not False
        or detection.get("watch_expansion_is_not_new_scientific_evidence") is not True
    ):
        raise SourceWatchContractError("v5_change_boundary_changed")


def _validate_v6(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
        "aneux_transient_cfd_material_revision_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v6_watch_set_changed")

    _validate_v5(
        {
            "watches": watches[:9],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    transient = watches[9]
    if transient.get("kind") != "huggingface_aneux_transient_revision" or transient.get(
        "review_request"
    ) != "fresh_source_reaudit_only":
        raise SourceWatchContractError("aneux_transient_watch_changed")
    if transient.get("source") != {
        "dataset_id": "yiyings/transient-dataset",
        "legacy_alias_id": "yiyings/sidewall-transient-cfd",
        "dataset_url": "https://huggingface.co/datasets/yiyings/transient-dataset",
        "dataset_api_url": "https://huggingface.co/api/datasets/yiyings/transient-dataset",
    }:
        raise SourceWatchContractError("aneux_transient_source_changed")
    if transient.get("frozen_snapshot") != {
        "sha": "38c574bc54a1ead9a4830da09ae5087e42b9d6c2",
        "created_at": "2026-05-04T03:02:11.000Z",
        "last_modified": "2026-06-20T09:40:19.000Z",
        "private": False,
        "gated": "manual",
        "disabled": False,
        "license_tags": ["license:cc-by-nc-4.0"],
        "used_storage_bytes": 1381031461556,
        "description_sha256": (
            "2650b26a6ee0234cacc107b6dc6b5fc200942616e0d2d5e7a12db08d8a8df29f"
        ),
        "sibling_count": 1940,
        "siblings_sha256": (
            "7874b4520d455f8921317ad1d97de7614d1ed95185df2b77f6bce40e39c6508d"
        ),
        "bifurcation_case_folders": 180,
        "sidewall_case_folders": 143,
        "unique_visible_case_ids": 322,
        "cross_topology_overlap_ids": ["SNF365"],
        "topology_case_manifest_sha256": (
            "53d0f8145b69f42ec630703fff27282a1e562009fa6b0136488ee5172cb6d5c3"
        ),
        "unique_id_manifest_sha256": (
            "2693754f1de732289ac5d15b94061dfe2815bca2bfe126da1c5460fb7ae5a648"
        ),
        "extension_counts": {
            "": 1,
            ".csv": 323,
            ".md": 1,
            ".npz": 323,
            ".obj": 323,
            ".ply": 323,
            ".pt": 646,
        },
        "availability": "manual_gated_aneux_derived_transient_cfd_metadata_only",
    }:
        raise SourceWatchContractError("aneux_transient_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("gated_manifest_metadata_is_not_payload_access") is not True
        or detection.get("visible_case_id_is_not_verified_patient_unit") is not True
        or detection.get("material_source_change_is_not_e0_pass") is not True
    ):
        raise SourceWatchContractError("v6_change_boundary_changed")


def _validate_v7(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
        "aneux_transient_cfd_material_revision_v1",
        "pointflownet_baseline_release_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v7_watch_set_changed")

    _validate_v6(
        {
            "watches": watches[:10],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    pointflownet = watches[10]
    if (
        pointflownet.get("kind") != "github"
        or pointflownet.get("review_request")
        != "direct_prior_baseline_feasibility_reaudit_only"
        or pointflownet.get("source")
        != {
            "repository": "yiyingsheng07/PointFlowNet",
            "repository_url": "https://github.com/yiyingsheng07/PointFlowNet",
            "default_branch": "main",
            "paper_doi": "10.1016/j.cmpb.2026.109308",
        }
    ):
        raise SourceWatchContractError("pointflownet_source_changed")
    if pointflownet.get("frozen_snapshot") != {
        "main_head_sha": "5cb4f2545d25b6e8b855806cb3a345b8b1d72594",
        "root_entries": [
            {"name": "dataloader.py", "type": "file", "size": 4782},
            {"name": "dataset", "type": "dir", "size": 0},
            {"name": "figs", "type": "dir", "size": 0},
            {"name": "logs", "type": "dir", "size": 0},
            {"name": "loss.py", "type": "file", "size": 2282},
            {"name": "model.py", "type": "file", "size": 12703},
            {"name": "README.md", "type": "file", "size": 35},
            {"name": "test.py", "type": "file", "size": 4836},
            {"name": "train.py", "type": "file", "size": 7239},
        ],
        "release_count": 0,
        "license_spdx_id": None,
        "repository_size_kib": 41563,
        "payload_or_code_entries": [
            "dataloader.py",
            "dataset",
            "figs",
            "logs",
            "loss.py",
            "model.py",
            "test.py",
            "train.py",
        ],
        "availability": (
            "public_partial_code_checkpoint_and_results_without_dataset_"
            "split_manifest_or_license"
        ),
    }:
        raise SourceWatchContractError("pointflownet_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("partial_baseline_repository_is_not_executable_baseline")
        is not True
        or detection.get("repository_change_is_not_architecture_selection")
        is not True
    ):
        raise SourceWatchContractError("v7_change_boundary_changed")


def _validate_v8(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
        "aneux_transient_cfd_material_revision_v1",
        "pointflownet_baseline_release_v1",
        "aaa_wss_neural_surrogate_baseline_release_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v8_watch_set_changed")

    _validate_v7(
        {
            "watches": watches[:11],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    aaa_wss = watches[11]
    if (
        aaa_wss.get("kind") != "github"
        or aaa_wss.get("review_request")
        != "direct_prior_baseline_feasibility_reaudit_only"
        or aaa_wss.get("source")
        != {
            "repository": "PatRyg99/AAA-WSS-neural-surrogate",
            "repository_url": (
                "https://github.com/PatRyg99/AAA-WSS-neural-surrogate"
            ),
            "default_branch": "main",
            "paper_url": "https://arxiv.org/abs/2507.22817",
        }
    ):
        raise SourceWatchContractError("aaa_wss_source_changed")
    if aaa_wss.get("frozen_snapshot") != {
        "main_head_sha": "2f78bf1879e5e555c3369d91822be3f567f9fbd1",
        "root_entries": [
            {"name": "README.md", "type": "file", "size": 183},
        ],
        "release_count": 0,
        "license_spdx_id": None,
        "repository_size_kib": 0,
        "payload_or_code_entries": [],
        "availability": (
            "stated_public_code_repository_is_readme_only_without_license_"
            "code_checkpoint_or_cfd_fields"
        ),
    }:
        raise SourceWatchContractError("aaa_wss_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get(
            "readme_only_stated_code_repository_is_not_executable_baseline"
        )
        is not True
        or detection.get("direct_prior_code_release_is_not_task_asset_release")
        is not True
        or detection.get("repository_change_is_not_architecture_selection")
        is not True
    ):
        raise SourceWatchContractError("v8_change_boundary_changed")


def _validate_v9(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
        "aneux_transient_cfd_material_revision_v1",
        "pointflownet_baseline_release_v1",
        "aaa_wss_neural_surrogate_baseline_release_v1",
        "mris_bench_postreview_target_contract_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v9_watch_set_changed")

    _validate_v8(
        {
            "watches": watches[:12],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    mris = watches[12]
    if (
        mris.get("kind") != "huggingface_under_review_dataset"
        or mris.get("review_request") != "fresh_source_reaudit_only"
        or mris.get("source")
        != {
            "dataset_id": "lixiangcog/MRIS-Bench",
            "legacy_alias_id": "lixiang007666/MRIS-Bench",
            "dataset_url": (
                "https://huggingface.co/datasets/lixiangcog/MRIS-Bench"
            ),
            "dataset_api_url": (
                "https://huggingface.co/api/datasets/lixiangcog/MRIS-Bench"
            ),
        }
    ):
        raise SourceWatchContractError("mris_bench_source_changed")
    if mris.get("frozen_snapshot") != {
        "sha": "6f2d6d9ad10eba68700ce95c7523ec78934f7a3d",
        "created_at": "2026-05-05T03:13:24.000Z",
        "last_modified": "2026-05-15T03:22:31.000Z",
        "private": False,
        "gated": False,
        "disabled": False,
        "license_tags": ["license:mit"],
        "used_storage_bytes": 7449574455,
        "description_sha256": (
            "626e6f483bc768f40a23d43ed2c3540e475525634bae9c9f3b14500267eb7f03"
        ),
        "sibling_count": 12,
        "siblings_sha256": (
            "f90a9ad569f6d7b552a811fe435f3c54cdebe742013bb4c4e02b93aa9d3fc71a"
        ),
        "arrow_shard_count": 8,
        "under_review_release_statement_present": True,
        "availability": (
            "public_arrow_payload_under_review_without_detailed_metadata_"
            "split_or_source_lineage"
        ),
    }:
        raise SourceWatchContractError("mris_bench_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("row_count_is_not_independent_patient_count") is not True
        or detection.get("card_license_is_not_upstream_medical_data_lineage")
        is not True
        or detection.get("postreview_metadata_change_is_not_e0_pass") is not True
        or detection.get(
            "visible_viewer_examples_are_not_registered_quality_prevalence"
        )
        is not True
    ):
        raise SourceWatchContractError("v9_change_boundary_changed")


def _validate_v10(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
        "aneux_transient_cfd_material_revision_v1",
        "pointflownet_baseline_release_v1",
        "aaa_wss_neural_surrogate_baseline_release_v1",
        "mris_bench_postreview_target_contract_v1",
        "topaneu_github_release_contract_v2",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v10_watch_set_changed")

    _validate_v9(
        {
            "watches": watches[:13],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    topaneu = watches[13]
    if (
        topaneu.get("kind") != "github_versioned_release_contract"
        or topaneu.get("review_request") != "fresh_source_reaudit_only"
        or topaneu.get("source")
        != {
            "repository": "Bangulli/TopAneu-26",
            "repository_api_url": (
                "https://api.github.com/repos/Bangulli/TopAneu-26"
            ),
            "default_branch": "main",
            "batch1_anchor_commit": (
                "15afd4b95e770f69cd3ff1dba9f625c65446a6e5"
            ),
            "release_prefix": "topaneu_release/",
        }
    ):
        raise SourceWatchContractError("topaneu_release_contract_source_changed")

    expected_counts = {
        "image_checksum_count": 417,
        "location_json_count": 417,
        "location_mask_checksum_count": 417,
        "type_mask_checksum_count": 417,
        "vessel_mask_checksum_count": 417,
    }
    expected_batch1_counts = {
        "image_checksum_count": 98,
        "location_json_count": 98,
        "location_mask_checksum_count": 98,
        "type_mask_checksum_count": 98,
        "vessel_mask_checksum_count": 98,
    }
    if topaneu.get("frozen_snapshot") != {
        "main_head_sha": "018c243445f99199f484018c4c80575c84c72293",
        "main_root_tree_sha": "e7af931d6d9e1e236bac5b96903ab6a2a65daa06",
        "current_release_tree_sha": (
            "0bab2856144db5f0ba11e4151a59d44517481e95"
        ),
        "readme_blob": {
            "sha": "36a91bcc6889964e9992a65d04467384ba052dcc",
            "size": 11184,
        },
        "changelog_blob": {
            "sha": "e937e8ba276df5290f9c02590b295c8414423bc7",
            "size": 3868,
        },
        "terms_blob": {
            "sha": "9897d02ae58e1f69482ec7f2a9a5d3f208a6c87a",
            "size": 1107,
        },
        "current_manifest_counts": expected_counts,
        "batch1_anchor_commit": "15afd4b95e770f69cd3ff1dba9f625c65446a6e5",
        "batch1_root_tree_sha": "8ca0e92bed6e75713557e2f8e10111ebfd9f489f",
        "batch1_release_tree_sha": (
            "3bf4db45c1c1100fbcb6fd763bf0fb554f15c831"
        ),
        "batch1_manifest_counts": expected_batch1_counts,
        "availability": (
            "public_versioned_git_manifest_and_annotation_metadata_"
            "without_medical_payload_access_or_terms_acceptance"
        ),
    }:
        raise SourceWatchContractError("topaneu_release_contract_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("versioned_annotation_history_is_not_method_novelty")
        is not True
        or detection.get("git_blob_change_is_not_terms_acceptance") is not True
        or detection.get("annotation_metadata_is_not_medical_image_access")
        is not True
    ):
        raise SourceWatchContractError("v10_change_boundary_changed")


def _validate_v11(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
        "aneux_transient_cfd_material_revision_v1",
        "pointflownet_baseline_release_v1",
        "aaa_wss_neural_surrogate_baseline_release_v1",
        "mris_bench_postreview_target_contract_v1",
        "topaneu_github_release_contract_v2",
        "rsna_ica_release_contract_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v11_watch_set_changed")

    _validate_v10(
        {
            "watches": watches[:14],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    rsna = watches[14]
    if (
        rsna.get("kind") != "github_registry_wiki_contract"
        or rsna.get("review_request") != "fresh_source_reaudit_only"
        or rsna.get("source")
        != {
            "registry_repository": "awslabs/open-data-registry",
            "registry_file_path": (
                "datasets/rsna-intracranial-aneurysm-detection-dataset.yaml"
            ),
            "registry_contents_api_url": (
                "https://api.github.com/repos/awslabs/open-data-registry/"
                "contents/datasets/rsna-intracranial-aneurysm-detection-"
                "dataset.yaml?ref=main"
            ),
            "registry_commits_api_url": (
                "https://api.github.com/repos/awslabs/open-data-registry/"
                "commits?path=datasets/rsna-intracranial-aneurysm-detection-"
                "dataset.yaml&per_page=1"
            ),
            "wiki_repository": "RSNA/AI-Challenge-Data.wiki",
            "wiki_raw_url": (
                "https://raw.githubusercontent.com/wiki/RSNA/AI-Challenge-Data/"
                "RSNA-Intracranial-Aneurysm-Detection-Dataset.md"
            ),
        }
    ):
        raise SourceWatchContractError("rsna_release_contract_source_changed")

    if rsna.get("frozen_snapshot") != {
        "registry_file_commit_sha": (
            "523ffd3914ba99e6c4b17441f1633cc3eec74c69"
        ),
        "registry_blob_sha": "97b8c1f16b2809d2e82ec0c39d3b156b174c8c83",
        "registry_file_bytes": 2626,
        "registry_file_sha256": (
            "864f0716a8f6618e90f4c257c417f599fd6bb454abe73fc06eee8e771d3d8a10"
        ),
        "controlled_access_declared": True,
        "data_resource_publication_forthcoming": True,
        "noncommercial_no_redistribution_terms_declared": True,
        "wiki_page_bytes": 11,
        "wiki_page_sha256": (
            "4f7d64017689437e6d93f5724f3f797054f3935d98a13148025b616b8db8fb2c"
        ),
        "wiki_page_is_coming_soon_only": True,
        "machine_auditable_release_contract_present": False,
        "availability": (
            "controlled_access_registry_with_forthcoming_publication_and_"
            "coming_soon_wiki_without_machine_auditable_release_contract"
        ),
    }:
        raise SourceWatchContractError("rsna_release_contract_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("registry_or_wiki_change_is_not_terms_acceptance") is not True
        or detection.get("controlled_access_metadata_is_not_payload_access")
        is not True
        or detection.get("release_contract_change_is_not_p0_authority") is not True
        or detection.get("reference_provenance_issue_is_not_method_novelty")
        is not True
    ):
        raise SourceWatchContractError("v11_change_boundary_changed")


def _validate_v12(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    expected_ids = [
        "iavs_public_release_v1",
        "topbrain2_material_release_v1",
        "trellis_stated_code_availability_v1",
        "aneumo_github_material_release_v1",
        "aneumo_huggingface_material_release_v1",
        "aneug_huggingface_material_revision_v1",
        "aneurisk_zenodo_material_revision_v1",
        "largeia_zenodo_access_revision_v1",
        "topaneu_material_release_v1",
        "aneux_transient_cfd_material_revision_v1",
        "pointflownet_baseline_release_v1",
        "aaa_wss_neural_surrogate_baseline_release_v1",
        "mris_bench_postreview_target_contract_v1",
        "topaneu_github_release_contract_v2",
        "rsna_ica_release_contract_v1",
        "topbrain2025_data_release_v1",
        "topbrain2025_podium_dockers_v1",
        "bravecowcow_rsna_multitask_baseline_v1",
    ]
    if not isinstance(watches, list) or [
        watch.get("watch_id") for watch in watches
    ] != expected_ids:
        raise SourceWatchContractError("v12_watch_set_changed")

    _validate_v11(
        {
            "watches": watches[:15],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    data, dockers, bravecow = watches[15:]
    expected_zenodo = {
        "topbrain2025_data_release_v1": {
            "source": {
                "zenodo_record_id": 16878417,
                "zenodo_api_url": "https://zenodo.org/api/records/16878417",
                "record_url": "https://zenodo.org/records/16878417",
            },
            "snapshot": {
                "zenodo_record_id": 16878417,
                "zenodo_modified": "2026-06-02T16:56:20.313691+00:00",
                "zenodo_revision": 14,
                "zenodo_status": "published",
                "zenodo_access_right": "open",
                "zenodo_license_id": None,
                "zenodo_files": [
                    {
                        "key": "TopBrain_Data_Release_Batches1n2_081425.zip",
                        "size": 1958849592,
                        "checksum": "md5:b703ea31cd1f0e7115a5d3e6e61f59b3",
                    }
                ],
                "payload_or_manifest_files": [
                    "TopBrain_Data_Release_Batches1n2_081425.zip"
                ],
                "availability": (
                    "open_metadata_with_custom_clickthrough_terms_"
                    "and_unopened_patient_payload"
                ),
            },
        },
        "topbrain2025_podium_dockers_v1": {
            "source": {
                "zenodo_record_id": 20158639,
                "zenodo_api_url": "https://zenodo.org/api/records/20158639",
                "record_url": "https://zenodo.org/records/20158639",
            },
            "snapshot": {
                "zenodo_record_id": 20158639,
                "zenodo_modified": "2026-06-02T16:51:06.110189+00:00",
                "zenodo_revision": 18,
                "zenodo_status": "published",
                "zenodo_access_right": "open",
                "zenodo_license_id": "cc-by-4.0",
                "zenodo_files": [
                    {
                        "key": "reorient_nii.py",
                        "size": 2459,
                        "checksum": "md5:3c540a37710c1c7c84c3704246fbe220",
                    },
                    {
                        "key": "run_docker_topbrain_2025.py",
                        "size": 5581,
                        "checksum": "md5:e9f0d16e497c28f897aa892a5e328b4c",
                    },
                    {
                        "key": "Team_ARG_2025_topbrain_segmentation_ct.tar.gz",
                        "size": 5863399183,
                        "checksum": "md5:35d5434f91a274456f72f428fce067e0",
                    },
                    {
                        "key": "Team_ARG_2025_topbrain_segmentation_mr.tar.gz",
                        "size": 6094969422,
                        "checksum": "md5:e1fe74d1707907918b1b91002962f40f",
                    },
                    {
                        "key": "Team_KDH_2025_topbrain_segmentation_ct.tar.gz",
                        "size": 8038457100,
                        "checksum": "md5:4b71fe691b99e8a76cd0d83ebcf2da95",
                    },
                    {
                        "key": "Team_KDH_2025_topbrain_segmentation_mr.tar.gz",
                        "size": 11864241848,
                        "checksum": "md5:0224662747a594f5bc17932f5c85c313",
                    },
                    {
                        "key": "Team_UZH_2025_topbrain_segmentation_ct_mr.tar.gz",
                        "size": 4795293483,
                        "checksum": "md5:7d04086c75bdd459f4a8af44e753be0a",
                    },
                ],
                "payload_or_manifest_files": [
                    "Team_ARG_2025_topbrain_segmentation_ct.tar.gz",
                    "Team_ARG_2025_topbrain_segmentation_mr.tar.gz",
                    "Team_KDH_2025_topbrain_segmentation_ct.tar.gz",
                    "Team_KDH_2025_topbrain_segmentation_mr.tar.gz",
                    "Team_UZH_2025_topbrain_segmentation_ct_mr.tar.gz",
                ],
                "availability": "open_podium_docker_metadata_exact_revision",
            },
        },
    }
    for watch in (data, dockers):
        expected = expected_zenodo[watch["watch_id"]]
        if watch.get("kind") != "zenodo_record":
            raise SourceWatchContractError("topbrain2025_zenodo_kind_changed")
        if watch.get("source") != expected["source"]:
            raise SourceWatchContractError("topbrain2025_zenodo_source_changed")
        if watch.get("frozen_snapshot") != expected["snapshot"]:
            raise SourceWatchContractError("topbrain2025_zenodo_snapshot_changed")
    if data.get("review_request") != "fresh_source_reaudit_only" or dockers.get(
        "review_request"
    ) != "direct_prior_baseline_feasibility_reaudit_only":
        raise SourceWatchContractError("topbrain2025_review_request_changed")

    if (
        bravecow.get("kind") != "github"
        or bravecow.get("review_request")
        != "direct_prior_baseline_feasibility_reaudit_only"
        or bravecow.get("source")
        != {
            "repository": (
                "PengchengShi1220/RSNA2025_Intracranial-Aneurysm-Detection"
            ),
            "repository_url": (
                "https://github.com/PengchengShi1220/"
                "RSNA2025_Intracranial-Aneurysm-Detection"
            ),
            "default_branch": "master",
            "paper_url": "https://arxiv.org/abs/2606.26706",
        }
    ):
        raise SourceWatchContractError("bravecowcow_source_changed")
    if bravecow.get("frozen_snapshot") != {
        "main_head_sha": "e59e2368a722eabedc6b2228b1c6e1e7325cacd5",
        "root_entries": [
            {
                "name": "bravecowcow-2nd-place-inference-demo.ipynb",
                "type": "file",
                "size": 64594,
            },
            {
                "name": "bravecowcow-2nd-place-inference-final-submission.ipynb",
                "type": "file",
                "size": 64984,
            },
            {"name": "LICENSE", "type": "file", "size": 11400},
            {"name": "nifti_by_dicom2nifti.py", "type": "file", "size": 2205},
            {"name": "nnXNet", "type": "dir", "size": 0},
            {
                "name": "nnXNetResEncUNetM_two_seg_with_cls_ps_224_224_224_Plans.json",
                "type": "file",
                "size": 11427,
            },
            {
                "name": "process_RSNA2025_all_data.py",
                "type": "file",
                "size": 11954,
            },
            {"name": "README.md", "type": "file", "size": 6387},
            {"name": "requirements.txt", "type": "file", "size": 2718},
        ],
        "release_count": 0,
        "license_spdx_id": "Apache-2.0",
        "repository_size_kib": 464,
        "payload_or_code_entries": [
            "bravecowcow-2nd-place-inference-demo.ipynb",
            "bravecowcow-2nd-place-inference-final-submission.ipynb",
            "nifti_by_dicom2nifti.py",
            "nnXNet",
            "nnXNetResEncUNetM_two_seg_with_cls_ps_224_224_224_Plans.json",
            "process_RSNA2025_all_data.py",
            "requirements.txt",
        ],
        "availability": (
            "public_apache_code_without_controlled_rsna_payload_"
            "or_independent_dense_reference"
        ),
    }:
        raise SourceWatchContractError("bravecowcow_snapshot_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get("topbrain2025_data_terms_not_automatically_accepted")
        is not True
        or detection.get("public_vessel_labels_are_not_aneurysm_targets")
        is not True
        or detection.get("podium_dockers_are_direct_priors_not_method_selection")
        is not True
        or detection.get("rsna_pseudomasks_are_not_independent_dense_reference")
        is not True
        or detection.get("baseline_code_is_not_controlled_challenge_data")
        is not True
    ):
        raise SourceWatchContractError("v12_change_boundary_changed")


def _validate_v13(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 20:
        raise SourceWatchContractError("v13_watch_set_changed")
    _validate_v12(
        {
            "watches": watches[:18],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    zenodo, github = watches[18:]
    if (
        zenodo.get("watch_id") != "da4dcta_zenodo_material_release_v1"
        or zenodo.get("kind") != "zenodo_record"
        or zenodo.get("review_request") != "fresh_source_reaudit_only"
        or zenodo.get("source")
        != {
            "zenodo_record_id": 13788524,
            "zenodo_api_url": "https://zenodo.org/api/records/13788524",
            "record_url": "https://zenodo.org/records/13788524",
        }
        or zenodo.get("frozen_snapshot")
        != {
            "zenodo_record_id": 13788524,
            "zenodo_modified": "2024-09-23T04:40:53.613542+00:00",
            "zenodo_revision": 4,
            "zenodo_status": "published",
            "zenodo_access_right": "open",
            "zenodo_license_id": "cc-by-4.0",
            "zenodo_files": [
                {
                    "key": "Kumrai-T/DA_4DCTA-v1.0.1.zip",
                    "size": 1934055674,
                    "checksum": "md5:fd9f856b485983cd430ab94d01a24596",
                }
            ],
            "payload_or_manifest_files": [
                "Kumrai-T/DA_4DCTA-v1.0.1.zip"
            ],
            "availability": "zenodo_record_metadata_state",
        }
    ):
        raise SourceWatchContractError("da4dcta_zenodo_contract_changed")

    expected_entries = [
        {"name": "attention.py", "type": "file", "size": 3910},
        {"name": "constant_value.py", "type": "file", "size": 95},
        {"name": "feature.py", "type": "file", "size": 8800},
        {"name": "gui.py", "type": "file", "size": 25563},
        {"name": "io_utils.py", "type": "file", "size": 16392},
        {"name": "jupyter_notebook", "type": "dir", "size": 0},
        {"name": "LSTM_model.py", "type": "file", "size": 13061},
        {"name": "navi_feature.py", "type": "file", "size": 6195},
        {"name": "pipeline.py", "type": "file", "size": 42564},
        {"name": "PlotLosses.py", "type": "file", "size": 1687},
        {"name": "project.py", "type": "file", "size": 4433},
        {"name": "raw_data", "type": "dir", "size": 0},
        {"name": "viz_utils.py", "type": "file", "size": 42496},
    ]
    expected_material = [
        "LSTM_model.py",
        "PlotLosses.py",
        "attention.py",
        "constant_value.py",
        "feature.py",
        "gui.py",
        "io_utils.py",
        "jupyter_notebook",
        "navi_feature.py",
        "pipeline.py",
        "project.py",
        "raw_data",
        "viz_utils.py",
    ]
    if (
        github.get("watch_id")
        != "da4dcta_github_release_and_baseline_v1"
        or github.get("kind") != "github"
        or github.get("review_request") != "fresh_source_reaudit_only"
        or github.get("source")
        != {
            "repository": "Kumrai-T/DA_4DCTA",
            "repository_url": "https://github.com/Kumrai-T/DA_4DCTA",
            "default_branch": "main",
            "paper_url": "https://doi.org/10.7717/peerj.19393",
        }
        or github.get("frozen_snapshot")
        != {
            "main_head_sha": "8df7d45e9f65e3cbfd4ae3fc430c65a98905bdfc",
            "root_entries": expected_entries,
            "release_count": 1,
            "license_spdx_id": None,
            "repository_size_kib": 3598858,
            "payload_or_code_entries": expected_material,
            "availability": (
                "public_derived_trajectory_csv_and_code_without_source_dicom_"
                "rgb_video_registration_surface_or_fold_contract"
            ),
        }
    ):
        raise SourceWatchContractError("da4dcta_github_contract_changed")

    detection = payload.get("change_detection", {})
    if (
        detection.get(
            "derived_trajectory_csv_is_not_source_4dcta_or_intraoperative_reference"
        )
        is not True
        or detection.get(
            "visible_case_directory_is_not_verified_independent_patient"
        )
        is not True
        or detection.get(
            "source_wall_phenotype_result_is_not_aurora_reproduced_evidence"
        )
        is not True
        or detection.get("repository_license_absence_is_not_method_novelty")
        is not True
    ):
        raise SourceWatchContractError("v13_change_boundary_changed")


def _validate_v14(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 23:
        raise SourceWatchContractError("v14_watch_set_changed")
    _validate_v13(
        {
            "watches": watches[:20],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    zenodo, pipeline, multiclass = watches[20:]
    if (
        zenodo.get("watch_id") != "asah_segmentation_zenodo_asset_v1"
        or zenodo.get("kind") != "zenodo_record"
        or zenodo.get("review_request") != "fresh_source_reaudit_only"
        or zenodo.get("source")
        != {
            "zenodo_record_id": 8228847,
            "zenodo_api_url": "https://zenodo.org/api/records/8228847",
            "record_url": "https://zenodo.org/records/8228847",
        }
        or zenodo.get("frozen_snapshot")
        != {
            "zenodo_record_id": 8228847,
            "zenodo_modified": "2023-08-10T02:26:49.570302+00:00",
            "zenodo_revision": 2,
            "zenodo_status": "published",
            "zenodo_access_right": "open",
            "zenodo_license_id": "cc-by-4.0",
            "zenodo_files": [
                {
                    "key": "subarachnoid_hemorrhage_rhuh.rar",
                    "size": 648502298,
                    "checksum": "md5:a67bf358ebb326f156071864c318ab42",
                }
            ],
            "payload_or_manifest_files": ["subarachnoid_hemorrhage_rhuh.rar"],
            "availability": "zenodo_record_metadata_state",
        }
    ):
        raise SourceWatchContractError("asah_zenodo_contract_changed")

    pipeline_entries = [
        {"name": "ct_template2mni.nii.gz", "type": "file", "size": 7493552},
        {"name": "gui.py", "type": "file", "size": 4607},
        {"name": "inference_2.py", "type": "file", "size": 7210},
        {"name": "LICENSE", "type": "file", "size": 8829},
        {"name": "README.md", "type": "file", "size": 8981},
        {"name": "requirements.txt", "type": "file", "size": 299},
        {"name": "SAH_mortality_prediction.py", "type": "file", "size": 16943},
        {"name": "THIRDPARTYLICENSEREADME", "type": "file", "size": 9715},
        {"name": "unvrh.png", "type": "file", "size": 162458},
    ]
    pipeline_material = [
        "SAH_mortality_prediction.py",
        "THIRDPARTYLICENSEREADME",
        "ct_template2mni.nii.gz",
        "gui.py",
        "inference_2.py",
        "requirements.txt",
        "unvrh.png",
    ]
    if (
        pipeline.get("watch_id") != "asah_segmentation_mortality_code_v1"
        or pipeline.get("kind") != "github"
        or pipeline.get("review_request") != "fresh_source_reaudit_only"
        or pipeline.get("source")
        != {
            "repository": "smcch/Subarachnoid_Hemorrhage_segmentation_and_mortality_prediction",
            "repository_url": "https://github.com/smcch/Subarachnoid_Hemorrhage_segmentation_and_mortality_prediction",
            "default_branch": "main",
            "paper_url": "https://doi.org/10.3390/brainsci14010010",
        }
        or pipeline.get("frozen_snapshot")
        != {
            "main_head_sha": "3fbd7a9282287a719aff5f603e9539b7a886b373",
            "root_entries": pipeline_entries,
            "release_count": 0,
            "license_spdx_id": "NOASSERTION",
            "repository_size_kib": 54931,
            "payload_or_code_entries": pipeline_material,
            "availability": "public_pipeline_code_and_template_without_patient_mask_outcome_split_or_tracked_checkpoint",
        }
    ):
        raise SourceWatchContractError("asah_pipeline_contract_changed")

    if (
        multiclass.get("watch_id") != "asah_multiclass_baseline_release_v1"
        or multiclass.get("kind") != "github"
        or multiclass.get("review_request")
        != "direct_prior_baseline_feasibility_reaudit_only"
        or multiclass.get("source")
        != {
            "repository": "claim-berlin/Multiclass-Segmentation-of-Hemorrhages-in-CT",
            "repository_url": "https://github.com/claim-berlin/Multiclass-Segmentation-of-Hemorrhages-in-CT",
            "default_branch": "main",
            "paper_url": "https://doi.org/10.3389/fneur.2024.1490216",
        }
        or multiclass.get("frozen_snapshot")
        != {
            "main_head_sha": "269f4724fde89515eac8dbdac648925dc24bf492",
            "root_entries": [
                {"name": "demo_data", "type": "dir", "size": 0},
                {"name": "figures", "type": "dir", "size": 0},
                {"name": "LICENSE.md", "type": "file", "size": 17689},
                {"name": "nnUNET_results", "type": "dir", "size": 0},
                {"name": "README.md", "type": "file", "size": 3590},
            ],
            "release_count": 0,
            "license_spdx_id": "NOASSERTION",
            "repository_size_kib": 21981,
            "payload_or_code_entries": ["demo_data", "figures", "nnUNET_results"],
            "availability": "public_config_demo_and_weight_link_without_patient_or_outcome_join",
        }
    ):
        raise SourceWatchContractError("asah_multiclass_contract_changed")

    detection = payload.get("change_detection", {})
    if any(
        detection.get(key) is not True
        for key in (
            "open_mask_archive_is_not_joined_outcome_asset",
            "pipeline_code_is_not_patient_outcome_release",
            "public_weights_are_direct_prior_not_task_identity",
            "paper_cohort_count_is_not_archive_manifest",
        )
    ):
        raise SourceWatchContractError("v14_change_boundary_changed")


def _validate_v15(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 24:
        raise SourceWatchContractError("v15_watch_set_changed")
    _validate_v14(
        {
            "watches": watches[:23],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    synthetic = watches[23]
    expected_entries = [
        {"name": ".gitattributes", "type": "file", "size": 66},
        {"name": ".gitignore", "type": "file", "size": 190},
        {"name": "__init__.py", "type": "file", "size": 0},
        {"name": "analysis", "type": "dir", "size": 0},
        {"name": "CITATION.cff", "type": "file", "size": 1588},
        {"name": "config.py", "type": "file", "size": 11664},
        {"name": "data", "type": "dir", "size": 0},
        {"name": "LICENSE", "type": "file", "size": 1721},
        {"name": "main.py", "type": "file", "size": 16440},
        {"name": "README.md", "type": "file", "size": 15253},
        {"name": "requirements.txt", "type": "file", "size": 467},
        {"name": "run_pipeline.py", "type": "file", "size": 2132},
        {"name": "src", "type": "dir", "size": 0},
    ]
    expected_material = [
        ".gitattributes",
        ".gitignore",
        "__init__.py",
        "analysis",
        "config.py",
        "data",
        "main.py",
        "requirements.txt",
        "run_pipeline.py",
        "src",
    ]
    if (
        synthetic.get("watch_id") != "synthetic_aaa_cfd_material_release_v1"
        or synthetic.get("kind") != "github"
        or synthetic.get("review_request") != "fresh_source_reaudit_only"
        or synthetic.get("source")
        != {
            "repository": "Harish-Research-Lab/Synthetic-AAA-CFD-framework",
            "repository_url": "https://github.com/Harish-Research-Lab/Synthetic-AAA-CFD-framework",
            "default_branch": "main",
            "paper_url": "https://doi.org/10.64898/2026.02.27.708461",
            "zenodo_doi": "10.5281/zenodo.21435232",
            "release_tag": "v1.0.0",
            "release_tag_commit": "98363a0104701dcc4bea11c2ee808eed1febafbe",
        }
        or synthetic.get("frozen_snapshot")
        != {
            "main_head_sha": "7872b816f1803195bcb54524caeb715970bfdcc7",
            "root_entries": expected_entries,
            "release_count": 1,
            "license_spdx_id": "NOASSERTION",
            "repository_size_kib": 143619,
            "payload_or_code_entries": expected_material,
            "availability": (
                "public_mit_generator_and_openfoam_pipeline_without_committed_"
                "generated_population_or_transient_field_cohort"
            ),
        }
    ):
        raise SourceWatchContractError("synthetic_aaa_contract_changed")

    detection = payload.get("change_detection", {})
    if any(
        detection.get(key) is not True
        for key in (
            "doi_badge_only_commit_is_not_material_asset_change",
            "generator_code_is_not_generated_cohort_or_transient_field_asset",
            "surface_vector_reentry_requires_whitelisted_material_change",
        )
    ):
        raise SourceWatchContractError("v15_change_boundary_changed")


def _validate_v16(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 27:
        raise SourceWatchContractError("v16_watch_set_changed")
    _validate_v15(
        {
            "watches": watches[:24],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    graph_physics, wss_transolver, expigeo = watches[24:]
    expected = [
        (
            graph_physics,
            "graph_physics_spatiotemporal_direct_prior_v1",
            "DonsetPG/graph-physics",
            "main",
            "e4ac523d749b126f504665fb6270fcb91ac3cbd2",
            None,
            1401089,
            [
                ".github", ".gitignore", "dataset_config", "graphphysics",
                "jraphphysics", "Makefile", "mock_training.json", "predict.sh",
                "requirements.txt", "retrain.sh", "setup.py", "tests",
                "train.sh", "training_config",
            ],
        ),
        (
            wss_transolver,
            "aneurysm_wss_transolver_direct_prior_v1",
            "IsaacLin247/aneurysm-wss-transolver",
            "master",
            "3087fc9b8370ad39db85db9a61315bb34bf43cbb",
            "NOASSERTION",
            1843,
            [".gitignore", "RESULTS.md", "audit", "configs", "reports", "scripts", "src"],
        ),
        (
            expigeo,
            "expigeo_geometry_gnn_direct_prior_v1",
            "mohamedaminelayachi/EXPIGEO",
            "main",
            "b28736842ec521641ea9389e4a9a58bccc5616f3",
            "MIT",
            13817,
            ["assets", "expigeo", "pyproject.toml", "uv.lock"],
        ),
    ]
    for watch, watch_id, repository, branch, head, license_id, size, material in expected:
        source = watch.get("source", {})
        snapshot = watch.get("frozen_snapshot", {})
        if (
            watch.get("watch_id") != watch_id
            or watch.get("kind") != "github"
            or watch.get("review_request")
            != "direct_prior_baseline_feasibility_reaudit_only"
            or source.get("repository") != repository
            or source.get("repository_url") != f"https://github.com/{repository}"
            or source.get("default_branch") != branch
            or snapshot.get("main_head_sha") != head
            or snapshot.get("release_count") != 0
            or snapshot.get("license_spdx_id") != license_id
            or snapshot.get("repository_size_kib") != size
            or snapshot.get("payload_or_code_entries") != material
            or snapshot.get("availability")
            != "public_direct_prior_code_without_aurora_task_or_compute_authority"
        ):
            raise SourceWatchContractError("v16_direct_prior_contract_changed")

    detection = payload.get("change_detection", {})
    if any(
        detection.get(key) is not True
        for key in (
            "direct_prior_code_is_not_material_task_asset",
            "public_patientwise_folds_are_not_new_task_novelty",
            "derived_wss_magnitude_is_not_transient_vector_ground_truth",
        )
    ):
        raise SourceWatchContractError("v16_change_boundary_changed")


def _validate_v17(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 28:
        raise SourceWatchContractError("v17_watch_set_changed")
    _validate_v16(
        {
            "watches": watches[:27],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    synthetic_dsa = watches[27]
    if (
        synthetic_dsa.get("watch_id")
        != "synthetic_cerebral_dsa_reader_study_embargo_v1"
        or synthetic_dsa.get("kind") != "zenodo_record"
        or synthetic_dsa.get("review_request") != "fresh_source_reaudit_only"
        or synthetic_dsa.get("source")
        != {
            "zenodo_record_id": 21104782,
            "zenodo_api_url": "https://zenodo.org/api/records/21104782",
            "record_url": "https://zenodo.org/records/21104782",
            "paper_url": "https://arxiv.org/abs/2602.11703",
        }
        or synthetic_dsa.get("frozen_snapshot")
        != {
            "zenodo_record_id": 21104782,
            "zenodo_modified": "2026-07-01T16:41:29.664703+00:00",
            "zenodo_revision": 4,
            "zenodo_status": "published",
            "zenodo_access_right": "embargoed",
            "zenodo_license_id": "cc-by-4.0",
            "zenodo_files": [],
            "payload_or_manifest_files": [],
            "availability": "zenodo_record_metadata_state",
        }
    ):
        raise SourceWatchContractError("synthetic_dsa_embargo_contract_changed")

    detection = payload.get("change_detection", {})
    if any(
        detection.get(key) is not True
        for key in (
            "embargo_lift_is_not_automatic_asset_admission",
            "synthetic_png_is_not_patient_pair_or_downstream_task_reference",
        )
    ):
        raise SourceWatchContractError("v17_change_boundary_changed")


def _validate_v18(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 31:
        raise SourceWatchContractError("v18_watch_set_changed")
    _validate_v17(
        {
            "watches": watches[:28],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    adam_folds, dino_3dra, geop2v = watches[28:]

    fold_root = sorted(
        [
            {"name": "README.md", "type": "file", "size": 6209},
            {
                "name": "folds_data_organization.json",
                "type": "file",
                "size": 12859,
            },
        ],
        key=lambda item: item["name"].lower(),
    )
    if (
        adam_folds.get("watch_id") != "adam_patch_fold_release_contract_v1"
        or adam_folds.get("kind") != "github_release_asset_contract"
        or adam_folds.get("review_request") != "fresh_source_reaudit_only"
        or adam_folds.get("source")
        != {
            "repository": "josedaviddr/Aneurysm_segmentation_DataSet_folds",
            "repository_url": (
                "https://github.com/josedaviddr/"
                "Aneurysm_segmentation_DataSet_folds"
            ),
            "default_branch": "main",
            "release_tag": "v1.0",
            "dataset_name": "ADAM",
            "manifest_path": "folds_data_organization.json",
        }
        or adam_folds.get("frozen_snapshot")
        != {
            "main_head_sha": "d36df7d19a96aa5b9fca0cc9050e021ac7319fee",
            "root_entries": fold_root,
            "release_count": 1,
            "license_spdx_id": None,
            "repository_size_kib": 10,
            "payload_or_code_entries": ["folds_data_organization.json"],
            "release_id": 349278633,
            "release_tag": "v1.0",
            "release_target_commitish": "main",
            "release_published_at": "2026-07-06T00:50:46Z",
            "release_asset_count": 35,
            "release_asset_total_bytes": 61506611200,
            "release_asset_manifest_sha256": (
                "7d5ebe80859b4d781a13a3c1b65d3b18fb2dfa2bd13486bb64c36b980b133f9c"
            ),
            "availability": "public_github_release_asset_contract",
        }
    ):
        raise SourceWatchContractError("adam_patch_fold_release_contract_changed")

    dino_root = sorted(
        [
            {"name": ".DS_Store", "type": "file", "size": 8196},
            {"name": ".gitattributes", "type": "file", "size": 108},
            {"name": "LICENSE", "type": "file", "size": 1066},
            {"name": "README.md", "type": "file", "size": 10617},
            {"name": "__pycache__", "type": "dir", "size": 0},
            {"name": "conda_env_backup", "type": "dir", "size": 0},
            {"name": "data", "type": "dir", "size": 0},
            {"name": "dino3dra_config.py", "type": "file", "size": 5212},
            {
                "name": "dino3dra_inference_inference.ipynb",
                "type": "file",
                "size": 33952,
            },
            {"name": "dino3dra_utils.py", "type": "file", "size": 7145},
            {"name": "dino_3dra_net.py", "type": "file", "size": 33826},
            {"name": "dino_backbone.py", "type": "file", "size": 30159},
            {"name": "dino_inference_v2.py", "type": "file", "size": 32514},
            {
                "name": "dino_postprocessing_v2.py",
                "type": "file",
                "size": 45640,
            },
            {
                "name": "dino_preprocessing_v2.py",
                "type": "file",
                "size": 13591,
            },
            {"name": "fapm_3d.py", "type": "file", "size": 34635},
            {
                "name": "visualize_3dra_notebook.py",
                "type": "file",
                "size": 21930,
            },
            {"name": "weight", "type": "dir", "size": 0},
        ],
        key=lambda item: item["name"].lower(),
    )
    geo_root = sorted(
        [
            {"name": "LICENSE", "type": "file", "size": 8960},
            {"name": "README.md", "type": "file", "size": 6810},
            {"name": "assets", "type": "dir", "size": 0},
            {"name": "configs", "type": "dir", "size": 0},
            {"name": "geop2vnet", "type": "dir", "size": 0},
            {"name": "requirements.txt", "type": "file", "size": 332},
            {"name": "scripts", "type": "dir", "size": 0},
            {"name": "setup.py", "type": "file", "size": 1470},
            {"name": "tools", "type": "dir", "size": 0},
        ],
        key=lambda item: item["name"].lower(),
    )
    direct_priors = [
        (
            dino_3dra,
            "dino_3dra_foundation_segmentation_direct_prior_v1",
            "JiayangDS/Dino3DRA",
            "5d9982ee794b531a8f04e73e849af0040976381f",
            "MIT",
            57013,
            dino_root,
            [
                ".DS_Store", ".gitattributes", "__pycache__",
                "conda_env_backup", "data", "dino3dra_config.py",
                "dino3dra_inference_inference.ipynb", "dino3dra_utils.py",
                "dino_3dra_net.py", "dino_backbone.py", "dino_inference_v2.py",
                "dino_postprocessing_v2.py", "dino_preprocessing_v2.py",
                "fapm_3d.py", "visualize_3dra_notebook.py", "weight",
            ],
            (
                "public_direct_prior_inference_code_sample_case_and_lfs_pointer_"
                "without_training_or_fold_contract"
            ),
        ),
        (
            geop2v,
            "geop2vnet_geometry_voxel_segmentation_direct_prior_v1",
            "somtiannes/GeoP2VNet",
            "25c59bc172d0fedac37c1b6cfc8fe4af0823bf65",
            "NOASSERTION",
            951,
            geo_root,
            [
                "assets", "configs", "geop2vnet", "requirements.txt",
                "scripts", "setup.py", "tools",
            ],
            "public_direct_prior_code_without_clinical_data_or_checkpoint",
        ),
    ]
    for (
        watch, watch_id, repository, head, license_id, size, root, material,
        availability,
    ) in direct_priors:
        source = watch.get("source", {})
        snapshot = watch.get("frozen_snapshot", {})
        if (
            watch.get("watch_id") != watch_id
            or watch.get("kind") != "github"
            or watch.get("review_request")
            != "direct_prior_baseline_feasibility_reaudit_only"
            or source.get("repository") != repository
            or source.get("repository_url") != f"https://github.com/{repository}"
            or source.get("default_branch") != "main"
            or snapshot.get("main_head_sha") != head
            or snapshot.get("root_entries") != root
            or snapshot.get("release_count") != 0
            or snapshot.get("license_spdx_id") != license_id
            or snapshot.get("repository_size_kib") != size
            or snapshot.get("payload_or_code_entries") != material
            or snapshot.get("availability") != availability
        ):
            raise SourceWatchContractError("v18_segmentation_prior_contract_changed")

    detection = payload.get("change_detection", {})
    if any(
        detection.get(key) is not True
        for key in (
            "release_asset_manifest_is_not_dataset_provenance_or_license",
            "patch_fold_label_is_not_patient_grouped_outer_test",
            "same_subject_timepoints_must_not_cross_development_and_test",
            "repository_reported_result_is_not_peer_review_or_aurora_evidence",
        )
    ):
        raise SourceWatchContractError("v18_change_boundary_changed")


def _validate_v19(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 32:
        raise SourceWatchContractError("v19_watch_set_changed")
    _validate_v18(
        {
            "watches": watches[:31],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    challenge = watches[31]
    expected_root = sorted(
        [
            {"name": "ChallengeDataFormat", "type": "dir", "size": 0},
            {"name": "CMRx4DFlowMaskGeneration", "type": "dir", "size": 0},
            {"name": "CMRx4DFlowReconDemo", "type": "dir", "size": 0},
            {"name": "Intro2026.gif", "type": "file", "size": 13806069},
            {"name": "README.md", "type": "file", "size": 10701},
            {"name": "Submission", "type": "dir", "size": 0},
            {"name": "TaskImage2026.png", "type": "file", "size": 1500447},
        ],
        key=lambda item: item["name"].lower(),
    )
    if (
        challenge.get("watch_id")
        != "cmrx4dflow2026_embargoed_challenge_code_v1"
        or challenge.get("kind") != "github"
        or challenge.get("review_request") != "fresh_source_reaudit_only"
        or challenge.get("source")
        != {
            "repository": "CmrxRecon/CMRx4DFlow2026",
            "repository_url": "https://github.com/CmrxRecon/CMRx4DFlow2026",
            "default_branch": "main",
            "challenge_url": "https://cmrxrecon.github.io/CMRx4DFlow2026/",
        }
        or challenge.get("frozen_snapshot")
        != {
            "main_head_sha": "f6f835f34b86464256e3ce4362e7831325f32590",
            "root_entries": expected_root,
            "release_count": 0,
            "license_spdx_id": None,
            "repository_size_kib": 36729,
            "payload_or_code_entries": [
                "ChallengeDataFormat",
                "CMRx4DFlowMaskGeneration",
                "CMRx4DFlowReconDemo",
                "Intro2026.gif",
                "Submission",
                "TaskImage2026.png",
            ],
            "availability": (
                "public_challenge_code_only_controlled_data_embargo_after_"
                "isbi_deadline"
            ),
        }
    ):
        raise SourceWatchContractError("cmrx4dflow2026_contract_changed")

    detection = payload.get("change_detection", {})
    if any(
        detection.get(key) is not True
        for key in (
            "challenge_code_is_not_data_access",
            "embargo_after_submission_deadline_is_not_current_asset",
            "challenge_registration_is_not_automatic_terms_acceptance",
            "multi_organ_case_count_is_not_aneurysm_patient_count",
        )
    ):
        raise SourceWatchContractError("v19_change_boundary_changed")


def _validate_v20(payload: Mapping[str, Any]) -> None:
    watches = payload.get("watches", [])
    if not isinstance(watches, list) or len(watches) != 33:
        raise SourceWatchContractError("v20_watch_set_changed")
    _validate_v19(
        {
            "watches": watches[:32],
            "change_detection": payload.get("change_detection", {}),
        }
    )
    release = watches[32]
    if (
        release.get("watch_id")
        != "cathaction_intervention_release_contract_v1"
        or release.get("kind") != "huggingface_intervention_release"
        or release.get("review_request") != "fresh_source_reaudit_only"
        or release.get("source")
        != {
            "dataset_api_url": "https://huggingface.co/api/datasets/airvlab/CathAction",
            "dataset_url": "https://huggingface.co/datasets/airvlab/CathAction",
            "paper_url": "https://arxiv.org/abs/2408.13126",
            "challenge_url": "https://endomiccai.github.io/cathation/",
        }
        or release.get("frozen_snapshot")
        != {
            "sha": "8b04056f0f4fa4b04d8454728f000730af0d5560",
            "last_modified": "2026-05-18T11:16:32Z",
            "private": False,
            "gated": False,
            "disabled": False,
            "license_tags": ["license:cc-by-nc-sa-4.0"],
            "used_storage_bytes": 56678352136,
            "sibling_count": 6,
            "siblings_sha256": (
                "30fdaad6d32078ffcb4c0b5bca83e4de0154162b52a4720be910cdbb0548bcb4"
            ),
            "archive_entries": [
                "collision_detection.zip",
                "segmentation_animal_phantom.zip",
                "segmentation_human_train.zip",
                "video_action_understanding.zip",
            ],
            "human_segmentation_archive_present": True,
            "human_collision_archive_present": False,
            "availability": (
                "public_metadata_and_large_archives_card_requests_download_form_"
                "and_license_agreement_independent_unit_onset_horizon_and_cross_"
                "archive_join_unresolved"
            ),
        }
    ):
        raise SourceWatchContractError("cathaction_release_contract_changed")

    detection = payload.get("change_detection", {})
    if any(
        detection.get(key) is not True
        for key in (
            "human_segmentation_is_not_human_collision_evidence",
            "frame_count_is_not_independent_procedure_or_specimen_count",
            "current_frame_collision_detection_is_not_precontact_anticipation",
            "cross_archive_join_must_be_explicit_and_immutable",
        )
    ):
        raise SourceWatchContractError("v20_change_boundary_changed")


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


def fetch_github_release_asset_contract_snapshot(
    repository: str, branch: str, release_tag: str
) -> dict[str, Any]:
    """Read a GitHub repository and one release's asset metadata only."""

    snapshot = fetch_github_snapshot(repository, branch)
    base = f"https://api.github.com/repos/{repository}"
    release = _json_get(f"{base}/releases/tags/{release_tag}", github=True)
    assets = sorted(
        [
            {
                "name": str(item.get("name", "")),
                "size": int(item.get("size", 0)),
                "digest": item.get("digest"),
                "content_type": item.get("content_type"),
                "state": item.get("state"),
            }
            for item in release.get("assets", [])
        ],
        key=lambda item: item["name"],
    )
    manifest = (json.dumps(assets, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    return {
        **snapshot,
        "release_id": int(release.get("id", 0)),
        "release_tag": str(release.get("tag_name", "")),
        "release_target_commitish": str(release.get("target_commitish", "")),
        "release_published_at": str(release.get("published_at", "")),
        "release_asset_count": len(assets),
        "release_asset_total_bytes": sum(item["size"] for item in assets),
        "release_asset_manifest_sha256": _sha256(manifest),
        "availability": "public_github_release_asset_contract",
    }


def fetch_github_versioned_release_contract_snapshot(
    repository_api_url: str,
    default_branch: str,
    batch1_anchor_commit: str,
    release_prefix: str,
) -> dict[str, Any]:
    """Read only Git object metadata for a versioned public release contract."""

    base = repository_api_url.rstrip("/")

    def commit_and_tree(ref: str) -> tuple[Mapping[str, Any], list[Mapping[str, Any]]]:
        commit = _json_get(f"{base}/commits/{ref}", github=True)
        root_tree_sha = str(commit.get("commit", {}).get("tree", {}).get("sha", ""))
        tree = _json_get(
            f"{base}/git/trees/{root_tree_sha}?recursive=1", github=True
        )
        entries = tree.get("tree", [])
        if not root_tree_sha or not isinstance(entries, list):
            raise SourceWatchContractError("unexpected_github_tree_response")
        return commit, entries

    current_commit, current_tree = commit_and_tree(default_branch)
    batch1_commit, batch1_tree = commit_and_tree(batch1_anchor_commit)

    def entry(
        entries: Sequence[Mapping[str, Any]], path: str
    ) -> Mapping[str, Any]:
        matches = [item for item in entries if item.get("path") == path]
        if len(matches) != 1:
            raise SourceWatchContractError(f"github_release_entry_missing:{path}")
        return matches[0]

    def blob(entries: Sequence[Mapping[str, Any]], path: str) -> dict[str, Any]:
        item = entry(entries, path)
        if item.get("type") != "blob":
            raise SourceWatchContractError(f"github_release_not_blob:{path}")
        return {"sha": str(item.get("sha", "")), "size": int(item.get("size", 0))}

    def manifest_counts(entries: Sequence[Mapping[str, Any]]) -> dict[str, int]:
        prefixes = {
            "image_checksum_count": f"{release_prefix}images/",
            "location_json_count": f"{release_prefix}location_jsons/",
            "location_mask_checksum_count": f"{release_prefix}location_masks/",
            "type_mask_checksum_count": f"{release_prefix}type_masks/",
            "vessel_mask_checksum_count": f"{release_prefix}vessel_masks/",
        }
        return {
            key: sum(
                item.get("type") == "blob"
                and str(item.get("path", "")).startswith(prefix)
                for item in entries
            )
            for key, prefix in prefixes.items()
        }

    release_path = release_prefix.rstrip("/")
    current_release = entry(current_tree, release_path)
    batch1_release = entry(batch1_tree, release_path)
    if current_release.get("type") != "tree" or batch1_release.get("type") != "tree":
        raise SourceWatchContractError("github_release_prefix_not_tree")

    current_root_tree_sha = str(
        current_commit.get("commit", {}).get("tree", {}).get("sha", "")
    )
    batch1_root_tree_sha = str(
        batch1_commit.get("commit", {}).get("tree", {}).get("sha", "")
    )
    return {
        "main_head_sha": str(current_commit.get("sha", "")),
        "main_root_tree_sha": current_root_tree_sha,
        "current_release_tree_sha": str(current_release.get("sha", "")),
        "readme_blob": blob(current_tree, f"{release_prefix}README.md"),
        "changelog_blob": blob(current_tree, f"{release_prefix}CHANGELOG.txt"),
        "terms_blob": blob(current_tree, f"{release_prefix}Terms_of_use.txt"),
        "current_manifest_counts": manifest_counts(current_tree),
        "batch1_anchor_commit": str(batch1_commit.get("sha", "")),
        "batch1_root_tree_sha": batch1_root_tree_sha,
        "batch1_release_tree_sha": str(batch1_release.get("sha", "")),
        "batch1_manifest_counts": manifest_counts(batch1_tree),
        "availability": (
            "public_versioned_git_manifest_and_annotation_metadata_"
            "without_medical_payload_access_or_terms_acceptance"
        ),
    }


def fetch_github_registry_wiki_contract_snapshot(
    registry_contents_api_url: str,
    registry_commits_api_url: str,
    wiki_raw_url: str,
) -> dict[str, Any]:
    """Read public release-document metadata without requesting medical data."""

    contents = _json_get(registry_contents_api_url, github=True)
    commits = _json_get(registry_commits_api_url, github=True)
    if (
        not isinstance(contents, Mapping)
        or not isinstance(commits, list)
        or not commits
    ):
        raise SourceWatchContractError("unexpected_registry_contract_response")
    download_url = contents.get("download_url")
    if not isinstance(download_url, str) or not download_url:
        raise SourceWatchContractError("registry_contract_download_url_missing")

    registry_payload = _url_get(download_url, "text/plain")
    wiki_payload = _url_get(wiki_raw_url, "text/plain")
    registry_text = registry_payload.decode("utf-8")
    wiki_text = wiki_payload.decode("utf-8")

    controlled = "ControlledAccess:" in registry_text
    forthcoming = "forthcoming Data Resource Publication" in registry_text
    restricted_terms = (
        "for non-commercial purposes only" in registry_text
        and "You may not share or redistribute" in registry_text
    )
    wiki_coming_soon = wiki_text.strip() == "Coming soon"
    machine_contract = not wiki_coming_soon and all(
        token in wiki_text.lower()
        for token in ("manifest", "patient", "annotation", "split")
    )
    return {
        "registry_file_commit_sha": str(commits[0].get("sha", "")),
        "registry_blob_sha": str(contents.get("sha", "")),
        "registry_file_bytes": int(contents.get("size", 0)),
        "registry_file_sha256": _sha256(registry_payload),
        "controlled_access_declared": controlled,
        "data_resource_publication_forthcoming": forthcoming,
        "noncommercial_no_redistribution_terms_declared": restricted_terms,
        "wiki_page_bytes": len(wiki_payload),
        "wiki_page_sha256": _sha256(wiki_payload),
        "wiki_page_is_coming_soon_only": wiki_coming_soon,
        "machine_auditable_release_contract_present": machine_contract,
        "availability": (
            "controlled_access_registry_with_forthcoming_publication_and_"
            "coming_soon_wiki_without_machine_auditable_release_contract"
            if controlled and forthcoming and wiki_coming_soon and not machine_contract
            else "rsna_release_contract_state_changed"
        ),
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


def fetch_huggingface_revision_snapshot(dataset_api_url: str) -> dict[str, Any]:
    """Fetch revision/access metadata without treating the file list as payload."""
    metadata = _json_get(dataset_api_url)
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
        "used_storage_bytes": int(metadata.get("usedStorage", 0)),
        "availability": "public_synthetic_transient_wss_payload_exact_revision",
    }


def fetch_huggingface_intervention_release_snapshot(
    dataset_api_url: str,
) -> dict[str, Any]:
    """Fetch CathAction release metadata without opening any archive payload."""
    metadata = _json_get(dataset_api_url)
    siblings = sorted(
        str(item.get("rfilename"))
        for item in metadata.get("siblings", [])
        if item.get("rfilename")
    )
    archive_entries = sorted(name for name in siblings if name.endswith(".zip"))
    sibling_manifest = ("\n".join(siblings) + "\n").encode("utf-8")
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
        "used_storage_bytes": int(metadata.get("usedStorage", 0)),
        "sibling_count": len(siblings),
        "siblings_sha256": _sha256(sibling_manifest),
        "archive_entries": archive_entries,
        "human_segmentation_archive_present": (
            "segmentation_human_train.zip" in archive_entries
        ),
        "human_collision_archive_present": any(
            "human" in name.lower() and "collision" in name.lower()
            for name in archive_entries
        ),
        "availability": (
            "public_metadata_and_large_archives_card_requests_download_form_"
            "and_license_agreement_independent_unit_onset_horizon_and_cross_"
            "archive_join_unresolved"
        ),
    }


def fetch_huggingface_under_review_snapshot(
    dataset_api_url: str,
) -> dict[str, Any]:
    """Read card and inventory metadata without opening Arrow or image payloads."""
    metadata = _json_get(dataset_api_url)
    siblings = sorted(
        str(item.get("rfilename"))
        for item in metadata.get("siblings", [])
        if item.get("rfilename")
    )
    sibling_manifest = ("\n".join(siblings) + "\n").encode("utf-8")
    description_text = str(metadata.get("description", ""))
    description = description_text.encode("utf-8")
    return {
        "sha": str(metadata.get("sha", "")),
        "created_at": str(metadata.get("createdAt", "")),
        "last_modified": str(metadata.get("lastModified", "")),
        "private": bool(metadata.get("private", False)),
        "gated": metadata.get("gated", False),
        "disabled": bool(metadata.get("disabled", False)),
        "license_tags": sorted(
            str(tag)
            for tag in metadata.get("tags", [])
            if str(tag).startswith("license:")
        ),
        "used_storage_bytes": int(metadata.get("usedStorage", 0)),
        "description_sha256": _sha256(description),
        "sibling_count": len(siblings),
        "siblings_sha256": _sha256(sibling_manifest),
        "arrow_shard_count": sum(name.endswith(".arrow") for name in siblings),
        "under_review_release_statement_present": (
            "double-blind review" in description_text.lower()
            and "detailed metadata" in description_text.lower()
        ),
        "availability": (
            "public_arrow_payload_under_review_without_detailed_metadata_"
            "split_or_source_lineage"
        ),
    }


def fetch_huggingface_aneux_transient_snapshot(
    dataset_api_url: str,
) -> dict[str, Any]:
    """Read the gated record's public API metadata without opening a member."""
    metadata = _json_get(dataset_api_url)
    siblings = sorted(
        str(item.get("rfilename"))
        for item in metadata.get("siblings", [])
        if item.get("rfilename")
    )
    topology_cases: dict[str, set[str]] = {
        "aneux_bifurcation_shapes": set(),
        "aneux_sidewall_shapes": set(),
    }
    extension_counts: dict[str, int] = {}
    for name in siblings:
        suffix = Path(name).suffix
        extension_counts[suffix] = extension_counts.get(suffix, 0) + 1
        parts = name.split("/")
        if len(parts) >= 3 and parts[0] in topology_cases:
            topology_cases[parts[0]].add(parts[1])

    bifurcation = topology_cases["aneux_bifurcation_shapes"]
    sidewall = topology_cases["aneux_sidewall_shapes"]
    topology_manifest = sorted(
        [f"bifurcation|{case_id}" for case_id in bifurcation]
        + [f"sidewall|{case_id}" for case_id in sidewall]
    )
    unique_ids = sorted(bifurcation | sidewall)
    sibling_manifest = ("\n".join(siblings) + "\n").encode("utf-8")
    topology_manifest_bytes = ("\n".join(topology_manifest) + "\n").encode(
        "utf-8"
    )
    unique_manifest = ("\n".join(unique_ids) + "\n").encode("utf-8")
    description = str(metadata.get("description", "")).encode("utf-8")
    return {
        "sha": str(metadata.get("sha", "")),
        "created_at": str(metadata.get("createdAt", "")),
        "last_modified": str(metadata.get("lastModified", "")),
        "private": bool(metadata.get("private", False)),
        "gated": metadata.get("gated", False),
        "disabled": bool(metadata.get("disabled", False)),
        "license_tags": sorted(
            str(tag)
            for tag in metadata.get("tags", [])
            if str(tag).startswith("license:")
        ),
        "used_storage_bytes": int(metadata.get("usedStorage", 0)),
        "description_sha256": _sha256(description),
        "sibling_count": len(siblings),
        "siblings_sha256": _sha256(sibling_manifest),
        "bifurcation_case_folders": len(bifurcation),
        "sidewall_case_folders": len(sidewall),
        "unique_visible_case_ids": len(unique_ids),
        "cross_topology_overlap_ids": sorted(bifurcation & sidewall),
        "topology_case_manifest_sha256": _sha256(topology_manifest_bytes),
        "unique_id_manifest_sha256": _sha256(unique_manifest),
        "extension_counts": dict(sorted(extension_counts.items())),
        "availability": "manual_gated_aneux_derived_transient_cfd_metadata_only",
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


def fetch_zenodo_record_snapshot(zenodo_api_url: str) -> dict[str, Any]:
    """Fetch a Zenodo record's immutable metadata and file manifest only."""
    record = _json_get(zenodo_api_url)
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
    access_right = str(metadata.get("access_right", ""))
    record_id = int(record.get("id", 0))
    if record_id == 19455127:
        availability = "public_cycle_averaged_wss_vtp_archive_exact_revision"
    elif record_id == 6801398 and access_right == "restricted" and not files:
        availability = "restricted_metadata_only_no_public_files"
    elif record_id == 16878417:
        availability = (
            "open_metadata_with_custom_clickthrough_terms_"
            "and_unopened_patient_payload"
        )
    elif record_id == 20158639:
        availability = "open_podium_docker_metadata_exact_revision"
    else:
        availability = "zenodo_record_metadata_state"
    return {
        "zenodo_record_id": record_id,
        "zenodo_modified": str(record.get("modified", "")),
        "zenodo_revision": int(record.get("revision", 0)),
        "zenodo_status": str(record.get("status", "")),
        "zenodo_access_right": access_right,
        "zenodo_license_id": license_info.get("id"),
        "zenodo_files": files,
        "payload_or_manifest_files": _zenodo_payload_or_manifest_files(files),
        "availability": availability,
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
            triggered = result["fresh_source_reaudit_triggered"]
            result["next_action"] = (
                watch["review_request"]
                if triggered
                else "continue_watch_only"
            )
            result["manual_review_triggered"] = triggered
            result["review_request"] = watch["review_request"]
            if (
                watch["review_request"]
                == "direct_prior_baseline_feasibility_reaudit_only"
            ):
                result["fresh_source_reaudit_triggered"] = False
                result[
                    "direct_prior_baseline_feasibility_reaudit_triggered"
                ] = triggered
        return result
    if watch.get("kind") == "github_release_asset_contract":
        frozen = watch["frozen_snapshot"]
        signal_names = {
            "main_head_sha": "github_release_repository_head_changed",
            "root_entries": "github_release_root_manifest_changed",
            "release_count": "github_release_count_changed",
            "license_spdx_id": "github_release_license_changed",
            "repository_size_kib": "github_release_repository_size_changed",
            "payload_or_code_entries": "github_release_material_entries_changed",
            "release_id": "github_release_identity_changed",
            "release_tag": "github_release_tag_changed",
            "release_target_commitish": "github_release_target_changed",
            "release_published_at": "github_release_publication_time_changed",
            "release_asset_count": "github_release_asset_count_changed",
            "release_asset_total_bytes": "github_release_asset_bytes_changed",
            "release_asset_manifest_sha256": "github_release_asset_manifest_changed",
            "availability": "github_release_availability_changed",
        }
        signals = [
            signal
            for key, signal in signal_names.items()
            if observed.get(key) != frozen.get(key)
        ]
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
    if watch.get("kind") == "github_versioned_release_contract":
        frozen = watch["frozen_snapshot"]
        signal_names = {
            "main_head_sha": "github_release_head_changed",
            "main_root_tree_sha": "github_root_tree_changed",
            "current_release_tree_sha": "github_release_tree_changed",
            "readme_blob": "github_release_readme_changed",
            "changelog_blob": "github_release_changelog_changed",
            "terms_blob": "github_release_terms_changed",
            "current_manifest_counts": "github_release_manifest_counts_changed",
            "batch1_anchor_commit": "github_batch1_anchor_changed",
            "batch1_root_tree_sha": "github_batch1_root_tree_changed",
            "batch1_release_tree_sha": "github_batch1_release_tree_changed",
            "batch1_manifest_counts": "github_batch1_manifest_counts_changed",
            "availability": "github_release_availability_changed",
        }
        signals = [
            signal
            for key, signal in signal_names.items()
            if observed.get(key) != frozen.get(key)
        ]
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
    if watch.get("kind") == "github_registry_wiki_contract":
        frozen = watch["frozen_snapshot"]
        signal_names = {
            "registry_file_commit_sha": "registry_file_commit_changed",
            "registry_blob_sha": "registry_blob_changed",
            "registry_file_bytes": "registry_file_size_changed",
            "registry_file_sha256": "registry_file_content_changed",
            "controlled_access_declared": "controlled_access_state_changed",
            "data_resource_publication_forthcoming": (
                "data_resource_publication_state_changed"
            ),
            "noncommercial_no_redistribution_terms_declared": (
                "registry_terms_state_changed"
            ),
            "wiki_page_bytes": "wiki_page_size_changed",
            "wiki_page_sha256": "wiki_page_content_changed",
            "wiki_page_is_coming_soon_only": "wiki_release_state_changed",
            "machine_auditable_release_contract_present": (
                "machine_auditable_release_contract_state_changed"
            ),
            "availability": "rsna_release_contract_availability_changed",
        }
        signals = [
            signal
            for key, signal in signal_names.items()
            if observed.get(key) != frozen.get(key)
        ]
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
    if watch.get("kind") == "huggingface_revision":
        frozen = watch["frozen_snapshot"]
        signals: list[str] = []
        for key, signal in (
            ("sha", "huggingface_revision_changed"),
            ("last_modified", "huggingface_last_modified_changed"),
            ("license_tags", "huggingface_license_changed"),
            ("used_storage_bytes", "huggingface_storage_size_changed"),
        ):
            if observed.get(key) != frozen.get(key):
                signals.append(signal)
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
    if watch.get("kind") == "huggingface_intervention_release":
        frozen = watch["frozen_snapshot"]
        signal_names = {
            "sha": "huggingface_revision_changed",
            "last_modified": "huggingface_last_modified_changed",
            "private": "huggingface_private_state_changed",
            "gated": "huggingface_gated_state_changed",
            "disabled": "huggingface_disabled_state_changed",
            "license_tags": "huggingface_license_changed",
            "used_storage_bytes": "huggingface_storage_size_changed",
            "sibling_count": "huggingface_file_count_changed",
            "siblings_sha256": "huggingface_file_inventory_changed",
            "archive_entries": "huggingface_archive_inventory_changed",
            "human_segmentation_archive_present": (
                "human_segmentation_archive_state_changed"
            ),
            "human_collision_archive_present": "human_collision_archive_state_changed",
            "availability": "huggingface_release_availability_changed",
        }
        signals = [
            signal
            for key, signal in signal_names.items()
            if observed.get(key) != frozen.get(key)
        ]
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
    if watch.get("kind") == "huggingface_under_review_dataset":
        frozen = watch["frozen_snapshot"]
        signals: list[str] = []
        for key, signal in (
            ("sha", "huggingface_revision_changed"),
            ("created_at", "huggingface_created_at_changed"),
            ("last_modified", "huggingface_last_modified_changed"),
            ("license_tags", "huggingface_license_changed"),
            ("used_storage_bytes", "huggingface_storage_size_changed"),
            ("description_sha256", "huggingface_dataset_card_changed"),
            ("sibling_count", "huggingface_file_count_changed"),
            ("siblings_sha256", "huggingface_file_inventory_changed"),
            ("arrow_shard_count", "huggingface_arrow_shard_count_changed"),
            (
                "under_review_release_statement_present",
                "huggingface_under_review_statement_changed",
            ),
        ):
            if observed.get(key) != frozen.get(key):
                signals.append(signal)
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
    if watch.get("kind") == "huggingface_aneux_transient_revision":
        frozen = watch["frozen_snapshot"]
        signals: list[str] = []
        for key, signal in (
            ("sha", "huggingface_revision_changed"),
            ("last_modified", "huggingface_last_modified_changed"),
            ("license_tags", "huggingface_license_changed"),
            ("used_storage_bytes", "huggingface_storage_size_changed"),
            ("description_sha256", "huggingface_dataset_card_changed"),
            ("siblings_sha256", "huggingface_file_inventory_changed"),
            ("topology_case_manifest_sha256", "topology_case_manifest_changed"),
            ("unique_id_manifest_sha256", "unique_id_manifest_changed"),
        ):
            if observed.get(key) != frozen.get(key):
                signals.append(signal)
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
    if watch.get("kind") == "zenodo_record":
        frozen = watch["frozen_snapshot"]
        signals: list[str] = []
        for key, signal in (
            ("zenodo_modified", "zenodo_record_modified"),
            ("zenodo_revision", "zenodo_revision_changed"),
            ("zenodo_status", "zenodo_status_changed"),
            ("zenodo_access_right", "zenodo_access_right_changed"),
            ("zenodo_license_id", "zenodo_license_changed"),
            ("zenodo_files", "zenodo_file_inventory_changed"),
            ("payload_or_manifest_files", "zenodo_payload_manifest_changed"),
        ):
            if observed.get(key) != frozen.get(key):
                signals.append(signal)
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
    if watch.get("kind") == "github_release_asset_contract":
        return fetch_github_release_asset_contract_snapshot(
            source["repository"], source["default_branch"], source["release_tag"]
        )
    if watch.get("kind") == "zenodo_challenge":
        return fetch_zenodo_challenge_snapshot(
            source["zenodo_api_url"], source["challenge_page_url"]
        )
    if watch.get("kind") == "github_repository_availability":
        return fetch_github_repository_availability_snapshot(
            source["repository_api_url"]
        )
    if watch.get("kind") == "github_versioned_release_contract":
        return fetch_github_versioned_release_contract_snapshot(
            source["repository_api_url"],
            source["default_branch"],
            source["batch1_anchor_commit"],
            source["release_prefix"],
        )
    if watch.get("kind") == "github_registry_wiki_contract":
        return fetch_github_registry_wiki_contract_snapshot(
            source["registry_contents_api_url"],
            source["registry_commits_api_url"],
            source["wiki_raw_url"],
        )
    if watch.get("kind") == "huggingface_dataset":
        return fetch_huggingface_dataset_snapshot(source["dataset_api_url"])
    if watch.get("kind") == "huggingface_revision":
        return fetch_huggingface_revision_snapshot(source["dataset_api_url"])
    if watch.get("kind") == "huggingface_intervention_release":
        return fetch_huggingface_intervention_release_snapshot(
            source["dataset_api_url"]
        )
    if watch.get("kind") == "huggingface_under_review_dataset":
        return fetch_huggingface_under_review_snapshot(source["dataset_api_url"])
    if watch.get("kind") == "huggingface_aneux_transient_revision":
        return fetch_huggingface_aneux_transient_snapshot(
            source["dataset_api_url"]
        )
    if watch.get("kind") == "zenodo_record":
        return fetch_zenodo_record_snapshot(source["zenodo_api_url"])
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
        "aurora.source_watch.v5",
        "aurora.source_watch.v6",
        "aurora.source_watch.v7",
        "aurora.source_watch.v8",
        "aurora.source_watch.v9",
        "aurora.source_watch.v10",
        "aurora.source_watch.v11",
        "aurora.source_watch.v12",
        "aurora.source_watch.v13",
        "aurora.source_watch.v14",
        "aurora.source_watch.v15",
        "aurora.source_watch.v16",
        "aurora.source_watch.v17",
        "aurora.source_watch.v18",
        "aurora.source_watch.v19",
        "aurora.source_watch.v20",
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
