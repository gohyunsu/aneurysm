from __future__ import annotations

import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import audit_source_watch
from aurora.source_watch import (
    SourceWatchContractError,
    evaluate_config,
    evaluate_snapshot,
    load_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "source_watch_v1.json"
CONFIG_V2 = ROOT / "configs" / "source_watch_v2.json"
CONFIG_V3 = ROOT / "configs" / "source_watch_v3.json"
CONFIG_V4 = ROOT / "configs" / "source_watch_v4.json"
CONFIG_V5 = ROOT / "configs" / "source_watch_v5.json"
WORKFLOW = ROOT / ".github" / "workflows" / "source-watch.yml"


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

    def test_v3_frozen_snapshots_require_no_manual_review(self) -> None:
        config = load_config(CONFIG_V3)
        self.assertEqual(
            [watch["watch_id"] for watch in config["watches"]],
            [
                "iavs_public_release_v1",
                "topbrain2_material_release_v1",
                "trellis_stated_code_availability_v1",
            ],
        )
        trellis = config["watches"][2]
        self.assertEqual(trellis["frozen_snapshot"]["repository_api_http_status"], 404)
        self.assertFalse(trellis["frozen_snapshot"]["repository_available"])
        self.assertEqual(
            trellis["review_request"],
            "direct_prior_baseline_feasibility_reaudit_only",
        )
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertFalse(result["fresh_source_reaudit_triggered"])
        self.assertFalse(
            result["direct_prior_baseline_feasibility_reaudit_triggered"]
        )
        self.assertEqual(result["manual_review_requests"], [])
        self.assertEqual(result["next_action"], "continue_watch_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_trellis_code_appearance_opens_only_baseline_review(self) -> None:
        config = load_config(CONFIG_V3)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observations["trellis_stated_code_availability_v1"] = {
            "repository_api_http_status": 200,
            "repository_available": True,
            "default_branch": "main",
            "main_head_sha": "f" * 40,
            "root_entries": [
                {"name": "src", "type": "dir", "size": 0},
                {"name": "LICENSE", "type": "file", "size": 11357},
            ],
            "release_count": 1,
            "license_spdx_id": "Apache-2.0",
            "repository_size_kib": 512,
            "payload_or_code_entries": ["src"],
            "availability": "publicly_readable_repository",
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertFalse(result["fresh_source_reaudit_triggered"])
        self.assertTrue(
            result["direct_prior_baseline_feasibility_reaudit_triggered"]
        )
        self.assertEqual(
            result["manual_review_requests"],
            ["direct_prior_baseline_feasibility_reaudit_only"],
        )
        self.assertEqual(result["next_action"], "manual_review_signal_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v3_source_and_direct_prior_changes_remain_manual_only(self) -> None:
        config = load_config(CONFIG_V3)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observations["iavs_public_release_v1"]["main_head_sha"] = "e" * 40
        observations["iavs_public_release_v1"]["root_entries"].append(
            {"name": "code", "type": "dir", "size": 0}
        )
        observations["iavs_public_release_v1"]["payload_or_code_entries"] = [
            "code"
        ]
        observations["trellis_stated_code_availability_v1"][
            "repository_api_http_status"
        ] = 200
        observations["trellis_stated_code_availability_v1"][
            "repository_available"
        ] = True
        result = evaluate_config(config, observations)
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertTrue(
            result["direct_prior_baseline_feasibility_reaudit_triggered"]
        )
        self.assertEqual(
            result["manual_review_requests"],
            [
                "direct_prior_baseline_feasibility_reaudit_only",
                "fresh_source_reaudit_only",
            ],
        )
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v3_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V3.read_text(encoding="utf-8"))
        payload["watches"][2]["frozen_snapshot"]["repository_available"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SourceWatchContractError, "trellis"):
                load_config(candidate)

        payload = json.loads(CONFIG_V3.read_text(encoding="utf-8"))
        payload["authorization"]["architecture_selection"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v4_frozen_snapshots_include_aneumo_without_authority(self) -> None:
        config = load_config(CONFIG_V4)
        self.assertEqual(
            [watch["watch_id"] for watch in config["watches"]],
            [
                "iavs_public_release_v1",
                "topbrain2_material_release_v1",
                "trellis_stated_code_availability_v1",
                "aneumo_github_material_release_v1",
                "aneumo_huggingface_material_release_v1",
            ],
        )
        github = config["watches"][3]["frozen_snapshot"]
        huggingface = config["watches"][4]["frozen_snapshot"]
        self.assertEqual(
            github["main_head_sha"],
            "701d53dde3489d84dbe9bc8324254629162eb45a",
        )
        self.assertIsNone(github["license_spdx_id"])
        self.assertEqual(
            huggingface["sha"], "f801adee816c18d3e18b23e6fcb147fe4c264209"
        )
        self.assertEqual(huggingface["sibling_count"], 370)
        self.assertEqual(huggingface["real_case_or_mapping_entries"], [])
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertEqual(result["next_action"], "continue_watch_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v4_aneumo_real_case_marker_opens_only_source_reaudit(self) -> None:
        config = load_config(CONFIG_V4)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        huggingface = observations["aneumo_huggingface_material_release_v1"]
        huggingface["sha"] = "a" * 40
        huggingface["sibling_count"] += 1
        huggingface["siblings_sha256"] = "b" * 64
        huggingface["real_case_or_mapping_entries"] = [
            "real_cases_with_cfd_mapping.csv"
        ]
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertFalse(
            result["direct_prior_baseline_feasibility_reaudit_triggered"]
        )
        self.assertEqual(result["manual_review_requests"], ["fresh_source_reaudit_only"])
        self.assertEqual(result["next_action"], "manual_review_signal_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v4_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V4.read_text(encoding="utf-8"))
        payload["watches"][4]["frozen_snapshot"]["sibling_count"] = 371
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SourceWatchContractError, "huggingface"):
                load_config(candidate)

        payload = json.loads(CONFIG_V4.read_text(encoding="utf-8"))
        payload["authorization"]["automatic_p0_registration"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v5_frozen_snapshots_add_material_sources_without_authority(self) -> None:
        config = load_config(CONFIG_V5)
        self.assertEqual(config["extends"], "source_watch_v4.json")
        self.assertEqual(len(config["watches"]), 9)
        self.assertEqual(
            [watch["watch_id"] for watch in config["watches"][-4:]],
            [
                "aneug_huggingface_material_revision_v1",
                "aneurisk_zenodo_material_revision_v1",
                "largeia_zenodo_access_revision_v1",
                "topaneu_material_release_v1",
            ],
        )
        aneug, aneurisk, largeia, topaneu = config["watches"][-4:]
        self.assertEqual(
            aneug["frozen_snapshot"]["sha"],
            "9dd418083899deddd93a67f9a6fca7a14304fa36",
        )
        self.assertEqual(aneurisk["frozen_snapshot"]["zenodo_revision"], 4)
        self.assertEqual(
            aneurisk["frozen_snapshot"]["zenodo_files"][0]["size"],
            1430889142,
        )
        self.assertEqual(
            largeia["frozen_snapshot"]["zenodo_access_right"], "restricted"
        )
        self.assertEqual(largeia["frozen_snapshot"]["zenodo_files"], [])
        self.assertFalse(
            topaneu["frozen_snapshot"]["challenge_under_construction"]
        )
        self.assertEqual(
            topaneu["frozen_snapshot"]["challenge_material_navigation_entries"],
            [
                "data|https://topaneu-26.grand-challenge.org/data/",
                "evaluation|https://topaneu-26.grand-challenge.org/evaluation/",
            ],
        )
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertEqual(result["next_action"], "continue_watch_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v5_material_changes_request_only_fresh_source_reaudit(self) -> None:
        config = load_config(CONFIG_V5)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observations["aneug_huggingface_material_revision_v1"]["sha"] = "f" * 40
        observations["largeia_zenodo_access_revision_v1"][
            "zenodo_access_right"
        ] = "open"
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertEqual(
            result["manual_review_requests"], ["fresh_source_reaudit_only"]
        )
        self.assertEqual(result["next_action"], "manual_review_signal_only")
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v5_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V5.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["sha"] = "e" * 40
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            (source / "source_watch_v4.json").write_text(
                CONFIG_V4.read_text(encoding="utf-8"), encoding="utf-8"
            )
            with self.assertRaisesRegex(SourceWatchContractError, "aneug"):
                load_config(candidate)

        payload = json.loads(CONFIG_V5.read_text(encoding="utf-8"))
        payload["authorization"]["automatic_terms_acceptance"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            (source / "source_watch_v4.json").write_text(
                CONFIG_V4.read_text(encoding="utf-8"), encoding="utf-8"
            )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v5_workflow_is_read_only_scheduled_and_fail_closed(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('cron: "17 2 * * 1,4"', workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("configs/source_watch_v5.json", workflow)
        self.assertIn("--fetch --fail-on-change", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("introai9", workflow)
        self.assertNotIn("junjinyong", workflow)
        self.assertNotIn("ssh ", workflow)

    def test_fail_on_change_cli_returns_three_without_authorizing_compute(self) -> None:
        config = load_config(CONFIG_V3)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        trellis = observations["trellis_stated_code_availability_v1"]
        trellis["repository_api_http_status"] = 200
        trellis["repository_available"] = True

        def fake_fetch(watch: dict[str, object]) -> dict[str, object]:
            return observations[str(watch["watch_id"])]

        output = io.StringIO()
        with mock.patch.object(
            audit_source_watch, "fetch_watch_snapshot", side_effect=fake_fetch
        ), contextlib.redirect_stdout(output):
            exit_code = audit_source_watch.main(
                [
                    "--config",
                    str(CONFIG_V3),
                    "--fetch",
                    "--fail-on-change",
                ]
            )
        result = json.loads(output.getvalue())
        self.assertEqual(exit_code, 3)
        self.assertTrue(result["manual_review_triggered"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])


if __name__ == "__main__":
    unittest.main()
