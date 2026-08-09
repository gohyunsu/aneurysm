# Treatment–surveillance source audit

**Frozen decision · 2026-08-10 KST:** all five candidates remain below the
unchanged **32/40** source-admission line. The strongest candidate scores
**30.0/40**. No spreadsheet, presentation, restricted MRA, patient image or
other payload was accessed; no P0, method, architecture, PBS job, GPU job or
outer test was opened.

This audit asks whether two newly inspected follow-up sources support an
identifiable treatment or surveillance problem that is not already occupied by
outcome prediction, propensity comparison or accelerated-MRA agreement work.
It does not revive the closed post-treatment segmentation, flow-diverter
counterfactual-selection or longitudinal-growth candidates.

## 1. Frozen candidate screen

Each axis is scored from 0 to 5 in the fixed order: scientific importance,
target identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Observed interval-censored post-FD occlusion forecasting | 5.0 | 3.5 | 1.0 | 4.5 | 4.0 | 5.0 | 3.0 | 4.0 | **30.0** | reject |
| Causal Pipeline-versus-Surpass device selection | 5.0 | 1.5 | 0.5 | 4.5 | 3.5 | 5.0 | 2.5 | 3.5 | **26.0** | reject |
| Early-complication versus delayed-occlusion utility prediction | 5.0 | 2.5 | 1.0 | 4.5 | 4.0 | 5.0 | 3.0 | 4.0 | **29.0** | reject |
| Recurrent-procedure patient-history sequence modeling | 4.5 | 2.5 | 1.5 | 4.5 | 1.5 | 5.0 | 3.0 | 3.5 | **26.0** | reject |
| Fast-versus-standard TOF-MRA remnant decision equivalence | 4.5 | 4.5 | 0.5 | 0.5 | 1.0 | 5.0 | 4.5 | 2.5 | **23.0** | reject |

The five scores were fixed together. The 30.0 row is not merged with another
endpoint, rounded upward or renamed as a method contribution.

## 2. Public flow-diverter table: useful outcomes, occupied questions

The [Data in Brief source](https://pmc.ncbi.nlm.nih.gov/articles/PMC9163419/)
and [Mendeley record](https://data.mendeley.com/datasets/nzzx92ky6r/2) describe
141 flow-diversion procedures in 126 subjects from two centers. The public
record lists a CC BY 4.0 spreadsheet, an R propensity-matching script and a
presentation containing selected cavernous-ICA DSA images. Tabular fields
include demographics, comorbidities, aneurysm morphology, device and procedure
features, complications, months to first and second DSA follow-up, and binary
complete-occlusion observations.

The difference between 141 procedures and 126 subjects matters. Procedures are
not independent patients, and the repeated subset is too small to justify a
sequence architecture. Device was chosen in retrospective practice rather than
randomized. Follow-up DSA occurs at irregular times, so the exact biological
occlusion time lies between observations; treating the recorded month as an
exact event time would manufacture precision.

No dataset payload was needed to establish these source-level constraints. The
spreadsheet, R document, presentation and image members remain unread.

### 2.1 Observed interval-censored occlusion forecasting · 30.0/40

A prospective estimand could be the probability that complete occlusion is
observed by a fixed follow-up horizon, with interval censoring represented
explicitly and all splits grouped by patient. This is identifiable only for the
recorded clinical follow-up process. It is not the counterfactual time to
occlusion under a different device or surveillance schedule.

Residual novelty is insufficient. The companion
[Pipeline-versus-Surpass study](https://doi.org/10.1016/j.wneu.2022.02.025)
already compares angiographic outcomes with propensity matching. Earlier work
already predicts six-month flow-diverter outcome from morphology, virtual
stenting and CFD using machine learning
([Paliwal et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6421840/)). A 2021
study explicitly models
[time to occlusion](https://pmc.ncbi.nlm.nih.gov/articles/PMC8757794/), and a
2025 multicenter study combines morphology, CFD, classical ML and SHAP for
[post-flow-diverter occlusion prediction](https://pubmed.ncbi.nlm.nih.gov/40237244/).
Interval-censored survival, calibration or a Transformer over two visits would
be sound controls, not an independent algorithmic gap.

### 2.2 Causal device selection · 26.0/40

Pipeline and Surpass are not exchangeable treatments in this retrospective
sample. The source paper reports 96 Pipeline and 45 Surpass procedures, and
device choice can co-vary with center, calendar time, aneurysm anatomy and
operator judgment. Measured-covariate propensity adjustment cannot identify
individual treatment effects without exchangeability, positivity and stable
treatment assumptions that the public record does not establish. The companion
paper already performs the direct device comparison. A treatment-effect network
would therefore add architecture without recovering the missing counterfactual.

### 2.3 Benefit–harm utility · 29.0/40

Jointly considering peri-procedural complications and later occlusion is
clinically sensible. The public table includes both outcome families, but severe
complications are rare and heterogeneous, follow-up is irregular, and patient
preferences or explicit utility weights are absent. A weighted multi-task loss
would choose the trade-off rather than identify it. Competing-risk, net-benefit
and decision-curve analyses are required baselines, not novelty by themselves.
The 29.0 score reflects a useful secondary analysis that is too small and too
confounded to carry the paper identity.

### 2.4 Recurrent-procedure histories · 26.0/40

Only 15 more procedures than subjects are reported. Some cases represent
retreatment after coiling or a prior flow diverter, but the source boundary does
not establish a large repeated trajectory per patient. Treating 141 rows as 141
independent cases would leak patient history; grouping by patient leaves a very
small recurrent subset. A temporal graph or patient-history Transformer is not
supported by the effective unit.

## 3. Paired fast-versus-standard follow-up MRA · 23.0/40

The [paired TOF-MRA study](https://pmc.ncbi.nlm.nih.gov/articles/PMC9227072/)
includes 22 patients, each scanned with compressed-sensing and parallel-imaging
TOF-MRA in the same examination. Four readers scored modified Raymond–Roy
occlusion and vessel depiction. The study reports inter-modality agreement of
0.98 while using the standard parallel-imaging sequence—not DSA—as the occlusion
reference. It already answers the direct sequence-equivalence question.

The linked [Zenodo record](https://zenodo.org/records/6654502) is published but
restricted and exposes no public file list through the record API. AURORA does
not request access, accept terms or infer that raw DICOM, k-space or reader-level
labels are available. Twenty-two paired patients are also inadequate for a new
reconstruction or decision-preservation model. Generic accelerated MRI,
paired-consistency learning and morphology-preserving losses are direct priors.

## 4. Decision boundary

- The public flow-diverter table is catalogued as a source-rejected treatment
  control, not a selected training cohort.
- Observed follow-up prediction must not be described as causal device
  selection or exact biological time to occlusion.
- Interval-censored survival, propensity methods, competing-risk modeling,
  utility weighting, patient-history Transformers, accelerated MRI and paired
  consistency are baselines or engineering choices, not headline novelty.
- No Mendeley spreadsheet, R document, presentation, DSA image, restricted
  Zenodo file, MRA image or patient payload was accessed.
- Since the maximum is 30.0/40, executable P0, method, architecture, PBS/GPU and
  outer test all remain unauthorized. Current AURORA GPU jobs remain zero.
- Future AURORA execution is restricted to `introai9` PBS. `junjinyong` remains
  excluded from connection, query, submission and monitoring.

The next allowed action remains a materially new source-level problem audit.
Only a fresh candidate scoring at least 32 may open a separately preregistered,
method-free CPU/PBS P0.
