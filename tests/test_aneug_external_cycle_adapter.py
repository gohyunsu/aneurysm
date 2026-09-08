import unittest

import torch
from torch import nn

from aurora.aneug_external_cycle_adapter import (
    ExternalLinearNOCycleAdapter,
    geometry_node_features,
)


class ToyInterfaceCore(nn.Module):
    """Tests the adapter interface only; not a stand-in benchmark LinearNO."""

    def __init__(self, width=439, output=240):
        super().__init__()
        self.readout = nn.Linear(width, output)
        self.calls = 0

    def forward(self, data):
        self.calls += 1
        cfd, geometry = data
        assert geometry is None
        return self.readout(cfd.x)


class GeometryOnly(dict):
    def __getitem__(self, key):
        if key in {"wss", "steady_wss", "target"}:
            raise AssertionError("target access during geometry-only inference")
        return super().__getitem__(key)


class ExternalCycleAdapterTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(36)
        self.case = GeometryOnly(
            coordinates=torch.randn(11, 3),
            normals=torch.randn(11, 3),
            vertex_weights=torch.arange(1, 12, dtype=torch.float32),
            ghd=torch.randn(432),
        )

    def test_geometry_input_and_area_scale_invariance(self):
        features = geometry_node_features(self.case)
        self.assertEqual(features.shape, (11, 439))
        torch.testing.assert_close(features[:, :3], self.case["coordinates"])
        torch.testing.assert_close(features[:, 7:], self.case["ghd"].expand(11, -1))
        scaled = dict(self.case, vertex_weights=19 * self.case["vertex_weights"])
        torch.testing.assert_close(features, geometry_node_features(scaled))

    def test_one_forward_and_physical_output_layout(self):
        core = ToyInterfaceCore()
        adapter = ExternalLinearNOCycleAdapter(core, output_scale=13.0)
        result = adapter(self.case)
        self.assertEqual(core.calls, 1)
        expected = core.readout(geometry_node_features(self.case))
        expected = expected.reshape(11, 80, 3).permute(1, 0, 2) * 13
        torch.testing.assert_close(result, expected)

    def test_gradients_reach_the_supplied_core(self):
        core = ToyInterfaceCore()
        adapter = ExternalLinearNOCycleAdapter(core, output_scale=1.0)
        adapter(self.case).square().mean().backward()
        for parameter in core.parameters():
            self.assertIsNotNone(parameter.grad)
            self.assertGreater(float(parameter.grad.norm()), 0)

    def test_node_permutation_and_no_input_mutation(self):
        model = ExternalLinearNOCycleAdapter(ToyInterfaceCore(), output_scale=1)
        original = {key: value.clone() for key, value in self.case.items()}
        permutation = torch.randperm(11)
        permuted = {
            key: value if key == "ghd" else value[permutation]
            for key, value in self.case.items()
        }
        torch.testing.assert_close(model(permuted), model(self.case)[:, permutation])
        for key in original:
            torch.testing.assert_close(self.case[key], original[key])

    def test_no_ghd_variant_declares_input_information(self):
        case = dict(self.case)
        del case["ghd"]
        model = ExternalLinearNOCycleAdapter(
            ToyInterfaceCore(width=7), output_scale=1, include_ghd=False
        )
        self.assertEqual(model.input_width, 7)
        self.assertEqual(model(case).shape, (80, 11, 3))

    def test_invalid_weights_scale_and_core_shape(self):
        for scale in (0, -1, float("nan")):
            with self.assertRaises(ValueError):
                ExternalLinearNOCycleAdapter(ToyInterfaceCore(), output_scale=scale)
        for weights in (torch.zeros(11), torch.full((11,), float("nan"))):
            with self.assertRaises(ValueError):
                geometry_node_features(dict(self.case, vertex_weights=weights))
        model = ExternalLinearNOCycleAdapter(ToyInterfaceCore(output=3), output_scale=1)
        with self.assertRaises(ValueError):
            model(self.case)


if __name__ == "__main__":
    unittest.main()
