"""Task adapters for externally supplied, unmodified neural-operator cores.

These adapters are not reproductions of a paper's dataset or training recipe.
They expose the admitted AneuG geometry and decode one complete WSS cycle.
No upstream source, weights, private identifiers or data loading lives here.
"""

from __future__ import annotations

import math
from types import SimpleNamespace
from typing import Mapping

import torch
from torch import nn


def geometry_node_features(
    case: Mapping[str, torch.Tensor], *, include_ghd: bool = True
) -> torch.Tensor:
    """Same coordinates, mesh normals, relative area and GHD as GHD/GPS.

    GHD is broadcast, not reconstructed from target WSS. Its train-only
    standardization and geometry normalization belong to the common reader.
    Labels may be present in ``case`` but are deliberately never accessed.
    """

    coordinates, normals = case["coordinates"], case["normals"]
    weights = case["vertex_weights"]
    if coordinates.ndim != 2 or coordinates.shape[1] != 3:
        raise ValueError("coordinates must have shape [nodes, 3]")
    if normals.shape != coordinates.shape or weights.shape != coordinates.shape[:1]:
        raise ValueError("normal/area shape mismatch")
    if weights.numel() == 0 or not bool(torch.isfinite(weights).all()):
        raise ValueError("finite nonempty area weights required")
    if not bool((weights > 0).all()):
        raise ValueError("positive vertex areas required")
    area = torch.log((weights / weights.mean()).clamp(min=1e-8)).unsqueeze(-1)
    features = [coordinates, normals, area]
    if include_ghd:
        ghd = case["ghd"]
        if ghd.shape != (432,):
            raise ValueError("standardized GHD must have shape [432]")
        features.append(ghd.unsqueeze(0).expand(coordinates.shape[0], -1))
    return torch.cat(features, dim=-1)


class ExternalLinearNOCycleAdapter(nn.Module):
    """Official ShapeNetCar LinearNO core + explicit 80×3 WSS readout.

    Supply ``LinearAttentionNeuralOperator`` with ``unified_pos=False``,
    ``Time_Input=False``, ``fun_dim=0``, ``space_dim=input_width`` and
    ``out_dim=3*phases``. Its attention, blocks and initializer stay unchanged.
    The separate private loader verifies exact upstream files before importing.

    This is geometry-only, transient-only task adaptation: no CFD anchor,
    waveform, steady supervision, tangent projection or periodic truncation.
    """

    def __init__(
        self,
        operator: nn.Module,
        *,
        output_scale: float,
        phases: int = 80,
        include_ghd: bool = True,
    ) -> None:
        super().__init__()
        if not math.isfinite(output_scale) or output_scale <= 0:
            raise ValueError("positive finite train-only output scale required")
        if isinstance(phases, bool) or not isinstance(phases, int) or phases < 2:
            raise ValueError("phases must be an integer >= 2")
        self.operator = operator
        self.phases = phases
        self.include_ghd = include_ghd
        self.register_buffer("output_scale", torch.tensor(float(output_scale)))

    @property
    def input_width(self) -> int:
        return 439 if self.include_ghd else 7

    def forward_cycle(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        features = geometry_node_features(case, include_ghd=self.include_ghd)
        # The author's forward unpacks this pair and reads only cfd_data.x.
        # No PyG dummy graph, target field or global module patch is needed.
        output = self.operator((SimpleNamespace(x=features), None))
        if output.shape != (features.shape[0], self.phases * 3):
            raise ValueError("external core returned an incompatible WSS shape")
        cycle = output.reshape(features.shape[0], self.phases, 3)
        return cycle.permute(1, 0, 2).contiguous() * self.output_scale

    def forward(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.forward_cycle(case)
