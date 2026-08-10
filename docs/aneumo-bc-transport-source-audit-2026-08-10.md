# Aneumo anchor-conditioned boundary-transport source audit

**Frozen source decision · 2026-08-10 KST:** one fresh problem scores
**33.5/40** and may open exactly one method-free, train-family-only CPU P0 on
`introai9`. It is not a selected method, architecture, result, contribution or
GPU authorization.

## 1. Why this is a different question

The closed Aneumo V1/V1e branches tried to infer an absolute velocity field from
geometry and a scalar flow condition. They failed prospectively. The strongest
boundary-aware V1e model had worst-seed train/validation full-field relative L2
of 0.77221/0.87796 and response L2 of 0.94918. In the fixed-checkpoint
attribution, however, a non-deployable same-case anchor-field power control had
response relative L2 0.20951 on train and 0.22794 on validation. This does not
rescue V1/V1e. It says that the realistic learnability question is different:

> Given one CFD solution on a vascular geometry at flow rate (q_0), can a
> model transport that solution to another observed flow rate (q), while
> preserving identity at (q=q_0) and path consistency across flow-rate
> ratios?

This is a one-solve scenario-sweep problem. It does not claim geometry-only
hemodynamics, missing patient boundary conditions, prospective rupture risk or
clinical deployment. A new geometry still requires one anchor simulation.

## 2. Observable source contract

The official Aneumo release is pinned at Hugging Face commit
`f801adee816c18d3e18b23e6fcb147fe4c264209`; the upstream mapping/code is pinned
at `701d53dde3489d84dbe9bc8324254629162eb45a`. The selective ZIP64 reader was
previously verified to reject ignored byte ranges, verify central/local records
and CRC32, and read the seven-column arrays as xyz, pressure and velocity.

The historical compact pilot defines 32 independent AneuX base families, two
deformations per family and eight steady mass-flow conditions
`0.001--0.004 kg/s`. Train/validation/test are disjoint by base family. This
audit does not change that split or inspect a test field.

The fresh P0 is narrower than model development. It reads only historical train
base family 1, cases 1 and 2, from `1.zip`; checks all eight aligned conditions;
samples 1,024 nodes deterministically; ignores pressure; emits aggregate
semantics only; and persists no field cache. It uses CPU 2, 8 GB, GPU 0 and a
45-minute PBS allocation. A pass opens only a separately preregistered,
train-only P1 task-adequacy audit.

## 3. Direct-prior red team

The following are mandatory controls rather than novelty:

- [DeltaPhi](https://proceedings.neurips.cc/paper_files/paper/2025/hash/12bf28fb68f295f855a5bf0c5a217d6e-Abstract-Conference.html)
  already learns residuals between similar physical states in data-limited PDE
  solving.
- [Scale-Consistent Learning](https://openreview.net/forum?id=9nt0jI0Dp2)
  already constructs scale-informed neural operators and consistency losses
  across PDE scales and Reynolds numbers.
- [Learned function extensions](https://arxiv.org/abs/2602.04923) explicitly
  condition neural operators on varying boundary data.
- Boundary-embedded operators, generalized boundary transfer, parametric neural
  operators, dimensionless inputs, power-law normalization, paired response
  losses and generic semigroup/cycle consistency are prior art or controls.
- The AneuG-Flow/RHSIA transient WSS task, geometry-aware PointNet surrogates and
  the failed AURORA conditional-density route remain direct evidence.

The residual question is therefore not “does residual learning work?” It is
whether a multiplicative **condition orbit** on an irregular vascular field can
be represented as anchor-conditioned transport with an exact identity route,
ratio-composition diagnostics and family-disjoint functional accuracy beyond a
strong analytic similarity control. Only a positive P1 and prospective
compute-matched superiority can turn that intersection into a method claim.

## 4. Frozen six-candidate screen

Axes are 0--5 for biomedical importance, target identifiability, residual gap,
asset readiness, effective independent units, strong-baseline feasibility,
interpretable-figure value and ISBI schedule feasibility.

| Rank | Candidate | Importance | Identifiable | Residual | Asset | Units | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Similarity-quotiented anchor-conditioned BC transport | 4.5 | 5.0 | 2.0 | 5.0 | 3.0 | 5.0 | 5.0 | 4.0 | **33.5** | conditional source lead; P0 only |
| 2 | Generic anchor-state residual operator | 4.5 | 5.0 | 0.5 | 5.0 | 3.0 | 5.0 | 5.0 | 3.5 | **31.5** | reject; DeltaPhi directly occupies it |
| 3 | Scale-informed geometry-to-field operator | 4.5 | 4.0 | 0.5 | 5.0 | 3.0 | 5.0 | 5.0 | 4.0 | **31.0** | reject; scale-consistent operator prior |
| 4 | Conformal selective CFD referral | 4.5 | 4.5 | 0.5 | 5.0 | 3.0 | 5.0 | 4.5 | 4.0 | **31.0** | reject; generic functional UQ/referral |
| 5 | Boundary-aware absolute-field operator | 4.0 | 5.0 | 0.0 | 5.0 | 3.0 | 5.0 | 5.0 | 4.0 | **31.0** | reject; V1e failed and direct priors exist |
| 6 | Joint missing-BC density/operator | 4.5 | 3.0 | 0.0 | 5.0 | 3.0 | 5.0 | 4.5 | 3.5 | **28.5** | reject; N1c failed and arbitrary conditioning is prior |

The 33.5 score is not method novelty. Asset and target identifiability carry the
candidate above the source line; the residual-gap score remains only 2/5.

## 5. Prospective P0 kill rules

The exact contract is `configs/aneumo_bc_transport_p0.json`. All checks must
pass:

1. public source and upstream commits are exact;
2. only the registered historical train family/cases are accessed;
3. all 16 required members exist and pass ZIP/CRC validation;
4. each array is finite, two-dimensional and has seven columns;
5. coordinates are bit-identical across the eight conditions of each case;
6. sampled velocity fields are finite and non-degenerate;
7. every non-anchor response has non-zero energy;
8. the fixed analytic power control is exactly identity at the anchor and has
   finite aggregate response error;
9. pressure, validation, test, morphology/status, model, checkpoint and GPU
   access remain zero.

Failure or execution-incomplete closes this exact P0 without same-contract
repair. Pass opens P1 only. P1 must use development families only to quantify
how much nonlinear departure remains after the analytic control, whether it is
stable across deformations, and whether a detectable margin over DeltaPhi and
scale-consistent controls exists. No architecture is named before that result.

## 6. Execution boundary

The only allowed server is `introai9` through PBS. `junjinyong` is excluded from
connection, query, transfer, submission and monitoring. Login-node GPU commands
are prohibited. The observed `introai9` scheduler list was empty immediately
before registration; that fact is operational provenance, not scientific
evidence.
