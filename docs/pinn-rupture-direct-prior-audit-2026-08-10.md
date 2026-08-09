# Geometry-conditioned PINN rupture-status direct-prior audit

**Frozen decision · 2026-08-10 KST:** the residual candidate scores
**23.5/40**, below the unchanged 32/40 admission line. It is rejected before
payload access, P0, method selection, architecture selection or compute. AURORA
therefore has no active primary problem, model, GPU job, outer test or submission
identity.

The audit asks whether the team's earlier idea—3D vascular geometry, learned or
physics-informed hemodynamics and clinical variables for aneurysm
rupture-status classification—still leaves an independent, testable contribution.
It does not evaluate the clinical correctness of any individual prediction.

## 1. The direct prior now occupies the original pipeline

The July 2026 preprint
[Integrating Physics-Informed Neural Networks and 3D Vascular Geometry Learning
for Cerebral Aneurysm Detection and Multimodal Rupture-Risk
Prediction](https://arxiv.org/abs/2607.10530) already implements the following
chain:

1. a PointNeXt vascular-surface encoder;
2. one PINN per aneurysm geometry, producing pressure, velocity, WSS, TAWSS,
   OSI and RRT descriptors without paired CFD field supervision;
3. clinical variables consisting of age, sex, location and side;
4. geometry-only, clinical-only, flow-plus-geometry, early-fusion and late-fusion
   comparisons on a common AneuX rupture-status cohort.

The paper reports 735 labeled aneurysms, including 261 ruptured and 474
unruptured lesions. Its best 70/30 probability-level late fusion reports pooled
out-of-fold AUROC/AUPRC 0.827/0.732; geometry plus clinical variables reports
0.809/0.701, clinical only 0.784/0.632, flow plus geometry 0.738/0.582 and
geometry only 0.611/0.448. These values are prior-work results, not AURORA
results.

Consequently, PointNeXt/GNN plus PINN descriptors plus clinical fusion is not a
new AURORA contribution. Replacing the backbone, adding attention, renaming the
fusion module or adding a physics loss would not restore novelty.

## 2. What the reported “hemodynamic modality” identifies

The AneuX surface is centered and scaled to a unit sphere. The PINN then uses the
largest open cap as inlet, a prescribed sinusoidal waveform, a common mean inlet
flow of 0.2 mL/s, rigid walls, Newtonian blood and a zero-relative-pressure
outlet gauge. It has no patient-specific inlet/outlet measurements and no paired
CFD or in-vivo flow targets.

Under this contract the PINN outputs are a geometry-conditioned deterministic
feature construction under shared modeling assumptions. They are not an
independently observed physiological modality. A classifier improvement after
adding them can establish predictive association within the evaluation split,
but it does not by itself establish that physically accurate patient-specific
hemodynamics add information beyond morphology.

The paper makes this boundary explicit: decreasing PINN residual and boundary
losses demonstrate optimization convergence, not physiological accuracy, and
the fields were not validated against conventional CFD or in-vivo flow
measurements. AURORA must preserve that distinction.

## 3. Endpoint and evaluation audit

### 3.1 Cross-sectional status is not future risk

The label is observed ruptured-versus-unruptured status. It can support
**rupture-status discrimination** only. It cannot support individualized future
rupture probability, time-to-event prediction or clinical utility. Rupture may
also change geometry, so morphology and derived PINN fields can encode
post-rupture consequences rather than prospective causes.

### 3.2 The independent unit is unresolved for the primary models

The official [AneuX record](https://zenodo.org/records/6678442) reports 750
aneurysm domes and 668 vessel trees. The official
[AneuX repository](https://github.com/hirsch-lab/aneuxdb) reports 605 patients.
The direct-prior paper describes stratified five-fold cross-validation for the
primary rupture-status models, while explicitly calling only its separate
tabular feature-importance folds patient-aware.

This does not prove that the primary split leaked patients, but it leaves
patient/vessel-family grouping unverified in the paper text. Lesion-level folds
cannot be treated as independent patient-level evidence until the exact mapping
and split manifest are available.

### 3.3 Model and fusion selection are not an outer test

The 70/30 weight was selected after sweeping weights on the same 735 pooled
out-of-fold predictions. The authors correctly describe this as sensitivity
analysis rather than independent hyperparameter validation. Likewise,
threshold-dependent metrics use a pooled out-of-fold F1-optimized threshold.
These results are useful internal evidence, but they are not a sealed outer
test, external validation or calibration study.

No code or split manifest is linked in the manuscript, and the paper reports no
external cohort, prospective outcome, CFD verification or in-vivo verification.
This audit therefore does not reproduce or challenge its reported numerical
results.

## 4. Residual candidate and frozen score

The only scientifically honest residual question is:

> After patient/vessel-family grouping and direct physical falsification, do
> patient-condition-aware hemodynamic fields contain incremental rupture-status
> information beyond morphology and clinical variables?

This is a worthwhile scientific question, but the currently audited assets do
not jointly identify it. AneuX supplies geometry, morphology and cross-sectional
status but no patient-specific boundary conditions or validated flow fields.
Aneumo/AneuG-style releases supply synthetic CFD under modeled conditions but do
not supply an independent clinical rupture-status cohort with matched
patient-specific physiology. Combining their labels would not create the
missing joint observation.

The frozen axes are clinical/scientific importance, target identifiability,
residual novelty after direct prior work, usable asset readiness, effective
independent unit, strong-baseline feasibility, interpretable-figure value and
ISBI schedule fit. Each is scored from 0 to 5.

| Axis | Score | Evidence-based reason |
|---|---:|---|
| importance | 4.5 | Whether apparent flow signal is physically real matters, but the released endpoint is cross-sectional status rather than future risk. |
| identifiability | 1.5 | No audited cohort jointly provides status, patient-specific conditions and verified CFD/in-vivo flow. Geometry-derived PINN features cannot identify independent physiology. |
| residual novelty | 2.0 | The full multimodal pipeline is directly occupied; physical falsification and grouping are necessary evaluation corrections, not yet a new algorithmic contribution. |
| asset readiness | 1.0 | AneuX lacks verified flow/BC, while synthetic CFD releases lack the matched clinical endpoint. The prior AneuX transport P0 is closed and is not repaired here. |
| independent unit | 3.0 | AneuX reports 605 patients, but the direct-prior primary split manifest and exact patient/vessel grouping are not available in the manuscript. |
| strong baselines | 5.0 | Clinical, morphology, PointNet/PointNeXt/GNN, flow-plus-geometry and fusion controls are clear and directly available in the literature. |
| interpretable figure | 4.5 | Geometry, assumed-versus-verified fields and conditional added value could be visualized clearly if a joint asset existed. |
| schedule fit | 2.0 | Per-case PINNs, patient-level regrouping and physical verification cannot be completed credibly for ISBI 2027 from the currently audited assets. |
| **Total** | **23.5 / 40** | **Rejected below the frozen 32/40 line.** |

The score is not repaired by counting 735 lesions as 735 independent patients,
calling a residual loss a CFD validation, or treating a synthetic and a clinical
dataset as one cohort.

## 5. Decision and implications

- The original geometry + PINN/surrogate hemodynamics + clinical fusion identity
  is directly occupied and is removed from the AURORA novelty space.
- GNN, PointNeXt, PINN, WSS/OSI/RRT channels, early/late fusion, feature
  importance and cross-sectional status classification are direct priors or
  controls, not contributions.
- The residual physically validated incremental-information question is rejected
  at 23.5/40 because the joint estimand and asset do not exist in the audited
  sources.
- No AneuX/model archive is downloaded, no closed P0 is repaired, and no
  executable P0, architecture, PBS job or GPU job is created.
- All future AURORA execution remains `introai9` PBS only. `junjinyong` is
  excluded from connection, query, submission and monitoring.
- The next allowed action remains a genuinely new or materially revised
  primary-source problem audit. Only a fresh candidate scoring at least 32/40
  can open a separately preregistered method-free CPU P0.

This is a direct-prior rejection, not a negative experiment and not a claim that
hemodynamics are clinically irrelevant. It says only that the original project
identity is already occupied and that the stronger residual claim is not
identifiable with the currently available joint evidence.
