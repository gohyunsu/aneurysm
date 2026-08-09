"""Prospective AneuG-Flow cycle-functional P0 asset audit.

P0 checks only whether two exact public processed archives support a later,
learned-method-free task-adequacy audit.  It does not select an architecture,
fit a model, inspect an outer test, or establish a paper contribution.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import sys
import types
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


class AneuGCycleP0Error(RuntimeError):
    """Raised when the frozen scientific asset contract fails."""


class AneuGCycleP0Incomplete(RuntimeError):
    """Raised when the registered archive cannot be evaluated as specified."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AneuGCycleP0Error(message)


def canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_bytes), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version") == "aurora.aneug_cycle_functional_p0.v1",
        "Unexpected AneuG cycle-functional P0 schema.",
    )
    _require(
        payload.get("status") == "preregistered_before_processed_payload_access",
        "P0 must remain prospective relative to both processed payloads.",
    )
    candidate = payload["candidate"]
    _require(candidate.get("source_shortlist_score") == 33, "Score changed.")
    _require(candidate.get("source_shortlist_maximum") == 40, "Scale changed.")
    _require(candidate.get("automatic_selection_threshold") == 32, "Threshold changed.")
    _require(sum(candidate.get("score_axes", {}).values()) == 33, "Axes no longer sum to 33.")
    _require(candidate.get("method_selected") is False, "P0 cannot select a method.")
    _require(
        candidate.get("architecture_selected") is False,
        "P0 cannot select an architecture.",
    )
    _require(
        candidate.get("submission_identity_active") is False,
        "P0 cannot activate a submission identity.",
    )
    source = payload["source"]
    _require(
        source.get("dataset_repository_commit")
        == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "Dataset commit changed.",
    )
    _require(
        source.get("official_code_commit")
        == "4a090a0f12538deef6fcea88b81afe78ce38152e",
        "Official code commit changed.",
    )
    expected_files = {
        "steady": (
            "assembled_registered_steady_data_1k_v4.pth",
            9632510050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
        "transient": (
            "assembled_registered_data_1k_v4.pth",
            23744862051,
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
        ),
    }
    for role, (name, size, digest) in expected_files.items():
        item = source["processed_files"][role]
        _require(
            (item.get("name"), item.get("bytes"), item.get("sha256"))
            == (name, size, digest),
            f"Pinned {role} file identity changed.",
        )
    reader = payload["reader_contract"]
    _require(reader.get("weights_only") is True, "Reader must be weights-only.")
    _require(reader.get("mmap") is True, "Reader must memory-map tensor storage.")
    _require(
        reader.get("arbitrary_pickle_globals_allowed") is False,
        "Arbitrary pickle globals are prohibited.",
    )
    gate = payload["gate"]
    _require(gate.get("all_checks_required") is True, "P0 is an all-check gate.")
    _require(
        gate.get("pass_authorizes")
        == "register_method_free_p1_cycle_functional_task_adequacy_perturbation_audit_only",
        "P0 pass authorization changed.",
    )
    execution = payload["execution"]
    _require(execution.get("server") == "introai9", "P0 must use introai9 only.")
    _require(execution.get("scheduler") == "pbs", "P0 must use PBS.")
    _require(execution.get("gpu_requested") is False, "P0 must be CPU-only.")
    _require(
        execution.get("same_contract_rerun_allowed") is False,
        "Same-contract reruns are prohibited.",
    )
    return payload


@contextlib.contextmanager
def _safe_meshes_global(torch: Any) -> Iterator[None]:
    """Allow only the serialized PyTorch3D Meshes state container.

    The P0 never calls a PyTorch3D method.  The placeholder permits PyTorch's
    weights-only unpickler to restore the object's tensor state while keeping
    every other arbitrary pickle global prohibited.
    """

    module_names = ("pytorch3d", "pytorch3d.structures", "pytorch3d.structures.meshes")
    previous = {name: sys.modules.get(name) for name in module_names}
    root = types.ModuleType("pytorch3d")
    structures = types.ModuleType("pytorch3d.structures")
    meshes = types.ModuleType("pytorch3d.structures.meshes")
    Meshes = type("Meshes", (), {})
    Meshes.__module__ = "pytorch3d.structures.meshes"
    meshes.Meshes = Meshes
    structures.Meshes = Meshes
    structures.meshes = meshes
    root.structures = structures
    sys.modules["pytorch3d"] = root
    sys.modules["pytorch3d.structures"] = structures
    sys.modules["pytorch3d.structures.meshes"] = meshes
    try:
        with torch.serialization.safe_globals([Meshes]):
            yield
    finally:
        for name in reversed(module_names):
            prior = previous[name]
            if prior is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = prior


def safe_torch_load(path: str | Path, torch: Any) -> Any:
    try:
        with _safe_meshes_global(torch):
            return torch.load(
                str(path), map_location="cpu", weights_only=True, mmap=True
            )
    except Exception as exc:  # exact failure is preserved in the aggregate
        raise AneuGCycleP0Incomplete(
            f"weights-only archive load failed: {type(exc).__name__}: {exc}"
        ) from exc


def cycle_moments(wss: Any, torch: Any, eps: float = 1e-12) -> dict[str, Any]:
    """Compute the exact discrete-cycle sufficient moments and derived fields."""

    _require(wss.ndim == 3 and wss.shape[-1] == 3, "WSS must have shape [T,N,3].")
    mean_vector = wss.mean(dim=0)
    mean_magnitude = torch.linalg.vector_norm(wss, dim=-1).mean(dim=0)
    mean_vector_magnitude = torch.linalg.vector_norm(mean_vector, dim=-1)
    safe_a = torch.clamp(mean_magnitude, min=eps)
    osi = 0.5 * (1.0 - mean_vector_magnitude / safe_a)
    osi = torch.clamp(osi, min=0.0, max=0.5)
    rrt = 1.0 / torch.clamp(mean_vector_magnitude, min=eps)
    return {
        "mean_vector": mean_vector,
        "mean_magnitude": mean_magnitude,
        "tawss": mean_magnitude,
        "osi": osi,
        "rrt": rrt,
    }


def _tensor_finite(tensor: Any, torch: Any) -> bool:
    return bool(torch.isfinite(tensor).all().item())


def inspect_payloads(
    steady: Mapping[str, Any],
    transient: Mapping[str, Any],
    torch: Any,
    *,
    minimum_cases: int,
    expected_timesteps: int,
    static_tolerance: float,
    roundtrip_tolerance: float,
) -> dict[str, Any]:
    """Inspect loaded payloads without fitting a model or exposing case IDs."""

    _require(isinstance(steady, Mapping), "Steady archive root is not a mapping.")
    _require(isinstance(transient, Mapping), "Transient archive root is not a mapping.")
    _require(
        {"label", "tensor_norm"}.issubset(steady),
        "Steady archive lacks label/tensor_norm.",
    )
    norm = steady["tensor_norm"]
    _require(isinstance(norm, Mapping), "tensor_norm is not a mapping.")
    _require({"mean", "std"}.issubset(norm), "tensor_norm lacks mean/std.")
    labels = [str(value) for value in steady["label"]]
    required_wss = ["wss_x", "wss_y", "wss_z"]
    _require(all(label in labels for label in required_wss), "Steady WSS labels missing.")
    mean = norm["mean"].detach().cpu()
    std = norm["std"].detach().cpu()
    _require(_tensor_finite(mean, torch) and _tensor_finite(std, torch), "Norm is non-finite.")
    wss_norm_idx = [labels.index(label) for label in required_wss]
    wss_mean = mean.reshape(-1)[wss_norm_idx]
    wss_std = std.reshape(-1)[wss_norm_idx]
    _require(bool((wss_std > 0).all().item()), "Physical WSS scale is not recoverable.")

    _require(
        {"registered_data_list", "mesh_data"}.issubset(transient),
        "Transient archive lacks registered_data_list/mesh_data.",
    )
    cases = transient["registered_data_list"]
    mesh_data = transient["mesh_data"]
    _require(isinstance(cases, Sequence), "registered_data_list is not a sequence.")
    _require(len(cases) >= minimum_cases, "Transient case count is below the frozen floor.")
    _require(isinstance(mesh_data, Mapping), "mesh_data is not a mapping.")
    _require("cases" in mesh_data and "faces_list" in mesh_data, "Mesh linkage is incomplete.")

    case_names = [str(case.get("case", "")) for case in cases]
    _require(all(case_names), "At least one transient case name is empty.")
    _require(len(case_names) == len(set(case_names)), "Transient case names are not unique.")
    _require(
        case_names == [str(name) for name in mesh_data["cases"]],
        "Transient and mesh case order differ.",
    )

    first = cases[0]
    _require(isinstance(first, Mapping), "Transient case is not a mapping.")
    common_labels = [str(value) for value in first.get("labels", [])]
    required_labels = [
        "x",
        "y",
        "z",
        "x_normal",
        "y_normal",
        "z_normal",
        "wss_x",
        "wss_y",
        "wss_z",
    ]
    _require(all(label in common_labels for label in required_labels), "Required labels missing.")
    static_idx = [common_labels.index(label) for label in required_labels[:6]]
    wss_idx = [common_labels.index(label) for label in required_wss]
    geometry_hashes: set[str] = set()
    node_count: int | None = None
    max_static_error = 0.0
    max_roundtrip_error = 0.0
    physical_abs_max = 0.0
    temporal_variation_min = math.inf

    for case in cases:
        _require(isinstance(case, Mapping), "Transient case is not a mapping.")
        _require([str(value) for value in case.get("labels", [])] == common_labels, "Labels differ.")
        tensor = case.get("tensor")
        _require(hasattr(tensor, "shape") and tensor.ndim == 3, "Case tensor is not [T,N,C].")
        _require(int(tensor.shape[0]) == expected_timesteps, "Unexpected timestep count.")
        _require(int(tensor.shape[2]) == len(common_labels), "Tensor/label width differs.")
        if node_count is None:
            node_count = int(tensor.shape[1])
        _require(int(tensor.shape[1]) == node_count, "Registered node count differs.")
        _require(_tensor_finite(tensor, torch), "Transient tensor is non-finite.")

        static = tensor[..., static_idx]
        static_error = float((static - static[:1]).abs().max().item())
        max_static_error = max(max_static_error, static_error)
        xyz = tensor[0, :, static_idx[:3]].detach().cpu().contiguous()
        geometry_hashes.add(hashlib.sha256(xyz.numpy().tobytes()).hexdigest())

        normalized_wss = tensor[..., wss_idx].detach().cpu()
        physical_wss = normalized_wss * wss_std.reshape(1, 1, 3) + wss_mean.reshape(1, 1, 3)
        _require(_tensor_finite(physical_wss, torch), "Denormalized WSS is non-finite.")
        physical_abs_max = max(physical_abs_max, float(physical_wss.abs().max().item()))
        variation = float((physical_wss[1:] - physical_wss[:-1]).abs().max().item())
        temporal_variation_min = min(temporal_variation_min, variation)
        roundtrip = (physical_wss - wss_mean.reshape(1, 1, 3)) / wss_std.reshape(1, 1, 3)
        max_roundtrip_error = max(
            max_roundtrip_error,
            float((roundtrip - normalized_wss).abs().max().item()),
        )

    _require(max_static_error <= static_tolerance, "Geometry changes across the cycle.")
    _require(physical_abs_max > 0.0, "All physical WSS is zero.")
    _require(temporal_variation_min > 0.0, "At least one case has no temporal WSS variation.")
    _require(max_roundtrip_error <= roundtrip_tolerance, "Normalization roundtrip failed.")
    _require(len(geometry_hashes) == len(cases), "Duplicate registered geometries found.")

    faces_list = mesh_data["faces_list"]
    _require(isinstance(faces_list, Sequence) and len(faces_list) > 0, "faces_list is empty.")
    faces = faces_list[0].detach().cpu()
    _require(faces.ndim == 2 and int(faces.shape[1]) == 3, "Faces are not triangles.")
    _require(_tensor_finite(faces, torch), "Faces are non-finite.")
    _require(int(faces.min().item()) >= 0, "Face index is negative.")
    _require(int(faces.max().item()) < int(node_count), "Face index exceeds node count.")

    return {
        "case_count": len(cases),
        "node_count": int(node_count),
        "timesteps": expected_timesteps,
        "channel_count": len(common_labels),
        "unique_geometry_count": len(geometry_hashes),
        "triangular_face_count": int(faces.shape[0]),
        "stable_prefix_case_count": sum(name.startswith("stable") for name in case_names),
        "nonstable_prefix_case_count": sum(not name.startswith("stable") for name in case_names),
        "max_static_abs_error": max_static_error,
        "max_normalization_roundtrip_abs_error": max_roundtrip_error,
        "minimum_case_temporal_wss_max_abs_difference": temporal_variation_min,
        "maximum_physical_wss_abs": physical_abs_max,
        "steady_labels": labels,
        "transient_labels": common_labels,
        "case_identifiers_in_result": False,
    }


def audit(
    config: Mapping[str, Any],
    steady_path: str | Path,
    transient_path: str | Path,
    source_commit: str,
) -> dict[str, Any]:
    import torch

    paths = {"steady": Path(steady_path), "transient": Path(transient_path)}
    file_checks: dict[str, Any] = {}
    identities_pass = True
    for role, path in paths.items():
        expected = config["source"]["processed_files"][role]
        observed_size = path.stat().st_size
        observed_sha256 = file_sha256(path)
        match = observed_size == expected["bytes"] and observed_sha256 == expected["sha256"]
        identities_pass = identities_pass and match
        file_checks[role] = {
            "name": expected["name"],
            "observed_bytes": observed_size,
            "observed_sha256": observed_sha256,
            "exact_identity_match": match,
        }
    _require(identities_pass, "One or both processed file identities differ.")

    steady = safe_torch_load(paths["steady"], torch)
    transient = safe_torch_load(paths["transient"], torch)
    checks = config["gate"]["checks"]
    summary = inspect_payloads(
        steady,
        transient,
        torch,
        minimum_cases=int(checks["transient_case_count_at_least"]),
        expected_timesteps=80,
        static_tolerance=float(
            checks["geometry_and_normals_are_static_across_the_cycle_with_max_abs_tolerance"]
        ),
        roundtrip_tolerance=float(
            checks["all_normalization_roundtrip_max_abs_error_at_most"]
        ),
    )
    return {
        "schema_version": "aurora.aneug_cycle_functional_p0.result.v1",
        "status": "completed_passed",
        "scientific_gate_evaluated": True,
        "gate_passed": True,
        "config_sha256": canonical_hash(config),
        "source_commit": source_commit,
        "dataset_repository_commit": config["source"]["dataset_repository_commit"],
        "official_code_commit": config["source"]["official_code_commit"],
        "server": "introai9",
        "scheduler": "pbs",
        "gpu_requested": False,
        "torch_version": torch.__version__,
        "files": file_checks,
        "summary": summary,
        "count_scope": {
            "observed_current_release_cases": summary["case_count"],
            "dataset_page_reported_cases": config["source"]["dataset_page_transient_cases"],
            "rhsia_paper_reported_cases": config["source"]["rhsia_paper_transient_cases"],
            "rhsia_same_release_assumed": False,
        },
        "authorization": config["gate"]["pass_authorizes"],
        "method_selected": False,
        "architecture_selected": False,
        "gpu_training_authorized": False,
        "outer_test_authorized": False,
        "submission_identity_active": False,
    }


def _write_result(path: str | Path, payload: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--steady", required=True)
    parser.add_argument("--transient", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config)
    config_digest = file_sha256(config_path)
    try:
        config = load_config(config_path)
        config_digest = canonical_hash(config)
        result = audit(config, args.steady, args.transient, args.source_commit)
        exit_code = 0
    except AneuGCycleP0Error as exc:
        result = {
            "schema_version": "aurora.aneug_cycle_functional_p0.result.v1",
            "status": "completed_failed",
            "scientific_gate_evaluated": True,
            "gate_passed": False,
            "config_sha256": config_digest,
            "source_commit": args.source_commit,
            "server": "introai9",
            "gpu_requested": False,
            "failure": f"{type(exc).__name__}: {exc}",
            "same_contract_rerun_allowed": False,
        }
        exit_code = 1
    except (AneuGCycleP0Incomplete, OSError, ImportError) as exc:
        result = {
            "schema_version": "aurora.aneug_cycle_functional_p0.result.v1",
            "status": "execution_incomplete",
            "scientific_gate_evaluated": False,
            "gate_passed": False,
            "config_sha256": config_digest,
            "source_commit": args.source_commit,
            "server": "introai9",
            "gpu_requested": False,
            "failure": f"{type(exc).__name__}: {exc}",
            "same_contract_rerun_allowed": False,
        }
        exit_code = 2
    except Exception as exc:
        result = {
            "schema_version": "aurora.aneug_cycle_functional_p0.result.v1",
            "status": "execution_incomplete",
            "scientific_gate_evaluated": False,
            "gate_passed": False,
            "config_sha256": config_digest,
            "source_commit": args.source_commit,
            "server": "introai9",
            "gpu_requested": False,
            "failure": f"{type(exc).__name__}: {exc}",
            "same_contract_rerun_allowed": False,
        }
        exit_code = 2
    _write_result(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
