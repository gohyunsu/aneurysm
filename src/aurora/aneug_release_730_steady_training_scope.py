"""Resolve the one leakage-audited steady scope shared by control and proposal.

This module validates metadata and the append-only overlap result. It returns
eligible row indices without indexing the steady tensor, selecting a model, or
fixing a training schedule.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class SteadyTrainingScopeError(RuntimeError):
    """Raised when matched steady-information provenance is inconsistent."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise SteadyTrainingScopeError(reason)


def file_sha256(path: str | Path, block_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(block_bytes):
            digest.update(block)
    return digest.hexdigest()


def canonical_case_digest(values: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(sorted(values)).encode("utf-8")).hexdigest()


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(payload)
    return payload


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_steady_training_scope.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id") == "aneug_release_730_steady_training_scope_v1",
        "protocol_id",
    )
    _require(
        config.get("status") == "reusable_scope_validator_not_a_training_run",
        "status",
    )
    source = config["source"]
    _require(
        source["steady_bytes"] == 9_632_510_050
        and source["steady_sha256"]
        == "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f"
        and source["public_overlap_result_sha256"]
        == "b3a118bae156a1dbc6c838b923a594f9b0f452a40f34b8bccb6bc396d28ba397"
        and source["private_overlap_result_sha256"]
        == "52219b9a7161f0932a4ed80020a339510474431b67e168741426c2a12e5092ef",
        "source",
    )
    scope = config["scope"]
    _require(
        (
            scope["processed_steady_rows"],
            scope["eligible_steady_rows"],
            scope["excluded_overlap_rows"],
            scope["nodes"],
            scope["channels"],
            scope["ghd_width"],
        )
        == (14_392, 13_985, 407, 13_902, 9, 432),
        "scope_counts",
    )
    _require(
        scope["eligible_case_digest"]
        == "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc",
        "eligible_digest",
    )
    control = config["information_control"]
    _require(
        control["model_roles"] == ["strongest_comparator", "selected_proposal"]
        and control["modes"] == ["transient_only", "eligible_steady"],
        "factorial_roles",
    )
    _require(control["same_eligible_indices_for_both_roles"] is True, "same_scope")
    _require(control["proposal_only_steady_labels"] is False, "proposal_privilege")
    _require(control["steady_supervision_is_novelty"] is False, "novelty")
    _require(
        control["training_schedule_fixed_here"] is False
        and control["architecture_fixed_here"] is False,
        "development_flexibility",
    )
    boundary = config["read_boundary"]
    _require(boundary["scope_validation_indexes_wss"] is False, "wss_scope")
    _require(boundary["locked_test_or_extra_wss_read"] is False, "sealed_scope")
    _require(boundary["case_ids_in_public_output"] is False, "public_ids")


def validate_scope_payloads(
    config: Mapping[str, Any],
    public_result: Mapping[str, Any],
    private_result: Mapping[str, Any],
    archive: Mapping[str, Any],
) -> tuple[int, ...]:
    """Return eligible indices after metadata-only cross-validation.

    Callers loading production files use :func:`load_scope_files`, which first
    validates the immutable config. Keeping payload validation separate permits
    small synthetic regression fixtures without weakening the production path.
    """
    scope = config["scope"]
    _require(public_result.get("status") == "complete", "public_status")
    _require(public_result.get("case_ids_public") is False, "public_case_ids")
    _require(
        public_result.get("steady_case_count") == scope["processed_steady_rows"]
        and public_result.get("eligible_steady_case_count")
        == scope["eligible_steady_rows"]
        and public_result.get("excluded_steady_case_count")
        == scope["excluded_overlap_rows"]
        and public_result.get("eligible_steady_case_digest")
        == scope["eligible_case_digest"],
        "public_scope",
    )
    for key in (
        "steady_wss_values_read",
        "transient_wss_values_read",
        "locked_test_wss_values_read",
        "processed_only_extra_wss_values_read",
    ):
        _require(public_result.get(key) is False, f"public_{key}")

    _require(
        private_result.get("schema_version")
        == "aurora.private.aneug_release_730_steady_overlap_audit.v1",
        "private_schema",
    )
    _require(private_result.get("any_wss_value_read") is False, "private_wss_read")
    _require(private_result.get("test_wss_opened") is False, "private_test_open")
    steady_names = [str(value) for value in private_result["steady_case_names"]]
    indices = [int(value) for value in private_result["eligible_steady_indices"]]
    eligible_names = [str(value) for value in private_result["eligible_steady_case_names"]]
    _require(
        len(steady_names) == len(set(steady_names)) == scope["processed_steady_rows"],
        "steady_names",
    )
    _require(
        len(indices) == len(set(indices)) == scope["eligible_steady_rows"]
        and indices == sorted(indices)
        and indices[0] >= 0
        and indices[-1] < len(steady_names),
        "eligible_indices",
    )
    _require(
        eligible_names == [steady_names[index] for index in indices],
        "eligible_index_name_alignment",
    )
    _require(
        canonical_case_digest(eligible_names) == scope["eligible_case_digest"],
        "eligible_name_digest",
    )

    archive_names = [str(value) for value in archive["case_name"]]
    _require(archive_names == steady_names, "archive_case_order")
    tensor = archive["tensor"]
    _require(
        tuple(int(value) for value in tensor.shape)
        == (scope["processed_steady_rows"], scope["nodes"], scope["channels"]),
        "archive_tensor_shape",
    )
    ghd = archive["ghd_dict"]["ghd"]
    _require(
        tuple(int(value) for value in ghd.shape)
        == (scope["processed_steady_rows"], scope["ghd_width"]),
        "archive_ghd_shape",
    )
    _require(
        [str(value) for value in archive["label"]]
        == [
            "x",
            "y",
            "z",
            "x_normal",
            "y_normal",
            "z_normal",
            "wss_x",
            "wss_y",
            "wss_z",
        ],
        "archive_labels",
    )
    return tuple(indices)


def load_scope_files(
    config: Mapping[str, Any],
    public_result_path: str | Path,
    private_result_path: str | Path,
    archive: Mapping[str, Any],
) -> tuple[int, ...]:
    """Hash-bind result files and resolve indices without tensor indexing."""

    validate_config(config)
    public_path = Path(public_result_path)
    private_path = Path(private_result_path)
    _require(
        file_sha256(public_path) == config["source"]["public_overlap_result_sha256"],
        "public_result_sha256",
    )
    _require(
        file_sha256(private_path) == config["source"]["private_overlap_result_sha256"],
        "private_result_sha256",
    )
    return validate_scope_payloads(
        config,
        json.loads(public_path.read_text(encoding="utf-8")),
        json.loads(private_path.read_text(encoding="utf-8")),
        archive,
    )
