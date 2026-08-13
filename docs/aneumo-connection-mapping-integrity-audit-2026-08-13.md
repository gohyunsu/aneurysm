# Aneumo family-mapping integrity audit

## Decision

Stability P0 v1 is withdrawn before any selected field access. Its 12-family,
60-member panel is historical provenance and cannot be activated. A new panel
must not be selected until the dataset owner publishes or otherwise confirms
an authoritative corrected family mapping.

## Primary-source evidence

The latest official Aneumo main commit is
`701d53dde3489d84dbe9bc8324254629162eb45a`, dated 2026-07-24 21:20:37 +08:00.
Its Connection.csv has SHA-256
`09a5344ac3b3b30a3a677ca619710142782983144362d069b5a2f57caaeabd0b`.

In official issue 4, the owner stated that samples 2158 and 2159 should map to
`115_deform`, not `114_deform`, and said the team would review the complete
mapping and release an updated table. The pinned commit is a partial correction
made before the full-review promise. It moves case 2159 and following rows but
still contains:

```text
2158,114_deform_10
2159,115_deform_1
```

No newer official commit exists. The owner statement and current table thus
still disagree for case 2158.

## What follows—and what does not

Cases 2158/2159 lie outside the transient 1--1000 subset. This does not prove
that any selected P0 row is wrong. It does prove that the current table has not
been shown to be the promised fully reviewed mapping. Consequently, the claim
that the first 1,000 cases form 40 correct base families is not sufficiently
verified for family-level confirmatory inference.

This source-integrity blocker is independent of the HF/GitHub licence conflict
and independent of introai9 health. Resolving one cannot rescue the others.
Until both mapping and licence are authoritatively resolved:

- stage/read no P0 field member;
- create no activation manifest or PBS submission;
- select no replacement family panel;
- train no model and activate no paper claim.

The D0 v2 development result remains valid only as a one-case parser/extractor
check because it did not use family-level scientific inference. No result is
deleted or relabelled. `junjinyong` remains completely excluded.
