# Release-730 matched-information factorial analysis

## Purpose

The AneuG-Flow source exposes abundant steady supervision, but Sheng et al.'s
current v2 preprint already uses steady augmentation and a predicted
steady-WSS prior. Steady data is
therefore a required information control rather than the proposed novelty.
This result-pending contract separates method and information effects before
the four validation results exist.

The exact factorial is:

| Cell | Model role | Training information |
|---|---|---|
| `control_T` | validation-selected strongest control | 584 transient cases |
| `control_TS` | same control | same transient cases + audited steady rows |
| `proposal_T` | selected aligned-cycle candidate | 584 transient cases |
| `proposal_TS` | same candidate | same transient cases + audited steady rows |

Both T+S cells must use the identical 13,985-row eligibility list with digest
`6dbfde4d...c82cc`. A proposal-only steady advantage is rejected.
They must also bind the same deterministic exposure-schedule contract and
report the actual terminal epoch, exposure count and prefix digest. This makes
row order and repetition auditable even when early stopping yields different
terminal horizons.

## Prespecified estimands

The analyzer reports five case-paired mean contrasts with 10,000-resample
percentile intervals for all recorded metrics:

1. proposal minus control under T;
2. proposal minus control under T+S;
3. steady minus transient-only for the control;
4. steady minus transient-only for the proposal; and
5. the method-by-steady difference in differences.

The interaction is

```text
(proposal_TS - proposal_T) - (control_TS - control_T).
```

Field relative L2, TAWSS error and OSI MAE are the three primary claim errors.
Mean-vector error is supporting evidence. Model-specific prediction-valid OSI
coverage within the common reference support is a diagnostic only; it is not
a gate or claim endpoint because invalid predictions already receive the
registered worst-case OSI error. For lower-is-better errors, a negative value
means that steady information benefited the proposal more than the control.
For diagnostic coverage, the favorable direction is positive. These roles and
orientations are descriptive and create no automatic winner or novelty
conclusion.

## Compute interpretation

T+S performs additional steady-head forward/backward work. Because no
compute-matched transient-replay cell is registered, the two within-model
T-to-T+S contrasts estimate the effect of the complete registered augmentation
protocol, not a causal effect of steady labels alone. The primary method
comparisons remain proposal versus control within T and within T+S.

Every terminal cell must report its transient-training protocol digest,
training seed, transient case-cycle exposures, optimizer steps, measured GPU seconds,
peak memory and active parameters. T and T+S must share the same base
transient-training protocol within each model role. T+S additionally binds the
executed steady-scale audit result and declares its extra forward/backward
work. The analyzer records these quantities but does not normalize away or
reinterpret unequal compute.

## Boundary

The kernel accepts four normalized terminal-validation cells only after they
share both the frozen 73-case set digest and the producer-derived ordered
loader digest `aac001b3...d4dc30`, as well as the exact private split hash.
The earlier planned `cceb0e47...5a24` value is superseded before any of these
four cells exists. The distinction is
essential: the set digest alone cannot prove that identifier-free rows are
paired in the same order. It rejects incomplete cells, different steady
eligibility or exposure provenance, identifiers, test/79-extra reads and paper
claims. A later private
activation must hash-bind the four raw results and the normalization adapter.
The current code executes only synthetic tests and contains no model result.
