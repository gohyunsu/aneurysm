# AURORA 연구 방향

최종 검토일: 2026-08-03 KST

상태: exact G1/G1r failed · G1b/D0b complete · Aneumo scaling audit velocity-only positive · density attribution next

## 1. 현재 판정

기존 v1을 “missing-BC probabilistic neural operator + Fourier cycle decoder”로
제출하면 AAAI급 독립 novelty가 부족하다.

- varying BC 밖 neural operator의 비식별성은 ICLR 2026 연구가 직접
  정식화했다.
- function-space diffusion/flow-matching/probabilistic operator가 이미 있다.
- marginal/conditional consistency는 neural process 문헌에 선행한다.
- aneurysm transient inflow-aware physics GNN은 npj Digital Medicine 2026에
  발표됐다.
- Fourier one-shot decoding은 architecture choice이지 새 원리가 아니다.

따라서 현재는 **아이디어 후보는 유망하지만 accept-ready가 아니다**. GNN,
attention, uncertainty, physics loss를 조합한 것만으로 제출하지 않는다.

## 2. 새 한 문장 연구 질문

> 하나의 PDE surrogate가 full, partial, missing physical condition을 모두
> 받을 때, 임의의 observation mask에서 나온 solution distribution들이
> 하나의 joint condition–solution model의 조건부·주변 분포로 일관되면서
> condition 변화에 대한 paired response까지 보존할 수 있는가?

뇌동맥류는 중요하고 어려운 irregular 3D application이지만, 방법의 유효성은
controlled PDE와 nonlinear PDE에서도 같은 protocol로 검증한다.

## 3. 보존하는 큰 틀과 버리는 주장

| 결정 | 내용 |
|---|---|
| 보존 | geometry와 미관측 physiology가 함께 hemodynamics를 결정한다는 틀 |
| 보존 | 같은 geometry의 다중 BC를 이용해 BC response를 분리하는 데이터 설계 |
| 보존 | GNN local encoder + global token + continuous query operator |
| 보존 | D0 통과 시 one-shot temporal representation |
| 중단 | missing-BC 문제 정의 자체를 novelty로 주장 |
| 중단 | Fourier/GNN/attention/physics loss를 contribution으로 나열 |
| 중단 | 현재 negative evidence에서 rupture-status alignment를 primary로 유지 |
| 중단 | cross-sectional status를 prospective risk 또는 clinical utility로 표현 |

## 4. AURORA v2

**AURORA**는 *Aneurysm Uncertainty-aware Reconstruction Operator for
Reliable Assessment*의 약자다.

### C1. Nested condition–marginal coherence

전체 BC \(B\), 관측 mask \(M\), field \(H\)에 대해

\[
p(H\mid G,B_M,M)
=\int p_\theta(H\mid G,B)
q_\phi(B_{\bar M}\mid G,B_M,M)\,dB_{\bar M}
\]

를 한 모델 안에서 계산한다. 초기 구현은 anatomy-conditioned low-rank
Gaussian mixture를 full BC record에 적합하고, 임의 관측 component에
analytic conditioning한다. 모든 mode는 같은 conditional solution
operator의 pushforward다.

핵심 검증은 별도 head의 숫자가 비슷하다는 것이 아니라, nested mask에서
tower property와 oracle conditional moments/coverage가 맞는지다.

### C2. Paired simulator-response supervision

같은 geometry에서 BC만 바꾼 두 simulation을 pair로 사용한다.

\[
\mathcal L_\Delta =
\|[\hat H(G,B_j)-\hat H(G,B_i)]-[H(G,B_j)-H(G,B_i)]\|.
\]

이는 geometry variation이 큰 absolute field loss 안에서 BC sensitivity가
묻히는 것을 막는다. 논문은 이를 causal effect가 아닌 simulator
intervention response라고 한정한다.

### C3. Structural/model uncertainty separation

BC completion sample과 model ensemble을 두 축으로 유지한다.

- BC-induced structural uncertainty: 미관측 물리 입력 때문에 생김
- model-induced uncertainty: 유한 학습 geometry와 parameter 때문에 생김

첫 항은 BC-held-out error, 둘째 항은 geometry OOD error를 각각 추적해야
한다. 합친 interval coverage 하나만 맞으면 성공으로 보지 않는다.

## 5. 아키텍처의 역할

### Backbone

