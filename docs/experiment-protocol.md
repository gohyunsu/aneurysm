# AURORA v2 사전 실험 프로토콜

버전: 2.0-draft · 2026-08-03

연결 설정: `configs/aurora_v1.json`

결과를 본 뒤 primary metric, split, threshold를 바꾸면 새 버전과
`exploratory` 표기를 남긴다.

## 1. 검증할 가설

- **H1 · Coherence:** 하나의 joint BC density를 conditioning해 만든
  AURORA가 독립 mask head, imputation, generic stochastic operator보다
  nested observation mask 사이의 projective consistency와 conditional
  coverage가 좋다.
- **H2 · Response:** same-geometry paired-response loss가 matched data/compute
  baseline보다 BC 변화에 따른 \(\Delta H\)를 더 정확히 예측한다.
- **H3 · Attribution:** BC-sample variance는 condition error를, ensemble
  variance는 geometry OOD error를 각각 더 잘 추적한다.
- **H4 · Generality:** H1–H3가 exact controlled PDE, nonlinear PDE,
  irregular 3D aneurysm에서 같은 방향으로 성립한다.
- **H5 · Efficiency secondary:** D0를 통과한 one-shot temporal basis가
  autoregressive rollout보다 compute-matched Pareto frontier를 개선한다.

## 2. Gate와 실행 순서

### G0 · asset integrity

- geometry/condition family가 split을 넘어 중복되지 않음
- BC coefficient의 unit, waveform phase, inlet/outlet identity 확인
- field coordinate frame, timestep, mesh marker, solver provenance 확인
- license와 공개 가능한 aggregate 범위 확인

하나라도 불명확하면 그 modality는 학습하지 않는다.

### D0 · temporal representation oracle

BenchAnXplore 105 geometry × 80 timestep에 Fourier 4/8/12 mode를 projection
한다. Primary \(K=8\)의 frozen threshold:

- full relative L2 ≤ 0.01
- retained temporal energy ≥ 0.995
- cycle mean/peak speed relative MAE 각각 ≤ 0.02
- bulge relative L2 ≤ 0.02

통과는 표현력만 의미한다. Learned model 성능이나 novelty로 보고하지 않는다.

2026-08-03 attempt 1은 scheduler walltime 30분 32초에 exit `-29`로
종료됐고 metric이 없었다. 동일 protocol의 attempt 2는 정상 완료됐지만
frozen \(K=8\) gate를 통과하지 못했다. Full relative L2 0.0162, peak
relative MAE 0.0214, bulge relative L2 0.0616이었다. \(K=12\)도 bulge
relative L2 0.0293으로 0.02 기준을 넘었다. Fixed Fourier branch는
중단하고 equal-coefficient nonperiodic/train-only basis만 exploratory
D0b에서 비교한다.

D0b의 coefficient budget은 결과를 본 뒤 임의로 늘리지 않는다.

| 후보 | budget | fit 범위 | 평가 |
|---|---:|---|---|
| DCT-II | 17, 25 | 고정 basis | held-out geometry |
| Temporal POD | 17, 25 | train geometry covariance only | held-out geometry |

105 geometry를 고정된 geometry-disjoint fold로 나누고, POD는 매 fold의
training case만으로 fit한다. Mean을 별도 무료 parameter로 더하지 않고
uncentered second moment의 rank 안에 포함해 coefficient budget을 지킨다.
Frozen D0와 같은 full L2, retained energy, cycle mean/peak, bulge L2
기준을 사용한다. D0b는 D0 실패 뒤 설계한 exploratory representation
diagnostic이며 D0를 대체하지 않는다.

2026-08-03 D0b 결과:

| 후보 | full rel. L2 | peak rel. MAE | bulge rel. L2 | frozen 기준 |
|---|---:|---:|---:|---|
| DCT-II 17 | 0.01644 | 0.02588 | 0.06486 | 실패 |
| DCT-II 25 | 0.00644 | 0.00813 | 0.03084 | bulge 실패 |
| train-only POD 17 | 0.00141 | 0.000764 | 0.00880 | 모두 충족 |
| train-only POD 25 | 0.000598 | 0.000211 | 0.00371 | 모두 충족 |

