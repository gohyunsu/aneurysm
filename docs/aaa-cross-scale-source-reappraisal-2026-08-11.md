# AAA cross-scale source reappraisal

**Frozen on:** 2026-08-11  
**State:** all six formulations rejected · no active problem, P0/P1, method,
architecture, scientific-server query or GPU job  
**Purpose:** determine whether two newly visible abdominal-aortic-aneurysm
(AAA) sources create an identifiable ISBI problem, rather than joining
unmatched cohorts or placing a new neural operator on an already occupied CFD
surrogate task.

## Decision

Neither source activates an AURORA paper identity.

The transcriptomic reproducibility package is scientifically useful, and one
of its upstream cohorts really does contain paired high- and low-wall-stress
biopsies. It is not, however, a patient-linked imaging--mechanics--molecular
dataset. The six upstream studies measure rupture, diameter, thrombus coverage,
regional wall stress and cell state in different cohorts. Their sample rows
cannot be joined into a common patient or surface coordinate system.

The synthetic AAA CFD framework is a materially stronger executable asset. It
releases a parametric geometry generator, OpenFOAM case construction and
post-processing code derived from measurements in 258 CTA cases. Its paper
reports 182 selected virtual geometries and 364 simulations. But the public
release does not contain the 258 CTA images, a patient-specific real-CFD outer
test or the complete generated CFD field cohort. More importantly, synthetic
AAA geometry--hemodynamics analysis and AAA WSS surrogation are already direct
priors. Training a GNN or operator on this generator would be executable
engineering, not residual novelty.

The prospectively frozen six-candidate screen peaks at **30.0/40**. The leading
candidate fails the residual-novelty floor at **0.5/5**; every other candidate
fails at least one non-compensatory floor. No source payload was downloaded,
no score was repaired, and no P0 or compute was opened.

## 1. What the transcriptomic package actually supplies

