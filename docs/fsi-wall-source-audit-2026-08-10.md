# FSI–wall source audit

**Frozen decision · 2026-08-10 KST:** all six candidates remain below the
unchanged **32/40** source-admission line. The strongest candidate scores
**31.0/40**. No AnXplore VTK mesh, rigid/FSI field, wall-motion image,
micro-CT volume, finite-element result or new BenchAnXplore member was
downloaded or opened; no P0, method, architecture, PBS job, GPU job or outer
test was registered.

This audit tests a physically important alternative to the exhausted rigid-wall
CFD and rupture-status branches: can wall compliance, wall motion or structural
risk provide a defensible ISBI 2027 identity? It separates a valid mechanistic
motivation from the stronger requirement that the target and paired evidence be
available at patient/geometry level.

## 1. Frozen candidate screen

Each axis is scored from 0 to 5 in the fixed order: scientific importance,
target identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Rigid-to-compliant hemodynamic discrepancy operator | 5.0 | 4.5 | 2.0 | 1.5 | 4.0 | 5.0 | 5.0 | 3.5 | **30.5** | reject |
| Dynamic-geometry inverse wall-property inference | 5.0 | 4.0 | 2.5 | 3.5 | 0.5 | 5.0 | 5.0 | 4.0 | **29.5** | reject |
| Compliance-conditioned flow-diverter response | 5.0 | 4.0 | 1.5 | 1.5 | 0.5 | 5.0 | 5.0 | 4.0 | **26.5** | reject |
| Lumen-to-wall-thickness hotspot prediction | 5.0 | 2.0 | 2.0 | 1.0 | 0.5 | 5.0 | 5.0 | 4.0 | **24.5** | reject |
| Selective rigid-CFD-to-FSI referral | 4.5 | 4.5 | 1.0 | 1.5 | 4.0 | 5.0 | 5.0 | 3.5 | **29.0** | reject |
| Multi-granularity conformal hemodynamic surrogate | 4.5 | 3.5 | 0.5 | 5.0 | 2.5 | 5.0 | 5.0 | 5.0 | **31.0** | reject |

The six scores were frozen together. The 31.0 row is not renamed or reweighted
after seeing that it misses the line by one point.

## 2. AnXplore identifies the scientific discrepancy, not a learnable release

The [AnXplore study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11243300/)
simulates 101 semi-idealized sidewall aneurysms under both rigid-wall and
fluid–structure-interaction (FSI) assumptions. It reports large case-dependent
changes, including sac-averaged OSI changes from -36% to +674% relative to the
rigid-wall calculation. That is strong evidence that compliance can matter and
that a rigid surrogate should not silently be called patient-specific truth.

The public [AnXplore repository](https://github.com/aurelegoetz/AnXplore),
however, describes itself as a tetrahedral mesh dataset. Its `full_dataset`
directory exposes 101 `Fluid_*.vtk` meshes; the highlighted cases expose fluid
and solid meshes. It does **not** expose the 101 paired rigid/FSI time-resolved
solution fields, displacements, wall stresses or per-case functional table used
in the paper. Mesh count is therefore not paired response count. Without that
target payload, a rigid-to-compliant residual operator, an FSI referral policy
or a coupled neural operator cannot be trained or independently evaluated.

All 101 cases also share an idealized toroidal parent artery, one prescribed
inflow waveform and fixed constitutive assumptions. Their patient-derived
bulges are legitimate geometry units, but they are not 101 observations of
patient-specific wall stiffness or boundary physiology.

## 3. Treatment response and inverse wall mechanics do not repair the unit

The AnXplore paper showcases one flow-diverter configuration under rigid and
compliant walls. It is valuable mechanistic evidence, but one device case is
not a treatment-response cohort. Device-conditioned prediction, counterfactual
selection or clinical outcome language would all exceed the released unit.

The open [inverse-mechanics record](https://doi.org/10.5061/dryad.tqjq2bw5q)
contains dynamic imaging and finite-element material identification for an
animal intracranial-aneurysm model. It supports reproducibility of one inverse
analysis pipeline, not patient-level generalization or a human imaging model.
Likewise, the published [3D micro-CT wall-thickness study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11341610/)
contains five resected aneurysms and shows 10--40-fold within-case spatial
variation. Lumen geometry alone does not identify local living-wall thickness,
and five specimens cannot support a headline learned predictor.

## 4. Reliability wrappers are already a dense direct-prior line

The existing [In-PI-MGN/BenchAnXplore paper](https://www.nature.com/articles/s41746-026-02404-z)
already reports bulge/neck/parent-region errors, WSS, TAWSS and mass-flow
checks. It also shows that the four patient-specific zero-shot cases are much
harder than the semi-idealized benchmark. Replacing global RMSE with a wall
functional is therefore an evaluation control, not a new problem.

The recent direct-prior line is even closer:

- [Multi-granularity conformal neural-operator surrogates](https://arxiv.org/abs/2607.17297)
  already calibrate case-level quantities and spatial pressure/WSS fields and
  use uncertainty to prioritize geometries and regions for CFD verification.
- [Conformal prediction for neural operators](https://arxiv.org/abs/2606.09923)
  already gives distribution-free adaptive field intervals.
- [Conformal operator learning for Navier–Stokes](https://arxiv.org/abs/2606.08654)
  already targets simultaneous field coverage in a data-scarce flow regime.
- [FNO-based FSI](https://arxiv.org/abs/2401.02311) already learns coupled
  fluid–structure dynamics in a generic mechanics setting.

Consequently, a conformal wrapper, ensemble, uncertainty heatmap, selective
CFD referral head or generic multiphysics operator is a required control. The
remaining aneurysm-specific gap would require released paired rigid/FSI fields,
disjoint patient-like geometries or measured wall motion, and positive
functional/referral evidence beyond those controls. That joint asset is not
present.

## 5. Decision boundary

- AnXplore meshes may be used in a future mesh/provenance audit, but the paper's
  paired simulation results are not inferred from those meshes.
- No FSI target is fabricated by rerunning a different solver and calling it
  the released ground truth. New simulation generation would define a new
  source and require a separate solver-validation and compute contract.
- The animal inverse-mechanics case, one flow-diverter case and five micro-CT
  specimens are not promoted to population-level evidence.
- Generic FSI neural operators, multi-fidelity correction, conformal field
  bands and selective simulation referral remain direct priors or controls.
- Since the maximum is 31.0/40, executable P0, method, architecture, PBS/GPU
  and outer test remain unauthorized. Current AURORA GPU jobs remain zero.
- Future AURORA execution is restricted to `introai9` PBS. `junjinyong` remains
  excluded from connection, query, submission and monitoring.

The next allowed action remains a materially new or revised primary-source
audit. Only a fresh candidate scoring at least 32 may open a separately
preregistered, method-free CPU/PBS P0.
