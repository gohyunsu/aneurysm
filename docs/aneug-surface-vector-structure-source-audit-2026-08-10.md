# Time-varying surface-WSS structure source audit

**Prospective decision · 2026-08-10 KST:** a genuinely new formulation scores
**32.0/40**, exactly meeting the unchanged admission line. It is a conditional
source lead, not a selected method or paper contribution. The only authorized
execution is the registered three-case, method-free, CPU-only P0 on
`introai9`. No architecture, GPU job, outer test or submission claim is open.

This is not a repair of the closed cycle-functional reader or the rejected
target-transport batch. Those versions asked whether TAWSS/OSI/RRT were
recoverable from the processed archive and whether interpolation conserved
pointwise/vector functionals. The present problem asks a different question:

> Can a time-varying wall-shear vector field be learned as a surface object
> whose indexed critical-point structure is preserved, rather than only as
> three independently regressed Cartesian channels?

## 1. Why this is a different estimand

Wall shear stress (WSS) lives in the tangent plane of the vessel wall. A zero
of that two-dimensional tangent field can mark impingement, separation,
attachment or the end of a near-wall vortex. Over a cardiac cycle these points
appear, disappear and move. Two predictions can therefore have similar mean
relative error while describing different near-wall flow organization.

The proposed estimand has three levels:

1. the time-resolved tangent WSS 1-form on the triangular surface;
2. the signed index of isolated critical points at every phase;
3. the trajectories and birth/death events of robust critical points across
   the cycle.

The third level is not inspected in P0. P0 only tests whether the released raw
mesh and WSS tensors support deterministic per-frame indexed critical-point
extraction. A later method-free P1 would have to establish stability under
mesh, tolerance and small-field perturbations before any learning method.

## 2. Exact public-source boundary

The audit pins:

- [AneuG-Flow dataset commit `9dd4180…`](https://huggingface.co/datasets/whding123/AneuG-Flow/tree/9dd418083899deddd93a67f9a6fca7a14304fa36),
  CC BY-SA 4.0, 730 reported transient cases;
- [official code commit `4a090a0…`](https://github.com/WenHaoDing/AneuG-Flow/tree/4a090a0f12538deef6fcea88b81afe78ce38152e);
- the official raw loader contract, which reads coordinate and vector WSS
  components from each `wall_data.pt` and retains the final 80 phases;
- three lexicographically fixed public probes: `stable_0`, `stable_100` and
  `stable_10001`.

Before registration, only repository metadata, file sizes, hashes, safe-pickle
imports and source code were read. No OBJ or `.pt` body was downloaded. The
three WSS objects total 256,179,406 bytes and their three remeshed OBJ files
total 20,463,279 bytes. These are schema probes, not independent scientific
test cases and not a training subset.

## 3. Direct-prior red team

This candidate is intentionally narrower than a generic “topology-aware neural
operator.” Direct controls and threats include:

- the 2026 [Hodge Spectral Duality operator](https://arxiv.org/abs/2605.13834),
  which already learns physical fields through discrete differential forms and
  Hodge splitting;
- [SE(3)-equivariant transient WSS estimation](https://doi.org/10.1016/j.compbiomed.2024.108238)
  on arterial surface meshes;
- classical and modern time-varying vector-field critical-point tracking;
- topology-preserving compression of critical-point trajectories;
- existing aneurysm studies that extract WSS critical points and their areas
  of influence;
- conservative remapping, tangent projection, train-only normalization and
  test-blind model selection.

Therefore none of Hodge decomposition, DEC, equivariance, tangency, a
critical-point loss or clean evaluation is individually novel. Residual
novelty exists only if an operator-specific representation and guarantee link
surface 1-form error to indexed critical-point/worldline preservation, and if
it improves strong baselines without sacrificing calibrated field accuracy.

## 4. Frozen score

Each axis is 0--5. The total is not rounded or repaired.

| Axis | Score | Reason |
|---|---:|---|
| Biomedical importance | 4.5 | WSS organization describes impingement, separation and near-wall vortices, but no clinical outcome is present. |
| Identifiable estimand | 4.0 | Raw vector WSS and surface geometry can identify per-frame indices if their correspondence and tangency pass P0. |
| Residual algorithmic gap | 2.5 | Direct Hodge, equivariant and vector-topology priors are strong; only the certified operator-to-worldline link remains. |
| Asset readiness | 3.5 | Exact public raw objects exist, but the release is 2.63 TB and prior processed-object transports closed incomplete. |
| Independent-unit strength | 4.5 | 730 synthetic transient geometries are reported; generator-family independence still needs P1. |
| Strong-baseline feasibility | 5.0 | Official GHD, mesh-equivariant, Hodge and post-hoc projected controls are definable. |
| Interpretable figure value | 5.0 | Surface arrows, signed critical points and their cardiac-cycle tracks are directly visualizable. |
| ISBI schedule/runtime fit | 3.0 | Four pages and large objects are restrictive; staged raw probes keep the first decision bounded. |
| **Total** | **32.0/40** | **Conditional source admission only** |

## 5. Registered P0

[`configs/aneug_surface_vector_structure_p0.json`](../configs/aneug_surface_vector_structure_p0.json)
freezes a single `introai9` PBS CPU job: 4 CPU, 16 GB memory, GPU 0 and one hour.
It downloads only the three exact raw WSS objects and their remeshed OBJ files
into job-local temporary storage. It uses `torch.load(weights_only=True)`,
never reads blood-volume fields, GHD checkpoints, processed archives, model
weights or outer-test data, and publishes only a deidentified aggregate.

All checks are required:

1. exact bytes and pinned WSS SHA-256 / OBJ Git-blob OID;
2. safe tensor-only dictionary with the six coordinate/WSS components;
3. at least 80 finite phases and static coordinates;
4. valid triangular mesh and at least 99.9% coordinate-to-vertex mapping;
5. median/p95 normal-component ratios at most 0.05/0.25;
6. non-zero temporal WSS variation;
7. at least 5% of phases in every probe contain a non-degenerate interior
   indexed critical point;
8. no model, GPU, outer test or patient interpretation.

Pass authorizes only a separately preregistered, method-free 32-case P1 that
tests perturbation, remeshing and extraction stability. Failure or incomplete
execution closes this exact version without same-contract repair or rerun.

## 6. What would be required after P1

Even a P1 pass would not make the idea a contribution. A viable ISBI method
would still require:

- an edge-integrated surface 1-form representation rather than Cartesian
  component regression;
- an explicit index/worldline preservation statement with assumptions and a
  falsifiable bound;
- family-disjoint, validation-selected comparison with official GHD,
  equivariant mesh, Hodge and post-hoc structure controls;
- field calibration, critical-point precision/recall, signed-index error,
  trajectory distance and birth/death event metrics;
- a real-CFD external audit that is not presented as prospective rupture risk.

Until those conditions are met, the project remains not submission-ready.
