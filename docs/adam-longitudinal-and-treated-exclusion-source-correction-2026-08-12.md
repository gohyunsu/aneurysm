# ADAM longitudinal and treated-exclusion source correction

**Date:** 2026-08-12  
**Decision:** reject all six fresh formulations; active lead, P0, method and compute remain zero  
**Latest best:** 28.5/40; best residual novelty 2.0/5; critical gate failed

## Executive judgment

The supplied surface-vector analysis contains one scientifically valuable idea:
field accuracy and structural fidelity are different questions. Its proposed
order—task stability, field-error-matched baseline failure, bounded development,
fresh confirmation and external interpretation—is retained. The suggested
edge-1-form, Hodge, SE(3), periodic and structural-loss modules remain an
**unselected control set**, not a contribution. No stable critical-point or
worldline failure has been observed, and no fresh material surface-field asset
has appeared. The closed `115645.ECE-util1` P0 therefore remains
execution-incomplete/no scientific verdict, with 0/10 checks and no repair or
rerun.

The fresh source delta instead concerns the meaning of ADAM's longitudinal and
treated-region annotations. It corrects an attractive but invalid shortcut:
ADAM's 35 follow-up scans cannot be assumed to be 35 post-treatment outcomes,
and label 2 cannot serve as a remnant, occlusion or treatment-response target.
That correction improves provenance but does not identify a new paper.

## What the official ADAM source actually supports

