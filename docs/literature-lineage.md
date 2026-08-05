# 선행연구 계보와 research gap

검토 기준일: 2026-08-05 KST

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
geometry와 14,000 steady/수백 pulsatile CFD case, surface 및 volume field를
제공하지만 공개 benchmark의 boundary condition은 case마다 바뀌지 않는다.

- [Aneumo (arXiv, 2025)](https://arxiv.org/abs/2505.14717)
- [AneuG-Flow (NeurIPS 2025 Datasets &
  Benchmarks)](https://papers.nips.cc/paper_files/paper/2025/hash/e2b8ff0035bc9f572a7deefbcbea85bc-Abstract-Datasets_and_Benchmarks_Track.html)

**기회:** 동일 geometry의 multiple BC가 geometry effect와 BC-induced
variation을 분리할 수 있게 하는 자산은 현재 Aneumo다. AneuG-Flow는
known-condition geometry pretraining에만 사용한다. 두 dataset 모두
synthetic geometry/solver policy이며 clinical truth가 아니다.

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

ICLR 2026 AI\&PDE workshop 연구는 varying BC에서 하나의 neural operator가 아니라
boundary-indexed operator family를 학습하며 support 밖에서는 식별되지
않는다는 문제를 직접 정식화했다. TMLR 2026 연구는 CNP에서 context를
추가한 뒤 다시 예측한 분포와 기존 joint를 조건화한 분포 사이의 gap을
KL로 정의하고 few-shot에서 그 차이가 클 수 있음을 보였다. NeurIPS 2025
Flow Matching Neural Processes는 target set의 marginal/conditional
consistency를 다룬다.

- [One Operator to Rule Them All? On Boundary-Indexed Operator Families in
  Neural PDE Solvers (AI\&PDE at ICLR, 2026)](https://openreview.net/forum?id=lDjWQ9UxRy)
- [On the Conditioning Consistency Gap in Conditional Neural Processes
  (TMLR, 2026)](https://arxiv.org/abs/2604.19312)
- [Flow Matching Neural Processes
  (NeurIPS, 2025)](https://papers.neurips.cc/paper_files/paper/2025/file/a92519f525c00085095fa41c5c46cdb5-Paper-Conference.pdf)

**영향:** missing-BC 비식별성 또는 “consistency”라는 이름만으로는
contribution이 되지 않는다. AURORA는 하나의 joint BC density를 arbitrary
mask에 조건화해 PDE solution으로 pushforward하는 구체적 구조, nested-mask
tower-property metric, same-geometry response supervision을 함께 입증해야
한다.

Joint density를 conditional density로 보내는 연산 자체도 2026년
conditioning-operator 연구가 continuity와 neural-operator approximation
관점에서 직접 다뤘다.

- [One Operator for Many Densities: Amortized Approximation of Conditioning
  by Neural Operators (arXiv, 2026)](https://arxiv.org/abs/2605.06873)

따라서 analytic conditioning과 tower property는 construction과 audit
도구이지 독립적인 새 정리가 아니다.

### 1.8 known boundary condition을 다루는 operator

2026년 learned boundary-to-domain extension과 Generalized Neural
Operator는 복잡하거나 서로 다른 **주어진** BC를 표준 operator에
전달하는 구조를 제안했다. NeurIPS 2025 workshop의 boundary-augmented
operator도 boundary/domain interaction으로 geometry OOD를 개선한다.

- [Imposing Boundary Conditions on Neural Operators via Learned Function
  Extensions (arXiv, 2026)](https://arxiv.org/abs/2602.04923)
- [Generalized Neural Operator for Parametric and Boundary-Value Problems
  (arXiv, 2026)](https://arxiv.org/abs/2607.21932)
- [Boundary-Augmented Neural Operators for Better Generalization to Unseen
  Geometries (NeurIPS AI4Science, 2025)](https://openreview.net/forum?id=DqZoWaDwfN)

**영향:** BC를 explicit token/extension으로 넣는 것, 여러 BC type에서
full-condition accuracy를 높이는 것은 독립 novelty가 아니다. AURORA의
검증 단위는 알려진 BC의 encoding이 아니라 **일부 physical input만
관측된 mask lattice 전체가 한 joint law와 양립하는가**이다.

### 1.9 partial-input operator와 residual learning

AAAI-26의 LANO는 부분 관측 spatial input을 mask-to-predict로 학습하고
boundary-first latent autoregressive reconstruction을 수행한다. NeurIPS
2025의 DeltaPhi는 유사한 physical state 사이의 residual을 학습해
data-limited operator를 개선한다.

- [Learning Neural Operators from Partial Observations via Latent
  Autoregressive Modeling (AAAI, 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/37001)
- [DeltaPhi: Physical States Residual Learning for Neural Operators
  (NeurIPS, 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/12bf28fb68f295f855a5bf0c5a217d6e-Abstract-Conference.html)

**영향:** partial observation, boundary-first reconstruction, residual/pair
learning은 각각 독립 novelty가 아니다. AURORA는 physical-variable mask
filtration의 compatible distributions를 LANO/NOP와 비교하고,
same-geometry BC contrast가 DeltaPhi-style retrieval/residual, pair-loss 0,
random cross-geometry pair보다 response fidelity를 개선하는지 보여야 한다.

### 1.10 uncertainty와 OOD PDE

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

### 1.11 active feature acquisition과 decision consistency

ICML 2021의 generative-surrogate AFA는 미관측 feature를 test-time에
순차 획득하는 정책을 generative model로 학습했다. ICML 2024의 Acquisition
Conditioned Oracle은 greedy 정보이득을 넘어 prediction과 일반 decision을
위한 non-greedy feature acquisition을 직접 다룬다. PaPQS와 UNED는 각각
training PDE setting과 sensor design의 정보가치를 최적화한다.

- [Active Feature Acquisition with Generative Surrogate Models
  (ICML, 2021)](https://proceedings.mlr.press/v139/li21p.html)
- [Acquisition Conditioned Oracle for Nongreedy Active Feature Acquisition
  (ICML, 2024)](https://proceedings.mlr.press/v235/valancius24a.html)
- [A Plug-and-Play Query Synthesis Active Learning Framework for Neural PDE
  Solvers (NeurIPS, 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/6a1b224b153e55c40a6359f9c9fb9d8c-Abstract-Conference.html)

**영향:** 다음 BC component를 고르는 것, entropy/variance/expected-risk
acquisition을 쓰는 것, path independence만 재는 것은 novelty가 아니다.
AURORA의 살아남는 후보는 같은 최종 BC mask로 가는 route posterior의
불일치가 PDE solution-functional Bayes action과 acquisition ranking에
만드는 regret를 정량화하고, coherent joint law가 이를 실제 oracle risk와
함께 줄이는지 보이는 것이다.

### 1.12 직접적인 2026 multimodal 경쟁작

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
| AneuG-Flow | synthetic geometry, steady/pulsatile CFD; fixed BC policy | large, MCA bifurcation | known-condition geometry pretraining |

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
| known-BC operator | diverse BC encoding·boundary transfer | hidden BC의 coherent marginalization | partial-input mask lattice |
| LANO | partial spatial input·boundary-first reconstruction | physical-variable mask compatibility | filtration-level distribution tests |
| probabilistic operator | function-space UQ/generative sampling | condition-source attribution | coherent BC pushforward |
| NOP/NP consistency | partial-response reconstruction·conditioning gap | physical-input mask compatibility | nested masks + paired response |
| DeltaPhi | similar-state residual learning | geometry-controlled BC response without label retrieval | paired \(\Delta H\) controls |
| active feature acquisition | test-time feature 선택과 general decision cost | route-inconsistent PDE functional posterior의 decision consequence | functional regret + AFA controls |
| neural-operator functional optimization | posterior operator sample로 비싼 input function query 선택과 regret bound | 한 사례의 partial physical condition에서 component measurement의 route-dependent value | NOTS-style adapted acquisition control |
| PDE UQ/OOD | model uncertainty와 OOD 분석 | BC-induced vs model-induced 분리 | two-axis falsification |
| synthetic CFD | 같은 geometry의 multiple BC | response supervision/generalization | paired \(\Delta H\) |

## 4. novelty를 지키기 위한 필수 baseline

다음 비교가 없으면 contribution을 증명할 수 없다.

1. zero/mean/conditional-mean BC imputation
2. mask-token deterministic operator
3. independent probabilistic head per observation mask
4. NOP-style latent mask-aware probabilistic operator
5. LANO mask-to-predict/boundary-first baseline
6. known-BC boundary extension/transfer operator
7. MC-dropout/deep ensemble
8. 공개 probabilistic/flow-matching operator
9. joint BC density + shared operator, pair loss 없음
10. DeltaPhi-style residual operator
11. full AURORA
12. random cross-geometry pair negative control
13. In-PI-MGN 또는 공개 graph-transformer checkpoint/재현
14. Secondary analysis에서만 clinical+morphology와 +real CFD
15. NOTS-style posterior-sample functional acquisition adapted control

## 5. 문헌상 아직 단정하지 않는 것

- “hemodynamics가 morphology보다 항상 우수하다”
- “WSS가 낮거나 높으면 곧 파열된다”
- “CFD는 ground truth다”
- “semi-idealized geometry에서의 OOD가 임상 외부 검증이다”
- “uncertainty interval이 넓으면 곧 임상 위험이 높다”
- “cross-sectional status model이 2년/5년 rupture probability를 준다”

이 문구들은 결과가 좋아도 현재 데이터로는 주장하지 않는다.
