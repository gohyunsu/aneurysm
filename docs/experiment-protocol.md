# AURORA 사전 실험 프로토콜

버전: 1.0-draft

연결 설정: `configs/aurora_v1.json`

결과 확인 전 primary metric과 gate를 고정한다.

## 1. 가설

- **H1 · Distribution:** missing BC에서 AURORA가 deterministic operator,
  MC-dropout, deep ensemble보다 functional energy score와 90% coverage-width
  trade-off가 우수하다.
- **H2 · One-shot:** temporal-basis decoder가 autoregressive baseline보다
  WSS/OSI error와 long-cycle stability를 개선한다.
- **H3 · Sufficiency:** real-CFD가 morphology 이후 추가 정보를 보일 때,
  task-aligned surrogate가 non-aligned surrogate보다 그 incremental AUPRC를
  더 많이 보존한다.
- **H4 · Honest uncertainty:** uncertainty가 held-out BC error, geometry OOD,
  mesh perturbation에서 증가하며 failure detection AUROC를 개선한다.

## 2. 먼저 실행할 feasibility gates

### G0. asset and label audit

- CMHA patient–CTA–mesh–CFD–clinical key가 일대일/일대다 중 무엇인지 확인
- real CFD가 field인지 summary table만 가용한지 확인
- AneuX status와 CMHA status 정의, rupture 시점, multiple aneurysm 처리 확인
- mesh unit, inlet/outlet marker, cardiac phase, WSS definition 확인

하나라도 불명확하면 해당 modality를 학습에 넣지 않고 `unresolved`로 둔다.

### G1. real-CFD incremental utility

CMHA에서 아래 저용량 모델을 동일 nested split으로 비교한다.

1. clinical
2. morphology
3. clinical + morphology
4. clinical + morphology + real CFD

모델은 penalized logistic regression과 gradient-boosted tree 두 family로
제한한다. G1의 목적은 SOTA가 아니라 hemodynamics branch를 정당화하는
것이다.

Primary: patient-level AUPRC difference `4 - 3`

Secondary: AUROC, Brier, calibration slope, decision curve exploratory

Gate: bootstrap 95% CI와 fold consistency를 함께 보고 판단

분모가 0에 가깝거나 음수면 risk-retention을 계산하지 않는다.

#### 2026-08-03 exploratory diagnostic

G0의 공식 case map이 해결되기 전에 표 구조와 pipeline을 검증하기 위한
penalized linear pilot을 `junjinyong`의 scheduler GPU allocation에서
실행했다. 이 결과는 confirmatory G1이 아니다.

| 입력 | AUPRC | AUROC | Brier | ECE |
|---|---:|---:|---:|---:|
| clinical | 0.777 | 0.615 | 0.207 | 0.165 |
| morphology | 0.756 | 0.540 | 0.218 | 0.163 |
| hemodynamics | 0.649 | 0.364 | 0.237 | 0.192 |
| clinical + morphology | 0.759 | 0.559 | 0.226 | 0.193 |
| clinical + morphology + hemodynamics | 0.717 | 0.462 | 0.242 | 0.189 |

Primary exploratory difference는 `−0.0419`, patient-bootstrap 95% CI는
`[−0.1083, 0.0066]`이었다. 현재 표 기반 real-CFD summary의 incremental
utility를 지지하지 않는다.

중간 audit에서 정의가 확인되지 않은 `PHASE`, `ELAPSS` 조합이 status를 거의
결정적으로 분리해 두 열을 제외했다. 105 lesion은 99 patient에 속하며
6 multi-lesion patient는 병변별 status가 달라 patient-group split을
사용했다.

결정:

- C3 task-aligned risk-retention은 현재 primary contribution이 아니라
  confirmatory G1에 종속된 secondary hypothesis다.
- C1 missing-BC operator와 C2 one-shot field/functional fidelity를 우선한다.
- 공식 case map, feature definition, gradient-boosted second family와 frozen
  confirmatory protocol 전에는 G1을 최종 실패로 선언하지 않는다.
