# Aggregate research results

이 디렉터리는 공개 가능한 **aggregate exploratory result**만 버전 관리한다.

포함:

- 실행 code commit과 protocol 상태
- cohort 전체 수와 class count
- patient-grouped aggregate metric과 bootstrap CI
- GPU/container version
- 해석 제한과 다음 결정
- metric이 생성되지 않은 scheduler failure의 비식별 상태·exit·walltime
- 필수 seed가 모두 완료되지 않아 gate를 판정할 수 없는 execution record

제외:

- source patient identifier
- row-level label·prediction·split
- 내부 서버 경로와 job endpoint
- raw table checksum과 protected asset
- checkpoint와 log 전체

`exploratory` 결과는 confirmatory gate 통과로 해석하지 않는다. 공식 case
mapping, feature provenance, 사전 정의 model family와 protocol을 모두
확인한 run만 confirmatory로 승격한다.

현재 ISBI task-translation 결과:

- `goal_oriented_s0a_cmha_stage_v1_execution_20260809.json`: exact source
  `b6b6175…`의 CMHA staging v1 execution-incomplete provenance. CPU/PBS job은
  exit 28이었고 verified/retained archive는 0 byte, raw stdout은 없었다.
  S0a는 `not_evaluated`이며 데이터 결과나 gate 판정이 아니다. 같은 v1
  source는 재제출하지 않고 one-change chunked v2를 별도 등록했다.
- `flow_mri_protocol_i0b_execution_20260809.json`: exact source
  `0ebdb344…`의 one-shot CPU/PBS 실행 기록. Registered wrapper가 기존
  read-only `h5py==3.12.1` layer를 누락해 archive/field access 전 exit 1로
  끝났고 cache/result는 생성되지 않았다.
  Gate는 미평가이며 scientific verdict가 아니다. Raw log·hostname·server
  path는 비공개로 두고 checksum만 기록한다. 등록된 no-rerun rule에 따라
  dependency를 보충한 I0b 재실행이나 I0c/method/GPU 권한은 없다.
- `flow_mri_protocol_i0a_asset_audit_20260808.json`: exact source
  `f7b4e024`의 post-discovery, field-free paired-protocol asset audit. 두
  official archive의 174/76 entry, descriptor/header 9/8개와 frozen protocol
  contract를 확인해 14/14를 통과했다. Processed RAW/REC read는 0이다. 이
  pass는 selective private staging과 learned-method-free I0b 등록만 허용하며
  task adequacy, posterior identifiability, method, novelty, outer test와
  submission evidence가 아니다.
- `aneumo_isbi_v0_20260808.json`: exact source `0589070`의 metadata-only
  8/8 pass. 새 field array와 validation/test field를 읽지 않았으며 V1
  64-case implementation smoke만 허용한다. Learned performance, outer
  test, headline과 submission evidence가 아니다.
- `aneumo_isbi_v1_20260808.json`: task source `a0479fb`의 12/12 checkpoint와
  aggregate source `78dca92`의 exact replay 결과. Gate는 5/7 fail이며 선택
  q-PointNet worst-seed full-q/response L2가 `1.03459/1.00354`였다. Test field,
  V2, headline과 submission은 닫혀 있고 current backbone branch를 중단한다.
- `aneumo_isbi_v1_attribution_20260808.json`: exact source `3a0d27f`가 같은
  12개 checkpoint를 train/validation에서만 replay한 threshold-free V1a
  aggregate. 네 family의 train full-q L2도 `0.76939--0.95647`이고 norm/cosine
  collapse가 나타나므로 실패는 geometry generalization만의 문제가 아니다.
  V1 relabel, retraining, model/V2 선택과 method novelty 권한은 없다.
- `aneumo_isbi_v1b_boundary_asset_audit_20260808.json`: exact source
  `fb1c21a`의 post-discovery asset-identifiability audit. 20 ZIP64 archive,
  64 case, 384 required member와 train representative 60 VTP를 확인해 8/8을
  통과했다. Validation/test payload와 field value는 읽지 않았으며 V1c
  boundary-geometry staging audit 등록만 허용한다. Model, V2/test, novelty와
  submission evidence가 아니다.
- `aneumo_isbi_v1c_boundary_geometry_staging_audit_20260808.json`: exact source
  `84fc244`의 train-only geometry-staging audit. 20 representative case,
  60 patch, 180 payload를 확인해 8/8을 통과했다. 60/60 patch가 세 flow에서
  exact invariant였고 minimum polygon-valid fraction은 1.0이었다. Field array,
  validation/test payload와 model/checkpoint는 읽지 않았다. V1d development
  geometry-cache protocol 등록만 허용하며 model, V2/test, novelty와 submission
  evidence가 아니다.
