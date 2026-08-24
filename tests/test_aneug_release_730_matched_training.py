import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import torch
from torch import nn

from aurora.aneug_release_730_matched_training import (
    MatchedCycleSingleFieldModel,
    Release730MatchedTrainingError,
    active_parameter_count,
    configure_information_mode,
    make_checkpoint,
    rebuild_exposure_digest,
    restore_checkpoint,
    transient_protocol_digest,
    validate_activation,
    validate_config,
    validate_development_bundle,
    validate_selection_record,
    validate_single_seed_matched_information_result,
    validate_steady_scale_result,
)
from aurora.aneug_release_730_steady_exposure_schedule import (
    exposure_prefix,
    ordered_digest,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "aneug_release_730_matched_training_v1.json"
PBS_PATH = ROOT / "cluster" / "pbs_aneug_release_730_matched_training_v1.pbs"


def config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def activation(
    role="selected_control", information="transient_only", training_seed=1103
):
    proposal = role == "selected_proposal"
    confirmation = training_seed != 1103
    return {
        "schema_version": "aurora.private.aneug_release_730_matched_training_activation.v1",
        "protocol_id": "aneug_release_730_matched_training_v1",
        "public_commit": "1" * 40,
        "quality_conclusion": "success",
        "authorized_stage": (
            "five_seed_matched_information_validation_confirmation"
            if confirmation
            else (
                "single_seed_auxiliary_compute_attribution_development"
                if information == "transient_mean"
                else "single_seed_matched_information_validation_development"
            )
        ),
        "training_seed": training_seed,
        "model_role": role,
        "information_mode": information,
        "model_family": (
            "release730_response_plus_local_residual"
            if proposal
            else "release730_ghd_gps"
        ),
        "objective_variant": "all_field_anchored" if proposal else "field_only",
        "selected_response_rank": 32 if proposal else None,
        "development_evidence_bundle_sha256": "2" * 64,
        "selected_model_decision_record_sha256": "3" * 64,
        "steady_scale_result_sha256": "4" * 64,
        "response_basis_sha256": "5" * 64 if proposal else None,
        "private_split_manifest_sha256": config()["split"]["private_manifest_sha256"],
        "private_train_audit_sha256": config()["split"]["train_audit_private_sha256"],
        "private_overlap_result_sha256": config()["source"]["private_overlap_result_sha256"],
        "multiseed_confirmation_config_sha256": (
            config()["source"]["multiseed_confirmation_config_sha256"]
            if confirmation
            else None
        ),
        "single_seed_matched_information_result_sha256": (
            "6" * 64 if confirmation else None
        ),
        "read_locked_test_or_extra": False,
        "continuation_mode": False,
        "resume_checkpoint_sha256": None,
        "prior_attempt_terminal_record_sha256": None,
    }


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DummyControlInner(nn.Module):
    def __init__(self):
        super().__init__()
        self.cycle_gain = nn.Parameter(torch.tensor(1.0))
        self.single_field_head = nn.Linear(3, 3, bias=False)
        nn.init.eye_(self.single_field_head.weight)

    def forward(self, case, *, mode):
        if mode == "cycle":
            return case["normalized_cycle"] * self.cycle_gain
        return self.single_field_head(case["single_features"])


class DummyProposalInner(nn.Module):
    def __init__(self):
        super().__init__()
        self.cycle_gain = nn.Parameter(torch.tensor(1.0))
        self.single_field_head = nn.Linear(3, 3, bias=False)
        nn.init.eye_(self.single_field_head.weight)

    def forward(self, case, *, variant, compute_residual_basis_leakage):
        assert variant == "response_plus_residual"
        assert compute_residual_basis_leakage is False
        return {"field": case["physical_cycle"] * self.cycle_gain}

    def forward_single_field(self, case):
        return self.single_field_head(case["single_features"])


class MatchedTrainingTests(unittest.TestCase):
    def test_config_is_symmetric_sealed_and_threshold_free(self):
        value = config()
        validate_config(value)
        self.assertEqual(value["eligible_steady"]["eligible_rows"], 13_985)
        self.assertEqual(value["factorial"]["cells"], [
            "control_T", "control_TS", "proposal_T", "proposal_TS"
        ])
        self.assertFalse(value["factorial"]["proposal_only_steady_access"])
        self.assertEqual(
            value["auxiliary_attribution"]["cells"],
            ["control_TM", "proposal_TM"],
        )
        self.assertEqual(
            value["auxiliary_attribution"]["steady_wss_rows_read"], 0
        )
        self.assertEqual(
            value["auxiliary_attribution"]["head_output_scale"],
            "transient_train_cycle_mean_physical_vector_rms",
        )
        self.assertEqual(
            value["confirmation"]["fresh_training_seeds"],
            [20260901, 20260902, 20260903, 20260904, 20260905],
        )
        self.assertEqual(value["confirmation"]["cell_count"], 20)
        self.assertFalse(value["objective"]["steady_scale_is_loss_weight"])
        self.assertEqual(value["objective"]["steady_pair_coefficient"], 1.0)
        self.assertFalse(value["split"]["read_locked_test_fields"])
        self.assertFalse(value["split"]["read_processed_only_extra_fields"])
        self.assertIsNone(value["evaluation"]["absolute_performance_threshold"])

    def test_config_rejects_information_privilege_test_access_and_weight_tuning(self):
        mutations = (
            ("factorial", "proposal_only_steady_access", True),
            ("split", "read_locked_test_fields", True),
            ("objective", "steady_pair_coefficient", 2.0),
            ("objective", "steady_scale_is_loss_weight", True),
            ("runtime", "server", "junjinyong"),
            ("authorization", "execute_now", True),
        )
        for section, key, replacement in mutations:
            with self.subTest(section=section, key=key):
                value = config()
                value[section][key] = replacement
                with self.assertRaises(Release730MatchedTrainingError):
                    validate_config(value)

    def test_activation_accepts_only_role_consistent_selected_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            control = activation()
            write_json(path, control)
            observed = validate_activation(
                path,
                config(),
                "1" * 40,
                "selected_control",
                "transient_only",
                1103,
            )
            self.assertEqual(observed["model_family"], "release730_ghd_gps")

            proposal = activation("selected_proposal", "eligible_steady")
            write_json(path, proposal)
            observed = validate_activation(
                path,
                config(),
                "1" * 40,
                "selected_proposal",
                "eligible_steady",
                1103,
            )
            self.assertEqual(observed["selected_response_rank"], 32)

            transient_mean = activation("selected_control", "transient_mean")
            write_json(path, transient_mean)
            observed = validate_activation(
                path,
                config(),
                "1" * 40,
                "selected_control",
                "transient_mean",
                1103,
            )
            self.assertEqual(
                observed["authorized_stage"],
                "single_seed_auxiliary_compute_attribution_development",
            )

            confirmation = activation(
                "selected_proposal", "eligible_steady", 20_260_903
            )
            write_json(path, confirmation)
            observed = validate_activation(
                path,
                config(),
                "1" * 40,
                "selected_proposal",
                "eligible_steady",
                20_260_903,
            )
            self.assertEqual(
                observed["authorized_stage"],
                "five_seed_matched_information_validation_confirmation",
            )

            invalid_confirmation = activation(
                "selected_control", "transient_mean", 20_260_901
            )
            write_json(path, invalid_confirmation)
            with self.assertRaisesRegex(
                Release730MatchedTrainingError, "confirmation_seed_mode"
            ):
                validate_activation(
                    path,
                    config(),
                    "1" * 40,
                    "selected_control",
                    "transient_mean",
                    20_260_901,
                )

            proposal["response_basis_sha256"] = None
            write_json(path, proposal)
            with self.assertRaises(Release730MatchedTrainingError):
                validate_activation(
                    path,
                    config(),
                    "1" * 40,
                    "selected_proposal",
                    "eligible_steady",
                    1103,
                )

    def test_bundle_selection_and_scale_are_hash_bound_and_sealed(self):
        bundle = {
            "schema_version": "aurora.private.aneug_release_730_development_evidence_bundle.v1",
            "status": "complete_all_required_validation_development",
            "locked_test_or_extra_read": False,
            "terminal_or_result_sha256": {
                "response_oracle": "a" * 64,
                "ghd_gps": "b" * 64,
                "transolver": "c" * 64,
                "response_only": "d" * 64,
                "response_plus_residual_field": "e" * 64,
                "selected_functional_variant": "f" * 64,
            },
        }
        selection = {
            "schema_version": "aurora.private.aneug_release_730_selected_models.v1",
            "status": "complete_validation_only_selection",
            "development_evidence_bundle_sha256": None,
            "locked_test_or_79_extra_used": False,
            "absolute_performance_threshold": None,
            "selected_control_family": "release730_ghd_gps",
            "selected_proposal_family": "release730_response_plus_local_residual",
            "selected_proposal_objective": "all_field_anchored",
            "selected_proposal_rank": 32,
            "selected_response_basis_sha256": "5" * 64,
        }
        scale = {
            "schema_version": "aurora.private.aneug_release_730_steady_scale_audit_result.v1",
            "status": "complete_eligible_steady_descriptive",
            "eligible_steady_rows": 13_985,
            "steady_physical_vector_rms": 2.5,
            "transient_train_physical_vector_rms": 1.75,
            "automatic_loss_weight": None,
            "steady_wss_rows_read": 13_985,
            "model_fit_or_prediction": False,
            "validation_test_or_extra_wss_rows_read": 0,
            "gpu_used": False,
            "case_ids_included": False,
            "paper_performance_claim": False,
        }
        matched_result = {
            "schema_version": "aurora.private.aneug_release_730_matched_information_analysis_result.v1",
            "protocol_id": "aneug_release_730_matched_information_analysis_v1",
            "status": "complete",
            "evidence_role": "validation_development_matched_information_factorial",
            "paired_case_count": 73,
            "case_identifiers_included": False,
            "locked_test_or_extra_values_read": False,
            "paper_performance_claim": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle_path = root / "bundle.json"
            bundle_hash = write_json(bundle_path, bundle)
            self.assertEqual(
                validate_development_bundle(bundle_path, bundle_hash)["status"],
                "complete_all_required_validation_development",
            )
            selection["development_evidence_bundle_sha256"] = bundle_hash
            selection_path = root / "selection.json"
            selection_hash = write_json(selection_path, selection)
            proposal = activation("selected_proposal", "eligible_steady")
            observed = validate_selection_record(
                selection_path, selection_hash, proposal, bundle_hash
            )
            self.assertEqual(observed["selected_proposal_rank"], 32)
            scale_path = root / "scale.json"
            scale_hash = write_json(scale_path, scale)
            observed_scale = validate_steady_scale_result(
                scale_path, scale_hash, config()
            )
            self.assertEqual(observed_scale["steady_physical_vector_rms"], 2.5)
            matched_path = root / "matched.json"
            matched_hash = write_json(matched_path, matched_result)
            self.assertEqual(
                validate_single_seed_matched_information_result(
                    matched_path, matched_hash, config()
                )["paired_case_count"],
                73,
            )

            selection["selected_response_basis_sha256"] = "0" * 64
            changed_hash = write_json(selection_path, selection)
            with self.assertRaises(Release730MatchedTrainingError):
                validate_selection_record(
                    selection_path, changed_hash, proposal, bundle_hash
                )
            selection["selected_response_basis_sha256"] = "5" * 64

            scale["steady_wss_rows_read"] = 13_984
            changed_scale_hash = write_json(scale_path, scale)
            with self.assertRaises(Release730MatchedTrainingError):
                validate_steady_scale_result(
                    scale_path, changed_scale_hash, config()
                )

            matched_result["locked_test_or_extra_values_read"] = True
            changed_matched_hash = write_json(matched_path, matched_result)
            with self.assertRaisesRegex(
                Release730MatchedTrainingError, "single_seed_matched_result"
            ):
                validate_single_seed_matched_information_result(
                    matched_path, changed_matched_hash, config()
                )

            selection["locked_test_or_79_extra_used"] = True
            changed_hash = write_json(selection_path, selection)
            with self.assertRaises(Release730MatchedTrainingError):
                validate_selection_record(
                    selection_path, changed_hash, proposal, bundle_hash
                )

    def test_control_wrapper_applies_physical_scales_and_mode_freezing(self):
        model = MatchedCycleSingleFieldModel(
            DummyControlInner(),
            model_role="selected_control",
            model_family="release730_ghd_gps",
            cycle_output_scale=2.0,
            single_field_output_scale=3.0,
        )
        case = {
            "normalized_cycle": torch.ones(4, 5, 3),
            "single_features": torch.ones(5, 3),
        }
        torch.testing.assert_close(model.forward_cycle(case), torch.full((4, 5, 3), 2.0))
        torch.testing.assert_close(model.forward_single_field(case), torch.full((5, 3), 3.0))
        total = sum(parameter.numel() for parameter in model.parameters())
        configure_information_mode(model, "transient_only")
        self.assertLess(active_parameter_count(model), total)
        self.assertTrue(all(not p.requires_grad for p in model.single_field_head.parameters()))
        configure_information_mode(model, "eligible_steady")
        self.assertTrue(all(p.requires_grad for p in model.single_field_head.parameters()))
        configure_information_mode(model, "transient_mean")
        self.assertTrue(all(p.requires_grad for p in model.single_field_head.parameters()))

    def test_proposal_wrapper_keeps_physical_cycle_and_scales_only_steady_head(self):
        model = MatchedCycleSingleFieldModel(
            DummyProposalInner(),
            model_role="selected_proposal",
            model_family="release730_response_plus_local_residual",
            cycle_output_scale=7.0,
            single_field_output_scale=3.0,
        )
        case = {
            "physical_cycle": torch.full((4, 5, 3), 2.0),
            "single_features": torch.ones(5, 3),
        }
        torch.testing.assert_close(model.forward_cycle(case), case["physical_cycle"])
        torch.testing.assert_close(model.forward_single_field(case), torch.full((5, 3), 3.0))

    def test_exposure_digest_matches_materialized_no_replacement_prefix(self):
        indices = (2, 5, 8, 13, 21)
        rebuilt = rebuild_exposure_digest(
            indices, epochs=4, cases_per_epoch=3, seed=17
        )
        expected = exposure_prefix(indices, epochs=4, cases_per_epoch=3, seed=17)
        self.assertEqual(rebuilt.count, 12)
        self.assertEqual(rebuilt.hexdigest(), ordered_digest(expected))
        self.assertEqual(len(set(expected[:5])), 5)

    def test_transient_protocol_digest_ignores_information_mode_but_not_model(self):
        control_t = activation("selected_control", "transient_only")
        control_ts = activation("selected_control", "eligible_steady")
        self.assertEqual(
            transient_protocol_digest(config(), control_t),
            transient_protocol_digest(config(), control_ts),
        )
        control_tm = activation("selected_control", "transient_mean")
        self.assertEqual(
            transient_protocol_digest(config(), control_t),
            transient_protocol_digest(config(), control_tm),
        )
        proposal = activation("selected_proposal", "transient_only")
        self.assertNotEqual(
            transient_protocol_digest(config(), control_t),
            transient_protocol_digest(config(), proposal),
        )
        fresh_one = activation(
            "selected_control", "transient_only", 20_260_901
        )
        fresh_two = activation(
            "selected_control", "transient_only", 20_260_902
        )
        self.assertEqual(
            transient_protocol_digest(config(), fresh_one),
            transient_protocol_digest(config(), fresh_two),
        )

    def test_checkpoint_restores_exact_cell_state(self):
        model = nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)
        state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        activated = activation("selected_control", "transient_only")
        provenance = {"selected_model_decision_record_sha256": "9" * 64}
        payload = make_checkpoint(
            config=config(),
            activation=activated,
            epoch=1,
            optimizer_steps=292,
            selection_name="validation_field_relative_l2",
            selection_value=0.4,
            best_selection_value=0.4,
            best_epoch=1,
            stale_epochs=0,
            model_state_dict=state,
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            best_state_dict=state,
            history=[{"epoch": 1, "selection_value": 0.4}],
            smoke={"finite_forward_backward": True},
            train_term_normalizers=None,
            selection_endpoint_normalizers=None,
            reference_tawss_floor=1e-4,
            steady_exposure_count=0,
            steady_exposure_prefix_sha256=None,
            elapsed_seconds_accumulated=3.0,
            provenance=provenance,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            torch.save(payload, path)
            with torch.no_grad():
                for parameter in model.parameters():
                    parameter.add_(5.0)
            restored = restore_checkpoint(
                path,
                config=config(),
                activation=activated,
                expected_provenance=provenance,
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
            )
        self.assertEqual(restored["optimizer_steps"], 292)
        for key, value in model.state_dict().items():
            torch.testing.assert_close(value, state[key])

    def test_checkpoint_rejects_cross_seed_resume(self):
        model = nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2)
        activated = activation(
            "selected_control", "transient_only", 20_260_901
        )
        state = {
            key: value.detach().clone()
            for key, value in model.state_dict().items()
        }
        payload = make_checkpoint(
            config=config(),
            activation=activated,
            epoch=1,
            optimizer_steps=292,
            selection_name="validation_field_relative_l2",
            selection_value=0.4,
            best_selection_value=0.4,
            best_epoch=1,
            stale_epochs=0,
            model_state_dict=state,
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            best_state_dict=state,
            history=[{"epoch": 1}],
            smoke={},
            train_term_normalizers=None,
            selection_endpoint_normalizers=None,
            reference_tawss_floor=1e-4,
            steady_exposure_count=0,
            steady_exposure_prefix_sha256=None,
            elapsed_seconds_accumulated=1.0,
            provenance={},
        )
        self.assertEqual(payload["training_seed"], 20_260_901)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            torch.save(payload, path)
            with self.assertRaisesRegex(
                Release730MatchedTrainingError, "checkpoint_identity"
            ):
                restore_checkpoint(
                    path,
                    config=config(),
                    activation=activation(
                        "selected_control", "transient_only", 20_260_902
                    ),
                    expected_provenance={},
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                )

    def test_restore_rejects_steady_cell_with_wrong_exposure_count(self):
        model = nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2)
        activated = activation("selected_control", "eligible_steady")
        state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        payload = make_checkpoint(
            config=config(),
            activation=activated,
            epoch=1,
            optimizer_steps=292,
            selection_name="validation_field_relative_l2",
            selection_value=0.4,
            best_selection_value=0.4,
            best_epoch=1,
            stale_epochs=0,
            model_state_dict=state,
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            best_state_dict=state,
            history=[{"epoch": 1}],
            smoke={},
            train_term_normalizers=None,
            selection_endpoint_normalizers=None,
            reference_tawss_floor=1e-4,
            steady_exposure_count=584,
            steady_exposure_prefix_sha256="a" * 64,
            elapsed_seconds_accumulated=1.0,
            provenance={},
        )
        payload["steady_exposure_count"] = 583
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            torch.save(payload, path)
            with self.assertRaisesRegex(
                Release730MatchedTrainingError, "checkpoint_steady_exposure"
            ):
                restore_checkpoint(
                    path,
                    config=config(),
                    activation=activated,
                    expected_provenance={},
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                )

    def test_transient_mean_checkpoint_counts_auxiliary_without_steady_exposure(self):
        model = nn.Linear(3, 2)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2)
        activated = activation("selected_control", "transient_mean")
        state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        payload = make_checkpoint(
            config=config(),
            activation=activated,
            epoch=2,
            optimizer_steps=584,
            selection_name="validation_field_relative_l2",
            selection_value=0.4,
            best_selection_value=0.4,
            best_epoch=1,
            stale_epochs=1,
            model_state_dict=state,
            optimizer_state_dict=optimizer.state_dict(),
            scheduler_state_dict=scheduler.state_dict(),
            best_state_dict=state,
            history=[{"epoch": 1}, {"epoch": 2}],
            smoke={},
            train_term_normalizers=None,
            selection_endpoint_normalizers=None,
            reference_tawss_floor=1e-4,
            steady_exposure_count=0,
            steady_exposure_prefix_sha256=None,
            elapsed_seconds_accumulated=1.0,
            provenance={},
        )
        self.assertEqual(payload["single_field_auxiliary_examples_consumed"], 1168)
        self.assertEqual(
            payload["single_field_auxiliary_source"],
            "same_train_case_cycle_mean",
        )
        self.assertEqual(payload["steady_exposure_count"], 0)

    def test_common_loader_preserves_faces_for_steady_geometry(self):
        source = (
            ROOT / "src" / "aurora" / "aneug_release_730_ghd_gps_baseline.py"
        ).read_text(encoding="utf-8")
        self.assertIn('faces = topology["faces"]', source)
        self.assertNotIn('faces = topology.pop("faces")', source)

    def test_pbs_binds_one_symmetric_cell_without_test_or_extra_input(self):
        script = PBS_PATH.read_text(encoding="utf-8")
        self.assertIn("Qlist=a6000", script)
        self.assertIn("ngpus=1", script)
        self.assertIn("#PBS -l walltime=72:00:00", script)
        for marker in (
            "AURORA_MATCHED_ACTIVATION",
            "AURORA_MATCHED_MODEL_ROLE",
            "AURORA_MATCHED_INFORMATION_MODE",
            "AURORA_MATCHED_TRAINING_SEED",
            "AURORA_DEVELOPMENT_EVIDENCE_BUNDLE",
            "AURORA_SELECTED_MODEL_RECORD",
            "AURORA_STEADY_SCALE_RESULT",
            "AURORA_PRIVATE_OVERLAP_RESULT",
            "AURORA_MATCHED_RESUME_CHECKPOINT",
            "AURORA_MATCHED_PRIOR_ATTEMPT_TERMINAL_RECORD",
            "AURORA_SINGLE_SEED_MATCHED_INFORMATION_RESULT",
        ):
            self.assertIn(marker, script)
        self.assertIn("--response-basis", script)
        self.assertIn("--resume-checkpoint", script)
        self.assertIn("--prior-attempt-terminal-record", script)
        self.assertIn("--multiseed-confirmation-config", script)
        self.assertNotIn("junjinyong", script)
        self.assertNotIn("test_manifest", script)
        self.assertNotIn("processed_only", script)


if __name__ == "__main__":
    unittest.main()
