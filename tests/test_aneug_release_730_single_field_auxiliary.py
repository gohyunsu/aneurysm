import math
import unittest

import torch
from torch import nn

from aurora.aneug_release_730_single_field_auxiliary import (
    SharedEncoderSingleFieldAdapter,
    SharedEncoderSingleFieldHead,
    SingleFieldAuxiliaryError,
    scaled_single_field_target,
    steady_auxiliary_case,
    train_cycle_mean_wss_rms,
    transient_mean_auxiliary_case,
)


class DummyBackbone(nn.Module):
    encoded_width = 8

    def __init__(self):
        super().__init__()
        self.encoder = nn.Linear(7, self.encoded_width)
        self.cycle = nn.Linear(self.encoded_width, 12)
        self.encoder_calls = 0

    def encode_geometry(self, case):
        self.encoder_calls += 1
        return self.encoder(case["node_features"])

    def decode_cycle(self, features):
        return self.cycle(features).reshape(features.shape[0], 4, 3).permute(1, 0, 2)

    def forward(self, case):
        return self.decode_cycle(self.encode_geometry(case))


def transient_case(nodes=5):
    generator = torch.Generator().manual_seed(31)
    return {
        "coordinates": torch.randn(nodes, 3, generator=generator),
        "normals": torch.randn(nodes, 3, generator=generator),
        "vertex_weights": torch.full((nodes,), 1.0 / nodes),
        "ghd": torch.randn(432, generator=generator),
        "wss": torch.randn(80, nodes, 3, generator=generator),
    }


class SingleFieldAuxiliaryTests(unittest.TestCase):
    def test_common_head_rejects_wrong_width(self):
        head = SharedEncoderSingleFieldHead(8)
        with self.assertRaisesRegex(SingleFieldAuxiliaryError, "encoded_features"):
            head(torch.randn(5, 7))

    def test_transient_mean_target_is_exact_and_train_case_only(self):
        case = transient_case()
        auxiliary = transient_mean_auxiliary_case(case)
        torch.testing.assert_close(auxiliary["single_field_wss"], case["wss"].mean(0))
        for key in ("coordinates", "normals", "vertex_weights", "ghd"):
            self.assertIs(auxiliary[key], case[key])

    def test_train_cycle_mean_scale_matches_area_weighted_target_population(self):
        first = transient_case(nodes=2)
        first["vertex_weights"] = torch.tensor([0.25, 0.75])
        first["wss"] = torch.zeros(80, 2, 3)
        first["wss"][:, 0] = torch.tensor([3.0, 4.0, 0.0])
        second = transient_case(nodes=2)
        second["vertex_weights"] = torch.tensor([0.5, 0.5])
        second["wss"] = torch.zeros(80, 2, 3)
        second["wss"][:, 1] = torch.tensor([0.0, 0.0, 2.0])
        self.assertAlmostEqual(
            train_cycle_mean_wss_rms([first, second]),
            math.sqrt((6.25 + 2.0) / 2.0),
        )

    def test_steady_adapter_reuses_lazy_field_without_copy(self):
        case = transient_case()
        steady = {
            key: case[key] for key in ("coordinates", "normals", "vertex_weights", "ghd")
        }
        steady["steady_wss"] = case["wss"][0]
        auxiliary = steady_auxiliary_case(steady)
        self.assertIs(auxiliary["single_field_wss"], steady["steady_wss"])

    def test_target_scaling_is_explicit_positive_and_shared(self):
        auxiliary = transient_mean_auxiliary_case(transient_case())
        scaled = scaled_single_field_target(auxiliary, 2.5)
        torch.testing.assert_close(scaled, auxiliary["single_field_wss"] / 2.5)
        for value in (0.0, -1.0, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(SingleFieldAuxiliaryError, "target_scale"):
                    scaled_single_field_target(auxiliary, value)

    def test_cycle_path_is_exact_and_each_mode_uses_one_encoder_pass(self):
        torch.manual_seed(37)
        backbone = DummyBackbone()
        adapter = SharedEncoderSingleFieldAdapter(backbone)
        case = {"node_features": torch.randn(5, 7)}
        expected = backbone(case)
        calls = backbone.encoder_calls
        actual = adapter(case, mode="cycle")
        self.assertEqual(backbone.encoder_calls, calls + 1)
        torch.testing.assert_close(actual, expected, rtol=0.0, atol=0.0)
        auxiliary = adapter(case, mode="single_field")
        self.assertEqual(backbone.encoder_calls, calls + 2)
        self.assertEqual(tuple(auxiliary.shape), (5, 3))

    def test_auxiliary_backward_updates_shared_encoder_and_single_head(self):
        backbone = DummyBackbone()
        adapter = SharedEncoderSingleFieldAdapter(backbone)
        output = adapter({"node_features": torch.randn(5, 7)}, mode="single_field")
        output.square().mean().backward()
        self.assertTrue(torch.isfinite(backbone.encoder.weight.grad).all())
        gradients = [parameter.grad for parameter in adapter.single_field_head.parameters()]
        self.assertTrue(
            all(
                value is not None and torch.isfinite(value).all()
                for value in gradients
            )
        )


if __name__ == "__main__":
    unittest.main()
