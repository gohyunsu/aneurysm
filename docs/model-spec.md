# AURORA v2 모델 명세

상태: method contract · 구현은 단계별 gate 뒤 진행

연결 설정: `configs/aurora_v1.json`

## 0. 한 줄 정의

AURORA는 **GNN을 geometry encoder로 포함하는 hybrid neural operator**이며,
핵심은 GNN이 아니라 full·partial·missing boundary observation에서 나온
예측 분포가 하나의 joint model의 조건부·주변 분포로 일관되게 만드는
것이다.

## 1. 왜 단순 missing-value 문제가 아닌가

geometry \(G\), 전체 BC coefficient \(B\), solution field \(H\), 관측
component mask \(M\)을 둔다. 배포 시에는 \(B_M\)만 관측될 수 있다.

Zero/mean imputation은 관측되지 않은 값을 특정 값으로 고정한다. Full,
partial, missing mode별 독립 head는 같은 사례에 서로 모순된 분포를 낼 수
있다. AURORA는 다음 하나의 확률법칙에서 모든 mode를 유도한다.

\[
p(H\mid G,B_M,M)
=
\int p_\theta(H\mid G,B)\,
q_\phi(B_{\bar M}\mid G,B_M,M)\,dB_{\bar M}.
\]

더 적게 관측한 mask \(M_1\)과 더 많이 관측한 \(M_2\)가
\(M_1\subset M_2\)일 때 tower property가 성립해야 한다.

\[
p(H\mid G,B_{M_1})
=
\int p(H\mid G,B_{M_2})
\,p(B_{M_2\setminus M_1}\mid G,B_{M_1})\,dB.
\]

이를 여기서는 **nested condition–marginal coherence**라고 부른다.
“Consistency”라는 단어 자체는 novelty가 아니다. Neural process의
marginal/conditional consistency 선행연구와 구분해, 임의의 physical
condition observation mask와 PDE solution pushforward에서 무엇을
구조적으로 보장하고 평가하는지 명시한다.

이 보장은 **내부 양립성**에 관한 것이지, 학습 support 밖 hidden-BC
분포의 정확성을 보장하지 않는다. 미관측 component의 생성법칙까지
바뀌면 추가 관측이나 가정 없이 그 test distribution은 식별되지 않는다.
따라서 ID partial/missing calibration, supplied full-BC extrapolation,
hidden-law shift detection을 서로 다른 표로 보고한다.

## 2. 전체 계산 흐름

```text
geometry G ── local graph encoder ── latent geometry tokens ZG ──────┐
                                                                     │
full BC training records ── geometry-conditioned joint BC density    │
                                  │                                  │
observed components + mask ── analytic conditioning                  │
                                  │                                  │
                          K coherent BC completions                   │
                                  └──── conditional field operator ──┤
                                                                     │
same-geometry BC pairs ── paired response supervision ───────────────┘
                                      │
                   K field/function samples + ensemble axis
                                      │
                  structural/model uncertainty decomposition
```

Fully specified CFD는 결정론적 forward problem으로 취급한다. Field의
structural distribution은 주로 미관측 BC를 적분하면서 생기고,
finite-data/model uncertainty는 별도 ensemble 축으로 추정한다.

## 3. 입출력 계약

### Geometry와 query

| tensor | 예시 shape | 의미 |
|---|---:|---|
| `surface_pos` | `[Ns, 3]` | local anatomical frame의 surface point |
| `surface_feat` | `[Ns, Fs]` | normal, curvature, radius, neck distance, node type |
| `edge_index` | `[2, Es]` | triangle 또는 kNN adjacency |
| `query_pos` | `[Nq, 3]` | surface/volume field를 물을 좌표 |
| `query_type` | `[Nq]` | wall, interior, inlet, outlet |
| `anatomy_context` | `[Ca]` | site, diameter, branch topology, scale |

### Boundary observation

BC waveform과 outlet split을 고정 길이 coefficient로 만든다.

| tensor | 예시 shape | 의미 |
|---|---:|---|
| `bc_value` | `[Cb]` | waveform PCA/Fourier, flow split, rheology |
| `bc_mask` | `[Cb]` | 관측된 component는 1, 미관측은 0 |
| `bc_location` | `[Cb, Fl]` | inlet/outlet identity와 spatial context |

