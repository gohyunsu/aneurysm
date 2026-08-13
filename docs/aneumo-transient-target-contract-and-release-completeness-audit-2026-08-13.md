# Aneumo transient target contract and release-completeness audit

> **Decision · 2026-08-13 KST:** the public transient release is substantially
> more usable than the earlier one-case directory probe established. A bounded
> audit of all case IDs 1--1000 finds **966 complete cycle cases** spanning all
> **40 base families**. Selective wall-file probes confirm a three-component
> `wallShearStress` array and phase-static surface connectivity in one complete
> case. This raises structure-faithful transient WSS from historical 28.0 to
> **30.0/40**, but it remains below the fixed 32-point admission line. License,
> units, polygon/tangency stability and method-free critical-structure
> identifiability remain unresolved. No task, P0, architecture, server job,
> GPU experiment, result or manuscript claim is opened.

## 1. The question this audit answers

The old audit answered only a narrow question: does the official public state
contain a transient archive with recognisable time and wall-file structure?
It inspected one nested case directory and correctly stopped before inferring
that all 1,000 cases were complete or that the wall files contained a usable
vector target.

This audit asks two stronger but deliberately separate questions.

1. **Release completeness:** across all 1,000 case archives, which cases have
   the documented `4.01`--`5.00` cycle and exactly one identifiable wall
   surface per observed phase?
2. **Selective target plausibility:** in a small, explicitly identified sample
   of wall files, is WSS actually a three-component array on a phase-consistent
   surface, and is it approximately tangent?

The first question uses directory metadata only. The second reads four wall
files. Evidence from the four files is never generalized to all 966 cases.

## 2. Exact source and bounded transport

