# Release-730 candidate static audit

## Scope

This audit was completed before any response/local candidate activation or GPU
run. It examined the oracle-to-decoder units, shared-encoder gradient routes,
trainable parameter scope, same-field functional objectives, checkpoint state,
and matched transient/steady wrapper. It did not read dataset values, select a
rank, tune a model, open the locked test or 79 processed-only rows, or create a
paper result.

## Representation and gradient findings

- The oracle fits an orthonormal basis to train-only, area/phase-weighted,
  unit-amplitude complete cycles. The candidate restores raw physical WSS by
  predicting the basis coefficients and a positive amplitude, then dividing
  out the same square-root area/phase weights. The mean, basis and train-scale
  tensors are immutable non-persistent buffers bound to the external oracle
  artifact.
- `encode_geometry` includes the entire GHD-conditioned down/up mesh path.
  Response-only therefore legitimately trains that shared representation and
  freezes only the unused 80-phase local output head, residual gate and
  single-field auxiliary head. The registered active-parameter count follows
  that definition.
- The combined cell decodes the global response and nodewise phase-shared
  gated local residual from one encoder pass. Mean-vector, TAWSS and OSI losses
  are derived from the same decoded vector field; no separate functional head
  can contradict it. Field-anchored gradient projection remains an optimization
  control, not a finite-step non-inferiority guarantee.
- Matched T/T+S training gives the selected control and proposal the same
  eligible steady row set and deterministic exposure rule. The steady field is
  handled by a separate single-field head and is never repeated across 80
  phases. Terminal epoch, exposure count, prefix digest, steps, time and memory
  remain reported because early stopping can produce different compute.

## Corrected inconsistency

The candidate evaluator previously replaced OSI MAE using the train-defined
reference-TAWSS support but retained the legacy fixed-threshold
`osi_coverage`. The correct same-support coverage was emitted under the extra
name `osi_area_coverage`. That made two fields in one result row describe
different supports.

The evaluator now overwrites the canonical `osi_coverage` key with the
same-support area coverage. The registered metric list includes
`osi_coverage`, rejects `osi_area_coverage`, and a regression test verifies the
result-row schema. Downstream response/local, matched-training and locked-test
config hashes are updated together.

## Verdict

No architecture, loss or data-protocol change was supported by the remaining
static checks. The response/local candidate remains conditional on the
response oracle and direct controls. The correction is evidence hygiene, not a
novelty or performance claim.