The official [Zenodo record](https://zenodo.org/records/21868617) is revision 4,
open under CC BY 4.0. It contains one 293,641-byte archive,
`AAA_transcriptomic_architecture_reproducibility_v1.1.zip`, with MD5
`264d9ada285aa65a09239266147a1ad5`. The record says the package contains R
analysis code, frozen programme definitions, sample manifests, selected
endpoint-level derived inputs and final integration inputs. Primary GEO
expression data, large derived matrices and third-party MSigDB files are not
redistributed. The archive itself was not downloaded or opened.

The word *integration* describes an evidence synthesis, not a multimodal
patient table. The upstream studies have different observational units.

- [GSE98278](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE98278) has
  48 wall samples: 31 elective stable and 17 ruptured AAAs; it also contrasts
  15 intermediate-size and 16 large AAAs.
- [GSE57691](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE57691) has
  20 small AAA, 29 large AAA, nine aortic-occlusive-disease and ten donor
  specimens.
- [GSE232911](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE232911)
  contains 246 media/adventitia samples from thrombus-covered and thrombus-free
  wall regions of 76 AAA patients plus 13 donor controls. Tissue regions are
  repeated measurements; 246 is not the patient count.
- [GSE205071](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE205071) is
  the important exception to the claim that wall stress is wholly unlinked:
  it contains biopsies from **12 patients**, sampled from high- and low-wall-
  stress regions selected by prior finite-element analysis. It does not expose
  a public CTA volume, surface mesh, finite-element field or biopsy-to-surface
  coordinate contract suitable for an imaging model.
- [GSE226492](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE226492)
  includes three AAA patients among ten aortic-wall specimens; its record says
  raw data are unavailable for privacy reasons.
- [GSE237230](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE237230) has
  four AAA patients sequenced in technical duplicate. Eight sequencing samples
  remain four independent patients.

Consequently, rupture labels from one cohort, local wall stress from another,
thrombus regions from a third and cell states from a fourth cannot supervise a
single patient-level cross-modal model. Dataset-level programme concordance can
be reproduced, but it cannot identify an individual imaging-to-biology target.

## 2. What the synthetic CFD framework actually supplies

The official [Zenodo software record](https://zenodo.org/records/21435232) is
revision 4 and MIT licensed. It contains one 37,064,038-byte archive with MD5
`93cec210d801786fe3728dbffe990067`. The linked
[GitHub repository](https://github.com/Harish-Research-Lab/Synthetic-AAA-CFD-framework)
was read at release `v1.0.0`, exact commit
`98363a0104701dcc4bea11c2ee808eed1febafbe`.

The public README specifies the following chain.

1. Fit marginal distributions and diameter-pair convex hulls to
   `aaa_data.xlsx`, which contains measurements derived from 258 CTA cases.
2. Generate parametric AAA surfaces and spherical morphs.
3. Keep cases inside all patient-data diameter-pair hulls.
4. Build OpenFOAM cases, run pulsatile CFD and extract WSS, TAWSS and OSI.

The associated study reports 400 generated candidates, 182 selected virtual
geometries and 364 simulations. Those figures are useful, but their unit is a
generated geometry under a shared statistical and solver pipeline. They are
not 182 newly observed patients. The README also states that generated
geometries and CFD results are not committed; only four example cases are
included. The code and README were inspected, but the release ZIP,
`aaa_data.xlsx`, example cases and CFD payload were not downloaded or run.

## 3. Direct-prior boundary

The attractive model identities are already occupied.

- [Rygiel et al.](https://arxiv.org/abs/2507.22817) train an E(3)-equivariant
  transient vector-WSS surrogate on CT-derived geometries from 100 AAA patients
  and evaluate boundary-condition, remodelling, topology and mesh-resolution
  generalization, including an external cohort.
- [WSSNet for AAA](https://doi.org/10.1063/5.0322588) directly studies
  patient-specific CTA/CFD alignment, spatial-resolution and neighbourhood
  design, temporal splitting and acquisition-noise robustness for AAA WSS
  prediction.
- The synthetic-framework paper itself studies geometry--hemodynamics
  relations, demographic virtual populations, joint plausibility filtering
  and risk descriptors.
- Regional wall-stress transcriptomics is the target of GSE205071 and of the
  new reproducibility package. Mechanosensitive-gene clustering and AAA subtype
  prediction have also already been reported on overlapping GEO cohorts.

Therefore an SE(3) mesh network, graph neural operator, Hodge layer, uncertainty
head, transcriptomic conditioning branch or synthetic-to-real loss is a
component or control. A model name or component stack cannot satisfy residual
novelty.

## 4. Frozen six-candidate screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Each axis is scored from 0 to 5.
Admission requires total at least 32 and simultaneous minima of 3.5 for
identifiability, 2.5 for residual novelty and 3.0 for asset, independent unit
and baseline feasibility.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Synthetic-AAA transient WSS neural operator | 4.0 / 4.5 / **0.5** / 3.5 / 3.5 / 5.0 / 5.0 / 4.0 | **30.0** | Reject: directly occupied by AAA WSS surrogates; public cohort is generated and lacks a real paired outer field reference |
| Selection-aware virtual-population validity and uncertainty | 4.0 / **3.0** / **1.0** / 4.0 / 3.5 / 4.5 / 4.5 / 4.0 | **28.5** | Reject: convex-hull selection is already part of the source paper and no observed-image target identifies distributional validity |
| Synthetic-to-real AAA hemodynamic transport with abstention | 4.5 / **2.0** / **2.0** / **2.5** / 3.0 / 4.5 / 5.0 / 3.0 | **26.5** | Reject: no released real geometry with matched reference field and synthetic provenance for calibration |
| Paired regional wall-stress transcriptomic-program prediction | 4.5 / 4.0 / **0.5** / 3.5 / **1.5** / 5.0 / 3.5 / 4.0 | **26.5** | Reject: direct source question on only 12 patients and no image/mesh/region-coordinate target |
| Mechanobiology-conditioned surface operator | 4.5 / **1.5** / **1.5** / **2.0** / **1.5** / 4.5 / 5.0 / 2.5 | **23.0** | Reject: imaging, CFD and programme labels are not jointly observed in the same patients |
| Local WSS-to-cell-state spatial alignment | 4.5 / **1.0** / **1.5** / **2.0** / **1.5** / 4.0 / 5.0 / 2.5 | **22.0** | Reject: single-cell cohorts have no biopsy-to-surface registration or matched local WSS field |

The leading 30.0 candidate is not repaired to 32 by assigning extra value to a
fancier architecture. The novelty floor is a veto. No phase, vertex,
transcript, technical replicate or synthetic morph is counted as an additional
patient.

## 5. What would make a cross-scale direction identifiable

A genuinely new patient-linked mechanics--molecular imaging paper would need a
prospective or versioned cohort in which the same patient has:

1. CTA or time-resolved vascular imaging and an explicit lesion/surface mask;
2. a registered surface mesh and patient-specific FEA/CFD field with units,
   boundary conditions and solver provenance;
3. biopsy locations mapped into that surface coordinate system;
4. regional molecular measurements with patient and specimen identifiers;
5. patient-grouped development/confirmation splits and enough independent
   patients to estimate uncertainty.

That would first open a **method-free linkage and task-stability P0**, not a
GNN. A future synthetic-to-real surrogate version would likewise need a sealed
real-patient outer cohort with matched reference fields. Without one of these
material releases, architecture work cannot answer the missing-observation
problem.

## 6. Relation to surface-vector and execution

This audit neither revives nor discards surface-vector. Its endpoint hierarchy
and evidence ladder remain unchanged: stable boundary-margin degree before
exact points/worldlines, and no structural training loss before a matched
field-accuracy failure is observed. Historical jobs `115645.ECE-util1` and
`115684.ECE-util1` remain closed execution-incomplete/no-verdict records and
are not repaired or rerun.

No scientific server was queried. No PBS job was submitted. Active lead,
primary problem, P0/P1, method, architecture, GPU, outer test, result row and
paper claim remain zero. Future eligible execution is restricted to
`introai9` PBS; login-node GPU commands are prohibited. `junjinyong` must never
be accessed, queried, transferred to, submitted to or monitored.

The two records are not added to the recurring source watch. They are already
public and their fundamental block is not a missing version number: it is the
absence of a patient-linked imaging/field/molecular contract or a real paired
outer field reference. Only a release that changes one of those task-defining
facts warrants a fresh audit.
