# 2026-08-09 inverse healthy-vessel counterfactual audit

상태: **source audit completed · rejected 27.0/40 · active shortlist 0 ·
no method/architecture/GPU/outer test · not submission-ready**

이 문서는 닫힌 Open-CTA parser를 수리하거나 실패한 Aneumo CFD 연구선을 다른
이름으로 되살리기 위한 계획이 아니다. `aneurysm-bearing surface → healthy
parent-vessel counterfactual + localized lesion edit`라는 새 문제를 실제 공개
자산과 가장 가까운 직접 선행연구로 먼저 반증한 기록이다. 데이터 payload를
추가로 받거나 모델을 학습하지 않았다.

## 1. 검토한 문제

관측한 aneurysm-bearing surface를 \(Y\), 병변 전 healthy parent-vessel
counterfactual을 \(H\), ostium과 aneurysm sac을 포함한 국소 edit를 \(Z\),
forward editor를 \(E\)라 두면 후보는

\[
  p(H,Z\mid Y), \qquad E(H,Z)\approx Y
\]

를 추론하는 문제였다. 단순 point-wise segmentation 대신 다음을 동시에
검사하려 했다.

1. 관측되지 않은 healthy parent vessel의 posterior
2. lesion/ostium support와 edit parameter
3. inferred counterfactual에 edit를 다시 적용한 reconstruction cycle
4. counterfactual uncertainty를 반영한 real-surface lesion localization

이는 해석 가능한 observed/pathology/counterfactual triptych을 만들 수 있고,
forward aneurysm generator를 inverse structured inference에 쓰는 좁은 잔여
가설을 제공한다. 그러나 이 formulation이 그럴듯하다는 사실과 현재 데이터에서
estimand가 식별된다는 사실은 다르다.

## 2. 현재 Aneumo가 제공하지 않는 짝

