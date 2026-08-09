# 2026-08-09 TopAneu vascular-attachment problem audit

상태: **source audit completed · conditional lead 29.0/40 · active shortlist 0 ·
TopAneu terms not accepted · image/label payload 0 · no method/architecture/GPU**

이 문서는 닫힌 BC-operator, 4D-flow, RSNA lesion-set 또는 goal-oriented
segmentation 후보를 다른 데이터로 되살리지 않는다. ISBI 2027을 위한 새
문제를 방법론보다 먼저 감사한 기록이다. 공식 challenge 문서에서 확인한
사실, 공개 ZIP의 byte-range metadata discovery와 아직 검증하지 않은 가설을
구분한다.

## 1. 감사한 질문

검토한 잔여 가설은 다음과 같다.

> 병변 segmentation과 52-class parent-vessel location을 독립 head로 예측하지
> 않고, 환자별 vascular tree에 대한 병변의 연속적·확률적 attachment에서 둘을
> 함께 유도하면 small lesion과 bifurcation case에서 검증 가능한 일관성과
> detection 이득이 생기는가?

잠재 단위는 환자별 vascular graph \(T_X\), 병변 instance support \(M_i\)와
graph 위 attachment \(a_i\)다. Dataset label \(c_i\)는 임의 classifier 출력이
아니라 미리 고정한 ontology projection \(\pi_D(a_i,T_X)\)으로 유도한다.
그러나 이 수식은 **문제 가설**일 뿐 현재 선택된 model, loss 또는 contribution이
아니다. Continuous attachment, graph extraction, ontology projection과 set
prediction 각각은 이미 알려진 구성요소다.

허용 endpoint는 cross-sectional aneurysm detection, voxel segmentation과
parent-vessel localization이다. Future rupture risk, growth, treatment decision,
clinical utility와 autonomous diagnosis는 포함하지 않는다.

## 2. TopAneu 2026에서 공식적으로 확인한 범위

