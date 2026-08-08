"""Validation-only Aneumo V1 backbone smoke for ISBI 2027.

The module keeps the development boundary explicit: it reads only train and
validation field arrays, compares four registered backbones on the same node
subsets and schedules, and never opens the test split.  The 64-case cache is
development-only; no V1 outcome is a headline or submission result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class AneumoISBIV1Error(RuntimeError):
    """Raised when the V1 protocol or development execution is invalid."""


@dataclass(frozen=True)
class CaseData:
    case_id: int
    base_family: int
    split: str
    coordinates: Any
    velocity: Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _imports() -> tuple[Any, Any, Any]:
    try:
        import h5py
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoISBIV1Error("V1 requires h5py, numpy, and torch.") from exc
    return np, h5py, torch


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("status") != "preregistered_before_v1_learning_result":
        raise AneumoISBIV1Error("V1 must remain prospectively registered.")
    access = payload["access"]
    if (
        access.get("read_field_splits") != ["train", "validation"]
        or access.get("forbid_test_field_reads") is not True
        or access.get("test_metrics_or_selection") is not False
    ):
        raise AneumoISBIV1Error("V1 must not read or select on test fields.")
    models = payload["models"]
    expected_models = [
        "q_pointnet",
        "knn_mgn",
        "deltaphi_graph",
        "anchor_token_equivariant",
    ]
    if models["families"] != expected_models:
        raise AneumoISBIV1Error("V1 model families cannot change after registration.")
    if models.get("candidate_is_method_novelty") is not False:
        raise AneumoISBIV1Error("The engineering backbone is not method novelty.")
    training = payload["training"]
    if (
        training["seeds"] != [820801, 820802, 820803]
        or int(training.get("steps", -1)) != 3000
        or int(training.get("validation_every_steps", -1)) != 250
        or training.get("paired_response_loss_weight") != 0.0
        or training.get("require_cuda") is not True
    ):
        raise AneumoISBIV1Error("V1 training schedule cannot change after registration.")
    if payload["feasibility_gate"].get("local_repair_allowed") is not False:
        raise AneumoISBIV1Error("V1 failure cannot enter a local repair loop.")
    authorization = payload["authorization"]
    if any(
        authorization[key] is not False
        for key in ("method_novelty", "outer_test", "headline_result", "isbi_submission")
    ):
        raise AneumoISBIV1Error("V1 cannot authorize a paper claim or outer test.")
    if authorization.get("measurement_solution_objective_requires_positive_m0") is not True:
        raise AneumoISBIV1Error("The candidate objective remains blocked before M0.")
    if payload["task"]["missing_condition_law"] != (
        "exact_discrete_uniform_over_registered_values"
    ):
        raise AneumoISBIV1Error("V1 must retain the exact registered design law.")
    ensemble = models.get("deep_ensemble", {})
    if (
        ensemble.get("members_per_family") != 3
        or ensemble.get("full_q_point_prediction")
        != "mean_across_seed_models_at_matching_condition"
        or ensemble.get("missing_predictive_distribution")
        != "cartesian_product_of_three_seed_models_and_eight_registered_condition_values"
        or ensemble.get("missing_predictive_components") != 24
        or ensemble.get("selector_uses_ensemble_metrics") is not False
        or ensemble.get("supports_uncertainty_separation_claim") is not False
    ):
        raise AneumoISBIV1Error("V1 must retain the registered 3x8 ensemble estimand.")
    oracle = payload["controls"].get("response_only_oracle", {})
    if (
        float(oracle.get("anchor_mass_flow_kg_s", float("nan"))) != 0.0025
        or float(oracle.get("power", float("nan"))) != 1.075
        or oracle.get("uses_true_validation_anchor_field") is not True
        or oracle.get("eligible_for_model_selection_or_gate") is not False
        or oracle.get("eligible_endpoint")
        != "validation_same_geometry_response_relative_l2_only"
    ):
        raise AneumoISBIV1Error("The same-case oracle must remain response-only.")
    if payload["controls"].get("negative_control") != (
        "condition_zeroed_at_validation_for_every_registered_family_with_gate_"
        "applied_to_selected_family"
    ):
        raise AneumoISBIV1Error("V1 condition-zero negative control cannot change.")
    aggregation = payload.get("aggregation", {})
    if (
        aggregation.get("requires_exact_four_family_by_three_seed_factorial")
        is not True
        or aggregation.get("replay_each_checkpoint_on_validation") is not True
        or aggregation.get("selector_uses_only_registered_per_seed_metrics")
        is not True
        or aggregation.get("response_oracle_is_report_only") is not True
        or aggregation.get("test_fields_read") is not False
        or float(aggregation.get("checkpoint_replay_absolute_tolerance", -1.0))
        != 0.00001
    ):
        raise AneumoISBIV1Error("V1 aggregation contract cannot change after registration.")
    expected_rank = [
        "seed_mean_validation_response_relative_l2",
        "seed_mean_validation_full_q_relative_l2",
        "seed_mean_missing_field_energy_score",
        "parameter_count",
    ]
    if (
        payload["selector"].get("rank_by") != expected_rank
        or payload["selector"].get("requires_all_three_seeds") is not True
    ):
        raise AneumoISBIV1Error("V1 selector cannot change after registration.")
    expected_checks = [
        "all_twelve_tasks_exit_zero",
        "no_test_field_read",
        "all_metrics_finite",
        "all_checkpoints_selected_on_validation_only",
        "selected_model_worst_seed_full_q_relative_l2_at_most_0.35",
        "selected_model_worst_seed_response_relative_l2_at_most_0.50",
        "condition_zeroing_worsens_full_q_error_in_all_selected_model_seeds",
    ]
    if payload["feasibility_gate"].get("checks") != expected_checks:
        raise AneumoISBIV1Error("V1 feasibility gate cannot change after registration.")
    return dict(payload)


def load_config(path: str | Path) -> dict[str, Any]:
    return validate_config(json.loads(Path(path).read_text(encoding="utf-8")))


def _decode(value: Any) -> str:
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def load_development_cases(
    config: Mapping[str, Any], cache: Path
) -> tuple[list[CaseData], list[CaseData], Any]:
    """Read train/validation arrays while deliberately skipping test fields."""

    np, h5py, _ = _imports()
    if _sha256(cache) != config["source"]["cache_sha256"]:
        raise AneumoISBIV1Error("V1 cache SHA-256 mismatch.")
    allowed = set(config["access"]["read_field_splits"])
    cases: dict[str, list[CaseData]] = {"train": [], "validation": []}
    with h5py.File(cache, "r") as handle:
        flows = np.asarray(handle["mass_flows_kg_s"], dtype=np.float64)
        expected_flows = np.asarray(config["task"]["condition_values"], dtype=np.float64)
        if not np.allclose(flows, expected_flows, rtol=0.0, atol=1e-9):
            raise AneumoISBIV1Error("V1 mass-flow values changed.")
        for case_name in sorted(handle["geometries"], key=int):
            group = handle["geometries"][case_name]
            split = _decode(group.attrs["split"])
            if split == "test":
                continue
            if split not in allowed:
                raise AneumoISBIV1Error(f"Unexpected cache split: {split}")
            # Only the three velocity channels are materialized. Test groups
            # are skipped before either dataset is indexed.
            coordinates = np.asarray(group["coordinates_m"], dtype=np.float32)
            velocity = np.asarray(
                group["pressure_velocity"][:, :, 1:4], dtype=np.float32
            )
            if coordinates.shape != (4096, 3) or velocity.shape != (8, 4096, 3):
                raise AneumoISBIV1Error(f"Unexpected V1 tensor shape for {case_name}.")
            if not np.isfinite(coordinates).all() or not np.isfinite(velocity).all():
                raise AneumoISBIV1Error(f"Non-finite V1 input for {case_name}.")
            cases[split].append(
                CaseData(
                    case_id=int(case_name),
                    base_family=int(group.attrs["base_family"]),
                    split=split,
                    coordinates=coordinates,
                    velocity=velocity,
                )
            )
    split_contract = config["split"]
    if len(cases["train"]) != int(split_contract["train_cases"]):
        raise AneumoISBIV1Error("V1 train case count mismatch.")
    if len(cases["validation"]) != int(split_contract["validation_cases"]):
        raise AneumoISBIV1Error("V1 validation case count mismatch.")
    if len({case.base_family for case in cases["train"]}) != int(
        split_contract["train_families"]
    ):
        raise AneumoISBIV1Error("V1 train family count mismatch.")
    if len({case.base_family for case in cases["validation"]}) != int(
        split_contract["validation_families"]
    ):
        raise AneumoISBIV1Error("V1 validation family count mismatch.")
    if {case.base_family for case in cases["train"]} & {
        case.base_family for case in cases["validation"]
    }:
        raise AneumoISBIV1Error("V1 train and validation families overlap.")
    return cases["train"], cases["validation"], flows


def deterministic_node_subset(
    nodes: int, count: int, *, seed: int, case_id: int
) -> Any:
    np, _, _ = _imports()
    if count > nodes:
        raise AneumoISBIV1Error("V1 node subset exceeds available nodes.")
    generator = np.random.default_rng(int(seed) + int(case_id))
    return np.sort(generator.choice(nodes, size=count, replace=False))


def normalize_coordinates(coordinates: Any) -> tuple[Any, Any, float]:
    np, _, _ = _imports()
    coordinates64 = np.asarray(coordinates, dtype=np.float64)
    center = np.mean(coordinates64, axis=0, keepdims=True)
    centered = coordinates64 - center
    scale = float(np.sqrt(np.mean(np.sum(centered * centered, axis=-1))))
    if not math.isfinite(scale) or scale <= 1e-12:
        raise AneumoISBIV1Error("Degenerate geometry coordinate scale.")
    return (centered / scale).astype(np.float32), center.astype(np.float32), scale


def knn_indices(coordinates: Any, k: int, *, chunk: int = 256) -> Any:
    """Return exact kNN without self edges using bounded distance chunks."""

    _, _, torch = _imports()
    points = torch.as_tensor(coordinates, dtype=torch.float32)
    if points.ndim != 2 or points.shape[1] != 3 or k >= points.shape[0]:
        raise AneumoISBIV1Error("Invalid coordinates or k for V1 kNN.")
    neighbors = []
    all_indices = torch.arange(points.shape[0])
    for start in range(0, points.shape[0], int(chunk)):
        stop = min(start + int(chunk), points.shape[0])
        distance = torch.cdist(points[start:stop], points)
        rows = torch.arange(stop - start)
        distance[rows, all_indices[start:stop]] = float("inf")
        neighbors.append(torch.topk(distance, k=int(k), largest=False).indices)
    return torch.cat(neighbors, dim=0)


def farthest_point_indices(coordinates: Any, count: int) -> Any:
    """Deterministic, rotation-invariant anchor order starting from centroid."""

    _, _, torch = _imports()
    points = torch.as_tensor(coordinates)
    squeeze = points.ndim == 2
    if squeeze:
        points = points.unsqueeze(0)
    if points.ndim != 3 or points.shape[-1] != 3 or count > points.shape[1]:
        raise AneumoISBIV1Error("Invalid coordinates or anchor count.")
    center = points.mean(dim=1, keepdim=True)
    radial = ((points - center) ** 2).sum(dim=-1)
    current = radial.argmax(dim=1)
    selected = []
    minimum = torch.full_like(radial, float("inf"))
    batch = torch.arange(points.shape[0], device=points.device)
    for _ in range(int(count)):
        selected.append(current)
        anchor = points[batch, current].unsqueeze(1)
        distance = ((points - anchor) ** 2).sum(dim=-1)
        minimum = torch.minimum(minimum, distance)
        current = minimum.argmax(dim=1)
    result = torch.stack(selected, dim=1)
    return result[0] if squeeze else result


def _gather_nodes(values: Any, indices: Any) -> Any:
    _, _, torch = _imports()
    batch = torch.arange(values.shape[0], device=values.device)[:, None, None]
    return values[batch, indices]


def _mlp(nn: Any, dimensions: Sequence[int], *, final_activation: bool = False) -> Any:
    layers = []
    for index, (left, right) in enumerate(zip(dimensions[:-1], dimensions[1:])):
        layers.append(nn.Linear(int(left), int(right)))
        if index < len(dimensions) - 2 or final_activation:
            layers.append(nn.SiLU())
    return nn.Sequential(*layers)


def build_model(config: Mapping[str, Any], family: str) -> Any:
    """Build one registered engineering backbone without third-party GNN code."""

    _, _, torch = _imports()
    nn = torch.nn
    model_config = config["models"]
    hidden = int(model_config["hidden_dim"])
    layers = int(model_config["message_passing_layers"])
    residual_blocks = int(model_config["parameter_match_residual_blocks"][family])
    anchors = int(config["representation"]["anchor_count"])

    class ResidualMLP(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = _mlp(nn, [hidden, hidden, hidden])
            self.norm = nn.LayerNorm(hidden)

        def forward(self, values: Any) -> Any:
            return self.norm(values + self.net(values))

    class MessageLayer(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.message = _mlp(nn, [2 * hidden + 1, hidden, hidden])
            self.update = _mlp(nn, [2 * hidden, hidden, hidden])
            self.norm = nn.LayerNorm(hidden)

        def forward(self, values: Any, coordinates: Any, neighbors: Any) -> Any:
            neighbor_values = _gather_nodes(values, neighbors)
            neighbor_coordinates = _gather_nodes(coordinates, neighbors)
            center_values = values.unsqueeze(2).expand_as(neighbor_values)
            center_coordinates = coordinates.unsqueeze(2)
            distance = torch.linalg.vector_norm(
                neighbor_coordinates - center_coordinates, dim=-1, keepdim=True
            )
            message = self.message(
                torch.cat([center_values, neighbor_values, distance], dim=-1)
            ).mean(dim=2)
            return self.norm(values + self.update(torch.cat([values, message], dim=-1)))

    class QPointNet(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.input = _mlp(nn, [4, hidden, hidden])
            self.blocks = nn.ModuleList(ResidualMLP() for _ in range(residual_blocks))
            self.global_net = _mlp(nn, [2 * hidden, hidden, hidden])
            self.output = _mlp(nn, [2 * hidden + 1, hidden, 3])

        def forward(self, coordinates: Any, condition: Any, neighbors: Any) -> Any:
            del neighbors
            q = condition[:, None, :].expand(-1, coordinates.shape[1], -1)
            values = self.input(torch.cat([coordinates, q], dim=-1))
            for block in self.blocks:
                values = block(values)
            global_value = self.global_net(
                torch.cat([values.mean(dim=1), values.amax(dim=1)], dim=-1)
            )
            global_value = global_value[:, None, :].expand(-1, coordinates.shape[1], -1)
            return self.output(torch.cat([values, global_value, q], dim=-1))

    class KNNMGN(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.input = _mlp(nn, [4, hidden, hidden])
            self.messages = nn.ModuleList(MessageLayer() for _ in range(layers))
            self.blocks = nn.ModuleList(ResidualMLP() for _ in range(residual_blocks))
            self.output = _mlp(nn, [hidden, hidden, 3])

        def forward(self, coordinates: Any, condition: Any, neighbors: Any) -> Any:
            q = condition[:, None, :].expand(-1, coordinates.shape[1], -1)
            values = self.input(torch.cat([coordinates, q], dim=-1))
            for message in self.messages:
                values = message(values, coordinates, neighbors)
            for block in self.blocks:
                values = block(values)
            return self.output(values)

    class DeltaPhiGraph(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.input = _mlp(nn, [3, hidden, hidden])
            self.messages = nn.ModuleList(MessageLayer() for _ in range(layers))
            self.blocks = nn.ModuleList(ResidualMLP() for _ in range(residual_blocks))
            self.base = _mlp(nn, [hidden, hidden, 3])
            self.response = _mlp(nn, [hidden + 1, hidden, 3])

        def forward(self, coordinates: Any, condition: Any, neighbors: Any) -> Any:
            values = self.input(coordinates)
            for message in self.messages:
                values = message(values, coordinates, neighbors)
            for block in self.blocks:
                values = block(values)
            q = condition[:, None, :].expand(-1, coordinates.shape[1], -1)
            # q is normalized to [-1, 1]; the registered 0.0025 anchor maps to 0.
            return self.base(values) + q * self.response(torch.cat([values, q], dim=-1))

    class TokenBlock(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            heads = int(model_config["attention_heads"])
            self.token_attention = nn.MultiheadAttention(hidden, heads, batch_first=True)
            self.node_attention = nn.MultiheadAttention(hidden, heads, batch_first=True)
            self.token_norm = nn.LayerNorm(hidden)
            self.node_norm = nn.LayerNorm(hidden)

        def forward(self, nodes: Any, tokens: Any) -> tuple[Any, Any]:
            update, _ = self.token_attention(tokens, nodes, nodes, need_weights=False)
            tokens = self.token_norm(tokens + update)
            update, _ = self.node_attention(nodes, tokens, tokens, need_weights=False)
            nodes = self.node_norm(nodes + update)
            return nodes, tokens

    class AnchorTokenEquivariant(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.input = _mlp(nn, [anchors + 1, hidden, hidden])
            self.messages = nn.ModuleList(MessageLayer() for _ in range(layers))
            self.tokens = nn.ModuleList(
                TokenBlock() for _ in range(int(model_config["token_blocks"]))
            )
            self.local_weight = _mlp(nn, [2 * hidden + 1, hidden, 1])
            self.anchor_weight = _mlp(nn, [2 * hidden + 1, hidden, 1])

        def forward(self, coordinates: Any, condition: Any, neighbors: Any) -> Any:
            anchor_indices = farthest_point_indices(coordinates, anchors)
            batch = torch.arange(coordinates.shape[0], device=coordinates.device)[:, None]
            anchor_coordinates = coordinates[batch, anchor_indices]
            anchor_distance = torch.linalg.vector_norm(
                coordinates[:, :, None, :] - anchor_coordinates[:, None, :, :],
                dim=-1,
            )
            q = condition[:, None, :].expand(-1, coordinates.shape[1], -1)
            values = self.input(torch.cat([anchor_distance, q], dim=-1))
            for message in self.messages:
                values = message(values, coordinates, neighbors)
            tokens = values[batch, anchor_indices]
            for block in self.tokens:
                values, tokens = block(values, tokens)

            neighbor_values = _gather_nodes(values, neighbors)
            neighbor_coordinates = _gather_nodes(coordinates, neighbors)
            local_delta = neighbor_coordinates - coordinates.unsqueeze(2)
            local_distance = torch.linalg.vector_norm(
                local_delta, dim=-1, keepdim=True
            ).clamp_min(1e-8)
            local_weight = self.local_weight(
                torch.cat(
                    [
                        values.unsqueeze(2).expand_as(neighbor_values),
                        neighbor_values,
                        local_distance,
                    ],
                    dim=-1,
                )
            )
            local_vector = (
                local_weight * local_delta / local_distance
            ).sum(dim=2) / math.sqrt(neighbors.shape[-1])

            anchor_delta = anchor_coordinates[:, None, :, :] - coordinates[:, :, None, :]
            anchor_distance_vector = torch.linalg.vector_norm(
                anchor_delta, dim=-1, keepdim=True
            ).clamp_min(1e-8)
            anchor_values = tokens[:, None, :, :].expand(
                -1, coordinates.shape[1], -1, -1
            )
            node_values = values[:, :, None, :].expand_as(anchor_values)
            anchor_weight = self.anchor_weight(
                torch.cat([node_values, anchor_values, anchor_distance_vector], dim=-1)
            )
            anchor_vector = (
                anchor_weight * anchor_delta / anchor_distance_vector
            ).sum(dim=2) / math.sqrt(anchors)
            return local_vector + anchor_vector

    builders = {
        "q_pointnet": QPointNet,
        "knn_mgn": KNNMGN,
        "deltaphi_graph": DeltaPhiGraph,
        "anchor_token_equivariant": AnchorTokenEquivariant,
    }
    if family not in builders:
        raise AneumoISBIV1Error(f"Unknown V1 model family: {family}")
    return builders[family]()


def _prepare_cases(
    config: Mapping[str, Any], cases: Sequence[CaseData]
) -> dict[int, dict[str, Any]]:
    np, _, _ = _imports()
    representation = config["representation"]
    prepared = {}
    for case in cases:
        subset = deterministic_node_subset(
            case.coordinates.shape[0],
            int(representation["development_nodes_per_case"]),
            seed=int(representation["node_subset_seed"]),
            case_id=case.case_id,
        )
        coordinates, center, coordinate_scale = normalize_coordinates(
            case.coordinates[subset]
        )
        neighbors = knn_indices(coordinates, int(representation["knn"])).numpy()
        prepared[case.case_id] = {
            "case_id": case.case_id,
            "base_family": case.base_family,
            "split": case.split,
            "coordinates": coordinates,
            "velocity": np.asarray(case.velocity[:, subset], dtype=np.float32),
            "neighbors": neighbors,
            "coordinate_center": center,
            "coordinate_scale": coordinate_scale,
            "node_indices": subset,
        }
    return prepared


def _velocity_scale(prepared_train: Mapping[int, Mapping[str, Any]]) -> float:
    np, _, _ = _imports()
    total = 0.0
    count = 0
    for case in prepared_train.values():
        values = np.asarray(case["velocity"], dtype=np.float64)
        total += float(np.sum(values * values))
        count += int(values.size)
    scale = math.sqrt(total / max(count, 1))
    if not math.isfinite(scale) or scale <= 1e-12:
        raise AneumoISBIV1Error("Invalid train-only velocity scale.")
    return scale


def _normalize_condition(flows: Any) -> Any:
    np, _, _ = _imports()
    values = np.asarray(flows, dtype=np.float32)
    minimum, maximum = float(values.min()), float(values.max())
    return (2.0 * (values - minimum) / (maximum - minimum) - 1.0).astype(np.float32)


def _relative_l2(prediction: Any, target: Any) -> float:
    _, _, torch = _imports()
    numerator = torch.linalg.vector_norm((prediction - target).reshape(-1))
    denominator = torch.linalg.vector_norm(target.reshape(-1)).clamp_min(1e-12)
    return float((numerator / denominator).item())


def _field_distance(left: Any, right: Any) -> Any:
    _, _, torch = _imports()
    return torch.sqrt(torch.mean((left - right) ** 2, dim=(-2, -1)).clamp_min(1e-20))


def _functionals(field: Any) -> Any:
    _, _, torch = _imports()
    speed = torch.linalg.vector_norm(field, dim=-1)
    return torch.stack(
        [speed.mean(dim=-1), torch.sqrt((speed * speed).mean(dim=-1)),
         torch.quantile(speed, 0.95, dim=-1)],
        dim=-1,
    )


def _family_average(entries: Sequence[tuple[int, Any]]) -> Any:
    """Average within base family before averaging across families."""

    np, _, _ = _imports()
    grouped: dict[int, list[Any]] = {}
    for family, value in entries:
        grouped.setdefault(int(family), []).append(np.asarray(value, dtype=np.float64))
    if not grouped:
        raise AneumoISBIV1Error("Cannot aggregate an empty V1 validation metric.")
    family_means = [np.mean(grouped[family], axis=0) for family in sorted(grouped)]
    return np.mean(family_means, axis=0)


def _predict_validation(
    model: Any,
    prepared_validation: Mapping[int, Mapping[str, Any]],
    normalized_flows: Any,
    velocity_scale: float,
    *,
    device: Any,
    condition_zeroed: bool = False,
) -> tuple[dict[int, Any], float]:
    """Replay one checkpoint and return CPU predictions for registered q values."""

    _, _, torch = _imports()
    model.eval()
    predictions: dict[int, Any] = {}
    latency_seconds = 0.0
    calls = 0
    with torch.no_grad():
        for case_id in sorted(prepared_validation):
            case = prepared_validation[case_id]
            coordinates = torch.as_tensor(case["coordinates"], device=device)[None]
            neighbors = torch.as_tensor(
                case["neighbors"], dtype=torch.long, device=device
            )[None]
            case_predictions = []
            for normalized_flow in normalized_flows:
                value = 0.0 if condition_zeroed else float(normalized_flow)
                condition = torch.tensor([[value]], dtype=torch.float32, device=device)
                if device.type == "cuda":
                    torch.cuda.synchronize(device)
                started = time.perf_counter()
                prediction = model(coordinates, condition, neighbors)[0] * velocity_scale
                if device.type == "cuda":
                    torch.cuda.synchronize(device)
                latency_seconds += time.perf_counter() - started
                calls += 1
                case_predictions.append(prediction.detach().cpu())
            predictions[int(case_id)] = torch.stack(case_predictions, dim=0)
    return predictions, 1000.0 * latency_seconds / max(calls, 1)


def _summarize_predictions(
    prepared_validation: Mapping[int, Mapping[str, Any]],
    same_q_predictions: Mapping[int, Any],
    *,
    missing_predictions: Mapping[int, Any] | None = None,
    latency_ms_per_case_condition: float = 0.0,
    condition_zeroed: bool = False,
) -> dict[str, Any]:
    """Evaluate full-q and exact-design-law distributional metrics."""

    np, _, torch = _imports()
    missing_predictions = missing_predictions or same_q_predictions
    full_errors: list[tuple[int, float]] = []
    response_errors: list[tuple[int, float]] = []
    energy_scores: list[tuple[int, float]] = []
    functional_coverages: list[tuple[int, Any]] = []
    functional_widths: list[tuple[int, Any]] = []
    anchor_index = 3
    expected_cases = set(prepared_validation)
    if set(same_q_predictions) != expected_cases or set(missing_predictions) != expected_cases:
        raise AneumoISBIV1Error("V1 predictions do not cover every validation case.")
    for case_id in sorted(prepared_validation):
        case = prepared_validation[case_id]
        family = int(case["base_family"])
        target = torch.as_tensor(case["velocity"], dtype=torch.float32)
        prediction_stack = torch.as_tensor(
            same_q_predictions[case_id], dtype=torch.float32
        )
        predictive_distribution = torch.as_tensor(
            missing_predictions[case_id], dtype=torch.float32
        )
        if prediction_stack.shape != target.shape:
            raise AneumoISBIV1Error("V1 matching-q prediction shape changed.")
        if (
            predictive_distribution.ndim != 3
            or predictive_distribution.shape[1:] != target.shape[1:]
        ):
            raise AneumoISBIV1Error("V1 missing-distribution prediction shape changed.")
        for condition_index in range(target.shape[0]):
            full_errors.append(
                (family, _relative_l2(prediction_stack[condition_index], target[condition_index]))
            )
            if condition_index != anchor_index:
                response_errors.append(
                    (
                        family,
                        _relative_l2(
                            prediction_stack[condition_index]
                            - prediction_stack[anchor_index],
                            target[condition_index] - target[anchor_index],
                        ),
                    )
                )
        first = []
        for true_index in range(target.shape[0]):
            repeated = target[true_index][None].expand_as(predictive_distribution)
            first.append(_field_distance(predictive_distribution, repeated).mean())
        pair_distance = _field_distance(
            predictive_distribution[:, None, :, :],
            predictive_distribution[None, :, :, :],
        ).mean()
        energy_scores.append(
            (family, float((torch.stack(first).mean() - 0.5 * pair_distance).item()))
        )

        predicted_functionals = _functionals(predictive_distribution)
        true_functionals = _functionals(target)
        lower = torch.quantile(predicted_functionals, 0.05, dim=0)
        upper = torch.quantile(predicted_functionals, 0.95, dim=0)
        coverage = ((true_functionals >= lower) & (true_functionals <= upper)).float()
        functional_coverages.append((family, coverage.mean(dim=0).numpy()))
        functional_widths.append((family, (upper - lower).numpy()))
    return {
        "full_q_relative_l2": float(_family_average(full_errors)),
        "response_relative_l2": float(_family_average(response_errors)),
        "missing_field_energy_score_m_s": float(_family_average(energy_scores)),
        "functional_coverage_90": _family_average(functional_coverages).tolist(),
        "functional_interval_width_90_m_s": _family_average(functional_widths).tolist(),
        "latency_ms_per_case_condition": float(latency_ms_per_case_condition),
        "condition_zeroed": bool(condition_zeroed),
        "validation_cases": len(prepared_validation),
        "validation_base_families": len(
            {int(case["base_family"]) for case in prepared_validation.values()}
        ),
        "aggregation_unit": "aneux_base_family",
        "validation_fields_read": True,
        "test_fields_read": False,
    }


def evaluate(
    model: Any,
    prepared_validation: Mapping[int, Mapping[str, Any]],
    normalized_flows: Any,
    velocity_scale: float,
    *,
    device: Any,
    condition_zeroed: bool = False,
) -> dict[str, Any]:
    predictions, latency = _predict_validation(
        model,
        prepared_validation,
        normalized_flows,
        velocity_scale,
        device=device,
        condition_zeroed=condition_zeroed,
    )
    return _summarize_predictions(
        prepared_validation,
        predictions,
        latency_ms_per_case_condition=latency,
        condition_zeroed=condition_zeroed,
    )


def run_training(
    config: Mapping[str, Any],
    *,
    root: Path,
    cache: Path,
    output: Path,
    family: str,
    seed: int,
    git_commit: str,
    require_cuda: bool,
) -> dict[str, Any]:
    np, _, torch = _imports()
    if family not in config["models"]["families"]:
        raise AneumoISBIV1Error("Requested model family is not registered.")
    if int(seed) not in {int(item) for item in config["training"]["seeds"]}:
        raise AneumoISBIV1Error("Requested seed is not registered.")
    if _sha256(root / config["source"]["staging_config"]) != config["source"][
        "staging_config_sha256"
    ]:
        raise AneumoISBIV1Error("V1 staging dependency SHA-256 mismatch.")
    if _sha256(root / config["source"]["v0_result"]) != config["source"][
        "v0_result_sha256"
    ]:
        raise AneumoISBIV1Error("V1 V0-result dependency SHA-256 mismatch.")

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if require_cuda and device.type != "cuda":
        raise AneumoISBIV1Error("V1 requires a scheduler-allocated CUDA device.")
    torch.manual_seed(int(seed))
    if device.type == "cuda":
        torch.cuda.manual_seed_all(int(seed))
        torch.cuda.reset_peak_memory_stats(device)

    train_cases, validation_cases, flows = load_development_cases(config, cache)
    prepared_train = _prepare_cases(config, train_cases)
    prepared_validation = _prepare_cases(config, validation_cases)
    velocity_scale = _velocity_scale(prepared_train)
    normalized_flows = _normalize_condition(flows)

    model = build_model(config, family).to(device)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    training = config["training"]
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(training["learning_rate"]),
        weight_decay=float(training["weight_decay"]),
    )
    use_amp = bool(training["mixed_precision"] and device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    samples = [
        (case_id, condition_index)
        for case_id in sorted(prepared_train)
        for condition_index in range(len(normalized_flows))
    ]
    sample_generator = torch.Generator(device="cpu")
    sample_generator.manual_seed(int(seed) + 10_000)
    best_score = float("inf")
    best_step = 0
    best_state = None
    trace = []
    model.train()
    for step in range(1, int(training["steps"]) + 1):
        selected = torch.randint(
            0,
            len(samples),
            (int(training["batch_cases"]),),
            generator=sample_generator,
        ).tolist()
        batch_samples = [samples[index] for index in selected]
        coordinates = torch.stack(
            [
                torch.as_tensor(prepared_train[case]["coordinates"])
                for case, _ in batch_samples
            ]
        ).to(device)
        neighbors = torch.stack(
            [
                torch.as_tensor(
                    prepared_train[case]["neighbors"], dtype=torch.long
                )
                for case, _ in batch_samples
            ]
        ).to(device)
        conditions = torch.tensor(
            [[float(normalized_flows[index])] for _, index in batch_samples],
            dtype=torch.float32,
            device=device,
        )
        target = torch.stack(
            [
                torch.as_tensor(prepared_train[case]["velocity"][index])
                for case, index in batch_samples
            ]
        ).to(device) / velocity_scale
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            prediction = model(coordinates, conditions, neighbors)
            loss = torch.mean((prediction - target) ** 2)
        if not torch.isfinite(loss):
            raise AneumoISBIV1Error(f"Non-finite V1 loss at step {step}.")
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(
            model.parameters(), float(training["gradient_clip_norm"])
        )
        scaler.step(optimizer)
        scaler.update()

        if step % int(training["validation_every_steps"]) == 0:
            validation = evaluate(
                model,
                prepared_validation,
                normalized_flows,
                velocity_scale,
                device=device,
            )
            score = validation["full_q_relative_l2"] + validation[
                "response_relative_l2"
            ]
            trace.append(
                {
                    "step": step,
                    "train_loss": float(loss.detach().item()),
                    "selection_score": score,
                    **validation,
                }
            )
            if score < best_score:
                best_score = score
                best_step = step
                best_state = {
                    key: value.detach().cpu().clone()
                    for key, value in model.state_dict().items()
                }
            model.train()
    if best_state is None:
        raise AneumoISBIV1Error("V1 produced no validation checkpoint.")
    model.load_state_dict(best_state)
    final_metrics = evaluate(
        model,
        prepared_validation,
        normalized_flows,
        velocity_scale,
        device=device,
    )
    condition_zeroed = evaluate(
        model,
        prepared_validation,
        normalized_flows,
        velocity_scale,
        device=device,
        condition_zeroed=True,
    )
    output.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "model_state": best_state,
        "family": family,
        "seed": int(seed),
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "cache_sha256": config["source"]["cache_sha256"],
        "velocity_scale": velocity_scale,
        "condition_values": [float(item) for item in flows],
        "node_subset_seed": int(config["representation"]["node_subset_seed"]),
        "test_fields_read": False,
    }
    torch.save(checkpoint, output / "checkpoint.pt")
    result = {
        "schema_version": "aurora.aneumo_isbi_v1.task_result.v1",
        "experiment_id": config["experiment_id"],
        "family": family,
        "seed": int(seed),
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "cache_sha256": config["source"]["cache_sha256"],
        "device": str(device),
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "parameter_count": int(parameter_count),
        "velocity_scale_m_s": velocity_scale,
        "best_step": best_step,
        "selection_score": best_score,
        "metrics": final_metrics,
        "condition_zeroed_metrics": condition_zeroed,
        "condition_zeroing_worsens_full_q_error": bool(
            condition_zeroed["full_q_relative_l2"]
            > final_metrics["full_q_relative_l2"]
        ),
        "peak_gpu_memory_mb": (
            float(torch.cuda.max_memory_allocated(device) / (1024**2))
            if device.type == "cuda"
            else 0.0
        ),
        "field_access": {
            "train_fields_read": True,
            "validation_fields_read": True,
            "test_fields_read": False,
        },
        "authorization": config["authorization"],
        "trace": trace,
    }
    (output / "metrics.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "status.json").write_text(
        json.dumps(
            {"state": "complete", "exit_status": 0, "test_fields_read": False},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return result


def _all_numeric_values_finite(value: Any) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    if isinstance(value, Mapping):
        return all(_all_numeric_values_finite(item) for item in value.values())
    if isinstance(value, Sequence):
        return all(_all_numeric_values_finite(item) for item in value)
    return True


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise AneumoISBIV1Error("Cannot average an empty registered metric.")
    return float(sum(float(item) for item in values) / len(values))


def select_registered_family(
    config: Mapping[str, Any], task_results: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Apply the frozen lexicographic selector to per-seed task metrics only."""

    expected_seeds = sorted(int(item) for item in config["training"]["seeds"])
    expected_families = list(config["models"]["families"])
    indexed: dict[tuple[str, int], Mapping[str, Any]] = {}
    for result in task_results:
        key = (str(result["family"]), int(result["seed"]))
        if key in indexed:
            raise AneumoISBIV1Error(f"Duplicate V1 task result: {key}")
        indexed[key] = result
    expected = {
        (family, seed) for family in expected_families for seed in expected_seeds
    }
    if set(indexed) != expected:
        raise AneumoISBIV1Error("V1 selector requires the exact 4x3 factorial.")

    ranking = []
    for family in expected_families:
        family_results = [indexed[(family, seed)] for seed in expected_seeds]
        counts = {int(result["parameter_count"]) for result in family_results}
        if len(counts) != 1:
            raise AneumoISBIV1Error("V1 parameter count changed across seeds.")
        full = [float(result["metrics"]["full_q_relative_l2"]) for result in family_results]
        response = [
            float(result["metrics"]["response_relative_l2"])
            for result in family_results
        ]
        energy = [
            float(result["metrics"]["missing_field_energy_score_m_s"])
            for result in family_results
        ]
        row = {
            "family": family,
            "seeds": expected_seeds,
            "seed_mean_validation_response_relative_l2": _mean(response),
            "seed_worst_validation_response_relative_l2": max(response),
            "seed_mean_validation_full_q_relative_l2": _mean(full),
            "seed_worst_validation_full_q_relative_l2": max(full),
            "seed_mean_missing_field_energy_score_m_s": _mean(energy),
            "parameter_count": next(iter(counts)),
            "condition_zeroing_worsens_full_q_error_by_seed": [
                bool(result["condition_zeroing_worsens_full_q_error"])
                for result in family_results
            ],
        }
        row["registered_rank_tuple"] = [
            row["seed_mean_validation_response_relative_l2"],
            row["seed_mean_validation_full_q_relative_l2"],
            row["seed_mean_missing_field_energy_score_m_s"],
            row["parameter_count"],
        ]
        ranking.append(row)
    ranking.sort(key=lambda row: tuple(row["registered_rank_tuple"]))
    for index, row in enumerate(ranking, start=1):
        row["rank"] = index
    return {
        "selected_family": ranking[0]["family"],
        "rank_by": list(config["selector"]["rank_by"]),
        "uses_ensemble_metrics": False,
        "uses_response_oracle": False,
        "ranking": ranking,
    }


