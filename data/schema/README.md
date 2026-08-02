# Canonical schema v0.2

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

## AURORA distribution contract

단일 surrogate output을 case의 사실값처럼 저장하지 않는다. model-generated
field는 다음 키로 versioning한다.

```text
prediction_id,case_id,model_id,checkpoint_sha,protocol_sha,
bc_mode,bc_prior_version,bc_sample_id,field_kind,temporal_basis,
mesh_mapping_sha,source_field,created_at
```

- `bc_mode ∈ {observed, partial, missing}`
- `source_field=surrogate` 고정
- 각 BC sample은 별도 `bc_sample_id`를 갖는다.
- sample mean만 materialize하더라도 quantile/coverage를 재구성할 수 있게
  sample artifact 또는 deterministic random seed를 보존한다.
- AneuX처럼 real CFD가 없는 case에는 `has_real_hemodynamics=false`를
  유지한다.

`derived/hemodynamics/functionals.parquet`의 최소 열:

```text
prediction_id,case_id,bc_sample_id,region,area_weighting,
tawss_mean,tawss_p95,osi_mean,lsa_fraction,rrt_mean,
hotspot_area,hotspot_centroid_x,hotspot_centroid_y,hotspot_centroid_z
```

Real-CFD와 surrogate summary는 같은 table에 둘 수 있지만
`prediction_id/source_field`로 구분하고, wide column merge로
`mean_wss_real`, `mean_wss_pred`를 임의 생성하지 않는다.

## Split registry

모든 run은 `split_hash`, `protocol_sha`, `manifest_sha`를 기록한다.

- operator: geometry/generator-seed 단위
- clinical: patient 단위
- 동일 geometry의 BC, timestep, cut, augmentation은 한 fold에만 존재
- multiple-aneurysm patient의 모든 lesion은 같은 fold에 존재
