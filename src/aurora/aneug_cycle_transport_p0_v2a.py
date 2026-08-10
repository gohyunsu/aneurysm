"""Bounded AneuG-Flow transport preflight for prospective P0-v2 re-entry.

This module reads exactly two HEAD responses and four one-MiB byte ranges.  It
does not download either processed object, deserialize PyTorch data, inspect a
case identifier, select a method, or authorize GPU work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


class AneuGCycleTransportV2AError(RuntimeError):
    """Raised when the prospective v2a contract or observed transport fails."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise AneuGCycleTransportV2AError(code)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_config_payload(payload: Mapping[str, Any]) -> None:
    _require(
        payload.get("schema_version") == "aurora.aneug_cycle_transport_p0_v2a.v1",
        "invalid_schema",
    )
    _require(payload.get("protocol_id") == "aneug_cycle_transport_p0_v2a", "invalid_protocol_id")
    _require(
        payload.get("status") == "preregistered_before_introai9_v2a_execution",
        "not_prospective",
    )

    candidate = payload["candidate"]
    _require(float(candidate["source_score"]) == 33.0, "source_score_changed")
    _require(float(candidate["automatic_selection_threshold"]) == 32.0, "threshold_changed")
    _require(abs(sum(map(float, candidate["axis_scores"])) - 33.0) < 1e-12, "axis_sum_changed")
    _require(int(candidate["active_source_shortlist_count"]) == 1, "shortlist_boundary_changed")
    for field in (
        "primary_problem_selected",
        "method_selected",
        "architecture_selected",
        "gpu_training_authorized",
        "outer_test_authorized",
        "submission_identity_active",
    ):
        _require(candidate[field] is False, f"candidate_boundary_changed_{field}")

    reentry = payload["prospective_reentry"]
    _require(reentry["historical_v1_same_contract_rerun_allowed"] is False, "v1_reopened")
    _require(reentry["historical_v1_failure_relabelled"] is False, "v1_relabelled")
    _require(int(reentry["repair_round_index"]) == 1, "repair_round_changed")
    _require(int(reentry["maximum_transport_repair_rounds"]) == 1, "repair_budget_changed")
    _require(
        reentry["only_changed_layer"]
        == "transport_preflight_before_any_full_object_or_reader_access",
        "repair_scope_changed",
    )

    source = payload["source"]
    _require(
        source["dataset_repository_commit"]
        == "9dd418083899deddd93a67f9a6fca7a14304fa36",
        "dataset_commit_changed",
    )
    _require(source["license"] == "cc-by-sa-4.0", "license_changed")
    _require(
        source["official_code_commit"]
        == "4a090a0f12538deef6fcea88b81afe78ce38152e",
        "code_commit_changed",
    )
    expected = {
        "steady": (
            9632510050,
            "0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f",
            "3325d68e3fc1a6b20abf80213bbd71c32baf52da1af5e9cd99e405529bb86a00",
            (0, 1048575, "c427dc1394bf6c0c14e86a3e52ff004066660d9bfb0a16333a8c35500793b845"),
            (9631461474, 9632510049, "416f4c703a761153fbf966a77129a97c2d1904c68f47bf2584f4e558263e5b1b"),
        ),
        "transient": (
            23744862051,
            "141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9",
            "3779ed5392d38eefc55e43fb9db42e108a15f0f8bdce0899b699f14aec8393f4",
            (0, 1048575, "ee53973d872f42c717e5ca1020c9a8ef71049aaa98862b38c508aeebf9c82a87"),
            (23743813475, 23744862050, "2a2d95cf0b4b01df06eba293c8ee82081ec1875fb00cfec685656864f43522ce"),
        ),
    }
    objects = source["objects"]
    _require(set(objects) == set(expected), "object_set_changed")
    for role, (size, linked_etag, xet_hash, prefix, suffix) in expected.items():
        item = objects[role]
        _require(int(item["bytes"]) == size, f"{role}_size_changed")
        _require(item["sha256_linked_etag"] == linked_etag, f"{role}_etag_changed")
        _require(item["xet_hash"] == xet_hash, f"{role}_xet_hash_changed")
        _require(str(item["url"]).startswith("https://huggingface.co/datasets/whding123/AneuG-Flow/resolve/"), f"{role}_url_changed")
        ranges = item["ranges"]
        _require([entry["id"] for entry in ranges] == ["prefix", "suffix"], f"{role}_range_ids_changed")
        for entry, frozen in zip(ranges, (prefix, suffix)):
            start, end, digest = frozen
            _require((int(entry["start"]), int(entry["end"]), int(entry["bytes"]), entry["sha256"]) == (start, end, 1048576, digest), f"{role}_{entry['id']}_range_changed")

    transport = payload["transport"]
    _require(
        (
            int(transport["head_operations"]),
            int(transport["range_operations"]),
            int(transport["range_bytes_per_operation"]),
            int(transport["maximum_total_payload_bytes"]),
            int(transport["retry_count"]),
            int(transport["connect_timeout_seconds"]),
            int(transport["head_max_time_seconds"]),
            int(transport["range_max_time_seconds"]),
            int(transport["process_timeout_slack_seconds"]),
            int(transport["maximum_curl_file_size_bytes"]),
        )
        == (2, 4, 1048576, 4194304, 0, 10, 45, 90, 15, 2097152),
        "transport_budget_changed",
    )
    _require(transport["resume_allowed"] is False, "resume_enabled")
    _require(transport["full_object_download_allowed"] is False, "full_download_enabled")
    _require(transport["torch_or_pickle_reader_allowed"] is False, "reader_enabled")

    execution = payload["execution"]
    _require(execution["server"] == "introai9", "server_changed")
    _require(execution["scheduler"] == "pbs", "scheduler_changed")
    _require(execution["gpu_requested"] is False, "gpu_enabled")
    _require(execution["login_node_gpu_command"] is False, "login_gpu_enabled")
    _require(execution["excluded_server"] == "junjinyong", "excluded_server_changed")


