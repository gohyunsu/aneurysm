# TopAneu code-semantics and direct-prior red team

**Frozen decision · 2026-08-10 KST:** the earlier 33/40
`factorized_leaf_risk_with_train_only_silver_anatomy` source lead is preserved
as historical schema-6.3 evidence, but a fresh official-code and primary-prior
audit rejects that formulation at **31.0/40**. The best candidates in this new
batch score **31.5/40**, below the frozen 32-point admission line. Active source
shortlist, primary problem, medical payload, executable P0, method,
architecture, PBS/GPU, outer test and paper contribution return to zero.

This is a new evidence version, not a retrospective repair of the 33/40 score.
It asks whether newly inspected public task code occupies the proposed gap.

## 1. Bounded source scope

The [official repository](https://github.com/Bangulli/TopAneu-26) was read at
commit
[`018c243445f99199f484018c4c80575c84c72293`](https://github.com/Bangulli/TopAneu-26/tree/018c243445f99199f484018c4c80575c84c72293).
The 44 MB checkout contains source, evaluation simulations, small taxonomy
metadata and `.sha` manifests. No NIfTI/MHA patient image or label mask, no
patient-level location JSON content and no SWITCHdrive medical member was read.
The user has not accepted the data-use terms.

Exact non-patient source hashes are:

| Object | SHA-256 |
|---|---|
| `topaneu_release/location_mapping.json` | `815c021012f499bff80b517bab1c7a351f4967ce628c0a8055d98e2ac8bc69fa` |
| `topaneu_release/type_mapping.json` | `2c75d432539028ac4c58f726c89bd216089015575388e51701a30f8b2f4833c6` |
| `topaneu_release/vessel_mapping.json` | `0ecca1d2a962a08c7c0fcdd41ed94af11e0e121be8b31677902396ea52dafe7f` |
| `eval/task1/evaluate.py` | `58cda5d310ec2e4588428b73fbadee5bfdd30a40a79ecec8c9a10f2ceefc462e` |
| `eval/task2/evaluate.py` | `5e24667a47f2141344c07666c7d0492bd8e92122a276512f801f1154ba00e09e` |
| `eval/task2/README.md` | `10ee0d290be010cc70c69b175621bd9db6ec2a0dbbabceb6ff3b55ba80bd2fa9` |
| Task-1/Task-2 template `main.py` | `5f87a02222cc2d0cb9903f012a7b77252407707e5fb3ebdadca8fa8cbee7f6d1` / `7b431588eebff8e154dab9ca286c5fa07a775b29e48b134ad6ec11d2afdb26dd` |

## 2. What the code establishes

### 2.1 The proposed leaf factorization is already explicit metadata

The 52 labels are not opaque class IDs. The official mapping contains 24
right/left pairs and four non-lateral leaves. Names and numeric prefixes already
encode vascular territory, laterality and roles such as trunk, junction,
terminus and distal branch. Turning these exact fields into a hierarchy is a
useful baseline, but not an independently discovered representation.

### 2.2 Image-only inference is already the official interface

Both Task-1 and Task-2 templates accept only `head-ct-angiography` or
`head-mr-angiography`. The silver vessel mask is not an algorithm input at
evaluation. Using it during training and removing the auxiliary branch at test
is therefore an implementation/control under the challenge contract, not a new
test-time information setting.

### 2.3 The two tasks do not expose a new cardinality algorithm by themselves

Task 1 reads a list and preserves repeated class IDs as counts. The active Task
2 path, however, binarizes each class over the whole volume: presence is one TP
when any predicted/ground-truth voxels overlap, and Dice/VS/HD95 are computed on
the merged class volume. An instance-level connected-component implementation
exists in source but is explicitly disabled with `omit for now`. The official
Task-2 documentation also states that multiple aneurysms in the same location
are very unlikely.

This reveals an evaluation-granularity boundary, but does not establish enough
same-leaf multiplicity for a new method. Optimizing or correcting the released
metric is evaluation engineering unless a distinct patient-level endpoint and
support are prospectively shown.

## 3. Direct priors that close the obvious mechanisms

- [Scaling Supervision for Free](https://proceedings.mlr.press/v301/li26d.html)
  already uses automatically generated anatomical segmentation as additional
  **training-only** supervision for medical-image diagnosis and removes the
  auxiliary branch at inference.
- [Segmentation-Consistent Probabilistic Lesion Counting](https://proceedings.mlr.press/v172/schroeter22a.html)
  already maps segmentation probabilities to calibrated lesion-count
  distributions using differentiable clustering and Poisson-binomial counting.
- [Image Classification with Consistent Supporting Evidence](https://proceedings.mlr.press/v158/wang21a.html)
  already formalizes compatibility between a prediction and its supporting
  spatial evidence.
- [HATs](https://papers.miccai.org/miccai-2024/374-Paper1451.html) already turns
  an anatomical hierarchy into a taxonomy-aware segmentation loss.
- [Vessel-aware aneurysm detection](https://papers.miccai.org/miccai-2024/831-Paper2366.html)
  already uses vessel segmentation-derived distance maps with deformable 3D
  attention for intracranial aneurysm detection.
- DeepSetNet/cardinality loss, joint lesion classification--segmentation,
  artery-aware centerline models, generic LUPI/distillation and conformal
  segmentation remain mandatory controls.

Consequently, hierarchy, train-only silver anatomy, set cardinality,
classification--mask consistency, artery-aware attention and metric alignment
cannot be combined and renamed as a contribution.

## 4. Fresh frozen six-candidate screen

Axes are 0--5 for biomedical importance, identifiable estimand, residual gap,
asset readiness, effective independent units, strong-baseline feasibility,
interpretable-figure value and schedule/runtime fit.

| Rank | Candidate | Importance | Identifiable | Residual | Asset | Units | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Official metric/instance-collapse-aware training | 4.0 | 5.0 | 0.5 | 5.0 | 4.5 | 5.0 | 3.5 | 4.0 | **31.5** | reject; metric engineering and explicit task contract |
| 2 | Explicit hierarchical 52-leaf taxonomy | 4.5 | 5.0 | 0.5 | 4.0 | 4.5 | 5.0 | 4.5 | 3.0 | **31.0** | reject; hierarchy is in metadata and HATs is direct prior |
| 3 | Image-only source generalization with train-only silver anatomy | 5.0 | 4.0 | 1.0 | 4.0 | 4.5 | 5.0 | 5.0 | 2.5 | **31.0** | reject; vessel-aware and training-only anatomy supervision are direct |
| 4 | Type--location compositional auxiliary segmentation | 4.5 | 4.0 | 1.0 | 4.0 | 4.5 | 5.0 | 4.5 | 3.0 | **30.5** | reject; generic multitask composition |
| 5 | Multiset--mask cardinality coherence | 4.5 | 2.5 | 1.0 | 4.0 | 4.5 | 4.5 | 5.0 | 2.5 | **28.5** | reject; support unknown/rare and direct counting prior |
| 6 | Center-4 longitudinal growth | 5.0 | 0.5 | 1.5 | 2.0 | 0.5 | 4.0 | 5.0 | 1.5 | **20.0** | reject; order, endpoint and units absent |

The earlier 33/40 candidate receives the fresh score **31.0/40** in this audit:
importance/identifiability/asset/units/baseline/figure/schedule remain useful,
but residual novelty falls from 3.0 to 1.0 after the official taxonomy,
image-only interface and direct 2022--2026 priors are included.

## 5. Decision and next action

- Historical schema-6.3 score 33.0 is immutable evidence; it is not edited.
- The fresh code-semantics version is rejected below 32. There is no active
  conditional lead and TopAneu terms acceptance no longer opens P0-R for this
  formulation.
- No patient payload, P0, method, architecture, PBS/GPU, outer test, C21 or
  result row is created.
- The next allowable work is a fresh problem-level source audit or a material
  change that supplies a distinct endpoint/residual algorithmic gap. Reusing
  hierarchy, train-only silver anatomy or count--mask consistency under a new
  name is forbidden.
- Any future authorized AURORA execution remains `introai9` PBS only;
  `junjinyong` is excluded from connection, query, transfer, submission and
  monitoring.
