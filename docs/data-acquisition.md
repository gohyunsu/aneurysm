# Dataset acquisition plan

> **Schema 10.5 acquisition boundary · 2026-08-12:** Do not contact authors,
> accept challenge terms, download patient images or infer culprit/mimic labels
> for this rejected batch. A material source must first expose lawful access,
> patient and lesion identifiers, aligned modalities, adjudication provenance,
> ambiguity rules, centre and sealed patient-grouped splits. Only then may a
> prospectively registered method-free P0 inspect bounded metadata and file
> integrity.

> **Schema 10.4 acquisition boundary · 2026-08-12:** Do not accept TopBrain
> 2025 custom download terms or open its 1,958,849,592-byte patient archive,
> exact podium Dockers, controlled RSNA data or Kaggle weights. Fifty public
> volumes are 25 paired patients and the labels are vessel anatomy, not an
> admitted aneurysm target. Source-watch v12 is metadata-only; change signals
> request review and never authorize acquisition. Re-entry requires a fresh
> lawful aneurysm-specific target/reference contract that independently passes
> the non-compensatory gate.

> **Schema 9.2 acquisition boundary · 2026-08-11:** Do not request RSNA MIRA
> access or accept terms for the rejected reference-provenance batch. Public
> registry/wiki changes are monitored read-only by source-watch v11. A change
> opens only a fresh source audit; actual access still requires an admitted
> candidate, verified terms, a machine-auditable manifest and independent-unit
> semantics. [Exact reappraisal](reference-provenance-and-rsna-release-contract-reappraisal-2026-08-11.md)

> **Schema 9.1 decision · 2026-08-11:** Surface-vector remains an inactive
> evaluation question; job `115645` is still execution-incomplete with 0/10
> checks and is not repaired. TopAneu's official Git history now verifies a
> 98-case → 417-scan annotation version orbit, but this does not clear novelty.
> The evaluator-unit candidate scores 32.0 with novelty 0.5/5, while the
> revision-aware formulation scores 31.5 with novelty 2.0/5, below the frozen
> 2.5 floor. Terms, individual labels, medical payload, P0/P1, model, server
> query and GPU remain closed. See
> [the exact adjudication](surface-vector-and-topaneu-version-orbit-adjudication-2026-08-11.md).

> **Schema 9.0 acquisition boundary · 2026-08-11:** The new AAA audit used
> public metadata and README text only. Do not download Zenodo ZIPs,
> `aaa_data.xlsx`, example OpenFOAM cases, GEO matrices, CFD fields or images;
> no candidate passed the source gate. A future acquisition must be a new,
> versioned same-patient imaging--field--molecular contract or a real paired
> AAA CFD reference and must first receive a prospectively frozen method-free
> P0. Routine source version changes do not authorize acquisition.

> **Schema 6.9 acquisition outcome · 2026-08-10:** The single authorized
> metadata read ended execution-incomplete and retained no registered source
> object. Do not repeat the HTTP read, download NIfTI/image/mask or clinical
> payload, inspect checkpoints, or open P1. Any new acquisition contract must
> belong to a different prospectively admitted problem and execute through
> `introai9` PBS only. `junjinyong` remains prohibited.

> **Schema 6.8 acquisition boundary · 2026-08-10:** The only authorized read is
> five small/public OpenNeuro/code metadata objects in one `introai9` CPU/PBS
> P0: recursive Git tree JSON, dataset description, two supervision-list blobs
> parsed without unpickling, and the code license. Do not read or download NIfTI
> image/mask bodies, participant/clinical tables, pretrained models, checkpoints
> or outer-test material. P0 pass is not acquisition permission; it opens only
> registration of a separate method-free P1. `junjinyong` remains prohibited.

> **Schema 6.6 acquisition outcome · 2026-08-10:** The one authorized Aneumo
> selective-read P0 ended before an aggregate result. No persistent field cache,
> completed/partial source payload or model artifact was retained. Do not repeat
> the read, download the full archive or open P1. Fresh acquisition requires a
> different prospectively admitted problem and remains `introai9`-only;
> `junjinyong` is prohibited.

> **Schema 6.5 acquisition override · 2026-08-10:** The only newly authorized
> read is the one-shot Aneumo P0's selective ZIP64 range access: train family 1,
> cases 1–2, eight flows, 16 members. Do not download a full archive, persist a
> field cache, inspect pressure or access validation/test data. Run only inside
> an `introai9` PBS CPU allocation. `junjinyong` is prohibited for connection,
> query, transfer, submission and monitoring. P0 pass is not permission to
> acquire more data; it permits registration of a separate train-only P1 only.

