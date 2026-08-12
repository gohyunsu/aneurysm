from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.response_fidelity import (
    ResponseFidelityError,
    coordinate_hash_partition,
    discrete_curvature,
    discrete_tangent,
    leave_one_interior_flow_error,
    load_p0_config,
    response_metrics,
    validate_case,
)

try:
    import numpy as np
except ImportError:  # pragma: no cover - lightweight local environment
    np = None


ROOT = Path(__file__).parents[1]


@unittest.skipIf(np is None, "response-fidelity tests require numpy")
class ResponseFidelityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = ROOT / "configs" / "aneumo_response_fidelity_p0.json"
        self.flows = np.asarray(
            [0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.00375, 0.004],
            dtype=np.float64,
        )
        self.coordinates = np.arange(96, dtype=np.float64).reshape(32, 3) / 100.0
        base = np.column_stack(
            [
                np.linspace(0.2, 1.0, 32),
                np.linspace(-0.4, 0.5, 32),
                np.linspace(0.1, 0.7, 32),
            ]
        )
        self.velocity = np.asarray(
            [base * flow + (base * base) * flow * flow for flow in self.flows]
        )

    def test_config_is_registered_but_non_executable(self) -> None:
        config = load_p0_config(self.config_path)
        self.assertEqual(config["source"]["allowed_split"], "train")
        self.assertFalse(config["source"]["pressure_read_allowed"])
        self.assertIsNone(config["source"]["exact_private_cache_path"])
        self.assertFalse(config["execution"]["executable"])
        self.assertEqual(config["execution"]["gpu"], 0)
        self.assertFalse(config["execution"]["junjinyong_allowed"])

    def test_private_path_cannot_be_invented_in_current_version(self) -> None:
        config = load_p0_config(self.config_path)
        changed = copy.deepcopy(config)
        changed["source"]["exact_private_cache_path"] = "/invented/cache.h5"
        with tempfile.TemporaryDirectory() as directory:
            changed_path = Path(directory) / "changed.json"
            changed_path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ResponseFidelityError, "invent"):
                load_p0_config(changed_path)

    def test_case_validation_and_coordinate_partition(self) -> None:
        q, xyz, velocity, anchor = validate_case(
            self.flows,
            self.coordinates,
            self.velocity,
            anchor_flow=0.0025,
        )
        self.assertEqual(anchor, 3)
        self.assertEqual(q.shape, (8,))
        self.assertEqual(xyz.shape, (32, 3))
        self.assertEqual(velocity.shape, (8, 32, 3))
        labels = coordinate_hash_partition(xyz)
        self.assertEqual(set(labels.tolist()), {0, 1})
        np.testing.assert_array_equal(labels, coordinate_hash_partition(xyz.copy()))

    def test_tangent_and_curvature_are_exact_for_quadratic_response(self) -> None:
        scalar = self.flows[:, None, None] ** 2
        tangent = discrete_tangent(self.flows, scalar)
        curvature = discrete_curvature(self.flows, scalar)
        np.testing.assert_allclose(tangent[:, 0, 0], 2.0 * self.flows, atol=1e-12)
        np.testing.assert_allclose(curvature[:, 0, 0], 2.0, atol=1e-9)

    def test_identical_prediction_has_zero_response_errors(self) -> None:
        metrics = response_metrics(
            self.flows,
            self.velocity,
            self.velocity.copy(),
            anchor_index=3,
        )
        for value in metrics.values():
            self.assertLess(abs(value), 1e-12)

    def test_matching_fields_but_wrong_anchor_changes_response_metric(self) -> None:
        prediction = self.velocity.copy()
        prediction[3] += 0.02
        metrics = response_metrics(
            self.flows,
            self.velocity,
            prediction,
            anchor_index=3,
        )
        self.assertGreater(metrics["paired_response_relative_l2"], 0.0)
        self.assertGreater(metrics["discrete_tangent_relative_l2"], 0.0)
        self.assertGreater(metrics["direction_cosine_error"], 0.0)

    def test_linear_flow_response_interpolates_exactly(self) -> None:
        linear = self.flows[:, None, None] * self.velocity[3][None, :, :]
        self.assertLess(leave_one_interior_flow_error(self.flows, linear), 1e-12)

    def test_nonincreasing_flow_grid_is_rejected(self) -> None:
        changed = self.flows.copy()
        changed[2] = changed[1]
        with self.assertRaisesRegex(ResponseFidelityError, "strictly increasing"):
            validate_case(changed, self.coordinates, self.velocity, anchor_flow=0.0025)
