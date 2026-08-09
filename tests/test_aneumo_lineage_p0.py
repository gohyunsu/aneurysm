import copy
import csv
import hashlib
import io
import json
import unittest
from pathlib import Path

from aurora.aneumo_lineage_p0 import (
    AneumoLineageP0ContractError,
    audit_payloads,
    load_config,
    parse_lfs_pointer,
    parse_mapping,
    validate_config_payload,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneumo_lineage_p0.json"
EXECUTION_RECORD = ROOT / "results" / "aneumo_lineage_p0_execution_20260810.json"


def csv_bytes(fields, rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


class AneumoLineageP0Tests(unittest.TestCase):
    def test_execution_record_closes_without_scientific_verdict_or_rerun(self):
        result = json.loads(EXECUTION_RECORD.read_text())
        self.assertEqual(
            hashlib.sha256(EXECUTION_RECORD.read_bytes()).hexdigest(),
            "c10c65766f0f0564cbddb911f10c32a03eb41f4aa7e8adbff99094cb5ad7b30d",
        )
        self.assertEqual(result["execution"]["server"], "introai9")
        self.assertEqual(result["execution"]["job_id"], "115386.ECE-util1")
        self.assertEqual(result["execution"]["exit_status"], -29)
        self.assertEqual(result["execution"]["gpu_requested"], 0)
        self.assertFalse(result["scientific_gate_evaluated"])
        self.assertIsNone(result["scientific_verdict"])
        self.assertEqual(result["materialization"]["completed_small_source_files"], 0)
        self.assertFalse(result["materialization"]["archive_member_payload_accessed"])
        self.assertFalse(result["boundary"]["same_contract_repair_or_resubmission_allowed"])
        self.assertEqual(result["boundary"]["active_source_shortlist_count_after_closure"], 0)

    def test_reference_config_preserves_cpu_only_boundary(self):
        config = load_config(CONFIG)
        self.assertEqual(config["execution"]["server"], "introai9")
        self.assertEqual(config["execution"]["excluded_server"], "junjinyong")
        self.assertFalse(config["execution"]["gpu_requested"])
        self.assertFalse(config["candidate"]["method_selected"])
        self.assertEqual(config["candidate"]["score"], 35.0)

    def test_config_rejects_gpu_or_resubmission(self):
        import json

        config = json.loads(CONFIG.read_text())
        config["execution"]["gpu_requested"] = True
        with self.assertRaisesRegex(AneumoLineageP0ContractError, "execution_boundary_changed"):
            validate_config_payload(config)

        config = json.loads(CONFIG.read_text())
        config["transport"]["same_source_job_resubmission_allowed"] = True
        with self.assertRaisesRegex(AneumoLineageP0ContractError, "transport_boundary_changed"):
            validate_config_payload(config)

    def test_mapping_requires_contiguous_lineage_syntax(self):
        mapping, families = parse_mapping(
            b"case_id,connection\n1,7_deform_1\n2,7_deform_2\n3,9_deform_1\n"
        )
        self.assertEqual(mapping[2], (7, 2))
        self.assertEqual(families, {7: [1, 2], 9: [1]})
        with self.assertRaisesRegex(AneumoLineageP0ContractError, "invalid_mapping_connection"):
            parse_mapping(b"case_id,connection\n1,unknown\n")

    def test_lfs_pointer_is_text_not_object(self):
        oid, size = parse_lfs_pointer(
            b"version https://git-lfs.github.com/spec/v1\n"
            b"oid sha256:15688323235a5bc064973d07d0ed13d69cc0b3f99937e6be702171ebac4bbb82\n"
            b"size 6878451054\n"
        )
        self.assertEqual(size, 6878451054)
        self.assertEqual(len(oid), 64)

    def test_aggregate_detects_case_disjoint_family_overlap(self):
        config = load_config(CONFIG)
        config = copy.deepcopy(config)
        config["expected_contract"].update(
            {
                "mapping_rows": 6,
                "base_families": 2,
                "minimum_deformations_per_family": 3,
                "maximum_deformations_per_family": 3,
                "morphometry_rows": 6,
                "train_cases": 2,
                "train_families": 2,
                "validation_cases": 2,
                "validation_families": 2,
                "exact_case_overlap": 0,
                "base_family_overlap": 2,
                "validation_family_overlap_fraction": 1.0,
            }
        )
        payloads = {
            "connection": csv_bytes(
                ["case_id", "connection"],
                [
                    {"case_id": 1, "connection": "1_deform_1"},
                    {"case_id": 2, "connection": "1_deform_2"},
                    {"case_id": 3, "connection": "1_deform_3"},
                    {"case_id": 4, "connection": "2_deform_1"},
                    {"case_id": 5, "connection": "2_deform_2"},
                    {"case_id": 6, "connection": "2_deform_3"},
                ],
            ),
            "morphometry": csv_bytes(
                ["case_id", "Size"],
                [{"case_id": value, "Size": 1.0} for value in range(1, 7)],
            ),
            "train": csv_bytes(
                ["case_id", "connect"],
                [
                    {"case_id": 1, "connect": "1_deform_1"},
                    {"case_id": 4, "connect": "2_deform_1"},
                ],
            ),
            "validation": csv_bytes(
                ["case_id", "connect"],
                [
                    {"case_id": 2, "connect": "1_deform_2"},
                    {"case_id": 5, "connect": "2_deform_2"},
                ],
            ),
            "datasheet": b"no geometric overlap with training\nCC BY 4.0\n",
            "github_readme": b"427 real aneurysm geometries\n",
            "hf_readme": b"---\nlicense: cc-by-nc-nd-4.0\n---\n",
            "steady_pointer": (
                b"version https://git-lfs.github.com/spec/v1\n"
                b"oid sha256:15688323235a5bc064973d07d0ed13d69cc0b3f99937e6be702171ebac4bbb82\n"
                b"size 6878451054\n"
            ),
            "transient_pointer": (
                b"version https://git-lfs.github.com/spec/v1\n"
                b"oid sha256:2495c0c060d2aa2e669e3abe038d7494b9b5a1724b91c1f847b534b91f080543\n"
                b"size 14530202660\n"
            ),
        }
        result = audit_payloads(config, payloads)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["aggregates"]["exact_case_overlap"], 0)
        self.assertEqual(result["aggregates"]["base_family_overlap"], 2)
        self.assertFalse(result["aggregates"]["license_sources_agree"])


if __name__ == "__main__":
    unittest.main()
