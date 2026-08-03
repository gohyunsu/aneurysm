# Changelog

연구 결정, 데이터 계약, 모델 설계, 실험 프로토콜, 사이트 변경을 함께
기록한다. 단순 오탈자는 묶어서 기록할 수 있지만 연구 주장을 바꾼 변경은
독립 항목으로 남긴다.

## 2026-08-03 · Novelty reset: coherent partial-condition operators

### Research

- ICLR 2026 boundary-indexed operator family, function-space flow/diffusion
  operator, neural-process consistency, PDE OOD-UQ를 직접 경쟁 선행연구로
  추가했다.
- Missing-BC 문제 정의, probabilistic operator, GNN+physics, Fourier
  decoder를 독립 novelty에서 제외했다.
- Primary contribution을 arbitrary observation mask의 nested
  condition–marginal coherence, same-geometry paired simulator response,
  BC-induced/model-induced uncertainty separation으로 재정의했다.
- AURORA의 정식 명칭을 **Aneurysm Uncertainty-aware Reconstruction Operator
  for Reliable Assessment**로 바꿔 현재 근거가 없는 `Risk-aligned` 표현을
  제거했다.

### Protocol

- Exact controlled PDE → nonlinear PDE → irregular 3D의 세-domain 검증을
  AAAI general-method gate로 고정했다.
- CMHA rupture-status diagnostic은 음성 exploratory signal을 반영해
  primary gate에서 secondary analysis로 이동했다.
- One-shot Fourier decoder는 D0 oracle 및 learned compute-matched 비교를
  통과할 때만 남기는 engineering choice로 낮췄다.

### Experiment

- BenchAnXplore D0 첫 실행은 30분 32초에 scheduler walltime exit `-29`로
  종료됐다. Aggregate metric이 생성되지 않아 과학적 verdict는
  `unresolved`다.
- 실패 attempt를 공개 aggregate provenance로 남기고, metric·threshold는
  바꾸지 않은 채 walltime 60분과 case-count progress log만 추가했다.
- Exact conditional distribution을 계산할 수 있는 Poisson family의 G1을
  5 seeds로 사전 등록했다. Joint Gaussian BC density, arbitrary-mask
  analytic conditioning, shared solution operator, paired-response loss와
  direct masked Gaussian baseline을 구현했다.
- Pinned experiment container에서 2-epoch CPU runtime smoke를 완료해
  tensor shape, conditioning, sampling, metric serialization을 검증했다.

### Site

- 메인 페이지와 11장 field guide의 architecture, gate, contribution,
  glossary를 v2 연구 질문으로 동기화했다.
- Full·partial·missing 모드가 하나의 joint BC density를 공유하는 과정과
  paired response·두 uncertainty 축을 배경지식 없이 읽을 수 있게 설명했다.

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
