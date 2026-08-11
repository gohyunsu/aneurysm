# Surface-vector analysis adjudication

> **Decision · schema 8.7 hardening · 2026-08-11 KST:** The supplied analysis is scientifically useful,
> but it mixes a defensible application question with an architecture proposal
> that current evidence does not authorize. We retain the question, narrow the
> estimand, demote the proposed components to controls, and open no experiment.

상태: **accepted in part · corrected in part · no active lead/model/P0/P1/GPU**

> **2026-08-12 delta review · no scientific-state change:** 새로 전달된 분석을
> 항목별로 다시 대조했다. Job 종료 상태, 32.0/40의 역사적 의미, same-contract
> no-repair, staged gate와 no-`junjinyong` 경계는 모두 정확하다. 다만
> “AGENTS.md 상단이 running으로 남아 있다”는 지적은 현재 snapshot에는 적용되지
> 않는다. Public/shared AGENTS는 이미 `115645.ECE-util1`을 closed no-verdict로
> 기록한다. 또한 현재 architecture는 GNN이 아니라 **선택된 architecture 없음**이다.
> Physics-constrained transient aneurysm mesh GNN은 아래의 direct prior이지 AURORA
> current model이 아니다. 이 재검토는 schema, score, source admission, P0/P1,
> method, architecture, server/GPU 또는 paper claim을 열지 않는다.

이 문서는 현재 surface-vector 판정의 authoritative record다. 과거 conditional
assessment의 넓은 endpoint 목록보다 이 문서의 primary/secondary hierarchy가
우선한다.

## 1. 무엇을 그대로 받아들이는가

다음 판단은 현재 기록과 일치하며 유지한다.

- Job `115645.ECE-util1`은 `E`/exit 2, walltime `00:27:02`, GPU 0으로
  종료됐다. Aggregate scientific result, raw PBS log와 persistent probe
  cache가 없고 등록된 10개 scientific check는 모두 **미평가**다.
- 따라서 결과는 `execution-incomplete / no scientific verdict`다. 32.0/40은
  source-admission history이지 모델 성능이나 가설 검증 점수가 아니다. 같은
  contract의 repair, cause reconstruction과 rerun은 금지한다.
- 이 job은 **running이 아니다**. Queue monitor, retry worker 또는 후속 GPU
  training도 없다.
- “Cartesian field error가 작아도 임계 흐름 구조가 맞는다는 보장은 없다”는
  문장은 중요한 **검증 가능 가설**이다. 다만 아직 관측된 failure가 아니며 active
  paper identity도 아니다.
- 새 evidence version이 열린다면 task stability → field-error-matched failure
  evidence → bounded development → fresh confirmation → external interpretation
  순서를 지켜야 한다. 환자 또는 base-geometry family만 독립 단위로 센다.
- 파열 위험, 임상 효용 또는 exact critical-point recovery로 주장을 확대하지
  않는다.

## 2. 무엇을 수정하는가

### Exact point/worldline보다 degree가 먼저다

Critical-point 위치, type과 birth/death track은 mesh, interpolation, tolerance,
matching rule과 near-degenerate zero에 민감하다. 안정성 확인 전에는 이들을
training loss나 primary endpoint로 쓰지 않는다. 더 먼저 물을 수 있는 것은
boundary에서 field가 충분히 0에서 떨어진 region의 **signed total degree**다.
Degree가 0이 아니면 내부에 적어도 한 zero가 존재한다는 것만 보장한다. Exact
개수·위치·type이나 상쇄되는 ± pair는 보장하지 않는다.

이 수정은 과거 surface-vector score를 수리한 것이 아니다. 별도 32.5/40
conformal-degree 후보가 이 좁은 estimand를 제안했지만, 그 exact P0 job
`115684.ECE-util1`도 `E`/exit 2와 10/10 미평가로 닫혔다. 따라서 degree 역시
현재 검증된 contribution이나 active lead가 아니라, 미래 후보가 만족해야 할 더
타당한 estimand hierarchy다.

### Architecture보다 failure mechanism이 먼저다

