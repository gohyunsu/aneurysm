# Diagnostic action and human--AI source reappraisal · 2026-08-12

## Decision

This audit asks whether AURORA should leave the inactive surface-vector question
for a clinically closer paper on diagnostic mimics, human--AI interaction,
treatment choice, contrast retention, biplane DSA or CFD-applicability-aware
segmentation. It should not. Six formulations were frozen together under the
unchanged eight-axis, non-compensatory source gate. They score
**29.5/27.0/26.0/26.0/25.0/24.5** and all are rejected.

The closest row, `cfd_applicability_certified_segmentation_on_iavs`, has an
additive score of 29.5/40 and residual novelty 0.5/5. The IAVS paper already
defines the downstream CFD-applicability problem, supplies a two-stage baseline
and evaluates topology-aware regularization. Its stated public repository is
still exactly one README without a license or dataset/code payload. Neither a
new loss nor the prospect of a later release identifies an independent AURORA
contribution today.

No active lead, primary problem, P0/P1, method, architecture, data terms,
patient payload, scientific-server query, PBS/GPU job, outer test, result row or
paper claim is opened. Patient-level all-lesion reliability and automation-bias
risk remain evaluation considerations only. Surface-vector remains an inactive
conditional hypothesis rather than a fallback model.

## Exact source facts

### Aneurysm mimics and automation bias