값 0과 “관측되지 않음”을 혼동하지 않는다. Mask는 모든 baseline에도
동일하게 제공한다.

### 출력

- `field_samples`: `[E, K, Nq, T, Ch]`
- `functional_samples`: `[E, K, Cf]`
- `bc_completion_samples`: `[K, Cb]`
- `structural_variance`: BC completion 축의 변동
- `model_variance`: ensemble 축의 변동
- `coherence_diagnostic`: nested mask pair별 random-projection discrepancy

여기서 \(E\)는 ensemble member, \(K\)는 BC completion sample이다.

## 4. Module A — geometry encoder

이 모듈은 강한 backbone이지만 논문의 독립 novelty가 아니다.

1. Local edge-message GNN이 곡률, 법선, 상대 위치, geodesic 정보를
   집계한다.
2. `4096 → 1024 → 256` hierarchical pooling에서 inlet, outlet, neck,
   dome landmark를 강제로 보존한다.
3. 128개 latent token과 8개 attention block이 멀리 떨어진
   inlet–aneurysm–outlet 관계를 연결한다.
4. Continuous query decoder가 고정 mesh node가 아닌 임의 좌표에서 field를
   복원한다.

따라서 “GNN 기반인가?”라는 질문의 정확한 답은 **local encoder는 GNN,
전체 모델은 query-based neural operator**다.

## 5. Module B — coherent boundary density

### 5.1 표현

Waveform은 train fold 안에서만 계산한 PCA 또는 고정 Fourier basis의
coefficient로 표현한다. Outlet fraction에는 합이 1이라는 제약을 만족하는
log-ratio 좌표를 사용한다.

### 5.2 joint density

초기 모델은 anatomy-conditioned low-rank Gaussian mixture다.

\[
q_\phi(B\mid A)
=\sum_{c=1}^{C}\pi_c(A)
\mathcal N(B;\mu_c(A),D_c(A)+U_c(A)U_c(A)^\top).
\]

- pilot: \(C=4\), covariance rank 4
- full BC training record의 negative log likelihood로 학습
- boundary density checkpoint는 field/operator loss와 섞어 test에서
  선택하지 않고, geometry-disjoint validation NLL로 별도 선택
- diagonal-only, unconditional empirical Gaussian, KDE를 baseline으로 비교
- 데이터가 density 복잡성을 지지하기 전에는 flow/diffusion prior를 쓰지 않음

### 5.3 arbitrary-mask conditioning

Gaussian component는 임의의 관측 index에 analytic conditioning할 수 있다.
Mixture weight도 관측 likelihood로 Bayes update한다. 따라서 full,
partial, missing mode가 하나의 joint density를 공유한다.

- full mask: 관측 BC에 사실상 delta conditioning
- partial mask: 미관측 component의 conditional mixture
- missing mask: anatomy-conditioned joint prior

이 구조는 별도 mask head의 경험적 consistency regularizer보다 단순하고
검증 가능하다. Non-Gaussian tail이 필요하다는 증거가 생기면 coherent
conditional sampler로 확장하되, coherence test를 먼저 유지한다.

### 5.4 exact-domain estimation contract

Frozen G1은 density NLL을 field objective와 함께 0.1 weight로 최적화했고
validation split을 checkpoint selection에 쓰지 않았다. G1b에서 density
error가 가장 큰 잔여 항으로 확인됐으므로, prospective G1r은 구조를
복잡하게 만들지 않고 optimization과 평가만 분리한다.

- density: full-BC NLL만으로 학습하고 disjoint validation geometry의 NLL로
  early stopping
- operator: full field + paired response로 별도 학습하고 validation field
  objective로 early stopping
- density-only conditional mean·coverage: exact affine Poisson
  pushforward로 analytic 평가
- end-to-end mean: 2-D Gauss–Hermite quadrature로 Monte Carlo mean noise 제거
- nested projective discrepancy: raw distance가 아니라 같은 \(K\)의 iid
  floor를 뺀 signed excess의 across-seed 95% CI upper bound

이는 failed G1을 relabel하는 변경이 아니라 fresh seed를 고정한 새 sanity
protocol이다. 통과해도 architecture novelty나 baseline superiority가
아니다.

