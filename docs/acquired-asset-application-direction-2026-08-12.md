# 확보 자산 기반 ISBI 2027 방향 재선정

> **Schema 11.8 superseding decision:** 아래 AneuX nested-orbit 방향은
> direct-prior 검토 후 schema 11.7에서 실행 전 기각된 역사다. 현재 유일한
> conditional source lead는 **Aneumo field-error-matched multi-flow response
> fidelity**다. 하나의 nominal-flow CFD field를 anchor로 받아 다른 유량의
> velocity response를 재현하는 sensitivity-sweep 문제이며, rupture/clinical
> target이 아니다. 34.0/40이지만 novelty는 정확히 2.5/5 하한선이므로
> [method-free P0 v2](../configs/aneumo_response_fidelity_p0_v2.json)와
> [상세 audit](response-faithful-hemodynamic-surrogate-source-audit-2026-08-12.md)만
> 허용한다. P0는 current exact private path가 unresolved라 non-executable이며,
> method/architecture/GPU/validation/test/claim은 아직 0이다.

상태: **AneuX factorized nested preprocessing-orbit conditional source lead 유지 ·
source-semantics 결함을 실행 전에 수정한 method-free P0 v2 사전등록 · exact path/
manifest/reader preflight 미해결 · primary problem/method/architecture/GPU/outer
test/paper claim 0**  
기준일: 2026-08-12 KST

## 0. 실행 전 source-semantics correction

공식 `content-description-v1.0.pdf`를 다시 읽은 결과, `morpho-per-cut.csv`의
170개 morphometric은 **area-005 resolution에만** 존재한다. 따라서 v1의
“source-provided 170 morphometrics로 세 resolution의 prediction instability를
측정한다”는 설계는 실행 불가능했다. 또한 exact official repository head
`a6b355e8f271e9a88399a2e432ed924d99b85d64`에는 README, license와 figure만 있고
README 자체가 code publication in progress라고 명시한다. 공식 feature code로 세
resolution을 재계산할 수도 없다.

이 결함은 data row, job 또는 endpoint를 보기 전에 발견했다. v1 config는 SHA-256
`b82e3606…` 그대로 보존하며 **pre-execution superseded**로 처리한다. 이는 결과를 본
뒤 threshold나 reader를 고치는 repair가 아니다. 현재 계약은
[`aneux_nested_orbit_p0_v2.json`](../configs/aneux_nested_orbit_p0_v2.json)이며,
정확한 private path, manifest와 reader dependency preflight가 아직 없으므로 실행할
수 없다.

## 1. 결론부터

가장 타당한 방향은 **같은 뇌동맥류가 mesh resolution과 neck/parent-vessel cut에
따라 여러 개의 유효한 surface representation을 갖는다는 사실을 학습 문제의
일부로 다루는 것**이다. 잠정 제목은 다음과 같다.

> **Same Aneurysm, Different Mesh: Preprocessing-Orbit Reliable Surface Learning
> for Rupture-Status Assessment**

단, 모든 전처리 변형을 하나의 nuisance로 취급해서는 안 된다.

- resolution은 같은 surface의 discretization을 주로 바꾸므로, fixed cut 안에서는
  nuisance invariance를 요구할 수 있다.
- dome, ninja, cut1, cut2는 parent-vessel context의 양을 바꾼다. 이 문맥은 실제
  판별 정보를 가질 수 있으므로 최종 logit까지 같게 강제하면 정보가 사라진다.
- 따라서 필요한 것은 flat consistency가 아니라 **shared aneurysm anatomy와
  context residual을 분리하는 nested orbit**이다.

이 선택은 “DiffusionNet에 consistency loss를 붙였다”는 조합 novelty가 아니다.
application contribution은 평균 AUROC가 가리는 **동일 병변의 casewise decision
instability**를 독립 평가 문제로 만들고, 정보가 보존되어야 하는 축과 달라져도 되는
축을 분리한 뒤, patient/source-held-out 조건에서 reliability를 검증하는 데 있다.

현재는 source-level 적합성만 통과했다. 과거 AneuX P0 `115177.ECE-util1`은
transport 단계에서 끝난 0/13 no-verdict이며 수리하거나 재실행하지 않는다. 이번
version은 network downloader가 아니라 **이미 확보한 private holding의 exact-path와
nested-orbit nontriviality를 검사하는 새 문제·새 증거 계약**이다.

## 2. 확보 자산을 같은 기준으로 다시 비교

