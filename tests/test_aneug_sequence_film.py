import copy
import tempfile
from pathlib import Path
import unittest

import torch
from torch import nn

from aurora.aneug_architecture_development import train_cycles
from aurora.aneug_sequence_film import (
    HierarchicalChebEncoder, SequenceFiLMWSS, SteadyWSSPredictor,
    geometry_only, interpolate_features, interpolation_stencil,
)
from aurora.aneug_steady_prior_training import train_steady_prior


def ring_edges(nodes):
    a = torch.arange(nodes)
    b = (a + 1) % nodes
    return torch.stack((torch.cat((a, b)), torch.cat((b, a))))


def topology():
    return dict(edge0=ring_edges(12), edge1=ring_edges(6), edge2=ring_edges(3),
                idx1=torch.arange(0, 12, 2), idx2=torch.tensor([0, 2, 4]))


def small_encoder(*, include_ghd=False):
    """Actual Cheb model at unit-test widths, never a scientific activation."""
    return HierarchicalChebEncoder(topology(), include_ghd=include_ghd,
        encoder_widths=(8, 12, 16), decoder_widths=(16, 16), global_width=16,
        intermediate_widths=(8, 8, 12, 20, 16), global_hidden=(16, 20))


class GeometryOnly(dict):
    def __getitem__(self, key):
        if key in {"wss", "steady_wss", "reference", "target"}:
            raise AssertionError("inference read a CFD label")
        return super().__getitem__(key)


class SequenceFiLMTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(2)
        torch.manual_seed(13)
        self.case = GeometryOnly(coordinates=torch.randn(12, 3), normals=torch.randn(12, 3),
            vertex_weights=torch.ones(12) / 12, ghd=torch.randn(432),
            wss=torch.full((80, 12, 3), float("nan")), steady_wss=torch.full((12, 3), float("nan")))
        t = torch.arange(40) / 40
        self.wave = 2 + (2 * torch.pi * t).sin() + .2 * (6 * torch.pi * t).cos()

    def model(self, prior=None):
        return SequenceFiLMWSS(small_encoder(), self.wave, output_scale=2.5, period=.8,
            heads=4, cross_layers=2, dropout=.1, steady_prior=prior,
            prior_conditioning_scale=3.0 if prior is not None else None)

    def test_interpolation_is_three_neighbor_weighted_and_chunk_exact(self):
        coarse, fine = self.case["coordinates"][:6], self.case["coordinates"]
        index, weight = interpolation_stencil(coarse, fine, chunk_size=2)
        other = interpolation_stencil(coarse, fine, chunk_size=12)
        torch.testing.assert_close(index, other[0], rtol=0, atol=0)
        torch.testing.assert_close(weight, other[1], rtol=0, atol=0)
        reference = torch.cdist(fine, coarse, compute_mode="donot_use_mm_for_euclid_dist").square()
        distances, expected_indices = reference.topk(3, largest=False)
        inverse = 1 / distances.clamp_min(1e-16)
        torch.testing.assert_close(index, expected_indices)
        torch.testing.assert_close(weight, inverse / inverse.sum(1, keepdim=True))
        values = torch.randn(6, 4, requires_grad=True)
        output = interpolate_features(values, (index, weight))
        torch.testing.assert_close(output[:6], values, rtol=1e-5, atol=1e-6)
        output.sum().backward()
        self.assertTrue(torch.all(values.grad > 0))

    def test_full_cycle_is_one_geometry_pass_and_no_label_read(self):
        model = self.model().eval()
        calls = []
        hook = model.encoder.register_forward_hook(lambda *args: calls.append(1))
        with torch.no_grad():
            output = model(self.case)
        hook.remove()
        self.assertEqual(output.shape, (80, 12, 3))
        self.assertEqual(len(calls), 1)
        self.assertTrue(torch.isfinite(output).all())
        self.assertFalse(torch.equal(output[0], output[79]))
        self.assertNotIn("wss", geometry_only(self.case))
        self.assertNotIn("steady_wss", geometry_only(self.case))

    def test_size_preserving_profile_is_visible_to_actual_sequence_encoder(self):
        from aurora.aneug_geometry_scale import RADIUS, apply_geometry_scale, fit_geometry_scale
        small = dict(self.case, **{RADIUS: torch.tensor(1., dtype=torch.float64)})
        large = dict(self.case, **{RADIUS: torch.tensor(2., dtype=torch.float64)})
        contract = fit_geometry_scale([small, large], expected_train_cases=2)
        model = self.model().eval()
        with torch.no_grad():
            # Identical legacy coordinates collapse these two inputs.
            torch.testing.assert_close(model(small), model(large), rtol=0, atol=0)
            first = model(apply_geometry_scale(small, contract))
            second = model(apply_geometry_scale(large, contract))
        self.assertEqual(first.shape, (80, 12, 3))
        self.assertFalse(torch.allclose(first, second, rtol=1e-5, atol=1e-6))

    def test_all_active_geometry_waveform_and_cross_attention_parameters_connected(self):
        model = self.model()
        model(self.case).square().mean().backward()
        for name, parameter in model.named_parameters():
            self.assertIsNotNone(parameter.grad, name)
            self.assertTrue(torch.isfinite(parameter.grad).all(), name)
        for name in ("encoder.down0.layers.0.lins.0.weight", "wave_projection.weight",
                     "cross.0.attention.in_proj_weight", "temporal.down1.0.weight"):
            self.assertGreater(float(dict(model.named_parameters())[name].grad.norm()), 0)

    def test_waveform_and_mesh_convolutions_actually_change_prediction(self):
        model = self.model().eval()
        with torch.no_grad():
            reference = model(self.case)
            model.waveform.copy_(model.waveform.roll(7))
            wave_changed = model(self.case)
            model.waveform.copy_(self.wave)
            model.encoder.down0.layers[0].lins[0].weight.add_(.1)
            mesh_changed = model(self.case)
        self.assertFalse(torch.allclose(reference, wave_changed))
        self.assertFalse(torch.allclose(reference, mesh_changed))

    def test_node_permutation_with_corresponding_hierarchy(self):
        model = self.model().eval()
        permuted = copy.deepcopy(model)
        order = torch.randperm(12)
        inverse = torch.empty_like(order)
        inverse[order] = torch.arange(12)
        permuted.encoder.edge0.copy_(inverse[model.encoder.edge0])
        permuted.encoder.idx1.copy_(inverse[model.encoder.idx1])
        case = GeometryOnly({key: value if key == "ghd" else value[order]
            for key, value in geometry_only(self.case).items()})
        with torch.no_grad():
            torch.testing.assert_close(permuted(case), model(self.case)[:, order], rtol=2e-5, atol=2e-6)

    def test_film_uses_prediction_and_prior_stays_frozen_in_eval(self):
        class BufferPrior(nn.Module):
            def __init__(self):
                super().__init__()
                self.bn, self.readout = nn.BatchNorm1d(3), nn.Linear(3, 3)
                self.calls = 0

            def forward(self, case):
                assert not {"wss", "steady_wss"} & set(case)
                self.calls += 1
                return self.readout(self.bn(case["coordinates"]))

        prior = BufferPrior()
        before = copy.deepcopy(prior.state_dict())
        model = self.model(prior).train()
        self.assertFalse(prior.training)
        model(self.case).square().mean().backward()
        self.assertEqual(prior.calls, 1)
        self.assertTrue(all(p.grad is None and not p.requires_grad for p in prior.parameters()))
        self.assertIsNotNone(model.film[0].weight.grad)
        for key, value in before.items():
            torch.testing.assert_close(value, prior.state_dict()[key], rtol=0, atol=0)
        model.eval()
        with torch.no_grad():
            reference = model(self.case)
            prior.readout.bias.add_(1)
            self.assertFalse(torch.allclose(reference, model(self.case)))

    def test_default_encoder_is_source_scale_actual_chebyshev(self):
        from torch_geometric.nn import ChebConv
        encoder = HierarchicalChebEncoder(topology())
        self.assertEqual(encoder.output_width, 128)
        self.assertEqual(encoder.recipe["global_width"], 2048)
        self.assertEqual(len([m for m in encoder.modules() if isinstance(m, ChebConv)]), 15)
        self.assertGreater(sum(p.numel() for p in encoder.parameters()), 12_000_000)
        with torch.no_grad():
            self.assertEqual(encoder(self.case).shape, (12, 128))

    def test_paired_seed_common_weights_are_identical_with_or_without_film(self):
        prior = SteadyWSSPredictor(small_encoder(), output_scale=3)
        torch.manual_seed(113)
        plain = self.model()
        torch.manual_seed(113)
        film = self.model(prior)
        for name, value in plain.state_dict().items():
            torch.testing.assert_close(value, film.state_dict()[name], rtol=0, atol=0)

    def test_ghd_input_variant_has_explicit_width_and_connected_projection(self):
        encoder = small_encoder(include_ghd=True)
        self.assertEqual(encoder.input_width, 439)
        self.assertEqual(encoder(self.case).shape, (12, 16))
        with self.assertRaises(KeyError):
            encoder({k: v for k, v in geometry_only(self.case).items() if k != "ghd"})

    def test_invalid_geometry_waveform_and_shared_prior_encoder(self):
        with self.assertRaises(ValueError):
            interpolation_stencil(torch.randn(2, 3), torch.randn(4, 3))
        with self.assertRaises(ValueError):
            HierarchicalChebEncoder(dict(topology(), idx2=torch.tensor([0, 2, 8])))
        model = self.model()
        with self.assertRaises(ValueError):
            model(dict(geometry_only(self.case), coordinates=torch.randn(5, 3)))
        with self.assertRaises(ValueError):
            SequenceFiLMWSS(small_encoder(), torch.full((40,), float("nan")), output_scale=1, period=.8)
        encoder = small_encoder()
        with self.assertRaisesRegex(ValueError, "separate"):
            SequenceFiLMWSS(encoder, self.wave, output_scale=1, period=.8,
                steady_prior=SteadyWSSPredictor(encoder, output_scale=1), prior_conditioning_scale=1)

    def test_real_cheb_steady_training_then_frozen_film_cycle_training(self):
        case = dict(geometry_only(self.case), steady_wss=torch.randn(12, 3))

        class Stream:
            def __init__(self):
                self.reads = []

            def decode(self, index):
                assert index in {2, 7, 9}
                self.reads.append(index)
                return case

        stream = Stream()
        prior = SteadyWSSPredictor(small_encoder(), output_scale=3)
        opt = dict(seed=13, epochs=2, cases_per_epoch=3, accumulation_cases=2,
                   checkpoint_interval=2, learning_rate=3e-4, weight_decay=1e-4,
                   step_size_epochs=50, gamma=.75, gradient_clip_norm=1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = train_steady_prior(prior, stream, [2, 7, 9], optimization=opt,
                output_directory=root / "steady", provenance={"synthetic": True},
                device=torch.device("cpu"), log=lambda _: None)
            self.assertEqual(result["steady_exposures"], 6)
            self.assertEqual(result["optimizer_updates"], 4)
            prior.zero_grad(set_to_none=True)
            before = copy.deepcopy(prior.state_dict())
            model = self.model(prior)
            cycle_opt = {k: v for k, v in opt.items() if k != "cases_per_epoch"}
            cycle_opt["validation_interval"] = 1
            data = [dict(geometry_only(self.case), wss=torch.randn(80, 12, 3)) for _ in range(3)]
            transient = train_cycles(model, data, data[:1], optimization=cycle_opt,
                reference_tawss_floor=1e-4, output_directory=root / "transient",
                provenance={"synthetic": True, "prior_sha256": result["prior_checkpoint_sha256"]},
                device=torch.device("cpu"), log=lambda _: None)
            self.assertEqual(transient["training_phase_field_exposures"], 480)
            self.assertEqual(transient["steady_exposures"], 0)  # prior stage is separately counted
            self.assertEqual(len(stream.reads), 6)  # no actual steady label at transient training/inference
            for key, value in before.items():
                torch.testing.assert_close(value, prior.state_dict()[key], rtol=0, atol=0)


if __name__ == "__main__":
    unittest.main()
