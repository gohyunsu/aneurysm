import copy
import unittest
import torch

from aurora.aneug_rhsia_geometry_cache import RHSIAGeometryCache


class PoisonTargets(dict):
    def __iter__(self):
        raise AssertionError("case keys must not be enumerated")

    def __getitem__(self, key):
        if key not in ("coordinates", "normals"):
            raise AssertionError("target or unrelated field was accessed")
        return super().__getitem__(key)


class GeometryCacheTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(17)
        self.case = PoisonTargets(coordinates=torch.randn(6, 3), normals=torch.randn(6, 3))
        self.calls = []

    def provider(self, identity, geometry):
        self.assertEqual(set(geometry), {"coordinates", "normals"})
        self.calls.append(identity)
        p, n = geometry["coordinates"], geometry["normals"]
        return dict(node_features=torch.cat((p, n, torch.ones(6, 4)), -1),
            ghd_descriptors=p[:, None, :1].expand(6, 8, 7),
            cot_descriptors=n[:, None, :1].expand(6, 16, 5),
            batch=torch.zeros(6, dtype=torch.long),
            edge_index=torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 5]]))

    def cache(self, **kwargs):
        return RHSIAGeometryCache(self.provider, context_sha256="a" * 64,
            **dict(dict(max_entries=2, max_bytes=100000), **kwargs))

    def test_bit_exact_reuse_does_not_read_targets_or_consume_rng(self):
        cache = self.cache()
        rng = torch.get_rng_state().clone()
        first, second = cache("admitted", self.case), cache("admitted", self.case)
        self.assertEqual(self.calls, ["admitted"])
        for key in first:
            torch.testing.assert_close(first[key], second[key], rtol=0, atol=0)
        self.assertTrue(torch.equal(torch.get_rng_state(), rng))
        self.assertEqual(cache.statistics()["hits"], 1)

    def test_inplace_geometry_and_normal_changes_cannot_reuse_stale_entries(self):
        cache = self.cache()
        first = cache(1, self.case)
        self.case["coordinates"].mul_(2)
        second = cache(1, self.case)
        self.assertFalse(torch.equal(first["node_features"], second["node_features"]))
        self.case["normals"].mul_(-1)
        cache(1, self.case)
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(cache.statistics()["entries"], 1)

    def test_returned_tensor_mutation_is_not_cached(self):
        cache = self.cache()
        first = cache(1, self.case)
        expected = first["node_features"].clone()
        first["node_features"].zero_()
        self.assertTrue(torch.equal(cache(1, self.case)["node_features"], expected))

    def test_count_bytes_and_disabled_cache_bound_execution_not_valid_data(self):
        cache = self.cache(max_entries=1)
        cache(1, self.case)
        cache(2, self.case)
        self.assertEqual(cache.statistics()["entries"], 1)
        self.assertEqual(cache.statistics()["evictions"], 1)
        for kwargs in (dict(max_entries=0), dict(max_bytes=1)):
            limited = self.cache(**kwargs)
            for _ in range(2):
                limited(1, self.case)
            self.assertEqual(limited.statistics()["entries"], 0)
            self.assertEqual(limited.statistics()["misses"], 2)

    def test_gradients_recompute_in_model_after_every_update(self):
        cache = self.cache()
        model = torch.nn.Linear(10, 3)
        reference = copy.deepcopy(model)
        for _ in range(3):
            model.zero_grad(set_to_none=True)
            reference.zero_grad(set_to_none=True)
            model(cache(1, self.case)["node_features"]).square().mean().backward()
            reference(self.provider(1, dict(coordinates=self.case["coordinates"],
                normals=self.case["normals"]))["node_features"]).square().mean().backward()
            with torch.no_grad():
                for p, q in zip(model.parameters(), reference.parameters()):
                    torch.testing.assert_close(p.grad, q.grad, rtol=0, atol=0)
                    p.add_(p.grad, alpha=-.01)
                    q.add_(q.grad, alpha=-.01)
        self.assertEqual(cache.statistics()["hits"], 2)
        self.assertFalse(cache.statistics()["learned_encodings_cached"])

    def test_learned_features_and_extra_target_keys_fail(self):
        def learned(identity, geometry):
            result = self.provider(identity, geometry)
            result["node_features"].requires_grad_()
            return result
        cache = RHSIAGeometryCache(learned, context_sha256="a" * 64, max_entries=1, max_bytes=100000)
        with self.assertRaisesRegex(ValueError, "learned"):
            cache(1, self.case)
        def extra(identity, geometry):
            return dict(self.provider(identity, geometry), wss=torch.zeros(6, 3))
        with self.assertRaisesRegex(ValueError, "keys"):
            RHSIAGeometryCache(extra, context_sha256="a" * 64,
                max_entries=1, max_bytes=100000)(1, self.case)
        module = torch.nn.Linear(3, 3)
        for provider in (module, module.forward):
            with self.assertRaises(ValueError):
                RHSIAGeometryCache(provider, context_sha256="a" * 64, max_entries=1, max_bytes=100000)
        self.case["coordinates"].requires_grad_()
        with self.assertRaisesRegex(ValueError, "geometry"):
            self.cache()(1, self.case)


if __name__ == "__main__":
    unittest.main()
