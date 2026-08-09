from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from aurora.aneumo_range import ZipMember
from aurora.aneux_preprocessing_orbit_p0 import (
    AneuXOrbitP0ContractError,
    audit_tabular_archive,
    load_config,
    main,
    summarize_model_members,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneux_preprocessing_orbit_p0.json"


def _csv_bytes(fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


class AneuXOrbitConfigTests(unittest.TestCase):
    def test_reference_config_is_asset_only_and_scores_34(self) -> None:
        config = load_config(CONFIG)
        score = sum(config["candidate"]["score_axes"].values())
        self.assertEqual(score, 34)
        self.assertFalse(config["candidate"]["method_selected"])
        self.assertFalse(config["candidate"]["gpu_training_authorized"])
        self.assertFalse(config["transport"]["full_model_archive_download_allowed"])
        self.assertEqual(
            config["transport"]["attempt_scope"],
            "maximum_three_attempts_per_http_operation_within_the_single_exact_job",
        )
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["excluded_server"], "junjinyong")

    def test_transport_or_gpu_boundary_cannot_be_relaxed(self) -> None:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["transport"]["full_model_archive_download_allowed"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(AneuXOrbitP0ContractError, "transport"):
                load_config(candidate)

        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        payload["candidate"]["gpu_training_authorized"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(AneuXOrbitP0ContractError, "candidate"):
                load_config(candidate)

    def test_validate_only_needs_no_cache_or_result(self) -> None:
        self.assertEqual(main(["--config", str(CONFIG), "--validate-only"]), 0)


class AneuXOrbitAggregateTests(unittest.TestCase):
    def _tabular_zip(self, path: Path) -> None:
        clinical = []
        per_cut = []
        morpho = []
        cuts = ["dome", "ninja", "cut1", "cut2"]
        for index in range(4):
            lesion = f"case-{index}"
            clinical.append(
                {
                    "source": "hug2016",
                    "dataset": lesion,
                    "status": "ruptured" if index % 2 else "unruptured",
                    "patientID": f"patient-{index}",
                    "vesselFileID": f"vessel-{index}",
                }
            )
            for cut in cuts:
                per_cut.append({"dataset": lesion, "cutType": cut})
                row = {"dataset": lesion, "cutType": cut}
                row.update({f"feature_{feature}": "0" for feature in range(170)})
                morpho.append(row)
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(
                "data/clinical.csv",
                _csv_bytes(list(clinical[0]), clinical),
            )
            archive.writestr(
                "data/clinical-per-cut.csv",
                _csv_bytes(["dataset", "cutType"], per_cut),
            )
            archive.writestr(
                "data/morpho-per-cut.csv",
                _csv_bytes(list(morpho[0]), morpho),
            )

    def test_tabular_audit_keeps_only_aggregate_counts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "data.zip"
            self._tabular_zip(archive)
            summary = audit_tabular_archive(archive)
        self.assertEqual(summary["unique_lesions"], 4)
        self.assertEqual(summary["observed_patient_groups"], 4)
        self.assertEqual(summary["lesions_with_dome_and_ninja"], 4)
        self.assertEqual(summary["morphometric_feature_columns"], 170)
        self.assertTrue(summary["per_cut_key_sets_match"])
        self.assertNotIn("case-0", json.dumps(summary))

    def test_model_summary_reads_names_but_zero_member_payload(self) -> None:
        members = {}
        for resolution in ("original", "area-001", "area-005"):
            for cut in ("dome", "ninja", "cut1", "cut2"):
                name = f"models/aneurysms/{resolution}/{cut}/case.vtp"
                members[name] = ZipMember(name, 0, 0, 0, 0, 0)
        summary = summarize_model_members(members)
        self.assertEqual(summary["aneurysm_vtp_members"], 12)
        self.assertEqual(summary["model_member_payload_bytes_read"], 0)
        self.assertTrue(summary["safe_member_paths"])
        self.assertEqual(len(summary["member_name_listing_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
