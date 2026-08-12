# Response-fidelity confirmation v2 red-team

Status: **inactive prefield design; v1 preserved and superseded before metadata,
field or prediction access; real P0 0/11; no model, compute, result or claim**  
Decision date: 2026-08-13 KST

## Verdict

Keep Aneumo and the response-fidelity question. Do not claim a new GNN, a new
boundary-conditioned operator or multi-flow learning. Replace inactive
confirmation v1 with v2 because v1 fixed the sample but did not prove that the
sample could resolve the target effect, did not define its estimator completely
and allowed a large mean improvement to be produced by a minority of families.

The current scientific identity remains conditional:

> At matched full-field error on aneurysm CFD sensitivity sweeps, does an
> identity-preserving anchor output improve response-curve fidelity on most
> unseen base geometries, without falling behind a same-backbone direct head or
> an analytic scaling control?

This is narrower than an architecture paper. It is an application failure,
controlled mechanism and family-level confirmation chain. Any missing link
deletes the corresponding paper claim.

## What is actually available

The verified private holding is one 64-case compact Aneumo cache: 32 generation
base families, two deformations per family, eight steady flows and 4,096 aligned
nodes. Its fields are not present in the local project workspace, and the exact
private `introai9` cache path remains unresolved. That is an execution blocker,
not evidence that the dataset was never acquired.

The [Aneumo source paper](https://arxiv.org/abs/2505.14717) reports 427 real base
geometries, 10,660 deformed shapes and eight flows, or 85,280 CFD records. Thus
the future 100-family confirmation is an expansion within the same selected
dataset, not a search for a different ideal dataset. Excluding all historical
32 leaves at most 395 base families before an exact metadata-only eligibility
audit; 100 is at most 25.3% of that post-exclusion population. Base geometry is
the independent generator-family unit. It is not relabelled as an independent
patient.

## Direct-prior subtraction

The source landscape is stricter than an architecture story permits:

- Aneumo already varies the number of training and validation flow conditions
  and reports that limited flow diversity can make evaluation optimistic.
  Eight-flow learning or evaluation is therefore not novel.
- [Hemo-MPO](https://doi.org/10.1016/j.aej.2026.05.044) already combines an
  SE(3)-equivariant mesh encoder, physical constraints and a DeepONet decoder
  that maps geometry and physiological boundary conditions to full velocity,
  pressure and WSS fields. Boundary-conditioned operator learning and that
  component stack are not AURORA contributions.
- [SC-FNO](https://openreview.net/forum?id=DPzQ5n3mNm) already establishes the
  generic mismatch between solution accuracy and parameter sensitivity.
- [AB-GATr](https://arxiv.org/abs/2605.18816) already evaluates equivariant
  neural CFD surrogates on Aneumo and makes LaB-GATr a strong reimplementable
  architecture control.

The residual gap is consequently endpoint- and control-specific: Aneumo has not
established that field-error-matched heads preserve the same-case, anchor-
relative response curve, nor that changing only the output parameterization
improves this endpoint on most prospectively selected base families.

## Why exactly 100 is not accepted on faith

One hundred remains a fixed, computationally bounded same-release benchmark,
not a formal sample-size claim. V2 adds a mandatory prefield viability gate
after the final candidate passes fresh re-entry but before any confirmation
field or prediction is read.

For each response endpoint, use the 20 complete development-family, five-seed
log-error contrasts of the final frozen candidate. The planning alternative is
`log(1.10)`. A one-sided level-0.05, 100-family noncentral-t approximation has
80% power only when the true family-log-contrast standard deviation is no more
than `0.3806859`. To account for estimating dispersion from 20 families, use the
one-sided 90% chi-square upper variance bound (`df=19`, 0.10 quantile
`11.6509100`). Both observed development standard deviations must therefore be
no greater than `0.2981055`.

This is a prospective planning adequacy check, not evidence of normality, a
paper-level power statement or a substitute for the family bootstrap. Failure
closes this exact confirmation before outer data are touched; it does not
authorize increasing 100, reducing the effect floor or changing endpoints.

The same prefield stage projects the entire inference workload from measured
development throughput and metadata-only selected case-flow counts:

`case-flow count × 2 primary models × 5 frozen seeds`.

The one-sided 95% upper runtime projection must fit within 40 GPU-hours. This
prevents a knowingly incomplete one-shot confirmation. It grants no current GPU
authority.

## Exact estimator and majority-family safeguard

For model `m`, seed `s`, family `f`, case `c` and endpoint `e`, compute the
registered eight-flow case error `E(m,s,f,c,e)`. The case contrast is

`log(max(E_direct, 2^-52) / max(E_candidate, 2^-52))`.

Average case contrasts within each family and seed, then average the five seed
contrasts within family. The reported multiplicative effect is the exponential
of the mean of the 100 family contrasts—a geometric mean error ratio. Only the
100 family rows enter the 10,000-replicate bootstrap. Nodes, flows, cases and
seeds never become independent replicates.

Mean superiority alone is insufficient for the phrase “across source
anatomies.” For both paired-response and tangent endpoints, define a family win
as a five-seed family contrast strictly above zero. The one-sided 95% Wilson
lower bound on the win proportion must exceed 0.5. With exactly 100 families,
58 wins fail and 59 wins pass. This is added to, not substituted for:

- candidate/direct field non-inferiority within 2%;
- candidate/power-law field competence within 2%;
- both response bootstrap lower bounds above zero;
- both geometric mean error ratios at least 1.10; and
- positive seed-level direction in at least four of five seeds.

All conditions form one intersection–union claim. A secondary endpoint,
descriptive model or attractive figure cannot rescue failure.

## Figure and four-page consequence

Rank families by the equal-weight mean of paired-response and tangent family
log contrasts. Show the minimum, median and maximum families as candidate worst,
typical and best. The within-family case and target flow use fixed hash and
flow-distance rules. Reference, direct and candidate panels use the same camera,
coordinates and reference-derived colour range.

The [official ISBI 2027 instructions](https://biomedicalimaging.org/2027/papers/)
were rechecked on 2026-08-13: review remains single blind; all technical content,
figures and tables must fit within four pages; a paid fifth page is restricted
to ethics, acknowledgments/conflicts and references; the deadline remains
26 October 2026, 23:59 USA EDT; and the submission link remains unpublished.

If activated, the paper spends its limited space on one chain only: matched
failure, anchor-identity mechanism, exactly-100-family confirmation and bounded
simulation-only interpretation. Protocol history, model-brand decoration and
failed discovery branches do not enter the four technical pages.

## Current boundary

The v2 config and validator are synthetic contract artifacts only. V1 remains
immutable pre-evidence history. Real P0 is 0/11; P1, final candidate, viability
audit, manifest, confirmation metadata, field, prediction, server query,
PBS/GPU job, result and paper claim are all zero. Do not retry `introai9` before
a verified external service or administrator change, and never access
`junjinyong`.
