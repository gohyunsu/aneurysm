# AURORA 연구 방향

최종 검토일: 2026-08-09 KST

상태: ISBI 2027 target locked · not submission-ready · G1/G1r failed
preserved · G1s pass · N0 failed preserved · N0r pass · N1c failed unchanged ·
post-N1c audits completed · ISBI V0 passed development-only · V1 backbone and
aggregation completed/failed 5/7 · V1a fixed-checkpoint attribution completed with training underfit · V1b/V1c/V1d asset gates passed · V1e failed 6/9 · M0 execution-incomplete/no scientific verdict · prior identity inactive · cross-protocol 4D-flow I0a passed 14/14 asset-only · I0b execution-incomplete before asset access/no scientific verdict/no rerun · 4D-flow branch closed · method unselected · submission blocked

## 0-A. 최근 candidate · protocol-indexed posterior prediction · closed

검증하려던 질문은 다음이었다.

> 한 intracranial 4D-flow MRI acquisition에서 얻은 posterior가 같은
> controlled phantom flow의 다른 resolution, acceleration 또는 VENC
> acquisition을 measurement space에서 예측할 수 있는가?

핵심은 고해상도 CFD를 MRI의 정답으로 놓는 super-resolution이 아니다.
Latent continuous velocity field (u)와 acquisition protocol
\(\alpha\)의 measurement operator \(A_\alpha\)를 분리하고,
\(p(u\mid y_\alpha,\alpha)\)를 다른 protocol \(\beta\)로 pushforward한
\(p(y_\beta\mid y_\alpha,\alpha,\beta)\)를 실제 held-out acquisition으로
검사하는 **cross-acquisition posterior predictive check**가 후보 estimand다.

이 방향도 아직 contribution이 아니다. 4DFlowNet·SRflow·FlowMRI-Net·VAST,
4D-flow velocity UQ와 2026 distributional SR가 reconstruction, denoising,
physics, domain shift와 uncertainty를 이미 다룬다. 공개 candidate asset은
소수 in-vitro phantom이고 반복 acquisition이 제한적이므로 posterior
calibration이 통계적으로 식별 가능한지도 미정이다. 따라서 method·이름·GNN
여부를 먼저 정하지 않는다.

`configs/flow_mri_protocol_i0a_asset_audit.json`의 I0a는 이미 확인한 record,
central directory, nine descriptors와 eight primary headers를 discovery로
공개하고, field payload를 전혀 읽지 않는 14-check asset audit이다. Exact
source `f7b4e024d69d43cf042f4163342b4d993386f441`에서 14/14를 통과했다.
ZIP32/ZIP64 entry 174/76개, descriptor 9개, primary header 8개를 검증했고
processed RAW/REC read는 0이었다. 이 결과는
`results/flow_mri_protocol_i0a_asset_audit_20260808.json`에 고정한다. Pass는
selective staging과 learned-method-free I0b의 별도 등록만 허용한다.

I0b는 `configs/flow_mri_protocol_i0b_task_adequacy.json`에 field read 전에
고정했다. 2021 release는 little-endian float32와 official MATLAB의
X-fastest→Y→Z→T 순서로 27 RAW만 decode하고, target field를 이용한 registration
없이 common 1.5-grid에서 support Dice·centroid, temporal correlation, vector
cosine, resolution/acceleration discrepancy와 protocol variance를 검사한다.
Registration 전에 공식 README/reader를 읽은 사실을 discovery로 공개한다.

별도로 Zenodo `17183575`의 23.2 GB/33-scan intervention release를 찾았다.
등록 전에 official record, 세 ZIP64 central directory와 33 primary PAR header를
확인했으며 field/REC는 보지 않았다. 실제 단위는 33 patients가 아니라 5 base
geometry, 22 physical model/device state, 8 multi-VENC state, 2 pump-off acquisition,
15 unique device condition이고 source patient anatomy는 2개다. 기존 Zenodo
`14981710`과의 case-level overlap도 unresolved이므로 독립 cohort로 합치지
않는다. I0b가 모두 통과해도 method-free I0c PAR/REC decoder·noise audit만
등록할 수 있도록 했고, 실패하면 threshold나 registration을 고쳐 반복하지
않도록 고정했다.

**Outcome · 2026-08-09.** Exact source `0ebdb344…`, config SHA `e19a1194…`의
one-shot CPU/PBS run은 wrapper가 기존 read-only `h5py==3.12.1` dependency
layer를 누락해 import 단계에서 exit 1이었다. 2021 archive request/RAW/field
read, 2025 PAR/REC read, cache와
metric/result 생성은 모두 0이다. 따라서 gate는 미평가이고 task adequacy를
지지하거나 반박하는 scientific verdict가 아니다. 등록된 no-rerun rule을
그대로 적용해 dependency를 보충한 I0b 재실행과 I0c를 열지 않는다. 이
4D-flow branch는 method를 정하지 않은 채 닫고, 다음 단계는 새 problem-level
candidate의 독립 audit이다.

## 0-B. 제출 목표와 보존된 이전 scope

목표 venue는 IEEE ISBI 2027 four-page regular paper이며 공식 마감은
2026-10-26이다. ISBI는 physical/statistical modelling, reconstruction,
uncertainty quantification과 medical applications를 포함하지만, 현재
negative nonlinear evidence와 계획만 있는 3D GNN을 제출 근거로 보지
않는다.

아래 Aneumo velocity-only 3D 경로는 실패 provenance와 재현 계약으로
보존한다. N1c, V1e와 M0 outcome 뒤에는 더 이상 active submission identity가
아니며 local repair나 이름 변경으로 되살리지 않는다. 4D-flow candidate도
I0b execution-incomplete 뒤 환경 repair로 되살리지 않는다. 새 candidate는
독립적인 positive evidence가 생기기 전에는 제출 identity가 아니다.

3D로 바로 넘어가지 않는다. `configs/aneumo_isbi_v0.json`은 64-case cache의
SHA, 32-family 20/6/6 split, 8개 scalar mass-flow mapping, velocity tensor
metadata와 이미 공개된 train-only physical-scaling aggregate를 8개
all-check gate로 고정한다. V0 자체는 field array를 읽지 않는다. Missing
law는 8개 조건의 discrete-uniform **design law**이며 patient physiology가
아니다. 기존 compact cache에는 boundary marker와 surface normal이 없으므로 WSS/OSI·mass flux는
추가하지 않는다. 통과해도 V1 implementation smoke만 열리고 method,
outer test와 논문 claim은 열리지 않는다.

