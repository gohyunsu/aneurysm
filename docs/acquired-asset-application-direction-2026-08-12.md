# 확보 자산 기반 ISBI 2027 방향 재선정

상태: **AneuX factorized nested preprocessing-orbit를 conditional source lead로
선정 · 새 method-free P0만 사전등록 · primary problem/method/architecture/GPU/outer
test/paper claim 0**  
기준일: 2026-08-12 KST

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

## 4. 새 method-free P0

새 계약은 [`configs/aneux_nested_orbit_p0.json`](../configs/aneux_nested_orbit_p0.json)에
고정한다. 과거 downloader/reader를 재실행하지 않으며 network access도 금지한다.
`introai9`의 이미 확보된 private holding을 CPU-only PBS에서 읽어 다음을 확인한다.

1. exact archive/extracted-root 존재, expected size/checksum 또는 immutable manifest;
2. lesion--patient--source--status grouping과 unknown/missing pattern;
3. 세 resolution과 네 cut의 실제 completeness 및 동일 lesion mapping;
4. fixed-cut resolution과 cross-cut context를 분리한 within-lesion/between-lesion
   morphometric variation;
5. development source와 patient group만 사용한 frozen regularized-morphometry
   baseline의 casewise logit range, decision-flip rate, rank reversal와 calibration;
6. external source, proposed method, neural architecture와 GPU에 접근하지 않았는지.

P0의 primary nontriviality gate는 development data에서 다음 세 조건 중 둘 이상을
요구한다.

- fixed-cut resolution 변화로 인한 decision flip fraction의 patient-bootstrap
  95% lower bound가 5%를 넘는다;
- lesion 중 10% 이상에서 fixed-cut resolution logit range가 0.20을 넘고 그 비율의
  95% lower bound가 10%를 넘는다;
- orbit disagreement와 baseline error 사이의 patient-bootstrap Spearman correlation
  95% lower bound가 0.20을 넘는다.

이 수치는 임상적 위해 임계값이 아니라, 새 방법을 개발할 정도로 failure가
비자명한지를 결정하는 prospectively frozen engineering threshold다. Gate가
통과해도 한 개의 baseline-feasibility P1만 등록할 수 있다. P0에서 architecture,
GPU, outer test 또는 논문 contribution을 열지 않는다.

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
