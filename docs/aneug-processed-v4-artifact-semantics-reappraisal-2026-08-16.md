# AneuG processed-v4 artifact-semantics reappraisal

> **Static verdict · 2026-08-16:** the official raw revision exposes 730
> filename-complete transient directories, while the checksum-exact processed
> v4 object contains fewer than the closed D3 minimum of 700 registered cases.
> The two cardinalities must not be conflated. No processed payload was reopened
> and D3 remains failed and closed.

## Why this review was necessary

D3 separated transport identity from cohort admission. It acquired the exact
23,744,862,051-byte object, passed its official SHA-256 and loaded the required
root keys, then stopped at `registered_data_list < 700`. The exact count was not
materialized. A post-hoc read cannot repair that result, but the public builder
and release metadata can still explain what the artifact name and construction
do—and do not—guarantee.

This audit fixes the official dataset at revision
[`9dd4180…`](https://huggingface.co/datasets/whding123/AneuG-Flow/tree/9dd418083899deddd93a67f9a6fca7a14304fa36)
and code at commit
[`4a090a0…`](https://github.com/WenHaoDing/AneuG-Flow/tree/4a090a0f12538deef6fcea88b81afe78ce38152e).
It reads code, the dataset card and filename metadata only. It reads no tensor
or CFD value from the acquired processed object.

## What is proven

The official dataset card states 730 transient cases. A complete enumeration of
the same pinned revision contains 730 unique `transient_data/stable_*`
directories, and all 730 expose each of the seven documented filenames:
`wall_data.pt`, `blood_data.pt`, `checkpoint.npy`, both geometry files, inlet
centroids and flow split ratio. The 5,110 transient filenames equal 730 × 7.
This is release-tree evidence, not a claim that the 730 shapes are independent
patients or independent generator families.

D3 independently proves that the exact distributed
`assembled_registered_data_1k_v4.pth` has fewer than 700 entries in
`registered_data_list`. Full size and SHA identity rule out an interrupted or
silently truncated transport as the explanation. The exact processed count,
missing IDs and build-time cause remain unknown.

## What `1k_v4` actually means

The official README sets `n_subdivide = 1` and formats the output as
`assembled_registered_data_{n_subdivide}k{tag}.pth`. Consequently, `1k` is a
preprocessing-resolution tag derived from `n_subdivide=1`; it is **not** a
declaration of 1,000 cases and does not imply a cohort-size floor.

The official builder has four relevant semantics:

1. `record_mesh_upsampling` takes the unsorted directories that contain
   `wall_data.pt`; it never asserts that there are 730.
2. With `overwrite_mesh=False`, an existing mesh cache and its stored case list
   are reused rather than reconciled against the current raw tree.
3. With `overwrite_assembled=False`, an existing assembled object is loaded
   rather than rebuilt.
4. The saved root contains `registered_data_list` and `mesh_data`, but the
   builder does not require a raw-tree revision, expected cardinality or build
   manifest.

Therefore, the public code permits a processed snapshot to lag the current raw
tree. This is a supported mechanism, not proof of the historical cause of this
specific file. Possible earlier subset/cache construction remains an inference.

The official baseline split is also unsuitable for confirmation. It selects
cases by a `stable` prefix and then slices serialized order; all 730 public raw
directories use that prefix. This is neither generator-lineage-disjoint nor a
reproducible independence guarantee, and AURORA will not reuse it.

## Scientific consequence

The dataset is not rejected. A processed cohort below 700 may still be large
enough for an ISBI application study, but raw case count is not the effective
sample size: the release is synthetic, the parent/latent lineage is unresolved
and common registration can make random splits optimistic. Lowering D3's floor
after seeing the failure would not resolve any of those issues.

The honest state remains:

- exact processed object: acquired;
- raw release tree: 730 filename-complete cases;
- processed cohort: fewer than 700, exact number and IDs unrecorded;
- lineage-disjoint unit: unresolved;
- scientific P0, model, GPU, validation/test and paper claim: zero;
- reference-relative transient-WSS candidate: 31.0/40 inactive.

## Recommended materially distinct D4

D4 should be a **descriptive processed-cohort census**, not a lower-threshold
rerun of D3. Before any execution it must be explicitly selected and frozen.
One CPU/GPU-0 PBS job would record:

- exact registered count and a private ordered ID manifest plus public digest;
- duplicate/missing ID counts without publishing IDs;
- label, timestep, tensor-shape and dtype histograms without reading values;
- exact `registered_data_list` ↔ `mesh_data.cases` order agreement;
- linkage counts against the existing geometry tree;
- compact normalization provenance separately from scientific field evidence.

D4 must have no cardinality pass threshold. Any outcome closes the census and
permits only human rescoring. It cannot open a split, target-stability P0,
architecture, GPU training or paper claim. If the observed cohort and later
geometry grouping support an adequate effective sample size, those stages need
their own prospective versions; D3 remains an immutable failure.

The machine-readable source of truth is
[`results/aneug_processed_v4_semantics_s0_20260816.json`](../results/aneug_processed_v4_semantics_s0_20260816.json).
