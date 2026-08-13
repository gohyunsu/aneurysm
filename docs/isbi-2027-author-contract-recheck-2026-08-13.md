# ISBI 2027 author-contract recheck

Checked: 2026-08-13 KST
Decision: venue contract verified; manuscript and scientific claim remain inactive

## What is now known

The official home page, author instructions and one-page call for papers agree
that the archival target is an IEEE ISBI 2027 four-page paper due on 26 October
2026 at 23:59 USA EDT. Notification is 12 January 2027 and the final paper is
due 26 January 2027. Review is single blind. The official submission endpoint
still says `Coming Soon`.

Every technical statement, table and figure must fit in pages 1--4. A paid
fifth page may contain only the separately titled ethics statement,
acknowledgments/conflict disclosure and references. The ethics statement is
required even when no approval was necessary. Funding and either a conflict
disclosure or an explicit absence-of-conflict disclosure are also required.
Human authors must verify those facts; a repository placeholder cannot do so.

The author page prohibits concurrent substantially similar conference or
workshop submission during review. The official CFP uses the stricter wording
conference or journal. AURORA therefore applies the conservative union:
**no substantially similar conference/workshop/journal concurrent review**.
Preprints remain allowed under the cited IEEE policy.

## The template link is legacy, not 2027-specific

The 2027 author page currently links a ZIP under a 2025 URL. More importantly,
the archive's own README is titled `ISBI 2021 Paper Submission Templates`, and
all internal timestamps are 31 July 2024. The link is organizer-provided, so it
is the best current layout source; it is not evidence that the organizers have
published a 2027-specific template.

Exact provenance:

- linked archive SHA-256:
  `3acdec37077eff51b787c710e4d971dcabc69f2cf11bd6a7308836d922b313d7`;
- template TeX SHA-256:
  `cd584135bca1b49c3b7b3f18e97dd2a86f22eae4dbff71174873edc7206c686b`;
- upstream `spconf.sty` SHA-256:
  `dc5d632639040cb183f2ab62780f314845aa021be73048c8a9ec9c2072d64a86`;
- upstream `IEEEbib.bst` SHA-256:
  `7e6ca0c8b72158d504a12bb091f817c07032a021ba41ca783cca4c2dd80d570b`;
- active-command stream shared by upstream and the comment-stripped private
  copy:
  `c9998f06a6ae31a8bf454bb93a1194f785993b8bc3bdd0e6f213b830d87766f7`.

The private copy removed upstream comments and added a provenance header, so
it is not byte-identical. Its active LaTeX command stream is identical. This
distinction is now explicit rather than calling the file an unmodified copy.

## Current manuscript classification

The private `response_fidelity_plan.tex` uses the organizer-linked `spconf`
layout, has a 136-word abstract, separate ethics and disclosure sections, and
keeps every result and contribution cell sealed. It uses `unsrt`, not the
linked template's `IEEEbib` bibliography style. It is therefore an internal
ISBI-layout pre-evidence shell, **not a submission manuscript** and not a final
format certification.

The sealed source and bibliography are not edited to make an inactive research
direction look submission-ready. If the evidence chain activates, a fresh
submission source must be built from the then-current organizer template,
carry the official bibliography style, pass pdfLaTeX and page-by-page visual
inspection, and keep all technical material within the first four pages.

## One role per paper element

If real P0, matched P1 and independent confirmation later activate the paper,
the four technical pages have the following non-overlapping jobs:

| Element | Sole role | Delete when |
|---|---|---|
| Introduction | Establish the repeated-flow application, matched-field failure question and direct-prior boundary | P1 finds no matched response failure |
| Method | Describe only the failure-linked anchor-identity intervention | The isolated intervention has no validation gain |
| Experiments | Define family independence, strong controls, field matching and prospective statistics | Any protected split or comparator is unavailable |
| Main table | Resolve field equivalence and all four direct/power-law response contrasts | Any mandatory cell is missing or fails |
| Figure | Show mechanically selected worst/median/best families under matched display settings | Confirmation rows or selection manifest are incomplete |
| Discussion | Bound inference to synthetic steady CFD velocity response | Text drifts to rupture risk, clinical utility, WSS or patient physiology |

Protocol version history, server operations, source scores, CI counts and
scheduler management do not consume technical-page space. They remain
reproducibility provenance.

## Scientific boundary

Venue compliance cannot rescue an unidentified task. Real response-fidelity P0
v3 is still 0/12; P1 is unregistered; method, GPU experiment, outer evidence,
result and claim remain zero. This audit made no scientific-server query,
transfer, scheduler query, PBS/GPU submission or monitoring. It is not an
`introai9` operational change and does not authorize a retry. `junjinyong`
remains prohibited.

## Official sources

- [ISBI 2027 home and important dates](https://biomedicalimaging.org/2027/)
- [ISBI 2027 initial author instructions](https://biomedicalimaging.org/2027/papers/)
- [ISBI 2027 call for papers](https://confcats-event-sessions.s3.us-east-1.amazonaws.com/isbi27/isbi27-cfp_web-03.pdf)
- [Machine-readable AURORA venue contract](../configs/isbi_2027_author_contract_v2.json)
