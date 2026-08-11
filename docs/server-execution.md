# AURORA 서버 실행과 provenance

> **Schema 8.0 deployment verification · 2026-08-11:** Exact outcome content
> `6123f0e917f084aad0bf352306ba9cf70f57e835` passed GitHub-hosted Quality
> `31448501704` and Pages `31448501265`. Live content matched the closed P0
> state. These checks did not query a scientific server and authorize no PBS or
> GPU work.

> **Schema 8.0 final P0 execution · 2026-08-11:** Exact source `4a0fa65b…`
> ran once on `introai9` PBS as job `115684.ECE-util1`, CPU 4, 16 GB, GPU 0.
> Final state was `E`, exit 2, walltime 00:40:06, CPU 00:00:01 and memory
> 56,812 kB. A bounded 323-byte status and 971-byte result report
> execution-incomplete/no scientific verdict and 0/10 evaluated checks. No raw
> PBS log or persistent archive/VTP exists; partial bytes and low-level cause
> are unknown. Do not repair, rerun or open P1/GPU. Final user queue was empty.
> No login-node GPU command ran and `junjinyong` was never accessed.

> **Schema 7.9 prospective execution boundary · 2026-08-11:** Exactly one new
> CPU-only P0 may be submitted from an exact clean public commit to `introai9`
> PBS (`coss_agpu`, CPU 4, 16 GB, GPU 0, two hours). It reads the registered
> Aneurisk archive only in job-local scratch. No server query or job has yet
> occurred for this version. Never run a login-node GPU command and never
> connect to, query, transfer to, submit to or monitor `junjinyong`.

> **Schema 7.8 deployment verification · 2026-08-11:** Exact scientific
> content `720e4c5e441c96bd2b35e31cb2a1a19da0ff6dee` passed Quality
> `31416106615` and Pages `31416105439`. Live pages expose the same 31.0/40
> source rejection and no-compute boundary. These GitHub-hosted checks queried
> neither `introai9` nor `junjinyong` and authorize no PBS/GPU work.

> **Schema 7.8 no-execution boundary · 2026-08-11:** The structure-faithful
> WSS reappraisal peaks at 31.0/40 and registers no P0/PBS/GPU work. No
> scientific server was connected to or queried during the source-only audit.
> Historical `115645.ECE-util1` remains closed at 0/10 checks and cannot be
> repaired or rerun. Future eligible work remains `introai9` PBS only; never
> access, query, submit to or monitor `junjinyong`, and never run GPU commands
> on an `introai9` login node.

> **Schema 7.7 deployment verification · 2026-08-11:** Exact content
> `611848cba1f19675ab850ebc0c9e2bcd8672c0ef` passed Quality
> `31413485546`, Pages `31413484543` and manual source-watch
> `31413562860`. All watched public states matched. These GitHub-hosted checks
> queried neither `introai9` nor `junjinyong` and authorized no PBS/GPU work.

> **Schema 7.7 public-metadata watch · 2026-08-11:** The v3 live refresh read
> only official public GitHub/Zenodo/Grand Challenge metadata and matched all
> frozen snapshots. It did not query `introai9`, access `junjinyong`, submit PBS
> or execute GPU commands. Scheduled/manual GitHub Actions remain read-only and
> cannot authorize scientific execution.

> **Schema 7.6 deployment verification · 2026-08-11:** Exact content
> `aec4b76a1646a4e3508640a1a0ecb7ac146979cc` passed Quality
> `31411063368` and Pages `31411180740`; live pages expose TRELLIS direct-prior,
> stated-code-404 and active lead/P0/P1/method/architecture/GPU 0. No SSH,
> scheduler query, transfer, PBS/GPU job or login-node GPU command occurred.
> Future eligible execution remains `introai9` PBS only and `junjinyong`
> remains prohibited.

> **Schema 7.2 final execution · 2026-08-10:** Exact source `8a06de2…` ran
> once on `introai9` PBS as CPU-only job `115645.ECE-util1`. Final evidence is
> state `E`, exit 2, walltime 00:27:02, CPU 00:00:06, memory 625,780 kB, CPU 4,
> 16 GB and GPU 0. Only bounded private status/result records materialized; no
> aggregate, raw PBS log or persistent probe cache exists. The scientific gate
> is unevaluated and the low-level cause unresolved. Do not repair, resubmit,
> open P1 or use GPU. No login-node GPU command ran. `junjinyong` was not
> accessed and remains prohibited for all AURORA operations.

> **Schema 7.1 registered boundary · 2026-08-10:** Credential-managed SSH to
> `introai9` was verified and `qstat -u introai9` returned an empty queue after
> the site profile was loaded. No login-node GPU command ran. One exact
> AneuG-Flow surface-vector P0 is preregistered but not submitted: PBS queue
> `coss_agpu`, CPU 4, memory 16 GB, GPU 0, walltime one hour, pinned CPU
> container, three raw wall/OBJ probe pairs and a one-submission guard. Submit
> only an exact clean public commit. Failure or incomplete execution closes the
> candidate without repair/rerun. `junjinyong` belongs to another project and is
> forbidden for connection, query, transfer, submission and monitoring.

> **Schema 7.0 current boundary · 2026-08-10:** A credential-managed,
> read-only `qstat -u introai9` observation returned an empty queue for AURORA.
> No GPU command was executed on the login node. The new AneuG target-
> construction source audit peaks at 31.5/40 below admission, so it creates no
> PBS script, CPU P0, GPU allocation or monitoring loop. A future job may run
> only through `introai9` PBS after a fresh candidate passes its source and
> method-free gates. `junjinyong` belongs to another project and is forbidden
> for SSH, status queries, code/data transfer, submission and monitoring.

> **Schema 6.9 final execution · 2026-08-10:** Exact source `bb227edc…` ran
> once on `introai9` CPU/PBS as `115622.ECE-util1`; final state `F`, exit 1,
> walltime 00:02:24, CPU 00:00:00, memory 15,328 kB and GPU 0. Only the
> deidentified private status materialized; aggregate result and raw PBS output
> did not. No job is running or queued for AURORA, no login-node GPU command was
> executed, and no second submission is permitted. The exact candidate closes
> with no P1/model/GPU/outer test. `junjinyong` was not accessed and remains
> prohibited for every AURORA operation.

> **Schema 6.8 registered execution boundary · 2026-08-10:** The only next
> AURORA job is one exact OpenNeuro metadata P0 on `introai9` PBS: queue
> `coss_agpu`, CPU 2, memory 4 GB, GPU 0, walltime 20 minutes. It reads only five
> pinned small/public metadata objects and may make three in-job transient HTTP
> attempts per object at 0/10/30 seconds. That retry budget is not permission for
> a second PBS submission. No patient payload, model, checkpoint or outer test
> is accessed; no login-node GPU command is run. `junjinyong` is another
> project's server and must not be connected, queried, used for transfer or
> submission, or monitored for AURORA.

> **Schema 6.6 deployment verification · 2026-08-10:** Exact outcome content
> `bb16d90d2e06bd1f12972efaf67093d425048d49` passed Quality
> `31375709669` and Pages `31375709322`. Live overview, Learn and execution JSON
> expose P0 closed/no verdict, no P1/model/GPU and `junjinyong_accessed=false`.
> This is deployment provenance only; it does not reopen the job, P0 or any
> scientific/compute authorization.

> **Schema 6.6 final execution · 2026-08-10:** Exact source `38e7894…` ran once
> on `introai9` CPU/PBS as `115518.ECE-util1`; final observed state was E/exit 1,
> walltime 00:08:21, CPU 00:00:00, memory 39,160 kB. Only a 275-byte private
> status artifact exists; aggregate result and raw PBS output do not. After exit
> the job disappeared and `qstat -u introai9` was empty. Do not reconnect for
> repair, resubmit, open P1 or use GPU. The scientific gate is unevaluated and
> the low-level cause unresolved. `junjinyong` was not accessed and remains
> prohibited.

> **Schema 6.5 pending execution · 2026-08-10:** One exact method-free Aneumo
> BC-transport P0 is preregistered but not yet submitted. Its allocation is
> `introai9` PBS, queue `coss_agpu`, CPU 2, memory 8 GB, GPU 0, walltime 45 min.
> The last bounded pre-registration observation verified the credential-managed
> public-key boundary and an empty `qstat -u introai9`; no login-node GPU command
> was run. Submit only an exact clean public commit, once. Failure or incomplete
> execution closes this version without repair/rerun. `junjinyong` is forbidden
> for connection, query, code/data transfer, submission and monitoring.

> **2026-08-10 schema 6.4 execution boundary:** The TopAneu code-semantics
> audit is source-only and rejects all candidates, maximum 31.5/40. It created
> no medical payload access, P0, PBS job, GPU allocation or monitoring loop.
> No TopAneu experiment is pending on `introai9`; current AURORA GPU jobs remain
> zero. A future experiment requires a different candidate to pass its frozen
> gates and must run through `introai9` PBS. `junjinyong` is never connected,
> queried, used for transfer/submission or monitored.

