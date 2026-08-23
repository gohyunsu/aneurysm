from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_ghd_gps_baseline import (
    Release730GHDGPSError,
    Release730GHDGPSUNet,
    _strict_atomic_torch_save,
    load_config,
    validate_activation,
    validate_config,
    validate_response_oracle_terminal_record,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_ghd_gps_baseline_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_ghd_gps_baseline_v1.pbs"
SOURCE = ROOT / "src" / "aurora" / "aneug_release_730_ghd_gps_baseline.py"


def synthetic_topology() -> dict[str, torch.Tensor]:
    return {
        "edge0": torch.tensor(
            [[0, 1, 1, 2, 2, 3, 3, 0], [1, 0, 2, 1, 3, 2, 0, 3]],
            dtype=torch.int64,
        ),
        "edge1": torch.tensor([[0, 1], [1, 0]], dtype=torch.int64),
        "edge2": torch.tensor([[0], [0]], dtype=torch.int64),
        "idx1": torch.tensor([0, 2], dtype=torch.int64),
        "idx2": torch.tensor([0], dtype=torch.int64),
        "parent1": torch.tensor([0, 0, 1, 1], dtype=torch.int64),
        "parent2": torch.tensor([0, 0], dtype=torch.int64),
    }


class Release730GHDGPSBaselineTests(unittest.TestCase):
    def test_config_is_matched_comparator_on_raw_sealed_protocol(self) -> None:
        config = load_config(CONFIG)
        identity = config["comparison_identity"]
        self.assertFalse(identity["exact_rhsia_reproduction"])
        self.assertFalse(identity["proposed_method"])
        self.assertEqual(config["split"]["train_cases"], 584)
        self.assertEqual(config["split"]["validation_cases"], 73)
        self.assertEqual(
            config["split"]["validation_loader_order_sha256"],
            "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        )
        self.assertFalse(config["split"]["read_locked_test_fields"])
        self.assertFalse(config["split"]["read_processed_only_extra_fields"])
        self.assertFalse(config["target_and_metric"]["hard_tangent_projection"])
        self.assertFalse(config["target_and_metric"]["hard_periodic_closure"])
        self.assertIsNone(config["decision_rule"]["absolute_performance_threshold"])
        self.assertFalse(config["authorization"]["execute_now"])
        self.assertTrue(
            config["authorization"]["requires_response_oracle_terminal_record"]
        )
        self.assertEqual(
            config["runtime"]["container_sha256"],
            "2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2",
        )

    def test_sealed_read_projection_closure_threshold_or_execution_is_rejected(self) -> None:
        config = json.loads(CONFIG.read_text())
        mutations = (
            ("split", "read_locked_test_fields", True),
            ("split", "read_processed_only_extra_fields", True),
            ("target_and_metric", "hard_tangent_projection", True),
            ("target_and_metric", "hard_periodic_closure", True),
            ("decision_rule", "absolute_performance_threshold", 0.35),
            ("authorization", "execute_now", True),
        )
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                changed = copy.deepcopy(config)
                changed[section][key] = value
                with self.assertRaises(Release730GHDGPSError):
                    validate_config(changed)

    def test_model_emits_finite_unprojected_complete_cycle(self) -> None:
        torch.manual_seed(17)
        model = Release730GHDGPSUNet(synthetic_topology(), width=16, heads=4)
        with torch.no_grad():
            bias = model.output[-1].bias.reshape(80, 3)
            bias.zero_()
            bias[:, 2] = 1.0
        case = {
            "coordinates": torch.tensor(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [1.0, 1.0, 0.0],
                    [0.0, 1.0, 0.0],
                ]
            ),
            "normals": torch.tensor([[0.0, 0.0, 1.0]]).expand(4, -1).clone(),
            "vertex_weights": torch.full((4,), 0.25),
            "ghd": torch.zeros(432),
        }
        field = model(case)
        split_field = model.decode_cycle(model.encode_geometry(case))
        torch.testing.assert_close(split_field, field, rtol=0.0, atol=0.0)
        self.assertEqual(tuple(field.shape), (80, 4, 3))
        self.assertTrue(bool(torch.isfinite(field).all().item()))
        self.assertGreater(float(field[..., 2].abs().mean().item()), 0.5)
        field.square().mean().backward()
        self.assertTrue(
            all(
                parameter.grad is None
                or bool(torch.isfinite(parameter.grad).all().item())
                for parameter in model.parameters()
            )
        )

    def test_activation_requires_terminal_direct_baseline_and_sealed_scope(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_ghd_gps_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "single_seed_validation_comparator",
            "direct_baseline_terminal_record_sha256": "1" * 64,
            "response_oracle_terminal_record_sha256": "2" * 64,
            "read_locked_test_or_extra": False,
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "private_train_audit_sha256": config["split"]["train_audit_private_sha256"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            activation["direct_baseline_terminal_record_sha256"] = ""
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaises(Release730GHDGPSError):
                validate_activation(path, config, "abc")
            activation["direct_baseline_terminal_record_sha256"] = "1" * 64
            activation["response_oracle_terminal_record_sha256"] = "short"
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaisesRegex(Release730GHDGPSError, "oracle_terminal"):
                validate_activation(path, config, "abc")

    def test_checkpoint_save_is_atomic_and_loadable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            _strict_atomic_torch_save(path, {"weight": torch.arange(3)})
            self.assertTrue(path.is_file())
            self.assertFalse(path.with_name("checkpoint.pt.tmp").exists())
            payload = torch.load(path, weights_only=True)
            torch.testing.assert_close(payload["weight"], torch.arange(3))

    def test_actual_oracle_terminal_bytes_must_match_activation(self) -> None:
        import hashlib

        payload = b'{"status":"terminal"}\n'
        activation = {
            "response_oracle_terminal_record_sha256": hashlib.sha256(
                payload
            ).hexdigest()
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oracle-terminal.json"
            path.write_bytes(payload)
            self.assertEqual(
                validate_response_oracle_terminal_record(path, activation),
                activation["response_oracle_terminal_record_sha256"],
            )
            path.write_bytes(payload + b"changed")
            with self.assertRaisesRegex(
                Release730GHDGPSError, "oracle_terminal_hash"
            ):
                validate_response_oracle_terminal_record(path, activation)

    def test_pbs_is_serialized_introai9_gpu_without_test_binding(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("ngpus=1", script)
        self.assertIn("AURORA_GHD_GPS_ACTIVATION", script)
        self.assertIn("AURORA_RESPONSE_ORACLE_TERMINAL_RECORD", script)
        self.assertIn("--response-oracle-terminal-record", script)
        self.assertIn("status_tmp", script)
        self.assertIn('/bin/mv "$status_tmp" "$status"', script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("test_manifest", script)
        self.assertNotIn("torch_geometric", source)
        self.assertNotIn("pytorch3d", source)
        self.assertNotIn("tangent_projection(", source)


if __name__ == "__main__":
    unittest.main()
