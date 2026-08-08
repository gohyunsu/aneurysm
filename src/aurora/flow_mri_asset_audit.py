"""Metadata-only audit for paired-protocol intracranial 4D-flow MRI assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_range import _request, fetch_member, parse_central_directory


class FlowMRIAssetAuditError(RuntimeError):
    """Raised when the frozen I0a asset contract is violated."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FlowMRIAssetAuditError(message)


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    _require(
        payload.get("schema_version")
        == "aurora.flow_mri_protocol_i0a_asset_audit.v1",
        "Unexpected I0a schema version.",
    )
    _require(
        payload.get("status")
        == "registered_after_central_directory_and_header_discovery_before_selective_staging",
        "I0a discovery boundary changed.",
    )
    discovery = payload.get("discovery_boundary", {})
    _require(
        discovery
        == {
            "inspected_before_registration": True,
            "scope": "official_record_metadata_two_zip_central_directories_nine_processed_velocity_descriptors_and_eight_primary_PAR_or_XML_headers",
            "not_prospective_evidence": True,
            "field_values_inspected": False,
            "raw_REC_payloads_inspected": False,
        },
        "I0a must disclose the full pre-registration discovery.",
    )
    access = payload.get("access", {})
    _require(
        access.get("processed_velocity_RAW_payloads") is False
        and access.get("REC_payloads") is False
        and access.get("field_values") is False
        and access.get("model_or_checkpoint") is False
        and access.get("training") is False,
        "I0a cannot read field payloads or train a model.",
    )
    sources = payload.get("sources", {})
    _require(
        set(sources) == {"multiresolution_2021", "dual_venc_2025"},
        "I0a source set changed.",
    )
    multi = sources["multiresolution_2021"]
    dual = sources["dual_venc_2025"]
    _require(
        multi.get("doi") == "10.5281/zenodo.4882572"
        and multi.get("archive_bytes") == 2216223733
        and multi.get("upstream_checksum")
        == "md5:f3159a34a6f222b491432650540f63b6"
        and multi.get("license") == "cc-by-4.0"
        and multi.get("archive_entries") == 174,
        "I0a multiresolution source pin changed.",
    )
    expected_protocols = {
        f"{resolution}_cs{acceleration}"
        for resolution in ("0.5", "1.0", "1.5")
        for acceleration in ("2.5", "4.5", "6.5")
    }
    _require(
        set(multi.get("protocols", {})) == expected_protocols,
        "I0a must retain the exact 3x3 protocol grid.",
    )
    _require(
        dual.get("doi") == "10.5281/zenodo.14981710"
        and dual.get("archive_bytes") == 6218491225
        and dual.get("upstream_checksum")
        == "md5:6e2437d0107677ad38708e01772db85d"
        and dual.get("license") == "cc-by-4.0"
        and dual.get("archive_entries") == 76
        and len(dual.get("models", {})) == 4
        and sum(len(item["protocols"]) for item in dual["models"].values()) == 8,
        "I0a dual-VENC source pin changed.",
    )
    gate = payload.get("gate", {})
    _require(
        gate.get("local_repair_allowed") is False
        and gate.get("pass_authorizes")
        == "register_selective_private_staging_and_method_free_I0b_task_adequacy_only"
        and "method_selection" in gate.get("pass_does_not_authorize", [])
        and "isbi_submission" in gate.get("pass_does_not_authorize", [])
        and len(gate.get("checks", [])) == 14,
        "I0a cannot authorize a method or submission.",
    )
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def _official_record(source: Mapping[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        str(source["record_api"]),
        headers={"User-Agent": "AURORA-flow-MRI-asset-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    metadata = payload.get("metadata", {})
    files = {item["key"]: item for item in payload.get("files", [])}
    _require(source["archive_name"] in files, "Pinned Zenodo file is missing.")
    item = files[source["archive_name"]]
    license_payload = metadata.get("license", {})
    return {
        "record_id": int(payload["id"]),
        "access_right": metadata.get("access_right"),
        "license": license_payload.get("id"),
        "archive_name": item["key"],
        "archive_bytes": int(item["size"]),
        "checksum": item["checksum"],
    }


def load_generic_zip_index(url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read a standard or ZIP64 central directory without downloading the archive."""

    _, headers = _request(url, method="HEAD")
    try:
        size = int(headers["content-length"])
    except (KeyError, ValueError) as exc:
        raise FlowMRIAssetAuditError("Archive HEAD lacks content-length.") from exc
    tail_start = max(0, size - 1_048_576)
    tail, _ = _request(url, start=tail_start, end=size - 1)
    eocd_position = tail.rfind(b"PK\x05\x06")
    _require(eocd_position >= 0, "ZIP end-of-central-directory was not found.")
    eocd = struct.unpack_from("<4s4H2LH", tail, eocd_position)
    disk, central_disk, disk_entries, entries = map(int, eocd[1:5])
    central_size, central_offset = int(eocd[5]), int(eocd[6])
    archive_format = "zip32"
    if entries == 0xFFFF or central_size == 0xFFFFFFFF or central_offset == 0xFFFFFFFF:
        locator_position = tail.rfind(b"PK\x06\x07", 0, eocd_position)
        _require(locator_position >= 0, "ZIP64 locator was not found.")
        _, locator_disk, zip64_offset, total_disks = struct.unpack_from(
            "<4sLQL", tail, locator_position
        )
        _require(
            int(locator_disk) == 0 and int(total_disks) in {0, 1},
            "Multi-disk ZIP64 archives are unsupported.",
        )
        relative = int(zip64_offset) - tail_start
        if 0 <= relative and relative + 56 <= len(tail):
            zip64 = tail[relative : relative + 56]
        else:
            zip64, _ = _request(
                url, start=int(zip64_offset), end=int(zip64_offset) + 55
            )
        values = struct.unpack_from("<4sQ2H2L4Q", zip64, 0)
        _require(values[0] == b"PK\x06\x06", "Invalid ZIP64 EOCD record.")
        disk, central_disk = int(values[4]), int(values[5])
        disk_entries, entries = int(values[6]), int(values[7])
        central_size, central_offset = int(values[8]), int(values[9])
        archive_format = "zip64"
    _require(disk == 0 and central_disk == 0, "Multi-disk ZIP is unsupported.")
    _require(disk_entries == entries, "Split central directories are unsupported.")
    central, _ = _request(
        url, start=central_offset, end=central_offset + central_size - 1
    )
    members = parse_central_directory(central)
    _require(len(members) == entries, "Central-directory entry count mismatch.")
    return members, {
        "content_length": size,
        "entries": entries,
        "archive_format": archive_format,
        "central_directory_size": central_size,
    }


def parse_velocity_descriptor(payload: bytes) -> dict[str, Any]:
    text = payload.decode("utf-8", errors="strict")
    dims = re.search(r"<DimensionSizes TZYX>([^<]+)</DimensionSizes TZYX>", text)
    spacing = [
        re.search(rf"<VoxelSize{axis} \[mm\]>([^<]+)</VoxelSize{axis} \[mm\]>", text)
        for axis in "XYZ"
    ]
    time_step = re.search(r"<TimeStep \[ms\]>([^<]+)</TimeStep \[ms\]>", text)
    _require(dims is not None and all(spacing) and time_step is not None, "Malformed GTFlow descriptor.")
    return {
        "dims_tzyx": [int(item) for item in dims.group(1).split()],
        "spacing_xyz_mm": [float(item.group(1)) for item in spacing if item],
        "time_step_descriptor_value": float(time_step.group(1)),
    }


def parse_primary_header(payload: bytes) -> dict[str, Any]:
    text = payload.decode("utf-8", errors="replace")
    venc = re.search(
        r"Phase encoding velocity \[cm/sec\]\s*:\s*([0-9.E+\-]+)", text, re.I
    ) or re.search(
        r'Name="Phase Encoding Velocity"[^>]*>([0-9.E+\-]+)', text, re.I
    )
    phases = re.search(r"Max\. number of cardiac phases\s*:\s*(\d+)", text, re.I) or re.search(
        r'Name="Max No Phases"[^>]*>(\d+)', text, re.I
    )
    scan = re.search(r"Scan resolution\s*\(x, y\)\s*:\s*(\d+)\s+(\d+)", text, re.I)
    scan_x = re.search(r'Name="Scan Resolution X"[^>]*>(\d+)', text, re.I)
    scan_y = re.search(r'Name="Scan Resolution Y"[^>]*>(\d+)', text, re.I)
    _require(venc is not None and phases is not None, "Primary 4D-flow header lacks VENC or phases.")
    if scan is not None:
        resolution = [int(scan.group(1)), int(scan.group(2))]
    else:
        _require(scan_x is not None and scan_y is not None, "Primary header lacks scan resolution.")
        resolution = [int(scan_x.group(1)), int(scan_y.group(1))]
    return {
        "venc_cm_s": float(venc.group(1)),
        "cardiac_phases": int(phases.group(1)),
        "scan_resolution_xy": resolution,
    }


def _audit_multiresolution(
    source: Mapping[str, Any], members: Mapping[str, Any]
) -> dict[str, Any]:
    root_token = str(source["processed_velocity_root_token"])
    relevant = {
        name: member
        for name, member in members.items()
        if root_token in name and (name.endswith("_Descr.txt") or name.endswith(".raw"))
    }
    rows: list[dict[str, Any]] = []
    for protocol, expected in sorted(source["protocols"].items()):
        prefix = f"/{protocol}/"
        names = [name for name in relevant if prefix in name]
        descriptors = [name for name in names if name.endswith("_Descr.txt")]
        _require(len(descriptors) == 1, f"Expected one descriptor for {protocol}.")
        descriptor = parse_velocity_descriptor(
            fetch_member(str(source["archive_url"]), relevant[descriptors[0]])
        )
        _require(descriptor["dims_tzyx"] == expected["dims_tzyx"], "Descriptor dimensions changed.")
        _require(
            all(
                math.isclose(left, right, rel_tol=0.0, abs_tol=1e-9)
                for left, right in zip(
                    descriptor["spacing_xyz_mm"], expected["spacing_xyz_mm"]
                )
            ),
            "Descriptor spacing changed.",
        )
        _require(
            math.isclose(
                descriptor["time_step_descriptor_value"],
                float(source["flow_state"]["time_step_descriptor_value"]),
                rel_tol=0.0,
                abs_tol=1e-12,
            ),
            "Descriptor time-step value changed.",
        )
        raw_names = [name for name in names if name.endswith(".raw")]
        _require(len(raw_names) == 3, f"Expected X/Y/Z RAW components for {protocol}.")
        suffixes = {name.rsplit("_", 1)[-1].removesuffix(".raw") for name in raw_names}
        _require(suffixes == set(source["velocity_components"]), "Velocity component set changed.")
        expected_bytes = math.prod(descriptor["dims_tzyx"]) * 4
        _require(
            all(int(relevant[name].uncompressed_size) == expected_bytes for name in raw_names),
            "RAW float32 byte contract changed.",
        )
        rows.append(
            {
                "protocol": protocol,
                **descriptor,
                "components": 3,
                "uncompressed_bytes_per_component": expected_bytes,
                "compressed_bytes_all_components": sum(
                    int(relevant[name].compressed_size) for name in raw_names
                ),
            }
        )
    return {"protocols": rows, "descriptors_read": len(rows), "raw_payloads_read": 0}


def _audit_dual_venc(source: Mapping[str, Any], members: Mapping[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    filename_disagreements: list[str] = []
    for model, model_spec in source["models"].items():
        for protocol, expected_venc in model_spec["protocols"].items():
            prefix = f"4D_flow_MRI/{model}/{protocol}/"
            names = [name for name in members if name.startswith(prefix) and not name.endswith("/")]
            rec = [name for name in names if name.lower().endswith(".rec")]
            metadata = [
                name
                for name in names
                if name.rsplit(".", 1)[-1] in source["metadata_extensions"]
            ]
            _require(len(rec) == len(metadata) == 4, "Dual-VENC protocol lacks four metadata/REC pairs.")
            rec_stems = {name.rsplit(".", 1)[0] for name in rec}
            metadata_stems = {name.rsplit(".", 1)[0] for name in metadata}
            _require(rec_stems == metadata_stems, "Dual-VENC metadata/REC stems disagree.")
            lower_stems = [Path(name).stem.lower() for name in metadata]
            encoding_tokens = [str(item).lower() for item in source["required_direction_tokens"]]
            covered_tokens = sorted(
                token for token in encoding_tokens if any(token in stem for stem in lower_stems)
            )
            _require(
                covered_tokens == sorted(encoding_tokens),
                "Dual-VENC protocol lacks a registered encoding token.",
            )
            primary = [name for name in metadata if re.search(r"_1\.(?:PAR|xml)$", name, re.I)]
            _require(len(primary) == 1, "Dual-VENC protocol lacks one primary header.")
            header = parse_primary_header(
                fetch_member(str(source["archive_url"]), members[primary[0]])
            )
            _require(
                math.isclose(header["venc_cm_s"], float(expected_venc), abs_tol=1e-8),
                "Header VENC changed.",
            )
            _require(
                header["cardiac_phases"] == source["flow_state"]["cardiac_phases"]
                and header["scan_resolution_xy"]
                == source["flow_state"]["scan_resolution_xy"],
                "Dual-VENC header phase or resolution contract changed.",
            )
            token = re.search(r"(\d+)venc", Path(primary[0]).name, re.I)
            if token is not None and float(token.group(1)) != header["venc_cm_s"]:
                filename_disagreements.append(f"{model}/{protocol}")
            rows.append(
                {
                    "model": model,
                    "protocol": protocol,
                    **header,
                    "encodings": 4,
                    "encoding_tokens": covered_tokens,
                    "metadata_payload_pairs": 4,
                }
            )
    return {
        "protocols": rows,
        "primary_headers_read": len(rows),
        "rec_payloads_read": 0,
        "filename_header_disagreements": sorted(filename_disagreements),
    }


def run_audit(config: Mapping[str, Any], *, output: Path, git_commit: str) -> dict[str, Any]:
    _require(
        re.fullmatch(r"[0-9a-f]{40}", git_commit) is not None,
        "I0a requires an exact 40-character lowercase Git commit.",
    )
    sources = config["sources"]
    official = {name: _official_record(source) for name, source in sources.items()}
    indexes: dict[str, Mapping[str, Any]] = {}
    archive_meta: dict[str, Mapping[str, Any]] = {}
    for name, source in sources.items():
        index, metadata = load_generic_zip_index(str(source["archive_url"]))
        indexes[name], archive_meta[name] = index, metadata
    multi = _audit_multiresolution(sources["multiresolution_2021"], indexes["multiresolution_2021"])
    dual = _audit_dual_venc(sources["dual_venc_2025"], indexes["dual_venc_2025"])
    official_ok = all(
        official[name]["access_right"] == source["access_right"]
        and official[name]["license"] == source["license"]
        and official[name]["archive_bytes"] == source["archive_bytes"]
        and official[name]["checksum"] == source["upstream_checksum"]
        for name, source in sources.items()
    )
    sizes_ok = all(
        archive_meta[name]["content_length"] == source["archive_bytes"]
        for name, source in sources.items()
    )
    entry_ok = all(
        archive_meta[name]["entries"] == source["archive_entries"]
        for name, source in sources.items()
    )
    expected_disagreement = ["M4_printed_16/4DFlow_50venc_inlet"]
    checks = {
        "official_records_are_open_cc_by_4_and_pin_archive_size_checksum": official_ok,
        "both_archives_are_exact_size_and_range_readable": sizes_ok,
        "central_directory_entry_counts_match": entry_ok,
        "multiresolution_protocol_grid_is_exactly_three_by_three": len(multi["protocols"]) == 9,
        "all_nine_descriptors_are_crc_verified_and_match_dimensions_spacing_and_time_step": multi["descriptors_read"] == 9,
        "all_twenty_seven_velocity_components_have_exact_float32_byte_contract": sum(row["components"] for row in multi["protocols"]) == 27,
        "dual_venc_has_exactly_four_models_and_eight_protocols": len({row["model"] for row in dual["protocols"]}) == 4 and len(dual["protocols"]) == 8,
        "each_dual_venc_protocol_has_four_metadata_REC_pairs": all(row["metadata_payload_pairs"] == 4 for row in dual["protocols"]),
        "each_dual_venc_protocol_covers_primary_AP_FH_and_RL_encodings": all(
            row["encoding_tokens"]
            == sorted(
                token.lower()
                for token in sources["dual_venc_2025"]["required_direction_tokens"]
            )
            for row in dual["protocols"]
        ),
        "all_eight_primary_headers_are_crc_verified": dual["primary_headers_read"] == 8,
        "dual_venc_headers_match_twenty_phases_and_scan_resolution": all(row["cardiac_phases"] == 20 and row["scan_resolution_xy"] == [148, 147] for row in dual["protocols"]),
        "dual_venc_header_values_match_registered_protocol_values": all(math.isclose(row["venc_cm_s"], float(sources["dual_venc_2025"]["models"][row["model"]]["protocols"][row["protocol"]]), abs_tol=1e-8) for row in dual["protocols"]),
        "known_M4_filename_header_disagreement_is_disclosed": dual["filename_header_disagreements"] == expected_disagreement,
        "no_velocity_RAW_or_REC_payload_was_read": multi["raw_payloads_read"] == 0 and dual["rec_payloads_read"] == 0,
    }
    _require(list(checks) == config["gate"]["checks"], "I0a check ordering changed.")
    result = {
        "schema_version": "aurora.flow_mri_protocol_i0a_asset_audit.result.v1",
        "experiment_id": config["experiment_id"],
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "discovery_boundary": config["discovery_boundary"],
        "official_records": official,
        "archives": archive_meta,
        "multiresolution_2021": multi,
        "dual_venc_2025": dual,
        "field_access": {
            "processed_velocity_RAW_payloads_read": 0,
            "REC_payloads_read": 0,
            "field_values_inspected": False,
        },
        "gate": {
            "checks": checks,
            "passed_checks": sum(bool(value) for value in checks.values()),
            "total_checks": len(checks),
            "all_checks_passed": all(checks.values()),
            "pass_authorizes": config["gate"]["pass_authorizes"],
            "pass_does_not_authorize": config["gate"]["pass_does_not_authorize"],
            "decision": (
                config["gate"]["pass_authorizes"]
                if all(checks.values())
                else config["gate"]["failure_action"]
            ),
        },
        "interpretation": config["interpretation"],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "status.json").write_text(
        json.dumps(
            {
                "exit_status": 0,
                "state": "complete",
                "field_values_inspected": False,
                "raw_or_REC_payloads_read": 0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    try:
        result = run_audit(config, output=args.output, git_commit=args.git_commit)
    except Exception as exc:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "status.json").write_text(
            json.dumps(
                {"exit_status": 1, "state": "failed", "error": str(exc)},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        raise
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
