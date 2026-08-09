# Aneumo generation-lineage split source audit

**Frozen source decision · 2026-08-10 KST:** generation-family-disjoint
hemodynamic-operator model selection scores **35.0/40** and is the only member
of this six-candidate batch above the unchanged **32/40** source-admission
line. This admits exactly one method-free, CPU-only metadata P0 on `introai9`.
It does not select a primary problem, method, architecture, GPU experiment,
outer test or paper contribution.

The material source revision is Aneumo commit
`701d53dde3489d84dbe9bc8324254629162eb45a`, whose corrected
`Connection.csv` makes the synthetic generation lineage explicit. The official
steady benchmark's 160 training geometries and 40 validation geometries have
disjoint case IDs, but all 20 validation base families also occur in training.
The released split therefore evaluates new deformations of already observed
source anatomies; it is not a held-out-base-anatomy validation set.

## 1. Frozen six-candidate screen

Each axis is scored from 0 to 5 in the fixed order: scientific importance,
target identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Generation-family-disjoint hemodynamic-operator model selection | 5.0 | 5.0 | 3.0 | 3.0 | 5.0 | 5.0 | 5.0 | 4.0 | **35.0** | admit metadata P0 only |
| Geometry–flow compositional OOD generalization | 4.5 | 4.0 | 1.5 | 3.0 | 5.0 | 5.0 | 5.0 | 3.5 | **31.5** | reject |
| Hierarchical deformation-versus-family uncertainty calibration | 4.5 | 3.5 | 1.5 | 3.0 | 5.0 | 5.0 | 5.0 | 3.5 | **31.0** | reject |
| Shape-derivative-informed deformation response | 4.5 | 2.0 | 1.0 | 3.0 | 5.0 | 5.0 | 5.0 | 3.5 | **29.0** | reject |
| Synthetic-to-real selection on ten original cases | 4.5 | 3.0 | 1.5 | 3.0 | 1.0 | 5.0 | 5.0 | 4.0 | **27.0** | reject |
| Family-disjoint transient WSS forecasting | 4.5 | 4.0 | 1.0 | 2.5 | 4.0 | 5.0 | 5.0 | 3.5 | **29.5** | reject |

The six scores were frozen together before any CFD archive member, mesh,
mask, point cloud or field payload was accessed. The 35.0 row is not a license
waiver, method score or expected performance claim.

## 2. What the revised official sources establish

The official [Aneumo repository](https://github.com/Xigui-Li/Aneumo) reports
10,660 generated geometries from 427 real AneuX bases and eight steady flow
conditions per geometry. Its corrected public mapping has 10,660 unique case
IDs, 427 base-family IDs and 6--30 deformations per family. The correction on
2026-07-24 changes the lineage assignment around cases 2,159--2,170, so the
mapping commit must be pinned rather than inferred from numeric proximity.

The official DeepONet and Swin–DeepONet split files are byte-identical across
the two implementations. Training contains 160 generated geometries from 20
base families, using deformations 1--8. Validation contains 40 different case
IDs from the same 20 families, using deformations 9--10. Thus:

- exact case-ID overlap is 0;
- base-family overlap is 20 of 20;
- every validation family is represented in training;
- the independent anatomical unit for generalization is the base family, not
  each deformation or each flow-condition record.

The datasheet nevertheless describes validation as having no geometric overlap
with training. It also says every base has at least 20 deformations, while the
current mapping includes families with 6--19. These are testable release
contract discrepancies, not grounds to guess missing records.

The exact Hugging Face dataset commit
`f801adee816c18d3e18b23e6fcb147fe4c264209` exposes 267 steady ZIP pointers and
100 transient batch pointers covering cases 1--1,000. The repository README
says the remaining transient cases are still to be uploaded, despite the
datasheet describing 10,660 transient sequences as distributed. P0 reads only
the tiny Git LFS pointer text for one steady and one transient archive; it does
not resolve or download either multi-gigabyte object.

There is also an unresolved license contradiction. The GitHub datasheet states
CC BY 4.0, whereas the current Hugging Face card declares CC BY-NC-ND 4.0. P0
must record the conflict exactly; it cannot interpret it as permission or
silently choose the less restrictive text.

## 3. Why split repair alone is not novelty

Group-disjoint splitting, duplicate/lineage detection and avoiding augmentation
before splitting are evaluation hygiene. Geometry-informed neural operators,
boundary-augmented operators, shape-derivative operators, OOD neural-operator
risk analysis, group DRO, contrastive invariance and hierarchical uncertainty
are direct priors. A renamed GNN, Transformer or neural operator cannot turn
the corrected split into an ISBI contribution.

The residual research question is narrower and empirical: does within-family
validation choose a materially different operator than development on held-out
base families, and does the difference persist simultaneously for full fields,
aneurysm-surface functionals and flow-condition response on untouched base
families? Only a prospectively separated development/outer-family evaluation
with strong geometry-operator baselines can establish that gap. A new method
would be considered only after the gap is positive and after its idea remains
distinct from generic group robustness and shape-operator work.

## 4. Exact P0 boundary

`configs/aneumo_lineage_p0.json` freezes a single `introai9` PBS CPU audit. It
may download only six small text/CSV sources and two Git LFS pointer files:

- `Connection.csv`, `MPs.csv`, the official train and validation CSVs, the
  repository datasheet and README;
- the Hugging Face README plus the pointer text for `1.zip` and
  `batch_1-10.zip`.

It checks exact hashes, mapping cardinality, family/deformation continuity,
morphometry-key coverage, train/validation case and family overlap, license
texts and pointer object sizes. It must not read an archive central directory
or member payload. One exact job may make the three frozen transient transport
attempts per small source; same-source repair or resubmission is forbidden.

Even a P0 scientific pass only establishes that the lineage flaw and a
family-disjoint task are identifiable. Because the license conflict is already
known, P1 remains on hold until the publisher provides an unambiguous dataset
license at a pinned source. P0 does not authorize a model, GPU or outer test.

## 5. Current research boundary

- Active source shortlist: one conditional metadata-P0 candidate.
- Selected primary problem, method and architecture: none.
- CFD archive/member payload, model weights and patient data accessed: none.
- Authorized execution: one CPU/PBS P0 on `introai9`, GPU 0.
- `junjinyong`: excluded from connection, query, submission and monitoring.
- Paper status: not submission-ready; no contribution is promoted from this
  source finding.

