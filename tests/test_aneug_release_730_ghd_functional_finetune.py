import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import torch
from torch import nn

from aurora.aneug_release_730_ghd_functional_finetune import (
    AUTHORIZED_STAGE,
    OBJECTIVE_VARIANTS,
    PhysicalGHDGPSCycle,
    Release730GHDFunctionalFinetuneError,
    make_checkpoint,
    validate_activation,
    validate_config,
    validate_predecessors,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = (
    ROOT / "configs" / "aneug_release_730_ghd_functional_finetune_v1.json"
)
PBS_PATH = (
    ROOT / "cluster" / "pbs_aneug_release_730_ghd_functional_finetune_v1.pbs"
)


def config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def activation(objective="all_field_anchored", server="introai9"):
    value = config()
    return {
        "schema_version": "aurora.private.aneug_release_730_ghd_functional_finetune_activation.v1",
        "protocol_id": value["protocol_id"],
        "public_commit": "1" * 40,
        "quality_conclusion": "success",
        "quality_run_id": 123,
        "authorized_stage": AUTHORIZED_STAGE,
        "objective_variant": objective,
        "training_seed": 1103,
        "server": server,
        "queue": value["runtime"]["queue_by_server"][server],
        "single_server_per_activation": True,
        "duplicate_scientific_cell_across_accounts": False,
        "initial_checkpoint_sha256": value["source"][
            "ghd_gps_best_checkpoint_sha256"
        ],
        "ghd_gps_result_sha256": value["source"]["ghd_gps_result_sha256"],
        "ghd_gps_terminal_status_sha256": value["source"][
            "ghd_gps_terminal_status_sha256"
        ],
        "private_split_manifest_sha256": value["split"][
            "private_manifest_sha256"
        ],
        "private_train_audit_sha256": value["split"][
            "train_audit_private_sha256"
        ],
        "read_locked_test_or_extra": False,
        "continuation_mode": False,
        "resume_checkpoint_sha256": None,
        "prior_attempt_terminal_record_sha256": None,
    }


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DummyBackbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.gain = nn.Parameter(torch.tensor(2.0))

    def forward(self, case):
        return case["normalized"] * self.gain


class GHDFunctionalFinetuneTests(unittest.TestCase):
    def test_config_freezes_common_objective_selection_and_sealed_scope(self):
        value = config()
        validate_config(value)
        self.assertEqual(tuple(value["objective"]["variants"]), OBJECTIVE_VARIANTS)
        self.assertEqual(
            value["objective"]["checkpoint_selection"],
            "common_field_plus_mean_of_mean_vector_tawss_and_osi_for_every_objective_variant",
        )
        self.assertEqual(value["split"]["train_cases"], 584)
        self.assertEqual(value["split"]["validation_cases"], 73)
        self.assertFalse(value["split"]["read_locked_test_fields"])
        self.assertFalse(value["split"]["read_processed_only_extra_fields"])
        self.assertIsNone(value["evaluation"]["absolute_performance_threshold"])

    def test_config_rejects_test_access_variant_drift_and_separate_head(self):
        mutations = (
            ("split", "read_locked_test_fields", True),
            ("objective", "variants", ["field_only"]),
            ("objective", "separate_functional_head", True),
            ("authorization", "execute_now", True),
        )
        for section, key, replacement in mutations:
            with self.subTest(section=section, key=key):
                value = config()
                value[section][key] = replacement
                with self.assertRaises(Release730GHDFunctionalFinetuneError):
                    validate_config(value)

    def test_activation_is_objective_server_and_checkpoint_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            value = activation("all_scalarized", "junjinyong")
            write_json(path, value)
            observed = validate_activation(
                path, config(), "1" * 40, "junjinyong", "all_scalarized"
            )
            self.assertEqual(observed["authorized_stage"], AUTHORIZED_STAGE)

            value["read_locked_test_or_extra"] = True
            write_json(path, value)
            with self.assertRaises(Release730GHDFunctionalFinetuneError):
                validate_activation(
                    path, config(), "1" * 40, "junjinyong", "all_scalarized"
                )

    def test_physical_cycle_has_no_auxiliary_prediction_head(self):
        model = PhysicalGHDGPSCycle(DummyBackbone(), 3.0)
        output = model.forward_cycle({"normalized": torch.ones(2, 4, 3)})
        self.assertTrue(torch.equal(output, torch.full((2, 4, 3), 6.0)))
        self.assertEqual(sum(parameter.numel() for parameter in model.parameters()), 1)

    def test_predecessor_validation_is_hash_bound_and_terminal(self):
        value = config()
        result = {
            "schema_version": "aurora.private.aneug_release_730_ghd_gps_result.v1",
            "protocol_id": "aneug_release_730_ghd_gps_baseline_v1",
            "status": "complete",
            "seed": 1103,
            "best_epoch": 20,
            "validation_case_count": 73,
            "validation_case_digest": value["split"]["validation_case_digest"],
            "validation_loader_order_sha256": value["split"][
                "validation_loader_order_sha256"
            ],
            "validation": {"aggregate": {"field_relative_l2": 0.2}},
        }
        status = {"job_id": "synthetic", "exit_code": 0, "complete": True}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result_path = root / "result.json"
            status_path = root / "status.json"
            value["source"]["ghd_gps_result_sha256"] = write_json(
                result_path, result
            )
            value["source"]["ghd_gps_terminal_status_sha256"] = write_json(
                status_path, status
            )
            observed, observed_status = validate_predecessors(
                value, result_path, status_path
            )
            self.assertEqual(observed["best_epoch"], 20)
            self.assertEqual(observed_status["exit_code"], 0)

    def test_checkpoint_records_common_selection_and_exact_provenance(self):
        payload = make_checkpoint(
            config=config(),
            objective_variant="field_only",
            epoch=1,
            optimizer_steps=292,
            selection_value=2.0,
            best_selection_value=2.0,
            best_epoch=1,
            stale_epochs=0,
            model_state_dict={"weight": torch.tensor([1.0])},
            optimizer_state_dict={"state": {}, "param_groups": []},
            scheduler_state_dict={"last_epoch": 1},
            best_state_dict={"weight": torch.tensor([1.0])},
            history=[{"epoch": 1}],
            smoke={"finite_forward_backward": True},
            train_term_normalizers={
                "field": 1.0,
                "mean_vector": 1.0,
                "tawss": 1.0,
                "osi": 1.0,
            },
            selection_endpoint_normalizers={
                "field": 1.0,
                "mean_vector": 1.0,
                "tawss": 1.0,
                "osi": 1.0,
            },
            initial_validation={"aggregate": {}},
            reference_tawss_floor=1e-4,
            elapsed_seconds_accumulated=1.0,
            provenance={"public_commit": "1" * 40},
        )
        self.assertEqual(
            payload["selection_name"],
            "common_initial_checkpoint_endpoint_normalized_validation_utility",
        )
        self.assertEqual(payload["public_commit"], "1" * 40)

        initial_payload = make_checkpoint(
            config=config(),
            objective_variant="all_field_anchored",
            epoch=1,
            optimizer_steps=292,
            selection_value=2.1,
            best_selection_value=2.0,
            best_epoch=0,
            stale_epochs=1,
            model_state_dict={"weight": torch.tensor([0.9])},
            optimizer_state_dict={"state": {}, "param_groups": []},
            scheduler_state_dict={"last_epoch": 1},
            best_state_dict={"weight": torch.tensor([1.0])},
            history=[{"epoch": 1}],
            smoke={"finite_forward_backward": True},
            train_term_normalizers={
                "field": 1.0,
                "mean_vector": 1.0,
                "tawss": 1.0,
                "osi": 1.0,
            },
            selection_endpoint_normalizers={
                "field": 1.0,
                "mean_vector": 1.0,
                "tawss": 1.0,
                "osi": 1.0,
            },
            initial_validation={"aggregate": {}},
            reference_tawss_floor=1e-4,
            elapsed_seconds_accumulated=1.0,
            provenance={"public_commit": "1" * 40},
        )
        self.assertEqual(initial_payload["best_epoch"], 0)

    def test_pbs_sidecar_has_no_locked_test_or_extra_argument(self):
        text = PBS_PATH.read_text(encoding="utf-8")
        self.assertIn("AURORA_GHD_INITIAL_CHECKPOINT", text)
        self.assertIn("--objective-variant", text)
        self.assertIn("--expected-execution-server", text)
        self.assertNotIn("--locked-test", text)
        self.assertNotIn("--processed-only-extra", text)


if __name__ == "__main__":
    unittest.main()
