# Release-730 split R2 and offline source manifest

CPU-only PBS job `117024.ECE-util1` exited 1 in 00:04:32. It passed the exact
schema guard and source checksum, then failed when the compute node attempted
to query the pinned Hugging Face API. The node has no external network route.
No processed object was loaded, no GHD distance or assignment was computed,
and no registered field or locked-test value was read.

The official release-tree request was repeated from the development host at
the same immutable dataset revision. Its 730 public `stable_*` directory names
are now stored in
`results/aneug_release_730_case_manifest_9dd4180.json` (SHA-256
`5218ae05...b20f0`). The sorted ID digest is the previously registered
`cccc90d7...390a`; the count and digest are independently revalidated by code.

The runner now consumes this exact local manifest and performs no compute-node
network request. Dataset revision, cohort, private split key, GHD tolerances,
target counts and test lock are unchanged. R2 remains immutable; a new-ID R3
is a transport-reproducibility correction, not a new scientific split.