- local surface: edge-message GNN
- global anatomy: latent-token attention
- continuous output: coordinate query neural operator

따라서 현재 architecture는 GNN을 포함하지만 순수 GNN이 아니다. Backbone은
강한 구현 선택이며 novelty의 중심이 아니다.

### Boundary model

- waveform PCA/Fourier coefficient와 outlet log-ratio를 joint density로 학습
- full/partial/missing mask에서 동일 density를 analytic conditioning
- 관측되지 않은 값과 값 0을 mask로 명확히 구분
- density 복잡성이 데이터로 정당화되기 전에는 diffusion/flow prior를 쓰지
  않음

### Temporal representation

Frozen D0에서 Fourier \(K=4/8/12\)를 80-step field에 oracle projection한
결과, \(K=8\)은 full·peak·bulge 기준을 실패했고 \(K=12\)도 bulge relative
L2 0.0293으로 0.02 기준을 넘었다. 따라서 fixed Fourier decoder는 현재
architecture에서 제거했다.

Post-result exploratory D0b는 Fourier \(K=8/12\)의 실수 coefficient 수와
같은 17/25 budget으로 DCT-II와 train-only POD를 비교한다. POD basis는
각 geometry-disjoint fold의 training geometry에서만 추정한다. 동일한
full·energy·cycle mean/peak·bulge 기준을 모두 통과한 표현만 learned
compute-matched 단계로 보낸다. 통과 후보가 없으면 one-shot temporal
branch 자체를 버린다.

D0b 결과, DCT-II rank 25는 full L2 0.00644와 peak error 0.00813을
회복했지만 bulge L2 0.03084로 탈락했다. Train-only POD rank 17은 full
L2 0.00141, bulge L2 0.00880, peak error 0.000764였고 rank 25도 모든
기준을 통과했다. 따라서 POD 17/25만 learned comparison에 eligible하다.

그러나 D0b의 fold-wise held-out metric에 105 case 전체가 이미 사용됐다.
이 결과로 architecture를 고른 뒤 같은 benchmark에서 얻는 learned
우월성은 architecture-discovery evidence이지 fresh confirmatory test가
아니다. BenchAnXplore 비교는 exploratory로 표시하고, G3 confirmatory
claim은 D0b에 쓰지 않은 transient case 또는 독립 pulsatile dataset에서
반복한다.

## 6. AAAI에 필요한 일반성

의료 case 하나에서 성능이 좋아도 general AI method로 충분하지 않다.

1. **Exact controlled PDE**: conditional field distribution을 계산할 수 있는
   Poisson/Laplace 계열에서 coherence, moment, coverage 검증
2. **Nonlinear PDE**: Burgers/Navier–Stokes 계열에서 condition support shift와
   geometry/parameter shift 분리
3. **Irregular 3D**: 동일 aneurysm geometry의 paired BC에서 field와
   intervention-response 평가
4. **Transient efficiency**: BenchAnXplore에서 autoregressive GNN과
   one-shot cycle을 compute-matched 비교

같은 C1–C3가 처음 세 domain에서 유효해야 G4를 통과한다.

## 7. 성공 기준

### G1 · exact coherence

- exact conditional mean의 standardized error ≤ 0.05
- 90% interval coverage absolute error ≤ 0.03
- nested-mask projective consistency error ≤ 0.05

이 gate는 pipeline sanity다. 통과 자체는 novelty evidence가 아니다.

2026-08-03 frozen run은 세 absolute gate를 모두 통과하지 못했다.
구조화 모델은 direct masked Gaussian보다 모든 mask의 mean error와 energy
score가 좋았지만, claim은 `unsupported`로 유지한다. Raw two-sample sliced
distance의 finite-\(K\) floor와 sampled-mean 오차를 분해하는 G1b는
post-result exploratory diagnostic이며 원래 실패를 소급해 바꾸지 않는다.

G1b 결과, \(K=128\)의 learned direct-vs-nested distance 0.1006은 iid
two-sample floor 0.1013과 구분되지 않았고 반대 nesting 방향도 같았다.
Analytic Gaussian moment residual은 \(7.45\times10^{-9}\)였다. 즉 raw
projective failure는 coherence violation보다 estimator floor였다.

