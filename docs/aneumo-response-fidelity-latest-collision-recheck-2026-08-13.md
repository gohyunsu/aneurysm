# Aneumo response-fidelity latest-collision recheck

Status: **32.5/40 conditional application/evaluation lead retained; method
novelty, model selection, execution and paper claims remain closed**  
Target: **IEEE ISBI 2027**  
Decision date: **2026-08-13 KST**

## Bottom line

Three additional 2026 sources make the boundary stricter, but they do not yet
occupy the exact aneurysm study. The direction survives only as an
**application-specific evaluation and evidence contribution**:

> At equivalent velocity-field error, do aneurysm surrogates preserve the
> same-geometry spatial response to inlet-flow change, and does a minimal
> anchor-identity adaptation improve that response beyond both a learned direct
> head and train-fitted physical scaling on independent generation families?

It does **not** survive as a new neural-operator, hard-constraint, one-anchor,
GNN or generic field-to-readout method. The source score stays 32.5/40 with
residual novelty exactly at the 2.5/5 admission floor; it does not increase.
Real P0 v3 is still 0/12, so this is not an active paper identity.

## What the new sources occupy

| Primary source | Already established | Consequence for AURORA |
|---|---|---|
| [PaNO (arXiv 2606.03038)](https://arxiv.org/abs/2606.03038) | In photonics, low global field error can coexist with poor localized readout and model ranking; a mediator/readout-aligned operator improves the downstream endpoint. It is a June 2026 preprint, not treated as peer-reviewed ISBI evidence. | “Accurate fields can mislead downstream use” and a generic field→mediator→readout story are occupied. AURORA must name and validate an aneurysm-specific response estimand under matched field error. |
| [NOEM, Nature Computational Science 2026](https://doi.org/10.1038/s43588-026-00974-2) | Neural-operator outputs can be transformed to satisfy constraints exactly. The paper explicitly formulates hard-constraint operators. | Multiplying a residual by a function that vanishes at an anchor is not method novelty. It is only a controlled mechanism test. |
| [Differentiable cardiovascular boundary-condition tuning, Annals of Biomedical Engineering 2026](https://doi.org/10.1007/s10439-026-04269-5) | One high-fidelity 3D CFD solve can calibrate a differentiable reduced-order model for repeated cardiovascular boundary-condition tuning. | “One reference simulation enables many boundary-condition evaluations” is not an application novelty by itself. AURORA must contribute spatial response fidelity on aneurysm fields, not the sweep scenario. |

These sources join the already mandatory boundaries: Aneumo multi-flow
benchmarks, NeurIPS interventional consistency, SC-FNO/DINO/DIFNO sensitivity
learning, DeltaPhi residual learning, Hemo-MPO/AB-GATr equivariant Aneumo
surrogation, transient aneurysm GNNs and vessel-dilation response surrogation.

## Why the score is retained rather than raised or closed

The exact remaining conjunction is not reported by the inspected sources:

1. **Aneurysm-specific matched failure.** Models are compared only after
   bilateral field-error equivalence; response error cannot be explained by a
   more accurate field.
2. **Two non-negotiable controls.** The candidate must beat both a
   same-backbone learned direct head and a train-fitted same-case power law.
3. **Application-specific estimands.** Paired spatial response and flow-grid
   tangent are evaluated with generation family as the independent unit.
4. **Independent-family confirmation.** Exactly 100 new base families exclude
   all historical 32 and require mean, seed and prevalence evidence.

That combination can support a focused ISBI application paper if the effects
are large and interpretable. It cannot support a broad method claim. If the
paper can be summarized without the words *Aneumo*, *matched field error*,
*analytic scaling* and *independent family*, its residual novelty falls below
the fixed floor and the direction must be rejected.

## Claim grammar after the recheck

| Cell | Permitted role after evidence | Prohibited wording |
|---|---|---|
| RF-C1 | First aneurysm-specific matched audit showing a material spatial-response failure under equivalent field accuracy | First demonstration that field accuracy can mislead downstream use |
| RF-C2 | Controlled effectiveness of an anchor-identity adaptation against learned direct and analytic controls | Novel hard-constraint operator, novel residual architecture, or novel GNN |
| RF-C3 | Independent-family confirmation with a complete, prevalence-aware estimator | Clinical validation, patient-level generalization, or new-dataset contribution |

RF-C2 is an **application solution**, not an algorithmic novelty claim. No
method name is warranted. A response-aware loss, a graph backbone or an exact
anchor may be used only when the observed failure requires it and the ablation
isolates it.

## Acceptance-oriented falsifiers

The direction is closed rather than rhetorically repaired if any condition
below fails.

1. P0 does not pass all 12 method-free stability checks.
2. A newly registered P1 does not expose a material response gap at matched
   field error.
3. Candidate gains disappear against either the learned-direct or power-law
   control.
4. Field error regresses outside the frozen bilateral equivalence band.
5. Confirmation is driven by a minority of families or fails a co-primary
   endpoint.
6. Qualitative panels cannot show the failure and correction under identical
   coordinates and reference-derived display limits.
7. The discussion needs rupture, patient-specific physiology, clinical utility
   or in-vivo validity to sound important.

Strong results under all seven conditions would make the study plausibly
competitive as a concise ISBI application/evaluation contribution. They would
not turn the output transform or GNN into a new general method.

## Current operational boundary

This recheck used public primary sources and existing aggregate records only.
It made no scientific-server or scheduler query, transfer, PBS/GPU submission,
cache-field read or monitoring action. The exact private cache identity is
known, but current execution remains locked: no verified external operational
change, no activation manifest and no current container-readability verdict.
Do not retry `introai9` or open a local scientific repair loop until that
external condition changes. Never access, query, transfer to, submit on or
monitor `junjinyong`.
