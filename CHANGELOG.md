# Changelog

연구 결정, 데이터 계약, 모델 설계, 실험 프로토콜, 사이트 변경을 함께
기록한다. 단순 오탈자는 묶어서 기록할 수 있지만 연구 주장을 바꾼 변경은
독립 항목으로 남긴다.

## 2026-08-03 · BenchAnXplore D0 preregistration

### Data

- Aneumo의 현재 서버 자산이 전체 release가 아니라 geometry 1개 × steady
  BC 2개 sample임을 확인해 full G2를 blocked로 표시했다.
- BenchAnXplore archive의 105 HDF5 + 105 XDMF, 80 velocity timestep,
  checksum을 확인하고 `junjinyong`의 read-only input cache를 준비했다.

### Experiment

- one-shot 모델 학습 전 Fourier 4/8/12-mode 표현 손실을 판정하는 D0
  audit과 `K=8` 성공 threshold를 결과 확인 전에 등록했다.
- pinned container는 수정하지 않고 `h5py==3.12.1` 외부 dependency layer를
  사용하도록 PBS template과 aggregate-only result contract를 추가했다.

## 2026-08-03 · Asset audit, G1 diagnostic, and field guide

### Experiment

- `introai9`에서 Aneumo, AneuG-Flow, BenchAnXplore, CMHA, AneuX,
  Aneurisk 자산을 읽기 전용으로 확인했다.
- `junjinyong`의 PBS A6000 allocation에서 pinned PyTorch/CUDA smoke와 CMHA
  G1 exploratory sensitivity를 실행했다.
- 99 patient/105 lesion을 patient-grouped 5×5 split으로 평가한 결과
  `clinical+morphology` AUPRC 0.759, `+real-CFD summary` 0.717,
  `Δ=-0.0419 [−0.1083, 0.0066]`이었다.
- 공식 case map과 second model family 전까지 confirmatory G1은
  `unresolved`다. C3를 conditional secondary로 낮추고 C1/C2를 우선한다.
- 정의가 확인되지 않고 target을 거의 분리한 `PHASE`, `ELAPSS`를
  baseline에서 제외했다.

### Implementation

- patient-grouped nested-CV linear pilot, patient bootstrap, CUDA smoke, PBS
  template과 aggregate result contract를 추가했다.
- grouped splitter의 empty-fold 오류를 unit/data smoke로 발견·수정했고 실패
  run도 provenance로 보존했다.
- 공개 aggregate result:
  `results/cmha_g1_exploratory_20260803.json`

### Site

- 한 장 요약을 유지하면서, 배경지식이 없는 독자를 위한 11개 상세 설명 창과
  16개 용어 glossary를 `site/learn.html`에 추가했다.
- 메인 architecture에 “GNN local encoder + attention + neural-operator
  decoder” 분류와 각 모듈의 상세 링크를 추가했다.
- G1의 음수 exploratory evidence와 conditional C3 결정을 gate·실험·변경
  이력에 반영했다.

### Deployment

- content commit: `c9a998b`
- GitHub quality workflow: success
- GitHub Pages workflow: success
- production verification: main, 11-chapter guide, aggregate result JSON all
  returned HTTP 200
- production guide:
  `https://gohyunsu.github.io/aneurysm/site/learn.html`

## 2026-08-03 · Research reset: AURORA

### Changed

- 기존 “In-PI-MGN + attention/masking/multigrid” 중심 개선안을 primary
  method에서 제외했다.
- geometry-only 입력에서 boundary condition이 관측되지 않는 문제를
  deterministic regression이 아닌 conditional field distribution으로
  재정의했다.
- autoregressive velocity rollout 대신 cardiac cycle의 temporal basis를
  one-shot으로 예측하는 dual-domain operator를 제안했다.
- real-CFD field fidelity와 downstream rupture-status functional
  sufficiency를 분리해 함께 평가하도록 설계했다.
- cross-sectional rupture status와 prospective rupture risk를 명시적으로
  분리했다.

### Added

- 연구 방향, 선행연구 계보, 모델 명세, 사전 실험 프로토콜 문서
- machine-readable `configs/aurora_v1.json`과 validation CLI
- 연구 가설·gate·변경 이력을 탐색할 수 있는 단일 프로젝트 사이트
- protocol test, local link/anchor audit, JavaScript syntax를 검사하는 GitHub
  Actions quality gate
- 팀 대화 반영, 보안, 사이트 동기화 규칙을 담은 `AGENTS.md`
- 원고, claim matrix, planned result table을 공개 코드와 분리하는 private
  `gohyunsu/aneurysm-paper` 저장소

### Rationale

2026년 직접 경쟁 연구가 inflow-aware GNN, graph transformer, masked
pretraining, physics-informed multimodal fusion을 이미 제안했다. 단순 구조
추가는 novelty가 약하고, 현재 surrogate는 deployment 때 필요한 초기
velocity/inflow를 가정한다. AURORA는 그 가정 자체를 연구 문제로 삼는다.

### Evidence status

- 문헌·설계: reviewed as of 2026-08-03
- AURORA implementation: protocol and architecture specification
- AURORA experiments: not started
- clinical validation: not performed