하지만 \(K=2048\) missing-mask end-to-end mean error는 0.0853이었고,
density-only 0.0754, operator-only 0.0341, sampling-only 0.0325였다.
BC-density estimation error가 남아 exact conditional distribution
정확성은 여전히 `unsupported`다. Coverage 귀속은 G1b 범위 밖이므로 frozen
coverage failure도 unresolved다.

새 `G1r`은 이 실패를 숨기지 않고 별도 prospective evidence로 재검증한다.
기존 seed와 겹치지 않는 5개 fresh seed를 미리 고정하고, density NLL과
operator objective를 분리해 geometry-disjoint validation으로만 checkpoint를
고른다. Density-only moment·coverage는 exact Poisson pushforward로,
end-to-end mean은 Gauss–Hermite quadrature로 계산하며, projective metric은
raw two-sample distance가 아니라 matched iid floor 대비 signed excess의
95% CI upper bound를 사용한다. Threshold와 split은
`configs/controlled_pde_g1r.json`에 고정되어 있다. G1r이 통과해도 frozen
G1은 failed로 남고, 이는 C1 novelty가 아니라 다음 domain으로 갈 최소 sanity
근거다.

G1r은 exact public commit `951ace1`의 A6000 run에서 정상 완료됐지만
**실패했다**. Coverage, full-BC operator, analytic nesting,
matched-IID-floor projective-excess의 네 축은 통과했다. 그러나 최악 seed의
density-only conditional-mean error는 0.07533, Gauss–Hermite
end-to-end mean error는 0.07518로 사전 기준 0.05를 넘었다. 다섯 seed
평균은 각각 0.04921, 0.04932였지만 gate는 결과 전에 최악 seed 기준으로
고정했으므로 평균으로 판정을 바꾸지 않는다. 두 seed가 mean 기준을 넘었고,
operator error는 최악 0.00375였으므로 남은 병목은 seed-sensitive BC-density
mean estimation이다. 이 음성 결과는
`results/controlled_pde_g1r_20260803.json`에 보존한다.

다음 실험은 새 architecture를 즉시 붙이는 것이 아니다. Controlled
generator에서만 가능한 세 개의 post-result upper-bound diagnostic으로
오차를 분리한다.

1. true Gaussian parameter를 target으로 회귀해 representation/optimizer
   ceiling을 측정한다.
2. empirical sample 대신 analytic population cross-entropy를 사용해
   finite-condition noise를 제거한다.
3. geometry 수와 geometry당 condition 수를 factorial하게 바꾸되 총
   boundary sample budget을 맞춰 geometry coverage와 repeated-condition
   information을 분리한다.

이 분해에서 empirical data insufficiency가 확인될 때만 shrinkage 또는
hierarchical density estimator를 새 fresh gate로 사전등록한다. 단순히
Gaussian을 flow로 교체하거나 threshold를 완화하지 않는다.

### G2 · paired response

한 숫자에 서로 다른 식별성 문제를 섞지 않는다.

- **ID partial/missing BC:** strong generic probabilistic operator 대비 field
  energy score, calibration, matched-coverage width를 비교
- **full-BC support shift:** 바뀐 BC 값을 실제로 제공한 뒤 field와 paired
  \(\Delta H\) extrapolation을 비교
- **geometry/parameter shift:** BC-induced uncertainty가 아니라 ensemble
  model uncertainty와 OOD score가 실패를 감지하는지 평가
- **partial BC + shifted hidden-BC law:** 추가 정보 없이 정답 분포를
  식별할 수 없으므로 정확한 coverage를 주장하지 않고 failure
  detection/abstention만 평가
- 모든 headline은 5 seeds와 geometry-family bootstrap 95% CI로 보고

Field만 좋아지거나 pair response만 좋아지면 핵심 주장을 축소한다.

Aneumo의 사전 비자명성 감사에서는 same-case anchor와 train-tuned global
power를 준 뒤에도 velocity residual median 0.2112, base-family bootstrap
CI95 `[0.2001, 0.2243]`가 남아 0.15 하한을 통과했다. Pressure는 0.1369
`[0.1190, 0.1496]`로 실패했다. 따라서 future irregular-3D G2는
velocity-only 후보이며 pressure/full-field response novelty는 폐기한다.
이 train-only 결과는 model 성능이 아니며 G1/G1r을 재개방하지 않는다.

### G3 · transient efficiency

