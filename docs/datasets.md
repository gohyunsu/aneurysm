# 데이터셋 인벤토리와 통합 방안

> **2026-08-09 conditional candidate:** Goal-oriented hemodynamic segmentation의
> primary data 후보는 CMHA뿐이다. 공식 record는 99 patients/105 MCA
> aneurysms, 44 controls의 NIfTI CTA, aneurysm–artery STL, aneurysm STL과
> 5개 table을 CC BY 4.0으로 제공한다. 다만 105 lesion의 exact-ID linkage,
> NIfTI/STL unit·frame과 별도 solver/adjoint runtime이 S0a에서 통과하기
> 전에는 training cohort가 아니다. OpenNeuro ds005096은 TOF-MRA external
> stress 후보이고 CMHA와 patient를 합치지 않는다. 2026 multi-center CTA
> Zenodo `15697196`은 172 series/122 aneurysm STL의 parent-vessel supervision을
> payload audit하기 전에는 primary domain으로 쓰지 않는다.

> **2026-08-09 supervision-semantics decision:** RSNA Intracranial Aneurysm
> Detection 2025의 selection-aware mixed-granularity lesion-set 후보는
> 기각됐다. 공개 1위 구현과 2위 report에서 약 178건에 제공된 segmentation은
> aneurysm extent가 아니라 13-class Circle-of-Willis vessel anatomy이며,
> official aneurysm supervision은 center point와 presence/territory label이다.
> 따라서 일부 공식 aneurysm mask가 비무작위로 선택된 cohort라는 전제가
> 성립하지 않는다. Controlled payload는 읽지 않았고 method/GPU/outer test도
> 열지 않았다. RSNA는 다른 task가 fresh audit를 통과할 경우에만 future
> challenge benchmark가 될 수 있다. 상세 근거는
> [`rsna-supervision-semantics-audit-2026-08-09.md`](rsna-supervision-semantics-audit-2026-08-09.md)를
> 따른다.

> **2026-08-09 source-only substitution screen:** CADA, ADAM, IntrA와 TopCoW의
> 공식 metadata·access·annotation 범위를 비교했지만 image/annotation payload는
> 읽지 않았다. CADA/ADAM은 fully supervised challenge이고 IntrA/TopCoW는 각각
> local surface segment/vascular anatomy라 기각된 study-level non-random
> annotation-selection 문제를 대체하거나 구제하지 않는다. 어느 대안도
> active problem, method/GPU 또는 outer test를 열지 않는다.

> **2026-08-08 candidate snapshot, closed 2026-08-09:** 공개 in-vitro 4D-flow MRI release들을
> 새 end-to-end cohort로 합치지 않는다. 2021 release는 한 aneurysm phantom의
> 3 resolution × 3 acceleration development view, Zenodo `14981710`은 네
> aneurysm/flow-diverter phantom의 dual-VENC view, 새 `17183575`는 33 scan의
> intervention/multi-VENC/noise-control asset이다. 그러나 마지막 자료도 실제로는
> 5 base geometry·22 model/device state·2 source patient anatomy다. 현재
> I0a metadata/header audit은 exact source `f7b4e024…`에서 14/14를 통과했다.
> I0b는 2021의 27 processed RAW만 읽도록 등록됐지만 exact `0ebdb344…`의
> one-shot run이 `h5py` import에서 종료돼 archive request, field staging과
> REC read는 모두 0이었다. Gate는 미평가이고 no-rerun rule로 branch를
> 닫았다. 두 2025 release의 독립성은 unresolved이다.
> CFD를 MRI ground truth로 부르거나 phantom을 clinical cohort로 해석하지 않는다.

> **2026-08-03 AURORA 역할 갱신:** 데이터셋은 하나의 end-to-end cohort로
> 합치지 않는다. Aneumo/AneuG-Flow는 BC-aware operator pretraining,
> BenchAnXplore는 transient baseline, CMHA는 real-CFD utility gate,
> AneuX는 external rupture-status stress test로 분리한다. 현재 실험 계약은
> [`experiment-protocol.md`](experiment-protocol.md)를 따른다.

> **2026-08-03 asset audit:** `introai9`에서 Aneumo, AneuG-Flow,
> BenchAnXplore, CMHA, AneuX, Aneurisk의 원본 또는 추출 자산을 확인했다.
> 내부 경로는 공개하지 않는다. 자산 존재만으로 G0를 통과한 것은 아니며,
> manifest·license·unit·case mapping 검증 상태는
> [`server-execution.md`](server-execution.md)에 기록한다.

> **가용 범위 정정:** Aneumo 공식 release의 `1.zip` 중앙 디렉터리를
> byte-range로 감사한 결과, geometry 1--40마다 같은 좌표의 8개 steady
> mass-flow condition이 확인됐다. Geometry 1의 두 internal NPY member는
> CRC와 `(N,7)=xyz+pressure+velocity` contract를 실제 검증했다. 전체
> archive를 받지 않는 32 base-family × 2 deformation × 8 condition
> selective pilot이 `configs/aneumo_g2_pilot_v1.json`에 사전 등록됐고
> staging 전이다. AneuG-Flow는 geometry archive만 확인됐으며 공식
> benchmark는 BC variation을 제공하지 않는다. BenchAnXplore coarse
> archive는 105개 HDF5/XDMF case, case당 80 velocity timestep이 완전하게
> 확인됐다. “공개 규모”, “감사된 구조”, “학습 가능한 local cache”를
> 구분한다.

