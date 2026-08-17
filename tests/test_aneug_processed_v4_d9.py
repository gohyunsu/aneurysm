from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

import torch

from aurora.aneug_processed_v4_d9 import (
    D9PilotError,
    MeshCanonicalizedPilot,
    aggregate_development_screen,
    canonicalize_case,
    case_metrics,
    choose_temporal_basis,
    field_loss,
    graph_parent_assignment,
    load_contract,
    tangent_projection,
    training_loss,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d9_mesh_canonicalized_pilot_v1.json"
R0_PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d9_r0_v1.pbs"
R1_PBS = ROOT / "cluster" / "pbs_aneug_processed_v4_d9_r1_v1.pbs"


def tiny_topology() -> dict[str, torch.Tensor]:
    edge0 = torch.tensor([[0, 1, 1, 2, 2, 3, 3, 0], [1, 0, 2, 1, 3, 2, 0, 3]])
    edge1 = torch.tensor([[0, 1], [1, 0]])
    edge2 = torch.tensor([[0], [0]])
    idx1 = torch.tensor([0, 2])
    idx2 = torch.tensor([0])
    return {
        "edge0": edge0,
        "edge1": edge1,
        "edge2": edge2,
        "idx1": idx1,
        "idx2": idx2,
        "parent1": graph_parent_assignment(edge0, idx1, 4),
        "parent2": graph_parent_assignment(edge1, idx2, 2),
    }


def tiny_case() -> dict[str, torch.Tensor]:
    return {
        "coordinates": torch.tensor(
            [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [1.0, 1.0, 0.0], [-1.0, 1.0, 0.0]]
        ),
        "normals": torch.tensor([[0.0, 0.0, 1.0]]).repeat(4, 1),
        "vertex_weights": torch.full((4,), 0.25),
        "ghd": torch.linspace(-1.0, 1.0, 432),
        "wss": torch.stack(
            [torch.tensor([1.0 + 0.01 * phase, 0.3, 0.0]).repeat(4, 1) for phase in range(80)]
        ),
    }


class AneuGProcessedV4D9Tests(unittest.TestCase):
    def test_contract_freezes_bounded_private_single_seed_scope(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["human_activation"]["selection"], "D9")
        self.assertEqual(contract["job_budget"]["maximum_total_requested_GPU_hours"], 28)
        self.assertFalse(contract["canonical_target"]["stored_normal_channels_used_by_model_or_loss"])
        self.assertFalse(contract["authorization"]["read_outer_or_auxiliary_tensor_values"])
        self.assertFalse(contract["scientific_role"]["single_seed_is_paper_evidence"])
        self.assertFalse(contract["outputs"]["static_site_update_required"])

    def test_mutations_of_scope_method_threshold_and_resources_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            (("human_activation", "selection"), "D8", "human_selection"),
            (("canonical_target", "stored_normal_channels_used_by_model_or_loss"), True, "stored_normal_exclusion"),
            (("train_only_temporal_basis", "maximum_rank"), 64, "basis_rank"),
            (("registered_models", "strict_SE3_claim"), True, "se3_claim"),
            (("optimization", "seed"), 7, "optimization_budget"),
            (("development_screen", "maximum_moment_over_direct_field_error_ratio"), 1.2, "field_screen"),
            (("job_budget", "maximum_accepted_jobs"), 4, "job_budget"),
            (("authorization", "outer_test"), True, "authorization_outer_test"),
        )
        for path, value, reason in mutations:
            candidate = copy.deepcopy(original)
            candidate[path[0]][path[1]] = value
            with self.assertRaisesRegex(D9PilotError, reason):
                validate_contract(candidate)

    def test_wrappers_record_before_strict_use_one_gpu_and_refuse_rerun(self) -> None:
        for path, walltime in ((R0_PBS, "04:00:00"), (R1_PBS, "12:00:00")):
            text = path.read_text(encoding="utf-8")
            self.assertLess(text.index("attempt.started"), text.index("set -euo pipefail"))
            self.assertLess(text.index('exec >>"$record_root/attempt.log"'), text.index("set -euo pipefail"))
            self.assertIn("ncpus=4:mem=64gb:ngpus=1", text)
            self.assertIn(f"walltime={walltime}", text)
            self.assertIn("rerun or repair is forbidden", text)
            self.assertNotIn("source /etc/profile", text)
            self.assertNotIn("#PBS -o", text)
            self.assertNotIn("#PBS -e", text)
            self.assertIn("AURORA_D9_ACTIVATION", text)
            subprocess.run(["bash", "-n", str(path)], check=True)

    def test_canonical_target_ignores_stored_normals_and_is_tangent(self) -> None:
        coordinates = torch.tensor(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
        )
        faces = torch.tensor([[0, 1, 2], [0, 2, 3]])
        phases = []
        for phase in range(5):
            stored = torch.full((4, 3), float(phase + 1) * 100.0)
            wss = torch.tensor([1.0, 0.5, 4.0]).repeat(4, 1)
            phases.append(torch.cat((coordinates, stored, wss), dim=1))
        normalized = torch.stack(phases)
        mean = torch.zeros(9)
        std = torch.full((9,), 1.0 - 1e-5)
        first = canonicalize_case(normalized, mean, std, faces)
        normalized[..., 3:6] = torch.randn_like(normalized[..., 3:6]) * 1e6
        second = canonicalize_case(normalized, mean, std, faces)
        self.assertTrue(torch.equal(first["normals"], second["normals"]))
        self.assertTrue(torch.equal(first["wss"], second["wss"]))
        self.assertLess(float(torch.abs(torch.sum(first["wss"] * first["normals"], dim=-1)).max()), 1e-6)
        self.assertAlmostEqual(float(first["vertex_weights"].sum()), 1.0, places=6)

    def test_temporal_basis_is_train_only_rule_compatible_and_zero_mean(self) -> None:
        time = torch.arange(80, dtype=torch.float64)
        modes = torch.stack([torch.sin(2 * torch.pi * (index + 1) * time / 80) for index in range(10)], dim=1)
        covariance = modes @ torch.diag(torch.linspace(10.0, 1.0, 10, dtype=torch.float64)) @ modes.T
        result = choose_temporal_basis(covariance)
        self.assertGreaterEqual(result["rank"], 8)
        self.assertLessEqual(result["rank"], 32)
        self.assertLess(float(result["basis"].mean(dim=0).abs().max()), 1e-6)
        self.assertTrue(torch.allclose(result["basis"].T @ result["basis"], torch.eye(result["rank"]), atol=1e-5))

    def test_direct_and_moment_models_have_registered_shapes_tangency_and_gradients(self) -> None:
        torch.manual_seed(1103)
        topology = tiny_topology()
        case = tiny_case()
        time = torch.arange(80, dtype=torch.float32)
        basis = torch.stack([torch.sin(2 * torch.pi * (index + 1) * time / 80) for index in range(8)], dim=1)
        basis, _ = torch.linalg.qr(basis)
        for variant in ("direct_cycle", "moment_pod"):
            model = MeshCanonicalizedPilot(topology, variant=variant, temporal_basis=basis if variant == "moment_pod" else None)
            output = model(case, exact_moment_projection=variant == "moment_pod")
            self.assertEqual(tuple(output["field"].shape), (80, 4, 3))
            self.assertTrue(torch.isfinite(output["field"]).all())
            self.assertLess(float(torch.abs(torch.sum(output["field"] * case["normals"], dim=-1)).max()), 1e-5)
            loss = training_loss(output, case["wss"], case["vertex_weights"], variant)
            loss.backward()
            self.assertTrue(torch.isfinite(loss))
            self.assertTrue(all(parameter.grad is None or torch.isfinite(parameter.grad).all() for parameter in model.parameters()))
            if variant == "moment_pod":
                self.assertTrue(torch.allclose(output["field"].mean(dim=0), output["mean_vector"], atol=2e-5, rtol=2e-5))
                achieved = torch.linalg.vector_norm(output["field"], dim=-1).mean(dim=0)
                self.assertTrue(torch.allclose(achieved, output["mean_magnitude"], atol=2e-5, rtol=2e-5))

    def test_scalar_vector_operator_rotates_outputs_without_claiming_strict_se3(self) -> None:
        torch.manual_seed(17)
        topology = tiny_topology()
        case = tiny_case()
        model = MeshCanonicalizedPilot(topology, variant="direct_cycle")
        model.eval()
        angle = torch.tensor(0.71)
        rotation = torch.tensor(
            [[torch.cos(angle), -torch.sin(angle), 0.0], [torch.sin(angle), torch.cos(angle), 0.0], [0.0, 0.0, 1.0]]
        )
        rotated = dict(case)
        rotated["coordinates"] = case["coordinates"] @ rotation.T
        rotated["normals"] = case["normals"] @ rotation.T
        with torch.no_grad():
            original = model(case)["field"]
            transformed = model(rotated)["field"]
        self.assertTrue(torch.allclose(transformed, original @ rotation.T, atol=2e-5, rtol=2e-5))

    def test_metrics_penalize_nonfinite_and_field_loss_is_zero_on_identity(self) -> None:
        case = tiny_case()
        self.assertEqual(float(field_loss(case["wss"], case["wss"], case["vertex_weights"])), 0.0)
        metrics = case_metrics(torch.full_like(case["wss"], float("nan")), case["wss"], case["vertex_weights"])
        self.assertEqual(metrics["osi_coverage"], 0.0)
        self.assertGreater(metrics["field_relative_l2"], 1e5)


if __name__ == "__main__":
    unittest.main()
