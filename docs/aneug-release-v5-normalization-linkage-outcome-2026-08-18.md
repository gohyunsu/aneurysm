# Processed-v5 normalization-linkage outcome

## Outcome

CPU-only PBS job `117006.ECE-util1` completed with exit code 0 in 00:26:15.
It compared every one of the 578 entries shared by processed v4 and v5. All
nine tensor channels, all 432 GHD values per case and all eight shared mesh
hierarchy items were bit-exact. The maximum absolute tensor mismatch was 0.

The exact public result is
`results/aneug_release_v5_normalization_linkage_20260818.json` with SHA-256
`a083a4a71abfca55cac4e638daad00c7acd2bd7a66a3a42b2d5302374fb11fdb`.
It binds the three full source hashes and the external steady-normalizer
fingerprint `5041cfc8...6b6f2`.

## What this supports

The pinned official builder has one normalization path: every transient
channel is transformed using the supplied steady `tensor_norm`, and that norm
is omitted from the transient output. Complete bit identity of the entire v4
cohort inside v5 therefore provides strong evidence that v5 extends the same
official processed lineage. Physical decoding with the exact bound steady
normalizer is supported for the release-aligned cohort.

This remains a provenance inference for the 231 v5-only entries, not a direct
creator-manifest proof. V5 embeds no normalization metadata, the dataset card
does not describe v5, and no v5-only creator manifest is available. These
limitations must remain in the paper. Model centering/scaling is separately
fit from the new training split only.

## What this does not support

The audit read no registered field distribution statistic, model result,
validation endpoint or locked-test outcome. It is not evidence that an
architecture performs well, and it does not justify using all 809 processed
entries. The paper cohort remains exactly the 730-case intersection with the
pinned public release tree.