POD 17/25는 learned comparison에 eligible하지만 선택된 architecture는
아니다. D0b가 105 case 전체의 held-out reconstruction을 architecture
discovery에 사용했으므로 같은 benchmark의 learned comparison은
exploratory로 보고한다. Confirmatory G3에는 D0b에 쓰지 않은 fresh
transient case 또는 독립 pulsatile dataset이 필요하다.

### G1 · exact condition–marginal coherence

정답 conditional distribution을 계산 가능한 controlled PDE에서 평가한다.

#### Data

- train/validation/test simulation family 분리
- correlated boundary coefficient distribution
- full, 25/50/75% random partial, missing mask
- interpolation mask와 support-shifted BC test 분리

#### Primary

- exact conditional mean standardized error
- 90% pointwise/simultaneous coverage error
- random-projection energy distance
- nested-mask projective consistency error

#### Gate

- standardized mean error ≤ 0.05
- coverage absolute error ≤ 0.03
- projective consistency error ≤ 0.05

이 sanity gate를 못 넘으면 aneurysm model을 구현하지 않는다.

Frozen 5-seed run은 maximum mean error 0.1504, coverage error 0.0377,
raw projective distance 0.1129로 실패했다. Direct masked Gaussian보다
모든 mask의 error/energy score는 개선했지만 이는 gate pass가 아니다.
Finite-sample two-sample floor와 density/operator error를 분해하는 G1b는
명시적으로 post-result exploratory diagnostic으로 기록한다.

#### G1b · 실패 원인 귀속만 수행

G1b는 frozen G1의 같은 5 seeds, train/test geometry, epoch, model을
재학습한다. threshold를 조정하지 않고 다음만 계산한다.

1. \(K=128,512,2048\)에서 두 iid sample set의 sliced-distance를
   finite-sample floor로 측정한다.
2. joint direct sampling과 `left→right`, `right→left` nested sampling의
   raw distance에서 같은-\(K\) iid floor를 함께 보고한다. Gaussian
   nested factorization의 mean/covariance residual은 analytic하게
   별도 확인한다.
3. exact Poisson의 선형성을 이용해 conditional-mean error를
   `sampling only`, `learned BC density only`, `learned operator only`,
   `end-to-end`로 분해한다.
4. 각 distance는 8회 sampling replicate와 32개 고정 random projection을
   사용한다.

`G1b complete`는 `G1 passed`를 뜻하지 않는다. 새로운 absolute threshold를
설정하거나 G1 결과를 소급해 바꾸려면 독립된 새 confirmatory protocol과
새 데이터 생성이 필요하다.

2026-08-03 G1b는 5 seeds에서 정상 완료됐다. \(K=128\)의 learned
direct-vs-nested distance는 0.1006, iid floor는 0.1013, signed excess는
−0.00073이었다. 반대 nesting 방향 signed excess도 0.00013이었고 analytic
moment residual은 \(7.45\times10^{-9}\)였다. Raw projective threshold
실패는 finite-sample floor로 귀속됐다.

반면 \(K=2048\) missing-mask mean error는 end-to-end 0.0853,
density-only 0.0754, operator-only 0.0341, sampling-only 0.0325였다.
Density estimation이 주 잔여 오차이며 G1은 닫힌 상태다. G1b는 coverage
귀속을 포함하지 않았으므로 frozen worst-seed coverage failure를 해결했다고
표현하지 않는다.

#### G1r · prospective fresh-test re-entry

G1r은 G1b 결과를 본 뒤 만든 **새 protocol**이며 frozen G1을 수정하거나
소급해 pass로 바꾸지 않는다. 실행 전
`configs/controlled_pde_g1r.json`에 다음을 고정한다.

- frozen G1 config/result와 G1b result checksum
- 기존 G1과 겹치지 않는 5개 seed, train/validation/test seed offset
- 768/192/192 geometry family와 geometry당 8 conditions
- density NLL과 operator objective의 분리 학습 및 disjoint-validation
  early stopping; test는 checkpoint 선택 뒤에만 생성
- analytic density-only conditional moment·coverage
- 12-point-per-axis Gauss–Hermite end-to-end conditional mean
- \(K=2048\) sampled coverage
- 양방향 nesting의 \(K=1024\) direct-vs-nested distance에서 matched iid
  floor를 뺀 across-seed 95% CI upper bound

Frozen thresholds:

