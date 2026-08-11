# Target time and aneurysm-instability prediction reappraisal

**Audit date:** 2026-08-12  
**Protocol state:** schema 10.3 prospective source screen  
**Decision:** all six formulations rejected; no active paper identity, P0,
method, architecture, server query or compute

## Executive verdict

A new seven-hospital study materially narrows the residual gap for
pre-growth/pre-rupture aneurysm-stability prediction. A second 2026 study
already combines vessel-wall MRI, habitat radiomics, deep features, clinical
variables, a Transformer fusion block, calibration, decision curves and SHAP.
The registered ANEURYSM@RISK study prospectively occupies automated
longitudinal MRA morphology plus clinical risk prediction at a much larger
scale.

The remaining scientifically important question is therefore not whether a
more elaborate fusion network can classify “instability.” It is whether every
input and label belongs to a prospectively declared target time and outcome
window, and whether an additional imaging or hemodynamic channel adds value
under patient-grouped, centre-held-out evaluation. No public versioned asset
identified in this audit joins those timestamps, patient/lesion mapping,
images, masks, centre labels and component outcomes. Architecture cannot repair
that missing estimand.

The supplied surface-vector idea remains an inactive, falsifiable structural
question. Nothing in this audit is a material transient-WSS source version, a
stable critical-structure target or an observed field-error-matched failure.

## 1. New direct prior: seven-hospital pre-event stability prediction

