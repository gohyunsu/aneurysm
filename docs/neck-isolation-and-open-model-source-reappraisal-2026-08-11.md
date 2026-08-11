# Neck isolation, workflow orbits and open-model source reappraisal

**Frozen on:** 2026-08-11  
**State:** all six candidates rejected; active lead, P0/P1, method, architecture,
scientific-server query and GPU job are zero  
**Question:** do newly public neck/isolation assets make an identifiable and
independently novel ISBI 2027 problem, including a viable re-entry path for the
inactive surface-vector hypothesis?

## Decision

No. AneuSI is a substantial new executable baseline and data inventory, but it
does not infer an aneurysm neck: it requires a surface, centerlines and a neck
polygon, then deterministically chooses a retained parent-vessel length using
`clipFactor`. NeckSpline already owns differentiable continuous neck-curve
prediction in CTA/MRA. A recent 1,024-run study already owns broad aneurysm-CFD
workflow variability. The updated open nnU-Net owns multicentre TOF-MRA
detection/segmentation, while TAR owns topology-aware semi-supervised aneurysm
and vessel segmentation. Combining these components, adding uncertainty, or
renaming a neck-conditioned GNN does not create residual novelty.

The strongest executable formulation is a seven-level `clipFactor` morphometry
stability audit. It scores **31.5/40** and fails the mandatory residual-novelty
floor at **0.5/5**. All six rows are frozen and rejected. No payload body was
opened, no P0 was registered, and no scientific server was queried.

## 1. What the public assets actually contain

### AneuSI is an isolation tool, not an automatic neck detector

The official AneuSI repository is public at exact head
`5b4c454ede46c4cd56d3831cb24748c7e1521eca`. The code repository reports an MIT
license, while its bundled Aneurisk data license states CC BY-NC 3.0. The Git
tree is complete (`truncated=false`) and contains 1,041 blobs totaling
977,740,269 bytes, including eight source files, 103 model files, 103
centerline files, 103 neck files and 716 analysis files. Repository metadata,
README and the small license text were inspected; VTK and ODS payload bodies
were not opened. There is no GitHub release.

The apparent count needs two corrections.

- The 103 model filenames reduce to **99 visible base IDs** after removing the
  `a`/`b` suffix used for multiple lesions. Four model pairs and four centerline
  pairs are byte-identical Git blobs. A lesion-specific neck does not make its
  shared parent anatomy a new patient.
- The analysis directory contains exactly 102 derived VTK files at each of
  seven `clipFactor` values, 20/25/30/35/40/45/50, plus two spreadsheets. These
  714 deterministic views are repeated transformations, not 714 independent
  anatomies.