> **2026-08-10 TopAneu deployment verification:** Exact content
> `e4038ca6d052def5f275c4118bd904c4ab543135` passed Quality `31367056976` and
> Pages `31367056610`; live overview, Learn and detailed audit expose the same
> 33/40 terms-pending/no-payload/no-compute boundary. This is GitHub deployment
> provenance, not an `introai9` experiment, and creates no PBS/GPU job.

> **2026-08-10 TopAneu source-lead boundary:** This was a public source and
> direct-prior audit, not a server experiment. TopAneu terms are not accepted,
> so no payload, PBS job, GPU allocation or monitoring loop was created. If the
> user explicitly accepts the terms, a separately preregistered CPU/read-only
> P0-R may run on `introai9` PBS only. `junjinyong` is prohibited for connection,
> query, transfer, submission and monitoring.

> **Current execution outcome · 2026-08-10:** Exact `introai9` CPU/PBS job
> `115467.ECE-util1` was observed in E with exit 1, walltime 8 s, CPU time 0 and
> 16824 kB memory. Only a 319-byte execution-incomplete status materialized;
> result and raw PBS output did not. The job later stopped returning from
> `qstat`. Do not repeat the connection, submission or repair loop. No v2b/P1/
> model/GPU is authorized. `junjinyong` was not used and remains prohibited.
> Exact public outcome `9632ee5a5e507318fd18bff217c934c30a0b1a02`
> passed Quality `31364095951` and Pages `31364095339`.

> **Current execution boundary · 2026-08-10:** `junjinyong` is prohibited for
> connection, query, transfer, submission and monitoring. The only pending
> action is one preregistered `introai9` CPU/PBS P0-v2a (2 CPU, 4 GB, GPU 0,
> 15 min; two HEAD + four 1 MiB reads; retry 0). No job has yet been submitted.
> The last bounded connection attempt reset before its remote command, so no
> current PBS queue state is claimed. Do not enter a connection or local repair
> loop. The job may run only from an exact clean public commit and may write
> only aggregate status/result plus ephemeral range bytes.

## 2026-08-10 · 4D-CTA source content and live site verified

- Exact content `f95b73a68ddc20b993ebd5dd0d28e4645a3dafc9` passed Quality
  `31359594992` and Pages `31359594475`.
- Live overview, Learn guide, detailed audit and research-data object expose
  the same 31.5/40, 20-patient, derived-target and no-compute boundary.
- This is deployment provenance only. It creates no archive access, P0, PBS/GPU
  job, monitoring loop, outer test or submission identity. `introai9` remains
  the only future execution target; `junjinyong` remains excluded.

## 2026-08-10 · 4D-CTA AAA source rejection; no compute opened

- Six frozen scores are 31.5/30.5/30.0/29.0/28.5/25.5. No candidate reaches
  32, so the 1.86 GB archive, P0, PBS submission, model, GPU, outer test and
  monitoring loop remain zero.
- One bounded `introai9` read-only status attempt reached the configured
  endpoint but was reset before a remote command. It yielded no current
  scheduler observation and was not followed by a connection-repair loop.
- `junjinyong` was not connected to, queried, used for transfer/submission or
  monitored. All future gate-authorized execution remains `introai9` PBS only.

## 2026-08-10 · Source-watch v2; no compute opened

- Official IAVS and TopBrain 2.0 snapshots match their frozen records. The
  TopBrain design object is `CC BY 4.0`, while no medical payload or executable
  task route appeared. The watcher returned `continue_watch_only`.
- Automatic download, P0, model, GPU and outer test remain false. No PBS job or
  monitoring loop was created. Future authorized execution remains
  `introai9`-only; `junjinyong` is completely excluded.
- Exact content `545df1b570ea9df6d3feac545bbc0f02cab18178` passed Quality
  `31357501911` and Pages `31357501328`; live overview, Learn, change data and
  detailed audit expose the same correction and no-compute boundary.

## 2026-08-10 · TopBrain 2.0 deployment verification

- Exact content `8b2a70c9a6bab21962d22b66601481d323e4a52e` passed Quality
  `31354245210` and Pages `31354244348`.
- Live overview, guide and detailed audit return HTTP 200 with the same
  29.0/40, all-rejected and no-compute boundary.
- This is provenance only. It creates no medical payload, P0, PBS/GPU job or
  monitoring loop. `introai9` remains the only possible future execution
  target, and `junjinyong` remains completely excluded.

## 2026-08-10 · TopBrain 2.0 source audit, no job authorized

- Six source-only candidates score 29.0/28.5/28.0/27.5/27.0/23.5, all below
  32. The official object is a design PDF; no medical payload or P0 was opened.
- Therefore no PBS job, GPU allocation or monitoring loop was created. The
  last bounded `introai9` AURORA queue observation remains empty; no login-node
  GPU command ran.
- `junjinyong` was not connected to, queried, used for transfer/submission or
  monitored and remains completely excluded from AURORA.

## 2026-08-10 · RSNA registry deployment verification

- Exact content `5690b104e6d3fc2644b3d934e12b834ea2c3c3da` passed Quality
  `31352980950` and Pages `31352980597`; live overview, guide and detailed
  audit return HTTP 200 with the same 31.5/40 and no-compute boundary.
- This is provenance only. It creates no terms acceptance, data access, PBS/GPU
  job or monitoring loop. `introai9` remains idle for AURORA and
  `junjinyong` remains completely excluded.

## 2026-08-10 · RSNA AWS registry correction, no job authorized

- Exact public registry YAML blob `97b8c1f…` at file commit `523ffd3…` was read;
  controlled MIRA terms were not accepted and no account, request, S3 listing
  or data payload was accessed.
- The frozen candidate score is 31.5/40, below 32. Therefore no P0, PBS job,
  model, GPU allocation, outer test or monitoring loop was created.
- Credential-managed `introai9` access succeeded and login-profile
  `qstat -u introai9` returned an empty list. No login-node GPU command ran.
  `junjinyong` was not accessed and remains fully excluded.

최종 갱신: 2026-08-10 KST

## 2026-08-10 · Broad-registry deployment verification

- Exact content `162903a6b66a9982c011fd96d8faf99e92de7eda` passed Quality
  `31351395527`.
- Pages `31351394932` succeeded but exposed the preceding public SHA in run API
  metadata, so it is not treated as an exact-content pin. Direct live checks of
  overview, Learn and the detailed audit returned HTTP 200 with 30.5/40 and the
  no-payload/P0/model/GPU boundary.
- This is provenance only. It creates no server job or monitoring loop and does
  not authorize `junjinyong`.

## 2026-08-10 · Broad-registry source-only stop; introai9 remains exclusive

- Six frozen scores are 30.5/29.5/26.0/26.0/24.5/18.0, all below 32. No access
  request, payload, executable P0, PBS submission, GPU job or monitoring loop was
  created. This is a scientific source-gate stop, not a server failure.
- A minimal public-key login reached `introai9`/`ECE-util2`; the last completed
  PBS check showed zero AURORA jobs. Two bounded name-level scans produced no
  artifact, so candidate-asset presence is not established and absence is not
  claimed. No login-node GPU command ran and no repeated local repair was opened.
- Any future job requires a new >=32 candidate and a separately frozen
  method-free P0, and must use PBS on `introai9`. `junjinyong` is completely
  excluded from connection, scheduler query, AURORA transfer, submission and
  monitoring.

## 2026-08-10 · Registry-gap deployment verification

- Public content `b4c3d48a107b969ce26cbc86abd9b36814116a3a` passed Quality
  `31349424733` and Pages `31349424311`; the live overview, Learn guide and
  detailed audit return HTTP 200.
- Private paper head `2403b746e8bbc663f87e08cc8493f5ed31cc85ab` pins that public
  content. The repository is private and unauthenticated API access returns 404.
- This is provenance verification only. It creates no PBS/GPU job and does not
  change the scientific early-stop boundary or authorize `junjinyong`.

## 2026-08-10 · Registry-gap source-only stop; introai9 remains exclusive

- Five metadata-only candidates score 26.5/26.0/26.0/25.5/23.5, all below 32.
  No payload, executable P0, PBS submission, GPU job or monitoring loop was
  created. This is a scientific source-gate stop, not a server failure.
- A future job is authorized only after a genuinely new candidate reaches 32
  and a separate method-free P0 is frozen. Such work must use PBS on `introai9`;
  login-node GPU commands remain forbidden.
- `junjinyong` is assigned to other work and is completely outside AURORA. Do
  not connect, query scheduler state, submit, transfer AURORA code/data or
  monitor it.

## 2026-08-10 · Method--asset source-only stop and introai9 status

- Five scores are 30/30/29/26/23, all below 32. No payload, P0, PBS/GPU job or
  outer test was created.
- Public-key access reached remote user `introai9` on `ECE-util2` and
  `qstat -u introai9` returned no jobs. No login-node GPU command ran.
- Exact public refs are unchanged for Royal, AneuG-Flow and IAVS; this is no
  source-version re-entry. `junjinyong` was not connected to, queried, submitted
  to or monitored.

## 2026-08-10 · Reconstruction/annotation source-only stop

- Frozen scores are 31.5/29.5/29.0/26.5/25.5/25.5, all below 32. No P0, PBS,
  GPU job or scheduler query was needed.
