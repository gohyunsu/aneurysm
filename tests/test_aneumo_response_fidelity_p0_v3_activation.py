from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from aurora.aneumo_response_fidelity_p0_v3_activation import (
    ACTIVATION_RUNNER,
    ACTIVATION_SCHEMA,
    BASE_CONFIG,
    BASE_CONFIG_SHA256,
    BASE_EVALUATOR,
    BASE_EVALUATOR_SHA256,
    PROTOCOL_ID,
    REGISTERED_CACHE_BYTES,
    REGISTERED_CACHE_SHA256,
    AneumoP0V3ActivationError,
    load_activation_manifest,
    validate_activation_manifest,
)


ROOT = Path(__file__).parents[1]
WRAPPER = ROOT / "cluster/pbs_aneumo_response_fidelity_p0_v3.pbs"
COMMIT = "a" * 40
CONTAINER_SHA = "b" * 64
HOST_CACHE = "/home/introai9/private/aneumo_pilot.h5"
CONTAINER_PATH = "/home/introai9/containers/pinned.sif"
OUTPUT_ROOT = "/home/introai9/private/results"


def _manifest() -> dict:
    runner_sha = hashlib.sha256((ROOT / ACTIVATION_RUNNER).read_bytes()).hexdigest()
    return {
        "schema_version": ACTIVATION_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "status": (
            "registered_after_verified_introai9_operational_change_"
            "before_p0_v3_field_read"
        ),
        "registration": {
            "registered_at_utc": "2026-08-13T00:00:00Z",
            "external_operational_change_evidence_id": "ops-change-0001",
            "external_operational_change_verified": True,
            "container_readability_verified": True,
            "cache_readability_verified_without_hdf5_array_read": True,
            "registered_before_any_p0_v3_field_array_read": True,
            "prior_p0_v3_scientific_attempt_count": 0,
        },
        "source": {
            "public_source_commit": COMMIT,
            "p0_config": BASE_CONFIG,
            "p0_config_sha256": BASE_CONFIG_SHA256,
            "p0_evaluator": BASE_EVALUATOR,
            "p0_evaluator_sha256": BASE_EVALUATOR_SHA256,
            "activation_runner": ACTIVATION_RUNNER,
            "activation_runner_sha256": runner_sha,
            "exact_private_cache_path": HOST_CACHE,
            "cache_bytes": REGISTERED_CACHE_BYTES,
            "cache_sha256": REGISTERED_CACHE_SHA256,
            "container_path": CONTAINER_PATH,
            "container_sha256": CONTAINER_SHA,
        },
        "execution": {
            "server": "introai9",
            "pbs_only": True,
            "queue": "coss_agpu",
            "cpu": 4,
            "memory_gb": 16,
            "gpu": 0,
            "walltime": "01:00:00",
            "network": False,
            "one_shot": True,
            "submitted": False,
            "allowed_split": "train",
            "output_root": OUTPUT_ROOT,
            "login_node_gpu_command_allowed": False,
            "junjinyong_allowed": False,
        },
        "authorization": {
            "p0_v3_train_only_field_read": True,
            "pressure_read": False,
            "validation_or_test_field_read": False,
            "method": False,
            "architecture": False,
            "gpu": False,
            "outer_test": False,
            "paper_claim": False,
        },
    }


