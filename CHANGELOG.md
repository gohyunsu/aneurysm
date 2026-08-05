# Changelog

연구 결정, 데이터 계약, 모델 설계, 실험 프로토콜, 사이트 변경을 함께
기록한다. 단순 오탈자는 묶어서 기록할 수 있지만 연구 주장을 바꾼 변경은
독립 항목으로 남긴다.

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
