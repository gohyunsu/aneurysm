"""Render traceable LaTeX macros from the complete ICCE primary-pair bundle.

The renderer accepts only the ten-terminal, five-seed validation bundle emitted
by :mod:`aurora.aneug_release_730_icce_primary_pair`.  It has no dataset path and
cannot access the historically opened test or processed-only extras.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


BUNDLE_SCHEMA = "aurora.aneug_release_730_icce_primary_pair_bundle.v1"
ANALYSIS_SCHEMA = "aurora.aneug_release_730_icce_primary_pair_analysis.v1"
PROTOCOL_ID = "aneug_release_730_icce_validation_revision_v2"
METHOD_TRANSIENT_ONLY = "T"
METHOD_REGIME_SEPARATED = "T_plus_S_regime_separated"
METHODS = (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED)
SEEDS = (20_260_901, 20_260_902, 20_260_903, 20_260_904, 20_260_905)
METRICS = (
    "field_relative_l2",
    "tawss_normalized_absolute_error",
    "osi_mae",
)


class ICCEPrimaryPairLatexError(RuntimeError):
    """Raised when a manuscript fragment lacks exact primary-pair evidence."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCEPrimaryPairLatexError(reason)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _mapping(value: Any, reason: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), reason)
    return value


def _estimate(value: Any, *, metric: str, contrast: bool) -> Mapping[str, Any]:
    estimate = _mapping(value, f"estimate:{metric}")
    point = estimate.get("point")
    low = estimate.get("ci95_low")
    high = estimate.get("ci95_high")
    _require(
        all(
            isinstance(item, (int, float)) and math.isfinite(float(item))
            for item in (point, low, high)
        )
        and float(low) <= float(high)
        and estimate.get("training_seed_count") == 5
        and estimate.get("paired_case_count") == 73
        and estimate.get("replicates") == 10_000
        and estimate.get("resampling")
        == "crossed_training_seed_and_paired_geometry_case",
        f"estimate_contract:{metric}",
    )
    if contrast:
        _require(
            estimate.get("candidate") == METHOD_REGIME_SEPARATED
            and estimate.get("comparator") == METHOD_TRANSIENT_ONLY
            and estimate.get("metric") == metric
            and estimate.get("lower_is_better") is True,
            f"contrast_contract:{metric}",
        )
    return estimate


def validate_bundle(path: Path) -> Mapping[str, Any]:
    bundle = _mapping(json.loads(path.read_text(encoding="utf-8")), "bundle_mapping")
    _require(
        bundle.get("schema_version") == BUNDLE_SCHEMA
        and bundle.get("status") == "complete_five_seed_validation_only"
        and bundle.get("protocol_id") == PROTOCOL_ID
        and _is_sha256(bundle.get("input_manifest_sha256"))
        and _is_sha256(bundle.get("protocol_sha256"))
        and _is_sha256(bundle.get("analysis_core_sha256"))
        and bundle.get("locked_test_or_extra_read") is False
        and bundle.get("case_identifiers_included") is False
        and bundle.get("full_attribution_required") is True
        and bundle.get("paper_claim") is False,
        "bundle_contract",
    )
    terminal_hashes = _mapping(
        bundle.get("input_terminal_result_sha256"), "terminal_hashes"
    )
    _require(
        len(terminal_hashes) == 10
        and all(
            isinstance(value, Mapping)
            and _is_sha256(value.get("result_sha256"))
            and _is_sha256(value.get("terminal_sha256"))
            for value in terminal_hashes.values()
        ),
        "ten_terminal_hashes",
    )
    analysis = _mapping(bundle.get("analysis"), "analysis_mapping")
    _require(
        analysis.get("schema_version") == ANALYSIS_SCHEMA
        and analysis.get("status") == "complete_five_seed_validation_only"
        and analysis.get("evidence_role")
        == "primary_pair_interim_before_full_attribution"
        and analysis.get("protocol_id") == PROTOCOL_ID
        and analysis.get("training_seeds") == list(SEEDS)
        and analysis.get("paired_case_count") == 73
        and analysis.get("bootstrap_replicates") == 10_000
        and analysis.get("bootstrap_seed") == 20_260_831
        and _is_sha256(analysis.get("validation_case_digest"))
        and analysis.get("full_attribution_required_for_secondary_contrasts")
        is True
        and analysis.get("locked_test_or_extra_read") is False
        and analysis.get("case_is_statistical_unit") is True
        and analysis.get("automatic_winner") is None
        and analysis.get("paper_claim") is False,
        "analysis_contract",
    )
    summaries = _mapping(analysis.get("method_summaries"), "method_summaries")
    contrasts = _mapping(analysis.get("proposed_minus_T"), "proposed_minus_T")
    _require(set(summaries) == set(METHODS) and set(contrasts) == set(METRICS), "method_metric_set")
    for method in METHODS:
        summary = _mapping(summaries[method], f"summary:{method}")
        for metric in METRICS:
            _estimate(summary.get(metric), metric=metric, contrast=False)
    for metric in METRICS:
        _estimate(contrasts.get(metric), metric=metric, contrast=True)
    return bundle


