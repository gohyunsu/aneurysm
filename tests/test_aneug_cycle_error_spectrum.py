import copy
import json
import math
import unittest

import torch

from aurora.aneug_cycle_error_spectrum import cycle_error_spectrum, summarize_spectra
from aurora.aneug_processed_v4_d9 import field_loss


class CycleErrorSpectrumTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)
        self.generator = torch.Generator().manual_seed(17)

    def test_matches_physical_field_loss_and_parseval_even_odd(self):
        for phases in (7, 8, 80):
            r = torch.randn(phases, 5, 3, generator=self.generator, dtype=torch.float64)
            p = r + .2 * torch.randn(r.shape, generator=self.generator, dtype=r.dtype)
            w = torch.tensor([0., 1., 2., 3., 9.], dtype=r.dtype)
            row = cycle_error_spectrum(p, r, w)
            expected = float(field_loss(p, r, w / w.sum()))
            self.assertAlmostEqual(row["field_relative_squared_error"], expected, places=12)
            self.assertAlmostEqual(sum(row["frequency_squared_error_contribution"]), expected, places=12)
            self.assertAlmostEqual(row["dc"]["squared_error_contribution"] +
                row["oscillatory"]["squared_error_contribution"], expected, places=12)
            self.assertLess(row["parseval_relative_discrepancy"], 1e-12)

    def test_known_dc_and_harmonic_errors_are_separate(self):
        t = torch.arange(80, dtype=torch.float64)
        r = (2. + torch.sin(2 * math.pi * 3 * t / 80))[:, None, None].expand(-1, 3, 3)
        p = r + .5
        row = cycle_error_spectrum(p, r, torch.ones(3))
        self.assertAlmostEqual(row["dc"]["band_relative_l2"], .25, places=12)
        self.assertLess(row["oscillatory"]["squared_error_contribution"], 1e-28)
        p2 = (2. + 1.2 * torch.sin(2 * math.pi * 3 * t / 80))[:, None, None].expand(-1, 3, 3)
        row2 = cycle_error_spectrum(p2, r, torch.ones(3))
        self.assertAlmostEqual(row2["oscillatory"]["band_relative_l2"], .2, places=12)
        self.assertLess(row2["dc"]["squared_error_contribution"], 1e-28)
        self.assertAlmostEqual(row2["frequency_squared_error_contribution"][3],
                               row2["field_relative_squared_error"], places=12)

    def test_nyquist_counted_once_without_endpoint_equalization(self):
        r = torch.ones(80, 2, 3, dtype=torch.float64)
        r[1::2] = -1
        row = cycle_error_spectrum(torch.zeros_like(r), r, torch.ones(2))
        self.assertAlmostEqual(row["frequency_reference_energy_fraction"][-1], 1.)
        self.assertAlmostEqual(row["frequency_squared_error_contribution"][-1], 1.)
        self.assertEqual(row["phase_count"], 80)
        self.assertFalse(row["physical_timestamps_verified"])

    def test_zero_reference_band_error_is_retained_not_masked_from_field(self):
        r = torch.ones(80, 2, 3, dtype=torch.float64)
        p = r.clone()
        p[1::2] += 1
        p[::2] -= 1
        row = cycle_error_spectrum(p, r, torch.ones(2))
        self.assertFalse(row["oscillatory"]["reference_support_resolved"])
        self.assertIsNone(row["oscillatory"]["band_relative_l2"])
        self.assertAlmostEqual(row["oscillatory"]["squared_error_contribution"], 1.)
        summary = summarize_spectra([row])
        self.assertEqual(summary["oscillatory"]["band_relative_l2_supported_case_count"], 0)
        self.assertAlmostEqual(summary["oscillatory"]["case_mean_squared_error_contribution"], 1.)
        json.dumps(summary, allow_nan=False)

    def test_rotation_scale_cyclic_shift_and_area_scale_invariance(self):
        r = torch.randn(80, 3, 3, generator=self.generator, dtype=torch.float64)
        p = torch.randn(r.shape, generator=self.generator, dtype=r.dtype)
        w = torch.tensor([1., 2., 7.])
        rotation = torch.tensor([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]], dtype=r.dtype)
        a = cycle_error_spectrum(p, r, w)
        b = cycle_error_spectrum((p @ rotation * 7).roll(13, 0),
                                 (r @ rotation * 7).roll(13, 0), w * 31)
        for key in ("frequency_reference_energy_fraction", "frequency_squared_error_contribution"):
            torch.testing.assert_close(torch.tensor(a[key]), torch.tensor(b[key]))

    def test_perfect_prediction_and_equal_case_not_energy_pooled_summary(self):
        r = torch.ones(8, 2, 3)
        perfect = cycle_error_spectrum(r, r, torch.ones(2))
        poor = cycle_error_spectrum(4 * r, 2 * r, torch.ones(2))
        summary = summarize_spectra([perfect, poor])
        self.assertEqual(summary["case_count"], 2)
        self.assertAlmostEqual(summary["case_mean_field_relative_l2"], .5)
        self.assertAlmostEqual(summary["case_mean_field_relative_squared_error"], .5)
        self.assertAlmostEqual(sum(summary["case_mean_frequency_squared_error_contribution"]), .5)
        self.assertFalse(summary["uncertainty_estimated"])

    def test_rejects_invalid_inputs_and_incompatible_aggregation(self):
        r = torch.ones(8, 2, 3)
        for p, reference, w in ((r[:2], r[:2], torch.ones(2)),
                (r, r, torch.zeros(2)), (r, r, torch.tensor([1., -1.])),
                (r, r, torch.tensor([1., float("nan")])),
                (r, torch.zeros_like(r), torch.ones(2)),
                (r, r.long(), torch.ones(2)), (r, r, torch.ones(3)),
                (r * float("inf"), r, torch.ones(2))):
            with self.assertRaises(ValueError):
                cycle_error_spectrum(p, reference, w)
        good = cycle_error_spectrum(r, r, torch.ones(2))
        for key, value in (("physical_timestamps_verified", True),
                           ("field_relative_squared_error", 2.),
                           ("frequency_squared_error_contribution", [0.]),
                           ("frequency_reference_energy_fraction", [float("nan")] * 5)):
            bad = copy.deepcopy(good)
            bad[key] = value
            with self.assertRaises(ValueError):
                summarize_spectra([good, bad])
        with self.assertRaises(ValueError):
            summarize_spectra([])

    def test_summary_rejects_forged_band_rows_and_support(self):
        r = torch.ones(8, 2, 3)
        row = cycle_error_spectrum(2 * r, r, torch.ones(2))
        for name, key, value in (("dc", "squared_error_contribution", 0.),
                ("dc", "band_relative_l2", -1.),
                ("oscillatory", "reference_support_resolved", True),
                ("oscillatory", "band_relative_l2", 0.)):
            bad = copy.deepcopy(row)
            bad[name][key] = value
            with self.assertRaises(ValueError):
                summarize_spectra([bad])

    def test_tiny_field_retains_common_evaluator_denominator_floor(self):
        r = torch.full((8, 2, 3), 1e-8, dtype=torch.float64)
        p, w = 2 * r, torch.ones(2, dtype=torch.float64) / 2
        row = cycle_error_spectrum(p, r, w)
        self.assertEqual(row["field_energy_denominator"], 1e-12)
        self.assertAlmostEqual(row["field_relative_squared_error"], float(field_loss(p, r, w)))
        self.assertAlmostEqual(row["dc"]["band_relative_l2"], 1.)
        summarize_spectra([row])


if __name__ == "__main__":
    unittest.main()
