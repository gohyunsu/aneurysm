"""Pre-execution Aneumo response-fidelity P0 v3.

V3 preserves the unexecuted v2 evaluator and adds one non-compensatory audit:
the discrete response tangent must be stable at the nominal anchor itself.
This module contains no model and the current public config remains
non-executable.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_response_fidelity_p0 import (
    AneumoResponseFidelityP0Error,
    _bootstrap_median_interval,
    _cosine,
    _load_train_hdf5,
    _require_execution_authority,
    _sha256,
    evaluate_records as evaluate_v2_records,
    load_dependencies,
    verify_cache_hash,
)
from .response_fidelity import (
    ResponseFidelityError,
    coordinate_hash_partition,
    load_p0_config,
    validate_case,
)


EXPECTED_V2_CONFIG_SHA256 = (
    "b82b3bfd3d83713f375378f471ec506e7b8437fd470e98366534d4cb1d021381"
)
EXPECTED_V2_EVALUATOR_SHA256 = (
    "3f9667329b2f7f61850eddbd5b118c8cab0520cccb86a3382ecfebf6cc292790"
)
ANCHOR_CHECK = "anchor_flow_tangent_direction_agreement_ci95_lower_at_least_0_80"


def _numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional local dependency
        raise AneumoResponseFidelityP0Error("Response P0 v3 requires numpy.") from exc
    return np


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    validate_config(payload, repository_root=config_path.resolve().parents[1])
    return payload


def validate_config(config: Mapping[str, Any], *, repository_root: Path) -> None:
    if config.get("schema_version") != "aurora.aneumo_response_fidelity_p0.v3":
        raise AneumoResponseFidelityP0Error("Unexpected response-fidelity P0 v3 schema.")
    if config.get("status") != (
        "registered_non_executable_pending_external_service_change_and_exact_private_cache_path"
    ):
        raise AneumoResponseFidelityP0Error("P0 v3 must remain fail-closed.")
    supersession = config["supersession"]
    if (
        supersession.get("v2_config_sha256") != EXPECTED_V2_CONFIG_SHA256
        or supersession.get("v2_evaluator_sha256") != EXPECTED_V2_EVALUATOR_SHA256
        or supersession.get("v2_executed") is not False
        or supersession.get("v2_cache_or_field_read") is not False
        or supersession.get("synthetic_negative_control_is_not_scientific_evidence")
        is not True
    ):
        raise AneumoResponseFidelityP0Error("P0 v2 supersession provenance drifted.")
    for relative, expected in (
        (supersession["v2_config"], EXPECTED_V2_CONFIG_SHA256),
        (supersession["v2_evaluator"], EXPECTED_V2_EVALUATOR_SHA256),
    ):
        path = repository_root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise AneumoResponseFidelityP0Error("Preserved P0 v2 bytes drifted.")
    source = config["source"]
    execution = config["execution"]
    if (
        source.get("allowed_split") != "train"
        or source.get("pressure_read_allowed") is not False
        or source.get("validation_or_test_field_read_allowed") is not False
        or source.get("exact_private_cache_path") is not None
        or source.get("external_service_state_changed_since_incomplete_inventory")
        is not False
    ):
        raise AneumoResponseFidelityP0Error("P0 v3 data boundary drifted.")
    if (
        execution.get("server") != "introai9"
        or execution.get("pbs_only") is not True
        or execution.get("gpu") != 0
        or execution.get("junjinyong_allowed") is not False
        or execution.get("executable") is not False
        or execution.get("submitted") is not False
        or execution.get("scientific_checks_evaluated") != 0
    ):
        raise AneumoResponseFidelityP0Error("P0 v3 execution boundary drifted.")
    gate = config["gate"]
    checks = tuple(gate["checks"])
    if (
        len(checks) != 12
        or checks.count(ANCHOR_CHECK) != 1
        or gate.get("anchor_flow_tangent_direction_agreement_min") != 0.8
        or gate.get("bootstrap_replicates") != 5000
        or gate.get("local_repair_allowed") is not False
        or config["task"].get("independent_unit") != "aneumo_generation_family"
    ):
        raise AneumoResponseFidelityP0Error("P0 v3 anchor-tangent gate drifted.")


def anchor_tangent_direction_agreement(
    flows: Any,
    coordinates: Any,
    velocity: Any,
    *,
    anchor_flow: float,
) -> float:
    """Median left/right tangent agreement with the anchor-neighbour secant."""

    np = _numpy()
    try:
        q, xyz, fields, anchor = validate_case(
            flows, coordinates, velocity, anchor_flow=anchor_flow
        )
        halves = coordinate_hash_partition(xyz)
    except ResponseFidelityError as exc:
        raise AneumoResponseFidelityP0Error(str(exc)) from exc
    if anchor <= 0 or anchor >= q.size - 1:
        raise AneumoResponseFidelityP0Error(
            "Anchor tangent audit requires an interior anchor flow."
        )
    secant = (fields[anchor + 1] - fields[anchor - 1]) / (
        q[anchor + 1] - q[anchor - 1]
    )
    left = (fields[anchor] - fields[anchor - 1]) / (q[anchor] - q[anchor - 1])
    right = (fields[anchor + 1] - fields[anchor]) / (q[anchor + 1] - q[anchor])
    values = [
        _cosine(tangent[halves == half], secant[halves == half])
        for tangent in (left, right)
        for half in (0, 1)
    ]
    return float(np.median(np.asarray(values, dtype=np.float64)))


def evaluate_records(
    config: Mapping[str, Any],
    *,
    repository_root: Path,
    flows: Any,
    records: Sequence[Mapping[str, Any]],
    expected_train_mapping: Mapping[int, Sequence[int]],
    reported_cache_sha256: str,
    dependency_hashes_exact: bool,
    historical_velocity_response_exact: bool,
) -> dict[str, Any]:
    """Evaluate all preserved v2 checks plus the explicit anchor check."""

    np = _numpy()
    supersession = config["supersession"]
    v2_config = load_p0_config(repository_root / supersession["v2_config"])
    v2_config = copy.deepcopy(v2_config)
    v2_config["gate"]["bootstrap_replicates"] = int(
        config["gate"]["bootstrap_replicates"]
    )
    v2_config["gate"]["bootstrap_seed"] = int(config["gate"]["bootstrap_seed"])
    v2_config["gate"]["confidence"] = float(config["gate"]["confidence"])
    inherited = evaluate_v2_records(
        v2_config,
        flows=flows,
        records=records,
        expected_train_mapping=expected_train_mapping,
        reported_cache_sha256=reported_cache_sha256,
        dependency_hashes_exact=dependency_hashes_exact,
        historical_velocity_response_exact=historical_velocity_response_exact,
    )

    anchor_by_family: dict[int, list[float]] = defaultdict(list)
    anchor_flow = float(config["task"]["anchor_mass_flow_kg_s"])
    for record in records:
        anchor_by_family[int(record["base_family"])].append(
            anchor_tangent_direction_agreement(
                flows,
                record["coordinates_m"],
                record["velocity_m_s"],
                anchor_flow=anchor_flow,
            )
        )
    family_values = [
        float(np.median(np.asarray(anchor_by_family[family], dtype=np.float64)))
        for family in sorted(anchor_by_family)
    ]
    anchor_summary = _bootstrap_median_interval(
        family_values,
        replicates=int(config["gate"]["bootstrap_replicates"]),
        seed=int(config["gate"]["bootstrap_seed"]) + 4,
        confidence=float(config["gate"]["confidence"]),
    )
    anchor_pass = bool(
        anchor_summary["ci95"][0]
        >= float(config["gate"]["anchor_flow_tangent_direction_agreement_min"])
    )
    checks: dict[str, bool] = {}
    for name in config["gate"]["checks"]:
        checks[name] = anchor_pass if name == ANCHOR_CHECK else bool(
            inherited["checks"][name]
        )
    passed = all(checks.values())
    result = copy.deepcopy(inherited)
    result.update(
        {
            "schema_version": "aurora.aneumo_response_fidelity_p0.result.v3",
            "protocol_id": config["protocol_id"],
            "status": (
                "passed_endpoint_stability_gate"
                if passed
                else "failed_endpoint_stability_gate"
            ),
            "gate_passed": passed,
            "passed_checks": sum(checks.values()),
            "total_checks": len(checks),
            "checks": checks,
            "superseded_v2_gate_would_pass": bool(inherited["gate_passed"]),
        }
    )
    result["aggregate_endpoints"][
        "anchor_flow_tangent_direction_agreement"
    ] = anchor_summary
    result["authorization"] = {
        "new_baseline_only_p1_version_registration": passed,
        "historical_p1_v1_v2_or_v3_activation": False,
        "method": False,
        "architecture": False,
        "gpu": False,
        "validation_or_test_field_access": False,
        "outer_test": False,
        "paper_claim": False,
    }
    return result


def run_authorized_p0(
    config_path: Path,
    *,
    root: Path,
    cache: Path,
    reported_cache_sha256: str,
) -> dict[str, Any]:
    config = load_config(config_path)
    _require_execution_authority(config)
    if Path(config["source"]["exact_private_cache_path"]).resolve() != cache.resolve():
        raise AneumoResponseFidelityP0Error("Cache path differs from the frozen exact path.")
    observed = verify_cache_hash(
        cache,
        reported_sha256=reported_cache_sha256,
        registered_sha256=config["source"]["cache_sha256"],
    )
    dependencies = load_dependencies(config, root=root)
    flows, records = _load_train_hdf5(config, cache)
    result = evaluate_records(
        config,
        repository_root=root,
        flows=flows,
        records=records,
        expected_train_mapping=dependencies["train_mapping"],
        reported_cache_sha256=observed,
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
        raise AneumoResponseFidelityP0Error("P0 v3 refuses to overwrite an aggregate.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
