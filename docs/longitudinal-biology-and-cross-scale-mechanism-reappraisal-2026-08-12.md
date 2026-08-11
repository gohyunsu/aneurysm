# Longitudinal biology and cross-scale mechanism reappraisal

> **Frozen delta decision · schema 10.7 unchanged · 2026-08-12 KST:** Recent
> human studies do contain genuine future follow-up, so it would be wrong to
> say that all current aneurysm evidence is cross-sectional. They still do not
> expose a versioned patient--image--biomarker--time--event asset, and the
> strongest association and imaging-endpoint questions are already occupied.
> A serial rat MRA study adds a useful detectability reference, not a public
> human progression benchmark. Six residual formulations score
> **28.5/26.5/25.0/23.0/22.5/20.0**; all fail at least one mandatory gate. No
> patient or animal payload, request, P0/P1, method, architecture, scientific
> server, PBS/GPU job, outer test or paper claim is opened.

This audit asks whether new biological and longitudinal evidence supplies the
missing application identity for AURORA, or supports the inactive
surface-vector hypothesis. It does neither. This is a source-level correction,
not a negative judgment on the source studies.

## 1. Human future follow-up exists, but the targets must stay separate

The long-term multicentre AWE study
[`10.1002/ana.78106`](https://doi.org/10.1002/ana.78106) is the most important
correction to an overly broad claim that the field has no future-event
evidence. It follows 198 patients with 224 untreated aneurysms from two
international cohorts for a median of 6.8 years. Its composite instability
endpoint is time to growth, morphological change or rupture. The source reports
28 events: 15/72 aneurysms with baseline wall enhancement and 13/152 without
enhancement, with adjusted HR 5.06. These are source-paper results, not AURORA
results.

This evidence does not create an unoccupied ML task. The article already owns
the baseline-AWE-to-long-term-instability association. Its endpoint is a
composite rather than pure rupture, and preventive treatment and end of
radiological follow-up produce censoring. The inspected public sources expose
no immutable patient/image/event/split artifact from which AURORA can reproduce
the survival analysis or perform a clean centre-held-out model comparison.
Adding a transformer, GNN, survival head or calibration layer would not create
the missing asset or an independent contribution.

The Academic Radiology study
[`10.1016/j.acra.2026.04.002`](https://doi.org/10.1016/j.acra.2026.04.002)
reports three distinct datasets: a local cross-sectional cohort of 308 patients
with 416 aneurysms for NHR/SIRI and wall enhancement, a local longitudinal
cohort of 80 patients with 85 aneurysms for growth, and UK Biobank for incident
aSAH. It reports associations of NHR/SIRI with AWE and growth, and an association
of NHR with incident aSAH. None is an AURORA result.

Those three analyses do **not** identify the patient-level mediation chain
`inflammation -> AWE -> growth -> aSAH`. They use different cohorts and
endpoints. Population-level consistency can motivate a hypothesis, but cannot
replace same-person temporal measurements, intervention timing, censoring and
mediation assumptions. UK Biobank is also a controlled research resource, not
a public aneurysm-image release joined to the local VWI cohorts.

A second 2026 HRVWI study
[`PMID 41913331`](https://pubmed.ncbi.nlm.nih.gov/41913331/) reports 311
patients/418 aneurysms and a longitudinal sub-cohort of 67 patients/84
aneurysms with median follow-up of 7.0 months. It strengthens the direct-prior
claim that systemic inflammatory indices, AWE and growth have already been
studied together. It does not expose a stable public image/biomarker/follow-up
contract, and a short longitudinal sub-cohort is not an external long-term
event benchmark.

## 2. The rat study identifies a measurement limit, not a ready benchmark

The open Scientific Reports study
[`10.1038/s41598-026-37369-2`](https://doi.org/10.1038/s41598-026-37369-2)
serially images the Hashimoto rat model at W0, W1, W4 and W12 using 7 T TOF-MRA,
T2 and black-blood imaging, with terminal SEM/corrosion casting as reference.
Thirteen induced rats reach W1; all reach W4, but only eight reach W12 because
five die early, including three with SAH. Six controls complete all timepoints.

The source reports lesion-level MR sensitivity 40% and specificity 60%. Its
TOF-MRA resolution is approximately 0.146 mm isotropic, whereas the largest of
six SEM-confirmed false-negative aneurysms is 0.10 mm. This is a scientifically
useful resolution-linked failure mechanism. It is already the source study's
result, not an observed AURORA model failure.

The MR, SEM, measurement and statistical datasets are available only on
reasonable request. The small effective animal count, event-dependent attrition,
induced fusiform posterior-circulation lesions and sub-resolution
microaneurysms also prevent direct relabelling as a human saccular-aneurysm
progression benchmark. Repeated phases, vessel segments or histology patches
must not be counted as independent animals.

The previously audited tissue-ingrowth study
[`10.1038/s41598-026-43798-w`](https://doi.org/10.1038/s41598-026-43798-w)
already occupies automated preclinical sac/tissue-ingrowth segmentation and
quantification on 64 selected histology images. Its plugin code is public but
the image cohort is request-only, and no public paired angiography--histology
manifest identifies treatment healing. It remains a direct prior; this audit
does not rescore it as a newly discovered asset.

## 3. What this means for surface-vector

None of these sources contains transient surface WSS, signed critical points,
worldlines, a matched conventional surrogate, or a patient/animal-level join
from those structures to growth, rupture or healing. They therefore do not
satisfy surface-vector E0 and do not authorize the proposed edge-1-form/Hodge/
SE(3)/periodic architecture.

The surface-vector statement remains a plausible conditional hypothesis:
field-accurate transient WSS surrogates may fail to preserve meaningful
critical-flow organization. It becomes an application identity only after a
method-free stability audit and a field-error-matched baseline failure are
observed on a fresh, executable contract. Biological association papers cannot
substitute for that failure evidence.

## 4. Frozen non-compensatory screen

Axes are scored 0--5 in the established order: clinical importance, target
identifiability, residual novelty, asset readiness, effective independent unit,
strong-baseline feasibility, interpretable evidence and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Baseline-AWE incremental survival value beyond clinical/morphology | 5.0 | 4.0 | 1.5 | 1.0 | 4.0 | 5.0 | 4.5 | 3.5 | **28.5** | reject |
| Component-specific long-term instability with intervention/censoring | 5.0 | 3.5 | 1.0 | 1.0 | 3.0 | 5.0 | 4.5 | 3.5 | **26.5** | reject |
| Resolution-calibrated preclinical MRA--SEM detectability | 4.0 | 4.0 | 0.5 | 1.0 | 2.0 | 5.0 | 5.0 | 3.5 | **25.0** | reject |
| Angiography-to-histological healing bridge | 4.5 | 2.0 | 0.5 | 1.0 | 2.0 | 5.0 | 5.0 | 3.0 | **23.0** | reject |
| Same-patient inflammation--AWE--growth--aSAH mediation | 5.0 | 1.5 | 2.5 | 0.5 | 1.5 | 4.0 | 5.0 | 2.5 | **22.5** | reject |
| Animal-to-human longitudinal instability transport | 4.5 | 1.0 | 2.5 | 0.5 | 1.0 | 3.5 | 5.0 | 2.0 | **20.0** | reject |

The 28.5 leader has an identifiable and important endpoint, but its scientific
question is already substantially answered and the row-level source asset is
not public. The mediation and cross-species rows retain more conceptual room,
but fail target, asset and independent-unit floors. A fancy cross-modal model
would hide, not repair, those failures.

## 5. Re-entry contract

A future biological-mechanical progression version can be rescored only if one
immutable release joins:

1. baseline patient and lesion IDs, centre and acquisition time;
2. blood biomarkers measured before the declared prediction time;
3. registered HRVWI/MRA/CTA and, for a surface claim, geometry and transient CFD;
4. serial growth/morphological-change observations with measurement tolerance;
5. separately coded rupture, growth and morphology events rather than only a
   composite label;
6. treatment, loss-to-follow-up, death and censoring times;
7. patient-grouped development and untouched centre-held-out confirmation;
8. if animal evidence is used, animal ID, intervention, every imaging time,
   attrition reason and registered terminal SEM/histology.

The first authorized action would still be a method-free audit of event counts,
missingness, patient grouping, measurement stability and target-time validity.
Only an observed, reproducible failure may motivate a minimal model. A release
or association alone does not authorize architecture or GPU work.

## 6. Authorization boundary

Schema 10.7 and the current aSAH primary batch remain unchanged. Active lead,
primary problem, P0/P1, method, architecture, scientific-server query, PBS/GPU,
outer test, result row, C21 and paper claim remain zero. Historical no-verdict
jobs are not repaired or rerun.

Any future gate-authorized execution uses `introai9` PBS only and never a
login-node GPU. Never access, query, transfer to, submit to or monitor
`junjinyong`.
