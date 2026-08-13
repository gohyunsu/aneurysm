# Changelog

## 2026-08-13 · introai9 preflight closes infrastructure, not science

- Administrator-reported recovery was followed by successful public-key login,
  an empty user queue, an enabled/running `coss_agpu` queue, exact cache size and
  SHA-256, readable storage and a readable Singularity 3.11.3 base image. No
  HDF5 array, validation/test field, GPU or scientific endpoint was read.
- The documented base image pins NumPy 2.1.2 and PyTorch 2.5.1 but lacks
  `h5py`. Submission was withheld. Activation schema v2 now additionally pins
  an `h5py==3.12.1` wheel and installs it with `--no-index --no-deps` into
  job-local temporary storage before the immutable evaluator starts.
- Final binary preflight also found that the base image lacks Git. No job was
  submitted. The host wrapper already checks a clean exact checkout; schema v3
  now passes only that verified SHA into the clean container and rejects a
  missing/different value. It also preserves and pins the superseded pre-attempt
  manifest with attempt count 0 and field read false.
- A subsequent exact wrapper dry-run rejected the renamed mount
  `h5py.whl` as an invalid wheel filename, again before qsub or field access.
  The wrapper now preserves the registered wheel basename inside the container.
- The scientific config, evaluator, 12 gates, family split, seed and thresholds
  remain byte-identical. Private activation manifest, field read and P0 attempt
  remain zero; `junjinyong` remains excluded.

## 2026-08-13 · the consolidated entry point passes public validation

- Exact consolidation source `b5fd69774e00cf58403c0a0fadfceba8b39fd3e4`
  passed Quality `31689617455` and Pages `31689616910`.
- Dependency-complete CI passed 609/609 tests, 115 protocol invariant groups,
  the README/site link and semantic graph, and browser JavaScript syntax.
- README/checker/research-data SHA-256 are `1cea2d86…46b2` /
  `2b080199…551` / `619e1ad5…9679`. This validates public presentation and
  guardrails; it creates no scientific result or execution authority.

## 2026-08-13 · the public entry point stops duplicating the history ledger

- Replaced the 2,598-line accumulated README with a 217-line current overview:
  task, data scope, claim boundary, evidence ladder, paper role and execution
  rules now appear once in a novice-readable order.
- Preserved every dated failure and superseded contract in this changelog, git
  history and the site's filterable History window rather than silently
  rewriting historical 0/11 states.
- Added semantic checks that cap the current README at 260 lines, require real
  P0 v3 0/12, no selected architecture and RF-C2's application-only role, and
  reject private server paths, stale current P0 wording or embedded dated
  changelog sections.
- Rechecked `tmp/kakaotalk` and `tmp/tistory`: modification dates remain
  2026-08-02 and SHA-256 remain `ad99ccdc…ab175d` / `6d50cb4a…c2b38`.
  No fresh team evidence, scientific-server action, experiment or claim opens.

## 2026-08-13 · latest-collision public evidence is green

- Froze scientific source `4f58f9f90cbad68b96058c1c84cb6817730ba69a` after
  Quality `31686226180` and Pages `31686225742` succeeded.
- Dependency-complete CI passed 609/609 tests and 115 protocol invariant
  groups. Local canonical protocol SHA-256 is
  `7e3e6a4f81189ea8f8364e36eb19c6a0f3341da43f4e806e68948eda55d12739`.
- This validation covers code, claim boundaries and the site graph. It does
  not activate a model, scientific result, server retry or paper claim.

## 2026-08-13 · latest collisions restrict the lead to application evidence

- Added PaNO as a direct collision for the broad field-error-versus-readout
  story, while preserving its June 2026 arXiv status rather than presenting it
  as peer-reviewed evidence.
- Added NOEM as a direct prior for hard-constraint neural-operator output
  transformations and a 2026 cardiovascular differentiable-ROM study as a
  direct prior for one-CFD repeated boundary-condition tuning.
- Retained 32.5/40 without increase only for the exact Aneumo-specific matched
  evaluation, mandatory learned-direct and analytic controls, and prospective
  100-new-family confirmation. RF-C2 is now explicitly an application
  adaptation rather than algorithmic novelty; no method name is active.
- Added a machine-readable collision contract, fail-closed tests, protocol
  invariant and detailed acceptance falsifiers. Corrected the current-facing
  residual-novelty audit from stale P0 0/11 to v3 0/12.
- No scientific server/scheduler query, cache-field read, transfer, PBS/GPU
  submission, result, model or paper claim was created. This is not an
  `introai9` recovery signal, and `junjinyong` remains prohibited.

## 2026-08-13 · ISBI contract is verified without overstating the legacy template

- Rechecked the official home page, author instructions and CFP. The archival
  deadline remains 26 October 2026 at 23:59 USA EDT; review is single blind;
  every technical table and figure must fit in the first four pages; and the
  optional USD 200 fifth page is restricted to ethics, acknowledgments/COI and
  references. The submission endpoint is still `Coming Soon`.
- Applied the stricter union of two official originality wordings: AURORA bars
  substantially similar concurrent conference, workshop and journal review.
- Downloaded the exact template link from the 2027 author page. Its archive
  README says `ISBI 2021 Paper Submission Templates`, despite the organizer
  link, and its URL is under the 2025 site. It is recorded as an
  organizer-linked legacy layout rather than a verified 2027-specific template.
- Verified that the private vendored `spconf` copy and upstream file have the
  same active LaTeX command stream. The private pre-evidence plan nevertheless
  uses `unsrt` instead of upstream `IEEEbib`; it is not a final-format or
  submission manuscript. The sealed manuscript and bibliography were not
  rewritten.
- Added a machine-readable venue contract, six fail-closed tests and a detailed
  audit. This changes no scientific gate: real P0 v3 remains 0/12 and no server,
  scheduler, PBS/GPU, model, result or claim opened.
- Exact source `67ccdd9…8aefbbf` passed Quality `31682965397` with the pinned
  NumPy/h5py/CPU-PyTorch runtime, 606/606 tests, 114 protocol invariant groups,
  site graph and JavaScript checks. Pages `31682964734` also succeeded.

## 2026-08-13 · whole-release Aneumo audit raises feasibility, not admission

- Exact scientific source `b06f83f…b25b68` is remote exact. Quality
  `31680411009` and Pages `31680410157` succeeded; public job `94384352300`
  reports every configured dependency, runtime, protocol, test, site-graph and
  browser-JavaScript step successful. This is source-integrity evidence, not a
  transient scientific result.
- Added a fail-closed public archive auditor and synthetic parser tests. It
  requires bounded HTTP 206 responses, enforces a 100 MB ceiling and reads ZIP
  headers/directories rather than nested scientific members.
- Audited all 1,000 public transient case archives at the pinned release using
  2,100 requests and 72,217,600 bytes. Exactly 966 cases have the complete
  documented cycle, 34 do not, 961 complete cases use the canonical wall name
  and five use noncanonical names. Every one of 40 base families has at least
  one complete usable case.
- Kept payload evidence separate: four selectively extracted, CRC-checked wall
  files expose three-component WSS; a complete case has byte-identical points,
  connectivity and offsets across two phases with changing WSS. This local
  evidence is not release-wide units or tangency evidence. Polygon faces,
  high-normal tails and missing explicit units remain target risks.
- Recorded two official-preprocessor hazards: a complete case can include
  `0.00` after a 100-cycle eligibility check, and five noncanonical wall names
  can be silently mishandled rather than rejected. These are required reader
  fixes, not novelty.
- Re-scored transient structure-faithful WSS from historical 28.0 to 30.0/40.
  It remains inactive below 32 because the licence, stable critical structures,
  independent-unit limit and strong matched baselines are unresolved. Steady
  response fidelity remains the sole 32.5/40 conditional lead at P0 v3 0/12.
  No server, scheduler, PBS/GPU, model, result or manuscript claim opened.

## 2026-08-13 · official Aneumo transient release reopens review, not a task

- Exact scientific source `86ad592…9c142` passed Quality `31675906790` under
  the pinned NumPy/h5py/CPU-PyTorch environment with 588/588 tests, 114
  protocol invariant groups, the site graph and browser JavaScript syntax.
  Pages `31675905793` also succeeded. These are source-integrity results, not
  transient target evidence or a steady P0 result.
- Froze official GitHub commit `701d53d…` and Hugging Face revision
  `f801ade…`. The public HF state contains 370 objects and 3.285 TB: 267
  numeric steady archives, 100 transient batch archives and three metadata
  files. The first transient batch is 14.53 GB.
- Used a 16 MiB ZIP64 tail-range probe instead of downloading that archive.
  Its outer directory has ten nested case ZIPs; inspected case 10 exposes an
  initial directory and 100 cycle directories, each with inlet, internal,
  outlet and wall files. No field value was interpreted.
- Reconciled released case IDs 1--1000 against `Connection.csv`: they span
  40 base generation families, not 1,000 independent anatomies.
- Audited the official transient code. Its geometry split overlaps all ten
  base families across train and test; its target is scalar WSS magnitude,
  not vector topology. It has one parser error, two declared missing model
  modules, no critical-point/worldline metric and data-dependent timestep
  truncation.
- Recorded the unresolved license conflict between the HF card's CC
  BY-NC-ND 4.0 and GitHub datasheet's CC BY 4.0 without making a legal
  conclusion.
- Re-scored structure-faithful transient WSS at 28.0/40. It is an inactive
  re-entry candidate, not a second lead. The existing steady response-fidelity
  direction remains the sole 32.5/40 conditional source lead at real P0 v3
  0/12. No payload staging, P0, method, model, server, PBS/GPU, outer test,
  result or paper claim opened.

## 2026-08-13 · current-facing evidence labels are synchronized

- Audited current-facing site and research-document summaries against schema
  11.9 without altering historical v1/v2 failure records.
- Corrected the live confirmation gate from v2 to inactive v3, including its
  mandatory direct-plus-power-law comparisons, bilateral field equivalence,
  four response contrasts and complete-row inference boundary.
- Replaced stale current `0/11` and private-path-unresolved wording with real
  P0 v3 `0/12` and the narrower truth: cache identity is resolved, while the
  private activation manifest and current container-readability verdict remain
  absent. Added a site semantic check that rejects v2-as-current confirmation
  markers. No scientific protocol bytes, server, cache field, PBS/GPU job,
  result, model or claim changed.

## 2026-08-13 · P0-v3 gains a separate fail-closed activation layer

- Found that the preserved historical PBS wrapper still invoked P0 v2 and
  that the documented separate v3 activation manifest had no implementation.
- Added a new activation runner without modifying the immutable v3 config or
  evaluator. A future private manifest must pin the public commit, immutable
  v3 hashes, runner and manifest hashes, exact cache and container, output root,
  verified external-change evidence and zero prior P0-v3 scientific attempts.
- Added a v3-only introai9 PBS wrapper fixed at 4 CPU, 16 GB and 0 GPU. It
  rejects dirty/different source, unreadable or hash-drifted private inputs,
  repeat attempts and any authority beyond train coordinates and velocity.
- Added seven dependency-light contract tests. No actual activation manifest
  was registered, no private path was published and no server, scheduler,
  transfer, PBS, cache, field, model, result or GPU was accessed. Real P0
  remains 0/12; the implementation does not authorize a retry.

## 2026-08-13 · exact Aneumo cache identity resolved; activation remains locked

- Recorded that a bounded private inventory resolves the cache identity and
  matches SHA-256 `9640b0ef…ab9`; exact path and infrastructure metadata remain
  private. HDF5 schema only was checked and array values were not read.
- Preserved P0 v3 instead of writing the path into its registered bytes. No
  activation manifest exists. One WSL attempt ended before the network because
  the Windows alias was unavailable; one Windows attempt was reset before any
  remote command, so current container readability and operational readiness
  remain no-verdict.
- Real P0 stays 0/12. No queue query, transfer, PBS/GPU job, field-array read,
  model, result or claim opened. `junjinyong` was never accessed.

## 2026-08-13 · schema 11.9 · P0 v3 closes the anchor-tangent loophole

- Preserved the unexecuted P0 v2 config and evaluator byte-for-byte. V2 skipped
  the nominal anchor while omitting undefined anchor interpolation and therefore
  did not independently test the anchor tangent used by the primary endpoint
  and proposed identity mechanism.
- Registered a deterministic negative control: with 5,000 family-cluster
  bootstrap replicates, v2 passed 11/11 while its omitted anchor-tangent median was
  `0.7987704542950331`. This is synthetic contract evidence, not a scientific
  finding.
- Added fail-closed P0 v3 with one non-compensatory anchor-tangent CI-lower
  ≥0.80 check. Smooth synthetic response passes 12/12; the anchor-kink control
  fails v3. V3 also states the independent unit directly as Aneumo generation
  family.
- Real P0 remains 0/12. No cache/field, scientific server, scheduler, PBS/GPU,
  model, outer test, result, or claim was accessed. Historical P1 and
  confirmation v1--v3 stay inactive; a fresh P1 version may be registered only
  after a real 12/12 v3 pass.

## 2026-08-13 · public Quality coverage v1 failed closed; v2 pins the full runtime

- The first changelog-only Quality run `31624153346` succeeded but discovered
  only 560 tests with 85 optional-dependency skips, while the scientific source
  had been validated over a 570-test discovery set.
- Coverage v1 source `96770ad…2ddcef` added NumPy/h5py. Quality
  `31624605016` preserved a useful failure: it discovered 561 tests but three
  now-active array checks errored because their shared scientific import also
  requires PyTorch. Installation itself passed; the protocol-test step failed.
- Coverage v2 pins NumPy 2.1.2, h5py 3.12.1 and CPU PyTorch 2.5.1 and verifies
  their versions before the contract suite. Exact v2 source
  `5d6f870…9c540` passed Quality `31625071586`: the log records all three
  pinned versions, 112 protocol invariants and 570/570 tests with zero errors.
  Pages `31625071537` also succeeded. No scientific contract, result or
  historical attempt was repaired.
- This is CI coverage hardening, not a P0 run, model experiment or scientific
  result. It changes no protocol threshold, field, split, seed, claim or
  execution authority.

## 2026-08-13 · residual-novelty and acquired-asset reuse reappraisal

- Re-screened the acquired holdings instead of requiring a perfect new
  dataset. Aneumo response fidelity remains the sole conditional application
  lead, but its effective score falls from historical 34.0/40 to 32.5/40 and
  residual novelty remains exactly at the 2.5/5 floor.
- Added NeurIPS 2024 interventionally consistent surrogates and the 2026
  six-case aneurysm dilation-response surrogate to the direct-prior lineage.
  General response preservation, perturbation-response prediction, multi-flow
  learning, GNN/equivariance/physics, derivative supervision and residual
  learning cannot be claimed as contributions.
- Restricted the residual paper identity to one conjunction: an observed
  Aneumo-specific field-error-matched response failure, a same-backbone exact
  identity-at-anchor mechanism, superiority to both learned direct and
  train-fitted power-law controls, and exactly 100 new-family confirmation
  excluding all historical 32.
- Rejected the same-holding alternatives: selective/UQ response surrogation
  30.5, mixed geometry×flow fidelity 30.0, new GNN benchmark 28.0,
  WSS/pressure response 25.5 and rupture-response phenotype 22.0. Synthetic
  deformation is not longitudinal growth, and the compact velocity cache is
  not relabelled as WSS, pressure or a clinical endpoint.
- Added a four-page ISBI role/deletion contract, claim–evidence matrix and
  consistent main-table/figure grammar to public and private planning. The
  manuscript and references remain byte-for-byte unchanged because RF-C1 is
  empty and real P0 remains 0/11.
- Exact scientific source `1cdc360…fb90e` passed Quality `31621343028` and
  Pages `31621342151`; final provenance head `d7e3acf…676a7d` passed Quality
  `31621602013` and Pages `31621600946`. Regression passes 570/570 with 112
  protocol invariants at `76dfe06a…2983fde4`.
- No scientific server, scheduler, transfer, PBS/GPU job or monitoring was
  used. Do not retry `introai9` before a verified external change and never
  access `junjinyong`.

## 2026-08-13 · schema 11.8 · confirmation v3 evaluator red-team

- Exact scientific source `9efe914…76157` passed Quality `31617703039` and
  Pages `31617702307`; local and remote main were exact at verification.
- Preserved v2 and superseded it before eligibility metadata, field or
  prediction access; no historical contract or result was repaired.
- Promoted train-fitted power law from field-competence check to a mandatory
  primary response comparator. Candidate must beat both power law and the
  same-backbone direct head on paired response and tangent error.
- Replaced one-sided field non-inferiority with bilateral ±2% field equivalence
  against both controls so better field accuracy cannot confound the claimed
  response-specific mechanism.
- Added a deterministic evaluator that derives every statistic from complete
  long-form error rows, rejects missing/duplicate/extra/nonfinite cells and
  requires bitwise-identical replicated analytic rows.
- Pinned shared-family SHA-256 counter bootstrap draws, rejection sampling and
  Hyndman--Fan type-7 quantiles. The figure ranks families by the weaker
  comparator and includes reference/direct/power-law/candidate panels.
- Synthetic negative controls reject learned-direct-only wins, minority-driven
  means, field-mismatch confounding, incomplete rows and analytic seed drift.
  They are software evidence, not Aneumo results.
- Dependency-complete regression passes 570/570 tests; protocol retains 111
  invariants at `d3d1d6d9…f6f763f6`. Real P0 remains 0/11 and no server,
  PBS/GPU, result or claim was opened.

## 2026-08-13 · schema 11.8 · confirmation v2 red-team

- Preserved v1 and superseded it before confirmation metadata, field or
  prediction access; no historical result was repaired or relabelled.
- Reconciled the verified 32-family compact holding with Aneumo's reported 427
  base geometries: 100 new families are a same-release expansion after excluding
  historical 32, not a search for another dataset.
- Added a prefield two-endpoint precision gate and complete
  `case-flow×2 model×5 seed` workload projection under the 40 GPU-hour cap.
- Defined the estimator as case log-error contrast → family/seed mean →
  100-family geometric mean and bootstrap. Both responses also require at least
  59/100 family wins so a minority of extreme families cannot create the claim.
- Subtracted Aneumo flow-diversity analysis and Hemo-MPO geometry+BC full-field
  learning as direct priors. Multi-flow conditioning and operator-component
  stacking are not novelty.
- Real P0 remains 0/11; no confirmation metadata, field, prediction, server,
  PBS/GPU, result or paper claim was opened.
- Dependency-complete regression passes 561/561 tests; protocol retains 111
  invariant groups at canonical SHA-256 `4e37a1d3…293b1a`.

## 2026-08-13 · schema 11.8 · confirmation and private ledger synchronized

- Exact scientific public source `d827452…` passed Quality `31610409552` and
  Pages `31610409674`; local and remote main were exact.
- Private planning head `b35a597…` is remote exact, PRIVATE and anonymously
  404. Manuscript and reference bytes remain unchanged.
- Scientific-server query, transfer, PBS/GPU submission and monitoring remain
  zero; real P0 is 0/11 and no paper claim is active.

## 2026-08-12 · schema 11.8 · independent confirmation fixed at 100 new families

- Replaced the under-specified “at least 50 untouched families” phrase before
  any confirmation metadata, field or prediction was read.
- The inactive template excludes all historical 32 compact families and fixes
  exactly 100 new families by field-blind SHA-256 order, all eligible cases and
  all eight flows, with no post-lock substitution or sample enlargement.
- Nodes, flows, cases and five frozen seeds are averaged within family before
  10,000 family bootstraps. Field non-inferiority, analytic competence and both
  response-superiority endpoints form a non-rescuing intersection–union pass.
- The primary figure must disclose candidate worst, typical and best families
  using matched coordinates, camera and a reference-derived colour range.
- The contract is non-authoritative and opens no manifest, metadata, field,
  prediction, server, PBS/GPU, outer test, result or claim. Real P0 stays 0/11.
- Dependency-complete regression passes 552/552 tests; protocol retains 111
  invariant groups at canonical SHA-256 `6851f372…5c2050`.

## 2026-08-12 · schema 11.8 · P1 v3 and private ledger synchronized

- Exact scientific public source `0f443c8…` passed Quality `31606655510` and
  Pages `31606655150`; the live site exposes the same-backbone directional
  falsifier and direct-prior boundary.
- Private planning head `bed6cb5…` is remote exact, PRIVATE and anonymously
  404. Manuscript/reference bytes remain unchanged and no paper claim is active.
- Scientific-server query, transfer, PBS/GPU submission and monitoring remain
  zero; real P0 is 0/11 and P1 remains unregistered.

## 2026-08-12 · schema 11.8 · direct priors narrow P1 to one directional mechanism test

- SC-FNO, Hemo-MPO and AB-GATr close the broad architecture-novelty story.
  GNN, SE(3) equivariance, physics loss, DeepONet and generic sensitivity
  supervision are direct-prior components, not contributions.
- Preserved unexecuted P1 v2 and added inactive P1 v3 before any model output or
  response endpoint. V3 holds an MIT-licensed LaB-GATr backbone fixed and
  compares only direct target-field output with the identity-preserving
  `v0 + log(q/q0) * residual` output map.
- Fixed the success direction prospectively. Both median co-primary endpoints
  require a positive stability lower bound, at least 10% residual-head error
  reduction and four of five positive seeds. Negative or mixed evidence closes
  the direction; it cannot be redescribed as a reverse mechanism.
- Hemo-MPO and AB-GATr remain source-only controls because the inspected public
  assets do not supply an executable exact reproduction contract. MLP,
  DeepONet and MeshGraphNet are descriptive, non-gating controls.
- Any post-P1 development requires a separate registration, at most two
  validation-only rounds, 80 additional GPU hours and fresh-seed or disjoint-
  split re-entry before confirmation. Real P0 remains 0/11 and no server,
  PBS/GPU, prediction, response metric or claim was opened.
- Dependency-complete regression passes 544/544 tests; the protocol retains
  111 invariant groups at canonical SHA-256 `d3b368f7…f8c02`.

## 2026-08-12 · schema 11.8 · P1 v2 and private ledger synchronized

- Exact scientific public source `8b288c0…` passed Quality `31601736993` and
  Pages `31601736273`; the live Overview and filterable history expose v2.
- Private planning head `83fc8861…` is remote exact, PRIVATE and anonymously
  404. Manuscript/reference bytes remain unchanged and no paper claim is active.
- Scientific-server query, transfer, PBS/GPU submission and monitoring remain
  zero; real P0 is 0/11 and P1 remains unregistered.

## 2026-08-12 · schema 11.8 · inactive P1 v2 closes five analysis loopholes

- Preserved unexecuted P1 v1 and created a separate non-authoritative v2 before
  any prediction or response metric was read.
- V2 jointly assigns three distinct checkpoints per model; duplicated or
  caliper-failing levels cannot be substituted. The median level's paired-
  response and tangent endpoints are co-primary; low/high levels are
  non-rescuing sensitivity checks.
- Defined response contrast direction and seed ties. Field competence versus
  power-law now requires a one-sided 95% family-bootstrap stability upper
  model/control log-error ratio no greater than `log(1.02)`.
- Removed v1's invalid exact-inference claim: overlapping cross-fit training
  sets preclude independent-family exact sign flipping, Holm p-values, nominal
  bootstrap coverage and formal power. P1 is a development screen only;
  confirmatory inference was historically reserved for ≥50 untouched families;
  the later inactive confirmation v1 supersedes this minimum with exactly 100
  new families and excludes all historical 32.
- No scientific server, PBS/GPU, model or claim was opened; real P0 is 0/11.
- Dependency-complete regression passes 536/536 tests; the protocol retains
  111 invariant groups at canonical SHA-256 `df65f22a…b5166d`.

## 2026-08-12 · schema 11.8 · inactive P1 and private ledger synchronized

- Exact public source `fdef095…` passed Quality `31597528606` and Pages
  `31597524201`; the deployed site exposes the six-cell primary contract.
- Private planning head `62f5664…` is remote exact and anonymously 404.
  Manuscript/reference bytes remain unchanged and no paper claim is active.
- Scientific-server query, transfer, PBS/GPU submission and monitoring remain
  zero; real P0 is 0/11 and P1 is still unregistered.

## 2026-08-12 · schema 11.8 · inactive P1 design hardened before P0 evidence

- Rechecked the official ISBI 2027 author page: single blind, four technical
  pages, optional paid nontechnical fifth page, 26 October 2026 deadline and
  `Coming Soon` submission endpoint are unchanged.
- Added a non-authoritative P1 template and validator. The template cannot
  execute or register itself while real P0 remains 0/11.
- Fixed a train-20-family cyclic 5-fold 12/4/4 fit/calibration/outer design.
  One mechanism-linked MeshGraphNet--DeltaPhi pair defines six primary cells;
  MLP/DeepONet pairs are secondary and non-gating. Matching uses response-blind
  25/50/75% iso-error levels, exact log(1.01) field equivalence, 10% response
  materiality, exact family sign-flip tests, Holm correction, five seeds and a
  160 GPU-hour ceiling.
- Historical validation/test and future confirmation families remain sealed;
  no server, PBS, GPU, model prediction, response metric or paper claim exists.
- Dependency-complete regression passes 526/526 tests and the protocol retains
  111 invariant groups at canonical SHA-256 `f963f06f…729cf`.

## 2026-08-12 · schema 11.8 · P0 v2 and private ledger synchronized

- Exact v2 source `5e431f8…` passed Quality `31594279674` and Pages
  `31594278998`.
- Private paper head `a2eedb4…` is remote exact, PRIVATE and anonymously 404;
  manuscript/reference bytes remain unchanged.
- Full regression is 516/516 with 111 invariants. Real P0 remains 0/11 and no
  result, method, model, GPU, outer test or claim is opened.

## 2026-08-12 · schema 11.8 · final pre-execution response-fidelity P0 v2

- Preserved unexecuted P0 v1 byte-for-byte after an 8× rank-preserving
  coordinate-half distortion passed its Spearman-only gate.
- Registered v2 with an additional coordinate-half magnitude gate: family-
  bootstrap symmetric-relative-difference upper CI ≤0.25. V2 has 11 checks.
- Hash the observed cache bytes instead of trusting a reported string and keep
  the frozen host cache path identical inside the container.
- Finalized pre-execution red-team. Any further metric or threshold change
  requires a new evidence version. Real P0 remains 0/11; no compute or claim.
- Full regression passes 516/516 tests; protocol retains 111 invariant groups
  at canonical SHA-256 `3e43a577…eb7a`.

## 2026-08-12 · schema 11.8 · tangent correction privately synchronized

- Corrected public source `7c48574…` passed Quality `31592497232` and Pages
  `31592496090`.
- Private paper head `b4e78f8…` is remote exact, PRIVATE and anonymously 404;
  manuscript/reference bytes remain unchanged.
- Full regression is 514/514 with 111 invariants. No real P0 endpoint, model,
  GPU, outer test or paper claim is opened.

## 2026-08-12 · schema 11.8 · pre-execution P0 tangent audit

- Found that same-location centered-difference comparison could be insensitive
  to an omitted center value on equally spaced flow stencils.
- Preserved the registered endpoint and 0.80 threshold, but corrected the
  evaluator to compare actual left/right one-sided tangents with the
  two-neighbour secant direction.
- Added a jagged-response negative control that must fail tangent agreement and
  the 0.35 interpolation-error bound; smooth response continues to pass.
- This is a prospective implementation correction before private-data access,
  execution or a scientific verdict—not threshold repair or result relabeling.
- Full regression passes 514/514 tests; protocol retains 111 invariant groups
  at canonical SHA-256 `635fcbd5…d773`.

## 2026-08-12 · schema 11.8 · implementation and private ledger synchronized

- Exact public implementation source `3332bf6…` passed Quality `31591274490`
  and Pages `31591274071`.
- Private paper head `bd71c81…` is remote exact, PRIVATE and anonymously 404;
  manuscript/reference hashes remain byte-for-byte unchanged.
- Full regression is 513/513 with 111 protocol invariant groups. This pin
  opens no real P0 result, P1, method, model, GPU, outer test or paper claim.

## 2026-08-12 · schema 11.8 · fail-closed P0 reference implementation

- Implemented the train-only aggregate Aneumo response-fidelity evaluator and
  a CPU 4/GPU 0 one-shot PBS wrapper without submitting it.
- Prevented trivial flow-order correlation by ranking families separately at
  each target flow before family-cluster bootstrap; the registered run retains
  5,000 replicates and exactly ten checks.
- Enforced 4,096 aligned nodes, frozen family/case mapping and aggregate-only
  output; pressure, identifiers, validation/test fields, model artifacts and
  GPU remain excluded.
- Added fail-closed tests proving the current non-executable config rejects
  before private-cache access. No server, scheduler, transfer, PBS or GPU
  action occurred and no scientific result or paper claim was created.
- Full dependency-complete regression passes 513/513 tests; protocol validation
  retains 111 invariant groups at canonical SHA-256 `fa6fb500…cab1`.

## 2026-08-12 · schema 11.8 · public/private/site synchronization

- Expanded the public Overview from the rejected AneuX hero to the current
  Aneumo response-fidelity thesis, conditional architecture, falsification
  sequence and evidence-locked RF-C1--RF-C3 paper blueprint.
- Scientific source `6512dfb…` passed Quality `31587974877`; Overview head
  `fc12db9…` passed Quality `31588829344` and Pages `31588828745` and is live.
- Private paper head `82dd511…` records the ISBI page, claim, experiment and
  table contracts while preserving `paper/main.tex` and references byte for
  byte. Anonymous repository API returns 404.
- Full local regression is 505/505 in the dependency-complete environment;
  protocol validation reports 111 invariant groups. No scientific server,
  transfer, PBS/GPU job or monitoring was used.

## 2026-08-12 · schema 11.8 · response-faithful Aneumo direction

- Re-screened acquired assets and admitted one conditional application lead at
  34.0/40: field-error-matched multi-flow response fidelity. Residual novelty is
  exactly the 2.5/5 floor; no architecture name contributes to the score.
- Registered a train-only, CPU-only, non-executable P0 contract and evaluation
  primitives for response, tangent, curvature, gain and direction. Eight
  numerical unit tests pass in the dependency-complete environment.
- Preserved the failed V1e geometry-only result and historical scaling aggregate
  without repair or recomputation. Validation/test fields, model, GPU, outer
  test, result and paper claim remain closed.
- Updated protocol, ISBI four-page claim–evidence plan, dataset/server guidance,
  beginner documentation and public change history. No scientific server was
  queried and no data were transferred.

## 2026-08-12 · Schema 11.7 is scientifically and privately pinned

- Exact scientific source `3bad0861aa46a32855e5868811473f45fd0e57f1`
  passed Quality `31584127030` and Pages `31584126536`.
- Private paper ledger `2323d7f18c6d71a160374f63608a8095c577090f` is
  remote exact, PRIVATE and anonymously returns 404; manuscript/reference
  hashes are unchanged.
- Full regression passes 486 tests: 420 pass/66 optional-dependency skip, with
  110 machine-protocol invariant groups. Site links, anchors, assets and
  browser JavaScript pass.
- No scientific server, transfer, PBS/GPU job or monitoring action occurred;
  active lead, experiment, model, result and claim remain zero.

## 2026-08-12 · AneuX reliability candidate closes before execution · schema 11.7

- Preserved the schema-11.6 33.0/40 screen and both frozen P0 configs without
  relabelling or repair.
- Added a fresh six-way direct-prior screen. The best AneuX factorized
  reliability row is 32.0/40 but residual novelty is 2.0/5, below the fixed
  2.5 floor, so all rows are rejected.
- Recorded direct collisions from AneuX cut robustness, AneuX dome/cut1
  PointNet++, DiffusionNet, perturbation-based radiomics reliability and
  preprocessing multiverse analysis.
- Recorded pre-execution contract defects: the code does not implement
  source-qualified patient/lesion identities and does not require one connected
  open surface. No v3 is created because scientific admission already fails.
- Reset active lead, P0/P1, method, model, GPU, outer test, result and claim to
  zero. No scientific server was queried and `junjinyong` remained untouched.

## 2026-08-12 · Schema 11.6 is deployed and privately pinned

- Exact scientific source `4dfe08f35934901de5bc8d88a06869a1a5230998`
  passed Quality `31579905965` and Pages `31579905336`.
- Private ledger `b32d0c8f9ce7660d5033c6534b99e5dd0c51d9fc` is remote exact,
  PRIVATE and anonymously returns 404; manuscript/reference bytes are unchanged.
- Full regression passes 486 tests: 420 pass/66 optional-dependency skip. The
  public Quality workflow now explicitly validates P0 v2 in addition to the
  targeted/unit protocol suite.
- This provenance creates no executable P0, method, architecture, result, GPU,
  outer test or manuscript claim. No scientific server was queried.

## 2026-08-12 · AneuX P0 is corrected before execution · schema 11.6

- Verified that the released 170 morphometrics are `area-005` only; the v1
  tabular probe therefore could not identify cross-resolution instability.
- Pinned official `hirsch-lab/aneuxdb` head `a6b355e…`: README, MIT license and
  figures only, with code publication still in progress. Multi-resolution
  official feature recomputation is not treated as available.
- Preserved v1 byte-for-byte at SHA-256 `b82e3606…` as an unexecuted,
  pre-result superseded contract. It saw zero data rows, submitted zero jobs
  and evaluated zero endpoints; historical job `115177` remains untouched.
- Added P0 v2 and a fail-closed validator/aggregate metric implementation. V2
  fixes a deterministic 11-feature surface signature, canonical area-005
  nested cross-fitting, exact patient bootstrap, AUROC adequacy and two
  threshold-free primary materiality checks. Decision flip is secondary.
- Added synthetic tests for config immutability, probability range, orbit-mean
  Brier residual, tied-rank Spearman, AUROC, true clustered-bootstrap
  multiplicity, exact triangle moments, planar subdivision, rigid invariance,
  scale behavior and non-manifold/closed-surface rejection.
- Full regression passes 486 tests: 420 pass and 66 optional-dependency skip.
  The initial unrestricted run failed only because the sandbox made every
  temporary directory read-only; the repository-local approved run passed.
- No scientific server, transfer, scheduler, PBS/GPU, external source or outer
  test was accessed. V2 is non-executable pending exact private path,
  immutable manifest and reader preflight after an external service change.

## 2026-08-12 · Schema 11.5 is deployed and privately pinned

- Exact scientific source `5208bd2afb2e90894de3add5cc720c7f760a5a27`
  passed Quality `31576238532` and Pages `31576237547`.
- Private ledger `41cb0279ab911390929c5d9285827ea689414a98` was pushed and
  remains anonymously invisible; manuscript/reference bytes are unchanged.
- Full regression passes 474 tests: 408 pass/66 optional skip, 109 protocol
  invariants, source-watch v21, site graph, JavaScript and diff hygiene.
- This provenance creates no executable P0, method, result, GPU, outer test or
  manuscript claim.

## 2026-08-12 · AneuX nested orbit becomes the sole conditional ISBI direction

- Re-screened six research formulations that use already acquired/audited
  assets. AneuX factorized nested preprocessing-orbit reliability is the only
  row that passes the 32/40 total and every non-compensatory critical floor,
  scoring 33.0/40.
- Separated fixed-cut resolution nuisance from cut-dependent parent-vessel
  context. Flat final-logit consistency is prohibited as the proposal because
  it can erase a legitimate information-set difference.
- Registered a new method-free CPU P0 scientific contract with three patient-
  bootstrap failure endpoints and a two-of-three gate. Exact private path and
  manifest are unresolved, so the execution envelope is not frozen and no job
  was submitted.
- Preserved historical job `115177.ECE-util1` as 0/13 no-verdict without
  downloader repair or rerun. Primary problem, method, architecture, GPU,
  outer test and paper claim remain 0.
- Rebuilt the site entry narrative, detailed beginner explanation,
  architecture hypothesis, experiment gate, paper claim matrix and filterable
  history around the conditional direction.

## 2026-08-12 · Schema 11.5 separates acquired holdings from active assignment

- Corrected the misleading statement that no verified research data existed.
  Six named historical holding records are preserved: Aneumo, BenchAnXplore,
  CMHA, AneuX, AneuG-Flow and Aneurisk.
- Added an authoritative four-layer ledger: official source/release, historical
  payload or holding audit, current `introai9` exact-path inventory, and active
  train/validation/test assignment.
- Recorded exact non-admission classes rather than one blanket rejection:
  performance failure, asset-linkage failure, execution-incomplete/no-verdict,
  task mismatch, controlled access, discovery reuse and active-assignment zero.
- Current server persistence remains unresolved after the incomplete listing;
  active train/validation/test remains 0/0/0 because no prospective paper split
  is selected. No historical job was repaired or relabelled and no compute was
  opened.

## 2026-08-12 · Schema 11.4 deployed and privately pinned

- Exact scientific source `423cf18c14f506d46561592f8fa4ca2a78d51c9a`
  passed Quality `31571433278` and Pages `31571433150`.
- Private ledger `a1997946a38644f218b352e32b76d9fda60b06dc` is remote exact,
  PRIVATE and anonymously returns 404; manuscript/reference bytes are unchanged.
- Full regression passes 472 tests: 406 pass/66 optional skip, 107 protocol
  invariants, source-watch v21, site graph, JavaScript and diff hygiene. This
  provenance creates no active dataset, method, result, compute or paper claim.

## 2026-08-12 · Schema 11.4 separates an open clinical table from an active imaging dataset

- Verified Zenodo 17339029 revision 6: one CC-BY-4.0 XLSX, 39,686 bytes,
  linked to 230 actual aSAH patients. The payload was not downloaded or opened.
- Kept medical imaging, image–row join and fixed target time separate from
  file availability. The source substitutes discharge or 3-month mRS for 70
  patients without 6-month mRS.
- Rejected six candidates at 29.5/28.0/27.0/27.0/26.0/25.5. Active dataset,
  problem, P0/P1, method, model, result, claim and GPU remain zero.
- Added fail-closed source-watch v21 with 34 exact public states. A change can
  request re-audit only; it cannot download data or authorize compute.
- Added a detailed beginner-facing site chapter and filterable change entry.
  Full regression passes 472 tests: 406 pass/66 optional skip and 107 protocol
  invariants. Protocol SHA-256 is
  `0a9ccadb4841715a761188e209329bc468c5fe5631f0d1cc81e9086b82bf6645`;
  source-watch v21 SHA-256 is
  `ab34cf2b69e44877270250e1421eec057411a3a0a108c567bc8a22bf9a483dbb`.

## 2026-08-12 · Schema 11.3 records an incomplete introai9 inventory

- Attempted a user-authorized, read-only inventory on both documented
  `introai9` login boundaries; both exposed TCP/22 and one explicitly completed
  public-key authentication.
- Obtained no remote shell or SFTP listing because session opening timed out.
  Presence and absence are both unresolved; authentication is not an asset.
- Preserved the prior bounded fact that `/home/introai9/AAAI` and aneurysm
  traces existed while IntrA was only a repository skeleton with unverified
  mesh payload. Current-direction verified train/validation/test cases remain 0.
- Submitted no PBS job, queried no scheduler, used no GPU, transferred no file
  and did not access `junjinyong`. A future retry requires an external service
  state change and exact paths, not recursive repair or broad search.
- Full regression passes 470 tests: 404 pass/66 optional skip and 105 protocol
  invariants. Protocol SHA-256 is `c4a226aaa12f6285aef0e584118b833a83bcf8aa9540ca26bf2a89e0e59c473b`.
- Private ledger `46ef9ff1fbb3880b552c06a964007611aac16925` is remote exact,
  PRIVATE and anonymously returns 404; manuscript and references are unchanged.
