# Aneumo transient structure re-entry after the closed response-fidelity P0

**Decision date:** 2026-08-13 KST  
**Target:** IEEE ISBI 2027  
**Decision:** **30.0/40 inactive re-entry candidate; D0 development only**

## Decision

The steady response-fidelity identity is closed. Its one allowed P0 v3 attempt
ended before any of 12 scientific checks were evaluated. The 32.5/40 score is
historical source provenance, not a reusable lead and not evidence that a
nearby formulation should be repaired.

The best remaining use of an acquired asset is the public Aneumo transient WSS
release. The candidate question is:

> Are signed critical structures in transient aneurysm-surface WSS stable to
> reasonable discretization and bounded perturbation; if so, do field-error-
> and compute-matched surrogates destroy that organization?

This remains below the 32-point admission threshold because target stability,
units, release-wide tangency and executable strong controls are unresolved.
The first action is therefore D0 reader/extractor development on two members
already inspected in the release audit—not a scientific P0 and not model
training.

## Direct-prior subtraction

| Primary source | Occupied contribution | Consequence |
|---|---|---|
| [Hodge Spectral Duality](https://arxiv.org/abs/2605.13834) | Discrete differential forms, Hodge splitting and topology-preserving operators on meshes | Hodge/edge-form architecture is a control |
| [SE(3) artery-wall mesh network](https://arxiv.org/abs/2212.05023) | Directional transient WSS prediction on surface meshes | Equivariance and vector WSS are controls |
| [RHSIA](https://arxiv.org/abs/2601.19876) | Aneurysm-surface Graph Transformer with temporal WSS supervision | GNN/Transformer/temporal input is not novelty |
| [Critical-point-trajectory compression](https://arxiv.org/abs/2510.25143) | Exact preservation of time-varying critical-point trajectories | Worldline preservation is occupied generically |
| [FaCTz](https://arxiv.org/abs/2608.10586) | GPU error-bounded compression with guaranteed critical-point preservation | Fast topology preservation is also occupied |
| [Karnam et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11315625/) | Phasewise WSS critical points, cardiac-cycle tracking and influence fields in 359 lesions | Extraction/tracking and aneurysm relevance are direct prior |

The architecture sketch—GNN, SE(3), edge 1-form, Hodge components, periodic
decoder and topology loss—therefore has no independent novelty. The residual
application intersection requires all of the following:

1. a method-free, robust target rather than matcher-dependent labels;
2. a material structural failure after field-error and compute matching;
3. a minimal correction directly linked to the observed failure;
4. family-level evidence without clinical or patient-level overclaim.

## Candidate score

The fixed axes are biomedical importance, target identifiability, residual
novelty, usable asset readiness, independent-unit strength, strong-baseline
feasibility, interpretable-figure value and ISBI schedule fit.

| Axis | Score | Reason |
|---|---:|---|
| Importance | 4.5 | WSS direction organizes near-wall flow |
| Identifiability | 4.0 | vector target observed locally; stability unresolved |
| Residual novelty | 2.5 | only the matched aneurysm application conjunction remains |
| Asset readiness | 4.0 | 966 complete cases across 40 families |
| Independent units | 3.0 | only 40 released base families |
| Strong baselines | 3.5 | direct-prior controls exist but executable matched bundle is absent |
| Figure value | 5.0 | vector fields, signed zeros and tracks are interpretable |
| Schedule | 3.5 | extraction/license/baseline gates can still terminate the work |
| **Total** | **30.0/40** | **inactive; admission remains 32** |

FaCTz does not lower the score further because trajectory-preserving
compression already occupied the generic preservation claim. It reinforces
that the proposal cannot be “a topology-preserving model.” Conversely,
administrator recovery changes executability, not scientific novelty, so it
does not raise the score.

## D0 contract

[`aneumo_transient_vtp_d0.json`](../configs/aneumo_transient_vtp_d0.json)
froze case 1 phases `4.01` and `5.00`, whose exact VTP hashes were already
observed. Its sole PBS job `116160.ECE-util1` ended E/exit 1 after 12:10 with
CPU 1 second and GPU 0 because the compute node returned network unreachable
before the first bounded range response. No VTP payload was obtained; the
reader, extractor and scientific stability gate were not evaluated. The
460-byte status SHA-256 is `6fa462f0…e0a`.

The final transport-only repair
[`aneumo_transient_vtp_d0_v2.json`](../configs/aneumo_transient_vtp_d0_v2.json)
keeps the same two members, hashes, reader, extractor and no-threshold checks.
It changes only member delivery: exact hash-verified bytes are placed in a
private ephemeral stage, PBS performs zero HTTP requests, and the wrapper
deletes the two staged files after the attempt. This is development repair
2/2. No further D0 repair or resubmission is allowed. D0 verifies:

- exact bounded ZIP member extraction and CRC/hash integrity;
- fail-closed VTK XML parsing;
- point/polygon and three-component WSS contracts;
- Newell and triangle-area normals;
- two deterministic polygon fan triangulations;
- signed nondegenerate critical-point extraction.

It reports counts and extractor agreement descriptively, with no stability
threshold. A pass authorizes only registration of a new family-disjoint,
method-free P0. It cannot change the case, phases or scientific claim.

## Scientific P0 that may follow

A future P0 must be registered before any new case/phase field read. It should
select cases by base family from metadata alone and freeze:

- normal construction and two plausible triangulations;
- tangency and nondegeneracy margins;
- spatial matching radius and temporal resampling;
- perturbation magnitudes derived independently of observed critical points;
- family-level pass/fail aggregation;
- maximum bytes, walltime and one-shot policy.

Primary P0 endpoints are bidirectional signed critical-point recall, total
index discrepancy, trajectory distance and birth/death event agreement. Empty
or sparse structures, triangulation sensitivity, perturbation instability or
boundary ambiguity close the direction.

## Architecture only after a matched failure

If P0 passes, P1 first compares Cartesian, tangent-projected, equivariant mesh
and Hodge/discrete-form controls at matched compute and vector-field error.
Only an observed structural separation can justify a candidate. The smallest
defensible change is an oriented edge-integral output with explicit tangent
reconstruction; a local degree-margin term is optional only for stable,
nondegenerate zeros. Hodge and equivariance remain controls.

The final claim would be an application/evaluation contribution, not a new
general topology-preserving neural operator. The paper is rejected internally
if field error explains the effect, HSD/trajectory-aware controls remove it,
or improvement is confined to a minority of families.

## License and interpretation boundary

The Hugging Face dataset tag says CC BY-NC-ND 4.0, while the pinned GitHub
datasheet says CC BY 4.0 and invites downstream ML research. No legal
conclusion is made. Until the maintainers clarify the exact transient payload,
AURORA applies the stricter noncommercial and nonredistribution boundary:
field members are ephemeral, raw/derived fields and weights are not published,
and only non-identifying aggregate development evidence is retained.

No rupture, treatment, clinical validity or patient-specific physiology claim
is permitted. The independent unit is the Aneumo generation family, not a
phase, vertex, triangle, critical point or synthetic deformation.
