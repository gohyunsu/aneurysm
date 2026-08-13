# AURORA · Aneurysm Research

[![Research contract and site quality](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml/badge.svg)](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml)
[![Pages](https://github.com/gohyunsu/aneurysm/actions/workflows/pages/pages-build-deployment/badge.svg)](https://gohyunsu.github.io/aneurysm/site/)

AURORA는 뇌동맥류 CFD surrogate가 transient wall-shear-stress(WSS)의
**방향성 있는 유동 구조**를 보존하는지 검증하는 ISBI 2027 연구 프로젝트입니다.
공개 저장소에는 코드·평가 계약·선행연구 감사·프로젝트 사이트만 두고, 원고와
미공개 결과는 별도 private 저장소에서 관리합니다.

> **현재 판정 · 2026-08-13:** active paper identity는 없습니다. 폐쇄된
> steady response-fidelity P0 v3는 `execution-incomplete · 0/12 evaluated`이며
> 같은 계약을 다시 실행하지 않습니다. 다음 후보인 transient
> structure-faithful WSS는 **30.0/40 inactive**입니다. 현재 열린 것은 이미
> 조사한 case 1의 두 phase만 재사용하는 D0 reader/extractor development뿐입니다.
> D0 v1 job `116160.ECE-util1`은 compute-node network 차단으로 VTP를 얻기 전에
> execution-incomplete로 끝났습니다. 현재는 exact 두 member를 private 임시
> stage에서 network-free PBS로 읽는 최종 transport repair 2/2만 열려 있으며,
> 새로운 scientific stability gate나 모델 학습이 아닙니다.

## 현재 상태

| 항목 | 상태 | 해석 |
|---|---|---|
| 목표 | IEEE ISBI 2027 | four technical pages, single-blind |
| active 연구 주제 | 없음 | transient 후보는 admission 32 미만 |
| 폐쇄된 steady P0 | execution-incomplete · 0/12 evaluated | 과학적 pass/fail이 아님 |
| transient 자산 | 966 complete case · 40 base family | 1,000 case가 1,000 독립 표본은 아님 |
| D0 | v1 transport-incomplete · final repair 2/2 prospective | VTP 미획득; 기존 case 1·phase 2개만 재사용 |
| scientific P0 / 모델 / GPU | 미등록 / 미선택 / 0 | GNN을 포함한 어떤 모델도 current method가 아님 |
| 논문 | pre-evidence shell | title·contribution·result·figure 봉인 |

[프로젝트 사이트](https://gohyunsu.github.io/aneurysm/site/)는 WSS, tangent
vector, critical point와 evidence gate를 배경지식 없이 읽을 수 있게 설명하고,
filterable History에 과거 방향과 실패를 보존합니다.

## 다시 정한 연구 질문

Cartesian MSE가 낮은 transient WSS surrogate라도 source·sink·saddle과 그것이
시간에 따라 이루는 궤적을 훼손할 수 있습니다. 그러나 critical point 자체가
mesh triangulation, normal construction, tolerance와 작은 field perturbation에
불안정하다면 보존해야 할 target이 존재하지 않습니다. 따라서 모델보다 먼저
다음 질문을 검증합니다.

> Aneumo aneurysm surface의 transient WSS에서 signed critical structure가
> 합리적인 discretization과 bounded perturbation 아래 안정적인가? 안정적이라면
> compute-와 vector-field-error가 맞춰진 strong surrogate들이 그 구조를 서로
> 다르게 훼손하는가?

첫 질문이 실패하면 방향을 닫습니다. 둘째 질문에서 실제 failure mechanism이
관측된 뒤에만 최소 representation/objective change를 설계합니다.

## novelty 경계

구성요소를 조합해 이름을 붙이는 것은 contribution이 아닙니다.

- [Hodge Spectral Duality](https://arxiv.org/abs/2605.13834)는 discrete form,
  Hodge decomposition과 topology-preserving mesh operator를 이미 다룹니다.
- [SE(3)-equivariant artery-wall network](https://arxiv.org/abs/2212.05023),
  [RHSIA](https://arxiv.org/abs/2601.19876)와
  [aneurysm GNN](https://doi.org/10.1038/s41746-026-02404-z)은 directional 또는
  transient WSS surrogation을 이미 다룹니다.
- [Critical-point-trajectory compression](https://arxiv.org/abs/2510.25143)과
  [FaCTz](https://arxiv.org/abs/2608.10586)은 critical-point/trajectory 보존을
  직접 점유합니다.
- 359-lesion aneurysm 연구는 phase별 WSS critical point를 추출하고 cardiac
  cycle에서 추적했습니다.

따라서 GNN, equivariance, edge 1-form, Hodge block, temporal decoder,
critical-point tracking과 topology loss는 novelty가 아닙니다. 남을 수 있는
contribution은 모두 결과에 의존합니다.

1. **Target audit:** aneurysm transient WSS에서 구조적 endpoint가 실제로
   안정적인지 공개하는 재현 가능한 평가 계약.
2. **Matched failure evidence:** field error와 compute가 같은 strong baseline도
   robust signed structure/worldline fidelity에서 갈릴 수 있다는 application
   evidence.
3. **Mechanism-linked correction:** 관측된 실패에 필요한 최소 변경이 field
   accuracy를 해치지 않으면서 구조 endpoint를 개선했다는 family-level 증거.

이 세 항목 중 하나라도 없으면 ISBI paper identity를 활성화하지 않습니다.

## 확보한 Aneumo transient 자산

고정된 Hugging Face revision의 case 1–1000 archive directory를 bounded range로
전수 감사했습니다.

- 966 case: `4.01–5.00` complete cardiac cycle
- 34 case: incomplete 또는 alternate sequence
- 961 complete case: official canonical wall filename
- 40/40 base family: complete case가 최소 하나 존재
- 선택한 wall file 4개: point/cell 3-component WSS 확인
- case 1의 두 phase: point/connectivity 동일, WSS는 시간에 따라 변화

관찰된 polygon은 4–9 vertices라 triangulation이 필요합니다. WSS unit,
release-wide tangency와 critical-structure stability는 아직 검증되지 않았습니다.
Hugging Face의 `CC BY-NC-ND 4.0` tag와 GitHub datasheet의 `CC BY 4.0` 문구가
충돌하므로, 저자 확인 전에는 더 엄격한 noncommercial·nonredistribution 경계를
적용합니다. 법률적 결론이나 raw/derived field 재배포는 하지 않습니다.

## Evidence ladder

```text
D0 · known-member reader/extractor development
  ├─ v1: compute-node network unreachable · VTP/read/extractor 0
  └─ v2: exact ephemeral stage · final repair 2/2 · PBS network 0
  └─ pass → 별도 prospective method-free P0 등록만 허용
P0 · family-disjoint target stability
  └─ pass → matched baseline screen 등록만 허용
P1 · compute/field-error-matched structural failure
  └─ pass → bounded validation-only development
fresh re-entry · new seed 또는 disjoint split
  └─ pass → untouched family-level confirmation
ISBI claim activation
```

D0는 scientific result가 아닙니다. 최대 두 번의 bounded repair만 허용하며,
각 repair는 VTK encoding, ZIP range extraction 또는 deterministic numerical
implementation defect 하나로 제한됩니다. Case·phase 변경, array 삭제,
threshold 사후 변경과 model training은 금지합니다. 첫 synthetic-fixture 수정이
repair 1/2를, compute-node egress를 exact private staging으로 바꾸는 transport
수정이 repair 2/2를 소모합니다. V2 결과와 관계없이 추가 D0 수리·재제출은 없습니다.

## 미래 아키텍처의 최소 조건

P0/P1 전에는 아키텍처를 선택하지 않습니다. 나중에 failure가 관측된다면 비교
단위는 동일 backbone·parameter·update·field error입니다.

- mandatory controls: Cartesian output, tangent-projected output,
  SE(3)-equivariant mesh model, Hodge/discrete-form control
- candidate change: oriented edge-integral output과 명시적 tangent reconstruction
- optional objective: stable non-degenerate zero에서만 margin-aware local degree
  control
- primary endpoints: signed critical-point precision/recall, index error,
  trajectory distance, birth/death event F1
- safeguard: vector field error non-inferiority

Hodge나 edge 1-form이 자동으로 zero 또는 worldline을 보존한다고 주장하지
않습니다. 열린 surface의 boundary condition과 Poincaré–Hopf bookkeeping도
별도로 정의해야 합니다.

## 논문·figure 원칙

Evidence가 활성화될 경우에만 원고를 채웁니다. 한 main table은 field safeguard와
구조 endpoint를 함께 보여주고, 한 ablation table은 관측된 failure mechanism만
분리합니다. Figure는 reference/baseline/candidate WSS, signed critical point와
track을 같은 mesh·phase·camera·reference-derived colour range에서 표시합니다.
Rupture risk, patient-specific physiology 또는 clinical utility로 과장하지
않습니다.

## 저장소와 검증

```text
configs/      machine-readable prospective contracts
src/aurora/   fail-closed readers, evaluators and validators
experiments/  bounded development/scientific runners
cluster/      PBS wrappers; execution authority는 별도 계약에서만 발생
tests/        synthetic/adversarial regression
docs/         current rationale, literature and dated audits
site/         explanatory project site and filterable history
results/      public aggregate outcome only
```

주요 문서:

- [현재 재판정](docs/aneumo-transient-structure-reentry-2026-08-13.md)
- [transient release 감사](docs/aneumo-transient-target-contract-and-release-completeness-audit-2026-08-13.md)
- [D0 계약](configs/aneumo_transient_vtp_d0.json)
- [폐쇄된 response P0 결과](docs/aneumo-response-fidelity-p0-v3-execution-2026-08-13.md)
- [선행연구 계보](docs/literature-lineage.md)
- [상세 변경 이력](CHANGELOG.md)

```bash
PYTHONPATH=src python -m aurora.protocol validate configs/aurora_v1.json
PYTHONPATH=src python -m unittest discover -s tests
python scripts/check_site.py --root .
node --check site/assets/research-data.js
```

과학 실행은 `introai9` PBS에서만 수행하고 login-node GPU를 사용하지 않습니다.
`junjinyong`에는 접근·조회·전송·제출·모니터링하지 않습니다. Confirmatory
threshold, seed, outer test와 one-shot 결과는 사후 repair하지 않습니다. 과거
방향, 실패, superseded protocol은 삭제하거나 성공으로 relabel하지 않습니다.
