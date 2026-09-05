import json
from pathlib import Path

import pytest
import torch

from aurora.aneug_release_730_icce_osi_support_audit import (
    ICCEOSISupportAuditError,
    audit_reference_support,
    reference_support_metrics,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]


def _config() -> dict:
    return json.loads(
        (ROOT / "configs/aneug_release_730_icce_osi_support_audit_v1.json").read_text()
    )


def test_reference_support_metrics_report_vertex_and_area_fractions() -> None:
    reference = torch.zeros(80, 4, 3)
    reference[:, :, 0] = torch.tensor([0.0, 2.0, 3.0, 0.5])
    weights = torch.tensor([0.1, 0.2, 0.3, 0.4])
    result = reference_support_metrics(reference, weights, 1.0)
    assert result["reference_support_vertex_count"] == 2
    assert result["reference_support_vertex_fraction"] == pytest.approx(0.5)
    assert result["reference_support_area_fraction"] == pytest.approx(0.5)


def test_config_rejects_locked_test_scope() -> None:
    config = _config()
    validate_config(config)
    config["evaluation_partition"] = "locked_test"
    with pytest.raises(ICCEOSISupportAuditError, match="support_config"):
        validate_config(config)


def test_full_audit_rejects_incomplete_validation_scope() -> None:
    config = _config()
    reference = torch.zeros(80, 4, 3)
    weights = torch.ones(4)
    case = {"wss": reference, "vertex_weights": weights}
    with pytest.raises(ICCEOSISupportAuditError, match="validation_scope"):
        audit_reference_support(
            [case],
            1.0,
            config,
            validation_case_digest=config["validation_case_digest"],
        )
