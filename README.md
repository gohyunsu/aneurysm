# Aneurysm AI Research Hub

뇌동맥류 연구를 두 개의 연결된 문제로 관리한다.

1. **Clinical imaging AI**: CTA/MRA에서 동맥류 검출·분할·혈관 위치 분류
2. **Hemodynamics surrogate**: patient/mesh geometry에서 CFD 혈류장과 WSS·OSI를 빠르게 근사

## 현재 상태

- 연구 맥락과 비판적 검토: [`docs/research-map.md`](docs/research-map.md)
- 데이터셋 인벤토리·통합 원칙: [`docs/datasets.md`](docs/datasets.md)
- 재현 실험 기록: [`docs/reproduction.md`](docs/reproduction.md)
- 표준 데이터 계약: [`data/schema/README.md`](data/schema/README.md)
- 사이트: [`site/index.html`](site/index.html)

## 중요한 해석

`BenchAnXplore`는 105개의 환자 유래 **semi-idealized ICA sidewall geometry**와 CFD field를 갖는 surrogate benchmark다. 실제 CTA를 입력받아 바로 혈류를 예측하는 end-to-end 임상 모델이 아니다. 따라서 AneuX의 geometry-only 자료에 surrogate 출력값을 붙일 때는 실제 hemodynamics가 아닌 **model-generated synthetic label**로 분리해야 하며, rupture prediction에 사용하면 label leakage와 domain shift를 별도로 검증해야 한다.

## 로드맵

1. 원자료의 checksum·license·case mapping을 고정한다.
2. dataset adapter를 만들고 `case_manifest.csv`를 생성한다.
3. geometry/mesh 좌표계와 단위를 검증한다.
4. CFD surrogate는 geometry-disjoint split으로 재현한다.
5. rupture stratification은 patient-level split과 real-CFD upper bound를 포함한다.

임상 의사결정을 위한 진단 도구가 아니며, 모든 모델은 외부 검증과 calibration 전에는 연구용으로만 해석한다.
