import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_cycle_transport_p0_v2a import (
    AneuGCycleTransportV2AError,
    audit,
    load_config,
    validate_config_payload,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_cycle_transport_p0_v2a.json"


class FakeTransport:
    def __init__(self, config, *, corrupt=None):
        self.config = config
        self.corrupt = corrupt
        self.calls = []

    def _role(self, url):
        return "steady" if "steady" in url else "transient"

    def head(self, url):
        role = self._role(url)
        item = self.config["source"]["objects"][role]
        self.calls.append(("head", role))
        return (
            "HTTP/2 302\r\n"
            f"x-repo-commit: {self.config['source']['dataset_repository_commit']}\r\n"
            "accept-ranges: bytes\r\n"
            f"x-linked-size: {item['bytes']}\r\n"
            f"x-linked-etag: \"{item['sha256_linked_etag']}\"\r\n"
            f"x-xet-hash: {item['xet_hash']}\r\n\r\n"
            "HTTP/2 200\r\n"
            "accept-ranges: bytes\r\n"
            f"content-length: {item['bytes']}\r\n\r\n"
        ).encode()

    def byte_range(self, url, start, end):
        role = self._role(url)
        item = self.config["source"]["objects"][role]
        spec = next(entry for entry in item["ranges"] if entry["start"] == start)
        self.calls.append(("range", role, spec["id"]))
        payload = (f"{role}-{spec['id']}".encode() * 1048576)[:1048576]
        spec["sha256"] = hashlib.sha256(payload).hexdigest()
        if self.corrupt == (role, spec["id"]):
            payload = payload[:-1] + bytes([payload[-1] ^ 1])
        headers = (
            "HTTP/2 302\r\n\r\n"
            "HTTP/2 206\r\n"
            f"content-range: bytes {start}-{end}/{item['bytes']}\r\n"
            "content-length: 1048576\r\n\r\n"
        ).encode()
        return headers, payload


class AneuGCycleTransportP0V2ATests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(CONFIG)

    def test_frozen_config_is_cpu_only_single_round(self):
        self.assertEqual(self.config["candidate"]["source_score"], 33.0)
        self.assertEqual(self.config["prospective_reentry"]["maximum_transport_repair_rounds"], 1)
        self.assertFalse(self.config["prospective_reentry"]["historical_v1_failure_relabelled"])
        self.assertEqual(self.config["transport"]["maximum_total_payload_bytes"], 4194304)
        self.assertFalse(self.config["transport"]["full_object_download_allowed"])
        self.assertFalse(self.config["execution"]["gpu_requested"])
        self.assertEqual(self.config["execution"]["server"], "introai9")
        self.assertEqual(self.config["execution"]["excluded_server"], "junjinyong")

    def test_config_rejects_more_bytes_gpu_or_v1_relabel(self):
        for mutation, code in (
            (("transport", "maximum_total_payload_bytes", 8388608), "transport_budget_changed"),
            (("execution", "gpu_requested", True), "gpu_enabled"),
            (("prospective_reentry", "historical_v1_failure_relabelled", True), "v1_relabelled"),
        ):
            candidate = copy.deepcopy(self.config)
            section, field, value = mutation
            candidate.pop("_config_sha256", None)
            candidate[section][field] = value
            with self.assertRaisesRegex(AneuGCycleTransportV2AError, code):
                validate_config_payload(candidate)

    def test_fake_transport_passes_without_retaining_payload(self):
        candidate = copy.deepcopy(self.config)
        client = FakeTransport(candidate)
        result = audit(candidate, client)
        self.assertTrue(result["transport_gate_passed"])
        self.assertFalse(result["scientific_p0_evaluated"])
        self.assertEqual(result["total_payload_bytes_read"], 4194304)
        self.assertFalse(result["full_object_downloaded"])
        self.assertFalse(result["torch_payload_deserialized"])
        self.assertFalse(result["gpu_accessed"])
        self.assertEqual(len(client.calls), 6)
        for observed in result["observed"].values():
            for range_result in observed["ranges"].values():
                self.assertFalse(range_result["payload_retained"])
                self.assertEqual(set(range_result), {"bytes", "sha256", "content_range", "payload_retained"})

    def test_range_corruption_fails_closed(self):
        candidate = copy.deepcopy(self.config)
        client = FakeTransport(candidate, corrupt=("transient", "suffix"))
        with self.assertRaisesRegex(AneuGCycleTransportV2AError, "transient_suffix_sha256_mismatch"):
            audit(candidate, client)

    def test_pbs_script_has_no_gpu_and_one_round_guard(self):
        script = (ROOT / "cluster" / "pbs_aneug_cycle_transport_p0_v2a.pbs").read_text()
        self.assertIn("ngpus=0", script)
        self.assertIn("the single v2a repair round has already been used", script)
        self.assertNotIn("nvidia-smi", script)


if __name__ == "__main__":
    unittest.main()