Exact public source `0589070`의 V0는 8/8 check를 통과했다. Registered cache
SHA와 64 case/32 family/8 condition/4,096 node metadata가 일치했고, 기존
train-only velocity scaling CI lower 0.20013이 0.15 기준을 유지했다. 새
field array 및 validation/test field read는 없었다. 따라서 V1의 bounded
64-case implementation smoke 등록만 허용한다. 이 수치를 모델 성능이나
contribution으로 세지 않는다.

V1은 `configs/aneumo_isbi_v1.json`에 결과 전에 고정했다. 40 train/12
validation case만 읽고 12 test case의 field는 건드리지 않는다. q-PointNet,
kNN-MGN, DeltaPhi graph와 frame-free anchor-token equivariant operator를
동일 1,024-node subset, 세 seed, 3,000 step과 train-only scalar velocity
normalization으로 비교한다. Anchor-token 모델은 local/anchor displacement의
scalar coefficient로 velocity vector를 복원해 회전 equivariance를 갖지만,
이는 engineering candidate이지 novelty가 아니다. Selector가 다른 baseline을
고르면 그대로 따른다. V1은 V2나 submission을 허용하지 않는다.

결과 전에 집계 의미도 고정한다. Matching-q point prediction은 같은 family의
세 seed 평균이고, missing-design-law predictive distribution은 세 seed와
8개 등록 q의 Cartesian product인 24개 component다. Ensemble metric은
selector에 쓰지 않고 uncertainty separation claim도 지지하지 않는다. 모든
checkpoint를 validation에서 replay해 저장 metric과 (10^{-5}) 안에서
일치시킨다. Same-case power 1.075 control은 true validation q=0.0025 field를
anchor로 쓰므로 response-only oracle이며 reconstruction baseline, selector,
gate가 아니다. Metric 집계는 case가 아니라 base-family를 먼저 평균한다.

첫 exact source `b8ce721` model contract는 8/9였고 parameter count
`[357603,374979,384582,422114]`의 relative range 15.283%가 frozen 15%를
0.283%p 넘었다. Learned metric과 cache field read 전이므로 threshold를
완화하지 않고 최소 model인 q-PointNet residual block만 16→17로 수정한다.
새 exact-source contract 전체가 통과하기 전 학습을 제출하지 않는다.
Correction source `a8b0042`는 model contract 9/9와 전체 168/168을
dependency-complete container에서 통과했다. 이후 CUDA bookkeeping과
aggregate observability만 결과 전에 별도 ops commit으로 고쳤고 scientific
config SHA는 유지했다.

**V1 outcome · 2026-08-08.** Exact task source `a0479fb`의 12 task는 모두
exit 0이었고 exact source/config, no-test-read, checkpoint SHA와 validation
replay를 통과했다. Aggregate source `78dca92`의 판정은 5/7 fail이다.
Lexicographic selector는 q-PointNet을 골랐지만 worst-seed full-q/response
relative L2가 `1.03459/1.00354`로 frozen `0.35/0.50`을 크게 넘었다. kNN-MGN,
DeltaPhi graph와 anchor-token도 seed-mean full/response L2가 모두 약 1이라
architecture superiority가 없다. True validation anchor를 쓰는 비배포용
response-only oracle은 `0.22794`였지만 selector/gate에 사용하지 않는다.
현재 3D backbone branch를 중단하며 hidden size, k, step, seed, loss와
threshold를 국소 수정하지 않는다. Public aggregate는
`results/aneumo_isbi_v1_20260808.json`이다.

**V1a outcome · 2026-08-08.** Exact source `3a0d27f`의 기존 12개
checkpoint replay는 exit 0, test-read false로 완료됐다. 네 family의
seed-mean train full-q L2가 `0.76939--0.95647`, validation이
`1.01369--1.02469`이고, train norm ratio/cosine도 각각
`0.35004--0.66921`/`0.29710--0.61342`다. 따라서 current failure는
family-disjoint generalization만이 아니라 training fit과 vector
representation collapse에서 이미 발생한다. Validation condition-energy
fraction `0.15748`, same-case mean oracle `0.56843`, true-anchor response
oracle `0.22794`는 condition response가 비자명하지만 geometry-only field
mapping이 입증되지 않았음을 보여준다. 이는 threshold-free diagnostic이지
causal decomposition, method selection 또는 gate가 아니다. Public aggregate는
`results/aneumo_isbi_v1_attribution_20260808.json`이다. Current geometry-only
branch를 폐기하고 learned method 전에 새 task/data identity를 감사한다.

**Boundary-asset discovery, V1b pass and V1c registration · 2026-08-08.** Official
pinned ZIP64 archive 1/case 1에는 compact cache에서 제외됐던 `.msh`, `.stl`,
volume `.vtu`, `inlet/outlet/wall.vtp`, poly connectivity와 `U/p` array가
존재한다. 이미 본 이 한 archive/header는 prospective evidence가 아니다.
Exact source `fb1c21a`의 V1b는 full 20-archive/64-case member contract와
train representative 60 VTP payload를 range/CRC로 감사해 8/8을 통과했다.
384 required member가 있었고 validation/test payload와 field array는 읽지
않았다. Public aggregate는
`results/aneumo_isbi_v1b_boundary_asset_audit_20260808.json`이다.

V1b가 허용한 범위에서 V1c를 geometry array decode 전에 prospective하게
고정했다. Exact source `84fc244`의 V1c는 train family별 한 representative의
세 patch×세 flow, 총 180 VTP에서 `Points/connectivity/offsets`만 decode해
8/8을 통과했다. Boundary geometry는 60/60 patch에서 exact q-invariant였고
minimum polygon-valid fraction은 1.0이었다. `U/p/TimeValue`, validation/test
payload, model/checkpoint와 학습은 접근하지 않았다. Public aggregate는
`results/aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json`이다.

