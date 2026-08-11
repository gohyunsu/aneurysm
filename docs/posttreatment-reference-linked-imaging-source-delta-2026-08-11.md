# Post-treatment reference-linked imaging source delta

> **Frozen decision · schema 8.5 · 2026-08-11 KST:** a new prospective
> PETRA-MRA/TOF-MRA/DSA study gives a clinically clear reference-linked task,
> and a prospective Helsinki cohort gives DWI and six-month occlusion
> endpoints. Neither creates an executable AURORA paper problem. The six
> prospectively scored formulations are
> **28.5/27.5/26.5/26.5/26.0/24.5**, all below the unchanged 32/40 admission
> line. No image payload, P0/P1, method, architecture, scientific-server query,
> PBS/GPU job, outer test, result row or paper claim is opened.

## 1. Why this batch was inspected

The surface-vector proposal correctly says that field error can differ from a
meaningful downstream structure. That scientific pattern is useful, but the
current WSS version has neither a stable target nor evidence that matched
baselines actually fail. It therefore remains an inactive hypothesis. A
rational search must also ask whether a newer, more directly observed imaging
problem offers a cleaner target and sufficient assets before returning to an
architecture-first surrogate project.

Post-treatment aneurysm surveillance is attractive because the reference is
closer to an observable clinical decision:

1. non-contrast MRA could reduce repeated invasive DSA;
2. residual filling and parent-vessel patency are directly interpretable;
3. DWI detects procedure-related ischemic injury that scalar clinical scores
   can miss; and
4. paired modalities and follow-up times can support compelling case figures.

These advantages improve *importance* and *identifiability*. They do not by
themselves supply an open learning asset or residual algorithmic novelty.

## 2. Source lineage and exact asset boundary

### 2.1 Prospective PETRA-MRA, TOF-MRA and DSA

