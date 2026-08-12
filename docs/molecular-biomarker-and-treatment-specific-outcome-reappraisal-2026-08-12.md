# Molecular-biomarker and treatment-specific outcome reappraisal

**Decision date:** 2026-08-12  
**Decision:** reject all six fresh formulations; open no active problem, P0,
method, architecture, scientific-server query, PBS/GPU job, outer test or paper
claim.

## Executive judgment

Public molecular data remove one asset bottleneck but do not create an
independent ISBI paper identity. The strongest reusable source, PXD024615,
contains patient-level serum-proteomic cohorts and small immutable public
supplements. Its source paper already performs the obvious machine-learning
task: aneurysm-versus-control and ruptured-versus-unruptured classification on
212 development/internal-validation samples with a separate 32-sample cohort.
The source also states that all aneurysm patients were inspected with 3D
rotational DSA, but no corresponding versioned image release or future-event
timeline is exposed. Replacing its sparse classifier with a transformer, GNN or
multimodal fusion block would therefore repeat the task without supplying a new
estimand.

The 2026 NBC-GARUDA study adds a distinct clinical question, but not an
executable asset. It develops treatment-specific in-hospital outcome models in
436 patients, 86.9% of whom presented with rupture, and reports only internal
bootstrap validation. It is a prognostic model conditional on the treatment
received, not an estimate of the counterfactual benefit of clipping versus
coiling. No public row-level cohort or external test was identified.

The best additive score in this batch is 31.0/40. It fails the mandatory
residual-novelty floor at 0.5/5. The most conceptually novel formulation—joint
pre-event imaging and molecular progression prediction—fails because no
same-patient baseline image, pre-event blood measurement, follow-up time and
outcome release exists. No model or compute is justified.

## 1. What PXD024615 makes reusable

