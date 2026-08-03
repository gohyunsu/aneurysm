from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneumo_scaling_audit import (
    AneumoScalingAuditError,
    _family_values,
    _select_power,
    _sufficient_statistics,
    audit,
    load_config,
)

try:
    import numpy as np
except ImportError:  # pragma: no cover - lightweight local environment
    np = None

try:
    import h5py
except ImportError:  # pragma: no cover - lightweight local environment
    h5py = None


@unittest.skipIf(np is None, "scaling audit tests require numpy")
class AneumoScalingAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = (
            Path(__file__).parents[1] / "configs" / "aneumo_scaling_audit_v1.json"
        )

    def test_reference_config_is_train_only_and_strong(self) -> None:
        config = load_config(self.path)
        self.assertEqual(config["source"]["allowed_split"], "train")
        self.assertTrue(
            config["strong_oracle_baseline"]["uses_same_case_anchor_field"]
        )
        self.assertEqual(
            config["eligibility_gate"][
                "minimum_tuned_power_residual_ci95_lower"
            ],
            0.15,
        )
        self.assertEqual(
            config["source"]["cache_sha256_from_completed_integrity_stage"],
            "9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9",
        )

    def test_validation_field_access_cannot_be_enabled(self) -> None:
        payload = json.loads(self.path.read_text())
        payload["source"]["allowed_split"] = "validation"
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "config.json"
            candidate.write_text(json.dumps(payload))
            with self.assertRaisesRegex(AneumoScalingAuditError, "train fields only"):
                load_config(candidate)

    def test_exact_power_law_has_zero_residual_and_recovers_power(self) -> None:
        anchor = np.linspace(0.5, 2.0, 32)[:, None]
        statistics = []
        for family in range(1, 5):
            for ratio in (0.4, 0.8, 1.2, 1.6):
                target = anchor * ratio**1.5
                delta_squared, cross, anchor_squared, response_ratio = (
                    _sufficient_statistics(
                        anchor, target, remove_spatial_mean=False
                    )
                )
                statistics.append(
                    {
                        "base_family": family,
                        "flow_ratio": ratio,
                        "delta_squared": delta_squared,
                        "cross": cross,
                        "anchor_squared": anchor_squared,
                        "response_to_anchor_norm": response_ratio,
                    }
                )
        power, objective = _select_power(
            statistics, {"minimum": 0.5, "maximum": 2.0, "step": 0.025}
        )
        self.assertAlmostEqual(power, 1.5)
        self.assertLess(objective, 1e-7)
        self.assertLess(max(_family_values(statistics, power).values()), 1e-7)

    def test_pressure_centering_removes_gauge_offset(self) -> None:
        anchor = np.linspace(-2.0, 2.0, 64)[:, None]
        target = 4.0 * anchor + 12345.0
        delta_squared, cross, anchor_squared, _ = _sufficient_statistics(
            anchor, target, remove_spatial_mean=True
        )
        statistic = {
            "base_family": 1,
            "flow_ratio": 2.0,
            "delta_squared": delta_squared,
            "cross": cross,
            "anchor_squared": anchor_squared,
        }
        self.assertLess(_family_values([statistic], 2.0)[1], 1e-7)

    @unittest.skipIf(h5py is None, "full audit test requires h5py")
    def test_full_audit_skips_nontrain_field_arrays_and_emits_aggregate_only(
        self,
    ) -> None:
        config = load_config(self.path)
        flows = np.asarray(
            [0.0010, 0.0015, 0.0020, 0.0025, 0.0030, 0.0035, 0.0040, 0.0045],
            dtype=np.float64,
        )
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "synthetic.h5"
            with h5py.File(cache, "w") as handle:
                handle.attrs["config_sha256"] = config["source"][
                    "staging_config_sha256"
                ]
                handle.create_dataset("mass_flows_kg_s", data=flows)
                geometries = handle.create_group("geometries")
                anchor = np.asarray(
                    [[-1.0, 0.5, 1.0, 1.5], [1.0, 1.5, 2.0, 2.5]],
                    dtype=np.float64,
                )
                for case_id in range(1, 41):
                    group = geometries.create_group(str(case_id))
                    group.attrs["split"] = "train"
                    group.attrs["base_family"] = (case_id - 1) // 2 + 1
                    values = []
                    for flow in flows:
                        ratio = float(flow / 0.0025)
                        values.append(
                            np.column_stack(
                                [anchor[:, 0] * ratio**2, anchor[:, 1:] * ratio]
                            )
                        )
                    group.create_dataset("pressure_velocity", data=np.asarray(values))
                nontrain = geometries.create_group("41")
                nontrain.attrs["split"] = "validation"
                nontrain.attrs["base_family"] = 21
                nontrain.create_dataset(
                    "pressure_velocity",
                    data=np.full((1, 1, 1), np.nan, dtype=np.float64),
                )

            result = audit(config, cache)
            self.assertFalse(
                result["field_access"]["validation_or_test_fields_read"]
            )
            self.assertEqual(result["field_access"]["train_cases"], 40)
            self.assertEqual(result["field_access"]["skipped_nontrain_cases"], 1)
            self.assertNotIn("train_case_ids", result["field_access"])
            self.assertNotIn(
                "per_base_family",
                result["channels"]["velocity"]["tuned_power_residual"],
            )


if __name__ == "__main__":
    unittest.main()