[TopAneu 2026](https://topaneu-26.grand-challenge.org/)은 MICCAI 2026 공식
challenge이며 CTA/MRA에서 병변을 검출·분할하고 각 병변을 vessel location
class에 할당한다. [live data page](https://topaneu-26.grand-challenge.org/data/)
와 [registered challenge design](https://doi.org/10.5281/zenodo.19848807)을
대조했다.

### 2.1 live release와 registered design을 구분한다

| 항목 | registered design | 2026-08-09 live page | 연구상 해석 |
|---|---:|---:|---|
| training 규모 | Task 1 약 500, Task 2 약 300 계획 | 417 scan, 409 unique patient | 계획 수치를 실제 sample size로 쓰지 않는다. |
| center | 다기관 CTA/MRA, UMCU test 계획 | CHUV 200, HUG 87, Mie-Chuo 54, public 68; UMCU test reserve | center/patient group split이 필요하다. |
| location taxonomy | 50개 이상 | 52 class | generic coarse artery 분류보다 훨씬 세밀하다. |
| released target | location와 type/lesion mask 계획 | location mask+JSON, type mask, vessel mask | exact payload semantics는 접근 뒤 다시 감사한다. |
| vessel mask | 일부 gold annotation 계획 | organizer model이 예측한 vessel mask로 명시 | silver anatomy를 ground truth라 부르지 않는다. |

Live page에는 saccular, dissecting, fusiform type mask와 52-class location
annotation이 기술돼 있다. Center 4에는 일곱 환자의 longitudinal scan이 있지만
filename 숫자가 시간 순서를 뜻하지 않는다고 명시한다. 이를 growth cohort로
재해석하지 않는다.

Challenge design은 parent vessel ambiguity가 생기는 구체적 오류원을 이미
열거한다. Bifurcation에서 여러 vessel이 병변에 닿는 경우, CTA의 skull-base
ICA, 얽힌 ACA laterality, small/low-contrast lesion과 center별 annotation style이
대표적이다. 반면 label은 single clinician verification을 거친 hard class이며,
inter-rater distribution이나 multi-parent reference는 제공된다고 확인되지
않았다. 따라서 attachment posterior의 calibration을 hard class accuracy보다
강하게 주장할 reference가 아직 없다.

Grand Challenge verified account와 공식 data terms가 필요하다. Download가
terms agreement로 취급되므로 에이전트는 사용자를 대신해 가입·동의·다운로드하지
않았다. TopAneu image, NIfTI, JSON, mask와 vessel prediction payload는 모두
읽지 않았다.

## 3. 직접 선행연구 red team

다음은 새 contribution이 아니다.

| 이미 점유된 요소 | 가장 가까운 직접 연구 | 이 후보에서의 처리 |
|---|---|---|
| soft vessel-distance prior | [Vessel-aware multi-scale deformable 3D attention, MICCAI 2024](https://papers.miccai.org/miccai-2024/831-Paper2366.html) | hard mask 대신 distance map을 넣는 것만으로 novelty를 주장하지 않는다. |
| soft vesselness와 weak lesion supervision | [Vesselness-prior multitask U-Net, ICCVW 2025](https://openaccess.thecvf.com/content/ICCV2025W/CVAMD/papers/Rainville_Weakly_Supervised_Intracranial_Aneurysm_Detection_and_Segmentation_in_MR_angiography_ICCVW_2025_paper.pdf) | vesselness input/attention과 joint detection-segmentation은 baseline이다. |
| patient-specific centerline graph와 artery-aware fusion | [ARAN, CVPRW 2026](https://openaccess.thecvf.com/content/CVPR2026W/PHAROS-AIF-MIH/papers/Shafique_ARAN_Leveraging_Foundation_Models_for_Vasculature-Tree-Informed_ARtery-Aware_Intracranial_ANeurysm_Detection_CVPRW_2026_paper.pdf) | GAT, curvature/torsion feature와 geometry-gated cross-attention은 direct baseline이다. |
| joint aneurysm/vessel multitask prediction | [RSNA 2025 second-place report](https://arxiv.org/abs/2606.26706) | lesion+vessel head를 추가하는 것 자체는 contribution이 아니다. |
| anatomy-aware pretraining/prompt | [AMAP, npj Digital Medicine 2025](https://doi.org/10.1038/s41746-025-02188-8) | foundation feature와 anatomy prompt는 engineering control이다. |
| universal taxonomy와 partial-label projection | [Overlapping-label multidomain segmentation, WACV 2022](https://openaccess.thecvf.com/content/WACV2022/html/Bevandi_Multi-Domain_Semantic_Segmentation_With_Overlapping_Labels_WACV_2022_paper.html) | class ontology를 통합하거나 log-sum projection하는 일반론은 novelty가 아니다. |
| hierarchical classification/segmentation loss | generic tree loss와 hierarchical recognition literature | 52-class tree loss만 붙인 방법은 기각한다. |

ARAN은 이미 CTA/MRA artery classification을 위해 VISTA3D vessel segmentation,
patient-specific centerline graph, radius/eccentricity/curvature/torsion GAT와
geometry-gated cross-attention을 사용한다. MICCAI 2024 방법은 vessel signed
distance에 deformable attention을 둔다. 따라서 `vessel-aware`, `graph-based`,
`parent-artery-aware`, `foundation model` 또는 `soft anatomy prior`는 독립
novelty가 될 수 없다.

TopAneu challenge 자체도 fine-grained location classification과 lesion
segmentation을 직접 점유한다. 남을 수 있는 차이는 단순 multitask가 아니라
**한 patient-specific attachment variable에서 voxel support와 ontology label을
동시에 유도하는 구조적 estimand**, 그리고 그 제약이 실제 detection/segmentation
오류를 줄인다는 prospective evidence다. 이 차이는 아직 문헌 부재와 데이터
적합성 모두에서 확정되지 않았다.

## 4. 공개 multi-center CTA metadata discovery

별도 공개 자료인
[Open dataset of annotated head CTA](https://doi.org/10.5281/zenodo.15697196)는
CC BY 4.0이며 data paper DOI는
[10.3390/data11040074](https://doi.org/10.3390/data11040074)다. 전체
`Dataset.zip`을 받지 않고 기존 AURORA ZIP64 reader로 중앙 디렉터리와
`Metadata.csv` 한 member만 HTTP byte-range로 읽었다. DICOM pixel/header와 STL
payload는 읽지 않았다.

재현 가능한 privacy-safe aggregate는
[`open_multicenter_cta_metadata_discovery_20260809.json`](../results/open_multicenter_cta_metadata_discovery_20260809.json)에
분리한다.

| 항목 | 관찰값 |
|---|---:|
| official archive | 25,578,845,008 byte; MD5 `264ff9ee868c022d108b7c7aa7396d32` |
| ZIP contract | ZIP64; 149,452 member; central directory 11,207,225 byte |
| payload inventory | 149,329 DICOM, 122 STL, 1 metadata CSV |
| metadata member | 16,458 byte; SHA-256 `407cd3c3…bc7f4`; CP1251, semicolon |
| task units | 172 case: 90 control, 82 positive; 122 lesion row |
| multiplicity | 24 multi-lesion case; 최대 5 lesion/case |
| size | miliary 30, middle 56, large 20, giant 16 |
| location | 11 parent-artery code; LICA 33, RICA 27, MCA 32 등 |
| rupture field | 113 unruptured, 9 ruptured lesion row |

이 discovery는 patient/lesion mapping과 class imbalance를 확인하지만 새
headline을 열지 않는다. 172 case, 11 coarse artery code와 threshold-derived STL은
TopAneu 52-class attachment task의 confirmatory cohort가 아니다. Rupture 9건을
future risk target으로 사용하지 않는다. 향후 후보가 독립적으로 P0/P1을 통과한
경우 small-lesion, multi-lesion, scanner/center shift의 external stress test로만
검토한다.

## 5. ISBI 후보 점수

점수는 0–5이며 잠재적 매력이 아니라 현재 검증된 상태를 평가한다.

| 축 | 점수 | 냉정한 판정 |
|---|---:|---|
| biomedical-imaging relevance | 5.0 | 실제 CTA/MRA, lesion segmentation과 parent-vessel localization은 ISBI에 직접 맞는다. |
| identifiable estimand | 3.0 | attachment→mask/location은 정의 가능하지만 ambiguous bifurcation의 reference distribution이 없다. |
| direct-prior residual gap | 2.5 | ARAN, vessel-distance attention, multitask lesion/vessel와 hierarchy 학습 뒤 구조적 attachment만 잔는다. |
| data available now | 2.0 | 417-scan release가 있지만 terms를 수락하지 않았고 payload semantics를 감사하지 않았다. |
| independent sample size | 4.0 | 409 patient 다기관은 유망하지만 52 class의 rare support와 official hidden test 가용성은 미확인이다. |
| strong-baseline feasibility | 4.5 | challenge task, ARAN, vessel-aware detector, nnDetection/nnU-Net과 hierarchy control이 명확하다. |
| interpretable figure | 5.0 | CTA/MRA slice, lesion mask, centerline attachment와 projected location을 한 case에서 연결할 수 있다. |
| compute/runtime feasibility | 3.0 | A6000 PBS는 가용하나 full-resolution 3D multi-center 5-seed 비교는 마감 대비 무겁다. |

합계는 **29.0/40**이다. 자동 채택 기준 32/40에 못 미친다. 점수는 payload
접근만으로 자동 상승하지 않는다. 특히 hard-label ambiguity와 direct-prior
residual이 method-free P0/P1에서 해소돼야 한다.

## 6. 후보별 판정

1. **Patient-specific vascular attachment-consistent lesion inference**:
   조건부 lead로 보존하지만 shortlist에는 올리지 않는다. Exact payload
   semantics와 ambiguity가 감사되고, independent-head prediction이 실제로
   모순되며 그 모순이 lesion metric과 연결돼야 한다.
2. **Cross-dataset fine/coarse vascular taxonomy harmonization**:
   현재 기각한다. Universal taxonomy, partial-label projection과 tree loss의
   직접 범위다. Continuous attachment가 별도 식별 가능한 이득을 만들지
   못하면 새 문제도 아니다.
3. **Small-lesion/scanner robust CTA detection on the open 172-case data**:
   external stress 역할만 허용한다. Vessel-aware detection과 anatomy-aware
   pretraining이 이미 직접 경쟁하고 표본도 headline 방법 개발에 작다.

따라서 active problem shortlist는 계속 **0개**다. Architecture, method name,
loss, GPU training, outer test와 contribution 문장을 만들지 않는다.

## 7. 다음 허용 gate

두 경로만 허용한다.

- 다른 fresh biomedical-imaging problem을 같은 기준으로 계속 감사한다.
- 사용자가 TopAneu verified account와 data terms를 직접 수락했다고 명시한 뒤,
  별도 prospective **P0-T asset/semantics audit**을 등록한다.

P0-T는 CPU/read-only이며 training을 하지 않는다. Exact release checksum과
patient/scan/center key, 52-class support, negative/multi-lesion unit, location
mask–JSON–type mask mapping, vessel mask의 silver provenance, longitudinal group,
split viability와 bifurcation ambiguity의 감사 가능성을 결과 전에 고정한다.
P0-T pass도 method/GPU를 열지 않고 method-free P1만 등록한다. 약관 수락 전에는
download, payload read, executable model config와 server staging을 하지 않는다.

## 8. 최종 판정

이번 감사는 유망한 영상 문제를 하나 좁혔지만 연구 정체성을 확정하지 못했다.
`vascular attachment`라는 이름으로 기존 GNN·vessel prior·hierarchy loss를
재포장하는 것은 허용하지 않는다. 현재 가장 정직한 상태는 **conditional lead,
29.0/40, active shortlist 0**이다. Open CTA metadata는 재현 가능한 asset
discovery일 뿐 TopAneu supervision이나 성능 근거가 아니다.
