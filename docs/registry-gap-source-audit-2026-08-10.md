# Registry-gap source audit · 2026-08-10

## Decision

This source-only audit asks whether records missed by the earlier named-dataset
searches identify a usable ISBI problem rather than another architecture. The
search was performed against the official Zenodo record API, then cross-checked
against the primary dataset papers and current direct methods. Before any file
payload was read, the existing eight 0--5 axes and the **32/40** admission line
were retained: biomedical importance, target identifiability, residual novelty,
usable asset readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value, and ISBI-schedule feasibility.

No candidate reaches admission. The public rupture-status test set is the best
candidate at **26.5/40**. Active shortlist, selected primary problem, executable
P0, method, architecture, PBS/GPU training, outer test, submission identity and
paper claim remain **zero**. No CSV, PKL, ZIP, image, wall map, CFD case, RNA
matrix or patient payload was downloaded or opened. This is a source-gate early
stop, not an `introai9` failure.

| Candidate | Importance | Identifiability | Residual gap | Asset | Independent unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Public test-only rupture-status reuse | 4.5 | 3.5 | 0.0 | 2.5 | 3.5 | 5.0 | 4.5 | 3.0 | **26.5** | reject |
| Scalar VWE--hemodynamic association | 4.5 | 1.5 | 0.5 | 4.5 | 3.0 | 5.0 | 3.0 | 4.0 | **26.0** | reject |
| Open CFD-pipeline numerical certificate | 4.0 | 2.5 | 0.5 | 5.0 | 0.5 | 5.0 | 4.5 | 4.0 | **26.0** | reject |
| Cross-cohort rupture transcriptomic core | 4.5 | 3.0 | 0.5 | 4.5 | 2.5 | 5.0 | 3.0 | 2.5 | **25.5** | reject |
| Autopsy CoW-variant geometry prior | 4.0 | 3.0 | 0.5 | 1.0 | 4.5 | 4.5 | 3.0 | 3.0 | **23.5** | reject |

The totals are the arithmetic sums of the displayed cells. Rejection applies to
these exact candidate versions, not to the scientific value of the source work.

## Search boundary

The exact-title Zenodo query returned 49 records. Videos, isolated figures,
case reports, challenge-design PDFs and already audited releases were excluded
before candidate scoring. The current IAVS machine watch was also run and found
the frozen exact `2e40088d9eaa671c592929a154b7b2cf99f9320a` README-only
snapshot unchanged: release 0, explicit repository license 0, code/payload 0.

The remaining records below were not present in the current protocol by record
identifier. Only official metadata, file names, sizes, checksums and linked
primary-source statements were read. A license on a binary blob does not repair
missing case semantics, a test-only split or a non-identifiable endpoint.

## 1. Public test-only rupture-status reuse · 26.5/40

Two CC BY 4.0 Zenodo records expose preprocessed rupture-status test blobs:

