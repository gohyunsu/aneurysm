# AURORA · Aneurysm Research

뇌동맥류 geometry만으로 하나의 “정답 CFD”를 만드는 대신, 관측되지 않은
boundary condition(BC)이 만들 수 있는 **hemodynamic field의 분포**를
예측하고 그 분포가 downstream rupture-status stratification에 필요한
정보를 보존하는지 검증하는 연구입니다.

> **AURORA** — Aneurysm Uncertainty-aware Risk-aligned Operator for Rapid
> Assessment

## 왜 방향을 바꿨는가

기존의 autoregressive MeshGraphNet 개선안은 현재 velocity와 inlet context를
필요로 합니다. 따라서 geometry-only AneuX에 그대로 적용할 수 없고, 2026년
선행연구가 이미 inflow-aware GNN, graph transformer, masked pretraining,
multigrid, physics-informed loss를 폭넓게 다룹니다. attention이나 masking을
추가하는 것만으로는 연구 gap도, 임상적 타당성도 충분하지 않습니다.

AURORA는 다음 세 질문을 한 모델과 실험 프로토콜로 연결합니다.

1. BC가 없을 때 field를 점 추정하지 않고 calibrated distribution으로
   표현할 수 있는가?
2. autoregressive rollout 없이 한 cardiac cycle의 velocity/WSS를
   one-shot temporal basis로 복원할 수 있는가?
3. 낮은 node RMSE가 아니라 real-CFD 기반 downstream signal을 얼마나
   보존하는가?

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
6. [`site/index.html`](site/index.html) — 위 내용을 압축한 프로젝트 사이트

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

## 해석의 경계

현재 공개 데이터의 ruptured/unruptured label은 **cross-sectional rupture
status**입니다. 향후 2년/5년 파열 확률이 아니므로 논문·코드·사이트에서
이를 `future rupture risk`로 표현하지 않습니다. 외부·전향 검증 전까지
모든 결과는 연구용이며 임상 의사결정 도구가 아닙니다.
