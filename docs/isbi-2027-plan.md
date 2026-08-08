# ISBI 2027 submission plan

최종 검토일: 2026-08-09 KST
상태: **target locked · not submission-ready · prior BC-operator identity
inactive · cross-protocol 4D-flow I0a passed 14/14 asset-only · I0b
execution-incomplete before asset access/no scientific verdict/no rerun ·
4D-flow branch closed · method unselected**

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

1. 실행된 exact/nonlinear 모델은 MLP 기반 lifted operator다. V1 point/graph
   네 후보는 학습됐지만 모두 relative L2 약 1로 실패했다. 공개 architecture
   문서의 더 큰 GNN+token+continuous-query 구조는 장기 irregular-3D target
   specification이다.
2. N1c는 field distribution, paired response, acquisition에서 실패했다.
   실패 분석 자체를 4-page biomedical-imaging paper의 headline으로
   제출하지 않는다.
3. 64-case Aneumo cache는 asset/scaling development pilot이다. Pressure는
   train-only nontriviality audit에서 탈락했고 velocity만 eligible하다.
4. M0의 multicomponent nonlinear mechanism 결과만으로 3D aneurysm
   reconstruction이나 biomedical relevance를 주장할 수 없다.
5. 4D-flow SR, denoising, physics reconstruction와 voxelwise UQ는 직접
   선행연구가 있으므로 새 candidate도 단순 재구성 성능으로는 제출할 수 없다.

## 3. 최근 candidate identity · closed, contribution 아님

> 한 intracranial 4D-flow acquisition에서 추론한 posterior가 같은
> controlled phantom flow의 다른 resolution·acceleration·VENC acquisition을
> measurement space에서 calibrated하게 예측할 수 있는가?

이 문장은 제출 제목이 아니라 I0a/I0b가 반증할 문제 정의다. Exact source
`f7b4e024…`의 I0a는 두 공개 paired-protocol release의
metadata/header/byte contract를 field read 없이 감사해 14/14를 통과했다.
이는 task 또는 method evidence가 아니다. I0b는 2021 processed velocity에서
target-dependent registration 없이 protocol discrepancy와 alignment를 검사하고,
새 33-scan intervention release의 5 base geometry·22 physical state·8 multi-VENC
state·2 pump-off scan을 header truth로 감사하도록 등록했다. 33 scans는 2
source patient anatomy에서 왔으므로 독립 patient cohort가 아니다.

Exact source `0ebdb344…`의 I0b는 wrapper가 기존 read-only `h5py==3.12.1`
layer를 누락해 archive와 field access 전 exit 1이었다. Gate는 미평가이고 task adequacy에 대한
scientific verdict가 아니다. One-shot/no-rerun 계약을 적용해 dependency
repair, I0b 반복과 I0c를 열지 않는다. 따라서 아래 가능한 identity는 구현
계획이 아니라 보존된 가설이며 이 4D-flow branch는 submission path가 아니다.

가능한 논문 정체성은 이후에만 열린다: protocol-aware latent field posterior를
held-out acquisition operator로 pushforward하고, CFD가 아닌 실제 paired
measurement predictive score와 aneurysm-localized functional calibration을
동시에 개선하는 algorithm과 보장이 direct SR/UQ baseline보다 우월해야 한다.
공개 phantom 수와 repeat 부족이 이를 지지하지 못하면 full-paper 방향을
중단하며 deterministic harmonization으로 자동 축소하지 않는다. 다음 제출
후보는 새 problem-level audit에서 다시 시작해야 한다.

## 3-A. 보존된 이전 한 문장 정체성 · inactive

다음 문장은 이전에 검증했으나 N1c/V1e/M0 뒤 active identity가 아니다.

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
solution marginal만 맞추는 것보다 유용한지를 한 번 falsify하도록
등록했지만, 2/3 seed만 완료돼 aggregate와 scientific verdict가 없다.
성공 seed metric을 선택 집계하지 않으며 sampler를 고쳐 반복하지 않는다.
따라서 mechanism은 inactive이고 ISBI method·3D translation·fresh re-entry를
열지 않는다.

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
기존 compact cache에 marker·surface normal·integration mesh가 없으므로 pressure, WSS/OSI와
mass-conservation endpoint는 실패 항목이 아니라 범위 밖이다. V0의 8개
check가 모두 통과해도 64-case V1 implementation smoke만 허용하며 outer
test, headline result와 submission은 계속 닫힌다.

