# 2026-08-09 problem-level candidate audit · historical, superseded

상태: **RSNA candidate rejected by later supervision-semantics audit · active
shortlist 0 · no selected method · no GPU authorization · not submission-ready**

> **2026-08-09 판정 갱신.** 이 문서가 조건부로 남겼던 RSNA
> annotation-selection-aware mixed-granularity lesion-set 후보는 같은 날의
> [supervision-semantics red team](rsna-supervision-semantics-audit-2026-08-09.md)에서
> 기각됐다. 제공 segmentation은 aneurysm extent가 아니라 13-class
> Circle-of-Willis 혈관 해부구조이며, 공식 aneurysm supervision은 center
> point와 presence/territory label이다. 아래 L0–L3는 당시의 prospective
> reasoning을 보존하는 history일 뿐 실행 가능한 현재 protocol이 아니다.

이 문서는 실패한 BC-operator, Aneumo 3D와 4D-flow 연구선을 다른 이름으로
되살리기 위한 문서가 아니다. ISBI 2027에 제출할 수 있는 새 문제를
방법론보다 먼저 선별한 cold audit이다. 문헌 검색만으로 얻은 수치와 실제
archive에서 검증한 수치를 구분하며, 데이터 이용 약관에 대한 동의는
사용자만 할 수 있다.

## 1. 당시 남겼던 후보 · 현재 기각

조건부 shortlist는 **annotation-selection-aware mixed-granularity
anatomy-structured lesion-set inference**다. 적용 데이터 후보는 controlled-access
[RSNA Intracranial Aneurysm Detection 2025](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)다.
공식 설명상 18개 기관의 4,000건 이상 CT/MR angiography와 13개 해부학적
위치 annotation, 일부 AI-generated segmentation 연구가 포함된다. 이 숫자는
archive audit 결과가 아니며 정확한 patient/study/lesion 수는 접근 뒤 다시
검증해야 한다.

한 scan의 목표를 14개의 서로 독립적인 binary label로 놓지 않는다. 잠재
정답을 순서가 없는 유한 병변 집합

\[
  S=\{(r_i,e_i,m_i)\}_{i=1}^{N}
\]

로 둔다. 여기서 \(r_i\)는 3D 위치 또는 extent, \(e_i\)는 vascular territory,
\(m_i\)는 이용 가능한 경우에만 존재하는 lesion mark다. Study-level presence,
territory multi-label, point localizer와 mask는 서로 다른 정답이 아니라 같은
\(S\)를 부분적으로 관측하는 annotation operator \(O_k(S)\)다. 그러나 어떤
study에 어떤 granularity \(K\)가 부여됐는지도 무작위라고 가정할 수 없다.
Site, modality, visible lesion, challenge workflow 또는 AI-generated label
eligibility가 annotation selection \(R\)을 바꿀 수 있다. 따라서 완전한 후보
형태는

\[
  p_{\theta,\phi}(A,K,R\mid X)=
  \int p(A\mid O_K(S),R)\,
  \pi_\phi(K,R\mid S,X)\,p_\theta(S\mid X)\,dS
\]

처럼 lesion set과 annotation-selection mechanism을 구분해야 한다. L0에서
selection이 관측 변수에 조건부로 무시 가능한지 확인하기 전에는
coarsening-at-random을 가정하지 않는다. Selection이 unobserved lesion에
의존하고 audit으로 식별되지 않으면 point-identification claim을 포기하고
sensitivity bound 또는 후보 폐기를 택한다. 이 식은 문제 경계를 정할 뿐,
tractable likelihood나 architecture가 이미 설계됐다는 뜻이 아니다.

임상적 예측을 주장하지 않는다. 허용되는 endpoint는 cross-sectional
lesion detection/localization과 reading-candidate burden이다. Rupture risk,
future growth, clinical utility와 autonomous diagnosis는 범위 밖이다.

## 2. 왜 이 후보만 남겼는가

