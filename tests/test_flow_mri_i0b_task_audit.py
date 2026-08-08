import copy
import unittest
from pathlib import Path

from aurora.flow_mri_i0b_task_audit import (
    FlowMRII0bError,
    REGISTERED_CONFIG_SHA256,
    erode_six_neighbor,
    load_config,
    sha256_file,
    symmetric_relative_l2,
    validate_config,
    vector_cosine,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "flow_mri_protocol_i0b_task_adequacy.json"


class FlowMRII0bTaskAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(CONFIG)

    def test_registered_config_is_valid(self) -> None:
        self.assertEqual(
            self.config["gate"]["pass_authorizes"],
            "register_method_free_I0c_PAR_REC_decoder_noise_and_cross_VENC_measurement_audit_only",
        )
        self.assertFalse(
            self.config["gate"]["local_repair_rerun_or_threshold_change_allowed"]
        )
        self.assertEqual(sha256_file(CONFIG), REGISTERED_CONFIG_SHA256)

    def test_pbs_wrapper_requires_clean_exact_CPU_execution(self) -> None:
        wrapper = (ROOT / "cluster" / "pbs_flow_mri_protocol_i0b_cpu.pbs").read_text()
        self.assertIn("rev-parse HEAD", wrapper)
        self.assertIn("status --porcelain", wrapper)
        self.assertIn("$AURORA_PROJECT_ROOT:/workspace:ro", wrapper)
        self.assertNotIn("nvidia-smi", wrapper)
        self.assertNotIn("--nv", wrapper)

    def test_discovery_boundary_cannot_be_hidden(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["discovery_boundary"]["inspected_before_registration"] = False
        with self.assertRaisesRegex(FlowMRII0bError, "disclose"):
            validate_config(candidate)

    def test_thresholds_cannot_be_relaxed(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["thresholds"][
            "minimum_same_resolution_acceleration_median_relative_L2"
        ] = 0.0
        with self.assertRaisesRegex(FlowMRII0bError, "threshold"):
            validate_config(candidate)

    def test_i0b_cannot_read_2025_REC_or_select_a_method(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["sources"]["expanded_intervention_2025"][
            "REC_payload_access_in_I0b"
        ] = True
        with self.assertRaisesRegex(FlowMRII0bError, "task-unit"):
            validate_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["gate"]["pass_authorizes"] = "select_neural_method"
        with self.assertRaisesRegex(FlowMRII0bError, "authorize"):
            validate_config(candidate)

    def test_two_2025_releases_cannot_be_called_independent(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["sources"]["dual_venc_2025"][
            "relationship_to_expanded_intervention_release"
        ] = "independent_external_cohort"
        with self.assertRaisesRegex(FlowMRII0bError, "independent"):
            validate_config(candidate)

    def test_symmetric_metrics_have_expected_limits(self) -> None:
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy is unavailable")
        left = np.asarray([1.0, 2.0, 3.0])
        same = left.copy()
        opposite = -left
        self.assertAlmostEqual(symmetric_relative_l2(left, same), 0.0)
        self.assertAlmostEqual(vector_cosine(left, same), 1.0)
        self.assertAlmostEqual(symmetric_relative_l2(left, opposite), 2.0)
        self.assertAlmostEqual(vector_cosine(left, opposite), -1.0)

    def test_six_neighbor_erosion_has_no_wrapped_boundary(self) -> None:
        try:
            import numpy as np
        except ImportError:
            self.skipTest("numpy is unavailable")
        mask = np.ones((5, 5, 5), dtype=bool)
        eroded = erode_six_neighbor(mask, 1)
        self.assertEqual(int(eroded.sum()), 27)
        self.assertFalse(eroded[0].any())
        self.assertFalse(eroded[-1].any())


if __name__ == "__main__":
    unittest.main()
