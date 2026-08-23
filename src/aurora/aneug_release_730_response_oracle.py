"""Release-730 complete-cycle response-manifold oracle.

The basis is fit only from the 584 training fields. Validation coefficients
and amplitudes are obtained from the true validation cycles, so every reported
number is an optimistic representation ceiling rather than learned surrogate
performance. Locked-test and processed-only-extra tensors are never indexed.
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

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_release_730_official_graphunet_baseline import (
    extended_case_metrics,
)
from aurora.aneug_release_730_train_audit import (
    _ordered_digest,
    _vertex_areas,
    index_case_records,
    selected_training_records,
    validate_split_evidence,
)


class Release730ResponseOracleError(RuntimeError):
    """Raised when an oracle evidence or execution boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730ResponseOracleError(reason)


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
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
        with temporary.open("xb") as handle:
            torch.save(dict(payload), handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version") == "aurora.aneug_release_730_response_oracle.v1",
        "schema_version",
    )
    _require(config.get("protocol_id") == "aneug_release_730_response_oracle_v1", "protocol_id")
    _require(
        config.get("status") == "prepared_non_executable_until_direct_baseline_terminal",
        "status",
    )
    source = config["source"]
    _require(
        source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36"
        and source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae"
        and source["steady_norm_bytes"] == 9_632_510_050
        and source["steady_norm_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        "source",
    )
    split = config["split"]
    _require(
        (
            split["train_cases"],
            split["validation_cases"],
            split["locked_test_cases"],
            split["processed_only_extra_cases"],
        )
        == (584, 73, 73, 79),
        "split_counts",
    )
    _require(
        split["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "validation_order",
    )
    _require(split["read_train_fields"] and split["read_validation_fields"], "development_read")
    _require(
        not split["read_locked_test_fields"]
        and not split["read_processed_only_extra_fields"]
        and not split["test_opened"],
        "sealed_read",
    )
    representation = config["representation"]
    _require(
        representation["input_field"]
        == "raw_released_physical_cartesian_complete_cycle_wss",
        "input_field",
    )
    _require(
        not representation["hard_tangent_projection"]
        and not representation["hard_periodic_closure"],
        "hard_constraint",
    )
    _require(
        representation["rank_grid"] == [0, 16, 32, 64, 128, 256]
        and representation["maximum_rank"] == 256
        and representation["rank_selection"] == "none_report_all"
        and representation["learned_coefficient_predictor"] is False,
        "rank_contract",
    )
    evaluation = config["evaluation"]
    _require(evaluation["absolute_performance_threshold"] is None, "threshold")
    _require(not evaluation["automatic_rank_or_method_selection"], "automatic_selection")
    runtime = config["runtime"]
    _require(
        runtime["server"] == "introai9"
        and runtime["ngpus"] == 1
        and runtime["memory_gb"] == 64
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        "runtime",
    )
    authorization = config["authorization"]
    _require(not authorization["execute_now"], "execute_now")
    _require(authorization["requires_direct_baseline_terminal_record"], "predecessor")
    _require(authorization["requires_fresh_private_activation"], "activation")
    for key in (
        "learned_predictor",
        "rank_selection",
        "read_locked_test",
        "read_processed_only_extra",
        "paper_performance_claim",
        "publish_numeric_result",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")
    _require(
        authorization["server"] == "introai9"
        and authorization["excluded_server"] == "junjinyong",
        "server_scope",
    )


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_response_oracle_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "single_validation_response_oracle",
        "activation_stage",
    )
    _require(bool(activation.get("direct_baseline_terminal_record_sha256")), "baseline_terminal")
    _require(activation.get("read_locked_test_or_extra") is False, "activation_scope")
    _require(
        activation.get("private_split_manifest_sha256")
        == config["split"]["private_manifest_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["split"]["train_audit_private_sha256"],
        "activation_evidence",
    )
    return activation


def _case_geometry(
    record: Mapping[str, Any], mean: torch.Tensor, std: torch.Tensor, faces: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    normalized = record["tensor"]
    _require(tuple(normalized.shape) == (80, 13_902, 9), "case_shape")
    coordinates = normalized[0, :, :3].detach().cpu().to(torch.float64) * (
        std[:3].to(torch.float64) + 1e-5
    ) + mean[:3].to(torch.float64)
    areas, normals, twice_area = _vertex_areas(coordinates, faces, torch)
    _require(bool((areas > 0).all().item()) and bool((twice_area > 0).all().item()), "mesh")
    return (areas / areas.sum()).to(torch.float32), normals.to(torch.float32)


def _physical_wss(
    record: Mapping[str, Any], mean: torch.Tensor, std: torch.Tensor, device: torch.device
) -> torch.Tensor:
    normalized = record["tensor"][:, :, 6:9]
    _require(tuple(normalized.shape) == (80, 13_902, 3), "wss_shape")
    value = normalized.to(device=device, dtype=torch.float32, non_blocking=True)
    value = value * (std[6:9].to(device).reshape(1, 1, 3) + 1e-5)
    value = value + mean[6:9].to(device).reshape(1, 1, 3)
    _require(bool(torch.isfinite(value).all().item()), "physical_wss")
    return value


def reference_vertex_weights(
    train_records: Sequence[Mapping[str, Any]],
    mean: torch.Tensor,
    std: torch.Tensor,
    faces: torch.Tensor,
) -> torch.Tensor:
    _require(len(train_records) == 584, "train_count")
    total = torch.zeros(13_902, dtype=torch.float64)
    for index, record in enumerate(train_records, start=1):
        weights, _ = _case_geometry(record, mean, std, faces)
        total += weights.to(torch.float64)
        if index % 100 == 0 or index == 584:
            print(json.dumps({"stage": "reference_weights", "cases": index}), flush=True)
    reference = total / len(train_records)
    _require(bool(torch.isfinite(reference).all().item()) and bool((reference > 0).all().item()), "weights")
    return (reference / reference.sum()).to(torch.float32)


def fit_basis_from_matrix(matrix: torch.Tensor, maximum_rank: int) -> dict[str, torch.Tensor]:
    _require(matrix.ndim == 2 and 0 < maximum_rank < matrix.shape[0], "matrix_shape")
    _require(bool(torch.isfinite(matrix).all().item()), "matrix_finite")
    mean = matrix.mean(dim=0)
    matrix.sub_(mean.unsqueeze(0))
    gram = matrix @ matrix.T
    gram = 0.5 * (gram + gram.T)
    values, vectors = torch.linalg.eigh(gram.to(torch.float64))
    order = torch.argsort(values, descending=True)
    values = torch.clamp(values[order], min=0.0)
    vectors = vectors[:, order].to(matrix.dtype)
    singular = torch.sqrt(values[:maximum_rank]).to(matrix.dtype)
    _require(bool((singular > 1e-7).all().item()), "basis_rank")
    basis = (vectors[:, :maximum_rank].T @ matrix) / singular.unsqueeze(1)
    orthogonality = torch.max(
        torch.abs(
            basis @ basis.T
            - torch.eye(maximum_rank, device=matrix.device, dtype=matrix.dtype)
        )
    )
    _require(float(orthogonality.item()) < 3e-3, "basis_orthogonality")
    explained = torch.cumsum(values, dim=0) / torch.clamp(values.sum(), min=1e-12)
    return {
        "mean": mean,
        "basis": basis,
        "eigenvalues": values.to(matrix.dtype),
        "explained_variance": explained.to(matrix.dtype),
        "orthogonality_error": orthogonality,
    }


def fit_response_basis(
    train_records: Sequence[Mapping[str, Any]],
    reference_weights: torch.Tensor,
    mean: torch.Tensor,
    std: torch.Tensor,
    maximum_rank: int,
    device: torch.device,
) -> dict[str, torch.Tensor]:
    _require(len(train_records) == 584 and reference_weights.shape == (13_902,), "fit_scope")
    factor = torch.sqrt(reference_weights.to(device) / 80.0).reshape(1, 13_902, 1)
    width = 80 * 13_902 * 3
    matrix = torch.empty((584, width), dtype=torch.float32, device=device)
    scales = torch.empty(584, dtype=torch.float32, device=device)
    for index, record in enumerate(train_records):
        weighted = _physical_wss(record, mean, std, device) * factor
        scale = torch.linalg.vector_norm(weighted)
        _require(bool(torch.isfinite(scale).item()) and float(scale.item()) > 0.0, "response_scale")
        matrix[index] = weighted.reshape(-1) / scale
        scales[index] = scale
        if (index + 1) % 50 == 0 or index + 1 == 584:
            print(json.dumps({"stage": "response_matrix", "cases": index + 1}), flush=True)
    fitted = fit_basis_from_matrix(matrix, maximum_rank)
    fitted["reference_weights"] = reference_weights.to(device)
    fitted["train_scales"] = scales
    return fitted


@torch.no_grad()
def evaluate_oracle(
    validation_records: Sequence[Mapping[str, Any]],
    fitted: Mapping[str, torch.Tensor],
    mean: torch.Tensor,
    std: torch.Tensor,
    faces: torch.Tensor,
    ranks: Sequence[int],
    device: torch.device,
) -> dict[str, Any]:
    _require(len(validation_records) == 73, "validation_count")
    reference_weights = fitted["reference_weights"].to(device)
    factor = torch.sqrt(reference_weights / 80.0).reshape(1, 13_902, 1)
    basis = fitted["basis"]
    response_mean = fitted["mean"]
    rows: dict[str, list[dict[str, float]]] = {str(rank): [] for rank in ranks}
    weighted_errors: dict[str, list[float]] = {str(rank): [] for rank in ranks}
    for case_index, record in enumerate(validation_records, start=1):
        reference = _physical_wss(record, mean, std, device)
        case_weights, normals = _case_geometry(record, mean, std, faces)
        weighted = reference * factor
        scale = torch.linalg.vector_norm(weighted)
        normalized = weighted.reshape(-1) / scale
        centered = normalized - response_mean
        coefficients = basis @ centered
        for rank in ranks:
            reconstructed = response_mean
            if rank:
                reconstructed = reconstructed + basis[:rank].T @ coefficients[:rank]
            prediction = (reconstructed.reshape(80, 13_902, 3) * scale) / factor
            error = torch.linalg.vector_norm((prediction - reference) * factor)
            error = error / torch.clamp(torch.linalg.vector_norm(weighted), min=1e-12)
            metrics = extended_case_metrics(
                prediction,
                reference,
                case_weights.to(device),
                normals.to(device),
            )
            rows[str(rank)].append(metrics)
            weighted_errors[str(rank)].append(float(error.item()))
        if case_index % 10 == 0 or case_index == 73:
            print(json.dumps({"stage": "oracle_validation", "cases": case_index}), flush=True)
    aggregate: dict[str, dict[str, float]] = {}
    for rank in ranks:
        key = str(rank)
        aggregate[key] = {
            metric: sum(row[metric] for row in rows[key]) / len(rows[key])
            for metric in rows[key][0]
        }
        aggregate[key]["reference_weighted_oracle_relative_l2"] = sum(
            weighted_errors[key]
        ) / len(weighted_errors[key])
    return {
        "aggregate_by_rank": aggregate,
        "per_case_without_identifiers_by_rank": rows,
        "validation_case_count": len(validation_records),
    }


def _load_records(
    config: Mapping[str, Any],
    transient_path: Path,
    steady_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    train_audit_public_path: Path,
    train_audit_private_path: Path,
) -> tuple[Sequence[Mapping[str, Any]], Sequence[Mapping[str, Any]], torch.Tensor, torch.Tensor, torch.Tensor]:
    source = config["source"]
    checks = (
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (steady_path, source["steady_norm_bytes"], source["steady_norm_sha256"], "steady"),
        (public_split_path, None, config["split"]["public_result_sha256"], "public_split"),
        (private_split_path, None, config["split"]["private_manifest_sha256"], "private_split"),
        (train_audit_public_path, None, config["split"]["train_audit_public_sha256"], "audit_public"),
        (train_audit_private_path, None, config["split"]["train_audit_private_sha256"], "audit_private"),
    )
    for path, size, digest, label in checks:
        _require(path.is_file() and (size is None or path.stat().st_size == size), f"{label}_identity")
        _require(file_sha256(path) == digest, f"{label}_sha256")
    public_split = json.loads(public_split_path.read_text(encoding="utf-8"))
    private_split = json.loads(private_split_path.read_text(encoding="utf-8"))
    audit_public = json.loads(train_audit_public_path.read_text(encoding="utf-8"))
    audit_private = json.loads(train_audit_private_path.read_text(encoding="utf-8"))
    _require(audit_public.get("integrity_pass") is True and audit_public.get("test_opened") is False, "audit_public")
    _require(audit_private.get("validation_test_or_extra_statistics_included") is False, "audit_private")
    buckets = validate_split_evidence(config, public_split, private_split)
    train_order = [str(value) for value in audit_private.get("loader_order_case_ids", [])]
    _require(
        len(train_order) == 584
        and _ordered_digest(train_order) == config["split"]["train_loader_order_sha256"]
        and set(train_order) == set(buckets["train"]),
        "train_order",
    )
    _require(
        _ordered_digest(buckets["validation"])
        == config["split"]["validation_loader_order_sha256"],
        "validation_order",
    )
    steady = safe_torch_load(steady_path, torch)
    transient = safe_torch_load(transient_path, torch)
    labels = [str(value) for value in steady["label"]]
    _require(labels == ["x", "y", "z", "x_normal", "y_normal", "z_normal", "wss_x", "wss_y", "wss_z"], "labels")
    mean = steady["tensor_norm"]["mean"].detach().cpu().to(torch.float32).reshape(-1)
    std = steady["tensor_norm"]["std"].detach().cpu().to(torch.float32).reshape(-1)
    _require(mean.numel() == std.numel() == 9 and bool((std > 0).all().item()), "normalizer")
    ordered, indexed = index_case_records(transient["registered_data_list"])
    _require(ordered == [str(value) for value in transient["mesh_data"]["cases"]], "case_order")
    train = selected_training_records(
        indexed, train_order, buckets["validation"] + buckets["test"] + buckets["extra"]
    )
    validation = selected_training_records(
        indexed, buckets["validation"], train_order + buckets["test"] + buckets["extra"]
    )
    faces = transient["mesh_data"]["faces_list"][0].detach().cpu().to(torch.int64)
    return train, validation, mean, std, faces


def run_oracle(
    config: Mapping[str, Any],
    paths: Mapping[str, Path],
    result_path: Path,
    basis_path: Path,
    provenance: Mapping[str, str],
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    device = torch.device("cuda")
    torch.manual_seed(1103)
    torch.cuda.manual_seed_all(1103)
    torch.use_deterministic_algorithms(True, warn_only=True)
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    train, validation, mean, std, faces = _load_records(
        config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
    )
    weights = reference_vertex_weights(train, mean, std, faces)
    maximum_rank = int(config["representation"]["maximum_rank"])
    ranks = [int(value) for value in config["representation"]["rank_grid"]]
    fitted = fit_response_basis(train, weights, mean, std, maximum_rank, device)
    evaluation = evaluate_oracle(validation, fitted, mean, std, faces, ranks, device)
    basis_payload = {
        "schema_version": "aurora.private.aneug_release_730_response_basis.v1",
        "protocol_id": config["protocol_id"],
        "reference_weights": fitted["reference_weights"].cpu(),
        "train_scales": fitted["train_scales"].cpu(),
        "mean": fitted["mean"].cpu(),
        "basis": fitted["basis"].cpu(),
        "eigenvalues": fitted["eigenvalues"].cpu(),
        "explained_variance": fitted["explained_variance"].cpu(),
        "orthogonality_error": float(fitted["orthogonality_error"].item()),
        "phases": 80,
        "nodes": 13_902,
        "train_cases": 584,
        "validation_loader_order_sha256": config["split"]
        ["validation_loader_order_sha256"],
        "case_ids_included": False,
        **provenance,
    }
    _strict_atomic_torch_save(basis_path, basis_payload)
    result = {
        "schema_version": "aurora.private.aneug_release_730_response_oracle_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "evidence_role": "train_basis_validation_oracle_not_learned_model_performance",
        "rank_grid": ranks,
        "explained_variance_by_rank": {
            str(rank): 0.0 if rank == 0 else float(fitted["explained_variance"][rank - 1].item())
            for rank in ranks
        },
        "orthogonality_error": float(fitted["orthogonality_error"].item()),
        "evaluation": evaluation,
        "basis_bytes": basis_path.stat().st_size,
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "train_case_count": 584,
        "validation_case_count": 73,
        "validation_case_digest": config["split"]["validation_case_digest"],
        "validation_loader_order_sha256": config["split"]
        ["validation_loader_order_sha256"],
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "oracle_uses_true_validation_amplitude_and_coefficients": True,
        "learned_predictor": False,
        "rank_selected": False,
        "hard_tangent_projection": False,
        "hard_periodic_closure": False,
        "case_ids_included": False,
        "development_only": True,
        "paper_performance_claim": False,
        **provenance,
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--basis", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    required = (
        args.activation,
        args.expected_commit,
        args.transient,
        args.steady,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.result,
        args.basis,
    )
    _require(all(value is not None for value in required), "execution_arguments")
    activation = validate_activation(args.activation, config, args.expected_commit)
    provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "processed_v5_sha256": config["source"]["processed_v5_sha256"],
        "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        "direct_baseline_terminal_record_sha256": activation[
            "direct_baseline_terminal_record_sha256"
        ],
    }
    run_oracle(
        config,
        {
            "transient": args.transient,
            "steady": args.steady,
            "public_split": args.public_split,
            "private_split": args.private_split,
            "train_audit_public": args.train_audit_public,
            "train_audit_private": args.train_audit_private,
        },
        args.result,
        args.basis,
        provenance,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
