# Longitudinal perfusion and biomarker source audit

**Frozen decision · 2026-08-10 KST:** all six candidates remain below the
unchanged **32/40** source-admission line. The strongest candidate scores
**31.0/40**. No standalone CTP JSON, spreadsheet, NIfTI/ZIP, SAH CT archive,
3DRA/CTA CSV, VWE CSV, image, mesh or field payload was downloaded or opened;
no P0, method, architecture, PBS job, GPU job or outer test was registered.

This audit asks whether recent open longitudinal perfusion data can support a
more defensible ISBI 2027 identity than the exhausted rupture-status and CFD
branches. The answer for the current source version is no. The release is
valuable and unusually open, but repeated images do not turn 62 patients and
nine DCI events into 291 independent clinical units. More importantly, the
scan process and rescue treatment are consequences of the evolving clinical
state, so unobserved untreated trajectories and unperformed scans are not
identified by the release.

## 1. Frozen candidate screen

Each axis is scored from 0 to 5 in the fixed order: scientific importance,
target identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Informative-scan-aware continuous-time CTP field forecasting | 4.5 | 3.0 | 2.0 | 5.0 | 2.0 | 5.0 | 5.0 | 4.5 | **31.0** | reject |
| Pre-DCI event-time perfusion early warning | 5.0 | 2.5 | 1.0 | 5.0 | 1.5 | 5.0 | 5.0 | 4.0 | **29.0** | reject |
| Personalized CTP reacquisition policy | 5.0 | 1.5 | 1.5 | 4.0 | 2.0 | 5.0 | 5.0 | 4.0 | **28.0** | reject |
| Treatment-conditioned perfusion counterfactual | 5.0 | 1.0 | 1.5 | 4.0 | 1.5 | 5.0 | 5.0 | 4.0 | **27.0** | reject |
| Cross-modality 3DRA–CTA hemodynamic invariance | 4.5 | 4.5 | 0.5 | 5.0 | 0.5 | 5.0 | 4.5 | 5.0 | **29.5** | reject |
| Global–local VWE–hemodynamic discordance | 4.5 | 4.0 | 0.5 | 5.0 | 2.0 | 5.0 | 3.0 | 5.0 | **29.0** | reject |

The six scores were frozen together. The 31.0 row is not renamed, reweighted
or treated as 32 after the direct-prior and unit audit.

## 2. What the open longitudinal CTP release actually contains

