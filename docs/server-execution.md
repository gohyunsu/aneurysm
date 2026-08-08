# AURORA 서버 실행과 provenance

최종 갱신: 2026-08-09 KST

이 문서는 재현에 필요한 역할과 절차만 공개한다. SSH endpoint, 내부 절대
경로, credential, patient-level row와 prediction은 기록하지 않는다. 실제
운영 명령과 private path는 Git에서 제외된 `SERVER_GUIDE.md`를 따른다.

## 서버 역할

| 서버 계정 | 역할 | 허용 작업 |
|---|---|---|
| `introai9` | source asset registry·데이터 감사 | 원본·추출본·매니페스트 read-only 확인, CPU metadata/asset audit |
| `junjinyong` | GPU 실행 목표·scheduler provenance | PBS allocation 안의 pinned-container smoke·학습·평가 |

원자료를 로컬 저장소에 내려받거나 서버 사이에 전체 복제하지 않는다. 실행
서버에서는 필요한 source root를 read-only로 bind하고 run output만 writable로
둔다. 어느 서버에서도 login node GPU를 사용하지 않는다. `introai9`의 asset을
서버 사이에 임의 복제하지 않으며, `junjinyong`에서 필요한 read-only staging과
container·cache SHA smoke를 확인하기 전 learned job을 제출하지 않는다.

## 2026-08-09 · Goal-oriented S0a runtime discovery

- `junjinyong` login node에서 `/etc/profile` 뒤 PBS `qsub/qstat`, target queue와
  Singularity CE 3.11.3을 read-only로 확인했다. GPU API와 `nvidia-smi`는
  호출하지 않았다.
- 기존 pinned PyTorch 2.5.1/CUDA 11.8 image는 공유 영역에서 읽을 수 있지만
  SciPy, trimesh, PyVista, meshio, VTK, FEniCS와 JAX를 포함하지 않는다.
  Host에서도 OpenFOAM, SU2, VMTK, FEniCS와 Gmsh executable을 확인하지 못했다.
- 이는 S0a outcome이 아니라 registration-before-execution discovery다.
  `configs/goal_oriented_segmentation_s0a.json`은 별도 solver image의 exact
  SHA-256, license, mesh/steady-forward와 discrete-adjoint 또는 검증 가능한
  shape-gradient capability를 필수 check로 둔다.
- CMHA full archive에 대한 bounded shared-storage query는 SSH handshake reset으로
  끝났고 재시도 loop를 돌리지 않았다. 기존 공개 row audit만 보존하며 105
  lesion exact-ID linkage를 아직 통과로 표시하지 않는다.
- S0a는 CPU-only PBS, source/code read-only, output writable, aggregate-only다.
  Pass도 S0b 등록만 열고 segmentation training, GPU와 outer test를 금지한다.

## 2026-08-08 · Cross-protocol 4D-flow I0a

- `configs/flow_mri_protocol_i0a_asset_audit.json`은 공식 Zenodo API와 HTTP
  byte range만 쓰는 CPU metadata audit이다. GPU job이 아니며 login node에서
  GPU API를 호출하지 않는다.
- 등록 전에 두 record, central directory, nine descriptor와 eight primary
  header를 본 범위를 result와 함께 보존한다. 이는 prospective performance
  evidence가 아니다.
- Processed RAW와 REC field payload는 읽지 않고, archive 전체도 내려받지
  않는다. Exact public commit과 config SHA, command, environment, 14-check
  result와 status만 private output에 남긴다.
- Pass 뒤에도 selective staging protocol을 별도 commit하기 전 field를 읽지
  않으며, learned method나 PBS GPU training을 제출하지 않는다.
- Exact public source `f7b4e024d69d43cf042f4163342b4d993386f441`의 pinned
  container run은 exit 0, 14/14 pass였다. ZIP entry 174/76개, descriptor/header
  9/8개를 CRC 검증했고 processed RAW/REC read는 0이었다. Public aggregate는
  `results/flow_mri_protocol_i0a_asset_audit_20260808.json`, SHA-256
  `2243172a720b25ebebd6052b9c0989880d95cba5b8d984f8980f70cf5f26d9c6`다.
  Task adequacy나 method evidence가 아니며 별도 I0b 등록만 연다.

## 2026-08-09 · Cross-protocol 4D-flow I0b registered

