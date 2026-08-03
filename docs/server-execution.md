# AURORA 서버 실행과 provenance

최종 갱신: 2026-08-03 KST

이 문서는 재현에 필요한 역할과 절차만 공개한다. SSH endpoint, 내부 절대
경로, credential, patient-level row와 prediction은 기록하지 않는다. 실제
운영 명령과 private path는 Git에서 제외된 `SERVER_GUIDE.md`를 따른다.

## 서버 역할

| 서버 계정 | 역할 | 허용 작업 |
|---|---|---|
| `introai9` | source asset registry와 데이터 감사 | 원본·추출본·매니페스트 read-only 확인 |
| `junjinyong` | scheduler 기반 실험 | PBS GPU allocation, pinned container, aggregate output |

원자료를 로컬 저장소에 내려받거나 서버 사이에 전체 복제하지 않는다.
`junjinyong`에서는 필요한 source root를 read-only로 bind하고 run output만
writable로 둔다.

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

`junjinyong`의 PBS `ssu_a6gpu` allocation 안에서 다음을 확인했다.

- GPU: NVIDIA RTX A6000 1장
- PyTorch: 2.5.1+cu118
- CUDA runtime: 11.8
- 2048 × 2048 CUDA matrix multiplication finite check: pass
- smoke exit status: 0

login node에서는 `nvidia-smi`나 학습을 실행하지 않았다.

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
- `cluster/ssu_a6gpu_controlled_density_attribution.pbs`
- `cluster/ssu_a6gpu_controlled_density_development.pbs`

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
relabel하지 않으며 다음 GPU 우선순위는 nonlinear N0다.

Nonlinear 단계는 learned model부터 제출하지 않는다.
`cluster/ssu_a6gpu_nonlinear_pde_n0.pbs`가 exact committed source와
`configs/nonlinear_pde_n0.json`을 read-only bind해 한 A6000 allocation에서
세 numerical-audit seed를 실행한다. 33×33 solver, nested 65×65 reference,
linear counterfactual, 8-component paired perturbation을 같은 job에 묶는다.
Output에는 command, commit, config hash, environment, aggregate metric과
실패 여부를 남긴다. N0가 통과해도 N1 등록만 허용하며 3D headline job은
제출하지 않는다.

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
