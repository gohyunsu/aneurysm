# Team downstream-utility and model-form reappraisal

> **Frozen decision · schema 8.4 · 2026-08-11 KST:** the most recent team
> discussion still asks whether a learned aneurysm-flow surrogate preserves
> the downstream information supplied by CFD. That is a valid evaluation
> question, but none of six formulations is an identifiable, residual paper
> problem with the audited assets. The batch scores
> **27.0/25.5/24.0/24.0/23.5/21.5**, all below the unchanged 32/40 admission
> line. No P0/P1, method, architecture, scientific-server query, PBS/GPU job,
> outer test, result row or paper claim is opened.

## 1. What was and was not new in the team record

The two files in the project `tmp/` directory were re-read as immutable source
material. Their exact SHA-256 values are:

- `kakaotalk`: `ad99ccdcc66fcb57a049e6f2dfaa7ee11dd305779dd49a6e545b9b6b6cab175d`;
- `tistory`: `6d50cb4ae8db683cf2b4f1aa48c402a8765a64d0f19b5c67687912ab660c2b38`.

Neither file contains a discussion later than 2026-08-02. The latest coherent
team question is whether a hemodynamic surrogate retains the incremental
rupture-status signal of real CFD after clinical and morphological features are
included. The associated engineering suggestions are attention, local/global
fusion, multigrid rollout, masking, inlet-aware training and video-style
temporal prediction.

Three parts remain useful:

1. compare `clinical+morphology`, `+real CFD`, and `+surrogate CFD` under one
   patient-grouped contract;
2. separate field error from downstream functional sufficiency;
3. show reference CFD, surrogate fields and downstream consequences in the
   same coordinates when a valid joint cohort exists.

The engineering components are not an independent contribution. Attention,
multigrid, masking, GNN rollout and temporal decoding are architecture choices
whose value must be established after a problem and estimand are identified.

## 2. Existing AURORA evidence does not answer the proposed comparison

The frozen CMHA exploratory result contains 99 patients and 105 lesions. Its
patient-grouped linear comparison reports AUPRC 0.7592 for
`clinical+morphology` and 0.7173 after adding released hemodynamic summaries,
with a patient-bootstrap difference of -0.0419 and 95% interval
[-0.1083, 0.0066]. This is a negative exploratory signal, not a confirmatory
failure and not evidence that hemodynamics are useless. The official case map
is unverified, the table contains no matched surrogate prediction, and the
comparison cannot measure real-CFD-to-surrogate retention.

The July 2026 direct-prior audit already rejected the stronger residual claim
at 23.5/40. A PointNeXt + per-geometry PINN + clinical-fusion pipeline has
already been reported on AneuX. Its fields use shared modeled boundary
conditions and lack paired CFD or in-vivo validation, so they are a
geometry-conditioned feature construction rather than an independently
observed physiological modality. The remaining question—whether physically
validated, patient-condition-aware flow adds information beyond morphology and
clinical variables—still lacks a cohort jointly containing the needed
observations.

Cross-sectional ruptured/unruptured status must not be called future rupture
risk. Rupture can alter geometry, and a classifier can learn post-rupture
consequences. Downstream AUPRC retention would be a model-behavior endpoint,
not a clinical-utility claim.

## 3. New direct-prior and asset evidence

### 3.1 PointFlowNet occupies peak-systolic point-cloud surrogation

