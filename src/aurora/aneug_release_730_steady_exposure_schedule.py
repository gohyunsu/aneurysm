"""Deterministic matched exposure schedule for leakage-audited steady rows.

This module reads only the private geometry-index manifest.  It never indexes
steady or transient WSS.  The schedule is shared by the selected control and
proposal so different row order cannot masquerade as a method effect.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


class SteadyExposureScheduleError(RuntimeError):
    """Raised when scope or exposure provenance is inconsistent."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise SteadyExposureScheduleError(reason)


def file_sha256(path: str | Path, block_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(block_bytes):
            digest.update(block)
    return digest.hexdigest()


def ordered_digest(values: Sequence[str | int]) -> str:
    return hashlib.sha256(
        "\n".join(str(value) for value in values).encode("utf-8")
    ).hexdigest()


def canonical_case_digest(values: Sequence[str]) -> str:
    return ordered_digest(sorted(str(value) for value in values))


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_steady_exposure_schedule.v1",
        "schema_version",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_steady_exposure_schedule_v1",
        "protocol_id",
    )
    _require(
        config.get("status")
        == "prepared_metadata_only_schedule_not_training_activation",
        "status",
    )
    source = config["source"]
    _require(
        source["steady_scope_config_sha256"]
        == "782285c95a7eed7ead983b298426606bdb6d9258d076908c9c65a0ad3d8aa5cf"
        and source["private_overlap_result_sha256"]
        == "52219b9a7161f0932a4ed80020a339510474431b67e168741426c2a12e5092ef",
        "source",
    )
    scope = config["scope"]
    _require(scope["eligible_steady_rows"] == 13_985, "eligible_rows")
    _require(
        scope["eligible_case_digest"]
        == "6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc"
        and scope["ordered_case_digest"]
        == "403ae3afedcbf755a1ff97e096090930b016fb8ebcfdaf5b2e7540bc6828feb7"
        and scope["ordered_index_digest"]
        == "292946acf8857942a68df1626ca58cf46f5260b0d64b277439b42a92d5bd4629",
        "scope_digests",
    )
    schedule = config["schedule"]
    _require(
        (
            schedule["algorithm"],
            schedule["seed"],
            schedule["steady_examples_per_transient_epoch"],
            schedule["minimum_epochs"],
            schedule["maximum_epochs"],
        )
        == (
            "sha256_ranked_full_cycle_without_replacement_v1",
            20_260_821,
            584,
            80,
            251,
        ),
        "schedule",
    )
    _require(
        schedule["one_steady_example_per_transient_case"] is True
        and schedule["repeat_only_after_full_eligible_cycle"] is True,
        "exposure_rule",
    )
    expected = (
        (
            "minimum_epoch_summary",
            46_720,
            3,
            4,
            "a8370b5b0824b570dab172a619e424dc3ebad79d26c297404ab7e0791f37d2d3",
        ),
        (
            "maximum_epoch_summary",
            146_584,
            10,
            11,
            "9166a9331d8715e0cfe9134989d9a8947078f334be4bb739971f49d04bb7dbf0",
        ),
    )
    for key, examples, minimum, maximum, digest in expected:
        summary = schedule[key]
        _require(
            (
                summary["examples"],
                summary["unique_rows"],
                summary["minimum_visits"],
                summary["maximum_visits"],
                summary["prefix_sha256"],
            )
            == (examples, 13_985, minimum, maximum, digest),
            key,
        )
    fairness = config["fairness"]
    _require(
        fairness["model_roles"]
        == ["selected_strongest_control", "selected_proposal"]
        and fairness["same_scope_and_schedule_rule_for_both_roles"] is True
        and fairness["proposal_only_steady_exposure"] is False
        and fairness["actual_epochs_and_prefix_digest_must_be_reported"] is True
        and fairness["steady_supervision_is_novelty"] is False,
        "fairness",
    )
    training = config["training_boundary"]
    _require(
        training["shared_geometry_encoder_required"] is True
        and training["separate_single_field_steady_head_required"] is True
        and training["replicate_steady_field_across_80_phases"] is False
        and training["steady_time_or_waveform_token"] is False,
        "steady_representation",
    )
    for key in (
        "architecture_selected_here",
        "loss_weight_selected_here",
        "optimizer_selected_here",
        "gpu_training_authorized",
    ):
        _require(training[key] is False, f"training_{key}")
    boundary = config["read_boundary"]
    for key in (
        "steady_wss_values_read",
        "transient_wss_values_read",
        "locked_test_or_extra_wss_read",
        "case_ids_in_public_output",
    ):
        _require(boundary[key] is False, f"boundary_{key}")
    _require(
        boundary["server"] == "introai9"
        and boundary["excluded_server"] == "junjinyong",
        "server",
    )