8개 축은 0--5점이다. 32/40 이상이어도 target identifiability 3.5, residual
novelty 2.5, asset readiness 3.0, independent unit 3.0, strong-baseline feasibility
3.0 중 하나라도 실패하면 admission이 아니다.

| 확보 자산 기반 후보 | 중요성 | target | residual gap | asset | unit | baseline | figure | 일정 | 합계 | 판정 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **AneuX factorized nested preprocessing-orbit reliability** | 4.0 | 4.5 | 3.0 | 4.0 | 4.0 | 5.0 | 4.5 | 4.0 | **33.0** | conditional lead; P0 only |
| BenchAnXplore sac-local transient velocity operator | 3.5 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 4.0 | 3.0 | 32.5 | novelty floor fail |
| Aneumo multi-BC steady surrogate re-entry | 3.0 | 5.0 | 2.0 | 5.0 | 5.0 | 5.0 | 4.0 | 3.5 | 32.5 | novelty floor + prior performance fail |
| AneuG/Aneurisk structure-faithful WSS | 4.5 | 3.0 | 2.5 | 2.0 | 4.0 | 5.0 | 5.0 | 2.0 | 28.0 | target/asset fail |
| CMHA hemodynamic incremental value | 4.0 | 3.0 | 2.0 | 2.0 | 3.5 | 5.0 | 4.5 | 3.0 | 27.0 | linkage + prior negative signal |
| Aneurisk context visualization alone | 2.5 | 5.0 | 1.0 | 3.0 | 4.0 | 5.0 | 5.0 | 4.0 | 29.5 | no residual research gap |

BenchAnXplore는 105×80 transient velocity field라는 훌륭한 engineering asset이지만
105 case 전체가 representation discovery에 사용됐고 pressure/WSS가 검증되지 않았다.
새 독립 pulsatile cohort 없이 이를 proposal superiority evidence로 쓰면 circular하다.
Aneumo는 boundary-aware model이 matched geometry-only model보다 3/3 seed에서
좋았지만 absolute relative-L2 gate를 모두 실패했다. 이 실패를 architecture tuning으로
수리하지 않는다. CMHA는 lesion-level image/mesh/hemodynamics join이 성립하지 않았고
exploratory ΔAUPRC도 음수였다. AneuG/Aneurisk의 vector-field 질문은 중요하지만 current
material evidence와 direct-prior separation이 부족하다.

## 3. 정확한 application problem

### 3.1 예측 대상

대상은 **cross-sectional rupture status association**이다. 미래 파열 확률,
instability, 성장, 임상 utility 또는 causal effect로 부르지 않는다. 독립 단위는
mesh가 아니라 patient이며, 한 patient의 여러 lesion과 한 lesion의 여러 surface는
항상 같은 split에 둔다. patient ID가 식별되지 않는 row는 supervised primary analysis에
넣지 않는다.

각 lesion (i)에 cut (c\in\mathcal C_i)와 resolution
(r\in\mathcal R)로 생성된 surface (X_{i,c,r})가 있다고 하자.

\[
\mathcal O_i=\{X_{i,c,r}:c\in\mathcal C_i, r\in\mathcal R\}
\]

flat orbit은 모든 (X_{i,c,r})를 의미상 동등하다고 가정한다. 대신 다음 nested
structure를 사용한다.

\[
X_{i,c,r}\mapsto(z^{\mathrm{aneurysm}}_{i,c,r},
z^{\mathrm{context}}_{i,c,r}),\qquad
\ell_{i,c,r}=b(z^{\mathrm{aneurysm}}_{i,c,r})+
\delta_c(z^{\mathrm{context}}_{i,c,r}).
\]

fixed (c) 안에서는 resolution에 따른 (z^{\mathrm{aneurysm}})와 prediction의
변화를 줄인다. 서로 다른 cut 사이에서는 공통 dome/anatomy token만 맞추고
context residual과 최종 logit은 같다고 가정하지 않는다.

### 3.2 검증할 failure mechanism

평균 AUROC가 비슷해도 다음 문제가 남을 수 있다.

1. 같은 병변의 representation을 바꾸면 임계값 양쪽으로 prediction이 뒤집힌다.
2. best-view 평균 성능은 좋아도 worst-view calibration과 Brier/NLL이 나쁘다.
3. parent-vessel context의 평균 이득이 일부 병변의 큰 반대방향 변화와 상쇄된다.
4. orbit disagreement가 error와 연관되지만 single-view model은 이를 관측하지 못한다.

