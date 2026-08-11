# Functional 4D-flow segmentation source-delta audit

> **Frozen decision · schema 8.2 · 2026-08-11 KST:** a new intracranial
> 4D-flow MRI study directly evaluates how segmentation changes flow and wall
> shear stress (WSS). That paper materially narrows the research gap, but its
> eleven clinical 7T scans are not public and its trained weights are promised
> only upon publication. The strongest fresh formulation scores **25.5/40**, far
> below the unchanged 32-point admission line. All six formulations are
> rejected. No image, mask, model weight, P0/P1, method, architecture, server
> query, PBS/GPU job, outer test, result row or paper claim is authorized.

## 1. What the new source changes

The March 2026 medRxiv study
[Automated Segmentation of Intracranial Arteries on 4D Flow MRI for
Hemodynamic Quantification](https://www.medrxiv.org/content/10.64898/2026.03.09.26347567)
pretrains a full-resolution 3D nnU-Net on 355 public COSTA TOF-MRA scans and
fine-tunes it on eleven 7T 4D-flow MRI scans. It does not stop at Dice. It
compares cross-sectional area, mean flow, velocity, mean WSS and maximum WSS
against a manual mask. Reported mean and maximum WSS agreement for nnU-Net is
1.57 ± 0.63 Pa (ICC 0.96) and 2.16 ± 1.05 Pa (ICC 0.97), with bias no larger
than 1.7%; the U-Net and DenseNet U-Net controls show approximately -5% and
+7% systematic bias.

This is direct prior for the sentence “segmentation accuracy affects
downstream WSS quantification.” Repeating that sentence with a different loss,
backbone or aneurysm label is application replication, not an independent
contribution. The paper also reports cross-resolution testing and TOF-to-
4D-flow transfer, so neither is a free novelty claim.

The result is scientifically useful but narrower than a complete aneurysm
study. The segmentation target is the Circle of Willis rather than the
aneurysm sac, a time-averaged mask is used for all cardiac phases, some
baseline masks require manual cleaning, and the clinical cohort is small.
Those limitations identify future questions; they do not by themselves supply
an executable AURORA asset or novelty.

## 2. Why the apparent sample size is misleading

The 355 COSTA volumes are TOF-MRA pretraining subjects. They are not 355
patients with paired 4D-flow velocity, WSS and manual downstream references.
The relevant functional supervision comes from eleven clinical 7T 4D-flow
scans. The paper's data-availability statement says that those clinical images
cannot be shared because of ethical and institutional privacy restrictions.
It says weights and inference configuration *will* be released on GitHub upon
publication; a future promise is neither a current checkpoint nor a material
asset.

Consequently, the independent unit for a functional claim is the clinical
patient, not a vessel segment, cardiac phase, surface vertex, analysis plane or
TOF pretraining scan. ICC values computed across repeated vessel-level
measurements are informative agreement statistics, but they do not create a
large independent aneurysm cohort for our development or confirmation.

The previously audited public dual-VENC and intervention phantoms also do not
repair this gap. They contain repeated acquisition or treatment states of one
effective anatomy (or very few physical base geometries), not a family-
disjoint clinical aneurysm cohort. They remain useful controls, not new patient
units.

## 3. Direct-prior boundary

- [VAST](https://arxiv.org/abs/2601.13393) already couples unsupervised
  intracranial 4D-flow vessel segmentation with phase unwrapping, outlier
  correction, low-rank denoising and continuity-constrained velocity
  reconstruction. A physics-consistency loss or joint segmentation/velocity
  wrapper is therefore not standalone novelty.
- [COMPASS](https://arxiv.org/abs/2509.22240), accepted at ICLR 2026, already
  gives exchangeability-based conformal intervals for downstream segmentation
  metrics and studies efficiency under covariate shift. Calling WSS the metric
  does not make generic metric certification new.
- Task-based segmentation, goal-oriented error estimation, segmentation-to-
  CFD uncertainty propagation, TOF transfer learning and generic domain or
  resolution adaptation are established controls in the AURORA lineage.
- The new medRxiv study itself supplies nnU-Net, U-Net and DenseNet U-Net
  functional baselines and directly measures segmentation-induced WSS bias.

The residual gap would need more than a named architecture. A credible new
version would require an independently usable patient-level asset and a
pre-registered failure not already reduced to Dice, generic WSS bias,
resolution shift or scalar metric coverage—for example a stable aneurysm-sac
functional endpoint whose error cannot be explained by existing task-based or
conformal controls. No such asset-target pair is presently verified.

## 4. Frozen eight-axis screen

Axes are fixed in this order: biomedical-imaging importance, target
identifiability, residual novelty after direct priors, usable asset readiness,
effective independent-unit strength, strong-baseline feasibility,
interpretable-figure value and ISBI-schedule fit.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Public-phantom-to-clinical WSS segmentation transfer | 5.0 | 3.0 | 1.5 | 3.0 | 0.5 | 5.0 | 5.0 | 2.5 | **25.5** | reject |
| Aneurysm-sac-aware 4D-flow functional segmentation | 5.0 | 3.5 | 2.0 | 0.5 | 1.0 | 5.0 | 5.0 | 2.5 | **24.5** | reject |
| Patient-level selective WSS-error certificate | 5.0 | 4.0 | 1.0 | 0.5 | 1.0 | 5.0 | 5.0 | 2.0 | **23.5** | reject |
| Segmentation-induced hemodynamic ranking reversal | 5.0 | 4.0 | 1.0 | 0.5 | 1.0 | 5.0 | 5.0 | 2.0 | **23.5** | reject |
| Resolution-shift functional segmentation | 4.5 | 4.5 | 0.5 | 0.5 | 1.0 | 5.0 | 5.0 | 2.5 | **23.5** | reject |
| TOF-pretrained 4D-flow anatomy transfer | 4.5 | 5.0 | 0.0 | 0.5 | 1.0 | 5.0 | 5.0 | 2.0 | **23.0** | reject |

The highest score is not promoted or rounded. Its public side has effectively
one physical anatomy, while its clinical side is unavailable; it therefore
cannot identify or confirm a phantom-to-patient effect. The aneurysm-sac
variant has slightly more residual scientific room, but no public paired
aneurysm-sac mask, velocity field and WSS reference. Strong baselines and
figures would be easy only after acquiring the missing target; those strengths
cannot compensate for missing units and assets.

## 5. Consequence for the surface-vector proposal

This audit does not kill the inactive structure-faithful surface-vector
hypothesis, and it does not validate it. It reinforces the earlier
adjudication: architecture-first work is premature. The first defensible
surface question remains patient-level, method-free stability of a precisely
defined estimand—signed total degree with boundary margin and abstention before
exact critical-point/worldline claims. Edge 1-forms, Hodge/DEC, equivariance,
periodic decoding and topology losses remain candidate controls, not novelty.

Jobs `115645.ECE-util1` and `115684.ECE-util1` remain immutable
execution-incomplete/no-scientific-verdict histories. Their registered checks
were unevaluated, not failed; neither job is repaired, rerun or reinterpreted.
No new source in this batch is a material E0 change for the phase-resolved
surface-WSS task.

## 6. Operational boundary

- Active source lead, shortlist, primary problem, method, architecture, P0/P1,
  GPU, outer test, result row and submission identity remain zero.
- A promised model release can trigger a fresh baseline-availability audit;
  it does not automatically authorize download, score repair or training.
- A new executable version requires a public or explicitly authorized
  patient-level 4D-flow asset with aneurysm target, velocity/WSS semantics,
  split keys and an independently novel estimand.
- This audit queried no scientific server and created no PBS/GPU job. Any
  future gate-authorized computation uses `introai9` PBS only. `junjinyong`
  remains prohibited for connection, query, transfer, submission and
  monitoring; login-node GPU commands remain prohibited.