V1c pass가 허용한 범위에서 V1d를 validation geometry payload decode 전에
고정했다. Exact source `369317a`의 V1d는 train 40·validation 12·test 0 case의
boundary 468개와 reference-volume 52개 payload에서 geometry arrays만 decode해
9/9을 통과했다. 156/156 patch의 q-invariance, minimum polygon-valid fraction
1.0, 52/52 case의 exact boundary-volume point correspondence를 확인했다.
Public aggregate는
`results/aneumo_isbi_v1d_development_geometry_cache_20260808.json`이다. 이는
physical boundary identity를 포함하는 development data contract가 일관됨을
보인 asset evidence이지 model evidence가 아니다.

이 pass 범위에서 어떤 training/checkpoint보다 먼저 V1e를 고정했다. V1e는
fully observed scalar inflow의 velocity field를 먼저 학습할 수 있는지 묻는
known-condition qualification이다. Exact `c62838b`의 6 GPU task는 모두 exit
0이었고, Boundary Perceiver와 geometry-only control은 같은 740,099 parameter와
320 source token을 사용했다. Boundary는 validation full-q와 response에서
3/3 seed로 control보다 좋았고 seed-mean 상대 개선도 `10.94%/6.41%`였다.
그러나 worst-seed train full-q `0.77221`, validation full-q `0.87796`,
response `0.94918`이 frozen `0.25/0.35/0.50`을 모두 넘어서 6/9로
실패했다. 이는 boundary asset의 incremental utility와 absolute operator
learnability를 분리한다. 전자는 양수지만 후자는 실패했으므로 current Aneumo
3D learning line을 local repair 없이 중단한다. Scalar missing-inflow protocol,
test, V2, multicomponent partial claim, novelty와 submission은 열지 않는다.
Known-BC encoding, boundary token, Perceiver 또는 surface GNN 자체는
contribution이 아니다. Public aggregate는
`results/aneumo_isbi_v1e_known_condition_baseline_20260808.json`이다.

## 1. 현재 판정

기존 v1을 “missing-BC probabilistic neural operator + Fourier cycle decoder”로
제출하면 독립 novelty가 부족하다.

- varying BC 밖 neural operator의 비식별성은 ICLR 2026 연구가 직접
  정식화했다.
- function-space diffusion/flow-matching/probabilistic operator가 이미 있다.
- marginal/conditional consistency는 neural process 문헌에 선행한다.
- aneurysm transient inflow-aware physics GNN은 npj Digital Medicine 2026에
  발표됐다.
- Fourier one-shot decoding은 architecture choice이지 새 원리가 아니다.

따라서 현재는 **accept-ready가 아니다**. N1c가 구조적 route consistency는
보였지만 strong baseline보다 field distribution·acquisition regret를
개선하지 못했고 paired objective도 DeltaPhi-style control보다 약했다.
GNN, attention, uncertainty, physics loss를 조합한 것만으로 제출하지
않는다.

실패 원인 분해인
`configs/nonlinear_pde_n1c_attribution.json`의 N1c-a도 완료됐다. 같은
open test와 frozen checkpoint만 읽은 threshold-free diagnostic에서 joint
BC density가 모든 mask에서 independent heads를 0/5 seed로 이겼고,
functional energy의 mean oracle-substitution difference는 density가
operator보다 missing에서 13.0배, sparse-2에서 5.81배 컸다. Acquisition은
64×128 sample에서도 ACFlow보다 1/5 seed에서만 좋았고 sparse-2는 두
방법 모두 oracle과 같아 판별력이 없었다. AURORA의 route compatibility는
수치적으로 회복됐지만 independent heads보다 true-oracle worst-route
regret가 낮은 seed는 3/5뿐이었다. 따라서 N1c 실패, 닫힌 3D와
`accept-ready가 아니다`라는 판정은 바뀌지 않는다.

그 결과를 본 뒤 유리한 목적함수나 task를 고르는 것을 막기 위해 다음 두
development audit을 결과 전에 분리해 고정한 뒤 exact `337c75e`에서
완료했다. Density audit은
`configs/nonlinear_pde_n1_density_objective_audit.json`, task audit은
`configs/nonlinear_pde_n1_decision_task_audit.json`이 실행 계약이다.
Full-joint NLL은 N1c raw objective보다 missing/sparse-2/partial-4 excess
NLL을 27.2%/23.8%/20.3% 줄였고 모두 5/5 seed 방향이 같았다. 반면
단순 normalization은 일관된 이득이 없고 registered composite 개선은
1.5–2.5%였다. True-law/simulator task에서는 missing acquisition의 VoI가
두 replicate에서 0.15587/0.15558이고 winner agreement가 0.9271이었다.
Sparse-2는 VoI가 0.18517/0.18554로 양수지만 component 6이 두 replicate의
96/96 context에서 고정 winner였다. 따라서 missing은 향후 decision
endpoint 후보로 남기고 sparse-2 adaptive-policy 비교는 제거한다. 이
결과는 success gate나 method selection이 아니며 N1c relabel·N1d/3D
권한도 없다.

## 2. 새 한 문장 연구 질문

> 하나의 PDE surrogate가 full, partial, missing physical condition을 모두
> 받을 때, joint-law compatibility를 지키면서도 정확한 mask conditional을
> 보존하고 그 차이를 solution-functional decision risk의 감소로 연결할
> 수 있는가?

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

### C2. Paired simulator-response supervision · ablation only

같은 geometry에서 BC만 바꾼 두 simulation을 pair로 사용한다.

\[
\mathcal L_\Delta =
\|[\hat H(G,B_j)-\hat H(G,B_i)]-[H(G,B_j)-H(G,B_i)]\|.
\]

이는 geometry variation이 큰 absolute field loss 안에서 BC sensitivity가
묻히는지를 검사한다. N1c에서 pair-zero보다 pooled context 기준으로는
좋았지만 seed 방향은 3/5였고 DeltaPhi-style residual의 seed-mean
paired-response L2 0.01221보다 나쁜 0.01331이었다. 따라서 독립
contribution이 아니라 ablation이며, 논문은 이를 causal effect가 아닌
simulator intervention response라고 한정한다.

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

따라서 3D **target specification**은 GNN을 포함하지만 순수 GNN이 아니다.
현재 실행된 N1은 MLP operator다. Planned backbone은 강한 구현 선택이며
novelty의 중심이 아니다.

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