class AneumoP0V3ActivationTests(unittest.TestCase):
    def test_valid_contract_pins_immutable_v3_and_cpu_only_pbs(self) -> None:
        validate_activation_manifest(
            _manifest(),
            repository_root=ROOT,
            expected_public_source_commit=COMMIT,
            expected_host_cache_path=HOST_CACHE,
            expected_container_path=CONTAINER_PATH,
            expected_output_root=OUTPUT_ROOT,
            observed_container_sha256=CONTAINER_SHA,
        )

    def test_absent_manifest_refuses_before_cache_access(self) -> None:
        missing = ROOT / "private-activation-must-not-exist.json"
        with self.assertRaisesRegex(AneumoP0V3ActivationError, "No registered"):
            load_activation_manifest(
                missing,
                repository_root=ROOT,
                expected_public_source_commit=COMMIT,
                expected_host_cache_path=HOST_CACHE,
                expected_container_path=CONTAINER_PATH,
                expected_output_root=OUTPUT_ROOT,
                observed_container_sha256=CONTAINER_SHA,
                expected_activation_manifest_sha256="d" * 64,
            )

    def test_unverified_change_or_prior_attempt_fails_closed(self) -> None:
        for key, value in (
            ("external_operational_change_verified", False),
            ("prior_p0_v3_scientific_attempt_count", 1),
        ):
            manifest = _manifest()
            manifest["registration"][key] = value
            with self.subTest(key=key), self.assertRaises(
                AneumoP0V3ActivationError
            ):
                validate_activation_manifest(
                    manifest,
                    repository_root=ROOT,
                    expected_public_source_commit=COMMIT,
                    expected_host_cache_path=HOST_CACHE,
                    expected_container_path=CONTAINER_PATH,
                    expected_output_root=OUTPUT_ROOT,
                    observed_container_sha256=CONTAINER_SHA,
                )

    def test_path_container_or_authority_drift_fails_closed(self) -> None:
        mutations = []
        changed = _manifest()
        changed["source"]["exact_private_cache_path"] += ".other"
        mutations.append(changed)
        changed = _manifest()
        changed["source"]["container_sha256"] = "c" * 64
        mutations.append(changed)
        changed = _manifest()
        changed["execution"]["gpu"] = 1
        mutations.append(changed)
        changed = _manifest()
        changed["authorization"]["validation_or_test_field_read"] = True
        mutations.append(changed)
        for manifest in mutations:
            with self.subTest(manifest=manifest), self.assertRaises(
                AneumoP0V3ActivationError
            ):
                validate_activation_manifest(
                    manifest,
                    repository_root=ROOT,
                    expected_public_source_commit=COMMIT,
                    expected_host_cache_path=HOST_CACHE,
                    expected_container_path=CONTAINER_PATH,
                    expected_output_root=OUTPUT_ROOT,
                    observed_container_sha256=CONTAINER_SHA,
                )

    def test_unknown_or_extra_manifest_field_is_rejected(self) -> None:
        manifest = _manifest()
        manifest["posthoc_override"] = True
        with self.assertRaisesRegex(AneumoP0V3ActivationError, "keys differ"):
            validate_activation_manifest(
                manifest,
                repository_root=ROOT,
                expected_public_source_commit=COMMIT,
                expected_host_cache_path=HOST_CACHE,
                expected_container_path=CONTAINER_PATH,
                expected_output_root=OUTPUT_ROOT,
                observed_container_sha256=CONTAINER_SHA,
            )

    def test_serialized_private_manifest_is_valid_but_not_registered(self) -> None:
        path = ROOT / "private-activation-fixture-is-not-created.json"
        serialized = json.dumps(_manifest()).encode("utf-8")
        manifest_sha = hashlib.sha256(serialized).hexdigest()
        with patch.object(Path, "is_file", return_value=True), patch.object(
            Path, "read_bytes", return_value=serialized
        ):
            loaded = load_activation_manifest(
                path,
                repository_root=ROOT,
                expected_public_source_commit=COMMIT,
                expected_host_cache_path=HOST_CACHE,
                expected_container_path=CONTAINER_PATH,
                expected_output_root=OUTPUT_ROOT,
                observed_container_sha256=CONTAINER_SHA,
                expected_activation_manifest_sha256=manifest_sha,
            )
        self.assertEqual(loaded["protocol_id"], PROTOCOL_ID)

    def test_wrapper_calls_v3_activation_and_forbids_gpu_other_server(self) -> None:
        text = WRAPPER.read_text(encoding="utf-8")
        self.assertIn("#PBS -l select=1:ncpus=4:mem=16gb:ngpus=0", text)
        self.assertIn("aneumo_response_fidelity_p0_v3_activation", text)
        self.assertIn('AURORA_ACTIVATION_MANIFEST', text)
        self.assertIn('AURORA_ACTIVATION_MANIFEST_SHA256', text)
        self.assertIn('AURORA_EXTERNAL_SERVICE_CHANGE_ACK', text)
        self.assertIn('PBS_JOBID', text)
        self.assertIn(
            "A P0 v3 attempt exists; same-contract resubmission is forbidden.", text
        )
        self.assertNotIn("aneumo_response_fidelity_p0_v2.json", text)
        self.assertNotIn("junjinyong", text.lower())


if __name__ == "__main__":
    unittest.main()
