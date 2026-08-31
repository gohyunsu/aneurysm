# ICCE 2027 implementation audit

Status: source-complete audit; new ICCE v2 numerical evidence remains pending.

Audit date: 2026-08-31 KST. The inspected public parent commit is
`0577acdf4674857b501fd8327460cb84711bf340`. Private case identifiers are not
included here. This document describes what the current code computes; it does
not infer a performance claim from a protocol, test, or running job.

## 1. Audited question and scope

The narrowly registered question is whether phase-free steady WSS should enter
a complete-cycle surrogate through a disposable, task-specific head attached
to the shared geometry encoder, while the 80-phase decoder remains supervised
only by transient cycles. Hard parameter sharing, auxiliary heads, GHD, graph
attention, the GNN backbone, and complete-cycle decoding are not treated as
architectural novelties.

The active attribution protocol is
[`configs/aneug_release_730_icce_validation_revision_v2.json`](../configs/aneug_release_730_icce_validation_revision_v2.json).
Its public training kernel is
[`src/aurora/aneug_release_730_icce_fixed_budget.py`](../src/aurora/aneug_release_730_icce_fixed_budget.py),
and its statistical kernel is
[`src/aurora/aneug_release_730_icce_analysis.py`](../src/aurora/aneug_release_730_icce_analysis.py).

The audit covered the following paths.

- Dataset decoding, split validation, and train-only statistics:
  [`aneug_release_730_ghd_gps_baseline.py`](../src/aurora/aneug_release_730_ghd_gps_baseline.py)
  and
  [`aneug_release_730_train_audit.py`](../src/aurora/aneug_release_730_train_audit.py).
- Steady-stream decoding and exposure schedules:
  [`aneug_release_730_matched_steady_stream.py`](../src/aurora/aneug_release_730_matched_steady_stream.py).
- Regime-separated and shared-decoder model interfaces:
  [`aneug_release_730_ghd_cross_regime_transfer.py`](../src/aurora/aneug_release_730_ghd_cross_regime_transfer.py).
- T+M target construction:
  [`aneug_release_730_single_field_auxiliary.py`](../src/aurora/aneug_release_730_single_field_auxiliary.py).
- Common field and functional metrics:
  [`aneug_processed_v4_d9.py`](../src/aurora/aneug_processed_v4_d9.py),
  [`aneug_release_730_official_graphunet_baseline.py`](../src/aurora/aneug_release_730_official_graphunet_baseline.py),
  [`cycle_functional_alignment.py`](../src/aurora/cycle_functional_alignment.py), and
  [`aneug_release_730_response_local_candidate.py`](../src/aurora/aneug_release_730_response_local_candidate.py).
- Direct architecture comparators: the released Graph U-Net adapter,
  GHD--GINE/GPS U-Net, and Transolver adapter.

## 2. Data identity, cardinality, and representation

The source-bound transient archive is `assembled_registered_data_1k_v5.pth`,
33,233,856,917 bytes, SHA-256
`3edf0d75ed8c83b10ebc23bb14fcb59392025b8b6ce9ce49f966377ce8f3b0ae`.
It contains 809 processed rows. The release-aligned cohort contains 730 rows;
the remaining 79 processed-only rows are a distinct excluded bucket.

The release-aligned split is exactly 584 train, 73 validation, and 73 test
geometries. The public evidence is
[`results/aneug_release_730_split_r3_20260818.json`](../results/aneug_release_730_split_r3_20260818.json).
The split was created without reading registered WSS fields. Exact and
registered-near-equivalent GHD component searches found 730 singleton
components, so component integrity does not change the 584/73/73 counts. The
split is outcome-blind and geometry-ID disjoint, but it is not evidence of
patient, site, boundary-condition, or latent source-family generalization.

At split creation, `test_opened=false` was true. That field is historical
creation-time evidence, not the present test state. The same 73-case test was
later opened for the original five-seed T versus regime-separated T+S
confirmation. The v2 attribution protocol therefore records it as
`historically_opened_once_preserve_no_new_access`; every new cell is validation
only.

Each decoded transient case has only five tensors:

