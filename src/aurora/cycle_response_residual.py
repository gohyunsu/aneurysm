"""Dataset-free building blocks for a cycle-response plus local-residual model.

The global branch predicts a positive response amplitude and coefficients in a
train-only complete-cycle basis. The local branch is supplied by an arbitrary
geometry backbone. Both branches are decoded in physical Cartesian units and
projected to the case-specific tangent plane. This module deliberately makes
no rank choice, performance gate or executable experiment decision.
"""

from __future__ import annotations

from typing import Any, Mapping

import torch
from torch import nn

from aurora.aneug_processed_v4_d9 import tangent_projection


class CycleResponseResidualError(RuntimeError):
    """Raised when a response basis or decoder input violates its contract."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise CycleResponseResidualError(label)


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.cycle_response_residual_prototype.v1",
        "config_schema",
    )
    _require(config.get("status") == "dataset_free_prototype", "status")
    representation = config["representation"]
    _require(
        representation["rank_grid"] == [16, 32, 64, 128, 256]
        and representation["rank_selected"] is False
        and representation["basis_source"]
        == "D13A_train_only_energy_normalized_complete_cycles",
        "representation",
    )
    branches = config["branches"]
    _require(
        branches["positive_amplitude"] == "centered_exponential"
        and branches["global_tangent_projection"] is True
        and branches["local_tangent_projection"] is True
        and branches["residual_basis_leakage"] == "reported_soft_penalty"
        and branches["hard_basis_projection"] is False,
        "branches",
    )
    evidence = config["evidence_boundary"]
    _require(
        evidence["absolute_performance_threshold"] is None
        and evidence["D12_terminal_required_before_selection"] is True
        and evidence["D13A_oracle_required_before_rank_or_execution"] is True
        and evidence["outer_or_auxiliary_access"] is False
        and evidence["paper_claim"] is False,
        "evidence_boundary",
    )
    _require(
        config["runtime_scope"]["server"] == "introai9"
        and config["runtime_scope"]["excluded_server"] == "junjinyong"
        and config["runtime_scope"]["execute_now"] is False,
        "runtime_scope",
    )


def _basis_contract(
    mean: torch.Tensor,
    basis: torch.Tensor,
    reference_weights: torch.Tensor,
    train_scales: torch.Tensor,
    phases: int,
    nodes: int,
    rank: int,
) -> None:
    dimension = phases * nodes * 3
    _require(phases > 1 and nodes > 2 and 0 < rank <= basis.shape[0], "shape")
    _require(mean.shape == (dimension,), "mean_shape")
    _require(basis.ndim == 2 and basis.shape[1] == dimension, "basis_shape")
    _require(reference_weights.shape == (nodes,), "weight_shape")
    _require(train_scales.ndim == 1 and train_scales.numel() >= 2, "scale_shape")
    tensors = (mean, basis[:rank], reference_weights, train_scales)
    _require(all(bool(torch.isfinite(value).all().item()) for value in tensors), "finite")
    _require(bool((reference_weights > 0).all().item()), "positive_weights")
    _require(bool((train_scales > 0).all().item()), "positive_scales")
    weight_sum = float(reference_weights.to(torch.float64).sum().item())
    _require(abs(weight_sum - 1.0) < 1e-5, "normalized_weights")
    gram = basis[:rank].to(torch.float64) @ basis[:rank].to(torch.float64).T
    identity = torch.eye(rank, dtype=torch.float64, device=gram.device)
    _require(float(torch.max(torch.abs(gram - identity)).item()) < 2e-3, "orthonormal_basis")


def _weighted_flatten(
    field: torch.Tensor, reference_weights: torch.Tensor
) -> torch.Tensor:
    phases, nodes, channels = field.shape
    _require(channels == 3 and reference_weights.shape == (nodes,), "field_shape")
    factor = torch.sqrt(reference_weights / phases).reshape(1, nodes, 1)
    return (field * factor).reshape(-1)


class CycleResponseResidualDecoder(nn.Module):
    """Decode complete-cycle basis coordinates and a tangent local residual."""

    def __init__(
        self,
        basis_payload: Mapping[str, Any],
        *,
        rank: int,
    ) -> None:
        super().__init__()
        _require(
            basis_payload.get("schema_version")
            == "aurora.aneug_processed_v4_d13a.private_basis.v1",
            "basis_schema",
        )
        phases = int(basis_payload["phases"])
        nodes = int(basis_payload["nodes"])
        mean = basis_payload["mean"].detach().to(torch.float32)
        basis = basis_payload["basis"].detach().to(torch.float32)
        weights = basis_payload["reference_weights"].detach().to(torch.float32)
        train_scales = basis_payload["train_scales"].detach().to(torch.float32)
        _basis_contract(mean, basis, weights, train_scales, phases, nodes, rank)
        self.rank = int(rank)
        self.phases = phases
        self.nodes = nodes
        self.register_buffer("response_mean", mean)
        # A contiguous prefix can still share the full rank-256 storage. Clone
        # the selected rows so low-rank experiments retain only their declared
        # basis memory on the GPU.
        self.register_buffer("response_basis", basis[:rank].contiguous().clone())
        self.register_buffer("reference_weights", weights)
        self.register_buffer("log_amplitude_center", torch.log(train_scales).mean())

    def _global_field(
        self,
        coefficients: torch.Tensor,
        log_amplitude_offset: torch.Tensor,
        normals: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        _require(coefficients.shape == (self.rank,), "coefficient_shape")
        _require(log_amplitude_offset.numel() == 1, "amplitude_shape")
        _require(normals.shape == (self.nodes, 3), "normal_shape")
        pattern = self.response_mean + self.response_basis.T @ coefficients
        pattern = pattern / torch.clamp(torch.linalg.vector_norm(pattern), min=1e-12)
        amplitude = torch.exp(
            torch.clamp(self.log_amplitude_center + log_amplitude_offset.reshape(()), -20, 20)
        )
        factor = torch.sqrt(self.reference_weights / self.phases).reshape(
            1, self.nodes, 1
        )
        global_field = pattern.reshape(self.phases, self.nodes, 3) * amplitude / factor
        global_field = tangent_projection(global_field, normals)
        tangent_amplitude = torch.linalg.vector_norm(
            _weighted_flatten(global_field, self.reference_weights)
        )
        global_field = global_field * amplitude / torch.clamp(tangent_amplitude, min=1e-12)
        return global_field, amplitude

    def forward(
        self,
        coefficients: torch.Tensor,
        log_amplitude_offset: torch.Tensor,
        raw_local_residual: torch.Tensor,
        residual_gate_logit: torch.Tensor,
        normals: torch.Tensor,
        *,
        response_only: bool = False,
    ) -> dict[str, torch.Tensor]:
        _require(
            raw_local_residual.shape == (self.phases, self.nodes, 3),
            "residual_shape",
        )
        _require(residual_gate_logit.numel() == 1, "gate_shape")
        global_field, amplitude = self._global_field(
            coefficients, log_amplitude_offset, normals
        )
        local_residual = tangent_projection(raw_local_residual, normals)
        weighted_residual = _weighted_flatten(local_residual, self.reference_weights)
        residual_energy = torch.sum(weighted_residual.square())
        basis_coordinates = self.response_basis @ weighted_residual
        leakage = torch.sum(basis_coordinates.square()) / torch.clamp(
            residual_energy, min=1e-12
        )
        gate = torch.zeros((), dtype=global_field.dtype, device=global_field.device)
        if not response_only:
            gate = torch.sigmoid(residual_gate_logit.reshape(()))
        field = tangent_projection(global_field + gate * local_residual, normals)
        return {
            "field": field,
            "global_field": global_field,
            "local_residual": local_residual,
            "coefficients": coefficients,
            "amplitude": amplitude,
            "residual_gate": gate,
            "residual_basis_leakage": leakage,
        }


class GHDConditionedCycleResponseResidual(nn.Module):
    """Attach a response head to a complete-cycle local geometry backbone."""

    def __init__(
        self,
        local_backbone: nn.Module,
        basis_payload: Mapping[str, Any],
        *,
        rank: int,
        width: int = 256,
    ) -> None:
        super().__init__()
        _require(width > 0, "width")
        self.local_backbone = local_backbone
        self.decoder = CycleResponseResidualDecoder(basis_payload, rank=rank)
        self.response_head = nn.Sequential(
            nn.LayerNorm(432),
            nn.Linear(432, width),
            nn.SiLU(),
            nn.Linear(width, width),
            nn.SiLU(),
            nn.Linear(width, rank + 2),
        )
        final = self.response_head[-1]
        _require(isinstance(final, nn.Linear), "head")
        nn.init.zeros_(final.weight)
        nn.init.zeros_(final.bias)
        with torch.no_grad():
            final.bias[-1] = -2.0

    def forward(
        self, case: Mapping[str, torch.Tensor], *, response_only: bool = False
    ) -> dict[str, torch.Tensor]:
        _require("ghd" in case and "normals" in case, "case_features")
        token = case["ghd"].reshape(-1)
        _require(token.shape == (432,), "ghd_shape")
        response = self.response_head(token)
        coefficients = response[: self.decoder.rank]
        log_amplitude_offset = response[self.decoder.rank : self.decoder.rank + 1]
        residual_gate_logit = response[self.decoder.rank + 1 :]
        local = self.local_backbone(case)
        _require("field" in local, "backbone_output")
        decoded = self.decoder(
            coefficients,
            log_amplitude_offset,
            local["field"],
            residual_gate_logit,
            case["normals"],
            response_only=response_only,
        )
        decoded["raw_local_backbone_field"] = local["field"]
        return decoded


def weighted_global_amplitude(
    field: torch.Tensor, reference_weights: torch.Tensor
) -> float:
    """Return the decoder's phase/area weighted field amplitude for audits."""

    value = torch.linalg.vector_norm(_weighted_flatten(field, reference_weights))
    _require(bool(torch.isfinite(value).item()), "amplitude_finite")
    return float(value.item())
