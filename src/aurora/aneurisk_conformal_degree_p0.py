"""Method-free Aneurisk archive/semantics P0 for conformal degree certificates.

The one-shot audit verifies only whether the public archive exposes a bounded,
patient-grouped surface-vector learning contract. It never extracts critical
points, calibrates a conformal predictor, constructs a model, or uses a GPU.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Mapping, Sequence


class AneuriskConformalDegreeP0Error(RuntimeError):
    """Raised when the prospective archive contract cannot be executed."""


_FULL_SHA = re.compile(r"[0-9a-f]{40}")
_DATA_ARRAY = re.compile(r"<DataArray\b[^>]*>", re.IGNORECASE)
_ATTRIBUTE = re.compile(r"([A-Za-z_:][A-Za-z0-9_.:-]*)\s*=\s*(['\"])(.*?)\2")


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneurisk_conformal_degree_p0.v1":
        raise AneuriskConformalDegreeP0Error("Unexpected P0 schema version.")
    if payload.get("protocol_id") != "aneurisk_conformal_degree_archive_semantics_p0_v1":
        raise AneuriskConformalDegreeP0Error("Unexpected P0 protocol id.")
    if payload.get("status") != "preregistered_before_first_introai9_pbs_execution":
        raise AneuriskConformalDegreeP0Error("P0 must remain prospective.")

    candidate = payload["candidate"]
    if (
        candidate["id"]
        != "patient_level_conformal_degree_certificate_for_surface_wss_surrogates"
        or float(candidate["score"]) != 32.5
        or float(candidate["admission_threshold"]) != 32.0
        or sum(float(value) for value in candidate["axis_scores"]) != 32.5
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
        raise AneuriskConformalDegreeP0Error("Frozen candidate contract changed.")

    sources = payload["sources"]
    archive = sources["archive"]
    readme = sources["readme"]
    if (
        int(sources["record_id"]) != 19455127
        or sources["record_doi"] != "10.5281/zenodo.19455127"
        or int(sources["record_revision"]) != 4
        or sources["record_modified"] != "2026-04-07T14:32:30.723519+00:00"
        or sources["record_status"] != "published"
        or sources["access_right"] != "open"
        or sources["license"] != "CC-BY-4.0"
        or int(sources["reported_patient_specific_geometries"]) != 76
        or archive["name"] != "AneuriskCFDResults_Zenodo.tar.gz"
        or int(archive["bytes"]) != 1430889142
        or archive["md5"] != "8c66e7bb359d04bd1a5d6db6da3f3926"
        or archive["url"]
        != "https://zenodo.org/api/records/19455127/files/AneuriskCFDResults_Zenodo.tar.gz/content"
        or int(readme["bytes"]) != 1436
        or readme["md5"] != "f552f4d1440848f0cdb8700371579115"
        or readme["payload_accessed_before_registration"] is not True
        or sources["companion_preprint"] != "arXiv:2602.21409"
    ):
        raise AneuriskConformalDegreeP0Error("Pinned official source changed.")

    access = payload["access"]
    if (
        int(access["maximum_download_bytes"]) != 1430889142
        or int(access["maximum_vtp_header_bytes_per_member"]) != 4194304
        or access["case_id_regex"] != "C[0-9]{4}"
        or int(access["minimum_vtp_members"]) != 76
        or int(access["exact_unique_case_ids"]) != 76
        or any(
            access[key] is not False
            for key in (
                "archive_persisted_after_job",
                "vtp_member_persisted_after_job",
                "critical_point_extraction",
                "conformal_calibration",
                "model_or_checkpoint_access",
                "outer_test_access",
            )
        )
    ):
        raise AneuriskConformalDegreeP0Error("Access boundary changed.")
    for key in (
        "wss_vector_name_regex",
        "cycle_average_name_regex",
        "age_or_inflow_name_regex",
        "coordinate_semantics_regex",
        "coordinate_unit_regex",
        "wss_unit_regex",
    ):
        re.compile(str(access[key]))

    transport = payload["transport"]
    if (
        transport["attempt_delays_seconds"] != [0, 10, 30]
        or int(transport["timeout_seconds_per_attempt"]) != 1800
        or int(transport["chunk_bytes"]) != 1048576
    ):
        raise AneuriskConformalDegreeP0Error("Transport budget changed.")
    execution = payload["execution"]
    if (
        execution["server"] != "introai9"
        or execution["excluded_server"] != "junjinyong"
        or execution["queue"] != "coss_agpu"
        or int(execution["ncpus"]) != 4
        or int(execution["memory_gb"]) != 16
        or int(execution["ngpus"]) != 0
        or execution["walltime"] != "02:00:00"
        or int(execution["maximum_submissions_for_exact_public_source"]) != 1
        or execution["same_contract_repair_or_rerun_allowed"] is not False
        or execution["login_node_gpu_command_allowed"] is not False
    ):
        raise AneuriskConformalDegreeP0Error("Execution boundary changed.")
    if len(payload["gate"]["checks"]) != 10 or payload["gate"]["all_checks_required"] is not True:
        raise AneuriskConformalDegreeP0Error("Scientific gate changed.")
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
                            raise AneuriskConformalDegreeP0Error(
                                "Registered archive exceeds its exact byte cap."
                            )
                        output.write(chunk)
            if observed != expected_bytes:
                raise AneuriskConformalDegreeP0Error(
                    "Registered archive byte count does not match."
                )
            return
        except (
            OSError,
            urllib.error.URLError,
            urllib.error.HTTPError,
            AneuriskConformalDegreeP0Error,
        ) as exc:
            last_error = exc
    destination.unlink(missing_ok=True)
    raise AneuriskConformalDegreeP0Error("Transport attempts exhausted.") from last_error


def _md5(path: Path, chunk_bytes: int) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_bytes)
            if not chunk:
                return digest.hexdigest()
            digest.update(chunk)


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

    signatures: set[str] = set()
    cycle_signatures: set[str] = set()
    wss_unit_semantics = False
    point_block = re.search(r"<PointData\b[^>]*>(.*?)</PointData>", header, re.I | re.S)
    cell_block = re.search(r"<CellData\b[^>]*>(.*?)</CellData>", header, re.I | re.S)
    wss_regex = re.compile(str(access["wss_vector_name_regex"]))
    cycle_regex = re.compile(str(access["cycle_average_name_regex"]))
    for association, block in (("point", point_block), ("cell", cell_block)):
        if block is None:
            continue
        for tag in _DATA_ARRAY.findall(block.group(1)):
            attrs = _attributes(tag)
            name = attrs.get("name", "")
            if int(attrs.get("numberofcomponents", "1")) == 3 and wss_regex.search(name):
                signature = f"{association}:{name}"
                signatures.add(signature)
                tag_semantics = " ".join((name, *attrs.values()))
                if re.search(str(access["wss_unit_regex"]), tag_semantics):
                    wss_unit_semantics = True
                if cycle_regex.search(name):
                    cycle_signatures.add(signature)

    coordinate_semantics = re.compile(str(access["coordinate_semantics_regex"]))
    coordinate_units = re.compile(str(access["coordinate_unit_regex"]))
    coordinate_unit_semantics = any(
        coordinate_semantics.search(" ".join(_attributes(tag).values()))
        and coordinate_units.search(" ".join(_attributes(tag).values()))
        for tag in _DATA_ARRAY.findall(header)
    )

    return {
        "polydata": polydata,
        "coordinate_three_component": coordinate_three,
        "wss_signatures": sorted(signatures),
        "cycle_wss_signatures": sorted(cycle_signatures),
        "has_coordinate_unit_semantics": coordinate_unit_semantics,
        "has_wss_unit_semantics": wss_unit_semantics,
        "has_age_or_inflow_semantics": bool(
            re.search(str(access["age_or_inflow_name_regex"]), header)
        ),
        "header_prefix_truncated": len(prefix) >= int(access["maximum_vtp_header_bytes_per_member"]),
    }


def inspect_archive(path: Path, config: Mapping[str, Any]) -> dict[str, Any]:
    access = config["access"]
    case_regex = re.compile(str(access["case_id_regex"]))
    seen_names: set[str] = set()
    safe = True
    links = 0
    nonregular = 0
    vtp_count = 0
    unmapped_vtp = 0
    case_headers: dict[str, list[dict[str, Any]]] = {}

    with tarfile.open(path, mode="r|gz") as archive:
        for member in archive:
            if member.name in seen_names or not _safe_member_name(member.name):
                safe = False
            seen_names.add(member.name)
            if member.issym() or member.islnk():
                links += 1
                safe = False
                continue
            if member.isdir():
                continue
            if not member.isfile():
                nonregular += 1
                safe = False
                continue
            if not member.name.lower().endswith(".vtp"):
                continue
            vtp_count += 1
            matches = sorted(set(case_regex.findall(member.name)))
            if len(matches) != 1:
                unmapped_vtp += 1
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                raise AneuriskConformalDegreeP0Error("A VTP member could not be read.")
            with extracted:
                prefix = _read_prefix(
                    extracted, int(access["maximum_vtp_header_bytes_per_member"])
                )
            case_headers.setdefault(matches[0], []).append(inspect_vtp_header(prefix, access))

    case_ids = sorted(case_headers)
    every_polydata = all(
        row["polydata"] for rows in case_headers.values() for row in rows
    )
    per_case_coordinates = all(
        any(row["coordinate_three_component"] for row in rows)
        for rows in case_headers.values()
    )
    per_case_wss_sets = [
        {signature for row in rows for signature in row["wss_signatures"]}
        for rows in case_headers.values()
    ]
    common_wss = set.intersection(*per_case_wss_sets) if per_case_wss_sets else set()
    per_case_cycle_sets = [
        {signature for row in rows for signature in row["cycle_wss_signatures"]}
        for rows in case_headers.values()
    ]
    common_cycle = set.intersection(*per_case_cycle_sets) if per_case_cycle_sets else set()
    explicit_units_and_inputs = all(
        any(row["has_coordinate_unit_semantics"] for row in rows)
        and any(row["has_wss_unit_semantics"] for row in rows)
        and any(row["has_age_or_inflow_semantics"] for row in rows)
        for rows in case_headers.values()
    )
    return {
        "member_count": len(seen_names),
        "vtp_member_count": vtp_count,
        "unique_case_id_count": len(case_ids),
        "unmapped_vtp_count": unmapped_vtp,
        "link_count": links,
        "nonregular_member_count": nonregular,
        "safe_unique_regular_contract": safe,
        "every_vtp_is_polydata": every_polydata,
        "every_case_has_three_component_coordinates": per_case_coordinates,
        "common_wss_signatures": sorted(common_wss),
        "common_cycle_wss_signatures": sorted(common_cycle),
        "case_count_with_coordinate_unit_semantics": sum(
            any(row["has_coordinate_unit_semantics"] for row in rows)
            for rows in case_headers.values()
        ),
        "case_count_with_wss_unit_semantics": sum(
            any(row["has_wss_unit_semantics"] for row in rows)
            for rows in case_headers.values()
        ),
        "case_count_with_age_or_inflow_semantics": sum(
            any(row["has_age_or_inflow_semantics"] for row in rows)
            for rows in case_headers.values()
        ),
        "every_case_has_explicit_units_and_input_contract": explicit_units_and_inputs,
        "truncated_header_count": sum(
            int(row["header_prefix_truncated"])
            for rows in case_headers.values()
            for row in rows
        ),
    }


def run_p0(
    config: Mapping[str, Any], *, work_dir: Path, public_source_commit: str
) -> dict[str, Any]:
    if not _FULL_SHA.fullmatch(public_source_commit):
        raise AneuriskConformalDegreeP0Error("Public source commit must be a full SHA.")
    work_dir.mkdir(parents=True, exist_ok=True)
    archive_config = config["sources"]["archive"]
    archive_path = work_dir / archive_config["name"]
    transport = config["transport"]
    _download(
        archive_config["url"],
        archive_path,
        expected_bytes=int(archive_config["bytes"]),
        delays=[int(value) for value in transport["attempt_delays_seconds"]],
        timeout=int(transport["timeout_seconds_per_attempt"]),
        chunk_bytes=int(transport["chunk_bytes"]),
        user_agent=str(transport["user_agent"]),
    )
    exact_integrity = bool(
        archive_path.stat().st_size == int(archive_config["bytes"])
        and _md5(archive_path, int(transport["chunk_bytes"])) == archive_config["md5"]
    )
    aggregate = inspect_archive(archive_path, config)
    archive_path.unlink(missing_ok=True)

    access = config["access"]
    checks = {
        "exact_archive_bytes_and_md5_match": exact_integrity,
        "tar_contains_only_safe_unique_regular_members_without_links": bool(
            aggregate["safe_unique_regular_contract"]
            and aggregate["link_count"] == 0
            and aggregate["nonregular_member_count"] == 0
        ),
        "at_least_76_vtp_members_and_exactly_76_case_ids": bool(
            aggregate["vtp_member_count"] >= int(access["minimum_vtp_members"])
            and aggregate["unique_case_id_count"] == int(access["exact_unique_case_ids"])
            and aggregate["unmapped_vtp_count"] == 0
        ),
        "every_case_id_maps_to_at_least_one_vtp_member": bool(
            aggregate["unique_case_id_count"] == int(access["exact_unique_case_ids"])
        ),
        "every_vtp_header_identifies_vtk_polydata": bool(aggregate["every_vtp_is_polydata"]),
        "every_case_exposes_three_component_point_coordinates": bool(
            aggregate["every_case_has_three_component_coordinates"]
        ),
        "every_case_exposes_a_consistent_three_component_wss_vector_array": bool(
            aggregate["common_wss_signatures"]
        ),
        "cycle_averaged_vector_semantics_are_explicit_for_every_case": bool(
            aggregate["common_cycle_wss_signatures"]
        ),
        "coordinate_wss_units_and_age_or_inflow_input_contract_are_explicit": bool(
            aggregate["every_case_has_explicit_units_and_input_contract"]
        ),
        "no_extraction_conformal_model_gpu_outer_test_or_persistent_payload": True,
    }
    if list(checks) != list(config["gate"]["checks"]):
        raise AneuriskConformalDegreeP0Error("Implemented checks differ from registration.")
    gate_passed = all(checks.values())
    return {
        "schema_version": "aurora.aneurisk_conformal_degree_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "status": "passed_asset_semantics_gate" if gate_passed else "failed_asset_semantics_gate",
        "public_source_commit": public_source_commit,
        "config_sha256": config["_config_sha256"],
        "scientific_gate_evaluated": True,
        "gate_passed": gate_passed,
        "checks": checks,
        "aggregate": aggregate,
        "access": {
            "archive_downloaded_to_job_local_scratch": True,
            "archive_persisted": False,
            "vtp_member_persisted": False,
            "critical_point_extraction": False,
            "conformal_calibration": False,
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
            "schema_version": "aurora.aneurisk_conformal_degree_p0.result.v1",
            "protocol_id": config["protocol_id"],
            "status": "execution_incomplete_no_scientific_verdict",
            "public_source_commit": args.public_source_commit,
            "config_sha256": config["_config_sha256"],
            "scientific_gate_evaluated": False,
            "gate_passed": False,
            "error_class": type(exc).__name__,
            "access": {
                "archive_persisted": False,
                "vtp_member_persisted": False,
                "critical_point_extraction": False,
                "conformal_calibration": False,
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
