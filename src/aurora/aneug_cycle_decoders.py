"""Development decoders for fair cross-regime and periodic-output comparisons.

These are AURORA controls, NOT an exact RHSIA reproduction or an established
architectural contribution. They perform no file IO or split selection. Callers
must supply audited phase coordinates and use the common physical evaluator.
Existing v2 model and training modules deliberately remain unchanged.
"""

from __future__ import annotations

import math
from typing import Mapping

import torch
from torch import nn


class CycleDecoderError(ValueError):
    """An input cannot represent the declared cycle or regime."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise CycleDecoderError(reason)


class RealPeriodicBasis(nn.Module):
    """Real Fourier basis on an explicitly supplied uniform, nonduplicated cycle.

    Columns have unit norm under the phase-average inner product. For an even
    phase count, Nyquist has one cosine column, never a redundant sine column.
    Phases are fractions of one period; a shifted origin is allowed. A repeated
    endpoint (e.g. linspace(0, 1, 80)) is rejected instead of silently changing
    the physical sampling grid. This is a representation, not a PDE constraint.
    """

    def __init__(self, phase_fractions: torch.Tensor, max_frequency: int) -> None:
        super().__init__()
        phases = torch.as_tensor(phase_fractions, dtype=torch.float64).detach().clone()
        _require(phases.ndim == 1 and phases.numel() >= 3, "phase_shape")
        _require(bool(torch.isfinite(phases).all()), "phase_finite")
        count = phases.numel()
        _require(
            isinstance(max_frequency, int) and not isinstance(max_frequency, bool)
            and 0 <= max_frequency <= count // 2,
            "max_frequency",
        )
        spacing = phases[1:] - phases[:-1]
        _require(
            bool(torch.allclose(spacing, torch.full_like(spacing, 1 / count),
                                rtol=0, atol=2e-7)),
            "uniform_unique_full_cycle_required",
        )
        angle = 2 * math.pi * (phases - phases[0])
        columns = [torch.ones_like(angle)]
        frequencies = [0]
        for frequency in range(1, max_frequency + 1):
            nyquist = count % 2 == 0 and frequency == count // 2
            scale = 1.0 if nyquist else math.sqrt(2)
            columns.append(scale * torch.cos(frequency * angle))
            frequencies.append(frequency)
            if not nyquist:
                columns.append(scale * torch.sin(frequency * angle))
                frequencies.append(frequency)
        self.register_buffer("phase_fractions", phases)
        self.register_buffer("matrix", torch.stack(columns, dim=1))
        self.register_buffer("frequencies", torch.tensor(frequencies, dtype=torch.long))
        self.max_frequency = max_frequency
        self.phase_count = count
        self.coefficient_count = len(columns)

    def encode(self, field: torch.Tensor) -> torch.Tensor:
        """Project [phase, node, vector] to [node, coefficient, vector]."""
        _require(field.ndim == 3 and field.shape[0] == self.phase_count
                 and field.shape[-1] == 3, "field_shape")
        _require(field.is_floating_point() and bool(torch.isfinite(field).all()),
                 "field_finite_float")
        return torch.einsum("tm,tnc->nmc", self.matrix.to(field), field) / self.phase_count

    def decode(self, coefficients: torch.Tensor) -> torch.Tensor:
        _require(coefficients.ndim == 3
                 and coefficients.shape[1:] == (self.coefficient_count, 3),
                 "coefficient_shape")
        _require(coefficients.is_floating_point(), "coefficient_float")
        return torch.einsum("tm,nmc->tnc", self.matrix.to(coefficients), coefficients)


class FourierCycleDecoder(nn.Module):
    """Fourier-only ablation: no steady anchor, gating, or separate metric head."""

    def __init__(self, width: int, basis: RealPeriodicBasis) -> None:
        super().__init__()
        _require(width > 0, "width")
        self.basis = basis
        self.coefficients = nn.Sequential(
            nn.Linear(width, width), nn.SiLU(),
            nn.Linear(width, basis.coefficient_count * 3),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        values = self.coefficients(features).reshape(
            features.shape[0], self.basis.coefficient_count, 3
        )
        return self.basis.decode(values)


class MaskedRegimeDecoder(nn.Module):
    """Simple shared snapshot decoder with explicit missing-time semantics.

    -1 means steady, while every integer from 0 through T-1 is transient.
    The entire learned time feature is masked AFTER its biased MLP, ensuring
    a phase-free steady input. An optional observed-regime indicator is a
    separate ordinary control. This does not implement RHSIA's waveform CNN,
    spectral geometry encoders, or per-GPS-block conditioning.
    """

    def __init__(self, width: int, phase_fractions: torch.Tensor, *,
                 phase_width: int = 16, regime_indicator: bool = False) -> None:
        super().__init__()
        _require(width > 0 and phase_width > 0 and phase_width % 2 == 0, "width")
        phases = torch.as_tensor(phase_fractions, dtype=torch.float64).detach().clone()
        _require(phases.ndim == 1 and phases.numel() >= 2
                 and bool(torch.isfinite(phases).all()), "phase_fractions")
        _require(bool((phases[1:] > phases[:-1]).all())
                 and float(phases[-1] - phases[0]) < 1.0,
                 "ordered_nonduplicated_cycle")
        self.register_buffer("phase_fractions", phases)
        self.register_buffer("harmonics", torch.arange(1, phase_width // 2 + 1))
        self.phase_count = phases.numel()
        self.width = width
        self.regime_indicator = regime_indicator
        self.phase_mlp = nn.Sequential(
            nn.Linear(phase_width, phase_width), nn.SiLU(),
            nn.Linear(phase_width, phase_width),
        )
        self.output = nn.Sequential(
            nn.Linear(width + phase_width + int(regime_indicator), width), nn.SiLU(),
            nn.Linear(width, 3),
        )

    def conditioning(self, phase_indices: torch.Tensor) -> torch.Tensor:
        _require(phase_indices.ndim == 1 and phase_indices.numel() > 0,
                 "phase_indices_shape")
        _require(phase_indices.dtype in (torch.int32, torch.int64), "phase_indices_dtype")
        _require(bool(((phase_indices >= -1) & (phase_indices < self.phase_count)).all()),
                 "phase_index_range")
        indices = phase_indices.to(self.phase_fractions.device)
        observed = indices >= 0
        angles = 2 * math.pi * self.phase_fractions[indices.clamp(min=0)]
        embedding = angles[:, None] * self.harmonics[None, :]
        embedding = torch.cat((embedding.cos(), embedding.sin()), dim=-1)
        parameter = next(self.phase_mlp.parameters())
        features = self.phase_mlp(embedding.to(parameter))
        features = features * observed[:, None].to(features)
        if self.regime_indicator:
            features = torch.cat((features, observed[:, None].to(features)), dim=-1)
        return features

    def forward(self, features: torch.Tensor, phase_indices: torch.Tensor) -> torch.Tensor:
        _require(features.ndim == 2 and features.shape[1] == self.width, "features_shape")
        condition = self.conditioning(phase_indices).to(features)
        count, nodes = condition.shape[0], features.shape[0]
        inputs = torch.cat((features.unsqueeze(0).expand(count, -1, -1),
                            condition.unsqueeze(1).expand(-1, nodes, -1)), dim=-1)
        return self.output(inputs)

    def forward_cycle(self, features: torch.Tensor, *, phase_batch_size: int = 8) -> torch.Tensor:
        """Share the geometry encoding; chunk only the snapshot decoder."""
        _require(isinstance(phase_batch_size, int) and phase_batch_size > 0, "phase_batch_size")
        phases = torch.arange(self.phase_count, device=features.device)
        return torch.cat([self(features, part) for part in phases.split(phase_batch_size)])

    def forward_steady(self, features: torch.Tensor) -> torch.Tensor:
        return self(features, torch.tensor([-1], device=features.device))[0]


class GeometryEncodedRegimeControl(nn.Module):
    """Attach the simple control to a geometry encoder without retaining its old head.

    A fresh, head-free encoder must be passed. The wrapper never mutates an
    existing trained model. Both regimes use the SAME physical output scale.
    """

    def __init__(self, encoder: nn.Module, decoder: MaskedRegimeDecoder, *,
                 output_scale: float) -> None:
        super().__init__()
        _require(callable(getattr(encoder, "encode_geometry", None)), "encoder")
        old_head = getattr(encoder, "output", None)
        _require(old_head is None or isinstance(old_head, nn.Identity), "encoder_must_be_head_free")
        _require(math.isfinite(output_scale) and output_scale > 0, "output_scale")
        self.encoder = encoder
        self.decoder = decoder
        self.register_buffer("output_scale", torch.tensor(float(output_scale)))

    def forward_cycle(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.decoder.forward_cycle(self.encoder.encode_geometry(case)) * self.output_scale

    def forward_single_field(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.decoder.forward_steady(self.encoder.encode_geometry(case)) * self.output_scale


def reconstruction_relative_l2(basis: RealPeriodicBasis, reference: torch.Tensor,
                               vertex_weights: torch.Tensor) -> torch.Tensor:
    """Representation oracle for one admitted case; not learned prediction error.

    Dataset admission remains the caller's responsibility. Scientific use must
    audit only training fields first, without selecting a cutoff on test labels.
    """
    _require(reference.ndim == 3 and vertex_weights.shape == (reference.shape[1],),
             "weights_shape")
    weights = vertex_weights.to(reference)
    _require(bool(torch.isfinite(weights).all()) and bool((weights >= 0).all())
             and bool(weights.sum() > 0), "weights")
    reconstructed = basis.decode(basis.encode(reference))
    numerator = ((reconstructed - reference).square() * weights[None, :, None]).sum()
    denominator = (reference.square() * weights[None, :, None]).sum()
    return torch.sqrt(numerator / denominator.clamp_min(1e-12))
