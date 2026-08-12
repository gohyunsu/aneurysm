# Open clinical outcome and target-time reappraisal

**Decision date:** 2026-08-12  
**Protocol:** AURORA schema 11.4  
**Verdict:** all six candidates rejected; active dataset, problem, method and compute remain zero

## Executive decision

A fresh 2026 search identified one genuinely material public asset that was not
in the previous lineage: Zenodo record
[`17339029`](https://zenodo.org/records/17339029). Its exact revision 6 exposes
one CC BY 4.0 file, `Data_aSAH-Risk_Score.xlsx` (39,686 bytes; MD5
`8aaba92f5fb74175af76edd3701b7404`). This is a real clinical table associated
with 230 retrospectively included patients with aneurysmal subarachnoid
hemorrhage (aSAH), not a synthetic table.

That is a public material asset, but it is **not an active AURORA dataset**.
The release contains no CT/MR/angiographic image payload, aneurysm mask or
case-wise image–row join. More importantly, the paper reports that 6-month mRS
was unavailable for 70 patients: 39 died at discharge and 31 were lost to
follow-up; a discharge or 3-month value was used when the 6-month value was
unavailable. A column called “6-month outcome” therefore does not by itself
identify one fixed-time estimand. The XLSX was not downloaded or opened, so its
row schema, identifiers and missing-value coding remain uninspected.

The best candidate scores 29.5/40 and fails the non-compensatory target-time,
residual-novelty and imaging-asset requirements. No P0, method, architecture,
GPU experiment or paper claim is authorized.

## What was actually found

| Source | Actual scientific unit | Public executable object | What it can support | What it cannot support |
|---|---:|---|---|---|
| [Ritter et al., 2026](https://doi.org/10.3389/fneur.2026.1781480) | 230 included aSAH patients; 17 variables | Versioned 39,686-byte XLSX, CC BY 4.0 | Table-level reproducibility and outcome-provenance audit | Image learning, a pure fixed 6-month target, external validation |
| [ASIS one-year mRS](https://doi.org/10.1016/j.compbiomed.2026.111731) | 487 real UIA patients in the source cohort | [Public repository](https://github.com/learbuehrer/asisR) contains synthetic data only | Reproducible code-path and synthetic example | Reanalysis of the 487 actual patients or a new clinical result |
| [Instability-score study](https://pubmed.ncbi.nlm.nih.gov/42390970/) | 2,258 aneurysms; 519 followed UIAs; 71 instability events | No verified versioned patient/image release | Direct-prior definition of growth/rupture instability | Public longitudinal model development or external confirmation |
| [Mixed-effects ABN](https://doi.org/10.1016/j.compbiomed.2025.111380) | 3,180 patients with solitary ruptured IA from seven centres | No verified public patient table or images | Direct prior for centre-aware dependency analysis | Future rupture prediction; the cohort is ruptured-only and cross-sectional |
| [Circle of Willis study](https://doi.org/10.3174/ajnr.A9428) | 1,021 IA patients and 1,052 controls | No verified public TOF-MRA/manifest | Direct prior for CoW anatomy association | A public image benchmark or longitudinal clinical endpoint |

Counts and reported performance from these sources are not AURORA results.
No cohort count is relabelled as a downloaded manifest or an independent test
set.

## Why the open table does not identify the proposed endpoint

An estimand must specify who is measured, what event is measured and when it is
measured. “Unfavourable outcome after six months” appears precise, but source
handling creates at least three observation times:

1. discharge for patients who died before discharge;
2. three months where that value substitutes for unavailable six-month mRS;
3. six months where follow-up exists.

Those values can be clinically defensible for the source analysis without
being interchangeable ground truth for a new fixed-time prediction task. A
model could learn both prognosis and follow-up availability. Without an exact
row-level provenance indicator and a prospectively declared missing-outcome
policy, better discrimination would not establish better six-month prognosis.

The release also has no medical images. Using categorical radiological grades
as if they were CT images would change the task from medical imaging to tabular
score replication. That can be useful work, but it is neither the intended ISBI
identity nor an independent contribution after the source paper has already
developed the score.

## Eight-axis non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. A total of 32 is necessary but
not sufficient; target ≥3.5, novelty ≥2.5, asset ≥3.0, unit ≥3.0 and baseline
≥3.0 must also pass.

| Rank | Candidate | Scores | Total | Critical decision |
|---:|---|---|---:|---|
| 1 | Endpoint-provenance-aware aSAH six-month prognosis | 4.5 / 2.5 / 2.0 / 4.0 / 3.5 / 5.0 / 4.0 / 4.0 | 29.5 | Reject: mixed observation times, no images, direct prediction prior |
| 2 | ASIS management → one-year mRS | 5.0 / 4.5 / 0.5 / 1.0 / 4.0 / 5.0 / 4.5 / 3.5 | 28.0 | Reject: public data are synthetic and task is directly occupied |
| 3 | Admission-only external calibration of aSAH-Risk | 4.5 / 4.0 / 0.5 / 2.0 / 3.0 / 5.0 / 4.5 / 3.5 | 27.0 | Reject: no external cohort; calibration alone is not a paper identity |
| 4 | Risk-score refinement for future instability | 5.0 / 4.0 / 0.5 / 0.5 / 4.0 / 5.0 / 5.0 / 3.0 | 27.0 | Reject: direct prior and no public longitudinal patient asset |
| 5 | Circle-of-Willis imaging-marker transport | 4.0 / 3.5 / 0.5 / 0.5 / 5.0 / 5.0 / 4.5 / 3.0 | 26.0 | Reject: direct case-control prior and no public TOF-MRA manifest |
| 6 | Centre-robust rupture-phenotype dependency | 4.0 / 3.0 / 0.5 / 0.5 / 5.0 / 5.0 / 4.0 / 3.5 | 25.5 | Reject: ruptured-only cross-sectional source and private rows |

## Dataset ledger: precise meanings of “secured”

| State | Current value |
|---|---|
| Stable public metadata and file contract verified | **1**: Zenodo 17339029 revision 6 |
| Public patient table downloaded or opened by AURORA | **0** |
| Public medical image joined to that table | **0** |
| Current-direction staged train / validation / test | **0 / 0 / 0** |
| introai9 current directory inventory verdict | **Incomplete / no asset verdict** |
| Active ISBI dataset | **0** |

Thus, “one public clinical table is available in principle” and “AURORA has an
active usable dataset” are not synonymous. The former is true; the latter is
false.

## What would change the decision

A fresh candidate may be admitted only if a stable release supplies all of the
following together:

- a medical image or geometry payload with immutable patient/lesion IDs;
- a prespecified landmark and fixed outcome horizon, with censoring and
  missingness semantics;
- patient-grouped development/test membership and preferably a held-out centre;
- enough outcome events for a bounded method-free feasibility test;
- a residual scientific question not already answered by risk-score
  development, generic calibration or a larger architecture.

Zenodo record 17339029 is now frozen in source-watch v21. A future revision can
request a fresh source audit only. It cannot automatically download data,
register P0, select a model or authorize GPU execution.

## Operational boundary

This update queried public bibliographic and release metadata only. No XLSX,
patient image, mask or clinical-row payload was downloaded or opened. No
scientific server, PBS scheduler or GPU was queried. Future gate-authorized
execution is restricted to `introai9` through PBS; login-node GPU commands are
forbidden. `junjinyong` is excluded from all access, query, transfer,
submission and monitoring.