- Future execution remains PBS-only on `introai9`, beginning with a method-free
  CPU/read-only P0 only after a fresh source passes 32. `junjinyong` is excluded
  from connection, query, submission and monitoring.
- Patient image/mask/mesh/projection/CFD/phantom payload remains zero. The
  article supplement is literature evidence, not patient data.
- Closed Aneumo/Open-CTA and prior model branches are not repaired or rerun.

## 2026-08-10 · Failure-mechanism/biology source-only stop

- All six scores are below 32; the maximum is 30.5/40. No P0 or PBS/GPU job was
  created and no scheduler query was required.
- This is a normal source-gate stop, not an `introai9` connection or execution
  failure. The last Aneumo P0 remains closed without repair or rerun.
- Any future authorized execution remains PBS-only on `introai9`.
  `junjinyong` remains forbidden for connection, query, submission and
  monitoring.

## 2026-08-10 · Aneumo lineage metadata P0 outcome

- AURORA execution remains `introai9` PBS only. `junjinyong` is forbidden for
  connection, query, submission and monitoring.
- The single exact job `115386.ECE-util1` requested 2 CPU, 4 GB and GPU 0. PBS
  finalized it at exit `-29`, walltime 20:36 and CPU time 0 before its first
  small source completed.
- Completed/partial cache, result JSON and raw scheduler log are absent. No
  login-node GPU command, archive/LFS object, model or outer test was accessed.
  Scientific checks are unevaluated and same-source repair/resubmission is
  forbidden. Current AURORA PBS/GPU job count is 0.

이 문서는 재현에 필요한 역할과 절차만 공개한다. SSH endpoint, 내부 절대
경로, credential, patient-level row와 prediction은 기록하지 않는다. 실제
운영 명령과 private path는 Git에서 제외된 `SERVER_GUIDE.md`를 따른다.

## 2026-08-10 · longitudinal-MRA growth source audit, no job authorized

- Frozen scores are 31.5/29.0/30.0/26.5/26.5/26.0, all below 32.
- Only official articles, OpenNeuro Git tree/tag/commit metadata and the public
  dataset description were inspected. Annotation spreadsheet, participant
  table, acquisition sidecar, NIfTI, segmentation, Slicer scene and STL payload
  were not accessed.
- There is no executable P0, PBS submission, GPU job or monitoring loop. No
  `introai9` connection or scheduler query was necessary for this source-gate
  stop; it is not a server failure.
- AURORA remains `introai9` PBS only. `junjinyong` is excluded from connection,
  query, submission and monitoring.

## 2026-08-10 · longitudinal-perfusion source audit, no job authorized

- Frozen scores are 31.0/29.0/28.0/27.0/29.5/29.0, all below 32.
- Only official records, embedded README text, file manifests and public
  manuscripts were inspected. No standalone JSON, spreadsheet, NIfTI/ZIP, SAH
  CT archive, 3DRA/CTA CSV, VWE CSV, image, mesh or field payload was opened.
- There is no executable P0, PBS submission, GPU job or monitoring loop. This
  is a source-gate stop, not a server failure.
- AURORA remains `introai9` PBS only. `junjinyong` is excluded from connection,
  query, submission and monitoring.

## 2026-08-10 · FSI–wall source audit, no job authorized

- Frozen scores are 30.5/29.5/26.5/24.5/29.0/31.0, all below 32.
- Only public manuscripts, official repository metadata and bounded file-tree
  names were inspected. Mesh, rigid/FSI field, wall image/property and device-
  response payloads were not accessed.
- There is no executable P0, PBS submission, GPU job or monitoring loop from
  this audit. This is a registered source-gate stop, not a server failure.
- AURORA remains `introai9` PBS only. `junjinyong` is excluded from connection,
  query, submission and monitoring.

## 2026-08-10 · acquisition–flow source audit, no job authorized

- Frozen scores are 27.5/26.5/24.0/26.0/27.0, all below 32.
- Only official public pages, manuscripts and repository records were inspected.
  No Synapse application, challenge form, terms acceptance, k-space/MAT,
  aneurysm ZIP or patient payload occurred.
- There is no executable P0, PBS submission, GPU job or monitoring loop from
  this audit. This is a registered source-gate stop, not a server failure.
- AURORA remains `introai9` PBS only. `junjinyong` is excluded from connection,
  query, submission and monitoring.

## 2026-08-10 · treatment–surveillance source audit, no job authorized

- Frozen scores are 30.0/26.0/29.0/26.0/23.0, all below 32.
- Only public record pages and manuscripts were inspected. Mendeley spreadsheet,
  R document, presentation/DSA images and restricted Zenodo MRA files were not
  accessed.
- There is no executable P0, PBS submission, GPU job or monitoring loop from
  this audit. A transient `introai9` SSH handshake reset is an access-state
  observation, not a scheduler or scientific result; it does not authorize a
  different server.
- AURORA remains `introai9` PBS only. `junjinyong` is excluded from connection,
  query, submission and monitoring.

## 2026-08-10 execution boundary check

- Credential-managed local SSH config의 `introai9` alias로 public-key 접속을
  다시 확인했다. Endpoint와 key 경로는 공개하지 않는다.
- 원격 사용자는 `introai9`였고 PBS AURORA job은 0개였다.
- Known source root의 후보 이름 검색이 login node에서 길어져 60초 뒤
  중단했다. 이 bounded metadata search를 반복하거나 deep recursive scan으로
  확대하지 않는다.
- Login-node `nvidia-smi`, GPU training과 PBS GPU 제출은 실행하지 않았다.
- `junjinyong`은 접속·조회·제출·모니터링하지 않았다.
- IAVS 상태 확인은 공식 GitHub metadata를 읽는 source watch이며 scientific
  experiment가 아니다. P0/P1 gate 전에는 `introai9` GPU job을 만들지 않는다.

## 2026-08-10 · provenance–evaluation source audit, no job authorized

- Frozen scores are 30.0/29.5/28.5/23.5/25.5, all below 32.
- Public manuscripts, README, Zenodo record and Git tree paths만 읽었다. AneuX/
  CFD archive, DICOM, STL, VTP, spreadsheet와 model weight는 읽지 않았다.
- `introai9` PBS job은 0개이며 P0/PBS/GPU job을 만들지 않았다. 이는 정상
  source-gate early stop이지 SSH·scheduler·GPU failure가 아니다.
- `junjinyong`은 접속·조회·제출·모니터링하지 않았다.

## 2026-08-10 · context–treatment source audit, no job authorized

- Frozen scores are 31.5/27.5/26.0/27.0/30.0, all below 32.
- AneuSI repository metadata와 small case-name file만 읽었다. Spreadsheet/VTK,
  treatment MRI archive와 latent source meshes는 읽거나 내려받지 않았다.
- `introai9` PBS job은 0개이며 P0/PBS/GPU job을 만들지 않았다. 이는 정상
  source-gate early stop이지 SSH·scheduler·GPU failure가 아니다.
- `junjinyong`은 접속·조회·제출·모니터링하지 않았다.

## 2026-08-10 · topology–procedure source audit, no job authorized

- Fresh source-only scores are 24.0/28.5/24.0/28.5/28.5, all below 32.
- Only public record pages, manuscripts, a 2,063-byte Figshare README and the
  rheology/slip repository README/tree were read. WSS/velocity/code archives,
  MAXIMUS weights, 3DRA and patient-image payloads were not accessed.
- No P0, PBS or GPU job was created on `introai9`; this is a normal source-gate
  early stop, not an SSH, scheduler or GPU failure.
- `junjinyong` was not connected to, queried, submitted to or monitored.

## 서버 역할

| 서버 계정 | 역할 | 허용 작업 |
|---|---|---|
| `introai9` | AURORA의 유일한 source·compute 대상 | 원본·매니페스트 read-only 감사, CPU/PBS, gate가 허용한 GPU smoke·학습·평가 |
| `junjinyong` | AURORA 실행 제외 | 다른 연구가 사용 중이므로 접속·제출·상태 조회·모니터링 금지; 과거 provenance만 보존 |

원자료를 로컬 저장소에 내려받거나 서버 사이에 전체 복제하지 않는다. 실행
서버에서는 필요한 source root를 read-only로 bind하고 run output만 writable로
둔다. 어느 서버에서도 login node GPU를 사용하지 않는다. `introai9`의 asset을
서버 사이에 임의 복제하지 않는다. `coss_agpu`와 `coss_a6gpu` queue ACL은
확인했지만 현재 AURORA GPU job은 0개다. 새 후보가 prospective gate로 GPU를
허용한 뒤 첫 `introai9` allocation에서 container·cache SHA와 GPU/runtime smoke를
확인하기 전 learned job을 제출하지 않는다.

이 정책은 2026-08-09 이후 새 실행에 적용한다. 아래의 `junjinyong` 언급과
`ssu_a6gpu_*` 파일명은 이미 끝난 run의 재현 이력이며, 새 제출 대상으로
해석하거나 복사하지 않는다.

## 2026-08-10 · hemodynamic–endpoint source audit, no job authorized

- New 76-case Aneurisk CFD record and four endpoint families were source-only
  audited. Frozen scores are 31.0/30.0/23.0/25.0/26.0, all below 32.
