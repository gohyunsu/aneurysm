# Culprit-lesion and mimic-differential source reappraisal

**Audit date:** 2026-08-12

**Protocol state:** schema 10.5 prospective source screen

**Decision:** all six formulations rejected; no active paper identity, data
request, payload access, P0, method, architecture, scientific-server query or
compute

## Executive verdict

Two clinically precise problems are more defensible than generic rupture
classification:

1. identify the responsible lesion **within one patient** who presents with
   subarachnoid haemorrhage and multiple aneurysms; and
2. distinguish a true aneurysm from an infundibulum or other vascular mimic
   before recommending invasive confirmation or serial surveillance.

They are not currently executable AURORA paper identities. Culprit-lesion
prediction is already directly occupied by an eight-hospital CTA morphology
study and a three-institution vessel-wall MRI study. The most attractive
residual formulation would align the non-contrast CT haemorrhage distribution
with the complete CTA lesion set, but no versioned public asset joins those
images, every candidate lesion, a patient-level culprit reference and a
patient-grouped split. The mimic problem is important, but the largest recent
longitudinal cohort is single-centre and does not expose a versioned image and
reference release. A public ICAN table is simulated, not patient evidence.

The best fresh formulation scores **30.5/40** and fails the mandatory
asset-readiness floor. No model name, set transformer, graph layer, conformal
wrapper or acquisition-policy head can repair that missing target.

## 1. Culprit identification is a set-conditional target

The independent statistical unit is the patient, not an aneurysm row. For
patient \(i\), the input is a set of candidate lesions
\(\{a_{i1},\ldots,a_{im_i}\}\), and the acute target is which member caused the
observed haemorrhage. A conventional lesion-wise classifier can assign high
scores to several lesions without enforcing the patient-set constraint. It may
also leak the same patient across development partitions when aneurysm rows are
split independently.

This distinction is scientifically useful, but not itself novel. The 2025
European Journal of Radiology study already develops CTA morphology models to
identify the responsible aneurysm. It includes 207 patients/460 aneurysms from
four hospitals for development and internal validation, plus 65 patients/147
aneurysms from four other hospitals for external validation. The source reports
external AUC 0.898 for Gaussian process, 0.892 for logistic regression and
0.897 for quadratic discriminant analysis. These are source results, not
AURORA results.

The source target was established using CT haemorrhage patterns or
neurosurgical findings. That makes haemorrhage--lesion spatial compatibility a
plausible residual mechanism, but also means that simply adding an NCCT branch
does not create novelty. A defensible study would need an independently
adjudicated reference and must show that its evidence alignment improves
patient-level top-1 accuracy or set coverage beyond morphology and haemorrhage
pattern controls.

No inspected primary-source record provides a stable public release containing
the required CTA/NCCT images, all within-patient lesions, culprit adjudication
and exact patient-grouped development/confirmation manifest. A literature
cohort is not an executable dataset.

## 2. Vessel-wall enhancement is already a direct culprit prior

A 2026 three-institution study includes 30 patients with 82 aneurysms, of which
30 were classified symptomatic and 52 asymptomatic. It directly tests
three-dimensional circumferential aneurysm wall enhancement together with
morphology. The source reports 88% specificity and 79% negative predictive
value at a 3D-CAWE cutoff of 1.02.

This study establishes neither a large confirmation cohort nor a public
versioned asset. It also predicts symptomatic status, which must not be
silently equated with the precise acute rupture culprit in every patient.
Nevertheless, it directly occupies the broad claim that wall-enhancement plus
morphology identifies the symptomatic lesion among multiple aneurysms.

## 3. Smaller-counterpart rupture is not prospective prevention evidence

A single-centre Scientific Reports cohort contains 285 patients with multiple
aneurysms and acute aSAH. The largest aneurysm was judged responsible in 261
patients and a smaller counterpart in 24. Two neuroradiologists and two
neurosurgeons reviewed haemorrhage distribution and procedural or operative
evidence. The source makes remaining anonymized data available only on request.

This supports the clinical failure of a naive “largest lesion first” rule. It
does not turn an after-rupture case-control label into a prospective future
rupture estimand. The source itself describes the retrospective,
cross-sectional, single-centre design and small smaller-counterpart subgroup as
limitations. AURORA therefore retains lesion multiplicity and within-patient
ranking as evaluation principles, not as a preventive-treatment claim.

## 4. Infundibulum differential is important but not asset-ready

The 2026 AJNR longitudinal analysis reports 665 intracranial outpouchings:
321 unequivocal infundibula and 344 lesions reported as “aneurysm versus
infundibulum.” Follow-up was available for 146 and 208 lesions respectively,
totalling 1,040 lesion-years. The source reports no complication or
morphological change; only ten ambiguous lesions had later DSA re-review, with
reported complete concordance when strict morphology criteria were applied.

