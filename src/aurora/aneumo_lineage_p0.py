"""Prospective metadata-only Aneumo generation-lineage P0.

The audit reads only pinned small text/CSV files and Git LFS pointer text.  It
never resolves an LFS object or reads a ZIP central directory/member payload.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class AneumoLineageP0Error(RuntimeError):
    """Base error for the frozen P0 contract."""


class AneumoLineageP0ExecutionIncomplete(AneumoLineageP0Error):
    """Raised after the bounded small-source transport attempts are exhausted."""


class AneumoLineageP0ContractError(AneumoLineageP0Error):
    """Raised when config or accessed metadata violates the frozen contract."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


RETRYABLE_HTTP = {408, 429, 500, 502, 503, 504}
FAMILY_PATTERN = re.compile(r"^(?P<family>[1-9][0-9]*)_deform_(?P<index>[1-9][0-9]*)$")
LFS_PATTERN = re.compile(
    r"\Aversion https://git-lfs\.github\.com/spec/v1\n"
    r"oid sha256:(?P<oid>[0-9a-f]{64})\n"
    r"size (?P<size>[1-9][0-9]*)\n?\Z"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_config_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("schema_version") != "aurora.aneumo_lineage_p0.v1":
        raise AneumoLineageP0ContractError("invalid_schema")
    if payload.get("protocol_id") != "aneumo_generation_lineage_p0_v1":
        raise AneumoLineageP0ContractError("invalid_protocol_id")
    if payload.get("status") != (
        "preregistered_before_any_aneumo_archive_or_member_payload_access"
    ):
        raise AneumoLineageP0ContractError("not_preregistered")

    candidate = payload["candidate"]
    if (
        float(candidate["score"]) < float(candidate["automatic_selection_threshold"])
        or abs(sum(float(value) for value in candidate["axis_scores"]) - float(candidate["score"])) > 1e-12
        or int(candidate["active_source_shortlist_count"]) != 1
        or candidate["primary_problem_selected"] is not False
        or candidate["method_selected"] is not False
        or candidate["architecture_selected"] is not False
        or candidate["gpu_training_authorized"] is not False
        or candidate["outer_test_authorized"] is not False
        or candidate["submission_identity_active"] is not False
    ):
        raise AneumoLineageP0ContractError("candidate_boundary_changed")

    transport = payload["transport"]
    if (
        int(transport["attempts_per_small_source_within_one_exact_job"]) != 3
        or list(transport["backoff_seconds"]) != [0, 10, 30]
        or transport["same_source_job_resubmission_allowed"] is not False
        or transport["archive_or_lfs_object_resolution_allowed"] is not False
    ):
        raise AneumoLineageP0ContractError("transport_boundary_changed")

    execution = payload["execution"]
    if (
        execution["server"] != "introai9"
        or execution["scheduler"] != "pbs"
        or execution["gpu_requested"] is not False
        or execution["login_node_training_or_gpu_command"] is not False
        or execution["excluded_server"] != "junjinyong"
    ):
        raise AneumoLineageP0ContractError("execution_boundary_changed")

    small_files = payload["sources"]["small_files"]
    expected_ids = {
        "connection",
        "morphometry",
        "train",
        "validation",
        "github_readme",
        "datasheet",
        "hf_readme",
        "steady_pointer",
        "transient_pointer",
    }
    if {item["id"] for item in small_files} != expected_ids:
        raise AneumoLineageP0ContractError("small_source_set_changed")
    if any(
        not str(item["url"]).startswith(("https://raw.githubusercontent.com/", "https://huggingface.co/"))
        or not re.fullmatch(r"[0-9a-f]{64}", str(item["sha256"]))
        or int(item["bytes"]) <= 0
        or int(item["bytes"]) > 4_000_000
        for item in small_files
    ):
        raise AneumoLineageP0ContractError("small_source_boundary_changed")


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    validate_config_payload(payload)

    payload["_config_sha256"] = sha256_bytes(source.read_bytes())
    return payload


class BoundedSmallSourceClient:
    """Download only preregistered small files with bounded in-job retries."""

    def __init__(self, backoffs: Sequence[int]):
        self.backoffs = [int(value) for value in backoffs]
        self.total_bytes_read = 0

    def fetch(self, url: str, expected_bytes: int) -> bytes:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "AURORA-Aneumo-lineage-P0/1.0"},
        )
        last_error: BaseException | None = None
        for attempt, delay in enumerate(self.backoffs):
            if delay:
                time.sleep(delay)
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    payload = response.read(expected_bytes + 1)
                if len(payload) != expected_bytes:
                    raise AneumoLineageP0ContractError("small_source_size_mismatch")
                self.total_bytes_read += len(payload)
                return payload
            except AneumoLineageP0ContractError:
                raise
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRYABLE_HTTP:
                    raise AneumoLineageP0ContractError(
                        f"nonretryable_http_{exc.code}"
                    ) from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                last_error = exc
            if attempt + 1 == len(self.backoffs):
                break
        raise AneumoLineageP0ExecutionIncomplete(
            "transport_attempts_exhausted"
        ) from last_error


