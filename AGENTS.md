# AGENTS.md — AURORA 연구 운영 규약

이 파일은 사람과 자동화 에이전트가 동일한 연구 가정과 품질 기준으로
작업하기 위한 단일 운영 메모다. 2026-08-03 KST에 팀 대화, 기존 저장소,
공개 1차 문헌을 재검토하여 작성했다.

## 1. 연구의 현재 기준선

- 프로젝트명: **AURORA**
- 정식 명칭: **Aneurysm Uncertainty-aware Risk-aligned Operator for Rapid
  Assessment**
- 연구용 endpoint: 공개 데이터의 **cross-sectional rupture status**
- 핵심 문제: geometry-only 배포에서 patient-specific BC가 관측되지 않으면
  hemodynamics는 식별되지 않는다. 따라서 하나의 synthetic CFD label을
  생성하지 않고 조건부 field distribution을 예측한다.
- 핵심 방법: multi-scale surface/volume operator + latent BC distribution +
  one-shot temporal basis decoder + downstream functional sufficiency
  distillation.
- 최종 주장은 “미래 파열 위험을 예측한다”가 아니라 “BC uncertainty를
  반영한 surrogate가 real-CFD 기반 rupture-status signal을 얼마나
  보존하는가”이다.

다음 아이디어는 주 방법론이 아니다. 비교·ablation으로만 남긴다.

- In-PI-MGN에 attention, node masking, V/W-cycle을 단순 추가
- geometry-only case에 deterministic WSS/OSI를 정답처럼 부착
- 1-step 또는 50-step velocity RMSE만으로 임상 유용성 주장
- ruptured/unruptured label을 2년/5년 prospective risk로 표현
- 서로 다른 공개 데이터셋을 파일명 유사성만으로 patient-level 병합

## 2. 현재 contribution 가설

논문 contribution은 아래 세 축으로 제한한다.

1. **Missing-BC distributional operator**: 관측 BC가 있으면 조건부
   prediction, 없으면 population-conditioned BC latent를 주변화하여
   function-space distribution을 출력한다.
2. **One-shot dual-domain cycle decoding**: autoregressive rollout 대신
   cardiac-cycle temporal Fourier coefficients를 한 번에 예측하고, coarse
   volume velocity/pressure와 high-resolution wall WSS를 cross-consistency로
   연결한다.
3. **Task-aligned functional sufficiency**: node RMSE뿐 아니라
   TAWSS/OSI/LSA/RRT와 real-CFD teacher의 ranking/calibration을 보존하도록
   학습하고 `risk-retention`으로 평가한다.

이 셋을 모두 새롭다고 단정하지 않는다. 문헌 검색일과 직접 경쟁작을
기록하고, 최종 novelty 문구는 실험 결과와 exhaustive review 뒤 확정한다.

## 3. 데이터셋의 역할

| 데이터 | 허용된 주 역할 | 금지된 해석 |
|---|---|---|
| Aneumo | 동일/유사 geometry의 다중 steady BC로 BC sensitivity pretraining | patient-specific clinical evidence |
| AneuG-Flow | 대규모 synthetic steady 및 selected pulsatile pretraining | real cohort generalization |
| BenchAnXplore | 105 semi-idealized transient field의 재현·baseline | geometry-only clinical deployment |
| CMHA | patient CTA/mesh, clinical, morphology, real-CFD bridge와 task gate | multi-center external validation로 과장 |
| AneuX | 750 geometry/status의 external association stress test | real hemodynamics validation |
| Aneurisk | provenance가 확인된 geometry/morphology 보조 평가 | asset audit 전 CFD 보유 가정 |

모든 case/field에는 `source_field ∈ {real_cfd, surrogate, synthetic_cfd}`와
dataset version, checksum, unit, coordinate frame을 기록한다.

## 4. 연구를 계속할지 결정하는 gate

- **G0 · Asset integrity**: case mapping, unit, boundary marker, license,
  patient ID/split이 검증되지 않으면 학습하지 않는다.
- **G1 · Hemodynamic utility**: CMHA에서 clinical+morphology+real CFD가
  clinical+morphology보다 patient-bootstrap 95% CI 기준으로 일관된
  incremental utility가 없으면 risk-aligned branch를 주 contribution에서
  내린다.
- **G2 · Operator fidelity**: OOD geometry와 held-out BC에서 field,
  functional, calibration gate를 동시에 통과하지 못하면 AneuX에
  hemodynamics를 생성하지 않는다.
- **G3 · Surrogate sufficiency**: surrogate risk-retention과 calibration이
  사전 정의 기준을 못 넘으면 clinical claim을 하지 않는다.
- **G4 · Non-redundancy**: direct geometry-to-status baseline과 비교해
  AURORA의 개선이 없거나 hemodynamic field가 설명력을 더하지 않으면
  “hemodynamics bridge” 주장을 철회한다.

정확한 threshold는 `configs/aurora_v1.json`에 버전 관리한다. 결과를 본 뒤
threshold를 바꾸면 반드시 exploratory로 표시한다.

## 5. 필수 평가 원칙

