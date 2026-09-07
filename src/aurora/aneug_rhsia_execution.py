"""Explicit execution-only wrapper around an unchanged native RHSIA core.

No layer, parameter or phase is removed. Checkpoints record the wrapper's
``core.`` namespace and the caller must bind the profile in provenance. Chunk
boundaries can change dropout realizations; BF16 is not FP32 equivalence.
"""
from __future__ import annotations

from contextlib import nullcontext

import torch
from torch import nn


class RHSIAExecutionAdapter(nn.Module):
    def __init__(self, core, *, node_chunk_size=512, precision="float32"):
        super().__init__()
        if (not isinstance(core, nn.Module) or not hasattr(core, "node_encoder")
                or not hasattr(core.node_encoder, "chunk_nodes") or not hasattr(core, "phases")):
            raise ValueError("native RHSIA core with explicit spectral chunking required")
        if type(node_chunk_size) is not int or node_chunk_size < 1:
            raise ValueError("positive integer execution chunk size required")
        if precision not in {"float32", "cuda_bfloat16"}:
            raise ValueError("explicit supported execution precision required")
        self.core = core
        self.core.node_encoder.chunk_nodes = node_chunk_size
        self.phases, self.precision = core.phases, precision
        self.execution_profile = dict(node_chunk_size=node_chunk_size, precision=precision,
            original_layers_and_parameters_retained=True, physical_output_dtype="float32" if precision == "cuda_bfloat16" else "unchanged",
            checkpoint_parameter_namespace="core.")

    def _context(self):
        if self.precision == "float32":
            return nullcontext()
        device = next(self.core.parameters()).device
        if device.type != "cuda" or not torch.cuda.is_bf16_supported():
            raise RuntimeError("BF16 profile requires an actually supported allocated CUDA device")
        return torch.autocast(device_type="cuda", dtype=torch.bfloat16)

    def _physical_output(self, value):
        # Loss/evaluation remain outside autocast in physical FP32. This does not
        # undo BF16 rounding or make mixed-precision training bit-identical.
        return value.float() if self.precision == "cuda_bfloat16" else value

    def forward_snapshot(self, features, phase_indices, waveform, *, period, output_scale):
        with self._context():
            value = self.core.forward_snapshot(features, phase_indices, waveform,
                period=period, output_scale=output_scale)
        return self._physical_output(value)

    @torch.no_grad()
    def forward_cycle(self, features, waveform, *, period, output_scale):
        if self.training:
            raise RuntimeError("native full-cycle evaluation requires eval mode")
        with self._context():
            value = self.core.forward_cycle(features, waveform, period=period, output_scale=output_scale)
        return self._physical_output(value)
