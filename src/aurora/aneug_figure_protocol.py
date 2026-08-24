"""Prediction-blind selection rules for the confirmatory AneuG CFD figure.

The functions accept reference cycles only. They cannot inspect model outputs,
which keeps case and trace-vertex selection independent of candidate error.
This module does not open the outer split or render a figure by itself.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

try:
    import torch
except ImportError:  # config validation remains available in lightweight environments
    torch = None

from aurora.cycle_functionals import compute_cycle_functionals


class AneuGFigureProtocolError(RuntimeError):
    """Raised when a confirmatory figure selection is not well defined."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise AneuGFigureProtocolError(label)


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version") == "aurora.aneug_confirmatory_figure.v1",
        "config_schema",
    )
    _require(config.get("status") == "frozen_non_executable", "status")
    selection = config["reference_only_selection"]
    _require(
        selection["case_metric"] == "area_weighted_mean_reference_OSI"
        and selection["case_quantiles"] == [0.1, 0.5, 0.9]
        and selection["trace_vertex_metric"] == "reference_OSI"
        and selection["trace_vertex_quantile"] == 0.9
        and selection["candidate_or_baseline_values_used"] is False,
        "selection",
    )
    display = config["display"]
    _require(
        display["camera"] == "fixed_canonical_orthographic"
        and display["shared_coordinates"] is True
        and display["shared_mask"] is True
        and display["tawss_colour_limits"]
        == "full_range_across_the_three_selected_references"
        and display["osi_colour_limits"] == [0.0, 0.5]
        and display["candidate_dependent_clipping"] is False,
        "display",
    )
    boundary = config["boundary"]
    _require(
        boundary["outer_case_count"] == 51
        and boundary["execute_now"] is False
        and boundary["outer_access_before_model_freeze"] is False
        and boundary["paper_claim"] is False,
        "boundary",
    )


def _normalized_vertex_weights(
    vertex_weights: torch.Tensor, node_count: int
) -> torch.Tensor:
    _require(vertex_weights.shape == (node_count,), "vertex_weight_shape")
    _require(
        bool(torch.isfinite(vertex_weights).all().item())
        and bool((vertex_weights >= 0).all().item())
        and bool((vertex_weights.sum() > 0).item()),
        "vertex_weights",
    )
    return vertex_weights / vertex_weights.sum()


def reference_osi_summary(
    wss: torch.Tensor,
    phase_weights: torch.Tensor,
    vertex_weights: torch.Tensor,
    *,
    reference_tawss_floor: float | None = None,
) -> dict[str, Any]:
    """Return reference-only area-weighted OSI burden and support coverage."""

    if reference_tawss_floor is None:
        activity_epsilon = 1e-12
    else:
        _require(
            math.isfinite(float(reference_tawss_floor))
            and float(reference_tawss_floor) > 0.0,
            "reference_tawss_floor",
        )
        activity_epsilon = float(reference_tawss_floor)
    functionals = compute_cycle_functionals(
        wss,
        phase_weights,
        torch,
        activity_epsilon=activity_epsilon,
    )
    weights = _normalized_vertex_weights(vertex_weights.to(wss), wss.shape[1])
    valid = functionals["osi_valid"] & torch.isfinite(functionals["osi"])
    support = weights * valid.to(weights.dtype)
    support_weight = support.sum()
    _require(bool((support_weight > 0).item()), "empty_osi_support")
    burden = torch.sum(
        weights[valid] * functionals["osi"][valid]
    ) / support_weight
    _require(bool(torch.isfinite(burden).item()), "nonfinite_burden")
    return {
        "area_weighted_mean_reference_osi": float(burden.item()),
        "area_weighted_osi_coverage": float(support_weight.item()),
        "osi": functionals["osi"],
        "osi_valid": valid,
    }


