"""Validate and score the prospective AneuX resolution-reliability P0 v2.

The module is deliberately network- and mesh-reader-free.  It freezes the
scientific contract and provides deterministic aggregate metrics for synthetic
tests and, later, a separately frozen PBS execution envelope.  No dataset is
opened by importing or validating this module.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class NestedOrbitP0V2Error(ValueError):
    """Raised when the prospective v2 boundary or aggregate rows are invalid."""


@dataclass(frozen=True)
class OrbitPrediction:
    """Cross-fitted probabilities for one eligible lesion orbit."""

    patient_id: str
    lesion_id: str
    label: int
    original: float
    area_001: float
    area_005: float

    @property
    def probabilities(self) -> tuple[float, float, float]:
        return (self.original, self.area_001, self.area_005)


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise NestedOrbitP0V2Error(f"invalid config: {exc}") from exc
    if not isinstance(payload, dict):
        raise NestedOrbitP0V2Error("config root must be an object")
    validate_config(payload)
    return payload


def _all_false(mapping: Mapping[str, Any], keys: Sequence[str]) -> bool:
    return all(mapping.get(key) is False for key in keys)


def validate_config(config: Mapping[str, Any]) -> list[str]:
    """Reject any silent change to the pre-execution v2 scientific contract."""

    if config.get("schema_version") != "aurora.aneux_nested_orbit_p0.v2":
        raise NestedOrbitP0V2Error("schema changed")
    if (
        config.get("experiment_id")
        != "aneux_resolution_reliability_nontriviality_p0_v2"
        or config.get("status")
        != "prospectively_registered_pre_execution_exact_private_path_and_reader_preflight_pending"
    ):
        raise NestedOrbitP0V2Error("registration state changed")

    supersession = config.get("supersession", {})
    if (
        supersession.get("superseded_config")
        != "configs/aneux_nested_orbit_p0.json"
        or supersession.get("superseded_config_sha256")
        != "b82e3606ea76697dbdc44973a287538a436fe330c25edcd8bf9f113d147149c1"
        or supersession.get("superseded_status")
        != "pre_execution_zero_dataset_rows_zero_job_zero_scientific_endpoints"
        or supersession.get("post_result_repair") is not False
        or supersession.get("historical_job_115177_repaired_or_rerun") is not False
    ):
        raise NestedOrbitP0V2Error("prospective supersession boundary changed")

    source = config.get("source", {})
    if (
        source.get("dataset") != "AneuX"
        or source.get("version") != "v1.0"
        or source.get("source_reported_lesions") != 750
        or source.get("source_reported_patients") != 605
        or source.get("source_reported_status_observed") != 735
        or source.get("source_reported_patient_id_observed_rows") != 637
        or source.get("mesh_resolutions")
        != ["original", "area-001", "area-005"]
        or source.get("primary_cut") != "dome"
        or source.get("morphometry_table_resolution") != "area-005_only"
        or source.get("official_code_head")
        != "a6b355e8f271e9a88399a2e432ed924d99b85d64"
        or source.get("official_feature_recomputation_available") is not False
    ):
        raise NestedOrbitP0V2Error("source correction changed")

    features = config.get("surface_signature", {})
    expected_features = [
        "log_total_surface_area",
        "log_boundary_perimeter",
        "log_surface_centroid_covariance_trace",
        "log_covariance_eigenvalue_1_over_3",
        "log_covariance_eigenvalue_2_over_3",
        "surface_area_over_covariance_trace",
        "boundary_perimeter_squared_over_surface_area",
        "radial_fourth_moment_over_covariance_trace_squared",
        "radial_sixth_moment_over_covariance_trace_cubed",
        "normal_tensor_eigenvalue_1",
        "normal_tensor_eigenvalue_2",
    ]
    if (
        features.get("features_in_order") != expected_features
        or features.get("implementation_status")
        != "frozen_and_unit_tested_reader_not_yet_verified_on_private_holding"
        or features.get("cell_rule")
        != "all_primary_surface_cells_must_be_non_degenerate_triangles_non_manifold_edges_fail"
        or features.get("weighting")
        != "exact_uniform_area_integrals_over_each_piecewise_planar_triangle"
        or features.get("eigenvalue_order") != "descending"
        or features.get("eigenvalue_floor_relative_to_covariance_trace") != 1e-12
        or features.get("mesh_density_or_face_count_feature_allowed") is not False
        or features.get("volume_or_watertightness_required") is not False
        or features.get("random_surface_sampling_allowed") is not False
        or features.get("rotation_translation_invariant") is not True
        or features.get("scale_signal_retained") is not True
    ):
        raise NestedOrbitP0V2Error("surface signature changed")

    crossfit = config.get("cross_fitting", {})
    if (
        crossfit.get("development_sources") != ["hug2016", "hug2016snf"]
        or crossfit.get("locked_external_sources") != ["aneurist", "aneurisk"]
        or crossfit.get("outer_folds") != 5
        or crossfit.get("inner_folds") != 4
        or crossfit.get("fold_seed") != 271828
        or crossfit.get("canonical_training_view") != "dome_area-005"
        or crossfit.get("held_out_prediction_views")
        != ["dome_original", "dome_area-001", "dome_area-005"]
        or crossfit.get("c_grid") != [0.01, 0.1, 1.0, 10.0, 100.0]
        or crossfit.get("tie_break") != "smallest_c"
        or crossfit.get("threshold_selected_from_data") is not False
        or crossfit.get("all_lesions_and_views_for_a_patient_are_atomic") is not True
    ):
        raise NestedOrbitP0V2Error("cross-fitting boundary changed")

    bootstrap = config.get("bootstrap", {})
    if (
        bootstrap.get("unit") != "source_qualified_patient"
        or bootstrap.get("replicates") != 2000
        or bootstrap.get("seed") != 314159
        or bootstrap.get("confidence_level") != 0.95
        or bootstrap.get("interval") != "percentile"
        or bootstrap.get("quantile_method") != "linear"
    ):
        raise NestedOrbitP0V2Error("bootstrap boundary changed")

    checks = config.get("checks", {})
    observed = [
        (row.get("endpoint"), row.get("criterion"))
        for row in checks.get("both_nontriviality_checks_required", [])
    ]
    expected = [
        (
            "fraction_of_eligible_lesions_with_cross_resolution_probability_range_gt_0_10",
            "patient_bootstrap_95pct_lower_bound_gt_0_05",
        ),
        (
            "spearman_between_probability_range_and_orbit_mean_brier_residual",
            "patient_bootstrap_95pct_lower_bound_gt_0_10",
        ),
    ]
    if (
        observed != expected
        or checks.get("decision_flip_is_primary") is not False
        or "canonical_area_005_oof_auroc_patient_bootstrap_95pct_lower_bound_gt_0_60"
        not in checks.get("all_asset_and_adequacy_checks_required", [])
    ):
        raise NestedOrbitP0V2Error("adequacy or nontriviality gate changed")

    data = config.get("data_boundary", {})
    if (
        data.get("private_holding_only") is not True
        or data.get("raw_or_case_level_payload_in_public_repository") is not False
        or data.get("exact_dataset_root") is not None
        or data.get("exact_manifest_sha256") is not None
        or data.get("reader_dependency_preflight_passed") is not False
        or data.get("execution_envelope_frozen") is not False
        or data.get("multi_lesion_patient_action")
        != "keep_all_lesions_in_one_fold_and_bootstrap_cluster"
    ):
        raise NestedOrbitP0V2Error("private data boundary changed")

    execution = config.get("execution", {})
    if (
        execution.get("server") != "introai9"
        or execution.get("scheduler") != "pbs"
        or execution.get("resources") != "select=1:ncpus=4:mem=16gb:ngpus=0"
        or execution.get("gpu_requested") is not False
        or execution.get("login_node_gpu_command") is not False
        or execution.get("network_access") is not False
        or execution.get("excluded_server") != "junjinyong"
        or execution.get("server_queried_for_v2") is not False
        or execution.get("job_submitted") is not False
    ):
        raise NestedOrbitP0V2Error("execution boundary changed")

    state = config.get("scientific_state", {})
    if state.get("conditional_source_lead") is not True or not _all_false(
        state,
        (
            "primary_problem_selected",
            "method_selected",
            "architecture_selected",
            "gpu_training_authorized",
            "outer_test_authorized",
            "submission_identity_active",
            "paper_claim_active",
        ),
    ):
        raise NestedOrbitP0V2Error("scientific state overclaimed")

    return [
        "prospective v1 supersession",
        "area-005-only morphometry correction",
        "fixed deterministic surface signature",
        "patient-grouped nested cross-fitting",
        "threshold-free primary materiality gate",
        "introai9 CPU-only pending-execution boundary",
    ]


Vector3 = tuple[float, float, float]
Triangle = tuple[int, int, int]
Matrix3 = list[list[float]]


def _subtract(left: Vector3, right: Vector3) -> Vector3:
    return tuple(left[index] - right[index] for index in range(3))  # type: ignore[return-value]


def _dot(left: Vector3, right: Vector3) -> float:
    return sum(left[index] * right[index] for index in range(3))


def _cross(left: Vector3, right: Vector3) -> Vector3:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _norm(vector: Vector3) -> float:
    return math.sqrt(_dot(vector, vector))


def _symmetric_eigenvalues(matrix: Matrix3) -> tuple[float, float, float]:
    """Return descending eigenvalues of one finite real symmetric 3x3 matrix."""

    if any(not math.isfinite(value) for row in matrix for value in row):
        raise NestedOrbitP0V2Error("matrix entries must be finite")
    off_diagonal_square = (
        matrix[0][1] ** 2 + matrix[0][2] ** 2 + matrix[1][2] ** 2
    )
    if off_diagonal_square == 0.0:
        return tuple(sorted((matrix[0][0], matrix[1][1], matrix[2][2]), reverse=True))
    mean = (matrix[0][0] + matrix[1][1] + matrix[2][2]) / 3.0
    scale_square = (
        (matrix[0][0] - mean) ** 2
        + (matrix[1][1] - mean) ** 2
        + (matrix[2][2] - mean) ** 2
        + 2.0 * off_diagonal_square
    ) / 6.0
    scale = math.sqrt(scale_square)
    normalized = [
        [
            (matrix[row][column] - (mean if row == column else 0.0)) / scale
            for column in range(3)
        ]
        for row in range(3)
    ]
    determinant = (
        normalized[0][0]
        * (normalized[1][1] * normalized[2][2] - normalized[1][2] * normalized[2][1])
        - normalized[0][1]
        * (normalized[1][0] * normalized[2][2] - normalized[1][2] * normalized[2][0])
        + normalized[0][2]
        * (normalized[1][0] * normalized[2][1] - normalized[1][1] * normalized[2][0])
    )
    angle = math.acos(max(-1.0, min(1.0, determinant / 2.0))) / 3.0
    values = [
        mean + 2.0 * scale * math.cos(angle),
        mean + 2.0 * scale * math.cos(angle + 2.0 * math.pi / 3.0),
    ]
    values.append(3.0 * mean - values[0] - values[1])
    return tuple(sorted(values, reverse=True))  # type: ignore[return-value]


def _add_polynomials(
    target: dict[tuple[int, int, int], float],
    source: Mapping[tuple[int, int, int], float],
) -> None:
    for exponents, coefficient in source.items():
        target[exponents] = target.get(exponents, 0.0) + coefficient


def _multiply_polynomials(
    left: Mapping[tuple[int, int, int], float],
    right: Mapping[tuple[int, int, int], float],
) -> dict[tuple[int, int, int], float]:
    result: dict[tuple[int, int, int], float] = {}
    for left_exp, left_coefficient in left.items():
        for right_exp, right_coefficient in right.items():
            exponent = tuple(left_exp[index] + right_exp[index] for index in range(3))
            result[exponent] = result.get(exponent, 0.0) + left_coefficient * right_coefficient
    return result


def _triangle_radial_even_moment(vertices: Sequence[Vector3], power: int) -> float:
    """Exact E[||X||^(2*power)] for uniform area on one triangle."""

    quadratic: dict[tuple[int, int, int], float] = {}
    for row in range(3):
        for column in range(3):
            exponent = [0, 0, 0]
            exponent[row] += 1
            exponent[column] += 1
            term = {tuple(exponent): _dot(vertices[row], vertices[column])}
            _add_polynomials(quadratic, term)
    polynomial: dict[tuple[int, int, int], float] = {(0, 0, 0): 1.0}
    for _ in range(power):
        polynomial = _multiply_polynomials(polynomial, quadratic)
    degree = 2 * power
    denominator = math.factorial(degree + 2)
    expectation = 0.0
    for exponents, coefficient in polynomial.items():
        dirichlet_moment = (
            2.0
            * math.factorial(exponents[0])
            * math.factorial(exponents[1])
            * math.factorial(exponents[2])
            / denominator
        )
        expectation += coefficient * dirichlet_moment
    return expectation


def surface_signature(
    points: Sequence[Sequence[float]], triangles: Sequence[Sequence[int]]
) -> tuple[float, ...]:
    """Compute the frozen 11-feature density-independent surface signature.

    Integrals are exact for the supplied piecewise-planar triangle surface.
    The function intentionally does not parse VTP; reader validation remains a
    separate pre-execution gate tied to the exact private holding.
    """

    vertices: list[Vector3] = []
    for point in points:
        if len(point) != 3:
            raise NestedOrbitP0V2Error("each point must have three coordinates")
        vector = (float(point[0]), float(point[1]), float(point[2]))
        if not all(math.isfinite(value) for value in vector):
            raise NestedOrbitP0V2Error("point coordinates must be finite")
        vertices.append(vector)
    if len(vertices) < 3 or not triangles:
        raise NestedOrbitP0V2Error("surface requires points and triangles")

    faces: list[Triangle] = []
    edge_counts: Counter[tuple[int, int]] = Counter()
    areas: list[float] = []
    normals: list[Vector3] = []
    for cell in triangles:
        if len(cell) != 3:
            raise NestedOrbitP0V2Error("all primary cells must be triangles")
        face = (int(cell[0]), int(cell[1]), int(cell[2]))
        if len(set(face)) != 3 or any(index < 0 or index >= len(vertices) for index in face):
            raise NestedOrbitP0V2Error("triangle indices must be distinct and in range")
        a, b, c = (vertices[index] for index in face)
        cross = _cross(_subtract(b, a), _subtract(c, a))
        doubled_area = _norm(cross)
        if not math.isfinite(doubled_area) or doubled_area <= 0.0:
            raise NestedOrbitP0V2Error("triangles must have positive finite area")
        area = doubled_area / 2.0
        faces.append(face)
        areas.append(area)
        normals.append(tuple(value / doubled_area for value in cross))  # type: ignore[arg-type]
        for first, second in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge_counts[tuple(sorted((first, second)))] += 1
    if any(count > 2 for count in edge_counts.values()):
        raise NestedOrbitP0V2Error("non-manifold edge detected")

    total_area = sum(areas)
    first_moment = [0.0, 0.0, 0.0]
    raw_second = [[0.0] * 3 for _ in range(3)]
    normal_tensor = [[0.0] * 3 for _ in range(3)]
    for face, area, normal in zip(faces, areas, normals):
        triangle_vertices = [vertices[index] for index in face]
        centroid = [sum(vertex[axis] for vertex in triangle_vertices) / 3.0 for axis in range(3)]
        for row in range(3):
            first_moment[row] += area * centroid[row]
            for column in range(3):
                vertex_outer_sum = sum(
                    vertex[row] * vertex[column] for vertex in triangle_vertices
                )
                raw_second[row][column] += area * (
                    9.0 * centroid[row] * centroid[column] + vertex_outer_sum
                ) / 12.0
                normal_tensor[row][column] += area * normal[row] * normal[column]
    centroid = tuple(value / total_area for value in first_moment)
    covariance = [
        [
            raw_second[row][column] / total_area
            - centroid[row] * centroid[column]
            for column in range(3)
        ]
        for row in range(3)
    ]
    covariance_trace = sum(covariance[index][index] for index in range(3))
    if not math.isfinite(covariance_trace) or covariance_trace <= 0.0:
        raise NestedOrbitP0V2Error("surface covariance must have positive trace")
    covariance_eigenvalues = _symmetric_eigenvalues(covariance)
    floor = 1e-12 * covariance_trace
    covariance_eigenvalues = tuple(max(value, floor) for value in covariance_eigenvalues)

    boundary_perimeter = sum(
        _norm(_subtract(vertices[first], vertices[second]))
        for (first, second), count in edge_counts.items()
        if count == 1
    )
    if not math.isfinite(boundary_perimeter) or boundary_perimeter <= 0.0:
        raise NestedOrbitP0V2Error("primary dome surface must have a positive boundary perimeter")

    radial_fourth = 0.0
    radial_sixth = 0.0
    for face, area in zip(faces, areas):
        centered = [_subtract(vertices[index], centroid) for index in face]
        radial_fourth += area * _triangle_radial_even_moment(centered, 2)
        radial_sixth += area * _triangle_radial_even_moment(centered, 3)
    radial_fourth /= total_area
    radial_sixth /= total_area

    normalized_normal_tensor = [
        [value / total_area for value in row] for row in normal_tensor
    ]
    normal_eigenvalues = _symmetric_eigenvalues(normalized_normal_tensor)
    first, second, third = covariance_eigenvalues
    signature = (
        math.log(total_area),
        math.log(boundary_perimeter),
        math.log(covariance_trace),
        math.log(first / third),
        math.log(second / third),
        total_area / covariance_trace,
        boundary_perimeter**2 / total_area,
        radial_fourth / covariance_trace**2,
        radial_sixth / covariance_trace**3,
        normal_eigenvalues[0],
        normal_eigenvalues[1],
    )
    if any(not math.isfinite(value) for value in signature):
        raise NestedOrbitP0V2Error("surface signature must be finite")
    return signature


def _validate_predictions(
    rows: Iterable[OrbitPrediction], *, require_unique_lesions: bool = True
) -> list[OrbitPrediction]:
    materialized = list(rows)
    if not materialized:
        raise NestedOrbitP0V2Error("prediction rows are empty")
    seen: set[str] = set()
    for row in materialized:
        if (
            not row.patient_id
            or not row.lesion_id
            or (require_unique_lesions and row.lesion_id in seen)
        ):
            raise NestedOrbitP0V2Error("patient/lesion keys must be nonempty and unique")
        seen.add(row.lesion_id)
        if row.label not in (0, 1):
            raise NestedOrbitP0V2Error("label must be binary")
        if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in row.probabilities):
            raise NestedOrbitP0V2Error("probabilities must be finite and in [0, 1]")
    return materialized


def probability_range(row: OrbitPrediction) -> float:
    """Return max-minus-min across the three fixed-cut resolution views."""

    return max(row.probabilities) - min(row.probabilities)


def orbit_mean_brier_residual(row: OrbitPrediction) -> float:
    """Return squared error of the orbit-mean probability, avoiding variance leakage."""

    mean_probability = sum(row.probabilities) / 3.0
    return (mean_probability - row.label) ** 2


def _average_ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and values[order[end]] == values[order[cursor]]:
            end += 1
        rank = (cursor + 1 + end) / 2.0
        for position in range(cursor, end):
            ranks[order[position]] = rank
        cursor = end
    return ranks


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman correlation with average ranks and a finite constant-input result."""

    if len(x) != len(y) or len(x) < 2:
        raise NestedOrbitP0V2Error("spearman requires equal vectors of length at least two")
    rank_x = _average_ranks(x)
    rank_y = _average_ranks(y)
    mean_x = sum(rank_x) / len(rank_x)
    mean_y = sum(rank_y) / len(rank_y)
    covariance = sum((a - mean_x) * (b - mean_y) for a, b in zip(rank_x, rank_y))
    variance_x = sum((a - mean_x) ** 2 for a in rank_x)
    variance_y = sum((b - mean_y) ** 2 for b in rank_y)
    denominator = math.sqrt(variance_x * variance_y)
    return 0.0 if denominator == 0.0 else covariance / denominator


