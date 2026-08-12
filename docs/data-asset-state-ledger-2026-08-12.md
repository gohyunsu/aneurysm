# 데이터 자산 상태 원장

> **Schema 11.5 correction.** “현재 논문에 배정된 active dataset이 0”과
> “과거에 확보·검사한 데이터가 0”은 전혀 다른 명제다. AURORA에는 실제 archive,
> field, table 또는 extracted sample을 확인한 자산 이력이 있다. 다만 현재 선택된
> paper identity가 없으므로 어느 자산도 active train/validation/test 역할을 갖지
> 않는다. 최근 `introai9` 재조사는 directory listing 전에 끝났으므로, 과거 보유
> 이력과 현재 exact-path 존재 여부도 분리한다. Schema 11.5에서는 이 이력 중
> AneuX의 native repeated-representation structure가 한 개의 **conditional source
> lead**를 만들었지만, 이는 active dataset assignment나 실행 가능한 P0를 뜻하지
> 않는다.

## 네 상태를 따로 기록하는 이유

| 층위 | 답하는 질문 | 현재 판정 |
|---|---|---|
| source/release 확인 | 공식 저장소, 파일, 라이선스가 존재하는가? | 다수 확인 |
| payload/holdings 감사 | AURORA가 실제 archive·field·table·sample을 읽고 무결성 또는 구조를 확인했는가? | 아래 6개 주요 holding record에 서로 다른 수준의 증거가 있음 |
| current server inventory | 지금 `introai9`의 exact path에 그대로 존재하는가? | listing 미완료, no-verdict |
| active scientific assignment | 현재 논문의 estimand와 split에 train/validation/test로 배정됐는가? | **0/0/0** |

따라서 `active dataset = 0`은 데이터가 없다는 뜻이 아니다. 현재 논문 문제가 아직
승인되지 않았고, 그 문제에 맞는 독립 단위·target·split·confirmatory 역할을 고정한
자산이 없다는 뜻이다. 공개 Git의 `data/`가 schema 파일만 가진다는 사실도 private
server holding의 역사적 부재를 뜻하지 않는다.

## 주요 확보·감사 이력

| 자산 | 실물 확인 범위 | 과학적 상태 | active가 아닌 정확한 이유 | 재사용 가능한 역할 |
|---|---|---|---|---|
| Aneumo | 32 base family × 2 deformation, 64 case, 8 steady-flow condition, 512-member compact cache; CRC/checksum과 family-disjoint 40/12/12 split 확인. Boundary/volume geometry audit V1b/V1c/V1d는 8/8, 8/8, 9/9 | **성능 gate 실패** | V1e boundary model은 matched geometry-only control보다 두 primary metric에서 3/3 seed 우수했지만 worst train/validation/response relative L2가 0.77221/0.87796/0.94918로 등록 기준 0.25/0.35/0.50을 모두 실패했다. Synthetic steady CFD이므로 임상 outcome이나 transient WSS evidence도 아니다. | 새 문제와 fresh version이 별도 admission을 통과할 때 asset sanity/control. 실패한 V1e를 repair하거나 재채점하지 않음 |
| BenchAnXplore | Exact archive checksum, 105 geometry × 80 transient velocity frame, HDF5/XDMF, coordinates/connectivity/boundary mask 확인; 해석 가능한 field figure 생성 | **representation-eligible, confirmation에는 사용 불가** | D0/D0b에서 105 case 전체가 architecture discovery에 사용됐다. Train-only POD는 통과했지만 같은 case에서 learned superiority를 확인하면 fresh confirmation이 아니다. Semi-idealized ICA-sidewall velocity이며 verified pressure/WSS contract도 없다. | Compute-matched transient control과 engineering benchmark; 독립 pulsatile test가 있을 때만 confirmatory 보조 |
| CMHA | 공식 archive 3개의 byte size/MD5, 다섯 CSV, 99 patient/105 lesion, 44 control, 6 multi-lesion group과 extracted patient material 확인 | **asset-linkage gate 실패; exploratory signal negative** | Patient directory 99개, morphology lesion ID 105개, hemodynamic ID 98개가 exact lesion-level image–parent STL–aneurysm STL triplet으로 연결되지 않아 5/9였다. Exploratory hemodynamic increment도 ΔAUPRC −0.04189, patient-bootstrap CI [−0.10834, 0.00664]로 지지되지 않았다. Single-centre cross-sectional rupture state다. | Patient-grouped descriptive/exploratory control. 공식 case map과 fresh task 없이는 primary/outer test 금지 |
| AneuX v1.0 | 과거 inventory에서 metadata, geometry archive와 extracted copy를 관찰; source는 750 lesion/605 reported patient와 same-lesion multi-resolution/cut orbit을 기술 | **historical P0 no-verdict; fresh conditional direction registered** | 과거 P0가 첫 tabular archive completion 전에 bounded transport를 소진해 CSV, patient/source grouping과 13개 check는 미평가다. 그 job은 no-rerun으로 닫혔다. 별개 schema-11.5 계약은 exact private path/manifest가 아직 null이라 실행 불가다. | Fixed-cut resolution nuisance와 cut-dependent context를 분리한 새 method-free audit. 현재는 source lead/P0 contract일 뿐 train/test assignment가 아님 |
| AneuG-Flow | 과거 geometry archive와 source lineage를 확인; exact release는 9.63 GB steady + 23.74 GB transient selected pair, broader repository 2.63 TB | **execution-incomplete/no scientific verdict** | Surface-vector P0 `115645`는 aggregate, raw log, persistent probe cache 없이 0/10으로 끝났다. 따라서 field/critical-point/worldline 적합성에 verdict가 없다. Synthetic release이고 direct priors도 강하다. | Material source change 뒤 fresh method-free structure audit 후보. 기존 job repair/rerun 금지 |
| Aneurisk | Source-native repository와 sample을 조사해 clinical/mesh preview를 생성. 별도 2026 CFD record는 76 geometry, 1.43 GB archive metadata를 확인 | **기존 sample 확인과 새 CFD archive 미확보를 분리** | 새 CFD P0 `115684`는 complete archive/VTP 없이 0/10으로 끝났다. Patient-measured BC가 아니라 population inflow scaling이며 exact vector/phase/extraction contract도 미확인이다. | Geometry/context visualization과 strong baseline source; 새 archive는 fresh version gate 전 active화 금지 |

