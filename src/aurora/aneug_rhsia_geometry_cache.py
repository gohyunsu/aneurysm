"""Bounded CPU reuse of immutable RHSIA input descriptors, never learned PE.

The provider owns a fixed, admitted spectral archive and topology. Its context
digest binds that immutable source and preprocessing. Every lookup additionally
hashes the actual coordinates/normals, so changed scale, pose or in-place tensor
edits cannot return stale features. Targets are neither inspected nor forwarded.
This is execution infrastructure, not a new model or a measured speedup.
"""
from __future__ import annotations

from collections import OrderedDict
import hashlib
import re

import torch


FEATURE_KEYS = frozenset(("node_features", "ghd_descriptors", "cot_descriptors", "edge_index", "batch"))


def _cpu_tensor_digest(value):
    if (not isinstance(value, torch.Tensor) or value.device.type != "cpu"
            or value.requires_grad or not value.is_floating_point()
            or not bool(torch.isfinite(value).all())):
        raise ValueError("fixed finite floating CPU geometry without gradients required")
    raw = value.detach().contiguous().view(torch.uint8).numpy().tobytes()
    h = hashlib.sha256(str((tuple(value.shape), str(value.dtype))).encode())
    h.update(raw)
    return h.digest()


def _owned_descriptors(features):
    if set(features) != FEATURE_KEYS:
        raise ValueError("only native geometry descriptor keys may be cached")
    owned = {}
    for key, value in features.items():
        if (not isinstance(value, torch.Tensor) or value.device.type != "cpu"
                or value.requires_grad or value.grad_fn is not None):
            raise ValueError("learned or non-CPU features cannot enter the geometry cache")
        if value.is_floating_point() and not bool(torch.isfinite(value).all()):
            raise ValueError("nonfinite geometry descriptor")
        owned[key] = value.detach().clone()
    return owned


class RHSIAGeometryCache:
    """One immutable provider context, a byte/count-bounded LRU, owned outputs.

    ``context_sha256`` must be regenerated when the provider's spectral archive,
    topology, row mapping or preprocessing changes. Do not mutate that provider
    behind the cache. This wrapper deliberately receives no trainable module.
    Zero capacity or an oversized entry merely disables reuse, not execution.
    """
    def __init__(self, provider, *, context_sha256, max_entries, max_bytes):
        if (not callable(provider) or not isinstance(context_sha256, str)
                or not re.fullmatch(r"[0-9a-f]{64}", context_sha256)
                or isinstance(provider, torch.nn.Module)
                or isinstance(getattr(provider, "__self__", None), torch.nn.Module)):
            raise ValueError("callable admitted provider and immutable context digest required")
        if any(type(v) is not int or v < 0 for v in (max_entries, max_bytes)):
            raise ValueError("nonnegative integer cache bounds required")
        self.provider, self.context_sha256 = provider, context_sha256
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self._entries = OrderedDict()
        self.bytes = self.peak_bytes = self.hits = self.misses = self.evictions = 0
        self.oversized_entries = 0

    def __call__(self, identity, case):
        if type(identity) not in (str, int):
            raise ValueError("explicit admitted string/integer geometry identity required")
        # Do not iterate over case keys: a lazy mapping may decode targets there.
        geometry = {key: case[key] for key in ("coordinates", "normals")}
        key = (self.context_sha256, identity,
               _cpu_tensor_digest(geometry["coordinates"]), _cpu_tensor_digest(geometry["normals"]))
        if key in self._entries:
            self.hits += 1
            features, size = self._entries.pop(key)
            self._entries[key] = (features, size)
            # Caller mutation cannot corrupt a later lookup.
            return {name: value.clone() for name, value in features.items()}
        self.misses += 1
        features = _owned_descriptors(self.provider(identity, geometry))
        size = sum(v.numel() * v.element_size() for v in features.values())
        if not self.max_entries or size > self.max_bytes:
            self.oversized_entries += int(size > self.max_bytes)
            return features
        # Keep one context/identity version, not stale copies after augmentation.
        for stale in [k for k in self._entries if k[:2] == key[:2]]:
            _, removed = self._entries.pop(stale)
            self.bytes -= removed
            self.evictions += 1
        while self._entries and (len(self._entries) >= self.max_entries or self.bytes + size > self.max_bytes):
            _, (_, removed) = self._entries.popitem(last=False)
            self.bytes -= removed
            self.evictions += 1
        self._entries[key] = (features, size)
        self.bytes += size
        self.peak_bytes = max(self.peak_bytes, self.bytes)
        return {name: value.clone() for name, value in features.items()}

    def statistics(self):
        return dict(entries=len(self._entries), bytes=self.bytes, peak_bytes=self.peak_bytes,
                    hits=self.hits, misses=self.misses, evictions=self.evictions,
                    oversized_entries=self.oversized_entries, max_entries=self.max_entries,
                    max_bytes=self.max_bytes, learned_encodings_cached=False,
                    target_values_read=False, context_sha256=self.context_sha256)
