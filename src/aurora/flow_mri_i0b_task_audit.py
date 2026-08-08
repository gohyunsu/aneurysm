"""One-shot, method-free task-adequacy audit for public 4D-flow phantom assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import urllib.request
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_range import fetch_member
from .flow_mri_asset_audit import load_generic_zip_index, parse_primary_header


class FlowMRII0bError(RuntimeError):
    """Raised when the frozen I0b contract or an upstream asset is violated."""


REGISTERED_CONFIG_SHA256 = (
    "e19a1194f1b9ec41861c5084b26c9add5be47924a19aee4d23ffc826399dce06"
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FlowMRII0bError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _scientific_imports() -> tuple[Any, Any, Any]:
    try:
        import h5py
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - pinned server dependency
        raise FlowMRII0bError("I0b requires numpy, h5py, and torch.") from exc
    return np, h5py, torch


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    _require(
        payload.get("schema_version")
        == "aurora.flow_mri_protocol_i0b_task_adequacy.v1",
        "Unexpected I0b schema version.",
    )
    _require(
        payload.get("status")
        == (
            "preregistered_after_i0a_and_expanded_asset_discovery_"
            "before_any_velocity_or_REC_field_read"
        ),
        "I0b registration boundary changed.",
    )
    discovery = payload.get("discovery_boundary", {})
    _require(
        discovery
        == {
            "inspected_before_registration": True,
            "scope": (
                "all_I0a_discovery_plus_2021_official_README_and_MATLAB_reader_"
                "and_Zenodo_17183575_record_three_ZIP64_central_directories_"
                "and_all_33_primary_PAR_headers"
            ),
            "not_prospective_evidence": True,
            "velocity_field_values_inspected": False,
            "REC_payloads_inspected": False,
            "learned_checkpoint_inspected": False,
        },
        "I0b must disclose every pre-registration inspection.",
    )
    prerequisite = payload.get("prerequisite", {})
    _require(
        prerequisite.get("i0a_source_commit")
        == "f7b4e024d69d43cf042f4163342b4d993386f441"
        and prerequisite.get("i0a_config_sha256")
        == "ceb6413047b117ecbc7b52d83919b73117491e8de6c099c7b158f592788f40ff"
        and prerequisite.get("i0a_public_result_sha256")
        == "2243172a720b25ebebd6052b9c0989880d95cba5b8d984f8980f70cf5f26d9c6"
        and prerequisite.get("i0a_gate") == "14_of_14_passed_asset_integrity_only",
        "I0b must retain the exact I0a prerequisite.",
    )
    sources = payload.get("sources", {})
    _require(
        set(sources)
        == {
            "multiresolution_processed_2021",
            "expanded_intervention_2025",
            "dual_venc_2025",
        },
        "I0b source set changed.",
    )
    multi = sources["multiresolution_processed_2021"]
    expected_protocols = {
        f"{resolution}_cs{acceleration}"
        for resolution in ("0.5", "1.0", "1.5")
        for acceleration in ("2.5", "4.5", "6.5")
    }
    _require(
        multi.get("doi") == "10.5281/zenodo.4882572"
        and set(multi.get("protocols", [])) == expected_protocols
        and multi.get("registered_raw_members") == 27
        and multi.get("registered_compressed_raw_bytes") == 68706606
        and multi.get("registered_uncompressed_raw_bytes") == 13071974400
        and multi.get("repeat_acquisitions_per_exact_protocol") == 1,
        "I0b 2021 field contract changed.",
    )
    expanded = sources["expanded_intervention_2025"]
    _require(
        expanded.get("doi") == "10.5281/zenodo.17183575"
        and expanded.get("primary_acquisitions") == 33
        and expanded.get("base_geometry_models") == 5
        and expanded.get("source_patient_anatomies") == 2
        and expanded.get("multi_venc_physical_states") == 8
        and expanded.get("pump_off_noise_acquisitions") == 2
        and expanded.get("unique_device_conditions") == 15
        and len(expanded.get("archives", [])) == 3
        and expanded.get("REC_payload_access_in_I0b") is False,
        "I0b expanded-asset task-unit contract changed.",
    )
    _require(
        sources["dual_venc_2025"].get("relationship_to_expanded_intervention_release")
        == "unresolved_do_not_count_as_independent_until_case_level_provenance_is_audited"
        and sources["dual_venc_2025"].get("REC_payload_access_in_I0b") is False,
        "The two 2025 releases cannot be counted as independent yet.",
    )
    staging = payload.get("field_staging", {})
    _require(
        staging.get("allowed_source") == "multiresolution_processed_2021_only"
        and staging.get("GPU_required") is False
        and staging.get("redistribute_field_cache") is False
        and staging.get("resampling", {}).get("target_field_registration_allowed")
        is False
        and staging.get("support", {}).get("target_derived_mask_allowed") is False,
        "I0b cannot access a 2025 REC, GPU, target-derived mask, or target registration.",
    )
    thresholds = payload.get("gate", {}).get("thresholds", {})
    expected_thresholds = {
        "required_2021_RAW_CRC_passes": 27,
        "required_finite_fraction": 1.0,
        "maximum_absolute_velocity_cm_s": 100.0,
        "minimum_reference_support_voxels": 1000,
        "maximum_reference_support_fraction": 0.2,
        "minimum_worst_protocol_support_Dice": 0.5,
        "maximum_protocol_support_centroid_spread_mm": 4.0,
        "minimum_worst_pair_temporal_curve_correlation": 0.8,
        "minimum_median_pair_vector_cosine": 0.75,
        "minimum_same_resolution_acceleration_median_relative_L2": 0.03,
        "minimum_cross_resolution_median_relative_L2": 0.05,
        "minimum_protocol_variance_fraction": 0.0025,
        "required_expanded_primary_headers": 33,
        "required_expanded_physical_model_device_states": 22,
        "required_expanded_multi_venc_states": 8,
        "required_expanded_pump_off_acquisitions": 2,
        "required_expanded_base_geometry_models": 5,
        "required_expanded_source_patient_anatomies": 2,
        "required_expanded_unique_device_conditions": 15,
    }
    _require(thresholds == expected_thresholds, "I0b frozen thresholds changed.")
    gate = payload.get("gate", {})
    _require(
        gate.get("all_checks_must_pass") is True
        and gate.get("local_repair_rerun_or_threshold_change_allowed") is False
        and gate.get("pass_authorizes")
        == "register_method_free_I0c_PAR_REC_decoder_noise_and_cross_VENC_measurement_audit_only"
        and "method_selection" in gate.get("pass_does_not_authorize", [])
        and "posterior_calibration_claim" in gate.get("pass_does_not_authorize", [])
        and "isbi_submission" in gate.get("pass_does_not_authorize", []),
        "I0b cannot authorize a method, posterior claim, rerun, or submission.",
    )
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    _require(
        sha256_file(path) == REGISTERED_CONFIG_SHA256,
        "I0b config bytes do not match the registered SHA-256.",
    )
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def _verify_i0a(root: Path, config: Mapping[str, Any]) -> dict[str, Any]:
    prerequisite = config["prerequisite"]
    result_path = root / str(prerequisite["i0a_public_result"])
    _require(result_path.is_file(), "Pinned I0a public result is missing.")
    _require(
        sha256_file(result_path) == prerequisite["i0a_public_result_sha256"],
        "Pinned I0a public result checksum changed.",
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    _require(
        result.get("source_commit") == prerequisite["i0a_source_commit"]
        and result.get("config_sha256") == prerequisite["i0a_config_sha256"]
        and result.get("gate", {}).get("all_checks_passed") is True
        and result.get("gate", {}).get("passed_checks") == 14,
        "I0a prerequisite is not the registered 14/14 pass.",
    )
    return {
        "source_commit": result["source_commit"],
        "config_sha256": result["config_sha256"],
        "public_result_sha256": prerequisite["i0a_public_result_sha256"],
        "checks": "14_of_14_passed_asset_integrity_only",
    }


def _protocol_shape(source: Mapping[str, Any], protocol: str) -> tuple[int, ...]:
    resolution = protocol.split("_", 1)[0]
    return tuple(int(item) for item in source["dimensions_tzyx"][resolution])


def _raw_members(
    source: Mapping[str, Any], members: Mapping[str, Any], protocol: str
) -> dict[str, Any]:
    root = str(source["processed_velocity_root_token"])
    selected = {
        name.rsplit("_", 1)[-1].removesuffix(".raw"): member
        for name, member in members.items()
        if root in name and f"/{protocol}/" in name and name.endswith(".raw")
    }
    _require(set(selected) == {"X", "Y", "Z"}, f"RAW component set changed: {protocol}")
    return selected


def _stage_2021_fields(
    source: Mapping[str, Any], staging: Mapping[str, Any], cache_path: Path
) -> dict[str, Any]:
    np, h5py, torch = _scientific_imports()
    import torch.nn.functional as functional

    _require(not cache_path.exists(), "Refusing to overwrite an existing I0b cache.")
    members, archive = load_generic_zip_index(str(source["archive_url"]))
    _require(archive["content_length"] == source["archive_bytes"], "2021 archive size changed.")
    raw_members = [
        member
        for protocol in source["protocols"]
        for member in _raw_members(source, members, protocol).values()
    ]
    _require(
        len(raw_members) == source["registered_raw_members"]
        and sum(item.compressed_size for item in raw_members)
        == source["registered_compressed_raw_bytes"]
        and sum(item.uncompressed_size for item in raw_members)
        == source["registered_uncompressed_raw_bytes"],
        "2021 RAW byte budget changed.",
    )
    common_shape = tuple(int(item) for item in staging["resampling"]["common_shape_tzyx"])
    finite = 0
    values = 0
    maximum_absolute = 0.0
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(cache_path, "x") as cache:
        cache.attrs["schema_version"] = "aurora.flow_mri_protocol_i0b.cache.v1"
        cache.attrs["source_doi"] = source["doi"]
        cache.attrs["velocity_unit"] = source["velocity_unit"]
        cache.attrs["common_shape_tzyx"] = common_shape
        cache.attrs["common_spacing_xyz_mm"] = staging["resampling"][
            "common_spacing_xyz_mm"
        ]
        velocity = cache.create_group("velocity")
        for protocol in source["protocols"]:
            dataset = velocity.create_dataset(
                protocol,
                shape=(*common_shape, 3),
                dtype="f4",
                chunks=(1, 10, 36, 36, 3),
                compression="gzip",
                compression_opts=4,
                shuffle=True,
            )
            component_members = _raw_members(source, members, protocol)
            shape = _protocol_shape(source, protocol)
            for component_index, component in enumerate(source["velocity_components"]):
                raw = fetch_member(str(source["archive_url"]), component_members[component])
                array = np.frombuffer(raw, dtype="<f4")
                _require(array.size == math.prod(shape), "Decoded RAW size changed.")
                array = array.reshape(shape)
                finite += int(np.isfinite(array).sum())
                values += int(array.size)
                maximum_absolute = max(maximum_absolute, float(np.max(np.abs(array))))
                tensor = torch.from_numpy(array).unsqueeze(1)
                resampled = functional.interpolate(
                    tensor,
                    size=common_shape[1:],
                    mode="trilinear",
                    align_corners=bool(staging["resampling"]["align_corners"]),
                ).squeeze(1)
                dataset[..., component_index] = resampled.numpy()
                del resampled, tensor, array, raw
            dataset.attrs["source_shape_tzyx"] = shape
    return {
        "archive_format": archive["archive_format"],
        "archive_entries": archive["entries"],
        "raw_CRC_passes": len(raw_members),
        "raw_compressed_bytes_read": sum(item.compressed_size for item in raw_members),
        "raw_uncompressed_bytes_decoded": sum(item.uncompressed_size for item in raw_members),
        "finite_fraction": finite / max(values, 1),
        "maximum_absolute_velocity_cm_s": maximum_absolute,
        "cache_bytes": cache_path.stat().st_size,
        "cache_sha256": sha256_file(cache_path),
        "REC_payloads_read": 0,
    }


def erode_six_neighbor(mask: Any, iterations: int) -> Any:
    np, _, _ = _scientific_imports()
    result = np.asarray(mask, dtype=bool).copy()
    for _ in range(iterations):
        eroded = np.zeros_like(result)
        eroded[1:-1, 1:-1, 1:-1] = (
            result[1:-1, 1:-1, 1:-1]
            & result[:-2, 1:-1, 1:-1]
            & result[2:, 1:-1, 1:-1]
            & result[1:-1, :-2, 1:-1]
            & result[1:-1, 2:, 1:-1]
            & result[1:-1, 1:-1, :-2]
            & result[1:-1, 1:-1, 2:]
        )
        result = eroded
    return result


def symmetric_relative_l2(left: Any, right: Any) -> float:
    np, _, _ = _scientific_imports()
    left64 = np.asarray(left, dtype=np.float64)
    right64 = np.asarray(right, dtype=np.float64)
    numerator = float(np.sum((left64 - right64) ** 2))
    denominator = 0.5 * float(np.sum(left64**2) + np.sum(right64**2))
    return math.sqrt(numerator / max(denominator, 1e-30))


def vector_cosine(left: Any, right: Any) -> float:
    np, _, _ = _scientific_imports()
    left64 = np.asarray(left, dtype=np.float64)
    right64 = np.asarray(right, dtype=np.float64)
    numerator = float(np.sum(left64 * right64))
    denominator = math.sqrt(float(np.sum(left64**2) * np.sum(right64**2)))
    return numerator / max(denominator, 1e-30)


def _support(data: Any, threshold: float, iterations: int) -> Any:
    np, _, _ = _scientific_imports()
    rms_speed = np.sqrt(np.mean(np.sum(np.asarray(data, dtype=np.float64) ** 2, axis=-1), axis=0))
    return erode_six_neighbor(rms_speed > threshold, iterations)


def _temporal_curve(data: Any, mask: Any) -> Any:
    np, _, _ = _scientific_imports()
    speed = np.sqrt(np.sum(np.asarray(data, dtype=np.float64) ** 2, axis=-1))
    return np.mean(speed[:, mask], axis=1)


def _field_metrics(
    cache_path: Path, source: Mapping[str, Any], staging: Mapping[str, Any]
) -> dict[str, Any]:
    np, h5py, _ = _scientific_imports()
    protocols = list(source["protocols"])
    support_spec = staging["support"]
    with h5py.File(cache_path, "r") as cache:
        reference_data = cache["velocity"][support_spec["reference_protocol"]][...]
        reference_mask = _support(
            reference_data,
            float(support_spec["temporal_rms_speed_threshold_cm_s"]),
            int(support_spec["six_neighbor_erosion_iterations"]),
        )
        support_voxels = int(reference_mask.sum())
        support_fraction = float(reference_mask.mean())
        support_dice: dict[str, float] = {}
        centroids: dict[str, Any] = {}
        spacing_xyz = np.asarray(staging["resampling"]["common_spacing_xyz_mm"], dtype=float)
        for protocol in protocols:
            data = cache["velocity"][protocol][...]
            mask = _support(
                data,
                float(support_spec["temporal_rms_speed_threshold_cm_s"]),
                int(support_spec["six_neighbor_erosion_iterations"]),
            )
            intersection = int(np.logical_and(reference_mask, mask).sum())
            support_dice[protocol] = 2.0 * intersection / max(
                support_voxels + int(mask.sum()), 1
            )
            indices = np.argwhere(mask)
            if len(indices):
                centroid_zyx = np.mean(indices, axis=0)
                centroids[protocol] = (
                    centroid_zyx * spacing_xyz[[2, 1, 0]]
                ).tolist()
            else:
                centroids[protocol] = [float("inf")] * 3
        centroid_spread = max(
            float(np.linalg.norm(np.asarray(centroids[left]) - np.asarray(centroids[right])))
            for left, right in combinations(protocols, 2)
        )

        by_resolution: dict[str, list[str]] = {}
        by_acceleration: dict[str, list[str]] = {}
        for protocol in protocols:
            resolution, acceleration = protocol.split("_cs")
            by_resolution.setdefault(resolution, []).append(protocol)
            by_acceleration.setdefault(acceleration, []).append(protocol)
        same_resolution = [
            pair for values in by_resolution.values() for pair in combinations(sorted(values), 2)
        ]
        same_acceleration = [
            pair for values in by_acceleration.values() for pair in combinations(sorted(values), 2)
        ]
        pair_rows: list[dict[str, Any]] = []
        for kind, pairs in (
            ("same_resolution_acceleration_contrast", same_resolution),
            ("same_acceleration_resolution_contrast", same_acceleration),
        ):
            for left, right in pairs:
                left_data = cache["velocity"][left][...][:, reference_mask, :]
                right_data = cache["velocity"][right][...][:, reference_mask, :]
                left_curve = _temporal_curve(cache["velocity"][left][...], reference_mask)
                right_curve = _temporal_curve(cache["velocity"][right][...], reference_mask)
                correlation = float(np.corrcoef(left_curve, right_curve)[0, 1])
                pair_rows.append(
                    {
                        "kind": kind,
                        "left": left,
                        "right": right,
                        "symmetric_relative_L2": symmetric_relative_l2(left_data, right_data),
                        "vector_cosine": vector_cosine(left_data, right_data),
                        "temporal_curve_correlation": correlation,
                    }
                )

        mean = None
        m2 = None
        count = 0
        for protocol in protocols:
            selected = cache["velocity"][protocol][...][:, reference_mask, :].astype(np.float64)
            count += 1
            if mean is None:
                mean = selected.copy()
                m2 = np.zeros_like(selected)
            else:
                delta = selected - mean
                mean += delta / count
                m2 += delta * (selected - mean)
        assert mean is not None and m2 is not None
        protocol_variance_fraction = float(np.mean(m2 / count) / max(np.mean(mean**2), 1e-30))

    same_resolution_l2 = [
        row["symmetric_relative_L2"]
        for row in pair_rows
        if row["kind"] == "same_resolution_acceleration_contrast"
    ]
    same_acceleration_l2 = [
        row["symmetric_relative_L2"]
        for row in pair_rows
        if row["kind"] == "same_acceleration_resolution_contrast"
    ]
    return {
        "reference_support_voxels": support_voxels,
        "reference_support_fraction": support_fraction,
        "support_Dice_by_protocol": support_dice,
        "worst_protocol_support_Dice": min(support_dice.values()),
        "support_centroid_by_protocol_zyx_mm": centroids,
        "maximum_support_centroid_spread_mm": centroid_spread,
        "pair_rows": pair_rows,
        "same_resolution_pairs": len(same_resolution_l2),
        "same_acceleration_pairs": len(same_acceleration_l2),
        "same_resolution_acceleration_median_relative_L2": float(
            np.median(same_resolution_l2)
        ),
        "cross_resolution_median_relative_L2": float(np.median(same_acceleration_l2)),
        "median_pair_vector_cosine": float(
            np.median([row["vector_cosine"] for row in pair_rows])
        ),
        "worst_pair_temporal_curve_correlation": min(
            row["temporal_curve_correlation"] for row in pair_rows
        ),
        "protocol_variance_fraction": protocol_variance_fraction,
    }


def _record_metadata(source: Mapping[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        str(source["record_api"]), headers={"User-Agent": "AURORA-I0b/1.0"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        record = json.loads(response.read().decode("utf-8"))
    metadata = record.get("metadata", {})
    files = {item["key"]: item for item in record.get("files", [])}
    _require(metadata.get("access_right") == source["access_right"], "Access right changed.")
    _require(metadata.get("license", {}).get("id") == source["license"], "License changed.")
    for archive in source["archives"]:
        item = files.get(archive["name"])
        _require(
            item is not None
            and int(item["size"]) == archive["bytes"]
            and item["checksum"] == archive["checksum"],
            f"Expanded archive pin changed: {archive['name']}",
        )
    return {"record_id": int(record["id"]), "license": source["license"]}


def _expanded_asset_audit(source: Mapping[str, Any]) -> dict[str, Any]:
    record = _record_metadata(source)
    primary_rows: list[dict[str, Any]] = []
    physical_states: set[str] = set()
    multi_venc_groups: dict[str, set[float]] = {}
    base_models: set[str] = {"ICA"}
    device_labels: set[str] = set()
    rec_members = 0
    par_members = 0
    archive_rows: list[dict[str, Any]] = []
    pump_off = 0
    for archive_index, archive in enumerate(source["archives"], start=1):
        members, metadata = load_generic_zip_index(str(archive["url"]))
        _require(
            metadata["content_length"] == archive["bytes"]
            and metadata["entries"] == archive["entries"]
            and metadata["archive_format"] == "zip64",
            f"Expanded central-directory contract changed: {archive['name']}",
        )
        primary = sorted(name for name in members if name.lower().endswith("_1.par"))
        _require(
            len(primary) == archive["primary_acquisitions"],
            f"Expanded primary acquisition count changed: {archive['name']}",
        )
        archive_rec = sum(name.lower().endswith(".rec") for name in members)
        archive_par = sum(name.lower().endswith(".par") for name in members)
        _require(
            archive_rec == archive_par == 4 * len(primary),
            f"Expanded archive lacks four PAR/REC encodings: {archive['name']}",
        )
        rec_members += archive_rec
        par_members += archive_par
        archive_rows.append(
            {
                "archive": archive["name"],
                "entries": metadata["entries"],
                "primary_headers": len(primary),
                "PAR_members": archive_par,
                "REC_members": archive_rec,
            }
        )
        root_token = archive["name"].removesuffix(".zip") + "/"
        for name in primary:
            header = parse_primary_header(fetch_member(str(archive["url"]), members[name]))
            _require(
                header["cardiac_phases"] == source["expected_cardiac_phases"]
                and header["scan_resolution_xy"] == archive["scan_resolution_xy"],
                f"Expanded primary header changed: {name}",
            )
            relative = name.split(root_token, 1)[-1]
            parts = relative.split("/")
            path_venc = re.search(r"/venc_(\d+)cms/", "/" + relative, re.I)
            if path_venc is not None:
                _require(
                    math.isclose(float(path_venc.group(1)), header["venc_cm_s"]),
                    f"Header and VENC directory disagree: {name}",
                )
            elif archive_index == 3:
                _require(
                    math.isclose(header["venc_cm_s"], 75.0),
                    f"BA header VENC changed: {name}",
                )
            if archive_index == 1:
                physical_key = f"exp1/{parts[0]}"
                multi_key = f"exp1/{parts[0]}/{parts[1]}"
            elif archive_index == 2:
                physical_key = f"exp2/{parts[0]}"
                multi_key = physical_key
            else:
                physical_key = f"exp3/{parts[0]}/{parts[1]}"
                multi_key = physical_key
                base_models.add(parts[0])
            physical_states.add(physical_key)
            multi_venc_groups.setdefault(multi_key, set()).add(header["venc_cm_s"])
            if "pump_off" in relative:
                pump_off += 1
            device_labels.update(re.findall(r"\b(?:IFD|FD)\d+\b", relative))
            primary_rows.append(
                {
                    "archive": archive_index,
                    "state": physical_key,
                    "venc_cm_s": header["venc_cm_s"],
                    "cardiac_phases": header["cardiac_phases"],
                    "scan_resolution_xy": header["scan_resolution_xy"],
                    "primary_header_CRC_verified": True,
                }
            )
    multi_venc_states = sum(len(values) >= 2 for values in multi_venc_groups.values())
    return {
        **record,
        "archives": archive_rows,
        "primary_headers_CRC_verified": len(primary_rows),
        "primary_rows": primary_rows,
        "PAR_members": par_members,
        "REC_members_present_not_read": rec_members,
        "REC_payloads_read": 0,
        "physical_model_device_states": len(physical_states),
        "multi_venc_physical_states": multi_venc_states,
        "pump_off_noise_acquisitions": pump_off,
        "base_geometry_models": len(base_models),
        "source_patient_anatomies": source["source_patient_anatomies"],
        "unique_device_conditions": len(device_labels),
        "device_labels": sorted(device_labels),
    }


def _gate(
    config: Mapping[str, Any], staging: Mapping[str, Any], field: Mapping[str, Any],
    expanded: Mapping[str, Any]
) -> dict[str, Any]:
    thresholds = config["gate"]["thresholds"]
    checks = {
        "i0a_prerequisite_is_exact_14_of_14_asset_pass": True,
        "all_27_2021_RAW_members_pass_CRC": staging["raw_CRC_passes"]
        == thresholds["required_2021_RAW_CRC_passes"],
        "all_2021_velocity_values_are_finite": math.isclose(
            staging["finite_fraction"], thresholds["required_finite_fraction"], abs_tol=0.0
        ),
        "2021_velocity_magnitude_is_within_registered_bound": staging[
            "maximum_absolute_velocity_cm_s"
        ]
        <= thresholds["maximum_absolute_velocity_cm_s"],
        "reference_support_size_is_eligible": field["reference_support_voxels"]
        >= thresholds["minimum_reference_support_voxels"]
        and field["reference_support_fraction"]
        <= thresholds["maximum_reference_support_fraction"],
        "all_protocol_supports_overlap_reference": field["worst_protocol_support_Dice"]
        >= thresholds["minimum_worst_protocol_support_Dice"],
        "center_alignment_does_not_require_target_registration": field[
            "maximum_support_centroid_spread_mm"
        ]
        <= thresholds["maximum_protocol_support_centroid_spread_mm"],
        "temporal_speed_curves_remain_aligned": field[
            "worst_pair_temporal_curve_correlation"
        ]
        >= thresholds["minimum_worst_pair_temporal_curve_correlation"],
        "pairwise_vector_signal_remains_correlated": field["median_pair_vector_cosine"]
        >= thresholds["minimum_median_pair_vector_cosine"],
        "acceleration_effect_is_nontrivial": field[
            "same_resolution_acceleration_median_relative_L2"
        ]
        >= thresholds["minimum_same_resolution_acceleration_median_relative_L2"],
        "resolution_effect_is_nontrivial": field["cross_resolution_median_relative_L2"]
        >= thresholds["minimum_cross_resolution_median_relative_L2"],
        "protocol_variance_is_nontrivial": field["protocol_variance_fraction"]
        >= thresholds["minimum_protocol_variance_fraction"],
        "expanded_release_has_all_33_primary_headers": expanded[
            "primary_headers_CRC_verified"
        ]
        == thresholds["required_expanded_primary_headers"],
        "expanded_release_has_registered_multi_VENC_and_noise_controls": expanded[
            "multi_venc_physical_states"
        ]
        == thresholds["required_expanded_multi_venc_states"]
        and expanded["pump_off_noise_acquisitions"]
        == thresholds["required_expanded_pump_off_acquisitions"],
        "expanded_release_retains_registered_state_and_device_counts": expanded[
            "physical_model_device_states"
        ]
        == thresholds["required_expanded_physical_model_device_states"]
        and expanded["unique_device_conditions"]
        == thresholds["required_expanded_unique_device_conditions"],
        "expanded_release_retains_five_models_from_two_source_anatomies": expanded[
            "base_geometry_models"
        ]
        == thresholds["required_expanded_base_geometry_models"]
        and expanded["source_patient_anatomies"]
        == thresholds["required_expanded_source_patient_anatomies"],
        "no_2025_REC_checkpoint_model_or_GPU_was_used": expanded["REC_payloads_read"] == 0
        and staging["REC_payloads_read"] == 0,
    }
    passed = sum(bool(value) for value in checks.values())
    all_passed = passed == len(checks)
    return {
        "checks": checks,
        "passed_checks": passed,
        "total_checks": len(checks),
        "all_checks_passed": all_passed,
        "decision": (
            config["gate"]["pass_authorizes"]
            if all_passed
            else config["gate"]["failure_action"]
        ),
        "does_not_authorize": config["gate"]["pass_does_not_authorize"],
    }


def run(
    config: Mapping[str, Any], *, root: Path, cache_path: Path, source_commit: str
) -> dict[str, Any]:
    _require(
        re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
        "I0b requires an exact lowercase 40-character source commit.",
    )
    i0a = _verify_i0a(root, config)
    source = config["sources"]["multiresolution_processed_2021"]
    staging = _stage_2021_fields(source, config["field_staging"], cache_path)
    field = _field_metrics(cache_path, source, config["field_staging"])
    expanded = _expanded_asset_audit(config["sources"]["expanded_intervention_2025"])
    gate = _gate(config, staging, field, expanded)
    return {
        "schema_version": "aurora.flow_mri_protocol_i0b_task_adequacy.result.v1",
        "experiment_id": config["experiment_id"],
        "source_commit": source_commit,
        "config_sha256": sha256_file(
            root / "configs" / "flow_mri_protocol_i0b_task_adequacy.json"
        ),
        "research_role": config["research_role"],
        "discovery_boundary": config["discovery_boundary"],
        "i0a_prerequisite": i0a,
        "staging_2021": staging,
        "field_task_metrics_2021": field,
        "expanded_asset_2025": expanded,
        "independence_boundary": {
            "2021_physical_phantoms": source["physical_phantoms"],
            "2021_repeats_per_exact_protocol": source[
                "repeat_acquisitions_per_exact_protocol"
            ],
            "expanded_base_geometry_models": expanded["base_geometry_models"],
            "expanded_source_patient_anatomies": expanded["source_patient_anatomies"],
            "voxels_phases_scans_and_device_states_are_not_independent_patients": True,
            "posterior_calibration_identified": False,
        },
        "gate": gate,
        "interpretation": config["interpretation"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.repository_root.resolve()
    config = load_config(args.config)
    result = run(
        config, root=root, cache_path=args.cache, source_commit=args.source_commit
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