def select_case_ordinals(
    burdens: Sequence[float],
    *,
    quantile_targets: Sequence[float] = (0.1, 0.5, 0.9),
) -> list[int]:
    """Select stable ordinal ranks after sorting by reference burden."""

    _require(len(burdens) >= len(quantile_targets), "case_count")
    _require(
        all(math.isfinite(float(value)) for value in burdens), "finite_burdens"
    )
    _require(
        tuple(sorted(quantile_targets)) == tuple(quantile_targets)
        and all(0.0 <= value <= 1.0 for value in quantile_targets),
        "quantiles",
    )
    ordered = sorted(range(len(burdens)), key=lambda index: (burdens[index], index))
    ranks = [
        int(math.floor(float(target) * (len(ordered) - 1) + 0.5))
        for target in quantile_targets
    ]
    _require(len(set(ranks)) == len(ranks), "duplicate_quantile_rank")
    return [ordered[rank] for rank in ranks]


def _weighted_quantile(
    values: torch.Tensor,
    weights: torch.Tensor,
    quantile: float,
) -> torch.Tensor:
    _require(values.ndim == 1 and weights.shape == values.shape, "quantile_shape")
    _require(0.0 <= quantile <= 1.0, "quantile_value")
    order = torch.argsort(values, stable=True)
    sorted_values = values[order]
    sorted_weights = weights[order]
    cumulative = torch.cumsum(sorted_weights, dim=0)
    target = quantile * sorted_weights.sum()
    position = int(torch.searchsorted(cumulative, target, right=False).item())
    position = min(position, sorted_values.numel() - 1)
    return sorted_values[position]


def select_reference_trace_vertex(
    summary: Mapping[str, Any],
    vertex_weights: torch.Tensor,
    *,
    quantile: float = 0.9,
) -> int:
    """Choose a stable valid vertex nearest a reference OSI weighted quantile."""

    osi = summary["osi"]
    valid = summary["osi_valid"]
    weights = _normalized_vertex_weights(vertex_weights.to(osi), osi.numel())
    valid_indices = torch.nonzero(valid, as_tuple=False).reshape(-1)
    _require(valid_indices.numel() > 0, "trace_support")
    valid_values = osi[valid_indices]
    valid_weights = weights[valid_indices]
    target = _weighted_quantile(valid_values, valid_weights, quantile)
    distance = torch.abs(valid_values - target)
    minimum = torch.min(distance)
    tied = valid_indices[distance == minimum]
    _require(tied.numel() > 0, "trace_tie")
    return int(torch.min(tied).item())


def build_reference_selection(
    reference_cases: Sequence[Mapping[str, torch.Tensor]],
    phase_weights: torch.Tensor,
    *,
    case_quantiles: Sequence[float] = (0.1, 0.5, 0.9),
    trace_vertex_quantile: float = 0.9,
    expected_case_count: int = 51,
    reference_tawss_floor: float | None = None,
) -> dict[str, Any]:
    """Build an identifier-free outer-figure selection from references only."""

    _require(expected_case_count > 0, "expected_case_count")
    _require(len(reference_cases) == expected_case_count, "outer_case_count")
    summaries = [
        reference_osi_summary(
            case["wss"],
            phase_weights,
            case["vertex_weights"],
            reference_tawss_floor=reference_tawss_floor,
        )
        for case in reference_cases
    ]
    burdens = [summary["area_weighted_mean_reference_osi"] for summary in summaries]
    selected = select_case_ordinals(burdens, quantile_targets=case_quantiles)
    traces = [
        select_reference_trace_vertex(
            summaries[index],
            reference_cases[index]["vertex_weights"],
            quantile=trace_vertex_quantile,
        )
        for index in selected
    ]
    return {
        "schema_version": "aurora.aneug_confirmatory_figure.selection.v1",
        "selection_role": "reference_only_prediction_blind",
        "selected_outer_ordinals": selected,
        "selected_reference_osi_burdens": [burdens[index] for index in selected],
        "selected_reference_trace_vertex_ordinals": traces,
        "case_quantiles": list(case_quantiles),
        "trace_vertex_quantile": trace_vertex_quantile,
        "reference_case_count": expected_case_count,
        "case_identifiers_included": False,
        "candidate_or_baseline_values_read": False,
    }
