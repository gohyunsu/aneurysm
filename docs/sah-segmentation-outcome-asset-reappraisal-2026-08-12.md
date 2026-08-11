# Aneurysmal-SAH segmentation and outcome-asset reappraisal

> **Frozen decision · schema 10.7 · 2026-08-12 KST:** The public NCCT/mask
> release is real and useful, but it does not expose a versioned patient-level
> join to 3-month mortality, 6-month GOS, centre, treatment or a frozen split.
> The strongest fresh formulation scores **29.0/40** and fails the residual-
> novelty floor. All six formulations are rejected. No RAR member, patient
> image, mask, model weight, outcome table, P0/P1, method, architecture,
> scientific-server query, PBS/GPU job, outer test or paper claim is opened.

This audit asks whether an open aneurysmal-subarachnoid-hemorrhage (aSAH)
non-contrast CT release creates a defensible ISBI problem around
**outcome-faithful hemorrhage segmentation**. It is a fresh problem-level
screen, not a repair of any closed surface-vector, VMR, conformal-degree or
open-CTA contract.

## 1. What is publicly identifiable

The exact [Zenodo record](https://doi.org/10.5281/zenodo.8228847), revision 2,
is open under CC BY 4.0. It contains one 648,502,298-byte file,
`subarachnoid_hemorrhage_rhuh.rar`, with MD5
`a67bf358ebb326f156071864c318ab42`. The record says that each preprocessed
NIfTI NCCT is accompanied by an expert hemorrhage segmentation. It does not
publish a top-level manifest, patient count, centre, acquisition, aetiology,
treatment, outcome, reader, split or lesion-compartment table. The RAR body
was not opened, so names inside the archive are not inferred.

The linked [Swin-UNETR paper](https://arxiv.org/html/2312.17553) reports 100
internally segmented aSAH patients randomly divided 70/10/20 and ten external
patients. It reports source test Dice 0.873 and external Dice 0.738, among
other segmentation metrics. Those values are not AURORA results. Publication
counts do not prove that the one RAR is exactly the reported 100-patient
internal cohort, nor do they create a machine-auditable patient/split join.

The exact official code head is
`3fbd7a9282287a719aff5f603e9539b7a886b373`. It exposes inference and mortality
pipeline code plus a non-patient CT template, while the README links the
segmentation checkpoint through Google Drive. The repository contains no
tracked patient cohort, mask set, mortality/GOS table, split manifest or model
binary. Its licence text is an Academic Non-Commercial Source Code Licence;
GitHub reports `NOASSERTION`, so it is not relabelled as CC BY-NC software.
Only the small public source repository was inspected. No checkpoint or
medical input was accessed.

## 2. The obvious outcome identity is already occupied

The 2026 [Journal of Clinical Neuroscience study](https://doi.org/10.1016/j.jocn.2026.111993)
directly tests the central obvious claim. Its two nnU-Net experiments trained
on 356 and 530 patients and used the same 89-case test set. It reports source
median Dice 0.81, recall 0.82, ICC(3) 0.92 and median volume difference 1.40
mL. Manual and automatic lesion volumes were then compared for six-month GOS
prediction and were reported to have similar predictive ability. The study
also adds broader haemorrhage and trauma cohorts and seven-neurosurgeon
blinded assessment. None of these source results was reproduced by AURORA.

The earlier [initial-CT mortality study](https://doi.org/10.3390/brainsci14010010)
already predicts three-month mortality directly from admission CT. It reports
219 patients, 175 development and 44 evaluation patients; 180/219 were
aneurysmal SAH and 39/219 idiopathic SAH. The source AUC 0.82 is not an AURORA
result. Mortality is a different endpoint from six-month GOS, and its
potential dependence on withdrawal-of-support decisions makes it unsuitable
for casual relabelling as a treatment-independent biological target.

The public segmentation release therefore does not create a new
segmentation-to-outcome identity merely by connecting two papers from the
same broad programme. A reproducible experiment needs one versioned row-level
join among images, masks, endpoint time, outcome definition, treatment,
centre and split.

## 3. Direct-prior boundary

The remaining architecture and task variants are also crowded:

- the 2024 [multiclass aSAH study](https://doi.org/10.3389/fneur.2024.1490216)
  already segments SAH, IVH, ventricles, ICH, aneurysm and SDH in 73 aSAH
  patients (43/10/20), with an external 104-patient primary-ICH set and public
  nnU-Net weights;
- [LoRA/DoRA aSAH transfer](https://doi.org/10.1186/s12880-025-02116-y)
  already pretrains on 124 TBI patients and fine-tunes/evaluates on 30 aSAH
  patients by three-fold cross-validation, including small-volume failure;
- [SAHVAI-3D/4D](https://doi.org/10.1161/SVIN.124.001620) already defines
  spatial haemorrhage maps and longitudinal volume trajectories, albeit from
  ten aneurysmal-SAH cases and 92 scans;
- nnU-Net, Swin-UNETR, cross-aetiology transfer, parameter-efficient tuning,
  segmentation uncertainty, selective prediction, calibration and
  downstream-aware segmentation are strong controls or generic direct prior,
  not AURORA novelty.

Consequently, adding a transformer, GNN, LoRA, uncertainty head or outcome
loss to the released masks would not establish a contribution. The residual
question would have to be a source-identifiable failure of clinical
information preservation that existing volume-equivalence and multiclass
studies do not already answer.

## 4. Frozen non-compensatory screen

Each axis is scored 0--5 in the established order: biomedical importance,
target identifiability, residual novelty, usable asset readiness, effective
independent-unit strength, strong-baseline feasibility, interpretable-figure
value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Cross-aetiology, small-volume aSAH transport | 4.5 | 4.0 | 1.0 | 3.0 | 3.0 | 5.0 | 4.5 | 4.0 | **29.0** | reject |
| Segmentation-error-aware six-month GOS volume equivalence | 5.0 | 4.5 | 0.5 | 1.0 | 3.5 | 5.0 | 5.0 | 4.0 | **28.5** | reject |
| Multicompartment burden beyond modified Fisher grade | 5.0 | 3.5 | 1.0 | 1.0 | 3.5 | 5.0 | 5.0 | 4.0 | **28.0** | reject |
| Segmentation-conditioned three-month mortality | 5.0 | 4.0 | 0.5 | 1.0 | 4.0 | 5.0 | 4.5 | 4.0 | **28.0** | reject |
| Selective outcome-preserving segmentation | 5.0 | 3.0 | 1.5 | 1.0 | 3.5 | 5.0 | 4.5 | 3.5 | **27.0** | reject |
| Longitudinal resolution/DCI trajectory modelling | 5.0 | 2.5 | 1.0 | 0.5 | 1.0 | 5.0 | 5.0 | 2.5 | **22.5** | reject |

The 29.0 leader is executable only as another segmentation transfer study,
which is already occupied by cross-aetiology nnU-Net training and LoRA/DoRA
transfer. It fails the required residual-novelty minimum of 2.5/5. The more
clinically meaningful outcome rows fail asset readiness because no open,
versioned image--mask--outcome join was identified. Total score cannot
compensate for either failure.

## 5. What would materially change the decision

A future version may be rescored only if an official release provides all of
the following together:

1. row-level NCCT, manual compartment mask and fixed endpoint time;
2. mortality and functional outcome kept separate, with treatment and
   withdrawal-of-support timing declared;
3. patient, centre, repeated-scan and split identifiers;
4. an independent reader or adjudication contract and clinically meaningful
   measurement tolerance;
5. a strong fixed baseline path that includes the published nnU-Net,
   Swin-UNETR, multiclass and cross-aetiology controls.

Even then, source admission opens only a method-free audit. The first question
would be whether segmentation errors that are matched on Dice and volume
actually change patient-level outcome ranking or incremental value beyond
predefined clinical scores. Architecture selection remains downstream of an
observed, stable failure mechanism.

## 6. Authorization and relation to surface-vector

This source does not satisfy surface-vector E0: it contains NCCT haemorrhage
masks, not phase-resolved tangent WSS fields. Surface-vector remains inactive
and every historical no-verdict job remains unrepaired.

Active lead, primary problem, P0/P1, method, architecture, scientific-server
query, PBS/GPU, outer test, result row, C21 and claim are all zero. Future
gate-authorized execution uses `introai9` PBS only and never a login-node GPU.
Never access, query, transfer to, submit to or monitor `junjinyong`.
