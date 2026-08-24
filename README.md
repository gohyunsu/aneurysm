# AURORA · Aneurysm Research

[![Research contract and site quality](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml/badge.svg)](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml)
AURORA는 합성 뇌동맥류 표면에서 한 cardiac cycle의 vector wall shear
stress(WSS)를 예측하는 ISBI 2027 연구입니다. 목표는 새 GNN이라는 이름이 아니라,
강한 동일조건 complete-cycle controls보다 physical field error를 악화시키지 않으면서
TAWSS와 OSI fidelity를 함께 높이는 것입니다.

공개 저장소에는 코드, 데이터·실행 계약과 재현 문서를 둡니다. 원고, 비공개 split
식별자, 미공개 결과와 raw PBS evidence는 별도 private 저장소에서 관리합니다.
공개 사이트는 유지보수하지 않습니다.

## 현재 상태

| 항목 | 상태 |
|---|---|
| 제출 목표 | IEEE ISBI 2027 · four technical pages |
| 주 데이터 | AneuG-Flow release/processed-v5 교집합 730 cases |
| split | 584 / 73 / 73 train/validation/locked test |
| 독립 단위 | geometry ID · GHD duplicate-disjoint; 730개를 환자 730명으로 해석하지 않음 |
| steady 정보 | leakage audit 후 13,985 rows를 selected control과 candidate에 동일 제공 |
| 직접 비교군 | released Graph U-Net, GHD–GPS/GINE, Transolver |
| 현재 실행 | response oracle `118376.ECE-util1`이 introai9에서 단일 queued job |
| 과학 결과 | Graph U-Net validation evidence만 완료; 모든 논문 성능 cell은 pending |
| 봉인 범위 | locked test 73 cases와 processed-only extras 79 cases 미개방 |
| 금지 서버 | junjinyong 사용 금지; introai9만 사용 |

Graph U-Net best validation physical field rL2 `0.631375`는 약한 단일-seed 개발
비교값이며 논문 결과가 아닙니다. Response oracle은 train-output response space의
reconstruction ceiling이고 학습 성능이 아닙니다. GHD–GPS와 Transolver는 exact
source/PBS 계약까지 준비됐지만 아직 실행되지 않았습니다.
## 연구 질문

Aggregate Cartesian field error가 비슷한 complete-cycle WSS surrogate도 시간 평균
magnitude와 방향 상쇄를 다르게 복원할 수 있습니다. 이 차이는 같은 예측 field에서
계산되는 TAWSS와 OSI 오차로 이어집니다. 현재 질문은 다음과 같습니다.

> Train-output cycle response, mesh-local correction, 같은-field functional
> alignment를 결합한 모델이 strong complete-cycle controls보다 field accuracy를
> 유지하면서 TAWSS와 OSI를 함께 개선하는가?

Low-rank response, global/local fusion, residual learning, steady augmentation과
derived-functional 평가는 각각 선행연구가 존재합니다. 논문 contribution은 이
failure-mechanism 연결과 동일 정보량·동일 evaluator의 aneurysm application evidence가
함께 성립할 때만 활성화됩니다.

## 데이터 프로토콜

- Release tree의 730 `stable_*` cases와 processed-v5의 정확한 ID 교집합만 main
  cohort로 사용합니다. Processed-v5의 추가 79 entries는 primary study에서 제외합니다.
- 모든 80 phases는 case와 같은 partition에 둡니다. Split, normalization,
  response basis와 loss scaling은 test WSS나 model outcome을 보지 않고 정합니다.
- Exact/fixed-tolerance GHD duplicate component는 모두 singleton입니다. 따라서
  split은 geometry-ID random, GHD-duplicate-disjoint일 뿐 patient-, site-, verified
  generator-family- 또는 boundary-condition-independent split이 아닙니다.
- 모든 transient cases가 공통 inlet waveform을 사용하므로 BC generalization을
  주장하지 않습니다.
- Primary target은 release의 raw physical Cartesian vector WSS입니다. Stored-normal과
  phase-boundary audit 때문에 hard tangent projection과 hard phase closure를 쓰지 않습니다.

자세한 근거는 [독립 데이터 프로토콜](docs/aneug-release-730-independent-protocol-2026-08-18.md)과
[split 결과](docs/aneug-release-730-split-r3-outcome-2026-08-18.md)에 있습니다.

## Steady 정보의 역할

출처 논문은 14,000 steady cases를 보고하지만 확보된 processed object에는 14,392
rows가 있습니다. Field-blind GHD audit에서 transient train/validation/test/extras와
겹치는 407 rows를 제외하여 13,985 eligible rows를 정했습니다.

Steady supervision은 novelty가 아니라 matched information factor입니다. Selected
control과 candidate는 각각 transient-only(T)와 동일 steady cohort를 더한 T+S로
평가합니다. 두 T+S cell은 같은 ordered manifest, exposure schedule과 single-field
auxiliary head를 사용하며 steady field 하나를 80 phases로 복제하지 않습니다.
Proposal-only steady access는 허용하지 않습니다.

구현 계약은 [steady information control](docs/aneug-release-730-steady-information-control-2026-08-18.md)과
[matched analysis](docs/aneug-release-730-matched-information-analysis-2026-08-21.md)에 있습니다.

BenchAnXplore, 2015 CFD Challenge, AneuX, Aneumo와 과거 processed-v4 실험은 dated
history로 보존하지만 현재 release-730 main table, model initialization 또는 external
validation에 사용하지 않습니다.

## novelty 경계

