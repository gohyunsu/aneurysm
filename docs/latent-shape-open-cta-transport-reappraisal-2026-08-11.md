# Latent-shape release and open-CTA transport reappraisal

> Frozen on 2026-08-11 KST · schema 9.4 · public paper, exact public Git
> repository, released aggregate latent cache and previously audited open-CTA
> metadata only · no medical mesh/image payload, scientific-server query,
> P0/P1, method, architecture or compute

## Decision

The new latent-shape release is useful methodological infrastructure, but it
does not create an active AURORA paper identity. The source paper already
learns saccular aneurysm shape spaces from five public datasets, evaluates
rupture-status discrimination, and reports the most important transport
warning itself: leave-one-dataset-out (LODO) AUC falls to 0.66 while
reconstruction error remains low. Therefore “a low-error latent model can fail
under source shift” is a direct-prior result rather than a new AURORA finding.

The tempting extension—use the fixed saccular model on the 2026 open CTA cohort
and add OOD, abstention or conformal calibration—also fails the residual-
novelty gate. Medical OOD benchmarking, generative likelihood filtering,
calibrated medical OOD detection and task-aligned abstention are established
methods. The CTA metadata supplies expert morphology categories, but an expert
`nonsaccular_type` label is not the mathematical support of a learned latent
density. Treating the two as ground-truth synonyms would make the main target
self-defined.

Six prospectively frozen formulations score
**29.5/29.0/28.5/28.0/28.0/23.0**. Every row fails the unchanged total or a
non-compensatory critical floor. No active lead, payload gate, model or PBS job
is opened. The old open-CTA physical-grid P0 and surface-vector P0 remain
execution-incomplete/no-verdict histories and are not repaired or rerun.

## 1. Exact latent-shape source boundary

