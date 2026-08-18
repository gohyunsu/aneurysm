# AneuG-Flow release-aligned 730-case protocol

## What the dataset actually is

The final AneuG-Flow paper and pinned dataset card document 14,000 steady and
730 pulsatile CFD cases. Each pulsatile case contains 80 uniformly sampled
phases from the second simulated cardiac cycle. These are synthetic MCA
bifurcation geometries generated from a model trained on real aneurysm shapes;
they are not 730 patients, hospitals or generator-parent families.

The distributed processed objects do not have identical cohort semantics.
Metadata-only HTTP range inspection reproduces the known v4 count of 578. V4
contains only 499 of the 730 documented release cases and 79 additional cases.
V5 contains 809 cases: all 730 documented release cases plus the same 79
extras. No tensor storage or pickle was executed during this comparison.

The independent study therefore defines its main cohort as the exact case-ID
intersection of the pinned public release tree and processed v5. The result is
exactly 730 cases. It does not silently call all 809 processed entries the
official release, mix the 79 extras into training, or reuse the historical
v4 406/51/51 assignment.

On `introai9`, PBS job `116626.ECE-util1` assembled the exact
33,233,856,917-byte v5 object and matched the official SHA-256; job
`116627.ECE-util1` then verified 809 unique, order-aligned mesh/case entries,
432-D GHD rows and case tensors shaped 80 × 13,902 × 9. Transport and archive
schema are therefore complete. The remaining construction step is the
explicit 809→730 release intersection and geometry-component split—not another
download. The 64 staging chunks are retained for now and are not a second
scientific cohort.

Source reconciliation is documented separately in
[`aneug-official-source-reconciliation-2026-08-18.md`](aneug-official-source-reconciliation-2026-08-18.md).
In particular, the proceedings HTML's 200-case text does not override the
final paper, card and exact 730-directory release tree; the final paper's
109-versus-116 real-shape conflict prevents any parent-lineage claim.

The v5 object does not embed the official steady `tensor_norm`. An exact steady
v4 normalization source is available, but physical-unit metrics remain closed
until a v4/v5 overlap audit supports that linkage. This is independent of the
already completed file-transport and schema checks.

## Independent split

The split is designed without reading WSS values or any model result. Exact
and fixed-tolerance duplicate GHD rows are first joined into geometry
components. A private keyed ordering then allocates components as close as
possible to 584 train, 73 validation and 73 locked test cases. Every one of a
case's 80 phases follows that case. Model normalization and any response basis
are fit on training data only; validation chooses models; test remains closed
until the candidate, baselines, endpoints and statistical analysis are frozen.

The independent unit for uncertainty is one synthetic geometry case. Phases
and surface vertices are repeated observations within a case and are never
treated as 58,400 independent samples. Since the release publishes no
patient, site or generator-parent label, the paper will say case-disjoint and
geometry-duplicate-disjoint—not patient-, site- or lineage-disjoint.

`shape_scale` is deliberately not used to group cases: the verified v5 object
stores it as three mesh-level tensors rather than an 809-row case descriptor.
Only the case-aligned 809 × 432 GHD matrix participates in duplicate detection.

## Minimal research identity

The task is geometry-to-complete-cycle vector WSS prediction under the common
waveform and geometry-dependent outlet conditions used by the release. The
paper should not add an artificial BC-imputation story or claim that a GNN,
equivariance, temporal basis or functional loss is novel by itself.

The clean candidate is a cycle-native mesh operator: a multiresolution local
mesh encoder plus a global geometry token predicts train-only temporal
response coordinates for all 80 phases in one pass. A tangent vector decoder
reconstructs WSS, and a field-anchored cycle-functional objective can align
TAWSS and OSI only if matched validation experiments show a gain without a
field-error tax. The direct released Graph U-Net, a strong local/global mesh
model and Transolver are matched controls. No absolute performance threshold
is set before those controls run on this new split.

The primary endpoint is per-case full-cycle vector-WSS relative L2. TAWSS
error, OSI MAE, low-WSS-region error and peak-systolic error test whether a
lower average field error also preserves application-relevant behavior.
Paired case-level intervals and compute/coverage accounting support every
comparison. No rupture-risk or clinical-outcome claim is made.
