# AURORA 연구 방향

최종 검토일: 2026-08-03 KST

상태: novelty reset · D0 running · learned operator result 없음

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

D0에서 80-step field를 Fourier 4/8/12 mode로 oracle reconstruction한다.
Primary \(K=8\)이 사전 threshold를 통과할 때만 learned one-shot branch를
유지한다. 통과는 모델 성능이 아니라 representation feasibility다.

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

### G2 · paired response

- geometry-disjoint × condition-support-disjoint test
- strong generic probabilistic operator 대비 field energy score 개선
- paired \(\Delta H\) relative L2 개선
- mask별 matched-coverage width가 악화되지 않음
- 5 seeds와 geometry bootstrap 95% CI

Field만 좋아지거나 pair response만 좋아지면 핵심 주장을 축소한다.

### G3 · transient efficiency

- D0 oracle representation 통과
- compute-matched autoregressive baseline 대비 cycle field/peak error와
  latency의 Pareto improvement

아니면 one-shot branch를 버린다.

### G4 · cross-domain generality

Controlled, nonlinear, irregular-3D 세 domain에서 같은 coherence/response
method가 strong baseline을 일관되게 개선해야 한다.

## 8. 가장 큰 위협

1. **Coherence가 자명한 재매개화에 불과할 위험**

   Generic joint probabilistic operator와 비교해 calibration, response,
   sample efficiency 중 실질적 개선을 보여야 한다.

2. **BC density misspecification**

   Gaussian mixture tail이 실제 waveform distribution을 못 담으면 coverage가
   무너진다. Density-only calibration과 posterior predictive check를
   solution metric과 분리한다.

3. **Paired loss가 단순 data augmentation일 위험**

   Cross-geometry pair negative control, pair-distance strata, matched example
   budget을 통해 같은 데이터량 효과와 구분한다.

4. **의료 특화 trick으로 보일 위험**

   비의료 PDE 두 축에서 같은 method와 metric을 먼저 제시한다.

5. **대규모 paired-BC 자산 부재**

   현재 introai9 Aneumo는 1 geometry × 2 BC sample뿐이다. Full release의
   shard·license·manifest를 확인하기 전 100×8 결과를 주장하지 않는다.

## 9. 논문 포지셔닝

작업 제목:

**AURORA: Coherent Neural Operators under Partial and Missing Boundary
Conditions**

논문의 순서는 application이 아니라 method claim에 맞춘다.

1. partial-condition operator family의 모순 문제
2. nested condition–marginal construction
3. paired simulator-response objective
4. uncertainty decomposition
5. exact → nonlinear → irregular 3D → transient 실험
6. failure cases와 의료 해석 경계

AAAI-27 main author kit은 2026-08-03 현재 공식 게시가 확인되지 않았다.
원고는 AAAI-26의 7-page two-column 구조를 임시 기준으로 관리하고,
AAAI-27 kit이 공개되면 style만 교체한다.

## 10. 실행 우선순위

1. D0 작업을 끝까지 모니터링하고 frozen threshold로 판정
2. exact controlled PDE의 G1 구현·5-seed 실행
3. Hugging Face full Aneumo의 shard 크기와 subset 가능성을 metadata-only로
   감사
4. paired-BC 자산 확보 전에는 nonlinear public PDE에서 C1/C2 pilot
5. G1/G2가 양수일 때만 irregular 3D full backbone과 transient 학습
6. CMHA status branch는 공식 case map과 positive real-CFD increment가
   확인될 때만 secondary로 복원
