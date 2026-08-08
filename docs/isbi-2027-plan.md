# ISBI 2027 submission plan

최종 검토일: 2026-08-09 KST
상태: **target locked · not submission-ready · conditional problem shortlist 1 ·
S0a staging v1/v2와 solver preflight v1 execution-incomplete · CMHA archive
integrity 3/3 확인 · source-server asset component preregistered · method,
architecture, GPU training, outer test와 paper identity 미선정**

## 1. 공식 제출 계약

목표는 IEEE ISBI 2027 archival four-page regular paper다.

- 제출 마감: **2026-10-26 23:59 USA EDT**
- 심사: **single blind**
- 첫 4쪽: abstract를 포함한 모든 technical content, figure와 table
- 선택적 5쪽: references, `Compliance with Ethical Standards`,
  acknowledgments와 conflict-of-interest statement만 허용; USD 200 추가 비용
- full paper만 proceedings와 oral-presentation 심사 대상
- open human-derived data를 쓰더라도 license뿐 아니라 필수 ethical-compliance
  statement와 이해상충 문구를 원고에 명시

공식 출처는 [ISBI 2027 author instructions](https://biomedicalimaging.org/2027/papers/)와
[conference dates](https://biomedicalimaging.org/2027/)다. Template가 갱신되면
private paper 저장소에서 공식 배포본을 다시 pin하고 compile audit를 수행한다.

## 2. 냉정한 현재 판정

현재 제출 가능한 논문은 없다. 선택된 primary method도 없다.

유일한 조건부 problem shortlist는 **goal-oriented hemodynamic
segmentation**이다. 같은 CTA에서 얻은 manual domain과 predicted domain에
동일한 고정 solver·boundary-condition scenario를 적용할 때, 여러 사전 정의
functional의 오차를 줄이는 segmentation을 학습할 수 있는지를 묻는다. 현재
cold score는 `27.0/40`으로 자동 선택 기준 `32.0/40`보다 낮다.

남아 있는 gap 가설은 다음 결합에 한정한다.

> CTA 경계의 signed normal displacement를 여러 고정 PDE functional의
> discrete-adjoint shape gradient로 pull back하고, 검증된 trust region과
> remainder control 안에서 학습했을 때, 표준 segmentation·topology·task-loss
> baseline보다 held-out patient의 standardized functional error가 감소하는가?

이는 아직 method, proposition, architecture 또는 contribution이 아니다.
다음 요소는 이미 direct prior 또는 engineering component이므로 단독 novelty로
주장하지 않는다.

- segmentation→CFD pipeline과 segmentation-induced CFD variability
- differentiable PDE, adjoint·shape derivative와 inverse-flow segmentation
- Image2Flow식 image→mesh/field prediction
- Dice/CE, boundary loss, clDice/cbDice와 CFD-applicability loss
- U-Net, nnU-Net, GNN, implicit SDF와 새 acronym
- task-based downstream segmentation evaluation 자체

이전 AURORA partial/missing-BC operator, Aneumo 3D, 4D-flow와 RSNA
mixed-supervision 후보는 모두 실패·미완료·기각 이력이다. 이를 현재 논문의
positive evidence나 ablation으로 재사용하지 않는다. 상세 이력은
[`research-direction.md`](research-direction.md)와 public result manifests에
보존한다.

## 3. 현재 evidence ladder

각 단계는 다음 단계의 **등록 권한**만 연다. 이전 실패를 relabel하거나 같은
source를 현장에서 고쳐 다시 제출하지 않는다.

### S0a-A · source-server asset component · 다음 실행

CMHA staging v1/v2는 둘 다 첫 verified payload 전에 exit 28이었고, solver
preflight v1은 reverse-AD runtime·probe 전에 exit 1이었다. 세 실행 모두 S0a를
평가하지 않았다. 같은 source와 추가 Figshare transport는 반복하지 않는다.

이후 `introai9`에서 발견한 세 official archive는 byte size와 MD5가 3/3
일치했다. 이 discovery는 CSV row, identifier, NIfTI/STL header, voxel과 field를
열지 않았으므로 S0a pass가 아니다.

다음 one-shot CPU/PBS run은
`configs/goal_oriented_segmentation_s0a_asset_component.json`의 9개 check를
모두 평가한다.

1. 세 archive size/MD5와 다섯 statistical CSV member
2. 99 patient, 105 lesion, 44 control, 6 multi-lesion-patient unit
3. row position·prefix·filename similarity 없는 explicit identifier linkage
4. 105 CTA–parent/aneurysm STL–aneurysm STL triplet
5. qform/sform, spacing, mm scale와 identity/LPS→RAS containment
6. identifier/private path/voxel/field를 쓰지 않는 aggregate boundary
7. rupture label, model, GPU와 outer-test access 0

Scientific check 하나라도 실패하면 현재 후보를 닫는다. 실행 자체가 중단되면
`not_evaluated`로 보존하며 같은 public source를 재제출하지 않는다. 9/9도 S0a
pass가 아니라 한 번의 별도 no-runtime-network solver preflight v2 등록만
허용한다.

### S0a-P · solver runtime · asset 9/9일 때만 등록

Solver v2는 medical data를 읽지 않고, dependency를 실행 중 내려받지 않는
immutable normal+reverse-AD runtime을 만든다. Fresh incompressible direct solve,
discrete adjoint와 finite/nonzero surface sensitivity를 확인하고 image SHA,
license, source/TestCases commit과 probe output을 고정한다. V2 contract는 S0a-A
결과 뒤 별도 public commit에서 prospective하게 등록한다.

Asset 9/9와 solver runtime pass가 모두 있어도 기존 11-check S0a 전체를 별도
all-or-none aggregate로 판정해야 한다. S0a pass는 method-free S0b 등록만
허용한다.

### S0b · task adequacy · S0a pass일 때만 등록

Development patient의 manual surface에 smooth local normal perturbation을 주고
동일 solver/BC로 remeshed forward difference를 계산한다. 결과 전에 patient,
functional, perturbation basis, mesh levels, thresholds와 compute budget을
고정한다.

- adjoint first-order prediction의 signed direction·magnitude가 small-perturbation
  forward difference와 일치
- remainder가 미리 정한 trust region 안에서 제어됨
- influence ranking이 mesh refinement와 고정 BC scenario에 안정적
- 비슷한 Dice/HD perturbation 사이에도 functional error가 충분히 달라 표준
  geometry metric과 task가 비동등
- solver/meshing failure가 특정 anatomy나 perturbation 방향에 선택적으로 집중되지 않음

하나라도 실패하면 architecture를 만들지 않는다.

### Baseline-first development · S0b pass일 때만 등록

먼저 patient-disjoint split에서 다음 compute-matched baseline을 고정한다.

- 3D nnU-Net의 Dice+CE 기준선
- boundary-distance objective
- clDice/cbDice topology control
- IAVS-style CFD-applicability control
- direct frozen-surrogate functional loss
- 가능하면 adjoint magnitude만 쓰는 unsigned control과 single-functional control

그 뒤에만 residual gap을 구현하는 candidate interface를 등록한다. Backbone
교체는 novelty가 아니며, 동일 image preprocessing·architecture capacity·training
budget에서 loss/interface 차이를 비교한다.

Development repair는 test를 봉인한 상태에서만 허용한다. 시작 전에 총 GPU
budget, 최대 repair round, variant 수와 selection rule을 고정한다. 각 round는
validation attribution이 지지하는 실패 가설 하나만 바꾸며 모든 variant와
negative result를 남긴다. 선택된 candidate는 fresh seed 또는 disjoint split의
prospective re-entry를 거쳐야 하고 기존 실패를 pass로 바꾸지 않는다.

### Frozen outer test

Outer test는 architecture·loss·threshold·seed·representative-case rule을 모두
고정한 뒤 한 번만 연다. 최소 다섯 seed와 patient-level bootstrap CI를 사용한다.

Primary evidence:

1. strongest eligible baseline 대비 patient-level standardized multi-functional
   error 차이와 95% CI
2. full-domain Dice/HD95/surface distance가 악화되지 않는지
3. matched-Dice 또는 사전 정의 covariate-adjusted 분석 뒤 남는 functional gain
4. first-order trust-region coverage와 held-out remainder

Secondary evidence:

- functional별 signed error와 worst-functional error
- mesh/BC sensitivity, solver failure rate와 runtime
- calibration이 실제 estimand일 때만 calibration endpoint

CMHA 공개 hemodynamic summary를 voxel/field ground truth처럼 사용하지 않는다.
Manual/predicted domain 양쪽에 같은 standardized simulator를 적용한 **research
utility**만 주장하며 clinical utility, rupture risk와 biological truth를
주장하지 않는다.

## 4. 논문 정체성의 승인 조건

다음 네 항목이 함께 양수여야만 contribution 문구를 연다.

1. multi-functional signed pullback과 trust-region remainder를 연결하는 명시적
   algorithm/proposition
2. direct prior와 strong baseline을 넘는 held-out functional improvement
3. 그 개선이 단순 Dice/HD 향상만으로 설명되지 않는 patient-level 분석
4. 실제 CTA slice, manual/predicted 3D surface, signed influence와 functional
   change를 연결한 predeclared qualitative example

하나라도 부족하면 이름을 붙여 novelty를 보충하지 않고 논문 identity를
`unsupported`로 유지한다.

## 5. ISBI 4쪽 구성 · positive outer test 이후에만 활성화

| 지면 | 역할 | 반드시 답할 질문 |
|---|---|---|
| Title + abstract · 0.30쪽 | 문제·방법·데이터·핵심 effect를 한 번에 요약 | 무엇이 새롭고 얼마나 개선됐는가? |
| Introduction · 0.55쪽 | direct prior와 단 하나의 residual gap | 왜 Dice나 일반 task loss로 충분하지 않은가? |
| Method · 1.05쪽 | signed pullback, trust region, proposition과 training objective | 어떤 조건에서 functional error를 제어하는가? |
| Data/protocol · 0.75쪽 | CMHA provenance, patient split, solver, baselines와 통계 계약 | leakage와 simulator asymmetry를 어떻게 막았는가? |
| Results · 1.15쪽 | 한 main table, 한 해석 figure, 최소 ablation | 결과가 contribution의 각 고리를 지지하는가? |
| Limitations/conclusion · 0.20쪽 | standardized CFD research utility와 실패 가능 범위 | 무엇을 임상적으로 주장하지 않는가? |

중복을 막기 위해 Introduction에는 실패 연대기를 넣지 않고, Method에는
backbone 설명을 최소화한다. Table row마다 하나의 비교 질문만 두고 모든
primary effect에는 환자 단위 CI를 붙인다.

권장 figure는 두 개를 넘지 않는다.

- **Figure 1:** CTA → boundary displacement → signed multi-functional adjoint
  pullback → trust-region loss → predicted surface/functional evaluation의 인과 흐름
- **Figure 2:** 사전 정의된 대표-case 규칙으로 고른 CTA slice, manual/predicted
  surface error, signed influence map과 functional change의 정합 패널

Main table은 `Method | Geometry | Topology | Task signal | Dice | HD95 |
Functional error | Δ vs strongest | 95% CI | Fail rate`의 고정 열을 사용한다.
표·그림·본문이 같은 claim을 세 번 반복하지 않도록 각각 비교, 해석, 한계를
나누어 맡긴다.

## 6. 일정과 kill rule

| Date (KST) | Deliverable | Kill rule |
|---|---|---|
| 2026-08-09 | source-server S0a-A exact public source freeze | CSV/header 접근 전 config·code·CI가 고정되지 않으면 제출 금지 |
| 2026-08-10 | S0a-A one-shot result | scientific fail이면 후보 종료; incomplete면 same-source rerun 금지 |
| 2026-08-14 | conditional solver v2 또는 candidate closure | asset 9/9 없이는 solver v2 등록 금지 |
| 2026-08-21 | S0a/S0b task-adequacy decision | 11/11 또는 linearization/non-equivalence 실패 시 method 없음 |
| 2026-09-03 | baseline eligibility와 development budget freeze | strong baseline/expanded patient split이 불명확하면 full paper 중단 |
| 2026-09-10 | candidate method/config freeze | 이후 outer-test architecture·loss search 금지 |
| 2026-09-24 | five-seed outer test 완료 | gate 실패 시 relabel·threshold/seed repair 금지 |
| 2026-10-08 | 공식 template 4쪽 draft + figure/table audit | unsupported 문장·technical overflow 삭제 |
| 2026-10-19 | internal paper freeze | provenance, ethics 또는 evidence gap이 남으면 미제출 |
| 2026-10-26 | ISBI submission | 23:59 USA EDT 이전 제출 |

일정은 성공을 가정하지 않는다. Early gate가 실패하면 GPU와 원고 수선을 멈추고,
모든 시도와 negative result를 public/private provenance에 보존한다.
