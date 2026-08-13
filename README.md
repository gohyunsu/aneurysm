# AURORA · Aneurysm Research

[![Research contract and site quality](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml/badge.svg)](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml)
[![Pages](https://github.com/gohyunsu/aneurysm/actions/workflows/pages/pages-build-deployment/badge.svg)](https://gohyunsu.github.io/aneurysm/site/)

AURORA는 뇌동맥류 CFD surrogate가 단순한 field error뿐 아니라 **유입 유량
변화에 대한 공간적 반응**까지 보존하는지를 검증하는 ISBI 2027 연구
프로젝트입니다. 이 저장소는 공개 코드, 사전등록 계약, 선행연구 감사와
프로젝트 사이트를 관리합니다. 원고와 미공개 결과는 별도 private 저장소에서
관리합니다.

> **현재 판정 · 2026-08-13:** 유일한 조건부 lead는 Aneumo-specific matched
> response-fidelity audit, 32.5/40입니다. Residual novelty는 2.5/5로 정확히
> 하한선이며, active paper identity가 아닙니다. Real P0 v3는 0/12이고 선택된
> architecture, scientific result, GPU run, outer test와 paper claim은 모두
> 없습니다.

## 한눈에 보기

| 항목 | 현재 상태 | 의미 |
|---|---|---|
| 목표 venue | IEEE ISBI 2027 | 공식 author contract 기준 four technical pages |
| 연구 lead | Aneumo matched response fidelity | application/evaluation contribution만 조건부 유지 |
| 데이터 identity | private inventory에서 등록 SHA-256 일치 | field array는 아직 읽지 않음 |
| Method-free P0 v3 | 0/12 | endpoint 안정성에 대한 과학적 verdict 없음 |
| P1 / architecture | 미등록 / 미선택 | GNN을 포함한 어떤 모델도 current method가 아님 |
| Development | 미개방 | test 봉인, prospective bounded repair만 향후 허용 |
| Confirmation | 0/100 family | 기존 32 family를 제외한 신규 family evidence 필요 |
| 실행 | activation preflight 완료 | PBS·cache·base container 정상, private manifest와 P0 제출은 아직 0 |
| 논문 | internal pre-evidence plan | title·contribution·result·figure 봉인 |

[프로젝트 사이트](https://gohyunsu.github.io/aneurysm/site/)는 배경지식이 없는
독자를 위한 단계별 설명과 필터 가능한 변경 이력을 제공합니다.

## 연구 질문

한 nominal-flow CFD field를 입력으로 받은 surrogate가 다른 유량에서 낮은
Cartesian field error를 보인다고 해서, 같은 geometry의 CFD response까지 맞는
것은 아닙니다. AURORA가 검증하려는 좁은 질문은 다음과 같습니다.

> 동일한 field error 범위에서 aneurysm surrogate들이 유량 변화에 따른 spatial
> response를 다르게 훼손하는가? 그렇다면 동일 backbone의 최소 anchor-identity
> adaptation이 learned-direct와 train-fitted power-law control 모두보다 그 반응을
> 더 충실하게 보존하는가?

평가 단위는 node나 case 수가 아니라 Aneumo base generation family입니다.
Co-primary endpoint는 paired spatial response와 flow-grid tangent이며, field
accuracy는 양측 equivalence safeguard로 사용합니다.

## novelty를 어디까지 주장할 수 있는가

최신 direct-prior 감사는 broad method story를 제거했습니다.

- [PaNO](https://arxiv.org/abs/2606.03038)는 global field accuracy와 downstream
  readout가 어긋날 수 있다는 일반 문제와 readout-aligned operator를 다룹니다.
- [NOEM](https://doi.org/10.1038/s43588-026-00974-2)은 neural-operator output
  transformation으로 constraint를 정확히 만족시키는 일반 구성을 다룹니다.
- [Differentiable cardiovascular BC tuning](https://doi.org/10.1007/s10439-026-04269-5)은
  한 번의 high-fidelity CFD로 보정한 ROM을 이용한 반복 BC tuning을 다룹니다.
- Aneumo, SC-FNO, Hemo-MPO, AB-GATr, DeltaPhi와 aneurysm GNN 계보는 multi-flow
  conditioning, sensitivity supervision, equivariance, physics constraint와
  residual parameterization을 이미 점유합니다.

따라서 GNN, equivariance, physics loss, response loss, residual head,
zero-at-anchor factor 또는 “one CFD, many queries”는 contribution이 아닙니다.
남아 있는 것은 다음 conjunction뿐입니다.

1. **RF-C1 · matched failure evidence:** Aneumo에서 bilateral field-error
   equivalence를 만족한 모델 사이에 material spatial-response failure가 존재함.
2. **RF-C2 · controlled application solution:** 동일 backbone에서 최소
   anchor-identity adaptation이 learned-direct와 train-fitted power law를 모두
   이김. 새 algorithm이나 hard-constraint operator claim이 아님.
3. **RF-C3 · independent-family evidence:** 기존 32 family를 모두 제외한 정확히
   100개 신규 base family에서 평균 효과와 family prevalence를 함께 확인함.

세 cell은 모두 현재 inactive입니다. *Aneumo*, *matched field error*, *analytic
scaling*, *independent family*를 빼도 같은 abstract가 된다면 방향을 폐기합니다.
상세 근거는 [최신 collision recheck](docs/aneumo-response-fidelity-latest-collision-recheck-2026-08-13.md)와
[선행연구 계보](docs/literature-lineage.md)에 있습니다.

## 확보한 데이터가 제공하는 것

검증된 compact Aneumo contract는 다음과 같습니다.

- 32 base generation families
- family당 두 deformation case, 총 64 case
- case당 8 steady mass-flow conditions
- 서로 정렬된 4,096 internal nodes
- historical family split 20/6/6
- velocity-only compact target

등록된 cache digest는 private inventory와 일치하지만 public 저장소에는 서버
경로와 인프라 metadata를 기록하지 않습니다. 이 holding을 WSS, pressure,
rupture risk, patient-specific physiology 또는 longitudinal growth dataset으로
재명명하지 않습니다. 상세 asset 역할과 기각 이유는 [데이터셋 문서](docs/datasets.md)와
[research direction](docs/research-direction.md)을 참고하십시오.

## 증거 사다리

```text
primary-source collision audit
          ↓
P0 v3 · train-only, method-free endpoint stability · 12/12 required
          ↓
fresh P1 · field-error-matched strong-baseline failure
          ↓
bounded validation-only development · test sealed
          ↓
prospective re-entry · fresh seed or disjoint split
          ↓
exactly 100 new-family one-shot confirmation
          ↓
RF-C1–RF-C3 activation and ISBI manuscript population
```

현재는 P0 v3 이전입니다. Synthetic fixtures의 12/12는 evaluator code test일
뿐 Aneumo result가 아닙니다. P0를 통과해도 historical P1이나 confirmation
template가 자동으로 활성화되지 않으며 fresh evidence version이 필요합니다.

관리자 확인 뒤 `introai9` 공개키 접속, 빈 사용자 queue, enabled PBS queue,
정확한 cache checksum과 base-container 가독성을 다시 확인했습니다. Base image에
`h5py`가 없어서 그대로 제출하지 않았고, 해시 고정 `h5py==3.12.1` wheel을
network-free·job-local로 설치하는 activation schema v2를 추가했습니다. Private
manifest 등록과 field-array read, PBS attempt는 여전히 0입니다.

### P0 v3

P0는 모델 성능을 측정하지 않습니다. Train family에서 response magnitude,
rank, interpolation, paired response, tangent와 anchor tangent가 node subset,
flow omission과 허용된 deterministic perturbation에 안정적인지 확인합니다.
12개 gate 중 하나라도 실패하면 이 formulation을 닫습니다.

### P1과 bounded development

P0 12/12 이후에만 새 P1을 등록합니다. P1은 같은 information, backbone,
parameter와 compute 조건에서 direct output과 최소 application adaptation을
비교하고, field error를 양측으로 matching한 뒤 response gap이 실제로 있는지
먼저 확인합니다.

Development가 열리더라도 outer test는 봉인합니다. 각 round는 attribution으로
지지되는 하나의 실패 가설만 검증하고, variant·선택 규칙·compute를 전부
기록합니다. 기존 실패를 relabel하지 않으며 개선 후보는 별도 version과 fresh
seed 또는 disjoint split으로 prospective re-entry를 통과해야 합니다.

### Confirmation

Confirmation은 historical 32를 제외한 정확히 100개 신규 family를 field-blind
하게 고정합니다. Candidate는 learned-direct와 train-fitted power law 각각에
대해 bilateral field equivalence를 만족하면서 paired/tangent error를 최소 10%
낮춰야 합니다. 네 comparator×endpoint contrast 각각에 bootstrap lower > 0,
최소 4/5 positive seeds와 최소 59/100 family wins가 필요합니다. Secondary
metric이나 좋은 qualitative sample은 실패를 구제하지 못합니다.

## 논문과 figure 역할

[ISBI 2027 계획](docs/isbi-2027-plan.md)은 공식 author instruction의 four-page
technical limit, single-blind review와 ethics/funding/COI 요구를 반영합니다.
현재 organizer가 연결한 template archive는 내부적으로 ISBI 2021이라고 적힌
legacy layout이므로 최종 제출 전 당시의 공식 template를 다시 받아야 합니다.

Evidence가 활성화될 경우에만 다음 구조를 사용합니다.

- Introduction: application need → direct-prior subtraction → observed matched
  failure
- Method: estimand과 controls → failure에 필요한 최소 adaptation
- Experiments: family grouping → matching → bounded development → untouched
  confirmation
- Results: one main table, one mechanism ablation, one matched 3D field figure
- Discussion: synthetic steady CFD 범위와 비임상적 한계

3D figure는 reference/direct/power-law/candidate를 동일 좌표, camera와
reference-derived colour range로 표시합니다. Family 선택은 weaker comparator
기준 candidate worst/typical/best로 기계적으로 결정하며, 결과를 본 뒤 예쁜
sample을 고르지 않습니다.

## 저장소 구조

```text
configs/      machine-readable research and evidence contracts
src/aurora/   validators and aggregate evaluators
cluster/      future PBS wrappers; not execution authority
tests/        adversarial and contract regression tests
docs/         current rationale, literature, datasets and historical audits
site/         explanatory project site and filterable history
results/      public aggregate historical evidence only
```

주요 진입점:

- [현재 연구 방향](docs/research-direction.md)
- [실험 프로토콜](docs/experiment-protocol.md)
- [P0 v3 config](configs/aneumo_response_fidelity_p0_v3.json)
- [P0 v3 activation boundary](docs/aneumo-response-fidelity-p0-v3-activation-contract-2026-08-13.md)
- [Confirmation evaluator red team](docs/response-fidelity-confirmation-evaluator-red-team-2026-08-13.md)
- [상세 변경 이력](CHANGELOG.md)

## 검증

```bash
PYTHONPATH=src python -m aurora.protocol validate configs/aurora_v1.json
PYTHONPATH=src python -m unittest discover -s tests
python scripts/check_site.py --root .
node --check site/assets/research-data.js
```

최신 dependency-complete GitHub Actions는 609/609 tests, 115 protocol invariant
groups, site graph와 browser JavaScript를 통과했습니다. 이는 코드·프로토콜
증거이며 scientific performance가 아닙니다.

## 실행 및 보안 경계

- 과학 실행은 향후 `introai9`의 PBS에서만 수행합니다.
- Login-node GPU 사용은 금지합니다.
- 검증된 외부 운영 변화 전에는 현재 P0를 재시도하거나 activation manifest를
  만들지 않습니다.
- `junjinyong`에는 접근·조회·전송·제출·모니터링하지 않습니다.
- Private cache 경로, raw fields, 미공개 결과와 manuscript는 public repository나
  site에 노출하지 않습니다.
- Confirmatory gate, threshold, seed, outer test와 one-shot 결과에는 사후 repair를
  허용하지 않습니다.

과거 방향, 실패, superseded protocol과 정확한 CI provenance는 삭제하지 않고
[CHANGELOG](CHANGELOG.md)와 사이트의 History 창에 보존합니다.
