# AneuG processed-v4 D5: field-blind geometry-component split gate

The user selected D5 on 2026-08-16. D5 is a fresh evidence version and does
not mutate the dormant draft or repair, rerun, backfill or relabel closed D4.
D4 remains a complete threshold-free census with a null scientific verdict.

## Why this gate exists

The official processed builder reads a GHD geometry descriptor from every
transient case-local checkpoint and writes it in the same order as
`mesh_data.cases`. Therefore, D4's 168/578 name overlap with a separate
geometry archive is not an input-completeness threshold. The unresolved risk
is different: exact or nearly identical synthetic geometries could cross a
case-level split and make generalization look better than it is.

D5 reads only the aligned 578×432 float32 `mesh_data.ghd` matrix. It hashes
the little-endian float32 bytes of every row, joins fixed-tolerance numerical
copies using both maximum absolute difference and RMS difference, and takes
the transitive closure. Every exact/near-copy component is indivisible.
`stable_<integer>`-only components form the primary pool. Components
containing any other filename are sealed as auxiliary; neither those names
nor the primary components are interpreted as patients, sites or known
generator parents.

## Prospective decision

Primary components are ordered by a salted BLAKE2b digest of their private
member IDs and allocated 80/10/10 to train, validation and outer test. All 80
phases follow their component. The gate passes only if the exact D4 count and
GHD shape/order/dtype remain intact, every value is finite, at least 400
primary components remain, and validation and outer test each contain at
least 40 components. A pass freezes the private split and permits only a
separate registration of field audit and bounded development. It does not
open field values, validation/test access, GPU training or a paper claim.

The public result contains counts and split digests only. Exact case IDs,
component membership, absolute paths and raw logs stay private. A failed or
execution-incomplete attempt closes D5 without repair.

## One-shot boundary

D5 permits one PBS attempt on `introai9`: CPU 4, memory 64 GB, GPU 0 and two
hours. The job requires a clean Quality-passed checkout, rehashes the exact
23,744,862,051-byte transient object in-job, loads it weights-only/mmap on CPU
and writes results atomically. `junjinyong` and login-node GPU use are
forbidden.

Registered artifacts:

- [`configs/aneug_processed_v4_d5_v1.json`](../configs/aneug_processed_v4_d5_v1.json)
- [`src/aurora/aneug_processed_v4_d5_v1.py`](../src/aurora/aneug_processed_v4_d5_v1.py)
- [`tests/test_aneug_processed_v4_d5_v1.py`](../tests/test_aneug_processed_v4_d5_v1.py)
- [`cluster/pbs_aneug_processed_v4_d5_v1.pbs`](../cluster/pbs_aneug_processed_v4_d5_v1.pbs)
