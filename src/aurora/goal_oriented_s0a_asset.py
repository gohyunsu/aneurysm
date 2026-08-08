"""Run the method-free CMHA asset component of the frozen S0a gate.

The executable intentionally uses only the Python standard library.  It reads
archive bytes, CSV columns needed for identifiers/counts, NIfTI headers and STL
vertices.  It never loads CTA voxels, CFD fields, rupture labels or a model, and
it never serializes a source identifier or private path.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import struct
from collections import Counter
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterable, List, Mapping, Sequence, Tuple


class AssetComponentProtocolError(ValueError):
    """Raised when the asset-component contract is weakened or inconsistent."""


EXPECTED_CHECKS = {
    "official_archive_size_and_md5_match",
    "five_statistical_csv_members_match",
    "patient_lesion_control_counts_match",
    "six_multi_lesion_patient_groups_recovered",
    "all_105_lesions_have_exact_identifier_linked_cta_parent_aneurysm_stl_and_aneurysm_stl",
    "no_row_order_or_filename_similarity_only_linkage",
    "nifti_spacing_orientation_and_stl_units_frames_are_finite_and_plausible",
    "aggregate_contains_no_identifier_private_path_image_voxel_or_field_payload",
    "training_gpu_outer_test_and_rupture_label_use_are_zero",
}

EXPECTED_ARCHIVES = {
    "controls": (4821489080, "8d18b970978a303ed89618066919a1b1"),
    "statistics": (34376, "12b92693c79587fb6dbab4638bfad8bc"),
    "patients": (10735821611, "e783d656ba51c6813aae9fca68565c17"),
}

EXPECTED_CSVS = {
    "clinical_all.csv",
    "hemodynamic_aneurysm_artery.csv",
    "hemodynamic_control.csv",
    "morphological_aneurysm_artery.csv",
    "morphological_control.csv",
}


def load_asset_config(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssetComponentProtocolError(f"Asset config does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssetComponentProtocolError(f"Invalid asset JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise AssetComponentProtocolError("Asset config root must be an object.")
    return payload


def validate_asset_config(config: Mapping[str, Any]) -> Tuple[str, ...]:
    required = {
        "schema_version",
        "protocol_id",
        "status",
        "purpose",
        "parent_s0a_config",
        "parent_s0a_config_sha256",
        "discovery_record",
        "discovery_record_sha256",
        "discovery_boundary",
        "official_release",
        "expected_units",
        "linkage_contract",
        "geometry_contract",
        "required_checks",
        "execution",
        "decision",
        "authorization",
    }
    missing = sorted(required - set(config))
    if missing:
        raise AssetComponentProtocolError(f"Asset config is missing: {', '.join(missing)}")
    if config["schema_version"] != "1.0" or config["protocol_id"] != (
        "goal_oriented_hemodynamic_segmentation_s0a_asset_component_v1"
    ):
        raise AssetComponentProtocolError("Unexpected asset-component schema or id.")
    if config["purpose"] != (
        "execute_the_asset_subset_of_the_existing_s0a_all_or_none_gate_with_early_stop"
    ):
        raise AssetComponentProtocolError("The asset component cannot become a model experiment.")

    discovery = config["discovery_boundary"]
    if (
        discovery.get("official_archive_size_and_md5_known_matching") is not True
        or discovery.get("existing_extracted_top_level_known_present") is not True
        or any(
            discovery.get(key) is not False
            for key in (
                "statistical_csv_opened",
                "identifier_mapping_attempted",
                "nifti_or_stl_header_opened",
                "image_voxel_or_field_payload_opened",
                "scientific_check_claimed_passed",
            )
        )
    ):
        raise AssetComponentProtocolError("The pre-registration discovery boundary changed.")

    release = config["official_release"]
    observed_archives = {
        item.get("label"): (item.get("bytes"), item.get("md5"))
        for item in release.get("archives", [])
    }
    if (
        release.get("license") != "CC_BY_4_0"
        or observed_archives != EXPECTED_ARCHIVES
        or set(release.get("statistical_members", [])) != EXPECTED_CSVS
    ):
        raise AssetComponentProtocolError("Official CMHA release pins changed.")

    if config["expected_units"] != {
        "patients": 99,
        "lesions": 105,
        "controls": 44,
        "multi_lesion_patients": 6,
        "patient_identifier_column": "number",
        "lesion_identifier_column": "number",
        "lesions_are_independent_samples": False,
    }:
        raise AssetComponentProtocolError("CMHA unit or identifier contract changed.")
    linkage = config["linkage_contract"]
    if (
        linkage.get("clinical_to_morphology") != "explicit_identifier_values_only"
        or linkage.get("morphology_to_hemodynamics")
        != "exact_unique_lesion_identifier_set"
        or linkage.get("morphology_to_case_directory")
        != "exact_unique_lesion_identifier_set"
        or linkage.get("row_position_fallback") is not False
        or linkage.get("prefix_or_filename_similarity_fallback") is not False
        or set(linkage.get("each_lesion_requires", []))
        != {
            "one_cta_nifti",
            "one_parent_plus_aneurysm_stl",
            "one_aneurysm_only_stl",
        }
    ):
        raise AssetComponentProtocolError("Exact-ID/no-fallback linkage changed.")

    geometry = config["geometry_contract"]
    exact_geometry = {
        "source_article_cta_matrix": 512,
        "source_article_field_of_view_mm": 230,
        "source_article_slice_thickness_mm": 1.25,
        "source_article_interlayer_spacing_mm": 0.625,
        "nifti_spatial_dimension_min": 16,
        "nifti_spatial_dimension_max": 2048,
        "nifti_spacing_min_mm": 0.1,
        "nifti_spacing_max_mm": 2.0,
        "nifti_physical_extent_min_mm": 5.0,
        "nifti_physical_extent_max_mm": 600.0,
        "nifti_qform_or_sform_required": True,
        "stl_axis_extent_min_mm": 0.01,
        "stl_axis_extent_max_mm": 600.0,
        "stl_absolute_coordinate_max_mm": 2000.0,
        "allowed_frame_transforms": ["identity", "lps_to_ras_xy_sign_flip"],
        "allowed_coordinate_scale": 1.0,
        "containment_tolerance_mm": 5.0,
        "all_lesions_must_pass": True,
    }
    if geometry != exact_geometry:
        raise AssetComponentProtocolError("Frozen NIfTI/STL geometry limits changed.")
    if set(config["required_checks"]) != EXPECTED_CHECKS:
        raise AssetComponentProtocolError("All nine asset checks must remain frozen.")

    execution = config["execution"]
    if (
        execution.get("server_role") != "introai9_read_only_source_asset_audit"
        or execution.get("scheduler") != "PBS"
        or execution.get("queue") != "coss_agpu"
        or execution.get("resource") != "4_cpu_16_gb_no_gpu"
        or execution.get("pbs_attempts_for_this_public_source") != 1
        or execution.get("login_node_heavy_work") is not False
        or execution.get("raw_and_extracted_assets_read_only") is not True
        or execution.get("code_read_only") is not True
        or execution.get("output_only_writable") is not True
        or execution.get("private_paths_in_config") is not False
        or execution.get("public_aggregate_only") is not True
    ):
        raise AssetComponentProtocolError("Asset execution must stay one-shot CPU/PBS/read-only.")

    decision = config["decision"]
    if (
        decision.get("all_nine_checks_required") is not True
        or decision.get("scientific_check_failure")
        != "close_the_current_goal_oriented_candidate_without_solver_v2_model_gpu_or_outer_test"
        or decision.get("execution_incomplete")
        != "preserve_no_s0a_verdict_and_forbid_same_source_resubmission"
        or decision.get("all_nine_pass_authorizes")
        != "register_one_distinct_prospective_no_runtime_network_solver_preflight_v2_only"
        or decision.get("all_nine_pass_is_s0a_pass") is not False
        or decision.get("same_source_rerun") is not False
        or decision.get("threshold_relaxation_after_result") is not False
        or decision.get("existing_s0a_relabelled") is not False
    ):
        raise AssetComponentProtocolError("Asset early-stop/no-repair decision changed.")
    authorization = config["authorization"]
    if any(value is not False for value in authorization.values()):
        raise AssetComponentProtocolError("Asset audit cannot authorize a solver, model or test.")
    return (
        "pre-access discovery boundary pinned",
        "official archives and statistical members pinned",
        "exact-ID linkage without positional fallback pinned",
        "NIfTI/STL unit and frame limits pinned",
        "nine-check one-shot CPU audit with no model authorization pinned",
    )


def _md5(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_bytes)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _open_nifti(path: Path) -> BinaryIO:
    if path.name.lower().endswith(".gz"):
        return gzip.open(str(path), "rb")
    return path.open("rb")


def _qform_affine(endian: str, header: bytes, pixdim: Sequence[float]) -> List[List[float]]:
    b, c, d = struct.unpack_from(endian + "3f", header, 256)
    x, y, z = struct.unpack_from(endian + "3f", header, 268)
    norm = b * b + c * c + d * d
    if norm > 1.0:
        scale = math.sqrt(norm)
        b, c, d = b / scale, c / scale, d / scale
        a = 0.0
    else:
        a = math.sqrt(max(0.0, 1.0 - norm))
    dx, dy, dz = (abs(float(value)) for value in pixdim[1:4])
    if pixdim[0] < 0:
        dz = -dz
    rotation = [
        [a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
        [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
        [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - c * c - b * b],
    ]
    scales = [dx, dy, dz]
    affine = [[rotation[row][col] * scales[col] for col in range(3)] for row in range(3)]
    affine[0].append(float(x))
    affine[1].append(float(y))
    affine[2].append(float(z))
    affine.append([0.0, 0.0, 0.0, 1.0])
    return affine


def read_nifti_header(path: Path) -> Dict[str, Any]:
    with _open_nifti(path) as stream:
        header = stream.read(352)
    if len(header) < 348:
        raise ValueError("NIfTI header is truncated")
    little = struct.unpack_from("<i", header, 0)[0]
    big = struct.unpack_from(">i", header, 0)[0]
    if little == 348:
        endian = "<"
    elif big == 348:
        endian = ">"
    else:
        raise ValueError("NIfTI sizeof_hdr is not 348")
    dim = struct.unpack_from(endian + "8h", header, 40)
    pixdim = struct.unpack_from(endian + "8f", header, 76)
    spatial = tuple(int(value) for value in dim[1:4])
    spacing = tuple(abs(float(value)) for value in pixdim[1:4])
    qform_code, sform_code = struct.unpack_from(endian + "2h", header, 252)
    if sform_code > 0:
        affine = [
            list(struct.unpack_from(endian + "4f", header, offset))
            for offset in (280, 296, 312)
        ]
        affine.append([0.0, 0.0, 0.0, 1.0])
        affine_source = "sform"
    elif qform_code > 0:
        affine = _qform_affine(endian, header, pixdim)
        affine_source = "qform"
    else:
        raise ValueError("NIfTI has neither qform nor sform")
    values = [value for row in affine for value in row]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("NIfTI affine is non-finite")
    determinant = (
        affine[0][0] * (affine[1][1] * affine[2][2] - affine[1][2] * affine[2][1])
        - affine[0][1] * (affine[1][0] * affine[2][2] - affine[1][2] * affine[2][0])
        + affine[0][2] * (affine[1][0] * affine[2][1] - affine[1][1] * affine[2][0])
    )
    if not math.isfinite(determinant) or abs(determinant) <= 1e-12:
        raise ValueError("NIfTI affine is singular")
    world = []
    for i in (0, spatial[0] - 1):
        for j in (0, spatial[1] - 1):
            for k in (0, spatial[2] - 1):
                world.append(
                    tuple(
                        affine[row][0] * i
                        + affine[row][1] * j
                        + affine[row][2] * k
                        + affine[row][3]
                        for row in range(3)
                    )
                )
    bounds_min = tuple(min(point[axis] for point in world) for axis in range(3))
    bounds_max = tuple(max(point[axis] for point in world) for axis in range(3))
    return {
        "spatial": spatial,
        "spacing": spacing,
        "physical_extent": tuple(spatial[i] * spacing[i] for i in range(3)),
        "bounds_min": bounds_min,
        "bounds_max": bounds_max,
        "affine_source": affine_source,
    }


def _update_bounds(
    mins: List[float], maxs: List[float], values: Iterable[float]
) -> None:
    coords = list(values)
    if len(coords) != 3 or not all(math.isfinite(value) for value in coords):
        raise ValueError("STL contains a non-finite vertex")
    for axis, value in enumerate(coords):
        mins[axis] = min(mins[axis], value)
        maxs[axis] = max(maxs[axis], value)


def read_stl_bounds(path: Path) -> Dict[str, Any]:
    size = path.stat().st_size
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    triangle_count = 0
    with path.open("rb") as stream:
        prefix = stream.read(84)
        if len(prefix) >= 84:
            declared = struct.unpack_from("<I", prefix, 80)[0]
            is_binary = 84 + declared * 50 == size
        else:
            is_binary = False
        stream.seek(0)
        if is_binary:
            stream.read(84)
            for _ in range(declared):
                record = stream.read(50)
                if len(record) != 50:
                    raise ValueError("Binary STL is truncated")
                floats = struct.unpack_from("<12f", record, 0)
                for start in (3, 6, 9):
                    _update_bounds(mins, maxs, floats[start : start + 3])
            triangle_count = int(declared)
            encoding = "binary"
        else:
            for line in stream:
                stripped = line.strip().lower()
                if stripped.startswith(b"facet normal"):
                    triangle_count += 1
                elif stripped.startswith(b"vertex "):
                    parts = stripped.split()
                    if len(parts) != 4:
                        raise ValueError("ASCII STL vertex is malformed")
                    _update_bounds(mins, maxs, (float(item) for item in parts[1:]))
            encoding = "ascii"
    if triangle_count <= 0 or any(not math.isfinite(value) for value in mins + maxs):
        raise ValueError("STL has no finite triangles")
    return {
        "bounds_min": tuple(mins),
        "bounds_max": tuple(maxs),
        "extent": tuple(maxs[i] - mins[i] for i in range(3)),
        "triangles": triangle_count,
        "encoding": encoding,
    }


def _transformed_bounds(
    mins: Sequence[float], maxs: Sequence[float], transform: str
) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    signs = (1.0, 1.0, 1.0) if transform == "identity" else (-1.0, -1.0, 1.0)
    out_min = []
    out_max = []
    for axis, sign in enumerate(signs):
        pair = (sign * mins[axis], sign * maxs[axis])
        out_min.append(min(pair))
        out_max.append(max(pair))
    return tuple(out_min), tuple(out_max)


def _contained(
    stl: Mapping[str, Any], nifti: Mapping[str, Any], tolerance: float, transform: str
) -> bool:
    mins, maxs = _transformed_bounds(stl["bounds_min"], stl["bounds_max"], transform)
    return all(
        mins[axis] >= nifti["bounds_min"][axis] - tolerance
        and maxs[axis] <= nifti["bounds_max"][axis] + tolerance
        for axis in range(3)
    )


def _selected_csv_columns(path: Path, columns: Sequence[str]) -> List[Tuple[str, ...]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"CSV is empty: {path.name}") from exc
        indices = []
        for column in columns:
            if column not in header:
                raise ValueError(f"CSV lacks required column {column}: {path.name}")
            indices.append(header.index(column))
        rows = []
        for row in reader:
            if not row or max(indices) >= len(row):
                continue
            rows.append(tuple(row[index].strip() for index in indices))
        return rows


def _is_one(value: str) -> bool:
    return value.strip() in {"1", "1.0"}


def _is_zero(value: str) -> bool:
    return value.strip() in {"0", "0.0"}


def _case_files(case_dir: Path) -> Tuple[Path, Path, Path]:
    nifti = [
        path
        for path in case_dir.iterdir()
        if path.is_file()
        and (path.name.lower().endswith(".nii") or path.name.lower().endswith(".nii.gz"))
    ]
    stls = [path for path in case_dir.iterdir() if path.is_file() and path.suffix.lower() == ".stl"]
    parent = [path for path in stls if "aneurysm_artery" in path.name.lower()]
    aneurysm = [
        path
        for path in stls
        if "aneurysm" in path.name.lower() and "aneurysm_artery" not in path.name.lower()
    ]
    if len(nifti) != 1 or len(parent) != 1 or len(aneurysm) != 1:
        raise ValueError("A lesion directory does not have exactly one required triplet")
    return nifti[0], parent[0], aneurysm[0]


def run_asset_audit(
    config: Mapping[str, Any],
    raw_root: Path,
    extracted_root: Path,
    public_source_commit: str,
) -> Dict[str, Any]:
    validate_asset_config(config)
    release = config["official_release"]
    geometry = config["geometry_contract"]
    units = config["expected_units"]

    raw_files = [path for path in raw_root.iterdir() if path.is_file()]
    observed_by_contract: Dict[str, Dict[str, Any]] = {}
    for item in release["archives"]:
        matching_size = [path for path in raw_files if path.stat().st_size == item["bytes"]]
        matches = []
        for path in matching_size:
            digest = _md5(path)
            if digest == item["md5"]:
                matches.append(path)
        observed_by_contract[item["label"]] = {
            "matching_files": len(matches),
            "bytes": item["bytes"],
            "md5_match": len(matches) == 1,
        }
    archive_ok = all(item["md5_match"] for item in observed_by_contract.values())

    stats_root = extracted_root / "statistical results"
    observed_csvs = {path.name for path in stats_root.iterdir() if path.is_file()}
    csv_ok = observed_csvs == set(release["statistical_members"])

    clinical_rows = _selected_csv_columns(stats_root / "clinical_all.csv", ("number", "Has aneurysm"))
    patient_rows = [identifier for identifier, flag in clinical_rows if identifier and _is_one(flag)]
    control_rows = [identifier for identifier, flag in clinical_rows if identifier and _is_zero(flag)]
    patient_counts = Counter(patient_rows)
    morphology_ids = [
        row[0]
        for row in _selected_csv_columns(
            stats_root / "morphological_aneurysm_artery.csv", ("number",)
        )
        if row[0]
    ]
    hemodynamic_ids = [
        row[0]
        for row in _selected_csv_columns(
            stats_root / "hemodynamic_aneurysm_artery.csv", ("number",)
        )
        if row[0]
    ]
    morphology_control_ids = [
        row[0]
        for row in _selected_csv_columns(
            stats_root / "morphological_control.csv", ("number",)
        )
        if row[0]
    ]
    hemodynamic_control_ids = [
        row[0]
        for row in _selected_csv_columns(
            stats_root / "hemodynamic_control.csv", ("number",)
        )
        if row[0]
    ]

    patients_root = extracted_root / "patients"
    controls_root = extracted_root / "controls"
    case_ids = {path.name for path in patients_root.iterdir() if path.is_dir()}
    control_case_ids = {path.name for path in controls_root.iterdir() if path.is_dir()}
    morphology_set = set(morphology_ids)
    hemodynamic_set = set(hemodynamic_ids)
    clinical_patient_set = set(patient_rows)
    morphology_control_set = set(morphology_control_ids)
    hemodynamic_control_set = set(hemodynamic_control_ids)

    counts_ok = (
        len(patient_rows) == units["lesions"]
        and len(clinical_patient_set) == units["patients"]
        and len(control_rows) == units["controls"]
        and len(morphology_ids) == units["lesions"]
        and len(hemodynamic_ids) == units["lesions"]
        and len(morphology_control_ids) == units["controls"]
        and len(hemodynamic_control_ids) == units["controls"]
        and len(case_ids) == units["lesions"]
        and len(control_case_ids) == units["controls"]
    )
    multi_ok = sum(count > 1 for count in patient_counts.values()) == units[
        "multi_lesion_patients"
    ]
    unique_lesion_ids = len(morphology_set) == len(morphology_ids) == units["lesions"]
    unique_hemodynamic_ids = len(hemodynamic_set) == len(hemodynamic_ids) == units["lesions"]
    explicit_patient_link = clinical_patient_set.issubset(morphology_set)
    exact_linkage_sets = (
        unique_lesion_ids
        and unique_hemodynamic_ids
        and morphology_set == hemodynamic_set == case_ids
        and set(control_rows) == morphology_control_set == hemodynamic_control_set == control_case_ids
        and explicit_patient_link
    )

    required_triplets = 0
    geometry_passed = 0
    affine_sources = Counter()
    frame_transforms = Counter()
    min_spacing = math.inf
    max_spacing = -math.inf
    min_stl_extent = math.inf
    max_stl_extent = -math.inf
    triplet_and_geometry_failures = 0
    if unique_lesion_ids and morphology_set == case_ids:
        for lesion_id in sorted(morphology_set):
            try:
                nifti_path, parent_path, aneurysm_path = _case_files(patients_root / lesion_id)
                required_triplets += 1
                nifti = read_nifti_header(nifti_path)
                parent = read_stl_bounds(parent_path)
                aneurysm = read_stl_bounds(aneurysm_path)
                affine_sources[nifti["affine_source"]] += 1
                min_spacing = min(min_spacing, *nifti["spacing"])
                max_spacing = max(max_spacing, *nifti["spacing"])
                min_stl_extent = min(min_stl_extent, *parent["extent"], *aneurysm["extent"])
                max_stl_extent = max(max_stl_extent, *parent["extent"], *aneurysm["extent"])
                nifti_limits = (
                    all(
                        geometry["nifti_spatial_dimension_min"] <= value <= geometry["nifti_spatial_dimension_max"]
                        for value in nifti["spatial"]
                    )
                    and all(
                        geometry["nifti_spacing_min_mm"] <= value <= geometry["nifti_spacing_max_mm"]
                        for value in nifti["spacing"]
                    )
                    and all(
                        geometry["nifti_physical_extent_min_mm"] <= value <= geometry["nifti_physical_extent_max_mm"]
                        for value in nifti["physical_extent"]
                    )
                )
                stl_limits = all(
                    geometry["stl_axis_extent_min_mm"] <= value <= geometry["stl_axis_extent_max_mm"]
                    for value in parent["extent"] + aneurysm["extent"]
                ) and all(
                    abs(value) <= geometry["stl_absolute_coordinate_max_mm"]
                    for value in parent["bounds_min"]
                    + parent["bounds_max"]
                    + aneurysm["bounds_min"]
                    + aneurysm["bounds_max"]
                )
                selected_transform = None
                for transform in geometry["allowed_frame_transforms"]:
                    if _contained(
                        parent, nifti, geometry["containment_tolerance_mm"], transform
                    ) and _contained(
                        aneurysm, nifti, geometry["containment_tolerance_mm"], transform
                    ):
                        selected_transform = transform
                        break
                if nifti_limits and stl_limits and selected_transform is not None:
                    geometry_passed += 1
                    frame_transforms[selected_transform] += 1
                else:
                    triplet_and_geometry_failures += 1
            except (OSError, ValueError, struct.error):
                triplet_and_geometry_failures += 1
    else:
        triplet_and_geometry_failures = units["lesions"]

    triplets_ok = required_triplets == units["lesions"]
    geometry_ok = geometry_passed == units["lesions"] and triplet_and_geometry_failures == 0
    checks = {
        "official_archive_size_and_md5_match": archive_ok,
        "five_statistical_csv_members_match": csv_ok,
        "patient_lesion_control_counts_match": counts_ok,
        "six_multi_lesion_patient_groups_recovered": multi_ok,
        "all_105_lesions_have_exact_identifier_linked_cta_parent_aneurysm_stl_and_aneurysm_stl": exact_linkage_sets and triplets_ok,
        "no_row_order_or_filename_similarity_only_linkage": exact_linkage_sets,
        "nifti_spacing_orientation_and_stl_units_frames_are_finite_and_plausible": geometry_ok,
        "aggregate_contains_no_identifier_private_path_image_voxel_or_field_payload": True,
        "training_gpu_outer_test_and_rupture_label_use_are_zero": True,
    }
    all_pass = all(checks.values())
    finite_summary = geometry_passed > 0
    return {
        "schema_version": "aurora.goal_oriented_s0a_asset_component.v1",
        "protocol_id": config["protocol_id"],
        "public_source_commit": public_source_commit,
        "audit_completed": True,
        "checks": checks,
        "checks_passed": sum(bool(value) for value in checks.values()),
        "checks_total": 9,
        "all_nine_pass": all_pass,
        "aggregate": {
            "archive_contracts_matching": sum(
                item["md5_match"] for item in observed_by_contract.values()
            ),
            "archive_contracts_total": 3,
            "statistical_csv_members": len(observed_csvs),
            "patient_records": len(patient_rows),
            "unique_patients": len(clinical_patient_set),
            "multi_lesion_patient_groups": sum(
                count > 1 for count in patient_counts.values()
            ),
            "control_records": len(control_rows),
            "morphology_lesion_ids": len(morphology_ids),
            "unique_morphology_lesion_ids": len(morphology_set),
            "unique_hemodynamic_lesion_ids": len(hemodynamic_set),
            "case_directories": len(case_ids),
            "required_triplets": required_triplets,
            "geometry_cases_passed": geometry_passed,
            "geometry_cases_failed": triplet_and_geometry_failures,
            "nifti_affine_source_counts": dict(sorted(affine_sources.items())),
            "accepted_frame_transform_counts": dict(sorted(frame_transforms.items())),
            "minimum_spacing_mm": min_spacing if finite_summary else None,
            "maximum_spacing_mm": max_spacing if finite_summary else None,
            "minimum_stl_axis_extent_mm": min_stl_extent if finite_summary else None,
            "maximum_stl_axis_extent_mm": max_stl_extent if finite_summary else None,
        },
        "privacy_boundary": {
            "source_identifiers_written": False,
            "private_paths_written": False,
            "image_voxels_read": False,
            "cfd_fields_read": False,
            "rupture_label_values_used": False,
            "model_access": False,
            "gpu_access": False,
            "outer_test_access": False,
        },
        "verdict": {
            "asset_component": "passed" if all_pass else "failed",
            "s0a_gate": "not_evaluated",
            "authorized_next_action": (
                "register_one_no_runtime_network_solver_preflight_v2_only"
                if all_pass
                else "close_the_current_goal_oriented_candidate_without_solver_v2_or_model"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--extracted-root", type=Path)
    parser.add_argument("--public-source-commit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = load_asset_config(args.config)
    checks = validate_asset_config(config)
    if args.validate_only:
        print(json.dumps({"status": "valid", "checks": checks}, indent=2))
        return 0
    if any(
        value is None
        for value in (
            args.raw_root,
            args.extracted_root,
            args.public_source_commit,
            args.output,
        )
    ):
        parser.error(
            "--raw-root, --extracted-root, --public-source-commit and --output "
            "are required unless --validate-only is used"
        )
    if len(args.public_source_commit) != 40 or any(
        char not in "0123456789abcdef" for char in args.public_source_commit
    ):
        raise AssetComponentProtocolError("A full lowercase public source SHA is required.")
    result = run_asset_audit(
        config,
        args.raw_root,
        args.extracted_root,
        args.public_source_commit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    partial = args.output.with_suffix(args.output.suffix + ".partial")
    partial.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(
        json.dumps(
            {
                "audit_completed": True,
                "checks_passed": result["checks_passed"],
                "checks_total": result["checks_total"],
                "all_nine_pass": result["all_nine_pass"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
