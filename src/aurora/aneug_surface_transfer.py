"""Development-only spatial-transfer candidate and common-backbone controls.

This is not an established novel operator or a trained scientific result.
Shared geometry-conditioned edge kernels receive steady and transient gradients;
only transient data train the frequency router and cycle coefficient readout.
No field target, archive, identifier, split, or fitted response basis is read.
"""

from __future__ import annotations

import math
from typing import Mapping

import torch
from torch import nn
from torch.nn import functional as F

from .aneug_cycle_decoders import RealPeriodicBasis
from .aneug_release_730_ghd_gps_baseline import Release730GHDGPSUNet


VARIANTS = ("fourier_only", "task_adapters", "always_shared", "selective_transfer")


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def geometry_inputs(case: Mapping[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    """Explicit allowlist: neither true steady nor transient WSS reaches inference."""
    return {name: case[name] for name in
            ("coordinates", "normals", "vertex_weights", "ghd")}


class ResidualTaskAdapter(nn.Module):
    """Ordinary residual MLP adapter, widenable for explicit capacity controls."""

    def __init__(self, width: int, bottleneck: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(width, bottleneck), nn.SiLU(),
                                    nn.Linear(bottleneck, width))

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return value + self.layers(value)


class SpatialKernelBank(nn.Module):
    """R learned, positive, neighbor-normalized kernels on supplied mesh edges.

    Each kernel weights projected source-node features using relative positions,
    edge length and normal agreement. Routing happens after neighbor aggregation,
    equivalent to a destination-node/mode-dependent mixture of these kernels.
    It is NOT a separate gate per edge, a PDE discretization or an equivariance
    guarantee. Geometry encoding and this bank are computed once per cycle.
    """

    def __init__(self, width: int, bank_width: int, operators: int,
                 edge_index: torch.Tensor) -> None:
        super().__init__()
        edges = torch.as_tensor(edge_index)
        _require(edges.ndim == 2 and edges.shape[0] == 2 and edges.numel() > 0
                 and edges.dtype in (torch.int32, torch.int64)
                 and bool((edges >= 0).all()), "mesh_edge_index")
        _require(min(width, bank_width, operators) > 0, "kernel_dimensions")
        self.register_buffer("edge_index", edges.detach().long().clone())
        self.operators, self.bank_width = operators, bank_width
        self.kernel = nn.Sequential(nn.Linear(5, bank_width), nn.SiLU(),
                                    nn.Linear(bank_width, operators))
        self.values = nn.Linear(width, operators * bank_width, bias=False)
        self.self_values = nn.Linear(width, operators * bank_width, bias=False)
        self.norm = nn.LayerNorm(bank_width)

    def forward(self, features: torch.Tensor, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        source, destination = self.edge_index
        count = features.shape[0]
        _require(int(self.edge_index.max()) < count, "edge_outside_geometry")
        positions, normals = case["coordinates"], case["normals"]
        _require(positions.shape == normals.shape == (count, 3), "mesh_geometry_shape")
        relative = positions[source] - positions[destination]
        descriptors = torch.cat((relative, relative.norm(dim=-1, keepdim=True),
                                 (normals[source] * normals[destination]).sum(-1, keepdim=True)), -1)
        weights = F.softplus(self.kernel(descriptors)) + 1e-6
        values = self.values(features).reshape(count, self.operators, self.bank_width)
        total = features.new_zeros(count, self.operators, self.bank_width)
        total.index_add_(0, destination, weights[..., None] * values[source])
        degree = features.new_zeros(count, self.operators)
        degree.index_add_(0, destination, weights)
        total = total / degree.clamp_min(1e-12)[..., None]
        local = self.self_values(features).reshape_as(total)
        return F.silu(self.norm(total + local))


class SurfaceTransferCycleModel(nn.Module):
    """Full-spectrum response with separated heads and optional kernel routing.

    All variants use the same full-width coefficient readout. Without adapters
    or kernels the transient path is exactly the existing Fourier-only MLP.
    No low-frequency truncation or output tangent projection is imposed.
    """

    def __init__(self, encoder: nn.Module, basis: RealPeriodicBasis, *,
                 variant: str, width: int, output_scale: float,
                 edge_index: torch.Tensor, auxiliary_steady: bool = True,
                 bank_width: int = 32, operators: int = 4,
                 adapter_width: int = 32, mode_chunk: int = 8) -> None:
        super().__init__()
        _require(variant in VARIANTS, "variant")
        _require(callable(getattr(encoder, "encode_geometry", None)), "geometry_encoder")
        _require(isinstance(getattr(encoder, "output", None), nn.Identity),
                 "fresh_head_free_encoder_required")
        _require(min(width, bank_width, operators, adapter_width) > 0, "model_dimensions")
        _require(isinstance(mode_chunk, int) and not isinstance(mode_chunk, bool)
                 and mode_chunk > 0, "mode_chunk")
        _require(math.isfinite(output_scale) and output_scale > 0, "output_scale")
        _require(basis.coefficient_count == basis.phase_count, "full_spectrum_required")
        self.encoder, self.basis, self.variant = encoder, basis, variant
        self.width, self.mode_chunk = width, mode_chunk
        self.auxiliary_steady = auxiliary_steady
        self.register_buffer("output_scale", torch.tensor(float(output_scale)))

        # Common modules precede optional ones, retaining paired initialization.
        self.cycle_hidden = nn.Sequential(nn.Linear(width, width), nn.SiLU())
        self.cycle_readout = nn.Linear(width, basis.coefficient_count * 3)
        if auxiliary_steady:
            self.steady_head = nn.Sequential(nn.Linear(width, width), nn.SiLU(),
                                             nn.Linear(width, 3))
        if variant != "fourier_only":
            self.transient_adapter = ResidualTaskAdapter(width, adapter_width)
            if auxiliary_steady:
                self.steady_adapter = ResidualTaskAdapter(width, adapter_width)
        if variant in ("always_shared", "selective_transfer"):
            self.bank = SpatialKernelBank(width, bank_width, operators, edge_index)
            self.bank_lift = nn.Linear(bank_width, width, bias=False)
        if variant == "selective_transfer":
            self.router_geometry = nn.Linear(width, bank_width)
            self.router_frequency = nn.Embedding(basis.max_frequency + 1, bank_width)
            self.router_output = nn.Linear(bank_width, operators)

    def routing_weights(self, features: torch.Tensor, frequencies: torch.Tensor) -> torch.Tensor:
        """[node, requested frequency, operator]; cos/sin share their routing.

        This is a model diagnostic, not evidence that gates identify physical
        transferability. Same-capacity and routing-intervention tests are needed.
        """
        _require(hasattr(self, "bank"), "no_kernel_bank")
        _require(frequencies.ndim == 1 and frequencies.numel() > 0
                 and frequencies.dtype in (torch.int32, torch.int64)
                 and bool(((frequencies >= 0) &
                           (frequencies <= self.basis.max_frequency)).all()), "frequency_index")
        if self.variant == "always_shared":
            return features.new_full((len(features), len(frequencies), self.bank.operators),
                                     1 / self.bank.operators)
        condition = (self.router_geometry(features)[:, None, :]
                     + self.router_frequency(frequencies)[None, :, :])
        return self.router_output(F.silu(condition)).softmax(dim=-1)

    def _coefficient_values(self, features: torch.Tensor,
                            bank: torch.Tensor | None) -> torch.Tensor:
        count = self.basis.coefficient_count
        if bank is not None and self.variant == "always_shared":
            # Uniform routing has no mode dependence: compute once, not 80 times.
            features = features + self.bank_lift(bank.mean(dim=1))
            bank = None
        if bank is None:
            if hasattr(self, "transient_adapter"):
                features = self.transient_adapter(features)
            return self.cycle_readout(self.cycle_hidden(features)).reshape(-1, count, 3)
        weights = self.cycle_readout.weight.reshape(count, 3, self.width)
        bias = self.cycle_readout.bias.reshape(count, 3)
        coefficients = []
        for start in range(0, count, self.mode_chunk):
            stop = min(start + self.mode_chunk, count)
            # Cosine/sine at one frequency use the same deterministic hidden
            # path. Reuse it inside this bounded chunk, retaining independent
            # coefficient readouts and the exact parameterization. No learned
            # tensor survives the current forward or crosses geometries.
            frequencies, inverse = torch.unique(
                self.basis.frequencies[start:stop], sorted=True, return_inverse=True)
            routing = self.routing_weights(features, frequencies)
            shared = torch.einsum("nmr,nrd->nmd", routing, bank)
            hidden = features[:, None, :] + self.bank_lift(shared)
            hidden = self.cycle_hidden(self.transient_adapter(hidden))
            hidden = hidden.index_select(1, inverse)
            coefficients.append(torch.einsum("nmh,mch->nmc", hidden, weights[start:stop])
                                + bias[None, start:stop, :])
        return torch.cat(coefficients, dim=1)

    def forward_coefficients(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        geometry = geometry_inputs(case)
        features = self.encoder.encode_geometry(geometry)
        bank = self.bank(features, geometry) if hasattr(self, "bank") else None
        return self._coefficient_values(features, bank) * self.output_scale

    def forward_cycle(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.basis.decode(self.forward_coefficients(case))

    def forward(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.forward_cycle(case)

    def forward_single_field(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        _require(self.auxiliary_steady, "steady_path_not_constructed")
        geometry = geometry_inputs(case)
        features = self.encoder.encode_geometry(geometry)
        if hasattr(self, "bank"):
            # No temporal router or cycle readout receives the steady target.
            shared = self.bank(features, geometry).mean(dim=1)
            features = features + self.bank_lift(shared)
        if hasattr(self, "steady_adapter"):
            features = self.steady_adapter(features)
        return self.steady_head(features) * self.output_scale


def build_surface_transfer_model(topology: Mapping[str, torch.Tensor],
                                 phase_fractions: torch.Tensor, *, variant: str,
                                 output_scale: float, width: int = 128, heads: int = 4,
                                 auxiliary_steady: bool = True, bank_width: int = 32,
                                 operators: int = 4, adapter_width: int = 32,
                                 mode_chunk: int = 8) -> SurfaceTransferCycleModel:
    """Fresh full-size existing mesh encoder, never an in-place trained-model edit."""
    encoder = Release730GHDGPSUNet(topology, width=width, heads=heads)
    encoder.output = nn.Identity()
    basis = RealPeriodicBasis(phase_fractions, len(phase_fractions) // 2)
    return SurfaceTransferCycleModel(
        encoder, basis, variant=variant, width=width, output_scale=output_scale,
        edge_index=topology["edge0"], auxiliary_steady=auxiliary_steady,
        bank_width=bank_width, operators=operators, adapter_width=adapter_width,
        mode_chunk=mode_chunk,
    )


def build_paired_surface_transfer_model(topology, phase_fractions, *, auxiliary_steady, **kwargs):
    """Initialize common T/T+S weights identically, then remove T-only dead heads.

    Constructing an auxiliary head consumes no data. Its parameters are removed
    before optimization/parameter accounting in the T-only condition. Callers
    seed identically and record shape-changing capacity controls separately.
    """
    model = build_surface_transfer_model(topology, phase_fractions,
                                         auxiliary_steady=True, **kwargs)
    if not auxiliary_steady:
        del model.steady_head
        if hasattr(model, "steady_adapter"):
            del model.steady_adapter
        model.auxiliary_steady = False
    return model