- Exact scientific source `6f276cab968b073a297bd61c21d01bde4758b227`
  passed Quality `31567525126` and Pages `31567524764`.

## 2026-08-12 · Schema 11.2 rejects an unobserved mechanics–response–outcome join

- Audited six fresh primary sources spanning virtual coil mechanics,
  injection-standardized QA/6-month occlusion, longitudinal growth CFD,
  amplified-MRI wall motion, semi-automated initiation CFD and particle
  transport.
- Kept source-reported `R²`, AUROC and association results separate from
  AURORA evidence. Synthetic geometry/configuration counts are not patients.
- Rejected six candidates at 27.5/25.5/24.0/23.5/23.0/22.5. The conceptually
  novel mechanics→outcome row fails because no public same-patient geometry–
  device–immediate-response–fixed-time-outcome join exists.
- Added no source watch because no stable versioned release endpoint was found.
  No payload, P0/P1, method, architecture, scientific server, PBS/GPU, outer
  test, result or paper claim opened; surface-vector `115645` stays unrepaired.

## 2026-08-12 · Schema 11.1 deployed and privately pinned

- Exact scientific source `9206415e43bd85cf4e592cf81005bc1b34851465`
  passed Quality `31563336315` and Pages `31563336017`.
- Private ledger `94da161d8de3589336aae5f0d0232c68814a3942` is remote exact,
  PRIVATE and anonymously returns 404; manuscript/reference bytes are unchanged.
- Full regression passes: 468 tests, 402 pass/66 optional skip, 103 protocol
  invariants, site graph, JSON, JavaScript and diff hygiene. This provenance
  creates no task, model, compute, result or paper claim.

## 2026-08-12 · Schema 11.1 separates TopAneu registered design from release

- Pinned the official MICCAI registry/Zenodo design, live Data page and exact
  Git/evaluator state without joining the challenge or opening medical payload.
- Separated planned 500 train/350 private test, 200 public-source train and
  50/20 gold vessel masks from realized 417 scans/409 patients, public-source
  count 68 and organizer-predicted vessel masks.
- Rejected six candidates at 31.5/30.5/27.5/26.5/26.5/20.5. Best residual
  novelty is 0.5/5; there is no active task, P0, model, GPU or paper claim.
- Reused source-watch v20 because it already freezes the exact design record and
  challenge route. Historical TopAneu scores and surface-vector job `115645`
  remain unchanged and unrepaired.
- Full local regression passes: 468 tests, 402 pass/66 optional skip, 103
  protocol invariants, JSON/JavaScript, site links/assets and diff hygiene.

## 2026-08-12 · Schema 11.0 deployed and privately pinned

- Exact scientific source `b7ef613ee6ac906ba23bdf5df29e51b59ac66899`
  passed Quality `31561077612` and Pages `31561073271`.
- Private ledger `b33a5cc82c61eb1b1da5236b363441be0951b1ad` is remote exact,
  PRIVATE and anonymously returns 404; manuscript/reference bytes are unchanged.
- Full regression passes: 467 tests, 401 pass/66 optional skip, 102 protocol
  invariants, site graph, JSON, JavaScript and diff hygiene. This provenance
  creates no task, model, compute, result or paper claim.

## 2026-08-12 · Schema 11.0 rejects collision anticipation before payload or compute

- Separated current-frame contact detection from a prospective pre-contact
  warning estimand. A valid warning needs first-contact onset, fixed horizons,
  complete negative sequences and procedure/specimen-grouped confirmation.
- Froze exact CathAction revision `8b04056…`: four archives and
  56,678,352,136 used bytes, with human segmentation but no declared human
  collision archive or immutable action–mask–collision join. No form, terms or
  archive payload was opened.
- Rejected all six rows at 26.5/26.5/26.0/24.5/24.0/20.0. Source-watch v20
  adds one review-only state for a total of 33 and authorizes no P0, model or
  compute.
- Retained surface-vector only as an inactive question and kept job `115645`
  immutable at E/exit 2, GPU 0, 0/10 and no scientific verdict.

## 2026-08-12 · Schema 10.9 deployed and privately pinned

- Exact scientific source `3a9fa3a1a3146457b7d0e8215db66ee26d5532ac`
  passed Quality `31559316259` and Pages `31559316027`.
- Private ledger `a4711543c245fb60617ec8975c4b94923400a3fd` is remote exact,
  PRIVATE and anonymously returns 404; manuscript/reference bytes are unchanged.
- Full regression passes: 465 tests, 399 pass/66 optional skip, 100 protocol
  invariants, site graph, JSON, JavaScript and diff hygiene. This provenance
  creates no task, model, compute, result or paper claim.

## 2026-08-12 · Molecular biomarker and treatment-specific outcome reappraisal

- Audited PXD024615 as patient-level serum proteomics: 212 discovery samples
  and a 32-sample external cohort. Its source already owns IA/control and
  rupture-state classification; sampling-time rupture is not a future event.
- Distinguished PXD013442's four pooled discovery mixtures from its 20 stated
  donors, and kept GSE231922's 30 samples as a small mechanism source.
- Classified NBC-GARUDA as internally bootstrapped treatment-specific
  prognosis, not counterfactual clipping-versus-coiling evidence.
- Rejected all six rows at 31.0/28.0/27.0/27.0/26.0/23.0. No payload, model,
  server query, PBS/GPU work or claim opened; surface-vector stays inactive.

## 2026-08-12 · Schema 10.8 deployed and privately pinned

- Exact scientific source `6b153b7f988e2d1c6fe9def294a6348849a4c53a`
  passed Quality `31557448461` and Pages `31557447516`.
- Private ledger `e4c3f8f5b3d908d2be418e1506cacbb6cdbac5d9` is remote exact;
  manuscript and references remain byte-for-byte unchanged.
- This provenance-only entry creates no task, method, model, result, compute or
  submission authority.

## 2026-08-12 · Structured-vessel and embargoed 4D-flow reappraisal

- Bounded exact-public audit found 20 masks in the inspected VeNet Git state,
  not a joined 200 image–mask benchmark or independent test. The paper itself
  flags topology discontinuity/topology-aware loss, narrowing residual novelty.
- RSNA multi-task learning already occupies the tri-axial ROI, 3D multi-task and
  pseudo-label route; its series-level split does not explicitly establish
  patient grouping. No leakage claim is made.
- CMRx4DFlow data are controlled and embargoed beyond the ISBI deadline. The
  open device phantom has eight acquisitions but one base anatomy.
- Rejected all six candidates at 27.5/27.0/27.0/26.5/26.0/21.0. Added
  source-watch v19 (32 states). No terms, payload, P0, model, server or compute.
- Full regression passes: 464 tests, 398 pass/66 optional skip, 99 protocol
  invariants, site graph, JSON, JavaScript and diff hygiene. Protocol canonical
  SHA-256 is `b4c4f18a…`; source-watch v19 is `911fa8b3…`.

## 2026-08-12 · ADAM-fold audit deployed and privately pinned

- Exact public scientific source `836293006a835c421aac474c668387daeb659f77`
  passed Quality `31555748252` and Pages `31555747611`; the live Overview,
  beginner chapter, exact audit and source-watch v18 were verified.
- Private ledger `25b10dec320f58528702fad23d8bde232e111e65` is remote exact
  and anonymously returns 404. Manuscript and reference hashes are unchanged.
- This provenance-only synchronization opens no active problem, method, model,
  compute, result or manuscript claim.

## 2026-08-12 · ADAM patch-fold release and segmentation-prior reappraisal

- Froze GitHub release v1.0 as 35 assets/61,506,611,200 bytes with canonical
  name/size/digest manifest SHA-256 `7d5ebe80…`; no archive body was accessed.
- The public JSON contains 93 positive scan IDs/58 bases, no validation IDs or
  negative controls. Under official ADAM B/F semantics, development/test base
  overlap is 2/3/5/6/2 across folds.
- Added DINO-3DRA and GeoP2VNet as code-level direct-prior controls, not
  peer-reviewed or AURORA-reproduced results. Rejected all six fresh candidates
  at 26.5/26.5/26.0/25.5/23.0/23.0.
- Added source-watch v18 with 31 exact states and release-asset-manifest change
  detection. It may request review only; no download, P0, method or compute.
- Full regression passes: 462 tests, 396 pass/66 optional-dependency skip,
  97 protocol invariant groups, site/JSON/JavaScript/diff hygiene. Protocol
  SHA-256 is `232bc58b12678481dbe9b89b1738f8ca284a88b93768a832208a481c32f05e98`;
  source-watch v18 SHA-256 is
  `ab69bca79ba70d8b6543dbcc1e11d9091eaef201f0da61a6f29fa26320d7cf00`.

## 2026-08-12 · Surface-vector/DSA audit deployed and privately pinned

- Exact public scientific source `cb4f6b16183ddd10a3982edbbdabf77d8a0a3808`
  passed Quality `31553310905` and Pages `31553310384`; the live beginner
  chapter, exact audit, machine protocol and source-watch v17 were verified.
- Private ledger `b708bc2581042d83e323c905035966a1047333bb` is remote exact,
  PRIVATE and anonymously returns 404. Manuscript and reference hashes are
  unchanged.
- This provenance-only synchronization opens no active problem, method, model,
  compute, result or paper claim.

## 2026-08-12 · Surface-vector and task-faithful sparse DSA delta · no state change

- Retained field-error-versus-structure as a falsifiable hypothesis, but made
  material source change mandatory for re-entry. A fresh label, wrapper,
  parser, cache, timeout or seed cannot reopen historical job `115645`.
- Corrected the proposed architecture contract: exact point/worldline
  extraction is evaluation-only before stability, and boundary-margin signed
  total degree with abstention precedes individual-feature endpoints.
- Added SAVE-Net, dual-centre DSA TransUNet and semantically conditioned
  synthetic DSA to the direct-prior lineage. DIAS remains the wrong endpoint
  contract for acquisition/dose/aneurysm-biomarker claims.
- Rejected six DSA formulations at 26.5/26.5/26.0/25.5/24.5/23.5. No
  payload/request, E0/P0/P1, method, architecture, scientific-server query,
  PBS/GPU, outer test or claim opened.
- Added source-watch v17 with embargoed Zenodo 21104782 revision 4 as the 28th
  review-only state, a detailed audit, machine invariants, beginner site window
  and filterable history entry.
- Full regression is 460 tests: 394 pass/66 optional-dependency skip with 95
  machine-protocol invariant groups; site, JSON and JavaScript checks pass.

## 2026-08-12 · Pose/operator audit deployed and privately pinned

- Exact public scientific source `8910e1b0f8148b45732493998983577d339ecdfd`
  passed Quality `31551588925` and Pages `31551587888`.
- Private ledger `e26dadb61acf5b1268ad8d7f8f4943b6fb42cffe` is remote exact,
  PRIVATE and anonymously returns 404. Manuscript and reference hashes are
  unchanged.
- This provenance-only synchronization opens no active problem, method, model,
  compute, result or paper claim.

## 2026-08-12 · Pose/workflow and spatiotemporal-operator source reappraisal

- Audited DeepAnePose exact `40042fa…`: 270 selected subject/session IDs, 140
  positive JSONs, 164 lesions and five patient-wise folds, with no explicit
  validation split, tracked checkpoint or repository license file.
- Added Graph Physics `e4ac523…`, Aneumo WSS Transolver `3087fc9…` and EXPIGEO
  `b287368…` to the direct-prior lineage. Derived steady WSS magnitude is not a
  transient tangent-vector/worldline reference.
- Rejected six candidates at 29.0/28.5/27.0/26.0/25.5/21.5. The proposed
  edge-1-form/Hodge/equivariant/periodic stack remains a control family only;
  no active problem, model or compute opens.
- Added source-watch v16 with 27 fail-closed states, machine protocol
  invariants, detailed audit, beginner-facing site chapter and filterable
  history entry. No scientific server, transfer, PBS/GPU or manuscript claim
  was touched.
- Full regression is 458 tests: 392 pass/66 optional-dependency skip with 93
  machine-protocol invariant groups. Site, JSON/JavaScript and diff hygiene
  checks pass; team-source hashes are unchanged and no post-2026-08-02 team
  conversation was found.

## 2026-08-12 · Surface-vector finite closure deployed and privately pinned

- Exact public scientific source `a9d79f0446041555585a73f0fc7ed9a0cd990514`
  passed Quality `31549386632` and Pages `31549386364`; the live site exposes
  the finite closure, re-entry contract and filterable change record.
- Private ledger `e8db8078f8c025b2715a4ee59fa5ff6aadea596c` is remote exact,
  PRIVATE and returns 404 to an anonymous API request. Manuscript and reference
  hashes are unchanged.
- Full regression is 456 tests: 390 pass/66 optional-dependency skip and 91
  protocol invariant groups. This provenance-only pin opens no scientific or
  submission authority.

## 2026-08-12 · Surface-vector finite closure and source-watch v15

- Accepted the scientific distinction between field accuracy and stable flow
  organization, but rejected architecture-first activation. The current asset
  family is now explicitly closed until a whitelisted material release.
- Reconfirmed AneuG `9dd4180…`, Aneurisk revision 4, AneuX `38c574b…`,
  AAA-WSS `2f78bf1…` and unavailable TRELLIS. The only observed Synthetic-AAA
  change from release `98363a0…` to main `7872b81…` touches README/CITATION
  metadata only; no generated cohort or transient fields were added.
- Added a finite re-entry whitelist and E0--E5 ladder. A README/DOI edit,
  wrapper, timeout, parser, cache, seed or locally generated synthetic set is
  not fresh evidence. Source-watch v15 freezes 24 public states and remains
  manual-review-only.
- Preserved `115645.ECE-util1` as E/exit 2, GPU 0, 0/10 no-verdict history.
  No payload, P0/P1, model, scientific server, PBS/GPU, outer test or claim
  opened; schema 10.7 and the current aSAH batch are unchanged.

## 2026-08-12 · Longitudinal-biology delta deployed and privately pinned

- Exact public scientific source `0cadda2cf03144f2e876862a727714858999b56c`
  passed Quality `31547562160` and Pages `31547561485`; live Learn exposes
  `#biology-chain`, the exact detailed audit and filterable change history.
- Private ledger `6189db9532203207d411e8983dcd8586cbe8efc4` is remote exact,
  PRIVATE and returns 404 to an anonymous API request. Manuscript and reference
  hashes are unchanged.
- Full regression is 451 tests: 385 pass/66 optional-dependency skip and 89
  protocol invariant groups. This provenance-only pin opens no scientific or
  submission authority.

## 2026-08-12 · Longitudinal biology and cross-scale mechanism delta · no state change

- Corrected the scope of the current evidence: genuine future follow-up exists
  in a two-centre 198-patient/224-aneurysm AWE study, but the source already
  owns the association with composite instability and exposes no versioned
  public patient/image/event/split artifact.
- Separated the 308-patient/416-aneurysm cross-sectional AWE cohort, the
  80/85 growth cohort and UK Biobank incident-aSAH analysis. Their aligned
  associations do not identify same-patient inflammation--AWE--growth--aSAH
  mediation.
- Recorded the 13-induced/6-control serial rat MRA study, its five early deaths,
  reported 40%/60% sensitivity/specificity and 0.146-mm versus ≤0.10-mm
  resolution failure. Request-only animal data are not a public human
  progression benchmark.
- Froze six candidates at 28.5/26.5/25.0/23.0/22.5/20.0. All fail a mandatory
  novelty, asset, unit or identifiability floor. Schema 10.7 and the current
  aSAH primary batch are unchanged; no payload, request, P0/P1, method,
  architecture, scientific-server query, PBS/GPU, outer test or claim opened.

## 2026-08-12 · Rupture-time delta deployed and privately pinned

- Exact public scientific source `309e16205a82f1fe7599a24719486da40375193d`
  passed Quality `31545461242` and exact-head Pages `31545766452`; the live
  Learn anchor and exact detailed audit were verified.
- Private ledger `7fb0fccb002763c2827d46b5c2186af53893ca2b` is remote
  exact, PRIVATE and returns 404 to an anonymous API request. Manuscript and
  reference hashes are unchanged.
- Full regression is 450 tests: 384 pass/66 optional-dependency skip and 88
  protocol invariant groups. This provenance-only pin opens no scientific or
  submission authority.

## 2026-08-12 · Rupture-state/future-risk and patient-unit delta · no state change

- Added the three-centre QIMS source: 756 patients/877 aneurysms, reported
  314/136 centre-I aneurysm rows and two external-centre sets. Separated its
  observed rupture-status target from a prospective future-event estimand and
  marked patient grouping as unresolved rather than asserting leakage.
- Kept source AUC 0.887/0.910/0.773/0.735 as unreproduced paper results and
  identified admission glucose as unavailable to a pure pre-event planner in
  already ruptured presentations.
- Pinned PLOS Figshare `28661913` metadata: one CC-BY-4.0 5,632-byte aggregate
  `Table 1.xls`, not patient rows, raw CTA or longitudinal follow-up. Its body
  and all patient payload remain unopened.
- Froze six candidates at 27.5/27.0/25.5/25.0/24.0/23.5. All fail a mandatory
  target, novelty, asset or independent-unit floor. Schema 10.7 and the aSAH
  primary decision are unchanged; no request, P0/P1, method, architecture,
  scientific-server query, PBS/GPU, outer test or claim opened.

## 2026-08-12 · RSNA/WEB-GAN delta deployed and privately pinned

- Exact public scientific source `445e3dc90abffad9e00bf0b1069acc949d66f536`
  passed Quality `31543772897` and Pages `31543771957`; the live Learn anchor
  and detailed audit were verified.
- Private ledger `827ae95026409f62eba988ebc0ec80a02003c94a` is remote
  exact, PRIVATE and returns 404 to an anonymous API request. Manuscript and
  reference hashes are unchanged.
- Full regression is 449 tests: 383 pass/66 optional-dependency skip and 87
  protocol invariant groups. This provenance-only pin opens no scientific or
  submission authority.

## 2026-08-12 · RSNA release-layer and WEB-GAN utility delta · no state change

- Separated the official RSNA launch corpus (>6,500 multimodal studies), AWS
  controlled registry collection (>4,000 CT scans) and second-place training
  count (4,348 series). No common unit, arithmetic split or release expansion
  is inferred without a public identity map.
- Pinned WEB-GAN article `10.1177/2997979X251369456` and exact public head
  `42ce2a8…`. Static code inspection shows the generator trained on the full
  78-case original table before the synthetic-trained predictor was evaluated
  on that same original donor table. The request-only original patient and
  institution data prevent a donor-disjoint reproduction.
- Froze six delta candidates at 29.0/28.5/26.0/25.5/24.5/23.0. All fail
  novelty or asset/unit floors. This is an evaluation limitation, not source-
  paper invalidation, an active paper identity or a reason to select a model.
- Added a full audit, machine invariants, a beginner-facing Learn window and a
  filterable site change entry. Schema 10.7 and the current aSAH batch are
  unchanged; no controlled payload, original patient data, scientific server,
  P0/P1, architecture, PBS/GPU, outer test or claim opened.

## 2026-08-12 · Surface-vector external-analysis delta review · no state change

- Accepted the exact closed-job, no-repair and staged-gate conclusions, but
  recorded that current public/shared `AGENTS.md` already showed job
  `115645.ECE-util1` as closed rather than running.
- Made the current architecture explicit: it is unselected, not GNN. Added
  In-PI-MGN/BenchAnXplore to the authoritative direct-prior contract for
  physics-constrained autoregressive transient aneurysm mesh GNNs.
- Preserved surface-vector as an inactive evaluation hypothesis. Schema 10.7,
  every score, source decision and the zero P0/P1/method/architecture/server/
  GPU/outer-test/claim boundary are unchanged; no server was queried and no
  experiment was opened.

## 2026-08-12 · Schema 10.7 scientific source deployed and privately pinned

- Exact scientific source `39b94a7c42d40c70c18fe76744349507bffb2ea8`
  passed Quality `31540996594` and Pages `31540995837`; live Overview, Learn,
  detailed audit and machine protocol expose the 29.0/40 novelty/joined-asset
  rejection and no-model/no-compute state.
- Private ledger `f04716e7c39f90a33fe76ccf677c4285a074819a` is remote exact.
  Manuscript and reference hashes are unchanged.
- Full regression is 448 tests: 382 pass/66 optional skip and protocol 86
  invariant groups; site and JavaScript checks pass. This provenance opens no
  P0/P1, method, model, compute or claim.

## 2026-08-12 · aSAH segmentation/outcome asset reappraisal · schema 10.7

- Froze exact Zenodo revision 2, official pipeline head `3fbd7a9…` and public
  multiclass baseline head `269f472…` in a fail-closed 23-source watch. No RAR,
  checkpoint or patient-level medical payload was opened.
- Separated an open NCCT/mask archive from a versioned image--mask--outcome
  join. Paper cohort counts are not treated as an archive manifest.
- Added the 2026 six-month-GOS volume-equivalence study, 3-month mortality,
  multiclass segmentation, LoRA/DoRA transfer and longitudinal SAHVAI as direct
  priors; none of their results is an AURORA result.
- Froze six candidates at 29.0/28.5/28.0/28.0/27.0/22.5. Every row fails
  residual novelty or joined-asset floors; no P0, model, server query or compute
  opened and surface-vector remains inactive.

## 2026-08-12 · Schema 10.6 scientific source deployed and privately pinned

- Exact scientific source `1f8ce3cf774b3a5562fbbc4c9ee5a48005056660`
  passed Quality `31537504625` and Pages `31537503585`; live Overview, Learn
  and machine protocol expose the 29.0/40 target/unit-floor rejection and
  no-model/no-compute state.
- Private ledger `3f510fabad9f19a5e3d01a288bbbd23996d23f73` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- Full regression is 443 tests: 377 pass/66 optional skip and protocol 84
  invariant groups; site and JavaScript checks pass. This provenance opens no
  P0/P1, method, model, compute or claim.

## 2026-08-12 · 4D-CTA wall-phenotype release reappraisal · schema 10.6

- Froze the exact DA_4DCTA Zenodo revision 4 and GitHub head `8df7d45…` in a
  fail-closed 20-source watch. No archive body or patient image was downloaded.
- Separated derived trajectory CSVs from source 4D-CTA, operative reference,
  registration, surface topology and patient/centre/fold semantics. Fifty-two
  visible directories are not asserted to be 52 independent patients.
- Added 2025–2026 dynamic repeatability and intraoperative phenotype direct
  priors. The source paper already owns trajectory-to-wall-phenotype prediction.
- Froze six candidates at 29.0/28.5/28.0/27.5/26.5/24.5. All fail total or
  mandatory target, novelty, asset or independent-unit floors; no P0, model,
  scientific-server query or compute opened.

## 2026-08-12 · Schema 10.5 scientific source deployed and privately pinned

- Exact scientific source `e69718448c85eedf4a4edad5c66fcd33ca791ff1`
  passed Quality `31534693949` and Pages `31534693040`; live Overview, Learn
  and machine protocol expose the 30.5/40 asset-floor rejection and
  no-model/no-compute state.
- Private ledger `529a38f30717d427b6b02f8f25e2962cd04b6ff0` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- Full regression is 438 tests: 372 pass/66 optional skip and protocol 82
  invariant groups; site and JavaScript checks pass. This provenance opens no
  P0/P1, method, model, compute or claim.

## 2026-08-12 · Culprit-lesion and mimic-differential reappraisal · schema 10.5

- Separated acute culprit, symptomatic-lesion, future-rupture and
  aneurysm--infundibulum targets rather than treating all rupture-related
  labels as interchangeable.
- Added the eight-hospital 272-patient/607-aneurysm CTA culprit study and the
  three-institution 30-patient/82-aneurysm VWI study as direct priors. Their
  source metrics are not AURORA results.
- Added the 285-patient smaller-counterpart and 665-outpouching infundibulum
  cohorts with bounded design/data-access interpretation. The public ICAN
  table is recorded as simulated, not patient evidence.
- Froze six candidates at 30.5/29.5/28.0/26.0/25.5/24.0. The best residual,
  haemorrhage-conditioned patient-set evidence alignment, fails the asset floor
  because no public NCCT--CTA--all-lesion--culprit-reference join was found.
- Added schema 10.5 protocol invariants, regression coverage, an exact audit
  and a beginner-facing site chapter. No data request, payload, P0, model,
  scientific-server query or compute opened.

## 2026-08-12 · Schema 10.4 scientific source deployed and privately pinned

- Exact scientific source `fb5fabce61cd6df53cd806538da86bbf81ec4f74`
  passed Quality `31532823553` and Pages `31532823420`; live Overview, Learn
  and machine protocol expose the 30.5/40 rejection and no-model/no-compute
  state.
- Private ledger `7522d43ee1cfb3c73cc914593e36b8d24ae3dfa6` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- Full regression is 437 tests: 371 pass/66 optional skip, protocol 81
  invariant groups, source-watch 18/18 exact and site/JavaScript checks pass.
  This provenance opens no P0/P1, method, model, compute or claim.

## 2026-08-12 · TopBrain 2025 and RSNA multitask source correction · schema 10.4

- Corrected the source ledger to distinguish the already public TopBrain 2025
  release from the future TopBrain 2.0 design record. Frozen exact Zenodo data
  revision 14, podium revision 18 and BraveCoWCoW Git head are now monitored by
  fail-closed source-watch v12; live read-only refresh matched 18/18 snapshots.
- Counted 50 public volumes as 25 same-patient CTA/MRA pairs and separated
  whole-brain vessel-anatomy labels from aneurysm targets. No custom terms were
  accepted and no patient/Docker/RSNA payload was opened.
- Added TopCoW and BraveCoWCoW as direct priors for paired-modality topology and
  multimodal ROI multi-task aneurysm learning. Pseudo-masks are not an
  independent expert-dense benchmark; public code is not controlled RSNA data.
- Froze six candidates at 30.5/29.0/27.0/25.0/25.0/24.5. All fail total or
  mandatory novelty/asset floors. Added schema 10.4 protocol invariants and
  source-watch tests; no P0, model, scientific-server query or compute opened.

## 2026-08-12 · Schema 10.3 scientific source deployed and privately pinned

- Exact scientific source `8d09d34ad2b05e1c65530811ede4d8aa5ada66ec`
  passed Quality `31525137390` and Pages `31525136523`; live Overview,
  Learn and the machine protocol expose the 27.0/40 rejection and
  no-model/no-compute state.
- Private ledger `7281f013695b8522cb901b75e397d50c7d5ddd3a` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- This deployment provenance opens no P0/P1, method, architecture, scientific
  server, PBS/GPU, outer test, result row, C21 or claim.

## 2026-08-12 · Target time and instability prediction rejected · schema 10.3

- Added the 852-patient/1,111-aneurysm seven-hospital pre-event radiomics study
  as a direct prior, including its source-reported six-hospital external AUCs.
- Added the 293-patient/312-aneurysm VWI habitat--deep Transformer study and
  separated its mixed prior/current/future instability components instead of
  treating the composite as one future-event target.
- Added NCT07111975 as a 3,800-participant, three-centre future direct prior,
  not a current result or public asset.
- Froze six candidates at 27.0/26.5/26.0/25.5/25.5/25.5. All fail total or
  mandatory asset/independent-unit floors; no P0/model/compute or paper identity
  opened.
- Added schema 10.3 machine invariants, regression coverage, an exact audit and
  beginner-facing target-time explanation. No scientific server was queried;
  `junjinyong` remains completely excluded.

## 2026-08-12 · Schema 10.2 scientific source deployed and privately pinned

- Exact scientific source `c6906134ad2cea6a7f1918edb2b515c95a9d0b41`
  passed Quality `31522903059` and Pages `31522901393`; live Learn and the
  machine protocol expose the 30.0/40 rejection and no-model/no-compute state.
- Private ledger `b66700864bd9f43d21ce8e1cff60d16f80a1d679` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- This deployment provenance opens no P0/P1, method, architecture, scientific
  server, PBS/GPU, outer test, result row, C21 or claim.

## 2026-08-12 · Decision-time and clinical-precision reappraisal · schema 10.2

- Added the 426-aneurysm/362-patient four-centre PED occlusion nomogram as a
  direct hemodynamic outcome prior, while distinguishing its random pooled
  aneurysm hold-out from centre-held-out external validation.
- Recorded the unresolved patient-dependence risk from 61 multi-aneurysm
  patients without claiming that cross-split leakage definitely occurred.
- Separated pre-operative CFD from immediate apposition and follow-up migration,
  preventing a post-deployment updater from being presented as a purely
  pre-operative treatment-selection model.
- Added the 148-patient/163-aneurysm commercial AI precision study: improved
  reproducibility did not yield DSA agreement within ±1 mm, and its
  cross-sectional design does not validate longitudinal growth.
- Froze six candidates at 30.0/26.0/25.5/25.0/24.5/23.0. All fail the total or
  mandatory novelty, asset and independent-unit floors; no P0/model/compute or
  paper identity opened.
- Added schema 10.2 machine invariants, regression coverage, an exact audit and
  a beginner-facing decision-time chapter. No scientific server was queried;
  `junjinyong` remains completely excluded.

## 2026-08-12 · Schema 10.1 scientific source deployed and privately pinned

- Exact scientific source `2abc73e07275e31ad87db3cf39b77864e1419322`
  passed Quality `31519811493` and Pages `31519810721`; live Overview, Learn
  and detailed audit expose the 26.5/40 rejection and no-model/no-compute state.
- Private ledger `8a9c1a905e715f0f47972a658528149620dfd6c9` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- This deployment provenance opens no P0/P1, method, architecture, scientific
  server, PBS/GPU, outer test, result row, C21 or claim.

## 2026-08-12 · Device planning and mechanistic occlusion rejected · schema 10.1

- Added NeurAneuNet as a direct prior for 3DRA-to-PED size/landing-zone planning
  and six-reader AI assistance, while bounding its endpoint to expert-consensus
  deployment adequacy rather than durable outcome.
- Added the device-thrombosis/virtual-DSA preprint as a direct mechanistic prior:
  three treatment strategies on three representative geometries, without
  clinical follow-up validation or a versioned simulation-output cohort.
- Kept the paired 33/38-dataset 4D-flow/black-blood material at its true two-
  anatomy unit and did not equate volume vortices with surface-WSS topology.
- Froze six candidates at 26.5/25.0/24.5/24.5/24.0/23.5. All fail total or
  critical novelty, asset and independent-unit floors; no P0/model/compute or
  paper identity opened.
- Added a fail-closed schema 10.1 invariant, regression test, exact audit and
  beginner-facing site explanation. No scientific server was queried;
  `junjinyong` remains completely excluded.
- Full regression passed 364 tests with 66 optional-dependency skips out of
  430. The protocol reports 77 invariant groups; JSON, JavaScript, site links,
  anchors, assets and diff hygiene pass.

## 2026-08-12 · Schema 10.0 scientific source deployed and privately pinned

- Exact scientific source `d7cf037cfd7b1833f12a0f90d24a8b070c0d7df6`
  passed Quality `31516119754` and Pages `31516119241`; live Overview and Learn
  expose the ADAM semantics correction and no-model/no-compute boundary.
- Private ledger `f0d172d8fa5f5578de487c532399532949b66198` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- This deployment provenance opens no terms, P0/P1, method, architecture,
  scientific server, PBS/GPU, outer test, result row, C21 or claim.

## 2026-08-12 · ADAM longitudinal semantics corrected and rejected · schema 10.0

- Retained the supplied surface-vector task-stability → matched-failure →
  bounded-development → fresh-confirmation order, but kept its architecture
  modules as unselected direct-prior controls. No material E0 or observed
  structural failure was identified; closed job `115645` remains unrepaired.
- Corrected ADAM units: 113 training cases include 35 paired subjects, not 70
  independent patients or 35 known interventions. The public source exposes no
  exact pair/lesion manifest or adjudicated growth target.
- Corrected label 2: it merges treated aneurysm and treatment artifact, is a
  rough one-pixel-dilated ignored region and cannot label remnant, occlusion,
  treatment response or clinical action.
- Recorded the 2025 MSDA-Net “post-treatment (follow-up)” wording as bounded
  source-semantic uncertainty: it neither proves the authors wrong nor creates
  a public intervention/lesion/response ground truth or method contribution.
- Froze six candidates at 28.5/28.0/28.0/27.0/27.0/24.5. All fail total or
  critical identifiability/novelty/asset floors. Accepted no ADAM terms, read no
  payload, queried no scientific server and opened no P0/model/GPU/claim.
- Added a fail-closed machine invariant, regression test, detailed audit and
  beginner-facing site chapter. `junjinyong` remains completely excluded.
- Full regression is 429 tests: 363 pass and 66 optional-dependency skips. The
  machine protocol passes 76 invariant groups; site links/anchors/assets,
  JavaScript, JSON and diff hygiene pass.

## 2026-08-12 · Schema 9.9 scientific source deployed and privately pinned

- Exact scientific source `ea30894b3df3721c22c2f2f312aac9cbb9990e18`
  passed Quality `31511921846`.
- Pages deployment `5854315031` reports success and live Overview/Learn serve
  schema 9.9. Exact Pages run `31511920868` has successful build,
  report-build-status and deploy jobs, while the run summary remained
  `in_progress` at this observation; no completed-run conclusion is asserted.
- Private interim ledger `048988e7bfc7ba482fb42518eca17c9e09f19523` is
  remote exact, PRIVATE and anonymous API returns 404. Manuscript and
  references hashes remain unchanged.
- This provenance opens no P0/P1, method, architecture, scientific server,
  PBS/GPU, outer test, result row, C21 or claim.

## 2026-08-12 · Diagnostic action and human-AI pivots rejected · schema 9.9

- Audited aneurysm automation bias, 7 T mimic clarification, the open
  multicentre TOF model, IAVS/TAR, contrast-retention functionals, MARTA,
  real-biplane cross-view localization and generic deferral priors.
- Froze six candidates at 29.5/27.0/26.0/26.0/25.0/24.5. All fail the total or
  critical novelty/asset floors; the additive leader is directly occupied by
  IAVS's stated CFD-applicability task and has residual novelty 0.5/5.
- Verified exact IAVS head `2e40088d…` is still README-only and exact TopAneu
  head `018c2434…` is unchanged. Read no medical payload and accepted no terms.
- Retained mimic taxonomy and patient-level recommendation/acquisition action
  as evaluation templates only. Opened no lead, P0/P1, method, architecture,
  scientific-server query, PBS/GPU, outer test, result or manuscript claim.
- Recorded an incomplete source-watch observation caused by GitHub HTTP 403
  and a terminated metadata request as operational non-verdicts, without
  retry, snapshot change or scientific interpretation. `junjinyong` remained
  completely excluded.
- Full regression passed 362 tests with 66 optional-dependency skips out of
  428. The protocol passed 75 invariant groups; all 15 frozen watch entries,
  historical contracts, site graph, JavaScript and diff hygiene also passed.

## 2026-08-12 · Schema 9.8 deployed and privately pinned

- Exact scientific source `975b6e360f71d6948c6cb09b6661704cf5732687`
  passed Quality `31507256370` and Pages `31507253480`; the public site exposes
  the 32.0 additive rejection and no-model/no-compute boundary.
- Private ledger `0075d080272b3d462d57d6ba07c7ed9a7df59080` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- This deployment provenance opens no P0/P1, method, architecture, server,
  PBS/GPU, outer test, result row, C21 or claim.

## 2026-08-12 · Longitudinal, intervention and patient reliability rejected · schema 9.8

- Audited the 2026 Bayesian surface-displacement growth source: 39 patients/42
  aneurysms internally, but only 16 patients/19 aneurysms selected from 24
  public follow-up patients; AURORA reproduced none of its reported results.
- Separated RSNA scale from its contract. The latest second-place method uses
  4,348 series with random series-level folds, while official data remain
  controlled and the official wiki remains `Coming soon`.
- Corrected intervention counts: the open CC BY 4.0 flow-diverter release has
  126 subjects/141 procedures and selected 2D DSA JPEGs, not 141 independent
  patients or a paired pre/post 3D cohort.
- Froze six candidates at 32.0/31.0/29.5/29.5/26.5/23.0. The additive 32.0
  all-lesion miss-risk row fails residual-novelty 1.5/5 and asset-readiness
  2.5/5 floors; total score cannot compensate. Retained patient-level all-
  lesion reliability only as an evaluation template.
- Opened no data terms, payload, P0/P1, method, architecture, scientific-server
  query, PBS/GPU, outer test or claim. Surface-vector and all no-verdict
  histories remain inactive and immutable; `junjinyong` remained excluded.
- Full regression passed 361 tests with 66 optional-dependency skips out of
  427. The protocol passed 74 invariant groups; all 15 source-watch entries,
  frozen contracts, site graph and JavaScript checks also passed.

## 2026-08-11 · Schema 9.7 deployed and privately pinned

- Exact scientific source `7b3208595f60f3c6972efec0c63d21c980a62353`
  passed Quality `31503802787` and Pages `31503801773`; live Overview and Learn
  render the 31.5/40, novelty 0.5/5, 99-base and 714-view boundaries.
- Private ledger `0bb7ffda374f801c0761fee7b589990eb175ab4f` is remote exact,
  PRIVATE and anonymous API returns 404. Manuscript and references hashes are
  unchanged.
- This deployment provenance opens no P0/P1, method, architecture, server,
  PBS/GPU, outer test, result row, C21 or claim.

## 2026-08-11 · Neck/isolation assets rejected as a paper identity · schema 9.7

- Audited exact AneuSI head `5b4c454…`: 1,041 blobs/977,740,269 bytes,
  103 model/centerline/neck files, 99 visible base IDs and 102 repeated derived
  VTKs at each of seven `clipFactor` values. Read metadata, README and license;
  opened no VTK or ODS body.
- Corrected the interpretation: AneuSI requires an input neck polygon;
  NeckSpline already predicts continuous CTA/MRA neck curves; 1,024-run CFD
  workflow variability, TAR and the open multicentre nnU-Net are direct priors.
- Froze six candidates at 31.5/30.0/29.0/28.0/24.0/22.5. The easiest executable
  audit fails the 32 total and 2.5 residual-novelty floors with novelty 0.5.
- Kept surface-vector inactive and opened no P0/P1, method, architecture,
  scientific-server query, PBS/GPU, outer test, result or claim. Historical
  no-verdict jobs remain immutable; `junjinyong` remained completely excluded.
- Added a detailed beginner-facing site chapter and synchronized the protocol,
  tests, research direction, ISBI boundary and decision history. Full regression
  passed 360 tests with 66 optional-dependency skips out of 426; protocol 73
  invariant groups, site graph, JavaScript and diff hygiene also passed.

## 2026-08-11 · VMR P0 closed without a scientific verdict · schema 9.6

- Ran exact source `92060937529f915649fcbbc06fc2856ce45d61ea` once on
  `introai9` as CPU/PBS job `115848.ECE-util1`: `E`/exit 2, walltime
  00:04:44, CPU 00:00:01, memory 57,084 kB and GPU 0.
- Preserved the 325-byte status and 980-byte bounded result by hash. They report
  execution-incomplete/no scientific verdict, 0/10 checks, no aggregate result
  and no persisted archive/VTP. Access extent and low-level cause are unknown;
  raw PBS output was not read.
- Closed the exact 32.5/40 conditional source lead without score relabelling,
  repair or rerun. P1, primary, method, architecture, GPU, outer test, result
  row, contribution and submission identity remain zero.
- Added the deidentified public execution record and returned the next allowed
  action to a fresh problem-level source/asset audit. `junjinyong` remained
  completely excluded and no login-node GPU command ran.

## 2026-08-11 · VMR growth-paired structure source lead · schema 9.5

