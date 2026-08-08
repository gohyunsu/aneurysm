import json
import unittest
from pathlib import Path

from aurora.aneumo_isbi_v0 import (
    AneumoISBIV0Error,
    audit,
    load_config,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_isbi_v0.json"


class AneumoISBIV0ContractTests(unittest.TestCase):
    def test_reference_config_is_valid(self) -> None:
        payload = load_config(CONFIG)
        self.assertEqual(payload["gate"]["rule"], "all_registered_checks")

    def test_patient_population_law_is_rejected(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["estimand"]["law_is_patient_population_physiology"] = True
        with self.assertRaisesRegex(AneumoISBIV0Error, "estimand"):
            validate_config(payload)

    def test_v0_cannot_authorize_outer_test(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["gate"]["pass_authorizes"] = "outer_test"
        with self.assertRaisesRegex(AneumoISBIV0Error, "development smoke"):
            validate_config(payload)


class AneumoISBIV0AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import h5py  # noqa: F401
            import numpy  # noqa: F401
        except ImportError as exc:
            raise unittest.SkipTest("h5py/numpy are unavailable") from exc

    def test_reference_contract_rejects_wrong_cache_before_field_access(self) -> None:
        config = load_config(CONFIG)
        with self.assertRaisesRegex(AneumoISBIV0Error, "cache SHA"):
            audit(config, root=ROOT, cache=Path("/dev/null"))


if __name__ == "__main__":
    unittest.main()
