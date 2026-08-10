from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.source_watch import (
    SourceWatchContractError,
    evaluate_config,
    evaluate_snapshot,
    load_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "source_watch_v1.json"
CONFIG_V2 = ROOT / "configs" / "source_watch_v2.json"


class SourceWatchContractTests(unittest.TestCase):
    def test_reference_snapshot_is_readme_only_and_authorizes_nothing(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["status"], "watch_only")
        self.assertEqual(config["frozen_snapshot"]["root_entries"][0]["name"], "README.md")
        self.assertEqual(config["frozen_snapshot"]["release_count"], 0)
        self.assertIsNone(config["frozen_snapshot"]["license_spdx_id"])
        self.assertFalse(config["authorization"]["automatic_download"])
        self.assertFalse(config["authorization"]["automatic_p0_registration"])
        self.assertFalse(config["authorization"]["gpu_training"])
        self.assertEqual(config["execution_boundary"]["scientific_execution_server"], "introai9")
        self.assertEqual(config["execution_boundary"]["excluded_server"], "junjinyong")

    def test_frozen_snapshot_produces_no_change_signal(self) -> None:
        config = load_config(CONFIG)
        observed = {
            key: copy.deepcopy(config["frozen_snapshot"][key])
            for key in (
                "main_head_sha",
                "root_entries",
                "release_count",
                "license_spdx_id",
                "repository_size_kib",
                "payload_or_code_entries",
            )
        }
        result = evaluate_snapshot(config, observed)
        self.assertTrue(result["same_as_frozen_snapshot"])
        self.assertFalse(result["fresh_source_reaudit_triggered"])
        self.assertEqual(result["next_action"], "continue_watch_only")
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_material_change_triggers_only_fresh_source_reaudit(self) -> None:
        config = load_config(CONFIG)
        observed = copy.deepcopy(config["frozen_snapshot"])
        observed["main_head_sha"] = "f" * 40
        observed["root_entries"].append({"name": "data", "type": "dir", "size": 0})
        observed["payload_or_code_entries"] = ["data"]
        observed["release_count"] = 1
        observed["license_spdx_id"] = "CC-BY-NC-4.0"
        result = evaluate_snapshot(config, observed)
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertEqual(result["next_action"], "fresh_source_reaudit_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_authorization_relaxation_is_rejected(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["authorization"]["gpu_training"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v2_frozen_snapshots_authorize_nothing(self) -> None:
        config = load_config(CONFIG_V2)
        self.assertEqual(
            [watch["watch_id"] for watch in config["watches"]],
            ["iavs_public_release_v1", "topbrain2_material_release_v1"],
        )
        topbrain = config["watches"][1]["frozen_snapshot"]
        self.assertEqual(topbrain["zenodo_license_id"], "cc-by-4.0")
        self.assertEqual(topbrain["payload_or_manifest_files"], [])
        self.assertTrue(topbrain["challenge_under_construction"])
        self.assertTrue(topbrain["challenge_join_registration_available"])
        self.assertFalse(config["authorization"]["automatic_download"])
        self.assertFalse(config["authorization"]["gpu_training"])
        self.assertEqual(
            config["execution_boundary"]["scientific_execution_server"], "introai9"
        )
        self.assertEqual(config["execution_boundary"]["excluded_server"], "junjinyong")

    def test_v2_frozen_observations_continue_watch_only(self) -> None:
        config = load_config(CONFIG_V2)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["fresh_source_reaudit_triggered"])
        self.assertEqual(result["next_action"], "continue_watch_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_topbrain_material_change_opens_only_source_reaudit(self) -> None:
        config = load_config(CONFIG_V2)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        topbrain = observations["topbrain2_material_release_v1"]
        topbrain["zenodo_modified"] = "2026-08-10T00:00:00+00:00"
        topbrain["zenodo_revision"] = 5
        topbrain["zenodo_files"].append(
            {
                "key": "topbrain2_manifest.json",
                "size": 1024,
                "checksum": "md5:" + "f" * 32,
            }
        )
        topbrain["payload_or_manifest_files"] = ["topbrain2_manifest.json"]
        topbrain["challenge_under_construction"] = False
        topbrain["challenge_material_navigation_entries"] = [
            "data|/topbrain2026/data/"
        ]
        result = evaluate_config(config, observations)
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertEqual(result["next_action"], "fresh_source_reaudit_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v2_authorization_relaxation_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V2.read_text(encoding="utf-8"))
        payload["authorization"]["gpu_training"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)


if __name__ == "__main__":
    unittest.main()