- Pinned three exact official VMR metadata CSVs: 22 patient-specific cerebral-
  aneurysm rows, eleven reciprocal growth/stable pairs and 22 time-resolved
  surface-VTP result rows. The advertised result archives total 1,998,793,994
  bytes. No medical image, project ZIP, result archive or VTP was opened.
- Corrected the gap against the source paper's WSS/OSI/low-shear and mesh-
  convergence analysis, a later 481-patient prospective growth study,
  aneurysm WSS critical tracking, robust trajectory preservation and
  equivariant/Hodge surface operators.
- Froze six candidates at 32.5/30.5/30.5/30.0/26.0/23.0. Only
  `growth_paired_transient_wss_structure_stability` passes the prospective
  non-compensatory gate, exactly at the 2.5 novelty and 3.0 unit floors.
- Registered one exact method-free `introai9` CPU/PBS P0. It checks metadata,
  pair/result/size joins and bounded ZIP/VTP vector-phase semantics. It does
  not extract structure, test growth association, select a model or use GPU.
  Pass can authorize only a separately registered stability P1; fail or
  incomplete closes the exact version without repair/rerun.
- Historical jobs `115645` and `115684` remain closed no-verdict histories.
  No scientific server was queried in this registration update; all
  `junjinyong` operations and login-node GPU commands remain prohibited.
- Added the P0 to CI and passed 72 machine invariant groups plus 425 regression
  tests (359 pass, 66 optional-dependency skips), site graph, JavaScript, PBS
  shell syntax and diff hygiene.

## 2026-08-11 · Schema 9.4 deployed and privately pinned

- Exact scientific source `eb9a6ae9db3980ca41814b3852b68fd4a0804c09`
  passed Quality `31493466627` and Pages `31493465268`.
- Private ledger `5764bd7f986d1e0a173cb18d168e4aca16676689` is remote exact and
  PRIVATE; manuscript and references hashes are unchanged.
- Live Overview, Learn and change history expose the 29.5/40 rejection,
  direct-prior LODO failure, bounded code/cache reproducibility findings and
  no-model/no-compute state. This provenance creates no scientific result or
  claim.

## 2026-08-11 · Latent-shape/open-CTA transport rejected · schema 9.4

- Audited the exact 958-surface latent-shape paper and official MIT repository
  head `43e8219…`, including public code, weights and aggregate caches without
  opening medical mesh or image payload.
- Preserved the paper's own LODO accuracy 0.68/AUC 0.66 and low reconstruction
  error as direct-prior evidence, not an AURORA result.
- Found that the released training scripts use a seed-42 file-level 80/20
  loader, the complete LODO driver/fold manifest and processed labels/OBJ are
  absent, and the unknown-status condition is always truthy. These are bounded
  reproducibility findings, not paper invalidation or method novelty.
- Froze six candidates at 29.5/29.0/28.5/28.0/28.0/23.0. All fail total or
  critical novelty/identifiability floors; no CTA/STL payload, P0/P1, method,
  architecture, result or claim is opened.
- Queried no scientific server and created no PBS/GPU job. Historical no-
  verdict P0s remain unrepaired; future eligible execution is `introai9` PBS
  only and every `junjinyong` operation remains prohibited.

## 2026-08-11 · Schema 9.3 deployed and privately pinned

- Exact scientific source `56b173ef98898fe6d0934f39a253f34ed348288c`
  passed Quality `31490372870` and Pages `31490372720`.
- Private ledger `27ca806e4a640cb842d310d5a51e98035bf0b5a5` is remote exact and
  PRIVATE; manuscript and references hashes are unchanged.
- Live Overview, Learn and change history expose the 27.5/40 rejection,
  claimed-but-unversioned SynVA release, inactive surface-vector question and
  no-model/no-compute state. This provenance creates no scientific result or
  claim.

## 2026-08-11 · SynVA release and synthetic utility rejected · schema 9.3

- Audited exact arXiv `2605.17620v1` and its 25,831,786-byte PDF without
  opening synthetic meshes, processed medical data, a checkpoint or a split.
  The paper reports 50,000 procedural meshes, 769 processed real samples and
  an eleven-regime synthetic-to-real segmentation experiment; these remain
  prior-paper claims rather than reproduced AURORA evidence.
- Found no dedicated SynVA code or dataset URL in the paper and no exact public
  GitHub repository/code match. A claimed release without version, license,
  checksums, seeds and executable split manifests is not an admitted asset.
- Corrected the research gap against SynVA itself, synthetic-counterfactual
  auditing, knowledge-based shape-artifact detection, patient/institution
  leakage audits and generic utility/fidelity/privacy/domain-adaptation work.
- Froze six candidates at 27.5/26.5/26.0/26.0/23.5/23.5. All fail total or
  critical novelty/asset floors; active lead, P0/P1, method, architecture,
  result and claim remain zero.
- Added no recurring watch because there is no stable official release endpoint.
  A future versioned release requests a fresh manual source audit only.
- Queried no scientific server and created no PBS/GPU job. Future eligible
  execution remains `introai9` PBS only; login-node GPU and every form of
  `junjinyong` access remain prohibited.

## 2026-08-11 · Schema 9.2 deployed and privately pinned

- Exact scientific source `fd60885e4e6c5a34c7d65f6ed2c0013a31c15657`
  passed Quality `31487538060` and Pages `31487537080`.
- Private ledger `be7d016c222c744acbdf5669b6ac79cdc393bdcb` is remote exact and
  PRIVATE; manuscript and references hashes are unchanged.
- Live Overview, Learn and change history expose the 31.0/40 rejection,
  incomplete RSNA release contract, inactive surface-vector question and
  no-model/no-compute state. This provenance creates no scientific result or
  claim.

## 2026-08-11 · Reference provenance rejected; RSNA release-contract watch · schema 9.2

- Retained surface-vector only as an inactive falsifiable evaluation question;
  job `115645.ECE-util1` remains closed execution-incomplete/no verdict with
  0/10 scientific checks and no repair or rerun.
- Pinned the exact RSNA registry file and official 11-byte `Coming soon` wiki.
  The registry remains controlled access, says the Data Resource Publication
  is forthcoming and exposes no machine-auditable patient, split, annotation-
  lineage, adjudication or clean-reference contract. No terms, MIRA request or
  medical payload was opened.
- Added direct-prior corrections for biased-ruler analysis, weak-reference
  partial identification, LNMBench and active label cleaning. Generic robust
  loss, metric interval, subgroup audit and review allocation are not novel by
  being applied to aneurysm data.
- Froze six candidates at 31.0/31.0/29.5/28.5/28.0/25.5. Every candidate fails
  the total or a non-compensatory critical floor; active lead, primary, P0/P1,
  method, architecture, result and claim remain zero.
- Added source-watch v11 over fifteen public metadata states. A registry/wiki
  change requests manual source re-audit only and cannot accept terms, repair a
  score, register P0, select a model or authorize compute.
- Queried no scientific server and created no PBS/GPU job. Future eligible
  execution remains `introai9` PBS only; login-node GPU and all `junjinyong`
  access/query/transfer/submission/monitoring remain prohibited.

## 2026-08-11 · Schema 9.1 deployed and privately pinned

- Exact scientific source `4619c0e77a02588c0b47d3b615442339f60968b0`
  passed Quality `31484751195` and Pages `31484750528`.
- Private ledger `7d506e0e0a614c9067aae7a64293f90668813ea9` is remote exact and
  PRIVATE; manuscript and references hashes are unchanged.
- Live Overview, Learn and change history expose the TopAneu critical-floor
  rejection, inactive surface-vector question and no-model/no-compute state.
  This provenance creates no scientific result or claim.

## 2026-08-11 · Schema 9.1 rejects TopAneu annotation-version formulations

- Retained surface-vector only as an inactive falsifiable evaluation question;
  job `115645.ECE-util1` remains execution-incomplete/no verdict with 0/10
  scientific checks and no repair, model or compute authority.
- Pinned official TopAneu current head/release tree and immutable 98-case batch
  anchor. Metadata-only comparison establishes a real annotation version orbit
  but does not interpret changed dense-mask hashes as expert contour revisions.
- Froze six candidates at 32.0/31.5/31.5/30.5/28.5/24.5. The additive 32.0
  evaluator candidate fails novelty at 0.5/5; the revision-aware formulation
  scores 31.5 with novelty 2.0/5, below the prospective 2.5 floor.
- Added source-watch v10 for current/batch-1 Git trees, README/changelog/terms
  blobs and aggregate manifests. It can request source re-audit only.
- Opened no TopAneu terms, individual annotations, medical payload, P0/P1,
  method, architecture, scientific-server query, PBS/GPU, outer test, result or
  paper claim. `introai9` remains the only future gated execution server and
  `junjinyong` remains prohibited.

## 2026-08-11 · Cross-scale AAA sources rejected without an architecture · schema 9.0

- Audited exact Zenodo transcriptomic record `21868617` revision 4 and synthetic
  CFD record `21435232` revision 4 plus GitHub release head `98363a0…`, without
  downloading ZIP/XLSX/expression/CFD/image payloads.
- Corrected the broad “wall stress is unlinked” premise: GSE205071 does have
  paired high/low wall-stress biopsies from 12 patients. It still lacks the
  public imaging, mesh, field and biopsy-coordinate linkage needed for an ISBI
  model, and the six GEO sources are not one joint cohort.
- Froze six formulations at 30.0/28.5/26.5/26.5/23.0/22.0. The executable
  synthetic WSS operator leads on total but has residual novelty 0.5/5 because
  AAA transient WSS surrogation and geometry--hemodynamics analysis are direct
  priors. No candidate passes all non-compensatory floors.
- Added the detailed audit, schema-9.0 machine guard and mutation tests. Kept
  source watch v9 at thirteen meaningful states and corrected CI to validate
  that current watch rather than legacy v5; a routine version change in these
  already-public rejected records cannot repair the missing patient join or
  real paired outer reference.
- Opened no source payload, P0/P1, method, architecture, scientific-server
  query, PBS/GPU job, outer test, result row or claim. Surface-vector and closed
  jobs `115645`/`115684` are unchanged. Future compute remains introai9 PBS only;
  junjinyong remains prohibited.

## 2026-08-11 · Schema 8.9 deployed and privately pinned

- Exact scientific source `646698c66c1eed75ecd4466823bb2cc18ed5ca98`
  passed Quality `31479001176` and Pages `31479000353`.
- Private ledger `6b3dcb87a2c49e40e07ae2113605362eedcf4f0e` is remote exact and
  PRIVATE; manuscript and references hashes are unchanged.
- Live Overview, Learn and change history expose the 24.0/40 critical-floor
  rejection, thirteen-source watch and no-model/no-compute boundary. This
  provenance creates no scientific result or claim.

## 2026-08-11 · MRIS-Bench target contract rejected; thirteen-source watch · schema 8.9

- Audited exact public MRIS-Bench revision `6f2d6d9…`: 30,110 reported rows,
  eight Arrow shards and no public mask field, patient grouping, split, source
  lineage or annotation protocol. No Arrow/image payload was opened.
- Froze six formulations at 24.0/23.5/23.0/22.5/22.0/21.0. Every candidate
  fails multiple non-compensatory floors; visible viewer contradictions remain
  warnings, not a measured dataset-wide error rate.
- Added source-watch v9. A live read-only refresh matched all thirteen exact
  snapshots; an MRIS card/revision/inventory change can request only a fresh
  source audit, never download, score repair, P0, method or compute.
- Kept surface-vector as an inactive falsifiable question and jobs `115645` and
  `115684` as closed execution-incomplete/no-verdict history. No scientific
  server was queried and no model, PBS/GPU job, outer test or paper claim was
  created.

## 2026-08-11 · Schema 8.8 deployed and privately pinned

- Exact scientific contract `765916bbfec7304c4813fb485116a7f2b634dbca`
  passed Quality `31476095988` and Pages `31476095342`.
- Private ledger `c285781c639fba9240d9c1ec143b59c487d2ea12` remains PRIVATE;
  anonymous API returns 404 and manuscript/references hashes are unchanged.
- Live Overview and Learn expose the 32.0 additive score, 0.5/5 novelty-floor
  rejection and no-model/no-compute state. This provenance creates no
  scientific or compute authority.

## 2026-08-11 · Open-model transport rejected; admission gate becomes non-compensatory · schema 8.8

- Retained surface-vector only as an inactive problem question and rejected the
  proposed component bundle as a selected architecture or contribution.
- Audited the public multicentre TOF-MRA model, RSNA pipelines, TAR/IAVS,
  TopAneu and OpenNeuro states without opening model or patient payload.
- Froze six formulations at 32.0/31.5/29.0/28.5/27.5/27.0. The apparent
  32.0 candidate has residual novelty 0.5/5 and is not a lead.
- Added a prospective non-compensatory gate: total ≥32 plus critical floors for
  novelty, identifiability, assets, independent units and strong baselines, with
  an explicit failure mechanism and falsifier. Historical scores and closed
  no-verdict jobs remain unchanged.
- Opened no P0/P1, method, architecture, server query, PBS/GPU, outer test,
  result row or paper claim.

## 2026-08-11 · Schema 8.7 deployed and privately pinned

- Exact contract content `d04abd841a553c024c0aa5ba684d93b305773123`
  passed Quality `31473930058` and Pages `31473929481`.
- Private ledger `5adc050227c03265c514242776839c7c429329e4` remains PRIVATE;
  anonymous API returns 404 and manuscript/references hashes are unchanged.
- Live Learn and machine-rendered change history expose the degree-first
  endpoint hierarchy and no-running-job status. This provenance creates no
  scientific or compute authority.

## 2026-08-11 · Surface-vector endpoint contract hardened · schema 8.7

- Accepted the application question and E0→E5 order, but kept the paper
  identity, model and structural loss inactive.
- Corrected the machine contract: E1 begins with boundary-margin signed total
  degree validity and efficiency/abstention; exact point, index, track and event
  metrics are secondary only after mesh/tolerance/perturbation/matching
  stability.
- Recorded job `115645.ECE-util1` explicitly as closed—not running—and retained
  E/exit 2, 0/10 scientific checks, no verdict and no repair/rerun.
- Froze five jointly required ISBI result conditions: fresh patient/family
  confirmation, field non-inferiority, stable structure superiority over
  compute- and field-error-matched controls, family bootstrap uncertainty and
  matched-case interpretation.
- Opened no source lead, P0/P1, method, architecture, scientific-server query,
  PBS/GPU, outer test, result row or paper claim.

## 2026-08-11 · Schema 8.6 deployed and privately pinned

- Exact scientific content `8d6ac0f1c29f613178817fe1c07e8292e5f1fb79`
  passed Quality `31472138451` and Pages `31472137714`.
- Private paper ledger `2e8e7c37080db942d3d58973f724ae398222cde3` records the
  rejected identity while preserving manuscript and references byte-for-byte.
- This is provenance only; no source lead, P0/P1, method, architecture,
  scientific-server query, PBS/GPU, outer test, result row or claim opened.

## 2026-08-11 · cross-vascular transient-WSS correction · schema 8.6

- Audited the patient-specific AAA transient-WSS direct prior: 100 training
  patients, 29 external patients/118 scans, 1,090 CFD simulations, transient
  WSS/TAWSS/OSI and BC/remodelling/topology/mesh generalisation.
- Corrected the availability boundary: the stated public code repository is
  exact head `2f78bf18…` with one 183-byte README, release 0, no recognized
  license and no implementation/checkpoint/CFD fields. AAA-100 is an open
  geometry/centerline source, not the published transient-WSS payload.
- Audited SANO v1.0 as CC0/141 public files but only twelve independent
  iliac-vein cases under steady CFD; the source paper already owns the
  geometry-fidelity-to-low-WSS relation.
- Froze six formulations at 30.0/29.0/28.5/25.5/23.0/21.5, all rejected below
  32. Surface-vector stays inactive; no source lead, P0/P1, method,
  architecture, server query, PBS/GPU, outer test, result row or claim opened.
- Added fail-closed source watch v8 for the README-only AAA-WSS baseline. A
  change requests baseline-feasibility re-audit only and cannot authorize task
  data, architecture or compute.

## 2026-08-11 · Surface-vector follow-up deployed

- Exact analysis content `8616257d501707df6d26b07841124d426fac6d86`
  passed Quality `31469240409` and Pages `31469239803`.
- Live Learn and machine-rendered change history expose the stricter E0–E5
  result contract and qDSA direct-prior correction.
- This is provenance only; it opens no source lead, P0/P1, method,
  architecture, scientific-server query, PBS/GPU, outer test or claim.

## 2026-08-11 · Surface-vector analysis follow-up tightens the result contract

- Clarified that hypothetical model quality cannot substitute for E0 source
  admission, E1 endpoint stability or E2 field-error-matched failure evidence.
- Defined a future positive result as joint patient/family-level field
  non-inferiority, stable structural superiority, bootstrap uncertainty and
  matched-case interpretation—not a best validation run.
- Added the 458-patient qDSA injection-standardization/occlusion-prediction
  study as a direct prior. It does not provide a versioned patient release and
  does not open a new source, method or compute gate.
- Kept jobs `115645`/`115684` closed and opened no P0/P1, architecture,
  scientific-server query, PBS/GPU, outer test, result row or paper claim.

## 2026-08-11 · Schema 8.5 scientific content deployed

- Exact public scientific content `6ceff3e1f5554a7d640089e14ef6808956b782c9`
  passed Quality `31468054437` and Pages `31468053500`.
- Live Overview and Learn expose the 28.5/40 rejection, public-asset boundary,
  direct controls and no-model/no-compute state.
- This is deployment provenance, not a scientific result or authorization for
  P0/P1, a method, PBS/GPU, outer test, result row or claim.

## 2026-08-11 · Schema 8.5 rejects post-treatment reference-linked imaging

- Audited a prospective 100-patient PETRA/TOF/DSA cohort, Helsinki
  DWI/occlusion cohorts and the public 58-patient post-clipping table without
  requesting or opening patient images.
- Separated clear observed DSA/DWI endpoints from executable asset readiness.
  PETRA images are author-request only, Helsinki processing requires FINDATA,
  and the clipped source is tabular only.
- Added selective prediction, learning-to-defer, conformal risk control and
  prior PETRA/SILENT MRA work as direct controls. Froze six formulations at
  28.5/27.5/26.5/26.5/26.0/24.5, all below 32.
- Preserved surface-vector as inactive and opened no P0/P1, method,
  architecture, server query, PBS/GPU, outer test, result row or paper claim.

## 2026-08-11 · Schema 8.4 scientific content deployed and privately pinned

- Exact public scientific content `62a3d7f252b1b73bcf4dc4113e6fd27880183be7`
  passed Quality `31459082444` and Pages `31459081698`.
- Private paper ledger `e659a0bb03e45eafe23e0e1ebb4e8e0d42a9a50b` pins the
  rejected identity and source-watch boundary while preserving manuscript and
  references byte-for-byte.
- This is deployment provenance, not a scientific result or authorization for
  P0/P1, a method, PBS/GPU, outer test, result row or claim.

## 2026-08-11 · Schema 8.4 rejects downstream-surrogate identity

- Re-read exact team-source hashes and found no discussion later than
  2026-08-02. Retained real-CFD→surrogate downstream retention as an evaluation
  template, not an active paper identity.
- Preserved the 99-patient CMHA result as exploratory; it has no matched
  surrogate output and cannot be relabelled as a confirmatory failure.
- Audited PointFlowNet exact head `5cb4f254…`, Hemo-MPO, the one-anatomy CC0
  rigid/FSI record and an eight-case rupture-overlap study as direct
  priors/assets without executing code or opening scientific payload.
- Froze six formulations at 27.0/25.5/24.0/24.0/23.5/21.5, all below 32. Opened
  no P0/P1, method, architecture, server query, PBS/GPU, outer test or claim.

## 2026-08-11 · Source watch v7 adds PointFlowNet baseline state

- Added exact PointFlowNet head, root manifest, release/license state and
  repository size as the eleventh fail-closed watch.
- Recorded that the public repository has partial code, checkpoint/results and
  normalization statistics but no CFD payload or tracked train/val/test split
  manifest.
- A change requests direct-prior baseline-feasibility re-audit only; it cannot
  download data, repair a score, select architecture or authorize compute.

## 2026-08-11 · Schema 8.3 rejects the AneuX-derived transient-CFD source branch

- Audited exact HF metadata `38c574bc…` without accepting the manual contact-
  sharing gate or opening tensor, mesh, raw README or commit-history payload.
- Counted 180 bifurcation + 143 side-wall folders but only 322 unique visible
  IDs because `SNF365` occurs in both topology roots. Did not relabel visible
  IDs as patients or base families.
- Added the 2026 RHSIA, physics-constrained mesh-GNN and multiphysics
  thrombosis-GNN boundaries. Froze six source formulations at
  28.0/27.5/27.5/27.0/26.0/26.0, all below 32.
- Preserved jobs `115645` and `115684` as closed no-verdict history. Opened no
  P0/P1, method, architecture, server query, PBS/GPU, outer test or claim.

## 2026-08-11 · Fail-closed source watch v6 adds the gated transient manifest

- Extended immutable v5 with a tenth exact source state: revision, gate,
  license, dataset-card hash, storage metadata, sibling inventory and
  topology-qualified/unique-ID manifests for `yiyings/transient-dataset`.
- A change can request only fresh source re-audit. The watcher cannot accept
  terms, download a member, repair a closed P0, alter a score, register P0/P1,
  select a model or authorize GPU/outer test.
- Added contract validation and regression tests; the workflow remains
  read-only and contains no scientific-server or SSH path.

## 2026-08-11 · Source-watch v5 deployment verified

- Exact public content `4de91614991dea82441599136dcbf567f0bbc8bd`
  passed Quality run `31455085579` and Pages run `31455085014`.
- The evidence verifies the contract, tests and rendered site only. It adds no
  candidate, scientific result, method, model, PBS/GPU job or submission claim.

## 2026-08-11 · Fail-closed source watch v5 covers material re-entry states

- Preserved v4 and added exact AneuG-Flow, Aneurisk WSS, LargeIA and TopAneu
  metadata as four separate watches.
- A live read-only refresh matched all nine snapshots. AneuG is unchanged at
  `9dd4180…`; Aneurisk remains revision 4 with the exact 1,430,889,142-byte
  archive; LargeIA remains restricted with zero public files; TopAneu exposes
  Data/Evaluation navigation but still requires verified-account participation.
- Changes can request only manual source re-audit. The monitor cannot accept
  terms, repair/rerun closed P0s, download payload, change scores, register
  P0/P1, select architecture or authorize GPU/outer test.

## 2026-08-11 · Schema 8.2 public deployment and private ledger verified

- Exact scientific content `205d3d534a80ef5e3821d321a403158148e68ac5`
  passed Quality `31453522210` and Pages `31453521880`.
- Live Learn exposes the 355-versus-11 unit correction, WSS/ICC/bias glossary,
  direct-prior boundary and frozen 25.5/40 rejection.
- Private ledger head `138f764…` is remote exact and remains anonymous-API
  invisible; manuscript and references are byte-for-byte unchanged.
- This provenance record opens no scientific asset, P0/P1, method,
  architecture, server query, PBS/GPU, outer test or claim.

## 2026-08-11 · Schema 8.2 rejects functional 4D-flow segmentation wrappers

- Added the direct 2026 intracranial 4D-flow segmentation-to-WSS prior and
  separated 355 TOF-MRA pretraining scans from eleven nonpublic functional
  4D-flow units.
- Frozen six candidates at 25.5/24.5/23.5/23.5/23.5/23.0. VAST, COMPASS,
  task-based segmentation and TOF transfer remove component-level novelty.
- No image, mask, checkpoint, P0/P1, method, architecture, server query,
  PBS/GPU, outer test, result row or paper claim was opened. Surface-vector
  stays inactive and both prior P0 jobs remain closed without repair/rerun.

## 2026-08-11 · Fail-closed source watch v4 adds Aneumo material-release signals

- Froze official Aneumo GitHub head `701d53dd…` and Hugging Face revision
  `f801adee…` alongside IAVS, TopBrain and TRELLIS.
- Live metadata-only refresh matched all five snapshots. No linked real/
  undeformed-case mapping is present; future maintainer plans are not E0.
- Material change can request only a manual fresh source audit. Automatic
  payload download, snapshot rewrite, score repair, P0/P1, model, GPU and outer
  test remain disabled.

## 2026-08-11 · Adjudication deployment and private ledger verified

- Exact public content `9d3280c8e5946134eddf2d1791e2a9fb18d8151d`
  passed Quality `31451731627` and Pages `31451730835`.
- Private paper head `382d1d77f3a66ec36df0d8c2170e6c53bd0b78cb` is
  PRIVATE and pins the public decision without changing manuscript sources.
- Live Overview and Learn expose the accepted/corrected/rejected split and the
  all-checks-unevaluated wording. No experiment or authorization was added.

## 2026-08-11 · Surface-vector analysis critically adjudicated

- Retained the falsifiable application question and staged evidence ladder,
  while keeping the structural failure unobserved and the paper identity
  inactive.
- Put signed total degree/abstention before exact point/worldline endpoints;
  the latter remain secondary evaluation until mesh/tolerance stability passes.
- Rejected edge 1-form, Hodge/DEC, equivariance, periodic decoding and
  structural-loss composition as standalone novelty or a selected architecture.
- Clarified on the public guide that all ten registered checks in both related
  P0 histories were unevaluated, not failed scientific checks. No experiment,
  server query, model, GPU, outer test or paper claim was opened.

## 2026-08-11 · Schema 8.1 deployment and private ledger verified

- Exact public source `6de391eafcabea5ba398c49892353a8a707565d1`
  passed Quality `31450399461` and Pages `31450398671`.
- Private paper head `567a995b7ce09887ffe3c480ce09f06b4d42fc0d`
  pins the same decision while preserving the manuscript and references.
- This provenance update opens no agreement, payload, P0/P1, model, server
  query, PBS/GPU, outer test, result row or paper claim.

## 2026-08-11 · Schema 8.1 rejects the cross-view projection branch

- Audited MIDL 2026 cross-view ADAM MIPs, multicenter clinical SDAN, selective
  biplanar 3D localization, conformal 2D/3D regions, inverse-problem task UQ,
  projective fusion and real-DSA path-length correction.
- Froze six exact scores at 31.0/30.0/29.5/26.5/22.5/21.5; all are below the
  32-point admission line. Synthetic MIP pairs are not clinical biplane DSA.
- Added a machine-validated source-only boundary and detailed site explanation.
  No agreement, payload, P0/P1, method, architecture, server query, PBS/GPU,
  outer test, result row or paper claim was opened.

## 2026-08-11 · Schema 8.0 outcome deployment verified

- Exact outcome content `6123f0e917f084aad0bf352306ba9cf70f57e835`
  passed Quality `31448501704` and Pages `31448501265`.
- Verified the live site exposes job `115684`, 0/10 no-verdict, closed
  32.5/40 source history and zero active lead/model/GPU.
- This deployment record adds no result, repair, rerun, P1 or compute authority.

## 2026-08-11 · Schema 8.0 closes the conformal-degree P0 without a verdict

- Ran exact public source `4a0fa65b…` once on `introai9` as CPU-only PBS job
  `115684.ECE-util1`; final state `E`, exit 2, walltime 00:40:06, CPU 00:00:01,
  memory 56,812 kB and GPU 0.
- Recorded a 323-byte status and 971-byte bounded result. They report
  `execution-incomplete/no scientific verdict`; 0/10 scientific checks were
  evaluated and the only reported error class is
  `AneuriskConformalDegreeP0Error`.
- Did not infer a low-level cause. Complete archive integrity, VTP access and a
  scientific aggregate were not reported; transient partial bytes are unknown,
  and no persistent archive/VTP or raw scheduler log exists.
- Preserved 32.5/40 as immutable source history while returning active
  shortlist/conditional lead/primary/method/architecture/GPU/outer test/result
  row/C21/submission identity to zero.
- Closed without transport, reader or dependency repair, same-contract rerun,
  or P1. The next allowed action is a fresh problem-level source/asset audit.
  Final `introai9` queue was empty; `junjinyong` remained untouched.

## 2026-08-11 · Schema 7.9 registers a conformal-degree semantics P0

- Froze a fresh six-candidate problem-level screen at
  32.5/31.0/29.5/29.5/29.0/28.5. Only patient-level conformal signed-degree
  certification crosses the unchanged 32/40 source line.
- Separated the new validity/efficiency estimand from the closed surface-vector
  endpoint-fidelity P0; historical scores, job `115645.ECE-util1`, 0/10 checks
  and no-repair verdict remain immutable.
- Limited the proposed guarantee to patient-marginal simultaneous tangent-field
  coverage and signed total degree in boundary-margin-certified regions. It
  does not guarantee exact critical-point count/location/type, conditional
  coverage, rupture risk or clinical utility.
- Added functional surrogate conformal prediction, whole-field downstream
  certificates, conformal neural operators, uncertain vector-field topology
  and multilevel robustness as direct priors.
- Registered one method-free `introai9` CPU/PBS P0 for the checksum-pinned
  1.43 GB Aneurisk archive. It checks safe tar inventory, 76 patient cases,
  VTP/three-component cycle-averaged WSS, units and age/inflow input semantics;
  it performs no critical-point extraction, conformal calibration, model or
  GPU work.
- Added a bounded standard-library reader, synthetic contract tests, machine
  guards and beginner-readable site/audit material. P0 pass can open only a
  separate CPU-only method-free stability P1; fail/incomplete closes without
  same-contract repair or rerun. `junjinyong` remains prohibited.

## 2026-08-11 · Schema 7.8 deployment verified

- Exact scientific content `720e4c5e441c96bd2b35e31cb2a1a19da0ff6dee`
  passed Quality run `31416106615` and Pages run `31416105439`.
- Live Overview, Learn, detailed audit and research-data object render best
  31.0/40, all rejected, Hodge-as-baseline, evaluation-first critical
  structures and archive/VTP/P0/model/GPU 0.
- This provenance-only record changes no score, closed P0, method,
  architecture, server state, outer test or paper claim.

## 2026-08-11 · Schema 7.8 rejects structure-faithful WSS before compute

- Reframed the submitted surface-vector analysis as an inactive, falsifiable
  application hypothesis rather than an active paper identity.
- Verified unchanged official AneuG heads and preserved the historical
  `115645.ECE-util1` execution-incomplete, 0/10, no-repair outcome.
- Audited the open 76-geometry Aneurisk v1 record and its 1,436-byte README
  without reading the 1.4 GB archive or VTP members. The manifest does not
  enumerate vector arrays, phases, annotations or extraction tolerances.
- Froze six formulations at 31.0/30.0/29.0/28.5/27.5/27.0; none crosses 32.
- Corrected the architecture logic: Hodge is a required baseline, critical
  structures begin as evaluation rather than a loss, edge 1-forms do not
  guarantee zeros, and surface boundaries require explicit index/Hodge
  conventions.
- Added machine guards and mutation tests preserving zero P0/P1, method,
  architecture, server query, GPU, outer test and paper claim. No scientific
  server was queried; `junjinyong` remains prohibited.

## 2026-08-11 · Schema 7.7 deployment verified

- Exact content `611848cba1f19675ab850ebc0c9e2bcd8672c0ef` passed Quality
  run `31413485546` and Pages run `31413484543`.
- Manual Public source watch run `31413562860` succeeded on the same content;
  IAVS, TopBrain 2.0 and TRELLIS matched their frozen snapshots and requested
  no manual review.
- This provenance record changes no source score, active candidate, closed P0,
  method, architecture, server state, GPU, outer test or paper claim.

## 2026-08-11 · Schema 7.7 adds a fail-closed three-source watch

- Added `source_watch_v3.json` for IAVS, TopBrain 2.0 and the TRELLIS stated-code
  repository while preserving v1/v2 as historical contracts.
- The live read-only refresh matches all three frozen snapshots. TRELLIS remains
  HTTP 404; no manual review, source re-audit, baseline-feasibility re-audit,
  payload, P0/P1, model, GPU or outer test is opened.
- Separated change semantics: IAVS/TopBrain can request only a fresh source
  audit, while TRELLIS can request only a direct-prior baseline-feasibility
  review. Neither path can mutate the snapshot or scientific authorization.
- Added a scheduled/manual read-only GitHub Action. Material change exits 3
  after printing evidence; network/contract failure also fails the workflow
  rather than being misreported as a scientific change.
- Added mutation tests for frozen-state equality, independent review routing and
  the no-download/no-P0/no-architecture/no-GPU boundary. No scientific server
  was queried; `junjinyong` remains prohibited.

## 2026-08-11 · Schema 7.6 deployment verified

- Exact content `aec4b76a1646a4e3508640a1a0ecb7ac146979cc` passed Quality
  run `31411063368` and Pages run `31411180740`.
- Live Overview, Learn and the detailed delta were checked for TRELLIS
  direct-prior, current code-404 and zero candidate/model/GPU boundaries.
- This provenance-only record creates no server query, job, scientific result,
  score repair, P0, method, architecture, outer test or paper claim.

## 2026-08-11 · Schema 7.6 adds the TRELLIS surface-feature direct prior

- Verified the paper/source contract for arXiv:2509.03095 and DOI
  10.1016/j.neuri.2026.100259: 1,024-dimensional TRELLIS features from a
  500,000-object non-medical pretraining corpus augment PointNet/PointNet++ and
  an AnXplore mesh GNN.
- Recorded 101 sacs on one uniform parent vessel, five with/without-feature
  runs, and rollout RMSE 7.57→6.09 and 4.03→3.55 without converting these
  values into surface-WSS topology evidence.
- Verified that the inspected source reports no critical-point/worldline
  endpoint or independent sealed GNN split and that the stated GitHub URL
  returns 404 with zero exact repository-search matches.
- Added foundation-surface features as a future matched direct control. No
  candidate score, closed P0, payload, method, architecture, server query,
  PBS/GPU, outer test, result row or contribution changed.
- AURORA remains `introai9`-only after a future gate; `junjinyong` remains
  prohibited.

## 2026-08-11 · Schema 7.5 rejects measurement-functional inverse flow

- Added Bayesian finite-element regression (arXiv:2607.20224) as a direct prior
  for noisy under-resolved velocity, unknown BC, exact wall constraints,
  velocity/pressure posterior inference and WSS uncertainty propagation.
- Froze six formulations at 30.0/29.0/28.0/26.5/26.0/25.0; none reaches the
  unchanged 32/40 source-admission line.
- Recorded why BenchAnXplore cannot carry fresh functional confirmation: the
  decoded compact contract has velocity and masks but no verified pressure/WSS
  target, the parent vessel is shared, and all 105 cases already informed
  representation selection.
- Recorded FlowMRI's ten healthy cerebrovascular volunteers and one reference
  test, CMRx's post-deadline independent-use embargo, and one-effective-anatomy
  physical/device sources without inflating scans or frames into patients.
- Added schema guards and mutation tests enforcing exact scores, direct-prior
  facts, 30<32 and zero payload/P0/method/architecture/server/PBS/GPU/outer
  test/claim. Surface-vector remains inactive and its closed P0 remains intact.
- No server was queried and no job was created. `introai9` is the only future
  gate-authorized target; `junjinyong` remains prohibited.

## 2026-08-11 · Schema 7.4 corrects the public virtual-removal asset record

- Verified official Figshare v3 metadata for 30 checksum-pinned VTP files:
  ten pathological cases, ten paired virtual-removal surfaces and ten matched
  controls, totaling 163,634,666 bytes; no VTP payload was accessed.
- Corrected the old broad pair-absence premise without relabeling its 27/40
  Aneumo/IntrA decision. The new pair is an investigator-created target, not an
  observed same-patient biological counterfactual, and has only ten independent
  paired cases.
