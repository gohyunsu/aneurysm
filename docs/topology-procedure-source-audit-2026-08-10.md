# Topology–procedure source audit

**Frozen decision · 2026-08-10 KST:** a fresh five-candidate screen found no
problem at or above the unchanged **32/40** admission line. Three candidates tie
at **28.5/40**. They are rejected without large archive or model-weight access,
P0, method selection, architecture selection, PBS submission or GPU use.
AURORA still has no active primary problem, model, outer test or submission
identity.

This batch was triggered by four materially new public sources: the 2026-08-07
``tornadic phenomena'' preprint and its Figshare data/code record, a new
18-patient C-arm working-view paper, public MAXIMUS nnU-Net weights, and an MIT
rheology/slip solver release. It asks whether any leaves an identifiable ISBI
problem after its own direct contribution is removed.

## 1. Frozen candidate screen

The eight axes remain scientific importance, target identifiability, residual
novelty, asset readiness, effective independent unit, strong-baseline
feasibility, interpretable-figure value and schedule fit, each scored 0--5.

| Candidate | Importance | Identifiability | Novelty | Asset | Unit | Baseline | Figure | Schedule | Total | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Cross-modality tornadic-topology preservation | 4.5 | 2.0 | 1.0 | 3.5 | 0.5 | 4.5 | 5.0 | 3.0 | **24.0** | reject |
| Noise/resolution-stable WSS topological skeleton | 4.0 | 4.0 | 1.5 | 4.5 | 0.5 | 5.0 | 5.0 | 4.0 | **28.5** | reject |
| Set-valued C-arm working-view distribution | 4.5 | 3.0 | 2.5 | 0.5 | 0.5 | 5.0 | 5.0 | 3.0 | **24.0** | reject |
| Differential-diagnosis-aware open-set TOF detection | 4.5 | 3.0 | 1.0 | 2.5 | 4.0 | 5.0 | 5.0 | 3.5 | **28.5** | reject |
| Rheology/slip model-form hemodynamic uncertainty | 4.0 | 5.0 | 1.0 | 4.5 | 0.5 | 5.0 | 5.0 | 3.5 | **28.5** | reject |

The tie does not permit candidates to be merged, rounded or reweighted. The
scores are source-admission decisions, not model performance.

## 2. Tornadic topology: open fields, occupied identity, tiny unit

The 2026-08-07 preprint *Evidence of tornadic phenomena in cerebral aneurysms*
introduces tornado-, downburst-, roll-cloud-like and mixed near-wall flow
patterns from WSS topology. It explicitly reports that their wall imprints were
also observed in vivo with 4D-flow MRI. A topology taxonomy, WSS critical-point
detector, attractive meteorological name or interpretable surface rendering is
therefore direct prior rather than AURORA novelty.

The linked [Figshare v2 record](https://doi.org/10.6084/m9.figshare.32270130.v2)
is CC BY 4.0 and unusually reproducible. Its README reports full-cycle WSS VTP
for only three CFD cases (`S`, `Um`, `Uh`), figure velocity files for those CFD
cases, and figure velocity files for two MRI cases (`M1`, `M2`). It also lists a
10,059-byte MATLAB-code archive. The three WSS archives total 3,189,493,388
bytes; a 309,081,947-byte velocity archive contains selected files used for
figures.

This is not a same-aneurysm CFD/MRI pair contract. The README does not expose
matched CFD and MRI observations of one case, full-cycle MRI WSS, repeated
acquisitions, reader labels or a clinical endpoint. Thus cross-modality
preservation is not identified. Noise/resolution robustness can be measured by
synthetically degrading three CFD fields, but the original MATLAB detector then
defines its own target and independent anatomy remains three. That is a useful
reproducibility study, not a four-page method contribution.

Only the 2,063-byte README and source record were read. The WSS, velocity and
MATLAB archives were not downloaded or opened.

## 3. Set-valued C-arm view: meaningful ambiguity, no public unit

The 2026 paper *A generative adversarial framework for optimal view prediction
in aneurysm embolization* already maps segmented 3D vasculature and aneurysm
volumes to a unit viewing vector through differentiable ray-casting/DRR/MIP-OR
projections. It evaluates a CNN and U-Net generator with an adversarial
discriminator and expert scoring.

The paper is commendably explicit about the gap: only 18 patients remained,
not every case had an expert reference, many annotations came from a researcher,
and multiple clinically acceptable views may exist. This motivates a set-valued
or distributional target, but the audited sources provide no public 3DRA
volumes, view sets, procedural ground truth or independent reader distribution.
A probabilistic head, diffusion model or conformal wrapper cannot identify a
missing target.

## 4. MAXIMUS: a strong public baseline, not an open-set dataset

[Zenodo 17894703](https://doi.org/10.5281/zenodo.17894703) releases a
1,167,744,043-byte `Dataset615_MAXIMUS.zip` under CC BY-NC 4.0. It is a trained
nnU-Net package, not the source images. The associated multicenter paper reports
385 3D TOF-MRI images from 345 patients plus 113 ADAM subjects, four training
sets designed around aneurysm-like differential diagnoses, and primary-model
sensitivity 85%, 0.23 false positives/case, Dice 0.73 and NSD 0.84 on correctly
detected aneurysms.

Differential-diagnosis-aware training is therefore direct prior. The public
weight archive is valuable as a baseline, but it does not provide mimic labels,
patient images or a prospective open-set test. ADAM and INSTED access semantics
remain separate; a public checkpoint cannot substitute for their terms or
manufacture a new independent cohort. The model ZIP was not downloaded.

## 5. Rheology/slip release: exact interventions on one geometry

The MIT `blood-rheology-slip` v1.0.0 release is pinned to Git tag
`acda3721a511a527ebe374728874f8e69cfa7fbb`. It contains a marked 3D aneurysm
mesh named `case01`, an inlet waveform and code for Newtonian or Carreau
HCT25/45/65 rheology with no-slip or partial-slip conditions. It directly
studies how rheology and wall slip alter WSS and other flow metrics.

This is a clean paired simulator control, but the independent patient geometry
count is one. The three additional meshes are idealized aortic-root radii, not
aneurysm anatomies. A model-form uncertainty decomposition trained on parameter
sweeps would learn one solver orbit and repeat the release's scientific
question. The repository tree and README were read; no generated field result
or Zenodo ZIP was downloaded.

## 6. Decision boundary

- Tornadic labels, WSS topological skeletons, generic field denoising,
  differentiable projection, adversarial or diffusion view prediction,
  nnU-Net open-set calibration and rheology/slip parameter tokens are direct
  priors or controls, not contribution statements.
- Figshare WSS/velocity archives, MAXIMUS weights, 3DRA volumes and generated
  rheology fields were not accessed. No patient image or controlled challenge
  payload was accessed.
- No candidate reaches 32/40, so no executable P0 is registered. There is no PBS
  submission or GPU job to run or monitor.
- Any future execution remains restricted to `introai9` PBS. `junjinyong` is
  excluded from connection, query, submission and monitoring.
- A materially new source may open only a fresh score. This batch is not repaired
  by calling synthetic corruptions ``measurement shift,'' treating five case
  names as five paired patients, or using public weights as public images.

The negative decision is scientifically substantive: the newest topology and
procedure-planning ideas are already methodologically occupied, while the
released independent units do not identify the attractive residual questions.