- Exact executable contract는
  `configs/flow_mri_protocol_i0b_task_adequacy.json`, SHA-256
  `e19a1194f1b9ec41861c5084b26c9add5be47924a19aee4d23ffc826399dce06`다.
- Registration 전 2021 official README/reader와 Zenodo `17183575` official
  record, 세 central directory, 33 primary PAR header를 확인한 범위를 공개했다.
  Velocity field와 REC는 읽지 않았다.
- Formal I0b는 `introai9`의 scheduler CPU allocation과 pinned container에서
  실행한다. 2021 processed RAW 27개만 HTTP byte-range/CRC로 읽고 private
  HDF5 common-grid cache를 만든다. Source는 read-only, output만 writable이다.
- 공개 wrapper `cluster/pbs_flow_mri_protocol_i0b_cpu.pbs`는 8 CPU/48 GB,
  exact source commit, source read-only, output writable와 기존 scientific
  output 거부를 강제한다. Queue·container·private absolute path는 제출 시
  환경으로만 주입하며 GPU resource와 `nvidia-smi`는 요청하지 않는다.
- 2025 intervention release의 132 REC member는 존재/byte contract만 확인하고
  payload는 읽지 않는다. Checkpoint, method와 GPU는 사용하지 않는다.
- Pass도 `junjinyong` GPU job을 열지 않는다. 별도 method-free I0c decoder/noise
  protocol을 public exact commit으로 먼저 고정해야 한다. Failure 뒤 local
  registration·mask·threshold 수선이나 I0b rerun은 금지한다.
- **Outcome:** exact source `0ebdb344…`의 PBS job `115093`은 8 CPU/48 GB,
  GPU 없이 5분 7초 뒤 exit 1이었다. Registered wrapper가 과거에 쓰던
  read-only `h5py==3.12.1` layer를 bind하지 않아 `_scientific_imports()`에서
  중단됐다. Container SHA는 `2da7b186…`이고 raw
  log/status checksum은 public execution record에 고정했다. Archive request,
  RAW/field/PAR/REC read, cache/result 생성은 0이다. Gate는 미평가이며
  dependency를 보충한 rerun이나 I0c/GPU job을 제출하지 않는다.

## 2026-08-03 자산 감사

`introai9`에서 다음 자산의 존재를 직접 확인했다.

| 데이터 | 확인된 상태 | 다음 G0 작업 |
|---|---|---|
| Aneumo | 32 family/64 case selective cache, case당 steady BC 8개, checksum 검증 | train-only physical-scaling audit; learned G2 보류 |
| AneuG-Flow | geometry archive | CFD field release subset 확보 |
| BenchAnXplore | archive와 105-case × 80-step HDF5/XDMF | unit·boundary semantics; D0 audit |
| CMHA | archive, statistical table, patient 추출본 | 공식 case map, field/summary provenance |
| AneuX | metadata와 geometry archive/추출본 | patient/source split과 license |
| Aneurisk | source-native repository | AneuX overlap과 asset provenance |

파일의 존재는 G0 통과를 뜻하지 않는다. 현재 명시적 manifest는
BenchAnXplore 표본에만 확인됐으므로 dataset별 checksum·license·unit·case
mapping을 계속 보강한다.

## CMHA row audit

공개 통계표의 aneurysm 부분은 105개 병변, 99명 환자다. 6명에게 두 병변이
있고, 해당 6명은 병변별 rupture status가 다르다. 따라서 split과 bootstrap은
병변 행이 아니라 환자 그룹 단위여야 한다.

세 표의 row alignment는 다음과 같이 관찰됐다.

- clinical–hemodynamic identifier exact match: 104/105
- morphology identifier가 patient ID 또는 lesion suffix와 호환: 105/105
- 공식 release case map: 아직 미확인

현재 G1 run은 이 row alignment를 사용하는 **exploratory audit**이다.
confirmatory G1 전에 release data dictionary 또는 공식 case map으로
검증한다.

또한 정의가 확인되지 않은 `PHASE`, `ELAPSS` 두 열의 조합이 target을 거의
결정적으로 분리했다. 표준 PHASES/ELAPSS 계산임을 확인하기 전까지 이 두
열은 baseline에서 제외한다.

## BenchAnXplore D0 준비

- coarse archive: 105 HDF5 + 105 XDMF
- case tensor: 80 timestep velocity, tetrahedral coordinates/connectivity,
  repeated binary boundary mask