Huang et al., *Journal of Clinical Neuroscience* 148 (2026) 111974,
[doi:10.1016/j.jocn.2026.111974](https://doi.org/10.1016/j.jocn.2026.111974),
report:

- 646 patients with 840 aneurysms from Beijing Tiantan Hospital for internal
  development;
- 206 patients with 271 aneurysms from six other hospitals for independent
  external validation;
- CTA, MRA and DSA input sources;
- at least one imaging follow-up per patient;
- features extracted from pre-growth or pre-rupture images;
- external AUC 0.85 (95% CI 0.77--0.94) for radiomics, 0.61 (0.48--0.74) for
  clinical+morphology, and 0.78 (0.67--0.89) for the combined model.

These are source-reported results, not AURORA reproduction. The accessible
publisher abstract and official Crossref record do not expose a versioned
patient table, image/mask release, centre-wise manifest, executable split or
code repository. The exact patient-grouping rules inside development and the
six-centre composition of the pooled external cohort are not established by
the inspected public metadata. Absence from this inspection is not a claim
that the authors possess no such information.

This source directly occupies the broad claims that pre-event radiomics,
multi-modality input and independent multi-hospital validation are themselves
novel.

## 2. New direct prior: VWI habitat--deep Transformer fusion

Li et al.,
[doi:10.3389/fnins.2026.1818110](https://doi.org/10.3389/fnins.2026.1818110),
are a particularly strong architecture-level prior:

- 293 patients and 312 unruptured aneurysms from one centre;
- 197 stable aneurysms from 188 patients and 115 unstable aneurysms from 105
  patients;
- patient-level random 7:3 split: 205/88 patients and 218/94 aneurysms;
- pre/post-contrast high-resolution vessel-wall MRI plus 3D TOF-MRA;
- manual wall/parent-vessel ROI, three K-means habitat regions, radiomics,
  DenseNet features, clinical variables, Transformer fusion and SHAP;
- source validation AUC 0.844 (95% CI 0.743--0.944), compared with 0.816 for
  DenseNet169 and 0.721 for the selected radiomics-habitat model.

The source correctly calls itself exploratory and reports no independent
external validation or optimism-corrected bootstrap. Raw data are
author-available rather than a versioned public asset.

More importantly, “unstable” mixes distinct temporal and biological events:
recent ipsilateral symptoms, growth or daughter-sac appearance on a prior
examination, rupture within three months after the index examination, or
progression across two examinations within six months. This is a legitimate
state-assessment composite, but it is not automatically a single future-event
estimand. A model that sees index VWI while the label partly encodes
pre-index symptoms or already-observed growth answers a different question
from baseline-to-future growth/rupture prediction.

Consequently, habitat radiomics, deep features, Transformer fusion, SHAP,
calibration, DCA, NRI and IDI cannot be claimed as AURORA novelty.

## 3. Near-future direct prior: ANEURYSM@RISK

[ClinicalTrials.gov NCT07111975](https://clinicaltrials.gov/study/NCT07111975)
is an active, not-recruiting retrospective observational study:

- estimated enrollment 3,800;
- MRA and follow-up records from UMC Utrecht, AP-HP Paris and UKE Hamburg;
- automated 3D segmentation and morphological/clinical feature learning;
- growth-or-rupture instability target and planned clinical vignette study;
- estimated primary completion June 2028 and study completion December 2028;
- de-identified derived IPD, protocol, SAP and analytic code planned only after
  the main publication and by qualified-researcher request.

It supplies no current AURORA asset or ISBI-2027 result, but it is a direct
novelty threat to generic “automatic longitudinal morphology risk prediction”
and human-AI decision-support claims. AURORA must not build a paper identity
around being first to that broad problem.

## 4. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total
at least 32 **and** critical floors; a large clinical score cannot compensate
for a missing asset.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Target-time-disjoint future-event benchmark | 5/5/3/0.5/1/5/5/2.5 | **27.0** | Reject: important estimand, but no public timestamped multi-centre patient asset |
| Segmentation/acquisition-uncertainty propagation to instability | 5/4.5/2.5/0.5/1/5/5/3 | **26.5** | Reject: measurement mechanism is meaningful, but patient outcomes and repeated acquisitions are not joined |
| Cross-modality/site-conditional pre-event radiomics transport | 5/4.5/1.5/0.5/1/5/5/3.5 | **26.0** | Reject: seven-hospital radiomics is direct prior and executable rows are unavailable |
| Growth/rupture multi-state competing-risk prediction | 5/5/2.5/0.5/1/5/4.5/2 | **25.5** | Reject: generic multi-state modeling plus no event-time/public cohort |
| External-centre hemodynamic incremental value over radiomics | 5/4.5/2/0.5/1/5/5/2.5 | **25.5** | Reject: no casewise image--CFD--future-outcome join |
| Patient-grouped centre-held-out calibrated selective referral | 5/5/1/0.5/1/5/5/3 | **25.5** | Reject: necessary evaluation correction, not independent method novelty |

No score is repaired from schema 10.2, and no historical candidate or failed
job is relabelled.

## 5. What remains scientifically defensible

Three principles survive as evaluation requirements, not contributions:

1. **Declare target time.** Freeze the index examination, prediction horizon
   and the exact information available at that instant.
2. **Separate endpoint components.** Report future growth, future rupture,
   prior growth and contemporaneous symptoms separately before considering a
   composite.
3. **Test incremental value under real shift.** Compare clinical,
   morphology/radiomics and added hemodynamics using patient-grouped,
   centre-held-out evaluation with calibration and clustered uncertainty.

The surface-vector hypothesis retains its independent evidence order:
stable extraction → observed field-error-matched failure → bounded development
→ fresh confirmation → external interpretation. Edge 1-forms, Hodge/DEC,
SE(3) equivariance, periodic operators and structural losses remain unselected
controls.

## 6. Gate for any future execution

A fresh candidate can enter a method-free P0 only after an official version
provides:

1. patient and lesion identifiers with multiplicity mapping;
2. centre and acquisition metadata;
3. index timestamp and prediction horizon;
4. component outcome timestamps and adjudication rules;
5. proof that every feature precedes the declared target time;
6. lawful, versioned image/mask or feature payload with checksums;
7. patient-grouped development and a genuinely untouched centre or temporal
   confirmation cohort;
8. a residual gap not reducible to fusion, attention, calibration, SHAP or
   another architecture name.

P0 would inventory only these semantics and assets. It would not train a
model. A P0 pass could open a separately registered method-free task-adequacy
P1, not architecture or GPU. Development repair remains possible only after
those gates, with the outer test sealed and a prospective bounded budget.

## 7. ISBI 2027 consequence

ISBI 2027 permits four pages of technical content; a fifth page may contain
only ethics, acknowledgments/conflict information or references. The official
deadline is 26 October 2026. A compact application paper still needs one
identified imaging estimand, one mechanism-linked method and confirmatory
evidence. At present AURORA has none of the three, so adding a Transformer,
GNN or topological loss would make the paper less defensible, not more.

No scientific server was queried, no terms were accepted, and no transfer,
PBS or GPU job was created in this audit. Future authorized execution remains
`introai9` PBS only. Login-node GPU commands are forbidden.
`junjinyong` must never be accessed, queried, used for transfer, submitted to
or monitored.
