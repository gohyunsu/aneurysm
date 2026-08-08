# RSNA-ICA supervision-semantics red team · 2026-08-09

상태: **public primary-source audit complete · candidate rejected · payload 0 ·
no method/GPU**

## 판정

이전 conditional shortlist는 RSNA-ICA의 study presence, 13 territory labels,
point localizers와 일부 segmentation을 하나의 latent aneurysm lesion set에
대한 서로 다른 granularity의 annotation projection으로 해석했다. 공개
1차 출처는 이 전제를 지지하지 않는다.

- 제공된 segmentation은 aneurysm extent mask가 아니라 **13-class Circle of
  Willis vessel-anatomy mask**다.
- Aneurysm supervision은 center point와 그로부터 집계된 presence/territory
  label이며, 2위 저자 보고에 따르면 center point는 annotated series
  전체에 제공된다.
- 2위 해법의 voxel aneurysm masks는 official mixed-granularity label이 아니라
  point에서 box를 만든 뒤 pseudo-label·수동 교정으로 저자들이 생성한
  derivative annotation이다.

따라서 official cohort에 dense/sparse **lesion** annotation이 비무작위로
선택된다는 메커니즘은 없다. Annotation-selection-aware
mixed-granularity lesion-set problem은 data semantics를 잘못 결합했으므로
**rejected**다. Access를 얻어도 이 판정을 소급해 바꾸지 않는다.

## 읽은 증거와 읽지 않은 것

| Source | 공개 증거 | 해석 |
|---|---|---|
| [RSNA AWS Registry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/) | 4,000개 이상 CT/MR scan, 18개 institution, 약 200개 AI-generated segmentation, controlled non-commercial access | Segmentation의 정확한 target semantics는 registry 요약만으로 확정하지 않음 |
| [RSNA data wiki](https://github.com/RSNA/AI-Challenge-Data/wiki/RSNA-Intracranial-Aneurysm-Detection-Dataset) | 2026-08-09에는 `Coming soon` | 별도 공식 schema 문서가 아직 없음 |
| [1위 저자 코드, exact `e1dcdf0`](https://github.com/uchiyama33/rsna2025_1st_place/tree/e1dcdf0058e1e0d0044d8053e92243b4b4794555) | `*_cowseg.nii`를 background+13 vessel class로 학습. `train_localizers.csv`의 point로 sphere target을 생성. 13 territory+presence는 classification heads | Vessel anatomy supervision과 aneurysm point supervision은 다른 target이며 lesion-mask granularity pair가 아님 |
| [2위 저자 논문, arXiv:2606.26706v1](https://arxiv.org/abs/2606.26706v1) | 4,348 series, 178개 13-class vessel mask, all annotated series의 aneurysm center point, official voxel aneurysm mask 없음. Point로부터 pseudo-mask를 만들고 수동 교정 | 저자 파생 mask를 official mixed supervision으로 세면 안 됨 |

이 audit는 image, CSV, NIfTI, DICOM, annotation payload를 읽지 않았다. 익명 S3
`ListObjectsV2(max-keys=1)` 요청은 HTTP 403이었고 MIRA 약관을
수락하지 않았다. `introai9` bounded root에서도 asset은 stage되지
않은 상태다.

## 기각된 수학적 가정

이전 식은 annotation type \(K\)가 lesion set \(S\)에서 study, territory,
point, dense mask 중 하나를 선택한다고 가정했다. 실제 public semantics는
다음에 가깝다.

\[
Y_{\mathrm{presence}},Y_{\mathrm{territory}}
\leftarrow A_{\mathrm{point}}, \qquad
V_{\mathrm{CoW}} \leftarrow X,
\]

여기서 \(A_{\mathrm{point}}\)는 aneurysm point annotation이고
\(V_{\mathrm{CoW}}\)는 vessel-anatomy mask다. \(V_{\mathrm{CoW}}\)는 \(S\)의 dense
lesion annotation이 아니므로 \(K\)의 missingness나 coarsening으로 설명할
수 없다. Presence/territory/point 사이의 모순이 있다면 이는 선택
메커니즘이 아니라 structured label-quality 문제다.

## 남은 연구 가능성에 대한 red team

RSNA는 향후 새로운 문제 정의를 통과하면 benchmark로 다시 쓸 수
있다. 그러나 다음은 현재 contribution이 아니다.

- Point로 sphere/box mask를 만드는 것: 1·2위 해법이 이미 사용했고
  point-supervised segmentation이 direct prior art다.
- Vessel-first ROI, anatomy mask pooling, location transformer: 1위 구성요소다.
- Pseudo-label·active learning·manual correction: 2위 해법의 핵심 data pipeline이고
  일반적 label-refinement 기법이다.
- Presence/territory/point consistency 자체: label이 point에서 결정되면 자명한
  data check이지 독립 algorithmic novelty가 아니다.
- Generic structured label correction, conformal/FDR, GNN/set predictor: 이름을
  결합해도 residual gap을 만들지 못한다.

Structured label-error audit는 2위 팀이 수동으로 발견한 left/right·supra/infra
오류 때문에 실용적 질문일 수는 있다. 그러나 현재는 label-noise
모델·기준·정답 감사 subset과 독립 novelty가 없으므로 새 shortlist로
올리지 않는다.

## 다음 허용 작업

1. Active candidate가 0인 상태에서 fresh problem-level audit을 수행한다.
2. 새 후보는 method name 전에 task unit, obtainable reference, direct prior,
   strong baseline, primary metric과 failure action을 먼저 가져야 한다.
3. Controlled-access RSNA를 다시 쓰려면 사용자 약관 수락과 payload L0
   감사 외에도, 이번에 기각한 annotation-selection 정체성과 다른
   새 estimand를 제시해야 한다.
4. 새 후보가 등록되기 전에는 executable method config, GPU job,
   outer test, result table과 submission claim을 만들지 않는다.