> **2026-08-10 schema 6.4 override:** Do not acquire TopAneu for the rejected
> factorized/silver-anatomy formulation. The official-code red team leaves no
> active source lead or P0, and terms acceptance alone cannot reopen it. Only a
> different prospectively admitted problem may define a new acquisition
> contract. Any authorized execution remains `introai9` PBS only; never use
> `junjinyong`.

> **2026-08-10 TopAneu release boundary:** Public challenge prose, source code,
> path/checksum manifests and download-share metadata are audited, but medical
> files and location-JSON content remain unread. The user must personally review
> and explicitly accept the TopAneu data-use terms before any acquisition.
> Acceptance would authorize only registration of the bounded CPU/read-only
> P0-R in `docs/topaneu-release-evaluation-audit-2026-08-10.md`; it is not
> permission to train, use the sealed test, or create a GPU job. Any authorized
> server operation is `introai9` PBS only, never `junjinyong`.

> **Current override · 2026-08-09:** AneuX preprocessing-orbit P0는 exact public
> commit 뒤 `introai9` CPU/PBS에서 한 번 실행됐지만 initial tabular transport
> attempt를 소진해 complete/partial archive와 CSV parse 없이 종료됐다. Model
> HEAD/range·central directory·member payload는 0이고 13개 gate는 미평가다.
> Same-source repair/rerun, full download, P1과 model/GPU를 열지 않는다. Active
> source shortlist는 0이며 아래 complete-corpus 계획과 “first executable
> milestone”은 historical storage planning이지 현재 실행 권한이 아니다.

## Storage decision

Do not place the complete raw corpus in this repository or in the current local workspace. At the time this plan was written, the local volume had only 32 GB free. The full corpus needs substantially more after extraction.

Recommended locations:

- `repo/`: code, manifests, schemas, small metadata, and documentation only.
- `dataset_root/`: a mounted NAS or external volume for immutable raw data and derived artifacts.
- `scratch_root/`: temporary extraction, conversion, and training data; safe to remove after a verified run.

## What to download

| Priority | Dataset | Download | Published compressed size | Why |
|---|---|---|---:|---|
| P0 | BenchAnXplore | `coarse_03_dataset.zip` | 1.12 GB (1,123,362,206 bytes) | Required to reproduce In-PI-MGN. |
| Closed P0 | AneuX | `data-v1.0.zip` transport attempted; no completed/partial file retained | 13 MB | Historical execution-incomplete asset audit; no rerun. |
| Closed P0 metadata-only | AneuX | model HEAD/range was not reached | 6.3 GB remote object | No central-directory/member access; no P1/model authorization. |
| P1 | CMHA / Gong 2024 | `patients.rar` + `statistical results.rar` | 9.99 GB + 34 KB | Patient CTA, STL, and real hemodynamic summaries. |
| P2 | CMHA / Gong 2024 | `controls.rar` | 4.49 GB | Only needed for case-control imaging studies. |
| P2 | AneuriskData | Git repository mirror | ~1.36 GiB repository size | Useful for source-native geometry/centerline/image assets; partly overlaps AneuX. |

Expected raw archive total for P0 + P1 is about 17.4 GB. Extraction and derivatives require at least 80 GB free; plan for 120 GB if keeping both raw and processed copies. The complete CMHA download is published as 14.49 GB compressed, while an alternate Kaggle distribution reports 71.28 GB after packaging; reserve 80 GB for CMHA if acquiring all assets.

## Do not download yet

- **TopAneu 2026:** acquire only after the user explicitly confirms verified-account
  enrollment and acceptance of the official challenge terms. First register a
  CPU/read-only P0 asset/semantics audit; do not download merely because the
  source audit retained a 29/40 conditional lead. Keep payload separate from the
  general corpus and never publish data or labels to this repository.
- **Open multi-center CTA 2026:** the ZIP64 central directory and 16 KB metadata
  member are already audited without full download. The registered P0 stopped
  after partial DICOM-prefix access at an unsupported undefined-length sequence;
  PixelData and STL were not accessed and the scientific gate was not evaluated.
  Do not repair/rerun the parser, stage the 25.58 GB archive, register P1, train
  a model or write case-level identifiers for this closed candidate version.
