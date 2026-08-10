# 2026-08-10 Reconstruction and annotation reliability source audit

## Decision

This is a fresh problem-level source audit. It is not a repair of the closed
Aneumo generation-lineage P0, the failed Open-CTA parser, or the historical GNN
surrogate. Before comparing candidates, the admission rule was frozen at eight
0--5 axes and 32/40: biomedical importance, target identifiability, residual
novelty after direct prior work, usable asset readiness, effective independent
unit, strong-baseline feasibility, interpretable-figure value, and ISBI-schedule
feasibility.

All six candidates remain below admission. The best, **one-sided outer-
annotation morphometry sets**, scores **31.5/40**. Active shortlist, selected
primary problem, method, architecture, executable P0, PBS/GPU training, outer
test, submission identity and paper claim therefore remain **zero**. No patient
DICOM/NIfTI, voxel mask, surface mesh, projection sequence, CFD field or phantom
image payload was read. Scores are not repaired after the asset and direct-prior
audit.

| Rank | Frozen candidate | Importance | Identifiability | Residual gap | Asset | Independent unit | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | One-sided outer-annotation morphometry sets | 4.5 | 4.0 | 1.5 | 3.5 | 5.0 | 5.0 | 5.0 | 3.0 | **31.5** | reject |
| 2 | Sparse-view DSA neck-risk reconstruction | 5.0 | 4.5 | 0.5 | 1.5 | 5.0 | 5.0 | 5.0 | 3.0 | **29.5** | reject |
| 3 | Software/threshold-orbit calibrated morphometry | 4.5 | 3.0 | 2.0 | 1.5 | 5.0 | 5.0 | 5.0 | 3.0 | **29.0** | reject |
| 4 | Dose/reconstruction phantom consistency | 4.0 | 5.0 | 1.0 | 2.0 | 0.5 | 5.0 | 5.0 | 4.0 | **26.5** | reject |
| 5 | Biplane shape posterior for neck and lobulation | 4.0 | 3.0 | 0.5 | 1.0 | 4.0 | 5.0 | 5.0 | 3.0 | **25.5** | reject |
| 6 | Reconstruction-induced hemodynamic-risk propagation | 5.0 | 2.0 | 1.0 | 1.5 | 3.0 | 5.0 | 5.0 | 3.0 | **25.5** | reject |

The total is the arithmetic sum of the displayed cells. “Reject” means reject
this exact candidate version before patient payload or compute; it does not mean
that the source study or dataset is poor.

## Why reconstruction reliability was screened

The team discussion correctly emphasized that segmentation, inlet handling and
rollout stability can dominate a hemodynamic surrogate. The stronger research
question is therefore not whether attention, masking or a GNN can improve an
old pipeline. It is whether an observable acquisition or annotation process
induces a *known set of admissible anatomical truths*, and whether clinically
meaningful geometry or flow functionals can be certified over that set.

That framing would be useful only if the coarsening mechanism, reference target
and independent patient unit are all observable. Otherwise an elegant set-
valued loss merely converts missing labels into an unverifiable uncertainty
claim. The audit below tests that boundary before naming a model.

## Candidate · One-sided outer-annotation morphometry sets · 31.5/40

The open TOF-MRA lineage is unusually attractive. Di Noto et al. report 284
subjects--157 patients and 127 controls--with 198 aneurysms. Their oversized
spherical annotations were four times faster to create than voxel-wise masks,
and data, code and weights were released under permissive licenses. A sphere is
not a noisy mask: it is intended as an outer localization set. A principled
candidate would train predictions whose support is compatible with that outer
set and return intervals for volume, neck, height and surface irregularity,
rather than pretending every sphere voxel is aneurysm.

This residual idea is not yet an admitted method. The 2025 VP-UNet direct prior
already combines soft vesselness guidance, joint detection and segmentation,
246 coarse-label subjects, a 38-subject refined-label test set and external ADAM
evaluation. FocalSegNet is another direct aneurysm-specific weak-label baseline.
More broadly, CVPR 2026 WeakMed removes box-shaped bias with differentiable
Mask-to-Box supervision and scale consistency across nine tasks, nine datasets
and six modalities. Generic partial-label likelihood, consistency, conformal
segmentation or a U-Net/Transformer backbone is therefore not independent
novelty.

Most importantly, the development cohort does not expose a prospective
patient-level annotation study in which the exact radiologist-created sphere
and an independently adjudicated precise mask are paired for the same cases.
The refined 38-subject set can evaluate final segmentation, and precise labels
can be algorithmically coarsened for a synthetic control, but that does not
identify how real weak annotators choose centers and radii. The candidate may
become admissible if a public same-subject annotation-orbit manifest or a small
prospectively frozen paired annotation study is available. It is not repaired
to 32 on the strength of architectural ornament.

## Candidate · Sparse-view DSA neck-risk reconstruction · 29.5/40