def load_config(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    validate_config_payload(payload)
    payload["_config_sha256"] = _sha256(source.read_bytes())
    return payload


def _header_values(raw: bytes) -> tuple[list[int], dict[str, list[str]]]:
    text = raw.decode("iso-8859-1")
    statuses: list[int] = []
    values: dict[str, list[str]] = {}
    for line in text.replace("\r\n", "\n").split("\n"):
        status = re.match(r"^HTTP/\S+\s+(\d{3})(?:\s|$)", line, re.IGNORECASE)
        if status:
            statuses.append(int(status.group(1)))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values.setdefault(key.strip().lower(), []).append(value.strip())
    return statuses, values


class Transport(Protocol):
    def head(self, url: str) -> bytes: ...

    def byte_range(self, url: str, start: int, end: int) -> tuple[bytes, bytes]: ...


class CurlTransport:
    def __init__(self, config: Mapping[str, Any], executable: str = "curl"):
        self.config = config
        self.executable = executable

    def head(self, url: str) -> bytes:
        transport = self.config["transport"]
        command = [
            self.executable,
            "--silent",
            "--show-error",
            "--fail",
            "--head",
            "--location",
            "--retry",
            str(transport["retry_count"]),
            "--connect-timeout",
            str(transport["connect_timeout_seconds"]),
            "--max-time",
            str(transport["head_max_time_seconds"]),
            url,
        ]
        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=int(transport["head_max_time_seconds"])
                + int(transport["process_timeout_slack_seconds"]),
            )
        except (subprocess.SubprocessError, OSError) as exc:
            raise AneuGCycleTransportV2AError(f"head_transport_failed_{type(exc).__name__}") from exc
        return result.stdout

    def byte_range(self, url: str, start: int, end: int) -> tuple[bytes, bytes]:
        transport = self.config["transport"]
        with tempfile.TemporaryDirectory(prefix="aurora-aneug-v2a-") as temporary:
            root = Path(temporary)
            payload_path = root / "range.bin"
            header_path = root / "headers.txt"
            command = [
                self.executable,
                "--silent",
                "--show-error",
                "--fail",
                "--location",
                "--retry",
                str(transport["retry_count"]),
                "--connect-timeout",
                str(transport["connect_timeout_seconds"]),
                "--max-time",
                str(transport["range_max_time_seconds"]),
                "--max-filesize",
                str(transport["maximum_curl_file_size_bytes"]),
                "--range",
                f"{start}-{end}",
                "--dump-header",
                str(header_path),
                "--output",
                str(payload_path),
                url,
            ]
            try:
                subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=int(transport["range_max_time_seconds"])
                    + int(transport["process_timeout_slack_seconds"]),
                )
            except (subprocess.SubprocessError, OSError) as exc:
                raise AneuGCycleTransportV2AError(f"range_transport_failed_{type(exc).__name__}") from exc
            return header_path.read_bytes(), payload_path.read_bytes()


