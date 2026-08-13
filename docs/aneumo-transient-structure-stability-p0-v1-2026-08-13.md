# Aneumo transient signed-structure stability P0 v1

**Status:** withdrawn before field access

**Reason:** exact release licence declarations conflict and the official family
mapping is not authoritative
**Model/GPU/paper authority:** none

## Question

Before learning a WSS surrogate, determine whether its proposed structural
target is identifiable. The primary question is not whether two extractors
return the same number of zeros. It is whether signed critical-point locations
remain mutually recoverable under plausible polygon triangulation, normal
construction and a small tangent-field perturbation.

## Historical field-blind panel

Official Connection.csv at commit 701d53d… hashes to 09a5344a…d0b.
Using only that mapping and release-directory completeness metadata, P0
excludes D0 family 1, hash-ranks the other 39 eligible families and freezes 12
families. One canonical complete case per family is hash-selected; five phases
(4.01, 4.25, 4.50, 4.75, 5.00) yield 60 future members. No selected P0 field
has been staged or read. This panel is preserved as provenance and cannot be
activated.

## Non-compensatory phase gates

Each phase uses Newell and triangle-area point normals, first- and last-vertex
polygon fans, tangent projection, a 0.02 barycentric interior margin and a
scale-relative degeneracy floor. The primary matching radius is twice the
median surface-edge length; one- and four-edge radii are sensitivity outputs.

A phase must simultaneously satisfy:

1. at least two nondegenerate critical points in every configuration;
2. tangency median at most 0.02 and p95 at most 0.10;
3. minimum pairwise bidirectional signed recall at least 0.80;
4. critical-point count range at most one and exact total signed-index
   agreement;
5. at least seven of eight deterministic 1%-RMS, three-step mesh-smoothed
   tangent perturbations meeting the same recall, count and index safeguards.
   The 0.5% and 2% amplitudes are frozen sensitivity curves and cannot rescue
   the primary 1% gate.

Equal count or total index cannot rescue poor spatial recall. A family passes
only if its mesh is phase-static and at least four of five phases are both
informative and fully passing. P0 passes only if at least 10 of 12 families
pass. Missing or duplicate members make execution incomplete; scientific
failure closes the transient direction without model or threshold repair.

## Why v1 was withdrawn

The Hugging Face card declares CC BY-NC-ND 4.0 while the official GitHub
datasheet declares CC BY 4.0. Applying stricter private handling is not an
authoritative resolution.

Separately, the dataset owner acknowledged in official issue 4 that cases 2158
and 2159 should map to family 115 rather than 114, then promised a complete
mapping review. The latest official commit remains the earlier partial update:
its pinned Connection.csv still assigns case 2158 to `114_deform_10`, while
2159 starts `115_deform_1`. The known cases are outside transient 1--1000, but
there is no evidence that the first 1,000 rows have passed the promised full
review. Therefore the family inference unit is unverified.

V1 is withdrawn with staged/read field 0/60. It cannot be activated later. A
successor may be selected only from an authoritatively corrected mapping and
after the separate licence conflict is resolved, and it would require a fresh
public contract and private manifest before field access.

No GNN, Hodge operator, edge 1-form, topology loss, tracking, GPU, outer test
or paper claim is authorized. A P0 pass would permit only registration of a
compute- and field-error-matched baseline-failure P1. junjinyong remains
completely excluded.
