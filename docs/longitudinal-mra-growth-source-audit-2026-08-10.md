# Longitudinal MRA growth and measurement-control source audit

**Frozen decision · 2026-08-10 KST:** all six candidates remain below the
unchanged **32/40** source-admission line. The strongest candidate scores
**31.5/40**. No OpenNeuro annotation spreadsheet, participant table, NIfTI,
segmentation, Slicer scene or STL payload was opened or downloaded. No P0,
method, architecture, PBS job, GPU job or outer test was registered.

This audit revisits longitudinal aneurysm growth only because a materially new
2026 direct prior and the exact public file tree make a sharper question
possible: can same-session acquisition variants act as no-biological-change
controls for surveillance growth? The idea is scientifically defensible, but
the released control orbit contains only four independent patients. That is
not enough to identify a new high-capacity model or to support an ISBI headline
beyond the direct surface-registration and Bayesian growth literature.

## 1. Frozen candidate screen

Each axis is scored from 0 to 5 in the fixed order: scientific importance,
target identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Acquisition-orbit-calibrated longitudinal MRA growth detection | 5.0 | 4.0 | 2.5 | 5.0 | 1.0 | 5.0 | 5.0 | 4.0 | **31.5** | reject |
| Single-anchor weakly supervised local-growth localization | 4.5 | 2.0 | 2.0 | 5.0 | 1.5 | 5.0 | 5.0 | 4.0 | **29.0** | reject |
| Interval-censored MRA growth-trajectory forecasting | 4.5 | 3.0 | 1.5 | 5.0 | 2.0 | 5.0 | 5.0 | 4.0 | **30.0** | reject |
| Mixed-modality clinical growth-measurement harmonization | 4.5 | 3.0 | 1.0 | 1.0 | 4.0 | 5.0 | 4.0 | 4.0 | **26.5** | reject |
| AWE-conditioned long-term instability prediction | 5.0 | 4.0 | 0.5 | 1.0 | 2.0 | 5.0 | 5.0 | 4.0 | **26.5** | reject |
| Same-day post-flow-diverter multimodal disagreement modeling | 4.5 | 4.0 | 0.5 | 1.0 | 2.0 | 5.0 | 5.0 | 4.0 | **26.0** | reject |

The six scores were frozen together. The 31.5 row is not rounded, reweighted,
merged with another candidate or renamed after the unit and direct-prior audit.

## 2. What OpenNeuro ds005096 actually supplies

