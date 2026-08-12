# AneuX reliability direct-prior reappraisal

> **Decision · schema 11.7:** the schema-11.6 AneuX nested-orbit candidate is
> closed **before execution**. Its 33.0/40 score remains an immutable historical
> source-screen result; it is not a scientific result and is not retroactively
> changed. A fresh direct-prior screen scores the strongest residual formulation
> 32.0/40 but only 2.0/5 on residual novelty, below the prospectively fixed 2.5
> floor. P0 v1 and v2 remain byte-for-byte frozen, were never submitted, and are
> not repaired, promoted, or interpreted.

## 1. Why the question was attractive

AneuX is unusual because one lesion can be represented by several surface
preprocessings. The released source describes `original`, `area-001`, and
`area-005` resolutions and several anatomical cuts. That makes it possible to
ask whether a classifier that looks accurate on average changes its probability
for the *same lesion* when only its valid surface representation changes.

That is a useful reliability question. It is not, by itself, a new ISBI paper
identity. Resolution and cut also have different semantics:

- changing resolution within one fixed cut is primarily a discretization
  nuisance;
- changing the cut changes how much parent-vessel context is visible and is
  therefore an information-set intervention;
- AneuX status is cross-sectional rupture status, not future rupture risk.

The corrected P0 v2 respected these distinctions. This reappraisal asks the
separate question that matters for admission: is the remaining application gap
both independent and large enough after direct prior is considered?

## 2. Direct-prior boundary

| Prior | What it already establishes | Consequence for AURORA |
|---|---|---|
| [Juchler et al., 2022](https://doi.org/10.3389/fneur.2022.809391) | AneuX morphology, multi-source internal/external evaluation, and robustness comparisons across dome and progressively larger cuts | “Use AneuX cuts to test robustness” is occupied. The reported average cut trend cannot be relabelled as our finding. |
| [Rupture status classification using PointNet++, 2024](https://doi.org/10.3389/fphys.2024.1293380) | Dome-versus-cut1 point-cloud classification with internal and external AneuX cohorts, including reprocessed surfaces | A surface network and cut comparison are strong baselines, not novelty. |
| [DiffusionNet](https://arxiv.org/abs/2012.00888) | Discretization-agnostic learning on sampled surfaces | Resolution robustness from the encoder alone is occupied. |
| [Teng et al., 2022](https://doi.org/10.1038/s41598-022-14178-x) | Same-image/contour perturbations can expose unreliable radiomic models despite apparently adequate discrimination | “Average performance hides casewise preprocessing instability” is a known reliability mechanism. |
| [Zhang et al., 2023](https://doi.org/10.1038/s41598-023-45477-6) | Image perturbation as a surrogate for test–retest assessment of radiomic model reliability | Perturbation-based reliability evaluation is not an independent contribution. |
| [Ozenne et al., 2025](https://doi.org/10.1162/imag_a_00523) | Multiverse analysis across preprocessing pipelines | Aggregating or testing a preprocessing multiverse is generic prior art. |

The residual AneuX-specific value is narrower: factor resolution and anatomical
context correctly, group patients across sources, and report lesion-wise
instability rather than only mean AUC. This is a sound evaluation protocol, but
the present assets do not turn it into a non-compositional method or application
contribution.

## 3. Fresh non-compensatory score

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence, and ISBI schedule fit. A total of 32 is necessary but
cannot compensate for a critical axis below its fixed floor.

| Candidate | Axis scores | Total | Critical decision |
|---|---|---:|---|
| Factorized AneuX same-lesion reliability audit | 4.0 / 4.5 / **2.0** / 4.0 / 4.0 / 5.0 / 4.5 / 4.0 | **32.0** | Reject: residual novelty < 2.5 |
| Reliability-selected robust surface signature | 4.0 / 4.5 / **1.5** / 4.0 / 4.0 / 5.0 / 4.5 / 4.0 | 31.5 | Reject: perturbation-stable feature selection is direct prior |
| Preprocessing-multiverse aggregation | 4.0 / 4.5 / **1.0** / 4.0 / 4.0 / 5.0 / 4.5 / 4.0 | 31.0 | Reject: generic multiverse aggregation |
| Orbit-disagreement abstention | 3.5 / 4.0 / **1.5** / 4.0 / 4.0 / 5.0 / 4.5 / 4.0 | 30.5 | Reject: generic uncertainty/selective prediction and no decision utility target |
| Adaptive cut or view selection | 3.5 / 3.0 / **2.0** / 4.0 / 4.0 / 5.0 / 4.5 / 3.5 | 29.5 | Reject: selected view changes the information set and lacks a reference utility |
| Flat consistency across all cuts | 3.0 / **2.0** / **1.0** / 4.0 / 4.0 / 5.0 / 4.0 / 4.0 | 27.0 | Reject: forces invariance to real anatomical context |

No row passes every critical floor. Therefore there is no active lead, primary
problem, P0/P1, method, architecture, GPU training, outer test, result row,
paper claim, or submission identity.

## 4. Pre-execution contract defects

The v2 registration also exposed two implementation-contract mismatches. They
are reasons **not to execute the frozen contract**, not post-result repair tasks.

1. The config declares `source:patient_id` as the grouping and bootstrap unit,
   but `OrbitPrediction` stores only `patient_id`. The implementation therefore
   cannot distinguish equal patient identifiers from different sources. It also
   checks lesion identity globally rather than as a source-qualified identity.
2. The surface signature rejects non-triangle faces, degenerate triangles,
   non-manifold edges, and closed meshes, but it does not require one connected
   open component or reject non-manifold vertices. A disconnected surface can
   therefore pass a contract intended for one primary aneurysm dome.

Repairing these issues would create a fresh implementation version, but direct
prior already closes the scientific direction. A v3 is therefore not created.
The frozen files remain evidence of what was prospectively proposed, not code to
be silently corrected until it runs.

## 5. What remains reusable

The following principles survive as evaluation requirements for a future,
independently novel task:

- qualify patient and lesion identifiers by source before splitting or
  bootstrapping;
- distinguish nuisance transformations from transformations that change the
  clinical information set;
- report same-unit reliability, worst-pipeline behavior, and calibration in
  addition to average discrimination;
- reject disconnected or topologically invalid primary surfaces before feature
  extraction;
- keep cross-sectional association separate from future-event prediction.

These are safeguards, not claimed contributions. A future lead must add a
task-specific observable failure and an application endpoint that existing
robustness literature does not already answer.

## 6. Execution and manuscript boundary

- No AneuX row, geometry, archive, or private manifest was opened in this
  reappraisal.
- No scientific server was queried; no transfer, PBS job, or GPU command was
  issued.
- `introai9` remains the only permitted future PBS server after an external
  service-state change. Login-node GPU use is prohibited.
- `junjinyong` was not accessed and remains prohibited.
- The ISBI manuscript title, abstract, method, results, table, figure, and claim
  remain unchanged because there is still no admitted paper identity or result.

The next admissible action is a fresh problem-level audit over the already
documented assets. It must not rename reliability machinery, repair P0 v2, or
use compute to manufacture novelty.
