from __future__ import annotations

import copy
import unittest
from pathlib import Path

from aurora.aneumo_response_fidelity_p0 import (
    AneumoResponseFidelityP0Error,
    _case_summaries,
    evaluate_records,
    load_dependencies,
    run_authorized_p0,
    spearman_correlation,
)
from aurora.response_fidelity import load_p0_config

try:
    import numpy as np
except ImportError:  # pragma: no cover - lightweight local environment
    np = None


ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "configs" / "aneumo_response_fidelity_p0.json"
PBS = ROOT / "cluster" / "pbs_aneumo_response_fidelity_p0.pbs"


@unittest.skipIf(np is None, "response P0 tests require numpy")
class AneumoResponseFidelityP0Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_p0_config(CONFIG)
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
            flows=self.flows,
            records=self.records if records is None else records,
            expected_train_mapping=self.dependencies["train_mapping"],
            reported_cache_sha256=self.config["source"]["cache_sha256"],
            dependency_hashes_exact=self.dependencies["hashes_exact"],
            historical_velocity_response_exact=self.dependencies[
                "historical_velocity_response_exact"
            ],
        )

    def test_dependencies_and_historical_velocity_result_are_exact(self) -> None:
        self.assertTrue(self.dependencies["hashes_exact"])
        self.assertTrue(self.dependencies["historical_velocity_response_exact"])
        self.assertEqual(len(self.dependencies["train_mapping"]), 20)
        self.assertEqual(self.config["gate"]["bootstrap_replicates"], 5000)

    def test_synthetic_smooth_response_passes_all_registered_checks(self) -> None:
        result = self._evaluate()
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["passed_checks"], 10)
        self.assertEqual(result["total_checks"], 10)
        self.assertFalse(result["access"]["pressure_read"])
        self.assertFalse(result["access"]["validation_or_test_fields_read"])
        self.assertFalse(result["authorization"]["method"])
        self.assertEqual(
            result["aggregate_endpoints"][
                "coordinate_half_response_descriptor_spearman"
            ]["aggregation"],
            "within_flow_family_ranks_then_concatenate",
        )
        self.assertNotIn("case_ids", result["asset"])
        self.assertNotIn("family_ids", result["asset"])

    def test_leave_one_flow_metrics_reject_jagged_response(self) -> None:
        record = self.records[0]
        smooth = _case_summaries(
            self.flows,
            record["coordinates_m"],
            record["velocity_m_s"],
            anchor_flow=self.config["task"]["anchor_mass_flow_kg_s"],
        )
        jagged_velocity = np.asarray(record["velocity_m_s"]).copy()
        orthogonal = np.column_stack(
            (
                -record["coordinates_m"][:, 1],
                record["coordinates_m"][:, 0],
                np.ones(4096, dtype=np.float64),
            )
        )
        for index in range(1, self.flows.size - 1):
            if index != 3:
                jagged_velocity[index] += (1.0 if index % 2 else -1.0) * orthogonal
        jagged = _case_summaries(
            self.flows,
            record["coordinates_m"],
            jagged_velocity,
            anchor_flow=self.config["task"]["anchor_mass_flow_kg_s"],
        )
        self.assertGreater(smooth["tangent_direction_agreement"], 0.99)
        self.assertLess(jagged["tangent_direction_agreement"], 0.80)
        self.assertGreater(jagged["interpolation_relative_error"], 0.35)

    def test_nontrain_or_changed_mapping_is_rejected(self) -> None:
        records = [dict(record) for record in self.records]
        records[0]["split"] = "validation"
        with self.assertRaisesRegex(AneumoResponseFidelityP0Error, "non-train"):
            self._evaluate(records)
        records = [dict(record) for record in self.records]
        records[0]["case_id"] = 999999
        with self.assertRaisesRegex(AneumoResponseFidelityP0Error, "mapping"):
            self._evaluate(records)

    def test_registered_node_count_is_enforced(self) -> None:
        records = [dict(record) for record in self.records]
        records[0]["coordinates_m"] = records[0]["coordinates_m"][:-1]
        records[0]["velocity_m_s"] = records[0]["velocity_m_s"][:, :-1]
        with self.assertRaisesRegex(AneumoResponseFidelityP0Error, "node count"):
            self._evaluate(records)

    def test_cache_hash_mismatch_fails_without_changing_metric_contract(self) -> None:
        result = evaluate_records(
            self.eval_config,
            flows=self.flows,
            records=self.records,
            expected_train_mapping=self.dependencies["train_mapping"],
            reported_cache_sha256="0" * 64,
            dependency_hashes_exact=True,
            historical_velocity_response_exact=True,
        )
        self.assertFalse(result["gate_passed"])
        self.assertFalse(result["checks"]["pinned_cache_and_dependency_hashes"])

    def test_current_config_refuses_before_private_cache_access(self) -> None:
        missing = ROOT / "this-private-cache-must-not-be-probed.h5"
        with self.assertRaisesRegex(AneumoResponseFidelityP0Error, "non-executable"):
            run_authorized_p0(
                CONFIG,
                root=ROOT,
                cache=missing,
                reported_cache_sha256=self.config["source"]["cache_sha256"],
            )

    def test_spearman_handles_ties_and_rejects_constant_rank(self) -> None:
        self.assertAlmostEqual(
            spearman_correlation([1, 1, 2, 3], [2, 2, 4, 6]), 1.0
        )
        with self.assertRaisesRegex(AneumoResponseFidelityP0Error, "constant"):
            spearman_correlation([1, 1, 1], [1, 2, 3])

    def test_pbs_wrapper_is_cpu_only_one_shot_and_currently_fail_closed(self) -> None:
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("ncpus=4:mem=16gb:ngpus=0", script)
        self.assertIn("aneumo_response_fidelity_p0.json", script)
        self.assertIn("AURORA_EXTERNAL_SERVICE_CHANGE_ACK", script)
        self.assertIn("exact-source P0 record exists", script)
        self.assertNotIn("nvidia-smi", script)
        self.assertNotIn("ssh ", script)
        self.assertNotIn("scp ", script)


if __name__ == "__main__":
    unittest.main()
