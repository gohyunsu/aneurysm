"""Prediction-blind confirmatory-figure selection for release-730 T0.

This module adapts the historical 51-case selection primitive to the active
73-case locked test. It consumes references only after a private T0 activation;
it neither loads fields nor renders predictions by itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    import torch
except ImportError:  # config validation remains available without PyTorch
    torch = None

from aurora.aneug_figure_protocol import (
    AneuGFigureProtocolError,
    build_reference_selection,
)


TEST_CASE_DIGEST = "1f87f52fc4b819548aebcc6df77f90830d475d1e92df0ca833980347d792aa56"
PRIVATE_SPLIT_SHA256 = (
    "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f"
)


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise AneuGFigureProtocolError(label)


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_confirmatory_figure.v1",
        "config_schema",
    )
    _require(
        config.get("protocol_id") == "aneug_release_730_confirmatory_figure_v1"
        and config.get("status") == "frozen_non_executable_until_T0",
        "protocol_status",
    )
    split = config["split"]
    _require(
        split["locked_test_cases"] == 73
        and split["test_case_digest"] == TEST_CASE_DIGEST
        and split["private_split_manifest_sha256"] == PRIVATE_SPLIT_SHA256
        and split["ordered_test_digest_source"]
        == "required_from_private_T0_activation",
        "split",
    )
    selection = config["reference_only_selection"]
    _require(
        selection["case_metric"] == "area_weighted_mean_reference_OSI"
        and selection["case_quantiles"] == [0.1, 0.5, 0.9]
        and selection["trace_vertex_metric"] == "reference_OSI"
        and selection["trace_vertex_quantile"] == 0.9
        and selection["ordinal_tie_break"] == "frozen_private_test_loader_order"
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
        and display["candidate_dependent_clipping"] is False
        and display["trace"]
        == "reference_control_proposal_same_vertex_all_80_phases",
        "display",
    )
    layout = config["render_layout"]
    _require(
        layout["figure_width_inches"] == 7.1
        and layout["figure_height_inches"] == 1.85
        and layout["paper_height_fraction"] == 0.235
        and layout["case_columns"]
        == ["low_reference_OSI", "median_reference_OSI", "high_reference_OSI"]
        and layout["surface_rows"] == ["TAWSS", "OSI"]
        and layout["method_columns_within_case"]
        == ["reference", "selected_control", "proposal"]
        and layout["trace_row"]
        == "signed_WSS_projection_at_reference_selected_vertex"
        and layout["trace_direction_anchor"]
        == "reference_vector_at_reference_maximum_magnitude_phase"
        and layout["trace_y_limits"]
        == "full_range_across_three_selected_reference_signed_traces"
        and layout["trace_y_margin_fraction"] == 0.05
        and layout["camera_azimuth_degrees"] == -60.0
        and layout["camera_elevation_degrees"] == 20.0
        and layout["surface_colormap"] == "viridis"
        and layout["error_or_candidate_dependent_limits"] is False
        and layout["surface_panels_rasterized_dpi"] == 600
        and layout["outputs"] == ["vector_text_pdf", "600dpi_png"],
        "render_layout",
    )
    boundary = config["boundary"]
    _require(
        boundary["execute_now"] is False
        and boundary["requires_frozen_C0_checkpoints"] is True
        and boundary["requires_private_T0_activation"] is True
        and boundary["locked_test_access_before_T0"] is False
        and boundary["processed_only_extra_access"] is False
        and boundary["case_identifiers_in_public_result"] is False
        and boundary["paper_claim"] is False
        and boundary["server"] == "introai9"
        and boundary["excluded_server"] == "junjinyong"
        and boundary["maintain_public_site"] is False,
        "boundary",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def build_release730_reference_selection(
    reference_cases: Sequence[Mapping[str, torch.Tensor]],
    phase_weights: torch.Tensor,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Select three locked-test ordinals using references only."""

    validate_config(config)
    _require(torch is not None, "torch_required")
    _require(tuple(phase_weights.shape) == (80,), "phase_count")
    _require(
        all(
            isinstance(case, Mapping)
            and "wss" in case
            and tuple(case["wss"].shape[:1]) == (80,)
            for case in reference_cases
        ),
        "reference_cycle_shape",
    )
    selection = config["reference_only_selection"]
    generic = build_reference_selection(
        reference_cases,
        phase_weights,
        case_quantiles=selection["case_quantiles"],
        trace_vertex_quantile=float(selection["trace_vertex_quantile"]),
        expected_case_count=73,
    )
    return {
        "schema_version": "aurora.aneug_release_730_confirmatory_figure.selection.v1",
        "protocol_id": config["protocol_id"],
        "selection_role": "locked_test_reference_only_prediction_blind",
        "locked_test_case_count": 73,
        "reference_phase_count": 80,
        "test_case_digest": config["split"]["test_case_digest"],
        "selected_locked_test_ordinals": generic["selected_outer_ordinals"],
        "selected_reference_osi_burdens": generic[
            "selected_reference_osi_burdens"
        ],
        "selected_reference_trace_vertex_ordinals": generic[
            "selected_reference_trace_vertex_ordinals"
        ],
        "case_quantiles": generic["case_quantiles"],
        "trace_vertex_quantile": generic["trace_vertex_quantile"],
        "case_identifiers_included": False,
        "candidate_or_baseline_values_read": False,
        "processed_only_extra_values_read": False,
        "paper_claim": False,
    }