G1r 결과는 density-only mean 0.07533, end-to-end quadrature mean
0.07518의 최악 seed로 실패했다. 반면 full-BC operator error 0.00375,
analytic nesting residual \(7.45\times10^{-9}\), projective-excess CI
upper 0.000202와 coverage는 통과했다. 따라서 현재 architecture에서
operator decoder나 nesting algebra를 복잡하게 만드는 것은 근거가 없다.
수정 대상은 BC-density estimator의 **seed-robust mean estimation**이다.

새 density family는 다음 diagnostic 순서 뒤에만 선택한다.

1. true mean/covariance target regression으로 현 MLP 표현력과 optimizer
   ceiling을 측정한다.
2. true Gaussian 사이 analytic cross-entropy로 empirical BC sampling
   noise를 제거한 population objective를 측정한다.
3. geometry count와 condition-per-geometry count를 분리한 sample-scaling
   곡선으로 필요한 관측 구조를 추정한다.

이 post-result 계약은
`configs/controlled_pde_density_attribution.json`에 `DA1`로 고정한다.
세 diagnostic seed와 결과 해석에는 pass threshold가 없고 G1/G1r을
재개방할 수 없다.

DA1에서 analytic population NLL의 최악 density-only error는 0.00495로
회복됐지만 empirical NLL은 checkpoint 선택법에 따라 최악
0.04401/0.04855였다. 따라서 현 density family의 capacity보다 유한 condition
정보에서 mean과 covariance를 함께 추정하는 과정이 병목이다. 다음
development candidate는 다음처럼 제한한다.

1. Geometry별 BC sample mean을 target으로 mean network를 별도 학습한다.
2. 서로 다른 condition의 차이
   \(\tfrac12(B_i-B_j)(B_i-B_j)^\top\)를 사용한 unbiased U-statistic으로
   covariance target을 만들고 mean-estimation noise와 분리한다.
3. Condition 수에 따른 target variance를 반영한 shrinkage와
   geometry-disjoint validation을 사용한다.
4. 최종 Gaussian likelihood는 평가와 calibration에 유지하고 empirical-NLL
   baseline과 동일 network·budget에서 비교한다.

이는 아직 선택된 method나 contribution이 아니다. Development-only 비교
후 단일 estimator를 고정하고 별도 fresh exact sanity를 통과해야 한다.
Non-Gaussian evidence 없이 conditional flow를 추가하지 않는다.

Executable DA2 contract는
`configs/controlled_pde_density_development.json`이다. 기존 empirical NLL,
unbiased grouped moments, covariance shrinkage 0.25/0.50을 동일한
5-output Gaussian density network와 optimizer budget에서 비교한다. 모든
checkpoint는 sampled validation NLL로 선택하며 768×8과 3,072×8 두
training cell에서 평가한다. Estimator 선택은 기존 G1r과 동일한 768×8에서
수행하고 3,072×8은 data-sufficiency control로만 사용해 방법 변경과
4배 geometry 증가를 혼동하지 않는다. Pairwise-difference U-statistic은 unbiased
sample covariance와 동일한 통계량이므로 그 자체를 novelty로 부르지 않는다.
DA2의 최선 estimator도 별도 fresh-seed exact gate 전에는 method로
확정하거나 nonlinear/3D 학습을 허용하지 않는다.

DA2 결과에서 formal selection은 shrinkage 0.50이었지만 기존 empirical
NLL 대비 평균 density-only error 개선은 0.23%에 그쳤고 1/3 seed에서
악화됐으며 population NLL도 더 나빴다. 따라서 grouped moment와 shrinkage를
현행 architecture에 채택하지 않는다. High-data control의 기존 empirical
NLL만 최악 0.02706으로 안정화됐다. 다음 exact re-entry는 architecture
변경 없이 3,072×8 data adequacy만 fresh seed에서 검증한다.

Executable re-entry는 `configs/controlled_pde_g1s.json`이다. G1s는 새
estimator나 architecture를 도입하지 않는다. Density는 G1r과 동일한
5-output Gaussian MLP와 empirical NLL, operator/direct baseline도 동일한
model·loss·optimizer를 사용한다. 유일한 training-side 변화는 독립
geometry 768→3,072이며 condition 수는 geometry당 8로 유지한다.
Validation과 fresh test는 기존 192/192 geometry다. Threshold, analytic
conditional moments, Gauss–Hermite mean,
sampled coverage와 matched-IID-floor projective metric은 G1r과 동일하다.
따라서 통과 시에도 이 절은 engineering/data sufficiency evidence이며
Module B–D의 novelty 증거가 아니다.

