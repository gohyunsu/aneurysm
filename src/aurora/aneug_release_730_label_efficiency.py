"""Prospective, label-blind utilities for release-730 label efficiency.

The module fixes nested transient-train memberships without inspecting a
geometry or CFD value, provides equal-compute repeated exposure schedules,
and recomputes every learned transient statistic from the selected unique
train cases.  It neither opens the locked test partition nor trains a model.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch


SCHEMA_VERSION = "aurora.aneug_release_730_label_efficiency.v1"
PROTOCOL_ID = "aneug_release_730_label_efficiency_v1"
EXPECTED_BUDGETS = ((10, 58), (25, 146), (50, 292), (100, 584))
EXPECTED_SEEDS = (20_260_901, 20_260_902, 20_260_903, 20_260_904, 20_260_905)
REFERENCE_EPOCH_EXPOSURES = 584


class Release730LabelEfficiencyError(RuntimeError):
    """Raised when a label-efficiency validity boundary is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730LabelEfficiencyError(reason)


def canonical_digest(values: Sequence[str]) -> str:
    return hashlib.sha256(
        json.dumps(list(values), separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(payload)
    return payload


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version") == SCHEMA_VERSION
        and config.get("protocol_id") == PROTOCOL_ID
        and config.get("status") == "prospective_validation_only_readiness",
        "identity",
    )
    base = config.get("base_protocol", {})
    _require(
        tuple(
            base.get(key)
            for key in (
                "official_transient_train_cases",
                "fixed_validation_cases",
                "locked_test_cases",
                "processed_only_extra_cases",
            )
        )
        == (584, 73, 73, 79),
        "split_counts",
    )
    _require(
        isinstance(base.get("matched_training_config_sha256"), str)
        and len(base["matched_training_config_sha256"]) == 64,
        "base_config_hash",
    )
    budgets = tuple(
        (int(row["percent"]), int(row["unique_transient_cases"]))
        for row in config.get("label_budgets", ())
    )
    _require(budgets == EXPECTED_BUDGETS, "label_budgets")
    subset = config.get("subset_selection", {})
    _require(
        subset.get("algorithm")
        == "sha256_ranked_case_identifier_nested_prefix_v1"
        and isinstance(subset.get("public_salt"), str)
        and bool(subset["public_salt"])
        and subset.get("uses_geometry_or_field_values") is False
        and subset.get("nested") is True
        and subset.get("selected_membership_remains_private") is True
        and subset.get("training_loader_preserves_original_train_order") is True,
        "subset_selection",
    )
    statistics = config.get("subset_only_statistics", {})
    _require(
        statistics.get("ghd_component_mean_and_population_std") is True
        and statistics.get("physical_wss_component_mean_and_population_std")
        is True
        and statistics.get("cycle_output_scale")
        == "sqrt_sum_component_second_moments"
        and statistics.get("reference_tawss_floor") is True
        and statistics.get("validation_or_test_values_used") is False,
        "subset_statistics",
    )
    exposure = config.get("training_exposure", {})
    _require(
        exposure.get("transient_examples_per_reference_epoch")
        == REFERENCE_EPOCH_EXPOSURES
        and exposure.get("algorithm")
        == "balanced_repeated_seeded_permutations_v1"
        and exposure.get("same_compute_schedule_across_label_budgets") is True
        and exposure.get("each_unique_case_repetitions_differ_by_at_most_one_per_epoch")
        is True
        and exposure.get("steady_examples_per_reference_epoch_for_T_plus_S")
        == REFERENCE_EPOCH_EXPOSURES,
        "training_exposure",
    )
    seeds = config.get("seeds", {})
    _require(
        tuple(seeds.get("10_25_50_percent", ())) == EXPECTED_SEEDS[:3]
        and tuple(seeds.get("100_percent", ())) == EXPECTED_SEEDS,
        "seeds",
    )
    model = config.get("model", {})
    _require(
        model.get("family") == "release730_ghd_gps"
        and model.get("objective") == "field_only"
        and tuple(model.get("information_modes", ()))
        == ("transient_only", "eligible_steady")
        and model.get("initialization") == "fresh_seeded_initialization"
        and model.get("separate_single_field_head_for_T_plus_S") is True
        and model.get("steady_field_required_at_inference") is False,
        "model",
    )
    evaluation = config.get("evaluation", {})
    _require(
        evaluation.get("selection_partition") == "fixed_validation_73"
        and evaluation.get("paired_case_bootstrap_replicates") == 10_000
        and evaluation.get("absolute_performance_threshold") is None
        and evaluation.get("read_locked_test") is False
        and evaluation.get("read_processed_only_extras") is False
        and evaluation.get("paper_performance_claim") is False,
        "evaluation_scope",
    )


def nested_subset_memberships(
    train_case_ids: Sequence[str], config: Mapping[str, Any]
) -> dict[int, tuple[str, ...]]:
    """Return hash-ranked nested memberships, preserving no input-order bias."""

    validate_config(config)
    case_ids = tuple(str(value) for value in train_case_ids)
    _require(len(case_ids) == 584 and len(set(case_ids)) == 584, "train_membership")
    salt = config["subset_selection"]["public_salt"]
    ranked = tuple(
        sorted(
            case_ids,
            key=lambda case_id: (
                hashlib.sha256(f"{salt}\0{case_id}".encode("utf-8")).digest(),
                case_id,
            ),
        )
    )
    output = {
        int(row["percent"]): ranked[: int(row["unique_transient_cases"])]
        for row in config["label_budgets"]
    }
    previous: set[str] = set()
    for percent, count in EXPECTED_BUDGETS:
        current = set(output[percent])
        _require(len(current) == count and previous <= current, "nested_membership")
        previous = current
    _require(set(output[100]) == set(case_ids), "full_membership")
    return output


def loader_order_for_membership(
    full_train_loader_order: Sequence[str], membership: Sequence[str]
) -> tuple[str, ...]:
    """Filter the frozen full-train loader order without exposing rank order."""

    full = tuple(str(value) for value in full_train_loader_order)
    selected = {str(value) for value in membership}
    _require(len(full) == 584 and len(set(full)) == 584, "full_loader_order")
    _require(bool(selected) and selected <= set(full), "subset_membership")
    ordered = tuple(case_id for case_id in full if case_id in selected)
    _require(len(ordered) == len(selected), "subset_loader_order")
    return ordered


def balanced_epoch_indices(
    unique_case_count: int,
    *,
    training_seed: int,
    epoch: int,
    exposures: int = REFERENCE_EPOCH_EXPOSURES,
) -> tuple[int, ...]:
    """Create equal-compute, balanced repeated permutations for one epoch."""

    _require(unique_case_count > 0, "unique_case_count")
    _require(exposures >= unique_case_count, "exposure_count")
    _require(training_seed in EXPECTED_SEEDS, "training_seed")
    _require(epoch >= 0, "epoch")
    result: list[int] = []
    round_index = 0
    while len(result) < exposures:
        order = list(range(unique_case_count))
        round_seed = training_seed + epoch + round_index * 1_000_003
        random.Random(round_seed).shuffle(order)
        result.extend(order[: exposures - len(result)])
        round_index += 1
    counts = [result.count(index) for index in range(unique_case_count)]
    _require(max(counts) - min(counts) <= 1, "unbalanced_exposure")
    return tuple(result)


def subset_training_statistics(
    normalized_records: Sequence[Mapping[str, Any]],
    raw_ghd_rows: torch.Tensor,
    decoder_mean: torch.Tensor,
    decoder_std: torch.Tensor,
    *,
    decoder_epsilon: float = 1e-5,
) -> dict[str, Any]:
    """Compute GHD and physical-WSS moments from selected train cases only."""

    _require(bool(normalized_records), "empty_subset")
    _require(
        raw_ghd_rows.ndim == 2
        and raw_ghd_rows.shape == (len(normalized_records), 432),
        "ghd_shape",
    )
    ghd = raw_ghd_rows.detach().cpu().to(torch.float64)
    mean = decoder_mean.detach().cpu().to(torch.float64).reshape(-1)
    std = decoder_std.detach().cpu().to(torch.float64).reshape(-1)
    _require(
        mean.numel() == std.numel() == 9
        and bool(torch.isfinite(ghd).all().item())
        and bool(torch.isfinite(mean).all().item())
        and bool(torch.isfinite(std).all().item())
        and bool((std > 0).all().item())
        and decoder_epsilon >= 0.0,
        "statistics_inputs",
    )
    wss_count = 0
    wss_sum = torch.zeros(3, dtype=torch.float64)
    wss_squared = torch.zeros(3, dtype=torch.float64)
    for record in normalized_records:
        tensor = record["tensor"].detach().cpu().to(torch.float64)
        _require(
            tensor.ndim == 3
            and tensor.shape[-1] == 9
            and bool(torch.isfinite(tensor).all().item()),
            "record_tensor",
        )
        physical = tensor[..., 6:9] * (std[6:9] + decoder_epsilon) + mean[6:9]
        wss_count += physical.shape[0] * physical.shape[1]
        wss_sum += physical.sum(dim=(0, 1))
        wss_squared += physical.square().sum(dim=(0, 1))
    wss_mean = wss_sum / wss_count
    wss_variance = torch.clamp(wss_squared / wss_count - wss_mean.square(), min=0)
    ghd_mean = ghd.mean(dim=0)
    ghd_variance = torch.clamp(ghd.square().mean(dim=0) - ghd_mean.square(), min=0)
    ghd_std = torch.sqrt(ghd_variance)
    wss_std = torch.sqrt(wss_variance)
    cycle_output_scale = float(
        torch.sqrt(torch.sum(wss_mean.square() + wss_variance)).item()
    )
    _require(
        math.isfinite(cycle_output_scale) and cycle_output_scale > 0.0,
        "cycle_output_scale",
    )
    statistics_payload = {
        "unique_train_cases": len(normalized_records),
        "ghd_mean": [float(value) for value in ghd_mean.tolist()],
        "ghd_std_population": [float(value) for value in ghd_std.tolist()],
        "wss_physical_mean": [float(value) for value in wss_mean.tolist()],
        "wss_physical_std_population": [
            float(value) for value in wss_std.tolist()
        ],
        "cycle_output_scale": cycle_output_scale,
        "validation_test_or_extra_statistics_included": False,
    }
    statistics_sha256 = hashlib.sha256(
        json.dumps(
            statistics_payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    return {
        **statistics_payload,
        "ghd_mean": ghd_mean.to(torch.float32),
        "ghd_std_population": ghd_std.to(torch.float32),
        "wss_physical_mean": wss_mean,
        "wss_physical_std_population": wss_std,
        "statistics_sha256": statistics_sha256,
    }
