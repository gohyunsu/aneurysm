from __future__ import annotations

import unittest

import torch
from torch import nn

from aurora.aneug_cycle_decoders import (
    CycleDecoderError,
    FourierCycleDecoder,
    GeometryEncodedRegimeControl,
    MaskedRegimeDecoder,
    RealPeriodicBasis,
    reconstruction_relative_l2,
)


def phases(count: int = 80, offset: float = 0) -> torch.Tensor:
    return torch.arange(count, dtype=torch.float64) / count + offset


class PeriodicBasisTests(unittest.TestCase):
    def test_full_even_basis_reconstructs_all_channels_including_nyquist(self) -> None:
        torch.manual_seed(7)
        basis = RealPeriodicBasis(phases(offset=1 / 80), 40)
        self.assertEqual(basis.coefficient_count, 80)
        torch.testing.assert_close(basis.matrix.T @ basis.matrix / 80,
                                   torch.eye(80, dtype=torch.float64))
        field = torch.randn(80, 5, 3, dtype=torch.float64)
        torch.testing.assert_close(basis.decode(basis.encode(field)), field)
        self.assertEqual(int((basis.frequencies == 40).sum()), 1)

    def test_full_odd_basis_and_dc_only(self) -> None:
        field = torch.randn(9, 4, 3, dtype=torch.float64)
        full = RealPeriodicBasis(phases(9), 4)
        torch.testing.assert_close(full.decode(full.encode(field)), field)
        dc = RealPeriodicBasis(phases(9), 0)
        torch.testing.assert_close(dc.decode(dc.encode(field)),
                                   field.mean(dim=0, keepdim=True).expand_as(field))

    def test_truncation_preserves_mean_and_has_nonincreasing_oracle_error(self) -> None:
        torch.manual_seed(9)
        field = torch.randn(80, 6, 3, dtype=torch.float64)
        weights = torch.arange(1, 7, dtype=torch.float64)
        errors = []
        for frequency in (0, 1, 4, 16, 39, 40):
            basis = RealPeriodicBasis(phases(), frequency)
            prediction = basis.decode(basis.encode(field))
            torch.testing.assert_close(prediction.mean(dim=0), field.mean(dim=0))
            errors.append(float(reconstruction_relative_l2(basis, field, weights)))
        self.assertTrue(all(a >= b for a, b in zip(errors, errors[1:])))
        self.assertLess(errors[-1], 1e-12)

    def test_grid_errors_do_not_silently_change_sampling(self) -> None:
        invalid = [torch.linspace(0, 1, 80), phases().flip(0), phases() * 0.5,
                   torch.zeros(80), torch.tensor([0.0, 0.25, float("nan"), 0.75])]
        for grid in invalid:
            with self.subTest(grid=grid[:3]):
                with self.assertRaises(CycleDecoderError):
                    RealPeriodicBasis(grid, 1)
        for frequency in (-1, 41, 1.5, True):
            with self.assertRaises(CycleDecoderError):
                RealPeriodicBasis(phases(), frequency)

    def test_physical_weighting_and_invalid_fields(self) -> None:
        basis = RealPeriodicBasis(phases(8), 0)
        field = torch.zeros(8, 2, 3, dtype=torch.float64)
        field[:, 0, 0] = 1
        field[:, 1, 0] = (-1.) ** torch.arange(8)
        actual = reconstruction_relative_l2(basis, field, torch.tensor([9., 1.]))
        self.assertAlmostEqual(float(actual), (1 / 10) ** 0.5)
        for weights in (torch.zeros(2), torch.tensor([-1., 2.]),
                        torch.tensor([float("nan"), 1.])):
            with self.assertRaises(CycleDecoderError):
                reconstruction_relative_l2(basis, field, weights)
        with self.assertRaises(CycleDecoderError):
            basis.encode(torch.full((8, 2, 3), float("nan")))

    def test_fourier_head_is_differentiable_and_has_one_field(self) -> None:
        model = FourierCycleDecoder(8, RealPeriodicBasis(phases(), 8)).double()
        features = torch.randn(4, 8, dtype=torch.float64, requires_grad=True)
        prediction = model(features)
        self.assertEqual(tuple(prediction.shape), (80, 4, 3))
        prediction.square().mean().backward()
        self.assertTrue(bool(torch.isfinite(features.grad).all()))
        self.assertTrue(all(p.grad is not None and bool(torch.isfinite(p.grad).all())
                            for p in model.coefficients.parameters()))


