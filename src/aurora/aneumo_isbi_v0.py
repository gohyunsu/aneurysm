"""Prospective ISBI V0 asset and task-translation audit for Aneumo.

V0 deliberately does not train a model and does not read any velocity or
pressure array. It verifies the frozen compact-cache metadata, the
base-family split, the scalar inflow design law, and the already public
train-only physical-scaling aggregate. Passing V0 authorizes only a 64-case
implementation smoke; it is not evidence for a paper claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class AneumoISBIV0Error(RuntimeError):
    """Raised when the preregistered V0 contract cannot be evaluated."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _h5py() -> Any:
    try:
        import h5py
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoISBIV0Error("V0 cache metadata audit requires h5py.") from exc
    return h5py


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and copy a V0 protocol payload without filesystem writes."""

    if payload.get("status") != "preregistered_before_v0_result":
        raise AneumoISBIV0Error("V0 must remain prospectively registered.")
    source = payload["source"]
    access = source["field_access"]
    if (
        access.get("allowed") != "previous_train_only_scaling_aggregate"
        or access.get("forbid_validation_and_test_field_reads") is not True
        or access.get("v0_reads_field_arrays") is not False
    ):
        raise AneumoISBIV0Error("V0 may not read field arrays from any split.")
    estimand = payload["estimand"]
    if (
        estimand.get("law_is_known_experimental_design") is not True
        or estimand.get("law_is_patient_population_physiology") is not False
        or estimand.get("pressure_included") is not False
        or estimand.get("wss_osi_or_surface_functionals_included") is not False
        or estimand.get("mass_conservation_endpoint_included") is not False
    ):
        raise AneumoISBIV0Error("The V0 estimand exceeds the audited asset contract.")
    gate = payload["gate"]
    if gate.get("local_repair_allowed") is not False:
        raise AneumoISBIV0Error("V0 failure must not enter a local repair loop.")
    if gate.get("pass_authorizes") != "v1_64_case_implementation_smoke_only":
        raise AneumoISBIV0Error("V0 may authorize only the development smoke.")
    return dict(payload)


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_config(payload)


def _load_dependency(
    root: Path, relative: str, expected_sha256: str, label: str
) -> tuple[Path, dict[str, Any]]:
    path = root / relative
    if _sha256(path) != expected_sha256:
        raise AneumoISBIV0Error(f"{label} SHA-256 mismatch.")
    return path, json.loads(path.read_text(encoding="utf-8"))


def _decode(value: Any) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def audit(
    config: Mapping[str, Any], *, root: Path, cache: Path
) -> dict[str, Any]:
    h5py = _h5py()
    source = config["source"]
    expected = config["expected_asset"]
    cache_sha256 = _sha256(cache)
    if cache_sha256 != source["cache_sha256"]:
        raise AneumoISBIV0Error("Compact-cache SHA-256 mismatch.")

    _, staging = _load_dependency(
        root,
        source["staging_config"],
        source["staging_config_sha256"],
        "staging config",
    )
    _, scaling = _load_dependency(
        root,
        source["scaling_audit_result"],
        source["scaling_audit_result_sha256"],
        "scaling result",
    )

    mapping = {
        int(key): {int(case) for case in cases}
        for key, cases in staging["asset_selection"]["cases_by_base_family"].items()
    }
    registered_splits = {
        split: {int(family) for family in staging["split"][f"{split}_base_families"]}
        for split in ("train", "validation", "test")
    }
    observed_splits = {split: set() for split in registered_splits}
    observed_cases: set[int] = set()
    field_shapes: set[tuple[int, ...]] = set()
    coordinate_shapes: set[tuple[int, ...]] = set()
    marker_like_keys: set[str] = set()

    with h5py.File(cache, "r") as handle:
        attrs = handle.attrs
        columns = json.loads(_decode(attrs["columns"]))
        flows = [float(item) for item in handle["mass_flows_kg_s"][:]]
        manifest = json.loads(bytes(handle["member_manifest_json"][()]).decode("utf-8"))
        archive_manifest = json.loads(_decode(attrs["archive_manifest_json"]))
        if _decode(attrs.get("config_sha256", "")) != source["staging_config_sha256"]:
            raise AneumoISBIV0Error("Cache does not pin the registered staging config.")
        if _decode(attrs.get("dataset", "")) != expected["dataset"]:
            raise AneumoISBIV0Error("Unexpected cache dataset label.")
        if _decode(attrs.get("license", "")) != expected["license"]:
            raise AneumoISBIV0Error("Unexpected cache license.")
        if bool(attrs.get("redistributable", True)) is not expected["redistributable"]:
            raise AneumoISBIV0Error("Cache redistribution flag changed.")

        geometries = handle["geometries"]
        for case_name in geometries:
            case = int(case_name)
            group = geometries[case_name]
            family = int(group.attrs["base_family"])
            split = _decode(group.attrs["split"])
            if family not in mapping or case not in mapping[family]:
                raise AneumoISBIV0Error("Cache case-to-family mapping changed.")
            if split not in registered_splits or family not in registered_splits[split]:
                raise AneumoISBIV0Error("Cache split assignment changed.")
            observed_cases.add(case)
            observed_splits[split].add(family)
            coordinate_shapes.add(tuple(group["coordinates_m"].shape))
            field_shapes.add(tuple(group["pressure_velocity"].shape))
            marker_like_keys.update(
                key
                for key in group.keys()
                if any(token in key.lower() for token in ("marker", "normal", "surface"))
            )

    expected_flows = [float(item) for item in expected["mass_flows_kg_s"]]
    flow_match = len(flows) == len(expected_flows) and all(
        abs(left - right) <= 1e-9 for left, right in zip(flows, expected_flows)
    )
    split_match = all(
        observed_splits[split] == registered_splits[split]
        and len(observed_splits[split]) == int(expected["split_family_counts"][split])
        for split in registered_splits
    )
    expected_cases = set().union(*mapping.values())
    tensor_match = (
        coordinate_shapes == {(int(expected["nodes_per_case"]), 3)}
        and field_shapes
        == {(
            int(expected["conditions"]),
            int(expected["nodes_per_case"]),
            4,
        )}
    )
    cache_dependency_match = (
        observed_cases == expected_cases
        and len(observed_cases) == int(expected["cases"])
        and len(mapping) == int(expected["base_families"])
        and len(archive_manifest) == int(expected["archives"])
        and len(manifest) == int(expected["members"])
        and columns == expected["array_columns"]
    )

    nontriviality = config["nontriviality_evidence"]
    velocity = scaling["channels"]["velocity"]
    pressure = scaling["channels"]["pressure"]
    lower = float(velocity["tuned_residual_ci95"][0])
    scaling_match = (
        scaling["dataset"].get("cache_sha256") == source["cache_sha256"]
        and scaling.get("source_config_sha256")
        == source["scaling_audit_config_sha256"]
        and scaling["dataset"].get("analysis_split") == "train_only"
        and scaling["dataset"].get("validation_or_test_fields_read") is False
        and scaling["decision"].get("audit_decision")
        == nontriviality["required_decision"]
        and scaling["decision"].get("eligible_channels")
        == nontriviality["required_eligible_channels"]
        and lower
        >= float(nontriviality["minimum_velocity_tuned_power_residual_ci95_lower"])
        and abs(
            lower
            - float(
                nontriviality[
                    "expected_velocity_tuned_power_residual_ci95_lower"
                ]
            )
        )
        <= 1e-15
        and pressure.get("eligible") is False
    )
    law = config["estimand"]
    law_identified = (
        law["missing_condition_law"]
        == "discrete_uniform_over_eight_registered_mass_flows"
        and law["law_is_known_experimental_design"] is True
        and law["law_is_patient_population_physiology"] is False
    )
    endpoint_exclusion = (
        marker_like_keys == set()
        and law["pressure_included"] is False
        and law["wss_osi_or_surface_functionals_included"] is False
        and law["mass_conservation_endpoint_included"] is False
    )

    checks = {
        "cache_and_dependency_integrity": cache_dependency_match,
        "family_disjoint_split_integrity": split_match,
        "scalar_mass_flow_contract": flow_match,
        "velocity_tensor_metadata_contract": tensor_match,
        "no_validation_or_test_field_access": True,
        "velocity_response_nontrivial_beyond_global_power": scaling_match,
        "missing_condition_law_semantically_identified": law_identified,
        "unsupported_surface_and_pressure_endpoints_excluded": endpoint_exclusion,
    }
    if list(checks) != list(config["gate"]["checks"]):
        raise AneumoISBIV0Error("Implementation and registered V0 checks disagree.")
    passed = all(checks.values())
    decision = (
        config["gate"]["pass_authorizes"]
        if passed
        else config["gate"]["failure_action"]
    )
    return {
        "schema_version": "aurora.aneumo_isbi_v0.result.v1",
        "experiment_id": config["experiment_id"],
        "cache_sha256": cache_sha256,
        "checks": checks,
        "passed_checks": sum(checks.values()),
        "total_checks": len(checks),
        "all_checks_passed": passed,
        "decision": decision,
        "field_access": {
            "cache_field_arrays_read": False,
            "previous_scaling_aggregate_split": "train",
            "validation_or_test_fields_read": False,
        },
        "asset": {
            "cases": len(observed_cases),
            "base_families": len(mapping),
            "conditions": len(flows),
            "nodes_per_case": int(expected["nodes_per_case"]),
            "archives": len(archive_manifest),
            "members_crc_verified_at_staging": len(manifest),
            "marker_or_surface_arrays_present": bool(marker_like_keys),
        },
        "estimand": law,
        "nontriviality": {
            "velocity_tuned_power_residual_ci95_lower": lower,
            "velocity_eligible": bool(velocity["eligible"]),
            "pressure_eligible": bool(pressure["eligible"]),
        },
        "authorization": {
            "v1_64_case_implementation_smoke": passed,
            "outer_test": False,
            "headline_result": False,
            "isbi_submission": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    result = audit(config, root=args.root, cache=args.cache)
    result["config_sha256"] = _sha256(args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
