# TopBrain 2025 release and RSNA multitask source correction

**Audit date:** 2026-08-12  
**Protocol state:** schema 10.4 prospective source screen  
**Decision:** material source correction, but all six formulations rejected;
no active paper identity, terms acceptance, payload access, P0, method,
architecture, scientific-server query or compute

## Executive verdict

The previous watch treated the future TopBrain 2.0 design record as the only
TopBrain material signal. That was incomplete. The distinct **TopBrain 2025**
challenge already has a public data record and exact podium Docker record. The
correction matters because it supplies same-patient CTA/MRA whole-brain vessel
anatomy labels and unusually strong executable controls.

It does **not** create an aneurysm study by itself:

- 50 public volumes are 25 CTA/MRA pairs from 25 patients, not 50 independent
  patients;
- the labels describe whole-brain arterial and venous anatomy, not aneurysm
  masks, rupture, growth, treatment response or WSS;
- the data record exposes custom download terms, while its API license field is
  null; AURORA accepted no terms and opened no archive;
- TopCoW already occupies paired CTA/MRA topology-aware Circle-of-Willis
  segmentation and a small external aneurysm-location analysis;
- BraveCoWCoW already combines four modalities, tri-axial ROI extraction,
  vessel segmentation and aneurysm classification/segmentation; its dense
  masks are iterative pseudo-labels rather than an independent expert-dense
  reference;
- public baseline code is not the controlled RSNA image cohort.

The strongest fresh formulation, a paired-modality graph-agreement
certificate, scores **30.5/40** and fails both residual-novelty and
asset-readiness floors. Adding cross-attention, a topology loss, uncertainty or
a graph head would stack occupied components without repairing the target.

## 1. Material correction: TopBrain 2025 is already released