def parse_csv(payload: bytes) -> tuple[list[str], list[dict[str, str]]]:
    wrapper = io.StringIO(payload.decode("utf-8-sig"), newline="")
    reader = csv.DictReader(wrapper)
    if reader.fieldnames is None:
        raise AneumoLineageP0ContractError("csv_header_missing")
    rows = [
        {str(key): "" if value is None else str(value).strip() for key, value in row.items()}
        for row in reader
    ]
    return [str(item) for item in reader.fieldnames], rows


def parse_mapping(payload: bytes) -> tuple[dict[int, tuple[int, int]], dict[int, list[int]]]:
    fields, rows = parse_csv(payload)
    if fields != ["case_id", "connection"]:
        raise AneumoLineageP0ContractError("mapping_header_changed")
    mapping: dict[int, tuple[int, int]] = {}
    families: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        try:
            case_id = int(row["case_id"])
        except ValueError as exc:
            raise AneumoLineageP0ContractError("invalid_mapping_case_id") from exc
        match = FAMILY_PATTERN.fullmatch(row["connection"])
        if match is None:
            raise AneumoLineageP0ContractError("invalid_mapping_connection")
        family = int(match.group("family"))
        deformation = int(match.group("index"))
        if case_id in mapping:
            raise AneumoLineageP0ContractError("duplicate_mapping_case_id")
        mapping[case_id] = (family, deformation)
        families[family].append(deformation)
    return mapping, dict(families)


def parse_split(payload: bytes) -> dict[int, tuple[int, int]]:
    fields, rows = parse_csv(payload)
    if fields != ["case_id", "connect"]:
        raise AneumoLineageP0ContractError("split_header_changed")
    result: dict[int, tuple[int, int]] = {}
    for row in rows:
        case_id = int(row["case_id"])
        match = FAMILY_PATTERN.fullmatch(row["connect"])
        if match is None or case_id in result:
            raise AneumoLineageP0ContractError("invalid_split_row")
        result[case_id] = (int(match.group("family")), int(match.group("index")))
    return result


def parse_morphometry_keys(payload: bytes) -> set[int]:
    fields, rows = parse_csv(payload)
    if not fields or fields[0] != "case_id":
        raise AneumoLineageP0ContractError("morphometry_header_changed")
    try:
        keys = [int(row["case_id"]) for row in rows]
    except ValueError as exc:
        raise AneumoLineageP0ContractError("invalid_morphometry_case_id") from exc
    if len(set(keys)) != len(keys):
        raise AneumoLineageP0ContractError("duplicate_morphometry_case_id")
    return set(keys)


def parse_lfs_pointer(payload: bytes) -> tuple[str, int]:
    match = LFS_PATTERN.fullmatch(payload.decode("ascii"))
    if match is None:
        raise AneumoLineageP0ContractError("invalid_lfs_pointer")
    return match.group("oid"), int(match.group("size"))


