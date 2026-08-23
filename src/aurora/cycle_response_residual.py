"""Dataset-free building blocks for a cycle-response plus local-residual model.

The global branch predicts a positive response amplitude and coefficients in a
train-only complete-cycle basis. The local branch is supplied by an arbitrary
geometry backbone. Both branches are decoded in the same raw physical
Cartesian coordinates as the release-730 oracle and common evaluator. This
module deliberately makes no rank choice, performance gate or executable
experiment decision.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

import torch
from torch import nn

from aurora.aneug_release_730_single_field_auxiliary import (
    SharedEncoderSingleFieldHead,
)


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
        == "release730_train_only_energy_normalized_complete_cycles",
        "representation",
    )
    branches = config["branches"]
    _require(
        branches["positive_amplitude"] == "centered_exponential"
        and branches["global_tangent_projection"] is False
        and branches["local_tangent_projection"] is False
        and branches["local_backbone_output_space"]
        == "explicit_positive_scale_to_raw_physical_cartesian"
        and branches["residual_basis_leakage"] == "reported_soft_penalty"
        and branches["hard_basis_projection"] is False,
        "branches",
    )
    shared_encoder = config["shared_encoder_contract"]
    _require(
        shared_encoder["active_candidate"]
        == "SharedEncoderCycleResponseResidual"
        and shared_encoder["one_geometry_encoder_pass_per_cycle_case"] is True
        and shared_encoder["global_token"]
        == "area_weighted_pool_of_GHD_conditioned_node_features"
        and shared_encoder["local_decoder_input"]
        == "the_same_GHD_conditioned_node_features"
        and shared_encoder["separate_GHD_only_global_encoder"] is False
        and shared_encoder["common_single_field_head_for_T_plus_M_and_T_plus_S"]
        is True,
        "shared_encoder_contract",
    )
    evidence = config["evidence_boundary"]
    _require(
        evidence["absolute_performance_threshold"] is None
        and evidence["release730_graph_unet_terminal_required_before_selection"]
        is True
        and evidence["release730_response_oracle_required_before_rank_or_execution"]
        is True
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
    _require(
        all(bool(torch.isfinite(value).all().item()) for value in tensors),
        "finite",
    )
    _require(bool((reference_weights > 0).all().item()), "positive_weights")
    _require(bool((train_scales > 0).all().item()), "positive_scales")
    weight_sum = float(reference_weights.to(torch.float64).sum().item())
    _require(abs(weight_sum - 1.0) < 1e-5, "normalized_weights")
    gram = basis[:rank].to(torch.float64) @ basis[:rank].to(torch.float64).T
    identity = torch.eye(rank, dtype=torch.float64, device=gram.device)
    _require(
        float(torch.max(torch.abs(gram - identity)).item()) < 2e-3,
        "orthonormal_basis",
    )


def _weighted_flatten(
    field: torch.Tensor, reference_weights: torch.Tensor
) -> torch.Tensor:
    phases, nodes, channels = field.shape
    _require(channels == 3 and reference_weights.shape == (nodes,), "field_shape")
    factor = torch.sqrt(reference_weights / phases).reshape(1, nodes, 1)
    return (field * factor).reshape(-1)


def _basis_leakage(
    field: torch.Tensor,
    basis: torch.Tensor,
    reference_weights: torch.Tensor,
) -> torch.Tensor:
    weighted = _weighted_flatten(field, reference_weights)
    energy = torch.sum(weighted.square())
    coordinates = basis @ weighted
    return torch.sum(coordinates.square()) / torch.clamp(energy, min=1e-12)


def _backbone_field(output: Any) -> torch.Tensor:
    """Normalize the two registered comparator output contracts."""

    if isinstance(output, torch.Tensor):
        field = output
    elif isinstance(output, Mapping):
        _require("field" in output, "backbone_output")
        field = output["field"]
    else:
        raise CycleResponseResidualError("backbone_output")
    _require(isinstance(field, torch.Tensor), "backbone_field")
    return field


class CycleResponseResidualDecoder(nn.Module):
    """Decode complete-cycle basis coordinates and a raw Cartesian residual."""

    def __init__(
        self,
        basis_payload: Mapping[str, Any],
        *,
        rank: int,
    ) -> None:
        super().__init__()
        _require(
            basis_payload.get("schema_version")
            == "aurora.private.aneug_release_730_response_basis.v1",
            "basis_schema",
        )
        _require(
            basis_payload.get("protocol_id")
            == "aneug_release_730_response_oracle_v1"
            and basis_payload.get("train_cases") == 584
            and basis_payload.get("case_ids_included") is False,
            "basis_scope",
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
        amplitude = torch.exp(
            torch.clamp(
                self.log_amplitude_center + log_amplitude_offset.reshape(()),
                -20,
                20,
            )
        )
        factor = torch.sqrt(self.reference_weights / self.phases).reshape(
            1, self.nodes, 1
        )
        global_field = pattern.reshape(self.phases, self.nodes, 3) * amplitude / factor
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
        local_residual = raw_local_residual
        leakage = _basis_leakage(
            local_residual, self.response_basis, self.reference_weights
        )
        gate = torch.zeros((), dtype=global_field.dtype, device=global_field.device)
        if not response_only:
            gate = torch.sigmoid(residual_gate_logit.reshape(()))
        field = global_field + gate * local_residual
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
    """Historical separate-encoder prototype retained for provenance tests."""

    def __init__(
        self,
        local_backbone: nn.Module | None,
        basis_payload: Mapping[str, Any],
        *,
        rank: int,
        local_output_scale: float,
        width: int = 256,
    ) -> None:
        super().__init__()
        _require(width > 0, "width")
        _require(
            math.isfinite(float(local_output_scale))
            and float(local_output_scale) > 0.0,
            "local_output_scale",
        )
        self.local_backbone = local_backbone
        self.decoder = CycleResponseResidualDecoder(basis_payload, rank=rank)
        self.register_buffer(
            "local_output_scale",
            torch.tensor(float(local_output_scale), dtype=torch.float32),
        )
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
        self,
        case: Mapping[str, torch.Tensor],
        *,
        variant: str = "response_plus_residual",
    ) -> dict[str, torch.Tensor]:
        _require("ghd" in case and "normals" in case, "case_features")
        _require(
            variant in {"response_only", "local_only", "response_plus_residual"},
            "variant",
        )
        normals = case["normals"]
        if variant == "local_only":
            _require(self.local_backbone is not None, "local_backbone")
            field = _backbone_field(self.local_backbone(case))
            field = field * self.local_output_scale
            zero = field.new_zeros(())
            leakage = _basis_leakage(
                field,
                self.decoder.response_basis,
                self.decoder.reference_weights,
            )
            return {
                "field": field,
                "global_field": torch.zeros_like(field),
                "local_residual": field,
                "physical_local_backbone_field": field,
                "coefficients": field.new_zeros(self.decoder.rank),
                "amplitude": zero,
                "residual_gate": field.new_ones(()),
                "residual_basis_leakage": leakage,
            }

        token = case["ghd"].reshape(-1)
        _require(token.shape == (432,), "ghd_shape")
        response = self.response_head(token)
        coefficients = response[: self.decoder.rank]
        log_amplitude_offset = response[self.decoder.rank : self.decoder.rank + 1]
        residual_gate_logit = response[self.decoder.rank + 1 :]
        if variant == "response_only":
            local_field = normals.new_zeros(
                (self.decoder.phases, self.decoder.nodes, 3)
            )
        else:
            _require(self.local_backbone is not None, "local_backbone")
            local_field = _backbone_field(self.local_backbone(case))
            local_field = local_field * self.local_output_scale
        decoded = self.decoder(
            coefficients,
            log_amplitude_offset,
            local_field,
            residual_gate_logit,
            normals,
            response_only=variant == "response_only",
        )
        decoded["physical_local_backbone_field"] = local_field
        return decoded


class SharedEncoderCycleResponseResidual(nn.Module):
    """Decode global response and local residual from one geometry encoding.

    The response token is an area-weighted pooling of the same GHD-conditioned
    per-node features consumed by the local cycle decoder.  Consequently, the
    response-only, local-only and combined variants change only their decoder
    branch, rather than changing the geometry information or encoder family.
    The optional single-field path reuses this encoder and the exact common
    auxiliary-head class used by matched T+M and T+S controls.
    """

    def __init__(
        self,
        backbone: nn.Module,
        basis_payload: Mapping[str, Any],
        *,
        rank: int,
        local_output_scale: float,
    ) -> None:
        super().__init__()
        _require(callable(getattr(backbone, "encode_geometry", None)), "encoder")
        _require(callable(getattr(backbone, "decode_cycle", None)), "cycle_decoder")
        encoded_width = int(getattr(backbone, "encoded_width", 0))
        _require(encoded_width > 0, "encoded_width")
        _require(
            math.isfinite(float(local_output_scale))
            and float(local_output_scale) > 0.0,
            "local_output_scale",
        )
        self.backbone = backbone
        self.encoded_width = encoded_width
        self.decoder = CycleResponseResidualDecoder(basis_payload, rank=rank)
        self.register_buffer(
            "local_output_scale",
            torch.tensor(float(local_output_scale), dtype=torch.float32),
        )
        self.response_head = nn.Sequential(
            nn.LayerNorm(encoded_width),
            nn.Linear(encoded_width, encoded_width),
            nn.SiLU(),
            nn.Linear(encoded_width, rank + 2),
        )
        self.single_field_head = SharedEncoderSingleFieldHead(encoded_width)
        final = self.response_head[-1]
        _require(isinstance(final, nn.Linear), "head")
        nn.init.zeros_(final.weight)
        nn.init.zeros_(final.bias)
        with torch.no_grad():
            final.bias[-1] = -2.0

    def _encode_and_pool(
        self, case: Mapping[str, torch.Tensor]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        _require("vertex_weights" in case and "normals" in case, "case_features")
        features = self.backbone.encode_geometry(case)
        _require(
            features.ndim == 2
            and features.shape[0] == self.decoder.nodes
            and features.shape[1] == self.encoded_width,
            "encoded_features",
        )
        weights = case["vertex_weights"]
        normals = case["normals"]
        _require(
            weights.shape == (self.decoder.nodes,)
            and bool(torch.isfinite(weights).all().item())
            and bool((weights > 0).all().item()),
            "vertex_weights",
        )
        _require(
            normals.shape == (self.decoder.nodes, 3)
            and bool(torch.isfinite(normals).all().item()),
            "normals",
        )
        normalized = weights / torch.clamp(weights.sum(), min=1e-12)
        pooled = torch.sum(features * normalized.unsqueeze(-1), dim=0)
        return features, pooled

    def _local_field(self, features: torch.Tensor) -> torch.Tensor:
        field = _backbone_field(self.backbone.decode_cycle(features))
        _require(
            field.shape == (self.decoder.phases, self.decoder.nodes, 3),
            "local_field_shape",
        )
        return field * self.local_output_scale

    def forward(
        self,
        case: Mapping[str, torch.Tensor],
        *,
        variant: str = "response_plus_residual",
    ) -> dict[str, torch.Tensor]:
        _require(
            variant in {"response_only", "local_only", "response_plus_residual"},
            "variant",
        )
        features, pooled = self._encode_and_pool(case)
        normals = case["normals"]

        if variant == "local_only":
            field = self._local_field(features)
            zero = field.new_zeros(())
            leakage = _basis_leakage(
                field,
                self.decoder.response_basis,
                self.decoder.reference_weights,
            )
            return {
                "field": field,
                "global_field": torch.zeros_like(field),
                "local_residual": field,
                "physical_local_backbone_field": field,
                "coefficients": field.new_zeros(self.decoder.rank),
                "amplitude": zero,
                "residual_gate": field.new_ones(()),
                "residual_basis_leakage": leakage,
            }

        response = self.response_head(pooled)
        coefficients = response[: self.decoder.rank]
        log_amplitude_offset = response[self.decoder.rank : self.decoder.rank + 1]
        residual_gate_logit = response[self.decoder.rank + 1 :]
        if variant == "response_only":
            local_field = normals.new_zeros(
                (self.decoder.phases, self.decoder.nodes, 3)
            )
        else:
            local_field = self._local_field(features)
        decoded = self.decoder(
            coefficients,
            log_amplitude_offset,
            local_field,
            residual_gate_logit,
            normals,
            response_only=variant == "response_only",
        )
        decoded["physical_local_backbone_field"] = local_field
        return decoded

    def forward_single_field(
        self, case: Mapping[str, torch.Tensor]
    ) -> torch.Tensor:
        """Predict one normalized vector field for a matched T+M/T+S row."""

        features, _ = self._encode_and_pool(case)
        return self.single_field_head(features)


def weighted_global_amplitude(
    field: torch.Tensor, reference_weights: torch.Tensor
) -> float:
    """Return the decoder's phase/area weighted field amplitude for audits."""

    value = torch.linalg.vector_norm(_weighted_flatten(field, reference_weights))
    _require(bool(torch.isfinite(value).item()), "amplitude_finite")
    return float(value.item())
