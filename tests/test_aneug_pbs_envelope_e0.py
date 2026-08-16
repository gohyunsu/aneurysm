from __future__ import annotations

import copy
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from aurora.aneug_pbs_envelope_e0 import (
    E0ContractError,
    _strict_atomic_json,
    load_contract,
    run,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_pbs_envelope_e0_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_pbs_envelope_e0_v1.pbs"


class AneuGPBSEnvelopeE0Tests(unittest.TestCase):
    def test_contract_is_one_shot_cpu_only_and_d6_stays_closed(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["execution"]["server"], "introai9")
        self.assertEqual(
            tuple(contract["execution"][key] for key in ("ncpus", "memory_gb", "ngpus")),
            (1, 2, 0),
        )
        self.assertEqual(contract["execution"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["execution"]["rerun_or_repair_after_any_outcome"])
        self.assertFalse(contract["closed_d6_boundary"]["e0_reopens_or_relabels_d6"])
        self.assertTrue(all(contract["forbidden_scope"].values()))

    def test_scope_and_resource_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("status", None, "active", "status"),
            ("execution", "server", "other", "server"),
            ("execution", "ngpus", 1, "resources"),
            ("execution", "maximum_pbs_attempts", 2, "attempt_budget"),
            ("execution", "rerun_or_repair_after_any_outcome", True, "rerun"),
            ("forbidden_scope", "tensor_or_field_value_read", False, "forbidden_scope"),
            ("consequence", "pass_does_not_authorize_model_or_gpu", False, "consequence"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            if key is None:
                candidate[section] = value
            else:
                candidate[section][key] = value
            with self.assertRaisesRegex(E0ContractError, reason):
                validate_contract(candidate)

    def test_atomic_json_refuses_nonfinite_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            with self.assertRaises(ValueError):
                _strict_atomic_json(target, {"value": math.nan})
            _strict_atomic_json(target, {"ok": True})
            self.assertEqual(json.loads(target.read_text()), {"ok": True})
            with self.assertRaisesRegex(E0ContractError, "output_exists"):
                _strict_atomic_json(target, {"ok": False})

    def test_runner_emits_only_infrastructure_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with mock.patch(
                "aurora.aneug_pbs_envelope_e0._git",
                side_effect=["a" * 40, ""],
            ), mock.patch.dict(
                os.environ,
                {"PBS_JOBID": "1.example", "PBS_O_WORKDIR": directory},
                clear=False,
            ), mock.patch.dict(
                sys.modules,
                {"torch": SimpleNamespace(__version__="test")},
            ):
                payload = run(CONFIG, ROOT, "a" * 40, output)
            self.assertTrue(payload["envelope_pass"])
            self.assertFalse(payload["scientific_boundary"]["payload_or_tensor_read"])
            self.assertIsNone(payload["scientific_boundary"]["scientific_verdict"])
            self.assertFalse(payload["consequence"]["field_read_authorized"])
            self.assertFalse(payload["consequence"]["model_or_gpu_authorized"])

    def test_wrapper_records_before_strict_mode_and_has_no_scientific_inputs(self) -> None:
        text = PBS.read_text(encoding="utf-8")
        self.assertIn("ncpus=1:mem=2gb:ngpus=0", text)
        self.assertIn("walltime=00:05:00", text)
        self.assertLess(text.index("attempt.started"), text.index("set -euo pipefail"))
        self.assertNotIn("source /etc/profile", text)
        self.assertNotIn("AURORA_DATA_ROOT", text)
        self.assertNotIn("AURORA_D5_PRIVATE_MANIFEST", text)
        self.assertNotIn("junjinyong", text)
        subprocess.run(["bash", "-n", str(PBS)], check=True)


if __name__ == "__main__":
    unittest.main()