- split은 patient/geometry 단위다. 같은 geometry의 timestep, BC, cut,
  augmentation이 train과 test에 갈라지면 leakage다.
- model selection은 nested CV 안쪽에서만 한다. test fold로 architecture,
  threshold, seed를 선택하지 않는다.
- AUROC만 보고하지 않는다. AUPRC, balanced accuracy, Brier, ECE, calibration
  slope/intercept와 patient-bootstrap 95% CI를 포함한다.
- field는 velocity/pressure RMSE 외에 WSS/OSI error, hotspot overlap,
  mass-flux, divergence, boundary violation, distributional coverage/width를
  평가한다.
- direct geometry model, clinical+morphology model, deterministic operator,
  real-CFD oracle, In-PI-MGN/graph-transformer 계열을 공정한 baseline으로 둔다.
- 여러 aneurysm이 한 환자에 있으면 bootstrap과 split의 sampling unit은
  환자다.
- 모든 headline result는 최소 5 seeds 또는 반복 nested split으로 확인한다.
- 통계 검정은 effect size와 CI가 우선이다. cross-validation prediction에
  단순 DeLong을 반복 적용하지 않는다.

## 6. 구현 동기화 규칙

연구 방향, architecture, dataset role, gate가 바뀌는 커밋은 아래를 함께
갱신한다.

1. `docs/research-direction.md`
2. `docs/model-spec.md`
3. `docs/experiment-protocol.md`
4. `configs/aurora_v1.json`
5. `site/assets/research-data.js`
6. `CHANGELOG.md`

사이트의 변경 이력은 `site/assets/research-data.js`에서 렌더링한다. 단순
미관 수정이 아니면 날짜, category, decision, rationale, affected files를
기록한다. README와 사이트가 서로 다른 연구 질문을 말하면 배포하지 않는다.

## 7. 새 팀 대화와 게시글 반영

`tmp/`는 private raw context이며 Git에 올리지 않는다.

새 내용이 들어오면:

1. 파일 수정 시각과 새 구간만 확인한다.
2. 주장, 실험 결과, 결정, 질문을 분리한다.
3. 논문 수치와 데이터 설명은 1차 출처 또는 raw asset으로 재검증한다.
4. 기존 기준선과 충돌하면 자동 채택하지 않고 decision log에 대안과 근거를
   남긴다.
5. 채택된 내용만 문서·config·site·changelog에 반영한다.

대화에 포함된 비밀번호, 회의 링크, 이메일, 서버 경로, 개인 식별정보는
문서·사이트·commit에 옮기지 않는다.

## 8. 사이트 품질 기준

- 첫 화면에서 연구 질문, pivot 이유, 현재 stage를 30초 안에 이해할 수
  있어야 한다.
- 같은 문장을 여러 페이지에 반복하지 않는다. 상세 문서는 GitHub 링크로
  연결한다.
- architecture diagram은 입력, latent uncertainty, decoder, output,
  downstream 평가의 인과 흐름을 보여야 한다.
- “완료”, “검증”, “SOTA”는 증거가 있을 때만 사용한다. 계획은 planned,
  구현은 implemented, 데이터 확인은 audited로 구분한다.
- 모바일, keyboard navigation, reduced motion, 색 대비를 점검한다.
- 외부 링크는 가능한 DOI, 공식 proceedings, dataset record 등 1차 출처를
  사용한다.

## 9. Git과 보안

- 공개 저장소: `https://github.com/gohyunsu/aneurysm`
- 비공개 논문 저장소: `https://github.com/gohyunsu/aneurysm-paper`
- 기본 branch: `main`
- 공개 저장소는 protocol, code, 공개 문서, site를 관리한다. 비공개 저장소는
  manuscript, claim matrix, 미공개 aggregate result와 reviewer 대응만
  관리한다.
- 비공개 원고의 `AGENTS.md`에 public source commit SHA를 pin한다. 연구
  방향이 바뀌면 public protocol/site/changelog를 먼저 갱신하고 private
  manuscript pin을 뒤따라 갱신한다.
- raw medical data, archive, checkpoint, private team log, credential은
  commit하지 않는다.
- 사용자 변경사항과 무관한 파일은 되돌리지 않는다.
- commit 전에 `git diff --check`, protocol validator, unit test, local site
  link/HTML smoke를 수행한다.
- GitHub Pages 또는 production deploy 뒤 공개 URL과 commit SHA를
  `CHANGELOG.md`에 기록한다.

## 10. 논문 언어

- `rupture status classification`: 현재 허용
- `rupture risk prediction`: prospective/time-to-event cohort가 있을 때만
  허용
- `real CFD`: solver provenance와 BC가 확인된 field/summary
- `surrogate hemodynamics`: model-generated; real CFD와 병합 금지
- `patient-specific`: patient geometry만 해당하면 그렇게 한정하고,
  generic BC까지 patient-specific이라고 부르지 않는다.
- `clinical utility`: 외부·전향 검증 전 사용 금지. 대신 `research utility`,
  `downstream association`, `functional sufficiency`를 쓴다.
