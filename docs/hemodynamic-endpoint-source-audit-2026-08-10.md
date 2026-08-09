# Hemodynamic–endpoint source audit

**Frozen decision · 2026-08-10 KST:** all five candidates remain below the
unchanged **32/40** admission line. The strongest candidate scores **31.0/40**
and is rejected without payload access, P0, method selection, architecture
selection, PBS submission or GPU use. AURORA therefore still has no active
primary problem, model, outer test or submission identity.

This audit was triggered by a new public release of CFD-derived surface fields
for 76 Aneurisk aneurysms and by 2025–2026 papers on multiple-aneurysm culprit
identification, post-treatment remnants and wall enhancement. It asks whether
these sources create a materially new, identifiable ISBI problem. It does not
repair any closed AURORA candidate or reinterpret cross-sectional rupture status
as prospective risk.

## 1. Frozen candidate screen

Each axis is scored from 0 to 5 in the fixed order: scientific importance,
target identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Curvature-only surrogate of local hemodynamic fields | 4.0 | 4.0 | 0.5 | 4.5 | 4.0 | 5.0 | 5.0 | 4.0 | **31.0** | reject |
| Cross-source curvature-residualized hemodynamic added value | 4.5 | 2.5 | 2.0 | 4.0 | 3.5 | 5.0 | 5.0 | 3.5 | **30.0** | reject |
| Within-patient multiple-aneurysm culprit ranking | 5.0 | 4.5 | 0.5 | 0.5 | 1.0 | 5.0 | 4.5 | 2.0 | **23.0** | reject |
| Paired pre/post-treatment remnant-change prediction | 5.0 | 3.5 | 1.5 | 1.5 | 1.0 | 5.0 | 5.0 | 2.5 | **25.0** | reject |
| Wall-enhancement/hemodynamic discordance localization | 4.5 | 3.0 | 1.0 | 2.0 | 2.5 | 5.0 | 5.0 | 3.0 | **26.0** | reject |

The scores were fixed together after the source-level review. No candidate is
rounded up, merged with another row or reweighted after seeing that the maximum
is one point below the threshold.

## 2. New Aneurisk CFD release: useful asset, occupied question