- archive SHA-256: `2116bf9e4feb4cd937b3a47a307821359a1010bcf6cc75d94fea70bcc639e579`
- runtime: pinned PyTorch container + read-only external `h5py==3.12.1` layer
- preregistration: `configs/benchanxplore_d0.json`

D0는 Fourier 4/8/12-mode reconstruction의 표현 손실만 측정한다. 학습된
operator 또는 In-PI-MGN 대비 성능으로 해석하지 않는다.

## GPU smoke

과거 `junjinyong`의 PBS `ssu_a6gpu` allocation 안에서 다음을 확인했다.

- GPU: NVIDIA RTX A6000 1장
- PyTorch: 2.5.1+cu118
- CUDA runtime: 11.8
- 2048 × 2048 CUDA matrix multiplication finite check: pass
- smoke exit status: 0

login node에서는 `nvidia-smi`나 학습을 실행하지 않았다.

## 2026-08-08 introai9 V1 scheduler audit

- PBS GPU smoke는 NVIDIA A100-SXM4-80GB, PyTorch 2.5.1+cu118, CUDA 11.8에서
  finite 2,048 × 2,048 matrix multiplication과 exit 0을 확인했다.
- 공식 release에서 서버 내 독립 재생성한 Aneumo compact cache는 64 case,
  512 member의 CRC 검사를 통과했고 등록 SHA-256
  `9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`와
  일치했다. Field와 cache는 공개 저장소에 복사하지 않는다.
- Exact `2ddd5e6`의 최초 V1 array와 same-source diagnostic은 metric 이전에
  실패했지만 PBS stdout이 반환되지 않았다. Exact `fd8bb40`은 task-local
  log를 남겨 pinned runtime이 device 객체를 받은 CUDA peak-memory reset을
  거부한 것을 cache load 전 traceback으로 분리했다.
- 이 source correction은 device 0을 선택하고 CUDA bookkeeping API를
  current-device 형식으로 호출한다. Scientific config와 selector는 그대로며,
  새 exact full contract와 one-task diagnostic을 모두 통과한 뒤에만 fresh
  12-task array를 제출한다. 기존 실패 artifact는 삭제하지 않는다.
- Exact task source `a0479fb`의 fresh array는 12개 checkpoint/metric과
  no-test-read 검사를 모두 통과했다. 첫 aggregate job은 result를 만들기 전에
  exit 1이었고 PBS가 지정 stdout을 반환하지 않았다. Aggregate wrapper에도
  task-local log/status fail-safe를 적용한 별도 ops source를 사용하되, model과
  12개 task artifact는 exact `a0479fb` read-only 상태로 replay한다.
- Observable replay는 cache `float32`의 `0.002499999944...`와 registered
  `0.0025`를 response-only oracle이 `1e-12`로 직접 비교해 result 전에
  중단됐음을 확인했다. Cache ordering은 기존 loader tolerance로 검증하고
  anchor와 ratio는 registered design value에서 계산한다. Aggregate code SHA와
  task/checkpoint SHA는 별도 provenance field로 남긴다.
- Aggregate source `78dca92`의 corrected replay는 exit 0으로 12개 checkpoint,
  validation replay, separate task/source provenance와 no-test-read를 확인했다.
  V1 gate는 5/7 fail이며 q-PointNet worst-seed full-q/response L2는
  `1.03459/1.00354`다. Public aggregate SHA-256은
  `f67970c4d8028bf869ae793a776ed86d32b9cc477a9ba414e54bf9c8fab6a9b1`이다.
  현재 branch를 재학습하지 않고 fixed-checkpoint V1a attribution만 등록한다.
- Exact source `3a0d27f`의 dependency-complete contract는 서버 고정
  container에서 183/183, V1a 전용 torch metric 5/5, protocol/site check를
  통과했다. PBS job `115051`은 실제 A100 80GB allocation에서 27초, exit 0으로
  완료됐고 12 checkpoint, train/validation field만 읽었다. Raw attribution
  SHA-256은 `4e11be6f3c73b338383c24a3c78902ad782f05f5e2ce0fa93e61b4351269d91a`다.
  Public aggregate는 raw의 family mean, truth-only diagnostic, access와
  authorization을 값 변경 없이 옮겼다. Test read, retraining과 checkpoint
  write는 없었다.
