# Release-730 split R1 schema-key outcome

CPU-only PBS job `117020.ECE-util1` exited 1 after 27 seconds, before loading
the processed tensor object, reading any registered field, computing any GHD
distance or assigning any case. The exact schema record passed its own audit
and has SHA-256 `9e74cb3d...fa6ed`.

The failure was a runner contract typo. The pinned schema record emits
`mesh_order_exact`; the R1 runner asked for `mesh_case_order_exact`. The fix
changes only that lookup and adds a regression test using the exact emitted
field name. Dataset revision, cohort, normalization result, grouping
tolerances, private key, targets and test lock are unchanged. R1 artifacts
remain immutable; a Quality-passed follow-up commit may be retried under a new
PBS job ID.