def evaluate_same_case_response_oracle(
    config: Mapping[str, Any],
    prepared_validation: Mapping[int, Mapping[str, Any]],
    flows: Any,
) -> dict[str, Any]:
    """Evaluate the registered validation-anchor scaling response control."""

    np, _, torch = _imports()
    oracle = config["controls"]["response_only_oracle"]
    flow_values = np.asarray(flows, dtype=np.float64)
    anchor_flow = float(oracle["anchor_mass_flow_kg_s"])
    matches = np.flatnonzero(np.isclose(flow_values, anchor_flow, rtol=0.0, atol=1e-12))
    if len(matches) != 1:
        raise AneumoISBIV1Error("The V1 response oracle anchor is not identifiable.")
    anchor_index = int(matches[0])
    power = float(oracle["power"])
    ratios = torch.as_tensor((flow_values / anchor_flow) ** power, dtype=torch.float32)
    errors: list[tuple[int, float]] = []
    for case_id in sorted(prepared_validation):
        case = prepared_validation[case_id]
        target = torch.as_tensor(case["velocity"], dtype=torch.float32)
        prediction = ratios[:, None, None] * target[anchor_index][None]
        for condition_index in range(target.shape[0]):
            if condition_index == anchor_index:
                continue
            errors.append(
                (
                    int(case["base_family"]),
                    _relative_l2(
                        prediction[condition_index] - prediction[anchor_index],
                        target[condition_index] - target[anchor_index],
                    ),
                )
            )
    return {
        "name": oracle["name"],
        "validation_response_relative_l2": float(_family_average(errors)),
        "anchor_mass_flow_kg_s": anchor_flow,
        "power": power,
        "uses_true_validation_anchor_field": True,
        "eligible_for_model_selection_or_gate": False,
        "eligible_endpoint": oracle["eligible_endpoint"],
        "validation_cases": len(prepared_validation),
        "validation_base_families": len(
            {int(case["base_family"]) for case in prepared_validation.values()}
        ),
        "test_fields_read": False,
    }


