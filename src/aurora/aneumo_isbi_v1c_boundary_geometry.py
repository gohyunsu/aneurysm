"""Prospective train-only boundary-geometry staging audit for Aneumo V1c."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_range import archive_for_case, fetch_member, load_archive_index


class AneumoV1cBoundaryGeometryError(RuntimeError):
    """Raised when the frozen V1c geometry-staging contract is violated."""


def _imports() -> tuple[Any, Any]:
    try:
        import h5py
        import numpy as np
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoV1cBoundaryGeometryError("V1c requires h5py and numpy.") from exc
    return np, h5py


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneumo_isbi_v1c_boundary_geometry_staging_audit.v1":
        raise AneumoV1cBoundaryGeometryError("Unexpected V1c schema version.")
    if payload.get("status") != "preregistered_after_v1b_pass_before_geometry_array_decode":
        raise AneumoV1cBoundaryGeometryError("V1c must remain prospective to geometry decode.")
    source = payload.get("source", {})
    if source != {
        "dataset": "Aneumo",
        "hf_repo": "SAIS-Life-Science/Aneumo",
        "hf_repo_commit": "f801adee816c18d3e18b23e6fcb147fe4c264209",
        "license": "CC-BY-NC-ND-4.0",
        "staging_config": "configs/aneumo_g2_pilot_v1.json",
        "staging_config_sha256": "f2b027c5f14107531ac1ae33eafab76513bcbdf49ad908c9a35641ae80181b7d",
        "v1b_result": "results/aneumo_isbi_v1b_boundary_asset_audit_20260808.json",
        "v1b_result_sha256": "8cc4871f8d8b234c7c3f3cb3763e5cc959b5653e26349497eb55d2e17b54d901",
        "compact_cache_sha256": "9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9",
    }:
        raise AneumoV1cBoundaryGeometryError("V1c source changed.")
    discovery = payload.get("discovery_boundary", {})
    if (
        discovery.get("already_inspected")
        != "archive_1_case_1_vtp_headers_and_array_names_only"
        or discovery.get("geometry_array_values_decoded_before_registration") is not False
        or discovery.get("v1b_is_post_discovery_asset_evidence") is not True
    ):
        raise AneumoV1cBoundaryGeometryError("V1c discovery boundary changed.")
    access = payload.get("access", {})
    if (
        access.get("splits") != ["train"]
        or access.get("compact_cache_datasets_read") != ["coordinates_m"]
        or access.get("compact_cache_field_values_read") is not False
        or access.get("vtp_arrays_decoded") != ["Points", "connectivity", "offsets"]
        or access.get("vtp_field_arrays_not_decoded") != ["U", "p", "TimeValue"]
        or access.get("validation_payload_read") is not False
        or access.get("test_payload_read") is not False
        or access.get("model_or_checkpoint_use") is not False
        or access.get("training") is not False
    ):
        raise AneumoV1cBoundaryGeometryError("V1c access boundary changed.")
    audit = payload.get("audit", {})
    if (
        audit.get("train_representative_cases") != 20
        or audit.get("patches") != ["inlet", "outlet", "wall"]
        or audit.get("flow_values_kg_s") != [0.001, 0.0025, 0.004]
        or audit.get("reference_flow_kg_s") != 0.0025
        or audit.get("payload_members") != 180
        or audit.get("require_exact_q_invariant_points_and_connectivity") is not True
        or audit.get("minimum_valid_polygon_fraction") != 0.999
        or audit.get("internal_coordinate_bounds_margin_fraction_of_diagonal") != 0.05
        or audit.get("derive_outward_inlet_outlet_normals_from_geometry_only") is not True
    ):
        raise AneumoV1cBoundaryGeometryError("V1c geometry audit changed.")
    cache = payload.get("private_cache", {})
    if (
        cache.get("contents")
        != "reference_flow_boundary_points_connectivity_offsets_and_geometry_summaries_for_twenty_train_representatives"
        or cache.get("contains_U_or_p") is not False
        or cache.get("contains_validation_or_test") is not False
        or cache.get("redistributable") is not False
        or cache.get("public_result_records_sha256_only") is not True
    ):
        raise AneumoV1cBoundaryGeometryError("V1c private-cache boundary changed.")
    expected_checks = [
        "v1b_pass_and_pinned_source_integrity",
        "exact_twenty_train_representatives_and_one_hundred_eighty_payloads",
        "all_vtp_geometry_arrays_crc_verified_and_decoded",
        "points_and_connectivity_exactly_invariant_across_three_flows",
        "all_polygon_topologies_valid_with_fraction_at_least_0.999",
        "all_patch_areas_and_inlet_outlet_frames_finite_and_nonzero",
        "all_compact_internal_coordinates_within_margin_expanded_boundary_bounds",
        "no_field_value_validation_test_model_or_checkpoint_access",
    ]
    gate = payload.get("gate", {})
    if (
        gate.get("checks") != expected_checks
        or gate.get("pass_authorizes")
        != "register_full_boundary_aware_geometry_cache_staging_protocol_only"
        or gate.get("local_repair_allowed") is not False
        or set(gate.get("pass_does_not_authorize", []))
        != {
            "relabel_v1",
            "reuse_or_tune_v1_backbones",
            "model_training",
            "v2_or_test_field_access",
            "method_novelty",
            "isbi_submission",
        }
    ):
        raise AneumoV1cBoundaryGeometryError("V1c cannot authorize learning or repair.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


_DTYPES = {
    "Float32": "<f4",
    "Float64": "<f8",
    "Int32": "<i4",
    "Int64": "<i8",
    "UInt32": "<u4",
    "UInt64": "<u8",
    "UInt8": "u1",
}


def _decode_inline_binary(element: Any) -> Any:
    np, _ = _imports()
    if element.get("format") != "binary" or element.get("type") not in _DTYPES:
        raise AneumoV1cBoundaryGeometryError("Unsupported VTP DataArray encoding.")
    encoded = "".join((element.text or "").split())
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) < 8:
        raise AneumoV1cBoundaryGeometryError("Truncated VTP binary header.")
    length = int(struct.unpack_from("<Q", raw, 0)[0])
    if len(raw) != 8 + length:
        raise AneumoV1cBoundaryGeometryError("VTP binary byte count mismatch.")
    values = np.frombuffer(raw, dtype=np.dtype(_DTYPES[element.get("type")]), offset=8)
    components = int(element.get("NumberOfComponents", "1"))
    if values.size % components:
        raise AneumoV1cBoundaryGeometryError("VTP component count mismatch.")
    return values.reshape(-1, components).copy() if components > 1 else values.copy()


def parse_vtp_geometry(payload: bytes, expected_patch: str) -> dict[str, Any]:
    np, _ = _imports()
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise AneumoV1cBoundaryGeometryError("Invalid VTP XML.") from exc
    if (
        root.tag != "VTKFile"
        or root.get("type") != "PolyData"
        or root.get("compressor")
        or root.get("header_type") != "UInt64"
        or root.get("byte_order") not in {None, "LittleEndian"}
    ):
        raise AneumoV1cBoundaryGeometryError("V1c requires uncompressed inline VTP PolyData.")
    text_head = payload[:512].decode("utf-8", errors="replace")
    if f"patch='{expected_patch}'" not in text_head and f'patch="{expected_patch}"' not in text_head:
        raise AneumoV1cBoundaryGeometryError("VTP patch identity mismatch.")
    piece = root.find("./PolyData/Piece")
    if piece is None:
        raise AneumoV1cBoundaryGeometryError("VTP Piece is missing.")
    points_element = piece.find("./Points/DataArray")
    poly_elements = {
        element.get("Name"): element for element in piece.findall("./Polys/DataArray")
    }
    if points_element is None or set(poly_elements) != {"connectivity", "offsets"}:
        raise AneumoV1cBoundaryGeometryError("VTP geometry arrays are incomplete.")
    points = _decode_inline_binary(points_element)
    connectivity = _decode_inline_binary(poly_elements["connectivity"])
    offsets = _decode_inline_binary(poly_elements["offsets"])
    if points.ndim != 2 or points.shape[1] != 3:
        raise AneumoV1cBoundaryGeometryError("VTP points are not Nx3.")
    connectivity = np.asarray(connectivity, dtype=np.int64).reshape(-1)
    offsets = np.asarray(offsets, dtype=np.int64).reshape(-1)
    if (
        offsets.size == 0
        or np.any(np.diff(offsets) <= 0)
        or offsets[-1] != connectivity.size
        or connectivity.size == 0
        or connectivity.min() < 0
        or connectivity.max() >= points.shape[0]
    ):
        raise AneumoV1cBoundaryGeometryError("VTP polygon topology is invalid.")
    starts = np.concatenate([np.zeros(1, dtype=np.int64), offsets[:-1]])
    if np.any(offsets - starts < 3):
        raise AneumoV1cBoundaryGeometryError("VTP polygon has fewer than three vertices.")
    return {
        "points": np.asarray(points, dtype=np.float64),
        "connectivity": connectivity,
        "offsets": offsets,
        "decoded_arrays": ["Points", "connectivity", "offsets"],
    }


def polygon_geometry(geometry: Mapping[str, Any]) -> dict[str, Any]:
    np, _ = _imports()
    points = geometry["points"]
    connectivity = geometry["connectivity"]
    offsets = geometry["offsets"]
    starts = np.concatenate([np.zeros(1, dtype=np.int64), offsets[:-1]])
    scale = max(float(np.linalg.norm(np.ptp(points, axis=0))), 1e-12)
    threshold = scale * scale * 1e-12
    areas = []
    for start, stop in zip(starts, offsets):
        polygon = points[connectivity[start:stop]]
        origin = polygon[0]
        area = 0.0
        for index in range(1, len(polygon) - 1):
            area += 0.5 * float(
                np.linalg.norm(np.cross(polygon[index] - origin, polygon[index + 1] - origin))
            )
        areas.append(area)
    areas_array = np.asarray(areas, dtype=np.float64)
    valid_fraction = float(np.mean(areas_array > threshold))
    if not np.isfinite(areas_array).all() or float(areas_array.sum()) <= 0.0:
        raise AneumoV1cBoundaryGeometryError("VTP patch area is invalid.")
    return {
        "area_m2": float(areas_array.sum()),
        "valid_polygon_fraction": valid_fraction,
        "centroid_m": np.mean(points, axis=0),
    }


def outward_frame(points: Any, internal_centroid: Any) -> Any:
    np, _ = _imports()
    centered = points - np.mean(points, axis=0, keepdims=True)
    covariance = centered.T @ centered / max(len(points), 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    normal = eigenvectors[:, int(np.argmin(eigenvalues))]
    direction = np.mean(points, axis=0) - internal_centroid
    if float(np.dot(normal, direction)) < 0.0:
        normal = -normal
    norm = float(np.linalg.norm(normal))
    if not math.isfinite(norm) or norm <= 0.0:
        raise AneumoV1cBoundaryGeometryError("Boundary frame is invalid.")
    return normal / norm


def _train_representatives(staging: Mapping[str, Any]) -> list[tuple[int, int]]:
    mapping = {
        int(family): [int(case) for case in cases]
        for family, cases in staging["asset_selection"]["cases_by_base_family"].items()
    }
    train = {int(family) for family in staging["split"]["train_base_families"]}
    return [(family, min(mapping[family])) for family in sorted(train)]


def _attribute_text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def run_audit(
    config: Mapping[str, Any],
    *,
    root: Path,
    compact_cache: Path,
    private_cache: Path,
    output: Path,
    git_commit: str,
) -> dict[str, Any]:
    np, h5py = _imports()
    source = config["source"]
    for key, hash_key in (
        ("staging_config", "staging_config_sha256"),
        ("v1b_result", "v1b_result_sha256"),
    ):
        if _sha256(root / source[key]) != source[hash_key]:
            raise AneumoV1cBoundaryGeometryError(f"V1c dependency mismatch: {key}")
    if _sha256(compact_cache) != source["compact_cache_sha256"]:
        raise AneumoV1cBoundaryGeometryError("V1c compact-cache SHA mismatch.")
    v1b = json.loads((root / source["v1b_result"]).read_text(encoding="utf-8"))
    if (
        v1b["gate"]["all_checks_passed"] is not True
        or v1b["gate"]["decision"] != "register_boundary_aware_cache_staging_audit_only"
    ):
        raise AneumoV1cBoundaryGeometryError("V1b did not authorize V1c registration.")
    staging = json.loads((root / source["staging_config"]).read_text(encoding="utf-8"))
    representatives = _train_representatives(staging)
    archives = sorted(
        {archive_for_case(case) for _, case in representatives},
        key=lambda name: int(name[:-4]),
    )
    base_url = (
        f"https://huggingface.co/datasets/{source['hf_repo']}/resolve/"
        f"{source['hf_repo_commit']}"
    )
    indexes = {
        archive: load_archive_index(f"{base_url}/{archive}")[0] for archive in archives
    }
    compact_coordinates = {}
    with h5py.File(compact_cache, "r") as handle:
        for _, case in representatives:
            group = handle["geometries"][str(case)]
            if _attribute_text(group.attrs["split"]) != "train":
                raise AneumoV1cBoundaryGeometryError("V1c representative is not train split.")
            compact_coordinates[case] = np.asarray(group["coordinates_m"], dtype=np.float64)

    private_cache.parent.mkdir(parents=True, exist_ok=True)
    if private_cache.exists():
        raise AneumoV1cBoundaryGeometryError("V1c refuses to overwrite a private cache.")
    temporary = private_cache.with_name(f".{private_cache.name}.partial")
    if temporary.exists():
        raise AneumoV1cBoundaryGeometryError("A stale V1c partial cache exists.")
    rows = []
    all_q_invariant = True
    all_bounds_contain = True
    all_topology_valid = True
    payload_members_read = 0
    decoded_geometry_arrays: set[str] = set()
    try:
        with h5py.File(temporary, "w") as target:
            target.attrs["dataset"] = "Aneumo"
            target.attrs["license"] = source["license"]
            target.attrs["redistributable"] = False
            target.attrs["contains_U_or_p"] = False
            target.attrs["splits"] = "train"
            target.attrs["coordinate_units"] = "m"
            cases_group = target.create_group("cases")
            for family, case in representatives:
                archive = archive_for_case(case)
                url = f"{base_url}/{archive}"
                index = indexes[archive]
                internal = compact_coordinates[case]
                internal_centroid = np.mean(internal, axis=0)
                case_group = cases_group.create_group(str(case))
                case_group.attrs["base_family"] = family
                boundary_reference = []
                for patch in config["audit"]["patches"]:
                    by_flow = {}
                    for flow in config["audit"]["flow_values_kg_s"]:
                        name = f"{case}/VTK/m={flow:g}/{patch}.vtp"
                        if name not in index:
                            raise AneumoV1cBoundaryGeometryError(f"V1c member missing: {name}")
                        raw = fetch_member(url, index[name])
                        geometry = parse_vtp_geometry(raw, patch)
                        payload_members_read += 1
                        decoded_geometry_arrays.update(geometry["decoded_arrays"])
                        by_flow[float(flow)] = geometry
                    reference = by_flow[float(config["audit"]["reference_flow_kg_s"])]
                    invariant = all(
                        np.array_equal(candidate["points"], reference["points"])
                        and np.array_equal(candidate["connectivity"], reference["connectivity"])
                        and np.array_equal(candidate["offsets"], reference["offsets"])
                        for candidate in by_flow.values()
                    )
                    all_q_invariant = all_q_invariant and invariant
                    summary = polygon_geometry(reference)
                    topology_valid = (
                        summary["valid_polygon_fraction"]
                        >= float(config["audit"]["minimum_valid_polygon_fraction"])
                    )
                    all_topology_valid = all_topology_valid and topology_valid
                    normal = (
                        outward_frame(reference["points"], internal_centroid)
                        if patch in {"inlet", "outlet"}
                        else np.zeros(3, dtype=np.float64)
                    )
                    patch_group = case_group.create_group(patch)
                    patch_group.create_dataset("points_m", data=reference["points"], compression="gzip")
                    patch_group.create_dataset("connectivity", data=reference["connectivity"], compression="gzip")
                    patch_group.create_dataset("offsets", data=reference["offsets"], compression="gzip")
                    patch_group.attrs["area_m2"] = summary["area_m2"]
                    patch_group.attrs["outward_normal"] = normal
                    boundary_reference.append(reference["points"])
                    rows.append(
                        {
                            "family": family,
                            "case": case,
                            "patch": patch,
                            "q_invariant": invariant,
                            "area_m2": summary["area_m2"],
                            "valid_polygon_fraction": summary["valid_polygon_fraction"],
                            "normal_norm": float(np.linalg.norm(normal)) if patch != "wall" else 0.0,
                        }
                    )
                boundary = np.concatenate(boundary_reference, axis=0)
                diagonal = max(float(np.linalg.norm(np.ptp(boundary, axis=0))), 1e-12)
                margin = float(
                    config["audit"]["internal_coordinate_bounds_margin_fraction_of_diagonal"]
                ) * diagonal
                lower = np.min(boundary, axis=0) - margin
                upper = np.max(boundary, axis=0) + margin
                contains = bool(np.all((internal >= lower) & (internal <= upper)))
                all_bounds_contain = all_bounds_contain and contains
                case_group.attrs["compact_internal_coordinates_within_bounds"] = contains
            target.attrs["config_sha256"] = config["_config_sha256"]
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise

    checks = {
        "v1b_pass_and_pinned_source_integrity": True,
        "exact_twenty_train_representatives_and_one_hundred_eighty_payloads": (
            len(representatives) == 20
            and len(rows) == 60
            and payload_members_read == int(config["audit"]["payload_members"])
        ),
        "all_vtp_geometry_arrays_crc_verified_and_decoded": (
            payload_members_read == 180
            and decoded_geometry_arrays == {"Points", "connectivity", "offsets"}
        ),
        "points_and_connectivity_exactly_invariant_across_three_flows": all_q_invariant,
        "all_polygon_topologies_valid_with_fraction_at_least_0.999": all_topology_valid,
        "all_patch_areas_and_inlet_outlet_frames_finite_and_nonzero": all(
            math.isfinite(row["area_m2"])
            and row["area_m2"] > 0.0
            and (row["patch"] == "wall" or abs(row["normal_norm"] - 1.0) <= 1e-8)
            for row in rows
        ),
        "all_compact_internal_coordinates_within_margin_expanded_boundary_bounds": all_bounds_contain,
        "no_field_value_validation_test_model_or_checkpoint_access": True,
    }
    passed = all(checks.values())
    if passed:
        temporary.replace(private_cache)
        private_cache_sha256 = _sha256(private_cache)
        private_cache_bytes = private_cache.stat().st_size
    else:
        temporary.unlink()
        private_cache_sha256 = None
        private_cache_bytes = 0
    result = {
        "schema_version": "aurora.aneumo_isbi_v1c_boundary_geometry_staging_audit.result.v1",
        "experiment_id": config["experiment_id"],
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "source": source,
        "counts": {
            "train_representative_cases": len(representatives),
            "patches": len(rows),
            "payload_members": len(representatives)
            * len(config["audit"]["patches"])
            * len(config["audit"]["flow_values_kg_s"]),
        },
        "geometry": {
            "area_m2_min": min(row["area_m2"] for row in rows),
            "area_m2_max": max(row["area_m2"] for row in rows),
            "valid_polygon_fraction_min": min(row["valid_polygon_fraction"] for row in rows),
            "q_invariant_patch_count": sum(row["q_invariant"] for row in rows),
            "private_cache_staged": passed,
            "private_cache_sha256": private_cache_sha256,
            "private_cache_bytes": private_cache_bytes,
            "private_cache_redistributable": False,
            "private_cache_contains_U_or_p": False,
        },
        "field_access": {
            "compact_cache_datasets_read": ["coordinates_m"],
            "vtp_arrays_decoded": ["Points", "connectivity", "offsets"],
            "vtp_field_arrays_decoded": [],
            "validation_payload_read": False,
            "test_payload_read": False,
        },
        "gate": {
            "checks": checks,
            "passed_checks": sum(bool(value) for value in checks.values()),
            "total_checks": len(checks),
            "all_checks_passed": passed,
            "decision": (
                "register_full_boundary_aware_geometry_cache_staging_protocol_only"
                if passed
                else config["gate"]["failure_action"]
            ),
            "pass_authorizes": config["gate"]["pass_authorizes"],
            "pass_does_not_authorize": config["gate"]["pass_does_not_authorize"],
        },
        "interpretation": config["interpretation"],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "status.json").write_text(
        json.dumps(
            {"exit_status": 0, "state": "complete", "test_payload_read": False},
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
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--compact-cache", type=Path, required=True)
    parser.add_argument("--private-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    try:
        result = run_audit(
            config,
            root=args.root,
            compact_cache=args.compact_cache,
            private_cache=args.private_cache,
            output=args.output,
            git_commit=args.git_commit,
        )
    except Exception:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "status.json").write_text(
            json.dumps(
                {"exit_status": 1, "state": "failed", "test_payload_read": False},
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
