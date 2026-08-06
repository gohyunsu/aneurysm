"""Create public aggregates for the two preregistered post-N1c audits."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde_decision import NonlinearDecisionError
from aurora.nonlinear_pde_decision_task_audit import (
    load_decision_task_audit_config,
)
from aurora.nonlinear_pde_density_objective import (
    VARIANT_IDS,
    load_density_objective_audit_config,
)


MASKS = ("missing", "sparse_2", "partial_4")


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _combined_sha256(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise NonlinearDecisionError(f"Expected JSON object: {path}")
    return payload


def _summary(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        raise NonlinearDecisionError("Cannot summarize an empty metric.")
    return {
        "mean": statistics.fmean(values),
        "sample_std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "minimum": min(values),
        "maximum": max(values),
        "per_seed": list(values),
    }


def aggregate_density(
    *,
    config_path: Path,
    input_root: Path,
    git_commit: str,
) -> dict[str, Any]:
    """Validate and aggregate all five paired density-audit seed outputs."""

    _, config = load_density_objective_audit_config(config_path)
    metric_paths = [
        input_root / f"seed_{index}" / "metrics.json" for index in range(5)
    ]
    if not all(path.is_file() for path in metric_paths):
        missing = [str(path) for path in metric_paths if not path.is_file()]
        raise NonlinearDecisionError(
            f"Density aggregate requires all five seed metrics: {missing}"
        )
    payloads = [_read_json(path) for path in metric_paths]
    expected_seeds = [int(seed) for seed in config["model_seeds"]]
    for index, (path, payload, expected_seed) in enumerate(
        zip(metric_paths, payloads, expected_seeds)
    ):
        if (
            payload.get("schema_version")
            != "aurora.nonlinear_pde_n1_density_objective_audit.seed.v1"
            or int(payload.get("seed_index", -1)) != index
            or int(payload.get("model_seed", -1)) != expected_seed
            or payload.get("git_commit") != git_commit
            or payload.get("test_contexts_generated") != 0
            or payload.get("test_split_generated") is not False
            or payload.get("test_seed_accessed") is not False
            or payload.get("decision", {}).get("cross_variant_method_selected")
            is not False
            or payload.get("decision", {}).get(
                "n1d_or_irregular_3d_authorized"
            )
            is not False
        ):
            raise NonlinearDecisionError(
                f"Density seed output violates the frozen boundary: {path}"
            )

    audit: dict[str, Any] = {}
    for mask in MASKS:
        true_values = [
            float(
                payload["audit_validation"][mask][
                    "true_radius_truncated_law"
                ]["conditional_nll_per_unobserved_component"]
            )
            for payload in payloads
        ]
        audit[mask] = {
            "true_radius_truncated_law": _summary(true_values),
            "variants": {},
        }
        baseline = [
            float(
                payload["audit_validation"][mask]["n1c_random_mask_raw"][
                    "excess_over_true_law"
                ]
            )
            for payload in payloads
        ]
        for variant in VARIANT_IDS:
            nll = [
                float(
                    payload["audit_validation"][mask][variant][
                        "conditional_nll_per_unobserved_component"
                    ]
                )
                for payload in payloads
            ]
            excess = [
                float(
                    payload["audit_validation"][mask][variant][
                        "excess_over_true_law"
                    ]
                )
                for payload in payloads
            ]
            delta = [
                value - reference
                for value, reference in zip(excess, baseline)
            ]
            audit[mask]["variants"][variant] = {
                "conditional_nll_per_unobserved_component": _summary(nll),
                "excess_over_true_law": _summary(excess),
                "paired_excess_delta_vs_n1c_raw": _summary(delta),
                "lower_excess_than_n1c_raw_seeds": sum(
                    value < 0.0 for value in delta
                ),
            }

    return {
        "schema_version": "aurora.public_aggregate_result.v1",
        "result_id": "nonlinear_pde_n1_density_objective_audit",
        "experiment_id": config["experiment_id"],
        "evidence_status": "threshold_free_development_audit_completed",
        "source_commit": git_commit,
        "source_config_sha256": _sha256(config_path),
        "source_metrics_sha256": _combined_sha256(metric_paths),
        "contract": {
            "model_seeds": 5,
            "paired_initialization_and_minibatches": True,
            "selection_validation_disjoint_from_audit_validation": True,
            "n1_test_generated_or_accessed": False,
            "has_success_threshold": False,
            "cross_variant_method_selected": False,
            "may_relabel_n1c": False,
            "may_authorize_n1d_or_irregular_3d": False,
        },
        "audit_validation": audit,
        "decision": {
            "n1c_status": "completed_failed_unchanged",
            "method_novelty_established": False,
            "fresh_reentry_registered": False,
            "n1d_or_irregular_3d_authorized": False,
        },
    }


def aggregate_decision_task(
    *,
    config_path: Path,
    metrics_path: Path,
    git_commit: str,
) -> dict[str, Any]:
    """Strip private context records from a validated task-audit output."""

    _, _, config = load_decision_task_audit_config(config_path)
    payload = _read_json(metrics_path)
    decision = payload.get("decision", {})
    if (
        payload.get("schema_version")
        != "aurora.nonlinear_pde_n1_decision_task_audit.result.v1"
        or payload.get("git_commit") != git_commit
        or payload.get("test_contexts_generated") != 0
        or payload.get("test_split_generated") is not False
        or payload.get("test_seed_accessed") is not False
        or payload.get("learned_models_loaded") != 0
        or payload.get("learned_checkpoints_loaded") != 0
        or decision.get("has_success_threshold") is not False
        or decision.get("task_pass_fail_label_assigned") is not False
        or decision.get("method_or_checkpoint_selected") is not False
        or decision.get("n1d_or_irregular_3d_authorized") is not False
    ):
        raise NonlinearDecisionError(
            "Decision-task output violates its model-free, non-gating boundary."
        )
    return {
        "schema_version": "aurora.public_aggregate_result.v1",
        "result_id": "nonlinear_pde_n1_decision_task_audit",
        "experiment_id": config["experiment_id"],
        "evidence_status": "threshold_free_task_adequacy_audit_completed",
        "source_commit": git_commit,
        "source_config_sha256": _sha256(config_path),
        "source_metrics_sha256": _sha256(metrics_path),
        "contract": {
            "uses_learned_model_or_checkpoint": False,
            "n1_test_generated_or_accessed": False,
            "has_success_threshold": False,
            "task_pass_fail_label_assigned": False,
            "method_or_checkpoint_selected": False,
            "may_relabel_n1c": False,
            "may_authorize_n1d_or_irregular_3d": False,
        },
        "task_adequacy": payload["task_adequacy"],
        "solver": payload["solver"],
        "environment": payload["environment"],
        "decision": {
            "n1c_status": "completed_failed_unchanged",
            "method_novelty_established": False,
            "fresh_reentry_registered": False,
            "n1d_or_irregular_3d_authorized": False,
        },
    }


def _write(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    density = subparsers.add_parser("density")
    density.add_argument("--config", type=Path, required=True)
    density.add_argument("--input-root", type=Path, required=True)
    density.add_argument("--git-commit", required=True)
    density.add_argument("--output", type=Path, required=True)
    task = subparsers.add_parser("decision-task")
    task.add_argument("--config", type=Path, required=True)
    task.add_argument("--metrics", type=Path, required=True)
    task.add_argument("--git-commit", required=True)
    task.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "density":
        payload = aggregate_density(
            config_path=args.config,
            input_root=args.input_root,
            git_commit=args.git_commit,
        )
    else:
        payload = aggregate_decision_task(
            config_path=args.config,
            metrics_path=args.metrics,
            git_commit=args.git_commit,
        )
    _write(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