def evaluate_family_ensemble(
    config: Mapping[str, Any],
    prepared_validation: Mapping[int, Mapping[str, Any]],
    predictions_by_seed: Mapping[int, Mapping[int, Any]],
) -> dict[str, Any]:
    """Evaluate the frozen 3-seed x 8-condition predictive mixture."""

    _, _, torch = _imports()
    expected_seeds = sorted(int(item) for item in config["training"]["seeds"])
    if sorted(int(seed) for seed in predictions_by_seed) != expected_seeds:
        raise AneumoISBIV1Error("V1 ensemble requires exactly the three registered seeds.")
    same_q: dict[int, Any] = {}
    missing: dict[int, Any] = {}
    for case_id in sorted(prepared_validation):
        members = [predictions_by_seed[seed][case_id] for seed in expected_seeds]
        stack = torch.stack(members, dim=0)
        same_q[case_id] = stack.mean(dim=0)
        missing[case_id] = stack.reshape(-1, *stack.shape[2:])
    result = _summarize_predictions(
        prepared_validation,
        same_q,
        missing_predictions=missing,
    )
    result.update(
        {
            "ensemble_members": len(expected_seeds),
            "registered_conditions": len(config["task"]["condition_values"]),
            "missing_predictive_components": len(expected_seeds)
            * len(config["task"]["condition_values"]),
            "full_q_point_prediction": config["models"]["deep_ensemble"][
                "full_q_point_prediction"
            ],
            "missing_predictive_distribution": config["models"]["deep_ensemble"][
                "missing_predictive_distribution"
            ],
            "eligible_for_selector": False,
            "supports_uncertainty_separation_claim": False,
        }
    )
    return result