def _cycle_order(indices: Sequence[int], seed: int, cycle: int) -> list[int]:
    _require(cycle >= 0, "cycle")
    return sorted(
        (int(index) for index in indices),
        key=lambda index: (
            hashlib.sha256(f"{seed}:{cycle}:{index}".encode("utf-8")).digest(),
            index,
        ),
    )


def exposure_prefix(
    indices: Sequence[int], *, epochs: int, cases_per_epoch: int, seed: int
) -> tuple[int, ...]:
    """Return an exhaustive no-replacement-cycle prefix for ``epochs``."""

    normalized = tuple(int(value) for value in indices)
    _require(len(normalized) > 0 and len(set(normalized)) == len(normalized), "indices")
    _require(epochs > 0 and cases_per_epoch > 0, "horizon")
    required = epochs * cases_per_epoch
    output: list[int] = []
    cycle = 0
    while len(output) < required:
        output.extend(_cycle_order(normalized, seed, cycle))
        cycle += 1
    return tuple(output[:required])


def summarize_prefix(values: Sequence[int]) -> dict[str, Any]:
    _require(len(values) > 0, "empty_prefix")
    counts = Counter(int(value) for value in values)
    return {
        "examples": len(values),
        "unique_rows": len(counts),
        "minimum_visits": min(counts.values()),
        "maximum_visits": max(counts.values()),
        "prefix_sha256": ordered_digest(values),
    }


def build_schedule_manifest(
    config: Mapping[str, Any], private_overlap: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate the private index/name alignment and emit digest-only evidence."""

    validate_config(config)
    _require(
        private_overlap.get("schema_version")
        == "aurora.private.aneug_release_730_steady_overlap_audit.v1",
        "private_schema",
    )
    _require(private_overlap.get("any_wss_value_read") is False, "wss_read")
    _require(private_overlap.get("test_wss_opened") is False, "test_opened")
    steady_names = [str(value) for value in private_overlap["steady_case_names"]]
    indices = [int(value) for value in private_overlap["eligible_steady_indices"]]
    names = [str(value) for value in private_overlap["eligible_steady_case_names"]]
    scope = config["scope"]
    _require(
        len(indices) == len(names) == scope["eligible_steady_rows"]
        and len(set(indices)) == len(indices)
        and indices == sorted(indices),
        "private_indices",
    )
    _require(
        names == [steady_names[index] for index in indices],
        "private_index_name_alignment",
    )
    _require(canonical_case_digest(names) == scope["eligible_case_digest"], "case_digest")
    _require(ordered_digest(names) == scope["ordered_case_digest"], "case_order")
    _require(ordered_digest(indices) == scope["ordered_index_digest"], "index_order")
    schedule = config["schedule"]
    summaries: dict[str, dict[str, Any]] = {}
    for label, epochs in (
        ("minimum_epoch_summary", int(schedule["minimum_epochs"])),
        ("maximum_epoch_summary", int(schedule["maximum_epochs"])),
    ):
        prefix = exposure_prefix(
            indices,
            epochs=epochs,
            cases_per_epoch=int(schedule["steady_examples_per_transient_epoch"]),
            seed=int(schedule["seed"]),
        )
        summary = summarize_prefix(prefix)
        _require(summary == schedule[label], f"{label}_mismatch")
        summaries[label] = summary
    return {
        "schema_version": "aurora.private.aneug_release_730_steady_exposure_schedule.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete",
        "algorithm": schedule["algorithm"],
        "seed": schedule["seed"],
        "eligible_steady_rows": scope["eligible_steady_rows"],
        "eligible_case_digest": scope["eligible_case_digest"],
        "ordered_case_digest": scope["ordered_case_digest"],
        "ordered_index_digest": scope["ordered_index_digest"],
        "summaries": summaries,
        "same_schedule_rule_for_control_and_proposal": True,
        "steady_wss_values_read": False,
        "transient_wss_values_read": False,
        "locked_test_or_extra_wss_read": False,
        "case_ids_included": False,
        "gpu_training_authorized": False,
        "paper_performance_claim": False,
    }


def _strict_atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "result_exists")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--private-overlap", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    _require(args.private_overlap is not None and args.output is not None, "arguments")
    _require(
        file_sha256(args.private_overlap)
        == config["source"]["private_overlap_result_sha256"],
        "private_overlap_sha256",
    )
    private_overlap = json.loads(args.private_overlap.read_text(encoding="utf-8"))
    _strict_atomic_json(args.output, build_schedule_manifest(config, private_overlap))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
