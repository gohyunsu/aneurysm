from __future__ import annotations

import json
from pathlib import Path
import unittest

import torch

from aurora.aneug_cycle_decoders import RealPeriodicBasis, reconstruction_relative_l2
from aurora.aneug_cycle_representation_audit import (
    LABELS, aggregate, audit_cycle, iter_training_fields, validate_config,
)


class CycleRepresentationTests(unittest.TestCase):
    def test_dense_and_fft_reconstruction_match_even_and_odd(self):
        for count in (7, 8, 80):
            generator = torch.Generator().manual_seed(count)
            field = torch.randn(count, 5, 3, dtype=torch.float64, generator=generator)
            weight = torch.tensor([0., 1., 2., 4., 8.], dtype=torch.float64)
            cutoffs = [0, 2, count // 2]
            result = audit_cycle(field, weight, cutoffs)
            self.assertLess(result["dense_full_basis_relative_l2"], 1e-12)
            self.assertAlmostEqual(sum(result["frequency_energy_fraction"]), 1., places=12)
            for row in result["cutoffs"]:
                basis = RealPeriodicBasis(torch.arange(count).double() / count, row["max_frequency"])
                direct = float(reconstruction_relative_l2(basis, field, weight))
                self.assertAlmostEqual(row["field_relative_l2"], direct, places=12)
                self.assertAlmostEqual(row["field_relative_l2"], row["discarded_energy_relative_l2"], places=12)
            self.assertEqual(result["cutoffs"][-1]["real_coefficients"], count)

    def test_nyquist_is_retained_once_and_endpoints_not_equalized(self):
        field = torch.ones(80, 3, 3, dtype=torch.float64)
        field[1::2] *= -1
        result = audit_cycle(field, torch.ones(3), [0, 39, 40])
        self.assertAlmostEqual(result["frequency_energy_fraction"][-1], 1.)
        self.assertAlmostEqual(result["cutoffs"][1]["field_relative_l2"], 1.)
        self.assertLess(result["cutoffs"][2]["field_relative_l2"], 1e-12)
        self.assertAlmostEqual(result["boundary_step_over_cycle_rms"], 2.)

    def test_pure_mean_reports_undefined_oscillation_without_nan(self):
        result = audit_cycle(torch.ones(8, 4, 3), torch.ones(4), [0, 4])
        self.assertFalse(result["has_numerically_resolved_oscillation"])
        self.assertIsNone(result["cutoffs"][0]["oscillatory_relative_l2"])
        summary = aggregate([result], [0, 4])
        self.assertEqual(summary["cutoffs"][0]["metrics"]["oscillatory_relative_l2"]["case_count"], 0)
        json.dumps(summary, allow_nan=False)

    def test_area_scaling_and_vector_rotation_invariance(self):
        field = torch.randn(8, 3, 3, generator=torch.Generator().manual_seed(3)).double()
        areas = torch.tensor([1., 2., 7.])
        rotation = torch.tensor([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]], dtype=torch.float64)
        a = audit_cycle(field, areas, [0, 2, 4])
        b = audit_cycle(field @ rotation, areas * 3, [0, 2, 4])
        for x, y in zip(a["cutoffs"], b["cutoffs"]):
            self.assertAlmostEqual(x["field_relative_l2"], y["field_relative_l2"], places=12)
            self.assertAlmostEqual(x["tawss_normalized_absolute_error"], y["tawss_normalized_absolute_error"], places=12)

    def test_invalid_inputs_are_not_silently_averaged(self):
        field = torch.ones(8, 3, 3)
        for weights in (torch.zeros(3), torch.tensor([1., -1., 1.]), torch.full((3,), float("nan"))):
            with self.assertRaises(ValueError):
                audit_cycle(field, weights, [0, 4])
        for cutoffs in ([4, 0], [0, 5], [0, 0], [True], []):
            with self.assertRaises(ValueError):
                audit_cycle(field, torch.ones(3), cutoffs)
        with self.assertRaises(ValueError):
            audit_cycle(torch.zeros_like(field), torch.ones(3), [0])

    def payload(self):
        class NontrainingRecord(dict):
            def __getitem__(self, key):
                if key != "case":
                    raise AssertionError("nontrain record field or schema was accessed")
                return super().__getitem__(key)

        shape = (8, 3, 9)
        values = torch.ones(shape, dtype=torch.float64)
        values[..., :3] = torch.tensor([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]])
        records = [{"case": "train", "labels": LABELS, "tensor": values},
                   NontrainingRecord(case="validation"), NontrainingRecord(case="test"),
                   NontrainingRecord(case="extra")]
        transient = {"registered_data_list": records,
                     "mesh_data": {"cases": [r["case"] for r in records],
                                   "faces_list": [torch.tensor([[0, 1, 2]])]}}
        normalizer = {"label": LABELS,
                      "tensor_norm": {"mean": torch.zeros(9), "std": torch.ones(9)}}
        return transient, normalizer, shape

    def test_stream_reads_train_only_and_inverts_source_encoding(self):
        transient, normalizer, shape = self.payload()
        rows = list(iter_training_fields(transient, normalizer, ["train"],
                    ["validation", "test", "extra"], expected_shape=shape))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "train")
        torch.testing.assert_close(rows[0][1], torch.ones(8, 3, 3, dtype=torch.float64) * 1.00001)
        self.assertEqual(rows[0][3], ["case", "labels", "tensor"])
        self.assertGreater(float(rows[0][2].sum()), 0.)

    def test_stream_rejects_overlap_missing_coverage_and_bad_mesh(self):
        transient, normalizer, shape = self.payload()
        for excluded in (["train", "validation", "test", "extra"], ["validation", "test"]):
            with self.assertRaises(ValueError if len(excluded) == 2 else RuntimeError):
                list(iter_training_fields(transient, normalizer, ["train"], excluded, expected_shape=shape))
        transient["mesh_data"]["faces_list"][0][0, 0] = -1
        with self.assertRaises(ValueError):
            list(iter_training_fields(transient, normalizer, ["train"],
                 ["validation", "test", "extra"], expected_shape=shape))

    def test_public_config_preserves_opened_test_and_nominal_grid(self):
        path = Path(__file__).parents[1] / "configs/aneug_cycle_representation_audit_v3.json"
        config = json.loads(path.read_text())
        validate_config(config)
        for key, value in (("physical_timestamps_verified", True),
                           ("historical_test_already_opened", False),
                           ("field_partition", "validation"),
                           ("automatic_model_selection", True)):
            with self.assertRaises(ValueError):
                validate_config({**config, key: value})


if __name__ == "__main__":
    unittest.main()
