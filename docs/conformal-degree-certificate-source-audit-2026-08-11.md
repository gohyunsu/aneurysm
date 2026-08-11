# Patient-level conformal degree certificates for surface WSS

> **Execution outcome override · schema 8.0 · 2026-08-11 KST:** Exact source
> `4a0fa65b…` ran once as `introai9` CPU/PBS job `115684.ECE-util1` and ended
> `E`/exit 2 after 00:40:06 with GPU 0. Its bounded status/result report
> `execution-incomplete/no scientific verdict`; 0/10 registered checks were
> evaluated. Complete archive integrity and VTP access were not reported,
> transient partial bytes are unknown, and no payload or raw scheduler log
> persisted. The low-level cause is unresolved. Preserve 32.5/40 as source
> history but close this exact candidate without repair/rerun, P1, method,
> architecture, GPU, outer test or paper claim. See the
> [deidentified execution record](../results/aneurisk_conformal_degree_p0_execution_20260811.json).

> **Prospective source decision · schema 7.9 · 2026-08-11 KST:** A fresh
> problem-level screen admits
> `patient_level_conformal_degree_certificate_for_surface_wss_surrogates` at
> **32.5/40** as one conditional source lead. This does not repair, rerun or
> relabel the closed surface-vector P0. It registers only a new method-free
> Aneurisk archive/semantics P0 on `introai9` PBS with CPU 4, memory 16 GB and
> GPU 0. Primary problem, method, architecture, outer test, numbered paper
> contribution and submission identity remain unselected.

## 1. The useful idea is a certificate, not another topology loss

The preceding surface-vector proposal asked whether field-error-matched WSS
surrogates preserve critical points and cardiac-cycle worldlines. That remains
an inactive hypothesis and its historical source scores and failed execution
are immutable. The present question is different:

> Can a learned tangent-vector field be accompanied by a patient-level,
> finite-sample certificate that identifies surface regions whose **signed
> total critical-point index** is guaranteed to agree with the unknown CFD
> field, while abstaining elsewhere?

Let \(S\) be an oriented surface patch, \(R\subset S\) a topological disk,
\(v\) the reference tangent field and \(\hat v\) a surrogate prediction in a
shared tangent trivialization. Suppose a split-conformal calibration over
exchangeable **patients** yields a simultaneous residual radius
\(q_{1-\alpha}\) satisfying

\[
  \Pr\{\lVert v-\hat v\rVert_{\infty,S}\le q_{1-\alpha}\}\ge 1-\alpha.
\]

If the predicted boundary margin obeys

\[
  \min_{x\in\partial R}\lVert \hat v(x)\rVert > q_{1-\alpha},
\]

then the straight-line homotopy between \(\hat v\) and \(v\) cannot cross zero
on \(\partial R\) on the coverage event. Their boundary maps have the same
degree, so

\[
  \deg(v,R,0)=\deg(\hat v,R,0).
\]

The certificate is model-agnostic. A nonzero certified degree implies at least
one reference-field zero inside the region. It does **not** certify the exact
number, coordinate, Jacobian, type or clinical meaning of individual critical
points. Those stronger statements require additional separation and
non-degeneracy assumptions and are not current claims.

Because the conformal event covers the whole field, every prediction-derived
region satisfying the registered margin test is covered simultaneously on that
event. Coverage remains marginal over exchangeable patients, not conditional
on aneurysm subtype, scanner, rupture status or a particular critical point.
Vertices, triangles, regions and detected zeros are never counted as
independent calibration units.

## 2. Why this is not a cosmetic repair

The historical 31.0/40 leader optimized or evaluated fixed-point fidelity. The
new estimand is the joint pair

1. **validity:** patient-level simultaneous field coverage and degree-certificate
   correctness; and
2. **efficiency:** certified surface/region fraction, abstention rate and
   certificate tightness at fixed \(\alpha\).

No change to a downloader, parser, loss or architecture creates this gap. The
new source screen adds an explicit inferential guarantee and new direct-prior
lineage. It does not reuse the AneuG three-probe contract and cannot alter job
`115645.ECE-util1`, its 32.0/40 history or its 0/10 no-verdict outcome.

## 3. Direct-prior boundary

The residual gap is narrow because all ingredients have strong predecessors.

