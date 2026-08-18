# AneuG steady supervision: required control, not paper novelty

## Decision

The frozen 584/73/73 transient split remains the main evaluation protocol.
The current transient-only released Graph U-Net run remains necessary and is
not stopped. The paper documents 14,000 steady cases, but metadata-only
inspection of the exact processed-v4 object shows 14,392 case names, a
`14,392 × 13,902 × 9` tensor and a `14,392 × 432` GHD matrix. The processed
asset is added as an information-budget control after a geometry-only overlap
audit; it does not redefine the split or open locked transient WSS.

This distinction is important because the two primary sources answer different
questions. The AneuG-Flow dataset paper reports 14,000 steady and 730 pulsatile
CFD cases, but its 4.67% benchmark is an 80/20 **steady-WSS** experiment. It is
not a complete-cycle transient result. The later RHSIA preprint already mixes
the 14,000 steady cases with transient snapshots by masking temporal features,
tests a separately predicted steady-WSS FiLM prior for a sequence baseline,
and reports transient label-efficiency ablations. Therefore, merely pretraining
on steady WSS or calling steady WSS an anchor is prior art, not an independent
contribution.

Primary sources:

- [AneuG-Flow final NeurIPS 2025 paper](https://papers.neurips.cc/paper_files/paper/2025/file/e2b8ff0035bc9f572a7deefbcbea85bc-Paper-Datasets_and_Benchmarks_Track.pdf)
- [RHSIA v2](https://arxiv.org/html/2601.19876v2)
- [Pinned AneuG-Flow code](https://github.com/WenHaoDing/AneuG-Flow/tree/4a090a0f12538deef6fcea88b81afe78ce38152e)

## Completed leakage audit

The exact 9,632,510,050-byte steady-v4 object is already present on
`introai9`. Its previously verified root schema includes `tensor`,
`case_name`, and `ghd_dict`, so no raw CFD download was needed. Before any
steady label use, CPU job `117143.ECE-util1` established:

1. exactly 14,392 unique steady case names and a `14,392 × 13,902 × 9`
   float32 tensor by metadata only, while preserving the source paper's
   documented 14,000 count as a provenance discrepancy;
2. an exact 432-D GHD row for every steady and transient geometry;
3. case-name, exact-GHD, and fixed-tolerance GHD overlap against train,
   validation, locked test, and the 79 processed-only transient extras;
4. an eligible steady index set excluding every steady geometry that matches
   any transient partition.

The audit read geometry metadata but indexed no steady or transient WSS value.
Its public result contains only counts, digests, and aggregate distance
summaries; the case-index mapping remains private and append-only.

### Result

- 14,392 processed steady geometries were present.
- 407 had an exact 432-D GHD match to a transient partition: 317 train, 42
  validation, 39 locked test and 9 processed-only extras.
- 398 pairs also shared an exact case name; the additional nine GHD matches
  belonged to the extras. No near-only pair met the fixed tolerance.
- All 407 matched steady rows are excluded, leaving 13,985 eligible rows
  (97.2% of the processed steady object) with digest
  `6dbfde4d...c82cc`.

This result resolves the review concern without accepting related-label
leakage: almost the entire steady asset remains available, while no exact
registered geometry from any transient partition contributes a steady WSS
label. Exact public result SHA-256 is `b3a118ba...a397`.

## Comparator design

Steady supervision must be evaluated as a matched pair, not granted only to a
favoured model:

| Pair | Transient information | Steady information | Purpose |
|---|---|---|---|
| released Graph U-Net | 584 transient cases | none | direct released-class baseline |
| GHD-GPS transient-only | same 584 cases | none | strong geometry baseline |
| GHD-GPS + steady | same 584 cases | eligible audited steady set | RHSIA-information control |
| proposal transient-only | same 584 cases | none | architecture/objective effect |
| proposal + steady | same 584 cases | same eligible steady set | information-budget interaction |

The augmentation mechanism must be declared precisely. Direct code inspection
at the pinned revision shows that the released trainer concatenates steady
snapshots (`time_step=-10`) and transient phase snapshots. Its waveform
embedder masks the steady rows, but its sinusoidal time embedder still evaluates
`t=-10`. The same strict `< T-1` mask also zeros the waveform embedding at
phase 79. The loader applies a transient-weighted mixed-frame objective, and
the released epoch-level test path evaluates only the first test-loader batch
rather than the full split. Consequently, the code path is a source-faithful
implementation control with documented quirks, not a canonical evaluation
protocol or definition of how steady information must be used. Our matched
adapter must retain full 73-case validation and state every difference. A
complete-cycle model cannot pretend that one steady field is an 80-phase cycle;
it must use a shared-encoder auxiliary steady objective or an explicitly
separated steady pretraining stage. These mechanisms are separate ablations.

All model and loss selection remains validation-only. The final candidate and
strongest comparator receive the same steady eligibility manifest, compute
accounting, seeds, and transient endpoints. The locked 73-case test is opened
only after those choices and the analysis rule are frozen.

## Paper identity

Using all available labels can improve performance and reviewer confidence,
but it is not sufficient novelty because RHSIA already occupies steady-data
augmentation. The conditional ISBI contribution remains complete-cycle
field/functional fidelity on a rigorous release-aligned protocol. Steady data
serves three supporting roles: a direct-prior control, an information-budget
ablation, and a label-efficiency factor. A successful paper must still show
that the proposed cycle-native representation improves physical vector-WSS
and TAWSS/OSI over a steady-augmented strong comparator without a field-error
tax.
