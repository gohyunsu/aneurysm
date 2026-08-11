# SynVA release and synthetic-utility source audit

> Frozen on 2026-08-11 KST · schema 9.3 · public paper and repository-search
> metadata only · no medical/synthetic payload, P0/P1, method, architecture,
> scientific-server query or compute

## Decision

SynVA is a substantive new direct prior, not a new executable AURORA asset.
The paper contributes healthy-vessel generation, ostium-conditioned aneurysm
editing, a procedural generator and a claimed 50,000-mesh release.  It also
already evaluates the most obvious downstream question: whether procedural
synthetic pretraining improves real aneurysm-head segmentation.

The full paper does not provide a dedicated SynVA code or dataset URL.  Its
clickable external links resolve to the paper itself, the Pointcept dependency,
the Brain Aneurysm Foundation and the unrelated CROWN source dataset.  Exact
public GitHub repository and code searches for the title and project name
returned no SynVA repository.  “We release” is therefore preserved as an
author claim, not relabelled as a versioned, licensed, checksum-auditable asset.

Six fresh formulations score **27.5/26.5/26.0/26.0/23.5/23.5**, all below the
unchanged 32/40 admission line and all failing at least the residual-novelty or
asset-readiness critical floor.  No active problem, P0, model or compute is
opened.  This is a separate source version; it does not repair the closed
AneuG, Aneurisk or surface-vector executions.

## Exact inspected source boundary

The inspected primary source is
[arXiv:2605.17620v1](https://arxiv.org/abs/2605.17620), submitted 13 May 2026.
The fetched 25,831,786-byte PDF has SHA-256
`f483f6b91bf8ab94d55dd456e22ea108468780131c9df9dcbcaff46d9f2d92fe`.
No paper supplement, generated mesh, model checkpoint or real patient member
was opened.

The paper reports the following rather than AURORA observing them:

- 50,000 independently sampled procedural bifurcation meshes, with 40,000 used
  for synthetic pretraining and 10,000 for synthetic validation;
- vertex labels for vessel, aneurysm and ostium, plus point clouds, submeshes,
  centerlines, radii, ostium descriptors and morphometrics;
- 769 processed real samples from AneuX, IntrA and CMHA before the stated
  exclusions and transformations;
- a 100-sample real test selected by dataset-stratified sampling;
- eleven Point Transformer V3 regimes, including real-only fractions,
  synthetic-only and synthetic-pretrained/fine-tuned variants;
- aggregate real-test mIoU 36.78 for synthetic-only, 50.41 for 10% real-only,
  and 63.88 after synthetic pretraining plus the same 10% real fraction.

These are prior-paper results.  They are not reproduced AURORA results.  The
paper says the real split is consistent across models, but it does not publish
an executable split manifest or explicitly state a patient-grouped split.  A
dataset-stratified sample is not automatically a patient- or source-sealed
outer test.

## Construct-validity boundary

The SynVA appendix is unusually explicit about what the procedural data cannot
support.  It describes simplified single-bifurcation anatomy, no acquisition or
annotation process, no validated WSS or pressure, and no construct validity for
rupture, progression or clinical decision-making.  It also states that the
procedural samples are not derived from patient records: each is generated from
rules, statistical priors and stochastic geometric perturbations.

Consequently:

- 50,000 procedural meshes are 50,000 generated draws, not patients;
- sample count cannot establish population coverage or clinical realism;
- the data cannot serve as transient-WSS or rupture-risk supervision;
- privacy/membership auditing against patient training records is not an
  identified primary problem for the fully procedural release; and
- synthetic-only failure and synthetic-to-real fine-tuning benefit are already
  reported by the source paper.

## Direct-prior red team

The residual space is narrower than “evaluate synthetic data more carefully.”

1. SynVA itself compares real-only, synthetic-only and synthetic-to-real
   pretraining over eleven regimes and a held-out real set.
2. [Synthetic Ground Truth Counterfactuals](https://papers.miccai.org/miccai-2025/0894-Paper2090.html)
   already uses synthetic interventions to localize causal-generative failure
   and separates intended effectiveness from unintended amplification.
3. [A knowledge-based method for detecting network-induced shape artifacts](https://proceedings.mlr.press/v301/deshpande26a.html)
   already connects anatomical shape rules, synthetic-image QA and a reader
   study.
4. [Auditing Data Leakage in Whole-Slide Image Multimodal Benchmarks](https://arxiv.org/abs/2607.12278)
   directly audits patient- and institution-level leakage and measures the
   resulting performance gap.
5. Synthetic-data utility, fidelity, privacy, domain adaptation, curriculum
   weighting, sample selection and scaling laws are established method
   families.  Applying them to procedural aneurysm meshes is not independent
   novelty without a new identifiable failure and action.

## Prospectively frozen candidate screen

Axes are clinical importance, target identifiability, residual novelty, asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence and ISBI schedule fit.  Admission requires total >=32
and the existing non-compensatory critical floors.

| Candidate | Axis scores | Total | Decision |
|---|---:|---:|---|
| Ostium segmentation with SynVA pretraining | 4.0 / 5.0 / 0.5 / 1.0 / 4.0 / 5.0 / 5.0 / 3.0 | **27.5** | Reject: source paper already performs the task; release contract absent |
| Procedural intervention-effect audit | 3.5 / 4.0 / 1.0 / 1.0 / 4.0 / 5.0 / 5.0 / 3.0 | **26.5** | Reject: counterfactual/effect auditing is direct prior and action asset absent |
| Source-disjoint synthetic-pretraining utility | 4.0 / 3.5 / 1.5 / 1.0 / 4.0 / 5.0 / 4.5 / 2.5 | **26.0** | Reject: pooled split critique is evaluation, not a residual method; manifest absent |
| Morphology-support-calibrated synthetic curriculum | 4.0 / 3.0 / 1.5 / 1.0 / 4.0 / 5.0 / 5.0 / 2.5 | **26.0** | Reject: rare-support truth and released generator controls are unavailable |
| Synthetic-to-real hemodynamic pretraining | 4.5 / 1.5 / 1.0 / 0.5 / 4.0 / 5.0 / 5.0 / 2.0 | **23.5** | Reject: source explicitly disclaims hemodynamic construct validity |
| Patient privacy or membership audit | 2.5 / 5.0 / 0.5 / 1.0 / 4.0 / 5.0 / 2.5 / 3.0 | **23.5** | Reject: procedural samples have no patient training members |

No candidate is admitted.  In particular, the best row cannot be rescued by a
Point Transformer, GNN, diffusion model, curriculum or uncertainty head because
its residual novelty is 0.5/5 and its executable asset score is 1.0/5.

## Material re-entry contract

A fresh SynVA version may be reconsidered only if an official source supplies:

1. a versioned code and dataset landing page with an explicit license;
2. immutable file identities, sizes and checksums;
3. the exact 40k/10k synthetic split and the 100-case real split;
4. patient and source grouping for AneuX, IntrA and CMHA;
5. generator seeds and sampled procedural parameters per mesh; and
6. a residual question beyond the source paper's own synthetic-to-real utility
   experiment and generic leakage, artifact, curriculum and domain-adaptation
   methods.

Such a release would trigger a fresh source audit only.  It would not
automatically authorize payload access, P0, an architecture or GPU training.

No scientific server or scheduler was queried for this audit.  Future
gate-authorized execution remains restricted to `introai9` PBS, with no
login-node GPU command.  `junjinyong` remains excluded from access, query,
transfer, submission and monitoring.
