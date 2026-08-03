"""Selective, provenance-preserving ingestion of Aneumo ZIP members.

The public Aneumo release is multi-terabyte, while each steady-state archive
contains independent NPY members. This module reads ZIP central directories
and selected members with HTTP byte ranges, verifies member CRCs, and writes a
compact non-redistributable HDF5 pilot cache. It never downloads a full archive.
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import io
import json
import os
import struct
import urllib.request
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class AneumoRangeError(RuntimeError):
    """Raised when the pinned range-ingestion contract cannot be honored."""


@dataclass(frozen=True)
class ZipMember:
    name: str
    compression: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    local_offset: int


def _imports() -> tuple[Any, Any]:
    try:
        import h5py
        import numpy as np
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoRangeError("Aneumo staging requires numpy and h5py.") from exc
    return np, h5py


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("status") != "preregistered_asset_pilot_before_learning_results":
        raise AneumoRangeError("The Aneumo pilot must remain prospectively registered.")
    dataset = payload["dataset"]
    if dataset.get("redistribute_raw_or_compact_fields") is not False:
        raise AneumoRangeError("Aneumo raw and compact fields must not be redistributed.")
    selection = payload["asset_selection"]
    families = [int(item) for item in selection["base_families"]]
    mapping = {
        int(key): [int(case) for case in cases]
        for key, cases in selection["cases_by_base_family"].items()
    }
    if set(families) != set(mapping):
        raise AneumoRangeError("Every selected base family needs an explicit case mapping.")
    if any(len(mapping[family]) != 2 for family in families):
        raise AneumoRangeError("The pilot fixes exactly two deformations per base family.")
    if sum(map(len, mapping.values())) != int(selection["cases"]):
        raise AneumoRangeError("Declared case count does not match the family mapping.")
    split = payload["split"]
    split_sets = [
        set(int(item) for item in split[key])
        for key in (
            "train_base_families",
            "validation_base_families",
            "test_base_families",
        )
    ]
    if set.union(*split_sets) != set(families):
        raise AneumoRangeError("Base-family split does not cover the selected families.")
    if any(left & right for i, left in enumerate(split_sets) for right in split_sets[i + 1 :]):
        raise AneumoRangeError("AneuX base families must be disjoint across splits.")
    if split.get("unit") != "aneux_base_family":
        raise AneumoRangeError("The split unit must remain the AneuX base family.")
    if int(selection["conditions_per_case"]) != len(dataset["mass_flows_kg_s"]):
        raise AneumoRangeError("Condition count and mass-flow list disagree.")
    return payload


def archive_for_case(case_id: int) -> str:
    return f"{1 + 40 * ((int(case_id) - 1) // 40)}.zip"


def _request(
    url: str,
    *,
    method: str = "GET",
    start: int | None = None,
    end: int | None = None,
) -> tuple[bytes, Mapping[str, str]]:
    headers = {"User-Agent": "AURORA-Aneumo-range-audit/1.0"}
    if start is not None and end is not None:
        headers["Range"] = f"bytes={start}-{end}"
    request = urllib.request.Request(url, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        response_headers = {key.lower(): value for key, value in response.headers.items()}
        if start is not None and end is not None:
            status = int(getattr(response, "status", 0))
            content_range = response_headers.get("content-range", "")
            expected_prefix = f"bytes {start}-{end}/"
            if status != 206 or not content_range.startswith(expected_prefix):
                raise AneumoRangeError(
                    "Server did not honor the exact byte range; refusing a possible "
                    "full-archive download."
                )
        payload = response.read() if method != "HEAD" else b""
    if start is not None and end is not None:
        expected = end - start + 1
        if len(payload) != expected:
            raise AneumoRangeError(
                f"Range response length {len(payload)} != requested {expected}."
            )
    return payload, response_headers


def _zip64_values(
    extra: bytes,
    *,
    uncompressed_size: int,
    compressed_size: int,
    local_offset: int,
    disk_start: int,
) -> tuple[int, int, int]:
    position = 0
    zip64 = b""
    while position + 4 <= len(extra):
        identifier, length = struct.unpack_from("<HH", extra, position)
        value = extra[position + 4 : position + 4 + length]
        if identifier == 0x0001:
            zip64 = value
            break
        position += 4 + length
    cursor = 0

    def take(width: int) -> int:
        nonlocal cursor
        if cursor + width > len(zip64):
            raise AneumoRangeError("ZIP64 extra field is truncated.")
        fmt = "<Q" if width == 8 else "<L"
        value = int(struct.unpack_from(fmt, zip64, cursor)[0])
        cursor += width
        return value

    if uncompressed_size == 0xFFFFFFFF:
        uncompressed_size = take(8)
    if compressed_size == 0xFFFFFFFF:
        compressed_size = take(8)
    if local_offset == 0xFFFFFFFF:
        local_offset = take(8)
    if disk_start == 0xFFFF:
        take(4)
    return uncompressed_size, compressed_size, local_offset


def parse_central_directory(payload: bytes) -> dict[str, ZipMember]:
    members: dict[str, ZipMember] = {}
    position = 0
    while position + 46 <= len(payload):
        if payload[position : position + 4] != b"PK\x01\x02":
            raise AneumoRangeError(f"Invalid central-directory signature at {position}.")
        values = struct.unpack_from("<4s6H3L5H2L", payload, position)
        flags = int(values[3])
        compression = int(values[4])
        crc32 = int(values[7])
        compressed_size = int(values[8])
        uncompressed_size = int(values[9])
        name_length, extra_length, comment_length = map(int, values[10:13])
        disk_start = int(values[13])
        local_offset = int(values[16])
        name_start = position + 46
        name_end = name_start + name_length
        extra_end = name_end + extra_length
        name = payload[name_start:name_end].decode("utf-8")
        extra = payload[name_end:extra_end]
        uncompressed_size, compressed_size, local_offset = _zip64_values(
            extra,
            uncompressed_size=uncompressed_size,
            compressed_size=compressed_size,
            local_offset=local_offset,
            disk_start=disk_start,
        )
        if flags & 0x1:
            raise AneumoRangeError(f"Encrypted ZIP member is unsupported: {name}")
        members[name] = ZipMember(
            name=name,
            compression=compression,
            crc32=crc32,
            compressed_size=compressed_size,
            uncompressed_size=uncompressed_size,
            local_offset=local_offset,
        )
        position = extra_end + comment_length
    if position != len(payload):
        raise AneumoRangeError("Central directory has trailing or truncated bytes.")
    return members


def load_archive_index(url: str) -> tuple[dict[str, ZipMember], dict[str, Any]]:
    _, headers = _request(url, method="HEAD")
    try:
        size = int(headers["content-length"])
    except (KeyError, ValueError) as exc:
        raise AneumoRangeError("Archive HEAD response lacks content-length.") from exc
    tail_start = max(0, size - 1_048_576)
    tail, _ = _request(url, start=tail_start, end=size - 1)
    locator = tail.rfind(b"PK\x06\x07")
    if locator < 0 or locator + 20 > len(tail):
        raise AneumoRangeError("ZIP64 locator was not found in the archive tail.")
    _, _, zip64_offset, disks = struct.unpack_from("<4sLQL", tail, locator)
    if disks != 1:
        raise AneumoRangeError("Multi-disk ZIP archives are unsupported.")
    relative = int(zip64_offset) - tail_start
    if relative < 0 or relative + 56 > len(tail):
        zip64, _ = _request(url, start=int(zip64_offset), end=int(zip64_offset) + 55)
    else:
        zip64 = tail[relative : relative + 56]
    values = struct.unpack_from("<4sQ2H2L4Q", zip64, 0)
    if values[0] != b"PK\x06\x06":
        raise AneumoRangeError("ZIP64 end-of-central-directory record is invalid.")
    entries = int(values[7])
    central_size = int(values[8])
    central_offset = int(values[9])
    central, _ = _request(
        url, start=central_offset, end=central_offset + central_size - 1
    )
    members = parse_central_directory(central)
    if len(members) != entries:
        raise AneumoRangeError(
            f"Central directory declares {entries} entries but parsed {len(members)}."
        )
    return members, {
        "content_length": size,
        "etag": headers.get("etag"),
        "entries": entries,
        "central_directory_size": central_size,
    }


def decode_member_payload(payload: bytes, expected: ZipMember) -> bytes:
    if len(payload) < 30:
        raise AneumoRangeError(f"Local member header is truncated: {expected.name}")
    values = struct.unpack_from("<4s5H3L2H", payload, 0)
    if values[0] != b"PK\x03\x04":
        raise AneumoRangeError(f"Invalid local member signature: {expected.name}")
    compression = int(values[3])
    name_length = int(values[9])
    extra_length = int(values[10])
    name = payload[30 : 30 + name_length].decode("utf-8")
    if name != expected.name or compression != expected.compression:
        raise AneumoRangeError(f"Local and central records disagree: {expected.name}")
    start = 30 + name_length + extra_length
    compressed = payload[start : start + expected.compressed_size]
    if len(compressed) != expected.compressed_size:
        raise AneumoRangeError(f"Compressed member is truncated: {expected.name}")
    if compression == 0:
        raw = compressed
    elif compression == 8:
        raw = zlib.decompress(compressed, -15)
    else:
        raise AneumoRangeError(
            f"Unsupported ZIP compression method {compression}: {expected.name}"
        )
    if len(raw) != expected.uncompressed_size:
        raise AneumoRangeError(f"Uncompressed size mismatch: {expected.name}")
    if binascii.crc32(raw) & 0xFFFFFFFF != expected.crc32:
        raise AneumoRangeError(f"CRC32 mismatch: {expected.name}")
    return raw


def fetch_member(url: str, member: ZipMember) -> bytes:
    prefix, _ = _request(
        url, start=member.local_offset, end=member.local_offset + 4095
    )
    if len(prefix) < 30:
        raise AneumoRangeError(f"Cannot read local header: {member.name}")
    local = struct.unpack_from("<4s5H3L2H", prefix, 0)
    name_length, extra_length = int(local[9]), int(local[10])
    data_start = member.local_offset + 30 + name_length + extra_length
    data_end = data_start + member.compressed_size - 1
    compressed, _ = _request(url, start=data_start, end=data_end)
    payload = prefix[: 30 + name_length + extra_length] + compressed
    return decode_member_payload(payload, member)


def select_node_indices(nodes: int, count: int, seed: int) -> Any:
    np, _ = _imports()
    if nodes < count:
        raise AneumoRangeError(f"Requested {count} nodes from an array with {nodes}.")
    generator = np.random.default_rng(int(seed))
    return np.sort(generator.choice(nodes, size=count, replace=False))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _split_for_family(config: Mapping[str, Any], family: int) -> str:
    split = config["split"]
    for name in ("train", "validation", "test"):
        if family in {int(item) for item in split[f"{name}_base_families"]}:
            return name
    raise AneumoRangeError(f"Base family {family} has no split assignment.")


def stage(config: Mapping[str, Any], output: Path) -> dict[str, Any]:
    np, h5py = _imports()
    dataset = config["dataset"]
    selection = config["asset_selection"]
    repo = dataset["hf_repo"]
    revision = dataset["hf_repo_commit"]
    root = f"https://huggingface.co/datasets/{repo}/resolve/{revision}"
    mass_flows = [float(item) for item in dataset["mass_flows_kg_s"]]
    mapping = {
        int(key): [int(case) for case in cases]
        for key, cases in selection["cases_by_base_family"].items()
    }
    cases = [
        (family, case, archive_for_case(case))
        for family in [int(item) for item in selection["base_families"]]
        for case in mapping[family]
    ]
    archive_names = sorted({archive for _, _, archive in cases}, key=lambda x: int(x[:-4]))
    archive_indexes: dict[str, dict[str, ZipMember]] = {}
    archive_manifest: dict[str, Any] = {}
    for index, archive in enumerate(archive_names, start=1):
        print(f"[Aneumo index] {index}/{len(archive_names)} {archive}", flush=True)
        members, metadata = load_archive_index(f"{root}/{archive}")
        archive_indexes[archive] = members
        archive_manifest[archive] = metadata

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.partial-{os.getpid()}")
    if temporary.exists():
        temporary.unlink()
    member_manifest: list[dict[str, Any]] = []
    try:
        with h5py.File(temporary, "w") as h5:
            h5.attrs["dataset"] = "Aneumo"
            h5.attrs["hf_repo"] = repo
            h5.attrs["hf_repo_commit"] = revision
            h5.attrs["upstream_code_commit"] = dataset["upstream_code_commit"]
            h5.attrs["license"] = dataset["license"]
            h5.attrs["redistributable"] = False
            h5.attrs["columns"] = json.dumps(dataset["array_columns"])
            h5.create_dataset("mass_flows_kg_s", data=np.asarray(mass_flows, dtype=np.float32))
            geometries = h5.create_group("geometries")
            for case_index, (family, case, archive) in enumerate(cases, start=1):
                print(
                    f"[Aneumo stage] case {case_index}/{len(cases)} "
                    f"id={case} family={family}",
                    flush=True,
                )
                url = f"{root}/{archive}"
                index = archive_indexes[archive]
                coordinates = None
                reference_coordinates = None
                selected = None
                fields = np.empty(
                    (len(mass_flows), int(selection["nodes_per_case"]), 4),
                    dtype=np.float32,
                )
                source_nodes = 0
                for condition_index, mass_flow in enumerate(mass_flows):
                    flow = f"{mass_flow:g}"
                    name = f"{case}/npy/m={flow}/array_internal_{case}.npy"
                    if name not in index:
                        raise AneumoRangeError(f"Required member is missing: {name}")
                    member = index[name]
                    raw = fetch_member(url, member)
                    array = np.load(io.BytesIO(raw), allow_pickle=False)
                    if array.ndim != 2 or array.shape[1] != 7:
                        raise AneumoRangeError(f"Unexpected array shape {array.shape}: {name}")
                    if coordinates is None:
                        source_nodes = int(array.shape[0])
                        selected = select_node_indices(
                            source_nodes,
                            int(selection["nodes_per_case"]),
                            int(selection["seed"]) + case,
                        )
                        reference_coordinates = np.asarray(array[:, :3]).copy()
                        coordinates = np.asarray(
                            reference_coordinates[selected], dtype=np.float32
                        )
                    elif not np.array_equal(
                        np.asarray(array[:, :3]), reference_coordinates
                    ):
                        raise AneumoRangeError(
                            f"Conditions do not share coordinates for case {case}."
                        )
                    fields[condition_index] = np.asarray(
                        array[selected, 3:7], dtype=np.float32
                    )
                    member_manifest.append(
                        {
                            "archive": archive,
                            "case_id": case,
                            "base_family": family,
                            "mass_flow_kg_s": mass_flow,
                            "member": name,
                            "crc32": f"{member.crc32:08x}",
                            "compressed_size": member.compressed_size,
                            "uncompressed_size": member.uncompressed_size,
                        }
                    )
                group = geometries.create_group(str(case))
                group.attrs["base_family"] = family
                group.attrs["split"] = _split_for_family(config, family)
                group.attrs["source_nodes"] = source_nodes
                group.create_dataset(
                    "selected_node_indices", data=selected, compression="gzip"
                )
                group.create_dataset("coordinates_m", data=coordinates, compression="gzip")
                group.create_dataset(
                    "pressure_velocity", data=fields, compression="gzip"
                )
            h5.create_dataset(
                "member_manifest_json",
                data=json.dumps(member_manifest, sort_keys=True).encode("utf-8"),
            )
            h5.attrs["archive_manifest_json"] = json.dumps(
                archive_manifest, sort_keys=True
            )
            h5.attrs["config_sha256"] = config["_config_sha256"]
        temporary.replace(output)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise
    return {
        "output": str(output),
        "cases": len(cases),
        "base_families": len(mapping),
        "conditions": len(mass_flows),
        "nodes_per_case": int(selection["nodes_per_case"]),
        "archives_range_read": len(archive_names),
        "members_crc_verified": len(member_manifest),
        "output_sha256": _sha256_file(output),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    summary = stage(config, args.output)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
