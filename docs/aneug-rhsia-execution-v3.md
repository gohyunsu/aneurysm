# RHSIA execution efficiency without changing the model

The source-sized comparator has two eight-layer per-node spectral Transformers
and eight phase-conditioned GPS blocks. Its node-wise spectral implementation
already supports bounded node chunks and gradient-checkpoint recomputation.
Chunk size changes execution and memory, not layer widths or parameter count.
With dropout enabled, changing chunk boundaries need not preserve a particular
seed's dropout realization. Do not claim bit-identical training across those
profiles. Full geometry/phase coverage and the measured budget remain explicit.

`RHSIAGeometryCache` only reuses fixed CPU input descriptors produced by the
admitted, immutable spectral/topology provider. It receives coordinates and
normals, never target fields. The provider context has an explicit digest and
each lookup hashes the actual geometry contents, including in-place changes.
Entry-count and byte limits bound an LRU; oversized entries are computed
normally without reuse. Returned tensors are owned copies, so caller mutation
does not corrupt later lookups. Changing the spectral archive, row mapping,
topology or preprocessing requires a new provider/context/cache.

This is not a cache of learned spectral embeddings, graph messages or model
predictions. The native trainable encoders still execute after every lookup,
with fresh gradients after each optimizer update. This distinction is necessary
for valid learning. Cache precomputation, misses, hits, CPU memory and transfer
time must be included in the actual execution report. A few repeatedly used
steady samples cannot establish the hit rate of a large steady training pool.

Six synthetic regressions cover exact descriptor reuse, untouched RNG,
target-access traps, actual geometry changes, returned-tensor mutation,
count/byte bounds and fresh model gradients. These tests do not establish an
actual full-size speedup. No deployed baseline or scientific result is changed
by this module; an activated runtime must separately integrate and measure it.

Mixed precision is another execution candidate, not architectural novelty or
FP32 numerical equivalence. Use the actual pinned runtime's
[PyTorch 2.5.1 autocast implementation](https://github.com/pytorch/pytorch/blob/v2.5.1/torch/amp/autocast_mode.py)
and [AMP guidance](https://github.com/pytorch/pytorch/blob/v2.5.1/docs/source/amp.rst),
retain FP32 physical losses/metrics, check actual GPU operators and gradients,
and record the chosen precision. No mixed-precision training is activated here.
