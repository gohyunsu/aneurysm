# Method--asset viability red team · 2026-08-10

## Decision

This audit asks a narrower question than another architecture brainstorm: does a
currently obtainable asset identify a task whose residual algorithmic gap remains
after the strongest 2025--2026 direct priors? The admission rule was frozen before
payload access at the existing eight 0--5 axes and 32/40 line: biomedical
importance, target identifiability, residual novelty, usable asset readiness,
effective independent unit, strong-baseline feasibility, interpretable-figure
value, and ISBI-schedule feasibility.

All five candidates remain below admission. Two candidates tie at **30.0/40**.
Active shortlist, selected primary problem, executable P0, method, architecture,
PBS/GPU training, outer test, submission identity and paper claim therefore remain
**zero**. No patient image, mask, surface, CFD field or controlled challenge
payload was read. The current no-job state is a scientific early stop, not an
`introai9` failure.

| Candidate | Importance | Identifiability | Residual gap | Asset | Independent unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Royal reference-morphometry certificate | 4.5 | 4.0 | 0.5 | 4.5 | 3.5 | 5.0 | 5.0 | 3.0 | **30.0** | reject |
| Partial-observation solution-functional operator | 4.5 | 5.0 | 0.5 | 2.5 | 5.0 | 5.0 | 4.5 | 3.0 | **30.0** | reject |
| IAVS topology-to-CFD reliability | 5.0 | 5.0 | 0.5 | 0.5 | 5.0 | 5.0 | 5.0 | 3.0 | **29.0** | reject |
| RSNA reader-source reliability | 5.0 | 1.0 | 2.0 | 1.0 | 5.0 | 5.0 | 4.0 | 3.0 | **26.0** | reject |
| CQ500 provenance-aware multimodal adaptation | 4.5 | 1.0 | 1.0 | 0.0 | 5.0 | 5.0 | 4.0 | 2.5 | **23.0** | reject |

The totals are the arithmetic sums of the displayed cells. A rejection applies to
this exact candidate version; it is not a judgment that the source dataset or
paper is unimportant.

## 1. Royal reference-morphometry certificate · 30.0/40

