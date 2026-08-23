"""Shared-encoder single-field adapter for the registered T+M and T+S cells.

The adapter is model-agnostic over release-730 backbones exposing
``encode_geometry`` and ``decode_cycle``.  T+M and T+S use the same auxiliary
head interface and differ only in their train-only auxiliary information.
This file selects no backbone, objective coefficient, activation, or run.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

import torch
from torch import nn


class SingleFieldAuxiliaryError(RuntimeError):
    """Raised when a shared-encoder auxiliary contract is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise SingleFieldAuxiliaryError(reason)


def transient_mean_auxiliary_case(
    case: Mapping[str, torch.Tensor],
) -> dict[str, torch.Tensor]:
    """Create one T+M target from an already admitted train-transient case."""

    required = ("coordinates", "normals", "vertex_weights", "ghd", "wss")
    _require(all(key in case for key in required), "transient_case")
    wss = case["wss"]
    _require(
        wss.ndim == 3
        and wss.shape[0] == 80
        and wss.shape[2] == 3
        and bool(torch.isfinite(wss).all().item()),
        "transient_wss",
    )
    output = {key: case[key] for key in required[:-1]}
    output["single_field_wss"] = wss.mean(dim=0)
    return output


def steady_auxiliary_case(case: Mapping[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    """Normalize the lazy steady reader's key without copying its field."""

    required = ("coordinates", "normals", "vertex_weights", "ghd", "steady_wss")
    _require(all(key in case for key in required), "steady_case")
    steady = case["steady_wss"]
    _require(
        steady.ndim == 2
        and steady.shape[1] == 3
        and bool(torch.isfinite(steady).all().item()),
        "steady_wss",
    )
    output = {key: case[key] for key in required[:-1]}
    output["single_field_wss"] = steady
    return output


def scaled_single_field_target(
    case: Mapping[str, torch.Tensor], target_scale: float
) -> torch.Tensor:
    """Return the dimensionless target used by the common auxiliary head."""

    _require(
        math.isfinite(float(target_scale)) and float(target_scale) > 0.0,
        "target_scale",
    )
    _require("single_field_wss" in case, "single_field_target")
    target = case["single_field_wss"]
    _require(
        target.ndim == 2
        and target.shape[1] == 3
        and bool(torch.isfinite(target).all().item()),
        "single_field_target",
    )
    return target / float(target_scale)


class SharedEncoderSingleFieldAdapter(nn.Module):
    """Attach one normalized vector-field head to a complete-cycle backbone."""

    def __init__(self, backbone: nn.Module) -> None:
        super().__init__()
        _require(callable(getattr(backbone, "encode_geometry", None)), "encoder")
        _require(callable(getattr(backbone, "decode_cycle", None)), "cycle_decoder")
        width = int(getattr(backbone, "encoded_width", 0))
        _require(width > 0, "encoded_width")
        self.backbone = backbone
        self.single_field_head = nn.Sequential(
            nn.LayerNorm(width),
            nn.Linear(width, width),
            nn.SiLU(),
            nn.Linear(width, 3),
        )

    def forward(
        self, case: Mapping[str, torch.Tensor], *, mode: str
    ) -> torch.Tensor:
        _require(mode in {"cycle", "single_field"}, "mode")
        features = self.backbone.encode_geometry(case)
        _require(
            features.ndim == 2
            and features.shape[1] == int(self.backbone.encoded_width),
            "encoded_features",
        )
        if mode == "cycle":
            return self.backbone.decode_cycle(features)
        return self.single_field_head(features)
