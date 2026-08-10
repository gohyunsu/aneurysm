# AneuG-Flow target-construction and evaluation audit

**Frozen decision · 2026-08-10 KST:** six formulations were scored from
official paper, code and repository metadata before any field payload, model or
GPU access. The best formulation scores **31.5/40**, below the unchanged
32-point admission line. All six are rejected. Active shortlist, primary
problem, P0, method, architecture, PBS/GPU job, outer test and paper
contribution remain zero.

This is not a repair or rerun of the closed cycle-functional WSS P0. That older
candidate asked whether transient fields support TAWSS/OSI/RRT prediction. This
audit asks a logically earlier question: **are the registered surface targets
and the published evaluation path suitable foundations for a new method?**

## 1. Why target construction matters

Wall shear stress (WSS) is a vector attached to the vessel wall. It therefore
has more structure than an ordinary three-channel image:

- its vector should lie in the local tangent plane rather than point through
  the wall;
- its area-weighted integral, high-WSS regions and derived quantities should
  not change arbitrarily when the mesh is replaced;
- vertex coordinates, face connectivity, normals and WSS must describe the
  same oriented surface;
- train normalization and model selection must not read information from the
  held-out test set.

For a beginner, the key analogy is moving wind arrows from one curved globe to
another. Copying nearby arrow components may create arrows that point into the
globe or change the total wind energy. A lower neural-network error cannot
repair a structurally inconsistent target.

## 2. Exact public-source boundary

The audit pins the following official versions:

