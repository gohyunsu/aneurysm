import copy
import json
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v1 import load_config
from aurora.aneumo_isbi_v1_attribution import (
    AneumoISBIV1AttributionError,
    load_attribution_config,
    truth_only_diagnostics,
    validate_attribution_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v1_attribution.json"
V1_CONFIG = ROOT / "configs" / "aneumo_isbi_v1.json"
PBS = ROOT / "cluster" / "pbs_aneumo_isbi_v1_attribution.pbs"


class AneumoISBIV1AttributionContractTests(unittest.TestCase):
    def test_reference_contract_is_valid(self) -> None:
        payload = load_attribution_config(CONFIG)
        self.assertIsNone(payload["success_thresholds"])

    def test_attribution_cannot_train_or_relabel(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["authorization"]["may_relabel_v1"] = True
        with self.assertRaisesRegex(AneumoISBIV1AttributionError, "authorize"):
            validate_attribution_config(payload)

    def test_attribution_cannot_read_test_or_define_threshold(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["access"]["test_field_read"] = True
        with self.assertRaisesRegex(AneumoISBIV1AttributionError, "access"):
            validate_attribution_config(payload)
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["success_thresholds"] = {"anything": 1.0}
        with self.assertRaisesRegex(AneumoISBIV1AttributionError, "threshold"):
            validate_attribution_config(payload)

    def test_pbs_preserves_pre_result_failure(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("trap aurora_write_v1a_pbs_status EXIT", script)
        self.assertIn('tee "$AURORA_ATTRIBUTION_OUTPUT/pbs.log"', script)
        self.assertIn('"attribution_created":%s', script)


class AneumoISBIV1AttributionMetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import numpy  # noqa: F401
            import torch
        except ImportError as exc:
            raise unittest.SkipTest("numpy/torch are unavailable") from exc
        cls.torch = torch
        cls.config = load_config(V1_CONFIG)

    def test_truth_only_decomposition_is_finite_and_non_gating(self) -> None:
        import numpy as np

        torch = self.torch
        flows = np.asarray(self.config["task"]["condition_values"], dtype=np.float32)
        anchor = float(self.config["controls"]["response_only_oracle"]["anchor_mass_flow_kg_s"])
        power = float(self.config["controls"]["response_only_oracle"]["power"])
        base = torch.randn(32, 3)
        target = torch.stack(
            [base * float((float(flow) / anchor) ** power) for flow in flows], dim=0
        )
        prepared = {1: {"base_family": 4, "velocity": target.numpy()}}
        metrics = truth_only_diagnostics(self.config, prepared, flows)
        self.assertAlmostEqual(metrics["zero_field_full_q_relative_l2"], 1.0, places=6)
        self.assertFalse(metrics["truth_oracles_are_deployable_baselines"])
        self.assertGreaterEqual(metrics["within_case_condition_energy_fraction"], 0.0)


if __name__ == "__main__":
    unittest.main()
