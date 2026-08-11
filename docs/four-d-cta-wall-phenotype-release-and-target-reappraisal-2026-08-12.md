# 4D-CTA wall-phenotype release and target reappraisal

**Audit date:** 2026-08-12  
**Protocol state:** schema 10.6 prospective source screen  
**Decision:** all six formulations rejected; no active paper identity, payload
download, P0, method, architecture, server query or compute

## Executive verdict

The public DA_4DCTA release is a materially stronger lead than a paper-only
cohort: it exposes derived point-trajectory CSVs, analysis code and an exact
Zenodo archive. It does **not** make a new AURORA wall-phenotype paper
identifiable. The source paper already predicts intraoperatively observed thin
wall and hyperplastic wall regions from 4D-CTA trajectories. The release omits
the source 4D-CTA DICOM, operative RGB image or video, image-to-wall
registration reference, mesh or surface adjacency, a complete patient/centre
and fold manifest, and an independent dense whole-wall reference.

The most plausible residual question—whether selection-aware inference can
separate model error from the fact that only visually evident wall regions were
annotated—scores **29.0/40**. It fails target-identifiability and independent-
unit floors. A graph network, spatiotemporal transformer, conformal wrapper or
new model name cannot repair those missing observables. The release is therefore
retained as a material-source and baseline watch, not an active paper identity.

## 1. What the primary source establishes

The PeerJ study reports 52 unruptured cerebral aneurysms collected at four
hospitals. It constructs 100 Hz, one-second point trajectories from 4D-CTA and
uses intraoperative wall appearance to identify thin-wall and hyperplastic-wall
regions. The source reports approximately 92% average accuracy under its stated
leave-one-patient-out-style evaluation. These are source claims, not AURORA
results, and AURORA has not reproduced them.

This direct prior already occupies the broad task “4D-CTA motion trajectory to
intraoperative wall phenotype.” Replacing its LSTM/attention pipeline with a
GNN, surface operator or transformer would be an architecture substitution, not
an independent contribution.

## 2. Exact public release contract

The Zenodo record is revision 4, modified
`2024-09-23T04:40:53.613542+00:00`, open under CC BY 4.0. It contains one file:

- `Kumrai-T/DA_4DCTA-v1.0.1.zip`
- 1,934,055,674 bytes
- `md5:fd9f856b485983cd430ab94d01a24596`

The archive body was not downloaded. Its exact metadata state is now monitored
read-only.

The public GitHub repository has exact `main` head
`8df7d45e9f65e3cbfd4ae3fc430c65a98905bdfc`. Its root exposes analysis code,
notebooks and a `raw_data` directory. The root has no README or recognized
repository license; the Zenodo record, rather than the GitHub metadata, declares
CC BY 4.0. This provenance asymmetry is a reproducibility constraint, not a
novelty claim.

Only the top-level manifest and selected notebook text were inspected. There
are 52 visible case directories, including suffix forms such as `A06-1`,
`A06-2`, `K09-1`, `K09-2`, `K13` and `K13-2`. The suffix semantics are not
machine-auditable, so 52 directories are not asserted to be 52 statistically
independent patients. A recursive Git-tree response was truncated; its visible
blob count and byte sum are therefore not a complete-corpus manifest.

The notebook material describes five trajectory colors and samples 2,000
trajectories per color per case. A visible training list is not a complete exact
52-fold driver and refers to identifiers that do not match the current root
one-for-one. This is bounded release drift, not proof that the paper is invalid.

## 3. Why the target is not independently identifiable

The release exposes derived trajectory features and color-group CSVs. It does
not expose the measurements needed to distinguish four separate error sources:

1. cardiac reconstruction and point-tracking error in source 4D-CTA;
2. selection of visually obvious wall regions during surgery;
3. image-to-operative-view registration error;
4. phenotype prediction error conditional on the released trajectory.

Without source images, operative reference and registration, these mechanisms
are observationally conflated. Without surface adjacency, a “surface GNN” would
have to invent a graph from derived points and could not be evaluated against a
frozen anatomical topology. Without dense or repeated independent labels,
pointwise calibration or conformal coverage does not certify the unobserved
wall.

## 4. Recent direct priors narrow the residual gap

