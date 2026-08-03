# AGENTS.md — AURORA 연구 운영 규약

이 파일은 사람과 자동화 에이전트가 동일한 연구 가정과 품질 기준으로
작업하기 위한 단일 운영 메모다. 2026-08-03 KST에 팀 대화, 기존 저장소,
공개 1차 문헌을 재검토하여 작성했다.

## 1. 연구의 현재 기준선

- 프로젝트명: **AURORA**
- 정식 명칭: **Aneurysm Uncertainty-aware Reconstruction Operator for
  Reliable Assessment**
- 주 연구 문제: **partial/missing physical-condition operator learning**
- 의료용 secondary endpoint: 공개 데이터의 **cross-sectional rupture
  status**. 현재 negative G1 signal 때문에 primary contribution이 아니다.
- 핵심 문제: full, partial, missing BC에서 각각 만든 예측이 서로 무관하면
  같은 물리계에 대해 모순된 분포를 낼 수 있다. 하나의 joint BC–solution
  model에서 유도되는 조건부/주변 분포로 일관되어야 한다.
- 핵심 방법: analytic conditioning이 가능한 BC density + conditional
  geometry operator + nested observation-mask marginalization +
  same-geometry paired response supervision.
- 현재 증거: D0 frozen \(K=8\)과 exact G1 absolute gate가 모두 실패했다.
  G1은 direct masked Gaussian보다 모든 mask에서 상대적으로 좋았지만 claim은
  `unsupported`다. G1b에서 \(K=128\) raw projective distance가 iid sampling
  floor와 같고 analytic nesting residual이 \(7.45\times10^{-9}\)임을
  확인했다. 그러나 \(K=2048\) missing-mask mean error는 0.0853이며
  density-only 0.0754가 지배적이므로 G1은 닫힌 상태다. 별도 `G1r`은
  fresh seed, validation-only checkpoint selection, analytic
  density moment/coverage, Gauss–Hermite end-to-end mean, iid-floor-calibrated
  projective metric을 결과 전에 고정한 prospective re-entry다. G1r 결과는
  frozen G1을 소급해 pass로 바꾸지 않는다.
- Fixed Fourier \(K=4/8/12\)는 bulge gate를 통과하지 못했으므로 현재
  one-shot temporal architecture에서 제거한다. Equal-budget nonperiodic
  D0b에서 DCT-II 17/25는 탈락했고 train-only POD 17/25는 모든 frozen
  threshold를 통과했다. POD는 learned compute-matched 후보일 뿐 아직
  선택된 temporal architecture나 novelty가 아니다.
- 최종 주장은 “미래 파열 위험을 예측한다”가 아니라 “불완전한 물리조건
  아래에서도 일관되고 보정된 PDE solution distribution을 학습한다”이다.

다음 아이디어는 주 방법론이 아니다. 비교·ablation으로만 남긴다.

- In-PI-MGN에 attention, node masking, V/W-cycle을 단순 추가
- geometry-only case에 deterministic WSS/OSI를 정답처럼 부착
- 1-step 또는 50-step velocity RMSE만으로 임상 유용성 주장
- ruptured/unruptured label을 2년/5년 prospective risk로 표현
- 서로 다른 공개 데이터셋을 파일명 유사성만으로 patient-level 병합

## 2. 현재 contribution 가설

논문 contribution은 아래 세 축으로 제한한다.

1. **Nested condition–marginal coherence**: full/partial/missing BC를 별도
   head나 임의 imputation으로 처리하지 않는다. 하나의 BC density를 임의
   observation mask에 analytic conditioning하고 solution operator로
   pushforward하여 tower property를 구조적으로 만족시킨다.
2. **Paired simulator-response supervision**: 동일 geometry의 두 BC에서
   절대 field뿐 아니라 `H(G,Bj)-H(G,Bi)`를 직접 감독하여 geometry
   confounding 없이 condition response를 학습한다. 인과 효과가 아니라
   simulator intervention response로만 부른다.
