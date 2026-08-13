from __future__ import annotations

import copy
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_p0 import (
    AneumoResponseFidelityP0Error,
    evaluate_records as evaluate_v2_records,
    load_dependencies,
)
from aurora.aneumo_response_fidelity_p0_v3 import (
    EXPECTED_V2_CONFIG_SHA256,
    EXPECTED_V2_EVALUATOR_SHA256,
    evaluate_records,
    load_config,
    run_authorized_p0,
)
from aurora.response_fidelity import load_p0_config

try:
    import numpy as np
except ImportError:  # pragma: no cover - lightweight local environment
    np = None


ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_p0_v3.json"
V2_CONFIG = ROOT / "configs" / "aneumo_response_fidelity_p0_v2.json"


@unittest.skipIf(np is None, "response P0 v3 tests require numpy")
class AneumoResponseFidelityP0V3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)
        self.eval_config = copy.deepcopy(self.config)
        self.eval_config["gate"]["bootstrap_replicates"] = 128
        self.dependencies = load_dependencies(self.config, root=ROOT)
        self.flows = np.asarray(self.config["task"]["mass_flows_kg_s"])
        self.records = []
        for family, cases in self.dependencies["train_mapping"].items():
            for deformation, case_id in enumerate(cases):
                coordinates = (
                    np.arange(12288, dtype=np.float64).reshape(4096, 3) / 10000.0
                    + family * 1e-5
                )
                spatial = np.column_stack(
                    (
                        0.5 + coordinates[:, 0],
                        -0.2 + coordinates[:, 1] ** 2,
                        0.1 + coordinates[:, 2],
                    )
                )
                amplitude = 1.0 + 0.015 * family + 0.003 * deformation
                velocity = np.asarray(
                    [
                        amplitude
                        * (
                            spatial * (flow / 0.0025) ** 1.075
                            + (0.02 + 0.004 * family)
                            * spatial**2
                            * ((flow / 0.0025) - 1.0) ** 2
                        )
                        for flow in self.flows
                    ]
                )
                self.records.append(
                    {
                        "case_id": case_id,
                        "base_family": family,
                        "split": "train",
                        "coordinates_m": coordinates,
                        "velocity_m_s": velocity,
                    }
                )

    def _evaluate(self, records=None):
        return evaluate_records(
            self.eval_config,
            repository_root=ROOT,
            flows=self.flows,
            records=self.records if records is None else records,
            expected_train_mapping=self.dependencies["train_mapping"],
            reported_cache_sha256=self.config["source"]["cache_sha256"],
            dependency_hashes_exact=self.dependencies["hashes_exact"],
            historical_velocity_response_exact=self.dependencies[
                "historical_velocity_response_exact"
            ],
        )

    def test_v2_is_hash_preserved_and_v3_has_twelve_checks(self) -> None:
        import hashlib

        self.assertEqual(
            hashlib.sha256(V2_CONFIG.read_bytes()).hexdigest(),
            EXPECTED_V2_CONFIG_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / "src/aurora/aneumo_response_fidelity_p0.py").read_bytes()
            ).hexdigest(),
            EXPECTED_V2_EVALUATOR_SHA256,
        )
        self.assertEqual(len(self.config["gate"]["checks"]), 12)
        self.assertEqual(
            self.config["task"]["independent_unit"], "aneumo_generation_family"
        )

    def test_smooth_response_passes_all_twelve_checks(self) -> None:
        result = self._evaluate()
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["passed_checks"], 12)
        self.assertEqual(result["total_checks"], 12)
        self.assertTrue(
            result["checks"][
                "anchor_flow_tangent_direction_agreement_ci95_lower_at_least_0_80"
            ]
        )
        self.assertFalse(result["authorization"]["method"])

    def test_v2_passes_anchor_kink_that_v3_rejects(self) -> None:
        changed_records = []
        for record in self.records:
            changed = dict(record)
            velocity = np.asarray(record["velocity_m_s"]).copy()
            slope = (velocity[4] - velocity[2]) / (self.flows[4] - self.flows[2])
            flat = slope.reshape(-1)
            orthogonal = np.roll(flat, 1)
            orthogonal -= flat * np.dot(orthogonal, flat) / np.dot(flat, flat)
            orthogonal *= np.linalg.norm(flat) / np.linalg.norm(orthogonal)
            velocity[3] += (
                0.755
                * (self.flows[4] - self.flows[3])
                * orthogonal.reshape(slope.shape)
            )
            changed["velocity_m_s"] = velocity
            changed_records.append(changed)

        v2_config = copy.deepcopy(load_p0_config(V2_CONFIG))
        v2_config["gate"]["bootstrap_replicates"] = 128
        v2_result = evaluate_v2_records(
            v2_config,
            flows=self.flows,
            records=changed_records,
            expected_train_mapping=self.dependencies["train_mapping"],
            reported_cache_sha256=self.config["source"]["cache_sha256"],
            dependency_hashes_exact=self.dependencies["hashes_exact"],
            historical_velocity_response_exact=self.dependencies[
                "historical_velocity_response_exact"
            ],
        )
        v3_result = self._evaluate(changed_records)
        self.assertTrue(v2_result["gate_passed"])
        self.assertTrue(v3_result["superseded_v2_gate_would_pass"])
        self.assertFalse(v3_result["gate_passed"])
        self.assertFalse(
            v3_result["checks"][
                "anchor_flow_tangent_direction_agreement_ci95_lower_at_least_0_80"
            ]
        )
        self.assertLess(
            v3_result["aggregate_endpoints"][
                "anchor_flow_tangent_direction_agreement"
            ]["ci95"][0],
            0.8,
        )

    def test_current_v3_refuses_before_cache_access(self) -> None:
        missing = ROOT / "this-private-cache-must-not-be-probed-v3.h5"
        with self.assertRaisesRegex(AneumoResponseFidelityP0Error, "non-executable"):
            run_authorized_p0(
                CONFIG,
                root=ROOT,
                cache=missing,
                reported_cache_sha256=self.config["source"]["cache_sha256"],
            )


if __name__ == "__main__":
    unittest.main()
