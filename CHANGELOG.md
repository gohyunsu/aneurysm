# Changelog

연구 결정, 데이터 계약, 모델 설계, 실험 프로토콜, 사이트 변경을 함께
기록한다. 단순 오탈자는 묶어서 기록할 수 있지만 연구 주장을 바꾼 변경은
독립 항목으로 남긴다.

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
