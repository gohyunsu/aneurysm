"""Reference-only OSI support reporting for the ICCE validation cohort.

This module has no loader, prediction, locked-test, or extra-row path. A
private runtime supplies the already admitted 73 validation references and the
exact TAWSS floor recorded by a completed full-train ICCE result.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

import torch


PROTOCOL_ID = "aneug_release_730_icce_osi_support_audit_v1"


class ICCEOSISupportAuditError(RuntimeError):
    pass


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCEOSISupportAuditError(reason)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    config = dict(payload)
    _require(
        config.get("protocol_id") == PROTOCOL_ID
        and config.get("status") == "prospective_reference_only"
        and config.get("evaluation_partition") == "validation"
        and config.get("validation_case_count") == 73
        and config.get("nodes_per_case") == 13_902
        and config.get("phases_per_case") == 80
        and config.get("reference_tawss_floor_source")
        == "completed_full_train_icce_result_bound_to_train_584_only"
        and config.get("locked_test_fields_read") is False
        and config.get("processed_only_extra_fields_read") is False
        and config.get("case_identifiers_included") is False
        and _is_sha256(config.get("validation_case_digest")),
        "support_config",
    )
    return config


def reference_support_metrics(
    reference_wss: torch.Tensor,
    vertex_weights: torch.Tensor,
    reference_tawss_floor: float,
) -> dict[str, float | int]:
    """Return exact support counts/fractions for one reference cycle."""

    _require(
        reference_wss.ndim == 3
        and reference_wss.shape[0] == 80
        and reference_wss.shape[-1] == 3
        and vertex_weights.shape == (reference_wss.shape[1],),
        "support_shape",
    )
    _require(
        bool(torch.isfinite(reference_wss).all().item())
        and bool(torch.isfinite(vertex_weights).all().item())
        and bool((vertex_weights >= 0).all().item())
        and bool((vertex_weights.sum() > 0).item())
        and math.isfinite(float(reference_tawss_floor))
        and reference_tawss_floor > 0.0,
        "support_values",
    )
    reference = reference_wss.to(torch.float64)
    weights = vertex_weights.to(torch.float64)
    weights = weights / weights.sum()
    tawss = torch.linalg.vector_norm(reference, dim=-1).mean(dim=0)
    support = tawss > float(reference_tawss_floor)
    support_count = int(support.sum().item())
    node_count = int(support.numel())
    return {
        "reference_support_vertex_count": support_count,
        "reference_support_vertex_fraction": support_count / node_count,
        "reference_support_area_fraction": float(weights[support].sum().item()),
    }


def _summary(values: Sequence[float]) -> dict[str, float | int]:
    _require(
        bool(values) and all(math.isfinite(float(value)) for value in values),
        "summary_values",
    )
    parsed = sorted(float(value) for value in values)

    def quantile(probability: float) -> float:
        position = probability * (len(parsed) - 1)
        lower = int(math.floor(position))
        upper = int(math.ceil(position))
        if lower == upper:
            return parsed[lower]
        fraction = position - lower
        return parsed[lower] * (1.0 - fraction) + parsed[upper] * fraction

    mean = sum(parsed) / len(parsed)
    return {
        "case_count": len(parsed),
        "mean": mean,
        "minimum": parsed[0],
        "q25": quantile(0.25),
        "median": quantile(0.50),
        "q75": quantile(0.75),
        "maximum": parsed[-1],
    }


def audit_reference_support(
    validation_cases: Sequence[Mapping[str, torch.Tensor]],
    reference_tawss_floor: float,
    config: Mapping[str, Any],
    *,
    validation_case_digest: str,
) -> dict[str, Any]:
    """Audit support on the fixed validation order without model predictions."""

    protocol = validate_config(config)
    _require(
        len(validation_cases) == protocol["validation_case_count"]
        and validation_case_digest == protocol["validation_case_digest"],
        "validation_scope",
    )
    rows: list[dict[str, float | int]] = []
    for case in validation_cases:
        _require(set(case) >= {"wss", "vertex_weights"}, "validation_case")
        _require(
            int(case["wss"].shape[1]) == protocol["nodes_per_case"],
            "node_count",
        )
        rows.append(
            reference_support_metrics(
                case["wss"], case["vertex_weights"], reference_tawss_floor
            )
        )
    support_counts = [int(row["reference_support_vertex_count"]) for row in rows]
    node_count = int(protocol["nodes_per_case"])
    total_vertices = node_count * len(rows)
    return {
        "schema_version": "aurora.aneug_release_730_icce_osi_support_audit.v1",
        "protocol_id": PROTOCOL_ID,
        "status": "complete_validation_reference_only",
        "reference_tawss_floor": float(reference_tawss_floor),
        "reference_tawss_floor_source": protocol["reference_tawss_floor_source"],
        "validation_case_count": len(rows),
        "nodes_per_case": node_count,
        "evaluated_vertex_count": total_vertices,
        "reference_support_vertex_count": sum(support_counts),
        "reference_support_vertex_fraction": sum(support_counts) / total_vertices,
        "case_support_vertex_fraction": _summary(
            [float(row["reference_support_vertex_fraction"]) for row in rows]
        ),
        "case_support_area_fraction": _summary(
            [float(row["reference_support_area_fraction"]) for row in rows]
        ),
        "per_case_without_identifiers": rows,
        "case_identifiers_included": False,
        "prediction_or_model_used": False,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "paper_claim": False,
    }
