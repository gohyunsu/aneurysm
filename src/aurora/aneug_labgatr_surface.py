"""Task interface for the external, unmodified official LaB-GATr surface model.

No third-party core is replaced here. The private builder supplies its actual
Data, pooling transform, PGA interface functions and LaBGATr class. This adapter
uses native phase-conditioned predictions, not an 80-channel one-shot shortcut.
"""
from __future__ import annotations

import math
from typing import Mapping

import torch
from torch import nn

PATCH_KEYS = ("scale0_sampling_index", "scale0_pool_source", "scale0_pool_target",
              "scale0_interp_source", "scale0_interp_target")


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _positions(case):
    pos = case["coordinates"]
    _require(pos.ndim == 2 and pos.shape[1] == 3 and pos.shape[0] >= 3,
             "surface coordinates must be [N,3]")
    _require(pos.is_floating_point() and bool(torch.isfinite(pos).all()), "finite coordinates")
    return pos


def prepare_labgatr_patches(case, *, data_factory, transform, seed: int):
    """Run official geometry-only FPS/kNN once, preserving the CPU RNG state.

    Keep these metadata with the admitted case; do not recompute stochastic
    patching for each phase or inspect target fields to choose patches.
    """
    pos = _positions(case)
    _require(pos.device.type == "cpu", "prepare geometry patches on CPU before training")
    _require(type(seed) is int and seed >= 0, "nonnegative patch seed")
    with torch.random.fork_rng(devices=[]):
        torch.random.default_generator.manual_seed(seed)
        data = transform(data_factory(pos=pos.detach().clone()))
    result = {"lab_patch_coordinates": pos.detach().clone()}
    for key in PATCH_KEYS:
        value = data[key]
        _require(value.dtype in (torch.int32, torch.int64) and value.ndim == 1, "patch index tensor")
        result["lab_" + key] = value.detach().clone().long()
    validate_labgatr_patches(dict(coordinates=pos, **result))
    return result


def validate_labgatr_patches(case):
    pos = _positions(case)
    _require(torch.equal(case["lab_patch_coordinates"], pos), "patches belong to different coordinates")
    indices = {key: case["lab_" + key] for key in PATCH_KEYS}
    n, m = len(pos), len(indices["scale0_sampling_index"])
    _require(3 <= m <= n, "at least three sampled surface points required")
    for key, value in indices.items():
        upper = n if key in ("scale0_sampling_index", "scale0_pool_source", "scale0_interp_target") else m
        _require(value.ndim == 1 and value.dtype == torch.long and value.device == pos.device,
                 "patch index dtype/device")
        _require(value.numel() > 0 and bool(((value >= 0) & (value < upper)).all()), "patch index range")
    _require(indices["scale0_sampling_index"].unique().numel() == m, "duplicate sampled point")
    for role, count in (("pool", 1), ("interp", 3)):
        source, target = indices[f"scale0_{role}_source"], indices[f"scale0_{role}_target"]
        _require(source.numel() == target.numel() == n * count, "surface patch edge count")
        fine = source if role == "pool" else target
        _require(bool((torch.bincount(fine, minlength=n) == count).all()), "patches do not cover all surface nodes")
    return indices


class SurfacePGAInterface:
    """Use original GATr point/plane embeddings and vector extraction functions."""
    num_input_channels = 2
    num_output_channels = 1
    num_output_scalars = None

    def __init__(self, *, include_ghd, embed_point, embed_oriented_plane, extract_oriented_plane):
        _require(type(include_ghd) is bool, "explicit geometry/GHD information condition")
        self.num_input_scalars = 4 + (432 if include_ghd else 0)
        self.embed_point, self.embed_plane, self.extract_plane = embed_point, embed_oriented_plane, extract_oriented_plane

    def embed(self, data):
        multivectors = torch.stack((self.embed_point(data.pos),
            self.embed_plane(normal=data.orientation, position=data.pos)), dim=1)
        return multivectors, data.x

    def dislodge(self, multivectors, scalars):
        return self.extract_plane(multivectors).squeeze(-2)