The 2026 *Computer Methods and Programs in Biomedicine* paper
[Geometry-aware PointNet for rapid prediction of cerebral aneurysm
hemodynamics](https://doi.org/10.1016/j.cmpb.2026.109308) trains on 984 idealized
middle-cerebral-artery bifurcation aneurysms. It predicts peak-systolic velocity
and WSS from query points augmented with distance to the nearest wall and
reports velocity/WSS NMAE of 4.05%/2.59%. It also reports degradation on
non-idealized out-of-distribution anatomy. These are prior-work results, not
AURORA results.

The linked public
[PointFlowNet repository](https://github.com/yiyingsheng07/PointFlowNet) was
audited at exact head `5cb4f2545d25b6e8b855806cb3a345b8b1d72594` without
executing code or opening a scientific server. The root contains model,
loader, train/test scripts, one 14,120,802-byte checkpoint, two result CSVs and
only a 538-byte normalization-stat file under `dataset/`. The 35-byte README
says only that release is forthcoming. There is no repository license, release,
CFD payload, or tracked `train.txt`, `val.txt`, and `test.txt` split manifest.
The public code therefore establishes a direct architecture/baseline threat,
not a fully executable matched control for AURORA.

The inspected implementation is consistent with the paper's single-input
description: the `mdata` surface argument is not used by the forward path;
geometry reaches the interior queries through the precomputed nearest-wall
distance. This is not itself an error, but it makes an added surface encoder or
GNN a baseline comparison rather than a novelty claim.

### 3.2 Hemo-MPO removes architecture-combination novelty

[Hemo-MPO](https://doi.org/10.1016/j.aej.2026.05.044) already combines an
SE(3)-equivariant mesh encoder, physics-informed constraints and a DeepONet
decoder for velocity, pressure and WSS-related prediction. Its article states
that supporting data are available only on request and does not provide an
audited public split or implementation contract. The paper's use of
“patient-level” language for Aneumo cannot be treated as verified patient
independence because the public Aneumo lineage is synthetic. Hemo-MPO is thus a
strong component prior, not external patient validation and not a runnable
baseline until its provenance can be reconciled.

### 3.3 Public rigid-versus-FSI data have one effective anatomy

The CC0 Dryad record
[Aneurysmal haemodynamics: A three-dimensional fluid–structure interaction
approach](https://doi.org/10.5061/dryad.pc866t22m) provides 289.37 MB of
synthetic fields: one rigid-wall case and two low/high-pulsatility FSI cases,
each on two grids with 55 time samples, plus TAWSS and OSI. Its effective
anatomy count is one. It is useful for solver validation, model-form
illustration and a controlled paired stress test; grid resolutions and time
samples are repeated measurements, not independent units. It cannot train or
confirm a population-level surrogate claim.

### 3.4 Rupture-status overlap is a warning, not a new target

The 2026 preprint
[Hemodynamic Overlap Between Ruptured and Unruptured Cerebral
Aneurysms](https://arxiv.org/abs/2606.00072) studies four ruptured and four
unruptured Aneurisk cases and emphasizes qualitative overlap in velocity, WSS
and TAWSS. It explicitly avoids proposing a rupture-prediction rule. Eight
selected cases without a classifier, prospective outcome, public solver data
or independent external cohort cannot justify a selective rupture-status
method or calibrate clinical abstention.

## 4. Frozen eight-axis screen

The axes remain, in order: biomedical-imaging importance, target
identifiability, residual novelty, usable asset readiness, effective
independent-unit strength, strong-baseline feasibility, interpretable-figure
value and ISBI-schedule fit. Each axis is scored from 0 to 5.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Geometry-only peak-systolic point surrogation | 3.5 | 4.0 | 0.5 | 2.0 | 4.0 | 5.0 | 4.5 | 3.5 | **27.0** | reject: directly occupied |
| Rigid/FSI model-form-robust functional concordance | 4.0 | 2.5 | 1.5 | 3.5 | 0.5 | 4.5 | 5.0 | 4.0 | **25.5** | reject: one anatomy |
| Real-CFD-to-surrogate downstream status retention | 4.5 | 1.0 | 1.5 | 1.5 | 3.5 | 5.0 | 4.5 | 2.5 | **24.0** | reject: joint observation absent |
| Attention/multigrid/masked rollout GNN | 3.0 | 3.0 | 0.5 | 2.0 | 3.0 | 5.0 | 3.5 | 4.0 | **24.0** | reject: architecture-only |
| Patient-condition-validated incremental status utility | 4.5 | 1.5 | 2.0 | 1.0 | 3.0 | 5.0 | 4.5 | 2.0 | **23.5** | preserve prior rejection |
| Hemodynamic-overlap-aware selective status abstention | 4.0 | 1.5 | 1.0 | 1.0 | 2.0 | 5.0 | 4.0 | 3.0 | **21.5** | reject: eight-case qualitative source |

The leading 27.0/40 formulation is not selected because its residual novelty is
0.5/5 and the published task is already occupied. The FSI formulation is the
only genuinely new controlled question in this batch, but one anatomy cannot
support a learned operator or patient-level inference. No score is repaired by
counting phases, grid cells, point samples or lesions as independent patients.

## 5. Decision and future evidence contract

- The team question is retained as an **evaluation template**, not an active
  paper identity.
- CMHA's exploratory negative signal stays unchanged and cannot be relabeled as
  a confirmatory real-versus-surrogate result.
- PointFlowNet and Hemo-MPO are mandatory direct priors/controls. Attention,
  multigrid, masking, SE(3) equivariance, PINN constraints and operator decoding
  are not AURORA novelty.
- The Dryad FSI record may later serve as a one-anatomy diagnostic or figure
  source only after a separately admitted problem authorizes payload access. It
  does not open P0 by itself.
- A future downstream-retention version needs one prospectively linked cohort
  with patient/base-family IDs, clinical and morphology variables, reference
  CFD fields and fixed summaries, matched surrogate predictions, explicit
  boundary/model-form provenance, and a sealed patient-level split.
- A future model-form version needs multiple independent anatomies with paired
  rigid/FSI or solver-ensemble reference fields; paired conditions within one
  geometry do not increase the independent sample size.
- PointFlowNet's exact public repository is watched fail closed. A new split
  manifest, dataset release, explicit license or code revision can request only
  a direct-prior baseline-feasibility re-audit. It cannot download data, repair
  a score, select a model or authorize compute.

No source in this batch reaches 32/40, so registering even a method-free P0
would be threshold shopping. No scientific server or scheduler was queried and
no job was submitted. Future gate-authorized execution remains restricted to
`introai9` PBS. `junjinyong` remains prohibited for connection, query,
transfer, submission and monitoring; login-node GPU commands remain prohibited.