- Recorded the repository license conflict (top-level CC BY 4.0 versus the
  description's CC BY-NC 3.0 plus researcher restriction) and froze the stricter
  no-payload boundary pending explicit clarification.
- Rejected the fresh formulation at 28.5/40. SynVA/AneuG, IntrACompletion,
  AneuSI, virtual-removal WSS analysis and counterfactual reconstruction are
  direct priors. The asset has no phase-resolved WSS and does not satisfy
  surface-vector E0.
- Created no P0, split, method, architecture, PBS/GPU job, outer test, result or
  contribution. No server was queried; `introai9` remains the only allowed
  execution target and `junjinyong` remains prohibited.

## 2026-08-10 · Schema 7.3 retains an inactive surface-vector hypothesis

- Accepted the falsifiable possibility that field-error-matched transient-WSS
  surrogates disagree on robust signed critical points and cardiac-cycle
  worldlines, but did not promote it to an active source lead or paper identity.
- Rejected edge 1-forms, SE(3) message passing, Hodge splitting, periodic
  decoding and structural losses as standalone novelty. They remain future
  candidate controls only after task stability.
- Added a six-level evidence ladder: material source E0, method-free stability,
  field-error-matched failure-mechanism and baseline audit, bounded development,
  fresh confirmation, and external physical interpretation.
- Corrected stale machine/site fields that still described the closed 32.0/40
  version as an active conditional P0. Active lead, primary, method,
  architecture, executable P0/P1, GPU, outer test and submission identity are
  all zero.
- Preserved job `115645.ECE-util1` and 0/10 evaluated checks as immutable closed
  history. A wrapper, downloader, retry rule or model rename cannot constitute
  a new evidence version; a material source/asset change is required.

## 2026-08-10 · Schema 7.2 closes the surface-vector P0 without a verdict

- Submitted exact public source `8a06de209892c09fe4adf86a3125a612a5030d9f`
  once to `introai9` PBS as CPU-only job `115645.ECE-util1`; it ended `E`/exit
  2 after 00:27:02 with CPU time 00:00:06, peak memory 625,780 kB and GPU 0.
- Retained only a 301-byte private status and a 588-byte bounded private result.
  No aggregate scientific result, raw scheduler log or persistent probe cache
  exists, so 0/10 registered checks were evaluated and the low-level cause is
  unresolved.
- Preserved the exact 32.0/40 source finding but closed this candidate version
  as execution-incomplete/no scientific verdict. Same-contract repair/rerun,
  P1, method, architecture, GPU, outer test, paper contribution and submission
  identity remain unauthorized; active shortlist and conditional lead are 0.
- Added `results/aneug_surface_vector_structure_p0_execution_20260810.json` and
  strengthened the direct-prior boundary: Hodge Spectral Duality is ICML 2026,
  critical-point trajectory preservation and aneurysm-specific cardiac-cycle
  tracking are already established, and the arterial SE(3) paper DOI is
  corrected to `10.1016/j.compbiomed.2024.108328`.

## 2026-08-10 · Schema 7.1 registers a surface-vector structure P0

- Froze `time_varying_surface_wss_index_structure_prediction` at exactly
  32.0/40 as one conditional source lead, with no selected primary, method,
  architecture, contribution, outer test or GPU job.
- Pinned AneuG-Flow dataset/code commits and six exact raw files for three
  lexicographic probes (`stable_0`, `stable_100`, `stable_10001`), totaling
  276,642,685 bytes; no payload body has yet been accessed.
- Added a one-shot `introai9` CPU/PBS P0 that verifies safe tensor schema,
  mesh/coordinate alignment, tangency, temporal variation and signed-index
  critical-point extractability. It reads no blood field, processed archive,
  checkpoint, model, clinical data or outer test.
- Made Hodge/DEC, equivariance, tangent projection, generic critical-point loss
  and clean evaluation explicit direct priors/controls. Independent novelty
  requires an operator-specific representation or guarantee plus prospective
  index/worldline superiority; a P0 pass opens only method-free P1.
- Added the executable config, PBS wrapper, bounded reader, synthetic tests,
  protocol guards and beginner-readable source audit. `junjinyong` remains
  prohibited; all execution is `introai9` PBS only.

## 2026-08-10 · Schema 7.0 rejects the AneuG target-construction batch

- Pinned official AneuG-Flow paper, code commit `4a090a0…` and dataset commit
  `9dd4180…`; inspected source and repository metadata without field/mesh or
  checkpoint payload.
- Recorded `k=3` coordinate/WSS registration with retained common connectivity,
  absent explicit tangent/functional conservation, pre-split normalization,
  test-loss checkpoint selection and ordered-prefix transient splitting.
- Froze six candidates at 31.5/31.0/30.5/30.5/30.0/29.5, all below the unchanged
  32-point admission line. Conservative remapping, tangent vector transfer and
  test-blind evaluation remain direct priors/controls rather than novelty.
- Created no P0, model, architecture, PBS/GPU, outer test or paper result. A
  read-only `introai9` queue observation was empty and no login-node GPU command
  ran. `junjinyong` remains completely prohibited for AURORA.
- Added the detailed beginner-readable audit, schema guards, mutation tests and
  synchronized public research/site/private-planning state.

## 2026-08-10 · Schema 6.9 closes OpenNeuro P0 without a scientific verdict

- Ran exact source `bb227edc86bf3b68e92b97f120a7918b0753c831` once on
  `introai9` PBS as CPU-only job `115622.ECE-util1`; final `F`/exit 1,
  walltime 00:02:24, CPU 00:00:00, memory 15,328 kB, GPU 0.
- Preserved the only materialized artifact as a 310-byte private
  `execution_incomplete` status. No aggregate result, raw scheduler log,
  patient payload, model, checkpoint or outer test materialized, leaving all
  10 registered scientific/semantics checks unevaluated.
- Added the deidentified immutable execution record
  `results/openneuro_containment_morphometry_p0_execution_20260810.json`.
- Closed the exact 32.5/40 source candidate without repair, rerun, P1, method,
  architecture or GPU authorization; reset active shortlist, primary problem,
  result row and paper identity to zero.
- Advanced the central contract to schema 6.9 and synchronized the overview,
  beginner explanation, protocol, model, dataset, acquisition, server,
  literature and ISBI planning views. `introai9` remains the only AURORA
  server and `junjinyong` remains prohibited.

## 2026-08-10 · Schema 6.8 registers an OpenNeuro containment metadata P0

- Preserved the rejected 31.5/40 coarsening-mechanism candidate without
  relabelling it. A distinct formulation uses only observed containment
  `Y ⊆ W` and asks for a set-valued lesion mask plus intervals for monotone
  morphometry; it scores 32.5/40 in a fresh frozen six-candidate batch.
- Pinned OpenNeuro `ds003949` tag `1.0.1`/commit `896b884…` and official code
  commit `5ecdf6e…`. Safe opcode-only inspection reconciles 284 public subjects
  into 246 weak and 38 precise subjects, with exactly four code-only weak
  subjects. Session strings are explicitly rejected as join keys.
- Registered one all-or-none metadata P0 reading only the Git tree, dataset
  description, two small supervision-list blobs and licenses. Patient NIfTI,
  participant/clinical tables, model/checkpoint, GPU and outer-test access are
  zero. Pass opens only a separately registered method-free P1; failure or
  incomplete closes the exact version without same-contract repair/rerun.
- Execution is restricted to one `introai9` PBS submission with CPU 2, 4 GB,
  GPU 0 and 20-minute walltime. `junjinyong` remains prohibited for connection,
  query, transfer, submission and monitoring.
- Added the detailed source audit, frozen config, stdlib audit implementation,
  one-shot PBS wrapper, unit tests, schema-6.8 protocol guards and beginner site
  explanations. No primary, method, architecture, contribution or paper result
  is selected.

## 2026-08-10 · Schema 6.7 hardens the ISBI author-compliance contract

- Rechecked the live official ISBI 2027 author instructions. The existing
  single-blind, four-technical-page, optional non-technical fifth-page and
  2026-10-26 23:59 USA EDT rules remain correct.
- Added machine guards for the two-first-author-submission limit, prohibition
  on substantially similar prior or concurrent peer-reviewed submissions,
  allowed preprints, mandatory ethics wording irrespective of approval need,
  mandatory funding/COI disclosure, and the current `Coming Soon` submission
  link state.
- Corrected the stale venue headline-domain string to the current BC-transport
  execution-incomplete/no-active-shortlist state. This format correction does
  not select a problem, method, architecture, GPU job, result, or submission.
- Added a visible, beginner-readable ISBI contract panel and decision-history
  entry to the public site. Future eligible compute remains `introai9` PBS only;
  `junjinyong` remains prohibited.

## 2026-08-10 · Schema 6.6 outcome and explanatory site are live

- Exact scientific content `bb16d90d2e06bd1f12972efaf67093d425048d49`
  passed Quality run `31375709669` and Pages run `31375709322`.
- Live overview, beginner Learn guide and public execution JSON expose the same
  `execution-incomplete/no scientific verdict`, no-repair/no-P1 and active
  lead/primary/method/architecture/GPU 0 boundary.
- Private paper head `b530d51b4e461c883dcc0d9c9e2e24b56cbddb17`
  pins the public schema-6.6 content as unnumbered history. Repository visibility
  is PRIVATE and the three-page structural PDF was visually checked.
- Deployment verification changes no scientific verdict, source score, access,
  compute or submission authorization. Future eligible compute remains
  `introai9` PBS only; `junjinyong` remains excluded.

## 2026-08-10 · BC-transport P0 closes execution-incomplete without a verdict

- Ran exact public source `38e7894fc5ae56ffb3efbe469c4e1f7480f81feb`
  once on `introai9` as CPU/PBS job `115518.ECE-util1`; no GPU or login-node GPU
  command was used and `junjinyong` was never accessed.
- The job ended E/exit 1 after 00:08:21, CPU time 00:00:00 and 39,160 kB memory.
  Only a 275-byte private status artifact was created. Aggregate result and raw
  PBS output were absent; the low-level cause and every scientific/source check
  remain unresolved/unevaluated.
- Closed this exact 33.5/40 candidate version as
  `execution-incomplete/no scientific verdict`. No repair, rerun, P1, method,
  architecture, validation/test access, GPU, outer test or paper contribution
  is authorized. Active conditional source lead returns to 0.
- Added the deidentified execution record
  `results/aneumo_bc_transport_p0_execution_20260810.json`, advanced the machine
  contract to schema 6.6 and synchronized protocol guards, public docs, site,
  private planning paper and shared operations boundary.

## 2026-08-10 · Anchor-conditioned BC transport opens one method-free CPU P0

- Froze a new problem rather than relabelling failed geometry-to-field V1/V1e:
  one CFD velocity field at anchor flow `q0` conditions transport to another
  observed flow `q` on the same aligned geometry.
- The six-candidate direct-prior screen admits only
  `similarity_quotiented_anchor_conditioned_bc_transport` at 33.5/40. Its
  residual-gap score is 2/5 because DeltaPhi, scale-consistent operators,
  learned boundary extensions and generic scaling/cycle mechanisms are direct
  controls, not novelty.
- Preregistered one exact method-free `introai9` CPU/PBS P0 over historical
  Aneumo train family 1, cases 1–2, eight flows and 16 members. Pressure,
  validation/test, persistent field cache, model/checkpoint, GPU and outer-test
  access are forbidden. Pass opens only a separate train-only method-free P1;
  fail or execution-incomplete closes this exact version without repair/rerun.
- Advanced the machine contract to schema 6.5 and added mutation guards,
  synthetic execution tests, PBS one-shot provenance, full research/site
  explanations and an explicit `introai9`-only boundary. `junjinyong` remains
  prohibited for connection, query, transfer, submission and monitoring.
- Affected files: `docs/aneumo-bc-transport-source-audit-2026-08-10.md`,
  `configs/aneumo_bc_transport_p0.json`, `src/aurora/aneumo_bc_transport_p0.py`,
  `scripts/audit_aneumo_bc_transport_p0.py`,
  `cluster/pbs_aneumo_bc_transport_p0.pbs`,
  `tests/test_aneumo_bc_transport_p0.py`, `configs/aurora_v1.json`, protocol
  guards, research docs, site, README and `AGENTS.md`.

## 2026-08-10 · TopAneu code semantics reject the historical source lead

- Preserved the earlier schema-6.3 33.0/40 score as immutable history rather
  than repairing it retrospectively.
- Audited official taxonomy mappings, Task 1/2 evaluators and image-only test
  templates at commit `018c243…`, without reading patient medical payload.
- Confirmed that location factorization is explicit metadata, silver anatomy is
  absent from test inputs, and Task 2 collapses instances into per-class binary
  volumes; direct priors already cover training-only anatomy supervision,
  hierarchy, vessel-aware detection and lesion counting.
- Froze six fresh scores at 31.5/31.0/31.0/30.5/28.5/20.0. All are below 32;
  active and conditional shortlist, P0, model, GPU and outer test remain zero.
- Advanced the machine contract to schema 6.4, added mutation guards, and made
  the public overview, Learn guide and decision history expose the rejection.
- Future AURORA execution remains `introai9` PBS only after a new gate;
  `junjinyong` remains completely excluded.

## 2026-08-10 · TopAneu schema 6.3 content and site verified

- Exact scientific content `e4038ca6d052def5f275c4118bd904c4ab543135`
  passed Quality `31367056976` and Pages `31367056610`.
- Live overview, zero-assumption guide and detailed source audit render the
  same 33/40 conditional lead, 417 scans/409 patients, terms-pending state and
  no-payload/P0/method/architecture/GPU boundary.
- Deployment provenance does not accept terms, activate a shortlist, authorize
  compute or turn the problem lead into a paper contribution.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `docs/server-execution.md`,
  `site/assets/research-data.js`.

## 2026-08-10 · TopAneu material release creates a terms-pending source lead

- Verified official TopAneu-26 repo commit `018c243445f99199f484018c4c80575c84c72293`
  and live challenge metadata: 417 scans/409 patients, 52 location leaves,
  three aneurysm types, location JSON, silver vessel masks, UMCU held-out test,
  official metrics and seven-minute/T4 runtime.
- Froze six candidates. Factorized leaf risk with silver anatomy restricted to
  noisy train-time privileged information scores 33.0/40; the other five score
  31.5/31.0/30.5/28.5/20.0. The historical 29/40 attachment candidate is not
  repaired or relabelled.
- This is one conditional source lead, not an active executable shortlist.
  User terms acceptance, medical payload, P0, selected primary, method,
  architecture, PBS/GPU, outer test and paper contribution remain zero.
- The only possible next execution is a separately preregistered CPU/read-only
  P0-R after explicit user terms acceptance, followed by method-free P1 only on
  an all-pass result. AURORA remains `introai9`-only; `junjinyong` is prohibited.
- 영향 파일: detailed audit, schema/validator/tests, research/experiment/model/
  dataset/ISBI/server docs, overview/Learn/change UI and private paper history.

## 2026-08-10 · AneuG-Flow P0-v2a closes execution-incomplete

- Exact public source `690035ae…` was cloned into a dedicated clean detached
  checkout and submitted once on `introai9` as CPU/PBS job
  `115467.ECE-util1`; `junjinyong` was not accessed.
- Scheduler observation was state E, exit 1, walltime 00:00:08, CPU 00:00:00
  and 16824 kB memory. A 319-byte execution-incomplete status materialized, but
  aggregate result and raw PBS output did not, and the job later stopped being
  returned by `qstat`.
- Transport operation counts, verified range bytes, transport pass/fail and all
  scientific checks are unevaluated. The low-level cause is unresolved. The
  sole repair round is consumed and the candidate closes without rerun, v2b,
  P1, model, GPU, outer test or claim. Active shortlist returns to 0.
- Exact outcome content `9632ee5a5e507318fd18bff217c934c30a0b1a02`
  passed Quality `31364095951` and Pages `31364095339`.
- 영향 파일: public execution record, schema/validator/tests, research docs,
  overview/Learn/change UI, private manuscript history and operations guides.

## 2026-08-10 · AneuG-Flow transport P0-v2a preregistered

- Preserved the historical 33/40 P0-v1 execution-incomplete result without
  rerun or relabelling and froze one distinct validation-development repair
  round around a single transport hypothesis.
- P0-v2a is `introai9` CPU/PBS only: two HEAD requests, four exact 1 MiB
  ranges, 4 MiB total, retry 0, no full object, reader, case ID, model, GPU or
  outer test. Pass can register only a separately budgeted P0-v2b; fail closes
  v2a.
- Schema 6.2 records one conditional source shortlist but no selected primary,
  method, architecture, scientific P0 verdict, GPU authority or paper claim.
  Current PBS state remains unknown because the latest connection reset before
  a remote command; no v2a job has yet been submitted. `junjinyong` remains
  fully excluded.
- 영향 파일: frozen config, stdlib audit CLI, CPU/PBS script, tests, rationale,
  central protocol, research documents, overview/Learn/change UI and
  `AGENTS.md`.

## 2026-08-10 · 4D-CTA source decision and explanatory site verified

- Exact schema-6.1 scientific content
  `f95b73a68ddc20b993ebd5dd0d28e4645a3dafc9` passed Quality `31359594992`
  and Pages `31359594475`.
- Direct live checks of the overview, beginner guide, detailed audit and
  research-data object render 31.5/40, 20 independent patients, the distinction
  between derived RSII and future clinical truth, and archive/P0/model/GPU 0.
- Deployment provenance changes no source score, method, compute or submission
  authorization. Future execution remains `introai9` PBS only and
  `junjinyong` remains fully excluded.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `docs/server-execution.md`,
  `site/assets/research-data.js`.

## 2026-08-10 · Open 4D-CTA AAA mechanics source remains below admission

- Verified official Zenodo `19182978`: CC BY 4.0, one 1.86 GB archive, 20
  patients/three centres, 2--10 cardiac phases and released wall/ILT/FE plus
  strain/tension/SII/RSII outputs. Archive and member payload access remain 0.
- Froze six candidates at **31.5/30.5/30.0/29.0/28.5/25.5**. Repeated phases
  and vertices are not independent patients; one synthetic deformation case is
  not population ground truth; no future clinical endpoint is released.
- Schema 6.1 adds a machine-validated source decision. Active shortlist,
  primary, executable P0, method, architecture, PBS/GPU, outer test, result row
  and submission identity remain zero without score repair.
- The current `introai9` status attempt reset before remote execution; no job
  was submitted and no repair loop was opened. `junjinyong` remains completely
  excluded.
- 영향 파일: detailed audit, protocol/validator/tests, research docs, public
  overview/Learn/change UI, `AGENTS.md` and private rejected-source history.

## 2026-08-10 · TopBrain 2.0 official metadata corrected; source watch v2

- Official Zenodo revision 4 marks the only released TopBrain 2.0 object—the
  35-page design PDF—`open` under `CC BY 4.0`. This does not license medical
  images, masks or manifests that have not been released. The live challenge
  remains `Under construction` and exposes Join registration but no executable
  Data, Evaluation, Rules or Submission task route.
- Schema 6.0 corrects the older license/submission wording without altering the
  frozen 29/40 rejection. Active shortlist, primary, payload, P0, method,
  architecture, PBS/GPU, outer test and C21 remain zero.
- `source_watch_v2.json` watches exact IAVS GitHub and TopBrain 2.0
  Zenodo/challenge snapshots. Live fetch matched both frozen states and returned
  `continue_watch_only`; all automatic download/P0/model/GPU flags remained
  false.
- Exact content `545df1b570ea9df6d3feac545bbc0f02cab18178` passed Quality
  `31357501911` and Pages `31357501328`; direct live checks rendered the same
  corrected license scope and no-compute boundary.
- Future gate-authorized execution remains `introai9` PBS only. `junjinyong` is
  excluded from connection, query, transfer, submission and monitoring.
- 영향 파일: machine protocol/validator/tests, source watcher/CLI/tests,
  detailed audits and plans, overview/Learn/changelog UI, `AGENTS.md`.

## 2026-08-10 · TopBrain 2.0 content and live site verified

- Exact scientific content `8b2a70c9a6bab21962d22b66601481d323e4a52e`
  passed Quality `31354245210` and Pages `31354244348`.
- Live overview, zero-assumption guide and detailed audit return HTTP 200 and
  render TopBrain 2.0 best 29.0/40, all six rejected, design-PDF-only source
  semantics and no medical payload/P0/model/GPU.
- Deployment verification creates no release/license/target assumption, P0,
  architecture, compute, outer test or submission identity. Future authorized
  execution remains `introai9`-only; `junjinyong` remains excluded.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `docs/server-execution.md`,
  `site/assets/research-data.js`.

## 2026-08-10 · TopBrain 2.0 proposal remains below source admission

- Verified the official Zenodo record, 35-page/139,840-byte design PDF,
  under-construction challenge page and exact TopBrain 2025 evaluation-
  repository head. Schema 6.0 later corrected the design-object license and
  Join-registration wording without changing this scoring decision.
- Froze six candidate scores at **29.0/28.5/28.0/27.5/27.0/23.5**. Planned
  aneurysm cases are vessel-anatomy robustness context, not a released lesion
  target; TopBrain 1, TopAneu, RSNA multitask and topology/connectivity methods
  are direct priors.
- Historical schema 5.9 preserved active shortlist/primary/medical payload/P0/method/
  architecture/PBS/GPU/outer test/C21 at zero. No score repair or scheduler job
  was created. Future authorized execution remains `introai9`-only;
  `junjinyong` is fully excluded.
- 영향 파일: `docs/topbrain2-source-audit-2026-08-10.md`, machine protocol,
  validator/tests, research docs, site, `AGENTS.md` and private paper history.

## 2026-08-10 · RSNA registry content and live site verified

- Exact scientific content `5690b104e6d3fc2644b3d934e12b834ea2c3c3da`
  passed Quality run `31352980950` and Pages run `31352980597`.
- Live overview, zero-assumption guide and detailed audit return HTTP 200 and
  render the same 31.5/40, `ControlledAccess`, vessel-anatomy-not-lesion-mask
  and no-P0/model/GPU boundary.
- Deployment verification creates no terms acceptance, access request, P0,
  architecture, compute, outer test or submission identity. `introai9` remains
  the only possible future execution target after a fresh gate;
  `junjinyong` remains excluded.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `docs/server-execution.md`,
  `site/assets/research-data.js`.

## 2026-08-10 · RSNA AWS registry correction remains below source admission

- Official AWS registry YAML blob `97b8c1f…` at exact file commit `523ffd3…`
  reports 4,000+ scans, 40+ radiologists, about 200 AI-segmented studies and 18
  institutions, correcting the earlier registry-visibility boundary.
- The resource is explicitly controlled-access; the wiki remains `Coming soon`,
  terms/request/S3/payload access are zero, and registry/competition modality
  plus reader/center/sealed-test contracts remain unresolved.
- Point/presence/territory supervision and 13-class vessel masks are preserved;
  vessel masks are not relabeled as aneurysm extent. Winning RSNA systems and
  conformal object/instance risk control remain direct priors.
- The frozen candidate score is **31.5/40**, so schema 5.8 retains no active
  shortlist, primary, P0, method, architecture, PBS/GPU, outer test, C21/result
  row or submission identity. Future authorized execution remains
  `introai9`-only; `junjinyong` remains excluded.
- 영향 파일: detailed audit, protocol/validator/tests, synchronized research
  documents, public site, private manuscript boundary, `AGENTS.md` and this log.

연구 결정, 데이터 계약, 모델 설계, 실험 프로토콜, 사이트 변경을 함께
기록한다. 단순 오탈자는 묶어서 기록할 수 있지만 연구 주장을 바꾼 변경은
독립 항목으로 남긴다.

## 2026-08-10 · Broad-registry content and live site verified

- Exact scientific content `162903a6b66a9982c011fd96d8faf99e92de7eda`
  passed Quality run `31351395527`.
- Pages run `31351394932` succeeded. Its API head metadata remained at the
  preceding public SHA, so it is not represented as an exact-content pin;
  direct live checks of overview, Learn and the detailed audit returned HTTP
  200 and rendered the current broad-registry 30.5/40, all-rejected,
  no-payload/P0/model/GPU boundary.
- Deployment verification creates no access request, P0, architecture, compute,
  outer test or submission identity. `introai9` remains the sole future
  execution target and `junjinyong` remains excluded.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `docs/server-execution.md`,
  `site/assets/research-data.js`.

## 2026-08-10 · Broad-registry audit rejects restricted and pseudoreplicated leads

- A bounded official-metadata screen covered 100 recent Zenodo records from a
  1,226-record broad query, 196 DataCite dataset hits, 100 Figshare hits,
  approximately 20 Dryad hits and the prior 49-record exact-title history.
- Six frozen candidates score **30.5/29.5/26.0/26.0/24.5/18.0**, all below 32.
  LargeIA is restricted and direct-prior dense; the 2015 CFD Challenge has only
  five independent anatomies despite 28 submissions; longitudinal SIG, aSAH
  hydrocephalus and VWI expose supplement-only/directly occupied endpoints;
  synthetic DSA is embargoed past the ISBI deadline.
- No access request, patient/image/mesh/spreadsheet/document/model payload,
  executable P0, PBS/GPU job, method, architecture, outer test or claim was
  created. The two bounded `introai9` name scans produced no artifact, so asset
  presence is not established rather than declared absent. `junjinyong` was not
  accessed and remains excluded.
- Schema 5.7, validator mutation guards, the detailed source audit, research/
  data/method/experiment/ISBI/server documents and the beginner-facing site now
  expose the same 30.5/40 normal early-stop boundary.
- 영향 파일: `docs/broad-registry-source-audit-2026-08-10.md`, machine protocol,
  validator/tests, public site, synchronized research documents, `AGENTS.md`
  and this changelog.

## 2026-08-10 · Registry-gap deployment and private-paper sync verified

- Exact public content `b4c3d48a107b969ce26cbc86abd9b36814116a3a`
  passed Quality `31349424733` and Pages `31349424311`.
- Live overview, Learn guide and detailed audit return HTTP 200 and show the
  same 26.5/40, all-rejected, no-payload/P0/model/GPU boundary.
- Private paper head `2403b746e8bbc663f87e08cc8493f5ed31cc85ab`
  pins the exact public content and records this batch only as unnumbered
  rejected history. The repository is private; unauthenticated GitHub API
  access returns 404. No credential or private result was copied publicly.
- Deployment verification changes no source score, gate, scientific verdict,
  architecture, compute authorization or submission identity. `introai9`
  remains the only future execution target and `junjinyong` remains excluded.

## 2026-08-10 · Registry-gap audit rejects test-only and endpoint-mismatched assets

- The official exact-title Zenodo query returned 49 records. Five previously
  unregistered candidate problems score **26.5/26.0/26.0/25.5/23.5**, all below
  the frozen 32/40 admission line.
- The two rupture-status blobs are public but test-only and lack a public
  development cohort, exact patient/center/raw-CTA lineage and prospective
  endpoint. TransIAR and GN-Net are direct method priors; reading the labels
  during development would also destroy the outer-test role.
- The VWE source is a 41-unruptured-aneurysm scalar association table; the CFD
  release is solver infrastructure; processed post-presentation transcriptomics
  has no casewise imaging bridge; the autopsy record has no casewise geometry
  asset. None identifies an ISBI learning target.
- Schema 5.6 records no payload, P0, PBS/GPU job, method, architecture, outer
  test or claim. Future authorized execution remains `introai9` PBS only;
  `junjinyong` remains excluded from connection, query, submission and
  monitoring.
- 영향 파일: `docs/registry-gap-source-audit-2026-08-10.md`, machine protocol,
  validator/tests, public site, research/experiment/dataset/literature/ISBI/
  server documents, private paper boundary and this changelog.

## 2026-08-10 · Method--asset viability stops before payload and compute

- Royal reference-morphometry certification, partial-observation
  solution-functional operators, IAVS topology-to-CFD reliability, RSNA
  reader-source reliability and CQ500 provenance-aware adaptation score
  **30.0/30.0/29.0/26.0/23.0**. All are below 32.
- COMPASS, conformal volumetry, NeckSpline, anatomical/morphological conformal
  sets, Neural Operator Processes, learned boundary extensions and amortized
  conditioning occupy the tempting method components. Historical N1c remains
  failed; no generic joint density, GNN or conformal wrapper is promoted.
- Exact public heads are unchanged for Royal, AneuG-Flow and IAVS. IAVS remains
  README-only; RSNA remains controlled without user-accepted terms or a public
  per-reader manifest; the cited CQ500-IA public Git remote is unresolved.
- Schema 5.5 freezes shortlist/primary/P0/method/architecture/PBS/GPU/outer test/
  submission identity at zero. `introai9` public-key access succeeded and its
  PBS list was empty. No login-node GPU command ran and `junjinyong` was not
  accessed.
- Exact content `3d21c005bd97b58e87310c3aee9989e91f78e61f` passed Quality
  `31347355040` and Pages `31347354527`; the live `/site/` and detailed audit
  return HTTP 200 with the frozen 30.0/40 boundary.
- 영향 파일: `docs/method-asset-viability-source-audit-2026-08-10.md`, machine
  contract/validator/tests, research/data/model/experiment/ISBI/server guides,
  public site, private manuscript history, `AGENTS.md` and this log.

## 2026-08-10 · Reconstruction/annotation reliability stops before payload and compute

- One-sided outer-annotation morphometry, sparse-view DSA neck reconstruction,
  software/threshold-orbit calibration, phantom consistency, biplane posterior
  reconstruction and reconstruction-to-hemodynamic propagation score
  **31.5/29.5/29.0/26.5/25.5/25.5**. All are below 32.
- The open TOF-MRA lineage has 284 subjects and four-times-faster weak spheres.
  VP-UNet uses 246 coarse-label subjects, a 38-subject precise test set and 113
  external ADAM subjects; FocalSegNet and CVPR 2026 WeakMed are direct priors.
  A public same-subject real-weak versus independently precise annotation
  manifest is absent.
- The 600-model study is author-request data without a public per-case orbit.
  The 202-patient sparse-view DSA, 150-aneurysm biplane reconstruction and
  one-anatomy phantom do not supply the residual independent target.
- Schema 5.4 freezes shortlist/primary/method/architecture/P0/PBS/GPU/outer
  test/submission identity at zero. No `introai9` job was needed;
  `junjinyong` remains excluded. Closed branches are not repaired or rerun.
- Exact content `41d579c0963bd3c7f72c2cd372f1c3cf3dbd77f1` passed Quality
  `31345064183` and Pages `31345063921`; the live site and detailed audit return
  HTTP 200 with the frozen 31.5/40 boundary.
- 영향 파일: `docs/reconstruction-annotation-reliability-source-audit-2026-08-10.md`,
  machine contract/validator/tests, research/data/model/experiment/ISBI/server
  guides, public site, private manuscript history, `AGENTS.md` and this log.

## 2026-08-10 · Failure-mechanism/biology batch stops before payload and compute

- Cause-specific CTA false-positive risk, post-release TopAneu attachment,
  directional topology, synthetic-avatar fidelity, preclinical ingrowth
  translation and imaging--spatial-wall alignment score
  **30.5/29.0/28.0/25.5/24.5/21.0**. All are below 32.
- The strongest direct study already tests anatomy-compartment filters using
  1,186 open training CTAs and two external cohorts, but public casewise
  false-positive cause labels are absent. Directional SECT independently
  occupies the small-lesion/bifurcation topology path.
- TopAneu now states open use with attribution and about 850 scans, but still
  requires a verified account. No join request, terms acceptance or payload
  access was performed. Paired image--tissue and angiography--histology targets
  are absent; ICAN's downloadable table is explicitly simulated.
- Schema 5.3 freezes active shortlist/primary/method/architecture/P0/PBS/GPU/
  outer test/submission identity at zero. No `introai9` job was created;
  `junjinyong` remains excluded from connection, query, submission and
  monitoring. The closed Aneumo P0 is not repaired or rerun.
- Exact audit content `e954d7d8852498d99e7063891d33d36a967e4284` passed Quality
  run `31343371108` and Pages run `31343370635`; the live site and detailed
  audit both returned HTTP 200 with the frozen 30.5/40 boundary.
- 영향 파일: `docs/failure-mechanism-biology-source-audit-2026-08-10.md`,
  machine contract/validator/tests, research/data/model/experiment/ISBI/server
  guides, public site, private manuscript history, `AGENTS.md` and this log.

## 2026-08-10 · Current-site panels align with the Aneumo lineage outcome

- Replaced stale longitudinal-perfusion and historical AneuX text in the live
  current-gap, decision-boundary, beginner architecture and paper-status panels.
- The site now distinguishes 0 case overlap from 20/20 base-family overlap,
  explains why split repair is evaluation hygiene rather than novelty, and
  shows the exact P0 incomplete/no-verdict/no-model boundary throughout.
- Historical branches remain available as history; no research authorization,
  method, architecture, GPU, outer test or claim changed.

## 2026-08-10 · Aneumo lineage P0 closes without a scientific verdict

- Exact public source `d3eb3d3…` ran once on `introai9` as CPU/PBS job
  `115386.ECE-util1`: final state `F`, exit `-29`, walltime 20:36, CPU time 0,
  GPU 0.
- No first small source completed. Completed/partial cache, result JSON and raw
  scheduler log are absent; all 11 registered high-level checks are unevaluated.
- Schema 5.2 preserves the 20/20 source-level family-overlap finding but closes
  this candidate version as execution-incomplete with no scientific verdict.
  Active shortlist, P1, primary, model, GPU and outer test return to zero.
- No transport repair or same-contract rerun is allowed. `junjinyong` was not
  accessed and remains excluded.
- Exact outcome content `5b98fa296bc7e25f2a3cff97a4a0e3df81c64f8a`
  passed Quality run `31341512723` and Pages run `31341512255`.

## 2026-08-10 · Aneumo generation-lineage candidate opens one CPU metadata P0

- Corrected official mapping commit `701d53d…` exposes 10,660 generated cases
  from 427 base families. The official validation has zero exact case overlap
  with training but shares all 20 base families.
- Six frozen scores are **35.0/31.5/31.0/29.0/27.0/29.5**. Only
  generation-family-disjoint operator model selection crosses 32, opening one
  exact method-free metadata P0—not a method or paper contribution.
- Schema 5.1 pins GitHub/Hugging Face commits, hashes, mapping/split counts and
  the CC BY 4.0 versus CC BY-NC-ND 4.0 conflict. P0 may read small text/CSV and
  Git LFS pointer text only; archive objects/members, model, GPU and outer test
  remain forbidden.
- Execution is `introai9` PBS CPU only. `junjinyong` remains excluded from
  connection, query, submission and monitoring.

## 2026-08-10 · Longitudinal-MRA rejection is live and verified

- Exact content `24c95c17042187ad43b0f16b76962f083bc8a053` passed Quality run
  `31338069136` and Pages run `31338068734`.
- The live overview renders best 31.5/40, all rejected and no active shortlist,
  selected primary, model or GPU. The detailed audit is publicly reachable and
  preserves no annotation/image/mesh payload, P0, PBS or outer test.
- Deployment verification changes no scientific verdict or compute authority.
  Future AURORA execution remains `introai9` PBS only, and `junjinyong` remains
  excluded from connection, query, submission and monitoring.

## 2026-08-10 · Longitudinal-MRA growth batch stops before payload and compute

- Acquisition-orbit-calibrated growth, single-anchor localization,
  interval-censored forecasting, mixed-modality harmonization, AWE instability
  and post-flow-diverter multimodal disagreement score
  **31.5/29.0/30.0/26.5/26.5/26.0**. All are below 32.
- OpenNeuro `ds005096` has 63 patients, 85 aneurysms, 24 longitudinal patients
  and 126 raw angiogram paths, but only four patients have same-session
  acquisition pairs. Expert derivatives cover one selected session per subject.
- The newest Bayesian direct prior uses 16 public patients/19 aneurysms with six
  growth positives and already includes surface registration, a healthy-vessel
  internal control, measurement error and calibrated probabilities.
- Schema 5.0 freezes no annotation spreadsheet/participant table/sidecar/NIfTI/
  segmentation/Slicer/STL payload, P0/model/PBS/GPU/outer test, `introai9`-only
  future execution and complete exclusion of `junjinyong`.
- 영향 파일: `docs/longitudinal-mra-growth-source-audit-2026-08-10.md`, machine
  contract/validator/tests, public research/data/server guides, educational
  site, private manuscript history and this changelog.

## 2026-08-10 · Longitudinal-perfusion rejection is live and verified

- Exact source content `7b03ace12b1e05329e47cd46b6968c0359143daa` passed
  Quality run `31336277131`; Pages run `31336276517` also succeeded.
- The live overview renders 62 patients/291 exams/873 maps, nine DCI events,
  best 31.0/40, all rejected and shortlist/primary/method/architecture/P0/PBS/
  GPU zero. The beginner window and detailed audit URL both resolve.
- Deployment verification changes no score, payload, method, compute, outer
  test or submission identity. `introai9` remains exclusive and `junjinyong`
  remains excluded.

## 2026-08-10 · Longitudinal-perfusion batch stops before payload and compute

- Informative-scan-aware CTP field forecasting, pre-DCI warning, personalized
  reacquisition, treatment counterfactual, 3DRA–CTA invariance and global–local
  VWE discordance score **31.0/29.0/28.0/27.0/29.5/29.0**. All are below 32.
- The open CC0 release has 62 patients, 291 original exams, 873 maps and nine
  DCI events. Scan timing is clinically informative and CTP guides rescue
  treatment; repeated maps and interpolants are not independent natural-history
  outcomes.
- ImageFlowNet, longitudinal latent diffusion, TESAR-CDE and existing CTP/NCCT
  DCI models are direct priors. The paired 3DRA–CTA and VWE records expose only
  small tabular summaries and their papers directly occupy the associations.
- Schema 4.9 freezes no standalone payload, P0/model/PBS/GPU/outer test,
  `introai9`-only execution and complete exclusion of `junjinyong`.
- 영향 파일: `docs/longitudinal-perfusion-source-audit-2026-08-10.md`, machine
  contract/validator/tests, public research/data/server guides, educational
  site, private manuscript history and this changelog.

## 2026-08-10 · FSI–wall rejection is live and verified

- Exact source content `f92bae804469d806e3d48079246a2a889a97c08a` passed
  Quality run `31334866427`; Pages run `31334866034` also succeeded.
- The Pages build API exposed stale/racing prior-SHA metadata, so it is not
  represented as an exact-content pin. Direct live checks render FSI–wall best
  31.0/40, all rejected, shortlist/primary/method/architecture/P0/GPU zero and
  the detailed audit URL returns HTTP 200.
- Deployment verification changes no score, payload access, P0, model, compute,
  outer test or submission identity. `introai9` remains exclusive and
  `junjinyong` remains excluded.

## 2026-08-10 · FSI–wall batch is rejected before payload and compute

- Rigid-to-compliant discrepancy, inverse wall property, device response,
  wall-thickness hotspot, selective FSI referral and multi-granularity conformal
  surrogation score **30.5/29.5/26.5/24.5/29.0/31.0**. All are below 32/40.
- AnXplore reports 101 rigid/FSI simulations, but its verified public
  full-dataset tree exposes 101 fluid meshes rather than paired time-resolved
  rigid/FSI solution fields. An animal inverse-mechanics record and five-
  aneurysm micro-CT wall-thickness study cannot supply target-scale labels.
- Generic FSI neural operators, multi-fidelity residual learning and conformal
  selective referral are direct priors or controls, not standalone novelty.
- Schema 4.8 freezes no mesh/field/image payload, P0/model/PBS/GPU/outer test,
  `introai9`-only execution and complete exclusion of `junjinyong`.
- 영향 파일: `docs/fsi-wall-source-audit-2026-08-10.md`, machine contract,
  validator/tests, public research/data/server guides, educational site and this
  changelog.

## 2026-08-10 · Acquisition–flow batch is rejected before access and compute

- CMRx4DFlow2026 reports 400+ cases, 138 fully sampled training cases and
  dedicated new-site/disease and cross-anatomy tasks, but independent research
  use is embargoed until December 2026—after the ISBI submission deadline.
- Nested acceleration, cross-domain reconstruction, explicit multi-VENC
  uncertainty, functional WSS risk and treated-aneurysm transfer score
  **27.5/26.5/24.0/26.0/27.0**. All are below 32/40.
- FlowMRI-Net, DAF-FlowNet and VAST are direct priors. CMRx does not report
  same-case repeat multi-VENC acquisitions; the open aneurysm record has eight
  scans but one effective anatomy.
- Schema 4.7 freezes no Synapse application/form/terms, k-space/MAT, aneurysm
  ZIP, P0/model/GPU/outer test, `introai9`-only execution and complete exclusion
  of `junjinyong`.
- 영향 파일: `docs/acquisition-flow-source-audit-2026-08-10.md`, machine
  contract/validator/tests, public research and dataset guides, site status and
  this changelog.

## 2026-08-10 · Treatment–surveillance rejection is deployed and verified

- Exact content `9080f4fea64bbad968e5a2508fa79d1a2f4da4d4` passed Quality
  run `31332304523` and Pages run `31332303841`.
- The live overview and field guide render best 30.0/40, all rejected,
  shortlist/primary/method/architecture/P0/GPU zero and the detailed audit link;
  the detailed Markdown URL returns HTTP 200.
- Deployment verification changes no score, payload access, P0, model, compute,
  outer test or submission identity. `introai9` remains exclusive and
  `junjinyong` remains excluded.

## 2026-08-10 · Treatment–surveillance source audit rejects all five candidates

- Public flow-diverter follow-up data report 126 subjects/141 procedures,
  complications and at most two irregular DSA follow-up observations. Device
  assignment is not randomized and exact biological occlusion time is not
  observed.
- Observed interval-censored occlusion, causal device selection,
  complication–occlusion utility, recurrent-procedure sequence modeling and
  paired fast/standard TOF-MRA equivalence score
  **30.0/26.0/29.0/26.0/23.0**. All are below the frozen 32/40 line.
- The 22-patient paired MRA source is restricted; its paper already reports
  inter-modality kappa 0.98 using standard TOF-MRA rather than DSA as reference.
- Schema 4.6 freezes no spreadsheet/R document/presentation/DSA/MRA payload,
  no P0/model/GPU/outer test, `introai9`-only execution and complete exclusion
  of `junjinyong`.
- 영향 파일: `docs/treatment-surveillance-source-audit-2026-08-10.md`, machine
  contract/validator/tests, public research and dataset guides, site status and
  this changelog.

## 2026-08-10 · Provenance–evaluation rejection is deployed and verified

- Exact content `4569c32fbdd19ddf34dac74ef840a8bfc6da080a`의 Quality
  `31331100581`과 Pages `31331100307`이 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 batch best
  30.0/40, all rejected, active shortlist/primary/method/architecture/P0/GPU 0과
  detailed audit link를 확인했다. 상세 audit 문서도 HTTP 200이다.
- 배포 검증은 score, archive/mesh/image/spreadsheet access, P0, model, compute,
  outer test 또는 submission identity를 바꾸지 않는다. `introai9`만 허용하고
  `junjinyong`은 계속 제외한다.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `site/assets/research-data.js`.

## 2026-08-10 · Provenance–evaluation batch is rejected before compute

- AneuX/Aneurisk/76-case CFD cross-release lineage, source-selective prediction,
  test-blind external re-evaluation, curator lineage와 multiple-aneurysm set
  consistency를 같은 frozen rubric으로 검토했다. 다섯 점수는
  30.0/29.5/28.5/23.5/25.5이며 모두 admission line 32 미만이다.
- Exact 76-to-101 lesion manifest가 없고 public Aneurisk mirror는 24 named
  model/DICOM folder와 15 label file만 노출한다. Generic patient/source split,
  near-duplicate detection과 cross-corpus contamination audit은 direct prior다.
- Schema 4.5는 active shortlist/primary/P0/method/architecture/GPU를 0으로
  고정한다. `introai9` PBS job은 0이고 새 작업을 제출하지 않았다.
  `junjinyong`은 접속·조회·제출·모니터링하지 않았다.
- 영향 파일: `docs/provenance-evaluation-source-audit-2026-08-10.md`, machine
  contract/validator/tests, overview documents, site, `AGENTS.md`.

## 2026-08-10 · Context–treatment batch is rejected before compute

- AneuSI, paired black-blood/4D-flow treatment MRI, DIVA-seg와 public
  latent-shape implementation을 같은 frozen rubric으로 검토했다. 다섯 점수는
  31.5/27.5/26.0/27.0/30.0이며 모두 admission line 32 미만이다.
- AneuSI의 parent-vessel context는 명확한 same-case ablation이지만 rupture
  morphology/point-cloud/vessel-graph direct prior가 강하다. Paper 102 case와
  repository 103 named case의 mapping도 미해결이며 spreadsheet/VTK는 열지
  않았다. Treatment MRI의 effective anatomy는 2다.
- Schema 4.4는 active shortlist/primary/P0/method/architecture/GPU를 0으로
  고정한다. `introai9` PBS job은 0이고 새 작업을 제출하지 않았다.
  `junjinyong`은 접속·조회·제출·모니터링하지 않았다.
- 영향 파일: `docs/context-treatment-source-audit-2026-08-10.md`, machine
  contract/validator/tests, overview documents, site, `AGENTS.md`.

## 2026-08-10 · Topology–procedure source rejection is deployed and verified

- Exact content `3f8e0a5d2c570cfb1c75f22f34d3989fdd5ff71d`의 Quality
  `31327799890`과 Pages `31327799626`이 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 batch best
  28.5/40, all rejected, active shortlist/primary/method/architecture/P0/GPU 0과
  latest detailed audit link를 확인했다. 상세 audit 문서도 배포됐다.
- 배포 검증은 score, archive/model-weight/patient-image access, P0, model,
  compute, outer test 또는 submission identity를 바꾸지 않는다. `introai9`만
  허용하고 `junjinyong`은 계속 제외한다.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `site/assets/research-data.js`.

## 2026-08-10 · Fresh topology–procedure source batch is rejected before compute

- A new preprint and CC BY 4.0 Figshare record already define tornadic WSS
  topology and its in-vivo 4D-flow observation. Public data names three CFD WSS
  cases and two MRI figure cases, with no reported same-case pair.
- Robust WSS topology, set-valued C-arm view prediction, differential-diagnosis
  TOF detection and rheology/slip uncertainty do not rescue the gap. MAXIMUS is
  weights-only, the view cohort is 18 patients and the solver release contains
  one aneurysm geometry.
- Five frozen scores are 24.0/28.5/24.0/28.5/28.5. No large archive, model
  weight, patient image, P0, method, architecture, PBS/GPU, outer test or
  submission identity is opened. Machine contract is schema 4.3 and execution
  remains `introai9`-only with `junjinyong` excluded.
- 영향 파일: `docs/topology-procedure-source-audit-2026-08-10.md`,
  `configs/aurora_v1.json`, validator/tests, overview documents, site data and
  `AGENTS.md`.

## 2026-08-10 · Hemodynamic–endpoint source rejection is deployed and verified

- Exact content `318a22a06a1a0d1ad8339183f290e1648c656fed`의 Quality
  `31326443420`과 Pages `31326443150`이 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 batch best
  31.0/40, all rejected, active shortlist/primary/method/architecture/P0/GPU 0과
  latest detailed audit link를 확인했다. 상세 audit 문서도 배포됐다.
- 배포 검증은 score, archive/payload access, scientific verdict, P0, model,
  compute, outer test 또는 submission identity를 바꾸지 않는다. `introai9`만
  허용하고 `junjinyong`은 계속 제외한다.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `site/assets/research-data.js`.

## 2026-08-10 · Fresh hemodynamic–endpoint source batch is rejected before compute

- New Zenodo `10.5281/zenodo.19455127` reports 76 Aneurisk geometries with
  OpenFOAM-derived VTP surface fields under CC BY 4.0. Its inflow is based on two
  population age-group waveforms scaled by inlet diameter, not measured
  patient-specific physiology. The record's outlet summary also differs from the
  companion paper's resistance-pressure description.
- Five frozen candidates score 31.0/30.0/23.0/25.0/26.0. Curvature-only local
  hemodynamic surrogation is best at 31.0/40 but the companion paper already
  frames curvature as a CFD proxy, while geometry-to-flow models are direct
  controls. Multiple-aneurysm culprit ranking, treated-remnant change and spatial
  wall-enhancement/WSS tasks are directly occupied and lack public endpoint maps
  or independent patient units.
- No 1.4 GB archive, VTP, clinical image or private cohort was accessed. No P0,
  method, architecture, PBS/GPU job, outer test or submission identity was
  created. Machine contract is schema 4.2; execution remains `introai9` PBS only
  and `junjinyong` remains excluded.
- 영향 파일: `docs/hemodynamic-endpoint-source-audit-2026-08-10.md`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  overview documents, site data and `AGENTS.md`.

## 2026-08-10 · PINN direct-prior audit is deployed and verified

- Exact content `ed426a58d556e987c4b5d745d9eb7c88c793a9fe`의 Quality
  `31325129769`와 Pages `31325129336`이 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 original
  geometry + PINN + clinical identity의 direct-prior 점유, residual 23.5/40
  rejection, active shortlist/primary/model/GPU 0과 latest audit link를 확인했다.
  Detailed audit URL도 HTTP 200이다.
- 배포 검증은 candidate score, payload access, P0, method, architecture, GPU,
  outer test 또는 submission identity를 바꾸지 않는다. `introai9`-only 및
  `junjinyong` excluded 경계를 유지한다.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `site/index.html`,
  `site/assets/research-data.js`.

## 2026-08-10 · Geometry + PINN + clinical fusion is rejected as direct prior

- A July 2026 preprint already combines PointNeXt vascular geometry,
  geometry-conditioned PINN pressure/velocity/WSS/TAWSS/OSI/RRT and clinical
  variables on 735 AneuX cross-sectional rupture-status lesions. Reported
  late-fusion AUROC/AUPRC 0.827/0.732 is prior-work evidence, not an AURORA result.
- The official AneuX source reports 750 lesions, 668 vessel trees and 605 patients.
  The direct-prior primary models are described as stratified five-fold, while
  only a separate tabular feature analysis explicitly says patient-aware. Primary
  patient/vessel-family grouping therefore remains unverified rather than assumed.
- PINN fields use prescribed shared conditions without patient-specific BC, paired
  CFD or in-vivo validation. Residual-loss convergence is not physiological
  validation, and cross-sectional status is not future rupture probability.
- The residual physically validated incremental-information candidate scores
  23.5/40, below the frozen 32/40 line. No payload, P0, method, architecture,
  PBS/GPU job, outer test or submission identity is created.
- Machine contract is schema 4.1. AURORA execution remains `introai9` PBS only;
  `junjinyong` is excluded from connection, query, submission and monitoring.
- 영향 파일: `docs/pinn-rupture-direct-prior-audit-2026-08-10.md`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `README.md`, `docs/research-direction.md`, `docs/literature-lineage.md`,
  `docs/model-spec.md`, `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/datasets.md`, `site/index.html`, `site/learn.html`,
  `site/assets/research-data.js`, `AGENTS.md`, `CHANGELOG.md`.

## 2026-08-10 · Vascular-semantics audit is deployed and verified

- Exact content `f735ab5a2e0eec411142b7834e743d6cf4cd0944`의 Quality
  `31324138662`와 Pages `31324138250`이 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 best 29.5/40,
  all rejected, active shortlist/primary/method/architecture/GPU 0과
  `introai9`-only 경계를 확인했다. 상세 audit 문서도 HTTP 200이다.
- 이 배포 확인은 candidate score, payload, P0, model, GPU, outer test 또는
  submission identity를 바꾸지 않는다.
- 영향 파일: `AGENTS.md`, `CHANGELOG.md`, `site/assets/research-data.js`.

## 2026-08-10 · Fresh vascular-semantics batch is rejected before compute

- Frozen 8축 40점 screen에서 TopBrain paired CTA/MRA anatomy, healthy IXI atlas,
  VesselVerse annotation semantics, NeckSpline extension, paired CTA phantom QA와
  ADAM longitudinal semantics를 29.5/28.5/27.5/26.5/26.0/25.0으로 판정했다.
- TopBrain은 25 paired patient의 48-class anatomy benchmark로 aneurysm endpoint가
  없다. VesselVerse의 “expert”에는 algorithm output이 포함되고 data access는
  email request를 요구한다. Phantom의 126 scan은 한 anatomy·세 병변의 반복이며
  논문이 제시한 URL은 HTTP 404다.
- Admission line 32 미만이므로 score repair, payload, P0, method, architecture,
  GPU와 outer test는 모두 0이다. 향후 실행은 `introai9` PBS만 사용하고
  `junjinyong`은 접속·조회·제출·모니터링하지 않는다.
- Machine contract를 schema 4.0으로 올리고 각 후보의 8개 axis 합계와 no-compute
  경계를 validator/test에 고정했다.
- 영향 파일: `docs/vascular-semantics-source-audit-2026-08-10.md`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `README.md`, `docs/research-direction.md`, `docs/literature-lineage.md`,
  `docs/datasets.md`, `docs/experiment-protocol.md`, `site/index.html`,
  `site/learn.html`, `site/assets/research-data.js`, `CHANGELOG.md`, `AGENTS.md`.

## 2026-08-10 · INSTED clarification is deployed and verified

- Exact content commit `35e925321b083485b6380b2c37493f499997e3c5`의
  Quality run `31322682231`과 Pages run `31322681793`이 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/) change data에서
  published 160-train/40-test challenge, five-year-survival template example와
  historical 26/40 preservation을 확인했다. 상세 문서도 no longitudinal
  outcome/no-score/P0/model/GPU 경계를 반환한다.
