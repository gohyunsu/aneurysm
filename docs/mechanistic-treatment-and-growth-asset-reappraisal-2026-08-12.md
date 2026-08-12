# 치료 기전·성장·outcome 결합 자산 재평가

> **판정 · 2026-08-12 · schema 11.2**  최신 문헌은 coil mechanics, 정규화된
> quantitative angiography(QA), 6개월 occlusion, longitudinal growth,
> amplified-MRI wall motion과 particle transport를 각각 다룬다. 그러나 이들을
> 동일 환자·동일 병변에서 잇는 공개되고 versioned된 자산은 확인되지 않았다.
> 여섯 후보의 최고점은 27.5/40이며 모두 total 또는 critical floor를 실패한다.
> Active lead, E0/P0/P1, method, architecture, scientific server, PBS/GPU,
> outer test와 paper claim은 0이다.

## 1. 왜 이 질문을 다시 보았는가

Surface-vector 가설은 field error가 낮아도 signed critical point와 cardiac-cycle
worldline이 훼손될 수 있다는 타당한 조건부 문제를 제시한다. 다만 그것만으로는
환자에게 중요한 치료 또는 성장 endpoint와 연결되지 않는다. 이번 audit은 그
가설을 재활성화하지 않고, 다음의 더 직접적인 질문을 검토한다.

> **시술 전 형상과 virtual-device mechanics, 시술 직후 angiographic response,
> 그리고 사전에 정한 시점의 실제 occlusion 또는 growth를 같은 병변에서 연결하는
> 실행 가능한 공개 자산과 미점유 estimand가 존재하는가?**

이 질문은 단순한 GNN/Hodge/equivariance 조합보다 훨씬 설득력이 있다. 성공한다면
모델이 예측하는 물리량이 실제 치료 결과와 어떻게 연결되는지를 검증할 수 있기
때문이다. 그러나 현재 답은 **아니다**이다. 방법론이 아니라 동일-patient join과
target time이 병목이다.

## 2. 최신 1차 출처가 실제로 제공하는 것

