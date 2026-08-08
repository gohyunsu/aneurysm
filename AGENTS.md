# AGENTS.md — AURORA 연구 운영 규약

이 파일은 사람과 자동화 에이전트가 동일한 연구 가정과 품질 기준으로
작업하기 위한 단일 운영 메모다. 2026-08-03 KST에 팀 대화, 기존 저장소,
공개 1차 문헌을 재검토하여 작성했고 2026-08-08 KST ISBI V1
backbone gate 5/7 fail, V1a attribution, V1b/V1c asset audit 8/8 pass와
V1d development geometry-cache audit 등록 상태를 반영했다.

## 1. 연구의 현재 기준선

- 프로젝트명: **AURORA**
- 정식 명칭: **Aneurysm Uncertainty-aware Reconstruction Operator for
  Reliable Assessment**
- 주 연구 문제: **partial/missing physical-condition operator learning**
- 제출 목표: **IEEE ISBI 2027 archival four-page regular paper**,
  2026-10-26 23:59 USA EDT. 현재는 `not submission-ready`다.
- ISBI headline은 actual irregular-3D aneurysm **velocity-only**
  reconstruction·response·calibration evidence가 있을 때만 연다. Exact와
  nonlinear PDE만으로 biomedical-imaging contribution을 주장하지 않는다.
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
  payload decode 전에 고정했다. V1d는 train 40·validation 12·test 0 case의
  boundary 468개와 reference-volume 52개 payload에서 geometry array만 읽어
  q-invariance, polygon/frame, compact coordinate bounds와 모든 boundary point의
  exact volume-point correspondence를 검사한다. Pass도 known-condition strong
  baseline **protocol 등록**만 허용한다. V1 relabel, 기존 backbone 수선,
  model training, test geometry/field, V2, partial/missing method, novelty와
  submission은 계속 금지한다.
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

현재 prospective 개발 가설은 **coherence–conditional-accuracy trade-off를
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
제외한다. `M0`는 이 mechanism의 development eligibility만 판정하며 아직
선택된 method나 fresh re-entry가 아니다.

Test-time active
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
  pullback의 3-seed M0 development gate만 결과 전에 등록했다. M0는 N1
  test를 생성하거나 읽지 않으며 통과해도 re-entry가 아니다.
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

### Local repair loop 금지

- 결과가 약하거나 한 check가 실패했다는 이유로 같은 evidence 안에서
  loss weight, kernel scale, mask, seed, threshold, sample budget을 순차
  조정하지 않는다.
- 사전등록 gate는 한 번 집계해 즉시 과학적 판정을 내린다. M0가 실패하면
  해당 operator-pullback mechanism을 폐기하고 실패 artifact를 보존한다.
- 새 가설은 실패 원인을 설명하는 독립 이론·task gap이 있을 때만 새
  version과 fresh seed로 등록한다. 같은 mechanism의 국소 repair는 새
  이름을 붙여도 허용하지 않는다.
- 운영 문제는 `server artifact → scientific decision → public
  protocol/site/changelog → private manuscript pin` 순서로 처리한다.
  로컬 dependency·tmp·TeX 문제는 한 번만 bounded diagnosis하고,
  authoritative validation은 frozen PBS와 GitHub CI로 한다.
- ISBI target을 이유로 실패한 N1c나 M0를 완화하지 않는다. Venue pivot은
  task·evidence 우선순위를 바꾸지만 기존 실패와 test boundary를 바꾸지
  않는다.

### ISBI 2027 제출 규약

- 자세한 단일 출처는 `docs/isbi-2027-plan.md`다.
- 모든 기술 내용·표·그림은 official template 첫 4쪽 안에 둔다. 5쪽은
  reference, ethics, acknowledgments/COI 외 기술 내용을 금지한다.
- Primary는 synthetic-CFD 기반 3D velocity reconstruction 연구다.
  Pressure, WSS/OSI, transient efficiency, rupture prediction과 clinical
  utility는 새 provenance와 prospective evidence 없이는 headline에서
  제외한다.
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
  현재 사용자 지시에 따른 GPU 실행 목표이기도 하다. 2026-08-08 Windows-host
  SSH config를 명시적으로 읽는 public-key BatchMode 접속과 PBS client 존재는
  확인했다. 이는 GPU queue allocation 성공 증거가 아니므로 scheduler GPU
  smoke와 cache SHA를 확인하기 전 learned job을 제출하지 않는다.
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
