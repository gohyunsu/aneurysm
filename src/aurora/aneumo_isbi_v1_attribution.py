"""Threshold-free attribution of the failed Aneumo ISBI V1 backbone smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_isbi_v1 import (
    AneumoISBIV1Error,
    _family_average,
    _imports,
    _load_registered_task_results,
    _normalize_condition,
    _predict_validation,
    _prepare_cases,
    _relative_l2,
    _sha256,
    _velocity_scale,
    build_model,
    evaluate_same_case_response_oracle,
    load_config,
    load_development_cases,
)


class AneumoISBIV1AttributionError(RuntimeError):
    """Raised when the frozen V1 attribution contract is violated."""


def validate_attribution_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneumo_isbi_v1_attribution.v1":
        raise AneumoISBIV1AttributionError("Unexpected V1a schema version.")
    if payload.get("experiment_id") != "aneumo_isbi_v1a_fixed_checkpoint_task_adequacy":
        raise AneumoISBIV1AttributionError("Unexpected V1a experiment id.")
    source = payload.get("source", {})
    required_source = {
        "v1_config",
        "v1_config_sha256",
        "v1_result",
        "v1_result_sha256",
        "task_git_commit",
        "aggregate_git_commit",
        "cache_sha256",
    }
    if set(source) != required_source:
        raise AneumoISBIV1AttributionError("V1a source dependencies changed.")
    access = payload.get("access", {})
    if (
        access.get("read_field_splits") != ["train", "validation"]
        or access.get("test_field_read") is not False
        or access.get("test_metric_or_selection") is not False
        or access.get("checkpoint_read") is not True
        or access.get("checkpoint_write") is not False
        or access.get("training") is not False
    ):
        raise AneumoISBIV1AttributionError("V1a access boundary changed.")
    if payload.get("success_thresholds") is not None:
        raise AneumoISBIV1AttributionError("V1a cannot define a success threshold.")
    authorization = payload.get("authorization", {})
    if set(authorization.values()) != {False}:
        raise AneumoISBIV1AttributionError("V1a cannot authorize selection or re-entry.")
    expected_questions = [
        "did_the_frozen_models_fit_training_fields_but_fail_family_disjoint_validation",
        "did_predictions_collapse_in_magnitude_or_vector_alignment",
        "how_much_true_field_energy_is_condition_variation_around_each_case_mean",
        "how_far_can_non_deployable_same_case_truth_oracles_reduce_response_error",
    ]
    if payload.get("questions") != expected_questions:
        raise AneumoISBIV1AttributionError("V1a questions changed after registration.")
    return dict(payload)


def load_attribution_config(path: Path) -> dict[str, Any]:
    return validate_attribution_config(json.loads(path.read_text(encoding="utf-8")))


def _split_diagnostics(
    prepared: Mapping[int, Mapping[str, Any]],
    predictions: Mapping[int, Any],
) -> dict[str, float]:
    _, _, torch = _imports()
    full_errors: list[tuple[int, float]] = []
    response_errors: list[tuple[int, float]] = []
    norm_ratios: list[tuple[int, float]] = []
    cosines: list[tuple[int, float]] = []
    span_errors: list[tuple[int, float]] = []
    span_ratios: list[tuple[int, float]] = []
    anchor_index = 3
    if set(prepared) != set(predictions):
        raise AneumoISBIV1AttributionError("V1a prediction coverage changed.")
    for case_id in sorted(prepared):
        case = prepared[case_id]
        family = int(case["base_family"])
        target = torch.as_tensor(case["velocity"], dtype=torch.float32)
        predicted = torch.as_tensor(predictions[case_id], dtype=torch.float32)
        if predicted.shape != target.shape:
            raise AneumoISBIV1AttributionError("V1a prediction shape changed.")
        for condition_index in range(target.shape[0]):
            true_field = target[condition_index]
            predicted_field = predicted[condition_index]
            full_errors.append((family, _relative_l2(predicted_field, true_field)))
            true_norm = torch.linalg.vector_norm(true_field.reshape(-1)).clamp_min(1e-12)
            predicted_norm = torch.linalg.vector_norm(predicted_field.reshape(-1))
            norm_ratios.append((family, float((predicted_norm / true_norm).item())))
            cosine = torch.sum(predicted_field * true_field) / (
                predicted_norm.clamp_min(1e-12) * true_norm
            )
            cosines.append((family, float(cosine.item())))
            if condition_index != anchor_index:
                response_errors.append(
                    (
                        family,
                        _relative_l2(
                            predicted_field - predicted[anchor_index],
                            true_field - target[anchor_index],
                        ),
                    )
                )
        true_span = target[-1] - target[0]
        predicted_span = predicted[-1] - predicted[0]
        span_errors.append((family, _relative_l2(predicted_span, true_span)))
        span_ratios.append(
            (
                family,
                float(
                    (
                        torch.linalg.vector_norm(predicted_span.reshape(-1))
                        / torch.linalg.vector_norm(true_span.reshape(-1)).clamp_min(1e-12)
                    ).item()
                ),
            )
        )
    return {
        "full_q_relative_l2": float(_family_average(full_errors)),
        "response_relative_l2": float(_family_average(response_errors)),
        "prediction_to_target_norm_ratio": float(_family_average(norm_ratios)),
        "prediction_target_cosine": float(_family_average(cosines)),
        "q_span_relative_l2": float(_family_average(span_errors)),
        "q_span_norm_ratio": float(_family_average(span_ratios)),
    }


def truth_only_diagnostics(
    config: Mapping[str, Any],
    prepared: Mapping[int, Mapping[str, Any]],
    flows: Any,
) -> dict[str, float | bool]:
    _, _, torch = _imports()
    zero_errors: list[tuple[int, float]] = []
    mean_errors: list[tuple[int, float]] = []
    condition_fractions: list[tuple[int, float]] = []
    span_to_mean: list[tuple[int, float]] = []
    for case_id in sorted(prepared):
        case = prepared[case_id]
        family = int(case["base_family"])
        target = torch.as_tensor(case["velocity"], dtype=torch.float32)
        condition_mean = target.mean(dim=0)
        for condition_index in range(target.shape[0]):
            zero_errors.append(
                (family, _relative_l2(torch.zeros_like(target[condition_index]), target[condition_index]))
            )
            mean_errors.append(
                (family, _relative_l2(condition_mean, target[condition_index]))
            )
        centered_energy = torch.sum((target - condition_mean[None]) ** 2)
        total_energy = torch.sum(target**2).clamp_min(1e-20)
        condition_fractions.append(
            (family, float((centered_energy / total_energy).item()))
        )
        span_to_mean.append(
            (
                family,
                float(
                    (
                        torch.linalg.vector_norm((target[-1] - target[0]).reshape(-1))
                        / torch.linalg.vector_norm(condition_mean.reshape(-1)).clamp_min(1e-12)
                    ).item()
                ),
            )
        )
    response_oracle = evaluate_same_case_response_oracle(config, prepared, flows)
    return {
        "zero_field_full_q_relative_l2": float(_family_average(zero_errors)),
        "same_case_condition_mean_oracle_full_q_relative_l2": float(
            _family_average(mean_errors)
        ),
        "within_case_condition_energy_fraction": float(
            _family_average(condition_fractions)
        ),
        "q_span_to_mean_field_norm_ratio": float(_family_average(span_to_mean)),
        "registered_anchor_power_response_relative_l2": float(
            response_oracle["validation_response_relative_l2"]
        ),
        "truth_oracles_are_deployable_baselines": False,
    }


def _family_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    np, _, _ = _imports()
    result: dict[str, Any] = {}
    for family in sorted({str(row["family"]) for row in rows}):
        family_rows = [row for row in rows if row["family"] == family]
        split_summary: dict[str, Any] = {}
        for split in ("train", "validation"):
            keys = family_rows[0][split].keys()
            split_summary[split] = {
                key: float(np.mean([float(row[split][key]) for row in family_rows]))
                for key in keys
            }
        split_summary["generalization_gap"] = {
            key: split_summary["validation"][key] - split_summary["train"][key]
            for key in (
                "full_q_relative_l2",
                "response_relative_l2",
                "q_span_relative_l2",
            )
        }
        result[family] = split_summary
    return result


def run_attribution(
    config: Mapping[str, Any],
    *,
    root: Path,
    cache: Path,
    task_output_root: Path,
    output: Path,
    attribution_git_commit: str,
    require_cuda: bool,
) -> dict[str, Any]:
    np, _, torch = _imports()
    source = config["source"]
    v1_config_path = root / source["v1_config"]
    v1_result_path = root / source["v1_result"]
    if _sha256(v1_config_path) != source["v1_config_sha256"]:
        raise AneumoISBIV1AttributionError("V1a V1-config SHA mismatch.")
    if _sha256(v1_result_path) != source["v1_result_sha256"]:
        raise AneumoISBIV1AttributionError("V1a V1-result SHA mismatch.")
    if _sha256(cache) != source["cache_sha256"]:
        raise AneumoISBIV1AttributionError("V1a cache SHA mismatch.")
    v1_config_bytes = v1_config_path.read_bytes()
    v1_config = load_config(v1_config_path)
    v1_config["_config_sha256"] = hashlib.sha256(v1_config_bytes).hexdigest()
    v1_result = json.loads(v1_result_path.read_text(encoding="utf-8"))
    if (
        v1_result["gate"]["all_checks_passed"] is not False
        or v1_result["gate"]["decision"]
        != "stop_the_current_3d_backbone_branch_without_local_hyperparameter_repair"
        or v1_result["task_git_commit"] != source["task_git_commit"]
        or v1_result["aggregate_git_commit"] != source["aggregate_git_commit"]
    ):
        raise AneumoISBIV1AttributionError("V1a cannot relabel its failed source result.")

    task_results, artifacts = _load_registered_task_results(
        v1_config, task_output_root, source["task_git_commit"]
    )
    public_manifest = {
        (str(row["family"]), int(row["seed"])): row
        for row in v1_result["task_manifest"]
    }
    for key, artifact in artifacts.items():
        row = public_manifest.get(key)
        if row is None or any(
            row[name] != artifact[name]
            for name in ("metrics_sha256", "checkpoint_sha256", "status_sha256")
        ):
            raise AneumoISBIV1AttributionError("V1a task manifest SHA mismatch.")

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if require_cuda and device.type != "cuda":
        raise AneumoISBIV1AttributionError("V1a requires scheduler CUDA.")
    if device.type == "cuda":
        torch.cuda.set_device(0)
        torch.cuda.reset_peak_memory_stats()

    train_cases, validation_cases, flows = load_development_cases(v1_config, cache)
    prepared_train = _prepare_cases(v1_config, train_cases)
    prepared_validation = _prepare_cases(v1_config, validation_cases)
    velocity_scale = _velocity_scale(prepared_train)
    normalized_flows = _normalize_condition(flows)
    rows = []
    for result in task_results:
        family = str(result["family"])
        seed = int(result["seed"])
        checkpoint = torch.load(
            artifacts[(family, seed)]["checkpoint_path"],
            map_location="cpu",
            weights_only=False,
        )
        model = build_model(v1_config, family).to(device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        train_predictions, _ = _predict_validation(
            model,
            prepared_train,
            normalized_flows,
            velocity_scale,
            device=device,
        )
        validation_predictions, _ = _predict_validation(
            model,
            prepared_validation,
            normalized_flows,
            velocity_scale,
            device=device,
        )
        rows.append(
            {
                "family": family,
                "seed": seed,
                "train": _split_diagnostics(prepared_train, train_predictions),
                "validation": _split_diagnostics(
                    prepared_validation, validation_predictions
                ),
                "test_fields_read": False,
            }
        )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()
    if len(rows) != 12 or not all(
        math.isfinite(float(value))
        for row in rows
        for split in ("train", "validation")
        for value in row[split].values()
    ):
        raise AneumoISBIV1AttributionError("V1a output is incomplete or non-finite.")

    attribution = {
        "schema_version": config["schema_version"],
        "experiment_id": config["experiment_id"],
        "attribution_git_commit": attribution_git_commit,
        "task_git_commit": source["task_git_commit"],
        "source_aggregate_git_commit": source["aggregate_git_commit"],
        "config_sha256": config["_config_sha256"],
        "v1_config_sha256": source["v1_config_sha256"],
        "v1_result_sha256": source["v1_result_sha256"],
        "cache_sha256": source["cache_sha256"],
        "task_count": len(rows),
        "per_task": sorted(rows, key=lambda row: (row["family"], row["seed"])),
        "family_seed_mean": _family_summary(rows),
        "truth_only_train": truth_only_diagnostics(v1_config, prepared_train, flows),
        "truth_only_validation": truth_only_diagnostics(
            v1_config, prepared_validation, flows
        ),
        "field_access": {
            "train_fields_read": True,
            "validation_fields_read": True,
            "test_fields_read": False,
            "test_metrics_or_selection": False,
        },
        "environment": {
            "device": str(device),
            "torch": torch.__version__,
            "cuda_runtime": torch.version.cuda,
            "peak_gpu_memory_mb": (
                float(torch.cuda.max_memory_allocated() / (1024**2))
                if device.type == "cuda"
                else 0.0
            ),
        },
        "success_thresholds": None,
        "authorization": config["authorization"],
        "interpretation": config["interpretation"],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "attribution.json").write_text(
        json.dumps(attribution, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "status.json").write_text(
        json.dumps(
            {"exit_status": 0, "state": "complete", "test_fields_read": False},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return attribution


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--task-output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--attribution-git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_attribution_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    result = run_attribution(
        config,
        root=args.root,
        cache=args.cache,
        task_output_root=args.task_output_root,
        output=args.output,
        attribution_git_commit=args.attribution_git_commit,
        require_cuda=args.require_cuda,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
