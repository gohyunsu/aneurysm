"""Frequency-independent spatial routing; synthetic mechanism tests, not CFD evidence."""
import copy
import json
from pathlib import Path
import unittest

import torch

from aurora.aneug_surface_transfer import build_paired_surface_transfer_model
from test_aneug_surface_transfer import geometry, model, topology


class GeometryRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def test_common_initialization_and_only_active_offset_is_retained(self):
        control, selective = model("geometry_routing"), model("selective_transfer")
        for name, value in control.state_dict().items():
            expected = selective.state_dict()[name]
            if name == "router_frequency.weight":
                expected = expected[:1]
            self.assertTrue(torch.equal(value, expected), name)
        self.assertEqual(control.router_frequency.num_embeddings, 1)
        self.assertTrue(control.router_frequency.weight.requires_grad)

    def test_same_gate_for_every_frequency_but_not_every_location(self):
        control = model("geometry_routing")
        features = control.encoder.encode_geometry(geometry())
        gates = control.routing_weights(features, control.basis.frequencies)
        torch.testing.assert_close(gates, gates[:, :1].expand_as(gates), rtol=0, atol=0)
        self.assertFalse(torch.allclose(gates[0], gates[1]))
        cycle = control(geometry())
        self.assertEqual(cycle.shape, (80, 4, 3))
        self.assertFalse(torch.allclose(cycle[0], cycle[1]))
        coefficients = control.forward_coefficients(geometry())
        self.assertGreater(float(coefficients[:, -1].abs().sum()), 0)

    def test_tied_frequency_candidate_recovers_control_outputs_and_gradients(self):
        control = model("geometry_routing").double().eval()
        selective = model("selective_transfer").double().eval()
        case = {key: value.double() for key, value in geometry().items()}
        with torch.no_grad():
            selective.router_frequency.weight.copy_(control.router_frequency.weight.expand_as(
                selective.router_frequency.weight))
        actual, expected = control(case), selective(case)
        torch.testing.assert_close(actual, expected, rtol=1e-11, atol=1e-12)
        actual.square().mean().backward()
        expected.square().mean().backward()
        candidate_parameters = dict(selective.named_parameters())
        for name, parameter in control.named_parameters():
            other = candidate_parameters[name]
            if parameter.grad is None:
                self.assertIsNone(other.grad)
                continue
            expected_gradient = other.grad
            if name == "router_frequency.weight":
                expected_gradient = expected_gradient.sum(0, keepdim=True)
            torch.testing.assert_close(parameter.grad, expected_gradient, rtol=1e-10, atol=1e-12)

    def test_uniform_geometry_gate_recovers_uniform_control(self):
        control = model("geometry_routing").double().eval()
        uniform = model("always_shared").double().eval()
        with torch.no_grad():
            control.router_output.weight.zero_()
            control.router_output.bias.zero_()
        case = {key: value.double() for key, value in geometry().items()}
        torch.testing.assert_close(control(case), uniform(case), rtol=1e-11, atol=1e-12)
        torch.testing.assert_close(control.forward_single_field(case),
                                   uniform.forward_single_field(case), rtol=0, atol=0)

    def test_one_hidden_path_per_cycle_and_chunk_independence(self):
        control, changed = model("geometry_routing", chunk=1), model("geometry_routing", chunk=80)
        calls = []
        hook = control.cycle_hidden.register_forward_pre_hook(
            lambda _, inputs: calls.append(tuple(inputs[0].shape)))
        output = control(geometry())
        hook.remove()
        self.assertEqual(calls, [(4, 16)])
        other = changed(geometry())
        torch.testing.assert_close(output, other, rtol=0, atol=0)
        output.square().mean().backward()
        other.square().mean().backward()
        for (_, first), (_, second) in zip(control.named_parameters(), changed.named_parameters()):
            if first.grad is None:
                self.assertIsNone(second.grad)
            else:
                torch.testing.assert_close(first.grad, second.grad, rtol=0, atol=0)

    def test_steady_does_not_train_router_but_cycle_trains_all_retained_rows(self):
        control = model("geometry_routing")
        control.forward_single_field(geometry()).square().mean().backward()
        for name, parameter in control.named_parameters():
            if name.startswith(("router_", "cycle_", "transient_adapter.")):
                self.assertIsNone(parameter.grad, name)
        control.zero_grad(set_to_none=True)
        control(geometry()).square().mean().backward()
        for name, parameter in control.named_parameters():
            if name.startswith(("steady_head.", "steady_adapter.")):
                self.assertIsNone(parameter.grad, name)
            else:
                self.assertIsNotNone(parameter.grad, name)
                self.assertTrue(bool(torch.isfinite(parameter.grad).all()), name)
        self.assertGreater(float(control.router_frequency.weight.grad.norm()), 0)

    def test_paired_information_conditions_and_declared_production_capacity(self):
        recipe = json.loads((Path(__file__).resolve().parents[1] /
                             "configs/aneug_surface_routing_ablation_v3.json").read_text())
        for auxiliary in (False, True):
            control = model("geometry_routing", default=True, auxiliary=auxiliary)
            selective = model("selective_transfer", default=True, auxiliary=auxiliary)
            difference = sum(p.numel() for p in control.parameters()) - sum(p.numel() for p in selective.parameters())
            self.assertEqual(difference, recipe["control_minus_comparator_parameters"])
            self.assertFalse(recipe["exact_parameter_count_matched"])
        paired = []
        for auxiliary in (False, True):
            torch.manual_seed(731)
            paired.append(build_paired_surface_transfer_model(
                topology(), torch.arange(80, dtype=torch.float64) / 80,
                variant="geometry_routing", output_scale=2., auxiliary_steady=auxiliary,
                width=16, heads=4, bank_width=4, operators=3, adapter_width=8))
        for name, value in paired[0].state_dict().items():
            self.assertTrue(torch.equal(value, paired[1].state_dict()[name]), name)
        self.assertFalse(any(name.startswith("steady_") for name, _ in paired[0].named_parameters()))

    def test_vertex_permutation_preserves_geometry_routing(self):
        original = model("geometry_routing")
        changed = copy.deepcopy(original)
        perm = torch.tensor([2, 0, 3, 1])
        inverse = torch.argsort(perm)
        changed.encoder.edge0 = inverse[changed.encoder.edge0]
        changed.bank.edge_index = inverse[changed.bank.edge_index]
        changed.encoder.idx1 = inverse[changed.encoder.idx1]
        changed.encoder.parent1 = changed.encoder.parent1[perm]
        case = geometry()
        moved = {key: value if key == "ghd" else value[perm] for key, value in case.items()}
        torch.testing.assert_close(changed(moved), original(case)[:, perm], rtol=2e-5, atol=2e-6)


if __name__ == "__main__":
    unittest.main()
