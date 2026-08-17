"""Bounded D9 mesh-canonicalized transient-WSS development pilot.

The executable reads only the frozen D5 train and validation components.  It
derives normals from coordinates and faces, projects the physical WSS target
to the tangent plane, and compares two readouts on one shared scalar-vector
mesh backbone.  D9 is single-seed validation development, not paper evidence.
All numeric outputs and checkpoints are private server artifacts.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
import random
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from aurora.aneug_cycle_functional_p0 import safe_torch_load
from aurora.aneug_processed_v4_d6 import (
    area_weighted_vertex_normals,
    decode_release_channels,
    load_contract as load_d6_registration,
    validate_private_split_manifest,
)
from aurora.cycle_moment_projection import (
    jensen_cone_mean_magnitude,
    project_cycle_moments,
)


class D9PilotError(RuntimeError):
    """Raised when a registered D9 boundary or invariant is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise D9PilotError(reason)


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def validate_contract(contract: Mapping[str, Any]) -> None:
    _require(
        contract.get("schema_version")
        == "aurora.aneug_processed_v4_d9_mesh_canonicalized_pilot.v1",
        "schema_version",
    )
    _require(
        contract.get("protocol_id")
        == "aneug_processed_v4_mesh_canonicalized_validation_pilot_d9_v1",
        "protocol_id",
    )
    _require(contract.get("status") == "human_selected_executable_bounded_development", "status")
    activation = contract["human_activation"]
    _require(activation["explicitly_selected"] is True and activation["selection"] == "D9", "human_selection")
    _require(activation["fresh_after_closed_d8_pass"] is True, "fresh_after_d8")
    _require(activation["does_not_repair_resume_rerun_reopen_or_relabel_d8"] is True, "d8_immutability")
    _require(activation["old_d7_conditional_gpu_template_remains_inactive"] is True, "old_template")

    role = contract["scientific_role"]
    _require(role["development_not_confirmation"] is True, "development_role")
    for key in (
        "single_seed_is_paper_evidence",
        "architecture_name_is_novelty",
        "deterministic_mesh_normal_and_tangent_projection_are_novelty",
        "broad_field_function_mismatch_is_novelty",
    ):
        _require(role[key] is False, f"scientific_role_{key}")

    bound = contract["bound_upstream"]
    _require(bound["d8_status"] == "closed_pass_1_of_1" and bound["d8_pass_required"] is True, "d8_pass")
    _require(bound["d8_private_result_sha256"] == "b9431fb31570a5db41fd5a968251c1f7676ba5420f50fa1d9ea01407f3b38e9c", "d8_result")
    _require(bound["d5_private_manifest_sha256"] == "0f95cf303fa63b58c049e722864389c1432460686e335d20402b677c368181d6", "d5_manifest")
    _require(bound["d5_train_split_sha256"] == "df583f3553ce4efcf0588da5bdc029921025648c1981eba3a85fe3841d2bf26e", "d5_train")

    expected_sources = {
        "transient": (23_744_862_051, "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9"),
        "steady": (9_632_510_050, "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f"),
    }
    for name, (size, digest) in expected_sources.items():
        item = contract["source_identity"][name]
        _require(item["bytes"] == size and item["sha256"] == digest, f"{name}_identity")
    _require(contract["source_identity"]["physical_decoder_epsilon"] == 1e-5, "decoder_epsilon")

    boundary = contract["immutable_data_boundary"]
    _require(
        (
            boundary["train_components"], boundary["validation_components"],
            boundary["outer_components"], boundary["auxiliary_cases"],
            boundary["timesteps"], boundary["nodes"], boundary["channels"],
        ) == (406, 51, 51, 70, 80, 13_902, 9),
        "data_counts",
    )
    _require(boundary["validation_only_development"] is True, "validation_role")
    for key in ("outer_tensor_values_read", "auxiliary_tensor_values_read", "split_or_unit_change_allowed", "case_identifiers_in_outputs"):
        _require(boundary[key] is False, f"boundary_{key}")

    target = contract["canonical_target"]
    _require(target["stored_normal_channels_used_by_model_or_loss"] is False, "stored_normal_exclusion")
    _require(target["surface_normal"] == "area_weighted_unit_normal_from_physical_coordinates_and_shared_finest_faces", "mesh_normal")
    _require(target["prediction_tangency"] == "deterministic_orthogonal_projection", "prediction_tangency")
    _require(target["uniform_80_phase_quadrature"] is True, "phase_quadrature")

    basis = contract["train_only_temporal_basis"]
    _require((basis["covariance_dimension"], basis["minimum_rank"], basis["maximum_rank"]) == (80, 8, 32), "basis_rank")
    _require(basis["minimum_retained_energy"] == 0.995, "basis_energy")
    _require(basis["validation_cannot_select_rank"] is True and basis["basis_columns_zero_temporal_mean"] is True, "basis_scope")

    models = contract["registered_models"]
    _require(models["shared_backbone"] == "three_level_scalar_vector_mesh_message_operator", "backbone")
    _require(models["strict_SE3_claim"] is False, "se3_claim")
    _require((models["hidden_scalar_channels"], models["hidden_vector_channels"]) == (64, 16), "hidden_width")
    _require(models["ghd_input_dimensions"] == 432 and models["ghd_embedding_dimensions"] == 32, "ghd_width")
    _require(models["message_blocks_per_level"] == [2, 2, 2, 1, 1], "block_schedule")
    _require(models["moment_pod"]["projection_uses_predicted_not_reference_moments"] is True, "projection_leakage")
    _require(models["same_geometry_information_and_backbone"] is True, "matched_backbone")

    optimization = contract["optimization"]
    _require((optimization["seed"], optimization["maximum_epochs"], optimization["minimum_epochs"], optimization["early_stopping_patience"]) == (1103, 20, 8, 4), "optimization_budget")
    _require((optimization["batch_cases"], optimization["gradient_accumulation_cases"]) == (1, 4), "batching")
    _require(optimization["checkpoint_selection"] == "lowest_validation_field_relative_L2_then_earliest_epoch", "selection_metric")

    screen = contract["development_screen"]
    _require(screen["all_required"] is True and screen["screen_pass_is_paper_result"] is False, "screen_role")
    _require((screen["maximum_direct_validation_field_relative_L2"], screen["maximum_moment_over_direct_field_error_ratio"]) == (0.35, 1.05), "field_screen")
    _require((screen["maximum_moment_over_direct_TAWSS_error_ratio"], screen["maximum_moment_over_direct_OSI_error_ratio"], screen["minimum_validation_OSI_coverage"]) == (0.98, 0.98, 0.99), "functional_screen")

    jobs = contract["job_budget"]
    _require(jobs["server"] == "introai9" and jobs["excluded_server"] == "junjinyong", "server")
    _require(jobs["scheduler"] == "PBS" and jobs["queue"] == "coss_agpu", "scheduler")
    _require((jobs["gpu_per_job"], jobs["maximum_concurrent_jobs"], jobs["maximum_accepted_jobs"], jobs["maximum_total_requested_GPU_hours"]) == (1, 1, 3, 28), "job_budget")
    _require(jobs["same_stage_rerun_repair_or_relabel"] is False, "rerun")
    _require(jobs["R1_requires_R0_complete_pass"] is True, "stage_order")
    _require(jobs["login_node_gpu_allowed"] is False, "login_gpu")
    _require(all(int(item["maximum_attempts"]) == 1 and int(item["ngpus"]) == 1 for item in jobs["jobs"].values()), "attempts")

    outputs = contract["outputs"]
    _require(outputs["cache_is_private_and_not_committed"] is True and outputs["all_numeric_results_private"] is True, "result_privacy")
    _require(outputs["atomic_JSON_and_checkpoint"] is True and outputs["refuse_existing_stage_output"] is True, "output_safety")
    _require(outputs["static_site_update_required"] is False, "site_scope")
    authorization = contract["authorization"]
    for key in ("execute_D9_R0_and_conditional_R1", "read_train_and_validation_tensor_values", "fit_and_select_registered_models_on_validation", "use_one_GPU_per_registered_job"):
        _require(authorization[key] is True, f"authorization_{key}")
    for key in ("read_outer_or_auxiliary_tensor_values", "multi_seed_confirmation", "outer_test", "paper_result_figure_or_claim", "publish_numeric_result", "maintain_public_site"):
        _require(authorization[key] is False, f"authorization_{key}")


