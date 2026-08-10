"""Method-free P0 for anchor-conditioned Aneumo boundary-condition transport."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_range import archive_for_case, fetch_member, load_archive_index


class AneumoBCTransportP0Error(RuntimeError):
    """Raised when the frozen P0 contract cannot be evaluated faithfully."""


def _imports() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - server runtime
        raise AneumoBCTransportP0Error("P0 requires numpy.") from exc
    return np


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneumo_bc_transport_p0.v1":
        raise AneumoBCTransportP0Error("Unexpected P0 schema version.")
    if payload.get("protocol_id") != "aneumo_anchor_conditioned_bc_transport_p0_v1":
        raise AneumoBCTransportP0Error("Unexpected P0 protocol id.")
    if payload.get("status") != "preregistered_before_first_introai9_pbs_execution":
        raise AneumoBCTransportP0Error("P0 must remain prospectively registered.")
    candidate = payload["candidate"]
    if (
        float(candidate["score"]) != 33.5
        or float(candidate["admission_threshold"]) != 32.0
        or sum(float(value) for value in candidate["axis_scores"]) != 33.5
    ):
        raise AneumoBCTransportP0Error("Frozen candidate score changed.")
    source = payload["source"]
    if (
        source["hf_repo_commit"] != "f801adee816c18d3e18b23e6fcb147fe4c264209"
        or source["upstream_code_commit"] != "701d53dde3489d84dbe9bc8324254629162eb45a"
        or source["archive"] != "1.zip"
        or len(source["mass_flows_kg_s"]) != 8
    ):
        raise AneumoBCTransportP0Error("Pinned source contract changed.")
    access = payload["access"]
    families = {int(value) for value in access["base_families"]}
    train = {int(value) for value in access["historical_pilot_train_base_families"]}
    validation = {
        int(value) for value in access["historical_pilot_validation_base_families"]
    }
    test = {int(value) for value in access["historical_pilot_test_base_families"]}
    if families != {1} or not families <= train or families & (validation | test):
        raise AneumoBCTransportP0Error("P0 may access only registered train family 1.")
    mapping = {
        int(key): [int(case) for case in cases]
        for key, cases in access["cases_by_base_family"].items()
    }
    if mapping != {1: [1, 2]}:
        raise AneumoBCTransportP0Error("P0 case mapping changed.")
    if any(archive_for_case(case) != source["archive"] for case in mapping[1]):
        raise AneumoBCTransportP0Error("Registered cases no longer map to one archive.")
    if any(
        access[key] is not False
        for key in (
            "pressure_channel_read_for_scientific_analysis",
            "validation_or_test_field_access",
            "persistent_field_cache",
            "outer_test_access",
        )
    ):
        raise AneumoBCTransportP0Error("P0 access boundary changed.")
    audit = payload["audit"]
    if (
        float(audit["anchor_mass_flow_kg_s"]) != 0.0025
        or float(audit["analytic_power"]) != 1.075
        or int(audit["required_members"]) != 16
        or int(audit["network_retry_count"]) != 0
        or audit["success_thresholds"] is not None
    ):
        raise AneumoBCTransportP0Error("P0 audit contract changed.")
    execution = payload["execution"]
    if (
        execution["server"] != "introai9"
        or execution["excluded_server"] != "junjinyong"
        or int(execution["ngpus"]) != 0
        or int(execution["maximum_submissions_for_exact_public_source"]) != 1
    ):
        raise AneumoBCTransportP0Error("P0 execution boundary changed.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def _relative_l2(prediction: Any, target: Any) -> float:
    np = _imports()
    denominator = float(np.linalg.norm(target.reshape(-1)))
    if denominator <= 0.0:
        raise AneumoBCTransportP0Error("Response target has zero norm.")
    return float(np.linalg.norm((prediction - target).reshape(-1)) / denominator)


def run_p0(config: Mapping[str, Any], *, public_source_commit: str) -> dict[str, Any]:
    np = _imports()
    if not __import__("re").fullmatch(r"[0-9a-f]{40}", public_source_commit):
        raise AneumoBCTransportP0Error("Public source commit must be a full SHA.")
    source = config["source"]
    access = config["access"]
    audit = config["audit"]
    root = (
        f"https://huggingface.co/datasets/{source['hf_repo']}/resolve/"
        f"{source['hf_repo_commit']}"
    )
    archive_url = f"{root}/{source['archive']}"
    members, archive_metadata = load_archive_index(archive_url)
    flows = [float(value) for value in source["mass_flows_kg_s"]]
    anchor_index = flows.index(float(audit["anchor_mass_flow_kg_s"]))
    power = float(audit["analytic_power"])
    sample_count = int(access["nodes_per_case"])
    seed = int(access["node_selection_seed"])
    member_rows: list[dict[str, Any]] = []
    case_errors: list[float] = []
    response_energies: list[float] = []
    coordinate_identity = True
    all_finite = True
    all_n_by_7 = True
    sampled_velocity_nondegenerate = True

    for family in access["base_families"]:
        for case in access["cases_by_base_family"][str(family)]:
            reference_coordinates = None
            selected = None
            velocity_fields: list[Any] = []
            for flow in flows:
                member_name = f"{case}/npy/m={flow:g}/array_internal_{case}.npy"
                if member_name not in members:
                    raise AneumoBCTransportP0Error(
                        f"Required source member is missing: {member_name}"
                    )
                member = members[member_name]
                raw = fetch_member(archive_url, member)
                array = np.load(io.BytesIO(raw), allow_pickle=False)
                all_n_by_7 = all_n_by_7 and array.ndim == 2 and array.shape[1] == 7
                if not all_n_by_7:
                    raise AneumoBCTransportP0Error(
                        f"Unexpected array shape for {member_name}: {array.shape}"
                    )
                all_finite = all_finite and bool(np.isfinite(array).all())
                if not all_finite:
                    raise AneumoBCTransportP0Error(f"Non-finite source array: {member_name}")
                coordinates = np.asarray(array[:, :3])
                if reference_coordinates is None:
                    if int(array.shape[0]) < sample_count:
                        raise AneumoBCTransportP0Error("Source array has too few nodes.")
                    reference_coordinates = coordinates.copy()
                    generator = np.random.default_rng(seed + int(case))
                    selected = np.sort(
                        generator.choice(array.shape[0], size=sample_count, replace=False)
                    )
                else:
                    coordinate_identity = coordinate_identity and bool(
                        np.array_equal(coordinates, reference_coordinates)
                    )
                    if not coordinate_identity:
                        raise AneumoBCTransportP0Error(
                            f"Coordinates differ across conditions for case {case}."
                        )
                velocity = np.asarray(array[selected, 4:7], dtype=np.float64)
                sampled_velocity_nondegenerate = (
                    sampled_velocity_nondegenerate
                    and float(np.linalg.norm(velocity.reshape(-1))) > 0.0
                )
                velocity_fields.append(velocity)
                member_rows.append(
                    {
                        "case_id": int(case),
                        "base_family": int(family),
                        "mass_flow_kg_s": flow,
                        "member": member_name,
                        "crc32": f"{member.crc32:08x}",
                        "compressed_size": int(member.compressed_size),
                        "uncompressed_size": int(member.uncompressed_size),
                    }
                )
            anchor = velocity_fields[anchor_index]
            per_case_errors = []
            for index, (flow, target) in enumerate(zip(flows, velocity_fields)):
                prediction = (flow / flows[anchor_index]) ** power * anchor
                if index == anchor_index and not np.array_equal(prediction, anchor):
                    raise AneumoBCTransportP0Error("Analytic control is not anchor identity.")
                if index != anchor_index:
                    response = target - anchor
                    response_energy = float(np.sum(response * response))
                    response_energies.append(response_energy)
                    per_case_errors.append(_relative_l2(prediction - anchor, response))
            case_errors.append(float(np.mean(per_case_errors)))

    checks = {
        "exact_source_and_upstream_commits": True,
        "registered_cases_are_historical_train_family_only": True,
        "all_required_members_exist_and_pass_crc": len(member_rows)
        == int(audit["required_members"]),
        "all_arrays_are_finite_n_by_7": bool(all_finite and all_n_by_7),
        "coordinates_are_bit_identical_across_conditions": bool(coordinate_identity),
        "sampled_velocity_fields_are_finite_and_nondegenerate": bool(
            sampled_velocity_nondegenerate
        ),
        "all_nonanchor_response_energies_are_positive": bool(
            response_energies and min(response_energies) > 0.0
        ),
        "analytic_power_control_is_exact_identity_at_anchor_and_finite": bool(
            case_errors and all(math.isfinite(value) for value in case_errors)
        ),
        "no_pressure_validation_test_model_checkpoint_gpu_or_outer_test_access": True,
    }
    passed = all(checks.values())
    result = {
        "schema_version": "aurora.aneumo_bc_transport_p0.result.v1",
        "protocol_id": config["protocol_id"],
        "status": "passed_asset_semantics_gate" if passed else "failed_asset_semantics_gate",
        "scientific_gate_evaluated": True,
        "public_source_commit": public_source_commit,
        "config_sha256": config["_config_sha256"],
        "source": {
            "hf_repo_commit": source["hf_repo_commit"],
            "upstream_code_commit": source["upstream_code_commit"],
            "archive": source["archive"],
            "archive_content_length": int(archive_metadata["content_length"]),
            "archive_entries": int(archive_metadata["entries"]),
        },
        "access": {
            "base_families": 1,
            "cases": 2,
            "conditions": 8,
            "sampled_nodes_per_case": sample_count,
            "members_crc_verified": len(member_rows),
            "pressure_analysis": False,
            "validation_field_access": False,
            "test_field_access": False,
            "persistent_field_cache": False,
            "model_or_checkpoint_access": False,
            "gpu_access": False,
            "outer_test_access": False,
        },
        "diagnostics": {
            "fixed_analytic_power": power,
            "train_family_case_mean_response_relative_l2": float(np.mean(case_errors)),
            "train_family_case_worst_response_relative_l2": float(max(case_errors)),
            "minimum_nonanchor_response_energy": float(min(response_energies)),
        },
        "checks": checks,
        "passed_checks": sum(bool(value) for value in checks.values()),
        "total_checks": len(checks),
        "gate_passed": passed,
        "decision": (
            "open_separate_train_only_method_free_p1_registration"
            if passed
            else "close_exact_p0_without_repair_or_rerun"
        ),
        "authorization": {
            "method": False,
            "architecture": False,
            "gpu_training": False,
            "validation_or_test_access": False,
            "paper_contribution": False,
        },
    }
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--public-source-commit", required=True)
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    if os.environ.get("AURORA_SOURCE_COMMIT") != args.public_source_commit:
        raise AneumoBCTransportP0Error("Environment source commit mismatch.")
    result = run_p0(config, public_source_commit=args.public_source_commit)
    args.result.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.result.with_suffix(args.result.suffix + ".partial")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(args.result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate_passed"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
