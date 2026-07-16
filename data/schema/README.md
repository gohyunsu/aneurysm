# Canonical schema v0.1

`case_manifest.csv`는 최소한 다음 컬럼을 갖는다.

```text
case_id,dataset,source_case_id,patient_id,site,modality,
has_volume,has_segmentation,has_vessel_mesh,has_aneurysm_mesh,
has_centerline,has_cfd,has_real_hemodynamics,rupture_label,
label_definition,mesh_units,coordinate_frame,license,sha256,status,notes
```

`has_real_hemodynamics=false`인 경우에도 `derived/hemodynamics`는 존재할 수 있다. 이때 `provenance=surrogate`와 model checkpoint/version을 반드시 기록한다.

`metadata/clinical.json`은 age, sex, hypertension, smoking, location, rupture_status, treatment_status를 optional field로 사용한다. 결측과 비공개는 각각 `null`과 `not_released`로 구분한다.

`derived/hemodynamics/features.csv`는 `case_id,source_field,field_kind,time_aggregation,mean_wss,max_wss,p95_wss,mean_osi,p95_velocity,mass_flux_error` 형식을 권장한다. 요약값은 node/cell weighting과 wall mask를 명시해야 한다.