| metric | 최대 허용값 |
|---|---:|
| density-only standardized mean error | 0.05 |
| density-only 90% coverage error | 0.03 |
| end-to-end quadrature mean error | 0.05 |
| end-to-end sampled coverage error | 0.03 |
| full-BC operator error | 0.03 |
| projective signed-excess 95% CI upper | 0.01 |
| analytic nesting moment residual | \(10^{-6}\) |

한 seed의 최선값이 아니라 5개 seed 중 최악값을 gate에 사용한다. Projective
항만 route별 seed mean의 bootstrap CI upper bound를 쓴다. Pass는 새로운
exact-domain pipeline sanity evidence일 뿐 C1 superiority나 AAAI novelty
증거가 아니다. 실패하면 nonlinear/3D confirmatory branch로 가지 않고
density family·data sufficiency를 다시 분석한다.

#### G1r 결과 · prospective negative

Public source commit `951ace1`, config SHA-256
`7f5779d53143b6b77d0b1f9ac4c5d1a98b0b7fce908fcd68891e33270ec58b8a`의
5-seed A6000 run은 exit 0으로 완료됐고 gate는 실패했다.

| 사전등록 metric | 최악 seed/route | 기준 | 판정 |
|---|---:|---:|---|
| density-only standardized mean | 0.07533 | 0.05 | fail |
| density-only 90% coverage error | 0.01605 | 0.03 | pass |
| end-to-end quadrature mean | 0.07518 | 0.05 | fail |
| end-to-end sampled coverage error | 0.01808 | 0.03 | pass |
| full-BC operator error | 0.00375 | 0.03 | pass |
| projective excess CI95 upper | 0.000202 | 0.01 | pass |
| analytic nesting residual | \(7.45\times10^{-9}\) | \(10^{-6}\) | pass |

Mean 관련 두 실패는 같은 seed에서 나타났고 다섯 seed 중 두 seed가 0.05를
넘었다. 다섯 seed 평균 density-only error 0.04921이 기준 아래여도
worst-seed contract를 사후 변경하지 않는다. 15개 seed×mask 셀의 descriptive
비교에서는 AURORA가 direct masked Gaussian보다 mean error와 energy score가
각각 15/15에서 낮았지만, 상대 개선은 absolute gate 실패를 상쇄하지 않는다.
결과는 `results/controlled_pde_g1r_20260803.json`에 공개한다.

다음 단계는 새로운 confirmatory run이 아니라 post-result density
attribution이다. Oracle-parameter regression, analytic population NLL,
geometry×condition sample-scaling으로 representation, optimization,
finite-data 요인을 분리한다. 이 진단에 fresh gate seed를 사용하지 않으며,
결과를 본 뒤 선택한 estimator는 다시 독립된 protocol과 seed를 고정해야
한다.

### G2 · paired response fidelity

동일 geometry에서 다중 BC field가 있는 dataset을 사용한다.

- outer test: geometry-disjoint
- ID partial/missing test: field energy score, calibration,
  matched-coverage interval width
- full-BC condition test: train support와 분리된 amplitude/waveform/split을
  **입력으로 제공**하고 field 및 paired \(\Delta H\) relative L2 평가
- partial/missing hidden-law shift: OOD detection과 abstention만 평가;
  shifted distribution의 coverage는 식별 가능하다고 가정하지 않음
- geometry/parameter OOD: ensemble model uncertainty와 error association
- pair sampler는 geometry 안에서만 pair 생성
- pair-distance bin을 small/medium/large로 고정

Primary comparison:

`AURORA – strongest compute-matched probabilistic operator`

Primary metrics:

- functional-space energy score
- paired-delta relative L2
- 90% matched-coverage interval width

세 지표 중 response와 distributional score가 함께 개선되어야 한다.

### G3 · transient efficiency

D0 통과 때만 실행한다.

- identical geometry split and BC information
- same preprocessing and query count
- train GPU-hour와 parameter budget 보고
- autoregressive In-PI-MGN/MeshGraphNet, direct-time operator와 비교
- BenchAnXplore learned 비교는 architecture discovery 후 exploratory
- fresh transient case/독립 pulsatile dataset에서 selected candidate 재검증
- field/spectral/peak error, latency, peak memory의 Pareto frontier 보고

One-shot이 단순히 빠르고 부정확하거나, 정확하지만 compute가 더 크면 핵심
주장에서 제외한다.

### G4 · cross-domain generality