| 검토 후보 | 직접 선행 연구 또는 데이터 한계 | 판정 |
|---|---|---|
| 일반 3D segmentation/detection + uncertainty | RSNA 상위권 vessel/ROI pipeline, multitask 3D nnU-Net, anatomy-aware foundation model, topology-guided uncertainty가 이미 직접 다룬다. | 독립 정체성으로 기각 |
| longitudinal growth | 공개 Royal Brisbane cohort는 63명/85 aneurysm이지만 clinician annotation은 patient당 선택된 한 session에만 제공된다. AGED와 2026 Bayesian growth detection도 직접 경쟁한다. | data/novelty 모두 부족해 기각 |
| geometry×BC shape-response operator | GINO, Reference Neural Operator, geometric operator learning과 2026 Shape-DINO가 variable-domain/shape derivative를 직접 다룬다. | 직접 점유되어 기각 |
| cross-protocol 4D-flow posterior prediction | I0b가 payload 접근 전에 execution-incomplete로 끝났고 등록된 no-rerun contract에 따라 branch를 닫았다. 실제 독립 flow unit도 매우 적다. | 보존된 closed branch |
| annotation-selection-aware lesion set | Structured latent-output weak detection, mixed-supervision detection/medical segmentation, partial-label learning, set prediction, vessel anatomy와 conformal control 각각은 선행 연구다. 남을 수 있는 gap은 annotation selection이 비무작위일 때의 식별·sensitivity와 lesion burden을 함께 다루는 정확한 task뿐이다. | **access와 L0 audit에 조건부 shortlist** |

Heterogeneous label을 latent structured output으로 두는 발상은 NeurIPS
2010에 이미 있었고, NeurIPS 2021 mixed-supervised detection은 image-level과
box/mask supervision을 결합했다. Medical imaging에서도 image-level
classification과 lesion segmentation의 mixed supervision이 직접 존재하며,
ICML 2024는 partial/unlabeled supervision을 통합적으로 다룬다. 따라서
annotation projection과 marginalization 자체도 novelty가 아니다.

이 후보의 장점은 새 module을 붙이기 전에 문제 단위를 고칠 수 있다는 데
있다. 한 환자에서 여러 aneurysm이 있을 때 scan, location label, lesion과
segmentation을 독립 sample처럼 세는 오류를 피하고, coarse label과 dense
label의 예측이 서로 모순되는지 직접 검사할 수 있다. 동시에 공개 challenge의
강한 baseline과 실제 multisite/modal variation이 있어 음수 결과도 명확하게
판정할 수 있다.

## 2-A. 공개 대안 데이터셋 substitution screen

2026-08-09에 공식 challenge·dataset record와 원 저자 저장소만 사용해 네
대안을 다시 검사했다. 이는 archive나 image payload를 읽은 asset audit이
아니라 **source-only metadata screen**이다. 데이터 약관에 동의하거나 접근
권한을 획득하지 않았고, 어느 후보도 method 또는 GPU 실행을 허용하지 않는다.

