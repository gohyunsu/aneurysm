"""Dataset-loader-free renderer for the frozen release-730 figure layout.

The builder accepts exactly three cases already selected by the reference-only
T0 selector.  It has no data loader, checkpoint loader, CLI, case identifier,
or selection logic.  Reference values alone determine display limits and trace
directions.  The optional Matplotlib renderer is imported only when called so
the scientific contract remains testable in the lightweight CI environment.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from aurora.aneug_release_730_figure_protocol import validate_config
from aurora.cycle_functionals import compute_cycle_functionals


class Release730FigureRendererError(RuntimeError):
    """Raised when a prediction-blind render contract is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730FigureRendererError(reason)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _finite_tensor(value: Any) -> bool:
    return isinstance(value, torch.Tensor) and bool(torch.isfinite(value).all().item())


def _case_payload(
    case: Mapping[str, torch.Tensor],
    trace_vertex: int,
    phase_weights: torch.Tensor,
) -> dict[str, Any]:
    required = (
        "coordinates",
        "faces",
        "display_mask",
        "reference_wss",
        "selected_control_wss",
        "proposal_wss",
    )
    _require(all(key in case for key in required), "case_keys")
    coordinates = case["coordinates"]
    faces = case["faces"]
    display_mask = case["display_mask"]
    _require(
        coordinates.ndim == 2
        and coordinates.shape[1] == 3
        and _finite_tensor(coordinates),
        "coordinates",
    )
    nodes = int(coordinates.shape[0])
    _require(
        faces.ndim == 2
        and faces.shape[1] == 3
        and faces.dtype in (torch.int32, torch.int64)
        and int(faces.min().item()) >= 0
        and int(faces.max().item()) < nodes,
        "faces",
    )
    _require(
        display_mask.dtype == torch.bool
        and display_mask.shape == (nodes,)
        and int(display_mask.sum().item()) >= 3,
        "display_mask",
    )
    retained_faces = display_mask[faces.to(torch.int64)].all(dim=1)
    _require(bool(retained_faces.any().item()), "empty_display_faces")
    _require(0 <= int(trace_vertex) < nodes, "trace_vertex")
    _require(bool(display_mask[int(trace_vertex)].item()), "trace_vertex_mask")

    methods: dict[str, dict[str, torch.Tensor]] = {}
    for label, key in (
        ("reference", "reference_wss"),
        ("selected_control", "selected_control_wss"),
        ("proposal", "proposal_wss"),
    ):
        cycle = case[key]
        _require(
            cycle.shape == (80, nodes, 3) and _finite_tensor(cycle),
            f"{label}_cycle",
        )
        functionals = compute_cycle_functionals(cycle, phase_weights, torch)
        methods[label] = {
            "tawss": functionals["tawss"].detach().cpu(),
            "osi": functionals["osi"].detach().cpu(),
            "osi_valid": functionals["osi_valid"].detach().cpu(),
            "cycle": cycle.detach().cpu(),
        }

    reference_trace = methods["reference"]["cycle"][:, int(trace_vertex), :]
    reference_magnitude = torch.linalg.vector_norm(reference_trace, dim=-1)
    anchor_phase = int(torch.argmax(reference_magnitude).item())
    anchor = reference_trace[anchor_phase]
    anchor_norm = torch.linalg.vector_norm(anchor)
    _require(bool((anchor_norm > 0).item()), "trace_anchor")
    direction = anchor / anchor_norm
    for values in methods.values():
        trace = values.pop("cycle")[:, int(trace_vertex), :]
        values["signed_trace"] = torch.sum(trace * direction.reshape(1, 3), dim=-1)

    return {
        "coordinates": coordinates.detach().cpu(),
        "faces": faces.detach().cpu().to(torch.int64),
        "display_mask": display_mask.detach().cpu(),
        "retained_faces": retained_faces.detach().cpu(),
        "trace_vertex_ordinal": int(trace_vertex),
        "trace_anchor_phase": anchor_phase,
        "methods": methods,
    }