Controlled PDE, nonlinear PDE, irregular 3D에서 같은 method가 strong
baseline을 일관되게 개선해야 한다. 한 domain에서만 양수면 application
paper로 범위를 축소하고 AAAI general method claim을 하지 않는다.

## 3. 데이터 역할

| 데이터 | 역할 | 현재 상태 |
|---|---|---|
| Controlled PDE | exact conditional/marginal oracle | 구현 우선 |
| Nonlinear PDE | ID mask calibration + supplied-BC shift response | semilinear/Burgers pilot 사전 등록 예정 |
| Aneumo | same-geometry × 8 steady BC | 32 base-family × 2 deformation selective pilot 등록; staging pending |
| AneuG-Flow | irregular 3D pretraining | geometry archive만 local; BC variation 없음 |
| BenchAnXplore | transient GNN baseline/D0 | 105×80 audited; D0 실행 |
| CMHA | secondary real-CFD/status diagnostic | exploratory increment negative |
| AneuX | secondary external association stress | real CFD 없음 |

Full multi-terabyte archive를 먼저 받지 않는다. Remote manifest에서 shard
크기, case/BC grouping, checksum을 확인한 뒤 최소 pilot subset만 승인된
storage에 가져온다.

## 4. Baseline matrix

### Partial-condition operator

| ID | BC 처리 | Solution model | coherence |
|---|---|---|---|
| B0 | zero imputation + mask | deterministic operator | 없음 |
| B1 | train mean imputation + mask | deterministic operator | 없음 |
| B2 | conditional mean imputation | deterministic operator | point only |
| B3 | mask-token direct head | heteroscedastic operator | empirical |
| B4 | independent head per mask | probabilistic operator | 없음 |
| B5 | MC dropout | direct operator | 없음 |
| B6 | deep ensemble | direct operator | 없음 |
| B7 | public probabilistic/flow operator | function-space generator | 비교 대상 |
| B8 | shared BC density, pair loss 0 | coherent pushforward | 있음 |
| B9 | AURORA full | coherent pushforward | 있음 |

B7 구현은 해당 저자의 공개 코드와 지원 입력 범위에 맞춘다. 지원하지 않는
arbitrary mask를 임의로 유리하게 개조하지 않고 adaptation을 명시한다.

### Irregular 3D backbone

- PointNet/Graph U-Net deterministic
- MeshGraphNet/In-PI-MGN autoregressive
- GNOT/Transolver-style direct operator
- 같은 backbone을 쓴 B3/B8/B9

Novelty 비교에서는 backbone을 고정하고 boundary mechanism과 pair loss만
바꾼다.

## 5. Split

### Operator

- primary split unit: geometry 또는 simulation family
- 같은 geometry의 BC, timestep, crop, resolution, augmentation은 모두 같은
  outer fold
- BC-support split은 geometry split과 직교하게 구성하되, OOD BC 값을
  제공한 response extrapolation과 hidden-law shift detection을 분리
- train-only PCA, normalization, BC density fitting
- validation으로 architecture와 sample 수를 선택
- test는 seed나 threshold 선택에 사용하지 않음

### Secondary clinical

- patient ID split
- multiple aneurysm patient는 같은 fold
- outer 5-fold × 3 repeats, inner 4-fold
- preprocessing, imputation, calibration은 fold 안에서만 fit
- 현재 negative exploratory G1 때문에 headline table이 아님

## 6. Metric 정의

### Field

- relative L2, normalized RMSE
- magnitude/direction error
- wall/interior 및 anatomical region별 error
- temporal spectral error와 peak phase error

### Paired response

\[
\mathrm{RelL2}_{\Delta} =
\frac{\|(\hat H_j-\hat H_i)-(H_j-H_i)\|_2}
{\|H_j-H_i\|_2+\epsilon}.
\]

Pair마다 먼저 계산한 뒤 geometry 단위로 평균한다. 큰 response pair가
case 수를 압도하지 않도록 distance stratum도 함께 보고한다.

### Distribution

- field/function random-projection energy score
- scalar functional CRPS
- 50/80/90/95% coverage
- matched-coverage interval width
- exact oracle가 있으면 mean/covariance error

### Coherence

Nested \(M_1\subset M_2\)에 대해 두 경로를 비교한다.

1. \(M_1\)에서 직접 BC completion 후 solution pushforward
2. \(M_1\)에서 추가 component를 sample하고 \(M_2\)로 조건화한 뒤 주변화

