"""Publication-aligned Sheng/RHSIA comparator, not a proposed architecture.

The released GraphEncoder names GHD deformation coefficients ``ghd_lambda``;
they are NOT eigenvalues. This explicit adaptation preserves those coefficients
and per-node GHD/cotangent modes, adds the surface gradients and boundary labels
described in the paper, and injects masked time/waveform features at every GPS
block. It is a reimplementation, not a byte-exact author training reproduction.
No geometry descriptor, inlet waveform, normalization or case split is invented
or fitted here. The caller must supply independently admitted inputs.
"""
from __future__ import annotations

import math
from typing import Mapping

import torch
from torch import nn
from torch.nn import functional as F


def surface_scalar_gradients(vertices: torch.Tensor, faces: torch.Tensor,
                             values: torch.Tensor) -> torch.Tensor:
    """Area-averaged piecewise-linear scalar gradients, [N,K,3].

    Uses original faces, not Euclidean nearest-neighbor connections. Degenerate
    faces are an input error rather than silently changing the reference mesh.
    """
    if (vertices.ndim != 2 or vertices.shape[1] != 3 or values.ndim != 2
            or values.shape[0] != len(vertices) or faces.ndim != 2
            or faces.shape[1] != 3 or faces.dtype != torch.long):
        raise ValueError("surface scalar gradient shapes")
    if faces.numel() == 0 or bool((faces < 0).any() or (faces >= len(vertices)).any()):
        raise ValueError("surface face indices")
    if not bool(torch.isfinite(vertices).all() and torch.isfinite(values).all()):
        raise ValueError("nonfinite geometry or scalar field")
    a, b, c = vertices[faces[:, 0]], vertices[faces[:, 1]], vertices[faces[:, 2]]
    normal = torch.linalg.cross(b - a, c - a)
    norm_sq = normal.square().sum(-1)
    if bool((norm_sq <= torch.finfo(vertices.dtype).tiny).any()):
        raise ValueError("degenerate triangle")
    basis_gradients = torch.stack([torch.linalg.cross(normal, c - b),
                                  torch.linalg.cross(normal, a - c),
                                  torch.linalg.cross(normal, b - a)], dim=1) / norm_sq[:, None, None]
    face_gradient = torch.einsum("fvk,fvc->fkc", values[faces], basis_gradients)
    area = torch.sqrt(norm_sq) / 2
    result = values.new_zeros((len(vertices), values.shape[1], 3))
    weight = vertices.new_zeros(len(vertices))
    for corner in range(3):
        result.index_add_(0, faces[:, corner], face_gradient * area[:, None, None])
        weight.index_add_(0, faces[:, corner], area)
    if bool((weight == 0).any()):
        raise ValueError("isolated vertex has no surface gradient")
    return result / weight[:, None, None]


