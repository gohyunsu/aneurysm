# Goal-oriented hemodynamic segmentation · cold audit

감사일: 2026-08-09 KST
상태: **conditional shortlist 1 · problem only · method/architecture unselected ·
S0a asset/runtime audit only · no GPU training · no outer test · not
submission-ready**

이 문서는 실패한 AURORA BC-operator, Aneumo V1/V1e, 4D-flow 또는 RSNA
후보를 다른 이름으로 복원하지 않는다. 새 후보가 직접 선행연구와 데이터·실행
현실성을 통과하는지 문제 수준에서 검사한 기록이다. 아직 방법론적 contribution을
확정하지 않으며, S0a/S0b가 실패하면 후보를 폐기한다.

## 1. 남은 연구 질문

고정된 표준 CFD 법칙과 미리 정한 hemodynamic functional 벡터
\(J(\Omega)\)가 있을 때, voxel overlap을 최대화하는 segmentation과
\(J\)의 오차를 최소화하는 segmentation은 일반적으로 같지 않다. 후보 질문은
다음과 같다.

> CTA에서 추정한 aneurysm–parent-vessel domain의 작은 경계 오차를 PDE
> shape sensitivity에 투영해 학습하면, Dice·boundary·topology loss로 학습한
> 강한 segmentation baseline보다 held-out 환자의 표준화된 simulation
> functional 오차를 줄일 수 있는가?

정답 domain을 \(\Omega\), 예측 경계의 signed normal displacement를
\(\delta_\theta(s)\), functional \(J_k\)의 discrete-adjoint shape gradient를
\(g_k(s)\)라 두면 후보 학습 신호의 핵심은

\[
  J_k(\widehat\Omega_\theta)-J_k(\Omega)
  = \int_{\partial\Omega}g_k(s)\,\delta_\theta(s)\,ds
  + R_k(\delta_\theta)
\]

의 signed first-order term이다. 단순히 sensitivity magnitude로 voxel을
가중하지 않는다. 국소 오차의 방향과 상쇄를 보존하는 vector projection,
기하학적 trust region과 remainder audit이 모두 필요하다. 이 식은 검증할
가설이지 현재 구현 또는 보장이 아니다.

Primary estimand 후보는 patient-disjoint outer test에서 manual domain과
predicted domain에 **같은 고정 solver·mesh policy·boundary-condition
scenario**를 적용했을 때의 standardized functional error 차이다. CFD를
임상 truth, patient-specific physiology 또는 rupture-risk predictor로 부르지
않는다. Rupture status는 architecture, loss, checkpoint 또는 threshold 선택에
사용하지 않는다.

## 2. 직접 선행연구가 이미 점유한 범위

