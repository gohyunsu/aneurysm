"""Dependency-free adapter tests; actual upstream-core checks are separate."""
import types
import unittest
import torch
from torch import nn

from aurora.aneug_labgatr_surface import LaBGATrSurfaceSnapshot, prepare_labgatr_patches, validate_labgatr_patches


class Data(dict):
    def __getattr__(self, name):
        return self[name]


def batch_factory(records):
    """Fixture-only collation; actual upstream Data/PyG checks are separate."""
    fields = {key: [] for key in ("pos", "orientation", "x", "batch", "scale0_sampling_index",
              "scale0_pool_source", "scale0_pool_target", "scale0_interp_source", "scale0_interp_target")}
    fine, coarse = 0, 0
    for index, data in enumerate(records):
        n, m = len(data.pos), len(data.scale0_sampling_index)
        for key in ("pos", "orientation", "x"):
            fields[key].append(data[key])
        fields["batch"].append(torch.full((n,), index, dtype=torch.long, device=data.pos.device))
        for key in ("scale0_sampling_index", "scale0_pool_source", "scale0_interp_target"):
            fields[key].append(data[key] + fine)
        for key in ("scale0_pool_target", "scale0_interp_source"):
            fields[key].append(data[key] + coarse)
        fine, coarse = fine + n, coarse + m
    return Data({key: torch.cat(parts) for key, parts in fields.items()})


def fixture():
    pos = torch.arange(18, dtype=torch.float32).reshape(6, 3) / 10
    return dict(coordinates=pos, normals=torch.ones(6, 3) / 3 ** .5,
        vertex_weights=torch.ones(6), ghd=torch.ones(432), lab_patch_coordinates=pos.clone(),
        lab_scale0_sampling_index=torch.tensor([0, 2, 4]),
        lab_scale0_pool_source=torch.arange(6), lab_scale0_pool_target=torch.arange(6) % 3,
        lab_scale0_interp_source=torch.arange(3).repeat(6),
        lab_scale0_interp_target=torch.arange(6).repeat_interleave(3))


class Core(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(.1))
        self.tokeniser = types.SimpleNamespace(cache=None)
        self.calls = []

    def forward(self, data):
        self.calls.append(data.x.detach().clone())
        self.tokeniser.cache = data
        return self.weight * (data.orientation + data.x.sum(-1, keepdim=True))


class AdapterTests(unittest.TestCase):
    def model(self, ghd=True):
        return LaBGATrSurfaceSnapshot(Core(), data_factory=Data, output_scale=2., include_ghd=ghd,
                                     batch_factory=batch_factory)

    def test_one_actual_batch_call_preserves_independent_geometry_phase_inputs(self):
        model, first, second = self.model(), fixture(), fixture()
        second["ghd"] = second["ghd"] * 2
        expected = (model(first, 19), model(second, None))
        model.core.calls.clear()
        predicted = model.forward_snapshot_batch([first, second], [19, None])
        self.assertEqual(len(model.core.calls), 1)
        for observed, reference in zip(predicted, expected):
            torch.testing.assert_close(observed, reference)
        sum(p.square().mean() for p in predicted).backward()
        self.assertIsNotNone(model.core.weight.grad)
        self.assertIsNone(model.core.tokeniser.cache)

    def test_incorrect_coarse_offsets_are_rejected_before_core_forward(self):
        model = self.model()
        def broken(records):
            data = batch_factory(records)
            data["scale0_pool_target"][6:] -= 3
            return data
        model.batch_factory = broken
        with self.assertRaisesRegex(ValueError, "crosses"):
            model.forward_snapshot_batch([fixture(), fixture()], [0, 1])
        self.assertEqual(model.core.calls, [])

    def test_phase_batching_retains_all_native_phases_and_partial_last_batch(self):
        model, case = self.model(), fixture()
        model.eval()
        with torch.no_grad():
            serial = model.forward_cycle(case)
            model.core.calls.clear()
            batched = model.forward_cycle(case, phase_batch_size=9)
        self.assertEqual(len(model.core.calls), 9)
        self.assertEqual(model.core.calls[-1].shape[0], 8 * 6)
        torch.testing.assert_close(serial, batched)
        for size in (0, 81, True):
            with self.assertRaises(ValueError):
                model.forward_cycle(case, phase_batch_size=size)

    def test_native_all_80_phases_are_distinct_calls_and_masked_steady_is_not_phase_zero(self):
        model, case = self.model(), fixture()
        with self.assertRaisesRegex(ValueError, "native snapshots"):
            model.forward_cycle(case)
        model.eval()
        with torch.no_grad():
            cycle = model.forward_cycle(case)
            self.assertEqual(len(model.core.calls), 80)
            self.assertEqual(cycle.shape, (80, 6, 3))
            model.forward_single_field(case)
        self.assertEqual(model.core.calls[0][0, 1:4].tolist(), [0., 1., 0.])
        self.assertEqual(model.core.calls[-1][0, 1:4].tolist(), [0., 0., 1.])
        self.assertIsNone(model.core.tokeniser.cache)

    def test_only_admitted_geometry_and_optional_GHD_enter_original_core(self):
        class Guard(dict):
            def __getitem__(self, key):
                if key in {"wss", "steady_wss", "case_id", "ghd"}:
                    raise AssertionError("forbidden feature read: " + key)
                return super().__getitem__(key)
        geometry = self.model(False)
        geometry.forward_snapshot(Guard(fixture()), 79).square().mean().backward()
        self.assertIsNotNone(geometry.core.weight.grad)
        self.assertEqual(geometry.core.calls[-1].shape, (6, 4))
        augmented = self.model()
        augmented.forward_snapshot(fixture(), 79)
        self.assertEqual(augmented.core.calls[-1].shape, (6, 436))
        changed = fixture()
        changed["ghd"] = changed["ghd"] * 2
        self.assertFalse(torch.equal(augmented.forward_snapshot(fixture(), 9), augmented.forward_snapshot(changed, 9)))

    def test_wrong_patch_geometry_or_coverage_is_rejected(self):
        case = fixture()
        case["coordinates"] = case["coordinates"] + 1
        with self.assertRaisesRegex(ValueError, "different coordinates"):
            self.model().forward_snapshot(case, 1)
        case = fixture()
        case["lab_scale0_interp_target"][0] = 2
        with self.assertRaisesRegex(ValueError, "cover"):
            validate_labgatr_patches(case)

    def test_patching_uses_official_transform_interface_without_targets_or_RNG_drift(self):
        seen = []
        def transform(data):
            seen.append(set(data))
            torch.rand(10)
            case = fixture()
            for name in list(case):
                if name.startswith("lab_scale"):
                    data[name[4:]] = case[name]
            return data
        torch.manual_seed(51)
        before = torch.get_rng_state().clone()
        result = prepare_labgatr_patches(fixture(), data_factory=Data, transform=transform, seed=9)
        self.assertTrue(torch.equal(before, torch.get_rng_state()))
        self.assertEqual(seen, [{"pos"}])
        self.assertEqual(len(result), 6)

    def test_invalid_phase_and_shape_are_not_silent_inputs(self):
        for phase in (-1, 80, True, .5):
            with self.assertRaises(ValueError):
                self.model().forward_snapshot(fixture(), phase)
        case = fixture()
        case["ghd"] = torch.ones(3)
        with self.assertRaisesRegex(ValueError, "432"):
            self.model().forward_snapshot(case, 0)


if __name__ == "__main__":
    unittest.main()
