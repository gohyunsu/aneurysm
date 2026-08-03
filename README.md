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

Fixed Fourier cycle은 frozen D0의 localized bulge gate를 실패해 제거했습니다.
D0b에서는 DCT-II 17/25가 탈락하고 train-only POD 17/25만 oracle
representation gate를 통과했습니다. POD는 아직 learned superiority나
선택된 architecture가 아니며, compute-matched 비교와 fresh transient
확인을 통과할 때만 one-shot temporal branch를 다시 검토합니다.

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

현재 Aneumo ZIP64 release는 전체 archive를 내려받지 않고 byte-range로
감사했습니다. 첫 shard에서 geometry당 8개 steady mass-flow condition과
실제 internal NPY의 좌표·압력·속도·CRC contract를 확인했고, 32개 AneuX
base family × 2 deformation의 family-disjoint selective pilot을 결과 확인
전에 등록했습니다. 이후 512 member를 selective range-read해 64 case,
case당 8 condition과 4,096 node의 compact cache를 완성했고, 40/12/12
case family-disjoint split과 finite field를 검증했습니다. Compact cache는
dataset license에 따라 공개 재배포하지 않습니다. BenchAnXplore 105-case
HDF5/XDMF archive는 무결성을 확인해 결과 확인 전에 D0를 등록하고
실행했습니다.
Fixed Fourier는 실패했으며, 후속 D0b도 표현 가능성만 판단할 뿐 모델 성능
또는 novelty로 해석하지 않습니다. Main method는 exact controlled PDE →
nonlinear PDE → paired-BC irregular 3D 순서로 검증합니다.

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
있습니다. G1b는 finite-sample metric floor와 density/operator/MC error를
분해하는 exploratory diagnostic으로 완료됐습니다. K=128 raw projective
distance는 iid floor로 설명됐지만, K=2048 missing-mask mean error가
0.0853이고 density estimation error가 지배적이어서 기존 G1 실패는 그대로
유지합니다. 공개 aggregate는
[`results/controlled_pde_g1b_20260803.json`](results/controlled_pde_g1b_20260803.json)입니다.

후속 [`G1r`](configs/controlled_pde_g1r.json)은 기존 G1을 다시 채점하지
않습니다. G1b가 드러낸 density optimization과 estimator-floor 문제만
수정하고, 서로 겹치지 않는 5개 fresh seed를 결과 전에 고정했습니다.
Density와 operator는 validation geometry로만 checkpoint를 선택하고,
density-only moment·coverage는 analytic하게, end-to-end mean은
Gauss–Hermite quadrature로, projective error는 matched iid floor 대비
95% CI upper bound로 평가했습니다. Exact commit `951ace1`의 prospective
run은 정상 완료됐지만 실패했습니다. Coverage, full-BC operator, analytic
nesting, projective-excess는 통과한 반면, 최악 seed의 density-only mean
0.07533과 end-to-end quadrature mean 0.07518이 고정 기준 0.05를
넘었습니다. 다섯 seed 평균이 기준 아래라는 이유로 gate를 완화하지 않으며,
공개 aggregate는
[`results/controlled_pde_g1r_20260803.json`](results/controlled_pde_g1r_20260803.json)에
있습니다. Density estimation의 representation·optimization·finite-data
오차를 분해하기 전까지 nonlinear/3D confirmatory 학습은 보류합니다.

Post-G1r density attribution은
[`configs/controlled_pde_density_attribution.json`](configs/controlled_pde_density_attribution.json)에
별도로 고정해 완료했습니다. Analytic population NLL은 최악 density-only
error 0.00495를 회복했지만 empirical NLL은 0.04401–0.04855였습니다.
동일 6,144 boundary sample의 192×32, 768×8, 3,072×2와 fixed-axis 비교는
geometry coverage와 repeated-condition information이 모두 필요함을
보였습니다. 이는 threshold가 없는 post-result attribution이며 실패한
G1/G1r을 relabel하지 않습니다. 공개 aggregate는
[`results/controlled_pde_density_attribution_20260803.json`](results/controlled_pde_density_attribution_20260803.json)에
있습니다.

