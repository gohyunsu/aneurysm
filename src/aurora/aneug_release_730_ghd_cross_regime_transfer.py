"""GHD steady-to-transient transfer primitives for complete-cycle WSS.

This module contains the model adapter and paired-gradient rule only.  It has
no dataset path, split, server, activation, training schedule or result
selection policy.  A caller must load a previously trained complete-cycle GHD
backbone and enforce the release protocol separately.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from aurora.aneug_release_730_single_field_auxiliary import (
    SharedEncoderSingleFieldHead,
)


class GHDCrossRegimeTransferError(RuntimeError):
    """Raised when a cross-regime model or gradient contract is invalid."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise GHDCrossRegimeTransferError(reason)


def _parameter_tuple(
    parameters: Sequence[nn.Parameter], label: str
) -> tuple[nn.Parameter, ...]:
    normalized = tuple(parameters)
    _require(bool(normalized), f"{label}_empty")
    _require(
        len({id(parameter) for parameter in normalized}) == len(normalized)
        and all(parameter.requires_grad for parameter in normalized),
        f"{label}_parameters",
    )
    return normalized


def _squared_norm(gradients: Sequence[torch.Tensor]) -> torch.Tensor:
    return sum(
        (torch.sum(gradient.square()) for gradient in gradients),
        start=torch.zeros((), device=gradients[0].device, dtype=gradients[0].dtype),
    )


def _dot(
    left: Sequence[torch.Tensor], right: Sequence[torch.Tensor]
) -> torch.Tensor:
    _require(len(left) == len(right) > 0, "gradient_dot_shape")
    return sum(
        (torch.sum(first * second) for first, second in zip(left, right, strict=True)),
        start=torch.zeros((), device=left[0].device, dtype=left[0].dtype),
    )


def _validate_gradients(
    parameters: Sequence[nn.Parameter], gradients: Sequence[torch.Tensor], label: str
) -> None:
    _require(len(parameters) == len(gradients), f"{label}_count")
    for parameter, gradient in zip(parameters, gradients, strict=True):
        _require(
            gradient is not None
            and gradient.shape == parameter.shape
            and gradient.device == parameter.device
            and gradient.dtype == parameter.dtype
            and bool(torch.isfinite(gradient).all().item()),
            f"{label}_gradient",
        )


def _accumulate(
    parameters: Sequence[nn.Parameter],
    gradients: Sequence[torch.Tensor],
    divisor: int,
) -> None:
    _require(divisor > 0, "accumulation_steps")
    for parameter, gradient in zip(parameters, gradients, strict=True):
        contribution = gradient.detach() / float(divisor)
        if parameter.grad is None:
            parameter.grad = contribution.clone()
        else:
            parameter.grad.add_(contribution)