def _metric_close(left: Any, right: Any, tolerance: float) -> bool:
    if isinstance(left, Sequence) and not isinstance(left, (str, bytes)):
        return (
            isinstance(right, Sequence)
            and not isinstance(right, (str, bytes))
            and len(left) == len(right)
            and all(_metric_close(a, b, tolerance) for a, b in zip(left, right))
        )
    try:
        return abs(float(left) - float(right)) <= tolerance
    except (TypeError, ValueError):
        return left == right


def _checkpoint_is_validation_selected(result: Mapping[str, Any], tolerance: float) -> bool:
    trace = result.get("trace", [])
    if not trace:
        return False
    best = min(trace, key=lambda item: float(item["selection_score"]))
    final_score = float(result["metrics"]["full_q_relative_l2"]) + float(
        result["metrics"]["response_relative_l2"]
    )
    return (
        int(best["step"]) == int(result["best_step"])
        and abs(float(best["selection_score"]) - float(result["selection_score"]))
        <= tolerance
        and abs(final_score - float(result["selection_score"])) <= tolerance
        and result["field_access"].get("test_fields_read") is False
    )


def _load_registered_task_results(
    config: Mapping[str, Any],
    task_output_root: Path,
    git_commit: str,
) -> tuple[list[dict[str, Any]], dict[tuple[str, int], dict[str, Any]]]:
    results = []
    artifacts: dict[tuple[str, int], dict[str, Any]] = {}
    template = config["aggregation"]["required_task_directory_template"]
    expected_config_sha = config["_config_sha256"]
    for family in config["models"]["families"]:
        for seed_value in config["training"]["seeds"]:
            seed = int(seed_value)
            directory = task_output_root / template.format(family=family, seed=seed)
            status_path = directory / "status.json"
            metrics_path = directory / "metrics.json"
            checkpoint_path = directory / "checkpoint.pt"
            if (
                not status_path.is_file()
                or not metrics_path.is_file()
                or not checkpoint_path.is_file()
            ):
                raise AneumoISBIV1Error(f"Incomplete registered V1 task: {family}/{seed}")
            status = json.loads(status_path.read_text(encoding="utf-8"))
            result = json.loads(metrics_path.read_text(encoding="utf-8"))
            if status != {"exit_status": 0, "state": "complete", "test_fields_read": False}:
                raise AneumoISBIV1Error(
                    f"Registered V1 task did not exit cleanly: {family}/{seed}"
                )
            if (
                result.get("family") != family
                or int(result.get("seed", -1)) != seed
                or result.get("git_commit") != git_commit
                or result.get("config_sha256") != expected_config_sha
                or result.get("cache_sha256") != config["source"]["cache_sha256"]
            ):
                raise AneumoISBIV1Error(f"V1 task provenance mismatch: {family}/{seed}")
            results.append(result)
            artifacts[(family, seed)] = {
                "directory": directory,
                "checkpoint_path": checkpoint_path,
                "metrics_sha256": _sha256(metrics_path),
                "checkpoint_sha256": _sha256(checkpoint_path),
                "status_sha256": _sha256(status_path),
            }
    return results, artifacts


