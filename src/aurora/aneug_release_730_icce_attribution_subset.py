"""Compile fully terminal five-seed subsets of the ICCE attribution matrix.

The complete manuscript artifact compiler correctly requires all 72 registered
validation cells.  This smaller compiler makes already-complete main-attribution
methods auditable while the remaining cells run.  Every included method must
have all five terminal validation seeds, and the analysis uses the exact method
and comparator bootstrap offsets of the eventual six-method analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_release_730_icce_analysis import analyze_attribution_subset
from aurora.aneug_release_730_icce_revision import (
    METHOD_IDS,
    METHOD_REGIME_SEPARATED,
    TRAINING_SEEDS,
)


INPUT_SCHEMA = "aurora.private.aneug_release_730_icce_attribution_subset_inputs.v1"
OUTPUT_SCHEMA = "aurora.aneug_release_730_icce_attribution_subset_bundle.v1"
TERMINAL_SCHEMA = "aurora.private.aneug_release_730_icce_fixed_budget_terminal.v1"
PROTOCOL_ID = "aneug_release_730_icce_validation_revision_v2"


class ICCEAttributionSubsetError(RuntimeError):
    """Raised when a completed-method subset is incomplete or not traceable."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ICCEAttributionSubsetError(reason)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _load(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(payload, Mapping), f"mapping:{path.name}")
    return payload


def _resolve(base: Path, value: Any, label: str) -> Path:
    _require(isinstance(value, str) and bool(value), label)
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def compile_attribution_subset(
    *,
    input_manifest_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Validate complete method blocks and atomically emit their analysis."""

    _require(not output_path.exists(), "output_exists")
    manifest = _load(input_manifest_path)
    methods_value = manifest.get("methods")
    _require(isinstance(methods_value, list), "manifest_methods")
    methods = tuple(str(value) for value in methods_value)
    _require(
        len(methods) >= 2
        and METHOD_REGIME_SEPARATED in methods
        and methods == tuple(method for method in METHOD_IDS if method in methods)
        and len(set(methods)) == len(methods),
        "canonical_completed_methods",
    )
    _require(
        manifest.get("schema_version") == INPUT_SCHEMA
        and manifest.get("status") == "complete_five_seed_validation_methods"
        and manifest.get("protocol_id") == PROTOCOL_ID
        and manifest.get("training_seeds") == list(TRAINING_SEEDS)
        and manifest.get("locked_test_or_extra_read") is False
        and manifest.get("case_identifiers_included") is False,
        "manifest_scope",
    )
    base = input_manifest_path.parent
    protocol_path = _resolve(base, manifest.get("protocol_path"), "protocol_path")
    _require(
        protocol_path.is_file()
        and _is_sha256(manifest.get("protocol_sha256"))
        and _sha256(protocol_path) == manifest["protocol_sha256"],
        "protocol_hash",
    )
    protocol = _load(protocol_path)
    entries = manifest.get("cells")
    _require(
        isinstance(entries, list) and len(entries) == len(methods) * len(TRAINING_SEEDS),
        "manifest_cells",
    )

    results: dict[str, dict[int, Mapping[str, Any]]] = {
        method: {} for method in methods
    }
    input_hashes: dict[str, dict[str, str]] = {}
    for entry in entries:
        _require(isinstance(entry, Mapping), "cell_entry")
        method = entry.get("method_id")
        training_seed = entry.get("training_seed")
        _require(
            method in methods
            and training_seed in TRAINING_SEEDS
            and training_seed not in results[method],
            "cell_identity",
        )
        result_path = _resolve(base, entry.get("result_path"), "result_path")
        terminal_path = _resolve(base, entry.get("terminal_path"), "terminal_path")
        _require(
            result_path.is_file()
            and terminal_path.is_file()
            and _is_sha256(entry.get("result_sha256"))
            and _is_sha256(entry.get("terminal_sha256"))
            and _sha256(result_path) == entry["result_sha256"]
            and _sha256(terminal_path) == entry["terminal_sha256"],
            "cell_hash",
        )
        result = _load(result_path)
        terminal = _load(terminal_path)
        _require(
            terminal.get("schema_version") == TERMINAL_SCHEMA
            and terminal.get("status") == "complete_validation_only"
            and terminal.get("protocol_id") == PROTOCOL_ID
            and terminal.get("method_id") == method
            and terminal.get("training_seed") == training_seed
            and terminal.get("label_percent") == 100
            and terminal.get("scheduler_state") == "F"
            and terminal.get("scheduler_substate") == 92
            and terminal.get("exit_status") == 0
            and terminal.get("run_count") == 1
            and terminal.get("scientific_entry_count") == 1
            and terminal.get("result_sha256") == entry["result_sha256"]
            and terminal.get("validation_case_count") == 73
            and terminal.get("validation_prediction_count") == 73
            and terminal.get("validation_prediction_sha256_all_exact") is True
            and terminal.get("recovery_checkpoint_count") == 26
            and terminal.get("recovery_checkpoint_sha256_all_exact") is True
            and terminal.get("locked_test_field_case_count_read") == 0
            and terminal.get("processed_only_extra_field_case_count_read") == 0
            and terminal.get("case_ids_included") is False
            and terminal.get("paper_claim") is False,
            "terminal_contract",
        )
        results[str(method)][int(training_seed)] = result
        input_hashes[f"{method}:seed{training_seed}"] = {
            "result_sha256": str(entry["result_sha256"]),
            "terminal_sha256": str(entry["terminal_sha256"]),
        }
    _require(
        all(set(results[method]) == set(TRAINING_SEEDS) for method in methods),
        "complete_method_blocks",
    )

    analysis = analyze_attribution_subset(results, protocol)
    output = {
        "schema_version": OUTPUT_SCHEMA,
        "status": "complete_five_seed_validation_methods",
        "protocol_id": PROTOCOL_ID,
        "completed_methods": list(methods),
        "analysis": analysis,
        "input_manifest_sha256": _sha256(input_manifest_path),
        "protocol_sha256": _sha256(protocol_path),
        "input_terminal_result_sha256": input_hashes,
        "analysis_core_sha256": _sha256(
            Path(__file__).with_name("aneug_release_730_icce_analysis.py")
        ),
        "locked_test_or_extra_read": False,
        "case_identifiers_included": False,
        "full_attribution_required": set(methods) != set(METHOD_IDS),
        "paper_claim": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{output_path.name}.", dir=output_path.parent)
    )
    temporary_path = temporary_directory / output_path.name
    try:
        temporary_path.write_text(
            json.dumps(output, sort_keys=True, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)
        temporary_directory.rmdir()
    return output


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = compile_attribution_subset(
        input_manifest_path=args.input_manifest,
        output_path=args.output,
    )
    print(
        json.dumps(
            {
                "output_sha256": _sha256(args.output),
                "completed_method_count": len(output["completed_methods"]),
                "training_seed_count": len(output["analysis"]["training_seeds"]),
                "paired_case_count": output["analysis"]["paired_case_count"],
                "locked_test_or_extra_read": False,
                "paper_claim": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
