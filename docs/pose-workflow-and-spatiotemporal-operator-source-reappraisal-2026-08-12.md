# Pose workflow와 spatiotemporal operator 재평가

> **판정 · 2026-08-12:** 제안된 surface-vector 문제의식은 과학적으로
> 타당하지만 active paper identity가 아니다. 새로 확인한 공개 pose 자산은
> 환자 단위가 비교적 명확한 반면 핵심 task가 이미 직접 점유돼 있고, 새
> spatiotemporal/WSS 구현은 direct prior를 강화할 뿐 transient-vector task
> 자산을 만들지 않는다. 여섯 후보의 점수는
> **29.0/28.5/27.0/26.0/25.5/21.5**이며 모두 비보상형 gate에서 기각한다.
> E0/P0/P1, method, architecture, server query, PBS/GPU, outer test와 paper
> claim은 0이다.

## 1. 전달된 분석에서 채택한 것과 수정한 것

채택한 핵심은 다음과 같다.

1. Cartesian field error가 작아도 signed critical point와 시간 궤적이 보존된다는
   보장은 없다. 이는 반증 가능한 좋은 **평가 가설**이다.
2. 안정성 → field-error-matched failure → bounded development → fresh
   confirmation → 외부 해석의 순서는 타당하다.
3. `115645.ECE-util1`은 `E`/exit 2, 0/10 no-verdict이며 같은 contract를
   수리·재실행하지 않는다.
4. GNN, Hodge, equivariance, topology loss의 이름이나 조합은 novelty가 아니다.

그러나 “좋은 architecture와 성능이 확보되면 ISBI application contribution이
될 수 있다”는 문장은 필요조건만 말한다. 현재에는 그 architecture를 평가할
식별 가능한 공개 transient-vector cohort와 독립 family split이 없고, 일반적인
spatiotemporal mesh operator의 직접 선행도 추가 확인됐다. 따라서 **가능성**을
active topic이나 compute authority로 바꾸지 않는다.

## 2. 공개 weak-pose 자산: 실제로 좋은 점