구체적으로 6,144 sample을 맞춘 192×32, 768×8, 3,072×2를 비교하고,
768 geometry 고정 및 8 condition 고정 scaling axis를 추가한다. Empirical
NLL은 sampled-validation 선택과 analytic-population 선택을 모두 두어
finite training data와 checkpoint noise를 분리한다. 세 diagnostic seed는
G1/G1r과 겹치지 않으며 이 post-result 분석에는 통과 기준이 없다.

DA1은 exact commit `cf675af`의 A6000 run에서 30개 학습 task를 exit 0으로
완료했다. Analytic population NLL은 최악 seed의 density-only mean error를
0.00495까지 낮춰 현 Gaussian family·MLP·optimizer가 정답 분포를 표현할
수 있음을 보였다. 반면 empirical NLL은 population-validation 선택에서
최악 0.04401, sampled-validation 선택에서 0.04855였다. Checkpoint 선택법
차이의 seed 평균은 작았으므로 주 병목은 selection보다 finite empirical
condition information이다.

동일 6,144 boundary record에서 192×32, 768×8, 3,072×2의 seed-평균
density-only error는 각각 0.05011, 0.03612, 0.04715였다. 세 seed뿐인
exploratory 결과이므로 768×8을 보편적 optimum이라고 주장하지 않는다.
다만 geometry를 768로 고정하면 condition 2→8→32에서
0.09244→0.03612→0.02744, condition을 8로 고정하면 geometry
192→768→3,072에서 0.09457→0.03612→0.02808로 개선됐다. Geometry
coverage와 repeated-condition information이 모두 필요하다는 진단은
분명하다.

따라서 다음 development branch는 mean/covariance를 결합 NLL 하나로
추정하지 않고, geometry-grouped mean regression과 pairwise-difference
U-statistic covariance target을 분리한 shrinkage estimator를 비교한다.
Estimator 선택은 DA1 analysis seed를 재사용하지 않는 development split에서
끝내고, 선택 뒤 별도 fresh exact-sanity protocol을 등록한다. 단순히
Gaussian을 flow로 교체하거나 threshold를 완화하지 않는다.

이 비교는 DA2로 실행 가능하게 고정했다. 세 새 development seed, 768×8과
3,072×8 data cell, empirical NLL 및 grouped covariance shrinkage
0/0.25/0.50을 사용한다. 모든 후보는 같은 Gaussian network와
sampled-validation checkpoint를 사용한다. Estimator는 기존 G1r과 같은
768×8에서 선택하고 3,072×8은 data-sufficiency control로만 사용한다.
따라서 estimator 변화와 4배 geometry 증가를 같은 효과로 세지 않는다.
U-statistic covariance나
shrinkage 자체는 고전적 estimator이므로 contribution 후보가 아니다.
독립 novelty는 이후 fresh gate와 nonlinear/irregular-3D에서 coherent
condition pushforward와 paired response가 strong probabilistic operator를
실제로 이길 때만 성립한다.

DA2는 exact commit `18dbfcd`의 24-task A6000 run에서 완료됐다. 고정
selection rule은 grouped shrinkage 0.50을 골랐지만, 768×8에서 empirical
NLL 대비 seed-평균 density-only error는 0.05444→0.05431로 0.23%만
개선됐다. 세 seed 중 둘에서만 좋아졌고 하나에서는 나빠졌으며 analytic
population excess NLL은 0.00290→0.00316으로 악화됐다. 이는 material하고
seed-robust한 estimator 개선이 아니다. Grouped unbiased moment는 평균
0.06770으로 더 나빴다.

반면 data-sufficiency control의 3,072×8 empirical NLL은 평균 0.02575,
최악 0.02706으로 모든 development seed에서 기존 0.05 기준보다 충분히
낮았다. 따라서 grouped/shrinkage를 method나 novelty로 승격하지 않는다.
다음 prospective exact sanity는 원래 empirical NLL estimator를 유지하고
3,072×8 data budget만 사전에 고정해 data adequacy를 검증한다. 이 pass가
성립해도 data quantity는 contribution이 아니며, 그 뒤 nonlinear/3D에서
핵심 mechanism의 독립적 이득을 입증해야 한다.

이 후속 sanity는 `G1s`다. `configs/controlled_pde_g1s.json`은 실행 전에
다음을 동결한다.

- G1/G1r/DA1/DA2와 겹치지 않는 5개 새 seed
- 기존 empirical NLL density estimator와 3,072×8 training budget
- G1r과 동일한 model family, optimizer, validation-only checkpoint,
  mask, analytic/quadrature/projective estimator와 모든 threshold
- G1r과 동일한 192 validation/192 fresh-test geometry
- 5개 seed 중 최악값 판정 및 G1/G1r non-relabeling

따라서 seed와 training geometry 수 외에는 G1r의 pipeline을 바꾸지 않는다.
G1s pass는 nonlinear regular-grid 실험을 시작할 최소 pipeline
권한만 주며, data scaling이나 exact toy 성능을 contribution으로 만들지
않는다. G1s가 실패하면 architecture를 더 화려하게 만들거나 3D로 우회하지
않고 exact-domain density estimation을 다시 중단·재검토한다.

G1s는 exact public commit `b0e555a`에서 fresh 5-seed A6000 run을
exit 0으로 완료했고 모든 frozen check를 통과했다.

| frozen check | 최악 seed/route | 기준 |
|---|---:|---:|
| density-only mean | 0.02863 | 0.05 |
| density-only coverage error | 0.00836 | 0.03 |
| end-to-end quadrature mean | 0.02977 | 0.05 |
| sampled coverage error | 0.01294 | 0.03 |
| full-BC operator | 0.00410 | 0.03 |
| projective excess CI95 upper | 0.000674 | 0.01 |
| analytic nesting residual | \(7.45\times10^{-9}\) | \(10^{-6}\) |

Direct masked Gaussian과의 15개 seed×mask descriptive cell에서는 energy,
mean error, coverage error가 모두 낮았지만 이 baseline만으로 superiority를
주장하지 않는다. LANO, NOP와 compute-matched generic probabilistic
operator를 포함하는 nonlinear comparison이 다음 falsification 단계다.
G1/G1r은 historical failed evidence로 그대로 남는다.

### N0 → N1 · 비선형 evidence ladder

