# D9 mesh-canonicalized validation pilot

## Decision

D8 established that coordinates and shared faces provide complete unit surface
normals and that physical WSS is tangent to those normals. D9 therefore opens a
bounded train/validation experiment. It is not confirmation, an outer test, or
paper evidence. The frozen D5 unit remains a synthetic-geometry component—not
a patient, institution, or verified generator family.

Stored normal channels are excluded from every model input, target, loss and
metric. Each case is decoded to physical units, its phase-0 coordinates are
centered and RMS-scaled, normals and triangle-lumped areas are recomputed from
the shared finest faces, and WSS is deterministically projected into the mesh
tangent plane. WSS scale and GHD standardization are computed from the 406
training components only. The 51 validation components may select an epoch;
outer and auxiliary tensor values remain unread.

## Matched question

The experiment asks whether a cycle-moment/POD readout improves TAWSS and OSI
without materially worsening transient field error when compared with an
80-phase direct readout on the same geometry information and backbone. Both
variants use the same three-level scalar-vector mesh message operator, seed,
optimizer, schedule, training budget and validation checkpoint rule. The
moment variant differs only in its readout: a tangent mean vector, a
Jensen-feasible mean magnitude and a residual in a train-only temporal POD
basis. At validation, an exact numerical projection uses predicted—not
reference—moments.

This isolates the proposed mechanism. It does not claim strict SE(3)
equivariance, parameter matching, generic GNN novelty, or novelty for mesh
normal construction, tangent projection, POD, TAWSS, OSI, or exact moment
correction. The direct AneuG prior already occupies broad transient-WSS graph
surrogation and cycle-functional evaluation.

## Prospective evidence and stop rule

The sole single-seed pilot reports case-aggregated area/phase-weighted field
relative L2, normalized TAWSS absolute error, OSI MAE and OSI support coverage.
Checkpoint selection uses validation field error only. A noncompensatory
development screen requires direct field relative L2 at most 0.35, moment/direct
field error at most 1.05, moment/direct TAWSS and OSI errors at most 0.98, and
OSI coverage at least 0.99 for both variants. These thresholds were frozen
before field access.

A pass permits registration of a fresh multi-seed validation confirmation only.
A failure does not justify threshold repair, architectural search on validation,
or outer access. Each of R0 preparation, R1 direct-cycle and R1 moment-POD has
one accepted PBS attempt; stages run sequentially on one `introai9` GPU, with a
maximum of 28 requested GPU-hours. No D9 numeric result is public, and no static
site is maintained.