[DeepAnePose official GitLab](https://gitlab.inria.fr/yassis/DeepAnePose)는 exact
head `40042fa4290fe2e36a30dfb100b514cbe2fbaea2`에서 MICCAI 2023 논문의 코드,
Lausanne 공개자료용 두 점 `P1`/`P2` annotation과 다섯 fold를 제공한다. 원 논문은
두 dataset의 416 patient/317 aneurysm에서 localization, size, main-axis
orientation과 reformatted plane을 직접 다룬다. 출처가 보고한 median localization
0.48 mm, orientation 12.27°, AP 76.60%, sensitivity 82.93%, 0.44 FP/case는
AURORA가 재현한 결과가 아니다.

Repository metadata를 method-free로 세면 다음과 같다.

- `selected_patients.txt`: 270 session, 270 unique subject identifier
- positive annotation JSON: 140개
- annotation에 기록된 lesion: 164개, positive subject당 1--3개
- fold 1/2/4: train 216, test 54; fold 3: train 217, test 53; fold 5:
  train 215, test 55
- 각 fold 내부 train/test overlap 0
- 다섯 test union 270, 각 selected subject는 test에 정확히 한 번 등장
- explicit validation split 0
- tracked checkpoint 0, repository-level `LICENSE` file 0

이는 예전의 모호한 lesion-file collection보다 훨씬 좋은 독립단위 계약이다.
하지만 자산의 품질과 새 연구문제의 novelty는 다른 축이다. DeepAnePose 자체가
weak two-point/sphere annotation, localization, diameter/axis pose와 reformatted
view를 이미 직접 점유한다. [OpenNeuro ds003949](https://openneuro.org/datasets/ds003949/versions/1.0.1)은
CC0 공개영상이지만, repository의 P1/P2 한 세트는 독립적인 dense sac/neck truth,
여러 reader의 pose 분포, annotation 시간 또는 reader action이 아니다. 후속
weakly supervised multi-task segmentation도 obvious weak-to-dense extension을
추가로 점유한다.

## 3. 새 direct prior가 surface-vector 제안에 미치는 영향

### Graph Physics

[graph-physics](https://github.com/DonsetPG/graph-physics/tree/e4ac523d749b126f504665fb6270fcb91ac3cbd2)와
[arXiv:2605.01542](https://arxiv.org/abs/2605.01542)는 MeshGraphNet,
Transolver와 Transformer 계열을 물리 mesh data에 적용하며 brain-aneurysm
subtask를 포함한다. Multi Node Prediction, temporal predictor--corrector,
3D rotary positional encoding과 WSS/pressure task가 이미 제시된다. AURORA가
그 결과를 재현하지 않았고 repository에 명시적 license가 없지만, generic
spatiotemporal mesh operator와 temporal correction을 새 architecture identity로
주장할 수 없게 만드는 direct prior다.

### Aneumo WSS Transolver

[exact repository](https://github.com/IsaacLin247/aneurysm-wss-transolver/tree/3087fc9b8370ad39db85db9a61315bb34bf43cbb)는
Aneumo steady synthetic cases에서 Transolver/DeepONet을 비교한다. 중요한
경계는 dataset이 `p,U`만 제공하고 WSS는 near-wall velocity gradient의
second-order least-squares reconstruction으로 **파생한 magnitude**라는 점이다.
Repository에는 dataset, checkpoint와 exact completed fold outputs가 없다.
출처가 기록한 velocity/WSS 성능은 AURORA result가 아니며, phase-resolved
tangent vector, signed critical point와 worldline reference도 아니다.

### Geometry-aware GNN과 mechanistic clot model

[EXPIGEO exact head](https://github.com/mohamedaminelayachi/EXPIGEO/tree/b28736842ec521641ea9389e4a9a58bccc5616f3)는
IntrA point cloud에서 ray/centreline/radius 기반 interior geometry를 GNN에
추가하고 explainability까지 직접 다룬다. Public code는 MIT지만 checkpoint와
frozen family-grouped split은 없고 file-level construction의 독립단위는 별도
검증이 필요하다. 출처가 보고한 accuracy 98.41%, F1 0.9589는 재현하지 않았다.

[HyCTOR exact head](https://github.com/danilodurs/HyCTOR/tree/31f69e6c0953b4d1d0f52856cd4d16efb9248556)는
2026 thrombus model의 3D extension을 구현하지만, learned components는
명시적으로 untrained placeholder이고 patient roles는 heuristic placeholder다.
원 논문도 두 idealized geometry를 사용한다. Mechanistic relevance는 있지만
patient task asset이나 validated AURORA control이 아니다.

암호화된 784-case growth bundle은 key, row/split/source contract가 공개되지 않아
검증할 수 없고, Slicer weak-annotation/review 도구의 sample은 synthetic phantom이다.
어느 것도 새 E0를 식별하지 않는다.

## 4. 비보상형 six-way screen

축 순서는 clinical importance, target identifiability, residual novelty, asset
readiness, effective independent unit, strong-baseline feasibility,
interpretable evidence, ISBI schedule fit이다. 총점 32/40과 함께 target 3.5,
novelty 2.5, asset 3.0, unit 3.0, baseline 3.0을 모두 넘어야 한다.

| 후보 | 8축 점수 | 합계 | 판정 |
|---|---|---:|---|
| patient-wise weak-pose benchmark repair | 4.0/4.0/1.0/4.0/4.5/5.0/4.0/2.5 | **29.0** | 원 task와 folds가 direct prior; benchmark repair는 paper identity가 아님 |
| axis-symmetry-aware selective pose sets | 4.0/3.0/1.5/3.5/4.5/4.5/4.5/3.0 | **28.5** | single annotation으로 pose uncertainty truth 미식별, generic selective prior |
| weak-pose external transport to ds005096 | 4.0/2.5/1.5/2.5/4.0/4.5/4.5/3.5 | **27.0** | external set에 expert P1/P2 pose reference 없음 |
| derived-WSS reference uncertainty | 4.0/3.0/1.0/2.5/2.5/4.5/5.0/3.5 | **26.0** | derived steady magnitude와 transient tangent-vector target이 다름 |
| family-disjoint EXPIGEO explainability | 3.5/3.0/0.5/3.0/2.0/5.0/4.5/4.0 | **25.5** | method와 explanation이 direct prior, family semantics unresolved |
| structure-faithful transient WSS operator | 4.0/2.0/1.0/1.0/1.0/5.0/5.0/2.5 | **21.5** | transient-vector cohort/family/structure reference 0, operator lineage crowded |

높은 점수가 낮은 novelty를 보상하지 않는다. 최고 29.0도 기각하며 conditional
lead를 만들지 않는다.

## 5. architecture에 대한 최종 판정

Oriented edge 1-form, SE(3)-equivariant message passing, discrete Hodge
decomposition, periodic temporal operator와 structure losses는 **향후 failure가
관측됐을 때 비교할 control family**로는 합리적이다. 현재 선택된 architecture가
아니며 각각이나 조합을 contribution으로 쓰지 않는다. 먼저 필요한 것은 모델이
아니라 다음 observable을 갖춘 새 material evidence version이다.

1. phase-resolved tangent WSS vector와 units/mesh/BC/solver schema
2. patient 또는 generating-family 단위의 immutable manifest와 held-out split
3. mesh/tolerance/perturbation에 대한 signed-degree와 track stability
4. 같은 field error에서 Cartesian/tangent/equivariant/Hodge baseline의 구조 실패
5. validation-only development 뒤 untouched confirmation family

이 조건이 충족되더라도 fresh source gate가 허용하는 것은 method-free E0/P0뿐이다.
그 failure가 안정적으로 확인된 다음에만 최소 원인-연결 architecture를 고른다.
임상 rupture risk나 treatment benefit으로 확장하지 않고, 실제 CFD surface에서는
동일 좌표계·색상 범위로 field, critical point와 track을 비교한다.

## 6. 운영 결론

- surface-vector: `closed_until_whitelisted_material_release` 유지
- DeepAnePose: useful public source/control, active paper identity 아님
- source-watch v16: 27개 frozen state, 새 3개 code source는 direct-prior
  baseline-feasibility re-audit만 요청
- `115645`: repair/rerun 없음
- scientific server query/transfer/PBS/GPU: 0
- future gate-authorized execution: `introai9` PBS only
- `junjinyong`: 접속·조회·전송·제출·모니터링 금지
- manuscript title/abstract/method/result/table/figure/claim: 변경 없음