Those observations support structured reporting and careful acquisition
decisions. They do not provide a public multicentre image benchmark with DSA
reference, reader disagreement, surveillance decision and outcome. A model
trained on diagnostic report labels could merely reproduce interpretive
variability. Generic selective prediction, learning-to-defer and acquisition
policy methods are also direct methodological priors.

## 5. Public tables and challenge data do not close the gap

The French ICAN public portal explicitly describes its downloadable clinical
table as **simulated**. It is useful for computational reproducibility of the
published analysis but cannot be counted as patient-level imaging evidence or
an external clinical test.

TopAneu 2026 offers a strong multi-centre CTA/MRA vessel-specific detection and
segmentation benchmark under a custom data agreement. Its target is fine-grained
vessel location and segmentation, not culprit attribution, haemorrhage--lesion
alignment or expert-adjudicated infundibulum differential. It is already
tracked by the existing source ledger and is not a substitute target.

## 6. Frozen non-compensatory screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at
least 32 and every critical floor.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Haemorrhage-conditioned patient-set evidence alignment | 5/5/2.5/0.5/3.5/5/5/4 | **30.5** | Reject: plausible residual mechanism, but no public joined CTA--NCCT--lesion-set--culprit asset |
| Patient-set conformal culprit shortlist | 5/5/1.5/0.5/3.5/5/5/4 | **29.5** | Reject: generic set-risk control and the same absent confirmation asset |
| Smaller-counterpart prospective triage | 5/3/1.5/1/3.5/5/5/4 | **28.0** | Reject: after-rupture cross-sectional label is not future rupture risk |
| Infundibulum-aware DSA escalation | 4.5/4.5/2/0.5/1/5/5/3.5 | **26.0** | Reject: request-only/single-centre references and too few DSA-confirmed ambiguous cases |
| VWI--morphology discordance localization | 5/4.5/0.5/0.5/1/5/5/4 | **25.5** | Reject: direct prior, 30 patients and no public versioned cohort |
| Longitudinal conundrum surveillance deferral | 4.5/2.5/1.5/0.5/2/5/4.5/3.5 | **24.0** | Reject: report label and follow-up selection do not identify a treatment/action target |

All six fail at least one critical floor. The 30.5 score is not rounded up and
does not compensate for asset 0.5/5. No historical score or job is repaired or
relabelled.

## 7. What a material re-entry would require

A fresh version may register a method-free P0 only after an official source
establishes:

1. lawful access and an explicit image-use license accepted by the user;
2. one patient identifier grouping every candidate aneurysm;
3. aligned NCCT and CTA, or a precisely declared alternative information set;
4. culprit reference provenance separated into haemorrhage pattern,
   operation/procedure and adjudication;
5. ambiguity and multi-culprit handling rules;
6. a patient-grouped, centre-separated confirmation manifest;
7. enough independent patients for top-1 accuracy and set-coverage uncertainty;
8. morphology-only, haemorrhage-pattern and recent published-model controls.

P0 would audit only these semantics and file integrity. Passing it would open a
separate method-free P1, not a model or GPU run.

## 8. Consequence for surface-vector and ISBI 2027

This audit neither repairs nor invalidates the inactive surface-vector
hypothesis. None of these sources supplies transient WSS, stable signed
critical points, cardiac-cycle worldlines or an observed field-error-matched
failure. Edge 1-forms, Hodge decomposition, equivariance, periodic operators
and structural losses remain unselected controls.

The strongest possible ISBI identity from this batch would be patient-set
haemorrhage--lesion evidence alignment, not a generic GNN rupture classifier.
It remains conditional on a material joined asset. No scientific server was
queried, no transfer occurred and no PBS or GPU job was created. Future
authorized execution remains `introai9` PBS only; login-node GPU commands are
forbidden and `junjinyong` remains excluded.

## Source ledger

- Eight-hospital CTA culprit models:
  [doi:10.1016/j.ejrad.2025.112466](https://doi.org/10.1016/j.ejrad.2025.112466)
- Three-institution VWI symptomatic-lesion study:
  [doi:10.1227/neu.0000000000003940](https://doi.org/10.1227/neu.0000000000003940)
- Smaller-counterpart rupture cohort:
  [Scientific Reports](https://www.nature.com/articles/s41598-025-21914-6)
- Infundibulum longitudinal cohort:
  [doi:10.3174/ajnr.A9135](https://doi.org/10.3174/ajnr.A9135)
- Simulated ICAN reproducibility table:
  [data.gouv.fr](https://www.data.gouv.fr/datasets/dataset-to-develop-diagnostic-and-predictive-tools-addressing-ia-rupture-risk)
- TopAneu challenge scope:
  [Grand Challenge](https://topaneu-26.grand-challenge.org/)
