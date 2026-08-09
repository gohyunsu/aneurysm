# ISBI 2027 제출 계획

> **2026-08-10 current boundary:** 가장 최근 fresh source batch는 76-case
> Aneurisk CFD, multiple-aneurysm culprit, post-treatment remnant와
> wall-enhancement endpoint를 평가했다. 최고 curvature-only local-hemodynamic
> surrogate도 31.0/40이며 companion paper가 핵심 proxy claim을 직접 점유한다.
> Release inflow는 두 population age-group waveform의 diameter scaling이지
> patient-specific measurement가 아니다. Archive/payload/P0/model/GPU는 0이다.
> 직전 direct-prior audit은 PointNeXt/GNN
> geometry + PINN hemodynamics + clinical fusion이 이미 직접 점유됐음을 확인했다.
> Patient-grouped, physically validated incremental-flow residual candidate도 joint
> asset이 없어 23.5/40으로 기각했다. Payload/P0/model/GPU는 0이다. 직전
> vascular-semantics batch의 최고 후보는 TopBrain paired CTA/MRA anatomy
> 29.5/40이며 source에서 기각했다. 공개
> 단위는 25 paired patient이고 target은 aneurysm이 아닌 48-class vascular
> anatomy다. Healthy IXI, VesselVerse, NeckSpline extension, phantom QA와 ADAM
> longitudinal 후보도 모두 32 미만이다. Payload/P0/model/GPU는 0이다. 그 이전 AneuX
> same-lesion preprocessing-orbit는
> 34/40으로 P0에 진입했지만, exact CPU-only job이 첫 tabular archive completion
> 전에 transport attempt를 소진해 scientific gate 미평가로 닫혔다. P1, selected
> primary, method, architecture, GPU, outer test와 four-page contribution은 없다.
> IAVS는 reported 641 MRA/587 annotation의 potential source지만 official
> repository가 README-only이고 release/license/payload가 0이라 watch-only다.
> 변화가 생겨도 fresh source audit 전에는 후보나 figure/result가 아니다.

최종 검토일: 2026-08-10 KST

상태: **target locked · hemodynamic–endpoint batch best 31.0/40 and all rejected · PINN rupture-status residual 23.5/40 rejected · AneuX
preprocessing-orbit P0 execution-incomplete/no verdict/no rerun · active
shortlist/selected primary problem/method/architecture/GPU 0 · not
submission-ready**

2026-08-09 open-CTA physical-coordinate 후보는 32.0/40으로 P0에 진입했지만,
exact `b437875…` one-shot 실행이 DICOM undefined-length Procedure Code Sequence를
frozen parser가 처리하지 못해 exit 1로 종료됐다. Scientific gate는 미평가이고
PixelData/STL/model/GPU access는 0이다. Parser repair/rerun 없이 후보를 닫았다.
TopAneu attachment lead는 29.0/40, terms/payload 0으로 별도 보존한다.

## 1. 제출 목표와 현재 결론

