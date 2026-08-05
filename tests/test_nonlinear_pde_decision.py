import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.nonlinear_pde_decision import NonlinearDecisionError, load_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "nonlinear_pde_n1.json"


class NonlinearDecisionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_config(CONFIG)

    def _write_candidate(self, payload: dict, directory: str) -> Path:
        config_dir = Path(directory) / "configs"
        result_dir = Path(directory) / "results"
        config_dir.mkdir()
        result_dir.mkdir()
        source = ROOT / "results" / "nonlinear_pde_n0r_20260805.json"
        (result_dir / source.name).write_bytes(source.read_bytes())
        candidate = config_dir / CONFIG.name
        candidate.write_text(json.dumps(payload), encoding="utf-8")
        return candidate

    def test_reference_contract_is_valid(self) -> None:
        self.assertEqual(len(self.config["model_seeds"]["confirmatory"]), 5)
        self.assertEqual(len(self.config["mandatory_models"]), 9)

    def test_test_access_cannot_move_before_checkpoint_freeze(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["data"]["test_access"] = "during_model_selection"
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_candidate(candidate, directory)
            with self.assertRaisesRegex(NonlinearDecisionError, "checkpoint freeze"):
                load_config(path)

    def test_nots_adaptation_cannot_be_called_reproduction(self) -> None:
        candidate = copy.deepcopy(self.config)
        nots = next(
            item
            for item in candidate["mandatory_models"]
            if item["id"] == "nots_adapted"
        )
        nots["not_a_reproduction"] = False
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_candidate(candidate, directory)
            with self.assertRaisesRegex(NonlinearDecisionError, "reproduction"):
                load_config(path)

    def test_n1_cannot_authorize_3d_execution(self) -> None:
        candidate = copy.deepcopy(self.config)
        candidate["success_rule"][
            "n1_pass_authorizes_irregular_3d_protocol_registration_only"
        ] = False
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_candidate(candidate, directory)
            with self.assertRaisesRegex(NonlinearDecisionError, "decision rule"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