- 분모가 양수가 아니므로 이 run에서 risk-retention을 계산하지 않는다.

공개 aggregate artifact:
`results/cmha_g1_exploratory_20260803.json`

### G2. same-geometry BC pilot

Aneumo에서 geometry 100개 × BC 8개 pilot을 구성한다.

- geometry-disjoint outer test
- 훈련 geometry에서도 2개 BC를 BC-held-out test로 예약
- point estimate, Gaussian NLL, MC-dropout, deep ensemble, PNO-style energy
  score 비교
- wall WSS functional만 먼저 평가

G2 실패 시 transient/clinical 단계로 확장하지 않는다.

현재 `introai9`에서 확인된 Aneumo는 geometry 1개 × BC 2개 sample뿐이므로
이 자산만으로 위 G2를 실행하지 않는다. 전체 multi-BC subset과 split
manifest를 확보하기 전 G2는 blocked다.

### D0. one-shot temporal representation gate

BenchAnXplore 전체 105 geometry × 80 timestep에서 모델을 학습하기 전에
Fourier 4/8/12 mode의 **oracle reconstruction**을 실행한다. primary는
`K=8`이며 설정과 threshold는 `configs/benchanxplore_d0.json`에 결과 확인
전에 고정했다.

- full-domain relative L2 ≤ 0.01
- retained temporal energy ≥ 0.995
- cycle mean/peak speed relative MAE 각각 ≤ 0.02
- bulge relative L2 ≤ 0.02

통과는 temporal representation이 병목이 아님을 뜻할 뿐 learned operator
성능을 뜻하지 않는다. 실패하면 mode 수를 늘리거나 one-shot Fourier
decoder를 폐기한다.

## 3. 데이터 split

### Operator pretraining

- split key: source geometry ID
- same geometry의 BC, timestep, sampling, augmentation은 한 fold에만 존재
- synthetic generator의 parent seed가 있으면 seed family 단위로 분리
- OOD test:
  - unseen geometry
  - unseen BC range
  - unseen site/topology
  - unseen mesh density

### Clinical evaluation

- split key: patient ID
- multiple aneurysm patient는 모두 같은 fold
- outer 5-fold × 3 repeats, class prevalence를 patient 단위 stratify
- inner 4-fold에서 preprocessing, hyperparameter, calibration 선택
- small sample이면 location은 hard stratification 대신 reporting stratum
- missing value imputation과 scaling은 fold 안에서 fit

### External stress test

AneuX는 status definition과 feature mapping audit 뒤 사용한다.

- CMHA에서 선택한 model/config를 고정
- AneuX label을 보고 threshold를 조정하지 않음
- site/location/source별 성능과 calibration shift 보고
- real CFD가 없으므로 field accuracy 또는 true risk utility를 주장하지 않음

## 4. baseline matrix

### Field surrogate

| ID | 모델 | BC 처리 | 시간 처리 |
|---|---|---|---|
| F0 | mean/nearest geometry | empirical | static |
| F1 | PointNet / Graph U-Net | observed | steady/direct |
| F2 | MeshGraphNet / In-PI-MGN | observed state | autoregressive |
| F3 | GNOT/Transolver-style | observed | direct |
| F4 | F3 + MC dropout | missing/observed | direct |
| F5 | F3 deep ensemble | missing/observed | direct |
| F6 | AURORA deterministic | observed | one-shot basis |
| F7 | AURORA distributional | missing/observed | one-shot basis |

### Downstream status

| ID | 입력 |
|---|---|
| R0 | clinical |
| R1 | morphology |
| R2 | clinical + morphology |
| R3 | direct 3D geometry encoder |
| R4 | clinical + morphology + real CFD |
| R5 | clinical + morphology + deterministic surrogate |
| R6 | clinical + morphology + distributional surrogate |
| R7 | R6 + task alignment (full AURORA) |