## 다른 자산이 active가 아닌 사유

- **Open multicentre CTA**는 172 series/122 aneurysm STL metadata와 ZIP64
  directory, 일부 DICOM header prefix까지 확인했지만 PixelData/STL을 열기 전
  registered parser가 종료됐다. Dataset failure가 아니라 execution-incomplete다.
- **OpenNeuro ds005096**은 실제 공개 종단 MRA지만 한 subject의 모든 시점에 대응하는
  lesion mask와 growth adjudication이 없다. 따라서 supervised future-growth dataset이
  아니다.
- **VMR**은 22 patient/11 pair와 22개 surface-result archive metadata가 있지만
  P0가 0/10이고 archive/VTP가 persist되지 않았다.
- **ADAM, CADA, TopAneu, RSNA**는 실제 데이터 source이나 registration,
  confidentiality agreement, custom terms 또는 controlled access와 환자 단위 재감사가
  필요하다. “가짜 데이터”라서 기각한 것이 아니다.
- **aSAH-Risk XLSX**는 안정된 공개 임상표이지만 영상이 아니고, 70명의 6개월 mRS가
  다른 시점으로 대체돼 현재 fixed-time imaging estimand에 맞지 않는다.

## 기각 사유 taxonomy

앞으로 모든 dataset 표와 change history는 다음 중 하나 이상을 명시한다.

1. `performance_gate_failed`: 자산은 유효하지만 등록 성능 기준을 실패
2. `asset_linkage_gate_failed`: 필요한 image/mesh/field/label join을 식별하지 못함
3. `execution_incomplete_no_verdict`: 실행이 과학적 check 전에 종료됨
4. `task_mismatch`: 공개 target이 현재 estimand와 다름
5. `controlled_or_terms_pending`: 접근권과 사용 조건이 충족되지 않음
6. `discovery_used_not_fresh_confirmation`: 후보 선택에 이미 사용해 outer evidence가 아님
7. `active_assignment_zero`: 선택된 paper identity와 prospective split이 아직 없음

한 자산이 이 중 하나를 만족한다고 “데이터셋 자체가 실패했다”고 쓰지 않는다.

## 현재 숫자의 올바른 읽기

- 역사적으로 문서화된 주요 holding record: **6**
- 공개 repo에 추적되는 raw patient/field payload: **0** — 비공개 또는 비재배포 자산과
  동일한 지표가 아님
- 최근 `introai9` exact-path listing: **미완료/no-verdict**
- conditional source lead / registered scientific P0 contract: **1/1**
- executable P0 / submitted PBS job: **0/0**
- 현재 paper identity에 배정된 active train/validation/test: **0/0/0**
- active P0/P1/model/GPU/outer test: **0/0/0/0/0**

다음 server 확인은 외부 service 상태가 달라진 뒤, 이 원장에 기록된 exact path와
expected checksum만 대상으로 하는 bounded read-only inventory여야 한다. Broad recursive
search나 historical job repair loop는 열지 않는다.
