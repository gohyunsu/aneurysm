"""Original-core LaB-GATr interface to the shared physical snapshot engine.

Only geometry patch metadata may be cached. Phase-dependent learned tensors
are recomputed. T/S sampling, case-relative loss, all-phase metrics and exact
epoch-boundary continuation are shared with the direct snapshot comparator.
"""
from __future__ import annotations

from collections import OrderedDict
import math

import torch

from aurora.aneug_labgatr_surface import LaBGATrSurfaceSnapshot, prepare_labgatr_patches
from aurora.aneug_rhsia_snapshot_training import train_snapshots


class LaBGATrGeometryProvider:
    """Bounded geometry-only LRU; never fit patches using target WSS or phase."""
    def __init__(self, *, data_factory, transform, include_ghd, seed, cache_size):
        if type(cache_size) is not int or cache_size < 1 or type(include_ghd) is not bool:
            raise ValueError("explicit information condition and positive geometry cache size")
        self.data_factory, self.transform = data_factory, transform
        self.include_ghd, self.seed, self.cache_size = include_ghd, seed, cache_size
        self.cache = OrderedDict()
        self.patch_constructions = 0

    def __call__(self, index, case):
        # Separate providers own train, validation and eligible steady index
        # spaces. Actual geometry values still bind every cache hit.
        keys = ("coordinates", "normals", "vertex_weights") + (("ghd",) if self.include_ghd else ())
        feature = {key: case[key] for key in keys}
        if any(value.device.type != "cpu" for value in feature.values()):
            raise ValueError("geometry provider accepts CPU inputs only")
        previous = self.cache.pop(index, None)
        if previous is not None:
            if any(not torch.equal(previous[key], feature[key]) for key in keys):
                raise ValueError("geometry cache key reused for different inputs")
            self.cache[index] = previous
            return previous
        patches = prepare_labgatr_patches(feature, data_factory=self.data_factory,
                                         transform=self.transform, seed=self.seed)
        result = {key: value.detach().clone() for key, value in feature.items()}
        result.update(patches)
        self.cache[index] = result
        if len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)
        self.patch_constructions += 1
        return result


class LaBGATrSnapshotBackend:
    name = "labgatr"

    def __init__(self, *, include_ghd, evaluation_phase_batch_size=1):
        if type(include_ghd) is not bool or type(evaluation_phase_batch_size) is not int or not 1 <= evaluation_phase_batch_size <= 80:
            raise ValueError("explicit LaB-GATr information and phase batching")
        self.include_ghd = include_ghd
        self.evaluation_phase_batch_size = evaluation_phase_batch_size

    @property
    def contract(self):
        return dict(name=self.name, include_ghd=self.include_ghd,
                    evaluation_phase_batch_size=self.evaluation_phase_batch_size,
                    native_phase_conditioned=True, full_cycle_graph_encodings=80,
                    batching="original_Data_offsets_masks_and_graph_reference_multivectors",
                    original_core_modified=False, actual_steady_CFD_at_inference=False)

    def validate_model(self, model, phases, output_scale):
        if (not isinstance(model, LaBGATrSurfaceSnapshot) or phases != 80
                or model.include_ghd != self.include_ghd
                or not math.isclose(float(model.output_scale), output_scale, rel_tol=1e-6)):
            raise ValueError("native LaB-GATr model, phase or train-only scale mismatch")

    def predict_batch(self, model, features, phases, device):
        moved = [{key: value.to(device) for key, value in feature.items()} for feature in features]
        # -1 is the shared scheduler's missing-time steady sentinel.
        return model.forward_snapshot_batch(moved, [None if phase == -1 else phase for phase in phases])

    def predict_cycle(self, model, features):
        return model.forward_cycle(features, phase_batch_size=self.evaluation_phase_batch_size)

    def evaluation_counts(self, phases):
        return dict(graphs=phases, model_calls=math.ceil(phases / self.evaluation_phase_batch_size))


def train_labgatr_snapshots(model, train, validation, *, backend, **kwargs):
    if not isinstance(backend, LaBGATrSnapshotBackend):
        raise ValueError("explicit native LaB-GATr backend required")
    return train_snapshots(model, train, validation, waveform=None, period=None,
                           output_scale=float(model.output_scale), native_backend=backend, **kwargs)
