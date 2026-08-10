# OpenNeuro containment-identified morphometry source audit · 2026-08-10

> **Outcome · schema 6.9:** Exact public source `bb227edc…` ran once on
> `introai9` as CPU/PBS job `115622.ECE-util1` and finished `F`/exit 1 after
> 00:02:24. Only a 310-byte `execution_incomplete` status materialized; no
> aggregate result or raw PBS output exists. Therefore 0/10 registered checks
> were evaluated and the scientific verdict is null. This exact candidate is
> closed without repair, rerun, P1, payload, method, architecture, GPU or outer
> test. See
> `results/openneuro_containment_morphometry_p0_execution_20260810.json`.

## Decision

This is a new evidence version, not a repair or relabelling of the rejected
31.5/40 `one_sided_outer_annotation_morphometry_sets` candidate. The old version
asked whether the real weak-annotation mechanism could be learned from paired
weak and independently precise masks of the same subject; that pairing is still
absent and the old rejection remains unchanged.

The new question deliberately does **not** estimate that coarsening mechanism.
It treats each weak sphere only as an observed containment statement,
\(Y\subseteq W\), and uses precise masks only in disjoint calibration and
evaluation subjects. The proposed estimand is a set-valued lesion mask and the
induced interval for monotone morphometry, not a pseudo-precise segmentation or
an unobserved biological truth.

The frozen eight-axis screen admits
`containment_identified_morphometry_envelopes` at **32.5/40**. This is one
conditional source lead and opens only one method-free, metadata-only P0. It is
not a selected method, architecture, contribution, GPU experiment, outer test or
submission identity.

| Rank | Fresh candidate | Importance | Identifiability | Residual gap | Asset | Independent unit | Baseline | Figure | Schedule | Total | Decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Containment-identified morphometry envelopes | 4.5 | 4.0 | 2.0 | 4.0 | 5.0 | 5.0 | 5.0 | 3.0 | **32.5** | conditional P0 |
| 2 | Longitudinal surface-growth detection | 5.0 | 4.5 | 0.5 | 4.5 | 2.0 | 5.0 | 5.0 | 5.0 | **31.5** | reject; unchanged prior version |
| 3 | Acquisition-quality-indexed external lesion-set risk | 5.0 | 3.0 | 1.5 | 4.5 | 4.0 | 5.0 | 5.0 | 3.0 | **31.0** | reject |
| 4 | Cross-centre weak-to-strong segmentation | 4.5 | 4.5 | 0.0 | 4.5 | 4.0 | 5.0 | 5.0 | 3.0 | **30.5** | reject |
| 5 | Reference-morphometry conformal certificate | 4.5 | 4.0 | 0.5 | 4.5 | 3.5 | 5.0 | 5.0 | 3.0 | **30.0** | reject |
| 6 | Conformal lesion-FNR control | 4.5 | 5.0 | 0.0 | 4.0 | 4.0 | 5.0 | 5.0 | 2.5 | **30.0** | reject |

The admission line remains 32/40. Scores are arithmetic sums of the displayed
cells and are frozen before patient image or mask payload access.

## Source facts that changed the executable boundary

The Lausanne OpenNeuro release is pinned to tag `1.0.1`, commit
`896b8846d899acee68c0246cc987ca96e77267d4`. Its Git tree has 5,737 paths,
284 public subjects, 296 subject-session pairs under `manual_masks`, and 494
NIfTI mask paths. The dataset description declares CC0 and DOI
`10.18112/openneuro.ds003949.v1.0.1`. No NIfTI content was read.

The official paper/code repository is pinned to
`5ecdf6e5b9a811e4ec7472c210dada42e60cc3dc` under Apache-2.0. Its pickle files
were inspected with `pickletools` opcodes only; they were never unpickled or
executed. They contain:

- 38 unique precise subject-session entries from 38 subjects;
- 262 unique weak subject-session entries from 250 subjects;
- no subject or session overlap between the two lists.

The public dataset has exactly 284 subjects because four weak-list subjects
(`sub-115`, `sub-143`, `sub-181`, `sub-272`) are absent from the public tree.
After this release filter, all public subjects map exactly once to 246 weak and
38 precise subjects. Session dates cannot be used as join keys: only 11 code
subject-session strings match released manual-mask paths, consistent with
de-identification/session rewriting. Subject identity is the only registered
join for P0.

This machine-auditable mapping is the new source evidence. It does not create
same-subject real weak/precise pairs and does not authorize a claim about how
annotators choose a sphere centre or radius.

## Direct-prior boundary

The residual novelty score is only 2/5 because every component has a strong
control:

- Di Noto et al. already establish aneurysm-specific weak spheres, anatomical
  sampling and public code/data.
- VP-UNet and FocalSegNet already perform aneurysm-specific weakly supervised
  detection/segmentation; CVPR 2026 WeakMed directly addresses box-shaped bias.
- MICCAI 2025 morphological conformal prediction constructs spatial prediction
  sets; Conformal Lesion Segmentation directly controls 3D lesion FNR.
- ICLR 2026 COMPASS calibrates downstream segmentation-metric intervals,
  including covariate-shift weighting.
- NeurIPS 2024 already frames weak-supervision evaluation as partial
  identification.

Therefore U-Net, vesselness, topology, conformal calibration, partial-label
loss, morphometry regression or a named uncertainty head is not novelty. A
future method can survive only if the containment formulation yields a tighter,
valid morphometry envelope than these direct controls while preserving lesion
detection and external-centre coverage.

The public MAXIMUS model cannot serve as an external Lausanne or Royal Brisbane
baseline because its training cohort explicitly includes both sources. Royal
Brisbane also contains aneurysm-positive patients rather than a representative
negative screening cohort, so it may test matched-lesion morphometry coverage
but not population screening workload.

## Frozen prospective method-free P0 · closed history

The following contract is preserved exactly as registered. It is no longer
pending or executable after the schema-6.9 outcome above.

`configs/openneuro_containment_morphometry_p0.json` registers one CPU/read-only
metadata audit. It may read only the exact GitHub tree JSON, dataset description,
two small supervision-list pickle blobs and the code license. It must not read a
NIfTI image/mask body, participant table, clinical annotation, pretrained model,
checkpoint or outer test.

All checks are all-or-none:

1. exact source commits and small-blob SHA-256 values;
2. non-truncated 5,737-path OpenNeuro tree;
3. 284 public subjects, 296 manual-mask subject-session pairs and 494 mask paths;
4. safe opcode-only parsing of 38 precise and 262 weak entries;
5. disjoint precise/weak subjects and sessions;
6. exact four-subject public-release exclusion;
7. exact 246 weak + 38 precise public partition with no unmapped subject;
8. session strings are rejected as a join key and subject identity is unique;
9. CC0 dataset and Apache-2.0 code license;
10. zero patient payload, method, model, GPU and outer-test access.

The single exact job permits three in-job transient transport attempts per HTTP
operation at frozen delays 0/10/30 seconds. This is not permission for a second
PBS submission or a same-contract repair. Pass authorizes only registration of
a separate method-free P1 task-adequacy audit. Fail or execution-incomplete
closes this exact version without method, architecture, GPU or paper claim.

Execution is restricted to `introai9` PBS with CPU 2, memory 4 GB, GPU 0 and
walltime 20 minutes. `junjinyong` is excluded from connection, query, transfer,
submission and monitoring. Login-node GPU commands remain prohibited.