| 계보 | 직접 선행 | 이 후보에서 novelty가 아닌 것 |
|---|---|---|
| segmentation→CFD 자동화 | [AI segmentation for aneurysm CFD](https://doi.org/10.1142/S0219519423400559), [automated anterior-circulation CFD pipeline](https://doi.org/10.1038/s41598-024-80891-4) | 자동 mesh/solver pipeline, CFD로 segmentation을 사후 평가하는 것 |
| 영상→mesh+field 공동예측 | [Image2Flow](https://doi.org/10.1371/journal.pcbi.1012231)은 MRI에서 volume mesh와 pressure/velocity를 함께 예측하고 pointwise CFD loss를 사용한다. | image-to-CFD, graph decoder, joint segmentation/field loss, 빠른 surrogate |
| CFD-ready segmentation | [IAVS](https://arxiv.org/abs/2512.01319)는 count-guided localization, topology-aware segmentation과 CFD Applicability Score를 제안한다. | topology-aware nnU-Net, solver success/applicability를 endpoint로 두는 것 |
| vascular loss | [clDice](https://doi.org/10.1109/CVPR46437.2021.00225), [cbDice](https://doi.org/10.1007/978-3-031-72111-3_5) | centerline, radius, boundary 또는 topology loss 자체 |
| segmentation-induced flow variation | [MATCH phase Ib](https://doi.org/10.1007/s13239-019-00407-y), [2015 IA CFD challenge](https://doi.org/10.1007/s13239-018-00385-7), [lumen/BC sensitivity](https://doi.org/10.1007/s13239-023-00675-1) | segmentation이 WSS·flow를 바꾼다는 재확인 |
| inverse flow-image segmentation | [Joint reconstruction and segmentation as an inverse Navier--Stokes problem](https://doi.org/10.1017/jfm.2022.503)은 noisy velocity image의 flow domain과 velocity를 shape gradient로 공동 추정한다. | PDE/adjoint shape gradient를 segmentation에 연결하는 일반 발상 |
| task-based segmentation evaluation | [Quantitative PET task-based evaluation](https://pubmed.ncbi.nlm.nih.gov/38360049/)은 overlap·boundary metric과 metabolic quantity endpoint를 함께 비교한다. | 표준 segmentation metric과 downstream quantity가 다를 수 있다는 관찰 |
| differentiable PDE/shape optimization | [Deep Differentiable Simplex Layer](https://arxiv.org/abs/1901.11082), [neural-operator derivatives for PDE-constrained optimization](https://proceedings.mlr.press/v267/cheng25f.html), [NeuralFluid](https://arxiv.org/abs/2405.14903) | differentiable geometry, adjoint/shape derivative 또는 PDE optimization 일반론 |
| generic task/UQ control | task-driven conformal prediction, topology UQ, lesion-risk/FROC control | downstream risk, conformal calibration, uncertainty map을 붙이는 것 |

따라서 “physics-informed segmentation”, “CFD-aware U-Net”, GNN, attention,
implicit surface, adjoint 또는 uncertainty를 단독 contribution으로 쓰지 않는다.
PDE와 segmentation의 결합이나 downstream endpoint 평가도 이미 점유됐다.
독립 gap은 **CTA 학습에서 여러 사전 정의 PDE functional의 signed shape
derivative를 boundary-error pullback으로 구성하고, remainder-controlled trust
region과 held-out functional error 우위를 함께 입증하는 algorithm**에만 남을
가능성이 있다. Image2Flow처럼 field를 동시에 예측하거나 IAVS처럼 solver
성공률을 높이는 문제뿐 아니라 inverse-flow segmentation과도 구분돼야 한다.

## 3. 데이터 현실성

### CMHA · 유일한 primary 후보

[CMHA 원 논문](https://doi.org/10.1038/s41597-024-04056-8)과
[공식 Figshare record](https://doi.org/10.6084/m9.figshare.26965450.v1)는
99 patients/105 MCA aneurysms와 44 controls의 NIfTI CTA, aneurysm–artery
STL, aneurysm STL, clinical/morphological/hemodynamic table을 CC BY 4.0으로
공개한다. 환자 archive는 10,735,821,611 bytes이고 공식 MD5는
`e783d656ba51c6813aae9fca68565c17`이다. 작은 statistical archive에는 공식
설명과 같은 5개 CSV가 있다.

그러나 다음 한계 때문에 아직 training cohort가 아니다.

- 1,021 CTA 중 고품질 MCA case를 골라 만든 single-center selected cohort다.
- 여러 aneurysm이 있는 6명 때문에 105 lesion을 독립 patient로 세면 안 된다.
- CTA–aneurysm/parent STL–aneurysm STL–table의 105-lesion exact key mapping은
  row order가 아닌 공식 identifier로 다시 검증해야 한다.
- 공개 hemodynamics는 Fluent의 steady, formula-driven inlet와 fixed outlet
  pressure에서 얻은 19개 summary다. full field나 patient-measured BC가 아니다.
- 공개 summary는 목표 functional의 정답으로 재사용하지 않는다. 모든 비교
  method에 동일한 새 standardized solver contract를 적용한다.

### 보조 데이터 · primary cohort로 합치지 않음

- [OpenNeuro ds005096](https://github.com/OpenNeuroDatasets/ds005096)은
  63 patients/85 aneurysms와 expert voxel masks/STL을 공개하지만 clinician
  annotation은 subject당 선택된 한 session에만 있다. 24 longitudinal subject를
  24 supervised growth trajectory로 해석하지 않는다. TOF-MRA external
  modality stress test 후보일 뿐 CMHA와 training patient를 합치지 않는다.
- [2026 open CTA record](https://doi.org/10.5281/zenodo.15697196)은 세
  center의 172 CTA series, 90 controls/82 IA cases와 122 aneurysm STL을
  공개한다. 25.58 GB payload와 parent-vessel supervision의 정확한 의미를
  감사하기 전에는 aneurysm–parent-domain segmentation evidence로 쓰지 않는다.
- Aneumo의 기존 V1/V1e 실패는 그대로 보존한다. Synthetic geometry/field를
  이 후보의 양수 model evidence로 재해석하거나 CMHA outer test와 섞지 않는다.

## 4. ISBI 2027 적합성 점수

점수는 0–5이며, 낙관적 가능성이 아니라 2026-08-09 현재 검증된 상태를
평가한다.

| 축 | 점수 | 냉정한 판정 |
|---|---:|---|
| biomedical-imaging relevance | 5.0 | CTA segmentation error가 downstream simulation functional에 미치는 영향은 ISBI scope에 직접 맞는다. |
| identifiable estimand | 4.0 | 같은 solver/BC를 양쪽 domain에 적용한 functional error는 명확하다. 임상 truth는 아니다. |
| direct-prior residual gap | 2.5 | inverse Navier--Stokes shape-gradient segmentation과 task-based evaluation까지 존재해, CTA용 multi-functional pullback·remainder control만 잔여 가설이다. |
| data available now | 2.5 | 공개 CTA/STL은 있으나 exact lesion linkage와 parent-domain completeness가 미검증이다. |
| independent sample size | 2.5 | 99 patient는 development/outer split에 작고 single-center다. |
| strong-baseline feasibility | 4.0 | nnU-Net, Dice+CE, boundary, clDice/cbDice와 matched task-loss baseline을 구성할 수 있다. |
| interpretable figure | 5.0 | CTA slice, surface error, adjoint influence와 WSS/pressure functional change를 한 case에서 연결할 수 있다. |
| compute/runtime feasibility | 1.5 | 현재 pinned image에 mesh/PDE stack이 없고 3D adjoint workflow도 없다. |

합계는 **27.0/40**이다. 자동 채택 기준 32/40에 못 미친다. 다만 estimand,
ISBI relevance와 시각적 검증 가능성이 분명해 **S0a/S0b에만 조건부인
shortlist 1개**로 남긴다. Method와 paper identity는 아직 선택하지 않는다.

## 5. novelty를 인정할 최소 조건

아래 네 항을 모두 만족할 때만 contribution 문장을 쓴다.

1. multi-functional signed adjoint pullback과 geometry trust region이
   first-order functional error를 어떻게 제어하는지 명시적 proposition과
   검증 가능한 remainder 조건을 제시한다.
2. same-image/same-architecture 조건에서 Dice+CE, boundary loss,
   clDice/cbDice, IAVS-style topology/applicability control과 direct frozen-
   surrogate functional loss보다 patient-level functional error가 개선된다.
3. 개선이 Dice/HD의 단순 향상으로 전부 설명되지 않는다. matched-Dice 또는
   covariate-adjusted 분석에서 functional effect와 patient-bootstrap CI를
   제시한다.
4. synthetic toy만이 아니라 held-out 실제 CTA에서 image, predicted surface,
   signed influence map과 standardized field/functional error를 연결한다.

표준 solver 자체, CMHA 적용, 새 acronym, U-Net backbone, GNN, SDF decoder,
multiple BC augmentation 또는 WSS visualization은 contribution이 아니다.

## 6. Prospective S0a · asset/runtime integrity only

실행 계약은 `configs/goal_oriented_segmentation_s0a.json`이다. S0a는 CPU,
read-only, no-payload-training audit이며 다음만 판정한다.

1. 공식 Figshare version, size, MD5와 CC BY 4.0 일치
2. 5개 CSV와 99-patient/105-lesion/44-control/6-multi-lesion unit contract
3. 105 lesion의 NIfTI–aneurysm/parent STL–aneurysm STL–table exact-ID mapping
4. NIfTI spacing/orientation와 STL unit/frame의 finite, plausible contract
5. 별도 pinned solver image의 hash, license, mesh/steady-solver와 discrete
   adjoint 또는 검증 가능한 shape-gradient capability
6. public aggregate에 identifier, private path, field와 image voxel을 쓰지 않는
   provenance boundary

현재 PyTorch image에는 SciPy, trimesh, VTK, meshio, FEniCS, JAX가 없고 host의
OpenFOAM/SU2/VMTK도 확인되지 않았다. 이 사실은 S0a 실패 결과가 아니라
**등록 전 discovery**다. 별도 solver image를 정확한 digest로 준비하고 그
상태 자체를 S0a에서 다시 검사한다. S0a pass도 model, GPU, outer test 또는
paper identity를 열지 않고 method-free S0b 등록만 허용한다.

추가 negative control에서 official SU2 8.5.0 OMP release는 steady direct
QuickStart를 exit 0으로 완료했지만 `DISCRETE_ADJOINT`는 AD support가 compile되지
않아 거부했다. 따라서 direct-only binary를 solver capability로 인정하지 않는다.
`configs/goal_oriented_segmentation_s0a_solver_preflight.json`은 exact source와
official reverse-AD build image에서 immutable SIF를 만들고, official
incompressible test mesh의 fresh direct solution을 이용한 discrete adjoint 및
finite/nonzero surface sensitivity를 먼저 확인한다. 이 preflight는 medical
asset을 읽지 않고 S0a를 평가하지 않으며, pass도 runtime pin과 단일 S0a
실행만 허용한다.

CMHA staging v1은 exact `b6b6175`의 CPU/PBS에서 exit 28로 종료됐고 verified
archive와 retained payload는 0 byte였다. Raw stdout이 없어 exact cause는
unresolved이며 S0a로 세지 않는다. Same-source v1 resubmission 대신 official
ID/size/MD5와 gate boundary를 그대로 유지하고 monolithic transfer만 64 MiB
range chunks로 바꾼 v2를 한 attempt로 prospective 등록했다. V2도 staging-only다.

## 7. S0b와 이후 kill rule

S0a가 통과한 경우에만, 결과 전에 별도 S0b를 등록한다. S0b는 development
patient의 manual surface에 smooth local normal perturbation을 주고 동일
steady solver/BC로 재해석한다. 최소 요구사항은 다음이다.

- small-perturbation에서 adjoint first-order prediction의 방향·크기와
  remeshed forward solve가 일치
- mesh refinement와 고정 BC scenario 사이에서 influence ranking이 안정적
- 비슷한 Dice/HD를 가진 perturbation 사이에 functional error가 충분히 달라
  새 task가 표준 geometry metric과 비동등
- solver/mesh failure가 특정 perturbation 또는 anatomy에 선택적으로 몰리지
  않음

Threshold, development patients, perturbation basis와 compute budget은 S0a
결과를 보기 전에 정하지 않는다. S0a가 asset/runtime에서 실패하면 dependency나
case mapping을 사후 수정해 같은 gate를 반복하지 않는다. 별도 version과 fresh
audit만 가능하다. S0b가 task non-equivalence 또는 linearization validity를
지지하지 않으면 후보를 폐기하고 architecture를 만들지 않는다.

## 8. 현재 허용·금지

허용: S0a validator/PBS wrapper 구현, exact public commit, CPU read-only run,
aggregate-only result, 실패 provenance 보존.
금지: segmentation training, GPU allocation, rupture-label selection, outer test,
adjoint 성공을 가정한 method name, contribution/paper headline, CMHA CFD summary를
ground truth field로 사용, closed branch의 checkpoint/threshold 재사용.