The official [ADAM challenge paper](https://doi.org/10.1016/j.neuroimage.2021.118216)
describes a TOF-MRA detection and segmentation challenge for untreated,
unruptured intracranial aneurysms. The reported units are:

| partition | scans/cases | positive scans | negative scans | paired subjects | unique positive subjects |
|---|---:|---:|---:|---:|---:|
| training | 113 | 93 | 20 | 35 baseline + 35 follow-up scans | 23 |
| sealed test | 141 | 115 | 26 | 43 baseline + 43 follow-up scans | 29 |

“35 baseline + 35 follow-up” means 70 scans from 35 people. It does not mean 70
independent patients, 35 growth events or 35 interventions. The paper states
that paired scans are separated by more than six months, but the public source
does not expose an exact pair manifest, lesion correspondence or adjudicated
growth label. The sealed challenge test is not a public AURORA outer test.

The official test counts deserve an explicit provenance note: the paper reports
141 total cases, 115 positive cases and 26 negative cases, which sum correctly.
Older web summaries have circulated different positive counts. AURORA pins the
paper values and does not manufacture a reconciliation from secondary text.

## Label 2 is an exclusion region, not a treatment endpoint

The official [manual reference standard](https://adam.isi.uu.nl/data/manual-reference-standard/)
defines:

| label | meaning | official evaluation role |
|---:|---|---|
| 0 | background | negative class |
| 1 | untreated, unruptured aneurysm | detection/segmentation target |
| 2 | treated aneurysm **or** treatment-related artifact | ignored region |

Label 2 is deliberately rough and dilated by one pixel in-plane. It merges a
treated aneurysm with its treatment artifact and is ignored in official
evaluation. It therefore does not identify residual filling, occlusion grade,
treatment type, retreatment need, biological change or clinical action. A
selective model may avoid false outputs in this region, but that is an
evaluation template until a clean patient-level reference and action contract
exists.

## Why the 2025 “pre/post-treatment” wording is not a new ground truth

The 2025 [MSDA-Net paper](https://doi.org/10.1049/ipr2.70199) reports the public
ADAM branch as 78 “distinct/baseline” and 35 “post-treatment (follow-up)”
volumes, while also excluding label 2 from evaluation. This wording conflicts
with the official target semantics: follow-up is a time relation, whereas label
2 is the only treatment-related annotation and is ignored. The private Uppsala
post-treatment cohort in that paper is separate.

AURORA records this as a **bounded semantic correction**, not an accusation
that every result in the paper is invalid. It also cannot be paper novelty:
source interpretation and reproducibility provenance are valuable, but they do
not supply an estimand, intervention or independent confirmatory cohort.

## Access and legal-operational boundary

The legacy ADAM pages now redirect to Grand Challenge. The signed
[confidentiality agreement](https://adam.isi.uu.nl/wp-content/uploads/2020/03/ADAMConfidentialityAgreement.pdf)
requires complete team registration, prohibits redistribution and limits data
to challenge-entry preparation unless the team has prior challenge
participation and organizer approval for other research use. AURORA has not
registered, signed or accepted these terms, contacted the organizers, obtained
reuse approval, downloaded a payload or inspected a pair manifest.

Consequently asset readiness remains 2.0/5. A paper abstract cannot convert a
controlled challenge asset into an executable ISBI development contract.

## Direct-prior lineage

The residual gap is narrower than “use two time points”:

1. ADAM itself stratified and evaluated baseline/follow-up performance.
2. The 2025 MSDA-Net source already combines aneurysm segmentation and
   volumetric quantification on ADAM plus a private post-treatment cohort.
3. Paired MRA growth measurement is established. In a 72-patient/84-aneurysm
   study, 2D change reliability was poor (ICC below 0.5) while 3D change ICC was
   0.76 ([PMID 34210663](https://pubmed.ncbi.nlm.nih.gov/34210663/)).
4. Serial volumetry, registration, longitudinal consistency and adjacent-vessel
   internal controls directly occupy the obvious measurement mechanisms.
5. Generic false-output budgets, selective prediction and conformal risk
   control directly occupy the obvious wrapper mechanisms.

Thus “longitudinal U-Net,” “registration consistency,” “treatment-aware mask”
or “calibrated growth” is not an independent residual contribution.

## Prospective non-compensatory screen

Axis order is importance, identifiability, residual novelty, asset readiness,
independent unit, strong-baseline feasibility, interpretable evidence and ISBI
schedule fit. Admission requires total at least 32 plus critical floors; a high
total cannot compensate for a missing target or asset.

| candidate | axis scores | total | decision |
|---|---|---:|---|
| Patient-level all-lesion correspondence | 5 / 3 / 2 / 2 / 3.5 / 5 / 5 / 3 | 28.5 | Exact pair, lesion and change contract absent |
| Ignored-treated-region false-output budget | 5 / 2.5 / 2 / 2 / 3 / 5 / 5 / 3.5 | 28.0 | Label 2 mixes treated lesion and artifact; no outcome target |
| Change-preserving paired segmentation | 5 / 3 / 1.5 / 2 / 3.5 / 5 / 5 / 3 | 28.0 | Direct-prior dense; growth truth absent |
| Paired-mask growth interval calibration | 5 / 2.5 / 1 / 2 / 3.5 / 5 / 5 / 3 | 27.0 | Mask difference is not biological growth |
| Registration-failure certificate | 4 / 3.5 / 1.5 / 2 / 3.5 / 5 / 4.5 / 3 | 27.0 | Registration QC is direct prior; pair contract controlled |
| MSDA-Net pre/post semantic re-audit | 4 / 2 / 0.5 / 2 / 3 / 5 / 4 / 4 | 24.5 | Provenance correction, not method contribution |

All six fail at least the total, novelty, identifiability or asset floor. Scores
are frozen and will not be repaired upward.

## Final decision and re-entry condition

- Surface-vector remains an inactive conditional hypothesis.
- The architecture sketch remains a baseline/control inventory only.
- ADAM longitudinal or label-2 semantics opens no active paper identity.
- No data terms, payload, P0/P1, method, architecture, server query, PBS/GPU,
  outer test, result row, C21, title or manuscript claim is authorized.
- Historical P0 scores and no-verdict outcomes are unchanged.

A future version needs a lawful, versioned patient-level asset exposing exact
timepoint and lesion correspondence, an adjudicated change or action target,
patient-disjoint development/confirmation units and a mechanism-linked failure
not already owned by longitudinal measurement or generic calibration. A future
surface-vector version separately needs material transient surface fields,
stable registered structure extraction and an observed field-error-matched
failure before any architecture or GPU run.

No scientific server was queried in this update. Future gate-authorized work is
`introai9` PBS only, with no login-node GPU command. `junjinyong` was not and
must never be accessed, queried, used for transfer, submitted to or monitored.
