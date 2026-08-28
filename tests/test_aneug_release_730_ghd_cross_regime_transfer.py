from __future__ import annotations

import math
import unittest

import torch
from torch import nn

from aurora.aneug_release_730_ghd_cross_regime_transfer import (
    GHDCrossRegimeTransferError,
    Release730GHDSharedDecoderSteadyControl,
    Release730GHDSteadyTransferModel,
    paired_cross_regime_backward,
    shared_decoder_cross_regime_backward,
)


class TinyCycleBackbone(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.encoded_width = 2
        self.encoder = nn.Linear(2, 2, bias=False)
        self.output = nn.Linear(2, 6, bias=False)

    def encode_geometry(self, case: dict[str, torch.Tensor]) -> torch.Tensor:
        return self.encoder(case["features"])

    def decode_cycle(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(features).reshape(features.shape[0], 2, 3).permute(1, 0, 2)

    def forward(self, case: dict[str, torch.Tensor]) -> torch.Tensor:
        return self.decode_cycle(self.encode_geometry(case))


class GHDCrossRegimeTransferTests(unittest.TestCase):
    def test_auxiliary_head_does_not_change_cycle_inference(self) -> None:
        torch.manual_seed(3)
        backbone = TinyCycleBackbone()
        case = {"features": torch.randn(5, 2)}
        expected = backbone(case) * 2.5
        model = Release730GHDSteadyTransferModel(
            backbone, cycle_output_scale=2.5, auxiliary_output_scale=4.0
        )
        self.assertTrue(torch.equal(model.forward_cycle(case), expected))
        self.assertEqual(model.forward_single_field(case).shape, (5, 3))
        shared = model.shared_encoder_parameters()
        cycle = model.cycle_decoder_parameters()
        auxiliary = model.auxiliary_head_parameters()
        self.assertTrue({id(value) for value in shared}.isdisjoint(map(id, cycle)))
        self.assertTrue({id(value) for value in shared}.isdisjoint(map(id, auxiliary)))

    def test_naive_sum_accumulates_unmodified_pair_gradients(self) -> None:
        shared = nn.Parameter(torch.tensor(1.0))
        cycle = nn.Parameter(torch.tensor(1.0))
        auxiliary = nn.Parameter(torch.tensor(1.0))
        diagnostic = paired_cross_regime_backward(
            transient_loss=shared + 2.0 * cycle,
            auxiliary_loss=-2.0 * shared + 3.0 * auxiliary,
            shared_encoder_parameters=(shared,),
            cycle_decoder_parameters=(cycle,),
            auxiliary_head_parameters=(auxiliary,),
            variant="naive_sum",
        )
        self.assertAlmostEqual(float(shared.grad.item()), -1.0)
        self.assertAlmostEqual(float(cycle.grad.item()), 2.0)
        self.assertAlmostEqual(float(auxiliary.grad.item()), 3.0)
        self.assertFalse(diagnostic["projection_applied"])

    def test_field_anchor_removes_only_opposing_shared_component(self) -> None:
        shared = nn.Parameter(torch.tensor(1.0))
        cycle = nn.Parameter(torch.tensor(1.0))
        auxiliary = nn.Parameter(torch.tensor(1.0))
        diagnostic = paired_cross_regime_backward(
            transient_loss=shared + 2.0 * cycle,
            auxiliary_loss=-2.0 * shared + 3.0 * auxiliary,
            shared_encoder_parameters=(shared,),
            cycle_decoder_parameters=(cycle,),
            auxiliary_head_parameters=(auxiliary,),
            variant="field_anchored",
        )
        self.assertAlmostEqual(float(shared.grad.item()), 1.0)
        self.assertAlmostEqual(float(cycle.grad.item()), 2.0)
        self.assertAlmostEqual(float(auxiliary.grad.item()), 3.0)
        self.assertTrue(diagnostic["projection_applied"])
        self.assertGreaterEqual(diagnostic["shared_gradient_dot_after"], -1e-7)

    def test_field_anchor_caps_effective_auxiliary_shared_norm(self) -> None:
        shared = nn.Parameter(torch.tensor(1.0))
        cycle = nn.Parameter(torch.tensor(1.0))
        auxiliary = nn.Parameter(torch.tensor(1.0))
        diagnostic = paired_cross_regime_backward(
            transient_loss=shared + cycle,
            auxiliary_loss=10.0 * shared + auxiliary,
            shared_encoder_parameters=(shared,),
            cycle_decoder_parameters=(cycle,),
            auxiliary_head_parameters=(auxiliary,),
            variant="field_anchored",
            maximum_auxiliary_to_transient_shared_norm=0.5,
            accumulation_steps=2,
        )
        self.assertAlmostEqual(float(shared.grad.item()), 0.75, places=6)
        self.assertAlmostEqual(float(cycle.grad.item()), 0.5, places=6)
        self.assertAlmostEqual(float(auxiliary.grad.item()), 0.5, places=6)
        self.assertAlmostEqual(
            diagnostic["effective_auxiliary_shared_gradient_norm"], 0.5, places=6
        )
        self.assertLess(diagnostic["auxiliary_shared_norm_scale"], 1.0)

    def test_parameter_overlap_fails_closed(self) -> None:
        parameter = nn.Parameter(torch.tensor(1.0))
        auxiliary = nn.Parameter(torch.tensor(1.0))
        with self.assertRaises(GHDCrossRegimeTransferError):
            paired_cross_regime_backward(
                transient_loss=parameter * 0.0,
                auxiliary_loss=parameter + auxiliary,
                shared_encoder_parameters=(parameter,),
                cycle_decoder_parameters=(parameter,),
                auxiliary_head_parameters=(auxiliary,),
                variant="field_anchored",
            )

    def test_zero_transient_shared_gradient_fails_closed(self) -> None:
        shared = nn.Parameter(torch.tensor(1.0))
        cycle = nn.Parameter(torch.tensor(1.0))
        auxiliary = nn.Parameter(torch.tensor(1.0))
        with self.assertRaisesRegex(
            GHDCrossRegimeTransferError, "shared_gradient_norm"
        ):
            paired_cross_regime_backward(
                transient_loss=shared * 0.0 + cycle,
                auxiliary_loss=shared + auxiliary,
                shared_encoder_parameters=(shared,),
                cycle_decoder_parameters=(cycle,),
                auxiliary_head_parameters=(auxiliary,),
                variant="field_anchored",
            )

    def test_auxiliary_coefficient_scales_both_auxiliary_paths(self) -> None:
        shared = nn.Parameter(torch.tensor(1.0))
        cycle = nn.Parameter(torch.tensor(1.0))
        auxiliary = nn.Parameter(torch.tensor(1.0))
        paired_cross_regime_backward(
            transient_loss=shared + cycle,
            auxiliary_loss=2.0 * shared + 4.0 * auxiliary,
            shared_encoder_parameters=(shared,),
            cycle_decoder_parameters=(cycle,),
            auxiliary_head_parameters=(auxiliary,),
            variant="naive_sum",
            auxiliary_coefficient=0.25,
        )
        self.assertAlmostEqual(float(shared.grad.item()), 1.5)
        self.assertAlmostEqual(float(cycle.grad.item()), 1.0)
        self.assertAlmostEqual(float(auxiliary.grad.item()), 1.0)

    def test_shared_decoder_control_has_no_auxiliary_parameters(self) -> None:
        torch.manual_seed(7)
        backbone = TinyCycleBackbone()
        case = {"features": torch.randn(5, 2)}
        expected_cycle = backbone(case) * 2.5
        expected_parameter_ids = {id(value) for value in backbone.parameters()}
        model = Release730GHDSharedDecoderSteadyControl(
            backbone, cycle_output_scale=2.5
        )
        self.assertTrue(torch.equal(model.forward_cycle(case), expected_cycle))
        self.assertTrue(
            torch.equal(model.forward_single_field(case), expected_cycle.mean(dim=0))
        )
        self.assertEqual(
            {id(value) for value in model.transfer_parameters()},
            expected_parameter_ids,
        )

    def test_shared_decoder_control_adds_both_gradients(self) -> None:
        first = nn.Parameter(torch.tensor(1.0))
        second = nn.Parameter(torch.tensor(2.0))
        diagnostic = shared_decoder_cross_regime_backward(
            transient_loss=2.0 * first + second,
            auxiliary_loss=-first + 3.0 * second,
            parameters=(first, second),
            auxiliary_coefficient=0.5,
            accumulation_steps=2,
        )
        self.assertAlmostEqual(float(first.grad.item()), 0.75)
        self.assertAlmostEqual(float(second.grad.item()), 1.25)
        self.assertEqual(diagnostic["variant"], "shared_decoder_naive_sum")
        self.assertTrue(math.isfinite(diagnostic["gradient_cosine"]))


if __name__ == "__main__":
    unittest.main()
