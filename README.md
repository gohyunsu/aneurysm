# AURORA · Aneurysm Research

[![Research contract and site quality](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml/badge.svg)](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml)
AURORA는 합성 뇌동맥류 표면에서 한 cardiac cycle의 vector wall shear
stress(WSS)를 예측하는 ICCE 2027 연구입니다. 목표는 새 GNN이라는 이름이 아니라,
강한 동일조건 complete-cycle controls보다 physical field error를 악화시키지 않으면서
TAWSS와 OSI fidelity를 함께 높이는 것입니다.

공개 저장소에는 코드, 데이터·실행 계약과 재현 문서를 둡니다. 원고, 비공개 split
식별자, 미공개 결과와 raw PBS evidence는 별도 private 저장소에서 관리합니다.
공개 사이트는 유지보수하지 않습니다.

## 현재 상태

| 항목 | 상태 |
|---|---|
| 제출 목표 | ICCE 2027 · 공식 author contract에 맞춘 최종 원고 |
| 주 데이터 | AneuG-Flow release/processed-v5 교집합 730 cases |
| split | 584 / 73 / 73 train/validation/locked test |
| 독립 단위 | geometry ID · GHD duplicate-disjoint; 730개를 환자 730명으로 해석하지 않음 |
| steady 정보 | leakage audit 후 13,985 rows를 selected control과 candidate에 동일 제공 |
| 직접 비교군 | released Graph U-Net, GHD–GPS/GINE, Transolver |
| 완료된 개발 비교 | Graph U-Net, GHD–GPS, Transolver, response-only, response+residual |
| 선택된 직접 비교군 | GHD–GPS · validation field rL2 `0.286619` |
| 현재 개발 단계 | GHD–GPS 공통 checkpoint에서 same-field functional objective 세 가지 비교 준비 |
| 현재 과학 판단 | response/local residual은 기각; functional alignment와 steady supervision은 미검증 |
| 봉인 범위 | locked test 73 cases와 processed-only extras 79 cases 미개방 |
| 실행 정책 | PBS 자원에 따라 양 서버 사용; 동일 scientific cell의 동시 중복만 금지 |

동일 73-case validation evaluator에서 GHD–GPS는 Transolver의 `0.292427`보다 낮은
field rL2를 보였고 paired difference는 `-0.005808`, 95% case-bootstrap interval은
`[-0.011793, -0.000211]`이었습니다. 이는 single-seed validation 개발 근거이지
locked-test 또는 최종 논문 성능이 아닙니다.

Rank-64 response-only와 response+local-residual은 각각 field rL2 `0.348802`와
`0.348325`였습니다. Residual-minus-response-only field difference의 95% interval
`[-0.006533, 0.005273]`은 0을 포함했고 TAWSS와 OSI도 개선되지 않았습니다. 더
중요하게 residual 후보는 GHD–GPS보다 field `+0.061706`, TAWSS `+0.040814`, OSI
`+0.000582`만큼 나빴으며 세 interval 모두 0보다 컸습니다. 따라서 global/local
candidate를 최종 architecture로 유지하지 않고 보존된 negative ablation으로
내렸습니다.
## 연구 질문

Aggregate Cartesian field error가 비슷한 complete-cycle WSS surrogate도 시간 평균
magnitude와 방향 상쇄를 다르게 복원할 수 있습니다. 이 차이는 같은 예측 field에서
계산되는 TAWSS와 OSI 오차로 이어집니다. 현재 질문은 다음과 같습니다.

> 가장 강한 GHD–GPS complete-cycle control에 same-field functional alignment와
> leakage-audited steady supervision을 더하면 field accuracy를 보존하면서 TAWSS와
> OSI fidelity 및 transient-label efficiency를 함께 개선할 수 있는가?

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

현재 남을 수 있는 contribution은 강한 GHD–GPS backbone에서 하나의 complete-cycle
WSS field의 field accuracy와 TAWSS/OSI fidelity를 함께 개선하고, 14,000 steady / 730
transient 비대칭을 누수 없이 활용해 label efficiency를 높인다는 application-specific
evidence입니다. Functional alignment나 steady supervision 자체는 prior art이므로,
동일 backbone·동일 evaluator에서의 결합 효과가 입증되지 않으면 해당 claim을
삭제합니다.

최신 aneurysm GNN과 POD 계열까지 포함한 세부 경계는
[functional-fidelity direct-prior update](docs/aneug-release-730-functional-prior-update-2026-08-24.md)에
정리했습니다. 특히 field 중심 학습의 OSI 실패와 shear-metric supervision 제안도
이미 선행연구에 있으므로, functional loss 하나를 contribution으로 주장하지 않습니다.

## Evidence ladder

1. Released Graph U-Net, GHD–GPS, Transolver — validation development 완료
2. Train-only response oracle와 rank selection — 완료
3. Response-only 및 response+local-residual — 완료; residual hypothesis 기각
4. GHD–GPS field-only/scalarized/field-anchored objective selection — 현재 단계
5. 선택 objective의 leakage-audited T/T+S 및 label-efficiency 비교
6. 선택된 control/proposal의 fresh multi-seed confirmation
7. 모든 개발 선택을 고정한 뒤 frozen checkpoint의 locked test 1회 평가

선택은 임의의 절대 pass threshold가 아니라 case-paired differences, 10,000-resample
bootstrap uncertainty, field/TAWSS/OSI Pareto relation과 measured compute를 사용합니다.
실패한 trial은 보존하며 다른 metric으로 실패를 상쇄하지 않습니다. 실행 우선순위는
[experiment priority](docs/aneug-release-730-experiment-priority-2026-08-18.md), fresh-seed
계약은 [confirmation protocol](docs/aneug-release-730-multiseed-confirmation-2026-08-24.md)에
정리되어 있습니다.

## 현재 선택된 개발 경로

최종 architecture는 아직 확정하지 않았습니다. 다만 직접 결과에 따라 출발점을
response/local 후보가 아니라 exact terminal GHD–GPS best checkpoint로 바꿨습니다.

1. `field_only`, `all_scalarized`, `all_field_anchored` 세 cell은 동일 checkpoint,
   backbone, seed, split과 optimizer budget에서 시작합니다.
2. Mean-vector, TAWSS와 valid-reference-support OSI는 별도 head가 아니라 하나의 raw
   Cartesian WSS cycle에서 계산합니다.
3. 모든 objective는 초기 checkpoint로 정규화한 동일 validation utility로 checkpoint를
   선택하며, epoch-0 checkpoint도 fallback으로 허용해 강제 열화를 막습니다.
4. Validation에서 objective를 고른 뒤에만 같은 GHD backbone에서 transient-only(T)와
   eligible steady augmentation(T+S)을 대칭 비교합니다.

구현과 해석 경계는
[GHD functional fine-tuning protocol](docs/aneug-release-730-ghd-functional-finetune-2026-08-29.md)에
정리했습니다. Functional gain이 field tax를 동반하거나 steady gain이 누수·추가
compute와 분리되지 않으면 proposal claim을 활성화하지 않습니다.

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
