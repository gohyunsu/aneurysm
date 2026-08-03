# Changelog

연구 결정, 데이터 계약, 모델 설계, 실험 프로토콜, 사이트 변경을 함께
기록한다. 단순 오탈자는 묶어서 기록할 수 있지만 연구 주장을 바꾼 변경은
독립 항목으로 남긴다.

## 2026-08-03 · Prospective exact-G1 re-entry registration

### Experiment

- Frozen G1과 exploratory G1b의 config/result checksum을 pin하고, 기존
  seed와 겹치지 않는 5개 fresh seed를 `controlled_pde_g1r.json`에 실행
  전에 고정했다. Failed G1은 relabel하지 않는다.
- Boundary density는 full-BC NLL로 별도 학습하고 geometry-disjoint
  validation NLL로 checkpoint를 선택한다. Operator와 direct baseline도
  validation split에서만 early stopping하며 test split은 선택 뒤 생성한다.
- Density-only conditional moment·coverage는 exact affine Poisson
  pushforward로, end-to-end mean은 Gauss–Hermite quadrature로 계산한다.
  Projective metric은 raw two-sample distance가 아니라 matched iid floor
  대비 signed excess의 across-seed 95% CI upper bound다.
- Mean 0.05, coverage 0.03, full-BC operator 0.03, projective excess upper
  0.01, analytic nesting residual \(10^{-6}\) threshold를 결과 전에
  machine-readable protocol과 validator에 고정했다.

### Scope

- G1r pass는 새 exact-domain sanity evidence일 뿐 frozen G1 pass, baseline
  superiority, C1 novelty 또는 AAAI readiness를 뜻하지 않는다.
- G1r failure 시 nonlinear/3D confirmatory 학습으로 확장하지 않고 density
  family와 data sufficiency를 다시 분석한다.

### Site

- 공개 gate와 실행 상태 창에 “G1 failed / G1b diagnostic complete / G1r
  preregistered and unrun”을 분리해 표시했다.

## 2026-08-03 · Aneumo selective paired-BC pilot registration

### Data

- 공식 Aneumo ZIP64 release의 중앙 디렉터리를 HTTP byte-range로 감사해
  첫 shard의 40 geometry 각각에 동일 좌표의 8개 steady mass-flow
  condition이 있음을 확인했다.
- Geometry 1의 두 internal NPY member를 실제 range-read해 CRC32,
  `(N,7)=xyz+pressure+velocity`, condition 간 좌표 동일성을 확인했다.
- Upstream `Connection.csv`의 AneuX ancestry를 반영해 synthetic case가
  아니라 32개 base family에서 split하고, family마다 두 deformation만
  선택하는 64-case 파일럿을 학습 결과 전에 등록했다.

### Implementation

- 전체 multi-terabyte release를 받지 않고 필요한 ZIP member만 읽는
  ZIP64 range ingester를 추가했다. Exact `206 Content-Range`, central/local
  record 일치, member CRC, condition 좌표 일치와 compact-cache SHA-256을
  검증한다.
- 8 conditions × 4,096 nodes를 compact HDF5로 기록하되 raw/derived field를
  CC BY-NC-ND 조건 아래 공개 저장소에 재배포하지 않는 계약을 고정했다.
- 이 파일럿은 steady same-geometry response C2와 base-family-disjoint
  irregular-3D 평가만 지원한다. Multicomponent partial-BC C1, transient
  efficiency, clinical utility의 근거로 사용하지 않는다.

### Research

- AAAI-26 LANO, NeurIPS-25 DeltaPhi, 2026 conditioning-operator 선행연구를
  반영해 partial observation, residual pair learning, analytic
  conditioning 자체를 novelty에서 제외했다.
- C2는 DeltaPhi-style residual baseline, pair-loss-zero, random
  cross-geometry pair를 matched data/compute로 모두 이겨야 유지한다.

## 2026-08-03 · Failed-G1 attribution and temporal-contract correction

### Experiment

- `G1b`를 frozen G1 뒤의 명시적 post-result diagnostic으로 구현했다.
  Frozen model·5 seeds·geometry split·500 epoch를 그대로 재학습하고
  \(K=128/512/2048\)에서 iid two-sample floor와 양방향 nested sampling을
  비교한다.
- Exact Poisson의 선형성을 이용해 conditional-mean error를 sampling only,
  BC-density only, operator only, end-to-end로 분해한다. G1b는 새 gate가
  아니며 완료·양수 결과 모두 기존 G1 실패를 재개방하거나 relabel하지 않는다.
- Pinned Singularity 환경에서 G1b tensor test 4개와 축소 end-to-end
  학습→sampling→attribution→aggregation smoke를 통과했다. 전체 suite의
  나머지 오류 2개는 기본 SIF에 BenchAnXplore용 외부 `h5py` layer가 없는
  기존 환경 차이로 분리했다.
