# AneuG-Flow reference-relative structure reappraisal

**Date:** 2026-08-14  
**Decision:** 31.0/40 inactive · fresh source-feasibility G0 registered · model/GPU/claim 0

## Executive judgment

Moving the required paper asset from Aneumo to AneuG-Flow is rational, but the
dataset switch is not itself a contribution. AneuG-Flow already publishes a
graph U-Net WSS baseline at 4.67% registered relative L2, and the literature
already covers equivariant transient-WSS prediction, Hodge/discrete-form
operators, robust critical-point tracking and trajectory preservation.
Likewise, the 2015 Challenge already established that CFD pipelines can produce
materially different WSS on the same anatomy. AURORA may claim none of those
ingredients or observations as new.

The defensible residual question is narrower:

> When field error is matched, does a learned transient-WSS surrogate add
> signed critical-point and worldline error beyond the variability observed
> between independent CFD pipelines on the same aneurysm anatomy?

This is **reference-relative structural fidelity**. Its novelty would be the
validation criterion and the linked failure/correction evidence, not a renamed
GNN, topology loss or discovery of solver variability.

## Dataset roles after the reappraisal

| Source | Permitted role | Prohibited interpretation |
|---|---|---|
| AneuG-Flow | conditional main development/evaluation source after lineage audit | 730 cases are not 730 patients; common topology is not proof of independent geometry |
| 2015 Aneurysm CFD Challenge | within-anatomy inter-solver structural-variability floor | 28 submissions are not 28 anatomies; this is not a training cohort or standalone novelty |
| AneuX | real-shape morphology support and representation/OOD stability | no WSS performance, transient validation or clinical endpoint |
| Aneumo | optional comparison after authoritative mapping and licence resolution | no required dependency and no reactivation of withdrawn panels |

The AneuG and Challenge licences are materially clearer than the conflicting
Aneumo declarations. AneuX remains noncommercial and geometry-only. This is a
source-role judgment, not legal advice.

## Why canonical topology is both useful and dangerous

AneuG maps cases to a common node count and connectivity. This makes phase-wise
critical-point tracking and vertex-aligned comparison much easier. The same
property can also hide two failure modes:

1. a model can exploit registration coordinates rather than learn geometry;
2. related generated shapes can cross train/test boundaries if their parent or
   latent lineage is unknown.

Therefore a random case split, prefix split or timestep split is invalid for
the proposed claim. An official parent/latent mapping is preferred. If none is
released, a geometry-only near-duplicate/cluster split must be frozen before
any WSS/model access and reported as a conservative surrogate grouping—not as
true patient lineage.

## Why the 2015 Challenge is a control, not a second test set

The Challenge contains five independent anatomies and multiple submitted CFD
solutions per anatomy. The correct hierarchy is anatomy at the top and solver
submission nested within anatomy. It can estimate a structural disagreement
range for a fixed anatomy, but it cannot estimate population generalization or
transient surrogate performance by itself.

The desired normalized endpoint is conceptually:

```text
excess structure error
  = surrogate-to-reference structural discrepancy
    minus within-anatomy inter-solver structural discrepancy
```

The exact estimator cannot be chosen until archive coordinates, normalization,
surface correspondence and available WSS representation are audited. A ratio
or subtraction is not automatically valid when solver outputs live on
different meshes; remeshing and uncertainty propagation are mandatory controls.

## Frozen score

| Axis | Score | Reason |
|---|---:|---|
| Biomedical importance | 4.5 | Flow organization is relevant, but no clinical outcome is available. |
| Identifiable estimand | 4.0 | Vector WSS and surfaces exist; cross-solver correspondence remains unaudited. |
| Residual novelty | 2.5 | Only the reference-relative learned-surrogate validation conjunction remains. |
| Asset readiness | 4.0 | Geometry-only AneuG bundles are local, but the transient WSS target is not confirmed. |
| Independent unit | 3.0 | Five Challenge anatomies are known; AneuG generator lineage is unresolved. |
| Strong baselines | 5.0 | Official graph U-Net and mesh/equivariant/Hodge controls are feasible in principle. |
| Interpretable evidence | 5.0 | Matched surfaces, critical points and tracks can be shown directly. |
| ISBI schedule fit | 3.0 | AneuG is 2.63 TB and cross-mesh solver calibration is nontrivial. |
| **Total** | **31.0/40** | **Below admission; source-feasibility evidence may trigger rescoring only.** |

The score is lower than the historical 32.0/40 AneuG surface-vector version
because the earlier 4.5 independent-unit score treated 730 reported synthetic
geometries too generously. It is not repaired by adding the Challenge: five
actual anatomies improve interpretation but do not establish AneuG lineage.

## Fresh G0: what is now registered

The machine contract
[`aneug_reference_floor_g0_v1.json`](../configs/aneug_reference_floor_g0_v1.json)
asks a new source question and does not rerun historical job `115645`.
It inventories the exact AneuG transient repository tree without downloading
mesh or field payloads, reports whether an explicit parent/latent manifest is
present, verifies the exact 2015 WSS archive and lists tar member names without
extracting fields, and verifies AneuX metadata without payload access.

The bounded introai9 inventory before registration found historical AneuG code,
configs and execution records, but no confirmed AneuG payload in that legacy
project scope. A later audit outside that root corrected the account-wide
interpretation: a verified geometry archive is materialized, with 14,710
complete three-file bundles among 14,712 directories, while the transient WSS
target remains unconfirmed. The separate reconciliation is documented in
[`introai9-acquired-asset-reconciliation-2026-08-14.md`](introai9-acquired-asset-reconciliation-2026-08-14.md).
Geometry availability improves immediate lineage engineering but does not
resolve field-target availability, generator independence or the G0 question.

G0 requests CPU 4, 8 GB, GPU 0 for one PBS attempt. Pass, failure or transport
incompleteness closes the exact contract without repair/rerun. Even a complete
G0 authorizes only human rescoring and a separately registered geometry-lineage
or method-free structure-stability audit. It cannot select an architecture,
read AneuG WSS fields, train a model, access an outer test or activate a paper
claim.

## Evidence ladder if and only if the source audit is adequate

```text
G0 · release lineage + Challenge archive feasibility
  └─ adequate → fresh score and independent-unit ruling
      └─ admitted → geometry-only leakage/near-duplicate audit
          └─ stable split → method-free critical-point/worldline audit
              └─ stable target → field-error-matched baseline failure screen
                  └─ excess structural error above solver floor
                      → minimal mechanism-linked method development
                          → untouched lineage-disjoint confirmation
```

The first method, if the ladder reaches it, must be the smallest correction
that addresses the observed failure. Oriented edge 1-forms, tangent projection,
Hodge components, equivariance and temporal decoding remain candidate controls,
not a preselected architecture or contribution.

## ISBI claim activation conditions

An application paper becomes defensible only if all three statements receive
prospective evidence:

1. robust critical structure is identifiable across AneuG phase, tolerance,
   mesh and bounded field perturbation;
2. strong field-error/compute-matched baselines add structural error beyond the
   Challenge-derived within-anatomy solver floor;
3. one minimal mechanism-linked change reduces that excess error without
   materially worsening vector-field accuracy on untouched lineage-disjoint
   units.

Failure at any stage closes or narrows the claim. Rupture risk, patient-specific
physiology and clinical utility remain out of scope.
