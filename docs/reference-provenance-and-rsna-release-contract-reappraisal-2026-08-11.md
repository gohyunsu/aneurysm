# Reference provenance and RSNA release-contract reappraisal

> Frozen on 2026-08-11 · schema 9.2 · source metadata and literature only · no
> data terms, MIRA access, medical payload, P0/P1, method, architecture, server
> query or compute

## Decision

The supplied surface-vector analysis is directionally sound but does not open
an active study.  The scientifically useful statement remains a falsifiable,
inactive question: a low transient-WSS field error may fail to preserve stable
critical-flow organization.  No such failure has been observed, and the closed
`115645.ECE-util1` execution evaluated none of its ten registered scientific
checks.  Edge 1-forms, Hodge/DEC, equivariance, periodic operators and
structural losses remain controls or possible interventions, not novelty.

A second possibility was considered: treating annotation or reference
provenance as the paper identity.  This is also rejected.  Reference provenance
is an important validity problem, but the currently visible TopAneu and RSNA
contracts do not identify a new estimand or supply an adjudicated reference.
Moreover, direct work already studies learned reference bias, partial
identification under weak references, active label cleaning and broad
label-noise robustness.  Renaming their combination for aneurysm imaging would
not create an independent contribution.

The resulting state is therefore **no active paper problem, no selected model
and no compute**.  This is a scientific rejection, not inactivity caused by an
implementation problem.

## What the official RSNA sources actually expose

The exact AWS Open Data Registry file is
`datasets/rsna-intracranial-aneurysm-detection-dataset.yaml` at file commit
`523ffd3914ba99e6c4b17441f1633cc3eec74c69`, blob
`97b8c1f16b2809d2e82ec0c39d3b156b174c8c83`, 2,626 bytes, SHA-256
`864f0716a8f6618e90f4c257c417f599fd6bb454abe73fc06eee8e771d3d8a10`.
It reports:

- more than 4,000 CT studies;
- more than 40 volunteer radiologists;
- 18 contributing institutions;
- about 200 studies with AI-generated segmentations;
- MIRA controlled access;
- non-commercial use and no redistribution; and
- a forthcoming Data Resource Publication.

The linked official wiki repository head is
`11dcd6571b312543b63f059617e5f34c265b984b`.  Its dataset page is exactly
11 bytes—`Coming soon`—with SHA-256
`4f7d64017689437e6d93f5724f3f797054f3935d98a13148025b616b8db8fb2c`.
Consequently, no machine-auditable patient manifest, split, annotation lineage,
adjudication protocol or clean-reference subset is public in the inspected
contract.  “About 200 AI segmentations” cannot be relabelled as 200 independent
lesion masks, expert revisions or a clean/noisy paired reference set.

No user terms were accepted, no MIRA request was made, and no S3 object, image,
CSV, segmentation or case-level record was opened.

## Direct-prior correction

The following work closes the tempting generic novelty claims:

1. **Biased-ruler analysis in medical segmentation.** The ISBI 2026 study on
   age-related segmentation disparity distinguishes bias inherited from a
   reference ruler from bias learned or amplified by a model.  An aneurysm
   instance of the same decomposition is an application audit, not a new
   method by itself.
2. **Partial identification under weak supervision.** Weak-reference
   performance can be reported as an identified set instead of a point metric.
   Merely replacing a noisy score by an interval is therefore direct-prior
   occupied.
3. **Large-scale label-noise benchmarking.** LNMBench compares ten noisy-label
   methods across seven medical datasets, six modalities and multiple noise
   mechanisms.  Generic robust-loss or model-ranking claims have a high
   baseline burden.
4. **Active label cleaning.** Review allocation based on model disagreement or
   expected correction utility is established.  Morphometry-based prioritizing
   needs a genuinely new decision estimand and an auditable correction action,
   neither of which is currently available.
5. **Challenge-ranking and revised-benchmark robustness.** Evaluation-unit and
   annotation-version sensitivity remain mandatory analyses, not standalone
   novelty.

Primary sources:

