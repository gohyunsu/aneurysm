# Common-cycle and paired-steady architecture training

This is an executable development path for the existing Fourier, ordinary-
adapter, uniform-transfer and selective-transfer controls. It is not evidence
that a proposed model outperforms sufficiently trained direct priors. The
separate runtime preserves existing baseline deployments and result files.

## One physical cycle and one independent auxiliary field

The common `train_cycles` routine accepts optional `PairedSteadySupervision`.
Every admitted transient geometry supplies its full 80-phase target. In T+S,
one independently scheduled, eligible steady geometry additionally supplies
one physical `[N, 3]` field, using the audited reader's `steady_wss` key.
It is never broadcast into 80 targets or equated to the transient mean.

For a gradient-accumulation group of actual size B, the objective is the mean
of `L_cycle + lambda * L_steady` over B pairs. Both terms are the existing
area-weighted physical relative squared errors, with each reference providing
its own denominator. The transient backward and steady backward contribute
to one optimizer update. The final partial group divides by its actual size,
not by the nominal accumulation setting. T-only constructs no inactive steady
head and performs no auxiliary read or backward.

No functional loss, hard tangency projection, frozen prior, topology loss or
performance-based early stopping is added here. Field accuracy remains the
objective. Common validation computes all 80 phases and same-field TAWSS and
valid-support OSI, selecting the earliest checkpoint with minimal validation
field rL2. Steady labels are not read during validation or cycle inference.

## Eligibility, deterministic sampling and measured work

The private caller reuses the existing 13,985 eligible steady rows and 407
exclusions from the 14,392-row processed archive. The source paper's 14,000
description remains distinct. Public code contains no private ID list.

Sampling follows seeded permutations of the admitted row list, concatenated
across pool passes. The prefix is identical across different epoch groupings
at equal total exposure. Computing a schedule or restoring its prefix reads
no fields. The lazy reader validates eligibility again before decoding one
row, and tests verify the actual tensor and coefficient indices accessed.

For E epochs and M admitted training geometries, T+S records:

- M E transient cycle exposures and 80 M E transient phase-field exposures;
- M E steady single-field exposures, not additional transient cycles;
- E ceil(M/B) optimizer updates, where B is accumulation size;
- distinct transient/steady encoder calls and validation cycle forwards;
- scheduled-row digests, unique steady coverage, measured epoch/runtime cost
  and CUDA peak allocation; raw prediction storage remains zero.

The public trainer supports supplied subsets, but the initial private runtime
activates full 584/73 development only. A reduced-label runtime must use the
existing subset-derived geometry/output statistics for both regimes; this
full-label source is not a disguised label-efficiency experiment.

## Paired initialization and auditable continuation

The runner constructs a common T+S model under the declared seed and removes
steady-only modules for T before optimization and parameter accounting. Thus
common parameters, including adapters and kernels, are paired when shapes
match; no discarded random auxiliary label influences initialization. Total
training parameters and active cycle-inference parameters are distinguished.
Nearest-capacity wide adapters retain their separately declared widths.

A completed-curve extension restores the hash-bound model, optimizer,
scheduler, RNG and selected validation checkpoint. Steady pool/order, weight,
seed, per-epoch exposure digests, coverage and field-count ledgers must agree.
Only epochs after the restored boundary decode new rows. Synthetic dropout
tests verify equality with uninterrupted mixed training. This verifies the
CPU test path and state restoration, not bit-exact nondeterministic CUDA.
Interrupted-run recovery without a completed parent result is a separate
integration task; the completed-curve path does not fabricate that result.

## What remains to establish a paper result

The real-data candidate still needs a source/config-pinned activation,
full-resolution GPU cost and optimization evidence, then paired comparisons
with strong baselines and simpler/capacity controls. No arbitrary accuracy
threshold is used to admit an architecture before these comparisons. Full
five-seed and nested label-efficiency evidence remain downstream work.

The original test was previously opened. New development remains train/
validation-only, and later old-test analysis cannot be called untouched
confirmation. Fixed waveform, registered synthetic geometry and common
connectivity do not establish clinical or variable-boundary generalization.