- The 1.4 GB archive and VTP payload were not accessed. No P0 config, PBS job,
  method, architecture, checkpoint, GPU allocation or outer test was created.
- This is a scientific early stop, not a connection failure. Only a genuinely
  new candidate at or above 32 may register an `introai9` CPU/PBS P0.
- `junjinyong` was not connected, queried, submitted to or monitored.

## 2026-08-10 · vascular-semantics source audit, no job authorized

- 최신 six-candidate frozen score는 29.5/28.5/27.5/26.5/26.0/25.0으로 모두
  admission line 32 미만이다.
- Source metadata 외 candidate payload를 읽지 않았고 executable P0, method,
  architecture, checkpoint, GPU와 outer test를 만들지 않았다.
- 이 no-job 판정이 현재 compute outcome이다. 다음 후보가 32점 이상일 때만
  `introai9` CPU/PBS method-free P0를 별도 등록한다.
- `junjinyong`에는 접속·조회·제출·모니터링하지 않는다.

## 2026-08-09 · source-delta audit, introai9 verified and idle

- Private 운영 가이드가 지정한 실제 login boundary에서 `introai9` 공개키 접속을
  확인했다. 로컬 WSL에 편의 alias가 없었던 것은 서버 또는 과학적 실패가 아니다.
- PBS 조회에서 AURORA job은 0개였다. Login node GPU 명령은 실행하지 않았다.
- 알려진 source root를 bounded read-only로 감사했다. IntrA는 README, split과
  preview만 있는 repository skeleton이며 mesh payload는 확인되지 않았다.
- 당시 여섯 후보의 최고 score가 31.5/40으로 gate 32 미만이어서 PBS P0와 GPU job을
  제출하지 않았다. 이 early stop이 현재 실행 결과다.
- 이 감사에서 `junjinyong`에는 접속·조회·제출·모니터링하지 않았다.

## 2026-08-09 · DIAS prefix-risk source rejection, no job submitted

- Official paper, repository와 Zenodo API metadata만 감사했다. DIAS archive,
  image frame, label과 patient identifier는 읽지 않았다.
- `introai9`에 read-only로 연결해 AURORA PBS job이 0개임을 확인하고 알려진
  dataset root를 bounded inventory했다. DIAS staging은 확인되지 않았지만 이를
  서버 전체의 asset 부재로 과장하지 않는다.
- Source score가 31/40으로 admission 기준 32에 못 미쳐 CPU/PBS P0와 GPU job을
  제출하지 않았다. Gate 미달 상태에서 resource를 점유하지 않은 것이 현재
  registered action이다.
- `junjinyong`에는 이 audit을 위해 접속, status query, submit 또는 monitor하지
  않았다.

## 2026-08-09 · AneuX preprocessing-orbit P0 execution-incomplete

- Exact public commit `42cc3c7127f382b440f2ac22f662c45692f37863`을 먼저
  고정한 뒤 `introai9`의 `coss_agpu` PBS job `115177.ECE-util1`에서 4 CPU/
  16 GB/GPU 0으로 한 번 실행했다. Login node GPU 명령은 실행하지 않았다.
- 계약은 official 13 MB tabular ZIP을 private run cache에 받고 exact size/MD5 뒤
  필요한 CSV만 읽도록 했다. 6.28 GB model ZIP은 HEAD, tail과 central-directory
  exact HTTP range만 허용하고 full archive와 member payload는 금지했다.
- 각 HTTP operation의 transient timeout/reset/408/429/5xx에만 0/10/30초 최대
  세 attempt를 허용했다. Semantic/parser/contract failure는 retry하지 않고,
  같은 public source commit의 PBS resubmission도 wrapper가 거부한다.
- Private output은 job status와 deidentified aggregate만 남겼다. Public 결과는
  case identifier, member listing, row-level clinical/morphometric value와 internal
  path를 포함하지 않는다.
- Scheduler는 exit 2, walltime `00:37:00`, CPU time `00:00:00`, peak memory
  `26596kb`를 기록했다. Result error는 `transport_attempts_exhausted`이며 첫
  tabular archive가 완성되기 전 종료됐다. Complete/partial cache, CSV parse,
  model HEAD/range/central-directory/member access는 0이고 13개 gate는 미평가다.
- Raw scheduler log는 materialize되지 않아 low-level exception은 단정하지 않는다.
  같은 contract의 transport/reader repair와 resubmission, P1, GPU allocation,
  model training, outer test와 status performance는 금지된다. 공개 execution
  record는 `results/aneux_preprocessing_orbit_p0_execution_20260809.json`이다.

## 2026-08-09 · Open-CTA physical-coordinate P0 execution-incomplete

- Exact public source `b437875f884346d7f0fada68f089981664ae2a3c`의
  registered P0는 local CPU/network에서 한 번 실행했다. GPU/PBS experiment가
  아니다.
- P0는 로컬 CPU의 official Zenodo HTTP byte-range audit이다. 516 DICOM member의
  compressed prefix를 PixelData tag 전까지만 읽고 122 STL을 in-memory로
  CRC/physical-frame 감사한다. Full archive staging, PixelData decode, raw
  retention, identifier publication과 GPU는 금지한다.
- 실제 실행은 22.53초 뒤 DICOM `(0008,1032) Procedure Code Sequence`의
  undefined-length element가 frozen minimal parser 범위 밖이어서 exit 1이었다.
  Threaded early exit로 완료 header 수는 미집계다. PixelData를 decode·inspect하지
  않았고 STL 단계에는 도달하지 않았다. Scientific gate와 P0 result는 없다.
- 결과를 본 뒤 parser, tolerance, threshold나 selection을 고쳐 같은 P0를
  반복하지 않는다. 후보는 execution-incomplete/no scientific verdict로 닫고
  P1과 어떤 PBS GPU job도 제출하지 않는다.
- `introai9`로 계산 대상을 통합했지만, 닫힌 공개 Zenodo P0를 그 서버에서
  대신 실행하거나 같은 계약으로 반복하지 않는다.

## 2026-08-09 · Fresh TopAneu/open-CTA source audit

- `junjinyong`은 `/etc/profile` 뒤 PBS와 Singularity를 확인했고 public-key
  연결도 정상이다. Active problem이 없으므로 GPU allocation, training과
  `nvidia-smi`는 실행하지 않았다.
- `introai9`는 Windows SSH config의 공식 alias로 read-only 연결했다. 알려진
  top-level source root와 `AAAI/datasets`, `AAAI/data`의 bounded depth에서
  TopAneu/open-CTA 이름의 staged asset을 찾지 못했다. 이는 서버 전체 부재
  증거가 아니며 recursive unbounded search는 약 1분 뒤 중단했다.
- TopAneu는 verified account와 terms가 필요해 사용자를 대신해 download하거나
  staging하지 않았다. Image/mask/JSON payload access는 0이다.
- Open CTA는 Zenodo endpoint에서 전체 archive 없이 ZIP64 central directory와
  metadata CSV 한 member만 range-read했다. DICOM header/pixel, STL과 full
  archive는 읽지 않았다. 이 local network discovery는 PBS/GPU experiment가
  아니며 external-stress feasibility만 기록한다.

## 2026-08-09 · Goal-oriented S0a runtime discovery

- `junjinyong` login node에서 `/etc/profile` 뒤 PBS `qsub/qstat`, target queue와
  Singularity CE 3.11.3을 read-only로 확인했다. GPU API와 `nvidia-smi`는
  호출하지 않았다.
- 기존 pinned PyTorch 2.5.1/CUDA 11.8 image는 공유 영역에서 읽을 수 있지만
  SciPy, trimesh, PyVista, meshio, VTK, FEniCS와 JAX를 포함하지 않는다.
  Host에서도 OpenFOAM, SU2, VMTK, FEniCS와 Gmsh executable을 확인하지 못했다.
- 이는 S0a outcome이 아니라 registration-before-execution discovery다.
  `configs/goal_oriented_segmentation_s0a.json`은 별도 solver image의 exact
  SHA-256, license, mesh/steady-forward와 discrete-adjoint 또는 검증 가능한
  shape-gradient capability를 필수 check로 둔다.
- CMHA full archive에 대한 bounded shared-storage query는 SSH handshake reset으로
  끝났고 재시도 loop를 돌리지 않았다. 기존 공개 row audit만 보존하며 105
  lesion exact-ID linkage를 아직 통과로 표시하지 않는다.
- S0a는 CPU-only PBS, source/code read-only, output writable, aggregate-only다.

### CMHA private staging boundary

- 최초에는 로컬에 등록된 source-server 연결에서 당시 가정한 project root만
  읽기 전용 검색해 CMHA archive를 찾지 못했다. 이 제한된
  위치 추론은 이후 더 넓은 source-root discovery에서 세 official archive를
  찾고 size/MD5 3/3을 확인하면서 폐기됐다.
  `junjinyong` home에도 official archive와 table은 없었다.
- `junjinyong`에는 `curl`, `7z`, checksum 도구와 약 4.1 TB 여유가 있고,
  host SU2/OpenFOAM은 없다. 기존 held job 두 개는 변경하지 않았다.
