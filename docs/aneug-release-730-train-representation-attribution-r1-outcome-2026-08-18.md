# Train-only representation attribution R1 outcome

CPU/PBS job `117052.ECE-util1` completed successfully after reading exactly
584 training fields and no validation, locked-test or processed-only-extra
field. It used no GPU. The identifier-free public result SHA-256 is
`a44eee330250fb4faee024f21a58f6ff0662cb4a4b3d21c160a17a6176c53b85`.

## Periodicity

The ordinary source behavior is not a hard periodic closure. Boundary jump
relative to cycle response has median `0.01166`, but six cases have a
boundary-to-interior-median ratio above 10 (`11.25--17.29`) and absolute
boundary jump `3.43--5.35`. Five of the six have the cycle boundary as the
largest transition; the sixth has an even larger interior jump. These are not
low-response denominator artifacts.

Consequently, phase 79 and phase 0 remain two observed endpoints. A periodic
embedding may still be an input representation, but no decoder or loss may
force their outputs to coincide. Complete-cycle response bases must be fit to
the raw 80-phase sequence, including its discontinuities.

## Normals and target space

Stored normals are not unit normals: their casewise median norm has median
`0.0463`, and 91.8% of vertices on average fall below norm 0.1. Their direction
usually agrees with geometry-derived normals, but direct normalization is
ill-conditioned at the minimum `0.000151` support.

Against mesh-derived unit normals, raw WSS is already close to tangent: the
casewise median normal-component ratio has median `0.00375`, and its casewise
95th-percentile ratio has median `0.0224`. This supports mesh normals as an
input or diagnostic, not rewriting the reference. Every baseline therefore
predicts the same raw Cartesian WSS; tangent projection is optional ablation
and must report its field tax.

## Split implication

Private train-only attribution shows that the six extreme cases share a small
release-name stratum. The public source does not document this stratum as a
generator family. The existing split is therefore described only as an
outcome-blind geometry-ID random, GHD-duplicate-disjoint split, not IID family,
patient, site or boundary-condition evidence. The locked test remains unopened
and the assignment is not changed after observing training fields. Any later
source-stratum report is descriptive and cannot be treated as population
inference.
