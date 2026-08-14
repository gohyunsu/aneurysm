# AURORA · Aneurysm Research

[![Research contract and site quality](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml/badge.svg)](https://github.com/gohyunsu/aneurysm/actions/workflows/quality.yml)
[![Pages](https://github.com/gohyunsu/aneurysm/actions/workflows/pages/pages-build-deployment/badge.svg)](https://gohyunsu.github.io/aneurysm/site/)

AURORA는 뇌동맥류 CFD surrogate의 transient wall-shear-stress(WSS)가
**방향성 있는 유동 구조를 얼마나 충실하게 보존하는지** 연구하는 ISBI 2027
프로젝트입니다. 공개 저장소에는 코드·평가 계약·선행연구 감사·프로젝트 사이트를,
원고와 미공개 결과는 별도 private 저장소에 둡니다.

> **현재 판정 · 2026-08-14:** active paper identity는 없습니다. AneuG-Flow를
> 조건부 주 데이터 후보로, 2015 Aneurysm CFD Challenge를 같은 해부학에서
> solver마다 생기는 구조 변동의 보조 기준선으로 재배치했습니다. AneuX는 실제
> 형상의 morphology/OOD 감사에만 쓰고, Aneumo는 family mapping과 licence가
> 해결될 때까지 필수 의존성에서 제외합니다. 새 질문은
> **reference-relative transient WSS structure fidelity**이며 **31.0/40 inactive**입니다.
> 아직 AneuG 생성 계보가 확인되지 않아 730 case를 730 독립 환자로 세지 않습니다.
> 새 G0는 `introai9` CPU/PBS에서 정확히 한 번 실행됐으나
> `public_source_request_failed` 뒤 source-feasibility 판정 전에 종료됐습니다.
> 빈 raw log로 어느 요청과 원인이었는지는 알 수 없으며, 동일 계약은 닫혀
> 수리·재제출하지 않습니다. 이 결과는 AneuG field·mesh, Challenge member field,
> model, GPU와 outer test를 열지 않습니다. 다만 기존
> 탐색 범위 밖의 데이터 트리를 다시 감사해 AneuG geometry 14,712개 디렉터리
> 중 14,710개 complete bundle과 BenchAnXplore 105×80 transient velocity 자산이
> 실제로 확보되어 있음을 확인했습니다. 공식 transient v4 target은 exact
> 23,744,862,051-byte object로 확인했고, 60GB cap의 processed-only D1 acquisition을
> 등록했습니다. 데이터 전체 부재가 아니라 **processed WSS의 local acquisition,
> schema와 독립 단위**가 현재 병목입니다.

## 현재 상태

| 항목 | 상태 | 해석 |
|---|---|---|
| 목표 | IEEE ISBI 2027 | four technical pages · single-blind |
| active 연구 주제 | 없음 | 새 후보 31.0/40 · admission 32 미만 |
| 조건부 주 데이터 | AneuG-Flow | 730 transient case 보고 · 독립 lineage 미검증 |
| processed-v4 D1 | closed after attempt 3/3 | partial 0 · connection timeout · schema/data/science verdict 0 |
| processed-v4 D2 | transport in progress | steady server exact · transient client checksum exact, final detached SFTP `reput` 3/3 · schema/science 0 |
| 확보된 engineering 데이터 | BenchAnXplore | 105 HDF5/XDMF × 80 frame · direct WSS 없음 |
| 외부 기준선 | 2015 CFD Challenge | 5 anatomy · solver submission은 anatomy가 아님 |
| geometry OOD | AneuX | WSS/CFD가 없는 실제 형상 보조 감사만 허용 |
| 선택적 외부 비교 | Aneumo | mapping·licence 해결 전 필수 의존성 아님 |
| source G0 | execution-incomplete · exact contract closed | job 116204 · CPU/PBS · GPU 0 · source/science verdict 없음 |
| scientific P0 / 모델 / GPU | 미등록 / 미선택 / 0 | GNN을 포함한 어떤 모델도 current method가 아님 |
| 폐쇄된 steady P0 | execution-incomplete · 0/12 evaluated | 과학적 pass/fail이 아니며 재실행 금지 |
| 논문 | pre-evidence shell | title·contribution·result·figure 봉인 |

[프로젝트 사이트](https://gohyunsu.github.io/aneurysm/site/)는 WSS, critical
point, worldline, solver variability와 evidence gate를 배경지식 없이 읽을 수
있게 설명합니다. 과거 방향과 실패는 filterable History에서 삭제하지 않습니다.

## 연구 질문

Cartesian relative L2가 낮은 transient WSS surrogate라도 source·sink·saddle과
그 cardiac-cycle worldline을 훼손할 수 있습니다. 그러나 CFD reference 자체도
solver, boundary condition, mesh와 numerical scheme에 따라 달라집니다. 그래서
raw structure error만 보고하지 않고 다음 질문을 묻습니다.

> Field error와 compute가 비슷한 learned surrogate가 만드는 signed critical-
> structure/worldline error는, 같은 aneurysm anatomy를 서로 다른 CFD pipeline이
> 계산할 때 생기는 structural variability보다 큰가?

이것을 **reference-relative structural fidelity**라고 부릅니다. 이름 자체는
novelty가 아닙니다. 아래 세 증거가 모두 있어야 논문 정체성이 생깁니다.

1. AneuG transient WSS의 critical structure가 phase, mesh, tolerance와 bounded
   perturbation에서 안정적이다.
2. Field-error/compute-matched strong baseline의 추가 구조 오차가 2015 Challenge의
   within-anatomy inter-solver 구조 변동보다 크다.
3. 관측된 failure와 직접 연결된 최소 변경이 field accuracy를 해치지 않으면서
   untouched lineage-disjoint unit에서 excess structural error를 줄인다.

## 데이터 역할과 기각 경계

### AneuG-Flow · 조건부 주 데이터

공식 릴리스는 14,000 steady case와 730 transient case, surface mesh, velocity,
pressure와 vector WSS를 보고합니다. 공통 node 수/connectivity는 phase tracking을
쉽게 하지만 등록 좌표를 암기하거나 관련 생성 shape가 split을 넘는 위험도 만듭니다.
공식 baseline이 registered WSS relative L2 4.67%를 이미 보고하므로 “GNN으로 WSS를
예측했다”는 contribution이 될 수 없습니다.

- 730 case ≠ 730 patient
- random/prefix/timestep split 금지
- 공식 parent/latent lineage를 우선 사용
- lineage가 없으면 WSS를 읽기 전에 geometry-only near-duplicate cluster를 고정하고,
  이를 환자 계보가 아닌 conservative surrogate grouping으로 명시

초기 bounded inventory는 legacy project root만 보았기 때문에 과거 코드·config·
execution record 외의 payload를 확인하지 못했습니다. 이후 별도 data tree를
재감사해 AneuG geometry archive와 extraction을 확인했습니다. Inventory에는
14,712개 geometry directory가 있으나 `shape.obj`/checkpoint/flow-split 3종이 모두
있는 bundle은 14,710개입니다. 이 tree에는 headline에 필요한 transient WSS target이
확인되지 않았으므로 geometry 확보를 transient data 확보로 바꾸어 말하지 않습니다.
대신 공식 revision의 `assembled_registered_data_1k_v4.pth` 정확한 크기와
LFS SHA-256을 고정했습니다. V4 transient에는 `registered_data_list`와 `mesh_data`가,
steady v4에는 물리 WSS 복원용 `tensor_norm`이 있습니다. D1은 transient v4만
persistent하게 두고 steady v4에서는 `label + tensor_norm`만 추출한 뒤 원본을
삭제합니다. V5, raw blood/wall, 14,000-case steady CFD와 `cfd/`는 받지 않습니다.

### BenchAnXplore · 즉시 실행 가능한 engineering control

검증된 coarse release에는 105 HDF5/XDMF pair와 case당 80개 velocity frame이
있습니다. 과거 geometry-held-out audit에서 train-only POD rank 17/25가 fixed
Fourier보다 국소 bulge dynamics를 훨씬 잘 보존했습니다. 따라서 POD cycle head의
설계 근거와 transient mesh pipeline 검증에는 유용합니다. 그러나 audited XDMF에는
직접 WSS/pressure가 없고 105 case 모두 representation selection에 이미 사용됐으며,
semi-idealized common parent를 공유합니다. 단독 headline/untouched confirmation으로
승격하지 않고 engineering benchmark로 사용합니다.

### 2015 Aneurysm CFD Challenge · solver-variability floor

공식 Figshare v2는 CC BY 4.0이며 동일한 다섯 MCA aneurysm anatomy에 여러 팀의
WSS surface를 제공합니다. 28 submission/26 team을 28 patient로 세지 않습니다.
Anatomy가 최상위 독립 단위이고 solver submission은 anatomy 안에 nested됩니다.
학습 cohort나 population outer test가 아니라 다음 calibration에만 씁니다.

```text
excess structural error
  = surrogate-to-reference discrepancy
    − within-anatomy inter-solver discrepancy
```

실제 estimator는 mesh correspondence·normalization·available WSS representation을
감사한 뒤에만 고정합니다. 다른 surface의 오차를 단순 subtraction/ratio로 합치는
것은 허용하지 않습니다.

### AneuX와 Aneumo · 엄격한 보조 역할

AneuX는 750 aneurysm dome과 668 vessel tree를 제공하지만 WSS/transient CFD가
없습니다. 실제 morphology support와 representation stability만 감사하며 WSS
성능이나 임상 validation으로 부르지 않습니다. Aneumo는 확보한 이력이 있지만
공식 family mapping이 authoritative하지 않고 HF/GitHub licence가 충돌합니다.
철회된 panel은 current panel activation 영구 금지이며, 해결 뒤에도 optional
comparison만 새 version으로 설계합니다.

## novelty 경계

다음은 direct prior, strong control 또는 protocol hygiene이지 contribution이
아닙니다.

- Graph U-Net, MeshGraphNet, SE(3)-equivariant GNN과 graph Transformer
- edge-integrated 1-form, Hodge/DEC decomposition과 tangent projection
- periodic temporal decoder, critical-point tracking와 topology/worldline loss
- family-disjoint split, train-only normalization과 validation-only selection
- CFD pipeline variability가 존재한다는 사실

남을 수 있는 contribution은 **AneuG learned surrogate의 field-matched 구조
failure를 실제-anatomy solver floor에 상대화하고, 그 excess만 겨냥한 최소 correction을
lineage-disjoint하게 확인하는 application evidence**입니다. Critical-point 또는
worldline이 불안정하거나 matched failure가 없으면 방향을 닫습니다.

## Evidence ladder

```text
D1 · exact processed-v4 acquisition + schema/norm/geometry-ID linkage [registered]
  └─ all pass → geometry-only leakage/near-duplicate grouping + split freeze
      └─ stable split → method-free structure-stability P0
          └─ stable target → matched baseline-failure P1
              └─ excess error above solver floor
                  → bounded validation-only minimal correction
                      → fresh lineage-disjoint confirmation
                          → ISBI claim activation
```

G0는 과거 AneuG surface-vector job을 수리하거나 재실행하지 않았습니다. Exact
G0 자체도 한 번의 incomplete outcome으로 닫혀 재실행하지 않습니다. AneuG
field/mesh payload를 다운로드하지 않고 release tree에서 case coverage와 explicit
lineage manifest 존재 여부만 기록합니다. 2015 Challenge WSS archive는 exact
size/MD5와 safe member directory만 확인하며 member extraction이나 field-value read를
하지 않습니다. Pass, fail, execution-incomplete 어느 경우든 동일 계약은 다시
실행하지 않습니다.

D1은 닫힌 G0의 retry가 아닙니다. 사용자가 선택한 processed-only acquisition이며
exact v4 두 object와 60GB selected-asset cap만 다룹니다. Transport가 incomplete인
동안만 동일 partial file을 최대 세 PBS attempt로 resume할 수 있고, object가 모두
완성된 뒤 schema gate는 한 번만 실행합니다. D1 pass도 scientific result나 method
승인이 아니라 leakage grouping과 development split 동결만 엽니다.

마지막 attempt 3 job `116209.ECE-util1`은 F/exit 28, walltime 00:07:32로
종료됐습니다. Persistent error는 `Connection timed out after 30001
milliseconds`이며 partial byte, reader, schema는 모두 0입니다. 즉 60GB 저장
계획이 기각된 것이 아니라 compute-node external transport가 완료되지 않은
것입니다. D1은 3/3에서 닫혔고 동일 contract 재제출은 없습니다.

D2는 compute-node download를 반복하지 않습니다. 접속이 확인된 client에서 steady→transient 순으로 exact object를 하나씩 받고 checksum 한 뒤 Windows
OpenSSH SFTP로 staging합니다. 최대 동시 new byte는 57.12GB로 60GB
경계 아래입니다. 두 server object의 size가 맞을 때만 introai9 CPU/PBS에서
checksum·schema를 단 한 번 검사하며, 현재 full object와 scientific evidence는 0입니다.

## 조건부 architecture와 평가

Active architecture는 아직 없습니다. 다만 자산 감사를 반영해 **post-admission
implementation scaffold**는 SE(3)-equivariant multi-resolution MeshGraphNet,
train-only POD full-cycle head와 deterministic tangent projection으로 고정했습니다.
이는 성능 중심의 구현 기본값이지 algorithmic novelty나 실행 승인이 아닙니다.
P0/P1에서 실제 failure가 확인된 뒤 같은 parameter/update/field-error 조건으로
다음을 비교합니다.

- controls: official Graph U-Net, Cartesian output, tangent-projected output,
  MeshGraphNet/equivariant mesh model, Hodge/discrete-form model
- minimal candidate: oriented edge-integral output과 deterministic tangent
  reconstruction; 추가 loss는 stable non-degenerate structure에만 적용
- field safeguard: vector relative L2와 tangency non-inferiority
- structural endpoints: signed critical-point precision/recall, index error,
  worldline distance와 birth/death event F1
- reference-relative endpoint: within-anatomy solver floor를 초과하는 structural
  error와 그 감소량

Edge 1-form이나 Hodge block이 자동으로 zero/worldline을 보존한다고 주장하지
않습니다. Open surface boundary와 Poincaré–Hopf bookkeeping도 별도 control입니다.

## 논문·table·figure 원칙

Evidence가 활성화될 때만 원고를 채웁니다. Main table은 field safeguard, raw
structure metric, solver-relative excess를 같은 열 체계로 제시합니다. Ablation은
관측된 failure mechanism만 분리합니다. Figure는 동일 camera·mesh·phase·reference-
derived colour range에서 reference CFD, matched baseline, candidate의 WSS,
signed critical point와 track을 보여주고, Challenge anatomy에서는 solver 간
분산을 함께 표시합니다. Rupture risk, patient-specific physiology와 clinical
utility로 과장하지 않습니다.

## 저장소와 검증

```text
configs/      machine-readable prospective contracts
src/aurora/   fail-closed source readers, evaluators and validators
cluster/      PBS wrappers; execution authority는 별도 계약에서만 발생
tests/        synthetic/adversarial regression
docs/         current rationale, literature and dated audits
site/         explanatory site and filterable history
results/      public aggregate outcomes only
```

주요 문서:

- [AneuG reference-relative 재판정](docs/aneug-reference-relative-structure-reappraisal-2026-08-14.md)
- [introai9 확보 자산 재조정](docs/introai9-acquired-asset-reconciliation-2026-08-14.md)
- [machine-readable 확보 자산 ledger](configs/introai9_acquired_asset_reconciliation_v1.json)
- [closed source-feasibility G0](configs/aneug_reference_floor_g0_v1.json)
- [G0 execution record](results/aneug_reference_floor_g0_execution_20260814.json)
- [processed-v4 D1 acquisition contract](configs/aneug_processed_v4_acquisition_d1.json)
- [processed-v4 storage audit](docs/aneug-processed-v4-storage-bounded-acquisition-2026-08-14.md)
- [과거 AneuG P0 no-verdict](docs/aneug-surface-vector-structure-source-audit-2026-08-10.md)
- [Aneumo source authority watch](docs/aneumo-source-authority-watch-v22-2026-08-14.md)
- [machine-readable source-watch v22](configs/source_watch_v22.json)
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
threshold, seed와 outer test는 사후 repair하지 않습니다. 과거 실패와
superseded protocol은 삭제하거나 성공으로 relabel하지 않습니다.