def audit(config: Mapping[str, Any], client: Transport) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    total_payload_bytes = 0
    for role in ("steady", "transient"):
        item = config["source"]["objects"][role]
        head_raw = client.head(str(item["url"]))
        statuses, headers = _header_values(head_raw)
        _require(statuses and statuses[-1] == 200, f"{role}_head_final_status_not_200")
        _require(302 in statuses, f"{role}_head_redirect_missing")
        _require(config["source"]["dataset_repository_commit"] in headers.get("x-repo-commit", []), f"{role}_repo_commit_header_mismatch")
        _require(str(item["bytes"]) in headers.get("x-linked-size", []), f"{role}_linked_size_header_mismatch")
        _require(f'"{item["sha256_linked_etag"]}"' in headers.get("x-linked-etag", []), f"{role}_linked_etag_header_mismatch")
        _require("bytes" in [value.lower() for value in headers.get("accept-ranges", [])], f"{role}_range_support_missing")
        _require(item["xet_hash"] in headers.get("x-xet-hash", []), f"{role}_xet_hash_header_mismatch")
        _require(str(item["bytes"]) in headers.get("content-length", []), f"{role}_final_content_length_mismatch")

        role_ranges: dict[str, Any] = {}
        for range_spec in item["ranges"]:
            start = int(range_spec["start"])
            end = int(range_spec["end"])
            range_headers_raw, payload = client.byte_range(str(item["url"]), start, end)
            range_statuses, range_headers = _header_values(range_headers_raw)
            _require(range_statuses and range_statuses[-1] == 206, f"{role}_{range_spec['id']}_status_not_206")
            expected_content_range = f"bytes {start}-{end}/{item['bytes']}"
            _require(expected_content_range in range_headers.get("content-range", []), f"{role}_{range_spec['id']}_content_range_mismatch")
            _require(len(payload) == int(range_spec["bytes"]), f"{role}_{range_spec['id']}_size_mismatch")
            digest = _sha256(payload)
            _require(digest == range_spec["sha256"], f"{role}_{range_spec['id']}_sha256_mismatch")
            total_payload_bytes += len(payload)
            role_ranges[str(range_spec["id"])] = {
                "bytes": len(payload),
                "sha256": digest,
                "content_range": expected_content_range,
                "payload_retained": False,
            }
        observed[role] = {
            "head_final_status": statuses[-1],
            "redirect_observed": True,
            "repository_commit": config["source"]["dataset_repository_commit"],
            "linked_size": int(item["bytes"]),
            "linked_etag": item["sha256_linked_etag"],
            "xet_hash": item["xet_hash"],
            "accept_ranges": "bytes",
            "ranges": role_ranges,
        }

    _require(total_payload_bytes == int(config["transport"]["maximum_total_payload_bytes"]), "total_payload_budget_mismatch")
    return {
        "schema_version": "aurora.aneug_cycle_transport_p0_v2a.result.v1",
        "protocol_id": config["protocol_id"],
        "status": config["gate"]["pass_status"],
        "transport_gate_evaluated": True,
        "transport_gate_passed": True,
        "scientific_p0_evaluated": False,
        "config_sha256": config["_config_sha256"],
        "source_commit": config["source"]["dataset_repository_commit"],
        "server": "introai9",
        "scheduler": "pbs",
        "total_payload_bytes_read": total_payload_bytes,
        "observed": observed,
        "full_object_downloaded": False,
        "torch_payload_deserialized": False,
        "case_identifier_accessed": False,
        "method_selected": False,
        "architecture_selected": False,
        "gpu_accessed": False,
        "outer_test_accessed": False,
        "authorization": config["gate"]["pass_authorizes"],
    }


def _write_result(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--curl", default="curl")
    args = parser.parse_args(argv)
    config_digest = "unavailable"
    try:
        config = load_config(args.config)
        config_digest = config["_config_sha256"]
        result = audit(config, CurlTransport(config, args.curl))
        exit_code = 0
    except Exception as exc:
        result = {
            "schema_version": "aurora.aneug_cycle_transport_p0_v2a.result.v1",
            "protocol_id": "aneug_cycle_transport_p0_v2a",
            "status": "completed_transport_preflight_failed_no_scientific_verdict",
            "transport_gate_evaluated": True,
            "transport_gate_passed": False,
            "scientific_p0_evaluated": False,
            "config_sha256": config_digest,
            "server": "introai9",
            "gpu_accessed": False,
            "full_object_downloaded": False,
            "torch_payload_deserialized": False,
            "case_identifier_accessed": False,
            "failure": f"{type(exc).__name__}: {exc}",
            "authorization": "close_v2a_without_second_transport_repair_round_v2b_p1_method_architecture_gpu_or_outer_test",
        }
        exit_code = 2
    _write_result(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
