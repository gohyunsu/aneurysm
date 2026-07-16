# Dataset acquisition plan

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
| P0 | AneuX | `data-v1.0.zip` | 13 MB | Clinical/morphology metadata and case mapping. |
| P1 | AneuX | `models-v1.0.zip` | 6.3 GB | Geometry scale for morphology and geometry-only experiments. |
| P1 | CMHA / Gong 2024 | `patients.rar` + `statistical results.rar` | 9.99 GB + 34 KB | Patient CTA, STL, and real hemodynamic summaries. |
| P2 | CMHA / Gong 2024 | `controls.rar` | 4.49 GB | Only needed for case-control imaging studies. |
| P2 | AneuriskData | Git repository mirror | ~1.36 GiB repository size | Useful for source-native geometry/centerline/image assets; partly overlaps AneuX. |

Expected raw archive total for P0 + P1 is about 17.4 GB. Extraction and derivatives require at least 80 GB free; plan for 120 GB if keeping both raw and processed copies. The complete CMHA download is published as 14.49 GB compressed, while an alternate Kaggle distribution reports 71.28 GB after packaging; reserve 80 GB for CMHA if acquiring all assets.

## Do not download yet

- **TopAneu 2026:** acquire only under the official challenge terms, keep separate from the general research corpus, and never publish data or labels to this repository.
- **ADAM / CADA:** download only when starting the CTA/MRA detection and segmentation task. They do not provide the CFD fields needed for In-PI-MGN reproduction.
- **AneuG-Flow / Aneumo:** useful later for synthetic pretraining and stress tests, but should not be the first source for a clinically interpreted risk model.
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

## First executable milestone

1. Download BenchAnXplore and AneuX metadata only.
2. Generate `datasets.csv` with SHA-256 and license data.
3. Inspect one HDF5 case and one AneuX mesh in a notebook/script.
4. Only then acquire AneuX models and CMHA patients on external storage.
