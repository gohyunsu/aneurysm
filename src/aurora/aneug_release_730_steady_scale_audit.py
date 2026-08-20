"""Audit eligible steady-WSS scale for a later matched auxiliary objective.

The audit reads only the leakage-audited steady rows and a previously frozen
train-transient aggregate.  It selects no model or loss weight and never reads
transient fields, validation, locked test, or processed-only extras.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_release_730_steady_training_scope import (
    file_sha256,
    load_config as load_scope_config,
    load_scope_files,
)


class SteadyScaleAuditError(RuntimeError):
    """Raised when data identity, read scope, or numerical checks fail."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise SteadyScaleAuditError(reason)


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_steady_scale_audit.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id") == "aneug_release_730_steady_scale_audit_v1",
        "protocol_id",
    )
    _require(
        config.get("status")
        == "prepared_non_executable_until_quality_activation_and_oracle_terminal",
        "status",
    )
    source = config["source"]
    _require(
        source["steady_bytes"] == 9_632_510_050
        and source["steady_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f"
        and source["public_overlap_result_sha256"]
        == "b3a118bae156a1dbc6c838b923a594f9b0f452a40f34b8bccb6bc396d28ba397"
        and source["private_overlap_result_sha256"]
        == "52219b9a7161f0932a4ed80020a339510474431b67e168741426c2a12e5092ef"
        and source["steady_scope_config_sha256"]
        == "782285c95a7eed7ead983b298426606bdb6d9258d076908c9c65a0ad3d8aa5cf"
        and source["private_train_audit_sha256"]
        == "ce1dd6d2852e290fbe187ac062af155f522cd4b8a82c1580b5430d15ed519385",
        "source",
    )
    scope = config["scope"]
    _require(
        (
            scope["processed_steady_rows"],
            scope["eligible_steady_rows"],
            scope["nodes"],
            scope["channels"],
            scope["wss_channels"],
            scope["decoder_epsilon"],
        )
        == (14_392, 13_985, 13_902, 9, [6, 7, 8], 0.00001),
        "scope",
    )
    _require(
        scope["eligible_case_digest"]
        == "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc",
        "eligible_digest",
    )
    audit = config["audit"]
    _require(
        audit["accumulator_dtype"] == "float64"
        and audit["block_rows"] == 32
        and audit["case_vector_rms_quantiles"] == [0.05, 0.5, 0.95]
        and audit["report_component_mean_and_population_std"] is True
        and audit["report_steady_to_transient_scale_ratio"] is True,
        "audit",
    )
    _require(
        audit["absolute_materiality_threshold"] is None
        and audit["automatic_loss_weight"] is False
        and audit["model_fit_or_prediction"] is False,
        "decision_boundary",
    )
    execution = config["execution"]
    _require(
        execution["server"] == "introai9"
        and execution["excluded_server"] == "junjinyong"
        and (execution["ncpus"], execution["memory_gb"], execution["ngpus"])
        == (4, 64, 0)
        and execution["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        "execution",
    )
    authorization = config["authorization"]
    _require(
        authorization[
            "execute_after_quality_private_activation_and_response_oracle_terminal"
        ]
        is True
        and authorization["read_eligible_steady_wss"] is True,
        "execution_authority",
    )
    for key in (
        "read_transient_wss",
        "read_validation_test_or_extra",
        "use_gpu",
        "fit_or_select_model",
        "select_loss_weight",
        "publish_numeric_result",
        "paper_performance_claim",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")


def validate_activation_payload(
    activation: Mapping[str, Any], config: Mapping[str, Any], expected_commit: str
) -> None:
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_steady_scale_audit_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(
        activation.get("authorized_stage") == "single_eligible_steady_cpu_scale_audit",
        "activation_stage",
    )
    _require(bool(activation.get("response_oracle_terminal_record_sha256")), "oracle_terminal")
    _require(
        activation.get("private_overlap_result_sha256")
        == config["source"]["private_overlap_result_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["source"]["private_train_audit_sha256"],
        "activation_evidence",
    )
    _require(activation.get("read_transient_validation_test_or_extra") is False, "sealed_scope")
    _require(activation.get("use_gpu") is False, "activation_gpu")


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> None:
    validate_activation_payload(
        json.loads(Path(path).read_text(encoding="utf-8")), config, expected_commit
    )


def _quantile(values: Any, probability: float, torch: Any) -> float:
    _require(values.numel() > 0 and 0.0 <= probability <= 1.0, "quantile")
    return float(torch.quantile(values, probability).item())


def eligible_steady_scale(
    archive: Mapping[str, Any],
    indices: Sequence[int],
    train_audit: Mapping[str, Any],
    torch: Any,
    *,
    expected_nodes: int | None = 13_902,
    block_rows: int = 32,
    decoder_epsilon: float = 0.00001,
) -> dict[str, Any]:
    """Compute float64 physical-WSS moments over only eligible steady rows."""

    tensor = archive["tensor"]
    _require(tensor.ndim == 3 and tensor.shape[2] == 9, "tensor_shape")
    nodes = int(tensor.shape[1])
    _require(expected_nodes is None or nodes == expected_nodes, "node_count")
    normalized_indices = tuple(int(index) for index in indices)
    _require(
        len(normalized_indices) > 0
        and len(set(normalized_indices)) == len(normalized_indices)
        and min(normalized_indices) >= 0
        and max(normalized_indices) < tensor.shape[0],
        "indices",
    )
    _require(block_rows > 0 and decoder_epsilon >= 0.0, "parameters")
    norm = archive["tensor_norm"]
    decoder_mean = norm["mean"].detach().cpu().to(torch.float64).reshape(-1)
    decoder_std = norm["std"].detach().cpu().to(torch.float64).reshape(-1)
    _require(
        decoder_mean.numel() == decoder_std.numel() == 9
        and bool(torch.isfinite(decoder_mean).all().item())
        and bool(torch.isfinite(decoder_std).all().item())
        and bool((decoder_std > 0).all().item()),
        "decoder",
    )
    mean = decoder_mean[6:9]
    std = decoder_std[6:9]
    component_sum = torch.zeros(3, dtype=torch.float64)
    component_square_sum = torch.zeros(3, dtype=torch.float64)
    case_rms: list[Any] = []
    count = 0
    for start in range(0, len(normalized_indices), block_rows):
        block = normalized_indices[start : start + block_rows]
        block_index = torch.tensor(block, dtype=torch.int64)
        normalized = tensor.index_select(0, block_index)[:, :, 6:9].detach().cpu()
        _require(bool(torch.isfinite(normalized).all().item()), "nonfinite_stored")
        physical = normalized.to(torch.float64) * (std.reshape(1, 1, 3) + decoder_epsilon)
        physical = physical + mean.reshape(1, 1, 3)
        _require(bool(torch.isfinite(physical).all().item()), "nonfinite_physical")
        component_sum += physical.sum(dim=(0, 1))
        component_square_sum += physical.square().sum(dim=(0, 1))
        case_rms.append(torch.sqrt(physical.square().sum(dim=-1).mean(dim=-1)))
        count += len(block) * nodes
        if expected_nodes == 13_902 and (
            start + len(block) == len(normalized_indices) or (start + len(block)) % 512 == 0
        ):
            print(
                json.dumps(
                    {"stage": "eligible_steady_scale", "rows": start + len(block)}
                ),
                flush=True,
            )
    component_mean = component_sum / count
    component_second_moment = component_square_sum / count
    component_variance = component_second_moment - component_mean.square()
    variance_tolerance = (
        64.0
        * torch.finfo(torch.float64).eps
        * torch.clamp(component_second_moment.max(), min=1.0)
    )
    _require(
        bool((component_variance >= -variance_tolerance).all().item()),
        "negative_variance",
    )
    component_variance = torch.clamp(component_variance, min=0.0)
    component_std = torch.sqrt(component_variance)
    vector_rms = torch.sqrt(component_square_sum.sum() / count)
    cases = torch.cat(case_rms)
    _require(cases.numel() == len(normalized_indices), "case_rms_count")

    _require(
        train_audit.get("schema_version")
        == "aurora.aneug_release_730_train_audit.private_statistics.v1"
        and train_audit.get("train_case_count") == 584
        and train_audit.get("validation_test_or_extra_statistics_included") is False,
        "train_audit",
    )
    transient = train_audit["wss_physical"]
    transient_mean = torch.tensor(transient["mean"], dtype=torch.float64)
    transient_std = torch.tensor(transient["std_population"], dtype=torch.float64)
    _require(transient_mean.shape == transient_std.shape == (3,), "transient_shape")
    transient_rms = torch.sqrt(torch.sum(transient_mean.square() + transient_std.square()))
    ratio = vector_rms / transient_rms
    values = [
        *component_mean.tolist(),
        *component_std.tolist(),
        float(vector_rms.item()),
        float(transient_rms.item()),
        float(ratio.item()),
    ]
    _require(all(math.isfinite(float(value)) for value in values), "nonfinite_result")
    return {
        "eligible_steady_rows": len(normalized_indices),
        "nodes_per_row": nodes,
        "physical_component_mean": [float(value) for value in component_mean.tolist()],
        "physical_component_std_population": [
            float(value) for value in component_std.tolist()
        ],
        "steady_physical_vector_rms": float(vector_rms.item()),
        "transient_train_physical_vector_rms": float(transient_rms.item()),
        "steady_to_transient_vector_rms_ratio": float(ratio.item()),
        "steady_to_transient_squared_scale_ratio": float(ratio.square().item()),
        "steady_case_vector_rms": {
            "minimum": float(cases.min().item()),
            "q05": _quantile(cases, 0.05, torch),
            "median": _quantile(cases, 0.5, torch),
            "q95": _quantile(cases, 0.95, torch),
            "maximum": float(cases.max().item()),
        },
        "decoder_epsilon": float(decoder_epsilon),
        "accumulator_dtype": "float64",
    }


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


def run_audit(
    config: Mapping[str, Any],
    steady_path: Path,
    public_overlap_path: Path,
    private_overlap_path: Path,
    scope_config_path: Path,
    train_audit_path: Path,
    result_path: Path,
    provenance: Mapping[str, Any],
    torch: Any,
) -> dict[str, Any]:
    source = config["source"]
    for path, size, digest, label in (
        (steady_path, source["steady_bytes"], source["steady_sha256"], "steady"),
        (public_overlap_path, None, source["public_overlap_result_sha256"], "public_overlap"),
        (private_overlap_path, None, source["private_overlap_result_sha256"], "private_overlap"),
        (scope_config_path, None, source["steady_scope_config_sha256"], "scope_config"),
        (train_audit_path, None, source["private_train_audit_sha256"], "train_audit"),
    ):
        _require(path.is_file() and (size is None or path.stat().st_size == size), f"{label}_identity")
        _require(file_sha256(path) == digest, f"{label}_sha256")
    archive = safe_torch_load(steady_path, torch)
    scope_config = load_scope_config(scope_config_path)
    indices = load_scope_files(
        scope_config, public_overlap_path, private_overlap_path, archive
    )
    train_audit = json.loads(train_audit_path.read_text(encoding="utf-8"))
    values = eligible_steady_scale(
        archive,
        indices,
        train_audit,
        torch,
        expected_nodes=config["scope"]["nodes"],
        block_rows=config["audit"]["block_rows"],
        decoder_epsilon=config["scope"]["decoder_epsilon"],
    )
    result = {
        "schema_version": "aurora.private.aneug_release_730_steady_scale_audit_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_eligible_steady_descriptive",
        **values,
        **provenance,
        "absolute_materiality_threshold": None,
        "automatic_loss_weight": None,
        "steady_wss_rows_read": len(indices),
        "transient_wss_rows_read": 0,
        "validation_test_or_extra_wss_rows_read": 0,
        "model_fit_or_prediction": False,
        "gpu_used": False,
        "case_ids_included": False,
        "paper_performance_claim": False,
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-overlap", type=Path)
    parser.add_argument("--private-overlap", type=Path)
    parser.add_argument("--scope-config", type=Path)
    parser.add_argument("--private-train-audit", type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    required = (
        args.activation,
        args.expected_commit,
        args.steady,
        args.public_overlap,
        args.private_overlap,
        args.scope_config,
        args.private_train_audit,
        args.result,
    )
    _require(all(value is not None for value in required), "execution_arguments")
    validate_activation(args.activation, config, args.expected_commit)
    import torch

    provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "steady_sha256": config["source"]["steady_sha256"],
        "private_overlap_result_sha256": config["source"]["private_overlap_result_sha256"],
        "private_train_audit_sha256": config["source"]["private_train_audit_sha256"],
        "response_oracle_terminal_record_sha256": json.loads(
            args.activation.read_text(encoding="utf-8")
        )["response_oracle_terminal_record_sha256"],
    }
    run_audit(
        config,
        args.steady,
        args.public_overlap,
        args.private_overlap,
        args.scope_config,
        args.private_train_audit,
        args.result,
        provenance,
        torch,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
