# 데이터셋 인벤토리와 통합 방안

## 핵심 비교

| 자료 | 직접 제공하는 것 | 규모/범위 | 적합한 용도 | 신뢰도 메모 |
|---|---|---:|---|---|
| AneuriskWeb | surface/centerline/morphology, 일부 배포본의 영상·annotation 여부 확인 필요 | 약 100 | geometry·형태 baseline | 배포본/미러별 asset 차이를 checksum으로 확인 |
| AneuX | aneurysm/vessel mesh, morphology·clinical table, rupture label | 750 models | geometry 규모 확장, morphology/rupture 연구 | CTA 원본·CFD가 없는 geometry dataset |
| CMHA / Gong et al. 2024 | CTA, 3D model, clinical/morphology/hemodynamic data | 99 IA + 44 controls | multimodal clinical/CFD 연결 | 다운로드 14.49 GB, 파일 매핑·license 기록 필요 |
| BenchAnXplore / npj DM 2026 | 105 semi-idealized geometry의 coarse CFD trajectories | 80 frames/case, 0.01 s | GNN surrogate benchmark | ICA sidewall 중심; patient CTA 입력자료가 아님 |
| AneuG-Flow / 관련 synthetic set | geometry와 steady/transient CFD field | 대규모 synthetic | pretraining·surrogate stress test | synthetic→clinical transfer 검증 필수 |

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

## 단계별 통합

1. 원본 archive의 SHA-256, 출처 URL, license, 다운로드 날짜를 기록한다.
2. 모든 파일을 `dataset/case/source_asset` 3중 키로 inventory한다.
3. case identifier mapping table을 수동 검토한다.
4. mesh의 units, coordinate frame, watertightness, normals, duplicate points를 검사한다.
5. CFD field가 node/cell 중 어디에 저장됐는지와 시간축·단위를 기록한다.
6. 공통 clinical/morphology 컬럼만 canonical table에 넣고 원본 column은 그대로 보존한다.
7. 실제 target별로 split을 다시 만든다: surrogate는 geometry-disjoint, rupture는 patient/site-disjoint.