- 후속 asset discovery는 official ZIP64 archive 1의 central directory와 case
  1 q=0.0025 VTP header에 한정했다. Existing compact cache와 달리 official
  archive에는 mesh/STL, volume VTU, inlet/outlet/wall VTP와 connectivity,
  `U/p`가 있다. 이미 본 범위를 V1b config에 공개했다. Exact source
  `fb1c21a`의 CPU audit은 20 archives·64 cases, 384 required member와 60
  train representative VTP를 검사해 8/8을 통과했다. Validation/test payload와
  field arrays는 읽지 않았다. V1c는 geometry array decode 전에 고정됐고
  20 train representative×3 patch×3 flow에서 geometry-only q-invariance,
  topology, area/frame와 compact-cache coordinate frame만 감사해 exact source
  `84fc244`에서 8/8을 통과했다. 180 payload, 60/60 q-invariant patch,
  minimum polygon-valid fraction 1.0과 field/test-read false를 확인했다.
  V1d는 validation geometry payload decode 전에 고정됐으며 exact source
  `369317a`의 CPU run에서 train 40·validation 12·test 0 case의 boundary 468개와
  volume 52개 geometry payload를 감사해 9/9을 통과했다. 156/156 patch의
  q-invariance와 52/52 exact boundary-volume correspondence를 확인했다. 이
  asset pass 뒤 V1e known-condition baseline을 학습 전에 고정했다. Exact
  `c62838b`의 6개 GPU task는 login node가 아닌 PBS A6000 allocation에서 모두
  exit 0으로 완료됐다. 각 task는 exact source, 두 private cache checksum,
  pinned container/dependency, CUDA device, validation-only checkpoint와 no-test
  access를 기록했다. CPU-only pinned-container aggregate가 6 task provenance를
  전수 검사했고 gate는 6/9로 실패했다. Public aggregate SHA-256은
  `63fdb3a6fbddb15bb8d6cb82fde7b6880e3b3c7badef46b7a4cc2da4d31f2c0e`다.
  Raw log, checkpoint와 per-task history는 private output에만 보존한다.

## Run contract

각 run은 최소한 다음을 남긴다.

```text
git_commit.txt
command.txt
environment.json
run_config.json
dataset_manifest.sha256
status.json
metrics.json
```

실패 run도 삭제하지 않는다. 첫 grouped-fold 구현 오류 run은 빈 fold를
감지하고 즉시 종료됐으며, 수정 commit에서 synthetic unit test와 실제
CMHA split smoke를 통과한 뒤 다시 제출했다.

공개 PBS template:

- `cluster/ssu_a6gpu_smoke.pbs`
- `cluster/ssu_a6gpu_contract_tests.pbs`
- `cluster/ssu_a6gpu_cmha_g1.pbs`
- `cluster/ssu_a6gpu_benchanxplore_d0.pbs`
- `cluster/ssu_a6gpu_controlled_g1r.pbs`
- `cluster/ssu_a6gpu_controlled_g1s.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n0.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n0_attribution.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n0r.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n1_development.pbs`
- `cluster/ssu_a6gpu_nonlinear_pde_n1_optimization_attribution.pbs`
- `cluster/ssu_a6gpu_controlled_density_attribution.pbs`
- `cluster/ssu_a6gpu_controlled_density_development.pbs`
- `cluster/pbs_gpu_smoke.pbs`
- `cluster/pbs_aneumo_isbi_v1.pbs`
- `cluster/pbs_aneumo_isbi_v1_aggregate.pbs`

V1 template에는 queue 이름을 고정하지 않는다. 제출 시 private 운영 가이드에
따라 `introai9`의 허용 queue를 명시하며, login node에서는 GPU runtime을
조회하지 않는다. 12개 model×seed task가 모두 완료된 뒤 별도 aggregate job이
checkpoint를 validation-only로 replay한다. Aggregate는 같은-q seed 평균,
seed×8 q의 24-component missing mixture, response-only physical oracle,
lexicographic selector와 7개 feasibility check를 계산한다. Raw checkpoint와
per-task log는 private output에 보존한다.

첫 exact `2ddd5e6` V1 array는 세 subjob이 metric/checkpoint 생성 전 동일한
exit 1로 끝나 pending subjob을 취소했다. PBS stdout 반환도 exit finalization에
머물러, model/config를 바꾸지 않고 task output 내부에 `pbs.log`와
`pbs_status.json`을 직접 기록하도록 execution wrapper만 보강한다. 실패
artifact는 보존하며 새 exact contract와 one-task diagnostic 전에는 full
array를 재제출하지 않는다.