def roc_auc(labels: Sequence[int], probabilities: Sequence[float]) -> float:
    """Binary AUROC computed from average ranks, including probability ties."""

    if len(labels) != len(probabilities) or not labels:
        raise NestedOrbitP0V2Error("auc inputs must be nonempty and aligned")
    positive = sum(labels)
    negative = len(labels) - positive
    if positive == 0 or negative == 0:
        raise NestedOrbitP0V2Error("auc requires both classes")
    ranks = _average_ranks(probabilities)
    positive_rank_sum = sum(rank for rank, label in zip(ranks, labels) if label == 1)
    return (positive_rank_sum - positive * (positive + 1) / 2.0) / (positive * negative)


def point_estimates(
    rows: Iterable[OrbitPrediction], *, allow_bootstrap_multiplicity: bool = False
) -> dict[str, float]:
    """Compute the three preregistered aggregate point estimates."""

    records = _validate_predictions(
        rows, require_unique_lesions=not allow_bootstrap_multiplicity
    )
    ranges = [probability_range(row) for row in records]
    residuals = [orbit_mean_brier_residual(row) for row in records]
    return {
        "canonical_area_005_auc": roc_auc(
            [row.label for row in records], [row.area_005 for row in records]
        ),
        "fraction_probability_range_gt_0_10": sum(value > 0.10 for value in ranges)
        / len(ranges),
        "range_error_spearman": spearman(ranges, residuals),
    }


