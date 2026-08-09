"""Prospective AneuX preprocessing-orbit P0 asset audit.

The audit downloads only the small official tabular archive.  For the 6.3 GB
model archive it reads the ZIP tail and central directory with exact HTTP byte
ranges and never reads a member payload.  Public output is aggregate-only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import posixpath
import struct
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneumo_range import ZipMember, parse_central_directory


class AneuXOrbitP0Error(RuntimeError):
    """Base error for the frozen P0 contract."""


class AneuXOrbitP0ExecutionIncomplete(AneuXOrbitP0Error):
    """Raised after the prospectively bounded transport attempts are exhausted."""


class AneuXOrbitP0ContractError(AneuXOrbitP0Error):
    """Raised when an accessed source violates the frozen scientific contract."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


RETRYABLE_HTTP = {408, 429, 500, 502, 503, 504}


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "aurora.aneux_preprocessing_orbit_p0.v1":
        raise AneuXOrbitP0ContractError("invalid_schema")
    if (
        payload.get("status")
        != "preregistered_before_tabular_or_model_archive_payload_access"
    ):
        raise AneuXOrbitP0ContractError("not_preregistered")
    candidate = payload["candidate"]
    if (
        int(candidate["source_shortlist_score"])
        < int(candidate["automatic_selection_threshold"])
        or candidate["method_selected"] is not False
        or candidate["architecture_selected"] is not False
        or candidate["gpu_training_authorized"] is not False
        or candidate["outer_test_authorized"] is not False
    ):
        raise AneuXOrbitP0ContractError("candidate_boundary_changed")
    transport = payload["transport"]
    if (
        int(transport["attempts_within_one_exact_job"]) != 3
        or transport["attempt_scope"]
        != "maximum_three_attempts_per_http_operation_within_the_single_exact_job"
        or list(transport["backoff_seconds"]) != [0, 10, 30]
        or transport["semantic_parser_or_contract_failure_retry"] is not False
        or transport["same_source_job_resubmission_allowed"] is not False
        or transport["full_model_archive_download_allowed"] is not False
    ):
        raise AneuXOrbitP0ContractError("transport_boundary_changed")
    execution = payload["execution"]
    if (
        execution["server"] != "introai9"
        or execution["scheduler"] != "pbs"
        or execution["gpu_requested"] is not False
        or execution["excluded_server"] != "junjinyong"
    ):
        raise AneuXOrbitP0ContractError("execution_boundary_changed")
    payload["_config_sha256"] = _sha256(source.read_bytes())
    return payload


def _safe_member_name(name: str) -> bool:
    normalized = posixpath.normpath(name.replace("\\", "/"))
    return bool(name) and not name.startswith(("/", "\\")) and not (
        normalized == ".." or normalized.startswith("../")
    )