The [Royal Brisbane OpenNeuro dataset](https://github.com/OpenNeuroDatasets/ds005096)
is an unusually clear open source: 63 patients, 85 aneurysms, 24 longitudinal
patients, TOF-MRA, clinician segmentations, aneurysm and parent-vessel STL files,
and clinical annotations. Its current public `main` remains exact
`0760bf865612600c4eee85f6f437aefaeb534204`.

A tempting method would return calibrated intervals for neck width, volume or
other mask-derived morphometry. That target must be described as the value derived
from the released reference annotation, not unknown biological truth. The mask and
STL are two representations of the same annotation pipeline, not independent
observers or an absolute anatomy reference.

More importantly, the residual method is directly occupied:

- [COMPASS, ICLR 2026](https://arxiv.org/abs/2509.22240) constructs conformal
  intervals for downstream metrics derived from medical segmentations, perturbs
  metric-sensitive feature subspaces, and includes covariate-shift weighting.
- [Robust conformal volume estimation](https://arxiv.org/abs/2407.19938) already
  studies calibrated 3D volume intervals under covariate shift.
- [NeckSpline](https://www.nature.com/articles/s41746-026-02613-6) treats the
  aneurysm neck as a differentiable topology-preserving spline, evaluates width
  and angle, and reports perturb-and-refit uncertainty with nominal 95% coverage.
- Spatial, anatomical and morphological conformal segmentation sets are already
  represented by [SACP](https://openreview.net/forum?id=uQaPr1wU1W),
  [RW-CP](https://arxiv.org/abs/2601.18997), and
  [morphological prediction sets](https://arxiv.org/abs/2503.05618).

Applying one of these methods to aneurysm morphometry, adding several scalar
functionals, or naming mask--mesh agreement a new certificate is not an independent
contribution. The 63-patient positive cohort is useful for external stress testing,
but it does not rescue the residual novelty.

## 2. Partial-observation solution-functional operator · 30.0/40

The original AURORA question asked whether full, partial and missing physical
conditions could be handled by one coherent probabilistic operator. Historical
controlled-PDE and nonlinear-PDE experiments preserve useful negative evidence:
exact nesting was achievable, but conditional accuracy and decision superiority
were not. The latest literature further narrows rather than reopens the gap.

- [Neural Operator Processes](https://arxiv.org/abs/2606.22946) directly study
  deterministic and probabilistic operator learning from sparse joint input--output
  observations.
- [Learned function extensions](https://arxiv.org/abs/2602.04923) handle variable
  boundary conditions in neural operators.
- [Amortized conditioning by neural operators](https://arxiv.org/abs/2605.06873)
  treats conditioning itself as an operator.
- DeltaPhi, arbitrary-conditioning generative models, active operator learning and
  decision-focused acquisition remain mandatory controls.

A generic joint density, arbitrary mask encoder, tower-property penalty, GNN,
attention block or functional loss therefore does not create novelty. The old N1c
outer result remains failed and is not relabeled. No open aneurysm asset currently
provides the paired condition--field--decision target required for a new medical
claim.

## 3. IAVS topology-to-CFD reliability · 29.0/40

The [IAVS paper](https://arxiv.org/abs/2512.01319) reports 641 3D MRA images,
587 aneurysm/parent-vessel annotations, centerlines, meshes, boundary labels, CFD
outcomes and a CFD-applicability evaluation. These would be valuable assets, but
the official repository still has exact `main`
`2e40088d9eaa671c592929a154b7b2cf99f9320a`, one 90-byte README, no release, no
repository license and no code/data/model payload. The paper itself already defines
two-stage localization/segmentation, topology-aware learning and CFD applicability.

Consequently this branch is both unavailable and directly occupied. It remains a
machine-monitored source watch, not an admitted task. A future material release may
trigger a fresh source audit only; it cannot automatically authorize download, P0,
method or GPU work.

## 4. RSNA reader-source reliability · 26.0/40

The [official RSNA registry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)
now describes more than 4,000 CT scans, more than 40 volunteer radiologists, 18
institutions and about 200 studies with AI-generated segmentations. It remains
controlled access with no redistribution, and the user has not accepted its terms.
The [official data wiki](https://github.com/RSNA/AI-Challenge-Data/wiki/RSNA-Intracranial-Aneurysm-Detection-Dataset)
still says `Coming soon`.

Public challenge evidence identifies aneurysm center/presence/location labels and
13-class vessel-anatomy segmentation, not a released per-reader label matrix,
adjudication trail or lesion-extent mask. More than 40 contributors do not imply 40
independent labels for every case. Reader-disagreement modeling, label-source
calibration or AI-assistance policy is therefore not identifiable from the current
public semantics. No account was created, no terms were accepted and no payload
was accessed.

## 5. CQ500 provenance-aware multimodal adaptation · 23.0/40

The 2026 AMAP paper describes CQ500 as a large CTA cohort and cites an open-source
aneurysm-annotation repository. The original CQ500 source is a non-contrast head-CT
collection, while the cited `ycchen218/CQ500-IA` repository currently returns
`repository not found` to an unauthenticated public Git remote. A paper citation is
not a versioned, licensed, machine-auditable asset.

This discrepancy is important provenance evidence but does not identify a model
task. Domain adaptation, anatomy-guided masked pretraining and multimodal prompting
are also directly occupied by AMAP and related work. Until an official versioned
annotation release and scan-to-mask manifest are available, no source score, split,
baseline or claim may rely on the reported approximately 490 cases.

## Frozen external-state check

The source audit used names, public metadata and exact Git refs only.

| Source | Observed public state |
|---|---|
| AneuG-Flow dataset | exact `main` `9dd418083899deddd93a67f9a6fca7a14304fa36`; unchanged closed-P0 source version |
| AneuG-Flow code | exact `master` `4a090a0f12538deef6fcea88b81afe78ce38152e`; unchanged |
| IAVS | exact `main` `2e40088d9eaa671c592929a154b7b2cf99f9320a`; README-only |
| Royal OpenNeuro mirror | exact `main` `0760bf865612600c4eee85f6f437aefaeb534204`; unchanged |
| CQ500-IA citation target | public Git remote not found |

An authenticated public-key check reached `introai9` as remote user `introai9` on
`ECE-util2`; `qstat -u introai9` returned no jobs. No login-node GPU command was
executed. `junjinyong` was not connected to, queried, submitted to or monitored.

## Consequence

There is no current GNN, Transformer, U-Net, diffusion model or neural operator.
The next allowed action is a material source-release watch or a genuinely new
problem with an observable target, public/authorized independent units and residual
novelty after the direct controls above. Only a fresh candidate scoring at least
32/40 may open a separately frozen, method-free CPU/read-only P0 on `introai9`.
P0 pass may open task adequacy only; architecture and GPU remain contingent on that
second gate. Closed P0s and failed confirmatory results are not repaired or relabeled.