이 네 항목 중 어느 것도 material하게 나타나지 않으면 논문 문제 자체를 닫는다.

## 4. 수정된 method-free P0 v2

V2는 `dome` cut만 primary로 사용해 **resolution nuisance**를 먼저 분리한다. Cut은
정보 집합을 바꾸므로 P0에서는 area-005 cross-cut descriptive analysis에만 두고
gate에 쓰지 않는다. 세 dome mesh 모두에서 같은 deterministic surface signature를
계산한다. Piecewise-planar triangle 위의 면적 적분을 정확히 사용해 surface area,
open boundary perimeter, centroid covariance/eigenvalue ratio, normalized radial
fourth/sixth moment와 normal-tensor eigenvalue 등 11개를 고정한다. 동일 평면을
triangle subdivision만 해도 값이 보존되도록 unit test한다. Vertex/face count,
random point sampling과 watertight volume은 사용하지 않아 resolution 자체를
feature로 누설하지 않는다. Degenerate triangle, non-manifold edge와 닫힌 dome은
reader preflight에서 fail한다.

HUG2016/HUG2016SNF만 development로 사용하고 @neurIST/Aneurisk는 열지 않는다.
Known status, known patientID, 세 dome resolution이 모두 있는 lesion만 eligible이다.
모든 lesion/view는 환자 단위로 5-fold outer/4-fold inner split에 함께 묶는다.
L2 logistic probe는 canonical `dome_area-005`에서만 fit하고, 같은 held-out lesion의
`original`, `area-001`, `area-005` signature에 동일하게 적용한다. Median imputation,
standardization, C 선택은 training fold 안에서만 수행하고 seed, grid와 tie-break를
고정한다.

먼저 probe가 무의미하지 않아야 한다. Canonical area-005 OOF AUROC의 patient-
bootstrap 95% lower bound가 0.60을 넘지 못하면 **uninformative probe**로 닫고
resolution reliability에 대한 과학 판정을 하지 않는다. Asset/reader/integrity와
이 adequacy gate가 모두 통과한 뒤 다음 두 primary 조건을 **모두** 요구한다.

1. 세 resolution OOF probability의 `max-min > 0.10`인 lesion 비율에 대한
   patient-bootstrap 95% lower bound가 0.05보다 크다.
2. 같은 probability range와 `orbit-mean probability`의 Brier residual 사이
   Spearman correlation의 patient-bootstrap 95% lower bound가 0.10보다 크다.

두 번째 error는 각 view Brier 평균이 아니라 orbit-mean probability의 squared
error다. 따라서 disagreement variance를 error 정의에 다시 넣어 correlation을
기계적으로 만드는 tautology를 피한다. 0.5 decision flip은 threshold에 민감하므로
secondary sensitivity로 내렸고 data에서 threshold를 선택하지 않는다. 모든 bootstrap은
환자를 복원추출하고 그 환자의 모든 lesion/view를 multiplicity와 함께 보존한다.

이 기준은 임상적 위해나 치료 threshold가 아니라 method development가 정당한지를
가르는 engineering effect size다. V2 pass도 strong-baseline feasibility P1 하나만
등록할 수 있으며 architecture, GPU, outer test 또는 contribution을 열지 않는다.

## 5. P0 통과 뒤의 최소 architecture

아래는 선택된 방법이 아니라 비교 가능한 development hypothesis다.

### 5.1 입력과 encoder

- surface vertices/faces, normals, curvature, cut-boundary distance와 cut token;
- area-weighted sampling 또는 intrinsic operators로 vertex density confounding을
  줄인 surface encoder;
- DiffusionNet을 가장 강한 discretization-agnostic backbone/control로 둔다.

### 5.2 factorized nested-orbit head

1. **shared anatomy token**: dome 중심의 intrinsic pooled representation. Fixed-cut
   resolution 사이에서 일치시킨다.
2. **context residual token**: neck/parent-vessel 영역에서 얻고 cut별 추가 정보를
   허용한다.
3. **orbit aggregator**: available view set을 permutation-invariant attention으로
   모으되, 누락 view mask를 입력한다.
4. **reliability head**: representation disagreement를 uncertainty score로 내고
   risk--coverage 평가에 사용한다.

