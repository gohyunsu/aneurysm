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
2. MLP/FNO backbone으로 nonlinear regular-grid paired-condition pilot
3. Same geometry multi-BC 자산에서 pair sampler와 response loss
4. GNN+latent-token irregular 3D operator
5. D0b와 learned compute-matched 비교를 모두 통과할 때만 선택된
   one-shot transient decoder
6. Secondary real-CFD/status analysis는 operator evidence가 확보된 뒤 재검토

전체 architecture를 한 번에 학습하지 않는다. 각 단계는 이전 단계보다
어떤 claim을 새로 지지하는지와 중단 기준을 함께 기록한다.