- [`10.5281/zenodo.7536330`](https://doi.org/10.5281/zenodo.7536330):
  `IA_testset.zip`, 578,924,037 bytes, MD5
  `f0770b8f59306f6db33f5411575020c9`;
- [`10.5281/zenodo.7757069`](https://doi.org/10.5281/zenodo.7757069):
  `dataset_cta_balanced_test.pkl`, 2,321,552,713 bytes, MD5
  `b579b4368ec7d14c621529554e394c6e`.

The first record is linked by the TransIAR paper. That study retained 423
patients with 449 aneurysms, called presentation status “rupture risk,” and
reports a balanced 200/82 train/test construction plus a 249-lesion imbalanced
test. Its data statement says the Zenodo test set was supplied for review and
that patient CTA is otherwise available only by request. The public record does
not provide a machine-readable patient manifest, center key, train data, raw
CTA lineage or a prospective pre-rupture endpoint.

The second record has only a one-line description and no related identifier.
Its creator overlaps the later GN-Net paper, which again reports 423 patients
and directly combines a geometric branch with 3D-CNN/Transformer neighborhood
context. Exact cross-record and cross-paper case lineage is not public, so the
blob cannot be assumed independent. TransIAR, GN-Net, radiomics, morphology,
PointNet-style geometry and neighborhood context already occupy the obvious
methods. Reading a public test label during method development would also destroy
its role as an untouched outer test. This asset can at most be a future sealed
benchmark after a separately released development cohort and exact lineage
manifest; it is not a training task or a new contribution now.

## 2. Scalar VWE--hemodynamic association · 26.0/40

[`10.5061/dryad.p2ngf1vrg`](https://doi.org/10.5061/dryad.p2ngf1vrg), mirrored
as Zenodo record `5588011`, is CC0 and contains one 3,572-byte CSV with MD5
`4ba44d3becf0a0f327aa9aa7aede01d2`. Its primary paper studies 41 **unruptured**
aneurysms and directly reports correlations between maximum pituitary-stalk-
normalized vessel-wall enhancement, size, rupture resemblance score, size ratio,
normalized WSS and OSI.

The released file is a scalar association table, not the MRA, pre/post-contrast
MRI, mapped wall-intensity field, CFD mesh or velocity/WSS field. More
fundamentally, the target is size and a derived rupture-resemblance score rather
than observed future growth or rupture. The paper already performs the proposed
VWE--hemodynamic association, and later 3D VWE workflows directly study spatial
enhancement. A GNN, multimodal fusion network or graph correlation head would
therefore add architecture without an observable new target.

## 3. Open CFD-pipeline numerical certificate · 26.0/40

[`vortex-cfd v1.0.0`](https://doi.org/10.5281/zenodo.20732293) is a useful MIT-
licensed 66,421-byte software release. It builds OpenFOAM cases from STL,
executes pulsatile `pimpleFoam`, and derives TAWSS, OSI, normalized WSS and sac
pressure. It contains no independent patient cohort, experimental reference,
paired boundary-condition measurements or adjudicated endpoint.

Re-running an open solver on a public geometry can improve reproducibility, but
solver automation, numerical self-consistency and standard biomarker extraction
are infrastructure rather than a new ISBI learning problem. It may become an
engineering dependency of a future admitted task; it cannot itself select a
method, create independent units or validate a neural surrogate.

## 4. Cross-cohort rupture transcriptomic core · 25.5/40

Zenodo record [`10.5281/zenodo.21249929`](https://doi.org/10.5281/zenodo.21249929)
is a CC BY 4.0, 13,855,303-byte processed-results deposit. It reports discovery
in GSE122897 wall tissue (43 labeled aneurysms: 22 ruptured, 21 unruptured), an
eight-gene blood bridge and a six-gene tissue core across external cohorts.
GSE122897 itself contains tissue removed after presentation and already reports
rupture-associated differential expression. Multiple published analyses reuse
the same small GEO cohorts for immune signatures and rupture-status models.

This is not prospective rupture prediction: post-rupture tissue can encode the
consequence of hemorrhage and surgery. External cohorts mix wall and blood,
aneurysm/control and rupture labels, so samples are not interchangeable patient
units. No casewise bridge to CTA/MRA, wall enhancement, geometry or CFD is
released. A cross-modal network would invent patient correspondence, and a new
gene panel would be a secondary omics analysis outside the ISBI imaging identity.

## 5. Autopsy CoW-variant geometry prior · 23.5/40

[`10.5281/zenodo.15692542`](https://doi.org/10.5281/zenodo.15692542) reports a
12-year autopsy study of 221 adults, including 29 aneurysm cases, and associates
aneurysm presence with atypical Circle-of-Willis configurations. The related
2026 record `21719088` is a 719,422-byte PNG described as an interactive semantic
map. Neither record releases casewise tabular data, CTA/MRA, vessel surfaces,
autopsy photographs or segmentation labels.

The aggregate association is biologically interesting but cannot supervise a
geometry model. The positive count is small, death-selected, and the available
figure is not a machine-auditable patient dataset. Existing anatomy-aware
detection, centerline graphs and fine vessel taxonomies remain direct controls.

## Consequence

There is still no current GNN, Transformer, U-Net, neural operator or multimodal
architecture. In particular, the public test blobs do **not** justify restoring
the original GNN direction: TransIAR and GN-Net directly occupy 3D geometry plus
neighborhood modeling, while the asset is test-only and presentation rupture
status is not prospective risk.

The next allowed action is a material source change that supplies all of: an
observable imaging endpoint, an auditable development split with independent
patient units, a sealed outer test, and a residual gap beyond the direct methods.
Only a fresh candidate scoring at least 32/40 may open a separately frozen,
method-free CPU/read-only P0 on `introai9`; P0 pass would still open only task
adequacy, not architecture or GPU. `junjinyong` remains excluded from connection,
query, submission and monitoring.
