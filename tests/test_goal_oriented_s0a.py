import copy
import unittest
from pathlib import Path

from aurora.goal_oriented_s0a import (
    S0AProtocolError,
    load_s0a_config,
    validate_s0a_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "goal_oriented_segmentation_s0a.json"


class GoalOrientedS0ATests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_s0a_config(CONFIG)

    def test_reference_config_is_valid(self) -> None:
        self.assertEqual(len(validate_s0a_config(self.config)), 5)

    def test_patient_grouping_cannot_be_relabelled_as_lesion_split(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["expected_units"]["split_unit"] = "lesion"
        with self.assertRaisesRegex(S0AProtocolError, "patient-grouping"):
            validate_s0a_config(candidate)

    def test_solver_check_cannot_be_removed(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["required_checks"].remove(
            "solver_container_has_mesh_steady_forward_and_discrete_adjoint_or_verified_shape_gradient_capability"
        )
        with self.assertRaisesRegex(S0AProtocolError, "eleven checks"):
            validate_s0a_config(candidate)

    def test_s0a_cannot_authorize_gpu_or_outer_test(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["authorization"]["gpu_training"] = True
        with self.assertRaisesRegex(S0AProtocolError, "cannot authorize"):
            validate_s0a_config(candidate)
        candidate = copy.deepcopy(self.config)
        candidate["authorization"]["outer_test"] = True
        with self.assertRaisesRegex(S0AProtocolError, "cannot authorize"):
            validate_s0a_config(candidate)

    def test_same_version_repair_rerun_cannot_be_opened(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["gate_rule"]["same_version_dependency_or_mapping_repair_rerun"] = True
        with self.assertRaisesRegex(S0AProtocolError, "no-repair"):
            validate_s0a_config(candidate)


if __name__ == "__main__":
    unittest.main()
