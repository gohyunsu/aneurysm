# AURORA 연구 방향

최종 검토일: 2026-08-03 KST

상태: architecture contract + exploratory G1 diagnostic 완료

2026-08-03 CMHA 표 기반 exploratory G1은 real-CFD summary의 incremental
utility를 지지하지 않았다(`ΔAUPRC=-0.0419`, patient-bootstrap 95% CI
`[-0.1083, 0.0066]`). 공식 case map과 second model family가 없는 진단
결과이므로 confirmatory gate는 `unresolved`다. 그동안 C3 risk-aligned
branch는 conditional secondary hypothesis로 낮추고 C1/C2를 우선한다.

## 1. 한 문장 연구 질문

> 환자별 inflow/outflow boundary condition이 관측되지 않은 3D 뇌동맥류
> geometry에서, 하나의 그럴듯한 CFD field가 아니라 **가능한 hemodynamic
> field의 보정된 분포**를 예측하고, 그 분포가 real CFD가 제공하는
> rupture-status 관련 정보를 얼마나 보존하는지 측정할 수 있는가?

이 질문은 기존 아이디어의 큰 틀을 유지한다.

`clinical + morphology + hemodynamics → rupture-status stratification`

다만 “geometry를 GNN에 넣어 WSS/OSI를 만든다”는 중간 단계를 근본적으로
바꾼다. geometry와 BC가 주어져야 Navier–Stokes 해가 정해진다. BC가 없는
geometry-only deployment에서 deterministic field를 만들면, 모델은 관측되지
않은 생리조건을 암묵적으로 평균 내거나 훈련 데이터의 조건을 복제할 뿐이다.

## 2. 냉정한 진단

### 2.1 기존 방향이 논문 중심축이 될 수 없는 이유

1. **입력-배포 불일치**

   In-PI-MGN은 현재 velocity, acceleration, inlet context를 입력으로 다음
   timestep을 예측한다. AneuX surface mesh에는 이 정보가 없다.

2. **방법 novelty 포화**

   MeshGraphNet, masked graph pretraining, multigrid, sparse graph
   transformer, inflow token, physics loss가 이미 선행연구에 등장했다.
   self-attention이나 V-cycle을 추가하는 것은 유효한 ablation이지 독립된
   AAAI contribution이 아니다.

3. **목표 불일치**

   낮은 velocity RMSE가 WSS/OSI hotspot, case-level ordering, downstream
   status discrimination을 보장하지 않는다. 반대로 task에 충분한 surrogate가
   모든 interior node에서 가장 낮은 RMSE를 가질 필요도 없다.

4. **label 정의 문제**

   공개 데이터의 ruptured/unruptured는 과거 상태다. 파열 뒤 geometry와
   flow가 변했을 수 있어 reverse causation이 존재한다. 이를 2년/5년 risk로
   부르면 임상적·인과적 주장이 무너진다.

5. **작은 paired clinical cohort**

   CMHA 약 99 IA만으로 큰 end-to-end multimodal network를 처음부터
   학습하면 성능보다 variance와 leakage를 학습할 가능성이 높다.

### 2.2 버리는 것과 보존하는 것

| 결정 | 내용 |
|---|---|
| 보존 | geometry–hemodynamics–clinical endpoint를 연결한다는 큰 틀 |
| 보존 | real CFD와 surrogate hemodynamics를 같은 downstream task에서 비교 |
| 보존 | 공개 데이터셋의 provenance-aware 통합 |
| 중단 | In-PI-MGN에 모듈을 누적하는 방식의 primary contribution |
| 중단 | geometry-only case에 단일 synthetic WSS/OSI를 사실처럼 부착 |
| 중단 | 50-step RMSE 하나로 모델을 선택 |
| 중단 | 공개 rupture status를 prospective risk로 서술 |

## 3. 제안: AURORA

**AURORA**는 *Aneurysm Uncertainty-aware Risk-aligned Operator for Rapid
Assessment*의 약자다.

```text
surface / sparse volume geometry
        │
        ├─ anatomy-aware multi-scale geometry encoder
        │
observed BC ───────────────┐
missing BC → p(z_bc | geometry, site proxy)
                           │
        ├─ one-shot dual-domain neural operator
        │    ├─ coarse volume u(x,t), p(x,t)
        │    └─ high-resolution wall τ_w(x,t)
        │
        ├─ differentiable TAWSS / OSI / LSA / RRT functionals
        │
clinical + morphology + distributional hemodynamics
        │
calibrated rupture-status score + uncertainty / abstention
```

핵심은 BC를 geometry에서 “맞히는” 것이 아니다. 관측 BC가 있으면 그대로
조건화하고, 없으면 anatomical site와 parent-vessel scale에 맞는 empirical
population prior를 적분한다. 출력은 field sample의 집합이며 평균 field만
보고하지 않는다.

## 4. contribution 가설과 현재 우선순위

### C1. Missing-BC distributional operator

기존 aneurysm surrogate는 BC 또는 초기 flow state를 입력으로 요구하거나
고정 BC 아래 deterministic output을 낸다. AURORA는 입력 가용성에 따라
두 mode를 같은 operator에서 지원한다.

- `observed-BC mode`: \(p(H \mid G, B)\)
- `missing-BC mode`: \(p(H \mid G)=\int p(H\mid G,B)p(B\mid A)\,dB\)

여기서 \(G\)는 geometry, \(B\)는 waveform/flow split, \(A\)는 해부학적
proxy, \(H\)는 hemodynamic field다. functional energy score와 coverage로
분포를 학습·평가한다.

### C2. One-shot dual-domain cycle operator

