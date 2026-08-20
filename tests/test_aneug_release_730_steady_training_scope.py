from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_steady_training_scope import (
    SteadyTrainingScopeError,
    load_config,
    validate_config,
    validate_scope_payloads,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_steady_training_scope_v1.json"


class SteadyTrainingScopeTests(unittest.TestCase):
    def test_config_requires_matched_roles_without_fixing_development(self) -> None:
        config = load_config(CONFIG)
        control = config["information_control"]
        self.assertTrue(control["same_eligible_indices_for_both_roles"])
        self.assertFalse(control["proposal_only_steady_labels"])
        self.assertFalse(control["steady_supervision_is_novelty"])
        self.assertFalse(control["training_schedule_fixed_here"])
        self.assertFalse(control["architecture_fixed_here"])

    def test_proposal_privilege_or_schedule_freeze_is_rejected(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        for key, value in (
            ("proposal_only_steady_labels", True),
            ("same_eligible_indices_for_both_roles", False),
            ("training_schedule_fixed_here", True),
            ("architecture_fixed_here", True),
        ):
            changed = copy.deepcopy(config)
            changed["information_control"][key] = value
            with self.subTest(key=key), self.assertRaises(SteadyTrainingScopeError):
                validate_config(changed)

    def test_scope_payload_alignment_uses_metadata_only(self) -> None:
        config = load_config(CONFIG)
        count = config["scope"]["processed_steady_rows"]
        eligible_count = config["scope"]["eligible_steady_rows"]
        names = [f"case_{index:05d}" for index in range(count)]
        indices = list(range(eligible_count))
        eligible = [names[index] for index in indices]
        digest = hashlib.sha256("\n".join(sorted(eligible)).encode()).hexdigest()
        synthetic = copy.deepcopy(config)
        synthetic["scope"]["eligible_case_digest"] = digest
        public = {
            "status": "complete",
            "case_ids_public": False,
            "steady_case_count": count,
            "eligible_steady_case_count": eligible_count,
            "excluded_steady_case_count": count - eligible_count,
            "eligible_steady_case_digest": digest,
            "steady_wss_values_read": False,
            "transient_wss_values_read": False,
            "locked_test_wss_values_read": False,
            "processed_only_extra_wss_values_read": False,
        }
        private = {
            "schema_version": "aurora.private.aneug_release_730_steady_overlap_audit.v1",
            "any_wss_value_read": False,
            "test_wss_opened": False,
            "steady_case_names": names,
            "eligible_steady_indices": indices,
            "eligible_steady_case_names": eligible,
        }
        archive = {
            "case_name": names,
            "tensor": torch.empty((count, 13_902, 9), device="meta"),
            "ghd_dict": {"ghd": torch.empty((count, 432), device="meta")},
            "label": [
                "x",
                "y",
                "z",
                "x_normal",
                "y_normal",
                "z_normal",
                "wss_x",
                "wss_y",
                "wss_z",
            ],
        }
        self.assertEqual(
            validate_scope_payloads(synthetic, public, private, archive),
            tuple(indices),
        )

    def test_index_name_misalignment_is_rejected(self) -> None:
        config = load_config(CONFIG)
        count = config["scope"]["processed_steady_rows"]
        names = [f"case_{index:05d}" for index in range(count)]
        private = {
            "schema_version": "aurora.private.aneug_release_730_steady_overlap_audit.v1",
            "any_wss_value_read": False,
            "test_wss_opened": False,
            "steady_case_names": names,
            "eligible_steady_indices": list(range(13_985)),
            "eligible_steady_case_names": list(reversed(names[:13_985])),
        }
        public = {
            "status": "complete",
            "case_ids_public": False,
            "steady_case_count": count,
            "eligible_steady_case_count": 13_985,
            "excluded_steady_case_count": 407,
            "eligible_steady_case_digest": config["scope"]["eligible_case_digest"],
            "steady_wss_values_read": False,
            "transient_wss_values_read": False,
            "locked_test_wss_values_read": False,
            "processed_only_extra_wss_values_read": False,
        }
        archive = {
            "case_name": names,
            "tensor": torch.empty((count, 13_902, 9), device="meta"),
            "ghd_dict": {"ghd": torch.empty((count, 432), device="meta")},
            "label": [
                "x", "y", "z", "x_normal", "y_normal", "z_normal",
                "wss_x", "wss_y", "wss_z",
            ],
        }
        with self.assertRaises(SteadyTrainingScopeError):
            validate_scope_payloads(config, public, private, archive)


if __name__ == "__main__":
    unittest.main()