def _linear_quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered or not 0.0 <= probability <= 1.0:
        raise NestedOrbitP0V2Error("invalid quantile request")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def patient_bootstrap(
    rows: Iterable[OrbitPrediction], *, replicates: int = 2000, seed: int = 314159
) -> dict[str, dict[str, float]]:
    """Percentile CIs from patient-cluster resampling with lesion multiplicity."""

    records = _validate_predictions(rows)
    if replicates < 1:
        raise NestedOrbitP0V2Error("bootstrap replicates must be positive")
    by_patient: dict[str, list[OrbitPrediction]] = {}
    for row in records:
        by_patient.setdefault(row.patient_id, []).append(row)
    patients = sorted(by_patient)
    if len(patients) < 2:
        raise NestedOrbitP0V2Error("bootstrap requires at least two patients")

    rng = random.Random(seed)
    samples: dict[str, list[float]] = {
        "canonical_area_005_auc": [],
        "fraction_probability_range_gt_0_10": [],
        "range_error_spearman": [],
    }
    attempts = 0
    maximum_attempts = replicates * 20
    while len(samples["canonical_area_005_auc"]) < replicates and attempts < maximum_attempts:
        attempts += 1
        sampled_rows: list[OrbitPrediction] = []
        for _ in patients:
            sampled_rows.extend(by_patient[rng.choice(patients)])
        try:
            estimate = point_estimates(
                sampled_rows, allow_bootstrap_multiplicity=True
            )
        except NestedOrbitP0V2Error:
            continue
        for key, value in estimate.items():
            samples[key].append(value)
    if len(samples["canonical_area_005_auc"]) != replicates:
        raise NestedOrbitP0V2Error("bootstrap could not obtain class-valid replicates")

    result: dict[str, dict[str, float]] = {}
    observed = point_estimates(records)
    for key, values in samples.items():
        result[key] = {
            "estimate": observed[key],
            "lower": _linear_quantile(values, 0.025),
            "upper": _linear_quantile(values, 0.975),
        }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    checks = validate_config(load_config(args.config))
    print(json.dumps({"status": "valid", "checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
