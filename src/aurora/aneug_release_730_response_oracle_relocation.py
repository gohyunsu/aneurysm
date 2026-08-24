"""Relocate the exact release-730 response oracle without changing its science.

The base configuration, implementation, activation, data, split, train audit,
rank grid and metrics remain hash-identical to the validated introai9
contract.  A second private activation authorizes only the execution account,
queue and output-root relocation.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from aurora.aneug_release_730_response_oracle import (
    _require,
    file_sha256,
    load_config as load_base_config,
    run_oracle,
    validate_activation as validate_base_activation,
)


def load_relocation_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_relocation_config(config)
    return config


def validate_relocation_config(config: Mapping[str, Any]) -> None:
    _require(
        config.get("schema_version")
        == "aurora.aneug_release_730_response_oracle_relocation.v1",
        "relocation_schema",
    )
    _require(
        config.get("protocol_id")
        == "aneug_release_730_response_oracle_relocation_junjinyong_v1",
        "relocation_protocol",
    )
    _require(config.get("status") == "prepared_execution_relocation_only", "relocation_status")
    base = config["base_scientific_contract"]
    _require(
        base["protocol_id"] == "aneug_release_730_response_oracle_v1"
        and base["public_commit"] == "1c5039292d60e9dcbb722318e43bacc66de1ad36"
        and base["config_sha256"]
        == "f3161f7d1d88a7a7f97c8965b3d996b670667d8a6fc2f0efc471429c1327a924"
        and base["implementation_sha256"]
        == "f58cd12c14d347ebd7d1554577c268fc6cdb8bcc26370b1404681a0c7de3d47a"
        and base["pbs_sha256"]
        == "d9fc96dca522494bc025d0fc8717aeefaf5f45720763d9ac65b3571e322a6654"
        and base["activation_sha256"]
        == "1658182882afc927f0acb849356bb8fc27d331dacad47f96970d34073417a7b5",
        "base_scientific_contract",
    )
    invariants = config["scientific_invariants"]
    _require(
        invariants["train_cases"] == 584
        and invariants["validation_cases"] == 73
        and invariants["locked_test_cases_read"] == 0
        and invariants["processed_only_extra_cases_read"] == 0
        and invariants["rank_grid"] == [0, 16, 32, 64, 128, 256]
        and invariants["learned_predictor"] is False
        and invariants["automatic_rank_selection"] is False
        and invariants["paper_performance_claim"] is False,
        "scientific_invariants",
    )
    runtime = config["runtime"]
    _require(
        runtime["execution_account"] == "junjinyong"
        and runtime["queue"] == "ssu_a6gpu"
        and runtime["Qlist"] == "a6000"
        and runtime["host_constraint"] is None
        and runtime["ncpus"] == 4
        and runtime["memory_gb"] == 64
        and runtime["ngpus"] == 1
        and runtime["walltime"] == "12:00:00"
        and runtime["container_sha256"]
        == "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        "relocation_runtime",
    )
    authorization = config["authorization"]
    _require(
        authorization["requires_fresh_private_relocation_activation"]
        and authorization["requires_base_private_activation"]
        and authorization["server_relocation_only"]
        and not authorization["change_scientific_contract"]
        and not authorization["read_locked_test"]
        and not authorization["read_processed_only_extra"]
        and not authorization["publish_numeric_result"]
        and not authorization["maintain_public_site"],
        "relocation_authorization",
    )


def validate_relocation_activation(
    path: str | Path,
    config: Mapping[str, Any],
    expected_execution_commit: str,
) -> dict[str, Any]:
    activation = json.loads(Path(path).read_text(encoding="utf-8"))
    base = config["base_scientific_contract"]
    _require(
        activation.get("schema_version")
        == "aurora.private.aneug_release_730_response_oracle_relocation_activation.v1",
        "relocation_activation_schema",
    )
    _require(activation.get("protocol_id") == config["protocol_id"], "relocation_activation_protocol")
    _require(
        activation.get("execution_public_commit") == expected_execution_commit
        and activation.get("quality_conclusion") == "success",
        "relocation_activation_public",
    )
    _require(
        activation.get("scientific_public_commit") == base["public_commit"]
        and activation.get("base_config_sha256") == base["config_sha256"]
        and activation.get("base_implementation_sha256") == base["implementation_sha256"]
        and activation.get("base_activation_sha256") == base["activation_sha256"],
        "relocation_activation_base",
    )
    _require(
        activation.get("execution_account") == config["runtime"]["execution_account"]
        and activation.get("queue") == config["runtime"]["queue"]
        and activation.get("Qlist") == config["runtime"]["Qlist"],
        "relocation_activation_runtime",
    )
    _require(
        activation.get("authorized_stage") == "single_validation_response_oracle_relocation"
        and activation.get("server_relocation_only") is True
        and activation.get("scientific_contract_changed") is False
        and activation.get("read_locked_test_or_extra") is False,
        "relocation_activation_scope",
    )
    return activation


def _verify_base_bytes(project_root: Path, config: Mapping[str, Any]) -> None:
    base = config["base_scientific_contract"]
    for path_key, digest_key, label in (
        ("config_path", "config_sha256", "base_config"),
        ("implementation_path", "implementation_sha256", "base_implementation"),
        ("pbs_path", "pbs_sha256", "base_pbs"),
    ):
        path = project_root / base[path_key]
        _require(path.is_file() and file_sha256(path) == base[digest_key], label)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--relocation-config", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--relocation-activation", type=Path)
    parser.add_argument("--base-activation", type=Path)
    parser.add_argument("--expected-execution-commit")
    parser.add_argument("--transient", type=Path)
    parser.add_argument("--steady", type=Path)
    parser.add_argument("--public-split", type=Path)
    parser.add_argument("--private-split", type=Path)
    parser.add_argument("--train-audit-public", type=Path)
    parser.add_argument("--train-audit-private", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--basis", type=Path)
    args = parser.parse_args(argv)
    relocation = load_relocation_config(args.relocation_config)
    if args.validate_only:
        return 0
    required = (
        args.project_root,
        args.relocation_activation,
        args.base_activation,
        args.expected_execution_commit,
        args.transient,
        args.steady,
        args.public_split,
        args.private_split,
        args.train_audit_public,
        args.train_audit_private,
        args.result,
        args.basis,
    )
    _require(all(value is not None for value in required), "relocation_execution_arguments")
    _require(os.environ.get("AURORA_EXECUTION_ACCOUNT") == "junjinyong", "execution_account")
    _verify_base_bytes(args.project_root, relocation)
    base_path = args.project_root / relocation["base_scientific_contract"]["config_path"]
    base_config = load_base_config(base_path)
    validate_base_activation(
        args.base_activation,
        base_config,
        relocation["base_scientific_contract"]["public_commit"],
    )
    validate_relocation_activation(
        args.relocation_activation,
        relocation,
        args.expected_execution_commit,
    )
    base = relocation["base_scientific_contract"]
    provenance = {
        "public_commit": base["public_commit"],
        "execution_public_commit": args.expected_execution_commit,
        "config_sha256": base["config_sha256"],
        "activation_sha256": file_sha256(args.base_activation),
        "relocation_config_sha256": file_sha256(args.relocation_config),
        "relocation_activation_sha256": file_sha256(args.relocation_activation),
        "execution_account": "junjinyong",
        "execution_queue": "ssu_a6gpu",
        "processed_v5_sha256": base["processed_v5_sha256"],
        "private_split_manifest_sha256": base["private_split_manifest_sha256"],
        "private_train_audit_sha256": base["private_train_audit_sha256"],
        "direct_baseline_terminal_record_sha256": json.loads(
            args.base_activation.read_text(encoding="utf-8")
        )["direct_baseline_terminal_record_sha256"],
    }
    run_oracle(
        base_config,
        {
            "transient": args.transient,
            "steady": args.steady,
            "public_split": args.public_split,
            "private_split": args.private_split,
            "train_audit_public": args.train_audit_public,
            "train_audit_private": args.train_audit_private,
        },
        args.result,
        args.basis,
        provenance,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
