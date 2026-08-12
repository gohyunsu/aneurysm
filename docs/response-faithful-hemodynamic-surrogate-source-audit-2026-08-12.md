# Response-faithful multi-flow haemodynamic surrogation

Status: **one conditional source lead; method-free P0 registered but not
executable; primary method, architecture, GPU, outer test, result and paper
claim remain unselected**  
Target venue: **IEEE ISBI 2027**  
Decision date: 2026-08-12 KST

## 1. Decision

The most defensible use of the assets already acquired by AURORA is not another
geometry-only CFD surrogate and not rupture prediction. It is a narrower
verification problem:

> Given one nominal-flow CFD field and an image-derived aneurysm geometry, can a
> fast surrogate sweep alternative inlet-flow conditions while preserving the
> reference CFD response, rather than merely attaining a low average field
> error?

The proposed application identity is **response-faithful multi-flow
haemodynamic surrogation**. The object to preserve is the change of the velocity
field with mass flow: response magnitude, direction, discrete tangent and
curvature, and the ranking of cases by response energy. It is not a clinical
risk score, biological phenotype or patient-specific physiology.

This formulation uses the verified Aneumo compact holding: 32 Aneumo
generation families, two deformations per family, eight steady mass-flow
conditions and 4,096 aligned internal points per case. The historical config
calls this grouping key `aneux_base_family`; it is an Aneumo `Connection.csv`
lineage unit, not the separate AneuX rupture-status dataset. The existing
20/6/6 base-family split is preserved. The exact cache SHA-256 is
`9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`.

The direction passes the prospective source screen only at the application
intersection. Residual learning, derivative supervision, neural operators,
equivariance and boundary conditioning are mandatory controls, not novelty.
A method-free P0 must first establish that the proposed response endpoints are
stable and resolved by the eight-flow grid. A later field-error-matched P1 must
then observe the alleged failure of standard surrogates. No architecture is
selected before those two facts exist.

## 2. Why this is different from the failed Aneumo branch

The closed V1/V1e branch tried to predict the absolute velocity field from
geometry and boundary information. V1e showed a consistent incremental benefit
from boundary tokens, but failed every preregistered absolute learnability
threshold: worst-seed train, validation and response relative L2 were
0.77221, 0.87796 and 0.94918. Those thresholds, checkpoints and outcomes remain
unchanged and are not repaired.

The new task has a different information set and estimand. It receives the
same case's nominal field at \(q_0=0.0025\,\mathrm{kg/s}\), then predicts fields
at the other registered flows. This corresponds to accelerating a CFD
sensitivity sweep after one reference solve, not replacing CFD from geometry
alone. The strongest non-learned control is therefore also unusually strong:
scale the same-case anchor field by a train-fitted power law. The previous
train-only audit found that this control still left a velocity-response
residual of 0.2112 with family-bootstrap 95% interval [0.2001, 0.2243]. This is
historical target evidence, not learned-model performance and not a new result
of the present version.

## 3. Direct-prior boundary

The following sources define what cannot be claimed as AURORA novelty.

