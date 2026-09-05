import copy
import unittest

import torch

from aurora.aneug_rhsia_graph_transformer import (
    RHSIAGraphTransformer, SpectralNodeEncoder, TemporalWaveformEncoder,
    surface_scalar_gradients,
)


def synthetic_features():
    torch.manual_seed(9)
    # Two genuinely distinct meshes, no cross-mesh edges.
    nodes = 9
    geometry = torch.randn(nodes, 10)
    geometry[:, 6:] = torch.nn.functional.one_hot(torch.arange(nodes) % 4, 4)
    edges = torch.tensor([[0, 1, 2, 3, 5, 6, 7], [1, 2, 3, 4, 6, 7, 8]])
    return {"node_features": geometry, "ghd_descriptors": torch.randn(nodes, 8, 7),
            "cot_descriptors": torch.randn(nodes, 16, 5),
            "edge_index": torch.cat((edges, edges.flip(0)), 1),
            "batch": torch.tensor([0] * 5 + [1] * 4)}


class SurfaceGradientTests(unittest.TestCase):
    def test_affine_field_and_rotation(self):
        vertices = torch.tensor([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]], dtype=torch.float64)
        faces = torch.tensor([[0, 1, 2], [0, 2, 3]])
        values = torch.stack((vertices[:, 0], vertices[:, 1], 2 * vertices[:, 0] - vertices[:, 1]), -1)
        expected = torch.tensor([[1., 0., 0.], [0., 1., 0.], [2., -1., 0.]], dtype=torch.float64).expand(4, -1, -1)
        actual = surface_scalar_gradients(vertices, faces, values)
        torch.testing.assert_close(actual, expected)
        rotation = torch.tensor([[0., 0., 1.], [1., 0., 0.], [0., 1., 0.]], dtype=torch.float64)
        rotated = surface_scalar_gradients(vertices @ rotation.T, faces, values)
        torch.testing.assert_close(rotated, actual @ rotation.T)
        torch.testing.assert_close(surface_scalar_gradients(vertices * 3, faces, values), actual / 3)

    def test_degenerate_and_isolated_vertices_fail(self):
        vertices = torch.tensor([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [2., 0., 0.]])
        with self.assertRaisesRegex(ValueError, "isolated"):
            surface_scalar_gradients(vertices, torch.tensor([[0, 1, 2]]), vertices[:, :1])
        with self.assertRaisesRegex(ValueError, "degenerate"):
            surface_scalar_gradients(vertices, torch.tensor([[0, 1, 3]]), vertices[:, :1])


class TemporalTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(4)
        self.encoder = TemporalWaveformEncoder(conv_width=4).eval()
        self.waveform = torch.linspace(0, 6.2, 64).sin() + 1.5

    def test_last_phase_and_post_bias_steady_mask(self):
        phases = torch.tensor([-1, 0, 79])
        first = self.encoder(phases, self.waveform, .8)
        second = self.encoder(phases, self.waveform.flip(0) * 2, .8)
        self.assertEqual(int(torch.count_nonzero(first[0])), 0)
        self.assertEqual(int(torch.count_nonzero(second[0])), 0)
        self.assertGreater(float(first[2].abs().sum()), 0)
        self.assertGreater(float((first[2] - second[2]).abs().sum()), 0)
        self.assertEqual(int(torch.count_nonzero(self.encoder(torch.tensor([-1]), self.waveform, .8))), 0)

    def test_invalid_time_is_not_clamped_silently(self):
        for phases in (torch.tensor([-2]), torch.tensor([80]), torch.tensor([1.5])):
            with self.assertRaises(ValueError):
                self.encoder(phases, self.waveform, .8)


class NativeGraphModelTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.features = synthetic_features()
        self.model = RHSIAGraphTransformer(hidden=16, heads=4, layers=2,
                                          pe_width=8, pe_layers=1, pe_feedforward=16,
                                          dropout=0, attention="performer")
        self.waveform = torch.linspace(0, 6.2, 64).sin() + 1.5

    def forward(self, features=None, phases=None, waveform=None):
        return self.model.forward_snapshot(
            self.features if features is None else features,
            torch.tensor([7, 79]) if phases is None else phases,
            self.waveform if waveform is None else waveform, period=.8, output_scale=2.)

    def test_actual_pyg_performer_gine_all_parameters_connected(self):
        output = self.forward()
        self.assertEqual(output.shape, (9, 3))
        target = torch.randn_like(output)
        (output - target).square().mean().backward()
        missing = [name for name, p in self.model.named_parameters() if p.requires_grad and p.grad is None]
        self.assertEqual(missing, [])
        for block in self.model.blocks:
            self.assertGreater(float(block.conv.nn[0].weight.grad.abs().sum()), 0)
        for injection in self.model.time_injections:
            self.assertGreater(float(injection.weight.grad.abs().sum()), 0)

    def test_steady_output_independent_of_waveform_and_other_graph_time(self):
        self.model.eval()
        first = self.forward(phases=torch.tensor([-1, 79]))
        second = self.forward(phases=torch.tensor([-1, 3]), waveform=self.waveform * 1.7)
        torch.testing.assert_close(first[:5], second[:5])
        self.assertGreater(float((first[5:] - second[5:]).abs().sum()), 0)

    def test_node_permutation_within_graphs(self):
        self.model.eval()
        original = self.forward()
        permutation = torch.tensor([4, 2, 1, 0, 3, 8, 6, 5, 7])
        inverse = torch.argsort(permutation)
        features = {key: value[permutation] for key, value in self.features.items() if key != "edge_index"}
        features["edge_index"] = inverse[self.features["edge_index"]]
        torch.testing.assert_close(self.forward(features), original[permutation], atol=2e-6, rtol=2e-5)

    def test_each_node_retains_its_spectral_descriptor(self):
        encoder = self.model.node_encoder.eval()
        original = encoder(self.features)
        changed = {key: value.clone() for key, value in self.features.items()}
        changed["cot_descriptors"][3] *= 8
        updated = encoder(changed)
        self.assertGreater(float((updated[3] - original[3]).abs().sum()), 0)
        torch.testing.assert_close(updated[[0, 1, 2, 4]], original[[0, 1, 2, 4]])

    def test_cross_graph_edges_fail(self):
        self.features["edge_index"][1, 0] = 8
        with self.assertRaisesRegex(ValueError, "crosses"):
            self.forward()

    def test_node_chunking_preserves_values_and_gradients(self):
        original = self.model.node_encoder
        chunked = copy.deepcopy(original)
        chunked.chunk_nodes = 3
        first, second = original(self.features), chunked(self.features)
        torch.testing.assert_close(first, second, atol=2e-6, rtol=2e-5)
        first.square().mean().backward()
        second.square().mean().backward()
        for p, q in zip(original.parameters(), chunked.parameters()):
            torch.testing.assert_close(p.grad, q.grad, atol=2e-6, rtol=2e-5)


if __name__ == "__main__":
    unittest.main()
