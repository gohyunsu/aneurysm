"""Reproducible, identifier-free manuscript artifacts for the ICCE v2 study.

The builder accepts only the complete validation-only 72-cell experiment grid.
It recomputes the registered analyses, emits case- and seed-level CSV files,
creates LaTeX-ready tables, and materializes the data payload for Figure 2.  It
has no locked-test or processed-extra input and refuses an existing output
directory so an old evidence bundle can never be overwritten.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_release_730_icce_analysis import (
    ALL_METRICS,
    ATTRIBUTION_COMPARATORS,
    PRIMARY_METRICS,
    REPORT_METRICS,
    _validate_result,
    analyze_label_efficiency,
    analyze_lambda_sensitivity,
    analyze_main_attribution,
)
from aurora.aneug_release_730_icce_revision import (
    LABEL_COUNTS,
    LAMBDA_SEEDS,
    LAMBDA_VALUES,
    METHOD_IDS,
    METHOD_REGIME_SEPARATED,
    METHOD_TRANSIENT_ONLY,
    TRAINING_SEEDS,
    validate_protocol_config,
)


ARTIFACT_SCHEMA = "aurora.aneug_release_730_icce_manuscript_artifacts.v1"
INPUT_SCHEMA = "aurora.private.aneug_release_730_icce_artifact_inputs.v1"
FIGURE_SCHEMA = "aurora.aneug_release_730_icce_figure2_payload.v1"

METHOD_LABELS = {
    "T": "T",
    "T_plus_M": "T+M",
    "T_plus_S_regime_separated": "T+S separated",
    "T_plus_S_shared_decoder": "T+S shared",
    "S_then_T": "S to T",
    "T_plus_S_shuffled_labels": "T+S shuffled",
}


class ICCEArtifactError(RuntimeError):
    """Raised when a manuscript artifact cannot be traced to complete evidence."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCEArtifactError(reason)