def load_contract(path: str | Path) -> dict[str, Any]:
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(contract)
    return contract


def validate_private_activation(path: str | Path, contract: Mapping[str, Any], expected_commit: str, stage: str) -> dict[str, Any]:
    activation_path = Path(path)
    _require(activation_path.is_file(), "missing_private_activation")
    activation = json.loads(activation_path.read_text(encoding="utf-8"))
    _require(activation.get("schema_version") == "aurora.aneug_processed_v4_d9.private_activation.v1", "activation_schema")
    _require(activation.get("protocol_id") == contract["protocol_id"], "activation_protocol")
    _require(activation.get("public_commit") == expected_commit, "activation_commit")
    _require(activation.get("quality_conclusion") == "success", "activation_quality")
    _require(activation.get("d8_private_result_sha256") == contract["bound_upstream"]["d8_private_result_sha256"], "activation_d8")
    _require(stage in activation.get("authorized_stages", []), "activation_stage")
    _require(activation.get("outer_or_auxiliary_access") is False, "activation_scope")
    return activation


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), f"output_exists:{target.name}")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _strict_atomic_torch_save(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), f"output_exists:{target.name}")
    try:
        torch.save(payload, temporary)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def _verify_exact_file(path: str | Path, identity: Mapping[str, Any], label: str) -> None:
    source = Path(path)
    _require(source.is_file(), f"missing_{label}")
    _require(source.stat().st_size == int(identity["bytes"]), f"{label}_size")
    _require(file_sha256(source) == identity["sha256"], f"{label}_sha256")


def tangent_projection(field: torch.Tensor, normals: torch.Tensor) -> torch.Tensor:
    """Orthogonally project ``[...,N,3]`` vectors using ``[N,3]`` normals."""

    _require(normals.shape == field.shape or field.shape[-2:] == normals.shape, "tangent_projection_shape")
    return field - torch.sum(field * normals, dim=-1, keepdim=True) * normals


