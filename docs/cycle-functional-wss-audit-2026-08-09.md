# Cycle-functional transient WSS candidate audit

상태: **33/40 historical source shortlist · exact P0 execution-incomplete/no
scientific verdict · candidate closed · processed payload/P1/method/GPU 0**
기준일: 2026-08-09 KST

## 냉정한 결론

새 후보는 **cycle-functional-compatible transient WSS surrogation**이다. 같은
예측 WSS 시계열에서 계산되는 TAWSS, OSI, RRT가 별도 head의 값과 모순되지
않도록, full field와 cycle functional을 하나의 moment contract로 묶을 수
있는지를 묻는다. 8개 고정 축에서 33/40을 얻어 이번 batch에서 유일하게
32점 admission line을 넘었다.

그러나 아직 연구 주제나 방법이 선택된 것은 아니다. 가장 가까운 직접
선행연구 RHSIA가 이미 graph transformer, GHD geometry 표현, steady-flow
augmentation으로 transient WSS를 예측한다. 논문에 보고된 낮은 WSS field
error와 높은 raw OSI relative error의 차이도 OSI가 0에 가까운 노드의 작은
분모에서 생긴 수치 현상일 수 있다. 따라서 그 숫자만 보고 functional-aware
loss나 새 head를 붙이는 것은 novelty가 아니라 사후적인 metric chasing이다.

등록한 `P0`는 두 exact processed archive를 처음 읽어 물리 WSS 복원,
case/topology linkage와 schema를 확인하려는 CPU-only asset gate였다. Exact
source `754ed746…`의 `introai9` PBS job `115168`은 00:05:16 뒤 exit 28로
끝났고 processed/partial payload, aggregate와 raw stdout이 생성되지 않았다.
따라서 16-check scientific gate는 미평가이며 exact shell cause는 단정하지
않는다. 등록 계약에 따라 dependency/reader/transport repair, same-contract
rerun과 P1 없이 candidate version을 닫는다. 모델과 GPU는 계속 금지된다.

## 이번 fresh batch의 동일 척도 비교

각 축은 0–5점이며 source audit 전에 같은 32/40 admission line을 적용했다.
점수는 성공 확률이 아니라, 지금 가진 공개 자산으로 식별 가능하고 strong
baseline과 비교 가능한 ISBI 문제를 만들 수 있는지에 대한 보수적 판단이다.

| 후보 | 중요성 | 식별성 | 남은 gap | 자산 | 단위 | baseline | figure | 일정 | 합계 | 판정 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Cycle-functional-compatible transient WSS | 4 | 5 | 4 | 5 | 3 | 4 | 4 | 4 | **33** | P0-only shortlist |
| BenchAnXplore multi-fidelity error | 4 | 3 | 4 | 2 | 4 | 4 | 4 | 3 | 28 | reject |
| deformation-sibling shape response/ranking | 4 | 3 | 3 | 4 | 2 | 4 | 4 | 4 | 28 | reject |
| flow-diverter outcome modelling | 5 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 22 | reject |
| generic segmentation/morphometry uncertainty | 4 | 4 | 2 | 4 | 4 | 3 | 3 | 3 | 27 | reject |

BenchAnXplore 공개 release에는 비교할 fine-grid truth가 없어 discretization
error learning을 식별할 수 없다. deformation sibling은 AneuG/Shape-DINO와
너무 가깝고 generator family를 patient intervention처럼 해석할 수 없다.
flow-diverter 공개 cohort는 작고 confounded tabular outcome이 중심이다.
segmentation/morphometry uncertainty는 이미 topology, ostium, implicit
representation과 uncertainty literature가 밀집해 독립적인 algorithmic gap이
약하다. 어느 branch도 이름이나 loss를 바꿔 점수를 보충하지 않는다.

## 식별하려는 양

한 synthetic geometry의 표면을 \(\Omega\), source simulation protocol에서
80개 시점의 WSS vector를 \(\tau(x,t)\in\mathbb R^3\)라 하자. 먼저 서로 다른
세 functional을 직접 예측하지 않고 두 cycle moment를 정의한다.

\[
m(x)=\frac1T\sum_{t=1}^{T}\tau(x,t),\qquad
a(x)=\frac1T\sum_{t=1}^{T}\lVert\tau(x,t)\rVert_2.
\]

그러면

\[
\operatorname{TAWSS}(x)=a(x),\qquad
\operatorname{OSI}(x)=\frac12\left(1-\frac{\lVert m(x)\rVert_2}{a(x)}\right),
\qquad
\operatorname{RRT}(x)=\frac1{\lVert m(x)\rVert_2}
\]

가 같은 WSS field에서 정확히 유도된다. 마지막 식은 일반적인
\(1/[(1-2\,OSI)TAWSS]\)와 동치이며, \(\lVert m\rVert\)이 작은 곳에서 RRT가
본질적으로 불안정해짐을 드러낸다. 따라서 향후 평가는 raw relative error
하나가 아니라 absolute error, denominator stratum, surface hotspot overlap,
case ranking과 spatial calibration을 함께 사용해야 한다.

AneuG-Flow는 synthetic CFD이므로 independent unit은 patient가 아니라
synthetic transient geometry case다. inlet waveform과 outlet split은 source
simulation protocol의 일부이지 임의의 patient-specific physiology가 아니다.
이 후보로 clinical utility나 future rupture risk를 주장하지 않는다.

## 선행연구 계보와 claim boundary

