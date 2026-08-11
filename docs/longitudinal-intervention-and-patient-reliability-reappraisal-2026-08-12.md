# Longitudinal, intervention-linked and patient-reliability reappraisal

**Frozen on:** 2026-08-12  
**State:** all six candidates rejected; active lead, P0/P1, method, architecture,
scientific-server query and GPU job are zero  
**Question:** do current longitudinal MRA, treatment-follow-up or large
multimodal detection assets identify a non-compositional ISBI 2027 problem?

## Decision

No current candidate passes the prospective non-compensatory admission gate.
The highest additive score is **32.0/40** for patient-level all-lesion miss-risk
control on RSNA-ICA, but it fails two mandatory floors: residual novelty is
**1.5/5** and asset readiness is **2.5/5**. Conformal risk control for lesion
detection and medical instance segmentation already owns the generic error-
budget mechanism, while the controlled RSNA release still lacks a public
machine-auditable patient/split/reference contract. A total score cannot
compensate for either failure.

The public longitudinal TOF-MRA cohort is scientifically valuable, but a fresh
2026 Bayesian displacement study already uses its adjacent vessel as an
internal reference for probabilistic growth detection. That study screens 24
follow-up patients, includes only 16 patients with 19 aneurysms and selects a
baseline--follow-up pair partly to improve growth-event representation. This is
not an unbiased prospective benchmark or dense local-remodelling reference.

The intervention-linked open asset contains 126 subjects and 141 procedures,
but its reusable contract is primarily tabular: clinical/procedural variables,
binary first/second follow-up occlusion and selected 2D DSA JPEGs for cavernous
ICA tortuosity. It is not a paired pre/post 3D image cohort. Geometry-based
flow-diverter occlusion prediction is also direct prior. No candidate therefore
opens data terms, payload transfer, P0, model selection or compute.

## 1. What changed in the source landscape

### Bayesian surface displacement directly occupies the obvious growth gap

The April 2026 preprint *Bayesian Aneurysm Growth Detection via Surface
Displacement Modeling* registers baseline and follow-up surfaces, computes
normal-directed displacements and subtracts mean adjacent-vessel displacement
from mean aneurysm-region displacement. A Bayesian soft threshold maps this
single patient-level statistic to growth probability and credible intervals.
It reports 39 patients/42 aneurysms in an institutional CE-MRA cohort and an
external public TOF-MRA subset of 16 patients/19 aneurysms selected from the 24
patients with follow-up imaging. The public pair-selection rule explicitly
maximizes image quality and representation of growth events while reducing
class imbalance. The public labels are re-derived with a 1 mm threshold even
though the original release used a 2 mm shape-change convention.

