import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_processed_v4_d12_official_graphunet import (
    D12OfficialGraphUNetError,
    balanced_snapshot_pairs,
    load_config,
    matched_snapshot_components,
    matched_snapshot_loss,
    validate_activation,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d12_official_graphunet_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d12_official_graphunet_v1.pbs"
CONFIG_V2 = ROOT / "configs" / "aneug_processed_v4_d12_official_graphunet_v2.json"
PBS_V2 = ROOT / "cluster" / "pbs_aneug_processed_v4_d12_official_graphunet_v2.pbs"
SOURCE = ROOT / "src" / "aurora" / "aneug_processed_v4_d12_official_graphunet.py"


class D12OfficialGraphUNetTests(unittest.TestCase):
    def test_config_is_direct_prior_adapter_without_arbitrary_gate(self) -> None:
        config = load_config(CONFIG)
        identity = config["comparison_identity"]
        self.assertEqual(
            identity["label"],
            "direct_execution_of_released_GraphUNet_model_class_with_protocol_adapter",
        )
        self.assertTrue(identity["unchanged_released_model_class_and_forward"])
        self.assertFalse(identity["exact_end_to_end_reproduction"])
        self.assertEqual(
            config["source"]["graphgps_encoders_sha256"],
            "8c91521c95c6bec7458e7d6f23998283c029028874edd0deff444dac38a574f2",
        )
        self.assertIsNone(config["decision_rule"]["absolute_field_threshold"])
        self.assertFalse(config["bound_data"]["read_outer_or_auxiliary"])
        self.assertFalse(config["authorization"]["outer_test"])

    def test_balanced_pairs_cover_every_case_phase_once(self) -> None:
        first = balanced_snapshot_pairs(3, 5, 11, 0)
        second = balanced_snapshot_pairs(3, 5, 11, 0)
        next_epoch = balanced_snapshot_pairs(3, 5, 11, 1)
        expected = {(case, phase) for case in range(3) for phase in range(5)}
        self.assertEqual(set(first), expected)
        self.assertEqual(len(first), len(expected))
        self.assertEqual(first, second)
        self.assertNotEqual(first, next_epoch)

    def test_matched_loss_is_finite_and_zero_for_exact_prediction(self) -> None:
        reference = torch.tensor(
            [[[1.0, 0.0, 0.0], [0.0, 2.0, 0.0]], [[0.5, 0.0, 0.0], [0.0, 1.0, 0.0]]]
        )
        weights = torch.tensor([[0.25, 0.75], [0.4, 0.6]])
        exact = matched_snapshot_loss(reference, reference, weights)
        shifted = matched_snapshot_loss(reference + 0.1, reference, weights)
        self.assertEqual(float(exact.item()), 0.0)
        self.assertTrue(bool(torch.isfinite(shifted).item()))
        self.assertGreater(float(shifted.item()), 0.0)
        with self.assertRaises(D12OfficialGraphUNetError):
            matched_snapshot_loss(reference, reference, torch.ones(2))

    def test_microbatch_components_recover_effective_batch_loss(self) -> None:
        torch.manual_seed(7)
        reference = torch.randn(8, 5, 3)
        prediction = reference + 0.2 * torch.randn(8, 5, 3)
        weights = torch.rand(8, 5) + 0.1
        whole = matched_snapshot_loss(prediction, reference, weights)
        _, denominator = matched_snapshot_components(prediction, reference, weights)
        accumulated = torch.zeros(())
        for start in range(0, 8, 2):
            numerator, _ = matched_snapshot_components(
                prediction[start : start + 2],
                reference[start : start + 2],
                weights[start : start + 2],
            )
            accumulated = accumulated + numerator / denominator
        self.assertTrue(torch.allclose(whole, accumulated, atol=1e-7, rtol=1e-7))

    def test_v2_preserves_effective_batch_after_r1_oom(self) -> None:
        config = load_config(CONFIG_V2)
        optimization = config["optimization"]
        self.assertEqual(optimization["physical_snapshot_batch_size"], 8)
        self.assertEqual(optimization["effective_snapshot_batch_size"], 32)
        self.assertEqual(optimization["gradient_accumulation_steps"], 4)
        self.assertIsNone(config["decision_rule"]["absolute_field_threshold"])
        self.assertFalse(config["bound_data"]["read_outer_or_auxiliary"])
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d12.private_activation.v2",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D12_official_graphunet_microbatch_validation",
            "outer_or_auxiliary_access": False,
            "cache_manifest_sha256": config["bound_data"]["cache_manifest_sha256"],
            "official_commit": config["source"]["commit"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_activation(path, config, "abc")

    def test_activation_binds_public_source_cache_and_scope(self) -> None:
        config = load_config(CONFIG)
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d12.private_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D12_official_graphunet_validation",
            "outer_or_auxiliary_access": False,
            "cache_manifest_sha256": config["bound_data"]["cache_manifest_sha256"],
            "official_commit": config["source"]["commit"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_activation(path, config, "abc")
            payload["outer_or_auxiliary_access"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(D12OfficialGraphUNetError):
                validate_activation(path, config, "abc")

    def test_pbs_pins_official_checkout_and_isolated_pyg(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("$AURORA_OFFICIAL_ROOT:/official:ro", script)
        self.assertIn("$AURORA_PYG_TARGET:/pyg:ro", script)
        self.assertIn("/output/checkpoints", script)
        self.assertNotIn("outer", script.lower())
        self.assertIn("importlib.import_module", source)
        self.assertIn("PyGGraphUNetwTemporalEmbedding", source)
        v2_script = PBS_V2.read_text(encoding="utf-8")
        self.assertIn("walltime=72:00:00", v2_script)
        self.assertIn("CUBLAS_WORKSPACE_CONFIG=:4096:8", v2_script)
        self.assertIn("official_graphunet_v2.json", v2_script)


if __name__ == "__main__":
    unittest.main()
