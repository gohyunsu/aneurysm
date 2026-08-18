"""Validation for the independent, release-aligned AneuG transient protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class Release730ProtocolError(RuntimeError):
    pass


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise Release730ProtocolError(label)


def validate_config(payload: dict[str, Any]) -> dict[str, Any]:
    _require(
        payload.get("schema_version") == "aurora.aneug_release_730_protocol.v1",
        "schema_version",
    )
    _require(
        payload.get("protocol_id") == "aneug_release_aligned_730_transient_wss_v1",
        "protocol_id",
    )
    source = payload["source"]
    _require(
        source["dataset_revision"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "dataset_revision",
    )
    _require(source["license"] == "cc-by-sa-4.0", "license")
    _require(
        source["proceedings_html_transient_cases"] == 200
        and source["official_paper_transient_cases"] == 730
        and source["official_paper_real_shape_counts_conflict"] == [109, 116],
        "source_conflicts",
    )
    v5 = source["processed_v5"]
    _require(
        (v5["bytes"], v5["sha256"])
        == (
            33_233_856_917,
            "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
        ),
        "v5_identity",
    )
    _require(
        (v5["remote_case_like_count"], v5["remote_release_intersection_count"], v5["remote_extra_count"])
        == (809, 730, 79),
        "remote_cohort",
    )
    cohort = payload["cohort"]
    _require(cohort["expected_case_count"] == 730, "cohort_count")
    _require(cohort["exclude_processed_only_extra_cases"] == 79, "extras")
    _require(cohort["patient_or_site_interpretation"] is False, "patient_claim")
    _require(cohort["embedded_registered_mesh_is_authoritative"] is True, "mesh_authority")
    verified = payload["verified_introai9_asset"]
    _require(
        (
            verified["finalize_job_id"],
            verified["finalize_exit_code"],
            verified["assembled_bytes"],
            verified["assembled_sha256"],
            verified["official_match"],
            verified["finalize_record_sha256"],
        )
        == (
            "116626.ECE-util1",
            0,
            33_233_856_917,
            "3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae",
            True,
            "cde7984f56e8da6b981ee05197bd5b90b32df561ec924ecd03c5f8d62d5b1331",
        ),
        "verified_asset",
    )
    _require(
        (
            verified["schema_job_id"],
            verified["schema_exit_code"],
            verified["schema_pass"],
            verified["registered_case_count"],
            verified["mesh_case_count"],
            verified["tensor_shape"],
            verified["mesh_case_order_exact"],
            verified["schema_record_sha256"],
        )
        == (
            "116627.ECE-util1",
            0,
            True,
            809,
            809,
            [80, 13_902, 9],
            True,
            "9e74cb3db68da83adcb0acb373ce47b01525258d1741cf43c3a718b5e25fa6ed",
        ),
        "verified_schema",
    )
    audit = payload["integrity_audit"]
    _require(audit["expected_timesteps"] == 80 and audit["expected_nodes"] == 13_902, "shape")
    _require(audit["field_values_used_for_split"] is False, "field_blind")
    normalization = payload["normalization_provenance"]
    _require(
        normalization["transient_archive_embeds_tensor_norm"] is False
        and normalization["official_builder_requires_external_steady_tensor_norm"] is True
        and normalization["v4_v5_overlap_identity_audit_status"] == "pending"
        and normalization["physical_wss_metrics_authorized_before_linkage"] is False
        and normalization["model_normalization_recomputed_from_new_train_only"] is True,
        "normalization_provenance",
    )
    _require(
        (normalization["steady_v4_bytes"], normalization["steady_v4_sha256"])
        == (
            9_632_510_050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
        ),
        "steady_norm_identity",
    )
    split = payload["split_design"]
    _require(
        (split["train_fraction"], split["validation_fraction"], split["test_fraction"])
        == (0.8, 0.1, 0.1),
        "fractions",
    )
    _require(split["singleton_target_counts"] == {"train": 584, "validation": 73, "test": 73}, "counts")
    _require(split["all_phases_follow_case"] is True, "phase_grouping")
    _require(split["validation_only_model_selection"] is True, "validation_selection")
    _require(split["test_locked_until_candidate_and_analysis_freeze"] is True, "test_lock")
    _require(split["field_or_model_result_used_to_choose_split"] is False, "outcome_blind")
    _require(split["grouping_inputs"] == ["mesh_data.ghd"], "grouping_inputs")
    evaluation = payload["evaluation"]
    _require(evaluation["independent_unit"] == "synthetic_geometry_case", "unit")
    _require(
        evaluation["primary_endpoint"]
        == "mean_over_cases_of_area_and_phase_weighted_complete_cycle_vector_wss_relative_l2",
        "primary_endpoint",
    )
    _require(evaluation["phase_level_pseudoreplication"] is False, "pseudoreplication")
    storage = payload["storage"]
    _require(storage["raw_per_case_cfd_downloaded"] is False, "raw_cfd")
    _require(storage["two_tb_release_downloaded"] is False, "two_tb")
    execution = payload["execution"]
    _require(execution["server"] == "introai9", "server")
    _require(execution["ngpus"] == 0, "gpu")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server")
    authorization = payload["authorization"]
    _require(authorization["download_v5"] is False, "duplicate_download")
    _require(authorization["use_verified_v5"] is True, "verified_v5")
    _require(authorization["freeze_private_split_after_audit"] is True, "split_freeze")
    _require(authorization["gpu_training_before_schema_and_split"] is False, "premature_gpu")
    _require(authorization["test_access_before_candidate_freeze"] is False, "premature_test")
    return payload


def load_config(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_config(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    arguments = parser.parse_args()
    load_config(arguments.config)


if __name__ == "__main__":
    main()
