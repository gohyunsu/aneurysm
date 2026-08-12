# Aneumo response-fidelity residual-novelty audit

Status: **conditional application lead retained at 32.5/40; no active method,
architecture, experiment or paper claim**  
Target venue: **IEEE ISBI 2027**  
Decision date: **2026-08-13 KST**

## 1. Decision in one sentence

The best defensible use of AURORA's acquired holdings remains an Aneumo
multi-flow sensitivity-sweep study, but the contribution can only be the
**aneurysm-specific, field-error-matched failure and repair of spatial response
fidelity**—not response-consistent surrogation, multi-flow learning, an
equivariant GNN, a neural operator, derivative supervision or residual learning
in general.

This is a conditional source decision, not a result. Real P0 remains 0/11, the
current exact private cache path is unresolved, and no scientific server, PBS
job, GPU, model prediction or outer-test field was used in this audit.

## 2. Why Aneumo remains the least-bad acquired asset

The choice is comparative, not enthusiastic.

| Audited holding | What is materially available | Why it is not the current lead |
|---|---|---|
| **Aneumo compact holding** | 32 generation families, two deformations per family, eight aligned steady-flow conditions and 4,096 internal points per case; historical cache checksum and family-disjoint split are recorded | It uniquely identifies repeated boundary-condition responses on the same geometry. The old geometry-to-field model failed, but the one-anchor response task is a different estimand. |
| BenchAnXplore | 105 geometries and 80 transient velocity frames | All cases were used in architecture discovery, so they cannot provide fresh confirmation; no verified pressure/WSS target contract is available. |
| CMHA | 99 patient-level clinical material with morphology/hemodynamic tables | The exact lesion-level image–surface–hemodynamic join failed and exploratory hemodynamic increment was not supported. |
| AneuX | Same-lesion resolution/cut orbits | The reliability idea is direct-prior dense and was rejected at residual novelty 2.0/5. |
| AneuG-Flow / Aneurisk / VMR | Valuable geometry or CFD metadata | Their registered probes ended before scientific checks; current vector/phase/field contracts are unresolved. Existing jobs are not repaired or rerun. |

This comparison does not say that the other datasets are bad. It says that only
Aneumo currently exposes the repeated-condition unit needed for a falsifiable
application question without inventing a clinical label that the source does
not contain.

## 3. Latest collision matrix

The new audit adds two direct priors that were missing from the previous
lineage. They narrow the wording but do not yet occupy the exact experimental
intersection.

