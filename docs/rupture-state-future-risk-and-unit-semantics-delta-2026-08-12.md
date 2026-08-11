# Rupture state, future risk and independent-unit source delta

> **Frozen delta decision · schema 10.7 unchanged · 2026-08-12 KST:** A new
> three-centre study provides important external-centre evidence for
> cross-sectional rupture-*status* classification, but it does not identify
> future rupture risk. The strongest of six residual formulations scores
> **27.5/40** and all six fail at least one mandatory gate. No patient image,
> feature row, supplementary table body, data request, P0/P1, method,
> architecture, scientific-server query, PBS/GPU job, outer test or paper claim
> is opened.

This delta asks a narrow but consequential question: does the latest
multicentre rupture literature create an executable, independently novel ISBI
problem for AURORA? It does not repair any historical job and it does not turn
cross-sectional rupture labels into a prospective endpoint.

## 1. The new three-centre result is a status classifier

The 2026 QIMS study
[`10.21037/qims-2025-1-2593`](https://doi.org/10.21037/qims-2025-1-2593)
reports 756 patients and 877 aneurysms from three centres. Centre I contributes
404 patients and 450 aneurysms; the reported 314/136 development/internal
division sums to 450 aneurysm rows. External sets I and II contain 125
patients/148 aneurysms and 227 patients/279 aneurysms. The inspected public
article does not explicitly state that patients with multiple aneurysms were
kept wholly within one side of the centre-I split. This is **unresolved
within-patient dependence**, not proof of leakage.

The target is observed rupture status. In patients with subarachnoid
haemorrhage, the source uses clot adjacency or surgical confirmation to assign
the responsible aneurysm; patients without symptoms or SAH are treated as
unruptured. This is a clinically relevant diagnostic target, but it is not the
same estimand as rupture after a fixed future horizon among aneurysms known to
be unruptured at baseline.

The final feature set includes admission blood glucose. For a patient already
presenting after rupture, that measurement is downstream of the event and is
not available to a pure pre-rupture planner. The study therefore must not be
described as if every predictor were available before the rupture event. Its
reported AUCs—0.887 in training, 0.910 in internal validation, 0.773 and 0.735
in the two external centres—are source-paper results, not AURORA results.

The public article and indexed supplementary material expose no versioned
patient/image/feature/centre/split artifact. A separate data-sharing form is
linked, but no public repository URI or immutable row manifest was identified
in the inspected sources. AURORA made no data request and reproduced none of
the reported models or AUCs.

## 2. Larger or newer fusion models do not create the missing estimand

The QIMS source already compares clinical, morphological and radiomic feature
sets and seven classical machine-learning algorithms. A separate 2026 study
[`10.1155/int/1564250`](https://doi.org/10.1155/int/1564250) reports clinical
and CTA-radiomic rupture-status modelling in 443 aneurysms (101 unruptured,
342 ruptured). The previously audited seven-hospital study
[`10.1016/j.jocn.2026.111974`](https://doi.org/10.1016/j.jocn.2026.111974)
already combines clinical, morphology and radiomics with external-centre
testing, while its “unstable” label mixes prior symptoms/growth and future
events. CLEO already applies privacy/utility-oriented synthetic tabular
learning to 1,035 three-hospital rupture-status records, but those clinical
rows are not public.

Consequently, adding a transformer, GNN, deep radiomics encoder, synthetic
generator, SHAP, calibration layer or decision-curve plot is not an
independent contribution. These are controls or direct prior. The missing
object is a timestamped cohort of aneurysms known to be unruptured at baseline,
with predictors measured before time zero, follow-up censoring, treatment as a
competing/intervening event and patient-grouped centre-separated validation.

## 3. The open PLOS object is an aggregate table, not CTA payload

The PLOS study
[`10.1371/journal.pone.0319500`](https://doi.org/10.1371/journal.pone.0319500)
reports 269 patients with MCA aneurysms and 269 age-matched controls. It
studies Circle-of-Willis variation, including ipsilateral A1 dysplasia, and
reports 193 ruptured and 76 unruptured MCA aneurysm patients. This association
is already the source paper's scientific contribution.

Official Figshare article `28661913` is CC BY 4.0 and contains exactly one
5,632-byte `Table 1.xls` object (MD5
`6e188acb4759df4b14ca4cb7d5eb3477`). The article identifies it as Table 1,
an aggregate comparison of the aneurysm and control groups. It is not a
patient-row table, raw CTA collection, segmentation set, centre split or
longitudinal outcome release. Only official metadata and article text were
read; the XLS body and patient CTA were not opened.

The open CMHA release remains a useful 99-patient/105-MCA-aneurysm plus
44-control cross-sectional dataset, but its 77/28 ruptured/unruptured labels
do not add a future-event clock. Open cross-sectional rows cannot repair an
unidentified prospective estimand merely by being larger or easier to train.

## 4. Frozen non-compensatory screen

Axes are scored 0--5 in the established order: clinical importance, target
identifiability, residual novelty, asset readiness, effective independent
unit, strong-baseline feasibility, interpretable evidence and ISBI schedule
fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| External-centre rupture-status calibration decomposition | 5.0 | 4.0 | 1.5 | 1.0 | 3.0 | 5.0 | 4.5 | 3.5 | **27.5** | reject |
| MCA Circle-of-Willis occurrence transport | 4.0 | 4.0 | 0.5 | 2.0 | 4.0 | 5.0 | 4.0 | 3.5 | **27.0** | reject |
| Measurement-time-aware incremental radiomics value | 5.0 | 2.5 | 1.5 | 1.0 | 2.5 | 5.0 | 4.5 | 3.5 | **25.5** | reject |
| Pre-event-only individualized future rupture prediction | 5.0 | 1.5 | 2.5 | 1.0 | 2.5 | 5.0 | 4.5 | 3.0 | **25.0** | reject |
| Patient-grouped multi-aneurysm external validation | 4.5 | 3.0 | 1.0 | 1.0 | 2.0 | 5.0 | 4.0 | 3.5 | **24.0** | reject |
| Rupture-status synthetic-data external utility | 4.5 | 3.0 | 0.5 | 1.0 | 2.0 | 5.0 | 4.0 | 3.5 | **23.5** | reject |

The 27.5 leader has an identifiable diagnostic-status endpoint, but external
calibration and centre-shift decomposition are established evaluation tools;
residual novelty is only 1.5/5 and the source rows are unavailable. The
future-risk row reaches the 2.5 novelty floor only by asking the right
prospective question, but it fails target identifiability and asset readiness.
No total can compensate for those failures.

## 5. Re-entry contract

A future version can be rescored only if one immutable release joins:

1. a baseline timestamp at which every included aneurysm is unruptured;
2. predictor acquisition times, excluding or separately flagging post-event
   measurements;
3. future rupture/progression time, censoring and prespecified horizon;
4. treatment timing and a declared estimand for treatment as intervention or
   competing event;
5. patient, lesion, centre and split identifiers that keep all lesions from a
   patient together;
6. a public strong-baseline path for clinical, morphology and radiomics-only
   models, with calibration and centre-held-out evaluation.

Even then, admission opens only a method-free audit of event prevalence,
timing, leakage and split feasibility. Architecture selection requires an
observed failure that a minimal method can address.

## 6. Authorization boundary

This delta does not satisfy surface-vector E0 and does not alter schema 10.7's
current aSAH decision. Surface-vector remains inactive. Active lead, primary
problem, P0/P1, method, architecture, scientific-server query, PBS/GPU, outer
test, result row, C21 and claim remain zero. Historical no-verdict jobs are not
repaired or rerun.

Any future gate-authorized execution uses `introai9` PBS only and never a
login-node GPU. Never access, query, transfer to, submit to or monitor
`junjinyong`.
