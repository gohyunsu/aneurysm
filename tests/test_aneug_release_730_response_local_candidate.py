import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch
from torch import nn

from aurora.aneug_release_730_response_local_candidate import (
    Release730ResponseLocalError,
    _valid_support_osi,
    active_parameter_count,
    configure_trainable_cell,
    make_candidate_checkpoint,
    restore_candidate_checkpoint,
    validate_activation,
    validate_config,
)
from aurora.cycle_response_residual import SharedEncoderCycleResponseResidual


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "aneug_release_730_response_local_candidate_v1.json"
PBS_PATH = ROOT / "cluster" / "pbs_aneug_release_730_response_local_candidate_v1.pbs"


def config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def activation(mode="architecture", architecture="response_only", objective="field_only"):
    initial = None
    if mode == "functional_finetune":
        initial = "5" * 64
    return {
        "schema_version": "aurora.private.aneug_release_730_response_local_activation.v1",
        "protocol_id": "aneug_release_730_response_local_candidate_v1",
        "public_commit": "1" * 40,
        "quality_conclusion": "success",
        "authorized_stage": "single_seed_validation_development",
        "authorized_mode": mode,
        "architecture_variant": architecture,
        "objective_variant": objective,
        "selected_response_rank": 32,
        "response_basis_sha256": "2" * 64,
        "response_oracle_terminal_record_sha256": "3" * 64,
        "ghd_gps_terminal_record_sha256": "4" * 64,
        "transolver_terminal_record_sha256": "6" * 64,
        "initial_combined_field_checkpoint_sha256": initial,
        "private_split_manifest_sha256": config()["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config()["split"]["train_audit_private_sha256"],
        "read_locked_test_or_extra": False,
        "continuation_mode": False,
        "resume_checkpoint_sha256": None,
        "prior_attempt_terminal_record_sha256": None,
    }


def synthetic_payload(phases=4, nodes=5, rank=3):
    generator = torch.Generator().manual_seed(31)
    dimension = phases * nodes * 3
    matrix = torch.randn(dimension, rank, generator=generator)
    basis = torch.linalg.qr(matrix, mode="reduced").Q.T
    return {
        "schema_version": "aurora.private.aneug_release_730_response_basis.v1",
        "protocol_id": "aneug_release_730_response_oracle_v1",
        "phases": phases,
        "nodes": nodes,
        "mean": torch.randn(dimension, generator=generator),
        "basis": basis,
        "reference_weights": torch.full((nodes,), 1.0 / nodes),
        "train_scales": torch.tensor([0.7, 1.0, 1.4]),
        "train_cases": 584,
        "case_ids_included": False,
    }


class TinySharedBackbone(nn.Module):
    encoded_width = 8

    def __init__(self, phases=4, nodes=5):
        super().__init__()
        self.phases = phases
        self.nodes = nodes
        self.encoder = nn.Linear(7, self.encoded_width)
        self.output = nn.Sequential(
            nn.Linear(self.encoded_width, self.encoded_width),
            nn.SiLU(),
            nn.Linear(self.encoded_width, phases * 3),
        )

    def encode_geometry(self, case):
        return self.encoder(case["node_features"])

    def decode_cycle(self, features):
        field = self.output(features).reshape(self.nodes, self.phases, 3)
        return field.permute(1, 0, 2).contiguous()


def tiny_case(nodes=5):
    generator = torch.Generator().manual_seed(37)
    normals = torch.randn(nodes, 3, generator=generator)
    normals = normals / torch.linalg.vector_norm(normals, dim=-1, keepdim=True)
    return {
        "node_features": torch.randn(nodes, 7, generator=generator),
        "vertex_weights": torch.arange(1, nodes + 1, dtype=torch.float32),
        "normals": normals,
        "ghd": torch.randn(432, generator=generator),
    }


class ResponseLocalCandidateTests(unittest.TestCase):
    def test_config_is_sealed_threshold_free_and_five_cell_bounded(self):
        value = config()
        validate_config(value)
        self.assertIsNone(value["evaluation"]["absolute_performance_threshold"])
        self.assertFalse(value["split"]["read_locked_test_fields"])
        self.assertFalse(value["split"]["read_processed_only_extra_fields"])
        self.assertEqual(value["cells"]["maximum_candidate_gpu_jobs_before_confirmation"], 5)
        self.assertEqual(
            value["model"]["local_gate"],
            "nodewise_phase_shared_sigmoid_from_shared_features",
        )

    def test_config_rejects_test_access_server_and_threshold_changes(self):
        for path, replacement in (
            (("split", "read_locked_test_fields"), True),
            (("runtime", "server"), "junjinyong"),
            (("evaluation", "absolute_performance_threshold"), 0.2),
        ):
            value = config()
            value[path[0]][path[1]] = replacement
            with self.assertRaises(Release730ResponseLocalError):
                validate_config(value)

    def test_activation_accepts_only_registered_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation()), encoding="utf-8")
            observed = validate_activation(
                path, config(), "1" * 40, "architecture", "response_only", "field_only"
            )
            self.assertEqual(observed["selected_response_rank"], 32)

            path.write_text(
                json.dumps(
                    activation(
                        "functional_finetune",
                        "response_plus_residual",
                        "all_field_anchored",
                    )
                ),
                encoding="utf-8",
            )
            observed = validate_activation(
                path,
                config(),
                "1" * 40,
                "functional_finetune",
                "response_plus_residual",
                "all_field_anchored",
            )
            self.assertEqual(observed["initial_combined_field_checkpoint_sha256"], "5" * 64)

            invalid = activation("functional_finetune", "response_only", "all_scalarized")
            path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaises(Release730ResponseLocalError):
                validate_activation(
                    path,
                    config(),
                    "1" * 40,
                    "functional_finetune",
                    "response_only",
                    "all_scalarized",
                )

    def test_response_only_freezes_only_inactive_heads(self):
        model = SharedEncoderCycleResponseResidual(
            TinySharedBackbone(), synthetic_payload(), rank=3, local_output_scale=2.0
        )
        total = sum(parameter.numel() for parameter in model.parameters())
        configure_trainable_cell(model, "response_only")
        self.assertLess(active_parameter_count(model), total)
        self.assertTrue(all(not p.requires_grad for p in model.backbone.output.parameters()))
        self.assertTrue(all(not p.requires_grad for p in model.residual_gate_head.parameters()))
        self.assertTrue(all(not p.requires_grad for p in model.single_field_head.parameters()))
        output = model(tiny_case(), variant="response_only")["field"]
        output.square().mean().backward()
        self.assertTrue(any(p.grad is not None for p in model.backbone.encoder.parameters()))
        self.assertTrue(any(p.grad is not None for p in model.response_head.parameters()))
        self.assertTrue(all(p.grad is None for p in model.backbone.output.parameters()))

    def test_combined_cell_uses_spatial_gate_and_excludes_steady_head(self):
        model = SharedEncoderCycleResponseResidual(
            TinySharedBackbone(), synthetic_payload(), rank=3, local_output_scale=2.0
        )
        configure_trainable_cell(model, "response_plus_residual")
        self.assertTrue(all(p.requires_grad for p in model.backbone.output.parameters()))
        self.assertTrue(all(p.requires_grad for p in model.residual_gate_head.parameters()))
        self.assertTrue(all(not p.requires_grad for p in model.single_field_head.parameters()))
        output = model(tiny_case(), variant="response_plus_residual")
        self.assertEqual(tuple(output["residual_gate"].shape), (1, 5, 1))
        output["field"].square().mean().backward()
        self.assertTrue(any(p.grad is not None for p in model.residual_gate_head.parameters()))

    def test_valid_support_osi_uses_area_weighted_reference_support(self):
        reference = torch.tensor(
            [
                [[1.0, 0.0, 0.0], [0.01, 0.0, 0.0]],
                [[-1.0, 0.0, 0.0], [0.01, 0.0, 0.0]],
            ]
        )
        prediction = reference.clone()
        weights = torch.tensor([0.75, 0.25])
        mae, coverage = _valid_support_osi(
            prediction, reference, weights, reference_tawss_floor=0.1
        )
        self.assertAlmostEqual(mae, 0.0, places=7)
        self.assertAlmostEqual(coverage, 1.0, places=7)

    def test_candidate_checkpoint_restores_selection_and_rng_state(self):
        model = nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)
        state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        provenance = {"response_basis_sha256": "a" * 64}
        payload = make_candidate_checkpoint(
            config=config(),
            mode="architecture",
            architecture_variant="response_only",
            objective_variant="field_only",
            rank=32,
            epoch=1,
            optimizer_steps=292,
            selection_name="validation_field_relative_l2",
            selection_value=0.42,
            best_selection_value=0.42,
            best_epoch=1,
            stale_epochs=0,
            model_state_dict=state,
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            best_state_dict=state,
            history=[{"epoch": 1, "selection_value": 0.42}],
            smoke={"finite_forward_backward": True},
            train_term_normalizers=None,
            selection_endpoint_normalizers=None,
            reference_tawss_floor=1e-4,
            elapsed_seconds_accumulated=3.0,
            provenance=provenance,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            torch.save(payload, path)
            with torch.no_grad():
                for parameter in model.parameters():
                    parameter.add_(10.0)
            restored = restore_candidate_checkpoint(
                path,
                config=config(),
                expected_provenance=provenance,
                mode="architecture",
                architecture_variant="response_only",
                objective_variant="field_only",
                rank=32,
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                maximum_epochs=251,
            )
        self.assertEqual(restored["selection_name"], "validation_field_relative_l2")
        self.assertEqual(restored["optimizer_steps"], 292)
        for key, value in model.state_dict().items():
            torch.testing.assert_close(value, state[key])

    def test_pbs_runs_one_bound_cell_on_introai9_without_test_or_extra_input(self):
        script = PBS_PATH.read_text(encoding="utf-8")
        candidate_source = (
            ROOT
            / "src"
            / "aurora"
            / "aneug_release_730_response_local_candidate.py"
        ).read_text(encoding="utf-8")
        loader_source = (
            ROOT / "src" / "aurora" / "aneug_release_730_ghd_gps_baseline.py"
        ).read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("ngpus=1", script)
        self.assertIn("#PBS -l walltime=72:00:00", script)
        for name in (
            "AURORA_RESPONSE_LOCAL_ACTIVATION",
            "AURORA_RESPONSE_LOCAL_MODE",
            "AURORA_RESPONSE_LOCAL_ARCHITECTURE",
            "AURORA_RESPONSE_LOCAL_OBJECTIVE",
            "AURORA_RESPONSE_BASIS",
            "AURORA_RESPONSE_ORACLE_TERMINAL_RECORD",
            "AURORA_GHD_GPS_TERMINAL_RECORD",
            "AURORA_TRANSOLVER_TERMINAL_RECORD",
            "AURORA_RESPONSE_LOCAL_RESUME_CHECKPOINT",
            "AURORA_RESPONSE_LOCAL_PRIOR_ATTEMPT_TERMINAL_RECORD",
        ):
            self.assertIn(name, script)
        self.assertIn("--initial-combined-field-checkpoint", script)
        self.assertIn("--resume-checkpoint", script)
        self.assertIn("--prior-attempt-terminal-record", script)
        self.assertIn('status_tmp="$run_root/attempt.status.json.tmp"', script)
        self.assertIn('/bin/mv "$status_tmp" "$status"', script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("test_manifest", script)
        self.assertNotIn("processed_only", script)
        self.assertGreaterEqual(
            candidate_source.count("compute_residual_basis_leakage=False"), 3
        )
        self.assertLess(
            loader_source.index("steady = safe_torch_load(steady_path, torch)"),
            loader_source.index("del steady"),
        )
        self.assertLess(
            loader_source.index("del steady"),
            loader_source.index("transient = safe_torch_load(transient_path, torch)"),
        )


if __name__ == "__main__":
    unittest.main()