class TemporalWaveformEncoder(nn.Module):
    """Time MLP + derivative-conditioned 1-D U-Net; missing time is masked last.

    The U-Net follows the paper's stated waveform encoder family; its exact
    widths are an explicit recipe, since the released encoder is instead a
    three-layer strided CNN. A steady sample has no temporal feature at all.
    """
    def __init__(self, phases=80, time_width=8, waveform_width=8, conv_width=32):
        super().__init__()
        if phases < 3 or time_width < 2 or time_width % 2 or waveform_width < 1:
            raise ValueError("temporal dimensions")
        self.phases, self.time_width = phases, time_width
        self.output_width = time_width + waveform_width
        self.time_mlp = nn.Sequential(nn.Linear(time_width, time_width * 2), nn.ReLU(),
                                      nn.Linear(time_width * 2, time_width))
        self.wave_norm = nn.BatchNorm1d(3)
        self.down1 = nn.Sequential(nn.Conv1d(3, conv_width, 7, padding=3), nn.ReLU())
        self.down2 = nn.Sequential(nn.Conv1d(conv_width, 2 * conv_width, 7, stride=2, padding=3), nn.ReLU())
        self.bottleneck = nn.Sequential(nn.Conv1d(2 * conv_width, 4 * conv_width, 7, stride=2, padding=3), nn.ReLU())
        self.up2 = nn.Sequential(nn.Conv1d(6 * conv_width, 2 * conv_width, 3, padding=1), nn.ReLU())
        self.up1 = nn.Sequential(nn.Conv1d(3 * conv_width, conv_width, 3, padding=1), nn.ReLU(),
                                nn.Conv1d(conv_width, waveform_width, 1))

    def forward(self, phases: torch.Tensor, waveform: torch.Tensor, period: float):
        if (phases.ndim != 1 or phases.dtype != torch.long
                or bool((phases < -1).any() or (phases >= self.phases).any())):
            raise ValueError("phase index must be -1 (steady) or a valid snapshot")
        if (waveform.ndim != 1 or waveform.numel() < 8
                or not bool(torch.isfinite(waveform).all())
                or not math.isfinite(period) or period <= 0):
            raise ValueError("explicit finite waveform and positive period required")
        valid = phases >= 0
        if not bool(valid.any()):
            return waveform.new_zeros((len(phases), self.output_width))
        dt = period / waveform.numel()
        first = torch.diff(waveform) / dt
        first = torch.cat((first, first[-1:]))
        second = torch.diff(first) / dt
        second = torch.cat((second, second[-1:]))
        wave = self.wave_norm(torch.stack((waveform, first, second))[None])
        h1 = self.down1(wave)
        h2 = self.down2(h1)
        h3 = self.bottleneck(h2)
        u2 = self.up2(torch.cat((F.interpolate(h3, size=h2.shape[-1], mode="linear", align_corners=True), h2), 1))
        u1 = self.up1(torch.cat((F.interpolate(u2, size=h1.shape[-1], mode="linear", align_corners=True), h1), 1))
        encoded_wave = F.interpolate(u1, size=self.phases, mode="linear", align_corners=True)[0].T
        frequency = torch.exp(-math.log(100) * torch.arange(
            self.time_width // 2, device=waveform.device, dtype=waveform.dtype) / (self.time_width // 2))
        angles = phases.clamp_min(0).to(waveform.dtype)[:, None] * frequency
        encoded_time = self.time_mlp(torch.cat((angles.cos(), angles.sin()), -1))
        encoded = torch.cat((encoded_time, encoded_wave[phases.clamp_min(0)]), -1)
        return torch.where(valid[:, None], encoded, torch.zeros_like(encoded))


class SpectralNodeEncoder(nn.Module):
    """Per-node mode encoding; no first-node-to-whole-graph broadcasting.

    Caller-supplied descriptor channels are GHD: mode/gradient/deformation xyz
    (7), cotangent: mode/gradient/eigenvalue (5). Random sign flips, if used,
    must flip the mode and its gradient together before this module.
    """
    def __init__(self, hidden=64, pe_width=32, pe_heads=4, pe_layers=8,
                 pe_feedforward=2048, node_types=4, dropout=0.1, chunk_nodes=512):
        super().__init__()
        if hidden <= pe_width or pe_width % pe_heads:
            raise ValueError("spectral encoder width")
        self.node_types = node_types
        if type(chunk_nodes) is not int or chunk_nodes < 1:
            raise ValueError("positive node chunk size")
        self.chunk_nodes = chunk_nodes
        self.ghd_projection, self.cot_projection = nn.Linear(7, pe_width), nn.Linear(5, pe_width)
        def transformer():
            return nn.TransformerEncoder(nn.TransformerEncoderLayer(
                pe_width, pe_heads, dim_feedforward=pe_feedforward,
                dropout=dropout, batch_first=True), pe_layers, enable_nested_tensor=False)
        self.ghd_transformer, self.cot_transformer = transformer(), transformer()
        self.pe_post = nn.Sequential(nn.Linear(2 * pe_width, 4 * pe_width), nn.ReLU(),
                                     nn.Linear(4 * pe_width, pe_width), nn.ReLU())
        self.geometry_projection = nn.Linear(6 + node_types, hidden - pe_width)

    def _encode_modes(self, tokens, projection, transformer):
        # Attention is across each node's modes, never across different nodes.
        # Exact eval chunking and training recomputation bound dense FFN memory
        # on 13,902 vertices without shrinking the publication-sized network.
        from torch.utils.checkpoint import checkpoint
        def encode(chunk):
            return transformer(projection(chunk)).sum(1)
        outputs = []
        for chunk in tokens.split(self.chunk_nodes, dim=0):
            if self.training and torch.is_grad_enabled():
                outputs.append(checkpoint(encode, chunk, use_reentrant=False))
            else:
                outputs.append(encode(chunk))
        return torch.cat(outputs, 0)

    def forward(self, features: Mapping[str, torch.Tensor]):
        geometry = features["node_features"]
        ghd, cot = features["ghd_descriptors"], features["cot_descriptors"]
        if (geometry.ndim != 2 or geometry.shape[1] != 6 + self.node_types
                or ghd.shape != (len(geometry), 8, 7)
                or cot.shape != (len(geometry), 16, 5)):
            raise ValueError("explicit node, GHD8 and cot16 descriptors required")
        if not all(bool(torch.isfinite(v).all()) for v in (geometry, ghd, cot)):
            raise ValueError("nonfinite geometry descriptors")
        ghd_pe = self._encode_modes(ghd, self.ghd_projection, self.ghd_transformer)
        cot_pe = self._encode_modes(cot, self.cot_projection, self.cot_transformer)
        pe = self.pe_post(torch.cat((ghd_pe, cot_pe), -1))
        return torch.cat((self.geometry_projection(geometry), pe), -1)


class RHSIAGraphTransformer(nn.Module):
    """Native phase-conditioned PyG GPS/GINE model with masked steady samples.

    This class does NOT pretend that one snapshot is a complete cycle. Training
    must use a snapshot-aware exposure ledger. Full-cycle evaluation can call
    forward_snapshot for all phases, recording the actual cost.
    """
    def __init__(self, *, hidden=64, heads=4, layers=8, phases=80,
                 pe_width=32, pe_layers=8, pe_feedforward=2048,
                 node_types=4, dropout=0.1, attention="performer"):
        super().__init__()
        from torch_geometric.nn import GINEConv, GPSConv
        self.phases = phases
        self.node_encoder = SpectralNodeEncoder(hidden, pe_width, 4, pe_layers,
                                                pe_feedforward, node_types, dropout)
        self.edge_encoder = nn.Linear(12, hidden)
        self.temporal_encoder = TemporalWaveformEncoder(phases)
        self.time_injections = nn.ModuleList([
            nn.Linear(self.temporal_encoder.output_width, hidden, bias=False)
            for _ in range(layers)])
        self.blocks = nn.ModuleList([GPSConv(hidden, GINEConv(nn.Sequential(
            nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, hidden))),
            heads=heads, dropout=dropout, attn_type=attention) for _ in range(layers)])
        self.output = nn.Sequential(nn.Linear(hidden, hidden // 2), nn.ReLU(),
                                    nn.Linear(hidden // 2, hidden // 4), nn.ReLU(),
                                    nn.Linear(hidden // 4, 3))

    def forward_snapshot(self, features: Mapping[str, torch.Tensor], phase_indices: torch.Tensor,
                         waveform: torch.Tensor, *, period: float, output_scale: float):
        if not math.isfinite(output_scale) or output_scale <= 0:
            raise ValueError("positive train-only physical output scale required")
        edge_index, batch = features["edge_index"], features["batch"]
        if (batch.dtype != torch.long or batch.shape != (len(features["node_features"]),)
                or edge_index.dtype != torch.long or edge_index.ndim != 2 or edge_index.shape[0] != 2
                or batch.numel() == 0 or int(batch.min()) < 0
                or int(batch.max()) + 1 != len(phase_indices)):
            raise ValueError("explicit batched mesh metadata required")
        if (edge_index.numel() == 0 or bool((edge_index < 0).any() or (edge_index >= len(batch)).any())
                or bool((batch[edge_index[0]] != batch[edge_index[1]]).any())):
            raise ValueError("edge crosses graphs or has invalid index")
        geometry = features["node_features"][:, :6]
        i, j = edge_index
        edges = self.edge_encoder(torch.cat(((geometry[i] - geometry[j]).abs(),
                                             (geometry[i] + geometry[j]) / 2), -1))
        temporal = self.temporal_encoder(phase_indices, waveform, period)
        x = self.node_encoder(features)
        for block, inject in zip(self.blocks, self.time_injections):
            x = block(x + inject(temporal)[batch], edge_index, batch, edge_attr=edges)
        return self.output(x) * output_scale
