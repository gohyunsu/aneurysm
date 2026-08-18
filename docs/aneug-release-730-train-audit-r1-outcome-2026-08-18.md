# Release-730 train audit R1 outcome

CPU-only PBS job `117034.ECE-util1` exited 1 after 2 minutes 11 seconds. Exact
source, processed-v5, steady-normalizer, public-split and private-manifest
checksums passed, and both tensor archives loaded through read-only mmap.
Execution then stopped during private split validation before any case tensor
was indexed.

The split producer defines its public case digest as SHA-256 of sorted IDs
joined by newlines. The audit reader independently reimplemented that helper
with compact JSON, while its synthetic test used the same incorrect helper.
The identifiers were identical; only serialization grammar differed. Train,
validation, locked-test and processed-only field read counts are all zero.
There is no scientific or performance verdict.

R1 remains immutable. The correction removes the duplicate implementation and
imports the producer's exact canonical-digest helper. A regression test pins
the newline grammar. After a fresh Research Quality pass and private activation,
the same scientific audit may run under a new append-only job ID. This is an
implementation repair, not a split change, threshold change or model retry.