- centered and RMS-scaled coordinates, shape `[13,902, 3]`;
- recomputed mesh unit normals, `[13,902, 3]`;
- normalized lumped vertex areas, `[13,902]` and summing to one;
- train-standardized GHD, `[432]`;
- physical Cartesian WSS, `[80, 13,902, 3]`.

The stored nine channels are `(x,y,z,n_x,n_y,n_z,WSS_x,WSS_y,WSS_z)`.
All cases use the registered 13,902-node surface and common hierarchy. The
target remains the released Cartesian WSS: no hard tangent projection and no
hard phase-0/phase-79 closure are applied.

The loader indexes case metadata first, then admits only the requested train or
validation membership. Test and extra records are included only in a sealed-ID
exclusion set and are never dereferenced for tensor values by the v2 runner.
`validate_partition_boundary` additionally requires 0 locked-test and 0 extra
field reads before a result can validate.

## 3. Steady-data admissibility and overlap exclusion

The processed steady archive is 9,632,510,050 bytes, SHA-256
`0c03c1d9cc5bdcfc32d663a82a6ac7f22db757fa40a4960a83038fb62890177f`.
It has 14,392 processed rows; the source paper documents 14,000 steady cases.
The study does not silently relabel the 392-row difference.

The public overlap audit is
[`results/aneug_release_730_steady_overlap_audit_r2_20260818.json`](../results/aneug_release_730_steady_overlap_audit_r2_20260818.json).
It found 407 exact 432-D GHD matches to a transient processed row and no
near-only match at maximum-absolute `1e-6` and RMS `1e-7` tolerances. All 407
matching steady rows are excluded, including matches to train, validation,
historical test, and processed-only extra rows. This leaves 13,985 eligible
steady rows with digest
`6dbfde4df94c50e66269ab8cf0e8c755d9f95cfbef43af1376af20036c6c82cc`.
The fixed schedule supplies 584 steady examples per reference epoch using a
SHA-256-ranked, without-replacement epoch schedule. No steady label is copied
across 80 phases and no steady time or waveform token is synthesized.

## 4. Normalization and scale provenance

The code separates source decoding constants from study-fitted statistics.

1. The archive's nine-channel `tensor_norm` mean and standard deviation are
   source-provided inverse-transform constants. They decode stored normalized
   tensors into physical coordinates and WSS. They are not refitted or selected
   by this study.
2. Full-budget GHD mean and population standard deviation are read from the
   584-train-only audit. For 10/25/50% experiments they are recomputed from the
   nested selected training subset only, with standard deviations clamped at
   `1e-6` for numerical division.
3. The cycle-output scale is the train-only physical vector RMS

   ```text
   s_cycle = sqrt((1/C) sum_c (1/T) sum_t sum_i a_ci ||tau_cti||_2^2),
   ```

   with normalized area weights `a_ci`, `C` admitted transient training cases,
   and `T=80`.
4. The T+M auxiliary scale is the analogous train-only area-weighted RMS of
   each transient cycle's vector mean.
5. The separated steady-head scale is computed from the leakage-excluded
   eligible steady training population. It is an output scale, not an
   auxiliary-loss coefficient.
6. The frozen OSI support floor is

   ```text
   epsilon_TAWSS = 1e-4 * s_cycle.
   ```

   It therefore depends only on the admitted transient training partition.
   Each completed result records the exact scalar. The v2 aggregate and paper
   must not substitute a validation- or test-derived threshold.

No vertex, phase, validation case, historical test case, or extra row is used
to fit a study normalization statistic. Vertices and phases remain correlated
within one case and are never treated as independent statistical samples.

## 5. Exact six-method attribution implementation

Let `E` denote all GHD--GINE/GPS backbone parameters except the phase-producing
output module, `D` that two-linear-layer module ending in 240 channels
(`80*3`), and `H` the common
LayerNorm--Linear--SiLU--Linear single-field head. `D(E(g))` is reshaped to one
80-phase Cartesian WSS cycle. All methods use the same width-128, four-head
GHD--GINE/GPS backbone, five seeds `20260901`--`20260905`, 251 fixed epochs,
AdamW (`lr=3e-4`, weight decay `1e-4`), StepLR (`50`, `0.75`), gradient
accumulation over two cases, and a fixed final checkpoint. Validation never
selects a checkpoint for this matrix.