The official [Scientific Data article](https://doi.org/10.1038/s41597-024-03397-8)
and [OpenNeuro record](https://openneuro.org/datasets/ds005096/versions/1.0.0)
describe 63 patients with 85 aneurysms. Twenty-four patients have interval
surveillance imaging. The release is CC0 and provides all raw TOF-MRA sessions,
but expert segmentations, masks, STL models and Slicer scenes correspond to one
selected session per patient rather than every surveillance time point.

We inspected the public Git tree without materializing annex payload. The
paper-linked tag `1.0.0` is exact Git commit
`645f8579ca0dbbf62edf0275bf35f104f66a2f41`; the current tag `1.0.3` is exact
commit `0760bf865612600c4eee85f6f437aefaeb534204`. Both expose 126 raw
`*_angio.nii.gz` paths. Only four subject/session folders contain two
acquisitions in the same session:

- `sub-006/ses-20141026`;
- `sub-013/ses-20171118`;
- `sub-015/ses-20121216`;
- `sub-028/ses-20080621`.

These are valuable no-biological-change comparisons, but the independent
control unit is four patients, not eight files. The audit opened the public
tree, commit/tag metadata and `dataset_description.json` only. It did not open
the released clinical spreadsheet, participant table, acquisition sidecars,
NIfTI volumes or derivative payload.

The version delta also matters. From `1.0.0` to `1.0.3`, raw angiogram count is
unchanged, while metadata and several derivative paths/files were corrected.
Any future audit would have to pin one version and prevent a corrected
derivative from silently crossing train/test or changing a result.

## 3. Why the new 2026 prior closes the obvious growth problem

The 2026 preprint
[*Bayesian Aneurysm Growth Detection via Surface Displacement Modeling*](https://arxiv.org/abs/2604.06649)
already registers baseline and follow-up surfaces, subtracts displacement on a
non-aneurysmal vessel segment as an internal processing reference and maps the
result to a posterior probability with uncertainty bounds. For the public
OpenNeuro cohort it screened 24 longitudinal patients but retained only 16
patients with 19 aneurysms; six aneurysms met its applied 1 mm growth rule. It
reports public-cohort AUC 0.87, leave-one-out AUC 0.82 and kappa 0.51.

That work is a direct prior, not merely a baseline with a different network
name. It explicitly handles registration, surface-processing drift,
measurement error, probability calibration and the healthy-vessel reference.
Earlier work already supplies complementary controls:

- [AGED](https://pmc.ncbi.nlm.nih.gov/articles/PMC10174624/) performs rigid and
  non-rigid mesh comparison and automated morphometry for longitudinal CTA;
- the [volumetric MRA metric](https://doi.org/10.3174/ajnr.A7190) estimates a
  5.5% measurement coefficient of variation from 95 patients, 112 aneurysms and
  616 scan measurements;
- [measurement-reliability work](https://pubmed.ncbi.nlm.nih.gov/34210663/)
  shows that the smallest detectable 2D change can exceed the clinical 1 mm
  threshold;
- [CONReg](https://doi.org/10.1007/s10278-026-01878-3) makes conformal
  registration uncertainty a direct control rather than standalone novelty.

The residual acquisition-orbit idea is narrower: estimate the false-growth
distribution from same-session protocol variants, then demand separation from
between-session surveillance change. That separation is meaningful, but four
same-session patients cannot characterize protocol, scanner, anatomy and
segmentation interactions or support a fresh confirmatory outer split.

## 4. The other longitudinal sources do not rescue the unit problem

A 2026 single-center cohort reports 588 patients, 858 aneurysms and 4,289
imaging observations across CTA, MRA and DSA. Growth was taken from routine
radiology reports without a standardized size threshold; contradictory cases
were reviewed. The article provides no public image release or patient-level
learning table. Its purpose is already risk-factor and time-to-growth analysis,
so a modality token or survival Transformer would repeat the endpoint without
an executable image target.

The long-term aneurysm-wall-enhancement study includes 198 patients, 224
aneurysms and 28 instability events across two centers. Its official data
statement says the supporting data are available from the corresponding author
upon reasonable request, not as a public imaging asset. The paper already
estimates the time-varying association of AWE with instability. A deep survival
head, uncertainty wrapper or attention map is therefore neither independently
identified nor novel from the released source.

The prospective MINIFLOW preprint includes 40 patients with 43 flow-diverter-
treated aneurysms and same-day subtraction CTA, DSA and pre/post-contrast TOF
MRA. The public article directly evaluates modality agreement and exposes no
public patient imaging dataset. Its all-rights-reserved preprint license also
does not create a reusable training release. A disagreement model would need
the paired images, reader labels and a held-out patient cohort; none is public.

The 2026 PCOM virtual-angiography paper is an additional negative control. It
already evaluates CFD-derived contrast retention in 312 PCOM aneurysms,
including 23 stable and 18 unstable longitudinal cases, and directly reports
the instability/rupture associations. No public case-wise mesh, field or
virtual-angiography release was identified. Replacing its statistics with a
GNN would not create a new estimand.

## 5. Decision boundary

- The public dataset has 24 longitudinal patients, but the newest direct prior
  retained 16 patients/19 aneurysms and only six growth positives.
- Same-session acquisition variants exist for four patients. Files are not
  independent biological controls.
- Expert derivative labels cover one selected session per patient, so local
  follow-up deformation or segmentation truth is not released.
- Surface registration, healthy-vessel internal control, Bayesian measurement
  error, volumetric repeatability, morphing and conformal registration
  uncertainty are mandatory direct baselines.
- The large clinical growth, AWE, MINIFLOW and PCOM cohorts do not expose the
  public paired image/field targets needed to enlarge the independent unit.
- Since the maximum is 31.5/40, executable P0, method, architecture, PBS/GPU
  and outer test remain unauthorized. No `introai9` connection or job was
  needed for this source-only stop; current AURORA GPU jobs remain zero.
- All future AURORA execution is restricted to `introai9` PBS. `junjinyong`
  remains excluded from connection, query, submission and monitoring.

The next allowed action remains a materially new or revised primary-source
audit. Only a fresh candidate scoring at least 32 may open a separately
preregistered, method-free CPU/PBS P0.