def triangle_lumped_vertex_weights(coordinates: torch.Tensor, faces: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    normals, twice_area = area_weighted_vertex_normals(coordinates, faces, torch)
    weights = torch.zeros(coordinates.shape[0], dtype=coordinates.dtype, device=coordinates.device)
    contribution = twice_area / 6.0
    for corner in range(3):
        weights.index_add_(0, faces[:, corner].to(dtype=torch.int64), contribution)
    _require(bool((weights > 0).all().item()) and bool(torch.isfinite(weights).all().item()), "vertex_area")
    weights = weights / weights.sum()
    return normals, weights


def canonicalize_case(
    normalized: torch.Tensor,
    mean: torch.Tensor,
    std: torch.Tensor,
    faces: torch.Tensor,
    *,
    wss_scale: float | None = None,
) -> dict[str, torch.Tensor]:
    """Decode one release case without ever consuming stored normal channels."""

    _require(list(normalized.shape[-2:]) == [13_902, 9] or normalized.shape[-1] == 9, "case_shape")
    physical = decode_release_channels(normalized.to(dtype=torch.float32), mean, std, torch, epsilon=1e-5)
    coordinates = physical[0, :, :3]
    center = coordinates.mean(dim=0, keepdim=True)
    centered = coordinates - center
    rms = torch.sqrt(torch.mean(torch.sum(centered * centered, dim=-1)))
    _require(bool(torch.isfinite(rms).item()) and float(rms.item()) > 0.0, "coordinate_scale")
    coordinates_normalized = centered / rms
    normals, weights = triangle_lumped_vertex_weights(coordinates, faces)
    _require(bool((torch.linalg.vector_norm(normals, dim=-1) > 0.999).all().item()), "mesh_normal_coverage")
    tangent_wss = tangent_projection(physical[..., 6:9], normals)
    if wss_scale is not None:
        _require(math.isfinite(wss_scale) and wss_scale > 0.0, "wss_scale")
        tangent_wss = tangent_wss / float(wss_scale)
    return {
        "coordinates": coordinates_normalized.contiguous(),
        "normals": normals.contiguous(),
        "vertex_weights": weights.contiguous(),
        "wss": tangent_wss.contiguous(),
    }


def choose_temporal_basis(covariance: torch.Tensor, minimum_rank: int = 8, maximum_rank: int = 32, retained_energy: float = 0.995) -> dict[str, Any]:
    _require(tuple(covariance.shape) == (80, 80), "covariance_shape")
    symmetric = 0.5 * (covariance.to(dtype=torch.float64) + covariance.to(dtype=torch.float64).T)
    centering = torch.eye(80, dtype=torch.float64) - torch.ones((80, 80), dtype=torch.float64) / 80.0
    symmetric = centering @ symmetric @ centering
    values, vectors = torch.linalg.eigh(symmetric)
    order = torch.argsort(values, descending=True)
    values = torch.clamp(values[order], min=0.0)
    vectors = vectors[:, order]
    total = values.sum()
    _require(bool(torch.isfinite(total).item()) and float(total.item()) > 0.0, "covariance_energy")
    cumulative = torch.cumsum(values, dim=0) / total
    reaching = torch.nonzero(cumulative >= retained_energy).reshape(-1)
    raw_rank = int(reaching[0].item()) + 1 if int(reaching.numel()) else maximum_rank
    rank = min(maximum_rank, max(minimum_rank, raw_rank))
    basis = vectors[:, :rank]
    basis = basis - basis.mean(dim=0, keepdim=True)
    basis, _ = torch.linalg.qr(basis, mode="reduced")
    retained = float(values[:rank].sum().div(total).item())
    return {"basis": basis.to(dtype=torch.float32), "rank": rank, "retained_energy": retained}


def symmetrize_edges(edge_index: torch.Tensor, node_count: int) -> torch.Tensor:
    edge = edge_index.to(dtype=torch.int64, device="cpu")
    if edge.ndim == 2 and edge.shape[1] == 2:
        edge = edge.T
    _require(edge.ndim == 2 and int(edge.shape[0]) == 2, "edge_shape")
    _require(int(edge.min().item()) >= 0 and int(edge.max().item()) < node_count, "edge_range")
    reverse = edge.flip(0)
    combined = torch.cat((edge, reverse), dim=1)
    keys = combined[0] * node_count + combined[1]
    order = torch.argsort(keys)
    combined = combined[:, order]
    keep = torch.ones(combined.shape[1], dtype=torch.bool)
    keep[1:] = keys[order][1:] != keys[order][:-1]
    return combined[:, keep].contiguous()


def graph_parent_assignment(edge_index: torch.Tensor, coarse_indices: torch.Tensor, node_count: int) -> torch.Tensor:
    """Assign each node to the nearest selected coarse node by graph hops."""

    edge = symmetrize_edges(edge_index, node_count)
    coarse = coarse_indices.to(dtype=torch.int64, device="cpu").reshape(-1)
    _require(len(set(int(value) for value in coarse.tolist())) == int(coarse.numel()), "coarse_unique")
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for source, target in edge.T.tolist():
        adjacency[int(source)].append(int(target))
    parent = torch.full((node_count,), -1, dtype=torch.int64)
    queue: collections.deque[int] = collections.deque()
    for parent_index, node in enumerate(coarse.tolist()):
        _require(0 <= int(node) < node_count, "coarse_range")
        parent[int(node)] = int(parent_index)
        queue.append(int(node))
    while queue:
        node = queue.popleft()
        for neighbor in adjacency[node]:
            if int(parent[neighbor].item()) < 0:
                parent[neighbor] = parent[node]
                queue.append(neighbor)
    _require(bool((parent >= 0).all().item()), "disconnected_hierarchy")
    return parent


class VectorLinear(nn.Module):
    def __init__(self, input_channels: int, output_channels: int) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.empty(output_channels, input_channels))
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))

    def forward(self, vectors: torch.Tensor) -> torch.Tensor:
        return torch.einsum("nvc,ov->noc", vectors, self.weight)


