from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_release_730_response_oracle import Release730ResponseOracleError
from aurora.aneug_release_730_response_oracle_relocation import (
    load_relocation_config,
    validate_relocation_activation,
    validate_relocation_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_response_oracle_relocation_junjinyong_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_release_730_response_oracle_relocation_junjinyong_v1.pbs"


class ResponseOracleRelocationTests(unittest.TestCase):
    def test_relocation_changes_runtime_only(self):
        config = load_relocation_config(CONFIG)
        self.assertEqual(config["runtime"]["execution_account"], "junjinyong")
        self.assertEqual(config["runtime"]["queue"], "ssu_a6gpu")
        self.assertEqual(config["scientific_invariants"]["rank_grid"], [0, 16, 32, 64, 128, 256])
        self.assertEqual(config["scientific_invariants"]["locked_test_cases_read"], 0)
        self.assertFalse(config["authorization"]["change_scientific_contract"])

    def test_scientific_or_sealed_scope_mutation_is_rejected(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        for section, key, value in (
            ("scientific_invariants", "rank_grid", [0, 32]),
            ("scientific_invariants", "locked_test_cases_read", 1),
            ("authorization", "change_scientific_contract", True),
            ("runtime", "queue", "coss_a6gpu"),
        ):
            changed = copy.deepcopy(config)
            changed[section][key] = value
            with self.subTest(section=section, key=key):
                with self.assertRaises(Release730ResponseOracleError):
                    validate_relocation_config(changed)

    def test_private_activation_binds_execution_and_base_commits(self):
        config = load_relocation_config(CONFIG)
        base = config["base_scientific_contract"]
        activation = {
            "schema_version": "aurora.private.aneug_release_730_response_oracle_relocation_activation.v1",
            "protocol_id": config["protocol_id"],
            "execution_public_commit": "execution-commit",
            "quality_conclusion": "success",
            "scientific_public_commit": base["public_commit"],
            "base_config_sha256": base["config_sha256"],
            "base_implementation_sha256": base["implementation_sha256"],
            "base_activation_sha256": base["activation_sha256"],
            "execution_account": "junjinyong",
            "queue": "ssu_a6gpu",
            "Qlist": "a6000",
            "authorized_stage": "single_validation_response_oracle_relocation",
            "server_relocation_only": True,
            "scientific_contract_changed": False,
            "read_locked_test_or_extra": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_relocation_activation(path, config, "execution-commit")
            activation["read_locked_test_or_extra"] = True
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaises(Release730ResponseOracleError):
                validate_relocation_activation(path, config, "execution-commit")

    def test_pbs_uses_junjinyong_queue_and_no_test_binding(self):
        script = PBS.read_text(encoding="utf-8")
        self.assertIn("#PBS -q ssu_a6gpu", script)
        self.assertIn("Qlist=a6000", script)
        self.assertIn("ngpus=1", script)
        self.assertIn('$(id -un)\" = \"junjinyong', script)
        self.assertIn("private_relocation_activation.json", script)
        self.assertNotIn("locked_test", script)
        self.assertNotIn("processed_only_extra", script)


if __name__ == "__main__":
    unittest.main()