- [Investigating Label Bias and Representational Sources of Age-Related Disparities in Medical Segmentation](https://arxiv.org/abs/2511.00477)
- [Weak Supervision Performance Evaluation via Partial Identification](https://arxiv.org/abs/2312.04601)
- [LNMBench: A Comprehensive Benchmark for Label Noise in Medical Image Classification](https://arxiv.org/abs/2512.09315)
- [Active Label Cleaning for Improved Dataset Quality under Resource Constraints](https://arxiv.org/abs/2109.00574)
- [RSNA-ICA AWS Open Data Registry entry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)
- [RSNA official dataset wiki](https://github.com/RSNA/AI-Challenge-Data/wiki/RSNA-Intracranial-Aneurysm-Detection-Dataset)

## Prospectively frozen candidate screen

Axes are ordered as clinical importance, target identifiability, residual
novelty, asset readiness, effective independent unit, strong-baseline
feasibility, interpretable evidence and ISBI schedule fit.  A candidate needs
total ≥32 **and** identifiability ≥3.5, novelty ≥2.5, asset ≥3.0, unit ≥3.0 and
baseline feasibility ≥3.0.  Scores are frozen without compensatory repair.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| TopAneu revision-robust lesion-set ranking interval | 4.0 / 4.0 / 1.0 / 4.0 / 4.0 / 5.0 / 5.0 / 4.0 | 31.0 | Reject: total and novelty floors; partial-identification and ranking direct priors |
| Versioned morphometry partial identification | 4.5 / 3.5 / 2.0 / 3.5 / 4.0 / 5.0 / 5.0 / 3.5 | 31.0 | Reject: total and novelty floors; no identified clean reference or version action |
| RSNA clean-calibration subgroup risk bound | 5.0 / 3.0 / 1.5 / 2.0 / 5.0 / 5.0 / 4.5 / 3.5 | 29.5 | Reject: no public clean audit subset and controlled asset |
| Reference-provenance-conditioned segmentation | 4.5 / 3.0 / 1.0 / 3.0 / 4.0 / 5.0 / 4.5 / 3.5 | 28.5 | Reject: provenance is not an identified target and biased-ruler prior is direct |
| Active review allocation by morphometric utility | 4.5 / 3.0 / 0.5 / 3.0 / 4.0 / 5.0 / 4.5 / 3.5 | 28.0 | Reject: active cleaning is direct prior and review action is unavailable |
| Subgroup biased-ruler audit for aneurysm masks | 4.5 / 2.0 / 0.5 / 2.0 / 4.0 / 5.0 / 4.0 / 3.5 | 25.5 | Reject: no adjudicated subgroup reference and direct-prior occupied |

The batch best is 31.0/40 and the best residual-novelty score is 2.0/5.  No
candidate passes.  None is a conditional lead.

## What would constitute a material re-entry

The RSNA release-contract watch is intentionally fail closed.  A change only
requests a fresh manual source audit.  It does not accept terms, fetch data,
repair scores, register P0, choose a model or authorize compute.

A future source audit would need to verify all of the following before a new
candidate can even be scored:

1. a versioned release or publication rather than “forthcoming” prose;
2. patient/study grouping and an executable split contract;
3. exact semantics and provenance for AI- and human-generated annotations;
4. an adjudicated clean-reference or review-action contract sufficient to
   identify the proposed estimand; and
5. a non-compositional residual gap beyond biased-ruler analysis, partial
   identification, active cleaning and noisy-label learning.

Only a fresh candidate passing the non-compensatory source gate may open a new,
method-free P0.  P0 would still not select an architecture or authorize GPU.

## Surface-vector boundary retained

If an independent material WSS source change later opens a new evidence
version, the order remains:

1. stable signed-degree and abstention audit;
2. mesh/tolerance/perturbation stability before exact critical-point tracking;
3. field-error-matched baseline failure observation;
4. bounded, one-factor-at-a-time intervention development;
5. fresh family/patient confirmation; and
6. matched-case physical interpretation without rupture-risk claims.

The old `115645.ECE-util1` contract remains closed and is not repaired or
rerun.  AURORA uses only future gate-authorized `introai9` PBS execution.
`junjinyong` is excluded from access, query, transfer, submission and
monitoring, and login-node GPU commands remain prohibited.
