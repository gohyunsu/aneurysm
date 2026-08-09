# 2026-08-09 open-CTA physical-coordinate lesion-instance audit

상태: **conditional shortlist 1 · provisional score 32.0/40 · P0 prospectively
registered before DICOM header/STL payload · primary problem/method/architecture/GPU 0**

이 문서는 TopAneu attachment 후보나 닫힌 RSNA lesion-set 후보를 다른 이름으로
복원하지 않는다. 완전 공개된 CTA–STL 자료가 별도의 **physical-coordinate
grid-commutation** 문제를 실제로 식별할 수 있는지, 학습보다 먼저 판정한다.

## 1. 감사하는 문제

후보 질문은 다음 하나다.

> 같은 CTA를 서로 다른 voxel grid로 표현해도, 예측된 병변의 개수, 물리 좌표의
> 표면과 morphometry가 동일한 연속 병변-instance 표현의 rendering으로 설명될 수
> 있는가?

입력은 native CTA와 DICOM acquisition geometry이고 잠재 출력은 물리 좌표
\(x\in\mathbb R^3\) 위의 병변 instance support다. Grid \(\alpha\)에 대한
sampling/rendering을 \(S_\alpha,R_\alpha\), 영상에서 잠재 표현을 얻는 map을
\(F\)라 쓰면 장래의 method가 만족해야 할 구조는 개념적으로

\[
R_\beta F(S_\alpha I,\alpha)
\simeq
F(S_\beta \widetilde I,\beta)
\]

이다. 단, 지금은 \(F\), loss, backbone이나 architecture를 정하지 않았다.
한 native acquisition을 계산적으로 resample한 self-consistency이지, 서로 다른
scanner에서 실제 반복 촬영한 acquisition consistency가 아니다. Expert STL도
manual isolation 뒤 threshold segmentation으로 생성됐으므로 discretization-free
해부학적 진실이라고 부르지 않는다.

허용 endpoint는 cross-sectional detection, lesion-instance segmentation과
physical-space surface/morphometry consistency다. Future rupture risk, clinical
utility, scanner-domain generalization과 TopAneu 52-class localization은 제외한다.

## 2. 왜 이 자료를 감사하는가