- `cluster/pbs_goal_oriented_s0a_stage_cmha.pbs`는 official Figshare file ID,
  byte size와 MD5를 고정한 **staging-only** CPU job이다. Private output에만
  archive와 extracted payload를 쓰고, 중단된 download는 resume한다.
  Identifier linkage, unit/frame, solver capability와 S0a pass/fail은 평가하지
  않으며 status에도 `gate_evaluated=false`를 기록한다.
  Pass도 S0b 등록만 열고 segmentation training, GPU와 outer test를 금지한다.

**V1 execution:** exact source `b6b6175…`의 job `115107`은 1,237초 후 exit
28이었다. Manifest 0 byte, final/partial archive 0, extraction 0이며 raw
scheduler stdout도 생성되지 않아 exact cause는 unresolved다. S0a는
`not_evaluated`이고 같은 v1 source는 재제출하지 않는다.

**V2 prospective transport:** login-node bounded diagnostic의 1 KiB/8 MiB range
GET은 HTTP 206이었고 8 MiB는 4.999초였다. 이를 근거로만 monolithic GET을
64 MiB ranged chunks로 바꾼다. `cluster/pbs_goal_oriented_s0a_stage_cmha_v2.pbs`
는 chunk별 206/size, ordered assembly, 전체 MD5와 failure status를 강제하며
public source당 PBS attempt를 1회로 제한한다. Dataset contract, extraction,
identifier/unit/solver/model/GPU/outer-test boundary는 v1과 같다.

**V2 execution:** exact `5cd4aa2…`의 one-shot job은 first verified chunk 전에
exit 28이었다. Chunk/archive manifest 0 byte, mapping 0, S0a 미평가이며 raw
stdout은 PBS post-job processing 뒤 materialize되지 않았다. 같은 source와
새 v3 Figshare transport를 제출하지 않는다.

**Source-server asset overlay:** `introai9`의 기존 세 archive는 low-priority
read-only MD5 discovery에서 official size/hash 3/3이 일치했다. CSV, identifier,
NIfTI/STL header와 voxel/field는 열지 않았으므로 S0a pass가 아니다.
`configs/goal_oriented_segmentation_s0a_asset_component.json`과
`cluster/pbs_goal_oriented_s0a_asset_component.pbs`는 `coss_agpu` 4 CPU/16 GB,
GPU 0으로 exact-ID와 header/mesh만 one-shot 감사한다. Raw/extracted/code는
read-only env path로 받고 output만 writable하다.

**Asset execution:** exact public source
`ef547a4ccb71fa45b4a43e67c0939e2701ebfc11`의 job `115119.ECE-util1`은 exit
0, walltime 1,271초, CPU 64초, peak memory 15,265,936 KB로 완료됐다. PBS는
`Post job file processing error`를 남겨 scheduler stdout은 보존되지 않았지만,
private aggregate와 status artifact는 정상 보존됐다. Raw aggregate SHA-256은
`7490fa3165ec47f9ac27c26425146af043db7861a1ff1224fda2a6d7a379b9ae`, status
SHA-256은 `e41e131da1edbe48258e84074fad76b6acc14b6e01643e0dedda1872016483bb`다.

Scientific result는 5/9 fail이다. 105 patient records/99 unique patients와 105
morphology IDs/98 unique hemodynamic IDs/99 case directories가 관찰됐지만,
explicit lesion-level linkage가 없어 required CTA+2 STL triplet은 0/105였다.
NIfTI/STL header와 voxel/field는 열지 않았다. S0a는 `not_evaluated`이고 후보를
닫았다. Solver v2, S0b, model, GPU와 outer test는 제출하지 않는다. 공개
privacy-safe aggregate는
`results/goal_oriented_s0a_asset_component_20260809.json`이다.

### SU2 reverse-AD runtime preflight boundary

- Official SU2 8.5.0 OMP release의 SHA-256을 확인하고 local temporary
  QuickStart direct solve를 완료했지만, 같은 binary는 `DISCRETE_ADJOINT`에서
  AD support가 compile되지 않았다고 종료했다. 이 binary는 S0a 부적격이며
  결과는 registration-before-execution negative control이다.
- `configs/goal_oriented_segmentation_s0a_solver_preflight.json`과
  `cluster/pbs_goal_oriented_s0a_solver_preflight.pbs`는 exact SU2/TestCases tag
  commit, GNU LGPL COPYING hash, official GHCR linux/amd64 OCI manifest와
  normal+reverse-AD build flag를 고정한다.
- Preflight는 8 CPU/32 GB PBS allocation에서 immutable SIF를 만들고 official
  incompressible heated-cylinder의 fresh direct solve 뒤 20-step discrete
  adjoint와 finite/nonzero surface sensitivity를 확인한다. Private path와 raw
  field는 public aggregate에 쓰지 않는다.
- 이는 S0a gate가 아니다. Medical asset, model, GPU와 outer test access는
  모두 0이며, 성공해도 runtime SHA pin과 단일 S0a 실행만 허용한다. 실패
  source version은 현장에서 dependency/flag를 고쳐 재실행하지 않는다.
- Exact `64284eb…`의 v1 실행은 official build SIF와 exact source/submodule
  materialization 뒤 exit 1이었다. TestCases/build/runtime/probe/sensitivity는
  남지 않았고 raw stdout도 materialize되지 않았다. 같은 v1을 반복하지 않으며
  asset component가 5/9로 실패했으므로 no-runtime-network v2는 등록하지 않는다.

## 2026-08-08 · Cross-protocol 4D-flow I0a

- `configs/flow_mri_protocol_i0a_asset_audit.json`은 공식 Zenodo API와 HTTP
  byte range만 쓰는 CPU metadata audit이다. GPU job이 아니며 login node에서
  GPU API를 호출하지 않는다.
- 등록 전에 두 record, central directory, nine descriptor와 eight primary
  header를 본 범위를 result와 함께 보존한다. 이는 prospective performance
  evidence가 아니다.
- Processed RAW와 REC field payload는 읽지 않고, archive 전체도 내려받지
  않는다. Exact public commit과 config SHA, command, environment, 14-check
  result와 status만 private output에 남긴다.
- Pass 뒤에도 selective staging protocol을 별도 commit하기 전 field를 읽지
  않으며, learned method나 PBS GPU training을 제출하지 않는다.
- Exact public source `f7b4e024d69d43cf042f4163342b4d993386f441`의 pinned
  container run은 exit 0, 14/14 pass였다. ZIP entry 174/76개, descriptor/header
  9/8개를 CRC 검증했고 processed RAW/REC read는 0이었다. Public aggregate는
  `results/flow_mri_protocol_i0a_asset_audit_20260808.json`, SHA-256
  `2243172a720b25ebebd6052b9c0989880d95cba5b8d984f8980f70cf5f26d9c6`다.
  Task adequacy나 method evidence가 아니며 별도 I0b 등록만 연다.

## 2026-08-09 · Cross-protocol 4D-flow I0b registered

- Exact executable contract는
  `configs/flow_mri_protocol_i0b_task_adequacy.json`, SHA-256
  `e19a1194f1b9ec41861c5084b26c9add5be47924a19aee4d23ffc826399dce06`다.
- Registration 전 2021 official README/reader와 Zenodo `17183575` official
  record, 세 central directory, 33 primary PAR header를 확인한 범위를 공개했다.
  Velocity field와 REC는 읽지 않았다.
- Formal I0b는 `introai9`의 scheduler CPU allocation과 pinned container에서
  실행한다. 2021 processed RAW 27개만 HTTP byte-range/CRC로 읽고 private
  HDF5 common-grid cache를 만든다. Source는 read-only, output만 writable이다.
- 공개 wrapper `cluster/pbs_flow_mri_protocol_i0b_cpu.pbs`는 8 CPU/48 GB,
  exact source commit, source read-only, output writable와 기존 scientific
  output 거부를 강제한다. Queue·container·private absolute path는 제출 시
  환경으로만 주입하며 GPU resource와 `nvidia-smi`는 요청하지 않는다.
- 2025 intervention release의 132 REC member는 존재/byte contract만 확인하고
  payload는 읽지 않는다. Checkpoint, method와 GPU는 사용하지 않는다.
- Pass도 GPU job을 열지 않는다. 별도 method-free I0c decoder/noise
  protocol을 public exact commit으로 먼저 고정해야 한다. Failure 뒤 local
  registration·mask·threshold 수선이나 I0b rerun은 금지한다.
- **Outcome:** exact source `0ebdb344…`의 PBS job `115093`은 8 CPU/48 GB,
  GPU 없이 5분 7초 뒤 exit 1이었다. Registered wrapper가 과거에 쓰던
  read-only `h5py==3.12.1` layer를 bind하지 않아 `_scientific_imports()`에서
  중단됐다. Container SHA는 `2da7b186…`이고 raw
  log/status checksum은 public execution record에 고정했다. Archive request,
  RAW/field/PAR/REC read, cache/result 생성은 0이다. Gate는 미평가이며
  dependency를 보충한 rerun이나 I0c/GPU job을 제출하지 않는다.

## 2026-08-03 자산 감사

`introai9`에서 다음 자산의 존재를 직접 확인했다.

