from __future__ import annotations

import binascii
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aurora.aneumo_bc_transport_p0 import (
    AneumoBCTransportP0Error,
    load_config,
    run_p0,
)
from aurora.aneumo_range import ZipMember

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


class AneumoBCTransportP0ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).parents[1] / "configs" / "aneumo_bc_transport_p0.json"

    def test_reference_config_is_train_only_cpu_one_shot(self) -> None:
        config = load_config(self.path)
        self.assertEqual(config["access"]["base_families"], [1])
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["excluded_server"], "junjinyong")
        self.assertEqual(config["execution"]["ngpus"], 0)
        self.assertEqual(config["execution"]["maximum_submissions_for_exact_public_source"], 1)

    def test_validation_family_cannot_enter_p0(self) -> None:
        payload = json.loads(self.path.read_text())
        payload["access"]["base_families"] = [13]
        payload["access"]["cases_by_base_family"] = {"13": [239, 240]}
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "config.json"
            candidate.write_text(json.dumps(payload))
            with self.assertRaisesRegex(AneumoBCTransportP0Error, "train family"):
                load_config(candidate)

    def test_gpu_or_other_server_cannot_be_enabled(self) -> None:
        payload = json.loads(self.path.read_text())
        payload["execution"]["server"] = "junjinyong"
        payload["execution"]["ngpus"] = 1
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "config.json"
            candidate.write_text(json.dumps(payload))
            with self.assertRaisesRegex(AneumoBCTransportP0Error, "execution"):
                load_config(candidate)


@unittest.skipIf(np is None, "P0 execution test requires numpy")
class AneumoBCTransportP0ExecutionTests(unittest.TestCase):
    def test_synthetic_aligned_source_passes_without_model_or_gpu(self) -> None:
        path = Path(__file__).parents[1] / "configs" / "aneumo_bc_transport_p0.json"
        config = load_config(path)
        config["_config_sha256"] = "synthetic"
        flows = config["source"]["mass_flows_kg_s"]
        members = {}
        payloads = {}
        coordinates = np.arange(3072, dtype=np.float64).reshape(1024, 3) * 1e-5
        base = np.column_stack((coordinates[:, 1], -coordinates[:, 0], coordinates[:, 2]))
        for case in (1, 2):
            for flow in flows:
                velocity = base * (flow / 0.0025) ** 1.075 * (1.0 + case * 0.01)
                array = np.column_stack((coordinates, np.zeros(1024), velocity))
                stream = io.BytesIO()
                np.save(stream, array)
                raw = stream.getvalue()
                name = f"{case}/npy/m={flow:g}/array_internal_{case}.npy"
                members[name] = ZipMember(
                    name=name,
                    compression=0,
                    crc32=binascii.crc32(raw) & 0xFFFFFFFF,
                    compressed_size=len(raw),
                    uncompressed_size=len(raw),
                    local_offset=0,
                )
                payloads[name] = raw
        with (
            mock.patch(
                "aurora.aneumo_bc_transport_p0.load_archive_index",
                return_value=(members, {"content_length": 123, "entries": len(members)}),
            ),
            mock.patch(
                "aurora.aneumo_bc_transport_p0.fetch_member",
                side_effect=lambda _, member: payloads[member.name],
            ),
        ):
            result = run_p0(config, public_source_commit="a" * 40)
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["passed_checks"], result["total_checks"])
        self.assertFalse(result["access"]["gpu_access"])
        self.assertFalse(result["authorization"]["method"])
        self.assertAlmostEqual(
            result["diagnostics"]["train_family_case_mean_response_relative_l2"],
            0.0,
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