G1r template은 기존 G1 실패를 덮어쓰지 않는다. Public source commit과
`configs/controlled_pde_g1r.json`을 read-only로 bind하고 새 output
directory만 writable로 둔다. Density/operator checkpoint selection이 끝난
뒤 fresh test split을 생성하며, scheduler artifact에는 config checksum과
`failed_g1_relabeled=false`를 남긴다.

Exact commit `951ace1`의 full G1r은 A6000에서 정상 완료됐지만 gate는
실패했다. Public aggregate는
`results/controlled_pde_g1r_20260803.json`이다. 동일 fresh seed를
architecture 선택에 재사용하지 않으며, 다음 GPU job은 별도의 post-result
density attribution만 허용한다. Aneumo 학습과 nonlinear/3D confirmatory
job은 새 exact sanity 근거 전까지 제출하지 않는다.

Post-G1r density attribution은 별도 세 diagnostic seed에서 density
network만 학습한다. True-parameter, analytic population NLL, empirical
NLL과 matched-budget geometry×condition cells를 비교하며 result threshold가
없다. Exact commit, config checksum, environment, status와 aggregate
metric을 남기되 G1/G1r status는 항상 failed로 보존한다.

Nonlinear N0는 exact `0ead687` source와 pinned container로 실행했다.
Dependency-complete contract 90개와 metric job은 모두 exit 0이었으나
worst-seed nonlinear departure가 frozen threshold를 통과하지 못했다.
공개 aggregate는 `results/nonlinear_pde_n0_20260803.json`이다. 완료된
solver 실행을 성공한 method 실험으로 표현하지 않으며 N1과 3D job은
N0 re-entry 전까지 제출하지 않는다.

N0a는 같은 pinned container와 A6000 allocation에서 실행하되
`configs/nonlinear_pde_n0_attribution.json`을 read-only로 bind한다.
원래 N0 seed의 all-context diagnostic만 생성하며 status artifact에는
`has_gate_decision=false`, `n0_status=failed_unchanged`,
`n1_authorized=false`를 반드시 남긴다.

Exact `749f596` N0a는 A6000에서 exit 0으로 완료됐다. 첫 contract 제출은
외부 h5py layer를 누락해 unrelated BenchAnXplore test 하나가 metric 전에
실패했고, 동일 source에 pinned `h5py==3.12.1` layer를 추가한 재실행은
97/97 test를 통과했다. 공개 aggregate는
`results/nonlinear_pde_n0_attribution_20260803.json`이다.

N0r는 exact preregistration commit `1a68053`의 config를 이후 source
commit에서도 그대로 pin한다. PBS artifact에는 config checksum, exact
execution commit, reference/paired flat indices, represented-context count와
모든 check를 남긴다. N0r metric은 dependency-complete contract test가
같은 execution source에서 통과한 뒤에만 제출한다.
Exact `37d31a8`의 dependency-complete PBS contract는 105/105 test를
통과했고, 이어진 fresh 3-seed A6000 metric job은 exit 0으로 9/9 check를
통과했다. 공개 aggregate는 `results/nonlinear_pde_n0r_20260805.json`이다.
이는 N1 사전등록만 허용하며 상세 config commit 전 N1 학습을 제출하지
않는다.

N1의 첫 GPU 경로는 confirmatory run이 아니라 validation-only core
development다. `AURORA_DEVELOPMENT_INDEX`는 config의 두 development seed
중 하나만 선택하며 density train/validation과 operator train/validation만
생성한다. Runner에는 test split 생성 호출이 없고 status에
`test_generated_or_accessed=false`, `n1_gate_decided=false`를 기록한다.
Joint-density/operator checkpoint는 server output에만 두며 공개 저장소에
commit하지 않는다. 이 smoke가 성공해도 모든 preregistered baseline과
checkpoint freeze 전에는 confirmatory test job을 제출하지 않는다.

첫 N1 contract attempt는 metric 제출 전에 unflattened coordinate envelope
shape 오류를 검출했다. 동시에 source SHA 변수가 exact commit이 아니어서
이 attempt는 결과와 무관하게 provenance-invalid로 보존한다. Shape fix는
frozen scientific contract를 바꾸지 않으며 새 full SHA contract가
통과하기 전 development metric job을 제출하지 않는다.