> **2026-08-08 boundary-asset 정정:** 위 selective compact cache는 internal
> NPY만 staging했지만 official Aneumo ZIP 전체에는 case별 `.msh`, `.stl`,
> `internal.vtu`, `inlet/outlet/wall.vtp`가 있다. Archive 1/case 1 header에서
> PolyData connectivity와 `Points/U/p` array를 확인했다. 이 one-case
> discovery는 전체 자산 감사가 아니다. Exact source `fb1c21a`의 V1b가 20
> archives·64 cases의 384 required member와 60 train representative VTP를
> 검사해 8/8을 통과했다. Validation/test payload와 field array는 읽지 않았다.
> 후속 V1c는 20 train representative×3 patch×3 flow의 geometry-only
> q-invariance·topology·area/frame·coordinate-frame audit에서 8/8을
> 통과했다. 60/60 patch가 exact q-invariant였고 minimum polygon-valid
> fraction은 1.0이었다. Exact source `369317a`의 V1d는 validation geometry
> decode 전에 고정한 train 40, validation 12, test 0 case의 520 geometry
> payload를 감사해 9/9을 통과했다. 156/156 patch가 q-invariant였고 52/52
> case의 exact boundary-volume correspondence를 확인했다. 이 asset pass로
> 등록한 V1e는 exact `c62838b`에서 6/9로 실패했다. Boundary는 matched
> geometry-only control보다 3/3 seed에서 좋았지만 absolute train/validation/
> response learnability 기준은 모두 실패했다. 따라서 boundary asset utility만
> 보존하며 test, missing-condition method와 current Aneumo 3D line은 열지 않는다.

## 핵심 비교

| 자료 | 직접 제공하는 것 | 규모/범위 | 적합한 용도 | 신뢰도 메모 |
|---|---|---:|---|---|
| RSNA-ICA 2025 | Multisite CT/MR angiography, study/location labels, aneurysm center points와 일부 13-class vessel-anatomy segmentation | official description: >4,000 scans, 18 institutions, 13 locations; second-place report: 4,348 series/178 vessel-mask cases | rejected for mixed-granularity lesion-selection task; possible future benchmark only after a new task audit | controlled access; not staged; no official voxel aneurysm mask; no redistribution |
| CADA 2020 | 3DRA와 task별 center/mask supervision | detection 109 volume/127 lesion; segmentation 110 volume/128 lesion | user access 뒤 fully supervised external detection/segmentation stress test | registration required; CC BY-NC-ND 4.0; selection-aware cohort 아님 |
| ADAM 2020 | TOF-MRA+structural MR, center/radius와 consensus binary mask | 113 scans; 93 positive, 20 negative; 일부 baseline/follow-up | user access 뒤 MRA fully supervised baseline | registration/confidentiality agreement; subject-group split 필수; selection-aware cohort 아님 |
| IntrA | Reconstructed vessel surface와 local aneurysm/healthy segments | 103 full vessel models; 1,694 healthy/215 aneurysm segment; 116 manual part annotations | license audit 뒤 surface anatomy pretraining/sanity | raw MRA와 whole-study negative/cardinality 없음; selection rule·payload license 재감사 필요 |
| TopCoW 2024 | CTA/MRA CoW masks, ROI와 vascular graph | permanent 14.4 GB release plus external subsets | anatomy encoder/topology control | aneurysm label이 아니며 listed LargeIA/Lausanne external subsets는 aneurysm-free |
| AneuriskWeb | surface/centerline/morphology, 일부 배포본의 영상·annotation 여부 확인 필요 | 약 100 | geometry·형태 baseline | 배포본/미러별 asset 차이를 checksum으로 확인 |
| AneuX | aneurysm/vessel mesh, morphology·clinical table, rupture label | 750 models | geometry 규모 확장, morphology/rupture 연구 | CTA 원본·CFD가 없는 geometry dataset |
| CMHA / Gong et al. 2024 | NIfTI CTA, aneurysm–artery STL, aneurysm STL, clinical/morphology/hemodynamic summaries | 99 patients/105 MCA IA + 44 controls | conditional S0a primary: image-domain linkage와 standardized-functional task audit | CC BY 4.0; 15.56 GB; 6 multi-lesion patient; exact-ID mapping/solver gate pending; public CFD is summary only |
| OpenNeuro ds005096 | TOF-MRA, selected-session voxel masks/STL/Slicer scene | 63 patients/85 IA; 24 longitudinal patients | external modality/geometry stress only | one annotated session per subject; longitudinal supervised-growth cohort 아님 |
| Open multi-center CTA 2026 / Zenodo 15697196 | raw CTA DICOM, case metadata, 122 aneurysm STL | 172 series: 90 controls/82 IA cases, 3 centers | future detection/morphometry/external audit | parent-vessel/voxel supervision unverified; 25.58 GB CC BY 4.0 payload not staged |
| BenchAnXplore / npj DM 2026 | 105 semi-idealized geometry의 coarse CFD trajectories | 80 frames/case, 0.01 s | GNN surrogate benchmark | ICA sidewall 중심; patient CTA 입력자료가 아님 |
| Aneumo | 10,660 geometry × 8 steady mass flow, pressure/velocity | 85,280 steady CFD | paired BC response | CC BY-NC-ND; base-family split·비재배포 |
| AneuG-Flow / 관련 synthetic set | 현재 서버에는 geometry archive; 논문 release에는 fixed-policy CFD field | 대규모 synthetic | known-condition geometry pretraining | paired-BC C2에는 사용 불가 |
| 4D-flow MRI multiresolution phantom 2021 | 같은 ICA aneurysm phantom의 3 voxel-size × 3 acceleration processed velocity | 1 physical phantom, 9 selected protocols | closed I0b candidate; field 미접근 | CC BY 4.0; execution-incomplete/no verdict/no rerun, 반복 측정·독립 geometry 부족 |
| 4D-flow MRI dual-VENC phantoms 2025 | 네 aneurysm/flow-diverter phantom의 raw four-encoding dual-VENC acquisition | 4 physical phantoms, 8 acquisitions | 보존된 metadata/header candidate | CC BY 4.0; REC 미접근, M4 filename/header 불일치 명시 |
| 4D-flow MRI intervention phantoms 2025 | untreated/device-treated, multi-VENC, pump-off four-encoding raw acquisitions | 33 scans, 22 physical states, 5 base geometry, 2 source anatomies | 보존된 task-unit discovery | CC BY 4.0; scan/device를 patient로 세지 않음, REC 미접근, `14981710` overlap unresolved |

