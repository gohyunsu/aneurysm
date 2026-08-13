# Acquired aneurysm-asset reconciliation beyond the legacy project root

**Date:** 2026-08-14  
**Decision:** usable assets exist; AneuG transient WSS is still not locally confirmed

## Executive correction

The earlier bounded inventory was too narrow. It was correct only for the
legacy project root that it searched; it was not a statement about the whole
research account. A read-only reconciliation of the separate data, legacy
workspace, run, deployment, generic-dataset and Lustre trees found several
materialized aneurysm datasets and historical experiment records.

The correction does **not** imply that every acquired archive is suitable for
the current paper. Acquisition, archive integrity, target availability,
independent-unit validity and confirmatory eligibility are separate questions.
No HDF5 field array was newly read, no archive was extracted, no scheduler job
was submitted and no GPU was used in this reconciliation.

## What is actually materialized

| Asset | Observed local state | What it can support now | What it cannot support now |
|---|---|---|---|
| AneuG-Flow geometry release | ZIP integrity log passes; 44,134 inventoried files in 14,712 geometry directories; 14,710 complete `shape.obj`/checkpoint/flow-split bundles | geometry lineage, near-duplicate grouping, representation pretraining | no locally confirmed transient WSS/pressure/velocity target in the audited geometry tree |
| BenchAnXplore coarse release | verified ZIP; 105 HDF5 + 105 XDMF pairs; 80-frame velocity trajectories | executable transient mesh-surrogate engineering and temporal-representation controls | no direct WSS/pressure field in the audited XDMF schema; all 105 cases already informed historical representation selection |
| AneuX | metadata and model archives materialized and extracted; metadata ZIP integrity passes | real-shape morphology/OOD and mesh-representation stability | no transient CFD or WSS performance claim |
| CMHA | raw archives and extracted 99 aneurysm-patient + 44 control directories; 105 aneurysm labels in the derived group count | image/geometry/clinical linkage audit and secondary morphology analysis | no validated nodewise transient WSS target; historical exact lesion linkage remains incomplete |
| Aneurisk mirror | 24-row case manifest with imaging, geometry and morphology assets | small real-geometry/image qualitative support | not the separate 76-case Aneurisk CFD release and not a transient WSS cohort |
| Aneumo | official code repository plus the separately known compact pilot cache | historical parser development only | mapping and licence conflicts still prevent confirmatory family inference |
| IntrA | repository, split lists and tools | code/schema reference | no materialized mesh payload was found in the audited tree |

The two incomplete AneuG geometry directories are `stable_5954` and
`stable_16384`; both lack `shape.obj` while retaining the checkpoint and
flow-split files. Therefore neither 14,712 directories nor 14,710 complete
bundles may be relabelled as 14,712 independent cases or patients. The official
14,000 steady/730 transient report and the local geometry inventory are
different accounting statements until the release manifest is reconciled.

## Existing BenchAnXplore evidence

BenchAnXplore is more than a downloaded archive: a historical five-fold,
geometry-held-out representation audit already evaluated all 105 cases. A
fixed Fourier rank-8 cycle representation failed the frozen localized-bulge
gate. Train-only POD passed the same representation thresholds at ranks 17 and
25; rank 17 achieved mean full-cycle relative L2 about 0.14% and mean bulge
relative L2 about 0.88%. These are **representation reconstruction** results,
not learned surrogate accuracy and not a new confirmatory test.

This evidence has one useful consequence: a train-only POD cycle head is a
better justified engineering default than a fixed Fourier decoder. It does not
make POD novel and it does not authorize reusing all 105 cases as untouched
confirmation after architecture selection.

## Why the paper does not pivot to BenchAnXplore alone

BenchAnXplore is the most executable local transient asset, but it is a weak
standalone answer to the current biomedical question:

1. it contains semi-idealized volumetric velocity trajectories rather than a
   released surface vector-WSS target;
2. its 105 cases share an idealized parent construction and cannot be treated
   as 105 independent patients;
3. the current XDMF contract exposes coordinates, tetrahedra, velocity and a
   wall mask, not a direct solver-reported WSS reference;
4. all cases already contributed to temporal-representation discovery; and
5. it offers no multi-solver same-anatomy variability floor.

It therefore becomes an **engineering benchmark and temporal-head control**,
not the headline confirmatory dataset. Deriving WSS from near-wall velocity
would require a separately validated gradient, viscosity, wall-normal and mesh-
resolution contract; a derived proxy cannot silently replace solver WSS.

## Selected implementation scaffold after source admission

The most defensible performance-oriented scaffold is:

- surface input: mesh geometry, local normals/curvatures and inflow/boundary
  waveform tokens;
- spatial operator: an SE(3)-equivariant multi-resolution MeshGraphNet;
- temporal output: a train-only POD full-cycle head, with rank chosen on
  validation only;
- physical output: three-component WSS followed by deterministic tangent-plane
  projection;
- strong controls: official Graph U-Net, Cartesian MeshGraphNet, the same
  backbone without equivariance, and matched Hodge/edge-form variants;
- optional correction: a signed-critical-point/worldline term only if a
  field-error-matched baseline demonstrably creates excess structural error.

This scaffold is selected for implementation efficiency and performance, not
claimed as algorithmic novelty. Equivariance, MeshGraphNet, POD, tangent
projection, Hodge representations and topology losses are prior art or
controls. The possible contribution remains the AneuG-specific,
reference-relative structural validation and a minimal failure-linked
correction that survives lineage-disjoint confirmation.

## Streamlined execution order

1. Execute the already registered source-only G0 once on CPU/PBS.
2. Reconcile official AneuG release accounting with the 14,710 complete local
   geometry bundles and freeze conservative near-duplicate groups before WSS.
3. Acquire or resolve the exact transient target payload prospectively; do not
   substitute the geometry-only archive.
4. Run a method-free critical-structure stability audit, then field-error- and
   compute-matched strong baselines.
5. Use the selected scaffold as the performance baseline. Add one structural
   correction only if the failure is observed, and select it on validation.
6. Confirm on untouched lineage groups; use the 2015 Challenge only as a
   within-anatomy solver-variability interpretation floor and AneuX only for
   geometry OOD.

This order removes the false “no data” bottleneck without manufacturing a WSS
target or a fresh test set that the acquired files do not contain.

## Scope limits

The reconciliation deliberately did not decompress the approximately 41 GB
home-recovery archive on a login node and did not recursively crawl multi-
terabyte shared storage. Those operations are disproportionate to the current
question and could duplicate recovered assets. Generic breast and liver
datasets found in the other dataset/project trees are unrelated to AURORA.
Intermittent SSH resets during broad directory traversal are recorded as
transport observations, not as evidence that a dataset is absent or damaged.
