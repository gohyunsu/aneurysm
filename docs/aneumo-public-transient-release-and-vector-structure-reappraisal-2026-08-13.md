# Aneumo public transient release and vector-structure reappraisal

> **Decision · 2026-08-13 KST:** the official source change is material enough
> to reopen *review* of transient vector WSS, but not enough to admit a task.
> The structure-faithful candidate scores **28.0/40** and remains inactive.
> The existing steady multi-flow response-fidelity direction stays the sole
> **32.5/40 conditional source lead**, with real P0 v3 still 0/12. No transient
> payload was staged, no P0 or model was selected, and no server or GPU was used.

## 1. What changed

The previous structure-faithful audit stopped at E0 because no bounded official
transient surface-vector release was identified. That premise is now outdated.
At exact official GitHub commit
[`701d53d`](https://github.com/Xigui-Li/Aneumo/tree/701d53dde3489d84dbe9bc8324254629162eb45a),
the repository describes 10,660 transient simulations, vector WSS with nominal
shape `[T,M,3]`, and transient DeepONet/FNO/U-Net/MeshGraphNet code. Exact
Hugging Face revision
[`f801ade`](https://huggingface.co/datasets/SAIS-Life-Science/Aneumo/tree/f801adee816c18d3e18b23e6fcb147fe4c264209)
is public and ungated and contains 100 `batch_*-*.zip` archives spanning case
IDs 1--1000.

This is a real source change, not a scientific result. It satisfies only the
old requirement that a material official release must appear before the
vector-structure question can be reviewed again.

## 2. What is actually in the release

The Hugging Face API reports 3,284,946,024,600 stored bytes and 370 repository
objects: 267 numeric steady ZIPs, 100 transient batch ZIPs and three metadata
files. The first transient batch is 14,530,202,660 bytes; the first steady
shard is 6,878,451,054 bytes. Therefore public availability does not imply a
small, immediately trainable asset.

To avoid a 14.5 GB download, only the final 16 MiB byte range of
`batch_1-10.zip` was requested. ZIP64 directory metadata shows ten nested case
archives. The visible central directory for case 10 contains 404 members:
101 time directories, each with inlet VTP, outlet VTP, wall VTP and internal
VTU. One directory is labelled `0.00`; the remaining 100 span `4.01`--`5.00`.
This reconciles the documented 100-cycle-step claim with an additional initial
directory, but it still does not establish array names, units, tangency,
surface connectivity or phase-to-phase correspondence. No field value was
interpreted and no complete archive was downloaded.

`Connection.csv` has 10,660 case rows. The released first 1,000 transient case
IDs map to only **40 base generation families**, with 3--30 deformations per
family. The scientific unit is therefore the base family, never the case,
phase, wall point, critical point or trajectory. “1,000 released cases” must
not be written as 1,000 independent anatomies.

## 3. Why the official benchmark is not yet a strong control

The official code is useful source material but cannot be used unchanged as a
family-generalization baseline.

- `train_cross.py` calls its split “geometry,” but trains on four deformations
  and tests on a fifth deformation from each of the same ten base families.
  Train and test therefore overlap in all ten lineage families.
- `cross_dataset.py` loads vector WSS and immediately reduces it to Euclidean
  magnitude. Every advertised cross-model target is scalar; direction,
  tangency, signed critical points and worldlines are absent.
- Evaluation reports only MSE, relative L2, MAE and MNAE. It contains no
  structure endpoint.
- One of 19 transient/baseline Python files has a syntax error in
  `baselines/evaluate_cross.py`. `train_cross.py` also declares Transolver and
  PointNet++ builders whose modules are absent from `baselines/models/`.
- Timesteps are truncated after the first WSS maximum over 100 Pa. This may be
  reasonable quality control, but it is outcome-dependent preprocessing and
  must be frozen before comparison rather than inherited silently.

These findings are not criticism for its own sake. They define the controls a
new study would need: a base-family-disjoint split, vector-valued targets,
prospective quality rules, executable baselines and structure-specific
endpoints.

## 4. Direct-prior boundary

The attractive architecture ingredients are already occupied.

- [Mesh neural networks for SE(3)-equivariant artery-wall estimation](https://arxiv.org/abs/2212.05023)
  already predict transient, directional WSS over a cardiac cycle under
  varying inflows.
- [Topology-Preserving Neural Operator Learning via Hodge Decomposition](https://openreview.net/pdf/61833afd2155326daa8f0c413eac333137902dc9.pdf)
  already binds vector fields to discrete forms and learns Hodge-structured
  operators.
- [Multilevel robustness](https://doi.org/10.1111/cgf.14799) already develops
  robust tracking and comparison of critical points in time-varying vector
  fields.
- [Time-varying vector-field compression with preserved critical-point trajectories](https://arxiv.org/abs/2510.25143)
  already targets exact worldline preservation.
- The aneurysm-specific [local hemodynamic environment study](https://doi.org/10.1002/cnm.3844)
  identifies and tracks WSS critical points over a cardiac cycle.

Thus an edge 1-form, Hodge split, equivariant GNN, periodic decoder, critical-
point extractor, worldline matcher or topology loss is a control or
implementation choice, not a contribution. The only potentially independent
application question remains:

> At matched vector-field error and compute, do transient WSS surrogates still
> disagree on robust signed critical structures and their cardiac-cycle
> worldlines, and can a minimal representation or objective correction reduce
> that disagreement without sacrificing field accuracy?

That conjunction is falsifiable, but it is not yet identified by the release.

## 5. Fresh score, without enthusiasm inflation

Axes are biomedical importance, target identifiability, residual novelty,
usable asset readiness, effective independent units, strong-baseline
feasibility, interpretable-figure value and ISBI schedule fit.

| Candidate | Axis scores | Total | Decision |
|---|---|---:|---|
| Existing steady multi-flow response fidelity | 4.0 / 5.0 / 2.5 / 4.0 / 3.0 / 5.0 / 5.0 / 4.0 | **32.5** | sole conditional lead; unchanged P0 v3 only |
| Transient structure-faithful vector-WSS surrogation | 4.5 / 3.0 / 2.5 / 3.0 / 3.0 / 3.5 / 5.0 / 3.5 | **28.0** | reject now; re-entry candidate |
| Family-disjoint scalar-WSS benchmark correction | 4.0 / 5.0 / 1.5 / 3.0 / 3.0 / 3.5 / 4.0 / 3.5 | **27.5** | reject; necessary hygiene is not novelty |
| Magnitude-to-vector direction-failure audit | 4.5 / 3.0 / 1.5 / 3.0 / 3.0 / 3.5 / 5.0 / 3.0 | **26.5** | reject; expected information loss is not a paper identity |
| New transient GNN/operator benchmark | 3.5 / 4.0 / 0.0 / 3.0 / 3.0 / 3.5 / 4.0 / 3.0 | **24.0** | reject; architecture space is direct-prior dense |

The 28.0 candidate is held back by evidence, not by lack of a fancy name.
Forty families may eventually support bounded development and a modest outer
test, but the current release has not yet established the target contract and
its provided comparison code leaks family lineage.

## 6. License and provenance stop

The exact Hugging Face card declares **CC BY-NC-ND 4.0**, whereas the GitHub
datasheet at the pinned source commit declares **CC BY 4.0** and says no
additional restrictions apply. This audit makes no legal conclusion. The
conflict must be resolved by an authoritative release statement before new
scientific activation or redistribution. Code license and upstream AneuX
license do not automatically settle the generated CFD release license.

## 7. Re-entry contract

A fresh transient score requires all of the following before a payload P0:

1. authoritative license resolution and a versioned member manifest;
2. a bounded case probe confirming wall-vector array name, three components,
   units, tangent convention, mesh connectivity and phase correspondence;
3. a frozen base-family-disjoint train/validation/test manifest;
4. method-free critical-point/worldline stability under mesh, tolerance and
   bounded perturbation changes;
5. executable compute-matched vector WSS baselines, including directional
   equivariant and Hodge/discrete-form controls.

Only after a fresh score reaches 32 may a transient P0 be registered. A P0
would establish target identifiability, not select a model. If critical
structures are unstable, too sparse, or determined by matched field error,
the direction closes without a topology-loss repair loop.

The public source change is not an `introai9` service recovery signal and does
not authorize retrying the immutable steady P0 v3. Future scientific execution
remains `introai9` PBS-only with no login-node GPU. `junjinyong` was not and
must never be accessed.
