"""Method-free VMR growth-paired transient-WSS asset/semantics P0.

The one-shot audit verifies source integrity, patient/pair/result joins, safe
archives and the existence of time-resolved three-component WSS arrays.  It
does not extract critical structures, test growth associations, train a model
or use a GPU.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import stat
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Mapping, Sequence


class VMRGrowthSurfaceStructureP0Error(RuntimeError):
    """Raised when the prospective source contract cannot be executed."""


_FULL_SHA = re.compile(r"[0-9a-f]{40}")
_DATA_ARRAY = re.compile(r"<DataArray\b[^>]*>", re.IGNORECASE)
_ATTRIBUTE = re.compile(r"([A-Za-z_:][A-Za-z0-9_.:-]*)\s*=\s*(['\"])(.*?)\2")


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _archive_name(case_id: str) -> str:
    return f"{case_id}_3D_RIGID_VTP.zip"


def _archive_url(case_id: str) -> str:
    return (
        "https://www.vascularmodel.com/svresults/"
        f"{case_id}/{_archive_name(case_id)}"
    )


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.vmr_growth_surface_structure_p0.v1":
        raise VMRGrowthSurfaceStructureP0Error("Unexpected P0 schema version.")
    if payload.get("protocol_id") != "vmr_growth_surface_structure_asset_semantics_p0_v1":
        raise VMRGrowthSurfaceStructureP0Error("Unexpected P0 protocol id.")
    if payload.get("status") != "preregistered_before_first_introai9_pbs_execution":
        raise VMRGrowthSurfaceStructureP0Error("P0 must remain prospective.")

    candidate = payload["candidate"]
    expected_axes = [
        "clinical_importance",
        "target_identifiability",
        "residual_novelty",
        "asset_readiness",
        "effective_independent_unit",
        "strong_baseline_feasibility",
        "interpretable_evidence",
        "isbi_schedule_fit",
    ]
    if (
        candidate["id"] != "growth_paired_transient_wss_structure_stability"
        or candidate["axis_order"] != expected_axes
        or [float(value) for value in candidate["axis_scores"]]
        != [4.5, 4.0, 2.5, 4.5, 3.0, 5.0, 5.0, 4.0]
        or float(candidate["score"]) != 32.5
        or sum(float(value) for value in candidate["axis_scores"]) != 32.5
        or float(candidate["admission_threshold"]) != 32.0
        or candidate["historical_surface_vector_score_repaired"] is not False
        or candidate["historical_surface_vector_p0_rerun"] is not False
        or any(
            candidate[key] is not False
            for key in (
                "primary_problem_selected",
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
            )
        )
    ):
        raise VMRGrowthSurfaceStructureP0Error("Frozen candidate contract changed.")

    sources = payload["sources"]
    expected_metadata = {
        "dataset-svprojects.csv": (
            "https://www.vascularmodel.com/dataset/dataset-svprojects.csv",
            152492,
            "d8d43c633df5fa7d7b21edf6a2b6158686fed4c6dbf0253cfffe77dcb18e19e0",
        ),
        "dataset-svresults.csv": (
            "https://www.vascularmodel.com/dataset/dataset-svresults.csv",
            77713,
            "9bf79ff7d79241c1e0b564ad4efbe7ae9da5a1405a9d3a36f3a5b5c6f39f6a14",
        ),
        "file_sizes.csv": (
            "https://www.vascularmodel.com/dataset/file_sizes.csv",
            39122,
            "0522f4b076eb82c1f85db6eb687ac97ef995506145953161cc135ec7a488ab94",
        ),
    }
    observed_metadata = {
        row["name"]: (row["url"], int(row["bytes"]), row["sha256"])
        for row in sources["metadata"]
    }
    expected_ids = [f"{index:04d}_H_CERE_CA" for index in range(199, 221)]
    expected_pairs = [expected_ids[index : index + 2] for index in range(0, 22, 2)]
    archives = sources["result_archives"]
    archive_ids = [row["case_id"] for row in archives]
    archive_sizes = [int(row["bytes"]) for row in archives]
    if (
        sources["repository_base_url"] != "https://www.vascularmodel.com/"
        or sources["primary_paper_doi"] != "10.3389/fphys.2023.1300754"
        or observed_metadata != expected_metadata
        or sources["case_ids"] != expected_ids
        or sources["matched_pairs"] != expected_pairs
        or archive_ids != expected_ids
        or len(set(archive_ids)) != 22
        or sum(archive_sizes) != 1998793994
        or int(sources["exact_total_result_archive_bytes"]) != 1998793994
    ):
        raise VMRGrowthSurfaceStructureP0Error("Pinned official source changed.")

    access = payload["access"]
    if (
        int(access["maximum_total_result_archive_bytes"]) != 1998793994
        or int(access["maximum_single_archive_bytes"]) != 332876814
        or int(access["maximum_vtp_header_bytes_per_member"]) != 4194304
        or int(access["expected_case_count"]) != 22
        or int(access["expected_pair_count"]) != 11
        or int(access["expected_growing_count"]) != 11
        or int(access["expected_stable_count"]) != 11
        or int(access["expected_vtp_members_per_archive"]) != 3
        or access["required_member_suffixes"]
        != ["_last.vtp", "_dome.vtp", "_parent.vtp"]
        or int(access["minimum_distinct_wss_phase_arrays"]) != 2
        or any(
            access[key] is not False
            for key in (
                "archive_persisted_after_job",
                "vtp_member_persisted_after_job",
                "medical_image_or_project_archive_access",
                "critical_point_or_degree_extraction",
                "growth_association_testing",
                "model_or_checkpoint_access",
                "outer_test_access",
            )
        )
    ):
        raise VMRGrowthSurfaceStructureP0Error("Access boundary changed.")
    re.compile(str(access["wss_vector_name_regex"]))
    re.compile(str(access["phase_name_regex"]))

    transport = payload["transport"]
    if (
        transport["attempt_delays_seconds"] != [0, 20]
        or int(transport["timeout_seconds_per_attempt"]) != 1800
        or int(transport["chunk_bytes"]) != 1048576
    ):
        raise VMRGrowthSurfaceStructureP0Error("Transport budget changed.")

    execution = payload["execution"]
    if (
        execution["server"] != "introai9"
        or execution["excluded_server"] != "junjinyong"
        or execution["queue"] != "coss_agpu"
        or int(execution["ncpus"]) != 4
        or int(execution["memory_gb"]) != 16
        or int(execution["ngpus"]) != 0
        or execution["walltime"] != "04:00:00"
        or int(execution["maximum_submissions_for_exact_public_source"]) != 1
        or execution["same_contract_repair_or_rerun_allowed"] is not False
        or execution["login_node_gpu_command_allowed"] is not False
    ):
        raise VMRGrowthSurfaceStructureP0Error("Execution boundary changed.")
    if len(payload["gate"]["checks"]) != 10 or payload["gate"]["all_checks_required"] is not True:
        raise VMRGrowthSurfaceStructureP0Error("Scientific gate changed.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validated = validate_config(payload)
    validated["_config_sha256"] = _canonical_hash(payload)
    return validated


def _download(
    url: str,
    destination: Path,
    *,
    expected_bytes: int,
    delays: Sequence[int],
    timeout: int,
    chunk_bytes: int,
    user_agent: str,
) -> None:
    last_error: BaseException | None = None
    for delay in delays:
        if delay:
            time.sleep(delay)
        destination.unlink(missing_ok=True)
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})
        try:
            observed = 0
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with destination.open("xb") as output:
                    while True:
                        chunk = response.read(chunk_bytes)
                        if not chunk:
                            break
                        observed += len(chunk)
                        if observed > expected_bytes:
                            raise VMRGrowthSurfaceStructureP0Error(
                                "Registered object exceeds its exact byte cap."
                            )
                        output.write(chunk)
            if observed != expected_bytes:
                raise VMRGrowthSurfaceStructureP0Error(
                    "Registered object byte count does not match."
                )
            return
        except (
            OSError,
            urllib.error.URLError,
            urllib.error.HTTPError,
            VMRGrowthSurfaceStructureP0Error,
        ) as exc:
            last_error = exc
    destination.unlink(missing_ok=True)
    raise VMRGrowthSurfaceStructureP0Error("Transport attempts exhausted.") from last_error


def _sha256(path: Path, chunk_bytes: int = 1048576) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_bytes)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def inspect_metadata(
    projects: Sequence[Mapping[str, str]],
    results: Sequence[Mapping[str, str]],
    sizes: Sequence[Mapping[str, str]],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    sources = config["sources"]
    case_ids = set(sources["case_ids"])
    project_rows = [row for row in projects if row.get("Name") in case_ids]
    result_rows = [row for row in results if row.get("Model Name") in case_ids]
    project_by_id = {row["Name"]: row for row in project_rows}
    result_by_id = {row["Model Name"]: row for row in result_rows}

    labels: dict[str, str] = {}
    reciprocal_pairs = True
    for growing_id, stable_id in sources["matched_pairs"]:
        growing_notes = project_by_id.get(growing_id, {}).get("Notes", "").lower()
        stable_notes = project_by_id.get(stable_id, {}).get("Notes", "").lower()
        labels[growing_id] = "growing"
        labels[stable_id] = "stable"
        reciprocal_pairs = reciprocal_pairs and (
            "growing aneurysm" in growing_notes
            and "stable aneurysm" in stable_notes
            and stable_id.lower() in growing_notes
            and growing_id.lower() in stable_notes
            and "at least 1mm in two or more dimensions" in growing_notes
            and "no increase in size by at least 1mm in two or more dimensions"
            in stable_notes
        )

    human_cerebral = all(
        row.get("Species") == "Human"
        and row.get("Anatomy") == "Cerebral"
        and row.get("Disease") == "Cerebral Aneurysm"
        and row.get("Results") == "1"
        for row in project_rows
    )
    time_resolved_surface = all(
        row.get("Full Simulation File Name") == _archive_name(case_id)
        and row.get("Simulation Fidelity") == "3D"
        and row.get("Simulation Method") == "Rigid Wall"
        and row.get("Results Type") == "Time-Resolved"
        and row.get("Results File Type") == "Surface (vtp)"
        and "wall shear stress" in row.get("Notes", "").lower()
        and "three files" in row.get("Notes", "").lower()
        for case_id, row in result_by_id.items()
    )

    expected_sizes = {
        f"svresults/{row['case_id']}/{_archive_name(row['case_id'])}": int(row["bytes"])
        for row in sources["result_archives"]
    }
    observed_sizes = {
        row["Name"]: int(row["Size"])
        for row in sizes
        if row.get("Name") in expected_sizes
    }
    return {
        "project_row_count": len(project_rows),
        "unique_project_case_count": len(project_by_id),
        "human_cerebral_aneurysm_result_contract": human_cerebral,
        "growing_count": sum(value == "growing" for value in labels.values()),
        "stable_count": sum(value == "stable" for value in labels.values()),
        "reciprocal_pair_contract": reciprocal_pairs,
        "result_row_count": len(result_rows),
        "unique_result_case_count": len(result_by_id),
        "time_resolved_surface_vtp_contract": time_resolved_surface,
        "size_manifest_row_count": len(observed_sizes),
        "size_manifest_exact": observed_sizes == expected_sizes,
        "size_manifest_total_bytes": sum(observed_sizes.values()),
    }


def _safe_member_name(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/"):
        return False
    path = PurePosixPath(name)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def _attributes(tag: str) -> dict[str, str]:
    return {match.group(1).lower(): match.group(3) for match in _ATTRIBUTE.finditer(tag)}


def _read_prefix(stream: BinaryIO, maximum_bytes: int) -> bytes:
    chunks: list[bytes] = []
    remaining = maximum_bytes
    while remaining > 0:
        chunk = stream.read(min(65536, remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
        if b"<AppendedData" in chunk:
            break
    return b"".join(chunks)


def inspect_vtp_header(prefix: bytes, access: Mapping[str, Any]) -> dict[str, Any]:
    text = prefix.decode("latin-1", errors="ignore")
    header = text.split("<AppendedData", 1)[0]
    polydata = bool(re.search(r"<VTKFile\b[^>]*\btype=['\"]PolyData['\"]", header, re.I))
    points_match = re.search(r"<Points\b[^>]*>(.*?)</Points>", header, re.I | re.S)
    coordinate_three = False
    if points_match:
        coordinate_three = any(
            int(_attributes(tag).get("numberofcomponents", "1")) == 3
            for tag in _DATA_ARRAY.findall(points_match.group(1))
        )

    wss_regex = re.compile(str(access["wss_vector_name_regex"]))
    phase_regex = re.compile(str(access["phase_name_regex"]))
    wss_names: set[str] = set()
    phased_wss_names: set[str] = set()
    for block_name in ("PointData", "CellData"):
        block = re.search(rf"<{block_name}\b[^>]*>(.*?)</{block_name}>", header, re.I | re.S)
        if block is None:
            continue
        for tag in _DATA_ARRAY.findall(block.group(1)):
            attrs = _attributes(tag)
            name = attrs.get("name", "")
            if int(attrs.get("numberofcomponents", "1")) == 3 and wss_regex.search(name):
                wss_names.add(name)
                if phase_regex.search(name):
                    phased_wss_names.add(name)
    return {
        "polydata": polydata,
        "coordinate_three_component": coordinate_three,
        "wss_names": sorted(wss_names),
        "phased_wss_names": sorted(phased_wss_names),
        "header_prefix_truncated": len(prefix) >= int(access["maximum_vtp_header_bytes_per_member"]),
    }


def inspect_result_archive(path: Path, case_id: str, access: Mapping[str, Any]) -> dict[str, Any]:
    required_suffixes = [suffix.lower() for suffix in access["required_member_suffixes"]]
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        unique_safe = len(names) == len(set(names)) and all(_safe_member_name(name) for name in names)
        regular_vtp = []
        no_links = True
        for info in infos:
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                no_links = False
            if not info.is_dir() and info.filename.lower().endswith(".vtp"):
                regular_vtp.append(info)
        suffix_contract = all(
            sum(info.filename.lower().endswith(suffix) for info in regular_vtp) == 1
            for suffix in required_suffixes
        )
        case_contract = all(case_id.lower() in info.filename.lower() for info in regular_vtp)
        crc_valid = archive.testzip() is None
        headers = []
        for info in regular_vtp:
            with archive.open(info) as stream:
                prefix = _read_prefix(stream, int(access["maximum_vtp_header_bytes_per_member"]))
            headers.append(inspect_vtp_header(prefix, access))

    common_wss = (
        set.intersection(*(set(row["wss_names"]) for row in headers)) if headers else set()
    )
    common_phases = (
        set.intersection(*(set(row["phased_wss_names"]) for row in headers)) if headers else set()
    )
    return {
        "safe_unique_member_names": unique_safe,
        "no_symbolic_links": no_links,
        "regular_vtp_member_count": len(regular_vtp),
        "required_suffix_contract": suffix_contract,
        "case_name_contract": case_contract,
        "zip_crc_valid": crc_valid,
        "all_polydata": bool(headers) and all(row["polydata"] for row in headers),
        "all_three_component_coordinates": bool(headers)
        and all(row["coordinate_three_component"] for row in headers),
        "common_wss_names": sorted(common_wss),
        "common_phased_wss_names": sorted(common_phases),
        "minimum_member_wss_phase_count": min(
            (len(row["phased_wss_names"]) for row in headers), default=0
        ),
        "truncated_header_count": sum(row["header_prefix_truncated"] for row in headers),
    }


def run_p0(
    config: Mapping[str, Any], *, work_dir: Path, public_source_commit: str
) -> dict[str, Any]:
    if not _FULL_SHA.fullmatch(public_source_commit):
        raise VMRGrowthSurfaceStructureP0Error("Public source commit must be a full SHA.")
    work_dir.mkdir(parents=True, exist_ok=True)
    transport = config["transport"]
    metadata_integrity: list[bool] = []
    metadata_paths: dict[str, Path] = {}
    for item in config["sources"]["metadata"]:
        path = work_dir / item["name"]
        _download(
            item["url"],
            path,
            expected_bytes=int(item["bytes"]),
            delays=[int(value) for value in transport["attempt_delays_seconds"]],
            timeout=int(transport["timeout_seconds_per_attempt"]),
            chunk_bytes=int(transport["chunk_bytes"]),
            user_agent=str(transport["user_agent"]),
        )
        metadata_integrity.append(
            path.stat().st_size == int(item["bytes"]) and _sha256(path) == item["sha256"]
        )
        metadata_paths[item["name"]] = path

    metadata = inspect_metadata(
        _read_csv(metadata_paths["dataset-svprojects.csv"]),
        _read_csv(metadata_paths["dataset-svresults.csv"]),
        _read_csv(metadata_paths["file_sizes.csv"]),
        config,
    )
    for path in metadata_paths.values():
        path.unlink(missing_ok=True)

    archive_rows = []
    for item in config["sources"]["result_archives"]:
        case_id = item["case_id"]
        archive_path = work_dir / _archive_name(case_id)
        _download(
            _archive_url(case_id),
            archive_path,
            expected_bytes=int(item["bytes"]),
            delays=[int(value) for value in transport["attempt_delays_seconds"]],
            timeout=int(transport["timeout_seconds_per_attempt"]),
            chunk_bytes=int(transport["chunk_bytes"]),
            user_agent=str(transport["user_agent"]),
        )
        row = inspect_result_archive(archive_path, case_id, config["access"])
        row["exact_registered_bytes"] = archive_path.stat().st_size == int(item["bytes"])
        archive_rows.append(row)
        archive_path.unlink(missing_ok=True)

    access = config["access"]
    archive_contract = all(
        row["exact_registered_bytes"]
        and row["safe_unique_member_names"]
        and row["no_symbolic_links"]
        and row["regular_vtp_member_count"] == int(access["expected_vtp_members_per_archive"])
        and row["required_suffix_contract"]
        and row["case_name_contract"]
        and row["zip_crc_valid"]
        for row in archive_rows
    )
    checks = {
        "three_metadata_files_match_exact_bytes_and_sha256": all(metadata_integrity),
        "metadata_identifies_twenty_two_unique_human_cerebral_aneurysm_cases": bool(
            metadata["project_row_count"] == 22
            and metadata["unique_project_case_count"] == 22
            and metadata["human_cerebral_aneurysm_result_contract"]
        ),
        "metadata_identifies_eleven_reciprocal_growth_stable_pairs": bool(
            metadata["growing_count"] == 11
            and metadata["stable_count"] == 11
            and metadata["reciprocal_pair_contract"]
        ),
        "results_join_is_exactly_twenty_two_time_resolved_surface_vtp_rows": bool(
            metadata["result_row_count"] == 22
            and metadata["unique_result_case_count"] == 22
            and metadata["time_resolved_surface_vtp_contract"]
        ),
        "file_size_manifest_matches_all_twenty_two_archives_and_total_bytes": bool(
            metadata["size_manifest_row_count"] == 22
            and metadata["size_manifest_exact"]
            and metadata["size_manifest_total_bytes"]
            == int(config["sources"]["exact_total_result_archive_bytes"])
        ),
        "all_archives_match_registered_bytes_and_safe_three_member_vtp_contract": archive_contract,
        "all_vtp_headers_identify_polydata_and_three_component_coordinates": bool(
            len(archive_rows) == 22
            and all(row["all_polydata"] and row["all_three_component_coordinates"] for row in archive_rows)
        ),
        "every_case_exposes_consistent_three_component_wss_arrays": bool(
            len(archive_rows) == 22 and all(row["common_wss_names"] for row in archive_rows)
        ),
        "every_case_exposes_at_least_two_ordered_wss_phase_arrays": bool(
            len(archive_rows) == 22
            and all(
                row["minimum_member_wss_phase_count"]
                >= int(access["minimum_distinct_wss_phase_arrays"])
                for row in archive_rows
            )
        ),
        "no_structure_growth_model_gpu_outer_test_or_persistent_payload": True,
    }
    if list(checks) != list(config["gate"]["checks"]):
        raise VMRGrowthSurfaceStructureP0Error("Implemented checks differ from registration.")
    gate_passed = all(checks.values())
    aggregate = {
        **metadata,
        "archive_count": len(archive_rows),
        "archive_contract_count": sum(
            row["exact_registered_bytes"]
            and row["safe_unique_member_names"]
            and row["no_symbolic_links"]
            and row["regular_vtp_member_count"] == 3
            and row["required_suffix_contract"]
            and row["case_name_contract"]
            and row["zip_crc_valid"]
            for row in archive_rows
        ),
        "polydata_coordinate_contract_count": sum(
            row["all_polydata"] and row["all_three_component_coordinates"]
            for row in archive_rows
        ),
        "wss_contract_count": sum(bool(row["common_wss_names"]) for row in archive_rows),
        "phase_contract_count": sum(
            row["minimum_member_wss_phase_count"]
            >= int(access["minimum_distinct_wss_phase_arrays"])
            for row in archive_rows
        ),
        "minimum_member_wss_phase_count_across_cases": min(
            (row["minimum_member_wss_phase_count"] for row in archive_rows), default=0
        ),
        "maximum_truncated_header_count_per_archive": max(
            (row["truncated_header_count"] for row in archive_rows), default=0
        ),
    }
    return {
        "schema_version": "aurora.vmr_growth_surface_structure_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "status": "passed_asset_semantics_gate" if gate_passed else "failed_asset_semantics_gate",
        "public_source_commit": public_source_commit,
        "config_sha256": config["_config_sha256"],
        "scientific_gate_evaluated": True,
        "gate_passed": gate_passed,
        "checks": checks,
        "aggregate": aggregate,
        "access": {
            "metadata_and_result_archives_downloaded_to_job_local_scratch": True,
            "archive_or_vtp_persisted": False,
            "medical_image_or_project_archive": False,
            "critical_point_or_degree_extraction": False,
            "growth_association": False,
            "model": False,
            "gpu": False,
            "outer_test": False,
        },
        "authorization": {
            "primary_problem": False,
            "method": False,
            "architecture": False,
            "gpu": False,
            "outer_test": False,
            "submission_identity": False,
            "next": config["gate"]["pass_authorizes"]
            if gate_passed
            else config["gate"]["failure_action"],
        },
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--public-source-commit")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    if args.work_dir is None or args.result is None or args.public_source_commit is None:
        parser.error("execution requires --work-dir, --result and --public-source-commit")
    try:
        result = run_p0(
            config,
            work_dir=args.work_dir,
            public_source_commit=args.public_source_commit,
        )
        _write_json(args.result, result)
        return 0 if result["gate_passed"] else 1
    except Exception as exc:
        result = {
            "schema_version": "aurora.vmr_growth_surface_structure_p0.result.v1",
            "protocol_id": config["protocol_id"],
            "status": "execution_incomplete_no_scientific_verdict",
            "public_source_commit": args.public_source_commit,
            "config_sha256": config["_config_sha256"],
            "scientific_gate_evaluated": False,
            "gate_passed": None,
            "checks_evaluated": 0,
            "error_class": type(exc).__name__,
            "access": {
                "archive_or_vtp_persisted": False,
                "critical_point_or_degree_extraction": False,
                "growth_association": False,
                "model": False,
                "gpu": False,
                "outer_test": False,
            },
            "authorization": {
                "primary_problem": False,
                "method": False,
                "architecture": False,
                "gpu": False,
                "outer_test": False,
                "submission_identity": False,
                "next": config["gate"]["execution_incomplete_action"],
            },
        }
        _write_json(args.result, result)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
