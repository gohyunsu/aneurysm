"""Freeze the release-730 proposal objective from validation-only evidence.

The three functional fine-tunes share one combined checkpoint and therefore
one set of initial validation endpoint normalizers.  This analyzer recomputes
one common four-endpoint utility for every objective variant, instead of
comparing the variants' different training/checkpoint objectives.  It reports
all five candidate cells, selects no architecture from the locked test, and
fails closed if the direct selector names a control unsupported by the frozen
matched-training implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


class Release730CandidateSelectionError(RuntimeError):
    """Raised when candidate-selection evidence violates the frozen contract."""


CELL_ORDER = (
    "architecture_response_only_field",
    "architecture_response_plus_residual_field",
    "finetune_response_plus_residual_field",
    "finetune_response_plus_residual_scalarized",
    "finetune_response_plus_residual_anchored",
)
CELL_IDENTITY = {
    "architecture_response_only_field": ("architecture", "response_only", "field_only"),
    "architecture_response_plus_residual_field": (
        "architecture",
        "response_plus_residual",
        "field_only",
    ),
    "finetune_response_plus_residual_field": (
        "functional_finetune",
        "response_plus_residual",
        "field_only",
    ),
    "finetune_response_plus_residual_scalarized": (
        "functional_finetune",
        "response_plus_residual",
        "all_scalarized",
    ),
    "finetune_response_plus_residual_anchored": (
        "functional_finetune",
        "response_plus_residual",
        "all_field_anchored",
    ),
}
SELECTION_CELLS = CELL_ORDER[2:]
OBJECTIVE_ORDER = ("field_only", "all_scalarized", "all_field_anchored")
RANKS = (16, 32, 64, 128, 256)
CONTROL_MAP = {
    "ghd_gps_unet": "release730_ghd_gps",
    "transolver": "release730_transolver",
}
NORMALIZER_TO_METRIC = {
    "field": "field_relative_l2",
    "mean_vector": "mean_vector_tawss_normalized_l2",
    "tawss": "tawss_normalized_absolute_error",
    "osi": "osi_mae",
}


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise Release730CandidateSelectionError(reason)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def file_sha256(path: str | Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(chunk_bytes):
            digest.update(block)
    return digest.hexdigest()


def _safe_relative(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def validate_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_candidate_selection.v1"
        and config.get("protocol_id") == "aneug_release_730_candidate_selection_v1"
        and config.get("status") == "prepared_result_pending",
        "config_identity",
    )
    source = config.get("source")
    _require(
        isinstance(source, Mapping)
        and source.get("candidate_config_sha256")
        == "38f256d4e60e2a7c748bb59b7e3de910a1bf1f464d18b7ec99ef0f435aa415b4"
        and source.get("candidate_implementation_sha256")
        == "881bde96e6aa49f3f4fd700fc631fddebb9ae9367c0444fcacf26a0c756af968"
        and source.get("direct_control_selection_config_sha256")
        == "326071333f4a7c909f1011c3125a593b3d8f6488899cb3000d1f9b6ce7568c3b",
        "source",
    )
    split = config.get("split")
    _require(
        isinstance(split, Mapping)
        and split.get("validation_cases") == 73
        and split.get("validation_case_digest")
        == "666913e21e291511af73dcecd287416d20eb673c4f47861e4df7ffb52297e024"
        and split.get("validation_loader_order_sha256")
        == "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30"
        and split.get("private_split_manifest_sha256")
        == "4ff881055c45ee87c917fbfe1a7ed5102ef63b9426539aea647eea7b65e3077f"
        and split.get("locked_test_read") is False
        and split.get("processed_only_extra_read") is False,
        "split",
    )
    cells = config.get("candidate_cells")
    _require(
        isinstance(cells, Mapping)
        and tuple(cells.get("ordered", ())) == CELL_ORDER
        and cells.get("seed") == 1103
        and cells.get("same_oracle_nominated_rank_required") is True
        and cells.get("same_train_only_response_basis_required") is True
        and cells.get("same_initial_combined_checkpoint_for_finetunes") is True
        and cells.get("report_all_cells") is True
        and cells.get("architecture_cells_are_ablation_not_final_objective_selection")
        is True,
        "candidate_cells",
    )
    control = config.get("control")
    _require(
        isinstance(control, Mapping)
        and tuple(control.get("eligible_matched_training_labels", ()))
        == tuple(CONTROL_MAP)
        and control.get("family_mapping") == CONTROL_MAP
        and control.get("released_graph_unet_is_development_reference_not_matched_training_family")
        is True
        and control.get("silent_fallback_if_graph_unet_is_selected") is False,
        "control",
    )
    proposal = config.get("proposal")
    _require(
        isinstance(proposal, Mapping)
        and proposal.get("family") == "release730_response_plus_local_residual"
        and tuple(proposal.get("objective_candidates_in_tie_order", ()))
        == OBJECTIVE_ORDER
        and tuple(proposal.get("selection_cells", ())) == SELECTION_CELLS
        and proposal.get("selection_rule")
        == "minimum_common_initial_checkpoint_endpoint_normalized_validation_utility_then_fixed_objective_order_exact_tie"
        and proposal.get("common_utility")
        == "field_over_initial_field_plus_mean_of_mean_vector_tawss_and_osi_over_their_shared_initial_values"
        and proposal.get("normalizers_fixed_at_shared_initial_combined_checkpoint")
        is True
        and proposal.get("common_utility_is_each_finetune_checkpoint_selector")
        is True
        and proposal.get("absolute_performance_threshold") is None
        and proposal.get("noninferiority_margin") is None
        and proposal.get("automatic_paper_winner") is False
        and proposal.get("automatic_novelty_conclusion") is False,
        "proposal",
    )
    boundary = config.get("boundary")
    _require(
        isinstance(boundary, Mapping)
        and boundary.get("execute_now") is False
        and boundary.get("requires_five_terminal_candidate_results") is True
        and boundary.get("requires_fresh_private_activation") is True
        and boundary.get("validation_development_only") is True
        and boundary.get("locked_test_or_extra_access") is False
        and boundary.get("repair_or_new_variant_authorization") is False
        and boundary.get("paper_performance_claim") is False
        and boundary.get("publish_numeric_result") is False
        and boundary.get("server") == "introai9"
        and boundary.get("excluded_server") == "junjinyong"
        and boundary.get("maintain_public_site") is False,
        "boundary",
    )


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_activation(
    path: str | Path, config: Mapping[str, Any], expected_commit: str
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_candidate_selection_activation.v1"
        and activation.get("protocol_id") == config["protocol_id"]
        and activation.get("public_commit") == expected_commit
        and activation.get("quality_conclusion") == "success",
        "activation_identity",
    )
    for key in ("candidate_result_sha256", "candidate_terminal_record_sha256"):
        values = activation.get(key)
        _require(
            isinstance(values, Mapping)
            and tuple(values) == CELL_ORDER
            and all(_is_sha256(values[cell]) for cell in CELL_ORDER),
            key,
        )
    checkpoints = activation.get("candidate_checkpoint_sha256")
    entries = activation.get("entries")
    _require(
        isinstance(checkpoints, Mapping)
        and tuple(checkpoints) == CELL_ORDER
        and all(_is_sha256(checkpoints[cell]) for cell in CELL_ORDER),
        "candidate_checkpoint_sha256",
    )
    _require(isinstance(entries, list) and len(entries) == 5, "activation_entries")
    for expected_cell, entry in zip(CELL_ORDER, entries):
        _require(
            isinstance(entry, Mapping)
            and entry.get("cell") == expected_cell
            and _safe_relative(entry.get("run_relative_path"))
            and entry.get("result_sha256")
            == activation["candidate_result_sha256"][expected_cell]
            and entry.get("terminal_record_sha256")
            == activation["candidate_terminal_record_sha256"][expected_cell]
            and entry.get("checkpoint_sha256") == checkpoints[expected_cell],
            "activation_entry",
        )
    _require(
        _is_sha256(activation.get("direct_control_selection_result_sha256"))
        and _is_sha256(activation.get("response_basis_sha256"))
        and _is_sha256(activation.get("candidate_selection_config_sha256"))
        and activation.get("validation_case_digest")
        == config["split"]["validation_case_digest"]
        and activation.get("validation_loader_order_sha256")
        == config["split"]["validation_loader_order_sha256"]
        and activation.get("private_split_manifest_sha256")
        == config["split"]["private_split_manifest_sha256"]
        and activation.get("read_locked_test_or_extra") is False
        and activation.get("repair_or_new_variant_authorization") is False
        and activation.get("paper_performance_claim") is False,
        "activation_scope",
    )
    return dict(activation)


def _parse_finite_mapping(payload: Any, keys: Sequence[str], reason: str) -> dict[str, float]:
    _require(isinstance(payload, Mapping), reason)
    result: dict[str, float] = {}
    for key in keys:
        value = float(payload.get(key, math.nan))
        _require(math.isfinite(value) and value >= 0.0, f"{reason}_{key}")
        result[key] = value
    return result


def _validate_candidate_result(
    cell: str, result: Mapping[str, Any], config: Mapping[str, Any]
) -> dict[str, Any]:
    mode, architecture, objective = CELL_IDENTITY[cell]
    split = config["split"]
    _require(
        result.get("schema_version")
        == "aurora.private.aneug_release_730_response_local_result.v1"
        and result.get("protocol_id")
        == "aneug_release_730_response_local_candidate_v1"
        and result.get("status") == "complete"
        and result.get("mode") == mode
        and result.get("architecture_variant") == architecture
        and result.get("objective_variant") == objective
        and result.get("selected_response_rank") in RANKS
        and result.get("seed") == 1103,
        f"{cell}_identity",
    )
    _require(
        result.get("validation_case_count") == 73
        and result.get("validation_case_digest") == split["validation_case_digest"]
        and result.get("validation_loader_order_sha256")
        == split["validation_loader_order_sha256"]
        and result.get("private_split_manifest_sha256")
        == split["private_split_manifest_sha256"]
        and _is_sha256(result.get("response_basis_sha256"))
        and result.get("locked_test_field_case_count_read") == 0
        and result.get("processed_only_extra_field_case_count_read") == 0
        and result.get("case_ids_included") is False
        and result.get("development_only") is True
        and result.get("paper_performance_claim") is False,
        f"{cell}_scope",
    )
    validation = result.get("validation")
    _require(
        isinstance(validation, Mapping)
        and validation.get("case_count") == 73
        and isinstance(validation.get("per_case_without_identifiers"), list)
        and len(validation["per_case_without_identifiers"]) == 73,
        f"{cell}_validation",
    )
    metrics = _parse_finite_mapping(
        validation.get("aggregate"), tuple(NORMALIZER_TO_METRIC.values()), f"{cell}_metrics"
    )
    expected_selection_name = (
        "validation_field_relative_l2"
        if mode == "architecture"
        else "common_initial_checkpoint_endpoint_normalized_validation_utility"
    )
    best_selection_value = float(result.get("best_selection_value", math.nan))
    _require(
        result.get("selection_name") == expected_selection_name
        and math.isfinite(best_selection_value)
        and best_selection_value >= 0.0,
        f"{cell}_checkpoint_selection",
    )
    return {
        "metrics": metrics,
        "rank": int(result["selected_response_rank"]),
        "basis_sha256": result["response_basis_sha256"],
        "public_commit": result.get("public_commit"),
        "config_sha256": result.get("config_sha256"),
        "initial_checkpoint_sha256": result.get(
            "initial_combined_field_checkpoint_sha256"
        ),
        "selection_normalizers": result.get("selection_endpoint_normalizers"),
        "initial_validation": result.get("initial_validation"),
        "best_epoch": int(result.get("best_epoch", 0)),
        "optimizer_steps": int(result.get("optimizer_steps", 0)),
        "parameter_count": int(result.get("parameter_count", 0)),
        "active_parameter_count": int(result.get("active_parameter_count", 0)),
        "elapsed_seconds": float(result.get("elapsed_seconds", math.nan)),
        "best_selection_value": best_selection_value,
    }


def _same_numeric_mapping(left: Mapping[str, float], right: Mapping[str, float]) -> bool:
    return set(left) == set(right) and all(
        math.isclose(float(left[key]), float(right[key]), rel_tol=0.0, abs_tol=1e-12)
        for key in left
    )


def _common_utility(metrics: Mapping[str, float], normalizers: Mapping[str, float]) -> float:
    ratios = {
        name: float(metrics[metric]) / float(normalizers[name])
        for name, metric in NORMALIZER_TO_METRIC.items()
    }
    value = ratios["field"] + (
        ratios["mean_vector"] + ratios["tawss"] + ratios["osi"]
    ) / 3.0
    _require(math.isfinite(value), "common_utility")
    return value


def analyze_candidate_selection(
    results: Mapping[str, Mapping[str, Any]],
    direct_selection: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    validate_config(config)
    _require(tuple(results) == CELL_ORDER, "result_order")
    _require(
        direct_selection.get("schema_version")
        == "aurora.private.aneug_release_730_direct_control_selection_result.v1"
        and direct_selection.get("status") == "complete"
        and direct_selection.get("selection_metric")
        == "case_mean_field_relative_l2"
        and direct_selection.get("locked_test_or_extra_values_read") is False
        and direct_selection.get("candidate_selected") is False
        and direct_selection.get("paper_performance_claim") is False,
        "direct_selection",
    )
    selected_direct = direct_selection.get("selected_direct_control")
    _require(selected_direct in CONTROL_MAP, "selected_direct_control_not_matched_trainable")
    parsed = {
        cell: _validate_candidate_result(cell, results[cell], config) for cell in CELL_ORDER
    }
    _require(len({parsed[cell]["rank"] for cell in CELL_ORDER}) == 1, "rank_alignment")
    _require(
        len({parsed[cell]["basis_sha256"] for cell in CELL_ORDER}) == 1,
        "basis_alignment",
    )
    _require(
        len({parsed[cell]["public_commit"] for cell in CELL_ORDER}) == 1
        and all(
            isinstance(parsed[cell]["public_commit"], str)
            and len(parsed[cell]["public_commit"]) == 40
            for cell in CELL_ORDER
        ),
        "public_commit_alignment",
    )
    _require(
        {parsed[cell]["config_sha256"] for cell in CELL_ORDER}
        == {config["source"]["candidate_config_sha256"]},
        "candidate_config_alignment",
    )
    for cell in CELL_ORDER:
        _require(
            parsed[cell]["best_epoch"] > 0
            and parsed[cell]["optimizer_steps"] > 0
            and parsed[cell]["parameter_count"] > 0
            and parsed[cell]["active_parameter_count"] > 0
            and math.isfinite(parsed[cell]["elapsed_seconds"])
            and parsed[cell]["elapsed_seconds"] > 0.0,
            f"{cell}_efficiency",
        )
    combined_checkpoint = results["architecture_response_plus_residual_field"].get(
        "best_checkpoint_sha256"
    )
    functional_checkpoint_values = {
        parsed[cell]["initial_checkpoint_sha256"] for cell in SELECTION_CELLS
    }
    _require(
        len(functional_checkpoint_values) == 1
        and None not in functional_checkpoint_values,
        "initial_checkpoint_alignment",
    )
    if combined_checkpoint is not None:
        _require(
            _is_sha256(combined_checkpoint)
            and functional_checkpoint_values == {combined_checkpoint},
            "combined_checkpoint_alignment",
        )
    normalizers: dict[str, float] | None = None
    initial_metrics: dict[str, float] | None = None
    for cell in SELECTION_CELLS:
        observed = _parse_finite_mapping(
            parsed[cell]["selection_normalizers"],
            tuple(NORMALIZER_TO_METRIC),
            f"{cell}_normalizers",
        )
        initial = parsed[cell]["initial_validation"]
        _require(isinstance(initial, Mapping), f"{cell}_initial_validation")
        initial_observed = _parse_finite_mapping(
            initial.get("aggregate"),
            tuple(NORMALIZER_TO_METRIC.values()),
            f"{cell}_initial_metrics",
        )
        expected_normalizers = {
            name: initial_observed[metric]
            for name, metric in NORMALIZER_TO_METRIC.items()
        }
        _require(
            all(value > 1e-12 for value in observed.values())
            and _same_numeric_mapping(observed, expected_normalizers),
            f"{cell}_normalizer_initial_alignment",
        )
        if normalizers is None:
            normalizers, initial_metrics = observed, initial_observed
        else:
            _require(_same_numeric_mapping(normalizers, observed), "normalizer_alignment")
            _require(
                initial_metrics is not None
                and _same_numeric_mapping(initial_metrics, initial_observed),
                "initial_validation_alignment",
            )
    _require(normalizers is not None, "normalizers")
    for cell in SELECTION_CELLS:
        expected = _common_utility(parsed[cell]["metrics"], normalizers)
        _require(
            math.isclose(
                parsed[cell]["best_selection_value"],
                expected,
                rel_tol=0.0,
                abs_tol=1e-12,
            ),
            f"{cell}_common_checkpoint_selection",
        )
    utilities = {
        cell: _common_utility(parsed[cell]["metrics"], normalizers)
        for cell in SELECTION_CELLS
    }
    selected_cell = min(
        SELECTION_CELLS,
        key=lambda cell: (
            utilities[cell],
            OBJECTIVE_ORDER.index(CELL_IDENTITY[cell][2]),
        ),
    )
    selected_objective = CELL_IDENTITY[selected_cell][2]
    return {
        "schema_version": "aurora.private.aneug_release_730_candidate_selection_result.v1",
        "protocol_id": config["protocol_id"],
        "status": "complete_validation_only_candidate_selection",
        "evidence_role": "freeze_control_proposal_objective_and_rank_before_matched_training",
        "selected_direct_control": selected_direct,
        "selected_control_family": CONTROL_MAP[str(selected_direct)],
        "selected_proposal_family": config["proposal"]["family"],
        "selected_proposal_objective": selected_objective,
        "selected_proposal_rank": parsed[selected_cell]["rank"],
        "selected_functional_cell": selected_cell,
        "selected_response_basis_sha256": parsed[selected_cell]["basis_sha256"],
        "selection_rule": config["proposal"]["selection_rule"],
        "common_initial_checkpoint_endpoint_normalizers": normalizers,
        "common_validation_utility_by_functional_cell": utilities,
        "candidate_metrics_by_cell": {
            cell: parsed[cell]["metrics"] for cell in CELL_ORDER
        },
        "candidate_efficiency_by_cell": {
            cell: {
                key: parsed[cell][key]
                for key in (
                    "best_epoch",
                    "optimizer_steps",
                    "parameter_count",
                    "active_parameter_count",
                    "elapsed_seconds",
                )
            }
            for cell in CELL_ORDER
        },
        "all_candidate_cells_reported": True,
        "architecture_cells_used_as_ablation_not_objective_selection": True,
        "absolute_performance_threshold": None,
        "noninferiority_margin": None,
        "case_identifiers_included": False,
        "locked_test_or_extra_values_read": False,
        "repair_or_new_variant_authorized": False,
        "automatic_paper_winner": None,
        "automatic_novelty_conclusion": None,
        "paper_performance_claim": False,
    }


def _atomic_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    _require(not target.exists() and not temporary.exists(), "output_exists")
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
    parser.add_argument("--activation", type=Path)
    parser.add_argument("--expected-commit")
    parser.add_argument("--direct-control-selection-result", type=Path)
    parser.add_argument("--response-basis", type=Path)
    parser.add_argument("--candidate-evidence-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.validate_only:
        return 0
    _require(
        args.activation is not None
        and args.expected_commit is not None
        and args.direct_control_selection_result is not None
        and args.response_basis is not None
        and args.candidate_evidence_root is not None
        and args.output is not None,
        "execution_arguments",
    )
    activation = validate_activation(args.activation, config, str(args.expected_commit))
    _require(
        file_sha256(args.config) == activation["candidate_selection_config_sha256"],
        "candidate_selection_config_hash",
    )
    _require(
        file_sha256(args.direct_control_selection_result)
        == activation["direct_control_selection_result_sha256"],
        "direct_selection_hash",
    )
    _require(
        file_sha256(args.response_basis) == activation["response_basis_sha256"],
        "response_basis_hash",
    )
    results: dict[str, Mapping[str, Any]] = {}
    evidence_root = args.candidate_evidence_root.resolve()
    _require(evidence_root.is_dir(), "candidate_evidence_root")
    for entry in activation["entries"]:
        cell = str(entry["cell"])
        run_root = (evidence_root / PurePosixPath(entry["run_relative_path"])).resolve()
        _require(run_root.is_relative_to(evidence_root), f"{cell}_path_escape")
        result_path = run_root / "result.json"
        terminal_path = run_root / "attempt.status.json"
        checkpoint_path = run_root / "checkpoints" / "best.pt"
        _require(
            result_path.is_file()
            and terminal_path.is_file()
            and checkpoint_path.is_file()
            and file_sha256(result_path) == activation["candidate_result_sha256"][cell]
            and file_sha256(terminal_path)
            == activation["candidate_terminal_record_sha256"][cell]
            and file_sha256(checkpoint_path)
            == activation["candidate_checkpoint_sha256"][cell],
            f"{cell}_hash",
        )
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        _require(
            terminal.get("exit_code") == 0 and terminal.get("complete") is True,
            f"{cell}_terminal",
        )
        results[cell] = json.loads(result_path.read_text(encoding="utf-8"))
    direct = json.loads(args.direct_control_selection_result.read_text(encoding="utf-8"))
    output = analyze_candidate_selection(results, direct, config)
    _require(
        output["selected_response_basis_sha256"]
        == activation["response_basis_sha256"],
        "activation_basis_alignment",
    )
    _require(
        all(
            results[cell].get("public_commit") == str(args.expected_commit)
            for cell in CELL_ORDER
        ),
        "activation_public_commit_alignment",
    )
    output.update(
        {
            "public_commit": str(args.expected_commit),
            "activation_sha256": file_sha256(args.activation),
            "candidate_result_sha256": dict(activation["candidate_result_sha256"]),
            "candidate_terminal_record_sha256": dict(
                activation["candidate_terminal_record_sha256"]
            ),
            "direct_control_selection_result_sha256": activation[
                "direct_control_selection_result_sha256"
            ],
        }
    )
    _atomic_json(args.output, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