학습부터 시작하지 않는다. `configs/nonlinear_pde_n0.json`은
\(-\nabla\cdot(a_G\nabla u)+\lambda_Gu^3=f_G\)를 33×33 grid와 nested
65×65 reference에서 푸는 numerical/problem-design gate다. 두 sine mode를
네 edge에 배치한 8-component BC와 context-conditioned 2-component GMM을
사용한다. 세 audit seed에서 다음을 모두 통과해야 N1을 등록한다.

- normalized solver residual과 coarse/reference relative \(L_2\)
- 같은 context·BC의 linear solution 대비 material nonlinear departure
- 여덟 BC component 각각의 paired response와 response effective rank
- domain mean, hotspot, smooth maximum, right flux의 winner diversity
- GMM을 \(\{0,2,5,7\}\)에 직접 condition한 moment와
  \(\{0,2\}\rightarrow\{5,7\}\) 순차 condition한 moment의 일치

N0 통과는 solver와 문제가 N1을 시험할 만큼 비자명하다는 뜻뿐이다.
Learned performance, AURORA novelty, 3D 진행 권한이 아니다.

Exact `0ead687`의 A6000 run은 9개 check 중 8개를 통과했지만 실패했다.
세 seed의 nonlinear-departure 중앙값은 0.02319, 0.02365, 0.00727이고,
frozen worst-seed 기준은 0.01이었다. 마지막 seed를 제외하거나 threshold를
낮추지 않는다. 이 실패는 이후 N0r 결과와 무관하게 보존한다.

사후 code audit에서는 context-major flatten 뒤 앞 12개 reference case를
자른 결과, 각 seed의 nonlinear statistic이 context 0의 12개 condition만
반영한다는 사실을 찾았다. Pair statistic도 앞 네 context에 한정된다.
이는 실패를 무효화하지 않는다. 먼저 threshold 없는 N0a에서 모든 context의
departure 분포를 정량화하고, 그 뒤에만 새로운 seed와 context-stratified
case selection, 기존 PDE·threshold를 고정한 N0r를 등록한다. N0r 통과 전에는
학습 실험을 열지 않는다.

N0a 실행 계약은 `configs/nonlinear_pde_n0_attribution.json`이다. 기존 세
seed의 288개 context-condition 조합을 전부 사용해 원래 contiguous
statistic, 12-context stratified statistic, 모든 context의 median 분포를
비교한다. Nonlinearity coefficient와 solution norm의 association도
attribution용으로만 계산한다. 성공 기준이 없고 N0r seed·threshold
selection에도 사용할 수 없으므로, 유리한 subset을 골라 gate를 우회하지
못한다.

Exact `749f596`의 N0a에서 failed seed의 contiguous 12-case median은
0.00774였지만 12-context stratified median은 0.01221, 전체 288-case
median은 0.01828이었다. 다른 두 seed의 stratified median도
0.01624/0.01811이었다. 반면 former 0.01 reference를 넘는 context median은
18–19/24뿐이다. 따라서 **single-context slice의 대표성 문제**는
지지하지만 **모든 context의 강한 비선형성**은 지지하지 않는다. N0는
failed로 유지한다. N0r는 fresh seed와 24-context coverage를 결과 전에
고정하고 기존 scientific threshold를 유지한다.

N0r의 exact contract는 N0a outcome 전 commit `1a68053`에서 고정됐다.
Fresh seed는 `[62080321, 62080322, 62080323]`이고, reference 24 case는
24 context를 각각 한 번, paired 48 case는 각각 두 번 포함한다. PDE,
BC density, solver, functionals, eight threshold, all-check/worst-seed rule은
N0와 같다. N0a 결과가 유리하거나 불리해도 이 계약을 수정하지 않는다.
Exact `37d31a8`의 fresh A6000 run은 9개 check를 모두 통과했다. 최악
seed 기준 nonlinear departure 0.01933, discretization error 0.00375,
8-component response minimum 0.17484, effective rank 7.06667,
conditioning-route residual \(8.94\times10^{-8}\)였다. 이 결과는 N1
strong-baseline protocol의 **등록만** 허용한다. N0 relabel, learned
superiority, method novelty, irregular-3D 실행 권한은 열지 않는다.

N1에서 검증한 후보 정체성은 active acquisition 자체가 아니라
**conditioning inconsistency가 solution-functional Bayes decision과 다음
BC 측정 선택에 만드는 regret**이었다. N1c-a에서 AURORA의 route
compatibility는 확인됐지만 independent heads 대비 true-oracle
worst-route regret 우위가 3/5 seed에 그쳤고, baseline의 route별 candidate
risk 변화도 selected component를 거의 바꾸지 않았다. 따라서 이 정체성은
현재 nonlinear benchmark에서 **unsupported**이며 그대로 논문 제목이나
contribution으로 올리지 않는다.

향후 되살릴 수 있는 더 좁은 가설은 *coherence–conditional-accuracy
trade-off를 solution-functional risk에 맞춰 해소할 수 있는가*이다. 그러나
mask-conditional composite likelihood는 고전적 estimation control이고,
compatibility/path consistency와 decision-focused learning도 선행연구가
있다. 완료된 validation-only audit에서 full-joint MLE는 conditional
excess를 20.3–27.2% 낮췄으므로 현재의 accuracy tax가 구조적으로 불가피한
것은 아니다. 그러나 이는 표준 likelihood control이지 새 방법이 아니다.
Method-independent audit은 missing task의 nonzero VoI와 안정성을
확인했지만 sparse-2가 fixed-winner라 adaptive benchmark가 아님을
확인했다. 따라서 missing endpoint에서만 남은 gap을 겨냥하는
operator-specific mechanism을 별도 결과 전 protocol로 설계해야 한다고
보았으나, 그 첫 one-shot falsification인 M0는 2/3 seed만 완료돼 과학적
판정 없이 닫혔다. 선택된 method나 fresh re-entry는 없다.

### Candidate-measurement–solution joint pullback · M0

선행연구와 구분되는 가장 좁은 남은 질문은 “solution distribution이
맞는가?”가 아니라 **각 후보 측정 \(B_j\)와 그 뒤 solution functional
\(Z=\Psi(H)\)의 joint law가 맞는가?**이다. Solution marginal
\(p(Z\mid G)\)과 candidate marginal \(p(B_j\mid G)\)이 각각 같아도 둘의
의존성이 다르면 \(B_j\)를 관측한 뒤의 Bayes action과 VoI는 달라진다.
따라서 solution-marginal proper score만으로 one-component acquisition을
식별할 수 없다.

