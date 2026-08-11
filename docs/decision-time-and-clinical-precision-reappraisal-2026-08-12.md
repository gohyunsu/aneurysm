# Decision-time, hemodynamic incremental value and clinical-precision reappraisal

**Date:** 2026-08-12  
**Decision:** reject all six fresh formulations; active lead, P0, method and
compute remain zero  
**Latest best:** 30.0/40, with mandatory novelty and independent-unit floors
failed

## Executive judgment

Two 2026 clinical sources materially tighten the boundary around a plausible
aneurysm-imaging paper. A four-centre study already combines pre-operative DSA
geometry and CFD-derived hemodynamics with clinical and deployment variables to
predict incomplete occlusion after Pipeline Embolization Device (PED)
treatment. A separate study shows that two commercial CTA measurement systems
are more reproducible than manual measurement but still fail a pre-specified
clinical agreement threshold against DSA.

These sources do **not** activate a new model. They expose a more fundamental
problem: a prediction must be indexed by the information that is actually
available at its claimed decision time. A model intended to choose a treatment
before deployment cannot use immediate wall apposition or device migration seen
at follow-up. Likewise, cross-sectional CTA--DSA agreement cannot establish
that an algorithm detects biological growth across time.

The scientifically meaningful residual question is therefore:

> Does pre-operative hemodynamics add patient-level, centre-held-out predictive
> value beyond clinical and geometric information, when the information set,
> patient grouping and follow-up horizon are fixed prospectively?

That is an important evaluation question, but it is not presently executable.
The inspected clinical cohorts are not public, and the open longitudinal MRA
source is too small and incompletely annotated for a fresh confirmatory
precision method. A temporal mask, causal label, GNN, neural operator or
uncertainty head cannot substitute for the missing patient-level contract.

## 1. What the multicentre PED nomogram actually establishes

