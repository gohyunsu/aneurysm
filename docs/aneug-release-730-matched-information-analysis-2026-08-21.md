# Release-730 matched-information factorial analysis

## Purpose

The AneuG-Flow source exposes abundant steady supervision, but RHSIA already
uses steady augmentation and a predicted steady-WSS prior. Steady data is
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

## Prespecified estimands

For every main-table endpoint, the analyzer reports five case-paired mean
contrasts with 10,000-resample percentile intervals:

1. proposal minus control under T;
2. proposal minus control under T+S;
3. steady minus transient-only for the control;
4. steady minus transient-only for the proposal; and
5. the method-by-steady difference in differences.

The interaction is

```text
(proposal_TS - proposal_T) - (control_TS - control_T).
```

For lower-is-better errors, a negative value means that steady information
benefited the proposal more than the control. For OSI coverage, the favorable
direction is positive. This orientation is descriptive and creates no
automatic winner or novelty conclusion.

## Boundary

The kernel accepts four normalized terminal-validation cells only after they
share both the frozen 73-case set digest and the ordered loader digest
`cceb0e47...5a24`, as well as the exact private split hash. The distinction is
essential: the set digest alone cannot prove that identifier-free rows are
paired in the same order. It rejects incomplete cells, different steady
eligibility, identifiers, test/79-extra reads and paper claims. A later private
activation must hash-bind the four raw results and the normalization adapter.
The current code executes only synthetic tests and contains no model result.