class BoundedHttpClient:
    """HTTP client with exactly the frozen in-job transport retry policy."""

    def __init__(self, backoffs: Sequence[int]):
        self.backoffs = [int(value) for value in backoffs]
        self.range_bytes_read = 0

    def _open(self, request: urllib.request.Request, *, timeout: int = 120) -> Any:
        last_error: BaseException | None = None
        for attempt, delay in enumerate(self.backoffs):
            if delay:
                time.sleep(delay)
            try:
                return urllib.request.urlopen(request, timeout=timeout)
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRYABLE_HTTP:
                    raise AneuXOrbitP0ContractError(
                        f"nonretryable_http_{exc.code}"
                    ) from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                last_error = exc
            if attempt + 1 == len(self.backoffs):
                break
        raise AneuXOrbitP0ExecutionIncomplete("transport_attempts_exhausted") from last_error

    def head(self, url: str) -> Mapping[str, str]:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "AURORA-AneuX-orbit-P0/1.0"},
            method="HEAD",
        )
        with self._open(request) as response:
            return {key.lower(): value for key, value in response.headers.items()}

    def range(self, url: str, start: int, end: int) -> bytes:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AURORA-AneuX-orbit-P0/1.0",
                "Range": f"bytes={start}-{end}",
            },
        )
        with self._open(request) as response:
            status = int(getattr(response, "status", 0))
            headers = {key.lower(): value for key, value in response.headers.items()}
            expected_prefix = f"bytes {start}-{end}/"
            if status != 206 or not headers.get("content-range", "").startswith(
                expected_prefix
            ):
                raise AneuXOrbitP0ContractError("exact_range_not_honored")
            payload = response.read()
        expected = end - start + 1
        if len(payload) != expected:
            raise AneuXOrbitP0ContractError("range_length_mismatch")
        self.range_bytes_read += len(payload)
        return payload

    def download(self, url: str, destination: Path, expected_bytes: int) -> None:
        request = urllib.request.Request(
            url, headers={"User-Agent": "AURORA-AneuX-orbit-P0/1.0"}
        )
        temporary = destination.with_name(f".{destination.name}.partial-{os.getpid()}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        last_error: BaseException | None = None
        for attempt, delay in enumerate(self.backoffs):
            if delay:
                time.sleep(delay)
            try:
                if temporary.exists():
                    temporary.unlink()
                total = 0
                with self._open_once(request) as response, temporary.open("wb") as handle:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > expected_bytes:
                            raise AneuXOrbitP0ContractError("tabular_download_oversized")
                        handle.write(chunk)
                if total != expected_bytes:
                    raise urllib.error.URLError("short_read")
                temporary.replace(destination)
                return
            except AneuXOrbitP0ContractError:
                if temporary.exists():
                    temporary.unlink()
                raise
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRYABLE_HTTP:
                    if temporary.exists():
                        temporary.unlink()
                    raise AneuXOrbitP0ContractError(
                        f"nonretryable_http_{exc.code}"
                    ) from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                last_error = exc
            if temporary.exists():
                temporary.unlink()
            if attempt + 1 == len(self.backoffs):
                break
        raise AneuXOrbitP0ExecutionIncomplete("transport_attempts_exhausted") from last_error

    @staticmethod
    def _open_once(request: urllib.request.Request, *, timeout: int = 120) -> Any:
        return urllib.request.urlopen(request, timeout=timeout)


def load_remote_zip_index(
    client: BoundedHttpClient, url: str, expected_size: int
) -> tuple[dict[str, ZipMember], dict[str, Any]]:
    headers = client.head(url)
    try:
        size = int(headers["content-length"])
    except (KeyError, ValueError) as exc:
        raise AneuXOrbitP0ContractError("model_head_missing_content_length") from exc
    if size != int(expected_size):
        raise AneuXOrbitP0ContractError("model_archive_size_mismatch")

    tail_start = max(0, size - 1_048_576)
    tail = client.range(url, tail_start, size - 1)
    eocd_position = tail.rfind(b"PK\x05\x06")
    if eocd_position < 0 or eocd_position + 22 > len(tail):
        raise AneuXOrbitP0ContractError("zip_eocd_missing")
    eocd = struct.unpack_from("<4s4H2LH", tail, eocd_position)
    entries = int(eocd[4])
    central_size = int(eocd[5])
    central_offset = int(eocd[6])
    zip64 = entries == 0xFFFF or central_size == 0xFFFFFFFF or central_offset == 0xFFFFFFFF
    if zip64:
        locator_position = tail.rfind(b"PK\x06\x07", 0, eocd_position)
        if locator_position < 0 or locator_position + 20 > len(tail):
            raise AneuXOrbitP0ContractError("zip64_locator_missing")
        _, _, zip64_offset, disks = struct.unpack_from(
            "<4sLQL", tail, locator_position
        )
        if int(disks) != 1:
            raise AneuXOrbitP0ContractError("multidisk_zip_unsupported")
        relative = int(zip64_offset) - tail_start
        if 0 <= relative and relative + 56 <= len(tail):
            zip64_record = tail[relative : relative + 56]
        else:
            zip64_record = client.range(
                url, int(zip64_offset), int(zip64_offset) + 55
            )
        values = struct.unpack_from("<4sQ2H2L4Q", zip64_record, 0)
        if values[0] != b"PK\x06\x06":
            raise AneuXOrbitP0ContractError("zip64_eocd_invalid")
        entries = int(values[7])
        central_size = int(values[8])
        central_offset = int(values[9])
    if entries <= 0 or central_size <= 0:
        raise AneuXOrbitP0ContractError("empty_central_directory")
    central = client.range(
        url, central_offset, central_offset + central_size - 1
    )
    try:
        members = parse_central_directory(central)
    except Exception as exc:
        raise AneuXOrbitP0ContractError("central_directory_parse_failed") from exc
    if len(members) != entries:
        raise AneuXOrbitP0ContractError("central_directory_entry_count_mismatch")
    return members, {
        "archive_bytes": size,
        "entries": entries,
        "central_directory_bytes": central_size,
        "zip64": zip64,
        "range_bytes_read": client.range_bytes_read,
    }


def _find_member(names: Sequence[str], basename: str) -> str:
    matches = [name for name in names if posixpath.basename(name) == basename]
    if len(matches) != 1:
        raise AneuXOrbitP0ContractError(f"required_member_{basename}_count")
    return matches[0]


def _read_csv(archive: zipfile.ZipFile, name: str) -> tuple[list[str], list[dict[str, str]]]:
    with archive.open(name) as handle:
        wrapper = io.TextIOWrapper(handle, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(wrapper)
        if reader.fieldnames is None:
            raise AneuXOrbitP0ContractError("csv_header_missing")
        rows = [
            {str(key): "" if value is None else str(value).strip() for key, value in row.items()}
            for row in reader
        ]
        return [str(item) for item in reader.fieldnames], rows


def _canonical_status(value: str) -> str:
    token = value.strip().lower()
    if token in {"r", "ruptured", "1", "true"}:
        return "ruptured"
    if token in {"u", "unruptured", "0", "false"}:
        return "unruptured"
    return "missing"


def _canonical_cut(value: str) -> str:
    token = value.strip().lower().replace("_", "-").replace(" ", "")
    aliases = {"cut-1": "cut1", "cut-2": "cut2"}
    return aliases.get(token, token)


def audit_tabular_archive(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if any(not _safe_member_name(name) for name in names):
            raise AneuXOrbitP0ContractError("unsafe_tabular_member_path")
        required = {
            basename: _find_member(names, basename)
            for basename in (
                "clinical.csv",
                "clinical-per-cut.csv",
                "morpho-per-cut.csv",
            )
        }
        clinical_header, clinical = _read_csv(archive, required["clinical.csv"])
        per_cut_header, per_cut = _read_csv(
            archive, required["clinical-per-cut.csv"]
        )
        morpho_header, morpho = _read_csv(archive, required["morpho-per-cut.csv"])

    required_clinical = {
        "source",
        "dataset",
        "status",
        "patientID",
        "vesselFileID",
    }
    if not required_clinical.issubset(clinical_header):
        raise AneuXOrbitP0ContractError("clinical_columns_missing")
    if not {"dataset", "cutType"}.issubset(per_cut_header) or not {
        "dataset",
        "cutType",
    }.issubset(morpho_header):
        raise AneuXOrbitP0ContractError("per_cut_key_columns_missing")

    lesion_ids = [row["dataset"] for row in clinical]
    source_counts = Counter(row["source"] for row in clinical)
    status_counts = Counter(_canonical_status(row["status"]) for row in clinical)
    observed_patient_rows = [row for row in clinical if row["patientID"]]
    patient_groups = {
        (row["source"], row["patientID"]) for row in observed_patient_rows
    }

    clinical_keys = [
        (row["dataset"], _canonical_cut(row["cutType"])) for row in per_cut
    ]
    morpho_keys = [
        (row["dataset"], _canonical_cut(row["cutType"])) for row in morpho
    ]
    cuts_by_lesion: dict[str, set[str]] = defaultdict(set)
    for lesion, cut in clinical_keys:
        cuts_by_lesion[lesion].add(cut)
    feature_columns = [
        name
        for name in morpho_header
        if name not in {"dataset", "cutType"}
        and not name.strip().lower().startswith("unnamed")
    ]
    return {
        "zip_members": len(names),
        "required_csv_members": len(required),
        "clinical_rows": len(clinical),
        "unique_lesions": len(set(lesion_ids)),
        "clinical_lesion_ids_unique": len(lesion_ids) == len(set(lesion_ids)),
        "source_counts": dict(sorted(source_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "patient_id_observed_rows": len(observed_patient_rows),
        "observed_patient_groups": len(patient_groups),
        "clinical_per_cut_rows": len(per_cut),
        "morphometry_rows": len(morpho),
        "clinical_per_cut_keys_unique": len(clinical_keys) == len(set(clinical_keys)),
        "morphometry_keys_unique": len(morpho_keys) == len(set(morpho_keys)),
        "per_cut_key_sets_match": set(clinical_keys) == set(morpho_keys),
        "cut_types": sorted({cut for _, cut in clinical_keys}),
        "lesions_with_dome_and_ninja": sum(
            {"dome", "ninja"}.issubset(cuts) for cuts in cuts_by_lesion.values()
        ),
        "morphometric_feature_columns": len(feature_columns),
    }


def summarize_model_members(members: Mapping[str, ZipMember]) -> dict[str, Any]:
    names = list(members)
    safe = all(_safe_member_name(name) for name in names)
    aneurysm_vtp = [
        name
        for name in names
        if name.lower().endswith(".vtp")
        and "models/aneurysms/" in name.lower().replace("\\", "/")
    ]
    resolution_counts = {
        token: sum(token in name.lower() for name in aneurysm_vtp)
        for token in ("original", "area-001", "area-005")
    }
    cut_counts = {
        token: sum(token in name.lower() for name in aneurysm_vtp)
        for token in ("dome", "ninja", "cut1", "cut2")
    }
    listing_hash = hashlib.sha256(
        "\n".join(sorted(names)).encode("utf-8")
    ).hexdigest()
    return {
        "safe_member_paths": safe,
        "aneurysm_vtp_members": len(aneurysm_vtp),
        "resolution_token_counts": resolution_counts,
        "cut_token_counts": cut_counts,
        "member_name_listing_sha256": listing_hash,
        "model_member_payload_bytes_read": 0,
    }


def evaluate_checks(
    config: Mapping[str, Any],
    tabular_path: Path,
    tabular: Mapping[str, Any],
    model_index: Mapping[str, Any],
    model_members: Mapping[str, Any],
) -> dict[str, bool]:
    expected = config["expected_contract"]
    tabular_source = config["source"]["files"]["tabular"]
    required_cuts = set(expected["cut_types"])
    required_resolutions = set(expected["mesh_resolutions"])
    return {
        "tabular_file_size_and_md5_match": (
            tabular_path.stat().st_size == int(tabular_source["bytes"])
            and _md5_file(tabular_path) == tabular_source["md5"]
        ),
        "required_csv_members_exist_and_have_safe_paths": (
            int(tabular["required_csv_members"]) == 3
        ),
        "clinical_has_exact_750_unique_lesions_and_source_counts": (
            int(tabular["clinical_rows"]) == int(expected["lesions"])
            and int(tabular["unique_lesions"]) == int(expected["lesions"])
            and tabular["clinical_lesion_ids_unique"] is True
            and dict(tabular["source_counts"]) == dict(expected["sources"])
        ),
        "status_and_patient_id_availability_match_source_contract": (
            int(tabular["status_counts"].get("ruptured", 0))
            == int(expected["status_ruptured"])
            and int(tabular["status_counts"].get("unruptured", 0))
            == int(expected["status_unruptured"])
            and int(tabular["patient_id_observed_rows"])
            == int(expected["patient_id_observed_rows"])
        ),
        "at_least_450_source_qualified_observed_patient_groups_exist": (
            int(tabular["observed_patient_groups"])
            >= int(expected["minimum_observed_patient_groups"])
        ),
        "clinical_per_cut_and_morphometry_have_identical_unique_dataset_cut_keys": (
            tabular["clinical_per_cut_keys_unique"] is True
            and tabular["morphometry_keys_unique"] is True
            and tabular["per_cut_key_sets_match"] is True
        ),
        "all_four_cut_types_exist_and_every_lesion_has_dome_and_ninja": (
            set(tabular["cut_types"]) == required_cuts
            and int(tabular["lesions_with_dome_and_ninja"])
            == int(expected["lesions"])
        ),
        "morphometry_has_exactly_170_non_index_feature_columns": (
            int(tabular["morphometric_feature_columns"])
            == int(expected["morphometric_feature_columns"])
        ),
        "model_archive_size_matches_and_exact_byte_ranges_are_honored": (
            int(model_index["archive_bytes"])
            == int(config["source"]["files"]["models"]["bytes"])
            and int(model_index["range_bytes_read"]) > 0
            and int(model_index["range_bytes_read"]) < int(model_index["archive_bytes"])
        ),
        "model_central_directory_is_valid_safe_and_contains_all_resolution_and_cut_tokens": (
            int(model_index["entries"]) > 0
            and model_members["safe_member_paths"] is True
            and {
                key
                for key, value in model_members["resolution_token_counts"].items()
                if int(value) > 0
            }
            == required_resolutions
            and {
                key
                for key, value in model_members["cut_token_counts"].items()
                if int(value) > 0
            }
            == required_cuts
        ),
        "model_archive_contains_at_least_4500_aneurysm_vtp_members": (
            int(model_members["aneurysm_vtp_members"])
            >= int(expected["minimum_aneurysm_vtp_members"])
        ),
        "no_model_member_payload_case_identifier_or_case_level_value_is_published": (
            int(model_members["model_member_payload_bytes_read"]) == 0
        ),
        "no_method_architecture_gpu_or_outer_test_is_opened": (
            config["candidate"]["method_selected"] is False
            and config["candidate"]["architecture_selected"] is False
            and config["candidate"]["gpu_training_authorized"] is False
            and config["candidate"]["outer_test_authorized"] is False
        ),
    }


def _source_commit() -> str:
    explicit = os.environ.get("AURORA_SOURCE_COMMIT", "").strip()
    if explicit:
        return explicit
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run(config: Mapping[str, Any], cache_dir: Path) -> dict[str, Any]:
    client = BoundedHttpClient(config["transport"]["backoff_seconds"])
    tabular_source = config["source"]["files"]["tabular"]
    model_source = config["source"]["files"]["models"]
    tabular_path = cache_dir / tabular_source["name"]
    client.download(tabular_source["url"], tabular_path, int(tabular_source["bytes"]))
    if _md5_file(tabular_path) != tabular_source["md5"]:
        raise AneuXOrbitP0ContractError("tabular_md5_mismatch")
    tabular = audit_tabular_archive(tabular_path)
    members, model_index = load_remote_zip_index(
        client, model_source["url"], int(model_source["bytes"])
    )
    model_summary = summarize_model_members(members)
    checks = evaluate_checks(config, tabular_path, tabular, model_index, model_summary)
    passed = all(checks.values())
    return {
        "schema_version": "aurora.aneux_preprocessing_orbit_p0.result.v1",
        "experiment_id": config["experiment_id"],
        "as_of": config["as_of"],
        "status": "passed_asset_only" if passed else "failed_asset_contract",
        "scientific_gate_evaluated": True,
        "gate": {
            "passed": passed,
            "checks_passed": sum(checks.values()),
            "checks_total": len(checks),
            "checks": checks,
            "pass_authorizes": config["gate"]["pass_authorizes"],
        },
        "source": {
            "doi": config["source"]["doi"],
            "version": config["source"]["version"],
            "license": config["source"]["license"],
            "config_sha256": config["_config_sha256"],
            "source_commit": _source_commit(),
        },
        "aggregate": {
            "tabular": tabular,
            "model_archive": model_index,
            "model_members": model_summary,
        },
        "privacy": {
            "case_identifiers_published": False,
            "case_level_values_published": False,
            "model_member_payload_bytes_read": 0,
            "raw_or_processed_payload_committed": False,
        },
        "authorization": {
            "primary_problem_selected": False,
            "method_selected": False,
            "architecture_selected": False,
            "gpu_training_authorized": False,
            "outer_test_authorized": False,
            "submission_identity_active": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        print(
            "AneuX preprocessing-orbit P0 contract valid · "
            f"sha256 {config['_config_sha256']}"
        )
        return 0
    if args.cache_dir is None or args.result is None:
        parser.error("--cache-dir and --result are required unless --validate-only is used")
    try:
        result = run(config, args.cache_dir)
        exit_code = 0
    except AneuXOrbitP0ExecutionIncomplete:
        result = {
            "schema_version": "aurora.aneux_preprocessing_orbit_p0.result.v1",
            "experiment_id": config["experiment_id"],
            "as_of": config["as_of"],
            "status": "execution_incomplete_no_scientific_verdict",
            "scientific_gate_evaluated": False,
            "error_code": "transport_attempts_exhausted",
            "source": {
                "config_sha256": config["_config_sha256"],
                "source_commit": _source_commit(),
            },
            "authorization": {
                "primary_problem_selected": False,
                "method_selected": False,
                "architecture_selected": False,
                "gpu_training_authorized": False,
                "outer_test_authorized": False,
                "submission_identity_active": False,
            },
        }
        exit_code = 2
    except AneuXOrbitP0ContractError as exc:
        result = {
            "schema_version": "aurora.aneux_preprocessing_orbit_p0.result.v1",
            "experiment_id": config["experiment_id"],
            "as_of": config["as_of"],
            "status": "failed_asset_contract",
            "scientific_gate_evaluated": True,
            "error_code": exc.code,
            "source": {
                "config_sha256": config["_config_sha256"],
                "source_commit": _source_commit(),
            },
            "authorization": {
                "primary_problem_selected": False,
                "method_selected": False,
                "architecture_selected": False,
                "gpu_training_authorized": False,
                "outer_test_authorized": False,
                "submission_identity_active": False,
            },
        }
        exit_code = 0
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
