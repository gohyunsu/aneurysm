# Broad-registry source audit · 2026-08-10

## Decision

The previous exact-title search was deliberately narrow. This audit broadens the
source boundary before inventing another architecture: official Zenodo,
DataCite, Figshare and Dryad metadata were screened, then the strongest records
were checked against their primary papers and direct methods. No patient file,
image, mesh, spreadsheet, document supplement or model archive was downloaded
or opened.

The eight frozen 0--5 axes remain unchanged: biomedical importance, target
identifiability, residual novelty, usable asset readiness, effective independent
unit, strong-baseline feasibility, interpretable-figure value and ISBI-schedule
feasibility. The admission line remains **32/40**.

| Candidate | Importance | Identifiability | Residual gap | Asset | Independent unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Multicenter study-level lesion-set risk control | 5.0 | 4.5 | 1.0 | 2.0 | 5.0 | 5.0 | 5.0 | 3.0 | **30.5** | reject |
| Solver-population-calibrated hemodynamic functionals | 4.5 | 3.5 | 1.0 | 5.0 | 1.5 | 5.0 | 5.0 | 4.0 | **29.5** | reject |
| Rupture-destined longitudinal SIG forecasting | 5.0 | 4.5 | 1.0 | 1.0 | 3.0 | 5.0 | 3.0 | 3.5 | **26.0** | reject |
| aSAH day-21 hydrocephalus dynamic imaging | 4.5 | 4.5 | 0.0 | 1.0 | 4.5 | 5.0 | 2.5 | 4.0 | **26.0** | reject |
| VWI habitat instability reanalysis | 4.5 | 3.0 | 0.0 | 1.0 | 4.5 | 5.0 | 3.0 | 3.5 | **24.5** | reject |
| Synthetic-DSA reader realism | 3.5 | 2.0 | 0.0 | 0.5 | 1.0 | 5.0 | 5.0 | 1.0 | **18.0** | reject |

Every total is the arithmetic sum of the displayed cells. The maximum is
**30.5/40**, so active shortlist, selected primary problem, executable P0,
method, architecture, PBS/GPU work, outer test, submission identity and paper
claim all remain **zero**. This is a normal source-gate stop, not a server
failure. It does not authorize rescoring or combining unrelated records to
manufacture an independent cohort.

## Search and access boundary

The bounded metadata screen covered:

- the first 100 recent records from a broad Zenodo `aneurysm` query, whose API
  reported 1,226 records;
- a DataCite `intracranial aneurysm` dataset query, which reported 196 records;
- the first 100 Figshare search results and approximately 20 Dryad search
  results; and
- the prior 49-record exact-title Zenodo query as a historical cross-check.

This is not a claim that every returned record is scientifically relevant or
that all 1,226 Zenodo objects were read. Titles, descriptions, access state,
licenses, related identifiers and file manifests were used to remove papers,
isolated figures, tiny demonstrations, duplicates and records already audited.
Only the six strongest previously unregistered candidate versions were scored.

The IAVS watch also remains unchanged at exact upstream
`2e40088d9eaa671c592929a154b7b2cf99f9320a`: one README, zero releases, no
explicit repository license and no payload/code. Two bounded name-level source
checks on `introai9` did not produce a result artifact; they therefore establish
neither presence nor absence and are not repeated. A minimal public-key login
did succeed, and the previously completed PBS query showed zero AURORA jobs. No
login-node GPU command ran. `junjinyong` was not accessed and is excluded from
connection, query, transfer, submission and monitoring.

## 1. Multicenter study-level lesion-set risk control · 30.5/40

