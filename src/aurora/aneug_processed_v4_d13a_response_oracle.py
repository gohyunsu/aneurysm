"""Train-basis validation oracle for complete transient WSS responses.

This is a representation diagnostic, not a learned surrogate.  A basis is fit
only from D5 training cycles.  Validation targets are projected to measure the
best reconstruction available to that representation.  Outer and auxiliary
values are never read, and oracle coefficients are never called predictions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_processed_v4_d9 import (
    case_metrics,
    load_cached_split,
    tangent_projection,
)


class D13AResponseOracleError(RuntimeError):
    """Raised when a D13A evidence or execution boundary is violated."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise D13AResponseOracleError(label)


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
    _require(not target.exists() and not temporary.exists(), "result_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _strict_atomic_torch_save(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "basis_exists")
    try:
        torch.save(dict(payload), temporary)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_processed_v4_d13a_response_oracle.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id") == "aneug_processed_v4_d13a_response_oracle_v1",
        "protocol",
    )
    _require(config.get("status") == "prepared_non_executable", "status")
    data = config["bound_data"]
    _require(
        (
            data["train_cases"],
            data["validation_cases"],
            data["outer_cases"],
            data["auxiliary_cases"],
            data["phases"],
            data["nodes"],
        )
        == (406, 51, 51, 70, 80, 13_902),
        "data_shape",
    )
    _require(data["read_outer_or_auxiliary"] is False, "sealed_data")
    representation = config["representation"]
    _require(
        representation["rank_grid"] == [0, 16, 32, 64, 128, 256]
        and representation["maximum_rank"] == 256,
        "rank_grid",
    )
    _require(
        representation["amplitude"] == "oracle_true_validation_rms"
        and representation["basis_source"] == "train_only_centered_normalized_cycles",
        "oracle_label",
    )
    authorization = config["authorization"]
    _require(authorization["execute_now"] is False, "non_executable")
    _require(authorization["requires_fresh_private_activation"] is True, "activation")
    for key in (
        "learned_predictor",
        "rank_selection",
        "outer_test",
        "paper_claim",
        "publish_numeric_result",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")
    _require(
        authorization["server"] == "introai9"
        and authorization["excluded_server"] == "junjinyong",
        "server_scope",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.aneug_processed_v4_d13a.private_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "D13A_response_oracle_validation",
        "activation_stage",
    )
    _require(activation.get("d12_terminal_record_sha256"), "d12_terminal_record")
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    _require(
        activation.get("cache_manifest_sha256")
        == config["bound_data"]["cache_manifest_sha256"],
        "activation_cache",
    )
    return activation


def reference_vertex_weights(cases: Sequence[Mapping[str, torch.Tensor]]) -> torch.Tensor:
    _require(len(cases) >= 2, "case_count")
    weights = torch.stack([case["vertex_weights"].to(torch.float64) for case in cases])
    reference = weights.mean(dim=0)
    _require(
        bool(torch.isfinite(reference).all().item())
        and bool((reference > 0).all().item()),
        "reference_weights",
    )
    return (reference / reference.sum()).to(torch.float32)


def weighted_normalized_cycles(
    cases: Sequence[Mapping[str, torch.Tensor]],
    reference_weights: torch.Tensor,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor, tuple[int, int]]:
    phases, nodes, channels = cases[0]["wss"].shape
    _require(channels == 3 and reference_weights.shape == (nodes,), "cycle_shape")
    factor = torch.sqrt(reference_weights / phases).view(1, nodes, 1)
    matrix = torch.empty(
        (len(cases), phases * nodes * channels), dtype=torch.float32, device=device
    )
    scales = torch.empty(len(cases), dtype=torch.float32, device=device)
    factor_device = factor.to(device)
    for index, case in enumerate(cases):
        _require(tuple(case["wss"].shape) == (phases, nodes, channels), "shared_shape")
        weighted = case["wss"].to(device=device, non_blocking=True) * factor_device
        scale = torch.linalg.vector_norm(weighted)
        _require(bool(torch.isfinite(scale).item()) and float(scale.item()) > 0.0, "scale")
        matrix[index] = weighted.reshape(-1) / scale
        scales[index] = scale
    return matrix, scales, (phases, nodes)


def fit_response_basis(
    cases: Sequence[Mapping[str, torch.Tensor]],
    maximum_rank: int,
    device: torch.device,
) -> dict[str, torch.Tensor]:
    _require(0 < maximum_rank < len(cases), "maximum_rank")
    weights = reference_vertex_weights(cases)
    matrix, scales, shape = weighted_normalized_cycles(cases, weights, device)
    mean = matrix.mean(dim=0)
    centered = matrix - mean.unsqueeze(0)
    gram = centered @ centered.T
    gram = 0.5 * (gram + gram.T)
    values, vectors = torch.linalg.eigh(gram.to(torch.float64))
    order = torch.argsort(values, descending=True)
    values = torch.clamp(values[order], min=0.0)
    vectors = vectors[:, order].to(torch.float32)
    singular = torch.sqrt(values[:maximum_rank]).to(torch.float32)
    _require(bool((singular > 1e-7).all().item()), "basis_rank")
    basis = (vectors[:, :maximum_rank].T @ centered) / singular.unsqueeze(1)
    gram_basis = basis @ basis.T
    identity = torch.eye(maximum_rank, device=device)
    orthogonality_error = torch.max(torch.abs(gram_basis - identity))
    _require(float(orthogonality_error.item()) < 2e-3, "basis_orthogonality")
    total = torch.clamp(values.sum(), min=1e-12)
    explained = torch.cumsum(values, dim=0) / total
    return {
        "reference_weights": weights,
        "train_scales": scales,
        "mean": mean,
        "basis": basis,
        "eigenvalues": values.to(torch.float32),
        "explained_variance": explained.to(torch.float32),
        "orthogonality_error": orthogonality_error,
        "phases": torch.tensor(shape[0]),
        "nodes": torch.tensor(shape[1]),
    }


@torch.no_grad()
def oracle_reconstruction(
    case: Mapping[str, torch.Tensor],
    fitted: Mapping[str, torch.Tensor],
    rank: int,
    device: torch.device,
) -> tuple[torch.Tensor, float]:
    phases = int(fitted["phases"].item())
    nodes = int(fitted["nodes"].item())
    reference_weights = fitted["reference_weights"].to(device)
    _require(0 <= rank <= int(fitted["basis"].shape[0]), "oracle_rank")
    factor = torch.sqrt(reference_weights / phases).view(1, nodes, 1)
    reference = case["wss"].to(device=device, non_blocking=True)
    weighted = reference * factor
    scale = torch.linalg.vector_norm(weighted)
    normalized = weighted.reshape(-1) / scale
    centered = normalized - fitted["mean"]
    if rank == 0:
        reconstructed = fitted["mean"]
    else:
        basis = fitted["basis"][:rank]
        coefficients = basis @ centered
        reconstructed = fitted["mean"] + basis.T @ coefficients
    weighted_prediction = reconstructed.reshape(phases, nodes, 3) * scale
    prediction = weighted_prediction / factor
    prediction = tangent_projection(prediction, case["normals"].to(device))
    weighted_error = float(
        torch.linalg.vector_norm((prediction - reference) * factor)
        .div(torch.clamp(torch.linalg.vector_norm(weighted), min=1e-12))
        .item()
    )
    return prediction, weighted_error


@torch.no_grad()
def evaluate_oracle(
    validation_cases: Sequence[Mapping[str, torch.Tensor]],
    fitted: Mapping[str, torch.Tensor],
    ranks: Sequence[int],
    device: torch.device,
) -> dict[str, Any]:
    rows: dict[str, list[dict[str, float]]] = {str(rank): [] for rank in ranks}
    weighted_errors: dict[str, list[float]] = {str(rank): [] for rank in ranks}
    for case in validation_cases:
        for rank in ranks:
            prediction, weighted_error = oracle_reconstruction(case, fitted, rank, device)
            metrics = case_metrics(
                prediction,
                case["wss"].to(device),
                case["vertex_weights"].to(device),
            )
            rows[str(rank)].append(metrics)
            weighted_errors[str(rank)].append(weighted_error)
    aggregate: dict[str, dict[str, float]] = {}
    for rank in ranks:
        key = str(rank)
        metric_keys = tuple(rows[key][0])
        aggregate[key] = {
            metric: sum(row[metric] for row in rows[key]) / len(rows[key])
            for metric in metric_keys
        }
        aggregate[key]["reference_weighted_oracle_relative_l2"] = sum(
            weighted_errors[key]
        ) / len(weighted_errors[key])
    return {
        "aggregate_by_rank": aggregate,
        "per_case_without_identifiers_by_rank": rows,
        "validation_case_count": len(validation_cases),
    }


def run_oracle(
    config: Mapping[str, Any],
    cache_path: str | Path,
    result_path: str | Path,
    basis_path: str | Path,
    provenance: Mapping[str, str],
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    cache = Path(cache_path)
    _require(
        file_sha256(cache / "cache_manifest.json")
        == config["bound_data"]["cache_manifest_sha256"],
        "cache_identity",
    )
    manifest = json.loads((cache / "cache_manifest.json").read_text(encoding="utf-8"))
    _require(
        manifest.get("r0_pass") is True
        and manifest.get("train_cases") == 406
        and manifest.get("validation_cases") == 51
        and manifest.get("outer_cases_read") == 0
        and manifest.get("auxiliary_cases_read") == 0,
        "cache_boundary",
    )
    device = torch.device("cuda")
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    train_cases = load_cached_split(cache, "train")
    validation_cases = load_cached_split(cache, "validation")
    maximum_rank = int(config["representation"]["maximum_rank"])
    ranks = [int(rank) for rank in config["representation"]["rank_grid"]]
    fitted = fit_response_basis(train_cases, maximum_rank, device)
    evaluation = evaluate_oracle(validation_cases, fitted, ranks, device)
    basis_payload = {
        "schema_version": "aurora.aneug_processed_v4_d13a.private_basis.v1",
        "protocol_id": config["protocol_id"],
        "reference_weights": fitted["reference_weights"].cpu(),
        "train_scales": fitted["train_scales"].cpu(),
        "mean": fitted["mean"].cpu(),
        "basis": fitted["basis"].cpu(),
        "eigenvalues": fitted["eigenvalues"].cpu(),
        "explained_variance": fitted["explained_variance"].cpu(),
        "orthogonality_error": float(fitted["orthogonality_error"].item()),
        "phases": int(fitted["phases"].item()),
        "nodes": int(fitted["nodes"].item()),
        "train_cases": 406,
        "case_ids_included": False,
        "public_commit": provenance["public_commit"],
        "config_sha256": provenance["config_sha256"],
        "activation_sha256": provenance["activation_sha256"],
        "cache_manifest_sha256": provenance["cache_manifest_sha256"],
        "d12_terminal_record_sha256": provenance["d12_terminal_record_sha256"],
    }
    _strict_atomic_torch_save(basis_path, basis_payload)
    result = {
        "schema_version": "aurora.aneug_processed_v4_d13a.private_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "evidence_role": "train_basis_validation_oracle_not_model_performance",
        "rank_grid": ranks,
        "explained_variance_by_rank": {
            str(rank): (
                0.0
                if rank == 0
                else float(fitted["explained_variance"][rank - 1].item())
            )
            for rank in ranks
        },
        "orthogonality_error": float(fitted["orthogonality_error"].item()),
        "evaluation": evaluation,
        "basis_bytes": Path(basis_path).stat().st_size,
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "train_case_count": 406,
        "validation_case_count": 51,
        "oracle_uses_true_validation_amplitude": True,
        "learned_predictor": False,
        "rank_selected": False,
        "outer_or_auxiliary_values_read": False,
        "case_ids_included": False,
        "development_only": True,
        "paper_result_or_claim": False,
        "public_commit": provenance["public_commit"],
        "config_sha256": provenance["config_sha256"],
        "activation_sha256": provenance["activation_sha256"],
        "cache_manifest_sha256": provenance["cache_manifest_sha256"],
        "d12_terminal_record_sha256": provenance["d12_terminal_record_sha256"],
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--basis", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    _require(
        all(
            value is not None
            for value in (
                args.activation,
                args.expected_commit,
                args.cache,
                args.result,
                args.basis,
            )
        ),
        "execution_arguments",
    )
    activation = validate_activation(args.activation, config, args.expected_commit)
    provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "cache_manifest_sha256": config["bound_data"]["cache_manifest_sha256"],
        "d12_terminal_record_sha256": activation["d12_terminal_record_sha256"],
    }
    run_oracle(config, args.cache, args.result, args.basis, provenance)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