- `aneumo_isbi_v1d_development_geometry_cache_20260808.json`: exact source
  `369317a`의 development-only geometry audit. Train 40·validation 12·test 0,
  boundary 468개와 reference-volume 52개 payload를 확인해 9/9을 통과했다.
  156/156 patch가 q-invariant였고 52/52 case에서 boundary points가 volume
  points에 exact하게 대응했다. Field array와 test payload는 읽지 않았다.
  V1e known-condition protocol 등록만 허용한 asset evidence이며 model,
  missing-condition, novelty 또는 submission evidence가 아니다.
- `aneumo_isbi_v1e_known_condition_baseline_20260808.json`: exact source
  `c62838b`의 fresh three-seed matched-budget known-condition qualification.
  Six A6000 task가 모두 exit 0이었고 boundary는 validation full-q/response에서
  3/3 seed로 geometry-only control보다 좋았으며 mean 상대 개선은
  `10.94%/6.41%`였다. 그러나 worst-seed train/validation full-q와 response
  L2 `0.77221/0.87796/0.94918`이 frozen `0.25/0.35/0.50`을 모두 넘어서
  6/9 fail이다. Current Aneumo 3D learning line을 local repair 없이 중단하며
  missing-condition, V2, novelty 또는 submission을 열지 않는다.

현재 controlled-PDE 결과:

- `nonlinear_pde_n1_missing_operator_pullback_m0_execution_20260808.json`:
  exact source `89bdc85`의 M0 3-seed array 실행 record. Seed 0/2만 exit 0,
  seed 1은 truncated conditional rejection stall로 exit 1이었다. Aggregate와
  과학적 pass/fail은 없고 성공 seed metric은 gate 용도로 검사하지 않았다.
  Sampler repair·rerun·fresh re-entry·method/N1d/3D 권한은 없다. 이 파일은
  metric aggregate가 아니라 공개 가능한 실행 provenance다.

- `controlled_pde_g1_attempt2_20260803.json`: frozen G1 실패
- `controlled_pde_g1b_20260803.json`: raw estimator floor와
  density/operator/MC attribution만 수행한 post-result diagnostic
- `controlled_pde_g1r_20260803.json`: fresh seed와 validation-only
  selection을 고정한 prospective re-entry 실패
- `controlled_pde_density_attribution_20260803.json`: threshold 없이
  capacity, finite-condition noise와 geometry×condition allocation을 분리한
  post-result DA1
- `controlled_pde_density_development_20260803.json`: grouped moment와
  shrinkage를 original budget에서 비교하고 high-data control을 분리한 DA2
- `controlled_pde_g1s_20260803.json`: G1r pipeline을 유지하고 training
  geometry만 768→3,072로 늘린 fresh 5-seed prospective data-adequacy pass
- `nonlinear_pde_n0_20260803.json`: 8/9 numerical/problem-design check를
  통과했지만 worst-seed nonlinear departure가 frozen 기준에 못 미친
  prospective N0 실패
- `nonlinear_pde_n0_attribution_20260803.json`: failed N0 seed의 24×12
  전체 context-condition grid에서 contiguous slicing 민감도를 확인한
  threshold-free N0a
- `nonlinear_pde_n0r_20260805.json`: N0a outcome 전에 동결한 fresh seed와
  24-context-stratified selector로 9/9 numerical/problem-design check를
  통과한 prospective re-entry
- `nonlinear_pde_n1_core_development_20260805.json`: test access 없이
  joint density와 lifted operator만 점검했고 operator 자격이 부족해
  confirmatory path를 열지 않은 validation-only development
- `nonlinear_pde_n1_core_development_unit_peak_20260805.json`: 동일 함수
  클래스의 unit-peak envelope로 크게 개선됐지만 0.05 기준을 넘어서
  insufficient로 유지한 두 번째 validation-only development
- `nonlinear_pde_n1_optimization_attribution_20260805.json`: test 없이
  train-only RMS-normalized loss와 2,800-step horizon을 선택한 N1a
- `nonlinear_pde_n1b_checkpoint_manifest_20260805.json`: exact source에서
  다섯 validation-only seed의 50개 checkpoint와 공통 POD hash를 동결한
  pre-test manifest

G1b는 G1을 대체하거나 재개방하지 않는다.
G1r도 coverage·operator·analytic nesting·iid-floor 보정 projective 항은
통과했지만, 최악 seed의 density-only mean 0.07533과 end-to-end
quadrature mean 0.07518이 사전 기준 0.05를 넘었다. 상대 baseline 개선으로
이 absolute 실패를 덮지 않으며 nonlinear/3D confirmatory 학습은 계속
보류한다.

DA1에서는 같은 density network가 analytic population NLL로 최악
density-only error 0.00495를 회복했지만 empirical NLL은
0.04401–0.04855였다. Fixed-axis scaling은 geometry 수와 반복 condition
수가 모두 오차를 줄임을 보였다. 이 attribution은 새 gate가 아니며,
development-only estimator 선택 뒤 별도 fresh exact sanity가 필요하다.

