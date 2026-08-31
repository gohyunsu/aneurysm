import csv
import importlib.util
import json
from pathlib import Path

import pytest

from aurora.aneug_release_730_icce_analysis import ALL_METRICS
from aurora.aneug_release_730_icce_artifacts import (
    ICCEArtifactError,
    compile_manuscript_artifacts,
    render_figure2,
)
from aurora.aneug_release_730_icce_revision import (
    LABEL_COUNTS,
    LAMBDA_SEEDS,
    METHOD_IDS,
    METHOD_REGIME_SEPARATED,
    METHOD_STEADY_THEN_TRANSIENT,
    METHOD_TRANSIENT_ONLY,
    TRAINING_SEEDS,
    expected_exposure_ledger,
)


ROOT = Path(__file__).resolve().parents[1]


def _protocol() -> dict:
    return json.loads(
        (ROOT / "configs/aneug_release_730_icce_validation_revision_v2.json").read_text()
    )


def _result(
    method: str,
    seed: int,
    *,
    percent: int,
    coefficient: float,
    offset: float,
) -> dict:
    ledger = expected_exposure_ledger(
        method, unique_transient_cases=LABEL_COUNTS[percent]
    )
    seed_index = TRAINING_SEEDS.index(seed)
    rows = []
    for case_position in range(73):
        base = 0.15 + offset + seed_index * 0.001 + case_position * 0.0001
        rows.append(
            {
                "field_relative_l2": base,
                "tawss_normalized_absolute_error": base * 0.7,
                "osi_mae": base * 0.03,
                "osi_coverage": 0.99,
                "mean_wss_vector_error": base * 0.8,
                "low_tawss_quartile_field_relative_l2": base * 1.2,
                "peak_systolic_wss_relative_l2": base * 1.1,
                "mesh_normal_component_relative_l2": base * 0.5,
                "mean_vector_tawss_normalized_l2": base * 0.75,
            }
        )
    aggregate = {
        metric: sum(row[metric] for row in rows) / 73 for metric in ALL_METRICS
    }
    updates = 502 if method == METHOD_STEADY_THEN_TRANSIENT else 251
    return {
        "schema_version": "aurora.private.aneug_release_730_icce_fixed_budget_result.v2",
        "status": "complete_validation_only",
        **ledger.as_dict(),
        "selected_epoch": 251,
        "training_seed": seed,
        "label_percent": percent,
        "train_case_count": LABEL_COUNTS[percent],
        "validation_case_count": 73,
        "validation_case_digest": "a" * 64,
        "auxiliary_coefficient": coefficient,
        "transient_encoder_forwards": ledger.transient_exposures,
        "auxiliary_encoder_forwards": ledger.auxiliary_exposures,
        "optimizer_updates": updates,
        "total_epochs": 502 if method == METHOD_STEADY_THEN_TRANSIENT else 251,
        "elapsed_wall_seconds": 1_000.0 + seed_index,
        "peak_gpu_memory_bytes": 123_456_789,
        "validation": {
            "case_count": 73,
            "aggregate": aggregate,
            "per_case_without_identifiers": rows,
        },
        "decoder_gradient_diagnostic": (
            {
                "count": 146_584,
                "mean": -0.1,
                "median": -0.08,
                "fraction_below_zero": 0.6,
            }
            if method == "T_plus_S_shared_decoder"
            else None
        ),
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
    }


