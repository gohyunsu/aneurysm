"""Fail-closed evaluator for the registered Aneumo response-fidelity P0.

The current public configuration is deliberately non-executable.  This module
therefore separates pure aggregate-metric evaluation (testable on synthetic
arrays) from authorized HDF5 access.  ``run_authorized_p0`` checks execution
authority before testing whether the private cache even exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from .response_fidelity import (
    ResponseFidelityError,
    coordinate_hash_partition,
    load_p0_config,
    relative_l2,
    validate_case,
)


class AneumoResponseFidelityP0Error(RuntimeError):
    """Raised when the P0 access or aggregation contract is violated."""


def _numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional local dependency
        raise AneumoResponseFidelityP0Error("Response P0 requires numpy.") from exc
    return np


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decode(value: Any) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def _rankdata(values: Any) -> Any:
    """Average ranks with deterministic stable ordering and no SciPy dependency."""

    np = _numpy()
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size < 2 or not np.all(np.isfinite(vector)):
        raise AneumoResponseFidelityP0Error("Spearman inputs must be finite vectors.")
    order = np.argsort(vector, kind="mergesort")
    ranks = np.empty(vector.size, dtype=np.float64)
    start = 0
    while start < vector.size:
        stop = start + 1
        while stop < vector.size and vector[order[stop]] == vector[order[start]]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    return ranks


def spearman_correlation(first: Any, second: Any) -> float:
    np = _numpy()
    left = _rankdata(first)
    right = _rankdata(second)
    if left.shape != right.shape:
        raise AneumoResponseFidelityP0Error("Spearman inputs must be shape-matched.")
    left = left - np.mean(left)
    right = right - np.mean(right)
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator <= 1e-30:
        raise AneumoResponseFidelityP0Error("Spearman ranks are constant.")
    return float(np.dot(left, right) / denominator)


def _cosine(first: Any, second: Any) -> float:
    np = _numpy()
    left = np.asarray(first, dtype=np.float64).reshape(-1)
    right = np.asarray(second, dtype=np.float64).reshape(-1)
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator <= 1e-30:
        raise AneumoResponseFidelityP0Error("Tangent direction has zero norm.")
    return float(np.clip(np.dot(left, right) / denominator, -1.0, 1.0))


def _bootstrap_median_interval(
    values: Sequence[float], *, replicates: int, seed: int, confidence: float
) -> dict[str, Any]:
    np = _numpy()
    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size < 2 or not np.all(np.isfinite(vector)):
        raise AneumoResponseFidelityP0Error(
            "Family bootstrap requires at least two finite family summaries."
        )
    generator = np.random.default_rng(int(seed))
    indices = generator.integers(0, vector.size, size=(int(replicates), vector.size))
    bootstrap = np.median(vector[indices], axis=1)
    tail = (1.0 - float(confidence)) / 2.0
    return {
        "independent_unit": "aneumo_generation_family",
        "family_count": int(vector.size),
        "median": float(np.median(vector)),
        "ci95": [
            float(np.quantile(bootstrap, tail)),
            float(np.quantile(bootstrap, 1.0 - tail)),
        ],
    }


def _flow_stratified_spearman(first: Any, second: Any) -> float:
    """Compare family rankings separately within every non-anchor flow."""

    np = _numpy()
    left = np.asarray(first, dtype=np.float64)
    right = np.asarray(second, dtype=np.float64)
    if left.shape != right.shape or left.ndim != 2 or left.shape[0] < 2:
        raise AneumoResponseFidelityP0Error(
            "Half descriptors must be matched [families, target flows] matrices."
        )
    left_ranks = np.column_stack([_rankdata(left[:, index]) for index in range(left.shape[1])])
    right_ranks = np.column_stack(
        [_rankdata(right[:, index]) for index in range(right.shape[1])]
    )
    return spearman_correlation(left_ranks.reshape(-1), right_ranks.reshape(-1))


def _bootstrap_stratified_spearman(
    first: Any,
    second: Any,
    *,
    replicates: int,
    seed: int,
    confidence: float,
) -> dict[str, Any]:
    np = _numpy()
    left = np.asarray(first, dtype=np.float64)
    right = np.asarray(second, dtype=np.float64)
    estimate = _flow_stratified_spearman(left, right)
    generator = np.random.default_rng(int(seed))
    values: list[float] = []
    attempts = 0
    maximum_attempts = int(replicates) * 4
    while len(values) < int(replicates) and attempts < maximum_attempts:
        attempts += 1
        indices = generator.integers(0, left.shape[0], size=left.shape[0])
        try:
            values.append(_flow_stratified_spearman(left[indices], right[indices]))
        except AneumoResponseFidelityP0Error:
            # A degenerate all-tied resample carries no rank information.
            continue
    if len(values) != int(replicates):
        raise AneumoResponseFidelityP0Error(
            "Family bootstrap produced too many degenerate rank resamples."
        )
    bootstrap = np.asarray(values, dtype=np.float64)
    tail = (1.0 - float(confidence)) / 2.0
    return {
        "independent_unit": "aneumo_generation_family",
        "family_count": int(left.shape[0]),
        "aggregation": "within_flow_family_ranks_then_concatenate",
        "estimate": estimate,
        "ci95": [
            float(np.quantile(bootstrap, tail)),
            float(np.quantile(bootstrap, 1.0 - tail)),
        ],
    }


def _linear_interpolation(q: Any, values: Any, index: int) -> Any:
    weight = float((q[index] - q[index - 1]) / (q[index + 1] - q[index - 1]))
    return (1.0 - weight) * values[index - 1] + weight * values[index + 1]


def _case_summaries(
    flows: Any, coordinates: Any, velocity: Any, *, anchor_flow: float
) -> dict[str, Any]:
    np = _numpy()
    try:
        q, xyz, fields, anchor_index = validate_case(
            flows, coordinates, velocity, anchor_flow=anchor_flow
        )
        halves = coordinate_hash_partition(xyz)
    except ResponseFidelityError as exc:
        raise AneumoResponseFidelityP0Error(str(exc)) from exc

    keep = np.arange(q.size) != anchor_index
    response = fields - fields[anchor_index][None, :, :]
    half_descriptors: list[list[float]] = [[], []]
    tangent_agreements: list[float] = []
    interpolation_errors: list[float] = []

    for half in (0, 1):
        mask = halves == half
        anchor_norm = float(np.linalg.norm(fields[anchor_index, mask]))
        if anchor_norm <= 1e-30:
            raise AneumoResponseFidelityP0Error("A coordinate half has zero anchor norm.")
        half_descriptors[half] = [
            float(np.linalg.norm(response[index, mask]) / anchor_norm)
            for index in np.flatnonzero(keep)
        ]

    for index in range(1, q.size - 1):
        if index == anchor_index:
            continue
        interpolated = _linear_interpolation(q, fields, index)
        interpolated_response = interpolated - fields[anchor_index]
        interpolation_errors.append(relative_l2(response[index], interpolated_response))
        secant = (fields[index + 1] - fields[index - 1]) / (
            q[index + 1] - q[index - 1]
        )
        left_tangent = (fields[index] - fields[index - 1]) / (
            q[index] - q[index - 1]
        )
        right_tangent = (fields[index + 1] - fields[index]) / (
            q[index + 1] - q[index]
        )
        for half in (0, 1):
            mask = halves == half
            tangent_agreements.extend(
                (
                    _cosine(left_tangent[mask], secant[mask]),
                    _cosine(right_tangent[mask], secant[mask]),
                )
            )

    response_energy = float(
        np.median(
            [
                np.linalg.norm(response[index])
                / max(float(np.linalg.norm(fields[anchor_index])), 1e-30)
                for index in np.flatnonzero(keep)
            ]
        )
    )
    return {
        "half_descriptors": half_descriptors,
        "tangent_direction_agreement": float(np.median(tangent_agreements)),
        "interpolation_relative_error": float(np.median(interpolation_errors)),
        "response_energy": response_energy,
    }


def load_dependencies(
    config: Mapping[str, Any], *, root: Path
) -> dict[str, Any]:
    source = config["source"]
    staging_path = root / source["staging_config"]
    scaling_path = root / source["historical_scaling_result"]
    staging_hash_ok = _sha256(staging_path) == source["staging_config_sha256"]
    scaling_hash_ok = _sha256(scaling_path) == source["historical_scaling_result_sha256"]
    staging = json.loads(staging_path.read_text(encoding="utf-8"))
    scaling = json.loads(scaling_path.read_text(encoding="utf-8"))
    train_families = [int(item) for item in staging["split"]["train_base_families"]]
    mapping = {
        family: tuple(
            int(case)
            for case in staging["asset_selection"]["cases_by_base_family"][str(family)]
        )
        for family in train_families
    }
    historical_exact = bool(
        scaling_hash_ok
        and scaling["dataset"].get("cache_sha256") == source["cache_sha256"]
        and scaling["dataset"].get("analysis_split") == "train_only"
        and scaling["dataset"].get("train_base_families")
        == source["expected_base_families"]
        and scaling["dataset"].get("train_cases") == source["expected_cases"]
        and scaling["dataset"].get("validation_or_test_fields_read") is False
        and scaling["channels"]["velocity"].get("eligible") is True
        and scaling["channels"]["velocity"].get("tuned_residual_ci95")
        == [0.20013078657046568, 0.22433041263796377]
    )
    return {
        "hashes_exact": bool(staging_hash_ok and scaling_hash_ok),
        "historical_velocity_response_exact": historical_exact,
        "train_mapping": mapping,
    }


def evaluate_records(
    config: Mapping[str, Any],
    *,
    flows: Any,
    records: Sequence[Mapping[str, Any]],
    expected_train_mapping: Mapping[int, Sequence[int]],
    reported_cache_sha256: str,
    dependency_hashes_exact: bool,
    historical_velocity_response_exact: bool,
) -> dict[str, Any]:
    """Evaluate aggregate P0 endpoints from already-loaded train records."""

    np = _numpy()
    source = config["source"]
    gate = config["gate"]
    q = np.asarray(flows, dtype=np.float64)
    registered_q = np.asarray(config["task"]["mass_flows_kg_s"], dtype=np.float64)
    if q.shape != registered_q.shape or not np.array_equal(q, registered_q):
        raise AneumoResponseFidelityP0Error("The observed flow grid changed.")
    anchor_flow = float(config["task"]["anchor_mass_flow_kg_s"])
    if np.count_nonzero(np.isclose(q, anchor_flow, rtol=0.0, atol=1e-12)) != 1:
        raise AneumoResponseFidelityP0Error("The anchor flow is not unique.")

    expected = {
        int(family): tuple(sorted(int(case) for case in cases))
        for family, cases in expected_train_mapping.items()
    }
    observed: dict[int, list[int]] = defaultdict(list)
    summaries: dict[int, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    seen_cases: set[int] = set()
    observed_node_counts: set[int] = set()
    for record in records:
        if str(record.get("split")) != "train":
            raise AneumoResponseFidelityP0Error("A non-train record entered P0.")
        case_id = int(record["case_id"])
        family = int(record["base_family"])
        if case_id in seen_cases:
            raise AneumoResponseFidelityP0Error("A train case was duplicated.")
        seen_cases.add(case_id)
        coordinates = np.asarray(record["coordinates_m"])
        if coordinates.ndim != 2:
            raise AneumoResponseFidelityP0Error("Coordinates are not a node matrix.")
        observed_node_counts.add(int(coordinates.shape[0]))
        observed[family].append(case_id)
        summary = _case_summaries(
            q,
            record["coordinates_m"],
            record["velocity_m_s"],
            anchor_flow=anchor_flow,
        )
        summaries[family].append((case_id, summary))

    observed_mapping = {
        family: tuple(sorted(cases)) for family, cases in sorted(observed.items())
    }
    mapping_exact = observed_mapping == expected
    if not mapping_exact:
        raise AneumoResponseFidelityP0Error(
            "Train family/case mapping does not match the frozen staging contract."
        )
    if len(records) != int(source["expected_cases"]) or len(observed) != int(
        source["expected_base_families"]
    ):
        raise AneumoResponseFidelityP0Error("Train family or case count changed.")
    if any(
        len(items) != int(source["expected_deformations_per_family"])
        for items in summaries.values()
    ):
        raise AneumoResponseFidelityP0Error("A family deformation count changed.")
    if observed_node_counts != {int(source["expected_nodes_per_case"])}:
        raise AneumoResponseFidelityP0Error("The registered node count changed.")

    half_zero_by_family: list[list[float]] = []
    half_one_by_family: list[list[float]] = []
    tangent_agreements: list[float] = []
    interpolation_errors: list[float] = []
    deformation_zero: list[float] = []
    deformation_one: list[float] = []
    for family in sorted(summaries):
        items = sorted(summaries[family], key=lambda item: item[0])
        half_zero_by_family.append(
            np.median(
                np.asarray([item[1]["half_descriptors"][0] for item in items]),
                axis=0,
            ).tolist()
        )
        half_one_by_family.append(
            np.median(
                np.asarray([item[1]["half_descriptors"][1] for item in items]),
                axis=0,
            ).tolist()
        )
        tangent_agreements.append(
            float(np.median([item[1]["tangent_direction_agreement"] for item in items]))
        )
        interpolation_errors.append(
            float(np.median([item[1]["interpolation_relative_error"] for item in items]))
        )
        deformation_zero.append(float(items[0][1]["response_energy"]))
        deformation_one.append(float(items[1][1]["response_energy"]))

    replicates = int(gate["bootstrap_replicates"])
    seed = int(gate["bootstrap_seed"])
    confidence = float(gate["confidence"])
    half_summary = _bootstrap_stratified_spearman(
        half_zero_by_family,
        half_one_by_family,
        replicates=replicates,
        seed=seed,
        confidence=confidence,
    )
    tangent_summary = _bootstrap_median_interval(
        tangent_agreements,
        replicates=replicates,
        seed=seed + 1,
        confidence=confidence,
    )
    interpolation_summary = _bootstrap_median_interval(
        interpolation_errors,
        replicates=replicates,
        seed=seed + 2,
        confidence=confidence,
    )
    family_rank = spearman_correlation(deformation_zero, deformation_one)

    checks = {
        "pinned_cache_and_dependency_hashes": bool(
            dependency_hashes_exact
            and reported_cache_sha256 == source["cache_sha256"]
        ),
        "train_only_twenty_family_forty_case_contract": mapping_exact,
        "eight_registered_flows_and_anchor_present_once": True,
        "coordinates_and_velocity_finite_and_aligned": True,
        "historical_velocity_response_nontriviality_dependency_exact": bool(
            historical_velocity_response_exact
        ),
        "coordinate_half_response_descriptor_spearman_ci95_lower_at_least_0_80": bool(
            half_summary["ci95"][0] >= 0.80
        ),
        "leave_one_flow_tangent_direction_agreement_ci95_lower_at_least_0_80": bool(
            tangent_summary["ci95"][0] >= 0.80
        ),
        "leave_one_flow_relative_interpolation_error_ci95_upper_at_most_0_35": bool(
            interpolation_summary["ci95"][1] <= 0.35
        ),
        "family_cluster_bootstrap_only": bool(
            config["task"]["independent_unit"] == "aneux_base_family"
            and config["task"]["case_flow_or_node_as_independent_unit"] is False
        ),
        "no_pressure_validation_test_model_checkpoint_prediction_or_gpu_read": True,
    }
    if tuple(checks) != tuple(gate["checks"]):
        raise AneumoResponseFidelityP0Error("Implemented checks differ from registration.")
    passed = all(checks.values())
    return {
        "schema_version": "aurora.aneumo_response_fidelity_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "status": (
            "passed_endpoint_stability_gate"
            if passed
            else "failed_endpoint_stability_gate"
        ),
        "scientific_gate_evaluated": True,
        "gate_passed": passed,
        "passed_checks": sum(bool(value) for value in checks.values()),
        "total_checks": len(checks),
        "checks": checks,
        "asset": {
            "dataset": "Aneumo",
            "split": "train",
            "base_families": len(observed),
            "cases": len(records),
            "conditions": int(q.size),
            "nodes_per_case": next(iter(observed_node_counts)),
            "cache_sha256": source["cache_sha256"],
            "case_ids_published": False,
            "family_ids_published": False,
        },
        "aggregate_endpoints": {
            "coordinate_half_response_descriptor_spearman": half_summary,
            "leave_one_flow_tangent_direction_agreement": tangent_summary,
            "leave_one_flow_response_interpolation_relative_l2": interpolation_summary,
            "paired_deformation_response_energy_rank_spearman": family_rank,
        },
        "access": {
            "datasets_read": [
                "coordinates_m",
                "pressure_velocity_velocity_channels_only",
            ],
            "pressure_read": False,
            "validation_or_test_fields_read": False,
            "model_checkpoint_or_prediction_read": False,
            "gpu_access": False,
            "network_access": False,
        },
        "authorization": {
            "baseline_only_p1_registration": passed,
            "method": False,
            "architecture": False,
            "gpu": False,
            "validation_or_test_field_access": False,
            "outer_test": False,
            "paper_claim": False,
        },
    }


def _require_execution_authority(config: Mapping[str, Any]) -> None:
    execution = config["execution"]
    source = config["source"]
    if (
        config.get("status")
        != "execution_authorized_after_external_service_change_and_exact_path_freeze"
        or source.get("external_service_state_changed_since_incomplete_inventory")
        is not True
        or not isinstance(source.get("exact_private_cache_path"), str)
        or not Path(source["exact_private_cache_path"]).is_absolute()
        or execution.get("execution_envelope_frozen") is not True
        or execution.get("executable") is not True
        or execution.get("submitted") is not False
        or execution.get("gpu") != 0
    ):
        raise AneumoResponseFidelityP0Error(
            "The registered response-fidelity P0 is non-executable; no cache access is allowed."
        )


def _load_train_hdf5(config: Mapping[str, Any], cache: Path) -> tuple[Any, list[dict[str, Any]]]:
    np = _numpy()
    try:
        import h5py
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoResponseFidelityP0Error("Authorized P0 requires h5py.") from exc
    records: list[dict[str, Any]] = []
    with h5py.File(cache, "r") as handle:
        if _decode(handle.attrs.get("config_sha256", "")) != config["source"][
            "staging_config_sha256"
        ]:
            raise AneumoResponseFidelityP0Error("Cache staging-config hash changed.")
        flows = np.asarray(handle["mass_flows_kg_s"], dtype=np.float64)
        for case_name in sorted(handle["geometries"], key=int):
            group = handle["geometries"][case_name]
            if _decode(group.attrs.get("split", "")) != "train":
                continue
            records.append(
                {
                    "case_id": int(case_name),
                    "base_family": int(group.attrs["base_family"]),
                    "split": "train",
                    "coordinates_m": np.asarray(group["coordinates_m"], dtype=np.float64),
                    "velocity_m_s": np.asarray(
                        group["pressure_velocity"][:, :, 1:4], dtype=np.float64
                    ),
                }
            )
    return flows, records


def run_authorized_p0(
    config_path: Path,
    *,
    root: Path,
    cache: Path,
    reported_cache_sha256: str,
) -> dict[str, Any]:
    config = load_p0_config(config_path)
    _require_execution_authority(config)
    if Path(config["source"]["exact_private_cache_path"]).resolve() != cache.resolve():
        raise AneumoResponseFidelityP0Error("Cache path differs from the frozen exact path.")
    dependencies = load_dependencies(config, root=root)
    flows, records = _load_train_hdf5(config, cache)
    result = evaluate_records(
        config,
        flows=flows,
        records=records,
        expected_train_mapping=dependencies["train_mapping"],
        reported_cache_sha256=reported_cache_sha256,
        dependency_hashes_exact=dependencies["hashes_exact"],
        historical_velocity_response_exact=dependencies[
            "historical_velocity_response_exact"
        ],
    )
    result["config_sha256"] = _sha256(config_path)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--reported-cache-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_authorized_p0(
        args.config,
        root=args.root,
        cache=args.cache,
        reported_cache_sha256=args.reported_cache_sha256,
    )
    temporary = args.output.with_name(f".{args.output.name}.partial")
    if args.output.exists() or temporary.exists():
        raise AneumoResponseFidelityP0Error("P0 refuses to overwrite an aggregate.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
