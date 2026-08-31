import json
from pathlib import Path

from aurora.aneug_release_730_icce_analysis import (
    ALL_METRICS,
    analyze_label_efficiency,
    analyze_lambda_sensitivity,
    analyze_main_attribution,
    crossed_seed_case_bootstrap,
)
from aurora.aneug_release_730_icce_revision import (
    LABEL_COUNTS,
    METHOD_IDS,
    METHOD_REGIME_SEPARATED,
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
    method_id: str,
    training_seed: int,
    *,
    train_count: int = 584,
    offset: float = 0.0,
) -> dict:
    ledger = expected_exposure_ledger(method_id, unique_transient_cases=train_count)
    seed_index = TRAINING_SEEDS.index(training_seed)
    rows = []
    for case_index in range(73):
        base = 0.2 + offset + seed_index * 0.001 + case_index * 0.0001
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
        metric: sum(row[metric] for row in rows) / len(rows) for metric in ALL_METRICS
    }
    return {
        "schema_version": "aurora.private.aneug_release_730_icce_fixed_budget_result.v2",
        "status": "complete_validation_only",
        **ledger.as_dict(),
        "selected_epoch": 251,
        "training_seed": training_seed,
        "label_percent": next(
            percent for percent, count in LABEL_COUNTS.items() if count == train_count
        ),
        "train_case_count": train_count,
        "validation_case_count": 73,
        "validation_case_digest": "a" * 64,
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
            if method_id == "T_plus_S_shared_decoder"
            else None
        ),
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "case_ids_included": False,
    }


def test_crossed_bootstrap_is_deterministic_and_case_level() -> None:
    values = [[seed_index + case_index / 100.0 for case_index in range(73)] for seed_index in range(5)]
    first = crossed_seed_case_bootstrap(values, replicates=10_000, seed=17)
    second = crossed_seed_case_bootstrap(values, replicates=10_000, seed=17)
    assert first == second
    assert first["training_seed_count"] == 5
    assert first["paired_case_count"] == 73


def test_main_attribution_reports_proposed_minus_each_control() -> None:
    offsets = {
        "T": 0.10,
        "T_plus_M": 0.08,
        "T_plus_S_regime_separated": 0.02,
        "T_plus_S_shared_decoder": 0.07,
        "S_then_T": 0.09,
        "T_plus_S_shuffled_labels": 0.095,
    }
    cells = {
        method: {
            seed: _result(method, seed, offset=offsets[method])
            for seed in TRAINING_SEEDS
        }
        for method in METHOD_IDS
    }
    analysis = analyze_main_attribution(cells, _protocol())
    assert len(analysis["proposed_minus_comparator"]) == 5
    primary = analysis["proposed_minus_comparator"][
        "T_plus_S_regime_separated_minus_T"
    ]["field_relative_l2"]
    assert primary["point"] < 0.0
    assert primary["ci95_high"] < 0.0
    assert analysis["locked_test_or_extra_read"] is False


def test_label_and_lambda_analyses_use_registered_common_seeds() -> None:
    label_cells = {}
    for percent, count in LABEL_COUNTS.items():
        label_cells[percent] = {
            METHOD_TRANSIENT_ONLY: {
                seed: _result(METHOD_TRANSIENT_ONLY, seed, train_count=count, offset=0.1)
                for seed in TRAINING_SEEDS
            },
            METHOD_REGIME_SEPARATED: {
                seed: _result(METHOD_REGIME_SEPARATED, seed, train_count=count, offset=0.05)
                for seed in TRAINING_SEEDS
            },
        }
    label = analyze_label_efficiency(label_cells, _protocol())
    assert label["common_training_seeds"] == list(TRAINING_SEEDS)
    assert set(label["curves"]) == {"10", "25", "50", "100"}
    assert label["curves"]["10"]["proposed_minus_T"]["field_relative_l2"]["point"] < 0

    lambda_cells = {
        value: {
            seed: _result(
                METHOD_REGIME_SEPARATED,
                seed,
                offset=abs(value - 1.0) * 0.01,
            )
            for seed in TRAINING_SEEDS[:3]
        }
        for value in (0.25, 0.5, 1.0, 2.0, 4.0)
    }
    sensitivity = analyze_lambda_sensitivity(lambda_cells, _protocol())
    assert sensitivity["main_lambda"] == 1.0
    assert sensitivity["main_lambda_selected_from_sensitivity"] is False