| Primary source | What it already owns | What it does **not** establish | Consequence |
|---|---|---|---|
| [Aneumo](https://arxiv.org/abs/2505.14717) | 427 base geometries, synthetic deformations, eight steady flows, boundary-conditioned DeepONet/Swin benchmarks and flow-diversity experiments | Field-error-matched spatial response-curve endpoints or a same-backbone output-mechanism contrast | Multi-flow prediction, flow conditioning and the dataset itself are not contributions. |
| [Cebral et al.](https://pubmed.ncbi.nlm.nih.gov/32008209/) | Nine inflows over 1,820 aneurysms and scalar response/linearity variables for rupture-status models | Fidelity of a learned spatial-field surrogate to CFD response curves | “Aneurysm response phenotype” is occupied; the target must remain surrogate fidelity, not rupture. |
| [Interventionally Consistent Surrogates, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/26b8e3dc3a21fcd660d80c63b767f324-Abstract-Conference.html) | The general principle that conventional surrogates can misjudge intervention effects and should be trained for interventional consistency | A PDE/aneurysm implementation, field-error matching, multi-flow spatial endpoints or the proposed anchor identity | “Response-preserving surrogate” is not a general novelty claim. Only the biomedical instantiation and evidence can remain. |
| [SC-FNO, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/227b19598f79ed838b01933b9a6ace41-Abstract-Conference.html) | The distinction between solution accuracy and parameter-sensitivity accuracy, plus sensitivity supervision | Aneurysm-specific matched failure, analytic scaling control or family-level confirmation | Sensitivity loss and the generic mismatch claim are controls, not contributions. |
| [DINO](https://doi.org/10.1016/j.jcp.2023.112555) and [DIFNO](https://arxiv.org/abs/2512.14086) | Joint solution/derivative learning for parametric PDE operators | The proposed application-specific evaluation and identity-output test | Derivative-informed training is a mandatory baseline family. |
| [Hemo-MPO](https://doi.org/10.1016/j.aej.2026.05.044) and [AB-GATr](https://arxiv.org/abs/2605.18816) | Aneumo field surrogation with equivariant mesh/operator components and anatomy-stratified evaluation | A complete executable matched reproduction bundle, or the exact response-fidelity estimand | SE(3), mesh encoders, physics loss and equivariance cannot be sold as novelty. |
| [Aneurysm haemodynamics under vessel dilation](https://doi.org/10.1016/j.cjph.2026.04.015) | POD–Transformer/LSTM surrogation of WSS, OSI and pressure under normal versus dilated vessels in six MCA cases | Multi-inflow response curves, field-error-matched failure, family-disjoint large-scale confirmation or one-anchor identity | “Predicting aneurysm haemodynamic response to a perturbation” is also too broad. |
| [Physics-constrained aneurysm GNN](https://doi.org/10.1038/s41746-026-02404-z) | Transient full-field GNN prediction, inflow information and unseen-inflow evaluation | The matched response-fidelity failure/repair test | GNN, inflow tokens and physics constraints are baselines. |

The exact residual gap is therefore:

> When two strong aneurysm CFD surrogates have equivalent velocity-field error,
> can they still differ materially in their anchor-relative spatial response to
> inlet flow, and can an exact identity-at-anchor output parameterization remove
> that failure beyond both a learned direct head and train-fitted power-law
> scaling?

No inspected primary source establishes this full conjunction. That is enough
to retain a conditional ISBI application lead, but not enough to activate a
paper or justify a method name.

## 4. Fresh acquired-asset candidate screen

Each axis is 0–5 in the fixed order: biomedical importance, target
identifiability, residual novelty, asset readiness, effective independent
units, strong-baseline feasibility, interpretable evidence and ISBI schedule
fit. Admission requires total at least 32 and every critical floor, including
residual novelty at least 2.5.

| Candidate using acquired assets | Importance | Target | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **Field-error-matched multi-flow response fidelity on Aneumo** | 4.0 | 5.0 | 2.5 | 4.0 | 3.0 | 5.0 | 5.0 | 4.0 | **32.5** | conditional lead; P0 only |
| Mixed geometry×flow interaction fidelity on Aneumo | 4.0 | 3.5 | 3.0 | 4.0 | 3.0 | 4.5 | 5.0 | 3.0 | **30.0** | reject; synthetic deformation lacks longitudinal meaning |
| Selective/uncertainty-aware response surrogation | 4.0 | 5.0 | 1.0 | 4.0 | 3.0 | 5.0 | 4.5 | 4.0 | **30.5** | reject; generic selective prediction/UQ is occupied |
| Cross-condition WSS/pressure response fidelity | 4.5 | 2.0 | 2.0 | 2.0 | 3.0 | 5.0 | 5.0 | 2.0 | **25.5** | reject; compact target is velocity-only |
| Multi-flow rupture-response phenotype | 4.5 | 1.0 | 0.5 | 0.5 | 3.0 | 5.0 | 4.5 | 3.0 | **22.0** | reject; no clinical label and direct prior |
| New equivariant GNN/operator benchmark | 3.0 | 5.0 | 0.0 | 4.0 | 3.0 | 5.0 | 4.0 | 4.0 | **28.0** | reject; architecture space is occupied |

The earlier 34.0/40 score remains provenance. The fresh score is lower because
the task is a synthetic steady-velocity application rather than a clinical
endpoint, the exact current cache path is unresolved, and new direct priors
occupy the general intervention-response story. The row still passes only by
0.5 points and sits exactly on the novelty floor. A failed P0 or matched P1
closes it; there is no fallback architecture narrative.

## 5. Minimal method hypothesis, not a selected architecture

If and only if P0 establishes stable endpoints and P1 observes the matched
failure, the cleanest mechanism test is:

\[
  \widehat{\mathbf{u}}(x,q)
  = \mathbf{u}(x,q_0)
  + \log(q/q_0)\,R_\theta\!\left(x,\mathcal{G},
    \mathbf{u}(\cdot,q_0),q/q_0\right).
\]

The multiplier makes the learned correction exactly zero at the reference
flow. The primary comparison changes only this output map while holding one
strong LaB-GATr backbone, information set, optimizer and compute fixed. This is
compared with:

1. the same-backbone direct target-field head;
2. a train-fitted same-case power law;
3. DeepONet and MeshGraphNet descriptive controls; and
4. derivative/sensitivity-informed controls when an exact executable
   implementation can be qualified.

The architecture is deliberately minimal. Attention, equivariance or physics
losses cannot rescue a negative mechanism test and cannot become additional
contributions.

## 6. Evidence sequence and stop rules

1. **P0—endpoint identifiability:** train-only, method-free stability of gain,
   direction and tangent on the eight-flow grid. Real status: 0/11.
2. **P1—matched failure:** same-backbone, response-blind field-error matching.
   If no response gap appears, delete the problem identity.
3. **Bounded development:** validation-only, at most two rounds and 80
   additional GPU-hours, with one registered failure hypothesis per round.
4. **One-shot confirmation:** exactly 100 new Aneumo base families, excluding
   all historical 32. Candidate must be within ±2% field error of both controls
   and improve both response endpoints against both controls by at least 10%,
   with positive bootstrap lower bounds, at least 4/5 positive seeds and at
   least 59/100 family wins.
5. **Interpretation:** identical coordinates and reference-derived colour
   limits for CFD, direct, power law and candidate; disclose candidate-worst,
   typical and best families rather than a favourable example.

No stage may be repaired after viewing its protected evidence. A failed stage
closes the exact direction.

## 7. ISBI 2027 four-page logic contract

The [official ISBI 2027 instructions](https://biomedicalimaging.org/2027/papers/)
specify single-blind review, four pages of technical content and an optional
paid fifth page restricted to ethics, acknowledgments/conflicts and references.
The deadline is 26 October 2026, 23:59 US EDT. Until P0 and P1 pass, this is a
role map rather than manuscript prose.

| Paper element | Unique role | Evidence it must point to | Delete if |
|---|---|---|---|
| Introduction paragraph 1 | Establish why repeated CFD sweeps matter and why one nominal solve is the actual information set | Aneumo source and boundary-condition literature | It drifts to rupture prediction or patient-specific physiology |
| Introduction paragraph 2 | Separate field accuracy from spatial response fidelity without claiming the generic concept | SC-FNO, interventional consistency and P1 matched failure | P1 shows no mismatch |
| Contributions | State only RF-C1 matched failure, RF-C2 same-backbone repair and RF-C3 independent-family confirmation | One evidence cell per sentence | Any cell is empty |
| Method task block | Define family unit, anchor flow, estimands and analytic control | Frozen task/metric contract | A definition is not reproducible in the result table |
| Method model block | Explain only the zero-at-anchor mechanism | Same-backbone contrast | The mechanism is not isolated or P1 direction is mixed |
| Experiments | Make leakage, matching, comparator and statistics auditable | Family manifests, compute log and raw-row evaluator | New family or completeness contract fails |
| Main table | Carry every headline quantitative claim | Field equivalence plus four comparator×endpoint cells | Any primary cell fails |
| Ablation table | Isolate identity output from backbone/capacity | Direct versus identity heads with matched backbone | It merely ranks unrelated architectures |
| Main figure | Make spatial response error interpretable | Same points/colour limits and predeclared cases | It is selected for attractiveness |
| Discussion | Bound synthetic steady-flow interpretation | Exact source limitations | It contains clinical-risk or in-vivo claims |

The logical chain is intentionally short:

> repeated-flow application → field metric insufficiency observed under a
> matched control → identity-at-anchor mechanism → superiority to learned and
> analytic controls → new-family confirmation → bounded interpretation.

Every method sentence must answer an observed failure, every result cell must
support one claim, and every limitation must block a plausible overreading.
Protocol hardening, software tests, scheduler management and model naming stay
out of the contribution list.

## 8. Operational boundary

This audit used public primary sources and existing local aggregate records.
It made no scientific-server query, transfer, PBS submission or GPU call.
`introai9` remains the only permitted future PBS execution server, with no
login-node GPU use, and it must not be retried before a verified external
service or administrator change. `junjinyong` must never be accessed, queried,
used for transfer, submitted to or monitored.
