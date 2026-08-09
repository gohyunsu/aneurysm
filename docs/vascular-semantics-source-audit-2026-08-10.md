# 2026-08-10 Vascular-semantics source audit

## Decision

This was a fresh, source-only batch. The scoring rule was frozen before comparing
the six candidates: eight axes, each scored from 0 to 5, and an admission line of
32/40. The axes are clinical/scientific importance, target identifiability,
residual novelty after direct prior work, usable asset readiness, effective
independent unit, strength of available baselines, interpretable-figure value,
and feasibility before the ISBI deadline.

No candidate reached the admission line. The best candidate, paired-modality
whole-brain vascular anatomy from TopBrain, scored **29.5/40**. The active source
shortlist, selected primary problem, method, architecture, executable P0, GPU
training, outer test, and submission identity therefore remain **zero**. No
candidate payload was accessed. We do not alter an axis weight or add a method
name after seeing these totals.

| Rank | Frozen candidate | Importance | Identifiability | Residual gap | Asset | Independent unit | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | TopBrain paired-modality vascular anatomy | 4.0 | 3.5 | 1.5 | 4.0 | 3.0 | 5.0 | 5.0 | 3.5 | **29.5** | reject |
| 2 | Healthy IXI vessel atlas as aneurysm-anomaly support | 4.0 | 2.0 | 1.5 | 4.5 | 4.5 | 4.5 | 4.0 | 3.5 | **28.5** | reject |
| 3 | VesselVerse protocol-conditioned vessel distributions | 4.0 | 2.0 | 1.5 | 2.0 | 4.5 | 4.5 | 5.0 | 4.0 | **27.5** | reject |
| 4 | NeckSpline multi-loop/artifact extension | 4.5 | 4.5 | 0.5 | 2.0 | 4.0 | 5.0 | 5.0 | 1.0 | **26.5** | reject |
| 5 | Paired CTA dose/reconstruction phantom orbit | 5.0 | 5.0 | 1.5 | 0.5 | 0.5 | 4.5 | 5.0 | 4.0 | **26.0** | reject |
| 6 | ADAM longitudinal or post-treatment remnant task | 4.5 | 1.5 | 1.5 | 1.5 | 2.5 | 5.0 | 5.0 | 3.5 | **25.0** | reject |

The total is the arithmetic sum of the displayed cells. “Reject” means reject
this candidate version before data access or compute; it does not mean the source
dataset or published paper is scientifically poor.

## 1. TopBrain paired-modality vascular anatomy · 29.5/40

