# Aneumo response-fidelity direct-prior reappraisal

Status: **conditional application question retained; P1 v2 superseded before
execution by an inactive v3 design; model, GPU, outer test and paper claim remain
zero**  
Decision date: 2026-08-12 KST

## Decision

The response-fidelity direction survives, but its architecture story does not.
Three direct priors materially narrow the defensible contribution:

- [Sensitivity-Constrained FNO, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/227b19598f79ed838b01933b9a6ace41-Abstract-Conference.html)
  already shows that solution accuracy does not ensure parameter-sensitivity
  accuracy and adds sensitivity supervision to neural operators.
- [Hemo-MPO](https://doi.org/10.1016/j.aej.2026.05.044) already evaluates an
  SE(3)-equivariant mesh encoder, physics constraint and DeepONet decoder on
  Aneumo. The inspected article reports architecture and aggregate performance,
  but no public code repository or exact family-split reproduction bundle was
  identified. It is a source-level direct prior, not an executable AURORA
  baseline or an AURORA result.
- [Symmetry in the Wild](https://arxiv.org/abs/2605.18816) already evaluates
  equivariant neural CFD surrogates on a base-anatomy-stratified Aneumo subset.
  It uses one flow condition, 0.001 kg/s, to isolate geometry. Its
  [official AB-GATr repository](https://github.com/PatRyg99/abgatr) is pinned at
  `49acb32083d3389e57dde0f7f82703366c4cba27`; the repository has no declared
  SPDX license and says experiment reproduction is “Coming soon.” It is not
  silently copied or treated as an executable matched control.

The residual application gap is narrower than previously written:

> On aneurysm CFD sensitivity sweeps, does field-error selection hide a
> practically material loss of response fidelity, and does an identity-preserving
> anchor-residual output parameterization prevent that loss when the backbone,
> information set, optimization and field accuracy are controlled?

This gap is not “GNN + equivariance + physics + operator learning.” Those parts
are occupied. It is also not the general observation that neural operators can
have inaccurate sensitivities; SC-FNO already establishes that. AURORA can
contribute only the aneurysm-specific matched failure, a tightly controlled
mechanism test, and independent family-level confirmation.

## Why P1 v2 is inadequate

P1 v2 compared an anchor-conditioned MeshGraphNet with a DeltaPhi-style residual
model. A difference would confound backbone capacity with output
parameterization. It also allowed either contrast direction to satisfy the
screen, so a result opposite to the proposed anchor-residual mechanism could
have been narrated after the fact. New Aneumo-specific equivariant priors make
MeshGraphNet an insufficient primary architecture control.

No v2 model was run, no prediction was produced and no response endpoint was
read. V2 is therefore preserved unchanged and prospectively superseded rather
than repaired.

## P1 v3 falsifier

The inactive v3 design is
[`configs/aneumo_response_fidelity_p1_template_v3.json`](../configs/aneumo_response_fidelity_p1_template_v3.json).
It cannot execute or register itself and remains blocked on real P0 11/11.

The primary pair shares one `LaB-GATr` anchor-conditioned backbone:

1. **Direct head:** predict the target velocity field directly.
2. **Identity-residual head:** predict a residual multiplied by
   `log(q/q0)` and add it to the nominal field, so the learned correction is
   exactly zero at the anchor.

The [official LaB-GATr implementation](https://github.com/sukjulian/lab-gatr)
is MIT-licensed and pinned at
`43379fddb7583d5a8527fc3e104b7c11f8f0afb9`. The AB-GATr source reports that
LaB-GATr has slightly lower field error on its single-flow Aneumo experiment;
this makes it the strongest currently reimplementable backbone control. This
does not select it as an AURORA method or authorize installation, training or
GPU use.

All non-output choices are identical. Calibration remains response-blind;
25/50/75% iso-error matches use three distinct checkpoints, with the median
level primary and low/high levels non-rescuing. Both models must remain within
the 1% field-equivalence band and be field-competent against the fitted
power-law control.

The direction is now prospective. Positive
`log(direct response error / residual response error)` means the residual head
is better. P1 passes only if both paired-response and tangent endpoints have:

- a 95% stability interval entirely above zero;
- at least a 10% pooled response-error reduction; and
- a positive contrast in at least four of five seeds, with zero ties excluded.

A negative or mixed direction closes the exact hypothesis. It cannot be
relabelled as evidence for a reversed method story. Dependent cross-fit
contrasts remain development evidence only: no exact p-value, multiplicity-
adjusted p-value, nominal confidence coverage, formal power or paper efficacy
claim is allowed.

## Bounded development contract

Even a v3 pass opens only a separately registered validation-only phase:

- at most two repair rounds;
- at most 80 additional GPU-hours in total;
- one attribution-supported failure hypothesis per round;
- every attempted variant and the selection rule logged;
- historical test and future confirmation families sealed; and
- a fresh seed set or disjoint split required for prospective re-entry.

No failed screen is renamed or overwritten. This implements bounded development
without weakening the confirmatory gate.

## ISBI claim consequences

The conditional paper identity is retained at 34.0/40 with residual novelty
exactly 2.5/5. The score is not increased for LaB-GATr, residual learning,
equivariance or a model name. If activated, the three possible contributions
are:

1. an Aneumo-specific, field-error-matched demonstration that field accuracy
   does not guarantee multi-flow response fidelity;
2. a same-backbone test showing that an anchor-identity residual
   parameterization corrects the observed failure without field regression; and
3. confirmation on exactly 100 prospectively frozen new base families, with
   all historical 32 excluded.

Every contribution is deleted if its evidence cell is empty. Until real P0 and
P1 pass, the manuscript title, abstract claim, method, result table and figure
remain inactive.

## Current execution boundary

Real P0 remains 0/11 and the exact private Aneumo cache path is unresolved.
This reappraisal queried no scientific server, transferred no data, submitted
no PBS/GPU job and read no validation/test field. Do not retry `introai9` before
a verified external service or administrator change. Never access, query,
transfer to, submit to or monitor `junjinyong`.
