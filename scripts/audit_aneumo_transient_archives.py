#!/usr/bin/env python3
"""Bounded metadata-only audit of the pinned public Aneumo transient release.

The public release stores ten inner case ZIPs without compression inside each
large batch ZIP.  This program reads only ZIP local headers and the final
central-directory window of each archive.  It never downloads an inner file
payload and fails if a server ignores a byte-range request.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import re
import struct
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REVISION = "f801adee816c18d3e18b23e6fcb147fe4c264209"
REPOSITORY = "SAIS-Life-Science/Aneumo"
DEFAULT_TAIL_BYTES = 65_536
DEFAULT_MAX_BYTES = 100_000_000


@dataclass(frozen=True)
class RangeBlock:
    data: bytes
    start: int
    end: int
    total: int


@dataclass(frozen=True)
class ZipEntry:
    name: str
    method: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    local_header_offset: int


class AuditError(RuntimeError):
    """A fail-closed archive or transport contract error."""


class RangeClient:
    def __init__(self, *, max_bytes: int, retries: int = 4) -> None:
        self.max_bytes = max_bytes
        self.retries = retries
        self.bytes_read = 0
        self.requests = 0
        self._lock = threading.Lock()

    def get(self, url: str, range_value: str) -> RangeBlock:
        last_error: Exception | None = None
        for attempt in range(self.retries):
            request = urllib.request.Request(
                url,
                headers={
                    "Range": range_value,
                    "User-Agent": "AURORA-Aneumo-metadata-audit/1.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    status = getattr(response, "status", response.getcode())
                    content_range = response.headers.get("Content-Range", "")
                    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
                    if status != 206 or match is None:
                        raise AuditError(
                            "server did not honor bounded range request: "
                            f"status={status}, content-range={content_range!r}"
                        )
                    start, end, total = map(int, match.groups())
                    expected = end - start + 1
                    with self._lock:
                        if self.bytes_read + expected > self.max_bytes:
                            raise AuditError(
                                f"network byte ceiling exceeded: {self.max_bytes}"
                            )
                        self.bytes_read += expected
                        self.requests += 1
                    data = response.read(expected + 1)
                    if len(data) != expected:
                        raise AuditError(
                            f"short or oversized range body: {len(data)} != {expected}"
                        )
                    return RangeBlock(data=data, start=start, end=end, total=total)
            except (urllib.error.URLError, TimeoutError, AuditError) as exc:
                last_error = exc
                if isinstance(exc, AuditError):
                    raise
                if attempt + 1 < self.retries:
                    time.sleep(0.5 * (2**attempt))
        raise AuditError(f"range request failed after retries: {last_error}")


def _zip64_values(extra: bytes) -> list[int]:
    position = 0
    while position + 4 <= len(extra):
        field_id, length = struct.unpack_from("<HH", extra, position)
        value = extra[position + 4 : position + 4 + length]
        position += 4 + length
        if field_id == 0x0001:
            if len(value) % 8:
                raise AuditError("malformed ZIP64 extra field")
            return list(struct.unpack("<" + "Q" * (len(value) // 8), value))
    return []


def parse_central_directory(block: RangeBlock) -> list[ZipEntry]:
    data = block.data
    eocd = data.rfind(b"PK\x05\x06")
    if eocd < 0 or eocd + 22 > len(data):
        raise AuditError("EOCD is absent from bounded tail")
    classic = struct.unpack_from("<4s4H2IH", data, eocd)
    entry_count, directory_size, directory_offset = classic[4:7]

    if (
        entry_count == 0xFFFF
        or directory_size == 0xFFFFFFFF
        or directory_offset == 0xFFFFFFFF
    ):
        locator = data.rfind(b"PK\x06\x07", 0, eocd)
        if locator < 0:
            raise AuditError("ZIP64 locator is absent")
        zip64_offset = struct.unpack_from("<Q", data, locator + 8)[0]
        relative = zip64_offset - block.start
        if relative < 0 or relative + 56 > len(data):
            raise AuditError("ZIP64 EOCD is outside bounded tail")
        zip64 = struct.unpack_from("<4sQ2H2I4Q", data, relative)
        entry_count = zip64[7]
        directory_size = zip64[8]
        directory_offset = zip64[9]

    position = directory_offset - block.start
    if position < 0 or position + directory_size > len(data):
        raise AuditError("central directory is outside bounded tail")

    entries: list[ZipEntry] = []
    for _ in range(entry_count):
        if data[position : position + 4] != b"PK\x01\x02":
            raise AuditError("invalid central-directory entry signature")
        header = struct.unpack_from("<4s6H3I5H2I", data, position)
        name_length, extra_length, comment_length = header[10:13]
        name_start = position + 46
        name_end = name_start + name_length
        extra_end = name_end + extra_length
        name = data[name_start:name_end].decode("utf-8")
        extra = data[name_end:extra_end]
        compressed = header[8]
        uncompressed = header[9]
        local_offset = header[16]
        zip64 = iter(_zip64_values(extra))
        if uncompressed == 0xFFFFFFFF:
            uncompressed = next(zip64)
        if compressed == 0xFFFFFFFF:
            compressed = next(zip64)
        if local_offset == 0xFFFFFFFF:
            local_offset = next(zip64)
        entries.append(
            ZipEntry(
                name=name,
                method=header[4],
                crc32=header[7],
                compressed_size=compressed,
                uncompressed_size=uncompressed,
                local_header_offset=local_offset,
            )
        )
        position = extra_end + comment_length

    if position != directory_offset - block.start + directory_size:
        raise AuditError("central-directory byte count does not reconcile")
    return entries


def parse_local_data_offset(block: RangeBlock, expected_name: str) -> int:
    if block.data[:4] != b"PK\x03\x04" or len(block.data) < 30:
        raise AuditError("invalid local ZIP header")
    header = struct.unpack_from("<4s5H3I2H", block.data)
    name_length, extra_length = header[9:11]
    end = 30 + name_length
    if end + extra_length > len(block.data):
        raise AuditError("local ZIP header window is too small")
    name = block.data[30:end].decode("utf-8")
    if name != expected_name:
        raise AuditError(f"local/central filename mismatch: {name} != {expected_name}")
    return block.start + end + extra_length


def _time_contract(times: list[str]) -> str:
    full = ["0.00"] + [f"{4.00 + index / 100:.2f}" for index in range(1, 101)]
    if times == full:
        return "initial_plus_complete_4p01_to_5p00_cycle"
    zero_prefix = [f"{index / 100:.2f}" for index in range(len(times))]
    if times == zero_prefix:
        return "zero_based_contiguous_partial_or_alternate_sequence"
    return "irregular_sequence"


def summarize_case(case_id: int, entries: Iterable[ZipEntry]) -> dict[str, object]:
    names = [entry.name for entry in entries]
    parsed: list[tuple[str, str]] = []
    for name in names:
        parts = name.split("/")
        if len(parts) != 3 or parts[0] != str(case_id):
            raise AuditError(f"unexpected inner member path for case {case_id}: {name}")
        try:
            float(parts[1])
        except ValueError as exc:
            raise AuditError(f"non-numeric time directory: {name}") from exc
        parsed.append((parts[1], parts[2]))

    times = sorted({time_name for time_name, _ in parsed}, key=float)
    counts = {time_name: 0 for time_name in times}
    canonical_wall = {time_name: False for time_name in times}
    surface_candidates = {time_name: [] for time_name in times}
    for time_name, filename in parsed:
        counts[time_name] += 1
        canonical_wall[time_name] |= filename == f"{time_name}_wall.vtp"
        if filename.endswith(".vtp") and filename not in {
            f"{time_name}_inlet.vtp",
            f"{time_name}_outlet.vtp",
        }:
            surface_candidates[time_name].append(filename)

    expected_cycle = {f"{4.00 + index / 100:.2f}" for index in range(1, 101)}
    existing = set(times)
    one_surface_each = all(len(surface_candidates[t]) == 1 for t in times)
    canonical_all = all(canonical_wall.values())
    return {
        "case_id": case_id,
        "member_count": len(names),
        "time_count": len(times),
        "first_time": times[0],
        "last_time": times[-1],
        "time_contract": _time_contract(times),
        "files_per_time_exactly_four": all(value == 4 for value in counts.values()),
        "one_wall_surface_candidate_per_time": one_surface_each,
        "canonical_wall_filename_every_time": canonical_all,
        "noncanonical_wall_examples": sorted(
            {
                candidates[0]
                for time_name, candidates in surface_candidates.items()
                if candidates and not canonical_wall[time_name]
            }
        )[:3],
        "official_cycle_directories_complete": expected_cycle <= existing,
        "official_preprocessor_wall_contract": expected_cycle <= existing and canonical_all,
        "directory_level_structural_target_contract": (
            expected_cycle <= existing and one_surface_each
        ),
    }


def _resolver_url(filename: str) -> str:
    quoted = urllib.parse.quote(filename, safe="")
    return (
        f"https://huggingface.co/datasets/{REPOSITORY}/resolve/"
        f"{REVISION}/{quoted}"
    )


def audit_batch(
    batch_start: int,
    client: RangeClient,
    tail_bytes: int,
) -> list[dict[str, object]]:
    batch_end = batch_start + 9
    filename = f"batch_{batch_start}-{batch_end}.zip"
    url = _resolver_url(filename)
    outer_tail = client.get(url, f"bytes=-{tail_bytes}")
    outer_entries = parse_central_directory(outer_tail)
    expected_names = {f"{case_id}.zip" for case_id in range(batch_start, batch_end + 1)}
    if {entry.name for entry in outer_entries} != expected_names:
        raise AuditError(f"unexpected outer member set: {filename}")

    records: list[dict[str, object]] = []
    for entry in sorted(outer_entries, key=lambda value: int(value.name[:-4])):
        case_id = int(entry.name[:-4])
        if entry.method != 0 or entry.compressed_size != entry.uncompressed_size:
            raise AuditError(f"inner archive is not stored verbatim: {filename}/{entry.name}")
        local = client.get(
            url,
            f"bytes={entry.local_header_offset}-{entry.local_header_offset + 127}",
        )
        data_start = parse_local_data_offset(local, entry.name)
        inner_size = entry.uncompressed_size
        inner_tail_size = min(tail_bytes, inner_size)
        inner_tail_start = data_start + inner_size - inner_tail_size
        inner_tail = client.get(
            url,
            f"bytes={inner_tail_start}-{data_start + inner_size - 1}",
        )
        relative_tail = RangeBlock(
            data=inner_tail.data,
            start=inner_tail.start - data_start,
            end=inner_tail.end - data_start,
            total=inner_size,
        )
        inner_entries = parse_central_directory(relative_tail)
        record = summarize_case(case_id, inner_entries)
        record.update(
            {
                "batch": filename,
                "inner_archive_bytes": inner_size,
                "inner_tail_sha256": hashlib.sha256(inner_tail.data).hexdigest(),
            }
        )
        records.append(record)
    return records


def load_family_map(path: Path) -> dict[int, str]:
    mapping: dict[int, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            case_id = int(row["case_id"])
            match = re.fullmatch(r"(.+)_deform_\d+", row["connection"])
            if match is None:
                raise AuditError(f"invalid Connection.csv lineage: {row}")
            mapping[case_id] = match.group(1)
    return mapping


def aggregate(records: list[dict[str, object]], family_map: dict[int, str]) -> dict:
    records = sorted(records, key=lambda row: int(row["case_id"]))
    expected_ids = list(range(1, 1001))
    if [row["case_id"] for row in records] != expected_ids:
        raise AuditError("audit does not contain exactly case IDs 1--1000")
    family_rows: dict[str, list[dict[str, object]]] = {}
    for row in records:
        family = family_map.get(int(row["case_id"]))
        if family is None:
            raise AuditError(f"missing lineage for case {row['case_id']}")
        row["base_family"] = family
        family_rows.setdefault(family, []).append(row)

    canonical = [row for row in records if row["official_preprocessor_wall_contract"]]
    structural = [
        row for row in records if row["directory_level_structural_target_contract"]
    ]
    incomplete = [row for row in records if not row["official_cycle_directories_complete"]]
    noncanonical = [
        row
        for row in records
        if row["directory_level_structural_target_contract"]
        and not row["canonical_wall_filename_every_time"]
    ]
    family_summary = []
    for family, rows in sorted(family_rows.items(), key=lambda item: int(item[0])):
        family_summary.append(
            {
                "base_family": family,
                "released_cases": len(rows),
                "directory_structural_cases": sum(
                    bool(row["directory_level_structural_target_contract"])
                    for row in rows
                ),
                "official_preprocessor_wall_cases": sum(
                    bool(row["official_preprocessor_wall_contract"]) for row in rows
                ),
            }
        )

    canonical_json = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": "aurora.aneumo_transient_archive_metadata_audit.v1",
        "status": "directory_metadata_only_no_inner_file_payload_or_scientific_result",
        "official_source": {
            "repository": REPOSITORY,
            "revision": REVISION,
            "released_case_range": [1, 1000],
        },
        "counts": {
            "cases": len(records),
            "base_families": len(family_rows),
            "directory_structural_target_cases": len(structural),
            "official_preprocessor_wall_contract_cases": len(canonical),
            "incomplete_cycle_cases": len(incomplete),
            "noncanonical_wall_naming_cases": len(noncanonical),
            "families_with_any_directory_structural_case": sum(
                any(bool(row["directory_level_structural_target_contract"]) for row in rows)
                for rows in family_rows.values()
            ),
            "families_with_any_official_preprocessor_wall_case": sum(
                any(bool(row["official_preprocessor_wall_contract"]) for row in rows)
                for rows in family_rows.values()
            ),
        },
        "incomplete_cycle_case_ids": [row["case_id"] for row in incomplete],
        "noncanonical_wall_case_ids": [row["case_id"] for row in noncanonical],
        "time_contract_counts": {
            contract: sum(row["time_contract"] == contract for row in records)
            for contract in sorted({str(row["time_contract"]) for row in records})
        },
        "family_summary": family_summary,
        "case_records_sha256": hashlib.sha256(canonical_json.encode()).hexdigest(),
        "case_records": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connection-csv", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--tail-bytes", type=int, default=DEFAULT_TAIL_BYTES)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument(
        "--allow-network",
        action="store_true",
        help="required acknowledgement; only bounded HTTP Range reads are made",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.allow_network:
        raise SystemExit("refusing network access without --allow-network")
    if args.workers < 1 or args.workers > 24:
        raise SystemExit("workers must be in [1, 24]")
    if args.tail_bytes < 32_768 or args.tail_bytes > 262_144:
        raise SystemExit("tail-bytes must be in [32768, 262144]")

    client = RangeClient(max_bytes=args.max_bytes)
    batch_starts = list(range(1, 1001, 10))
    records: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(audit_batch, start, client, args.tail_bytes): start
            for start in batch_starts
        }
        for future in concurrent.futures.as_completed(futures):
            start = futures[future]
            try:
                records.extend(future.result())
            except Exception as exc:
                for pending in futures:
                    pending.cancel()
                raise AuditError(f"batch {start}-{start + 9} failed: {exc}") from exc

    result = aggregate(records, load_family_map(args.connection_csv))
    result["transport"] = {
        "range_requests": client.requests,
        "bytes_read": client.bytes_read,
        "byte_ceiling": client.max_bytes,
        "tail_bytes": args.tail_bytes,
        "inner_file_payload_downloaded": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