def _decimal(value: Any, digits: int) -> str:
    number = float(value)
    _require(math.isfinite(number), "finite_format_value")
    rendered = f"{number:.{digits}f}"
    if rendered.startswith("-0."):
        return "-." + rendered[3:]
    if rendered.startswith("0."):
        return "." + rendered[2:]
    return rendered


def _interval(estimate: Mapping[str, Any], digits: int) -> str:
    return (
        "$"
        + _decimal(estimate["point"], digits)
        + "$ [$"
        + _decimal(estimate["ci95_low"], digits)
        + ","
        + _decimal(estimate["ci95_high"], digits)
        + "$]"
    )


def render_primary_pair_latex(*, bundle_path: Path, output_path: Path) -> dict[str, Any]:
    _require(bundle_path.is_file(), "bundle_missing")
    _require(not output_path.exists(), "output_exists")
    bundle = validate_bundle(bundle_path)
    analysis = bundle["analysis"]
    summaries = analysis["method_summaries"]
    contrasts = analysis["proposed_minus_T"]
    t = summaries[METHOD_TRANSIENT_ONLY]
    separated = summaries[METHOD_REGIME_SEPARATED]
    values = {
        "iccePrimaryTField": _decimal(t[METRICS[0]]["point"], 4),
        "iccePrimaryTTAWSS": _decimal(t[METRICS[1]]["point"], 4),
        "iccePrimaryTOSI": _decimal(t[METRICS[2]]["point"], 5),
        "iccePrimarySeparatedField": _decimal(separated[METRICS[0]]["point"], 4),
        "iccePrimarySeparatedTAWSS": _decimal(separated[METRICS[1]]["point"], 4),
        "iccePrimarySeparatedOSI": _decimal(separated[METRICS[2]]["point"], 5),
        "iccePrimaryFieldDelta": _interval(contrasts[METRICS[0]], 4),
        "iccePrimaryTAWSSDelta": _interval(contrasts[METRICS[1]], 4),
        "iccePrimaryOSIDelta": _interval(contrasts[METRICS[2]], 5),
    }
    lines = [
        "% Generated from the complete five-seed validation primary-pair bundle.",
        f"% input_sha256={_sha256(bundle_path)}",
    ]
    lines.extend(f"\\newcommand{{\\{name}}}{{{value}}}" for name, value in values.items())
    payload = "\n".join(lines) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{output_path.name}.", dir=output_path.parent)
    )
    temporary_path = temporary_directory / output_path.name
    try:
        temporary_path.write_text(payload, encoding="utf-8")
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)
        temporary_directory.rmdir()
    return {
        "input_sha256": _sha256(bundle_path),
        "output_sha256": _sha256(output_path),
        "macro_count": len(values),
        "locked_test_or_extra_read": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    print(
        json.dumps(
            render_primary_pair_latex(
                bundle_path=arguments.bundle,
                output_path=arguments.output,
            ),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
