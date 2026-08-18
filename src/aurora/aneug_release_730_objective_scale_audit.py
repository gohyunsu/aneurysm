"""Train-only audit of the released Graph U-Net frame-loss channel scale.

The pinned upstream trainer computes a phasewise population standard deviation
over training cases and surface nodes, averages that deviation over phase, and
rescales frame-MSE residuals by the resulting channel vector.  This utility
reproduces only that statistic on the 584 training fields.  It reads no
validation, locked-test or processed-only-extra field and fits no model.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_release_730_train_audit import (
    _ordered_digest,
    file_sha256,
    index_case_records,
    selected_training_records,
    validate_split_evidence,
)


class ObjectiveScaleAuditError(RuntimeError):
    """Raised when source identity or sealed-read boundaries fail."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ObjectiveScaleAuditError(reason)


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_objective_scale_audit.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_train_only_official_objective_scale_audit_v1",
        "protocol_id",
    )
    _require(
        config.get("status")
        == "prepared_non_executable_until_quality_and_private_activation",
        "status",
    )
    source = config["source"]
    _require(
        source["dataset_revision"] == "9dd418083899deddd93a67f9a6fca7a14304fa36"
        and source["official_code_revision"]
        == "4a090a0f12538deef6fcea88b81afe78ce38152e"
        and source["processed_v5_bytes"] == 33_233_856_917
        and source["processed_v5_sha256"]
        == "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
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
    _require(split["read_train_fields"] is True, "train_read")
    _require(
        split["read_validation_fields"] is False
        and split["read_locked_test_fields"] is False
        and split["read_processed_only_extra_fields"] is False
        and split["test_opened"] is False,
        "sealed_read",
    )
    audit = config["audit"]
    _require(
        audit["stored_wss_channels"] == [6, 7, 8]
        and audit["expected_phases"] == 80
        and audit["expected_nodes"] == 13_902
        and audit["upstream_renormalization_epsilon"] == 0.000001,
        "audit_shape",
    )
    _require(audit["absolute_materiality_threshold"] is None, "threshold")
    _require(audit["automatic_sensitivity_authorization"] is False, "automatic")
    _require(audit["model_fit_or_prediction"] is False, "model")
    execution = config["execution"]
    _require(
        execution["server"] == "introai9"
        and execution["excluded_server"] == "junjinyong"
        and (execution["ncpus"], execution["memory_gb"], execution["ngpus"])
        == (4, 64, 0),
        "execution",
    )
    authorization = config["authorization"]
    _require(authorization["execute_after_quality_and_private_activation"] is True, "execute")
    for key in (
        "read_validation_test_or_extra",
        "use_gpu",
        "fit_or_select_model",
        "stop_or_modify_active_graphunet",
        "publish_numeric_result",
        "paper_performance_claim",
        "maintain_public_site",
    ):
        _require(authorization[key] is False, f"authorization_{key}")


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_objective_scale_audit_activation.v1",
        "activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "activation_protocol")
    _require(
        activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_public",
    )
    _require(activation.get("authorized_stage") == "single_train_only_cpu_audit", "stage")
    _require(activation.get("read_validation_test_or_extra") is False, "activation_scope")
    _require(activation.get("use_gpu") is False, "activation_gpu")
    _require(
        activation.get("private_split_sha256") == config["source"]["private_split_sha256"]
        and activation.get("private_train_audit_sha256")
        == config["source"]["private_train_audit_sha256"],
        "activation_evidence",
    )
    return activation


def upstream_channel_scale(
    records: Sequence[Mapping[str, Any]],
    torch: Any,
    *,
    channels: Sequence[int] = (6, 7, 8),
    expected_phases: int | None = 80,
    expected_nodes: int | None = 13_902,
    renormalization_epsilon: float = 0.000001,
) -> dict[str, Any]:
    """Match upstream `get_transient_components` population-statistic grammar."""

    _require(bool(records), "empty_records")
    first = records[0]["tensor"]
    phases, nodes = int(first.shape[0]), int(first.shape[1])
    _require(
        first.ndim == 3
        and len(channels) == 3
        and max(channels) < first.shape[2]
        and (expected_phases is None or phases == expected_phases)
        and (expected_nodes is None or nodes == expected_nodes),
        "shape",
    )
    _require(renormalization_epsilon >= 0.0, "renormalization_epsilon")
    # Upstream initializes float32 CPU accumulators and adds the stored
    # tensors directly.  The release cache is float32, so retain that
    # arithmetic here instead of silently substituting a float64 estimate.
    total = torch.zeros((phases, len(channels)), dtype=torch.float32)
    squared = torch.zeros_like(total)
    for index, record in enumerate(records, start=1):
        tensor = record["tensor"]
        _require(tuple(tensor.shape[:2]) == (phases, nodes), "record_shape")
        _require(tensor.dtype == torch.float32, "record_dtype")
        values = tensor[:, :, list(channels)].detach().cpu()
        _require(bool(torch.isfinite(values).all().item()), "nonfinite")
        total += values.mean(dim=1)
        squared += values.square().mean(dim=1)
        if expected_nodes == 13_902 and (index % 50 == 0 or index == len(records)):
            print(json.dumps({"stage": "objective_scale", "cases": index}), flush=True)
    phase_mean = total / len(records)
    phase_variance = squared / len(records) - phase_mean.square()
    _require(bool((phase_variance >= 0.0).all().item()), "negative_variance")
    phase_std = torch.sqrt(phase_variance)
    averaged_std = phase_std.mean(dim=0)
    _require(bool((averaged_std > 0).all().item()), "zero_scale")
    squared_weight = (averaged_std + renormalization_epsilon).square()
    relative = squared_weight / squared_weight.mean()
    ratio = squared_weight.max() / squared_weight.min()
    values = [*averaged_std.tolist(), *relative.tolist(), float(ratio.item())]
    _require(all(math.isfinite(float(value)) for value in values), "nonfinite_result")
    return {
        "upstream_phase_averaged_channel_std": [float(value) for value in averaged_std.tolist()],
        "upstream_renormalization_epsilon": float(renormalization_epsilon),
        "upstream_squared_channel_weights_normalized_by_their_mean": [
            float(value) for value in relative.tolist()
        ],
        "maximum_to_minimum_squared_channel_weight_ratio": float(ratio.item()),
        "phase_count": phases,
        "node_count": nodes,
        "train_case_count": len(records),
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
    transient_path: Path,
    public_split_path: Path,
    private_split_path: Path,
    train_audit_public_path: Path,
    train_audit_private_path: Path,
    result_path: Path,
    provenance: Mapping[str, Any],
    torch: Any,
) -> dict[str, Any]:
    source = config["source"]
    for path, size, digest, label in (
        (transient_path, source["processed_v5_bytes"], source["processed_v5_sha256"], "transient"),
        (public_split_path, None, source["public_split_sha256"], "public_split"),
        (private_split_path, None, source["private_split_sha256"], "private_split"),
        (train_audit_public_path, None, source["public_train_audit_sha256"], "audit_public"),
        (train_audit_private_path, None, source["private_train_audit_sha256"], "audit_private"),
    ):
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
        and _ordered_digest(train_order) == source["train_loader_order_sha256"]
        and set(train_order) == set(buckets["train"]),
        "train_order",
    )
    transient = safe_torch_load(transient_path, torch)
    ordered, indexed = index_case_records(transient["registered_data_list"])
    _require(ordered == [str(value) for value in transient["mesh_data"]["cases"]], "case_order")
    train = selected_training_records(
        indexed,
        train_order,
        buckets["validation"] + buckets["test"] + buckets["extra"],
    )
    values = upstream_channel_scale(
        train,
        torch,
        channels=config["audit"]["stored_wss_channels"],
        expected_phases=config["audit"]["expected_phases"],
        expected_nodes=config["audit"]["expected_nodes"],
        renormalization_epsilon=config["audit"]["upstream_renormalization_epsilon"],
    )
    result = {
        "schema_version": "aurora.private.aneug_release_730_objective_scale_audit_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_train_only_descriptive",
        **values,
        **provenance,
        "active_adapter_channel_weights": [1.0, 1.0, 1.0],
        "absolute_materiality_threshold": None,
        "automatic_sensitivity_authorization": False,
        "validation_field_case_count_read": 0,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
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
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    required = (
        args.activation,
        args.expected_commit,
        args.transient,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.result,
    )
    _require(all(value is not None for value in required), "execution_arguments")
    validate_activation(args.activation, config, args.expected_commit)
    import torch

    provenance = {
        "public_commit": args.expected_commit,
        "config_sha256": file_sha256(args.config),
        "activation_sha256": file_sha256(args.activation),
        "processed_v5_sha256": config["source"]["processed_v5_sha256"],
        "private_split_sha256": config["source"]["private_split_sha256"],
        "private_train_audit_sha256": config["source"]["private_train_audit_sha256"],
    }
    run_audit(
        config,
        args.transient,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.result,
        provenance,
        torch,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
