# AGENTS.md — AURORA 연구 운영 규약

## 2026-08-25 pragmatic execution policy

- Repairs, retries, checkpoint resumes and justified host/queue/server
  migration are normal operational tools. Preserve every attempt and avoid
  counting duplicate scientific evidence, but do not use historical oracle
  order, server pins or failed commands as unrelated experiment gates.
- Independent development cells may run concurrently when capacity permits.
  Retain the validity boundaries: fixed splits, train-only preprocessing,
  validation-only selection, locked-test isolation, case-level evaluation and
  exact code/config/data/result provenance.
- Both comparator PBS templates explicitly request the queue's Singularity
  capability. Host pinning remains an incident-specific qsub override rather
  than a permanent source constraint.
- The Transolver config now states `prepared_validation_development`; the
  obsolete oracle/GHD-terminal status string is removed. Execution still
  requires its own exact activation and normal scientific safeguards, not
  another comparator's outcome.
- Either `introai9/coss_a6gpu` or `junjinyong/ssu_a6gpu` may be used when an
  activation records the actual server. Public-site work is out of scope and
  credentials must never enter the repository.

## 2026-08-24 post-staging queue and storage audit

- Introai9 response oracle `118479.ECE-util1` remains unheld `Q` and
  scientifically unstarted on full, hook-clean host7. Host8 still has two
  nominally free GPUs and the cgroup-cleanup warning; a data-free CUDA smoke
  must precede any relocated scientific execution there.
- Junjinyong's staged 42,866,553,272-byte payload remains intact and its queue
  is empty. Shared `/home` had approximately 29.3 GB free at 20:54 KST.
  `/SHARE_ST` had 979,930,972,160 bytes free, but no authorized AURORA-owned
  namespace was found. Do not infer storage authority from the permissive mode
  of `/SHARE_ST/acs`.
- The maximum response-basis artifact is approximately 3.43 GB and uses an
  atomic temporary write. This is smaller than current free space but does not
  eliminate shared-home exhaustion risk. No smoke artifact, relocation
  activation, GPU job, field read, basis or result was created in this audit.

## 2026-08-24 relocation staging terminal; host8 smoke awaits exact transfer authority

- Approved GPU-0 staging job `118499.ECE-util1` is terminal `F/exit 0`,
  stage-out 0, run count one in 00:22:58. The exact 42,866,553,272-byte payload
  passed destination SHA checks and atomic install, left no partial and decoded
  no field array or sealed case.
- Introai9 oracle `118479` remains queued and scientifically unstarted on
  fully occupied hook-clean host7. Host8 still exposes two nominal free GPUs
  but retains its cgroup-cleanup warning. Junjinyong has no PBS job/result and
  shared `/home` free space is approximately 33.1 GB; recheck it before any
  scientific output allocation.
- Private integrity-passed head `4153745...` prepares a data-free host8 CUDA
  smoke, but its 2,267-byte script and 1,477-byte private manifest were not
  transferred because they were outside the exact staging approval. Do not
  submit an inline or indirect replacement. The exact two-file transfer and
  one-time smoke qsub require explicit user approval.

## 2026-08-24 shared-A6000 relocation safety recheck

- Introai9 oracle `118479.ECE-util1` remains unheld `Q` on the hard
  hook-clean-host7 contract with no run root or scientific execution.
  Junjinyong's authorized queue `ssu_a6gpu` uses the same A6000 node pool.
- Host7 is hook-clean but 4/4 occupied. Host8 has two nominally free GPUs but
  retains the cgroup-cleanup warning that caused 15 pre-script rejections and
  terminal `F/-18` for this exact oracle; the other A6000 nodes are full,
  down/offline or warning-marked. Do not treat account relocation as an
  independent capacity source or submit the current unconstrained wrapper.
- The exact public checkout, container and focused tests on junjinyong remain
  ready, but no data has been staged. Cross-account transfer of the exact
  42,866,553,272-byte private payload still requires explicit approval of its
  scope and destination. After approval, GPU submission additionally requires
  hook-clean capacity and proof that the introai9 oracle has not begun, so the
  same scientific execution can never run twice.

## 2026-08-24 conditional junjinyong execution relocation

- The user explicitly superseded the earlier absolute `junjinyong` ban while
  introai9 oracle `118479.ECE-util1` remains queued for host7 capacity. The
  introai9 job stays untouched during relocation preparation; never submit an
  unversioned or scientifically different duplicate.
- `junjinyong` public-key login is healthy, its PBS user queue is empty and it
  belongs to the `ssu` rather than `introai` group. Use `ssu_a6gpu` with
  `Qlist=a6000`; do not claim access to `coss_a6gpu`. The shared `/home`
  filesystem has approximately 183 GB available but is reported 100% used, so
  stage only the exact 33.23 GB transient and 9.63 GB normalizer assets and
  preserve checksums.
- The original oracle config, implementation, activation, split, audit, ranks,
  metrics and sealed scope remain fixed at scientific public commit
  `1c5039292d60e9dcbb722318e43bacc66de1ad36`. A separate public execution
  overlay and fresh private activation may change only account, queue, host
  constraint and owner-readable paths. It remains a development-only oracle,
  not learned performance or a paper claim.
- Use a fresh exact checkout and isolated data/private/output roots under the
  `junjinyong` account. Do not reuse historical AURORA directories, disturb
  unrelated work, run GPU code on the login node, or maintain the public site.

> **2026-08-24 fresh five-seed executor closure:** The active manuscript's
> twenty-cell confirmation is now executable rather than analysis-only. The
> common matched runner accepts only seeds `20260901`--`20260905` for T/T+S
> confirmation, keeps seed 1103 for single-seed development/T+M and rejects
> T+M at fresh seeds. Every activation, checkpoint, best checkpoint, result
> and scientific provenance records the exact seed and stage; cross-seed
> resume is rejected. A fresh-seed activation also binds the exact multiseed
> config and a completed sealed single-seed 2x2 result before data loading.
> The training-protocol digest deliberately excludes the separately reported
> seed but remains exact for every other training field. The analyzer requires
> the same selected family/objective/rank and protocol within role across all
> five seeds and the confirmation stage on every cell. This sets no favorable-
> seed threshold, winner, test authorization or paper claim. All 51 related
> regressions and the full 1,032-test local suite pass with PBS syntax. This
> creates no activation, job or result. Locked test/79
> extras remain sealed; use only introai9, never junjinyong, and do not
> maintain the site.

> **2026-08-24 bounded T+M attribution readiness:** Omitting the processed
> steady cohort is not the active plan, but steady supervision cannot be
> credited for effects caused only by adding a shared head and a second model
> pass. The common matched runner now also supports `control_TM` and
> `proposal_TM`: each uses the exact T+S single-field head and coefficient,
> predicts the same train case's 80-phase mean WSS on a second geometry pass,
> derives its output scale from the exact cycle-mean targets over only the 584
> frozen train fields and reads zero steady WSS rows. The paired sidecar
> contrasts T+S with T+M for each role
> on the same 73 validation cases. It is single-seed development attribution,
> not a replacement for the primary T/T+S factorial, a fully compute-matched
> control, a causal steady-label effect, novelty or a paper result. Storage
> I/O and target information remain deliberately unmatched and must be stated.
> It cannot block the primary factorial, but steady-specific interpretation in
> the manuscript requires it. All 34 related regressions pass; the full local
> suite passes 1,031/1,031. This
> creates no activation, job, result or claim. Locked test/79 extras remain
> sealed; use only introai9, never junjinyong, and do not maintain the site.

> **2026-08-24 matched T/T+S trainer readiness:** The steady cohort is no
> longer only a downstream analysis promise. A common activation-bound runner
> now supports the selected GHD--GPS/Transolver control and response/local
> proposal as transient-only and eligible-steady cells. T+S pairs exactly one
> scheduled steady row with each of 584 transient cases per epoch, uses a
> separate shared-encoder single-field head, never replicates a field over 80
> phases and records exact exposure count/prefix. The same ordered 13,985 rows
> and schedule serve both roles; T freezes the head. Steady RMS parameterizes
> physical head output and is not a loss weight; primary inference remains
> within-information method comparison, not steady-use novelty. Selection,
> all development evidence, scale result, split/audit/overlap and response
> basis are hash-bound before data loading. Exact-state resume recomputes the
> exposure prefix. Twelve focused and 46 related tests pass with PBS syntax;
> the full local suite passes 1,023/1,023.
> This selects no model, creates no activation/job/result/claim and cannot run
> before all predecessors terminal. Locked test/79 extras remain sealed; use
> only introai9, never junjinyong, and do not maintain the site.

> **2026-08-24 response/local candidate runner readiness:** The active
> release-730 candidate is now executable as five activation-bound,
> single-seed validation cells: response-only/combined field training followed
> by field-only/scalarized/field-anchored fine-tunes from the exact same
> combined checkpoint. It uses one shared GHD--GPS encoder, a train-only
> response basis, a phase-specific local field and a nodewise phase-shared
> gate. Inactive local or steady heads are frozen and active parameter count is
> reported. Report-only basis leakage is skipped during training/intermediate
> validation, and the shared loader releases the 9.6-GB steady object before
> opening the 33.2-GB transient object. Basis, oracle, GHD--GPS and Transolver
> terminal hashes are checked
> before data loading; exact-state continuation requires a preserved failed
> terminal plus checkpoint. Eight candidate tests and 37 related regressions
> pass. This T-only runner is architecture/objective attribution, not a reason
> to omit steady supervision: the final selected control and proposal still
> require matched T/T+S comparison over the same ordered 13,985 eligible steady
> rows. No rank, activation, job, result or paper claim exists; locked test/79
> extras remain sealed, use only introai9, never junjinyong, and do not maintain
> the site.

> **2026-08-24 response/local spatial-gate correction:** The active shared
> candidate no longer uses one pooled scalar residual gate. It predicts a
> nodewise, phase-shared gate from the same GHD-conditioned surface features,
> while the residual remains phase-specific. This makes the claimed local
> correction executable without adding a second temporal head. Tests must
> prove the gate receives gradients only in the combined row and is skipped in
> response-only/local-only/steady-head paths. This selects no rank or method,
> creates no job/result/novelty claim and does not change the oracle ->
> GHD--GPS -> Transolver order, sealed test/79 extras, introai9-only execution,
> never-junjinyong rule or no-site scope.

> **2026-08-24 functional-fidelity direct-prior correction:** Primary-source
> inspection of Garnier et al. `arXiv:2512.09013v1` shows a distinct 51M sparse
> graph-Transformer aneurysm study, not a bibliographic substitute for the
> peer-reviewed Lannelongue et al. MeshGraphNet study. It autoregressively
> derives WSS/TAWSS/OSI, explicitly reports lower OSI accuracy from near-wall
> directional fluctuations under an overall-flow objective and names
> shear-metric multi-task supervision as future work. Kheiri et al.
> `10.1016/j.cjph.2026.04.015` also already combines POD with Transformer/LSTM
> for pulsatile cerebral-aneurysm hemodynamics in six dilation cases.
> Therefore neither the domain failure observation, a functional loss, POD nor
> reduced-order temporal prediction is standalone AURORA novelty. The active
> conditional contribution remains matched same-field field/TAWSS/OSI evidence
> from the response/local candidate against strong T and T+S controls. Add no
> comparator or GPU job from this audit; preserve oracle `118376.ECE-util1` ->
> GHD--GPS -> Transolver, sealed test/79 extras, introai9-only execution, never
> junjinyong and no site maintenance.

> **2026-08-24 current-facing README synchronization:** The repository entry
> point now describes the active release-730 joint field/functional-fidelity
> study instead of the superseded inactive reference-relative/worldline
> direction. It exposes the 584/73/73 split, sealed 73-test/79-extra scope,
> matched 13,985-row T/T+S factor, direct comparators and queued response
> oracle without publishing private identifiers or results. `check_site.py`
> now enforces these current markers and rejects the obsolete paper identity.
> This is documentation/quality-contract synchronization only; no site asset,
> scientific byte, split, model, rank, execution or claim changed. Continue
> oracle `118376.ECE-util1` without duplication, use only introai9, never
> junjinyong, and do not maintain the public site.

> **2026-08-24 candidate checkpoint-storage correction:** The dormant
> response/local candidate previously registered the immutable oracle response
> mean, selected basis, reference weights and amplitude center as persistent
> buffers. A rank-256 basis is about 3.18 GiB and would therefore be copied
> into every periodic optimizer checkpoint. These fixed tensors now remain
> device-moving buffers but are absent from `state_dict`; a future runner must
> hash-bind and load the separate oracle basis artifact before restoring
> trainable state. Dataset-free regression verifies both properties. This
> changes no field, rank, model selection, data, result or execution authority.
> Exact source head `96bb0a91df03ff571a028e657ea1717c3de5ada8`
> passed 1,001 local tests and Research Quality `32685594119`; 42 focused
> candidate/functional/comparator tests also passed.
> Oracle `118376.ECE-util1` remains first; use only introai9, never junjinyong,
> and do not maintain the public site.

> **2026-08-24 comparator exact-state continuation closure:** The pending
> GHD--GPS and Transolver jobs can now survive a genuine scheduler/walltime
> interruption without restarting or changing science. Version-2 checkpoints
> preserve current/best model state, optimizer, scheduler, patience counter,
> full history, smoke record, accumulated time and Python/Torch/CUDA RNG.
> Continuation requires a fresh activation plus the actual read-only prior
> attempt terminal record and checkpoint; both hashes are recomputed before
> restore. Only nonzero-exit/noncomplete attempts qualify, completed runs are
> rejected, and the continuation writes a new run root. Model, seed, data,
> objective, epoch rule and sealed scope are unchanged. No activation, job,
> result or claim exists; oracle `118376.ECE-util1` remains first. Use only
> introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 comparator walltime-envelope correction:** Read-only PBS
> evidence shows completed Graph U-Net `117056.ECE-util1` used 28:41:19 for
> 25,050 optimizer steps under a 72-hour request. GHD--GPS requires 23,360
> steps even at its 80-epoch minimum, yet requested 12 hours; Transolver used
> the same minimum but requested 24 hours. Both pending comparators now request
> the enabled `coss_a6gpu` queue's 72-hour default. Model, seed, loss, epoch
> ceiling/minimum, patience, validation cadence and checkpoint rule are
> unchanged; actual GPU-hours remain the reported cost. This creates no
> activation, job, result or claim. Oracle `118376.ECE-util1` remains first;
> use only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 candidate residual-overlap objective closure:** The dormant
> candidate described response-basis overlap as a soft complementarity penalty
> even though the bounded R1/R2 rows register no such loss weight or ablation.
> It is now an explicitly detached, reported diagnostic and cannot silently
> enter optimization. Field decoding, gate behavior and every active field/
> functional gradient remain unchanged; registered branch ablations provide
> the mechanism evidence. This removes an unbudgeted regularizer before any
> candidate execution and selects no rank, backbone, loss, data, result or
> claim. Response oracle `118376.ECE-util1` remains first; use only introai9,
> never junjinyong, and do not maintain the public site.

> **2026-08-24 candidate anchored-gradient inactive-head correction:** A
> dataset-free reproduction showed that the planned complete field-anchored
> objective would fail before an optimizer step because
> `SharedEncoderCycleResponseResidual` registers the common T+M/T+S
> single-field head although cycle forward does not use it. Anchored backward
> now excludes only parameter tensors unused by both field and functional
> objectives and fails on asymmetric dependencies. Minimal and exact shared-
> candidate regressions verify finite active-cycle gradients and `grad=None`
> on the inactive auxiliary head. This changes no active gradient, objective,
> model, rank, data, result or execution authority. Response oracle
> `118376.ECE-util1` remains first; use only introai9, never junjinyong, and do
> not maintain the public site.

> **2026-08-24 Transolver serial-predecessor enforcement:** The pending
> Transolver comparator now requires fresh activation hashes for the preserved
> Graph U-Net, response-oracle and GHD--GPS terminal records. Its CLI/PBS
> runner recomputes the oracle/GHD record hashes before any data load. This
> aligns executable code with the already fixed oracle -> GHD--GPS ->
> Transolver order; a future evidence-based reprioritization requires a
> separately versioned contract. Older Transolver activations are superseded.
> No model, split, target, optimizer, result or sealed scope changed. Oracle
> `118376.ECE-util1` remains first; use only introai9, never junjinyong, and do
> not maintain the public site.

> **2026-08-24 GHD--GPS serial-predecessor enforcement:** The pending strong
> comparator now requires a fresh activation containing valid Graph U-Net and
> response-oracle terminal-record SHA-256 values. Its CLI/PBS runner binds the
> actual oracle terminal record read-only and recomputes that hash before any
> data load. This closes the gap between the documented oracle-first priority
> and executable code; all older GHD--GPS activations are superseded. No model,
> split, target, optimizer, result or sealed scope changed. Job
> `118376.ECE-util1` remains first; use only introai9, never junjinyong, and do
> not maintain the public site.

> **2026-08-24 five-seed matched-information confirmation:** The single-seed
> T/T+S factorial remains development attribution, not headline evidence. Once
> validation selects the strongest control and candidate, twenty terminal
> validation cells must cover the full factorial at prospectively fixed fresh
> seeds `20260901`--`20260905`. The new analyzer reports per-seed effects,
> favorable-sign counts and a crossed seed/case bootstrap, but fixes no
> favorable-seed threshold, winner, novelty conclusion or automatic test
> authorization. It rejects seed/protocol drift and all test/79-extra access.
> The locked test remains one later batched scope event after all five
> checkpoints and analysis rules are frozen. Response oracle remains first;
> use only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 matched steady stream provenance closure:** The lazy T+S stream
> now validates unique archive case names plus both exact eligible-index and
> ordered index-to-case-name digests before any steady WSS row can be indexed.
> A negative synthetic order-drift test fails with zero tensor/GHD reads. This
> is metadata-only implementation hardening; scope remains 13,985 rows, the
> exposure schedule/model/result are unchanged, oracle remains first, and
> test/79 extras stay sealed. Use only introai9, never junjinyong.

> **2026-08-24 confirmatory renderer readiness:** The active release-730
> figure protocol now fixes a loader-free renderer before T0: a
> 7.1-by-1.85-inch two-column layout matching the manuscript's
> `0.235\textheight` slot, three reference-OSI case groups, TAWSS/OSI rows,
> reference/control/proposal columns and one signed 80-phase trace per case.
> The orthographic camera is numerically fixed at azimuth -60/elevation 20;
> TAWSS limits, the common three-case trace y-axis and trace direction come only
> from selected references, while OSI remains [0,0.5]. The code has no loader,
> checkpoint reader, CLI or identifier
> path. Synthetic rendering selects no case/model and does not authorize T0;
> actual test rendering still requires frozen C0 and private activation. Use
> only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 candidate shared-encoder correction:** Static inspection found
> that the dormant response-residual wrapper used a separate GHD-only MLP for
> the global branch while the local branch owned an independent mesh encoder.
> That would confound the planned response/local ablation and contradict the
> manuscript's shared-encoder description. The active candidate interface is
> now `SharedEncoderCycleResponseResidual`: one GHD-conditioned geometry
> encoder produces per-node features, their area-weighted pool drives the
> response coefficients/amplitude/gate, and the same features drive the local
> cycle decoder. Response-only skips only the local decoder; local-only skips
> only the response head. T+M and T+S reuse the exact common single-field head
> class. This pre-result correction selects no backbone, rank, loss or run and
> does not invalidate queued response-oracle job `118376.ECE-util1`, which is
> bound to its earlier exact oracle-only source. Keep test/79 extras sealed,
> use only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 validation-row provenance correction:** A read-only
> recomputation from the exact private split manifest showed that the actual
> stored validation loader order has SHA-256 `aac001b3...d4dc30`; the earlier
> manually registered `cceb0e47...5a24` value was not producer-derived and is
> superseded before any response-oracle or matched-information result exists.
> Every future producer now recomputes and emits the exact ordered digest; the
> completed legacy Graph U-Net result is bound to an identifier-free private
> sidecar rather than modified or rerun. The held pre-script oracle job
> `118333.ECE-util1` points to superseded bytes and must not be released. After
> public Quality and a fresh private activation, cancel that unstarted job and
> submit one corrected replacement only on confirmed hook-clean A6000
> capacity. Keep locked test/79 extras sealed, use only introai9, never
> junjinyong, and do not maintain the public site.

> **2026-08-24 functional-kernel correction:** The dataset-free OSI term now
> uses the standard pseudo-Huber outer factor `delta^2`, not `delta`. No active
> release-730 functional job or result existed, and train-initial term scaling
> would have absorbed the missing constant, but the definition is corrected
> before execution. The public planned objective rows now match private R2:
> field-only, complete scalarized and complete field-anchored. Isolated
> functional rows are omitted for the higher-value matched control/proposal
> T+M reviewer controls; all four kernel terms remain separately reported.
> This selects no weight/model and grants no execution authority. Response
> oracle remains first; use only introai9, never junjinyong, and do not maintain
> the public site. Thirteen focused tests and the full 970-test suite pass.

> **2026-08-24 release-730 figure-scope correction:** The historical
> prediction-blind figure selector remains fixed to v4's 51-case outer split.
> The active paper must use the new release-730 selector over exactly 73 locked
> test references, after frozen C0 checkpoints and a private T0 activation.
> It selects 10/50/90% area-weighted reference-OSI cases and a reference-only
> 90% OSI trace vertex; model values cannot affect cases, camera, masks or
> colour limits. This code opens no test/extra scope, performs no rendering and
> creates no claim. Use only introai9, never junjinyong, and do not maintain
> the public site.

> **2026-08-24 deterministic oracle-rank nomination:** Before response-oracle
> values are observed, the release-730 comparison fixes at most three learned
> R1 candidates as the minimum, lower-median and maximum positive ranks on the
> storage-aware oracle Pareto front. Rank zero remains a reported mean-response
> control. This is candidate nomination only, not final rank selection or a
> global-branch decision; every rank, paired interval and Pareto set remains
> reported. It creates no threshold, activation, result or execution authority.
> Response oracle remains first; use only introai9, never junjinyong, and do
> not maintain the public site.

> **2026-08-24 shared single-field auxiliary interface:** Release-730
> GHD--GPS and Transolver now expose output-equivalent `encode_geometry` and
> `decode_cycle` paths while preserving parameter names and the exact pending
> comparator checkouts. Future T+M and T+S development must attach the same
> `SharedEncoderSingleFieldAdapter` within a model role. T+M derives a
> train-only cycle-mean vector target; T+S adapts exactly one lazy steady row.
> Both targets use explicit positive train-only scaling and a `nodes x 3`
> head, never an 80-phase clone. This selects no backbone, loss weight,
> activation or run; response oracle remains first, use only introai9, never
> junjinyong, and do not maintain the public site.

> **2026-08-24 matched steady streaming boundary:** Future T+S cells must use
> `MatchedSteadyStream` (or a byte-equivalent reviewed successor) so the
> 9.63-GB mmap archive is never advanced-indexed into a 13,985-row eager copy.
> Construction is metadata-only; each training exposure decodes exactly one
> eligible row, and ineligible indices fail before tensor access. Epoch order
> and the incremental terminal digest reproduce the registered matched
> schedule. The dedicated steady objective is a single-field area-weighted
> relative error, never an 80-phase replication. This selects no model, loss
> weight, rank, activation or execution; response oracle remains first, use
> only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 candidate branch-unit correction:** The response basis is in
> raw physical WSS coordinates, while registered comparator backbones emit a
> train-RMS-normalized field and apply physical scaling in their evaluators.
> The dormant wrapper now requires an explicit finite positive local-output
> scale and converts before combined or local-only routing. No scale is
> selected, no result is read and no execution is authorized. Response oracle
> remains first; use only introai9, never junjinyong, and do not maintain the
> public site.

> **2026-08-24 candidate/comparator interface correction:** The dormant
> response-residual wrapper now accepts the tensor output used by both
> registered release-730 GHD--GPS and Transolver comparators as well as the
> mapping output used by auxiliary backbones. This corrects a pre-execution
> smoke failure without changing the branch equation, rank, model selection,
> loss, data scope or execution authority. Response oracle remains first; use
> only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 oracle paired-order provenance correction:** The result-pending
> release-730 oracle comparison now distinguishes the 73-case set digest from
> the ordered-loader digest required by paired resampling. A fresh private
> activation must bind both direct/oracle result hashes, both terminal-record
> hashes, the exact split manifest and the ordered validation digest before the
> comparison can run. This changes no producer, metric, result, rank decision,
> execution order or sealed scope. The held response oracle remains first; use
> only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-24 response-prototype representation correction:** The dormant
> dataset-free response+residual prototype now accepts only the release-730
> oracle basis schema and applies its mean-plus-basis reconstruction exactly.
> Historical v4 schema use, hidden pattern renormalization and hard tangent
> projection were removed. Both branches and the final output remain in the
> common raw physical Cartesian target space; normals are inputs/diagnostics,
> not a target transformation. This selects no rank/backbone/loss, reads no
> field, opens no GPU/test/extra scope and creates no paper claim. Response
> oracle remains first; use only introai9 and never junjinyong.

> **2026-08-24 response-oracle pre-script system hold:** PBS recovered and
> exact response-oracle job `118333.ECE-util1` was submitted once after an
> empty-queue and exact-input preflight. PBS attempted to dispatch that one job
> 21 times to `ece-a6gpu8`, then system-held it with exit status `-18`; the node
> still reports `Hook pbs_cgroups: Unable to clean up one or more cgroups`.
> No run root, attempt marker, stdout, stderr, scientific tensor read or CUDA
> process exists, and PBS run count is not qsub count. Do not duplicate-submit
> or change scientific bytes. Release this same held job only after the cgroup
> hook clears or healthy A6000 capacity is confirmed. The serial priority is
> response oracle, GHD-GPS, then Transolver. Keep locked test/79 extras sealed,
> use only introai9, never junjinyong, and do not maintain the public site.

> **2026-08-21 matched-information compute interpretation:** The four-cell
> analyzer now fail-closes on terminal optimizer steps, transient case-cycle
> exposures,
> GPU seconds, peak memory, active parameters, seed, same within-role base
> training-protocol digest and T+S scale-audit provenance. Because T+S adds
> steady-head forward/backward work and no transient-replay compute control is
> registered, its within-model contrast is the registered augmentation
> protocol effect, never a causal steady-label-only effect. Primary method
> comparisons remain within T and within T+S. This creates no result, model,
> test/extra read or GPU authority; response oracle remains first after PBS
> recovery, use only introai9 and never junjinyong.

> **2026-08-21 eligible-steady scale-audit preparation:** A CPU-only audit now
> prepares the one missing normalization fact for later T+S training: physical
> vector RMS over exactly the leakage-audited 13,985 steady rows, compared with
> the frozen 584-train transient aggregate. It reports component moments,
> case-RMS quantiles and scale ratios but has no threshold, automatic loss
> weight, model or claim. It reads no transient WSS, validation, test or extra
> field and uses GPU 0. Execution requires a fresh private activation and a
> preserved response-oracle terminal record; do not submit it first. PBS is
> still unavailable, response oracle remains first, use only introai9 and never
> junjinyong.

> **2026-08-21 matched steady exposure schedule:** A metadata-only schedule now
> binds the private ordered 13,985-row manifest and gives the selected control
> and proposal the same SHA-256-ranked no-replacement-cycle rule. Each transient
> epoch pairs 584 steady examples; all eligible rows receive 3--4 visits by the
> 80-epoch minimum and 10--11 by the 251-epoch ceiling. Terminal T+S cells must
> report actual epoch, exposure count and prefix digest. This fixes ordering and
> repetition fairness but selects no backbone, loss weight, optimizer or
> checkpoint and reads no WSS. A later selected model must use a shared geometry
> encoder plus separate single-field steady head, never an 80-phase copy. No GPU
> or paper claim is authorized; response oracle remains first after PBS
> recovery, test/79 extras stay sealed, use only introai9 and never junjinyong.

> **2026-08-21 direct-prior metadata and novelty correction:** The current
> arXiv v2 title of Sheng et al. 2601.19876 is *Real-Time Pulsatile Flow
> Prediction for Realistic, Diverse Intracranial Aneurysm Morphologies using a
> Graph Transformer and Steady-Flow Data Augmentation*; the current metadata
> and HTML do not use `RHSIA`. Use the exact title and `Sheng et al.` in the
> active manuscript. Historical internal `RHSIA-style` labels may remain only
> as implementation provenance. Direct v2 inspection confirms 808 reported
> pulsatile cases, mixed steady/transient sampling, a complete-sequence
> surrogate, a separately predicted steady-WSS FiLM prior and a 512-mode modal
> surrogate. These occupy steady augmentation, sequence decoding, modal
> prediction and steady-anchor claims; none is AURORA novelty. Keep the
> official 730 release intersection distinct from the reported 808 cohort and
> the exact processed object's 809 rows. This changes no split, model, result
> or execution authority. Response oracle remains first after PBS recovery;
> test/79 extras remain sealed and junjinyong remains excluded.

> **2026-08-21 matched-information factorial analyzer preparation:** Public
> code now defines a result-pending 2x2 analysis crossing selected
> control/proposal with transient-only/the identical 13,985 eligible steady
> rows. It reports paired method effects, steady effects and their
> difference-in-differences for field, mean-vector, TAWSS, OSI and coverage.
> It requires all four terminal validation cells, the frozen 73-case
> split/order provenance and identical steady digest, and rejects identifiers,
> locked test/79-extra reads, proposal-only steady labels, incomplete cells,
> thresholds and automatic conclusions. This is synthetic-tested readiness
> only; keep the response oracle first after PBS recovery, use only introai9,
> never junjinyong, and do not maintain the site.

> **2026-08-21 comparator container-hash correction:** The prepared GHD-GPS
> and Transolver configs/validators had a 61-character transcription of the
> pinned container digest. Correct it to the verified 64-character SHA-256
> before either comparator is activated. This changes no model, data, split,
> loss, schedule or result; all earlier comparator readiness heads are
> superseded for execution provenance and no comparator job exists.

> **2026-08-19 matched steady scope implemented:** Reusable metadata-only
> validator `aneug_release_730_steady_training_scope` hash-binds the exact
> public/private overlap results, archive case order, tensor/GHD schema,
> index-to-name alignment and eligible digest before returning the common
> 13,985 indices. It indexes no WSS and fixes neither architecture nor training
> schedule. Both strongest comparator and selected proposal must use this same
> scope; proposal-only steady labels and steady-as-novelty are rejected.

> **2026-08-18 steady and objective controls completed:** Geometry-only steady
> audit R2 completed without indexing WSS. The processed object has 14,392
> rows; excluding 407 exact-GHD matches to train/validation/locked-test/extras
> leaves the common 13,985-row eligible information budget, digest
> `6dbfde4d...c82cc`. The same private index list must be used by the strongest
> comparator and proposal; steady supervision is a control, not novelty.
> The train-only objective-scale CPU audit also completed after 584 train and
> zero validation/test/extra field reads. Its numeric output remains private
> and authorizes no automatic sensitivity. Release-730 Graph U-Net
> `117056.ECE-util1` remains the sole GPU job, healthy through coverage 9;
> monitor without stopping, tuning or duplicating it. Use only introai9, never
> junjinyong, and do not maintain the public site.

> **2026-08-18 upstream split wording corrected:** The AneuG-Flow paper's
> 4.67% result is steady WSS under an 80/20 split. The pinned transient helper
> implements a nominal 90/10 path by taking the leading eligible `stable_*`
> entries in archive order without shuffling. Therefore the active immutable
> config's literal `released random 90/10 split` is imprecise; interpret it as
> the released helper's order-slice 90/10 path and do not alter the running
> config bytes. The keyed, field-blind 584/73/73 split remains the main
> protocol, with unresolved source lineage and no family/patient/BC claim.

> **2026-08-18 train-only objective-scale audit prepared:** This historical
> preparation state is superseded by the completed execution above. The exact
> utility reproduces the upstream phasewise train-transient WSS channel scale
> on 584 training fields, with no validation/test/extra read, GPU, model fit,
> public numeric result, threshold or automatic sensitivity decision.

> **2026-08-18 released-objective boundary corrected:** Direct inspection of
> pinned upstream `train_baselines.py`, `datasets_wss_optimized.py` and
> `losser.py` found that `renormalize_transient=True` rescales frame-MSE
> residuals by train-transient channel statistics. Active job
> `117056.ECE-util1` instead applies frame MSE directly in the stored
> steady-normalized coordinates while retaining the unchanged released class,
> physical log-magnitude term and common physical evaluator. Preserve it as a
> released-class protocol adapter, never an objective reproduction. Do not
> stop or duplicate it solely for this bounded weighting difference. Consider
> an objective-only sensitivity after its terminal result only if exact
> train-only scale ratios and validation attribution show material value; hold
> every other model, split, seed, schedule, metric and sealed-scope field fixed.

> **2026-08-18 release-730 oracle comparison prepared:** A new result-pending
> analyzer parses only the 73-case released Graph U-Net and true-coefficient
> response-oracle result roles. It requires exact private hashes and the shared
> validation-order digest, and reports 10,000-resample paired deltas, metric
> Pareto membership and rank-specific active basis storage. It has no absolute
> threshold, automatic rank/global-branch decision, locked-test/79-extra read,
> public numeric output or paper claim. Do not execute it until both terminal
> results and a fresh private activation exist. The historical v4 51-case
> utility remains unchanged. Use only introai9, never junjinyong, and do not
> maintain the site.

> **2026-08-18 train representation attribution completed:** CPU job
> `117052.ECE-util1` finalized F/exit 0 in 00:08:32 with 584 train and zero
> validation/test/79-extra field reads. Exact public/private/log/status hashes
> are `a44eee33...3b85` / `3e5ef9dc...9255` / `8c589f88...d1f` /
> `143bdccd...b42`. Six training cases have genuine boundary discontinuities:
> boundary/interior-median ratios 11.25--17.29 and absolute jumps 3.43--5.35.
> Do not force periodic closure. Stored normals are nonunit/near-zero; use
> mesh-derived normals only as input/diagnostic. Raw Cartesian WSS remains the
> common target and tangent projection is an optional field-tax ablation.
> The split remains fixed but must be described as outcome-blind geometry-ID
> random duplicate-disjoint with unresolved source lineage, never family-IID.

> **2026-08-18 release-730 direct-prior baseline prepared:** A fresh baseline
> imports the released AneuG Graph U-Net class unchanged and binds the exact
> 584/73 development split. It uses released normalized six-channel inputs and
> frame-MSE/log-magnitude objective, but evaluates the unprojected raw physical
> Cartesian WSS under the common area/phase-weighted metric. The missing common
> waveform is zero and BC generalization is not claimed. This is a declared
> protocol adapter, not an end-to-end reproduction. It has no absolute gate,
> winner, locked-test/79-extra access, multi-seed confirmation or paper claim.
> Execute only after public Quality and a private activation, on `introai9`.

> **2026-08-18 train-only representation attribution prepared:** A single
> CPU-only analysis is prepared to distinguish a genuine phase-79-to-0 source
> discontinuity from an isolated relative-error effect and to quantify whether
> stored or mesh-derived normals support a tangent target. It may read only the
> 584 training fields, publishes no case IDs, has no threshold or automatic
> architecture selection, and cannot delay the new-split direct baselines.
> Every comparator initially predicts the identical raw physical Cartesian
> WSS. Validation/test/79-extra fields, GPU, model fitting and paper claims
> remain closed. Use only `introai9`, never `junjinyong`, and do not maintain
> the site.

> **2026-08-18 train-audit R2 completed:** Corrected CPU job
> `117037.ECE-util1` exited 0 in 00:07:10 after reading exactly 584 train
> fields; validation/test/79-extra reads remain zero. All integrity checks pass.
> Exact public/private/log/status hashes are `3c525820...9587` /
> `ce1dd6d2...9385` / `2c93523e...9ec` / `e1e0fcbe...d89`.
>
> Descriptive evidence changes the architecture boundary. Phase 79-to-0 jump
> has median 0.01166 and q95 0.01456 but maximum 0.36399. Stored-normal norm
> reaches 0.000151, and reference WSS has nonzero normal ratios (casewise
> median-ratio median 0.0211; p95-ratio median 0.1107). Do not hard-project
> outputs tangent or enforce periodic closure yet. Run one train-only
> attribution of cyclic adjacent jumps and near-zero-normal support first; keep
> raw released vector WSS as the common primary target.

> **2026-08-18 train-audit R1 pre-field failure:** CPU-only job
> `117034.ECE-util1` exited 1 in 00:02:11 after all exact source/split hashes
> passed and mmap objects loaded, but before any case tensor index. The reader
> reimplemented the producer's newline case-digest grammar as compact JSON;
> its fixture repeated the same error. Train/validation/test/extra field reads
> are all zero and no scientific verdict exists. Preserve R1. Import the exact
> producer helper, pin its grammar in a regression test, pass Research Quality,
> and rerun the unchanged train-only audit under a fresh ID. This is allowed by
> the diagnosed append-only retry policy.

> **2026-08-18 release-730 experiment priority reset:** The main paper now
> uses the completed 584/73/73 processed-v5 release intersection. Historical
> v4 406/51 D11/D12 records are engineering provenance, not main-table rows or
> initialization sources. Immediate order is train-only physical audit;
> train-only response oracle; new-split official Graph U-Net, GHD-GPS/GINE and
> Transolver; response/local ablations; then functional-objective ablations.
> Defer LinearNO/Transolver++ and the 79 processed-only cases until the core
> comparison is complete.
>
> A new CPU-only train audit is prepared. It binds the exact R3 public/private
> split hashes and may index only 584 training tensors. Hard checks cover data
> identity, finiteness, static geometry, normalization round-trip, faces, GHD
> and cycle endpoints; tangency, phase-boundary jump and hemodynamic summaries
> are descriptive rather than model pass thresholds. It creates no tensor
> duplicate and permits diagnosed append-only retries. Validation/test/extra
> fields, models, GPU and paper claims remain closed. Use only `introai9`,
> never `junjinyong`, and do not maintain the site.

> **2026-08-18 release-730 split completed:** Network-free CPU/PBS R3
> `117026.ECE-util1` exited 0 in 00:00:27 at exact source `0dd4f851...ba1dc`.
> All 730 canonical cases are singleton GHD components (zero exact duplicates,
> zero tolerance edges, maximum size 1), yielding exactly 584 train / 73
> validation / 73 locked test. Public result SHA-256 is
> `4fa3be7c...5bf991`; private manifest SHA-256 is
> `4ff88105...3077f`. Independent structure audit found 730 unique union IDs,
> zero cross-overlap and a matching private-key hash. No field/model outcome
> was used and test remains unopened. New work may read train fields for
> source/normalization audit; validation is development only and test stays
> sealed. D12 remains the sole GPU job. Use only `introai9`, never
> `junjinyong`, and do not maintain the site.

> **2026-08-18 release-730 split R2 network-preload failure:** CPU-only job
> `117024.ECE-util1` exited 1 in 00:04:32 after the exact source checksum when
> the compute node could not reach the pinned Hugging Face API. It did not load
> the processed object, compute GHD distances or assignments, or read fields/
> test values. Preserve R2. The exact 730 public directory IDs are now pinned
> locally in manifest SHA-256 `5218ae05...b20f0`, with the already registered
> sorted-ID digest `cccc90d7...390a`. A Quality-passed network-free runner may
> retry under a new job ID with every scientific split input unchanged. D12
> remains the sole GPU job; never use `junjinyong` or maintain the site.

> **2026-08-18 release-730 split R1 pre-load failure:** CPU-only PBS job
> `117020.ECE-util1` exited 1 after 27 seconds because the runner requested
> `mesh_case_order_exact` while the exact pinned schema record emits
> `mesh_order_exact`. It failed before processed-object load, GHD comparison,
> assignment or field/test access. Preserve R1. A source-only correction and
> regression test may rerun the unchanged scientific split under a new job ID
> after Research Quality passes. D12 remains the sole GPU job. Use only
> `introai9`, never `junjinyong`, and do not maintain the site.

> **2026-08-18 processed-v5 normalization provenance completed:** CPU-only
> PBS job `117006.ECE-util1` exited 0 after 00:26:15. Every one of 578 v4/v5
> overlap cases is bit-exact across all nine tensor channels and 432-D GHD;
> all eight hierarchy items match and maximum tensor mismatch is zero. Exact
> public result SHA-256 is `a083a4a7...11fdb`; steady-normalizer fingerprint
> is `5041cfc8...6b6f2`. This supports physical decoding under the pinned
> official single-normalizer builder, but v5 still lacks a creator manifest,
> so state the v5-only lineage as strong inference, not direct attestation.
> The split runner must bind this exact result. No field statistic, model
> endpoint or locked test was read. D12 remains the sole GPU job. Use only
> `introai9`, never `junjinyong`, and do not maintain the site.

> **2026-08-18 official-source reconciliation and normalization boundary:**
> Final NeurIPS PDF, pinned dataset card and exact release tree support 730
> transient synthetic CFD cases, while the proceedings HTML still says 200.
> The final PDF itself conflicts on 109 versus 116 real generator-training
> shapes, so do not infer patient or generator-parent lineage. The official
> 4.67% result is steady WSS, not a transient-cycle baseline. Processed v5 is
> an official blob but is not named by the card and its 809 entries are not the
> canonical cohort. The official builder requires an external steady
> `tensor_norm` and omits it from transient output. Exact steady v4 metadata is
> present on `introai9`; a CPU/PBS audit will compare all 578 v4/v5 overlapping
> tensors, GHD rows and shared hierarchy before physical-unit v5 metrics are
> authorized. This audit is provenance, not performance, and does not open the
> locked test. Use only `introai9`, never `junjinyong`, and do not maintain the
> site.

> **2026-08-18 complete-release v5 reconstruction:** The exact processed-v5
> object is present on `introai9`. CPU/PBS finalize job `116626.ECE-util1`
> exited 0 after assembling 33,233,856,917 bytes and matching official SHA-256
> `3edf0d75…f3b0ae`; schema job `116627.ECE-util1` exited 0 with 809 unique,
> mesh-order-aligned cases, 80 × 13,902 × 9 case tensors and 809 × 432 GHD
> metadata. The pinned public release tree contains 730 cases; v5 contains all
> 730 plus 79 extras. The new study cohort is exactly the 730-case intersection,
> never all 809 and never the historical v4 406/51/51 split. A fresh
> outcome-blind GHD duplicate-component 584/73/73 assignment is being prepared
> with a private key; no WSS/model outcome or locked-test value is used. D12
> remains historical and must not be duplicated. Use only `introai9`, never
> `junjinyong`, and do not maintain the site.

> **2026-08-18 active-branch source synchronization:** Exact public
> scientific source `27be93fb90391c5981982b0bd5a0c090a3980b25` is remote
> exact and passed Research Quality `32057390792` with 852/852 tests. Its
> automatic Pages run `32057389118` passed but site work remains out of scope.
> D13B stays dataset-free/non-executable with no rank, model, field, GPU,
> result or claim selected. Never use `junjinyong` or maintain the site.

> **2026-08-18 architecture-ablation compute boundary:** The dataset-free
> wrapper now has three explicit forwards. `response_only` can be constructed
> without a local backbone and never calls one; `local_only` never calls the
> response head but still reports its actual response-basis leakage; and
> `response_plus_residual` evaluates both branches. This prevents hidden
> unused-branch compute or parameters from contaminating D13B ablations. Exact
> implementation/test/rationale hashes are `266f10d5…1ee8` /
> `702c8964…70a1` / `a280594c…c877`; 9 focused and 852 full tests pass. No
> architecture, rank, result or execution is selected. Never use `junjinyong`
> or maintain the site.

> **2026-08-18 selected-rank storage source synchronization:** Exact public
> scientific source `2ce228364c402433cd4f69836eacd2e68f8ef1b5` is remote
> exact and passed Research Quality `32056691160` with 850/850 tests. Its
> automatic Pages run `32056690269` passed but site maintenance remains out of
> scope. D13B is still dataset-free/non-executable and no rank, field, GPU,
> result or claim was selected. Never use `junjinyong` or maintain the site.

> **2026-08-18 selected-rank storage correction:** Dataset-free inspection
> found that a contiguous rank prefix could retain the complete rank-256 basis
> storage. The decoder now clones only the selected rows, and a storage-level
> regression test proves that low-rank variants do not silently carry the full
> GPU allocation. This changes no response equation, rank choice, evidence
> gate or result. Exact implementation/test/rationale hashes are
> `b141e287…1b76` / `0061c6b4…4400` / `c66021a9…3f50`; 7 focused and 850
> full tests pass. D13B remains non-executable. Never use `junjinyong` or
> maintain the site.

> **2026-08-18 paired-comparison source synchronization:** Exact public
> scientific source `416627724435b6ec46bbde9aabea52088aa2eed6` is remote
> exact and passed Research Quality `32055879571` with 849/849 tests. The
> automatic Pages failure `32055878103` is outside research scope and must not
> be repaired. No numeric comparison, automatic winner, absolute threshold,
> outer/auxiliary access or paper claim exists. Never use `junjinyong` or
> maintain the site.

> **2026-08-18 result-pending paired validation comparison:** A public,
> dataset-free utility now compares matched validation results through raw
> endpoint means, paired component-bootstrap candidate-minus-reference deltas,
> favorable-direction probabilities and a multi-endpoint Pareto set. It has no
> absolute threshold or automatic winner and explicitly treats the 51 units as
> synthetic geometry components, not patients or population inference. A
> future private activation must bind exact result hashes and the shared cache
> order before numeric use. Exact implementation/test/config/rationale hashes
> are `9e10a9c3…3b53` / `1b39c1ff…d13f` / `5aff967b…07a7` /
> `2a5b6529…b941`; 6 focused and 849 full tests pass. No outer/auxiliary read,
> method selection, result or paper claim exists. Never use `junjinyong` or
> maintain the site.

> **2026-08-18 cycle-response residual source synchronization:** Exact public
> scientific source `2d702044d8fff81bee7a9cf258e8aa00ebb189d3` is remote
> exact and passed Research Quality `32054927814` with 843/843 tests. The
> automatic Pages run `32054927242` failed outside research scope; do not
> repair it. The prototype remains dataset-free and non-executable with no
> rank choice, field read, GPU job, result or paper claim. Never use
> `junjinyong` or maintain the site.

> **2026-08-18 cycle-response residual prototype:** A dataset-free D13B
> building block now makes the conditional performance method concrete. It
> predicts positive amplitude and complete-cycle response coordinates from the
> 432-D GHD token, decodes a case-tangent global field, and combines it through
> a near-zero-initialized case gate with an interchangeable tangent local
> backbone. Response-basis overlap is a reported soft penalty; there is no hard
> projection, rank choice, absolute threshold, field read, GPU job or paper
> claim. D12 must terminate and D13A must report every oracle rank before a
> fresh executable D13B contract may exist. Exact implementation/test/config/
> rationale hashes are `1afc4bb9…6d26` / `e93b9de8…332c` /
> `2a36db75…8cef` / `291abc0a…f35`; 6 focused and 843 full tests pass. Use
> only `introai9`, never `junjinyong`, and do not maintain the site.

> **2026-08-18 D13C source synchronization:** Exact public D13C source
> `0710696abef755ecbb3001641c76052525733d9e` is remote exact and passed
> Research Quality `32053563054` with 837/837 tests. Automatic Pages run
> `32053561757` failed but site maintenance is outside scope; do not repair it
> or alter research code for deployment. D13C remains prepared/non-executable,
> with no real-field read, job, result or paper claim. Never use `junjinyong`.

> **2026-08-18 prepared D13C same-backbone functional fine-tuning:** D13C is
> implemented and testable but non-executable until D12 has a terminal record
> and one fresh private activation binds one variant. Five rows start from the
> exact D11 epoch-121 checkpoint: field-only continuation, statistics-only,
> OSI-only, all-functional scalarization and all-functional field-anchored
> optimization. Training loss scales come only from all 406 D11-initial train
> predictions; checkpoint utilities use the identical initial D11 validation
> endpoints, making field-only selection match D11's average-rL2 grammar.
> There is no absolute threshold, outer/auxiliary read, confirmation or paper
> claim. Exact config/implementation/PBS/test/rationale hashes are
> `b3bf4ba1…82d1` / `ee6bb211…313e` / `bdc962d5…3391` /
> `9d0136a9…dcd4` / `8bdc189a…c3d9`; 7 focused and 837 full tests pass.
> D12 job `116609.ECE-util1` remains the sole GPU job. Never use `junjinyong`
> or maintain the site.

> **2026-08-18 functional-alignment source synchronization:** Exact public
> scientific source `1e27570753e51a645e800ef846e158b58e5a933a` is remote
> exact and passed Research Quality `32051075036`. Twelve focused and 830 full
> tests pass. The unrelated automatic Pages run `32051075537` failed; public
> site maintenance is outside the current user scope, so do not repair it or
> change research code for deployment. D12 job `116609.ECE-util1` remains the
> sole introai9 GPU job. Never use `junjinyong`.

> **2026-08-18 complete-cycle functional-alignment kernel:** A dataset-free,
> non-executable D13C building block now computes explicit field, mean-vector,
> TAWSS and reference-support OSI losses from one decoded WSS cycle. It adds no
> inconsistent auxiliary head and uses neither RRT nor the failed D9A hard
> post-hoc projection. The reference support floor and all loss weights remain
> external inputs; no absolute performance threshold, architecture selection,
> real-field read, GPU run or paper claim is encoded. Future same-backbone
> development compares field-only, statistic-aligned, OSI-aligned and complete
> objectives after the direct controls. An optional field-anchored optimizer
> removes only first-order functional/field gradient conflict and norm-matches
> the retained direction; it is a control, not a finite-step guarantee or
> standalone novelty. Exact implementation/test/config/doc hashes are
> `a54ded57…82f6` / `d5802bb2…69b4` / `35da75a6…b6f1` /
> `6dbeee93…85bc`; 12 focused and 830 full tests pass. Never use `junjinyong`
> or the site.

> **2026-08-18 prepared D14 Transolver control:** D14 is implemented and
> testable but non-executable while D12 has no terminal record. It adapts the
> exact pinned MIT Transolver physics-slice design into a same-information
> complete-cycle control: coordinates, mesh normals, relative area and 432-D
> GHD enter eight 256-wide blocks with eight heads and 32 slices, followed by
> an 80-phase tangent WSS output. It is a comparator, not the proposed method
> or an exact upstream reproduction. It has no absolute threshold and reads no
> outer/auxiliary values. Fresh Quality and private activation are required;
> never use `junjinyong` or the site.

> **2026-08-18 prepared D13A response-manifold oracle:** D13A is implemented
> and testable but non-executable while D12 has no terminal record. It fits an
> area/phase-weighted, energy-normalized complete-cycle basis from the 406
> train fields and reports validation oracle reconstructions at ranks
> 0/16/32/64/128/256. True validation RMS amplitude and oracle coefficients
> make this a representation ceiling, never model performance. It selects no
> rank, uses no absolute threshold and reads no outer/auxiliary values. A fresh
> Quality-passed source and private activation binding D12's terminal record
> are required before one introai9 job; never use `junjinyong` or the site.

> **2026-08-18 D12 R1 OOM and effective-batch-preserving retry:** Job
> `116607.ECE-util1`, run ID `d12_official_graphunet_r1`, finalized F/exit 1,
> stage-out 0 after the registered physical-batch-32 forward reached CUDA OOM.
> Failure occurred in the pre-optimizer smoke; no checkpoint, validation,
> outer/auxiliary read, metric or scientific verdict exists. Preserve R1.
> D12 v2 changes only execution batching: physical batch 8, four accumulated
> microbatches and the same effective batch 32 with one shared reference-energy
> denominator. Official model/forward, seed, split, input, loss, optimizer,
> schedule, validation and no-threshold interpretation stay fixed. The new
> run requires fresh Quality and private activation; use only `introai9`.

> **2026-08-18 D12 pre-submit source-pin correction:** A field-free introai9
> import smoke found a one-character transcription error in the pinned
> `GraphGPS_encoders.py` SHA-256. No PBS job, GPU, case tensor or scientific
> result was created. The canonical clean-checkout hash is
> `8c91521c95c6bec7458e7d6f23998283c029028874edd0deff444dac38a574f2`;
> the corrected config and regression assertion require fresh Quality and
> private activation before submission. Model, split, input, objective,
> optimization and metric are unchanged.

> **2026-08-18 D11 completion and direct-prior next step:** D11 job
> `116602.ECE-util1`, run ID `d11_gpsunet_r1`, finalized F/exit 0 and stage-out
> 0 after 161 epochs, selecting epoch 121. It used exactly the 406/51 cache,
> read no outer/auxiliary values and produced finite field/TAWSS/OSI metrics
> with full coverage. Raw numeric output, checkpoint and logs are preserved in
> the PRIVATE repository. Its registered legacy boolean is true, but it is not
> a paper-success verdict or an absolute gate. D12 directly imports the
> released official `PyGGraphUNetwTemporalEmbedding` class at `4a090a0…`
> through the same split/input/metric adapter and has no absolute threshold.
> The released trainer does not instantiate the repository's GraphGPS/GPSUNet
> class, so D12 is the actually wired Graph U-Net prior, not an exact RHSIA
> reproduction. PyG 2.6.1 is isolated from the pinned Torch container. Keep
> outer sealed, preserve all trials, use only `introai9`, and do not update the
> site.

> **2026-08-17 highest current operating authority:** Decisions are
> evidence-led and risk-based, not controlled by an inherited blanket ban.
> Older statements that a method, repair, retry, question or study family may
> “never” be revisited are historical provenance only. Preserve every old run
> and artifact, but re-test previously under-evaluated ingredients using a new
> run ID/result directory, linked predecessor, exact source/config/environment
> and explicit rationale. Exact-config infrastructure retries, bug-fix checks,
> validation-stage optimization/capacity iterations, ablations and stochastic
> replications are allowed when they can add information; no cosmetic new
> hypothesis or arbitrary attempt cap is required. Do not tune on confirmation
> or outer-test outcomes, and never overwrite or hide evidence. The operational
> scope remains `introai9` only, with `junjinyong` excluded unless the user
> explicitly changes it; maintain code and private records, not the site. This
> paragraph supersedes conflicting execution bans below.

> **2026-08-17 baseline-first performance authority:** D11's registered 0.35
> field-rL2 ceiling is retained as a legacy diagnostic, not treated as a
> literature-calibrated acceptance gate or a ban on continuation. Finish and
> preserve D11 regardless of that boolean. Before comparative or paper-level
> judgment, execute a clearly labelled direct AneuG/RHSIA prior baseline under
> the same data, split, inputs, metric and materially matched compute budget,
> using the released dependency/feature path wherever possible and recording
> every deviation. Then permit staged validation exploration of backbone
> capacity, geometric representation, periodic temporal decoding, objectives
> and cycle-functional readouts, including justified combinations. Retain all
> trials and keep outer data sealed until the candidate and confirmatory rule
> are frozen. This paragraph supersedes D11 text that makes later development
> conditional on the 0.35 boolean.

> **2026-08-17 D11 strong-baseline registration:** D10 Round 1 failed its
> frozen private feasibility gate, so projection repair on the custom backbone
> stays closed. D11 is one validation-development job on the exact 406/51 D9
> cache and seed 1103. It is explicitly a pure-Torch matched reimplementation,
> not a reproduction, of released AneuG/RHSIA elements: Cartesian geometry,
> GHD conditioning, GINE-style local messages, coarse global attention, graph
> U-Net hierarchy and direct 80-phase vector WSS. The official exact trainer,
> PyG/PyTorch3D runtime and cotangent encodings are unavailable and the
> differences are declared. Field feasibility must pass before any functional
> readout is registered. Outer/auxiliary, multi-seed confirmation, paper claim
> and public numeric output remain closed. Use only `introai9`; never use
> `junjinyong` or update the site.

> **2026-08-17 D10 Round 1 outcome and baseline pivot:** introai9 job
> `116601.ECE-util1`, run ID `d10_round1_direct_horizon_r1`, finalized F/exit 0
> and stage-out 0 with zero outer/auxiliary reads. The exact private result
> fails its frozen validation field-feasibility gate; numeric outputs,
> checkpoint and logs remain private. The longer horizon added information but
> did not make the custom backbone feasible, so D10 Round 2 is not authorized.
> Next is a separately versioned, compute-matched adaptation of an official
> AneuG/RHSIA strong baseline; establish field feasibility before testing any
> functional readout. Preserve D10 as negative validation development. Never
> use `junjinyong` or update the site.

> **2026-08-17 D10 bounded repair registration:** D9 remains failed and D9A
> remains attribution only. D10 predeclares at most two validation repair
> rounds and two training jobs. Round 1 changes only the direct cosine horizon
> from 20 to at most 251 epochs, retaining seed/backbone/loss/cache/metric and
> the original 0.35 threshold. Failure abandons the custom backbone. Round 2
> stays non-executable and could only align moment train/eval projection after
> a Round 1 pass and fresh activation. Outer/auxiliary and paper claims remain
> closed; numeric results are private. Never use `junjinyong` or update site.

> **2026-08-17 D9A projection attribution registration:** D9 completed but
> failed its private noncompensatory validation screen; outer/auxiliary remain
> sealed and D9 is not relabelled. D9A is a frozen-checkpoint, validation-only,
> no-fit comparison of raw moment-POD versus exact moment projection on the
> same 51 cases. It changes no checkpoint, metric, threshold, seed or split and
> cannot authorize repair or a paper claim. Numeric output remains private.
> Use only introai9 `coss_a6gpu:Qlist=a6000`; never use `junjinyong` or update
> the site.

> **2026-08-17 D9 container execution retry registration:** Passing R4 job
> `116555.ECE-util1` selects introai9 `coss_a6gpu:Qlist=a6000` plus the exact
> pinned Torch 2.5.1+cu118 container. New R0/R1 wrappers reuse byte-exact D9
> scientific config/code; split, architecture, loss, seed and thresholds do
> not change. R0 verifies R4, mounts data read-only and writes a new private
> cache; R1 requires its pass and reads only that cache. Outer/auxiliary,
> confirmation and paper-claim authority remain zero. Every execution uses a
> new append-only run ID. Never use `junjinyong` or update the site.

> **2026-08-17 D9 GPU-runtime R3 finding and R4 registration:** Requesting
> `coss_a6gpu` alone again allocated `ece-tgpu3` (`Qlist=tgpu`) and reproduced
> missing UVM plus `cuInit` 999; queue name alone is not node isolation. PBS
> metadata shows actual A6000 nodes advertise `Qlist=a6000`. R4 adds exactly
> `:Qlist=a6000` to the select resource and reuses the exact data-free probe and
> pinned container. Pass selects that route for D9 R0; non-A6000 allocation or
> CUDA failure is an explicit scheduler/admin blocker. Never use `junjinyong`
> or update the site.

> **2026-08-17 D9 GPU-runtime R2 finding and R3 registration:** On
> `coss_agpu`/`ece-tgpu3`, R2 found a scheduler-visible GPU but no
> `/dev/nvidia-uvm` or `uvm-tools`; host/container `cuInit(0)` returned 999 in
> inherited/zero/unset conditions. This is node CUDA/UVM engineering evidence,
> not D9 science. R3 changes only the introai9 queue to enabled `coss_a6gpu`
> and reuses the exact probe/container to separate node-route failure from an
> account-wide runtime problem. A container pass selects that queue for new-ID
> D9 R0; repeated missing-UVM failure is an administrator blocker. Never use
> `junjinyong`, read data in this probe or update the site.

> **2026-08-17 D9 GPU-runtime R1 outcome and R2 registration:** R1 job
> `116551.ECE-util1` had working scheduler `nvidia-smi` but the same CUDA
> initialization failure in host/user-site Torch and the pinned container,
> before any scientific path or read. R2 is an information-gaining data-free
> diagnostic: selected environment keys, NVIDIA/UVM device nodes, low-level
> `cuInit` and inherited/zero/unset visibility variants across both runtimes.
> A matching pinned-container driver plus Torch pass selects the D9 R0 runtime;
> all-variant failure produces an administrator-level blocker record. This is
> engineering evidence, not a dataset/model/scientific failure. Use only
> `introai9`; never access `junjinyong`, and do not update the site.

> **2026-08-17 D9 GPU-runtime revalidation registration:** The first action
> under the current iterative policy is a data-free, one-allocation comparison
> of scheduler `nvidia-smi`, the original host/user-site Torch runtime and the
> existing pinned Torch 2.5.1+cu118 Singularity runtime. It reads no AneuG path,
> model or metric. Container CUDA availability plus a finite matrix multiply is
> the pass condition; host failure is diagnostic and nonblocking. Pass selects
> the exact pinned image for a new-ID D9 R0 retry with the same scientific
> split, architecture, loss and thresholds. Runtime outputs remain private.
> Use only `introai9`; never access `junjinyong`, and do not update the site.

> **2026-08-17 current iterative-validation authority:** The user withdrew the
> blanket local-repair-loop and no-rerun rule. Historical jobs and artifacts
> remain immutable, but their dataset, split, architecture, loss, code path and
> scientific question may be reused in a new run. Infrastructure/dependency/
> scheduler failures, interrupted jobs, stochastic replications and bug-fix
> checks may be retried without inventing a new hypothesis. Every repetition
> uses a new run ID/result directory and append-only provenance containing its
> predecessor, exact commit/config, seed, environment and rationale; never
> overwrite, hide or selectively discard an earlier outcome. Training/
> validation development may iterate, while outer/confirmatory endpoints and
> rules must be frozen before access and may not be tuned after observation.
> There is no arbitrary one-attempt cap, but an unchanged failure is repeated
> only when the run can add information. This paragraph supersedes older
> one-shot/no-repair statements as current policy; those statements remain
> historical records. Code and experiment records are maintained, not the
> public static site. Use only `introai9`; never access/query/transfer/submit/
> monitor `junjinyong`.

> **2026-08-16 transient WSS functional metric kernel:** A synthetic-only,
> method-free kernel now requires explicit phase quadrature for TAWSS/OSI/RRT,
> returns NaN plus validity masks at singular nodes and verifies the algebraic
> identity RRT = inverse mean-vector magnitude. Established functionals and the
> kernel are not novelty or paper results; RRT is redundant secondary evidence,
> never an independent co-primary. Future comparison masks/floors must be
> train-defined before validation. D6/field/model/PBS/GPU/result/claim remain
> 0. Never use `junjinyong`; do not maintain the public static site.
> The paired per-case evaluator additionally requires external triangle-lumped
> areas and reference-side direction/TAWSS/mean-vector floors; it never fits
> them, aggregates cases or infers independence. Invalid predictions are
> penalized and their coverage is returned beside area/phase-weighted field,
> mean-vector, TAWSS, direction, OSI and log-RRT sufficient metrics.

> **2026-08-16 cycle-moment projection synthetic prototype:** A dataset-free,
> non-executable PyTorch prototype now tests the conditional readout's actual
> mathematical constraint. It tangent-projects and temporally centres a raw
> residual, then selects the nonnegative scale closest to one whose cycle has
> the predicted mean vector and mean magnitude. The closest-root rule avoids
> erasing valid collinear magnitude pulsatility at the non-unique Jensen
> boundary. Synthetic tests cover both moments, tangency, rotation
> equivariance, infeasible/degenerate rejection and finite gradients. These are
> self-consistency properties, not CFD accuracy, model selection, novelty or a
> paper result. D6 activation/field/PBS/GPU and validation/outer/model/claim
> remain 0. Never use `junjinyong`; do not maintain the public static site.
> Root bracketing runs under `no_grad`; one strict-interior implicit correction
> restores gradients with backward-graph size independent of iteration count.
> Autograd agrees with central differences on separate raw-residual,
> mean-vector, cone-coordinate and joint perturbation routes at the registered
> synthetic tolerances.
> The set-valued Jensen-boundary scale is deliberately detached and requires
> explicit endpoint supervision if this mechanism ever becomes eligible.
> A reproducible local CPU-only `[80,13902,3]`, 24-iteration, four-thread
> synthetic benchmark observed 0.5221--0.8612 s forward, 0.0497--0.0810 s
> backward and 635,880--649,748 KiB process peak RSS with zero
> registered-tolerance moment error. The range preserves timing variation; it
> is not a GPU/model throughput, memory or scientific result.

> **2026-08-16 AneuG transient direct-prior reappraisal:** Current
> arXiv:2601.19876v2 already occupies AneuG transient vector WSS with a
> GHD-GraphGPS/GINE model, 14k steady augmentation, Graph U-Net/LaB-GATr/
> LaB-VaTr/sequence/spectral controls and TAWSS/OSI/RRT evaluation. Its best
> 2.84% maximum-normalized field error coexists with 26.98% conventional field
> rL2 and 68.35% OSI rL2; the broad mismatch observation is therefore also
> prior. The only conditional residual question is a same-backbone,
> field-error-matched cycle-functional audit plus a minimal moment-consistent
> readout on the exact D5 component split. This is application/evaluation, not
> new-GNN novelty, and remains unselected until D6 pass plus observed matched
> baseline failure. RRT equals inverse mean-vector magnitude and is never an
> independent co-primary. Earlier notes mischaracterized NOEM
> `10.1038/s43588-026-00974-2`; it is a neural-operator-element FEM, not a hard
> output transform. The relevant generic correction collision is
> arXiv:2505.24579v2. D6 activation, real field, validation/outer read,
> architecture/loss, PBS/GPU, result and claim stay 0. Never use `junjinyong`;
> do not maintain the public static site.

> **2026-08-16 D6 pre-activation implementation readiness:** The registered
> non-executable source now has a full one-case-at-a-time aggregate gate,
> fixed-histogram quantiles, private train-only sufficient statistics and
> strict public/private JSON. Synthetic 406-item and adversarial tests cover
> tangency, mesh-normal mismatch, temporal degeneracy, Jensen violation and
> endpoint degeneracy. A sealed-record sentinel proves validation/outer tensor
> values are never accessed by the iterator. Real payload read, file-I/O entry
> point, PBS/GPU wrapper, human activation, result and claim remain 0. This is
> not D6 execution and does not change its fresh-selection requirement. Never
> use `junjinyong`; do not edit the public static site.

> **2026-08-16 processed-v4 D6 train-field registration:** Closed/pass D5
> permits registration only of a fresh field audit. D6 is now registered but
> not human-activated and may not be mutated into an executable contract. It
> would read only the 406 private D5-train tensors plus shared finest faces;
> validation, outer and auxiliary tensor values remain sealed. The exact
> physical inverse is the official transient builder rule
> `normalized*(std+1e-5)+mean`; steady norm is release-decoder metadata and
> future model statistics must be recomputed from physical D5-train fields.
> The all-or-none audit covers mesh/stored-normal agreement, WSS tangency,
> temporal residual, positive TAWSS/finite OSI, unclipped RRT-denominator
> support and the Jensen cone `a>=||m||`. A pass would permit registration of
> bounded train/validation baseline development only. Current train-field
> read, PBS/GPU, method/model, validation/test, result and paper claim are 0.
> No site file is maintained. Never use `junjinyong`.

> **2026-08-16 processed-v4 D5 final synchronization:** Exact public closure
> source `a610b265b811da97941f1f4ffeced10db3f0863e` passed Quality
> `31947656106`. Exact private outcome source
> `c000504ad1da79d3b51b23413bcb1f733d3b9df9` passed integrity
> `31947694961`; IDs/component membership/log remain private and sealed paper
> bytes are unchanged. D5 remains closed complete/pass at 1/1 with split
> 406/51/51 and `scientific_verdict=null`. This synchronization creates no
> server query, field read, PBS/GPU work, model/test/result claim or site
> change. Next is registration only of a fresh field audit/bounded-development
> version. Never use `junjinyong`.

> **2026-08-16 processed-v4 D5 final closure:** Quality-passed public source
> `483409a…21e6` ran once as introai9 job `116483.ECE-util1`, CPU 4, 64 GB,
> GPU 0. It finalized F/exit 0 after 00:01:19; D5 is closed 1/1 and may never
> be rerun or repaired. Exact source/order passed. The 578 finite 432-D GHD
> rows form 576 components: 2 exact duplicate components, 0 additional
> tolerance edges, max size 2. Primary is 508 singleton `stable_*` components;
> 70 auxiliary cases form 68 components and mixed count is 0. The private
> split is frozen at 406/51/51 train/validation/outer components, all phases
> together. This is a synthetic-geometry split, not patient/site/family
> lineage. No field/connectivity value or scientific endpoint was read;
> `scientific_verdict=null`. Pass permits registration of field audit/bounded
> development only. Method, architecture, GPU, test, result and paper claim
> remain 0. Never use `junjinyong`; do not update the public static site.

> **2026-08-16 processed-v4 D5 selected registration:** The user explicitly
> selected D5 as a fresh executable evidence version. Closed D4 and the
> dormant D5 draft remain immutable; D5 is neither their repair nor relabel.
> Fresh config/evaluator/tests/PBS/document read only the aligned 578×432
> float32 `mesh_data.ghd`, group exact and prospectively tolerance-matched
> copies, seal every non-`stable_*` or mixed component as auxiliary, and
> prepare a private 80/10/10 synthetic-geometry-component split. This unit is
> never called a patient, site or verified generator family. D5 permits one
> `introai9` PBS attempt at CPU 4, 64 GB, GPU 0 after public Quality and private
> activation; any outcome closes it. A gate pass freezes the private split and
> permits only registration of later field audit/bounded development. Field
> read, validation/test, method, architecture, GPU, result and paper claim
> remain 0. Never use `junjinyong` or publish IDs, component membership,
> private paths/manifests or raw logs. Do not edit the public static site.

> **2026-08-16 processed-v4 D5 non-executable draft:** D4's 168/578 direct
> external-directory overlap is preserved but is no longer treated as proof
> that the processed geometry input is absent. Pinned official
> `record_mesh_upsampling` reads each transient case-local `checkpoint.npy`
> and writes aligned `mesh_data.cases` / `mesh_data.ghd`; it asserts no patient
> or parent-family lineage. A dormant D5 draft therefore permits only future
> reading of the 578×432 processed GHD values to group exact/numerical copies
> and, if feasible, freeze an 80/10/10 synthetic-geometry-component split.
> Filename-defined non-`stable_*` cases remain sealed auxiliary units and are
> never patients/sites by inference. Draft config/code/document plus 4/4
> synthetic tests exist, but D5 is unselected, unregistered and non-executable:
> processed GHD/field/server/PBS/GPU/split/result/claim remain 0. A fresh D5
> requires explicit human selection and may never mutate the draft. Never use
> `junjinyong`.

> **2026-08-16 processed-v4 D4 final closure:** Quality/Pages-passed public
> source `be233176…9e08` ran exactly once as introai9 PBS job
> `116482.ECE-util1` with CPU 4, 64 GB and GPU 0. It finalized F/exit 0 after
> 00:01:56 with 222,168 kB recorded memory. Exact source identities passed and
> the threshold-free census completed: 578 unique nonblank cases, all
> `[80,13902,9]` float32 with vector-WSS labels; mesh case count/order is
> 578/exact. Only 168/578 case IDs link directly to the current geometry root,
> leaving 410 unresolved. Public aggregate SHA is `06d11149…de8d`; ordered IDs,
> manifest and raw log remain private. D4 is closed 1/1 with no rerun and
> `scientific_verdict=null`. Human rescore keeps the AneuG direction inactive
> at 31.0/40: processed-target feasibility improved, but generator lineage and
> geometry linkage remain unresolved. D4 opens no grouping/split/P0/method/
> architecture/GPU/test/result/claim. A fresh metadata-only case↔geometry/
> lineage mapping version requires explicit human selection. Never use
> `junjinyong`.

> **2026-08-16 processed-v4 D4 selected registration:** The user explicitly
> selected D4 as a materially distinct, threshold-free descriptive metadata
> census. D3 remains closed and immutable; D4 is not its repair, rerun,
> backfill or relabel. Fresh config/evaluator/test/PBS/document hashes are
> registered while the dormant draft remains byte-exact. D4 rechecks both
> official object identities, uses weights-only/mmap CPU loading, records the
> exact count and ordered IDs privately, and exposes only deidentified
> metadata aggregates/digest. Tensor values, connectivity values, WSS metrics
> and scientific verdict are excluded. It gets exactly one introai9 PBS
> attempt at CPU 4, 64 GB, GPU 0; any outcome closes the version. Current
> attempt count is 0/1 pending Quality, private activation and submission. A
> complete census permits human rescoring only. Grouping/split/P0/method/
> architecture/GPU/test/result/claim remain zero. Never use `junjinyong` or
> publish private paths, IDs, manifests or raw logs.

> **2026-08-16 processed-v4 static artifact semantics S0:** Exact official
> dataset/code remain `9dd4180…` / `4a090a0…`. Filename-only enumeration finds
> 730 transient directories and all 730 have the seven documented assets, but
> closed D3 proves the exact processed v4 `registered_data_list` is below 700.
> Never substitute raw 730 for the processed cohort. Official `1k` is formatted
> from `n_subdivide=1`, not a 1,000-case promise. The builder asserts no 730
> floor, uses unsorted `wall_data.pt` directories, may reuse mesh/assembled
> caches and provides no lineage-disjoint split. Specific missing IDs and build
> cause remain unknown; no processed payload was reopened and D3 stays failed
> without count backfill. Static result `eeb18e27…b56a4` is complete. Recommend
> only a human-selected, threshold-free metadata D4 census. Its non-executable
> draft and pure metadata code pass 5/5 synthetic tests, keep ordered IDs
> private, reject tensor-value access and refuse draft execution. Official
> builder `loaders.py` independently corroborates the exact case keys and mesh
> hierarchy; the draft records hierarchy shape/dtype only, never connectivity
> values, and emits `scientific_verdict=null`. This entry records the
> pre-selection S0 state; the newer D4 registration above supersedes its
> activation status. Split/P0/method/model/GPU/test/result/claim remain zero.
> Never use `junjinyong`.

> **2026-08-16 D3 final closure:** Exact client source became 23/23 immutable
> server chunks in 23 first SFTP sessions, with zero resume and zero hash
> mismatch. Finalizer job `116425.ECE-util1` used CPU 4/8 GB/GPU 0 and finished
> F/exit 0 after 00:19:16; it retired the closed D2 partial only after all
> chunks passed, published exact 23,744,862,051 bytes/SHA-256 `141541ed…51c9`,
> then deleted the chunks. The sole CPU 4/64 GB/GPU 0 schema job
> `116437.ECE-util1` finished F/exit 1 after 00:10:53. Object checksums,
> weights-only/mmap root loads and required root keys passed, then the frozen
> minimum of 700 registered cases failed as `AcquisitionContractError:
> case_floor`. Exact count, IDs, timestep/label, mesh order, geometry linkage,
> norm/case manifests and schema result were not materialized. D3 is closed:
> never rerun, repair or backfill the exact count by post-hoc payload read.
> Preserve the exact transient and temporary steady object pending a human-
> selected materially distinct evidence version. Scientific P0/split/method/
> architecture/GPU/test/result/claim remain 0. Never use `junjinyong` or
> publish private paths, IDs or raw logs.

> **2026-08-15 D3 fixed-chunk registration:** The user explicitly selected
> D3 as a materially distinct acquisition version. D1 and D2 remain closed;
> D3 never resumes the monolithic D2 partial or creates D2 session 4. The
> checksum-exact 23,744,862,051-byte client object is partitioned into 22 ×
> 1,073,741,824-byte chunks plus one 122,541,923-byte chunk. Create/upload only
> one local chunk at a time, bind each to a private offset/size/SHA-256
> manifest, delete it only after server size/hash match, and never re-upload a
> completed chunk. An interrupted chunk permits only one same-chunk resume.
> After all 23 server chunks pass, and only then, retire the closed D2 partial;
> one CPU 4/8 GB/GPU 0 PBS finalizer reassembles and checks the exact full
> identity under a 57,122,234,152-byte peak. Any finalizer outcome closes it.
> A pass permits exactly one CPU 4/64 GB/GPU 0 checksum/schema PBS; any outcome
> closes it. Scientific P0, method, architecture, GPU training, test, result
> and claim remain 0. Never use junjinyong or publish private paths/manifests.

> **2026-08-14 D2 final closure:** Final SFTP session 3/3 ended with exact
> persistent `Connection reset` / `Couldn't send packet: Broken pipe` after
> preserving a public-rounded 10.17 GB transient server partial. Client transient
> remains exact at 23,744,862,051 bytes/SHA-256 `141541ed…51c9`; server steady
> remains exact-size at 9,632,510,050 bytes. SFTP is exhausted and closed:
> never repair/resume or open a fourth session. The checksum/schema PBS was
> not submitted; marker, schema, field read, science, P0/model/GPU/test/result/
> claim remain 0. This is transport-incomplete, not dataset, storage-plan or
> scientific failure. A materially distinct version requires explicit human
> selection or a verified transport change. Never use `junjinyong` or publish
> private staging paths.

> **2026-08-14 D2 final transient SFTP session:** SFTP session 2 also ended
> only with a turn-lifecycle interruption and preserved a public-rounded
> 6.27 GB remote partial. Final allowed SFTP session 3/3 uses the same exact
> client object and same incomplete-only remote object with `reput`. It runs
> as a detached Windows OpenSSH batch process so later turn changes cannot
> terminate it, and the remote partial is increasing. Internal connection
> attempts are bounded in that one process. Any session-3 outcome closes SFTP;
> never open a fourth session. Remote exactness, checksum/schema PBS, science,
> P0/model/GPU/test/result/claim remain 0. Never use `junjinyong` or publish
> private staging paths.

> **2026-08-14 D2 transient SFTP resume:** Quality/Pages-passed public source
> `8e46c0f…` records the exact client object. SFTP session 1 ended only with
> the orchestration-turn interruption and preserved a public-rounded 2.64 GB
> server partial; this is not a source, checksum, storage or schema
> failure. SFTP session 2/3 uses `reput` on the same exact client object and
> the same incomplete-only server object; it resumed at the preserved offset
> and is increasing. Transient server exactness, one-shot schema/PBS, science,
> P0/model/GPU/test/result/claim remain 0. Never use `junjinyong` or publish
> private staging paths.

> **2026-08-14 D2 transient client exact and SFTP:** Transient v4 completed
> allowed client session 2/3 at exact size 23,744,862,051 bytes after three
> recoverable response interruptions inside that session. Independent full
> SHA-256 exactly matches official `141541ed…51c9`; no payload was parsed.
> Windows OpenSSH SFTP session 1/3 is uploading the exact object to an
> incomplete-only server filename. Steady remains server-exact and its client
> copy remains deleted. Transient is client-exact but not yet server-exact;
> checksum/schema PBS, scientific P0, model, GPU, test, result and claim remain
> 0. Never use `junjinyong` or publish private staging paths.

> **2026-08-14 D2 steady server staging and transient resume:** Steady v4
> completed Windows OpenSSH SFTP session 1 and the introai9 object has exact
> size 9,632,510,050 bytes. Its independently checksum-matched client copy was
> deleted before transient acquisition and is recoverable from the official
> source. Transient client session 1 ended only because the orchestration turn
> was interrupted, preserving a public-rounded 4.57 GB partial; this is not
> a source, checksum, schema or scientific failure. The same exact partial is
> increasing in allowed client session 2/3. Steady is server-exact 1/2,
> transient is not yet client-exact or server-staged, and schema/PBS/science,
> P0/model/GPU/test/result/claim remain 0. The registered wrapper requires the
> temporary steady filename and deletes it only after schema success. Never
> use `junjinyong` or publish private staging paths.

> **2026-08-14 D2 steady client completion:** Quality-passed D2 source
> `0b8eab2…` downloaded steady v4 in client session 1. Exact size is
> 9,632,510,050 bytes and full SHA-256 matches official
> `0c03c1d9…0177f`; no payload was parsed. Server staged objects remain 0/2,
> transient client sessions 0 and schema/PBS/science 0. Next: SFTP the exact
> steady object, verify server size, delete the client steady copy, then begin
> transient. Never use `junjinyong` or expose private staging paths.

> **2026-08-14 client-staged D2 registration:** D1 remains closed 3/3 and is
> never relabelled. A local HEAD audit verified both official v4 identities,
> and a 67,108,864-byte transient range probe returned HTTP 206 at 5,697,265
> B/s to a null sink; no byte persisted or was parsed. D2 uses only official
> HTTPS to sequential exact client cache, then Windows OpenSSH SFTP to
> introai9. It forbids compute/login-node external download. Client cap is
> 30 GB, server peak 33,377,372,101 bytes and maximum simultaneous new bytes
> 57,122,234,152 under a 60 GB workflow cap. Steady is uploaded first and its
> client copy deleted before transient download; server steady is deleted only
> after a successful compact norm/schema record. Up to three same-partial
> client/SFTP sessions per object are transport bounds, not scientific trials.
> Exact server sizes permit exactly one CPU 4/64 GB/GPU 0 PBS checksum/schema
> attempt; any outcome closes it with no repair/rerun. Pass opens only geometry
> grouping and split freeze, never scientific P0/model/GPU/test/claim. Never
> use `junjinyong` and never publish private client/server paths.

> **2026-08-14 D1 final closure:** Quality/Pages-passed public source
> `274bb0e3ced86a908bdb4d6cfa7b61c4c248f9cb` ran as final introai9 job
> `116209.ECE-util1`, CPU 4, 64 GB, GPU 0. It finalized F/exit 28 after
> 00:07:32 with exact persistent error `Connection timed out after 30001
> milliseconds`. Partial bytes, transport-complete marker, reader and schema
> are 0. Log/status SHA-256 are `66d3a249…402d` / `7f093a68…2a72`; raw PBS
> output did not materialize. This is compute-node transport failure, not a
> dataset, storage-plan or scientific verdict. D1 exhausted 3/3 and is closed;
> never repair/resubmit it or disguise a fourth attempt. Scientific P0/model/
> GPU/result/claim remain 0. A materially distinct acquisition version needs
> explicit human selection or a newly verified external transport change.
> Never use `junjinyong`.

> **2026-08-14 D1 transport attempt 2:** Quality-passed source `0be4d8f…`
> ran as introai9 job `116208.ECE-util1`, CPU 4, 64 GB, GPU 0. Persistent log
> proves compute-node curl 7.58.0 rejected unsupported `--retry-all-errors`
> before any partial object. Exit 2, partial bytes 0, reader/schema 0. This is
> a transport-client compatibility result, not source/data/science failure.
> Final attempt 3 changes only that flag to curl-7.58-compatible `--retry-delay`
> and `--retry-connrefused`; exact objects, hashes, cap and schema remain fixed.
> No further D1 transport attempt exists after attempt 3. Never use
> `junjinyong`.

> **2026-08-14 D1 transport attempt 1:** Exact public source
> `b16ae4b8ebcea99e089034952eb68655b842109a` passed Quality
> `31728458903`. Introai9 CPU/PBS job `116207.ECE-util1` used CPU 4, 64 GB,
> GPU 0 and run count 1, then exited 2 immediately. Only a 17-byte attempt-start
> marker exists; transient/steady partial bytes, persistent PBS log, source
> object, reader and schema verdict are 0. Do not infer the cause or call this
> a data/source failure. D1 permits at most three resumable transport attempts.
> Attempt 2 changes only persistent stage logging and an exit-status trap;
> object URLs, sizes, SHA-256, storage cap, reader/schema and all scientific
> boundaries remain exact. After transport completes, schema cannot rerun.
> Never access/query/transfer/submit/monitor `junjinyong`.

> **2026-08-14 processed-v4 D1 registration:** The user selected a
> materially different processed-only AneuG acquisition, not a repair/rerun of
> closed G0 or historical cycle P0. Official revision `9dd4180…fa36` exposes
> exact transient v4 at 23,744,862,051 bytes/SHA-256 `141541ed…51c9` and
> steady v4 at 9,632,510,050 bytes/SHA-256 `0c03c1d9…0177f`. Official code
> shows transient v4 lacks its own normalization and uses steady `tensor_norm`.
> Keep transient v4 persistent; use steady v4 temporarily to extract only
> label/norm metadata, then delete that full object. Selected-AneuG peak cap is
> 60 GB; v5, per-case raw blood/wall, 14,000-case steady CFD and `cfd/` are
> forbidden. Transport may resume the same immutable partial object for at
> most three PBS attempts only while transport is incomplete; once both
> objects are complete, schema audit gets no rerun. D1 checks weights-only
> metadata, case count, 80 phases, vector-WSS labels, unique case IDs, mesh
> order and local-geometry linkage. It opens only leakage grouping/split freeze,
> never scientific P0, method, GPU or paper result. `introai9` PBS-only, GPU 0;
> never access/query/transfer/submit/monitor `junjinyong`.

> **2026-08-14 AneuG source G0 execution closure:** Exact public source
> `01ae2184facd76c9b2056557263fc92dff22831c` ran once on `introai9` as
> CPU/PBS job `116204.ECE-util1` with CPU 4, 8 GB and GPU 0. It ended state
> E/exit 2 after `00:02:14`; the 408-byte private result SHA-256 is
> `524df994…338` and the raw PBS log is empty. The only reported reason is
> `public_source_request_failed`; the exact request and low-level cause are
> unresolved. Source-feasibility and scientific gates were not evaluated,
> and scientific checks remain 0/0. This is not evidence that AneuG is absent
> or scientifically invalid. The separate acquired-asset observations remain
> valid. The exact G0 is closed with no repair/rerun; scientific P0/P1, field
> access, method, architecture, GPU, validation/test, outer test and paper
> claim remain 0. Any future executable study must be a materially different
> acquired-data task/version. Never access/query/transfer/submit/monitor
> `junjinyong`.

> **2026-08-14 acquired-asset reconciliation beyond the legacy root:** The
> prior “no confirmed AneuG payload” statement was scoped to one legacy
> project tree and must not be generalized account-wide. A separate read-only
> data-tree audit confirms an integrity-checked AneuG geometry archive with
> 14,712 directories and 14,710 complete `shape.obj`/checkpoint/flow-split
> bundles; `stable_5954` and `stable_16384` lack `shape.obj`. It does **not**
> confirm the transient WSS target. BenchAnXplore is fully materialized as 105
> HDF5/XDMF pairs × 80 velocity frames; its audited XDMF exposes coordinates,
> tetrahedra, velocity and wall mask, not direct WSS/pressure. All 105 cases
> already informed historical POD representation selection, so use it as an
> engineering/temporal-head control, not fresh confirmation.
>
> AneuX metadata/models, CMHA 99 aneurysm-patient + 44 control extraction,
> a 24-case Aneurisk image/geometry mirror, Aneumo code/cache history and the
> IntrA repository are also materialized to the stated extents. Never merge
> acquisition with scientific admissibility or count generated directories as
> patients. The headline remains AneuG reference-relative transient WSS after
> source/lineage/target admission. The post-admission implementation scaffold
> is SE(3)-equivariant multi-resolution MeshGraphNet + train-only POD cycle
> head + deterministic tangent projection; this is a performance scaffold,
> not algorithmic novelty or current execution authority. G0 is now closed
> execution-incomplete and may not be repaired or rerun. This audit newly read
> no HDF5 field array, extracted no archive,
> submitted no PBS job and used no GPU. Broad-scan SSH resets are transport
> observations, never evidence of asset absence. Never access/query/transfer/
> submit/monitor `junjinyong`.

> **2026-08-14 AneuG reference-relative structure reappraisal and G0:**
> AneuG-Flow is the conditional primary candidate, not an active training
> split. Exact dataset/code remain `9dd4180…`/`4a090a0…`; the release
> reports 730 transient cases, but generator parent/latent lineage is
> unverified and 730 cases must never be counted as patients. The 2015
> Challenge is an auxiliary within-anatomy inter-solver structural-variability
> floor with five independent anatomies; its 28 submissions are nested solver
> calculations. AneuX is geometry-only morphology/OOD support. Aneumo is
> optional only after mapping/licence resolution and no withdrawn panel may
> reactivate.
>
> The residual question is whether field-error/compute-matched learned
> surrogates add signed critical-point/worldline error beyond solver
> disagreement. CFD variability, Graph U-Net, GNN, equivariance, edge 1-form,
> Hodge/DEC, temporal decoding, tracking and topology loss are direct prior or
> control—not novelty. The fresh score is **31.0/40 inactive** with axes
> 4.5/4.0/2.5/4.0/3.0/5.0/5.0/3.0. Historical AneuG 32.0 is not repaired.
>
> Fresh `aneug_reference_floor_g0_v1` asks a materially different source
> question and never repairs/reruns job `115645`. It inventories the AneuG
> transient tree without field/mesh payload, reports explicit lineage paths
> without inferring independence, verifies the exact Figshare WSS archive and
> safe tar directory without member extraction, and verifies AneuX metadata
> only. Exactly one introai9 CPU/PBS attempt is allowed: CPU 4, 8 GB, GPU 0.
> Any outcome closes without repair/rerun; complete permits human rescoring
> only. Scientific P0/P1, architecture, field access, GPU, test and claim
> remain 0. Never use login-node GPU. Never access/query/transfer/submit/
> monitor `junjinyong`.


> **2026-08-14 source-authority watch v22:** Administrator-confirmed introai9
> recovery does not resolve scientific source authority. V22 extends v21 to 35
> exact states by freezing official Aneumo issue 4, all six comment IDs, owner
> comments, timestamps and body hashes. A live refresh matches 35/35 and opens
> no review signal. This means no new correction exists, not that the mapping
> is authoritative. Any issue/repository/licence change requests a fresh human
> source audit only; it cannot resolve the licence conflict, reactivate
> withdrawn P0 v1, access a field, select a model or authorize GPU. Successor
> P0 remains unregistered; transient WSS remains 30.0/40 inactive. Future
> scientific execution is introai9 PBS-only/no login-node GPU. Never access,
> query, transfer to, submit on or monitor junjinyong.

> **2026-08-13 mapping-integrity withdrawal:** Official Aneumo issue 4 owner
> comment `5070184242` says cases 2158/2159 belong to family 115 rather than
> 114; later comment `5070473308` promises a complete mapping review. Current
> official main remains `701d53d…45a`, the earlier partial correction, whose
> Connection.csv still maps case 2158 to `114_deform_10`. The known case lies
> outside transient 1--1000, so do not declare a selected row wrong, but the
> first 1,000 family labels are not authoritatively verified. Stability P0 v1
> is withdrawn before field access at 0/60; its 12-family panel is immutable
> history and may never activate. A successor requires an authoritative
> corrected mapping, the independent licence resolution, a fresh public
> selection and a new private manifest. Model/method/GPU/result/claim remain 0.
> Server recovery does not resolve source integrity. Never access or query
> junjinyong.

> **2026-08-13 registered non-executable stability P0 v1:** Official
> scientific source `c5f1cb0a2acdb0841398d1ee52ebcb3140b98dfe` passed
> Quality `31711690130` with NumPy 2.1.2, h5py 3.12.1, CPU PyTorch
> 2.5.1, 635/635 tests, site graph and browser JavaScript; Pages
> `31711688753` succeeded.
> Connection.csv SHA-256 09a5344a…d0b and release-directory metadata exclude
> D0 family 1 and field-blindly freeze 12 distinct families, one canonical
> complete case each and phases 4.01/4.25/4.50/4.75/5.00: 60 future members.
> No P0 field has been staged/read. Phase gates for informative structure,
> tangency, pairwise bidirectional signed recall, exact index, count range and
> deterministic 1%-RMS perturbation are non-compensatory; 10/12 families must
> pass 4/5 phases. HF declares CC BY-NC-ND 4.0 while the GitHub datasheet says
> CC BY 4.0. Stricter private handling is not authoritative resolution, so
> staging/execution remain false until clarification and a separate private
> activation manifest. Do not weaken this gate or treat it as a legal
> conclusion. Field/result/method/model/GPU/test/claim remain 0. Never access
> or query junjinyong.

> **2026-08-13 D0 v2 final operational outcome:** Green public source
> `158f6bfa45c9eeac93211b875352a64f69a2e69e` passed Quality
> `31708012464` with 629/629 tests and Pages `31708011675`. Final introai9 PBS
> job `116165.ECE-util1` ran once with CPU 4, 16 GB, GPU 0 and zero PBS HTTP,
> then completed E/exit 0 in 25 seconds. Its two-file raw stage was deleted.
> Keep the exact field-derived aggregate private while release licence
> declarations conflict; public records may expose operational metadata only.
> D0 had no scientific stability threshold and activates no paper evidence.
> Repair 2/2 is consumed; never repair or resubmit D0. A separate prospective,
> family-disjoint method-free P0 must be registered before any new case/phase
> field read. Method, architecture, GPU, test and claim remain closed. Never
> access or query `junjinyong`.

> **2026-08-13 D0 v1 outcome and final transport repair 2/2:** Exact public
> source `148848d065df46160edc233bfa746748e4f00cef` ran once as introai9 PBS
> job `116160.ECE-util1` with CPU 4, 16 GB, GPU 0. It ended E/exit 1 after
> 12:10 because compute-node outbound network returned `Errno 101` before the
> first bounded range response. No VTP payload was obtained; reader/extractor
> and scientific stability are unevaluated. Private 460-byte status SHA-256 is
> `6fa462f0…e0a`. Final repair 2/2 may change only transport: privately stage
> the same two exact hash-verified known members, use zero PBS HTTP requests,
> and delete those two staged files after the attempt. Do not change case,
> phase, array, reader, extractor or threshold. Any v2 outcome closes further
> D0 repair/resubmission. A pass opens only separate family-disjoint method-free
> P0 registration. Model, architecture, GPU, test and paper claim stay closed.
> Never access or query `junjinyong`.

> **2026-08-13 D0 development repair 1/2:** Quality run `31704718929`
> executed 624 tests; 623 passed and the sole failure was a synthetic fixture
> that assigned coordinates and WSS arrays in reverse in the inline-base64
> representation. Swap only those fixture arrays. This is registered bounded
> development repair 1 of 2, not a field read or scientific repair. It changes
> no release member, case, phase, parser behavior, threshold or claim. Preserve
> the failed run and do not reset the repair count.

> **2026-08-13 post-P0 problem re-entry boundary:** Do not repair or relabel
> the closed response-fidelity P0 v3. Its 32.5/40 is source history and its
> scientific state remains execution-incomplete with 0/12 evaluated. The best
> remaining acquired-asset candidate is Aneumo transient structure-faithful
> WSS at **30.0/40 inactive**, not an active paper identity. Hodge Spectral
> Duality, SE(3) wall-WSS networks, RHSIA, critical-point-trajectory
> compression, FaCTz and the 359-lesion aneurysm critical-point study make GNN,
> equivariance, edge 1-forms, Hodge blocks, temporal decoding, tracking and
> topology loss direct prior/control—not novelty. The only residual
> application path is robust target identification, field-error/compute-
> matched structural failure and a minimal mechanism-linked correction.
>
> Current prospective D0 is reader/extractor development only. It reuses exact
> Aneumo case 1 phases `4.01` and `5.00`, already inspected at SHA-256
> `39e0f802…fc3a` / `007c9b72…eff9`; it must not read a new case or phase.
> D0 validates bounded ZIP extraction, fail-closed VTP decoding, two normal
> constructions, two deterministic polygon fans and signed critical-point
> reporting. It has no scientific threshold and cannot establish target
> stability. At most two bounded development repairs are allowed, each tied to
> one encoding, range-extraction or deterministic implementation defect. A
> pass opens only registration of a separate family-disjoint method-free P0.
> Method, architecture, GPU, validation/test, outer test and paper claim stay
> closed. Apply the stricter noncommercial/nonredistribution handling while
> HF `CC BY-NC-ND 4.0` and GitHub-datasheet `CC BY 4.0` conflict; make no legal
> conclusion and publish no raw/derived fields or weights. All execution is
> introai9 PBS-only/no login-node GPU. Never access, query, transfer to, submit
> on or monitor `junjinyong`.

> **2026-08-13 P0-v3 one-shot final outcome:** Exact Quality/Pages-passed public
> source `8252d354e22990f480344327f2fce34cf8016dfa` was activated prospectively
> and submitted once on introai9 PBS as `116146.ECE-util1`. PBS allocated CPU 4,
> 16 GB and GPU 0. The job finalized F/exit 1 after walltime `00:00:34`, CPU
> `00:00:19` and 160,404 kB memory. Only a 313-byte private status at SHA-256
> `4f517743…4c6` materialized; aggregate result and raw PBS output did not.
> Scientific gate evaluated false, so current evidence is execution-incomplete,
> no scientific verdict and 0/12 evaluated—not a 0/12 scientific failure.
> Authorized train-field read extent and low-level cause are unknown and must
> not be inferred. Public execution record SHA-256 is `bbed8806…d82fd`.
> Same-contract repair/resubmission is permanently forbidden. P1, method,
> architecture, GPU, validation/test, outer test, RF-C1--RF-C3 and paper claim
> remain closed. Preserve 32.5/40 only as conditional source history; active
> paper identity is zero. Never access, query, transfer to, submit on or monitor
> `junjinyong`.

> **2026-08-13 introai9 recovery/runtime pre-activation boundary:** Treat the
> administrator report as the verified external operational change. Public-key
> login, an empty user queue, enabled/running `coss_agpu`, exact cache identity,
> storage readability, Singularity 3.11.3 and base-image readability were
> confirmed without an HDF5 array read. The base image has NumPy 2.1.2 and
> PyTorch 2.5.1 but lacks `h5py`; do not submit it alone. Activation schema v2
> must pin the separately verified `h5py==3.12.1` wheel and install it
> network-free with `--no-index --no-deps` into job-local temporary storage.
> Final binary preflight also found no Git executable in the base image. Preserve
> the schema-v2 private manifest as superseded before any attempt/field read.
> Schema v3 must pin that manifest SHA and both zero counters, while the host
> wrapper verifies a clean checkout and passes its exact commit into the clean
> container for runner-side equality validation.
> The wrapper must also preserve the registered wheel's full basename inside
> the container; `h5py.whl` is not a valid wheel filename. The failed no-field
> dry-run is pre-attempt provenance, not a PBS attempt, and must not be hidden.
> Immutable P0 v3 config/evaluator bytes and all 12 gates are unchanged. At this
> source-preparation state the private manifest, field read and PBS attempt are
> still 0. Freeze and push the public runtime source, then register exactly one
> private manifest before the first field-array read. One CPU-only PBS attempt
> is permitted after that; any attempt status forbids same-contract resubmission.
> Never access, query, transfer to, submit on or monitor `junjinyong`.

> **2026-08-13 current-overview public evidence synchronization:** Exact
> consolidation source `b5fd69774e00cf58403c0a0fadfceba8b39fd3e4` passed
> Quality `31689617455` and Pages `31689616910`. Dependency-complete CI records
> 609/609 tests, 115 protocol invariant groups and the README/site semantic and
> link graph pass. README/checker/research-data SHA-256 are
> `1cea2d86ea30a2b2cca9570069c22284b27fb7a51e4dec208007f679de0546b2` /
> `2b0801991ae08aa3a90c1430bec39915917ad3f6a7567676bcfad3d9e17ee551` /
> `619e1ad5d685cbce02526e804f33520fd1579fb42d7f623f4cf4056b87ce9679`.
> These are documentation/code-quality results, not Aneumo evidence.

> **2026-08-13 current-facing documentation boundary:** Keep `README.md` as a
> compact current overview, not a second changelog. It must remain at most 260
> lines, state real P0 v3 0/12, no selected architecture and RF-C2 as an
> application solution, and expose no private path. Route dated evidence to
> `CHANGELOG.md` and the site's filterable History window. Historical 0/11
> records remain exact history and are not rewritten. Team source remains
> unchanged at 2026-08-02 with SHA-256 `ad99ccdc…ab175d` /
> `6d50cb4a…c2b38`; it supplies no fresh architecture or execution evidence.
> This documentation consolidation changes no P0 bytes, scientific result or
> execution authority.

> **2026-08-13 latest-collision public evidence synchronization:** Exact
> scientific source `4f58f9f90cbad68b96058c1c84cb6817730ba69a` passed Quality
> `31686226180` and Pages `31686225742`. Dependency-complete CI recorded
> 609/609 tests and 115 protocol invariant groups; the local canonical protocol
> SHA-256 is `7e3e6a4f81189ea8f8364e36eb19c6a0f3341da43f4e806e68948eda55d12739`.
> Collision config/test/audit SHA-256 are
> `f217b90daa248592d12db30e33f91f3122da92f1db3e2830ef183c7f53d959f2` /
> `120fa44e2ab04460b8084715997cdc2de613a0451dda880d216b6041d3897989` /
> `1f4c737454ed423a91e5511295033e912e99e48d3c6750c06401f32f1b5f62ce`.
> These are code/provenance results, not Aneumo scientific evidence. Real P0
> v3 remains 0/12; no scientific server/scheduler/cache-field query, transfer,
> PBS/GPU submission or monitoring occurred.

> **2026-08-13 latest response-fidelity collision recheck:** Preserve
> `configs/aneumo_response_fidelity_latest_collision_recheck_v1.json` and
> `docs/aneumo-response-fidelity-latest-collision-recheck-2026-08-13.md` as the
> current claim boundary. PaNO (`arXiv:2606.03038`) owns generic global-field
> versus downstream-readout mismatch; NOEM
> (`10.1038/s43588-026-00974-2`) owns generic hard-constraint neural-operator
> output transformations; differentiable cardiovascular BC tuning
> (`10.1007/s10439-026-04269-5`) owns one-high-fidelity-CFD repeated-BC tuning.
> Do not claim any of those, or GNN/equivariance/residual/response loss, as
> novelty. Retain 32.5/40 with novelty exactly 2.5/5 only for the Aneumo-
> specific bilateral field-error-matched audit, learned-direct and analytic
> controls, and exactly-100-new-family evidence. RF-C2 is an application
> solution, not a general method contribution; no method name is active.
> Real P0 v3 stays 0/12 and active method/architecture/paper identity/result/
> claim remain 0. This public-source audit is not a verified `introai9`
> operational change: do not retry, register a manifest, or open a local
> scientific repair loop. Never access, query, transfer to, submit on or
> monitor `junjinyong`.

> **2026-08-13 ISBI 2027 author-contract correction:** Official home page
> `1019` (modified `2026-07-29T11:16:41`), author page `1026` (modified
> `2026-07-22T10:39:56`) and CFP SHA-256 `0aed86f4…38a14` confirm the
> four-page archival deadline and disclosure contract. Apply the conservative
> union of the official originality clauses: no substantially similar
> conference/workshop/journal concurrent review. The author-page template ZIP
> SHA-256 is `3acdec37…13d7`, but its internal README says `ISBI 2021 Paper
> Submission Templates`; do not call it a 2027-specific template. The private
> vendored `spconf` active-command stream matches upstream at
> `c9998f06…766f7`, but comments differ and the current plan uses `unsrt`, not
> `IEEEbib`. Therefore classify it only as an organizer-linked-layout internal
> pre-evidence shell. Preserve its sealed scientific bytes; do not relabel it
> final-format or submission-ready. Recheck and rehash the then-current
> organizer template before submission. This format audit is not scientific
> evidence or an `introai9` operational change. Real P0 v3 remains 0/12; do not
> retry or open a local repair loop. Never access `junjinyong`.
> Exact source `67ccdd9c0bc740d5763d23a7a4728b9018aefbbf` passed Quality
> `31682965397` and Pages `31682964734`. Quality verified NumPy 2.1.2,
> h5py 3.12.1, CPU PyTorch 2.5.1, all 606 tests, 114 protocol invariant
> groups, the site graph and browser JavaScript syntax. This is format/source
> integrity evidence only.

> **2026-08-13 Aneumo transient whole-release target-contract audit:** Current
> transient decision is **30.0/40, inactive**, superseding the earlier
> source-level 28.0 score without rewriting it. A fail-closed audit at exact HF
> revision `f801adee816c18d3e18b23e6fcb147fe4c264209` used 2,100 range requests,
> 72,217,600 bytes and a 100,000,000-byte ceiling to inspect every case ZIP
> directory from 1 to 1000. It found 966 complete `4.01`--`5.00` cycles, 34
> incomplete/alternate sequences, 961 complete cases with canonical wall names
> and five complete cases with noncanonical wall names. All 40 base families
> have at least one complete and one official-preprocessor-compatible case.
> The release-wide audit read zero inner scientific members.
> Raw audit JSON/canonical case-record SHA-256 are `f3b90977…4962a` /
> `8f516cd3…de424`. Current compact decision/auditor/two test files/audit-document
> SHA-256 are `8086224f…720b6` / `db2ba604…1f9f0` /
> `ae07e7ca…7c0a` / `eef3525d…a09` / `be26643d…22821`.
>
> A distinct selective probe read four CRC-checked wall members: complete case
> 1 phases `4.01`/`5.00` and partial case 7 phases `0.20`/`0.26`. Both point and
> cell data expose three-component `wallShearStress`; case 1 point/connectivity/
> offset bytes are phase-identical while WSS differs. Never generalize four
> files to release-wide units or tangency. Units are unspecified, faces have
> 4--9 vertices and case-1 Newell-normal WSS p99 is about 0.34, so deterministic
> triangulation, mesh quality, normal convention and perturbation stability are
> unresolved. HF CC BY-NC-ND 4.0 versus GitHub CC BY 4.0 remains an unresolved
> licence conflict; make no legal conclusion.
>
> This improves target/asset readiness only. Equivariance, GNN, edge 1-form,
> Hodge, periodic decoding, critical-point tracking and worldline/topology loss
> remain controls/direct priors. No transient P0, method, architecture, data
> staging, GPU, outer test, result or paper claim is authorized. The sole
> conditional lead remains steady response fidelity 32.5/40 with immutable real
> P0 v3 0/12. This audit is not an `introai9` operational change; do not retry
> before one and do not open a local scientific repair loop. Never access,
> query, transfer to, submit on or monitor `junjinyong`.
> Targeted 19/19, site graph, JavaScript syntax and diff hygiene pass. The local
> full regression passes 590/590 with 89 optional-dependency skips after a
> writable-temp rerun; the earlier sandbox run's 38 errors were exclusively
> `TemporaryDirectory` environment failures and must not be labelled code
> failures or dependency-complete CI.
> Exact scientific public source
> `b06f83fa3b3339de601f1230b25d60f18ab25b68` is remote exact. Quality
> `31680411009` and Pages `31680410157` succeeded. Public Quality job
> `94384352300` reports every configured dependency, pinned-runtime, protocol,
> full test, site-graph and browser-JavaScript step successful. This CI validates
> source integrity only and does not change the 30.0 inactive decision or open
> any scientific execution authority.

> **2026-08-13 official Aneumo transient-release scientific-source
> validation · historical source-level score:** Exact scientific public source
> `86ad5923d56202d9bd8a1748aabdf0783789c142` is remote exact. Quality
> `31675906790` passed NumPy 2.1.2, h5py 3.12.1, CPU PyTorch 2.5.1, all
> 588 tests, 114 protocol invariant groups, the site graph and browser
> JavaScript syntax; Pages `31675905793` succeeded. Reappraisal config/test/
> audit-document SHA-256 are
> `2e8377d523a17bf152f2d2489166df1755f3dc7e4a55a36af3ab0d9dac20bff1` /
> `721b3529ea1a9352f3b0efc6cf69afde363cb9bd0372e3fd9c4caef551eeecd3` /
> `283e19afe072fd51221baaaa4ff3cac0ff27b2cb8f59e90fea84e4d111a6a559`.
> This validates the public source/audit contract, not the transient target or
> the steady P0. Its 28.0/40 transient score is preserved as the historical
> pre-whole-release verdict and is superseded for current decisions by 30.0/40;
> the sole conditional lead remains steady response fidelity 32.5/40 at real
> P0 v3 0/12. This synchronization made zero scientific server query, remote command,
> cache-field read, scheduler query, transfer, PBS/GPU submission or monitoring.
> Do not retry `introai9` before a newly verified operational change or open a
> local scientific repair loop. Never access `junjinyong`.

> **2026-08-13 official Aneumo transient-release reappraisal · historical
> one-case probe:** Freeze GitHub
> commit `701d53dde3489d84dbe9bc8324254629162eb45a` and Hugging Face revision
> `f801adee816c18d3e18b23e6fcb147fe4c264209`. HF exposes 370 objects and
> 3,284,946,024,600 bytes: 267 numeric steady ZIPs, 100 transient batch ZIPs and
> three metadata files. The first transient batch is 14,530,202,660 bytes. A
> bounded 16 MiB ZIP-directory probe, not a full download, found ten nested case
> archives; inspected case 10 has 101 time directories (`0.00` plus 100 labels
> `4.01`--`5.00`) and four inlet/internal/outlet/wall members per directory. No
> field value was interpreted. `Connection.csv` maps released case IDs 1--1000
> to only 40 base families, 3--30 deformations each. Never call cases, phases,
> points, critical points or tracks independent units.
>
> The official cross code reduces vector WSS to magnitude and its declared
> geometry split shares all ten base families across train and test. It reports
> only scalar field metrics, has one Python parse error, references two absent
> model modules and uses data-dependent divergence truncation. Do not relabel
> it as a family-disjoint vector baseline. HF declares CC BY-NC-ND 4.0 while the
> GitHub datasheet declares CC BY 4.0; make no legal conclusion and require an
> authoritative resolution before scientific activation or redistribution.
> The then-current transient structure-faithful WSS score of 28.0/40 remains
> exact history and is superseded by the 30.0 whole-release verdict above. This
> source delta satisfies only historical material-E0
> review, not task P0 or introai9 service recovery. The sole conditional lead
> remains steady response fidelity at 32.5/40; real P0 v3 is 0/12. Transient
> staging/P0/model/GPU/claim remain zero. Never access `junjinyong`.

> **2026-08-13 current-facing consistency boundary:** Public current-state
> summaries must say P0 v3 `0/12`, cache identity resolved, private activation
> manifest absent and current container readability unverified. The current
> independent-confirmation gate is inactive v3 with direct and power-law
> controls; v1/v2 remain historical. Do not bulk-relabel dated lineage rows,
> historical configs or failed runs. This wording synchronization changes no
> protocol bytes or execution authority and permits no introai9 retry. Never
> access `junjinyong`.

> **2026-08-13 P0-v3 activation implementation boundary:** Preserve the
> immutable v3 config/evaluator hashes `1c7cc85d…fcc81` / `51a7db66…1d25`.
> The historical response-fidelity PBS wrapper is v2 provenance and must never
> execute v3. The public activation runner SHA-256 is
> `492c842f27777f0e235ce02cab4f6051993edd425859e6ddf67e8f187c920a9c`;
> its tests and v3 PBS wrapper SHA-256 are
> `ed97014d27faaf470d66842fc643f8ae8c558af3e5c62bad84e38b8d767395e4` /
> `a5e288d63ae5d59fc7ecfd83026de4ca86e503cd524cc4f61956f1da63daca1d`.
> These bytes implement a future separate private-manifest binding; they do
> not register one. Do not create that manifest until a verified introai9
> operational change and container/cache readability evidence exist. It must
> be registered before any v3 field read, pin its own bytes, and report zero
> prior P0-v3 scientific attempts. Current manifest/PBS/cache-field/scientific
> result remain 0 and real P0 is 0/12. Do not retry locally or access
> `junjinyong`.

> **2026-08-13 schema 11.9 · current P0 is v3 with 12 checks:** Preserve
> unexecuted P0 v2 config SHA-256 `b82b3bfd…1381` and evaluator SHA-256
> `3f966732…2790` byte-for-byte. A deterministic 5,000-replicate
> family-cluster bootstrap
> negative control showed v2 11/11 pass while the omitted anchor-tangent median
> was `0.7987704542950331`; this is contract evidence only, not an Aneumo or
> model result. Current v3 config/evaluator SHA-256 are
> `1c7cc85d…fcc81` / `51a7db66…1d25`; it adds the independent anchor tangent
> CI-lower ≥0.80 check. Real status is 0/12. Do not edit or activate historical
> P1/confirmation v1--v3; only a real v3 12/12 pass may authorize registration
> of a fresh P1 evidence version. A user-supplied exact inventory now resolves
> the private cache identity and registered SHA-256; schema only was reported
> read. The path and infrastructure metadata stay in a private ledger and must
> never be copied to this public repository. Do not edit v3 in place. A separate activation manifest remains
> absent because this session's bounded Windows SSH attempt was reset before a
> remote command and container readability is unverified. No transfer,
> scheduler query, PBS submission, field-array read, monitoring, or GPU action
> occurred. Retry only after a newly verified introai9 operational change and
> never access
> `junjinyong`.

> **2026-08-13 Quality coverage failure preserved and v2 correction
> verified:** The first changelog-only remote Quality run `31624153346`
> succeeded but discovered only 560 tests with 85 optional skips. Coverage v1
> source `96770ad5e7d874ae2353864da18eaad1724ddcef` then installed NumPy/h5py;
> Quality `31624605016` correctly failed after discovering 561 tests because
> three now-active array checks reached a shared runtime import that also
> requires PyTorch. Do not relabel either run dependency-complete. Coverage v2
> source `5d6f8703edac82e872056a177cadb2fb3999c540` pins the previously
> documented contract runtime: NumPy 2.1.2, h5py 3.12.1 and CPU PyTorch
> 2.5.1. Quality `31625071586` verified the versions and passed all 570 tests
> with zero errors; Pages `31625071537` also succeeded. This is CI coverage
> only and opens no scientific authority, data access or experiment.

> **2026-08-13 residual-novelty scientific synchronization:** Exact scientific
> public source `1cdc360170739894dde6bd71508ade76ed7fb90e` passed Quality
> `31621343028` and Pages `31621342151`. Dependency-complete regression passes
> 570/570; the machine protocol retains 112 invariant groups at canonical
> SHA-256 `76dfe06a0c05130e68dd2c47a07c0db5dad4cbfa0462c57e195c05ed2983fde4`.
> `CHANGELOG.md` and the site's filterable `changes` ledger must expose this
> same decision; lineage-only publication is insufficient. The separate
> private planning ledger is synchronized while manuscript and reference bytes
> remain unchanged. This provenance opens no P0/P1, method,
> model, server, PBS/GPU, outer test, result or claim. No scientific server was
> queried. Do not retry `introai9` before verified external change; never
> access `junjinyong`.

> **2026-08-13 residual-novelty audit:** Fresh acquired-asset/direct-prior
> review lowers the Aneumo response-fidelity lead from historical 34.0 to
> 32.5/40; novelty remains exactly 2.5/5. General interventional consistency and
> aneurysm perturbation-response surrogation are occupied. The only residual
> conjunction is an observed Aneumo-specific matched-field response failure,
> one same-backbone identity-at-anchor mechanism, superiority to learned direct
> and analytic power-law controls, and exactly-100-new-family confirmation.
> Alternative acquired-asset rows score 30.5 or lower and are rejected. Real
> P0 remains 0/11; exact cache path, active split, method, architecture, server,
> PBS/GPU, outer test, result and claim remain zero. Do not retry `introai9`
> before verified external change; never access `junjinyong`.

> **2026-08-13 schema 11.8 inactive independent-confirmation v3:** Preserve v2
> unchanged and supersede it with eligibility metadata/field/prediction all zero.
> Exact scientific public source `9efe9145e86086f951242fa86340b19020676157`
> passed Quality `31617703039` and Pages `31617702307`; remote main was exact.
> Current v3 config/validator SHA-256 are
> `f9d52aeb2abd9832289db4852ab7dfec03db125093762e5f515ceebd43018226` /
> `d42e99fcea13eabe9f4a7bf8336487c5b7876c02e742031bcfb039a3325edccd`.
> A candidate must be bilaterally field-equivalent within ±`log(1.02)` to both
> same-backbone direct and train-fitted power-law controls, then improve paired
> response and tangent error by at least 10% against both. All four response
> contrasts independently require bootstrap lower >0, ≥4/5 positive seeds and
> ≥59/100 family wins. Never demote a failed analytic control.
> Derive evidence only from complete
> `family×case×5 seed×3 model×3 metric` rows. Missing, duplicate, extra,
> nonfinite or negative rows and non-identical replicated power-law seed rows
> close the execution without verdict. Use one SHA-256 counter family-bootstrap
> stream, shared draws, 10,000 replicates and Hyndman--Fan type-7 quantiles.
> Figure ranking uses the weaker direct/power-law response contrast and shows
> reference/direct/power-law/candidate under matched display settings.
> Dependency-complete regression passes 570/570; protocol retains 111 invariant
> groups at canonical SHA-256
> `d3d1d6d9c066511f5bac6ef97a64c737b9db9c40de0f6c3b3de10996f6f763f6`.
> Real P0 remains 0/11; eligibility metadata, manifest, field, prediction,
> model, server, PBS/GPU, result and claim remain zero. Never access
> `junjinyong`; do not retry `introai9` before verified external change.

> **2026-08-13 schema 11.8 inactive independent-confirmation v2:** Preserve v1
> unchanged and supersede it before confirmation metadata/field/prediction
> access. Current v2 config/validator SHA-256 are
> `570bbca4218e1ef22f681c8e308c012b62f92a93807a92dc4953226342f64481` /
> `7c6dca01253dc7494ba013f72b0c2aee7a7c8ea49fc24e7215fdde97431a0564`.
> Aneumo reports 427 base geometries; excluding historical 32 leaves at most
> 395, so exactly 100 is same-release expansion, not new-dataset search. Before
> outer field access, both final-candidate development response SDs must be
> ≤0.2981054601 and the complete case-flow×2-model×5-seed projection must be
> ≤40 GPU-hours. Case log-error ratios aggregate through five seeds to one row
> per family. Both responses additionally require one-sided Wilson lower >0.5,
> i.e. at least 59/100 family wins. Aneumo flow diversity and Hemo-MPO geometry+
> BC full-field learning are direct priors; multi-flow/operator/component-stack
> novelty is forbidden. Current viability/metadata/field/prediction/server/PBS/
> GPU/result/claim are 0; real P0 remains 0/11. Never access `junjinyong` and do
> not retry `introai9` before verified external change.
> Dependency-complete regression passes 561/561 tests; protocol retains 111
> invariant groups at canonical SHA-256
> `4e37a1d3bdcda6456d7de07bbdaa5d8ad51022fb161fdbb58063f712a5293b1a`.

> **2026-08-13 schema 11.8 confirmation/private synchronization:** Exact
> scientific public source `d82745261c9b62e182a9b82f03207b90b3733960`
> passed Quality `31610409552` and Pages `31610409674`. Private planning head
> `b35a597cdc69694a4b965b6f32d11256e9e9c45c` is remote exact, PRIVATE and
> anonymously 404. Manuscript/reference SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` /
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> No title, abstract claim, method, result row, figure or C21 is active. This
> synchronization queried no scientific server and used no transfer, PBS/GPU
> or monitoring. Real P0 remains 0/11; never access `junjinyong` and do not
> retry `introai9` before verified external change.

> **2026-08-12 schema 11.8 inactive independent-confirmation v1:** Supersede
> the vague historical ≥50-family phrase before any confirmation access. The
> current non-authoritative template is
> `configs/aneumo_response_fidelity_confirmation_template_v1.json`, SHA-256
> `aa2cf90f9b1d34ecf74f94ef8eb88559671458e126ab5004d1ae24024bc910ec`;
> validator SHA-256 is
> `a03c9b754fc857298a6b8a136d7651edfcaa17092f9551b1a40cdd03a0958aac`.
> It excludes all historical 32 families, requires exactly 100 new families,
> uses all eligible cases/eight flows and averages node→flow→case→five seeds
> before 10,000 family bootstraps. Field non-inferiority, power-law competence
> and both response-superiority endpoints form one intersection–union pass.
> Candidate worst/typical/best figure roles are predeclared. No family
> substitution, sample enlargement, partial aggregation or favourable-only
> visualization is allowed. The 40 GPU-hour value is a future inference-only
> ceiling, not authority. Current qualified new family/manifest/metadata/field/
> prediction/server/PBS/GPU/result/claim are 0. Real P0 remains 0/11; never
> access `junjinyong` and do not retry `introai9` before verified external change.
> Dependency-complete regression passes 552/552 tests; protocol retains 111
> invariant groups at canonical SHA-256
> `6851f372fe52ef10e069b34b59e6997b96db93bcf1fcd315d59eb7b4845c2050`.

> **2026-08-12 schema 11.8 P1 v3/private synchronization:** Exact scientific
> public source `0f443c8d68f5d8dced3b9e092a1f6e3bb0b8a723` passed Quality
> `31606655510` and Pages `31606655150`. Private planning head
> `bed6cb5d867a4f7ca28993bb9dda6da74b47ad6d` is remote exact, PRIVATE and
> anonymously 404. Manuscript/reference SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` /
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> No title/abstract/method/result/figure/C21 is active. No scientific server,
> transfer, PBS/GPU or monitoring occurred; real P0 is 0/11 and P1 remains
> unregistered. Never access `junjinyong`; do not retry `introai9` before a
> verified external change.

> **2026-08-12 schema 11.8 direct-prior-complete P1 v3:** SC-FNO already owns
> the generic solution-accuracy/sensitivity mismatch and sensitivity loss;
> Hemo-MPO owns Aneumo SE(3) mesh encoding + physics constraint + DeepONet;
> AB-GATr owns base-anatomy-stratified equivariant Aneumo comparison. Do not
> claim GNN, equivariance, physics loss, DeepONet, sensitivity supervision or
> their combination as AURORA novelty. Preserve unexecuted P1 v2 unchanged.
> Current inactive P1 v3 is
> `configs/aneumo_response_fidelity_p1_template_v3.json`, SHA-256
> `fb18827b6153422f2e97c7cf6151c653b0490f09e2942572c064dc1ea66adbc0`;
> validator SHA-256 is
> `5b73037fa6320c2d39de80b5415e176625b6c259dbfc0db53223ebd9e457253c`.
> Its sole primary pair shares one pinned LaB-GATr backbone and changes only
> direct target-field versus `v0 + log(q/q0) * residual` output. Only positive
> `log(direct error / residual error)` may pass both co-primary endpoints;
> negative/mixed evidence closes the direction without narrative reversal.
> Source-only Hemo-MPO/AB-GATr are not silently treated as executable controls.
> MLP/DeepONet/MeshGraphNet are descriptive and non-rescuing. Post-P1
> development, if separately registered, is validation-only, maximum two
> rounds and 80 additional GPU hours, followed by fresh-seed/disjoint-split
> re-entry. Real P0 remains 0/11; P1/model/server/PBS/GPU/outer test/result/
> claim remain 0. Do not retry `introai9` before verified external change and
> never access `junjinyong`.
> Dependency-complete regression passes 544/544 tests; protocol retains 111
> invariant groups at canonical SHA-256
> `d3b368f7171a9dd900bd81e6e11dc0db98fba9fded21b1b301a47dc01b4f8c02`.

> **2026-08-12 schema 11.8 P1 v2/private synchronization:** Exact scientific
> public source `8b288c0f6edacc4721f06bbd2a3cb21e73d83146` passed Quality
> `31601736993` and Pages `31601736273`. Private planning head
> `83fc88618ca98707ba09540a4686b18c93085819` is remote exact, PRIVATE and
> anonymously 404. Manuscript/reference SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` /
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> No title/abstract/method/result/figure/C21 is active. No scientific server,
> transfer, PBS/GPU or monitoring occurred; real P0 is 0/11 and P1 remains
> unregistered. Never access `junjinyong`; do not retry `introai9` before a
> verified external change.

> **2026-08-12 schema 11.8 inactive P1 v2 red-team:** Preserve unexecuted v1
> template/validator at SHA-256 `07d7b89e…32d06` / `b14e4c8d…4d9fa`.
> Current non-authoritative v2 is
> `configs/aneumo_response_fidelity_p1_template_v2.json`. It requires distinct
> checkpoint assignment across three iso-levels, fixes the median level's two
> endpoints as co-primary and makes low/high levels non-rescuing sensitivity.
> Cross-fit overlap prohibits exact sign-flip, Holm, nominal-coverage and
> formal-power claims. V2 also fixes response log-ratio direction and zero-seed
> tie handling, and defines power-law field competence as a one-sided 95%
> stability upper model/control log-error ratio ≤ `log(1.02)`. V1 had no
> execution, prediction or response read. V2 is also non-executable; real P0
> remains 0/11 and P1/model/GPU/claim remain 0. This update makes zero server,
> transfer, PBS/GPU or monitoring action. Never access `junjinyong`; do not
> retry `introai9` before verified external change.
> Dependency-complete regression passes 536/536 tests; protocol retains 111
> invariant groups at canonical SHA-256
> `df65f22a1c3500effe5fc585201eb191560d70549897d1f413c661d534b5166d`.

> **2026-08-12 schema 11.8 inactive P1/private synchronization:** Exact public
> scientific source `fdef0955907cd7ec617a924e13c92c47dd2df205` passed Quality
> `31597528606` and Pages `31597524201`. Private planning head
> `62f5664156178290dda3753a67996b94eab15a87` is remote exact and anonymously
> 404. Manuscript/reference SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` /
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> No title/abstract/method/result/figure/C21 is active. No scientific server,
> transfer, PBS/GPU or monitoring occurred; real P0 is 0/11 and P1 remains
> unregistered. Never access `junjinyong`; do not retry `introai9` before a
> verified external change.

> **2026-08-12 schema 11.8 inactive P1 design hardening:** Public
> historical `configs/aneumo_response_fidelity_p1_template_v1.json` is a
> superseded, non-authoritative and non-executable template—not P1
> registration. It fixes historical-train-20
> family cyclic 5-fold 12/4/4 fit/calibration/outer rotation; response-blind
> log-field iso-error levels 25/50/75%; one mechanism-linked primary model pair;
> exact log(1.01) outer field equivalence; six-cell Holm FWER 0.05 with exact
> family sign-flip tests; ≥10% response gap; 4/5 seed direction;
> 2M±10% parameters, 20,000 update budget and 160 GPU-hour cap. Historical
> validation/test and future confirmation families remain sealed. Validator
> synthetic tests are code checks only. Real P0 remains 0/11, so P1/model/GPU/
> claim stay 0. This update makes zero server/PBS/GPU action. Do not retry
> `introai9` before verified external change and never access `junjinyong`.
> Full dependency-complete regression passes 526/526 tests; protocol retains
> 111 invariant groups at canonical SHA-256
> `f963f06f28109f0abe8403e2baeda8191d26d1c0c0a4a55a686fc05ab90729cf`.

> **2026-08-12 schema 11.8 P0-v2/private synchronization:** Exact v2 public
> source `5e431f87c996f354ac5ed6aaa62cb1dd2fadac56` passed Quality
> `31594279674` and Pages `31594278998`. Private paper head
> `a2eedb4d970b4895bb7050f8bdf7e061ad19053f` is remote exact, PRIVATE and
> anonymously 404. Manuscript/reference SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` /
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 516/516 with 111 invariants. Real P0 is 0/11 and no
> server/PBS/GPU/model/test/claim opens. Never access `junjinyong`; do not
> retry `introai9` before verified external change.

> **2026-08-12 schema 11.8 final pre-execution P0 v2:** Preserve unexecuted v1
> `configs/aneumo_response_fidelity_p0.json` at SHA-256 `07c0c897…135f`.
> A rank-preserving 8× coordinate-half response distortion passed v1's
> Spearman-only gate, so v1 is prospectively superseded before data/job/result.
> Current v2 is `configs/aneumo_response_fidelity_p0_v2.json`, SHA-256
> `b82b3bfd3d83713f375378f471ec506e7b8437fd470e98366534d4cb1d021381`.
> It retains within-flow family-rank CI lower ≥0.80 and adds family-bootstrap
> coordinate-half symmetric-relative-difference CI upper ≤0.25. It also hashes
> actual cache bytes and bind-mounts the frozen host path unchanged. Evaluator/
> wrapper SHA-256 is `3f9667329b2f7f61850eddbd5b118c8cab0520cccb86a3382ecfebf6cc292790` /
> `d895fa85926cdbd70f7d9b152cc8ace9e91eced1a943d2889c5c398511d6b6ee`.
> V2 has 11 checks and finalizes pre-execution red-team; further metric or
> threshold changes require a new evidence version. Real P0 is 0/11; no server,
> PBS/GPU, P1, model, test or claim. Never access `junjinyong`; do not retry
> `introai9` before verified external change.
> Full dependency-complete regression passes 516/516 tests; protocol retains
> 111 invariant groups at canonical SHA-256
> `3e43a5773eb8c4c6b3e47fa82ee97fb1b796cc380d9031ade5af250d14c6eb7a`.

> **2026-08-12 schema 11.8 tangent-correction/private synchronization:**
> Exact corrected source `7c48574199e330c2b55ffb29836ede4fee8cfc4b`
> passed Quality `31592497232` and Pages `31592496090`. Private paper head
> `b4e78f845f46c0443a1f3572ca80125bfb9586a3` is remote exact, PRIVATE and
> anonymously 404. Manuscript/reference SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` /
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 514/514 with 111 invariants. This update used no
> scientific server, transfer, PBS/GPU or monitoring and opens no result or
> claim. Never access `junjinyong`; do not retry `introai9` before external
> change.

> **2026-08-12 schema 11.8 pre-execution P0 metric correction:** A red-team
> negative control showed that replacing an omitted flow and comparing the
> centered derivative at that same grid point can be insensitive on an equally
> spaced stencil. Before any private row, job or scientific endpoint, the
> evaluator was corrected to compare actual left/right one-sided velocity
> tangents with the two-neighbour secant. Registered thresholds, split,
> bootstrap seed/count and stop rules are unchanged. Smooth synthetic response
> passes; deliberately jagged response falls below tangent agreement 0.80 and
> above interpolation error 0.35. Evaluator SHA-256 is now
> `9ce64f931f779d9679ba26924d27a43916fc9d6f902c27a473465361cd2849ba`.
> Real P0 remains 0/10 and no server/scheduler/transfer/PBS/GPU action occurred.
> Do not retry `introai9` before verified external change; never access
> `junjinyong`.
> Full dependency-complete regression passes 514/514 tests; protocol retains
> 111 invariant groups at canonical SHA-256
> `635fcbd5d2655d7db7c708db3e8098a282527c7c7f3d94d1df03aa912713d773`.

> **2026-08-12 schema 11.8 implementation/private synchronization:** Exact
> public scientific source `3332bf605d7be8e200009a9cb165b58e6a27cbeb`
> passed Quality `31591274490` and Pages `31591274071`. Private paper head
> `bd71c81f9ef6bf73f6380832bee936ba8c8812d2` is remote exact, PRIVATE and
> anonymously returns 404. `paper/main.tex` and references remain byte-for-byte
> at SHA-256 `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full public regression passes 513/513 tests with 111 invariant groups. No
> scientific server/scheduler query, transfer, PBS/GPU job or monitoring was
> used. P0 result/P1/method/model/outer test/claim remain 0. Never access
> `junjinyong`; do not retry `introai9` before a verified external change.

> **2026-08-12 schema 11.8 P0 implementation boundary:**
> `src/aurora/aneumo_response_fidelity_p0.py` and
> `cluster/pbs_aneumo_response_fidelity_p0.pbs` implement the registered
> aggregate evaluator and a CPU 4/GPU 0 one-shot wrapper. Protocol-pinned
> SHA-256 values are `9ce64f931f779d9679ba26924d27a43916fc9d6f902c27a473465361cd2849ba`
> and `d1341ca525176484ea51619967df50197f3f10381486f517a182df27b3f95974`.
> Synthetic tests exercise all 10 checks; registered real-data bootstrap count
> remains 5,000. Coordinate halves compare within-flow family ranks, not the
> trivially ordered flow sequence. Current config must refuse before cache
> access and the wrapper is not submittable. No scientific server/scheduler
> query, transfer, PBS submission, monitoring or GPU action occurred. P0
> result/P1/method/architecture/outer test/claim remain 0. Never access
> `junjinyong`; do not retry `introai9` before a verified external change.
> Full dependency-complete regression passes 513/513 tests. Protocol validation
> retains 111 invariant groups at canonical SHA-256
> `fa6fb500606f1d52895042c25e78ba24ce757780493f4b7068d4ce5159b1cab1`.

> **2026-08-12 schema 11.8 public/private/site synchronization:** Exact
> scientific source `6512dfb83483ebfee8999f6e72717b096f46b8f3` passed Quality
> `31587974877`. Exact response-fidelity Overview head
> `fc12db9b28e1fa632c49b87667eed37b077bb2f0` passed Quality
> `31588829344` and Pages `31588828745`; the live Overview and Learn pages
> expose schema 11.8. Private paper head
> `82dd511d8747015cb5a902891ea01d6791471b0b` is remote exact and anonymous API
> returns 404. Manuscript/reference SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` /
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 505/505 pass in the dependency-complete environment;
> dependency-light CI retains its declared optional-dependency skips, and
> protocol validation has 111 invariant groups. Title, abstract claim, method, result table,
> figure and C21 remain inactive. This synchronization queried no scientific
> server and used no transfer/PBS/GPU. Never access/query/transfer/submit/
> monitor `junjinyong`; do not retry `introai9` before an external service
> change.

> **2026-08-12 response-faithful Aneumo direction · schema 11.8:** Fresh
> acquired-asset screening admits only
> `field_error_matched_multi_flow_response_fidelity` at 34.0/40 with residual
> novelty exactly 2.5/5. It is a CFD sensitivity-sweep application after one
> nominal same-case solve, not rupture risk, patient-specific physiology, WSS
> or clinical utility. Primary paper identity, method and architecture remain 0.
>
> The verified compact contract is Aneumo 32 generation families × two cases ×
> eight flows × 4,096 aligned nodes with the historical 20/6/6 family split and
> cache SHA-256 `9640b0ef…ab9`. Historical unit string `aneux_base_family` is an
> Aneumo `Connection.csv` lineage key, not the separate AneuX rupture dataset.
> Active train/validation/test remains 0/0/0 because the current exact private
> path is unresolved.
>
> Historical v1 `configs/aneumo_response_fidelity_p0.json` SHA-256
> `07c0c89799e04fbee88a1218383aa7b7fd8fc3a5ab8d7bcb15d286195571135f` is a
> train-only, method-free, CPU-only, non-executable P0 superseded before
> execution by the current v2 contract. V2 audits response
> magnitude/direction/tangent/curvature under node-hash halves and leave-one-
> interior-flow interpolation. It cannot read pressure, validation/test fields,
> models, checkpoints or predictions and cannot use a GPU.
>
> P0 pass authorizes only registration of a development-only, field-error-
> matched P1. If P1 does not observe a response-fidelity mismatch, close the
> direction. Only P0+P1 may open an analytic anchor-scaling plus zero-at-anchor
> residual hypothesis. GNN, SE(3), DeepONet/FNO, DeltaPhi, derivative losses
> and boundary tokens are controls/implementation, not novelty. The historical
> ≥50 confirmation minimum is superseded by exactly 100 new base families with
> all historical 32 excluded and locked before field read.
>
> This update performs zero scientific-server query, transfer, scheduler/PBS
> submission and GPU use. Do not retry `introai9` inventory before an external
> service/admin change. Future authorized execution is `introai9` PBS-only with
> no login-node GPU. Never access, query, transfer to, submit to or monitor
> `junjinyong`. Manuscript title/abstract/method/result/figure remain unchanged.

> **2026-08-12 schema 11.7 scientific/private synchronization:** Exact public
> scientific source `3bad0861aa46a32855e5868811473f45fd0e57f1` passed Quality
> `31584127030` and Pages `31584126536`. Private paper head
> `2323d7f18c6d71a160374f63608a8095c577090f` is remote exact, PRIVATE and
> anonymous API returns 404. Full regression is 486 tests: 420 pass/66
> optional-dependency skip; protocol has 110 invariant groups. Manuscript and
> references remain byte-for-byte at SHA-256
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This provenance opens no active lead, P0/P1, method, model, result, GPU,
> outer test or claim. No scientific server was queried; never access/query/
> transfer/submit/monitor `junjinyong`.

> **2026-08-12 AneuX direct-prior closure · schema 11.7:** Preserve the
> schema-11.6 33.0/40 score and P0 v1/v2 bytes as history. The fresh AneuX
> reliability batch is rejected at 32.0/40 because residual novelty is 2.0/5,
> below the fixed 2.5 floor. AneuX morphology/cut robustness, dome/cut1
> PointNet++ evaluation, DiffusionNet discretization robustness, perturbation-
> based radiomics reliability and preprocessing multiverse analysis are direct
> prior. The frozen implementation also lacks source-qualified patient/lesion
> identity and a single-connected-open-surface gate. Do not repair, execute or
> promote v2 and do not create v3 for this direction. Active lead, P0/P1,
> method, architecture, GPU, outer test, result, C21 and paper claim are 0.
> This update queried no scientific server. Future authorized execution remains
> `introai9` PBS only; never access/query/transfer/submit/monitor `junjinyong`.

> **2026-08-12 schema 11.6 deployment/private synchronization:** Exact public
> scientific source `4dfe08f35934901de5bc8d88a06869a1a5230998` passed Quality
> `31579905965` and Pages `31579905336`. Private paper ledger head
> `b32d0c8f9ce7660d5033c6534b99e5dd0c51d9fc` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` and references remain
> byte-for-byte at SHA-256
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 486 tests: 420 pass/66 optional-dependency skip. The final
> public workflow also validates the corrected P0-v2 contract explicitly.
> This pin creates no executable P0, method, architecture, result, GPU, outer
> test or manuscript claim. No scientific server was queried; never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 AneuX P0 v2 source correction · schema 11.6:** Official
> `content-description-v1.0.pdf` states that `morpho-per-cut.csv` has the 170
> morphometrics at mesh resolution `area-005` only. Exact official repository
> head `a6b355e8f271e9a88399a2e432ed924d99b85d64` contains README/LICENSE/docs
> only and says code publication is in progress; do not claim official multi-
> resolution feature recomputation is available. Preserve v1 config SHA
> `b82e3606…` as pre-execution superseded history: dataset row 0, job 0,
> endpoint 0, post-result repair false. Current contract is
> `configs/aneux_nested_orbit_p0_v2.json`, SHA-256
> `86de76c4c7e4d493f12d2eb300e78647a74daf88e469102411f959982a07d0da`.
> Canonical protocol SHA-256 is
> `0a449a49badab859d75bb91a2af8536495f90e0b302e560e84ab8554d776f6b9`.
> Full regression is 486 tests: 420 pass/66 optional-dependency skip. It freezes a
> deterministic 11-feature signature on all three dome resolutions; canonical
> area-005-only patient/source-grouped nested-CV logistic probing; clustered
> bootstrap; mandatory AUROC adequacy; and both primary gates: probability
> range >0.10 materiality and range–orbit-mean-Brier association. Decision flip
> is secondary and no learned threshold is used. V2 remains non-executable
> until an external service change permits one bounded exact-path/manifest/
> reader preflight on `introai9`; do not query earlier. No P0 job, method,
> architecture, GPU, outer test or claim is authorized. Never access/query/
> transfer/submit/monitor `junjinyong`. The first unrestricted full-test attempt
> failed only because the current sandbox exposes `/tmp` read-only; the same
> suite passed with an approved repository-local temporary directory. Do not
> interpret that environment failure as a scientific or code failure.

> **2026-08-12 schema 11.5 deployment/private synchronization:** Exact public
> scientific source `5208bd2afb2e90894de3add5cc720c7f760a5a27` passed Quality
> `31576238532` and Pages `31576237547`. Private paper ledger head
> `41cb0279ab911390929c5d9285827ea689414a98` is remote-pushed and anonymous API
> returns 404. Manuscript and references remain byte-for-byte at SHA-256
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 474 tests: 408 pass/66 optional-dependency skip with 109
> protocol invariant groups. This provenance opens no executable P0, model,
> GPU, outer test or paper claim.

> **2026-08-12 acquired-asset direction · schema 11.5 historical registration:** Maintain exactly one
> conditional source lead: `aneux_factorized_nested_preprocessing_orbit_reliability`
> at 33.0/40. Treat resolution as a nuisance only within a fixed cut. Treat
> dome/ninja/cut1/cut2 as different information sets whose parent-vessel
> context residual may legitimately change the final prediction. Never promote
> flat final-logit consistency, DiffusionNet, PointNet, E(3), GroupDRO, set
> attention or calibration as novelty. The claim candidate is casewise
> preprocessing reliability hidden by average discrimination. The registered
> contract at that schema was `configs/aneux_nested_orbit_p0.json`; it was non-executable until
> one bounded read-only `introai9` inventory freezes an exact private path and
> manifest. Never repair or rerun historical AneuX job `115177.ECE-util1`.
> P0 is CPU-only, network-free and development-source-only; it must satisfy two
> of three frozen nontriviality checks. P0 pass authorizes only one strong-
> baseline feasibility P1, not a method, architecture, GPU, outer test or paper
> claim. Preserve cross-sectional rupture-status wording and forbid future-risk,
> clinical-utility and causal claims. Keep manuscript main/reference bytes
> unchanged until the evidence gate explicitly opens writing. Execution is
> `introai9` PBS-only; never access/query/transfer/submit/monitor `junjinyong`.

> **2026-08-12 data-state correction · schema 11.5:** Never equate active
> dataset/split 0 with historical dataset absence. Preserve six heterogeneous
> holding records: Aneumo, BenchAnXplore, CMHA, AneuX, AneuG-Flow and Aneurisk.
> Their exact states are respectively performance-gate failure;
> discovery-used/no-fresh-confirmation; asset-linkage failure; and three latest
> exact execution-incomplete/no-verdict records. The latest `introai9` listing
> does not establish current persistence or absence. Active
> train/validation/test remains 0/0/0 only because no paper identity and
> prospective split are assigned. Use the reason taxonomy in
> `docs/data-asset-state-ledger-2026-08-12.md`; do not write blanket “all
> datasets rejected” or “no verified research data.” A fresh ISBI direction may
> exploit a holding's native structure, but it must be a new problem/evidence
> version and may not repair or relabel closed jobs. Future execution remains
> `introai9` PBS-only with no login-node GPU. Never access/query/transfer/
> submit/monitor `junjinyong`.

> **2026-08-12 schema 11.4 deployment/private synchronization:** Exact public
> scientific source `423cf18c14f506d46561592f8fa4ca2a78d51c9a` passed Quality
> `31571433278` and Pages `31571433150`. Private paper head
> `a1997946a38644f218b352e32b76d9fda60b06dc` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` and references SHA-256 remain
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 472 tests: 406 pass/66 optional skip with 107 protocol
> invariants. This provenance opens no dataset, task, method, model, result,
> compute or paper claim.

> **2026-08-12 open clinical outcome/target-time boundary · schema 11.4:**
> Zenodo `17339029` revision 6 verifies one actual public clinical XLSX: CC BY
> 4.0, 39,686 bytes, MD5 `8aaba92f5fb74175af76edd3701b7404`, linked to a
> 230-patient aSAH source. It is not medical imaging and was not downloaded or
> opened. Source 6-month mRS is unavailable for 70 patients and discharge or
> 3-month values are substituted; do not relabel mixed observation times as
> fixed 6-month truth. Fresh scores 29.5/28.0/27.0/27.0/26.0/25.5 are all
> rejected. Source-watch v21 freezes 34 review-only states. Public versioned
> table = 1, active dataset = 0, staged train/validation/test = 0/0/0. Active
> lead/P0/P1/method/model/result/claim/GPU = 0. Full regression is 472 tests:
> 406 pass/66 optional skip with 107 protocol invariants. Protocol SHA-256 is
> `0a9ccadb4841715a761188e209329bc468c5fe5631f0d1cc81e9086b82bf6645`;
> source-watch v21 SHA-256 is
> `ab34cf2b69e44877270250e1421eec057411a3a0a108c567bc8a22bf9a483dbb`.
> This update queried no scientific server and submitted no PBS/GPU work.
> Future gate-authorized work uses `introai9` PBS only, never login-node GPU.
> Never access/query/transfer/submit/monitor `junjinyong`. Preserve private
> manuscript/reference bytes unchanged.

> **2026-08-12 introai9 inventory no-verdict · schema 11.3:** User-authorized
> read-only audit attempted the two documented `introai9` login boundaries.
> TCP/22 was reachable on both; public-key authentication was confirmed on one.
> Remote shell and SFTP sessions timed out before listing output, so current
> dataset presence/absence is unresolved. Prior bounded legacy-project history
> knows aneurysm-related traces and an IntrA repository
> skeleton, but not verified IntrA mesh payload. Do not relabel those traces as
> an acquired dataset. Verified current-direction train/validation/test cases
> are 0. No PBS, scheduler query, GPU, transfer or login-node GPU command ran.
> `junjinyong` was not accessed and remains prohibited. Repeat only after a
> service/admin state change, against exact paths; do not enter a recursive
> local-repair or broad-search loop.
> Full regression is 470 tests: 404 pass/66 optional skip with 105 protocol
> invariants. Canonical protocol SHA-256 is
> `c4a226aaa12f6285aef0e584118b833a83bcf8aa9540ca26bf2a89e0e59c473b`.
> Private ledger `46ef9ff1fbb3880b552c06a964007611aac16925` is remote exact,
> PRIVATE and anonymous API returns 404; manuscript/reference hashes remain
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Exact scientific source `6f276cab968b073a297bd61c21d01bde4758b227`
> passed Quality `31567525126` and Pages `31567524764`.

> **2026-08-12 mechanistic treatment/growth asset boundary · schema 11.2:**
> Fresh public metadata review separates six source objects: 500 synthetic
> coil sacs; 458 flow-diverter patients with six-month occlusion; 34 aneurysms
> in 17 longitudinal pairs; growing 6/stable 6 amplified-MRI cases; 42
> semi-automated CFD cases with five initially failed/manual reconstructions;
> and 28 particle configurations on one idealized anatomy. These counts are
> not interchangeable patients or one cohort. No public immutable asset joins
> pre-treatment geometry, actual device/deployment, immediate angiographic
> response and fixed-time outcome for the same lesion. Fresh scores
> 27.5/25.5/24.0/23.5/23.0/22.5 are all rejected. Source metrics are not AURORA
> results. Active lead/E0/P0/P1/method/architecture/server/PBS/GPU/result/claim
> are 0. Surface-vector remains inactive; job `115645` is not repaired/rerun.
> No new source watch is added. Future gate-authorized work uses `introai9`
> PBS only, never login-node GPU. Never access/query/transfer/submit/monitor
> `junjinyong`.

> **2026-08-12 schema 11.1 deployment/private synchronization:** Exact public
> scientific source `9206415e43bd85cf4e592cf81005bc1b34851465` passed Quality
> `31563336315` and Pages `31563336017`. Private paper head
> `94da161d8de3589336aae5f0d0232c68814a3942` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` and references SHA-256 remain
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 468 tests: 402 pass/66 optional skip with 103 protocol
> invariants. No title, claim, method, result, figure, server or compute
> authority is added.

> **2026-08-12 TopAneu registered-design/release boundary · schema 11.1:**
> Registered design 500 train/350 private test, 200 public-source train and
> 50/20 gold vessel-mask plans are not realized-release facts. The live public
> train is 417 scan/409 patient with public-source count 68 and organizer-
> TopBrain-predicted vessel masks; public casewise gold/silver, complete
> patient-grouped split, test manifest, minimum per-location support and control
> fraction are not established. Zenodo CC BY 4.0 covers the design record, not
> the medical-data agreement. Six fresh scores 31.5/30.5/27.5/26.5/26.5/20.5
> are all rejected; best residual novelty is 0.5/5. Historical TopAneu scores
> and surface-vector job `115645` are not relabelled or reopened. Active lead,
> P0/P1, method, architecture, terms/payload, server query, PBS/GPU, result and
> claim are 0. Source-watch v20 is reused without a duplicate watch. Future
> gate-authorized work uses `introai9` PBS only; login-node GPU is forbidden.
> Never access, query, transfer, submit to or monitor `junjinyong`.
> Full local regression is 468 tests: 402 pass/66 optional skip with 103
> protocol invariants. Protocol SHA-256 is
> `872a3917485512c5990d3e46185cddd2f74d1acbf568cfcfc7d8e3582a3d87cd`;
> unchanged source-watch v20 SHA-256 is
> `57d2a8671e09a2f49d3e3b265ee87353b86245ecdf2d0199f482c11d50580198`.

> **2026-08-12 schema 11.0 deployment/private synchronization:** Exact public
> scientific source `b7ef613ee6ac906ba23bdf5df29e51b59ac66899` passed Quality
> `31561077612` and Pages `31561073271`. Private paper head
> `b33a5cc82c61eb1b1da5236b363441be0951b1ad` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` and references SHA-256 remain
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 467 tests: 401 pass/66 optional skip with 102 protocol
> invariants; canonical protocol SHA-256 is
> `01860b4f7b0cee98c50cc546e78b0ba43f767a3aa144d7b57af18578b40a19a8`.
> No title, claim, method, result, figure, server or compute authority is added.

> **2026-08-12 endovascular collision-anticipation · schema 11.0:** 전달된
> surface-vector 분석에서는 “field error와 stable flow structure가 다를 수
> 있다”는 가설 및 task stability→matched failure→bounded development→fresh
> confirmation 순서만 보존한다. Job `115645.ECE-util1`은 E/exit 2,
> walltime 00:27:02, GPU 0, 0/10, aggregate/raw log/cache 0인 execution-
> incomplete/no-verdict history다. 32.0/40 source score를 유지하며 같은
> contract를 repair/rerun하지 않는다. Edge-1-form/Hodge/SE(3)/periodic
> operator/structural loss는 unselected controls이지 novelty나 architecture가
> 아니다.
>
> Exact CathAction HF revision `8b04056…`은 네 archive와 56,678,352,136
> used bytes를 공개하지만 card가 download form/license agreement를 요청하고,
> public metadata에는 collision onset/horizon/complete negatives/procedure-
> specimen-anatomy IDs/cross-archive join/human collision split이 없다. Human
> segmentation은 human collision evidence가 아니고 frame 수는 독립 procedure
> 수가 아니다. Source가 action anticipation, collision detection,
> segmentation과 phantom→animal adaptation을 이미 점유한다. Fresh scores
> 26.5/26.5/26.0/24.5/24.0/20.0은 모두 reject. Terms/payload/P0/P1/method/
> architecture/server/PBS/GPU/outer test/result/C21/claim은 0이다. Source-watch
> v20은 33-state review-only다. Future gate-authorized execution은 `introai9`
> PBS만 사용하며 login-node GPU를 금지한다. `junjinyong`에는 절대 접속·조회·
> 전송·제출·모니터링하지 않는다.

> **2026-08-12 schema 10.9 deployment/private synchronization:** Exact public
> scientific source `3a9fa3a1a3146457b7d0e8215db66ee26d5532ac` passed Quality
> `31559316259` and Pages `31559316027`. Private paper head
> `a4711543c245fb60617ec8975c4b94923400a3fd` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` and references SHA-256 remain
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 465 tests: 399 pass/66 optional skip with 100 protocol
> invariants; canonical protocol SHA-256 is
> `83cd0e12be0c73af88cfe8a2e020a6be4bd5e29a5971feb91e83360301806a3d`.
> No title, claim, method, result, figure, server or compute authority is added.

> **2026-08-12 molecular-biomarker/treatment-outcome · schema 10.9:** Exact
> public-source audit separates downloadable patient-level data, an unoccupied
> task, and a valid target time. PXD024615 supplies 212 discovery and 32
> external serum-proteomics samples, but the source already performs IA/control
> and rupture-state classification. It does not join pre-event blood, baseline
> imaging and future event/censoring for the same patient. PXD013442 has four
> pooled discovery mixtures; GSE231922 has 30 plasma samples; NBC-GARUDA has
> bootstrap-only prognosis and no treatment-effect identification. Scores
> 31.0/28.0/27.0/27.0/26.0/23.0 are all rejected. No payload, P0/P1, method,
> architecture, server query, PBS/GPU, result or claim opens. Historical
> `115645` remains closed 0/10 no-verdict and is never repaired/rerun. Future
> execution is `introai9` PBS-only with no login-node GPU. Never access/query/
> transfer/submit/monitor `junjinyong`.

> **2026-08-12 schema 10.8 deployment/private synchronization:** Exact public
> scientific source `6b153b7f988e2d1c6fe9def294a6348849a4c53a` passed Quality
> `31557448461` and Pages `31557447516`. Private paper head
> `e4c3f8f5b3d908d2be418e1506cacbb6cdbac5d9` is remote exact. Manuscript and
> references SHA-256 remain `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> No title, claim, method, result, figure, server or compute authority is added.

> **2026-08-12 structured-vessel/embargoed-4D-flow · schema 10.8:** Exact
> VeNet data/code heads `c233ab9…`/`7c9cf0f…`를 bounded public-state audit했다.
> Public Git은 20 mask뿐이며 source MRA, independent test와 full-200 contract는
> 없다. RSNA multi-task `e59e236…`은 series-level five-fold/pseudo-label direct
> prior이고 patient grouping은 unresolved다. CMRx4DFlow exact `f6f835f…`은 code
> only; 138/32/43 regular split은 controlled이고 Dec-2026 embargo가 Oct-26 ISBI
> deadline 뒤다. Zenodo 14981710의 8 acquisition은 한 anatomy/4 model/2 VENC다.
> Fresh scores 27.5/27.0/27.0/26.5/26.0/21.0, 모두 reject. Active lead/P0/P1/
> method/architecture/server/PBS/GPU/outer-test/result/claim은 0이다. `115645`을
> repair/rerun하지 않는다. Future gate-authorized execution은 `introai9` PBS만
> 사용하고 login-node GPU를 금지한다. `junjinyong`에는 절대 접속·조회·전송·
> 제출·모니터링하지 않는다. Source-watch v19는 32-state review-only다.
> Full regression은 464개 중 398 pass/66 optional-dependency skip, protocol 99
> invariant group이다. Machine protocol canonical SHA-256은
> `b4c4f18ad7a7f6c31179c015a63c751933268a955491efc9698f6847c5d9eb5e`,
> source-watch v19 SHA-256은
> `911fa8b327b8f828de9ca349c577c9375d32e5fc3ddbe33ae8d06b0f04d1c228`다.

> **2026-08-12 ADAM-fold deployment·private synchronization:** Exact public
> scientific source `836293006a835c421aac474c668387daeb659f77` passed Quality
> `31555748252` and Pages `31555747611`. Live Overview, Learn
> `#adam-fold-release`, the exact audit, machine protocol, source-watch v18 and
> filterable history expose the same rejection. Private paper ledger
> `25b10dec320f58528702fad23d8bde232e111e65` is remote exact and anonymous
> API returns 404. `paper/main.tex` and references SHA-256 remain
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This provenance adds no lead/P0/P1/method/model/server/GPU/result/claim.

> **2026-08-12 ADAM patch-fold/segmentation-prior delta · schema 10.7
> unchanged:** Exact public fold repository `d36df7d…`의 v1.0은 35 asset,
> 61,506,611,200 bytes지만 dataset license/upstream ADAM reuse contract가 없다.
> Small organization JSON만 읽었고 archive payload는 0이다. 93 positive scan,
> 58 base ID, B/F 35 pair+23 unique 구조에서 official ADAM same-subject
> semantics를 적용하면 fold별 development/test base overlap은 2/3/5/6/2다.
> Validation ID와 negative 20건은 manifest에 없다. DINO-3DRA `5d9982e…`,
> GeoP2VNet `25c59bc…`, modality/weak-supervision public code는 direct-prior
> control일 뿐 AURORA result나 selected model이 아니다. Fresh scores
> 26.5/26.5/26.0/25.5/23.0/23.0은 모두 기각한다. Source-watch v18은 31
> state review-only다. Active lead/E0/P0/P1/method/architecture/server/PBS/GPU/
> outer test/result/C21/claim은 0이다. `115645`을 repair/rerun하지 않는다.
> Future gate-authorized execution은 `introai9` PBS-only, login-node GPU 금지다.
> `junjinyong`에는 절대 접속·조회·전송·제출·모니터링하지 않는다.
> Full regression은 462개 중 396 pass/66 optional-dependency skip, machine
> protocol 97 invariant group이며 site/JSON/JavaScript/diff hygiene가 통과했다.
> Machine protocol SHA-256은
> `232bc58b12678481dbe9b89b1738f8ca284a88b93768a832208a481c32f05e98`,
> source-watch v18 SHA-256은
> `ab69bca79ba70d8b6543dbcc1e11d9091eaef201f0da61a6f29fa26320d7cf00`다.

> **2026-08-12 surface-vector/DSA deployment·private synchronization:** Exact
> public scientific source `cb4f6b16183ddd10a3982edbbdabf77d8a0a3808`
> passed Quality `31553310905` and Pages `31553310384`. Live Learn
> `#dsa-task-fidelity`, the exact audit, machine protocol, source-watch v17 and
> filterable change history expose the same fail-closed decision. Private paper
> ledger `b708bc2581042d83e323c905035966a1047333bb` is remote exact, PRIVATE and
> anonymously returns 404. `paper/main.tex` and references SHA-256 remain
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This provenance opens no paper identity, method, model or compute.

> **2026-08-12 surface-vector/task-faithful DSA delta · schema 10.7
> unchanged:** 전달된 field-accuracy/structure 문제와 stability→matched
> failure→bounded development→fresh confirmation 순서는 채택한다. 그러나
> material source 없이 fresh version으로 같은 contract를 재개하지 않는다.
> Exact critical point/worldline extractor는 E1 stability 전 evaluation-only이고
> boundary-margin signed total degree+abstention이 먼저다. SAVE-Net은 sparse
> frame synthesis/dose/TIC/reader confidence, dual-centre TransUNet은 real-DSA
> segmentation→morphology/QDSA, arXiv 2602.11703은 semantic synthetic DSA와
> reader study를 직접 점유한다. Zenodo 21104782 revision 4는 2026-10-31까지
> embargoed이고 original patient DSA/downstream label이 없다. DIAS는 expert-
> pruned vessel-mask task다. Fresh DSA scores 26.5/26.5/26.0/25.5/24.5/23.5는
> 모두 기각한다. `115645`은 E/exit 2, GPU 0, 0/10 no-verdict로 immutable하며
> repair/rerun 0이다. Architecture는 null, source-watch v17은 28 state review-
> only다. 이번 update의 scientific server query/transfer/PBS/GPU/monitoring은
> 0이다. Future authorized execution은 `introai9` PBS only, login-node GPU 금지,
> `junjinyong`에는 절대 접속·조회·전송·제출·모니터링하지 않는다.
> Full regression은 460개 중 394 pass/66 optional-dependency skip, machine
> protocol 95 invariant group이며 site/JSON/JavaScript/diff hygiene가 통과했다.
> Machine protocol canonical SHA-256은
> `7edd19bed7d6cef1d727aa9185ce8a92660b60a4a29d84d7df5b47e4595cdd6b`,
> source-watch v17 SHA-256은
> `ebd1bdf0e6708e93c77b59870cf8cedbf051c16d41467673c516cc26ac5b3653`다.

> **2026-08-12 pose/operator deployment·private synchronization:** Exact
> public scientific source `8910e1b0f8148b45732493998983577d339ecdfd`
> passed Quality `31551588925` and Pages `31551587888`. Private paper ledger
> `e26dadb61acf5b1268ad8d7f8f4943b6fb42cffe` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This provenance changes no schema-10.7 scientific state and opens no
> lead/P0/P1/method/model/server/PBS/GPU/outer test/result/C21/claim.

> **2026-08-12 pose/workflow and spatiotemporal-operator reappraisal · schema
> 10.7 unchanged:** DeepAnePose exact `40042fa…` has 270 selected IDs, 140
> positive JSON, 164 lesions and patient-wise five-fold test coverage, but weak
> pose/detection/reformatted planes are direct prior. Graph Physics
> `e4ac523…`, Aneumo WSS Transolver `3087fc9…` and EXPIGEO `b287368…`
> further crowd generic operator/GNN claims. Six rows score
> 29.0/28.5/27.0/26.0/25.5/21.5 and all are rejected. Surface-vector remains a
> valid inactive hypothesis; edge-1-form/Hodge/equivariant/periodic modules are
> unselected controls, not novelty. Source-watch v16 freezes 27 states and can
> request review only. No payload, E0/P0/P1, method, architecture, scientific
> server, transfer, PBS/GPU, outer test, result or claim opened. `115645` is not
> repaired/rerun. Future authorized execution is `introai9` PBS only; never
> access/query/transfer/submit/monitor `junjinyong`, and never use login-node GPU.
> Full regression: 458 total, 392 pass/66 optional-dependency skip; machine
> protocol 93 invariant groups. Site link/anchor/asset/app mount, JSON,
> JavaScript and diff hygiene pass. Team-source hashes remain `ad99cc…` and
> `6d50cb…`; no conversation newer than 2026-08-02 was present.
> Machine protocol SHA-256 is `36935be0c3c01147d839bebb767f639e3c306ffd1f2da53f5a35656b69d201eb`;
> source-watch v16 SHA-256 is `fb1b0cb80d764873f5364a4a56d3cd4c64dbd7c620e01bbb64d495da9de0b875`.

> **2026-08-12 surface-vector finite closure deployment·private
> synchronization:** Exact public scientific source
> `a9d79f0446041555585a73f0fc7ed9a0cd990514` passed Quality `31549386632`
> and Pages `31549386364`. Live Overview, Learn, the exact audit and filterable
> history expose `closed_until_whitelisted_material_release`. Private paper
> ledger `e8db8078f8c025b2715a4ee59fa5ff6aadea596c` is remote exact, PRIVATE and
> anonymous API is 404. Full regression is 456 tests: 390 pass/66 optional
> skip with 91 protocol invariant groups; site/JavaScript/diff hygiene pass.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization opens no lead/P0/P1/method/model/server/PBS/GPU/outer
> test/result/C21/claim and changes no schema-10.7 scientific state.

> **2026-08-12 surface-vector finite closure · schema 10.7 unchanged:** Keep
> the hypothesis, but mark the current asset family
> `closed_until_whitelisted_material_release`. Job `115645.ECE-util1` remains
> E/exit 2, GPU 0, 0/10 and no-verdict; never repair or rerun it. Exact source
> states remain AneuG `9dd4180…`, Aneurisk revision 4, AneuX `38c574b…`,
> AAA-WSS `2f78bf1…` and unavailable TRELLIS. Synthetic-AAA moved from tag
> `98363a0…` to main `7872b81…`, but the complete diff changes only README and
> CITATION metadata. It is not fresh E0. Source-watch v15 freezes 24 states and
> may request source re-audit only. Architecture/GNN/P0/P1/server/PBS/GPU/
> outer test/result/C21/claim remain 0. Future gate-authorized execution is
> `introai9` PBS-only with no login-node GPU. Never access, query, transfer to,
> submit to or monitor `junjinyong`.

> **2026-08-12 longitudinal-biology delta deployment·private synchronization:**
> Exact public scientific source
> `0cadda2cf03144f2e876862a727714858999b56c` passed Quality `31547562160`
> and Pages `31547561485`. Live Learn `#biology-chain`, the detailed audit and
> filterable change history are deployed. Private paper ledger
> `6189db9532203207d411e8983dcd8586cbe8efc4` is remote exact, PRIVATE and
> anonymous API is 404. Full regression is 451 tests: 385 pass/66 optional
> skip with 89 protocol invariant groups; site/JavaScript/diff hygiene pass.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization opens no lead/P0/P1/method/model/server/PBS/GPU/outer
> test/result/C21/claim and changes no schema-10.7 scientific state.

> **2026-08-12 longitudinal-biology/cross-scale mechanism delta · schema 10.7
> unchanged:** Long-term AWE source `10.1002/ana.78106` follows 198 patients/
> 224 untreated aneurysms for median 6.8 years and directly owns the association
> with composite growth/morphological-change/rupture; reported adjusted HR 5.06
> is not an AURORA result. Academic Radiology `10.1016/j.acra.2026.04.002`
> uses separate 308/416 AWE, 80/85 growth and UK Biobank incident-aSAH datasets,
> so never infer same-patient NHR/SIRI→AWE→growth→aSAH mediation. JMRI PMID
> 41913331 supplies another 311/418 AWE cohort with a 67/84, median-7-month
> growth subcohort; it is direct prior, not an open benchmark. Rat source
> `10.1038/s41598-026-37369-2` has 13 induced/6 control animals, only eight
> induced animals at W12, five early deaths, source sensitivity/specificity
> 40%/60%, 0.146-mm MRA resolution and ≤0.10-mm false-negative lesions; data are
> request-only. Six scores 28.5/26.5/25.0/23.0/22.5/20.0 are all rejected.
> No source joins transient WSS critical structures to outcome; surface-vector
> remains inactive. Active lead/P0/P1/method/architecture/server/PBS/GPU/outer
> test/result/C21/claim are 0. Historical jobs are not repaired or rerun.
> Future gate-authorized execution is `introai9` PBS-only with no login-node
> GPU. Never access, query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 rupture-time delta deployment·private synchronization:** Exact
> public scientific source `309e16205a82f1fe7599a24719486da40375193d`
> passed Quality `31545461242` and exact-head Pages `31545766452`. Private paper
> ledger `7fb0fccb002763c2827d46b5c2186af53893ca2b` is remote exact, PRIVATE and
> anonymous API is 404. Full regression is 450 tests: 384 pass/66 optional
> skip with 88 protocol invariant groups; site/JavaScript/diff hygiene pass.
> `paper/main.tex` and references remain byte-for-byte unchanged. This
> provenance pin opens no lead/P0/P1/method/model/server/PBS/GPU/outer test/
> result/C21/claim and changes no schema-10.7 scientific state.

> **2026-08-12 rupture-state/future-risk and unit-semantics delta · no state
> change:** QIMS `10.21037/qims-2025-1-2593` reports 756 patients/877
> aneurysms from three centres. Its endpoint is observed rupture status, not a
> future-event estimand; admission blood glucose is post-event for ruptured
> presentations. Centre-I 314/136 rows sum to 450 aneurysms from 404 patients,
> and patient-grouped splitting is not explicit. Treat this as unresolved
> dependence, never proven leakage. Source AUC 0.887/0.910/0.773/0.735 is not
> an AURORA result. PLOS Figshare `28661913` exposes one 5,632-byte aggregate
> `Table 1.xls`, not patient rows or CTA. Scores
> 27.5/27.0/25.5/25.0/24.0/23.5 are all rejected. Schema 10.7, current aSAH
> batch, surface-vector inactivity and lead/P0/P1/method/architecture/server/
> PBS/GPU/outer-test/claim 0 remain unchanged. No patient payload, XLS body,
> request or scientific server was opened. Future gate-authorized execution is
> `introai9` PBS-only; never access, query, transfer to, submit to or monitor
> `junjinyong`.

> **2026-08-12 RSNA/WEB-GAN delta deployment·private synchronization:** Exact
> public scientific source `445e3dc90abffad9e00bf0b1069acc949d66f536`
> passed Quality `31543772897` and Pages `31543771957`. Private paper ledger
> `827ae95026409f62eba988ebc0ec80a02003c94a` is remote exact, PRIVATE and
> anonymous API is 404. Full regression is 449 tests: 383 pass/66 optional
> skip with 87 protocol invariant groups; site/JavaScript/diff hygiene pass.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization opens no lead/P0/P1/method/model/server/PBS/GPU/outer
> test/result/C21/claim and changes no schema-10.7 scientific state.

> **2026-08-12 RSNA release-layer/WEB-GAN utility delta · no state change:**
> Official RSNA launch `>6,500` multimodal studies, AWS registry `>4,000`
> controlled CT scans and the second-place method's 4,348 training series are
> different source claims. Never infer a common unit, public expansion or
> arithmetic train/test split without an official identity map. WEB-GAN paper
> `10.1177/2997979X251369456` reports 78 cases/3 institutions/1,000 synthetic
> rows. Exact repository head `42ce2a8…` trains the generator on the complete
> original table and tests the synthetic-trained predictor on those same
> original donors; original patient/institution data are request-only. Treat
> this as an evaluation-contract limitation, not paper invalidation or novelty.
> Six delta scores 29.0/28.5/26.0/25.5/24.5/23.0 are all rejected. Schema
> 10.7, the current aSAH batch, surface-vector inactivity and lead/P0/P1/method/
> architecture/scientific-server/PBS/GPU/outer-test/claim 0 remain unchanged.
> No controlled payload or synthetic CSV body was opened; no server was
> queried. Future authorized execution remains `introai9` PBS-only and
> `junjinyong` remains absolutely excluded.

> **2026-08-12 surface-vector external-analysis delta review · no state
> change:** The supplied job-state/no-repair/staged-gate reasoning is accepted.
> The claimed stale running label is not present in the current snapshot:
> `115645.ECE-util1` is already closed at E/exit 2, GPU 0, 0/10 scientific
> checks evaluated. Current architecture is null—not GNN. In-PI-MGN/
> BenchAnXplore is now explicitly cross-linked as a physics-constrained
> autoregressive transient aneurysm mesh-GNN direct prior. Surface-vector
> remains an inactive hypothesis; schema 10.7, scores, lead/P0/P1/method/
> architecture/server/GPU/outer-test/claim 0 and all execution prohibitions are
> unchanged. No server query, transfer, submission or monitoring occurred.

> **2026-08-12 schema 10.7 scientific deployment·private synchronization:**
> Exact scientific public source
> `39b94a7c42d40c70c18fe76744349507bffb2ea8` passed Quality
> `31540996594` and Pages `31540995837`. Live Overview, Learn, detailed audit
> and machine protocol expose schema 10.7, best 29.0/40 rejected, all six
> rejected and lead/P0/method/model/server/GPU/claim 0. Private paper ledger
> `f04716e7c39f90a33fe76ccf677c4285a074819a` is remote exact; `paper/main.tex`
> SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 448 tests: 382 pass/66 optional skip, protocol 86
> invariant groups and site/JavaScript checks pass. This synchronization opens
> no scientific or submission authority.

> **2026-08-12 aSAH segmentation/outcome reappraisal · schema 10.7:** Exact
> Zenodo record `8228847` revision 2 is open CC BY 4.0 and contains one
> 648,502,298-byte RAR of stated NCCT/mask pairs. The archive body was not
> opened and its metadata exposes no patient count, centre, split or outcome
> join. Official pipeline head `3fbd7a9…` contains code and a non-patient
> template, but no tracked patient cohort, mask set, mortality/GOS table or
> checkpoint. The 2026 nnU-Net study directly compares manual/automatic volume
> for six-month GOS; multiclass segmentation, LoRA/DoRA transfer and SAHVAI
> 3D/4D are direct priors. Fresh scores 29.0/28.5/28.0/28.0/27.0/22.5 are all
> rejected; best residual novelty is 1.0/5. Source-watch v14 freezes 23 public
> states and can request review only. RAR/checkpoint/patient payload, active
> lead/P0/P1/method/architecture/server/PBS/GPU/outer test/result/C21/claim are
> 0. Surface-vector remains inactive and historical no-verdict jobs are not
> repaired or rerun. Future gate-authorized execution uses `introai9` PBS only,
> never login-node GPU. Never access, query, transfer to, submit to or monitor
> `junjinyong`.

> **2026-08-12 schema 10.6 scientific deployment·private synchronization:**
> Exact scientific public source
> `1f8ce3cf774b3a5562fbbc4c9ee5a48005056660` passed Quality
> `31537504625` and Pages `31537503585`. Live Overview, Learn and machine
> protocol expose schema 10.6, best 29.0/40 rejected, all six rejected and
> lead/P0/method/model/server/GPU/claim 0. Private paper head
> `3f510fabad9f19a5e3d01a288bbbd23996d23f73` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 443 tests: 377 pass/66 optional skip, protocol 84
> invariant groups and site/JavaScript checks pass. This synchronization opens
> no scientific or submission authority.

> **2026-08-12 4D-CTA wall-phenotype release reappraisal · schema 10.6:**
> PeerJ source `10.7717/peerj.19393` reports 52 aneurysms from four hospitals,
> 100 Hz one-second trajectories and source average accuracy 92%; none is an
> AURORA result. Exact Zenodo record `13788524` revision 4 contains one
> 1,934,055,674-byte CC-BY-4.0 archive. Exact GitHub head `8df7d45…` exposes
> code and 52 visible case directories, but no source DICOM, operative RGB/
> video, registration reference, surface adjacency, complete patient/centre/
> fold contract or dense independent wall truth. Directory count is not
> verified patient count. Six rows score 29.0/28.5/28.0/27.5/26.5/24.5 and
> all fail total or critical floors. Source-watch v13 freezes 20 sources;
> changes request review only. Active lead/P0/P1/method/architecture/server/
> PBS/GPU/outer test/result/C21/claim are 0. Surface-vector stays inactive and
> historical no-verdict jobs are not repaired or rerun. Future gate-authorized
> execution uses `introai9` PBS only, never login-node GPU. Never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 schema 10.5 scientific deployment·private synchronization:**
> Exact scientific public source
> `e69718448c85eedf4a4edad5c66fcd33ca791ff1` passed Quality
> `31534693949` and Pages `31534693040`. Live Overview, Learn and machine
> protocol expose schema 10.5, best 30.5/40 rejected, all six rejected and
> lead/P0/method/model/server/GPU/claim 0. Private paper head
> `529a38f30717d427b6b02f8f25e2962cd04b6ff0` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 438 tests: 372 pass/66 optional skip, protocol 82
> invariant groups and site/JavaScript checks pass. This synchronization opens
> no scientific or submission authority.

> **2026-08-12 culprit-lesion/mimic reappraisal · schema 10.5:** The
> eight-hospital CTA culprit study contains 207 patients/460 aneurysms for
> development/internal validation and 65/147 from four other hospitals for
> external validation. Source external AUC 0.898/0.892/0.897 is not an AURORA
> result. A three-institution VWI study directly covers symptomatic-lesion
> identification in 30 patients/82 aneurysms. The 285-patient smaller-
> counterpart cohort is cross-sectional and request-only; the 665-outpouching
> infundibulum cohort has 1,040 lesion-years but only ten DSA re-reviews and no
> public joined image/reference/action release. ICAN public tables are
> simulated, not patient evidence. Six frozen rows score
> 30.5/29.5/28.0/26.0/25.5/24.0; all fail total or critical floors. Best asset
> readiness is 0.5/5. Patient-set accounting, culprit-reference provenance and
> target separation remain evaluation principles only. Active lead/P0/P1/
> method/architecture/server/PBS/GPU/outer test/result/C21/claim are 0.
> Surface-vector stays inactive and historical no-verdict jobs are not repaired
> or rerun. No scientific server was queried, no transfer/job occurred. Future
> gate-authorized execution uses `introai9` PBS only, never login-node GPU.
> Never access, query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 schema 10.4 scientific deployment·private synchronization:**
> Exact scientific public source
> `fb5fabce61cd6df53cd806538da86bbf81ec4f74` passed Quality
> `31532823553` and Pages `31532823420`. Live Overview, Learn and machine
> protocol expose schema 10.4, best 30.5/40 rejected, 25 paired TopBrain
> patients, all six rejected and lead/P0/method/model/server/GPU/claim 0.
> Private paper head `7522d43ee1cfb3c73cc914593e36b8d24ae3dfa6` is remote
> exact, PRIVATE and anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 437 tests: 371 pass/66 optional skip, protocol 81
> invariant groups, source-watch 18/18 exact and site/JavaScript checks pass.
> This synchronization opens no scientific or submission authority.

> **2026-08-12 TopBrain 2025/RSNA material correction · schema 10.4:** Public
> TopBrain record `16878417` revision 14 contains one 1,958,849,592-byte archive
> representing 50 volumes from 25 same-patient CTA/MRA pairs. It is 25
> independent patients, and its vessel-anatomy labels are not aneurysm masks.
> API license is null, custom download terms were not accepted and payload was
> not opened. Exact podium record `20158639` revision 18 and BraveCoWCoW head
> `e59e2368…` are direct-prior controls, not architecture authority. Six frozen
> rows score 30.5/29.0/27.0/25.0/25.0/24.5 and all fail total or critical
> novelty/asset floors. Source-watch v12 live refresh is 18/18 exact with review
> signal 0. Active lead/P0/P1/method/architecture/server/PBS/GPU/outer test/
> result/C21/claim remain 0. Surface-vector remains inactive; historical
> no-verdict jobs are not repaired or rerun. Future gate-authorized work uses
> `introai9` PBS only, never login-node GPU. Never access, query, transfer to,
> submit to or monitor `junjinyong`.

> **2026-08-12 schema 10.3 scientific deployment·private synchronization:**
> Exact scientific source `8d09d34ad2b05e1c65530811ede4d8aa5ada66ec`
> passed Quality `31525137390` and Pages `31525136523`. Live Overview,
> Learn and the machine protocol expose best 27.0/40 rejected, all six rejected
> and lead/P0/method/model/server/GPU/claim zero. Private ledger
> `7281f013695b8522cb901b75e397d50c7d5ddd3a` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization opens no lead, P0/P1, method, architecture, scientific-
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> execution is `introai9` PBS only; prohibit login-node GPU and never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 target-time and instability-prediction reappraisal · schema
> 10.3:** Seven-hospital source `10.1016/j.jocn.2026.111974` reports 852
> patients/1,111 aneurysms: internal 646/840 and six-hospital external 206/271,
> with source external AUC 0.85 radiomics, 0.61 clinical+morphology and 0.78
> combined. These are not AURORA results. The inspected public metadata expose
> no versioned patient/image/mask/split/code asset and do not establish complete
> patient-grouping or centre-wise external-manifest semantics.
>
> VWI Transformer source `10.3389/fnins.2026.1818110` has 293 patients/312
> aneurysms and a patient-random 205/88 split. It directly occupies habitat
> radiomics, deep features, clinical fusion, attention, SHAP, calibration and
> DCA. Its composite unstable label mixes recent symptoms, previously observed
> growth, and future rupture/progression, so it is not one pure future-event
> estimand. Source AUC 0.844 is not reproduced; the study is single-centre,
> author-available and has no external validation or optimism-corrected
> bootstrap.
>
> NCT07111975 plans 3,800 retrospective MRA participants across three European
> centres, automated morphology/clinical prediction and a vignette study, but
> has no results and completes in 2028. Six fresh scores
> 27.0/26.5/26.0/25.5/25.5/25.5 all fail the non-compensatory gate. Target-time
> declaration, component-endpoint separation and external-centre incremental
> value remain evaluation principles only. Surface-vector stays inactive; job
> `115645.ECE-util1` remains 0/10 no-verdict without repair/rerun. Lead,
> P0/P1, method, architecture, scientific-server query, PBS/GPU, outer test,
> result, C21 and claim are zero. Future authorized work is `introai9` PBS
> only; prohibit login-node GPU and never access, query, transfer to, submit to
> or monitor `junjinyong`.

> **2026-08-12 schema 10.2 scientific deployment·private synchronization:**
> Exact scientific source `c6906134ad2cea6a7f1918edb2b515c95a9d0b41`
> passed Quality `31522903059` and Pages `31522901393`. Live Learn and the
> machine protocol expose best 30.0/40 rejected, all six rejected and lead/P0/
> method/model/server/GPU/claim zero. Private ledger
> `b66700864bd9f43d21ce8e1cff60d16f80a1d679` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization opens no lead, P0/P1, method, architecture, scientific-
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> execution is `introai9` PBS only; prohibit login-node GPU and never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 decision-time and clinical-precision reappraisal · schema
> 10.2:** Four-centre PED source `10.3389/fneur.2026.1756374` reports 362
> patients/426 aneurysms, 298/128 pooled random aneurysm split, 61 patients with
> one PED covering multiple aneurysms, median follow-up 199 days and source AUC
> 0.785/0.809. Patient-grouped splitting is not explicitly stated and the
> described validation is not centre-held-out. Do not assert definite leakage;
> preserve unresolved patient dependence. Poor apposition is immediate VasoCT
> information and migration is postoperative/follow-up information, so the
> final nomogram is not a pure pre-operative information set.
>
> Commercial-precision source `10.1186/s12880-026-02209-2` has 148 patients/
> 163 aneurysms and 86 paired CTA--DSA patients. Two commercial AI systems are
> more reproducible than manual CTA in the source, but all method-vs-DSA limits
> exceed the prospective ±1 mm agreement boundary. It is cross-sectional,
> single-centre and request-only, not longitudinal growth validation. Five-
> centre autonomous CTA morphometry `10.1148/ryai.251093` is direct prior; its
> public web tool is not a patient-level training release.
>
> Six fresh rows are frozen at 30.0/26.0/25.5/25.0/24.5/23.0 and all fail the
> non-compensatory gate. Retain information-set declaration, hemodynamic
> incremental-value testing and clinical precision before growth claims as
> evaluation principles only. No joined timestamped public patient/centre/
> image/CFD/device/outcome asset exists. Surface-vector remains inactive; job
> `115645.ECE-util1` remains 0/10 no-verdict without repair/rerun. Lead, P0/P1,
> method, architecture, scientific-server query, PBS/GPU, outer test, result,
> C21 and claim are zero. Future authorized work is `introai9` PBS only;
> prohibit login-node GPU and never access, query, transfer to, submit to or
> monitor `junjinyong`.

> **2026-08-12 schema 10.1 scientific deployment·private synchronization:**
> Exact scientific source `2abc73e07275e31ad87db3cf39b77864e1419322`
> passed Quality `31519811493` and Pages `31519810721`. Live Overview, Learn
> and the detailed audit expose best 26.5/40, all six rejected, no joined
> patient-outcome asset and lead/P0/model/compute 0. Private ledger
> `8a9c1a905e715f0f47972a658528149620dfd6c9` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization opens no lead, P0/P1, method, architecture, scientific-
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> execution is `introai9` PBS only; prohibit login-node GPU and never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 device-planning/mechanistic-occlusion reappraisal · schema
> 10.1:** NeurAneuNet (`10.1002/cns.71047`) already maps pre-operative 3DRA to
> PED size and landing zones and reports a 21-case/six-reader assistance study;
> its reference is three-senior-reader consensus on deployment adequacy, not
> durable occlusion, safety or patient utility. Its 600 reported aneurysms split
> into 390 non-PED and 210 PED-treated cases; the 147/21/42 PED partitions are
> preserved as cases because patient-disjointness is not explicitly stated.
> Data are request-only with ethics/DUA and the inspected paper states no public
> code release.
>
> The exact device-thrombosis direct prior `arXiv:2605.03536v1` already couples
> coiling, flow diversion and stent-assisted coiling to acute fibrin, contrast
> transport and virtual DSA on three representative challenge geometries. It
> has no clinical follow-up validation or versioned output cohort. The paired
> 4D-flow/black-blood releases contain 33/38 datasets, five models, 15 devices
> but only two source patient anatomies. Volume-flow vortex evidence is not
> equivalent to signed surface-WSS critical points or worldlines and is no
> surface-vector E0.
>
> Six fresh formulations score 26.5/25.0/24.5/24.5/24.0/23.5; all fail the
> prospective non-compensatory gate. The best executable row is a two-anatomy
> direct-prior phantom, while the strongest residual novelty belongs to an
> unidentified counterfactual target. Outcome-grounded device planning remains
> an evaluation template only. Active lead/paper identity/P0/P1/method/
> architecture/server query/PBS/GPU/outer test/result/C21/claim are 0. No
> scientific server was queried. Future gate-authorized execution is
> `introai9` PBS only; prohibit login-node GPU and never access, query, transfer
> to, submit to or monitor `junjinyong`.
> Full regression is 430 tests: 364 pass and 66 optional-dependency skips. The
> machine protocol passes 77 invariant groups; JavaScript, JSON, site link/
> anchor/asset checks and diff hygiene pass.

> **2026-08-12 schema 10.0 scientific deployment·private synchronization:**
> Exact scientific source `d7cf037cfd7b1833f12a0f90d24a8b070c0d7df6`의
> Quality `31516119754`와 Pages `31516119241`이 성공했고 live Overview/Learn은
> schema 10.0을 표시한다. Private ledger
> `f0d172d8fa5f5578de487c532399532949b66198`은 remote exact, PRIVATE이고
> anonymous API는 404다. `paper/main.tex` SHA-256
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`와
> references SHA-256
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`는
> unchanged다. 이 synchronization은 provenance뿐이며 lead, terms, P0/P1,
> method, architecture, scientific-server query, PBS/GPU, outer test, result,
> C21과 claim을 열지 않는다. Future authorized execution은 `introai9` PBS만
> 사용하고 `junjinyong`에는 절대 접근하지 않는다.

> **2026-08-12 ADAM longitudinal/treated-exclusion correction · schema 10.0:**
> 전달된 surface-vector 분석에서는 field accuracy와 structure fidelity의
> 분리, task stability→matched failure→bounded development→fresh confirmation
> 순서만 채택한다. Edge-1-form/Hodge/SE(3)/periodic/structural-loss는 선택된
> architecture나 novelty가 아니라 unselected direct-prior control이다. Material
> E0와 관측된 구조 failure가 없어 surface-vector는 inactive이고 closed job
> `115645.ECE-util1`은 0/10 no-verdict로 repair/rerun하지 않는다.
>
> Official ADAM training 113 case는 positive 93/negative 20이며 35
> baseline+follow-up subject pair와 23 unique positive subject를 포함한다. Scan,
> timepoint, lesion은 independent patient가 아니다. Public exact pair/lesion
> manifest와 growth adjudication은 없다. Label 2는 treated aneurysm 또는
> treatment artifact의 rough mask이고 in-plane 1 pixel dilation 뒤 official
> evaluation에서 ignore된다. Remnant, occlusion, treatment response나 action
> target으로 해석하지 않는다. MSDA-Net의 78 baseline/distinct + 35
> post-treatment(follow-up) 표현은 public intervention/lesion/response equivalence를
> 확립하지 않는 bounded semantic uncertainty일 뿐 invalidity 판정이나 contribution이
> 아니다.
>
> Fresh scores 28.5/28.0/28.0/27.0/27.0/24.5는 모두 기각한다. ADAM
> registration/agreement/organizer approval, payload, P0/P1, method,
> architecture, scientific-server query, PBS/GPU, outer test, result, C21과
> claim은 0이다. Future gate-authorized work는 `introai9` PBS만 사용하고
> login-node GPU를 금지한다. `junjinyong`에는 절대 접속·조회·전송·제출·
> 모니터링하지 않는다.
> Full regression은 429개 중 363 pass/66 dependency skip, machine protocol
> 76 invariant group, site link/anchor/asset, JSON/JavaScript와 diff hygiene가
> 통과했다.

> **2026-08-12 schema 9.9 scientific deployment·private interim
> synchronization:** Exact scientific source
> `ea30894b3df3721c22c2f2f312aac9cbb9990e18` passed Quality
> `31511921846`. GitHub Pages deployment `5854315031` has success status and
> live Overview/Learn expose schema 9.9. Exact Pages run `31511920868` has
> successful build, report-build-status and deploy jobs, but its summary was
> still `in_progress` at this observation; do not relabel the run conclusion.
> Private interim ledger `048988e7bfc7ba482fb42518eca17c9e09f19523` is
> remote exact, PRIVATE and anonymous API returns 404. `paper/main.tex`
> SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization adds no lead, P0/P1, method, architecture, scientific-
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> work is `introai9` PBS only; prohibit login-node GPU and never access, query,
> transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 diagnostic-action and human-AI reappraisal · schema 9.9:** Six
> fresh rows are frozen at 29.5/27.0/26.0/26.0/25.0/24.5 and all are rejected.
> `cfd_applicability_certified_segmentation_on_iavs` is the additive best, but
> CFD applicability is the source task itself and residual novelty is 0.5/5.
> Exact IAVS head `2e40088d9eaa671c592929a154b7b2cf99f9320a` remains README-only
> with no license or released patient rows, masks, CFD targets or split.
>
> The automation-bias source has 20 TOF-MRA examinations, nine radiologists and
> ten false-positive-AI cases (five vascular loops, three infundibula and two
> perforators). The 7 T reference source has six patients with 0.9--2.0 mm
> suspected lesions, five clarified as infundibula. These establish clinical
> importance, not a public patient-level reader/reference contract. The open
> multicentre model, generic complementarity/deferral and cross-view methods are
> direct baselines. Mimic-aware selective diagnosis or acquisition escalation
> remains an evaluation template only.
>
> The contrast-retention source already defines functional flow markers on 271
> cross-sectional PCOM aneurysms and 41 longitudinal cases; MARTA already owns
> treatment-specific risk on 2,647 patients. Neither exposes the required
> versioned joined imaging/CFD/outcome rows. Real-biplane DSA calibration also
> lacks a public acquired-pair reference asset. No terms, payload, P0/P1,
> method, architecture, server query, PBS/GPU, outer test, result, C21 or claim
> is opened. The incomplete 15-source watch observation caused by GitHub HTTP
> 403 is neither a source change nor a scientific failure and is not repaired
> or retried. Surface-vector stays inactive. Future gate-authorized execution
> is `introai9` PBS only; prohibit login-node GPU and never access, query,
> transfer to, submit to or monitor `junjinyong`.
> Full regression is 428 tests: 362 pass and 66 optional-dependency skips. The
> machine protocol passes 75 invariant groups; all 15 frozen source-watch
> entries validate, and historical contracts, site links/anchors/assets,
> JavaScript syntax and diff hygiene pass without scientific execution.

> **2026-08-12 schema 9.8 deployment·private synchronization:** Exact public
> scientific source `975b6e360f71d6948c6cb09b6661704cf5732687` passed Quality
> `31507256370` and Pages `31507253480`. Private paper ledger
> `0075d080272b3d462d57d6ba07c7ed9a7df59080` is remote exact and anonymous
> API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization adds no lead, P0/P1, method, architecture, scientific-
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> work is `introai9` PBS only; prohibit login-node GPU and never access, query,
> transfer to, submit to or monitor `junjinyong`.

> **2026-08-12 longitudinal/intervention/patient-reliability reappraisal ·
> schema 9.8:** Six fresh rows are frozen at
> 32.0/31.0/29.5/29.5/26.5/23.0 and all are rejected. Never treat the additive
> 32.0 `patient_level_all_lesion_miss_risk_control_on_rsna` row as admitted:
> its residual novelty 1.5/5 and asset readiness 2.5/5 fail the prospective
> non-compensatory floors. Generic pulmonary-nodule/medical-instance CRC owns
> the error-budget mechanism, while RSNA remains controlled, nonredistributable
> and publicly contract-incomplete. Terms/request/payload access is zero.
>
> Bayesian growth preprint `arXiv:2604.06649v1` uses adjacent-vessel
> displacement as an internal control. Distinguish its 39-patient/42-aneurysm
> internal cohort from its public subset: 24 follow-up patients were screened,
> only 16 patients/19 aneurysms were included, and the baseline--follow-up pair
> was selected partly for growth-event representation. Do not call the reported
> AUC/kappa AURORA results. The source states no versioned code release. The
> underlying public dataset has 63 patients/85 aneurysms, 24 follow-up patients
> and 16 multiple-aneurysm patients; sessions, pairs, vertices and lesions are
> not independent patients.
>
> Mendeley `10.17632/nzzx92ky6r.2` is CC BY 4.0 and contains 126 subjects/141
> procedures, a workbook, an R script in Word and selected 2D DSA JPEGs in
> PowerPoint. Never describe it as 141 patients or paired pre/post 3D imaging.
> PETRA paired raw images remain request-only. Patient-level all-lesion
> reliability is an evaluation template, not paper identity. Surface-vector is
> not reactivated. Active lead/primary/P0/P1/method/architecture/server query/
> PBS/GPU/outer test/result/C21/claim remain zero; historical jobs and scores
> are not repaired, rerun or relabelled. Future gate-authorized execution is
> `introai9` PBS only; prohibit login-node GPU and never access, query, transfer
> to, submit to or monitor `junjinyong`.
> Full regression is 427 tests: 361 pass and 66 optional-dependency skips. The
> machine protocol passes 74 invariant groups; all 15 frozen source-watch
> entries, historical P0/asset contracts, site links/anchors/assets, JavaScript
> syntax and diff hygiene pass.

> **2026-08-11 schema 9.7 deployment·private synchronization:** Exact public
> scientific source `7b3208595f60f3c6972efec0c63d21c980a62353` passed Quality
> `31503802787` and Pages `31503801773`; live Overview and Learn expose the
> 31.5/40 rejection, novelty 0.5/5, 99 visible base IDs, 714 repeated views and
> no-model/no-compute boundary. Private paper ledger
> `0bb7ffda374f801c0761fee7b589990eb175ab4f` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization adds no lead, P0/P1, method, architecture, scientific-
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> work is `introai9` PBS only; prohibit login-node GPU and never access, query,
> transfer to, submit to or monitor `junjinyong`.

> **2026-08-11 neck/isolation and open-model reappraisal · schema 9.7:** Exact
> AneuSI head `5b4c454…` is a substantive public baseline with MIT code and a
> bundled CC BY-NC 3.0 Aneurisk notice. Its complete tree has 1,041 blobs/
> 977,740,269 bytes, 103 model/centerline/neck files and 716 analysis files.
> Strip `a`/`b` lesion suffixes to obtain 99 visible base IDs; never count the
> 102 derived VTKs at each of seven `clipFactor` values as independent patients.
> README/license metadata were read, but no VTK or ODS body was opened. AneuSI
> requires an input neck polygon and does not establish cross-dataset neck
> inference.
>
> NeckSpline DOI `10.1038/s41746-026-02613-6` directly owns differentiable
> continuous CTA/MRA neck-curve prediction; its stated anonymous code endpoint
> currently returns HTTP 401 and no expert-loop/code payload was accessed.
> Open-model Zenodo `17894703` revision 4 exposes one 1,167,744,043-byte CC
> BY-NC 4.0 v2 archive, but its reported 1,094 positive scans include Lausanne
> and ADAM and are training provenance, not fresh external patients. Workflow
> variability over 1,024 transient simulations/four anatomies, TAR and generic
> selective/conformal topology UQ are direct priors.
>
> Six fresh rows are frozen at 31.5/30.0/29.0/28.0/24.0/22.5. The leader,
> `clipfactor_orbit_morphometry_stability_audit`, fails total and residual
> novelty at 0.5/5. Do not repair a score or promote isolation, neck inference,
> uncertainty, Hodge/GNN/operator composition to novelty. Active lead/primary/
> P0/P1/method/architecture/server query/PBS/GPU/outer test/result/C21/claim are
> zero. Surface-vector is not reactivated and VMR/115645/115684/115848 histories
> are not repaired, rerun or relabelled. Next action is a fresh problem-level
> source/asset audit only. Future authorized execution is `introai9` PBS only;
> prohibit login-node GPU and never access, query, transfer to, submit to or
> monitor `junjinyong`. Full regression is 426 tests: 360 pass and 66 optional-
> dependency skips. The machine protocol passes 73 invariant groups, while site
> links/anchors/assets, JavaScript syntax and diff hygiene pass.

> **2026-08-11 VMR P0 outcome · schema 9.6:** Exact public source
> `92060937529f915649fcbbc06fc2856ce45d61ea` ran once on `introai9` as
> CPU-only PBS job `115848.ECE-util1`. It ended `E`/exit 2 after 00:04:44 with
> CPU 00:00:01, memory 57,084 kB and GPU 0. The 325-byte status and 980-byte
> bounded result have SHA-256 `d4c67a…` and `6ec006…` and report
> `execution_incomplete_no_scientific_verdict`. Registered checks are 0/10;
> no aggregate scientific result exists.
>
> The bounded records do not identify the low-level cause or how much
> archive/VTP content was transiently read. Do not infer transport, reader,
> dependency or source failure. No archive/VTP persisted, the raw PBS log was
> not accessed and medical images/project archives, critical structure, growth
> association, model, GPU and outer test remain zero. Preserve 32.5/40 as
> source-screen history but close the active/conditional lead. Same-contract
> repair/rerun, P1, primary, method, architecture, result row, paper
> contribution and submission identity are forbidden. The next allowed action
> is a fresh problem-level source/asset audit only.
>
> Public execution record is
> `results/vmr_growth_surface_structure_p0_execution_20260811.json` with
> SHA-256 `c3c7c5f4984436b43cde94ed8f76f3abe006ba15d027f22ae43b1bf5b97e18a1`.
> Historical jobs `115645` and `115684` remain independently closed and are not
> relabelled. AURORA remains `introai9` PBS only; never access, query, transfer
> to, submit to or monitor `junjinyong`, and never run GPU work on a login node.

> **2026-08-11 VMR growth-paired structure source lead · schema 9.5
> prospective:** Exact official VMR metadata CSVs establish 22 patient-specific
> cerebral-aneurysm entries, eleven declared growing/stable pairs and 22
> advertised time-resolved surface-VTP result archives totaling 1,998,793,994
> bytes. The three metadata hashes are `d8d43c…`, `9bf79f…` and `0522f4…`.
> Medical images, project ZIPs, result archives and VTP bodies were not opened
> before registration. Patient is the independent unit; pair membership is a
> design variable, while phases, vertices, triangles and extracted structures
> are never counted as patients.
>
> Six prospectively frozen rows score 32.5/30.5/30.5/30.0/26.0/23.0. Only
> `growth_paired_transient_wss_structure_stability` passes schema-8.8's total
> and every non-compensatory floor, exactly at residual novelty 2.5 and
> effective-unit 3.0. This creates one conditional source lead, not an active
> primary, paper identity, growth biomarker, contribution, model or clinical
> claim. Weiss et al. already own WSS/OSI/low-shear and mesh-convergence growth
> analysis; the 481-patient prospective study owns size-dependent WSS growth
> mechanisms. Critical-point tracking, trajectory-preserving vector-field
> methods, SE(3) transient-WSS prediction and Hodge/geometric operators are
> direct priors. Edge 1-form, Hodge/DEC, equivariant GNN, periodic decoder and
> structural loss remain unselected controls rather than novelty.
>
> Exact protocol `configs/vmr_growth_surface_structure_p0.json` registers one
> method-free `introai9` PBS P0 with 4 CPU, 16 GB, GPU 0 and four-hour walltime.
> It checks exact metadata, safe/complete ZIPs, three expected VTP surfaces,
> PolyData, three-component WSS and phase semantics only. It computes no
> critical point, signed degree, worldline, growth association, surrogate or
> model metric and retains no payload. Pass authorizes only registration of a
> separate CPU-only mesh/phase/tolerance/perturbation stability P1. Failure or
> incomplete execution closes this exact version without same-contract repair
> or rerun. At this prospective state P0 is registered but not submitted; no
> scientific server was queried.
>
> Historical jobs `115645.ECE-util1` and `115684.ECE-util1` remain immutable
> execution-incomplete/no-scientific-verdict records and must never be repaired,
> rerun or relabelled. AURORA execution is `introai9` PBS only; never access,
> query, transfer to, submit to or monitor `junjinyong`, and never run GPU work
> on an `introai9` login node. Keep protocol, tests, research docs, Learn,
> Overview, change history and this file synchronized at every state change.
> Prospective registration regression is 425 tests: 359 pass and 66 optional-
> dependency skips; the machine protocol passes 72 invariant groups, site graph,
> JavaScript, PBS shell syntax and diff hygiene.

> **2026-08-11 schema 9.4 deployment·private synchronization:** Exact public
> scientific source `eb9a6ae9db3980ca41814b3852b68fd4a0804c09` passed
> Quality `31493466627` and Pages `31493465268`. Private paper ledger
> `5764bd7f986d1e0a173cb18d168e4aca16676689` is remote exact and PRIVATE.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> Full regression is 352 pass plus 66 optional-dependency skips out of 418.
> This synchronization is provenance only and creates no lead, P0/P1, method,
> architecture, scientific-server query, PBS/GPU, outer test, result row, C21
> or claim. Future authorized execution is `introai9` PBS only; prohibit
> login-node GPU and never access, query, transfer to, submit to or monitor
> `junjinyong`.

> **2026-08-11 latent-shape/open-CTA transport override · schema 9.4:** Exact
> latent-shape paper DOI `10.1016/j.cmpb.2026.109445`은 five-source 958
> saccular surface/338 rupture-status label과 LODO accuracy 0.68, AUC 0.66,
> AE/VAE MSE 0.16/0.14를 이미 보고한다. Low reconstruction error와 weak label
> transport의 분리는 direct-prior result이며 AURORA finding이 아니다. Official
> repo exact `43e8219…`은 MIT code/weights/cache를 제공하지만 processed OBJ,
> `rupture_labels.csv`, complete LODO driver/fold manifest는 없다. Default train
> scripts는 seed-42 file-level 80/20 loader를 사용하고 두 loader의
> `status == "unruptured" or "other"` 조건은 unknown을 0으로 보낸다. 이를
> paper invalidation이나 novelty로 relabel하지 않는다. Exact 3k VAE cache는
> SHA-256 `4ceafa78…`, 885 unique row/734 nonblank status/261 ruptured이며
> paper 958/338과 immutable mapping이 없다. Open CTA metadata는 172 case/122
> lesion/30 miliary/9 ruptured row를 보존하지만 STL/PixelData는 이번 schema에서
> 열지 않았고 expert morphology를 latent-support truth로 쓰지 않는다. Frozen
> scores 29.5/29.0/28.5/28.0/28.0/23.0은 모두 total 또는 novelty/
> identifiability floor를 실패한다. Active lead/primary/P0/P1/method/
> architecture/scientific-server query/PBS/GPU/outer test/result/C21/claim은 0이다.
> Open-CTA physical-grid와 surface-vector no-verdict P0를 repair/rerun하지 않는다.
> Future gate-authorized work는 `introai9` PBS만 사용하고 login-node GPU를
> 금지한다. `junjinyong`에는 절대 접속·조회·전송·제출·모니터링하지 않는다.

> **2026-08-11 schema 9.3 deployment·private synchronization:** Exact public
> scientific source `56b173ef98898fe6d0934f39a253f34ed348288c` passed
> Quality `31490372870` and Pages `31490372720`. Private paper ledger
> `27ca806e4a640cb842d310d5a51e98035bf0b5a5` is remote exact and PRIVATE.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization is provenance only and creates no lead, P0/P1, method,
> architecture, scientific-server query, PBS/GPU, outer test, result row, C21
> or claim. Future authorized execution is `introai9` PBS only; prohibit
> login-node GPU and never access, query, transfer to, submit to or monitor
> `junjinyong`.

> **2026-08-11 SynVA release and synthetic-utility override · schema 9.3:**
> Exact arXiv `2605.17620v1` reports a procedural generator, a claimed 50,000-
> mesh release, 769 processed real samples and eleven synthetic-to-real
> segmentation regimes. These are prior-paper claims, not AURORA results. The
> paper exposes no dedicated versioned SynVA code/data URL, license, checksum
> manifest, generator seeds, exact 40k/10k split or patient-grouped real-test
> manifest; exact public GitHub title/project searches found no release.
> SynVA itself already occupies the obvious synthetic-pretraining utility task.
> Synthetic counterfactual, shape-artifact, patient/institution leakage and
> generic utility/fidelity/privacy/domain-adaptation methods are direct priors.
> Frozen scores 27.5/26.5/26.0/26.0/23.5/23.5 all fail total or critical novelty/
> asset floors and are not repaired. Do not count generated meshes as patients
> or use this source for hemodynamic, rupture, progression or clinical claims.
> Recurring source-watch was not added because no stable official release URL
> exists; a versioned release requests fresh manual source audit only. Active
> lead/primary/P0/P1/method/architecture/scientific-server query/PBS/GPU/outer
> test/result/C21/claim are 0. Surface-vector remains inactive and closed jobs
> remain unrepaired. Future gate-authorized work may use only `introai9` PBS;
> prohibit login-node GPU and never access, query, transfer to, submit to or
> monitor `junjinyong`.

> **2026-08-11 schema 9.2 deployment·private synchronization:** Exact public
> scientific source `fd60885e4e6c5a34c7d65f6ed2c0013a31c15657` passed
> Quality `31487538060` and Pages `31487537080`. Private paper ledger
> `be7d016c222c744acbdf5669b6ac79cdc393bdcb` is remote exact and PRIVATE.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization is provenance only and creates no lead, P0/P1, method,
> architecture, scientific-server query, PBS/GPU, outer test, result row, C21
> or claim. Future authorized execution is `introai9` PBS only; never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-11 reference-provenance and RSNA release-contract override ·
> schema 9.2:** Surface-vector는 inactive falsifiable evaluation question으로만
> 유지한다. Job `115645.ECE-util1`은 E/exit 2, GPU 0, aggregate/raw log/cache 0,
> scientific check 0/10의 execution-incomplete/no-verdict history이며 repair/
> rerun하지 않는다. Edge 1-form/Hodge/SE(3)/periodic operator/structural loss는
> component/control이지 선택 architecture나 novelty가 아니다. Exact RSNA
> registry file `523ffd…`/blob `97b8c1…`은 controlled access, forthcoming Data
> Resource Publication, 4,000+ study/40+ radiologist/18 institution/about 200
> AI-segmentation aggregate만 보고하고 official wiki는 11-byte `Coming soon`
> 뿐이다. 이를 patient, lesion mask, expert revision 또는 clean/noisy pair로
> relabel하지 않는다. Terms, MIRA, S3/image/CSV/mask payload access는 0이다.
> Biased-ruler analysis, weak-reference partial identification, LNMBench,
> active label cleaning과 challenge-ranking robustness는 direct prior다. Frozen
> scores 31.0/31.0/29.5/28.5/28.0/25.5는 모두 total 또는 critical floor를
> 실패하며 사후 수리하지 않는다. Source-watch v11은 15개 public state를
> fail-closed 감시하며 change는 fresh manual source re-audit만 요청한다. Active
> lead/primary/P0/P1/method/architecture/server query/PBS/GPU/outer test/result/
> C21/claim은 0이다. Future gate-authorized execution은 `introai9` PBS만
> 사용하고 login-node GPU command를 금지한다. `junjinyong`에는 절대 접속·조회·
> 전송·제출·모니터링하지 않는다.

> **2026-08-11 schema 9.1 deployment·private synchronization:** Exact public
> scientific source `4619c0e77a02588c0b47d3b615442339f60968b0` passed
> Quality `31484751195` and Pages `31484750528`. Private paper ledger
> `7d506e0e0a614c9067aae7a64293f90668813ea9` is remote exact and PRIVATE.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization is provenance only and creates no lead, P0/P1, method,
> architecture, scientific-server query, PBS/GPU, outer test, result row, C21
> or claim. Future authorized execution is `introai9` PBS only; never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-11 surface-vector + TopAneu version-orbit override · schema 9.1:**
> 전달된 surface-vector 분석은 문제 가설과 평가 순서만 채택한다. Job
> `115645.ECE-util1`은 E/exit 2, 00:27:02, GPU 0, aggregate/raw log/cache 0,
> scientific check 0/10인 execution-incomplete/no-verdict history이며
> repair/rerun하지 않는다. Edge 1-form/Hodge/SE(3)/periodic operator/critical-
> point loss는 선택 architecture나 novelty가 아니다. TopAneu official Git
> history의 immutable 98-case batch와 current 417-scan release는 실제
> annotation version orbit를 제공한다. Metadata-only comparison은 common path
> 87, same image blob 73, changed location JSON blob 53이며 intersection lower
> bound는 39다. 이를 patient pair나 contour revision 수로 부르지 않는다.
> Fresh scores 32.0/31.5/31.5/30.5/28.5/24.5는 모두 기각한다. 32.0 metric
> candidate는 novelty 0.5, revision-aware candidate는 novelty 2.0으로 frozen
> minimum 2.5를 못 넘는다. Terms/individual annotation/image/mask/P0/P1/method/
> architecture/server query/PBS/GPU/outer test/result/claim은 0이다. Source
> watch v10만 current/batch-1 Git trees와 aggregate manifest를 fail-closed
> 감시한다. AURORA future execution은 gate-authorized `introai9` PBS만
> 허용하고 login-node GPU command를 금지한다. `junjinyong`에는 절대 접속·
> 조회·전송·제출·모니터링하지 않는다.

> **2026-08-11 AAA cross-scale source reappraisal · schema 9.0:** Zenodo
> `21868617` revision 4 is a CC-BY-4.0 reproducibility package over six distinct
> GEO cohorts, not a common patient table. GSE205071 contains paired high/low
> wall-stress biopsies from 12 patients but no public CTA/surface/FEA-field/
> biopsy-coordinate contract. Zenodo `21435232` revision 4 and GitHub release
> `v1.0.0` exact `98363a0…` provide an MIT synthetic-AAA/OpenFOAM pipeline based
> on 258 CTA measurements; 182 selected virtual geometries and 364 simulations
> are generated units, not observed patients, and no public real-patient paired
> CFD outer reference exists. Rygiel transient AAA WSS, WSSNet, the source
> geometry--hemodynamics study and regional wall-stress transcriptomics are
> direct priors. Frozen scores 30.0/28.5/26.5/26.5/23.0/22.0 all fail the
> non-compensatory gate; best residual novelty is 0.5/5. Do not select a GNN,
> operator, omics branch or architecture. Do not add these already-public
> rejected records to the recurring watch merely to create activity. Active
> lead/P0/P1/method/architecture/server query/PBS/GPU/outer test/result/claim
> remain 0. Surface-vector stays inactive; jobs `115645`/`115684` remain closed
> no-verdict histories without repair/rerun. Future eligible execution is
> `introai9` PBS only, never login-node GPU. Never access, query, transfer to,
> submit to or monitor `junjinyong`.

> **2026-08-11 schema 8.9 deployment·private synchronization:** Exact public
> scientific source `646698c66c1eed75ecd4466823bb2cc18ed5ca98` passed
> Quality `31479001176` and Pages `31479000353`. Private paper ledger
> `6b3dcb87a2c49e40e07ae2113605362eedcf4f0e` is remote exact and PRIVATE.
> `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`;
> references remain
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization is provenance only and creates no lead, P0/P1, method,
> architecture, scientific-server query, PBS/GPU, outer test, result row, C21
> or claim. Future authorized execution is `introai9` PBS only; never access,
> query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-11 MRIS-Bench target-contract audit · schema 8.9:** Exact public
> HF revision `6f2d6d9…` reports 30,110 rows and exposes eight Arrow shards,
> but the under-review release has no public mask field, patient grouping,
> split, source lineage or annotation protocol. Rows are not independent
> patients, the card MIT tag is not upstream medical-image lineage, and visible
> viewer contradictions are warnings rather than registered error prevalence.
> Six frozen formulations score 24.0/23.5/23.0/22.5/22.0/21.0 and all fail
> several non-compensatory floors. Source watch v9 matches 13/13 exact states
> and a change requests fresh source re-audit only. Surface-vector remains an
> inactive falsifiable question; closed jobs `115645`/`115684` are unchanged.
> No Arrow/image payload, P0/P1, method, architecture, scientific-server query,
> PBS/GPU, outer test, result row or claim was opened. Future gate-authorized
> execution uses `introai9` PBS only; login-node GPU commands are prohibited.
> Never access, query, transfer to, submit to or monitor `junjinyong`.

> **2026-08-11 schema 8.8 deployment·private synchronization:** Exact public
> scientific contract `765916bbfec7304c4813fb485116a7f2b634dbca` passed
> Quality `31476095988` and Pages `31476095342`. Private paper ledger
> `c285781c639fba9240d9c1ec143b59c487d2ea12` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> references SHA-256 remains
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization creates no source lead, P0/P1, method, architecture,
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> work remains `introai9` PBS only; never access `junjinyong` or run login-node
> GPU commands.

> **2026-08-11 open-model transport and admission reappraisal · schema 8.8:**
> Surface-vector는 inactive falsifiable question으로만 유지하며 edge 1-form,
> Hodge/DEC, SE(3), periodic decoder와 structural loss를 architecture나 novelty로
> 선택하지 않는다. MAXIMUS Zenodo revision 10의 1,143,245,289-byte public
> weight bundle, RSNA first-place exact `e1dcdf…`, TAR exact `5e852d…`, IAVS
> exact `2e4008…`, TopAneu exact `018c24…`, OpenNeuro exact `0760bf…`를
> read-only metadata/code state로 재심사했다. Best fresh candidate는 기존 합산
> 기준 32.0/40이지만 residual novelty 0.5/5라 기각한다. Schema 8.8 이후 fresh
> candidate에는 total≥32와 identifiability≥3.5, novelty≥2.5, asset/unit/baseline
> 각각 ≥3.0을 동시에 요구한다. Component stacking과 model naming은 novelty를
> 충족하지 못하며 explicit residual gap+failure mechanism+falsifier가 필요하다.
> 이 규칙은 prospective-only이고 historical score/job verdict를 relabel하지 않으며
> pass도 method-free P0만 연다. Active lead/P0/P1/method/architecture/server query/
> PBS/GPU/outer test/result/claim은 0이다. Future gate-authorized execution은
> `introai9` PBS만 사용하고 login-node GPU command를 금지한다. `junjinyong`에는
> 절대 접속·조회·전송·제출·모니터링하지 않는다.

> **2026-08-11 schema 8.7 deployment·private synchronization:** Exact public
> contract content `d04abd841a553c024c0aa5ba684d93b305773123` passed Quality
> `31473930058` and Pages `31473929481`. Private paper ledger
> `5adc050227c03265c514242776839c7c429329e4` is remote exact, PRIVATE and
> anonymous API returns 404. `paper/main.tex` SHA-256 remains
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b` and
> references SHA-256 remains
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`.
> This synchronization creates no source lead, P0/P1, method, architecture,
> server query, PBS/GPU, outer test, result row, C21 or claim. Future authorized
> work remains `introai9` PBS only; never access `junjinyong` or run login-node
> GPU commands.

> **2026-08-11 surface-vector contract hardening · schema 8.7 prospective:**
> 전달된 분석은 inactive falsifiable question과 E0→E5 순서만 채택한다. Job
> `115645.ECE-util1`은 running이 아니라 E/exit 2, 0/10 check 미평가로 닫힌
> no-verdict history이며 same-contract repair/rerun을 금지한다. Machine contract는
> E1 전 primary를 boundary-margin signed total degree validity와 certificate
> efficiency/abstention으로 제한한다. Critical-point precision/recall, per-frame
> index discrepancy, trajectory distance와 event F1은 mesh·tolerance·perturbation·
> matching stability를 통과한 뒤의 secondary endpoint다. E2의 field-error-matched
> failure 전 structural training loss를 금지한다. Future ISBI result는 fresh
> patient/base-family confirmation, area-weighted field non-inferiority, compute- 및
> field-error-matched control 대비 stable structure superiority, family bootstrap
> uncertainty와 same-coordinate/same-color-scale matched figure를 모두 만족해야
> 한다. Architecture bundle은 novelty가 아니며 failure에 대응하는 one-at-a-time
> minimal intervention만 E3에서 고려한다. Active lead/P0/P1/method/architecture/
> server query/PBS/GPU/outer test/result/claim은 0이다. Future authorized work는
> `introai9` PBS만 사용하고 login-node GPU command를 금지한다. `junjinyong`에는
> 절대 접속·조회·전송·제출·모니터링하지 않는다.

> **2026-08-11 schema 8.6 deployment·private synchronization:** Exact
> scientific content `8d6ac0f1c29f613178817fe1c07e8292e5f1fb79` passed
> Quality `31472138451` and Pages `31472137714`. Private paper ledger
> `2e8e7c37080db942d3d58973f724ae398222cde3` records the rejection and
> remains PRIVATE; `paper/main.tex` SHA-256
> `42738a36feefcdddfad35b7caa876457470a31f0f2057b4e25139350d8a65b8b`
> and references SHA-256
> `5b7d673202784ff6197022855fa0fe04fdbd1de40c67f5684b3bafdad4580aeb`
> are byte-for-byte unchanged. This synchronization creates no source lead,
> P0/P1, method, architecture, scientific-server query, PBS/GPU, outer test,
> result row, C21 or claim. Future authorized execution remains `introai9` PBS
> only; never access `junjinyong` or run a login-node GPU command.

> **2026-08-11 cross-vascular transient-WSS correction · schema 8.6:**
> Rygiel et al.은 100 AAA patient training, 29 patient/118 scan external
> cohort와 1,090 transient CFD로 E(3)-equivariant vector-WSS, TAWSS/OSI,
> BC·remodelling·topology·mesh generalization을 직접 점유한다. Reported
> directional over-smoothing은 plausible mechanism이지 signed degree,
> critical-point/worldline failure evidence가 아니다. Exact stated-code
> repository `2f78bf18…`은 183-byte README 하나, release 0, license null,
> size 0 KiB이며 code/checkpoint/CFD field가 없다. AAA-100 revision 10은
> CC-BY-NC-4.0 geometry/centerline만 공개한다. SANO v1.0은 CC0/141 public
> files지만 12 patient iliac-vein steady CFD이고 원 논문이 geometry fidelity→
> low-WSS를 이미 분석한다. Fresh scores 30.0/29.0/28.5/25.5/23.0/21.5는
> 모두 32 미만이며 lead/P0/P1/method/architecture/server query/PBS/GPU/outer
> test/result/claim은 0이다. Source watch v8은 exact AAA-WSS repository를
> 열두 번째로 감시하고 change 시 baseline-feasibility re-audit만 요청한다.
> Closed jobs `115645`/`115684`는 repair/rerun하지 않는다. Future authorized
> work는 `introai9` PBS만 사용하고 login-node GPU command를 금지한다.
> `junjinyong`에는 절대 접속·조회·전송·제출·모니터링하지 않는다.

> **2026-08-11 schema 8.5 overlay deployment verification:** Exact analysis
> content `8616257d501707df6d26b07841124d426fac6d86` passed Quality
> `31469240409` and Pages `31469239803`. Live Learn and change history expose
> the stricter E0–E5/result-contract distinction and 458-patient qDSA direct
> prior. This is publication provenance only. It creates no source lead,
> P0/P1, method, architecture, scientific-server query, PBS/GPU, outer test,
> result row or claim. Future gate-authorized work remains `introai9` PBS only;
> never access `junjinyong` or run login-node GPU commands.

> **2026-08-11 surface-vector analysis follow-up · schema 8.5 overlay:**
> Application question과 E0→E5 evidence ladder는 유지하지만 “좋은 architecture와
> 성능이면 경쟁력이 있다”는 조건문은 admission 근거가 아니다. Good performance는
> E4/E5에서 fresh patient/family confirmation, field non-inferiority, stable
> structure superiority, bootstrap uncertainty와 matched case figure를 함께 만족할
> 때만 의미가 있다. 458-patient qDSA direct prior는 injection deconvolution+
> standardized reconvolution+six-month occlusion DNN+LIME를 이미 수행하므로
> measurement normalization/explanation도 novelty가 아니다. 새 source/asset gate,
> P0/P1, method, architecture, server query, PBS/GPU와 claim은 열지 않는다.
> `introai9`는 future gate-authorized PBS만 허용하며 login-node GPU command를
> 금지한다. `junjinyong`에는 절대 접속·조회·전송·제출·모니터링하지 않는다.

> **2026-08-11 schema 8.5 deployment verification:** Exact scientific content
> `6ceff3e1f5554a7d640089e14ef6808956b782c9` passed Quality
> `31468054437` and Pages `31468053500`. Live Overview/Learn expose the
> post-treatment 28.5/40 rejection and no-image/no-model/no-compute boundary.
> This provenance creates no P0/P1, method, architecture, scientific-server
> query, PBS/GPU, outer test, result row or claim. Future authorized execution
> remains `introai9` PBS only; never access `junjinyong` or run login-node GPU.

> **2026-08-11 post-treatment reference-linked imaging · schema 8.5:**
> Prospective PETRA/TOF/DSA는 100 patient/100 aneurysm, day-1/6-month pair,
> SAC 72/FD 28과 DSA reference를 제공하지만 raw image는 versioned public
> asset이 아니다. Helsinki는 DWI 119명, 6-month angiographic follow-up
> 113명이지만 researcher-initiated sharing이 불가능하고 FINDATA 공식 결정이
> 필요하다. Public clipped source는 58 patient/72 aneurysm/141 branch의
> 18.5-KB XLSX와 37.3-KB PDF 표이며 raw CTA/TOF/PETRA image가 아니다.
> SelectiveNet, learning-to-defer, conformal risk control, PETRA/UTE/SILENT MRA
> comparison과 published DWI/occlusion tradeoff는 direct prior/control이다.
> Fresh scores 28.5/27.5/26.5/26.5/26.0/24.5는 모두 32 미만이며 score repair,
> P0/P1, method, architecture, server query, PBS/GPU, outer test와 claim은 0이다.
> Surface-vector는 inactive hypothesis로 유지하고 closed jobs `115645`/
> `115684`를 repair/rerun하지 않는다. 이번 update에서 scientific server는
> 조회하지 않았다. Future gate-authorized work는 `introai9` PBS만 사용하고
> login-node GPU command를 금지하며 `junjinyong`에는 절대 접근하지 않는다.

> **2026-08-11 schema 8.4 deployment verification:** Exact scientific content
> `62a3d7f252b1b73bcf4dc4113e6fd27880183be7` passed Quality
> `31459082444` and Pages `31459081698`. Private paper head
> `e659a0bb03e45eafe23e0e1ebb4e8e0d42a9a50b` is remote exact and anonymous
> GitHub API returns 404. Manuscript and references hashes remain
> `42738a36…`/`5b7d6732…`. This provenance creates no scientific or compute
> authority; `introai9` remains the only future eligible server and
> `junjinyong` remains prohibited.

> **2026-08-11 team downstream-utility reappraisal · schema 8.4:** Exact team
> source hashes remain `ad99cc…`/`6d50cb…`; no discussion later than
> 2026-08-02 was found. The real-CFD→surrogate downstream-retention question is
> an evaluation template only. CMHA's 99-patient exploratory negative signal is
> not relabelled as confirmatory and contains no matched surrogate output.
> PointFlowNet, Hemo-MPO, AneuX PINN fusion and task-based functional evaluation
> are direct priors. Dryad rigid/FSI data have one effective anatomy. Frozen
> scores 27.0/25.5/24.0/24.0/23.5/21.5 are all rejected; lead/primary/P0/P1/
> method/architecture/server query/PBS/GPU/outer test/claim remain 0.

> **2026-08-11 source-watch v7:** Exact public PointFlowNet head is
> `5cb4f2545d25b6e8b855806cb3a345b8b1d72594`, release 0, license null,
> README 35 bytes. The repository contains a 14,120,802-byte checkpoint and a
> 538-byte normalization file but no tracked train/val/test manifest or CFD
> payload. A material change requests direct-prior baseline-feasibility review
> only. Never auto-download, repair a score, select a model or open compute.
> This update queried no scientific server. AURORA remains `introai9` PBS only;
> never access `junjinyong` or run login-node GPU commands.

> **2026-08-11 AneuX-derived transient-CFD material audit · schema 8.3:** Exact
> HF metadata `yiyings/transient-dataset` revision `38c574bc…`은 AneuX-derived
> side-wall/bifurcation transient CFD를 새로 확인시킨다. Public API manifest는
> 180+143 topology folder, 322 unique visible ID와 cross-root duplicate
> `SNF365`를 보인다. Manual contact-sharing gate는 수락하지 않았고 tensor,
> mesh, raw README와 commit history는 읽지 않았다. Card에는 patient/base-
> family mapping, tensor/units/phases/BC/solver/split이 없다. Fresh six-way
> screen 28.0/27.5/27.5/27.0/26.0/26.0은 모두 32 미만이므로 기각한다. 이는
> material source-change signal이지 E0 pass나 historical job `115645`의
> repair/rerun 근거가 아니다. Lead/primary/P0/P1/method/architecture/server
> query/PBS/GPU/outer test/claim은 0이다.

> **2026-08-11 source-watch v6:** `configs/source_watch_v6.json`은 immutable
> v5 아홉 source에 위 exact gated metadata를 열 번째로 추가한다. Revision,
> access, license, card 또는 manifest 변화는 fresh source re-audit만 요청한다.
> Automatic terms acceptance/download/score repair/P0/model/GPU/outer test는
> 금지한다. Visible ID는 verified patient나 base family가 아니다. 이 update는
> scientific server를 조회하지 않았고 job을 만들지 않았다. Future eligible
> execution은 `introai9` PBS뿐이며 `junjinyong`은 절대 접근하지 않는다.

> **2026-08-11 source-watch v5 deployment verification:** Exact public content
> `4de91614991dea82441599136dcbf567f0bbc8bd` passed Quality
> `31455085579` and Pages `31455085014`. The validated contract has nine exact
> metadata watches, manual review 0 and no download/terms/P0/P1/model/GPU
> authority. This deployment queried no scientific server and created no PBS or
> GPU job. `junjinyong` was not accessed and remains prohibited.

> **2026-08-11 fail-closed source watch v5:** Historical v4를 그대로 상속하고
> AneuG-Flow HF, Aneurisk WSS Zenodo, LargeIA Zenodo와 TopAneu challenge를
> 추가한 아홉-source metadata contract다. Live read-only refresh는 nine snapshot
> 모두 exact match, manual review 0이었다. AneuG는 `9dd4180…`/2.63 TB,
> Aneurisk는 revision 4와 1,430,889,142-byte/MD5 `8c66e7bb…`, LargeIA는
> revision 10/restricted/public file 0, TopAneu는 revision 4/Data+Evaluation
> navigation/verified-account participation 상태다. 이는 새 scientific evidence나
> E0가 아니며 terms acceptance, score repair, jobs `115645`/`115684` repair·
> rerun, payload/P0/P1/method/architecture/GPU/outer test를 자동으로 열지 않는다.
> Source of truth는 `configs/source_watch_v5.json`과 `docs/source-watch.md`다.
> Scientific server query는 0이고 AURORA는 future gate-authorized `introai9`
> PBS만 사용한다. `junjinyong`에는 절대 접근하지 않는다.

> **2026-08-11 schema 8.2 deployment verification:** Exact content
> `205d3d534a80ef5e3821d321a403158148e68ac5` passed Quality
> `31453522210` and Pages `31453521880`. Live Learn directly exposes the
> schema-8.2 unit/asset/direct-prior correction. Private ledger head
> `138f764f9dae6f6cf1ae8e26f5ae4ad30a45c866` is remote exact and anonymous
> GitHub API returns 404; `paper/main.tex` and references hashes remain
> unchanged. This is provenance only. No scientific server query, P0/P1,
> method, PBS/GPU, outer test or claim is opened.

> **2026-08-11 functional 4D-flow segmentation delta · schema 8.2:** 2026
> intracranial 4D-flow work already evaluates segmentation-to-flow/WSS bias:
> 355 public TOF-MRA pretraining scans, eleven nonpublic clinical 7T 4D-flow
> scans, Circle-of-Willis rather than aneurysm-sac target, static time-averaged
> mask and future-not-current weight release. VAST and COMPASS occupy joint
> physics-aware processing and downstream-metric certification. Frozen scores
> 25.5/24.5/23.5/23.5/23.5/23.0 are all rejected without repair. Do not count
> 355 as functional patient units or promote a promised checkpoint to an asset.
> Surface-vector remains inactive and jobs `115645`/`115684` remain closed
> no-verdict histories. Lead/primary/P0/P1/method/architecture/GPU/outer test/
> claim are zero.

> **2026-08-11 source watch v4:** exact IAVS, TopBrain, TRELLIS, Aneumo GitHub
> and Aneumo Hugging Face metadata all match frozen snapshots. Aneumo GitHub is
> exact `701d53dd…`, release 0, license null; Hugging Face is exact
> `f801adee…`, 370 entries, `CC-BY-NC-ND-4.0`, with no real/undeformed/AneuX/
> mapping filename marker. A maintainer's planned linked real-case release is
> not E0. Changes request manual source re-audit only; never auto-download,
> score repair, P0, method, GPU or outer test. No scientific server was queried.
> `introai9` is the only future execution server; `junjinyong` remains strictly
> prohibited.

> **2026-08-11 adjudication deployment verification:** Exact adjudication
> content `9d3280c8e5946134eddf2d1791e2a9fb18d8151d` passed Quality
> `31451731627` and Pages `31451730835`. Private paper ledger head
> `382d1d77f3a66ec36df0d8c2170e6c53bd0b78cb` is PRIVATE and pins that public
> source; manuscript and references remain unchanged. Live Overview and Learn
> expose the accepted/corrected/rejected split and state that all ten checks
> were unevaluated rather than scientific failures. This is provenance only and
> opens no lead, P0/P1, model, server query, PBS/GPU, outer test or claim.

> **2026-08-11 surface-vector external-analysis adjudication:** 전달된 분석의
> application question과 evidence ladder는 채택하되 architecture 제안은 채택하지
> 않는다. Field-error와 critical organization의 불일치 가능성은 inactive
> hypothesis이고 아직 관측된 result가 아니다. Exact point/worldline은 mesh·
> tolerance 안정성 전에는 loss가 아니라 secondary evaluation이며, boundary-margin
> signed total degree와 abstention이 더 먼저 검증될 estimand다. Edge 1-form,
> Hodge/DEC, equivariance, periodic decoder와 structural loss는 direct-prior
> component/control이지 novelty가 아니다. Jobs `115645`와 `115684`는 모두
> execution-incomplete/no-verdict로 닫혀 repair/rerun하지 않는다. Active lead,
> primary, P0/P1, method, architecture, server query, PBS/GPU, outer test와 claim은
> 0이다. Exact adjudication은
> `docs/surface-vector-analysis-adjudication-2026-08-11.md`를 따른다. AURORA는
> `introai9`만 사용하고 `junjinyong`에는 절대 접근하지 않는다.

> **2026-08-11 schema 8.1 deployment verification:** Exact public source
> `6de391eafcabea5ba398c49892353a8a707565d1` passed Quality
> `31450399461` and Pages `31450398671`. Private paper head
> `567a995b7ce09887ffe3c480ce09f06b4d42fc0d` is PRIVATE, remote-exact and
> pins that source; manuscript and references remain unchanged. This
> provenance update changes no score, lead, P0/P1, method, architecture,
> scientific-server query, PBS/GPU, outer test or claim. AURORA remains
> `introai9`-only and `junjinyong` remains prohibited.

> **2026-08-11 cross-view projection source delta · schema 8.1:** Fresh MIDL
> cross-view, clinical SDAN, RibAssist 3D, conformal landmark/inverse-problem
> UQ, ProVLNet and quantitative-DSA evidence yields a best score of 31.0/40.
> ADAM views are deterministic MRA-derived MIPs, not acquired biplane DSA;
> SDAN data are non-public; correspondence-gated triangulation, conformal 3D
> regions and abstention are direct prior. All six candidates are rejected
> without score repair. Patient payload, terms acceptance, P0/P1, method,
> architecture, server query, PBS/GPU, outer test, result row and paper identity
> are 0. Historical jobs `115645.ECE-util1` and `115684.ECE-util1` remain closed
> and are not repaired/rerun. Future work requires a material paired clinical
> asset. AURORA remains `introai9` PBS only; never access `junjinyong`.

> **2026-08-11 schema 8.0 deployment verification:** Exact outcome content
> `6123f0e917f084aad0bf352306ba9cf70f57e835` passed Quality
> `31448501704` and Pages `31448501265`. Live Overview, Learn, machine protocol
> and the execution record expose the same 32.5/40 closed history, 0/10
> no-verdict and lead/primary/method/architecture/GPU/outer-test/claim 0.
> This is publication provenance only. It does not reopen the exact P0 or
> authorize a server action; `introai9` remains the only eligible AURORA PBS
> server and `junjinyong` remains absolutely prohibited.

> **2026-08-11 conformal-degree P0 outcome · schema 8.0:** Exact public source
> `4a0fa65b37d69696ff232420e09c4560349fd27b` ran once on `introai9` PBS as
> CPU-only job `115684.ECE-util1`; final state is `E`, exit 2, walltime
> 00:40:06, CPU 00:00:01, memory 56,812 kB and GPU 0. The 323-byte private
> status (SHA-256 `c03716ad…`) and 971-byte bounded private result (SHA-256
> `7e9f04e2…`) say `execution-incomplete/no scientific verdict` and report only
> `AneuriskConformalDegreeP0Error`. All 10 scientific checks are unevaluated.
> Complete archive integrity, VTP header access and a scientific aggregate were
> not reported; transient partial download bytes are unknown. No archive/VTP
> file or raw PBS log persisted, so do not invent a low-level transport or
> reader cause. Preserve 32.5/40 as source history but close the exact candidate
> without repair/rerun, P1, method, architecture, GPU, outer test, result row,
> C21 or submission identity. Active shortlist and conditional lead are 0;
> final `qstat -u introai9` was empty. Source of truth is
> `results/aneurisk_conformal_degree_p0_execution_20260811.json`. No login-node
> GPU command ran. `junjinyong` was not accessed and remains absolutely
> prohibited for AURORA.

> **2026-08-11 patient-level conformal-degree source lead · schema 7.9:** Fresh
> problem-level red team은
> `patient_level_conformal_degree_certificate_for_surface_wss_surrogates`를
> **32.5/40**으로 조건부 입장시켰다. 이는 historical surface-vector
> 31.0/40 또는 `115645.ECE-util1`의 32.0/40·0/10·no-verdict를 사후 수리한
> 것이 아니다. 새 estimand는 exchangeable patient 단위의 simultaneous tangent-
> field residual coverage, signed **total degree** certificate correctness와
> certificate efficiency/abstention이다. Whole-field conformal event에서
> predicted boundary margin이 calibrated radius보다 큰 region만 true/predicted
> degree equality를 인증한다. Nonzero degree는 최소 한 zero의 존재만 뜻하며
> exact critical-point 수·좌표·type, conditional/per-point coverage, 임상 위험을
> 보장하지 않는다. UAI-2025 functional surrogate prediction sets, functional
> conformal distance fields, conformal neural operators, uncertain vector-field
> topology와 multilevel robustness는 direct prior다. Exactly one method-free
> `introai9` CPU/PBS P0만 등록한다: Zenodo 19455127 revision 4의
> 1,430,889,142-byte/MD5 `8c66e7bb…` tar.gz를 job-local scratch에 받아 safe
> inventory, 76 case, VTP PolyData/3-component cycle-averaged WSS, units와
> age/inflow input semantics만 검사한다. Critical-point extraction, conformal
> calibration, model, architecture, GPU, outer test, result row, C21과 submission
> identity는 0이다. Pass도 별도 CPU-only method-free P1 stability 등록만
> 허용하며 fail/incomplete는 같은 contract의 repair/rerun 없이 닫는다. Source
> of truth는 `docs/conformal-degree-certificate-source-audit-2026-08-11.md`,
> `configs/aneurisk_conformal_degree_p0.json`과 schema 7.9다. AURORA는
> `introai9` PBS만 사용하며 `junjinyong`에는 절대 접속·조회·전송·제출·
> 모니터링하지 않는다. Login node GPU 명령도 금지한다.

> **2026-08-11 schema 7.8 deployment verification overlay:** Exact scientific
> content `720e4c5e441c96bd2b35e31cb2a1a19da0ff6dee` passed Quality
> `31416106615` and Pages `31416105439`. Live Overview, Learn, detailed audit
> and research-data object expose best 31.0/40, all rejected, Hodge-as-baseline,
> evaluation-first critical structures and archive/VTP/P0/method/architecture/
> GPU 0. This publication record neither changes the score nor opens a server
> action. No scientific server was queried. Future gate-authorized work is
> `introai9` PBS only; never access or monitor `junjinyong`.

> **2026-08-11 structure-faithful WSS reappraisal override · schema 7.8:**
> Surface-vector WSS는 폐기하지 않지만 active paper identity도 아니다. Fresh
> Aneurisk/CFD-Challenge/RHSIA six-way screen은
> **31.0/30.0/29.0/28.5/27.5/27.0**으로 모두 32 미만이다. Aneurisk v1은
> 76 geometry와 CC BY 4.0 VTP archive를 보고하지만 public manifest는 array,
> phase, alignment, critical-point annotation/tolerance를 열거하지 않는다.
> 1,436-byte README만 읽었고 archive/VTP는 접근하지 않았다. Companion paper의
> fixed point와 separatrix는 cycle-averaged WSS 대상이며 cardiac-cycle
> critical-point worldline이 아니다. Hodge/HSD는 proposal이 아니라 mandatory
> strong baseline이고, critical point/worldline은 stability 전에는 loss가 아닌
> evaluation이다. Edge 1-form도 zero/index 보존을 보장하지 않으며 wall boundary
> convention이 필요하다. AneuG code `4a090a0…`/dataset `9dd4180…`는 unchanged;
> historical `115645.ECE-util1`, 32/40, 0/10과 no-repair 판정을 보존한다. Active
> shortlist/primary/P0/P1/method/architecture/GPU/outer test/paper contribution은
> 모두 0이다. Source of truth는
> `docs/structure-faithful-wss-source-reappraisal-2026-08-11.md`와 schema 7.8이다.
> No scientific server was queried. Future gate-authorized execution은
> `introai9` PBS만 사용하며 `junjinyong`에는 절대 접속·조회·제출·모니터링하지
> 않는다.

> **2026-08-11 schema 7.7 deployment verification overlay:** Exact content
> `611848cba1f19675ab850ebc0c9e2bcd8672c0ef` passed Quality
> `31413485546`, Pages `31413484543` and manual Public source watch
> `31413562860`. The watch matched all three frozen snapshots and returned no
> manual review request. This verifies code, publication and public-metadata
> monitoring only; it creates no scientific evidence or authorization. No
> AURORA server was queried. Future eligible execution is `introai9` PBS only;
> never access or monitor `junjinyong`.

> **2026-08-11 fail-closed source-watch override · schema 7.7:**
> `configs/source_watch_v3.json`은 IAVS, TopBrain 2.0과 TRELLIS stated-code
> repository를 분리해 감시한다. 2026-08-11 live read-only refresh에서 세
> source 모두 frozen snapshot과 같았다: IAVS는 exact `2e40088d…`의
> README-only 상태, TopBrain은 revision-4 design PDF/under-construction 상태,
> TRELLIS repository API는 HTTP 404다. 따라서 manual review request, source
> re-audit, direct-prior baseline review, payload, P0/P1, method, architecture,
> GPU와 outer test는 모두 0이다. Scheduled/manual GitHub Action은 material
> change나 관측 실패 시 fail closed하며 repository state를 쓰거나 frozen
> snapshot을 자동 갱신하지 않는다. IAVS·TopBrain change는 fresh source
> re-audit만, TRELLIS code availability change는 direct-prior baseline
> feasibility re-audit만 요청한다. 어느 경로도 score repair, download,
> terms acceptance, P0 또는 compute를 열지 않는다. 이 public-metadata
> monitor는 scientific server execution이 아니다. AURORA는 future gate 뒤
> `introai9` PBS만 사용하고 `junjinyong`에는 절대 접속·조회·제출·모니터링하지
> 않는다.

> **2026-08-11 schema 7.6 deployment verification overlay:** Exact content
> `aec4b76a1646a4e3508640a1a0ecb7ac146979cc` passed Quality
> `31411063368` and Pages `31411180740`. Live Overview, Learn and
> `docs/trellis-surface-feature-direct-prior-delta-2026-08-11.md` expose the
> same direct-prior/no-authority boundary. This verifies publication only; it
> does not change a score, source lead, closed P0, method, architecture, server
> query, PBS/GPU, outer test or claim. No AURORA server was queried. Any later
> gate-authorized execution is `introai9` PBS only; never access or monitor
> `junjinyong`.

> **2026-08-11 TRELLIS surface-feature direct-prior override · schema 7.6:**
> TRELLIS-Enhanced Surface Features (`arXiv:2509.03095`, DOI
> `10.1016/j.neuri.2026.100259`) already augments aneurysm point/mesh models
> with 1,024-dimensional features from a 500,000-object non-medical 3D
> foundation encoder. Its AnXplore experiment uses 101 sacs on one uniform
> parent vessel and reports rollout RMSE 7.57→6.09 and 4.03→3.55. It does not
> evaluate transient tangent-WSS critical points, signed index or worldlines,
> and no independent sealed GNN split is stated in the inspected source. The
> stated GitHub URL returned 404 and exact repository search returned zero on
> 2026-08-11. Treat foundation surface features/rendering/concatenation as a
> direct control, not novelty or a material E0 source. Do not change the
> historical 32/40 score or closed 0/10 P0. No payload, checkpoint, candidate,
> P0/P1, method, architecture, server query, PBS/GPU, outer test, result row or
> contribution is opened. Source of truth is
> `docs/trellis-surface-feature-direct-prior-delta-2026-08-11.md` and schema
> 7.6. Use only `introai9` after a future gate; never access or monitor
> `junjinyong`.

> **2026-08-11 measurement-functional inverse-flow source-delta override ·
> schema 7.5:** Bayesian finite-element regression now directly reconstructs
> steady vascular velocity/pressure from noisy under-resolved velocity with
> unknown BC, exact no-slip, a Laplace posterior and WSS uncertainty. This
> removes sparse observation, probabilistic BC, physics reconstruction and WSS
> propagation as standalone novelty. Six fresh formulations score
> **30.0/29.0/28.0/26.5/26.0/25.0**, all below 32. BenchAnXplore is the best at
> 30.0, but its current compact contract is velocity/mask-only, all 105 cases
> share an idealized parent context and all were already used in D0/D0b.
> FlowMRI has ten healthy cerebrovascular volunteers and one reference test;
> CMRx independent use begins after the ISBI deadline; physical aneurysm
> references have one effective anatomy. No new payload, P0, split, model,
> architecture, server query, PBS/GPU job, outer test, result row or paper
> contribution exists. Surface-vector remains inactive—not rejected and not
> activated—and its closed 32.0/40 P0 is not repaired. Source of truth is
> `docs/measurement-functional-inverse-flow-source-delta-2026-08-11.md` and
> schema 7.5. Use only `introai9` after a future gate; never access or monitor
> `junjinyong`.

> **2026-08-11 expert virtual-removal source-delta override · schema 7.4:**
> Figshare `1159108` v3 exposes 30 checksum-pinned VTP objects: ten pathological
> cases, ten corresponding expert virtual-removal surfaces and ten matched
> controls, totaling 163,634,666 bytes. This corrects the historical pair-
> absence premise only. The removal is investigator-created to mimic a
> pre-aneurysm geometry, not observed same-patient healthy anatomy; the public
> manifest exposes one removal per case although the paper reports a second-
> observer sensitivity analysis. The independent paired unit is 10. The API's
> CC BY 4.0 field conflicts with the description's CC BY-NC 3.0 plus bona-fide-
> researcher restriction, so no VTP payload is accessed. Fresh score is
> **28.5/40**, below 32, and must not be repaired. This is not surface-vector E0
> because it has no phase-resolved WSS field. Active shortlist, P0, method,
> architecture, GPU, outer test, result row and paper contribution remain 0.
> Historical inverse-editing 27/40 and surface-vector 32/40/P0 outcomes remain
> immutable. Source of truth is
> `docs/expert-virtual-removal-pair-source-delta-2026-08-11.md` and schema 7.4.
> No server was queried or job created. Use only `introai9` for any later
> gate-authorized PBS work and never access or monitor `junjinyong`.

> **2026-08-10 surface-vector conditional-assessment override · schema 7.3:**
> The surface-vector idea is retained only as an inactive, falsifiable
> application hypothesis: field-error-matched transient-WSS surrogates may
> disagree on robust signed critical points and cardiac-cycle worldlines. It is
> not an active source lead, primary problem, method, architecture,
> contribution or paper identity. Edge-integrated 1-forms, SE(3) mesh message
> passing, Hodge decomposition, periodic temporal operators and structural
> losses are candidate controls/components, not novelty. The exact 32.0/40
> source score and job `115645.ECE-util1` outcome remain immutable; 0/10 checks
> were evaluated and that contract cannot be repaired, reconstructed or rerun.
> A fresh executable version requires a material official source/asset change;
> changing a wrapper, downloader, retry rule or model name is not new evidence.
> Then E0 source entry, E1 method-free stability, E2 field-error-matched failure
> mechanism, E3 bounded development, E4 fresh confirmation and E5 external
> interpretation must occur in order. Current P0/P1/method/architecture/GPU/
> outer test/submission identity are all 0. Source of truth is
> `docs/surface-vector-conditional-assessment-2026-08-10.md` and schema 7.3.
> AURORA uses `introai9` PBS only; never access or monitor `junjinyong`, and
> never run a GPU command on an `introai9` login node.

> **2026-08-10 surface-vector structure outcome override · schema 7.2:** Exact
> public source `8a06de209892c09fe4adf86a3125a612a5030d9f` was submitted exactly
> once to `introai9` PBS as `115645.ECE-util1`, CPU 4, memory 16 GB, GPU 0.
> Final scheduler evidence is `E`/exit 2, walltime 00:27:02, CPU 00:00:06,
> peak memory 625,780 kB and peak virtual memory 5,076,920 kB. Only a 301-byte
> private status and 588-byte private bounded result materialized. Aggregate
> scientific result, raw PBS output and persistent probe cache are absent, so
> 0/10 registered checks remain unevaluated and the low-level transport/reader/
> runtime cause is unresolved. Preserve the frozen 32.0/40 source score, but
> close this exact candidate as `execution-incomplete/no scientific verdict`.
> Never reconstruct the cause by local repair, never resubmit the same contract,
> and do not open P1, method, architecture, GPU, outer test, result row, C21 or
> submission identity. Active shortlist and conditional lead count are 0.
> ICML-2026 Hodge Spectral Duality, SE(3)-equivariant transient WSS prediction,
> robust critical-point tracking, trajectory-preserving compression and
> aneurysm-specific WSS critical-point tracking are direct priors. AURORA uses
> only `introai9`; never run GPU commands on its login node and never connect,
> query, transfer, submit to or monitor `junjinyong`. Source of truth is
> `results/aneug_surface_vector_structure_p0_execution_20260810.json`, the
> closed audit document and schema-7.2 machine contract.

> **2026-08-10 AneuG target-construction override · schema 7.0:** A fresh
> source-only audit pins official code `4a090a0f12538deef6fcea88b81afe78ce38152e`
> and dataset metadata `9dd418083899deddd93a67f9a6fca7a14304fa36`.
> `new_version/loaders.py` uses `knn_interpolate(k=3)` for coordinates and WSS,
> retains common connectivity, recomputes normals and exposes no explicit WSS
> tangent projection or area/functional conservation. Official training code
> normalizes processed steady data before split, evaluates the test loader each
> epoch and selects the best checkpoint by test MSE; transient splitting uses
> ordered prefix matching. These are target/evaluation risks, not proof of bad
> labels. Conservative remapping, surface-vector transport, conservation laws,
> train-only normalization and test-blind/family-disjoint evaluation are direct
> priors or mandatory controls. Six scores are frozen at
> 31.5/31.0/30.5/30.5/30.0/29.5, all below 32; never round up or repair them.
> Field/mesh payload, P0, method, architecture, PBS/GPU, outer test, C21 and
> result row remain zero. A bounded read-only `qstat -u introai9` was empty; no
> login-node GPU command was run. AURORA uses `introai9` only. Never connect,
> query, transfer, submit to or monitor `junjinyong`. Next work is a fresh
> problem-level source/asset audit, not an AneuG target-construction repair.
> Source of truth:
> `docs/aneug-target-construction-source-audit-2026-08-10.md` and
> `problem_selection.aneug_target_construction_source_audit`.

> **2026-08-10 OpenNeuro P0 outcome override · schema 6.9:** Exact clean
> public source `bb227edc86bf3b68e92b97f120a7918b0753c831` was deployed and
> submitted exactly once to `introai9` PBS as `115622.ECE-util1`, CPU 2,
> memory 4 GB, GPU 0. Final state was `F`/exit 1, walltime 00:02:24, CPU time
> 00:00:00 and memory 15,328 kB. Only a 310-byte private status record
> materialized (SHA-256
> `d5022b2c3ac689e1d36083175c04be87ba71a09f3d4ec2275b8729e089c66444`);
> aggregate result and raw PBS stdout/stderr did not. No registered source
> object was retained and all 10 high-level checks remain unevaluated. The
> low-level transport/scheduler cause is unresolved. Preserve this exact
> version as `execution-incomplete/no scientific verdict`; do not call it a
> data, containment-hypothesis or method failure, and do not repair or
> resubmit it. P1, patient payload, method, architecture, GPU, outer test,
> contribution and submission identity remain unauthorized. Active source
> shortlist is 0; next work is a fresh problem-level primary-source/asset
> audit. Source of truth is
> `results/openneuro_containment_morphometry_p0_execution_20260810.json` and
> schema 6.9 `configs/aurora_v1.json`. AURORA uses `introai9` only. Never
> connect/query/transfer/submit/monitor `junjinyong`, and never execute a GPU
> command on an `introai9` login node.

> **2026-08-10 OpenNeuro containment-morphometry override · schema 6.8:**
> `containment_identified_morphometry_envelopes` is one conditional source lead
> at 32.5/40. It does not learn the real annotation-coarsening mechanism and
> does not treat a weak sphere as a precise lesion mask. The only registered
> object is a method-free metadata P0 over exact OpenNeuro tree metadata,
> dataset description, two small supervision-list blobs parsed with
> `pickletools` opcodes only, and the code license. Patient NIfTI image/mask
> bodies, participant/clinical tables, pretrained models, checkpoints and outer
> test remain unread. The source mapping to verify is 284 public subjects = 246
> weak + 38 precise, with four registered code-only weak subjects and subject ID
> as the sole join because released session strings were rewritten. P0 is one
> exact `introai9` PBS submission, CPU 2/4 GB/GPU 0/20 min. Pass opens only
> registration of a separate method-free P1 task-adequacy audit; fail or
> execution-incomplete closes this version without repair/rerun. Primary,
> method, architecture, contribution, GPU and outer test remain 0. Never
> connect/query/transfer/submit/monitor `junjinyong`; never run GPU commands on
> an `introai9` login node. Source of truth:
> `docs/openneuro-containment-morphometry-source-audit-2026-08-10.md` and
> `configs/openneuro_containment_morphometry_p0.json`.

> **2026-08-10 ISBI author-compliance override · schema 6.7:** The live official
> author instructions are frozen as machine guards: single blind, four
> technical pages, at most two first-author submissions per person, no
> substantially similar prior or concurrent peer-reviewed submission, preprints
> allowed, mandatory ethics wording irrespective of approval need, mandatory
> funding/COI disclosure, and submission link `Coming Soon`. The stale venue
> headline-domain value is corrected to the current BC-transport
> execution-incomplete/no-active-shortlist boundary. This is a format and public
> explanation update only: source lead, primary, method, architecture, GPU,
> outer test, result and submission identity remain 0. AURORA uses only
> `introai9` PBS; never connect/query/transfer/submit/monitor `junjinyong`.

> **2026-08-10 BC-transport P0 outcome override · schema 6.6:** Exact clean
> public source `38e7894fc5ae56ffb3efbe469c4e1f7480f81feb` was submitted once to
> `introai9` CPU/PBS as job `115518.ECE-util1` (CPU 2, 8 GB, GPU 0). Final
> scheduler evidence was E/exit 1, walltime 00:08:21, CPU time 00:00:00 and
> memory 39,160 kB; the job later disappeared and `qstat -u introai9` was empty.
> Only a 275-byte private status artifact materialized (SHA-256
> `5f0c26118e86cc68ed6c494c782e301537b11589565e77996a672c442c266207`).
> Aggregate result and raw PBS output are absent, so source-member completion,
> array parsing, coordinate identity, response energy and analytic-control checks
> are all unevaluated and the low-level cause is unresolved. Preserve the state
> as `execution-incomplete/no scientific verdict`; do not call it a source,
> hypothesis or method failure. The exact P0 is closed with no repair/rerun or
> P1. Active source lead, primary, method, architecture, GPU, outer test,
> submission identity and contribution are 0. Next is a fresh problem-level
> source/direct-prior audit. AURORA remains `introai9`-only; `junjinyong` was not
> accessed and is prohibited for connection/query/transfer/submission/monitoring.
> Exact schema-6.6 outcome content
> `bb16d90d2e06bd1f12972efaf67093d425048d49` passed Quality
> `31375709669` and Pages `31375709322`. Direct live checks of overview, Learn
> and the public execution record show P0 closed/no scientific verdict, active
> lead/P1/method/model/GPU 0 and `junjinyong_accessed=false`. Private paper head
> `b530d51b4e461c883dcc0d9c9e2e24b56cbddb17` pins this public content and the
> repository remains PRIVATE.

> **2026-08-10 anchor-conditioned BC-transport override · schema 6.5:** A fresh
> source/prior red team admits
> `similarity_quotiented_anchor_conditioned_bc_transport` at 33.5/40 as one
> **conditional source lead**. The task takes geometry, one same-geometry anchor
> CFD velocity field at `q0`, and an observed ratio `q/q0`; it predicts the
> target-flow response with exact anchor identity and ratio/path diagnostics.
> This is a one-solve scenario-sweep question, not geometry-only hemodynamics,
> missing patient BC inference, prospective rupture risk or clinical utility.
> Historical V1/V1e failures remain failures. DeltaPhi, scale-consistent neural
> operators, learned boundary extensions, power-law normalization and generic
> cycle consistency are direct priors/controls; residual novelty is only 2/5.
> Exact `configs/aneumo_bc_transport_p0.json` registers one method-free P0 on
> historical train family 1/cases 1–2/all eight flows: 16 CRC-checked members,
> 1,024 deterministic nodes, pressure/validation/test/model/checkpoint/GPU/
> outer-test access 0, persistent field cache 0, one submission only. Pass opens
> only a separate train-only method-free P1; failure or execution-incomplete
> closes the exact P0 without same-contract repair/rerun. There is no selected
> primary, method, architecture, contribution or submission identity.
> **AURORA uses `introai9` PBS only. `junjinyong` is another project's server and
> must never be connected, queried, used for transfer/submission or monitored.**
> Do not run GPU commands on a login node; this P0 is CPU 2/8 GB/GPU 0.

> **2026-08-10 TopAneu code-semantics override · schema 6.4:** The official
> repository remains pinned at `018c243445f99199f484018c4c80575c84c72293`.
> Bounded public-code inspection established that the 52 location leaves already
> encode territory, laterality and branch role; Task 1 preserves repeated class
> IDs as counts; Task 2's active path scores per-class binary volumes and its
> instance branch is disabled; and official test templates accept CTA/MRA images
> but no vessel mask. MIDL-26 training-only automatic anatomy supervision,
> MIDL-22 probabilistic lesion counting, HATs and vessel-aware aneurysm detection
> directly occupy the obvious method components. Preserve the schema-6.3
> 33.0/40 score as historical evidence; do not edit or relabel it. In the fresh
> evidence version the same formulation is 31.0/40 and the six-candidate maximum
> is 31.5/40, so every candidate is rejected below 32. Active shortlist,
> conditional lead, primary, executable P0, method, architecture, GPU, outer
> test, result row and submission identity are all 0. Terms acceptance no longer
> opens P0-R for this rejected formulation. The next permitted work is a fresh
> problem-level primary-source/direct-prior audit, not a TopAneu repair or model.
> No patient image/mask, patient location-JSON content or SWITCHdrive medical
> member was read. Source of truth:
> `docs/topaneu-code-semantics-red-team-2026-08-10.md` and
> `problem_selection.topaneu_code_semantics_red_team`. AURORA may use only
> `introai9` PBS after a future gate; never connect/query/transfer/submit/monitor
> `junjinyong`.

> **2026-08-10 TopAneu deployment provenance:** Exact schema-6.3 scientific
> content `e4038ca6d052def5f275c4118bd904c4ab543135` passed Research contract and
> site quality run `31367056976` and Pages run `31367056610`. The deployed
> overview, Learn guide and detailed audit render 33/40, 417 scans/409 patients,
> terms pending and executable shortlist/payload/P0/model/GPU 0. This deployment
> record changes no access, scientific gate or execution authority.

> **2026-08-10 TopAneu material-release override:** Official TopAneu-26 repo
> commit `018c243445f99199f484018c4c80575c84c72293` and the live challenge now
> define 417 scans/409 patients, 52 location leaves, three aneurysm types,
> location JSON, organizer-predicted silver vessel masks, UMCU held-out test,
> official metrics and a seven-minute/T4 execution contract. The fresh
> `topaneu_factorized_leaf_risk_with_train_only_silver_anatomy` problem scores
> 33.0/40 and is retained only as one **conditional source lead**. It asks
> whether a predeclared territory/laterality/branch-role factorization improves
> patient-level leaf localization plus mask risk on an unseen centre while the
> silver vessel mask is train-time privileged information and test inference is
> image-only. The historical 29/40 attachment candidate remains rejected; do
> not relabel it. The user has not explicitly accepted the TopAneu terms.
> Therefore medical payload/JSON content, executable P0, active shortlist,
> selected primary, method, architecture, GPU, outer test, result row and paper
> contribution are all 0. Terms acceptance, if explicitly confirmed by the
> user, authorizes only prospective registration of a CPU/read-only P0-R; it
> does not authorize automatic download or training. P0-R must close unless all
> 417 mappings, 409-patient grouping, factor map, empty/multiple same-leaf
> support, mask–JSON agreement, silver provenance, centre/source lineage,
> sealed-test boundary and official metric/runtime contract pass. A P0-R pass
> opens only method-free P1. AURORA never connects to, queries, transfers to,
> submits on or monitors `junjinyong`; future authorized execution is PBS on
> `introai9` only. Source of truth:
> `docs/topaneu-release-evaluation-audit-2026-08-10.md` and
> `problem_selection.topaneu_release_evaluation_source_audit` in schema 6.3.

> **2026-08-10 AneuG-Flow P0-v2a outcome override:** Exact clean public source
> `690035ae5385328780fbaace9f956ce142a78f33` ran once on `introai9` as PBS
> CPU job `115467.ECE-util1`. Last observed scheduler state was `E`, exit 1,
> walltime 00:00:08, CPU 00:00:00 and memory 16824 kB; the record later stopped
> returning from `qstat`. The 319-byte status artifact (SHA-256
> `5a3322f2…`) says execution-incomplete before aggregate result. Result JSON and
> raw PBS output did not materialize, so HEAD/range operations, verified bytes,
> transport gate and all scientific checks are unevaluated; low-level cause is
> unresolved. The single repair round is consumed. Do not rerun v2a, open a
> second transport repair, register v2b/P1, select a method/architecture, use
> GPU/outer test or create a paper claim. Public execution source of truth is
> `results/aneug_cycle_transport_p0_v2a_execution_20260810.json`. Active
> shortlist, selected primary, method, architecture and GPU are 0. Future work
> is a fresh problem-level source/asset audit, not local repair. `junjinyong`
> was not accessed and remains prohibited for all AURORA operations.
> Exact outcome content `9632ee5a5e507318fd18bff217c934c30a0b1a02`
> passed Quality `31364095951` and Pages `31364095339`; this deployment
> evidence changes no gate, repair or compute authorization.

> **2026-08-10 AneuG-Flow P0-v2a operational override:** Historical exact
> P0-v1 (`754ed746…`, job `115168.ECE-util1`, exit 28) remains
> execution-incomplete/no scientific verdict and closed. Under the goal's
> bounded validation-development rule, schema 6.2 preregisters one distinct
> transport-only re-entry for the unchanged 33/40 source candidate. The single
> failure hypothesis is that whole-object transfer obscured reachability before
> reader evaluation. The only changed layer is a process-bounded preflight: two
> HEAD requests and four exact 1 MiB ranges, 4 MiB total, retry 0, one repair
> round, `introai9` PBS CPU 2/4 GB/GPU 0/15 min. Local discovery fixed the
> expected headers and range hashes but is not scientific evidence. No full
> object, torch/pickle reader, case ID, method, architecture, GPU or outer test
> is allowed. Pass permits only prospective registration of a separate fixed-
> budget reader P0-v2b; fail closes v2a without another transport repair. The
> current scheduler state is unknown after a connection reset before the
> remote command; no v2a job is yet submitted. Source of truth:
> `configs/aneug_cycle_transport_p0_v2a.json`,
> `docs/aneug-cycle-transport-reentry-2026-08-10.md` and
> `problem_selection.aneug_cycle_transport_reentry_v2a`. `junjinyong` must not
> be connected to, queried, used for transfer/submission, or monitored.

> **2026-08-10 4D-CTA source deployment provenance:** Exact schema-6.1
> scientific content `f95b73a68ddc20b993ebd5dd0d28e4645a3dafc9` passed Quality
> `31359594992` and Pages `31359594475`. Direct live checks of the overview,
> zero-assumption guide, detailed audit and research-data object render
> 31.5/40, 20 independent patients, derived-target semantics and
> archive/P0/model/GPU 0. This deployment evidence creates no source-score,
> task, method, compute, outer-test, C21 or submission authorization. All
> future authorized execution remains `introai9` PBS only; `junjinyong` remains
> completely excluded.

> **2026-08-10 4D-CTA AAA mechanics source override:** Official Zenodo
> `10.5281/zenodo.19182978` is open under `CC BY 4.0` and reports one
> 1,857,980,948-byte archive (MD5 `11b74684e382d1410a2d64f81967e613`), 20
> patients from three centres, 2--10 cardiac phases, wall/ILT surfaces, FE
> meshes and strain/tension/SII/RSII maps. Metadata and primary article text
> were read; ZIP/NRRD/VTP/INP payload access is 0. Six frozen candidate scores
> are 31.5/30.5/30.0/29.0/28.5/25.5, all below 32. Repeated phases/nodes do not
> increase independent patient units, the synthetic displacement truth has one
> effective case, and no future growth/rupture/treatment/wall-strength/histology
> endpoint is released. Schema **6.1** source of truth is
> `docs/four-d-cta-aaa-mechanics-source-audit-2026-08-10.md` and
> `problem_selection.four_d_cta_aaa_mechanics_source_audit`. Active shortlist,
> primary, P0, method, architecture, PBS/GPU, outer test, C21/result row and
> submission identity are 0. One bounded `introai9` status attempt reset before
> remote command, so no current queue observation is claimed and no repair loop
> is opened. AURORA uses only `introai9` PBS after a fresh admitted source and
> separate method-free P0. `junjinyong` must never be connected to, queried,
> used for transfer/submission or monitored for AURORA.

> **2026-08-10 source-metadata correction + operational override:** Official
> TopBrain 2.0 Zenodo revision 4 marks the published design object `open` under
> `CC BY 4.0`; this covers the sole 35-page PDF, not unreleased patient data.
> The live challenge is `Under construction` and offers Join registration but
> no executable Data/Evaluation/Rules/Submission task route. Schema **6.0** and
> `configs/source_watch_v2.json` supersede the older license/submission wording
> without repairing the frozen 29/40 score or opening payload, P0, method,
> architecture, GPU, outer test or C21. The watcher may request only a fresh
> source audit. Any future gate-authorized execution uses `introai9` PBS;
> `junjinyong` must never be connected to, queried, used for transfer or
> submission, or monitored for AURORA.
> Exact schema-6.0 content `545df1b570ea9df6d3feac545bbc0f02cab18178`
> passed Quality `31357501911` and Pages `31357501328`. Direct live checks of
> overview, Learn, change data and the detailed audit rendered the corrected
> license scope, 29/40 rejection and no-P0/model/GPU boundary. This deployment
> evidence creates no scientific or compute authorization.

> **2026-08-10 TopBrain 2.0 source overlay:** Official Zenodo record
> `10.5281/zenodo.19707577` contains one 35-page, 139,840-byte design PDF
> (MD5 `da6c835d…`, SHA-256 `15a2269b…`), not a verified medical-image
> release. The challenge page is `Under construction` with Join registration
> but no executable task-submission contract; a versioned dataset, data license,
> casewise target/lineage and executable 2026 evaluation contract are not
> verified. Planned aneurysm cases are a vessel-anatomy robustness condition,
> not lesion supervision. Six frozen scores are
> 29.0/28.5/28.0/27.5/27.0/23.5, all below 32. Schema 6.0 source of truth is
> `docs/topbrain2-source-audit-2026-08-10.md` and
> `problem_selection.topbrain2_source_audit`. Active shortlist, primary,
> medical payload, P0, method, architecture, PBS/GPU, outer test, C21/result
> row and submission identity are 0. AURORA uses only `introai9` after a fresh
> gate; `junjinyong` must not be connected to, queried, used for transfer or
> submission, or monitored.
> Exact scientific content `8b2a70c9a6bab21962d22b66601481d323e4a52e`
> passed Quality `31354245210` and Pages `31354244348`. Direct live checks of
> overview, zero-assumption guide and detailed audit returned HTTP 200 and
> rendered TopBrain 2.0 best 29.0/40, all rejected, no medical payload/P0/
> model/GPU. This deployment evidence changes no source score, task, method,
> compute or submission authorization.

> **2026-08-10 RSNA AWS registry correction overlay:** Official AWS registry
> YAML blob `97b8c1f…` at file commit `523ffd3…` reports RSNA-ICA as 4,000+
> scans, 40+ radiologists, about 200 AI-segmented studies and 18 institutions.
> It explicitly links `ControlledAccess`; the official wiki remains `Coming
> soon`, the data-resource paper is forthcoming, and its DataAtWork URL points
> to an unrelated pulmonary-embolism paper. User terms, MIRA account/request,
> S3 listing and patient/image/CSV/segmentation/model payload access are 0.
> Public competition code preserves point/presence/territory aneurysm labels
> and 13-class vessel masks, not official aneurysm-extent masks. The frozen
> source score is 31.5/40, so active shortlist, primary, P0, method,
> architecture, PBS/GPU, outer test, C21/result row and submission identity are
> all 0. Schema 5.8 source of truth is
> `docs/rsna-aws-registry-audit-2026-08-10.md` and
> `problem_selection.rsna_aws_registry_correction_audit`. AURORA uses only
> `introai9`; `junjinyong` remains excluded from connection, query, transfer,
> submission and monitoring.
> Exact scientific content `5690b104e6d3fc2644b3d934e12b834ea2c3c3da`
> passed Quality run `31352980950` and Pages run `31352980597`. Direct live
> checks of the overview, zero-assumption guide and detailed audit returned
> HTTP 200 and rendered 31.5/40, `ControlledAccess`, vessel-mask semantics and
> the no-P0/model/GPU boundary. This deployment evidence changes no access,
> scientific or compute authorization.

> **2026-08-10 broad-registry source overlay:** A bounded official-metadata
> screen across Zenodo, DataCite, Figshare and Dryad freezes six candidate scores
> at 30.5/29.5/26.0/26.0/24.5/18.0, all below the unchanged 32/40 admission line.
> LargeIA reports 1,338 internal CTA/1,489 aneurysms from six institutions and
> 138 external CTA/101 aneurysms from two, but files are restricted, no user
> request or terms acceptance occurred, public reader/sealed-test semantics are
> insufficient, and GLIA-Net plus conformal detection are direct priors. The
> 2015 CFD Challenge has 28 submitted datasets from 26 teams but only five
> independent anatomies; the primary paper already owns whole-pipeline WSS
> uncertainty. Longitudinal SIG, aSAH hydrocephalus and VWI are supplement-only
> or directly occupied; synthetic DSA is embargoed past the ISBI deadline.
> Schema 5.7 source of truth is
> `docs/broad-registry-source-audit-2026-08-10.md` and
> `problem_selection.broad_registry_source_audit`. Patient/image/mesh/
> spreadsheet/document/model payload, access request, active shortlist,
> selected primary, P0, method, architecture, PBS/GPU, outer test and submission
> identity are all 0. Only `introai9` PBS may be used after a separately frozen
> >=32 candidate gate; `junjinyong` must not be connected to, queried, used for
> transfer/submission or monitored.
> Exact scientific content `162903a6b66a9982c011fd96d8faf99e92de7eda`
> passed Quality `31351395527`. Pages run `31351394932` also succeeded, although
> its API head metadata remained at the preceding public SHA; direct live checks
> of overview, Learn and the detailed audit returned HTTP 200 and rendered
> broad-registry 30.5/40 with no payload/P0/model/GPU. This deployment evidence
> changes no scientific or compute authorization.

> **2026-08-10 registry-gap source overlay:** The official exact-title Zenodo
> query returned 49 records. Five previously unregistered candidates score
> 26.5/26.0/26.0/25.5/23.5, all below the frozen 32/40 admission line. The best
> record is a public test-only rupture-status blob from a source-reported
> 423-patient lineage; it has no public development cohort, patient/center/raw-
> CTA manifest or prospective endpoint, and TransIAR/GN-Net directly occupy the
> method space. VWE is a 3,572-byte scalar table from 41 unruptured aneurysms;
> vortex-cfd is software without independent patient units; the processed
> transcriptomic record has no casewise imaging bridge; the autopsy record has
> no casewise table or geometry payload. Schema 5.6 source of truth is
> `docs/registry-gap-source-audit-2026-08-10.md` and
> `problem_selection.registry_gap_source_audit`. CSV/PKL/ZIP/image/wall-map/CFD/
> RNA/patient payload, active shortlist, selected primary, P0, method,
> architecture, PBS/GPU, outer test, submission identity and paper claim are 0.
> Closed P0s and failed gates remain closed without local repair or relabeling.
> AURORA may use only `introai9` PBS after a separately frozen candidate reaches
> 32 and passes a method-free P0. `junjinyong` must not be connected to, queried,
> submitted to or monitored for this project.
> Exact registry-gap content `b4c3d48a107b969ce26cbc86abd9b36814116a3a`
> passed Quality run `31349424733` and Pages run `31349424311`. Live overview,
> Learn guide and detailed audit return HTTP 200 and render the same 26.5/40,
> all-rejected, no-payload/P0/model/GPU boundary. Private paper head
> `2403b746e8bbc663f87e08cc8493f5ed31cc85ab` pins this public content and stores
> the batch as unnumbered rejected history without C21 or a result row. The paper
> repository is private and its unauthenticated API response is 404.

> **2026-08-10 method--asset viability source overlay:** Fresh five-candidate
> scores are 30.0/30.0/29.0/26.0/23.0, all below the frozen 32/40 line. Royal
> Brisbane has 63 patients/85 aneurysms and mask/STL outputs, but both outputs
> share one annotation source. ICLR 2026 COMPASS already provides downstream
> segmentation-metric conformal intervals and shift weighting; NeckSpline
> directly occupies topology-preserving neck morphometry and perturbation UQ.
> Neural Operator Processes, learned boundary extensions and amortized
> conditioning directly occupy generic partial-observation operator components,
> while historical N1c decision superiority remains failed. Exact public heads
> remain Royal `0760bf8…`, AneuG-Flow dataset `9dd4180…`, code `4a090a0…`, and
> IAVS `2e40088…`; IAVS remains README-only. RSNA terms are not user-accepted
> and no public per-reader manifest is identified. The cited CQ500-IA Git remote
> is not publicly resolvable. Schema 5.5 source of truth is
> `docs/method-asset-viability-source-audit-2026-08-10.md` and
> `problem_selection.method_asset_viability_source_audit`. Patient payload, P0,
> primary, method, architecture, PBS/GPU, outer test and submission identity are
> 0. Public-key access reached `introai9`/`ECE-util2`; PBS jobs were 0 and no
> login-node GPU command ran. `junjinyong` was not accessed and remains excluded.
> Closed P0s and failed confirmatory results are not repaired or relabeled.
> Exact content `3d21c005bd97b58e87310c3aee9989e91f78e61f`의 Quality
> run `31347355040`과 Pages run `31347354527`이 성공했다. Live `/site/`와
> 상세 audit가 HTTP 200으로 30.0/40, all rejected와
> no-payload/P0/model/GPU 경계를 표시함을 확인했다.

> **2026-08-10 reconstruction/annotation reliability source overlay:** Fresh
> scores는 31.5/29.5/29.0/26.5/25.5/25.5로 모두 32 미만이며 31.5를 사후
> 수리하지 않는다. Di Noto source는 284 subject/198 aneurysm과 weak sphere
> annotation 4× speedup을 보고하고 VP-UNet은 246 coarse-label subject/38
> precise-label test/113 ADAM external subject를 사용한다. 그러나 real weak
> annotation과 independently adjudicated precise mask의 same-subject
> prospective manifest는 public하지 않다. VP-UNet/FocalSegNet, CVPR 2026
> WeakMed, 202-patient ultra-sparse DSA, AutoCAR, 600-model reconstruction
> variability, biplane curve morphing과 phantom consistency가 direct prior다.
> Schema 5.4 source of truth는
> `docs/reconstruction-annotation-reliability-source-audit-2026-08-10.md`와
> `problem_selection.reconstruction_annotation_reliability_source_audit`이다.
> Patient payload, P0, primary, method, architecture, PBS/GPU, outer test와
> submission identity는 0이다. AURORA는 `introai9`만 사용하고 `junjinyong`은
> 접속·조회·제출·모니터링하지 않는다. Closed branch는 repair/rerun하지 않는다.
> Exact content `41d579c0963bd3c7f72c2cd372f1c3cf3dbd77f1`의 Quality
> run `31345064183`과 Pages run `31345063921`이 성공했고 live site와 상세
> audit가 HTTP 200으로 31.5/40, all rejected와 no-payload/P0/model/GPU를
> 표시함을 확인했다.

> **2026-08-10 failure-mechanism/biology source overlay:** Fresh six-candidate
> score는 cause-specific CTA false-positive risk, post-release TopAneu
> attachment, directional topology, synthetic-avatar fidelity, preclinical
> ingrowth translation과 imaging--spatial-wall alignment 순으로
> 30.5/29.0/28.0/25.5/24.5/21.0이다. 모두 frozen admission line 32 미만이며
> score를 사후 수리하지 않는다. 1,186 open CTA/1,373 aneurysm으로 학습한
> direct paper가 anatomy-compartment filtering을 143 private CTA와 843 public
> RSNA CTA에서 이미 검증했지만 reviewed casewise FP-cause label은 public
> target이 아니다. Directional SECT도 small-lesion/bifurcation과 four-
> manufacturer analysis를 직접 점유한다. TopAneu current page는 약 850
> CTA/MRA와 open use with attribution을 명시하지만 verified account가 필요해
> 사용자를 대신해 join/terms를 수락하지 않았다. Human spatial atlas는 14
> aneurysm/11 control vessel과 6/3 spatial donor를 보고하지만 paired
> preoperative image--tissue coordinate manifest가 없다. Preclinical ingrowth
> source는 64 histology image를 쓰며 dataset은 author request이고 public
> angiography--histology pair가 없다. ICAN table은 명시적 simulated clinical
> data다. Schema 5.3 source of truth는
> `docs/failure-mechanism-biology-source-audit-2026-08-10.md`와
> `problem_selection.failure_mechanism_biology_source_audit`이다. Payload, P0,
> primary, method, architecture, PBS/GPU, outer test와 submission identity는
> 모두 0이며 closed Aneumo P0는 repair/rerun하지 않는다. AURORA는
> `introai9`만 사용하고 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.
> Exact audit content `e954d7d8852498d99e7063891d33d36a967e4284`의 Quality
> run `31343371108`과 Pages run `31343370635`는 모두 성공했고, live
> `/aneurysm/site/`와 상세 audit 문서의 HTTP 200 및 30.5/40 판정을 확인했다.

> **2026-08-10 Aneumo generation-lineage P0 outcome overlay:** Exact public
> source `d3eb3d344d284aaae42db1490f2946d54c94029e`의 method-free CPU/PBS
> job `115386.ECE-util1`은 `introai9`에서 final state `F`, exit `-29`, walltime
> `00:20:36`, CPU time `00:00:00`, GPU 0으로 끝났다. 첫 preregistered small
> source가 완성되기 전 종료되어 completed/partial cache와 result JSON은 0이고,
> raw scheduler log도 materialize되지 않았다. 따라서 exact low-level cause와
> 11개 high-level scientific check는 미평가다. Privacy-safe status SHA-256은
> `20755816853044b33dbe54113937e5fec35076a4975494a3a741ab43e4a0ca24`,
> public execution record는 `results/aneumo_lineage_p0_execution_20260810.json`
> (SHA-256 `c10c65766f0f0564cbddb911f10c32a03eb41f4aa7e8adbff99094cb5ad7b30d`)다.
> Exact outcome content `5b98fa296bc7e25f2a3cff97a4a0e3df81c64f8a`의 Quality
> run `31341512723`과 Pages run `31341512255`는 모두 성공했다.
> Historical schema 5.2는 이 candidate version을 `execution-incomplete/no scientific
> verdict`로 닫고 active shortlist, P1, primary, method, architecture, GPU,
> outer test와 submission identity를 0으로 되돌린다. Transport repair와
> same-contract rerun은 금지한다. `junjinyong`은 접속·조회·제출·모니터링하지
> 않았고 앞으로도 AURORA에서 사용하지 않는다.

> **2026-08-10 Aneumo generation-lineage P0 overlay:** Current official Aneumo
> commit `701d53dde3489d84dbe9bc8324254629162eb45a` corrects the explicit
> 10,660-case/427-family mapping. Official steady train has 160 cases from 20
> base families; validation has 40 disjoint case IDs but the same 20 base
> families. Fresh scores are 35.0/31.5/31.0/29.0/27.0/29.5. Only
> `generation_family_disjoint_hemodynamic_operator_model_selection` crosses the
> fixed 32 line. Historical schema 5.1 registered exactly one method-free
> `configs/aneumo_lineage_p0.json`: small pinned text/CSV and two Git LFS pointer
> reads on `introai9` PBS CPU, with archive central-directory/member/LFS-object
> access, method, architecture, GPU and outer test all forbidden. GitHub's
> CC BY 4.0 text conflicts with the pinned Hugging Face card's CC BY-NC-ND 4.0;
> P0 must record—not resolve—the conflict, and P1 remains on license hold.
> Same-contract repair/resubmission is forbidden. `junjinyong` must not be
> connected to, queried, submitted to or monitored for AURORA.

> **2026-08-10 longitudinal-MRA growth deployment overlay:** Exact public
> content `24c95c17042187ad43b0f16b76962f083bc8a053`의 Quality run
> `31338069136`과 Pages run `31338068734`가 성공했다. Live overview는
> best 31.5/40, all rejected, active shortlist/selected primary/model/GPU 0을
> 표시하고 상세 audit도 HTTP 200으로 같은 no-payload/P0/PBS/model/GPU 경계를
> 제공한다. 이 배포 확인은 scientific verdict나 compute authorization을 바꾸지
> 않는다. 향후 실행은 `introai9` PBS만 허용하고 `junjinyong`은 접속·조회·제출·
> 모니터링하지 않는다.

> **2026-08-10 longitudinal-MRA growth source-audit overlay:** Fresh six-
> candidate batch는 acquisition-orbit-calibrated growth, single-anchor local
> growth, interval-censored trajectory, mixed-modality measurement, AWE
> instability와 post-flow-diverter multimodal disagreement를
> 31.5/29.0/30.0/26.5/26.5/26.0으로 판정했다. 모두 frozen admission line 32
> 미만이다. OpenNeuro `ds005096`은 CC0, 63 patient/85 aneurysm/24 longitudinal
> patient/126 raw angiogram path지만 same-session multi-acquisition control은
> 4 patient뿐이고 expert derivative는 subject당 한 selected session에만 있다.
> 2026 Bayesian surface-displacement direct prior는 16 public patient/19
> aneurysm/6 growth를 사용한다. Official article, public Git tree/tag/commit과
> `dataset_description.json`만 읽었고 annotation spreadsheet, participant
> table, sidecar, NIfTI, segmentation, Slicer/STL payload, P0, method,
> architecture, PBS/GPU와 outer test는 0이다. Schema 5.0 source of truth는
> `problem_selection.longitudinal_mra_growth_source_audit`와
> `docs/longitudinal-mra-growth-source-audit-2026-08-10.md`다. 이번 source-only
> stop에 server access는 필요하지 않았다. 향후 실행은 `introai9` PBS만
> 허용하며 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 longitudinal-perfusion deployment overlay:** Exact source
> content `7b03ace12b1e05329e47cd46b6968c0359143daa`의 Quality run
> `31336277131`과 Pages run `31336276517`이 성공했다. Live overview는
> 62 patient/291 exam/873 map과 DCI 9건, best 31.0/40, all rejected,
> active shortlist/primary/method/architecture/P0/PBS/GPU 0을 렌더링한다.
> Field guide의 repeated-CTP beginner window와 상세 audit URL도 HTTP 200으로
> 확인했다. 이 배포 확인은 score, payload, method, compute, outer test 또는
> submission identity를 바꾸지 않는다. `introai9`만 허용하고 `junjinyong`은
> 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 longitudinal-perfusion source-audit overlay:** Fresh source-only
> batch는 informative-scan-aware continuous-time CTP field forecasting,
> pre-DCI early warning, personalized reacquisition, treatment counterfactual,
> 3DRA–CTA hemodynamic invariance와 global–local VWE discordance를
> 31.0/29.0/28.0/27.0/29.5/29.0으로 판정했다. 모두 frozen admission line 32
> 미만이다. Open CC0 CTP는 62 patient/291 original exam/873 map이지만 DCI는
> 9건이며 scan timing이 clinically informative하고 CTP가 rescue treatment를
> 유도한다. ImageFlowNet, longitudinal latent diffusion, TESAR-CDE와 기존
> CTP/NCCT DCI prediction은 direct prior다. 3DRA–CTA와 VWE records는 각각
> 10/41 aneurysm의 tabular summary만 공개하고 primary paper가 association을
> 직접 점유한다. Standalone JSON/spreadsheet/NIfTI/ZIP/CSV/image/mesh/field
> payload, P0, method, architecture, PBS/GPU와 outer test는 0이다. Schema 4.9
> source of truth는 `problem_selection.longitudinal_perfusion_source_audit`와
> `docs/longitudinal-perfusion-source-audit-2026-08-10.md`다. AURORA는
> `introai9` PBS만 사용하며 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 FSI–wall deployment overlay:** Exact source content
> `f92bae804469d806e3d48079246a2a889a97c08a`의 Quality run `31334866427`과
> Pages run `31334866034`이 성공했다. Pages build API의 commit field는 직전
> `d847f28…`을 표시하는 race/stale metadata를 보였지만, live overview와 field
> guide는 FSI–wall best 31.0/40, all rejected, active shortlist/primary/method/
> architecture/P0/GPU 0과 detailed audit link를 렌더링하고 상세 audit URL도
> HTTP 200이다. Live content를 deployment evidence로 기록하되 API commit
> mismatch를 exact-content pin으로 과장하지 않는다. 이 배포 확인은 score,
> payload, P0, model, compute, outer test 또는 submission identity를 바꾸지
> 않는다. `introai9`만 허용하고 `junjinyong`은 계속 완전히 제외한다.

> **2026-08-10 FSI–wall source-audit overlay:** Fresh source-only batch는
> rigid-to-compliant discrepancy operator, dynamic-geometry inverse wall
> property, compliance-conditioned flow-diverter response, lumen-to-wall-
> thickness hotspot, selective FSI referral과 multi-granularity conformal
> surrogate를 30.5/29.5/26.5/24.5/29.0/31.0으로 판정했다. 모두 frozen
> admission line 32 미만이다. AnXplore 논문은 101 semi-idealized rigid/FSI
> simulation을 기술하지만 official repository의 확인된 full-dataset 자산은
> 101 `Fluid_*.vtk` mesh이며 paired time-resolved rigid/FSI solution field
> release가 아니다. Animal inverse mechanics와 five-aneurysm micro-CT wall-
> thickness evidence도 target-scale supervision을 만들지 못한다. Generic FSI
> neural operator, rigid-to-FSI residual learning, conformal field calibration과
> selective referral은 direct prior/control이다. Mesh/field/image payload, P0,
> method, architecture, PBS/GPU와 outer test는 0이다. Schema 4.8 source of
> truth는 `problem_selection.fsi_wall_source_audit`와
> `docs/fsi-wall-source-audit-2026-08-10.md`다. AURORA는 `introai9` PBS만
> 사용하며 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 acquisition–flow source-audit overlay:** Fresh source-only batch는
> nested-acceleration coherence, cross-site/anatomy reconstruction, explicit
> multi-VENC divergence-free uncertainty, functional-risk WSS/vorticity와
> treated-aneurysm device-response transfer를
> 27.5/26.5/24.0/26.0/27.0으로 판정했다. 모두 frozen admission line 32
> 미만이다. CMRx는 138 fully sampled train case와 10/20 cerebrovascular
> validation/test case를 보고하지만 independent research embargo가 2026년
> 12월까지라 ISBI 2027 마감 뒤다. 공식 task와 FlowMRI-Net, DAF-FlowNet,
> VAST가 직접 선행이다. Same-case repeat multi-VENC는 보고되지 않았고 공개
> dual-VENC aneurysm record의 8 scan/4 printed state는 effective anatomy 1이다.
> Synapse application, challenge form, terms acceptance, k-space/MAT, 6.2 GB
> aneurysm ZIP, P0, method, architecture, PBS/GPU와 outer test는 0이다. Schema
> 4.7 source of truth는 `problem_selection.acquisition_flow_source_audit`와
> `docs/acquisition-flow-source-audit-2026-08-10.md`다. AURORA는 `introai9`
> PBS만 사용하며 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 treatment–surveillance deployment overlay:** Exact source content
> `9080f4fea64bbad968e5a2508fa79d1a2f4da4d4`의 Quality `31332304523`과 Pages
> `31332303841`이 성공했다. Live overview와 field guide는 batch best 30.0/40,
> all rejected, active shortlist/primary/method/architecture/P0/GPU 0을 렌더링하고
> detailed audit URL도 HTTP 200이다. 이 배포 확인은 score, payload, P0, model,
> compute, outer test 또는 submission identity를 바꾸지 않는다. AURORA는
> `introai9` PBS만 사용하고 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 treatment–surveillance source-audit overlay:** Fresh source-only
> batch는 observed interval-censored post-flow-diverter occlusion, causal
> Pipeline-versus-Surpass selection, early-complication/delayed-occlusion
> utility, recurrent-procedure sequence와 fast-versus-standard TOF-MRA remnant
> equivalence를 30.0/26.0/29.0/26.0/23.0으로 판정했다. 모두 frozen admission
> line 32 미만이다. Public Mendeley source는 126 subject/141 procedure와 최대
> 두 DSA follow-up을 보고하지만 exact biological occlusion time과 randomized
> device assignment를 제공하지 않는다. Paired MRA는 22 patient이며 Zenodo
> record가 restricted이고 원 논문이 kappa 0.98을 직접 보고한다. Spreadsheet,
> R document, presentation, DSA/MRA/patient payload, P0, method, architecture,
> PBS/GPU와 outer test는 0이다. Schema 4.6 source of truth는
> `problem_selection.treatment_surveillance_source_audit`와
> `docs/treatment-surveillance-source-audit-2026-08-10.md`다. AURORA는
> `introai9` PBS만 사용하며 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 provenance–evaluation deployment overlay:** Exact source content
> `4569c32fbdd19ddf34dac74ef840a8bfc6da080a`의 Quality `31331100581`과 Pages
> `31331100307`이 성공했다. Live overview는 batch best 30.0/40, all rejected,
> active shortlist/primary/method/architecture/P0/GPU 0과 detailed audit link를
> 렌더링하고 상세 문서도 HTTP 200으로 배포됐다. 이 검증은 score, payload
> access, scientific verdict, model, compute, outer test 또는 submission
> identity를 바꾸지 않는다. AURORA는 `introai9` PBS만 사용하고 `junjinyong`은
> 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 provenance–evaluation source-audit overlay:** Fresh source-only
> batch는 cross-release lineage-blocked CFD-to-rupture transfer, source-selective
> prediction, test-blind PointNet++ re-evaluation, HUG curator-lineage
> morphometry와 multiple-aneurysm patient-set consistency를
> 30.0/29.5/28.5/23.5/25.5로 판정했다. 모두 frozen admission line 32 미만이다.
> AneuX는 Aneurisk 101 lesion/97 patient를 포함하고 새 CFD release는 Aneurisk
> 100 case 중 76개를 선별하지만 exact 76-to-101 lineage manifest는 공개 small-
> file boundary에 없다. Public mirror는 24 named model/DICOM folder와 15 label
> file만 노출한다. Generic patient/source-disjoint split, near-duplicate detection,
> contamination matrix, calibration과 domain adaptation은 direct prior/control이다.
> AneuX/CFD archive, DICOM, STL, VTP, spreadsheet, P0, method, architecture,
> PBS/GPU와 outer test는 0이다. Schema 4.5 source of truth는
> `problem_selection.provenance_evaluation_source_audit`와
> `docs/provenance-evaluation-source-audit-2026-08-10.md`다. `introai9` PBS job은
> 0이고 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 context–treatment source-audit overlay:** Fresh source-only
> batch는 AneuSI ordered parent-vessel context, paired black-blood/4D-flow
> treatment response, device-conditioned counterfactual selection,
> morphology-decision-preserving TOF segmentation과 external latent-shape
> calibration을 31.5/27.5/26.0/27.0/30.0으로 판정했다. 모두 frozen admission
> line 32 미만이다. AneuSI는 paper 99 patient/102 case와 repository 103 named
> case가 아직 reconciled되지 않았고, parent-vessel morphology·point-cloud/
> vessel-graph rupture prediction과 latent shape가 direct prior다. Treatment
> MRI는 33/38 scan이 아니라 2 source patient anatomy가 독립 단위다.
> Spreadsheet, VTK, MRI archive, P0, method, architecture, PBS/GPU와 outer test는
> 0이다. Schema 4.4 source of truth는
> `problem_selection.context_treatment_source_audit`와
> `docs/context-treatment-source-audit-2026-08-10.md`다. `introai9` PBS job은
> 0이고 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 topology–procedure deployment overlay:** Exact content
> `3f8e0a5d2c570cfb1c75f22f34d3989fdd5ff71d`의 Quality `31327799890`과 Pages
> `31327799626`이 성공했다. Live overview는 batch best 28.5/40, all rejected,
> active shortlist/primary/method/architecture/P0/GPU 0과 detailed audit link를
> 렌더링하고 상세 문서도 배포됐다. 이 검증은 score, payload access,
> scientific verdict, model, compute 또는 submission identity를 바꾸지 않는다.
> AURORA는 `introai9` PBS만 사용하고 `junjinyong`은 접속·조회·제출·모니터링하지
> 않는다.

> **2026-08-10 topology–procedure source-audit overlay:** Fresh source-only
> batch는 cross-modality tornadic topology, noise/resolution-stable WSS
> skeleton, set-valued C-arm view, differential-diagnosis-aware TOF detection과
> rheology/slip uncertainty를 24.0/28.5/24.0/28.5/28.5로 판정했다. Figshare
> `10.6084/m9.figshare.32270130.v2`는 3 CFD WSS case와 figure용 2 MRI case를
> 보고하지만 same-case pair는 0이고 원 논문이 taxonomy와 in-vivo observation을
> 직접 점유한다. MAXIMUS record는 weights-only, C-arm cohort는 18 patient,
> rheology/slip aneurysm geometry는 1개다. Schema 4.3 source of truth는
> `problem_selection.topology_procedure_source_audit`와
> `docs/topology-procedure-source-audit-2026-08-10.md`다. Large archive/model
> weight/patient image, P0, method, architecture, PBS/GPU, outer test와 submission
> identity는 0이다. `introai9` PBS만 허용하고 `junjinyong`은 접속·조회·제출·
> 모니터링하지 않는다.

> **2026-08-10 hemodynamic–endpoint deployment overlay:** Exact content
> `318a22a06a1a0d1ad8339183f290e1648c656fed`의 Quality `31326443420`과 Pages
> `31326443150`이 성공했다. Live overview는 batch best 31.0/40, all rejected,
> active shortlist/primary/method/architecture/P0/GPU 0과 detailed audit link를
> 렌더링하고 상세 문서도 배포됐다. 이 검증은 score, payload access,
> scientific verdict, model, compute 또는 submission identity를 바꾸지 않는다.
> AURORA는 `introai9` PBS만 사용하고 `junjinyong`은 접속·조회·제출·모니터링하지
> 않는다.

> **2026-08-10 hemodynamic–endpoint source-audit overlay:** New Zenodo
> `10.5281/zenodo.19455127` reports a 1.4 GB CC BY 4.0 archive of OpenFOAM VTP
> surface fields for 76 selected Aneurisk geometries. Inflow uses two
> population-average age-group waveforms scaled by inlet diameter, not measured
> patient-specific conditions; the record's zero-pressure outlet summary and the
> companion paper's resistance-pressure description are not treated as
> equivalent. A frozen five-candidate batch scores curvature-only field surrogate,
> cross-source residual added value, multiple-aneurysm culprit ranking,
> pre/post-treatment remnant change and wall-enhancement/WSS localization at
> 31.0/30.0/23.0/25.0/26.0. All remain below the 32-point line. The companion
> paper directly frames curvature as a hemodynamic proxy, multicenter culprit and
> remnant/wall-enhancement studies directly occupy the other tasks, and public
> endpoint maps or independent patient units are absent. Source of truth is schema
> 4.2 `problem_selection.hemodynamic_endpoint_source_audit` and
> `docs/hemodynamic-endpoint-source-audit-2026-08-10.md`. The archive/payload,
> P0, method, architecture, PBS/GPU, outer test and submission identity remain 0.
> AURORA execution is `introai9` PBS only; `junjinyong` is excluded from
> connection, query, submission and monitoring.

> **2026-08-10 PINN direct-prior deployment overlay:** Exact content
> `ed426a58d556e987c4b5d745d9eb7c88c793a9fe`의 Quality `31325129769`와 Pages
> `31325129336`이 성공했다. Live overview는 23.5/40 rejection, active
> shortlist/primary/method/architecture/P0/GPU 0과 latest audit link를 렌더링하고
> detailed audit URL은 HTTP 200이다. 이는 score, payload, scientific verdict,
> method 또는 compute authorization을 바꾸지 않는다. 실행은 `introai9` PBS만
> 사용하고 `junjinyong`은 제외한다.

> **2026-08-10 PINN rupture-status direct-prior overlay:** July 2026
> `arXiv:2607.10530`이 PointNeXt vascular geometry, geometry-conditioned PINN
> pressure/velocity/WSS/TAWSS/OSI/RRT와 clinical variables를 735 AneuX
> cross-sectional rupture-status lesion에 이미 결합했다. Official AneuX는 750
> lesion/668 vessel tree/605 patient다. Direct-prior primary models는 stratified
> five-fold로만 기술되고 separate tabular importance만 patient-aware라 primary
> patient/vessel grouping은 manuscript에서 미확인이다. PINN은 prescribed shared
> BC를 쓰며 patient-specific BC, paired CFD와 in-vivo validation이 없다. 따라서
> 원래 pipeline은 direct prior이고, physically validated incremental-flow residual
> candidate도 joint asset 부재로 23.5/40이다. Frozen admission line 32 미만이므로
> active shortlist, primary, payload, P0, method, architecture, PBS/GPU, outer test와
> submission identity는 모두 0이다. Public machine source는 schema 4.1의
> `problem_selection.pinn_rupture_direct_prior_audit`와
> `docs/pinn-rupture-direct-prior-audit-2026-08-10.md`다. AURORA 실행은
> `introai9` PBS만 사용하고 `junjinyong`은 접속·조회·제출·모니터링하지 않는다.

> **2026-08-10 vascular-semantics deployment overlay:** Exact audit content
> `f735ab5a2e0eec411142b7834e743d6cf4cd0944`의 Quality `31324138662`와 Pages
> `31324138250`이 성공했다. Live overview와 change data는 best 29.5/40, all
> rejected, active shortlist/primary/method/architecture/P0/GPU 0과
> `introai9`-only/`junjinyong` excluded 경계를 렌더링하며 상세 audit URL은 HTTP
> 200이다. 이 deployment verification은 candidate score, payload access,
> scientific verdict 또는 compute authorization을 바꾸지 않는다.

> **2026-08-10 vascular-semantics source-audit overlay:** Fresh frozen batch는
> TopBrain paired CTA/MRA anatomy, healthy IXI atlas, VesselVerse annotations,
> NeckSpline extension, paired CTA phantom QA와 ADAM longitudinal semantics를
> 29.5/28.5/27.5/26.5/26.0/25.0으로 판정했다. Admission line 32 미만이므로
> active shortlist, selected primary, payload, P0, method, architecture, GPU와
> outer test는 모두 0이다. TopBrain의 공개 독립 단위는 25 paired patient이고
> target은 48-class anatomy이지 aneurysm endpoint가 아니다. VesselVerse의
> “expert”에는 algorithm output이 포함되고 request-gated이며, CTA phantom의
> 126 scan은 one anatomy/three lesion 반복이고 published data URL은 HTTP 404다.
> Source of truth는 `docs/vascular-semantics-source-audit-2026-08-10.md`와 schema
> 4.0의 `problem_selection.vascular_semantics_source_audit`이다. Score repair와
> compute는 없다. AURORA 실행은 `introai9` PBS만 사용하고 `junjinyong`은 접속·
> 조회·제출·모니터링하지 않는다.

> **2026-08-10 INSTED source clarification:** Official Codabench는 INSTED를
> published CC BY-NC challenge로 확인하며 160 train(healthy/IA/stenosis
> 32/64/64), 40 closed test와 signup-gated training Files를 기술한다. BIAS PDF의
> “5-year survival” 문장은 template example이고 실제 target은 3D TOF-MRA의
> IA/stenosis box+segmentation이다. Official code exact `e48a9ba…`만 감사했고
> signup/terms acceptance/payload access는 0이다. Historical IAIA 26.0/40
> rejection은 보존하며 새 score/P0/method/architecture/GPU/outer test를 열지
> 않는다. 이는 source semantics correction이지 closed candidate repair가 아니다.
> Exact content `35e925321b083485b6380b2c37493f499997e3c5`의 Quality
> `31322682231`과 Pages `31322681793`이 성공했고 live change data와 상세
> 문서에서 같은 endpoint/no-score/no-compute 경계를 확인했다.

> **2026-08-10 IAVS watch-only overlay:** Official IAVS paper는 641개 3D MRA,
> 587개 aneurysm–parent-vessel annotation과 CFD outcome을 보고하지만 official
> repository `main` exact `2e40088d9eaa671c592929a154b7b2cf99f9320a`에는
> 90-byte README 한 파일만 있다. Release, explicit repository license와
> code/data payload는 모두 0이다. `configs/source_watch_v1.json`은 이 상태를
> watch-only로 고정하며 source score를 부여하지 않는다. External state가
> 바뀌어도 fresh source audit만 열고 automatic download/terms acceptance,
> P0, method, architecture, GPU와 outer test를 열지 않는다. IAVS의 two-stage
> localization/segmentation과 CFD Applicability Score는 direct prior다.
> `introai9` 접속과 PBS AURORA job 0을 재확인했고 login-node GPU command는
> 실행하지 않았다. `junjinyong`에는 접속·조회·제출·모니터링하지 않았다.
> Exact content `ac6a7075d6607ae29d39e77a87d1ecfbcb87147d`의 Quality
> `31322131949`와 Pages `31322131485`가 성공했고 live overview, deployed
> change data와 source-watch document에서 동일한 경계를 확인했다. 이 배포는
> source score나 scientific authorization을 바꾸지 않는다.

이 파일은 사람과 자동화 에이전트가 동일한 연구 가정과 품질 기준으로
작업하기 위한 단일 운영 메모다. 2026-08-03 KST에 팀 대화, 기존 저장소,
공개 1차 문헌을 재검토하여 작성했고 2026-08-08 KST ISBI V1
backbone gate 5/7 fail, V1a attribution, V1b/V1c/V1d asset audit pass,
V1e known-condition qualification 6/9 fail과 M0 execution-incomplete 상태,
그리고 cross-protocol 4D-flow candidate I0a 14/14 asset pass와 2026-08-09
I0b one-shot execution-incomplete/no-verdict/no-rerun 상태, 같은 날 수행한
problem-level cold audit, CADA·ADAM·IntrA·TopCoW source-only dataset
substitution screen, RSNA supervision-semantics red team으로 그 lesion-set
후보를 기각한 상태, 그리고 2026-08-09 goal-oriented hemodynamic segmentation
cold audit와 S0a preregistration, official precompiled SU2의 reverse-AD
negative control 및 별도 solver preflight 등록, CMHA staging v1
execution-incomplete와 one-change chunked v2 등록, 이어진 v2/solver-preflight-v1
execution-incomplete 보존, `introai9` 기존 CMHA archive 3/3 size·MD5 discovery와
CSV/identifier/NIfTI/STL access 전 asset-component early-stop 등록, inverse
Navier--Stokes shape-gradient segmentation과 task-based quantitative segmentation
평가를 추가 direct prior로 올린 novelty red team, 그리고 exact `ef547a4…`
asset component의 5/9 실패와 goal-oriented 후보 종료를 반영했다.
2026-08-09의 후속 fresh audit은 TopAneu 2026 live release와 registered design,
직접 vessel-aware/artery-aware/taxonomy 선행연구를 대조하고 patient-specific
vascular attachment 가설을 29.0/40의 조건부 lead로만 남겼다. TopAneu terms는
사용자가 수락했다고 확인되지 않았고 payload는 0이다. 별도 open multi-center
CTA는 ZIP64 central directory와 metadata CSV만 range-read했으며 DICOM/STL
payload는 열지 않았다. 같은 날 후속 direct-prior red team은 그 공개 CTA의
physical-coordinate lesion-instance grid-commutation 문제를 32.0/40의
conditional shortlist로 남기고, DICOM header/STL payload 전에 exact P0를
등록했다. Exact `b437875…` one-shot P0는 DICOM undefined-length Procedure Code
Sequence에서 frozen parser incompatibility로 exit 1이었다. Scientific gate는
미평가이고 PixelData/STL access는 0이다. Parser repair/rerun 없이 후보를 닫아
active shortlist는 다시 0이다. 이어서 inverse healthy-vessel counterfactual과
localized aneurysm editing을 하나의 posterior로 역추론하는 후보를 감사했지만,
Aneumo의 released healthy/pathological pair·ostium/edit manifest 부재,
IntrA의 same-patient healthy counterfactual·명시적 repository license 부재와
SynVA/AneuG/counterfactual anomaly·point-cloud reconstruction direct prior 때문에
27.0/40으로 기각했다. Executable P0, method, architecture와 GPU는 0이다.
그 뒤 fresh batch는 AneuG-Flow transient WSS와 cycle functional의 compatibility
문제를 33.0/40의 유일한 조건부 shortlist로 남겼다. Exact steady
9,632,510,050-byte SHA-256 `0c03c1d9…0177f`와 transient 23,744,862,051-byte
SHA-256 `141541ed…51c9` pair를 `configs/aneug_cycle_functional_p0.json`에서
payload access 전에 고정했다. Exact public source `754ed746…`의 `introai9`
CPU/PBS job `115168`은 walltime 00:05:16, exit 28로 종료됐고 payload·partial
file·aggregate가 모두 0이었다. Raw PBS stdout도 materialize되지 않아 exact
shell cause는 unresolved이며 scientific 16-check gate는 미평가다. 등록 계약에
따라 dependency/reader/transport repair, same-contract rerun과 P1을 열지 않고
candidate version을 `execution-incomplete/no scientific verdict`로 닫는다. 이를
source recoverability나 가설의 scientific failure로 relabel하지 않는다. 공개
record는 `results/aneug_cycle_functional_p0_execution_20260809.json`, SHA-256은
`cf2eab0a…90ae`다. Primary problem, shortlist, method, architecture, GPU, outer
test와 submission identity는 모두 0이며 다음은 fresh problem-level source/asset
audit뿐이다.

2026-08-09의 다음 fresh six-candidate red team은 AneuX v1.0의 same-lesion
resolution × cut preprocessing orbit만 34/40으로 admission line 위에 남겼다.
이는 historical source shortlist이며 selected primary는 0이다. Official record와
content-description상 750 lesion, 605 patient, patientID observed 637 row,
3 resolution, 4 cut, area-005 morphometric feature 170개가 보고된다. CSV/model
payload 전 exact `configs/aneux_preprocessing_orbit_p0.json`을 고정했다. P0는
`introai9` PBS CPU 4/16 GB/GPU 0 한 job에서 13 MB tabular ZIP의 exact MD5와
aggregate patient/cut/morphometry mapping, 6.28 GB model ZIP의 HEAD/tail/central
directory exact ranges만 검사한다. Full model download와 member payload access는
금지한다. 한 exact job의 각 HTTP operation에 대한 transient transport attempt 3회 외 same-source
resubmission은 없고, pass도 별도 method-free P1만 허용한다. DiffusionNet,
PointNet++, E(3), generic consistency, precomputed morphometry, MATCH와
multi-resolution latent shape는 novelty가 아니라 direct prior/control이다.
Exact public source `42cc3c7127f382b440f2ac22f662c45692f37863`의
`introai9` CPU/PBS job `115177.ECE-util1`은 exit 2, walltime 00:37:00,
CPU time 00:00:00으로 종료됐고 result는 `transport_attempts_exhausted`였다.
첫 tabular archive가 완성되지 않아 completed/partial cache, CSV parse와 model
HEAD/range/central-directory/member access는 모두 0이며 13개 check는 미평가다.
Raw scheduler log도 materialize되지 않아 low-level exception은 단정하지 않는다.
등록 계약에 따라 transport/reader repair, same-contract rerun과 P1 없이 candidate
version을 `execution-incomplete/no scientific verdict`로 닫았다. Public record는
`results/aneux_preprocessing_orbit_p0_execution_20260809.json`, SHA-256은
`ba547b98…e05a`다. Active shortlist, method, architecture, GPU, outer test와
submission identity는 모두 0이고 다음은 fresh problem-level source/asset
audit뿐이다.

Exact content commit `15bbccbfb367516ee0daaf8d2f5beca20b7c587b`의 Quality
run `31291453002`와 Pages run `31291452634`는 모두 성공했고, live site에서
이 판정과 `introai9`-only/현재 GPU job 0 경계를 확인했다. 배포 확인은
scientific state나 authorization을 바꾸지 않는다.

Exact cycle-functional P0 outcome content `7c6bf9e8c4354f4f3557551a1d7f795265ce069d`의
Quality run `31294677050`과 Pages run `31294676782`도 모두 성공했다. Live
site와 공개 execution record에서 shortlist 0, scientific gate 미평가와
no-repair/no-rerun/P1/model/GPU 경계를 확인했다. 이 배포 검증도 candidate를
재개방하지 않는다.

Exact AneuX P0 outcome content `f4cbf727364325a32f6da148189b976be9d22c6f`의
Quality run `31299794163`과 Pages run `31299793742`도 모두 성공했다. Live site와
공개 execution record에서 active shortlist 0, P0 execution-incomplete/no
scientific verdict, scheduler exit 2, no P1/model/GPU와 fresh problem-audit-only
경계를 확인했다. 이 배포 검증도 candidate를 재개방하지 않는다.

그 다음 fresh six-candidate primary-source red team에서는 DIAS DSA prefix로
final merged vessel support와 thin-vessel miss risk를 추론하는 문제가 최고
31.0/40이었으나 32점 admission line을 넘지 못했다. DIAS는 60 patient/120
sequence, 60 fully annotated sequence와 전문가가 선별한 4--14 arterial-phase
frame을 보고한다. 원 논문의 full-sequence/minimum-projection DSC는
0.7822/0.7802로 차이가 0.0020이다. VSS-Net, DSCA, TemSAM, incomplete-angiogram
temporal recovery, risk-controlled early exit와 conditional conformal risk가
direct prior다. Raw full-phase acquisition, dose/stop action과 frame-level arrival
ground truth가 없어 acquisition stopping을 clinical endpoint로 식별하지 못한다.
Source score repair 없이 기각했고 payload, executable P0, method, architecture와
GPU job은 0이다. Source of truth는
`docs/dsa-prefix-risk-audit-2026-08-09.md`, 당시 판정은 schema 3.9에서도
historical `problem_selection.dsa_prefix_risk_source_audit`로 보존한다.

Exact DSA audit content `4600d9c45b257c99db1c294ca4481724ede0b360`의
Quality run `31301858683`과 Pages run `31301858151`도 모두 성공했다. Live
overview와 상세 설명, 공개 audit 문서에서 31/40 source rejection, active
shortlist 0, no payload/P0/model/architecture/GPU와 `introai9`-only 경계를
확인했다. 이 배포 검증은 candidate를 재개방하거나 scientific state와 실행
권한을 바꾸지 않는다.

2026-08-09 후속 source-delta audit은 OpenNeuro longitudinal surface growth,
RSNA anatomy-indexed point set, VICTORIA neck-curve reader distribution, IntrA
topology control, IAIA aneurysm–stenosis와 flow-diverter DSA outcome을 같은
40점 rubric으로 다시 평가했다. 점수는 31.5/30.5/30.5/28.5/26.0/25.5이며
모두 admission line 32 미만이다. OpenNeuro 최고 후보는 같은 공개 cohort의
Bayesian surface-displacement growth direct prior와 public longitudinal 24 patient
한계가 있다. RSNA controlled terms는 사용자가 수락하지 않았고 새 payload는
0이다. `introai9` 실제 login boundary의 public-key 접속과 PBS AURORA job 0을
확인했으며 bounded read-only inventory에서 IntrA는 repository skeleton만 있었다.
Login-node GPU command는 실행하지 않았고 `junjinyong`에는 접속·조회·제출·
모니터링하지 않았다. Schema 3.9의 source of truth는
`docs/source-delta-audit-2026-08-09.md`와
`problem_selection.source_delta_audit`이다. Active shortlist, primary, method,
 architecture, P0와 GPU는 0이며 31.5를 사후 수리하지 않는다.

Exact source-delta content commit `8d7f7d7d4e41c72eafb1dd08ae27d843ee00fc54`의
Quality run `31303877413`과 Pages run `31303877371`은 모두 성공했다. Live
site에서 best 31.5/40, all rejected, active shortlist/primary/model/GPU 0과 no
current GNN/U-Net/Transformer를 확인했다. 이 deployment verification은 score,
data terms, payload/P0, scientific state 또는 execution authorization을 바꾸지
않는다.

## 1. 연구의 현재 기준선

- 프로젝트명: **AURORA**
- 정식 명칭: **Aneurysm Uncertainty-aware Reconstruction Operator for
  Reliable Assessment**
- 현재 primary problem과 method는 **선택되지 않았다**. Active primary와
  source shortlist는 모두 0이다. 가장 최근 topology-procedure batch의 최고점은
  28.5/40이다. Tornadic taxonomy는 direct prior이고 public unit은 3 CFD + 2
  unpaired MRI figure case, MAXIMUS는 weights-only, C-arm cohort는 18 patient,
  rheology/slip geometry는 1개다. Large archive/P0/model/GPU는 0이다. 직전
  hemodynamic-endpoint batch의 최고 curvature-only surrogate도 31.0/40이며 새
  76-case archive는 내려받지 않았다. 원 논문이 curvature proxy claim을 직접
  점유하고 나머지 endpoint도 direct priors/public-unit 부족으로 기각됐다. 그 전
  direct-prior audit은 원래
  geometry + PINN hemodynamics + clinical rupture-status fusion pipeline이 July
  2026 prior에 의해 점유됐음을 확인했다. Physically validated incremental-flow
  residual도 joint asset 부재로 23.5/40이며 새 payload/P0/model/GPU는 0이다.
  직전 vascular-semantics TopBrain 29.5/40도 기각했고 공개 단위는 25 paired
  patient이며 aneurysm endpoint가 없다. 그 전
  source-delta 최고 OpenNeuro 31.5/40과 DIAS prefix-risk 31.0/40도 기각했다.
  그 이전 AneuX
  preprocessing-orbit 후보는 34.0/40으로
  P0에 진입했지만 initial tabular transport attempt exhaustion으로 scientific
  gate 전에 닫혔다. Complete/partial archive, CSV parse와 model range/member
  access는 0이고 task adequacy는 미확인이다. Same-source repair/rerun과 P1은
  금지한다.
  Cycle-functional transient WSS 후보는 33.0/40으로 P0에 진입했지만
  execution-incomplete로 닫혔고 no-repair/no-rerun 상태다.
  Open-CTA physical-grid 후보의 source-only score
  32.0/40과 registered P0 history는 보존하지만, P0가 execution-incomplete로
  끝나 primary selection이나 contribution이 아니다.
  가장 최근 inverse healthy-vessel counterfactual/editing source audit은
  27.0/40으로 기각했고, 직전 TopAneu attachment source audit도 29.0/40으로
  기준을 통과하지 못했다.
  Goal-oriented
  hemodynamic segmentation은 CTA
  boundary displacement를 PDE adjoint shape sensitivity에 signed projection해
  standardized CFD functional error를 줄일 수 있는지 물었지만 S0a asset
  component에서 5/9 실패해 닫혔다. Method, architecture, GPU, outer test와
  paper identity는 모두 미선정이다.
- 닫힌 goal-oriented 후보의 score는 27.0/40로 자동 선택 기준 32에 못 미친다.
  `configs/goal_oriented_segmentation_s0a.json`의 CPU/read-only S0a가 CMHA
  99 patient/105 lesion exact image–surface–table linkage와 별도 pinned
  solver/adjoint runtime의 11개 check를 모두 통과해야 method-free S0b만
  등록할 수 있다. 같은 version의 dependency/mapping repair rerun은 없다.
- Official SU2 8.5.0 OMP binary는 steady direct QuickStart를 완료했지만
  `DISCRETE_ADJOINT`에서 AD support가 compile되지 않았음을 명시하고
  종료했으므로 S0a에 사용할 수 없다. 이는 S0a 결과가 아니라 등록 전
  negative control이다. `configs/goal_oriented_segmentation_s0a_solver_preflight.json`
  은 exact SU2/TestCases commit과 official GHCR linux/amd64 manifest에서
  normal+reverse-AD runtime을 CPU/PBS로 build하고, fresh incompressible
  forward 뒤 discrete adjoint와 finite nonzero surface sensitivity를 확인한다.
  Preflight도 medical asset, model, GPU, outer test를 읽지 않는다. Exact
  `64284eb`의 v1 실행은 official build SIF와 SU2/11 submodule HEAD를 남겼지만
  TestCases/build/probe 전에 exit 1이었다. PBS stdout은 materialize되지 않아
  exact shell cause는 unresolved이며 runtime/sensitivity와 S0a verdict는 없다.
  같은 v1 source는 재실행하지 않는다.
- Exact public `b6b6175`의 CMHA staging v1 job `115107`은 4 CPU/16 GB,
  GPU 없이 20분 37초 뒤 exit 28이었다. Verified archive와 retained payload는
  0 byte, manifest는 0 byte, raw scheduler stdout은 materialize되지 않았다.
  따라서 원인은 unresolved이고 S0a는 `not_evaluated`다. 같은 v1 source는
  재제출하지 않는다. 사후 bounded transport diagnostic에서 1 KiB와 8 MiB
  range GET은 HTTP 206이었으므로, official ID/size/MD5·extraction·gate boundary는
  그대로 두고 monolithic GET만 64 MiB range chunk로 바꾼
  `configs/goal_oriented_segmentation_s0a_cmha_stage_v2.json`을 한 PBS attempt로
  등록했다. Exact `5cd4aa2`의 v2도 첫 verified chunk 전에 exit 28로 끝났고
  같은 source를 재제출하지 않는다. `results/goal_oriented_s0a_cmha_stage_v2_execution_20260809.json`
  은 chunk/manifest 0 byte와 S0a 미평가를 보존한다.
- 이후 `introai9`의 기존 CMHA source asset을 읽기 전용으로 찾아 세 archive의
  15,557,345,067 byte와 official MD5가 3/3 일치함을 확인했다. 이 login-node
  low-priority checksum discovery는 CSV row, identifier, NIfTI/STL header,
  voxel/field를 열지 않았고 S0a check pass로 세지 않는다. 추가 Figshare
  transport나 raw cross-server transfer는 하지 않는다.
- `configs/goal_oriented_segmentation_s0a_asset_component.json`은 위 discovery 뒤
  CSV/identifier/NIfTI/STL access 전에 고정한 CPU/PBS early-stop overlay다.
  Exact archive, five CSV, 99/105/44/6 unit, non-positional exact-ID linkage,
  NIfTI header와 STL finite/unit/frame, aggregate privacy를 9/9로 검사한다.
  하나라도 scientific fail이면 후보를 닫고 solver v2를 만들지 않는다. 9/9도
  S0a pass나 model 권한이 아니라 no-runtime-network solver-preflight-v2 등록만
  허용한다. Execution-incomplete면 같은 public source를 반복하지 않는다.
- Exact public source `ef547a4ccb71fa45b4a43e67c0939e2701ebfc11`의 CPU/PBS
  asset job `115119.ECE-util1`은 exit 0으로 완료됐지만 **5/9 failed**다.
  Archive integrity, five CSV member set, six multi-lesion group, aggregate privacy와
  no-model/GPU/test boundary만 통과했다. 99 patient-level case directory와 105
  lesion table row 사이의 explicit non-positional key가 없어 required triplet은
  0/105였고 unit count, exact lesion linkage와 그 linkage에 의존하는 geometry
  check는 실패했다. NIfTI/STL header는 열지 않았으므로 geometry 자체 실패라고
  쓰지 않는다. S0a는 `not_evaluated`, 후보는 closed이며 solver v2, S0b,
  method, GPU와 outer test는 모두 금지한다. 공개 aggregate는
  `results/goal_oriented_s0a_asset_component_20260809.json`, SHA-256은
  `c220cb8d92909a5a401b29ad5b75d54f4881d9db4a32ea6f33dd6007e424ad6e`다.
- Automatic segmentation→CFD, Image2Flow의 joint mesh/field CFD loss, IAVS의
  CFD Applicability Score, clDice/cbDice, segmentation-induced flow variability,
  inverse Navier--Stokes shape-gradient boundary segmentation, task-based
  quantitative segmentation 평가, adjoint/shape derivative와 PDE optimization
  일반론은 novelty가 아니다. Multi-functional signed pullback의 first-order
  validity와 remainder control, standard geometry metric과의 비동등성,
  held-out patient functional-error 우위가 모두 있어야만 contribution 후보가
  된다.
- 직전 RSNA-ICA 2025의 annotation-selection-aware mixed-granularity
  lesion-set 후보는 2026-08-09 supervision-semantics red team에서 기각했다.
- 공식 공개 근거에서 제공 `segmentations/{uid}_cowseg.nii`는 aneurysm
  extent가 아니라 13-class Circle-of-Willis 혈관 해부구조다. Aneurysm
  supervision은 annotated series의 center point와 presence/territory label이며,
  공식 voxel aneurysm mask는 없다. 2위 팀의 aneurysm mask는 point box,
  pseudo-label과 manual correction으로 저자가 만든 파생 label이다. 따라서
  서로 다른 granularity의 공식 lesion annotation이 선택된 cohort라는 핵심
  전제가 성립하지 않는다.
- 이 판정은 image/annotation payload 없이 official registry·wiki, 1위 공개
  구현 exact commit `e1dcdf0058e1e0d0044d8053e92243b4b4794555`, 2위
  preprint `arXiv:2606.26706v1`로 확정했다. Anonymous S3 listing은 HTTP
  403, official data wiki는 `Coming soon`이었고 controlled-access 약관은
  수락하지 않았다. Payload read, executable config, split, model code, GPU
  job과 outer test는 모두 0이다.
- CADA·ADAM·IntrA·TopCoW source-only substitution screen은 이 기각을
  되돌리지 않는다. 이들은 향후 fully supervised control 또는 vascular
  anatomy pretraining에 쓸 수 있지만, 기각된 annotation-selection estimand의
  대체 근거가 아니다.
- TopAneu live page는 417 scan/409 unique patient, 52-class location,
  lesion/type mask와 organizer-predicted vessel mask를 기술한다. Vessel mask는
  silver prediction이지 ground truth가 아니다. Verified account와 data terms를
  사용자가 직접 수락했다고 확인되지 않아 image, mask와 JSON payload는 읽지
  않았다. 에이전트가 가입·동의·download하지 않는다.
- ARAN은 patient-specific centerline graph, geometry feature GAT와 artery-aware
  cross-attention을, MICCAI 2024/ICCVW 2025 연구는 soft vessel-distance/vesselness
  prior를 이미 사용한다. Parent-artery classification, joint lesion/vessel
  multitask, universal taxonomy와 hierarchical loss도 단독 novelty가 아니다.
  Attachment에서 mask와 ontology label을 함께 유도하는 가설은 29.0/40의
  conditional lead일 뿐 active candidate, architecture 또는 contribution이
  아니다.
- Open multi-center CTA Zenodo `15697196`은 전체 25,578,845,008-byte archive를
  받지 않고 ZIP64 central directory와 16,458-byte metadata CSV 한 member만
  range-read했다. 149,329 DICOM/122 STL, 172 case/122 lesion/24 multi-lesion
  case와 source-reported 0.5--2 mm thickness를 확인했다. 등록 시점에 DICOM
  header/PixelData와 STL payload는 0이다.
- `configs/open_cta_physical_p0.json`은 clean public commit `b437875…`에서 정확히
  한 번 실행됐다. 일부 DICOM compressed prefix/header semantics 접근 뒤
  `(0008,1032)` undefined-length sequence가 minimal parser 범위 밖이어서 exit
  1이었다. Threaded early exit로 완료 header 수는 미집계다. PixelData를
  decode·inspect하지 않았고 STL payload, raw retention과 identifier publication은
  0이다.
- Scientific 12-check gate는 미평가이고 P1은 unauthorized다. Parser repair,
  same-contract rerun, P0r과 이 후보의 model/GPU/outer test는 금지한다. 이를
  scientific P0 fail이나 data inadequacy로 relabel하지 않는다. Public record는
  `results/open_cta_physical_p0_execution_20260809.json`이다. Goal-oriented S0a,
  solver v2/S0b도 재개하지 않는다.
- Vessel graph/GNN, vessel-first nnU-Net, anatomy-masked pooling, location
  transformer, point-to-sphere auxiliary target, generic set prediction, mixed
  supervision, anatomy prompt, foundation model, soft vessel-distance/vesselness,
  patient-specific centerline GAT, parent-artery classifier, universal taxonomy,
  hierarchy loss, joint lesion/vessel multitask와 conformal/FDR는 단독 novelty가
  아니다. 새 후보에서도 direct prior 또는 strong baseline으로 취급한다.
- 이전 주 연구 문제: **partial/missing physical-condition operator learning**.
  N1c/V1e/M0 evidence 뒤 active paper identity가 아니다.
- 가장 최근 source-rejected candidate는 **noise/resolution-stable WSS
  topological skeleton**이다. Batch tie best 28.5/40이며 independent CFD anatomy
  3개와 self-defined detector target 때문에 기각됐다. 직전 candidate는
  **curvature-only surrogate of local hemodynamic fields**다. 31.0/40이며 direct
  proxy prior 때문에 기각됐다. 그 전 candidate는 **physically validated incremental hemodynamic information
  beyond geometry and clinical variables**다. 원래
  PointNeXt/GNN + PINN + clinical fusion은 direct prior이며, joint asset 부재로
  residual도 23.5/40이다. 가장 최근 execution-closed
  candidate는 AneuX preprocessing orbit이다. Goal-oriented hemodynamic
  segmentation은 S0a asset component의 explicit lesion-level linkage
  precondition이 성립하지 않아 5/9로 종료한 더 이른 history다. 그 직전은
  **annotation-selection-aware mixed-granularity anatomy-structured lesion-set
  inference**다. 제공
  segmentation이 lesion mask가 아니라 혈관 해부구조 mask여서 latent
  annotation-projection 전제가 성립하지 않는다. 그 직전의
  protocol-indexed intracranial 4D-flow posterior prediction도 scientific
  verdict 없이 닫힌 history다.
- 직전 4D-flow 보존 기록: exact public source
  `f7b4e024d69d43cf042f4163342b4d993386f441`의 I0a가 14/14를 통과했다.
  Registration 전에 본 official record, two central directories, nine
  descriptor와 eight primary header를 discovery로 공개했고 processed
  RAW/REC field read는 0이었다. Public aggregate는
  `results/flow_mri_protocol_i0a_asset_audit_20260808.json`이다. 이 pass는
  selective private staging과 learned-method-free I0b의 별도 등록만
  허용했다. I0b는 config SHA
  `e19a1194f1b9ec41861c5084b26c9add5be47924a19aee4d23ffc826399dce06`으로
  field read 전에 고정했다. 2021의 27 processed RAW만 읽고, 새 Zenodo
  `17183575`는 metadata·central directory·33 primary PAR header만 감사한다.
  33 scans의 실제 구조는 5 base geometry, 22 physical model/device state,
  8 multi-VENC state, 2 pump-off scan, 15 device condition과 2 source patient
  anatomy다. Exact source `0ebdb344a6cd4009a928746cda5389b95f12bf8d`의
  PBS job `115093`은 wrapper가 과거에 사용한 read-only `h5py==3.12.1`
  dependency layer를 bind하지 않아 import 단계에서 exit 1이었다.
  Archive/RAW/field/PAR/REC read, cache와 result 생성은 0이고 gate는
  미평가다. Scientific verdict가 아니며 등록된 no-rerun rule을 유지해 I0c와
  dependency repair를 열지 않는다. Method·architecture는 선택하지 않았다.
- 제출 목표: **IEEE ISBI 2027 archival four-page regular paper**,
  2026-10-26 23:59 USA EDT. 현재는 `not submission-ready`다.
- ISBI headline domain과 metric은 아직 선택되지 않았다. Fresh problem
  audit로 데이터·estimand·direct-prior gap을 통과한 active 후보를 만든 뒤,
  method-free task adequacy와 disjoint prospective evidence가 있을 때만 연다.
  Exact/nonlinear PDE나 과거 irregular-3D specification만으로 biomedical-
  imaging contribution을 주장하지 않는다.
- 실행된 exact/nonlinear architecture는 MLP lifted operator다. V1에는
  q-PointNet, 두 kNN graph model과 frame-free anchor-token equivariant
  candidate가 구현·학습됐지만 네 family 모두 validation relative L2 약 1로
  실패했다. 더 큰
  GNN+anatomy-token+continuous-query 구조는 장기 3D target specification이며
  구현·검증된 현재 모델이 아니다.
- Exact public source `0589070`의 metadata-only V0는 8/8 check를 통과했다.
  64-case cache, family split, scalar mass-flow design law와 기존 train-only
  scaling aggregate를 감사했고 새 field array와 validation/test field를
  읽지 않았다. 이는 64-case V1 implementation smoke만 허용하며 learned
  performance, outer test, headline, novelty 또는 submission 증거가 아니다.
  공개 aggregate는 `results/aneumo_isbi_v0_20260808.json`이다.
- Exact task source `a0479fb`의 V1은 12/12 exit 0, no-test-read와 checkpoint
  replay를 통과했지만 aggregate source `78dca92`에서 gate 5/7로 실패했다.
  선택 q-PointNet worst-seed full-q/response L2는 `1.03459/1.00354`로
  frozen `0.35/0.50`을 넘었고 다른 세 family도 약 1이었다. Response-only
  oracle `0.22794`는 true validation anchor를 쓰므로 reconstruction baseline,
  selector 또는 gate가 아니다. Public aggregate는
  `results/aneumo_isbi_v1_20260808.json`이다. Current 3D backbone branch를
  중단하고 hidden size, k, step, seed, loss와 threshold를 국소 수정하지
  않는다. 기존 scheduler/CUDA/aggregate 실패 artifact도 모두 보존한다.
- Exact source `3a0d27f`의 V1a는 기존 12개 checkpoint를 train/validation에서
  read-only replay해 PBS exit 0으로 완료했다. 네 family의 seed-mean train
  full-q L2가 `0.76939--0.95647`로 이미 높고 validation은
  `1.01369--1.02469`다. Train prediction/target norm ratio도
  `0.35004--0.66921`, cosine은 `0.29710--0.61342`여서 실패를 단순
  family-disjoint generalization으로 돌릴 수 없다. Validation truth의
  within-case condition energy fraction은 `0.15748`, same-case condition-mean
  oracle full-q L2는 `0.56843`, true-anchor power response oracle는
  `0.22794`다. 즉 condition signal은 비자명하지만 current geometry-only
  full-field mapping과 네 backbone은 training fit부터 성립하지 않았다.
  Public aggregate는 `results/aneumo_isbi_v1_attribution_20260808.json`이다.
  V1 실패와 current branch 종료를 유지하며, 다음은 새 method가 아니라 새
  task/data identity의 식별 가능성·비자명성 audit이다. V1a에는 success
  threshold, retraining, model selection, V1 relabel, test/V2 권한과 method
  novelty가 없다.
- 기존 “boundary marker가 없다”는 판정은 **64-case compact cache**에만
  해당한다. 2026-08-08 공식 pinned ZIP64 archive 1의 중앙 디렉터리와 case 1
  reference-flow header를 확인해 `.msh`, `.stl`, volume `.vtu`,
  `inlet/outlet/wall.vtp`와 poly connectivity, `U`, `p` array가 실제 존재함을
  발견했다. 이 one-archive discovery는 prospective evidence가 아니다. 이후
  `configs/aneumo_isbi_v1b_boundary_asset_audit.json`에 20 archive·64 case의
  member completeness와 train family당 한 case의 60 VTP CRC/header를
  체계적으로 감사하도록 고정했다. Exact source `fb1c21a`의 CPU audit은
  8/8을 통과했다. 384 required member와 60 train representative payload를
  검증했고 validation/test payload와 field array는 읽지 않았다. Public
  aggregate는 `results/aneumo_isbi_v1b_boundary_asset_audit_20260808.json`이다.
  이 pass가 허용한 범위 안에서
  `configs/aneumo_isbi_v1c_boundary_geometry_staging_audit.json`을 geometry
  array decode 전에 고정했다. Exact source `84fc244`의 V1c는 train family
  representative 20 case의
  세 patch×세 flow, 총 180 VTP에서 `Points/connectivity/offsets`만 읽어
  q-invariance, polygon validity, area/frame와 compact-cache 좌표계를 검사해
  8/8을 통과했다. 60/60 patch가 세 flow에서 exact invariant였고 minimum
  polygon-valid fraction은 1.0이었다. `U/p/TimeValue`, validation/test payload,
  model/checkpoint와 학습은 읽지 않았다. Public aggregate는
  `results/aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json`이다.
  이 pass 범위 안에서
  `configs/aneumo_isbi_v1d_development_geometry_cache.json`을 validation geometry
  payload decode 전에 고정했다. Exact source `369317a`의 V1d는 train
  40·validation 12·test 0 case의
  boundary 468개와 reference-volume 52개 payload에서 geometry array만 읽어
  q-invariance, polygon/frame, compact coordinate bounds와 모든 boundary point의
  exact volume-point correspondence를 검사해 9/9을 통과했다. 156/156 patch가
  q-invariant였고 52/52 case의 surface-volume correspondence와 minimum
  polygon-valid fraction 1.0을 확인했다. Public aggregate는
  `results/aneumo_isbi_v1d_development_geometry_cache_20260808.json`이다.
  이 pass 범위에서 `configs/aneumo_isbi_v1e_known_condition_baseline.json`을
  어떤 V1e training/checkpoint보다 먼저 고정했다. Exact source `c62838b`의
  V1e는 동일 parameter(740,099)와 320 source-token budget의 boundary
  Perceiver와 geometry-only control을 fresh 3 seed·6 GPU task로 비교했고
  모두 exit 0이었다. Boundary는 validation full-q/response에서 3/3 seed로
  control보다 좋았고 seed-mean 상대 개선도 `10.94%/6.41%`로 relative
  checks를 통과했다. 그러나 worst-seed train full-q `0.77221`, validation
  full-q `0.87796`, response `0.94918`이 frozen `0.25/0.35/0.50`을 모두
  넘어 gate는 6/9로 실패했다. Public aggregate는
  `results/aneumo_isbi_v1e_known_condition_baseline_20260808.json`이며 SHA-256은
  `63fdb3a6fbddb15bb8d6cb82fde7b6880e3b3c7badef46b7a4cc2da4d31f2c0e`다.
  Boundary asset의 incremental utility는 인정하지만 known-condition operator
  learnability나 partial/missing method evidence는 아니다. 등록된 결정대로
  architecture, loss, step, seed, threshold를 국소 수정하지 않고 current
  Aneumo 3D learning line을 중단한다. Scalar missing-inflow protocol, V1
  relabel, 기존 backbone 수선, test geometry/field, V2, multicomponent partial
  claim, novelty와 submission은 열지 않는다.
- 의료용 secondary endpoint: 공개 데이터의 **cross-sectional rupture
  status**. 현재 negative G1 signal 때문에 primary contribution이 아니다.
- 핵심 문제: full, partial, missing BC에서 각각 만든 예측이 서로 무관하면
  같은 물리계에 대해 모순된 분포를 낼 수 있다. 하나의 joint BC–solution
  model에서 유도되는 조건부/주변 분포로 일관되어야 한다.
- 현재 검증 중인 방법 틀: analytic conditioning이 가능한 BC density +
  conditional geometry operator + nested observation-mask marginalization.
  Same-geometry paired response supervision은 N1c에서 DeltaPhi-style
  control보다 약해 ablation으로 내렸다.
- 현재 증거: D0 frozen \(K=8\)과 exact G1 absolute gate가 모두 실패했다.
  G1은 direct masked Gaussian보다 모든 mask에서 상대적으로 좋았지만 claim은
  `unsupported`다. G1b에서 \(K=128\) raw projective distance가 iid sampling
  floor와 같고 analytic nesting residual이 \(7.45\times10^{-9}\)임을
  확인했다. 그러나 \(K=2048\) missing-mask mean error는 0.0853이며
  density-only 0.0754가 지배적이므로 G1은 닫힌 상태다. 별도 `G1r`은
  fresh seed, validation-only checkpoint selection, analytic
  density moment/coverage, Gauss–Hermite end-to-end mean, iid-floor-calibrated
  projective metric을 결과 전에 고정한 prospective re-entry다. G1r도
  2026-08-03 fresh 5-seed run에서 실패했다. Coverage, full-BC operator,
  analytic nesting, projective-excess는 통과했지만 최악 seed의 density-only
  mean 0.07533과 end-to-end quadrature mean 0.07518이 기준 0.05를
  넘었다. 다섯 seed 중 두 seed가 mean 기준을 넘었으므로 평균 0.0492를
  근거로 pass라 하지 않는다. 후속 DA1/DA2는 finite condition information이
  병목이며 estimator novelty가 없음을 보였다. 별도 fresh G1s는 G1r 대비
  seed와 training geometry 768→3,072만 바꾸고 7/7 check를 통과했다.
  G1/G1r은 실패로 보존하며 G1s는 data adequacy일 뿐이다. 현재 허용된
  N0는 8/9 check를 통과했지만 worst-seed nonlinear departure가
  0.00727 < 0.01이어서 failed다. N0a attribution 뒤 N0a outcome 전에
  동결한 fresh context-stratified N0r가 9/9를 통과했다. N0 실패는
  보존한다. N1a validation-only 2×2 attribution은
  scale-normalized loss와 2,800-step horizon을 선택했고 full-BC/paired
  validation L2 0.01162/0.01220을 얻었다. 이는 optimization engineering
  evidence일 뿐 gate pass가 아니다. 선택값은
  `configs/nonlinear_pde_n1b.json`에 prospective하게 동결됐다. Exact
  `1d0bd9c`의 다섯 confirmatory seed는 dependency-complete A6000 run에서
  모두 exit 0, checkpoint-eligible, test access false로 완료됐고 50개
  checkpoint와 공통 train-only POD hash를 public manifest에 고정했다.
  AURORA validation full-BC/paired mean은 0.01347/0.01366이지만
  DeltaPhi-style objective보다 좋은 seed는 0/5였고 pair loss도
  pair-zero/random-pair/DeltaPhi 대비 각각 4/5, 3/5, 2/5 방향만 얻었다.
  이는 test 실행 자격이지 superiority나 N1 pass가 아니다. Outer-test
  selector·RNG·estimand·bootstrap은
  `configs/nonlinear_pde_n1c.json`에 별도 prospective overlay로 고정했다.
  Exact source `62605a0`의 dependency-complete contract는 125/125를
  통과했고, PBS A6000 outer test도 exit 0으로 완료됐다. N1c는 failed다.
  Full-BC operator, functional coverage와 AURORA route action consistency는
  통과했지만 field distribution, paired response와 acquisition regret가
  실패했다. Missing/sparse-2 energy score는 independent heads보다 각각
  0.65%/1.09% 나빴고 0/5 seed에서만 우세했다. Missing acquisition
  regret는 ACFlow보다 2/5 seed에서만 낮았고, sparse-2에서는 두 learned
  policy가 모두 oracle과 같아 strict superiority가 성립하지 않았다.
  Pair loss는 pair-zero보다 3/5 seed에서만 좋았고 seed-mean
  paired-response L2도 DeltaPhi-style 0.01221보다 큰 0.01331이었다.
  Route VoI 보조 계산은 route별 Monte Carlo seed offset 때문에 등록된
  common-random-number 계약을 위반했으므로 해당 VoI/next-component
  두 지표만 invalid로 제외한다. 이는 N1 fail을 결정한 field, pair,
  acquisition 지표나 valid route action metric에는 영향을 주지 않는다.
  Registered N1d shift와 irregular 3D는 실행하지 않는다. 다음 단계로
  `configs/nonlinear_pde_n1c_attribution.json`에 결과 전에 고정한
  threshold-free post-result attribution `N1c-a`도 완료했다. 같은 open
  test와 50개 checkpoint만 재사용해 conditional NLL,
  true-density/true-simulator functional floor, acquisition
  8×32/32×64/64×128 stability, corrected CRN true-oracle route regret를
  분해했다. Exact `b97899c`의 A6000 run은 130/130 contract와 5 seed를
  모두 exit 0으로 완료했다. Joint conditional excess NLL은
  missing/sparse-2/partial-4 모두 independent heads보다 0/5 seed로
  열세였다. Functional-energy mean oracle-substitution difference는
  density가 operator보다 missing에서 13.0배, sparse-2에서 5.81배 컸다.
  이는 비가산적 교체 diagnostic이지 causal decomposition은 아니다.
  Missing acquisition은 64×128에서도 ACFlow보다 1/5 seed에서만 좋았고
  sparse-2는 두 방법 모두 oracle과 같아 non-discriminative였다. AURORA의
  route candidate risk는 약 \(3.1\times10^{-8}\) 안에서 일치했지만
  independent heads보다 true-oracle worst-route risk가 낮은 seed는
  3/5뿐이었다. 따라서 joint density/objective가 1차 병목, operator가
  2차 병목이며 현재 paper identity는 unsupported다. N1c failed, paired
  ablation, N1d/3D blocked 판정은 유지한다. 다음 두 development audit은
  결과 전에 별도 config로 고정한 뒤 exact source `337c75e`에서 완료했다.
  Density-objective audit은
  `configs/nonlinear_pde_n1_density_objective_audit.json`에서 N1 seed와
  겹치지 않는 fresh 5 seed, 3,072×8 train, 384×8 selection-validation,
  별도 384×8 audit-validation과 같은 joint 2-GMM·초기 weight·minibatch를
  고정한다. N1c raw random-mask conditional, per-component normalization,
  full-joint per-component, registered-mask composite per-component의 네
  objective를 모두 보고하며 winner를 선택하지 않는다. 다섯 seed가 모두
  exit 0, test access false로 끝났다. Full-joint excess NLL은 N1c raw 대비
  missing 0.06352→0.04622(27.2%), sparse-2 0.07772→0.05923(23.8%),
  partial-4 0.09794→0.07808(20.3%)로 감소했고 세 mask 모두 5/5 seed
  방향이 같았다. Registered composite 개선은 1.5–2.5%로 작았고 단순
  per-component normalization은 일관된 이득이 없었다. 이는 full-joint
  likelihood의 통계효율을 지지하는 engineering evidence이며 method
  selection이나 novelty가 아니다. Decision-task
  audit은 `configs/nonlinear_pde_n1_decision_task_audit.json`에서 learned
  model/checkpoint를 전혀 읽지 않고 true-law/simulator calibration 384×8,
  disjoint 96 context, base 2,048 및 독립 두 outer 32 × inner 64
  replicate로 task adequacy와 Monte Carlo stability를 분해했다. PBS는
  exit 0, walltime 58:04였고 2,882 solver batch가 모두 수렴했다. Missing
  mask는 base risk 0.50366에서 post-acquisition 0.34778/0.34807,
  VoI 0.15587/0.15558, replicate winner agreement 0.9271로 acquisition
  endpoint가 비자명하고 재현 가능했다. Sparse-2도 risk는
  0.33221→0.14704/0.14667로 감소했지만 두 replicate 모두 96/96
  context에서 component 6이 고정 winner였다. 따라서 sparse-2는
  adaptive-policy 비교에서 제외하고 missing만 향후 decision endpoint
  후보로 남긴다. 이 해석은 task pass/fail이나 method selection이 아니다.
  공개 aggregate는
  `results/nonlinear_pde_n1_density_objective_audit_20260806.json`과
  `results/nonlinear_pde_n1_decision_task_audit_20260806.json`이다. 두 결과는
  N1c relabel, method novelty, fresh re-entry 또는 N1d/3D 권한을 열지
  않는다. 이 두 audit과 2024–2026 직접 선행연구를 다시 대조한 뒤,
  missing mask 하나만 다루는 `M0` mechanism gate를
  `configs/nonlinear_pde_n1_missing_operator_pullback_m0.json`에 결과 전에
  고정했다. 표준 full-joint likelihood에 각 후보 BC component와
  solution functional의 joint pushforward
  \(T_j(G,B)=(B_j,\Psi(F(G,B)))\) kernel score를 더한다. Solution
  marginal score만으로는 한 component를 관측했을 때의 VoI를 식별할 수
  없다는 gap을 겨냥하며 acquisition head는 두지 않는다. 세 fresh
  development seed, missing-only audit, full-joint·boundary-kernel·solution
  marginal controls, disjoint selection/audit validation과 9개
  all-required check를 고정했다. 실패하면 weight, kernel, mask, seed,
  threshold를 국소 조정하지 않고 mechanism을 폐기한다. 통과해도 별도
  five-seed fresh re-entry protocol을 설계할 자격만 생기며 method,
  novelty, N1 relabel 또는 3D 권한은 생기지 않는다.
  Exact source `89bdc85`, frozen config SHA
  `78aa6752ed647ffbcb1b90f262873a05156ddda49c6aa21557cc6f7908345f91`의
  PBS array `115078`은 seed 0/2만 exit 0이었고 seed 1은
  `candidate_risk_matrix`의 radius-constrained conditional rejection이
  stall해 exit 1이었다. 등록된 3-seed aggregate를 만들 수 없으므로 M0는
  pass도 fail도 아닌 **execution-incomplete / no scientific verdict**다.
  성공한 두 seed의 metric은 gate를 위해 열거나 선택 집계하지 않았다.
  공개 execution record는
  `results/nonlinear_pde_n1_missing_operator_pullback_m0_execution_20260808.json`이다.
  One-shot 계약에 따라 sampler repair, rerun, M0r, fresh re-entry 또는
  method selection을 등록하지 않으며 이 mechanism branch는 inactive다.
  N1c failed, N1d/3D blocked와 current Aneumo 3D line stopped는 유지한다.
- Fixed Fourier \(K=4/8/12\)는 bulge gate를 통과하지 못했으므로 현재
  one-shot temporal architecture에서 제거한다. Equal-budget nonperiodic
  D0b에서 DCT-II 17/25는 탈락했고 train-only POD 17/25는 모든 frozen
  threshold를 통과했다. POD는 learned compute-matched 후보일 뿐 아직
  선택된 temporal architecture나 novelty가 아니다.
- 최종 주장은 아직 없다. 이전 “불완전한 물리조건 아래의 coherent PDE
  solution distribution”, 4D-flow와 RSNA selection-aware identity는 모두
  unsupported/rejected history로 보존한다. 새 candidate도 task audit와 fresh
  strong-baseline evidence 전에는 contribution 문구로 쓰지 않는다.

다음 아이디어는 주 방법론이 아니다. 비교·ablation으로만 남긴다.

- In-PI-MGN에 attention, node masking, V/W-cycle을 단순 추가
- geometry-only case에 deterministic WSS/OSI를 정답처럼 부착
- 1-step 또는 50-step velocity RMSE만으로 임상 유용성 주장
- ruptured/unruptured label을 2년/5년 prospective risk로 표현
- 서로 다른 공개 데이터셋을 파일명 유사성만으로 patient-level 병합

## 2. 현재 contribution 가설

현재 확정 contribution, prospective method hypothesis와 active source shortlist는
없다. 직전 AneuX 후보 가설은 same-lesion preprocessing orbit을
명시적 equivalence class로 quotient하면서 casewise functional/prediction
stability와 source-held-out between-lesion signal을 함께 보존할 수 있는가이다.
Exact P0가 scientific gate 전에 execution-incomplete로 닫혔고 P1은 열리지
않았으므로 inactive history이며 contribution이 아니다.
닫힌 Open-CTA P0 가설은 하나의 physical-coordinate lesion-instance representation에서 grid별
cardinality·surface·morphometry가 함께 commute하는 문제다. Consispace류
resampling, implicit continuous segmentation, resolution-invariant latent,
random finite-set detection, LesionDETR류 set prediction과 aneurysm shape/topology
loss는 모두 direct prior다. P0가 execution-incomplete로 닫혀 P1에 도달하지
못했으므로 contribution이 아니다. 닫힌 RSNA, 4D-flow와 BC-operator 가설은
아래 history로만 보존한다.

기존 세 축은 아래처럼 재판정한다.

1. **Nested condition–marginal coherence**: full/partial/missing BC를 별도
   head나 임의 imputation으로 처리하지 않는다. 하나의 BC density를 임의
   observation mask에 analytic conditioning하고 solution operator로
   pushforward하여 tower property를 구조적으로 만족시킨다. N1c에서
   구조적 일관성은 회복했지만 predictive/decision superiority가 없으므로
   아직 contribution이 아니다.
2. **Paired simulator-response supervision · demoted**: 동일 geometry의 두 BC에서
   절대 field뿐 아니라 `H(G,Bj)-H(G,Bi)`를 직접 감독하여 geometry
   confounding 없이 condition response를 학습한다. 인과 효과가 아니라
   simulator intervention response로만 부른다. N1c에서 DeltaPhi-style
   residual보다 열세였으므로 독립 contribution에서 내리고 ablation으로만
   유지한다.
3. **Structural/model uncertainty separation · untested secondary**: BC completion sample 간
   변동과 model ensemble 간 변동을 law of total variance에 맞춰 분리하고,
   ID mask별 calibration·supplied-BC response shift·geometry OOD에서 각각
   검증한다. Hidden-BC 생성법칙 자체가 shift된 경우에는 정답 coverage를
   식별 가능하다고 가정하지 않고 OOD detection/abstention만 평가한다.
   Positive N1 전에는 headline contribution이 아니다.

GNN, attention, probabilistic operator, flow matching, physics loss,
one-shot Fourier는 선행 구성요소 또는 engineering choice다. contribution
문구에 단독 novelty로 올리지 않는다. Fixed Fourier decoder는 D0에서
실패했으며, 다른 temporal decoder도 새 representation gate와
compute-matched 이득이 있을 때만 남긴다.

AAAI-26 LANO, NeurIPS-25 PaPQS·DeltaPhi, arbitrary-conditioning generative
model, 2026 conditioning-consistency와 NeurIPS-25 neural-operator
Thompson-sampling 연구를 고려하면 partial observation,
joint density의 analytic conditioning, tower-property 검사, paired
residual, active acquisition을 각각 단독 novelty로 주장할 수 없다. 현재
C1–C3는 **검증할 연구 가설**이지 확정 contribution이 아니다. 독립적
novelty는 이들을 PDE solution functional에 맞게 결합했을 때 생기는 새
문제 정의·보장·알고리즘과 strong baseline 대비 양수 결과가 함께 있을
때만 확정한다.

검증했던 paper identity 가설은
**conditioning inconsistency의 solution-functional decision consequence**다.
경로가 다른 posterior가 같은 최종 관측 mask에서 달라질 때 bounded
functional loss의 Bayes action과 다음 BC component의 value-of-information가
얼마나 흔들리는지를 regret으로 정의한다. Posterior TV/KL에서
Bayes-regret를 제한하는 보장, joint BC–solution model의 route
compatibility와 fresh prospective test의 실제 regret 감소가 함께 있어야
한다. N1c에서는 baseline route action 차이는 보였지만 signed true-risk
차이가 작고 seed별 부호가 섞였으므로 이 identity도 현재 unsupported다.
N1c-a의 corrected true-oracle regret에서도 AURORA가 independent heads보다
좋은 seed는 3/5에 그쳤고, baseline route candidate-risk 변화는 selected
component를 거의 바꾸지 않았다. 따라서 이 identity는 현 nonlinear
benchmark에서 폐기하며, direct route를 정답처럼 두거나 signed route
차이를 평균해 상쇄하지 않는다.

보존된 이전 prospective 개발 가설은 **coherence–conditional-accuracy trade-off를
candidate-measurement–solution joint risk에 맞춰 해소할 수 있는가**다. 완료된 audit은
full-joint likelihood가 random-mask conditional objective의 excess NLL을
20.3–27.2% 줄여 이 trade-off가 현재 모델에서 불가피하지 않음을 보였다.
그러나 full-joint MLE와 registered-mask composite likelihood는 engineering
control일 뿐 novelty가 아니다. Compatibility/path consistency, arbitrary
conditioning과 decision-focused learning도 선행 연구이므로, 독립 novelty는
missing-mask decision endpoint에서 solution marginal이 아니라 각
\((B_j,\Psi(H))\) joint pushforward를 직접 맞추는 operator-pullback
algorithm·보장과 fresh strong-baseline 우위가 있을 때만 인정한다.
Sparse-2 adaptive acquisition은 고정 winner task이므로 headline에서
제외한다. `M0`는 2/3 seed execution-incomplete로 닫혔고 이 mechanism의
method, repair 또는 fresh re-entry를 열지 않는다.

Test-time active
feature acquisition 자체, path independence 자체, 이름만 붙인 acquisition
head는 novelty가 아니다. ACFlow류 generative AFA, ICML-24 acquisition
conditioned oracle와 NOTS-style posterior-sample functional acquisition을
필수 baseline으로 둔다. NOTS는 whole input-function query 문제이므로
N1 adaptation을 원 논문 재현으로 표현하지 않는다.

## 3. 데이터셋의 역할

| 데이터 | 허용된 주 역할 | 금지된 해석 |
|---|---|---|
| RSNA-ICA 2025 | 새 task audit를 별도로 통과할 경우의 challenge benchmark 후보 | vessel anatomy mask를 aneurysm mask로 해석하거나 기각한 selection-aware task 복원 |
| CADA/ADAM | 사용자 접근 뒤 fully supervised 3DRA/MRA external control | annotation-selection cohort로 해석 |
| IntrA/TopCoW | license/task-unit 확인 뒤 surface/anatomy pretraining control | study-level lesion-set evidence 또는 primary 대체 |
| Aneumo | 동일/유사 geometry의 다중 steady BC로 BC sensitivity pretraining | patient-specific clinical evidence |
| AneuG-Flow | 대규모 synthetic steady 및 selected pulsatile pretraining | real cohort generalization |
| BenchAnXplore | 105 semi-idealized transient field의 재현·baseline | geometry-only clinical deployment |
| CMHA | patient CTA/mesh, clinical, morphology, real-CFD bridge와 task gate | multi-center external validation로 과장 |
| AneuX v1.0 | closed preprocessing-orbit P0 history; future independent source audit의 direct prior | real hemodynamics validation, prospective rupture risk, variant를 독립 환자로 계산 |
| Aneurisk | provenance가 확인된 geometry/morphology 보조 평가 | asset audit 전 CFD 보유 가정 |
| 4D-flow multiresolution phantom 2021 | same-flow 3×3 protocol development/task audit 후보 | high-resolution acquisition 또는 CFD를 clinical truth로 해석 |
| 4D-flow dual-VENC phantoms 2025 | four-phantom external protocol-pair audit 후보 | phantom을 independent clinical cohort 또는 repeat calibration set으로 과장 |
| 4D-flow intervention phantoms 2025 | multi-VENC, pump-off noise와 untreated/device response task-unit audit | 33 scans/device/phase/voxel을 independent patient로 계산 |

모든 case/field에는 `source_field ∈ {real_cfd, surrogate, synthetic_cfd}`와
dataset version, checksum, unit, coordinate frame을 기록한다.

## 4. 연구를 계속할지 결정하는 gate

- **I0a · Paired-protocol asset integrity · passed 14/14 asset-only**: 두 official Zenodo record의
  license·size·checksum, ZIP entry, 2021 3×3 descriptor/27 RAW byte contract,
  2025 four-model/eight-protocol primary/AP/FH/RL·phase/resolution/VENC header를
  14개 all-check rule로 감사한다. Processed RAW/REC payload는 읽지 않는다.
  Exact source `f7b4e024d69d43cf042f4163342b4d993386f441`에서 14/14를
  통과했고 public aggregate SHA-256은
  `2243172a720b25ebebd6052b9c0989880d95cba5b8d984f8980f70cf5f26d9c6`다.
  Pass는 selective private staging과 method-free I0b의 별도 등록만 허용한다.
  Task adequacy, posterior identifiability, method, novelty, performance와
  submission evidence가 아니다. 별도 I0b contract 전 field payload를 읽지
  않으며 local repair는 없다.

- **I0b · Method-free field/task-unit adequacy · execution-incomplete/closed**: 2021 official
  README/Matlab reader와 Zenodo `17183575` record·세 central directory·33
  primary PAR header를 registration 전 discovery로 공개했다. Formal run은
  2021 processed RAW 27개만
  little-endian float32/X-fastest 순서로 decode해 common grid에서 support
  alignment, temporal/vector similarity, resolution/acceleration discrepancy와
  protocol variance를 one-shot all-check rule로 검사한다. Expanded release는
  33 scans가 아니라 5 base geometry/2 source anatomy를 headline unit으로
  유지하며 두 2025 release의 overlap은 unresolved이다. Pass도 method-free
  I0c PAR/REC decoder·noise audit 등록만 허용하도록 설계했다. 실제 exact
  `0ebdb344…` run은 `h5py` import에서 asset access 전에 끝나 cache/result가
  없고 gate도 미평가다. Public execution record SHA는 `1b75bb95…`다.
  Dependency 보충, mask/registration/threshold repair, I0b rerun, I0c와 task
  relabel은 금지한다. 다음은 새 problem-level candidate audit이다.

- **G0 · Asset integrity**: case mapping, unit, boundary marker, license,
  geometry/condition split이 검증되지 않으면 학습하지 않는다.
- **G1 · Exact-coherence sanity**: 정답 conditional distribution을 계산할
  수 있는 controlled PDE에서 oracle moment·coverage·nested-mask coherence를
  회복하지 못하면 복잡한 aneurysm 실험으로 확장하지 않는다. 현재 frozen
  run은 실패했으므로 원인 분해 전까지 gate는 닫혀 있다. `G1b`는
  \(K=128/512/2048\)의 iid Monte Carlo floor와 sampling/BC-density/operator
  오차를 분해하는 post-result diagnostic일 뿐이며 G1을 재개방하거나
  소급해 relabel할 수 없다. G1b가 coverage attribution을 수행하지 않았으므로
  frozen worst-seed coverage failure도 unresolved로 남긴다. `G1r`은
  `configs/controlled_pde_g1r.json`의 다섯 fresh seed와 threshold를
  test access 전에 고정한 새 evidence다. Density/operator checkpoint는
  disjoint validation geometry로만 고르고 test split은 선택이 끝난 뒤
  생성한다.
  2026-08-03 G1r은 exact public commit `951ace1`의 PBS A6000 run에서
  정상 완료됐지만 gate는 실패했다. 최악 seed density-only mean
  0.07533, end-to-end quadrature mean 0.07518로 두 항이 0.05를 넘었다.
  Coverage 0.01809 이하, full-BC operator 0.00375 이하, analytic nesting
  \(7.45\times10^{-9}\), projective-excess CI upper 0.000202는 통과했다.
  다음 단계는 representation·optimization·finite-data error를 분리하는
  post-result density diagnostic이며, 새 fresh gate를 즉시 반복하지 않는다.
  이 진단은 `configs/controlled_pde_density_attribution.json`에 threshold
  없이 고정한다. True-parameter, population-NLL, empirical-NLL supervision과
  192×32/768×8/3,072×2 matched-budget scaling을 비교하며, G1/G1r seed를
  재사용하거나 어느 실패도 relabel하지 않는다.
  Exact commit `cf675af`의 DA1은 A6000에서 30개 task를 정상 완료했다.
  Analytic population NLL은 최악 density-only mean error 0.00495를
  회복했지만 empirical NLL은 population-selected 0.04401,
  sampled-selected 0.04855였다. 동일 6,144 record에서는 768×8이 기술적으로
  가장 안정적이었고, fixed-axis 결과는 geometry 수와 반복 condition이 모두
  필요함을 보였다. 이는 capacity보다 finite empirical information과
  allocation이 주 병목이라는 attribution이며 새 gate 통과가 아니다.
  후속 `DA2`는 G1/G1r/DA1과 겹치지 않는 세 development seed에서 기존
  empirical NLL, geometry-grouped unbiased moment, covariance shrinkage
  0.25/0.50을 같은 density network와 sampled-validation checkpoint로
  비교한다. Estimator는 원래 G1r budget인 768×8에서만 선택하고,
  3,072×8은 data-sufficiency control로 둔다. Success threshold는 없다.
  Pairwise-difference U-statistic은 unbiased sample covariance와 같은
  통계량이므로 novelty가 아니다. DA2가 한 estimator를 선택해도 별도
  fresh exact gate 전에는 nonlinear/3D confirmatory 학습을 허용하지 않는다.
  Exact commit `18dbfcd`의 DA2는 24 task를 exit 0으로 완료했다. 고정
  규칙은 shrinkage 0.50을 골랐지만 768×8 empirical NLL 대비 평균 개선은
  0.05444→0.05431(0.23%)뿐이고 1/3 seed에서는 악화됐으며 population
  excess NLL도 더 나빴다. 이를 method로 승격하지 않는다. 3,072×8의 기존
  empirical NLL은 평균 0.02575, 최악 0.02706으로 안정화돼 다음 fresh
  exact sanity는 estimator novelty가 아니라 data adequacy를 검사한다.
  이 fresh sanity는 `G1s`로 분리해
  `configs/controlled_pde_g1s.json`에 결과 전에 고정한다. 이전
  G1/G1r/DA1/DA2와 겹치지 않는 5개 seed, empirical NLL, 3,072 geometry
  × 8 condition, 기존 G1r model·optimizer·mask·threshold와
  validation-only selection을 유지한다. Validation/test size도 192/192로
  유지해 training geometry 수 외의 차이를 만들지 않는다. G1s가 통과해도
  data/pipeline adequacy이지 novelty가 아니며, 실패한 G1/G1r은 그대로다.
  Exact commit `b0e555a`의 G1s는 A6000 fresh 5-seed run에서 7개 check를
  모두 통과했다. 최악 density-only/end-to-end mean은
  0.02863/0.02977, density/sampled coverage error는
  0.00836/0.01294, projective CI upper는 0.000674였다. G1/G1r은
  failed로 유지한다. 이 pass는 nonlinear/3D protocol 등록을 허용하지만
  data scaling이나 exact toy result를 contribution으로 만들지 않는다.
- **G2 · Paired response fidelity**: ID partial/missing calibration과
  supplied full-BC support-shift response를 분리한다. Strong probabilistic
  baseline보다 field distribution과 paired response가 모두 개선되어야
  하며, hidden-law shift에서는 detection/abstention만 주장한다. Aneumo
  train-only physical-scaling audit에서 velocity tuned residual은
  0.2112, CI95 `[0.2001, 0.2243]`로 0.15 기준을 통과했지만 pressure는
  0.1369 `[0.1190, 0.1496]`로 실패했다. 따라서 향후 G2는 velocity-only
  후보이며 pressure/full-field novelty는 주장하지 않는다. G1s pass로
  velocity-only learned protocol 등록은 가능하지만, nonlinear domain과
  strong baseline을 먼저 통과하지 않은 3D 결과를 headline으로 올리지 않는다.
  `N0`는 33/65 nested grid의
  \(-\nabla\cdot(a_G\nabla u)+\lambda_Gu^3=f_G\), 8-component edge basis,
  context-conditioned 2-GMM BC law를 학습 전에 감사한다. Solver residual,
  discretization, nonlinear departure, 모든 BC component response,
  response effective rank, functional winner diversity, analytic
  direct/sequential conditioning을 모두 통과해야 N1을 등록한다. N0는
  numerical/problem adequacy일 뿐 method claim이 아니다. Frozen N0는
  nonlinear departure 한 항목에서 실패했다. Context-major contiguous
  slicing을 발견했지만 threshold를 낮추거나 N0를 relabel하지 않는다.
  N0a는 attribution만, N0r는 fresh seed와 context-stratified selector를
  결과 전에 고정한 re-entry만 허용한다. N0a는 기존 세 seed의 24×12
  전체 case를 검사하지만 success threshold, N0 relabel, N1/3D 권한,
  N0r seed·threshold 선택을 모두 금지한다. N0a 결과는 failed seed의
  contiguous/stratified/all-case median 0.00774/0.01221/0.01828로 slice
  민감도를 지지했지만, former reference 이상인 context는 18–19/24라
  uniformly nonlinear하다고 쓰지 않는다.
  N0r exact contract는 N0a outcome 전 commit `1a68053`에서 동결했다.
  Fresh seeds `[62080321, 62080322, 62080323]`, reference 24(각 context
  1회), paired 48(각 context 2회)을 사용한다. PDE·BC law·solver·functionals,
  threshold와 worst-seed rule은 N0와 같다. Exact commit `37d31a8`의
  A6000 run은 9/9 check를 통과했다. Worst-seed nonlinear departure
  0.01933, grid error 0.00375, worst-component response 0.17484,
  route residual \(8.94\times10^{-8}\)였다. 이는 N1 상세 protocol 등록만
  허용하며, N0 failed history·method novelty·3D headline을 바꾸지 않는다.
  N1 core attempt 1은 exact `6075530` validation-only run에서 density NLL
  -4.290, operator full-BC/paired-response L2 0.1739/0.1862였다. Test는
  생성·접근하지 않았고 operator가 0.05 자격에 못 미쳐 confirmatory path는
  닫혀 있다. Unit-peak envelope rescaling은 동일 함수 클래스의 optimization
  diagnostic이며 threshold·rank·data·loss를 바꾸지 않는다.
  Unit-peak attempt 2는 exact `54046a3`에서 full-BC/paired-response L2
  0.05771/0.05729로 개선됐지만 unchanged 0.05를 넘고 best step이
  maximum 1,400이어서 insufficient다. N1a는 새 development seed에서
  raw/scale-normalized loss × 1,400/2,800 step만 비교하는 threshold-free
  validation attribution이다. Exact `eebcd91`의 PBS run은 exit 0이었고
  test context를 생성하지 않았다. 선택된 scale-normalized 2,800-step
  variant의 full-BC/paired-response validation L2는
  0.01162/0.01220이었다. N1 pass가 아니라 기존 miss가 optimization
  conditioning 때문이었다는 attribution이다. `N1b`는 이 값만 고정한 새
  prospective version이며 모든 mandatory model의 validation checkpoint와
  checksum을 public manifest로 commit하기 전 test/N1/3D 권한이 없다.
  Direct generic/NOP control의 centered POD-96은 operator-training field
  전용이고 seed 73080601, subspace iteration 4회로 고정한다. 단, 각
  confirmatory model seed는 direct baseline의 weight initialization과
  minibatch sampling을 모두 제어해야 한다.
  N1c exact source `62605a0`은 50개 checkpoint hash를 확인한 뒤에만
  192×12 outer test를 생성했고 PBS job은 exit 0이었다. 공개 aggregate는
  `results/nonlinear_pde_n1c_20260805.json`이다. Gate는 full-BC operator,
  coverage, route action만 통과하고 pair, field distribution,
  acquisition regret가 실패해 closed다. Invalid route-VoI 보조 지표를
  고치는 post-result diagnostic은 N1c를 재개방하거나 3D를 허용하지
  않는다. Exact `b97899c`의 N1c-a는 joint/independent conditional NLL,
  true-law density와 oracle operator floor, acquisition sample-size
  stability, true-oracle worst-route excess risk를 threshold 없이
  분해했다. 공개 aggregate는
  `results/nonlinear_pde_n1c_attribution_20260806.json`이다. Joint density는
  모든 mask에서 independent heads보다 0/5 seed로 열세였고, stable-budget
  acquisition과 corrected route regret도 robust superiority를 회복하지
  못했다. 결과 전에 고정한 validation-only objective control과
  method-independent task-adequacy audit은 각각
  `configs/nonlinear_pde_n1_density_objective_audit.json`과
  `configs/nonlinear_pde_n1_decision_task_audit.json`에서 완료됐다.
  Full-joint objective는 세 mask 모두 N1c raw보다 5/5 seed에서 나았지만
  method novelty가 아니다. Missing task는 stable nonzero VoI를 보였고,
  sparse-2는 component 6이 96/96 context의 고정 winner여서 adaptive
  acquisition 비교에서 제외한다. N1c failed와 N1d/3D blocked는 유지하며
  별도 operator-specific fresh prospective re-entry는 아직 등록하지
  않는다. 대신 missing-only candidate-measurement–solution joint
  pullback의 3-seed M0 development gate만 결과 전에 등록했다. Exact
  `89bdc85` 실행은 2/3 seed만 완료되어 aggregate와 과학적 판정이 없고,
  성공 seed metric은 검사하지 않았다. M0는 N1 test를 생성하거나 읽지
  않았으며 local sampler repair·rerun·fresh re-entry 없이 닫혔다.
- **G3 · Transient efficiency**: one-shot 표현이 oracle D0를 통과하고,
  learned compute-matched 비교에서 autoregressive baseline보다 cycle
  fidelity/latency trade-off가 좋아야 한다. Fixed Fourier \(K=8\)은
  실패했으므로 현재 닫혀 있다. D0b는 Fourier 8/12의 실수 계수 수와 같은
  17/25 budget에서 DCT-II와 train-geometry-only POD를 geometry-disjoint로
  비교했다. POD 두 rank만 representation-eligible이다. 다만 105 case
  전체가 architecture discovery에 쓰였으므로 같은 BenchAnXplore의 learned
  비교는 exploratory다. Confirmatory G3는 D0b에 쓰지 않은 fresh transient
  case 또는 독립 pulsatile dataset을 요구한다.
- **G4 · Cross-domain generality**: controlled PDE, nonlinear PDE, irregular
  3D aneurysm 중 적어도 세 domain에서 같은 method가 유효해야 한다.

CMHA real-CFD incremental utility는 독립된 secondary diagnostic이다.
2026-08-03 exploratory signal이 음수이므로 risk-retention과 clinical
utility는 현재 gate나 contribution이 아니다.

정확한 threshold는 `configs/aurora_v1.json`에 버전 관리한다. 결과를 본 뒤
threshold를 바꾸면 반드시 exploratory로 표시한다.

## 5. 필수 평가 원칙

- split은 patient/geometry 단위다. 같은 geometry의 timestep, BC, cut,
  augmentation이 train과 test에 갈라지면 leakage다.
- model selection은 nested CV 안쪽에서만 한다. test fold로 architecture,
  threshold, seed를 선택하지 않는다.
- AUROC만 보고하지 않는다. AUPRC, balanced accuracy, Brier, ECE, calibration
  slope/intercept와 patient-bootstrap 95% CI를 포함한다.
- field는 velocity/pressure RMSE 외에 paired-response error, mass-flux,
  divergence, boundary violation, distributional coverage/width와
  nested-mask coherence error를 평가한다.
- direct geometry model, clinical+morphology model, deterministic operator,
  independent mask heads, mean/zero imputation, generic probabilistic
  operator, deep ensemble, In-PI-MGN/graph-transformer 계열을 공정한
  baseline으로 둔다.
- 여러 aneurysm이 한 환자에 있으면 bootstrap과 split의 sampling unit은
  환자다.
- 모든 headline result는 최소 5 seeds 또는 반복 nested split으로 확인한다.
- 통계 검정은 effect size와 CI가 우선이다. cross-validation prediction에
  단순 DeLong을 반복 적용하지 않는다.

## 6. 구현 동기화 규칙

연구 방향, architecture, dataset role, gate가 바뀌는 커밋은 아래를 함께
갱신한다.

1. `docs/research-direction.md`
2. `docs/model-spec.md`
3. `docs/experiment-protocol.md`
4. `configs/aurora_v1.json`
5. `CHANGELOG.md`

공개 사이트는 더 이상 연구 운영 동기화 대상이 아니다. 코드·설정·실험 문서와
`CHANGELOG.md`에 날짜, category, decision, rationale, affected files를
기록한다. README와 연구 문서가 서로 다른 연구 질문을 말하면 배포하지 않는다.

### 반복 검증과 재실행 정책

- 기존 job의 marker·log·status·metric·result는 덮어쓰거나 삭제·은폐·재명명하지
  않는다. 반복 실행은 새 run ID와 결과 디렉터리를 사용하고 predecessor,
  exact commit/config, seed, 환경, 반복 사유와 변경점을 기록한다.
- 인프라·scheduler·전송·dependency·환경 실패, 중단된 job, stochastic
  replication, 재현성 확인과 bug-fix 검증은 같은 과학 설정으로 재실행할 수
  있다. 별도의 새 가설이나 이름만 바꾼 evidence version은 필요하지 않다.
- train/validation 범위에서는 모델·loss·optimizer를 반복 개발할 수 있다. 모든
  유의미한 trial을 보존하고 development로 표시하며, 선택된 결과를 독립적인
  confirmation처럼 서술하지 않는다.
- confirmatory/outer split, endpoint와 decision rule은 접근 전에 동결한다.
  관측한 outer 결과로 tuning하지 않는다. 실행 무효를 입증한 결함을 수정할
  때는 원인과 fix를 남기고 비교 가능성이 영향받으면 관련 method 전체를 같은
  pipeline으로 다시 평가한다. 그 외 유효한 반복 결과는 모두 유지·보고한다.
- 횟수 자체를 임의로 1회로 제한하지 않는다. 각 재시도는 검증 가능한 이유와
  계산·저장 예산을 가져야 한다. 동일 실패를 정보 증가 없이 반복하지 않고,
  진단 후 최소 변경을 적용하거나 unresolved blocker로 보고한다.
- `execution-incomplete / no scientific verdict`는 해당 실행의 상태이지 연구
  요소의 영구 폐기 판정이 아니다. 실패했던 dataset, architecture, loss,
  split과 evaluator도 타당하면 이후 실행에서 재사용할 수 있다.

### ISBI 2027 제출 규약

- 자세한 단일 출처는 `docs/isbi-2027-plan.md`다.
- 모든 기술 내용·표·그림은 official template 첫 4쪽 안에 둔다. 5쪽은
  reference, ethics, acknowledgments/COI 외 기술 내용을 금지한다.
- 한 사람의 제1저자 제출은 최대 2편이다. 이미 출판·채택되었거나 ISBI 심사
  기간 중 다른 conference/workshop에 동시 제출된 substantially similar 원고는
  금지하고, preprint는 허용한다.
- `Compliance with Ethical Standards`는 별도 윤리 승인이 필요하지 않은
  simulation/open-data 연구에도 필수다. Funding과 실제 COI 또는 그 부재도
  acknowledgments에서 저자가 확인해 공개한다. Submission link는 현재
  `Coming Soon`이며 임의 endpoint를 기록하지 않는다.
- 현재 primary, headline domain과 source shortlist는 모두 미선정이다. AneuX
  preprocessing-orbit P0/P1은 닫혔으며 이 candidate를 primary로 부르지 않는다.
  다음 fresh candidate가 데이터 의미, 식별 가능한 estimand, direct-prior gap과
  feasible patient/source-level evaluation을 모두 통과해야 한다. Open-CTA
  P0/P1도 닫혔다.
  과거 synthetic-CFD 3D velocity 규약은 실패한
  Aneumo branch의 history다.
  Pressure, WSS/OSI, transient efficiency, rupture prediction과 clinical
  utility는 새 provenance와 prospective evidence 없이는 headline에서 제외한다.
- 64-case Aneumo cache는 implementation/development pilot이다. Expanded
  base-family-disjoint cache 또는 독립 3D cohort 없이 confirmatory
  headline이라 하지 않는다.
- M0는 한 번의 nonlinear mechanism falsification일 뿐 ISBI method나 3D
  evidence가 아니다. 통과해도 scalar-inflow 3D estimand에 맞춘 별도
  prospective translation contract가 필요하다.
- ISBI full-paper gate가 실패하면 제목·threshold·metric을 사후 변경해
  제출하지 않는다.
- V1은 12개 model×seed validation task만 허용한다. Selector는 seed-mean
  response L2, full-q L2, exact eight-component missing energy, parameter
  count 순이고 후보 이름은 선택 우선권이 없다. V1 실패 뒤 hidden size,
  k, seed, step과 threshold를 국소 수정하지 않는다.

## 7. 새 팀 대화와 게시글 반영

`tmp/`는 private raw context이며 Git에 올리지 않는다.

새 내용이 들어오면:

1. 파일 수정 시각과 새 구간만 확인한다.
2. 주장, 실험 결과, 결정, 질문을 분리한다.
3. 논문 수치와 데이터 설명은 1차 출처 또는 raw asset으로 재검증한다.
4. 기존 기준선과 충돌하면 자동 채택하지 않고 decision log에 대안과 근거를
   남긴다.
5. 채택된 내용만 문서·config·site·changelog에 반영한다.

대화에 포함된 비밀번호, 회의 링크, 이메일, 서버 경로, 개인 식별정보는
문서·사이트·commit에 옮기지 않는다.

## 8. 사이트 품질 기준

- 첫 화면에서 연구 질문, pivot 이유, 현재 stage를 30초 안에 이해할 수
  있어야 한다.
- 같은 문장을 여러 페이지에 반복하지 않는다. 상세 문서는 GitHub 링크로
  연결한다.
- architecture diagram은 입력, latent uncertainty, decoder, output,
  downstream 평가의 인과 흐름을 보여야 한다.
- “완료”, “검증”, “SOTA”는 증거가 있을 때만 사용한다. 계획은 planned,
  구현은 implemented, 데이터 확인은 audited로 구분한다.
- 모바일, keyboard navigation, reduced motion, 색 대비를 점검한다.
- 외부 링크는 가능한 DOI, 공식 proceedings, dataset record 등 1차 출처를
  사용한다.

## 9. Git과 보안

- 공개 저장소: `https://github.com/gohyunsu/aneurysm`
- 비공개 논문 저장소: `https://github.com/gohyunsu/aneurysm-paper`
- 기본 branch: `main`
- 공개 저장소는 protocol, code, 공개 문서, site를 관리한다. 비공개 저장소는
  manuscript, claim matrix, 미공개 aggregate result와 reviewer 대응만
  관리한다.
- 비공개 원고의 `AGENTS.md`에 public source commit SHA를 pin한다. 연구
  방향이 바뀌면 public protocol/site/changelog를 먼저 갱신하고 private
  manuscript pin을 뒤따라 갱신한다.
- raw medical data, archive, checkpoint, private team log, credential은
  commit하지 않는다.
- 사용자 변경사항과 무관한 파일은 되돌리지 않는다.
- commit 전에 `git diff --check`, protocol validator, unit test, local site
  link/HTML smoke를 수행한다.
- GitHub Pages 또는 production deploy 뒤 공개 URL과 commit SHA를
  `CHANGELOG.md`에 기록한다.

## 10. 논문 언어

- `rupture status classification`: 현재 허용
- `rupture risk prediction`: prospective/time-to-event cohort가 있을 때만
  허용
- `real CFD`: solver provenance와 BC가 확인된 field/summary
- `surrogate hemodynamics`: model-generated; real CFD와 병합 금지
- `patient-specific`: patient geometry만 해당하면 그렇게 한정하고,
  generic BC까지 patient-specific이라고 부르지 않는다.
- `clinical utility`: 외부·전향 검증 전 사용 금지. 대신 `research utility`,
  `downstream association`, `functional sufficiency`를 쓴다.

## 11. 서버와 실행 기준선

- private 운영 가이드는 Git에서 제외된 `SERVER_GUIDE.md`다. endpoint,
  password, private key, 내부 데이터 절대경로를 공개 문서에 옮기지 않는다.
- `introai9`는 뇌동맥류 source asset과 manifest를 읽기 전용으로 감사하고,
  CPU/PBS 및 향후 gate-authorized GPU 실험도 이 계정의 scheduler allocation에서만
  실행한다. 허용 queue ACL은 `coss_agpu`와 `coss_a6gpu`에서 확인했지만 현재
  AURORA GPU job은 0개다. 새 후보가 gate를 통과한 뒤 첫 allocation에서
  GPU/runtime smoke와 실제 사양을 다시 기록한다.
- `junjinyong`은 다른 연구가 사용 중이므로 AURORA에서는 접속, job 제출,
  상태 조회와 모니터링을 모두 금지한다. 과거 실행 기록과 frozen config/PBS는
  provenance로만 보존하고 재제출하지 않는다. 어느 서버에서도 login node GPU를
  사용하지 않으며, source asset을 서버 사이에 임의 복제하지 않는다.
- 이전 실행 계정에서 완료된 compact-cache 재생성은 byte-range/CRC와
  등록 SHA가 일치함을 확인하는 asset audit일 뿐 GPU 결과가 아니다. 어느
  서버에서도 login node에서 GPU 학습이나 `nvidia-smi`를 실행하지 않는다.
- pinned Singularity image를 사용하고 code/data는 read-only, output만
  writable로 bind한다.
- run은 commit, command, environment, config, dataset checksum, status,
  aggregate metrics를 남긴다. 실패 run도 provenance로 보존한다.
- 2026-08-03 smoke 기준은 RTX A6000, PyTorch 2.5.1+cu118, CUDA 11.8이다.
  사양은 매 job에서 다시 기록한다.
- 2026-08-08 `introai9` PBS GPU smoke는 A100-SXM4-80GB,
  PyTorch 2.5.1+cu118, CUDA 11.8에서 exit 0이었다. 서버에서 공식 release로
  독립 재생성한 64-case compact cache도 등록 SHA와 일치했다. Exact
  `2ddd5e6`의 첫 12-task array와 diagnostic은 metric 전에 실패했고,
  exact `fd8bb40`의 task-local log가 device 객체를 인자로 받은 CUDA
  peak-memory reset의 runtime incompatibility를 cache load 전에 확인했다.
  Scientific 설정은 바꾸지 않고 current-device bookkeeping API만 고치며,
  새 exact contract와 one-task diagnostic 전에는 fresh array를 제출하지
  않는다. 모든 실패 artifact를 보존한다.
- Exact `a0479fb`의 fresh V1 array는 12/12 exit 0, checkpoint·metric
  12쌍, exact source/config와 no-test-read 전수 검사를 통과했다. 첫 aggregate
  PBS job은 result 이전 exit 1이었고 stage-out 성공 표기와 달리 stdout이
  나타나지 않았다. Aggregate wrapper에 task-local log/status fail-safe만
  추가하고 같은 12개 artifact를 read-only replay한다. Model, config,
  selector, threshold와 task source를 바꾸지 않으며 실패 aggregate를 보존한다.
- Observable aggregate replay는 cache의 registered flow가 `float32`라
  `0.0025`가 `0.002499999944...`로 저장된 반면 response-only oracle만
  `1e-12`로 cache 값을 직접 비교해 result 전에 실패했음을 확인했다. Cache
  ordering을 기존 loader tolerance로 검증하고 anchor/ratio는 config의 design
  value로 계산한다. 이는 selector/gate에 들어가지 않는 control 구현 수정이며
  config, task metric/checkpoint와 threshold는 유지한다. Aggregate source와
  task source SHA는 artifact에서 분리해 기록하고 두 실패 aggregate를 보존한다.
- Exact `c62838b`의 V1e six-task A6000 array는 scheduler control-plane
  timeout과 dispatch 지연 중에도 기존 array를 중복 제출하지 않고 6/6 exit 0으로
  완료했다. Pinned CPU aggregate는 exact config, two-cache checksum, CUDA task,
  PBS index, eligible validation checkpoint와 forbidden-access false를 전수
  검사했다. Gate는 6/9 fail이며 public aggregate SHA-256은
  `63fdb3a6fbddb15bb8d6cb82fde7b6880e3b3c7badef46b7a4cc2da4d31f2c0e`다.
  Boundary relative utility가 양수여도 absolute train/validation/response가
  모두 실패했으므로 current Aneumo 3D line을 중단한다. Raw task metric,
  checkpoints, histories와 scheduler logs는 private output에만 보존한다.
- Exact `89bdc85`의 M0 A6000 array `115078`은 dependency-complete
  150/150 contract와 frozen N1b checkpoint hash를 확인한 뒤 실행했다.
  Seed 0/2는 exit 0, seed 1은 truncated conditional rejection stall로 exit
  1이었다. 세 seed 완결을 요구하는 aggregate는 생성하지 않았고 성공 seed
  metric도 gate 용도로 읽지 않았다. 따라서 M0에는 과학적 pass/fail이 없으며
  sampler repair, rerun, re-entry와 N1d/3D 제출 권한도 없다.
- Cross-protocol I0a는 exact source `f7b4e024…`를 먼저 push한 뒤 `introai9`의
  pinned container에서 수행한 CPU metadata audit이다. Official API와
  byte-range만 사용했고 14/14를 통과했으며 processed RAW/REC field read는
  0이었다. 별도 I0b contract 전에는 field payload를 읽지 않고 method code나
  GPU training을 실행하지 않는다.
- I0b exact `0ebdb344…`는 `introai9` scheduler CPU allocation에서 실행됐으나
  wrapper가 기존 read-only `h5py==3.12.1` layer를 누락해 asset access 전에
  exit 1이었다. Source는
  read-only였고 private cache/result는 생성되지 않았다. 2021 RAW/field, 2025
  PAR/REC, checkpoint와 GPU read는 0이다. Gate는 미평가이고 no-rerun rule에
  따라 dependency 보충, I0c와 어떤 GPU training도 열리지 않는다.
- 2026-08-03 Aneumo 공식 ZIP64 release를 HTTP byte-range로 감사해 첫
  shard의 geometry 1--40마다 8개 steady mass-flow condition이 있음을
  확인했다. Geometry 1의 두 internal NPY는 CRC와
  `(N,7)=xyz+pressure+velocity` contract를 실제 검증했다. 이후 32개
  AneuX base family × 2 deformation, 8 condition, 4,096 node의 selective
  pilot staging을 완료했다. 64 case와 512 member가 모두 검증됐고
  family-disjoint split은 20/6/6 family와 40/12/12 case다. Compact-cache
  SHA-256은
  `9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`다.
  Raw/compact field는 CC BY-NC-ND 조건에 따라 공개 저장소에 재배포하지
  않는다. Learned G2 전에 train-family field만 읽는 same-case-anchor
  physical-scaling audit을 실행하며 validation/test field read는 금지한다.
  두 채널 모두 비자명성 기준을 실패하면 Aneumo response 학습을 중단한다.
  Exact public commit `e12ff0a`의 audit은 exit 0으로 완료됐고 velocity만
  eligible했다. Public aggregate는
  `results/aneumo_scaling_audit_20260803.json`이다.
- BenchAnXplore coarse archive는 105 geometry × 80 timestep,
  velocity/wall-mask HDF5와 XDMF 210개로 확인했다. archive checksum과
  외부 `h5py==3.12.1` dependency layer를 run provenance에 고정한다.
- CMHA 통계표는 105 lesion/99 patient, 6 multi-lesion patient로 감사됐다.
  split/bootstrap은 patient group 단위다. 공식 case map 확인 전 row-aligned
  G1은 exploratory다.
- CMHA `PHASE`, `ELAPSS`는 정의가 확인되지 않았고 target과 거의 결정적
  관계를 보여 baseline에서 제외한다.
- 2026-08-03 당시 `G1`이라 부른 exploratory clinical diagnostic은 `C+M`
  AUPRC 0.759, `C+M+H` 0.717, `Δ=-0.0419 [−0.1083, 0.0066]`이었다.
  v2의 G1은 exact-coherence gate이므로 둘을 혼동하지 않는다. 공식 case
  map과 second model family 전에는 risk-retention을 계산하거나 status
  alignment를 primary claim으로 복원하지 않는다.
- Exact G1b는 공개 commit `8e24950`의 PBS A6000 run에서 exit 0,
  walltime 45초로 완료됐다. Public aggregate는
  `results/controlled_pde_g1b_20260803.json`이며 raw metrics checksum은
  그 artifact 안에만 기록한다. 결과를 근거로 frozen G1 threshold를
  완화하지 않는다.
- G1r은 frozen G1/G1b artifact checksum을 pin한 별도 prospective
  protocol이다. `preregistered_before_fresh_test` 상태와 seed·threshold를
  실행 전에 public commit으로 고정하며, 결과를 본 뒤 변경하면 새 버전과
  exploratory 표기가 필요하다. Exact public commit `951ace1`의 run은
  exit 0, elapsed 46.74초였으나 gate는 실패했다. Public aggregate는
  `results/controlled_pde_g1r_20260803.json`이다.
- D0b 구현은 DCT-II/POD orthonormality, held-out covariance exclusion,
  synthetic two-pass runtime을 pinned container에서 통과했다. Exact public
  commit `1dfc856`의 105-case run은 exit 0, walltime 3분 49초였다.
  POD-17 full L2 0.00141, bulge L2 0.00880, peak error 0.000764였고
  POD-25도 통과했다. DCT-25는 bulge L2 0.03084로 탈락했다. Public
  aggregate는 `results/benchanxplore_d0b_20260803.json`이다.
