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
schema are therefore complete. CPU/PBS job `117026.ECE-util1` subsequently
completed the explicit 809→730 release intersection and split: all 730 GHD
components were singleton, producing exactly 584 train, 73 validation and 73
locked-test cases. The 64 staging chunks are retained for now and are not a
second scientific cohort.

Source reconciliation is documented separately in
[`aneug-official-source-reconciliation-2026-08-18.md`](aneug-official-source-reconciliation-2026-08-18.md).
In particular, the proceedings HTML's 200-case text does not override the
final paper, card and exact 730-directory release tree; the final paper's
109-versus-116 real-shape conflict prevents any parent-lineage claim.

The v5 object does not embed the official steady `tensor_norm`. An exact steady
v4 normalization source is available, and CPU/PBS job `117006.ECE-util1`
established strong overlap linkage: all nine tensors, GHD rows and mesh
hierarchy entries were bit-exact for the 578 shared v4/v5 cases. Physical-unit
metrics are therefore enabled with that exact decoder source while model
normalization remains train-only. A v5-only creator manifest is still absent,
so the linkage and its limitation remain explicit.

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

The clean candidate is a cycle-native mesh operator: a train-only global
complete-cycle response manifold captures broad variation, while a
multiresolution local mesh branch predicts the remaining Cartesian residual.
The single decoded field may receive a soft tangency penalty, but it is not
hard-projected because the released reference contains small nonzero
mesh-normal components. A field-anchored cycle-functional objective can align
TAWSS and OSI only if matched validation experiments show a gain without a
field-error tax. The direct released Graph U-Net, a strong GHD-GPS/GINE mesh
model and Transolver are matched controls. No absolute performance threshold
is set before those controls run on this new split.

The primary endpoint is per-case full-cycle vector-WSS relative L2. TAWSS
error, OSI MAE, low-WSS-region error and peak-systolic error test whether a
lower average field error also preserves application-relevant behavior.
Paired case-level intervals and compute/coverage accounting support every
comparison. No rupture-risk or clinical-outcome claim is made.
