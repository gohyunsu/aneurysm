# Aneumo response-fidelity independent-confirmation design

> **Superseded before evidence on 2026-08-13:** This v1 design remains immutable
> history. No confirmation metadata, field or prediction was read. Current
> inactive [v2](../configs/aneumo_response_fidelity_confirmation_template_v2.json)
> adds a prefield precision/complete-workload viability gate, exact case-log to
> family geometric estimators and a majority-family Wilson safeguard. See the
> [v2 red-team](response-fidelity-confirmation-red-team-2026-08-13.md).

Status: **inactive, non-authoritative template; blocked on real P0, P1 v3,
bounded development and fresh re-entry; no data, model, compute or claim**  
Decision date: 2026-08-12 KST

## Decision

The previous phrase “at least 50 untouched families” was not a complete
confirmatory contract. It left sample-size enlargement, reuse of the six
historical compact-test families, within-family weighting, seed handling,
inference and visual-case selection open. Those choices could change after a
development result and therefore weaken RF-C3.

The inactive
[`confirmation template v1`](../configs/aneumo_response_fidelity_confirmation_template_v1.json)
closes those choices prospectively. It does not register or execute an outer
test. It can be replaced only before any confirmation metadata, field or
prediction is read and with a new evidence version.

## Sample contract

The future primary confirmation requires **exactly 100 new Aneumo generation
base families**. All 32 historical compact families—including the six old test
families—are excluded and cannot count toward 100. The release reports hundreds
of base geometries, so 100 is a feasible inference-only target while remaining
large enough to avoid presenting a six-family result as independent evidence.
It is a fixed precision-oriented benchmark size, not a formal power claim.

Eligibility and selection may use only release identifiers, lineage and archive
member metadata such as name, size, CRC and eight-flow completeness. Velocity,
pressure, response endpoints, predictions, model errors, rupture status and
clinical variables are forbidden. Eligible nonhistorical family IDs are sorted
by SHA-256 of `2027081301:<exact family ID>` and the first 100 are taken. The
manifest and hashes must be public before any selected-family field is read.

Use every release case with complete eight-flow alignment in each selected
family and all target flows. If fewer than 100 eligible families exist, or a
locked family later becomes missing or corrupt, close the exact version without
replacement, sample-size reduction or partial aggregation.

## Independent unit and aggregation

The independent unit is a generation base family, not a node, flow, deformation
or training seed. Aggregation order is fixed:

1. compute node-weighted error within a case and target flow;
2. average over all nonanchor target flows;
3. average over every eligible case in a family;
4. average the five frozen-seed model contrasts within that family; and
5. resample 100 family rows only.

This gives equal weight to base families and prevents thousands of aligned
nodes or multiple deformations from manufacturing a large sample size.

## Frozen comparison and primary conjunction

No confirmation training, tuning or checkpoint selection is allowed. Before
field access, freeze exact container, preprocessing, evaluator and five
checkpoint hashes for:

- the fresh-reentry identity-preserving candidate;
- its same-backbone direct target-field control; and
- the train-fitted analytic power-law competence control.

The primary claim is an intersection–union conjunction; every row below must
pass. No secondary endpoint or descriptive architecture can compensate.

| Requirement | Family-level contrast | One-shot criterion |
|---|---|---|
| Field non-inferiority | `log(candidate field error / direct field error)` | one-sided 95% upper bound ≤ `log(1.02)` |
| Analytic competence | `log(candidate field error / power-law error)` | one-sided 95% upper bound ≤ `log(1.02)` |
| Paired-response superiority | `log(direct error / candidate error)` | one-sided 95% lower bound > 0, point ratio ≥1.10, positive in ≥4/5 seeds |
| Tangent superiority | `log(direct error / candidate error)` | one-sided 95% lower bound > 0, point ratio ≥1.10, positive in ≥4/5 seeds |

Bounds use 10,000 family-bootstrap replicates with seed `2027081302`, after
within-family seed averaging. Because all requirements are conjunctive, each
one-sided 95% bound is used in an intersection–union decision; no Holm rescue,
exact p-value or formal-power statement is registered. Inference is limited to
the eligible Aneumo release-family benchmark, not patients or clinical risk.

## Figure contract

A favourable example alone is not interpretable evidence. The future primary
figure must deterministically show three family roles based on the mean of the
two primary response contrasts:

1. minimum contrast: candidate worst case;
2. median contrast: typical case; and
3. maximum contrast: candidate best case.

Ties use the predeclared family hash order; the displayed case uses a
predeclared within-family hash order; the target flow is farthest from the
nominal flow on the log scale. Reference, direct and candidate panels share
coordinates, camera and a reference-derived colour range. The caption must
disclose the selection rule and role. These panels explain benchmark behaviour;
they are not clinical rupture-risk images.

## Compute and stopping boundary

Even after every upstream gate, confirmation is inference-only on `introai9`
PBS with a 40 GPU-hour ceiling. Login-node GPU and every `junjinyong` action are
forbidden. All 100 families, eligible cases, flows and five seeds are required.
After any confirmation field or prediction is read, sample, model, checkpoint,
margin, metric, seed, figure rule and stop rule are immutable. Execution-
incomplete closes with no verdict. Any field or co-primary response failure
deletes RF-C2/RF-C3 without narrative reversal.

## Current state

The template has synthetic validator tests only. Real P0 remains 0/11; P1 is
unregistered; no candidate, manifest, confirmation metadata, field, prediction,
server query, PBS/GPU job, result or paper claim exists. The historical six
compact test families remain sealed history and contribute zero qualified new
confirmation families.
