# Response-fidelity confirmation v3 evaluator red-team

Status: **inactive pre-evidence design; v2 preserved and superseded with
eligibility metadata, field and prediction access all zero; real P0 0/11; no
model, compute, result or claim**  
Decision date: 2026-08-13 KST

## Verdict

Keep the Aneumo response-fidelity question, but reject confirmation v2 as the
final evidence contract. V2 closed sample-size and prevalence loopholes, yet it
could still pass when the proposed candidate beat the learned direct head while
losing response fidelity to a simple train-fitted power law. It also required
only one-sided field non-inferiority, which does not establish the
**field-error-matched** premise when the candidate has materially lower field
error.

V3 preserves v2 unchanged and closes those gaps before any confirmation
eligibility metadata, field or prediction is read. It adds no architecture and
creates no execution authority.

## The comparator logic

The proposed application identity is not “a neural model is more accurate than
another neural model.” It is that a field-error-matched surrogate can preserve
the response curve better because its output parameterization preserves the
nominal anchor identity. Therefore the candidate must survive both controls:

1. the same-backbone direct target-field head tests the parameterization
   mechanism; and
2. the train-fitted analytic power law tests whether learning is needed at all.

For both controls, the complete family-bootstrap field interval for
`log(candidate field error / control field error)` must lie inside
`[-log(1.02), +log(1.02)]`. One-sided non-inferiority is insufficient: a
candidate with much better field accuracy would make a response improvement
mechanistically ambiguous.

At field equivalence, the candidate must reduce both paired-response and
discrete-tangent error relative to **each** control. This produces four primary
response contrasts. Every contrast needs:

- a one-sided 95% family-bootstrap lower bound above zero;
- a geometric mean error ratio of at least 1.10;
- a positive population contrast in at least four of five frozen seeds; and
- at least 59 of 100 family wins, whose one-sided Wilson lower bound exceeds
  0.5.

The four development contrast dispersions must each pass the prefield
`SD <= 0.2981054601` planning gate. A failed analytic comparison cannot be
removed, demoted to a secondary result or hidden behind a learned-control win.

## Raw rows, not a hand-authored summary

V2 exposed a `confirmation_pass(summary)` helper. That is useful for contract
tests but too permissive for final evidence because the summary can be supplied
without proving a complete factorial evaluation. V3 derives its summary only
from long-form error rows with exactly these factors:

`family × case × 5 frozen seeds × {candidate, direct, power_law} ×`
`{field, paired response, tangent}`.

For every selected family, all models, metrics and seeds must share the same
nonempty case set. There must be exactly one row per factor cell and no missing,
duplicate, extra-family, nonfinite or negative entry. Because the analytic
power law has no training randomness, its replicated seed rows must be bitwise
identical. Any violation produces execution-incomplete/no-verdict rather than
partial aggregation.

Case log-error ratios are averaged within family and seed, then across all five
seeds to one row per base family. Nodes, flows, cases, deformations and seeds do
not become independent replicates. The reported ratio is the exponential of
the mean of exactly 100 family log contrasts.

## Deterministic resampling

The 10,000 family bootstraps use one shared set of family-index draws for every
endpoint and comparator. Indices come from a SHA-256 counter stream with
unsigned-64 rejection sampling, avoiding modulo bias and library-specific PRNG
state. The interval uses the explicit Hyndman--Fan type-7 linear quantile at
0.05 or 0.95. The bootstrap supports the frozen pass rule; it is not relabelled
as an exact p-value or a proof of nominal coverage.

## Failure-revealing figure

Rank a family by its weaker comparator: the minimum of its direct-control and
power-law average paired/tangent response contrasts. Show minimum, median and
maximum ranked families as candidate worst, typical and best. Each row contains
reference, same-backbone direct, analytic power-law and candidate panels under
the same coordinates, camera and reference-derived colour scale. The display
seed, case and flow are fixed prospectively.

This prevents a favourable learned-control comparison from hiding a failure
against the analytic baseline.

## Synthetic adversarial checks

The evaluator is tested on deliberately hostile fixtures:

- a candidate that beats direct but loses to power law must fail;
- a candidate with a large response mean driven by only 40 winning families
  must fail;
- a candidate with materially better field error must fail the matched-mechanism
  claim rather than pass by one-sided non-inferiority;
- missing, duplicate or extra rows and power-law seed drift must fail closed;
  and
- prefield precision or compute failure must remain non-compensatory.

These are synthetic software checks, not Aneumo results.

The dependency-complete public regression passes 570/570 tests. The central
machine protocol retains 111 invariant groups at canonical SHA-256
`d3d1d6d9c066511f5bac6ef97a64c737b9db9c40de0f6c3b3de10996f6f763f6`.

## ISBI paper consequence

If future evidence passes, the four-page paper can support one compact chain:

> matched field accuracy against learned and analytic controls -> response
> failure of both controls -> same-backbone anchor-identity mechanism ->
> majority-family independent confirmation.

If the candidate does not beat the power law, the application method claim is
deleted. If field equivalence fails, the response-specific mechanism claim is
deleted. Neither outcome is repaired by renaming the model or changing the
comparison after result access.

## Current boundary

V3 is a non-executable synthetic contract. Real P0 remains 0/11. P1, bounded
development, fresh re-entry, eligibility metadata, manifest, field, prediction,
server query, PBS/GPU, result and paper claim are zero. Do not retry `introai9`
before a verified external service or administrator change, and never access
`junjinyong`.