def _canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _digest_payload(payload: Any) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _json_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _csv_text(fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _same_payload(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return _canonical_bytes(left) == _canonical_bytes(right)


def _validate_reuse_aliases(
    main: Mapping[str, Mapping[int, Mapping[str, Any]]],
    labels: Mapping[int, Mapping[str, Mapping[int, Mapping[str, Any]]]],
    lambdas: Mapping[float, Mapping[int, Mapping[str, Any]]],
) -> None:
    _require(100 in labels and 1.0 in lambdas, "reuse_aliases")
    for seed in TRAINING_SEEDS:
        for method in (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED):
            _require(
                _same_payload(main[method][seed], labels[100][method][seed]),
                f"label_100_alias_{method}_{seed}",
            )
    for seed in LAMBDA_SEEDS:
        _require(
            _same_payload(
                main[METHOD_REGIME_SEPARATED][seed], lambdas[1.0][seed]
            ),
            f"lambda_1_alias_{seed}",
        )


def _unique_cells(
    main: Mapping[str, Mapping[int, Mapping[str, Any]]],
    labels: Mapping[int, Mapping[str, Mapping[int, Mapping[str, Any]]]],
    lambdas: Mapping[float, Mapping[int, Mapping[str, Any]]],
) -> list[tuple[str, str, int, int, float, Mapping[str, Any]]]:
    cells: list[tuple[str, str, int, int, float, Mapping[str, Any]]] = []
    for method in METHOD_IDS:
        for seed in TRAINING_SEEDS:
            cells.append(("main_attribution", method, seed, 100, 1.0, main[method][seed]))
    for percent in (10, 25, 50):
        for method in (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED):
            for seed in TRAINING_SEEDS:
                cells.append(
                    ("label_efficiency", method, seed, percent, 1.0, labels[percent][method][seed])
                )
    for coefficient in (0.25, 0.5, 2.0, 4.0):
        for seed in LAMBDA_SEEDS:
            cells.append(
                (
                    "lambda_sensitivity",
                    METHOD_REGIME_SEPARATED,
                    seed,
                    100,
                    coefficient,
                    lambdas[coefficient][seed],
                )
            )
    _require(len(cells) == 72, "unique_cell_count")
    keys = {(group, method, seed, percent, coefficient) for group, method, seed, percent, coefficient, _ in cells}
    _require(len(keys) == 72, "unique_cell_keys")
    return cells


def _case_and_seed_rows(
    cells: Sequence[tuple[str, str, int, int, float, Mapping[str, Any]]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    case_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []
    result_digests: dict[str, str] = {}
    for group, method, seed, percent, coefficient, result in cells:
        parsed = _validate_result(
            result,
            method_id=method,
            training_seed=seed,
            unique_transient_cases=LABEL_COUNTS[percent],
        )
        _require(
            math.isclose(float(result.get("auxiliary_coefficient", coefficient)), coefficient),
            "auxiliary_coefficient",
        )
        cell_key = f"{group}__{method}__p{percent}__lambda{coefficient:g}__seed{seed}"
        digest = _digest_payload(result)
        result_digests[cell_key] = digest
        for case_position, row in enumerate(parsed):
            case_rows.append(
                {
                    "experiment_group": group,
                    "method_id": method,
                    "training_seed": seed,
                    "label_percent": percent,
                    "auxiliary_coefficient": f"{coefficient:g}",
                    "validation_case_position": case_position,
                    **{metric: f"{float(row[metric]):.17g}" for metric in REPORT_METRICS},
                    "source_result_sha256": digest,
                }
            )
        aggregate = result["validation"]["aggregate"]
        seed_rows.append(
            {
                "experiment_group": group,
                "method_id": method,
                "training_seed": seed,
                "label_percent": percent,
                "auxiliary_coefficient": f"{coefficient:g}",
                "transient_encoder_forwards": int(result["transient_encoder_forwards"]),
                "auxiliary_encoder_forwards": int(result["auxiliary_encoder_forwards"]),
                "optimizer_updates": int(result["optimizer_updates"]),
                "total_epochs": int(result["total_epochs"]),
                "elapsed_wall_seconds": f"{float(result['elapsed_wall_seconds']):.17g}",
                "peak_training_gpu_memory_bytes": int(result["peak_gpu_memory_bytes"]),
                **{
                    metric: f"{float(aggregate[metric]):.17g}"
                    for metric in ALL_METRICS
                },
                "osi_invalid_reference_support_area_fraction": f"{1.0 - float(aggregate['osi_coverage']):.17g}",
                "source_result_sha256": digest,
            }
        )
    _require(len(case_rows) == 72 * 73 and len(seed_rows) == 72, "compiled_rows")
    return case_rows, seed_rows, result_digests


def _estimate_rows(analysis: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for contrast_name, metrics in analysis["proposed_minus_comparator"].items():
        for metric in PRIMARY_METRICS:
            estimate = metrics[metric]
            rows.append(
                {
                    "contrast": contrast_name,
                    "candidate": estimate["candidate"],
                    "comparator": estimate["comparator"],
                    "metric": metric,
                    "mean_difference": f"{float(estimate['point']):.17g}",
                    "ci95_low": f"{float(estimate['ci95_low']):.17g}",
                    "ci95_high": f"{float(estimate['ci95_high']):.17g}",
                    "training_seed_count": int(estimate["training_seed_count"]),
                    "paired_case_count": int(estimate["paired_case_count"]),
                    "bootstrap_replicates": int(estimate["replicates"]),
                }
            )
    _require(len(rows) == 15, "attribution_contrast_rows")
    return rows


def _label_rows(analysis: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for percent in (10, 25, 50, 100):
        point = analysis["curves"][str(percent)]
        for metric in PRIMARY_METRICS:
            for method in (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED):
                estimate = point["methods"][method][metric]
                rows.append(
                    {
                        "label_percent": percent,
                        "unique_transient_cases": point["unique_transient_cases"],
                        "estimand": "raw_method_mean",
                        "method_or_contrast": method,
                        "metric": metric,
                        "point": f"{float(estimate['point']):.17g}",
                        "ci95_low": f"{float(estimate['ci95_low']):.17g}",
                        "ci95_high": f"{float(estimate['ci95_high']):.17g}",
                    }
                )
            estimate = point["proposed_minus_T"][metric]
            rows.append(
                {
                    "label_percent": percent,
                    "unique_transient_cases": point["unique_transient_cases"],
                    "estimand": "paired_difference",
                    "method_or_contrast": "T_plus_S_regime_separated_minus_T",
                    "metric": metric,
                    "point": f"{float(estimate['point']):.17g}",
                    "ci95_low": f"{float(estimate['ci95_low']):.17g}",
                    "ci95_high": f"{float(estimate['ci95_high']):.17g}",
                }
            )
    _require(len(rows) == 36, "label_rows")
    return rows


def _lambda_rows(analysis: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for coefficient in LAMBDA_VALUES:
        point = analysis["lambda_results"][str(float(coefficient))]
        for metric in PRIMARY_METRICS:
            estimate = point["metrics"][metric]
            difference = point["minus_lambda_1"][metric]
            rows.append(
                {
                    "auxiliary_coefficient": f"{coefficient:g}",
                    "metric": metric,
                    "point": f"{float(estimate['point']):.17g}",
                    "ci95_low": f"{float(estimate['ci95_low']):.17g}",
                    "ci95_high": f"{float(estimate['ci95_high']):.17g}",
                    "minus_lambda_1": f"{float(difference['point']):.17g}",
                    "minus_lambda_1_ci95_low": f"{float(difference['ci95_low']):.17g}",
                    "minus_lambda_1_ci95_high": f"{float(difference['ci95_high']):.17g}",
                }
            )
    _require(len(rows) == 15, "lambda_rows")
    return rows


def _gradient_rows(analysis: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for seed in TRAINING_SEEDS:
        value = analysis["shared_decoder_gradient_diagnostic_by_seed"][str(seed)]
        rows.append(
            {
                "training_seed": seed,
                "measurement_count": int(value["count"]),
                "mean_cosine": f"{float(value['mean']):.17g}",
                "median_cosine": f"{float(value['median']):.17g}",
                "fraction_below_zero": f"{float(value['fraction_below_zero']):.17g}",
            }
        )
    return rows


def _format_estimate(estimate: Mapping[str, Any], digits: int = 4) -> str:
    return f"{float(estimate['point']):.{digits}f}"


def _format_delta(estimate: Mapping[str, Any], digits: int = 4) -> str:
    return (
        f"{float(estimate['point']):.{digits}f} "
        f"[{float(estimate['ci95_low']):.{digits}f}, "
        f"{float(estimate['ci95_high']):.{digits}f}]"
    )


def _latex_tables(
    main: Mapping[str, Any], labels: Mapping[str, Any], sensitivity: Mapping[str, Any]
) -> dict[str, str]:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Method & Field & TAWSS & OSI & Proposed$-$method field [95\% CI] \\",
        r"\midrule",
    ]
    for method in METHOD_IDS:
        summary = main["method_summaries"][method]
        if method == METHOD_REGIME_SEPARATED:
            delta = "--"
        else:
            estimate = main["proposed_minus_comparator"][
                f"{METHOD_REGIME_SEPARATED}_minus_{method}"
            ]["field_relative_l2"]
            delta = _format_delta(estimate)
        lines.append(
            "{} & {} & {} & {} & {} \\\\".format(
                METHOD_LABELS[method],
                _format_estimate(summary["field_relative_l2"]),
                _format_estimate(summary["tawss_normalized_absolute_error"]),
                _format_estimate(summary["osi_mae"], 5),
                delta,
            )
        )
    lines.extend((r"\bottomrule", r"\end{tabular}", ""))

    label_lines = [
        r"\begin{tabular}{rrrrr}",
        r"\toprule",
        r"Labels & Cases & T & T+S & T+S$-$T [95\% CI] \\",
        r"\midrule",
    ]
    for percent in (10, 25, 50, 100):
        point = labels["curves"][str(percent)]
        label_lines.append(
            "{}\\% & {} & {} & {} & {} \\\\".format(
                percent,
                point["unique_transient_cases"],
                _format_estimate(point["methods"][METHOD_TRANSIENT_ONLY]["field_relative_l2"]),
                _format_estimate(point["methods"][METHOD_REGIME_SEPARATED]["field_relative_l2"]),
                _format_delta(point["proposed_minus_T"]["field_relative_l2"]),
            )
        )
    label_lines.extend((r"\bottomrule", r"\end{tabular}", ""))

    sensitivity_lines = [
        r"\begin{tabular}{rrrr}",
        r"\toprule",
        r"$\lambda$ & Field & TAWSS & OSI \\",
        r"\midrule",
    ]
    for coefficient in LAMBDA_VALUES:
        metrics = sensitivity["lambda_results"][str(float(coefficient))]["metrics"]
        sensitivity_lines.append(
            "{} & {} & {} & {} \\\\".format(
                f"{coefficient:g}",
                _format_estimate(metrics["field_relative_l2"]),
                _format_estimate(metrics["tawss_normalized_absolute_error"]),
                _format_estimate(metrics["osi_mae"], 5),
            )
        )
    sensitivity_lines.extend((r"\bottomrule", r"\end{tabular}", ""))
    return {
        "table_2_validation_attribution.tex": "\n".join(lines),
        "table_label_efficiency.tex": "\n".join(label_lines),
        "table_lambda_sensitivity.tex": "\n".join(sensitivity_lines),
    }


def _figure_payload(main: Mapping[str, Any], labels: Mapping[str, Any]) -> dict[str, Any]:
    label_points = []
    for percent in (10, 25, 50, 100):
        point = labels["curves"][str(percent)]
        label_points.append(
            {
                "label_percent": percent,
                "unique_transient_cases": point["unique_transient_cases"],
                "T": point["methods"][METHOD_TRANSIENT_ONLY]["field_relative_l2"],
                "T_plus_S_regime_separated": point["methods"][METHOD_REGIME_SEPARATED]["field_relative_l2"],
            }
        )
    contrasts = []
    for comparator in ATTRIBUTION_COMPARATORS:
        estimate = main["proposed_minus_comparator"][
            f"{METHOD_REGIME_SEPARATED}_minus_{comparator}"
        ]["field_relative_l2"]
        contrasts.append(
            {
                "comparator": comparator,
                "label": f"T+S separated - {METHOD_LABELS[comparator]}",
                "estimate": estimate,
            }
        )
    return {
        "schema_version": FIGURE_SCHEMA,
        "status": "complete_validation_only",
        "metric": "field_relative_l2",
        "lower_is_better": True,
        "label_efficiency": label_points,
        "attribution_contrasts": contrasts,
        "bootstrap_replicates": 10_000,
        "case_is_statistical_unit": True,
        "locked_test_or_extra_read": False,
        "automatic_paper_claim": False,
    }


def render_figure2(payload: Mapping[str, Any], pdf: str | Path, png: str | Path) -> None:
    """Render the registered label curve and attribution-delta panel."""

    _require(
        payload.get("schema_version") == FIGURE_SCHEMA
        and payload.get("status") == "complete_validation_only"
        and payload.get("metric") == "field_relative_l2"
        and payload.get("locked_test_or_extra_read") is False
        and len(payload.get("label_efficiency", ())) == 4
        and len(payload.get("attribution_contrasts", ())) == 5,
        "figure_payload",
    )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(1, 2, figsize=(7.16, 2.65), constrained_layout=True)
    palette = {"T": "#64748b", "T_plus_S_regime_separated": "#0f766e"}
    for method, label in (("T", "T"), ("T_plus_S_regime_separated", "T+S separated")):
        x = [int(point["unique_transient_cases"]) for point in payload["label_efficiency"]]
        estimates = [point[method] for point in payload["label_efficiency"]]
        y = [float(value["point"]) for value in estimates]
        low = [max(0.0, value - float(estimate["ci95_low"])) for value, estimate in zip(y, estimates, strict=True)]
        high = [max(0.0, float(estimate["ci95_high"]) - value) for value, estimate in zip(y, estimates, strict=True)]
        axes[0].errorbar(x, y, yerr=[low, high], marker="o", capsize=2.5, linewidth=1.5, label=label, color=palette[method])
    axes[0].set(xlabel="Transient training geometries", ylabel="Field relative $L_2$", title="Label efficiency")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].grid(axis="y", alpha=0.22)

    contrast_payload = list(payload["attribution_contrasts"])
    y_positions = list(range(len(contrast_payload)))
    points = [float(item["estimate"]["point"]) for item in contrast_payload]
    xerr = [
        [max(0.0, point - float(item["estimate"]["ci95_low"])) for point, item in zip(points, contrast_payload, strict=True)],
        [max(0.0, float(item["estimate"]["ci95_high"]) - point) for point, item in zip(points, contrast_payload, strict=True)],
    ]
    axes[1].errorbar(points, y_positions, xerr=xerr, fmt="o", capsize=2.5, color="#0f766e")
    axes[1].axvline(0.0, color="#334155", linewidth=0.8, linestyle="--")
    axes[1].set_yticks(y_positions, [METHOD_LABELS[item["comparator"]] for item in contrast_payload])
    axes[1].invert_yaxis()
    axes[1].set(xlabel="T+S separated minus comparator", title="Validation attribution")
    axes[1].grid(axis="x", alpha=0.22)
    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.tick_params(labelsize=8)
        axis.title.set_fontsize(9)
        axis.xaxis.label.set_fontsize(8)
        axis.yaxis.label.set_fontsize(8)
    pdf_path, png_path = Path(pdf), Path(png)
    _require(not pdf_path.exists() and not png_path.exists(), "figure_output_exists")
    figure.savefig(pdf_path, metadata={"Creator": "AURORA ICCE artifact compiler"})
    figure.savefig(png_path, dpi=600, metadata={"Software": "AURORA"})
    plt.close(figure)


def compile_manuscript_artifacts(
    *,
    main_results: Mapping[str, Mapping[int, Mapping[str, Any]]],
    label_results: Mapping[int, Mapping[str, Mapping[int, Mapping[str, Any]]]],
    lambda_results: Mapping[float, Mapping[int, Mapping[str, Any]]],
    protocol: Mapping[str, Any],
    output_directory: str | Path,
    render_figure: bool = False,
) -> dict[str, Any]:
    """Compile all quantitative manuscript artifacts from complete v2 results."""

    output = Path(output_directory)
    _require(not output.exists(), "output_directory_exists")
    validate_protocol_config(protocol)
    _validate_reuse_aliases(main_results, label_results, lambda_results)
    main_analysis = analyze_main_attribution(main_results, protocol)
    label_analysis = analyze_label_efficiency(label_results, protocol)
    lambda_analysis = analyze_lambda_sensitivity(lambda_results, protocol)
    cells = _unique_cells(main_results, label_results, lambda_results)
    case_rows, seed_rows, result_digests = _case_and_seed_rows(cells)
    contrast_rows = _estimate_rows(main_analysis)
    label_rows = _label_rows(label_analysis)
    lambda_rows = _lambda_rows(lambda_analysis)
    gradient_rows = _gradient_rows(main_analysis)
    figure_payload = _figure_payload(main_analysis, label_analysis)
    tables = _latex_tables(main_analysis, label_analysis, lambda_analysis)

    case_fields = [
        "experiment_group", "method_id", "training_seed", "label_percent",
        "auxiliary_coefficient", "validation_case_position", *REPORT_METRICS,
        "source_result_sha256",
    ]
    seed_fields = [
        "experiment_group", "method_id", "training_seed", "label_percent",
        "auxiliary_coefficient", "transient_encoder_forwards",
        "auxiliary_encoder_forwards", "optimizer_updates", "total_epochs",
        "elapsed_wall_seconds", "peak_training_gpu_memory_bytes", *ALL_METRICS,
        "osi_invalid_reference_support_area_fraction", "source_result_sha256",
    ]
    files: dict[str, str] = {
        "analysis_main_attribution.json": _json_text(main_analysis),
        "analysis_label_efficiency.json": _json_text(label_analysis),
        "analysis_lambda_sensitivity.json": _json_text(lambda_analysis),
        "per_case_metrics.csv": _csv_text(case_fields, case_rows),
        "per_seed_metrics.csv": _csv_text(seed_fields, seed_rows),
        "attribution_contrasts.csv": _csv_text(
            ("contrast", "candidate", "comparator", "metric", "mean_difference", "ci95_low", "ci95_high", "training_seed_count", "paired_case_count", "bootstrap_replicates"),
            contrast_rows,
        ),
        "label_efficiency.csv": _csv_text(
            ("label_percent", "unique_transient_cases", "estimand", "method_or_contrast", "metric", "point", "ci95_low", "ci95_high"),
            label_rows,
        ),
        "lambda_sensitivity.csv": _csv_text(
            ("auxiliary_coefficient", "metric", "point", "ci95_low", "ci95_high", "minus_lambda_1", "minus_lambda_1_ci95_low", "minus_lambda_1_ci95_high"),
            lambda_rows,
        ),
        "gradient_diagnostics.csv": _csv_text(
            ("training_seed", "measurement_count", "mean_cosine", "median_cosine", "fraction_below_zero"),
            gradient_rows,
        ),
        "figure2_payload.json": _json_text(figure_payload),
        **tables,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    try:
        for name, content in files.items():
            (temporary / name).write_text(content, encoding="utf-8", newline="\n")
        if render_figure:
            render_figure2(
                figure_payload,
                temporary / "figure2_label_efficiency_attribution.pdf",
                temporary / "figure2_label_efficiency_attribution.png",
            )
        output_hashes = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(temporary.iterdir())
            if path.is_file()
        }
        provenance = {
            "schema_version": ARTIFACT_SCHEMA,
            "status": "complete_validation_only",
            "protocol_id": protocol["protocol_id"],
            "unique_scientific_cell_count": 72,
            "per_case_row_count": len(case_rows),
            "per_seed_row_count": len(seed_rows),
            "input_result_sha256": result_digests,
            "output_sha256_before_provenance": output_hashes,
            "locked_test_or_extra_read": False,
            "case_identifiers_included": False,
            "vertices_or_phases_are_statistical_units": False,
            "bootstrap_replicates": 10_000,
            "automatic_winner": None,
            "paper_claim": False,
        }
        (temporary / "provenance.json").write_text(
            _json_text(provenance), encoding="utf-8", newline="\n"
        )
        os.replace(temporary, output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return provenance


def load_artifact_inputs(manifest_path: str | Path) -> dict[str, Any]:
    """Load a private path manifest while returning identifier-free result objects."""

    path = Path(manifest_path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(
        payload.get("schema_version") == INPUT_SCHEMA
        and set(payload) == {
            "schema_version", "protocol", "main_attribution",
            "label_efficiency", "lambda_sensitivity",
        },
        "input_manifest_schema",
    )

    def resolve(value: str) -> Path:
        target = Path(value)
        return target if target.is_absolute() else path.parent / target

    def load(value: str) -> Mapping[str, Any]:
        result = json.loads(resolve(value).read_text(encoding="utf-8"))
        _require(isinstance(result, Mapping), "result_json")
        return result

    protocol = json.loads(resolve(payload["protocol"]).read_text(encoding="utf-8"))
    main = {
        method: {int(seed): load(result_path) for seed, result_path in seeds.items()}
        for method, seeds in payload["main_attribution"].items()
    }
    labels = {
        int(percent): {
            method: {int(seed): load(result_path) for seed, result_path in seeds.items()}
            for method, seeds in methods.items()
        }
        for percent, methods in payload["label_efficiency"].items()
    }
    lambdas = {
        float(coefficient): {
            int(seed): load(result_path) for seed, result_path in seeds.items()
        }
        for coefficient, seeds in payload["lambda_sensitivity"].items()
    }
    return {
        "protocol": protocol,
        "main_results": main,
        "label_results": labels,
        "lambda_results": lambdas,
    }