class LaBGATrSurfaceSnapshot(nn.Module):
    """Native snapshot control with full-cycle evaluation and explicit GHD scope.

    Standardized Cartesian GHD coefficients are not rotation-invariant scalars.
    The +GHD condition retains information parity, not an end-to-end E(3) claim.
    Geometry-only is a separate control, not a silently weakened replacement.
    """
    def __init__(self, core: nn.Module, *, data_factory, output_scale: float, include_ghd: bool,
                 batch_factory=None):
        super().__init__()
        _require(type(include_ghd) is bool, "explicit information condition")
        _require(math.isfinite(output_scale) and output_scale > 0, "positive train-only output scale")
        self.core, self.data_factory, self.include_ghd = core, data_factory, include_ghd
        self.batch_factory = batch_factory
        self.register_buffer("output_scale", torch.tensor(float(output_scale)))

    def _data(self, case: Mapping[str, torch.Tensor], phase: int | None):
        _require(phase is None or type(phase) is int and 0 <= phase < 80, "native phase index 0..79 or masked steady")
        pos = _positions(case)
        normals, area = case["normals"], case["vertex_weights"]
        _require(normals.shape == pos.shape and bool(torch.isfinite(normals).all()), "surface normals")
        _require(area.shape == (len(pos),) and bool(torch.isfinite(area).all()) and bool((area > 0).all()), "positive vertex areas")
        indices = validate_labgatr_patches(case)
        # Area and nominal periodic phase are dimensionless; missing time is
        # explicit and never equated with transient phase zero or cycle mean.
        angle = 0.0 if phase is None else 2 * math.pi * phase / 80
        condition = pos.new_tensor([0.0, 0.0, 1.0] if phase is None else
                                   [math.sin(angle), math.cos(angle), 0.0])
        scalar = [area[:, None] / area.mean(), condition[None].expand(len(pos), -1)]
        if self.include_ghd:
            ghd = case["ghd"]
            _require(ghd.shape == (432,) and bool(torch.isfinite(ghd).all()), "432 train-standardized GHD coefficients")
            scalar.append(ghd[None].expand(len(pos), -1))
        return self.data_factory(pos=pos, orientation=normals, x=torch.cat(scalar, dim=-1),
                                 batch=None, **indices)

    def forward_snapshot(self, case, phase: int | None):
        data = self._data(case, phase)
        return self._forward_data(data)

    def _forward_data(self, data):
        try:
            prediction = self.core(data)
            _require(prediction.shape == data.pos.shape, "original core must output one surface vector")
            return prediction * self.output_scale
        finally:
            # The original tokeniser stores forward-local tensors for lifting.
            # Clear its completed-call cache, not a learned state or checkpoint.
            tokeniser = getattr(self.core, "tokeniser", None)
            if tokeniser is not None and hasattr(tokeniser, "cache"):
                tokeniser.cache = None

    def forward_snapshot_batch(self, cases, phases):
        """One original-core graph batch, not sequential gradient accumulation.

        Original Data.__inc__ offsets fine and coarse indices independently;
        original attention masks and per-graph reference multivectors isolate
        geometries. The native upstream masked backend is not replaced here.
        """
        _require(len(cases) == len(phases) > 0, "nonempty matched snapshot microbatch")
        if len(cases) == 1:
            return (self.forward_snapshot(cases[0], phases[0]),)
        records = [self._data(case, phase) for case, phase in zip(cases, phases)]
        factory = self.batch_factory
        if factory is None:
            from torch_geometric.data import Batch
            factory = Batch.from_data_list
        data = factory(records)
        sizes = [len(record.pos) for record in records]
        device = records[0].pos.device
        expected = torch.cat([torch.full((size,), index, device=device, dtype=torch.long)
                              for index, size in enumerate(sizes)])
        _require(torch.equal(data.batch, expected), "original batch must retain contiguous graph ownership")
        samples = data.scale0_sampling_index
        # Source Data offsets pool/interpolation index spaces differently.
        # Check the integer ownership boundary, not approximate vector equality.
        owners = data.batch[samples]
        _require(bool((owners[1:] >= owners[:-1]).all()), "sampled graph order")
        for role in ("pool", "interp"):
            source, target = data[f"scale0_{role}_source"], data[f"scale0_{role}_target"]
            left = data.batch[source] if role == "pool" else owners[source]
            right = owners[target] if role == "pool" else data.batch[target]
            _require(torch.equal(left, right), "patch edge crosses batched geometries")
        return tuple(self._forward_data(data).split(sizes))

    def forward_single_field(self, case):
        return self.forward_snapshot(case, None)

    def forward(self, case, phase):
        return self.forward_snapshot(case, phase)

    def forward_cycle(self, case, *, phase_batch_size=1):
        _require(not self.training, "train via native snapshots, not 80 retained full graphs")
        _require(type(phase_batch_size) is int and 1 <= phase_batch_size <= 80, "phase batch size 1..80")
        fields = []
        for start in range(0, 80, phase_batch_size):
            phases = list(range(start, min(start + phase_batch_size, 80)))
            fields.extend(self.forward_snapshot_batch([case] * len(phases), phases))
        return torch.stack(fields)