Exact public source `0589070`의 CPU metadata audit은 2026-08-08 8/8 check를
통과했다. Cache field array와 validation/test field는 읽지 않았다. 공개
aggregate는 `results/aneumo_isbi_v0_20260808.json`이다. 이 결과로 V1
contract 등록만 가능하며 expanded/independent outer test 조건은 바뀌지
않는다.

### V1 · 3D development eligibility

64-case pilot은 구현 smoke와 loss/normalization 선택에만 사용한다.
Headline outer test 전에는 더 넓은 base-family-disjoint cache 또는 독립
3D cohort를 고정한다.

- channels: velocity only
- selection: train/validation only
- exact contract: `configs/aneumo_isbi_v1.json`
- fixed inputs: per-case centered/isotropic coordinates, scalar mass flow,
  deterministic 1,024/4,096 development nodes
- compared backbones: q-conditioned PointNet, kNN-MGN, DeltaPhi-style graph
  residual, frame-free anchor-token equivariant operator
- mandatory controls: same-case global scaling for response only and the
  three registered seed ensemble for missing uncertainty
- ensemble estimand: matching-q seed mean for point prediction; 3 seeds × 8 q
  values for a 24-component missing-design-law mixture
- aggregate integrity: exact 4×3 task manifest and validation checkpoint replay
  within absolute 1e-5 before selection
- matched budget: 3 seeds, 3,000 steps, hidden 96, parameter range within 15%
- selector: seed-mean response L2, full-q L2, missing energy, parameters
- no test read until architecture, objective, samples, stopping rule frozen

V1은 candidate method 비교가 아니라 backbone selection이다. Candidate
이름은 selector에 우선권이 없고 paired-response loss weight는 0이다.
Measurement–solution objective는 positive M0와 별도 protocol 전에는
추가하지 않는다. V1 pass도 V2나 submission을 열지 않는다.

**Outcome · 2026-08-08.** Exact task source `a0479fb`의 12개 task는 모두
exit 0이었고 aggregate source `78dca92`가 checkpoint를 validation에서
재현했다. 그러나 선택 q-PointNet의 worst-seed full-q/response L2
`1.03459/1.00354`가 frozen `0.35/0.50`을 실패해 gate는 5/7이다. True
validation anchor를 쓰는 response-only oracle `0.22794`는 task signal은
보이지만 deployable reconstruction evidence가 아니다. Current backbone
branch, V2, headline과 submission을 닫는다.

V1a는 exact source `3a0d27f`에서 기존 checkpoint의 train/validation fit과
truth-only field-energy decomposition만 계산해 exit 0으로 완료됐다. 네
family의 train full-q L2가 이미 `0.76939--0.95647`이고 validation은 모두
약 1이다. 이는 새로운 family 일반화만의 실패가 아니라 training fit과
vector prediction collapse다. Validation truth의 condition-energy fraction
`0.15748`과 true-anchor response oracle `0.22794`는 condition response가
비자명하지만 geometry-only reconstruction은 성립하지 않았음을 보여준다.
V1은 failed로 보존하고 current branch는 폐기한다. 새 task/data identity를
learned method 없이 감사하기 전에는 candidate method와 V2를 등록하지 않는다.

