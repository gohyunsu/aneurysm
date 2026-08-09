# 2026-08-09 DSA prefix-risk candidate audit

상태: **source audit completed · rejected 31.0/40 · active shortlist 0 ·
no P0/model/GPU authorization · not submission-ready**

이 문서는 닫힌 AneuX·AneuG-Flow·4D-flow branch를 다른 이름으로 다시 실행하기
위한 계획이 아니다. 공개 1차 자료만으로 여섯 문제 후보를 다시 비교하고,
가장 높은 후보조차 현재 ISBI primary로 채택할 수 없는 이유를 고정한다.
Dataset payload, image frame, label과 patient identifier는 읽지 않았다.

## 1. 가장 높은 후보

검토한 질문은 다음과 같다.

> 이미 관측한 DSA prefix \(X_{1:t}\)로 전체 arterial-phase sequence에서 보일
> 최종 혈관 support \(Y\)를 추론하고, 특히 thin/distal vessel의 missed-support
> risk가 허용 수준 이하인지 보정해 언제 prefix가 충분한지 판정할 수 있는가?

형식적으로는 각 pixel 또는 centerline element의 contrast-arrival time
\(T_v\)를 latent event time으로 두고, prefix를 right-censored evidence로 보는
방법을 상상할 수 있다. 그러나 이것은 아직 method가 아니다. 현재 release가
지원하는 관측 task는 **전문가가 미리 고른 arterial-phase 4--14 frame의 prefix로
그 sequence의 merged 2D artery mask를 예측하는 것**뿐이다. 원 촬영을 조기에
중단했을 때의 radiation, contrast dose, missed pathology나 clinical action은
관측하지 않는다. 따라서 `acquisition stopping`, `dose reduction` 또는
`clinical utility`를 endpoint로 쓰지 않는다.

## 2. DIAS에서 실제로 확인된 것