숫자와 확장자는 원 배포본을 받은 뒤 자동 inventory로 확정한다. 정리글의 “Aneurisk CFD 포함”은 현재 프로젝트의 샘플 관찰만으로 확인되지 않았으므로 `unknown`으로 시작한다.

## 권장 canonical 구조

```text
dataset_root/
  raw/<dataset_name>/                 # 원본 보존, 수정 금지
  unified/cases/<case_id>/
    imaging/volume.nii.gz             # 있으면; DICOM은 raw/dicom
    geometry/vessel.vtp
    geometry/aneurysm.vtp
    geometry/centerline.vtp           # optional
    annotation/segmentation.nii.gz    # optional
    metadata/clinical.json
    metadata/morphology.csv
    simulation/cfd/                   # h5/xdmf/cas.gz 원본 paired asset
    derived/hemodynamics/features.csv
  manifests/case_manifest.csv
  splits/geometry_disjoint.json
```

`.vtp`는 point/cell attributes를 보존하기 좋아 canonical mesh로 삼되, STL은 raw에 남긴다. NIfTI 변환은 단순 확장자 변경이 아니라 orientation, affine, voxel spacing을 보존하는 변환이어야 한다. HDF5/XDMF와 Fluent CAS는 역변환·재구성하지 말고 paired raw asset으로 보존한다.

## 병합하지 말아야 할 것

- AneuX의 geometry-only case에 GNN이 생성한 WSS를 `real_cfd`로 저장하지 않는다.
- 서로 다른 환자/기관의 동일 ID를 파일명으로 추정해 합치지 않는다.
- rupture label, future rupture risk, treatment decision을 같은 `label` 필드로 뭉치지 않는다.
- node-level CFD와 case-level summary를 같은 학습 split에 섞지 않는다.
- image–mesh–CFD를 매핑할 수 없는 case는 삭제하지 말고 `unmatched`로 보고한다.

## CMHA 현재 주의사항

- aneurysm 통계표는 105개 병변/99명 환자로 관찰됐다.
- 6명은 다병변이며 병변별 status가 달라 patient-group split이 필수다.
- morphology table의 lesion suffix와 clinical/hemodynamic table의 반복
  patient identifier는 row alignment로는 호환되지만 공식 case map 확인 전
  exploratory로만 사용한다.
- 정의가 확인되지 않은 `PHASE`, `ELAPSS` 열은 target을 거의 분리하므로
  baseline에서 제외한다.

## 단계별 통합

1. 원본 archive의 SHA-256, 출처 URL, license, 다운로드 날짜를 기록한다.
2. 모든 파일을 `dataset/case/source_asset` 3중 키로 inventory한다.
3. case identifier mapping table을 수동 검토한다.
4. mesh의 units, coordinate frame, watertightness, normals, duplicate points를 검사한다.
5. CFD field가 node/cell 중 어디에 저장됐는지와 시간축·단위를 기록한다.
6. 공통 clinical/morphology 컬럼만 canonical table에 넣고 원본 column은 그대로 보존한다.
7. 실제 target별로 split을 다시 만든다: surrogate는 geometry-disjoint, rupture는 patient/site-disjoint.
