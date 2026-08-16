# AneuG processed-v4 D6 train-field audit registration

**State · 2026-08-16:** D6 is registered but not activated. It has read no
train, validation, outer-test or auxiliary tensor value and has submitted no
PBS/GPU job. The immutable D5 outcome permits this registration; it does not
itself authorize the field read. A fresh human-selected executable contract is
required, and this registration may not be mutated into it.

## Why D6 exists

D5 established a leakage-aware synthetic-geometry split without reading a
field: 406 train, 51 validation and 51 outer components. Before choosing a
network, D6 asks the logically prior question:

> Do the 406 training tensors form a finite, tangent, temporally nontrivial
> surface-vector target whose cycle moments are sufficiently identified for a
> field-and-functional surrogate?

This is not a repair of the transport-era cycle-functional P0. That closed
version predated acquisition and D5, required at least 700 cases, had no split
and never reached either processed object. D6 uses the exact 578-case snapshot,
the frozen D5 split and train-only field access. Its endpoint is data admission,
not a model result.

## Exact physical decoder

The pinned official `assemble_registered_transient_data` implementation
normalizes every channel as

\[
z=(x-\mu)/(\sigma+10^{-5}).
\]

D6 therefore recovers physical channels as

\[
x=z(\sigma+10^{-5})+\mu.
\]

The separate official cycle helper uses `std + 1e-6` when decoding WSS. D6
does not silently choose between them: the preprocessing inverse above is the
primary decoder, while the helper convention is recorded only as a sensitivity
diagnostic. The steady `tensor_norm` is release-decoding metadata. It is never
reused as model-fitted normalization; future model statistics must be recomputed
from the 406 D5-train geometries only.

Primary source: [pinned official `loaders.py`](https://github.com/WenHaoDing/AneuG-Flow/blob/4a090a0f12538deef6fcea88b81afe78ce38152e/new_version/loaders.py),
[pinned official `datasets_cycle.py`](https://github.com/WenHaoDing/AneuG-Flow/blob/4a090a0f12538deef6fcea88b81afe78ce38152e/new_version/datasets_cycle.py).

## Method-free quantities

For physical WSS \(\tau_t(x)\), D6 computes

\[
m(x)=\mathbb E_t[\tau_t(x)],\qquad
a(x)=\mathbb E_t[\|\tau_t(x)\|],\qquad
r_t(x)=\tau_t(x)-m(x).
\]

TAWSS is \(a\), OSI is
\(\tfrac12(1-\|m\|/a)\) where \(a>0\), and the RRT denominator is
\(\|m\|\). D6 does not turn an arbitrary epsilon-clipped RRT into a headline
endpoint. Instead it records the denominator support and near-zero fraction.
Jensen's inequality requires \(a\geq\|m\|\); violations beyond the registered
relative tolerance fail the gate.

These moments motivate, but do not yet select, a compact future mechanism. A
periodic decoder could predict \(m\), \(a\) and a zero-mean residual shape,
then solve one nonnegative scale per vertex so the reconstructed cycle has the
predicted mean vector and mean magnitude exactly. This is preferable to
attaching unrelated direct TAWSS/OSI/RRT heads because all endpoints remain
derived from the same vector cycle. It is still only a candidate application
mechanism: generic hard output transforms, tangent projection, temporal heads
and endpoint losses are prior art, not novelty.

## Prospective all-or-none gate

D6 will, if separately activated, read only the 406 private train IDs. It will
not index validation, outer-test or auxiliary tensor values. A single CPU-only
pass checks:

1. exact transient, steady and D5-manifest byte identities and train digest;
2. exact labels, 80 phases, 13,902 nodes and finite physical decoding;
3. phase-static coordinates/normals and normalization round-trip;
4. shared triangular connectivity, nondegenerate faces and agreement between
   stored and area-weighted mesh normals;
5. WSS tangency above a case-relative 1%-of-p99 magnitude mask;
6. nonzero temporal residual in every train case, positive TAWSS support,
   finite/nonconstant cycle endpoints and the Jensen moment cone;
7. private train-only channel/endpoint statistics for later development.

The tangency median/p95 limits 0.05/0.25 are inherited from the already closed
surface-vector control rather than tuned after this payload. Equal-width
10,000-bin histograms make aggregate quantiles bounded and reproducible without
retaining hundreds of millions of point-time values.

## Consequences

- **Pass:** permits registration of bounded train/validation baseline
  development. It does not expose outer-test fields or create a paper claim.
- **Scientific fail:** closes D6. The observed target defect determines whether
  to abandon the field or register a genuinely new target-repair problem.
- **Execution incomplete:** closes D6 without reader, threshold or same-contract
  rerun.

The prospective execution envelope is one `introai9` PBS job, CPU 4, 64 GB,
GPU 0. `junjinyong` is prohibited. No login-node GPU is allowed. The public
static site is deliberately outside this workflow.