def _all_equal(values: Iterable[object]) -> bool:
    values = list(values)
    return bool(values) and all(value == values[0] for value in values[1:])


def audit_payloads(config: Mapping[str, Any], payloads: Mapping[str, bytes]) -> dict[str, Any]:
    expected = config["expected_contract"]
    mapping, family_indices = parse_mapping(payloads["connection"])
    morphometry_keys = parse_morphometry_keys(payloads["morphometry"])
    train = parse_split(payloads["train"])
    validation = parse_split(payloads["validation"])

    family_counts = [len(indices) for indices in family_indices.values()]
    mapping_contiguous = all(
        sorted(indices) == list(range(1, len(indices) + 1))
        and len(indices) == len(set(indices))
        for indices in family_indices.values()
    )
    split_rows_match_mapping = all(
        mapping.get(case_id) == lineage
        for split in (train, validation)
        for case_id, lineage in split.items()
    )
    train_families = {lineage[0] for lineage in train.values()}
    validation_families = {lineage[0] for lineage in validation.values()}
    case_overlap = set(train) & set(validation)
    family_overlap = train_families & validation_families
    overlap_fraction = len(family_overlap) / len(validation_families)

    datasheet = payloads["datasheet"].decode("utf-8")
    github_readme = payloads["github_readme"].decode("utf-8")
    hf_readme = payloads["hf_readme"].decode("utf-8")
    steady_oid, steady_size = parse_lfs_pointer(payloads["steady_pointer"])
    transient_oid, transient_size = parse_lfs_pointer(payloads["transient_pointer"])

    checks = {
        "mapping_row_count": len(mapping) == int(expected["mapping_rows"]),
        "mapping_family_count": len(family_indices) == int(expected["base_families"]),
        "mapping_minimum_deformations": min(family_counts) == int(expected["minimum_deformations_per_family"]),
        "mapping_maximum_deformations": max(family_counts) == int(expected["maximum_deformations_per_family"]),
        "mapping_deformations_contiguous": mapping_contiguous,
        "morphometry_row_count": len(morphometry_keys) == int(expected["morphometry_rows"]),
        "morphometry_keys_match_mapping": morphometry_keys == set(mapping),
        "split_rows_match_mapping": split_rows_match_mapping,
        "train_case_count": len(train) == int(expected["train_cases"]),
        "train_family_count": len(train_families) == int(expected["train_families"]),
        "validation_case_count": len(validation) == int(expected["validation_cases"]),
        "validation_family_count": len(validation_families) == int(expected["validation_families"]),
        "exact_case_overlap": len(case_overlap) == int(expected["exact_case_overlap"]),
        "base_family_overlap": len(family_overlap) == int(expected["base_family_overlap"]),
        "validation_family_overlap_fraction": abs(overlap_fraction - float(expected["validation_family_overlap_fraction"])) < 1e-12,
        "datasheet_no_geometric_overlap_claim_present": "no geometric overlap with training" in datasheet,
        "github_cc_by_text_present": expected["github_license_text"] in datasheet,
        "hf_license_token_present": f"license: {expected['huggingface_license_token']}" in hf_readme,
        "license_conflict_detected": expected["license_sources_agree"] is False and expected["github_license_text"] in datasheet and f"license: {expected['huggingface_license_token']}" in hf_readme,
        "steady_lfs_pointer_matches": steady_oid == expected["steady_lfs_oid"] and steady_size == int(expected["steady_lfs_bytes"]),
        "transient_lfs_pointer_matches": transient_oid == expected["transient_lfs_oid"] and transient_size == int(expected["transient_lfs_bytes"]),
        "source_readme_identifies_427_bases": "427 real aneurysm geometries" in github_readme,
    }
    return {
        "checks": checks,
        "aggregates": {
            "mapping_rows": len(mapping),
            "base_families": len(family_indices),
            "minimum_deformations_per_family": min(family_counts),
            "maximum_deformations_per_family": max(family_counts),
            "morphometry_rows": len(morphometry_keys),
            "train_cases": len(train),
            "train_families": len(train_families),
            "validation_cases": len(validation),
            "validation_families": len(validation_families),
            "exact_case_overlap": len(case_overlap),
            "base_family_overlap": len(family_overlap),
            "validation_family_overlap_fraction": overlap_fraction,
            "license_sources_agree": False,
            "steady_lfs_bytes": steady_size,
            "transient_lfs_bytes": transient_size,
        },
    }