제안된 edge-integrated 1-form은 좌표 회전에 덜 임의적인 flux-like 표현을 줄 수
있지만 vertex field의 zero, index 또는 track을 자동 보존하지 않는다. Hodge
decomposition은 boundary convention에 의존하며, SE(3)-equivariance와 periodic
temporal decoding도 이미 알려진 inductive bias다. 따라서 미래 evidence가
열리더라도 첫 모델 질문은 “어떤 fancy block을 붙일까”가 아니라 다음 두 가지다.

1. Field-error-matched Cartesian, tangent-projected, equivariant와 Hodge/DEC
   baseline이 안정적인 structure endpoint에서 실제로 갈리는가?
2. Proposal의 structural gain이 field-error 또는 compute 증가만으로 설명되지
   않는가?

이 두 질문에 답하기 전에는 structural loss를 추가하지 않는다. 먼저 evaluation
endpoint로 failure를 확인하고, 그 failure와 직접 연결되는 가장 작은 intervention만
bounded development에서 검토한다.

Schema 8.6의 fresh direct-prior correction은 이 경계를 더 강하게 만든다.
100-patient AAA/29-patient 118-scan external cohort의 LaB-GATr 연구가
E(3)-equivariant transient vector WSS, TAWSS/OSI, BC·remodelling·topology·mesh
generalization과 directional over-smoothing을 이미 보고한다. 따라서 equivariance,
geometry descriptor, flow prior, inflow conditioning과 transient decoding은 명백한
strong control이다. 다만 해당 연구도 signed degree, critical point나 worldline을
평가하지 않았으므로, over-smoothing은 plausible failure mechanism이지 우리가
필요로 하는 structural failure evidence는 아니다. 이 distinction의 exact source·asset
감사는
[`cross-vascular-transient-wss-source-correction-2026-08-11.md`](cross-vascular-transient-wss-source-correction-2026-08-11.md)를
따른다.

### 좋은 architecture와 성능은 admission 근거가 아니다

“충분히 좋은 architecture와 성능이 나오면 ISBI에서 경쟁력이 있다”는 조건문은
결과적으로는 맞지만 현재 의사결정에는 거의 정보를 주지 않는다. 성능은 이미
식별된 task와 독립 단위, 고정된 reference, 실행 가능한 development/confirmation
asset 위에서만 정의된다. 현재는 그 전제들이 충족되지 않았다. 따라서 validation
MSE나 구조 metric이 좋아질 가능성을 source·task gate를 건너뛸 근거로 사용하지
않는다.

미래의 “좋은 성능”도 단일 best run이 아니라 다음 joint criterion을 뜻해야 한다.

1. 환자 또는 base-geometry-family 단위의 fresh confirmation에서 field error가
   사전 정의된 non-inferiority margin을 넘지 않는다.
2. Signed-degree validity/efficiency와, E1에서 안정성이 확인된 secondary point·track
   endpoint가 compute- 및 field-error-matched strong controls보다 개선된다.
3. Seed, remeshing, tolerance와 boundary-margin 변화에 결론이 유지되고, 실패하기
   쉬운 case를 숨기지 않는 patient/family bootstrap uncertainty를 보고한다.
4. 동일 좌표계·color scale의 실제 surface figure가 aggregate metric의 개선이 어떤
   failure를 바로잡았는지 보여 준다.

이 네 조건은 E4/E5의 결과 계약이지 E0 admission 조건을 대신하지 않는다.

### “Fancy architecture”는 E2 이후에도 한 번에 묶지 않는다

E2가 실제 structural failure를 확인하더라도 edge 1-form, Hodge block,
equivariance, periodic operator와 topology loss를 동시에 넣는 설계는 원인 귀속이
불가능하다. 첫 bounded proposal은 가장 강한 field-matched control을 고정한 채
failure와 직접 연결된 **한 가지 최소 intervention**만 추가해야 한다. 예를 들면
edge-integrated output parameterization 또는 boundary-margin degree regularizer 중
하나를 먼저 비교하고, 다음 요소는 validation-only ablation에서 독립 효과가
남을 때만 추가한다. 이 순서는 덜 화려해 보이기 위한 것이 아니라 novelty를
구성요소 수가 아니라 설명 가능한 failure correction으로 만들기 위한 것이다.

## 3. 무엇을 명시적으로 기각하는가

다음은 contribution이나 novelty 문장으로 사용할 수 없다.

