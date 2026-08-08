# ISBI 2027 submission plan

최종 검토일: 2026-08-06 KST  
상태: **target locked · not submission-ready · V0 preregistered/unrun · M0
metric unrun**

## 1. Venue contract

목표는 IEEE ISBI 2027의 archival four-page regular paper다.

- 공식 마감: 2026-10-26 23:59 USA EDT
- 심사: single blind
- 기술 내용·그림·표: 첫 4쪽 안에 모두 포함
- 5쪽: references, ethical-compliance statement, acknowledgments/COI만 허용
- 공식 scope와의 접점: physical/statistical modelling, reconstruction,
  uncertainty quantification, trustworthy AI, medical applications
- 사람 또는 동물 자료를 쓰지 않는 현재 primary study는 numerical
  simulation study로 명시한다. 공개 human-derived asset을 추가할 때는
  license와 ethics/waiver 문구를 별도로 확인한다.

공식 출처:

- <https://biomedicalimaging.org/2027/>
- <https://biomedicalimaging.org/2027/papers/>
- <https://confcats-event-sessions.s3.us-east-1.amazonaws.com/isbi27/isbi27-cfp_web-03.pdf>

## 2. 냉정한 현재 판정

현재 원고는 ISBI-ready가 아니다.

1. 실행된 exact/nonlinear 모델은 MLP 기반 lifted operator다. 공개
   architecture 문서의 GNN+token+continuous-query 구조는 irregular-3D
   target specification이며 아직 학습 구현이 아니다.
2. N1c는 field distribution, paired response, acquisition에서 실패했다.
   실패 분석 자체를 4-page biomedical-imaging paper의 headline으로
   제출하지 않는다.
3. 64-case Aneumo cache는 asset/scaling development pilot이다. Pressure는
   train-only nontriviality audit에서 탈락했고 velocity만 eligible하다.
4. M0의 multicomponent nonlinear mechanism 결과만으로 3D aneurysm
   reconstruction이나 biomedical relevance를 주장할 수 없다.

## 3. 제출 가능한 한 문장 정체성

다음 문장은 **획득해야 할 identity**이지 현재 contribution이 아니다.

> 3D aneurysm geometry와 불완전한 inflow 정보에서 velocity-field
> distribution을 복원할 때, measurement–solution dependence를 보존하는
> operator objective가 강한 graph/operator baseline보다 field accuracy,
> calibration, mass-flow response를 함께 개선하는가?

ISBI용 범위는 의도적으로 좁힌다.

- primary output: steady 3D velocity
- primary uncertainty: missing scalar inflow under an explicitly declared
  experimental/design law
- secondary: observed-inflow response curve
- 제외: pressure, WSS/OSI, transient efficiency, rupture prediction,
  clinical utility, multicomponent active acquisition

Scalar inflow design law를 patient physiology라고 부르지 않는다. 실제
Doppler/4D-flow measurement distribution이 없으므로 “measurement value”
또는 “design-law uncertainty”로만 표현한다.

## 4. 모델과 method boundary

### Executed evidence model

- exact/nonlinear domains: context MLP + boundary tokens + lifted spatial
  decoder
- 목적: method falsification과 oracle-attribution
- GNN 아님

### Planned irregular-3D backbone

- input: normalized 3D coordinates, kNN graph, scalar inflow value/mask
- local encoder: residual edge-message blocks
- global context: pooled anatomy tokens and inflow token
- output: node-wise velocity query decoder
- uncertainty: missing inflow samples × seed ensemble

Backbone 자체는 contribution이 아니다. MGN/kNN graph operator와
conditioned point/operator baseline을 동일 split·budget에서 비교한다.

### Candidate method

M0는 candidate measurement와 solution functional의 joint dependence가
solution marginal만 맞추는 것보다 유용한지를 한 번 falsify한다. M0가
통과해도 그대로 ISBI method가 되지 않는다. 3D에서는 알려진 scalar inflow
design law와 학습되는 velocity operator에 맞춘 별도 prospective objective
contract가 필요하다.

M0가 실패하면 weight, kernel, seed, threshold를 고쳐 반복하지 않는다.
M0가 통과하더라도 아래 3D task-translation audit에서 estimand가 일치하지
않으면 mechanism을 제출 method로 사용하지 않는다.

## 5. Prospective evidence ladder

### V0 · Venue/task translation audit

실행 계약은 `configs/aneumo_isbi_v0.json`이다. 모델 학습 전에 compact
cache와 기존 공개 train-only scaling aggregate만 감사하며, 새 field
array는 어느 split에서도 읽지 않는다.

- 3D data에서 scalar inflow와 velocity functional의 dependence가
  strong physical-scaling baseline 뒤에도 남는가?