def run_audit(config: Mapping[str, Any], cache_dir: Path) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    client = BoundedSmallSourceClient(config["transport"]["backoff_seconds"])
    payloads: dict[str, bytes] = {}
    observed_hashes: dict[str, str] = {}
    for item in config["sources"]["small_files"]:
        payload = client.fetch(str(item["url"]), int(item["bytes"]))
        digest = sha256_bytes(payload)
        if digest != item["sha256"]:
            raise AneumoLineageP0ContractError(f"sha256_mismatch_{item['id']}")
        payloads[str(item["id"])] = payload
        observed_hashes[str(item["id"])] = digest
        # Cache stays private to the exact run and contains small public metadata only.
        (cache_dir / f"{item['id']}.source").write_bytes(payload)

    audited = audit_payloads(config, payloads)
    all_checks_pass = all(bool(value) for value in audited["checks"].values())
    return {
        "schema_version": "aurora.aneumo_lineage_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "status": config["gate"]["pass_status"] if all_checks_pass else "failed_metadata_contract",
        "scientific_gate_evaluated": True,
        "all_checks_pass": all_checks_pass,
        "public_source_commit": os.environ.get("AURORA_SOURCE_COMMIT", "unrecorded"),
        "config_sha256": config["_config_sha256"],
        "github_source_commit": config["sources"]["github_commit"],
        "huggingface_source_commit": config["sources"]["huggingface_commit"],
        "small_source_bytes_read": client.total_bytes_read,
        "small_source_sha256": observed_hashes,
        "checks": audited["checks"],
        "aggregates": audited["aggregates"],
        "license_hold": True,
        "archive_central_directory_accessed": False,
        "archive_member_payload_accessed": False,
        "lfs_object_resolved": False,
        "method_accessed": False,
        "architecture_selected": False,
        "gpu_accessed": False,
        "outer_test_accessed": False,
        "next_authorized_action": config["gate"]["pass_authorizes"] if all_checks_pass else config["gate"]["failure_action"],
    }


def _write_result(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = run_audit(config, args.cache_dir)
        _write_result(args.result, result)
        return 0 if result["all_checks_pass"] else 1
    except AneumoLineageP0ExecutionIncomplete as exc:
        _write_result(
            args.result,
            {
                "schema_version": "aurora.aneumo_lineage_p0.result.v1",
                "protocol_id": "aneumo_generation_lineage_p0_v1",
                "status": "execution_incomplete_no_scientific_verdict",
                "reason": str(exc),
                "scientific_gate_evaluated": False,
                "archive_central_directory_accessed": False,
                "archive_member_payload_accessed": False,
                "lfs_object_resolved": False,
                "method_accessed": False,
                "gpu_accessed": False,
                "outer_test_accessed": False,
            },
        )
        return 2
    except AneumoLineageP0ContractError as exc:
        _write_result(
            args.result,
            {
                "schema_version": "aurora.aneumo_lineage_p0.result.v1",
                "protocol_id": "aneumo_generation_lineage_p0_v1",
                "status": "failed_metadata_contract",
                "reason": exc.code,
                "scientific_gate_evaluated": True,
                "archive_central_directory_accessed": False,
                "archive_member_payload_accessed": False,
                "lfs_object_resolved": False,
                "method_accessed": False,
                "gpu_accessed": False,
                "outer_test_accessed": False,
            },
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
