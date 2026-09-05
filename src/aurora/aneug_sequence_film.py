"""Paper-described sequence/steady-FiLM comparator, not a new architecture.

Sheng et al. III-F specifies a Chebyshev graph U-Net, waveform cross-attention,
an MLP complete-cycle readout and an optional separately predicted steady
prior. Its exact sequence/FiLM class is absent from the pinned released tree.
This explicit reimplementation supplies those operations without vendoring
upstream code. Widths, FiLM placement and normalization are declared choices.
No CFD target or statistical fit belongs in a model's inference interface.
"""
from __future__ import annotations

import math
from typing import Mapping

import torch
from torch import nn
from torch.nn import functional as F

from aurora.aneug_external_cycle_adapter import geometry_node_features
from aurora.aneug_rhsia_graph_transformer import TemporalWaveformEncoder


def geometry_only(case: Mapping[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    """Strip targets before handing geometry to either independently run model."""
    keys = ("coordinates", "normals", "vertex_weights", "ghd")
    return {key: case[key] for key in keys if key in case}


@torch.no_grad()
def interpolation_stencil(coarse: torch.Tensor, fine: torch.Tensor,
                          *, neighbors: int = 3, chunk_size: int = 512):
    """Three-neighbor inverse-squared-distance feature interpolation.

    Mesh *edges* remain the supplied topology. Nearest neighbors are used only
    for U-Net feature upsampling, as in the released FPModule. Chunking avoids
    materializing a full fine-by-coarse distance matrix and requires no compiled
    torch-cluster extension. Stencils contain geometry only, not learned state.
    """
    if (coarse.ndim != 2 or fine.ndim != 2 or coarse.shape[1] != 3
            or fine.shape[1] != 3 or len(coarse) < neighbors or len(fine) == 0
            or type(neighbors) is not int or neighbors < 1
            or type(chunk_size) is not int or chunk_size < 1
            or coarse.device != fine.device or coarse.dtype != fine.dtype
            or not bool(torch.isfinite(coarse).all() and torch.isfinite(fine).all())):
        raise ValueError("finite compatible coordinates and positive interpolation dimensions required")
    indices, weights = [], []
    for start in range(0, len(fine), chunk_size):
        # Direct distances preserve zero distance at retained mesh vertices.
        squared = torch.cdist(fine[start:start + chunk_size], coarse,
                              compute_mode="donot_use_mm_for_euclid_dist").square()
        distance, index = squared.topk(neighbors, dim=1, largest=False, sorted=True)
        inverse = 1 / distance.clamp_min(1e-16)
        indices.append(index)
        weights.append(inverse / inverse.sum(1, keepdim=True))
    return torch.cat(indices), torch.cat(weights)


def interpolate_features(features, stencil):
    index, weight = stencil
    return (features[index] * weight[..., None]).sum(1)


class _ChebStack(nn.Module):
    def __init__(self, widths, *, order=3):
        super().__init__()
        from torch_geometric.nn import ChebConv
        self.layers = nn.ModuleList(ChebConv(a, b, K=order, normalization="sym")
                                    for a, b in zip(widths[:-1], widths[1:]))

    def forward(self, x, edges):
        for layer in self.layers:
            x = F.relu(layer(x, edges))
        return x


class HierarchicalChebEncoder(nn.Module):
    """Three-level Cheb U-Net with global max context and genuine mesh skips.

    Default layer widths follow the released generic U-Net scale, not a toy
    MLP substituted for the direct comparator. Topology is shared registered
    geometry; position-dependent interpolation is recomputed per input call.
    No persistent geometry or learned-embedding cache is held by the model.
    """
    def __init__(self, topology: Mapping[str, torch.Tensor], *, include_ghd=False,
                 encoder_widths=(64, 128, 256), decoder_widths=(512, 128),
                 global_width=2048, intermediate_widths=(32, 64, 128, 1024, 256),
                 global_hidden=(512, 1024), cheb_order=3, interpolation_chunk=512):
        super().__init__()
        dimensions = (*encoder_widths, *decoder_widths, global_width,
                      *intermediate_widths, *global_hidden, cheb_order, interpolation_chunk)
        if (len(encoder_widths) != 3 or len(decoder_widths) != 2
                or len(intermediate_widths) != 5 or len(global_hidden) != 2
                or any(type(v) is not int or v < 1 for v in dimensions)):
            raise ValueError("positive explicit U-Net dimensions required")
        self.include_ghd, self.input_width = include_ghd, 439 if include_ghd else 6
        self.output_width = decoder_widths[-1]
        self.interpolation_chunk = interpolation_chunk
        for key in ("edge0", "edge1", "edge2", "idx1", "idx2"):
            value = topology[key].detach().clone()
            if value.dtype != torch.long or value.numel() == 0 or bool((value < 0).any()):
                raise ValueError("nonempty integer registered topology required")
            if key.startswith("edge") and (value.ndim != 2 or value.shape[0] != 2):
                raise ValueError("edges must have shape [2,E]")
            if key.startswith("idx") and (value.ndim != 1 or len(value.unique()) != len(value)):
                raise ValueError("unique one-dimensional hierarchy indices required")
            self.register_buffer(key, value)
        if (len(self.idx2) < 3 or len(self.idx1) < 3
                or int(self.idx2.max()) >= len(self.idx1)
                or int(self.edge1.max()) >= len(self.idx1)
                or int(self.edge2.max()) >= len(self.idx2)):
            raise ValueError("registered hierarchy bounds")
        a, b, c = encoder_widths
        d, e = decoder_widths
        p, q, r, s, t = intermediate_widths
        self.down0 = _ChebStack((self.input_width, p, p, a), order=cheb_order)
        self.down1 = _ChebStack((a + 3, q, q, b), order=cheb_order)
        self.bottom = _ChebStack((b + 3, r, r, c), order=cheb_order)
        self.global_context = nn.Sequential(
            nn.Linear(b + 3, global_hidden[0]), nn.ReLU(),
            nn.Linear(global_hidden[0], global_hidden[1]), nn.ReLU(),
            nn.Linear(global_hidden[1], global_width), nn.ReLU())
        self.up1 = _ChebStack((global_width + c + a, s, s, d), order=cheb_order)
        self.up0 = _ChebStack((d + self.input_width, t, t, e), order=cheb_order)
        self.recipe = dict(include_ghd=include_ghd, encoder_widths=list(encoder_widths),
            decoder_widths=list(decoder_widths), global_width=global_width,
            intermediate_widths=list(intermediate_widths), global_hidden=list(global_hidden),
            cheb_order=cheb_order, interpolation_chunk=interpolation_chunk,
            global_mlp_normalization="none_explicit_reimplementation")

    def forward(self, case: Mapping[str, torch.Tensor]):
        positions, normals = case["coordinates"], case["normals"]
        if (positions.ndim != 2 or positions.shape[1] != 3 or normals.shape != positions.shape
                or positions.device != self.edge0.device
                or not bool(torch.isfinite(positions).all() and torch.isfinite(normals).all())
                or int(self.idx1.max()) >= len(positions) or int(self.edge0.max()) >= len(positions)):
            raise ValueError("input geometry does not match the registered hierarchy")
        x = geometry_node_features(case) if self.include_ghd else torch.cat((positions, normals), -1)
        pos1, pos2 = positions[self.idx1], positions[self.idx1][self.idx2]
        h1 = self.down0(x, self.edge0)[self.idx1]
        h2 = self.down1(torch.cat((h1, pos1), -1), self.edge1)[self.idx2]
        coarse = torch.cat((h2, pos2), -1)
        bottom = self.bottom(coarse, self.edge2)
        context = self.global_context(coarse).amax(0, keepdim=True).expand(len(pos2), -1)
        up1 = interpolate_features(torch.cat((bottom, context), -1),
            interpolation_stencil(pos2, pos1, chunk_size=self.interpolation_chunk))
        up1 = self.up1(torch.cat((up1, h1), -1), self.edge1)
        up0 = interpolate_features(up1,
            interpolation_stencil(pos1, positions, chunk_size=self.interpolation_chunk))
        return self.up0(torch.cat((up0, x), -1), self.edge0)


class SteadyWSSPredictor(nn.Module):
    """Separate geometry-only steady surrogate for the FiLM comparator."""
    def __init__(self, encoder: HierarchicalChebEncoder, *, output_scale: float):
        super().__init__()
        if not math.isfinite(output_scale) or output_scale <= 0:
            raise ValueError("positive training-derived steady output scale required")
        self.encoder = encoder
        self.readout = nn.Sequential(nn.Linear(encoder.output_width, 64), nn.ReLU(), nn.Linear(64, 3))
        self.register_buffer("output_scale", torch.tensor(float(output_scale)))

    def forward(self, case):
        return self.readout(self.encoder(geometry_only(case))) * self.output_scale


class _WaveCrossAttention(nn.Module):
    def __init__(self, width, heads, dropout):
        super().__init__()
        self.attention = nn.MultiheadAttention(width, heads, dropout=dropout, batch_first=True)
        self.norm1, self.norm2 = nn.LayerNorm(width), nn.LayerNorm(width)
        self.feedforward = nn.Sequential(nn.Linear(width, 4 * width), nn.GELU(),
                                         nn.Dropout(dropout), nn.Linear(4 * width, width))
        self.dropout = nn.Dropout(dropout)

    def forward(self, geometry, waveform):
        # Only N-by-T cross-attention, not an undocumented N-by-N self-attention.
        update = self.attention(geometry[None], waveform[None], waveform[None],
                                need_weights=False)[0][0]
        h = self.norm1(geometry + self.dropout(update))
        return self.norm2(h + self.dropout(self.feedforward(h)))


class SequenceFiLMWSS(nn.Module):
    """One geometry encoding and one full-cycle readout, optionally steady-FiLM.

    The prior is frozen AND kept in eval mode during transient training. Only
    its predicted physical [N,3] field conditions FiLM; true steady labels are
    never accepted. The private runner must bind the separately trained prior's
    provenance. Passing an untrained prior does not constitute a valid baseline.
    """
    def __init__(self, encoder: HierarchicalChebEncoder, waveform: torch.Tensor, *,
                 output_scale: float, period: float, phases=80, heads=8,
                 cross_layers=2, dropout=.1, steady_prior: nn.Module | None = None,
                 prior_conditioning_scale: float | None = None):
        super().__init__()
        if (not math.isfinite(output_scale) or output_scale <= 0
                or not math.isfinite(period) or period <= 0
                or type(phases) is not int or phases < 3
                or type(heads) is not int or heads < 1 or encoder.output_width % heads
                or type(cross_layers) is not int or cross_layers < 1
                or not math.isfinite(dropout) or not 0 <= dropout < 1):
            raise ValueError("sequence dimensions, scales or period")
        if waveform.ndim != 1 or len(waveform) < 8 or not bool(torch.isfinite(waveform).all()):
            raise ValueError("supplied finite waveform required")
        if (steady_prior is None) != (prior_conditioning_scale is None):
            raise ValueError("a steady prior and its fixed conditioning scale must be supplied together")
        if steady_prior is not None and (not math.isfinite(prior_conditioning_scale)
                                         or prior_conditioning_scale <= 0):
            raise ValueError("positive training-derived FiLM conditioning scale required")
        self.encoder, self.phases, self.period = encoder, phases, period
        self.register_buffer("waveform", waveform.detach().clone())
        self.register_buffer("output_scale", torch.tensor(float(output_scale)))
        self.temporal = TemporalWaveformEncoder(phases=phases)
        width = encoder.output_width
        self.wave_projection = nn.Linear(self.temporal.output_width, width)
        self.cross = nn.ModuleList(_WaveCrossAttention(width, heads, dropout) for _ in range(cross_layers))
        # Initialize all common parameters before the optional FiLM module so
        # paired seeds give the T and T+S paths identical common initial weights.
        self.readout = nn.Sequential(nn.Linear(width, width), nn.ReLU(),
                                     nn.Linear(width, 64), nn.ReLU(), nn.Linear(64, phases * 3))
        self.prior = steady_prior
        if self.prior is not None:
            if {id(p) for p in encoder.parameters()} & {id(p) for p in self.prior.parameters()}:
                raise ValueError("the steady predictor must be separate, not an aliased transient encoder")
            self.prior.requires_grad_(False)
            self.prior.zero_grad(set_to_none=True)
            self.prior.eval()
            self.register_buffer("prior_conditioning_scale", torch.tensor(float(prior_conditioning_scale)))
            self.film = nn.Sequential(nn.Linear(3, 64), nn.ReLU(), nn.Linear(64, 2 * width))

    def train(self, mode: bool = True):
        super().train(mode)
        if self.prior is not None:
            self.prior.eval()
        return self

    def forward_cycle(self, case):
        geometry = geometry_only(case)
        h = self.encoder(geometry)
        times = torch.arange(self.phases, device=h.device)
        waveform = self.wave_projection(self.temporal(times, self.waveform, self.period))
        for layer in self.cross:
            h = layer(h, waveform)
        if self.prior is not None:
            with torch.no_grad():
                prediction = self.prior(geometry)
            if prediction.shape != (len(h), 3) or not bool(torch.isfinite(prediction).all()):
                raise ValueError("finite physical steady prediction [N,3] required")
            gamma, beta = self.film(prediction / self.prior_conditioning_scale).chunk(2, -1)
            h = (1 + gamma) * h + beta
        cycle = self.readout(h).reshape(len(h), self.phases, 3).permute(1, 0, 2)
        return cycle.contiguous() * self.output_scale

    def forward(self, case):
        return self.forward_cycle(case)