The 2026 prospective study
[Feasibility and diagnostic performance of PETRA-MRA for postoperative
follow-up of intracranial aneurysms](https://doi.org/10.3389/fneur.2026.1786151)
contains 100 patients with 100 aneurysms. Every included patient underwent
TOF-MRA, PETRA-MRA and DSA at postoperative day 1 and six months. The cohort
contains 72 stent-assisted coiling and 28 flow-diverter cases. DSA is the
reference for aneurysm occlusion. The article reports SAC PETRA-MRA accuracy of
94.44% and 97.67% at the two times and already argues that PETRA-MRA may serve
as a non-invasive follow-up alternative.

This is valuable clinical evidence, but not a public model-development asset.
The data-availability statement says that raw data will be made available by
the authors rather than linking a versioned image repository, case manifest,
license or sealed split. No images were requested or accessed. The 28-case
flow-diverter stratum is also too small to hide by counting two time points as
200 independent patients.

The method lineage is already dense. A 2023 prospective
[SILENT-MRA follow-up study](https://doi.org/10.1136/neurintsurg-2022-018726)
and prior PETRA/UTE studies already target device-artifact reduction and DSA
agreement. The new paper itself evaluates the paired modalities and proposes
non-invasive substitution. A model must therefore solve a residual problem;
“PETRA is better than TOF” is not that problem.

The adjacent outcome-prediction space is also more occupied than a generic
measurement-aware model would suggest. A 458-patient
[quantitative-angiography study](https://arxiv.org/abs/2503.10887) already
deconvolves the parent-artery input, reconvolves an idealized injection curve,
and predicts six-month flow-diverter occlusion from the standardized
angiographic response. It reports AUROC changing from 0.60±0.05 before the
correction to 0.79±0.02 after it and adds per-case LIME explanations. The study
is single-center, uses self-adjudicated outcomes and does not link a versioned
patient dataset or code release. These limitations motivate external
validation; they do not make injection normalization, an explanation head or
occlusion prediction an unoccupied AURORA contribution.

### 2.2 Helsinki DWI and occlusion cohort

The prospective study
[Technique and device specific DWI-detected ischemic lesions and occlusion
outcomes](https://doi.org/10.1007/s00701-026-06934-z) reports DWI for 119
treated patients and six-month angiographic occlusion for 113. It directly
compares the benefit–harm pattern across treatment techniques. Its parent
[Helsinki quality-of-care study](https://doi.org/10.3171/2025.7.JNS25775)
contains 169 patients, MRI within three days and three-month outcomes; the
published analysis already shows that large DWI lesions carry different
clinical information from merely having any lesion.

This is not an open image-learning cohort. The article explicitly states that
researcher-initiated sharing is not possible under the Finnish Secondary Use
Act and that permitted processing requires an official FINDATA decision. The
supplement is a small study document, not patient images or a casewise learning
table. No FINDATA request, patient table or image was accessed.

More importantly, an observational technique comparison does not identify the
counterfactual outcome under an alternative device. A treatment-policy model
would need audited assignment variables, positivity, confounders, a fixed
decision time and an external policy-independent test. High clinical value
cannot compensate for the missing counterfactual estimand.

### 2.3 Public post-clipping table

The open Data in Brief record
[Clipped cerebral aneurysm radiological findings](https://doi.org/10.1016/j.dib.2021.106874)
covers 58 patients, 72 aneurysms and 141 nearby branches assessed with CTA,
TOF-MRA and PETRA-MRA. Its public supplements are an 18.5-KB Excel table and a
37.3-KB PDF. They contain characteristics and visibility assessments, not raw
CTA/MRA volumes. The companion analysis already relates visibility to branch
diameter, clip number, shape, material and hematoma.

This source can reproduce tabular associations. It cannot train or validate an
artifact-robust image model, localize an error, or make an image-based
interpretable case figure. Branches within one patient are repeated
observations, not 141 independent clinical units.

## 3. Why selective prediction is a control, not novelty

A PETRA-first workflow with DSA referral only for uncertain cases is clinically
more defensible than unconditional DSA replacement. But abstention is not a
new method family. [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html)
integrates a reject option into deep networks;
[learning to defer](https://proceedings.mlr.press/v119/mozannar20b.html)
optimizes delegation to an expert; and
[conformal risk control](https://arxiv.org/abs/2208.02814) provides a generic
route to bounded loss. These are mandatory controls. Adding an uncertainty
head, calibration loss or conformal wrapper to PETRA-MRA does not establish an
ISBI contribution.

The residual application question would have to be narrower:

> Under a prospectively fixed PETRA-first policy, can DSA use be reduced while
> controlling the patient-level probability of missing any clinically relevant
> residual filling or parent-vessel abnormality?

That is a clear estimand, but it requires casewise images, blinded DSA labels,
an explicit clinical relevance threshold, device strata, calibration patients
and a sealed external test. None is publicly executable in this batch.

## 4. Frozen eight-axis screen

The axes are biomedical-imaging importance, target identifiability, residual
novelty, usable asset readiness, effective independent-unit strength,
strong-baseline feasibility, interpretable-figure value and ISBI-schedule fit.
Each is scored from 0 to 5 before any development.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PETRA-first selective DSA referral with a patient-level missed-residual budget | 5.0 | 4.5 | 1.5 | 1.0 | 4.5 | 5.0 | 5.0 | 2.0 | **28.5** | reject: direct comparison + no public images |
| Device-conditioned residual-filling estimation | 4.5 | 4.5 | 1.0 | 1.0 | 4.0 | 5.0 | 5.0 | 2.5 | **27.5** | reject: request-only images; FD n=28 |
| Longitudinal occlusion-change concordance | 4.5 | 4.0 | 1.0 | 1.0 | 4.0 | 5.0 | 4.5 | 2.5 | **26.5** | reject: paired comparison already analyzed |
| DWI lesion-size outcome stratification | 5.0 | 3.0 | 1.0 | 0.5 | 4.5 | 5.0 | 5.0 | 2.5 | **26.5** | reject: no public image asset; endpoint already analyzed |
| Post-clip branch-visibility reliability | 4.0 | 4.0 | 0.5 | 3.0 | 3.5 | 5.0 | 2.0 | 4.0 | **26.0** | reject: table only; no raw images/reference |
| Treatment-technique benefit–harm decision model | 5.0 | 2.0 | 1.0 | 0.5 | 4.5 | 5.0 | 4.0 | 2.5 | **24.5** | reject: observational counterfactual absent |

The 28.5 leader is not repaired upward for clinical relevance. A request-only
cohort is not a schedule-ready asset, and a standard selective-inference layer
is not residual novelty. Two visits, modalities, lesions or branches do not
increase the patient count.

## 5. Decision for AURORA and the surface-vector proposal

- The new clinical imaging sources do **not** replace surface-vector with an
  active paper identity. They demonstrate that even a clearer clinical endpoint
  remains unusable without auditable image-level assets.
- Surface-vector stays an inactive hypothesis. Its proper next scientific step
  remains a fresh material source change followed by method-free stability and
  field-error-matched failure evidence—not the edge-1-form architecture.
- PETRA-first selective DSA referral is retained as a rejected, well-defined
  formulation. It may be rescored only after a versioned patient-level release
  exposes paired images, DSA reference semantics and a lawful development/test
  contract.
- Helsinki DWI data are not pursued by bypassing FINDATA. An official access
  decision would still trigger a new source audit, not automatic training.
- The public clipped table is useful background evidence only. It is not
  relabelled as an image dataset.
- SelectiveNet, learning-to-defer, conformal risk control, PETRA/UTE/SILENT MRA
  comparison and the published DWI/occlusion analysis are baselines/direct
  priors, not AURORA contributions.

No scientific server or scheduler was queried. No data terms were accepted and
no scientific payload was opened. Future gate-authorized execution remains
restricted to `introai9` PBS; login-node GPU commands are prohibited.
`junjinyong` remains prohibited for connection, inspection, transfer,
submission and monitoring.
