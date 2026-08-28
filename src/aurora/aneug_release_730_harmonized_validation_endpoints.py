"""Common-floor endpoint re-evaluation for the three frozen direct controls.

The job performs no training or selection. It derives the OSI support floor
from the 584 training references, evaluates the exact frozen Graph U-Net,
GHD--GPS and Transolver checkpoints on the same ordered 73 validation cases,
and recomputes every endpoint with one area-weighted physical-field kernel.
Locked-test and processed-only-extra fields have no input path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_processed_v4_d13c_functional_finetune import train_wss_rms
from aurora.aneug_release_730_ghd_gps_baseline import (
    Release730GHDGPSUNet,
    _to_device,
    extended_case_metrics,
    load_config as load_ghd_config,
    load_development_data as load_ghd_data,
)
from aurora.aneug_release_730_official_graphunet_baseline import (
    _predict_normalized,
    build_released_model,
    load_config as load_graph_config,
    load_development_data as load_graph_data,
)
from aurora.aneug_release_730_transolver_baseline import (
    Release730FullCycleTransolver,
    load_config as load_transolver_config,
)


class HarmonizedValidationEndpointError(RuntimeError):
    """Raised when frozen-model endpoint evidence is not comparable."""


DIRECT_LABELS = (
    "released_graph_unet_adapter",
    "ghd_gps_unet",
    "transolver",
)
TABLE_METRICS = (
    "field_relative_l2",
    "mean_wss_vector_error",
    "tawss_normalized_absolute_error",
    "osi_mae",
)
DIAGNOSTIC_METRICS = ("osi_coverage",)
ALL_METRICS = TABLE_METRICS + DIAGNOSTIC_METRICS
RESULT_CONTRACTS = {
    "released_graph_unet_adapter": (
        "aurora.aneug_release_730_graphunet.private_result.v1",
        "aneug_release_730_official_graphunet_baseline_v1",
        "complete_validation_development",
    ),
    "ghd_gps_unet": (
        "aurora.private.aneug_release_730_ghd_gps_result.v1",
        "aneug_release_730_ghd_gps_baseline_v1",
        "complete",
    ),
    "transolver": (
        "aurora.private.aneug_release_730_transolver_result.v1",
        "aneug_release_730_transolver_baseline_v1",
        "complete",
    ),
}
CHECKPOINT_CONTRACTS = {
    "released_graph_unet_adapter": (
        "aurora.aneug_release_730_graphunet.private_best.v1",
        "aneug_release_730_official_graphunet_baseline_v1",
    ),
    "ghd_gps_unet": (
        "aurora.private.aneug_release_730_ghd_gps_best.v1",
        "aneug_release_730_ghd_gps_baseline_v1",
    ),
    "transolver": (
        "aurora.private.aneug_release_730_transolver_best.v1",
        "aneug_release_730_transolver_baseline_v1",
    ),
}


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise HarmonizedValidationEndpointError(label)


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
    return digest.hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(dict(payload), handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_harmonized_validation_endpoints.v1"
        and config.get("protocol_id")
        == "aneug_release_730_harmonized_validation_endpoints_v1"
        and config.get("status")
        == "prepared_non_executable_until_three_frozen_direct_controls_and_private_activation",
        "config_identity",
    )
    source = config["source"]
    _require(
        source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae"
        and source["steady_norm_bytes"] == 9_632_510_050
        and source["steady_norm_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f"
        and all(
            _is_sha256(source[key])
            for key in (
                "graph_config_sha256",
                "ghd_gps_config_sha256",
                "transolver_config_sha256",
            )
        ),
        "source",
    )
    split = config["split"]
    _require(
        (split["train_cases"], split["validation_cases"], split["locked_test_cases"], split["processed_only_extra_cases"])
        == (584, 73, 73, 79)
        and split["validation_loader_order_sha256"]
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30"
        and split["validation_case_digest"]
        == "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024"
        and split["read_train_fields_for_floor_only"] is True
        and split["read_validation_fields"] is True
        and split["read_locked_test_fields"] is False
        and split["read_processed_only_extra_fields"] is False,
        "split",
    )
    evaluation = config["evaluation"]
    _require(
        tuple(evaluation["models"]) == DIRECT_LABELS
        and tuple(evaluation["metrics"]) == ALL_METRICS
        and evaluation["reference_tawss_floor_multiplier"] == 1e-4
        and evaluation["osi_reference_support"]
        == "reference_TAWSS_above_common_train_frozen_floor"
        and evaluation["reference_support_weighting"]
        == "normalized_mesh_vertex_area"
        and evaluation["invalid_prediction_osi_error"] == 0.5
        and evaluation["all_endpoints_recomputed_together"] is True
        and evaluation["case_identifiers_in_result"] is False
        and evaluation["model_or_checkpoint_selection"] is False
        and evaluation["absolute_performance_threshold"] is None
        and evaluation["automatic_paper_claim"] is False,
        "evaluation",
    )
    runtime = config["runtime"]
    authorization = config["authorization"]
    _require(
        runtime["server"] == "introai9"
        and runtime["excluded_server"] == "junjinyong"
        and runtime["ngpus"] == 1
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        "runtime",
    )
    _require(
        authorization["execute_now"] is False
        and authorization["requires_three_terminal_direct_controls"] is True
        and authorization["requires_exact_frozen_checkpoint_sha256"] is True
        and authorization["requires_private_activation"] is True
        and authorization["training"] is False
        and authorization["optimizer_or_scheduler_state_change"] is False
        and authorization["checkpoint_or_model_state_change"] is False
        and authorization["read_locked_test"] is False
        and authorization["read_processed_only_extra"] is False
        and authorization["paper_claim"] is False,
        "authorization",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(value)
    return value


def validate_activation(
    activation_path: Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(activation_path.read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_harmonized_validation_endpoints_activation.v1"
        and activation.get("protocol_id") == config["protocol_id"]
        and activation.get("status")
        == "activated_after_three_terminal_frozen_direct_controls"
        and activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_identity",
    )
    for key in ("source_result_sha256", "source_checkpoint_sha256", "terminal_record_sha256"):
        value = activation.get(key)
        _require(
            isinstance(value, Mapping)
            and tuple(value) == DIRECT_LABELS
            and all(_is_sha256(value[label]) for label in DIRECT_LABELS),
            f"activation_{key}",
        )
    _require(
        activation.get("validation_case_digest") == config["split"]["validation_case_digest"]
        and activation.get("validation_loader_order_sha256")
        == config["split"]["validation_loader_order_sha256"]
        and activation.get("read_train_fields_for_floor_only") is True
        and activation.get("read_validation_fields") is True
        and activation.get("read_locked_test_or_extra") is False
        and activation.get("training") is False
        and activation.get("model_or_checkpoint_selection") is False
        and activation.get("paper_claim") is False
        and activation.get("single_materialization") is True
        and activation.get("server") == "introai9"
        and activation.get("excluded_server") == "junjinyong",
        "activation_boundary",
    )
    return activation


def common_case_endpoints(
    prediction: torch.Tensor,
    reference: torch.Tensor,
    weights: torch.Tensor,
    normals: torch.Tensor,
    reference_tawss_floor: float,
) -> dict[str, float]:
    """Evaluate one cycle with a shared physical and support definition."""

    _require(
        prediction.shape == reference.shape
        and prediction.ndim == 3
        and prediction.shape[0] == 80
        and prediction.shape[-1] == 3
        and weights.shape == (prediction.shape[1],)
        and normals.shape == (prediction.shape[1], 3)
        and math.isfinite(float(reference_tawss_floor))
        and float(reference_tawss_floor) > 0.0,
        "case_shape",
    )
    metrics = extended_case_metrics(prediction, reference, weights, normals)
    reference_tawss = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0)
    prediction_tawss = torch.linalg.vector_norm(prediction, dim=-1).mean(dim=0)
    support = reference_tawss > float(reference_tawss_floor)
    support_area = torch.sum(weights[support])
    total_area = torch.sum(weights)
    _require(
        bool(torch.isfinite(reference_tawss).all().item())
        and bool(torch.isfinite(weights).all().item())
        and bool((weights >= 0.0).all().item())
        and bool((support_area > 0.0).item())
        and bool((total_area > 0.0).item()),
        "reference_support",
    )
    valid = support & torch.isfinite(prediction_tawss) & (prediction_tawss > 0.0)
    reference_mean = reference.mean(dim=0)
    prediction_mean = prediction.mean(dim=0)
    reference_osi = 0.5 * (
        1.0
        - torch.linalg.vector_norm(reference_mean, dim=-1)
        / torch.clamp(reference_tawss, min=1e-12)
    )
    prediction_osi = 0.5 * (
        1.0
        - torch.linalg.vector_norm(prediction_mean, dim=-1)
        / torch.clamp(prediction_tawss, min=1e-12)
    )
    error = torch.full_like(reference_osi, 0.5)
    error[valid] = torch.abs(prediction_osi[valid] - reference_osi[valid])
    metrics["osi_mae"] = float(torch.sum(weights[support] * error[support]).div(support_area).item())
    metrics["osi_coverage"] = float(torch.sum(weights[valid]).div(support_area).item())
    metrics["osi_reference_support_fraction"] = float(support_area.div(total_area).item())
    _require(
        all(math.isfinite(float(metrics[key])) and float(metrics[key]) >= 0.0 for key in ALL_METRICS)
        and 0.0 <= metrics["osi_coverage"] <= 1.0
        and 0.0 <= metrics["osi_reference_support_fraction"] <= 1.0,
        "case_metrics",
    )
    return {key: float(value) for key, value in metrics.items()}


def reference_support_area_fraction(
    reference: torch.Tensor, weights: torch.Tensor, reference_tawss_floor: float
) -> float:
    """Compute the model-independent support once on CPU for one case."""

    reference = reference.detach().cpu().to(torch.float64)
    weights = weights.detach().cpu().to(torch.float64)
    _require(
        reference.ndim == 3
        and reference.shape[0] == 80
        and reference.shape[-1] == 3
        and weights.shape == (reference.shape[1],)
        and bool(torch.isfinite(reference).all().item())
        and bool(torch.isfinite(weights).all().item())
        and bool((weights >= 0.0).all().item())
        and bool((weights.sum() > 0.0).item())
        and math.isfinite(float(reference_tawss_floor))
        and float(reference_tawss_floor) > 0.0,
        "reference_support_input",
    )
    support = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0) > float(
        reference_tawss_floor
    )
    fraction = torch.sum(weights[support]) / torch.sum(weights)
    value = float(fraction.item())
    _require(math.isfinite(value) and 0.0 <= value <= 1.0, "reference_support_value")
    return value


def _aggregate_rows(rows: Sequence[Mapping[str, float]]) -> dict[str, float]:
    _require(len(rows) == 73, "aggregate_case_count")
    keys = tuple(rows[0])
    _require(all(tuple(row) == keys for row in rows), "aggregate_keys")
    return {key: sum(float(row[key]) for row in rows) / len(rows) for key in keys}


def assemble_result(
    rows_by_model: Mapping[str, Sequence[Mapping[str, float]]],
    *,
    reference_tawss_floor: float,
    activation: Mapping[str, Any],
    provenance: Mapping[str, Any],
    elapsed_seconds: float,
    peak_gpu_memory_bytes: int,
) -> dict[str, Any]:
    _require(tuple(rows_by_model) == DIRECT_LABELS, "model_order")
    parsed = {
        label: [dict(row) for row in rows_by_model[label]] for label in DIRECT_LABELS
    }
    for label in DIRECT_LABELS:
        _require(len(parsed[label]) == 73, f"{label}_case_count")
        for row in parsed[label]:
            _require(
                all(metric in row for metric in ALL_METRICS)
                and "osi_reference_support_fraction" in row,
                f"{label}_metric_contract",
            )
    support = [
        float(row["osi_reference_support_fraction"])
        for row in parsed[DIRECT_LABELS[0]]
    ]
    for label in DIRECT_LABELS[1:]:
        _require(
            all(
                float(row["osi_reference_support_fraction"]) == support[index]
                for index, row in enumerate(parsed[label])
            ),
            f"{label}_reference_support_mismatch",
        )
    source_results = activation["source_result_sha256"]
    source_checkpoints = activation["source_checkpoint_sha256"]
    controls = {}
    for label in DIRECT_LABELS:
        controls[label] = {
            "source_checkpoint_sha256": source_checkpoints[label],
            "frozen_checkpoint_loaded_weights_only": True,
            "training_performed": False,
            "aggregate": _aggregate_rows(parsed[label]),
            "per_case_without_identifiers": parsed[label],
        }
    return {
        "schema_version": "aurora.private.aneug_release_730_harmonized_validation_endpoints.v1",
        "protocol_id": "aneug_release_730_harmonized_validation_endpoints_v1",
        "status": "complete_common_train_floor_validation_re_evaluation",
        "evidence_stage": "single_seed_development_validation",
        "validation_case_count": 73,
        "reference_tawss_floor": float(reference_tawss_floor),
        "source_result_sha256": dict(source_results),
        "controls": controls,
        "osi_reference_support": {
            "definition": "reference_TAWSS_above_common_train_frozen_floor",
            "model_independent": True,
            "area_weighted": True,
            "case_count": 73,
            "per_case_area_fraction_without_identifiers": support,
            "case_mean_area_fraction": sum(support) / len(support),
            "distinct_from_model_specific_prediction_valid_coverage": True,
        },
        "training_performed": False,
        "optimizer_or_scheduler_state_changed": False,
        "checkpoint_or_model_state_changed": False,
        "predictions_generated_from_exact_frozen_checkpoints": True,
        "all_endpoints_recomputed_with_common_evaluator": True,
        "model_or_checkpoint_selection": False,
        "case_identifiers_included": False,
        "locked_test_or_extra_read": False,
        "paper_claim": False,
        "elapsed_seconds": float(elapsed_seconds),
        "peak_gpu_memory_bytes": int(peak_gpu_memory_bytes),
        **dict(provenance),
    }


def _load_checkpoint(
    label: str, path: Path, expected_sha256: str
) -> Mapping[str, Any]:
    _require(path.is_file() and file_sha256(path) == expected_sha256, f"{label}_checkpoint_hash")
    value = torch.load(str(path), map_location="cpu", weights_only=True)
    schema, protocol = CHECKPOINT_CONTRACTS[label]
    _require(
        isinstance(value, Mapping)
        and value.get("schema_version") == schema
        and value.get("protocol_id") == protocol
        and value.get("seed") == 1103
        and isinstance(value.get("model_state_dict"), Mapping),
        f"{label}_checkpoint_identity",
    )
    return value


def _validate_source_result(
    label: str, path: Path, expected_sha256: str
) -> Mapping[str, Any]:
    _require(path.is_file() and file_sha256(path) == expected_sha256, f"{label}_result_hash")
    value = json.loads(path.read_text(encoding="utf-8"))
    schema, protocol, status = RESULT_CONTRACTS[label]
    _require(
        value.get("schema_version") == schema
        and value.get("protocol_id") == protocol
        and value.get("status") == status
        and value.get("validation_case_count") == 73
        and value.get("case_ids_included") is False
        and value.get("processed_only_extra_field_case_count_read") == 0,
        f"{label}_result_identity",
    )
    if label == "released_graph_unet_adapter":
        _require(value.get("test_field_case_count_read") == 0, f"{label}_sealed")
    else:
        _require(value.get("locked_test_field_case_count_read") == 0, f"{label}_sealed")
    return value


def run_evaluation(
    *,
    config: Mapping[str, Any],
    activation: Mapping[str, Any],
    graph_config: Mapping[str, Any],
    ghd_config: Mapping[str, Any],
    transolver_config: Mapping[str, Any],
    paths: Mapping[str, Path],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    _require(torch.cuda.is_available(), "cuda_required")
    torch.set_num_threads(4)
    device = torch.device("cuda")
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    for label in DIRECT_LABELS:
        _validate_source_result(
            label, paths[f"{label}_result"], activation["source_result_sha256"][label]
        )
        terminal = json.loads(paths[f"{label}_terminal"].read_text(encoding="utf-8"))
        _require(
            file_sha256(paths[f"{label}_terminal"])
            == activation["terminal_record_sha256"][label]
            and terminal.get("exit_code") == 0
            and terminal.get("complete") is True,
            f"{label}_terminal",
        )

    train, validation, topology, wss_scale = load_ghd_data(
        ghd_config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
    )
    reference_tawss_floor = train_wss_rms(train) * float(
        config["evaluation"]["reference_tawss_floor_multiplier"]
    )
    del train
    common_reference_support = [
        reference_support_area_fraction(
            case["wss"], case["vertex_weights"], reference_tawss_floor
        )
        for case in validation
    ]

    rows_by_model: dict[str, list[dict[str, float]]] = {}
    ghd_checkpoint = _load_checkpoint(
        "ghd_gps_unet",
        paths["ghd_gps_unet_checkpoint"],
        activation["source_checkpoint_sha256"]["ghd_gps_unet"],
    )
    ghd_model = Release730GHDGPSUNet(
        topology,
        width=int(ghd_config["architecture"]["width"]),
        heads=int(ghd_config["architecture"]["attention_heads"]),
    ).to(device)
    ghd_model.load_state_dict(ghd_checkpoint["model_state_dict"], strict=True)
    ghd_model.eval()
    rows_by_model["ghd_gps_unet"] = []
    with torch.no_grad():
        for cpu_case in validation:
            case = _to_device(cpu_case, device)
            prediction = ghd_model(case) * float(wss_scale)
            rows_by_model["ghd_gps_unet"].append(
                common_case_endpoints(
                    prediction,
                    case["wss"],
                    case["vertex_weights"],
                    case["normals"],
                    reference_tawss_floor,
                )
            )
    del ghd_model, ghd_checkpoint
    torch.cuda.empty_cache()

    transolver_checkpoint = _load_checkpoint(
        "transolver",
        paths["transolver_checkpoint"],
        activation["source_checkpoint_sha256"]["transolver"],
    )
    architecture = transolver_config["architecture"]
    transolver = Release730FullCycleTransolver(
        width=int(architecture["width"]),
        heads=int(architecture["attention_heads"]),
        blocks=int(architecture["blocks"]),
        slices=int(architecture["slices"]),
        mlp_ratio=int(architecture["mlp_ratio"]),
        dropout=float(architecture["dropout"]),
        output_phases=int(architecture["output_phases"]),
    ).to(device)
    transolver.load_state_dict(transolver_checkpoint["model_state_dict"], strict=True)
    transolver.eval()
    rows_by_model["transolver"] = []
    with torch.no_grad():
        for cpu_case in validation:
            case = _to_device(cpu_case, device)
            prediction = transolver(case) * float(wss_scale)
            rows_by_model["transolver"].append(
                common_case_endpoints(
                    prediction,
                    case["wss"],
                    case["vertex_weights"],
                    case["normals"],
                    reference_tawss_floor,
                )
            )
    del transolver, transolver_checkpoint
    torch.cuda.empty_cache()

    graph_train, graph_validation, graph_topology, mean, std = load_graph_data(
        graph_config,
        paths["transient"],
        paths["steady"],
        paths["public_split"],
        paths["private_split"],
        paths["train_audit_public"],
        paths["train_audit_private"],
    )
    del graph_train
    graph_checkpoint = _load_checkpoint(
        "released_graph_unet_adapter",
        paths["released_graph_unet_adapter_checkpoint"],
        activation["source_checkpoint_sha256"]["released_graph_unet_adapter"],
    )
    graph_model = build_released_model(
        paths["official_root"],
        graph_config,
        {key: value.to(device) for key, value in graph_topology.items()},
    ).to(device)
    graph_model.load_state_dict(graph_checkpoint["model_state_dict"], strict=True)
    graph_model.eval()
    waveform = torch.zeros((1, 80, 1), dtype=torch.float32, device=device)
    mean_wss = mean[6:9].reshape(1, 1, 3)
    std_wss = std[6:9].reshape(1, 1, 3)
    graph_batch = int(graph_config["optimization"]["physical_snapshot_batch_size"])
    rows_by_model["released_graph_unet_adapter"] = []
    with torch.no_grad():
        for case_index, graph_case in enumerate(graph_validation):
            chunks = []
            pairs = [(case_index, phase) for phase in range(80)]
            for start in range(0, 80, graph_batch):
                prediction, _target, _weights = _predict_normalized(
                    graph_model,
                    graph_validation,
                    pairs[start : start + graph_batch],
                    device,
                    waveform,
                )
                chunks.append(prediction.detach().cpu())
            prediction_physical = torch.cat(chunks, dim=0) * (
                std_wss + float(graph_config["optimization"]["physical_metric_decoder_epsilon"])
            ) + mean_wss
            reference = validation[case_index]
            graph_reference_physical = graph_case["target_normalized"] * (
                std_wss + float(graph_config["optimization"]["physical_metric_decoder_epsilon"])
            ) + mean_wss
            _require(
                torch.equal(graph_reference_physical, reference["wss"]),
                "graph_common_reference_identity",
            )
            rows_by_model["released_graph_unet_adapter"].append(
                common_case_endpoints(
                    prediction_physical,
                    reference["wss"],
                    reference["vertex_weights"],
                    reference["normals"],
                    reference_tawss_floor,
                )
            )
    del graph_model, graph_checkpoint
    torch.cuda.empty_cache()
    for label in DIRECT_LABELS:
        for index, value in enumerate(common_reference_support):
            rows_by_model[label][index]["osi_reference_support_fraction"] = value
    ordered_rows = {label: rows_by_model[label] for label in DIRECT_LABELS}
    return assemble_result(
        ordered_rows,
        reference_tawss_floor=reference_tawss_floor,
        activation=activation,
        provenance=provenance,
        elapsed_seconds=time.monotonic() - started,
        peak_gpu_memory_bytes=int(torch.cuda.max_memory_allocated()),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--graph-config", type=Path)
    parser.add_argument("--ghd-gps-config", type=Path)
    parser.add_argument("--transolver-config", type=Path)
    for label in DIRECT_LABELS:
        option = label.replace("_", "-")
        parser.add_argument(f"--{option}-result", type=Path)
        parser.add_argument(f"--{option}-terminal", type=Path)
        parser.add_argument(f"--{option}-checkpoint", type=Path)
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
    parser.add_argument("--official-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    required = (
        args.activation,
        args.expected_commit,
        args.graph_config,
        args.ghd_gps_config,
        args.transolver_config,
        args.transient,
        args.steady,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.official_root,
        args.output,
    )
    _require(all(value is not None for value in required), "execution_arguments")
    paths: dict[str, Path] = {
        "transient": args.transient,
        "steady": args.steady,
        "public_split": args.public_split,
        "private_split": args.private_split,
        "train_audit_public": args.train_audit_public,
        "train_audit_private": args.train_audit_private,
        "official_root": args.official_root,
    }
    for label in DIRECT_LABELS:
        for suffix in ("result", "terminal", "checkpoint"):
            value = getattr(args, f"{label}_{suffix}")
            _require(value is not None, f"{label}_{suffix}_argument")
            paths[f"{label}_{suffix}"] = value
    for path, key in (
        (args.graph_config, "graph_config_sha256"),
        (args.ghd_gps_config, "ghd_gps_config_sha256"),
        (args.transolver_config, "transolver_config_sha256"),
    ):
        _require(file_sha256(path) == config["source"][key], key)
    activation = validate_activation(args.activation, config, str(args.expected_commit))
    result = run_evaluation(
        config=config,
        activation=activation,
        graph_config=load_graph_config(args.graph_config),
        ghd_config=load_ghd_config(args.ghd_gps_config),
        transolver_config=load_transolver_config(args.transolver_config),
        paths=paths,
        provenance={
            "public_commit": str(args.expected_commit),
            "config_sha256": file_sha256(args.config),
            "activation_sha256": file_sha256(args.activation),
            "validation_case_digest": config["split"]["validation_case_digest"],
            "validation_loader_order_sha256": config["split"]["validation_loader_order_sha256"],
        },
    )
    _atomic_json(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