The multicenter ultra-sparse DSA study contains 202 patient datasets and
reconstructs from 4, 6, 8, 10 and 12 projections against a roughly 133-view
reference. It reports identification of all 82 analyzed aneurysms at eight
views and publishes analysis code. This supplies a clear acquisition orbit and
an interpretable view-count curve.

It also directly occupies self-supervised sparse-view 3D DSA reconstruction and
aneurysm analysis. Raw patient projection data are private/available on request,
so a public casewise neck, lobulation or calibrated surface target is absent.
AutoCAR further establishes pose adaptation, sparse backprojection and vascular
graph optimization for two-view dynamic coronary reconstruction, using imaging
parameter statistics from more than 1,000 clinical cases. Adapting the same
ingredients to cerebral vessels without a new observable endpoint is domain
transfer, not an ISBI contribution.

## Candidate · Software/threshold-orbit calibrated morphometry · 29.0/40

The 2026 systematic study reconstructs 600 models from 100 patient DSA datasets:
Mimics and 3D Slicer crossed with thresholds 1000, 1500 and 2500. Slicer models
are systematically smaller, lowering the threshold increases some dimensions
by as much as 15.9%, and the least experienced user's aneurysm-size measurement
differs by 22.7% from the reference user. This is strong evidence that a single
segmentation is not an absolute anatomical truth.

The paper itself already quantifies software, threshold and user variability.
Its patient DSA and 600 reconstructed models are available from the authors on
request rather than as a public paired asset. The public article and
supplementary document contain methods and illustrations, not a reusable
per-case orbit manifest, mesh set or independent physical/histologic truth.
Without an absolute reference, an orbit-invariant network could suppress real
small-vessel structure as easily as software artifact. Calibration to one
arbitrary software/threshold cannot resolve that target ambiguity.

## Candidate · Dose/reconstruction phantom consistency · 26.5/40

The PhantomX catalog describes 39,000 axial images, 120 series, 30 dose levels
from 0.1 to 10.5 mGy and four reconstruction methods--FBP, AIDR 3D, FIRST and
AiCE. This is a clean acquisition/reconstruction factorial design. However, it
contains three aneurysms in one effective phantom anatomy and is a catalog
product rather than an open confirmatory patient cohort. A published phantom
study has already measured commercial AI and five neuroradiologists across
dose/reconstruction settings. It is a useful QA or stress-test control, not an
independent clinical method identity.

## Candidate · Biplane shape posterior for neck and lobulation · 25.5/40

The ISUIA work already reconstructs aneurysm sac surfaces from two silhouettes
by curve morphing and reports morphometry for 150 aneurysms. Ten pre-existing 3D
models provide a simulation validation set, while the neck is unidentifiable in
23 of 150 clinical aneurysms. The paper explicitly states that biplane surfaces
remain approximations and can sharpen daughter sacs or distort the neck plane.

Those facts motivate uncertainty, but they also expose the missing target. The
legacy patient angiograms and 3D reconstructions are not a public development
asset, and neuroradiologist measurements are a consistency comparison rather
than absolute 3D truth. A diffusion posterior or neural renderer cannot be
validated merely by reproducing the two input silhouettes.

## Candidate · Reconstruction-induced hemodynamic-risk propagation · 25.5/40

A tempting extension is to pass each software/threshold/annotation realization
through CFD and certify the spread of WSS, OSI or a downstream rupture-status
score. This would be meaningful only with a public same-patient reconstruction
orbit, fully specified boundary conditions, paired fields and an independent
physical or clinical endpoint. None is jointly released by the audited sources.

Earlier MATCH-style multi-group segmentation variability, segmentation-to-WSS
studies, generic ensemble UQ and multi-fidelity neural operators are direct
controls. Synthetic CFD can measure numerical sensitivity but cannot determine
which reconstruction is anatomically correct or whether a derived risk score is
clinically calibrated. This version is therefore target-unidentified.

## Consequence for architecture and experiments

There is no current GNN, U-Net, Transformer, diffusion model, neural operator or
multimodal architecture. The source audit leaves a precise conditional path:

1. Obtain a public or explicitly authorized *same-subject* annotation/reconstruction
   orbit with an independently adjudicated reference, or a prospective paired
   annotation study whose selection rule is frozen before labels are read.
2. Register a method-free CPU/read-only P0 that checks patient grouping, exact
   orbit membership, coordinate frames, label containment, reference
   independence, licenses and effective units.
3. Only a passing P0 may open a method-free task-adequacy P1. Architecture and
   GPU remain forbidden until the task shows nontrivial uncertainty and strong
   direct baselines leave a measurable residual gap.

Since 31.5 is below 32, no `introai9` connection, scheduler query, P0 or GPU job
is needed for this cycle. This is a normal source-gate early stop, not a server
failure. The closed Aneumo P0 and every earlier failed/invalid branch remain
unchanged. Future execution is PBS-only on `introai9` after prospective
authorization. `junjinyong` remains excluded from connection, query, submission
and monitoring.
