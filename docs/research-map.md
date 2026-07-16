# 연구 지형과 현재 작업

## 1. 연구가 진행되는 맥락

뇌동맥류의 임상적 난점은 비파열 동맥류를 발견한 뒤 치료의 이득과 시술 위험을 비교해야 한다는 점이다. 크기·모양·위치·환자 임상정보만으로는 개인별 위험을 충분히 설명하기 어렵고, 혈류가 벽에 가하는 힘(WSS, OSI, pressure/velocity field)이 보완 정보를 제공할 가능성이 있다. 그러나 CFD는 geometry segmentation, meshing, 경계조건 설정과 수치해석에 시간·전문성이 필요하다.

현재 프로젝트는 이 병목을 **CFD-trained graph surrogate**로 줄이는 재현 연구다.

`geometry → CFD ground truth → mesh graph → In-PI-MGN → velocity rollout → WSS/OSI/summary features`

그 다음 단계의 연구 가설은 다음과 같다.

`clinical + morphology + real/surrogate hemodynamics → rupture-risk stratification`

이는 “파열을 직접 예측한다”기보다, 관찰된 rupture status와 연관된 위험 표현을 검증하는 연구로 시작해야 한다. 단면적 ruptured/unruptured label은 미래 파열 확률과 동일하지 않다.

## 2. In-PI-MGN의 의미

MeshGraphNet의 encode–15-step message passing–decode 구조를 기반으로, (a) local acceleration과 inlet velocity summary를 모든 노드에 주입하고 (b) data loss에 continuity, convection, viscosity 물리 제약을 더한다. 핵심은 물리 loss 단독보다 inlet context가 장기 rollout 안정성에 큰 기여를 했다는 ablation이다.

보고된 비교는 MGN 50-step RMSE 50.51, PI-MGN 55.62, In-MGN 9.22, In-PI-MGN 7.58이며, 1-step은 각각 1.11, 1.06, 1.09, 0.85다. 수치는 논문 설정·split·정규화·mask에 종속되므로 독립 재현의 절대 기준으로 사용하면 안 된다.

## 3. 객관적 평가

### 긍정적 의미

- 비정형 CFD mesh를 graph로 직접 다뤄 복잡한 혈관 topology에 맞는다.
- transient 3D field를 autoregressive하게 예측하고 WSS 같은 파생 지표까지 계산할 수 있다.
- inlet context와 discrete physics regularization은 장기 예측과 plausibility를 개선할 합리적 설계다.
- BenchAnXplore 공개는 hemodynamics ML의 재현성과 비교를 돕는다.

### 아직 주장할 수 없는 것

- 105개가 충분한 임상 코호트라는 뜻은 아니다. geometry는 semi-idealized이고 ICA sidewall에 집중된다.
- zero-shot은 내부 데이터의 4개 사례 보고이며, multi-center 임상 일반화나 rupture 예측 검증이 아니다.
- CFD ground truth도 경계조건·혈액 물성·벽 모델·mesh와 solver 선택의 영향을 받는다.
- surrogate가 빠르다는 사실만으로 임상적으로 유용한 risk biomarker가 되는 것은 아니다.
- PI loss가 실제로 보존법칙·경계조건을 만족하는지 residual, mass flux, wall boundary를 별도로 보고해야 한다.

## 4. 현재 작업

1. 원문과 정리글의 주장/근거를 분리한다.
2. AneuriskWeb, AneuX, CMHA(Gong et al.), BenchAnXplore를 case-level manifest로 통합한다.
3. raw asset과 derived asset을 분리하고, geometry-disjoint split을 고정한다.
4. 공개 재현 run의 1-step/50-step discrepancy 원인을 조사한다.
5. 이후 hemodynamics를 rupture stratification에 넣되 real CFD와 surrogate를 비교한다.

## 5. 다른 도메인으로의 확장

같은 방법은 “비정형 mesh/graph + 시간 변화 + 보존법칙”이 있는 문제에 적합하다.

| 도메인 | graph | 예측 예 | 주의점 |
|---|---|---|---|
| 관상동맥·대동맥 | CFD mesh | velocity, pressure, WSS | stenosis와 outlet BC |
| 심장·판막 | deforming mesh | fluid–structure dynamics | moving boundary, FSI |
| 호흡기 | airway graph/mesh | airflow, pressure | compliance와 분기 topology |
| 혈액투석·혈관 graft | porous/CFD graph | flow, shear | device geometry |
| 기상·해양 | unstructured grid | velocity, pressure | multi-scale 장거리 의존성 |
| 구조·재료 | FEM mesh | stress, strain, damage | constitutive law |
| 배터리·다공성 매질 | cell graph | concentration, potential | reaction/transport coupling |

확장 시 “물리 loss를 넣으면 자동으로 좋아진다”가 아니라, 보존량·경계조건·단위·관측 가능한 target을 도메인별로 다시 정의해야 한다.
