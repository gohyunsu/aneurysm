# Expert virtual-removal pair source-delta audit

> **Decision · 2026-08-11 KST:** A public paired surface asset materially
> corrects one premise of the historical inverse-editing audit, but does not
> identify a biological healthy counterfactual and does not satisfy the
> surface-vector E0 gate. The fresh formulation scores **28.5/40**, below the
> unchanged 32/40 admission line. Active shortlist, payload access, P0, method,
> architecture, GPU, outer test and paper contribution remain zero.

## 1. The correction that must be made

The historical audit correctly rejected the available Aneumo and IntrA assets
as observed healthy--pathological pairs. It was too broad, however, to leave the
impression that no public expert-created removal pair exists anywhere.

[Figshare record 1159108, version 3](https://doi.org/10.6084/m9.figshare.1159108.v3)
contains 30 VTP files with checksums and a total registered size of 163,634,666
bytes:

- ten `case##_aneurysm.vtp` pathological surfaces;
- ten corresponding `case##.vtp` surfaces after virtual aneurysm removal; and
- ten `control##.vtp` matched control surfaces.

The canonical SHA-256 of the sorted `(name, size, computed_md5)` manifest is
`875cc1f92f586ab4c9fba8b28180b57fa2c2e58657c6a98c2fb98e128e04a2fb`.

The associated primary study states that ten ACA-A1 aneurysm cases were paired
with ten controls and that the aneurysms were virtually removed to *mimic* the
pre-aneurysm geometry. The study also reports a second-observer sensitivity
analysis and a 20% inflow perturbation. The public record's 30-file manifest,
however, exposes one removal surface per case and does not expose a separately
named second-observer removal pair.

This is a real source delta. It creates an expert virtual-removal target that was
not represented in the old source account. It does **not** turn a reconstructed
surface into the same patient's observed pre-disease anatomy.

## 2. What the pair identifies—and what it does not

Let (Y_i) be the pathological surface and \(\tilde H_i^{(r)}\) the surface
produced by removal rule or reader \(r\). The release can support comparison to
one observed expert construction,

\[
  \hat H_i(Y_i) \quad\text{versus}\quad \tilde H_i^{(1)},
\]

for ten cases. It cannot identify error to an unobserved biological state
\(H_i^*\):

\[
  H_i^* \ne \tilde H_i^{(1)} \quad\text{by assumption or by observation.}
\]

Consequently, the defensible target is **expert virtual-removal emulation or
uncertainty**, not disease reversal, causal aneurysm initiation, or recovery of
the patient's true healthy vessel. Forward reconstruction consistency can test
self-consistency with an editor; it cannot validate the missing biological
counterfactual.

The independent paired unit is ten cases. Vertices, triangles, sampled surface
points and augmented removals are not additional patients. The ten matched
controls help characterize a population reference but are not same-patient
counterfactuals.

## 3. Asset and license boundary

Only the official metadata and file manifest were read. No VTP payload was
downloaded or parsed.

The record has a material license inconsistency:

- the Figshare API's top-level license object says **CC BY 4.0**;
- the record description says **CC BY-NC 3.0**, limits use to bona fide
  researchers under an MRC data-sharing definition, and asks uncertain users to
  contact the data owner.

The stricter descriptive terms govern this audit until the data owner or
repository clarifies the conflict. Metadata availability is not treated as
permission to download or redistribute patient-derived surface payload.

## 4. Direct-prior pressure

| Occupied capability | Direct source | Consequence |
|---|---|---|
| Virtual removal and hemodynamic analysis | [Geers et al., 2017](https://doi.org/10.1007/s10237-016-0804-3) | The released pair was created for, and already used in, WSS magnitude, gradient, directionality and pulsatility analysis. |
| Healthy vessel generation and localized aneurysm editing | [SynVA](https://arxiv.org/abs/2605.17620) | Healthy generation, ostium selection, aneurysm synthesis and a claimed 50,000-mesh synthetic release make a generic forward editor non-novel. The audited arXiv HTML did not expose a dedicated SynVA code or dataset landing link, so the claimed release is not counted as an executable asset here. |
| Aneurysm-conditioned surface generation | [AneuG, MICCAI 2025](https://papers.miccai.org/miccai-2025/paper/1474_paper.pdf) | A GHD/VAE/mesh generator conditioned on morphology or vessel context is a direct baseline. |
| Aneurysm and parent-vessel point completion | [MSENet / IntrACompletion](https://doi.org/10.3390/cells11244107) | Point-cloud completion of idealized aneurysm and healthy-vessel surfaces is already directly evaluated. |
| Automatic aneurysm/neck isolation | [AneuSI](https://doi.org/10.1016/j.cmpb.2026.109525) | Automatic surface isolation is preprocessing or a control, not a contribution. |
| Generic healthy reconstruction and anomaly localization | [TMI counterfactual anomaly detection](https://pubmed.ncbi.nlm.nih.gov/39269801/) | Reconstruction residuals, uncertainty maps and cycle losses are not independently novel. |

The only plausible residual question is whether a probabilistic inverse vascular
editor can represent **reader-defined removal ambiguity** and generalize beyond
the ten released constructions. The release does not provide the reader
distribution needed to evaluate that question, and the direct method space is
already dense.

## 5. Frozen source score

Each axis is scored 0--5 against assets and evidence available now, not data that
could later be created.

| Axis | Score | Reason |
|---|---:|---|
| Biomedical-imaging importance | 4.5 | Parent-vessel reconstruction and aneurysm-neck interpretation are relevant, although the input is a derived surface rather than the image. |
| Target identifiability | 3.0 | One expert construction is observable, but biological healthy anatomy and reader uncertainty are not. |
| Residual gap after direct prior | 1.5 | Forward editing, completion, isolation and counterfactual reconstruction already occupy nearly all architectural ingredients. |
| Asset readiness | 3.5 | Exact files, sizes and checksums are public, but the license statements conflict and payload use was not authorized. |
| Independent unit | 1.5 | The paired evaluation unit is only ten cases from one ACA-A1 location pattern. |
| Strong-baseline feasibility | 5.0 | Classical removal, surface completion, SynVA/AneuG and counterfactual baselines are clear. |
| Interpretable figure | 5.0 | Pathological, removed and control surfaces make a strong same-view triptych. |
| ISBI schedule feasibility | 4.5 | A small surface study is computable, but no amount of compute fixes the target and sample-size limits. |

Total: **28.5/40**. The unchanged automatic admission line is 32.0. The score is
not rounded up and the formulation is rejected before payload or executable P0.

## 6. Relation to the surface-vector hypothesis

This release is **not** a material surface-vector E0 asset. It provides geometry,
not a phase-resolved tangent WSS field with units, orientation, boundary
conditions, geometry--field correspondence and independent families. It cannot
repair or rerun the closed AneuG surface-vector P0, and it creates no permission
for edge-1-form, Hodge, equivariant, temporal or structural-loss development.

The surface-vector hypothesis therefore remains inactive. Its next admissible
step is still a genuinely new, licensed field asset followed by method-free
structure-stability and field-error-matched failure-mechanism gates.

## 7. Frozen decision

- Preserve the historical inverse-editing 27.0/40 decision as the judgment on
  its then-audited Aneumo/IntrA formulation; do not rewrite it as a pass.
- Record this Figshare pair as a new evidence version and reject it at 28.5/40.
- Do not download VTP payload until the license conflict and intended use are
  explicitly resolved; such clarification would authorize only a fresh asset
  audit, not a model.
- Do not create a P0, split, method, architecture, checkpoint, GPU job, outer
  test, result row or numbered paper contribution.
- Continue fresh problem/source search. Any later eligible execution remains
  PBS-scheduled on `introai9` only. No server was queried or job created for this
  audit, and `junjinyong` remains prohibited for every AURORA action.
