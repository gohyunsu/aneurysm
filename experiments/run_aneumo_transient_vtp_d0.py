#!/usr/bin/env python3
"""Run the bounded Aneumo transient VTP D0 development contract."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import math
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from aurora.aneumo_transient_vtp import (
    bidirectional_signed_recall,
    extract_critical_points,
    normal_component_fraction,
    parse_polydata,
    project_tangent,
    triangulate,
    vertex_normals,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.audit_aneumo_transient_archives import (  # noqa: E402
    AuditError,
    RangeBlock,
    RangeClient,
    parse_central_directory,
    parse_local_data_offset,
)


class D0Error(RuntimeError):
    pass


def _url(repository: str, revision: str, filename: str) -> str:
    return f"https://huggingface.co/datasets/{repository}/resolve/{revision}/{filename}"


def _get_member(
    client: RangeClient,
    *,
    url: str,
    case_id: int,
    member_name: str,
) -> bytes:
    outer_tail = client.get(url, "bytes=-65536")
    outer = {entry.name: entry for entry in parse_central_directory(outer_tail)}
    inner_name = f"{case_id}.zip"
    if inner_name not in outer:
        raise D0Error(f"inner archive absent: {inner_name}")
    inner = outer[inner_name]
    if inner.method != 0 or inner.compressed_size != inner.uncompressed_size:
        raise D0Error("inner archive is not stored verbatim")
    outer_local = client.get(
        url, f"bytes={inner.local_header_offset}-{inner.local_header_offset + 511}"
    )
    inner_start = parse_local_data_offset(outer_local, inner_name)
    tail_size = min(65536, inner.uncompressed_size)
    remote_tail_start = inner_start + inner.uncompressed_size - tail_size
    inner_tail = client.get(
        url, f"bytes={remote_tail_start}-{inner_start + inner.uncompressed_size - 1}"
    )
    relative_tail = RangeBlock(
        data=inner_tail.data,
        start=inner_tail.start - inner_start,
        end=inner_tail.end - inner_start,
        total=inner.uncompressed_size,
    )
    entries = {entry.name: entry for entry in parse_central_directory(relative_tail)}
    if member_name not in entries:
        raise D0Error(f"wall member absent: {member_name}")
    member = entries[member_name]
    local_offset = inner_start + member.local_header_offset
    local = client.get(url, f"bytes={local_offset}-{local_offset + 1023}")
    data_start = parse_local_data_offset(local, member_name)
    compressed = client.get(
        url, f"bytes={data_start}-{data_start + member.compressed_size - 1}"
    ).data
    if member.method == 0:
        payload = compressed
    elif member.method == 8:
        try:
            payload = zlib.decompress(compressed, -zlib.MAX_WBITS)
        except zlib.error as exc:
            raise D0Error("invalid deflated wall member") from exc
    else:
        raise D0Error(f"unsupported ZIP method: {member.method}")
    if len(payload) != member.uncompressed_size:
        raise D0Error("wall member length mismatch")
    if (binascii.crc32(payload) & 0xFFFFFFFF) != member.crc32:
        raise D0Error("wall member CRC mismatch")
    return payload


def _phase_metrics(phase: str, payload: bytes) -> tuple[dict, dict]:
    data = parse_polydata(payload)
    bbox_diagonal = float(np.linalg.norm(data.points.max(0) - data.points.min(0)))
    if not math.isfinite(bbox_diagonal) or bbox_diagonal <= 0:
        raise D0Error("invalid surface bounding box")
    metrics: dict[str, object] = {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "points": int(data.points.shape[0]),
        "polygons": len(data.polygons),
        "polygon_vertex_minimum": min(len(polygon) for polygon in data.polygons),
        "polygon_vertex_maximum": max(len(polygon) for polygon in data.polygons),
        "point_wss_components": int(data.point_wss.shape[1]),
        "cell_wss_components": None if data.cell_wss is None else int(data.cell_wss.shape[1]),
        "wss_rms": float(np.sqrt(np.mean(np.square(data.point_wss)))),
        "normal_modes": {},
        "critical_extractions": {},
    }
    critical: dict[tuple[str, str], list] = {}
    for normal_mode in ("polygon_newell", "triangle_area"):
        normals = vertex_normals(data.points, data.polygons, normal_mode)
        fractions = normal_component_fraction(data.point_wss, normals)
        tangent = project_tangent(data.point_wss, normals)
        metrics["normal_modes"][normal_mode] = {
            "normal_fraction_median": float(np.median(fractions)),
            "normal_fraction_p95": float(np.quantile(fractions, 0.95)),
            "normal_fraction_p99": float(np.quantile(fractions, 0.99)),
        }
        for fan in ("first", "last"):
            points = extract_critical_points(
                data.points,
                triangulate(data.polygons, fan),
                tangent,
                phase=phase,
            )
            critical[(normal_mode, fan)] = points
            metrics["critical_extractions"][f"{normal_mode}__{fan}"] = {
                "count": len(points),
                "positive_index_count": sum(point.signed_index > 0 for point in points),
                "negative_index_count": sum(point.signed_index < 0 for point in points),
            }
    radius = bbox_diagonal * 1e-3
    agreement = {}
    keys = sorted(critical)
    for left_index, left in enumerate(keys):
        for right in keys[left_index + 1 :]:
            forward, backward = bidirectional_signed_recall(
                critical[left], critical[right], radius=radius
            )
            agreement[f"{'__'.join(left)}--{'__'.join(right)}"] = {
                "left_recall": forward,
                "right_recall": backward,
                "radius_bbox_fraction": 1e-3,
            }
    metrics["pairwise_extractor_agreement"] = agreement
    private = {"points": data.points, "polygons": data.polygons, "wss": data.point_wss}
    return metrics, private


def run(config_path: Path) -> dict:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source = config["source"]
    transport = config["transport"]
    client = RangeClient(max_bytes=int(transport["maximum_http_bytes"]), retries=3)
    url = _url(source["repository"], source["huggingface_revision"], source["batch"])
    phase_rows = []
    private = []
    for phase, member_name, expected_hash in zip(
        source["phases"], source["member_names"], source["expected_vtp_sha256"]
    ):
        payload = _get_member(
            client, url=url, case_id=int(source["case_id"]), member_name=member_name
        )
        observed = hashlib.sha256(payload).hexdigest()
        if observed != expected_hash:
            raise D0Error(f"exact wall-member hash mismatch for phase {phase}")
        metrics, internal = _phase_metrics(phase, payload)
        phase_rows.append({"phase": phase, **metrics})
        private.append(internal)
    if client.requests > int(transport["maximum_requests"]):
        raise D0Error("HTTP request ceiling exceeded")
    points_equal = np.array_equal(private[0]["points"], private[1]["points"])
    polygons_equal = len(private[0]["polygons"]) == len(private[1]["polygons"]) and all(
        np.array_equal(left, right)
        for left, right in zip(private[0]["polygons"], private[1]["polygons"])
    )
    wss_equal = np.array_equal(private[0]["wss"], private[1]["wss"])
    checks = {
        "two_exact_member_hashes_match": all(
            row["sha256"] == expected
            for row, expected in zip(phase_rows, source["expected_vtp_sha256"])
        ),
        "point_and_connectivity_contracts_match_previous_audit": (
            points_equal
            and polygons_equal
            and all(row["points"] == 9399 and row["polygons"] == 4701 for row in phase_rows)
        ),
        "point_wss_is_three_component_finite_and_time_varying": (
            not wss_equal
            and all(row["point_wss_components"] == 3 and row["wss_rms"] > 0 for row in phase_rows)
        ),
        "two_normal_constructions_and_two_polygon_fans_execute": all(
            len(row["normal_modes"]) == 2 and len(row["critical_extractions"]) == 4
            for row in phase_rows
        ),
        "critical_points_are_reported_without_claiming_stability": all(
            all("count" in value for value in row["critical_extractions"].values())
            for row in phase_rows
        ),
    }
    return {
        "schema_version": "aurora.aneumo_transient_vtp_d0.result.v1",
        "protocol_id": config["protocol_id"],
        "state": "development_pass" if all(checks.values()) else "development_fail",
        "scientific_stability_gate_evaluated": False,
        "paper_identity_active": False,
        "method_or_architecture_selected": False,
        "gpu_used": False,
        "raw_or_derived_field_redistributed": False,
        "transport": {"http_requests": client.requests, "http_bytes": client.bytes_read},
        "cross_phase": {
            "point_values_equal": points_equal,
            "polygon_connectivity_equal": polygons_equal,
            "wss_values_equal": wss_equal,
        },
        "phases": phase_rows,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": "reader_and_extractor_development_only_not_target_stability_or_paper_evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.config)
    except Exception as exc:
        result = {
            "schema_version": "aurora.aneumo_transient_vtp_d0.status.v1",
            "protocol_id": "aneumo_transient_vtp_reader_and_structure_development_d0_v1",
            "state": "execution_incomplete",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "scientific_stability_gate_evaluated": False,
            "paper_identity_active": False,
            "method_or_architecture_selected": False,
            "gpu_used": False,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("state") == "development_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
