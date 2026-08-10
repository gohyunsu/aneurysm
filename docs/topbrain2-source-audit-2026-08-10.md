# TopBrain 2.0 source audit · 2026-08-10

> **Official-API correction · 2026-08-10:** Zenodo revision 4 marks the
> published design object `open` under `CC BY 4.0`. That license covers the
> only released object—the 35-page design PDF—not an unreleased medical
> dataset. The live challenge page is still `Under construction` and exposes
> a Join registration route, but no Data, Evaluation, Rules or Submission
> task route. This corrects the earlier “no license identifier” and “not
> accepting submissions” wording without changing any score or gate decision.

## Decision

TopBrain 2.0 is a material new challenge **proposal**, not a verified medical-
image release. Six problem formulations were frozen together against the
unchanged eight-axis source rubric. The strongest is joint aneurysm–parent-
vessel consistency, at **29.0/40**. All six remain below the automatic
**32/40** admission line.

This batch is therefore rejected without score repair. Active shortlist,
selected primary problem, executable P0, method, architecture, PBS/GPU work,
outer test, submission identity and manuscript claim remain zero. No
`introai9` job was created. `junjinyong` was not contacted, queried, used for
transfer, submission or monitoring.

## What the official source actually is

The [official Zenodo record](https://zenodo.org/records/19707577), DOI
`10.5281/zenodo.19707577`, was published on 2026-04-23. Its only file is a
35-page, 139,840-byte challenge-design PDF:

- Zenodo MD5: `da6c835d0336db81a94b78e7601f47b8`;
- independently verified SHA-256:
  `15a2269bc00b6720f10d6efd41d8996010703451aef32de14f599cd3357ff4f7`;
- patient image, vessel mask, aneurysm annotation, clinical table, split
  manifest and held-out test payload accessed: **0**.

The [official challenge page](https://topbrain2026.grand-challenge.org/topbrain2026/)
is `Under construction` and exposes a Join registration route. Registration
is not an executable task submission contract: no Data, Evaluation, Rules or
Submission task route was present in the bounded page inventory. The design
document planned a 2026-07-05 training release and a 2026-09-05--15 test
window, but the bounded official-source screen did not identify a versioned
TopBrain 2.0 dataset or executable 2026 evaluation contract. This is recorded
as **not verified**, not as proof that no private or future asset exists.

The public evaluation repository remains explicitly the TopBrain **2025**
package at exact head `ba4252ab0dbe9d59a9ae45058ae040b016aae0ad`.
It implements six anatomy-segmentation metrics. It does not establish the ten
planned TopBrain 2.0 metrics, the ordinal clinical task or a sealed 2026 test.
Zenodo revision 4 attaches `CC BY 4.0` to this public design record. Because
the record contains only the PDF, that identifier does not establish a license
or terms for medical data that have not been released. Intended use terms in
the proposal likewise cannot substitute for a data-release contract.

## Planned tasks are not released targets

### Task 1 · whole-brain vessel anatomy

The proposal plans a unified artery/vein segmentation benchmark with at least
55 labels across CTA, MRA, CTV, MRV and 7T MRA. It lists 215 training and 123
test volumes. The aneurysm-bearing subset is planned as 25 CTA and 25 MRA
training volumes plus 10 CTA and 10 MRA test volumes from TopAneu.

Crucially, aneurysm is a **robustness condition** for the vessel-anatomy task,
not a released lesion target. The proposal does not provide a casewise
aneurysm-mask, parent-vessel attachment, acquisition, reader or cross-challenge
identity manifest. Counting 70 planned aneurysm-bearing volumes as 70 usable
lesion targets would be a semantic error.

The planned evaluation already contains Dice, HD95, component-count error,
clDice, invalid-neighbor error, side-road-vessel detection and four class-
contamination measures. Repackaging these organizer-owned criteria as a new
topology or contamination method is not a residual contribution.

### Task 2 · stenosis and occlusion grading

The proposal plans ordinal stenosis/occlusion labels at roughly 15 named
vessels, with 315 training and 183 test volumes. It notes that only a subset was
annotated at design time and that a single clinical expert labels each case
without a merge procedure. The endpoint is stenosis/occlusion, not aneurysm
detection, growth, rupture, treatment response or hemodynamics. Combining two
challenge tasks in a multi-head network would broaden outputs without creating
an identifiable aneurysm question.

## Frozen score

The axes, each scored 0--5, are biomedical importance, target identifiability,
residual novelty, usable asset readiness, effective independent unit, strong-
baseline feasibility, interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Residual gap | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Joint lesion–parent-vessel consistency across planned TopBrain 2.0/TopAneu cases | 5.0 | 3.5 | 1.5 | 1.0 | 4.0 | 5.0 | 5.0 | 4.0 | **29.0** | reject |
| Aneurysm-conditioned vessel-integrity failure localization | 4.5 | 3.5 | 1.5 | 1.0 | 4.0 | 5.0 | 5.0 | 3.5 | **28.0** | reject |
| Disease-conditioned selective vessel segmentation | 4.5 | 3.0 | 2.0 | 1.0 | 4.0 | 5.0 | 5.0 | 4.0 | **28.5** | reject |
| Unified modality/source-invariant artery–vein anatomy | 4.0 | 3.5 | 1.0 | 1.0 | 4.5 | 5.0 | 4.5 | 4.0 | **27.5** | reject |
| Class-contamination-aware multiclass vessel calibration | 4.0 | 4.0 | 1.0 | 1.0 | 4.0 | 5.0 | 4.5 | 3.5 | **27.0** | reject |
| Compositional aneurysm–stenosis ordinal diagnosis | 3.5 | 3.5 | 0.5 | 1.0 | 4.5 | 5.0 | 3.5 | 2.0 | **23.5** | reject |

The table is intentionally not ranked by appearance. The maximum is 29.0; no
rounding, axis reweighting, planned-sample inflation or cross-challenge pooling
is used to approach 32.

## Direct-prior red team

The following are controls or occupied problem components, not contributions:

- [TopBrain 1.0](https://www.medrxiv.org/content/10.64898/2026.05.28.26354312v1)
  already benchmarks 48-class CTA/MRA artery-and-vein segmentation, including
  anatomy, topology and side-road-vessel metrics;
- [TopAneu 2026](https://topaneu-26.grand-challenge.org/) directly targets
  aneurysm detection, location classification and segmentation across CTA/MRA;
- the [RSNA second-place system](https://arxiv.org/abs/2606.26706) already uses
  joint aneurysm/vessel classification and segmentation across CTA, MRA,
  T1-post and T2;
- [multi-class Betti matching](https://papers.miccai.org/miccai-2024/779-Paper0582.html),
  [cbDice](https://papers.miccai.org/miccai-2024/129-Paper0458.html) and
  [centerline cross entropy](https://papers.miccai.org/miccai-2024/770-Paper1081.html)
  directly occupy multiclass topology, diameter and connectivity losses; and
- generic pathology-aware domain generalization, atlas-aware segmentation,
  selective prediction, failure detection and multi-task learning occupy the
  remaining wrappers.

A GNN, topology loss, anatomy token, modality head, uncertainty head or
conformal wrapper does not solve the missing target/release contract. A future
residual method would require a released casewise observation process and a new
estimand that the organizer tasks and these controls do not already define.

## Consequence

TopBrain 2.0 becomes a **source watch**, not a primary task. A material future
release may trigger a new versioned source audit only if it exposes concrete
development units, label provenance, license, cross-challenge lineage and a
sealed evaluation contract. It does not reopen the historical TopBrain 1.0
29.5/40 rejection or authorize automatic download, P0 or training.

The machine-auditable watch is
[`configs/source_watch_v2.json`](../configs/source_watch_v2.json). It freezes
Zenodo revision, license scope, file inventory and challenge navigation while
retaining a single automatic outcome: request a fresh source audit. It cannot
download, accept terms, register P0, select a model or authorize GPU work.

The next allowable action remains a fresh problem-level source audit. Only a
candidate frozen at at least 32/40 can register a separate method-free,
read-only CPU P0 on `introai9`; a P0 pass would still not authorize a model or
GPU training.
