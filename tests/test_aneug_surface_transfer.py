from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_cycle_decoders import FourierCycleDecoder, RealPeriodicBasis
from aurora.aneug_architecture_development import train_cycles
from aurora.aneug_processed_v4_d9 import field_loss
from aurora.aneug_release_730_matched_steady_stream import single_field_relative_squared_error
from aurora.aneug_surface_transfer import (
    VARIANTS, SpatialKernelBank, build_surface_transfer_model,
)


def topology():
    return {
        "edge0": torch.tensor([[0, 1, 1, 2, 2, 3, 3, 0], [1, 0, 2, 1, 3, 2, 0, 3]]),
        "edge1": torch.tensor([[0, 1], [1, 0]]), "edge2": torch.tensor([[0], [0]]),
        "idx1": torch.tensor([0, 2]), "idx2": torch.tensor([0]),
        "parent1": torch.tensor([0, 0, 1, 1]), "parent2": torch.tensor([0, 0]),
    }


def geometry():
    return {
        "coordinates": torch.tensor([[0., 0., 0.], [1., 0., 0.],
                                      [1., 1., .2], [0., 1., 0.]]),
        "normals": torch.tensor([[0., 0., 1.]]).repeat(4, 1),
        "vertex_weights": torch.tensor([.1, .2, .3, .4]),
        "ghd": torch.linspace(-1, 1, 432),
    }


def model(variant="selective_transfer", *, auxiliary=True, chunk=8, default=False):
    torch.manual_seed(913)
    options = {} if default else dict(width=16, heads=4, bank_width=4,
                                     operators=3, adapter_width=8)
    return build_surface_transfer_model(topology(), torch.arange(80, dtype=torch.float64) / 80,
                                        variant=variant, output_scale=2.,
                                        auxiliary_steady=auxiliary, mode_chunk=chunk, **options)


class SurfaceTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def test_all_variants_have_full_cycle_and_independent_steady_field(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                current = model(variant)
                cycle, steady = current(geometry()), current.forward_single_field(geometry())
                self.assertEqual(cycle.shape, (80, 4, 3))
                self.assertEqual(steady.shape, (4, 3))
                self.assertTrue(bool(torch.isfinite(cycle).all()))
                self.assertFalse(torch.allclose(cycle.mean(0), steady))
                self.assertFalse(torch.allclose(cycle[0], cycle[79]))
                self.assertFalse(any(name.startswith("encoder.output.")
                                     for name, _ in current.named_parameters()))

    def test_fourier_only_is_exact_existing_decoder_not_a_different_small_head(self):
        current = model("fourier_only")
        reference = FourierCycleDecoder(16, RealPeriodicBasis(torch.arange(80, dtype=torch.float64) / 80, 40))
        reference.coefficients[0].load_state_dict(current.cycle_hidden[0].state_dict())
        reference.coefficients[2].load_state_dict(current.cycle_readout.state_dict())
        encoded = current.encoder.encode_geometry(geometry())
        torch.testing.assert_close(current(geometry()), reference(encoded) * 2,
                                   rtol=0, atol=0)

    def test_target_fields_and_identifiers_are_not_read_or_forwarded(self):
        class Trap(dict):
            def __getitem__(self, key):
                if key not in geometry():
                    raise AssertionError("forbidden target/identifier access")
                return super().__getitem__(key)
        current = model()
        case = Trap(geometry())
        case.update(wss=object(), steady_wss=object(), case_id=object())
        inspected = []
        original = current.encoder.encode_geometry
        def checked(inputs):
            inspected.append(set(inputs))
            self.assertEqual(set(inputs), set(geometry()))
            return original(inputs)
        current.encoder.encode_geometry = checked
        current(case)
        current.forward_single_field(case)
        self.assertEqual(len(inspected), 2)

    def test_one_encoding_and_one_bank_per_cycle_without_persistent_cache(self):
        current = model(chunk=3)
        calls = []
        hooks = [current.encoder.node_input.register_forward_hook(lambda *_: calls.append("encoder")),
                 current.bank.register_forward_hook(lambda *_: calls.append("bank"))]
        current(geometry())
        current(geometry())
        self.assertEqual(calls, ["encoder", "bank", "encoder", "bank"])
        for hook in hooks:
            hook.remove()

    def test_steady_gradient_trains_spatial_bank_not_transient_response_or_router(self):
        current = model()
        prediction = current.forward_single_field(geometry())
        prediction.square().mean().backward()
        for name, parameter in current.named_parameters():
            transient = name.startswith(("cycle_", "transient_adapter.", "router_"))
            with self.subTest(parameter=name):
                if transient:
                    self.assertIsNone(parameter.grad)
                else:
                    self.assertIsNotNone(parameter.grad)
                    self.assertTrue(bool(torch.isfinite(parameter.grad).all()))
        self.assertGreater(float(current.bank.values.weight.grad.abs().sum()), 0)

    def test_cycle_gradient_trains_router_and_every_operator_not_steady_head(self):
        current = model()
        current(geometry()).square().mean().backward()
        for name, parameter in current.named_parameters():
            with self.subTest(parameter=name):
                if name.startswith(("steady_head.", "steady_adapter.")):
                    self.assertIsNone(parameter.grad)
                else:
                    self.assertIsNotNone(parameter.grad)
                    self.assertTrue(bool(torch.isfinite(parameter.grad).all()))
        self.assertGreater(float(current.router_output.weight.grad.abs().sum()), 0)
        per_operator = current.bank.values.weight.grad.reshape(3, 4, 16).abs().sum((1, 2))
        self.assertTrue(bool((per_operator > 0).all()))

    def test_real_mixed_training_has_no_unused_parameters_in_any_variant(self):
        case = geometry()
        target = torch.sin(torch.arange(80)[:, None, None] * .09).expand(80, 4, 3) + .4
        steady_target = torch.full((4, 3), .7)
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                current = model(variant)
                optimizer = torch.optim.AdamW(current.parameters(), lr=.001)
                initial = None
                for _ in range(8):
                    optimizer.zero_grad(set_to_none=True)
                    loss = field_loss(current(case), target, case["vertex_weights"])
                    loss = loss + single_field_relative_squared_error(
                        current.forward_single_field(case), steady_target, case["vertex_weights"])
                    if initial is None:
                        initial = float(loss.detach())
                    loss.backward()
                    self.assertTrue(all(p.grad is not None and bool(torch.isfinite(p.grad).all())
                                        for p in current.parameters()))
                    optimizer.step()
                self.assertLess(float(loss.detach()), initial)

    def test_steady_update_changes_shared_bank_and_cycle_not_router_weights(self):
        current = model()
        before = current(geometry()).detach()
        router = current.router_output.weight.detach().clone()
        bank = current.bank.values.weight.detach().clone()
        optimizer = torch.optim.SGD(current.parameters(), lr=.001)
        current.forward_single_field(geometry()).square().mean().backward()
        optimizer.step()
        self.assertTrue(torch.equal(router, current.router_output.weight))
        self.assertFalse(torch.equal(bank, current.bank.values.weight))
        self.assertFalse(torch.equal(before, current(geometry())))

    def test_actual_common_cycle_trainer_records_cycles_not_snapshots(self):
        current = model(auxiliary=False)
        case = geometry()
        case["wss"] = torch.randn(80, 4, 3) + .5
        optimization = dict(seed=71, epochs=2, accumulation_cases=2,
                            validation_interval=1, checkpoint_interval=1,
                            learning_rate=.001, weight_decay=.0001,
                            step_size_epochs=2, gamma=.75, gradient_clip_norm=1.)
        with tempfile.TemporaryDirectory() as directory:
            result = train_cycles(current, [case] * 3, [case] * 2,
                                  optimization=optimization, reference_tawss_floor=.01,
                                  output_directory=Path(directory) / "synthetic",
                                  provenance={"synthetic_only": True},
                                  device=torch.device("cpu"), log=lambda _: None)
            self.assertEqual(result["training_cycle_exposures"], 6)
            self.assertEqual(result["training_phase_field_exposures"], 480)
            self.assertEqual(result["optimizer_updates"], 4)
            self.assertEqual(result["validation_cycle_forwards"], 4)
            self.assertEqual(result["steady_exposures"], 0)
            self.assertFalse(result["independent_confirmatory_evaluation"])

    def test_pair_initialization_and_uniform_router_recover_always_shared_control(self):
        shared, selective = model("always_shared"), model()
        for name, value in shared.state_dict().items():
            self.assertTrue(torch.equal(value, selective.state_dict()[name]), name)
        with torch.no_grad():
            selective.router_output.weight.zero_()
            selective.router_output.bias.zero_()
        torch.testing.assert_close(shared(geometry()), selective(geometry()), rtol=2e-5, atol=2e-6)
        torch.testing.assert_close(shared.forward_single_field(geometry()),
                                   selective.forward_single_field(geometry()), rtol=0, atol=0)

    def test_routing_is_geometry_and_frequency_dependent_not_coefficient_phase_dependent(self):
        current = model()
        encoded = current.encoder.encode_geometry(geometry())
        gates = current.routing_weights(encoded, current.basis.frequencies)
        self.assertEqual(gates.shape, (4, 80, 3))
        torch.testing.assert_close(gates.sum(-1), torch.ones(4, 80))
        torch.testing.assert_close(gates[:, 1], gates[:, 2], rtol=0, atol=0)
        self.assertFalse(torch.allclose(gates[:, 0], gates[:, 1]))
        self.assertFalse(torch.allclose(gates[0], gates[1]))

    def test_mode_chunking_preserves_full_forward_and_gradients(self):
        reference, chunked = model(chunk=80), model(chunk=7)
        a, b = reference(geometry()), chunked(geometry())
        torch.testing.assert_close(a, b, rtol=2e-5, atol=2e-6)
        a.square().mean().backward()
        b.square().mean().backward()
        for (name, p), (_, q) in zip(reference.named_parameters(), chunked.named_parameters()):
            with self.subTest(parameter=name):
                if p.grad is None:
                    self.assertIsNone(q.grad)
                else:
                    torch.testing.assert_close(p.grad, q.grad, rtol=2e-4, atol=2e-6)

    def test_graph_and_geometry_change_actual_spatial_operator(self):
        current = model()
        case = geometry()
        encoded = current.encoder.encode_geometry(case)
        original = current.bank(encoded, case)
        moved = copy.deepcopy(case)
        moved["coordinates"][1, 0] += .7
        self.assertFalse(torch.allclose(original, current.bank(encoded, moved)))
        current.bank.edge_index = current.bank.edge_index[:, :4]
        self.assertFalse(torch.allclose(original, current.bank(encoded, case)))

    def test_vertex_permutation_with_same_hierarchy_permutes_outputs(self):
        original = model()
        perm = torch.tensor([2, 0, 3, 1])
        inverse = torch.argsort(perm)
        changed = copy.deepcopy(original)
        changed.encoder.edge0 = inverse[changed.encoder.edge0]
        changed.bank.edge_index = inverse[changed.bank.edge_index]
        changed.encoder.idx1 = inverse[changed.encoder.idx1]
        changed.encoder.parent1 = changed.encoder.parent1[perm]
        case = geometry()
        moved = {key: value if key == "ghd" else value[perm] for key, value in case.items()}
        torch.testing.assert_close(changed(moved), original(case)[:, perm], rtol=2e-5, atol=2e-6)
        torch.testing.assert_close(changed.forward_single_field(moved),
                                   original.forward_single_field(case)[perm], rtol=2e-5, atol=2e-6)

    def test_full_spectrum_including_nyquist_and_free_dc_are_decoded(self):
        current = model()
        coefficients = current.forward_coefficients(geometry())
        cycle = current(geometry())
        torch.testing.assert_close(current.basis.encode(cycle), coefficients, rtol=3e-5, atol=3e-6)
        torch.testing.assert_close(cycle.mean(0), coefficients[:, 0], rtol=3e-5, atol=3e-6)
        self.assertEqual(int((current.basis.frequencies == 40).sum()), 1)
        self.assertGreater(float(coefficients[:, -1].abs().sum()), 0)

    def test_transient_only_does_not_construct_unused_auxiliary_parameters(self):
        for variant in VARIANTS:
            current = model(variant, auxiliary=False)
            self.assertFalse(any("steady_" in name for name, _ in current.named_parameters()))
            current(geometry()).square().mean().backward()
            self.assertTrue(all(p.grad is not None for p in current.parameters()))
            with self.assertRaisesRegex(ValueError, "not_constructed"):
                current.forward_single_field(geometry())

    def test_production_recipe_keeps_full_backbone_and_reports_added_capacity(self):
        config = json.loads((Path(__file__).resolve().parents[1] /
                             "configs/aneug_surface_transfer_model_v3.json").read_text())
        sizes = {}
        for variant in config["variants"]:
            current = model(variant, default=True)
            self.assertEqual(current.encoder.encoded_width, 128)
            self.assertEqual(current.cycle_readout.out_features, 240)
            self.assertEqual(current(geometry()).shape, (80, 4, 3))
            sizes[variant] = sum(p.numel() for p in current.parameters())
        self.assertLess(sizes["fourier_only"], sizes["task_adapters"])
        self.assertLess(sizes["task_adapters"], sizes["always_shared"])
        self.assertLess(sizes["always_shared"], sizes["selective_transfer"])
        self.assertFalse(config["comparison"]["same_parameter_count_claimed"])

    def test_wide_ordinary_adapter_is_nearest_capacity_control_in_both_information_modes(self):
        config = json.loads((Path(__file__).resolve().parents[1] /
                             "configs/aneug_surface_transfer_model_v3.json").read_text())
        for auxiliary, name, difference in ((False, "adapter_width_T", 95),
                                             (True, "adapter_width_T_plus_S", -162)):
            target = sum(p.numel() for p in model(auxiliary=auxiliary, default=True).parameters())
            width = config["capacity_control"][name]
            counts = []
            for candidate_width in (width - 1, width, width + 1):
                control = build_surface_transfer_model(
                    topology(), torch.arange(80, dtype=torch.float64) / 80,
                    variant="task_adapters", output_scale=2,
                    auxiliary_steady=auxiliary, adapter_width=candidate_width)
                counts.append(sum(p.numel() for p in control.parameters()))
            self.assertEqual(counts[1] - target, difference)
            self.assertLess(abs(counts[1] - target), abs(counts[0] - target))
            self.assertLess(abs(counts[1] - target), abs(counts[2] - target))

    def test_invalid_contracts_fail_without_data_access(self):
        with self.assertRaisesRegex(ValueError, "variant"):
            model("unknown")
        for chunk in (0, -1, True):
            with self.assertRaisesRegex(ValueError, "mode_chunk"):
                model(chunk=chunk)
        with self.assertRaisesRegex(ValueError, "mesh_edge"):
            SpatialKernelBank(8, 4, 2, torch.tensor([[0., 1.], [1., 0.]]))
        current = model()
        for frequency in (torch.tensor([-1]), torch.tensor([41]), torch.tensor([.5])):
            with self.assertRaisesRegex(ValueError, "frequency_index"):
                current.routing_weights(torch.randn(4, 16), frequency)


if __name__ == "__main__":
    unittest.main()
