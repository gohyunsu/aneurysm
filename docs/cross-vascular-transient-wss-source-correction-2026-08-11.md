# Cross-vascular transient-WSS source correction · 2026-08-11

> **Frozen decision · schema 8.6 prospective:** a newly inspected patient-specific
> AAA transient-WSS study makes the proposed architecture substantially less
> novel, while two public geometry/WSS sources still do not identify an
> executable structure-fidelity task. Six formulations score
> **30.0/29.0/28.5/25.5/23.0/21.5**, all below the unchanged 32-point admission
> line. No lead, P0/P1, method, architecture, server query, PBS/GPU work, outer
> test, result row or paper claim is opened.

## 1. Material direct-prior correction

[Rygiel et al.](https://arxiv.org/abs/2507.22817) do not merely provide a
generic equivariant mesh baseline. They train on CTA-derived lumen surfaces
from 100 AAA patients, use ten-fold cross-validation, and evaluate an ensemble
on a geographically external longitudinal cohort of 29 patients and 118 scans.
Their SimVascular pipeline extracts 21 WSS fields per cardiac cycle and reports
1,090 transient CFD simulations across the two sources and boundary-condition
variants.

The model is LaB-GATr: an E(3)-equivariant geometric-algebra Transformer on
surface point clouds. It uses normals, principal curvature, inlet/outlet
geodesics and a parallel-transported flow prior, conditions on inflow, and
directly predicts transient vector WSS. The paper evaluates transient WSS,
TAWSS and OSI as well as boundary-condition shift, longitudinal remodelling,
unseen branch topology and mesh resolution. It also explicitly reports that
high-frequency directional patterns are over-smoothed.

This evidence strengthens only one part of the proposed application identity:
field-accurate surrogates can exhibit a plausible smoothing mechanism. It does
**not** show signed-degree, critical-point, separatrix or worldline failure,
because none of those endpoints is extracted or evaluated. We therefore keep
structure fidelity as an inactive, falsifiable question while treating
equivariance, geometric descriptors, transient decoding, topology
generalisation, remeshing and TAWSS/OSI evaluation as direct-prior controls.

## 2. The stated public code is not an executable baseline

The paper states that code is public at
[`PatRyg99/AAA-WSS-neural-surrogate`](https://github.com/PatRyg99/AAA-WSS-neural-surrogate).
The exact public state inspected on 2026-08-11 is head
`2f78bf1879e5e555c3369d91822be3f567f9fbd1`: one commit, one 183-byte
`README.md`, zero releases, repository size 0 KiB and no GitHub-recognized
license. There is no implementation, checkpoint, environment, CFD field,
train/validation/test manifest or executable command.

The separate [AAA-100 Zenodo record](https://zenodo.org/records/10932957),
revision 10, is open under CC BY-NC 4.0 and contains 100 watertight patient
geometries and centerlines. Its three public files are `meshes.zip`
(780,174,221 bytes), `centerlines.zip` (824,809 bytes), and
`description.pdf` (8,490,227 bytes). It does **not** publish the transient CFD
fields used in the WSS paper. No file was downloaded or range-read in this
audit.

Thus the paper is a strong scientific direct prior but not currently a
reproducible matched baseline or a new phase-resolved WSS asset. A future
repository change may request a baseline-feasibility re-audit only; it cannot
select that architecture or authorize data access and compute.

## 3. The new open iliac-vein source is diagnostic, not confirmatory

The [SANO Dataverse release](https://doi.org/10.71580/SANO/GVPFQ5), version
1.0, exposes 141 public files under CC0. The associated
[preprint](https://doi.org/10.64898/2026.02.17.706277) uses MRI/CT-derived
common-iliac-vein geometries from twelve patients, compares 2D projections,
3D extrusions and full 3D reconstructions, and runs steady-state CFD under a
standardised inflow. It already relates statistical shape modes to low-WSS
area at 0.05, 0.10 and 0.15 Pa and reports that simplified geometries enlarge
low-WSS burden by roughly 118--136% for two of those thresholds.

This is useful evidence that geometry representation can change a downstream
WSS functional. It is not an aneurysm source, is not transient, has twelve
independent patients, and does not supply a fresh clinical outcome. Shape-mode
members, reconstructed surfaces and WSS thresholds are repeated measurements,
not additional patients. The original study already owns the geometry-
fidelity-to-low-WSS analysis. The 1.5-GB payload was not opened; public
metadata and the paper were sufficient for this decision.

## 4. Frozen six-way screen

Each axis is scored 0--5 in the unchanged order: biomedical-imaging
importance, target identifiability, residual novelty, usable asset readiness,
effective independent unit, strong-baseline feasibility, interpretable-figure
value and ISBI-schedule fit.

| Candidate | Importance | Identifiability | Residual gap | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| SANO anatomical-fidelity low-WSS reproduction | 4.0 | 5.0 | 0.5 | 5.0 | 1.0 | 5.0 | 5.0 | 4.5 | **30.0** | reject |
| SANO steady-WSS structural-stability audit | 4.0 | 3.5 | 2.5 | 5.0 | 1.0 | 5.0 | 5.0 | 3.0 | **29.0** | reject |
| New CFD generation on open AAA-100 geometry | 4.5 | 2.5 | 2.0 | 4.5 | 5.0 | 4.0 | 5.0 | 1.0 | **28.5** | reject |
| AAA transient-WSS structure-failure audit | 4.5 | 3.0 | 3.0 | 1.5 | 5.0 | 1.0 | 5.0 | 2.5 | **25.5** | reject |
| AAA longitudinal structure consistency | 4.5 | 3.5 | 2.5 | 1.0 | 3.5 | 1.0 | 5.0 | 2.0 | **23.0** | reject |
| Cross-vascular structure transfer | 4.5 | 2.5 | 2.0 | 1.0 | 4.0 | 1.0 | 5.0 | 1.5 | **21.5** | reject |

The best row is largely a reproduction of the source paper and therefore has
little residual novelty. The rows with a cleaner residual question lack the
actual transient WSS fields and executable direct baseline. Generating new CFD
labels on geometry-only AAA-100 would create model-derived evidence under a new
pipeline, not independently confirm the published labels, and cannot support
an ISBI claim on the current schedule.

## 5. Consequence for the supplied surface-vector analysis

The supplied analysis is accepted only with the following hierarchy.

1. **Retain the question, not the paper identity.** Field error may fail to
   preserve critical-flow organization, but this failure remains unobserved.
2. **Degree before exact tracks.** Boundary-margin signed total degree and
   abstention precede exact point, type, birth/death and worldline metrics.
3. **Evaluation before structural loss.** A field-error- and compute-matched
   baseline failure must be observed before any 1-form/Hodge/degree loss is
   considered.
4. **Minimal intervention after the failure.** E(3) equivariance, point/mesh
   attention, flow priors, transient decoding and remeshing robustness are
   controls, not novelty.
5. **Fresh patient/family confirmation.** A future positive result must jointly
   satisfy field non-inferiority, stable structural superiority, patient/family
   bootstrap uncertainty and matched-case interpretation.

The only valid re-entry signal is a versioned source that exposes
phase-resolved tangent-WSS semantics, patient/base-family mapping, reproducible
mesh and boundary-condition provenance, a usable development/confirmation
split, and an executable strong baseline or enough information to reproduce
one. A new model name, loss, downloader fix or the empty repository becoming
slightly larger is not E0.

## 6. Operational decision

No scientific server was queried. No payload, split, P0/P1, method,
architecture, PBS/GPU job, outer test, result row or manuscript claim was
created. Closed jobs `115645.ECE-util1` and `115684.ECE-util1` remain
execution-incomplete/no-verdict history and are not repaired or rerun.

Any future gate-authorized execution uses PBS on `introai9`; login-node GPU
commands remain prohibited. `junjinyong` remains excluded from connection,
query, transfer, submission and monitoring.
