# Measurement-functional inverse-flow source-delta audit

> **Frozen decision · 2026-08-11 KST:** a new direct prior materially narrows
> the inverse-flow branch. Six exact formulations were scored together under
> the unchanged eight-axis rubric. The strongest,
> `benchanxplore_transient_measurement_to_functional_posterior`, scores
> **30.0/40**, below the automatic 32-point source-admission line. All six are
> rejected. No new payload, split, P0, model, architecture, server query, PBS
> job, GPU job, outer test, result row or paper contribution is authorized.

## 1. What changed

[Gormezano and Shadden (2026)](https://arxiv.org/abs/2607.20224) now directly
formulate vascular flow reconstruction from noisy, under-resolved velocity
observations with unknown inlet and outlet conditions. Their Bayesian finite-
element regression uses Taylor--Hood velocity/pressure bases, a physics-based
maximum-entropy prior, exact no-slip walls, analytical pressure elimination and
a Laplace posterior. It propagates uncertainty to pressure drop, flow, and WSS,
and evaluates one cerebral-aneurysm, one aortic-aneurysm and one coarctation
geometry against interpolation and a PINN.

This does not make transient learned inverse flow unimportant. It does mean that
the following are no longer residual novelty by themselves:

- sparse or noisy velocity observations as input;
- unknown boundary conditions treated probabilistically;
- physics-constrained velocity and pressure reconstruction;
- exact wall constraints;
- a posterior or uncertainty head; and
- propagating that posterior to WSS or other scalar functionals.

The arXiv record does not expose an associated code or data release. Its three
synthetic-CFD geometries therefore define a strong method baseline, not a usable
multi-geometry confirmation asset. A learned method would need a genuinely
different failure mechanism—most plausibly transient amortization under an
acquisition model—and independent evidence that it preserves a registered
functional without sacrificing field accuracy.

## 2. Frozen candidate screen

Each axis is scored from 0 to 5 in the fixed order: biomedical-imaging
importance, target identifiability, residual gap after direct prior work, usable
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value, and ISBI-schedule feasibility. Totals are arithmetic
sums; they are not rounded, renamed, or reweighted after the decision.

| Candidate | Importance | Identifiability | Residual gap | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BenchAnXplore transient measurement-to-functional posterior | 5.0 | 3.0 | 1.5 | 4.5 | 2.5 | 5.0 | 5.0 | 3.5 | **30.0** | reject |
| In-vitro cross-physics functional calibration | 4.5 | 4.5 | 1.5 | 4.0 | 0.5 | 5.0 | 5.0 | 4.0 | **29.0** | reject |
| Device-state posterior WSS reconstruction | 5.0 | 3.0 | 1.5 | 5.0 | 0.5 | 5.0 | 5.0 | 3.0 | **28.0** | reject |
| Amortized exact-boundary Bayesian FER across geometries | 5.0 | 5.0 | 1.0 | 1.5 | 1.5 | 5.0 | 4.5 | 3.0 | **26.5** | reject |
| FlowMRI cerebrovascular k-space-to-WSS/pressure posterior | 5.0 | 1.5 | 1.5 | 4.0 | 1.0 | 5.0 | 5.0 | 3.0 | **26.0** | reject |
| CMRx functional-risk reconstruction | 5.0 | 2.0 | 1.0 | 1.0 | 5.0 | 5.0 | 5.0 | 1.0 | **25.0** | reject |

The 30.0 row is the current best of this evidence version, not an invitation to
add two points through an architecture name or a simulated metric.

## 3. Why the strongest open CFD asset still falls short

[BenchAnXplore](https://www.nature.com/articles/s41746-026-02404-z) provides 105
semi-idealized aneurysm geometries and 80 transient velocity frames per case.
It is a valuable controlled benchmark. The original high-resolution CFD used
wall-refined meshes, while the released learning benchmark was remeshed to fewer
than 25,000 nodes and approximately 120,000 tetrahedra for tractable training.

Three limitations prevent a confirmatory inverse-functional paper now:

1. **The current decoded contract is velocity-only.** AURORA's registered
   compact loader observes coordinates, tetrahedra, 80 velocity vectors and a
   repeated boundary mask. It has not established pressure, surface WSS, units
   and a wall-gradient reference in the compact contract. Differentiating a
   coarse velocity field at the wall is not a substitute for registered WSS
   ground truth.
2. **The parent context is shared.** The aneurysm bulges are derived from real
   shapes, but they are mounted on a common idealized parent vessel. The 105
   cases therefore provide shape variation, not 105 independent clinical
   acquisition protocols, parent anatomies or boundary-condition laws.
3. **The benchmark is no longer fresh for learned selection.** All 105 cases
   were already used in AURORA's D0/D0b temporal-representation work. A learned
   comparison on the same cases would be exploratory; it cannot be presented as
   a fresh confirmatory test.

The existing physics-constrained MeshGraphNet paper also owns the obvious
geometry-plus-inflow transient velocity baseline. A probabilistic decoder,
masked-node encoder, GNN, Transformer, neural operator or functional loss does
not repair these three evidence limits.

## 4. Why the open measurement branches do not rescue the task

### 4.1 FlowMRI-Net source

The official [ETH dataset](https://doi.org/10.3929/ethz-b-000705347) is open
under CC BY-SA 4.0. The associated
[FlowMRI-Net paper](https://www.journalofcmr.com/article/S1097-6647%2825%2900075-4/fulltext)
already uses self-supervised complex-valued recurrent unrolling and joint
velocity-encoding information. Its cerebrovascular cohort has ten healthy
volunteers, split nine for training and one for testing; only that one test
volunteer has the hour-long two-fold GRAPPA reference acquisition. This can
support reconstruction feasibility, not a population claim about calibrated
aneurysm WSS or pressure.

[Cerebrovascular super-resolution plus pressure estimation](https://doi.org/10.1016/j.media.2023.102831)
already combines learned resolution enhancement with physics-informed relative
pressure inference. [VAST](https://arxiv.org/abs/2601.13393) already combines
intracranial segmentation, phase unwrapping, outlier correction, low-rank
denoising and continuity constraints. Unrolling, super-resolution, divergence
control, pressure recovery and uncertainty are therefore controls, not a new
identity.

No FlowMRI payload was downloaded for this audit. Open licensing does not
change the effective reference unit or create WSS ground truth.

### 4.2 CMRx4DFlow2026

The [official challenge data page](https://cmrx.chihucloud.com/2026/data.html)
reports more than 400 cases, including 138 fully sampled training cases and
dedicated new-site and cross-anatomy tasks. The official
[join page](https://cmrx.chihucloud.com/2026/join-the-challenge.html) states that
independent research use begins only after the December 2026 embargo, later than
the frozen 26 October 2026 ISBI deadline. The challenge itself already owns
high-acceleration reconstruction, resource-limited inference and domain
generalization. AURORA does not join the challenge, accept terms, or access its
data on the team's behalf.

### 4.3 Physical and device examples

The Minnesota [giant-aneurysm in-vitro record](https://doi.org/10.13020/D6WX0S)
provides velocity, pressure and WSS over a cardiac cycle, but represents one
physical replica. The public dual-VENC flow-diverter source contains untreated
and device states derived from one paraophthalmic anatomy. Frames, repeated
scans and device configurations are not independent aneurysm geometries.
Both sources have excellent figure value and could become qualitative external
interpretation panels after a method exists; neither can carry fresh
multi-geometry confirmation.

## 5. Consequence for the surface-vector hypothesis

This audit neither rejects nor activates the surface-vector question. It
clarifies a separate boundary:

- a **measurement-conditioned inverse-flow posterior** is now more directly
  occupied than the surface 1-form/index/worldline endpoint;
- conversely, the current surface-vector asset failure is not repaired by a
  volume-velocity or k-space dataset that lacks registered phase-resolved WSS
  topology;
- Hodge decomposition, equivariance, tangency and critical-point losses remain
  candidate components only, not approved architecture or novelty.

The surface-vector formulation therefore remains the better *inactive
hypothesis*, but it still lacks E0 task identifiability and cannot be promoted
to paper identity. The most honest current comparison is “promising question
with no admissible experiment,” not “selected GNN architecture.”

## 6. Frozen decision and next boundary

- Preserve the historical surface-vector 32.0/40 score and its exact
  execution-incomplete P0 outcome. Do not repair or rerun it.
- Preserve the earlier acquisition-flow and partial-observation scores as
  decisions on their own evidence versions. This audit adds a new direct-prior
  correction; it does not rewrite history.
- Reject all six formulations in this batch. Do not access new payload, define
  a split, register P0/P1, select a method or architecture, or run GPU work.
- A new version requires a material asset that supplies phase-resolved
  reference functionals or WSS vectors, a reproducible acquisition operator,
  and enough independent geometries for family-disjoint confirmation. Merely
  deriving noisy observations from the already-used 105 cases is not new
  evidence.
- No server was queried and no job was created. Any later gate-authorized work
  uses PBS on `introai9` only. `junjinyong` remains prohibited for connection,
  query, transfer, submission and monitoring.