| Source | Source가 보고한 범위 | AURORA가 넘지 않는 경계 |
|---|---|---|
| [Coil-mechanics simulation](https://doi.org/10.1063/5.0312971) | clinical morphology를 매개로 500 synthetic sac을 만들고 virtual coil deployment의 reaction force, elastic energy와 contact pressure를 예측. Source surrogate의 reported reaction-force `R²=0.74`, elastic-energy `R²=0.68` | 500 synthetic geometry를 500 patient로 세지 않는다. 공개 geometry, coil sequence, source patient mapping, 실제 recurrence/occlusion join과 supplement를 확인하지 못했다. Source 결과는 AURORA result가 아니다. |
| [Injection-standardized QA](https://doi.org/10.1136/jnis-2025-023416) | flow-diverter 치료 458 patient의 angiogram과 6-month occlusion을 사용. Parent-artery input deconvolution/reconvolution으로 injection bias를 줄인 뒤 DNN과 LIME을 평가. Source reported AUROC는 0.60에서 0.79로 증가 | Injection correction, QA→6-month occlusion과 explainability는 direct prior다. 공개 patient row, angiogram, immutable split, acquisition curve와 lesion-device join은 확인되지 않았다. |
| [Matched longitudinal paraclinoid study](https://doi.org/10.3174/ajnr.A9125) | 34 aneurysm/17 matched pair, 병변당 3 CTA, 평균 4.10년 follow-up에서 morphology와 CFD를 분석 | 34 aneurysm을 34 independent pair로 세지 않는다. 공개 image/mesh/CFD/growth-adjudication manifest가 없고 “possible predictor”를 외부 검증된 future predictor로 바꾸지 않는다. |
| [Amplified-MRI wall motion](https://doi.org/10.1136/jnis-2025-023486) | growing 6, stable 6의 matched 4D-flow MRI에서 wall-motion heterogeneity와 directional WSS-gradient variability의 연관을 보고 | 12-case retrospective association은 중요한 mechanistic prior지만 public field–wall-motion–growth asset이나 independent external test가 아니다. Causal rupture mechanism으로 과장하지 않는다. |
| [Automated initiation workflow](https://doi.org/10.1016/j.cmpb.2026.109245) | 42 case의 semi-automated centerline+CFD workflow. 최초 실패 5건은 manual reconstruction으로 해결 | “42/42 autonomous success”가 아니다. 공개 casewise initial-failure mask, healthy pre-initiation reference 또는 future initiation label을 확인하지 못했다. |
| [Particle-transport DEM–CFD](https://doi.org/10.1016/j.compbiomed.2026.111884) | 하나의 idealized aneurysm에서 28 particle configuration을 분석하고 5개 무차원 수로 regime map을 제시 | 28 configuration은 28 anatomy/patient가 아니다. Clinical delivery, thrombus, occlusion 또는 patient outcome 자산으로 재해석하지 않는다. |

위 수치는 원 논문의 보고값이며 AURORA가 재현한 결과가 아니다. 이번 update는
Europe PMC의 공식 bibliographic/abstract metadata와 공개 publisher page만 읽었다.
Subscription full text, supplement, patient image, mesh, waveform, device deployment,
clinical row와 server-side dataset을 열거나 내려받지 않았다.

## 3. 왜 자연스러운 논문 identity가 아직 성립하지 않는가

가장 매력적인 잔여 질문은 다음과 같다.

> **Can patient-specific virtual coil mechanics and injection-invariant immediate
> angiographic response jointly predict prespecified follow-up occlusion?**

이 질문은 반응력이 작은 모델 이름이나 loss 조합보다 훨씬 자연스럽다. 하지만
현재 공개 출처 사이에는 다음 join key가 없다.

1. 동일 patient와 aneurysm의 pre-treatment 3D geometry
2. 실제 coil/device type, deployment sequence와 packing configuration
3. source-matched virtual mechanics target 또는 검증 가능한 mechanical reference
4. 시술 직후 원본 DSA와 injection curve
5. 사전에 정한 follow-up 시점의 adjudicated occlusion와 censoring
6. patient/lesion-disjoint development, validation와 external test manifest

서로 다른 cohort의 500 synthetic shape와 458 clinical patient를 feature-space에서
결합하는 것은 환자 수준의 기전 검증이 아니다. Missing join을 neural network로
추정하면 모델은 “기전”을 학습하는 것이 아니라 dataset 차이를 흡수하게 된다.

## 4. direct prior가 닫는 쉬운 novelty

다음은 새 contribution이 아니라 반드시 포함할 control 또는 이미 점유된 task다.

- geometry feature에서 coil reaction force/elastic energy/contact pressure를 예측
- angiographic input-function normalization과 QA-based occlusion prediction
- LIME/SHAP를 추가한 설명 가능성
- longitudinal morphology+CFD growth association
- wall-motion–WSS correlation
- automated centerline/CFD workflow와 particle-regime map
- GNN, neural operator, Hodge, SE(3), topology loss 또는 periodic module의 조합

특히 architecture component를 합치는 것으로 서로 다른 환자 cohort 사이의
unobserved join을 복구할 수 없다. Fancy함은 모듈 수가 아니라 **관측 가능한 실패
기전, 타당한 target time, 독립 unit과 confirmatory evidence가 한 흐름으로 연결되는
것**에서 나와야 한다.

## 5. prospectively frozen six-way screen

축 순서는 clinical importance / target identifiability / residual novelty / asset
readiness / effective independent unit / strong baseline feasibility / interpretable
evidence / ISBI schedule fit이다. 총점 32 이상이어도 identifiability 3.5, novelty
2.5, asset 3.0, unit 3.0, baseline 3.0의 모든 floor를 통과해야 한다.

| 후보 | 8축 점수 | 합계 | 결정적 실패 | 판정 |
|---|---|---:|---|---|
| Injection-invariant QA → 6-month occlusion | 5.0/5.0/0.5/0.5/4.0/5.0/4.5/3.0 | **27.5** | source가 task를 직접 점유; public rows/images/split 없음 | reject |
| Longitudinal hemodynamics → future growth | 5.0/4.0/1.0/0.5/3.0/4.5/5.0/2.5 | 25.5 | 17 private matched pair; external/public contract 없음 | reject |
| Patient-family-disjoint coil-mechanics transport | 4.5/4.5/0.5/0.5/1.0/5.0/5.0/3.0 | 24.0 | 500 synthetic sac의 generating family/mapping 공개 안 됨 | reject |
| Amplified wall motion + CFD growth mechanism | 4.5/4.0/0.5/0.5/2.0/4.5/5.0/2.5 | 23.5 | 12 private cases; association은 direct prior | reject |
| Coil mechanics → actual follow-up occlusion | 5.0/2.0/3.0/0.5/1.0/4.0/5.0/2.5 | 23.0 | mechanics–patient–outcome join 없음 | reject |
| Particle-regime-guided therapeutic delivery | 3.5/4.5/0.5/0.5/0.5/5.0/5.0/3.0 | 22.5 | one idealized anatomy; clinical target 없음 | reject |

모든 후보가 total 또는 critical floor를 실패한다. 잔여 novelty 3.0인
coil-mechanics→occlusion 후보도 asset 0.5, unit 1.0, identifiability 2.0이므로
admission이 아니다. 높은 novelty 가능성이 낮은 실행 가능성을 보상할 수 없다.

## 6. Surface-vector 분석에 대한 최종 반영

제시된 순서인 task stability → field-error-matched failure → bounded development →
fresh confirmation → external interpretation은 계속 유지한다. 다만 이번 출처들은
surface-vector E0가 아니다.

- coil force와 elastic energy는 transient surface-WSS worldline reference가 아니다.
- QA impulse response와 6-month occlusion은 surface critical point reference가 아니다.
- 12-case wall-motion association은 public method-free stability asset이 아니다.
- idealized particle trajectories는 independent aneurysm surface family가 아니다.

따라서 edge 1-form, Hodge decomposition, SE(3)-equivariant mesh message passing,
80-phase operator와 structural loss는 여전히 **unselected controls**다. Job
`115645.ECE-util1`은 E/exit 2, GPU 0, 0/10의 execution-incomplete/no-verdict
history로 보존하고 repair/rerun하지 않는다.

## 7. 다음 admission에 필요한 최소 자산

다음 중 하나가 stable, lawful, versioned하게 공개되기 전에는 같은 방향을
architecture 단계로 올리지 않는다.

1. 여러 independent patient family의 transient surface-vector field와 BC waveform,
   mesh/tolerance 변형을 허용하는 method-free stability reference
2. patient/lesion-level pre-treatment geometry–device–immediate response–fixed-time
   outcome join
3. complete negative/censoring semantics와 patient-family-disjoint split
4. strong baseline을 동일 input/compute/field-error 조건으로 비교할 수 있는 license와
   executable manifest

이 gate를 통과한 fresh version만 P0를 등록할 수 있다. P0가 통과해도 method,
architecture 또는 GPU를 자동 승인하지 않는다.

## 8. 운영 결정

- Active lead, primary problem, estimand, E0/P0/P1, method, architecture: **0**
- 의료·simulation payload download와 cross-source join: **0**
- Scientific server query, transfer, PBS submission, GPU와 monitoring: **0**
- Result row, figure, C21, contribution과 submission identity: **0**
- Stable official release endpoint가 없는 논문은 recurring source watch에 추가하지 않는다.
- 이후 허용되는 작업은 fresh unrelated problem-level source audit 또는 위 최소 자산이
  material하게 공개됐을 때의 manual source re-audit뿐이다.
- 미래 gate-authorized 실행은 `introai9` PBS만 사용하며 login-node GPU를 금지한다.
  `junjinyong`에는 접속·조회·전송·제출·모니터링하지 않는다.

현재 가장 타당한 결론은 “모델을 더 fancy하게 만들자”가 아니다. **기전과 실제
결과를 잇는 동일-patient evidence가 공개되지 않은 상태에서, architecture가 그
간극을 메웠다고 주장하지 않는 것**이 과학적으로 더 강한 선택이다.

## 9. Schema 11.3 · introai9 실제 보유 자산 확인 결과

사용자 요청에 따라 두 개의 문서화된 `introai9` login boundary를 read-only로
확인했다. 두 endpoint 모두 TCP/22에 도달했고, 그중 하나는 `introai9` 계정의
public-key authentication 완료까지 명시적으로 확인됐다. 그러나 authentication
뒤 remote shell channel과 SFTP subsystem이 모두 timeout되어 `find`, `ls`, `pwd`
등의 출력은 한 줄도 얻지 못했다.

따라서 이번 감사는 다음과 같이 닫는다.

- fresh directory listing: **0 line**
- current dataset presence/absence: **unresolved**
- verified current-direction train/validation/test: **0/0/0**
- PBS submission / scheduler query / GPU / transfer: **0/0/0/0**
- `junjinyong` access: **0**
- verdict: **execution-incomplete / no asset verdict**

과거 bounded 성공 기록은 `/home/introai9/AAAI` project root와 aneurysm-related
trace, 그리고 IntrA repository skeleton을 확인했지만 IntrA mesh payload는 확인하지
못했다. 더 넓은 candidate/manifest 재귀 검색도 시간 한도를 넘겨 미완료였다. 이
과거 trace와 오늘의 authentication을 “데이터셋 확보”로 바꾸지 않는다. 외부
service 또는 관리자 상태가 바뀐 뒤 exact known path에 한해 새 bounded read-only
inventory를 열 수 있으며, 동일한 broad search나 local repair를 반복하지 않는다.
