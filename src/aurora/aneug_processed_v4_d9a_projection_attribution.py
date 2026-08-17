"""No-fit validation attribution for the failed D9 moment-POD projection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_processed_v4_d9 import (
    MeshCanonicalizedPilot,
    case_metrics,
    load_cached_split,
)
from aurora.cycle_moment_projection import project_cycle_moments


class D9AAttributionError(RuntimeError):
    """Raised when a frozen D9A boundary is violated."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise D9AAttributionError(label)


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
        temporary.replace(target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def validate_config(config: Mapping[str, Any]) -> None:
    _require(config.get("schema_version") == "aurora.aneug_processed_v4_d9a_projection_attribution.v1", "config_schema")
    _require(config.get("status") == "executable_validation_only_no_fit_attribution", "config_status")
    scope = config["scope"]
    _require(scope["validation_cases"] == 51, "validation_count")
    for key in ("fit_model", "select_checkpoint", "read_train_case_values", "read_outer_or_auxiliary", "change_threshold_seed_split_or_metric"):
        _require(scope[key] is False, f"scope_{key}")
    comparison = config["comparison"]
    _require(comparison["same_frozen_checkpoint_single_forward"] is True, "same_checkpoint")
    _require(comparison["modes"] == ["raw_moment_pod", "exact_moment_projection"], "modes")
    authorization = config["authorization"]
    _require(authorization["execute_D9A_once"] is True, "execute")
    for key in ("repair_model", "multi_seed_confirmation", "outer_test", "paper_result_or_claim", "publish_numeric_result", "maintain_public_site"):
        _require(authorization[key] is False, f"authorization_{key}")
    _require(authorization["excluded_server"] == "junjinyong", "excluded_server")


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(path: str | Path, config: Mapping[str, Any], expected_commit: str) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(activation.get("schema_version") == "aurora.aneug_processed_v4_d9a.private_activation.v1", "activation_schema")
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(activation.get("public_commit") == expected_commit, "activation_commit")
    _require(activation.get("quality_conclusion") == "success", "activation_quality")
    _require(activation.get("authorized_stage") == "D9A_projection_attribution", "activation_stage")
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    for key in ("cache_manifest_sha256", "moment_checkpoint_sha256", "moment_result_sha256", "d9_aggregate_sha256"):
        _require(activation.get(key) == config["bound_evidence"][key], f"activation_{key}")
    return activation


def summarize_pairs(per_case: Sequence[Mapping[str, Mapping[str, float] | float]]) -> dict[str, Any]:
    _require(len(per_case) > 0, "empty_cases")
    metric_keys = tuple(per_case[0]["raw"].keys())  # type: ignore[union-attr]
    raw = {key: sum(float(item["raw"][key]) for item in per_case) / len(per_case) for key in metric_keys}  # type: ignore[index]
    projected = {key: sum(float(item["projected"][key]) for item in per_case) / len(per_case) for key in metric_keys}  # type: ignore[index]
    ratios = {
        key: projected[key] / max(raw[key], 1e-12)
        for key in ("field_relative_l2", "tawss_normalized_absolute_error", "osi_mae")
    }
    directions = {
        "projection_increases_field_error": projected["field_relative_l2"] > raw["field_relative_l2"],
        "projection_reduces_tawss_error": projected["tawss_normalized_absolute_error"] < raw["tawss_normalized_absolute_error"],
        "projection_increases_osi_error": projected["osi_mae"] > raw["osi_mae"],
        "projection_preserves_coverage": projected["osi_coverage"] >= raw["osi_coverage"],
    }
    return {"raw": raw, "projected": projected, "projected_over_raw": ratios, "directions": directions}


def _moment_residuals(field: torch.Tensor, mean_vector: torch.Tensor, mean_magnitude: torch.Tensor, weights: torch.Tensor) -> dict[str, float]:
    observed_vector = field.mean(dim=0)
    vector_numerator = torch.sum(weights * torch.sum((observed_vector - mean_vector) ** 2, dim=-1))
    vector_denominator = torch.sum(weights * torch.sum(mean_vector**2, dim=-1))
    vector_relative_l2 = torch.sqrt(vector_numerator / torch.clamp(vector_denominator, min=1e-12))
    observed_magnitude = torch.linalg.vector_norm(field, dim=-1).mean(dim=0)
    magnitude_relative_l1 = torch.sum(weights * torch.abs(observed_magnitude - mean_magnitude)) / torch.clamp(torch.sum(weights * mean_magnitude), min=1e-12)
    return {"mean_vector_relative_l2": float(vector_relative_l2.item()), "mean_magnitude_relative_l1": float(magnitude_relative_l1.item())}


@torch.no_grad()
def run_attribution(config: Mapping[str, Any], cache_path: str | Path, checkpoint_path: str | Path, result_path: str | Path) -> dict[str, Any]:
    cache = Path(cache_path)
    checkpoint_file = Path(checkpoint_path)
    bound = config["bound_evidence"]
    _require(file_sha256(cache / "cache_manifest.json") == bound["cache_manifest_sha256"], "cache_manifest_identity")
    _require(file_sha256(checkpoint_file) == bound["moment_checkpoint_sha256"], "checkpoint_identity")
    manifest = json.loads((cache / "cache_manifest.json").read_text(encoding="utf-8"))
    _require(manifest.get("r0_pass") is True and manifest.get("validation_cases") == 51, "cache_boundary")
    _require(manifest.get("outer_cases_read") == 0 and manifest.get("auxiliary_cases_read") == 0, "sealed_cache")

    device = torch.device("cuda")
    topology = torch.load(cache / "topology.pt", map_location=device, weights_only=True)
    basis = torch.load(cache / "temporal_basis.pt", map_location=device, weights_only=True)["basis"]
    validation_cases = load_cached_split(cache, "validation")
    checkpoint = torch.load(checkpoint_file, map_location="cpu", weights_only=True)
    _require(checkpoint.get("schema_version") == "aurora.aneug_processed_v4_d9.private_checkpoint.v1", "checkpoint_schema")
    _require(checkpoint.get("variant") == "moment_pod" and checkpoint.get("seed") == 1103, "checkpoint_variant_seed")
    model = MeshCanonicalizedPilot(topology, variant="moment_pod", temporal_basis=basis).to(device)
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()

    per_case: list[dict[str, Any]] = []
    for cpu_case in validation_cases:
        case = {key: value.to(device=device, non_blocking=True) for key, value in cpu_case.items()}
        output = model(case, exact_moment_projection=False)
        raw = output["field"]
        projected = project_cycle_moments(output["residual"], output["mean_vector"], output["mean_magnitude"], case["normals"], torch)["field"]
        raw_metrics = case_metrics(raw, case["wss"], case["vertex_weights"])
        projected_metrics = case_metrics(projected, case["wss"], case["vertex_weights"])
        displacement = torch.sqrt(torch.sum(case["vertex_weights"].unsqueeze(0) * torch.sum((projected - raw) ** 2, dim=-1)) / torch.clamp(torch.sum(case["vertex_weights"].unsqueeze(0) * torch.sum(raw**2, dim=-1)), min=1e-12))
        per_case.append({
            "raw": raw_metrics,
            "projected": projected_metrics,
            "raw_internal_moment_residual": _moment_residuals(raw, output["mean_vector"], output["mean_magnitude"], case["vertex_weights"]),
            "projected_internal_moment_residual": _moment_residuals(projected, output["mean_vector"], output["mean_magnitude"], case["vertex_weights"]),
            "projection_relative_displacement": float(displacement.item()),
        })

    comparison = summarize_pairs(per_case)
    internal_keys = ("mean_vector_relative_l2", "mean_magnitude_relative_l1")
    internal = {
        mode: {key: sum(float(item[f"{mode}_internal_moment_residual"][key]) for item in per_case) / len(per_case) for key in internal_keys}
        for mode in ("raw", "projected")
    }
    result = {
        "schema_version": "aurora.aneug_processed_v4_d9a.private_projection_attribution.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "case_count": len(per_case),
        "comparison": comparison,
        "internal_moment_residual": internal,
        "mean_projection_relative_displacement": sum(float(item["projection_relative_displacement"]) for item in per_case) / len(per_case),
        "per_case_without_identifiers": per_case,
        "fit_or_checkpoint_selection_performed": False,
        "train_case_values_read": False,
        "outer_or_auxiliary_values_read": False,
        "repair_authorized": False,
        "paper_result_or_claim": False,
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--activation", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    validate_activation(args.activation, config, args.expected_commit)
    _require(torch.cuda.is_available(), "cuda_required")
    torch.set_num_threads(4)
    run_attribution(config, args.cache, args.checkpoint, args.result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