A 2026 prospective 4D-CTA study follows 10 patients with 11 unruptured
aneurysms for 4.3±1.1 years, uses 20 cardiac phases and explicitly analyzes
first-harmonic wall pulsation with measurement/noise thresholds. Its data are
available on demand, not as a versioned public asset.

A 2025 repeatability study analyzes 15 subjects and 17 aneurysms over three
consecutive cardiac cycles; the source reports consistent volume-change
patterns in only two aneurysms. It directly establishes that dynamic
repeatability must precede biological interpretation, while providing no public
release identified in this audit.

A 2025 wall-phenotype study links intraoperative video, morphology and
hemodynamics in 133 patients with 148 aneurysms. It is request-only and directly
occupies broad wall-phenotype characterization. Generic centre-domain
generalization, spatiotemporal graph learning, weak supervision and clustered
conformal prediction are methodological controls, not residual novelty.

## 5. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at least
32 and every critical floor.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Verification-aware wall-phenotype partial identification | 5/2/2.5/3.5/2.5/4.5/5/4 | **29.0** | Reject: selection, registration and prediction errors are not separately observed |
| Centre-held-out spatiotemporal surface mapping | 5/3.5/1.5/3/2.5/4.5/5/3.5 | **28.5** | Reject: centre/patient grouping and surface adjacency are unresolved; core task is direct prior |
| Patient-clustered conformal phenotype mapping | 4.5/3/1/3/2.5/5/5/4 | **28.0** | Reject: generic calibration and no dense independent whole-wall truth |
| Temporal-resolution-stable phenotype inference | 4.5/2.5/2/2.5/2.5/4.5/5/4 | **27.5** | Reject: repeated-cycle/raw-image measurements are absent and repeatability is direct prior |
| Joint motion–hemodynamics wall map | 5/3/1.5/1.5/2.5/5/5/3 | **26.5** | Reject: no joined public trajectory–CFD–operative-reference contract |
| Motion-to-future-growth bridge | 5/1.5/2.5/1/1/5/5/3.5 | **24.5** | Reject: no linked longitudinal growth event in the release |

All six fail at least one critical floor. None opens payload access, P0, P1,
method selection, architecture selection, server access, GPU training or an
outer test.

## 6. Material re-entry conditions

A fresh evidence version could register a method-free P0 only if an official
source establishes all of the following:

1. source 4D-CTA with phase timing and repeated-cycle or acquisition-quality
   metadata;
2. operative RGB image/video and a frozen image-to-wall registration reference;
3. surface geometry and adjacency tied to every released trajectory;
4. machine-auditable patient, aneurysm, centre and fold grouping;
5. explicit rules for unlabeled wall, ambiguous colors and visually selected
   regions;
6. a dense, repeated or independently adjudicated reference, or a clearly
   identified partial-label estimand;
7. enough independent confirmation patients and a centre-held-out manifest;
8. source model, trajectory-only, geometry-only and recent phenotype controls.

Passing P0 would open only a separate method-free task-adequacy gate. It would
not select a GNN, Hodge operator, loss, architecture or GPU job.

## 7. Consequence for surface-vector and ISBI 2027

This source does not provide transient WSS or a field-error-matched failure of
signed critical points and worldlines. It neither activates nor invalidates the
surface-vector hypothesis. Edge 1-forms, Hodge decomposition, equivariance,
periodic operators and structural losses remain unselected controls.

No scientific server was queried, no payload was transferred and no PBS/GPU
job was created. Future gate-authorized execution remains `introai9` PBS only;
login-node GPU commands are forbidden and `junjinyong` remains excluded.

## Source ledger

- Original wall-phenotype paper: [PeerJ / PubMed](https://pubmed.ncbi.nlm.nih.gov/40356666/)
- Public record: [Zenodo 13788524](https://zenodo.org/records/13788524)
- Public repository: [Kumrai-T/DA_4DCTA](https://github.com/Kumrai-T/DA_4DCTA)
- 2026 prospective dynamic study: [PubMed 42188680](https://pubmed.ncbi.nlm.nih.gov/42188680/)
- 2025 repeated-cycle study: [PubMed 40811924](https://pubmed.ncbi.nlm.nih.gov/40811924/)
- 2025 intraoperative phenotype study: [PubMed 41323131](https://pubmed.ncbi.nlm.nih.gov/41323131/)