| Prior | What it already establishes | Consequence for AURORA |
|---|---|---|
| [Aneumo](https://arxiv.org/abs/2505.14717) | 427 base geometries, 10,660 synthetic shapes, eight steady flows and DeepONet/Swin-DeepONet benchmarks; evaluation becomes more optimistic when fewer flow conditions are used | Multi-flow conditioning, DeepONet and condition-diversity evaluation are direct controls |
| [Cebral et al.](https://pubmed.ncbi.nlm.nih.gov/32008209/) | 1,820 aneurysms, nine inflows and flow-response variables used for rupture-status assessment | A haemodynamic “response phenotype” and its clinical classification use are not new and are not the present target |
| [DeltaPhi](https://proceedings.neurips.cc/paper_files/paper/2025/hash/12bf28fb68f295f855a5bf0c5a217d6e-Abstract-Conference.html) | Learning residuals between nearby physical states on regular and irregular domains | Anchor-to-target residual learning is a strong baseline, not the contribution |
| [Derivative-Informed Neural Operator](https://doi.org/10.1016/j.jcp.2023.112555) | Joint operator/Jacobian accuracy for parametric PDE maps | Finite-difference or derivative loss alone cannot be claimed as novel |
| [Derivative-Informed FNO](https://arxiv.org/abs/2512.14086) | Simultaneous output and Fréchet-derivative approximation, including Navier--Stokes examples | “Field accuracy is insufficient for derivatives” is a general SciML prior |
| [Physics-constrained aneurysm GNN](https://doi.org/10.1038/s41746-026-02404-z) | Inflow-aware transient aneurysm velocity rollout with regional errors and unseen-inflow evaluation | GNN, inflow tokens, physics loss and aneurysm flow surrogation are controls |
| [Geometry-aware PointNet](https://doi.org/10.1016/j.cmpb.2026.109308) | Fast peak-systolic velocity/WSS prediction and non-idealized OOD degradation | Point-cloud surrogation and field-level speedup are not independent novelty |
| [2015 aneurysm CFD challenge](https://pubmed.ncbi.nlm.nih.gov/30203115/) | Workflow, extent and inflow choices can materially change WSS | Response credibility is important, but variability itself is established |

The residual application gap is therefore exact and falsifiable: published
aneurysm surrogates are selected mainly by pointwise or regional field error,
whereas a multi-condition surrogate may reproduce fields yet misrepresent the
gain, direction, curvature or case ordering of the CFD response. AURORA must
observe this mismatch at matched field error before it can claim the gap.

## 4. Frozen six-candidate screen

Each axis is scored from 0 to 5 in the fixed order: biomedical importance,
target identifiability, residual novelty, asset readiness, effective
independent units, strong-baseline feasibility, interpretable evidence and
ISBI schedule fit. Admission requires at least 32/40 and every critical floor.

| Candidate | Importance | Target | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **Field-error-matched multi-flow response fidelity** | 4.5 | 5.0 | 2.5 | 5.0 | 3.0 | 5.0 | 5.0 | 4.0 | **34.0** | conditional source lead; P0 only |
| Generic anchor-state residual operator | 4.0 | 5.0 | 0.5 | 5.0 | 3.0 | 5.0 | 5.0 | 4.0 | **31.5** | reject; DeltaPhi directly occupies it |
| Derivative-informed aneurysm operator | 4.0 | 5.0 | 0.5 | 5.0 | 3.0 | 5.0 | 5.0 | 3.5 | **31.0** | reject; DINO/DIFNO directly occupy it |
| Multi-flow condition-diversity benchmark | 3.0 | 5.0 | 0.0 | 5.0 | 3.0 | 5.0 | 4.0 | 4.0 | **29.0** | reject; Aneumo already reports it |
| Geometry-only full-field re-entry | 3.0 | 5.0 | 0.0 | 5.0 | 3.0 | 5.0 | 4.0 | 3.0 | **28.0** | reject; direct prior and V1e failure |
| Multi-flow rupture-response phenotype | 4.5 | 1.0 | 0.5 | 0.5 | 3.0 | 5.0 | 4.5 | 3.0 | **22.0** | reject; no clinical labels and direct prior |

The leader's novelty score is exactly the 2.5 floor. It is intentionally not
raised for an architecture name. If P0 cannot identify stable response
endpoints, or P1 does not observe a field-error/response-fidelity mismatch, the
direction closes.

## 5. Method-free P0

The frozen contract is
[`configs/aneumo_response_fidelity_p0.json`](../configs/aneumo_response_fidelity_p0.json).
It is registered but non-executable because the current private cache path has
not been re-established after the incomplete `introai9` inventory. No server
retry is allowed until an external administrator/service state change.

The aggregate evaluator and its CPU-only one-shot wrapper are now implemented
at [`src/aurora/aneumo_response_fidelity_p0.py`](../src/aurora/aneumo_response_fidelity_p0.py)
and [`cluster/pbs_aneumo_response_fidelity_p0.pbs`](../cluster/pbs_aneumo_response_fidelity_p0.pbs).
This is implementation readiness, not execution authority or scientific
evidence. The current config is tested to refuse before checking whether a
private cache exists. The wrapper is therefore not submittable in the current
state and has not been submitted.

P0 reads only the 20 historical train base families and only `coordinates_m`
plus the three velocity channels. It does not read pressure, validation/test
fields, a model, checkpoint or prediction. It checks:

1. the frozen cache, staging contract, flow grid, 40 cases and 20 families;
2. exact coordinate alignment and finite velocity across all eight flows;
3. exact reproduction of the already published scaling-audit dependency,
   without relabelling it as a fresh result;
4. response-descriptor agreement under two deterministic coordinate-hash
   halves, ranking families separately within each non-anchor flow before
   concatenation so the monotone flow grid cannot manufacture agreement;
5. stability of direction, gain and discrete tangent/curvature summaries under
   leave-one-interior-flow interpolation;
6. family-bootstrap uncertainty with family, not case/flow/node, as the unit.

Every check must pass. Failure or execution-incomplete closes this exact P0
without threshold, parser, split or source repair. A pass opens a separately
registered baseline-only P1; it does not select a model or authorize a GPU.
All uncertainty uses 5,000 family-cluster bootstrap replicates. The evaluator
publishes only aggregate endpoints and explicitly excludes pressure, case IDs,
family IDs, validation/test fields, checkpoints, predictions and GPU access.

## 6. P1 and model-selection falsifier

P1 uses development families only. It compares the same-case analytic power
law, linear response interpolation, a pointwise conditional MLP, DeepONet,
DeltaPhi, MeshGraphNet and the frozen V1e control. Checkpoints are selected by
field error only. P1 then asks whether field-error-matched models differ
materially on response endpoints.

The direction stops if either condition holds:

- response metrics are almost completely determined by field relative L2, so
  they add no distinct evaluation information; or
- no strong baseline pair with comparable field error exhibits a reproducible
  response-fidelity difference across base families.

Only an observed mismatch permits a minimal response-factorized model. The
model hypothesis is

\[
\widehat{\mathbf v}(x,q)=
\left(\frac{q}{q_0}\right)^{\alpha}\mathbf v(x,q_0)
+\phi\!\left(\log\frac{q}{q_0}\right)
R_\theta\!\left(G,\mathbf v(\cdot,q_0),x,q\right),
\qquad \phi(0)=0.
\]

The first term is the strong physical scaling control. The zero-at-anchor
factor gives an exact identity route. `R` may use an SE(3)-equivariant local
graph encoder, boundary tokens and a continuous coordinate query. Those blocks
are implementation choices. The only defensible method claim would be that
the factorization tied to the observed response failure improves response
fidelity without degrading matched field accuracy.

## 7. Confirmation and statistics

The current six untouched compact-cache test families are too few for a strong
standalone claim. Before model development, the existing 20/6 development
families remain fixed. If P0 and P1 pass, select additional untouched Aneumo
base families from the same official release using only `Connection.csv` and
train-only morphometrics, then freeze their IDs before any field read. A
minimum of 50 independent confirmation families is required; deformations,
flows and nodes never increase that count. Selective ZIP64 range reads may
stage only coordinates and velocity, and raw/compact fields remain private and
non-redistributed under the more restrictive observed dataset terms.

Report family-cluster bootstrap 95% intervals and five training seeds. The
primary comparison requires both:

- no worse field relative L2 than the strongest field-selected baseline under
  a prospectively fixed non-inferiority margin; and
- lower paired-response L2 and discrete-tangent error with the same direction
  in at least four of five seeds and a family-bootstrap interval excluding
  zero.

Secondary endpoints are gain error, curvature error, family response-rank
correlation and high-response-region overlap. They do not replace the two
primary endpoints.

## 8. Four-page ISBI paper contract

The official ISBI 2027 rules require single-blind review and four pages of
technical content. A paid fifth page may contain only ethics,
acknowledgments/conflicts and references. Submission is due 26 October 2026 at
23:59 US EDT.

The paper remains provisional until P0/P1 pass. The compact structure is:

1. **Introduction (0.65 page):** one gap—field accuracy does not establish
   multi-flow response credibility; three evidence-linked contributions.
2. **Method (1.15 pages):** task/units, response endpoints and, only if
   authorized, the minimal anchor-response factorization.
3. **Experiments (0.70 page):** family-disjoint development/confirmation,
   direct controls, matched compute and statistics.
4. **Results (1.15 pages):** one main table, one ablation table and one
   reference/baseline/proposal response figure on identical coordinates and
   colour scales.
5. **Discussion (0.35 page):** steady synthetic CFD, modeled mass flows,
   limited clinical interpretation and exact failure domain.

Provisional claims and their deletion rules are:

| Claim | Required evidence | Delete when absent |
|---|---|---|
| C1. Field accuracy can hide response error | field-error-matched P1 mismatch | delete the problem identity |
| C2. The minimal factorization preserves CFD response | primary response improvement with field non-inferiority | delete the method contribution |
| C3. The result generalizes across source anatomies | at least 50 locked, family-disjoint confirmation families | label all results exploratory |

No sentence may claim clinical risk, patient-specific inflow, in-vivo
validation, WSS fidelity or prospective utility from this velocity-only,
synthetic steady-CFD evidence.

## 9. Operational boundary

This audit used public primary sources and existing local aggregate records.
It queried no scientific server, scheduler or GPU and transferred no data.
`introai9` remains the only allowed future PBS execution server, and no
login-node GPU command is allowed. `junjinyong` must never be accessed, queried,
used for transfer, submitted to or monitored.