공식 목표는 IEEE ISBI 2027 regular paper다. 공식 author instruction 기준으로
review는 single-blind이며 technical content는 4쪽이다. 유료 optional fifth page는
references와 compliance statements, acknowledgments, conflict of interest에만
사용할 수 있다. 제출 마감은 **2026-10-26 23:59 USA EDT**다. 형식과 마감은
[ISBI 2027 author instructions](https://biomedicalimaging.org/2027/papers/)를
최종 제출 직전에 다시 확인한다.

현재 제출 가능한 paper identity는 없다. 최신 hemodynamic–endpoint batch의
다섯 후보는 모두 32점 미만이고, 최고 curvature-only surrogate는 직접 prior의
proxy 결론을 학습 모델로 반복할 뿐이다. 그 이전 vascular-semantics batch 여섯
후보는 모두 32점 admission line에 못 미쳤고, 그중 최고 TopBrain도 aneurysm
endpoint가 없는 강한 anatomy challenge라 독립 method identity가 아니다. 직전
OpenNeuro growth 역시 직접 Bayesian prior와 작은 종단 단위 때문에 기각됐다. DIAS
prefix 후보도 공개 release가
arterial phase를 미리 선별했고 full-sequence DSC가 minimum projection보다
0.0020 높을 뿐이며 temporal/MIP/frame-selection/early-exit/risk-control 선행이
강해 31/40으로 기각했다. AneuX orbit 후보는 official source와
direct-prior gap만 통과한 뒤, exact `42cc3c7…` `introai9` CPU/PBS P0가
`transport_attempts_exhausted`로 끝났다. Completed tabular archive와 CSV parse,
model range/central-directory/member access는 0이고 13개 check는 미평가다.
등록된 no-rerun rule로 후보를 닫았으며 P1, method와 figure/result를 열지 않는다.
Cycle-functional WSS도 P0 execution-incomplete로 닫혔고 P1은 열리지 않았다. Open-CTA grid-commutation 문제는
asset gate를 평가하지 못했고 P1도 열리지 않았다. Partial/missing-BC AURORA, Aneumo
irregular-3D, cross-protocol 4D-flow, RSNA mixed-granularity lesion-set과
goal-oriented hemodynamic segmentation을 모두 실패 또는 부적격 이력으로
보존한다. 마지막 후보는 exact public source
`ef547a4ccb71fa45b4a43e67c0939e2701ebfc11`의 CMHA asset component에서
**5/9 failed**였고 S0a는 `not_evaluated`다. Solver v2, S0b, model, GPU와 outer
test는 열리지 않았다.

TopAneu는 실제 CTA/MRA, 409 patient와 52-class location이라는 장점이 있지만
challenge 자체가 joint location/segmentation task를 점유하고 ARAN·vessel-aware
attention·hierarchical taxonomy가 직접 경쟁한다. 남은 attachment-consistency
가설은 payload semantics와 ambiguity reference를 확인한 method-free audit 뒤에도
independent-head failure가 남아야만 후보가 된다.

Open-CTA 후보의 direct prior에는 spacing-aware resampling, continuous implicit
segmentation, resolution-invariant latent, probabilistic finite-set detection,
variable-cardinality LesionDETR와 aneurysm shape/topology learning이 포함된다.
따라서 resampler, coordinate decoder, query set 또는 topology loss를 붙이는
것은 contribution이 아니다. P1 뒤에도 남는 joint cardinality–surface–morphometry
commutation gap과 strong direct-baseline 우위가 함께 있어야 ISBI method identity를
검토한다.

이 결과는 “좋은 아이디어인데 데이터만 불편하다”는 뜻이 아니다. Frozen
estimand에 필요한 105-lesion image–surface–table linkage를 공개 자산에서
재현할 수 없으므로, 해당 version의 검증 가능한 연구 문제 자체가 성립하지
않는다는 뜻이다. Mapping을 추측하거나 수작업으로 복구해 같은 후보를 살리지
않는다.

## 2. 현재 후보를 판단하는 순서

이후의 모든 새 후보는 이름이나 architecture가 아니라 다음 다섯 증거를
순서대로 갖춰야 한다. 닫힌 AneuX P0를 이 ladder의 진행 중 후보로 세지 않는다.

1. **Biomedical-imaging question**: 입력 영상, 관측 단위, target과 실제 실패
   비용을 한 문장으로 정의한다.
2. **Task-unit audit**: patient/case/lesion/acquisition 중 독립 표본 단위를 원
   자료와 asset으로 일치시킨다.
3. **Direct-prior residual gap**: 가장 가까운 논문이 이미 점유한 문제·보장·평가를
   제거하고 남는 algorithmic gap을 적는다.
4. **Method-free adequacy**: 새 model 없이도 target variability, annotation
   reliability, baseline discriminability와 sample size가 효과를 식별할 수 있는지
   측정한다.
5. **Compute-matched feasibility**: strong baseline, 5-seed 또는 repeated split,
   interpretable figure와 outer test를 마감 전에 완주할 수 있어야 한다.

한 항목이라도 실패하면 method를 붙이지 않는다. 이전 후보의 data, checkpoint,
threshold나 unreported result로 새 후보 점수를 높이지 않는다.

## 3. Fresh evidence ladder

### P0 · problem and asset integrity

- 1차 논문, 공식 dataset record, license와 raw manifest를 함께 감사한다.
- 데이터 접근 전에 candidate question, independent unit, allowed target,
  prohibited interpretation과 kill rule을 config로 고정한다.
- 파일명 유사성, row order와 사람의 사후 추측으로 patient/lesion을 연결하지
  않는다.
- P0 pass는 P1 등록만 허용하고 architecture나 GPU를 열지 않는다.

### P1 · method-free task adequacy

- target의 within-unit repeatability와 between-unit signal을 분리한다.
- trivial image-only, morphology-only, prevalence-only control이 task를 이미
  포화하는지 확인한다.
- clinically suggestive label을 prospective risk로 바꾸지 않는다.
- negative 또는 non-discriminative이면 후보를 닫는다.

### P2 · baseline and estimand freeze

- primary estimand, patient-level split, primary/secondary metric, failure handling,
  seed와 confidence interval을 결과 전에 고정한다.
- 가장 가까운 direct method, strong task baseline, capacity/compute-matched
  baseline과 simple control을 포함한다.
- outer test는 model selection과 완전히 분리한다.

### P3 · bounded validation-only development

- test를 봉인한 채 최대 repair round와 총 GPU budget을 미리 정한다.
- 각 round는 한 개의 attribution-supported failure hypothesis만 검사한다.
- 모든 variant, failed run, selection rule과 compute를 기록한다.
- 개발 성공은 confirmatory pass가 아니다.

### P4 · fresh prospective evidence

- disjoint/fresh split과 최소 5 seeds 또는 반복 nested split으로 실행한다.
- primary effect size와 patient-bootstrap CI가 strong baseline 대비 양수여야 한다.
- calibration, safety/abstention, failure subgroup과 compute를 함께 보고한다.
- 실패하면 threshold, seed, estimand를 고치지 않고 해당 version을 닫는다.

## 4. 방법론을 선택하는 기준

현재 GNN 기반도, U-Net 기반도 아니다. Architecture는 P1 이후 관찰된 실패
구조가 정한다. Irregular surface relation이 핵심이면 graph/mesh encoder를,
voxel localization이 핵심이면 3D CNN/ViT를, continuous acquisition operator가
핵심이면 neural field/operator를 검토할 수 있다. 그러나 GNN, transformer,
diffusion, foundation feature, physics loss, uncertainty와 새 acronym은 독립
novelty가 아니다.

Contribution은 다음 세 문장이 각각 증거를 가질 때만 쓴다.

- 기존법이 실패하는 구체적 biomedical-imaging condition을 새 estimand로
  정의했다.
- 그 condition을 직접 다루는 algorithmic mechanism과 분석 가능한 성질을
  제시했다.
- Fresh outer evidence에서 strong direct baseline보다 재현 가능한 이득을
  보였다.

## 5. ISBI 4쪽 구조

Positive P4 evidence 전에는 원고 구조만 유지하고 claim 문장을 채우지 않는다.

| 부분 | 권장 분량 | 역할 |
|---|---:|---|
| Introduction | 0.55쪽 | 영상 문제, direct gap, 검증된 contribution만 제시 |
| Related work | 0.30쪽 | 가장 가까운 두세 계보와 차이를 압축 |
| Method | 1.10쪽 | estimand, architecture, objective와 보장/직관 |
| Experiments | 1.25쪽 | cohort, split, baselines, metrics, ablation, statistics |
| Results/Discussion | 0.65쪽 | primary table, failure analysis, 범위와 한계 |
| Conclusion | 0.15쪽 | 주장 범위를 넘지 않는 한 문단 |

Table은 모두 `method / supervision / data access / compute / primary metric /
95% CI` 열 순서를 공유한다. 숫자의 precision, best/second-best 표시와 실패
표기 규칙을 통일한다. AUROC만으로 결론 내리지 않고 task에 맞는 proper score,
calibration과 patient-level CI를 포함한다.

Figure는 최소 두 개를 계획한다.

1. 입력 영상 → 핵심 representation/uncertainty → output → 평가 estimand의 인과
   흐름을 보여주는 architecture figure
2. 실제 held-out 의료영상, reference/prediction, 오류 또는 uncertainty, 관련
   3D surface/field와 quantitative functional을 같은 case에서 연결하는
   interpretable figure

실제 의료영상을 사용할 수 없는 후보는 ISBI headline 후보로 자동 선택하지
않는다. Synthetic/toy visualization은 mechanism 보조에만 둔다.

## 6. 일정과 go/no-go

| 날짜 | 결정점 | 통과하지 못하면 |
|---|---|---|
| 2026-08-09 | Goal-oriented S0a-A exact run | 5/9 fail로 후보 종료; solver v2 없음 |
| 2026-08-09 | Open-CTA P0-C one-shot asset audit | execution-incomplete/no verdict로 후보 종료; parser repair/P1 없음 |
| 2026-08-16 | Fresh P0 problem/asset audit | 독립 후보가 없으면 method/GPU 계속 금지 |
| 2026-08-30 | P1 method-free adequacy | 후보 종료 또는 baseline/estimand freeze |
| 2026-09-13 | P2와 bounded P3 등록 | outer test 봉인 불가 시 중단 |
| 2026-09-27 | Development freeze | strong baseline과 positive validation 부재 시 P4 금지 |
| 2026-10-11 | Fresh P4 complete | 양수 primary evidence 부재 시 ISBI 제출 보류 |
| 2026-10-18 | 4-page manuscript freeze | claim–table–figure 불일치 시 claim 축소 |
| 2026-10-26 | Official deadline | 형식·compliance 최종 감사 뒤 제출 |

마감 때문에 gate를 낮추지 않는다. ISBI 2027에 약한 논문을 억지로 제출하는
것보다 실패를 보존하고 다음 검증 가능한 후보를 만드는 것이 우선이다.

## 7. 현재 허용·금지

허용:

- 새 problem의 primary-source/asset/task-unit audit
- open-CTA P0 execution-incomplete provenance와 실패 경계 보존
- 사용자의 명시적 TopAneu terms 수락 뒤 prospectively registered CPU/read-only P0-T
- 기존 실패의 public aggregate, protocol, site와 private manuscript 동기화
- P0 전에 실행하지 않는 비교표·claim matrix 정리

금지:

- Goal-oriented S0a mapping repair 또는 rerun
- 에이전트의 TopAneu 가입·terms 수락·무등록 payload download
- Solver preflight v2, S0b, segmentation model과 GPU job
- P0-C/P1 전에 open-CTA model, architecture, GPU 또는 outer-test config 작성
- Open-CTA frozen parser repair, same-contract rerun, P0r 또는 P1 등록
- Closed checkpoint/threshold/outer-test 재사용
- Cross-sectional rupture status를 future rupture risk로 표현
- 실제 positive evidence 없이 method name, architecture figure 또는 contribution
  문장을 submission-ready 상태로 승격
