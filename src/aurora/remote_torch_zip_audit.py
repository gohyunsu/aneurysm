"""Read metadata from a remote ``torch.save`` ZIP without downloading tensors.

PyTorch's modern serialization format is a ZIP archive.  This module exposes a
seekable HTTP range reader so :mod:`zipfile` can retrieve only the central
directory and ``data.pkl``.  The pickle is inspected with :mod:`pickletools`;
it is never executed.  The resulting inventory is therefore suitable for a
pre-download cohort census, but it is not a tensor-integrity or scientific
field audit.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import pickletools
import re
import urllib.request
import zipfile
from collections import Counter
from typing import Any, Iterable, Pattern


class RemoteTorchZipAuditError(RuntimeError):
    """Raised when a bounded remote metadata audit cannot be completed."""


class HTTPRangeReader(io.RawIOBase):
    """Minimal seekable reader backed by HTTP byte-range requests."""

    def __init__(self, url: str, *, timeout: float = 60.0) -> None:
        self._url = url
        self._timeout = timeout
        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            length = response.headers.get("Content-Length")
            self._resolved_url = response.geturl()
        if length is None or not length.isdigit() or int(length) <= 0:
            raise RemoteTorchZipAuditError("missing_content_length")
        self._length = int(length)
        self._position = 0
        self.request_count = 0
        self.bytes_received = 0

    @property
    def content_length(self) -> int:
        return self._length

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._position

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            position = offset
        elif whence == io.SEEK_CUR:
            position = self._position + offset
        elif whence == io.SEEK_END:
            position = self._length + offset
        else:
            raise ValueError("invalid_whence")
        if position < 0:
            raise ValueError("negative_seek")
        self._position = min(position, self._length)
        return self._position

    def read(self, size: int = -1) -> bytes:
        if self._position >= self._length:
            return b""
        if size is None or size < 0:
            end = self._length - 1
        else:
            end = min(self._position + size, self._length) - 1
        if end < self._position:
            return b""
        request = urllib.request.Request(
            self._resolved_url,
            headers={"Range": f"bytes={self._position}-{end}"},
        )
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            status = getattr(response, "status", response.getcode())
            payload = response.read()
            content_range = response.headers.get("Content-Range")
        if status != 206 or not content_range:
            raise RemoteTorchZipAuditError("range_not_honoured")
        expected = end - self._position + 1
        if len(payload) != expected:
            raise RemoteTorchZipAuditError("short_range_response")
        self._position = end + 1
        self.request_count += 1
        self.bytes_received += len(payload)
        return payload


def extract_case_like_strings(
    pickle_bytes: bytes,
    patterns: Iterable[Pattern[str]],
) -> list[str]:
    """Return sorted unique case identifiers found in pickle string opcodes."""

    compiled = tuple(patterns)
    found: set[str] = set()
    try:
        operations = pickletools.genops(pickle_bytes)
        for opcode, argument, _ in operations:
            if opcode.name not in {
                "STRING",
                "BINSTRING",
                "SHORT_BINSTRING",
                "UNICODE",
                "BINUNICODE",
                "SHORT_BINUNICODE",
                "BINUNICODE8",
            }:
                continue
            if isinstance(argument, bytes):
                try:
                    value = argument.decode("utf-8")
                except UnicodeDecodeError:
                    continue
            else:
                value = str(argument)
            if any(pattern.fullmatch(value) for pattern in compiled):
                found.add(value)
    except Exception as exc:  # pickletools emits several parse exception types
        raise RemoteTorchZipAuditError("invalid_data_pickle") from exc
    return sorted(found)


def load_huggingface_release_case_ids(
    api_url: str,
    *,
    directory: str = "transient_data",
    pattern: str = r"stable_[0-9]+",
    timeout: float = 60.0,
) -> list[str]:
    """Enumerate public case directories from a pinned HF dataset API record."""

    with urllib.request.urlopen(api_url, timeout=timeout) as response:
        payload = json.load(response)
    prefix = directory.rstrip("/") + "/"
    compiled = re.compile(pattern)
    case_ids = {
        item["rfilename"].split("/")[1]
        for item in payload.get("siblings", [])
        if item.get("rfilename", "").startswith(prefix)
        and len(item["rfilename"].split("/")) > 2
        and compiled.fullmatch(item["rfilename"].split("/")[1])
    }
    return sorted(case_ids)


def audit_remote_torch_zip(
    url: str,
    *,
    case_patterns: Iterable[str],
    reference_case_ids: Iterable[str] | None = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Audit archive and case-ID metadata without loading any pickle object."""

    reader = HTTPRangeReader(url, timeout=timeout)
    try:
        with zipfile.ZipFile(reader) as archive:
            names = archive.namelist()
            candidates = [name for name in names if name.endswith("/data.pkl")]
            if len(candidates) != 1:
                raise RemoteTorchZipAuditError("data_pickle_member_count")
            info = archive.getinfo(candidates[0])
            if info.file_size > 64 * 1024 * 1024:
                raise RemoteTorchZipAuditError("data_pickle_too_large")
            pickle_bytes = archive.read(info)
    except (OSError, zipfile.BadZipFile) as exc:
        raise RemoteTorchZipAuditError("invalid_remote_zip") from exc

    compiled = tuple(re.compile(pattern) for pattern in case_patterns)
    case_ids = extract_case_like_strings(pickle_bytes, compiled)
    prefix_counts = Counter(
        "stable" if re.fullmatch(r"stable_[0-9]+", case_id) else case_id.split("_")[0]
        for case_id in case_ids
    )
    joined = "\n".join(case_ids).encode("utf-8")
    result: dict[str, Any] = {
        "schema_version": "aurora.remote_torch_zip_metadata_audit.v1",
        "content_length": reader.content_length,
        "zip_member_count": len(names),
        "data_pickle_member": candidates[0],
        "data_pickle_bytes": len(pickle_bytes),
        "data_pickle_sha256": hashlib.sha256(pickle_bytes).hexdigest(),
        "case_like_unique_count": len(case_ids),
        "case_like_sorted_sha256": hashlib.sha256(joined).hexdigest(),
        "case_prefix_counts": dict(sorted(prefix_counts.items())),
        "case_identifiers_emitted": False,
        "pickle_executed": False,
        "tensor_storage_bytes_read": 0,
        "http_range_request_count": reader.request_count,
        "http_range_bytes_received": reader.bytes_received,
    }
    if reference_case_ids is not None:
        reference = set(reference_case_ids)
        observed = set(case_ids)
        missing = sorted(reference - observed)
        extra = sorted(observed - reference)
        result["release_comparison"] = {
            "reference_case_count": len(reference),
            "artifact_case_like_count": len(observed),
            "intersection_count": len(reference & observed),
            "missing_from_artifact_count": len(missing),
            "extra_in_artifact_count": len(extra),
            "missing_sorted_sha256": hashlib.sha256(
                "\n".join(missing).encode("utf-8")
            ).hexdigest(),
            "extra_sorted_sha256": hashlib.sha256(
                "\n".join(extra).encode("utf-8")
            ).hexdigest(),
            "extra_prefix_counts": dict(
                sorted(
                    Counter(
                        "stable"
                        if re.fullmatch(r"stable_[0-9]+", case_id)
                        else case_id.split("_")[0]
                        for case_id in extra
                    ).items()
                )
            ),
            "case_identifiers_emitted": False,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument(
        "--case-pattern",
        action="append",
        default=[],
        help="Full-match regex. May be repeated.",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--reference-dataset-api",
        help="Optional pinned Hugging Face dataset API URL for release comparison.",
    )
    arguments = parser.parse_args()
    patterns = arguments.case_pattern or [
        r"stable_[0-9]+",
        r"Almaha_shape_[0-9]+",
        r"Eyad_shape_[0-9]+",
        r"Nuzhat_[0-9]+",
    ]
    reference_case_ids = None
    if arguments.reference_dataset_api:
        reference_case_ids = load_huggingface_release_case_ids(
            arguments.reference_dataset_api,
            timeout=arguments.timeout,
        )
    result = audit_remote_torch_zip(
        arguments.url,
        case_patterns=patterns,
        reference_case_ids=reference_case_ids,
        timeout=arguments.timeout,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