- Exact commit `8e24950`의 G1b가 PBS A6000에서 exit 0, walltime 45초로
  완료됐다. \(K=128\) learned direct-vs-nested 0.1006은 iid floor
  0.1013과 같고 analytic moment residual은 \(7.45\times10^{-9}\)였다.
- 그러나 \(K=2048\) missing-mask end-to-end mean error 0.0853 중
  density-only가 0.0754로 남았다. Raw projective metric의 실패는
  설명했지만 learned conditional distribution은 지지되지 않으므로 G1을
  재개방하지 않았다. Coverage attribution도 unresolved로 명시했다.

### Model

- Frozen D0 실패 뒤에도 `configs/aurora_v1.json`과 상세 사이트에 남아 있던
  `temporal_fourier_modes=8` 현행 표시를 제거했다.
- D0b는 17/25 equal coefficient budget의 DCT-II와
  train-geometry-only temporal POD만 geometry-disjoint로 비교한다. 새
  oracle gate와 learned compute-matched 비교 전에는 one-shot temporal
  branch를 선택하지 않는다.
- 5-fold POD covariance fit과 held-out evaluation의 two-pass 실행을
  구현했다. Pinned container에서 DCT orthonormality, span reconstruction,
  held-out covariance exclusion, 4-case synthetic runtime의 9개 검사를
  통과했다.
- Exact commit `1dfc856`의 105-case D0b가 A6000에서 exit 0, walltime
  3분 49초로 완료됐다. DCT-II rank 17/25는 탈락했고 train-only POD
  rank 17/25는 모든 frozen representation threshold를 충족했다.
- POD-17은 full L2 0.00141, bulge L2 0.00880, peak error 0.000764였다.
  POD-25도 통과했지만 아직 selected architecture가 아니며 두 rank를
  learned inner validation 후보로만 둔다.
- D0b의 105 case 전체가 architecture discovery에 쓰였으므로 같은
  BenchAnXplore에서의 learned comparison을 exploratory로 제한했다.
  Confirmatory G3는 fresh transient case 또는 독립 pulsatile dataset에서
  재현하도록 protocol validator에 고정했다.

### Site

- 11장 상세 가이드의 temporal 창을 계획형 Fourier 설명에서 실제 실패
  수치, global-energy 함정, DCT/POD 후보, leakage 방지 규칙으로 교체했다.
- G1b aggregate 결과와 “projective floor 설명 ≠ learned distribution
  성공” 경계를 변경 이력과 실행 상태 창에 추가했다.
- D0b의 DCT/POD별 실제 수치와 “representation eligibility ≠ learned
  superiority” 및 same-benchmark selection leakage 경계를 사이트에
  반영했다.

## 2026-08-03 · Novelty reset: coherent partial-condition operators

### Research

- 추가 red-team에서 2026 conditioning-consistency gap, Neural Operator
  Processes, learned boundary extension, Generalized Neural Operator를 직접
  경쟁 선행연구로 반영했다.
- Partial/missing BC의 ID coherence·calibration, 값이 제공된 full-BC
  support-shift response, hidden-BC law shift의 detection/abstention을
  분리했다. 식별 불가능한 OOD hidden-law coverage 주장을 제거했다.
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

- BenchAnXplore D0 attempt 2가 정상 완료됐지만 frozen \(K=8\) gate는
  실패했다. Full relative L2 0.0162, peak error 0.0214, bulge relative
  L2 0.0616이었고, \(K=12\)도 bulge 0.0293으로 기준 0.02를 넘었다.
- Exact controlled G1도 maximum mean error 0.1685, coverage error 0.0377,
  raw projective distance 0.1129로 frozen gate를 실패했다. 다만 direct
  masked Gaussian보다 모든 mask의 mean error와 energy score가 좋고 raw
  projective distance가 모든 seed에서 낮은 상대 신호는 보존했다.
- 두 실패를 confirmatory aggregate artifact로 공개했다. Raw two-sample
  distance의 finite-sample floor와 sampled mean의 density/operator/MC
  error를 분해하는 G1b는 post-result exploratory로만 실행한다.
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
- 첫 G1 submission은 GPU 실행 전 `Q` 상태에서 2,000회 geometry-bootstrap
  CI가 result JSON에 빠지는 것을 발견해 취소했다. Point estimate를 본 뒤
  고치는 일을 피하기 위한 pre-run correction이다.
- Geometry-family cluster bootstrap과 95% CI 직렬화를 구현하고 pinned
  container smoke에서 `geometry_bootstrap_ci95` 생성을 확인했다.

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
