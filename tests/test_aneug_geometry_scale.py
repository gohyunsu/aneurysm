import copy
import math
import unittest

import torch

from aurora.aneug_geometry_scale import (
    APPLIED, RADIUS, SizePreservingSteadyStream, apply_geometry_scale, fit_geometry_scale,
)
from aurora.aneug_release_730_ghd_gps_baseline import _case_from_record
from test_aneug_release_730_matched_steady_stream import synthetic_archive, synthetic_stream


class GeometryScaleTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)

    def examples(self):
        archive, tensor, ghd, faces = synthetic_archive()
        tensor.value[2, :, :3] *= 2
        tensor.value[4, :, :3] *= 100
        stream = synthetic_stream(archive, faces)
        cases = [stream.decode(i, retain_coordinate_scale=True) for i in (0, 2)]
        return stream, cases, tensor

    def test_actual_steady_decoder_exhibits_and_corrects_lost_size(self):
        stream, cases, _ = self.examples()
        # Positive uniform dilation was exactly erased by the old descriptor.
        for key in ("coordinates", "normals", "vertex_weights"):
            torch.testing.assert_close(cases[0][key], cases[1][key], rtol=0, atol=0)
        self.assertAlmostEqual(float(cases[1][RADIUS] / cases[0][RADIUS]), 2)
        contract = fit_geometry_scale(cases, expected_train_cases=2)
        transformed = [apply_geometry_scale(c, contract) for c in cases]
        torch.testing.assert_close(transformed[1]["coordinates"], 2 * transformed[0]["coordinates"])
        for old, new in zip(cases, transformed):
            for key in old:
                if key != "coordinates":
                    self.assertIs(new[key], old[key])
            self.assertNotIn(APPLIED, old)
        legacy = stream.decode(0)
        self.assertNotIn(RADIUS, legacy)
        for key, value in legacy.items():
            torch.testing.assert_close(value, cases[0][key], rtol=0, atol=0)

    def test_fit_reads_only_train_geometry_and_freezes_the_reference(self):
        stream, cases, tracked = self.examples()
        self.assertEqual(tracked.indices, [0, 2])
        class RadiusOnly(dict):
            def __getitem__(self, key):
                if key != RADIUS:
                    raise AssertionError("normalizer read more than training radii")
                return super().__getitem__(key)
        contract = fit_geometry_scale([RadiusOnly(c) for c in cases], expected_train_cases=2)
        before = copy.deepcopy(contract)
        wrapped = SizePreservingSteadyStream(stream, contract)
        far = wrapped.decode(4)
        self.assertEqual(tracked.indices, [0, 2, 4])
        self.assertEqual(contract, before)
        expected = float(cases[0][RADIUS]) * math.sqrt(2.5)
        self.assertAlmostEqual(contract["reference_rms"], expected)
        self.assertGreater(float(far["coordinates"].square().sum(-1).mean().sqrt()), 50)
        with self.assertRaises(ValueError):
            fit_geometry_scale(cases, expected_train_cases=584)
        with self.assertRaises(Exception):
            wrapped.decode(1)  # Original row exclusion remains effective.

    def test_actual_full_size_transient_decoder_preserves_legacy_values(self):
        nodes = 13902
        triangles = nodes // 3
        points = torch.zeros(triangles, 3, 3)
        points[:, :, 0] = torch.arange(triangles)[:, None] * 3
        points[:, 1, 0] += 1
        points[:, 2, 1] = 1
        tensor = torch.zeros(80, nodes, 9)
        tensor[:, :, :3] = points.reshape(nodes, 3)
        labels = ["x", "y", "z", "x_normal", "y_normal", "z_normal", "wss_x", "wss_y", "wss_z"]
        args = (dict(labels=labels, tensor=tensor), torch.zeros(432), torch.zeros(432),
                torch.ones(432), torch.zeros(9), torch.ones(9), torch.arange(nodes).reshape(-1, 3))
        old = _case_from_record(*args)
        new = _case_from_record(*args, retain_coordinate_scale=True)
        self.assertEqual(set(new), set(old) | {RADIUS})
        for key in old:
            torch.testing.assert_close(old[key], new[key], rtol=0, atol=0)
        self.assertGreater(float(new[RADIUS]), 0)
        contract = fit_geometry_scale([new], expected_train_cases=1)
        restored = apply_geometry_scale(new, contract)
        torch.testing.assert_close(restored["coordinates"], old["coordinates"], rtol=0, atol=0)

    def test_missing_invalid_or_double_normalization_is_not_silent(self):
        _, cases, _ = self.examples()
        contract = fit_geometry_scale(cases, expected_train_cases=2)
        with self.assertRaises(ValueError):
            apply_geometry_scale(apply_geometry_scale(cases[0], contract), contract)
        for value in (torch.tensor(0.), torch.tensor(float("nan")), torch.ones(2), 1.):
            with self.subTest(value=value), self.assertRaises(ValueError):
                fit_geometry_scale([dict(cases[0], **{RADIUS: value})], expected_train_cases=1)
        for key, value in (("reference_rms", 0), ("reference_rms", True),
                           ("validation_geometry_used", True), ("profile", "casewise")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                apply_geometry_scale(cases[0], dict(contract, **{key: value}))


if __name__ == "__main__":
    unittest.main()
