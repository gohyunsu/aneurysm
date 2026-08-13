"""Method-free transient WSS critical-structure stability audit.

The public v1 contract was withdrawn before field access because the exact
release licence declarations conflict and the official family mapping is not
yet authoritative. This module preserves and validates the historical frozen
contract and deterministic metrics for synthetic tests. It cannot activate a
runner or select a model.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

from aurora.aneumo_transient_vtp import (
    PolyData,
    bidirectional_signed_recall,
    extract_critical_points,
    normal_component_fraction,
    project_tangent,
    triangulate,
    vertex_normals,
)


class StabilityP0Error(RuntimeError):
    """Raised when the prospective stability contract is incomplete."""


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if config.get("schema_version") != "aurora.aneumo_transient_structure_stability_p0.v1":
        raise StabilityP0Error("unexpected stability P0 schema")
    selection = config["selection"]
    selected = selection["selected"]
    if len(selected) != 12 or len({row["family_id"] for row in selected}) != 12:
        raise StabilityP0Error("P0 requires 12 distinct selected families")
    if len({row["case_id"] for row in selected}) != 12:
        raise StabilityP0Error("P0 selected cases must be distinct")
    if "1" in {row["family_id"] for row in selected}:
        raise StabilityP0Error("D0 development family leaked into P0")
    if selection["phases"] != ["4.01", "4.25", "4.50", "4.75", "5.00"]:
        raise StabilityP0Error("P0 phase panel changed")
    if selection["field_members"] != 60:
        raise StabilityP0Error("P0 member count changed")
    if config["status"] != (
        "withdrawn_before_field_access_pending_authoritative_family_mapping_"
        "and_release_license_resolution"
    ):
        raise StabilityP0Error("v1 withdrawal state changed")
    if (
        selection["inference_unit_verified"]
        or not selection["panel_withdrawn_before_field_access"]
        or not selection["selected_panel_is_historical_and_not_activatable"]
    ):
        raise StabilityP0Error("withdrawn family panel was reactivated")
    if config["execution"]["authorized"] or config["authorization"]["p0_execution"]:
        raise StabilityP0Error("v1 must remain non-executable pending licence resolution")
    if not config["license_boundary"]["authoritative_resolution_required_before_staging_or_execution"]:
        raise StabilityP0Error("licence-resolution gate was removed")
    mapping = config["family_mapping_boundary"]
    if (
        not mapping["owner_acknowledged_connection_csv_error"]
        or not mapping["pinned_csv_still_contradicts_owner_statement_for_case_2158"]
        or not mapping["authoritative_corrected_mapping_required_before_any_successor_selection"]
        or not mapping["current_12_family_panel_may_not_be_activated"]
    ):
        raise StabilityP0Error("family-mapping integrity gate was removed")
    if config["execution"]["ngpus"] != 0:
        raise StabilityP0Error("method-free P0 must remain CPU-only")
    return config


def _edges(polygons: tuple[np.ndarray, ...]) -> np.ndarray:
    values: set[tuple[int, int]] = set()
    for polygon in polygons:
        for left, right in zip(polygon, np.roll(polygon, -1)):
            edge = tuple(sorted((int(left), int(right))))
            if edge[0] != edge[1]:
                values.add(edge)
    if not values:
        raise StabilityP0Error("surface has no polygon edge")
    return np.asarray(sorted(values), dtype=np.int64)


def median_edge_length(data: PolyData) -> float:
    edges = _edges(data.polygons)
    lengths = np.linalg.norm(data.points[edges[:, 0]] - data.points[edges[:, 1]], axis=1)
    value = float(np.median(lengths))
    if not np.isfinite(value) or value <= 0:
        raise StabilityP0Error("invalid median edge length")
    return value


def smoothed_tangent_perturbation(
    data: PolyData,
    normals: np.ndarray,
    tangent: np.ndarray,
    *,
    seed: int,
    relative_amplitude: float,
    smoothing_steps: int,
) -> np.ndarray:
    if relative_amplitude <= 0 or smoothing_steps < 0:
        raise StabilityP0Error("invalid perturbation contract")
    rng = np.random.default_rng(seed)
    noise = project_tangent(rng.standard_normal(tangent.shape), normals)
    edges = _edges(data.polygons)
    for _ in range(smoothing_steps):
        total = noise.copy()
        count = np.ones((noise.shape[0], 1), dtype=np.float64)
        np.add.at(total, edges[:, 0], noise[edges[:, 1]])
        np.add.at(total, edges[:, 1], noise[edges[:, 0]])
        np.add.at(count[:, 0], edges[:, 0], 1)
        np.add.at(count[:, 0], edges[:, 1], 1)
        noise = project_tangent(total / count, normals)
    noise_rms = float(np.sqrt(np.mean(np.sum(noise * noise, axis=1))))
    field_rms = float(np.sqrt(np.mean(np.sum(tangent * tangent, axis=1))))
    if noise_rms <= 0 or field_rms <= 0 or not np.isfinite([noise_rms, field_rms]).all():
        raise StabilityP0Error("zero or nonfinite perturbation scale")
    return tangent + noise * (relative_amplitude * field_rms / noise_rms)


def _derived_seed(base_seed: int, family_id: str, case_id: int, phase: str) -> int:
    text = f"{base_seed}:{family_id}:{case_id}:{phase}".encode()
    return int.from_bytes(hashlib.sha256(text).digest()[:8], "little")


def audit_phase(
    data: PolyData,
    *,
    family_id: str,
    case_id: int,
    phase: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    representation = config["representation"]
    thresholds = config["phase_gates"]
    edge = median_edge_length(data)
    critical: dict[str, list] = {}
    tangency: dict[str, dict[str, float]] = {}
    tangents: dict[str, np.ndarray] = {}
    normals_by_mode: dict[str, np.ndarray] = {}
    for normal_mode in representation["normal_modes"]:
        normals = vertex_normals(data.points, data.polygons, normal_mode)
        normals_by_mode[normal_mode] = normals
        fractions = normal_component_fraction(data.point_wss, normals)
        tangent = project_tangent(data.point_wss, normals)
        tangents[normal_mode] = tangent
        tangency[normal_mode] = {
            "median": float(np.median(fractions)),
            "p95": float(np.quantile(fractions, 0.95)),
        }
        for fan in representation["triangulation_modes"]:
            key = f"{normal_mode}__{fan}"
            critical[key] = extract_critical_points(
                data.points,
                triangulate(data.polygons, fan),
                tangent,
                phase=phase,
                interior_margin=float(representation["critical_point_interior_margin"]),
                determinant_relative_floor=float(
                    representation["critical_point_determinant_relative_floor"]
                ),
            )

    radius_rows: dict[str, dict[str, float]] = {}
    primary_min_recall = 1.0
    for multiplier in representation["sensitivity_matching_radius_median_edge_multipliers"]:
        pair_values = []
        for left, right in itertools.combinations(sorted(critical), 2):
            forward, backward = bidirectional_signed_recall(
                critical[left], critical[right], radius=edge * float(multiplier)
            )
            pair_values.extend((forward, backward))
        minimum = min(pair_values) if pair_values else 1.0
        radius_rows[str(multiplier)] = {"minimum_bidirectional_signed_recall": minimum}
        if float(multiplier) == float(
            representation["primary_matching_radius_median_edge_multiplier"]
        ):
            primary_min_recall = minimum

    counts_by_key = {key: len(value) for key, value in critical.items()}
    signed_by_key = {
        key: sum(point.signed_index for point in value) for key, value in critical.items()
    }
    counts = list(counts_by_key.values())
    signed_totals = list(signed_by_key.values())
    informative = min(counts) >= int(
        representation["minimum_informative_critical_points_per_configuration"]
    )
    tangency_pass = all(
        row["median"] <= float(thresholds["tangency_median_maximum"])
        and row["p95"] <= float(thresholds["tangency_p95_maximum"])
        for row in tangency.values()
    )
    discretization_pass = (
        informative
        and primary_min_recall
        >= float(thresholds["minimum_pairwise_bidirectional_signed_recall"])
        and max(counts) - min(counts)
        <= int(thresholds["maximum_critical_point_count_range"])
        and max(signed_totals) - min(signed_totals)
        <= int(thresholds["maximum_total_signed_index_range"])
    )

    perturbation = config["perturbation"]
    normal_mode = perturbation["reference_normal_mode"]
    fan = perturbation["reference_triangulation_mode"]
    base = critical[f"{normal_mode}__{fan}"]
    triangles = triangulate(data.polygons, fan)
    perturbation_rows = []
    primary_amplitude = float(
        perturbation["primary_amplitude_relative_to_phase_tangent_rms"]
    )
    for amplitude in perturbation["sensitivity_amplitudes_relative_to_phase_tangent_rms"]:
        for base_seed in perturbation["seeds"]:
            perturbed = smoothed_tangent_perturbation(
                data,
                normals_by_mode[normal_mode],
                tangents[normal_mode],
                seed=_derived_seed(int(base_seed), family_id, case_id, phase),
                relative_amplitude=float(amplitude),
                smoothing_steps=int(perturbation["smoothing_steps"]),
            )
            points = extract_critical_points(
                data.points,
                triangles,
                perturbed,
                phase=phase,
                interior_margin=float(representation["critical_point_interior_margin"]),
                determinant_relative_floor=float(
                    representation["critical_point_determinant_relative_floor"]
                ),
            )
            forward, backward = bidirectional_signed_recall(
                base,
                points,
                radius=edge
                * float(representation["primary_matching_radius_median_edge_multiplier"]),
            )
            passed = (
                min(forward, backward)
                >= float(thresholds["minimum_pairwise_bidirectional_signed_recall"])
                and abs(len(points) - len(base))
                <= int(thresholds["maximum_perturbation_count_difference"])
                and abs(
                    sum(point.signed_index for point in points)
                    - sum(point.signed_index for point in base)
                )
                <= int(thresholds["maximum_perturbation_total_index_difference"])
            )
            perturbation_rows.append(
                {
                    "amplitude": float(amplitude),
                    "seed": int(base_seed),
                    "minimum_bidirectional_signed_recall": min(forward, backward),
                    "critical_point_count": len(points),
                    "pass": passed,
                }
            )
    primary_rows = [
        row for row in perturbation_rows if row["amplitude"] == primary_amplitude
    ]
    perturbation_pass = len(primary_rows) == len(perturbation["seeds"]) and sum(
        row["pass"] for row in primary_rows
    ) >= int(
        thresholds["minimum_passing_perturbation_seeds"]
    )
    checks = {
        "informative": informative,
        "tangency": tangency_pass,
        "discretization": discretization_pass,
        "perturbation": perturbation_pass,
    }
    return {
        "family_id": family_id,
        "case_id": case_id,
        "phase": phase,
        "median_edge_length": edge,
        "critical_point_counts": counts_by_key,
        "signed_index_totals": signed_by_key,
        "tangency": tangency,
        "radius_sensitivity": radius_rows,
        "perturbations": perturbation_rows,
        "checks": checks,
        "pass": all(checks.values()),
    }


def aggregate_family(
    *,
    family_id: str,
    case_id: int,
    phase_rows: list[dict[str, Any]],
    mesh_static: bool,
    config: dict[str, Any],
) -> dict[str, Any]:
    expected = set(config["selection"]["phases"])
    observed = {row["phase"] for row in phase_rows}
    if observed != expected or len(phase_rows) != len(expected):
        raise StabilityP0Error("family phase panel is incomplete or duplicated")
    family_gate = config["family_gate"]
    passing = sum(bool(row["pass"]) for row in phase_rows)
    informative = sum(bool(row["checks"]["informative"]) for row in phase_rows)
    passed = (
        mesh_static
        and passing >= int(family_gate["required_passing_phases_of_5"])
        and informative >= int(family_gate["required_informative_phases_of_5"])
    )
    return {
        "family_id": family_id,
        "case_id": case_id,
        "mesh_static": mesh_static,
        "passing_phases": passing,
        "informative_phases": informative,
        "pass": passed,
        "phases": phase_rows,
    }


def aggregate_p0(
    family_rows: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    expected = {row["family_id"] for row in config["selection"]["selected"]}
    observed = {row["family_id"] for row in family_rows}
    if observed != expected or len(family_rows) != len(expected):
        raise StabilityP0Error("P0 family panel is incomplete or duplicated")
    passing = sum(bool(row["pass"]) for row in family_rows)
    passed = passing >= int(config["overall_gate"]["required_passing_families_of_12"])
    return {
        "schema_version": "aurora.aneumo_transient_structure_stability_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "state": "scientific_pass" if passed else "scientific_fail",
        "passing_families": passing,
        "total_families": len(family_rows),
        "all_primary_gate_groups_noncompensatory": True,
        "method_or_architecture_selected": False,
        "gpu_used": False,
        "paper_identity_active": False,
        "families": family_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    if not args.validate_only:
        raise SystemExit(
            "P0 v1 was withdrawn before field access: authoritative family "
            "mapping and release licence resolutions are required before a "
            "separately registered successor"
        )
    print(
        json.dumps(
            {
                "protocol_id": config["protocol_id"],
                "status": config["status"],
                "selected_families": len(config["selection"]["selected"]),
                "field_members_staged": 0,
                "execution_authorized": False,
                "panel_withdrawn_before_field_access": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