The 2025 multireader study
[Automation bias in AI-assisted detection of cerebral aneurysms](https://doi.org/10.1007/s11547-025-01964-6)
used 20 TOF-MRA examinations and nine radiologists. Each case was read with and
without commercial AI after a washout; ten cases contained at least one false
AI mark. False-positive AI increased aneurysm suspicion (`p=0.01`) and caused
inexperienced readers to recommend more intensive follow-up (`p=0.005`). The
ten false marks were five vascular loops, three infundibula and two
perforators. This establishes the harm mechanism; AURORA did not reproduce the
reader study or its statistics.

In the small [7-T MRA study](https://doi.org/10.1016/j.mri.2016.11.006), six
patients with 0.9--2.0 mm equivocal lesions underwent higher-resolution imaging
and five were clarified as infundibula. The clinically relevant estimand is
whether an apparent outpouching is a true aneurysm and whether another
acquisition is warranted, not segmentation Dice alone.

The open multicentre TOF-MRA model
[`arXiv:2408.17115`](https://arxiv.org/abs/2408.17115) is a strong baseline. It
reports 385 scans from 364 patients plus 113 ADAM cases, explicitly includes
aneurysm-like differential diagnoses, and releases model weights. The source
does not provide a versioned public patient-level release of the 364-patient
differential-diagnosis cohort. OpenNeuro `ds005096` contains aneurysms but no
reference set of loops, infundibula and perforators matched to the reader-study
categories. Generic complementarity-driven deferral and selective clinical AI
are also direct priors. A confidence threshold, reject head, second-reader
display or extra-acquisition policy is a baseline family, not novelty.

### CFD applicability is already the IAVS task

[IAVS](https://openreview.net/forum?id=2kGGR5KbWE) reports 641 multicentre 3D
MRA volumes, 587 aneurysm/parent-vessel annotations, centerlines, meshes and CFD
outcomes. It explicitly reframes segmentation around downstream CFD
applicability and supplies global localization plus fine segmentation
benchmarks. The related
[topology-aware regularization paper](https://openreview.net/forum?id=OseTyrIvKR)
directly targets vessel adhesion and surface errors that invalidate CFD.

Authenticated read-only GitHub inspection on 2026-08-12 found exact official
repository head `2e40088d9eaa671c592929a154b7b2cf99f9320a`, dated
2025-12-06. Its complete tree contains only `README.md`; repository license is
null. No image, mask, mesh, CFD result, split, code or checkpoint is publicly
executable from that repository. A promised future release is not a current
asset and cannot authorize a model.

### Contrast retention already links a functional to instability

The 2026 study
[Investigation of Contrast Retention in PCOM Aneurysms](https://doi.org/10.1002/cnm.70184)
constructs CFD-based virtual angiograms and time-density curves. Its
cross-sectional subset has 271 PCOM aneurysms (129 unruptured, 142 ruptured),
and its longitudinal subset has 41 aneurysms: 23 stable, 13 enlarged and five
with new cranial-nerve III palsy. The authors already define parent-artery-
normalized contrast-retention functionals and report associations with
instability and rupture, including examples with WSS critical points.

This directly occupies “replace WSS error with clinically interpretable
washout error.” No versioned public patient geometry/CFD/contrast/outcome bundle
or sealed split was identified in the official article record. A neural
operator for contrast transport would add a model before an independently
testable target exists.

### Treatment-risk prediction does not identify a treatment policy

The 2026 [MARTA score](https://doi.org/10.1227/neu.0000000000003900) uses
2,647 treated patients across 15 centres: 1,907 endovascular and 740
neurosurgical. Reported procedural complication rates are 6.3% and 12.8%, with
moderate external discrimination (AUROC 0.68 and 0.65). A public calculator
exposes the score, but no versioned patient-row dataset joined to images is
identified.

Observed outcomes under chosen treatments do not identify the unobserved
outcome under the alternative treatment. Adding CTA/MRA embeddings to MARTA or
training separate treatment heads would not recover this counterfactual. The
open flow-diverter record also lacks a paired 3D imaging contract.

### Real biplane DSA remains unavailable

The MIDL 2026 cross-view paper already proposes cross-view-consistent aneurysm
detection. Its inspected 113 pairs are deterministic AP/lateral MIPs rendered
from ADAM 3D MRA rather than acquired biplane DSA, and inference uses one view.
Clinical DSA sources do not provide a public paired AP/lateral aneurysm
reference and calibration contract. Projective fusion, correspondence,
triangulation and selective 2D/3D localization are direct priors.

## Frozen non-compensatory screen

Axes are ordered as biomedical importance, target identifiability, residual
novelty, asset readiness, effective independent unit, strong-baseline
feasibility, interpretable-evidence value and ISBI schedule fit. Every axis is
0--5. Admission requires total >=32 and, independently, novelty >=2.5,
identifiability >=3.5, asset >=3.0, unit >=3.0 and baseline >=3.0.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CFD-applicability-certified segmentation on IAVS | 5.0 | 5.0 | 0.5 | 1.0 | 5.0 | 5.0 | 5.0 | 3.0 | **29.5** | reject: task occupied; release README-only |
| Contrast-retention instability functional surrogate | 5.0 | 4.5 | 1.0 | 1.0 | 3.0 | 5.0 | 5.0 | 2.5 | **27.0** | reject: functional occupied; matched public bundle absent |
| Mimic-aware selective diagnosis with acquisition escalation | 5.0 | 4.0 | 2.0 | 1.0 | 1.5 | 5.0 | 5.0 | 2.5 | **26.0** | reject: paired mimic/reference asset absent |
| Real-biplane DSA cross-view lesion-set localization | 5.0 | 4.0 | 0.5 | 1.0 | 3.0 | 5.0 | 5.0 | 2.5 | **26.0** | reject: direct prior; no public acquired pair contract |
| Imaging-augmented treatment-specific MARTA risk | 5.0 | 2.0 | 0.5 | 1.0 | 5.0 | 5.0 | 4.5 | 2.0 | **25.0** | reject: counterfactual and joined image asset absent |
| Automation-bias-aware evidence display policy | 5.0 | 3.5 | 1.5 | 1.0 | 1.5 | 5.0 | 5.0 | 2.0 | **24.5** | reject: direct human-AI prior; no development reader asset |

The arithmetic is frozen exactly as displayed. No operational readiness,
clinical importance or attractive visualization may compensate for a failed
critical floor. No row is rescored after direct-prior inspection.

## What remains scientifically useful

Three ideas are retained only as future evaluation requirements:

1. report false outputs by aneurysm, infundibulum, vascular loop and perforator
   when a reference taxonomy is actually available;
2. evaluate patient-level recommendations or acquisition escalation, not only
   confidence and Dice; and
3. for any future segmentation paper, measure CFD conversion/applicability
   against the released IAVS baselines once a lawful versioned asset exists.

These are not numbered contributions or selected endpoints now. A future
candidate must bring a material patient-level contract that identifies one of
these actions and still pass a fresh direct-prior screen.

## Operational observations and boundary

The exact TopAneu official head remains
`018c243445f99199f484018c4c80575c84c72293`; authenticated read-only inspection
found no release change after 2026-08-03. A full 15-source watch refresh was
attempted once but did not complete because the unauthenticated GitHub API hit
HTTP 403 rate limiting. This is an observation failure, not a source change,
asset failure or trigger to update frozen snapshots. A separate Aneumo metadata
request was terminated after prolonged response delay and produced no source
verdict. Neither request accessed scientific payload.

No scientific server was queried, no data were transferred and no PBS/GPU job
was created. Future gate-authorized execution remains `introai9` PBS only;
login-node GPU commands are prohibited. `junjinyong` remains prohibited for
connection, query, transfer, submission and monitoring.