- [NeurIPS 2025 dataset paper](https://papers.neurips.cc/paper_files/paper/2025/file/e2b8ff0035bc9f572a7deefbcbea85bc-Paper-Datasets_and_Benchmarks_Track.pdf),
  which reports 14,000 steady and 730 transient cases;
- [official code commit `4a090a0…`](https://github.com/WenHaoDing/AneuG-Flow/tree/4a090a0f12538deef6fcea88b81afe78ce38152e);
- [official Hugging Face dataset commit `9dd4180…`](https://huggingface.co/datasets/whding123/AneuG-Flow/tree/9dd418083899deddd93a67f9a6fca7a14304fa36).

Only public paper text, source code and repository metadata were inspected. No
large `.pt` field, OBJ mesh body, external GHD checkpoint or model weight was
downloaded. Repository metadata confirms that even a single public case can
contain a 3.60 GB blood-field object and an approximately 79.5 MB wall-field
object, so source plausibility must precede payload transfer.

## 3. What the official implementation establishes

### 3.1 Registration is `k=3` interpolation, not a physical transfer guarantee

In `new_version/loaders.py`, both steady and transient registration use
`torch_geometric.nn.unpool.knn_interpolate(..., k=3)`. Coordinates and WSS are
interpolated together. The interpolated coordinates replace the canonical
vertices while canonical common connectivity is retained, and normals are then
recomputed on that coordinate/connectivity pair.

The inspected path contains no explicit post-transfer projection of WSS onto
the new tangent plane and no area-, integral-, extrema- or functional-
conservation constraint. This does **not** prove that released targets are
wrong; it identifies an unverified target-construction property.

### 3.2 The official evaluation path is not confirmatory as written

The steady processed tensor is normalized before a random train/test split.
The training path computes its representation/statistics from the registered
steady collection before that split. The trainer evaluates `test_loader` every
epoch and saves the best checkpoint using test MSE. The transient loader also
uses ordered prefix matching to form its split.

These observations make a strictly train-only normalization, family-disjoint
split and validation-selected checkpoint mandatory controls. They do not by
themselves create a novel learning algorithm.

### 3.3 The public registered target is useful but not self-certifying

The paper's reported registered-WSS baseline error of 4.67% is meaningful only
conditional on the target construction and evaluation contract. An audit would
need to separate:

1. interpolation error from surrogate-model error;
2. scalar magnitude error from vector tangency/orientation error;
3. pointwise error from area-weighted and hotspot-functional error;
4. random-case performance from unseen-family performance;
5. validation-selected performance from test-selected performance.

## 4. Direct prior and control lineage

The residual gap is smaller than it first appears:

- [Farrell et al., conservative interpolation between unstructured meshes](https://doi.org/10.1016/j.cma.2009.03.004)
  establishes conservative supermesh transfer;
- [Optimal Transport Neural Operator](https://jmlr.org/papers/v26/25-1380.html)
  handles varying geometries through transport-based alignment;
- [Conservation-law neural operators](https://proceedings.mlr.press/v235/liu24p.html)
  make conserved quantities an explicit operator-learning constraint;
- tangent projection/parallel transport for surface vector fields, train-only
  preprocessing, validation-only checkpoint selection and family-disjoint
  evaluation are established mathematical or experimental controls.

Therefore `k`-NN replacement, barycentric/conservative remapping, tangent
projection, a conservation loss, or a clean split cannot be renamed as AURORA
novelty. A new contribution would require an aneurysm-specific estimand and an
operator-specific guarantee that remain nontrivial after these controls.

## 5. Fresh frozen six-candidate screen

Each axis is scored 0--5 for biomedical importance, identifiable estimand,
residual algorithmic gap, asset readiness, effective independent units,
strong-baseline feasibility, interpretable-figure value and schedule/runtime
fit.

| Rank | Candidate | Importance | Identifiable | Residual | Asset | Units | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Surface-vector tangency + functional commutation | 4.5 | 4.0 | 2.0 | 3.5 | 4.5 | 5.0 | 5.0 | 3.0 | **31.5** | reject; direct surface-vector and conservative-remap priors leave too little residual gap |
| 2 | Area-integral + hotspot-conservative target transport | 4.5 | 4.0 | 1.5 | 3.5 | 4.5 | 5.0 | 5.0 | 3.0 | **31.0** | reject; physical transfer is a required control, not a standalone method |
| 3 | Coordinate/connectivity orientation + area validity | 4.0 | 4.0 | 1.5 | 3.5 | 4.5 | 5.0 | 5.0 | 3.0 | **30.5** | reject; mesh certification alone is quality control |
| 4 | Remap-then-integrate vs integrate-then-remap transient functionals | 4.5 | 4.0 | 1.0 | 3.5 | 4.5 | 5.0 | 5.0 | 3.0 | **30.5** | reject; commutation is important but generic priors are dense |
| 5 | Split-blind normalization provenance | 4.5 | 5.0 | 1.0 | 4.0 | 4.5 | 5.0 | 3.0 | 3.0 | **30.0** | reject; required benchmark hygiene |
| 6 | Test-blind checkpoint + prefix-split reaudit | 4.5 | 5.0 | 0.5 | 4.0 | 4.5 | 5.0 | 3.0 | 3.0 | **29.5** | reject; required evaluation hygiene |

The 31.5 maximum is not rounded up. No architecture is named because doing so
would turn an unresolved target audit into an unjustified model story.

## 6. Compute and server decision

An exact read-only `qstat -u introai9` observation on 2026-08-10 returned no
AURORA job. No login-node GPU command was executed. Because every fresh
candidate is below 32, this audit creates no PBS script, CPU P0 or GPU job.

AURORA execution is restricted to `introai9` PBS after a future prospective
gate. `junjinyong` is used by another project and is prohibited for connection,
query, transfer, submission and monitoring.

## 7. What would justify future compute

A future candidate must be a genuinely new problem version, not a local repair
of this batch. Before any GPU use it must:

1. define a clinically or physically meaningful target that survives
   conservative/tangent-aware transfer controls;
2. identify independent family units and a test-blind evaluation contract;
3. show a residual operator-specific algorithmic gap beyond remapping,
   conservation loss and clean evaluation;
4. score at least 32/40 before payload access;
5. pass a separately registered method-free CPU P0 on `introai9`.

Until then, “no experiment” is the scientific result of the gate, not an
infrastructure failure.
