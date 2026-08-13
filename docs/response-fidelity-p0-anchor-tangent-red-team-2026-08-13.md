# Aneumo response-fidelity P0 anchor-tangent red team

**Decision date:** 2026-08-13

**Evidence type:** synthetic contract test only; no Aneumo field was read

**Current scientific status:** P0 v3 registered but non-executable, 0/12 checks

**Compute status:** no server query, PBS submission, GPU use, model, result, or claim

## Decision

Preserve the unexecuted P0 v2 byte-for-byte and supersede it with a fresh P0
v3 contract. V2 correctly excluded interpolation error at the nominal anchor,
where the anchor-relative response is exactly zero, but the same loop also
excluded the anchor from the discrete-tangent stability audit. That omission is
material because the primary P1 endpoint includes the anchor tangent and the
candidate mechanism explicitly enforces identity at that anchor.

This is a prospective contract correction, not a repair of observed data and
not evidence that Aneumo is stable or unstable. The exact private compact-cache
path remains unresolved and no real P0 check has been evaluated.

## Preserved evidence versions

| Item | SHA-256 | Status |
|---|---|---|
| `configs/aneumo_response_fidelity_p0_v2.json` | `b82b3bfd3d83713f375378f471ec506e7b8437fd470e98366534d4cb1d021381` | preserved, unexecuted |
| `src/aurora/aneumo_response_fidelity_p0.py` | `3f9667329b2f7f61850eddbd5b118c8cab0520cccb86a3382ecfebf6cc292790` | preserved v2 evaluator |

P0 v1 remains the earlier superseded Spearman-only contract. V2 remains the
second historical evidence version; its thresholds, parser, split, evaluator,
and 11 checks are not edited or re-labelled.

## The exact loophole

For every interior flow, v2 computed interpolation and one-sided tangent
diagnostics inside one loop. It skipped the anchor index before both operations.
Skipping interpolation at the anchor is necessary: its anchor-relative response
has zero denominator. Skipping the tangent is not necessary: left and right
one-sided differences are finite and test whether the sampled response curve is
locally coherent exactly where the proposed residual head claims an identity
constraint.

A global or non-anchor tangent summary cannot substitute for this check. A
localized kink at the anchor can leave all non-anchor tangents essentially
unchanged while weakening the mechanism's central endpoint.

## Registered negative control

A deterministic 20-family, two-deformation synthetic fixture was perturbed only
at the anchor field. With the registered 5,000 family-cluster bootstrap draws:

| Contract quantity | Observed synthetic value |
|---|---:|
| v2 all registered checks | 11/11 pass |
| v2 flow-stratified response-descriptor Spearman CI lower | 0.805536878291973 |
| v2 non-anchor tangent agreement CI lower | 0.9999441120650744 |
| omitted anchor-tangent median | 0.7987704542950331 |

The same fixture is a negative contract control only. It is deliberately not an
Aneumo result, a model result, a threshold estimate, or a paper contribution.

## P0 v3 correction

V3 inherits all 11 v2 checks and adds one non-compensatory twelfth check:

> In each coordinate-hash half, compare both one-sided anchor tangents with the
> secant joining the neighbouring flows; family-cluster bootstrap the per-family
> median and require its 95% CI lower bound to be at least 0.80.

The 0.80 threshold, 5,000 bootstrap count, seed, train-only data boundary, cache
checksum, endpoints, and family unit were fixed before any real cache access.
The unit label is clarified from a vague historical phrase to
`aneumo_generation_family`; case, flow, and node are never independent units.

V3 is fail-closed until both conditions are independently verified:

1. an external introai9 service or administrator state change; and
2. the exact absolute path of the already-verified compact cache.

Only one bounded checksum/path preflight may follow such a change. Scientific
execution, if later authorized, is CPU-only through introai9 PBS. Login-node GPU
commands are forbidden and `junjinyong` must never be accessed.

## Downstream consequence

A real 12/12 P0 v3 pass would authorize only registration of a **new**
baseline-only P1 evidence version. It does not activate the historical P1 v1,
v2, or v3 templates, choose LaB-GATr, authorize GPU training, expose validation
or test fields, or open the 100-family confirmation. The existing confirmation
v1--v3 designs likewise remain immutable, inactive planning history; a fresh
downstream version must inherit the 12-check prerequisite.

If any real v3 check fails, close this exact response-fidelity direction without
threshold, parser, split, source, or anchor repair. If v3 passes but a fresh
field-error-matched P1 does not show the registered response mismatch, close the
direction rather than manufacture an architectural novelty claim.