| 데이터 | 확인된 상태 | 다음 G0 작업 |
|---|---|---|
| Aneumo | 32 family/64 case selective cache, case당 steady BC 8개, checksum 검증 | train-only physical-scaling audit; learned G2 보류 |
| AneuG-Flow | geometry archive | CFD field release subset 확보 |
| BenchAnXplore | archive와 105-case × 80-step HDF5/XDMF | unit·boundary semantics; D0 audit |
| CMHA | archive, statistical table, patient 추출본 | 공식 case map, field/summary provenance |
| AneuX | metadata와 geometry archive/추출본 | patient/source split과 license |
| Aneurisk | source-native repository | AneuX overlap과 asset provenance |

파일의 존재는 G0 통과를 뜻하지 않는다. 현재 명시적 manifest는
BenchAnXplore 표본에만 확인됐으므로 dataset별 checksum·license·unit·case
mapping을 계속 보강한다.

## CMHA row audit

공개 통계표의 aneurysm 부분은 105개 병변, 99명 환자다. 6명에게 두 병변이
있고, 해당 6명은 병변별 rupture status가 다르다. 따라서 split과 bootstrap은
병변 행이 아니라 환자 그룹 단위여야 한다.

세 표의 row alignment는 다음과 같이 관찰됐다.

- clinical–hemodynamic identifier exact match: 104/105
- morphology identifier가 patient ID 또는 lesion suffix와 호환: 105/105
- 공식 release case map: 아직 미확인

현재 G1 run은 이 row alignment를 사용하는 **exploratory audit**이다.
confirmatory G1 전에 release data dictionary 또는 공식 case map으로
검증한다.

또한 정의가 확인되지 않은 `PHASE`, `ELAPSS` 두 열의 조합이 target을 거의
결정적으로 분리했다. 표준 PHASES/ELAPSS 계산임을 확인하기 전까지 이 두
열은 baseline에서 제외한다.

## BenchAnXplore D0 준비

- coarse archive: 105 HDF5 + 105 XDMF
- case tensor: 80 timestep velocity, tetrahedral coordinates/connectivity,
  repeated binary boundary mask
- archive SHA-256: `2116bf9e4feb4cd937b3a47a307821359a1010bcf6cc75d94fea70bcc639e579`
- runtime: pinned PyTorch container + read-only external `h5py==3.12.1` layer
- preregistration: `configs/benchanxplore_d0.json`

D0는 Fourier 4/8/12-mode reconstruction의 표현 손실만 측정한다. 학습된
operator 또는 In-PI-MGN 대비 성능으로 해석하지 않는다.

## GPU smoke

과거 `junjinyong`의 PBS `ssu_a6gpu` allocation 안에서 다음을 확인했다.

- GPU: NVIDIA RTX A6000 1장
- PyTorch: 2.5.1+cu118
- CUDA runtime: 11.8
- 2048 × 2048 CUDA matrix multiplication finite check: pass
- smoke exit status: 0

login node에서는 `nvidia-smi`나 학습을 실행하지 않았다.

## 2026-08-08 introai9 V1 scheduler audit

- PBS GPU smoke는 NVIDIA A100-SXM4-80GB, PyTorch 2.5.1+cu118, CUDA 11.8에서
  finite 2,048 × 2,048 matrix multiplication과 exit 0을 확인했다.
- 공식 release에서 서버 내 독립 재생성한 Aneumo compact cache는 64 case,
  512 member의 CRC 검사를 통과했고 등록 SHA-256
  `9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`와
  일치했다. Field와 cache는 공개 저장소에 복사하지 않는다.
- Exact `2ddd5e6`의 최초 V1 array와 same-source diagnostic은 metric 이전에
  실패했지만 PBS stdout이 반환되지 않았다. Exact `fd8bb40`은 task-local
  log를 남겨 pinned runtime이 device 객체를 받은 CUDA peak-memory reset을
  거부한 것을 cache load 전 traceback으로 분리했다.
- 이 source correction은 device 0을 선택하고 CUDA bookkeeping API를
  current-device 형식으로 호출한다. Scientific config와 selector는 그대로며,
  새 exact full contract와 one-task diagnostic을 모두 통과한 뒤에만 fresh
  12-task array를 제출한다. 기존 실패 artifact는 삭제하지 않는다.
- Exact task source `a0479fb`의 fresh array는 12개 checkpoint/metric과
  no-test-read 검사를 모두 통과했다. 첫 aggregate job은 result를 만들기 전에
  exit 1이었고 PBS가 지정 stdout을 반환하지 않았다. Aggregate wrapper에도
  task-local log/status fail-safe를 적용한 별도 ops source를 사용하되, model과
  12개 task artifact는 exact `a0479fb` read-only 상태로 replay한다.
- Observable replay는 cache `float32`의 `0.002499999944...`와 registered
  `0.0025`를 response-only oracle이 `1e-12`로 직접 비교해 result 전에
  중단됐음을 확인했다. Cache ordering은 기존 loader tolerance로 검증하고
  anchor와 ratio는 registered design value에서 계산한다. Aggregate code SHA와
  task/checkpoint SHA는 별도 provenance field로 남긴다.
- Aggregate source `78dca92`의 corrected replay는 exit 0으로 12개 checkpoint,
  validation replay, separate task/source provenance와 no-test-read를 확인했다.
  V1 gate는 5/7 fail이며 q-PointNet worst-seed full-q/response L2는
  `1.03459/1.00354`다. Public aggregate SHA-256은
  `f67970c4d8028bf869ae793a776ed86d32b9cc477a9ba414e54bf9c8fab6a9b1`이다.
  현재 branch를 재학습하지 않고 fixed-checkpoint V1a attribution만 등록한다.
- Exact source `3a0d27f`의 dependency-complete contract는 서버 고정
  container에서 183/183, V1a 전용 torch metric 5/5, protocol/site check를
  통과했다. PBS job `115051`은 실제 A100 80GB allocation에서 27초, exit 0으로
  완료됐고 12 checkpoint, train/validation field만 읽었다. Raw attribution
  SHA-256은 `4e11be6f3c73b338383c24a3c78902ad782f05f5e2ce0fa93e61b4351269d91a`다.
  Public aggregate는 raw의 family mean, truth-only diagnostic, access와
  authorization을 값 변경 없이 옮겼다. Test read, retraining과 checkpoint
  write는 없었다.
- 후속 asset discovery는 official ZIP64 archive 1의 central directory와 case
  1 q=0.0025 VTP header에 한정했다. Existing compact cache와 달리 official
  archive에는 mesh/STL, volume VTU, inlet/outlet/wall VTP와 connectivity,
  `U/p`가 있다. 이미 본 범위를 V1b config에 공개했다. Exact source
  `fb1c21a`의 CPU audit은 20 archives·64 cases, 384 required member와 60
  train representative VTP를 검사해 8/8을 통과했다. Validation/test payload와
  field arrays는 읽지 않았다. V1c는 geometry array decode 전에 고정됐고
  20 train representative×3 patch×3 flow에서 geometry-only q-invariance,
  topology, area/frame와 compact-cache coordinate frame만 감사해 exact source
  `84fc244`에서 8/8을 통과했다. 180 payload, 60/60 q-invariant patch,
  minimum polygon-valid fraction 1.0과 field/test-read false를 확인했다.
  V1d는 validation geometry payload decode 전에 고정됐으며 exact source
  `369317a`의 CPU run에서 train 40·validation 12·test 0 case의 boundary 468개와
  volume 52개 geometry payload를 감사해 9/9을 통과했다. 156/156 patch의
  q-invariance와 52/52 exact boundary-volume correspondence를 확인했다. 이
  asset pass 뒤 V1e known-condition baseline을 학습 전에 고정했다. Exact
  `c62838b`의 6개 GPU task는 login node가 아닌 PBS A6000 allocation에서 모두
  exit 0으로 완료됐다. 각 task는 exact source, 두 private cache checksum,
  pinned container/dependency, CUDA device, validation-only checkpoint와 no-test
  access를 기록했다. CPU-only pinned-container aggregate가 6 task provenance를
  전수 검사했고 gate는 6/9로 실패했다. Public aggregate SHA-256은
  `63fdb3a6fbddb15bb8d6cb82fde7b6880e3b3c7badef46b7a4cc2da4d31f2c0e`다.
  Raw log, checkpoint와 per-task history는 private output에만 보존한다.

## Run contract

각 run은 최소한 다음을 남긴다.

```text
git_commit.txt
command.txt
environment.json
run_config.json
dataset_manifest.sha256
status.json
metrics.json
```

실패 run도 삭제하지 않는다. 첫 grouped-fold 구현 오류 run은 빈 fold를
감지하고 즉시 종료됐으며, 수정 commit에서 synthetic unit test와 실제
CMHA split smoke를 통과한 뒤 다시 제출했다.

공개 PBS template:

- `cluster/ssu_a6gpu_smoke.pbs`
- `cluster/ssu_a6gpu_contract_tests.pbs`
- `cluster/ssu_a6gpu_cmha_g1.pbs`
- `cluster/ssu_a6gpu_benchanxplore_d0.pbs`
- `cluster/ssu_a6gpu_controlled_g1r.pbs`
- `cluster/ssu_a6gpu_controlled_g1s.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n0.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n0_attribution.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n0r.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n1_development.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n1_optimization_attribution.pbs`
- `cluster/ssu_a6gpu_controlled_density_attribution.pbs`
- `cluster/ssu_a6gpu_controlled_density_development.pbs`
- `cluster/pbs_gpu_smoke.pbs`
- `cluster/pbs_aneumo_isbi_v1.pbs`
- `cluster/pbs_aneumo_isbi_v1_aggregate.pbs`

