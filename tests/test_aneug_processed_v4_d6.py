from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

try:
    import torch
except ImportError:  # PyTorch is pinned in public Quality and on introai9
    torch = None

from aurora.aneug_processed_v4_d6 import (
    D6ContractError,
    aggregate_case_diagnostics,
    approximate_histogram_quantile,
    assert_execution_authorized,
    canonical_case_digest,
    cycle_moments,
    flatten_private_components,
    inspect_case_tensor,
    load_contract,
    stream_selected_case_diagnostics,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "aneug_processed_v4_d6_train_field_audit_v1.json"


class AneuGProcessedV4D6RegistrationTests(unittest.TestCase):
    @staticmethod
    def _planar_fixture() -> tuple[list[str], object, object, object, object]:
        if torch is None:
            raise RuntimeError("PyTorch fixture requested without PyTorch")
        labels = [
            "x",
            "y",
            "z",
            "x_normal",
            "y_normal",
            "z_normal",
            "wss_x",
            "wss_y",
            "wss_z",
        ]
        tensor = torch.zeros((4, 3, 9), dtype=torch.float32)
        tensor[:, :, :3] = torch.tensor(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        )
        tensor[:, :, 5] = 1.0 / 1.00001
        tensor[:, 0, 6] = torch.tensor([1.0, 2.0, 1.0, 0.5])
        tensor[:, 1, 6] = torch.tensor([1.0, -1.0, 1.0, -1.0])
        tensor[:, 2, 6] = 1.0
        faces = torch.tensor([[0, 1, 2]], dtype=torch.int64)
        mean = torch.zeros((1, 1, 9), dtype=torch.float32)
        std = torch.ones((1, 1, 9), dtype=torch.float32)
        return labels, tensor, faces, mean, std

    def test_registration_is_train_only_cpu_only_and_non_executable(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["read_scope"]["expected_train_cases"], 406)
        self.assertFalse(contract["read_scope"]["read_validation_tensor_values"])
        self.assertFalse(contract["read_scope"]["read_outer_test_tensor_values"])
        self.assertEqual(contract["execution_if_activated"]["ngpus"], 0)
        self.assertEqual(contract["execution_if_activated"]["maximum_pbs_attempts"], 1)
        self.assertFalse(contract["authority"]["human_activation_recorded"])
        with self.assertRaisesRegex(D6ContractError, "not_activated"):
            assert_execution_authorized(contract)

    def test_exact_official_decoder_and_unclipped_rrt_policy_are_frozen(self) -> None:
        contract = load_contract(CONFIG)
        self.assertEqual(contract["physical_decoder"]["epsilon"], 1e-5)
        self.assertEqual(
            contract["method_free_estimands"]["rrt_policy"],
            "diagnose_denominator_only_no_epsilon_clipped_rrt_headline",
        )
        self.assertTrue(
            contract["physical_decoder"][
                "future_model_normalization_must_be_recomputed_from_d5_train_only"
            ]
        )

    def test_private_components_flatten_and_hash_without_public_ids(self) -> None:
        components = [
            {"case_ids": ["stable_10"], "case_count": 1},
            {"case_ids": ["stable_2", "stable_3"], "case_count": 2},
        ]
        ids = flatten_private_components(components)
        self.assertEqual(ids, ["stable_10", "stable_2", "stable_3"])
        self.assertEqual(canonical_case_digest(ids), canonical_case_digest(reversed(ids)))
        with self.assertRaisesRegex(D6ContractError, "case_id_integrity"):
            flatten_private_components(
                [
                    {"case_ids": ["stable_1"], "case_count": 1},
                    {"case_ids": ["stable_1"], "case_count": 1},
                ]
            )

    def test_scope_threshold_and_authorization_mutations_fail_closed(self) -> None:
        original = json.loads(CONFIG.read_text(encoding="utf-8"))
        mutations = (
            ("authority", "human_activation_recorded", True, "activation_state"),
            ("read_scope", "read_validation_tensor_values", True, "read_validation"),
            ("read_scope", "expected_train_cases", 405, "expected_shape"),
            ("physical_decoder", "epsilon", 1e-6, "decoder_epsilon"),
            (
                "gate",
                "histogram_bins",
                100,
                "histogram_bins",
            ),
            ("execution_if_activated", "ngpus", 1, "resources"),
            ("implementation_readiness", "real_payload_read", True, "real_payload_read"),
            ("implementation_readiness", "pbs_wrapper", True, "pbs_wrapper"),
            ("authorization", "execute_d6_now", True, "execute_d6_now"),
        )
        for section, key, value, reason in mutations:
            candidate = copy.deepcopy(original)
            candidate[section][key] = value
            with self.assertRaisesRegex(D6ContractError, reason):
                validate_contract(candidate)

    @unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
    def test_planar_tangent_cycle_has_valid_mesh_moments_and_roundtrip(self) -> None:
        labels, tensor, faces, mean, std = self._planar_fixture()
        result = inspect_case_tensor(tensor, labels, mean, std, faces, torch)
        self.assertLessEqual(result["static_max_abs"], 0.0)
        self.assertLess(result["roundtrip_max_abs"], 1e-12)
        self.assertAlmostEqual(result["face_nondegenerate_fraction"], 1.0)
        self.assertTrue(bool((result["normal_cosine"] > 0.999).all().item()))
        self.assertTrue(bool((result["tangent_ratio"] == 0).all().item()))
        self.assertTrue(result["temporal_residual_nonzero"])
        self.assertEqual(result["positive_tawss_count"], 3)
        self.assertLessEqual(float(result["relative_jensen_violation"].max().item()), 1e-12)
        self.assertGreater(float(result["decoder_epsilon_relative_difference"].max().item()), 0)

    @unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
    def test_stream_never_reads_sealed_tensor_values(self) -> None:
        labels, tensor, faces, mean, std = self._planar_fixture()

        class SealedCase(dict):
            def get(self, key: object, default: object = None) -> object:
                if key == "tensor":
                    raise AssertionError("sealed tensor was accessed")
                return super().get(key, default)

        records = {
            "train_a": {"labels": labels, "tensor": tensor},
            "validation_a": SealedCase({"labels": labels}),
            "outer_a": SealedCase({"labels": labels}),
        }
        streamed = list(
            stream_selected_case_diagnostics(
                records,
                ["train_a"],
                ["validation_a", "outer_a"],
                labels,
                mean.reshape(-1),
                std.reshape(-1),
                faces,
                torch,
                expected_shape=[4, 3, 9],
                decoder_epsilon=1e-5,
                legacy_epsilon=1e-6,
                tangency_mask_fraction=0.01,
            )
        )
        self.assertEqual(len(streamed), 1)
        with self.assertRaisesRegex(D6ContractError, "train_sealed_overlap"):
            list(
                stream_selected_case_diagnostics(
                    records,
                    ["train_a"],
                    ["train_a", "outer_a"],
                    labels,
                    mean.reshape(-1),
                    std.reshape(-1),
                    faces,
                    torch,
                    expected_shape=[4, 3, 9],
                    decoder_epsilon=1e-5,
                    legacy_epsilon=1e-6,
                    tangency_mask_fraction=0.01,
                )
            )

    @unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
    def test_streaming_aggregate_passes_and_keeps_train_stats_private(self) -> None:
        contract = load_contract(CONFIG)
        labels, tensor, faces, mean, std = self._planar_fixture()
        diagnostic = inspect_case_tensor(tensor, labels, mean, std, faces, torch)
        public, private = aggregate_case_diagnostics(
            contract,
            (diagnostic for _ in range(406)),
            torch,
            source_identity_reverified=True,
            private_manifest_reverified=True,
            train_scope_enforced=True,
            normalization_metadata_valid=True,
            shared_faces_valid=True,
        )
        self.assertTrue(public["gate_pass"])
        self.assertEqual(public["scientific_verdict"], "pass")
        self.assertEqual(public["train_case_count"], 406)
        self.assertEqual(public["validation_case_field_count_read"], 0)
        self.assertFalse(public["private_normalization_values_published"])
        serialized = json.dumps(public, sort_keys=True)
        self.assertNotIn("coordinate_physical", serialized)
        self.assertNotIn("wss_physical", serialized)
        self.assertEqual(private["train_split_sha256"], contract["source"]["d5_train_split_sha256"])
        self.assertEqual(
            private["model_normalization_source"], "d5_train_physical_values_only"
        )
        self.assertFalse(private["validation_outer_or_auxiliary_statistics_included"])
        json.dumps(public, sort_keys=True, allow_nan=False)
        json.dumps(private, sort_keys=True, allow_nan=False)

    @unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
    def test_noncompensatory_failures_cannot_be_hidden_by_other_metrics(self) -> None:
        contract = load_contract(CONFIG)
        labels, tensor, faces, mean, std = self._planar_fixture()
        reference = inspect_case_tensor(tensor, labels, mean, std, faces, torch)
        variants = []
        bad_tangency = dict(reference)
        bad_tangency["tangent_ratio"] = torch.ones_like(reference["tangent_ratio"])
        variants.append(("wss_tangency", bad_tangency))
        bad_normals = dict(reference)
        bad_normals["normal_cosine"] = torch.zeros_like(reference["normal_cosine"])
        variants.append(("mesh_stored_normal_agreement", bad_normals))
        bad_temporal = dict(reference)
        bad_temporal["temporal_residual_nonzero"] = False
        variants.append(("all_cases_temporally_nonzero", bad_temporal))
        bad_jensen = dict(reference)
        bad_jensen["relative_jensen_violation"] = torch.ones_like(
            reference["relative_jensen_violation"]
        )
        variants.append(("jensen_moment_cone", bad_jensen))
        bad_endpoints = dict(reference)
        bad_endpoints["osi"] = torch.zeros_like(reference["osi"])
        variants.append(("cycle_endpoints_finite_and_nonconstant", bad_endpoints))

        for expected_reason, diagnostic in variants:
            with self.subTest(expected_reason=expected_reason):
                public, _ = aggregate_case_diagnostics(
                    contract,
                    (diagnostic for _ in range(406)),
                    torch,
                    source_identity_reverified=True,
                    private_manifest_reverified=True,
                    train_scope_enforced=True,
                    normalization_metadata_valid=True,
                    shared_faces_valid=True,
                )
                self.assertFalse(public["gate_pass"])
                self.assertEqual(public["scientific_verdict"], "fail")
                self.assertIn(expected_reason, public["gate_reasons"])

    @unittest.skipIf(torch is None, "PyTorch is optional in the lightweight local environment")
    def test_cycle_moments_expose_oscillation_without_clipping(self) -> None:
        wss = torch.tensor(
            [
                [[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                [[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
            ],
            dtype=torch.float64,
        )
        moments = cycle_moments(wss, torch)
        self.assertAlmostEqual(float(moments["osi_unclipped"][0].item()), 0.5)
        self.assertAlmostEqual(float(moments["osi_unclipped"][1].item()), 0.0)
        self.assertAlmostEqual(float(moments["mean_vector_magnitude"][0].item()), 0.0)
        self.assertTrue(bool((moments["mean_magnitude"] >= moments["mean_vector_magnitude"]).all().item()))

    def test_histogram_quantile_is_deterministic(self) -> None:
        histogram = [0, 2, 0, 2]
        self.assertAlmostEqual(approximate_histogram_quantile(histogram, 0.5, 0.0, 1.0), 0.375)
        self.assertAlmostEqual(approximate_histogram_quantile(histogram, 0.95, 0.0, 1.0), 0.875)


if __name__ == "__main__":
    unittest.main()