Exact `b0e555a` G1s는 fresh 5 seeds에서 모든 frozen check를 통과했다.
최악 density-only/end-to-end mean은 0.02863/0.02977, coverage error는
0.00836/0.01294였다. Analytic nesting residual은
\(7.45\times10^{-9}\), projective excess CI upper는 0.000674였다.
따라서 동일 empirical-NLL pipeline을 다음 nonlinear domain에 사용할
최소 안정성은 확보했다. 이 결과로 Gaussian MLP나 data scale을
architecture contribution으로 승격하지 않는다.

### 5.6 Nonlinear N0 tensor/solver contract

N0는 학습 architecture가 아니라 다음 domain의 입력·출력 식별성과 numerical
reference를 고정한다.

- context \(G\in\mathbb R^5\): forcing 위치·폭·세기, diffusivity bump,
  semilinear coefficient를 결정
- BC \(B\in\mathbb R^8\): 네 edge마다 corner-zero sine basis 두 개
- BC law: \(G\)에 따라 weight/mean/covariance가 바뀌는 2-Gaussian mixture
- field \(u\in\mathbb R^{33\times33}\), reference
  \(u_{\mathrm{ref}}\in\mathbb R^{65\times65}\)
- registered functionals: domain mean, central hotspot, smooth maximum,
  right-boundary outward diffusive flux \(-a_G\partial_nu\)

Damped Jacobi–Newton update는 variable diffusivity face flux와
\(\lambda_Gu^3\)를 함께 푼다. N0에서 convergence, normalized residual,
nested-grid error, nonlinear departure, 여덟 component response, response
effective rank, functional winner diversity를 확인한다. Analytic GMM
conditioning은 direct-union route와 sequential route의 mixture moment가
일치하는지 별도로 검사한다. N0 출력은 learned score가 아니다.

Frozen N0의 solver와 8-component response는 안정적이었지만
nonlinear-departure worst-seed gate가 실패했다. 구현 감사 결과,
context-major flatten tensor를 앞에서 연속 slice해 reference 12개가
단일 context에 몰렸다. 이 실패를 보존하며, operator tensor 계약에
**context와 condition 축을 명시적으로 유지하는 stratified selector**를
추가하기 전에는 N1 architecture를 구현하지 않는다. Selector 수정은
새 seed의 N0r에서만 gate evidence가 된다.

새 selector는 flattened tensor의 암묵적 순서에 의존하지 않는다. 12-case
reference audit에서는 24 context를 균등 간격으로 선택하고 condition
index를 회전한다. 48-case paired audit에서는 24 context를 모두 정확히
두 번 포함한다. N0a는 이 selector를 diagnostic comparison에만 사용하고,
N0r에서만 fresh prospective evidence로 사용한다.

N0a에서 failed seed의 median은 contiguous 0.00774에서 stratified
0.01221, all-case 0.01828로 바뀌었다. 이는 selector 필요성을 정당화하지만
모든 context가 비선형이라는 뜻은 아니다. N0r tensor contract는
reference axis에 24 context를 각각 한 번, paired-response axis에 각각
두 번 포함하도록 한다.

### 5.7 N0r prospective tensor contract

`configs/nonlinear_pde_n0r.json`은 N0a outcome 전에 동결됐다. Runtime은
N0의 PDE/solver config를 그대로 resolve하고 다음 두 index tensor만
교체한다.

- reference index: shape `[24]`, 각 context id가 정확히 한 번
- paired base index: shape `[48]`, 각 context id가 정확히 두 번

두 selector는 context-major flat index를 반환하지만 prefix slice를 쓰지
않는다. Full semilinear solve는 여전히 24×12 전체 case다. N0r result에는
선택된 flat index와 represented-context count를 기록해 contract가 실제
실행됐는지 검증한다.

## 6. Module C — conditional solution operator

주 operator는 완전한 \(B\)가 주어졌을 때 \(H=F_\theta(G,B)\)를 예측한다.

