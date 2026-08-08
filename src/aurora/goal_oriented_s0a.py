"""Validate the prospective S0a asset/runtime contract.

S0a is intentionally method-free.  This module validates the public contract;
it does not read medical payloads, run a solver, train a model, or select a
checkpoint.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


class S0AProtocolError(ValueError):
    """Raised when the S0a contract no longer preserves its audit boundary."""


EXPECTED_CHECKS = {
    "official_archive_size_and_md5_match",
    "five_statistical_csv_members_match",
    "patient_lesion_control_counts_match",
    "six_multi_lesion_patient_groups_recovered",
    "all_105_lesions_have_exact_identifier_linked_cta_parent_aneurysm_stl_and_aneurysm_stl",
    "no_row_order_or_filename_similarity_only_linkage",
    "nifti_spacing_orientation_and_stl_units_frames_are_finite_and_plausible",
    "solver_container_is_pinned_by_sha256_and_license",
    "solver_container_has_mesh_steady_forward_and_discrete_adjoint_or_verified_shape_gradient_capability",
    "aggregate_contains_no_identifier_private_path_image_voxel_or_field_payload",
    "training_gpu_outer_test_and_rupture_label_access_are_zero",
}


def load_s0a_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise S0AProtocolError(f"S0a config does not exist: {source}") from exc
    except json.JSONDecodeError as exc:
        raise S0AProtocolError(f"Invalid S0a JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise S0AProtocolError("S0a config root must be an object.")
    return payload


def _require(mapping: Mapping[str, Any], keys: set[str], context: str) -> None:
    missing = sorted(keys - set(mapping))
    if missing:
        raise S0AProtocolError(f"{context} is missing: {', '.join(missing)}")


def validate_s0a_config(config: Mapping[str, Any]) -> list[str]:
    _require(
        config,
        {
            "schema_version",
            "protocol_id",
            "status",
            "purpose",
            "candidate_status",
            "audit_document",
            "public_sources_inspected_before_registration",
            "official_release",
            "expected_units",
            "required_checks",
            "gate_rule",
            "execution",
            "authorization",
        },
        "S0a config",
    )
    if config["schema_version"] != "1.0":
        raise S0AProtocolError("S0a schema must remain 1.0.")
    if config["protocol_id"] != "goal_oriented_hemodynamic_segmentation_s0a":
        raise S0AProtocolError("Unexpected S0a protocol id.")
    if config["purpose"] != "method_free_asset_linkage_and_runtime_integrity_only":
        raise S0AProtocolError("S0a cannot become a model or performance experiment.")

    release = config["official_release"]
    _require(
        release,
        {
            "version",
            "license",
            "total_bytes",
            "patients_archive",
            "controls_archive",
            "statistical_archive",
        },
        "official_release",
    )
    expected_archives = {
        "patients_archive": (
            "patients.rar",
            10735821611,
            "e783d656ba51c6813aae9fca68565c17",
        ),
        "controls_archive": (
            "controls.rar",
            4821489080,
            "8d18b970978a303ed89618066919a1b1",
        ),
        "statistical_archive": (
            "statistical results.rar",
            34376,
            "12b92693c79587fb6dbab4638bfad8bc",
        ),
    }
    if (
        release["version"] != 1
        or release["license"] != "CC_BY_4_0"
        or release["total_bytes"] != 15557345067
    ):
        raise S0AProtocolError("Official CMHA version, license, or size changed.")
    for key, (name, size, digest) in expected_archives.items():
        archive = release[key]
        if (
            archive.get("name") != name
            or archive.get("bytes") != size
            or archive.get("md5") != digest
        ):
            raise S0AProtocolError(f"Official CMHA {key} contract changed.")

    units = config["expected_units"]
    if units != {
        "patients": 99,
        "aneurysms": 105,
        "controls": 44,
        "multi_lesion_patients": 6,
        "split_unit": "patient",
        "lesions_are_independent_samples": False,
    }:
        raise S0AProtocolError("CMHA unit and patient-grouping contract changed.")
    if set(config["required_checks"]) != EXPECTED_CHECKS:
        raise S0AProtocolError("S0a must retain all eleven checks without substitution.")

    gate = config["gate_rule"]
    if gate != {
        "pass": "all_11_checks_true",
        "worst_case_rule": True,
        "threshold_relaxation_after_result": False,
        "same_version_dependency_or_mapping_repair_rerun": False,
        "pass_authorizes": "register_method_free_s0b_functional_non_equivalence_and_linearization_audit_only",
        "failure_action": "close_this_candidate_version_without_model_gpu_or_outer_test",
    }:
        raise S0AProtocolError("S0a gate or no-repair rule changed.")

    execution = config["execution"]
    if (
        execution.get("server") != "junjinyong"
        or execution.get("scheduler") != "PBS"
        or execution.get("resource") != "cpu_only_no_ngpus"
        or execution.get("login_node_heavy_work") is not False
        or execution.get("medical_assets_read_only") is not True
        or execution.get("code_read_only") is not True
        or execution.get("output_only_writable") is not True
        or execution.get("private_paths_in_config") is not False
        or execution.get("public_aggregate_only") is not True
    ):
        raise S0AProtocolError("S0a execution must remain CPU/PBS/read-only and aggregate-only.")

    authorization = config["authorization"]
    if set(authorization) != {
        "method_selected",
        "architecture_selected",
        "gpu_training",
        "outer_test",
        "submission_identity",
        "clinical_claim",
        "rupture_status_for_selection",
    } or any(value is not False for value in authorization.values()):
        raise S0AProtocolError("S0a cannot authorize method, GPU, test, or clinical claims.")

    return [
        "official CMHA release pinned",
        "patient-level unit contract pinned",
        "eleven all-or-none checks pinned",
        "CPU/PBS read-only execution pinned",
        "method/GPU/outer-test authorization closed",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    checks = validate_s0a_config(load_s0a_config(args.config))
    print(json.dumps({"status": "valid", "checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
