# RSNA release-layer and WEB-GAN utility delta

> Frozen on 2026-08-12 · schema 10.7 scientific-state delta · official/public
> sources and static code only · no controlled RSNA payload, original WEB
> patient table, scientific server, P0/P1, model, PBS or GPU

## Decision

This delta does **not** replace the current aSAH problem-level screen and does
not open an active paper identity. It resolves two tempting but invalid
shortcuts.

1. The RSNA figures `>6,500`, `>4,000` and `4,348` are not interchangeable.
   They come from different source layers and do not establish a new public
   release or an executable external split.
2. WEB-GAN exposes a clinically meaningful six-month occlusion target and
   public code, but the inspected notebook does not identify unseen-patient
   synthetic-to-real utility. The generator is trained on the complete original
   table and the downstream synthetic-trained model is evaluated on that same
   original table. The original 78-case table is request-only, so AURORA cannot
   reconstruct a donor-disjoint or institution-held-out evaluation.

The second observation is an evaluation-contract limitation, not a claim that
the source paper is invalid. It also does not create sufficient novelty:
training a generator inside each development fold and evaluating once on an
untouched real patient/centre split is established synthetic-data hygiene.

The result remains **no active lead, no selected architecture and no compute**.
The current architecture is still `none`, not GNN. Surface-vector remains an
inactive conditional hypothesis, and closed job `115645.ECE-util1` remains
execution-incomplete/0-of-10 without repair or rerun.

## RSNA: three numbers, three claims

The official July 2025 RSNA launch release describes the challenge reference
corpus as more than 6,500 imaging studies, more than 3,500 annotated aneurysms,
18 institutions and more than 60 expert radiologists. It explicitly spans CTA,
MRA, post-contrast T1 and T2-weighted MRI. A subset of MRI studies has 3D
segmentations of 13 vascular territories.

The current AWS Open Data Registry page instead describes a controlled-access
collection of more than 4,000 CT brain scans, more than 40 radiologists, 18
institutions and about 200 studies with AI-generated segmentations. It prohibits
redistribution and still points to a forthcoming Data Resource Publication.

Finally, `4,348` is the number of training series reported by the public
second-place method, not an official declaration that all 6,500 challenge
studies or every AWS object are its training set. No inspected official source
provides a machine-readable identity map that proves one of the following:

- `6,500 = public train + hidden test`;
- the `>4,000` registry collection is exactly the competition training set;
- all three counts use the same study/series/examination unit; or
- the MRI segmentation subset and the approximately 200 AI-segmented studies
  are the same cases or the same annotation object.

Therefore AURORA records the layers separately and infers no arithmetic split.
No RSNA terms were accepted; no MIRA request, S3 listing, CSV, DICOM or mask was
opened.

Primary sources:

