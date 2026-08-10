# TopAneu release and evaluation source audit

**Frozen decision · 2026-08-10 KST:** the live TopAneu release is a material
source change, but it does not revive the rejected 29/40 latent-attachment
candidate. One distinct observable candidate scores **33.0/40** and is retained
as a **conditional source lead only**. User acceptance of the data terms is not
verified; medical payload, executable P0, active shortlist, primary problem,
method, architecture, PBS/GPU, outer test and paper contribution remain zero.

## 1. What materially changed

The earlier registered design is no longer the only public object. The
[official data page](https://topaneu-26.grand-challenge.org/data/) now reports a
two-batch release of **417 scans from 409 unique patients**: CHUV MRA 200,
HUG CTA/MRA 87, Mie-Chuo CTA 54 and public INSTED/OpenNeuro MRA 68. UMCU
center-3 is reserved for test. The release contains one image, 52-class location
mask, location JSON, three-class aneurysm-type mask and organizer-predicted
silver vessel mask per scan. The public share reports 21,025,241,495 bytes.

The official repository is frozen at commit
[`018c243445f99199f484018c4c80575c84c72293`](https://github.com/Bangulli/TopAneu-26/tree/018c243445f99199f484018c4c80575c84c72293).
Its public tree contains 417 paths in each of the image, location-mask,
type-mask and vessel-mask SHA manifests and 417 location JSON paths. No medical
member was read. Exact small-source hashes are:

| Public source object | SHA-256 |
|---|---|
| `topaneu_release/Terms_of_use.txt` | `aa7d73eefe57adae20fafd23ddafc068341468aec53db33948060a203ba3432e` |
| `topaneu_release/README.md` | `ea7c5cd4898b5abeef9c251ec05e962d769b51e83d35b0678c41aaa5f9273577` |
| `topaneu_release/CHANGELOG.txt` | `5a992240cb6f4089c138d8dd62830204326693d859f159794e681e44f8e7f0b1` |
| `eval/task1/evaluate.py` | `58cda5d310ec2e4588428b73fbadee5bfdd30a40a79ecec8c9a10f2ceefc462e` |
| `eval/task2/evaluate.py` | `5e24667a47f2141344c07666c7d0492bd8e92122a276512f801f1154ba00e09e` |

The [official evaluation page](https://topaneu-26.grand-challenge.org/evaluation/)
defines class-macro precision, recall and MCC for both tasks, plus Dice,
volumetric similarity and normalized HD95 for Task 2; final ordering is mean
rank across metrics. Task 2 evaluates one binary volume per class rather than
aneurysm instances. The
[participation contract](https://topaneu-26.grand-challenge.org/participation/)
limits inference to 7 minutes/case, 32 GB RAM and one NVIDIA T4 with 16 GB.
On the audit snapshot, the official statistics page reported 285 participants,
12 Task-1 and 8 Task-2 sanity submissions, and no final-test submission.

These facts establish an executable benchmark, not a new method or a performance
result.

## 2. Terms and access boundary

The public terms say that downloading the data constitutes agreement. The user
has not explicitly confirmed that agreement. We therefore read only public
challenge prose, repository source, path/checksum manifests and share-level
file metadata. NIfTI images, location JSON content, lesion/type/vessel masks and
patient payload remain unread.

No agent may accept the terms, create a Grand Challenge team, download the
medical release or submit a challenge container on the user's behalf. Explicit
user acceptance can authorize registration of a new read-only P0, but cannot
authorize a model or GPU by itself.

## 3. Direct-prior red team

The following components are controls, not contributions:

- the TopAneu task itself already couples fine-grained location and lesion masks;
- vessel-distance attention, vesselness-prior multitask learning and ARAN's
  patient-specific centerline GAT already make aneurysm prediction anatomy-aware;
- the public RSNA system already combines aneurysm and vessel heads;
- overlapping-label universal taxonomies, hierarchical/tree losses and
  left--right label-permuting augmentation are generic structured-prediction
  tools;
- VAEsselSparse already learns sparse whole-vascular representations and uses
  them for aneurysm/stenosis discrimination;
- generic learning with privileged information, teacher--student distillation,
  noisy-label learning, annotation-ambiguity modeling and conformal segmentation
  do not become novel when applied to TopAneu;
- direct optimization or a surrogate for the published mean-rank metric is
  benchmark engineering.

The batch-2 changelog lists 52 revised cases, including missing aneurysms,
location relabeling, defacing/cropping changes and the new bilateral M1 early-
bifurcation leaves. This is evidence that the taxonomy and annotation process
matter. It is not an old/new paired supervision asset: the live share exposes
only the current release, so revision-aware training is not currently
identified.

## 4. Frozen six-candidate screen

Each axis is scored 0--5: biomedical importance, identifiable estimand,
residual gap after direct priors, asset readiness, independent units, strong-
baseline feasibility, interpretable-figure value and schedule/runtime fit.

| Rank | Fresh candidate | Importance | Identifiable | Residual gap | Asset | Units | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Factorized leaf risk with train-only silver anatomy and image-only test | 5.0 | 4.5 | 3.0 | 4.0 | 4.5 | 4.5 | 5.0 | 2.5 | **33.0** | conditional source lead; terms/P0 pending |
| 2 | Bilateral reflection-equivariant 52-leaf taxonomy | 4.5 | 4.5 | 1.5 | 4.0 | 4.5 | 5.0 | 4.5 | 3.0 | 31.5 | reject; generic equivariance/augmentation |
| 3 | Type--location compositional auxiliary segmentation | 4.5 | 4.0 | 1.5 | 4.0 | 4.5 | 5.0 | 4.5 | 3.0 | 31.0 | reject; generic multitask factorization |
| 4 | Official mean-rank-aligned optimization | 3.5 | 5.0 | 0.5 | 5.0 | 4.5 | 5.0 | 3.0 | 4.0 | 30.5 | reject; metric engineering |
| 5 | Batch-revision-aware annotation robustness | 4.5 | 3.5 | 2.5 | 2.0 | 4.0 | 4.5 | 4.5 | 3.0 | 28.5 | reject; old paired annotations absent |
| 6 | Longitudinal growth from repeated center-4 scans | 5.0 | 0.5 | 1.5 | 2.0 | 0.5 | 4.0 | 5.0 | 1.5 | 20.0 | reject; order/outcome and units absent |

The 33/40 candidate asks one falsifiable question:

> When 52 rare leaf labels must be predicted with a lesion mask on an unseen
> center, does an observable factorization of territory, laterality and branch
> role, using organizer vessel masks only as noisy training-time privileged
> information, improve patient-level leaf localization and mask risk over flat
> 52-class multitask and artery-aware baselines without requiring a vessel mask
> at test time?

This is not yet a contribution. The factorization, privileged supervision and
anatomy encoder are individually prior art. A method identity exists only if
method-free audits first demonstrate leaf scarcity/source confounding, a valid
factor map and a measurable flat-model failure, and a prospectively frozen
method then improves the official and patient-level estimands on disjoint
centers.

## 5. Gates before any architecture

### Conditional P0-R · asset and semantics

P0-R is not registered or executable until the user explicitly confirms the
TopAneu data-use terms. A future prospective CPU/read-only contract must freeze:

1. release root, total bytes and every official SHA before member access;
2. 417 image--location--type--vessel--JSON one-to-one mappings;
3. 409 patient groups, repeated-scan grouping and center/source lineage;
4. empty/negative, multi-lesion and same-leaf multiplicity support;
5. 52 leaf support, three type classes and a deterministic leaf-to-factor map;
6. location mask--JSON agreement without treating silver vessel masks as gold;
7. batch-revision and selected-public-center provenance;
8. a patient/center-disjoint development split with center-3 and challenge test
   sealed;
9. official metric implementation and 7-minute/T4 deployment contract.

All checks must pass. Failure closes that P0 version without method or GPU.
Pass opens only a separately preregistered method-free P1.

### P1-R · task adequacy

P1-R must quantify class support, source--leaf mutual information, coarse versus
leaf support, silver-mask availability/quality proxies, label-factor validity,
trivial frequency and flat segmentation controls, and the smallest patient-
level effect distinguishable from the planned direct baselines. It uses no
learned proposal and no outer test.

Only a positive P1-R may open bounded validation development with fresh seeds,
a fixed compute budget and a maximum repair count. The first GPU action would
be an `introai9` PBS runtime smoke. `junjinyong` remains excluded from connection,
query, transfer, submission and monitoring.

## 6. Current decision

- Conditional source leads: 1.
- Active executable shortlist: 0.
- Selected primary problem, method, architecture and metric: none.
- TopAneu medical payload and terms acceptance: 0 / unverified.
- Executable P0/P1, PBS/GPU job, outer test and paper contribution: 0.
- Historical 29/40 attachment posterior, closed candidates and failed gates are
  unchanged and are not repaired by this release.

The next decision requires explicit user acceptance of the TopAneu terms or a
different fresh source audit. It does not require an architecture name.
