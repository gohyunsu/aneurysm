# Release-730 eligible-steady objective-scale audit

## Why this audit is needed

The T+S experiment must not use an arbitrary steady-loss multiplier. The
transient comparators currently normalize physical Cartesian WSS by a
train-transient vector RMS. The steady archive has its own distribution, so
reusing the transient scale without measurement may create a hidden task-weight
imbalance.

This CPU-only audit computes the corresponding physical vector RMS over the
13,985 leakage-audited steady rows. It uses the released decoder statistics and
the same unweighted component-moment grammar as the transient training scale.
It additionally reports component means/population standard deviations,
case-level RMS quantiles, and steady-to-transient scale ratios.

The result is descriptive. It does not automatically set the auxiliary loss
weight, declare a material mismatch, select a model, or create a paper claim.
A later shared-encoder implementation must use this evidence only inside a
separately versioned bounded validation-development contract.

## Read and execution boundary

- Read: the exact 9.63 GB steady object, the private eligible-row manifest and
  the frozen aggregate train-transient statistics.
- Not read: any transient WSS tensor, validation field, locked test field, or
  processed-only-extra field.
- Compute: four CPU cores, 64 GB memory, zero GPUs, float64 streaming moments.
- Order: execute only after the response-oracle terminal record and a fresh
  private activation. It cannot delay, stop, or alter the oracle or direct
  comparators.
- Server: `introai9` only; `junjinyong` is excluded.