| ID | Code path and actual update |
|---|---|
| T | `Release730GHDSteadyTransferModel` is instantiated for interface symmetry, but `H` is frozen. Only `L_cycle(D(E(g_T)), tau_T)` updates `E,D`. |
| T+M | A second encoder pass uses the same `H`. Its target is the arithmetic mean of the admitted transient train case's 80 physical WSS phases. `L_cycle + lambda L_one` updates `E,D,H`; the auxiliary graph contains no `D`. |
| T+S-separated | One eligible steady geometry/WSS pair feeds `E,H` per transient exposure. `L_cycle + lambda L_one` updates `E,D,H`, but the steady loss graph contains no `D`. `H` is discarded for cycle inference. |
| T+S-shared | `Release730GHDSharedDecoderSteadyControl` has no auxiliary head. The steady prediction is `mean_t D(E(g_S))`, so its loss updates both `E` and `D`. |
| S->T | Stage 1 trains only `E,H` for 146,584 steady exposures. Stage 2 trains only `E,D` for 146,584 transient exposures with a newly initialized optimizer/scheduler. `H` is absent from the stage-2 graph and inference. |
| T+S-shuffled | Architecture and updates match separated T+S, but a seed-bound SHA-256 ranking maps every eligible steady index to the next index in one cyclic permutation. There are no fixed points; geometry order, target marginal counts, and auxiliary exposure count are preserved. |

Every method consumes 146,584 transient exposures (`584*251`). T+M and the
three joint steady methods consume 146,584 auxiliary exposures. S->T consumes
146,584 steady pretraining plus 146,584 transient fine-tuning exposures. Each
result records encoder forwards, optimizer updates, total epochs, wall time,
peak allocated training memory, exposure-prefix digests, configuration
provenance, and zero test/extra reads. S->T necessarily has an additional
optimization stage; this difference is reported rather than hidden.

## 6. Exact loss and evaluation equations

For case `c`, phase `t`, vertex `i`, prediction `p_cti`, reference `y_cti`, and
normalized lumped area `a_ci`, the code uses uniform phase weights `1/T`.

### 6.1 Cycle training loss

The cycle loss is a relative **squared** error, not a relative L2:

```text
L_cycle(c) =
  [sum_t sum_i a_ci ||p_cti-y_cti||_2^2 / T]
  ------------------------------------------------
  [sum_t sum_i a_ci ||y_cti||_2^2 / T],
```

with the denominator clamped below at `1e-12`. Since the same `1/T` appears in
both terms, it cancels numerically. The fixed-budget epoch objective is the
mean of per-case losses through gradient accumulation; it is not a global
vertex-pooled loss.

### 6.2 Single-field auxiliary loss

For one steady or cycle-mean target `z_ci` and head prediction `h_ci`,

```text
L_one(c) = sum_i a_ci ||h_ci-z_ci||_2^2
           --------------------------------,
           sum_i a_ci ||z_ci||_2^2
```

again with a `1e-12` denominator clamp. The joint methods optimize
`L_cycle + lambda L_one`; the main registered value is `lambda=1`.

### 6.3 Primary physical vector-WSS field metric

The per-case primary field endpoint is

```text
rL2_field(c) = sqrt(L_cycle(c)).
```

The reported method mean is the arithmetic mean of 73 case values. The code
does not concatenate all vertices/phases across cases before normalization.
Accordingly, manuscript text must not call this endpoint "relative squared
error" or imply a global pooled rL2.

### 6.4 Mean-vector metrics

Two distinct diagnostics exist and must not be conflated.

```text
m_y(i) = (1/T) sum_t y_ti,   m_p(i) = (1/T) sum_t p_ti.

mean_wss_vector_error =
  sqrt[sum_i a_i ||m_p(i)-m_y(i)||^2 /
       sum_i a_i ||m_y(i)||^2].

mean_vector_tawss_normalized_l2 =
  sqrt[sum_i a_i ||m_p(i)-m_y(i)||^2 /
       sum_i a_i TAWSS_y(i)^2].
```

