"""Train-family-only audit of trivial physical scaling in Aneumo.

The audit gives a deliberately strong baseline the field from the same geometry
at one anchor flow. It asks whether velocity-linear or gauge-invariant
pressure-quadratic scaling, and a train-tuned global power law, already explain
the paired response. Validation and test field arrays are never read.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


class AneumoScalingAuditError(RuntimeError):
    """Raised when the preregistered scaling-audit contract is violated."""


def _numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoScalingAuditError("The Aneumo scaling audit requires numpy.") from exc
    return np


def _imports() -> tuple[Any, Any]:
    np = _numpy()
    try:
        import h5py
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoScalingAuditError("Reading the Aneumo cache requires h5py.") from exc
    return np, h5py


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("status") != "preregistered_before_train_field_audit":
        raise AneumoScalingAuditError("The audit must remain prospectively registered.")
    source = payload["source"]
    if source.get("allowed_split") != "train":
        raise AneumoScalingAuditError("The scaling audit may read train fields only.")
    if source.get("forbid_validation_and_test_field_reads") is not True:
        raise AneumoScalingAuditError("Validation/test field reads must remain forbidden.")
    cache_sha256 = str(source.get("cache_sha256_from_completed_integrity_stage", ""))
    if len(cache_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in cache_sha256
    ):
        raise AneumoScalingAuditError("A staged compact-cache SHA-256 must be pinned.")
    if payload["strong_oracle_baseline"].get("uses_same_case_anchor_field") is not True:
        raise AneumoScalingAuditError("The strong oracle anchor baseline cannot be weakened.")
    gate = payload["eligibility_gate"]
    threshold = float(gate["minimum_tuned_power_residual_ci95_lower"])
    if not 0.0 < threshold < 1.0:
        raise AneumoScalingAuditError("The nontriviality threshold must lie in (0, 1).")
    if gate.get("full_pressure_velocity_learning_requires_both_channels") is not True:
        raise AneumoScalingAuditError("Full-field learning must require both channels.")
    return payload


def _candidate_powers(contract: Mapping[str, Any]) -> Any:
    np = _numpy()
    minimum = float(contract["minimum"])
    maximum = float(contract["maximum"])
    step = float(contract["step"])
    if minimum <= 0.0 or maximum < minimum or step <= 0.0:
        raise AneumoScalingAuditError("Invalid global power-search interval.")
    count = int(round((maximum - minimum) / step))
    candidates = minimum + step * np.arange(count + 1, dtype=np.float64)
    if abs(float(candidates[-1]) - maximum) > 1e-10:
        raise AneumoScalingAuditError("Power-search bounds must be divisible by step.")
    return candidates


def _sufficient_statistics(
    anchor: Any,
    target: Any,
    *,
    remove_spatial_mean: bool,
) -> tuple[float, float, float, float]:
    np = _numpy()
    anchor64 = np.asarray(anchor, dtype=np.float64)
    target64 = np.asarray(target, dtype=np.float64)
    if remove_spatial_mean:
        anchor64 = anchor64 - np.mean(anchor64, axis=0, keepdims=True)
        target64 = target64 - np.mean(target64, axis=0, keepdims=True)
    delta = target64 - anchor64
    delta_squared = float(np.sum(delta * delta))
    anchor_squared = float(np.sum(anchor64 * anchor64))
    cross = float(np.sum(delta * anchor64))
    anchor_norm = float(np.sqrt(max(anchor_squared, 0.0)))
    response_ratio = float(np.sqrt(max(delta_squared, 0.0)) / max(anchor_norm, 1e-30))
    if delta_squared <= 1e-30 or anchor_squared <= 1e-30:
        raise AneumoScalingAuditError("A train response or anchor field has zero norm.")
    return delta_squared, cross, anchor_squared, response_ratio


def _residual_ratio(statistic: Mapping[str, Any], power: float) -> float:
    np = _numpy()
    coefficient = float(statistic["flow_ratio"]) ** float(power) - 1.0
    delta_squared = float(statistic["delta_squared"])
    residual_squared = (
        delta_squared
        - 2.0 * coefficient * float(statistic["cross"])
        + coefficient * coefficient * float(statistic["anchor_squared"])
    )
    tolerance = 1e-10 * max(
        delta_squared,
        coefficient * coefficient * float(statistic["anchor_squared"]),
        1.0,
    )
    if residual_squared < -tolerance:
        raise AneumoScalingAuditError("Negative residual energy exceeds roundoff.")
    return float(np.sqrt(max(residual_squared, 0.0) / delta_squared))


def _family_values(statistics: Sequence[Mapping[str, Any]], power: float) -> dict[int, float]:
    np = _numpy()
    grouped: dict[int, list[float]] = defaultdict(list)
    for statistic in statistics:
        grouped[int(statistic["base_family"])].append(
            _residual_ratio(statistic, power)
        )
    return {
        family: float(np.median(np.asarray(values, dtype=np.float64)))
        for family, values in sorted(grouped.items())
    }


def _summarize_families(
    values: Mapping[int, float],
    *,
    replicates: int,
    seed: int,
    confidence: float,
) -> dict[str, Any]:
    np = _numpy()
    ordered = np.asarray([values[key] for key in sorted(values)], dtype=np.float64)
    if ordered.size < 2:
        raise AneumoScalingAuditError("At least two base families are required.")
    generator = np.random.default_rng(int(seed))
    indices = generator.integers(0, ordered.size, size=(int(replicates), ordered.size))
    bootstrap = np.median(ordered[indices], axis=1)
    tail = (1.0 - float(confidence)) / 2.0
    return {
        "base_families": int(ordered.size),
        "median": float(np.median(ordered)),
        "interquartile_range": [
            float(np.quantile(ordered, 0.25)),
            float(np.quantile(ordered, 0.75)),
        ],
        "bootstrap_ci": [
            float(np.quantile(bootstrap, tail)),
            float(np.quantile(bootstrap, 1.0 - tail)),
        ],
    }


def _select_power(
    statistics: Sequence[Mapping[str, Any]],
    contract: Mapping[str, Any],
) -> tuple[float, float]:
    np = _numpy()
    best_power = None
    best_objective = None
    for candidate in _candidate_powers(contract):
        family_values = _family_values(statistics, float(candidate))
        objective = float(np.median(np.asarray(list(family_values.values()))))
        if best_objective is None or objective < best_objective - 1e-15:
            best_power = float(candidate)
            best_objective = objective
    if best_power is None or best_objective is None:
        raise AneumoScalingAuditError("Global power search produced no candidate.")
    return best_power, best_objective


def audit(config: Mapping[str, Any], cache: Path) -> dict[str, Any]:
    np, h5py = _imports()
    source = config["source"]
    anchor_flow = float(config["anchor_mass_flow_kg_s"])
    statistics: dict[str, list[dict[str, Any]]] = {
        channel: [] for channel in config["channels"]
    }
    train_case_ids: list[int] = []
    skipped_nontrain_cases = 0
    with h5py.File(cache, "r") as handle:
        if str(handle.attrs.get("config_sha256", "")) != str(
            source["staging_config_sha256"]
        ):
            raise AneumoScalingAuditError("Cache staging-config SHA-256 mismatch.")
        flows = np.asarray(handle["mass_flows_kg_s"], dtype=np.float64)
        if flows.size != int(source["expected_conditions"]):
            raise AneumoScalingAuditError("Unexpected condition count in cache.")
        anchor_matches = np.flatnonzero(np.isclose(flows, anchor_flow, rtol=0.0, atol=1e-9))
        if anchor_matches.size != 1:
            raise AneumoScalingAuditError("Anchor mass flow is missing or ambiguous.")
        anchor_index = int(anchor_matches[0])
        for case_name in sorted(handle["geometries"], key=int):
            group = handle["geometries"][case_name]
            split = group.attrs.get("split", "")
            if isinstance(split, bytes):
                split = split.decode("utf-8")
            if str(split) != "train":
                skipped_nontrain_cases += 1
                continue
            fields = np.asarray(group["pressure_velocity"], dtype=np.float64)
            if fields.shape[0] != flows.size or fields.ndim != 3 or fields.shape[2] != 4:
                raise AneumoScalingAuditError(f"Unexpected train field shape for {case_name}.")
            if not np.all(np.isfinite(fields)):
                raise AneumoScalingAuditError(f"Non-finite train field for {case_name}.")
            family = int(group.attrs["base_family"])
            train_case_ids.append(int(case_name))
            for channel, channel_contract in config["channels"].items():
                columns = [int(item) for item in channel_contract["columns"]]
                anchor = fields[anchor_index][:, columns]
                for condition_index, flow in enumerate(flows):
                    if condition_index == anchor_index:
                        continue
                    delta_squared, cross, anchor_squared, response_ratio = (
                        _sufficient_statistics(
                            anchor,
                            fields[condition_index][:, columns],
                            remove_spatial_mean=bool(
                                channel_contract["remove_spatial_mean"]
                            ),
                        )
                    )
                    statistics[channel].append(
                        {
                            "case_id": int(case_name),
                            "base_family": family,
                            "mass_flow_kg_s": float(flow),
                            "flow_ratio": float(flow / anchor_flow),
                            "delta_squared": delta_squared,
                            "cross": cross,
                            "anchor_squared": anchor_squared,
                            "response_to_anchor_norm": response_ratio,
                        }
                    )

    observed_families = sorted(
        {int(item["base_family"]) for item in statistics["velocity"]}
    )
    if len(train_case_ids) != int(source["expected_cases"]):
        raise AneumoScalingAuditError("Train case count does not match the contract.")
    if len(observed_families) != int(source["expected_base_families"]):
        raise AneumoScalingAuditError("Train base-family count does not match the contract.")

    metric_contract = config["metrics"]
    bootstrap = {
        "replicates": int(metric_contract["bootstrap_replicates"]),
        "seed": int(metric_contract["bootstrap_seed"]),
        "confidence": float(metric_contract["confidence"]),
    }
    search = config["strong_oracle_baseline"]["global_power_search"]
    threshold = float(
        config["eligibility_gate"]["minimum_tuned_power_residual_ci95_lower"]
    )
    channel_results: dict[str, Any] = {}
    for offset, (channel, channel_contract) in enumerate(config["channels"].items()):
        analytic_power = float(channel_contract["analytic_power"])
        tuned_power, search_objective = _select_power(
            statistics[channel], search[channel]
        )
        analytic_summary = _summarize_families(
            _family_values(statistics[channel], analytic_power),
            replicates=bootstrap["replicates"],
            seed=bootstrap["seed"] + 2 * offset,
            confidence=bootstrap["confidence"],
        )
        tuned_summary = _summarize_families(
            _family_values(statistics[channel], tuned_power),
            replicates=bootstrap["replicates"],
            seed=bootstrap["seed"] + 2 * offset + 1,
            confidence=bootstrap["confidence"],
        )
        response_ratios = np.asarray(
            [item["response_to_anchor_norm"] for item in statistics[channel]],
            dtype=np.float64,
        )
        channel_results[channel] = {
            "analytic_power": analytic_power,
            "analytic_power_residual": analytic_summary,
            "train_tuned_global_power": tuned_power,
            "power_search_objective": search_objective,
            "tuned_power_residual": tuned_summary,
            "response_to_anchor_norm": {
                "median": float(np.median(response_ratios)),
                "interquartile_range": [
                    float(np.quantile(response_ratios, 0.25)),
                    float(np.quantile(response_ratios, 0.75)),
                ],
            },
            "eligible": bool(tuned_summary["bootstrap_ci"][0] >= threshold),
        }

    eligible = [
        channel for channel, result in channel_results.items() if result["eligible"]
    ]
    if len(eligible) == len(channel_results):
        decision = "full_pressure_velocity_learning_eligible"
    elif eligible:
        decision = "channel_scoped_learning_only"
    else:
        decision = "stop_aneumo_g2_as_novelty_evidence"
    return {
        "schema_version": "aurora.aneumo_scaling_audit.result.v1",
        "experiment_id": config["experiment_id"],
        "cache_filename": cache.name,
        "cache_sha256": source["cache_sha256_from_completed_integrity_stage"],
        "cache_sha256_provenance": "verified_before_train_field_audit",
        "field_access": {
            "read_split": "train",
            "validation_or_test_fields_read": False,
            "train_cases": len(train_case_ids),
            "train_base_family_count": len(observed_families),
            "skipped_nontrain_cases": skipped_nontrain_cases,
        },
        "anchor_mass_flow_kg_s": anchor_flow,
        "oracle_same_case_anchor": True,
        "threshold": threshold,
        "channels": channel_results,
        "eligible_channels": eligible,
        "decision": decision,
        "interpretation": config["interpretation"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    result = audit(config, args.cache)
    import hashlib

    result["config_sha256"] = hashlib.sha256(args.config.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
