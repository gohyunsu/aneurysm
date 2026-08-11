# Cross-view projection source-delta audit

> **Frozen decision · schema 8.1 · 2026-08-11 KST:** recent cross-view DSA,
> biplanar localization and conformal-localization sources do not open a new
> AURORA problem. The strongest exact formulation,
> `adam_projection_consistent_3d_lesion_set`, scores **31.0/40**, below the
> unchanged 32-point admission line. All six formulations are rejected. No
> patient payload, access agreement, P0/P1, method, architecture, server query,
> PBS/GPU job, outer test, result row or paper claim is authorized.

## 1. The attractive idea, stated correctly

Two approximately orthogonal angiographic projections appear to offer a clean
route from 2D aneurysm detections to a 3D location. A more defensible output than
an unconditional point would be a projection-consistent 3D set, with abstention
when correspondence is ambiguous. This is a meaningful reliability question.
It is not, however, an unoccupied problem simply because the output is called a
set or certificate.

The fresh [MIDL 2026 cross-view paper](https://openreview.net/pdf/f943ad69f9a9542edf4f959c51bb2a2b2ba7f2d2.pdf)
materially changes the direct-prior boundary. It uses all 113 ADAM cases,
creates AP and lateral maximum-intensity projections from the 3D MRA volumes,
projects the 3D labels into both views, and trains an RT-DETR-based detector
with shared superior--inferior-coordinate prompting and a consistency loss.
Its reported AP mAP50 rises from 0.270 for RT-DETR to 0.643 for joint prompting.
At inference, however, it uses one view only. The work therefore directly owns
cross-view training on ADAM-derived projections, but does not validate real
biplane DSA or 3D reconstruction.

That distinction is essential: these are deterministic MIPs of an already
available volume, not independently acquired DSA projections with calibration,
foreshortening, contrast-flow and view-timing errors. Calling them simply
“DSA” would overstate the evidence.

## 2. Asset reality

### 2.1 ADAM is usable only after a human access decision

The official [ADAM data page](https://adam.isi.uu.nl/data/) describes a
registration- and confidentiality-agreement-gated release. Its 113 scans
contain 93 positive and 20 negative cases with centers/radii and consensus
masks; some subjects have baseline and follow-up scans. The independent unit
must therefore be the subject, not the scan or the two projections. AURORA has
not accepted the agreement or accessed the payload. The 8:1:1 case split in the
cross-view paper is not evidence of a subject-grouped split.

### 2.2 Large clinical DSA cohorts are not public execution assets

The 2025 multicenter [SDAN study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12554613/)
reports 62,187 DSA images from 1,114 patients across three hospitals, with 632,
131, 285 and 237 aneurysms in its train, internal-test and two external-test
partitions. It is a strong demonstration that single-frame DSA segmentation
and external-center degradation are already direct clinical problems. Its data
availability statement also says the data are third-party owned, cannot be
publicly distributed and are available only on reasonable request. No paired
AP/lateral calibration or public manifest is released. Cohort size is not
asset readiness.

### 2.3 Real cross-view physics is already known to matter

A 2025 [path-length correction study](https://pubmed.ncbi.nlm.nih.gov/41295973/)
uses rotational and 2D DSA from three cerebrovascular cases, aligns synthesized
projections to the acquired views and corrects kVp and path length. It reduces
cross-view time-density-curve RMSE from 0.23 to 0.14. This is only three cases,
but it directly shows why orthographic MIP consistency is not a faithful model
of clinical biplane DSA intensity or flow.

## 3. Direct-prior boundary

The residual methodological ingredients are also occupied:

- [RibAssist 3D](https://arxiv.org/abs/2608.06914) already decomposes
  CT-derived biplanar localization into detection, correspondence and geometry,
  commits only confident pairs, measures correct 3D yield at a fixed false-
  output budget and confirms once on a sealed 55-case cohort. It explicitly
  identifies correspondence confidence—not triangulation—as the bottleneck.
- [Reliable multi-output conformal landmark localization](https://doi.org/10.1016/j.media.2026.103953)
  already constructs finite-sample-valid, flexible non-convex prediction
  regions for 2D and 3D medical landmarks and releases code.
- [Task-driven conformal UQ for inverse problems](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/7734_ECCV_2024_paper.php)
  already calibrates downstream-task uncertainty induced by an imaging inverse
  problem and uses efficiency to guide further measurement.
- [ProVLNet](https://pmc.ncbi.nlm.nih.gov/articles/PMC11858964/) already fuses
  calibrated biplanar features in 3D using projective geometry for medical
  landmark localization.
- Aneurysm-specific biplane silhouette reconstruction, 3D/2D registration,
  generic conformal risk control and abstention remain direct controls from the
  existing AURORA lineage.

Consequently, cross-view fusion, a shared-axis prompt, triangulation,
projection consistency, conformal regions and abstention are not standalone
novelty. The combination is especially weak when both views are rendered from
the same source volume and the proposed clinical target is independently
acquired DSA.

## 4. Frozen eight-axis screen

Axes are fixed in this order: biomedical-imaging importance, target
identifiability, residual novelty after direct priors, usable asset readiness,
effective independent-unit strength, strong-baseline feasibility,
interpretable-figure value and ISBI-schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ADAM projection-consistent 3D lesion set | 4.5 | 4.0 | 1.0 | 3.0 | 4.0 | 5.0 | 5.0 | 4.5 | **31.0** | reject |
| ADAM selective biplanar 3D point localization | 4.5 | 4.0 | 0.5 | 3.0 | 4.0 | 5.0 | 5.0 | 4.0 | **30.0** | reject |
| ADAM cross-view consistency failure audit | 4.5 | 4.0 | 1.0 | 3.0 | 4.0 | 5.0 | 5.0 | 3.0 | **29.5** | reject |
| Multicenter single-frame DSA shift abstention | 5.0 | 4.0 | 0.5 | 0.5 | 5.0 | 5.0 | 5.0 | 1.5 | **26.5** | reject |
| Cross-view quantitative-DSA functional calibration | 5.0 | 4.0 | 0.5 | 0.5 | 0.5 | 5.0 | 5.0 | 2.0 | **22.5** | reject |
| Clinical biplane DSA projection-set localization | 5.0 | 2.0 | 1.5 | 0.5 | 0.5 | 5.0 | 5.0 | 2.0 | **21.5** | reject |

The 31.0 leader is deliberately not repaired. Its target is mathematically
clean on synthetic orthographic projections, but the strongest residual claim
would be an aneurysm-specific application of methods already demonstrated in
biplanar selective localization, conformal 3D regions and inverse-problem task
UQ. Registration-gated ADAM data and synthetic-view evidence do not justify
promoting that application to an active ISBI identity.

## 5. Consequence for AURORA

- The surface-vector hypothesis remains inactive; this audit neither repairs
  nor reruns jobs `115645.ECE-util1` or `115684.ECE-util1`.
- The latest conformal-degree P0 remains execution-incomplete/no scientific
  verdict with 0/10 checks. Its historical 32.5/40 score is unchanged.
- No GNN, detector, projective network, conformal head or architecture is
  selected. There is no experiment result to add to the paper.
- A future cross-view version requires a materially new paired clinical asset:
  calibrated AP/lateral DSA from independent patients, explicit acquisition
  geometry and timing, patient-level split keys, 3D reference or a defensible
  set-valued estimand, and terms that permit prospective use. A new loss or
  public code release alone is not that change.
- This audit made no scientific-server query and created no PBS/GPU job. Any
  later gate-authorized execution uses `introai9` PBS only; `junjinyong` remains
  prohibited for connection, query, transfer, submission and monitoring.