1. **Dataset와 baseline.** NeurIPS 2025 Datasets and Benchmarks의
   [AneuG-Flow paper](https://papers.nips.cc/paper_files/paper/2025/file/e2b8ff0035bc9f572a7deefbcbea85bc-Paper-Datasets_and_Benchmarks_Track.pdf)는
   14,000 steady와 730 pulsatile synthetic CFD case, PointNet/graph U-Net WSS
   baseline을 제공한다. 현재
   [dataset release](https://huggingface.co/datasets/whding123/AneuG-Flow)는
   CC BY-SA 4.0이고 transient 730 case와 약 32 GB processed data를 명시한다.
2. **가장 가까운 직접 방법.** [RHSIA](https://arxiv.org/abs/2601.19876)는
   geometry와 temporal information에서 cardiac-cycle WSS를 예측하는 graph
   transformer와 steady-flow augmentation을 이미 제안했다. 따라서 graph
   transformer, GHD, transient WSS surrogation, steady augmentation과 derived
   functional 평가를 novelty로 주장하지 않는다.
3. **Functional-aware operator.** [DOPE](https://arxiv.org/abs/2604.19296)는
   neural-operator trajectory의 scalar target functional에 대한 plug-in bias를
   분석하고 Neyman-orthogonal debiasing을 제안한다. spatially resolved
   full-field/cycle-moment compatibility와 목적이 같지는 않지만, 향후 비교와
   theory red team에서 반드시 다뤄야 한다.
4. **일반 구성요소.** POD/Fourier/DCT/sequence decoder, generic functional
   loss, direct functional head, goal-oriented correction, E(3)-equivariant GNN은
   단독 novelty가 아니다. 이전 D0의 fixed Fourier 실패와 POD eligibility도
   이 후보를 자동으로 지지하지 않는다.

남을 수 있는 gap은 좁다. **같은 spatial transient vector field와 여러
nonlinear cycle functional이 공유하는 최소 moment를 한 representation에서
구조적으로 만족시키면서, strong full-field surrogate보다 hotspot/ranking
오차를 줄이고 field accuracy를 훼손하지 않는가**다. 이 문장도 P1과 이후
fresh baseline 결과가 양수일 때만 contribution 후보가 된다.

## 정확히 pin한 source contract

| 항목 | 값 |
|---|---|
| dataset repo commit | `9dd418083899deddd93a67f9a6fca7a14304fa36` |
| official code commit | `4a090a0f12538deef6fcea88b81afe78ce38152e` |
| steady file | `assembled_registered_steady_data_1k_v4.pth` · 9,632,510,050 bytes · SHA-256 `0c03c1d9…0177f` |
| transient file | `assembled_registered_data_1k_v4.pth` · 23,744,862,051 bytes · SHA-256 `141541ed…51c9` |
| execution | `introai9` PBS · CPU · 128 GB RAM · GPU 0 |

공식 preprocessing code는 transient tensor를 steady archive의
`tensor_norm`으로 정규화하지만, transient assembled object에는 norm을 다시
저장하지 않는다. 따라서 두 파일은 선택 사항이 아니라 하나의 물리 단위
복원 pair다. Dataset page와 NeurIPS paper는 730 transient case를 쓰지만
RHSIA는 808을 보고한다. P0는 현재 exact commit의 실제 수를 기록할 뿐 두
version이 같다고 가정하거나 case를 임의로 추가하지 않는다.

## P0: asset와 recoverability만 검사

Frozen config는 [`aneug_cycle_functional_p0.json`](../configs/aneug_cycle_functional_p0.json)이다.
다음 항목을 all-or-none으로 확인한다.

1. 두 파일의 byte count와 SHA-256이 exact source pin과 일치한다.
2. arbitrary pickle global을 금지한 weights-only reader로 두 archive를 읽는다.
   PyTorch3D `Meshes`는 method를 호출하지 않는 allowlisted state container로만
   복원한다.
3. steady `label/tensor_norm`과 transient `registered_data_list/mesh_data`가
   존재하고 WSS normalization round-trip이 성립한다.
4. 적어도 700 unique case, 모든 80 timestep, 공통 node/channel schema,
   finite tensor와 static geometry/normal을 확인한다.
5. 모든 case에서 denormalized WSS와 temporal variation이 0이 아니고, common
   triangular connectivity가 node range 안에 있으며 geometry fingerprint가
   중복되지 않는다.
6. case identifier, tensor, mesh와 normalization value는 public result에 쓰지
   않고 aggregate count/range/check만 남긴다.

P0 pass는 P1 등록만 허용한다. P0 fail 또는 dependency/reader
execution-incomplete는 이 candidate version을 닫는다. 같은 contract의 reader
수리, dependency 추가, 재다운로드·재실행, threshold 변경, method/GPU/outer
test는 허용하지 않는다.

## P1 이후에만 고려할 수 있는 방법 가설

P1이 field-error-matched perturbation에서도 absolute/spatial functional
degradation이 단순 near-zero 분모 artifact를 넘어선다고 보일 때만 다음
가설을 등록한다. 네트워크가 \(m(x)\), \(a(x)\)와 zero-mean temporal residual을
예측하고, residual을 differentiable projection으로 조정해 재구성한
\(\hat\tau(x,t)\)가 예측 moment를 정확히 갖게 한다. 이때 TAWSS/OSI/RRT는
별도 head가 아니라 같은 moment에서 계산한다.

이 구조는 현재 **아이디어 스케치**일 뿐이다. P1 전에는 이름을 붙이지 않고,
contribution으로 쓰지 않으며, architecture나 loss를 구현하지 않는다. P1이
실패하면 후보를 닫고 OSI metric을 확대해 해석하지 않는다.