Exact `6075530` contract는 113/113을 통과했고 development seed 0 job도
exit 0이었다. Train/validation solver는 모두 수렴했지만 operator
full-BC/paired-response relative L2 0.1739/0.1862로 checkpoint-ineligible다.
Test는 생성하지 않았다. 다음 server job은 unit-peak envelope의 development
seed 1뿐이며 confirmatory seed/job은 계속 금지한다.

Exact `54046a3`의 114/114 contract와 development seed 1은 exit 0이었다.
Unit-peak operator는 full-BC/paired-response L2 0.05771/0.05729로
개선됐지만 0.05를 넘었다. 다음 PBS job은
`cluster/ssu_a6gpu_nonlinear_pde_n1_optimization_attribution.pbs`의
threshold-free N1a뿐이다. 네 variant는 같은 새 development seed와
train/validation split을 쓰며 test contexts를 0으로 강제한다.
Exact commit `cf675af`의 30-task A6000 run은 exit 0으로 완료됐고 공개
aggregate는 `results/controlled_pde_density_attribution_20260803.json`이다.
이 결과로 nonlinear/3D job을 제출하지 않으며 다음 GPU 실행은
development-only grouped-moment estimator 비교다.

DA2는 exact committed source를 read-only bind해 empirical NLL과 세 grouped
moment/shrinkage 후보를 768×8/3,072×8에서 비교한다. 세 seed×여덟 task의
24개 학습을 한 A6000 allocation에 직렬 배치해 scheduler overhead와 idle
GPU를 줄인다. Run은 descriptive development selection을 기록할 수 있지만
selection은 768×8에서만 수행하고 3,072×8은 data-sufficiency control이다.
`new_gate_defined_or_passed=false`와
`nonlinear_or_3d_training_authorized=false`를 항상 보존한다.

Exact `18dbfcd` DA2는 24 task를 exit 0으로 완료했다. 첫 container
contract-test attempt는 기존 BenchAnXplore test의 외부 `h5py` layer가
bind되지 않아 환경 실패했고, 같은 commit의 attempt 2는 pinned
`h5py==3.12.1` layer와 72 tests를 모두 통과했다. Scientific result는
첫 test attempt와 무관하게 full run exit 0 및 두 번째 test pass가 함께
확인된 뒤에만 채택했다.

G1s는 DA2의 data-sufficiency 신호를 별도 fresh exact test로 검증한다.
등록된 public commit과 `configs/controlled_pde_g1s.json`을 read-only로
bind하며, G1r 대비 fresh seed와 training geometry 768→3,072만 바꾼다.
Validation/test 192/192, empirical NLL, model, optimizer, metric과 threshold는
유지한다. 다섯 seed 전체 gate가 끝나기 전에는 nonlinear/3D job을 제출하지
않고, pass하더라도 data quantity를 method contribution으로 기록하지 않는다.

Exact `b0e555a`의 G1s는 dependency-complete 82-test contract와 A6000
fresh 5-seed run을 모두 exit 0으로 완료했다. 일곱 frozen check가 모두
통과해 다음 nonlinear/3D protocol 등록이 허용됐다. Raw run은 계속
비공개 provenance로 보존하고 공개 aggregate만
`results/controlled_pde_g1s_20260803.json`에 둔다. 과거 G1/G1r은
relabel하지 않는다.

Nonlinear 단계는 learned model부터 제출하지 않는다.
`cluster/ssu_a6gpu_nonlinear_pde_n0.pbs`가 exact committed source와
`configs/nonlinear_pde_n0.json`을 read-only bind해 한 A6000 allocation에서
세 numerical-audit seed를 실행한다. 33×33 solver, nested 65×65 reference,
linear counterfactual, 8-component paired perturbation을 같은 job에 묶는다.
Output에는 command, commit, config hash, environment, aggregate metric과
실패 여부를 남긴다. N0가 통과해도 N1 등록만 허용하며 3D headline job은
제출하지 않는다.

