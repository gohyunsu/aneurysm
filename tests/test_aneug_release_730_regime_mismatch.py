import json
from pathlib import Path

import pytest
import torch

from aurora.aneug_release_730_regime_mismatch import (
    RegimeMismatchError,
    distribution_summary,
    mismatch_metrics,
    summarize_case_metrics,
)


ROOT = Path(__file__).resolve().parents[1]


def _cycle(field: torch.Tensor) -> torch.Tensor:
    return field.unsqueeze(0).repeat(80, 1, 1)


def test_identical_steady_and_constant_cycle() -> None:
    field = torch.tensor([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
    result = mismatch_metrics(field, _cycle(field), torch.tensor([0.25, 0.75]))
    assert result["steady_vs_cycle_mean_vector_relative_l2"] == pytest.approx(0.0)
    assert result["steady_vs_cycle_mean_global_cosine"] == pytest.approx(1.0)
    assert result["steady_vs_cycle_mean_magnitude_spatial_correlation"] == pytest.approx(1.0)
    assert result["steady_magnitude_vs_transient_tawss_normalized_absolute_difference"] == pytest.approx(0.0)
    assert result["steady_magnitude_vs_transient_tawss_signed_bias"] == pytest.approx(0.0)


def test_opposite_field_has_negative_cosine_and_relative_error_two() -> None:
    reference = torch.tensor([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
    result = mismatch_metrics(-reference, _cycle(reference), torch.tensor([0.5, 0.5]))
    assert result["steady_vs_cycle_mean_vector_relative_l2"] == pytest.approx(2.0)
    assert result["steady_vs_cycle_mean_global_cosine"] == pytest.approx(-1.0)
    assert result["steady_vs_cycle_mean_magnitude_spatial_correlation"] == pytest.approx(1.0)


def test_zero_spatial_variance_is_rejected() -> None:
    field = torch.ones(3, 3)
    with pytest.raises(RegimeMismatchError, match="magnitude_variance"):
        mismatch_metrics(field, _cycle(field), torch.ones(3))


def test_distribution_and_case_summary() -> None:
    summary = distribution_summary([1.0, 2.0, 3.0, 4.0])
    assert summary["mean"] == pytest.approx(2.5)
    assert summary["median"] == pytest.approx(2.5)
    combined = summarize_case_metrics([{"x": 1.0, "y": 3.0}, {"x": 2.0, "y": 5.0}])
    assert combined["x"]["count"] == 2
    assert combined["y"]["mean"] == pytest.approx(4.0)


def test_config_is_train_only() -> None:
    payload = json.loads(
        (ROOT / "configs/aneug_release_730_regime_mismatch_audit_v1.json").read_text()
    )
    assert payload["expected_matched_train_geometry_count"] == 317
    assert payload["read_scope"] == {
        "locked_test_fields": False,
        "processed_only_extra_fields": False,
        "transient_train_overlap_fields": True,
        "validation_fields": False,
    }
