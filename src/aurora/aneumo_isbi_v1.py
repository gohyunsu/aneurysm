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
    expected_models = {
        "q_pointnet",
        "knn_mgn",
        "deltaphi_graph",
        "anchor_token_equivariant",
    }
    if set(models["families"]) != expected_models:
        raise AneumoISBIV1Error("V1 model families cannot change after registration.")
    if models.get("candidate_is_method_novelty") is not False:
        raise AneumoISBIV1Error("The engineering backbone is not method novelty.")
    training = payload["training"]
    if (
        len(training["seeds"]) != 3
        or training.get("paired_response_loss_weight") != 0.0
        or training.get("require_cuda") is not True
    ):
        raise AneumoISBIV1Error("V1 keeps three seeds and zero paired-loss weight.")
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


def evaluate(
    model: Any,
    prepared_validation: Mapping[int, Mapping[str, Any]],
    normalized_flows: Any,
    velocity_scale: float,
    *,
    device: Any,
    condition_zeroed: bool = False,
) -> dict[str, Any]:
    np, _, torch = _imports()
    model.eval()
    full_errors = []
    response_errors = []
    energy_scores = []
    functional_coverages = []
    functional_widths = []
    latency_seconds = 0.0
    calls = 0
    with torch.no_grad():
        for case_id in sorted(prepared_validation):
            case = prepared_validation[case_id]
            coordinates = torch.as_tensor(case["coordinates"], device=device)[None]
            neighbors = torch.as_tensor(
                case["neighbors"], dtype=torch.long, device=device
            )[None]
            target = torch.as_tensor(case["velocity"], device=device)
            predictions = []
            for condition_index, normalized_flow in enumerate(normalized_flows):
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
                predictions.append(prediction)
                full_errors.append(_relative_l2(prediction, target[condition_index]))
            prediction_stack = torch.stack(predictions, dim=0)
            anchor_index = 3
            for index in range(target.shape[0]):
                if index == anchor_index:
                    continue
                response_errors.append(
                    _relative_l2(
                        prediction_stack[index] - prediction_stack[anchor_index],
                        target[index] - target[anchor_index],
                    )
                )
            first = []
            for true_index in range(target.shape[0]):
                repeated = target[true_index][None].expand_as(prediction_stack)
                first.append(_field_distance(prediction_stack, repeated).mean())
            pair_distance = _field_distance(
                prediction_stack[:, None, :, :], prediction_stack[None, :, :, :]
            ).mean()
            energy_scores.append(float((torch.stack(first).mean() - 0.5 * pair_distance).item()))

            predicted_functionals = _functionals(prediction_stack)
            true_functionals = _functionals(target)
            lower = torch.quantile(predicted_functionals, 0.05, dim=0)
            upper = torch.quantile(predicted_functionals, 0.95, dim=0)
            coverage = ((true_functionals >= lower) & (true_functionals <= upper)).float()
            functional_coverages.append(coverage.mean(dim=0).cpu().numpy())
            functional_widths.append((upper - lower).cpu().numpy())
    return {
        "full_q_relative_l2": float(np.mean(full_errors)),
        "response_relative_l2": float(np.mean(response_errors)),
        "missing_field_energy_score_m_s": float(np.mean(energy_scores)),
        "functional_coverage_90": np.mean(functional_coverages, axis=0).tolist(),
        "functional_interval_width_90_m_s": np.mean(
            functional_widths, axis=0
        ).tolist(),
        "latency_ms_per_case_condition": 1000.0 * latency_seconds / max(calls, 1),
        "condition_zeroed": bool(condition_zeroed),
        "validation_cases": len(prepared_validation),
        "validation_or_test_fields_read": False,
        "test_fields_read": False,
    }


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