동일 random projection과 sample budget에서 energy distance를 계산한다.
Monte Carlo floor는 oracle sampler 대 oracle sampler로 추정해 함께 표기한다.

### Uncertainty attribution

- BC variance ↔ held-out BC squared error rank correlation
- model variance ↔ geometry OOD squared error rank correlation
- swapped association을 negative control로 보고
- selective risk/coverage curve

### Physics·functional

검증된 discretization에서만 divergence, mass imbalance, no-slip을 계산한다.
WSS/OSI/RRT는 wall gradient pipeline과 단위가 확인되기 전 headline에 쓰지
않는다. BenchAnXplore D0는 velocity와 cycle speed만 평가한다.

### Efficiency

- training GPU hour, inference latency, peak memory
- parameter 수, BC samples \(K\), ensemble \(E\)
- preprocessing와 meshing time 별도

## 7. Ablation과 falsification

1. pair loss 0
2. true same-geometry pair ↔ random cross-geometry pair
3. joint BC density ↔ independent mask heads
4. full covariance ↔ low-rank+diagonal ↔ diagonal
5. unconditional ↔ anatomy-conditioned BC density
6. \(K=4/8/16/32/64\) completion sample
7. ensemble 1 ↔ 5
8. deterministic ↔ probabilistic backbone
9. Fourier 4/8/12 ↔ autoregressive/direct-time
10. rotated/scaled/decimated geometry
11. BC amplitude and outlet policy support shift
12. randomized BC–field pairing negative control

같은 data example budget, optimizer search budget, backbone을 맞춘다.

## 8. 통계

- headline result: 최소 5 seeds
- geometry 또는 simulation family cluster bootstrap 2,000회
- paired model difference를 같은 outer-test prediction에서 계산
- primary comparison과 metric은 config에 고정
- effect size와 95% CI가 우선
- subgroup는 exploratory와 multiplicity를 명시
- “SOTA”는 같은 split/data/BC information을 사용한 비교에서만 허용

## 9. 결과 표 계약

모든 표는 `booktabs` 스타일로 통일하고 다음 열을 유지한다.

`domain | split hash | mask | method | field/response metric | distribution
metric | coverage | compute | mean ± 95% CI`

- 소수점 자리: error/score 3자리, coverage 1 percentage point, latency 단위 명시
- best는 통계적으로 구분되는 경우만 bold
- second-best 장식은 사용하지 않음
- 실패 run과 제외 이유는 supplement provenance table에 남김

## 10. Figure 계약

1. **Method figure:** nested mask → analytic BC conditioning → shared
   pushforward → uncertainty axes
2. **Exact PDE figure:** oracle와 predicted conditional mean/interval,
   full/partial/missing을 같은 sample에 표시
3. **Paired response figure:** 같은 geometry에서 두 BC의 real/predicted
   \(\Delta H\), error map
4. **3D sample figure:** 사전 정의한 median, worst, OOD case; cherry-pick 금지
5. **Calibration figure:** mask별 coverage–width와 uncertainty attribution
6. **Efficiency figure:** error–latency Pareto

의료 figure는 비식별 공개 sample만 사용하고 case identifier를 표시하지
않는다.

## 11. 현재 secondary clinical evidence

CMHA exploratory linear diagnostic:

| 입력 | AUPRC |
|---|---:|
| clinical + morphology | 0.759 |
| clinical + morphology + hemodynamics | 0.717 |

\(\Delta=-0.0419\), patient-bootstrap 95% CI
\([-0.1083,0.0066]\). 공식 case map과 second model family가 없어
confirmatory verdict는 unresolved지만, 현재는 real-CFD incremental utility를
지지하지 않는다. Risk-retention은 계산하지 않고 C1–C3와 분리한다.

## 12. 계산 우선순위

1. 실행 중 D0 완료·판정
2. G1 exact controlled PDE, 5 seeds
3. Nonlinear regular-grid C1/C2 pilot
4. Full paired-BC shard manifest와 최소 subset 확보
5. G2 ablation, 성공할 때만 irregular 3D backbone 확장
6. G3 learned transient 비교
7. G4 cross-domain 통합 table

GPU는 PBS allocation 안에서만 사용한다. 각 run은 commit, command,
environment, config, dataset checksum, status, aggregate metric을 남긴다.
