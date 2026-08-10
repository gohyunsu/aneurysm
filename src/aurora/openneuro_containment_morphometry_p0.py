"""Method-free metadata P0 for the OpenNeuro containment-morphometry lead."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickletools
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence


class OpenNeuroContainmentP0Error(RuntimeError):
    """Raised when the frozen metadata-only contract cannot be evaluated."""


_SUBJECT_SESSION = re.compile(r"sub-\d{3}_ses-\d{8}")
_SUBJECT = re.compile(r"sub-\d{3}")
_MANUAL_PATH = re.compile(
    r"derivatives/manual_masks/(sub-\d{3})/(ses-\d{8})/(.+)"
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.openneuro_containment_morphometry_p0.v1":
        raise OpenNeuroContainmentP0Error("Unexpected P0 schema version.")
    if payload.get("protocol_id") != "openneuro_containment_morphometry_metadata_p0_v1":
        raise OpenNeuroContainmentP0Error("Unexpected P0 protocol id.")
    if payload.get("status") != "preregistered_before_first_introai9_pbs_execution":
        raise OpenNeuroContainmentP0Error("P0 must remain prospectively registered.")
    candidate = payload["candidate"]
    if (
        candidate["id"] != "containment_identified_morphometry_envelopes"
        or float(candidate["score"]) != 32.5
        or float(candidate["admission_threshold"]) != 32.0
        or sum(float(value) for value in candidate["axis_scores"]) != 32.5
        or candidate["coarsening_mechanism_estimated"] is not False
    ):
        raise OpenNeuroContainmentP0Error("Frozen candidate contract changed.")
    sources = payload["sources"]
    if (
        sources["dataset_commit"]
        != "896b8846d899acee68c0246cc987ca96e77267d4"
        or sources["code_commit"]
        != "5ecdf6e5b9a811e4ec7472c210dada42e60cc3dc"
        or sources["dataset_tag"] != "1.0.1"
        or sources["dataset_license"] != "CC0"
        or sources["code_license"] != "Apache-2.0"
    ):
        raise OpenNeuroContainmentP0Error("Pinned source contract changed.")
    expected = payload["expected"]
    fixed_counts = {
        "dataset_tree_paths": 5737,
        "public_subjects": 284,
        "manual_mask_subject_sessions": 296,
        "manual_mask_nifti_paths": 494,
        "precise_list_entries": 38,
        "precise_list_subjects": 38,
        "weak_list_entries": 262,
        "weak_list_subjects": 250,
        "public_precise_subjects": 38,
        "public_weak_subjects": 246,
        "code_session_pairs_matching_public_tree": 11,
    }
    if any(int(expected[key]) != value for key, value in fixed_counts.items()):
        raise OpenNeuroContainmentP0Error("Frozen source counts changed.")
    if expected["code_only_weak_subjects"] != [
        "sub-115",
        "sub-143",
        "sub-181",
        "sub-272",
    ]:
        raise OpenNeuroContainmentP0Error("Frozen release exclusions changed.")
    access = payload["access"]
    if any(
        access[key] is not False
        for key in (
            "pickle_unpickling_or_execution",
            "patient_nifti_image_or_mask_body_access",
            "participants_or_clinical_table_access",
            "pretrained_model_or_checkpoint_access",
            "outer_test_access",
        )
    ):
        raise OpenNeuroContainmentP0Error("Metadata-only access boundary changed.")
    transport = payload["transport"]
    if (
        transport["attempt_delays_seconds"] != [0, 10, 30]
        or int(transport["timeout_seconds_per_attempt"]) != 30
    ):
        raise OpenNeuroContainmentP0Error("Frozen transport budget changed.")
    execution = payload["execution"]
    if (
        execution["server"] != "introai9"
        or execution["excluded_server"] != "junjinyong"
        or int(execution["ngpus"]) != 0
        or int(execution["maximum_submissions_for_exact_public_source"]) != 1
    ):
        raise OpenNeuroContainmentP0Error("Execution boundary changed.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def _request_bytes(
    url: str,
    *,
    maximum_bytes: int,
    delays: Sequence[int],
    timeout: int,
    user_agent: str,
) -> bytes:
    last_error: BaseException | None = None
    for delay in delays:
        if delay:
            time.sleep(delay)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": user_agent, "Accept": "application/vnd.github+json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read(maximum_bytes + 1)
            if len(payload) > maximum_bytes:
                raise OpenNeuroContainmentP0Error(
                    f"Registered HTTP object exceeds byte cap: {url}"
                )
            return payload
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_error = exc
    raise OpenNeuroContainmentP0Error(
        f"Transport attempts exhausted for registered object: {url}"
    ) from last_error


def _subject_sessions_from_pickle(payload: bytes) -> set[str]:
    """Extract strings from pickle opcodes without constructing pickle objects."""

    values: set[str] = set()
    try:
        operations = pickletools.genops(payload)
        for operation, argument, _ in operations:
            if operation.name not in {"BINUNICODE", "SHORT_BINUNICODE", "UNICODE"}:
                continue
            if isinstance(argument, str) and _SUBJECT_SESSION.fullmatch(argument):
                values.add(argument)
    except ValueError as exc:  # pragma: no cover - defensive
        raise OpenNeuroContainmentP0Error("Invalid supervision-list pickle opcodes.") from exc
    if not values:
        raise OpenNeuroContainmentP0Error("No subject-session identifiers found.")
    return values


def _subject(identifier: str) -> str:
    value = identifier.split("_ses-", maxsplit=1)[0]
    if not _SUBJECT.fullmatch(value):
        raise OpenNeuroContainmentP0Error(f"Invalid subject identifier: {identifier}")
    return value


def _fetch_registered_objects(config: Mapping[str, Any]) -> dict[str, bytes]:
    sources = config["sources"]
    transport = config["transport"]
    caps = config["access"]["maximum_bytes_by_object"]
    common = {
        "delays": [int(value) for value in transport["attempt_delays_seconds"]],
        "timeout": int(transport["timeout_seconds_per_attempt"]),
        "user_agent": str(transport["user_agent"]),
    }
    return {
        "dataset_tree_json": _request_bytes(
            sources["dataset_tree_api"],
            maximum_bytes=int(caps["dataset_tree_json"]),
            **common,
        ),
        "dataset_description_json": _request_bytes(
            sources["dataset_description_url"],
            maximum_bytes=int(caps["dataset_description_json"]),
            **common,
        ),
        "precise_subject_list_pickle_bytes_opcode_only": _request_bytes(
            sources["precise_list_url"],
            maximum_bytes=int(caps["precise_subject_list_pickle_bytes_opcode_only"]),
            **common,
        ),
        "weak_subject_list_pickle_bytes_opcode_only": _request_bytes(
            sources["weak_list_url"],
            maximum_bytes=int(caps["weak_subject_list_pickle_bytes_opcode_only"]),
            **common,
        ),
        "code_license_text": _request_bytes(
            sources["code_license_url"],
            maximum_bytes=int(caps["code_license_text"]),
            **common,
        ),
    }


def run_p0(config: Mapping[str, Any], *, public_source_commit: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", public_source_commit):
        raise OpenNeuroContainmentP0Error("Public source commit must be a full SHA.")
    objects = _fetch_registered_objects(config)
    sources = config["sources"]
    expected = config["expected"]

    hashes = {
        key: _sha256_bytes(value)
        for key, value in objects.items()
        if key != "dataset_tree_json"
    }
    exact_hashes = (
        hashes["dataset_description_json"] == sources["dataset_description_sha256"]
        and hashes["precise_subject_list_pickle_bytes_opcode_only"]
        == sources["precise_list_sha256"]
        and hashes["weak_subject_list_pickle_bytes_opcode_only"]
        == sources["weak_list_sha256"]
        and hashes["code_license_text"] == sources["code_license_sha256"]
    )

    try:
        tree_payload = json.loads(objects["dataset_tree_json"].decode("utf-8"))
        description = json.loads(objects["dataset_description_json"].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OpenNeuroContainmentP0Error("Invalid registered JSON source.") from exc
    tree_rows = tree_payload.get("tree", [])
    if not isinstance(tree_rows, list):
        raise OpenNeuroContainmentP0Error("GitHub tree response has no list tree.")
    paths = [row.get("path") for row in tree_rows if isinstance(row, dict)]
    if any(not isinstance(path, str) for path in paths):
        raise OpenNeuroContainmentP0Error("GitHub tree contains an invalid path.")

    public_subjects = {
        match.group(1)
        for path in paths
        if (match := re.match(r"(sub-\d{3})/", path))
    }
    manual_pairs: set[str] = set()
    manual_nifti_paths = 0
    for path in paths:
        match = _MANUAL_PATH.fullmatch(path)
        if not match:
            continue
        manual_pairs.add(f"{match.group(1)}_{match.group(2)}")
        if match.group(3).endswith((".nii", ".nii.gz")):
            manual_nifti_paths += 1

    precise_sessions = _subject_sessions_from_pickle(
        objects["precise_subject_list_pickle_bytes_opcode_only"]
    )
    weak_sessions = _subject_sessions_from_pickle(
        objects["weak_subject_list_pickle_bytes_opcode_only"]
    )
    precise_subjects = {_subject(value) for value in precise_sessions}
    weak_subjects = {_subject(value) for value in weak_sessions}
    code_only_weak = weak_subjects - public_subjects
    public_precise = precise_subjects & public_subjects
    public_weak = weak_subjects & public_subjects
    partition_overlap = public_precise & public_weak
    unmapped = public_subjects - (public_precise | public_weak)
    session_matches = len((precise_sessions | weak_sessions) & manual_pairs)

    license_text = objects["code_license_text"].decode("utf-8", errors="strict")
    checks = {
        "exact_commits_and_small_blob_hashes": bool(
            exact_hashes and tree_payload.get("sha") == sources["dataset_commit"]
        ),
        "dataset_tree_complete_and_path_count_exact": bool(
            tree_payload.get("truncated") is False
            and len(paths) == int(expected["dataset_tree_paths"])
        ),
        "public_subject_and_manual_mask_counts_exact": bool(
            len(public_subjects) == int(expected["public_subjects"])
            and len(manual_pairs) == int(expected["manual_mask_subject_sessions"])
            and manual_nifti_paths == int(expected["manual_mask_nifti_paths"])
        ),
        "supervision_lists_parsed_without_unpickling": bool(
            len(precise_sessions) == int(expected["precise_list_entries"])
            and len(precise_subjects) == int(expected["precise_list_subjects"])
            and len(weak_sessions) == int(expected["weak_list_entries"])
            and len(weak_subjects) == int(expected["weak_list_subjects"])
        ),
        "weak_and_precise_code_lists_are_disjoint": bool(
            not (precise_sessions & weak_sessions)
            and not (precise_subjects & weak_subjects)
        ),
        "public_release_excludes_exactly_four_registered_weak_subjects": bool(
            code_only_weak == set(expected["code_only_weak_subjects"])
            and not (precise_subjects - public_subjects)
        ),
        "public_subjects_partition_exactly_into_246_weak_and_38_precise": bool(
            len(public_weak) == int(expected["public_weak_subjects"])
            and len(public_precise) == int(expected["public_precise_subjects"])
            and not partition_overlap
            and not unmapped
        ),
        "subject_join_unique_and_session_join_explicitly_rejected": bool(
            session_matches == int(expected["code_session_pairs_matching_public_tree"])
            and session_matches < len(public_subjects)
        ),
        "dataset_and_code_licenses_match": bool(
            description.get("License") == "CC0"
            and str(description.get("DatasetDOI", "")).endswith(
                "10.18112/openneuro.ds003949.v1.0.1"
            )
            and "Apache License" in license_text
            and "Version 2.0" in license_text
        ),
        "no_patient_payload_table_model_checkpoint_gpu_or_outer_test_access": True,
    }
    passed = all(checks.values())
    return {
        "schema_version": "aurora.openneuro_containment_morphometry_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "status": "passed_asset_semantics_gate" if passed else "failed_asset_semantics_gate",
        "scientific_gate_evaluated": True,
        "public_source_commit": public_source_commit,
        "config_sha256": config["_config_sha256"],
        "source": {
            "dataset_commit": sources["dataset_commit"],
            "code_commit": sources["code_commit"],
            "dataset_license": description.get("License"),
            "dataset_doi": description.get("DatasetDOI"),
        },
        "counts": {
            "tree_paths": len(paths),
            "public_subjects": len(public_subjects),
            "manual_mask_subject_sessions": len(manual_pairs),
            "manual_mask_nifti_paths": manual_nifti_paths,
            "precise_list_entries": len(precise_sessions),
            "precise_list_subjects": len(precise_subjects),
            "weak_list_entries": len(weak_sessions),
            "weak_list_subjects": len(weak_subjects),
            "public_precise_subjects": len(public_precise),
            "public_weak_subjects": len(public_weak),
            "code_only_weak_subjects": sorted(code_only_weak),
            "code_session_pairs_matching_public_tree": session_matches,
            "public_partition_overlap": len(partition_overlap),
            "public_subjects_unmapped": len(unmapped),
        },
        "checks": checks,
        "passed_checks": sum(bool(value) for value in checks.values()),
        "total_checks": len(checks),
        "gate_passed": passed,
        "access": {
            "git_tree_metadata": True,
            "small_supervision_metadata": True,
            "pickle_unpickled_or_executed": False,
            "patient_nifti_image_or_mask_body": False,
            "participants_or_clinical_table": False,
            "model_or_checkpoint": False,
            "gpu": False,
            "outer_test": False,
        },
        "authorization": {
            "method_free_p1_registration": passed,
            "patient_payload": False,
            "method": False,
            "architecture": False,
            "gpu": False,
            "outer_test": False,
            "paper_contribution": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--public-source-commit", required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(args.config.read_bytes()).hexdigest()
    result = run_p0(config, public_source_commit=args.public_source_commit)
    args.result.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.result.with_suffix(args.result.suffix + ".partial")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(args.result)
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
