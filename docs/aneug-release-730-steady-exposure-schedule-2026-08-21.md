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

## Boundary

This is schedule readiness, not a training activation or performance result.
It reads no transient, steady, locked-test or processed-only-extra WSS. It
creates no paper claim, does not use `junjinyong`, and does not authorize a GPU
job while the response oracle remains first in the serial queue.