- train/validation/test base family가 완전히 분리되는가?
- inlet/volume node 의미, unit, coordinate frame, condition mapping을
  checksum으로 고정할 수 있는가?
- missing-inflow estimand가 known design law인지 learned population law인지
  혼동하지 않는가?

하나라도 실패하면 missing-inflow distribution claim을 버리고 full-condition
velocity reconstruction paper로 자동 축소하지 않는다. 새 identity를
별도로 검토한다.

고정 estimand는 8개 mass-flow의 **discrete uniform experimental design
law** 아래 internal-point 3-component velocity distribution이다. 이를
patient physiology나 측정 분포라 부르지 않는다. Compact cache에 boundary
marker·surface normal·integration mesh가 없으므로 pressure, WSS/OSI와
mass-conservation endpoint는 실패 항목이 아니라 범위 밖이다. V0의 8개
check가 모두 통과해도 64-case V1 implementation smoke만 허용하며 outer
test, headline result와 submission은 계속 닫힌다.

### V1 · 3D development eligibility

64-case pilot은 구현 smoke와 loss/normalization 선택에만 사용한다.
Headline outer test 전에는 더 넓은 base-family-disjoint cache 또는 독립
3D cohort를 고정한다.

- channels: velocity only
- selection: train/validation only
- mandatory controls: global flow scaling, q-conditioned point/operator,
  kNN MGN, DeltaPhi-style response residual, deep ensemble
- no test read until architecture, objective, samples, stopping rule frozen

### V2 · Frozen five-seed 3D outer test

필수 headline endpoint:

1. full-inflow node-wise velocity relative L2
2. same-geometry inflow-response relative L2
3. missing-inflow velocity energy score
4. nominal 90% functional coverage and interval width
5. paired base-family bootstrap effect and 95% CI against the strongest control
6. inference latency and parameter/compute match

보조 endpoint는 global kinetic-energy/peak-speed response로 제한한다.
Inlet/outlet marker와 surface-gradient provenance가 없으면 mass conservation,
WSS, OSI를 넣지 않는다.

### ISBI submission gate

다음을 모두 만족해야 full paper를 제출한다.

- one frozen candidate method; no post-test variant selection
- expanded or independent 3D outer test
- five seeds and base-family bootstrap CI
- full-condition fidelity가 strongest control보다 악화되지 않음
- missing-inflow distribution과 response endpoint 중 적어도 하나에서
  practically meaningful한 paired improvement와 CI
- representative 3D figure가 cherry-pick 없이 predeclared rule로 선택됨
- technical content가 official template 첫 4쪽에 들어감

실패하면 “fancy”한 이름으로 포장하지 않고 full-paper submission을
보류한다.

## 6. Four-page paper design

1. **Introduction + gap (0.65 page):** missing inflow is not zero inflow;
   current aneurysm GNNs assume supplied conditions; exact claim boundary.
2. **Method (1.05 pages):** graph/operator backbone in one small diagram,
   measurement–solution objective, missing-inflow pushforward.
3. **Data + protocol (0.75 page):** Aneumo provenance, family split, baselines,
   five-seed and bootstrap contract.
4. **Results (1.25 pages):** one compact table, one 3D qualitative panel, one
   calibration/response plot.
5. **Limitations (0.30 page):** synthetic CFD, design-law inflow, velocity only,
   no clinical/risk claim.

Exact/nonlinear sanity는 한두 문장 또는 작은 ablation row로만 남긴다.
실패 chronology 전체를 본문에 넣지 않는다.

## 7. Calendar and kill dates

| Date (KST) | Deliverable | Kill rule |
|---|---|---|
| 2026-08-10 | V0 asset/task contract | marker·split·estimand 불명확 시 distribution branch 중단 |
| 2026-08-20 | 64-case 3D implementation smoke | graph baseline이 scaling control도 재현 못 하면 backbone 수정 1회 후 중단 |
| 2026-09-03 | expanded-cache validation study | data 확대가 불가능하거나 validation signal 부재 시 full paper 중단 |
| 2026-09-10 | candidate method/config freeze | 이후 architecture·loss search 금지 |
| 2026-09-24 | five-seed outer test complete | gate 실패 시 relabel·threshold repair 금지 |
| 2026-10-08 | four-page draft + figures | unsupported claim 삭제 |
| 2026-10-19 | internal paper freeze | technical page overflow 또는 provenance gap 해소 못 하면 미제출 |
| 2026-10-26 | ISBI submission | official deadline |

이 일정은 연구 결과를 낙관해서 정한 것이 아니라, 실패를 일찍 확정해
불필요한 GPU·원고 수선을 막기 위한 운영 계약이다.
