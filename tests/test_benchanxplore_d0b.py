import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import torch
except ImportError:  # pragma: no cover - lightweight local environment
    torch = None

from aurora.benchanxplore_d0b import (
    geometry_fold_assignment,
    load_d0b_config,
)

if torch is not None:
    import numpy as np

    from aurora.benchanxplore import CaseArrays
    from aurora.benchanxplore_d0b import (
        dct_ii_basis,
        project_temporal,
        run_d0b,
        temporal_covariance,
        train_only_pod_basis,
    )


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "benchanxplore_d0b.json"


class D0bContractTests(unittest.TestCase):
    def test_reference_diagnostic_pins_failed_d0(self) -> None:
        diagnostic, failed, _ = load_d0b_config(CONFIG)
        self.assertFalse(failed["frozen_gate"]["passed"])
        self.assertEqual(diagnostic["coefficient_budgets"], [17, 25])
        self.assertEqual(
            diagnostic["candidate_bases"], ["dct_ii", "train_only_pod"]
        )

    def test_status_inflation_is_rejected_before_asset_access(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["status"] = "confirmatory"
        with patch.object(Path, "read_text", return_value=json.dumps(payload)):
            with self.assertRaisesRegex(Exception, "post-result exploratory"):
                load_d0b_config(CONFIG)

    def test_geometry_folds_are_deterministic_and_balanced(self) -> None:
        first = geometry_fold_assignment(105, 5, 20260803)
        second = geometry_fold_assignment(105, 5, 20260803)
        self.assertEqual(first, second)
        self.assertEqual([first.count(fold) for fold in range(5)], [21] * 5)


@unittest.skipIf(torch is None, "D0b tensor tests require torch")
class D0bTensorTests(unittest.TestCase):
    def test_dct_basis_is_orthonormal(self) -> None:
        basis = dct_ii_basis(80, 25)
        identity = basis.T @ basis
        self.assertTrue(torch.allclose(identity, torch.eye(25), atol=2e-5))

    def test_projection_recovers_signals_in_the_basis_span(self) -> None:
        basis = dct_ii_basis(80, 17)
        coefficient = torch.randn(17, 12)
        signal = (basis @ coefficient).reshape(80, 4, 3)
        prediction = project_temporal(signal, basis)
        self.assertTrue(torch.allclose(signal, prediction, atol=2e-5))

    def test_pod_fit_excludes_held_out_covariance(self) -> None:
        training_signal = torch.zeros(80, 4)
        training_signal[2] = 2.0
        held_out_signal = torch.zeros(80, 4)
        held_out_signal[60] = 100.0
        covariances = torch.stack(
            (
                temporal_covariance(training_signal),
                temporal_covariance(held_out_signal),
            )
        )
        basis = train_only_pod_basis(
            covariances,
            [0],
            1,
            device=torch.device("cpu"),
        )
        self.assertGreater(float(torch.abs(basis[2, 0])), 0.99)
        self.assertLess(float(torch.abs(basis[60, 0])), 1e-5)

    def test_two_pass_runtime_preserves_post_result_contract(self) -> None:
        diagnostic, failed, _ = load_d0b_config(CONFIG)
        diagnostic = copy.deepcopy(diagnostic)
        diagnostic["dataset"]["expected_cases"] = 4
        diagnostic["dataset"]["timesteps"] = 8
        diagnostic["geometry_folds"] = 2
        diagnostic["coefficient_budgets"] = [2, 3]
        diagnostic["bootstrap_replicates"] = 20
        diagnostic["success_thresholds"] = {
            "full_relative_l2_max": 10.0,
            "full_energy_retained_min": -10.0,
            "full_cycle_mean_speed_relative_mae_max": 10.0,
            "full_cycle_peak_speed_relative_mae_max": 10.0,
            "bulge_relative_l2_max": 10.0,
        }
        coordinates = np.asarray(
            [[0.0, 6.0, 0.0], [0.0, 7.5, 0.0], [0.0, 9.0, 0.0]],
            dtype=np.float32,
        )

        def synthetic_case(path, expected_timesteps=8):
            index = int(Path(path).stem.split("_")[-1])
            time = np.arange(expected_timesteps, dtype=np.float32)[:, None, None]
            velocity = np.sin(
                2.0 * np.pi * (index + 1) * time / expected_timesteps
            )
            velocity = np.broadcast_to(
                velocity, (expected_timesteps, 3, 3)
            ).copy()
            return CaseArrays(
                coordinates=coordinates,
                tetrahedra=np.zeros((1, 4), dtype=np.int64),
                velocity=velocity,
                boundary_mask=np.zeros(3, dtype=np.float32),
            )

        fake_paths = [Path(f"case_{index}") for index in range(4)]
        with patch(
            "aurora.benchanxplore_d0b.discover_cases",
            return_value=fake_paths,
        ), patch(
            "aurora.benchanxplore_d0b.load_case",
            side_effect=synthetic_case,
        ):
            result = run_d0b(
                data_root=Path("."),
                config=diagnostic,
                failed_result=failed,
                require_cuda=False,
                git_commit="smoke",
            )
        self.assertEqual(result["geometry_split"]["fold_case_counts"], [2, 2])
        self.assertFalse(result["frozen_d0_relabeled"])
        self.assertEqual(
            set(result["representations"]), {"dct_ii", "train_only_pod"}
        )


if __name__ == "__main__":
    unittest.main()
