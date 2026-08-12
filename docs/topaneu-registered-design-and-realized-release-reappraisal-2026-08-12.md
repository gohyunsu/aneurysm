# TopAneu 등록 설계와 실제 공개 release 재평가

> **판정 · 2026-08-12 · schema 11.1**  TopAneu는 실재하는 2026 MICCAI
> challenge이지만, 등록 설계서의 계획과 현재 공개 학습 release를 같은 자산으로
> 간주할 수 없다. 이 차이는 중요한 provenance·evaluation 경계이지 독립적인
> 방법론 novelty가 아니다. 여섯 후보의 최고점은 31.5/40이며 residual novelty
> 0.5/5로 필수 floor를 실패한다. Terms, 의료 payload, P0/P1, method,
> architecture, server query와 GPU는 모두 0이다.

## 1. 이번 재평가가 답하는 질문

이번 audit은 surface-vector를 재평가하지 않는다. 이미 닫힌 CPU-only job
`115645.ECE-util1`을 수리하거나 같은 contract로 다시 실행하지도 않는다. 질문은
하나뿐이다.

> TopAneu의 공식 등록 설계와 실제 release 사이에, 기존 anatomy-aware aneurysm
> learning과 분리되는 실행 가능한 새 연구 문제가 남아 있는가?

결론은 **아직 없다**이다. 공개 자산은 유용한 장래 benchmark가 될 수 있지만,
현재 확인 가능한 contract만으로는 새 estimand와 clean reference가 식별되지 않는다.

## 2. 정확히 확인한 공식 source

