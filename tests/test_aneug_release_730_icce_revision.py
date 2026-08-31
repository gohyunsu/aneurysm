import json
from pathlib import Path

import pytest
import torch

from aurora.aneug_release_730_icce_revision import (
    ICCERevisionProtocolError,
    LABEL_COUNTS,
    METHOD_IDS,
    METHOD_REGIME_SEPARATED,
    METHOD_STEADY_THEN_TRANSIENT,
    METHOD_TRANSIENT_ONLY,
    TRAINING_SEEDS,
    decoder_gradient_cosine,
    deterministic_shuffled_target_map,
    expected_exposure_ledger,
    summarize_gradient_cosines,
    validate_exposure_result,
    validate_partition_boundary,
    validate_protocol_config,
)
from aurora.aneug_release_730_ghd_cross_regime_transfer import (
    shared_decoder_cross_regime_backward_with_decoder_diagnostic,
)
from aurora.aneug_release_730_icce_fixed_budget import _transient_epoch_order


ROOT = Path(__file__).resolve().parents[1]


def test_public_protocol_is_exact() -> None:
    payload = json.loads(
        (ROOT / "configs/aneug_release_730_icce_validation_revision_v2.json").read_text()
    )
    validate_protocol_config(payload)


def test_six_method_ledgers_have_equal_transient_budget() -> None:
    ledgers = [expected_exposure_ledger(method) for method in METHOD_IDS]
    assert {ledger.transient_exposures for ledger in ledgers} == {146_584}
    assert expected_exposure_ledger(METHOD_TRANSIENT_ONLY).auxiliary_exposures == 0
    assert expected_exposure_ledger(METHOD_REGIME_SEPARATED).auxiliary_exposures == 146_584
    transfer = expected_exposure_ledger(METHOD_STEADY_THEN_TRANSIENT)
    assert transfer.steady_pretraining_exposures == 146_584
    assert transfer.checkpoint_epoch == 251


def test_label_ledgers_cycle_to_common_reference_budget() -> None:
    for cases in LABEL_COUNTS.values():
        ledger = expected_exposure_ledger(
            METHOD_REGIME_SEPARATED, unique_transient_cases=cases
        )
        assert ledger.transient_exposures == 146_584
        assert ledger.unique_transient_cases == cases


def test_shuffled_target_mapping_is_a_derangement_and_seed_bound() -> None:
    indices = tuple(range(19))
    first = deterministic_shuffled_target_map(indices, training_seed=TRAINING_SEEDS[0])
    repeat = deterministic_shuffled_target_map(indices, training_seed=TRAINING_SEEDS[0])
    second = deterministic_shuffled_target_map(indices, training_seed=TRAINING_SEEDS[1])
    assert first == repeat
    assert first != second
    assert set(first) == set(indices)
    assert set(first.values()) == set(indices)
    assert all(source != target for source, target in first.items())


def test_decoder_gradient_diagnostic_is_decoder_only_and_non_mutating() -> None:
    encoder = torch.nn.Linear(2, 2, bias=False)
    decoder = torch.nn.Linear(2, 1, bias=False)
    x = torch.tensor([[1.0, -2.0]])
    transient = decoder(encoder(x)).square().sum()
    auxiliary = -decoder(encoder(-x)).sum()
    diagnostic = decoder_gradient_cosine(
        transient, auxiliary, tuple(decoder.parameters())
    )
    assert -1.0 <= diagnostic["decoder_gradient_cosine"] <= 1.0
    assert all(parameter.grad is None for parameter in encoder.parameters())
    assert all(parameter.grad is None for parameter in decoder.parameters())


def test_shared_update_uses_all_parameters_but_reports_decoder_subset() -> None:
    encoder = torch.nn.Linear(2, 2, bias=False)
    decoder = torch.nn.Linear(2, 1, bias=False)
    transient = decoder(encoder(torch.tensor([[1.0, 2.0]]))).square().sum()
    auxiliary = decoder(encoder(torch.tensor([[-2.0, 1.0]]))).square().sum()
    parameters = tuple(encoder.parameters()) + tuple(decoder.parameters())
    diagnostic = shared_decoder_cross_regime_backward_with_decoder_diagnostic(
        transient_loss=transient,
        auxiliary_loss=auxiliary,
        optimization_parameters=parameters,
        diagnostic_decoder_parameters=tuple(decoder.parameters()),
    )
    assert diagnostic["variant"].endswith("decoder_only_diagnostic_v2")
    assert -1.0 <= diagnostic["decoder_gradient_cosine"] <= 1.0
    assert all(parameter.grad is not None for parameter in parameters)


def test_gradient_summary_uses_strictly_negative_fraction() -> None:
    summary = summarize_gradient_cosines([-1.0, 0.0, 0.5, -0.5])
    assert summary == {
        "count": 4,
        "mean": -0.25,
        "median": -0.25,
        "fraction_below_zero": 0.5,
    }


def test_partition_guard_rejects_test_or_extra_reads() -> None:
    valid = {
        "train_case_count": 584,
        "validation_case_count": 73,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "train_digest": "a" * 64,
        "validation_digest": "b" * 64,
    }
    validate_partition_boundary(**valid)
    with pytest.raises(ICCERevisionProtocolError, match="locked_test_read"):
        validate_partition_boundary(
            **{**valid, "locked_test_field_case_count_read": 1}
        )


def test_result_ledger_rejects_early_selected_checkpoint() -> None:
    expected = expected_exposure_ledger(METHOD_TRANSIENT_ONLY)
    result = {
        **expected.as_dict(),
        "selected_epoch": 250,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
    }
    with pytest.raises(ICCERevisionProtocolError, match="result_checkpoint_rule"):
        validate_exposure_result(result, expected)


def test_fixed_budget_epoch_order_is_balanced_and_seed_bound() -> None:
    full = _transient_epoch_order(
        train_count=584, training_seed=TRAINING_SEEDS[0], epoch=3, exposures=584
    )
    assert len(full) == len(set(full)) == 584
    assert full != _transient_epoch_order(
        train_count=584, training_seed=TRAINING_SEEDS[1], epoch=3, exposures=584
    )
    reduced = _transient_epoch_order(
        train_count=58, training_seed=TRAINING_SEEDS[0], epoch=3, exposures=584
    )
    assert len(reduced) == 584
    counts = [reduced.count(index) for index in range(58)]
    assert max(counts) - min(counts) <= 1