The first uses mean-vector energy; the second uses reference TAWSS energy.

### 6.5 TAWSS

```text
TAWSS_y(i) = (1/T) sum_t ||y_ti||_2,
TAWSS_p(i) = (1/T) sum_t ||p_ti||_2,

TAWSS_NAE(c) =
  sum_i a_i |TAWSS_p(i)-TAWSS_y(i)|
  -----------------------------------.
       sum_i a_i TAWSS_y(i)
```

This is a normalized absolute error, not an L2 error.

### 6.6 OSI, support, invalid predictions, and coverage

For either field `q`,

```text
OSI_q(i) = 0.5 * [1 - ||(1/T) sum_t q_ti||_2 / TAWSS_q(i)].
```

The evaluation implementation clamps the TAWSS denominator at `1e-12`.
Reference support is fixed by training statistics:

```text
S = {i : TAWSS_y(i) > epsilon_TAWSS}.
```

A prediction is valid at `i` only if `i` is in `S`, predicted TAWSS is finite,
and predicted TAWSS is strictly positive. Valid vertices receive absolute OSI
error. Invalid supported vertices receive the prespecified maximal error 0.5:

```text
OSI_MAE(c) = sum_{i in S} a_i e_i / sum_{i in S} a_i,
e_i = |OSI_p(i)-OSI_y(i)| if valid, else 0.5.
```

The existing `osi_coverage` is

```text
sum_{i valid} a_i / sum_{i in S} a_i.
```

It is **area-weighted valid-prediction coverage within support**, not the
fraction of vertices in support. Invalid-prediction area coverage is
`1-osi_coverage`. The reference-support vertex fraction and reference-support
area fraction are not emitted by the current training result and must be
derived deterministically from validation references using the frozen
train-derived floor before manuscript finalization. They must not be inferred
from `osi_coverage`.

The differentiable OSI training primitive uses the same reference support but
a pseudo-Huber error with delta `0.02`. The active fixed-budget attribution
uses field-only cycle loss, so that pseudo-Huber term is not part of the six
methods' cycle objective.

### 6.7 Retained diagnostics

- Low-WSS error selects vertices at or below the unweighted per-case 25th
  percentile of reference TAWSS, then computes an area-weighted field rL2 on
  that support.
- Peak-systolic error selects the reference phase maximizing
  `sum_i a_i ||y_ti||` and computes area-weighted vector rL2 at that phase.
- `mesh_normal_component_relative_l2` compares predicted and reference normal
  components and normalizes by reference normal-component energy. It is not a
  direct tangent-leakage fraction.

These are diagnostics, not the three registered primary endpoints.

## 7. Label efficiency, mismatch, gradient, and lambda analyses

Label-efficiency memberships are nested, outcome-blind prefixes with
58/146/292/584 unique transient train cases for 10/25/50/100%. Each reference
epoch still has 584 deterministic balanced transient exposures. Both T and
separated T+S use the same five seeds at every budget; T+S adds the registered
584 steady exposures per epoch. Subset GHD/output/support statistics are
recomputed from the admitted subset only.

The train-only regime-mismatch kernel is
[`aneug_release_730_regime_mismatch.py`](../src/aurora/aneug_release_730_regime_mismatch.py).
For the 317 exact GHD overlaps belonging to transient train only, it computes:

- area-weighted steady-versus-cycle-mean vector rL2, normalized by cycle-mean
  vector energy;
- one global area-weighted vector cosine;
- area-weighted Pearson correlation between steady magnitude and cycle-mean
  vector magnitude;
- area-weighted normalized absolute difference and signed bias between steady
  magnitude and transient TAWSS.

Validation, historical test, and extra overlaps are forbidden. A kernel or
config is not a result; the distribution remains TODO until an exact run
completes.

For T+S-shared, the code calls `torch.autograd.grad` on transient and weighted
steady losses before summation. The recorded cosine uses only `D` parameters,
while the actual naive-sum update still covers `E,D`. The analysis reports all
146,584 measurements per seed, their mean, median, and fraction below zero.
This is descriptive evidence and does not identify a causal mechanism.

