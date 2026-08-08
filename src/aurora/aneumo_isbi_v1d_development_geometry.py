"""Prospective field-free development geometry-cache audit for Aneumo V1d."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_isbi_v1c_boundary_geometry import (
    _attribute_text,
    _decode_inline_binary,
    _imports,
    _sha256,
    outward_frame,
    parse_vtp_geometry,
    polygon_geometry,
)
from .aneumo_range import archive_for_case, fetch_member, load_archive_index


class AneumoV1dDevelopmentGeometryError(RuntimeError):
    """Raised when the frozen V1d development-cache contract is violated."""


_SOURCE = {
    "dataset": "Aneumo",
    "hf_repo": "SAIS-Life-Science/Aneumo",
    "hf_repo_commit": "f801adee816c18d3e18b23e6fcb147fe4c264209",
    "license": "CC-BY-NC-ND-4.0",
    "staging_config": "configs/aneumo_g2_pilot_v1.json",
    "staging_config_sha256": "f2b027c5f14107531ac1ae33eafab76513bcbdf49ad908c9a35641ae80181b7d",
    "v1c_result": "results/aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json",
    "v1c_result_sha256": "a023e9fbcbcbc1fc719c8a902a582dee031cf3e08d360d28a741f5530aa2bbd1",
    "compact_cache_sha256": "9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9",
}


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneumo_isbi_v1d_development_geometry_cache.v1":
        raise AneumoV1dDevelopmentGeometryError("Unexpected V1d schema version.")
    if payload.get("status") != (
        "preregistered_after_v1c_pass_before_validation_geometry_payload_decode"
    ):
        raise AneumoV1dDevelopmentGeometryError("V1d must remain prospective to validation geometry.")
    if payload.get("source") != _SOURCE:
        raise AneumoV1dDevelopmentGeometryError("V1d source changed.")
    discovery = payload.get("discovery_boundary", {})
    if (
        discovery.get("already_decoded_by_v1c")
        != "twenty_train_representatives_three_patches_three_flows_geometry_only"
        or discovery.get("validation_geometry_payload_decoded_before_registration") is not False
        or discovery.get("remaining_train_geometry_payload_decoded_before_registration") is not False
        or discovery.get("v1c_result_is_asset_evidence_only") is not True
    ):
        raise AneumoV1dDevelopmentGeometryError("V1d discovery boundary changed.")
    access = payload.get("access", {})
    if (
        access.get("splits") != ["train", "validation"]
        or access.get("expected_cases_by_split")
        != {"train": 40, "validation": 12, "test": 0}
        or access.get("compact_cache_datasets_read") != ["coordinates_m"]
        or access.get("compact_cache_field_values_read") is not False
        or access.get("boundary_vtp_arrays_decoded")
        != ["Points", "connectivity", "offsets"]
        or access.get("volume_vtu_arrays_decoded") != ["Points"]
        or access.get("field_arrays_not_decoded") != ["U", "p", "TimeValue"]
        or access.get("validation_geometry_payload_read") is not True
        or access.get("validation_field_array_decoded") is not False
        or access.get("test_payload_read") is not False
        or access.get("model_or_checkpoint_use") is not False
        or access.get("training") is not False
    ):
        raise AneumoV1dDevelopmentGeometryError("V1d access boundary changed.")
    audit = payload.get("audit", {})
    if (
        audit.get("development_cases") != 52
        or audit.get("patches") != ["inlet", "outlet", "wall"]
        or audit.get("flow_values_kg_s") != [0.001, 0.0025, 0.004]
        or audit.get("reference_flow_kg_s") != 0.0025
        or audit.get("boundary_payload_members") != 468
        or audit.get("volume_payload_members") != 52
        or audit.get("total_payload_members") != 520
        or audit.get("require_exact_q_invariant_boundary_geometry") is not True
        or audit.get("require_every_boundary_point_in_reference_volume_points") is not True
        or audit.get("minimum_valid_polygon_fraction") != 0.999
        or audit.get("internal_coordinate_bounds_margin_fraction_of_diagonal") != 0.05
        or audit.get("derive_outward_inlet_outlet_normals_from_geometry_only") is not True
    ):
        raise AneumoV1dDevelopmentGeometryError("V1d audit changed.")
    cache = payload.get("private_cache", {})
    if (
        cache.get("contents")
        != "reference_flow_boundary_points_connectivity_offsets_geometry_summaries_and_volume_correspondence_for_fifty_two_development_cases"
        or cache.get("contains_U_or_p") is not False
        or cache.get("contains_test") is not False
        or cache.get("redistributable") is not False
        or cache.get("public_result_records_sha256_only") is not True
    ):
        raise AneumoV1dDevelopmentGeometryError("V1d private-cache contract changed.")
    expected_checks = [
        "v1c_pass_and_pinned_source_integrity",
        "exact_forty_train_twelve_validation_zero_test_cases",
        "exact_four_hundred_sixty_eight_boundary_and_fifty_two_volume_payloads",
        "all_boundary_geometry_exactly_invariant_across_three_flows",
        "all_polygon_topologies_areas_and_inlet_outlet_frames_valid",
        "every_boundary_point_exactly_present_in_reference_volume_points",
        "all_compact_internal_coordinates_within_margin_expanded_boundary_bounds",
        "private_cache_schema_is_field_free_development_only_and_nonredistributable",
        "no_field_value_test_model_or_checkpoint_access",
    ]
    gate = payload.get("gate", {})
    if (
        gate.get("checks") != expected_checks
        or gate.get("pass_authorizes")
        != "register_boundary_aware_known_condition_baseline_protocol_only"
        or gate.get("local_repair_allowed") is not False
        or set(gate.get("pass_does_not_authorize", []))
        != {
            "relabel_v1",
            "reuse_or_tune_v1_backbones",
            "model_training",
            "test_geometry_or_field_access",
            "v2_outer_test",
            "partial_or_missing_condition_method",
            "method_novelty",
            "isbi_submission",
        }
    ):
        raise AneumoV1dDevelopmentGeometryError("V1d cannot authorize training or test access.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def parse_vtu_points(payload: bytes) -> dict[str, Any]:
    np, _ = _imports()
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise AneumoV1dDevelopmentGeometryError("Invalid VTU XML.") from exc
    if (
        root.tag != "VTKFile"
        or root.get("type") != "UnstructuredGrid"
        or root.get("compressor")
        or root.get("header_type") != "UInt64"
        or root.get("byte_order") not in {None, "LittleEndian"}
    ):
        raise AneumoV1dDevelopmentGeometryError(
            "V1d requires uncompressed inline VTU UnstructuredGrid."
        )
    piece = root.find("./UnstructuredGrid/Piece")
    if piece is None:
        raise AneumoV1dDevelopmentGeometryError("VTU Piece is missing.")
    points_element = piece.find("./Points/DataArray")
    if points_element is None:
        raise AneumoV1dDevelopmentGeometryError("VTU Points are missing.")
    points = _decode_inline_binary(points_element)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise AneumoV1dDevelopmentGeometryError("VTU points are not finite Nx3.")
    expected_points = int(piece.get("NumberOfPoints", "-1"))
    if expected_points != points.shape[0] or expected_points <= 0:
        raise AneumoV1dDevelopmentGeometryError("VTU point count changed.")
    available_fields = {
        element.get("Name") for element in piece.findall("./PointData/DataArray")
    }
    if not {"U", "p"}.issubset(available_fields):
        raise AneumoV1dDevelopmentGeometryError("VTU field contract is incomplete.")
    return {
        "points": np.asarray(points, dtype=np.float64),
        "decoded_arrays": ["Points"],
        "available_but_not_decoded": sorted(name for name in available_fields if name),
    }


def exact_surface_subset(surface_points: Any, volume_points: Any) -> bool:
    np, _ = _imports()
    surface = np.ascontiguousarray(surface_points, dtype="<f8")
    volume = np.ascontiguousarray(volume_points, dtype="<f8")
    if surface.ndim != 2 or volume.ndim != 2 or surface.shape[1:] != (3,) or volume.shape[1:] != (3,):
        raise AneumoV1dDevelopmentGeometryError("Surface/volume point shape changed.")
    key_dtype = np.dtype((np.void, surface.dtype.itemsize * 3))
    surface_keys = surface.view(key_dtype).reshape(-1)
    volume_keys = volume.view(key_dtype).reshape(-1)
    return bool(np.isin(surface_keys, volume_keys, assume_unique=False).all())


def _development_cases(staging: Mapping[str, Any]) -> list[tuple[int, int, str]]:
    mapping = {
        int(family): [int(case) for case in cases]
        for family, cases in staging["asset_selection"]["cases_by_base_family"].items()
    }
    rows = []
    for split in ("train", "validation"):
        families = [int(item) for item in staging["split"][f"{split}_base_families"]]
        for family in sorted(families):
            rows.extend((family, case, split) for case in sorted(mapping[family]))
    return rows


def _cache_contract(path: Path, expected_cases: int) -> bool:
    _, h5py = _imports()
    with h5py.File(path, "r") as handle:
        if (
            _attribute_text(handle.attrs["splits"]) != "train,validation"
            or bool(handle.attrs["redistributable"])
            or bool(handle.attrs["contains_U_or_p"])
            or bool(handle.attrs["contains_test"])
            or set(handle["cases"].keys()) == set()
            or len(handle["cases"]) != expected_cases
        ):
            return False
        for group in handle["cases"].values():
            if _attribute_text(group.attrs["split"]) not in {"train", "validation"}:
                return False
            if set(group.keys()) != {"inlet", "outlet", "wall"}:
                return False
    return True


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
        ("v1c_result", "v1c_result_sha256"),
    ):
        if _sha256(root / source[key]) != source[hash_key]:
            raise AneumoV1dDevelopmentGeometryError(f"V1d dependency mismatch: {key}")
    if _sha256(compact_cache) != source["compact_cache_sha256"]:
        raise AneumoV1dDevelopmentGeometryError("V1d compact-cache SHA mismatch.")
    v1c = json.loads((root / source["v1c_result"]).read_text(encoding="utf-8"))
    if (
        v1c["gate"]["all_checks_passed"] is not True
        or v1c["gate"]["decision"]
        != "register_full_boundary_aware_geometry_cache_staging_protocol_only"
    ):
        raise AneumoV1dDevelopmentGeometryError("V1c did not authorize V1d registration.")
    staging = json.loads((root / source["staging_config"]).read_text(encoding="utf-8"))
    cases = _development_cases(staging)
    archives = sorted(
        {archive_for_case(case) for _, case, _ in cases},
        key=lambda name: int(name[:-4]),
    )
    base_url = (
        f"https://huggingface.co/datasets/{source['hf_repo']}/resolve/"
        f"{source['hf_repo_commit']}"
    )
    indexes = {
        archive: load_archive_index(f"{base_url}/{archive}")[0] for archive in archives
    }
    compact_coordinates: dict[int, Any] = {}
    with h5py.File(compact_cache, "r") as handle:
        for _, case, split in cases:
            group = handle["geometries"][str(case)]
            if _attribute_text(group.attrs["split"]) != split:
                raise AneumoV1dDevelopmentGeometryError("Compact-cache split changed.")
            compact_coordinates[case] = np.asarray(group["coordinates_m"], dtype=np.float64)

    private_cache.parent.mkdir(parents=True, exist_ok=True)
    if private_cache.exists():
        raise AneumoV1dDevelopmentGeometryError("V1d refuses to overwrite a private cache.")
    temporary = private_cache.with_name(f".{private_cache.name}.partial")
    if temporary.exists():
        raise AneumoV1dDevelopmentGeometryError("A stale V1d partial cache exists.")
    patch_rows: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []
    boundary_payloads_read = 0
    volume_payloads_read = 0
    decoded_boundary_arrays: set[str] = set()
    decoded_volume_arrays: set[str] = set()
    available_field_arrays: set[str] = set()
    try:
        with h5py.File(temporary, "w") as target:
            target.attrs["dataset"] = "Aneumo"
            target.attrs["license"] = source["license"]
            target.attrs["redistributable"] = False
            target.attrs["contains_U_or_p"] = False
            target.attrs["contains_test"] = False
            target.attrs["splits"] = "train,validation"
            target.attrs["coordinate_units"] = "m"
            cases_group = target.create_group("cases")
            for case_index, (family, case, split) in enumerate(cases, start=1):
                print(
                    f"[V1d geometry] case {case_index}/{len(cases)} id={case} split={split}",
                    flush=True,
                )
                archive = archive_for_case(case)
                url = f"{base_url}/{archive}"
                index = indexes[archive]
                internal = compact_coordinates[case]
                internal_centroid = np.mean(internal, axis=0)
                reference_flow = float(config["audit"]["reference_flow_kg_s"])
                volume_name = f"{case}/VTK/m={reference_flow:g}/internal.vtu"
                if volume_name not in index:
                    raise AneumoV1dDevelopmentGeometryError(
                        f"V1d volume member missing: {volume_name}"
                    )
                volume = parse_vtu_points(fetch_member(url, index[volume_name]))
                volume_payloads_read += 1
                decoded_volume_arrays.update(volume["decoded_arrays"])
                available_field_arrays.update(volume["available_but_not_decoded"])
                case_group = cases_group.create_group(str(case))
                case_group.attrs["base_family"] = family
                case_group.attrs["split"] = split
                case_group.attrs["volume_point_count"] = len(volume["points"])
                boundary_reference = []
                for patch in config["audit"]["patches"]:
                    by_flow = {}
                    for flow in config["audit"]["flow_values_kg_s"]:
                        name = f"{case}/VTK/m={flow:g}/{patch}.vtp"
                        if name not in index:
                            raise AneumoV1dDevelopmentGeometryError(
                                f"V1d boundary member missing: {name}"
                            )
                        geometry = parse_vtp_geometry(fetch_member(url, index[name]), patch)
                        boundary_payloads_read += 1
                        decoded_boundary_arrays.update(geometry["decoded_arrays"])
                        by_flow[float(flow)] = geometry
                    reference = by_flow[reference_flow]
                    q_invariant = all(
                        np.array_equal(candidate["points"], reference["points"])
                        and np.array_equal(
                            candidate["connectivity"], reference["connectivity"]
                        )
                        and np.array_equal(candidate["offsets"], reference["offsets"])
                        for candidate in by_flow.values()
                    )
                    summary = polygon_geometry(reference)
                    normal = (
                        outward_frame(reference["points"], internal_centroid)
                        if patch in {"inlet", "outlet"}
                        else np.zeros(3, dtype=np.float64)
                    )
                    patch_group = case_group.create_group(patch)
                    patch_group.create_dataset(
                        "points_m", data=reference["points"], compression="gzip"
                    )
                    patch_group.create_dataset(
                        "connectivity", data=reference["connectivity"], compression="gzip"
                    )
                    patch_group.create_dataset(
                        "offsets", data=reference["offsets"], compression="gzip"
                    )
                    patch_group.attrs["area_m2"] = summary["area_m2"]
                    patch_group.attrs["outward_normal"] = normal
                    boundary_reference.append(reference["points"])
                    patch_rows.append(
                        {
                            "case": case,
                            "patch": patch,
                            "q_invariant": q_invariant,
                            "area_m2": summary["area_m2"],
                            "valid_polygon_fraction": summary["valid_polygon_fraction"],
                            "normal_norm": (
                                float(np.linalg.norm(normal)) if patch != "wall" else 0.0
                            ),
                        }
                    )
                boundary = np.concatenate(boundary_reference, axis=0)
                diagonal = max(float(np.linalg.norm(np.ptp(boundary, axis=0))), 1e-12)
                margin = float(
                    config["audit"]["internal_coordinate_bounds_margin_fraction_of_diagonal"]
                ) * diagonal
                within_bounds = bool(
                    np.all(
                        (internal >= np.min(boundary, axis=0) - margin)
                        & (internal <= np.max(boundary, axis=0) + margin)
                    )
                )
                surface_in_volume = exact_surface_subset(boundary, volume["points"])
                case_group.attrs["compact_internal_coordinates_within_bounds"] = within_bounds
                case_group.attrs["all_boundary_points_in_volume"] = surface_in_volume
                case_rows.append(
                    {
                        "case": case,
                        "split": split,
                        "within_bounds": within_bounds,
                        "surface_in_volume": surface_in_volume,
                        "volume_point_count": len(volume["points"]),
                    }
                )
            target.attrs["config_sha256"] = config["_config_sha256"]
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise

    split_counts = {
        split: sum(row["split"] == split for row in case_rows)
        for split in ("train", "validation", "test")
    }
    cache_contract = _cache_contract(temporary, len(cases))
    checks = {
        "v1c_pass_and_pinned_source_integrity": True,
        "exact_forty_train_twelve_validation_zero_test_cases": split_counts
        == {"train": 40, "validation": 12, "test": 0},
        "exact_four_hundred_sixty_eight_boundary_and_fifty_two_volume_payloads": (
            boundary_payloads_read == int(config["audit"]["boundary_payload_members"])
            and volume_payloads_read == int(config["audit"]["volume_payload_members"])
            and decoded_boundary_arrays == {"Points", "connectivity", "offsets"}
            and decoded_volume_arrays == {"Points"}
        ),
        "all_boundary_geometry_exactly_invariant_across_three_flows": all(
            row["q_invariant"] for row in patch_rows
        ),
        "all_polygon_topologies_areas_and_inlet_outlet_frames_valid": all(
            row["valid_polygon_fraction"]
            >= float(config["audit"]["minimum_valid_polygon_fraction"])
            and math.isfinite(row["area_m2"])
            and row["area_m2"] > 0.0
            and (row["patch"] == "wall" or abs(row["normal_norm"] - 1.0) <= 1e-8)
            for row in patch_rows
        ),
        "every_boundary_point_exactly_present_in_reference_volume_points": all(
            row["surface_in_volume"] for row in case_rows
        ),
        "all_compact_internal_coordinates_within_margin_expanded_boundary_bounds": all(
            row["within_bounds"] for row in case_rows
        ),
        "private_cache_schema_is_field_free_development_only_and_nonredistributable": cache_contract,
        "no_field_value_test_model_or_checkpoint_access": available_field_arrays.issuperset(
            {"U", "p"}
        ),
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
        "schema_version": "aurora.aneumo_isbi_v1d_development_geometry_cache.result.v1",
        "experiment_id": config["experiment_id"],
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "source": source,
        "counts": {
            "train_cases": split_counts["train"],
            "validation_cases": split_counts["validation"],
            "test_cases": split_counts["test"],
            "patches": len(patch_rows),
            "boundary_payload_members": boundary_payloads_read,
            "volume_payload_members": volume_payloads_read,
        },
        "geometry": {
            "area_m2_min": min(row["area_m2"] for row in patch_rows),
            "area_m2_max": max(row["area_m2"] for row in patch_rows),
            "valid_polygon_fraction_min": min(
                row["valid_polygon_fraction"] for row in patch_rows
            ),
            "q_invariant_patch_count": sum(row["q_invariant"] for row in patch_rows),
            "surface_in_volume_case_count": sum(
                row["surface_in_volume"] for row in case_rows
            ),
            "volume_point_count_min": min(row["volume_point_count"] for row in case_rows),
            "volume_point_count_max": max(row["volume_point_count"] for row in case_rows),
            "private_cache_staged": passed,
            "private_cache_sha256": private_cache_sha256,
            "private_cache_bytes": private_cache_bytes,
            "private_cache_redistributable": False,
            "private_cache_contains_U_or_p": False,
            "private_cache_contains_test": False,
        },
        "field_access": {
            "compact_cache_datasets_read": ["coordinates_m"],
            "boundary_vtp_arrays_decoded": ["Points", "connectivity", "offsets"],
            "volume_vtu_arrays_decoded": ["Points"],
            "field_arrays_decoded": [],
            "validation_geometry_payload_read": True,
            "validation_field_array_decoded": False,
            "test_payload_read": False,
        },
        "gate": {
            "checks": checks,
            "passed_checks": sum(bool(value) for value in checks.values()),
            "total_checks": len(checks),
            "all_checks_passed": passed,
            "decision": (
                "register_boundary_aware_known_condition_baseline_protocol_only"
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