- D0b의 equal-budget nonperiodic/train-only oracle representation 통과
- compute-matched autoregressive baseline 대비 cycle field/peak error와
  latency의 Pareto improvement
- D0b architecture selection에 쓰이지 않은 fresh transient test에서 재현

아니면 one-shot branch를 버린다.

### G4 · cross-domain generality

Controlled, nonlinear, irregular-3D 세 domain에서 같은 coherence/response
method가 strong baseline을 일관되게 개선해야 한다.

## 8. 가장 큰 위협

1. **Coherence가 자명한 재매개화에 불과할 위험**

   Generic joint probabilistic operator와 비교해 calibration, response,
   sample efficiency 중 실질적 개선을 보여야 한다.

2. **직접 선행연구가 빠르게 좁히는 gap**

   Neural Operator Processes는 sparse joint input-output observation에서
   probabilistic field를 복원하고, Generalized Neural Operator와 learned
   boundary extension은 다양한 known BC를 명시적으로 처리한다. AURORA는
   partial response reconstruction이나 prescribed-BC accuracy를 novelty로
   주장하지 않고, physical-input mask lattice의 compatibility와
   same-geometry response를 직접 비교해야 한다.

3. **BC density misspecification**

   Gaussian mixture tail이 실제 waveform distribution을 못 담으면 coverage가
   무너진다. Density-only calibration과 posterior predictive check를
   solution metric과 분리한다.

4. **Paired loss가 단순 data augmentation일 위험**

   Cross-geometry pair negative control, pair-distance strata, matched example
   budget을 통해 같은 데이터량 효과와 구분한다.

5. **의료 특화 trick으로 보일 위험**

   비의료 PDE 두 축에서 같은 method와 metric을 먼저 제시한다.

6. **paired-BC pilot의 family diversity와 license**

   Aneumo ZIP64 selective cache에서 64 case × 8 steady mass-flow 조건을
   검증했지만 synthetic deformation끼리 base AneuX anatomy를 공유한다.
   Split은 synthetic case가 아니라 base family에서 끊었다. 현재 32
   family × 2 deformation pilot은 C2의 방향성만 평가하며 full-release
   또는 임상 일반화를 주장하지 않는다. CC BY-NC-ND 원시·compact field와
   derived rendering은 공개 저장소에 재배포하지 않는다. Learned G2 전에
   same-case anchor를 가진 analytic/train-tuned power scaling이 남기지
   못한 response가 있는지 train family에서만 감사한다.

## 9. 논문 포지셔닝

작업 제목:

**AURORA: Coherent Neural Operators under Partial and Missing Boundary
Conditions**

논문의 순서는 application이 아니라 method claim에 맞춘다.

1. partial-condition operator family의 모순 문제
2. nested condition–marginal construction
3. paired simulator-response objective
4. uncertainty decomposition
5. coherence와 OOD correctness를 구분하는 식별성 경계
6. exact → nonlinear → irregular 3D → transient 실험
7. failure cases와 의료 해석 경계

AAAI-27 공식 author kit의 `aaai2027` style과 reproducibility checklist를
사용한다. 본문은 최대 7페이지이고 이후 최대 2페이지는 references만
허용된다. 2026-08-03 기준 abstract/full-paper/supplement 마감은 이미
지났으므로, 유효한 기존 submission이 없다면 이 원고를 새 AAAI-27
submission이라고 표현하지 않고 다음 cycle 또는 다른 venue용으로 준비한다.

## 10. 실행 우선순위

1. 실패한 D0·G1 결과를 aggregate artifact로 보존 **(완료)**
2. G1b oracle-floor/error-attribution 진단과 equal-budget temporal D0b를
   exploratory로 실행 **(완료)**
3. Prospective G1r을 fresh test에서 실행하고 gate를 냉정하게 판정
   **(완료 · 실패)**
4. Density representation/optimization/data-sufficiency attribution을
   test-free diagnostic으로 실행 **(현재 우선순위)**
5. 완료·검증된 Aneumo base-family-disjoint selective cache에서 train-only
   physical-scaling audit을 실행하고, learned response의 비자명성을 먼저
   판정 **(완료 · velocity만 eligible, pressure 탈락)**
6. 새 prospective exact sanity와 G2가 양수일 때만 irregular 3D backbone과
   transient 학습
7. CMHA status branch는 공식 case map과 positive real-CFD increment가
   확인될 때만 secondary로 복원