M0의 proposed objective는 하나의 joint BC density \(q_\theta(B\mid G)\)와
frozen full-condition operator \(\hat F\)를 유지한 채

\[
T_j(G,B)=
\left(
\operatorname{std}(B_j),
\operatorname{std}\{\Psi(\hat F(G,B))\}
\right)
\]

의 eight candidate-wise joint pushforward에 characteristic product-kernel
score를 적용한다. Full-joint log score의 양의 weight를 유지하므로 exact
operator와 population limit에서 true BC joint law가 unique optimum이라는
properness를 잃지 않는다. Acquisition head, mask별 density head 또는
별도 imputer는 추가하지 않으며 측정 뒤 posterior는 같은 joint density의
analytic conditional이다.

이론 계약은 세 문장으로 제한한다.

1. full-joint log score와 characteristic pushforward kernel score의 합은
   exact-operator population setting에서 true joint BC law를 보존한다.
2. 같은 \(B_j\), \(Z\) marginal을 갖더라도 correlated와 independent joint는
   서로 다른 post-measurement Bayes risk를 만들 수 있다.
3. 각 policy loss integrand의 RKHS norm이 \(C\) 이하이면 candidate-risk
   오차는 \(C\,\mathrm{MMD}\), 선택된 component regret는
   \(2C\max_j\mathrm{MMD}_j\)로 제한된다.

Kernel/energy score, probabilistic neural operator, arbitrary conditioning,
active feature acquisition, joint MLE와 generic IPM decision bound는 모두
선행 구성요소다. 독립 novelty 후보는 이들을 나열하는 데 있지 않고,
**candidate measurement–solution joint를 operator를 통해 직접 점수화해
coherent posterior의 finite-sample acquisition sufficiency를 겨냥하는
문제·목적함수·보장**의 결합에 있다. 이 문구도 M0와 별도 fresh strong
baseline 실험이 양수일 때만 contribution으로 승격한다.

Exact contract는
`configs/nonlinear_pde_n1_missing_operator_pullback_m0.json`이다. Missing
mask만 primary로 쓰고 sparse-2는 fixed-winner control로만 남긴다. 세 fresh
development seed에서 full-joint MLE, boundary-kernel compute control,
solution-marginal proper-score control과 proposed joint pullback을 같은
initialization·minibatch·kernel RNG로 비교한다. 3,072×8 training,
384×8 selection-validation, disjoint 192×8 audit-validation, frozen
pair-zero full-condition operator와 true-simulator oracle을 사용한다.

Mechanism gate는 candidate-joint MMD²와 true-oracle acquisition regret가
각각 strongest control보다 5% 이상 개선되고 3/3 seed 방향과 paired
context bootstrap CI upper < 0을 모두 만족해야 한다. 동시에 full-joint
density excess degradation ≤ 5%, solution-marginal MMD² degradation ≤ 1%,
모든 frozen-operator audit L2 ≤ 0.05를 요구한다. 하나라도 실패하면
weight·kernel·mask·seed·threshold를 고치는 local repair 없이 mechanism을
폐기한다. 통과해도 separate five-seed fresh re-entry 설계 자격일 뿐 N1c
relabel, method novelty, N1d 또는 3D 권한은 아니다.

Exact source `89bdc85`의 PBS array `115078`은 3개 seed 중 0과 2만 exit
0이었고 seed 1은 `candidate_risk_matrix`에서 radius-constrained truncated
conditional rejection이 stall해 exit 1이었다. 필수 3-seed aggregate를 만들
수 없으므로 M0는 과학적 pass/fail이 아니라 **execution-incomplete / no
scientific verdict**다. 성공한 두 seed의 metric을 gate 용도로 열거나
선택 집계하지 않았다. 공개 record는
`results/nonlinear_pde_n1_missing_operator_pullback_m0_execution_20260808.json`이다.
One-shot 계약에 따라 sampler repair·rerun·M0r·fresh re-entry를 등록하지
않으며 이 mechanism branch는 inactive다. 따라서 위 novelty 문구는
unsupported hypothesis로만 보존하고 N1c failed, method unselected,
N1d/3D blocked를 유지한다.

새 방법이 정당화된다면 bounded loss에서 posterior TV/KL로 Bayes-regret를
제한하는 분석과, compatible joint model이 실제 oracle functional risk와
acquisition regret를 함께 줄이는 fresh 실험을 결합해야 한다.
LANO, NOP, compute-matched probabilistic operator, generative AFA,
acquisition-conditioned oracle와 NeurIPS-25 NOTS-style posterior-sample
functional acquisition이 필수 비교다. NOTS는 전체 operator input function
query를 고르는 문제이므로 그대로 같은 task는 아니며 adapted control로
명시한다. 이 중 하나라도 빠지면
“active BC”를 contribution으로 주장하지 않는다.

N1의 exact prospective contract는 `configs/nonlinear_pde_n1.json`이다.
5개 confirmatory model seed, geometry-disjoint split, full-covariance
2-GMM, Dirichlet-lifted rank-96 coordinate operator, 모든 baseline,
mask route, decision loss, bootstrap rule과 5% minimum effect를 결과 전에
고정한다. Development seed는 validation-only이며 test 생성·threshold
변경 권한이 없다. N1 pass도 irregular-3D **protocol 등록만** 허용한다.

첫 core development seed는 test를 생성하지 않고 정상 완료됐지만 operator
자격을 얻지 못했다. Joint-density validation NLL은 -4.290이었으나 full-BC
relative L2 0.1739, paired-response relative L2 0.1862였고 best checkpoint가
maximum 1,400 step에 있었다. Density 결과로 operator 실패를 덮지 않는다.
Interior envelope의 최대값 0.0625가 correction과 gradient를 16배 감쇠한
동일 함수 클래스 parameterization임을 확인해 unit-peak로만 재척도화했다.
두 번째 development seed에서는 full-BC/paired-response L2가
0.05771/0.05729로 크게 줄었지만 unchanged 0.05 기준을 넘었고 best
checkpoint도 다시 maximum 1,400 step이었다. “거의 통과”로 해석하지 않는다.