def build_release730_render_payload(
    selected_cases: Sequence[Mapping[str, torch.Tensor]],
    selection: Mapping[str, Any],
    phase_weights: torch.Tensor,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Build plot-ready tensors after reference-only selection is frozen."""

    validate_config(config)
    _require(len(selected_cases) == 3, "selected_case_count")
    _require(
        selection.get("schema_version")
        == "aurora.aneug_release_730_confirmatory_figure.selection.v1"
        and selection.get("protocol_id") == config["protocol_id"],
        "selection_identity",
    )
    ordinals = selection.get("selected_locked_test_ordinals")
    traces = selection.get("selected_reference_trace_vertex_ordinals")
    _require(
        isinstance(ordinals, list)
        and len(ordinals) == 3
        and len(set(int(value) for value in ordinals)) == 3
        and all(0 <= int(value) < 73 for value in ordinals),
        "selection_ordinals",
    )
    _require(
        isinstance(traces, list) and len(traces) == 3,
        "selection_traces",
    )
    _require(
        selection.get("candidate_or_baseline_values_read") is False
        and selection.get("processed_only_extra_values_read") is False
        and selection.get("case_identifiers_included") is False,
        "prediction_blind_selection",
    )
    _require(
        phase_weights.shape == (80,)
        and _finite_tensor(phase_weights)
        and bool((phase_weights >= 0).all().item())
        and int((phase_weights > 0).sum().item()) >= 2,
        "phase_weights",
    )
    cases = [
        _case_payload(case, int(trace), phase_weights)
        for case, trace in zip(selected_cases, traces)
    ]
    reference_tawss = torch.cat(
        [
            case["methods"]["reference"]["tawss"][case["display_mask"]]
            for case in cases
        ]
    )
    _require(_finite_tensor(reference_tawss), "reference_tawss_limits")
    tawss_min = float(reference_tawss.min().item())
    tawss_max = float(reference_tawss.max().item())
    _require(math.isfinite(tawss_min) and tawss_max > tawss_min, "tawss_range")
    layout = config["render_layout"]
    reference_traces = torch.cat(
        [case["methods"]["reference"]["signed_trace"] for case in cases]
    )
    _require(_finite_tensor(reference_traces), "reference_trace_limits")
    trace_min = float(reference_traces.min().item())
    trace_max = float(reference_traces.max().item())
    _require(math.isfinite(trace_min) and trace_max > trace_min, "trace_range")
    trace_padding = float(layout["trace_y_margin_fraction"]) * (trace_max - trace_min)
    return {
        "schema_version": "aurora.aneug_release_730_confirmatory_figure.render_payload.v1",
        "protocol_id": config["protocol_id"],
        "selection_ordinals": [int(value) for value in ordinals],
        "case_labels": list(layout["case_columns"]),
        "method_labels": list(layout["method_columns_within_case"]),
        "surface_rows": list(layout["surface_rows"]),
        "camera": {
            "projection": "orthographic",
            "azimuth_degrees": float(layout["camera_azimuth_degrees"]),
            "elevation_degrees": float(layout["camera_elevation_degrees"]),
        },
        "figure_size_inches": [
            float(layout["figure_width_inches"]),
            float(layout["figure_height_inches"]),
        ],
        "rasterized_dpi": int(layout["surface_panels_rasterized_dpi"]),
        "surface_colormap": layout["surface_colormap"],
        "tawss_limits": [tawss_min, tawss_max],
        "osi_limits": [0.0, 0.5],
        "signed_trace_limits": [trace_min - trace_padding, trace_max + trace_padding],
        "cases": cases,
        "case_identifiers_included": False,
        "candidate_or_control_used_for_selection_limits_or_camera": False,
        "paper_claim": False,
    }


def _project(coordinates: Any, azimuth: float, elevation: float) -> tuple[Any, Any]:
    import numpy as np

    azimuth_rad = math.radians(azimuth)
    elevation_rad = math.radians(elevation)
    right = np.asarray([-math.sin(azimuth_rad), math.cos(azimuth_rad), 0.0])
    view = np.asarray(
        [
            math.cos(elevation_rad) * math.cos(azimuth_rad),
            math.cos(elevation_rad) * math.sin(azimuth_rad),
            math.sin(elevation_rad),
        ]
    )
    up = np.cross(view, right)
    projected = np.stack((coordinates @ right, coordinates @ up), axis=-1)
    depth = coordinates @ view
    return projected, depth


def _surface_panel(
    axis: Any,
    case: Mapping[str, Any],
    values: torch.Tensor,
    valid: torch.Tensor,
    *,
    limits: Sequence[float],
    colormap: str,
    azimuth: float,
    elevation: float,
    xy_limits: Sequence[float],
) -> Any:
    import numpy as np
    from matplotlib.collections import PolyCollection
    from matplotlib.colors import Normalize

    coordinates = case["coordinates"].numpy()
    faces = case["faces"][case["retained_faces"]].numpy()
    projected, depth = _project(coordinates, azimuth, elevation)
    face_values = values[case["faces"][case["retained_faces"]]].mean(dim=1).numpy()
    face_valid = valid[case["faces"][case["retained_faces"]]].all(dim=1).numpy()
    face_values = np.where(face_valid, face_values, np.nan)
    order = np.argsort(depth[faces].mean(axis=1))
    collection = PolyCollection(
        projected[faces][order],
        array=face_values[order],
        cmap=colormap,
        norm=Normalize(vmin=float(limits[0]), vmax=float(limits[1]), clip=True),
        edgecolors="none",
        linewidths=0.0,
        rasterized=True,
    )
    axis.add_collection(collection)
    axis.set_xlim(float(xy_limits[0]), float(xy_limits[1]))
    axis.set_ylim(float(xy_limits[2]), float(xy_limits[3]))
    axis.set_aspect("equal", adjustable="box")
    axis.set_axis_off()
    return collection


def render_release730_confirmatory_figure(
    payload: Mapping[str, Any],
    pdf_path: str | Path,
    png_path: str | Path,
) -> dict[str, Any]:
    """Render the fixed layout; the caller must supply T0-authorized payload."""

    _require(
        payload.get("schema_version")
        == "aurora.aneug_release_730_confirmatory_figure.render_payload.v1",
        "payload_schema",
    )
    _require(payload.get("case_identifiers_included") is False, "identifier_scope")
    _require(
        payload.get("candidate_or_control_used_for_selection_limits_or_camera")
        is False,
        "display_scope",
    )
    pdf = Path(pdf_path)
    png = Path(png_path)
    _require(pdf.suffix.lower() == ".pdf" and png.suffix.lower() == ".png", "outputs")
    _require(not pdf.exists() and not png.exists(), "output_exists")
    _require(pdf.parent.is_dir() and png.parent.is_dir(), "output_parent")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize

    cases = payload["cases"]
    camera = payload["camera"]
    projected_points = []
    for case in cases:
        points, _ = _project(
            case["coordinates"][case["display_mask"]].numpy(),
            camera["azimuth_degrees"],
            camera["elevation_degrees"],
        )
        projected_points.append(points)
    stacked = np.concatenate(projected_points, axis=0)
    margin = 0.04 * max(float(np.ptp(stacked[:, 0])), float(np.ptp(stacked[:, 1])))
    xy_limits = [
        float(stacked[:, 0].min() - margin),
        float(stacked[:, 0].max() + margin),
        float(stacked[:, 1].min() - margin),
        float(stacked[:, 1].max() + margin),
    ]

    figure = plt.figure(figsize=tuple(payload["figure_size_inches"]))
    grid = figure.add_gridspec(
        3,
        9,
        height_ratios=[1.0, 1.0, 0.62],
        left=0.035,
        right=0.955,
        bottom=0.12,
        top=0.93,
        wspace=0.02,
        hspace=0.04,
    )
    method_titles = {"reference": "Ref.", "selected_control": "Control", "proposal": "Ours"}
    metric_rows = (("tawss", payload["tawss_limits"]), ("osi", payload["osi_limits"]))
    collections: dict[str, list[Any]] = {"tawss": [], "osi": []}
    for case_index, case in enumerate(cases):
        for metric_index, (metric, limits) in enumerate(metric_rows):
            for method_index, method in enumerate(payload["method_labels"]):
                column = case_index * 3 + method_index
                axis = figure.add_subplot(grid[metric_index, column])
                values = case["methods"][method][metric]
                valid = (
                    torch.isfinite(values)
                    if metric == "tawss"
                    else case["methods"][method]["osi_valid"] & torch.isfinite(values)
                )
                collection = _surface_panel(
                    axis,
                    case,
                    values,
                    valid,
                    limits=limits,
                    colormap=payload["surface_colormap"],
                    azimuth=camera["azimuth_degrees"],
                    elevation=camera["elevation_degrees"],
                    xy_limits=xy_limits,
                )
                collections[metric].append(collection)
                if metric_index == 0:
                    axis.set_title(method_titles[method], fontsize=5.2, pad=0.5)
                if method_index == 0:
                    axis.text(
                        -0.04,
                        0.5,
                        metric.upper(),
                        transform=axis.transAxes,
                        rotation=90,
                        va="center",
                        ha="right",
                        fontsize=5.0,
                    )
                if metric_index == 0 and method_index == 1:
                    axis.text(
                        0.5,
                        1.28,
                        payload["case_labels"][case_index].replace("_", " "),
                        transform=axis.transAxes,
                        ha="center",
                        va="bottom",
                        fontsize=5.4,
                        fontweight="bold",
                    )
        trace_axis = figure.add_subplot(grid[2, case_index * 3 : case_index * 3 + 3])
        phase = np.arange(80)
        styles = {
            "reference": ("black", "-"),
            "selected_control": ("#4477AA", "--"),
            "proposal": ("#CC6677", "-"),
        }
        for method in payload["method_labels"]:
            color, style = styles[method]
            trace_axis.plot(
                phase,
                case["methods"][method]["signed_trace"].numpy(),
                color=color,
                linestyle=style,
                linewidth=0.65,
                label=method_titles[method],
            )
        trace_axis.axhline(0.0, color="0.75", linewidth=0.35)
        trace_axis.set_xlim(0, 79)
        trace_axis.set_ylim(payload["signed_trace_limits"])
        trace_axis.set_xticks([0, 40, 79] if case_index == 2 else [0, 40])
        trace_axis.tick_params(labelsize=4.2, width=0.3, length=1.5, pad=0.8)
        for spine in trace_axis.spines.values():
            spine.set_linewidth(0.35)
        if case_index == 0:
            trace_axis.set_ylabel("signed WSS", fontsize=4.5, labelpad=1.0)
            trace_axis.legend(
                loc="upper center",
                ncol=3,
                fontsize=3.8,
                frameon=False,
                handlelength=1.5,
                columnspacing=0.8,
            )
        else:
            trace_axis.tick_params(labelleft=False)
        trace_axis.set_xlabel("phase", fontsize=4.5, labelpad=0.4)

    for metric, limits, vertical_position in (
        ("tawss", payload["tawss_limits"], 0.865),
        ("osi", payload["osi_limits"], 0.54),
    ):
        color_axis = figure.add_axes([0.965, vertical_position, 0.007, 0.17])
        figure.colorbar(
            ScalarMappable(
                norm=Normalize(vmin=float(limits[0]), vmax=float(limits[1])),
                cmap=payload["surface_colormap"],
            ),
            cax=color_axis,
        )
        color_axis.tick_params(labelsize=3.8, width=0.3, length=1.2, pad=0.5)
        color_axis.set_ylabel(metric.upper(), fontsize=4.0, labelpad=1.0)

    try:
        figure.savefig(pdf, dpi=int(payload["rasterized_dpi"]), metadata={"Creator": "AURORA"})
        figure.savefig(png, dpi=int(payload["rasterized_dpi"]), metadata={"Software": "AURORA"})
    finally:
        plt.close(figure)
    return {
        "schema_version": "aurora.aneug_release_730_confirmatory_figure.render_result.v1",
        "pdf_sha256": _file_sha256(pdf),
        "png_sha256": _file_sha256(png),
        "pdf_bytes": pdf.stat().st_size,
        "png_bytes": png.stat().st_size,
        "case_identifiers_included": False,
        "paper_claim": False,
    }