[공식 Zenodo record](https://doi.org/10.5281/zenodo.15697196)와
[data paper](https://doi.org/10.3390/data11040074)는 세 기관에서 수집한 172개
CTA series, 90 control, 82 positive case와 expert-validated 122개 STL을 기술한다.
공식 설명은 slice thickness 0.5--2 mm, manual aneurysm isolation 뒤 threshold
segmentation, miliary lesion 30개를 명시한다.

기존 exploratory range discovery에서 전체 25,578,845,008-byte ZIP을 받지 않고
ZIP64 central directory와 16,458-byte metadata member만 읽었다. 확인된 범위는
149,329 DICOM, 122 STL, 172 case, 24 multi-lesion case다. 그때 DICOM header,
PixelData value와 STL payload는 읽지 않았다.

이 조합은 최대 4배인 source-reported slice-thickness 범위와 3 mm 미만 병변을
동시에 포함해 grid sensitivity를 물을 근거는 제공한다. 그러나 실제 DICOM
geometry, 익명 patient/study key, STL–DICOM frame과 STL physical unit을 확인하기
전에는 문제 자체가 성립했다고 볼 수 없다.

## 3. 직접 선행연구 red team

다음 요소는 contribution이 아니다.

| 이미 점유된 요소 | 직접 선행 | 이 후보의 경계 |
|---|---|---|
| voxel-spacing-aware resampling | [Consispace, 2026](https://arxiv.org/abs/2606.31839) | spacing normalization이나 semantic resampler 자체를 novelty로 주장하지 않는다. |
| continuous implicit segmentation | [I-MedSAM](https://arxiv.org/abs/2311.17081), [MICCAI 2025 implicit/noisy-label segmentation](https://papers.miccai.org/miccai-2025/0443-Paper0665.html) | coordinate decoder나 uncertainty sampling 자체는 baseline이다. |
| resolution-invariant latent | [Resolution Invariant Autoencoder](https://arxiv.org/abs/2503.09828) | learned resize와 common latent 자체는 contribution이 아니다. |
| calibrated random finite object set | [Object Detection as Probabilistic Set Prediction, ECCV 2022](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136700545.pdf) | cardinality distribution이나 RFS 이름만 붙이지 않는다. |
| variable-cardinality medical lesion set | [LesionDETR, 2026](https://arxiv.org/abs/2606.04365) | query set과 Hungarian matching은 direct baseline이다. |
| aneurysm shape/topology pretext or loss | [ISBI 2026 shape-guided SSL](https://doi.org/10.1109/ISBI61048.2026.11515789), [MIDL 2026 TAR](https://proceedings.mlr.press/v315/xiao26a.html) | synthetic deformation, shape prior와 topology regularization은 단독 novelty가 아니다. |

따라서 남을 수 있는 간극은 implicit decoder, set prediction 또는 resampling 중
하나가 아니다. **하나의 물리 좌표 병변-instance 표현에서 grid별 mask를 유도하고,
cardinality·surface·morphometry가 함께 commute한다는 구조와 실제 small/multiple
aneurysm 이득**이 모두 있어야 한다. 이 결합도 P0/P1과 strong-baseline evidence
전에는 contribution이 아니다.

## 4. 현재 후보 점수

점수는 0--5이며 현재 확인된 source evidence만 반영한다.

| 축 | 점수 | 판정 |
|---|---:|---|
| biomedical-imaging relevance | 5.0 | 실제 CTA의 tiny aneurysm detection/segmentation과 직접 연결된다. |
| identifiable estimand | 3.5 | deterministic grid commutation은 정의되지만 repeated native acquisition은 없다. |
| direct-prior residual gap | 3.0 | spacing, INR, RFS, DETR, topology 각각은 점유됐고 joint physical-instance commutation만 남는다. |
| data available now | 4.5 | CC BY 4.0 공개 archive와 exact checksum이 있으나 DICOM/STL payload는 아직 미감사다. |
| independent sample size | 3.5 | 172 case/122 lesion은 P0/P1에 적합하지만 5-seed 3D confirmatory에는 작다. |
| strong-baseline feasibility | 4.0 | nnU-Net/nnDetection, Consispace, implicit decoder, LesionDETR류가 명확하다. |
| interpretable figure | 5.0 | native CTA, alternate grids, STL과 physical morphometry를 같은 case에서 연결할 수 있다. |
| compute/runtime feasibility | 3.5 | selective audit은 작지만 whole-volume 3D 5-seed 비교는 제한된 budget이 필요하다. |

합계는 **32.0/40**으로 자동 shortlist 기준과 정확히 같다. 이는 primary problem
선정이 아니라 P0를 한 번 실행할 가치가 있다는 의미다. Direct-prior gap은
3.0에 불과하므로 P0/P1에서 구조적 failure가 작으면 후보를 닫는다.

## 5. Prospective P0 계약

Executable source of truth는
[`configs/open_cta_physical_p0.json`](../configs/open_cta_physical_p0.json)이다.
계약은 DICOM header 또는 STL payload를 보기 전에 고정했다.

- 172 case마다 숫자 순 first/upper-median/last DICOM member, 총 516개만 선택한다.
- DICOM의 compressed prefix를 PixelData tag까지만 range-read한다. PixelData
  값을 decode·inspect하지 않고 raw member를 보존하지 않는다.
- 122 STL은 모두 range-read하고 member CRC, finite vertex, triangle degeneracy,
  metadata volume scale와 DICOM physical frame 정합을 감사한다.
- 익명 PatientID와 StudyUID가 172 case에서 일대일인지 aggregate로만 확인한다.
  통과 전 split unit은 patient가 아니라 `cta_case`다.
- 모든 결과는 aggregate만 공개하며 case ID, UID, 좌표와 raw payload를 남기지
  않는다.

All-check gate는 archive/metadata exactness, case–lesion mapping, 516 header
parse, patient/study key, series geometry, declared image count, metadata/header
thickness, observed thickness ratio ≥2, STL finite/nondegenerate, metadata volume
scale와 STL–DICOM frame alignment를 모두 요구한다.

- **모두 통과:** method-free P1 native-grid rasterization/instance-stability audit만
  별도 등록한다.
- **하나라도 실패:** threshold, tolerance, selection을 고치지 않고 후보를 닫는다.
- 어느 outcome도 method, architecture, GPU, outer test, contribution 또는
  submission identity를 열지 않는다.

## 6. P0 뒤에만 가능한 P1

P1은 learned model이 아니다. P0가 통과한 경우에만, STL을 native grid와 미리
정한 alternate physical grids에 rasterize해 다음을 측정하도록 별도 contract를
결과 전에 고정한다.

1. miliary/other lesion별 component-cardinality retention
2. physical volume·maximum extent bias와 surface distance
3. lesion/case 단위 aggregation 차이와 multi-lesion identity 보존
4. standard discrete preprocessing이 이미 안정적인지 여부

Grid change가 비자명한 target 변화를 만들지 않거나 standard baseline이 문제를
포화하면 후보를 닫는다. P1 결과를 본 뒤 continuous decoder나 topology loss를
선택하지 않는다. Method 설계는 별도 P2에만 가능하다.

## 7. 현재 판정

현재는 **conditional shortlist 1, P0 registered, primary problem 0**이다. 이
후보는 GNN 기반도, implicit decoder 기반도, DETR 기반도 아니다. 등록된 P0의
실제 asset evidence가 다음 판정을 결정한다.