def aggregate_training_outputs(
    config: Mapping[str, Any],
    *,
    root: Path,
    cache: Path,
    task_output_root: Path,
    output: Path,
    git_commit: str,
    require_cuda: bool,
) -> dict[str, Any]:
    """Replay all V1 checkpoints, aggregate the selector, and evaluate the gate."""

    _, _, torch = _imports()
    if _sha256(root / config["source"]["staging_config"]) != config["source"][
        "staging_config_sha256"
    ]:
        raise AneumoISBIV1Error("V1 aggregation staging dependency mismatch.")
    if _sha256(root / config["source"]["v0_result"]) != config["source"][
        "v0_result_sha256"
    ]:
        raise AneumoISBIV1Error("V1 aggregation V0 dependency mismatch.")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if require_cuda and device.type != "cuda":
        raise AneumoISBIV1Error("V1 aggregation requires a scheduler CUDA device.")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    task_results, artifacts = _load_registered_task_results(
        config, task_output_root, git_commit
    )
    train_cases, validation_cases, flows = load_development_cases(config, cache)
    prepared_train = _prepare_cases(config, train_cases)
    prepared_validation = _prepare_cases(config, validation_cases)
    velocity_scale = _velocity_scale(prepared_train)
    normalized_flows = _normalize_condition(flows)
    tolerance = float(config["aggregation"]["checkpoint_replay_absolute_tolerance"])
    replay_keys = (
        "full_q_relative_l2",
        "response_relative_l2",
        "missing_field_energy_score_m_s",
        "functional_coverage_90",
        "functional_interval_width_90_m_s",
    )
    predictions: dict[str, dict[int, dict[int, Any]]] = {
        family: {} for family in config["models"]["families"]
    }
    checkpoint_metadata_valid = True
    checkpoint_replay_valid = True
    for result in task_results:
        family = str(result["family"])
        seed = int(result["seed"])
        checkpoint = torch.load(
            artifacts[(family, seed)]["checkpoint_path"],
            map_location="cpu",
            weights_only=False,
        )
        checkpoint_metadata_valid = checkpoint_metadata_valid and (
            checkpoint.get("family") == family
            and int(checkpoint.get("seed", -1)) == seed
            and checkpoint.get("git_commit") == git_commit
            and checkpoint.get("config_sha256") == config["_config_sha256"]
            and checkpoint.get("cache_sha256") == config["source"]["cache_sha256"]
            and checkpoint.get("test_fields_read") is False
            and abs(float(checkpoint.get("velocity_scale", float("nan"))) - velocity_scale)
            <= 1e-12
        )
        model = build_model(config, family).to(device)
        actual_parameter_count = sum(
            parameter.numel() for parameter in model.parameters()
        )
        checkpoint_metadata_valid = checkpoint_metadata_valid and (
            actual_parameter_count == int(result["parameter_count"])
        )
        model.load_state_dict(checkpoint["model_state"], strict=True)
        predicted, _ = _predict_validation(
            model,
            prepared_validation,
            normalized_flows,
            velocity_scale,
            device=device,
        )
        replay = _summarize_predictions(prepared_validation, predicted)
        checkpoint_replay_valid = checkpoint_replay_valid and all(
            _metric_close(replay[key], result["metrics"][key], tolerance)
            for key in replay_keys
        )
        predictions[family][seed] = predicted
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    selection = select_registered_family(config, task_results)
    ensembles = {
        family: evaluate_family_ensemble(
            config, prepared_validation, predictions[family]
        )
        for family in config["models"]["families"]
    }
    response_oracle = evaluate_same_case_response_oracle(
        config, prepared_validation, flows
    )
    selected = next(
        row
        for row in selection["ranking"]
        if row["family"] == selection["selected_family"]
    )
    validation_selected = all(
        _checkpoint_is_validation_selected(result, tolerance) for result in task_results
    )
    no_test_read = all(
        result["field_access"].get("test_fields_read") is False
        and result["metrics"].get("test_fields_read") is False
        and result["condition_zeroed_metrics"].get("test_fields_read") is False
        for result in task_results
    ) and response_oracle["test_fields_read"] is False
    finite = all(
        _all_numeric_values_finite(result["metrics"])
        and _all_numeric_values_finite(result["condition_zeroed_metrics"])
        for result in task_results
    ) and _all_numeric_values_finite(ensembles) and _all_numeric_values_finite(response_oracle)
    selected_results = [
        result
        for result in task_results
        if result["family"] == selection["selected_family"]
    ]
    gate_checks = {
        "all_twelve_tasks_exit_zero": len(task_results) == 12,
        "no_test_field_read": no_test_read,
        "all_metrics_finite": finite,
        "all_checkpoints_selected_on_validation_only": (
            validation_selected and checkpoint_metadata_valid and checkpoint_replay_valid
        ),
        "selected_model_worst_seed_full_q_relative_l2_at_most_0.35": (
            float(selected["seed_worst_validation_full_q_relative_l2"]) <= 0.35
        ),
        "selected_model_worst_seed_response_relative_l2_at_most_0.50": (
            float(selected["seed_worst_validation_response_relative_l2"]) <= 0.50
        ),
        "condition_zeroing_worsens_full_q_error_in_all_selected_model_seeds": all(
            bool(result["condition_zeroing_worsens_full_q_error"])
            for result in selected_results
        ),
    }
    if list(gate_checks) != list(config["feasibility_gate"]["checks"]):
        raise AneumoISBIV1Error("V1 implementation and gate check order disagree.")
    parameter_counts = [int(row["parameter_count"]) for row in selection["ranking"]]
    relative_parameter_range = (max(parameter_counts) - min(parameter_counts)) / max(
        parameter_counts
    )
    if relative_parameter_range > float(
        config["models"]["parameter_match_relative_tolerance"]
    ):
        raise AneumoISBIV1Error("V1 execution violated the frozen parameter match.")
    passed = all(gate_checks.values())
    task_manifest = []
    for result in sorted(task_results, key=lambda item: (item["family"], item["seed"])):
        key = (str(result["family"]), int(result["seed"]))
        task_manifest.append(
            {
                "family": key[0],
                "seed": key[1],
                "metrics_sha256": artifacts[key]["metrics_sha256"],
                "checkpoint_sha256": artifacts[key]["checkpoint_sha256"],
                "status_sha256": artifacts[key]["status_sha256"],
                "best_step": int(result["best_step"]),
                "parameter_count": int(result["parameter_count"]),
                "test_fields_read": False,
            }
        )
    aggregate = {
        "schema_version": "aurora.aneumo_isbi_v1.aggregate.v1",
        "experiment_id": config["experiment_id"],
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "cache_sha256": config["source"]["cache_sha256"],
        "task_count": len(task_results),
        "selection": selection,
        "deep_ensemble_validation_metrics": ensembles,
        "response_only_oracle": response_oracle,
        "integrity": {
            "exact_four_family_by_three_seed_factorial": len(task_results) == 12,
            "checkpoint_metadata_valid": checkpoint_metadata_valid,
            "checkpoint_validation_replay_within_tolerance": checkpoint_replay_valid,
            "checkpoint_replay_absolute_tolerance": tolerance,
            "parameter_counts": parameter_counts,
            "relative_parameter_range": relative_parameter_range,
            "parameter_match_tolerance": float(
                config["models"]["parameter_match_relative_tolerance"]
            ),
        },
        "gate": {
            "checks": gate_checks,
            "passed_checks": sum(bool(value) for value in gate_checks.values()),
            "total_checks": len(gate_checks),
            "all_checks_passed": passed,
            "decision": (
                config["authorization"]["pass_allows"]
                if passed
                else config["feasibility_gate"]["failure_action"]
            ),
        },
        "field_access": {
            "train_fields_read": True,
            "validation_fields_read": True,
            "test_fields_read": False,
            "test_metrics_or_selection": False,
        },
        "environment": {
            "aggregation_device": str(device),
            "torch": torch.__version__,
            "cuda_runtime": torch.version.cuda,
            "task_devices": sorted({str(result["device"]) for result in task_results}),
            "task_torch_versions": sorted({str(result["torch"]) for result in task_results}),
            "task_cuda_runtimes": sorted(
                {str(result["cuda_runtime"]) for result in task_results}
            ),
            "peak_gpu_memory_mb": (
                float(torch.cuda.max_memory_allocated(device) / (1024**2))
                if device.type == "cuda"
                else 0.0
            ),
        },
        "task_manifest": task_manifest,
        "authorization": config["authorization"],
        "interpretation": {
            "development_only": True,
            "selected_backbone_is_method_novelty": False,
            "response_oracle_is_reconstruction_baseline": False,
            "ensemble_supports_uncertainty_separation": False,
            "outer_test_authorized": False,
            "isbi_submission_evidence": False,
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "aggregate.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "status.json").write_text(
        json.dumps(
            {
                "state": "complete",
                "exit_status": 0,
                "gate_passed": passed,
                "test_fields_read": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return aggregate


def aggregate_main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate the preregistered Aneumo ISBI V1 tasks."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--task-output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    result = aggregate_training_outputs(
        config,
        root=args.root,
        cache=args.cache,
        task_output_root=args.task_output_root,
        output=args.output,
        git_commit=args.git_commit,
        require_cuda=args.require_cuda,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    result = run_training(
        config,
        root=args.root,
        cache=args.cache,
        output=args.output,
        family=args.family,
        seed=args.seed,
        git_commit=args.git_commit,
        require_cuda=args.require_cuda,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
