"""Instrumentation fixtures; actual source-size GPU evidence is separate."""
import unittest

import torch
from torch import nn

from aurora.aneug_rhsia_repeatability import audit_repeatability, discrepancy


class InstrumentedFixture(nn.Module):
    phases = 80

    def __init__(self, *, decoder_variation=False, mutate_cache=False, mutate_state=False):
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(1.))
        self.register_buffer("counter", torch.tensor(0))
        self.calls = 0
        self.decoder_variation, self.mutate_cache, self.mutate_state = decoder_variation, mutate_cache, mutate_state

    def _encode_geometry(self, features, graphs):
        return dict(x=features["x"] * self.weight, edges=features["edges"] * self.weight)

    def _decode_snapshot(self, encoded, phases, waveform, period, scale):
        if self.mutate_state:
            self.counter.add_(1)
        if self.mutate_cache:
            encoded["x"].add_(.01)
        self.calls += 1
        shift = self.calls * .001 if self.decoder_variation else 0.
        return encoded["x"] * scale + phases[0] * .01 + shift

    def forward_snapshot(self, features, phase, waveform, *, period, output_scale):
        return self._decode_snapshot(self._encode_geometry(features, 1), phase, waveform, period, output_scale)

    def forward_cycle(self, features, waveform, *, period, output_scale):
        encoded = self._encode_geometry(features, 1)
        return torch.stack([self._decode_snapshot(encoded, torch.tensor([phase]), waveform, period, output_scale)
                            for phase in range(self.phases)])


class RepeatabilityTests(unittest.TestCase):
    def run_audit(self, **kwargs):
        model = InstrumentedFixture(**kwargs).eval()
        features = dict(x=torch.arange(18).reshape(6, 3).float() + 1.,
                        edges=torch.ones(4, 2), batch=torch.zeros(6, dtype=torch.long))
        return audit_repeatability(model, features, torch.ones(16), period=.8, output_scale=2.)

    def test_componentwise_failure_is_preserved_not_loosened(self):
        a = torch.tensor([0., 2., 3.])
        row = discrepancy(a, a + torch.tensor([.0003, 0., 0.]))
        self.assertEqual(row["original_componentwise_failures"], 1)
        self.assertGreater(row["relative_l2"], 0)
        self.assertEqual(row["original_atol"], 1e-5)

    def test_stable_model_does_not_modify_state_or_flags(self):
        before = torch.are_deterministic_algorithms_enabled(), torch.is_deterministic_algorithms_warn_only_enabled()
        result = self.run_audit()
        self.assertEqual(before, (torch.are_deterministic_algorithms_enabled(), torch.is_deterministic_algorithms_warn_only_enabled()))
        self.assertEqual(result["parameter_or_buffer_mutations"], [])
        self.assertEqual(result["input_mutations"], [])
        self.assertFalse(result["default_eval_RNG_changed"])
        self.assertFalse(result["caching_equivalence_claim"])
        for row in result["actual_cycle_native"]:
            self.assertEqual(row["max_abs"], 0)

    def test_native_variation_is_not_attributed_only_to_cache(self):
        result = self.run_audit(decoder_variation=True)
        for phase in result["phase_comparisons"]:
            self.assertGreater(phase["native_native"][0]["max_abs"], 0)
            self.assertGreater(phase["fixed_decoder_repeat"][0]["max_abs"], 0)
        self.assertEqual(result["encoder_repeat"]["x"]["max_abs"], 0)

    def test_cache_and_buffer_mutations_are_detected(self):
        result = self.run_audit(mutate_cache=True, mutate_state=True)
        self.assertIn("counter", result["parameter_or_buffer_mutations"])
        self.assertIn("x", result["phase_comparisons"][0]["encoded_mutation_names"])
        self.assertEqual(result["input_mutations"], [])

    def test_invalid_shapes_and_nonfinite_are_not_hidden(self):
        for value in (torch.ones(2), torch.tensor([float("nan")])):
            with self.assertRaises(ValueError):
                discrepancy(torch.ones(1), value)


if __name__ == "__main__":
    unittest.main()