3. **Structural/model uncertainty separation**: BC completion sample 간
   변동과 model ensemble 간 변동을 law of total variance에 맞춰 분리하고,
   ID mask별 calibration·supplied-BC response shift·geometry OOD에서 각각
   검증한다. Hidden-BC 생성법칙 자체가 shift된 경우에는 정답 coverage를
   식별 가능하다고 가정하지 않고 OOD detection/abstention만 평가한다.

GNN, attention, probabilistic operator, flow matching, physics loss,
one-shot Fourier는 선행 구성요소 또는 engineering choice다. contribution
문구에 단독 novelty로 올리지 않는다. Fixed Fourier decoder는 D0에서
실패했으며, 다른 temporal decoder도 새 representation gate와
compute-matched 이득이 있을 때만 남긴다.

## 3. 데이터셋의 역할

| 데이터 | 허용된 주 역할 | 금지된 해석 |
|---|---|---|
| Aneumo | 동일/유사 geometry의 다중 steady BC로 BC sensitivity pretraining | patient-specific clinical evidence |
| AneuG-Flow | 대규모 synthetic steady 및 selected pulsatile pretraining | real cohort generalization |
| BenchAnXplore | 105 semi-idealized transient field의 재현·baseline | geometry-only clinical deployment |
| CMHA | patient CTA/mesh, clinical, morphology, real-CFD bridge와 task gate | multi-center external validation로 과장 |
| AneuX | 750 geometry/status의 external association stress test | real hemodynamics validation |
| Aneurisk | provenance가 확인된 geometry/morphology 보조 평가 | asset audit 전 CFD 보유 가정 |

모든 case/field에는 `source_field ∈ {real_cfd, surrogate, synthetic_cfd}`와
dataset version, checksum, unit, coordinate frame을 기록한다.

## 4. 연구를 계속할지 결정하는 gate

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
- **G2 · Paired response fidelity**: ID partial/missing calibration과
  supplied full-BC support-shift response를 분리한다. Strong probabilistic
  baseline보다 field distribution과 paired response가 모두 개선되어야
  하며, hidden-law shift에서는 detection/abstention만 주장한다.
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
5. `site/assets/research-data.js`
6. `CHANGELOG.md`

사이트의 변경 이력은 `site/assets/research-data.js`에서 렌더링한다. 단순
미관 수정이 아니면 날짜, category, decision, rationale, affected files를
기록한다. README와 사이트가 서로 다른 연구 질문을 말하면 배포하지 않는다.

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
- `introai9`는 뇌동맥류 source asset과 manifest를 읽기 전용으로 감사한다.
- GPU 실험은 `junjinyong`의 PBS scheduler allocation에서 실행한다. login
  node에서 GPU 학습이나 `nvidia-smi`를 실행하지 않는다.
- pinned Singularity image를 사용하고 code/data는 read-only, output만
  writable로 bind한다.
- run은 commit, command, environment, config, dataset checksum, status,
  aggregate metrics를 남긴다. 실패 run도 provenance로 보존한다.
- 2026-08-03 smoke 기준은 RTX A6000, PyTorch 2.5.1+cu118, CUDA 11.8이다.
  사양은 매 job에서 다시 기록한다.
- 2026-08-03 Aneumo 공식 ZIP64 release를 HTTP byte-range로 감사해 첫
  shard의 geometry 1--40마다 8개 steady mass-flow condition이 있음을
  확인했다. Geometry 1의 두 internal NPY는 CRC와
  `(N,7)=xyz+pressure+velocity` contract를 실제 검증했다. 32개 AneuX
  base family × 2 deformation selective pilot만 사전 등록했으며,
  synthetic case가 아니라 base family 단위로 split한다. Raw/compact
  field는 CC BY-NC-ND 조건에 따라 공개 저장소에 재배포하지 않는다.
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
  exploratory 표기가 필요하다.
- D0b 구현은 DCT-II/POD orthonormality, held-out covariance exclusion,
  synthetic two-pass runtime을 pinned container에서 통과했다. Exact public
  commit `1dfc856`의 105-case run은 exit 0, walltime 3분 49초였다.
  POD-17 full L2 0.00141, bulge L2 0.00880, peak error 0.000764였고
  POD-25도 통과했다. DCT-25는 bulge L2 0.03084로 탈락했다. Public
  aggregate는 `results/benchanxplore_d0b_20260803.json`이다.