후속 DA2는
[`configs/controlled_pde_density_development.json`](configs/controlled_pde_density_development.json)에
development-only로 등록했습니다. 세 새 seed에서 empirical NLL과 grouped
unbiased/shrinkage estimator를 같은 network·optimizer로 비교하며,
원래 G1r과 같은 768×8에서 후보를 선택합니다. 3,072×8은 데이터 증가
효과만 보는 control입니다. 결과에는 pass threshold가 없고,
선택된 estimator도 별도 fresh exact gate 전에는 nonlinear/3D 학습을
허용하지 않습니다.

DA2도 완료됐습니다. 고정 규칙상 shrinkage 0.50이 선택됐지만 원래
768×8 empirical NLL 대비 평균 개선은 0.23%에 불과하고 한 seed에서는
악화돼 material한 estimator 이득으로 보지 않습니다. 반면 3,072×8의
기존 empirical NLL은 평균 0.02575, 최악 0.02706으로 안정화됐습니다.
공개 aggregate는
[`results/controlled_pde_density_development_20260803.json`](results/controlled_pde_density_development_20260803.json)이며,
다음 fresh gate는 새 방법이 아니라 데이터 충분성을 검증합니다.

D0b에서 DCT-II rank 17/25는 탈락했고 train-only POD rank 17/25가 모든
frozen representation 기준을 통과했습니다. POD-17의 full L2는 0.00141,
bulge L2는 0.00880입니다. 다만 같은 105 case가 architecture discovery에
쓰였으므로 BenchAnXplore learned 비교는 exploratory이며, confirmatory
효율 주장은 fresh transient test가 필요합니다. 공개 aggregate는
[`results/benchanxplore_d0b_20260803.json`](results/benchanxplore_d0b_20260803.json)입니다.

Aneumo pilot의 고정 split과 허용 범위는
[`configs/aneumo_g2_pilot_v1.json`](configs/aneumo_g2_pilot_v1.json)에,
선택적 ZIP64 range ingestion은
[`scripts/stage_aneumo_range.py`](scripts/stage_aneumo_range.py)에 있습니다.
이 steady scalar-BC pilot은 same-geometry response C2와 irregular-3D
일반화만 검사하며, multicomponent partial-BC C1이나 transient 효율을
뒷받침하지 않습니다.

학습에 앞서
[`configs/aneumo_scaling_audit_v1.json`](configs/aneumo_scaling_audit_v1.json)
은 train base family만 읽는 비자명성 gate를 고정합니다. 같은 case의 한
anchor field까지 제공한 강한 oracle에 대해 velocity-linear,
gauge-invariant pressure-quadratic scaling과 train-tuned global power
law를 검사합니다. Tuned scaling이 response norm의 15%도 남기지 않으면
해당 채널은 G2 novelty 근거에서 제외하며, 두 채널 모두 실패하면 Aneumo
학습을 중단합니다. 이는 단순 물리 스케일링을 새 방법의 성과로 오인하지
않기 위한 사전 감사입니다.

Exact commit `e12ff0a`의 train-only 감사 결과, velocity는 tuned
\(Q^{1.075}\) scaling 뒤에도 response residual median 0.2112,
base-family bootstrap 95% CI `[0.2001, 0.2243]`로 기준을 통과했습니다.
Pressure는 tuned \(Q^{1.75}\)에서 0.1369 `[0.1190, 0.1496]`로
실패했습니다. 따라서 미래 Aneumo G2는 velocity-only 후보이며
pressure/full-field novelty는 제외합니다. 이 결과는 learned 성능이 아니고
G1/G1r 실패도 해소하지 않으므로 3D 학습은 여전히 보류합니다. 공개
aggregate는
[`results/aneumo_scaling_audit_20260803.json`](results/aneumo_scaling_audit_20260803.json)에
있습니다.

## 해석의 경계

현재 공개 데이터의 ruptured/unruptured label은 **cross-sectional rupture
status**입니다. 향후 2년/5년 파열 확률이 아니므로 논문·코드·사이트에서
이를 `future rupture risk`로 표현하지 않습니다. 외부·전향 검증 전까지
모든 결과는 연구용이며 임상 의사결정 도구가 아닙니다.