- 이 배포는 signup, terms acceptance, payload access, candidate score, method,
  architecture 또는 compute authorization을 바꾸지 않는다.
- 영향 파일: `CHANGELOG.md`, `site/assets/research-data.js`, `AGENTS.md`.

## 2026-08-10 · INSTED source semantics are corrected without score repair

- Official Codabench API는 INSTED를 published CC BY-NC challenge로 확인한다.
  Training 160건은 healthy/IA/stenosis 32/64/64이고 closed test는 40건이다.
  Training asset은 signup 뒤 Files에서 제공된다.
- BIAS design PDF page 11의 5-year survival 문장은 case-definition template의
  example이다. Challenge-specific answer와 metrics는 3D TOF-MRA의 IA/stenosis
  box+segmentation만 정의하며 survival, rupture와 follow-up endpoint는 없다.
- Official code repository exact `e48a9ba16398cca309d932813cda7dd3dc3e4cb9`를
  확인했다. Signup, terms acceptance, image/mask/bbox payload access는 0이다.
- Historical IAIA 26.0/40 rejection을 재채점하지 않고, proposal-only 표현만
  published signup-gated segmentation challenge로 정정한다. Fresh score, P0,
  method, architecture, GPU와 outer test는 열지 않는다.
- 영향 파일: `docs/insted-source-clarification-2026-08-10.md`,
  `docs/source-delta-audit-2026-08-09.md`, `docs/research-direction.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`,
  `docs/experiment-protocol.md`, `site/assets/research-data.js`, `AGENTS.md`,
  `CHANGELOG.md`.

## 2026-08-10 · IAVS watch-only state is deployed and verified

- Exact content commit `ac6a7075d6607ae29d39e77a87d1ecfbcb87147d`의
  Quality run `31322131949`와 Pages run `31322131485`가 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 IAVS
  README-only watch 문구와 상세 문서 링크를 확인했다. 배포된 change data는
  exact upstream `2e40088d9eaa671c592929a154b7b2cf99f9320a`를, 상세 문서는
  `no source score/P0/model/GPU` 경계를 렌더링한다.
- 이 배포 확인은 source score, candidate admission, payload access, method,
  architecture, GPU 또는 outer-test 권한을 바꾸지 않는다. Scientific execution은
  계속 `introai9`만 사용하고 `junjinyong`은 제외한다.
- 영향 파일: `CHANGELOG.md`, `site/assets/research-data.js`, `AGENTS.md`.

## 2026-08-10 · IAVS is frozen as a watch-only external source

- IAVS paper는 641개 3D MRA, 587개 aneurysm–parent-vessel annotation과 CFD
  outcome을 보고하지만, official repository `main` exact
  `2e40088d9eaa671c592929a154b7b2cf99f9320a`에는 90-byte README 한 파일만
  있다. Release 0, explicit repository license 0, payload/code 0이다.
- 논문 자체의 two-stage localization/segmentation과 CFD Applicability Score를
  direct prior로 올렸다. Generic segmentation→CFD evaluation, topology metric,
  U-Net/GNN/Transformer 또는 uncertainty head는 독립 novelty가 아니다.
- `configs/source_watch_v1.json`과 standard-library validator는 official metadata
  변화만 감지한다. 변화가 생겨도 fresh source audit만 요청하며 automatic
  download/terms acceptance/P0/method/architecture/GPU/outer test는 모두 false다.
- `introai9` public-key 접속과 PBS AURORA job 0을 재확인했다. Login-node GPU
  명령은 실행하지 않았고 `junjinyong`에는 접속·조회·제출·모니터링하지 않았다.
- 영향 파일: `configs/source_watch_v1.json`, `src/aurora/source_watch.py`,
  `scripts/audit_source_watch.py`, `tests/test_source_watch.py`,
  `docs/source-watch.md`, `README.md`, `docs/research-direction.md`,
  `docs/model-spec.md`, `docs/experiment-protocol.md`, `docs/datasets.md`,
  `docs/literature-lineage.md`, `docs/isbi-2027-plan.md`,
  `docs/server-execution.md`, `site/index.html`, `site/assets/research-data.js`,
  `AGENTS.md`, `CHANGELOG.md`.

## 2026-08-09 · Source-delta decision is deployed and verified

- Exact content commit `8d7f7d7d4e41c72eafb1dd08ae27d843ee00fc54`의
  Quality run `31303877413`과 Pages run `31303877371`이 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 source-delta
  best 31.5/40, all rejected, active shortlist/selected primary/model/GPU 0과
  “현재 GNN·U-Net·Transformer가 없다”는 경계를 확인했다. Latest-audit link는
  공개 source-delta 문서를 가리킨다.
- 이 배포 확인은 score, terms acceptance, payload/P0, method, architecture, GPU
  또는 submission authorization을 바꾸지 않는다. 실행 대상은 계속
  `introai9`뿐이며 `junjinyong`은 제외한다.
- 영향 파일: `AGENTS.md`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Fresh source-delta batch is rejected before P0

- OpenNeuro longitudinal surface growth, RSNA anatomy-indexed point-set detection,
  VICTORIA neck-curve distribution, IntrA topology control, IAIA aneurysm–stenosis와
  flow-diverter DSA outcome을 같은 frozen 40점 rubric으로 감사했다. 점수는
  31.5/30.5/30.5/28.5/26.0/25.5이며 모두 admission line 32 미만이다.
- 최고 OpenNeuro 후보도 동일 공개 cohort의 Bayesian surface-displacement growth
  direct prior와 24 longitudinal patient의 effective-unit 한계가 있다. RSNA는
  controlled-access terms를 사용자가 수락하지 않았고 공식 supervision은
  aneurysm extent mask가 아니다. VICTORIA의 reader 55명은 독립 geometry 5개를
  대체하지 않는다.
- `introai9` 실제 login boundary의 공개키 접속과 PBS AURORA job 0을 확인했다.
  Known source root를 bounded read-only로 감사했으며 IntrA는 repository skeleton만
  확인됐다. Login-node GPU command는 실행하지 않았고 `junjinyong`에는 접속·조회·
  제출·모니터링하지 않았다.
- Schema를 3.9로 올리고 all-six rejection, score/no-repair, no-payload/P0/method/
  architecture/GPU와 `introai9`-only idle boundary를 validator/test로 고정했다.
- 영향 파일: `docs/source-delta-audit-2026-08-09.md`, `AGENTS.md`, `README.md`,
  `docs/research-direction.md`, `docs/model-spec.md`, `docs/experiment-protocol.md`,
  `docs/isbi-2027-plan.md`, `docs/literature-lineage.md`, `docs/datasets.md`,
  `docs/server-execution.md`, `configs/aurora_v1.json`, `src/aurora/protocol.py`,
  `tests/test_protocol.py`, `site/index.html`, `site/learn.html`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · DSA source rejection is deployed and verified

- Exact content commit `4600d9c45b257c99db1c294ca4481724ede0b360`의
  Quality run `31301858683`과 Pages run `31301858151`이 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 six-candidate
  audit, DIAS source rejection 31/40, active shortlist 0을 확인했고, 상세
  설명 페이지에서 `no payload/P0/model/GPU`와 현재 architecture가 없다는
  경계를 확인했다. 공개 source-audit 문서도 동일한 31.0/40 판정을 렌더링한다.
- 이 배포 확인은 candidate 점수, dataset access, P0/model/GPU 권한 또는
  scientific verdict를 바꾸지 않는다. 향후 실행 대상은 계속 `introai9`만이며
  `junjinyong`은 접근·조회·제출·모니터링에서 제외한다.
- 영향 파일: `AGENTS.md`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · DSA prefix-risk candidate is rejected at source audit

- Fresh six-candidate red team의 최고 후보는 DIAS DSA prefix로 final merged
  vessel support와 thin-vessel miss risk를 추론하는 문제였으나 **31.0/40**으로
  automatic admission 기준 32에 못 미쳤다. Active shortlist, selected primary,
  method와 architecture는 모두 0이다.
- Official DIAS paper/Zenodo/repository에서 60 patient, 120 sequence, 60 fully
  annotated sequence, expert-preselected 4--14 arterial frame, CC BY 4.0과
  292,444,663-byte archive MD5를 source-only로 확인했다. Paper summary의 753
  frame과 collection section의 762 image 불일치는 payload audit 전 unresolved다.
  Dataset payload, frame, label과 patient identifier는 읽지 않았다.
- 원 논문의 full sequence/minimum projection DSC는 0.7822/0.7802로 차이가
  0.0020이다. VSS-Net, DSCA, TemSAM, incomplete-angiogram temporal recovery,
  SAFE-KD류 early exit와 conditional conformal segmentation을 direct prior로
  올렸다. Temporal encoder, MIP prompt, arrival map, stopping head와 conformal
  wrapper를 단독 novelty로 세지 않는다.
- Release는 raw full-phase acquisition, frame exposure/dose, prospective stop
  action과 frame-level arrival ground truth를 제공하지 않는다. 따라서
  `acquisition stopping`, dose reduction과 clinical utility를 endpoint로 쓰지
  않고 score를 thin-vessel metric으로 사후 수리하지 않는다.
- Known `introai9` dataset root의 bounded read-only inventory에서 DIAS staging은
  확인되지 않았다. Source gate가 닫혔으므로 download, executable P0, PBS job,
  model, checkpoint와 GPU를 만들지 않았다. `junjinyong`은 접속·조회·제출·
  모니터링에서 계속 제외한다.
- Central schema는 `3.8`이며 protocol validator 15 invariant group, focused
  protocol test 92개와 전체 unit suite 292개가 통과했다(63개 environment-dependent
  test는 기존 skip contract 유지).
- 영향 파일: `docs/dsa-prefix-risk-audit-2026-08-09.md`, `AGENTS.md`, `README.md`,
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`, `docs/server-execution.md`,
  `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`, `site/index.html`,
  `site/learn.html`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Closed AneuX P0 state is deployed

- Exact outcome content commit `f4cbf727364325a32f6da148189b976be9d22c6f`의
  Quality run `31299794163`과 Pages run `31299793742`가 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 active shortlist
  0, AneuX P0 execution-incomplete/no scientific verdict, no P1/model/GPU와 fresh
  problem/source-audit-only 경계를 확인했다.
- 공개 [execution record](https://gohyunsu.github.io/aneurysm/results/aneux_preprocessing_orbit_p0_execution_20260809.json)도
  candidate closed, scheduler exit 2와 scientific gate unevaluated를 렌더링한다.
  이 배포 확인은 P0를 평가·수리하거나 candidate를 재개방하지 않는다.
- 영향 파일: `AGENTS.md`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · AneuX preprocessing-orbit P0 closes execution-incomplete

- Exact public source `42cc3c7127f382b440f2ac22f662c45692f37863`의
  `introai9` CPU/PBS job `115177.ECE-util1`을 4 CPU/16 GB/GPU 0으로 정확히
  한 번 실행했다. PBS는 exit 2, walltime `00:37:00`, CPU time `00:00:00`,
  peak memory `26596kb`, run count 1을 기록했다.
- Privacy-safe result는 `transport_attempts_exhausted`를 기록했다. 첫 official
  tabular archive가 완성되기 전 bounded attempt가 소진돼 completed/partial
  cache file은 0이고 CSV member는 parse되지 않았다. Model archive HEAD/range,
  central directory와 member payload도 접근하지 않았다. Transient transfer
  byte 수와 low-level exception은 aggregate로 식별하지 않는다.
- 13개 asset/unit check는 모두 미평가다. 이는 AneuX나 preprocessing-orbit
  가설의 scientific failure가 아니다. Frozen no-resubmission rule에 따라
  transport/reader repair, same-contract rerun, P1, method, architecture, GPU,
  outer test와 submission identity를 열지 않고 candidate version을 닫았다.
  Active shortlist는 0으로 돌아갔다.
- 공개 execution record는
  `results/aneux_preprocessing_orbit_p0_execution_20260809.json`, SHA-256은
  `ba547b9855229d59fd2ca79293e870828d878ad0b818ca4bb904eb29defde05a`다.
  Private raw result/status SHA-256은 각각 `f57ef074…333a0`,
  `b278d9f7…5d184`로 고정했다. Raw scheduler stdout/stderr는 materialize되지
  않았다.
- 영향 파일: `results/aneux_preprocessing_orbit_p0_execution_20260809.json`,
  `AGENTS.md`, `README.md`, `docs/aneux-preprocessing-orbit-audit-2026-08-09.md`,
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`, `docs/data-acquisition.md`,
  `docs/server-execution.md`, `configs/aurora_v1.json`, `src/aurora/protocol.py`,
  `tests/test_protocol.py`, `site/index.html`, `site/learn.html`,
  `site/assets/aurora.js`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · AneuX same-lesion preprocessing orbit enters a P0-only shortlist

- Fresh six-candidate red team에서 AneuX resolution × cut variant를 독립 표본이
  아니라 같은 병변의 preprocessing orbit으로 다루는 후보만 **34/40**으로
  admission line을 넘겼다. Active source shortlist는 1이지만 selected primary,
  method, architecture, GPU, outer test와 submission identity는 0이다.
- AneuX 원 morphometry/cut robustness, MATCH reconstruction variability,
  DiffusionNet, AneuX PointNet++, 2026 multi-resolution latent shape, generic
  consistency와 E(3) equivariance를 direct prior/control로 올렸다. 따라서 남을
  수 있는 novelty는 orbit quotient가 casewise functional/prediction stability와
  source-held-out biological separation을 동시에 보존하는 경우로 좁혔다.
- CSV/model payload 전에 `configs/aneux_preprocessing_orbit_p0.json`을 고정했다.
  Official 12,992,074-byte tabular ZIP은 exact MD5와 aggregate patient/cut/
  morphometry mapping을, 6,277,720,483-byte model ZIP은 HEAD/tail/central-directory
  exact range만 검사한다. Full model download와 member payload access는 금지된다.
- Official repository README의 CC BY 4.0 표기와 Zenodo v1.0 distribution
  record의 CC BY-NC 4.0+추가 attribution 조건이 충돌하므로, 배포 record의 더
  엄격한 조건을 적용하고 geometry/table을 공개 저장소에 재배포하지 않는다.
- 실행은 `introai9` PBS의 CPU 4/16 GB/GPU 0 한 번뿐이다. 동일 exact job 안의
  각 HTTP operation의 transient transport에만 0/10/30초 최대 세 attempt를 허용하고, semantic/parser
  failure retry와 same-source resubmission은 금지한다. P0 pass도 별도 method-free
  P1 등록만 허용한다.
- 직전 cycle-functional/open-CTA/goal-oriented/4D-flow failure와 no-repair
  판정은 그대로 보존한다. `junjinyong`은 접속·실행·조회·모니터링에서 계속
  제외한다.
- 영향 파일: `docs/aneux-preprocessing-orbit-audit-2026-08-09.md`,
  `configs/aneux_preprocessing_orbit_p0.json`,
  `src/aurora/aneux_preprocessing_orbit_p0.py`,
  `scripts/audit_aneux_preprocessing_orbit_p0.py`,
  `cluster/pbs_aneux_preprocessing_orbit_p0.pbs`,
  `tests/test_aneux_preprocessing_orbit_p0.py`, `.github/workflows/quality.yml`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`, `AGENTS.md`, `README.md`,
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`, `docs/data-acquisition.md`,
  `docs/server-execution.md`, `site/index.html`,
  `site/learn.html`, `site/assets/aurora.js`, `site/assets/research-data.js`,
  `CHANGELOG.md`.

## 2026-08-09 · Cycle-functional P0 is execution-incomplete and the candidate closes

- Exact public source `754ed746fb60aef707f639189ad59e84a0fca556`의
  `introai9` CPU/PBS job `115168.ECE-util1`을 8 CPU/128 GB/GPU 0으로 정확히
  한 번 실행했다. PBS는 walltime `00:05:16`, CPU time `00:00:01`, peak memory
  `33132kb`, exit 28을 기록했다.
- 두 pinned processed payload, partial file과 aggregate result는 모두 생성되지
  않았다. Raw scheduler stdout도 materialize되지 않아 exit 28이 transport
  timeout과 양립한다는 범위를 넘어 exact failing shell command를 단정하지
  않는다.
- Physical-WSS recovery, archive schema/linkage, 80-frame geometry/topology와
  unique-unit 16-check scientific gate는 전부 미평가다. 이는 AneuG-Flow 자산이나
  cycle-functional 가설의 scientific failure가 아니다.
- 등록 계약에 따라 dependency/reader/transport repair, same-contract rerun,
  P1, method, architecture, GPU와 outer test를 열지 않고 candidate version을
  닫았다. Active shortlist는 0으로 돌아갔고 다음 허용 작업은 fresh
  problem-level primary-source/asset audit뿐이다.
- 공개 execution record는
  `results/aneug_cycle_functional_p0_execution_20260809.json`, SHA-256은
  `cf2eab0a118688698183004928d7fc1786f694c1435fe7f4316502817e6290ae`다.
- 영향 파일: `results/aneug_cycle_functional_p0_execution_20260809.json`,
  `AGENTS.md`, `README.md`, `docs/cycle-functional-wss-audit-2026-08-09.md`,
  `docs/research-direction.md`, `docs/model-spec.md`, `docs/experiment-protocol.md`,
  `docs/isbi-2027-plan.md`, `docs/literature-lineage.md`, `docs/datasets.md`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/index.html`, `site/learn.html`, `site/assets/aurora.js`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Closed P0 state is deployed

- Exact content commit `7c6bf9e8c4354f4f3557551a1d7f795265ce069d`의 Quality
  run `31294677050`과 Pages run `31294676782`가 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 active shortlist
  0, cycle-functional P0 execution-incomplete/no scientific verdict, P1/model/GPU
  금지와 fresh problem audit-only 경계를 확인했다.
- 공개 [execution record](https://gohyunsu.github.io/aneurysm/results/aneug_cycle_functional_p0_execution_20260809.json)도
  HTTP 200으로 확인했다. 이 배포 확인은 scientific gate를 평가하거나 후보를
  재개방하지 않는다.
- 영향 파일: `AGENTS.md`, `site/index.html`, `site/assets/research-data.js`,
  `CHANGELOG.md`.

## 2026-08-09 · Cycle-functional WSS enters a P0-only conditional shortlist

- 같은 transient WSS field와 TAWSS/OSI/RRT가 공유하는 cycle moments를 하나의
  representation에서 만족시키는 문제를 fresh batch의 유일한 33.0/40 후보로
  남겼다. Active primary, method, architecture, GPU, outer test와 contribution은
  여전히 0이다.
- AneuG-Flow dataset commit `9dd4180…`, official code `4a090a0…`, steady
  9,632,510,050-byte SHA-256 `0c03c1d9…0177f`, transient 23,744,862,051-byte
  SHA-256 `141541ed…51c9`를 payload access 전에 pin했다. Dataset/NeurIPS의
  730 case와 RHSIA의 808 case를 같은 version으로 가정하지 않는다.
- Official preprocessing은 transient tensor를 steady `tensor_norm`으로
  정규화하지만 transient assembled object에는 norm을 저장하지 않는다. 따라서
  두 파일을 한 physical-WSS recovery pair로 검사한다.
- `configs/aneug_cycle_functional_p0.json`은 `introai9` PBS CPU-only one-shot,
  weights-only/mmap reader, exact hash/schema/linkage/static-topology/normalization
  checks를 고정한다. Pass도 method-free P1 perturbation audit만 열고,
  fail/execution-incomplete는 dependency·reader repair나 same-contract rerun 없이
  candidate version을 닫는다.
- RHSIA의 Graph Transformer/GHD/steady augmentation, generic functional loss/head,
  temporal basis와 DOPE류 functional debiasing을 direct/non-novel boundary로
  명시했다. Raw OSI relative error만으로 task gap을 확정하지 않는다.
- 영향 파일: `docs/cycle-functional-wss-audit-2026-08-09.md`,
  `configs/aneug_cycle_functional_p0.json`, `src/aurora/aneug_cycle_functional_p0.py`,
  `scripts/audit_aneug_cycle_functional_p0.py`,
  `scripts/run_aneug_cycle_functional_p0_pbs.sh`,
  `tests/test_aneug_cycle_functional_p0.py`,
  `AGENTS.md`, `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`, `docs/literature-lineage.md`,
  `docs/datasets.md`, `configs/aurora_v1.json`, `src/aurora/protocol.py`,
  `tests/test_protocol.py`, `site/index.html`, `site/learn.html`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Inverse audit and introai9 policy are deployed

- Exact content commit `15bbccbfb367516ee0daaf8d2f5beca20b7c587b`의 Quality
  run `31291453002`와 Pages run `31291452634`가 모두 성공했다.
- [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 inverse
  counterfactual 후보 27/40 source rejection, active shortlist/primary/model/GPU
  0과 `introai9`-only future compute를 확인했다. 상세 가이드에서도
  `junjinyong` 제외, 현재 GPU job 0과 gate 뒤 scheduler smoke 경계가 보인다.
- 이 배포 확인은 후보 점수, dataset access, method/GPU authorization 또는
  scientific verdict를 바꾸지 않는다.
- 영향 파일: `AGENTS.md`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · AURORA compute moves exclusively to introai9

- `junjinyong`은 다른 연구가 사용 중이므로 AURORA에서 접속, job 제출,
  상태 조회와 모니터링을 모두 금지한다. 과거 run과 frozen PBS/config는
  provenance로만 보존하며 재제출하지 않는다.
- `introai9`를 source audit, CPU/PBS와 향후 gate-authorized GPU 실험의 유일한
  대상으로 정했다. SSH/PBS 접근과 `coss_agpu`·`coss_a6gpu` ACL compatibility는
  읽기 전용으로 확인했다.
- 현재 AURORA GPU job은 0개다. Active candidate가 없으므로 GPU allocation,
  training과 monitoring을 시작하지 않았다. 새 후보가 prospective gate를
  통과하면 첫 scheduler allocation에서 GPU model, runtime과 CUDA smoke를 다시
  기록한다.
- Public config schema 3.3은 이 server boundary를 validator invariant로 고정한다.
  내부 endpoint, credential과 절대 경로는 공개 저장소에 기록하지 않는다.
- 영향 파일: `AGENTS.md`, `README.md`, `docs/server-execution.md`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/index.html`, `site/learn.html`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Inverse healthy-vessel counterfactual candidate is rejected at source audit

- 검토한 문제는 aneurysm-bearing surface \(Y\)에서 healthy parent vessel
  \(H\)와 localized lesion edit \(Z\)의 posterior를 추론하고 fixed editor로
  \(E(H,Z)\approx Y\) cycle을 검사하는 구조였다.
- Current Aneumo repository와 pinned cache는 base-family deformation mapping과
  nonzero aneurysm morphometry를 제공하지만 released healthy counterpart,
  ostium/lesion label 또는 edit-parameter pair manifest를 제공하지 않는다.
  초기 10,000-model preprint의 466 aneurysm-free count를 현재 10,660-geometry
  release의 paired supervision으로 소급하지 않는다.
- IntrA는 103 whole-vessel model, 1,909 local segment와 116 expert-annotated
  aneurysm segment를 제공하지만 동일 환자의 real healthy counterfactual,
  complete whole/local mapping과 명시적 repository license가 없다. Payload는
  받거나 읽지 않았다.
- SynVA/AneuG forward editing, supervised aneurysm surface isolation, medical
  healthy-counterfactual anomaly localization과 point-cloud reconstruction을
  direct prior로 올렸다. 남는 inverse-editor posterior는 현재 자산에서 real
  counterfactual correctness로 검증할 수 없다.
- Cold-audit score는 **27.0/40**으로 자동 shortlist 기준 32에 못 미친다.
  Executable P0, method name, architecture, config, seed, threshold, checkpoint와
  GPU job을 만들지 않고 active shortlist를 0으로 유지한다.
- 영향 파일: `docs/inverse-aneurysm-editing-audit-2026-08-09.md`, `AGENTS.md`,
  `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/datasets.md`, `docs/literature-lineage.md`,
  `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`, `site/index.html`,
  `site/learn.html`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Open-CTA P0 is execution-incomplete and the candidate closes

- Prospective source `b437875f884346d7f0fada68f089981664ae2a3c`는 Quality
  run `31288906410`과 Pages run `31288906069`이 모두 성공했고 live site 배포를
  확인한 뒤 clean worktree에서 정확히 한 번 실행했다. Frozen config SHA-256은
  `278b95c1e77c0918eb894fd5431cb8d1d8859d693184026827987ef659c3a551`다.
- 실행은 22.53초 뒤 selected DICOM header의 `(0008,1032) Procedure Code
  Sequence`가 undefined-length로 나타난 지점에서 minimal parser의
  `OpenCTAP0Error`, exit 1로 종료됐다. Threaded early exit 때문에 완료 header
  수를 추측하지 않는다.
- ZIP64 index, metadata와 일부 DICOM compressed prefix/header semantics에는
  접근했지만 PixelData value는 decode·inspect하지 않았고 STL 단계에는
  도달하지 않았다. Raw payload, identifier, model, checkpoint와 GPU는 보존하거나
  공개하지 않았다.
- Scientific 12-check gate는 미평가이고 P0 result JSON은 생성되지 않았다.
  이를 scientific P0 fail, asset inadequacy 또는 grid-commutation 가설 반증으로
  표현하지 않는다.
- 등록 계약대로 parser repair, same-contract rerun, P0r과 P1을 만들지 않는다.
  후보는 `execution-incomplete/no scientific verdict`로 닫고 active shortlist는
  0으로 돌아간다. 다음은 독립된 fresh problem-level audit뿐이다.
- Public execution record SHA-256은
  `538725c9901039169cc6e747a112630f327411c5594d021edf9b76fd913f950b`다.