V1b는 official archive에 발견된 boundary asset을 새 input으로 채택하는 실험이
아니라 asset identifiability audit이다. Archive 1/case 1의 mesh/VTP header는
등록 전에 이미 보았음을 공개한다. 이후 20 archives·64 cases의 member
completeness와 train representative 60 VTP의 CRC, patch identity,
connectivity/array contract만 검사했다. Exact source `fb1c21a`에서 8/8을
통과했지만 model evidence는 아니다. 이 pass 뒤 geometry value를 보기 전에
V1c를 고정했다. V1c는 20 train representative×3 patch×3 flow의 180
payload에서 geometry만 decode해 q-invariance, topology, area/frame와 기존
compact cache 좌표계 일치를 감사해 8/8을 통과했다. 60/60 patch가 exact
q-invariant였고 minimum polygon-valid fraction은 1.0이었다. 이 pass 뒤
validation geometry를 보기 전에 V1d를 고정했다. Exact source `369317a`의
V1d는 train 40·validation 12·test 0 case의 boundary 468개와 reference-volume
52개 payload에서 geometry만 decode해 9/9을 통과했다. 156/156 patch가
q-invariant였고 52/52 case의 exact boundary-volume point correspondence를
확인했다. 이 asset pass 뒤 어떤 학습보다 먼저 V1e known-condition baseline을
고정했다. Exact source `c62838b`의 boundary Perceiver와 matched geometry-only
control 6-task는 모두 정상 완료됐고 boundary가 full-q/response에서 3/3 seed로
우세했으며 mean 상대 개선은 `10.94%/6.41%`였다. 그러나 boundary worst-seed
train/validation/response L2가 `0.77221/0.87796/0.94918`로 frozen
`0.25/0.35/0.50`을 모두 넘어서 6/9 fail이다. Boundary asset utility는
있지만 known-condition learnability는 없다. 등록대로 current Aneumo 3D line을
local repair 없이 중단하고 scalar missing-inflow protocol, test geometry/field,
V1 relabel, V2, multicomponent partial claim과 submission은 열지 않는다.

### V2 · Frozen five-seed 3D outer test

필수 headline endpoint:

1. full-inflow node-wise velocity relative L2
2. same-geometry inflow-response relative L2
3. missing-inflow velocity energy score
4. nominal 90% functional coverage and interval width
5. paired base-family bootstrap effect and 95% CI against the strongest control
6. inference latency and parameter/compute match

보조 endpoint는 sampled-node mean/RMS/95th-percentile speed로 제한한다.
Node volume weight가 없으므로 이를 kinetic energy라 부르지 않는다.
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
| 2026-08-08 | 64-case V1 implementation smoke | 5/7 fail; current backbone branch 중단, local repair 금지 |
| 2026-08-08 | V1a fixed-checkpoint attribution | 완료: training underfit/collapse; method/V2 권한 없음 |
| 2026-08-08 | V1b boundary-asset audit | 완료: 8/8; asset evidence만 인정, model 권한 없음 |
| 2026-08-08 | V1c boundary-geometry audit | 완료: 8/8; geometry staging adequacy만 인정 |
| 2026-08-08 | V1d development geometry cache | 완료: 9/9; 156/156 q-invariant, 52/52 exact boundary-volume correspondence |
| 2026-08-08 | V1e known-condition baseline | 완료: 6/9 fail; relative boundary utility 3/3·10.94%/6.41%, absolute learnability 3 checks fail; current Aneumo 3D line 중단 |
| 2026-08-08 | M0 one-shot mechanism execution | 미완료: 2/3 seed exit 0, 1/3 conditional rejection stall; aggregate·과학적 판정 없음, 성공 seed metric 미검사, local repair/re-entry 금지 |
| 2026-09-03 | 새 task/data identity 결정 | reference state·boundary marker·expanded data 중 식별 가능성과 비자명성을 회복하는 근거가 없으면 full paper 중단 |
| 2026-09-10 | candidate method/config freeze | 이후 architecture·loss search 금지 |
| 2026-09-24 | five-seed outer test complete | gate 실패 시 relabel·threshold repair 금지 |
| 2026-10-08 | four-page draft + figures | unsupported claim 삭제 |
| 2026-10-19 | internal paper freeze | technical page overflow 또는 provenance gap 해소 못 하면 미제출 |
| 2026-10-26 | ISBI submission | official deadline |

이 일정은 연구 결과를 낙관해서 정한 것이 아니라, 실패를 일찍 확정해
불필요한 GPU·원고 수선을 막기 위한 운영 계약이다.