The exact primary source is
[Zhao et al., 2026](https://doi.org/10.3389/fneur.2026.1756374), published in
*Frontiers in Neurology*. It retrospectively includes **426 aneurysms from 362
patients** treated with PED Flex at four centres. Sixty-one patients had one PED
cover two or more adjacent aneurysms. The outcome is incomplete occlusion at the
first follow-up DSA, defined as residual contrast filling corresponding to
O'Kelly--Marotta grades A, B or C. Median angiographic follow-up was **199 days**
and 340/426 aneurysms were completely occluded.

The source reports a 7:3 split of the **aneurysms** into 298 development and 128
validation rows. The whole cohort was randomly divided; a centre-held-out or
chronologically held-out partition is not described. The article calls the
128-row evaluation “external validation,” but the stated protocol is a random
hold-out from the same pooled cohort. Because 61 patients contribute multiple
aneurysms and patient-grouped splitting is not explicitly stated, AURORA records
an unresolved dependence risk. It does not assert that the same patient
definitely crossed the split.

Pre-operative 3D DSA was processed with AneuFlow Pro. CFD used a rigid, no-slip,
Newtonian wall model, one normal-subject pulsatile inlet waveform and a published
mean ICA flow rate of 4.6 ml/s. Outlet flow was assigned proportional to diameter
cubed. The model used morphology, scalar hemodynamics and qualitative flow
patterns. Independent predictors reported by the source were smoking, flow
complexity, aneurysm angle, low-WSS area ratio, device migration and poor wall
apposition. Reported AUC was 0.785 in development and 0.809 in the random
validation subset. These are source results and were not reproduced by AURORA.

### The decision-time problem

The input set is not purely pre-operative:

- poor wall apposition was read on immediate VasoCT after deployment;
- device migration was defined from immediate postoperative or follow-up DSA
  relative to the intra-operative release site;
- the outcome was assessed at the first follow-up DSA.

The resulting nomogram may be useful for **post-deployment risk updating**, but
it cannot be read without qualification as a pre-operative device-selection
model. The article's conclusion emphasizes pre-operative hemodynamics, while
two of its final predictors become known only after treatment has begun. The
proper correction is to define separate information sets rather than label the
paper invalid:

1. **pre-operative:** clinical state, baseline image, geometry and baseline CFD;
2. **post-deployment:** add device size, landing zone and immediate apposition;
3. **follow-up update:** add migration and interval imaging;
4. **outcome:** delayed occlusion, retreatment, complication and a fixed horizon.

Performance and utility must be reported separately at each stage. Later
observations may improve prognosis but cannot support an earlier intervention
claim.

The raw data statement is author-availability rather than a public, versioned
patient release. No public code release is stated in the inspected article.
Consequently, AURORA cannot audit patient identifiers, centre membership,
split assignment, case-wise CFD values or exact information timestamps.

## 2. What the clinical-precision study establishes—and does not establish

The second primary source is
[Chen et al., 2026](https://doi.org/10.1186/s12880-026-02209-2) in *BMC Medical
Imaging*. It includes **148 patients with 163 aneurysms** on CTA; 86 patients
also had DSA within one week. Shukun AI, UIH AI and manual CTA measurements were
compared for neck width and maximum length. A 95% limit of agreement contained
within **±1.0 mm** was prospectively treated as clinically acceptable.

The source reports narrower coefficients of variation for the commercial AI
systems than for manual CTA, yet every AI/manual comparison against DSA exceeded
the ±1.0 mm agreement boundary. The two platforms also showed different
systematic bias directions. This directly warns against interpreting improved
reproducibility as adequate clinical precision or switching platforms during
serial surveillance.

The study is nevertheless **cross-sectional**, single-centre and limited to two
proprietary systems. CTA and DSA were paired within one week; true biological
growth, treatment choice and patient outcome were not followed longitudinally.
Its dataset is available only on reasonable request. It therefore motivates an
acquisition- and platform-aware longitudinal evaluation, but does not supply
the public repeated-imaging reference needed to execute one.

The direct-prior boundary is even stronger after adding the May 2026 autonomous
CTA study
[Pettersson et al.](https://doi.org/10.1148/ryai.251093). Its abstract reports
2,980 patients, 2,585 aneurysms and five international centres, with internal
prospective and multicentre external testing of end-to-end detection and
morphology extraction. A public web interface is not a public training or
patient-level evaluation release. Generic “automated morphology from CTA” is
therefore already directly occupied at clinical scale.

## 3. Why this does not rescue the open longitudinal branch

OpenNeuro `ds005096` remains the only relevant open longitudinal imaging source
in the frozen inventory. It has 63 patients, 85 aneurysms and 24 patients with
follow-up scans, but expert derivatives cover one selected session per subject.
Only four patients provide same-session acquisition variants that can act as
no-biological-change controls.

The April 2026 Bayesian displacement direct prior already screens the 24
follow-up patients and retains 16 patients with 19 aneurysms, including six
growth positives. It performs surface registration, uses adjacent vessel
displacement as an internal processing control and models measurement error.
Local growth maps, healthy-vessel calibration and probabilistic growth are
therefore not unoccupied novelty. The commercial-platform paper adds a clinical
precision failure, but it does not increase the four-patient acquisition-control
unit or release longitudinal ground truth.

The previously frozen 31.5 acquisition-orbit formulation is not repaired. In
this fresh context it scores lower because clinical cross-platform precision
and Bayesian internal-reference control are now direct priors. No payload is
opened and no historical score is overwritten.

## 4. Frozen non-compensatory screen

Axis order is importance, target identifiability, residual novelty, asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total at least
32 **and** all mandatory floors. Scores were frozen as one batch and are not
reweighted or renamed after inspection.

| candidate | axis scores | total | decision |
|---|---|---:|---|
| Acquisition-conditioned longitudinal morphology precision certificate | 5.0 / 4.5 / **2.0** / 4.0 / **1.5** / 5.0 / 5.0 / 3.0 | **30.0** | Reject: four same-session controls; Bayesian and clinical-precision mechanisms are direct prior |
| Decision-time-stratified PED occlusion prediction | 5.0 / 4.5 / 3.0 / **0.5** / **1.0** / 5.0 / 5.0 / 2.0 | **26.0** | Reject: meaningful formulation but no public timestamped patient rows or external cohort |
| Pre-operative CFD incremental value over geometry | 5.0 / 5.0 / **1.0** / **0.5** / **1.0** / 5.0 / 5.0 / 3.0 | **25.5** | Reject: hemodynamic nomogram is direct prior and case-wise data are unavailable |
| Patient-grouped, centre-held-out nomogram revalidation | 5.0 / 5.0 / **0.5** / **0.5** / **1.0** / 5.0 / 4.0 / 4.0 | **25.0** | Reject: rigorous evaluation correction is necessary but not independent method novelty |
| Deployment-mediator-aware dynamic occlusion update | 5.0 / 4.0 / 2.5 / **0.5** / **1.0** / 4.5 / 5.0 / 2.0 | **24.5** | Reject: no timestamped deployment/outcome asset and dynamic prediction is generic prior |
| Outcome-grounded autonomous morphometry and neck planning | 5.0 / 3.5 / **1.0** / **0.5** / **1.0** / 5.0 / 5.0 / 2.0 | **23.0** | Reject: automated morphology is directly occupied and no treatment-benefit target is joined |

The best additive row is 30.0 and fails residual-novelty and independent-unit
floors. The largest novelty value is 3.0 for the decision-time formulation, but
its asset and patient-unit values are 0.5 and 1.0. No row is an admitted lead.

## 5. What remains scientifically useful

Three evaluation principles are retained without becoming contributions:

1. **Information-set declaration.** Every prediction must state what is known
   at baseline, immediately after deployment and during follow-up.
2. **Incremental-value falsifier.** A future hemodynamic method must beat a
   patient-grouped clinical+morphology baseline at fixed information time,
   centre shift and follow-up horizon—not merely improve apparent fit.
3. **Clinical precision before longitudinal claims.** Repeatability, agreement
   and biological change are separate quantities. Platform bias must not be
   counted as aneurysm growth.

A future admissible source must expose a lawful, versioned patient identifier,
centre, lesion-to-patient map, exact timestamps, baseline 3D imaging, geometry,
CFD or measured flow, deployed device/apposition, fixed-horizon occlusion and
safety, and patient-grouped centre-held-out confirmation. A pre-registered
analysis would compare clinical-only, morphology-only, clinical+morphology and
the same model plus hemodynamics. It would report discrimination, calibration,
decision utility and confidence intervals clustered at the patient level.

This contract could support a competitive ISBI application paper if it also
revealed a reproducible failure of the strongest baseline. It does not exist in
the currently inspected public assets.

## 6. Surface-vector adjudication and operational boundary

The supplied surface-vector analysis remains correctly bounded. Field accuracy
may fail to preserve critical-flow organization, but that failure has not been
observed on a stable task. Task stability → field-error-matched failure →
bounded development → fresh confirmation → external interpretation remains the
only acceptable order. Edge 1-forms, Hodge decomposition, SE(3) equivariance,
periodic operators and structural losses are unselected direct-prior controls,
not novelty or an architecture.

Historical job `115645.ECE-util1` remains E/exit 2 with 0/10 registered checks,
`execution-incomplete/no scientific verdict`. It is not repaired, rerun or
relabelled. None of the new sources is a transient surface-WSS E0.

- Active lead, primary problem, P0/P1, method, architecture, outer test, result
  row, C21, claim and submission identity remain zero.
- No patient image, spreadsheet, CFD field, code or proprietary-model payload
  was downloaded.
- No scientific server was queried and no PBS/GPU job was created or monitored.
- Future gate-authorized work may use only `introai9` through PBS. Login-node
  GPU commands are prohibited.
- `junjinyong` was not and must never be accessed, queried, transferred to,
  submitted to or monitored.

The next allowed action is another genuinely new problem-level source or
material-asset audit. A paper title, model name or architecture cannot be
selected before such a source passes the gate.
