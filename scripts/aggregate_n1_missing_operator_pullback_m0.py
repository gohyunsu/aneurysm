"""Validate and aggregate the three-seed M0 mechanism-gate outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.nonlinear_pde_decision import NonlinearDecisionError
from aurora.nonlinear_pde_evaluation import context_bootstrap_interval
from aurora.nonlinear_pde_operator_pullback import (
    PROPOSED_VARIANT,
    VARIANT_IDS,
    load_operator_pullback_config,
)


CONTROLS = tuple(name for name in VARIANT_IDS if name != PROPOSED_VARIANT)
JOINT_METRIC = "true_simulator_candidate_joint_mmd_squared"
SOLUTION_METRIC = "true_simulator_solution_mmd_squared"
REGRET_METRIC = "true_oracle_acquisition_regret"
DENSITY_METRIC = "missing_excess_over_true_law"


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


def _metric_values(
    payloads: Sequence[Mapping[str, Any]],
    variant: str,
    metric: str,
) -> list[float]:
    return [
        float(payload["audit_validation"][variant][metric])
        for payload in payloads
    ]


def _relative_improvement(control: float, proposed: float) -> float:
    return (control - proposed) / max(abs(control), 1e-12)


def _relative_degradation(reference: float, proposed: float) -> float:
    return (proposed - reference) / max(abs(reference), 1e-12)


def _strongest_control(
    payloads: Sequence[Mapping[str, Any]], metric: str
) -> str:
    means = {
        name: statistics.fmean(_metric_values(payloads, name, metric))
        for name in CONTROLS
    }
    return min(means, key=means.get)


def _paired_context_ci(
    raw_payloads: Sequence[Mapping[str, Any]],
    *,
    control: str,
    metric: str,
    contexts: int,
    replicates: int,
    seed: int,
) -> dict[str, float]:
    import torch

    differences = []
    for payload in raw_payloads:
        proposed = payload["audit_validation"][PROPOSED_VARIANT][metric]
        reference = payload["audit_validation"][control][metric]
        if len(proposed) != contexts or len(reference) != contexts:
            raise NonlinearDecisionError(
                f"Unexpected paired-context length for {metric}."
            )
        differences.append(
            [float(left) - float(right) for left, right in zip(proposed, reference)]
        )
    return context_bootstrap_interval(
        torch.tensor(differences, dtype=torch.float64),
        replicates=replicates,
        seed=seed,
    )


def aggregate_operator_pullback_m0(
    *,
    config_path: Path,
    input_root: Path,
    git_commit: str,
) -> dict[str, Any]:
    """Apply the preregistered all-checks-required mechanism gate once."""

    _, config, _ = load_operator_pullback_config(config_path)
    metric_paths = [
        input_root / f"seed_{index}" / "metrics.json" for index in range(3)
    ]
    raw_paths = [
        input_root / f"seed_{index}" / "per_context_metrics.json"
        for index in range(3)
    ]
    required = [*metric_paths, *raw_paths]
    if not all(path.is_file() for path in required):
        missing = [str(path) for path in required if not path.is_file()]
        raise NonlinearDecisionError(
            f"M0 aggregate requires all three complete seed outputs: {missing}"
        )
    payloads = [_read_json(path) for path in metric_paths]
    raw_payloads = [_read_json(path) for path in raw_paths]
    expected_seeds = [int(seed) for seed in config["model_seeds"]]
    for index, (payload, raw, expected_seed) in enumerate(
        zip(payloads, raw_payloads, expected_seeds)
    ):
        decision = payload.get("decision", {})
        if (
            payload.get("schema_version")
            != "aurora.nonlinear_pde_n1_missing_operator_pullback_m0.seed.v1"
            or int(payload.get("seed_index", -1)) != index
            or int(payload.get("model_seed", -1)) != expected_seed
            or int(raw.get("model_seed", -1)) != expected_seed
            or payload.get("git_commit") != git_commit
            or payload.get("test_contexts_generated") != 0
            or payload.get("test_split_generated") is not False
            or payload.get("test_seed_accessed") is not False
            or payload.get("solver", {}).get("all_converged") is not True
            or decision.get("mechanism_gate_decided_per_seed") is not False
            or decision.get("n1c_verdict_unchanged") is not True
            or decision.get("fresh_reentry_registered") is not False
            or decision.get("n1d_or_irregular_3d_authorized") is not False
            or decision.get("method_novelty_established") is not False
            or decision.get("local_weight_or_kernel_repair_authorized")
            is not False
            or set(payload.get("audit_validation", {})) != set(VARIANT_IDS)
        ):
            raise NonlinearDecisionError(
                f"M0 seed output violates the prospective boundary: {index}."
            )

    aggregate = {
        variant: {
            metric: _summary(_metric_values(payloads, variant, metric))
            for metric in (
                DENSITY_METRIC,
                SOLUTION_METRIC,
                JOINT_METRIC,
                REGRET_METRIC,
                "selected_component_agreement_with_true_oracle",
            )
        }
        for variant in VARIANT_IDS
    }
    gate = config["mechanism_gate"]
    joint_control = _strongest_control(payloads, JOINT_METRIC)
    regret_control = _strongest_control(payloads, REGRET_METRIC)
    proposed_joint = aggregate[PROPOSED_VARIANT][JOINT_METRIC]["mean"]
    control_joint = aggregate[joint_control][JOINT_METRIC]["mean"]
    proposed_regret = aggregate[PROPOSED_VARIANT][REGRET_METRIC]["mean"]
    control_regret = aggregate[regret_control][REGRET_METRIC]["mean"]
    joint_improvement = _relative_improvement(control_joint, proposed_joint)
    regret_improvement = _relative_improvement(
        control_regret, proposed_regret
    )
    joint_directions = sum(
        left < right
        for left, right in zip(
            aggregate[PROPOSED_VARIANT][JOINT_METRIC]["per_seed"],
            aggregate[joint_control][JOINT_METRIC]["per_seed"],
        )
    )
    regret_directions = sum(
        left < right
        for left, right in zip(
            aggregate[PROPOSED_VARIANT][REGRET_METRIC]["per_seed"],
            aggregate[regret_control][REGRET_METRIC]["per_seed"],
        )
    )
    bootstrap_replicates = int(
        config["audit_evaluation"]["bootstrap_replicates"]
    )
    joint_ci = _paired_context_ci(
        raw_payloads,
        control=joint_control,
        metric=JOINT_METRIC,
        contexts=int(config["data"]["audit_validation_contexts"]),
        replicates=bootstrap_replicates,
        seed=73081901,
    )
    regret_ci = _paired_context_ci(
        raw_payloads,
        control=regret_control,
        metric=REGRET_METRIC,
        contexts=int(config["data"]["acquisition_audit_contexts"]),
        replicates=bootstrap_replicates,
        seed=73081902,
    )
    density_degradation = _relative_degradation(
        aggregate["full_joint_mle"][DENSITY_METRIC]["mean"],
        aggregate[PROPOSED_VARIANT][DENSITY_METRIC]["mean"],
    )
    solution_degradation = _relative_degradation(
        aggregate["full_joint_mle"][SOLUTION_METRIC]["mean"],
        aggregate[PROPOSED_VARIANT][SOLUTION_METRIC]["mean"],
    )
    operator_errors = [
        float(
            payload["frozen_operator"][
                "audit_validation_full_bc_relative_l2"
            ]
        )
        for payload in payloads
    ]
    checks = {
        "candidate_joint_mmd_relative_improvement": {
            "value": joint_improvement,
            "threshold_minimum": float(
                gate[
                    "candidate_joint_mmd_relative_improvement_over_strongest_control_minimum"
                ]
            ),
            "passed": joint_improvement
            >= float(
                gate[
                    "candidate_joint_mmd_relative_improvement_over_strongest_control_minimum"
                ]
            ),
        },
        "candidate_joint_mmd_seed_directions": {
            "value": joint_directions,
            "threshold_minimum": int(
                gate["candidate_joint_mmd_better_seed_directions_minimum"]
            ),
            "passed": joint_directions
            >= int(gate["candidate_joint_mmd_better_seed_directions_minimum"]),
        },
        "candidate_joint_mmd_paired_context_ci": {
            **joint_ci,
            "required_ci95_high_below_zero": True,
            "passed": joint_ci["ci95_high"] < 0.0,
        },
        "acquisition_regret_relative_improvement": {
            "value": regret_improvement,
            "threshold_minimum": float(
                gate[
                    "acquisition_regret_relative_improvement_over_strongest_control_minimum"
                ]
            ),
            "passed": regret_improvement
            >= float(
                gate[
                    "acquisition_regret_relative_improvement_over_strongest_control_minimum"
                ]
            ),
        },
        "acquisition_regret_seed_directions": {
            "value": regret_directions,
            "threshold_minimum": int(
                gate["acquisition_regret_better_seed_directions_minimum"]
            ),
            "passed": regret_directions
            >= int(gate["acquisition_regret_better_seed_directions_minimum"]),
        },
        "acquisition_regret_paired_context_ci": {
            **regret_ci,
            "required_ci95_high_below_zero": True,
            "passed": regret_ci["ci95_high"] < 0.0,
        },
        "missing_density_excess_relative_degradation": {
            "value": density_degradation,
            "threshold_maximum": float(
                gate[
                    "missing_density_excess_relative_degradation_vs_full_joint_maximum"
                ]
            ),
            "passed": density_degradation
            <= float(
                gate[
                    "missing_density_excess_relative_degradation_vs_full_joint_maximum"
                ]
            ),
        },
        "solution_marginal_mmd_relative_degradation": {
            "value": solution_degradation,
            "threshold_maximum": float(
                gate[
                    "solution_marginal_mmd_relative_degradation_vs_full_joint_maximum"
                ]
            ),
            "passed": solution_degradation
            <= float(
                gate[
                    "solution_marginal_mmd_relative_degradation_vs_full_joint_maximum"
                ]
            ),
        },
        "frozen_operator_audit_validation_error": {
            "values": operator_errors,
            "worst": max(operator_errors),
            "threshold_maximum": float(
                gate["operator_checkpoint_validation_error_maximum"]
            ),
            "passed": all(
                value
                <= float(gate["operator_checkpoint_validation_error_maximum"])
                for value in operator_errors
            ),
        },
    }
    passed = all(item["passed"] for item in checks.values())
    return {
        "schema_version": "aurora.public_aggregate_result.v1",
        "result_id": "nonlinear_pde_n1_missing_operator_pullback_m0",
        "experiment_id": config["experiment_id"],
        "evidence_status": (
            "development_mechanism_gate_passed"
            if passed
            else "development_mechanism_gate_failed"
        ),
        "source_commit": git_commit,
        "source_config_sha256": _sha256(config_path),
        "source_metrics_sha256": _combined_sha256(metric_paths),
        "source_private_per_context_sha256": _combined_sha256(raw_paths),
        "contract": {
            "model_seeds": 3,
            "missing_mask_only": True,
            "selection_and_audit_validation_disjoint": True,
            "n1_test_generated_or_accessed": False,
            "all_checks_required": True,
            "local_weight_or_kernel_repair_after_failure": False,
            "pass_only_allows_separate_fresh_reentry_protocol_design": True,
        },
        "strongest_controls": {
            "candidate_joint_mmd": joint_control,
            "acquisition_regret": regret_control,
        },
        "audit_validation": aggregate,
        "mechanism_gate": {
            "checks": checks,
            "passed": passed,
        },
        "decision": {
            "n1c_status": "completed_failed_unchanged",
            "mechanism_eligible_for_separate_fresh_reentry_design": passed,
            "mechanism_abandoned_without_local_repair": not passed,
            "method_novelty_established": False,
            "fresh_reentry_registered": False,
            "n1d_or_irregular_3d_authorized": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    args = parser.parse_args(argv)
    result = aggregate_operator_pullback_m0(
        config_path=args.config,
        input_root=args.input_root,
        git_commit=args.git_commit,
    )
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
