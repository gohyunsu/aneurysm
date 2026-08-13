"""One-shot source feasibility audit for the AneuG reference-floor direction.

The audit reads repository metadata and an exact public tar archive directory.
It never downloads AneuG field/mesh payloads and never extracts Challenge
members.  It is source evidence, not a model or scientific endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


class G0Error(RuntimeError):
    """Base error for a fail-closed G0 audit."""


class G0ContractError(G0Error):
    """The prospective contract is internally inconsistent."""


class G0ExecutionIncomplete(G0Error):
    """The exact public source could not be audited in one attempt."""


def load_contract(path: Path) -> dict[str, Any]:
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise G0ContractError("contract_unreadable") from exc
    if contract.get("schema_version") != "aurora.aneug_reference_floor_g0.v1":
        raise G0ContractError("invalid_schema")
    if contract.get("status") != "prospectively_registered_source_feasibility_audit":
        raise G0ContractError("not_preregistered")
    candidate = contract.get("candidate", {})
    if candidate.get("score") != 31.0 or candidate.get("admission_threshold") != 32.0:
        raise G0ContractError("candidate_score_boundary_changed")
    if sum(candidate.get("axis_scores", [])) != candidate.get("score"):
        raise G0ContractError("candidate_axis_sum_changed")
    for key in (
        "method_selected",
        "architecture_selected",
        "gpu_training_authorized",
        "outer_test_authorized",
        "submission_identity_active",
    ):
        if candidate.get(key) is not False:
            raise G0ContractError(f"candidate_{key}_changed")
    gate = contract.get("gate", {})
    if gate.get("same_contract_repair_or_rerun_allowed") is not False:
        raise G0ContractError("rerun_boundary_changed")
    execution = contract.get("execution", {})
    if (
        execution.get("server") != "introai9"
        or execution.get("excluded_server") != "junjinyong"
        or execution.get("scheduler") != "pbs"
        or execution.get("queue") != "coss_agpu"
        or execution.get("ncpus") != 4
        or execution.get("memory_gb") != 8
        or execution.get("ngpus") != 0
        or execution.get("walltime") != "01:00:00"
        or execution.get("maximum_submissions_for_exact_contract") != 1
        or execution.get("login_node_gpu_command_allowed") is not False
    ):
        raise G0ContractError("execution_boundary_changed")
    audit = contract.get("audit", {})
    if (
        audit.get("aneug_field_payload_downloaded") is not False
        or audit.get("aneug_mesh_payload_downloaded") is not False
        or audit.get("challenge_archive_members_extracted_or_field_values_read") is not False
        or audit.get("aneux_payload_downloaded") is not False
        or audit.get("maximum_figshare_download_bytes") != 425_372_824
        or audit.get("maximum_hugging_face_tree_pages") != 100
        or audit.get("maximum_challenge_tar_members") != 20_000
        or audit.get("timeout_seconds_per_request") != 900
        or audit.get("retry_count") != 0
    ):
        raise G0ContractError("payload_or_retry_boundary_changed")
    return contract


def _request(url: str, timeout: int) -> Any:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AURORA-ISBI2027-reference-floor-G0/1.0"},
    )
    try:
        return urllib.request.urlopen(request, timeout=timeout)
    except Exception as exc:  # network errors are an execution state, not science
        raise G0ExecutionIncomplete("public_source_request_failed") from exc


def _get_json(url: str, timeout: int) -> tuple[Any, dict[str, str]]:
    with _request(url, timeout) as response:
        try:
            payload = json.load(response)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise G0ExecutionIncomplete("public_source_json_invalid") from exc
        return payload, dict(response.headers.items())


def _next_link(headers: dict[str, str]) -> str | None:
    link = headers.get("Link") or headers.get("link")
    if not link:
        return None
    for part in link.split(","):
        match = re.match(r'\s*<([^>]+)>;\s*rel="?next"?', part)
        if match:
            url = match.group(1)
            if not url.startswith("https://huggingface.co/api/datasets/"):
                raise G0ExecutionIncomplete("unsafe_pagination_url")
            return url
    return None


def fetch_hf_tree(repo: str, revision: str, timeout: int, max_pages: int) -> list[dict[str, Any]]:
    url = (
        f"https://huggingface.co/api/datasets/{repo}/tree/{revision}/"
        "transient_data?recursive=true&expand=false&limit=1000"
    )
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for _ in range(max_pages):
        if url in seen:
            raise G0ExecutionIncomplete("pagination_cycle")
        seen.add(url)
        page, headers = _get_json(url, timeout)
        if not isinstance(page, list):
            raise G0ExecutionIncomplete("hf_tree_page_not_list")
        entries.extend(item for item in page if isinstance(item, dict))
        next_url = _next_link(headers)
        if next_url is None:
            return entries
        url = next_url
    raise G0ExecutionIncomplete("hf_tree_page_budget_exhausted")


def analyze_hf_tree(entries: list[dict[str, Any]]) -> dict[str, Any]:
    paths = sorted(
        str(item.get("path"))
        for item in entries
        if isinstance(item.get("path"), str)
    )
    wall_cases = {
        match.group(1)
        for path in paths
        if (match := re.fullmatch(r"transient_data/([^/]+)/wall_data\.pt", path))
    }
    remeshed_cases = {
        match.group(1)
        for path in paths
        if (match := re.fullmatch(r"transient_data/([^/]+)/shape_remeshed\.obj", path))
    }
    shape_cases = {
        match.group(1)
        for path in paths
        if (match := re.fullmatch(r"transient_data/([^/]+)/shape\.obj", path))
    }
    lineage_tokens = ("lineage", "parent", "ancestry", "latent", "source_geometry", "seed_map")
    lineage_paths = [path for path in paths if any(token in path.lower() for token in lineage_tokens)]
    return {
        "tree_entries": len(paths),
        "wall_case_count": len(wall_cases),
        "shape_case_count": len(shape_cases),
        "remeshed_case_count": len(remeshed_cases),
        "wall_and_remeshed_case_count": len(wall_cases & remeshed_cases),
        "wall_shape_and_remeshed_case_count": len(wall_cases & shape_cases & remeshed_cases),
        "explicit_lineage_path_count": len(lineage_paths),
        "explicit_lineage_paths": lineage_paths[:20],
        "lineage_path_scan_is_not_proof_of_independence": True,
    }


def download_exact(url: str, destination: Path, expected_bytes: int, expected_md5: str, timeout: int) -> None:
    md5 = hashlib.md5(usedforsecurity=False)
    total = 0
    with _request(url, timeout) as response, destination.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > expected_bytes:
                raise G0ExecutionIncomplete("archive_oversized")
            md5.update(chunk)
            handle.write(chunk)
    if total != expected_bytes:
        raise G0ExecutionIncomplete("archive_size_mismatch")
    if md5.hexdigest() != expected_md5:
        raise G0ExecutionIncomplete("archive_md5_mismatch")


def inspect_tar_members(path: Path, *, maximum_members: int = 20_000) -> dict[str, Any]:
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            members = archive.getmembers()
    except (tarfile.TarError, OSError) as exc:
        raise G0ExecutionIncomplete("challenge_tar_invalid") from exc
    if len(members) > maximum_members:
        raise G0ExecutionIncomplete("challenge_tar_member_budget_exhausted")
    unsafe = [member.name for member in members if member.name.startswith("/") or ".." in Path(member.name).parts]
    if unsafe:
        raise G0ExecutionIncomplete("challenge_tar_unsafe_member")
    files = [member for member in members if member.isfile()]
    suffixes = Counter(Path(member.name).suffix.lower() or "<none>" for member in files)
    top_levels = sorted({Path(member.name).parts[0] for member in files if Path(member.name).parts})
    file_inventory = [
        {"name": member.name, "size": int(member.size)}
        for member in files
    ]
    inventory_bytes = json.dumps(
        file_inventory, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "member_count": len(members),
        "file_member_count": len(files),
        "suffix_counts": dict(sorted(suffixes.items())),
        "top_level_entry_count": len(top_levels),
        "top_level_entries": top_levels[:100],
        "file_inventory": file_inventory,
        "file_inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "members_extracted": False,
        "field_values_read": False,
    }


def run(contract: dict[str, Any]) -> dict[str, Any]:
    sources = contract["sources"]
    audit = contract["audit"]
    timeout = int(audit["timeout_seconds_per_request"])

    aneug = sources["aneug_flow"]
    repo = aneug["dataset_repository"]
    revision = aneug["dataset_revision"]
    code_repo = aneug["official_code_repository"]
    code_commit = aneug["official_code_commit"]
    github_commit, _ = _get_json(
        f"https://api.github.com/repos/{code_repo}/commits/{code_commit}", timeout
    )
    if not isinstance(github_commit, dict) or github_commit.get("sha") != code_commit:
        raise G0ExecutionIncomplete("aneug_code_commit_identity_changed")
    hf_info, _ = _get_json(f"https://huggingface.co/api/datasets/{repo}/revision/{revision}", timeout)
    if not isinstance(hf_info, dict):
        raise G0ExecutionIncomplete("hf_info_not_object")
    card = hf_info.get("cardData") or {}
    if (
        hf_info.get("sha") != revision
        or hf_info.get("private") is not False
        or hf_info.get("gated") not in (False, None)
        or str(card.get("license", "")).lower() != aneug["dataset_license"]
    ):
        raise G0ExecutionIncomplete("hf_identity_or_access_changed")
    tree = fetch_hf_tree(repo, revision, timeout, int(audit["maximum_hugging_face_tree_pages"]))
    tree_summary = analyze_hf_tree(tree)
    if tree_summary["wall_case_count"] != aneug["reported_transient_cases"]:
        raise G0ExecutionIncomplete("aneug_transient_wall_case_count_changed")

    challenge = sources["aneurysm_cfd_challenge_2015"]
    figshare, _ = _get_json(
        f"https://api.figshare.com/v2/articles/{challenge['figshare_record_id']}/versions/{challenge['figshare_version']}",
        timeout,
    )
    if not isinstance(figshare, dict):
        raise G0ExecutionIncomplete("figshare_metadata_not_object")
    files = {int(item["id"]): item for item in figshare.get("files", [])}
    file_info = files.get(int(challenge["wss_archive_file_id"]))
    if (
        figshare.get("doi") != challenge["doi"]
        or str((figshare.get("license") or {}).get("name")) != challenge["license"]
        or file_info is None
        or file_info.get("name") != challenge["wss_archive_name"]
        or int(file_info.get("size", -1)) != challenge["wss_archive_bytes"]
        or str(file_info.get("computed_md5")) != challenge["wss_archive_md5"]
    ):
        raise G0ExecutionIncomplete("figshare_identity_changed")
    download_url = str(file_info.get("download_url", ""))
    if not download_url.startswith("https://"):
        raise G0ExecutionIncomplete("figshare_download_url_invalid")

    aneux = sources["aneux"]
    zenodo, _ = _get_json(f"https://zenodo.org/api/records/{aneux['zenodo_record_id']}", timeout)
    if not isinstance(zenodo, dict):
        raise G0ExecutionIncomplete("aneux_metadata_not_object")
    metadata = zenodo.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise G0ExecutionIncomplete("aneux_record_metadata_not_object")
    license_id = str((metadata.get("license") or {}).get("id", "")).lower()
    searchable_metadata = re.sub(
        r"<[^>]+>",
        " ",
        " ".join(str(metadata.get(key, "")) for key in ("title", "description", "notes")),
    )
    if (
        int(zenodo.get("id", -1)) != aneux["zenodo_record_id"]
        or int(zenodo.get("revision", -1)) != aneux["record_revision"]
        or str(metadata.get("version")) != aneux["version"]
        or license_id != "cc-by-nc-4.0"
        or str(aneux["aneurysm_domes"]) not in searchable_metadata
        or str(aneux["vessel_trees"]) not in searchable_metadata
    ):
        raise G0ExecutionIncomplete("aneux_identity_changed")

    with tempfile.TemporaryDirectory(prefix="aurora-reference-floor-g0-") as tmp:
        archive_path = Path(tmp) / challenge["wss_archive_name"]
        download_exact(
            download_url,
            archive_path,
            int(challenge["wss_archive_bytes"]),
            challenge["wss_archive_md5"],
            timeout,
        )
        challenge_summary = inspect_tar_members(
            archive_path,
            maximum_members=int(audit["maximum_challenge_tar_members"]),
        )
    if challenge_summary["file_member_count"] == 0:
        raise G0ExecutionIncomplete("challenge_archive_has_no_files")

    return {
        "schema_version": "aurora.aneug_reference_floor_g0.result.v1",
        "protocol_id": contract["protocol_id"],
        "status": "source_feasibility_complete",
        "scientific_gate_evaluated": False,
        "candidate_score_before_human_rescoring": contract["candidate"]["score"],
        "aneug": {
            "revision": revision,
            "official_code_commit": code_commit,
            "public": True,
            "ungated": True,
            "license": aneug["dataset_license"],
            **tree_summary,
            "field_payload_downloaded": False,
            "mesh_payload_downloaded": False,
        },
        "challenge_2015": {
            "record_id": challenge["figshare_record_id"],
            "version": challenge["figshare_version"],
            "archive_bytes": challenge["wss_archive_bytes"],
            "archive_md5": challenge["wss_archive_md5"],
            "independent_anatomies": challenge["independent_anatomies"],
            **challenge_summary,
        },
        "aneux": {
            "record_id": aneux["zenodo_record_id"],
            "version": aneux["version"],
            "license": aneux["license"],
            "geometry_only_role": True,
            "payload_downloaded": False,
        },
        "authority": {
            "human_rescoring_required": True,
            "method_selected": False,
            "architecture_selected": False,
            "gpu_training_authorized": False,
            "outer_test_authorized": False,
            "paper_contribution_active": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    contract = load_contract(args.config)
    if args.validate_only:
        print("AneuG reference-floor G0 contract valid · source-only · GPU 0")
        return 0
    if args.output is None:
        raise SystemExit("--output is required unless --validate-only is used")
    try:
        result = run(contract)
    except G0ExecutionIncomplete as exc:
        result = {
            "schema_version": "aurora.aneug_reference_floor_g0.result.v1",
            "protocol_id": contract["protocol_id"],
            "status": "execution_incomplete_no_source_feasibility_verdict",
            "scientific_gate_evaluated": False,
            "reason": str(exc),
            "same_contract_repair_or_rerun_allowed": False,
            "method_selected": False,
            "gpu_training_authorized": False,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 2
    except Exception as exc:  # preserve a terminal one-shot status for unanticipated runtime faults
        result = {
            "schema_version": "aurora.aneug_reference_floor_g0.result.v1",
            "protocol_id": contract["protocol_id"],
            "status": "execution_incomplete_no_source_feasibility_verdict",
            "scientific_gate_evaluated": False,
            "reason": f"unexpected_execution_error_{type(exc).__name__}",
            "same_contract_repair_or_rerun_allowed": False,
            "method_selected": False,
            "gpu_training_authorized": False,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
