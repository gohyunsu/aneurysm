"""Prospective boundary-aware known-condition qualification for Aneumo V1e."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_isbi_v1c_boundary_geometry import _attribute_text, _imports, _sha256


class AneumoV1eKnownConditionError(RuntimeError):
    """Raised when the frozen V1e contract is violated."""


PRIMARY = "boundary_perceiver_operator"
CONTROL = "geometry_only_token_matched_perceiver_operator"
SEEDS = [821101, 821102, 821103]
VARIANTS = [PRIMARY, CONTROL]


def _torch_imports() -> tuple[Any, Any]:
    try:
        import torch
        from torch import nn
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoV1eKnownConditionError("V1e requires PyTorch.") from exc
    return torch, nn


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneumo_isbi_v1e_known_condition_baseline.v1":
        raise AneumoV1eKnownConditionError("Unexpected V1e schema version.")
    if payload.get("status") != (
        "preregistered_after_v1d_pass_before_any_v1e_training_or_checkpoint"
    ):
        raise AneumoV1eKnownConditionError("V1e must remain prospective to training.")
    source = payload.get("source", {})
    if source != {
        "dataset": "Aneumo",
        "license": "CC-BY-NC-ND-4.0",
        "pilot_config": "configs/aneumo_g2_pilot_v1.json",
        "pilot_config_sha256": (
            "f2b027c5f14107531ac1ae33eafab76513bcbdf49ad908c9a35641ae80181b7d"
        ),
        "compact_cache_sha256": (
            "9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9"
        ),
        "v1d_result": "results/aneumo_isbi_v1d_development_geometry_cache_20260808.json",
        "v1d_result_sha256": "051a722cb96ca1adb4f7eb4997d9f4dc96f5c84c04fb295e4aa489be7ff1b0db",
        "v1d_private_geometry_cache_sha256": (
            "ea524be495061c876124c8541c35e513ce6029a9732899f16a052373d9db340f"
        ),
    }:
        raise AneumoV1eKnownConditionError("V1e source changed.")
    access = payload.get("access", {})
    if (
        access.get("splits") != ["train", "validation"]
        or access.get("expected_cases_by_split")
        != {"train": 40, "validation": 12, "test": 0}
        or access.get("compact_cache_datasets_read")
        != [
            "coordinates_m",
            "mass_flows_kg_s",
            "pressure_velocity_velocity_channels_only",
        ]
        or access.get("private_geometry_cache_datasets_read")
        != ["inlet", "outlet", "wall"]
        or access.get("pressure_channel_read") is not False
        or access.get("validation_used_for_checkpoint_selection") is not True
        or access.get("test_geometry_or_field_read") is not False
        or access.get("test_metric_computed") is not False
    ):
        raise AneumoV1eKnownConditionError("V1e access boundary changed.")
    task = payload.get("task", {})
    if task != {
        "condition": "fully_observed_scalar_mass_flow",
        "output": "steady_volume_velocity_vector",
        "query_nodes_per_case": 4096,
        "conditions_per_case": 8,
        "training_examples": 320,
        "validation_examples": 96,
        "missing_or_partial_condition_evaluated": False,
        "clinical_endpoint_evaluated": False,
    }:
        raise AneumoV1eKnownConditionError("V1e task changed.")
    representation = payload.get("representation", {})
    if (
        representation.get("coordinate_normalization")
        != "per_case_compact_query_centroid_and_rms_radius"
        or representation.get("condition_normalization")
        != "exact_eight_flow_design_law_mean_and_standard_deviation"
        or representation.get("velocity_normalization") != "train_split_scalar_rms"
        or representation.get("interior_geometry_tokens_boundary_variant") != 128
        or representation.get("boundary_tokens_per_patch") != 64
        or representation.get("total_source_tokens_per_case") != 320
        or representation.get("interior_geometry_tokens_control_variant") != 320
        or representation.get("token_selection")
        != "deterministic_farthest_point_sampling_in_normalized_coordinates"
        or representation.get("boundary_token_features")
        != [
            "normalized_xyz",
            "token_type_one_hot_interior_inlet_outlet_wall",
            "patch_outward_normal",
            "normalized_mass_flow",
            "log_patch_area_over_case_radius_squared",
        ]
        or representation.get("query_features")
        != ["normalized_xyz", "normalized_mass_flow"]
        or representation.get("rotation_augmentation")
        != (
            "seeded_uniform_proper_rotation_applied_to_coordinates_normals_"
            "and_velocity_train_only"
        )
    ):
        raise AneumoV1eKnownConditionError("V1e representation changed.")
    models = payload.get("models", {})
    if (
        models.get("primary") != PRIMARY
        or models.get("control") != CONTROL
        or models.get("architecture_role")
        != "known_condition_engineering_baseline_not_method_novelty"
        or models.get("shared_parameterization")
        != {
            "hidden_dim": 128,
            "latent_tokens": 64,
            "attention_heads": 8,
            "latent_self_attention_layers": 4,
            "mlp_ratio": 2,
            "dropout": 0.0,
            "query_chunk_size": 1024,
        }
        or models.get("parameter_count_must_match_exactly") is not True
        or models.get("source_token_count_must_match_exactly") is not True
        or models.get("historical_v1_models_are_retrained_or_tuned") is not False
        or models.get("paired_response_loss_weight") != 0.0
    ):
        raise AneumoV1eKnownConditionError("V1e model contract changed.")
    training = payload.get("training", {})
    if training != {
        "seeds": SEEDS,
        "variants": VARIANTS,
        "tasks": 6,
        "steps": 8000,
        "batch_cases": 2,
        "train_query_nodes_per_example": 2048,
        "optimizer": "adamw",
        "learning_rate": 0.0002,
        "weight_decay": 0.0001,
        "warmup_steps": 400,
        "schedule": "cosine_to_zero",
        "gradient_clip_norm": 1.0,
        "validation_every_steps": 400,
        "checkpoint_selection": (
            "minimum_validation_mean_of_full_q_and_reference_paired_response_relative_l2"
        ),
        "loss": "train_scalar_rms_normalized_velocity_mse",
        "mixed_precision": True,
        "require_cuda": True,
    }:
        raise AneumoV1eKnownConditionError("V1e training contract changed.")
    if payload.get("evaluation") != {
        "reference_flow_kg_s": 0.0025,
        "metrics": [
            "train_full_q_relative_l2_at_selected_checkpoint",
            "validation_full_q_relative_l2",
            "validation_reference_paired_response_relative_l2",
            "validation_prediction_target_norm_ratio",
            "validation_vector_cosine",
            "parameter_count",
            "source_token_count",
        ],
        "selection_split": "validation_only",
        "seed_aggregation": "mean_and_worst_seed",
        "no_test_access": True,
    }:
        raise AneumoV1eKnownConditionError("V1e evaluation contract changed.")
    expected_checks = [
        "pinned_data_and_geometry_cache_integrity",
        "all_six_gpu_tasks_exit_zero_with_eligible_validation_selected_checkpoints",
        "exact_parameter_and_source_token_match_between_variants",
        "no_pressure_missing_partial_test_or_clinical_access",
        "boundary_worst_seed_train_full_q_relative_l2_at_most_0.25",
        "boundary_worst_seed_validation_full_q_relative_l2_at_most_0.35",
        "boundary_worst_seed_validation_paired_response_relative_l2_at_most_0.50",
        (
            "boundary_better_than_geometry_control_on_both_primary_metrics_"
            "in_at_least_two_of_three_seeds"
        ),
        "boundary_seed_mean_relative_improvement_at_least_0.05_on_both_primary_metrics",
    ]
    gate = payload.get("gate", {})
    if (
        gate.get("rule") != "all_registered_checks"
        or gate.get("checks") != expected_checks
        or gate.get("thresholds")
        != {
            "maximum_worst_seed_train_full_q_relative_l2": 0.25,
            "maximum_worst_seed_validation_full_q_relative_l2": 0.35,
            "maximum_worst_seed_validation_paired_response_relative_l2": 0.50,
            "minimum_better_seeds_each_primary_metric": 2,
            "minimum_seed_mean_relative_improvement_each_primary_metric": 0.05,
        }
        or gate.get("pass_authorizes")
        != "register_boundary_aware_scalar_missing_inflow_development_protocol_only"
        or gate.get("failure_action")
        != (
            "stop_the_current_aneumo_3d_learning_line_without_local_"
            "architecture_loss_step_seed_or_threshold_repair"
        )
        or gate.get("local_repair_allowed") is not False
        or set(gate.get("pass_does_not_authorize", []))
        != {
            "relabel_v1",
            "reuse_or_tune_v1_backbones",
            "test_geometry_or_field_access",
            "v2_outer_test",
            "partial_multicomponent_claim",
            "method_novelty",
            "isbi_submission",
        }
    ):
        raise AneumoV1eKnownConditionError("V1e cannot authorize test or novelty.")
    if (
        payload.get("interpretation")
        != (
            "known_condition_learnability_and_boundary_asset_utility_not_"
            "partial_missing_method_or_novelty_evidence"
        )
    ):
        raise AneumoV1eKnownConditionError("V1e interpretation changed.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


@dataclass(frozen=True)
class CaseData:
    case: int
    split: str
    coordinates: Any
    velocity: Any
    patches: Mapping[str, Mapping[str, Any]]


def load_cases(compact_cache: Path, geometry_cache: Path) -> tuple[Any, list[CaseData]]:
    np, h5py = _imports()
    cases: list[CaseData] = []
    with h5py.File(compact_cache, "r") as compact, h5py.File(
        geometry_cache, "r"
    ) as geometry:
        flows = np.asarray(compact["mass_flows_kg_s"], dtype=np.float64)
        if flows.shape != (8,) or not np.all(np.diff(flows) > 0):
            raise AneumoV1eKnownConditionError("V1e mass-flow design changed.")
        for case_key in sorted(geometry["cases"].keys(), key=int):
            boundary_group = geometry["cases"][case_key]
            split = _attribute_text(boundary_group.attrs["split"])
            if split not in {"train", "validation"}:
                raise AneumoV1eKnownConditionError("V1e geometry cache exposed test data.")
            compact_group = compact["geometries"][case_key]
            if _attribute_text(compact_group.attrs["split"]) != split:
                raise AneumoV1eKnownConditionError("V1e compact/geometry split mismatch.")
            coordinates = np.asarray(compact_group["coordinates_m"], dtype=np.float32)
            velocity = np.asarray(
                compact_group["pressure_velocity"][:, :, 1:4], dtype=np.float32
            )
            if coordinates.shape != (4096, 3) or velocity.shape != (8, 4096, 3):
                raise AneumoV1eKnownConditionError("V1e compact tensor shape changed.")
            patches = {}
            for patch in ("inlet", "outlet", "wall"):
                group = boundary_group[patch]
                patches[patch] = {
                    "points": np.asarray(group["points_m"], dtype=np.float32),
                    "normal": np.asarray(group.attrs["outward_normal"], dtype=np.float32),
                    "area": float(group.attrs["area_m2"]),
                }
            cases.append(
                CaseData(
                    case=int(case_key),
                    split=split,
                    coordinates=coordinates,
                    velocity=velocity,
                    patches=patches,
                )
            )
    counts = {
        split: sum(case.split == split for case in cases)
        for split in ("train", "validation")
    }
    if counts != {"train": 40, "validation": 12}:
        raise AneumoV1eKnownConditionError("V1e development split count changed.")
    return flows, cases


def farthest_point_indices(points: Any, count: int) -> Any:
    np, _ = _imports()
    points64 = np.asarray(points, dtype=np.float64)
    if points64.ndim != 2 or points64.shape[1] != 3 or len(points64) < count:
        raise AneumoV1eKnownConditionError("Invalid V1e farthest-point request.")
    selected = np.empty(count, dtype=np.int64)
    selected[0] = int(np.argmin(np.sum(points64 * points64, axis=1)))
    distances = np.sum((points64 - points64[selected[0]]) ** 2, axis=1)
    for index in range(1, count):
        selected[index] = int(np.argmax(distances))
        candidate = np.sum((points64 - points64[selected[index]]) ** 2, axis=1)
        distances = np.minimum(distances, candidate)
    return selected


def normalize_case(case: CaseData) -> dict[str, Any]:
    np, _ = _imports()
    coordinates = np.asarray(case.coordinates, dtype=np.float64)
    center = np.mean(coordinates, axis=0)
    centered = coordinates - center
    radius = float(np.sqrt(np.mean(np.sum(centered * centered, axis=1))))
    if not math.isfinite(radius) or radius <= 1e-12:
        raise AneumoV1eKnownConditionError("Invalid V1e case radius.")
    normalized_coordinates = (centered / radius).astype(np.float32)
    interior_320 = farthest_point_indices(normalized_coordinates, 320)
    interior_128 = interior_320[:128]
    normalized_patches = {}
    for patch, values in case.patches.items():
        points = ((np.asarray(values["points"], dtype=np.float64) - center) / radius).astype(
            np.float32
        )
        indices = farthest_point_indices(points, 64)
        normalized_patches[patch] = {
            "points": points[indices],
            "normal": np.asarray(values["normal"], dtype=np.float32),
            "log_area": float(math.log(max(float(values["area"]) / (radius * radius), 1e-12))),
        }
    return {
        "case": case.case,
        "split": case.split,
        "coordinates": normalized_coordinates,
        "velocity": np.asarray(case.velocity, dtype=np.float32),
        "interior_128": normalized_coordinates[interior_128],
        "interior_320": normalized_coordinates[interior_320],
        "patches": normalized_patches,
    }


def velocity_scale(prepared: Sequence[Mapping[str, Any]]) -> float:
    np, _ = _imports()
    train = [case for case in prepared if case["split"] == "train"]
    total = sum(
        float(np.sum(np.asarray(case["velocity"], dtype=np.float64) ** 2))
        for case in train
    )
    count = sum(int(np.asarray(case["velocity"]).size) for case in train)
    scale = math.sqrt(total / max(count, 1))
    if not math.isfinite(scale) or scale <= 1e-12:
        raise AneumoV1eKnownConditionError("Invalid V1e velocity scale.")
    return scale


def source_features(
    case: Mapping[str, Any], variant: str, normalized_flow: float
) -> Any:
    np, _ = _imports()
    rows = []

    def make(points: Any, type_index: int, normal: Any, log_area: float) -> Any:
        features = np.zeros((len(points), 12), dtype=np.float32)
        features[:, :3] = points
        features[:, 3 + type_index] = 1.0
        features[:, 7:10] = normal
        features[:, 10] = normalized_flow
        features[:, 11] = log_area
        return features

    if variant == PRIMARY:
        rows.append(
            make(case["interior_128"], 0, np.zeros(3, dtype=np.float32), 0.0)
        )
        for type_index, patch in enumerate(("inlet", "outlet", "wall"), start=1):
            values = case["patches"][patch]
            rows.append(
                make(values["points"], type_index, values["normal"], values["log_area"])
            )
    elif variant == CONTROL:
        rows.append(
            make(case["interior_320"], 0, np.zeros(3, dtype=np.float32), 0.0)
        )
    else:
        raise AneumoV1eKnownConditionError(f"Unknown V1e variant: {variant}")
    source = np.concatenate(rows, axis=0)
    if source.shape != (320, 12):
        raise AneumoV1eKnownConditionError("V1e source-token budget changed.")
    return source


def query_features(coordinates: Any, normalized_flow: float) -> Any:
    np, _ = _imports()
    queries = np.empty((len(coordinates), 4), dtype=np.float32)
    queries[:, :3] = coordinates
    queries[:, 3] = normalized_flow
    return queries


def uniform_rotation(rng: Any) -> Any:
    np, _ = _imports()
    u1, u2, u3 = rng.random(3)
    quaternion = np.asarray(
        [
            math.sqrt(1.0 - u1) * math.sin(2.0 * math.pi * u2),
            math.sqrt(1.0 - u1) * math.cos(2.0 * math.pi * u2),
            math.sqrt(u1) * math.sin(2.0 * math.pi * u3),
            math.sqrt(u1) * math.cos(2.0 * math.pi * u3),
        ],
        dtype=np.float64,
    )
    x, y, z, w = quaternion
    rotation = np.asarray(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=np.float32,
    )
    if (
        not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-6)
        or np.linalg.det(rotation) < 0.999
    ):
        raise AneumoV1eKnownConditionError("V1e rotation generation failed.")
    return rotation


def apply_rotation(
    source: Any, queries: Any, target: Any, rotation: Any
) -> tuple[Any, Any, Any]:
    source_rotated = source.copy()
    query_rotated = queries.copy()
    target_rotated = target.copy()
    source_rotated[:, :3] = source_rotated[:, :3] @ rotation.T
    source_rotated[:, 7:10] = source_rotated[:, 7:10] @ rotation.T
    query_rotated[:, :3] = query_rotated[:, :3] @ rotation.T
    target_rotated[:] = target_rotated @ rotation.T
    return source_rotated, query_rotated, target_rotated


def build_model(config: Mapping[str, Any]) -> Any:
    torch, nn = _torch_imports()
    spec = config["models"]["shared_parameterization"]
    hidden = int(spec["hidden_dim"])
    heads = int(spec["attention_heads"])
    mlp_hidden = hidden * int(spec["mlp_ratio"])

    class LatentBlock(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.norm_attention = nn.LayerNorm(hidden)
            self.attention = nn.MultiheadAttention(
                hidden, heads, dropout=float(spec["dropout"]), batch_first=True
            )
            self.norm_mlp = nn.LayerNorm(hidden)
            self.mlp = nn.Sequential(
                nn.Linear(hidden, mlp_hidden),
                nn.GELU(),
                nn.Linear(mlp_hidden, hidden),
            )

        def forward(self, values: Any) -> Any:
            normalized = self.norm_attention(values)
            update = self.attention(
                normalized, normalized, normalized, need_weights=False
            )[0]
            values = values + update
            return values + self.mlp(self.norm_mlp(values))

    class PerceiverOperator(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.source = nn.Sequential(
                nn.Linear(12, hidden), nn.GELU(), nn.Linear(hidden, hidden)
            )
            self.latents = nn.Parameter(
                torch.randn(int(spec["latent_tokens"]), hidden) / math.sqrt(hidden)
            )
            self.cross_norm = nn.LayerNorm(hidden)
            self.cross = nn.MultiheadAttention(hidden, heads, batch_first=True)
            self.blocks = nn.ModuleList(
                LatentBlock() for _ in range(int(spec["latent_self_attention_layers"]))
            )
            self.query = nn.Sequential(
                nn.Linear(4, hidden), nn.GELU(), nn.Linear(hidden, hidden)
            )
            self.decode_norm = nn.LayerNorm(hidden)
            self.decode = nn.MultiheadAttention(hidden, heads, batch_first=True)
            self.output = nn.Sequential(
                nn.LayerNorm(hidden),
                nn.Linear(hidden, mlp_hidden),
                nn.GELU(),
                nn.Linear(mlp_hidden, 3),
            )
            self.chunk = int(spec["query_chunk_size"])

        def forward(self, source: Any, queries: Any) -> Any:
            encoded = self.source(source)
            latents = self.latents[None].expand(source.shape[0], -1, -1)
            normalized = self.cross_norm(latents)
            latents = latents + self.cross(
                normalized, encoded, encoded, need_weights=False
            )[0]
            for block in self.blocks:
                latents = block(latents)
            predictions = []
            for start in range(0, queries.shape[1], self.chunk):
                query = self.query(queries[:, start : start + self.chunk])
                query = query + self.decode(
                    self.decode_norm(query), latents, latents, need_weights=False
                )[0]
                predictions.append(self.output(query))
            return torch.cat(predictions, dim=1)

    return PerceiverOperator()


def parameter_count(model: Any) -> int:
    return sum(int(parameter.numel()) for parameter in model.parameters())


def _normalized_flows(flows: Any) -> Any:
    np, _ = _imports()
    flows64 = np.asarray(flows, dtype=np.float64)
    return ((flows64 - flows64.mean()) / flows64.std(ddof=0)).astype(np.float32)


def evaluate(
    model: Any,
    cases: Sequence[Mapping[str, Any]],
    flows: Any,
    variant: str,
    scale: float,
    device: Any,
    reference_flow: float,
) -> dict[str, float]:
    np, _ = _imports()
    torch, _ = _torch_imports()
    normalized_flows = _normalized_flows(flows)
    reference = int(np.argmin(np.abs(np.asarray(flows) - reference_flow)))
    full_numerator = 0.0
    full_denominator = 0.0
    response_numerator = 0.0
    response_denominator = 0.0
    norm_prediction = 0.0
    norm_target = 0.0
    dot = 0.0
    model.eval()
    with torch.no_grad():
        for case in cases:
            predictions = []
            for condition, normalized_flow in enumerate(normalized_flows):
                source = torch.as_tensor(
                    source_features(case, variant, float(normalized_flow)), device=device
                )[None]
                query = torch.as_tensor(
                    query_features(case["coordinates"], float(normalized_flow)), device=device
                )[None]
                prediction = model(source, query)[0].float().cpu().numpy() * scale
                target = np.asarray(case["velocity"][condition], dtype=np.float64)
                prediction64 = np.asarray(prediction, dtype=np.float64)
                full_numerator += float(np.sum((prediction64 - target) ** 2))
                full_denominator += float(np.sum(target**2))
                norm_prediction += float(np.sum(prediction64**2))
                norm_target += float(np.sum(target**2))
                dot += float(np.sum(prediction64 * target))
                predictions.append(prediction64)
            reference_prediction = predictions[reference]
            reference_target = np.asarray(case["velocity"][reference], dtype=np.float64)
            for condition, prediction in enumerate(predictions):
                if condition == reference:
                    continue
                target = np.asarray(case["velocity"][condition], dtype=np.float64)
                prediction_delta = prediction - reference_prediction
                target_delta = target - reference_target
                response_numerator += float(np.sum((prediction_delta - target_delta) ** 2))
                response_denominator += float(np.sum(target_delta**2))
    return {
        "full_q_relative_l2": math.sqrt(full_numerator / max(full_denominator, 1e-30)),
        "paired_response_relative_l2": math.sqrt(
            response_numerator / max(response_denominator, 1e-30)
        ),
        "prediction_target_norm_ratio": math.sqrt(
            norm_prediction / max(norm_target, 1e-30)
        ),
        "vector_cosine": dot / math.sqrt(max(norm_prediction * norm_target, 1e-30)),
    }


def _batch(
    rng: Any,
    train_cases: Sequence[Mapping[str, Any]],
    normalized_flows: Any,
    variant: str,
    nodes: int,
    batch_size: int,
) -> tuple[Any, Any, Any]:
    np, _ = _imports()
    sources = []
    queries = []
    targets = []
    for _ in range(batch_size):
        case = train_cases[int(rng.integers(0, len(train_cases)))]
        condition = int(rng.integers(0, len(normalized_flows)))
        indices = np.sort(rng.choice(len(case["coordinates"]), size=nodes, replace=False))
        source = source_features(case, variant, float(normalized_flows[condition]))
        query = query_features(case["coordinates"][indices], float(normalized_flows[condition]))
        target = np.asarray(case["velocity"][condition, indices], dtype=np.float32)
        rotation = uniform_rotation(rng)
        source, query, target = apply_rotation(source, query, target, rotation)
        sources.append(source)
        queries.append(query)
        targets.append(target)
    return np.stack(sources), np.stack(queries), np.stack(targets)


def train_task(
    config: Mapping[str, Any],
    *,
    root: Path,
    compact_cache: Path,
    geometry_cache: Path,
    output: Path,
    variant: str,
    seed: int,
    git_commit: str,
    require_cuda: bool,
) -> dict[str, Any]:
    np, _ = _imports()
    torch, _ = _torch_imports()
    if variant not in VARIANTS or seed not in SEEDS:
        raise AneumoV1eKnownConditionError("V1e variant or seed is not registered.")
    source = config["source"]
    for key, hash_key in (
        ("pilot_config", "pilot_config_sha256"),
        ("v1d_result", "v1d_result_sha256"),
    ):
        if _sha256(root / source[key]) != source[hash_key]:
            raise AneumoV1eKnownConditionError(f"V1e dependency mismatch: {key}")
    if _sha256(compact_cache) != source["compact_cache_sha256"]:
        raise AneumoV1eKnownConditionError("V1e compact-cache SHA mismatch.")
    if _sha256(geometry_cache) != source["v1d_private_geometry_cache_sha256"]:
        raise AneumoV1eKnownConditionError("V1e geometry-cache SHA mismatch.")
    v1d = json.loads((root / source["v1d_result"]).read_text(encoding="utf-8"))
    if (
        v1d["gate"]["all_checks_passed"] is not True
        or v1d["gate"]["decision"]
        != "register_boundary_aware_known_condition_baseline_protocol_only"
    ):
        raise AneumoV1eKnownConditionError("V1d did not authorize V1e registration.")
    if require_cuda and not torch.cuda.is_available():
        raise AneumoV1eKnownConditionError("V1e requires scheduler-allocated CUDA.")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    flows, raw_cases = load_cases(compact_cache, geometry_cache)
    prepared = [normalize_case(case) for case in raw_cases]
    train_cases = [case for case in prepared if case["split"] == "train"]
    validation_cases = [case for case in prepared if case["split"] == "validation"]
    scale = velocity_scale(prepared)
    model = build_model(config).to(device)
    count = parameter_count(model)
    training = config["training"]
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(training["learning_rate"]),
        weight_decay=float(training["weight_decay"]),
    )
    warmup = int(training["warmup_steps"])
    steps = int(training["steps"])

    def schedule(step: int) -> float:
        if step < warmup:
            return max((step + 1) / max(warmup, 1), 1e-8)
        progress = min(max((step - warmup) / max(steps - warmup, 1), 0.0), 1.0)
        return 0.5 * (1.0 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, schedule)
    scaler = torch.cuda.amp.GradScaler(
        enabled=bool(training["mixed_precision"] and torch.cuda.is_available())
    )
    rng = np.random.default_rng(seed)
    normalized_flows = _normalized_flows(flows)
    output.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output / "checkpoint.pt"
    best_score = float("inf")
    best_step = -1
    history = []
    for step in range(1, steps + 1):
        model.train()
        source_batch, query_batch, target_batch = _batch(
            rng,
            train_cases,
            normalized_flows,
            variant,
            int(training["train_query_nodes_per_example"]),
            int(training["batch_cases"]),
        )
        source_tensor = torch.as_tensor(source_batch, device=device)
        query_tensor = torch.as_tensor(query_batch, device=device)
        target_tensor = torch.as_tensor(target_batch, device=device) / scale
        optimizer.zero_grad(set_to_none=True)
        with torch.cuda.amp.autocast(enabled=scaler.is_enabled()):
            prediction = model(source_tensor, query_tensor)
            loss = torch.mean((prediction - target_tensor) ** 2)
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(
            model.parameters(), float(training["gradient_clip_norm"])
        )
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()
        if step % int(training["validation_every_steps"]) == 0 or step == steps:
            validation = evaluate(
                model,
                validation_cases,
                flows,
                variant,
                scale,
                device,
                float(config["evaluation"]["reference_flow_kg_s"]),
            )
            score = 0.5 * (
                validation["full_q_relative_l2"]
                + validation["paired_response_relative_l2"]
            )
            history.append(
                {
                    "step": step,
                    "training_loss": float(loss.detach().cpu()),
                    "selection_score": score,
                    **validation,
                }
            )
            print(
                f"[V1e] variant={variant} seed={seed} step={step} "
                f"full={validation['full_q_relative_l2']:.6f} "
                f"response={validation['paired_response_relative_l2']:.6f}",
                flush=True,
            )
            if score < best_score:
                best_score = score
                best_step = step
                torch.save(
                    {
                        "config_sha256": config["_config_sha256"],
                        "git_commit": git_commit,
                        "variant": variant,
                        "seed": seed,
                        "step": step,
                        "velocity_scale": scale,
                        "state_dict": model.state_dict(),
                    },
                    checkpoint_path,
                )
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    if (
        checkpoint["config_sha256"] != config["_config_sha256"]
        or checkpoint["git_commit"] != git_commit
        or checkpoint["variant"] != variant
        or checkpoint["seed"] != seed
        or checkpoint["step"] != best_step
    ):
        raise AneumoV1eKnownConditionError("V1e selected checkpoint provenance changed.")
    model.load_state_dict(checkpoint["state_dict"])
    train_metrics = evaluate(
        model,
        train_cases,
        flows,
        variant,
        scale,
        device,
        float(config["evaluation"]["reference_flow_kg_s"]),
    )
    validation_metrics = evaluate(
        model,
        validation_cases,
        flows,
        variant,
        scale,
        device,
        float(config["evaluation"]["reference_flow_kg_s"]),
    )
    metrics = {
        "schema_version": "aurora.aneumo_isbi_v1e_known_condition.task.v1",
        "experiment_id": config["experiment_id"],
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "variant": variant,
        "seed": seed,
        "selected_step": best_step,
        "selection_score": best_score,
        "parameter_count": count,
        "source_token_count": 320,
        "velocity_scale_m_s": scale,
        "dependencies": {
            "compact_cache_sha256": source["compact_cache_sha256"],
            "geometry_cache_sha256": source["v1d_private_geometry_cache_sha256"],
            "v1d_result_sha256": source["v1d_result_sha256"],
        },
        "train": train_metrics,
        "validation": validation_metrics,
        "history": history,
        "access": {
            "splits_read": ["train", "validation"],
            "pressure_channel_read": False,
            "missing_or_partial_condition_evaluated": False,
            "test_geometry_or_field_read": False,
            "test_metric_computed": False,
            "clinical_endpoint_evaluated": False,
        },
        "checkpoint": {
            "selected_on": "validation_only",
            "sha256": _sha256(checkpoint_path),
            "eligible": True,
        },
        "device": {
            "type": str(device),
            "cuda_available": bool(torch.cuda.is_available()),
            "name": (
                torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
            ),
            "torch": torch.__version__,
        },
    }
    (output / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metrics


def aggregate_tasks(
    config: Mapping[str, Any], *, tasks_root: Path, output: Path, git_commit: str
) -> dict[str, Any]:
    expected_access = {
        "splits_read": ["train", "validation"],
        "pressure_channel_read": False,
        "missing_or_partial_condition_evaluated": False,
        "test_geometry_or_field_read": False,
        "test_metric_computed": False,
        "clinical_endpoint_evaluated": False,
    }
    expected_dependencies = {
        "compact_cache_sha256": config["source"]["compact_cache_sha256"],
        "geometry_cache_sha256": config["source"]["v1d_private_geometry_cache_sha256"],
        "v1d_result_sha256": config["source"]["v1d_result_sha256"],
    }
    metric_names = (
        "full_q_relative_l2",
        "paired_response_relative_l2",
        "prediction_target_norm_ratio",
        "vector_cosine",
    )
    records = []
    for variant in VARIANTS:
        for seed in SEEDS:
            task = tasks_root / f"{variant}_seed_{seed}"
            metrics_path = task / "metrics.json"
            status_path = task / "pbs_status.json"
            if not metrics_path.is_file() or not status_path.is_file():
                raise AneumoV1eKnownConditionError(f"Missing V1e task artifact: {task.name}")
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            status = json.loads(status_path.read_text(encoding="utf-8"))
            expected_index = VARIANTS.index(variant) * len(SEEDS) + SEEDS.index(seed)
            checkpoint = metrics.get("checkpoint", {})
            checkpoint_sha = str(checkpoint.get("sha256", ""))
            selected_step = metrics.get("selected_step")
            device = metrics.get("device", {})
            numeric_values = [metrics.get("selection_score"), metrics.get("velocity_scale_m_s")]
            for split in ("train", "validation"):
                numeric_values.extend(metrics.get(split, {}).get(name) for name in metric_names)
            if (
                metrics.get("schema_version")
                != "aurora.aneumo_isbi_v1e_known_condition.task.v1"
                or metrics.get("experiment_id") != config["experiment_id"]
                or metrics.get("variant") != variant
                or metrics.get("seed") != seed
                or metrics.get("git_commit") != git_commit
                or metrics.get("config_sha256") != config["_config_sha256"]
                or metrics.get("dependencies") != expected_dependencies
                or metrics.get("access") != expected_access
                or not isinstance(selected_step, int)
                or selected_step < 400
                or selected_step > 8000
                or selected_step % 400 != 0
                or not all(
                    isinstance(value, (int, float)) and math.isfinite(float(value))
                    for value in numeric_values
                )
                or float(metrics.get("velocity_scale_m_s", 0.0)) <= 0.0
                or int(metrics.get("parameter_count", 0)) <= 0
                or metrics.get("source_token_count") != 320
                or checkpoint.get("eligible") is not True
                or checkpoint.get("selected_on") != "validation_only"
                or len(checkpoint_sha) != 64
                or any(character not in "0123456789abcdef" for character in checkpoint_sha)
                or device.get("cuda_available") is not True
                or not str(device.get("type", "")).startswith("cuda")
                or not str(device.get("name", ""))
                or status.get("exit_status") != 0
                or status.get("state") != "complete"
                or status.get("metrics_created") is not True
                or status.get("array_index") != expected_index
                or status.get("variant") != variant
                or status.get("seed") != seed
            ):
                raise AneumoV1eKnownConditionError("V1e task provenance mismatch.")
            records.append(metrics)
    by_variant = {
        variant: [record for record in records if record["variant"] == variant]
        for variant in VARIANTS
    }

    def values(variant: str, split: str, metric: str) -> list[float]:
        return [float(record[split][metric]) for record in by_variant[variant]]

    full_primary = values(PRIMARY, "validation", "full_q_relative_l2")
    full_control = values(CONTROL, "validation", "full_q_relative_l2")
    response_primary = values(PRIMARY, "validation", "paired_response_relative_l2")
    response_control = values(CONTROL, "validation", "paired_response_relative_l2")
    train_primary = values(PRIMARY, "train", "full_q_relative_l2")
    thresholds = config["gate"]["thresholds"]
    better_full = sum(left < right for left, right in zip(full_primary, full_control))
    better_response = sum(
        left < right for left, right in zip(response_primary, response_control)
    )
    mean_full_primary = sum(full_primary) / len(full_primary)
    mean_full_control = sum(full_control) / len(full_control)
    mean_response_primary = sum(response_primary) / len(response_primary)
    mean_response_control = sum(response_control) / len(response_control)
    improvement_full = (mean_full_control - mean_full_primary) / mean_full_control
    improvement_response = (
        mean_response_control - mean_response_primary
    ) / mean_response_control
    parameter_counts = {int(record["parameter_count"]) for record in records}
    source_token_counts = {int(record["source_token_count"]) for record in records}
    checks = {
        "pinned_data_and_geometry_cache_integrity": True,
        "all_six_gpu_tasks_exit_zero_with_eligible_validation_selected_checkpoints": (
            len(records) == 6
            and all(record["checkpoint"]["eligible"] for record in records)
            and all(
                record["checkpoint"]["selected_on"] == "validation_only"
                for record in records
            )
        ),
        "exact_parameter_and_source_token_match_between_variants": (
            len(parameter_counts) == 1 and source_token_counts == {320}
        ),
        "no_pressure_missing_partial_test_or_clinical_access": all(
            record["access"] == expected_access for record in records
        ),
        "boundary_worst_seed_train_full_q_relative_l2_at_most_0.25": max(train_primary)
        <= float(thresholds["maximum_worst_seed_train_full_q_relative_l2"]),
        "boundary_worst_seed_validation_full_q_relative_l2_at_most_0.35": max(full_primary)
        <= float(thresholds["maximum_worst_seed_validation_full_q_relative_l2"]),
        "boundary_worst_seed_validation_paired_response_relative_l2_at_most_0.50": max(
            response_primary
        )
        <= float(thresholds["maximum_worst_seed_validation_paired_response_relative_l2"]),
        (
            "boundary_better_than_geometry_control_on_both_primary_metrics_"
            "in_at_least_two_of_three_seeds"
        ): (
            better_full >= int(thresholds["minimum_better_seeds_each_primary_metric"])
            and better_response
            >= int(thresholds["minimum_better_seeds_each_primary_metric"])
        ),
        "boundary_seed_mean_relative_improvement_at_least_0.05_on_both_primary_metrics": (
            improvement_full
            >= float(thresholds["minimum_seed_mean_relative_improvement_each_primary_metric"])
            and improvement_response
            >= float(thresholds["minimum_seed_mean_relative_improvement_each_primary_metric"])
        ),
    }
    passed = all(checks.values())
    summary = {}
    for variant in VARIANTS:
        summary[variant] = {
            "seeds": [record["seed"] for record in by_variant[variant]],
            "selected_steps": [record["selected_step"] for record in by_variant[variant]],
            "parameter_count": by_variant[variant][0]["parameter_count"],
            "train_full_q_relative_l2": values(variant, "train", "full_q_relative_l2"),
            "validation_full_q_relative_l2": values(
                variant, "validation", "full_q_relative_l2"
            ),
            "validation_paired_response_relative_l2": values(
                variant, "validation", "paired_response_relative_l2"
            ),
            "validation_prediction_target_norm_ratio": values(
                variant, "validation", "prediction_target_norm_ratio"
            ),
            "validation_vector_cosine": values(
                variant, "validation", "vector_cosine"
            ),
        }
    result = {
        "schema_version": "aurora.aneumo_isbi_v1e_known_condition.aggregate.v1",
        "experiment_id": config["experiment_id"],
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "tasks": len(records),
        "summary": summary,
        "comparison": {
            "boundary_better_full_q_seeds": better_full,
            "boundary_better_response_seeds": better_response,
            "boundary_seed_mean_relative_improvement_full_q": improvement_full,
            "boundary_seed_mean_relative_improvement_response": improvement_response,
        },
        "gate": {
            "checks": checks,
            "passed_checks": sum(bool(value) for value in checks.values()),
            "total_checks": len(checks),
            "all_checks_passed": passed,
            "decision": (
                config["gate"]["pass_authorizes"]
                if passed
                else config["gate"]["failure_action"]
            ),
            "pass_authorizes": config["gate"]["pass_authorizes"],
            "pass_does_not_authorize": config["gate"]["pass_does_not_authorize"],
        },
        "access": {
            "splits_read": ["train", "validation"],
            "pressure_channel_read": False,
            "missing_or_partial_condition_evaluated": False,
            "test_geometry_or_field_read": False,
            "test_metric_computed": False,
            "clinical_endpoint_evaluated": False,
        },
        "interpretation": config["interpretation"],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--compact-cache", type=Path)
    parser.add_argument("--geometry-cache", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    parser.add_argument("--aggregate-tasks", type=Path)
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    if args.aggregate_tasks is not None:
        result = aggregate_tasks(
            config,
            tasks_root=args.aggregate_tasks,
            output=args.output,
            git_commit=args.git_commit,
        )
    else:
        if (
            args.compact_cache is None
            or args.geometry_cache is None
            or args.variant is None
            or args.seed is None
        ):
            parser.error("training requires caches, variant, and seed")
        result = train_task(
            config,
            root=args.root,
            compact_cache=args.compact_cache,
            geometry_cache=args.geometry_cache,
            output=args.output,
            variant=args.variant,
            seed=args.seed,
            git_commit=args.git_commit,
            require_cuda=args.require_cuda,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