DA2의 formal selection은 grouped shrinkage 0.50이었지만 empirical NLL
대비 평균 개선은 0.23%뿐이고 seed-robust하지 않았으므로 method로 승격하지
않는다. 3,072×8 empirical NLL의 최악 error 0.02706만 data-adequacy
후보를 지지한다. 이는 새 gate 통과나 novelty evidence가 아니다.

G1s는 이전 모든 seed와 겹치지 않는 5개 seed에서 7개 frozen check를 모두
통과했다. 최악 density-only/end-to-end mean은 0.02863/0.02977,
coverage error는 0.00836/0.01294, projective CI upper는 0.000674였다.
G1/G1r은 failed로 유지한다. 이 결과는 nonlinear/3D protocol 등록을
허용하는 data/pipeline sanity이며, data quantity나 exact toy 성능은
method contribution이 아니다.

N0는 solver와 multicomponent response가 안정적이었지만 seed-wise
nonlinear-departure minimum 0.00727이 threshold 0.01보다 낮아 실패했다.
사후에 발견한 context-major contiguous slicing은 attribution 대상이지
소급 합격 사유가 아니다. N1/3D는 차단하고, threshold-free all-context
diagnostic과 fresh-seed stratified N0r만 허용한다.

N0a에서 failed seed의 contiguous/stratified/all-case median은
0.00774/0.01221/0.01828이었다. 이는 contiguous context-0 statistic의
대표성 문제를 지지한다. 그러나 former reference를 넘는 context는
18–19/24이므로 uniformly strong nonlinearity를 주장하지 않는다. N0a에는
gate가 없고 N0 실패와 N1/3D 차단은 그대로다.

N0r는 exact `37d31a8`에서 worst-seed nonlinear departure 0.01933,
maximum grid error 0.00375, minimum worst-component response 0.17484로
9/9를 통과했다. N0 failed history는 그대로이며, 이 결과는 N1 상세
사전등록만 허용한다. Learned superiority, method novelty와 irregular-3D
headline은 아직 허용되지 않는다.

첫 N1 core development는 exact `6075530`에서 exit 0이었고 joint-density
validation NLL -4.290을 얻었다. 그러나 lifted operator full-BC와
paired-response relative L2는 0.1739/0.1862로 insufficient였다. Test
split과 seed는 접근하지 않았으며 N1 gate는 결정되지 않았다. Unit-peak
envelope 재척도화는 동일 함수 클래스의 optimization diagnostic이고
threshold 완화가 아니다.

Unit-peak attempt는 full-BC/paired-response L2를 0.05771/0.05729로
낮췄지만 unchanged 0.05를 통과하지 못했다. N1a는 이 결과 뒤 학습
horizon과 train-only loss normalization을 분리하는 threshold-free
validation attribution이며 gate 결과로 수록하지 않는다.

N1b는 exact `1d0bd9c`에서 다섯 checkpoint job이 모두 exit 0,
eligibility true, test access false로 완료됐다. AURORA validation
full-BC/paired-response mean은 0.01347/0.01366이지만 DeltaPhi-style
combined objective보다 좋은 seed는 0/5였다. 이 manifest는 비교 대상을
고정할 뿐 superiority나 N1 pass가 아니다. 별도 prospective execution
overlay 전 outer test는 생성하지 않는다.

현재 temporal representation 결과:

- `benchanxplore_d0_attempt2_20260803.json`: fixed Fourier K=8 실패,
  K=12도 bulge 기준 실패
- `benchanxplore_d0b_20260803.json`: DCT-II 탈락, train-only POD
  rank 17/25 representation screen 통과

D0b 통과는 learned one-shot 성능이나 novelty를 뜻하지 않는다. 같은
105-case benchmark의 후속 learned 비교는 exploratory이며 fresh transient
confirmation이 필요하다.

현재 Aneumo response-eligibility 결과:

- `aneumo_scaling_audit_20260803.json`: 20 train base family·40 case만 읽은
  사전등록 strong physical-scaling audit
- velocity: tuned \(Q^{1.075}\) residual 0.2112,
  family-bootstrap CI95 [0.2001, 0.2243] · channel eligibility 통과
- pressure: gauge-removed tuned \(Q^{1.75}\) residual 0.1369,
  CI95 [0.1190, 0.1496] · eligibility 실패

이는 같은-case anchor field까지 사용하는 강한 물리 baseline 뒤에도
velocity response가 남는다는 train-only 결과다. Learned model 성능이나
G2 통과는 아니다. G1s pass로 velocity-only protocol 등록은 가능하지만
nonlinear C1/C2 strong-baseline 검증을 먼저 수행한다.