N0는 failed로 보존됐고 fresh context-stratified N0r만 9/9를 통과했다.
그 뒤 validation-only N1b checkpoint 50개를 동결하고 exact source
`62605a0`의 N1c outer test를 실행했다. Dependency-complete contract는
125/125, PBS A6000 metric job은 exit 0이었지만 field distribution,
paired response와 acquisition regret가 실패해 N1은 closed다. Route
candidate VoI의 common-random-number 위반 보조 지표는 제외하되 gate
판정은 바꾸지 않는다. Same checkpoint/test를 쓰는 threshold-free N1c-a도
exact source `b97899c`에서 완료됐다. Contract job `109738`은 130/130,
metric job `109739`는 5 seed 모두 exit 0이었다. Joint density가 모든
mask에서 independent heads보다 conditional NLL이 나빴고, high-budget
acquisition과 corrected route regret도 robust superiority를 회복하지
못했다. Raw/per-context artifact는 private provenance에 보존하고 공개
aggregate만 `results/nonlinear_pde_n1c_attribution_20260806.json`에 둔다.
N1d shift와 irregular 3D job은 제출하지 않는다.

Post-N1c development는 두 read-only-source PBS job으로 분리한다.

- `cluster/ssu_a6gpu_nonlinear_pde_n1_density_objective_audit.pbs`는
  0–4 array의 각 A6000 allocation에서 fresh model seed 하나와 네 objective를
  함께 실행한다. Seed별 checkpoint·history·per-context metric은 private
  output에만 두고, 다섯 job이 모두 완료된 뒤 aggregate만 공개한다.
- `cluster/ssu_a6gpu_nonlinear_pde_n1_decision_task_audit.pbs`는 checkpoint
  mount 자체가 없으며 true law/simulator-only audit 한 개만 실행한다.
  solver batch size 2,048을 config에 고정했고 calibration/audit split 외 N1 test
  seed를 생성하거나 읽지 않는다.

두 job 모두 exact public commit과 config hash의 container contract가 먼저
통과해야 제출한다. 하나의 결과를 먼저 보고 다른 config·seed·mask·sample
budget을 바꾸지 않으며, 어느 결과도 N1c relabel이나 3D 실행 권한으로 쓰지
않는다.

Exact source `337c75e`의 dependency-complete contract job `110165`는
144/144 test를 통과했다. Density array `110170[0-4]`와 task job `110171`은
모두 PBS exit 0이었고 test access false였다. Task walltime은 58:04,
solver 2,882 batch는 모두 수렴했으며 최대 normalized residual은
\(5.94\times10^{-6}\)이었다. Frozen aggregate만 공개해
`results/nonlinear_pde_n1_density_objective_audit_20260806.json`과
`results/nonlinear_pde_n1_decision_task_audit_20260806.json`에 둔다.
Checkpoint, training history와 per-context metric은 private output에
보존한다. Full-joint density signal과 missing-only task adequacy는
development 방향을 좁히지만 새 method·fresh re-entry·N1d/3D 권한을
열지 않는다.

M0는
`cluster/ssu_a6gpu_nonlinear_pde_n1_missing_operator_pullback_m0.pbs`의
0–2 A6000 array로만 실행한다. Public source와 N1b checkpoint root는
각각 read-only, seed output만 writable로 bind한다. 각 array index는
fresh density seed와 seed-matched pair-loss-zero frozen operator 하나를
사용한다. Runner는 checkpoint SHA-256, config/source commit, train/selection/
audit split, operator audit L2, solver convergence, test-access false와
private per-context metric을 기록한다. 세 seed가 전부 exit 0일 때만 한 번
aggregate하며, 일부 결과를 보고 config나 남은 job을 바꾸지 않는다.
M0 실패 또는 execution-incomplete 뒤 같은 mechanism의 weight/kernel/sampler
repair job은 제출하지 않는다.

Exact source `89bdc85`의 실제 array `115078`은 seed 0/2가 exit 0, seed 1이
`candidate_risk_matrix`의 truncated conditional rejection stall로 exit 1이었다.
세 seed 완결 조건을 충족하지 못해 aggregate를 실행하지 않았고 성공 seed
metric도 gate 용도로 읽지 않았다. 공개 execution record만 남기며 상태는
`execution-incomplete / no scientific verdict`다. One-shot 규약에 따라
sampler repair·rerun·fresh re-entry job은 제출하지 않는다.

## Aneumo selective-cache contract

