# Provenance–evaluation source audit

**Frozen decision · 2026-08-10 KST:** all five candidates are below the
unchanged **32/40** source-admission line. The strongest candidate,
lineage-blocked CFD-to-rupture transfer validity, scores **30.0/40**. It is
rejected without score repair, archive or mesh access, P0, method/architecture
selection, PBS submission or GPU use. AURORA therefore still has no active
primary problem, model, outer test or submission identity.

This batch asks a narrower question than ordinary patient-disjoint splitting.
Several public aneurysm resources repackage related Aneurisk geometries for
morphology, CFD and rupture-status studies. If an evaluation geometry is first
seen through a CFD pretraining release, a later rupture experiment cannot be
called unseen-geometry transfer unless that lineage is blocked. The question is
important, but it becomes an ISBI method contribution only if exact lineage is
identifiable, contamination changes a scientific conclusion, and a new
operator-specific solution remains after direct leakage-audit work.

## 1. Frozen candidate screen

The eight axes are scientific importance, target identifiability, residual
novelty, asset readiness, effective independent unit, strong-baseline
feasibility, interpretable-figure value and schedule fit, each scored 0–5.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Lineage-blocked CFD-to-rupture transfer validity | 4.5 | 4.0 | 1.5 | 2.0 | 4.5 | 5.0 | 5.0 | 3.5 | **30.0** | reject |
| Source-conditional selective rupture prediction | 4.0 | 4.0 | 1.0 | 3.0 | 4.0 | 5.0 | 4.5 | 4.0 | **29.5** | reject |
| Test-blind PointNet++ external re-evaluation | 3.5 | 5.0 | 0.5 | 2.5 | 4.0 | 5.0 | 4.0 | 4.0 | **28.5** | reject |
| HUG curator-lineage invariant morphometry | 3.5 | 2.0 | 1.0 | 2.0 | 1.5 | 5.0 | 5.0 | 3.5 | **23.5** | reject |
| Patient-set multiple-aneurysm rupture consistency | 4.5 | 2.5 | 1.5 | 1.5 | 3.0 | 4.5 | 5.0 | 3.0 | **25.5** | reject |

The 30.0 is not supplemented with an unrelated candidate, rounded upward or
used to reopen the closed AneuX preprocessing-orbit P0.

## 2. What the public lineage establishes—and does not

The official [AneuX repository](https://github.com/hirsch-lab/aneuxdb) describes
750 aneurysm domes from 605 patients: 485 lesions from two HUG curation
portions, 164 from @neurIST and 101 from Aneurisk. It also states that the two
HUG portions differ in exact case selection while representing a very similar
patient cohort. The repository tree contains a README and figures, not a
case-level source or patient-lineage table.

The new [76-case Aneurisk CFD record](https://doi.org/10.5281/zenodo.19455127)
states that every geometry comes from the public Aneurisk repository. Its
[companion preprint](https://arxiv.org/abs/2602.21409) says that 76 anterior-
circulation cases were selected from 100 Aneurisk cases after excluding
multiple-aneurysm trees and unsuitable inlet/outlet geometry. It names examples
such as `C0001` and `C0002` and stratifies analyses by rupture status. This is
strong source-level evidence of shared ancestry with the Aneurisk part of
AneuX, but it is not an exact 76-to-101 lesion manifest.

A bounded metadata-only inspection of the public
[AneuriskData mirror](https://github.com/permfl/AneuriskData) found 24 named
model folders, 24 named DICOM folders and 15 label files. `C0074a` and `C0074b`
are separate named variants. No DICOM, STL, VTP, CSV member, 1.43-GB CFD archive
or AneuX ZIP was opened. Thus the current public small-file boundary cannot
establish which exact geometry, patient and lesion instance is shared across
the three releases.

Without that mapping, the proposed estimand—matched performance difference
between naive sample-disjoint transfer and exact-lineage-blocked transfer—is
well defined in principle but not executable from audited assets. Similarity
matching cannot silently replace provenance: near-isometry may reflect a
re-mesh, cut, smoothing orbit or two genuinely similar aneurysms.

## 3. Direct priors remove the generic novelty

Patient-disjoint evaluation, duplicate detection and cross-corpus
contamination auditing are not new algorithms. [CTSCAN](https://arxiv.org/abs/2604.15561)
already provides deterministic multi-source patient-disjoint medical-imaging
evaluation and matched protocol controls. A 2026
[pathology benchmark audit](https://arxiv.org/abs/2607.12278) constructs
cross-dataset lineage matrices at case and institution level and connects them
to feature-space memorization and accuracy inflation. A prior
[3D medical-image duplicate benchmark](https://arxiv.org/abs/2312.07273)
evaluates pretrained embeddings for near- and duplicate detection.

Consequently, exact-ID joins, rigid/scale registration, shape hashing,
PointNet/DGCNN embeddings, contrastive learning, domain-adversarial training,
source-aware calibration and group-disjoint splitting are mandatory controls,
not contribution statements. The residual aneurysm-specific claim would have
to show that a purported *hemodynamic* transfer gain disappears after blocking
the same anatomical lineage, then introduce a principled way to recover a
positive unseen-anatomy gain. The current sources identify neither half.

## 4. Existing AneuX evaluation further narrows the gap

The original [AneuX morphology study](https://doi.org/10.3389/fneur.2022.809391)
already trains on HUG and uses @neurIST plus Aneurisk as external validation.
The later [PointNet++ rupture study](https://doi.org/10.3389/fphys.2024.1293380)
trains on HUG and evaluates @neurIST, reporting internal/external AUC 0.85/0.71
for its cut1 model. Its methods state that the curve considered most reliable
across training, internal validation **and external validation** was selected
for each fold. A test-blind reanalysis is therefore scientifically worthwhile,
but correcting external-set model selection is evaluation hygiene rather than
an independent fancy architecture.

The same paper already discusses class-composition, resolution, artifact and
selection-bias shifts between HUG and @neurIST. Source-conditional calibration,
abstention or a source classifier alone does not create a new endpoint. The HUG
curator portions also lack an audited identity mapping, so they cannot be
treated as paired curation views or independent centers. Multiple-aneurysm
patient-set consistency is clinically attractive, but the open mapping needed
to connect lesions to one patient and identify a culprit/growth outcome is not
available in the audited small-file boundary.

## 5. Decision boundary

- Cross-release lineage is a mandatory future split/audit field, not the active
  paper identity. A canonical mapping must distinguish patient, lesion,
  acquisition, geometry, cut, resolution, source release and derived CFD field.
- Generic deduplication, patient/source-disjoint splitting, source calibration,
  external-test blindness and shape embeddings are direct priors or scientific
  hygiene—not novelty claims.
- No AneuX archive, CFD archive, DICOM, STL, VTP, clinical spreadsheet, model
  weight or patient payload was accessed. The closed AneuX preprocessing-orbit
  transport failure is not repaired or rerun under a new name.
- No executable P0 is registered because the best score is 30.0/40. Therefore
  there is no PBS or GPU experiment to run or monitor; this is a source-gate
  early stop, not a server failure.
- Any future AURORA execution remains restricted to `introai9` PBS.
  `junjinyong` is excluded from connection, query, submission and monitoring.
- Only a materially new source/task unit with an exact public lineage manifest
  or independent patient-level endpoint may receive a fresh score.

This negative result prevents a necessary leakage check from being marketed as
a model contribution. It also records a concrete requirement for any later CFD
pretraining claim: unseen-patient evaluation must be unseen-anatomy and
unseen-lineage evaluation as well.