- **ADAM / CADA:** download only when starting the CTA/MRA detection and segmentation task. They do not provide the CFD fields needed for In-PI-MGN reproduction.
- **AneuG-Flow full archive:** useful for known-condition geometry pretraining,
  but its released BC policy does not vary across cases and it cannot support
  paired-BC C2.
- **Aneumo full archive:** do not download the multi-terabyte release. Use
  `scripts/stage_aneumo_range.py` with the pinned pilot config to range-read
  only selected internal NPY members. The compact fields remain
  non-redistributable under the dataset-specific license.
- **CFD Rupture Challenge:** small and useful for qualitative checks, but too small for a primary training set.

## Canonical layout

```text
dataset_root/
  raw/                                  # immutable; source layout retained
    benchanxplore/v1/coarse_03_dataset.zip
    aneux/v1/data-v1.0.zip
    aneux/v1/models-v1.0.zip
    cmha/v1/patients.rar
  extracted/                            # reproducible extraction output
    benchanxplore/v1/
    aneux/v1/
    cmha/v1/
  manifests/
    datasets.csv                        # version, URL, license, checksum, acquired_at
    cases.csv                           # canonical case identity and source mapping
    assets.csv                          # one row per raw/derived asset
  derivatives/
    geometry_vtp/v1/
    imaging_nifti/v1/
    hemodynamics_features/v1/
    graphs/v1/
  splits/
    surrogate_geometry_disjoint_v1.json
    risk_patient_site_disjoint_v1.json
```

The Git repository keeps only `docs/`, `scripts/`, `manifests/` (without protected identifiers), and small samples. `raw/`, `extracted/`, `derivatives/`, and `scratch/` must be ignored by Git.

## Case and provenance rules

- Canonical ID: `<dataset>--<source_case_id>`; for example `cmha--AHMU1218001`.
- Do not infer that cases shared by AneuX and Aneurisk are the same patient unless a documented mapping establishes it.
- Preserve original files and create conversions as separate derived assets.
- Record coordinate frame, physical unit, checksum, extraction command, and software version for every derived file.
- Use `source_field=real_cfd` or `source_field=surrogate`; never merge these labels.
- Use geometry-disjoint splits for surrogate learning and patient/site-disjoint splits for clinical association studies.

## Closed AneuX executable milestone

1. The exact public AneuX P0 ran once on `introai9` CPU/PBS.
2. It ended execution-incomplete before a completed tabular archive or scientific gate.
3. Preserve the outcome; do not repair/rerun, register P1, download the full model archive,
   or open a model/GPU experiment for this candidate version.

## Aneumo selective paired-BC pilot

`configs/aneumo_g2_pilot_v1.json` fixes 32 distinct AneuX base families, two
deformations per family, eight mass-flow conditions, and 4,096 nodes per case.
The train/validation/test split is disjoint at the **base-family** level, not
merely the synthetic-geometry level. The staging code reads ZIP64 central
directories and required members with HTTP Range, verifies every CRC32, checks
that all eight conditions share coordinates, and writes one compact HDF5 cache.

The preregistered staging completed on 2026-08-03: 512 members formed 64 cases
from 32 base families, with 40/12/12 train/validation/test cases and
20/6/6 disjoint families. Every coordinate and field tensor was finite and had
the expected `(8, 4096, 4)` field shape. The compact-cache SHA-256 is
`9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`.
Neither the cache nor derived field renderings are redistributed.

The pilot supports steady same-geometry mass-flow response only. One scalar mass
flow has no nontrivial partial-component mask lattice, so the pilot cannot
support the full partial-BC coherence claim.

Before any learned G2 fit, `configs/aneumo_scaling_audit_v1.json` permits reads
from the 20 train base families only. It gives a physical baseline the same-case
anchor field, removes pressure gauge offsets, and tests both analytic
\(v\propto Q,\ p\propto Q^2\) scaling and a stronger train-tuned global power
law. A channel is eligible only when the base-family-bootstrap lower confidence
bound leaves at least 15% of paired-response norm unexplained. Full
pressure--velocity learning requires both channels; if neither passes, Aneumo
is retained only as ingestion/runtime evidence rather than a novelty result.

The exact `e12ff0a` audit completed without validation/test field access.
Velocity retained a tuned-scaling residual of 0.2112 with base-family bootstrap
95% CI `[0.2001, 0.2243]`, whereas pressure retained 0.1369
`[0.1190, 0.1496]`. Only velocity is therefore eligible for a future
preregistered learned-response test. This does not authorize that test while
the exact G1/G1r gate remains failed.
