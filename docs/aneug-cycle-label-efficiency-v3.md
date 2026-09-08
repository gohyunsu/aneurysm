# Complete-cycle label efficiency: unique cases versus training exposure

This is a training primitive, not an activated experiment or data-efficiency
result. It does not select a model or subset and does not change a running job.

A separate private runtime connects this primitive to admitted-training inputs
and the original eligible steady reader. Twenty-three input, arithmetic,
runtime and existing-profile tests pass, including full-width synthetic T/T+S
optimization. This path is prepared, not an actual label-efficiency result.
Real membership pins are metadata-verified privately. At 100%, use the
existing audited 584-case reader/transforms; a redundant refit is not required.
Smaller subsets must refit using their unique admitted training cases.
The implementation requirements below describe what the new path enforces;
they do not imply an actual-data label-efficiency result.

## What changes

`train_cycles(..., transient_examples_per_epoch=584)` can train on a smaller
list of admitted unique cases without reducing the exposure budget. Each
reference epoch uses repeated deterministic permutations with balanced visit
counts: any two cases differ by at most one visit in that epoch. The sampler
uses local RNG instances and cannot inspect targets or choose favorable cases.

With 250 reference epochs and accumulation of two cycles, every condition has
146,000 transient cycle exposures, 11,680,000 phase-field exposures and 73,000
optimizer updates. The unique-label counts can remain 58, 146, 292 or 584.
Paired T+S supervision adds one eligible steady field for each transient cycle;
validation reads no steady target. These are matched exposure/update budgets,
not proof of equal wall time, memory, model capacity or convergence.

The default `None` retains one visit per unique case per epoch and adds no
sampling metadata. The first permutation of an explicit schedule is exactly
the default order. The remaining rounds follow the previously used balanced
label-efficiency algorithm, without restricting a generic trainer to five
particular seed values.

## Data preparation is separate and essential

Choose nested memberships using a label-blind rule and preserve original
within-subset loader order. Supply only admitted unique training cases to the
reader, before preprocessing. The existing release-730 reader accepts
`train_subset_case_ids` and recomputes GHD moments and WSS output scale from
that subset. Fit the size-preserving coordinate reference and OSI support
floor on the returned unique training cases, not the expanded exposure list.

Use those same subset GHD and geometry statistics for eligible steady inputs
and validation. The separate subset runtime explicitly forwards both GHD
moments; the older full-cohort wrapper must not be used unchanged for smaller
subsets. At 100%, the original audited moments are supplied explicitly and
their provenance identifies reuse rather than a new fit. Changing only a
label-fraction field or repeating the case list is insufficient.

Reusing a completed full-cohort endpoint also requires the same model, seed,
input and information condition, optimization/selection recipe and exposure
ledger. Reusing the valid preprocessing path does not make a different
historical model or training budget comparable.

Do not add withheld transient labels, validation/test fields or processed-only
extras to fit statistics. Any decoder normalizer required to interpret the
released archive remains separately disclosed from newly fitted statistics.

## Provenance and recovery

An explicit `cycle_sampling` provenance record binds unique case count,
per-epoch exposure count, seed and scheduling algorithm. `train_cases` remains
the unique count; effective exposure/update totals reflect all repeated visits.
Checkpoint state includes the contract. Changing or silently dropping it on
completed-curve continuation is rejected. T and paired T+S completed extensions
restore the same learning sequence, and interrupted T recovery retains the
fixed original budget and unknown discarded-work accounting.

Interrupted joint-T+S recovery still needs the pre-existing separate sampler
recovery support; this change does not claim to provide it. Native snapshot
models also retain their own phase-conditioned trainers and ledgers.

## Verification scope

Focused tests cover real synthetic full-cycle optimization, balanced 584-exposure
schedules at each label budget, actual production-width selective T/T+S models,
default-path equality, changed-contract rejection, completed extensions and
true synthetic interruption. No CFD accuracy, allocated-GPU stability,
multiseed improvement or label-efficiency curve is established by these tests.