- BC coefficient는 FiLM만으로 주입하지 않고 boundary location token으로
  geometry token과 cross-attention한다.
- Query decoder는 coordinate, query type, local geometry feature를 받아
  velocity/pressure 또는 benchmark solution coefficient를 출력한다.
- Full-BC field loss가 기본 학습 신호다.
- Flux, divergence, no-slip residual은 discretization이 검증된 dataset에서만
  regularizer로 쓴다. “physics guaranteed”라고 부르지 않는다.

Partial/missing prediction은 sampled BC completion을 같은 conditional
operator에 병렬 통과시킨 pushforward distribution이다. 별도의 임의
imputation field head를 두지 않는다.

## 7. Module D — paired simulator-response supervision

동일 geometry \(G\)에 서로 다른 \(B_i,B_j\)와 solution \(H_i,H_j\)가 있을
때 다음을 추가한다.

\[
\mathcal L_\Delta =
\frac{\lVert
[\hat H(G,B_j)-\hat H(G,B_i)]-[H_j-H_i]
\rVert_2}
{\lVert H_j-H_i\rVert_2+\epsilon}.
\]

절대 field loss만 쓰면 geometry 차이가 큰 신호를 지배해 condition
sensitivity를 약하게 학습할 수 있다. Pair loss는 geometry를 고정한
counterpart끼리 비교한다.

필수 검증:

- pair loss weight 0 ablation
- 같은 수의 무작위 cross-geometry pair를 쓴 negative control
- small/large BC distance별 response error
- BC interpolation과 support-disjoint extrapolation 분리
- support-disjoint test에서는 바뀐 BC를 모두 제공한 response와, 일부가
  숨겨진 상황의 OOD detection/abstention을 분리

이는 관측 연구의 causal effect가 아니다. 데이터 생성 simulator 안에서
BC를 바꾼 **paired simulator response**로만 해석한다.

### 7.1 Aneumo의 현재 출력 계약

Train-family만 사용한 사전등록 physical-scaling audit에서, 같은 case의
anchor field와 train-tuned global power를 함께 허용한 뒤에도 velocity
response residual은 0.2112, family-bootstrap CI95
\([0.2001, 0.2243]\)가 남았다. 반면 gauge를 제거한 pressure residual은
0.1369 \([0.1190, 0.1496]\)로 eligibility 기준 0.15를 통과하지 못했다.

따라서 향후 exact sanity를 새로 통과해 irregular-3D 실험이 허용되더라도
Aneumo의 학습·평가 대상은 **velocity response만**이다.

- Pressure head와 pressure/full-field novelty 문구는 headline에서 제외한다.
- 같은-case anchor + train-tuned global power를 반드시 강한 baseline으로
  유지한다.
- 학습 모델은 절대 velocity field뿐 아니라 anchor 대비
  \(\Delta u\)를 개선해야 한다.
- 이 audit은 train-only nontriviality screen이다. Learned accuracy,
  validation/test generalization, G2 통과를 뜻하지 않는다.
- G1s pass로 velocity-only 3D protocol 등록은 허용됐다. 다만
  multicomponent nonlinear N0/N1과 strong baseline을 먼저 검증하고,
  해당 결과 없이 3D pilot을 headline evidence로 사용하지 않는다.

## 8. Module E — uncertainty decomposition

Ensemble member \(e\), BC completion \(k\)의 prediction을
\(\hat H_{e,k}\)라 한다.

\[
\underbrace{\mathbb E_e[\operatorname{Var}_k(\hat H_{e,k})]}
_{\text{BC-induced structural}}
\quad+\quad
\underbrace{\operatorname{Var}_e(\mathbb E_k[\hat H_{e,k}])}
_{\text{model-induced}}
\]

- structural variance는 미관측 BC가 많아질수록 증가해야 하며 held-out BC
  response error를 추적해야 한다.
- model variance는 geometry OOD, 적은 train data, backbone shift에서
  증가해야 한다.
- 두 항을 합친 coverage만 맞추고 성공이라 하지 않는다.

Aleatoric/epistemic이라는 넓은 용어보다 원인이 분명한
`BC-induced`와 `model-induced`를 사용한다.

## 9. 시간 표현의 위치