| 후보 | 공식적으로 확인된 supervision·access | 현재 문제를 대체하지 못하는 이유 | 허용 가능한 후속 역할 |
|---|---|---|---|
| [CADA 2020](https://cada.grand-challenge.org/Dataset/) | 3D rotational angiography. Detection은 109 volume/127 aneurysm, segmentation은 110 volume/128 aneurysm이며 training image에 mask·center 정보를 함께 제공한다. 등록 승인 뒤 접근하며 [CC BY-NC-ND 4.0](https://cada.grand-challenge.org/Copyright/)이다. | Training annotation이 task별로 사실상 완전해 dense/sparse annotation **선택**을 식별하는 cohort가 아니다. RSNA의 multisite CT/MR study-level lesion-set 구조도 대체하지 않는다. | 사용자 접근 뒤 fully supervised 3DRA detection/segmentation external stress test |
| [ADAM 2020](https://adam.isi.uu.nl/data/) | 113 TOF-MRA+structural MR scan, 93 positive/20 negative이며 center·radius와 consensus binary mask를 제공한다. 일부 subject의 baseline/follow-up이 함께 있고 registration·confidentiality agreement가 필요하다. | Point와 mask가 같은 training case에 제공되는 fully supervised task다. Repeat scan을 독립 patient로 세면 leakage가 생기며 annotation-selection gap을 제공하지 않는다. | 사용자 접근 뒤 MRA fully supervised baseline·modality stress test |
| [IntrA](https://github.com/intra3d2019/IntrA) | 원 저자 저장소가 103 reconstructed vessel model, 1,694 healthy/215 aneurysm segment와 116 manually annotated aneurysm segment를 공개한다. Raw 2D MRA는 제공하지 않는다. | Local surface segment 단위이고 whole-study negative·lesion cardinality·localizer가 없다. 116개 dense subset의 선택 규칙과 dataset license도 payload 사용 전에 별도 감사가 필요하다. | License 확인 뒤 surface anatomy/part-segmentation pretraining 또는 sanity check |
| [TopCoW](https://zenodo.org/records/15692630) | CTA/MRA의 Circle-of-Willis mask, ROI와 graph를 공개한다. Main release는 source attribution과 commercial-use permission 조건이 있다. | Aneurysm lesion annotation이 아니다. 공개 external LargeIA/Lausanne 각 20 case도 공식 record상 CoW ROI에 aneurysm이 없는 subset이다. | Anatomy encoder·vessel topology control; lesion-set headline evidence로 사용 금지 |

이 source-only screen의 당시 결론은 RSNA를 더 작은 공개 segmentation
task로 바꾸지 않는다는 것이었다. 이후 supervision semantics가 핵심 전제를
반박했으므로 RSNA access를 기다리지 않고 후보를 폐기했다. CADA·ADAM·IntrA·
TopCoW도 기각된 estimand를 구제하지 않으며, 다음은 fresh problem-level
audit이다.

## 3. novelty를 인정하기 위한 최소 조건

아래 요소는 단독 contribution이 아니다.

- vessel graph, GNN, graph transformer 또는 anatomy prompt
- DETR류 set prediction, point process 또는 segmentation backbone
- weak/mixed supervision과 missing-label marginalization 일반론
- latent structured-output marginalization과 coarsening-at-random 가정
- temperature scaling, deep ensemble, conformal prediction 또는 FDR control
- CT/MR multimodal training과 foundation-model feature

독립 contribution 후보는 다음 세 항이 **모두** 성립할 때만 작성한다.

1. 실제 archive의 label 생성·선택 과정을 반영하고 non-random annotation
   selection 아래의 식별 조건 또는 sensitivity bound를 갖는 새로운 tractable
   lesion-set algorithm 또는 보장
2. 독립-head/ROI/multitask/set-prediction baseline보다 lesion localization과
   cross-granularity coherence를 함께 개선하는 patient/study-level evidence
3. 동일 sensitivity에서 candidate per study를 줄이거나, 고정된 candidate
   burden에서 missed-lesion risk를 줄이는 calibration-supported evidence

세 번째 항의 risk control은 평가 가치가 있지만 그 자체가 novelty는 아니다.
Morphological conformal prediction과 medical instance-level FDR control이
이미 존재하므로, 적용만 한 결과는 contribution으로 세지 않는다. Site 또는
modality shift에서 exchangeability가 깨지면 coverage를 보장했다고 쓰지 않고
OOD detection/abstention만 평가한다.

## 4. Historical L0 · 실행하지 않는 조건부 계획

2026-08-09 현재 `introai9`의 bounded name audit에서 RSNA-ICA archive를 찾지
못했고 Kaggle credential/CLI도 없다. 이는 데이터가 서버 전체에 없다는
증명이 아니라 **현재 알려진 경로에 stage되지 않았다는 운영 판정**이다.
Controlled-access 약관을 에이전트가 사용자 대신 수락하거나 credential을
생성하지 않는다. 따라서 config, split, model code와 GPU job을 아직 만들지
않는다.

사용자가 공식 access를 완료하고 private asset 위치를 제공한 뒤, L0는
payload 학습 없이 CPU/read-only로 다음을 감사한다.

1. official version, license/terms, file count, byte size와 checksum
2. patient–study–series–site–modality key와 중복/파생 study 관계
3. study presence, 13 territory label, localizer와 segmentation의 정확한 mapping
4. multi-lesion study, negative study, rare territory와 partial annotation 수
5. AI-generated segmentation의 provenance와 ground-truth 사용 가능 범위
6. annotation granularity를 배정한 rule과 site/modality/lesion-dependent
   selection; coarsening-at-random의 검증 가능 조건
7. patient/site group split과 CT/MR별 validation/outer-test viability
8. 공개 가능한 aggregate와 공개하면 안 되는 image/annotation 경계

L0에는 사후 수선 대상이 될 수치 threshold를 아직 두지 않는다. 먼저 exact
counts와 task unit을 공개 aggregate로 고정한 뒤, label coverage와 split
viability에 대한 prospective L1 기준을 별도 commit으로 등록한다. L0가
patient-level linkage 또는 lesion mapping을 복구하지 못하면 이 후보도
폐기한다.

## 5. Historical L1–L3 · 실행하지 않는 단계적 계획

### L1 · method-free task adequacy

- lesion 수와 location-label cardinality의 일치·불일치 유형을 blind audit한다.
- official localizer/segmentation subset만으로 lesion-to-territory mapping의
  ambiguity를 측정한다.
- observed covariate별 annotation-selection propensity와 positivity를 검사하고,
  unobserved-lesion-dependent selection을 배제할 수 없으면 sensitivity range를
  먼저 산출한다.
- site·modality·rare territory를 보존하는 patient-level outer split이 가능한지
  확인한다.
- trivial study prior, anatomy prior와 published pipeline prediction만으로
  task가 포화되는지 확인한다.

L1까지 GPU가 필요하지 않다. 양수여도 method를 확정하지 않고 L2
development protocol만 연다.

### L2 · bounded method development

먼저 재현할 강한 비교군은 challenge 1위 vessel-segmentation+ROI classifier,
2위 tri-axial ROI+26-class 3D nnU-Net, nnDetection, anatomy heuristic,
topological shape representation, ARAN 계열 anatomy-aware model이다. 동일
patient split, image resolution policy, pretraining access와 compute budget을
기록한다.

그 뒤에만 다음 두 control을 분리해 비교한다.

- independent study/location heads 또는 shared multitask head
- latent lesion-set model + exact/controlled annotation marginalization

Architecture는 L1의 병목 뒤에 고른다. 3D encoder, vessel graph와 query decoder는
가능한 구현 구성요소일 뿐 현재 AURORA architecture가 아니다. 개발 단계는
validation-only이며 outer test를 읽지 않는다.

### L3 · prospective outer test

Headline metric은 lesion-level FROC/sensitivity at fixed candidates per study와
patient-bootstrap 95% CI다. Study-level AUPRC, per-territory macro AUPRC,
localization distance/overlap, calibration slope/intercept, Brier/ECE,
cross-granularity contradiction rate를 함께 보고한다. Site·modality subgroup은
sample size와 uncertainty를 항상 제시한다. 최소 five seeds에서 방향이
일치하지 않으면 평균 하나로 superiority를 주장하지 않는다.

Outer-test protocol은 baseline 재현과 development selection이 끝난 exact
commit에서 고정한다. 실패 뒤 같은 test에 architecture, matching rule,
threshold 또는 calibration strata를 맞추는 local repair는 금지한다.

## 6. 최종 판정

이 후보는 **기각됐다**. 이유는 access 부재가 아니라 공식 supervision
semantics가 latent mixed-granularity lesion-annotation 전제와 맞지 않기
때문이다. 현재 모델은 GNN도 set predictor도 아니며 active experiment도
없다. 다음 fresh problem-level audit에서 별도 후보를 고르기 전까지 이
문서의 방법·metric·L0–L3 계획을 재사용하거나 이름만 바꿔 복원하지 않는다.

## 7. 직접 확인한 1차 자료

- [RSNA-ICA official challenge page](https://www.rsna.org/artificial-intelligence/ai-image-challenge/intracranial-aneurysm-detection-ai-challenge)
- [RSNA-ICA official AWS registry](https://registry.opendata.aws/rsna-intracranial-aneurysm-detection-dataset/)
- [RSNA 2025 first-place public implementation](https://github.com/uchiyama33/rsna2025_1st_place)
- [RSNA 2025 second-place method report](https://arxiv.org/abs/2606.26706)
- [AMAP anatomy-aware domain prompting](https://www.nature.com/articles/s41746-025-02188-8)
- [ARAN vasculature-tree-informed detection](https://openaccess.thecvf.com/content/CVPR2026W/PHAROS-AIF-MIH/papers/Shafique_ARAN_Leveraging_Foundation_Models_for_Vasculature-Tree-Informed_ARtery-Aware_Intracranial_ANeurysm_Detection_CVPRW_2026_paper.pdf)
- [Morphological conformal prediction sets](https://papers.miccai.org/miccai-2025/0169-Paper3902.html)
- [Structured-output detection with heterogeneous weak labels (NeurIPS 2010)](https://proceedings.neurips.cc/paper/2010/hash/6da37dd3139aa4d9aa55b8d237ec5d4a-Abstract.html)
- [Mixed-supervised object detection (NeurIPS 2021)](https://proceedings.neurips.cc/paper/2021/hash/20885c72ca35d75619d6a378edea9f76-Abstract.html)
- [Collaborative medical classification and segmentation (CVPR 2019)](https://openaccess.thecvf.com/content_CVPR_2019/html/Zhou_Collaborative_Learning_of_Semi-Supervised_Segmentation_and_Classification_for_Medical_Images_CVPR_2019_paper.html)
- [Uniform partial-label and unlabeled learning (ICML 2024)](https://proceedings.mlr.press/v235/liu24ar.html)
- [OpenNeuro ds005096 longitudinal cohort record](https://openneuro.org/datasets/ds005096)
- [CADA official detection dataset and access](https://cada.grand-challenge.org/Dataset/)
- [CADA official license boundary](https://cada.grand-challenge.org/Copyright/)
- [ADAM official data and access](https://adam.isi.uu.nl/data/)
- [IntrA official author repository](https://github.com/intra3d2019/IntrA)
- [TopCoW permanent official data release](https://zenodo.org/records/15692630)
- [Bayesian longitudinal aneurysm growth detection](https://arxiv.org/abs/2604.06649)
- [Shape-DINO](https://arxiv.org/abs/2603.03211)