autoregressive rollout은 작은 one-step bias를 누적한다. AURORA는 cardiac
cycle을 8개 temporal Fourier mode로 압축해 한 번에 계수를 예측한다.

- coarse volume branch: velocity와 pressure의 전역 구조, divergence/flux
- fine wall branch: WSS의 국소 gradient와 hotspot
- cross-consistency: volume velocity gradient에서 계산한 wall shear와 wall
  branch가 일치하도록 제약

full transient tensor를 매 step decode하지 않으므로 메모리와 drift를 줄이고,
TAWSS/OSI를 differentiable하게 복원한다.

### C3. Task-aligned functional sufficiency · conditional secondary

surrogate 선택 기준을 “CFD imitation”에서 “CFD가 downstream task에
제공하는 정보 보존”으로 확장한다.

- real-CFD oracle head의 logit/ranking을 held-out patient 안에서 distill
- TAWSS/OSI/LSA/RRT distribution과 neck/dome hotspot 보존
- `risk-retention`:

\[
\mathrm{RR} =
\frac{M(\mathrm{clinical+morph+surrogate})-M(\mathrm{clinical+morph})}
     {M(\mathrm{clinical+morph+realCFD})-M(\mathrm{clinical+morph})}
\]

\(M\)은 primary metric인 AUPRC다. 분모가 양수라는 G1 gate를 통과할 때만
해석한다. RR이 높아도 absolute utility가 작으면 성공으로 부르지 않는다.
현재 exploratory G1의 분모는 음수이므로 C3를 실험하거나 risk-retention을
보고하지 않는다.

## 5. 무엇이 실제 novelty인가

단일 구성요소는 이미 존재한다.

- probabilistic neural operator
- physics-aware transformer
- aneurysm CFD surrogate
- clinical+morphology+hemodynamics fusion

따라서 novelty 주장은 조합 자체가 아니라 다음 문제 설정과 검증에 둔다.

1. aneurysm geometry-only deployment의 **missing-BC non-identifiability**를
   명시적 distributional operator로 정의
2. 동일 geometry/다중 BC 데이터로 aleatoric BC sensitivity를 학습하고
   geometry OOD와 BC OOD를 분리 평가
3. real CFD의 downstream incremental information을 surrogate가 얼마나
   보존하는지 field·functional·decision 세 층에서 동시에 측정

2026-07 공개 arXiv 경쟁작이 geometry-conditioned PINN과 multimodal
rupture-status fusion을 제안했으므로, “physics-informed multimodal
aneurysm prediction”은 우리 novelty가 아니다.

## 6. 성공·실패의 사전 정의

### 성공으로 볼 최소 조건

- G1: real CFD가 clinical+morphology 대비 positive incremental AUPRC를
  patient-bootstrap 95% CI에서 보인다.
- held-out geometry × held-out BC에서 deterministic baseline보다
  distributional score와 coverage가 개선된다.
- surrogate functionals가 real CFD의 case ranking과 hotspot을 보존한다.
- direct geometry-to-status, deterministic operator, late fusion보다
  AURORA가 calibration을 해치지 않으면서 일관된 incremental utility를 낸다.
- missing-BC uncertainty가 실제 BC-induced error와 양의 상관을 보인다.

### 방향을 축소하거나 중단할 조건

- real CFD가 morphology 이후 정보를 추가하지 못함 → risk-aligned branch를
  내리고 missing-BC operator 논문으로 축소
- CMHA raw CFD field가 case와 안전하게 매핑되지 않음 → patient field
  fine-tuning 주장을 제거하고 summary-only validation으로 변경
- uncertainty가 miscalibrated이거나 geometry OOD를 감지하지 못함 →
  deployment claim 제거
- direct geometry model이 동일 성능이고 surrogate field가 기능적으로
  무의미함 → hemodynamic interpretability 주장을 철회
- AneuX와 CMHA의 label/site shift가 통제되지 않음 → external test를
  descriptive stress test로만 보고

## 7. 논문 포지셔닝

### 작업 제목

**AURORA: Boundary-Condition Marginalized Neural Operators for
Task-Aligned Intracranial Aneurysm Hemodynamics**

### 논문이 답해야 할 세 질문

1. Does modeling missing BCs as a distribution improve calibrated field
   prediction under geometry and inflow shift?
2. Does one-shot dual-domain decoding preserve wall functionals better than
   autoregressive full-field surrogates at comparable compute?
3. Do surrogate hemodynamics retain the incremental information of real CFD
   for cross-sectional rupture-status stratification?

### 예상 본문 구성

1. Introduction: missing-BC contradiction와 field/downstream gap
2. Related work: aneurysm CFD, operator learning, uncertainty, risk models
3. Method: conditional field distribution, dual-domain decoder, sufficiency
4. Experimental design: three axes of shift와 nested clinical evaluation
5. Results: field → functionals → downstream → calibration → efficiency
6. Limitations: status≠risk, CFD≠truth, small paired cohort, domain shift
7. Conclusion: rapid research surrogate, not clinical decision system

## 8. 현실적인 진행 순서

1. CMHA 공식 case map·feature provenance를 해결하고 second model family로
   confirmatory G1 여부를 결정
2. 그와 병렬로 동일 geometry/다중 BC가 있는 Aneumo subset의 C1
   missing-BC pilot을 우선
3. deterministic operator와 probabilistic wrapper를 geometry/BC OOD에서 비교
4. temporal basis decoder를 selected AneuG-Flow/BenchAnXplore에 검증
5. G1이 양수일 때만 CMHA task alignment와 risk-retention을 재개
6. C1/C2가 독립적으로 통과하면 status branch 없이 operator paper로 진행

가장 비싼 full-scale 학습은 1–3단계가 성공한 뒤 시작한다.
