"""Prospective ICCE validation-only supervision-attribution contract.

This module does not open data or train a model.  It centralizes the method
identities, fixed exposure accounting, partition guards, deterministic shuffled
steady-label control, and decoder-only gradient diagnostic used by the revision
runners.  Historical v1 training and locked-test evidence remain immutable.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import torch
from torch import nn


PROTOCOL_ID = "aneug_release_730_icce_validation_revision_v2"
SCHEMA_VERSION = "aurora.aneug_release_730_icce_validation_revision.v2"

METHOD_TRANSIENT_ONLY = "T"
METHOD_TRANSIENT_MEAN = "T_plus_M"
METHOD_REGIME_SEPARATED = "T_plus_S_regime_separated"
METHOD_SHARED_DECODER = "T_plus_S_shared_decoder"
METHOD_STEADY_THEN_TRANSIENT = "S_then_T"
METHOD_SHUFFLED_STEADY = "T_plus_S_shuffled_labels"
METHOD_IDS = (
    METHOD_TRANSIENT_ONLY,
    METHOD_TRANSIENT_MEAN,
    METHOD_REGIME_SEPARATED,
    METHOD_SHARED_DECODER,
    METHOD_STEADY_THEN_TRANSIENT,
    METHOD_SHUFFLED_STEADY,
)

TRAINING_SEEDS = (20_260_901, 20_260_902, 20_260_903, 20_260_904, 20_260_905)
LAMBDA_SEEDS = TRAINING_SEEDS[:3]
LAMBDA_VALUES = (0.25, 0.5, 1.0, 2.0, 4.0)
LABEL_PERCENTS = (10, 25, 50, 100)
LABEL_COUNTS = {10: 58, 25: 146, 50: 292, 100: 584}


class ICCERevisionProtocolError(RuntimeError):
    """Raised when a revision experiment leaves its registered boundary."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCERevisionProtocolError(reason)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical_digest(payload: Mapping[str, Any]) -> str:
    """Return a stable digest for identifier-free protocol metadata."""

    return hashlib.sha256(
        json.dumps(
            dict(payload), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ExposureLedger:
    """Exact optimization-example counts for one completed scientific cell."""

    method_id: str
    unique_transient_cases: int
    reference_epochs: int
    transient_exposures: int
    auxiliary_exposures: int
    auxiliary_source: str | None
    steady_pretraining_exposures: int
    checkpoint_epoch: int
    checkpoint_rule: str = "fixed_final_epoch_no_validation_selection"

    def as_dict(self) -> dict[str, Any]:
        return {
            "method_id": self.method_id,
            "unique_transient_cases": self.unique_transient_cases,
            "reference_epochs": self.reference_epochs,
            "transient_exposures": self.transient_exposures,
            "auxiliary_exposures": self.auxiliary_exposures,
            "auxiliary_source": self.auxiliary_source,
            "steady_pretraining_exposures": self.steady_pretraining_exposures,
            "checkpoint_epoch": self.checkpoint_epoch,
            "checkpoint_rule": self.checkpoint_rule,
        }


def expected_exposure_ledger(
    method_id: str,
    *,
    unique_transient_cases: int = 584,
    reference_epochs: int = 251,
    transient_exposures_per_epoch: int = 584,
) -> ExposureLedger:
    """Construct the registered ledger without inferring it from a run result."""

    _require(method_id in METHOD_IDS, "method_id")
    _require(unique_transient_cases in set(LABEL_COUNTS.values()), "case_count")
    _require(reference_epochs > 0, "reference_epochs")
    _require(transient_exposures_per_epoch == 584, "reference_epoch_exposures")
    transient = reference_epochs * transient_exposures_per_epoch
    sources: dict[str, str | None] = {
        METHOD_TRANSIENT_ONLY: None,
        METHOD_TRANSIENT_MEAN: "transient_cycle_mean",
        METHOD_REGIME_SEPARATED: "eligible_steady_wss",
        METHOD_SHARED_DECODER: "eligible_steady_wss",
        METHOD_STEADY_THEN_TRANSIENT: "eligible_steady_wss_pretraining",
        METHOD_SHUFFLED_STEADY: "eligible_steady_wss_permuted_targets",
    }
    auxiliary = 0 if method_id == METHOD_TRANSIENT_ONLY else transient
    pretraining = transient if method_id == METHOD_STEADY_THEN_TRANSIENT else 0
    return ExposureLedger(
        method_id=method_id,
        unique_transient_cases=unique_transient_cases,
        reference_epochs=reference_epochs,
        transient_exposures=transient,
        auxiliary_exposures=auxiliary,
        auxiliary_source=sources[method_id],
        steady_pretraining_exposures=pretraining,
        checkpoint_epoch=reference_epochs,
    )


def validate_partition_boundary(
    *,
    train_case_count: int,
    validation_case_count: int,
    locked_test_field_case_count_read: int,
    processed_only_extra_field_case_count_read: int,
    train_digest: str,
    validation_digest: str,
) -> None:
    """Fail before result creation if a validation-only cell crossed partitions."""

    _require(train_case_count in set(LABEL_COUNTS.values()), "train_case_count")
    _require(validation_case_count == 73, "validation_case_count")
    _require(locked_test_field_case_count_read == 0, "locked_test_read")
    _require(processed_only_extra_field_case_count_read == 0, "extra_read")
    _require(_is_sha256(train_digest), "train_digest")
    _require(_is_sha256(validation_digest), "validation_digest")


def validate_exposure_result(
    result: Mapping[str, Any], expected: ExposureLedger
) -> None:
    """Check exact counts and the prespecified non-selective checkpoint rule."""

    _require(result.get("method_id") == expected.method_id, "result_method")
    _require(
        result.get("unique_transient_cases") == expected.unique_transient_cases,
        "result_unique_cases",
    )
    _require(
        result.get("transient_exposures") == expected.transient_exposures,
        "result_transient_exposures",
    )
    _require(
        result.get("auxiliary_exposures") == expected.auxiliary_exposures,
        "result_auxiliary_exposures",
    )
    _require(
        result.get("steady_pretraining_exposures")
        == expected.steady_pretraining_exposures,
        "result_pretraining_exposures",
    )
    _require(
        result.get("selected_epoch") == expected.checkpoint_epoch
        and result.get("checkpoint_rule") == expected.checkpoint_rule,
        "result_checkpoint_rule",
    )
    _require(result.get("locked_test_field_case_count_read") == 0, "result_test_read")
    _require(
        result.get("processed_only_extra_field_case_count_read") == 0,
        "result_extra_read",
    )


def deterministic_shuffled_target_map(
    eligible_indices: Sequence[int], *, training_seed: int
) -> dict[int, int]:
    """Create a deterministic bijection with no source/target fixed points.

    Indices are hash-ranked and mapped to the next member of the resulting cycle.
    This destroys geometry-label pairing without changing target marginal counts.
    """

    indices = tuple(int(value) for value in eligible_indices)
    _require(training_seed in TRAINING_SEEDS, "shuffle_seed")
    _require(len(indices) > 1 and len(indices) == len(set(indices)), "eligible_indices")
    ranked = tuple(
        sorted(
            indices,
            key=lambda value: hashlib.sha256(
                f"{training_seed}:{value}".encode("ascii")
            ).digest(),
        )
    )
    mapping = {
        source: ranked[(position + 1) % len(ranked)]
        for position, source in enumerate(ranked)
    }
    _require(set(mapping) == set(indices), "shuffle_domain")
    _require(set(mapping.values()) == set(indices), "shuffle_codomain")
    _require(all(source != target for source, target in mapping.items()), "shuffle_fixed_point")
    return mapping


def shuffled_target_map_digest(mapping: Mapping[int, int]) -> str:
    """Hash a permutation without publishing dataset identifiers."""

    pairs = [[int(source), int(mapping[source])] for source in sorted(mapping)]
    return canonical_digest({"ordered_index_pairs": pairs})


def _flatten_gradients(
    gradients: Sequence[torch.Tensor | None], parameters: Sequence[nn.Parameter]
) -> torch.Tensor:
    _require(len(gradients) == len(parameters) and bool(parameters), "gradient_shape")
    pieces: list[torch.Tensor] = []
    for gradient, parameter in zip(gradients, parameters, strict=True):
        _require(gradient is not None, "missing_gradient")
        _require(gradient.shape == parameter.shape, "gradient_parameter_shape")
        _require(bool(torch.isfinite(gradient).all().item()), "nonfinite_gradient")
        pieces.append(gradient.reshape(-1))
    return torch.cat(pieces)


def decoder_gradient_cosine(
    transient_loss: torch.Tensor,
    auxiliary_loss: torch.Tensor,
    decoder_parameters: Sequence[nn.Parameter],
    *,
    auxiliary_coefficient: float = 1.0,
    epsilon: float = 1e-12,
) -> dict[str, float]:
    """Measure pre-summation task gradients on cycle-decoder parameters only.

    This function is diagnostic-only: it does not write ``parameter.grad``.  A
    runner must subsequently backpropagate its registered optimization objective.
    The two losses must originate from separate forward graphs or be retained by
    the caller.
    """

    parameters = tuple(decoder_parameters)
    _require(bool(parameters), "decoder_parameters")
    _require(
        transient_loss.ndim == auxiliary_loss.ndim == 0
        and bool(torch.isfinite(transient_loss).item())
        and bool(torch.isfinite(auxiliary_loss).item()),
        "diagnostic_loss",
    )
    _require(
        math.isfinite(auxiliary_coefficient) and auxiliary_coefficient > 0.0,
        "auxiliary_coefficient",
    )
    transient_gradients = torch.autograd.grad(
        transient_loss, parameters, retain_graph=True, allow_unused=False
    )
    auxiliary_gradients = torch.autograd.grad(
        auxiliary_loss, parameters, retain_graph=True, allow_unused=False
    )
    transient = _flatten_gradients(transient_gradients, parameters)
    auxiliary = _flatten_gradients(auxiliary_gradients, parameters) * float(
        auxiliary_coefficient
    )
    transient_norm = torch.linalg.vector_norm(transient)
    auxiliary_norm = torch.linalg.vector_norm(auxiliary)
    _require(
        bool(torch.isfinite(transient_norm).item())
        and bool(torch.isfinite(auxiliary_norm).item())
        and float(transient_norm.item()) > epsilon
        and float(auxiliary_norm.item()) > epsilon,
        "diagnostic_gradient_norm",
    )
    cosine = torch.dot(transient, auxiliary) / torch.clamp(
        transient_norm * auxiliary_norm, min=epsilon
    )
    cosine = torch.clamp(cosine, min=-1.0, max=1.0)
    return {
        "decoder_gradient_cosine": float(cosine.item()),
        "transient_decoder_gradient_norm": float(transient_norm.item()),
        "weighted_auxiliary_decoder_gradient_norm": float(auxiliary_norm.item()),
    }


def summarize_gradient_cosines(values: Sequence[float]) -> dict[str, float | int]:
    """Return the prespecified mean, median, and fraction below zero."""

    ordered = sorted(float(value) for value in values)
    _require(bool(ordered) and all(math.isfinite(value) for value in ordered), "cosines")
    middle = len(ordered) // 2
    median = (
        ordered[middle]
        if len(ordered) % 2 == 1
        else 0.5 * (ordered[middle - 1] + ordered[middle])
    )
    return {
        "count": len(ordered),
        "mean": sum(ordered) / len(ordered),
        "median": median,
        "fraction_below_zero": sum(value < 0.0 for value in ordered) / len(ordered),
    }


def validate_protocol_config(config: Mapping[str, Any]) -> None:
    """Validate the public, identifier-free prospective protocol."""

    _require(config.get("schema_version") == SCHEMA_VERSION, "schema_version")
    _require(config.get("protocol_id") == PROTOCOL_ID, "protocol_id")
    _require(config.get("status") == "prospectively_registered_validation_only", "status")
    _require(tuple(config.get("methods", ())) == METHOD_IDS, "methods")
    _require(tuple(config.get("training_seeds", ())) == TRAINING_SEEDS, "seeds")
    _require(config.get("reference_epochs") == 251, "reference_epochs")
    _require(config.get("transient_exposures_per_reference_epoch") == 584, "epoch_exposures")
    _require(config.get("selected_checkpoint_rule") == "fixed_final_epoch_no_validation_selection", "checkpoint_rule")
    access = config.get("access", {})
    _require(
        access.get("train_cases") == 584
        and access.get("validation_cases") == 73
        and access.get("locked_test_cases") == 73
        and access.get("processed_only_extra_cases") == 79
        and access.get("read_locked_test_fields") is False
        and access.get("read_processed_only_extra_fields") is False
        and access.get("locked_test_state")
        == "historically_opened_once_preserve_no_new_access",
        "access",
    )
    sensitivity = config.get("lambda_sensitivity", {})
    _require(
        tuple(sensitivity.get("values", ())) == LAMBDA_VALUES
        and tuple(sensitivity.get("seeds", ())) == LAMBDA_SEEDS
        and sensitivity.get("main_value") == 1.0
        and sensitivity.get("validation_only") is True,
        "lambda_sensitivity",
    )
    labels = config.get("label_efficiency", {})
    _require(
        tuple(labels.get("percents", ())) == LABEL_PERCENTS
        and labels.get("unique_case_counts")
        == {str(key): value for key, value in LABEL_COUNTS.items()}
        and tuple(labels.get("training_seeds", ())) == TRAINING_SEEDS
        and labels.get("nested") is True,
        "label_efficiency",
    )