AneuSI uses the supplied neck as a spatial reference and is explicitly tied to
AneuriskWeb centerline conventions. Cross-dataset generalization therefore
requires adapting the input and reference logic; it is not established by the
release. [Official repository](https://github.com/grupomoccai/AneuSI) ·
[Paper DOI](https://doi.org/10.1016/j.cmpb.2026.109525)

### NeckSpline removes the obvious automatic-neck gap

NeckSpline directly predicts a continuous periodic cubic B-spline neck curve
from volumetric angiography with centerline guidance and curve regularization.
It evaluates CTA and MRA and reports width/angle measurements. The original
datasets did not supply closed neck loops; the study generated candidate loops
and used reader review and adjudication. Those study annotations are not
identified as a versioned public training asset in the inspected source.

The stated anonymous code URL currently redirects to its repository API and
returns HTTP 401. A paper code-availability sentence is therefore not treated
as currently executable code, and no code or annotation payload was accessed.
[Paper DOI](https://doi.org/10.1038/s41746-026-02613-6)

### The open model is real, but not a clean external cohort

Zenodo record `17894703`, revision 4, publishes v2 of the multicentre TOF-MRA
nnU-Net as one open CC BY-NC 4.0 file:
`Dataset615_MAXIMUS.zip`, 1,167,744,043 bytes, MD5
`3b38956f084d1570c00c47b232d6269d`. The record reports training on 1,094
positive scans from RSNA, Royal Brisbane, Lausanne, ADAM and Basel. It is a
model artifact, not 1,094 new AURORA patients, and Lausanne/ADAM cannot be
called unseen external cohorts for that v2 model. The archive was not
downloaded. [Official record](https://zenodo.org/records/17894703) ·
[Paper DOI](https://doi.org/10.1007/s10278-025-01533-3)

### Direct priors leave no architecture-shaped novelty

- A 2025 workflow study varies reconstruction, segmentation, smoothing,
  rheology, inlet/outlet boundary conditions and ostium/parent definition over
  1,024 transient simulations. Its four anatomies limit confirmation, but the
  generic workflow-orbit question is already explicit.
  [Paper DOI](https://doi.org/10.1016/j.compbiomed.2025.110018)
- TAR's exact public head is
  `5e852dd919feb98406067a8034dd744ddb78877f`; the complete 4,495,522-byte tree
  contains training/evaluation code and one weight-like file, but has no
  recognized repository license. It remains a strong topology-aware
  segmentation control, not a reusable licensed asset by assumption.
  [Official repository](https://github.com/AbsoluteResonance/TAR)
- Selective prediction, conformal shape/landmark regions and topology-aware
  uncertainty already occupy generic uncertainty wrappers. They cannot repair
  a missing expert-loop contract or an already occupied application question.

## 2. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at
least 32 plus the schema-8.8 critical minima; scores are not repaired after
ordering.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| `clipFactor`-orbit morphometry stability audit | 3.5 / 4.5 / **0.5** / 5.0 / 3.0 / 5.0 / 5.0 / 5.0 | **31.5** | Reject: total and novelty floor fail; the release already exposes the deterministic orbit |
| Neck-conditioned ROI isolation transfer | 4.0 / 3.5 / **0.5** / 4.5 / 3.0 / 5.0 / 5.0 / 4.5 | **30.0** | Reject: AneuSI owns the operation and cross-source adaptation is engineering, not a residual scientific gap |
| Automatic surface neck-loop transfer | 4.5 / **3.0** / **1.0** / 4.0 / 3.0 / 4.5 / 5.0 / 4.0 | **29.0** | Reject: NeckSpline is direct prior and expert-loop provenance/variability is unavailable |
| Differential-diagnosis set calibration of the open model | 4.5 / **2.5** / **0.5** / 4.0 / **2.0** / 5.0 / 5.0 / 4.5 | **28.0** | Reject: fixed-model study already analyzes differential diagnoses; reference-linked error labels are private |
| Neck uncertainty to hemodynamic-functional certificate | 4.5 / **2.0** / **1.5** / **2.0** / 3.0 / 3.5 / 5.0 / 2.5 | **24.0** | Reject: no paired expert-neck distribution and CFD functional asset |
| Workflow-orbit structure-faithful WSS surrogate | 4.5 / **3.0** / **1.0** / **1.5** / **1.0** / 4.0 / 5.0 / 2.5 | **22.5** | Reject: four-anatomy prior is insufficient as a development cohort and the broad workflow question is occupied |

## 3. Consequence for the supplied surface-vector proposal

The supplied scientific sequence remains correct as a **future gate order**:
task stability, field-error-matched baseline failure, bounded family-disjoint
development, fresh confirmation and external interpretation. It is not a
current experiment plan. AneuSI supplies neck-conditioned geometric variants,
not transient WSS, robust critical-point truth, a matched surrogate, or an
independent confirmatory cohort. It therefore does not constitute the required
material evidence version for reactivating surface-vector work.

Edge 1-forms, Hodge/DEC, SE(3) message passing, periodic decoding, tangency and
structural losses remain possible controls only. Exact critical points and
worldlines remain secondary evaluation objects until a method-free stability
source passes a prospectively registered gate. Job `115645.ECE-util1` remains
execution-incomplete/no scientific verdict and is not repaired or rerun.

## 4. Operational boundary

- Active lead, primary problem, P0/P1, method, architecture, result row, outer
  test, paper contribution and submission identity remain zero.
- No scientific server was queried, no transfer occurred and no PBS/GPU job was
  created for this audit.
- Future gate-authorized execution may use only `introai9` through PBS. A GPU
  command on a login node is forbidden. `junjinyong` must never be accessed,
  queried, transferred to, submitted to or monitored.
- Re-entry requires a versioned asset that supplies expert neck/ROI provenance
  and a patient- or base-family-grouped downstream target not already occupied
  by NeckSpline, AneuSI or generic workflow-variability analysis. A code release
  or architecture rename alone does not qualify.
