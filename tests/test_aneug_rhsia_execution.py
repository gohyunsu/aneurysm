import copy
import unittest

import torch
from torch import nn

from aurora.aneug_rhsia_execution import RHSIAExecutionAdapter


class SyntheticCore(nn.Module):
    def __init__(self):
        super().__init__()
        self.node_encoder = nn.Linear(3, 3)
        self.node_encoder.chunk_nodes = 512
        self.phases = 80

    def forward_snapshot(self, features, phases, waveform, *, period, output_scale):
        return self.node_encoder(features["coordinates"]) * output_scale

    def forward_cycle(self, features, waveform, *, period, output_scale):
        return torch.stack([self.forward_snapshot(features, None, waveform,
            period=period, output_scale=output_scale) for _ in range(self.phases)])


class ExecutionAdapterTests(unittest.TestCase):
    def test_float32_default_preserves_values_parameters_and_gradients(self):
        torch.manual_seed(4)
        core = SyntheticCore()
        adapted = RHSIAExecutionAdapter(copy.deepcopy(core), node_chunk_size=2048)
        features = dict(coordinates=torch.randn(6, 3))
        phases, waveform = torch.tensor([0]), torch.ones(32)
        a = core.forward_snapshot(features, phases, waveform, period=.8, output_scale=2.)
        b = adapted.forward_snapshot(features, phases, waveform, period=.8, output_scale=2.)
        torch.testing.assert_close(a, b, rtol=0, atol=0)
        a.square().mean().backward()
        b.square().mean().backward()
        for p, q in zip(core.parameters(), adapted.parameters()):
            torch.testing.assert_close(p.grad, q.grad, rtol=0, atol=0)
        self.assertEqual(sum(p.numel() for p in core.parameters()), sum(p.numel() for p in adapted.parameters()))
        self.assertEqual(adapted.core.node_encoder.chunk_nodes, 2048)
        self.assertTrue(all(n.startswith("core.") for n in adapted.state_dict()))
        adapted.eval()
        self.assertEqual(adapted.forward_cycle(features, waveform, period=.8, output_scale=2.).shape, (80, 6, 3))
        self.assertFalse(adapted.forward_cycle(features, waveform, period=.8, output_scale=2.).requires_grad)

    def test_no_silent_CPU_mixed_precision_or_training_cycle(self):
        adapted = RHSIAExecutionAdapter(SyntheticCore(), precision="cuda_bfloat16")
        features = dict(coordinates=torch.randn(6, 3))
        with self.assertRaisesRegex(RuntimeError, "allocated CUDA"):
            adapted.forward_snapshot(features, torch.tensor([0]), torch.ones(32), period=.8, output_scale=2.)
        with self.assertRaisesRegex(RuntimeError, "eval"):
            adapted.forward_cycle(features, torch.ones(32), period=.8, output_scale=2.)
        for kwargs in (dict(precision="implicit"), dict(node_chunk_size=0), dict(node_chunk_size=True)):
            with self.assertRaises(ValueError):
                RHSIAExecutionAdapter(SyntheticCore(), **kwargs)

    def test_actual_PyG_core_values_and_gradients_with_execution_chunk_change(self):
        try:
            import torch_geometric
        except ImportError:
            self.skipTest("run actual PyG check in the pinned comparator container")
        from aurora.aneug_rhsia_graph_transformer import RHSIAGraphTransformer
        torch.set_num_threads(1)
        torch.manual_seed(8)
        core = RHSIAGraphTransformer(hidden=16, heads=4, layers=1, phases=80,
            pe_width=8, pe_layers=1, pe_feedforward=16, dropout=0.)
        adapted = RHSIAExecutionAdapter(copy.deepcopy(core), node_chunk_size=3)
        features = dict(node_features=torch.randn(6, 10), ghd_descriptors=torch.randn(6, 8, 7),
            cot_descriptors=torch.randn(6, 16, 5), batch=torch.zeros(6, dtype=torch.long),
            edge_index=torch.tensor([[0, 1, 1, 2, 2, 3, 3, 4, 4, 5], [1, 0, 2, 1, 3, 2, 4, 3, 5, 4]]))
        args = (features, torch.tensor([39]), torch.linspace(1, 2, 32))
        a = core.forward_snapshot(*args, period=.8, output_scale=2.)
        b = adapted.forward_snapshot(*args, period=.8, output_scale=2.)
        torch.testing.assert_close(a, b, rtol=2e-5, atol=2e-6)
        a.square().mean().backward()
        b.square().mean().backward()
        for p, q in zip(core.parameters(), adapted.parameters()):
            torch.testing.assert_close(p.grad, q.grad, rtol=2e-5, atol=2e-6)


if __name__ == "__main__":
    unittest.main()
