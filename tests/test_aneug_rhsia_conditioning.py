"""Explicit conditioning controls; synthetic tests are not accuracy evidence."""
import copy
import json
from pathlib import Path
import unittest

import torch
from torch.nn import functional as F

from aurora.aneug_rhsia_graph_transformer import (
    RHSIAGraphTransformer, TemporalWaveformEncoder,
)
from test_aneug_rhsia_graph_transformer import synthetic_features


class ConditioningTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(45)
        self.waveform = torch.linspace(0, 6.2, 64).sin() + 1.5

    def encoder(self, mode="separate_layer_norm"):
        return TemporalWaveformEncoder(conv_width=4,
                                       conditioning_normalization=mode).eval()

    def test_prospective_recipe_preserves_full_core_and_separates_precision(self):
        config = json.loads((Path(__file__).resolve().parents[1] / "configs" /
                             "aneug_rhsia_conditioning_control_v3.json").read_text())
        for mode in config["conditioning_normalization_options"]:
            model = RHSIAGraphTransformer(**config["architecture"], conditioning_normalization=mode)
            self.assertEqual(sum(p.numel() for p in model.parameters()), config["native_core_parameters"])
            self.assertEqual(model.temporal_encoder.conditioning_normalization, mode)
        self.assertEqual(config["training_precision_options"], ["float32", "cuda_bfloat16"])
        self.assertEqual(config["evaluation_precision"], "float32")
        self.assertTrue(config["requires_fresh_explicit_private_recipe"])
        self.assertFalse(config["legacy_checkpoint_keys_identify_normalization"])
        self.assertFalse(config["zero_excluding_interval_required_for_development_selection"])
        self.assertFalse(config["scientific_result_exists"])

    def test_default_preserves_explicit_none_state_rng_output_and_gradients(self):
        torch.manual_seed(45)
        default = TemporalWaveformEncoder(conv_width=4)
        default_rng = torch.get_rng_state().clone()
        torch.manual_seed(45)
        explicit = TemporalWaveformEncoder(conv_width=4,
                                          conditioning_normalization="none")
        self.assertTrue(torch.equal(default_rng, torch.get_rng_state()))
        for key, value in default.state_dict().items():
            self.assertTrue(torch.equal(value, explicit.state_dict()[key]), key)
        phases = torch.tensor([-1, 0, 79])
        first = default(phases, self.waveform, .8)
        second = explicit(phases, self.waveform, .8)
        self.assertTrue(torch.equal(first, second))
        first.square().mean().backward()
        second.square().mean().backward()
        for p, q in zip(default.parameters(), explicit.parameters()):
            self.assertTrue(torch.equal(p.grad, q.grad))

    def test_normalizes_branches_separately_without_cross_sample_statistics(self):
        raw = self.encoder("none")
        with torch.no_grad():
            raw.up1[-1].weight.mul_(100000.)
            raw.up1[-1].bias.copy_(torch.arange(8) * 100000.)
        normalized = self.encoder()
        normalized.load_state_dict(raw.state_dict(), strict=True)
        phases = torch.tensor([-1, 0, 7, 79])
        reference = raw(phases, self.waveform, .8)
        actual = normalized(phases, self.waveform, .8)
        expected = torch.cat([F.layer_norm(x, (8,), eps=1e-5)
                              for x in reference.split(8, -1)], -1)
        torch.testing.assert_close(actual, expected, atol=0, rtol=0)
        for branch in actual[1:].split(8, -1):
            self.assertLessEqual(float(branch.square().mean(-1).max()), 1.00001)
            torch.testing.assert_close(branch.mean(-1), torch.zeros(3), atol=1e-6, rtol=0)
        last_alone = normalized(torch.tensor([79]), self.waveform, .8)
        torch.testing.assert_close(actual[-1:], last_alone)
        self.assertGreater(float((actual[1] - actual[-1]).abs().sum()), 0.)

    def test_mask_is_last_and_all_steady_does_not_update_waveform_buffers(self):
        model = self.encoder().train()
        with torch.no_grad():
            model.time_mlp[-1].bias.fill_(19.)
            model.up1[-1].bias.copy_(torch.arange(8) + 23.)
        original = copy.deepcopy(model.state_dict())
        steady = model(torch.tensor([-1, -1]), self.waveform, .8)
        self.assertEqual(int(torch.count_nonzero(steady)), 0)
        for key, value in model.state_dict().items():
            self.assertTrue(torch.equal(value, original[key]), key)
        mixed = model(torch.tensor([-1, 79]), self.waveform, .8)
        self.assertEqual(int(torch.count_nonzero(mixed[0])), 0)
        self.assertGreater(float(mixed[1].abs().sum()), 0.)

    def test_low_precision_normalization_accumulates_in_fp32(self):
        for dtype in (torch.float32, torch.bfloat16):
            values = (torch.randn(4, 8) * 10000).to(dtype).requires_grad_()
            with torch.autocast("cpu", dtype=torch.bfloat16):
                output = TemporalWaveformEncoder._normalize_branch(values)
            expected = F.layer_norm(values.float(), (8,), eps=1e-5).to(dtype)
            self.assertEqual(output.dtype, dtype)
            self.assertTrue(torch.equal(output, expected))
            (output.float() * torch.arange(8)).sum().backward()
            self.assertTrue(bool(torch.isfinite(values.grad).all()))
            self.assertGreater(float(values.grad.abs().sum()), 0.)
        double = torch.randn(2, 8, dtype=torch.float64, requires_grad=True)
        self.assertTrue(torch.autograd.gradcheck(
            TemporalWaveformEncoder._normalize_branch, (double,)))

    def test_native_size_state_keys_rng_and_finite_backward_are_retained(self):
        torch.manual_seed(22)
        original = RHSIAGraphTransformer()
        original_rng = torch.get_rng_state().clone()
        torch.manual_seed(22)
        normalized = RHSIAGraphTransformer(conditioning_normalization="separate_layer_norm")
        self.assertTrue(torch.equal(original_rng, torch.get_rng_state()))
        for model in (original, normalized):
            self.assertEqual(sum(p.numel() for p in model.parameters()), 3071337)
        self.assertEqual(list(original.state_dict()), list(normalized.state_dict()))
        for key, value in original.state_dict().items():
            self.assertTrue(torch.equal(value, normalized.state_dict()[key]), key)
        output = normalized.forward_snapshot(
            synthetic_features(), torch.tensor([0, 79]), self.waveform,
            period=.8, output_scale=2.)
        (output - torch.randn_like(output)).square().mean().backward()
        self.assertEqual(tuple(output.shape), (9, 3))
        for name, parameter in normalized.named_parameters():
            self.assertIsNotNone(parameter.grad, name)
            self.assertTrue(bool(torch.isfinite(parameter.grad).all()), name)
        self.assertGreater(float(normalized.node_encoder.geometry_projection.weight.grad.abs().sum()), 0.)

    def test_all_eighty_native_phase_passes_remain(self):
        from unittest.mock import patch
        model = RHSIAGraphTransformer(
            hidden=16, layers=2, pe_width=8, pe_layers=1, pe_feedforward=16,
            dropout=0, conditioning_normalization="separate_layer_norm").eval()
        features = synthetic_features()
        features = {k: v[:5] for k, v in features.items() if k != "edge_index"} | {
            "edge_index": torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]])}
        with torch.no_grad(), patch.object(model, "_decode_snapshot", wraps=model._decode_snapshot) as decode:
            actual = model.forward_cycle(features, self.waveform, period=.8, output_scale=2.)
            self.assertEqual(decode.call_count, 80)
            phases = [int(call.args[1].item()) for call in decode.call_args_list]
        self.assertEqual(phases, list(range(80)))
        self.assertEqual(tuple(actual.shape), (80, 5, 3))
        self.assertTrue(bool(torch.isfinite(actual).all()))

    def test_unsupported_modes_and_degenerate_normalized_branch_fail(self):
        for mode in ("layer_norm", True, None):
            with self.assertRaisesRegex(ValueError, "conditioning normalization"):
                self.encoder(mode)
        with self.assertRaisesRegex(ValueError, "at least two channels"):
            TemporalWaveformEncoder(waveform_width=1,
                                    conditioning_normalization="separate_layer_norm")


if __name__ == "__main__":
    unittest.main()