[DIAS 원 논문](https://doi.org/10.1016/j.media.2024.103247)은 60 patient에서
얻은 120 DSA sequence를 보고한다. 원 sequence는 6--46 frame, 4 FPS였으나,
motion artifact·incomplete arterial phase·duplicate를 제외하고 전문의가
pre-contrast, capillary와 venous phase를 제거해 최종 release는 4--14 arterial
frame만 남겼다. 논문 본문의 summary는 120 sequence/753 frame, 수집 절은
120 sequence/762 image로 서로 다르게 적혀 있으므로 exact count는 payload
감사 전 unresolved다.

Full annotation은 patient ID를 기준으로 고른 60 sequence에만 제공한다. 두
neurosurgery MD student의 annotation을 10년 경력 associate physician이 교정하고
15년 경력 chief physician이 확인했다. Thick vessel과 thin vessel을 각각
anterior/posterior phase에서 중점적으로 표시한 뒤 pixelwise OR로 하나의 최종
2D mask를 만들었다. Frame별 arrival-time ground truth, prospective stop decision,
aneurysm mask와 clinical outcome은 제공하지 않는다.

가장 중요한 task-adequacy 경고는 원 논문의 input ablation이다.

| 입력 | DSC | clDice |
|---|---:|---:|
| first frame | 0.6232 | 0.6835 |
| last frame | 0.7604 | 0.6940 |
| first + last | 0.7777 | 0.7039 |
| temporal mean | 0.7790 | 0.6997 |
| minimum projection | 0.7802 | 0.7040 |
| full sequence VSS-Net | 0.7822 | 0.7119 |

Full-sequence DSC는 minimum projection보다 **0.0020** 높을 뿐이다. clDice의
0.0079 차이는 topology-sensitive endpoint를 검토할 근거는 되지만, prefix
stopping이 비자명하고 독립적인 problem이라는 증거는 아니다. 특히 공개
release 자체가 arterial phase를 수동 선별했으므로 full raw DSA에서 자동으로
언제 멈출지를 평가할 수 없다.

Official [Zenodo v3 record](https://zenodo.org/records/11637181)는 open access,
CC BY 4.0, `DIAS.zip` 292,444,663 byte와 MD5
`780f32df6fb2a5de5d476f385cf2e83b`를 명시한다. 이는 재사용 가능성만 확인하며,
이번 audit에서 archive를 내려받거나 열었다는 뜻이 아니다. Official
[code repository](https://github.com/lseventeen/DIAS)는 Apache-2.0이지만
code license와 dataset license를 혼동하지 않는다.

## 3. 직접 선행연구가 제거하는 novelty

| 단독으로는 새롭지 않은 요소 | 직접 선행·근거 | 판정 |
|---|---|---|
| full DSA sequence segmentation | DIAS의 VSS-Net, bidirectional ConvGRU 기반 TSI/ST-U-Net, [DSCA](https://doi.org/10.1109/TMI.2025.3540886) | temporal encoder나 2D+time segmentation은 mandatory baseline이다. |
| MIP와 informative-frame fusion | [TemSAM, MICCAI 2025](https://papers.miccai.org/miccai-2025/paper/2267_paper.pdf) | MIP global prompt, complementary frame selection과 cross-temporal attention은 직접 점유됐다. |
| incomplete angiogram의 temporal curve recovery | [RNN recovery of complete time-density curves](https://pmc.ncbi.nlm.nih.gov/articles/PMC9385185/)와 contrast-arrival parametric imaging | latent arrival map 또는 missing-frame imputation만으로 novelty가 되지 않는다. |
| risk-controlled early exit | [SAFE-KD](https://arxiv.org/abs/2602.03043) | confidence-based stopping과 risk-controlled exit를 의료영상에 적용하는 것만으로는 부족하다. |
| segmentation risk calibration | [Conditional conformal risk adaptation](https://arxiv.org/abs/2504.07611) 및 medical segmentation risk-control 계보 | conformal wrapper, coverage 또는 abstention 자체는 contribution이 아니다. |
| dynamic DSA vessel reconstruction | [vessel-probability-guided sparse-view dynamic DSA](https://arxiv.org/abs/2405.10705) | static/dynamic attenuation decomposition과 temporal consistency도 직접 비교 범위다. |

잔여 gap이 존재하려면 **prefix-censored contrast-arrival posterior가 같은 최종
vessel-support event에 대해 filtration-compatible하고, thin-vessel/topology
miss risk를 보정하며, full-sequence/MIP/TemSAM/DSCA/early-exit/conformal
baseline보다 실제 frame--risk frontier를 개선하는 operator-specific algorithm과
보장**이 모두 필요하다. 현재 source만으로는 마지막 요구를 식별하거나
평가할 수 없다.

## 4. 여섯 후보의 같은 기준 비교

각 축은 0--5이며 현재 확인된 자산과 직접 선행만 평가한다. 미래에 받을 수
있는 데이터나 만들 수 있는 annotation은 점수에 넣지 않는다.

| 후보 | relevance | estimand | residual gap | data now | independent unit | baselines | figure | runtime | 합계 | 판정 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [DIAS](https://zenodo.org/records/11637181) prefix-to-final support + calibrated miss risk | 4.5 | 3.5 | 2.0 | 4.5 | 2.5 | 5.0 | 5.0 | 4.0 | **31.0** | 기각 |
| [DynaVessel](https://github.com/alceballosa/robust-vessel-segmentation) dynamic-phase robust 3D CTA segmentation | 4.5 | 4.0 | 1.5 | 1.5 | 4.0 | 5.0 | 5.0 | 2.5 | 28.0 | 저자 연구가 task를 직접 점유하고 IRB request 필요 |
| [sparse-view dynamic DSA](https://arxiv.org/abs/2405.10705) 3D reconstruction | 4.5 | 3.5 | 2.0 | 1.0 | 2.0 | 4.5 | 5.0 | 2.5 | 25.0 | matching public multi-view geometry/ground truth 없음 |
| [IAVS](https://github.com/AbsoluteResonance/IAVS) CFD-applicability-aware vessel segmentation | 4.5 | 4.0 | 1.0 | 0.5 | 3.5 | 5.0 | 5.0 | 3.0 | 26.5 | dataset/code/weights 미공개이고 CFD applicability가 원 논문의 contribution |
| [flow-diverter 4D-flow](https://zenodo.org/records/17183575) treatment-response field model | 4.0 | 4.0 | 2.0 | 4.0 | 1.0 | 4.0 | 5.0 | 2.0 | 26.0 | 33 scan이지만 5 base geometry·2 source patient; 닫힌 4D-flow branch 재사용 금지 |
| DIAS weak-label selection/acquisition | 4.0 | 2.5 | 1.0 | 4.5 | 2.5 | 5.0 | 4.5 | 4.0 | 28.0 | full/weak/semi-supervision을 DIAS 자체가 직접 benchmark |

자동 admission 기준은 32/40이다. 가장 높은 DIAS prefix 후보도 31.0이므로
P0를 등록하지 않는다. 점수 한 점을 올리기 위해 endpoint를 `thin-vessel risk`로
사후 교체하지 않는다. 먼저 raw full-phase sequence, frame timestamp/exposure,
patient grouping과 prefix별 clinically meaningful action을 제공하는 독립 source가
확인돼야 새 version으로 다시 채점할 수 있다.

## 5. 실행·서버 판정

- `introai9`는 AURORA의 유일한 실행 대상이며 현재 AURORA PBS job은 0개다.
- `junjinyong`에는 접속, 조회, 제출 또는 모니터링하지 않는다.
- 알려진 `introai9` dataset root의 bounded read-only inventory에서 DIAS asset을
  찾지 못했다. 이는 서버 전체에 없다는 증명이 아니다.
- Source score가 gate 미달이므로 DIAS download, CPU/PBS P0, model code,
  Singularity image, GPU smoke, training과 outer test를 만들지 않는다.
- GPU를 비워 둔 것은 실행 실패가 아니라 사전 등록된 문제-selection rule을
  지킨 결과다.

## 6. 최종 판정

이 후보는 해석 가능한 progression figure와 명료한 probabilistic formulation을
가질 수 있지만, 현재 release에서는 **수동으로 잘린 arterial phase의 final-mask
segmentation을 일반 early-exit 문제로 다시 포장할 위험**이 더 크다. 강한
temporal/MIP/frame-selection/risk-control 선행이 존재하고 aggregate metric도
거의 포화됐다. 따라서 method name, GNN/U-Net/Transformer architecture,
checkpoint와 GPU job을 만들지 않으며 active shortlist를 0으로 유지한다.

다음 허용 작업은 DIAS score repair가 아니라, 독립된 새 biomedical-imaging
problem의 primary-source/task-unit audit이다.