V1 template에는 queue 이름을 고정하지 않는다. 제출 시 private 운영 가이드에
따라 `introai9`의 허용 queue를 명시하며, login node에서는 GPU runtime을
조회하지 않는다. 12개 model×seed task가 모두 완료된 뒤 별도 aggregate job이
checkpoint를 validation-only로 replay한다. Aggregate는 같은-q seed 평균,
seed×8 q의 24-component missing mixture, response-only physical oracle,
lexicographic selector와 7개 feasibility check를 계산한다. Raw checkpoint와
per-task log는 private output에 보존한다.

첫 exact `2ddd5e6` V1 array는 세 subjob이 metric/checkpoint 생성 전 동일한
exit 1로 끝나 pending subjob을 취소했다. PBS stdout 반환도 exit finalization에
머물러, model/config를 바꾸지 않고 task output 내부에 `pbs.log`와
`pbs_status.json`을 직접 기록하도록 execution wrapper만 보강한다. 실패
artifact는 보존하며 새 exact contract와 one-task diagnostic 전에는 full
array를 재제출하지 않는다.

G1r template은 기존 G1 실패를 덮어쓰지 않는다. Public source commit과
`configs/controlled_pde_g1r.json`을 read-only로 bind하고 새 output
directory만 writable로 둔다. Density/operator checkpoint selection이 끝난
뒤 fresh test split을 생성하며, scheduler artifact에는 config checksum과
`failed_g1_relabeled=false`를 남긴다.

Exact commit `951ace1`의 full G1r은 A6000에서 정상 완료됐지만 gate는
실패했다. Public aggregate는
`results/controlled_pde_g1r_20260803.json`이다. 동일 fresh seed를
architecture 선택에 재사용하지 않으며, 다음 GPU job은 별도의 post-result
density attribution만 허용한다. Aneumo 학습과 nonlinear/3D confirmatory
job은 새 exact sanity 근거 전까지 제출하지 않는다.

Post-G1r density attribution은 별도 세 diagnostic seed에서 density
network만 학습한다. True-parameter, analytic population NLL, empirical
NLL과 matched-budget geometry×condition cells를 비교하며 result threshold가
없다. Exact commit, config checksum, environment, status와 aggregate
metric을 남기되 G1/G1r status는 항상 failed로 보존한다.

Nonlinear N0는 exact `0ead687` source와 pinned container로 실행했다.
Dependency-complete contract 90개와 metric job은 모두 exit 0이었으나
worst-seed nonlinear departure가 frozen threshold를 통과하지 못했다.
공개 aggregate는 `results/nonlinear_pde_n0_20260803.json`이다. 완료된
solver 실행을 성공한 method 실험으로 표현하지 않으며 N1과 3D job은
N0 re-entry 전까지 제출하지 않는다.

N0a는 같은 pinned container와 A6000 allocation에서 실행하되
`configs/nonlinear_pde_n0_attribution.json`을 read-only로 bind한다.
원래 N0 seed의 all-context diagnostic만 생성하며 status artifact에는
`has_gate_decision=false`, `n0_status=failed_unchanged`,
`n1_authorized=false`를 반드시 남긴다.

Exact `749f596` N0a는 A6000에서 exit 0으로 완료됐다. 첫 contract 제출은
외부 h5py layer를 누락해 unrelated BenchAnXplore test 하나가 metric 전에
실패했고, 동일 source에 pinned `h5py==3.12.1` layer를 추가한 재실행은
97/97 test를 통과했다. 공개 aggregate는
`results/nonlinear_pde_n0_attribution_20260803.json`이다.

N0r는 exact preregistration commit `1a68053`의 config를 이후 source
commit에서도 그대로 pin한다. PBS artifact에는 config checksum, exact
execution commit, reference/paired flat indices, represented-context count와
모든 check를 남긴다. N0r metric은 dependency-complete contract test가
같은 execution source에서 통과한 뒤에만 제출한다.
Exact `37d31a8`의 dependency-complete PBS contract는 105/105 test를
통과했고, 이어진 fresh 3-seed A6000 metric job은 exit 0으로 9/9 check를
통과했다. 공개 aggregate는 `results/nonlinear_pde_n0r_20260805.json`이다.
이는 N1 사전등록만 허용하며 상세 config commit 전 N1 학습을 제출하지
않는다.

N1의 첫 GPU 경로는 confirmatory run이 아니라 validation-only core
development다. `AURORA_DEVELOPMENT_INDEX`는 config의 두 development seed
중 하나만 선택하며 density train/validation과 operator train/validation만
생성한다. Runner에는 test split 생성 호출이 없고 status에
`test_generated_or_accessed=false`, `n1_gate_decided=false`를 기록한다.
Joint-density/operator checkpoint는 server output에만 두며 공개 저장소에
commit하지 않는다. 이 smoke가 성공해도 모든 preregistered baseline과
checkpoint freeze 전에는 confirmatory test job을 제출하지 않는다.

첫 N1 contract attempt는 metric 제출 전에 unflattened coordinate envelope
shape 오류를 검출했다. 동시에 source SHA 변수가 exact commit이 아니어서
이 attempt는 결과와 무관하게 provenance-invalid로 보존한다. Shape fix는
frozen scientific contract를 바꾸지 않으며 새 full SHA contract가
통과하기 전 development metric job을 제출하지 않는다.

Exact `6075530` contract는 113/113을 통과했고 development seed 0 job도
exit 0이었다. Train/validation solver는 모두 수렴했지만 operator
full-BC/paired-response relative L2 0.1739/0.1862로 checkpoint-ineligible다.
Test는 생성하지 않았다. 다음 server job은 unit-peak envelope의 development
seed 1뿐이며 confirmatory seed/job은 계속 금지한다.

Exact `54046a3`의 114/114 contract와 development seed 1은 exit 0이었다.
Unit-peak operator는 full-BC/paired-response L2 0.05771/0.05729로
개선됐지만 0.05를 넘었다. 다음 PBS job은
`cluster/ssu_a6gpu_nonlinear_pde_n1_optimization_attribution.pbs`의
threshold-free N1a뿐이다. 네 variant는 같은 새 development seed와
train/validation split을 쓰며 test contexts를 0으로 강제한다.
Exact commit `cf675af`의 30-task A6000 run은 exit 0으로 완료됐고 공개
aggregate는 `results/controlled_pde_density_attribution_20260803.json`이다.
이 결과로 nonlinear/3D job을 제출하지 않으며 다음 GPU 실행은
development-only grouped-moment estimator 비교다.

DA2는 exact committed source를 read-only bind해 empirical NLL과 세 grouped
moment/shrinkage 후보를 768×8/3,072×8에서 비교한다. 세 seed×여덟 task의
24개 학습을 한 A6000 allocation에 직렬 배치해 scheduler overhead와 idle
GPU를 줄인다. Run은 descriptive development selection을 기록할 수 있지만
selection은 768×8에서만 수행하고 3,072×8은 data-sufficiency control이다.
`new_gate_defined_or_passed=false`와
`nonlinear_or_3d_training_authorized=false`를 항상 보존한다.

Exact `18dbfcd` DA2는 24 task를 exit 0으로 완료했다. 첫 container
contract-test attempt는 기존 BenchAnXplore test의 외부 `h5py` layer가
bind되지 않아 환경 실패했고, 같은 commit의 attempt 2는 pinned
`h5py==3.12.1` layer와 72 tests를 모두 통과했다. Scientific result는
첫 test attempt와 무관하게 full run exit 0 및 두 번째 test pass가 함께
확인된 뒤에만 채택했다.

G1s는 DA2의 data-sufficiency 신호를 별도 fresh exact test로 검증한다.
등록된 public commit과 `configs/controlled_pde_g1s.json`을 read-only로
bind하며, G1r 대비 fresh seed와 training geometry 768→3,072만 바꾼다.
Validation/test 192/192, empirical NLL, model, optimizer, metric과 threshold는
유지한다. 다섯 seed 전체 gate가 끝나기 전에는 nonlinear/3D job을 제출하지
않고, pass하더라도 data quantity를 method contribution으로 기록하지 않는다.

Exact `b0e555a`의 G1s는 dependency-complete 82-test contract와 A6000
fresh 5-seed run을 모두 exit 0으로 완료했다. 일곱 frozen check가 모두
통과해 다음 nonlinear/3D protocol 등록이 허용됐다. Raw run은 계속
비공개 provenance로 보존하고 공개 aggregate만
`results/controlled_pde_g1s_20260803.json`에 둔다. 과거 G1/G1r은
relabel하지 않는다.