`configs/nonlinear_pde_n1_optimization_attribution.json`은 새 development
seed에서 raw/scale-normalized loss × 1,400/2,800 step의 2×2 요인만
validation-only로 비교한다. Success threshold가 없고 test/N1/3D 권한도
없다. Lowest validation objective를 선택하되 1% 이내면 짧은 horizon을
고른다. Exact `eebcd91`의 A6000 run은 test를 생성하지 않고 exit 0으로
끝났다. Raw 1,400/2,800의 validation objective는 0.05007/0.02071,
scale-normalized 1,400/2,800은 0.03732/0.01772였다. 고정 규칙은
scale-normalized 2,800-step을 선택했고 full-BC/paired-response L2는
0.01162/0.01220이었다. 이 결과는 N1 pass나 novelty가 아니라 optimization
attribution이다.

새 prospective `configs/nonlinear_pde_n1b.json`은 이 선택만 parent N1에
추가한다. 다섯 confirmatory seed에서 joint/independent/ACFlow/LANO
completion, pair/pair-zero/random-pair/DeltaPhi-style operator,
generic probabilistic operator와 NOP adaptation을 train/validation만으로
학습한다. 모든 checkpoint·validation metric·source commit checksum을
public manifest에 고정하기 전 outer test는 생성하지 않는다.
Conditional-mean, random/variance acquisition, NOTS-style policy와 ACO
ceiling은 비학습 control로 같은 manifest에 명시한다. Train-only
centered POD-96은 direct probabilistic baseline의 fixed representation일
뿐 AURORA architecture나 novelty가 아니다. 모든 model seed가 같은
representation을 쓰도록 POD seed 73080601과 subspace iteration 4회를
test 전에 고정했다. POD RNG와 model RNG를 분리해 각 confirmatory seed가
generic/NOP weight initialization과 minibatch sampling을 함께 제어한다.

Exact `1d0bd9c`의 dependency-complete contract는 117/117을 통과했고
다섯 A6000 checkpoint job은 모두 exit 0, eligibility true, test access
false로 끝났다. 50개 learned checkpoint와 모든 seed에서 동일한
train-only POD hash는
`results/nonlinear_pde_n1b_checkpoint_manifest_20260805.json`에 고정했다.
AURORA shared operator의 validation full-BC/paired-response L2 mean은
0.01347/0.01366이었다. 그러나 pair loss는 pair-zero보다 4/5,
random-pair보다 3/5, DeltaPhi-style paired metric보다 2/5 seed에서만
좋았고, combined objective는 DeltaPhi-style보다 0/5 seed에서 좋았다.
Checkpoint freeze의 목적은 실행 가능한 비교군을 test 전에 고정하는
것이지 validation superiority를 선언하는 것이 아니다. Outer-test
selector, evaluation RNG, route estimand와 bootstrap은
`configs/nonlinear_pde_n1c.json`에 고정했고 exact source `62605a0`의
125/125 A6000 contract 뒤 처음 test를 열었다. PBS outer test는 5 seed를
모두 정상 완료했지만 N1은 failed다.

| N1c check | observed | decision |
|---|---:|---|
| worst full-BC operator L2 | 0.01404 | pass |
| worst functional coverage error | 0.03281 | pass |
| maximum AURORA route-action disagreement | 0 | pass |
| pair loss better than pair-zero | 3/5 seeds | fail |
| missing energy vs independent heads | −0.65%, 0/5 | fail |
| sparse-2 energy vs independent heads | −1.09%, 0/5 | fail |
| missing acquisition regret vs ACFlow | 2/5 seeds | fail |
| sparse-2 acquisition | both learned policies equal oracle | strict superiority fail |

독립 heads와 ACFlow의 direct/sequential action disagreement seed mean은
각각 0.1174/0.1762였으나, sequential-minus-direct true-risk 차이는
0.00065/0.00121로 작고 seed별 부호가 섞였다. 따라서 route inconsistency의
존재는 보였어도 positive decision harm는 입증하지 못했다.

Route candidate VoI 구현은 route별 seed offset을 사용해 등록된 common
random numbers 계약을 위반했다. 해당 VoI/next-component 보조 지표만
invalid로 제외하며, N1 fail을 결정한 distribution, pair, acquisition과
valid route-action 지표는 영향을 받지 않는다. N1d shift와 irregular 3D는
실행하지 않는다. N1c-a는 exact `b97899c`의 130/130 contract 뒤 같은 open
test와 50개 checkpoint만 재사용해 5 seed 모두 완료됐다.

| N1c-a diagnostic | AURORA | strongest control | direction |
|---|---:|---:|---:|
| missing conditional excess NLL | 0.07074 | ACFlow 0.06275 | 0/5 |
| sparse-2 conditional excess NLL | 0.08439 | independent 0.06716 | 0/5 |
| partial-4 conditional excess NLL | 0.10362 | independent 0.07688 | 0/5 |
| missing 64×128 acquisition regret | 0.001029 | ACFlow 0.000489 | 1/5 |
| worst-route true-oracle excess risk | 0.01015 | independent 0.01034 | 3/5 |

Missing/sparse-2 functional energy에서 density oracle substitution의
seed-mean difference는 0.02478/0.02392이고 true simulator substitution은
0.00191/0.00412였다. 이는 비가산적 교체 진단이지 인과적 분해는 아니지만,
현재 병목이 operator보다 joint density와 그 학습 objective에 있음을
일관되게 지지한다. 8×32에서 64×128로 sample을 늘리면 regret가 크게
감소해 기존 acquisition 실패가 일부 Monte Carlo-limited였음을 보였으나,
안정화된 예산에서도 ACFlow 우위는 뒤집히지 않았다. Sparse-2에서는 모든
budget에서 AURORA와 ACFlow가 oracle과 동일해 task 자체가
non-discriminative였다.

공개 aggregate는
`results/nonlinear_pde_n1c_20260805.json`과
`results/nonlinear_pde_n1c_attribution_20260806.json`이다. N1c-a에는
success threshold, model selection, N1c relabel 또는 N1d/3D 권한이 없다.

#### 결과 전 고정해 완료한 두 development audit