Graph Transformer, complete-sequence decoding, modal prediction, steady augmentation,
steady-WSS anchor와 post-hoc TAWSS/OSI 평가는 direct prior입니다. Generic output
basis, global/local operator, residual learning과 endpoint alignment도 단독 novelty로
주장하지 않습니다.

남을 수 있는 contribution은 하나의 complete-cycle WSS field에서 field accuracy와
TAWSS/OSI fidelity를 함께 개선하고, 그 효과가 strong controls와 동일 transient 및
steady information 조건에서 유지된다는 application-specific mechanism evidence입니다.
이 conjunctive evidence가 실패하면 해당 claim을 삭제합니다.

최신 aneurysm GNN과 POD 계열까지 포함한 세부 경계는
[functional-fidelity direct-prior update](docs/aneug-release-730-functional-prior-update-2026-08-24.md)에
정리했습니다. 특히 field 중심 학습의 OSI 실패와 shear-metric supervision 제안도
이미 선행연구에 있으므로, functional loss 하나를 contribution으로 주장하지 않습니다.

## Evidence ladder

1. Released Graph U-Net — validation development 완료
2. Train-only response oracle — 단일 queued job, 결과 없음
3. GHD–GPS/GINE — oracle terminal 후 실행
4. Transolver — GHD–GPS terminal 후 실행
5. Validation-only bounded candidate와 ablation
6. Selected control/candidate의 fresh five-seed T/T+S confirmation
7. Frozen checkpoints의 locked test 1회 batched evaluation

선택은 임의의 절대 pass threshold가 아니라 case-paired differences, 10,000-resample
bootstrap uncertainty, field/TAWSS/OSI Pareto relation과 measured compute를 사용합니다.
실패한 trial은 보존하며 다른 metric으로 실패를 상쇄하지 않습니다. 실행 우선순위는
[experiment priority](docs/aneug-release-730-experiment-priority-2026-08-18.md), fresh-seed
계약은 [confirmation protocol](docs/aneug-release-730-multiseed-confirmation-2026-08-24.md)에
정리되어 있습니다.

## 조건부 architecture와 평가

Candidate는 아직 선택된 최종 모델이 아닙니다. 현재의 bounded hypothesis는 다음 네
부분으로 구성됩니다.

1. 하나의 GHD-conditioned mesh encoder가 node features를 만듭니다.
2. Area-pooled global branch가 train-only complete-cycle response basis의 amplitude와
   coefficients를 예측합니다.
3. 같은 node features를 쓰는 local decoder가 고주파·국소 WSS residual을 복원합니다.
4. 하나의 raw Cartesian WSS cycle에서 mean magnitude, mean vector와 valid-support
   OSI를 계산해 field objective와 함께 정렬합니다.

Response-only, local-only, combined, functional-aligned rows는 encoder와 정보량을
유지하여 각 역할을 분리합니다. Oracle ceiling이 약하면 global branch를 제거하고,
functional gain이 명확한 field tax를 동반하면 joint-fidelity claim을 폐기합니다.

## 논문·table·figure 원칙

Primary evidence는 area/phase-weighted physical vector-WSS relative L2, TAWSS
normalized absolute error와 valid-support OSI MAE입니다. Mean-vector error, coverage,
parameters, GPU time, peak memory와 inference latency는 진단·효율 지표입니다.
Vertices와 phases를 독립 표본으로 세지 않고 case-level paired bootstrap을 사용합니다.

Figure는 reference-only 규칙으로 low/median/high OSI test surfaces를 고르고 같은
camera와 reference-derived colour scale에서 reference, strongest control과 candidate를
비교합니다. 사전 선택된 vertex의 signed 80-phase trace도 함께 제시합니다. Figure
코드는 준비되어 있지만 locked test를 열지 않았습니다. 자세한 계약은
[confirmatory figure protocol](docs/aneug-release-730-confirmatory-figure-2026-08-24.md)에
있습니다. Rupture risk나 clinical utility는 주장하지 않습니다.

## 저장소와 검증

```text
configs/      machine-readable prospective contracts
src/aurora/   fail-closed source readers, evaluators and validators
cluster/      PBS wrappers; execution authority는 별도 계약에서만 발생
tests/        synthetic/adversarial regression
docs/         current rationale, literature and dated audits
site/         historical generated site assets; no active maintenance
results/      public aggregate outcomes only
```

주요 문서:

- [release-730 experiment priority](docs/aneug-release-730-experiment-priority-2026-08-18.md)
- [Graph U-Net comparator](docs/aneug-release-730-official-graphunet-baseline-2026-08-18.md)
- [response oracle](docs/aneug-release-730-response-oracle-2026-08-18.md)
- [GHD–GPS comparator](docs/aneug-release-730-ghd-gps-baseline-2026-08-18.md)
- [Transolver comparator](docs/aneug-release-730-transolver-baseline-2026-08-18.md)
- [steady exposure schedule](docs/aneug-release-730-steady-exposure-schedule-2026-08-21.md)
- [선행연구 계보](docs/literature-lineage.md)
- [상세 변경 이력](CHANGELOG.md)

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/check_site.py --root .
```

과학 실행은 introai9 PBS에서만 수행하고 login-node GPU와 junjinyong을 사용하지
않습니다. Confirmatory seed, selection rule과 locked test는 사후 repair하지 않으며,
validation development repair는 사전에 정한 bounded contract 안에서만 허용합니다.
과거 실패와 superseded protocol은 git history와 dated docs에 그대로 보존합니다.