The exact primary source is
[`10.15252/emmm.202114713`](https://doi.org/10.15252/emmm.202114713). It
quantifies 113 peptide candidates corresponding to 100 proteins in serum cohort
I (212 samples: 55 ruptured, 57 unruptured and 100 controls) and cohort II (32
samples: 6 ruptured, 6 unruptured and 20 controls). The source reports a
75%/25% development/internal-validation split of cohort I and uses cohort II as
an external validation set. Its reported classification results are source
results, not AURORA reproductions.

The source's Europe PMC record exposes immutable supplementary metadata. Dataset
EV1 is `EMMM-14-e14713-s024.xlsx`, 13,784 bytes, MD5
`b22ecc3da824b8a72a767ff39cb649be`; EV2 is
`EMMM-14-e14713-s022.xlsx`, 13,642 bytes, MD5
`5f9b9b933f8546659378a11264089735`. Mass-spectrometry data are deposited under
ProteomeXchange accession PXD024615 via iProX. AURORA inspected only the
official article/XML and repository metadata; the spreadsheets and raw
mass-spectrometry payload were not downloaded.

The same source states that 3D rotational DSA was reviewed for the aneurysm
patients and that size, width and neck diameter were recorded. This does not
establish a public image--proteome pair: no DSA volume, segmentation, immutable
image identifier, acquisition metadata or patient-level image-to-serum join is
present in the inspected release contract. A clinical table or mention of image
review is not a medical-image dataset.

Most importantly, ruptured and unruptured status is observed at presentation.
Serum collected around that clinical episode can support diagnostic
stratification, but it cannot be relabelled as a baseline predictor of future
rupture. The event may itself alter the circulating proteome. A future-risk
claim would require blood sampled before a declared prediction time and
prospective follow-up or censoring.

## 2. Why other open omics records do not repair the estimand

PXD013442 is a real public ProteomeXchange record with 42 listed files. Its
discovery design uses 20 tissue and 20 serum samples across four clinical
groups, but five individual samples within each group are pooled before iTRAQ
analysis. The effective discovery unit is therefore four biological pools, not
20 independently learnable patients. The larger validation phase measures
selected ORM1 and MMP9 candidates; it does not turn the pooled untargeted data
into a patient-level imaging benchmark.

GEO GSE231922 is also genuinely public: 30 plasma-miRNA samples, ten smoking IA,
ten non-smoking IA and ten healthy controls, with raw SRA data and a processed
matrix. Its primary task is the molecular association of smoking status in IA.
It is not a longitudinal rupture cohort, has no released lesion imaging or
patient-level future event, and its 10/10/10 design is not an independent
confirmatory population.

These sources are useful for biological hypothesis generation. Combining them
post hoc is not a valid multi-omics cohort because the patients, collection
protocols, disease states and targets differ. Batch integration cannot create
same-patient multimodality or a causal temporal order.

## 3. What the new treatment-specific model establishes

[`10.1016/j.jocn.2026.112073`](https://doi.org/10.1016/j.jocn.2026.112073)
reports 436 consecutive index treatment episodes: 224 coiling and 212 clipping.
The endpoints are in-hospital mortality, good GOSE and recovery of GCS to the
premorbid baseline. The source uses separate logistic regressions for each
treatment--outcome pair with multiple imputation, bidirectional AIC selection
and 500 bootstrap resamples. It explicitly describes the calculator as
preliminary, single-centre and pending temporal/external validation. Source AUCs
are not AURORA results.

Conditioning prediction on the treatment actually received does not identify
which treatment would have been better for the same patient. Treatment choice
reflects anatomy, severity, clinical resources and operator judgment. A
counterfactual decision model needs a pre-treatment eligibility set, overlap,
measured confounders, a treatment policy estimand and an external validation
contract. A larger neural model or treatment token does not supply those
assumptions.

The cohort is predominantly ruptured (86.9%) and the endpoints are in-hospital.
It should not be merged conceptually with long-term unruptured-aneurysm growth,
preventive treatment selection or delayed angiographic occlusion. Those are
different populations, information times and outcomes.

## 4. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at least
32 and every critical floor; total score cannot compensate for a novelty,
target, asset or unit failure.

| Candidate | Axis scores | Total | Binding rejection |
|---|---:|---:|---|
| Cross-cohort serum-proteomic rupture-state calibration | 4.5/4.0/0.5/4.5/4.0/5.0/4.0/4.5 | **31.0** | Source already performs internal and external rupture-state classification; not future risk |
| Morphology-conditioned proteomic incremental value | 4.5/2.5/1.0/3.0/4.0/5.0/4.0/4.0 | **28.0** | No public DSA/image-to-serum join or fixed image-derived reference |
| Smoking-conditioned plasma-miRNA mechanism | 4.0/2.5/0.5/4.5/2.5/5.0/4.0/4.0 | **27.0** | 10/10/10 cross-sectional groups; task and biomarker analysis are direct prior |
| Treatment-specific in-hospital outcome recalibration | 5.0/4.5/0.5/0.5/3.5/5.0/4.5/3.5 | **27.0** | Single-centre rows unavailable; source already owns the prognostic task |
| Pooled tissue/serum proteomic reanalysis | 4.0/4.0/0.5/4.0/0.5/5.0/4.0/4.0 | **26.0** | Four biological iTRAQ pools, not 20 independent discovery patients |
| Pre-event imaging--proteomic progression prediction | 5.0/2.0/2.5/0.5/1.0/4.5/5.0/2.5 | **23.0** | No same-patient baseline image, pre-event blood, time-to-event or censoring asset |

The 31.0 leader is executable in principle but scientifically occupied. The
23.0 row has more conceptual room but no identifiable target or material asset.
This is exactly why architecture must follow problem admission rather than lead
it.

## 5. What would materially change the decision

A molecular-imaging progression version can be rescored only if one immutable
release joins:

1. patient, lesion and centre identifiers with patient-grouped splits;
2. baseline CTA/MRA/3DRA and expert lesion/parent-vessel references;
3. blood sampled before the explicitly declared prediction time;
4. sample-level molecular measurements without group pooling;
5. separately coded future growth, morphological change, rupture, treatment and
   censoring times;
6. an untouched centre- or time-held-out confirmation cohort;
7. predefined clinical+morphology and molecular-only baselines, with incremental
   value, calibration and decision utility assessed at the patient level.

A treatment-selection version additionally needs an explicit causal estimand,
pre-treatment eligibility, overlap diagnostics and outcome horizons that are
meaningful for both treatment arms. A prognostic calculator conditional on the
observed treatment is not a treatment-effect model.

The first authorized action would still be a method-free audit of unit mapping,
target time, batch structure, missingness, treatment/censoring and independent
event counts. Only an observed and stable failure of fixed strong baselines may
motivate a minimal model.

## 6. Operational boundary

- Active lead, primary problem, P0/P1, method, architecture, scientific-server
  query, PBS/GPU job, outer test, result row, C21 and paper claim: **zero**.
- No omics spreadsheet, raw mass-spectrometry file, sequencing payload, patient
  image or clinical row table was downloaded.
- Historical surface-vector job `115645.ECE-util1` remains immutable
  execution-incomplete/no-verdict and is not repaired or rerun.
- Future gate-authorized work may use only `introai9` through PBS; login-node
  GPU commands are forbidden.
- `junjinyong` must never be accessed, queried, transferred to, submitted to or
  monitored.

## Primary sources

- PXD024615 source paper: <https://doi.org/10.15252/emmm.202114713>
- PXD024615 repository record: <https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=PXD024615-1>
- PXD013442 repository record: <https://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=PXD013442>
- PXD013442 source paper: <https://doi.org/10.1089/omi.2020.0057>
- GSE231922: <https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE231922>
- GSE231922 source paper: <https://doi.org/10.1007/s40120-023-00547-9>
- NBC-GARUDA: <https://doi.org/10.1016/j.jocn.2026.112073>