Density-objective audit은 같은 context-conditioned 2-GMM, 초기 weight,
minibatch, optimizer와 한 step당 likelihood 평가 1회를 유지한다. Fresh
development seed 5개에서 3,072×8 train, 384×8 selection-validation,
별도 384×8 audit-validation을 쓴다. 다음 네 objective를 서로 선택하지
않은 채 모두 보고한다.

1. N1c와 같은 random-mask raw conditional NLL
2. 같은 random mask의 unobserved-component 정규화 NLL
3. full-joint NLL의 component 정규화 control
4. missing/sparse-2/partial-4를 동일 주기로 도는 registered composite
   conditional NLL

공통 checkpoint metric은 세 registered mask의 component-normalized
conditional NLL 평균이다. Disjoint audit-validation에서는 exact
radius-truncated true BC law 대비 excess NLL을 seed별로 보고한다.
Independent head나 ACFlow를 이 audit에서 다시 학습해 winner를 고르지
않으며, 어떤 variant도 여기서 method가 되지 않는다.

Decision-task adequacy audit은 learned model과 checkpoint를 0개 읽는다.
True simulator calibration 384×8로 네 functional을 표준화하고, disjoint
96-context의 missing/sparse-2 mask에서 true truncated BC law만 condition해
bounded-loss Bayes action과 component acquisition risk를 계산한다. Base
posterior 2,048 sample과 독립적인 두 outer 32 × inner 64 replicate를
고정했다. Winner entropy뿐 아니라 VoI, first–second margin, risk
dispersion, action-change rate와 replicate winner/top-2/risk stability를
함께 보고한다. Threshold가 없으므로 결과는 task가 충분히 비자명한지에
대한 정량적 근거이지 pass/fail이 아니다.

Exact source `337c75e`의 dependency-complete contract는 144/144를
통과했다. Density 5-seed array와 task job은 모두 exit 0이고 N1 test
access는 false였다.

| Density audit · exact-law excess NLL | N1c raw | full joint | reduction | direction |
|---|---:|---:|---:|---:|
| missing | 0.06352 | 0.04622 | 27.2% | 5/5 |
| sparse-2 | 0.07772 | 0.05923 | 23.8% | 5/5 |
| partial-4 | 0.09794 | 0.07808 | 20.3% | 5/5 |

Registered composite의 감소는 1.5–2.5%이고 세 mask에서 5/5 방향이었지만,
per-component normalization은 missing/sparse-2/partial-4에서 각각
1/5, 2/5, 4/5뿐이었다. Full-joint가 가장 강한 engineering control이라는
진단은 분명하지만 어떤 variant도 method로 선택하지 않는다.

| Task audit | missing | sparse-2 |
|---|---:|---:|
| base no-acquisition risk | 0.50366 | 0.33221 |
| post-acquisition risk · replicate A/B | 0.34778 / 0.34807 | 0.14704 / 0.14667 |
| VoI · replicate A/B | 0.15587 / 0.15558 | 0.18517 / 0.18554 |
| winner agreement | 0.9271 | 1.0000 |
| top-2 agreement | 0.7396 | 0.9583 |
| winner diversity | components 2/6 dominate | component 6 · 96/96 |

Missing은 value와 context-dependent winner가 모두 남아 향후 acquisition
평가 후보가 된다. Sparse-2는 acquisition 자체의 value는 크지만 최적
component가 고정되어 adaptive policy를 식별하지 못한다. 이 mask를 결과
뒤 삭제하지 않고 negative adequacy evidence로 보존하되, 향후 adaptive
headline에서는 제외한다. 공개 aggregate는
`results/nonlinear_pde_n1_density_objective_audit_20260806.json`과
`results/nonlinear_pde_n1_decision_task_audit_20260806.json`이다.

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
G1s가 새 exact pipeline sanity를 통과했으므로 learned protocol 등록은
가능하다. 그러나 multicomponent nonlinear N0/N1을 먼저 검증하고,
velocity-only 3D는 그 결과와 strong physical baseline 뒤에 실행한다.

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

이전 작업 제목 **“AURORA: Coherent Neural Operators under Partial and
Missing Boundary Conditions”**은 N1c-a 뒤 제출 제목으로 사용하지 않는다.
Coherence는 달성했지만 conditional accuracy와 decision superiority를
함께 얻지 못했기 때문이다. 현재는 **확정된 paper identity나 headline
contribution이 없다**. Paired supervision과 uncertainty decomposition도
양수 증거 전까지 contribution 목록에서 제외한다.

다음 원고 구조는 missing endpoint용 operator-specific method와 fresh
prospective result가 strong baseline보다 양수일 때만 활성화한다.

1. joint compatibility가 accurate mask conditionals와 충돌하는 문제
2. solution-functional risk를 보존하는 compatible posterior construction
3. posterior discrepancy에서 bounded functional regret를 제한하는 보장
4. exact → nonlinear strong-baseline falsification
5. model-independent adequacy를 통과한 nontrivial acquisition benchmark
6. positive nonlinear result 뒤에만 irregular 3D protocol
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
4. Density representation/optimization/data-sufficiency attribution과
   G1s fresh exact sanity **(완료 · G1s 통과)**
5. 완료·검증된 Aneumo base-family-disjoint selective cache에서 train-only
   physical-scaling audit을 실행하고, learned response의 비자명성을 먼저
   판정 **(완료 · velocity만 eligible, pressure 탈락)**
6. Multicomponent nonlinear N0/N1 strong-baseline test와 N1c-a failure
   attribution **(완료 · N0r 통과, N1c 실패 유지, joint density 병목)**
7. 같은 joint GMM의 네 density objective를 fresh development seed의
   validation에서 비교 **(완료 · full-joint 5/5 개선, novelty 아님)**.
8. True law와 simulator만으로 acquisition value·winner diversity·Monte
   Carlo stability를 감사 **(완료 · missing 유의미, sparse-2 fixed winner)**.
9. Missing endpoint에서 full-joint training의 이득을 보존하면서 arbitrary
   conditional accuracy를 개선하는 operator-specific algorithm·보장과
   fresh N1 re-entry를 별도 결과 전 protocol로 설계한다. 현재는 미등록이다.
10. Fresh N1이 양수일 때만 velocity-only irregular 3D backbone과 transient
   학습을 등록한다.
11. CMHA status branch는 공식 case map과 positive real-CFD increment가
   확인될 때만 secondary로 복원
