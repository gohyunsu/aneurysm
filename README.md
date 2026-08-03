# AURORA · Aneurysm Research

불완전하게 관측된 boundary condition(BC) 아래에서 서로 모순되지 않는
**PDE solution distribution**을 학습하고, 이를 3D 뇌동맥류 혈류에
검증하는 연구입니다. Full, partial, missing BC를 별도 문제처럼 풀지 않고
하나의 joint BC–solution model의 조건부·주변 분포로 연결합니다.

> **AURORA** — Aneurysm Uncertainty-aware Reconstruction Operator for
> Reliable Assessment

## 현재 모델은 GNN인가?

**GNN을 사용하지만 순수 GNN은 아닙니다.** 혈관 표면의 가까운 점 관계는
edge message-passing GNN으로 encode하고, 멀리 떨어진 inlet–aneurysm–outlet
관계는 physics-token attention으로 연결합니다. 마지막에는 고정 graph
node의 다음 상태만 예측하지 않고, 임의의 volume/wall query에서 한 cardiac
cycle의 field를 복원하는 neural-operator decoder를 사용합니다.

의학·CFD·mesh·GNN 배경이 없는 독자는
[`site/learn.html`](site/learn.html)에서 11개 장을 순서대로 읽을 수 있습니다.

## 왜 방향을 바꿨는가

기존의 autoregressive MeshGraphNet 개선안은 현재 velocity와 inlet context를
필요로 합니다. 따라서 geometry-only AneuX에 그대로 적용할 수 없고, 2026년
선행연구가 이미 inflow-aware GNN, graph transformer, masked pretraining,
multigrid, physics-informed loss를 폭넓게 다룹니다. attention이나 masking을
추가하는 것만으로는 연구 gap도, 임상적 타당성도 충분하지 않습니다.

AURORA는 다음 세 질문을 한 모델과 실험 프로토콜로 연결합니다.

1. 관측된 BC component가 달라도 예측들이 하나의 확률법칙의
   조건부·주변 분포로 일관되는가?
2. 동일 geometry에서 BC만 바꾼 simulator response를 직접 감독하면
   condition shift의 field 변화를 더 정확히 학습하는가?
3. BC-induced structural uncertainty와 finite-data/model uncertainty를
   분리했을 때 각각 실제 BC shift와 geometry OOD를 추적하는가?

One-shot Fourier cycle은 핵심 novelty가 아닙니다. D0 oracle 표현력 gate와
compute-matched learned 비교를 모두 통과할 때만 효율 구성요소로 남깁니다.

## 문서 읽는 순서

1. [`docs/research-direction.md`](docs/research-direction.md) — 연구 질문,
   contribution, novelty, kill criteria
2. [`docs/literature-lineage.md`](docs/literature-lineage.md) — 선행연구 계보와
   직접 경쟁작 비교
3. [`docs/model-spec.md`](docs/model-spec.md) — AURORA 입력·모듈·loss·tensor
   계약
4. [`docs/experiment-protocol.md`](docs/experiment-protocol.md) — 데이터 역할,
   nested evaluation, ablation, 통계
5. [`CHANGELOG.md`](CHANGELOG.md) — 결정과 구현 변경 이력
6. [`site/index.html`](site/index.html) — 연구 판단을 압축한 프로젝트 허브
7. [`site/learn.html`](site/learn.html) — 동맥류·CFD·GNN·operator·실험을
   처음부터 설명하는 상세 field guide
8. [`docs/server-execution.md`](docs/server-execution.md) — 비식별 자산 감사와
   scheduler 실행 provenance

기존 데이터 감사 기록은 [`docs/datasets.md`](docs/datasets.md)와
[`docs/reproduction.md`](docs/reproduction.md)에 보존합니다.

## 실행 가능한 연구 계약

```bash
PYTHONPATH=src python -m aurora.protocol validate configs/aurora_v1.json
python -m unittest discover -s tests -v
```

설정 파일은 task 정의, split 단위, gate, loss, provenance를 함께
검증합니다. 연구 방향이 바뀌면 문서만 수정하지 말고 이 계약과 사이트의
변경 이력도 같은 커밋에서 갱신합니다.

CMHA legacy exploratory diagnostic은 scheduler allocation과 pinned container에서
실행합니다. 공개 template은 `cluster/`, 실행 코드는
`experiments/run_cmha_g1.py`에 있으며, source identifier는 run artifact에
기록하지 않습니다.

2026-08-03 표 기반 exploratory 결과는 real-CFD summary의 incremental
rupture-status utility를 지지하지 않았습니다(`ΔAUPRC=-0.0419`,
patient-bootstrap 95% CI `[-0.1083, 0.0066]`). 이 결과 때문에 downstream
risk alignment는 논문의 primary contribution에서 제외했습니다.

현재 source audit에서 Aneumo는 전체 학습 release가 아니라 geometry 1개 ×
steady BC 2개 sample만 확인됐습니다. 반면 BenchAnXplore 105-case
HDF5/XDMF archive는 무결성을 확인해, 학습 전 단계인 D0 temporal-basis
audit을 `configs/benchanxplore_d0.json`에 결과 확인 전에 등록했습니다.
이 audit은 Fourier 표현 가능성만 판단하며 모델 성능으로 해석하지
않습니다. Main method는 exact controlled PDE → nonlinear PDE → paired-BC
irregular 3D 순서로 검증합니다.

D0 첫 실행은 scheduler walltime으로 종료되어 metric이 없었습니다.
동일 protocol의 attempt 2는 정상 완료됐지만 frozen \(K=8\) gate를
실패했습니다. \(K=12\)도 bulge relative L2 기준을 통과하지 못해 fixed
Fourier decoder는 중단합니다. 두 provenance는
[`results/benchanxplore_d0_attempt1_20260803.json`](results/benchanxplore_d0_attempt1_20260803.json)에
와
[`results/benchanxplore_d0_attempt2_20260803.json`](results/benchanxplore_d0_attempt2_20260803.json)에
남겼습니다.

첫 method sanity experiment는
[`configs/controlled_pde_g1.json`](configs/controlled_pde_g1.json)에 5개
seed, mask, metric, threshold를 결과 전에 고정했습니다. Exact Poisson
family에서 learned joint BC density + shared operator를 direct masked
Gaussian baseline과 비교합니다. PBS 실행 코드는
[`cluster/ssu_a6gpu_controlled_g1.pbs`](cluster/ssu_a6gpu_controlled_g1.pbs)이며,
통과해도 pipeline sanity일 뿐 novelty 성능으로 해석하지 않습니다.
Frozen 5-seed run은 absolute mean, coverage, raw projective gate를 모두
통과하지 못했습니다. Direct baseline보다 일관된 상대 개선은 있었지만
claim은 `unsupported`이며 결과는
[`results/controlled_pde_g1_attempt2_20260803.json`](results/controlled_pde_g1_attempt2_20260803.json)에
있습니다. 다음 G1b는 finite-sample metric floor와 density/operator/MC
error를 분해하는 exploratory diagnostic입니다.

## 해석의 경계

현재 공개 데이터의 ruptured/unruptured label은 **cross-sectional rupture
status**입니다. 향후 2년/5년 파열 확률이 아니므로 논문·코드·사이트에서
이를 `future rupture risk`로 표현하지 않습니다. 외부·전향 검증 전까지
모든 결과는 연구용이며 임상 의사결정 도구가 아닙니다.
