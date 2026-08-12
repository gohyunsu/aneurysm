import copy
import math
import unittest
from pathlib import Path

from aurora.aneux_nested_orbit_p0_v2 import (
    NestedOrbitP0V2Error,
    OrbitPrediction,
    load_config,
    orbit_mean_brier_residual,
    patient_bootstrap,
    point_estimates,
    probability_range,
    spearman,
    surface_signature,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneux_nested_orbit_p0_v2.json"


class NestedOrbitP0V2Tests(unittest.TestCase):
    def test_registered_contract_is_valid_and_non_executable(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(len(validate_config(config)), 6)
        self.assertIsNone(config["data_boundary"]["exact_dataset_root"])
        self.assertFalse(config["data_boundary"]["reader_dependency_preflight_passed"])
        self.assertFalse(config["execution"]["job_submitted"])

    def test_area_005_only_source_fact_cannot_be_silently_relabelled(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["source"]["morphometry_table_resolution"] = "all_resolutions"
        with self.assertRaisesRegex(NestedOrbitP0V2Error, "source correction"):
            validate_config(config)

    def test_decision_flip_cannot_be_promoted_to_primary(self) -> None:
        config = copy.deepcopy(load_config(CONFIG))
        config["checks"]["decision_flip_is_primary"] = True
        with self.assertRaisesRegex(NestedOrbitP0V2Error, "gate"):
            validate_config(config)

    def test_probability_range_and_orbit_mean_error_are_separate(self) -> None:
        row = OrbitPrediction("p1", "l1", 1, 0.2, 0.5, 0.8)
        self.assertAlmostEqual(probability_range(row), 0.6)
        self.assertAlmostEqual(orbit_mean_brier_residual(row), 0.25)

    def test_spearman_uses_average_ranks(self) -> None:
        self.assertAlmostEqual(spearman([1.0, 2.0, 2.0, 4.0], [1.0, 2.0, 2.0, 4.0]), 1.0)
        self.assertAlmostEqual(spearman([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]), 0.0)

    def test_surface_signature_is_invariant_to_planar_subdivision(self) -> None:
        coarse_points = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
        coarse_faces = [(0, 1, 2), (0, 2, 3)]
        refined_points = coarse_points + [(0, 0, 0)]
        refined_faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        coarse = surface_signature(coarse_points, coarse_faces)
        refined = surface_signature(refined_points, refined_faces)
        for left, right in zip(coarse, refined):
            self.assertAlmostEqual(left, right, places=11)

    def test_surface_signature_is_rigid_invariant_and_scale_explicit(self) -> None:
        points = [(-1, -1, 0), (1, -1, 0), (1, 1, 1), (-1, 1, 0)]
        faces = [(0, 1, 2), (0, 2, 3)]
        rigid = [(3 - y, -2 + x, 5 + z) for x, y, z in points]
        original = surface_signature(points, faces)
        transformed = surface_signature(rigid, faces)
        for left, right in zip(original, transformed):
            self.assertAlmostEqual(left, right, places=11)

        scaled = surface_signature([(2 * x, 2 * y, 2 * z) for x, y, z in points], faces)
        self.assertAlmostEqual(scaled[0] - original[0], math.log(4.0), places=11)
        self.assertAlmostEqual(scaled[1] - original[1], math.log(2.0), places=11)
        self.assertAlmostEqual(scaled[2] - original[2], math.log(4.0), places=11)
        for index in range(3, 11):
            self.assertAlmostEqual(scaled[index], original[index], places=10)

    def test_surface_signature_rejects_nonmanifold_or_closed_primary_mesh(self) -> None:
        points = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)]
        with self.assertRaisesRegex(NestedOrbitP0V2Error, "non-manifold"):
            surface_signature(points, [(0, 1, 2), (0, 3, 1), (0, 1, 4)])
        tetrahedron_points = [points[0], points[1], points[2], points[4]]
        tetrahedron = [(0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)]
        with self.assertRaisesRegex(NestedOrbitP0V2Error, "boundary perimeter"):
            surface_signature(tetrahedron_points, tetrahedron)

    def test_point_estimates_detect_signal_and_casewise_disagreement(self) -> None:
        rows = [
            OrbitPrediction("p1", "l1", 0, 0.05, 0.10, 0.08),
            OrbitPrediction("p2", "l2", 0, 0.10, 0.25, 0.15),
            OrbitPrediction("p3", "l3", 1, 0.40, 0.85, 0.75),
            OrbitPrediction("p4", "l4", 1, 0.75, 0.80, 0.90),
        ]
        result = point_estimates(rows)
        self.assertEqual(result["canonical_area_005_auc"], 1.0)
        self.assertEqual(result["fraction_probability_range_gt_0_10"], 0.75)
        self.assertTrue(-1.0 <= result["range_error_spearman"] <= 1.0)

    def test_patient_bootstrap_keeps_multilesion_clusters(self) -> None:
        rows = [
            OrbitPrediction("p1", "l1", 0, 0.05, 0.10, 0.08),
            OrbitPrediction("p1", "l2", 0, 0.10, 0.20, 0.12),
            OrbitPrediction("p2", "l3", 0, 0.15, 0.30, 0.20),
            OrbitPrediction("p3", "l4", 1, 0.50, 0.85, 0.75),
            OrbitPrediction("p4", "l5", 1, 0.75, 0.80, 0.90),
            OrbitPrediction("p4", "l6", 1, 0.65, 0.90, 0.85),
        ]
        first = patient_bootstrap(rows, replicates=50, seed=314159)
        second = patient_bootstrap(rows, replicates=50, seed=314159)
        self.assertEqual(first, second)
        self.assertEqual(first["canonical_area_005_auc"]["estimate"], 1.0)
        for interval in first.values():
            self.assertLessEqual(interval["lower"], interval["estimate"])
            self.assertLessEqual(interval["estimate"], interval["upper"])

    def test_bootstrap_resampling_is_not_reduced_to_patient_permutations(self) -> None:
        rows = [
            OrbitPrediction("p1", "l1", 0, 0.05, 0.10, 0.08),
            OrbitPrediction("p2", "l2", 0, 0.10, 0.15, 0.12),
            OrbitPrediction("p3", "l3", 1, 0.40, 0.85, 0.75),
            OrbitPrediction("p4", "l4", 1, 0.75, 0.80, 0.90),
        ]
        result = patient_bootstrap(rows, replicates=200, seed=7)
        interval = result["fraction_probability_range_gt_0_10"]
        self.assertLess(interval["lower"], interval["upper"])

    def test_duplicate_lesion_and_invalid_probability_fail_closed(self) -> None:
        duplicate = [
            OrbitPrediction("p1", "l1", 0, 0.1, 0.2, 0.3),
            OrbitPrediction("p2", "l1", 1, 0.7, 0.8, 0.9),
        ]
        with self.assertRaisesRegex(NestedOrbitP0V2Error, "unique"):
            point_estimates(duplicate)
        with self.assertRaisesRegex(NestedOrbitP0V2Error, "probabilities"):
            point_estimates([OrbitPrediction("p1", "l1", 0, -0.1, 0.2, 0.3)])


if __name__ == "__main__":
    unittest.main()
