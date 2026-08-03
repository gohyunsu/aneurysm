"""Fresh exact-data adequacy sanity after the failed AURORA G1r.

G1s reuses the G1r training and evaluation implementation without changing the
density estimator, operator, validation/test sizes, metrics, or thresholds.
Only the five simulation-family seeds and the number of training geometries
change.  A pass can authorize progression to nonlinear and irregular-3D
experiments, but data quantity is not a method contribution.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .controlled_pde import ControlledPDEError
from .controlled_pde_reentry import (
    _environment,
    _imports,
    _sha256,
    _write_json,
    run_experiment as _run_g1r_experiment,
)


def _require_keys(payload: Mapping[str, Any], keys: Sequence[str], label: str) -> None:
    missing = sorted(set(keys) - set(payload))
    if missing:
        raise ControlledPDEError(f"{label} is missing keys: {missing}")


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate the immutable prospective G1s contract."""

    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    _require_keys(
        payload,
        [
            "schema_version",
            "experiment_id",
            "status",
            "source_gate",
            "source_diagnostic",
            "may_relabel_g1_or_g1r",
            "may_claim_data_quantity_as_method_contribution",
            "g1r_config",
            "g1r_config_sha256",
            "g1r_result",
            "g1r_result_sha256",
            "da1_result",
            "da1_result_sha256",
            "da2_config",
            "da2_config_sha256",
            "da2_result",
            "da2_result_sha256",
            "changes_from_g1r",
            "density_estimator",
            "seeds",
            "split_seed_offsets",
            "grid_points",
            "train_geometries",
            "validation_geometries",
            "test_geometries",
            "conditions_per_geometry",
            "hidden_dim",
            "observation_masks",
            "primary_masks",
            "density_training",
            "operator_training",
            "direct_baseline_training",
            "evaluation",
            "success_thresholds",
            "decision_rule",
            "interpretation",
        ],
        "G1s config",
    )
    if payload["schema_version"] != "aurora.controlled_pde_g1s.v1":
        raise ControlledPDEError("Unexpected G1s schema version.")
    if payload["status"] != "preregistered_before_fresh_test":
        raise ControlledPDEError("G1s must remain registered before test access.")
    if payload["source_gate"] != "G1r" or payload["source_diagnostic"] != "DA2":
        raise ControlledPDEError("G1s must remain linked to failed G1r and DA2.")
    if (
        payload["may_relabel_g1_or_g1r"] is not False
        or payload["may_claim_data_quantity_as_method_contribution"] is not False
    ):
        raise ControlledPDEError(
            "G1s cannot relabel prior failures or promote data quantity to novelty."
        )

    pins = (
        ("g1r_config", "g1r_config_sha256", "G1r config"),
        ("g1r_result", "g1r_result_sha256", "G1r result"),
        ("da1_result", "da1_result_sha256", "DA1 result"),
        ("da2_config", "da2_config_sha256", "DA2 config"),
        ("da2_result", "da2_result_sha256", "DA2 result"),
    )
    for path_key, digest_key, label in pins:
        artifact = (config_path.parent / payload[path_key]).resolve()
        if not artifact.is_file() or _sha256(artifact) != payload[digest_key]:
            raise ControlledPDEError(f"Pinned {label} does not match G1s.")

    g1r_path = (config_path.parent / payload["g1r_config"]).resolve()
    g1r = json.loads(g1r_path.read_text(encoding="utf-8"))
    invariant_keys = (
        "split_seed_offsets",
        "grid_points",
        "validation_geometries",
        "test_geometries",
        "conditions_per_geometry",
        "hidden_dim",
        "observation_masks",
        "primary_masks",
        "density_training",
        "operator_training",
        "direct_baseline_training",
        "evaluation",
        "success_thresholds",
    )
    changed = [key for key in invariant_keys if payload[key] != g1r[key]]
    if changed:
        raise ControlledPDEError(
            f"G1s changed frozen G1r fields beyond data adequacy: {changed}"
        )
    if int(g1r["train_geometries"]) != 768 or int(payload["train_geometries"]) != 3072:
        raise ControlledPDEError("G1s must change training geometry from 768 to 3072.")
    if payload["density_estimator"] != "empirical_nll":
        raise ControlledPDEError("G1s must retain the original empirical NLL.")
    if payload["changes_from_g1r"] != [
        "five_entirely_fresh_simulation_family_seeds",
        "training_geometries_increased_from_768_to_3072",
    ]:
        raise ControlledPDEError("G1s changes from G1r must remain exhaustive.")

    seeds = [int(item) for item in payload["seeds"]]
    if len(seeds) != 5 or len(set(seeds)) != 5:
        raise ControlledPDEError("G1s requires five unique fresh seeds.")
    prior_seeds: set[int] = set()
    for relative in (
        "controlled_pde_g1.json",
        "controlled_pde_g1r.json",
        "controlled_pde_density_attribution.json",
        "controlled_pde_density_development.json",
    ):
        prior = json.loads((config_path.parent / relative).read_text(encoding="utf-8"))
        prior_seeds.update(int(item) for item in prior["seeds"])
    if prior_seeds & set(seeds):
        raise ControlledPDEError("G1s seeds overlap a prior exact or development run.")

    decision = payload["decision_rule"]
    if decision != {
        "worst_seed_or_route_decides": True,
        "pass_authorizes_progression_to_nonlinear_and_irregular_3d_experiments": True,
        "pass_does_not_establish_method_novelty_or_baseline_superiority": True,
        "failure_keeps_nonlinear_and_irregular_3d_confirmation_blocked": True,
    }:
        raise ControlledPDEError("G1s decision rule changed after registration.")
    return payload


def run_experiment(config: Mapping[str, Any], require_cuda: bool) -> dict[str, Any]:
    """Run the shared exact pipeline and attach G1s non-inflation decisions."""

    result = _run_g1r_experiment(config, require_cuda)
    passed = bool(result["aggregate"]["gate"]["passed"])
    result.update(
        {
            "failed_g1_relabeled": False,
            "failed_g1r_relabeled": False,
            "data_quantity_claimed_as_method_contribution": False,
            "nonlinear_or_3d_confirmatory_training_authorized": passed,
        }
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    (args.output / "command.txt").write_text(
        " ".join(shlex.quote(item) for item in sys.argv) + "\n", encoding="utf-8"
    )
    (args.output / "git_commit.txt").write_text(
        args.git_commit + "\n", encoding="utf-8"
    )
    (args.output / "config.sha256").write_text(
        _sha256(args.config) + "\n", encoding="utf-8"
    )
    _write_json(args.output / "run_config.json", config)
    try:
        result = run_experiment(config, args.require_cuda)
        _, torch = _imports()
        result.update(
            {
                "git_commit": args.git_commit,
                "started_at_utc": started,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "environment": _environment(torch),
            }
        )
        _write_json(args.output / "metrics.json", result)
        _write_json(
            args.output / "status.json",
            {
                "state": "completed",
                "gate_passed": result["aggregate"]["gate"]["passed"],
                "failed_g1_relabeled": False,
                "failed_g1r_relabeled": False,
                "nonlinear_or_3d_confirmatory_training_authorized": result[
                    "nonlinear_or_3d_confirmatory_training_authorized"
                ],
            },
        )
        return 0
    except Exception as exc:
        _write_json(
            args.output / "status.json",
            {
                "state": "failed",
                "error_type": type(exc).__name__,
                "message": str(exc),
                "started_at_utc": started,
                "failed_at_utc": datetime.now(timezone.utc).isoformat(),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