The [official TopBrain summary](https://www.medrxiv.org/content/10.64898/2026.05.28.26354312v1)
reports 90 annotated CTA/MRA volumes and 48 fine-grained arterial and venous
classes, with 50 training volumes public. The
[official data page](https://topbrain2025.grand-challenge.org/data/) clarifies the
effective public paired unit: 25 patients, each with CTA and MRA. This is much
more informative than counting the 50 volumes as 50 independent people.

The attractive hypothesis would be cross-modal correspondence or
topology-calibrated vascular graphs. It is not admitted because TopBrain already
defines detection-aware segmentation, anatomical-plausibility, contamination,
and hidden-test evaluation; strong challenge submissions already occupy the
main method space. More importantly, its 48-class target is whole-brain vascular
anatomy, not aneurysm presence, extent, growth, treatment response, or rupture.
Using the 25 paired patients for a renamed graph architecture would drift away
from the aneurysm problem without creating a separately identified endpoint.

## 2. Healthy IXI atlas as aneurysm-anomaly support · 28.5/40

The [Scientific Data descriptor](https://www.nature.com/articles/s41597-025-06354-1)
releases vessel masks for 100 healthy IXI MRA subjects from two sites. It uses
Frangi initialization, manual refinement, surgeon review, and a three-rater
technical-validation subset of 10 volumes. The annotation asset is real and
useful, but it contains healthy anatomy only.

The rejected proposal would learn a healthy-vessel support and use deviations as
aneurysm evidence. Without same-protocol diseased controls or observed
healthy/pathological pairs, site, scanner, intensity, age, and pathology remain
confounded. Existing healthy vascular atlases and vessel segmentation methods
are direct controls. Combining this healthy IXI source with ADAM, TopAneu, or CTA
lesions would not manufacture the missing counterfactual; it would mostly test
cross-dataset domain discrimination.

## 3. VesselVerse protocol-conditioned distributions · 27.5/40

[VesselVerse at MICCAI 2025](https://papers.miccai.org/miccai-2025/1004-Paper0087.html)
reports 950 annotated images and up to nine annotations. The official paper and
author response are crucial for interpreting that phrase: a single assisted
manual annotator is combined with Frangi and several segmentation-model outputs,
and the term “expert” deliberately includes algorithms. Four specialists rated
five annotations per image over 20 selected images; this is not a voxel-level
multi-radiologist distribution for every subject.

The official repository was inspected at exact `main`
`ef94d3fd3ce9102cf396a83b1554c98f9f1b5e99`. It requires an email request with
name, affiliation, and intended use; original IXI, TubeTK, and TopCoW images must
be obtained under their own terms. Its MIT repository license does not by itself
establish one license for the external images and requested annotation payload.
The README also states that comprehensive quality control is still under
development. No email request or payload access was performed.

Protocol-conditioned consensus is a legitimate future benchmark question, but
the source does not identify a human annotator distribution for aneurysm labels.
STAPLE, label fusion, protocol-aware aggregation, versioning, and annotator-
uncertainty models are direct prior work. Treating algorithm outputs as
independent clinicians would be pseudoreplication.

## 4. NeckSpline extension · 26.5/40

[NeckSpline](https://www.nature.com/articles/s41746-026-02613-6) already treats
the aneurysm neck as a centerline-guided periodic cubic B-spline, uses explicit
topology and tightness constraints, evaluates neck width and angle, reports
perturb-and-refit uncertainty and artifact stress tests, and discusses adaptive
multi-loop extensions. Its expert neck loops were derived because MCA-CTA and
ADAM do not natively provide them; the paper does not release those loops as a
standalone public target asset.

Consequently, “a fancier spline,” multi-loop handling, topology loss, or
uncertainty calibration is an incremental extension of a 2026 direct prior. A
new method would need a different clinical decision target plus released labels
and a strong comparative evaluation. Those prerequisites do not exist in the
audited sources on an ISBI schedule.

## 5. Paired CTA acquisition orbit · 26.0/40

The [Scientific Reports phantom study](https://www.nature.com/articles/s41598-025-04830-7)
is unusually clean about nuisance intervention: one realistic head phantom with
three aneurysms was scanned at 21 dose levels, reconstructed by IR and FBP, and
repeated three times, yielding 126 scans. Five neuroradiologists and a commercial
AI system were assessed. This is strong within-phantom identifiability.

It is not 126 independent anatomies. The effective anatomy count is one and the
lesion count is three; the publication already demonstrates the central
inconsistency claim. The paper's data-availability URL returned HTTP 404 on
2026-08-10, so no manifest, payload, or asset license could be audited. Generic
phantom QA, degradation robustness, task-informed reconstruction, calibration,
and AI monitoring are direct prior families. This is a useful external stress
test if a future method exists, not a sufficient primary learning problem.

## 6. ADAM longitudinal/post-treatment task · 25.0/40

The [official ADAM source](https://adam.isi.uu.nl/data/) describes a registered,
confidentiality-agreement challenge with 113 training cases, including 35
baseline/follow-up pairs, and a hidden test set. The official evaluation concerns
untreated aneurysms and does not turn repeated scans into a released treatment-
response endpoint. Treated locations are not a public remnant target.

Therefore neither “post-treatment remnant segmentation” nor prospective growth
can be recovered by relabeling ADAM follow-up scans. Patient-grouped splitting is
mandatory, hidden test labels are unavailable, and access terms have not been
accepted on the user's behalf. Existing fully supervised ADAM methods and
longitudinal surface-change models remain required controls.

## Consequence for architecture and compute

There is no current GNN, U-Net, Transformer, operator, or foundation-model
architecture. Selecting one before a problem survives the source and task-unit
gates would make the architecture the paper's identity and invite an incremental
review. The next admissible action is a genuinely new or materially revised
primary-source audit. A candidate scoring at least 32 may open only a separate,
prospectively registered, method-free CPU/PBS P0. GPU work may follow only after
that P0 and task-adequacy gate pass.

All AURORA execution remains `introai9`-only through PBS. `junjinyong` is excluded
from connection, status checks, submission, and monitoring. This source-only
batch created no PBS job and ran no login-node GPU command.

