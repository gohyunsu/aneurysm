# AGENTS.md — AURORA 연구 운영 규약

이 파일은 사람과 자동화 에이전트가 동일한 연구 가정과 품질 기준으로
작업하기 위한 단일 운영 메모다. 2026-08-03 KST에 팀 대화, 기존 저장소,
공개 1차 문헌을 재검토하여 작성했고 2026-08-05 KST N0r/N1 상태를
반영했다.

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
  Acquisition/route는 결과와 무관한 context index 0,4,…,188과 condition
  0만 사용한다. True oracle은 global latent radius 2.5 truncation을
  conditional component acceptance와 residual rejection으로 정확히
  반영한다. Exact N1c source를 public commit하고 dependency-complete
  contract를 통과하기 전 test 생성은 계속 금지한다. Registered support,
  geometry, hidden-law shift는 model·threshold·test seed를 바꾸지 않는
  별도 N1d secondary job으로 둔다. Irregular-3D headline은 positive N1
  전까지 보류한다.
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

AAAI-26 LANO, NeurIPS-25 PaPQS·DeltaPhi, arbitrary-conditioning generative
model, 2026 conditioning-consistency와 NeurIPS-25 neural-operator
Thompson-sampling 연구를 고려하면 partial observation,
joint density의 analytic conditioning, tower-property 검사, paired
residual, active acquisition을 각각 단독 novelty로 주장할 수 없다. 현재
C1–C3는 **검증할 연구 가설**이지 확정 contribution이 아니다. 독립적
novelty는 이들을 PDE solution functional에 맞게 결합했을 때 생기는 새
문제 정의·보장·알고리즘과 strong baseline 대비 양수 결과가 함께 있을
때만 확정한다.

현재 가장 유망하지만 아직 확정하지 않은 paper identity는
**conditioning inconsistency의 solution-functional decision consequence**다.
경로가 다른 posterior가 같은 최종 관측 mask에서 달라질 때 bounded
functional loss의 Bayes action과 다음 BC component의 value-of-information가
얼마나 흔들리는지를 regret으로 정의한다. Posterior TV/KL에서
Bayes-regret를 제한하는 보장, joint BC–solution model의 route
compatibility, N1의 실제 regret 감소가 함께 있어야 한다. Test-time active
feature acquisition 자체, path independence 자체, 이름만 붙인 acquisition
head는 novelty가 아니다. ACFlow류 generative AFA, ICML-24 acquisition
conditioned oracle와 NOTS-style posterior-sample functional acquisition을
필수 baseline으로 둔다. NOTS는 whole input-function query 문제이므로
N1 adaptation을 원 논문 재현으로 표현하지 않는다.

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