The audit pins official GitHub commit
[`701d53d`](https://github.com/Xigui-Li/Aneumo/tree/701d53dde3489d84dbe9bc8324254629162eb45a)
and Hugging Face revision
[`f801ade`](https://huggingface.co/datasets/SAIS-Life-Science/Aneumo/tree/f801adee816c18d3e18b23e6fcb147fe4c264209).
The release is several terabytes, so full staging would be wasteful before a
scientific gate.

The reproducible auditor
[`scripts/audit_aneumo_transient_archives.py`](../scripts/audit_aneumo_transient_archives.py)
therefore fails closed unless the server returns HTTP 206 byte ranges. For each
of 100 outer batch ZIPs it reads the final central-directory window; for each
of 1,000 nested case ZIPs it reads one local-header window and one final
central-directory window. It does not read any nested VTP/VTU member payload.

| Transport item | Frozen value |
|---|---:|
| HTTP range requests | 2,100 |
| Bytes received | 72,217,600 |
| Hard byte ceiling | 100,000,000 |
| Tail window | 65,536 bytes |
| Inner scientific file payload | 0 |
| Raw audit JSON SHA-256 | `f3b909773338ea943db8e24ec1b0e0471389b8a2f7da935c4ad3553fd794962a` |
| Canonical case-record SHA-256 | `8f516cd39c5bb0fb83293f19ff95d996f2299ebd6848d4609ced8aa9dbbde424` |

The raw output is not treated as a result table. It is release metadata. The
compact machine decision is
[`configs/aneumo_transient_target_contract_reappraisal_v2.json`](../configs/aneumo_transient_target_contract_reappraisal_v2.json).

## 3. Whole-release result

Every observed time directory has exactly four files and exactly one VTP that
is neither the inlet nor outlet surface. The important differences are cycle
completeness and whether the wall filename matches the official code's exact
`{time}_wall.vtp` assumption.

| Contract | Cases | Interpretation |
|---|---:|---|
| `0.00` plus complete `4.01`--`5.00` cycle | **966** | directory-level structural target candidate |
| Zero-based contiguous partial/alternate sequence | 32 | not the documented complete cycle |
| Irregular sequence | 2 | not the documented complete cycle |
| Exact official wall-filename convention among complete cases | **961** | usable by the current filename lookup in principle |
| Complete cycle but noncanonical wall name | 5 | usable only with a corrected, manifest-driven reader |

The 34 incomplete case IDs are:

`7, 28, 93, 103, 167, 234, 236, 238, 251, 259, 260, 273, 354, 361, 471, 477, 512, 522, 524, 533, 586, 599, 629, 630, 668, 673, 702, 796, 808, 825, 843, 908, 944, 972`.

The five complete but noncanonical-wall cases are `4, 9, 15, 583, 728`.
They are not counted as incomplete. Hence `961 + 5 = 966`, while
`966 + 34 = 1000`.

All 40 base families have at least one complete structural case and at least
one case compatible with the official filename convention. This removes the
earlier concern that complete-cycle filtering might erase an entire family.
It does **not** turn 1,000 cases into 1,000 independent subjects. Family remains
the only defensible independent inference unit.

## 4. What four wall files establish—and what they do not

Two phases from complete-cycle case 1 (`4.01`, `5.00`) and two phases from
partial-sequence case 7 (`0.20`, `0.26`) were extracted by exact compressed
byte range and checked against their ZIP CRC. Both point and cell data expose
scalar `p`, three-component `U` and three-component `wallShearStress` arrays.

For case 1, the two phases have 9,399 points and 4,701 polygons. Point bytes,
connectivity and offsets are byte-identical across the phases, while WSS bytes
change. This is direct evidence of a phase-static surface and a time-varying
vector target in that case. Case 7 shows the same qualitative contract with
10,184 points and 5,097 polygons.

The meshes are polygonal rather than triangular: observed faces have four to
nine vertices. A signed triangle-interior critical-point extractor therefore
needs a deterministic triangulation rule, and conclusions must be tested
against plausible triangulations rather than hidden in preprocessing.

Using Newell polygon normals aggregated to points, the selected case-1 phases
have median absolute normal WSS fractions of about 0.0042 and 95th percentiles
near 0.036. This supports “mostly tangent” on the inspected phases. The 99th
percentiles are approximately 0.34 and maxima are much larger, so the local
tail may reflect non-manifold/boundary geometry, normal estimation, point/cell
interpolation or real storage convention. It is not acceptable to call the
full release tangent-clean yet.

The VTP and datasheet do not state a WSS unit unambiguously. Numeric values must
not be labelled Pa, dyn/cm² or another unit by inference from a threshold in
example code.

## 5. Official preprocessor failure modes

The official preprocessor first calls a case complete when directories
`4.01`--`5.00` exist. Its later step discovery includes *all* numeric
directories, including `0.00`, so a case documented as 100 cycle phases can be
written with 101 timesteps. This is a contract mismatch, not proof that either
choice is scientifically wrong.

The wall reader constructs the canonical filename directly. In the five
noncanonical cases, wall indices can become empty and downstream WSS can become
empty or zero-like without a hard, case-level rejection. The official cross
evaluator makes the same canonical-name assumption. A new study must build a
manifest-driven, fail-closed reader and freeze whether `0.00` is an initial
condition or part of the model target.

These are engineering requirements, not novelty claims.

## 6. Why the score rises only to 30.0/40

| Axis | Old | New | Reason for change or cap |
|---|---:|---:|---|
| Biomedical importance | 4.5 | 4.5 | directional wall-flow organization remains meaningful |
| Target identifiability | 3.0 | 4.0 | vector WSS and phase-static mesh observed, but units/tail/stability unresolved |
| Residual novelty | 2.5 | 2.5 | direct-prior boundary is unchanged |
| Usable asset readiness | 3.0 | 4.0 | 966 complete cases across all 40 families verified |
| Effective independent units | 3.0 | 3.0 | still only 40 generation families |
| Strong-baseline feasibility | 3.5 | 3.5 | official controls remain scalar, family-leaky and partially broken |
| Interpretable figure value | 5.0 | 5.0 | vector fields, critical points and tracks are visually testable |
| ISBI schedule fit | 3.5 | 3.5 | license and method-free stability can still terminate the direction |
| **Total** | **28.0** | **30.0** | **inactive; fixed admission is 32.0** |

This is a near-threshold re-entry candidate, not an invitation to combine
equivariance, Hodge blocks and topology losses. Those ingredients and
critical-point/worldline tracking are already direct prior. The remaining
application gap is conditional:

> At matched vector-field error and compute, do strong transient WSS
> surrogates disagree on *robust* signed critical structures and worldlines,
> and does a minimal correction improve those endpoints without reducing field
> accuracy?

The word *robust* is essential. If the reference structures change under a
reasonable triangulation, normal construction, tolerance or bounded field
perturbation, there is no stable target for a fancy model to preserve.

## 7. Next admissible evidence, in order

1. Resolve the exact payload licence through an authoritative statement. The
   Hugging Face card says CC BY-NC-ND 4.0 while the pinned GitHub datasheet says
   CC BY 4.0. This audit makes no legal conclusion.
2. Register a method-free target-identifiability audit before reading more
   fields. Freeze polygon triangulations, normal construction, critical-point
   tolerance, matching radius and perturbation magnitudes.
3. On family-disjoint development only, measure critical-point existence,
   signed-index agreement, track stability and birth/death stability. Failure
   closes the direction; thresholds are not repaired after seeing results.
4. Only after stability, establish executable compute-matched vector controls:
   Cartesian/tangent projection, directional equivariant mesh prediction and
   Hodge/discrete-form controls.
5. Only after a matched-field structural failure is observed may a minimal
   model change be selected. Architecture components are justified by that
   failure mechanism, never by appearance.

The current steady response-fidelity direction remains the sole conditional
lead at 32.5/40 and immutable real P0 v3 remains 0/12. This source audit is not
an `introai9` operational recovery signal. No server or scheduler was queried,
no job was submitted and no GPU was used. `junjinyong` was not accessed and
remains prohibited.
