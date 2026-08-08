"""Post-discovery, metadata-first boundary-asset audit for Aneumo V1b."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from .aneumo_range import archive_for_case, fetch_member, load_archive_index


class AneumoV1bBoundaryAuditError(RuntimeError):
    """Raised when the frozen V1b boundary-asset contract is violated."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_config(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != "aurora.aneumo_isbi_v1b_boundary_asset_audit.v1":
        raise AneumoV1bBoundaryAuditError("Unexpected V1b schema version.")
    if payload.get("status") != (
        "registered_after_archive1_case1_discovery_before_full_audit"
    ):
        raise AneumoV1bBoundaryAuditError("V1b discovery boundary changed.")
    discovery = payload.get("discovery_boundary", {})
    if (
        discovery.get("inspected_before_registration") is not True
        or discovery.get("scope")
        != "archive_1_central_directory_and_case_1_reference_flow_vtp_headers"
        or discovery.get("not_prospective_evidence") is not True
    ):
        raise AneumoV1bBoundaryAuditError("V1b must disclose the pre-registration discovery.")
    access = payload.get("access", {})
    if (
        access.get("central_directory_splits") != ["train", "validation", "test"]
        or access.get("payload_member_splits") != ["train"]
        or access.get("payload_contains_field_bytes") is not True
        or access.get("field_arrays_decoded") is not False
        or access.get("validation_payload_read") is not False
        or access.get("test_payload_read") is not False
        or access.get("model_or_checkpoint_use") is not False
        or access.get("training") is not False
    ):
        raise AneumoV1bBoundaryAuditError("V1b access boundary changed.")
    source = payload.get("source", {})
    if source != {
        "dataset": "Aneumo",
        "hf_repo": "SAIS-Life-Science/Aneumo",
        "hf_repo_commit": "f801adee816c18d3e18b23e6fcb147fe4c264209",
        "license": "CC-BY-NC-ND-4.0",
        "staging_config": "configs/aneumo_g2_pilot_v1.json",
        "staging_config_sha256": "f2b027c5f14107531ac1ae33eafab76513bcbdf49ad908c9a35641ae80181b7d",
        "v1_result": "results/aneumo_isbi_v1_20260808.json",
        "v1_result_sha256": "f67970c4d8028bf869ae793a776ed86d32b9cc477a9ba414e54bf9c8fab6a9b1",
        "v1a_result": "results/aneumo_isbi_v1_attribution_20260808.json",
        "v1a_result_sha256": "1a7b3e768e97b560da54d52cfe343c019d392e5af2fb3bbf518705f3728076a2",
    }:
        raise AneumoV1bBoundaryAuditError("V1b pinned source changed.")
    expected = payload.get("expected_asset", {})
    if (
        expected.get("archives") != 20
        or expected.get("cases") != 64
        or expected.get("base_families") != 32
        or expected.get("train_base_families") != 20
        or expected.get("validation_base_families") != 6
        or expected.get("test_base_families") != 6
        or float(expected.get("reference_mass_flow_kg_s", -1.0)) != 0.0025
        or expected.get("required_patches") != ["inlet", "outlet", "wall"]
        or expected.get("required_case_members")
        != [
            "Mesh/{case}.msh",
            "Stl/{case}.stl",
            "VTK/m=0.0025/internal.vtu",
            "VTK/m=0.0025/inlet.vtp",
            "VTK/m=0.0025/outlet.vtp",
            "VTK/m=0.0025/wall.vtp",
        ]
        or expected.get("required_vtp_arrays")
        != ["Points", "TimeValue", "U", "p", "connectivity", "offsets"]
    ):
        raise AneumoV1bBoundaryAuditError("V1b expected asset changed.")
    representative = payload.get("representative_payload_audit", {})
    if (
        representative.get("selection")
        != "lowest_case_id_in_each_train_base_family"
        or representative.get("cases") != 20
        or representative.get("members_per_case") != 3
        or representative.get("members") != 60
        or float(representative.get("flow_kg_s", -1.0)) != 0.0025
        or representative.get("crc32_verified") is not True
        or representative.get("require_positive_points_and_polys") is not True
        or representative.get("do_not_decode_U_or_p_values") is not True
    ):
        raise AneumoV1bBoundaryAuditError("V1b representative payload audit changed.")
    gate = payload.get("gate", {})
    expected_checks = [
        "pinned_source_and_license",
        "all_twenty_zip64_central_directories_range_readable",
        "all_sixty_four_cases_have_mesh_stl_volume_and_three_boundary_members",
        "one_train_case_per_family_has_three_crc_verified_vtp_payloads",
        "all_representative_vtp_patch_labels_match",
        "all_representative_vtp_have_poly_connectivity_and_required_arrays",
        "no_validation_or_test_payload_read",
        "v1_failure_and_v1a_no_reentry_decision_preserved",
    ]
    if (
        gate.get("local_repair_allowed") is not False
        or gate.get("pass_authorizes")
        != "register_a_new_boundary_aware_cache_staging_audit_only"
        or gate.get("checks") != expected_checks
        or set(gate.get("pass_does_not_authorize", []))
        != {
            "relabel_v1",
            "reuse_or_tune_v1_backbones",
            "model_training",
            "v2_or_test_field_access",
            "method_novelty",
            "isbi_submission",
        }
    ):
        raise AneumoV1bBoundaryAuditError("V1b cannot authorize a model or repair loop.")
    return dict(payload)


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def parse_vtp_contract(payload: bytes, expected_patch: str) -> dict[str, Any]:
    text = payload.decode("utf-8", errors="strict")
    if not re.search(r"<VTKFile\s+type=['\"]PolyData['\"]", text):
        raise AneumoV1bBoundaryAuditError("Representative boundary member is not VTP PolyData.")
    patch_match = re.search(r"patch=['\"]([^'\"]+)['\"]", text)
    piece_match = re.search(
        r"<Piece\s+NumberOfPoints=['\"](\d+)['\"]\s+NumberOfPolys=['\"](\d+)['\"]",
        text,
    )
    if patch_match is None or patch_match.group(1) != expected_patch:
        raise AneumoV1bBoundaryAuditError("VTP patch identity mismatch.")
    if piece_match is None:
        raise AneumoV1bBoundaryAuditError("VTP point/polygon counts are missing.")
    points, polys = (int(piece_match.group(1)), int(piece_match.group(2)))
    if points <= 0 or polys <= 0:
        raise AneumoV1bBoundaryAuditError("VTP has no positive point/polygon support.")
    arrays = sorted(set(re.findall(r"Name=['\"]([^'\"]+)['\"]", text)))
    required = {"Points", "TimeValue", "U", "p", "connectivity", "offsets"}
    if not required.issubset(arrays):
        raise AneumoV1bBoundaryAuditError("VTP required arrays are missing.")
    return {"patch": expected_patch, "points": points, "polys": polys, "arrays": arrays}


