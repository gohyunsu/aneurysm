# AneuG-Flow official-source reconciliation

## Adjudicated dataset identity

The canonical transient release is **730 synthetic CFD cases**, not 730
patients. This number is supported independently by the final NeurIPS paper,
the pinned Hugging Face dataset card and an exact inventory of the pinned
release tree. The tree contains 730 `stable_*` directories, and every directory
contains the seven assets documented by the card (5,110 files in total).

This conclusion does not erase conflicts in the primary sources. They are
retained explicitly:

| Question | Primary-source observations | Adjudication |
|---|---|---|
| pulsatile case count | NeurIPS proceedings HTML says 200; the final PDF repeatedly says 730; the card and release tree also say/show 730 | use 730; record the HTML value as inconsistent metadata |
| real shapes used to train the generator | final-paper abstract says 109; Table 1 says 116 | unresolved; make no patient- or generator-parent-lineage claim |
| documented processed object | dataset card names v4 | v5 is an official repository blob, but is not described by the card |
| v5 cohort | exact metadata audit finds 809 entries | use only the exact 730-case release intersection; exclude 79 undocumented extras |

Primary sources: [final NeurIPS 2025 paper](https://papers.neurips.cc/paper_files/paper/2025/file/e2b8ff0035bc9f572a7deefbcbea85bc-Paper-Datasets_and_Benchmarks_Track.pdf),
[proceedings HTML](https://papers.neurips.cc/paper_files/paper/2025/hash/e2b8ff0035bc9f572a7deefbcbea85bc-Abstract-Datasets_and_Benchmarks_Track.html),
[pinned dataset card](https://huggingface.co/datasets/whding123/AneuG-Flow/blob/9dd418083899deddd93a67f9a6fca7a14304fa36/README.md), and
[pinned official code](https://github.com/WenHaoDing/AneuG-Flow/tree/4a090a0f12538deef6fcea88b81afe78ce38152e).

## What one case means

Each case is a synthetic middle cerebral artery bifurcation geometry with one
inlet and two outlets. The source uses the same average inlet waveform for all
transient simulations and a geometry-dependent outlet mass-flow split. Two
cycles were simulated and 80 uniformly spaced phases from the second cycle were
released. The registered ML surface has 13,902 nodes and 14,000 triangles with
shared connectivity.

The defensible task is therefore:

> predict registered complete-cycle vector WSS from synthetic geometry under
> the release's fixed waveform protocol and geometry-dependent outlet rule.

It is not patient-specific boundary-condition inference, multi-site
generalization or rupture-risk prediction. The release has no patient, site or
generator-parent labels and no boundary-condition variation.

## Raw release versus processed v5

The final paper describes raw transient variables in per-case files. The card
lists the seven files in each raw case folder and explicitly names processed
v4. The official preprocessing code interpolates raw wall fields to the common
surface, inserts normals and concatenates coordinates, normals and vector WSS.
That code explains the verified v5 case tensor shape `80 × 13,902 × 9`, but
does not turn all 809 v5 entries into the documented release.

The v5 object contains every canonical release ID and 79 additional IDs. The
main cohort is therefore the set intersection of v5 with the pinned release
tree. The historical v4 object contains 578 entries but only 499 canonical
release IDs, so neither its cohort nor its old split is reused.

## Normalization provenance is a separate completeness condition

The official builder normalizes every transient channel using a separately
loaded steady `tensor_norm`:

\[
z=(x-\mu)/(\sigma+10^{-5}).
\]

It then saves only `registered_data_list` and `mesh_data`; the transient object
does not embed the normalization record. The official README says
`given_norm=None` may be chosen, but the pinned implementation raises
`NotImplementedError` in that branch. The executable official training script
loads the v4 steady object and passes its `tensor_norm` to the builder.

The exact steady v4 source needed for decoding remains on `introai9`
(9,632,510,050 bytes; SHA-256 `0c03c1d9…0177f`). CPU/PBS job
`117006.ECE-util1` subsequently compared every one of the 578 v4/v5
overlapping cases. All nine channels, GHD rows and shared hierarchy items were
bit-exact; the maximum tensor mismatch was zero. The result binds the
steady-normalizer fingerprint and supports physical decoding under the
official single-normalizer builder. Because v5 has no embedded creator
manifest, this is strong common-lineage evidence rather than direct metadata
proof for the 231 v5-only entries.

## Source-intended composition versus the acquired study object

| Item | Official source intent | Exact acquired evidence | Study use |
|---|---|---|---|
| transient cohort | 730 synthetic pulsatile CFD cases in the final paper/card/tree | all 730 occur in v5; no release ID is missing | exact 730-ID intersection |
| processed v5 | not documented by the card | official blob has 809 entries | exclude 79 processed-only extras |
| temporal sampling | second simulated cardiac cycle, 80 uniform phases | every canonical case tensor has 80 phases | keep the full cycle within its case split |
| registered surface | common connectivity, 13,902 nodes and 14,000 triangles | schema has 13,902 nodes and shared hierarchy | registered surface operator task |
| target | Cartesian vector WSS at the wall | final three channels are `wss_x/y/z` | vector WSS, with derived TAWSS/OSI |
| boundary conditions | one common inlet waveform; geometry-dependent two-outlet split | no independent BC-varied input is present | geometry-conditioned fixed-protocol prediction only |
| normalization | external steady `tensor_norm` in official builder | complete v4 overlap is bit-exact in v5 | decode with bound steady norm; fit model transforms on train only |

The raw release additionally contains volume velocity, pressure and derivative
fields, but they are not present in the acquired processed surface object and
are not implied by this study.

## What the published baseline does and does not establish

The paper's 4.67% normalized relative-L2 result is from a **steady-state** WSS
experiment on the 14,000-case steady dataset with an 80/20 split. It is not a
730-case transient full-cycle baseline. The released transient helper defaults
to v4 and makes an order-dependent 90/10 prefix slice; it does not publish a
patient-, family- or site-disjoint transient protocol.

Consequently, the new 730-case work needs its own outcome-blind,
geometry-duplicate-disjoint train/validation/locked-test split and direct
transient baselines. It must not compare a complete-cycle error to the paper's
steady 4.67% as if the tasks were identical.
