from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import torch

from aurora.aneug_release_730_harmonized_validation_endpoints import (
    DIRECT_LABELS,
    HarmonizedValidationEndpointError,
    assemble_result,
    common_case_endpoints,
    file_sha256,
    load_config,
    reference_support_area_fraction,
    validate_activation,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_release_730_harmonized_validation_endpoints_v1.json"
SIDECAR = ROOT / "cluster" / "pbs_aneug_release_730_harmonized_validation_endpoints_v1.pbs"
GRAPH_CONFIG = ROOT / "configs" / "aneug_release_730_official_graphunet_baseline_v1.json"
GHD_GPS_CONFIG = ROOT / "configs" / "aneug_release_730_ghd_gps_baseline_v1.json"
TRANSOLVER_CONFIG = ROOT / "configs" / "aneug_release_730_transolver_baseline_v1.json"


def endpoint_row(offset: float = 0.0, support: float = 0.75) -> dict[str, float]:
    return {
        "field_relative_l2": 0.4 + offset,
        "mean_wss_vector_error": 0.3 + offset,
        "tawss_normalized_absolute_error": 0.2 + offset,
        "osi_mae": 0.1 + offset,
        "osi_coverage": 0.9,
        "osi_reference_support_fraction": support,
    }


def activation() -> dict:
    config = load_config(CONFIG)
    return {
        "schema_version": "aurora.private.aneug_release_730_harmonized_validation_endpoints_activation.v1",
        "protocol_id": config["protocol_id"],
        "status": "activated_after_three_terminal_frozen_direct_controls",
        "public_commit": "a" * 40,
        "quality_conclusion": "success",
        "source_result_sha256": {
            label: character * 64
            for label, character in zip(DIRECT_LABELS, "abc")
        },
        "source_checkpoint_sha256": {
            label: character * 64
            for label, character in zip(DIRECT_LABELS, "def")
        },
        "terminal_record_sha256": {
            label: character * 64
            for label, character in zip(DIRECT_LABELS, "123")
        },
        "validation_case_digest": config["split"]["validation_case_digest"],
        "validation_loader_order_sha256": config["split"][
            "validation_loader_order_sha256"
        ],
        "read_train_fields_for_floor_only": True,
        "read_validation_fields": True,
        "read_locked_test_or_extra": False,
        "training": False,
        "model_or_checkpoint_selection": False,
        "paper_claim": False,
        "single_materialization": True,
        "server": "introai9",
        "excluded_server": "junjinyong",
    }


class HarmonizedValidationEndpointTests(unittest.TestCase):
    def test_sidecar_is_pbs_only_frozen_validation_scope(self) -> None:
        text = SIDECAR.read_text(encoding="utf-8")
        self.assertIn("#PBS -q coss_agpu", text)
        self.assertIn("#PBS -l select=1:ncpus=4:mem=64gb:ngpus=1:Qlist=agpu", text)
        self.assertIn("${PBS_JOBID:?harmonized validation evaluation is PBS-only}", text)
        self.assertIn("python -m aurora.aneug_release_730_harmonized_validation_endpoints", text)
        self.assertIn("--bind \"$AURORA_DATA_ROOT:/data:ro\"", text)
        self.assertIn("--bind \"$AURORA_PROJECT_ROOT:/workspace:ro\"", text)
        self.assertNotIn("qsub", text)
        self.assertNotIn("junjinyong", text.lower())
        self.assertNotIn("locked_test", text.lower())
        self.assertNotIn("processed_only_extra", text.lower())

    def test_config_is_common_floor_frozen_inference_only(self) -> None:
        config = load_config(CONFIG)
        self.assertEqual(config["runtime"]["queue"], "coss_agpu")
        self.assertEqual(config["runtime"]["Qlist"], "agpu")
        self.assertEqual(
            config["source"]["graph_config_sha256"], file_sha256(GRAPH_CONFIG)
        )
        self.assertEqual(
            config["source"]["ghd_gps_config_sha256"],
            file_sha256(GHD_GPS_CONFIG),
        )
        self.assertEqual(
            config["source"]["transolver_config_sha256"],
            file_sha256(TRANSOLVER_CONFIG),
        )
        self.assertEqual(config["split"]["validation_cases"], 73)
        self.assertFalse(config["split"]["read_locked_test_fields"])
        self.assertEqual(
            config["evaluation"]["reference_tawss_floor_multiplier"], 1e-4
        )
        self.assertFalse(config["authorization"]["training"])
        for path, key, changed in (
            (("split", "read_locked_test_fields"), None, True),
            (("evaluation", "reference_tawss_floor_multiplier"), None, 1e-3),
            (("authorization", "training"), None, True),
        ):
            mutated = copy.deepcopy(config)
            mutated[path[0]][path[1]] = changed
            with self.assertRaises(HarmonizedValidationEndpointError):
                validate_config(mutated)

    def test_common_endpoint_uses_area_weighted_train_floor_support(self) -> None:
        reference = torch.zeros(80, 2, 3)
        reference[:, 0, 0] = torch.where(
            torch.arange(80) % 2 == 0,
            torch.tensor(1.0),
            torch.tensor(-1.0),
        )
        reference[:, 1, 0] = 0.01
        prediction = reference.clone()
        weights = torch.tensor([0.75, 0.25])
        normals = torch.tensor([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
        result = common_case_endpoints(
            prediction, reference, weights, normals, reference_tawss_floor=0.1
        )
        self.assertAlmostEqual(result["osi_mae"], 0.0)
        self.assertAlmostEqual(result["osi_coverage"], 1.0)
        self.assertAlmostEqual(result["osi_reference_support_fraction"], 0.75)
        self.assertAlmostEqual(
            reference_support_area_fraction(reference, weights, 0.1), 0.75
        )

    def test_invalid_prediction_receives_registered_osi_penalty(self) -> None:
        reference = torch.zeros(80, 2, 3)
        reference[:, 0, 0] = 1.0
        reference[:, 1, 0] = 0.01
        prediction = reference.clone()
        prediction[:, 0] = 0.0
        result = common_case_endpoints(
            prediction,
            reference,
            torch.tensor([0.75, 0.25]),
            torch.tensor([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]]),
            reference_tawss_floor=0.1,
        )
        self.assertAlmostEqual(result["osi_mae"], 0.5)
        self.assertAlmostEqual(result["osi_coverage"], 0.0)

    def test_result_binds_three_frozen_models_and_common_support(self) -> None:
        active = activation()
        rows = {
            label: [endpoint_row(index * 0.01) for _ in range(73)]
            for index, label in enumerate(DIRECT_LABELS)
        }
        result = assemble_result(
            rows,
            reference_tawss_floor=0.00125,
            activation=active,
            provenance={"public_commit": "a" * 40},
            elapsed_seconds=12.0,
            peak_gpu_memory_bytes=123,
        )
        self.assertEqual(result["validation_case_count"], 73)
        self.assertEqual(tuple(result["controls"]), DIRECT_LABELS)
        self.assertEqual(
            result["osi_reference_support"]["case_mean_area_fraction"], 0.75
        )
        self.assertFalse(result["training_performed"])
        self.assertFalse(result["model_or_checkpoint_selection"])
        changed = copy.deepcopy(rows)
        changed["transolver"][0]["osi_reference_support_fraction"] = 0.5
        with self.assertRaisesRegex(
            HarmonizedValidationEndpointError, "reference_support_mismatch"
        ):
            assemble_result(
                changed,
                reference_tawss_floor=0.00125,
                activation=active,
                provenance={},
                elapsed_seconds=1.0,
                peak_gpu_memory_bytes=1,
            )

    def test_activation_rejects_test_access_and_writes_no_identifiers(self) -> None:
        config = load_config(CONFIG)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            value = activation()
            path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
            observed = validate_activation(path, config, "a" * 40)
            self.assertFalse(observed["read_locked_test_or_extra"])
            value["read_locked_test_or_extra"] = True
            path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(
                HarmonizedValidationEndpointError, "activation_boundary"
            ):
                validate_activation(path, config, "a" * 40)


if __name__ == "__main__":
    unittest.main()