R3은 필수다. R7이 R3보다 낫지 않으면 hemodynamic interpretation이 실제
incremental signal인지 입증하기 어렵다.

## 5. 평가 지표

### Field level

- normalized relative L2 of velocity, pressure, WSS
- magnitude와 direction error 분리
- wall/interior, neck/dome/parent, low/high-gradient region별 error
- temporal spectral error와 peak phase error

### Functional level

- TAWSS/OSI/RRT/LSA MAE, Spearman, CCC
- top 10% WSS hotspot Dice와 geodesic centroid distance
- neck inflow concentration ordering
- area-weighted summary calibration

### Physics level

- divergence residual
- inlet–outlet mass imbalance
- wall no-slip violation
- volume-derived/direct-wall WSS consistency

### Distribution level

- functional-space energy score
- CRPS for scalar functionals
- 50/80/90/95% empirical coverage
- interval width at matched coverage
- calibration by geometry/BC/site stratum

### Downstream level

- primary: AUPRC
- AUROC, balanced accuracy, sensitivity at fixed specificity
- Brier score, ECE, calibration slope/intercept
- uncertainty–error correlation
- selective risk: coverage vs performance after abstention
- risk-retention with bootstrap CI, G1 통과 때만

### Efficiency

- preprocessing/meshing dependency
- training GPU hours
- inference latency per case and per BC sample
- peak GPU memory, parameters, query count

## 6. ablation

한 번에 한 축만 바꾼다.

1. deterministic vs BC distribution
2. autoregressive vs one-shot Fourier 4/8/12 modes
3. wall-only vs volume-only vs dual-domain
4. no physics vs flux/divergence vs full consistency
5. field loss vs +functional vs +task alignment
6. empirical BC prior vs conditional mixture
7. no synthetic pretrain vs Aneumo vs +AneuG-Flow
8. no canonical frame vs local frame augmentation
9. mean of BC samples vs set encoder
10. geometry direct path blocked vs allowed

## 7. robustness and falsification

- inlet waveform amplitude ±10/20/30%
- outlet split policy change: Murray exponent variants
- mesh resolution ×0.5/×2와 node dropout
- neck boundary perturbation
- geometry scale and coordinate rotation
- synthetic→CMHA shift
- location-held-out where sample count permits
- randomized hemodynamics negative control
- shuffled status within patient/source strata

특히 shuffled hemodynamics로 같은 성능이 나오면 model이 clinical/morphology
path만 사용하는 것으로 본다.

## 8. 통계

- 환자 bootstrap 2,000회로 CI
- multiple aneurysm는 cluster bootstrap
- outer-fold prediction을 한데 모은 뒤 단순 i.i.d.로 취급하지 않음
- paired model difference를 동일 patient prediction으로 계산
- 주요 비교와 metric은 config에서 사전 지정
- p-value보다 effect size, CI, calibration을 우선
- exploratory subgroup은 multiplicity와 작은 n을 명시

## 9. 결과 표의 필수 열

모든 headline table은 다음 metadata를 포함한다.

`dataset version | split hash | patient/geometry n | BC mode | field source |
seed/repeat | metric definition | mean | 95% CI | calibration | compute`

## 10. 단계별 계산 계획

### Phase 0 · 1–2주

- G0/G1
- 100 geometry BC pilot
- 예상 계산: 단일 GPU 1–3일 + tabular nested CV

### Phase 1 · 2–4주

- 1,000–2,000 geometry steady pretraining
- deterministic/probabilistic baseline
- surface-only functionals

### Phase 2 · 3–6주

- selected pulsatile cases
- one-shot temporal basis와 dual-domain decoder
- In-PI-MGN/transformer comparison

### Phase 3 · 3–5주

- CMHA paired fine-tuning
- task alignment와 nested downstream evaluation
- AneuX external stress test

Full AneuG-Flow 2.6 TB를 먼저 받지 않는다. geometry/processed subset으로
G2를 통과한 뒤 storage owner 승인과 manifest를 갖춰 확장한다.
