# Release-730 train-only physical audit

This stage is the first field-value read under the completed 584/73/73
release-aligned split. It uses CPU only and indexes tensors for the 584
training cases. Validation, locked-test and the 79 processed-only cases remain
sealed.

The official transient object stores normalized nine-channel tensors but not
the normalizer. The audit therefore binds the exact steady normalizer already
supported by the 578-case bit-identity lineage audit, decodes
`physical = normalized * (std + 1e-5) + mean`, and verifies finite tensors,
static geometry, round-trip accuracy, connectivity and cycle endpoints. These
are data-integrity checks, not arbitrary model-performance thresholds.

Tangency, stored/mesh-normal agreement, phase-79-to-0 jump, surface area,
response RMS, TAWSS and OSI are descriptive. They may influence representation
and loss design but cannot pass or reject a model. Private output contains the
exact train loader order and train-derived coordinate, normal, WSS and GHD
statistics. Public output contains only deidentified aggregates and four zero
read counts for validation, test and processed-only fields.

No compact tensor duplicate is created. All later comparators must bind the
same private statistics and loader-order hash, which avoids both unnecessary
storage and normalization drift. A diagnosed infrastructure or implementation
failure may be corrected under a fresh append-only run ID; completed attempts
are never overwritten.