The official [Dryad record](https://doi.org/10.5061/dryad.0zpc86784) is public
under CC0. Its API identifies version 7, 62 patients, 291 original CTP exams and
873 MNI-normalized parametric maps: TMax, CBF and MTT for every exam. The file
manifest contains four objects:

- `CTP_exams_dates.json`, 2,065 bytes, SHA-256
  `c83de7da3e538e5a00fb0282138f7ae6be7c2d846a8665c5dc2a9e3622d1de51`;
- `normalizedCTP.zip`, 7,854,703,571 bytes, SHA-256
  `57866aab2e816045b3d114062084d46b59845660c25613ce40869432dc51f8ff`;
- `patients_table.xlsx`, 25,098 bytes, SHA-256
  `95c0fef78d81d85eea204e5a886d7a255bc4911be89c7678fdbee0a0db092599`;
- `README.md`, 3,446 bytes, SHA-256
  `e151f8c5808ee7c842daa60570c13d612ebcd8dc4f81c3b37204f145dac6a93d`.

The official record and its embedded README state that the maps were acquired
on one GE 24-slice scanner with 5 mm source slices, processed by the vendor's
Perfusion 4D software, and warped to a 181 × 217 × 181 MNI grid at 1 mm. Dates
are delays from SAH symptom onset. These details make a bounded asset audit
plausible; they do not make the maps raw perfusion acquisitions or
multi-center ground truth.

The associated [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12325239/)
reports 42 patients with vasospasm and only nine with DCI. The 291 exams average
4.69 per patient, with a mean 2.8-day interval and a 0.6--13.1-day range. The
paper additionally creates 302 linearly interpolated exams for its group-level
analysis. Those synthetic interpolants are analysis products, not extra
patients or independent targets.

## 3. Why the observation process is part of the target

All patients received nimodipine. Clinical examination and transcranial
Doppler were used to trigger evaluation for vasospasm or DCI, and CTP-guided
milrinone was used for prevention or treatment. Therefore, three processes are
coupled:

1. the latent perfusion trajectory influences clinical deterioration;
2. deterioration influences whether and when a CTP exam is acquired;
3. the observed CTP result influences subsequent rescue treatment and hence
   the later trajectory.

A model can predict the next **observed** scan under this historical care
process. It cannot identify the map that would have existed at an unobserved
time or under a different treatment policy without additional assumptions.
Masking an observed exam supplies a reconstruction benchmark, not a randomized
counterfactual. A scan-scheduling policy also lacks a released utility for
radiation, delayed detection and rescue-treatment consequences.

This is not a minor modeling inconvenience. The ICML 2023
[TESAR-CDE framework](https://proceedings.mlr.press/v202/vanderschueren23a.html)
already formalizes informative sampling for longitudinal treatment-outcome
forecasting. Classical joint disease/observation-process models and recent
irregular medical time-series work occupy the same statistical issue. An
intensity head, missingness token or inverse-intensity weight is therefore a
mandatory control, not standalone novelty.

## 4. Image forecasting and DCI prediction are directly occupied

The primary CTP article already describes the spatial and temporal dynamics,
uses early CBF change and later pre-DCI TMax change, and reports a full-model
AUC of 0.97, optimism-corrected to 0.94. Replacing its logistic regression with
a Transformer does not create a new endpoint. The full model also uses a
post-day-4 derivative before DCI, so it must not be described as an admission
prediction model.

The broader direct-prior line is dense:

- [ImageFlowNet](https://doi.org/10.1109/ICASSP49660.2025.10890535) forecasts
  irregularly sampled medical-image trajectories with multiscale latent
  ODE/SDE flows.
- [Conditional latent diffusion for irregular longitudinal radiology](https://papers.miccai.org/miccai-2025/0164-Paper2656.html)
  already combines multi-time fusion, a temporal Transformer and future-image
  generation.
- A 242-patient [CTP machine-learning study](https://pubmed.ncbi.nlm.nih.gov/37466187/)
  already predicts DCI and functional outcome from presentation CTP and
  clinical variables.
- A 950-patient 2026 [NCCT/CTP/CTA comparison](https://doi.org/10.1186/s13244-026-02238-z)
  reports that a simpler admission NCCT model outperformed its CTP model,
  0.837 versus 0.783 AUC, while lacking external validation.

Consequently, continuous-time decoding, diffusion, a temporal Transformer,
uncertainty, DCI classification and informative-sampling adjustment are strong
baselines or components. A residual contribution would need independent
patients, a prospective prediction time, policy-independent labels and
positive evidence beyond those controls. The current release has nine DCI
events from one center and cannot supply that claim.

## 5. Two small open controls do not rescue the problem

The [3DRA–CTA Figshare record](https://doi.org/10.6084/m9.figshare.1354056.v3)
is public under CC BY 4.0, but it contains one 2,516-byte CSV with aggregate
geometry and hemodynamic variables for ten aneurysms. The associated
[2011 study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8013098/) directly reports
modality discrepancies, including 44.2% mean sac-WSS difference. No source
image, surface mesh or field is released in this record. Ten paired rows cannot
support a learned modality-invariant operator.

The [VWE–hemodynamics Dryad record](https://doi.org/10.5061/dryad.p2ngf1vrg)
is CC0 but contains only one 3,572-byte CSV for 41 unruptured aneurysms. Its
[primary paper](https://pubmed.ncbi.nlm.nih.gov/34804573/) already reports the
global and local relationships: CRstalk correlates with size and rupture
resemblance score, while local WSS–MRI intensity correlation is weak. The
public record does not expose the MRI volumes, aneurysm surfaces or spatial
maps needed to learn or independently visualize a new local–global model.

An open [SAH hemorrhage-segmentation archive](https://doi.org/10.5281/zenodo.8228847)
is also not a bridge: it belongs to different patients, the record displays no
dataset license, and its companion code/papers already target hemorrhage
segmentation and mortality. Cross-cohort pretraining is a baseline; it cannot
create paired NCCT-to-CTP or causal DCI supervision.

## 6. Decision boundary

- The 873 maps are repeated measures from 62 patients, not 873 independent
  outcome units. The nine DCI events remain the relevant endpoint count.
- Interpolated exams, masked observed scans and clinically triggered scans are
  not unobserved natural-history ground truth.
- Treatment-conditioned counterfactuals and scan-policy value are not
  identified from CTP-guided observational care.
- ImageFlowNet, longitudinal latent diffusion, TESAR-CDE, clinical/CTP DCI
  prediction and simple NCCT models are mandatory direct baselines.
- The 3DRA–CTA and VWE records release tabular summaries, not source images,
  surfaces or fields; their primary papers directly occupy the proposed
  associations.
- Since the maximum is 31.0/40, executable P0, method, architecture, PBS/GPU
  and outer test remain unauthorized. Current AURORA GPU jobs remain zero.
- Future AURORA execution is restricted to `introai9` PBS. `junjinyong` remains
  excluded from connection, query, submission and monitoring.

The next allowed action remains a materially new or revised primary-source
audit. Only a fresh candidate scoring at least 32 may open a separately
preregistered, method-free CPU/PBS P0.
