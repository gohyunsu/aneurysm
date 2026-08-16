# AneuG processed-v4 D4 · non-executable draft

> **Status:** design and synthetic metadata code only. D4 is not selected,
> registered, submitted or monitored. This draft cannot access a processed
> object and cannot be mutated into an executable contract.

## Purpose

Closed D3 asked whether the exact processed artifact met a frozen 700-case
floor. It did not. D4 asks a materially different descriptive question:
**what metadata is actually present in the exact processed snapshot?** It has
no cardinality pass threshold and never repairs D3.

The draft implementation accepts already loaded synthetic mappings only. It
derives count, ordered-ID digest, duplicate/blank counts, metadata histograms,
mesh-order agreement and optional geometry-linkage counts without indexing,
converting or materializing tensor values. Full ordered IDs exist only in a
private manifest; the public result contains a digest and aggregates.

## Static schema corroboration

The draft is independently aligned to official AneuG-Flow code commit
`4a090a0f12538deef6fcea88b81afe78ce38152e`, not merely copied from the
closed D3 reader. Pinned `new_version/loaders.py` constructs transient case
records with exactly `tensor`, `labels` and `case`; serializes
`registered_data_list` plus `mesh_data`; and stores case order in
`mesh_data.cases`. The same builder exposes `idx_list`, `edge_index_list`,
`faces_list`, `ghd` and `shape_scale`. D4 therefore describes the shape and
dtype of those hierarchy/geometry objects without reading connectivity or
field values. The pinned loader SHA-256 is
`133fc170ab395fe7bf44891ed625837e9b20ed4de7b977a325cc8e44d61393b5`.

Missing or malformed metadata is reported descriptively rather than converted
into a replacement cohort threshold. The public result uses
`scientific_verdict=null`, not `false`, because D4 makes no scientific pass or
failure judgment.

## Activation boundary

A future D4 requires explicit human selection, a fresh registered config,
Quality-passed public source, clean introai9 checkout and a private activation
manifest. The draft file itself remains immutable and non-executable. The
prospective envelope is one PBS attempt on introai9 with CPU 4, 64 GB and GPU
0; any outcome closes that future census.

Even a complete census permits human rescoring only. It does not authorize
geometry grouping, split freeze, target-stability P0, method selection, GPU
training, validation/test, outer test or a manuscript claim. `junjinyong` is
excluded.

## Synthetic falsification tests

The draft tests require all of the following:

- `human_selected=false` and every authorization false;
- execution refusal in draft state;
- D3 no-backfill/no-relabel and no replacement cardinality threshold;
- tensor sentinels that fail if values are indexed or materialized;
- hierarchy sentinels that expose only list length, tensor shape and dtype;
- case IDs absent from public JSON and present only in the private manifest;
- malformed metadata recorded descriptively without a scientific verdict;
- scope, GPU and authorization mutations rejected.

The source artifacts are
[`configs/aneug_processed_v4_d4_draft.json`](../configs/aneug_processed_v4_d4_draft.json),
[`src/aurora/aneug_processed_v4_d4.py`](../src/aurora/aneug_processed_v4_d4.py)
and
[`tests/test_aneug_processed_v4_d4.py`](../tests/test_aneug_processed_v4_d4.py).
