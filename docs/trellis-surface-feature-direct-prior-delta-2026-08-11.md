# TRELLIS surface-feature direct-prior delta · 2026-08-11

> **Decision · schema 7.6:** This is a direct-prior correction, not a new
> candidate, source-score repair or surface-vector re-entry. A 2026 paper has
> already augmented aneurysm point/mesh models with 1,024-dimensional features
> from a general-purpose 3D foundation model and reports lower AnXplore rollout
> error. Generic foundation-surface features, rendering-based geometric
> pretraining and feature concatenation are therefore controls rather than
> AURORA novelty. The paper does not evaluate transient surface-WSS critical
> points or worldlines, and its stated code URL returned HTTP 404 on
> 2026-08-11. The inactive surface-vector hypothesis and every zero-
> authorization boundary remain unchanged.

## 1. Why this paper matters

[TRELLIS-Enhanced Surface Features for Comprehensive Intracranial Aneurysm
Analysis](https://doi.org/10.1016/j.neuri.2026.100259), also available as
[arXiv:2509.03095](https://arxiv.org/abs/2509.03095), is closer to the proposed
architecture than a generic 3D-foundation-model citation. It uses the TRELLIS
encoder on IntrA and AnXplore surfaces, then adds the extracted features to
PointNet/PointNet++ and a mesh GNN for blood-flow simulation.

The source manuscript reports the following exact boundary:

- AnXplore contains 101 aneurysm models extracted from IntrA and placed on one
  common uniform parent vessel; the aneurysm sacs vary in shape and size;
- TRELLIS was pretrained on 500,000 non-medical 3D assets and returns a
  1,024-dimensional token per active surface voxel;
- each object is rendered from 200 views, voxelized on a (64^3) grid with
  roughly 5,000 active voxels, and encoded with DINOv2-conditioned sparse VAE
  features;
- the hemodynamic experiment leaves the cited GNN core unchanged and adds
  TRELLIS features extracted from the first simulation time step;
- five runs with and five runs without the features are reported for different
  model sizes;
- all-rollout RMSE changes from 7.57 to 6.09 for S/1 and from 4.03 to 3.55 for
  L/1. The paper summarizes this as approximately 15% lower simulation error.

This is real evidence that off-domain 3D representations can improve a
geometry-conditioned aneurysm flow surrogate. It means that a foundation
surface encoder, a large geometric descriptor, or simple feature concatenation
cannot be presented as an independent contribution.

## 2. What it does not establish

The source does **not** validate AURORA's retained structural hypothesis.

1. The AnXplore description is volumetric blood-flow simulation. The reported
   GNN table uses all-rollout RMSE and does not report transient tangent WSS,
   triangle-interior critical points, signed index, trajectories or
   birth/death events.
2. All 101 aneurysm sacs share one uniform parent-vessel context. This is not a
   patient- or generator-family-disjoint test of vascular context.
3. The paper does not state an independent sealed GNN split in the inspected
   source. Five training runs are not five independent geometry cohorts.
4. The paper itself shows that TRELLIS separates IntrA and AnXplore in feature
   space, indicating strong dataset/context encoding. That separation is not
   evidence of clinically transportable vascular semantics.
5. The manuscript says code is public at
   `https://github.com/clementhrv/trellis_for_intra`, but the GitHub repository
   API returned HTTP 404 and exact repository search returned zero matches on
   2026-08-11. A faithful executable baseline is therefore not currently
   verified from that URL.

The paper is consequently a **methodological direct prior with an unavailable
stated implementation**, not a new public phase-resolved WSS asset and not an
outer test.

## 3. Consequence for the surface-vector direction

The retained hypothesis remains:

> Field-error-matched transient-WSS surrogates may disagree on robust signed
> critical points and cardiac-cycle worldlines.

TRELLIS narrows how that hypothesis may later be tested:

- add raw Cartesian/tangent features and a foundation-surface-feature control
  to the representation baseline family if a faithful implementation becomes
  available;
- match data, parameters, training compute and field error before comparing
  structural endpoints;
- do not credit a pretrained encoder, extra feature width or rendering budget
  as the cause of structure preservation;
- stratify by parent-vessel or generator family, not by mesh, phase, vertex or
  critical point;
- retain the residual contribution boundary: an operator-specific relation
  between surface representation error and stable index/worldline fidelity,
  plus prospective field-noninferior and structure-superior evidence.

This also prevents an overreaction. TRELLIS does not make edge 1-forms or
critical-flow structure useless; it makes generic 3D representation transfer a
stronger control. The surface-vector question is still scientifically distinct
because the direct prior optimizes rollout RMSE rather than topology of the
tangent WSS field.

## 4. Frozen operational boundary

- No candidate was rescored and the historical 32.0/40 surface-vector score is
  unchanged.
- The closed job `115645.ECE-util1` remains execution-incomplete with 0/10
  scientific checks evaluated; it is not repaired or rerun.
- No medical payload, TRELLIS checkpoint, repository clone, P0, P1, method,
  architecture, server query, PBS/GPU job, outer test, result row or paper
  contribution is created.
- The next executable surface-vector version still requires a material
  phase-resolved WSS source/asset change and must begin at E0/E1, not with a
  foundation encoder.
- Any later authorized execution uses `introai9` PBS only. Never connect,
  query, transfer, submit to or monitor `junjinyong`.

