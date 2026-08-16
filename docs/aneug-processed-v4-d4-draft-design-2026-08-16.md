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
- case IDs absent from public JSON and present only in the private manifest;
- malformed metadata recorded descriptively without a scientific verdict;
- scope, GPU and authorization mutations rejected.

The source artifacts are
[`configs/aneug_processed_v4_d4_draft.json`](../configs/aneug_processed_v4_d4_draft.json),
[`src/aurora/aneug_processed_v4_d4.py`](../src/aurora/aneug_processed_v4_d4.py)
and
[`tests/test_aneug_processed_v4_d4.py`](../tests/test_aneug_processed_v4_d4.py).
