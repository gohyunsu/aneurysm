"""Method-free raw surface-WSS structure P0 for AneuG-Flow.

The audit deliberately stops before model construction. It downloads three
exact public schema probes, verifies their tensor/mesh contract, and asks only
whether indexed critical points can be extracted from a tangent surface vector
field. Raw payloads remain in PBS job-local temporary storage.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence


class AneuGSurfaceVectorP0Error(RuntimeError):
    """Raised when the frozen P0 cannot be executed as registered."""


_FULL_SHA = re.compile(r"[0-9a-f]{40}")
_REQUIRED_KEYS = (
    "x_coordinate",
    "y_coordinate",
    "z_coordinate",
    "x_wall_shear",
    "y_wall_shear",
    "z_wall_shear",
)


def _canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneug_surface_vector_structure_p0.v1":
        raise AneuGSurfaceVectorP0Error("Unexpected P0 schema version.")
    if payload.get("protocol_id") != "aneug_surface_vector_structure_raw_probe_p0_v1":
        raise AneuGSurfaceVectorP0Error("Unexpected P0 protocol id.")
    if payload.get("status") != "preregistered_before_first_introai9_pbs_execution":
        raise AneuGSurfaceVectorP0Error("P0 must remain prospective.")

    candidate = payload["candidate"]
    if (
        candidate["id"] != "time_varying_surface_wss_index_structure_prediction"
        or float(candidate["score"]) != 32.0
        or float(candidate["admission_threshold"]) != 32.0
        or sum(float(value) for value in candidate["axis_scores"]) != 32.0
        or any(
            candidate[key] is not False
            for key in (
                "method_selected",
                "architecture_selected",
                "gpu_training_authorized",
                "outer_test_authorized",
                "submission_identity_active",
            )
        )
    ):
        raise AneuGSurfaceVectorP0Error("Frozen candidate contract changed.")

    sources = payload["sources"]
    if (
        sources["dataset_commit"]
        != "9dd418083899deddd93a67f9a6fca7a14304fa36"
        or sources["official_code_commit"]
        != "4a090a0f12538deef6fcea88b81afe78ce38152e"
        or sources["dataset_license"] != "CC-BY-SA-4.0"
        or int(sources["reported_transient_cases"]) != 730
    ):
        raise AneuGSurfaceVectorP0Error("Pinned source contract changed.")
    cases = sources["cases"]
    expected_cases = {
        "stable_0": (
            79495962,
            "895652c006f6eef53710486936950b80fb8015abac63e6a6f08c7de0b320fef1",
            5844998,
            "d4936fd72def5ff287775295ea8f47bd1298d21f",
        ),
        "stable_100": (
            98007322,
            "4478d67df4fd50b627739c7aa1b680183db80fdf383e2c779ce6ae03010d7c5c",
            8469495,
            "1c1b482e4df377f32f6fc0e2e1933bef91866ebd",
        ),
        "stable_10001": (
            78676122,
            "8138124a8b37907df6efc226339431764d45ef9df2fbc773c336ad13c3bee77e",
            6148786,
            "4f4a3092f4eabf0db4cb1e954446b43408622cf3",
        ),
    }
    observed_cases = {
        row["id"]: (
            int(row["wall_bytes"]),
            row["wall_sha256"],
            int(row["mesh_bytes"]),
            row["mesh_git_blob_oid"],
        )
        for row in cases
    }
    if observed_cases != expected_cases:
        raise AneuGSurfaceVectorP0Error("Probe files, sizes, or hashes changed.")
    if payload["access"]["required_tensor_keys"] != list(_REQUIRED_KEYS):
        raise AneuGSurfaceVectorP0Error("Required WSS tensor keys changed.")
    if int(payload["access"]["maximum_total_download_bytes"]) != 276642685:
        raise AneuGSurfaceVectorP0Error("Download budget changed.")
    if any(
        payload["access"][key] is not False
        for key in (
            "blood_data_access",
            "checkpoint_access",
            "processed_archive_access",
            "model_weight_access",
            "patient_data_access",
            "outer_test_access",
        )
    ):
        raise AneuGSurfaceVectorP0Error("Access boundary changed.")

    transport = payload["transport"]
    if (
        transport["attempt_delays_seconds"] != [0, 10, 30]
        or int(transport["timeout_seconds_per_attempt"]) != 900
        or int(transport["chunk_bytes"]) != 1048576
    ):
        raise AneuGSurfaceVectorP0Error("Transport budget changed.")
    execution = payload["execution"]
    if (
        execution["server"] != "introai9"
        or execution["excluded_server"] != "junjinyong"
        or execution["queue"] != "coss_agpu"
        or int(execution["ncpus"]) != 4
        or int(execution["memory_gb"]) != 16
        or int(execution["ngpus"]) != 0
        or int(execution["maximum_submissions_for_exact_public_source"]) != 1
        or execution["same_contract_repair_or_rerun_allowed"] is not False
        or execution["login_node_gpu_command_allowed"] is not False
    ):
        raise AneuGSurfaceVectorP0Error("Execution boundary changed.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validated = validate_config(payload)
    validated["_config_sha256"] = _canonical_hash(payload)
    return validated


def _sha256_file(path: Path, chunk_bytes: int = 1048576) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_bytes)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob_oid(path: Path, chunk_bytes: int = 1048576) -> str:
    digest = hashlib.sha1()
    digest.update(f"blob {path.stat().st_size}\0".encode("ascii"))
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(chunk_bytes)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _download_file(
    url: str,
    destination: Path,
    *,
    expected_bytes: int,
    delays: Sequence[int],
    timeout: int,
    chunk_bytes: int,
    user_agent: str,
) -> None:
    last_error: BaseException | None = None
    for delay in delays:
        if delay:
            time.sleep(delay)
        destination.unlink(missing_ok=True)
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})
        try:
            observed = 0
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with destination.open("xb") as output:
                    while True:
                        chunk = response.read(chunk_bytes)
                        if not chunk:
                            break
                        observed += len(chunk)
                        if observed > expected_bytes:
                            raise AneuGSurfaceVectorP0Error(
                                f"Registered object exceeds byte cap: {url}"
                            )
                        output.write(chunk)
            if observed != expected_bytes:
                raise AneuGSurfaceVectorP0Error(
                    f"Registered object byte mismatch: expected {expected_bytes}, got {observed}"
                )
            return
        except (
            OSError,
            urllib.error.URLError,
            urllib.error.HTTPError,
            AneuGSurfaceVectorP0Error,
        ) as exc:
            last_error = exc
    destination.unlink(missing_ok=True)
    raise AneuGSurfaceVectorP0Error(
        f"Transport attempts exhausted for registered object: {url}"
    ) from last_error


def _import_torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - execution environment boundary
        raise AneuGSurfaceVectorP0Error("Pinned runtime has no PyTorch.") from exc
    return torch


def _load_obj(path: Path):
    torch = _import_torch()
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    with path.open("r", encoding="utf-8", errors="strict") as stream:
        for line in stream:
            if line.startswith("v "):
                fields = line.split()
                if len(fields) < 4:
                    raise AneuGSurfaceVectorP0Error("Invalid OBJ vertex row.")
                vertices.append([float(fields[1]), float(fields[2]), float(fields[3])])
            elif line.startswith("f "):
                tokens = line.split()[1:]
                indices = [int(token.split("/", maxsplit=1)[0]) - 1 for token in tokens]
                if len(indices) < 3:
                    raise AneuGSurfaceVectorP0Error("Invalid OBJ face row.")
                for offset in range(1, len(indices) - 1):
                    faces.append([indices[0], indices[offset], indices[offset + 1]])
    if not vertices or not faces:
        raise AneuGSurfaceVectorP0Error("OBJ has no triangular surface.")
    vertex_tensor = torch.tensor(vertices, dtype=torch.float64)
    face_tensor = torch.tensor(faces, dtype=torch.long)
    if int(face_tensor.min()) < 0 or int(face_tensor.max()) >= len(vertices):
        raise AneuGSurfaceVectorP0Error("OBJ face index is out of range.")
    return vertex_tensor, face_tensor


def _component_2d(value, key: str):
    torch = _import_torch()
    if not torch.is_tensor(value):
        raise AneuGSurfaceVectorP0Error(f"{key} is not a tensor.")
    tensor = value.detach().cpu()
    if tensor.ndim == 3 and tensor.shape[-1] == 1:
        tensor = tensor[..., 0]
    if tensor.ndim != 2:
        raise AneuGSurfaceVectorP0Error(f"{key} must have shape [T,N] or [T,N,1].")
    return tensor.to(dtype=torch.float64)


def _load_wall(path: Path, phases_used: int):
    torch = _import_torch()
    try:
        payload = torch.load(path, map_location="cpu", weights_only=True)
    except Exception as exc:  # pragma: no cover - exact upstream payload dependent
        raise AneuGSurfaceVectorP0Error("weights_only wall tensor load failed.") from exc
    if not isinstance(payload, Mapping):
        raise AneuGSurfaceVectorP0Error("wall_data.pt is not a tensor mapping.")
    missing = [key for key in _REQUIRED_KEYS if key not in payload]
    if missing:
        raise AneuGSurfaceVectorP0Error(
            "wall_data.pt is missing required keys: " + ", ".join(missing)
        )
    components = [_component_2d(payload[key], key) for key in _REQUIRED_KEYS]
    shapes = {tuple(component.shape) for component in components}
    if len(shapes) != 1:
        raise AneuGSurfaceVectorP0Error("Coordinate and WSS component shapes differ.")
    source_phases, nodes = components[0].shape
    if source_phases < phases_used or nodes < 3:
        raise AneuGSurfaceVectorP0Error("Insufficient phases or wall nodes.")
    components = [component[-phases_used:] for component in components]
    xyz = torch.stack(components[:3], dim=-1)
    wss = torch.stack(components[3:], dim=-1)
    return xyz, wss, int(source_phases), sorted(str(key) for key in payload.keys())


def _vertex_normals(vertices, faces):
    torch = _import_torch()
    p0, p1, p2 = (vertices[faces[:, index]] for index in range(3))
    face_cross = torch.cross(p1 - p0, p2 - p0, dim=-1)
    face_area2 = torch.linalg.vector_norm(face_cross, dim=-1)
    normals = torch.zeros_like(vertices)
    for index in range(3):
        normals.index_add_(0, faces[:, index], face_cross)
    lengths = torch.linalg.vector_norm(normals, dim=-1)
    valid = lengths > 0
    normals[valid] = normals[valid] / lengths[valid, None]
    return normals, face_area2, valid


def _spatial_vertex_map(data_vertices, mesh_vertices, tolerance: float):
    torch = _import_torch()
    if data_vertices.shape[0] != mesh_vertices.shape[0]:
        return torch.full((data_vertices.shape[0],), -1, dtype=torch.long), 0.0, -1.0
    direct_distance = torch.linalg.vector_norm(data_vertices - mesh_vertices, dim=-1)
    if float(direct_distance.max()) <= tolerance:
        mapping = torch.arange(data_vertices.shape[0], dtype=torch.long)
        return mapping, 1.0, float(direct_distance.max())

    def key(point) -> tuple[int, int, int]:
        return tuple(int(round(float(value) / tolerance)) for value in point)

    buckets: dict[tuple[int, int, int], list[int]] = {}
    for index, point in enumerate(mesh_vertices.tolist()):
        buckets.setdefault(key(point), []).append(index)
    mapping = torch.full((data_vertices.shape[0],), -1, dtype=torch.long)
    used: set[int] = set()
    maximum_distance = 0.0
    offsets = tuple(itertools.product((-1, 0, 1), repeat=3))
    for data_index, point in enumerate(data_vertices.tolist()):
        base = key(point)
        best_index = -1
        best_distance = math.inf
        for offset in offsets:
            for mesh_index in buckets.get(
                (base[0] + offset[0], base[1] + offset[1], base[2] + offset[2]),
                (),
            ):
                if mesh_index in used:
                    continue
                distance = math.dist(point, mesh_vertices[mesh_index].tolist())
                if distance < best_distance:
                    best_distance = distance
                    best_index = mesh_index
        if best_index >= 0 and best_distance <= tolerance:
            mapping[data_index] = best_index
            used.add(best_index)
            maximum_distance = max(maximum_distance, best_distance)
    fraction = float((mapping >= 0).to(torch.float64).mean())
    return mapping, fraction, maximum_distance


def _critical_counts(
    vertices,
    faces,
    wss_mesh,
    *,
    barycentric_margin: float,
    determinant_relative_floor: float,
) -> tuple[list[int], list[int]]:
    torch = _import_torch()
    p0, p1, p2 = (vertices[faces[:, index]] for index in range(3))
    e1_raw = p1 - p0
    e1_norm = torch.linalg.vector_norm(e1_raw, dim=-1)
    face_normal_raw = torch.cross(e1_raw, p2 - p0, dim=-1)
    face_normal_norm = torch.linalg.vector_norm(face_normal_raw, dim=-1)
    valid_face = (e1_norm > 0) & (face_normal_norm > 0)
    e1 = e1_raw / e1_norm.clamp_min(1e-30)[:, None]
    face_normal = face_normal_raw / face_normal_norm.clamp_min(1e-30)[:, None]
    e2 = torch.cross(face_normal, e1, dim=-1)
    nonzero_wss = torch.linalg.vector_norm(wss_mesh, dim=-1)
    scale = float(nonzero_wss[nonzero_wss > 0].median()) if bool((nonzero_wss > 0).any()) else 0.0
    determinant_floor = max(1e-30, determinant_relative_floor * scale * scale)
    counts: list[int] = []
    signed_counts: list[int] = []
    for frame in wss_mesh:
        vectors = frame[faces]
        ux = (vectors * e1[:, None, :]).sum(dim=-1)
        uy = (vectors * e2[:, None, :]).sum(dim=-1)
        a00 = ux[:, 0] - ux[:, 2]
        a01 = ux[:, 1] - ux[:, 2]
        a10 = uy[:, 0] - uy[:, 2]
        a11 = uy[:, 1] - uy[:, 2]
        determinant = a00 * a11 - a01 * a10
        stable = valid_face & (determinant.abs() > determinant_floor)
        denominator = torch.where(stable, determinant, torch.ones_like(determinant))
        lambda0 = (-ux[:, 2] * a11 + a01 * uy[:, 2]) / denominator
        lambda1 = (-a00 * uy[:, 2] + ux[:, 2] * a10) / denominator
        lambda2 = 1.0 - lambda0 - lambda1
        inside = (
            stable
            & (lambda0 > barycentric_margin)
            & (lambda1 > barycentric_margin)
            & (lambda2 > barycentric_margin)
        )
        counts.append(int(inside.sum()))
        signed_counts.append(int(torch.sign(determinant[inside]).sum()))
    return counts, signed_counts


def analyse_case(wall_path: Path, mesh_path: Path, config: Mapping[str, Any]) -> dict[str, Any]:
    torch = _import_torch()
    phases_used = int(config["access"]["phases_used"])
    xyz, wss, source_phases, payload_keys = _load_wall(wall_path, phases_used)
    vertices, faces = _load_obj(mesh_path)
    finite = bool(torch.isfinite(xyz).all() and torch.isfinite(wss).all())
    coordinate_static_max_abs = float((xyz - xyz[:1]).abs().max())
    data_vertices = xyz[0]
    bbox_diagonal = float(
        torch.linalg.vector_norm(data_vertices.max(dim=0).values - data_vertices.min(dim=0).values)
    )
    tolerance = max(
        1e-12,
        bbox_diagonal
        * float(config["gate"]["mesh_coordinate_tolerance_fraction_of_bbox_diagonal"]),
    )
    mapping, match_fraction, maximum_match_distance = _spatial_vertex_map(
        data_vertices, vertices, tolerance
    )
    normals, face_area2, valid_normal = _vertex_normals(vertices, faces)
    mesh_valid = bool(
        vertices.shape[0] >= 3
        and faces.shape[0] >= 1
        and torch.isfinite(vertices).all()
        and (face_area2 > 0).all()
        and valid_normal.all()
    )
    complete_mapping = bool((mapping >= 0).all())
    if complete_mapping:
        wss_mesh = torch.zeros(
            (phases_used, vertices.shape[0], 3), dtype=torch.float64
        )
        wss_mesh[:, mapping, :] = wss
        magnitude = torch.linalg.vector_norm(wss_mesh, dim=-1)
        nonzero = magnitude > 0
        normal_ratio = torch.zeros_like(magnitude)
        normal_ratio[nonzero] = (
            (wss_mesh * normals[None, :, :]).sum(dim=-1).abs()[nonzero]
            / magnitude[nonzero]
        )
        valid_ratios = normal_ratio[nonzero]
        median_ratio = float(valid_ratios.median()) if valid_ratios.numel() else math.inf
        p95_ratio = (
            float(torch.quantile(valid_ratios, 0.95)) if valid_ratios.numel() else math.inf
        )
        temporal_variation = float(
            torch.linalg.vector_norm(wss_mesh - wss_mesh.mean(dim=0, keepdim=True), dim=-1).mean()
            / magnitude.mean().clamp_min(1e-30)
        )
        critical_counts, signed_counts = _critical_counts(
            vertices,
            faces,
            wss_mesh,
            barycentric_margin=float(config["gate"]["critical_barycentric_interior_margin"]),
            determinant_relative_floor=float(
                config["gate"]["critical_determinant_relative_floor"]
            ),
        )
        nonempty_fraction = sum(value > 0 for value in critical_counts) / len(critical_counts)
    else:
        median_ratio = 1.0
        p95_ratio = 1.0
        temporal_variation = 0.0
        critical_counts = []
        signed_counts = []
        nonempty_fraction = 0.0

    return {
        "source_phases": source_phases,
        "phases_used": phases_used,
        "wall_nodes": int(xyz.shape[1]),
        "mesh_vertices": int(vertices.shape[0]),
        "mesh_faces": int(faces.shape[0]),
        "payload_key_count": len(payload_keys),
        "all_required_keys_present": all(key in payload_keys for key in _REQUIRED_KEYS),
        "finite": finite,
        "coordinate_static_max_abs": coordinate_static_max_abs,
        "mesh_valid": mesh_valid,
        "mesh_coordinate_match_fraction": match_fraction,
        "mesh_coordinate_maximum_match_distance": maximum_match_distance,
        "mesh_coordinate_tolerance": tolerance,
        "median_normal_component_ratio": median_ratio,
        "p95_normal_component_ratio": p95_ratio,
        "relative_temporal_variation": temporal_variation,
        "critical_nonempty_frame_fraction": nonempty_fraction,
        "critical_count_min": min(critical_counts) if critical_counts else 0,
        "critical_count_median": (
            float(torch.tensor(critical_counts, dtype=torch.float64).median())
            if critical_counts
            else 0.0
        ),
        "critical_count_max": max(critical_counts) if critical_counts else 0,
        "signed_index_count_min": min(signed_counts) if signed_counts else 0,
        "signed_index_count_max": max(signed_counts) if signed_counts else 0,
    }


def _median(values: Sequence[float]) -> float:
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return 0.5 * (ordered[middle - 1] + ordered[middle])


def run_p0(
    config: Mapping[str, Any], *, work_dir: Path, public_source_commit: str
) -> dict[str, Any]:
    if not _FULL_SHA.fullmatch(public_source_commit):
        raise AneuGSurfaceVectorP0Error("Public source commit must be a full SHA.")
    work_dir.mkdir(parents=True, exist_ok=True)
    transport = config["transport"]
    base_url = str(transport["base_resolve_url"])
    case_results: list[dict[str, Any]] = []
    exact_integrity = True
    for index, case in enumerate(config["sources"]["cases"]):
        case_root = work_dir / f"probe_{index:02d}"
        case_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        wall_path = case_root / "wall_data.pt"
        mesh_path = case_root / "shape_remeshed.obj"
        common = {
            "delays": [int(value) for value in transport["attempt_delays_seconds"]],
            "timeout": int(transport["timeout_seconds_per_attempt"]),
            "chunk_bytes": int(transport["chunk_bytes"]),
            "user_agent": str(transport["user_agent"]),
        }
        _download_file(
            base_url + case["wall_path"],
            wall_path,
            expected_bytes=int(case["wall_bytes"]),
            **common,
        )
        _download_file(
            base_url + case["mesh_path"],
            mesh_path,
            expected_bytes=int(case["mesh_bytes"]),
            **common,
        )
        integrity = bool(
            wall_path.stat().st_size == int(case["wall_bytes"])
            and mesh_path.stat().st_size == int(case["mesh_bytes"])
            and _sha256_file(wall_path) == case["wall_sha256"]
            and _git_blob_oid(mesh_path) == case["mesh_git_blob_oid"]
        )
        exact_integrity = exact_integrity and integrity
        try:
            analysis = analyse_case(wall_path, mesh_path, config)
            analysis_error = None
        except AneuGSurfaceVectorP0Error as exc:
            analysis = None
            analysis_error = type(exc).__name__
        case_results.append(
            {"registered_probe_index": index, "exact_integrity": integrity,
             "analysis": analysis, "analysis_error": analysis_error}
        )

    analyses = [row["analysis"] for row in case_results if row["analysis"] is not None]
    all_analysed = len(analyses) == len(case_results)
    gate = config["gate"]
    checks = {
        "all_exact_bytes_hashes_and_blob_oids_match": exact_integrity,
        "weights_only_tensor_dictionary_loads": all_analysed,
        "all_required_coordinate_and_wss_keys_exist": bool(
            all_analysed and all(row["all_required_keys_present"] for row in analyses)
        ),
        "at_least_80_finite_phases_and_static_coordinates": bool(
            all_analysed
            and all(
                row["source_phases"] >= int(config["access"]["minimum_phases"])
                and row["finite"]
                and row["coordinate_static_max_abs"]
                <= float(gate["coordinate_static_max_abs_tolerance"])
                for row in analyses
            )
        ),
        "triangular_mesh_indices_and_nonzero_normals_are_valid": bool(
            all_analysed and all(row["mesh_valid"] for row in analyses)
        ),
        "coordinate_to_mesh_vertex_match_fraction_at_least_0_999": bool(
            all_analysed
            and all(
                row["mesh_coordinate_match_fraction"]
                >= float(gate["mesh_coordinate_match_fraction_minimum"])
                for row in analyses
            )
        ),
        "median_and_p95_normal_component_ratios_within_bounds": bool(
            all_analysed
            and all(
                row["median_normal_component_ratio"]
                <= float(gate["median_normal_component_ratio_maximum"])
                and row["p95_normal_component_ratio"]
                <= float(gate["p95_normal_component_ratio_maximum"])
                for row in analyses
            )
        ),
        "wss_is_nonzero_and_varies_over_time": bool(
            all_analysed and all(row["relative_temporal_variation"] > 1e-6 for row in analyses)
        ),
        "every_probe_has_nonempty_indexed_critical_points_in_at_least_5_percent_of_frames": bool(
            all_analysed
            and all(
                row["critical_nonempty_frame_fraction"]
                >= float(gate["minimum_nonempty_critical_frame_fraction_per_case"])
                for row in analyses
            )
        ),
        "no_model_gpu_outer_test_or_patient_interpretation": True,
    }
    if set(checks) != set(gate["checks"]):
        raise AneuGSurfaceVectorP0Error("Implemented checks differ from registration.")
    gate_passed = all(checks.values())
    aggregate: dict[str, Any] = {"probe_count": len(case_results)}
    if analyses:
        for key in (
            "source_phases",
            "wall_nodes",
            "mesh_vertices",
            "mesh_faces",
            "mesh_coordinate_match_fraction",
            "median_normal_component_ratio",
            "p95_normal_component_ratio",
            "relative_temporal_variation",
            "critical_nonempty_frame_fraction",
            "critical_count_median",
        ):
            values = [float(row[key]) for row in analyses]
            aggregate[key] = {
                "minimum": min(values), "median": _median(values), "maximum": max(values)
            }
    return {
        "schema_version": "aurora.aneug_surface_vector_structure_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "status": "passed_asset_structure_gate" if gate_passed else "failed_asset_structure_gate",
        "public_source_commit": public_source_commit,
        "config_sha256": config["_config_sha256"],
        "scientific_gate_evaluated": True,
        "gate_passed": gate_passed,
        "checks": checks,
        "aggregate": aggregate,
        "private_probe_records": case_results,
        "access": {
            "raw_wall_probe_objects": len(case_results),
            "raw_remeshed_obj_objects": len(case_results),
            "blood_data": False,
            "checkpoint": False,
            "processed_archive": False,
            "model_weight": False,
            "patient_data": False,
            "outer_test": False,
        },
        "authorization": {
            "method": False,
            "architecture": False,
            "gpu": False,
            "outer_test": False,
            "submission_identity": False,
            "next": gate["pass_authorizes"] if gate_passed else gate["failure_action"],
        },
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--public-source-commit", required=True)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        result = run_p0(
            config,
            work_dir=args.work_dir,
            public_source_commit=args.public_source_commit,
        )
        _write_json(args.result, result)
        return 0 if result["gate_passed"] else 1
    except Exception as exc:  # preserve a bounded no-verdict execution record
        result = {
            "schema_version": "aurora.aneug_surface_vector_structure_p0.result.v1",
            "protocol_id": "aneug_surface_vector_structure_raw_probe_p0_v1",
            "status": "execution_incomplete_no_scientific_verdict",
            "public_source_commit": args.public_source_commit,
            "scientific_gate_evaluated": False,
            "gate_passed": False,
            "error_type": type(exc).__name__,
            "authorization": {
                "method": False,
                "architecture": False,
                "gpu": False,
                "outer_test": False,
                "submission_identity": False,
                "next": "close_without_same_contract_repair_or_rerun",
            },
        }
        _write_json(args.result, result)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