Nonlinear 단계는 learned model부터 제출하지 않는다.
`cluster/ssu_a6gpu_nonlinear_pde_n0.pbs`가 exact committed source와
`configs/nonlinear_pde_n0.json`을 read-only bind해 한 A6000 allocation에서
세 numerical-audit seed를 실행한다. 33×33 solver, nested 65×65 reference,
linear counterfactual, 8-component paired perturbation을 같은 job에 묶는다.
Output에는 command, commit, config hash, environment, aggregate metric과
실패 여부를 남긴다. N0가 통과해도 N1 등록만 허용하며 3D headline job은
제출하지 않는다.

N0는 failed로 보존됐고 fresh context-stratified N0r만 9/9를 통과했다.
그 뒤 validation-only N1b checkpoint 50개를 동결하고 exact source
`62605a0`의 N1c outer test를 실행했다. Dependency-complete contract는
125/125, PBS A6000 metric job은 exit 0이었지만 field distribution,
paired response와 acquisition regret가 실패해 N1은 closed다. Route
candidate VoI의 common-random-number 위반 보조 지표는 제외하되 gate
판정은 바꾸지 않는다. Same checkpoint/test를 쓰는 threshold-free N1c-a도
exact source `b97899c`에서 완료됐다. Contract job `109738`은 130/130,
metric job `109739`는 5 seed 모두 exit 0이었다. Joint density가 모든
mask에서 independent heads보다 conditional NLL이 나빴고, high-budget
acquisition과 corrected route regret도 robust superiority를 회복하지
못했다. Raw/per-context artifact는 private provenance에 보존하고 공개
aggregate만 `results/nonlinear_pde_n1c_attribution_20260806.json`에 둔다.
N1d shift와 irregular 3D job은 제출하지 않는다.

Post-N1c development는 두 read-only-source PBS job으로 분리한다.

- `cluster/ssu_a6gpu_nonlinear_pde_n1_density_objective_audit.pbs`는
  0–4 array의 각 A6000 allocation에서 fresh model seed 하나와 네 objective를
  함께 실행한다. Seed별 checkpoint·history·per-context metric은 private
  output에만 두고, 다섯 job이 모두 완료된 뒤 aggregate만 공개한다.
- `cluster/ssu_a6gpu_nonlinear_pde_n1_decision_task_audit.pbs`는 checkpoint
  mount 자체가 없으며 true law/simulator-only audit 한 개만 실행한다.
  solver batch size 2,048을 config에 고정했고 calibration/audit split 외 N1 test
  seed를 생성하거나 읽지 않는다.

두 job 모두 exact public commit과 config hash의 container contract가 먼저
통과해야 제출한다. 하나의 결과를 먼저 보고 다른 config·seed·mask·sample
budget을 바꾸지 않으며, 어느 결과도 N1c relabel이나 3D 실행 권한으로 쓰지
않는다.

Exact source `337c75e`의 dependency-complete contract job `110165`는
144/144 test를 통과했다. Density array `110170[0-4]`와 task job `110171`은
모두 PBS exit 0이었고 test access false였다. Task walltime은 58:04,
solver 2,882 batch는 모두 수렴했으며 최대 normalized residual은
\(5.94\times10^{-6}\)이었다. Frozen aggregate만 공개해
`results/nonlinear_pde_n1_density_objective_audit_20260806.json`과
`results/nonlinear_pde_n1_decision_task_audit_20260806.json`에 둔다.
Checkpoint, training history와 per-context metric은 private output에
보존한다. Full-joint density signal과 missing-only task adequacy는
development 방향을 좁히지만 새 method·fresh re-entry·N1d/3D 권한을
열지 않는다.

M0는
`cluster/ssu_a6gpu_nonlinear_pde_n1_missing_operator_pullback_m0.pbs`의
0–2 A6000 array로만 실행한다. Public source와 N1b checkpoint root는
각각 read-only, seed output만 writable로 bind한다. 각 array index는
fresh density seed와 seed-matched pair-loss-zero frozen operator 하나를
사용한다. Runner는 checkpoint SHA-256, config/source commit, train/selection/
audit split, operator audit L2, solver convergence, test-access false와
private per-context metric을 기록한다. 세 seed가 전부 exit 0일 때만 한 번
aggregate하며, 일부 결과를 보고 config나 남은 job을 바꾸지 않는다.
M0 실패 또는 execution-incomplete 뒤 같은 mechanism의 weight/kernel/sampler
repair job은 제출하지 않는다.

Exact source `89bdc85`의 실제 array `115078`은 seed 0/2가 exit 0, seed 1이
`candidate_risk_matrix`의 truncated conditional rejection stall로 exit 1이었다.
세 seed 완결 조건을 충족하지 못해 aggregate를 실행하지 않았고 성공 seed
metric도 gate 용도로 읽지 않았다. 공개 execution record만 남기며 상태는
`execution-incomplete / no scientific verdict`다. One-shot 규약에 따라
sampler repair·rerun·fresh re-entry job은 제출하지 않는다.

## Aneumo selective-cache contract

사전등록한 32 AneuX base family × 2 deformation의 selective range staging은
완료됐다. 전체 release를 복제하지 않고 필요한 512 internal member만 읽어
64 case × 8 mass-flow condition × 4,096 node의 compact HDF5를 만들었다.
Train/validation/test는 20/6/6 base family와 40/12/12 case이며, 모든
coordinate와 pressure/velocity field가 finite이고 condition 간 coordinate
contract가 일치한다. Cache SHA-256은
`9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`다.
License의 CC BY-NC-ND 제약 때문에 raw/compact field와 derived rendering은
공개 저장소에 넣지 않는다.

이 무결성 통과는 learned response의 필요성을 뜻하지 않는다. 먼저
`configs/aneumo_scaling_audit_v1.json`에 사전등록한 CPU audit이 train
family field만 읽고, same-case anchor를 가진 analytic 및 train-tuned
power-law scaling이 설명하지 못한 paired response를 측정한다.
Validation/test field access는 금지하고, 결과는 base-family bootstrap
aggregate만 저장한다. 두 채널 모두 고정된 0.15 lower-bound 기준을
실패하면 Aneumo G2 학습은 중단한다.

Exact commit `e12ff0a`의 pinned CPU run은 52개 전체 test 뒤 exit 0으로
완료됐다. Train 20 family/40 case만 분석하고 validation/test 24 case의
field는 읽지 않았다. Velocity tuned-power residual은 0.2112
`[0.2001, 0.2243]`로 eligible, pressure는 0.1369
`[0.1190, 0.1496]`로 ineligible이었다. Public aggregate는
`results/aneumo_scaling_audit_20260803.json`이다. 이 결과는 learned G2
실행 권한이 아니며 exact density attribution이 먼저다.

template에는 서버 절대경로를 넣지 않고 `AURORA_PROJECT_ROOT`,
`AURORA_DATA_ROOT`, `AURORA_OUTPUT_ROOT`, `AURORA_SIF`를 제출 시 주입한다.

## 2026-08-08 · ISBI V0 metadata-only audit

- Exact public source: `0589070063cfaac765e6d6785653880be860e861`
- Config SHA-256: `0c9745e42e84149d5f788a4e4425ab02028267cc9d1e0b4685ec92d7baf43559`
- Raw result SHA-256: `ec6b50269e929b3b3fad109b239f7c220e22a628222c95b077249656b84ffb50`
- Runtime: pinned container, Python 3.11.10, NumPy 2.1.2, external
  `h5py==3.12.1`; CPU metadata-only, no GPU allocation
- Result: exit 0, 8/8 check pass; cache field arrays and validation/test field
  were not read
- Authorization: V1 64-case implementation smoke only. Outer test, headline
  and submission remain false.

## 2026-08-08 · ISBI V1 pre-learning contract

- First exact source `b8ce721`: model contract 8/9. Parameter range 15.283%
  failed the frozen 15% check; no cache field or learned metric was read.
- Corrected exact source `a8b0042f52d008f5085b7f6c16091682cd649917`:
  q-PointNet residual blocks 16→17 only; tolerance and other contracts unchanged
- Targeted model contract: 9/9, including rigid-rotation equivariance and
  parameter matching
- Dependency-complete full contract: 168/168, exit 0, pinned container and
  read-only `h5py==3.12.1` layer
- Scientific status: learning unrun; test field, outer test, headline and
  submission remain false

후속 exact task source `a0479fb`는 12/12 exit 0이었고 aggregate source
`78dca92`의 replay 결과 gate는 5/7 fail이었다. 위 항목은 실행 전 contract
이력으로만 보존한다. Current status는 이 문서의 앞쪽 V1 scheduler audit과
`results/aneumo_isbi_v1_20260808.json`을 따른다.

## 2026-08-03 G1 exploratory result

최종 sensitivity는 public code commit `900fedc`, 5 outer folds × 5 repeats,
3-fold inner selection, patient bootstrap 1,000회로 실행했다.

| 비교 | AUPRC |
|---|---:|
| clinical | 0.777 |
| clinical + morphology | 0.759 |
| clinical + morphology + real-CFD summary | 0.717 |

Incremental `ΔAUPRC=-0.0419`, patient-bootstrap 95% CI
`[-0.1083, 0.0066]`이다. 현재 exploratory evidence는 incremental utility를
지지하지 않는다. 공식 case map, feature provenance와 second model family
확인 전 confirmatory G1은 `unresolved`로 유지한다.

공개 aggregate result:
`results/cmha_g1_exploratory_20260803.json`