| Source | 확인한 사실 | 해석 경계 |
|---|---|---|
| [MICCAI challenge registry](https://miccai.org/sig/sig-challenges/) | TopAneu 2026, DOI `10.5281/zenodo.19848807`, classification/detection/segmentation, custom data usage agreement | 정식 challenge라는 근거이지 data access나 terms 수락 근거가 아님 |
| [Registered design, Zenodo 19848807](https://zenodo.org/records/19848807) | revision 4, 37-page PDF, 150,978 bytes, MD5 `773b04597d4ff2c798837fb5d40b4bf9`, record license CC BY 4.0 | CC BY는 design PDF에 적용된다. 의료 영상 release의 terms와 혼동하지 않음 |
| [Live Data page](https://topaneu-26.grand-challenge.org/data/) | 현재 학습 release 417 scan/409 patient; 409 patient의 source count는 CHUV 200, HUG 87, Mie-Chuo 54, public 68; UMCU는 private test; vessel mask는 organizer TopBrain prediction | 실제 공개 학습 규모와 mask provenance의 근거. 계획된 전체 수나 gold mask를 확정하지 않음 |
| [Official Git repository](https://github.com/Bangulli/TopAneu-26) | head `018c243445f99199f484018c4c80575c84c72293`; 417-row checksum/mapping contract; 52 location class와 3 type | 공개 code·manifest contract. 의료 payload를 열었다는 뜻이 아님 |
| [Task-1 evaluator](https://github.com/Bangulli/TopAneu-26/blob/main/evaluation_scripts/evaluate_task1.py) | class별 count에서 `n_aneu=sum(gts.values())`를 사용하고 `tn=n_aneu-(tp+fn)` 계산 | 표준 patient×class true negative와 같다고 가정하지 않음 |
| [Task-2 evaluator](https://github.com/Bangulli/TopAneu-26/blob/main/evaluation_scripts/evaluate_task2.py) | active path는 class별 full-volume binary overlap; instance connected-component path는 active score가 아님 | instance detection 성능으로 과대 해석하지 않음 |

이번 update는 공개 metadata, design PDF와 code만 읽었다. Challenge 가입, verified
account 사용, terms 수락, SWITCHdrive 접근, 영상·mask·JSON payload download는 하지
않았다.

## 3. 계획과 실제 release를 분리한다

| Contract 항목 | 등록 설계서의 계획 | 2026-07-31 이후 실제 공개 상태 | 판단 |
|---|---:|---:|---|
| Task-1 학습 | 500 volume | 417 scan / 409 patient | 500을 released train으로 보고하지 않음 |
| 공개 source 몫 | 200 volume | 68 scan | 설계 수치를 현재 manifest에 대입하지 않음 |
| private test | 350 volume, UMCU 포함 | UMCU reserved; case manifest 비공개 | 외부-centre 결과나 독립 unit 수를 선취하지 않음 |
| 학습 vessel mask | gold 50 또는 silver | organizer-model-predicted mask 설명 | casewise gold/silver indicator가 공개됐다고 보지 않음 |
| 최소 location support | train/test 각각 location당 positive ≥3 | public page에서 완전한 casewise support contract 미확인 | rare-class 보장을 실제 release fact로 쓰지 않음 |
| control 비율 | train/test 각각 ≥20% | 현재 공개 manifest의 완전한 control semantics 미확인 | planned proportion을 관측 분포로 쓰지 않음 |
| annotation | single clinician verifier; site-style uncertainty 명시 | adjudicated multi-reader distribution 미공개 | uncertainty-aware learning target이 식별됐다고 보지 않음 |

Landing page의 약 850건은 계획된 train+private test 전체 규모와 일치하는 표현이지,
850개의 공개 학습 case를 뜻하지 않는다. 또한 417 scan을 417 independent patient로
세지 않는다. 현재 공식 설명은 409 patient이며, 기존 Git audit은 7명의 반복 base
patient를 확인했다.

## 4. direct prior가 닫는 쉬운 novelty

다음은 baseline 또는 direct prior이지 AURORA contribution이 아니다.

- vessel graph/GNN, centerline conditioning과 soft vessel-distance attention
- joint aneurysm-location, aneurysm-mask와 vessel-mask multi-task learning
- hierarchy, laterality, branch-role factorization과 anatomy-aware pretraining
- topology/connectivity loss, silver-label distillation과 generic label-noise learning
- center/modality invariance, calibration, conformal prediction과 ranking robustness

가장 가까운 직접 선행으로는 [Tri-Axial ROI multi-task system](https://arxiv.org/abs/2606.26706)이
CTA/MRA/T2/T1-post에서 13개 aneurysm location 분류, 13개 aneurysm segmentation과
13개 vessel segmentation을 함께 다룬다. MICCAI 2024 vessel-distance attention,
WACV 2026 artery-aware masked pretraining, CVPRW 2026 ARAN centerline model과
ICCVW 2025 vesselness multi-task도 anatomy-aware 결합을 이미 점유한다. 따라서
구성요소를 묶거나 이름을 붙이는 것으로 residual novelty를 만들 수 없다.

## 5. prospectively frozen six-way screen

축 순서는 clinical importance / target identifiability / residual novelty / asset
readiness / effective independent unit / strong baseline feasibility / interpretable
evidence / ISBI schedule fit이다. 총점 32 이상이어도 identifiability 3.5, novelty
2.5, asset 3.0, unit 3.0, baseline 3.0의 모든 floor를 통과해야 한다.

| 후보 | 8축 점수 | 합계 | 결정적 실패 | 판정 |
|---|---|---:|---|---|
| Official-metric / instance-collapse-aware evaluation | 4.0/5.0/0.5/5.0/4.5/5.0/3.5/4.0 | **31.5** | novelty; evaluator audit이지 새 method가 아님 | reject |
| Registered-to-realized benchmark-contract fidelity | 4.0/4.5/0.5/5.0/4.0/5.0/3.5/4.0 | 30.5 | novelty; provenance audit 자체는 submission identity가 아님 | reject |
| Gold/silver provenance-conditioned generalization | 4.5/2.0/1.0/2.0/4.0/5.0/5.0/3.0 | 26.5 | casewise gold/silver manifest 없음 | reject |
| External-centre modality generalization | 5.0/3.0/0.5/2.0/4.0/5.0/5.0/3.0 | 27.5 | challenge direct objective; private test inaccessible | reject |
| Bifurcation-uncertainty-aware fine location | 5.0/1.5/2.0/2.0/3.5/4.5/5.0/3.0 | 26.5 | uncertainty distribution/adjudicated reference 없음 | reject |
| Longitudinal patient-set consistency | 4.5/1.0/1.5/2.0/0.5/4.0/5.0/2.0 | 20.5 | 7 repeated patient, chronology·growth reference 없음 | reject |

모든 후보가 total 또는 critical floor를 실패한다. 최고 후보의 31.5와 novelty
0.5는 이전 32.0/40 evaluator 역사와 모순되지 않는다. 이번 점수는 등록 설계와
실제 release를 구분한 **새 evidence version에만** 적용하며, 과거 점수를
소급 수정하지 않는다.

## 6. surface-vector 분석을 어떻게 반영하는가

제시된 핵심 가설은 과학적으로 합리적이다. Cartesian field error가 낮아도 signed
critical point와 cardiac-cycle worldline이 망가질 수 있으며, 그런 실패가 실제로
안정되게 관측된다면 structure-faithful transient WSS surrogation은 ISBI application
identity가 될 수 있다. 그러나 현재는 다음 경계를 유지한다.

1. `115645.ECE-util1`은 E/exit 2, GPU 0, scientific check 0/10의
   execution-incomplete/no-verdict 역사다.
2. aggregate result, raw PBS log와 persistent probe cache가 없으므로 실패 원인이나
   과학 결과를 복원하지 않는다.
3. edge 1-form, Hodge decomposition, SE(3) equivariance, periodic operator와
   structure loss는 direct-prior component/control이며 선택 architecture가 아니다.
4. 동일 contract를 repair/rerun하지 않는다.
5. 다시 검토하려면 새로운 material field asset과 새 evidence version에서
   method-free task stability → field-error-matched failure를 prospectively 통과해야
   한다. 그 뒤에만 bounded development를 논의한다.

즉, 제안된 architecture는 설계 가설로만 보존한다. P1, GPU, outer test와 paper
contribution을 승인하지 않는다.

## 7. 최종 운영 결정

- Active lead, primary problem, estimand, P0/P1, method, architecture, result row,
  figure, contribution과 submission identity: **0**
- TopAneu terms acceptance와 medical payload: **0**
- Scientific server query, transfer, PBS submission, GPU와 monitoring: **0**
- Source watch: 기존 v20이 exact Zenodo design record와 live challenge route를 이미
  감시하므로 중복 watch를 만들지 않는다.
- 이후 허용되는 작업: fresh problem-level source audit 또는 TopAneu의 casewise
  gold/silver/adjudication/independent-test contract가 material하게 공개될 때의 source
  re-audit뿐이다.
- 미래 gate-authorized 실행은 `introai9` PBS만 사용하고 login-node GPU command를
  금지한다. `junjinyong`에는 접속·조회·전송·제출·모니터링하지 않는다.

TopAneu는 “사용하지 않을 dataset”이 아니라 **방법론 gap이 먼저 식별되어야 하는
terms-gated future benchmark**다. 현재 가장 냉정하고 타당한 결론은 모델을 만드는
것이 아니라, 잘못된 단위·계획 수치·mask provenance를 paper claim으로 가져오지
않도록 연구 상태를 fail-closed로 유지하는 것이다.