class Release730GHDSteadyTransferModel(nn.Module):
    """Attach a disposable steady-field head to a complete-cycle GHD model."""

    def __init__(
        self,
        backbone: nn.Module,
        *,
        cycle_output_scale: float,
        auxiliary_output_scale: float,
    ) -> None:
        super().__init__()
        _require(callable(getattr(backbone, "encode_geometry", None)), "encoder")
        _require(callable(getattr(backbone, "decode_cycle", None)), "cycle_decoder")
        _require(isinstance(getattr(backbone, "output", None), nn.Module), "output_head")
        width = int(getattr(backbone, "encoded_width", 0))
        _require(width > 0, "encoded_width")
        _require(
            math.isfinite(float(cycle_output_scale)) and cycle_output_scale > 0.0,
            "cycle_output_scale",
        )
        _require(
            math.isfinite(float(auxiliary_output_scale))
            and auxiliary_output_scale > 0.0,
            "auxiliary_output_scale",
        )
        self.backbone = backbone
        self.single_field_head = SharedEncoderSingleFieldHead(width)
        self.register_buffer(
            "cycle_output_scale", torch.tensor(float(cycle_output_scale))
        )
        self.register_buffer(
            "auxiliary_output_scale", torch.tensor(float(auxiliary_output_scale))
        )

    def encode_geometry(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        features = self.backbone.encode_geometry(case)
        _require(
            features.ndim == 2
            and features.shape[1] == self.single_field_head.encoded_width,
            "encoded_features",
        )
        return features

    def forward_cycle(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return (
            self.backbone.decode_cycle(self.encode_geometry(case))
            * self.cycle_output_scale
        )

    def forward_single_field(self, case: Mapping[str, torch.Tensor]) -> torch.Tensor:
        return self.single_field_head(self.encode_geometry(case)) * self.auxiliary_output_scale

    def shared_encoder_parameters(self) -> tuple[nn.Parameter, ...]:
        cycle_ids = {id(parameter) for parameter in self.backbone.output.parameters()}
        parameters = tuple(
            parameter
            for parameter in self.backbone.parameters()
            if id(parameter) not in cycle_ids
        )
        return _parameter_tuple(parameters, "shared_encoder")

    def cycle_decoder_parameters(self) -> tuple[nn.Parameter, ...]:
        return _parameter_tuple(tuple(self.backbone.output.parameters()), "cycle_decoder")

    def auxiliary_head_parameters(self) -> tuple[nn.Parameter, ...]:
        return _parameter_tuple(
            tuple(self.single_field_head.parameters()), "auxiliary_head"
        )


def paired_cross_regime_backward(
    *,
    transient_loss: torch.Tensor,
    auxiliary_loss: torch.Tensor,
    shared_encoder_parameters: Sequence[nn.Parameter],
    cycle_decoder_parameters: Sequence[nn.Parameter],
    auxiliary_head_parameters: Sequence[nn.Parameter],
    variant: str,
    auxiliary_coefficient: float = 1.0,
    maximum_auxiliary_to_transient_shared_norm: float = 1.0,
    accumulation_steps: int = 1,
    epsilon: float = 1e-12,
) -> dict[str, float | bool | str]:
    """Backpropagate one transient/auxiliary pair without changing either head.

    ``naive_sum`` adds both shared-encoder gradients directly.  The
    ``field_anchored`` variant removes only an auxiliary component that
    opposes the transient field gradient, then caps the remaining auxiliary
    shared-gradient norm.  Cycle-head gradients always come only from the
    transient loss; auxiliary-head gradients always come only from the
    auxiliary loss.
    """

    _require(variant in {"naive_sum", "field_anchored"}, "variant")
    _require(
        transient_loss.ndim == auxiliary_loss.ndim == 0
        and bool(torch.isfinite(transient_loss).item())
        and bool(torch.isfinite(auxiliary_loss).item()),
        "loss",
    )
    _require(
        math.isfinite(float(auxiliary_coefficient)) and auxiliary_coefficient > 0.0,
        "auxiliary_coefficient",
    )
    _require(
        math.isfinite(float(maximum_auxiliary_to_transient_shared_norm))
        and maximum_auxiliary_to_transient_shared_norm > 0.0,
        "maximum_auxiliary_to_transient_shared_norm",
    )
    _require(accumulation_steps > 0 and epsilon > 0.0, "numerical_parameters")
    shared = _parameter_tuple(shared_encoder_parameters, "shared_encoder")
    cycle = _parameter_tuple(cycle_decoder_parameters, "cycle_decoder")
    auxiliary = _parameter_tuple(auxiliary_head_parameters, "auxiliary_head")
    shared_ids = {id(parameter) for parameter in shared}
    cycle_ids = {id(parameter) for parameter in cycle}
    auxiliary_ids = {id(parameter) for parameter in auxiliary}
    _require(
        shared_ids.isdisjoint(cycle_ids)
        and shared_ids.isdisjoint(auxiliary_ids)
        and cycle_ids.isdisjoint(auxiliary_ids),
        "parameter_partition",
    )

    transient_gradients = torch.autograd.grad(
        transient_loss, shared + cycle, retain_graph=False, create_graph=False
    )
    auxiliary_gradients = torch.autograd.grad(
        auxiliary_loss, shared + auxiliary, retain_graph=False, create_graph=False
    )
    transient_shared = tuple(transient_gradients[: len(shared)])
    transient_cycle = tuple(transient_gradients[len(shared) :])
    auxiliary_shared = tuple(auxiliary_gradients[: len(shared)])
    auxiliary_head = tuple(auxiliary_gradients[len(shared) :])
    _validate_gradients(shared, transient_shared, "transient_shared")
    _validate_gradients(cycle, transient_cycle, "transient_cycle")
    _validate_gradients(shared, auxiliary_shared, "auxiliary_shared")
    _validate_gradients(auxiliary, auxiliary_head, "auxiliary_head")

    weighted_auxiliary = tuple(
        gradient * float(auxiliary_coefficient) for gradient in auxiliary_shared
    )
    transient_norm_squared = _squared_norm(transient_shared)
    auxiliary_norm_squared = _squared_norm(weighted_auxiliary)
    _require(
        bool(torch.isfinite(transient_norm_squared).item())
        and bool(torch.isfinite(auxiliary_norm_squared).item())
        and float(transient_norm_squared.item()) > epsilon,
        "shared_gradient_norm",
    )
    transient_norm = torch.sqrt(transient_norm_squared)
    auxiliary_norm = torch.sqrt(torch.clamp(auxiliary_norm_squared, min=0.0))
    dot_before = _dot(transient_shared, weighted_auxiliary)
    denominator = torch.clamp(transient_norm * auxiliary_norm, min=epsilon)
    cosine_before = dot_before / denominator

    projection_applied = False
    norm_scale = 1.0
    effective_auxiliary = weighted_auxiliary
    if variant == "field_anchored":
        if float(dot_before.item()) < 0.0:
            coefficient = dot_before / torch.clamp(transient_norm_squared, min=epsilon)
            effective_auxiliary = tuple(
                auxiliary_gradient - coefficient * transient_gradient
                for auxiliary_gradient, transient_gradient in zip(
                    effective_auxiliary, transient_shared, strict=True
                )
            )
            projection_applied = True
        effective_norm = torch.sqrt(
            torch.clamp(_squared_norm(effective_auxiliary), min=0.0)
        )
        maximum_norm = (
            transient_norm * float(maximum_auxiliary_to_transient_shared_norm)
        )
        if float(effective_norm.item()) > float(maximum_norm.item()):
            scale_tensor = maximum_norm / torch.clamp(effective_norm, min=epsilon)
            norm_scale = float(scale_tensor.item())
            effective_auxiliary = tuple(
                gradient * scale_tensor for gradient in effective_auxiliary
            )

    combined_shared = tuple(
        transient_gradient + auxiliary_gradient
        for transient_gradient, auxiliary_gradient in zip(
            transient_shared, effective_auxiliary, strict=True
        )
    )
    weighted_auxiliary_head = tuple(
        gradient * float(auxiliary_coefficient) for gradient in auxiliary_head
    )
    _validate_gradients(shared, combined_shared, "combined_shared")
    _validate_gradients(auxiliary, weighted_auxiliary_head, "weighted_auxiliary_head")
    _accumulate(shared, combined_shared, accumulation_steps)
    _accumulate(cycle, transient_cycle, accumulation_steps)
    _accumulate(auxiliary, weighted_auxiliary_head, accumulation_steps)

    effective_norm = torch.sqrt(
        torch.clamp(_squared_norm(effective_auxiliary), min=0.0)
    )
    dot_after = _dot(transient_shared, effective_auxiliary)
    return {
        "variant": variant,
        "projection_applied": projection_applied,
        "transient_shared_gradient_norm": float(transient_norm.item()),
        "raw_weighted_auxiliary_shared_gradient_norm": float(auxiliary_norm.item()),
        "effective_auxiliary_shared_gradient_norm": float(effective_norm.item()),
        "auxiliary_shared_norm_scale": norm_scale,
        "shared_gradient_cosine_before": float(cosine_before.item()),
        "shared_gradient_dot_after": float(dot_after.item()),
    }
