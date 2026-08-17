# D13C same-backbone functional fine-tuning preparation

## Question

Does differentiating through complete-cycle WSS functionals improve TAWSS and
OSI without relying on a different encoder, more input information or an
arbitrary field-error cutoff?

D13C is prepared but non-executable. Every row starts from the exact D11
selected checkpoint and uses the same 406/51 component split, seed, optimizer
budget and full-cycle decoder. D12 must have a terminal record before any D13C
activation, but D12 does not impose an absolute pass threshold.

## Controlled rows

1. `field_only`: continued-training control from the D11 checkpoint.
2. `statistics_scalarized`: field plus mean-vector and TAWSS terms.
3. `osi_scalarized`: field plus reference-support OSI.
4. `all_scalarized`: field plus all three functional terms.
5. `all_field_anchored`: the same complete functional objective with the
   first-order field-anchored gradient control.

The control rows isolate objective effects from extra capacity. Each variant
receives a fresh run ID and result directory; no failed or weak row is hidden.

## Scale and support

All four training terms are normalized by their mean value when the frozen D11
checkpoint is evaluated on all 406 training cases. This train-only calibration
is recomputed identically for every row and stored in its result, so equal
weights do not silently mean unequal numerical scales. The OSI support floor is
`1e-4` times the area/phase-weighted training WSS RMS. This is a singularity
support definition, not a performance gate. RRT and the failed hard D9A
projection are excluded.

Checkpoint selection uses the conventional reported validation endpoints,
each divided by its value at the identical initial D11 checkpoint. Therefore
the field-only row is selected by exactly the same average field rL2 grammar as
D11, while composite rows do not mix uncalibrated metric scales. These initial
validation normalizers are development quantities, recomputed before every row
and never treated as independent evidence.

For the field-anchored row, only a negative functional/field gradient component
is removed; the retained functional direction is norm-matched to the field
gradient. Conflict rate and gradient geometry are recorded. This is a
first-order optimization control inspired by prior gradient surgery, not a
finite-step guarantee or generic novelty claim.

## Selection and interpretation

Each row selects its checkpoint by the lowest variant-specific validation
utility using the frozen initial-D11 endpoint normalizers. Conventional field, mean-vector,
TAWSS, OSI and coverage metrics are reported separately. No absolute threshold
exists. Validation development may identify a candidate, but it cannot create
paper evidence, authorize confirmation or open the 51 outer components.