This is a substantive direct prior, not AURORA evidence. Its reported AUC
0.86--0.87 and Cohen's kappa up to 0.66 were not reproduced here. The source
does not state a versioned code release. Its limitations include small and
imbalanced cohorts, manual partitioning, nearest-neighbour rather than material
correspondence, selected timepoint pairs, heterogeneous intervals and no local
ground-truth remodelling field. [Preprint](https://arxiv.org/abs/2604.06649) ·
[public dataset DOI](https://doi.org/10.1038/s41597-024-03397-8) ·
[OpenNeuro release](https://doi.org/10.18112/openneuro.ds005096.v1.0.0)

The underlying release contains 63 patients and 85 aneurysms; 24 patients have
interval surveillance, 16 patients have more than one aneurysm, and all
available sessions are organized in BIDS. Those counts remain patient- and
lesion-level facts. Sessions, surfaces, vertices and pair choices are not new
independent patients.

### RSNA supplies scale, but not a new reliability mechanism or open contract

The official registry describes more than 4,000 CT studies from 18 institutions
and controlled, non-commercial, non-redistributable access. Its official wiki
still says only `Coming soon`. The June 2026 second-place study uses all 4,348
challenge series, 13 location labels and four modalities. It generates dense
pseudo-labels by predict--correct--retrain, uses random series-level five-fold
splits, selects the best two folds and evaluates the competition's weighted
14-label AUC. Its exact public code head observed for this audit is
`e59e2368a722eabedc6b2228b1c6e1e7325cacd5`; the released code and weights are
strong baselines, not a patient-level miss certificate.
[official registry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/) ·
[challenge page](https://www.rsna.org/artificial-intelligence/ai-image-challenge/intracranial-aneurysm-detection-ai-challenge) ·
[2026 method preprint](https://arxiv.org/abs/2606.26706) ·
[official method repository](https://github.com/PengchengShi1220/RSNA2025_Intracranial-Aneurysm-Detection)

Conformal risk control has already been applied to pulmonary-nodule detection,
including the false-positive/sensitivity trade-off and disagreement in lesion
ground truth. A separate medical instance-segmentation formulation explicitly
targets expected FNR/FDR control. Consequently, changing the anatomy to
intracranial aneurysm, applying a fixed detector and calling the output a
patient-level certificate is application transfer unless a distinct aneurysm-
specific failure mechanism and public reference contract are first identified.
[pulmonary-nodule CRC](https://proceedings.mlr.press/v266/hulsman25a.html) ·
[medical instance-risk preprint](https://arxiv.org/abs/2504.04482)

### The open flow-diverter asset is tabular follow-up, not paired 3D response

Mendeley record `nzzx92ky6r`, version 2, DOI
`10.17632/nzzx92ky6r.2`, is CC BY 4.0. It contains 141 procedures from 126
subjects, a raw Excel workbook, a propensity-score-matching R script embedded
in a Word file and a PowerPoint library of selected 2D DSA JPEGs used to grade
cavernous ICA tortuosity. Follow-up fields record months to first/second DSA and
binary complete obliteration. Repeated procedures are not independent patients,
and the JPEG subset is not a paired pre/post 3D imaging endpoint.
[official data record](https://data.mendeley.com/datasets/nzzx92ky6r/2) ·
[data article](https://doi.org/10.1016/j.dib.2022.108299)

A June 2026 study already evaluates parent-artery/aneurysm geometry as a
predictor of complete occlusion after flow diversion in 119 aneurysms. Earlier
patient-specific work also directly compares pre/post-interventional
hemodynamics and virtual stenting. A tabular neural network, geometry encoder or
survival head therefore does not by itself provide residual novelty.
[2026 geometry-outcome study](https://doi.org/10.1007/s00062-026-01668-y) ·
[pre/post hemodynamics study](https://doi.org/10.1016/j.compbiomed.2023.106720)

Prospective PETRA-MRA work pairs TOF-MRA, PETRA-MRA and DSA at postoperative day
1 and six months for 100 patients, but its raw images remain author-request
only. It is evidence that a reference-linked task matters, not an executable
public training or outer-test asset.
[prospective study](https://doi.org/10.3389/fneur.2026.1786151)

## 2. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at
least 32 and all schema-8.8 critical floors. Scores were frozen before ordering
and are not repaired after direct-prior inspection.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Patient-level all-lesion miss-risk control on RSNA | 5.0 / 4.0 / **1.5** / **2.5** / 4.5 / 5.0 / 5.0 / 4.5 | **32.0** | Reject: generic detection CRC/FNR control is direct prior and controlled RSNA release lacks an auditable public contract |
| Selection-audited adjacent-vessel longitudinal growth benchmark | 5.0 / **3.0** / **1.5** / 4.5 / **2.5** / 5.0 / 5.0 / 4.5 | **31.0** | Reject: the 2026 Bayesian study owns the mechanism; 16 selected public patients cannot support unbiased confirmation |
| Flow-diverter occlusion prediction from the open procedural table | 4.5 / 3.5 / **0.5** / 4.5 / **2.5** / 5.0 / 4.0 / 5.0 | **29.5** | Reject: repeated procedures, sparse image contract and direct geometry/outcome priors |
| Multimodality second-reader selective referral on RSNA | 5.0 / 3.5 / **0.5** / **2.5** / 4.5 / 5.0 / 4.5 / 4.0 | **29.5** | Reject: deferral/calibration is generic and reference adjudication is unavailable |
| Local posterior growth maps using adjacent-vessel control | 4.5 / **2.5** / **1.0** / 3.5 / **2.5** / 4.5 / 5.0 / 3.0 | **26.5** | Reject: explicitly proposed by the direct prior, with no local biological ground truth or material correspondence |
| Non-invasive post-treatment image-to-DSA concordance | 5.0 / 4.0 / **0.5** / **1.0** / **2.0** / 4.5 / 4.5 / **1.5** | **23.0** | Reject: paired raw images are request-only and the ISBI schedule cannot support independent confirmation |

The additive 32.0 row is not an admitted lead. It fails two critical axes and
therefore cannot authorize even a method-free P0.

## 3. Consequence for research identity

The surface-vector hypothesis remains inactive and unchanged. None of these
sources supplies a material transient-WSS evidence version, a stable structural
target or a field-error-matched surrogate failure. The old task-stability to
confirmation sequence remains the only acceptable re-entry order, but it is
not activated by this audit.

Longitudinal growth is also not adopted as a fallback identity. A defensible
future version would need a prospectively fixed all-session inclusion rule,
patient-grouped calibration and confirmation cohorts, independently adjudicated
growth/change references, and a failure mechanism not already reduced to the
adjacent-vessel displacement contrast. A larger neural architecture is not that
mechanism.

Patient-level lesion reliability is an evaluation principle worth retaining:
all lesions in one study form one set, and a missed second aneurysm should not
disappear inside mean location AUC. It remains an evaluation template, not a
paper contribution, until an open patient/split/reference contract and an
aneurysm-specific non-compositional gap exist.

## 4. Operational boundary

- Active lead, primary problem, P0/P1, method, architecture, result row, outer
  test, paper contribution and submission identity remain zero.
- No scientific server was queried, no transfer occurred and no PBS/GPU job was
  created for this audit. Public paper sources and metadata were inspected only.
- Future gate-authorized execution may use only `introai9` through PBS. Login-
  node GPU commands are forbidden. `junjinyong` must never be accessed, queried,
  transferred to, submitted to or monitored.
- Historical VMR and surface-vector scores/jobs retain their exact labels and
  are neither repaired nor rerun.
- The next allowed action is another genuinely new problem-level source or
  material-asset audit. Model naming, loss stacking, terms acceptance or a code
  release alone cannot open P0.
