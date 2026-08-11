# MRIS-Bench target-contract audit

**Frozen on:** 2026-08-11  
**State:** all six formulations rejected · no active problem, P0/P1, method,
architecture, server query or GPU job  
**Purpose:** test whether a large, fashionable vision-language source supplies
the target lineage and independent units required for an ISBI paper, instead of
letting row count or model style substitute for a scientific estimand.

## Decision

MRIS-Bench is not an admissible AURORA task in its current revision. Its public
Hugging Face page reports 30,110 rows and calls the source a benchmark for
Medical Referring Image Segmentation, but the same card says that the full
dataset, code and detailed metadata will be released only after double-blind
review. The repository currently exposes eight Arrow shards while omitting the
source-dataset lineage, patient grouping, split, annotator or generator
protocol, mask semantics and paper citation needed to interpret those rows.

More importantly, the machine schema contains `id`, free-text `problem`,
string-valued `solution`, image and image dimensions; it contains no mask field.
The public viewer renders `solution` as a 2D bounding box and point. A referring
segmentation paper cannot treat that contract as a pixel mask without an
unreleased conversion or annotation process. The best of six prospectively
frozen formulations scores **24.0/40** and fails the identifiability, residual
novelty, asset and independent-unit floors. No payload, P0, method or compute is
opened.

## 1. Exact public state

The canonical API resolves the older `lixiang007666/MRIS-Bench` path to
[`lixiangcog/MRIS-Bench`](https://huggingface.co/datasets/lixiangcog/MRIS-Bench)
at exact revision `6f2d6d9ad10eba68700ce95c7523ec78934f7a3d`, last modified
2026-05-15. It is public, non-gated and tagged `license:mit`.

- The API lists twelve files: `.gitattributes`, a 629-byte README, eight Arrow
  shards, `dataset_info.json` and `state.json`.
- The eight Arrow shards total 3,728,270,168 bytes. They were not downloaded or
  range-read.
- The page reports 30,110 rows, but a row is not an independent patient,
  examination or lesion.
- `state.json` has `_split: null`; no train/validation/test contract is exposed.
- `dataset_info.json` leaves citation, description, homepage and license empty,
  despite the top-level card's MIT tag.
- The README repeats only the under-review release statement. It supplies no
  upstream image license, clinical source, de-identification statement,
  inclusion criteria, annotation protocol or patient-level key.

The repository's public API reports 7,449,574,455 storage bytes, whereas the
eight Arrow file sizes sum to 3.73 GB. This storage accounting difference is not
interpreted as extra cases, duplicate patients or an additional split.

## 2. Visible contradictions are a warning, not a measured corruption rate

The default public viewer exposes examples in which a text states that no
aneurysm is present while a positive box and point are attached. Another visible
description assigns Hounsfield units to a TOF-MRA image. Other examples mention
DSA scores, rupture, thrombosis or arteriovenous malformation without any public
source field establishing that those attributes were observed.

These examples justify a fail-closed target audit; they do **not** establish a
dataset-wide error prevalence. No registered random sample was drawn, no image
was downloaded, and no clinical adjudication was performed. We therefore do not
call the source corrupted or use the visible inconsistencies as paper results.
They show only that the current card cannot support an assumption that free text,
box/point and image are mutually valid ground truth.

## 3. Direct-prior boundary

The attractive model ideas are already occupied or must be controls.

- [VividMed](https://aclanthology.org/2025.naacl-long.89/) already supports
  instance boxes, semantic masks, 2D/3D medical data, VQA and report generation.
- [NTP-MRISeg](https://doi.org/10.1109/TMI.2026.3705770) directly formulates
  medical referring segmentation as next-token mask prediction.
- [Semi-MedRef](https://arxiv.org/abs/2605.15720) directly treats
  augmentation-induced image-text misalignment in semi-supervised MRIS.
- [MedRIS](https://doi.org/10.1007/978-3-032-09513-8_36) already addresses
  multi-lesion reference and annotation uncertainty.
- [OmniCT](https://openreview.net/forum?id=nrZI64gTvC) directly targets the
  slice-versus-volume and cross-slice consistency gap in medical LVLMs.

Consequently, adding a VLM, SAM, cross-attention, language consistency loss,
uncertainty head or abstention wrapper is not residual novelty. Before a model
could be proposed, a stable release would have to establish the observable
target and show a failure not already explained by label-generation error or
missing patient grouping.

## 4. Frozen six-candidate screen

Axis order is clinical importance, target identifiability, residual novelty,
asset readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Modality-semantic contradiction detection with selective abstention | 4.0 / **2.0** / **1.5** / **2.5** / **1.0** / 4.5 / 4.5 / 4.0 | **24.0** | Reject: the visible contradiction has no adjudicated reference or patient grouping; grounded/selective VLM evaluation is direct prior |
| Evidence-grounded aneurysm referring segmentation | 4.0 / **1.5** / **1.0** / **2.5** / **1.0** / 5.0 / 4.5 / 4.0 | 23.5 | Reject: the released schema has box/point strings rather than a mask target |
| Dataset-contract and provenance benchmark | 4.0 / **2.5** / **1.5** / **2.5** / **1.0** / 3.5 / 3.5 / 4.5 | 23.0 | Reject: source lineage and adjudication needed to define the benchmark are the missing objects |
| Patient-grouped cross-slice statement consistency | 4.0 / **1.0** / **1.5** / **2.5** / **1.0** / 4.0 / 5.0 / 3.5 | 22.5 | Reject: filename recurrence cannot substitute for a patient/session manifest |
| Label-noise-robust MRIS training | 3.5 / **1.5** / **0.5** / **2.5** / **1.0** / 5.0 / 4.0 / 4.0 | 22.0 | Reject: robust training cannot identify which text, point, box or image is correct |
| Two-dimensional descriptions to three-dimensional lesion consistency | 4.0 / **1.0** / **1.0** / **2.0** / **1.0** / 4.0 / 5.0 / 3.0 | 21.0 | Reject: slice order, spacing, volume membership and 3D reference are absent |

Every row fails several non-compensatory minima. No score is repaired by
calling 30,110 rows independent samples, inferring patient IDs from filenames,
or choosing an architecture after seeing the ordering.

## 5. Relation to the surface-vector analysis

This audit strengthens, rather than weakens, the supplied surface-vector
judgment. A superficially executable and fashionable pivot is not preferable
when its target contract is less identifiable. Surface-vector remains an
inactive falsifiable question; MRIS-Bench does not replace it as the active
paper identity. In both cases, the next step is a material source change and a
new method-free gate, not architecture development.

The surface-vector endpoint hierarchy is unchanged: boundary-margin signed
total degree and abstention precede exact critical points and worldlines, and a
structural loss remains prohibited before a field-error-matched failure is
observed. Job `115645.ECE-util1` remains closed at E/exit 2 with 0/10 checks
evaluated and no scientific verdict; it is not repaired or rerun.

## 6. Execution and watch boundary

No scientific server was queried. No Arrow shard, image, model, checkpoint or
medical archive was downloaded. No P0/P1, method, architecture, PBS/GPU job,
outer test, result row or manuscript claim was created.

The exact under-review Hugging Face state is added to a fail-closed source
watch. A revision, detailed card, citation, split or file-inventory change can
request only a fresh source/target audit. It cannot accept terms, download data,
repair a score, register P0, select a model or authorize compute.

Any future eligible execution remains `introai9` PBS only; login-node GPU
commands are prohibited. `junjinyong` must never be accessed, queried,
transferred to, submitted to or monitored.
