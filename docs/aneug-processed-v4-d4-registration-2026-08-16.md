# AneuG processed-v4 D4: threshold-free metadata census

The user selected D4 on 2026-08-16. D4 is a fresh descriptive evidence
version, not a repair, rerun, backfill or relabel of the closed D3 case-floor
gate. D3's `<700` verdict and unrecorded exact count remain immutable history.

## Question and output

D4 asks one threshold-free question: what metadata is actually present in the
checksum-exact processed-v4 snapshot? It records the exact registered count,
ordered-ID digest, blank/duplicate counts, case/label/timestep shape and dtype
histograms, mesh-order agreement, hierarchy shape/dtype, geometry linkage and
normalization metadata. Ordered case identifiers are written only to a private
manifest. The public-safe aggregate contains neither IDs nor field values.

The census uses `torch.load(..., weights_only=True, mmap=True,
map_location="cpu")` with only the known serialized `Meshes` state container
allowlisted. It never indexes tensor contents, reads connectivity values,
computes a WSS endpoint or emits a scientific pass/fail verdict. Its
`scientific_verdict` is JSON `null`.

## One-shot execution boundary

The registered envelope is one PBS attempt on `introai9`: CPU 4, memory 64 GB,
GPU 0 and walltime 2 hours. The job rechecks both exact object identities,
requires an exact clean Quality-passed checkout and writes atomically under a
private output root. An attempt marker makes every later submission fail
closed. Any scheduler or program outcome closes D4.

A complete D4 permits human rescoring only. It does not authorize lineage
grouping, split freeze, scientific P0, architecture selection, GPU training,
validation/test, outer test, paper result or claim. `junjinyong` is excluded.

Registered artifacts:

- [`configs/aneug_processed_v4_d4_v1.json`](../configs/aneug_processed_v4_d4_v1.json)
- [`src/aurora/aneug_processed_v4_d4_v1.py`](../src/aurora/aneug_processed_v4_d4_v1.py)
- [`tests/test_aneug_processed_v4_d4_v1.py`](../tests/test_aneug_processed_v4_d4_v1.py)
- [`cluster/pbs_aneug_processed_v4_d4_v1.pbs`](../cluster/pbs_aneug_processed_v4_d4_v1.pbs)