사전등록한 32 AneuX base family × 2 deformation의 selective range staging은
완료됐다. 전체 release를 복제하지 않고 필요한 512 internal member만 읽어
64 case × 8 mass-flow condition × 4,096 node의 compact HDF5를 만들었다.
Train/validation/test는 20/6/6 base family와 40/12/12 case이며, 모든
coordinate와 pressure/velocity field가 finite이고 condition 간 coordinate
contract가 일치한다. Cache SHA-256은
`9640b0efbc8ff17a8382b1592547bef109620faeced8a004a932b3cde3b97ab9`다.
License의 CC BY-NC-ND 제약 때문에 raw/compact field와 derived rendering은
공개 저장소에 넣지 않는다.

이 무결성 통과는 learned response의 필요성을 뜻하지 않는다. 먼저
`configs/aneumo_scaling_audit_v1.json`에 사전등록한 CPU audit이 train
family field만 읽고, same-case anchor를 가진 analytic 및 train-tuned
power-law scaling이 설명하지 못한 paired response를 측정한다.
Validation/test field access는 금지하고, 결과는 base-family bootstrap
aggregate만 저장한다. 두 채널 모두 고정된 0.15 lower-bound 기준을
실패하면 Aneumo G2 학습은 중단한다.

Exact commit `e12ff0a`의 pinned CPU run은 52개 전체 test 뒤 exit 0으로
완료됐다. Train 20 family/40 case만 분석하고 validation/test 24 case의
field는 읽지 않았다. Velocity tuned-power residual은 0.2112
`[0.2001, 0.2243]`로 eligible, pressure는 0.1369
`[0.1190, 0.1496]`로 ineligible이었다. Public aggregate는
`results/aneumo_scaling_audit_20260803.json`이다. 이 결과는 learned G2
실행 권한이 아니며 exact density attribution이 먼저다.

template에는 서버 절대경로를 넣지 않고 `AURORA_PROJECT_ROOT`,
`AURORA_DATA_ROOT`, `AURORA_OUTPUT_ROOT`, `AURORA_SIF`를 제출 시 주입한다.

## 2026-08-08 · ISBI V0 metadata-only audit

- Exact public source: `0589070063cfaac765e6d6785653880be860e861`
- Config SHA-256: `0c9745e42e84149d5f788a4e4425ab02028267cc9d1e0b4685ec92d7baf43559`
- Raw result SHA-256: `ec6b50269e929b3b3fad109b239f7c220e22a628222c95b077249656b84ffb50`
- Runtime: pinned container, Python 3.11.10, NumPy 2.1.2, external
  `h5py==3.12.1`; CPU metadata-only, no GPU allocation
- Result: exit 0, 8/8 check pass; cache field arrays and validation/test field
  were not read
- Authorization: V1 64-case implementation smoke only. Outer test, headline
  and submission remain false.

## 2026-08-08 · ISBI V1 pre-learning contract

- First exact source `b8ce721`: model contract 8/9. Parameter range 15.283%
  failed the frozen 15% check; no cache field or learned metric was read.
- Corrected exact source `a8b0042f52d008f5085b7f6c16091682cd649917`:
  q-PointNet residual blocks 16→17 only; tolerance and other contracts unchanged
- Targeted model contract: 9/9, including rigid-rotation equivariance and
  parameter matching
- Dependency-complete full contract: 168/168, exit 0, pinned container and
  read-only `h5py==3.12.1` layer
- Scientific status: learning unrun; test field, outer test, headline and
  submission remain false

후속 exact task source `a0479fb`는 12/12 exit 0이었고 aggregate source
`78dca92`의 replay 결과 gate는 5/7 fail이었다. 위 항목은 실행 전 contract
이력으로만 보존한다. Current status는 이 문서의 앞쪽 V1 scheduler audit과
`results/aneumo_isbi_v1_20260808.json`을 따른다.

## 2026-08-03 G1 exploratory result

최종 sensitivity는 public code commit `900fedc`, 5 outer folds × 5 repeats,
3-fold inner selection, patient bootstrap 1,000회로 실행했다.

| 비교 | AUPRC |
|---|---:|
| clinical | 0.777 |
| clinical + morphology | 0.759 |
| clinical + morphology + real-CFD summary | 0.717 |

Incremental `ΔAUPRC=-0.0419`, patient-bootstrap 95% CI
`[-0.1083, 0.0066]`이다. 현재 exploratory evidence는 incremental utility를
지지하지 않는다. 공식 case map, feature provenance와 second model family
확인 전 confirmatory G1은 `unresolved`로 유지한다.

공개 aggregate result:
`results/cmha_g1_exploratory_20260803.json`