def _selected_cases(staging: Mapping[str, Any]) -> list[tuple[int, int, str]]:
    selection = staging["asset_selection"]
    mapping = {
        int(family): [int(case) for case in cases]
        for family, cases in selection["cases_by_base_family"].items()
    }
    split = staging["split"]
    split_by_family = {
        int(family): name
        for name, key in (
            ("train", "train_base_families"),
            ("validation", "validation_base_families"),
            ("test", "test_base_families"),
        )
        for family in split[key]
    }
    return [
        (family, case, split_by_family[family])
        for family in sorted(mapping)
        for case in sorted(mapping[family])
    ]


def run_audit(config: Mapping[str, Any], *, root: Path, output: Path, git_commit: str) -> dict[str, Any]:
    source = config["source"]
    for path_key, hash_key in (
        ("staging_config", "staging_config_sha256"),
        ("v1_result", "v1_result_sha256"),
        ("v1a_result", "v1a_result_sha256"),
    ):
        if _sha256(root / source[path_key]) != source[hash_key]:
            raise AneumoV1bBoundaryAuditError(f"V1b dependency mismatch: {path_key}")
    v1 = json.loads((root / source["v1_result"]).read_text(encoding="utf-8"))
    v1a = json.loads((root / source["v1a_result"]).read_text(encoding="utf-8"))
    if (
        v1["gate"]["all_checks_passed"] is not False
        or v1["gate"]["decision"]
        != "stop_the_current_3d_backbone_branch_without_local_hyperparameter_repair"
        or v1a["authorization"]["may_relabel_v1"] is not False
        or v1a["authorization"]["may_open_v2_or_test"] is not False
    ):
        raise AneumoV1bBoundaryAuditError("V1b cannot reopen V1 or V2.")
    staging = json.loads((root / source["staging_config"]).read_text(encoding="utf-8"))
    cases = _selected_cases(staging)
    archives = sorted({archive_for_case(case) for _, case, _ in cases}, key=lambda x: int(x[:-4]))
    base_url = (
        f"https://huggingface.co/datasets/{source['hf_repo']}/resolve/"
        f"{source['hf_repo_commit']}"
    )
    indexes: dict[str, Mapping[str, Any]] = {}
    archive_rows = []
    for archive in archives:
        index, metadata = load_archive_index(f"{base_url}/{archive}")
        indexes[archive] = index
        archive_rows.append(
            {
                "archive": archive,
                "members": len(index),
                "content_length": int(metadata["content_length"]),
            }
        )
    required_rows = []
    for family, case, split in cases:
        archive = archive_for_case(case)
        index = indexes[archive]
        required = [
            f"{case}/Mesh/{case}.msh",
            f"{case}/Stl/{case}.stl",
            f"{case}/VTK/m=0.0025/internal.vtu",
            f"{case}/VTK/m=0.0025/inlet.vtp",
            f"{case}/VTK/m=0.0025/outlet.vtp",
            f"{case}/VTK/m=0.0025/wall.vtp",
        ]
        for name in required:
            if name not in index or int(index[name].uncompressed_size) <= 0:
                raise AneumoV1bBoundaryAuditError(f"Required boundary member missing: {name}")
            required_rows.append(
                {
                    "family": family,
                    "case": case,
                    "split": split,
                    "archive": archive,
                    "member": name,
                    "crc32": f"{index[name].crc32:08x}",
                    "uncompressed_size": int(index[name].uncompressed_size),
                }
            )
    train_by_family: dict[int, int] = {}
    for family, case, split in cases:
        if split == "train":
            train_by_family[family] = min(case, train_by_family.get(family, case))
    payload_rows = []
    for family, case in sorted(train_by_family.items()):
        archive = archive_for_case(case)
        url = f"{base_url}/{archive}"
        index = indexes[archive]
        for patch in config["expected_asset"]["required_patches"]:
            name = f"{case}/VTK/m=0.0025/{patch}.vtp"
            raw = fetch_member(url, index[name])
            contract = parse_vtp_contract(raw, patch)
            payload_rows.append(
                {
                    "family": family,
                    "case": case,
                    "split": "train",
                    "member": name,
                    "crc32": f"{index[name].crc32:08x}",
                    **contract,
                }
            )
    if len(archives) != 20 or len(cases) != 64 or len(payload_rows) != 60:
        raise AneumoV1bBoundaryAuditError("V1b count contract changed.")
    canonical = json.dumps(required_rows + payload_rows, sort_keys=True).encode("utf-8")
    checks = {
        "pinned_source_and_license": source["license"] == "CC-BY-NC-ND-4.0",
        "all_twenty_zip64_central_directories_range_readable": len(archive_rows) == 20,
        "all_sixty_four_cases_have_mesh_stl_volume_and_three_boundary_members": len(required_rows) == 384,
        "one_train_case_per_family_has_three_crc_verified_vtp_payloads": len(payload_rows) == 60,
        "all_representative_vtp_patch_labels_match": all(row["patch"] in {"inlet", "outlet", "wall"} for row in payload_rows),
        "all_representative_vtp_have_poly_connectivity_and_required_arrays": all(row["points"] > 0 and row["polys"] > 0 for row in payload_rows),
        "no_validation_or_test_payload_read": all(row["split"] == "train" for row in payload_rows),
        "v1_failure_and_v1a_no_reentry_decision_preserved": True,
    }
    result = {
        "schema_version": "aurora.aneumo_isbi_v1b_boundary_asset_audit.result.v1",
        "experiment_id": config["experiment_id"],
        "git_commit": git_commit,
        "config_sha256": config["_config_sha256"],
        "source": source,
        "discovery_boundary": config["discovery_boundary"],
        "counts": {
            "archives": len(archive_rows),
            "cases": len(cases),
            "required_members": len(required_rows),
            "representative_train_payload_members": len(payload_rows),
        },
        "representative_vtp": {
            "point_count_min": min(row["points"] for row in payload_rows),
            "point_count_max": max(row["points"] for row in payload_rows),
            "polygon_count_min": min(row["polys"] for row in payload_rows),
            "polygon_count_max": max(row["polys"] for row in payload_rows),
            "required_arrays": config["expected_asset"]["required_vtp_arrays"],
            "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
            "field_arrays_decoded": False,
        },
        "field_access": {
            "central_directory_splits": ["train", "validation", "test"],
            "payload_member_splits": ["train"],
            "validation_payload_read": False,
            "test_payload_read": False,
            "field_arrays_decoded": False,
        },
        "gate": {
            "checks": checks,
            "passed_checks": sum(bool(value) for value in checks.values()),
            "total_checks": len(checks),
            "all_checks_passed": all(checks.values()),
            "pass_authorizes": config["gate"]["pass_authorizes"],
            "pass_does_not_authorize": config["gate"]["pass_does_not_authorize"],
            "decision": (
                "register_boundary_aware_cache_staging_audit_only"
                if all(checks.values())
                else config["gate"]["failure_action"]
            ),
        },
        "interpretation": config["interpretation"],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "status.json").write_text(
        json.dumps(
            {"exit_status": 0, "state": "complete", "test_payload_read": False},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--git-commit", required=True)
    args = parser.parse_args(argv)
    config_bytes = args.config.read_bytes()
    config = load_config(args.config)
    config["_config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
    try:
        result = run_audit(
            config,
            root=args.root,
            output=args.output,
            git_commit=args.git_commit,
        )
    except Exception:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "status.json").write_text(
            json.dumps(
                {"exit_status": 1, "state": "failed", "test_payload_read": False},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        raise
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
