# AneuG-Flow processed-v4 storage-bounded acquisition

## Decision

The paper does not require the roughly 2 TB raw release. The official transient
v4 object is exactly 23,744,862,051 bytes at LFS SHA-256
`141541ed9b3f57bcbbda868512b54b57407547fdc1e86eec34195f47b8a451c9`.
It is the only full transient object retained. V5, per-case `blood_data.pt`,
per-case `wall_data.pt`, the 14,000-case steady CFD set and `cfd/` are excluded.

The official assembler shows one necessary correction to a transient-only
plan: transient v4 stores `registered_data_list` and `mesh_data`, while its
normalization comes from steady v4 and is not embedded in the transient root.
Without that normalization, normalized-space training is possible but physical
WSS recovery and zero-sensitive critical-point analysis are not defensible.
The exact 9,632,510,050-byte steady v4 object is therefore temporary: after its
checksum is verified, only `label` and `tensor_norm` are retained in a compact
private manifest and the full steady object is deleted.

Peak new processed storage is 33,377,372,101 bytes. The selected AneuG-v4
acquisition cap is 60 GB.
The existing geometry release plus transient object and temporary steady norm
source fit inside this bound; raw/v5 expansion is machine-forbidden.

## D1 gate

The D1 job is acquisition and schema validation, not a scientific experiment.
It verifies exact object size/hash, then uses a weights-only memory-mapped
reader to check:

- at least 700 unique transient case IDs;
- 80 phases per case;
- common tensor shape and labels including `x/y/z` and vector `wss_x/y/z`;
- exact case-order agreement with `mesh_data`;
- linkage of every processed case ID to a local geometry directory; and
- a label-aligned compact steady `tensor_norm` manifest.

It reads no tensor value used for a field/scientific metric and publishes no
case ID. A successful gate authorizes a geometry-linked near-duplicate grouping
and development-split freeze, followed by an engineering baseline smoke. It
does not itself activate scientific P0, GPU training, outer test or a paper
claim.

Transport is resumable because byte-exact acquisition is not a statistical
trial. At most three PBS attempts may extend the same partial file. Every
attempt targets the same immutable revision, byte count and SHA-256; retries
cannot change an endpoint, split or scientific decision. Execution is
`introai9` PBS-only with GPU 0. `junjinyong` remains prohibited.

## Attempt 1 outcome and bounded observability change

Exact Quality-passed source `b16ae4b…` ran once as introai9 job
`116207.ECE-util1` with CPU 4, 64 GB and GPU 0. It exited 2 immediately. Only
the attempt-start marker exists; no partial object, persistent PBS log, reader
access or schema verdict materialized. The low-level cause is unresolved.

Attempt 2 consumes the next transport slot and changes only observability:
the wrapper writes stage transitions and a final exit status directly to the
private shared record directory. Exact URLs, sizes, SHA-256, storage cap,
resume semantics, reader and schema checks are unchanged. This is not a
scientific-contract repair.

## Attempt 2 outcome and final compatibility change

Job `116208.ECE-util1` persisted the missing stage evidence. The compute node
runs curl 7.58.0, which rejects `--retry-all-errors`; it exited 2 before any
partial byte. Reader and schema remain untouched. Final attempt 3 replaces
only that unsupported option with curl-7.58-compatible retry delay and
connection-refused handling. There is no fourth D1 transport attempt.