class ScalarVectorMessageBlock(nn.Module):
    def __init__(self, scalar_channels: int, vector_channels: int) -> None:
        super().__init__()
        width = scalar_channels
        self.message = nn.Sequential(
            nn.Linear(2 * scalar_channels + 1, width), nn.SiLU(),
            nn.Linear(width, scalar_channels + 2 * vector_channels),
        )
        self.vector_message = VectorLinear(vector_channels, vector_channels)
        self.scalar_update = nn.Sequential(
            nn.Linear(2 * scalar_channels + vector_channels, width), nn.SiLU(), nn.Linear(width, scalar_channels)
        )
        self.scalar_norm = nn.LayerNorm(scalar_channels)
        self.vector_update = VectorLinear(vector_channels, vector_channels)
        self.vector_gate = nn.Linear(scalar_channels, vector_channels)

    def forward(self, scalar: torch.Tensor, vector: torch.Tensor, positions: torch.Tensor, edge_index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        source, target = edge_index
        displacement = positions[source] - positions[target]
        distance = torch.linalg.vector_norm(displacement, dim=-1, keepdim=True)
        direction = displacement / torch.clamp(distance, min=1e-8)
        message = self.message(torch.cat((scalar[source], scalar[target], distance), dim=-1))
        scalar_message, vector_gate, direction_gate = torch.split(
            message, [scalar.shape[-1], vector.shape[1], vector.shape[1]], dim=-1
        )
        vector_message = (
            torch.tanh(vector_gate).unsqueeze(-1) * self.vector_message(vector[source])
            + torch.tanh(direction_gate).unsqueeze(-1) * direction.unsqueeze(1)
        )
        node_count = int(scalar.shape[0])
        counts = torch.bincount(target, minlength=node_count).to(dtype=scalar.dtype).clamp(min=1).unsqueeze(-1)
        aggregate_scalar = torch.zeros_like(scalar).index_add_(0, target, scalar_message) / counts
        aggregate_vector = torch.zeros_like(vector).index_add_(0, target, vector_message) / counts.unsqueeze(-1)
        invariant_norm = torch.linalg.vector_norm(aggregate_vector, dim=-1)
        updated_scalar = self.scalar_norm(
            scalar + self.scalar_update(torch.cat((scalar, aggregate_scalar, invariant_norm), dim=-1))
        )
        gate = torch.sigmoid(self.vector_gate(updated_scalar)).unsqueeze(-1)
        updated_vector = vector + gate * self.vector_update(aggregate_vector)
        return updated_scalar, updated_vector


class MeshCanonicalizedPilot(nn.Module):
    """Three-level scalar-vector mesh operator with one registered readout."""

    def __init__(
        self,
        topology: Mapping[str, torch.Tensor],
        *,
        variant: str,
        temporal_basis: torch.Tensor | None = None,
        scalar_channels: int = 64,
        vector_channels: int = 16,
    ) -> None:
        super().__init__()
        _require(variant in {"direct_cycle", "moment_pod"}, "variant")
        if variant == "moment_pod":
            _require(temporal_basis is not None and temporal_basis.ndim == 2 and temporal_basis.shape[0] == 80, "temporal_basis")
        self.variant = variant
        for name in ("edge0", "edge1", "edge2", "idx1", "idx2", "parent1", "parent2"):
            self.register_buffer(name, topology[name].to(dtype=torch.int64))
        basis = torch.empty((80, 0), dtype=torch.float32) if temporal_basis is None else temporal_basis.to(dtype=torch.float32)
        self.register_buffer("temporal_basis", basis)
        self.ghd_embedding = nn.Sequential(nn.Linear(432, 64), nn.SiLU(), nn.Linear(64, 32))
        self.scalar_input = nn.Sequential(nn.Linear(35, scalar_channels), nn.SiLU(), nn.Linear(scalar_channels, scalar_channels))
        self.vector_input = VectorLinear(2, vector_channels)
        counts = [2, 2, 2, 1, 1]
        self.fine_encoder = nn.ModuleList([ScalarVectorMessageBlock(scalar_channels, vector_channels) for _ in range(counts[0])])
        self.middle_encoder = nn.ModuleList([ScalarVectorMessageBlock(scalar_channels, vector_channels) for _ in range(counts[1])])
        self.coarse_encoder = nn.ModuleList([ScalarVectorMessageBlock(scalar_channels, vector_channels) for _ in range(counts[2])])
        self.middle_decoder = nn.ModuleList([ScalarVectorMessageBlock(scalar_channels, vector_channels) for _ in range(counts[3])])
        self.fine_decoder = nn.ModuleList([ScalarVectorMessageBlock(scalar_channels, vector_channels) for _ in range(counts[4])])
        self.scalar_up2 = nn.Linear(scalar_channels, scalar_channels)
        self.scalar_up1 = nn.Linear(scalar_channels, scalar_channels)
        self.vector_up2 = VectorLinear(vector_channels, vector_channels)
        self.vector_up1 = VectorLinear(vector_channels, vector_channels)
        output_vectors = 80 if variant == "direct_cycle" else 1 + int(basis.shape[1])
        self.vector_output = VectorLinear(vector_channels, output_vectors)
        self.cone_output = nn.Linear(scalar_channels, 1) if variant == "moment_pod" else None

    def _blocks(self, blocks: nn.ModuleList, scalar: torch.Tensor, vector: torch.Tensor, positions: torch.Tensor, edges: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        for block in blocks:
            scalar, vector = block(scalar, vector, positions, edges)
        return scalar, vector

    def forward(self, case: Mapping[str, torch.Tensor], *, exact_moment_projection: bool = False) -> dict[str, torch.Tensor]:
        positions = case["coordinates"]
        normals = case["normals"]
        weights = case["vertex_weights"]
        ghd = case["ghd"]
        embedding = self.ghd_embedding(ghd.reshape(1, -1)).expand(positions.shape[0], -1)
        local = torch.cat((torch.linalg.vector_norm(positions, dim=-1, keepdim=True), weights.unsqueeze(-1), torch.ones_like(weights.unsqueeze(-1)), embedding), dim=-1)
        scalar0 = self.scalar_input(local)
        vector0 = self.vector_input(torch.stack((positions, normals), dim=1))
        scalar0, vector0 = self._blocks(self.fine_encoder, scalar0, vector0, positions, self.edge0)
        positions1 = positions[self.idx1]
        scalar1, vector1 = scalar0[self.idx1], vector0[self.idx1]
        scalar1, vector1 = self._blocks(self.middle_encoder, scalar1, vector1, positions1, self.edge1)
        positions2 = positions1[self.idx2]
        scalar2, vector2 = scalar1[self.idx2], vector1[self.idx2]
        scalar2, vector2 = self._blocks(self.coarse_encoder, scalar2, vector2, positions2, self.edge2)
        scalar1 = scalar1 + self.scalar_up2(scalar2[self.parent2])
        vector1 = vector1 + self.vector_up2(vector2[self.parent2])
        scalar1, vector1 = self._blocks(self.middle_decoder, scalar1, vector1, positions1, self.edge1)
        scalar0 = scalar0 + self.scalar_up1(scalar1[self.parent1])
        vector0 = vector0 + self.vector_up1(vector1[self.parent1])
        scalar0, vector0 = self._blocks(self.fine_decoder, scalar0, vector0, positions, self.edge0)
        output = self.vector_output(vector0)
        output = tangent_projection(output, normals.unsqueeze(1).expand_as(output))
        if self.variant == "direct_cycle":
            field = output.permute(1, 0, 2).contiguous()
            return {"field": field, "raw_field": field}
        mean_vector = output[:, 0]
        coefficients = output[:, 1:]
        residual = torch.einsum("tk,nkc->tnc", self.temporal_basis, coefficients)
        residual = tangent_projection(residual, normals)
        residual = residual - residual.mean(dim=0, keepdim=True)
        cone_coordinate = self.cone_output(scalar0).squeeze(-1)
        mean_magnitude = jensen_cone_mean_magnitude(mean_vector, cone_coordinate, torch)
        raw_field = mean_vector.unsqueeze(0) + residual
        field = raw_field
        if exact_moment_projection:
            field = project_cycle_moments(residual, mean_vector, mean_magnitude, normals, torch)["field"]
        return {
            "field": field,
            "raw_field": raw_field,
            "mean_vector": mean_vector,
            "mean_magnitude": mean_magnitude,
            "residual": residual,
        }


def model_parameter_count(model: nn.Module) -> int:
    return sum(int(parameter.numel()) for parameter in model.parameters() if parameter.requires_grad)


def _case_by_id(records: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    output: dict[str, Mapping[str, Any]] = {}
    for record in records:
        case_id = str(record.get("case", ""))
        _require(case_id and case_id not in output, "case_id_integrity")
        output[case_id] = record
    return output


def _aligned_ghd(mesh: Mapping[str, Any]) -> dict[str, torch.Tensor]:
    cases = [str(item) for item in mesh["cases"]]
    ghd = mesh["ghd"].detach().to(dtype=torch.float32, device="cpu")
    _require(tuple(ghd.shape) == (578, 432) and len(cases) == 578 and len(set(cases)) == 578, "ghd_alignment")
    _require(bool(torch.isfinite(ghd).all().item()), "ghd_nonfinite")
    return {case_id: ghd[index] for index, case_id in enumerate(cases)}


def _extract_topology(mesh: Mapping[str, Any]) -> dict[str, torch.Tensor]:
    edge_list = mesh["edge_index_list"]
    idx_list = mesh["idx_list"]
    _require(len(edge_list) >= 3 and len(idx_list) >= 2, "mesh_hierarchy")
    idx1 = idx_list[0].detach().to(dtype=torch.int64, device="cpu").reshape(-1)
    idx2 = idx_list[1].detach().to(dtype=torch.int64, device="cpu").reshape(-1)
    _require(int(idx1.min().item()) >= 0 and int(idx1.max().item()) < 13_902, "idx1_range")
    _require(int(idx2.min().item()) >= 0 and int(idx2.max().item()) < int(idx1.numel()), "idx2_range")
    edge0 = symmetrize_edges(edge_list[0].detach(), 13_902)
    edge1 = symmetrize_edges(edge_list[1].detach(), int(idx1.numel()))
    edge2 = symmetrize_edges(edge_list[2].detach(), int(idx2.numel()))
    faces = mesh["faces_list"][0].detach().to(dtype=torch.int64, device="cpu")
    _require(faces.ndim == 2 and int(faces.shape[1]) == 3, "faces_shape")
    _require(int(faces.min().item()) >= 0 and int(faces.max().item()) < 13_902, "faces_range")
    _require(not bool((faces[:, 0] == faces[:, 1]).any().item()) and not bool((faces[:, 1] == faces[:, 2]).any().item()) and not bool((faces[:, 0] == faces[:, 2]).any().item()), "faces_repeated_vertex")
    return {
        "edge0": edge0,
        "edge1": edge1,
        "edge2": edge2,
        "idx1": idx1,
        "idx2": idx2,
        "parent1": graph_parent_assignment(edge0, idx1, 13_902),
        "parent2": graph_parent_assignment(edge1, idx2, int(idx1.numel())),
        "faces": faces,
    }


def _cache_case(path: Path, canonical: Mapping[str, torch.Tensor], ghd: torch.Tensor, ghd_mean: torch.Tensor, ghd_std: torch.Tensor) -> None:
    payload = {key: value.to(dtype=torch.float32, device="cpu") for key, value in canonical.items()}
    payload["ghd"] = ((ghd - ghd_mean) / ghd_std).to(dtype=torch.float32, device="cpu")
    _strict_atomic_torch_save(path, payload)


def prepare_cache(
    contract: Mapping[str, Any],
    d6_registration_path: str | Path,
    transient_path: str | Path,
    steady_path: str | Path,
    private_manifest_path: str | Path,
    cache_directory: str | Path,
    result_path: str | Path,
) -> dict[str, Any]:
    started = time.monotonic()
    cache = Path(cache_directory)
    _require(not cache.exists(), "cache_exists")
    cache.mkdir(parents=True)
    try:
        _verify_exact_file(transient_path, contract["source_identity"]["transient"], "transient")
        _verify_exact_file(steady_path, contract["source_identity"]["steady"], "steady")
        manifest_path = Path(private_manifest_path)
        _require(manifest_path.is_file() and file_sha256(manifest_path) == contract["bound_upstream"]["d5_private_manifest_sha256"], "private_manifest_identity")
        d6_contract = load_d6_registration(d6_registration_path)
        buckets = validate_private_split_manifest(
            d6_contract, json.loads(manifest_path.read_text(encoding="utf-8"))
        )
        _require((len(buckets["train"]), len(buckets["validation"]), len(buckets["outer_test"]), len(buckets["auxiliary"])) == (406, 51, 51, 70), "split_counts")
        steady = safe_torch_load(steady_path, torch)
        transient = safe_torch_load(transient_path, torch)
        expected_labels = ["x", "y", "z", "x_normal", "y_normal", "z_normal", "wss_x", "wss_y", "wss_z"]
        _require([str(item) for item in steady["label"]] == expected_labels, "release_labels")
        mean = steady["tensor_norm"]["mean"].detach().to(dtype=torch.float32, device="cpu").reshape(-1)
        std = steady["tensor_norm"]["std"].detach().to(dtype=torch.float32, device="cpu").reshape(-1)
        _require(mean.numel() == std.numel() == 9 and bool((std > 0).all().item()), "release_normalization")
        mesh = transient["mesh_data"]
        topology = _extract_topology(mesh)
        faces = topology.pop("faces")
        records = _case_by_id(transient["registered_data_list"])
        ghd_by_id = _aligned_ghd(mesh)
        allowed_ids = list(buckets["train"]) + list(buckets["validation"])
        forbidden = set(buckets["outer_test"]) | set(buckets["auxiliary"])
        _require(not set(allowed_ids).intersection(forbidden), "sealed_split_overlap")
        _require(set(allowed_ids).issubset(records) and set(allowed_ids).issubset(ghd_by_id), "allowed_case_missing")

        ghd_train = torch.stack([ghd_by_id[case_id] for case_id in buckets["train"]])
        ghd_mean = ghd_train.mean(dim=0)
        ghd_std = ghd_train.std(dim=0, unbiased=False).clamp(min=1e-6)
        covariance = torch.zeros((80, 80), dtype=torch.float64, device="cuda")
        squared_sum = torch.zeros((), dtype=torch.float64, device="cuda")
        vector_count = 0
        for case_id in buckets["train"]:
            record = records[case_id]
            _require([str(item) for item in record.get("labels", [])] == expected_labels, "train_labels")
            tensor = record["tensor"]
            _require(tuple(tensor.shape) == (80, 13_902, 9), "train_tensor_shape")
            canonical = canonicalize_case(tensor, mean, std, faces)
            wss = canonical["wss"].to(device="cuda", dtype=torch.float32)
            residual = wss - wss.mean(dim=0, keepdim=True)
            flattened = residual.reshape(80, -1)
            covariance += (flattened @ flattened.T).to(dtype=torch.float64)
            squared_sum += torch.sum(wss.to(dtype=torch.float64) ** 2)
            vector_count += int(wss.shape[0] * wss.shape[1])
        _require(vector_count == 406 * 80 * 13_902, "train_vector_count")
        wss_scale = float(torch.sqrt(squared_sum / vector_count).item())
        covariance = covariance.cpu() / (406 * 13_902 * 3)
        basis_result = choose_temporal_basis(
            covariance,
            minimum_rank=int(contract["train_only_temporal_basis"]["minimum_rank"]),
            maximum_rank=int(contract["train_only_temporal_basis"]["maximum_rank"]),
            retained_energy=float(contract["train_only_temporal_basis"]["minimum_retained_energy"]),
        )
        basis = basis_result["basis"]

        for split in ("train", "validation"):
            (cache / split).mkdir()
            for index, case_id in enumerate(buckets[split]):
                record = records[case_id]
                _require([str(item) for item in record.get("labels", [])] == expected_labels, f"{split}_labels")
                tensor = record["tensor"]
                _require(tuple(tensor.shape) == (80, 13_902, 9), f"{split}_tensor_shape")
                canonical = canonicalize_case(tensor, mean, std, faces, wss_scale=wss_scale)
                _cache_case(cache / split / f"case_{index:04d}.pt", canonical, ghd_by_id[case_id], ghd_mean, ghd_std)

        _strict_atomic_torch_save(cache / "topology.pt", topology)
        _strict_atomic_torch_save(cache / "temporal_basis.pt", {"basis": basis})
        sample = torch.load(cache / "train" / "case_0000.pt", map_location="cpu", weights_only=True)
        topology_gpu = {key: value.to(device="cuda") for key, value in topology.items()}
        sample_gpu = {key: value.to(device="cuda") for key, value in sample.items()}
        smoke: dict[str, Any] = {}
        for variant in ("direct_cycle", "moment_pod"):
            model = MeshCanonicalizedPilot(topology_gpu, variant=variant, temporal_basis=basis.to(device="cuda") if variant == "moment_pod" else None).to(device="cuda")
            torch.cuda.reset_peak_memory_stats()
            before = time.monotonic()
            output = model(sample_gpu, exact_moment_projection=False)
            loss = field_loss(output["field"], sample_gpu["wss"], sample_gpu["vertex_weights"])
            loss.backward()
            torch.cuda.synchronize()
            if variant == "moment_pod":
                with torch.no_grad():
                    projected = model(sample_gpu, exact_moment_projection=True)["field"]
                    _require(bool(torch.isfinite(projected).all().item()), "projection_smoke")
            smoke[variant] = {
                "parameter_count": model_parameter_count(model),
                "forward_backward_seconds": time.monotonic() - before,
                "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
                "finite_loss": bool(torch.isfinite(loss).item()),
            }
            _require(smoke[variant]["finite_loss"], f"{variant}_smoke")
            del model, output, loss
            torch.cuda.empty_cache()

        cache_manifest = {
            "schema_version": "aurora.aneug_processed_v4_d9.private_cache.v1",
            "protocol_id": contract["protocol_id"],
            "r0_pass": True,
            "train_cases": 406,
            "validation_cases": 51,
            "outer_cases_read": 0,
            "auxiliary_cases_read": 0,
            "case_ids_included": False,
            "wss_scale": wss_scale,
            "temporal_rank": int(basis_result["rank"]),
            "temporal_retained_energy": float(basis_result["retained_energy"]),
            "topology_sha256": file_sha256(cache / "topology.pt"),
            "temporal_basis_sha256": file_sha256(cache / "temporal_basis.pt"),
        }
        _strict_atomic_json(cache / "cache_manifest.json", cache_manifest)
        result = {
            "schema_version": "aurora.aneug_processed_v4_d9.r0_result.v1",
            "protocol_id": contract["protocol_id"],
            "status": "complete_pass",
            "r0_pass": True,
            "train_cases": 406,
            "validation_cases": 51,
            "outer_or_auxiliary_tensor_values_read": False,
            "case_ids_included": False,
            "temporal_rank": int(basis_result["rank"]),
            "temporal_retained_energy": float(basis_result["retained_energy"]),
            "wss_scale": wss_scale,
            "smoke": smoke,
            "elapsed_seconds": time.monotonic() - started,
            "single_seed_validation_development_only": True,
            "paper_result_or_claim": False,
        }
        _strict_atomic_json(result_path, result)
        return result
    except Exception:
        # Accepted R0 failure closes D9-R0.  Partial private cache is retained
        # for diagnosis and is never treated as a completed cache.
        raise


def load_cached_split(cache_directory: str | Path, split: str) -> list[dict[str, torch.Tensor]]:
    _require(split in {"train", "validation"}, "cache_split")
    root = Path(cache_directory)
    manifest = json.loads((root / "cache_manifest.json").read_text(encoding="utf-8"))
    _require(manifest.get("r0_pass") is True, "r0_not_passed")
    expected = int(manifest[f"{split}_cases"])
    paths = sorted((root / split).glob("case_*.pt"))
    _require(len(paths) == expected, f"{split}_cache_count")
    return [torch.load(path, map_location="cpu", weights_only=True) for path in paths]


def field_loss(prediction: torch.Tensor, reference: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
    numerator = torch.sum(weights.unsqueeze(0) * torch.sum((prediction - reference) ** 2, dim=-1)) / prediction.shape[0]
    denominator = torch.sum(weights.unsqueeze(0) * torch.sum(reference ** 2, dim=-1)) / prediction.shape[0]
    return numerator / torch.clamp(denominator, min=1e-12)


def training_loss(output: Mapping[str, torch.Tensor], reference: torch.Tensor, weights: torch.Tensor, variant: str) -> torch.Tensor:
    loss = field_loss(output["raw_field"], reference, weights)
    if variant == "direct_cycle":
        return loss
    reference_mean = reference.mean(dim=0)
    reference_magnitude = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0)
    mean_vector_error = torch.sum(weights * torch.sum((output["mean_vector"] - reference_mean) ** 2, dim=-1)) / torch.clamp(torch.sum(weights * torch.sum(reference_mean ** 2, dim=-1)), min=1e-12)
    mean_magnitude_error = torch.sum(weights * (output["mean_magnitude"] - reference_magnitude) ** 2) / torch.clamp(torch.sum(weights * reference_magnitude ** 2), min=1e-12)
    raw_magnitude = torch.linalg.vector_norm(output["raw_field"], dim=-1).mean(dim=0)
    consistency = torch.sum(weights * (raw_magnitude - output["mean_magnitude"]) ** 2) / torch.clamp(torch.sum(weights * output["mean_magnitude"].detach() ** 2), min=1e-12)
    return loss + 0.2 * mean_vector_error + 0.2 * mean_magnitude_error + 0.1 * consistency


def case_metrics(prediction: torch.Tensor, reference: torch.Tensor, weights: torch.Tensor) -> dict[str, float]:
    finite = bool(torch.isfinite(prediction).all().item())
    if not finite:
        return {"field_relative_l2": 1e6, "tawss_normalized_absolute_error": 1e6, "osi_mae": 0.5, "osi_coverage": 0.0, "tangency_rms": 1e6}
    field = float(torch.sqrt(field_loss(prediction, reference, weights)).item())
    reference_tawss = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0)
    prediction_tawss = torch.linalg.vector_norm(prediction, dim=-1).mean(dim=0)
    tawss = float((torch.sum(weights * torch.abs(prediction_tawss - reference_tawss)) / torch.clamp(torch.sum(weights * reference_tawss), min=1e-12)).item())
    reference_mean = reference.mean(dim=0)
    prediction_mean = prediction.mean(dim=0)
    support = reference_tawss > 1e-4
    prediction_valid = support & torch.isfinite(prediction_tawss) & (prediction_tawss > 0)
    coverage = float(prediction_valid.sum().div(torch.clamp(support.sum(), min=1)).item())
    reference_osi = 0.5 * (1.0 - torch.linalg.vector_norm(reference_mean, dim=-1) / torch.clamp(reference_tawss, min=1e-12))
    prediction_osi = 0.5 * (1.0 - torch.linalg.vector_norm(prediction_mean, dim=-1) / torch.clamp(prediction_tawss, min=1e-12))
    osi_error = torch.full_like(reference_osi, 0.5)
    osi_error[prediction_valid] = torch.abs(prediction_osi[prediction_valid] - reference_osi[prediction_valid])
    osi = float(torch.sum(weights[support] * osi_error[support]).div(torch.clamp(weights[support].sum(), min=1e-12)).item())
    return {"field_relative_l2": field, "tawss_normalized_absolute_error": tawss, "osi_mae": osi, "osi_coverage": coverage}


@torch.no_grad()
def evaluate(model: MeshCanonicalizedPilot, cases: Sequence[Mapping[str, torch.Tensor]], device: torch.device) -> dict[str, Any]:
    model.eval()
    per_case: list[dict[str, float]] = []
    for cpu_case in cases:
        case = {key: value.to(device=device, non_blocking=True) for key, value in cpu_case.items()}
        prediction = model(case, exact_moment_projection=model.variant == "moment_pod")["field"]
        per_case.append(case_metrics(prediction, case["wss"], case["vertex_weights"]))
    keys = tuple(per_case[0])
    return {
        "aggregate": {key: sum(item[key] for item in per_case) / len(per_case) for key in keys},
        "per_case_without_identifiers": per_case,
        "case_count": len(per_case),
    }


def train_variant(contract: Mapping[str, Any], cache_directory: str | Path, variant: str, result_path: str | Path, checkpoint_path: str | Path) -> dict[str, Any]:
    _require(variant in {"direct_cycle", "moment_pod"}, "variant")
    seed = int(contract["optimization"]["seed"])
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device("cuda")
    cache = Path(cache_directory)
    manifest = json.loads((cache / "cache_manifest.json").read_text(encoding="utf-8"))
    _require(manifest.get("r0_pass") is True, "r0_not_passed")
    topology = torch.load(cache / "topology.pt", map_location=device, weights_only=True)
    basis = torch.load(cache / "temporal_basis.pt", map_location=device, weights_only=True)["basis"]
    train_cases = load_cached_split(cache, "train")
    validation_cases = load_cached_split(cache, "validation")
    model = MeshCanonicalizedPilot(topology, variant=variant, temporal_basis=basis if variant == "moment_pod" else None).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(contract["optimization"]["learning_rate"]), weight_decay=float(contract["optimization"]["weight_decay"]))
    maximum_epochs = int(contract["optimization"]["maximum_epochs"])
    minimum_epochs = int(contract["optimization"]["minimum_epochs"])
    patience = int(contract["optimization"]["early_stopping_patience"])
    accumulation = int(contract["optimization"]["gradient_accumulation_cases"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=maximum_epochs, eta_min=0.1 * float(contract["optimization"]["learning_rate"]))
    best_field = math.inf
    best_epoch = -1
    best_state: dict[str, torch.Tensor] | None = None
    stale = 0
    history: list[dict[str, float | int]] = []
    started = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    for epoch in range(maximum_epochs):
        model.train()
        order = list(range(len(train_cases)))
        random.Random(seed + epoch).shuffle(order)
        optimizer.zero_grad(set_to_none=True)
        epoch_loss = 0.0
        for step, index in enumerate(order):
            cpu_case = train_cases[index]
            case = {key: value.to(device=device, non_blocking=True) for key, value in cpu_case.items()}
            output = model(case, exact_moment_projection=False)
            loss = training_loss(output, case["wss"], case["vertex_weights"], variant)
            _require(bool(torch.isfinite(loss).item()), "nonfinite_training_loss")
            (loss / accumulation).backward()
            epoch_loss += float(loss.detach().item())
            if (step + 1) % accumulation == 0 or step + 1 == len(order):
                torch.nn.utils.clip_grad_norm_(model.parameters(), float(contract["optimization"]["gradient_clip_norm"]))
                optimizer.step()
                optimizer.zero_grad(set_to_none=True)
        scheduler.step()
        validation = evaluate(model, validation_cases, device)
        validation_field = float(validation["aggregate"]["field_relative_l2"])
        history.append({"epoch": epoch + 1, "training_loss": epoch_loss / len(order), "validation_field_relative_l2": validation_field, "learning_rate": float(scheduler.get_last_lr()[0])})
        if validation_field < best_field:
            best_field = validation_field
            best_epoch = epoch + 1
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
        if epoch + 1 >= minimum_epochs and stale >= patience:
            break
    _require(best_state is not None and best_epoch > 0, "missing_best_checkpoint")
    model.load_state_dict(best_state)
    final_validation = evaluate(model, validation_cases, device)
    checkpoint = {
        "schema_version": "aurora.aneug_processed_v4_d9.private_checkpoint.v1",
        "protocol_id": contract["protocol_id"],
        "variant": variant,
        "seed": seed,
        "best_epoch": best_epoch,
        "model_state_dict": best_state,
        "optimizer_selection_metric": "validation_field_relative_l2",
    }
    _strict_atomic_torch_save(checkpoint_path, checkpoint)
    result = {
        "schema_version": "aurora.aneug_processed_v4_d9.private_training_result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "complete",
        "variant": variant,
        "seed": seed,
        "best_epoch": best_epoch,
        "epochs_completed": len(history),
        "parameter_count": model_parameter_count(model),
        "elapsed_seconds": time.monotonic() - started,
        "peak_gpu_bytes": int(torch.cuda.max_memory_allocated()),
        "validation": final_validation,
        "history": history,
        "train_case_count": len(train_cases),
        "validation_case_count": len(validation_cases),
        "outer_or_auxiliary_tensor_values_read": False,
        "case_ids_included": False,
        "single_seed_validation_development_only": True,
        "paper_result_or_claim": False,
    }
    _strict_atomic_json(result_path, result)
    return result


def aggregate_development_screen(contract: Mapping[str, Any], direct_path: str | Path, moment_path: str | Path, result_path: str | Path) -> dict[str, Any]:
    direct = json.loads(Path(direct_path).read_text(encoding="utf-8"))
    moment = json.loads(Path(moment_path).read_text(encoding="utf-8"))
    _require(direct.get("variant") == "direct_cycle" and moment.get("variant") == "moment_pod", "result_variants")
    _require(direct.get("protocol_id") == moment.get("protocol_id") == contract["protocol_id"], "result_protocol")
    d = direct["validation"]["aggregate"]
    m = moment["validation"]["aggregate"]
    ratios = {
        "field": m["field_relative_l2"] / max(d["field_relative_l2"], 1e-12),
        "tawss": m["tawss_normalized_absolute_error"] / max(d["tawss_normalized_absolute_error"], 1e-12),
        "osi": m["osi_mae"] / max(d["osi_mae"], 1e-12),
    }
    screen = contract["development_screen"]
    checks = {
        "direct_field_feasible": d["field_relative_l2"] <= screen["maximum_direct_validation_field_relative_L2"],
        "moment_field_tax": ratios["field"] <= screen["maximum_moment_over_direct_field_error_ratio"],
        "moment_tawss_improvement": ratios["tawss"] <= screen["maximum_moment_over_direct_TAWSS_error_ratio"],
        "moment_osi_improvement": ratios["osi"] <= screen["maximum_moment_over_direct_OSI_error_ratio"],
        "direct_osi_coverage": d["osi_coverage"] >= screen["minimum_validation_OSI_coverage"],
        "moment_osi_coverage": m["osi_coverage"] >= screen["minimum_validation_OSI_coverage"],
    }
    passed = all(checks.values())
    result = {
        "schema_version": "aurora.aneug_processed_v4_d9.private_development_screen.v1",
        "protocol_id": contract["protocol_id"],
        "screen_pass": passed,
        "checks": checks,
        "validation_aggregate": {"direct_cycle": d, "moment_pod": m},
        "moment_over_direct_ratios": ratios,
        "screen_is_paper_result": False,
        "screen_pass_authorizes": screen["screen_pass_authorizes"] if passed else "no_successor_registration",
        "outer_test_read": False,
    }
    _strict_atomic_json(result_path, result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--mode", choices=("validate", "prepare", "train", "aggregate"), required=True)
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--d6-registration", type=Path)
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--private-d5-manifest", type=Path)
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--variant", choices=("direct_cycle", "moment_pod"))
    parser.add_argument("--result", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--direct-result", type=Path)
    parser.add_argument("--moment-result", type=Path)
    args = parser.parse_args(argv)
    contract = load_contract(args.config)
    if args.mode == "validate":
        return 0
    stage = "R0_prepare_smoke" if args.mode == "prepare" else (f"R1_{args.variant}" if args.mode == "train" else "aggregate")
    _require(args.activation is not None and args.expected_commit, "missing_activation")
    validate_private_activation(args.activation, contract, args.expected_commit, stage)
    torch.set_num_threads(4)
    if args.mode == "prepare":
        _require(torch.cuda.is_available(), "cuda_required")
        _require(all(value is not None for value in (args.d6_registration, args.transient, args.steady, args.private_d5_manifest, args.cache, args.result)), "missing_prepare_argument")
        prepare_cache(contract, args.d6_registration, args.transient, args.steady, args.private_d5_manifest, args.cache, args.result)
    elif args.mode == "train":
        _require(torch.cuda.is_available(), "cuda_required")
        _require(all(value is not None for value in (args.cache, args.variant, args.result, args.checkpoint)), "missing_train_argument")
        train_variant(contract, args.cache, args.variant, args.result, args.checkpoint)
    else:
        _require(all(value is not None for value in (args.direct_result, args.moment_result, args.result)), "missing_aggregate_argument")
        aggregate_development_screen(contract, args.direct_result, args.moment_result, args.result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