- “GNN + Hodge + equivariance + topology loss”라는 구성요소 조합
- Edge 1-form을 썼다는 사실 자체
- MSE 개선만으로 structure-faithful하다고 부르는 것
- Critical-point metric을 많이 추가했다는 사실
- 기존 P0의 downloader, parser, retry 또는 dependency를 고쳐 같은 source score를
  다시 여는 것
- 환자 수 대신 vertex, triangle, phase, point 또는 track 수를 표본 수로 세는 것

관련 direct prior에는 Hodge spectral/duality 계열, equivariant transient WSS
prediction, robust critical-point tracking, trajectory-preserving vector-field
compression, aneurysm WSS fixed-point/cycle analysis와 whole-field conformal
functional certification이 포함된다. 이름을 바꾸거나 이들을 합치는 것은 residual
gap이 아니다.

여기에 [In-PI-MGN/BenchAnXplore](https://www.nature.com/articles/s41746-026-02404-z)도
명시적으로 포함한다. 이 2026 npj Digital Medicine 연구는 semi-idealized aneurysm
mesh에서 cardiac-cycle 3D velocity/pressure를 autoregressive physics-constrained
GNN으로 예측하고 inflow OOD와 rollout을 평가한다. 따라서 “aneurysm mesh GNN +
transient decoder + physics loss”도 이미 강한 direct control이다. 이 연구가
surface-WSS signed critical point/worldline fidelity를 직접 해결하지 않았다는 점은
미래의 **평가 질문**을 남기지만, 곧바로 새 architecture novelty를 만들지는 않는다.

## 4. 향후 재진입 시의 최소 연구 계약

현재 허용되는 실행은 없다. Material official source/asset change가 생겨 fresh
candidate가 다시 admission line을 넘는 경우에만 아래를 별도 prospective
version으로 등록할 수 있다.

| Gate | 먼저 답할 질문 | 통과해도 아직 열리지 않는 것 |
|---|---|---|
| E0 · source | License, manifest, patient/family unit, tangent-field semantics가 식별되는가? | Model, GPU |
| E1 · stability | Degree와 보조 point/track endpoint가 mesh·tolerance·perturbation에 안정적인가? | Structural loss |
| E2 · failure | Field-error-matched strong baselines가 structure에서 실제로 실패하는가? | Paper claim |
| E3 · development | Family-disjoint validation에서 최소 intervention이 compute-matched controls를 이기는가? | Outer-test access |
| E4 · confirmation | Fresh sealed units에서 field tax 없이 degree validity/efficiency와 보조 structure가 개선되는가? | Clinical claim |
| E5 · interpretation | 동일 좌표계·색상 범위의 실제 surface figure가 failure와 correction을 설명하는가? | Rupture-risk claim |

Primary statistical target이 열리는 경우에는 boundary-margin signed total degree의
validity와 efficiency/abstention을 먼저 둔다. Critical-point precision/recall,
per-frame index discrepancy, trajectory distance와 event F1은 E1에서 mesh,
tolerance, perturbation과 matching-rule 안정성이 입증된 뒤의 secondary endpoint다.
기존 machine contract의 이 네 지표를 무조건 `mandatory`로 부르던 표현은 schema
8.7에서 이 hierarchy에 맞게 수정했다.

## 5. 현재 결론

이 방향은 **폐기할 아이디어는 아니지만, 현재 ISBI 논문 주제도 모델도 아니다.**
좋은 성능이 나오면 경쟁력이 있을 수 있다는 조건문만으로는 admission 근거가 되지
않는다. Accept 가능한 application identity가 되려면 (i) field accuracy로 설명되지
않는 재현 가능한 structural failure, (ii) 그 failure에 직접 대응하는 최소 방법,
(iii) patient/family-disjoint fresh confirmation이 모두 필요하다.

현재 active shortlist, primary problem, method, architecture, P0/P1, scientific
server query, PBS/GPU, outer test, result row와 paper contribution은 모두 0이다.
다음 허용 작업은 닫힌 job의 repair가 아니라 **fresh problem-level source/asset
audit**다. AURORA는 gate 이후에도 `introai9` PBS만 사용하며 `junjinyong`에는
접속·조회·전송·제출·모니터링하지 않는다.
