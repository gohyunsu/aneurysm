import unittest

import torch

from aurora.aneug_rhsia_features import (
    canonical_opening_types, resample_repeated_waveform, single_graph_features,
)


class RHSIAFeaturesTests(unittest.TestCase):
    def setUp(self):
        vertices = torch.tensor([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]])
        faces = torch.tensor([[0, 1, 2], [0, 2, 3]])
        types, count = canonical_opening_types(faces, 4)
        self.kwargs = dict(coordinates=vertices, normals=torch.tensor([[0., 0., 1.]]).repeat(4, 1),
            faces=faces, edge_index=torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]]),
            node_types=types, node_type_count=count, ghd_modes=vertices[:, :1].repeat(1, 8),
            ghd_coefficients=torch.arange(24).reshape(8, 3).float(),
            cotangent_modes=vertices[:, 1:2].repeat(1, 16), cotangent_eigenvalues=torch.arange(16).float())

    def test_actual_channel_roles_and_anonymous_boundary(self):
        result = single_graph_features(**self.kwargs)
        self.assertEqual(result["node_features"].shape, (4, 8))
        self.assertTrue(torch.equal(result["node_features"][:, -2:], torch.tensor([[0., 1.]]).repeat(4, 1)))
        torch.testing.assert_close(result["ghd_descriptors"][:, :, 1:4], torch.tensor([1., 0., 0.]).expand(4, 8, 3))
        torch.testing.assert_close(result["cot_descriptors"][:, :, 1:4], torch.tensor([0., 1., 0.]).expand(4, 16, 3))
        torch.testing.assert_close(result["ghd_descriptors"][:, :, 4:], self.kwargs["ghd_coefficients"].expand(4, -1, -1))
        self.assertFalse(any(value.requires_grad for value in result.values()))

    def test_vertex_permutation_preserves_features_when_template_labels_follow(self):
        original = single_graph_features(**self.kwargs)
        p = torch.tensor([2, 0, 3, 1])
        inverse = torch.argsort(p)
        kwargs = dict(self.kwargs)
        for key in ("coordinates", "normals", "node_types", "ghd_modes", "cotangent_modes"):
            kwargs[key] = kwargs[key][p]
        for key in ("faces", "edge_index"):
            kwargs[key] = inverse[kwargs[key]]
        permuted = single_graph_features(**kwargs)
        for key in ("node_features", "ghd_descriptors", "cot_descriptors", "batch"):
            torch.testing.assert_close(permuted[key], original[key][p])

    def test_invalid_modes_and_boundary_indices_are_not_repaired_silently(self):
        with self.assertRaisesRegex(ValueError, "shapes"):
            single_graph_features(**dict(self.kwargs, cotangent_modes=torch.zeros(4, 15)))
        with self.assertRaisesRegex(ValueError, "node types"):
            single_graph_features(**dict(self.kwargs, node_types=torch.full((4,), 2, dtype=torch.long)))
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            single_graph_features(**dict(self.kwargs, ghd_coefficients=torch.full((8, 3), float("nan"))))

    def test_waveform_repetition_and_resampling_are_explicit(self):
        first = torch.linspace(.4, 1., 16)
        repeated = torch.cat((first.repeat(5), first[:1]))
        sampled = resample_repeated_waveform(repeated, samples=32)
        torch.testing.assert_close(sampled, torch.linspace(.4, 1., 32))
        repeated[20] += .1
        with self.assertRaisesRegex(ValueError, "segments differ"):
            resample_repeated_waveform(repeated)


if __name__ == "__main__":
    unittest.main()
