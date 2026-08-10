# 4D-CTA AAA mechanics source audit · 2026-08-10

## Decision

The new public 4D-CTA abdominal aortic aneurysm (AAA) release is a strong
reproducibility asset, but it does not identify an admission-qualified AURORA
problem. Six formulations were frozen together under the unchanged eight-axis
source rubric. The strongest, phase-subset preservation of a released RSII
hotspot decision, scores **31.5/40**. It remains below the automatic **32/40**
admission line.

The active shortlist, selected primary problem, executable P0, method,
architecture, PBS/GPU work, outer test and submission identity therefore remain
zero. The 1.86 GB archive was not downloaded or range-read. We do not round
31.5, count cardiac phases as independent patients, add a GNN name, or merge
candidate scores after seeing the result.

## What the official source actually provides

The [official Zenodo record](https://zenodo.org/records/19182978), DOI
`10.5281/zenodo.19182978`, is open under CC BY 4.0. Its single file is
`Dataset_root.zip`, 1,857,980,948 bytes, with Zenodo MD5
`11b74684e382d1410a2d64f81967e613`. The API metadata and the associated
[Data in Brief descriptor](https://doi.org/10.1016/j.dib.2026.112865) report:

- 20 patients from three clinical centres;
- two to ten ECG-gated 3D CTA phases per patient, not 20 times the number of
  phases as independent people;
- patient-coordinate wall and intraluminal-thrombus surfaces, Abaqus FE meshes,
  and released strain, tension, SII and RSII surface maps;
- PRAEVAorta-assisted segmentation for P01--P10 and nnInteractive-assisted
  segmentation for P11--P20; and
- expert-selected systolic and diastolic configurations whose naming and phase
  indices vary across acquisition groups.

The release has no prospective rupture, growth, intervention, failure-location,
histology, wall-strength or treatment-utility endpoint. Its maps are derived
outputs of the published image-registration and biomechanics workflow, not
independent clinical ground truth. Source metadata and article text were read;
the ZIP, NRRD images, surfaces, FE members and field payloads were not accessed.

## Frozen candidate screen

Each axis is scored 0--5: biomedical importance, target identifiability,
residual novelty after direct prior work, usable asset readiness, effective
independent unit, strong-baseline feasibility, interpretable-figure value and
ISBI schedule fit.

| Candidate | Importance | Identifiability | Residual gap | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Phase-subset RSII hotspot preservation | 4.5 | 3.5 | 2.0 | 5.0 | 2.0 | 5.0 | 5.0 | 4.5 | **31.5** | reject |
| Image-to-RSII surface operator | 4.0 | 5.0 | 1.0 | 5.0 | 2.0 | 5.0 | 5.0 | 3.5 | **30.5** | reject |
| Mechanics-consistent cardiac-cycle registration | 4.5 | 4.0 | 1.0 | 5.0 | 2.0 | 5.0 | 5.0 | 3.5 | **30.0** | reject |
| Synthetic-GT-calibrated selective strain mapping | 4.5 | 3.0 | 2.0 | 5.0 | 0.5 | 5.0 | 5.0 | 4.0 | **29.0** | reject |
| Centre/pipeline-invariant structural-integrity mapping | 4.0 | 2.0 | 2.0 | 5.0 | 2.5 | 5.0 | 4.5 | 3.5 | **28.5** | reject |
| Progression or rupture prediction from released mechanics | 5.0 | 0.5 | 2.0 | 5.0 | 2.0 | 4.5 | 5.0 | 1.5 | **25.5** | reject |

The score is the arithmetic sum of the displayed cells. Rejection concerns the
current research formulation, not the quality or clinical value of the source
dataset.

## Why the strongest candidate still stops at 31.5

A reduced-phase question is measurable only as fidelity to the authors'
released RSII output. It does not establish fidelity to wall failure, future
growth or treatment benefit. The primary workflow already selects systolic and
diastolic configurations rather than requiring every frame, so generic phase
masking or an acquisition policy does not create a clean residual claim.
Different phase counts also reflect acquisition groups; randomly hiding frames
would not reproduce an observed clinical stopping process.

The effective confirmatory unit is 20 patients. Repeated cardiac frames, mesh
nodes and surface vertices are correlated measurements, not new people. A
patient-grouped outer split would consequently contain very few cases, while
centre is partly confounded with segmentation software and acquisition naming.
These facts lower unit strength and prevent a credible model-selection plus
confirmatory protocol on the ISBI schedule.

## Direct-prior red team

The attractive components are already occupied or must be controls:

- [Kinematics of Abdominal Aortic Aneurysms](https://doi.org/10.1016/j.jbiomech.2024.112484)
  already estimates local displacement and strain from 4D-CTA by regularized
  deformable registration and validates against a synthetic deformation;
- [Towards Personalised Assessment of AAA Structural Integrity](https://doi.org/10.1002/cnm.70140)
  already combines registered strain with FE-derived tension to define SII and
  RSII;
- [CARL](https://openaccess.thecvf.com/content/CVPR2025/html/Greer_CARL_A_Framework_for_Equivariant_Image_Registration_CVPR_2025_paper.html)
  and [SGDIR](https://openaccess.thecvf.com/content/CVPR2026/html/Matinkia_Learning_Diffeomorphism_for_Medical_Image_Registration_with_Time-Embedded_Architectures_Using_CVPR_2026_paper.html)
  directly occupy equivariant, cycle/semigroup-consistent registration;
- [uncertainty-aware deformable registration](https://openaccess.thecvf.com/content/WACV2022/html/Gong_Uncertainty_Learning_Towards_Unsupervised_Deformable_Medical_Image_Registration_WACV_2022_paper.html)
  already couples registration and correspondence uncertainty;
- [AAA wall-stress neural prediction](https://doi.org/10.1115/1.4051905) and
  recent geometry-aware aneurysm field surrogates make a generic image/mesh to
  mechanics regressor incremental; and
- [functional surrogate prediction sets](https://proceedings.mlr.press/v286/gray25a.html)
  and [function-valued neural-operator uncertainty](https://proceedings.mlr.press/v267/magnani25a.html)
  directly occupy generic calibrated field UQ.

Consequently, a GNN, graph Transformer, neural operator, diffeomorphic loss,
cycle loss, uncertainty head, conformal wrapper or field-functional loss is a
baseline or engineering choice. None repairs the missing independent outcome
or small effective unit.

## Compute and next action

No executable P0 is registered because no candidate reaches 32. No archive
member, patient image, mesh or field was read. No PBS job was created and no
login-node GPU command was run. A bounded `introai9` status attempt on
2026-08-10 reached the configured endpoint but was reset before any remote
command, so it produced no current scheduler observation and triggered no
connection-repair loop.

All future AURORA execution remains restricted to `introai9` PBS.
`junjinyong` is excluded from connection, status query, transfer, submission and
monitoring. The next admissible work is a genuinely new source with an
independent clinical or physical target and sufficient patient units, followed
by a fresh source audit. This rejected batch is not repaired into a method or
GPU experiment.
