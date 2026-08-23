# Release-730 matched steady exposure schedule

## Why the eligible set is not enough

The matched-information table already requires the selected strongest control
and proposal to use the same 13,985 leakage-audited steady geometries. That
does not by itself guarantee equal exposure: different row orders or early
repetition can change optimization and be mistaken for a method effect.

This metadata-only component fixes the common exposure rule before either T+S
cell exists. It reads the private geometry-index manifest but no WSS value. It
also selects no backbone, objective weight, optimizer or checkpoint.

## Exact schedule

- The private eligible order is bound by case and index digests.
- Each transient epoch consumes 584 steady examples, one per transient case.
- A SHA-256-ranked permutation visits every eligible row once before starting
  another independently ranked cycle.
- The same seed, eligible order and prefix rule apply to the selected control
  and proposal.
- At the registered 80-epoch minimum, all 13,985 rows have been seen three or
  four times. At the 251-epoch ceiling, each has been seen ten or eleven times.
- Each terminal T+S result must report its completed epoch, number of steady
  examples and exact exposure-prefix digest.

The rule fixes exposure fairness, not architecture. The later selected models
must share their geometry encoder with a separate single-field steady-WSS head.
A steady field is never copied into 80 phases and receives no time or waveform
token. The exact loss integration and any bounded validation-only weight search
require a later version after the strongest transient control is known.

## Streaming implementation boundary

`MatchedSteadyStream` validates archive shape, normalizers and the private
eligible-index set without indexing the field tensor. During training it
decodes one scheduled row at a time from the mmap-backed archive, recomputes
mesh-derived normals and area weights, and uses the frozen transient-train GHD
normalizer. It never constructs `archive[eligible_indices]` or another eager
13,985-row field copy. An incremental ledger emits the exact consumed-prefix
digest required by the matched-information analyzer.

The steady target has shape `nodes × 3` and uses its own area-weighted
single-field relative objective. Reusing the transient `80 × nodes × 3` loss
would introduce an incorrect phase-axis interpretation, so the two objectives
are kept explicit. The eventual loss coefficient remains validation-only and
unselected.

The same single-field interface also supports the prospectively registered
T+M development control. T+M makes a second geometry pass over a training
transient case and uses its 80-phase mean vector WSS as the `nodes × 3` target.
Both registered comparator classes expose output-equivalent
`encode_geometry`/`decode_cycle` methods, and `SharedEncoderSingleFieldAdapter`
attaches the common auxiliary head. T+M and T+S therefore differ in auxiliary
information rather than in head shape or the existence of a second encoder
pass. T+M is a single-seed attribution control, not a confirmatory information
factor or a causal steady-label-only estimate.

## Boundary

This is schedule readiness, not a training activation or performance result.
It reads no transient, steady, locked-test or processed-only-extra WSS. It
creates no paper claim, does not use `junjinyong`, and does not authorize a GPU
job while the response oracle remains first in the serial queue.
