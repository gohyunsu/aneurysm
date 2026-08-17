import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d9a_projection_attribution import (
    D9AAttributionError,
    load_config,
    summarize_pairs,
    validate_activation,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "aneug_processed_v4_d9a_projection_attribution_v1.json"
PBS_PATH = ROOT / "cluster" / "pbs_aneug_processed_v4_d9a_projection_attribution_v1.pbs"


class D9AProjectionAttributionTests(unittest.TestCase):
    def test_config_is_no_fit_validation_only_and_seals_outer(self) -> None:
        config = load_config(CONFIG_PATH)
        self.assertEqual(config["scope"]["validation_cases"], 51)
        self.assertFalse(config["scope"]["fit_model"])
        self.assertFalse(config["scope"]["read_train_case_values"])
        self.assertFalse(config["scope"]["read_outer_or_auxiliary"])
        self.assertFalse(config["authorization"]["repair_model"])
        self.assertFalse(config["authorization"]["paper_result_or_claim"])

    def test_pair_summary_reports_tradeoff_without_authorizing_repair(self) -> None:
        cases = [
            {
                "raw": {"field_relative_l2": 0.4, "tawss_normalized_absolute_error": 0.3, "osi_mae": 0.02, "osi_coverage": 1.0},
                "projected": {"field_relative_l2": 0.5, "tawss_normalized_absolute_error": 0.2, "osi_mae": 0.08, "osi_coverage": 1.0},
            },
            {
                "raw": {"field_relative_l2": 0.6, "tawss_normalized_absolute_error": 0.5, "osi_mae": 0.04, "osi_coverage": 1.0},
                "projected": {"field_relative_l2": 0.7, "tawss_normalized_absolute_error": 0.4, "osi_mae": 0.10, "osi_coverage": 1.0},
            },
        ]
        summary = summarize_pairs(cases)
        self.assertTrue(summary["directions"]["projection_increases_field_error"])
        self.assertTrue(summary["directions"]["projection_reduces_tawss_error"])
        self.assertTrue(summary["directions"]["projection_increases_osi_error"])
        self.assertAlmostEqual(summary["projected_over_raw"]["field_relative_l2"], 1.2)

    def test_private_activation_binds_exact_evidence(self) -> None:
        config = load_config(CONFIG_PATH)
        payload = {
            "schema_version": "aurora.aneug_processed_v4_d9a.private_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "authorized_stage": "D9A_projection_attribution",
            "outer_or_auxiliary_access": False,
            **config["bound_evidence"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_activation(path, config, "abc")
            payload["moment_checkpoint_sha256"] = "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(D9AAttributionError):
                validate_activation(path, config, "abc")

    def test_pbs_uses_exact_a6000_container_and_read_only_inputs(self) -> None:
        script = PBS_PATH.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("singularity exec --nv --cleanenv", script)
        self.assertIn('$AURORA_D9_CACHE:/cache:ro', script)
        self.assertIn('$checkpoint_parent:/checkpoint:ro', script)
        self.assertIn("--result /output/projection_attribution.json", script)
        self.assertNotIn("--mode train", script)
        self.assertNotIn("outer", script.lower())


if __name__ == "__main__":
    unittest.main()
