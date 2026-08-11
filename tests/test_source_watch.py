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
CONFIG_V6 = ROOT / "configs" / "source_watch_v6.json"
CONFIG_V7 = ROOT / "configs" / "source_watch_v7.json"
CONFIG_V8 = ROOT / "configs" / "source_watch_v8.json"
CONFIG_V9 = ROOT / "configs" / "source_watch_v9.json"
CONFIG_V10 = ROOT / "configs" / "source_watch_v10.json"
CONFIG_V11 = ROOT / "configs" / "source_watch_v11.json"
CONFIG_V12 = ROOT / "configs" / "source_watch_v12.json"
CONFIG_V13 = ROOT / "configs" / "source_watch_v13.json"
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

    def test_v6_adds_gated_aneux_transient_metadata_without_authority(self) -> None:
        config = load_config(CONFIG_V6)
        self.assertEqual(config["extends"], "source_watch_v5.json")
        self.assertEqual(len(config["watches"]), 10)
        transient = config["watches"][-1]
        self.assertEqual(
            transient["watch_id"], "aneux_transient_cfd_material_revision_v1"
        )
        frozen = transient["frozen_snapshot"]
        self.assertEqual(
            frozen["sha"], "38c574bc54a1ead9a4830da09ae5087e42b9d6c2"
        )
        self.assertEqual(frozen["gated"], "manual")
        self.assertEqual(frozen["sibling_count"], 1940)
        self.assertEqual(frozen["bifurcation_case_folders"], 180)
        self.assertEqual(frozen["sidewall_case_folders"], 143)
        self.assertEqual(frozen["unique_visible_case_ids"], 322)
        self.assertEqual(frozen["cross_topology_overlap_ids"], ["SNF365"])
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

    def test_v6_manifest_change_requests_source_reaudit_only(self) -> None:
        config = load_config(CONFIG_V6)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observed = observations["aneux_transient_cfd_material_revision_v1"]
        observed["sha"] = "f" * 40
        observed["unique_visible_case_ids"] = 323
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertEqual(
            result["manual_review_requests"], ["fresh_source_reaudit_only"]
        )
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v6_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V6.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"][
            "unique_visible_case_ids"
        ] = 323
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            (source / "source_watch_v5.json").write_text(
                CONFIG_V5.read_text(encoding="utf-8"), encoding="utf-8"
            )
            (source / "source_watch_v4.json").write_text(
                CONFIG_V4.read_text(encoding="utf-8"), encoding="utf-8"
            )
            with self.assertRaisesRegex(SourceWatchContractError, "aneux_transient"):
                load_config(candidate)

        payload = json.loads(CONFIG_V6.read_text(encoding="utf-8"))
        payload["authorization"]["automatic_terms_acceptance"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            (source / "source_watch_v5.json").write_text(
                CONFIG_V5.read_text(encoding="utf-8"), encoding="utf-8"
            )
            (source / "source_watch_v4.json").write_text(
                CONFIG_V4.read_text(encoding="utf-8"), encoding="utf-8"
            )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v6_workflow_is_read_only_scheduled_and_fail_closed(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('cron: "17 2 * * 1,4"', workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("configs/source_watch_v13.json", workflow)
        self.assertIn("--fetch --fail-on-change", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("introai9", workflow)
        self.assertNotIn("junjinyong", workflow)
        self.assertNotIn("ssh ", workflow)

    def test_v7_adds_partial_pointflownet_baseline_without_authority(self) -> None:
        config = load_config(CONFIG_V7)
        self.assertEqual(config["extends"], "source_watch_v6.json")
        self.assertEqual(len(config["watches"]), 11)
        pointflownet = config["watches"][-1]
        self.assertEqual(pointflownet["watch_id"], "pointflownet_baseline_release_v1")
        self.assertEqual(
            pointflownet["review_request"],
            "direct_prior_baseline_feasibility_reaudit_only",
        )
        frozen = pointflownet["frozen_snapshot"]
        self.assertEqual(
            frozen["main_head_sha"],
            "5cb4f2545d25b6e8b855806cb3a345b8b1d72594",
        )
        self.assertEqual(frozen["release_count"], 0)
        self.assertIsNone(frozen["license_spdx_id"])
        self.assertEqual(frozen["root_entries"][6]["name"], "README.md")
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
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v7_pointflownet_change_requests_baseline_review_only(self) -> None:
        config = load_config(CONFIG_V7)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observed = observations["pointflownet_baseline_release_v1"]
        observed["main_head_sha"] = "f" * 40
        observed["license_spdx_id"] = "MIT"
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
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v7_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V7.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["release_count"] = 1
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            (source / "source_watch_v6.json").write_text(
                CONFIG_V6.read_text(encoding="utf-8"), encoding="utf-8"
            )
            (source / "source_watch_v5.json").write_text(
                CONFIG_V5.read_text(encoding="utf-8"), encoding="utf-8"
            )
            (source / "source_watch_v4.json").write_text(
                CONFIG_V4.read_text(encoding="utf-8"), encoding="utf-8"
            )
            with self.assertRaisesRegex(SourceWatchContractError, "pointflownet"):
                load_config(candidate)

        payload = json.loads(CONFIG_V7.read_text(encoding="utf-8"))
        payload["authorization"]["gpu_training"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            (source / "source_watch_v6.json").write_text(
                CONFIG_V6.read_text(encoding="utf-8"), encoding="utf-8"
            )
            (source / "source_watch_v5.json").write_text(
                CONFIG_V5.read_text(encoding="utf-8"), encoding="utf-8"
            )
            (source / "source_watch_v4.json").write_text(
                CONFIG_V4.read_text(encoding="utf-8"), encoding="utf-8"
            )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v8_adds_readme_only_aaa_wss_baseline_without_authority(self) -> None:
        config = load_config(CONFIG_V8)
        self.assertEqual(config["extends"], "source_watch_v7.json")
        self.assertEqual(len(config["watches"]), 12)
        aaa_wss = config["watches"][-1]
        self.assertEqual(
            aaa_wss["watch_id"],
            "aaa_wss_neural_surrogate_baseline_release_v1",
        )
        self.assertEqual(
            aaa_wss["review_request"],
            "direct_prior_baseline_feasibility_reaudit_only",
        )
        frozen = aaa_wss["frozen_snapshot"]
        self.assertEqual(
            frozen["main_head_sha"],
            "2f78bf1879e5e555c3369d91822be3f567f9fbd1",
        )
        self.assertEqual(frozen["root_entries"], [
            {"name": "README.md", "type": "file", "size": 183}
        ])
        self.assertEqual(frozen["release_count"], 0)
        self.assertIsNone(frozen["license_spdx_id"])
        self.assertEqual(frozen["payload_or_code_entries"], [])

        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v8_aaa_wss_code_change_requests_baseline_review_only(self) -> None:
        config = load_config(CONFIG_V8)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observed = observations[
            "aaa_wss_neural_surrogate_baseline_release_v1"
        ]
        observed["main_head_sha"] = "e" * 40
        observed["root_entries"].append(
            {"name": "src", "type": "dir", "size": 0}
        )
        observed["payload_or_code_entries"] = ["src"]
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
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v8_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V8.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["release_count"] = 1
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (CONFIG_V7, CONFIG_V6, CONFIG_V5, CONFIG_V4):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "aaa_wss"):
                load_config(candidate)

        payload = json.loads(CONFIG_V8.read_text(encoding="utf-8"))
        payload["authorization"]["gpu_training"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (CONFIG_V7, CONFIG_V6, CONFIG_V5, CONFIG_V4):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v9_adds_mris_postreview_watch_without_authority(self) -> None:
        config = load_config(CONFIG_V9)
        self.assertEqual(config["extends"], "source_watch_v8.json")
        self.assertEqual(len(config["watches"]), 13)
        mris = config["watches"][-1]
        self.assertEqual(
            mris["watch_id"], "mris_bench_postreview_target_contract_v1"
        )
        self.assertEqual(mris["review_request"], "fresh_source_reaudit_only")
        frozen = mris["frozen_snapshot"]
        self.assertEqual(
            frozen["sha"], "6f2d6d9ad10eba68700ce95c7523ec78934f7a3d"
        )
        self.assertEqual(frozen["sibling_count"], 12)
        self.assertEqual(frozen["arrow_shard_count"], 8)
        self.assertTrue(frozen["under_review_release_statement_present"])

        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v9_postreview_change_requests_source_reaudit_only(self) -> None:
        config = load_config(CONFIG_V9)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observed = observations["mris_bench_postreview_target_contract_v1"]
        observed["sha"] = "d" * 40
        observed["description_sha256"] = "e" * 64
        observed["under_review_release_statement_present"] = False
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertFalse(
            result["direct_prior_baseline_feasibility_reaudit_triggered"]
        )
        self.assertEqual(
            result["manual_review_requests"], ["fresh_source_reaudit_only"]
        )
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v9_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V9.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["arrow_shard_count"] = 9
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "mris_bench"):
                load_config(candidate)

        payload = json.loads(CONFIG_V9.read_text(encoding="utf-8"))
        payload["authorization"]["automatic_download"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v10_adds_topaneu_versioned_release_watch_without_authority(self) -> None:
        config = load_config(CONFIG_V10)
        self.assertEqual(config["extends"], "source_watch_v9.json")
        self.assertEqual(len(config["watches"]), 14)
        topaneu = config["watches"][-1]
        self.assertEqual(
            topaneu["watch_id"], "topaneu_github_release_contract_v2"
        )
        self.assertEqual(topaneu["review_request"], "fresh_source_reaudit_only")
        frozen = topaneu["frozen_snapshot"]
        self.assertEqual(
            frozen["main_head_sha"],
            "018c243445f99199f484018c4c80575c84c72293",
        )
        self.assertEqual(frozen["current_manifest_counts"]["location_json_count"], 417)
        self.assertEqual(frozen["batch1_manifest_counts"]["location_json_count"], 98)

        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v10_topaneu_change_requests_source_reaudit_only(self) -> None:
        config = load_config(CONFIG_V10)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observed = observations["topaneu_github_release_contract_v2"]
        observed["main_head_sha"] = "c" * 40
        observed["changelog_blob"]["sha"] = "d" * 40
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertFalse(result["direct_prior_baseline_feasibility_reaudit_triggered"])
        self.assertEqual(result["manual_review_requests"], ["fresh_source_reaudit_only"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v10_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V10.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["terms_blob"]["size"] = 1108
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "topaneu"):
                load_config(candidate)

        payload = json.loads(CONFIG_V10.read_text(encoding="utf-8"))
        payload["authorization"]["automatic_terms_acceptance"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v11_adds_rsna_release_contract_watch_without_authority(self) -> None:
        config = load_config(CONFIG_V11)
        self.assertEqual(config["extends"], "source_watch_v10.json")
        self.assertEqual(len(config["watches"]), 15)
        rsna = config["watches"][-1]
        self.assertEqual(rsna["watch_id"], "rsna_ica_release_contract_v1")
        self.assertEqual(rsna["review_request"], "fresh_source_reaudit_only")
        frozen = rsna["frozen_snapshot"]
        self.assertEqual(
            frozen["registry_file_commit_sha"],
            "523ffd3914ba99e6c4b17441f1633cc3eec74c69",
        )
        self.assertTrue(frozen["controlled_access_declared"])
        self.assertTrue(frozen["data_resource_publication_forthcoming"])
        self.assertTrue(frozen["wiki_page_is_coming_soon_only"])
        self.assertFalse(frozen["machine_auditable_release_contract_present"])

        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v11_rsna_change_requests_source_reaudit_only(self) -> None:
        config = load_config(CONFIG_V11)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observed = observations["rsna_ica_release_contract_v1"]
        observed["wiki_page_sha256"] = "e" * 64
        observed["wiki_page_is_coming_soon_only"] = False
        observed["machine_auditable_release_contract_present"] = True
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertFalse(result["direct_prior_baseline_feasibility_reaudit_triggered"])
        self.assertEqual(result["manual_review_requests"], ["fresh_source_reaudit_only"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v11_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V11.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["wiki_page_bytes"] = 12
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V10,
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "rsna"):
                load_config(candidate)

        payload = json.loads(CONFIG_V11.read_text(encoding="utf-8"))
        payload["authorization"]["gpu_training"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V10,
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v12_adds_topbrain_and_bravecowcow_watches_without_authority(self) -> None:
        config = load_config(CONFIG_V12)
        self.assertEqual(config["extends"], "source_watch_v11.json")
        self.assertEqual(len(config["watches"]), 18)
        data, dockers, bravecow = config["watches"][-3:]
        self.assertEqual(data["watch_id"], "topbrain2025_data_release_v1")
        self.assertEqual(data["frozen_snapshot"]["zenodo_revision"], 14)
        self.assertEqual(
            data["frozen_snapshot"]["zenodo_files"][0]["size"], 1958849592
        )
        self.assertIsNone(data["frozen_snapshot"]["zenodo_license_id"])
        self.assertEqual(
            dockers["watch_id"], "topbrain2025_podium_dockers_v1"
        )
        self.assertEqual(dockers["frozen_snapshot"]["zenodo_revision"], 18)
        self.assertEqual(len(dockers["frozen_snapshot"]["zenodo_files"]), 7)
        self.assertEqual(
            bravecow["watch_id"], "bravecowcow_rsna_multitask_baseline_v1"
        )
        self.assertEqual(
            bravecow["frozen_snapshot"]["main_head_sha"],
            "e59e2368a722eabedc6b2228b1c6e1e7325cacd5",
        )
        self.assertEqual(bravecow["frozen_snapshot"]["release_count"], 0)

        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v12_changes_request_only_the_registered_review(self) -> None:
        config = load_config(CONFIG_V12)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observations["topbrain2025_data_release_v1"]["zenodo_revision"] = 15
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertFalse(result["direct_prior_baseline_feasibility_reaudit_triggered"])
        self.assertEqual(result["manual_review_requests"], ["fresh_source_reaudit_only"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observations["bravecowcow_rsna_multitask_baseline_v1"][
            "main_head_sha"
        ] = "f" * 40
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertFalse(result["fresh_source_reaudit_triggered"])
        self.assertTrue(result["direct_prior_baseline_feasibility_reaudit_triggered"])
        self.assertEqual(
            result["manual_review_requests"],
            ["direct_prior_baseline_feasibility_reaudit_only"],
        )
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v12_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V12.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["zenodo_revision"] = 15
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V11,
                CONFIG_V10,
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "topbrain2025"):
                load_config(candidate)

        payload = json.loads(CONFIG_V12.read_text(encoding="utf-8"))
        payload["authorization"]["gpu_training"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V11,
                CONFIG_V10,
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

    def test_v13_adds_da4dcta_material_watches_without_authority(self) -> None:
        config = load_config(CONFIG_V13)
        self.assertEqual(config["extends"], "source_watch_v12.json")
        self.assertEqual(len(config["watches"]), 20)
        zenodo, github = config["watches"][-2:]
        self.assertEqual(zenodo["watch_id"], "da4dcta_zenodo_material_release_v1")
        self.assertEqual(zenodo["frozen_snapshot"]["zenodo_revision"], 4)
        self.assertEqual(
            zenodo["frozen_snapshot"]["zenodo_files"][0]["size"], 1934055674
        )
        self.assertEqual(
            zenodo["frozen_snapshot"]["zenodo_license_id"], "cc-by-4.0"
        )
        self.assertEqual(
            github["watch_id"], "da4dcta_github_release_and_baseline_v1"
        )
        self.assertEqual(
            github["frozen_snapshot"]["main_head_sha"],
            "8df7d45e9f65e3cbfd4ae3fc430c65a98905bdfc",
        )
        self.assertEqual(github["frozen_snapshot"]["release_count"], 1)
        self.assertIsNone(github["frozen_snapshot"]["license_spdx_id"])
        self.assertEqual(
            github["frozen_snapshot"]["payload_or_code_entries"][:2],
            ["LSTM_model.py", "PlotLosses.py"],
        )

        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        result = evaluate_config(config, observations)
        self.assertTrue(result["same_as_all_frozen_snapshots"])
        self.assertFalse(result["manual_review_triggered"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v13_change_requests_fresh_source_reaudit_only(self) -> None:
        config = load_config(CONFIG_V13)
        observations = {
            watch["watch_id"]: copy.deepcopy(watch["frozen_snapshot"])
            for watch in config["watches"]
        }
        observations["da4dcta_zenodo_material_release_v1"]["zenodo_revision"] = 5
        result = evaluate_config(config, observations)
        self.assertTrue(result["manual_review_triggered"])
        self.assertTrue(result["fresh_source_reaudit_triggered"])
        self.assertFalse(result["direct_prior_baseline_feasibility_reaudit_triggered"])
        self.assertEqual(result["manual_review_requests"], ["fresh_source_reaudit_only"])
        self.assertFalse(result["automatic_download_authorized"])
        self.assertFalse(result["p0_authorized"])
        self.assertFalse(result["method_or_architecture_authorized"])
        self.assertFalse(result["gpu_or_outer_test_authorized"])

    def test_v13_snapshot_or_authorization_rewrite_is_rejected(self) -> None:
        payload = json.loads(CONFIG_V13.read_text(encoding="utf-8"))
        payload["added_watches"][0]["frozen_snapshot"]["zenodo_revision"] = 5
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V12,
                CONFIG_V11,
                CONFIG_V10,
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "da4dcta"):
                load_config(candidate)

        payload = json.loads(CONFIG_V13.read_text(encoding="utf-8"))
        payload["authorization"]["gpu_training"] = True
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            candidate = source / "source_watch.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            for config_path in (
                CONFIG_V12,
                CONFIG_V11,
                CONFIG_V10,
                CONFIG_V9,
                CONFIG_V8,
                CONFIG_V7,
                CONFIG_V6,
                CONFIG_V5,
                CONFIG_V4,
            ):
                (source / config_path.name).write_text(
                    config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )
            with self.assertRaisesRegex(SourceWatchContractError, "authorization"):
                load_config(candidate)

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