The official [Zenodo record](https://zenodo.org/records/19455127) reports a
1.4 GB CC BY 4.0 archive, `AneuriskCFDResults_Zenodo.tar.gz`, with MD5
`8c66e7bb359d04bd1a5d6db6da3f3926`. It describes VTP surface fields for 76
patient-specific saccular aneurysm geometries derived from Aneurisk and an
OpenFOAM laminar pulsatile solver. This is a materially useful public asset.

It is not an in-vivo hemodynamic cohort. The companion
[preprint](https://arxiv.org/html/2602.21409) uses two population-average inflow
waveforms selected by age group and scales flow by inlet diameter. It assumes
rigid walls and Newtonian blood. The source paper excludes multiple-aneurysm
trees and models with insufficient inlet or outlet lengths. The archive is thus
best described as **patient-geometry CFD under population boundary-condition
assumptions**, not patient-specific measured physiology.

The record and paper also require an asset-level reconciliation that is not
silently resolved here. The record summarizes zero-pressure outlet conditions,
whereas the paper specifies a flux-corrected velocity condition and a resistance
pressure condition at outlets. Payload inspection would be needed to determine
the executable provenance. Because no candidate crosses the source gate, the
1.4 GB archive is not downloaded merely to repair this ambiguity.

### 2.1 Curvature-only surrogate · 31.0/40

Predicting TAWSS, OSI or related fields from local geometry is identifiable in
the released VTP data and would produce clear surface figures. It nevertheless
fails the novelty axis. The companion paper already establishes Gaussian
curvature patch type as a primary determinant of TAWSS, OSI and near-wall
vortical activity, explicitly motivates curvature as a fast proxy for CFD, and
reports that the relation persists across rupture-status and aneurysm-type
subgroups. Geometry-to-flow GNNs, neural operators and PINN surrogates are also
direct controls. A learned curvature proxy would mainly automate the paper's
existing conclusion.

### 2.2 Cross-source residual added value · 30.0/40

The stronger residual question is whether CFD fields add stable
rupture-status information after clinical variables and morphology, and whether
that increment transports across CFD pipelines. The public
[CMHA record](https://springernature.figshare.com/articles/dataset/CMHA_Intracranial_Aneurysm_CTA_Image_3D_Model_Dataset_with_Clinical_Morphological_Hemodynamic_Data/26965450)
reports 99 patients with 105 MCA aneurysms, clinical variables, morphology and
scalar CFD summaries. The new Aneurisk release supplies 76 surface-field cases.

These are not two exchangeable validation cohorts. CMHA is MCA-only and exposes
summary features; the new release exposes Aneurisk surface fields, different
selection rules and different CFD assumptions. Exact cross-source feature,
case-ID and rupture-label linkage is not established by source metadata. More
importantly, both endpoints are cross-sectional status and both hemodynamic
representations are simulated. A source-robust association can be measured if
the mappings exist, but it cannot establish prospective clinical risk or an
independent physiological modality. The July 2026 PointNeXt–PINN–clinical fusion
work and classical morphology/hemodynamics rupture models further narrow the
residual novelty. The resulting 30.0/40 is not repaired by pooling lesions from
incompatible sources.

## 3. Multiple-aneurysm culprit ranking · 23.0/40

The patient-set formulation is clinically meaningful and its target can be
defined by operative or angiographic confirmation. It is, however, directly
occupied. A 2025
[multicenter study](https://doi.org/10.1016/j.ejrad.2025.112466) trained 13
families of morphology-based classifiers on 207 patients/460 aneurysms and
tested 65 patients/147 aneurysms from four additional hospitals; its best
external AUCs are approximately 0.89–0.90. The paper explicitly consolidates
aneurysms from the same patient into the same group. A 2026
[three-center study](https://doi.org/10.1227/neu.0000000000003940) separately
uses 3D circumferential wall enhancement in 30 patients with 82 aneurysms.

No audited public source supplies a sufficiently large set of SAH patients with
multiple aneurysms, one confirmed culprit per patient and the required CTA or
wall images. Open CTA multi-lesion cases and AneuX lesion families do not create
culprit labels. A set-ranking network, GNN or attention block cannot substitute
for that endpoint and would not be novel against the direct studies.

## 4. Post-treatment remnant change · 25.0/40

A 2025 open paper on
[pre/post-treatment MRA segmentation](https://doi.org/10.1049/ipr2.70199)
reports 35 paired baseline/follow-up volumes and 42 post-treatment subjects, but
identifies the Uppsala cohort as private in-house data. Its MSDA-Net already
targets treated-remnant segmentation. A July 2026 dual-center TransUNet study
also reports preoperative, postoperative and coil-treated DSA segmentation.

The public [4D-flow intervention release](https://zenodo.org/records/17183575)
does not fill the clinical endpoint gap. Its 33 acquisitions arise from five
base models derived from only two patients, with 15 device states. The related
[Communications Medicine study](https://pmc.ncbi.nlm.nih.gov/articles/PMC13031954/)
already analyzes immediate device-induced flow reduction and black-blood MRI
response. Repeated scans and device states are valuable physical controls, but
they are not 33 independent patients and contain no longitudinal occlusion or
recanalization outcome. This branch was previously closed and is not reopened.

## 5. Wall-enhancement discordance · 26.0/40

The public
[Dryad table](https://datadryad.org/dataset/doi%3A10.5061/dryad.p2ngf1vrg)
contains scalar risk, morphology, hemodynamic and enhancement values for 41
unruptured aneurysms. It does not release the spatial MRI-to-surface maps needed
for a localization model. The accompanying 2021 paper already studies
enhancement, normalized WSS, OSI and rupture-resemblance score, while earlier
work reports local low-WSS/enhancement association. A 2026
[European Radiology study](https://pubmed.ncbi.nlm.nih.gov/41935243/) directly
quantifies the three-dimensional distance between maximal enhancement and
low-WSS locations in 49 private cases.

Thus the spatial target is directly occupied and the only public table has
case-level summaries rather than spatial supervision. Reconstructing pseudo
maps from aggregate values would manufacture the target rather than identify
it.

## 6. Decision boundary

- The new Aneurisk CFD archive is added to the source catalogue as a
  source-rejected control, not a training cohort.
- Curvature maps, TAWSS/OSI channels, GNNs, PINNs, generic neural operators,
  cross-sectional rupture fusion, patient-set attention, remnant U-Nets and
  wall-enhancement/WSS correlation are direct priors or controls.
- No new archive payload, DICOM, VTP member, source image or private cohort was
  accessed. Public record pages and manuscripts are the complete audit scope.
- No P0 is registered because no candidate reaches 32/40. Consequently there is
  no PBS submission and no GPU experiment to run or monitor.
- Any future execution is restricted to `introai9` PBS. `junjinyong` remains
  excluded from connection, query, submission and monitoring.
- The next allowed action is a genuinely new or materially revised source-level
  problem audit. Only a fresh score of at least 32 may open a separately frozen,
  method-free CPU/PBS P0.

This rejection does not claim that curvature, hemodynamics, wall enhancement or
treatment response are scientifically unimportant. It states that the available
assets and 2025–2026 direct priors do not leave an independent, identifiable
method contribution suitable for AURORA's ISBI paper.
