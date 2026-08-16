# AneuG processed-v4 D5 · non-executable geometry-token draft

> **Status:** unselected design and synthetic tests only. No processed object,
> server, scheduler, field, split or GPU is authorized. A selected D5 must be a
> fresh registered version; this draft remains immutable.

## Correction after D4

D4 found only 168 direct name matches between 578 processed transient cases
and the separately materialized geometry tree. That count is real, but it is
not by itself a processed-input failure. At pinned official code revision
`4a090a0f…`, `record_mesh_upsampling` enumerates the transient case root, reads
each case-local `checkpoint.npy`, stacks its GHD token and stores that exact
order in `mesh_data.cases` and `mesh_data.ghd`. Registration subsequently uses
the same case order. The processed object therefore already carries its
geometry representation; an external directory-name join is not required to
train from the processed representation.

This does **not** establish patient independence. The official paper describes
synthetic shapes sampled through a generative model trained on a small real IA
cohort. It exposes no parent-family key for the processed cases. The defensible
independent unit is consequently a unique synthetic geometry component, never
a patient.

## D5 question and permitted read

D5 asks one field-blind question:

> Do the 578 aligned 432-dimensional processed GHD rows contain enough unique,
> finite geometry components to freeze a synthetic-case-disjoint development,
> validation and outer-test split without reading WSS?

Only `mesh_data.ghd` values and the already-private case order may be read.
Registered tensors, coordinates, normals, WSS, connectivity and external mesh
payloads remain forbidden. Exact float32 row hashes and a fixed numerical-copy
tolerance form connected components. Every exact or tolerance-equivalent row
must remain in one split.

The primary cohort is filename-defined `stable_[0-9]+` only. Other names stay
in a sealed auxiliary bucket until their provenance is authoritative; the
bucket is not called a patient, site or clinical cohort. Primary components are
ordered by a salted BLAKE2b digest of private IDs and assigned 80/10/10 to
train, validation and sealed outer test. All 80 phases follow their geometry.
Only aggregate counts and split digests may be public.

## Prospective consequence

A selected D5 gets one introai9 CPU-4, 64-GB, GPU-0 PBS attempt. Any outcome
closes it. Feasibility requires the exact D4 count and 432 columns, all-finite
GHD rows, at least 400 primary components and at least 40 validation and 40
outer-test components. A pass may freeze the private field-blind split and
permit registration of a separate field audit plus bounded development
contract. It does not itself authorize a WSS read, model, GPU, validation/test
access or paper claim.

The likely post-admission application identity is full-cycle vector-WSS
prediction with a periodic low-rank temporal head, deterministic tangent
projection and explicit TAWSS/OSI/RRT fidelity. Critical-point/worldline
endpoints remain optional until their stability is demonstrated; they do not
hold the paper hostage.

## Draft falsification

Synthetic tests verify execution refusal, immutable D4 history, official
builder semantics, GHD-only access, exact/numerical duplicate grouping,
split-member privacy, phase-by-geometry splitting and rejection of field/GPU/
authorization expansion. The draft artifacts are
[`configs/aneug_processed_v4_d5_draft.json`](../configs/aneug_processed_v4_d5_draft.json),
[`src/aurora/aneug_processed_v4_d5.py`](../src/aurora/aneug_processed_v4_d5.py)
and
[`tests/test_aneug_processed_v4_d5.py`](../tests/test_aneug_processed_v4_d5.py).
