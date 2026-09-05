from types import SimpleNamespace
import unittest

import torch

from aurora.aneug_rhsia_input_alignment import (
    align_rows, audit_loaded_inputs, boundary_components, coefficient_rows,
)


class GeometryOnly:
    def __init__(self, xyz, allowed=True):
        self.xyz, self.allowed, self.reads = xyz, allowed, 0

    def __getitem__(self, key):
        if not self.allowed or key != (0, slice(None), [0, 1, 2]):
            raise AssertionError("non-geometry or held-out tensor access")
        self.reads += 1
        return self.xyz


def fixture():
    generator = torch.Generator().manual_seed(7)
    t = torch.randn(3, 432, generator=generator)
    s = torch.randn(4, 432, generator=generator)
    mean, std = torch.arange(432).float() / 100, torch.full((432,), 0.3)
    faces = torch.tensor([[0, 1, 2], [0, 2, 3]])
    topology = dict(faces_list=[faces], edge_index_list=[faces[:, :2].T],
                    idx_list=[torch.arange(4)], ds_factors=[1])
    xyz = torch.randn(3, 4, 3, generator=generator)
    records = [{"case": f"case{i}", "labels": ["x", "y", "z", "wss_x"],
                "tensor": GeometryOnly(xyz[i], allowed=i < 2)} for i in range(3)]
    transient = {"mesh_data": {**topology, "ghd": t, "ghd_mean": mean,
                  "ghd_std": std, "cases": [r["case"] for r in records]},
                 "registered_data_list": records}
    steady = {"ghd_dict": {"ghd": s, "mean_ghd": mean, "std_ghd": std},
              "case_name": [f"steady{i}" for i in range(4)],
              "tensor": GeometryOnly(None, allowed=False)}
    encoder = {**topology, "ghd_lambda": coefficient_rows(t, mean, std).reshape(3, 8, 3),
               "ghd_lambda_steady": coefficient_rows(s, mean, std).reshape(4, 8, 3),
               "ghd_eigvec": torch.ones(4, 8), "cot_eigvec": torch.ones(3, 4, 16),
               "cot_lambda": torch.ones(3, 16, 1), "cot_eigvec_steady": torch.ones(4, 4, 16),
               "cot_lambda_steady": torch.ones(4, 16, 1),
               "meshes": SimpleNamespace(_verts_padded=xyz.clone())}
    return encoder, transient, steady


class AlignmentTests(unittest.TestCase):
    def test_released_constructor_equation(self):
        x = torch.ones(2, 432)
        self.assertTrue(torch.equal(coefficient_rows(x, torch.ones(432), torch.full((432,), 2.)), torch.full((2, 24), 3.)))

    def test_permutation_recovered_without_positional_assumption(self):
        x = torch.arange(12).reshape(3, 4).float()
        result = align_rows(x, x[[2, 0, 1]])
        self.assertTrue(result["unique_bijection"])
        self.assertEqual(result["source_to_encoder_row"], [1, 2, 0])

    def test_duplicate_is_not_resolved_by_row_index(self):
        result = align_rows(torch.ones(2, 4), torch.ones(2, 4))
        self.assertFalse(result["unique_bijection"])
        self.assertEqual(result["ambiguous_source_rows"], 2)

    def test_roundoff_matching_and_missing_row(self):
        x = torch.tensor([[1., 2.], [3., 4.]])
        result = align_rows(x, x + 1e-6)
        self.assertTrue(result["unique_bijection"])
        self.assertEqual(result["tolerance_source_rows"], 2)
        self.assertEqual(align_rows(x, x + 1)["unmatched_source_rows"], 2)

    def test_no_wss_or_held_out_tensor_access(self):
        enc, transient, steady = fixture()
        result = audit_loaded_inputs(enc, transient, steady, ["case0", "case1"])
        self.assertTrue(result["coefficient_row_alignment_verified"])
        self.assertTrue(result["development_geometry_alignment_verified"])
        self.assertEqual(result["wss_field_values_read"], 0)
        self.assertEqual([r["tensor"].reads for r in transient["registered_data_list"]], [1, 1, 0])
        self.assertEqual(result["boundary"]["component_sizes"], [4])

    def test_descriptor_and_mesh_permutation_is_reconciled(self):
        enc, transient, steady = fixture()
        enc["ghd_lambda"] = enc["ghd_lambda"][[2, 0, 1]]
        enc["meshes"]._verts_padded = enc["meshes"]._verts_padded[[2, 0, 1]]
        result = audit_loaded_inputs(enc, transient, steady, ["case0", "case1"])
        self.assertTrue(result["development_geometry_alignment_verified"])

    def test_independently_misaligned_mesh_is_detected(self):
        enc, transient, steady = fixture()
        enc["meshes"]._verts_padded = enc["meshes"]._verts_padded[[2, 0, 1]]
        result = audit_loaded_inputs(enc, transient, steady, ["case0", "case1"])
        self.assertFalse(result["development_geometry_alignment_verified"])

    def test_partial_low_mode_duplicates_resolve_by_geometry(self):
        enc, transient, steady = fixture()
        transient["mesh_data"]["ghd"][1, :24] = transient["mesh_data"]["ghd"][0, :24]
        enc["ghd_lambda"][1] = enc["ghd_lambda"][0]
        result = audit_loaded_inputs(enc, transient, steady, ["case0", "case1"])
        self.assertFalse(result["coefficient_row_alignment_verified"])
        self.assertTrue(result["development_geometry_alignment_verified"])
        self.assertEqual([r["encoder_row"] for r in result["development_geometry"]], [0, 1])

    def test_identical_geometry_requires_equivalent_descriptors_for_tie(self):
        enc, transient, steady = fixture()
        transient["mesh_data"]["ghd"][1, :24] = transient["mesh_data"]["ghd"][0, :24]
        enc["ghd_lambda"][1] = enc["ghd_lambda"][0]
        enc["meshes"]._verts_padded[1] = enc["meshes"]._verts_padded[0]
        transient["registered_data_list"][1]["tensor"].xyz = transient["registered_data_list"][0]["tensor"].xyz
        result = audit_loaded_inputs(enc, transient, steady, ["case0", "case1"])
        self.assertTrue(result["development_geometry_alignment_verified"])
        self.assertTrue(result["development_geometry"][0]["descriptor_equivalent_duplicate"])
        enc["cot_eigvec"][1] *= -1
        result = audit_loaded_inputs(enc, transient, steady, ["case0", "case1"])
        self.assertFalse(result["development_geometry_alignment_verified"])
        self.assertEqual(result["development_input_rows_unresolved"], 2)

    def test_nonfinite_descriptor_recorded_and_bad_shape_rejected(self):
        enc, transient, steady = fixture()
        enc["cot_eigvec_steady"][2, 1, 0] = float("nan")
        self.assertEqual(audit_loaded_inputs(enc, transient, steady, ["case0"])["spectral_nonfinite_counts"]["cot_eigvec_steady"], 1)
        enc["cot_lambda"] = torch.ones(3, 4)
        with self.assertRaisesRegex(ValueError, "descriptor shape"):
            audit_loaded_inputs(enc, transient, steady, ["case0"])

    def test_boundary_is_anonymous_and_rejects_nonmanifold(self):
        result = boundary_components(torch.tensor([[0, 1, 2]]), 3)
        self.assertFalse(result["semantic_inlet_outlet_labels_available"])
        with self.assertRaisesRegex(ValueError, "nonmanifold"):
            boundary_components(torch.tensor([[0, 1, 2], [1, 0, 3], [0, 1, 4]]), 5)


if __name__ == "__main__":
    unittest.main()
