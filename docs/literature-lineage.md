# 선행연구 계보와 research gap

검토 기준일: 2026-08-03 KST

원칙: DOI, 공식 proceedings, 저널, 공식 dataset record, arXiv 원문을
우선한다. arXiv preprint는 peer-reviewed evidence와 분리한다.

## 1. 계보

### 1.1 형태·혈류와 파열 상태의 연관성

초기 CFD 연구는 morphology-only, hemodynamics-only, combined model을
비교했다. Xiang et al.은 119 IA에서 size ratio, WSS, OSI 등과 rupture
status의 연관성을 분석했다. 이후 여러 연구가 clinical, morphology,
hemodynamics의 결합을 시도했지만 대부분 retrospective status
classification이다.

- [Hemodynamic-Morphologic Discriminants for Intracranial Aneurysm Rupture
  (Stroke, 2011)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3021316/)
- [Machine Learning Classification of Cerebral Aneurysm Rupture Status
  (Radiology: AI, 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8017392/)
- [Small IA rupture-status prediction with CTA-derived hemodynamics,
  multicenter](https://pmc.ncbi.nlm.nih.gov/articles/PMC8041003/)

**남은 문제:** rupture status는 future rupture event가 아니다. ruptured
geometry가 rupture 이전과 같다는 보장도 없으며, 치료 선택과 referral
bias가 있다.

### 1.2 CFD reliability와 BC sensitivity

patient-specific geometry만으로 patient-specific hemodynamics가 정해지지
않는다. inflow waveform, outlet split, segmentation, smoothing, rheology,
wall assumption이 field와 derived biomarker를 바꾼다.

- [Generalized versus patient-specific inflow BC
  (AJNR, 2014)](https://pubmed.ncbi.nlm.nih.gov/24651816/)
- [Inflow variability in rupture assessment
  (J Biomech, 2020)](https://pubmed.ncbi.nlm.nih.gov/32008209/)
- [Segmentation versus outlet BC sensitivity
  (Int J CARS, 2023)](https://pubmed.ncbi.nlm.nih.gov/37582997/)
- [Impact of workflow variability
  (Computers in Biology and Medicine, 2025)](https://www.sciencedirect.com/science/article/pii/S0010482525003695)

**AURORA의 출발점:** BC가 없는데 deterministic field를 출력하는 것은
architecture 문제가 아니라 inverse problem의 식별성 문제다.

### 1.3 mesh simulation learning

MeshGraphNet은 unstructured mesh에서 encode–process–decode와 autoregressive
next-step prediction을 정립했다. 이후 masked pretraining, multiscale GNN,
graph transformer가 long-range dependency와 효율을 개선했다.

- [MeshGraphNets (ICLR 2021)](https://arxiv.org/abs/2010.03409)
- [GNOT (ICML 2023)](https://proceedings.mlr.press/v202/hao23c.html)
- [Transolver (ICML 2024)](https://proceedings.mlr.press/v235/wu24r.html)
- [MeshMask (ICML 2025)](https://arxiv.org/abs/2410.20952)

**남은 문제:** 일반 PDE benchmark의 낮은 field error가 aneurysm wall
functional이나 clinical association을 보존한다는 근거는 없다.

### 1.4 aneurysm hemodynamic surrogate

2026년 npj Digital Medicine의 In-PI-MGN은 105개 semi-idealized ICA
sidewall geometry에서 transient velocity를 예측했다. current velocity,
acceleration, node type, distance-to-inflow, inflow statistics를 입력으로
사용하고 physics constraint와 inflow context를 결합한다.

- [Physics constrained GNN for real-time IA hemodynamics
  (npj Digital Medicine, 2026)](https://www.nature.com/articles/s41746-026-02404-z)

같은 연구 계열의 2025-12 arXiv preprint는 graph transformer, sparse/global
attention, masking, multi-stage pretraining을 사용하고 AneuXplore,
few-shot patient geometry, MATCH OOD에서 평가한다.

- [Graph Deep Learning for Intracranial Aneurysm Blood Flow Simulation and
  Risk Assessment (arXiv, 2025)](https://arxiv.org/abs/2512.09013)

**구분점:** 두 방법 모두 known inflow/current flow state 아래의 forward
surrogate에 가깝다. geometry-only missing-BC distribution과 downstream
functional sufficiency가 중심이 아니다.

### 1.5 대규모 synthetic geometry–CFD

Aneumo는 427 real geometry에서 10,660 synthetic shape를 만들고 각 shape에
8개 steady mass-flow condition을 계산했다. AneuG-Flow는 generative
geometry와 14,000 steady/수백 pulsatile CFD case, BC metadata, surface 및
volume field를 제공한다.

- [Aneumo (arXiv, 2025)](https://arxiv.org/abs/2505.14717)
- [AneuG-Flow (NeurIPS 2025 Datasets &
  Benchmarks)](https://papers.nips.cc/paper_files/paper/2025/hash/e2b8ff0035bc9f572a7deefbcbea85bc-Abstract-Datasets_and_Benchmarks_Track.html)

**기회:** 동일 geometry의 multiple BC가 geometry effect와 BC-induced
variation을 분리할 수 있게 한다. 다만 synthetic geometry/solver policy는
clinical truth가 아니다.

### 1.6 probabilistic operator learning

probabilistic neural operator는 output function space의 distribution을
proper scoring rule로 학습한다. 이는 AURORA의 uncertainty mechanism에
직접적인 방법론적 기반을 제공한다.

- [Probabilistic Neural Operators for Functional Uncertainty Quantification
  (arXiv, 2025)](https://arxiv.org/abs/2502.12902)
- [Neural Operator Processes under Partial Observations
  (arXiv, 2026)](https://arxiv.org/abs/2606.22946)
- [Flow-matching Operators for Residual-Augmented Probabilistic Learning of
  PDEs (ICLR, 2026)](https://openreview.net/forum?id=fcBMLJtCoc)
- [Guided Diffusion Sampling on Function Spaces with Applications to PDEs
  (NeurIPS, 2025)](https://openreview.net/forum?id=oAgwvZay2U)

**영향:** 확률적 operator, flow matching, sparse/noisy observation을
도입하는 것 자체는 novelty가 아니다. AURORA는 생성 방식이 아니라 임의
physical-condition observation mask 사이의 nested coherence와 paired
condition response를 검증해야 한다.

### 1.7 boundary-indexed operator와 conditional consistency

ICLR 2026 연구는 varying BC에서 하나의 neural operator가 아니라
boundary-indexed operator family를 학습하며 support 밖에서는 식별되지
않는다는 문제를 직접 정식화했다. NeurIPS 2025 Flow Matching Neural
Processes는 target set의 marginal/conditional consistency를 다룬다.

- [One Operator to Rule Them All? On Boundary-Indexed Operator Families in
  Neural PDE Solvers (ICLR, 2026)](https://openreview.net/forum?id=lDjWQ9UxRy)
- [Flow Matching Neural Processes
  (NeurIPS, 2025)](https://papers.neurips.cc/paper_files/paper/2025/file/a92519f525c00085095fa41c5c46cdb5-Paper-Conference.pdf)

**영향:** missing-BC 비식별성 또는 “consistency”라는 이름만으로는
contribution이 되지 않는다. AURORA는 하나의 joint BC density를 arbitrary
mask에 조건화해 PDE solution으로 pushforward하는 구체적 구조, nested-mask
tower-property metric, same-geometry response supervision을 함께 입증해야
한다.

### 1.8 uncertainty와 OOD PDE

PDE OOD에서 ensemble, uncertainty, conservation update를 비교한 연구와
neural operator를 function-valued Gaussian process로 선형화한 연구가 있다.

- [Using Uncertainty Quantification to Characterize and Improve Out-of-
  Distribution Learning for PDEs
  (ICML, 2024)](https://openreview.net/forum?id=Y50K6DSrWo)
- [Linearization Turns Neural Operators into Function-Valued Gaussian
  Processes (ICML, 2025)](https://openreview.net/forum?id=4Z04wVQ9FY)

**영향:** OOD uncertainty 하나를 보고하는 것은 부족하다. BC completion
축과 model ensemble 축을 분리하고 각각 condition error와 geometry OOD
error를 추적하는지 falsification해야 한다.

### 1.9 직접적인 2026 multimodal 경쟁작

2026-07 arXiv preprint는 PointNeXt geometry, unsteady PINN descriptors,
clinical variables를 late fusion하여 rupture-status prediction을
보고했다.

- [Integrating PINNs and 3D Vascular Geometry Learning for Multimodal
  Rupture-Risk Prediction (arXiv, 2026)](https://arxiv.org/abs/2607.10530)

이 논문 때문에 “PINN + geometry + clinical + hemodynamics”는 novelty가
아니다. AURORA는 아래를 반드시 실험으로 구분해야 한다.

- prescribed BC point prediction vs missing-BC distribution
- independently generated descriptor late fusion vs task-aligned functional
  sufficiency
- pooled out-of-fold score vs nested patient-level evaluation/calibration
- field point accuracy vs distributional coverage and decision retention

## 2. 데이터 계보

| 데이터 | 직접 관측 | 규모와 domain | AURORA 역할 |
|---|---|---|---|
| AneuX | surface geometry, morphology/clinical 일부, status | 750; multi-source | external status stress test |
| CMHA | CTA, 3D models, clinical/morphology/hemodynamic data | 99 IA + 44 controls | real-CFD bridge/gate |
| BenchAnXplore | transient CFD on semi-idealized geometry | 105; ICA sidewall 중심 | transient reproduction |
| Aneumo | synthetic deformation × 8 steady BC | 85,280 simulations | BC sensitivity pretraining |
| AneuG-Flow | synthetic geometry, steady/pulsatile CFD, BC | large, MCA bifurcation | operator pretraining |

- [CMHA official dataset record](https://springernature.figshare.com/articles/dataset/CMHA_Intracranial_Aneurysm_CTA_Image_3D_Model_Dataset_with_Clinical_Morphological_Hemodynamic_Data/26965450)
- [AneuX project](https://aneux.org/)

서로 다른 dataset row를 “통합”한다는 것은 환자를 합친다는 뜻이 아니다.
공통 schema와 provenance로 나란히 관리하고, 역할별로 독립 split을 만든다.

## 3. research gap matrix

| 선행 축 | 해결한 것 | 아직 비어 있는 것 | AURORA 검증 |
|---|---|---|---|
| rupture-status ML | multimodal association | CFD increment·status≠future risk | secondary diagnostic only |
| autoregressive GNN | fast transient field | partial/missing condition, rollout drift | coherence + efficiency gate |
| graph transformer | long-range mesh interaction | calibrated field family | shared-backbone comparison |
| boundary-indexed NO | varying-BC non-identifiability 정식화 | arbitrary-mask coherent prediction | tower-property test |
| probabilistic operator | function-space UQ/generative sampling | condition-source attribution | coherent BC pushforward |
| neural process consistency | marginal/conditional consistency | physical-condition operator response | nested masks + paired response |
| PDE UQ/OOD | model uncertainty와 OOD 분석 | BC-induced vs model-induced 분리 | two-axis falsification |
| synthetic CFD | 같은 geometry의 multiple BC | response supervision/generalization | paired \(\Delta H\) |

## 4. novelty를 지키기 위한 필수 baseline

다음 비교가 없으면 contribution을 증명할 수 없다.

1. zero/mean/conditional-mean BC imputation
2. mask-token deterministic operator
3. independent probabilistic head per observation mask
4. MC-dropout/deep ensemble
5. 공개 probabilistic/flow-matching operator
6. joint BC density + shared operator, pair loss 없음
7. full AURORA
8. random cross-geometry pair negative control
9. In-PI-MGN 또는 공개 graph-transformer checkpoint/재현
10. Secondary analysis에서만 clinical+morphology와 +real CFD

## 5. 문헌상 아직 단정하지 않는 것

- “hemodynamics가 morphology보다 항상 우수하다”
- “WSS가 낮거나 높으면 곧 파열된다”
- “CFD는 ground truth다”
- “semi-idealized geometry에서의 OOD가 임상 외부 검증이다”
- “uncertainty interval이 넓으면 곧 임상 위험이 높다”
- “cross-sectional status model이 2년/5년 rupture probability를 준다”

이 문구들은 결과가 좋아도 현재 데이터로는 주장하지 않는다.