- Outcome content commit `9181862bdf62a81d16b1b20976e8632fb50e2b53`의
  Quality run `31289833490`과 Pages run `31289833028`이 모두 성공했다.
  [공개 사이트](https://gohyunsu.github.io/aneurysm/site/)에서 active shortlist
  0, execution-incomplete/no-verdict와 fresh-problem-audit 경계를 확인했다.
- 영향 파일: `results/open_cta_physical_p0_execution_20260809.json`,
  `results/README.md`, `.github/workflows/quality.yml`, `configs/aurora_v1.json`, `src/aurora/protocol.py`,
  `tests/test_protocol.py`, `AGENTS.md`, `README.md`,
  `docs/open-cta-physical-grid-audit-2026-08-09.md`,
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`, `docs/data-acquisition.md`,
  `docs/server-execution.md`, `site/index.html`, `site/learn.html`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Open-CTA physical-coordinate candidate enters a P0-only shortlist

- Fresh direct-prior red team은 spacing-aware resampling, implicit continuous
  segmentation, resolution-invariant latent, random-finite-set detection,
  variable-cardinality LesionDETR와 aneurysm shape/topology learning을 모두
  선행 범위로 올렸다. 잔여 가설은 하나의 physical-coordinate lesion-instance
  representation에서 cardinality·surface·morphometry가 grid 변화에 함께
  commute하고 small/multiple lesion에서 실제 이득을 보이는 경우로 한정했다.
- Source-only score는 **32.0/40**으로 automatic shortlist 기준과 정확히 같다.
  이는 conditional shortlist 1일 뿐 primary problem, method, architecture,
  contribution 또는 submission identity의 선택이 아니다.
- DICOM header와 STL payload를 읽기 전에
  `configs/open_cta_physical_p0.json`을 고정했다. 172 case의 first/upper-median/last
  DICOM header 516개는 PixelData tag 전에만 읽고, 122 STL은 CRC·geometry·
  metadata-volume scale·DICOM frame alignment를 aggregate-only로 검사한다.
  PixelData decode, raw retention, case identifier publication, model, GPU와
  outer test는 금지한다.
- 모든 check가 통과하면 별도 method-free P1 rasterization/instance-stability
  audit만 등록한다. 하나라도 실패하면 threshold·tolerance·selection·parser를
  결과에 맞춰 수리하지 않고 후보를 닫는다. P0 실행은 clean public registration
  commit 이후 정확히 한 번만 허용한다.
- 영향 파일: `configs/open_cta_physical_p0.json`, `src/aurora/open_cta_physical_p0.py`,
  `scripts/audit_open_cta_physical_p0.py`, `tests/test_open_cta_physical_p0.py`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `.github/workflows/quality.yml`, `docs/open-cta-physical-grid-audit-2026-08-09.md`,
  `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`, `docs/data-acquisition.md`,
  `docs/server-execution.md`, `AGENTS.md`, `site/index.html`, `site/learn.html`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · TopAneu source audit deployment is verified

- Exact source `58fd5f97ed9b68c19dfabc7bb95db53f59343b94`의 GitHub
  Quality run `31286527562`와 Pages run `31286527078`은 모두 `success`다.
- <https://gohyunsu.github.io/aneurysm/site/>에서 TopAneu attachment lead
  29/40, active problem shortlist 0과 terms/payload/model/GPU 0 경계를 확인했다.
  Site change history에도 below-admission decision이 렌더링된다.
- 공개 result URL에서
  `open_multicenter_cta_metadata_discovery_20260809`와
  `dicom_header_or_pixel_read=false`를 확인했다. Individual row, DICOM/STL
  payload와 private path는 노출되지 않는다.
- 이 deployment record는 source audit 점수, 약관 상태, active shortlist,
  method/GPU authorization 또는 artifact를 바꾸지 않는다.
- 영향 파일: `CHANGELOG.md`, `site/assets/research-data.js`.

## 2026-08-09 · TopAneu attachment remains a below-threshold conditional lead

- TopAneu official challenge, live data page와 registered design을 대조해 live
  train 417 scan/409 unique patient, 52-class location, lesion/type mask와
  organizer-predicted silver vessel mask를 확인했다. Registered design의 계획
  규모를 live sample size로 사용하지 않는다.
- Vessel-aware deformable attention은 soft vessel distance를, ICCVW multitask
  U-Net은 vesselness prior를, ARAN은 patient-specific centerline GAT와
  artery-aware cross-attention을 이미 사용한다. Joint lesion/vessel prediction,
  parent-artery classification, universal taxonomy와 hierarchy loss도 direct
  prior이므로 단독 novelty에서 제외했다.
- Mask와 location을 하나의 patient-specific vascular attachment에서 유도하는
  가설은 **29.0/40**, 자동 채택 기준 32 아래의 conditional lead다. Bifurcation
  ambiguity reference와 payload semantics가 확인되지 않아 active problem,
  method, architecture, GPU, outer test와 paper identity는 모두 0이다.
- TopAneu verified account와 terms를 사용자가 수락했다고 확인되지 않았다.
  에이전트는 가입·동의·download하지 않았고 TopAneu image/mask/JSON payload는
  읽지 않았다. 명시적 사용자 수락 뒤에도 먼저 prospective CPU/read-only P0-T
  asset/semantics audit만 등록할 수 있다.
- Zenodo `15697196`의 공개 25,578,845,008-byte CTA archive는 전체 download
  없이 ZIP64 central directory와 16,458-byte `Metadata.csv`만 range-read했다.
  149,329 DICOM/122 STL, 172 case/122 lesion/24 multi-lesion case를 확인했지만
  DICOM header/pixel과 STL payload는 읽지 않았다. 공개 aggregate는
  `results/open_multicenter_cta_metadata_discovery_20260809.json`, SHA-256은
  `8ed7fa00f10bc81e3db5cfed1b26fa8f5c910ab7edc78b1384f3c8e6bcabb3ed`다.
- 중앙 schema는 `3.0`으로 올리고 conditional lead를 shortlist나 training으로
  승격하거나 open CTA metadata를 TopAneu supervision으로 부르는 변경을
  validator와 unit test가 거부하도록 했다. 다른 fresh problem audit은 계속
  허용한다.
- 영향 파일: `docs/topaneu-attachment-audit-2026-08-09.md`,
  `results/open_multicenter_cta_metadata_discovery_20260809.json`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `AGENTS.md`, `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`, `docs/data-acquisition.md`,
  `docs/server-execution.md`, `results/README.md`, `site/index.html`,
  `site/learn.html`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · The 5/9 closure state is deployed and verified

- Exact result-bearing source `07fb98eabfa36ee226bde337cae7f23fef2cbc72`의
  GitHub Quality run `31284456367`과 Pages run `31284456053`은 모두
  `success`다.
- <https://gohyunsu.github.io/aneurysm/site/>에서 `active problem shortlist 0`,
  goal-oriented candidate의 5/9 asset failure와 no solver-v2/S0b/model/GPU
  boundary를 확인했다. Public result URL에서도 `failed_5_of_9` verdict를
  확인했다.
- 이 deployment record는 실행 전 source `ef547a4…`, public result, threshold,
  candidate closure 또는 next authorization을 바꾸지 않는다.
- 영향 파일: `CHANGELOG.md`, `site/assets/research-data.js`.

## 2026-08-09 · Goal-oriented candidate closes after S0a asset component fails 5/9

- Exact prospective source `ef547a4ccb71fa45b4a43e67c0939e2701ebfc11`의
  CPU/PBS job `115119.ECE-util1`은 exit 0으로 완료됐지만 frozen asset
  component는 **5/9 failed**다.
- 통과한 항목은 official archive size/MD5 3/3, five CSV member set, six
  multi-lesion patient group, aggregate privacy와 no-model/GPU/outer-test boundary다.
  Frozen patient/lesion/control count, 105-lesion exact CTA/STL/table linkage,
  non-positional linkage와 linkage-dependent unit/frame check는 실패했다.
- 관찰 단위는 105 patient records, 99 unique patients, 105 morphology lesion
  IDs, 98 unique hemodynamic IDs와 99 patient-level case directories였다.
  Required CTA+parent/aneurysm STL+aneurysm STL triplet은 0/105다.
- NIfTI/STL header, voxel과 field는 열지 않았다. 따라서 unit/frame 항목은
  geometry 자체가 implausible하다는 결과가 아니라 exact-linkage 전제조건
  실패로 미도달한 check다.
- S0a 전체는 `not_evaluated`로 보존한다. Frozen early-stop대로 goal-oriented
  candidate를 닫고 solver preflight v2, S0b, model, GPU와 outer test를 열지
  않는다. 같은 source의 case-mapping repair나 rerun도 금지한다.
- Public privacy-safe result는
  `results/goal_oriented_s0a_asset_component_20260809.json`, SHA-256은
  `c220cb8d92909a5a401b29ad5b75d54f4881d9db4a32ea6f33dd6007e424ad6e`다.
  중앙 schema는 `2.9`, active problem shortlist는 0이다. 다음 허용 작업은
  닫힌 후보를 수리하지 않는 fresh problem-level primary-source and asset
  audit다.
- 영향 파일: `results/goal_oriented_s0a_asset_component_20260809.json`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`,
  `tests/test_protocol.py`, `tests/test_goal_oriented_s0a_asset.py`, `AGENTS.md`,
  `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/goal-oriented-segmentation-audit-2026-08-09.md`,
  `docs/server-execution.md`, `docs/datasets.md`, `docs/literature-lineage.md`,
  `results/README.md`, `site/index.html`, `site/learn.html`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Source-server S0a asset gate is deployed and verified

- Exact prospective source `ef547a4ccb71fa45b4a43e67c0939e2701ebfc11`의
  GitHub Quality run `31282466660`과 Pages run `31282466314`가 모두
  `success`다.
- 공개 사이트는 <https://gohyunsu.github.io/aneurysm/>에서 현재
  staging/solver-v1 실패, archive 3/3 discovery, one-shot asset early-stop과
  method/GPU/outer-test 금지를 렌더링한다.
- 이 기록은 prospective source의 code/config를 바꾸지 않는다. 실제 asset
  audit은 위 exact source를 clean checkout으로 사용한다.
- 영향 파일: `CHANGELOG.md`, `site/assets/research-data.js`.

## 2026-08-09 · Preserve two pre-gate failures and freeze source-server asset early stop

- Exact `5cd4aa2…`의 chunked CMHA staging v2는 79초 뒤 exit 28이었다.
  First verified chunk, archive/extraction, identifier mapping과 retained payload는
  모두 0이고 S0a는 `not_evaluated`다. Raw stdout이 PBS post-job processing 뒤
  materialize되지 않아 exact network cause를 단정하지 않는다. 같은 v2와 새
  v3 Figshare transport를 실행하지 않는다.
- Exact `64284eb…`의 solver preflight v1은 7,519초 뒤 exit 1이었다. Official
  build SIF SHA `c6afff1d…`, SU2 exact main/COPYING/config와 11/11 submodule
  HEAD는 확인했지만 TestCases checkout, solver install, runtime SIF,
  forward/adjoint probe와 sensitivity는 없다. Raw stdout 부재로 exact shell
  cause는 unresolved이며 S0a가 아니다. 같은 v1을 재실행하지 않는다.
- 규약대로 `introai9`의 기존 source asset을 읽기 전용으로 찾아 세 official
  CMHA archive 총 15,557,345,067 byte와 MD5가 3/3 일치함을 확인했다. 이
  low-priority login-node discovery는 CSV row, identifier, NIfTI/STL header,
  voxel과 field를 열지 않았고 S0a check pass로 세지 않는다. 추가 다운로드나
  raw cross-server transfer를 중단한다.
- `configs/goal_oriented_segmentation_s0a_asset_component.json`은 위 discovery
  뒤 medical header access 전에 고정한 one-shot CPU/PBS early-stop overlay다.
  Pure-standard-library runner가 exact archive/CSV, 99/105/44/6 unit,
  non-positional exact-ID sets, 105 CTA/STL triplet, qform/sform·mm scale·fixed
  LPS→RAS containment와 privacy/no-model boundary를 9/9로 검사한다.
- Scientific fail이면 현재 후보를 닫고 solver v2를 만들지 않는다. 9/9도 S0a
  pass가 아니라 한 번의 no-runtime-network solver-preflight-v2 등록만
  허용한다. Method, architecture, GPU, outer test와 paper identity는 계속
  닫혀 있다. 중앙 schema를 `2.8`로 올렸다.
- 영향 파일: `results/goal_oriented_s0a_cmha_stage_v2_execution_20260809.json`,
  `results/goal_oriented_s0a_solver_preflight_v1_execution_20260809.json`,
  `results/goal_oriented_s0a_cmha_source_asset_discovery_20260809.json`,
  `configs/goal_oriented_segmentation_s0a_asset_component.json`,
  `src/aurora/goal_oriented_s0a_asset.py`,
  `cluster/pbs_goal_oriented_s0a_asset_component.pbs`,
  `tests/test_goal_oriented_s0a_asset.py`, `AGENTS.md`, `README.md`,
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/goal-oriented-segmentation-audit-2026-08-09.md`,
  `docs/server-execution.md`, `results/README.md`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `.github/workflows/quality.yml`, `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Direct-prior red team narrows the conditional gap again

- [JFM 2022 inverse Navier--Stokes study](https://doi.org/10.1017/jfm.2022.503)는
  noisy velocity image의 flow reconstruction과 boundary segmentation을 shape
  gradient로 공동 추정한다. 따라서 PDE/adjoint shape gradient를 segmentation에
  연결하는 일반 발상은 novelty가 아니다.
- [2024 quantitative-PET task-based evaluation](https://pubmed.ncbi.nlm.nih.gov/38360049/)
  은 Dice/Jaccard/Hausdorff와 downstream metabolic quantity를 함께 비교한다.
  따라서 standard geometry metric과 downstream endpoint가 다를 수 있다는
  관찰이나 task-based 평가만으로도 contribution을 주장하지 않는다.
- 잔여 가설은 CTA predictor의 **multi-functional signed adjoint pullback +
  remainder-controlled trust region + held-out functional superiority**가 함께
  성립하는 경우로 좁혔다. Direct-prior residual 점수를 3.0→2.5, 전체 cold
  score를 27.5→27.0/40으로 낮췄다. 자동 선택 기준 32/40은 유지한다.
- 이 red team은 S0a의 asset/runtime contract, 실행 source, threshold 또는
  권한을 바꾸지 않는다. Method, architecture, GPU, outer test와 paper identity는
  계속 닫혀 있다. 중앙 schema를 `2.7`로 갱신했다.
- Exact public source `d8fbabd72b50039d899229484265968df25b3508`의
  GitHub quality run `31279925201`과 Pages run `31279924772`는 모두
  success다. <https://gohyunsu.github.io/aneurysm/site/>의 live asset에서
  27.0/40 score와 inverse Navier--Stokes direct-prior 경계를 확인했다.
- 영향 파일: `docs/literature-lineage.md`,
  `docs/goal-oriented-segmentation-audit-2026-08-09.md`, `AGENTS.md`,
  `docs/isbi-2027-plan.md`, `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Preserve CMHA staging v1 transport failure and freeze one-change v2

- Exact public source `b6b6175…`의 CPU-only PBS job `115107`은 20분 37초 뒤
  exit 28이었다. Archive manifest는 0 byte이고 final/partial archive,
  extraction, success status와 raw scheduler stdout은 없다. Verified archive와
  retained payload는 0 byte이며 S0a는 `not_evaluated`다.
- Exit 28을 Figshare unavailable로 단정하지 않았다. Bounded diagnostic에서
  HEAD는 redirect 뒤 403이었지만 1 KiB와 8 MiB GET은 HTTP 206이었고,
  8 MiB는 4.999초·1,678,057 B/s였다. Exact v1 cause는 unresolved로 보존한다.
- 같은 v1 source를 재제출하지 않는다. Official file ID/size/MD5, extraction과
  gate boundary는 유지하고 monolithic GET만 64 MiB range chunks+atomic
  assembly로 바꾼 v2를 public source당 한 PBS attempt로 등록했다. V2도
  staging-only이며 model/GPU/outer test와 S0a verdict를 열지 않는다.
- 중앙 schema를 `2.6`으로 갱신했다.
- 영향 파일: `results/goal_oriented_s0a_cmha_stage_v1_execution_20260809.json`,
  `configs/goal_oriented_segmentation_s0a_cmha_stage_v2.json`,
  `src/aurora/goal_oriented_s0a_staging.py`,
  `cluster/pbs_goal_oriented_s0a_stage_cmha_v2.pbs`,
  `tests/test_goal_oriented_s0a.py`, `.github/workflows/quality.yml`, `AGENTS.md`,
  `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`,
  `docs/goal-oriented-segmentation-audit-2026-08-09.md`,
  `docs/server-execution.md`, `results/README.md`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Reject direct-only SU2 runtime and register reverse-AD preflight

- Official SU2 8.5.0 OMP release의 30,226,528-byte asset과 SHA-256을 확인했다.
  NACA0012 QuickStart steady direct는 exit 0으로 수렴했지만 같은 binary의
  `DISCRETE_ADJOINT`는 AD support가 compile되지 않았음을 명시하고 종료했다.
  이 negative control은 S0a 결과가 아니며 direct-only binary는 부적격이다.
- Exact SU2/TestCases v8.5.0 commit, LGPL COPYING hash와 official GHCR
  linux/amd64 build-image manifest를 고정한 CPU/PBS preflight를 등록했다.
  Normal+reverse-AD immutable SIF를 build하고, official incompressible
  heated-cylinder에서 fresh direct solution → discrete adjoint → finite/nonzero
  surface sensitivity를 실제 실행한다.
- Preflight 10/10도 runtime pin과 단 한 번의 S0a 실행만 열며, S0a pass,
  method, architecture, GPU, outer test와 paper identity를 열지 않는다. 실패한
  동일 source version은 고쳐 재실행하지 않는다.
- 중앙 schema를 `2.5`로 올려 direct-only 부적격, preflight 상태와 제한된
  authorization을 검증한다.
- 영향 파일: `configs/goal_oriented_segmentation_s0a_solver_preflight.json`,
  `src/aurora/goal_oriented_s0a_solver.py`,
  `cluster/pbs_goal_oriented_s0a_solver_preflight.pbs`,
  `tests/test_goal_oriented_s0a.py`, `.github/workflows/quality.yml`, `AGENTS.md`,
  `README.md`, `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`,
  `docs/goal-oriented-segmentation-audit-2026-08-09.md`,
  `docs/server-execution.md`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Register CMHA staging without evaluating S0a

- `introai9` 승인 root와 `junjinyong` home을 읽기 전용으로 확인했지만 CMHA
  archive/table은 staged되어 있지 않았다. 이를 자산 부재나 S0a failure로
  해석하지 않는다.
- Official Figshare file ID, size와 MD5를 고정한 CPU/PBS staging wrapper를
  추가했다. Download는 partial file을 보존해 resume하고 checksum 통과 후에만
  extraction한다. GPU, model, identifier mapping, solver probe와 gate outcome은
  모두 접근하지 않는다. 실행 전 exact clean public checkout도 강제한다.
- 영향 파일: `cluster/pbs_goal_oriented_s0a_stage_cmha.pbs`,
  `tests/test_goal_oriented_s0a.py`, `docs/server-execution.md`,
  `site/assets/research-data.js`, `CHANGELOG.md`.

## 2026-08-09 · Goal-oriented segmentation survives only as an S0a-conditional problem

- CMHA, OpenNeuro `ds005096`, 공개 multi-center CTA 2026의 실제 supervision과
  독립 단위를 공식 논문·dataset record로 다시 감사했다. CMHA는 99 patients/
  105 MCA aneurysms와 44 controls의 NIfTI CTA, aneurysm–artery STL,
  aneurysm STL을 제공하지만 6 multi-lesion patient와 exact image–surface–
  table linkage를 먼저 처리해야 한다.
- Image2Flow의 joint image→mesh+CFD field loss, IAVS의 topology-aware
  segmentation/CFD Applicability Score, clDice/cbDice, MATCH/CFD challenge의
  segmentation variability와 differentiable PDE/shape optimization을 direct
  prior로 올렸다. Automatic segmentation→CFD, solver success, GNN/U-Net,
  adjoint와 sensitivity weighting 자체는 novelty가 아니다. Nearly automated
  anterior-vasculature pipeline은 공식 Scientific Reports DOI
  `10.1038/s41598-024-80891-4`로 교정했다.
- 유일하게 남을 수 있는 gap을 predefined PDE functional의 adjoint shape
  gradient에 signed boundary displacement를 투영하는 segmentation supervision으로
  제한했다. Cold-audit score는 27.5/40로 자동 선택 기준 32에 못 미치므로
  method나 paper identity가 아니라 **conditional problem shortlist**다.
- `configs/goal_oriented_segmentation_s0a.json`은 official archive size/MD5/
  license, 99/105/44/6 unit, 105 exact-ID linkage, NIfTI/STL unit·frame와 별도
  pinned steady-solver/adjoint runtime을 11개 all-or-none check로 고정한다.
  S0a pass도 method-free S0b만 열고 같은 version의 dependency/mapping repair
  rerun, GPU, outer test와 submission claim을 금지한다.
- `junjinyong`에서 PBS와 기존 pinned PyTorch image 접근은 확인했지만 host와
  container 모두 mesh/PDE stack을 제공하지 않았다. Login-node GPU는 사용하지
  않았고 기존 held job을 변경하지 않았다. 별도 solver image의 exact digest와
  license를 S0a에서 검증해야 한다.
- 중앙 schema를 `2.4`로 갱신하고 research direction, model boundary,
  protocol, ISBI plan, dataset/lineage, site와 운영 규약을 동기화했다.
- Prospective source `24e0444dc1a7d5fcff924c70f3b8319d134b5bd3`에서
  GitHub quality workflow와 Pages deployment가 모두 성공했다. 공개본은
  <https://gohyunsu.github.io/aneurysm/site/>에서 확인했다.
- 영향 파일: `docs/goal-oriented-segmentation-audit-2026-08-09.md`,
  `configs/goal_oriented_segmentation_s0a.json`,
  `src/aurora/goal_oriented_s0a.py`, `tests/test_goal_oriented_s0a.py`,
  `AGENTS.md`, `README.md`, `docs/research-direction.md`,
  `docs/model-spec.md`, `docs/experiment-protocol.md`,
  `docs/isbi-2027-plan.md`, `docs/literature-lineage.md`, `docs/datasets.md`,
  `docs/server-execution.md`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`, `site/index.html`,
  `site/learn.html`, `site/assets/research-data.js`,
  `docs/problem-candidate-audit-2026-08-09.md`,
  `.github/workflows/quality.yml`, `CHANGELOG.md`.

## 2026-08-09 · RSNA supervision semantics reject the only shortlist

- Official registry/wiki, 1위 공개 구현 exact commit
  `e1dcdf0058e1e0d0044d8053e92243b4b4794555`, 2위 report
  `arXiv:2606.26706v1`을 red-team했다. Image·annotation payload와
  controlled-access 약관 수락은 0이다.
- 제공 `segmentations/{uid}_cowseg.nii`는 aneurysm extent가 아니라
  background+13-class Circle-of-Willis vessel anatomy다. 2위 report는 4,348
  training series 중 178건에 이 vessel mask가 있고, aneurysm center point는
  annotated series 전체에 있으며 official voxel aneurysm mask는 없다고
  설명한다. 저자들의 voxel aneurysm target은 point box, pseudo-label과
  manual correction으로 파생한 것이다.
- 따라서 presence·territory·point·“일부 official lesion mask”를 한 latent
  lesion set의 annotation projection으로 놓고 mask-selection mechanism을
  학습한다는 전제가 거짓이다. 후보를 access-blocked로 유지하지 않고
  **rejected**로 보존한다. CADA·ADAM·IntrA·TopCoW screen도 이를 구제하지
  않는다.
- Central schema를 `2.3`으로 올리고 active shortlist, estimand, method,
  GPU, outer test와 submission identity를 모두 미선정/비허용으로 고정했다.
  다음 허용 작업은 fresh problem-level candidate audit다.
- 영향 파일: `AGENTS.md`, `README.md`,
  `docs/rsna-supervision-semantics-audit-2026-08-09.md`,
  `docs/problem-candidate-audit-2026-08-09.md`,
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/datasets.md`, `docs/literature-lineage.md`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`,
  `tests/test_protocol.py`, `site/index.html`, `site/learn.html`,
  `site/assets/aurora.js`, `site/assets/research-data.js`,
  `CHANGELOG.md`.
- Production source
  `bf3deeb44c9c492e51733e1f4f30a407166e8e1e`의 GitHub quality run
  `31270301588`과 Pages run `31270301232`은 모두 success다. 2026-08-09
  KST에 <https://gohyunsu.github.io/aneurysm/site/>와
  <https://gohyunsu.github.io/aneurysm/site/learn.html>이 active shortlist 0,
  vessel-anatomy/lesion-extent 구분, candidate rejected와 fresh problem audit
  경계를 실제 제공함을 확인했다.

## 2026-08-09 · public alternatives do not replace the selection-aware task

- CADA, ADAM, IntrA와 TopCoW의 공식 challenge/dataset record만 사용해
  source-only dataset substitution screen을 수행했다. Image·annotation payload,
  registered download와 약관 동의는 모두 0이다.
- CADA와 ADAM은 point/mask가 함께 있는 fully supervised 3DRA/MRA challenge라
  non-random annotation-selection cohort가 아니다. IntrA는 whole-study raw
  angiography가 없는 local surface segment이고 TopCoW는 aneurysm이 아닌
  Circle-of-Willis anatomy label이다.
- 네 자료는 향후 external fully supervised control 또는 anatomy pretraining
  역할만 가능하다. 어느 것도 RSNA-ICA의 study-level selection-aware lesion-set
  task, executable config, method/GPU 또는 outer test를 열지 않는다. RSNA
  access가 불가능하면 일반 segmentation으로 축소하지 않고 shortlist를
  폐기한다.
- Central schema를 `2.2`로 올려 `primary_problem`, application endpoint,
  primary metric과 ISBI headline domain을 `unselected`로 고정했다. 닫힌
  4D-flow I0a/I0b와 실패한 irregular-3D evidence는 exact history로 유지하되
  validator가 active task처럼 강제하던 모순을 제거했다.
- 영향 파일: `AGENTS.md`, `README.md`, `docs/research-direction.md`,
  `docs/model-spec.md`, `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/datasets.md`, `docs/literature-lineage.md`,
  `docs/problem-candidate-audit-2026-08-09.md`,
  `configs/aurora_v1.json`, `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/index.html`, `site/learn.html`, `site/assets/research-data.js`,
  `CHANGELOG.md`.
- Production source `773a0d6a2139ea02c94f972e8553809761948e20`의 GitHub
  quality run `31268591665`와 Pages run `31268591180`은 모두 success다.
  2026-08-09 KST에 <https://gohyunsu.github.io/aneurysm/site/>가
  `현재 모델은 없다`, RSNA access/L0 차단, public alternatives가
  selection-aware task를 대체하지 않는다는 판정을 실제 제공함을
  확인했다.

## 2026-08-09 · direct mixed-supervision prior art narrows the shortlist

- 추가 direct search에서 heterogeneous weak annotations의 latent structured
  output은 NeurIPS 2010, mixed-supervised detection은 NeurIPS 2021,
  classification+lesion-segmentation mixed supervision은 CVPR 2019,
  partial/unlabeled uniform learning은 ICML 2024에 이미 존재함을 확인했다.
- 따라서 annotation projection/marginalization 자체를 novelty에서 제외했다.
  Shortlist는 어떤 study에 dense/sparse annotation이 선택됐는지의 mechanism이
  비무작위일 때 식별 조건 또는 sensitivity bound가 필요한지 묻는
  `annotation-selection-aware lesion-set` 문제로 더 좁혔다.
- 실제 selection process는 asset access 전에는 알 수 없다.
  `coarsening-at-random`은 가정하지 않고, L0에서 assignment rule, propensity,
  positivity와 unobserved-lesion dependence를 감사한다. 식별되지 않으면
  point claim을 버리고 sensitivity range 또는 후보 폐기를 택한다.
- 영향 파일: `AGENTS.md`, `README.md`, `docs/research-direction.md`,
  `docs/model-spec.md`, `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`,
  `docs/problem-candidate-audit-2026-08-09.md`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/index.html`, `site/learn.html`, `site/assets/research-data.js`,
  `CHANGELOG.md`.
- Production source `ba79491c3401ee462918368abd7742f405b875f4`의
  GitHub quality run `31267438441`과 Pages run `31267438083`은 모두
  success다. 2026-08-09 KST에 live site가 selection-aware shortlist,
  `no CAR assumption`과 L0 차단 상태를 실제 제공함을 확인했다.

## 2026-08-09 · one access-blocked lesion-set problem enters the shortlist

- 4D-flow branch 종료 뒤 방법 이름 없이 새 problem-level cold audit을
  수행했다. Generic segmentation/UQ, longitudinal growth와 geometry×BC shape
  response는 각각 직접 prior art 또는 annotation/data-unit 부족으로 기각했다.
- 유일한 조건부 후보는 RSNA-ICA 2025의 study/location/localizer/segmentation을
  하나의 anatomy-structured latent lesion set의 annotation projection으로
  다루는 문제다. Vessel graph, GNN, set prediction, mixed supervision,
  anatomy/foundation prompt와 conformal/FDR는 단독 novelty에서 제외했다.
- 현재 알려진 `introai9` 경로에 archive가 없고 Kaggle credential도 없어
  access prerequisite가 충족되지 않았다. 사용자 약관 수락 전에는 download,
  executable protocol, method/GPU training과 outer test를 열지 않는다.
- Access 뒤 허용되는 첫 단계는 patient/study/lesion mapping, annotation
  provenance와 split viability의 CPU/read-only L0 audit이다. 자세한 cold audit과
  baseline/metric/kill sequence는
  `docs/problem-candidate-audit-2026-08-09.md`에 기록했다.
- 영향 파일: `AGENTS.md`, `README.md`, `docs/research-direction.md`,
  `docs/model-spec.md`, `docs/experiment-protocol.md`, `docs/isbi-2027-plan.md`,
  `docs/literature-lineage.md`, `docs/datasets.md`,
  `docs/problem-candidate-audit-2026-08-09.md`, `configs/aurora_v1.json`,
  `src/aurora/protocol.py`, `tests/test_protocol.py`,
  `site/assets/research-data.js`, `CHANGELOG.md`.
- Production source `8fb7bb51f7b8097d843a541289c7ac57e6481dce`의
  GitHub quality run `31266919156`과 Pages run `31266918668`은 모두
  success다. 2026-08-09 KST에
  <https://gohyunsu.github.io/aneurysm/site/>가 `One lesion set`, `L0`와
  controlled-access 상태를 실제 제공함을 확인했다.

## 2026-08-09 · I0b stops before asset access and is not rerun

- Exact public source `0ebdb344a6cd4009a928746cda5389b95f12bf8d`, frozen
  config SHA `e19a1194…`의 one-shot PBS job `115093`은 GPU 없이 8 CPU/48 GB로
  5분 7초 실행된 뒤 exit 1이었다. Registered wrapper가 과거 실행에서 쓰던
  read-only `h5py==3.12.1` dependency layer를 bind하지 않았다.
- Failure는 archive index 요청 전 `_scientific_imports()`에서 발생했다.
  2021 archive/RAW/velocity field, 2025 PAR/REC, checkpoint와 GPU access는 0이고
  cache·metric·scientific result도 생성되지 않았다. Gate는 `not_evaluated`이며
  task adequacy를 지지하거나 반박하지 않는다.
- Public execution record는
  `results/flow_mri_protocol_i0b_execution_20260809.json`, SHA-256
  `1b75bb953352966b9c7e2edbb838973d5222c883fe821e4b77ee2302c2ba2130`다.
  Raw log, hostname, cache와 server path는 private output에만 보존한다.
- 등록한 no-rerun rule을 적용해 `h5py`를 보충한 I0b 재실행, I0c, method/GPU
  training과 outer test를 열지 않는다. 4D-flow candidate는 scientific verdict
  없이 닫고 다음은 새 problem-level candidate audit이다.
- Central config/validator/tests including the immutable execution-record guard,
  AGENTS, research/model/experiment/dataset/
  server/ISBI 문서, README, results index와 site를 같은 상태로 동기화했다.
- Production source `1bdf22de76f7a89f09528f1551b4c5717cc40447`의 GitHub
  quality run `31265099170`은 success다. 2026-08-09 KST에
  <https://gohyunsu.github.io/aneurysm/site/>가 새
  `I0b execution-incomplete` 상태를 제공하고 이전 `I0b preregistered`
  문구를 제공하지 않음을 직접 확인했다. 같은 push의 Pages run
  `31265098894`는 success지만 public Actions API의 `head_sha`는 이전
  `0ebdb344…`를 보고하므로 live-content 검증과 분리해 기록한다.

## 2026-08-09 · I0b freezes task adequacy before any field read

- I0a 14/14가 허용한 범위에서
  `configs/flow_mri_protocol_i0b_task_adequacy.json`, SHA-256
  `e19a1194f1b9ec41861c5084b26c9add5be47924a19aee4d23ffc826399dce06`을
  one-shot learned-method-free audit으로 등록했다.
- Registration 전 2021 official README/Matlab reader를 읽어 little-endian
  float32와 X-fastest→Y→Z→T decode를 확인한 사실을 discovery로 공개했다.
  I0b는 68,706,606 compressed bytes의 27 processed RAW만 selective staging해
  common-grid alignment, temporal/vector similarity, resolution/acceleration
  discrepancy와 protocol variance를 frozen all-check rule로 평가한다.
- 검색에서 Zenodo `17183575`의 CC BY 4.0 33-scan intervention release를
  추가로 찾았다. Official record, 세 ZIP64 central directory와 33 primary
  PAR header를 registration 전에 확인했고 velocity/REC field는 읽지 않았다.
  실제 구조는 5 base geometry, 22 physical model/device state, 8 multi-VENC
  state, 2 pump-off acquisition, 15 device condition과 2 source patient
  anatomy다.
- 33 scans, device conditions, phases와 voxels를 independent patients로 세지
  않는다. 기존 Zenodo `14981710`과 case-level overlap도 unresolved이므로
  독립 external cohort로 합치지 않는다.
- I0b pass도 method-free I0c PAR/REC decoder·noise·cross-VENC measurement
  audit 등록만 허용한다. Method/GPU training, posterior calibration claim,
  outer test와 submission은 닫혀 있다. Failure 뒤 registration·mask·threshold
  local repair, rerun 또는 expanded device data로의 자동 relabel은 금지한다.
- Central config/validator/tests, AGENTS, research/model/experiment/literature/
  dataset/server/ISBI 문서, README와 site를 같은 상태로 동기화했다.
- `cluster/pbs_flow_mri_protocol_i0b_cpu.pbs`는 GPU를 요청하지 않는 8 CPU,
  48 GB formal wrapper다. Exact source commit, read-only source, writable fresh
  output과 기존 scientific output 거부를 강제하고 queue·container·private
  server path는 공개 코드에 넣지 않는다.

## 2026-08-08 · I0a passes 14/14 asset checks without field access

- Exact public source `f7b4e024d69d43cf042f4163342b4d993386f441`, frozen
  config SHA
  `ceb6413047b117ecbc7b52d83919b73117491e8de6c099c7b158f592788f40ff`의
  pinned-container CPU audit은 exit 0, 14/14 pass였다.
- 2021 ZIP32와 2025 ZIP64의 central-directory entry 174/76개, CRC-verified
  descriptor/header 9/8개, protocol dimension·spacing·phase·VENC와 27개
  float32 byte contract를 확인했다. Processed RAW/REC read와 field-value
  inspection은 0이며 등록된 M4 filename/header 불일치를 그대로 공개했다.
- 공개 aggregate는
  `results/flow_mri_protocol_i0a_asset_audit_20260808.json`, SHA-256
  `2243172a720b25ebebd6052b9c0989880d95cba5b8d984f8980f70cf5f26d9c6`다.
  Private raw result/status SHA-256은 각각
  `c666644bf72fa10bb550747fbeace923ca0caabbf8142f4f6c7ff5417af00faa`,
  `254c5966474e3304449b94976e0f03392f1b154b716812c40736d722213b74ec`로
  pin했다.
- 이 pass는 selective private staging과 learned-method-free I0b의 별도
  등록만 허용한다. Task adequacy, posterior identifiability, method,
  novelty, performance, outer test와 ISBI submission은 열리지 않는다.
- Research direction, model boundary, experiment protocol, central config,
  validator/tests, dataset/server/ISBI 문서, README와 site를 같은 상태로
  동기화했다. 향후 GPU 실험은 `junjinyong` PBS allocation에서만 실행한다.

## 2026-08-08 · Research identity resets to a cross-protocol 4D-flow candidate

- N1c failure, M0 execution-incomplete state와 V1e 6/9 failure를 보존하고
  current Aneumo 3D line을 local repair 없이 종료한 뒤, selected method가
  없는 상태에서 새 task/data identity를 감사한다.
- 4DFlowNet, SRflow, FlowMRI-Net, VAST, 4D-flow velocity UQ와 2026
  distributional SR를 직접 prior art로 추가했다. Generic SR, denoising,
  physics reconstruction, implicit field, dual-VENC와 voxel uncertainty는
  novelty가 아니다.
- 새 candidate는 한 real acquisition posterior가 같은 controlled phantom
  flow의 다른 resolution·acceleration·VENC acquisition을 measurement space에서
  예측하는지 검사한다. CFD를 MRI truth로 두지 않는다.
- `configs/flow_mri_protocol_i0a_asset_audit.json`에 registration 전 discovery를
  명시하고, 두 official record/archive와 descriptor/header를 field payload
  없이 감사하는 14-check I0a를 고정했다. Pass도 selective private staging과
  learned-method-free I0b 등록만 허용한다.
- Protocol validator, standard-library range audit, parser/guardrail test와
  README, research/model/experiment/literature/dataset/server/ISBI 문서를 같은
  `method unselected · not submission-ready` 상태로 동기화했다.

## 2026-08-08 · M0 execution closes without a scientific verdict

- Exact source `89bdc8560a7e5db1d4b5402cd76dbbb01d991aad`, frozen config SHA
  `78aa6752ed647ffbcb1b90f262873a05156ddda49c6aa21557cc6f7908345f91`의
  PBS array `115078`을 dependency-complete 150/150 contract와 frozen N1b
  checkpoint hash 확인 뒤 실행했다.
- Seed 0/2는 exit 0이었고 seed 1은 `candidate_risk_matrix`에서
  `Truncated conditional rejection stalled.`로 exit 1이었다. Required
  complete seed 3개 중 2개만 완료되어 등록된 aggregate를 만들 수 없다.
- M0를 과학적 pass 또는 fail로 표시하지 않는다. 성공한 두 seed metric은
  gate를 위해 검사·선택 집계하지 않았고 공개 파일에는 metric 값이 없다.
  Execution provenance는
  `results/nonlinear_pde_n1_missing_operator_pullback_m0_execution_20260808.json`,
  SHA-256
  `5376cd4629cc30f1fa16ab1e1762a576866a4d35620cc5e34a9986d5a2bfc593`에
  고정했다.
- One-shot/local-repair 금지 계약에 따라 sampler repair, rerun, M0r,
  fresh re-entry, method selection과 N1d/irregular-3D 권한을 등록하지 않는다.
  N1c failed, current Aneumo 3D line stopped와 not submission-ready를 유지한다.
- 2026 CMPB geometry-aware PointNet을 직접 aneurysm surrogate lineage에
  추가했다. Point cloud, distance-to-wall와 known-law peak-systolic velocity/WSS
  surrogate 자체도 novelty가 아니며 geometry OOD reliability와 missing-BC
  evidence를 별도로 요구한다.
- Protocol validator와 새 execution-record test가 no-verdict, no-aggregate,
  no-cherry-pick, no-repair/re-entry 경계를 강제한다. Research docs, config,
  site 첫 화면·gate·상세 가이드·변경 이력을 같은 상태로 동기화했다.

## 2026-08-08 · V1e fails absolute learnability despite relative boundary utility

- Exact source `c62838b`, config SHA
  `e21414f467b3f6dc0ac6d8a0086ed04cf2873f66f890239c033c77d464e4ae19`의
  boundary Perceiver와 parameter/token-matched geometry-only control을 fresh
  3 seed·6 A6000 task로 실행했다. 모두 exit 0, validation-selected checkpoint
  eligible, CUDA true, test/pressure/missing/clinical access false로 완료됐다.
- 두 variant는 각각 740,099 parameter와 320 source token을 정확히 맞췄다.
  Boundary는 validation full-q와 paired response에서 control보다 3/3 seed로
  좋았고 seed-mean 상대 개선은 `10.94%/6.41%`로 두 relative checks를
  통과했다. 이는 physical boundary asset의 incremental utility다.
- Boundary worst-seed train full-q `0.77221`, validation full-q `0.87796`,
  response `0.94918`은 frozen `0.25/0.35/0.50`을 모두 넘었다. Absolute
  learnability 세 check가 실패해 전체 gate는 **6/9 fail**이다. 상대적으로
  control보다 낫다는 사실로 qualification을 pass라 하지 않는다.
- Public aggregate는
  `results/aneumo_isbi_v1e_known_condition_baseline_20260808.json`, SHA-256
  `63fdb3a6fbddb15bb8d6cb82fde7b6880e3b3c7badef46b7a4cc2da4d31f2c0e`다.
  Raw logs, checkpoint와 histories는 private output에만 보존한다.
- 등록된 failure action에 따라 architecture, loss, step, seed, threshold를
  국소 수정하지 않고 current Aneumo 3D learning line을 중단한다. Scalar
  missing-inflow protocol, test/V2, method novelty와 ISBI submission은 열지
  않는다. V1/V1a 실패와 V1b/V1c/V1d asset-only 판정도 유지한다.
- `AGENTS.md`, README, research/model/protocol/ISBI/data/server 문서,
  executable protocol validator, result ledger, field guide와 site change window를
  같은 판정으로 동기화한다. Private manuscript source pin은 이 public commit이
  확정된 뒤 갱신한다.

## 2026-08-08 · V1d passes asset adequacy and V1e freezes known-condition learnability

- Exact source `369317a`의 V1d는 dependency-complete 199/199 tests와
  protocol/site 검증을 통과한 뒤 CPU audit을 exit 0으로 완료했다.
- Train 40·validation 12·test 0 case, boundary 468개와 reference-volume 52개
  payload를 감사해 9/9을 통과했다. 156/156 patch가 exact q-invariant였고
  52/52 case의 exact boundary-volume point correspondence와 minimum
  polygon-valid fraction 1.0을 확인했다. Field array와 test payload는 읽지
  않았다.
- Public aggregate는
  `results/aneumo_isbi_v1d_development_geometry_cache_20260808.json`이다. V1d는
  asset adequacy이지 model evidence가 아니며 V1 failure를 바꾸지 않는다.
- V1d가 허용한 범위에서
  `configs/aneumo_isbi_v1e_known_condition_baseline.json`을 어떤 V1e training
  또는 checkpoint보다 먼저 고정했다. 같은 parameter·320-token budget의
  boundary Perceiver와 geometry-only control을 fresh three-seed, six GPU task로
  비교한다. Full-field MSE만 학습하고 paired-response loss는 0이다.
- V1e는 absolute learnability와 seed-robust 5% boundary utility를 모두
  요구한다. 실패하면 current Aneumo 3D line을 local repair 없이 중단한다.
  통과해도 scalar missing-inflow development protocol만 등록할 수 있으며
  test/V2, multicomponent partial claim, novelty와 submission은 열리지 않는다.

## 2026-08-08 · V1c passes geometry staging and V1d seals development caching

- Exact source `84fc244`는 pinned container에서 dependency-complete 193/193
  tests와 protocol/site 검증을 통과했다. 이어진 V1c CPU run은 exit 0으로
  완료돼 8/8을 통과했다. 20 train representatives, 60 patches, 180 payloads를
  확인했고 60/60 patch가 세 flow에서 exact invariant였다. Minimum
  polygon-valid fraction은 1.0이고 private geometry cache는 3.93 MB다.
- `U/p/TimeValue`, validation/test payload, model/checkpoint는 읽지 않았다.
  Public aggregate
  `results/aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json`의
  SHA-256은 `a023e9fb...bbd1`이며 private cache는 재배포하지 않는다. 이 pass는
  full boundary-aware geometry-cache staging protocol 등록만 허용한다.
- `configs/aneumo_isbi_v1d_development_geometry_cache.json`은 V1c outcome 뒤,
  validation geometry payload decode 전에 고정했다. Train 40·validation
  12·test 0 case의 boundary VTP 468개와 volume VTU 52개에서 geometry만
  decode한다. Q-invariance·topology·frame·bounds와 함께 모든 boundary point가
  reference-volume point에 exact하게 대응해야 한다.
- V1d pass도 known-condition strong-baseline **protocol 등록**만 허용한다.
  Model training, test geometry/field, V2, partial/missing method, novelty와
  submission은 계속 금지한다. V1 실패와 current branch 폐기는 유지한다.

## 2026-08-08 · V1b passes asset identifiability and V1c freezes geometry staging

- Exact source `fb1c21a`의 V1b CPU audit은 20 ZIP64 archives, 64 cases,
  384 required members와 train-family representative 60 VTP payload를 확인해
  8/8을 통과했다. Point/polygon count 범위와 manifest hash를 public aggregate
  `results/aneumo_isbi_v1b_boundary_asset_audit_20260808.json`에 고정했다.
  Validation/test payload, field arrays, model과 checkpoint는 읽지 않았다.
- V1b가 허용한 범위에서
  `configs/aneumo_isbi_v1c_boundary_geometry_staging_audit.json`을 geometry array
  decode 전에 고정했다. 20 train representatives×3 patches×3 flows의 180
  payload에서 `Points/connectivity/offsets`만 decode해 exact q-invariance,
  polygon validity, patch area/frame와 compact-cache coordinate frame을
  검사한다. 성공한 private geometry cache의 hash만 공개한다.
- V1c pass도 full boundary-aware geometry-cache staging protocol 등록만
  허용한다. 기존 V1은 5/7 failed, current backbone branch는 retired 상태로
  보존한다. Local repair, model training, V2/test, method novelty와 submission은
  계속 금지한다.

## 2026-08-08 · V1b discloses boundary-asset discovery and freezes a full audit

- 기존 compact cache와 official Aneumo release를 구분한다. 등록 전 pinned
  archive 1/case 1의 central directory/header에서 `.msh`, `.stl`,
  `internal.vtu`, `inlet/outlet/wall.vtp`, connectivity, `U`, `p`를 확인했다.
  이 discovery는 prospective evidence가 아님을 config에 명시한다.
- `configs/aneumo_isbi_v1b_boundary_asset_audit.json`은 이후 20 ZIP64
  archives·64 cases의 required member와 train family representative 20
  cases×3 patches의 CRC/VTP contract를 감사한다. Validation/test payload와
  field-array decoding, model/checkpoint는 금지한다.
- 8/8 pass도 새 boundary-aware cache staging audit 등록만 허용한다. V1
  failure, current branch 폐기와 local-repair 금지는 유지하며 boundary token,
  known-BC encoding 또는 mesh GNN을 novelty나 성능 결과로 승격하지 않는다.

## 2026-08-08 · V1a attributes failure to training underfit, not only generalization

- Exact source `3a0d27f`의 fixed-checkpoint V1a는 PBS job `115051`에서 exit
  0, test-read false로 완료됐다. 서버 raw artifact SHA는
  `4e11be6f...d91a`, public aggregate는
  `results/aneumo_isbi_v1_attribution_20260808.json`이다.
- 네 family의 seed-mean train full-q L2가 `0.76939--0.95647`, validation이
  `1.01369--1.02469`다. Train prediction/target norm ratio와 cosine도 각각
  `0.35004--0.66921`, `0.29710--0.61342`여서 V1 실패는 family-disjoint
  generalization 하나가 아니라 training underfit과 vector collapse를 포함한다.
- Validation within-case condition energy fraction `0.15748`, same-case mean
  oracle full-q L2 `0.56843`, true-anchor response oracle `0.22794`는 condition
  signal이 비자명함을 보이지만 geometry-only reconstruction을 입증하지 않는다.
  V1 실패와 local-repair 금지를 유지하고 current geometry-only branch를
  폐기한다. Learned method 전에 새 task/data identity를 별도 감사하며 V2,
  test, novelty와 submission 상태는 열지 않는다.

## 2026-08-08 · V1 fails 5/7; V1a freezes attribution without local repair

- Exact task source `a0479fb`의 4 family×3 seed는 12/12 exit 0이었고,
  aggregate source `78dca92`가 checkpoint SHA, validation replay `1e-5`,
  exact config/cache와 no-test-read를 모두 확인했다. Public aggregate는
  `results/aneumo_isbi_v1_20260808.json`이다.
- Selector는 q-PointNet을 골랐지만 worst-seed full-q/response relative L2
  `1.03459/1.00354`가 frozen `0.35/0.50`을 실패했다. Gate는 5/7이며 다른
  kNN-MGN, DeltaPhi graph, anchor-token도 약 1이라 superiority가 없다.
  True validation anchor response-only oracle `0.22794`는 selection/gate와
  learned reconstruction row에서 제외한다.
- Registered decision대로 current 3D backbone branch를 중단하고 hidden size,
  k, step, seed, loss와 threshold를 국소 수정하지 않는다. 다음 V1a는 기존
  checkpoint의 train–validation gap, norm/cosine, q-span과 truth-only condition
  energy만 threshold 없이 분석한다. Retraining, model selection, V1 relabel,
  V2/test, method novelty와 submission 권한은 없다.

## 2026-08-08 · V1 aggregate uses registered design values and split provenance

- Task-local log를 가진 aggregate replay는 selector/gate result 전에
  response-only oracle anchor를 식별하지 못해 exit 1이었다. Cache의 flow가
  `float32`라 등록값 `0.0025`가 `0.002499999944...`로 저장됐지만 oracle만
  absolute tolerance `1e-12`로 cache 값을 직접 비교한 구현 불일치였다.
- Cache loader가 이미 검증하는 `1e-9` 범위로 cache 순서와 등록된 8개 design
  값을 먼저 대조하고, anchor index와 analytic ratio는 config의 고정된 design
  값에서 계산한다. Oracle은 계속 response-only이며 selector와 gate에 들어가지
  않는다. Config, tolerance, task metric과 checkpoint는 바꾸지 않는다.
- Aggregate runner source와 기존 12개 task source를 하나의 SHA로 위장하지
  않고 `aggregate_git_commit`과 `task_git_commit`으로 분리해 artifact에
  기록한다. 실패 aggregate 두 건은 그대로 보존한다.

## 2026-08-08 · V1 aggregate failure becomes observable before any gate result

- Exact task source `a0479fb`의 fresh 4×3 PBS array는 12/12 exit 0,
  checkpoint·metric 12쌍, exact source/config와 no-test-read 전수 검사를
  통과했다. 별도 aggregate job은 17초 만에 exit 1이었고
  `aggregate.json`이나 `status.json`을 만들지 않았다.
- PBS history는 stage-out 성공을 기록했지만 지정 stdout 파일은 실제 output에
  나타나지 않았다. 따라서 실패를 model/gate 결과로 해석하지 않고 aggregate
  wrapper도 writable output에 `pbs.log`와 `pbs_status.json`을 직접 남긴다.
- Task checkpoint, model implementation, config, selector, threshold와 metric은
  변경하지 않는다. 새 wrapper exact contract 뒤 동일 12개 read-only artifact를
  replay하며, 실패 aggregate job과 빈 output은 보존한다.

## 2026-08-08 · V1 fixes scheduler-visible CUDA bookkeeping before cache access

- Task-local fail-safe를 포함한 exact `fd8bb40` one-task diagnostic은 A100을
  정상 할당받았지만 `torch.cuda.reset_peak_memory_stats(torch.device("cuda:0"))`
  호출에서 exit 1로 끝났다. `pbs_status.json`은 learned metric과 checkpoint가
  생성되지 않았음을 확인했고 traceback은 cache load와 training보다 앞섰다.
- 일부 pinned PyTorch/CUDA 조합에서 device 객체 인자를 거부하는 bookkeeping
  API만 current-device 호출로 바꾼다. CUDA device 0을 명시적으로 선택한 뒤
  reset, synchronize와 peak-memory query는 인자 없이 호출한다.
- Model, config, cache, seed, step, loss, selector, threshold와 scientific
  estimand은 바꾸지 않는다. 실패 array와 두 diagnostic은 보존하며, 새 exact
  contract와 one-task scheduler diagnostic 전에는 fresh 12-task array를
  제출하지 않는다.

## 2026-08-08 · V1 PBS failure becomes directly observable before metrics

- Exact `2ddd5e6`의 첫 `introai9` 12-task array는 앞선 세 subjob이 각각
  CPU 4초, exit 1로 끝나고 checkpoint·metric을 하나도 만들지 않아 나머지
  subjob을 취소했다. Scientific result나 gate failure로 해석하지 않는다.
- PBS가 exit finalization에서 stdout을 반환하지 않아 동일-source one-task
  diagnostic도 원인 message를 제공하지 못했다. 실패 array와 diagnostic
  provenance는 삭제하지 않는다.
- Model, config, data, seed, step, loss, selector와 threshold를 바꾸지 않고
  각 task의 writable output에 `pbs.log`와 `pbs_status.json`을 직접 남기는
  fail-safe만 추가한다. 새 exact source contract와 one-task diagnostic이
  통과하기 전 12-task array를 다시 제출하지 않는다.

## 2026-08-08 · V1 freezes complete aggregation semantics before learning

- Matching-q point prediction은 같은 family의 세 seed 평균으로, missing
  predictive distribution은 seed×8 registered q의 24-component mixture로
  고정했다. Ensemble metric은 selector에 사용하지 않으며 uncertainty
  separation claim도 지지하지 않는다.
- Same-case power 1.075 control은 true validation q=0.0025 field를 사용하는
  response-only oracle다. Learned reconstruction row, selector와 feasibility
  gate에서 제외한다.
- Exact 4 family×3 seed artifact manifest, checkpoint SHA, validation replay
  absolute tolerance `1e-5`, base-family-first aggregation, per-seed
  lexicographic selector와 기존 7개 gate를 executable aggregate runner에
  구현했다. Condition-zero control은 모든 후보에 계산하고 선택 family의 세
  seed에만 gate를 적용한다.
- 이 correction은 learned output과 새 cache field를 읽기 전 이뤄졌다. Model,
  seed, step, loss, scientific threshold와 selector 순서는 바뀌지 않았다.
- `introai9` public-key SSH와 PBS client는 확인했지만 scheduler GPU smoke,
  pinned container와 cache SHA가 아직 확인되지 않아 V1 learning은 unrun이다.

## 2026-08-08 · Corrected V1 source passes 168/168 before learning

- Exact correction `a8b0042f52d008f5085b7f6c16091682cd649917`은
  q-PointNet residual block 16→17 외 data, model, seed, step, tolerance와
  selector를 유지했다.
- Targeted V1 model contract 9/9와 external `h5py==3.12.1`을 포함한 full
  repository contract 168/168이 pinned container에서 exit 0으로 완료됐다.
  Rotation equivariance와 parameter matching이 모두 통과했다.
- Cache field와 learned metric은 아직 읽지 않았다. 이는 V1 GPU learning
  submission의 code 자격일 뿐 model 성능, method novelty, V2, headline
  또는 submission 증거가 아니다.

## 2026-08-08 · V1 pre-result contract corrects parameter matching

- Exact source `b8ce721`의 pinned-container model contract는 output shape,
  kNN self-edge exclusion, unique anchors와 anchor-token rigid-rotation
  equivariance를 포함해 8/9를 통과했다. Learned metric과 cache field는
  읽지 않았다.
- Registered model parameter counts는
  `357603/374979/384582/422114`였고 relative range 15.283%가 frozen 15%
  tolerance를 0.283%p 넘었다. Threshold를 완화하지 않는다.
- 가장 작은 q-PointNet residual block만 16→17로 올린다. 다른 architecture,
  data, node subset, seed, step, tolerance와 selector는 유지하며 새 exact
  full contract가 통과하기 전 학습을 제출하지 않는다.

## 2026-08-08 · V1 freezes one matched validation-only backbone smoke

### Scope and fair comparison

- `configs/aneumo_isbi_v1.json`에 20 train family/40 case와 6 validation
  family/12 case만 읽는 12-task protocol을 고정했다. Test 6 family/12 case
  field read와 모든 outer-test access는 false다.
- q-PointNet, kNN-MGN, DeltaPhi graph residual, frame-free anchor-token
  equivariant operator를 동일 deterministic 1,024-node subset, 세 seed,
  hidden 96, 3,000 step과 train-only scalar velocity normalization으로
  비교한다. Family별 residual block으로 parameter range를 15% 안에 맞춘다.
- Selector는 seed-mean response L2, full-q L2, exact eight-component missing
  field energy, parameter count 순이다. `candidate` 이름은 우선권이 없고
  paired-response loss weight는 0이다.
- Same-case anchor power 1.075 scaling은 response-only oracle control이다.
  Deep ensemble은 동일 세 seed를 재사용해 design-law uncertainty만
  기술한다.

### Guardrails and implementation

- Anchor-token output은 local/anchor displacement vector의 scalar combination으로
  구성해 rigid-rotation equivariance를 코드 수준에서 검사한다. 이는
  engineering backbone이지 contribution이 아니다.
- 12/12 exit, no-test-read, finite metrics, validation checkpoint, generous
  worst-seed feasibility와 q-zero negative control을 모두 요구한다. 실패 뒤
  hidden size, k, step, seed, threshold를 국소 수정하지 않는다.
- V1 pass도 한 backbone을 별도 mechanism protocol에 고정할 자격뿐이다.
  Positive M0 전 measurement–solution objective를 추가하지 않으며 V2,
  headline, novelty와 submission은 계속 닫는다.

## 2026-08-08 · V0 passes all checks without opening the headline

- Exact public source `0589070`, config SHA
  `0c9745e42e84149d5f788a4e4425ab02028267cc9d1e0b4685ec92d7baf43559`의
  pinned-container CPU audit이 exit 0으로 완료됐다. Raw result SHA는
  `ec6b50269e929b3b3fad109b239f7c220e22a628222c95b077249656b84ffb50`다.
- Cache/dependency integrity, family split, scalar mass-flow contract, tensor
  metadata, field-access lock, velocity nontriviality, design-law semantics와
  unsupported endpoint exclusion이 8/8을 통과했다.
- V0는 새 field array와 validation/test field를 읽지 않았다. Velocity
  tuned-scaling residual CI lower는 0.20013으로 frozen 0.15 기준을 넘었고
  pressure는 계속 제외한다.
- 판정은 `v1_64_case_implementation_smoke_only`다. Learned performance,
  method novelty, outer test, headline과 ISBI submission authorization은
  모두 false다. 공개 aggregate는
  `results/aneumo_isbi_v0_20260808.json`이다.

## 2026-08-08 · ISBI V0 fixes the 3D task before model implementation

### Prospective asset and estimand gate

- `configs/aneumo_isbi_v0.json`에 compact-cache와 dependency SHA,
  32-family 20/6/6 split, 8개 scalar mass flow, 64×8×4,096×4 tensor
  metadata와 기존 train-only scaling aggregate를 고정했다.
- V0는 새 field array를 읽지 않는 8-check metadata/task audit이다. Missing
  inflow는 8개 조건의 discrete-uniform experimental design law이며 patient
  physiology나 실제 measurement distribution으로 표현하지 않는다.
- Compact cache에는 boundary marker, surface normal, verified integration
  mesh가 없으므로 pressure, WSS/OSI와 mass-conservation endpoint를
  제외한다. Pressure는 기존 scaling gate도 실패했다.
- 모든 check가 통과해도 64-case V1 implementation smoke만 허용한다.
  Model novelty, outer test, headline result와 ISBI submission은 계속 닫는다.
  실패하면 threshold나 schema를 국소 수정하지 않고 이 asset의
  missing-inflow distribution branch를 중단한다.

### Implementation and synchronization

- Strict config loader, whole-cache/dependency hash, HDF5 metadata, family
  split와 공개 scaling aggregate 검증기를 추가했다.
- AGENTS, README, research/model/protocol 문서, executable protocol validator,
  사이트 evidence/status와 changelog가 동일한 V0 경계를 말하도록
  동기화했다.

## 2026-08-06 · ISBI 2027 target lock makes 3D velocity evidence mandatory

### Venue and claim boundary

- 공식 ISBI 2027 regular-paper 마감은 2026-10-26 23:59 USA EDT이고,
  single-blind 심사와 technical content 4-page 제한을 고정했다.
- 현재 N1c 실패와 3D evidence 부재를 근거로 `not submission-ready`를
  유지한다. Exact/nonlinear PDE만으로 biomedical-imaging contribution을
  주장하지 않는다.
- ISBI identity는 missing scalar inflow 아래의 3D aneurysm velocity
  reconstruction·calibration·same-geometry response로 좁힌다. Pressure,
  WSS/OSI, transient efficiency, rupture prediction과 clinical utility는
  제외한다.

### Architecture truth and experiment ladder

- 실행된 exact/nonlinear model은 context MLP + boundary token + lifted
  decoder다. GNN+anatomy token+continuous query 구조는 irregular-3D
  target specification이며 아직 구현·검증된 현재 모델이 아니다.
- 64-case Aneumo cache는 development pilot이다. Expanded 또는 independent
  base-family-disjoint 3D outer test, five seeds, bootstrap CI와 strong
  graph/operator baseline이 없으면 headline을 열지 않는다.
- M0는 one-shot nonlinear mechanism falsification으로만 남긴다. 통과해도
  scalar-inflow 3D estimand에 맞춘 별도 prospective translation contract가
  필요하며, 실패 뒤 local repair는 금지한다.
- `docs/isbi-2027-plan.md`에 V0/V1/V2 evidence ladder, four-page 구성,
  2026-08-10부터 submission일까지의 kill date를 기록했다.

### Synchronized surfaces

- `AGENTS.md`, README, research/model/protocol 문서, executable config와
  validator tests, main site/field guide/changelog가 같은 target과
  readiness를 말하도록 동기화했다.

## 2026-08-06 · M0 freezes one operator-specific mechanism without a repair loop

### Research gap and method boundary

- 2024–2026 direct prior art를 재감사해 solution-marginal proper scoring,
  arbitrary conditioning, path compatibility, AFA, acquisition-conditioned
  oracle와 neural-operator Thompson sampling을 독립 novelty에서 제외했다.
- 남은 좁은 gap은 candidate measurement \(B_j\)와 solution functional
  \(\Psi(H)\)의 joint dependence다. 두 marginal이 각각 같아도 dependence가
  다르면 post-measurement Bayes risk와 VoI가 달라질 수 있다.
- M0는 하나의 analytically conditionable joint BC density를 유지하고,
  frozen full-condition operator를 통한 candidate-wise
  \((B_j,\Psi(H))\) product-kernel pushforward score를 full-joint
  likelihood에 더한다. Kernel score, probabilistic operator, active
  acquisition과 generic IPM bound 자체는 novelty로 주장하지 않는다.

### Prospective validation-only contract

- `configs/nonlinear_pde_n1_missing_operator_pullback_m0.json`에 missing-only
  3-seed development gate를 output 전에 고정했다. 3,072×8 train,
  384×8 selection, disjoint 192×8 audit와 first-96 acquisition context를
  사용하고 N1 test는 생성·접근하지 않는다.
- Full-joint MLE, full-boundary kernel, solution-marginal kernel과 proposed
  candidate–solution joint pullback을 identical initialization, minibatch,
  kernel random number, checkpoint-selection metric으로 비교한다.
- Candidate-joint MMD²와 true-oracle acquisition regret가 각각 strongest
  control 대비 ≥5%, 3/3 seed, paired-context CI95 upper <0을 만족해야 한다.
  Density excess degradation ≤5%, solution MMD² degradation ≤1%와 모든
  frozen-operator audit L2 ≤0.05도 동시에 요구한다.
- 하나라도 실패하면 weight, kernel scale, mask, seed, sample budget,
  threshold를 국소 조정하지 않고 mechanism을 폐기한다. 통과해도 별도
  five-seed fresh re-entry protocol 설계 자격일 뿐 method, novelty,
  N1c relabel, N1d/3D 권한은 아니다.

### Implementation and synchronized surfaces

- Strict loader, differentiable GMM pullback score, frozen-operator training,
  true-simulator MMD/acquisition audit, private per-context output와
  public aggregate gate를 구현했다. PBS는 code/checkpoint read-only,
  output-only writable인 A6000 array 0–2다.
- Protocol validator와 tests가 M0의 missing-only scope, test lock,
  all-checks rule과 failure-terminal/no-local-repair 계약을 강제한다.
- 연구 방향, model spec, experiment protocol, executable contract,
  README, AGENTS 운영 규약, 사이트의 architecture/evidence/changelog를
  같은 판정으로 동기화했다.

## 2026-08-06 · Post-N1c audits complete without selecting a method

### Exact-source execution

- Exact source `337c75e6fcb933eaab86c900fc132d4a13b740a5`의
  dependency-complete A6000 contract job `110165`는 144/144를 통과했다.
- Density array `110170[0-4]`는 fresh 다섯 seed 모두 exit 0,
  `test_generated_or_accessed=false`로 완료됐다. Model-free task job
  `110171`도 exit 0, walltime 58분 04초였고 2,882 solver batch가 모두
  수렴했다. Learned model/checkpoint와 N1 test는 읽지 않았다.
- 공개 aggregate SHA-256은 density
  `94686547ea927324cd4e376c3500067176843b401511d519e993864ea199b147`,
  task
  `4492a7759fc08b4c2ac81196e2c345634419215f89030b062356aa801e232ab7`다.
  Raw history, checkpoint와 per-context metric은 private provenance에만
  보존한다.

### Density-objective attribution

- Full-joint per-component NLL의 exact-law excess는
  missing/sparse-2/partial-4에서 0.04622/0.05923/0.07808이었다. N1c raw
  conditional objective보다 27.2%/23.8%/20.3% 낮고 모든 mask에서 5/5
  seed 방향이 같았다.
- Registered composite는 1.5–2.5%의 작은 5/5 개선이었다. 단순
  per-component normalization은 missing/sparse-2/partial-4에서
  1/5, 2/5, 4/5 방향으로 일관되지 않았다.
- Full-joint likelihood가 현재 strongest engineering control이라는
  진단은 채택한다. 표준 joint MLE를 method나 novelty로 선택하지 않으며,
  N1c test를 재사용하지 않는다.

### Decision-task adequacy

- Missing base risk 0.50366은 독립 replicate에서
  0.34778/0.34807로 줄었다. VoI는 0.15587/0.15558, winner agreement는
  0.9271, top-2 agreement는 0.7396이었다. Missing은 future
  decision-aware evaluation 후보로 남긴다.
- Sparse-2 base risk 0.33221도 0.14704/0.14667로 줄어 acquisition value는
  분명했지만, component 6이 두 replicate 모두 96/96 context의 winner였다.
  따라서 sparse-2는 adaptive-policy comparison에서 제외하고 fixed
  acquisition control로만 보존한다.
- 이는 threshold-free task evidence이지 pass/fail gate가 아니다. N1c
  failed, current identity unsupported, method unselected, fresh re-entry와
  N1d/irregular-3D blocked 판정을 유지한다.

### Synchronized surfaces

- 공개 결과:
  `results/nonlinear_pde_n1_density_objective_audit_20260806.json`,
  `results/nonlinear_pde_n1_decision_task_audit_20260806.json`.
- 판정과 숫자를 `AGENTS.md`, `README.md`,
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `configs/aurora_v1.json`,
  `site/assets/research-data.js`, main site와 field guide에 동기화한다.

### Deployment

- Result-sync commit
  `c8a427bd574c27848120139f4e2349c74a010649`의 research-contract
  quality와 GitHub Pages workflow가 모두 통과했다.
- Public hub `https://gohyunsu.github.io/aneurysm/site/index.html`, field
  guide와 두 frozen aggregate URL이 최신 판정·수치를 제공하며 HTTP 200을
  반환함을 확인했다.

## 2026-08-06 · Post-N1c development audits are frozen before output

### Density-objective control

- `configs/nonlinear_pde_n1_density_objective_audit.json`은 N1c-a 공개
  aggregate와 N1 joint-density architecture를 pin한다. N1의 development와
  confirmatory seed에 겹치지 않는 fresh seed 5개를 사용한다.
- 3,072×8 train, 384×8 selection-validation, disjoint 384×8
  audit-validation에서 같은 initial weight, minibatch, optimizer와 step당
  likelihood 평가 한 번을 고정한다.
- N1c random-mask raw conditional NLL, 동일 loss의 per-component
  normalization, full-joint per-component NLL, registered-mask equal-cycle
  composite per-component NLL을 모두 실행한다. Cross-variant winner를
  선택하지 않고 exact radius-truncated true-law excess NLL을 seed별로
  보고한다.

### Method-independent decision-task audit

- `configs/nonlinear_pde_n1_decision_task_audit.json`은 learned model과
  checkpoint를 전혀 읽지 않는다. True simulator calibration 384×8과
  disjoint 96-context audit split만 사용한다.
- Missing/sparse-2 mask에서 base posterior 2,048 sample과 독립적인 두
  outer 32 × inner 64 replicate를 고정했다. VoI, winner margin/entropy,
  candidate-risk dispersion, Bayes-action diversity/change와
  cross-replicate winner·top-2·risk stability를 함께 보고한다.
- 두 audit 모두 success threshold, method selection, N1 test access,
  N1c relabel, fresh re-entry와 N1d/irregular-3D 권한이 없다. Positive
  feasibility signal도 별도 fresh prospective protocol을 설계할 근거일
  뿐이다.

### Implementation and synchronized surfaces

- 새 loader·trainer·true-oracle evaluator·runner·PBS wrapper, 결과 전
  public-aggregate 변환기와 변조 방지 unit test를 추가했다. 변환기는 seed
  누락, test 접근, model selection 또는 task-audit checkpoint 사용을
  거부한다. Public code는 read-only, output만 writable bind하며 density는
  0–4 PBS array, task audit은 checkpoint mount 없는 단일 job이다.
- 영향 파일:
  `docs/research-direction.md`, `docs/model-spec.md`,
  `docs/experiment-protocol.md`, `configs/aurora_v1.json`,
  `site/assets/research-data.js`, `site/index.html`, `site/learn.html`,
  `README.md`, `AGENTS.md`, `docs/server-execution.md`,
  `src/aurora/protocol.py`, generic container contract wrapper와 새 audit
  code/config/PBS/test.

### Preregistration deployment

- Exact preregistration commit:
  `ab6bd38e10e4d60dacef5463c0b53883acaf2d9b`.
- GitHub research-contract quality와 Pages build가 모두 통과했다.
- Public hub `https://gohyunsu.github.io/aneurysm/site/index.html`과 두
  config URL이 `preregistered/unrun`, no-threshold, no-checkpoint 경계를
  production에서 그대로 제공함을 확인했다.

## 2026-08-06 · N1c-a completes and rejects the current paper identity

### Exact-source execution

- Exact source `b97899c`의 PBS A6000 contract job `109738`은 130/130을
  통과했고, 5-seed metric job `109739`는 exit 0, walltime 49분 48초로
  완료됐다.
- N1c와 같은 192×12 open test와 frozen 50 checkpoint만 재사용했다.
  새 test seed, checkpoint/model selection, success threshold는 없다.
- Raw aggregate SHA-256은
  `01fa774e17b43c7c14d68da1b9be46cac020aa81239f3bf136f6add7b0720070`이며
  raw/per-context artifact는 private run provenance에만 보존한다.
  공개 저장소에는 검증된 aggregate
  `results/nonlinear_pde_n1c_attribution_20260806.json`만 둔다.

### Scientific decision

- Joint conditional excess NLL은 missing/sparse-2/partial-4 모두
  independent heads보다 0/5 seed로 열세였다.
- Functional energy의 mean oracle-substitution difference는 density가
  simulator보다 missing에서 13.0배, sparse-2에서 5.81배 컸다. 이는
  non-additive diagnostic이지 causal error decomposition은 아니다.
- Missing acquisition은 64×128에서도 ACFlow보다 1/5 seed에서만 좋았고,
  sparse-2는 AURORA와 ACFlow 모두 0 regret라 판별력이 없었다.
- AURORA는 route candidate risk를 약 \(3.1\times10^{-8}\) 안에서
  일치시켰지만 independent heads보다 true-oracle worst-route risk가 낮은
  seed는 3/5였다. Structural compatibility가 robust decision advantage로
  이어졌다는 주장은 지지되지 않는다.
- N1c failed, paired-response ablation, N1d/irregular-3D blocked를
  유지한다. 현 paper identity는 폐기하며, 다음은 validation-only
  density-objective control과 true-law/simulator-only decision-task
  adequacy audit이다. Composite likelihood, compatibility와
  decision-focused training 자체는 novelty로 세지 않는다.
- 최상위 실행 계약도 이 demotion과 맞춘다. Headline
  `paired_response` weight는 0으로 고정하고, 0.5는 이름이 명시된
  ablation weight로만 보존한다. Validator는 paired loss가 조용히 main
  objective로 복귀하거나 ablation control이 사라지는 경우를 모두
  거부한다.

### Deployment

- Content commit `559591b`의 research-contract quality와 GitHub Pages
  workflow가 모두 통과했다.
- Public hub:
  `https://gohyunsu.github.io/aneurysm/site/index.html`
- N1c-a aggregate:
  `https://gohyunsu.github.io/aneurysm/results/nonlinear_pde_n1c_attribution_20260806.json`
- Main, 11-chapter guide와 aggregate가 production에서 최신 N1c-a 문구와
  함께 HTTP 200을 반환함을 확인했다.

## 2026-08-05 · N1c-a failure attribution is fixed before execution

### Threshold-free diagnostic contract

- `configs/nonlinear_pde_n1c_attribution.json`은 failed N1c 공개 결과와
  동일 N1c config, open test, 50개 frozen checkpoint를 pin한다. 새 seed,
  checkpoint selection, threshold와 pass/fail은 없다.
- Joint/independent/ACFlow의 mask별 conditional NLL, true radius-truncated
  law와 true simulator를 한 축씩 대입한 functional energy,
  acquisition 8×32/32×64/64×128 stability, true-oracle route excess risk를
  분해한다.
- Route candidate risk는 direct/5→7/7→5에 동일 random stream을 쓰도록
  수정하고 회귀 테스트를 추가했다. 이 수정은 N1c에서 제외한 두 보조
  지표를 위한 post-result diagnostic이며 failed gate를 바꾸지 않는다.
- N1d와 irregular 3D는 계속 닫혀 있고, method 변경은 새 version과 fresh
  seed/test를 요구한다.

### Pre-metric runtime correction

- 첫 본 job `109733`은 checkpoint/model/test metric을 만들기 전에
  `experiments` helper import에서 종료됐다. PBS의 container
  `PYTHONPATH`에 `/workspace`가 빠진 entrypoint wiring 오류였다.
- `/workspace/src:/workspace`를 명시하고 wrapper regression test를
  추가한다. 실패 run은 보존하며 수정 commit의 full contract 전에는
  재제출하지 않는다.
- 수정 source의 첫 재실행 `109735`도 seed aggregate 전에 oracle
  energy-floor solve에서 CUDA OOM으로 종료됐다. Evaluation helper가
  autograd graph를 불필요하게 보존한 것이 원인이다.
- Oracle solver를 `no_grad`로 고정하고 energy-floor batch만 512에서
  128로 낮춘다. Estimand·sample 수·checkpoint·test는 바꾸지 않으며,
  output이 gradient graph를 갖지 않는 회귀 테스트를 추가한다.
- 첫 메모리 수정 commit의 contract job `109737`은 130개 중 이 새 회귀
  테스트 하나에서 실패했다. PDE solve만 `no_grad`였고 뒤이은 functional
  계산이 gradient-enabled 입력 context를 통해 graph를 다시 만들 수
  있었기 때문이다. 본 실험은 제출하지 않았으며, field 결합과 functional
  계산까지 같은 `no_grad` 경계로 옮겨 helper 자체가 호출 환경과 무관하게
  graph-free임을 보장한다.

## 2026-08-05 · N1c completes and fails the strong-baseline outer test

### Prospective result

- Exact source `62605a0`은 dependency-complete PBS A6000 contract
  125/125를 통과했다. 50개 learned checkpoint와 공통 POD hash를 모두
  확인한 뒤에만 192 context × 12 condition test를 생성했다.
- PBS `109724`는 5 seed를 exit 0, walltime 2분 34초로 완료했다. Raw
  aggregate SHA-256은
  `a3759dcf7d47aa3f636e8cab695ee96d285d60c7236e4899bb2af0737ebc0368`이고
  공개 결과는 `results/nonlinear_pde_n1c_20260805.json`이다.
- Full-BC operator, functional coverage와 AURORA route-action consistency는
  통과했다. Field distribution, paired response와 acquisition regret는
  실패해 N1은 failed다.
- Missing/sparse-2 energy score는 independent heads보다 각각
  0.65%/1.09% 나빴고 AURORA가 좋은 seed는 0/5였다. Missing acquisition
  regret는 ACFlow보다 2/5 seed에서만 낮았다. Sparse-2에서는 두 learned
  policy가 모두 oracle과 같아 strict superiority가 성립하지 않았다.
- Pair loss는 pair-zero보다 pooled context bootstrap에서는 좋았지만
  seed 방향은 3/5였고 seed-mean paired-response L2 0.01331은
  DeltaPhi-style 0.01221보다 나빴다. Paired supervision을 독립
  contribution에서 ablation으로 내린다.

### Integrity and next decision

- Independent/ACFlow의 route action은 route에 따라 달랐지만 signed
  true-risk difference가 작고 seed별 부호가 섞여 positive decision harm는
  입증되지 않았다.
- Candidate VoI subroutine이 route별 seed offset을 사용해 등록된 common
  random numbers를 위반했음을 post-result audit에서 발견했다. VoI와
  selected-next-component 보조 지표만 invalid로 제외한다. Gate에 쓰인
  field, pair, acquisition과 valid route-action 지표에는 영향이 없으므로
  N1 fail은 바뀌지 않는다.
- N1d shift와 irregular 3D는 실행하지 않는다. 다음은 joint conditional
  NLL, true-law/operator floor, acquisition MC stability와 true-oracle
  worst-route excess risk를 분해하는 threshold-free attribution이다.

## 2026-08-05 · N1c outer-test execution is frozen before test access

### Prospective estimand and implementation

- `configs/nonlinear_pde_n1c.json`은 public checkpoint manifest commit
  `c66f651`과 50개 checkpoint hash를 pin한다. Runner는 모든 hash를
  재검증한 뒤에만 parent의 test seed를 처음 읽는다.
- Route/acquisition은 192 context에서 결과와 무관한 index
  `0,4,…,188`, condition 0을 사용한다. Functional scaling·action grid는
  operator-training split에서만 정한다.
- True conditional과 ACO ceiling은 latent radius 2.5 truncation을
  component별 chi-square acceptance와 conditional residual rejection으로
  반영한다. Untruncated Gaussian conditional을 정답으로 쓰지 않는다.
- Direct/sequential route의 functional posterior, Bayes action, true action
  risk와 candidate VoI를 함께 측정한다. Route가 정의되지 않는 LANO/direct
  operator는 N/A이지 0이 아니다.
- Active acquisition, functional operator optimization, analytic
  conditioning, route consistency와 generic regret는 각각 novelty로
  주장하지 않는다. Positive identity에는 solution-functional decision
  consequence와 strong-baseline improvement가 모두 필요하다.

### Execution boundary

- N1c는 ID distribution, paired response, route, acquisition regret의
  single outer test다. Registered support/geometry/hidden-law shift는
  model·threshold·test seed를 바꾸지 않는 별도 N1d secondary job이다.
- N1c source의 public commit과 dependency-complete A6000 contract 전에는
  test split을 생성하지 않는다. N1과 3D는 아직 미결정·차단 상태다.
- 첫 두 exact-source attempts는 checkpoint hash verification 뒤 동일
  test marker까지 남기고 exit 1이었지만 read-only source로 반환되는 PBS
  spool 때문에 traceback을 보존하지 못했다. Scientific config·runner는
  바꾸지 않고 batch wrapper만 stdout/stderr를 writable output의
  `run.log`에 명시적으로 기록하도록 보강한다. 두 attempt는 failed
  provenance로 보존하며 결과가 아니다.
- Logging-fixed attempt 3에서 test marker 뒤, seed-0 metric 생성 전에
  `generate_solution_split` 반환값에 없는 `true_weights`를 읽어
  `KeyError`가 발생했다. 이는 결과를 보지 않은 schema wiring 오류다.
  Frozen test context에 기존 analytic `boundary_law`를 다시 적용해
  true GMM parameter를 복원한다. Config, context/seed, truncation,
  checkpoint, metric과 threshold는 바꾸지 않는다.

## 2026-08-05 · N1b five-seed checkpoint manifest is complete

### Validation-only execution

- Exact `1d0bd9c`의 dependency-complete A6000 contract는 117/117을
  통과했고, 다섯 confirmatory checkpoint job은 모두 exit 0이었다.
- 모든 run은 checkpoint-eligible이고 test context 0, test split/seed
  access false다. Seed별 10개 learned checkpoint와 공통 train-only
  POD-96의 SHA-256을
  `results/nonlinear_pde_n1b_checkpoint_manifest_20260805.json`에 고정했다.
- AURORA validation full-BC/paired-response relative L2의 seed mean은
  0.01347/0.01366이다. Pair loss는 pair-zero보다 4/5, random-pair보다
  3/5, DeltaPhi-style paired metric보다 2/5 seed에서 좋았다. Combined
  objective는 DeltaPhi-style보다 0/5 seed에서 좋았다.

### Decision

- Checkpoint freeze 완료는 outer-test 실행 자격일 뿐 N1 pass, baseline
  superiority, method novelty가 아니다. 강한 DeltaPhi validation 결과를
  숨기지 않는다.
- 192 test context 중 48개 acquisition context selector, evaluation RNG,
  route estimand, bootstrap과 checkpoint-manifest hash를 별도 prospective
  overlay에 commit하기 전 test split을 생성하지 않는다.
- N1과 irregular-3D는 계속 차단한다.

## 2026-08-05 · N1b model RNG is separated from the fixed POD RNG

### Pre-test implementation correction

- Exact `938d6c2`의 dependency-complete contract는 117/117을 통과했고
  seed 0–2 checkpoint jobs도 exit 0, test access false였다.
- 감사 결과 direct generic/NOP의 weight initialization이 고정 POD seed 뒤
  RNG state를 상속하고, confirmatory seed는 minibatch sampling에만
  반영됨을 발견했다. 표현을 seed 간 공유하는 것은 의도했지만 weight
  initialization까지 공유하는 것은 five-seed uncertainty를 과소평가한다.
- 아직 test를 생성하지 않았으므로 seed 3 running/seed 4 queued job을
  중단했다. Seed 0–2 artifact는 runtime diagnostic으로 보존하지만
  checkpoint manifest에 넣지 않는다.
- POD seed 73080601과 iteration 4는 유지하고, direct model build 직전 RNG를
  각 confirmatory seed로 reset한다. 수정 source의 dependency-complete
  contract 뒤 5개 checkpoint job을 모두 새로 실행한다.

## 2026-08-05 · N1a selects optimization; prospective N1b is frozen

### Validation-only result

- Exact `eebcd91`의 PBS A6000 run은 116/116 contract 뒤 exit 0으로
  완료됐고 test split·seed·context는 생성하거나 읽지 않았다.
- Raw 1,400/2,800-step validation objective는 0.05007/0.02071,
  scale-normalized 1,400/2,800은 0.03732/0.01772였다.
- 고정 selection rule은 scale-normalized 2,800-step을 골랐다. 해당
  checkpoint의 full-BC/paired-response L2는 0.01162/0.01220이다.
- 이 결과는 기존 miss의 optimization attribution이며 N1 pass, baseline
  superiority, method novelty 또는 3D 실행 권한이 아니다.

### Prospective checkpoint-freeze contract

- `configs/nonlinear_pde_n1b.json`은 parent N1의 data, split, seed, mask,
  mandatory baseline, metric과 threshold를 유지하고 N1a 선택만 고정한다.
- 다섯 confirmatory seed에서 모든 learned model을 train/validation으로
  선택하고 checkpoint SHA-256 manifest를 public commit하기 전 outer test
  generation을 금지한다.
- Direct generic/NOP baseline의 train-only centered POD-96과 latent
  Gaussian은 compute-matched control이며 architecture novelty가 아니다.
- 실행 전 세부 amendment로 모든 confirmatory seed가 같은 POD를 쓰도록
  representation seed 73080601과 randomized subspace iteration 4회를
  고정했다. Test 또는 confirmatory metric은 아직 생성되지 않았다.

## 2026-08-05 · Unit-peak N1 core remains insufficient; N1a is frozen

### Validation-only result

- Exact `54046a3`의 두 번째 development seed는 full-BC L2를
  0.1739→0.05771, paired-response L2를 0.1862→0.05729로 낮췄다.
- 개선은 크지만 unchanged 0.05 기준을 넘고 best checkpoint가 다시
  maximum 1,400 step이므로 core checkpoint는 여전히 ineligible다.
- Test split/seed, N1 gate, confirmatory path와 3D는 접근하지 않았다.

### Preregistered attribution

- `configs/nonlinear_pde_n1_optimization_attribution.json`에 새 development
  seed, raw/scale-normalized loss와 1,400/2,800 step의 2×2 비교를 동결했다.
- N1a는 threshold가 없고 test/N1/3D를 열 수 없다. 선택 variant도 새
  prospective N1 version에 고정하기 전 confirmatory evidence가 아니다.

## 2026-08-05 · First N1 core development is insufficient

### Validation-only result

- Exact `6075530`의 A6000 run은 113/113 contract와 모든 train/validation
  solver를 통과했다. Test split과 test seed는 생성·접근하지 않았다.
- Joint-density best validation NLL은 -4.290이었다. Lifted operator의
  full-BC relative L2 0.1739와 paired-response relative L2 0.1862는
  preregistered full-BC 0.05 자격과 거리가 있고 best epoch도 maximum
  1,400이었다.

### Decision

- Density가 학습됐다는 사실로 operator failure를 덮지 않는다. N1 gate,
  baseline superiority, confirmatory test, 3D는 모두 열지 않는다.
- Exact-zero interior envelope를 unit peak로 16배 재척도화한다. 함수
  클래스·rank·data·loss·threshold·test rule은 그대로이며 두 번째
  development seed에서만 재검사한다.

## 2026-08-05 · N1 tensor shape is corrected before any metric

### Pre-execution amendment

- 첫 PBS contract attempt는 metric runner 제출 전에 coordinate correction
  `[B,1089]`과 unflattened envelope `[33,33]`의 shape mismatch를 검출했다.
- Envelope를 `[1089]`로 flatten했다. Data, seed, model rank, loss,
  threshold, test-access rule은 바꾸지 않았고 scientific/development
  metric은 생성되지 않았다.
- 첫 attempt는 source SHA 문자열도 잘못 축약돼 provenance-invalid로
  보존한다. 수정 commit의 full SHA로 dependency-complete contract를 새로
  제출한다.

## 2026-08-05 · N1 core has a validation-only execution path

### Implementation

- Context-conditioned full-covariance 2-GMM, truncated latent-BC sampler,
  chunked semilinear split solver와 exact Dirichlet-lifted rank-96 coordinate
  operator를 구현했다.
- 첫 runner는 density/operator train·validation만 생성한다. Test generator를
  호출하지 않고 output status에 test access와 N1 decision이 모두 false임을
  남긴다.
- 이 smoke는 baseline superiority나 N1 gate evidence가 아니다. 모든
  registered baseline 구현과 validation-only checkpoint freeze가 끝나기
  전 confirmatory job을 금지한다.

## 2026-08-05 · N1 decision falsification is frozen before test

### Research decision

- NeurIPS-25 NOTS가 neural-operator posterior sample로 known output
  functional을 최적화하고 regret bound를 제시하므로 functional operator
  acquisition과 generic regret bound를 novelty에서 제외했다.
- 남긴 질문은 한 사례의 partial physical condition에서 같은 최종 mask로
  가는 posterior route 불일치가 Bayes action과 다음 component의
  value-of-information를 얼마나 바꾸는지다.

### Experiment

- `configs/nonlinear_pde_n1.json`에 data/split/model seed, joint
  full-covariance 2-GMM, lifted rank-96 coordinate operator, mask routes,
  decision loss, 5% minimum effect와 bootstrap decision rule을 동결했다.
- LANO/NOP adaptation, generic probabilistic operator, independent heads,
  ACFlow-style AFA, ACO ceiling, NOTS-style adapted functional acquisition과
  pair-loss/DeltaPhi controls를 모두 보고한다.
- Development는 validation-only다. 다섯 confirmatory checkpoint를
  고정하기 전 test를 생성하지 않으며 N1 pass도 3D protocol 등록만
  허용한다.

### Deployment

- N0r result commit `3c9e165`의 quality와 Pages workflow가 모두 통과했다.
  공개 사이트는 `https://gohyunsu.github.io/aneurysm/`에서 배포됐다.

## 2026-08-05 · Fresh context-stratified N0r passes 9/9

### Result

- N0a outcome 전에 commit `1a68053`에서 동결한 계약을 exact execution
  commit `37d31a8`로 A6000에서 실행했다. Dependency-complete contract
  105/105 tests와 metric job이 모두 exit 0이었다.
- 세 fresh seed의 worst nonlinear departure 0.01933, maximum grid error
  0.00375, minimum worst-component response 0.17484, minimum effective rank
  7.06667, maximum route residual \(8.94\times10^{-8}\)로 9개 check를 모두
  통과했다.
- 공개 aggregate와 raw-metric hash는
  `results/nonlinear_pde_n0r_20260805.json`에 기록했다.

### Decision

- N0는 failed로 보존한다. N0r은 numerical/problem-design adequacy이며
  learned superiority나 method novelty가 아니다.
- N1 learned strong-baseline protocol의 상세 사전등록만 허용한다.
  그 config를 결과 전에 commit하기 전에는 N1 학습을 시작하지 않는다.
- Irregular-3D headline과 AAAI accept-ready 판정은 계속 보류한다.

## 2026-08-05 · Pre-outcome N0r contract is executable

### Experiment

- N0a metric을 보기 전 public commit `1a68053`에서 N0r fresh seed,
  selector, sample count, threshold와 worst-seed rule을 동결했다.
- N0r는 N0와 같은 PDE, BC law, functionals, solver, 8개 scientific
  threshold를 사용한다. 바뀌는 것은 fresh seed와 biased contiguous
  prefix를 명시적 context-stratified selector로 교체하는 것뿐이다.
- Reference 24 case는 24 context를 각각 한 번, paired 48 case는 각각
  두 번 포함한다. N0a outcome은 이 계약을 바꿀 수 없다.

### Scope

- N0r pass는 N1 learned strong-baseline protocol 등록만 허용한다.
  Failed N0 relabel, method novelty, irregular-3D headline은 허용하지 않는다.

## 2026-08-03 · N0a confirms context sensitivity without changing N0

### Result

- Exact `749f596`의 threshold-free A6000 attribution이 24×12 case/seed에서
  완료됐다. Failed seed의 contiguous/stratified/all-case median은
  0.00774/0.01221/0.01828이었다.
- 다른 두 seed의 stratified median은 0.01624/0.01811이었다. 그러나
  former 0.01 reference를 넘는 context median은 seed별 18/24, 19/24,
  18/24로 모든 context가 강한 비선형성을 갖는 것은 아니다.
- 첫 contract 제출은 기존 h5py layer 누락으로 metric 전에 실패했다.
  Layer를 고정한 동일 source 재실행은 97/97 test를 통과했다.

### Decision

- Contiguous single-context statistic이 대표성이 없었다는 가설은
  지지하지만 N0 실패는 그대로다.
- N0r는 새로운 seed, 동일 PDE·threshold, 24 context 각각의 reference
  1개와 paired-response 2개를 결과 전에 고정한다. N0r 전에는 N1/3D를
  실행하지 않는다.

## 2026-08-03 · N0a isolates the contiguous-context sampling hypothesis

### Experiment

- `configs/nonlinear_pde_n0_attribution.json`에 failed N0 result/config
  checksum과 기존 세 seed를 고정했다.
- 각 seed의 24 context × 12 condition 전체에서 semilinear–linear
  departure를 계산하고, 원래 contiguous 12 case, context-stratified
  12 case, 전체 case와 context-median 분포를 비교한다.
- N0a에는 success threshold가 없다. N0를 relabel하거나 N1/3D를
  authorize하거나 N0r threshold·seed를 선택할 수 없다.

## 2026-08-03 · Frozen nonlinear N0 fails one of nine checks

### Result

- Exact `0ead687`의 3-seed A6000 run과 90-test contract가 exit 0으로
  완료됐다. Solver convergence, residual, 33/65-grid error, 8-component
  response, effective rank, functional diversity와 analytic conditioning은
  통과했다.
- Seed별 nonlinear departure 중앙값은 0.02319, 0.02365, 0.00727이었다.
  최악 seed가 frozen 0.01 기준을 넘지 못했으므로 N0는 실패다. Threshold를
  결과 뒤에 낮추거나 2/3 seed 다수결로 바꾸지 않는다.

### Decision

- N1 learned comparison과 irregular-3D headline은 계속 차단한다.
- Post-result code audit에서 context-major로 펼친 case의 앞 12개가 모두
  context 0이고, 앞 48개가 context 0–3뿐임을 확인했다. 이는 N0를
  relabel하는 근거가 아니라 단일-context statistic의 취약성 가설이다.
- 다음 실행은 threshold 없는 all-context N0a attribution이다. 그 결과와
  무관하게 re-entry는 새로운 seed, context-stratified sampling, 같은
  scientific threshold를 별도 사전등록한 N0r로만 가능하다.

## 2026-08-03 · N0 contract failure is corrected before metric access

### Pre-execution amendment

- 첫 dependency-complete PBS contract job은 새 GMM tensor path의 Python
  scalar `.pow` 오류를 검출해 exit 1로 끝났다. N0 scientific metric job은
  제출하지 않았으며 tensor-safe alternating sign으로 교정했다.
- 선언된 \(a_G\in[0.7,1.3]\), \(\lambda_G\in[8,40]\) envelope와 실제
  context mapping을 일치시켰다.
- `right_boundary_flux`는 단순 gradient가 아니라 outward diffusive flux
  \(-a_G\partial_nu\)를 계산한다. Seed, sample count, threshold와 decision
  rule은 바꾸지 않았다.

## 2026-08-03 · Nonlinear N0 is frozen before learning

### Research decision

- Active BC acquisition 자체는 ICML active-feature-acquisition 계보와
  PaPQS/UNED 때문에 novelty가 아니다.
- 남겨 둔 후보는 같은 최종 BC mask에서 conditioning route가 달라질 때
  solution-functional Bayes action과 acquisition ranking에 생기는 regret다.
  TV/KL 기반 bounded-loss risk bound와 N1 strong-baseline evidence가 함께
  있어야만 contribution으로 승격한다.

### Experiment

- 33/65 nested grid의
  \(-\nabla\cdot(a_G\nabla u)+\lambda_Gu^3=f_G\), 네 edge × 두 sine mode의
  8-component BC, context-conditioned 2-GMM을 N0로 동결했다.
- 세 numerical-audit seed에서 solver residual, discretization, nonlinear
  departure, 모든 component response, response effective rank, functional
  winner diversity, analytic direct/sequential conditioning을 모두 검사한다.
- N0 pass는 N1 model/strong-baseline 등록만 허용한다. Learned superiority,
  method novelty, irregular-3D headline은 허용하지 않는다.

## 2026-08-03 · G1s passes every frozen exact-data check

### Result

- Exact `b0e555a`의 fresh 5-seed A6000 run이 exit 0으로 완료됐다.
- 최악 density-only/end-to-end mean은 0.02863/0.02977로 0.05 기준을
  통과했다. Density/sample coverage error는 0.00836/0.01294,
  full-BC operator는 0.00410, projective CI upper는 0.000674,
  analytic nesting residual은 \(7.45\times10^{-9}\)였다.
- Pinned container에서 82개 전체 test와 GitHub quality/Pages가
  같은 source commit으로 통과했다.

### Decision

- G1/G1r 실패는 그대로 보존한다. G1s는 training geometry 768→3,072의
  data adequacy를 확인했으며 method novelty나 baseline superiority가 아니다.
- Nonlinear/3D protocol 등록은 허용한다. 우선순위는 multicomponent
  nonlinear N0/N1과 strong probabilistic/partial-observation baseline이며,
  그 결과 전에는 aneurysm 3D를 headline evidence로 만들지 않는다.

## 2026-08-03 · G1s fresh data-adequacy sanity is preregistered

### Experiment

- G1/G1r/DA1/DA2와 겹치지 않는 다섯 seed, original empirical NLL,
  3,072 geometry × 8 condition을 결과 전에 동결했다.
- G1r의 model, optimizer, validation-only checkpoint selection, mask,
  metric estimator와 모든 threshold를 그대로 유지한다.
- Checkpoint 선택 뒤 생성하는 192-geometry fresh test까지 G1r과 동일하게
  유지해 training geometry 수 외의 실험 차이를 제거했다.

### Scope

- G1s는 estimator innovation이 아니라 data/pipeline adequacy sanity다.
  통과해도 실패한 G1/G1r을 relabel하거나 data scaling을 novelty로
  주장하지 않는다.
- 완전한 5-seed pass 전에는 nonlinear/3D confirmatory 학습을 실행하지
  않는다.

## 2026-08-03 · DA2 finds data adequacy, not a new estimator

### Result

- Exact `18dbfcd`의 24-task A6000 run과 dependency-complete 72-test PBS
  validation이 exit 0으로 완료됐다.
- Formal selection은 grouped shrinkage 0.50이지만 768×8 empirical NLL
  대비 평균 error는 0.05444→0.05431, 0.23%만 개선됐다. 2/3 seed에서
  개선, 1/3에서 악화됐고 population excess NLL은 더 나빴다.
- 3,072×8 control에서는 original empirical NLL이 평균 0.02575, 최악
  0.02706으로 grouped 후보보다 좋았다.

### Decision

- Grouped moment, U-statistic, shrinkage를 method나 novelty로 승격하지
  않는다. Fixed selection 결과와 material scientific verdict를 구분한다.
- 다음 prospective exact sanity는 original empirical NLL과 3,072×8
  data budget만 고정한다. 통과해도 이는 data-adequacy sanity일 뿐
  contribution이 아니다.

## 2026-08-03 · DA2 estimator development contract

### Experiment

- G1/G1r/DA1과 겹치지 않는 세 development seed에서 empirical NLL,
  unbiased grouped moments, covariance shrinkage 0.25/0.50을 비교한다.
- 768×8과 3,072×8 cell에 동일한 5-output Gaussian network, optimizer,
  epoch budget과 sampled-validation NLL checkpoint selection을 적용한다.
- 원래 G1r budget인 768×8의 seed-평균 density-only error로 한 estimator를
  기술적으로 선택하고 analytic population excess NLL을 tie-breaker로
  사용한다. 3,072×8은 data-sufficiency control로만 둔다.

### Scope

- Pairwise-difference U-statistic은 unbiased sample covariance와 같은
  통계량이므로 novelty로 주장하지 않는다.
- DA2에는 success threshold가 없으며 G1/G1r을 relabel하거나 nonlinear/3D
  실행을 허용하지 않는다. 선택 뒤 별도 fresh exact gate를 등록한다.

## 2026-08-03 · DA1 attributes G1r error to finite empirical information

### Result

- Exact public commit `cf675af`의 A6000 run이 30개 task를 3개 diagnostic
  seed에서 정상 완료했다.
- Analytic population NLL은 최악 density-only mean error 0.00495를
  회복했다. 같은 network의 empirical NLL은 population-selected에서
  0.04401, sampled-selected에서 0.04855였다.
- 6,144 record matched comparison의 seed-평균은 192×32 0.05011,
  768×8 0.03612, 3,072×2 0.04715였다. Fixed-axis 비교에서는 geometry와
  반복 condition을 각각 늘릴 때 모두 개선됐다.

### Decision

- Density family/MLP capacity는 주 병목이 아니다. Finite empirical
  condition information과 mean--covariance 결합 추정을 먼저 수정한다.
- 3-seed matched-budget 순위를 보편적 optimum으로 주장하지 않는다.
  G1/G1r은 failed로 유지하며 nonlinear/3D confirmatory 학습을 허용하지
  않는다.
- 다음 후보는 grouped mean regression과 pairwise-difference U-statistic
  covariance target이다. Development-only 선택 뒤 별도 fresh exact-sanity
  protocol을 등록한다.

## 2026-08-03 · Post-G1r density attribution contract

### Experiment

- 실패한 G1r을 재채점하지 않는 post-result diagnostic을 별도 등록했다.
  G1/G1r seed와 겹치지 않는 세 seed만 사용하며 success threshold는 없다.
- Reference 768 geometry × 8 condition에서 true-parameter regression,
  analytic population NLL, empirical NLL을 같은 density network로 비교한다.
  Empirical NLL은 sampled validation과 population validation selection을
  분리해 checkpoint noise도 확인한다.
- 6,144 boundary sample을 고정한 192×32, 768×8, 3,072×2 비교와,
  geometry 또는 condition을 고정한 두 scaling axis를 함께 등록했다.

### Scope

- 이 진단은 representation/optimizer ceiling, finite-condition noise,
  geometry coverage, repeated-condition information만 분리한다.
- 어떤 결과도 G1/G1r을 relabel하거나 nonlinear/3D 학습을 허용하지 않는다.
  결과가 estimator 변경을 시사하면 새 protocol과 fresh seed가 필요하다.
- Main protocol은 이를 threshold 없는 `DA1`로 고정하고, validator가 seed
  수·matched-budget cell·non-relabeling 계약을 강제한다.

## 2026-08-03 · Aneumo physical-scaling audit is velocity-only positive

### Experiment

- Exact public commit `e12ff0a`의 pinned CPU environment에서 52개 전체
  test를 통과한 뒤, 사전등록한 train 20 family/40 case만 분석했다.
  Validation/test 24 case의 field는 읽지 않았다.
- Velocity의 train-tuned global power는 1.075였고 relative-response
  residual median은 0.2112, family-bootstrap CI95는
  `[0.2001, 0.2243]`로 고정 하한 0.15를 통과했다.
- Gauge-invariant pressure의 tuned power는 1.75였고 residual median은
  0.1369, CI95는 `[0.1190, 0.1496]`로 하한을 통과하지 못했다.

### Decision

- Aneumo의 비자명성 근거는 velocity response로만 제한한다. Pressure
  novelty와 full pressure--velocity learning은 제외한다.
- 이는 learned-model 성능이 아니라 future G2 eligibility다. Exact
  G1/G1r 실패가 남아 있으므로 3D confirmatory 학습은 아직 허용하지 않고
  density attribution을 먼저 완료한다.

### Contract and site

- `configs/aurora_v1.json`의 asset snapshot, dataset split unit과
  irregular-3D 출력 계약을 32 base-family cache 및 velocity-only 판정에
  맞췄다.
- `docs/model-spec.md`, aggregate-result index와 첫 화면에 pressure head
  제외, mandatory scaling oracle, learned G2 blocking 조건을 명시했다.

## 2026-08-03 · Aneumo cache integrity and physical-scaling preregistration

### Data

- 전체 multi-terabyte release를 복제하지 않고, 사전등록한 64 case의
  512 internal member만 selective ZIP64 range-read했다.
- Compact HDF5는 32 base family, 64 case, case당 8 condition과 4,096
  node를 포함한다. Family-disjoint split은 train/validation/test
  20/6/6 family, 40/12/12 case이며 모든 field와 coordinate가 finite다.
- Cache SHA-256은
  `9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`다.
  CC BY-NC-ND 원시·compact field는 공개 저장소에 재배포하지 않는다.

### Experiment

- Learned G2보다 먼저 train-family field만 읽는 물리 스케일링 감사를
  등록했다. Validation/test field access는 코드에서 금지한다.
- Same-case anchor oracle에 analytic \(v\propto Q,\ p\propto Q^2\)와
  train-tuned global power law를 적용하고, pressure는 spatial gauge
  offset을 제거한다.
- Base-family bootstrap CI95 lower가 paired-response norm의 0.15 이상
  남는 채널만 learned response의 근거로 허용한다. 두 채널 모두 실패하면
  Aneumo G2 학습을 중단하며 threshold는 결과 뒤에 조정하지 않는다.

## 2026-08-03 · Prospective G1r negative result

### Experiment

- Exact public commit `951ace1`과 사전등록 config checksum을 사용한 5-seed
  A6000 run이 정상 완료됐다. Frozen G1은 relabel하지 않는다.
- Density-only coverage error 0.01605, sampled coverage error 0.01808,
  full-BC operator error 0.00375, projective-excess CI95 upper 0.000202,
  analytic nesting residual \(7.45\times10^{-9}\)는 고정 기준을 통과했다.
- 최악 seed의 density-only standardized mean error 0.07533과 end-to-end
  quadrature mean error 0.07518이 기준 0.05를 넘어 G1r은 실패했다.
  다섯 seed 평균이 약 0.049라는 이유로 worst-seed 판정을 바꾸지 않는다.
- AURORA는 descriptive 15개 seed×mask 셀에서 direct masked Gaussian보다
  mean error와 energy score가 모두 낮았지만, 상대 개선으로 absolute
  gate 실패를 덮지 않는다.

### Decision

- Nonlinear/3D confirmatory 학습은 허용하지 않는다. Oracle-parameter,
  analytic population-NLL, geometry×condition scaling diagnostic으로
  density representation·optimization·finite-data error를 먼저 분리한다.
- AAAI-26 LANO, NeurIPS-25 PaPQS·DeltaPhi, arbitrary-conditioning과
  conditioning-consistency 선행연구를 반영해 analytic conditioning,
  paired residual, active acquisition을 각각 단독 novelty로 주장하지
  않는다. Solution-functional value-of-boundary-information은 아직 audit
  대상 후보이며 확정 contribution이 아니다.

### Site

- Gate, evidence ledger, learn page, result link를 “G1r completed · failed”로
  갱신하고 두 실패 지표와 다음 density diagnostic을 독자가 바로 확인할
  수 있게 한다.

## 2026-08-03 · Prospective exact-G1 re-entry registration

### Experiment

- Frozen G1과 exploratory G1b의 config/result checksum을 pin하고, 기존
  seed와 겹치지 않는 5개 fresh seed를 `controlled_pde_g1r.json`에 실행
  전에 고정했다. Failed G1은 relabel하지 않는다.
- Boundary density는 full-BC NLL로 별도 학습하고 geometry-disjoint
  validation NLL로 checkpoint를 선택한다. Operator와 direct baseline도
  validation split에서만 early stopping하며 test split은 선택 뒤 생성한다.
- Density-only conditional moment·coverage는 exact affine Poisson
  pushforward로, end-to-end mean은 Gauss–Hermite quadrature로 계산한다.
  Projective metric은 raw two-sample distance가 아니라 matched iid floor
  대비 signed excess의 across-seed 95% CI upper bound다.
- Mean 0.05, coverage 0.03, full-BC operator 0.03, projective excess upper
  0.01, analytic nesting residual \(10^{-6}\) threshold를 결과 전에
  machine-readable protocol과 validator에 고정했다.

### Scope

- G1r pass는 새 exact-domain sanity evidence일 뿐 frozen G1 pass, baseline
  superiority, C1 novelty 또는 AAAI readiness를 뜻하지 않는다.
- G1r failure 시 nonlinear/3D confirmatory 학습으로 확장하지 않고 density
  family와 data sufficiency를 다시 분석한다.

### Site

- 공개 gate와 실행 상태 창에 “G1 failed / G1b diagnostic complete / G1r
  preregistered and unrun”을 분리해 표시했다.

## 2026-08-03 · Aneumo selective paired-BC pilot registration

### Data

- 공식 Aneumo ZIP64 release의 중앙 디렉터리를 HTTP byte-range로 감사해
  첫 shard의 40 geometry 각각에 동일 좌표의 8개 steady mass-flow
  condition이 있음을 확인했다.
- Geometry 1의 두 internal NPY member를 실제 range-read해 CRC32,
  `(N,7)=xyz+pressure+velocity`, condition 간 좌표 동일성을 확인했다.
- Upstream `Connection.csv`의 AneuX ancestry를 반영해 synthetic case가
  아니라 32개 base family에서 split하고, family마다 두 deformation만
  선택하는 64-case 파일럿을 학습 결과 전에 등록했다.

### Implementation

- 전체 multi-terabyte release를 받지 않고 필요한 ZIP member만 읽는
  ZIP64 range ingester를 추가했다. Exact `206 Content-Range`, central/local
  record 일치, member CRC, condition 좌표 일치와 compact-cache SHA-256을
  검증한다.
- 8 conditions × 4,096 nodes를 compact HDF5로 기록하되 raw/derived field를
  CC BY-NC-ND 조건 아래 공개 저장소에 재배포하지 않는 계약을 고정했다.
- 이 파일럿은 steady same-geometry response C2와 base-family-disjoint
  irregular-3D 평가만 지원한다. Multicomponent partial-BC C1, transient
  efficiency, clinical utility의 근거로 사용하지 않는다.

### Research

- AAAI-26 LANO, NeurIPS-25 DeltaPhi, 2026 conditioning-operator 선행연구를
  반영해 partial observation, residual pair learning, analytic
  conditioning 자체를 novelty에서 제외했다.
- C2는 DeltaPhi-style residual baseline, pair-loss-zero, random
  cross-geometry pair를 matched data/compute로 모두 이겨야 유지한다.

## 2026-08-03 · Failed-G1 attribution and temporal-contract correction

### Experiment

- `G1b`를 frozen G1 뒤의 명시적 post-result diagnostic으로 구현했다.
  Frozen model·5 seeds·geometry split·500 epoch를 그대로 재학습하고
  \(K=128/512/2048\)에서 iid two-sample floor와 양방향 nested sampling을
  비교한다.
- Exact Poisson의 선형성을 이용해 conditional-mean error를 sampling only,
  BC-density only, operator only, end-to-end로 분해한다. G1b는 새 gate가
  아니며 완료·양수 결과 모두 기존 G1 실패를 재개방하거나 relabel하지 않는다.
- Pinned Singularity 환경에서 G1b tensor test 4개와 축소 end-to-end
  학습→sampling→attribution→aggregation smoke를 통과했다. 전체 suite의
  나머지 오류 2개는 기본 SIF에 BenchAnXplore용 외부 `h5py` layer가 없는
  기존 환경 차이로 분리했다.
- Exact commit `8e24950`의 G1b가 PBS A6000에서 exit 0, walltime 45초로
  완료됐다. \(K=128\) learned direct-vs-nested 0.1006은 iid floor
  0.1013과 같고 analytic moment residual은 \(7.45\times10^{-9}\)였다.
- 그러나 \(K=2048\) missing-mask end-to-end mean error 0.0853 중
  density-only가 0.0754로 남았다. Raw projective metric의 실패는
  설명했지만 learned conditional distribution은 지지되지 않으므로 G1을
  재개방하지 않았다. Coverage attribution도 unresolved로 명시했다.

### Model

- Frozen D0 실패 뒤에도 `configs/aurora_v1.json`과 상세 사이트에 남아 있던
  `temporal_fourier_modes=8` 현행 표시를 제거했다.
- D0b는 17/25 equal coefficient budget의 DCT-II와
  train-geometry-only temporal POD만 geometry-disjoint로 비교한다. 새
  oracle gate와 learned compute-matched 비교 전에는 one-shot temporal
  branch를 선택하지 않는다.
- 5-fold POD covariance fit과 held-out evaluation의 two-pass 실행을
  구현했다. Pinned container에서 DCT orthonormality, span reconstruction,
  held-out covariance exclusion, 4-case synthetic runtime의 9개 검사를
  통과했다.
- Exact commit `1dfc856`의 105-case D0b가 A6000에서 exit 0, walltime
  3분 49초로 완료됐다. DCT-II rank 17/25는 탈락했고 train-only POD
  rank 17/25는 모든 frozen representation threshold를 충족했다.
- POD-17은 full L2 0.00141, bulge L2 0.00880, peak error 0.000764였다.
  POD-25도 통과했지만 아직 selected architecture가 아니며 두 rank를
  learned inner validation 후보로만 둔다.
- D0b의 105 case 전체가 architecture discovery에 쓰였으므로 같은
  BenchAnXplore에서의 learned comparison을 exploratory로 제한했다.
  Confirmatory G3는 fresh transient case 또는 독립 pulsatile dataset에서
  재현하도록 protocol validator에 고정했다.

### Site

- 11장 상세 가이드의 temporal 창을 계획형 Fourier 설명에서 실제 실패
  수치, global-energy 함정, DCT/POD 후보, leakage 방지 규칙으로 교체했다.
- G1b aggregate 결과와 “projective floor 설명 ≠ learned distribution
  성공” 경계를 변경 이력과 실행 상태 창에 추가했다.
- D0b의 DCT/POD별 실제 수치와 “representation eligibility ≠ learned
  superiority” 및 same-benchmark selection leakage 경계를 사이트에
  반영했다.

## 2026-08-03 · Novelty reset: coherent partial-condition operators

### Research

- 추가 red-team에서 2026 conditioning-consistency gap, Neural Operator
  Processes, learned boundary extension, Generalized Neural Operator를 직접
  경쟁 선행연구로 반영했다.
- Partial/missing BC의 ID coherence·calibration, 값이 제공된 full-BC
  support-shift response, hidden-BC law shift의 detection/abstention을
  분리했다. 식별 불가능한 OOD hidden-law coverage 주장을 제거했다.
- ICLR 2026 boundary-indexed operator family, function-space flow/diffusion
  operator, neural-process consistency, PDE OOD-UQ를 직접 경쟁 선행연구로
  추가했다.
- Missing-BC 문제 정의, probabilistic operator, GNN+physics, Fourier
  decoder를 독립 novelty에서 제외했다.
- Primary contribution을 arbitrary observation mask의 nested
  condition–marginal coherence, same-geometry paired simulator response,
  BC-induced/model-induced uncertainty separation으로 재정의했다.
- AURORA의 정식 명칭을 **Aneurysm Uncertainty-aware Reconstruction Operator
  for Reliable Assessment**로 바꿔 현재 근거가 없는 `Risk-aligned` 표현을
  제거했다.

### Protocol

- Exact controlled PDE → nonlinear PDE → irregular 3D의 세-domain 검증을
  AAAI general-method gate로 고정했다.
- CMHA rupture-status diagnostic은 음성 exploratory signal을 반영해
  primary gate에서 secondary analysis로 이동했다.
- One-shot Fourier decoder는 D0 oracle 및 learned compute-matched 비교를
  통과할 때만 남기는 engineering choice로 낮췄다.

### Experiment

- BenchAnXplore D0 attempt 2가 정상 완료됐지만 frozen \(K=8\) gate는
  실패했다. Full relative L2 0.0162, peak error 0.0214, bulge relative
  L2 0.0616이었고, \(K=12\)도 bulge 0.0293으로 기준 0.02를 넘었다.
- Exact controlled G1도 maximum mean error 0.1685, coverage error 0.0377,
  raw projective distance 0.1129로 frozen gate를 실패했다. 다만 direct
  masked Gaussian보다 모든 mask의 mean error와 energy score가 좋고 raw
  projective distance가 모든 seed에서 낮은 상대 신호는 보존했다.
- 두 실패를 confirmatory aggregate artifact로 공개했다. Raw two-sample
  distance의 finite-sample floor와 sampled mean의 density/operator/MC
  error를 분해하는 G1b는 post-result exploratory로만 실행한다.
- BenchAnXplore D0 첫 실행은 30분 32초에 scheduler walltime exit `-29`로
  종료됐다. Aggregate metric이 생성되지 않아 과학적 verdict는
  `unresolved`다.
- 실패 attempt를 공개 aggregate provenance로 남기고, metric·threshold는
  바꾸지 않은 채 walltime 60분과 case-count progress log만 추가했다.
- Exact conditional distribution을 계산할 수 있는 Poisson family의 G1을
  5 seeds로 사전 등록했다. Joint Gaussian BC density, arbitrary-mask
  analytic conditioning, shared solution operator, paired-response loss와
  direct masked Gaussian baseline을 구현했다.
- Pinned experiment container에서 2-epoch CPU runtime smoke를 완료해
  tensor shape, conditioning, sampling, metric serialization을 검증했다.
- 첫 G1 submission은 GPU 실행 전 `Q` 상태에서 2,000회 geometry-bootstrap
  CI가 result JSON에 빠지는 것을 발견해 취소했다. Point estimate를 본 뒤
  고치는 일을 피하기 위한 pre-run correction이다.
- Geometry-family cluster bootstrap과 95% CI 직렬화를 구현하고 pinned
  container smoke에서 `geometry_bootstrap_ci95` 생성을 확인했다.

### Site

- 메인 페이지와 11장 field guide의 architecture, gate, contribution,
  glossary를 v2 연구 질문으로 동기화했다.
- Full·partial·missing 모드가 하나의 joint BC density를 공유하는 과정과
  paired response·두 uncertainty 축을 배경지식 없이 읽을 수 있게 설명했다.

## 2026-08-03 · BenchAnXplore D0 preregistration

### Data

- Aneumo의 현재 서버 자산이 전체 release가 아니라 geometry 1개 × steady
  BC 2개 sample임을 확인해 full G2를 blocked로 표시했다.
- BenchAnXplore archive의 105 HDF5 + 105 XDMF, 80 velocity timestep,
  checksum을 확인하고 `junjinyong`의 read-only input cache를 준비했다.

### Experiment

- one-shot 모델 학습 전 Fourier 4/8/12-mode 표현 손실을 판정하는 D0
  audit과 `K=8` 성공 threshold를 결과 확인 전에 등록했다.
- pinned container는 수정하지 않고 `h5py==3.12.1` 외부 dependency layer를
  사용하도록 PBS template과 aggregate-only result contract를 추가했다.

## 2026-08-03 · Asset audit, G1 diagnostic, and field guide

### Experiment

- `introai9`에서 Aneumo, AneuG-Flow, BenchAnXplore, CMHA, AneuX,
  Aneurisk 자산을 읽기 전용으로 확인했다.
- `junjinyong`의 PBS A6000 allocation에서 pinned PyTorch/CUDA smoke와 CMHA
  G1 exploratory sensitivity를 실행했다.
- 99 patient/105 lesion을 patient-grouped 5×5 split으로 평가한 결과
  `clinical+morphology` AUPRC 0.759, `+real-CFD summary` 0.717,
  `Δ=-0.0419 [−0.1083, 0.0066]`이었다.
- 공식 case map과 second model family 전까지 confirmatory G1은
  `unresolved`다. C3를 conditional secondary로 낮추고 C1/C2를 우선한다.
- 정의가 확인되지 않고 target을 거의 분리한 `PHASE`, `ELAPSS`를
  baseline에서 제외했다.

### Implementation

- patient-grouped nested-CV linear pilot, patient bootstrap, CUDA smoke, PBS
  template과 aggregate result contract를 추가했다.
- grouped splitter의 empty-fold 오류를 unit/data smoke로 발견·수정했고 실패
  run도 provenance로 보존했다.
- 공개 aggregate result:
  `results/cmha_g1_exploratory_20260803.json`

### Site

- 한 장 요약을 유지하면서, 배경지식이 없는 독자를 위한 11개 상세 설명 창과
  16개 용어 glossary를 `site/learn.html`에 추가했다.
- 메인 architecture에 “GNN local encoder + attention + neural-operator
  decoder” 분류와 각 모듈의 상세 링크를 추가했다.
- G1의 음수 exploratory evidence와 conditional C3 결정을 gate·실험·변경
  이력에 반영했다.

### Deployment

- content commit: `c9a998b`
- GitHub quality workflow: success
- GitHub Pages workflow: success
- production verification: main, 11-chapter guide, aggregate result JSON all
  returned HTTP 200
- production guide:
  `https://gohyunsu.github.io/aneurysm/site/learn.html`

## 2026-08-03 · Research reset: AURORA

### Changed

- 기존 “In-PI-MGN + attention/masking/multigrid” 중심 개선안을 primary
  method에서 제외했다.
- geometry-only 입력에서 boundary condition이 관측되지 않는 문제를
  deterministic regression이 아닌 conditional field distribution으로
  재정의했다.
- autoregressive velocity rollout 대신 cardiac cycle의 temporal basis를
  one-shot으로 예측하는 dual-domain operator를 제안했다.
- real-CFD field fidelity와 downstream rupture-status functional
  sufficiency를 분리해 함께 평가하도록 설계했다.
- cross-sectional rupture status와 prospective rupture risk를 명시적으로
  분리했다.

### Added

- 연구 방향, 선행연구 계보, 모델 명세, 사전 실험 프로토콜 문서
- machine-readable `configs/aurora_v1.json`과 validation CLI
- 연구 가설·gate·변경 이력을 탐색할 수 있는 단일 프로젝트 사이트
- protocol test, local link/anchor audit, JavaScript syntax를 검사하는 GitHub
  Actions quality gate
- 팀 대화 반영, 보안, 사이트 동기화 규칙을 담은 `AGENTS.md`
- 원고, claim matrix, planned result table을 공개 코드와 분리하는 private
  `gohyunsu/aneurysm-paper` 저장소

### Rationale

2026년 직접 경쟁 연구가 inflow-aware GNN, graph transformer, masked
pretraining, physics-informed multimodal fusion을 이미 제안했다. 단순 구조
추가는 novelty가 약하고, 현재 surrogate는 deployment 때 필요한 초기
velocity/inflow를 가정한다. AURORA는 그 가정 자체를 연구 문제로 삼는다.

### Evidence status

- 문헌·설계: reviewed as of 2026-08-03
- AURORA implementation: protocol and architecture specification
- AURORA experiments: not started
- clinical validation: not performed