개발 loss의 후보는 supervised orbit risk, fixed-cut resolution consistency,
shared-anatomy cross-cut alignment, worst-view risk와 residual magnitude control이다.
최종 logit의 unconditional cross-cut consistency는 금지한다. Loss를 많이 붙이는
것 자체가 contribution이 되지 않도록 각 항은 하나의 failure mechanism과 하나의
ablation에 대응시킨다.

## 6. 반드시 이겨야 하는 baseline

동일 patient/source split, parameter budget, preprocessing budget과 seed에서 다음을
비교한다.

1. 170 morphometrics + penalized logistic regression;
2. PointNet++ dome, cut1 및 naive multi-view average;
3. PointNeXt 또는 DGCNN single-view;
4. DiffusionNet single-view;
5. E(3)-equivariant anatomical mesh model control;
6. naive logit/view averaging;
7. flat final-logit consistency;
8. GroupDRO with preprocessing pipeline as group;
9. proposed nested factorization.

PointNet, DiffusionNet, equivariance, consistency, GroupDRO와 set attention 각각은
선행 구성요소 또는 control이다. Proposal이 이들을 단순 조합한 정도라면 논문을
진행하지 않는다.

## 7. split과 평가

### 7.1 split

- 모든 split은 patient-grouped, lesion-orbit atomic이다.
- HUG 계열 안에서 train/validation을 고정하고 development 선택만 수행한다.
- @neurIST와 Aneurisk source는 가능한 경우 별도 locked external-source test로 둔다.
- missing patient ID, unknown rupture status와 source ambiguity는 primary analysis에서
  제외하고 flow diagram에 수를 공개한다.
- outer test는 final config hash, checkpoint selection rule과 table shell이 고정되기
  전에는 열지 않는다.

### 7.2 primary evidence

| 역할 | endpoint |
|---|---|
| discrimination 유지 | patient-cluster bootstrap AUROC/AUPRC, worst-pipeline AUROC/AUPRC |
| casewise reliability | resolution-only decision flip, logit range/variance, rank reversal |
| probabilistic quality | worst-view NLL, Brier, ECE, calibration slope/intercept |
| source transport | source-held-out metric과 source×method interaction |
| useful uncertainty | orbit-disagreement error AUROC, selective risk--coverage/AURC |

Primary success는 strong DiffusionNet과 compute-matched flat consistency 대비
worst-view Brier와 flip rate를 개선하면서 AUROC의 patient-bootstrap 95% CI가 사전
등록 non-inferiority margin 아래로 내려가지 않는 것이다. Exact margin은 P1의
training-only pilot 전에 고정한다. 평균 AUROC 하나만 좋아서는 성공이 아니다.

### 7.3 figure와 table

- **Figure 1:** 한 병변의 3 resolution × 4 cut을 같은 camera/scale로 놓고,
  prediction, uncertainty와 anatomy/context attribution을 표시한다.
- **Figure 2 또는 compact panel:** cohort-level best-average metric과 casewise
  flip/worst-view metric의 불일치를 보여준다.
- **Table 1:** baseline main results. 모든 셀은 같은 point estimate/95% CI 형식.
- **Table 2:** factorization, resolution loss, context residual, aggregator와
  reliability head의 one-factor ablation.

## 8. 논문 claim--evidence 구조

| claim | 필요한 evidence | 없으면 삭제할 문장 |
|---|---|---|
| C1. 평균 field/classification accuracy는 preprocessing reliability를 보장하지 않는다 | P0/P1에서 평균 metric이 유사한데 casewise flip·worst-view error가 material함 | problem motivation과 “hidden failure” 주장 |
| C2. resolution nuisance와 cut context를 분리해야 한다 | flat consistency 대비 nested factorization의 matched ablation | factorized method novelty |
| C3. proposal은 평균 discrimination을 희생하지 않고 worst-view reliability를 높인다 | locked validation/outer source에서 AUROC non-inferiority + flip/Brier improvement | efficacy claim |
| C4. orbit disagreement는 오류를 식별하는 유용한 신호다 | selective risk/AURC와 calibration, failure-case figure | uncertainty/abstention claim |

이 matrix 밖의 auxiliary result는 본문에 넣지 않는다. 임상 파열 위험, treatment
decision, causal mechanism과 prospective utility는 주장하지 않는다.

## 9. ISBI 2027 네 쪽 설계

공식 author instructions 기준 regular paper는 technical content가 첫 4쪽 안에
들어가야 하고, optional 5쪽은 ethics, acknowledgement/conflict와 references에만
쓸 수 있다. Single-blind이며 full paper는 proceedings에 포함된다.