def _inputs() -> tuple[dict, dict, dict]:
    offsets = {
        "T": 0.10,
        "T_plus_M": 0.08,
        "T_plus_S_regime_separated": 0.02,
        "T_plus_S_shared_decoder": 0.07,
        "S_then_T": 0.09,
        "T_plus_S_shuffled_labels": 0.095,
    }
    main = {
        method: {
            seed: _result(
                method,
                seed,
                percent=100,
                coefficient=1.0,
                offset=offsets[method],
            )
            for seed in TRAINING_SEEDS
        }
        for method in METHOD_IDS
    }
    labels = {}
    for percent in (10, 25, 50):
        labels[percent] = {
            method: {
                seed: _result(
                    method,
                    seed,
                    percent=percent,
                    coefficient=1.0,
                    offset=offsets[method] + percent / 10_000,
                )
                for seed in TRAINING_SEEDS
            }
            for method in (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED)
        }
    labels[100] = {
        method: dict(main[method])
        for method in (METHOD_TRANSIENT_ONLY, METHOD_REGIME_SEPARATED)
    }
    lambdas = {}
    for coefficient in (0.25, 0.5, 2.0, 4.0):
        lambdas[coefficient] = {
            seed: _result(
                METHOD_REGIME_SEPARATED,
                seed,
                percent=100,
                coefficient=coefficient,
                offset=0.02 + abs(coefficient - 1.0) * 0.01,
            )
            for seed in LAMBDA_SEEDS
        }
    lambdas[1.0] = {
        seed: main[METHOD_REGIME_SEPARATED][seed] for seed in LAMBDA_SEEDS
    }
    return main, labels, lambdas


def test_compiler_emits_traceable_72_cell_bundle(tmp_path: Path) -> None:
    main, labels, lambdas = _inputs()
    output = tmp_path / "bundle"
    provenance = compile_manuscript_artifacts(
        main_results=main,
        label_results=labels,
        lambda_results=lambdas,
        protocol=_protocol(),
        output_directory=output,
    )
    assert provenance["unique_scientific_cell_count"] == 72
    assert provenance["per_case_row_count"] == 72 * 73
    assert provenance["case_identifiers_included"] is False
    with (output / "per_case_metrics.csv").open(newline="") as stream:
        case_rows = list(csv.DictReader(stream))
    with (output / "per_seed_metrics.csv").open(newline="") as stream:
        seed_rows = list(csv.DictReader(stream))
    assert len(case_rows) == 72 * 73
    assert len(seed_rows) == 72
    assert {int(row["validation_case_position"]) for row in case_rows} == set(range(73))
    assert "case_id" not in case_rows[0]
    assert (output / "table_2_validation_attribution.tex").is_file()
    assert (output / "figure2_payload.json").is_file()
    with pytest.raises(ICCEArtifactError, match="output_directory_exists"):
        compile_manuscript_artifacts(
            main_results=main,
            label_results=labels,
            lambda_results=lambdas,
            protocol=_protocol(),
            output_directory=output,
        )


def test_compiler_rejects_nonidentical_reuse_alias(tmp_path: Path) -> None:
    main, labels, lambdas = _inputs()
    labels[100][METHOD_TRANSIENT_ONLY][TRAINING_SEEDS[0]] = dict(
        labels[100][METHOD_TRANSIENT_ONLY][TRAINING_SEEDS[0]], elapsed_wall_seconds=9.0
    )
    with pytest.raises(ICCEArtifactError, match="label_100_alias"):
        compile_manuscript_artifacts(
            main_results=main,
            label_results=labels,
            lambda_results=lambdas,
            protocol=_protocol(),
            output_directory=tmp_path / "never-created",
        )


@pytest.mark.skipif(
    importlib.util.find_spec("matplotlib") is None,
    reason="matplotlib is optional in the contract-test environment",
)
def test_figure2_renderer_uses_compiled_validation_payload(tmp_path: Path) -> None:
    main, labels, lambdas = _inputs()
    output = tmp_path / "bundle"
    compile_manuscript_artifacts(
        main_results=main,
        label_results=labels,
        lambda_results=lambdas,
        protocol=_protocol(),
        output_directory=output,
    )
    payload = json.loads((output / "figure2_payload.json").read_text())
    pdf = tmp_path / "figure2.pdf"
    png = tmp_path / "figure2.png"
    render_figure2(payload, pdf, png)
    assert pdf.stat().st_size > 1_000
    assert png.stat().st_size > 10_000