Fixed Fourier \(K=4/8/12\)는 frozen D0에서 localized bulge error를
회복하지 못해 현행 architecture에서 제거했다. Global retained energy가
0.9997이어도 bulge relative L2가 0.0616이면 의료적으로 중요한 국소
파형을 보존했다고 볼 수 없다는 것이 이 결정의 근거다.

D0b는 17/25 coefficient의 두 equal-budget 후보만 진단한다.

| 후보 | 정의 | leakage 방지 |
|---|---|---|
| DCT-II | 유한 구간의 비주기 cosine basis | 고정 변환 |
| train-only POD | training field covariance의 상위 singular vector | test geometry를 basis fit에서 제외 |

각 후보는 동일한 full L2, retained energy, cycle mean/peak, bulge L2로
평가한다. 하나가 통과해도 곧바로 모델에 채택하지 않는다. Learned
compute-matched 비교에서 autoregressive rollout보다 fidelity–latency
Pareto frontier가 좋아야 선택한다. 아무 후보도 통과하지 않으면
direct-time query 또는 autoregressive decoder를 사용하며, one-shot
temporal representation은 contribution에서 완전히 제외한다.

현재 D0b 구현은 5-fold geometry assignment, case-normalized uncentered
temporal second moment, fold별 train-only eigendecomposition, DCT/POD
projection을 포함한다. Mean vector를 rank 밖의 무료 parameter로 추가하지
않는다. Pinned container에서 orthonormality, held-out covariance exclusion,
synthetic two-pass runtime을 통과했다.

실제 105-case D0b에서 DCT-II 17/25는 탈락했고 train-only POD 17/25는
모든 frozen 기준을 통과했다. 따라서 learned candidate는 POD뿐이다.
Rank 17/25 선택은 learned experiment의 inner validation에서만 수행하고,
같은 BenchAnXplore에서의 결과는 exploratory로 제한한다. Confirmatory
효율 주장은 D0b architecture selection에 사용되지 않은 fresh transient
test에서 재현해야 한다.

## 10. 학습 목적

\[
\mathcal L =
\lambda_f\mathcal L_{\mathrm{full\ field}}+
\lambda_\Delta\mathcal L_{\mathrm{paired\ response}}+
\lambda_B\mathcal L_{\mathrm{BC\ NLL}}+
\lambda_P\mathcal L_{\mathrm{physics}}+
\lambda_F\mathcal L_{\mathrm{functional}}.
\]

Nested coherence는 analytic conditional density와 shared pushforward로
구조화한다. 별도 숫자 loss를 추가해 보이는 것만으로 보장했다고 하지 않고,
random projection에서 empirical tower-property error를 측정한다.

## 11. 필수 baseline

| 범주 | 비교 |
|---|---|
| Imputation | zero, train mean, conditional mean + deterministic operator |
| Mask model | mask-token deterministic operator, 독립 mask별 head |
| Generic UQ | MC dropout, deep ensemble, heteroscedastic Gaussian |
| Generative operator | 공개 probabilistic/flow-matching operator |
| Coherent ablation | joint BC density 없이 direct marginal head |
| Response ablation | pair loss 0, cross-geometry pair |
| 3D transient | In-PI-MGN/MeshGraphNet, direct transformer/operator |

Parameter 수, train examples, geometry split, BC information, search budget,
inference sample 수를 맞춘다.

## 12. 구현 순서

1. Exact controlled PDE에서 analytic BC conditioning과 metric 검증
2. Semilinear 8-component N0 solver/nontriviality gate
3. N0 pass 뒤 MLP/FNO backbone과 LANO/NOP/generic probabilistic/AFA
   baseline을 갖춘 N1 pair/mask/decision-regret experiment
4. N1이 양수일 때 Aneumo velocity-only pair sampler와 response loss;
   pressure head는 새 사전등록 근거 전까지 제외
5. GNN+latent-token irregular 3D operator
6. D0b와 learned compute-matched 비교를 모두 통과할 때만 선택된
   one-shot transient decoder
7. Secondary real-CFD/status analysis는 operator evidence가 확보된 뒤 재검토

전체 architecture를 한 번에 학습하지 않는다. 각 단계는 이전 단계보다
어떤 claim을 새로 지지하는지와 중단 기준을 함께 기록한다.
