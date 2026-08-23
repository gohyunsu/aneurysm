from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from aurora.aneug_release_730_oracle_comparison import (
    RANK_GRID,
    Release730OracleComparisonError,
    compare_oracle_to_direct,
    extract_direct_rows,
    extract_oracle_rows,
    load_config,
    nominate_r1_candidate_ranks,
    validate_activation,
    validate_direct_order_attestation,
    validate_private_split_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_oracle_comparison_v1.json"


def rows(offset: float) -> list[dict[str, float]]:
    return [
        {
            "field_relative_l2": 0.5 + offset + index * 1e-5,
            "tawss_normalized_absolute_error": 0.3 + offset,
            "osi_mae": 0.02 + offset * 0.01,
            "osi_coverage": 1.0,
        }
        for index in range(73)
    ]


def direct_result() -> dict:
    return {
        "schema_version": "aurora.aneug_release_730_graphunet.private_result.v1",
        "protocol_id": "aneug_release_730_official_graphunet_baseline_v1",
        "status": "complete_validation_development",
        "single_seed_validation_development_only": True,
        "case_ids_included": False,
        "test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "paper_result_or_claim": False,
        "validation_loader_order_sha256":
        "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "validation": {"per_case_without_identifiers": rows(0.0)},
    }


def oracle_result() -> dict:
    return {
        "schema_version": "aurora.private.aneug_release_730_response_oracle_result.v1",
        "protocol_id": "aneug_release_730_response_oracle_v1",
        "status": "complete",
        "development_only": True,
        "case_ids_included": False,
        "locked_test_field_case_count_read": 0,
        "processed_only_extra_field_case_count_read": 0,
        "oracle_uses_true_validation_amplitude_and_coefficients": True,
        "learned_predictor": False,
        "rank_selected": False,
        "paper_performance_claim": False,
        "validation_loader_order_sha256":
        "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        "rank_grid": list(RANK_GRID),
        "evaluation": {
            "per_case_without_identifiers_by_rank": {
                str(rank): rows(-0.01 - rank * 0.0001) for rank in RANK_GRID
            }
        },
    }


class Release730OracleComparisonTests(unittest.TestCase):
    def test_config_is_threshold_free_and_sealed(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["split"]["validation_cases"], 73)
        self.assertEqual(
            config["split"]["validation_loader_order_sha256"],
            "aac001b3092d11fa0204b49ada2788d21afdb35d015f9c626a5dcae992d4dc30",
        )
        self.assertIsNone(config["decision"]["absolute_performance_threshold"])
        self.assertFalse(config["decision"]["automatic_rank_selection"])
        self.assertFalse(config["decision"]["automatic_global_branch_decision"])
        self.assertEqual(config["decision"]["maximum_R1_candidate_ranks"], 3)
        self.assertFalse(config["boundary"]["execute_now"])
        self.assertFalse(config["boundary"]["locked_test_or_extra_access"])

    def test_extractors_accept_exact_direct_and_oracle_roles(self) -> None:
        self.assertEqual(len(extract_direct_rows(direct_result())), 73)
        for rank in RANK_GRID:
            self.assertEqual(len(extract_oracle_rows(oracle_result(), rank)), 73)

    def test_comparison_reports_every_rank_without_a_decision(self) -> None:
        config = load_config(CONFIG)
        output = compare_oracle_to_direct(
            direct_result(), oracle_result(), config, replicates=200
        )
        self.assertEqual(len(output["paired_oracle_minus_direct"]), len(RANK_GRID))
        self.assertIsNone(output["automatic_rank_selection"])
        self.assertIsNone(output["automatic_global_branch_decision"])
        self.assertFalse(output["oracle_is_learned_model_performance"])
        self.assertTrue(output["learned_response_validation_required"])
        self.assertEqual(output["paired_case_count"], 73)
        self.assertEqual(output["paired_unit"], "synthetic_geometry_case")
        self.assertEqual(output["r1_candidate_rank_nomination"], [16, 64, 256])
        self.assertFalse(output["r1_nomination_is_final_rank_selection"])

    def test_nomination_spans_positive_storage_pareto_without_selecting_rank(self) -> None:
        self.assertEqual(
            nominate_r1_candidate_ranks(
                [
                    "oracle_rank_256",
                    "oracle_rank_0",
                    "oracle_rank_64",
                    "oracle_rank_16",
                    "oracle_rank_128",
                    "oracle_rank_32",
                ]
            ),
            [16, 64, 256],
        )
        self.assertEqual(
            nominate_r1_candidate_ranks(["oracle_rank_0", "oracle_rank_32"]),
            [32],
        )
        with self.assertRaisesRegex(
            Release730OracleComparisonError, "nomination_duplicate"
        ):
            nominate_r1_candidate_ranks(["oracle_rank_16", "oracle_rank_16"])

    def test_storage_accounting_is_rank_specific(self) -> None:
        config = load_config(CONFIG)
        output = compare_oracle_to_direct(
            direct_result(), oracle_result(), config, replicates=200
        )
        storage = output["active_basis_bytes_by_rank"]
        self.assertLess(storage["oracle_rank_0"], storage["oracle_rank_256"])
        self.assertEqual(
            storage["oracle_rank_16"],
            17 * config["comparison"]["basis_width"] * 4,
        )

    def test_activation_binds_result_hashes_and_shared_order(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_oracle_comparison_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "direct_result_sha256": "1" * 64,
            "oracle_result_sha256": "2" * 64,
            "validation_case_digest": config["split"]["validation_case_digest"],
            "validation_loader_order_sha256": config["split"][
                "validation_loader_order_sha256"
            ],
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "direct_terminal_record_sha256": "3" * 64,
            "oracle_terminal_record_sha256": "4" * 64,
            "direct_order_attestation_sha256": "5" * 64,
            "read_locked_test_or_extra": False,
            "rank_selection": False,
            "paper_performance_claim": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(activation), encoding="utf-8")
            validate_activation(path, config, "abc")
            activation["rank_selection"] = True
            path.write_text(json.dumps(activation), encoding="utf-8")
            with self.assertRaisesRegex(Release730OracleComparisonError, "rank_selection"):
                validate_activation(path, config, "abc")

    def test_activation_rejects_missing_order_or_terminal_provenance(self) -> None:
        config = load_config(CONFIG)
        activation = {
            "schema_version": "aurora.private.aneug_release_730_oracle_comparison_activation.v1",
            "protocol_id": config["protocol_id"],
            "public_commit": "abc",
            "quality_conclusion": "success",
            "direct_result_sha256": "1" * 64,
            "oracle_result_sha256": "2" * 64,
            "validation_case_digest": config["split"]["validation_case_digest"],
            "validation_loader_order_sha256": config["split"][
                "validation_loader_order_sha256"
            ],
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "direct_terminal_record_sha256": "3" * 64,
            "oracle_terminal_record_sha256": "4" * 64,
            "direct_order_attestation_sha256": "5" * 64,
            "read_locked_test_or_extra": False,
            "rank_selection": False,
            "paper_performance_claim": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            changed = copy.deepcopy(activation)
            changed.pop("validation_loader_order_sha256")
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(Release730OracleComparisonError, "validation_order"):
                validate_activation(path, config, "abc")
            changed = copy.deepcopy(activation)
            changed.pop("oracle_terminal_record_sha256")
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(
                Release730OracleComparisonError, "oracle_terminal_record_sha256"
            ):
                validate_activation(path, config, "abc")

    def test_legacy_direct_order_requires_bound_attestation(self) -> None:
        config = load_config(CONFIG)
        legacy = direct_result()
        legacy.pop("validation_loader_order_sha256")
        with self.assertRaisesRegex(
            Release730OracleComparisonError, "direct_validation_order"
        ):
            extract_direct_rows(legacy)
        self.assertEqual(
            len(extract_direct_rows(legacy, legacy_order_attested=True)), 73
        )

        activation = {
            "direct_result_sha256": "1" * 64,
            "direct_terminal_record_sha256": "3" * 64,
        }
        attestation = {
            "schema_version": "aurora.private.aneug_release_730_direct_order_attestation.v1",
            "direct_result_sha256": "1" * 64,
            "direct_terminal_record_sha256": "3" * 64,
            "producer_public_commit": "c53b5bc4d0664436de6ae916551448a613e9a4ac",
            "private_split_manifest_sha256": config["split"]["private_manifest_sha256"],
            "validation_case_digest": config["split"]["validation_case_digest"],
            "validation_loader_order_sha256": config["split"]
            ["validation_loader_order_sha256"],
            "order_derivation": "flatten_private_validation_components_in_stored_order",
            "case_ids_included": False,
            "scientific_result_changed": False,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attestation.json"
            path.write_text(json.dumps(attestation), encoding="utf-8")
            validate_direct_order_attestation(path, config, activation)
            attestation["validation_loader_order_sha256"] = "0" * 64
            path.write_text(json.dumps(attestation), encoding="utf-8")
            with self.assertRaisesRegex(
                Release730OracleComparisonError,
                "direct_order_attestation_order",
            ):
                validate_direct_order_attestation(path, config, activation)

    def test_rejects_sealed_or_interpretation_violations(self) -> None:
        changed = copy.deepcopy(direct_result())
        changed["test_field_case_count_read"] = 1
        with self.assertRaisesRegex(Release730OracleComparisonError, "direct_sealed"):
            extract_direct_rows(changed)
        changed_oracle = copy.deepcopy(oracle_result())
        changed_oracle["learned_predictor"] = True
        with self.assertRaisesRegex(
            Release730OracleComparisonError, "oracle_interpretation"
        ):
            extract_oracle_rows(changed_oracle, 16)

    def test_private_manifest_recomputes_order_and_set(self) -> None:
        import hashlib

        from aurora.aneug_release_730_split import (
            _canonical_digest,
            _ordered_digest,
        )

        validation = [f"stable_{index:04d}" for index in range(73)]
        manifest = {
            "validation_components": [
                {"case_ids": [case_id]} for case_id in validation
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "split.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            config = copy.deepcopy(load_config(CONFIG))
            config["split"]["private_manifest_sha256"] = digest
            config["split"]["validation_case_digest"] = _canonical_digest(validation)
            config["split"]["validation_loader_order_sha256"] = _ordered_digest(validation)
            activation = {"private_split_manifest_sha256": digest}
            evidence = validate_private_split_manifest(path, config, activation)
            self.assertEqual(evidence["validation_case_count"], 73)
            self.assertFalse(evidence["case_ids_included"])

            manifest["validation_components"].reverse()
            path.write_text(json.dumps(manifest), encoding="utf-8")
            changed_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            config["split"]["private_manifest_sha256"] = changed_hash
            activation["private_split_manifest_sha256"] = changed_hash
            with self.assertRaisesRegex(
                Release730OracleComparisonError, "validation_manifest_order"
            ):
                validate_private_split_manifest(path, config, activation)


if __name__ == "__main__":
    unittest.main()
