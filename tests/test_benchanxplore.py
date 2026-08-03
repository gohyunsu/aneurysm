import unittest

try:
    import torch
except ImportError:  # pragma: no cover - local protocol-only environment
    torch = None

if torch is not None:
    from aurora.benchanxplore import fourier_reconstruct, reconstruction_metrics


@unittest.skipIf(torch is None, "operator experiment dependencies are not installed")
class TemporalBasisTests(unittest.TestCase):
    def test_low_frequency_signal_is_reconstructed(self):
        time = torch.arange(80, dtype=torch.float32)
        signal = (
            2.0
            + torch.sin(2.0 * torch.pi * time / 80.0)
            + 0.25 * torch.cos(4.0 * torch.pi * time / 80.0)
        )
        signal = signal[:, None, None].repeat(1, 4, 3)
        prediction = fourier_reconstruct(signal, modes=2)
        self.assertLess(float(torch.max(torch.abs(signal - prediction))), 1e-5)

    def test_metrics_detect_removed_high_mode(self):
        time = torch.arange(80, dtype=torch.float32)
        signal = torch.sin(20.0 * torch.pi * time / 80.0)
        signal = signal[:, None, None].repeat(1, 5, 3)
        prediction = fourier_reconstruct(signal, modes=2)
        metrics = reconstruction_metrics(
            signal, prediction, torch.ones(5, dtype=torch.bool)
        )
        self.assertGreater(metrics["relative_l2"], 0.9)
        self.assertLess(metrics["energy_retained"], 0.1)


if __name__ == "__main__":
    unittest.main()