The official [LargeIA Zenodo record](https://doi.org/10.5281/zenodo.6801398)
reports 1,338 internal 3D CTA studies with 1,489 aneurysms from six institutions
and 138 external CTA studies with 101 aneurysms from two institutions. It states
that voxelwise aneurysm masks, age, sex and presentation rupture status are
available. This is a much stronger independent-unit and multicenter boundary
than the public test-only records in the preceding audit.

It is not, however, an executable public asset. Files are restricted and an
access request requires a person's name, institutional email, department,
mentor and project. No account was created, no terms were accepted and no
request was submitted on the user's behalf. The record's 2025 modification date
does not establish a new public version, case manifest, reader provenance or
sealed development/test contract.

The linked Patterns paper already introduces GLIA-Net, a global-local 3D
localization and fine segmentation pipeline on this cohort. Later LargeIA and
RSNA-era systems directly occupy anatomy-aware detection, global-local patches,
centerline/graph context and lesion segmentation. Generic conformal risk
control, sequential conformal object detection and conformal instance-set
coverage also occupy the obvious certification wrapper.

A residual problem could be clinically meaningful only if the restricted asset
can prospectively support study-level sensitivity under a bounded false-positive
or miss-risk loss, preserve multi-lesion patient grouping, expose independent
reader/adjudication semantics and retain a sealed center-level outer test. Those
facts are not publicly auditable now. Restricted scale plus a conformal name is
therefore insufficient for admission.

## 2. Solver-population-calibrated hemodynamic functionals · 29.5/40

Figshare record [`6383516`](https://figshare.com/articles/dataset/6383516)
describes the 2015 International Aneurysm CFD Challenge: five MCA aneurysm DICOM
volumes and 28 submitted solution sets from 26 teams. Its public manifest lists
the raw spreadsheet, DICOMs, WSS surfaces, segmentations and large velocity
archives. No one of these payload files was opened in this audit.

The [primary challenge paper](https://doi.org/10.1007/s13239-018-00374-2)
already defines whole-pipeline uncertainty. It reports sac-average WSS
interquartile ranges as high as 56%, reduced below 30% after parent-artery
normalization, and analyzes variation in segmentation, model extent, inflow,
blood properties and CFD choices. MATCH subsequently isolates segmentation-
induced hemodynamic variability on five aneurysms. The VISC PIV record adds one
experimental plane from one anatomy rather than a broad independent validation
cohort.

Treating 28 solver submissions as 28 patients would be pseudoreplication. A
hierarchical operator could model solver-to-solver distributions, but the source
paper already owns workflow-level uncertainty and only five independent
anatomies identify cross-geometry behavior. Generic ensemble, Bayesian neural
operator, multi-fidelity and conformal-functional calibration are direct
controls. The archive is valuable for benchmarking numerical variation, not a
standalone new ISBI learning identity.

## 3. Rupture-destined longitudinal SIG forecasting · 26.0/40

Figshare records `23905128`, `23905134` and `23905143` expose the same
293,305-byte supplementary PDF for the paper
[`10.1159/000533167`](https://doi.org/10.1159/000533167). The study compares 20
rupture-destined aneurysms from 20 patients with 45 unruptured aneurysms from 41
patients under serial TOF-MRA and directly analyzes geometric, hemodynamic and
signal-intensity-gradient change. It reports delta-SIG ratio AUC 0.72 versus
size-ratio AUC 0.56.

This is one of the rare truly longitudinal rupture endpoints, but the public
objects are duplicate supplement PDFs, not casewise serial MRA, surfaces,
segmentations or a machine-readable measurement table. The primary paper already
performs the proposed SIG/geometric/hemodynamic analysis. Without images or an
independent development split, a fancy temporal GNN or survival head has neither
a trainable input nor residual algorithmic novelty.

## 4. aSAH day-21 hydrocephalus dynamic imaging · 26.0/40

Figshare record `33077267` and its related tables accompany
[`10.3389/fneur.2026.1837898`](https://doi.org/10.3389/fneur.2026.1837898). The
paper reports 228 development and 102 external patients and a day-21 shunt-
dependent hydrocephalus endpoint. The random-forest model, including dynamic
clinical features, reports development/external AUC 0.894/0.867.

The public record consists of supplementary documents and aggregate tables; no
patient-level longitudinal images, scan-time series or executable feature
matrix was identified. The paper already owns the prediction problem and strong
external result. Replacing the classifier with a Transformer would not create
independent novelty, and a predominantly clinical postoperative endpoint is a
poor fit to a four-page aneurysm-imaging submission without image-linked data.

## 5. VWI habitat instability reanalysis · 24.5/40

Figshare record [`32695140`](https://figshare.com/articles/dataset/32695140)
contains a 1,747,210-byte article supplement and related record `32695074`
contains a 14,565-byte table. The linked study reports 293 patients with 312
unruptured aneurysms, divided into 197 stable and 115 unstable lesions, and
already combines VWI radiomics habitat, deep features and clinical variables
with a Transformer. Reported validation AUC is 0.844.

No raw vessel-wall MRI, segmentation, habitat map or patient-level manifest was
identified in the public record. The exact multimodal method and endpoint are
already the direct paper contribution. Reanalysis of a small summary table
cannot support an imaging architecture, attribution map or external stress
test.

## 6. Synthetic-DSA reader realism · 18.0/40

Zenodo record [`21104782`](https://zenodo.org/records/21104782) describes 400
synthetic cerebral DSA images: ten runs, four projections and ten images per
projection. The record is embargoed until **2026-10-31**, after the ISBI 2027
paper deadline of 2026-10-26. It reports no original patient DSA and no public
file access at the audit date. The linked preprint directly frames the asset as
a diffusion-synthesis and reader-study problem.

Repeated generated views are not 400 independent patients. With one generator
lineage, no real paired source and no pre-deadline access, realism scoring or a
new diffusion model cannot yield a defensible medical-imaging contribution.

## Direct-prior red team

The attractive combinations do not survive a method-level novelty check:

- “multicenter detector + conformal guarantee” is bounded by GLIA-Net and later
  anatomy-aware detectors on the data side, and by conformal risk control,
  sequential conformal object detection and conformal instance segmentation on
  the method side;
- “learn the CFD solver population” is bounded by the original 2015 whole-
  pipeline variability analysis, MATCH, and generic probabilistic/multi-fidelity
  neural-operator uncertainty;
- “forecast rupture from serial SIG” and “predict VWI instability” are the
  linked primary papers' own endpoints and analyses;
- low-quality CTA restoration is also directly occupied by Zenodo software
  record [`20754346`](https://zenodo.org/records/20754346), whose description is
  physics-grounded synthetic supervision for controlled CT restoration; and
- adding a GNN, Transformer, diffusion decoder, uncertainty head or memorable
  acronym to any one of these does not repair access, independent units or
  residual novelty.

## Consequence and next action

The most credible lead is LargeIA because its reported patient/center scale is
substantial. It is still rejected in this exact version: access is restricted,
the user has not authorized a personal request, public reader/outer-test
semantics are insufficient, and direct detection plus conformal priors leave
only a narrow residual gap. The score is frozen at 30.5 rather than rounded or
combined with RSNA/TopCoW to cross 32.

No current architecture exists. The next allowed action is a material source
change that independently provides an observable endpoint, auditable
development units, a sealed outer test and a residual algorithmic gap. Only a
fresh candidate at or above 32/40 may open a separately frozen method-free,
CPU/read-only P0 on `introai9` PBS. P0 success would still not authorize a model
or GPU. `junjinyong` remains completely outside AURORA.
