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

One phase requires one native model forward; an80-phase cycle requires80.
The wrapper does not replace that path with a cheap multi-output head or
retain a learned geometry encoding across phase-dependent inputs. It uses one
geometry per forward, so the original no-mask PyTorch SDPA backend is selected
naturally, without monkeypatching xFormers or attention. Future batching,
phase-exposure budgets, memory and full-cycle timing must be reported separately.

Source-sized synthetic tests of the actual external core are private and
separate from dependency-free wrapper tests. Full13902-node GPU feasibility,
native snapshot training, complete curves and multiseed performance remain
required before adding a measured LaB-GATr row to the paper. No arbitrary
accuracy gate or performance claim is introduced by this interface.
