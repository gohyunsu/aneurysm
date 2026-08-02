"""Validate the machine-readable AURORA research contract.

This module intentionally uses only Python's standard library so the protocol
can be checked before a GPU environment or medical dataset is available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class ProtocolError(ValueError):
    """Raised when a research protocol violates a project invariant."""


ALLOWED_ENDPOINTS = {"cross_sectional_rupture_status"}
ALLOWED_PROVENANCE = {"real_cfd", "synthetic_cfd", "surrogate", "none"}
ALLOWED_SPLIT_UNITS = {"patient", "geometry", "generator_seed_geometry"}
REQUIRED_GATES = {"G0", "G1", "G2", "G3", "G4"}
REQUIRED_DATASETS = {"aneumo", "aneug_flow", "benchanxplore", "cmha", "aneux"}


def load_protocol(path: str | Path) -> dict[str, Any]:
    """Load a protocol JSON file and validate its top-level representation."""

    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProtocolError(f"Protocol does not exist: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Invalid JSON in {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProtocolError("Protocol root must be a JSON object.")
    return payload


def _require_keys(
    mapping: Mapping[str, Any], keys: Sequence[str], context: str
) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ProtocolError(f"{context} is missing: {', '.join(missing)}")


def _unique_ids(items: Sequence[Mapping[str, Any]], key: str, context: str) -> set[str]:
    values = [str(item.get(key, "")) for item in items]
    if "" in values:
        raise ProtocolError(f"{context} contains an empty {key}.")
    if len(values) != len(set(values)):
        raise ProtocolError(f"{context} contains duplicate {key} values.")
    return set(values)


def validate_protocol(protocol: Mapping[str, Any]) -> list[str]:
    """Return human-readable checks or raise :class:`ProtocolError`.

    The validator focuses on invariants that prevent target inflation,
    provenance loss, and split leakage. It does not judge whether a future
    experiment passed a scientific gate.
    """

    _require_keys(
        protocol,
        ["schema_version", "project", "task", "datasets", "model", "loss", "gates",
         "evaluation", "phases"],
        "protocol",
    )
    checks: list[str] = []

    project = protocol["project"]
    _require_keys(project, ["name", "status", "clinical_use"], "project")
    if project["name"] != "AURORA":
        raise ProtocolError("Project name must remain AURORA for schema v1.")
    if project["clinical_use"] is not False:
        raise ProtocolError("AURORA v1 must be marked research-only.")
    checks.append("research-only project boundary")

    task = protocol["task"]
    _require_keys(task, ["endpoint", "primary_metric", "forbidden_claims"], "task")
    if task["endpoint"] not in ALLOWED_ENDPOINTS:
        raise ProtocolError(
            "Only cross-sectional rupture status is supported; prospective risk "
            "requires a longitudinal protocol."
        )
    forbidden = set(task["forbidden_claims"])
    if "prospective_rupture_risk" not in forbidden or "clinical_utility" not in forbidden:
        raise ProtocolError("Task must forbid prospective-risk and clinical-utility claims.")
    checks.append("endpoint and forbidden-claim guardrails")

    datasets = protocol["datasets"]
    if not isinstance(datasets, list) or not datasets:
        raise ProtocolError("datasets must be a non-empty list.")
    dataset_names = _unique_ids(datasets, "name", "datasets")
    missing_datasets = REQUIRED_DATASETS - dataset_names
    if missing_datasets:
        raise ProtocolError(
            f"Required dataset roles are absent: {', '.join(sorted(missing_datasets))}"
        )
    for dataset in datasets:
        _require_keys(
            dataset, ["name", "role", "field_provenance", "split_unit"],
            f"dataset {dataset.get('name', '?')}",
        )
        if dataset["field_provenance"] not in ALLOWED_PROVENANCE:
            raise ProtocolError(
                f"Unsupported provenance for {dataset['name']}: "
                f"{dataset['field_provenance']}"
            )
        if dataset["split_unit"] not in ALLOWED_SPLIT_UNITS:
            raise ProtocolError(
                f"Unsupported split unit for {dataset['name']}: {dataset['split_unit']}"
            )
    cmha = next(item for item in datasets if item["name"] == "cmha")
    aneux = next(item for item in datasets if item["name"] == "aneux")
    if cmha["field_provenance"] != "real_cfd":
        raise ProtocolError("CMHA is the declared real-CFD bridge in protocol v1.")
    if aneux["field_provenance"] != "none":
        raise ProtocolError("AneuX must not be declared as real-CFD data.")
    checks.append("dataset provenance and split units")

    model = protocol["model"]
    numeric_model_keys = [
        "surface_queries", "volume_queries", "knn", "latent_tokens", "hidden_dim",
        "attention_layers", "attention_heads", "temporal_fourier_modes",
        "bc_latent_dim", "bc_samples_train", "bc_samples_eval",
        "physics_collocation_points",
    ]
    _require_keys(model, numeric_model_keys, "model")
    for key in numeric_model_keys:
        if not isinstance(model[key], int) or model[key] <= 0:
            raise ProtocolError(f"model.{key} must be a positive integer.")
    if model["hidden_dim"] % model["attention_heads"] != 0:
        raise ProtocolError("hidden_dim must be divisible by attention_heads.")
    if model["bc_samples_eval"] < model["bc_samples_train"]:
        raise ProtocolError("Evaluation must use at least as many BC samples as training.")
    checks.append("model dimensional contract")

    loss = protocol["loss"]
    loss_keys = [
        "field", "functional", "physics", "energy", "cross_consistency",
        "task_alignment",
    ]
    _require_keys(loss, loss_keys, "loss")
    if any(not isinstance(loss[key], (int, float)) or loss[key] < 0 for key in loss_keys):
        raise ProtocolError("All loss weights must be non-negative numbers.")
    if loss["field"] <= 0 or loss["energy"] <= 0:
        raise ProtocolError("Field and distributional energy losses cannot be disabled.")
    checks.append("field and distributional objectives")

    gates = protocol["gates"]
    gate_ids = _unique_ids(gates, "id", "gates")
    if gate_ids != REQUIRED_GATES:
        raise ProtocolError(
            "Gate set must be exactly G0–G4; change schema version to alter it."
        )
    g3 = next(item for item in gates if item["id"] == "G3")
    if g3.get("requires_g1_positive_denominator") is not True:
        raise ProtocolError("Risk-retention must require a positive G1 denominator.")
    checks.append("blocking gates and risk-retention denominator")

    evaluation = protocol["evaluation"]
    _require_keys(
        evaluation,
        ["operator_outer_split", "clinical_outer_folds", "clinical_inner_folds",
         "bootstrap_unit", "bootstrap_replicates", "headline_seeds"],
        "evaluation",
    )
    if evaluation["operator_outer_split"] != "geometry_disjoint":
        raise ProtocolError("Operator evaluation must remain geometry-disjoint.")
    if evaluation["bootstrap_unit"] != "patient":
        raise ProtocolError("Clinical uncertainty must be bootstrapped by patient.")
    if evaluation["clinical_outer_folds"] < 3 or evaluation["clinical_inner_folds"] < 3:
        raise ProtocolError("Nested clinical validation requires at least 3 folds per level.")
    if evaluation["bootstrap_replicates"] < 1000:
        raise ProtocolError("At least 1,000 patient bootstrap replicates are required.")
    checks.append("geometry-disjoint and nested patient-level evaluation")

    phases = protocol["phases"]
    _unique_ids(phases, "id", "phases")
    for phase in phases:
        _require_keys(phase, ["id", "name", "requires", "outputs"], "phase")
        unknown = set(phase["requires"]) - gate_ids
        if unknown:
            raise ProtocolError(
                f"Phase {phase['id']} references unknown gates: {sorted(unknown)}"
            )
    checks.append("phase dependency graph")
    return checks


def canonical_hash(protocol: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 for split/run manifests."""

    encoded = json.dumps(
        protocol, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "summary"):
        child = subparsers.add_parser(command)
        child.add_argument("protocol", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    protocol = load_protocol(args.protocol)
    checks = validate_protocol(protocol)
    digest = canonical_hash(protocol)
    if args.command == "validate":
        print(f"AURORA protocol valid · {len(checks)} invariant groups")
        for check in checks:
            print(f"  ✓ {check}")
        print(f"  sha256 {digest}")
    else:
        print(
            json.dumps(
                {
                    "project": protocol["project"]["name"],
                    "endpoint": protocol["task"]["endpoint"],
                    "datasets": [item["name"] for item in protocol["datasets"]],
                    "gates": [item["id"] for item in protocol["gates"]],
                    "protocol_sha256": digest,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