class MaskedRegimeTests(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(23)
        self.model = MaskedRegimeDecoder(8, phases(), phase_width=4).double()
        self.features = torch.randn(5, 8, dtype=torch.float64)

    def test_only_missing_phase_is_masked_including_last_valid_phase(self) -> None:
        with torch.no_grad():
            for parameter in self.model.phase_mlp.parameters():
                parameter.zero_()
            self.model.phase_mlp[-1].bias.fill_(2)
        condition = self.model.conditioning(torch.tensor([-1, 0, 78, 79]))
        self.assertTrue(torch.equal(condition[0], torch.zeros(4, dtype=torch.float64)))
        self.assertTrue(torch.equal(condition[1:], torch.full((3, 4), 2., dtype=torch.float64)))

    def test_missing_phase_has_no_gradient_into_time_mlp(self) -> None:
        self.model.forward_steady(self.features).square().mean().backward()
        for parameter in self.model.phase_mlp.parameters():
            self.assertTrue(parameter.grad is None or not bool(parameter.grad.any()))
        self.assertTrue(any(p.grad is not None and bool(p.grad.any())
                            for p in self.model.output.parameters()))

    def test_all_cycle_phases_train_time_conditioner(self) -> None:
        result = self.model(self.features, torch.tensor([79]))
        result.square().mean().backward()
        self.assertTrue(any(p.grad is not None and bool(p.grad.any())
                            for p in self.model.phase_mlp.parameters()))

    def test_chunked_cycle_equals_snapshot_and_full_decoder(self) -> None:
        full = self.model.forward_cycle(self.features, phase_batch_size=80)
        for size in (1, 7, 8, 31, 80, 81):
            torch.testing.assert_close(self.model.forward_cycle(self.features,
                                        phase_batch_size=size), full)
        torch.testing.assert_close(full[79], self.model(self.features, torch.tensor([79]))[0])
        self.assertEqual(tuple(full.shape), (80, 5, 3))

    def test_steady_is_not_forced_to_cycle_mean(self) -> None:
        cycle_mean = self.model.forward_cycle(self.features).mean(dim=0)
        steady = self.model.forward_steady(self.features)
        self.assertFalse(torch.allclose(steady, cycle_mean))

    def test_control_is_permutation_equivariant_over_vertices(self) -> None:
        order = torch.tensor([2, 4, 0, 3, 1])
        original = self.model.forward_cycle(self.features)
        torch.testing.assert_close(self.model.forward_cycle(self.features[order]),
                                   original[:, order])

    def test_regime_indicator_distinguishes_observed_time(self) -> None:
        model = MaskedRegimeDecoder(8, phases(), phase_width=4, regime_indicator=True)
        condition = model.conditioning(torch.tensor([-1, 0, 79]))
        torch.testing.assert_close(condition[:, -1], torch.tensor([0., 1., 1.]))
        self.assertEqual(tuple(condition.shape), (3, 5))

    def test_invalid_phase_indices_rejected(self) -> None:
        for indices in (torch.tensor([-2]), torch.tensor([80]), torch.tensor([0.5]),
                        torch.empty(0, dtype=torch.long), torch.tensor([[0]])):
            with self.assertRaises(CycleDecoderError):
                self.model(self.features, indices)

    def test_encoder_wrapper_has_common_scale_and_both_paths_train_encoder(self) -> None:
        class Encoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.layer = nn.Linear(8, 8)
                self.output = nn.Identity()

            def encode_geometry(self, case):
                return self.layer(case["features"])

        encoder = Encoder().double()
        model = GeometryEncodedRegimeControl(encoder, self.model, output_scale=2.5).double()
        case = {"features": self.features}
        encoded = encoder.encode_geometry(case)
        torch.testing.assert_close(model.forward_cycle(case),
                                   self.model.forward_cycle(encoded) * 2.5)
        torch.testing.assert_close(model.forward_single_field(case),
                                   self.model.forward_steady(encoded) * 2.5)
        for forward in (model.forward_cycle, model.forward_single_field):
            model.zero_grad(set_to_none=True)
            forward(case).square().mean().backward()
            self.assertTrue(bool(encoder.layer.weight.grad.abs().sum() > 0))
        encoder.output = nn.Linear(8, 240)
        with self.assertRaisesRegex(CycleDecoderError, "head_free"):
            GeometryEncodedRegimeControl(encoder, self.model, output_scale=2.5)


if __name__ == "__main__":
    unittest.main()
