# Original-core LaB-GATr surface control

This is an explicit task adaptation of the [official LaB-GATr implementation](https://github.com/sukjulian/lab-gatr),
not a new model or an exact reproduction of the unavailable 2025 AAA training
application. The original model and its recommended GATr fork stay external,
unmodified and checksum-pinned. Interface unit tests alone do not establish
that the original core, full-resolution GPU training or a baseline result works.

## Information and execution

The interface embeds positions as PGA points and surface normals as oriented
planes with the original GATr functions. Relative vertex area and nominal
sin/cos phase are scalar inputs. Missing time has its own indicator and zero
phase features; independently supervised steady WSS is not equated with phase0
or the transient mean. One vector field is extracted using the original
oriented-plane extractor. Inference never requires actual steady CFD.

Two explicit conditions are available: geometry-only and geometry plus the
same432 training-standardized GHD coefficients as current comparators. The
second is the information-matched comparison condition. These Cartesian
coefficients are not invariant scalars under a physical rotation: importing a
geometric algebra core therefore does not establish end-to-end E(3) equivariance
for the +GHD condition. Geometry-only is an additional control, not a silent
replacement with less information. Semantic inlet/outlet labels are not invented.

The source-sized recipe retains8 multivector channels,10 blocks and4 heads
from the official main example. Native cross-attention patching uses the
original FPS/kNN transform at1% sampling, with3-neighbor surface interpolation.
This is a surface/phase/input adaptation of the generic implementation, not a
claim to reproduce its volume-task features, optimizer or published scores.
Geometry patching runs once before training with a preserved CPU RNG state;
coordinate binding prevents accidental reuse on another geometry.

## Native cost and testing

An80-phase cycle requires80 phase-conditioned graph encodings. Serial
execution uses80 model calls; phase batches of size B use ceil(80/B) calls,
still evaluating all80 graphs. The wrapper neither substitutes a multi-output
head nor caches a learned phase-dependent encoding. Single-graph execution
uses the original no-mask PyTorch SDPA path. Genuine batches use original
Data fine/coarse offsets, graph-specific reference multivectors and original
xFormers block-diagonal attention masks. No attention implementation is patched.
Integer ownership checks reject patch edges crossing graph boundaries.

`aneug_labgatr_snapshot_training` connects the original core to the same
physical snapshot sampler, loss, full-cycle evaluator and checkpoint engine
as the direct phase-conditioned comparator, while retaining distinct LaB-GATr
result/checkpoint identities. Separate train/validation/eligible-steady
providers cache only geometry metadata with a bounded CPU LRU; no labels or
learned encodings enter that cache. Cache hits are checked against geometry.
Steady time is explicitly missing, never phase zero or a cycle-mean target.

Full geometry-times-phase enumeration and balanced phase subsampling are
different training budgets. The engine records phase targets, steady fields,
graph encodings, model calls, optimizer updates and full-cycle validation
separately. A native snapshot epoch is not a one-shot cycle epoch. Averaging
all80 snapshot losses recovers the common case-relative cycle objective,
because each uses full reference-cycle energy, not its own phase energy.
This physical objective is a task adaptation, not the author's exact recipe.

Regression tests cover explicit fixture batching/ownership, mixed supervision,
phase accounting, geometry-only caching and dropout-exact epoch continuation.
They do not establish original-core CUDA batching: that additionally needs
actual original Data/xFormers forward, backward, graph-isolation and cost
measurements in the pinned GPU environment. Preserve completed serial
measurements; native batching is a distinct execution path to verify.

Source-sized synthetic tests of the actual external core are private and
separate from dependency-free wrapper tests. Full13902-node GPU feasibility,
native snapshot training, complete curves and multiseed performance remain
required before adding a measured LaB-GATr row to the paper. No arbitrary
accuracy gate or performance claim is introduced by this interface.
