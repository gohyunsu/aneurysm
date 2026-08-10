# RSNA-ICA AWS registry correction audit · 2026-08-10

## Decision

An official AWS Open Data Registry entry was missed by the earlier RSNA source
screen. It is a material **metadata correction**, but not an open-data or method
gate. The strongest residual candidate is:

> study-level lesion-set miss-risk control under point, presence and vascular-
> territory supervision.

It scores **31.5/40**, below the unchanged **32/40** source-admission line. The
candidate is rejected in this exact version. Active shortlist, selected primary
problem, executable P0, method, architecture, PBS/GPU work, outer test,
submission identity and manuscript claim remain zero. The 31.5 is not rounded,
reweighted or combined with LargeIA, CADA or TopAneu.

## What the new official record changes

The [RSNA-ICA AWS registry entry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)
reports more than 4,000 brain scans, more than 40 volunteer radiologists, about
200 studies with AI-generated segmentations and imaging from 18 institutions.
The exact registry YAML is blob
`97b8c1f16b2809d2e82ec0c39d3b156b174c8c83`; its latest file commit is
`523ffd3914ba99e6c4b17441f1633cc3eec74c69` dated 2026-04-24.

This corrects the previous statement that only a competition page and an empty
wiki were visible. It does **not** establish anonymous public access:

- the registry resource explicitly points to `ControlledAccess` at RSNA MIRA;
- use is non-commercial, requires agreement to the stated provisions and
  forbids redistribution;
- the [official data wiki](https://github.com/RSNA/AI-Challenge-Data/wiki/RSNA-Intracranial-Aneurysm-Detection-Dataset)
  still says `Coming soon`;
- the registry says “CT brain scans”, whereas public competition systems report
  CTA, MRA, T1-post and T2 inputs, so the released modality contract cannot be
  inferred from the registry description alone; and
- the registry's `DataAtWork` URL currently resolves to an unrelated pulmonary-
  embolism data paper, while the aneurysm data-resource publication is described
  as forthcoming.

No MIRA account was created, no terms were accepted, no access request was
submitted and no S3 listing, CSV, DICOM, segmentation, patient record or model
payload was opened. The prior anonymous HTTP 403 and current controlled-access
metadata are consistent rather than contradictory.

## Supervision that is actually supported

The exact public first-place implementation remains
[`e1dcdf0058e1e0d0044d8053e92243b4b4794555`](https://github.com/uchiyama33/rsna2025_1st_place/tree/e1dcdf0058e1e0d0044d8053e92243b4b4794555).
It and the public second-place report establish the usable semantic boundary:

- aneurysm supervision is center point, study presence and vascular territory;
- supplied voxel segmentations describe 13-class Circle-of-Willis vessel
  anatomy, not official aneurysm-extent masks; and
- author-generated spheres, pseudo masks or manual corrections are method
  products, not a released mixed-granularity lesion-mask cohort.

The registry's “AI-generated segmentations highlighting abnormalities” wording
does not override those code-level semantics. A source-only record cannot be
used to relabel vessel anatomy as lesion extent or to invent reader-level
annotations.

## Frozen score

The eight unchanged 0--5 axes are biomedical importance, target
identifiability, residual novelty, usable asset readiness, effective independent
unit, strong-baseline feasibility, interpretable-figure value and ISBI schedule
fit.

| Candidate | Importance | Identifiability | Residual gap | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| RSNA registry-backed study-level lesion-set miss-risk control | 5.0 | 4.5 | 1.5 | 2.0 | 5.0 | 5.0 | 5.0 | 3.5 | **31.5** | reject |

The large multicenter unit raises importance and potential external validity.
Asset readiness remains low because user-accepted terms, a machine-auditable
manifest, center/modality identifiers, reader/adjudication lineage and a sealed
post-challenge outer-test contract are not publicly verified. Residual novelty
is narrow because detection and reliability are already occupied.

## Direct-prior red team

The following are mandatory direct controls, not contributions:

- the RSNA 2025 first- and second-place global/local, anatomy-aware and
  multitask systems;
- [vessel-aware multi-scale deformable 3D attention](https://papers.miccai.org/miccai-2024/831-Paper2366.html);
- [Sequential Conformal Risk Control for object detection](https://arxiv.org/abs/2505.24038);
- [conformal prediction sets for instance segmentation](https://arxiv.org/abs/2602.10045);
- generic point-supervised 3D lesion detection, set prediction, false-discovery
  control, subgroup calibration and center-shift robustness.

Adding a GNN, Transformer, U-Net, lesion-set decoder, uncertainty head or
conformal wrapper does not create a residual algorithm. A defensible new method
would need an operator or guarantee specific to the released study-level
point/presence/territory observation process, plus prospective superiority over
the public competition systems and the direct risk-control baselines. That gap
is not identified from current public metadata.

## Consequence

This audit supersedes only the claim that the AWS registry entry was absent. It
does not relabel the 2026-08-09 supervision-semantics rejection, authorize data
access or create C21/a result-table row. A fresh candidate can be considered
only after the user personally accepts the RSNA terms and an official versioned
manifest exposes the development units, label provenance and sealed evaluation
contract. Even then, access would trigger a new source/task audit, not automatic
training.

Future authorized execution remains `introai9` PBS only. The current AURORA PBS
list is empty, no login-node GPU command or PBS job was created, and
`junjinyong` remains excluded from connection, query, transfer, submission and
monitoring.
