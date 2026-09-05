import hashlib
import json
from pathlib import Path

import pytest

from aurora.aneug_release_730_icce_primary_pair_latex import (
    ICCEPrimaryPairLatexError,
    render_primary_pair_latex,
)


METRICS = (
    "field_relative_l2",
    "tawss_normalized_absolute_error",
    "osi_mae",
)


def _estimate(point: float, *, metric: str | None = None) -> dict:
    value = {
        "point": point,
        "ci95_low": point - 0.01,
        "ci95_high": point + 0.01,
        "per_seed_points": [point] * 5,
        "training_seed_count": 5,
        "paired_case_count": 73,
        "replicates": 10_000,
        "bootstrap_seed": 20260831,
        "resampling": "crossed_training_seed_and_paired_geometry_case",
        "population_inference": False,
    }
    if metric is not None:
        value.update(
            {
                "candidate": "T_plus_S_regime_separated",
                "comparator": "T",
                "metric": metric,
                "lower_is_better": True,
            }
        )
    return value


def _bundle() -> dict:
    summaries = {
        "T": {
            metric: _estimate(value)
            for metric, value in zip(METRICS, (0.30123, 0.18456, 0.00876))
        },
        "T_plus_S_regime_separated": {
            metric: _estimate(value)
            for metric, value in zip(METRICS, (0.23456, 0.13210, 0.00789))
        },
    }
    terminal_hashes = {
        f"method{method}:seed{seed}": {
            "result_sha256": hashlib.sha256(f"r{method}{seed}".encode()).hexdigest(),
            "terminal_sha256": hashlib.sha256(f"t{method}{seed}".encode()).hexdigest(),
        }
        for method in range(2)
        for seed in range(5)
    }
    return {
        "schema_version": "aurora.aneug_release_730_icce_primary_pair_bundle.v1",
        "status": "complete_five_seed_validation_only",
        "protocol_id": "aneug_release_730_icce_validation_revision_v2",
        "analysis": {
            "schema_version": "aurora.aneug_release_730_icce_primary_pair_analysis.v1",
            "protocol_id": "aneug_release_730_icce_validation_revision_v2",
            "status": "complete_five_seed_validation_only",
            "evidence_role": "primary_pair_interim_before_full_attribution",
            "method_summaries": summaries,
            "proposed_minus_T": {
                metric: _estimate(value, metric=metric)
                for metric, value in zip(METRICS, (-0.06667, -0.05246, -0.00087))
            },
            "training_seeds": [20260901, 20260902, 20260903, 20260904, 20260905],
            "paired_case_count": 73,
            "validation_case_digest": "1" * 64,
            "bootstrap_replicates": 10_000,
            "bootstrap_seed": 20260831,
            "full_attribution_required_for_secondary_contrasts": True,
            "locked_test_or_extra_read": False,
            "case_is_statistical_unit": True,
            "automatic_winner": None,
            "paper_claim": False,
        },
        "input_manifest_sha256": "2" * 64,
        "protocol_sha256": "3" * 64,
        "input_terminal_result_sha256": terminal_hashes,
        "analysis_core_sha256": "4" * 64,
        "locked_test_or_extra_read": False,
        "case_identifiers_included": False,
        "full_attribution_required": True,
        "paper_claim": False,
    }


def test_renders_traceable_primary_pair_macros(tmp_path: Path) -> None:
    bundle = tmp_path / "primary_pair.json"
    bundle.write_text(json.dumps(_bundle(), sort_keys=True, indent=2) + "\n")
    output = tmp_path / "primary_pair.tex"
    provenance = render_primary_pair_latex(bundle_path=bundle, output_path=output)
    tex = output.read_text()
    assert provenance["macro_count"] == 9
    assert provenance["locked_test_or_extra_read"] is False
    assert f"input_sha256={hashlib.sha256(bundle.read_bytes()).hexdigest()}" in tex
    assert r"\newcommand{\iccePrimaryTField}{.3012}" in tex
    assert r"\newcommand{\iccePrimarySeparatedOSI}{.00789}" in tex
    assert r"\newcommand{\iccePrimaryFieldDelta}{$-.0667$ [$-.0767,-.0567$]}" in tex


def test_rejects_test_access_or_overwrite(tmp_path: Path) -> None:
    payload = _bundle()
    payload["locked_test_or_extra_read"] = True
    bundle = tmp_path / "primary_pair.json"
    bundle.write_text(json.dumps(payload))
    with pytest.raises(ICCEPrimaryPairLatexError, match="bundle_contract"):
        render_primary_pair_latex(bundle_path=bundle, output_path=tmp_path / "out.tex")

    payload["locked_test_or_extra_read"] = False
    bundle.write_text(json.dumps(payload))
    output = tmp_path / "out.tex"
    output.write_text("existing\n")
    with pytest.raises(ICCEPrimaryPairLatexError, match="output_exists"):
        render_primary_pair_latex(bundle_path=bundle, output_path=output)