The official [TopBrain 2025 data record](https://zenodo.org/records/16878417)
is distinct from the under-construction TopBrain 2.0 design record. The exact
machine-readable state frozen by AURORA is:

| Field | Exact state |
|---|---:|
| Zenodo record | `16878417` |
| Revision | 14 |
| Modified | `2026-06-02T16:56:20.313691+00:00` |
| File | `TopBrain_Data_Release_Batches1n2_081425.zip` |
| Bytes | 1,958,849,592 |
| MD5 | `b703ea31cd1f0e7115a5d3e6e61f59b3` |
| API access right | open |
| API license identifier | null |

The record text points to custom opendata.swiss terms and treats download as
agreement. “Open” access metadata therefore does not authorize AURORA to
accept those terms. No archive bytes, NIfTI image or label payload were opened.

### Correct independent-unit accounting

The public release contains 50 volumes from **25 same-patient CTA/MRA pairs**.
The full challenge contains 90 volumes from 45 patients, including a hidden
40-volume/20-patient test set. Consequently:

\[
n_{\text{public independent patient}}=25,\qquad
n_{\text{public volume}}=50.
\]

A model may see two modalities, but statistical uncertainty must cluster the
pair by patient. Reporting 50 independent cases would halve neither dependence
nor uncertainty; it would only inflate the nominal sample.

### Correct target semantics

The source describes 40 CTA labels, 42 MRA labels and 34 overlapping labels,
within a 48-class whole-brain vascular anatomy. These classes are valuable for
arterial/venous anatomy and branch-aware segmentation. They are not dense
aneurysm masks or lesion outcomes. A vessel graph can provide context to a
later aneurysm model, but context is not the target.

The source paper reports challenge endpoints for overlap, topology, small
branches, foreground contamination and anatomically invalid adjacency. Those
endpoints directly threaten claims that topology correction, contamination
control or small-branch sensitivity is independently novel. Source-reported
challenge performance is not an AURORA result.

## 2. Executable direct priors: exact TopBrain podium Dockers

The official [TopBrain 2025 podium record](https://zenodo.org/records/20158639)
is revision 18, modified `2026-06-02T16:51:06.110189+00:00`, and declares
CC BY 4.0. Its exact seven-file inventory includes two launch utilities and
five Docker archives:

| File | Bytes | MD5 |
|---|---:|---|
| `reorient_nii.py` | 2,459 | `3c540a37710c1c7c84c3704246fbe220` |
| `run_docker_topbrain_2025.py` | 5,581 | `e9f0d16e497c28f897aa892a5e328b4c` |
| ARG CT | 5,863,399,183 | `35d5434f91a274456f72f428fce067e0` |
| ARG MR | 6,094,969,422 | `e1fe74d1707907918b1b91002962f40f` |
| KDH CT | 8,038,457,100 | `4b71fe691b99e8a76cd0d83ebcf2da95` |
| KDH MR | 11,864,241,848 | `0224662747a594f5bc17932f5c85c313` |
| UZH CT/MR | 4,795,293,483 | `7d04086c75bdd459f4a8af44e753be0a` |

No Docker archive or script body was opened. Their importance is conceptual:
if a future aneurysm target becomes lawful and identifiable, these are direct
paired-modality anatomy baselines. They are not evidence for selecting an
AURORA architecture now.

## 3. Direct prior: TopCoW already owns paired CTA/MRA topology

[TopCoW](https://doi.org/10.1007/978-3-031-43901-8_12) uses same-patient paired
CTA/MRA and evaluates multi-class Circle-of-Willis segmentation with topology.
Its challenge accounting is 200 unique patients: 125 training, 5 validation
and 70 test. The ROI excludes large aneurysms, so TopCoW is not a general dense
aneurysm target. Nevertheless, it already occupies:

- paired CTA/MRA cerebrovascular segmentation;
- mixed-modality training;
- branch anatomy and topology evaluation;
- an external aneurysm-location analysis on 12 LargeIA patients.

Therefore “use paired modalities and a graph/topology consistency loss” is not
a residual research gap. A fresh claim would need a different, independently
referenced aneurysm endpoint and enough paired patients to test it.

## 4. Direct prior: BraveCoWCoW already owns the multimodal multitask design

The 2026 paper
[Intracranial Aneurysm Classification and Segmentation via Tri-Axial ROI and Multi-Task Learning](https://arxiv.org/abs/2606.26706)
describes the second-place RSNA 2025 solution. The official
[Apache-2.0 repository](https://github.com/PengchengShi1220/RSNA2025_Intracranial-Aneurysm-Detection)
is frozen at exact head
`e59e2368a722eabedc6b2228b1c6e1e7325cacd5`, has no GitHub release, and
contains preprocessing, inference notebooks, an nnXNet tree and a plans file.

Its scientific design already includes:

- CTA, MRA, T2 and post-contrast T1;
- 13 aneurysm-location classes and 13 vessel classes;
- tri-axial ROI extraction;
- vessel/aneurysm multi-task decoding and cross-attention;
- iterative predict--correct--retrain pseudo-mask generation across 4,348
  series.

The source reports public/private challenge AUC 0.90035/0.86727. AURORA did not
reproduce these values. More importantly, RSNA supplies lesion centres but not
an independent expert-dense aneurysm-mask benchmark. The paper's iterative
pseudo-masks may be useful supervision, but they cannot validate their own
dense boundary accuracy. Qualitative segmentation examples are not an
independent dense-reference test.

Public source code also does not convey the controlled, non-redistributable
RSNA data. AURORA accepted no RSNA terms and accessed neither images nor
weights.

## 5. Other direct-prior pressure

The residual gap is further narrowed by paired-data cross-modality
cerebrovascular segmentation, multimodal pre/post-treatment consistency
learning, generic selective/conformal segmentation and segmentation-to-flow
uncertainty studies. A 2026 CTA-versus-TOF-MRA Circle-of-Willis study also
reports modality-dependent pressure-model sensitivity in 19 patients, but
offers no public joined image--segmentation--flow--pressure asset for AURORA.

These sources do not prove that uncertainty or paired-modality robustness is
unimportant. They show that a paper must identify a specific aneurysm failure,
reference and executable cohort rather than call the component combination the
contribution.

## 6. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at
least 32 **and** every critical floor.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Paired CTA/MRA graph-agreement certificate | 4/5/2/2.5/3/5/5/4 | **30.5** | Reject: same-patient graph consistency is directly occupied; novelty and asset floors fail |
| Small-branch failure-aware selective segmentation | 4/4.5/1/2.5/3/5/5/4 | **29.0** | Reject: TopBrain already owns small-branch, contamination and topology endpoints; selection is generic |
| Paired-modality aneurysm-location robustness | 5/3.5/1.5/1.5/2/5/5/3.5 | **27.0** | Reject: TopCoW is direct prior and no public same-patient aneurysm-pair target is joined |
| Reference-provenance-aware RSNA dense pseudo-label audit | 5/3/2.5/0.5/1/5/5/3 | **25.0** | Reject: controlled data and no independent dense reference; audit is not method novelty |
| Segmentation uncertainty to hemodynamic-pressure certificate | 5/4/1.5/0.5/1/5/5/3 | **25.0** | Reject: no public image--segmentation--flow--pressure join and direct priors exist |
| Anatomy-conditioned multimodal aneurysm segmentation | 5/4.5/0.5/0.5/1/5/5/3 | **24.5** | Reject: BraveCoWCoW directly occupies the task and architecture family |

All six candidates fail at least one critical floor. No score is repaired from
schema 10.3, and no historical candidate or execution-incomplete P0 is
relabelled.

## 7. What remains useful, but is not a contribution

Three principles remain mandatory evaluation controls:

1. **Count patients, not volumes.** Paired modalities and repeated views stay
   within the same bootstrap/split unit.
2. **Separate context from target.** Vessel anatomy labels can condition an
   aneurysm model but cannot stand in for an aneurysm mask, event or treatment
   outcome.
3. **Name the reference provenance.** Expert dense labels, centres,
   pseudo-labels and algorithm-assisted corrections must be reported
   separately.

These principles improve validity. They are not, alone, a method contribution.

## 8. Gate for any future execution

A fresh candidate may enter a method-free P0 only if a new official version
establishes all of the following:

1. lawful terms or an explicit license accepted by the user;
2. patient-level modality pairing and lesion multiplicity;
3. an aneurysm-specific dense mask, event, treatment or functional target;
4. independent reference provenance rather than self-generated pseudo-labels;
5. a machine-auditable patient-grouped development/confirmation split;
6. a direct-prior residual gap that is not graph consistency, topology loss,
   cross-attention, uncertainty or another occupied component;
7. enough independent patients for a registered uncertainty calculation.

P0 would audit only those semantics and files. A pass could open a separately
registered method-free P1, not an architecture or GPU run.

## 9. Consequence for the surface-vector hypothesis and ISBI 2027

TopBrain and BraveCoWCoW do not provide transient surface WSS, stable signed
critical points, cardiac-cycle worldlines or an observed field-error-matched
structural failure. They are not a material E0 for surface-vector re-entry.
Edge 1-forms, Hodge/DEC, equivariance and periodic operators remain inactive
controls, not novelty.

For ISBI 2027, a compelling application paper would still require one
identified aneurysm imaging estimand, one mechanism-linked minimal method and
fresh confirmatory evidence. This batch supplies strong controls but not that
identity. No scientific server was queried, no transfer occurred, and no PBS
or GPU job was created. Future authorized execution remains `introai9` PBS
only; login-node GPU commands are forbidden and `junjinyong` remains excluded.

## Source ledger

- TopBrain 2025 data: [Zenodo 16878417](https://zenodo.org/records/16878417)
- TopBrain 2025 podium Dockers: [Zenodo 20158639](https://zenodo.org/records/20158639)
- TopBrain source manuscript:
  [doi:10.64898/2026.05.28.26354312](https://doi.org/10.64898/2026.05.28.26354312)
- TopCoW: [challenge paper](https://doi.org/10.1007/978-3-031-43901-8_12)
- BraveCoWCoW: [arXiv:2606.26706](https://arxiv.org/abs/2606.26706),
  [official code](https://github.com/PengchengShi1220/RSNA2025_Intracranial-Aneurysm-Detection)