- [RSNA challenge launch release](https://www.rsna.org/media/press/i/2596)
- [RSNA-ICA AWS Open Data Registry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)
- [Official RSNA dataset wiki](https://github.com/RSNA/AI-Challenge-Data/wiki/RSNA-Intracranial-Aneurysm-Detection-Dataset)
- [Second-place multi-task method](https://arxiv.org/abs/2606.26706)

## WEB-GAN: what is public and what the code evaluates

The source article reports 78 clinical/procedural/morphometric WEB cases from
three institutions, a conditional GAN that generates 1,000 synthetic rows and
RF/XGBoost prediction of six-month occlusion grade. Its reported class AUC
range `0.62–0.91` and mean `0.78` are source results, not AURORA results. The
article makes the original data available only on request and links public code
and synthetic data.

The exact public repository head inspected here is
`42ce2a8c795b32e03163be3a9a324eba9a0a76e5` (2025-10-10). It has zero GitHub
releases, no tracked `LICENSE` file and no GitHub-recognized license; its README
states MIT. The repository contains a 109,364-byte synthetic CSV, but no
original `WEB_TARGET.csv`. The synthetic CSV body was not inspected.

Static notebook lineage is decisive:

1. `WEB_GAN copy.ipynb` loads `WEB_TARGET.csv` into `df`, selects the modelling
   columns, scales that complete table and assigns `X = data.values`.
2. The cGAN is trained for 5,000 epochs from rows sampled from that complete
   `X`. It then generates 1,000 rows while repeating binary conditions derived
   from the same `X`.
3. `multiclass_classification.ipynb` loads the public synthetic CSV and the
   unavailable original table. For the synthetic-trained experiment it sets
   `X = synthetic_df[features]` and `X_test = original_df[features]`, tunes on
   synthetic data, fits on all synthetic rows and predicts on all original
   rows.

Thus the real evaluation rows were already donors to the generator that made
the training rows. This is not a held-out real-patient test, even though the
predictor never directly fits `X_test`. The proper unit is the original patient
or procedure donor, not one of the 1,000 generated rows. Without the 78-case
table and patient/institution identifiers, neither nested patient splits nor
leave-one-institution-out validation can be executed.

Primary sources:

- [WEB-GAN article](https://journals.sagepub.com/doi/10.1177/2997979X251369456)
- [Exact public WEB-GAN repository](https://github.com/shrinitbabel/WEB-GAN-occlusion-prediction)
- [NeurIPS synthetic-tabular benchmark using held-out real tests](https://proceedings.neurips.cc/paper_files/paper/2023/file/6aa9a05b929fb08ff46a58cab6cf860d-Paper-Datasets_and_Benchmarks.pdf)
- [Synthetic Data, Real Errors](https://proceedings.mlr.press/v202/van-breugel23a.html)
- [Medical image generation evaluated on real test data](https://www.nature.com/articles/s41746-021-00507-3)

## Prospectively frozen candidate screen

Axes are clinical importance, target identifiability, residual novelty, asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit. Admission needs total at least
32 and every critical floor: target 3.5, novelty 2.5, asset 3.0, unit 3.0 and
baseline 3.0. A high total cannot compensate for a failed floor.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| RSNA release-layer-aware multimodal transport | 5.0 / 3.5 / 0.5 / 2.0 / 5.0 / 5.0 / 4.5 / 3.5 | 29.0 | Reject: controlled contract and challenge systems already occupy the task |
| RSNA modality/site selective risk | 5.0 / 3.0 / 1.0 / 2.0 / 5.0 / 5.0 / 4.5 / 3.0 | 28.5 | Reject: subgroup manifest absent; selective calibration is direct prior |
| Donor-disjoint WEB synthetic utility | 4.5 / 4.0 / 1.0 / 1.0 / 2.0 / 5.0 / 4.5 / 4.0 | 26.0 | Reject: original donor table unavailable and split hygiene is not novelty |
| Leave-one-institution-out WEB outcome transport | 4.5 / 4.0 / 1.5 / 1.0 / 2.0 / 4.5 / 4.5 / 3.5 | 25.5 | Reject: institution IDs/sizes and clean test rows unavailable |
| Leakage-aware synthetic-utility identified set | 4.0 / 3.0 / 1.5 / 1.0 / 2.0 / 5.0 / 4.5 / 3.5 | 24.5 | Reject: no unseen real observations identify a utility bound |
| Released-synthetic-only WEB reproducibility | 4.0 / 2.0 / 0.5 / 4.0 / 1.0 / 5.0 / 3.5 / 3.0 | 23.0 | Reject: generated rows are not independent clinical units or real validation |

All six candidates fail. Batch-best residual novelty is 1.5/5, and no row has
the assets needed for its claimed estimand. These scores are a fresh rejected
delta and do not overwrite the schema-10.7 aSAH current batch.

## Material re-entry contract

A WEB outcome candidate may be rescored only after a versioned, lawfully
usable release or an explicit team-provided contract supplies:

1. original patient/procedure IDs and institution IDs;
2. fixed six-month outcome definition and missing-follow-up handling;
3. a patient- and centre-disjoint outer test untouched by generator selection,
   preprocessing, tuning and predictor fitting;
4. generator training nested entirely inside each development fold;
5. real-only, oversampling, regularized linear/tree and synthetic-augmentation
   controls with paired uncertainty; and
6. a mechanism-linked claim beyond generic augmentation, fidelity, privacy or
   leakage-safe evaluation.

An RSNA candidate similarly requires the official versioned publication,
study/series/patient mapping, exact modality/site splits, annotation lineage
and lawful access. A source change requests manual re-audit only. It does not
accept terms, fetch payload, register P0, select architecture or authorize GPU.

All future execution remains `introai9` PBS-only after an explicit gate.
Login-node GPU commands are prohibited. `junjinyong` remains excluded from
access, query, transfer, submission and monitoring.
