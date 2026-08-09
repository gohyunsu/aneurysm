# Acquisition–flow source audit

**Frozen decision · 2026-08-10 KST:** all five candidates remain below the
unchanged **32/40** source-admission line. The strongest candidate scores
**27.5/40**. No Synapse application, challenge form, challenge data, k-space,
MAT file, 6.2 GB aneurysm archive or patient payload was accessed; no P0,
method, architecture, PBS job, GPU job or outer test was opened.

This audit asks whether the newly available CMRx4DFlow2026 source boundary can
support a defensible ISBI 2027 reconstruction problem while retaining an
aneurysm-relevant external endpoint. It deliberately separates an attractive
benchmark from a publishable, identifiable research gap.

## 1. Frozen candidate screen

Each axis is scored from 0 to 5 in the fixed order: scientific importance,
target identifiability, residual novelty after direct prior work, usable asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable-figure value and ISBI schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Nested-acceleration coherent 4D-flow reconstruction | 5.0 | 5.0 | 1.0 | 1.0 | 5.0 | 5.0 | 4.5 | 1.0 | **27.5** | reject |
| Cross-site and cross-anatomy reconstruction | 4.5 | 5.0 | 0.5 | 1.0 | 5.0 | 5.0 | 4.5 | 1.0 | **26.5** | reject |
| Explicit multi-VENC divergence-free uncertainty | 5.0 | 2.0 | 1.5 | 2.0 | 1.0 | 5.0 | 5.0 | 2.5 | **24.0** | reject |
| Functional-risk-controlled WSS/vorticity reconstruction | 5.0 | 2.0 | 2.0 | 1.0 | 5.0 | 5.0 | 5.0 | 1.0 | **26.0** | reject |
| Treated-aneurysm dual-VENC device-response transfer | 5.0 | 4.0 | 0.5 | 5.0 | 0.5 | 4.5 | 5.0 | 2.5 | **27.0** | reject |

The five scores were fixed together. Neither the 27.5 row nor the public
challenge scale is repaired upward after seeing the decision.

## 2. CMRx4DFlow2026: large and useful, but unavailable on the ISBI clock

The [official data page](https://cmrx.chihucloud.com/2026/data.html) reports
more than 400 multi-center, multi-vendor 4D-flow MRI cases. The regular split
contains 138 fully sampled training cases, 32 validation cases and 43 test
cases. Special tasks add new-site/disease and new-anatomy evaluation, including
10 cerebrovascular validation and 20 cerebrovascular test cases. Inputs include
multi-channel Cartesian k-space, coil maps, ROI masks, undersampling masks and
acquisition metadata.

These facts make the source scientifically attractive, but they do not make it
an AURORA asset. Full access requires joining the Synapse challenge and
submitting team information. More importantly, the official
[join page](https://cmrx.chihucloud.com/2026/join-the-challenge.html) permits
independent research use or reference only **after the December 2026 embargo**.
That is later than the frozen ISBI 2027 paper deadline of 2026-10-26. AURORA
does not accept these terms on behalf of the team, request access or treat
future permission as present asset readiness.

### 2.1 The obvious tasks are directly occupied

The official [task definition](https://cmrx.chihucloud.com/2026/tasks.html)
already evaluates 10×--50× high-acceleration reconstruction, A6000-bounded fast
reconstruction, unseen-site/disease generalization and transfer across anatomy.
Its metrics include magnitude nRMSE/SSIM and velocity relative/angular error.
Consequently, “one network for all masks,” a fast unrolled network or a domain
generalization block is not by itself a new problem or contribution.

The direct method lineage is also dense:

- [FlowMRI-Net](https://pmc.ncbi.nlm.nih.gov/articles/PMC12271072/) already
  combines self-supervised physics-driven unrolling, complex-valued recurrent
  reconstruction and joint velocity-encoding information, with aortic and
  cerebrovascular evaluation.
- [DAF-FlowNet](https://arxiv.org/abs/2604.00205) jointly targets velocity
  enhancement and phase unwrapping with a divergence-free parameterization.
- [VAST](https://arxiv.org/abs/2601.13393) already couples intracranial vessel
  segmentation, phase unwrapping and flow-physics consistency on synthetic,
  in-vitro and in-vivo aneurysm examples.
- Generic distributional reconstruction, arbitrary-mask uncertainty,
  data-consistency unrolling and functional-risk training are mandatory
  controls, not standalone novelty.

## 3. Why multi-VENC coherence is not identified

CMRx stores multiple velocity-encoding channels within each 4D-flow
acquisition, but the public source describes one anatomy-dependent VENC range
per scan—not repeat acquisitions of the same patient at multiple VENC settings.
Channel-wise velocity encodings are therefore not the same supervision as a
paired low-VENC/high-VENC repeat scan. A method cannot claim calibrated
cross-VENC completion or acquisition selection without such paired observations
or a trusted measurement simulator registered before training.

The open aneurysm [dual-VENC Zenodo record](https://zenodo.org/records/14981710)
does contain eight scans: four models, each measured at two VENC settings. But
all four represent one paraophthalmic aneurysm anatomy—one untreated state and
three flow-diverter variants. The associated publication already studies device
effects. Counting eight scans or four printed models as eight or four
independent anatomies would inflate the unit. This source can illustrate a
future method, but it cannot carry a headline generalization claim.

## 4. Why functional-risk reconstruction is not yet a valid endpoint

CMRx ranks against fully sampled MRI reference data. That reference supports
image and velocity reconstruction metrics; it is not automatically trusted
ground truth for near-wall gradients, wall shear stress, treatment response or
clinical decision utility. A WSS-focused loss could optimize its own derived
target without proving that the target is physically accurate. A valid version
would need an independent reference such as paired particle velocimetry or
registered CFD with uncertainty and enough independent geometries. No such
linked cohort is identified at this source boundary.

The dual-VENC aneurysm record has strong figure value but only one effective
anatomy. It cannot convert the missing reference into a population-level
validation set. Therefore a functional head, conformal interval or fancy
operator name would not repair target identifiability.

## 5. Decision boundary

- CMRx4DFlow2026 remains a post-embargo watch source, not a current AURORA
  training or evaluation asset.
- AURORA does not join Synapse, submit the challenge form, accept terms or
  download any challenge data on the user's behalf.
- Nested masks, cross-domain reconstruction, self-supervised unrolling,
  divergence-free parameterization, multi-encoding fusion, uncertainty and WSS
  losses are direct priors or controls—not independent novelty.
- The aneurysm dual-VENC source is one effective anatomy and is not promoted to
  a cohort by scan-level counting.
- Since the maximum is 27.5/40, executable P0, method, architecture, PBS/GPU and
  outer test remain unauthorized. Current AURORA GPU jobs remain zero.
- Future AURORA execution is restricted to `introai9` PBS. `junjinyong` remains
  excluded from connection, query, submission and monitoring.

The next allowed action remains a genuinely new or revised primary-source
audit. Only a fresh candidate scoring at least 32 may open a separately
preregistered, method-free CPU/PBS P0.