초기 [Aneumo preprint](https://arxiv.org/abs/2501.09980)는 466개
aneurysm-free model과 9,534개 deformed model을 포함한 10,000개 synthetic
model을 기술한다. 그러나 현재 프로젝트가 pin한 공개 release와 upstream
repository는 이 초기 기술과 동일한 자산 계약이 아니다.

- 현재 [upstream repository](https://github.com/Xigui-Li/Aneumo)는 427개
  AneuX base case에서 만든 10,660개 geometry와 `Connection.csv`의
  geometry-to-base mapping을 제공한다.
- Current datasheet는 aneurysm region을 제거한 뒤 randomized non-rigid
  deformation으로 다시 도입했다고 설명하지만, released instance의 label은
  CFD field이며 manual aneurysm/ostium annotation은 없다고 명시한다.
- `Connection.csv`의 현재 case naming은 `base_deform_index`이고, 공개
  `MPs.csv`의 case 1부터 size, neck width와 volume이 모두 정의된 aneurysm
  morphometry를 가진다. 프로젝트의 audited 64-case cache도 32 base family의
  두 **deformation**씩이지 healthy–pathological pair가 아니다.
- [Hugging Face release](https://huggingface.co/datasets/SAIS-Life-Science/Aneumo)는
  CC BY-NC-ND 4.0의 267개 archive shard를 나열하지만, 별도 healthy intermediate,
  ostium label 또는 forward-edit parameter를 식별하는 공개 pair manifest는
  확인되지 않았다.
- 제공 NIfTI는 whole vessel ROI mask다. Aneurysm sac/ostium semantic mask라고
  바꾸어 읽지 않는다.

따라서 “같은 patient anatomy의 observed healthy vessel이 이미 local cache에
있다”는 전제는 거짓이다. 초기 preprint의 legacy count를 현재 pinned asset의
paired supervision으로 소급 사용하지 않는다. Commercial mesh editing으로
중간 healthy geometry를 새로 만드는 것도 새로운 관측 정답이 아니라 연구자가
정한 pseudo-counterfactual이다.

## 3. IntrA는 real counterfactual 정답이 아니다

[IntrA author repository](https://github.com/intra3d2019/IntrA)와
[CVPR 2020 paper](https://openaccess.thecvf.com/content_CVPR_2020/papers/Yang_IntrA_3D_Intracranial_Aneurysm_Dataset_for_Deep_Learning_CVPR_2020_paper.pdf)는
다음을 제공한다고 기술한다.

- reconstructed whole-vessel model 103개; raw 2D MRA는 비공개
- 자동 생성된 local segment 1,909개: healthy 1,694개, aneurysm 215개
- 전문가가 경계를 나눈 aneurysm local segment 116개

이 구조는 surface classification/part segmentation baseline에는 유용하지만,
동일 환자의 병변 전 healthy vessel \(H\)를 관측하지 않는다. Whole-vessel
103개와 116개 local annotation 사이의 complete lesion-instance mapping,
whole-study negative/cardinality와 counterfactual surface도 공식 README에서
보장되지 않는다. Repository root에는 명시적 LICENSE 파일도 없고 README의
“open-access” 문구만 있으므로 payload 사용 권한을 license grant로 추정하지
않는다. 이번 audit에서는 IntrA payload를 받거나 읽지 않았다.

따라서 IntrA Dice/IoU는 lesion-support 평가가 될 수 있어도 healthy
counterfactual accuracy의 real ground truth는 아니다. Synthetic editor에서
학습하고 IntrA part segmentation만 평가하면 “inverse counterfactual recovery”와
“synthetic pretraining을 쓴 surface segmentation”을 구분할 수 없다.

## 4. 직접 선행연구가 이미 점유한 범위

| 이미 점유된 요소 | 직접 선행 | 이 후보에서의 처리 |
|---|---|---|
| aneurysm surface isolation | [Vascular surface segmentation](https://arxiv.org/abs/2005.14449), [two-step surface pipeline](https://arxiv.org/abs/2006.16161) | PointNet/PointNet++/SO-Net류 직접 segmentation은 strong baseline이지 novelty가 아니다. |
| healthy vessel 생성과 localized aneurysm editing | [SynVA](https://arxiv.org/abs/2605.17620) | Healthy generation, ostium selection, anatomy-conditioned sac synthesis와 50,000 labeled meshes는 forward editor 자체의 novelty를 제거한다. |
| sac–parent-vessel generative modeling | [AneuG, MICCAI 2025](https://papers.miccai.org/miccai-2025/paper/1474_paper.pdf) | Morphology-conditioned mesh generation 또는 GHD/VAE를 붙이는 것만으로는 새 방법이 아니다. |
| synthetic vasculature for aneurysm detection | [TMI 2025](https://pubmed.ncbi.nlm.nih.gov/39504285/) | Synthetic pathology augmentation 뒤 real detection/segmentation은 이미 직접 평가됐다. |
| healthy counterfactual lesion localization | [TMI counterfactual anomaly detection](https://pubmed.ncbi.nlm.nih.gov/39269801/), [ORBIT](https://openreview.net/forum?id=n5penvYg4j) | Healthy reconstruction과 structured mask proposal은 의료영상 일반에서 점유됐다. |
| point-cloud normal reconstruction/anomaly localization | [WACV 2023](https://openaccess.thecvf.com/content/WACV2023/papers/Bergmann_Anomaly_Detection_in_3D_Point_Clouds_Using_Deep_Geometric_Descriptors_WACV_2023_paper.pdf), [PCDiff](https://arxiv.org/abs/2606.25740) | Local/global point-cloud reconstruction residual과 diffusion anomaly map은 architecture novelty가 아니다. |

남을 수 있는 차이는 **명시적 vascular editor의 inverse posterior를 healthy
surface와 lesion edit에 걸쳐 함께 추론하고 forward-cycle로 검증하는 것**뿐이다.
하지만 현재 자산에는 paired healthy target과 real counterfactual 평가가 없어서
이 잔여 차이를 독립 contribution으로 검증할 수 없다.

## 5. ISBI 후보 점수

점수는 0--5이며 미래에 만들 수 있는 데이터가 아니라 현재 검증된 상태를
평가한다.

| 축 | 점수 | 냉정한 판정 |
|---|---:|---|
| biomedical-imaging relevance | 4.5 | Aneurysm/neck delineation과 parent-vessel morphology에 직접 연결되지만 raw image가 아닌 derived surface가 주 입력이다. |
| identifiable estimand | 2.5 | Synthetic editor 내부에서는 정의되지만 real healthy counterfactual은 관측되지 않고 여러 vessel continuation이 같은 \(Y\)를 설명할 수 있다. |
| direct-prior residual gap | 2.5 | Forward editing, healthy counterfactual, point-cloud anomaly reconstruction과 surface segmentation 뒤 inverse-editor posterior만 좁게 남는다. |
| data available now | 2.0 | Aneumo deformation과 IntrA segment는 공개됐지만 paired healthy target·ostium/edit manifest와 명시적 IntrA license가 없다. |
| independent sample size | 2.5 | Aneumo variation의 독립 단위는 427 base family이고 real IntrA는 103 whole model/116 local annotation으로 작고 mapping이 불완전하다. |
| strong-baseline feasibility | 4.5 | Supervised surface networks, curvature/centerline isolation, SynVA/AneuG, counterfactual reconstruction과 3D anomaly methods가 명확하다. |
| interpretable figure | 5.0 | Observed aneurysm, inferred healthy vessel, uncertainty band와 re-applied edit를 한 surface에서 시각화할 수 있다. |
| compute/runtime feasibility | 3.5 | Downsampled surface P0는 가능하지만 probabilistic mesh editing과 5-seed real external comparison은 가볍지 않다. |

합계는 **27.0/40**이다. 자동 shortlist 기준 32/40에 못 미친다. Pair asset
부재를 architecture의 cycle loss나 pseudo-label로 감추면 estimand가 좋아지는
것이 아니라 연구자가 만든 editor를 복원하는 self-consistency task가 된다.

## 6. 판정과 허용 범위

- 후보를 **source-audit rejection**으로 기록하고 active shortlist를 0으로
  유지한다.
- Method name, architecture, config, split, threshold, seed, P0 executable,
  checkpoint와 GPU job을 만들지 않는다.
- Aneumo의 기존 two-deformation cache를 healthy–pathological pair로 relabel하지
  않는다.
- IntrA payload를 명시적 license와 whole/local mapping 확인 없이 받지 않는다.
- SynVA procedural pair가 실제로 versioned release되고, disjoint real whole-vessel
  lesion mapping과 legal-use boundary까지 독립 audit에서 확인되더라도 이 문서를
  pass로 바꾸지 않는다. 그때는 새 version의 fresh candidate로 다시 채점한다.
- 다음 허용 작업은 이 후보의 pseudo-counterfactual repair가 아니라 다른
  biomedical-imaging problem에 대한 fresh primary-source/asset audit이다.

## 7. 최종 결론

Inverse editing은 설명 가능한 figure와 구조적 formulation을 제공하지만,
현재 상태에서는 **fancy한 architecture가 식별되지 않는 counterfactual target을
가리는 위험이 더 크다.** 직접 선행은 강하고, 현재 release에는 필요한 pair가
없으며, real dataset은 counterfactual correctness를 평가하지 못한다. 따라서
ISBI 2027 primary problem으로 채택하지 않는다.