- [Guaranteed Prediction Sets for Functional Surrogate Models](https://proceedings.mlr.press/v286/gray25a.html)
  already gives model-agnostic conformal prediction sets for PDE surrogate
  outputs through SVD error representations and set propagation.
- [Functional conformalized distance fields](https://arxiv.org/abs/2607.00776)
  already convert whole-field coverage into a downstream uniform safety
  statement. Whole-field conformalization is therefore not itself novel.
- [Conformal operator learning for Navier--Stokes](https://arxiv.org/abs/2606.08654)
  already targets simultaneous field coverage for a neural operator.
- [Uncertain 2D Vector Field Topology](https://diglib.eg.org/items/7a4a3a9f-999e-431f-85f0-efde93411798)
  and [multilevel robustness](https://doi.org/10.1111/cgf.14799) already model
  uncertain vector-field topology and robustness of critical points.
- Hodge Spectral Duality, SE(3)-equivariant transient WSS prediction, RHSIA,
  deterministic critical-point extraction/tracking and the Aneurisk companion
  paper's cycle-averaged fixed-point analysis remain mandatory controls.

The possible residual novelty is specifically the composition

> patient-level simultaneous tangent-field residual coverage → an intrinsic,
> boundary-margin degree certificate → selective surface-hemodynamic topology
> reporting with explicit abstention.

An exhaustive title/abstract search found no direct prior claiming this exact
certificate. That absence is not proof of novelty; it justifies a bounded
asset gate and later formal-prior review. The theorem is useful only if the
certificate is non-vacuous. A globally valid but huge residual radius that
certifies almost no region is a failure, not a positive result.

## 4. Frozen eight-axis red team

Axes are 0--5 in the established order: biomedical importance, target
identifiability, residual novelty, usable asset readiness, effective
independent-unit strength, strong-baseline feasibility, interpretable-figure
value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Patient-level conformal degree certificate | 4.5 | 4.0 | 3.0 | 4.0 | 3.5 | 5.0 | 5.0 | 3.5 | **32.5** | conditional lead; P0 only |
| Conformal critical-region localization | 4.5 | 3.5 | 2.0 | 4.0 | 3.5 | 5.0 | 5.0 | 3.5 | **31.0** | reject |
| Conformal separatrix-network certificate | 4.5 | 2.5 | 2.0 | 4.0 | 3.5 | 5.0 | 5.0 | 3.0 | **29.5** | reject |
| Margin-trained topology-preserving surrogate | 4.5 | 3.0 | 1.0 | 4.0 | 3.5 | 5.0 | 5.0 | 3.5 | **29.5** | reject |
| Generic structure-selective abstention | 4.5 | 3.0 | 1.0 | 4.0 | 3.5 | 5.0 | 4.5 | 3.5 | **29.0** | reject |
| Phase-resolved worldline-event certificate | 4.5 | 1.5 | 2.5 | 3.5 | 3.5 | 5.0 | 5.0 | 3.0 | **28.5** | reject |

The leader crosses 32 because its certificate target is identifiable from a
cycle-averaged tangent vector field and does not require expert critical-point
labels or phase-resolved worldlines. The novelty score remains only 3/5 because
the mathematical ingredients are established and their composition may prove
too direct or too conservative. The 76-patient cohort supports a bounded
application study, not broad conditional-coverage or clinical claims.

## 5. Exact asset boundary

[Zenodo record 19455127](https://zenodo.org/records/19455127) revision 4 was
created and last modified on 2026-04-07. It is published, open and CC BY 4.0.
The official API reports:

- 76 selected patient-specific Aneurisk geometries;
- `AneuriskCFDResults_Zenodo.tar.gz`, 1,430,889,142 bytes, MD5
  `8c66e7bb359d04bd1a5d6db6da3f3926`;
- `README.md`, 1,436 bytes, MD5
  `f552f4d1440848f0cdb8700371579115`.

The public record does not enumerate VTP members, vector-array names,
association, units, coordinate frames, patient/case mapping or whether age and
the diameter-scaled inlet condition are recoverable as model inputs. The
companion paper states that fixed points and separatrices are extracted from
the **cycle-averaged WSS vector field** and that inflow depends on inlet
diameter and patient age. These are enough to motivate a semantics P0, but not
enough to select a learning problem.

## 6. Prospectively frozen P0

The only executable opened by this decision is
`configs/aneurisk_conformal_degree_p0.json`. Exactly one `introai9` PBS
CPU-only submission may:

1. download the exact 1.43 GB archive into PBS job-local scratch;
2. verify bytes and MD5;
3. inventory the tar without extracting paths, following links or persisting
   VTP payload;
4. verify safe, unique regular members and exactly 76 recoverable case units;
5. inspect bounded VTP XML headers for PolyData geometry, one consistent
   three-component cycle-averaged WSS vector array and its point/cell
   association;
6. determine whether coordinate units, WSS units, patient age/inflow category
   and geometry-to-field mapping are explicitly available; and
7. publish only a deidentified schema aggregate.

P0 is method-free and does not compute a critical point, conformal quantile,
model prediction or performance metric. Pass opens only a separately
registered CPU-only P1 for intrinsic field reconstruction, boundary/trivialization
and degree-extractor stability. Fail or execution-incomplete closes this exact
version without same-contract repair or rerun.

## 7. Stop rules and later evidence ladder

Even a P0/P1 pass would not establish a paper. Development may begin only
after all of the following are prospectively fixed:

- patient-disjoint train/calibration/validation/outer-test units;
- the tangent transport/correspondence and surface-region construction;
- a field-wide intrinsic residual score and exact split-conformal quantile;
- marginal-coverage, certificate-correctness and efficiency estimands;
- deterministic and randomized negative controls showing that invalid margins
  fail rather than being silently certified;
- geometry-only, Cartesian, tangent-projected, equivariant, Hodge/HSD and
  functional-surrogate conformal baselines at matched compute.

Stop if the archive lacks a consistent vector field or recoverable input
contract, if degree extraction is mesh/tolerance unstable, if the calibrated
radius certifies a negligible region fraction, or if the proposed procedure
does not improve efficiency at matched validity and field error. Do not repair
these outcomes into an architecture claim.

## 8. Authorization

There is one conditional source lead and one registered method-free P0. There
is still no selected primary problem, architecture, model, GPU experiment,
outer test, result row, C21 or manuscript contribution. AURORA uses only
`introai9` PBS. Never connect to, query, transfer to, submit to or monitor
`junjinyong`; never execute a GPU command on the `introai9` login node.
