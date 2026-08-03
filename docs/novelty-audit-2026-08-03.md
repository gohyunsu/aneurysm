# AURORA novelty audit · 2026-08-03

## 결론

현재 v1을 “missing-BC probabilistic neural operator + Fourier cycle decoder”로
제출하면 AAAI급 독립 novelty가 부족하다. 문제의 중요성은 높지만 다음
요소는 이미 선행연구가 직접 다룬다.

1. BC 분포 밖에서 neural operator가 비식별적이라는 문제 정의
2. function space의 probabilistic/diffusion/flow-matching operator
3. aneurysm transient CFD의 inflow-aware physics GNN
4. Fourier basis를 이용한 non-autoregressive temporal decoding

따라서 GNN, attention, uncertainty, Fourier를 조합했다는 서술은
contribution에서 제외한다.

## 직접적인 prior-art 충돌

| 선행연구 | 이미 해결하거나 주장한 것 | AURORA에 미치는 영향 |
|---|---|---|
| [LANO (AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/37001) | mask-to-predict와 boundary-first latent reconstruction으로 partial spatial input을 다룸 | partial input 또는 boundary-first reconstruction 자체는 직접 선행연구임 |
| [One Operator to Rule Them All? (AI\&PDE at ICLR 2026)](https://openreview.net/forum?id=lDjWQ9UxRy) | varying BC에서 학습되는 것은 boundary-indexed operator family이며, support 밖 BC는 비식별적임을 정식화 | missing-BC 문제 제기 자체를 novelty로 주장할 수 없음 |
| [Flow-matching Operators (ICLR 2026)](https://openreview.net/forum?id=fcBMLJtCoc) | function space에서 conditional probabilistic operator와 residual transport | flow matching을 붙이는 것만으로 novelty가 되지 않음 |
| [Guided Diffusion Sampling on Function Spaces (NeurIPS 2025)](https://openreview.net/forum?id=oAgwvZay2U) | sparse/noisy observation으로부터 PDE solution function을 조건부 sampling | partial observation만으로 차별화할 수 없음 |
| [Neural Operator Processes (arXiv 2026)](https://arxiv.org/abs/2606.22946) | sparse joint input–response observation에서 probabilistic operator decoding | partial-observation field reconstruction은 직접 선행연구임 |
| [Conditioning Consistency Gap (TMLR 2026)](https://arxiv.org/abs/2604.19312) | context 추가와 joint conditioning의 차이를 KL로 정량화 | conditioning consistency라는 문제·metric 자체는 novelty가 아님 |
| [Learned Boundary Extensions (arXiv 2026)](https://arxiv.org/abs/2602.04923) / [Generalized Neural Operator (arXiv 2026)](https://arxiv.org/abs/2607.21932) | 다양한 prescribed BC를 boundary transfer/extension으로 명시적 encoding | known-BC conditioning 또는 transfer architecture는 novelty가 아님 |
| [UQ for OOD PDE Learning (ICML 2024)](https://openreview.net/forum?id=Y50K6DSrWo) | OOD error와 uncertainty, ensemble/diverse head, conservation update | OOD uncertainty 비교가 필수 baseline임 |
| [Flow Matching Neural Processes (NeurIPS 2025)](https://papers.neurips.cc/paper_files/paper/2025/file/a92519f525c00085095fa41c5c46cdb5-Paper-Conference.pdf) | conditional distribution의 marginal/conditional consistency 문제 | consistency라는 단어만으로 novelty를 주장할 수 없음 |
| [One Operator for Many Densities (arXiv 2026)](https://arxiv.org/abs/2605.06873) | joint density를 conditional density로 보내는 conditioning operator의 continuity·approximation | conditioning 연산이나 보편근사 정리 자체는 novelty가 아님 |
| [DeltaPhi (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/12bf28fb68f295f855a5bf0c5a217d6e-Abstract-Conference.html) | 유사한 physical state 사이 residual을 학습하는 architecture-agnostic framework | pair/residual loss 자체는 novelty가 아니며 same-geometry BC contrast의 추가 가치를 입증해야 함 |
| [Physics-Constrained GNN for IA Hemodynamics (npj Digital Medicine 2026)](https://www.nature.com/articles/s41746-026-02404-z) | BenchAnXplore의 transient autoregressive GNN, inflow/OOD 평가, physics loss | GNN+inflow+physics는 직접 baseline이며 primary method가 아님 |

## 살아남는 연구 질문

> 하나의 PDE surrogate가 full, partial, missing boundary observation을 모두
> 받을 때, 서로 다른 observation mask의 예측 분포가 하나의 joint
> boundary–solution model의 조건부/주변 분포로서 일관되도록 학습할 수
> 있는가?

BC를 단순히 dropout하거나 평균 imputation하는 대신,

\[
p_\theta(H\mid G,B_{\mathrm{obs}},M)
=
\int p_\theta(H\mid G,B)\,
q_\phi(B_{\mathrm{mis}}\mid G,B_{\mathrm{obs}},M)\,dB_{\mathrm{mis}}
\]

를 모델의 구조와 학습 목표에 명시한다. \(M\)은 관측된 BC component의
mask다.

## 제안하는 방법론적 핵심

### 1. Physical-condition observation filtration

동일 case에 대해 관측 BC component가 늘어나는 nested mask들을 하나의
observation filtration로 본다. 각 prediction은 별도 head가 아니라 하나의
joint BC law를 조건화하고 같은 solution operator로 pushforward한 분포다.

- full BC: sharp conditional solution
- partial BC: unresolved components만 적분
- missing BC: learned population BC distribution 전체를 적분

비교 대상은 zero/mean imputation, mask-token deterministic operator,
LANO, NOP, MC-dropout, deep ensemble, generic probabilistic operator다.
Tower property는 새 확률 정리가 아니라 이 construction이 실제로
구현됐는지를 검사하는 falsification metric이다.

### 2. Geometry-controlled BC response

동일 geometry \(G\)의 두 BC \(B_i,B_j\)에 대해 절대 field만 맞히지 않고
BC 변화에 따른 paired response를 직접 학습한다.

\[
\mathcal L_{\Delta}
=
\left\|
[\hat H(G,B_j)-\hat H(G,B_i)]
-
[H(G,B_j)-H(G,B_i)]
\right\|.
\]

이는 geometry 차이를 제거한 상태에서 boundary response를 감독한다.
논문에서는 인과 효과가 아니라 **simulator intervention response**로
한정한다. DeltaPhi-style residual operator, pair-loss 0, random
cross-geometry pair와 matched example/compute로 비교해야 독립 효과가
성립한다.

### 3. Structural uncertainty decomposition

BC marginal sample 간 분산과 model ensemble 간 분산을 분리한다.

- BC-induced: 관측되지 않은 물리 입력에 따른 구조적 불확실성
- model-induced: 유한 데이터와 parameter uncertainty

두 값을 합친 interval만 보고하지 않고 held-out BC error, geometry OOD,
observation mask별 coverage로 각각 검증한다. 단, hidden-BC 생성법칙 자체가
학습 support 밖에서 바뀌는 경우 정답 conditional distribution은 추가
정보 없이 식별되지 않는다. ID partial/missing calibration, supplied
full-BC extrapolation, hidden-law OOD detection/abstention을 분리한다.

## one-shot cycle decoder의 위치

Fourier cycle decoder는 contribution이 아니라 효율과 안정성을 위한
architecture choice다. BenchAnXplore D0에서 표현 손실을 먼저 판정하고,
통과할 때만 autoregressive In-PI-MGN과 learned operator를 동일 split과
compute budget에서 비교한다.

BenchAnXplore release는 velocity와 boundary mask를 직접 제공한다. WSS와
OSI는 검증된 spatial-gradient/postprocessing pipeline이 준비되기 전까지
headline target으로 쓰지 않는다.

## AAAI 범용성을 위한 실험 축

의료 case 하나만으로 일반 method novelty를 입증하지 않는다.

1. **Controlled PDE:** BC posterior와 solution distribution의 정답을 계산할
   수 있는 Poisson/Laplace 계열에서 mask consistency와 coverage 검증
2. **Nonlinear PDE:** varying boundary family를 가진 semilinear/Burgers
   benchmark에서 ID mask calibration, supplied-BC response shift,
   hidden-law detection, geometry/parameter shift를 분리
3. **Irregular 3D application:** aneurysm paired-BC field에서 intervention
   response와 observation-mask calibration
4. **Transient efficiency:** BenchAnXplore에서 one-shot cycle과
   autoregressive rollout의 field/spectral error, latency, memory 비교

적어도 controlled PDE와 irregular 3D application에서 같은 method가
동작해야 “aneurysm 전용 trick”이 아닌 AAAI method contribution으로
설득력이 생긴다.

## 현재 accept 가능성 평가

현재 상태는 **아이디어 후보는 유망하지만 AAAI accept-ready는 아니다**.

- positive: 실제 배포 가정의 모순을 정확히 겨냥하고 일반 PDE 문제로 확장
  가능하다.
- negative: full paired-BC 학습 자산과 learned operator 결과가 아직 없다.
- negative: frozen exact G1은 실패했고, estimator confound를 제거한
  prospective G1r은 등록됐지만 아직 실행 결과가 없다.
- critical threat: condition–marginal consistency가 generic probabilistic
  operator보다 calibration과 BC-intervention fidelity를 실제로 개선해야
  한다.
- required evidence: 5 seeds, geometry/BC/mask shift의 식별성별 분리,
  matched-coverage 비교,
  strong autoregressive/direct/probabilistic baselines, compute-matched ablation.

성능 없이 명칭이나 architecture 복잡성만 늘리면 제출하지 않는다.
