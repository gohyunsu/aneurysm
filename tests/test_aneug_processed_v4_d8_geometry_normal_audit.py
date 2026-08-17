from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

from aurora.aneug_processed_v4_d8_geometry_normal_audit import (
    D8AuditError,
    aggregate_diagnostics,
    inspect_case,
    load_contract,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d8_geometry_normal_audit_v1.json"
PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d8_geometry_normal_audit_v1.pbs"

try:
    import torch
except ModuleNotFoundError:  # pragma: no cover - lightweight local environment
    torch = None


class AneuGProcessedV4D8GeometryNormalAuditTests(unittest.TestCase):
    def test_contract_is_fresh_train_only_private_and_cpu_only(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["human_activation"]["selection"], "D8")
        self.assertTrue(contract["human_activation"]["does_not_repair_resume_rerun_reopen_or_relabel_d7"])
        self.assertTrue(contract["question"]["stored_normal_magnitude_is_descriptive_only"])
        self.assertFalse(contract["descriptive_stored_normal_census"]["thresholds_select_or_change_gate"])
        self.assertFalse(contract["read_boundary"]["read_validation_tensor_values"])
        self.assertFalse(contract["read_boundary"]["read_outer_test_tensor_values"])
        self.assertEqual(contract["execution"]["ngpus"], 0)
        self.assertTrue(contract["output_contract"]["all_numeric_results_private"])

    def test_scope_gate_attempt_privacy_and_claim_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("human_activation", "selection", "D7", "human_selection_name"),
            ("descriptive_stored_normal_census", "thresholds_select_or_change_gate", True, "census_gate"),
            ("read_boundary", "read_validation_tensor_values", True, "read_boundary"),
            ("prospective_gate", "maximum_global_mesh_normal_component_ratio_p95", 0.3, "tangency"),
            ("execution", "maximum_pbs_attempts", 2, "attempt_budget"),
            ("execution", "ngpus", 1, "resources"),
            ("output_contract", "all_numeric_results_private", False, "result_privacy"),
            ("authorization", "paper_result_or_claim", True, "authorization"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            candidate[section][key] = value
            with self.assertRaisesRegex(D8AuditError, reason):
                validate_contract(candidate)

    def test_pbs_records_before_strict_mode_and_never_sources_profile(self) -> None:
        text = PBS.read_text(encoding="utf-8")
        self.assertLess(text.index("attempt.started"), text.index("set -euo pipefail"))
        self.assertLess(text.index('exec >>"$record_root/attempt.log"'), text.index("set -euo pipefail"))
        self.assertNotIn("source /etc/profile", text)
        self.assertIn("ncpus=4:mem=64gb:ngpus=0", text)
        self.assertIn("rerun or repair is forbidden", text)
        self.assertNotIn("#PBS -o", text)
        self.assertNotIn("#PBS -e", text)
        subprocess.run(["bash", "-n", str(PBS)], check=True)

    @unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
    def test_mesh_normals_repair_low_magnitude_stored_normal_without_changing_gate(self) -> None:
        contract = load_contract(CONFIG)
        labels = contract["bound_inputs"]["expected_labels"]
        coordinates = torch.tensor(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
            dtype=torch.float64,
        )
        stored = torch.tensor(
            [[0.0, 0.0, 0.001], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]],
            dtype=torch.float64,
        )
        phases = []
        for phase in range(4):
            angle = phase * 0.3
            wss = torch.tensor([1.0 + angle, 0.5 - angle, 0.0], dtype=torch.float64).repeat(4, 1)
            phases.append(torch.cat((coordinates, stored, wss), dim=1))
        tensor = torch.stack(phases)
        faces = torch.tensor([[0, 1, 2], [0, 2, 3]], dtype=torch.int64)
        mean = torch.zeros(9, dtype=torch.float64)
        std = torch.full((9,), 1.0 - 1e-5, dtype=torch.float64)
        diagnostic = inspect_case(tensor, labels, mean, std, faces, contract, torch)
        result, statistics = aggregate_diagnostics(
            (diagnostic for _ in range(406)),
            contract,
            torch,
            source_identity_reverified=True,
            private_manifest_reverified=True,
            train_scope_enforced=True,
            shared_faces_valid=True,
        )
        self.assertTrue(result["gate_pass"])
        self.assertGreater(statistics["stored_normal_magnitude_below_counts"]["0.5"], 0)
        self.assertTrue(statistics["stored_normal_census_is_descriptive_only"])
        self.assertFalse(result["stored_normal_census_selects_gate"])

    @unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
    def test_mesh_normal_wss_misalignment_fails_noncompensatorily(self) -> None:
        contract = load_contract(CONFIG)
        labels = contract["bound_inputs"]["expected_labels"]
        coordinates = torch.tensor(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
            dtype=torch.float64,
        )
        stored = torch.tensor([0.0, 0.0, 1.0], dtype=torch.float64).repeat(4, 1)
        wss = torch.tensor([0.0, 0.0, 1.0], dtype=torch.float64).repeat(4, 1)
        tensor = torch.stack([torch.cat((coordinates, stored, wss), dim=1) for _ in range(4)])
        faces = torch.tensor([[0, 1, 2], [0, 2, 3]], dtype=torch.int64)
        diagnostic = inspect_case(
            tensor,
            labels,
            torch.zeros(9, dtype=torch.float64),
            torch.full((9,), 1.0 - 1e-5, dtype=torch.float64),
            faces,
            contract,
            torch,
        )
        result, _ = aggregate_diagnostics(
            (diagnostic for _ in range(406)),
            contract,
            torch,
            source_identity_reverified=True,
            private_manifest_reverified=True,
            train_scope_enforced=True,
            shared_faces_valid=True,
        )
        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["check_results"]["mesh_normal_wss_tangency_global"])
        self.assertFalse(result["check_results"]["mesh_normal_wss_tangency_case_coverage"])


if __name__ == "__main__":
    unittest.main()