Lambda sensitivity is validation-only at `{0.25,0.5,1,2,4}` using seeds
`20260901`--`20260903`. Lambda 1 remains the main registered method regardless
of the sensitivity result.

## 8. Statistical unit and bootstrap

The inferential unit is one geometry. The primary analysis first constructs
the paired per-seed, per-case difference between separated T+S and each
comparator. For each of 10,000 draws, it independently resamples the five seed
indices and 73 paired case positions with replacement and averages the
resulting crossed seed-by-case array. The interval is the 2.5th and 97.5th
percentile of those draws. Raw method means, point differences, and intervals
are reported; the analyzer does not choose a winner or claim population
inference. Vertices and phases never enter the resampling array as independent
observations.

## 9. Architecture-comparison boundary

Architecture comparison and supervision attribution are separate tables.

- **Released Graph U-Net adapter:** the upstream
  `PyGGraphUNetwTemporalEmbedding` class/forward is preserved, but the study
  uses the release-aligned split, a zero waveform because the released waveform
  file is absent, matched physical metrics, and a single-GPU accumulation
  adapter. It is not an exact end-to-end upstream reproduction.
- **GHD--GINE/GPS U-Net:** width 128, four attention heads, three registered
  resolutions, two fine and two middle encoder blocks, three coarse GPS blocks,
  one middle and one fine decoder block, and a one-shot 80-phase output. Pure
  PyTorch substitutes for unavailable PyG/scatter/Performer details. This is
  the common backbone for the attribution matrix, not the claimed novelty.
- **Transolver adapter:** official AirfRANS-scale defaults (width 256, eight
  blocks/heads, 32 slices, MLP ratio 2) are adapted to coordinates, normals,
  relative area, 432-D GHD, and an 80-phase WSS output. It is not an exact
  upstream task reproduction.

All three use the same 584/73 development boundary and common physical
case-level endpoints. Historical single-seed results are not silently treated
as a fresh five-seed architecture comparison.

## 10. Documented discrepancies and required resolutions

1. **Squared loss versus rL2 metric:** training logs named
   `mean_cycle_relative_squared_error` are correct; the paper's field metric is
   the square root. Manuscript equations and table headings must preserve this
   distinction.
2. **Historical OSI helper:** the generic `case_metrics` helper uses an absolute
   support floor `1e-4` and count-based validity coverage. The active ICCE
   fixed-budget evaluator immediately overwrites its OSI/coverage values using
   `_valid_support_osi` with the train-derived physical floor and area weights.
   Only the overwritten values may enter ICCE v2 results.
3. **OSI support reporting gap:** the frozen floor and valid-support area
   coverage are recorded, but reference-support vertex/area fractions are not.
   A validation-only deterministic reporting step is required before the paper
   can state them.
4. **Normal-component terminology:**
   `mesh_normal_component_relative_l2` is prediction-versus-reference normal
   component error, not tangent leakage. The corrected term must be used.
5. **Two mean-vector denominators:** `mean_wss_vector_error` and
   `mean_vector_tawss_normalized_l2` are different diagnostics. They cannot be
   merged under one ambiguous heading.
6. **Present test state:** split/config files that say `test_opened=false`
   describe development or split creation. The current v2 policy must state
   that the 73-case test was historically opened and is unavailable for new
   controls.
7. **Consumer benchmark:** the public benchmark contract is implemented, but a
   real commodity-GPU CUDA measurement and paired terminal T/T+S checkpoints
   are still required. No latency, throughput, or deployment number exists
   from source readiness alone.

## 11. Evidence still required before manuscript finalization

- terminal six-method by five-seed validation results and exposure ledgers;
- five common seeds at all four label budgets;
- train-only mismatch distribution;
- three-seed lambda sensitivity;
- five-seed shared-decoder gradient summaries;
- fresh or clearly labeled existing architecture-comparator evidence;
- reference-support fractions and invalid-prediction coverage using the frozen
  floor;
- paired T/T+S consumer-GPU measurements;
- generated CSVs, LaTeX tables, plots, and a six-page PDF whose every number
  traces to an immutable result hash.

Until those artifacts exist, manuscript cells remain explicit TODOs and no
missing value may be inferred, copied from an intermediate epoch, or fabricated.
