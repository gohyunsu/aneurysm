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
| Aneumo | source repository와 preprocessing/baseline 자산 | CFD case/BC 수와 field checksum |
| AneuG-Flow | geometry archive와 추출 geometry | CFD field availability와 release subset |
| BenchAnXplore | 원 archive와 HDF5/XDMF 105-case 추출본 | 전체 manifest, unit, boundary mask |
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
- `cluster/ssu_a6gpu_cmha_g1.pbs`

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