The primary paper is
[The latent shape space of intracranial saccular aneurysms](https://doi.org/10.1016/j.cmpb.2026.109445).
It reports 958 patient-derived saccular aneurysm surfaces, including 338 with a
ruptured status, aggregated from five public datasets. Its PointNet AE/VAE uses
registered corresponding surfaces at approximately 700, 3,000 and 12,000
points. The paper reports 2D latent reconstruction, synthesis and retrospective
rupture-status discrimination; this is not prospective rupture-risk evidence.

The paper's own LODO experiment reports average accuracy 0.68, AUC 0.66, AE
MSE 0.16 and VAE MSE 0.14. It explicitly attributes some variation to source
composition and notes that IntrA contains smaller, less complex cases and no
ruptured cases. Thus the separation between acceptable reconstruction and
weak label transfer is already observed and interpreted by the direct source.

The official code repository is
[`PepeEulzer/aneurysm-latent-space`](https://github.com/PepeEulzer/aneurysm-latent-space)
at exact head `43e8219e947cfa318ab83a01df01c6602e7d5756`, with an MIT license.
It genuinely releases:

- uniform remeshing and morphometry scripts;
- AE/VAE definitions and training scripts;
- medium-resolution AE/VAE encoder and decoder weights, plus lower-resolution
  weights; and
- six aggregate latent caches and face matrices.

It does **not** track the processed OBJ datasets or the `rupture_labels.csv`
consumed by the training scripts. The released 3k VAE cache has SHA-256
`4ceafa78bee07a50f94b844840ba7c94b64ca3414258ec06ca431f82fded3173`
and contains 885 rows with 885 unique file identifiers. Among these, 749 have
nonblank hospital metadata, 734 have nonblank status, and 261 are marked
ruptured. This does not byte-for-byte instantiate the paper headline of
958/338. It may be a selected release view; without the missing label and mesh
manifest, AURORA does not call the discrepancy an error or reconstruct the
missing mapping.

## 2. Code-to-paper semantics are a reproducibility issue, not novelty

The default `AneurysmDataset` sorts files, shuffles them with seed 42, and uses
a file-level 80/20 split. The released `train_ae.py`, `train_vae.py` and
`train_vae_classifier.py` instantiate this default loader. A separate
`AneurysmDatasetLOO` class exists, but the repository does not expose the paper's
complete LODO driver or immutable source-fold manifest.

Both loader classes contain the Python condition
`status == "unruptured" or "other"`. Because the second operand is a nonempty
string, unknown or missing statuses reach class 0 rather than the intended
unknown class. This is a concrete code issue. It does not prove that the
published analyses used the affected path, invalidate the paper's reported
numbers, or create an algorithmic contribution. A careful reproduction should
fix and test it, but ISBI novelty cannot be obtained from a loader patch.

## 3. Open-CTA asset boundary

The independent public source is
[Zenodo 15697196](https://doi.org/10.5281/zenodo.15697196), revision 4,
`CC BY 4.0`. Its exact `Dataset.zip` is 25,578,845,008 bytes with MD5
`264ff9ee868c022d108b7c7aa7396d32`. The
[data paper](https://doi.org/10.3390/data11040074) reports 172 CTA series: 90
controls and 82 positive cases with 122 aneurysm STL annotations, including
nine rupture-positive patients.

Earlier metadata-only range discovery verified 172 cases, 122 lesion rows, 24
multi-lesion cases, 30 miliary lesions, 113 unruptured and nine ruptured lesion
rows. Its `nonsaccular_type` field contains 39 blister-like, eight fusiform,
nine eccentric-fusiform, nine fusiform-saccular and 57 missing entries. These
are source metadata categories, not audited latent-support labels.

No CTA pixel or STL payload is opened in schema 9.4. The earlier one-shot
physical-grid P0 reached only partial DICOM header prefixes and ended at an
unsupported undefined-length sequence before STL access. Its scientific gate
was unevaluated. The new latent paper does not repair that parser or authorize
a same-contract rerun.

There is also a representation mismatch that must not be hidden. The published
latent remeshing assumes an isolated saccular sac with an identifiable ostium
boundary and half-sphere topology. The CTA release describes sac-lumen STL
annotations, including nonsaccular categories, but metadata alone does not
establish an open ostium boundary, topology, orientation or successful mapping
through the released remesher. A model evaluation cannot be registered before
that target-free compatibility question is independently identified.

## 4. Direct-prior red team

The residual gap is narrower than “make the latent space safe.”

1. The latent-shape paper already reports LODO source shift, low reconstruction
   error, poorer rupture-status transfer and rare-morphology limitations.
2. [Transformer-based OOD detection for clinically safe segmentation](https://proceedings.mlr.press/v172/graham22a.html)
   already uses generative likelihood to filter unsuitable medical inputs.
3. [Know Your Space](https://proceedings.mlr.press/v227/narayanaswamy24a.html)
   directly calibrates medical OOD detectors through inlier/outlier
   construction.
4. [OpenMIBOOD](https://openaccess.thecvf.com/content/CVPR2025/html/Gutbrod_OpenMIBOOD_Open_Medical_Imaging_Benchmarks_for_Out-Of-Distribution_Detection_CVPR_2025_paper.html)
   benchmarks 24 post-hoc OOD methods over 14 medical datasets and separates
   covariate, near-OOD and far-OOD settings.
5. [Task and shift effects in medical OOD detection](https://papers.miccai.org/miccai-2025/0450-Paper3992.html)
   show that better OOD detection does not automatically yield better
   abstained downstream prediction.
6. Anatomical shape synthesis, topology-aware registration, conformal risk
   control and generic selective prediction are method families, not new
   contributions when attached to an aneurysm VAE.

The only potentially useful residual is an **application audit**: define in
advance when a fixed saccular representation should abstain on morphology-
diverse CTA and show that abstention predicts a prespecified downstream
morphometry failure rather than merely an expert category. Current metadata
and direct priors do not yet identify that target or an independent method.

## 5. Prospectively frozen six-candidate screen

Axes are clinical importance, target identifiability, residual novelty, asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission requires total >=32,
novelty >=2.5, identifiability >=3.5, and asset/unit/baseline >=3.0.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Released code--paper contract reproducibility audit | 3.5 / 4.0 / 0.5 / 4.0 / 4.0 / 5.0 / 4.5 / 4.0 | **29.5** | Reject: valuable correction, but loader/split reproducibility is not independent method novelty |
| Source-disjoint latent transport reliability | 4.0 / 4.0 / 0.5 / 3.5 / 4.0 / 5.0 / 4.5 / 3.5 | **29.0** | Reject: the paper already reports LODO reconstruction/classification separation |
| Miliary-shape support abstention | 4.5 / 3.0 / 1.5 / 3.0 / 3.5 / 5.0 / 5.0 / 3.0 | **28.5** | Reject: expert size class is not latent-support truth; OOD/abstention is direct prior |
| Support-certified saccular-model transport to open CTA | 4.0 / 3.0 / 1.5 / 3.0 / 3.5 / 5.0 / 5.0 / 3.0 | **28.0** | Reject: no prespecified downstream failure defines support; calibration wrapper is occupied |
| Nonsaccular topology-aware registration extension | 4.0 / 2.5 / 2.0 / 3.0 / 3.5 / 5.0 / 5.0 / 3.0 | **28.0** | Reject: one correspondence rule cannot identify heterogeneous nonsaccular topology; registration/shape modeling is direct prior |
| Open-CTA rupture-selective prediction | 4.5 / 1.5 / 1.0 / 3.0 / 1.0 / 5.0 / 4.5 / 2.5 | **23.0** | Reject: nine rupture-positive patients cannot identify confirmation or prospective rupture risk |

No score is repaired after viewing the batch. The 29.5 leader is not admitted
because residual novelty is 0.5/5; the highest novelty anywhere in the batch is
2.0/5, still below the 2.5 floor.

## 6. What remains useful

The released latent model remains a strong **baseline and visualization tool**
for a future problem that independently passes admission. The open CTA cohort
remains a potentially valuable **external application asset**, not a currently
authorized training or evaluation payload. A material re-entry would require:

1. an immutable mapping from the 958 paper cases to released meshes, source
   folds, rupture-status labels and the 885-row caches;
2. a method-free compatibility audit showing which CTA STL surfaces possess
   the ostium boundary and topology required by the fixed remesher;
3. a prespecified downstream failure—such as bounded morphometry error—that is
   distinct from the OOD score used to detect it;
4. patient-grouped, source-sealed calibration and confirmation units with no
   lesion- or mesh-level pseudo-replication;
5. a residual mechanism and method beyond latent density, reconstruction
   residual, ensemble uncertainty, conformal calibration or a renamed
   combination; and
6. a mechanism-linked falsifier under which the candidate is closed rather
   than repaired.

Such evidence would trigger a fresh source audit only. It would not
automatically authorize CTA/STL payload access, a P0, architecture or GPU.

No scientific server or scheduler was queried for this reappraisal. Future
gate-authorized execution remains restricted to `introai9` PBS with no
login-node GPU command. `junjinyong` remains prohibited for access, query,
transfer, submission and monitoring.