| 지면 | 기능 | 들어갈 내용 |
|---|---|---|
| 1 | 문제와 gap 고정 | title/abstract, clinical preprocessing failure, direct-prior boundary, C1--C3 |
| 2 | 해법의 필연성 | nested orbit 정의, anatomy/context factorization, loss와 inference; Figure 1 |
| 3 | 반증 가능한 평가 | AneuX cohort/split, baselines, primary metrics, statistics, ethics; Table 1 |
| 4 | 결과와 한계 | main/ablation, casewise figure, limitations, conclusion |
| 5 선택 | 비기술 요소 | Compliance with Ethical Standards, COI/funding, references only |

결과가 없으므로 현재 title/abstract/method/result/figure를 main manuscript에 넣지
않는다. 먼저 P0 failure를 관측하고, P1에서 strong baseline feasibility를 확인한 뒤,
development protocol과 빈 table shell을 고정한다.

## 10. 직접 선행과 claim boundary

- [AneuX official v1.0](https://zenodo.org/records/6678442): 750 dome, 668 vessel
  tree, 세 resolution, 네 cut과 170 morphometrics를 제공한다.
- [Shape trumps size](https://doi.org/10.3389/fneur.2022.809391): AneuX
  morphometry, cut robustness와 source transport의 직접 선행이다.
- [AneuX PointNet++](https://doi.org/10.3389/fphys.2024.1293380): dome/cut1
  point-cloud rupture-status classification과 external validation의 직접 선행이다.
- [MATCH geometry uncertainty](https://pmc.ncbi.nlm.nih.gov/articles/PMC6434802/)
  및 [MATCH hemodynamics](https://pmc.ncbi.nlm.nih.gov/articles/PMC6524809/):
  reconstruction variability가 morphometry와 hemodynamics를 바꾸는 직접 근거다.
- [DiffusionNet](https://arxiv.org/abs/2012.00888): discretization-agnostic
  surface learning baseline이다.
- [Latent aneurysm shape space](https://doi.org/10.1016/j.cmpb.2026.109445):
  multi-resolution latent robustness를 직접 점유한다.
- [EAMS](https://openreview.net/forum?id=sEMJHUb8Qf): intracranial aneurysm을
  포함한 anatomical mesh segmentation에서 pose/resolution robustness와
  equivariant mesh modelling을 직접 점유한다.
- [GroupDRO](https://openreview.net/forum?id=ryxGuJrFvS),
  [Set Transformer](https://proceedings.mlr.press/v97/lee19d.html),
  [neural calibration](https://proceedings.mlr.press/v70/guo17a.html)과
  [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html)은 각각
  worst-group optimization, permutation-invariant aggregation, calibration과
  selective prediction의 직접 방법 선행이다. 이 구성요소는 novelty가 아니라
  baseline 또는 측정 도구다.

최종 4쪽 원고에서는 이 계보를 역할별로 압축한다. 데이터/임상 맥락 2--3개,
aneurysm surface/cut 직접 선행 3--4개, mesh representation 2--3개,
robustness/reliability 방법 선행 3--4개, 통계·보고 근거 1--2개만 본문 주장과
일대일로 연결한다. 참고문헌 수를 늘리기 위한 citation은 넣지 않고, C1--C4의
선행 점유 또는 평가 선택을 설명하지 못하는 reference는 삭제한다.

## 11. 중단 조건

다음 중 하나면 이름이나 loss를 바꿔 살리지 않고 후보를 닫는다.

1. exact private AneuX orbit과 patient/source grouping을 재확인하지 못함;
2. P0의 nontriviality 조건이 2/3 미만;
3. strong DiffusionNet/naive averaging이 이미 casewise reliability를 해결함;
4. factorization이 flat consistency 대비 compute-matched 이득이 없음;
5. AUROC를 크게 희생해야 reliability가 좋아짐;
6. source-held-out 결과가 방향 또는 크기 면에서 재현되지 않음;
7. contribution이 generic consistency/uncertainty/model stacking으로만 설명됨.

이 방향은 현재 가장 가능성 높은 **conditional research identity**이지 accept-ready
paper가 아니다. 장점은 이미 확보 이력이 있는 AneuX의 고유 반복표현 구조를 정면으로
사용하면서, direct prior가 점유한 평균 성능·단순 mesh robustness와 다른 반증 가능한
application question을 만든다는 점이다.
